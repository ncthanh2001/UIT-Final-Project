# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
ERPNext Data Loader for Scheduling

Loads scheduling data from ERPNext:
- Work Orders and their operations
- Job Cards
- Workstations with capacity and working hours
- Production Plans

Transforms ERPNext data into scheduling problem format.
"""

import frappe
from frappe.utils import now_datetime, getdate, get_datetime, add_days, cint, flt
from datetime import datetime, time, timedelta
from typing import List, Dict, Optional, Tuple

from uit_aps.scheduling.ortools.models import (
    Job,
    Operation,
    Machine,
    WorkingHourSlot,
    SchedulingProblem,
    SchedulingConfig,
)


class ERPNextDataLoader:
    """
    Loads and transforms ERPNext manufacturing data for scheduling.
    """

    def __init__(self, company: str = None):
        """
        Initialize the loader.

        Args:
            company: Filter by company name
        """
        self.company = company

    def load_from_production_plan(
        self,
        production_plan: str,
        config: SchedulingConfig = None
    ) -> SchedulingProblem:
        """
        Load scheduling problem from APS Production Plan.

        Creates Work Orders if they don't exist, then loads Job Cards.

        Args:
            production_plan: Name of APS Production Plan
            config: Scheduling configuration

        Returns:
            SchedulingProblem ready for solver
        """
        if config is None:
            config = SchedulingConfig()

        plan_doc = frappe.get_doc("APS Production Plan", production_plan)

        if plan_doc.status not in ["Draft", "Planned", "Released"]:
            frappe.throw(f"Production Plan {production_plan} is not in schedulable status")

        jobs = []
        for item in plan_doc.items:
            # Get or create Work Order for this item
            work_order = self._get_or_create_work_order(item, plan_doc)
            if work_order:
                job = self._convert_work_order_to_job(work_order, item)
                if job and job.operations:
                    jobs.append(job)

        # Load machines (workstations)
        machines = self._load_workstations()

        return SchedulingProblem(
            jobs=jobs,
            machines=machines,
            config=config,
            production_plan=production_plan
        )

    def load_from_work_orders(
        self,
        work_order_names: List[str] = None,
        filters: Dict = None,
        config: SchedulingConfig = None
    ) -> SchedulingProblem:
        """
        Load scheduling problem from existing Work Orders.

        Args:
            work_order_names: List of specific Work Order names
            filters: Filters for Work Order query
            config: Scheduling configuration

        Returns:
            SchedulingProblem ready for solver
        """
        if config is None:
            config = SchedulingConfig()

        if work_order_names:
            work_orders = [frappe.get_doc("Work Order", name) for name in work_order_names]
        else:
            if filters is None:
                filters = {
                    "docstatus": 1,
                    "status": ["not in", ["Completed", "Stopped", "Cancelled"]]
                }
            if self.company:
                filters["company"] = self.company

            work_order_names = frappe.get_all("Work Order", filters=filters, pluck="name")
            work_orders = [frappe.get_doc("Work Order", name) for name in work_order_names]

        jobs = []
        for wo in work_orders:
            job = self._convert_work_order_to_job(wo)
            if job and job.operations:
                jobs.append(job)

        machines = self._load_workstations()

        return SchedulingProblem(
            jobs=jobs,
            machines=machines,
            config=config
        )

    def _get_or_create_work_order(
        self,
        plan_item,
        plan_doc
    ) -> Optional["frappe._dict"]:
        """
        Get existing Work Order or create new one from Production Plan Item.

        Args:
            plan_item: APS Production Plan Item
            plan_doc: Parent APS Production Plan

        Returns:
            Work Order document or None
        """
        # Check if Work Order already exists for this item
        existing_wo = frappe.db.exists("Work Order", {
            "production_item": plan_item.item,
            "planned_start_date": [">=", plan_item.planned_start_date or plan_item.plan_period],
            "docstatus": ["<", 2],
            "status": ["not in", ["Completed", "Stopped", "Cancelled"]]
        })

        if existing_wo:
            return frappe.get_doc("Work Order", existing_wo)

        # Get BOM for item
        bom = self._get_default_bom(plan_item.item)
        if not bom:
            frappe.log_error(
                f"No BOM found for item {plan_item.item}",
                "Scheduling - Missing BOM"
            )
            return None

        try:
            # Create new Work Order
            wo = frappe.get_doc({
                "doctype": "Work Order",
                "production_item": plan_item.item,
                "bom_no": bom,
                "qty": plan_item.planned_qty,
                "company": plan_doc.company,
                "planned_start_date": plan_item.planned_start_date or plan_item.plan_period,
                "expected_delivery_date": plan_item.plan_period,
                "use_multi_level_bom": 1,
                "skip_transfer": 0
            })
            wo.insert(ignore_permissions=True)
            wo.submit()
            frappe.db.commit()

            return wo

        except Exception as e:
            frappe.log_error(
                f"Failed to create Work Order for {plan_item.item}: {str(e)}",
                "Scheduling - Work Order Creation Error"
            )
            return None

    def _convert_work_order_to_job(
        self,
        work_order,
        plan_item=None
    ) -> Optional[Job]:
        """
        Convert ERPNext Work Order to scheduling Job.

        Args:
            work_order: Work Order document
            plan_item: Optional APS Production Plan Item for additional context

        Returns:
            Job object or None
        """
        operations = []

        # Get Job Cards for this Work Order
        job_cards = frappe.get_all(
            "Job Card",
            filters={
                "work_order": work_order.name,
                "docstatus": ["<", 2],
                "status": ["not in", ["Completed", "Cancelled"]]
            },
            fields=["name", "operation", "workstation", "workstation_type",
                    "for_quantity", "time_in_mins", "sequence_id"],
            order_by="sequence_id asc"
        )

        if not job_cards:
            # Create Job Cards from Work Order operations
            job_cards = self._create_job_cards_from_work_order(work_order)

        for idx, jc in enumerate(job_cards):
            # Get eligible machines for this operation
            eligible_machines = self._get_eligible_machines(
                jc.get("workstation"),
                jc.get("workstation_type")
            )

            if not eligible_machines:
                frappe.log_error(
                    f"No eligible machines for Job Card {jc.get('name')}",
                    "Scheduling - No Machines"
                )
                continue

            operation = Operation(
                id=jc.get("name"),
                job_id=work_order.name,
                name=jc.get("operation") or f"Operation {idx + 1}",
                machine_type=jc.get("workstation_type"),
                eligible_machines=eligible_machines,
                duration_mins=cint(jc.get("time_in_mins")) or 60,  # Default 1 hour
                sequence=jc.get("sequence_id") or (idx + 1),
                setup_time_mins=10  # Default setup time
            )
            operations.append(operation)

        if not operations:
            return None

        # Determine dates
        release_date = get_datetime(work_order.planned_start_date) if work_order.planned_start_date else now_datetime()
        due_date = get_datetime(work_order.expected_delivery_date) if work_order.expected_delivery_date else add_days(release_date, 7)

        # Priority based on delivery urgency
        days_until_due = (due_date - now_datetime()).days
        if days_until_due <= 1:
            priority = 10
        elif days_until_due <= 3:
            priority = 7
        elif days_until_due <= 7:
            priority = 5
        else:
            priority = 1

        return Job(
            id=work_order.name,
            item_code=work_order.production_item,
            qty=flt(work_order.qty),
            operations=operations,
            release_date=release_date,
            due_date=due_date,
            priority=priority
        )

    def _create_job_cards_from_work_order(self, work_order) -> List[Dict]:
        """
        Create Job Cards from Work Order operations if they don't exist.

        Args:
            work_order: Work Order document

        Returns:
            List of Job Card data dicts
        """
        job_cards = []

        if not work_order.operations:
            # No operations defined, create a single default operation
            jc = frappe.get_doc({
                "doctype": "Job Card",
                "work_order": work_order.name,
                "operation": "Default Operation",
                "for_quantity": work_order.qty,
                "time_in_mins": 60,
                "sequence_id": 1
            })
            jc.insert(ignore_permissions=True)
            job_cards.append({
                "name": jc.name,
                "operation": jc.operation,
                "workstation": jc.workstation,
                "workstation_type": jc.workstation_type,
                "for_quantity": jc.for_quantity,
                "time_in_mins": jc.time_in_mins,
                "sequence_id": jc.sequence_id
            })
        else:
            for op in work_order.operations:
                # Check if Job Card exists
                existing = frappe.db.exists("Job Card", {
                    "work_order": work_order.name,
                    "operation": op.operation,
                    "docstatus": ["<", 2]
                })

                if existing:
                    jc_doc = frappe.get_doc("Job Card", existing)
                else:
                    jc = frappe.get_doc({
                        "doctype": "Job Card",
                        "work_order": work_order.name,
                        "operation": op.operation,
                        "workstation": op.workstation,
                        "workstation_type": op.workstation_type,
                        "for_quantity": work_order.qty,
                        "time_in_mins": op.time_in_mins or 60,
                        "sequence_id": op.sequence_id or op.idx
                    })
                    jc.insert(ignore_permissions=True)
                    jc_doc = jc

                job_cards.append({
                    "name": jc_doc.name,
                    "operation": jc_doc.operation,
                    "workstation": jc_doc.workstation,
                    "workstation_type": jc_doc.workstation_type,
                    "for_quantity": jc_doc.for_quantity,
                    "time_in_mins": jc_doc.time_in_mins,
                    "sequence_id": jc_doc.sequence_id
                })

        frappe.db.commit()
        return job_cards

    def _get_eligible_machines(
        self,
        workstation: str = None,
        workstation_type: str = None
    ) -> List[str]:
        """
        Get list of eligible machine IDs for an operation.

        Args:
            workstation: Specific workstation name
            workstation_type: Type of workstation

        Returns:
            List of workstation names
        """
        if workstation:
            # Check if workstation exists and is not disabled
            if frappe.db.exists("Workstation", {"name": workstation, "disabled": 0}):
                return [workstation]

        if workstation_type:
            # Get all workstations of this type
            machines = frappe.get_all(
                "Workstation",
                filters={
                    "workstation_type": workstation_type,
                    "disabled": 0
                },
                pluck="name"
            )
            if machines:
                return machines

        # Fallback: return all available workstations
        return frappe.get_all(
            "Workstation",
            filters={"disabled": 0},
            pluck="name"
        ) or []

    def _load_workstations(self) -> List[Machine]:
        """
        Load all workstations as machines.

        Returns:
            List of Machine objects
        """
        workstations = frappe.get_all(
            "Workstation",
            filters={"disabled": 0},
            fields=["name", "workstation_name", "workstation_type",
                    "production_capacity", "holiday_list"]
        )

        machines = []
        for ws in workstations:
            # Load working hours
            working_hours = self._load_working_hours(ws.name)

            machine = Machine(
                id=ws.name,
                name=ws.workstation_name or ws.name,
                machine_type=ws.workstation_type,
                capacity=cint(ws.production_capacity) or 1,
                working_hours=working_hours,
                holiday_list=ws.holiday_list,
                is_available=True
            )
            machines.append(machine)

        return machines

    def _load_working_hours(self, workstation: str) -> List[WorkingHourSlot]:
        """
        Load working hour slots for a workstation.

        Args:
            workstation: Workstation name

        Returns:
            List of WorkingHourSlot objects
        """
        slots = []

        working_hours = frappe.get_all(
            "Workstation Working Hour",
            filters={"parent": workstation},
            fields=["start_time", "end_time"],
            order_by="start_time asc"
        )

        for wh in working_hours:
            try:
                start = wh.start_time
                end = wh.end_time

                # Handle timedelta objects from database
                if isinstance(start, timedelta):
                    start = (datetime.min + start).time()
                elif isinstance(start, str):
                    start = datetime.strptime(start, "%H:%M:%S").time()

                if isinstance(end, timedelta):
                    end = (datetime.min + end).time()
                elif isinstance(end, str):
                    end = datetime.strptime(end, "%H:%M:%S").time()

                slots.append(WorkingHourSlot(start_time=start, end_time=end))
            except Exception as e:
                frappe.log_error(
                    f"Error parsing working hours for {workstation}: {str(e)}",
                    "Scheduling - Working Hours Error"
                )

        # If no working hours defined, use default 8 AM - 5 PM
        if not slots:
            slots.append(WorkingHourSlot(
                start_time=time(8, 0),
                end_time=time(17, 0)
            ))

        return slots

    def _get_default_bom(self, item_code: str) -> Optional[str]:
        """
        Get default BOM for an item.

        Args:
            item_code: Item code

        Returns:
            BOM name or None
        """
        # First try to get default BOM
        bom = frappe.db.get_value(
            "BOM",
            {"item": item_code, "is_default": 1, "is_active": 1, "docstatus": 1},
            "name"
        )

        if not bom:
            # Try to get any active BOM
            bom = frappe.db.get_value(
                "BOM",
                {"item": item_code, "is_active": 1, "docstatus": 1},
                "name"
            )

        return bom

    def get_holidays(self, holiday_list: str, start_date: datetime, end_date: datetime) -> List[datetime]:
        """
        Get list of holidays in date range.

        Args:
            holiday_list: Holiday List name
            start_date: Start date
            end_date: End date

        Returns:
            List of holiday dates
        """
        if not holiday_list:
            return []

        holidays = frappe.get_all(
            "Holiday",
            filters={
                "parent": holiday_list,
                "holiday_date": ["between", [start_date.date(), end_date.date()]]
            },
            pluck="holiday_date"
        )

        return [get_datetime(h) for h in holidays]
