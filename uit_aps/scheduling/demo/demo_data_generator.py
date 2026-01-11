# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Demo Data Generator for APS Scheduling

Creates sample data for demonstrating the APS scheduling system:
- 3 Production Plans with different scenarios
- Work Orders and Job Cards
- Uses EXISTING Workstations, Items, BOMs from the system
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, add_days, add_to_date, getdate, get_datetime
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random


class DemoDataGenerator:
    """
    Generates demo data for APS scheduling demonstrations.
    Uses existing Workstations, Items, and BOMs from the system.
    Only creates: Production Plans, Work Orders, Job Cards
    """

    def __init__(self):
        self.created_work_orders = []
        self.created_job_cards = []
        self.created_production_plans = []

        # Load existing data
        self.existing_items = []
        self.existing_boms = []
        self.existing_workstations = []

    def load_existing_data(self) -> Dict:
        """
        Load existing Items, BOMs, Workstations from the system.

        Returns:
            Dict with lists of existing data
        """
        # Get Items that have BOMs with operations
        boms_with_operations = frappe.get_all(
            "BOM",
            filters={
                "is_active": 1,
                "is_default": 1,
                "with_operations": 1,
                "docstatus": 1
            },
            fields=["name", "item", "quantity"],
            order_by="creation desc"
        )

        self.existing_boms = boms_with_operations
        self.existing_items = [bom["item"] for bom in boms_with_operations]

        # Get active Workstations
        self.existing_workstations = frappe.get_all(
            "Workstation",
            filters={"status": ["!=", ""]},  # Get all workstations
            fields=["name", "workstation_name", "status"],
            order_by="name"
        )

        return {
            "items": self.existing_items,
            "boms": [b["name"] for b in self.existing_boms],
            "workstations": [w["name"] for w in self.existing_workstations]
        }

    def generate_all(self) -> Dict:
        """
        Generate all demo data using existing Items, BOMs, Workstations.

        Returns:
            Dict with summary of created records
        """
        results = {
            "existing_data": {},
            "production_plans": [],
            "work_orders": [],
            "job_cards": [],
            "errors": []
        }

        try:
            # Step 1: Load existing data
            existing = self.load_existing_data()
            results["existing_data"] = existing

            if not self.existing_items:
                results["errors"].append("No Items with active BOMs found. Please create Items and BOMs first.")
                return results

            if not self.existing_workstations:
                results["errors"].append("No Workstations found. Please create Workstations first.")
                return results

            # Step 2: Create 3 Production Plans with different scenarios
            production_plans = self.create_production_plans()
            results["production_plans"] = production_plans

            # Step 3: Create Work Orders and Job Cards for each plan
            for pp in production_plans:
                wo_jc = self.create_work_orders_and_job_cards(pp)
                results["work_orders"].extend(wo_jc["work_orders"])
                results["job_cards"].extend(wo_jc["job_cards"])

            frappe.db.commit()

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Demo Data Generator Error")
            results["errors"].append(str(e))

        return results

    def create_production_plans(self) -> List[str]:
        """
        Create 3 Production Plans with different scenarios using existing Items:
        1. Normal production - standard load
        2. Rush order - tight deadlines, more quantity
        3. Machine breakdown scenario - needs rescheduling
        """
        today = getdate()

        # Get random items from existing items (or use first few)
        available_items = self.existing_items[:5] if len(self.existing_items) >= 5 else self.existing_items

        if len(available_items) < 1:
            frappe.throw(_("Need at least 1 item with BOM to create demo data"))

        # Get default company and warehouse
        company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")

        # Get valid warehouse for the company
        default_warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
        if not default_warehouse or not frappe.db.exists("Warehouse", default_warehouse):
            # Try to get Stores warehouse for the company
            default_warehouse = frappe.db.get_value(
                "Warehouse",
                {"warehouse_name": "Stores", "company": company, "is_group": 0},
                "name"
            )
        if not default_warehouse:
            # Try any non-group warehouse for the company
            default_warehouse = frappe.db.get_value(
                "Warehouse",
                {"company": company, "is_group": 0},
                "name"
            )
        if not default_warehouse:
            frappe.throw(_("No valid warehouse found for company {0}").format(company))

        plans_config = [
            {
                "name_suffix": "NORMAL",
                "posting_date": today,
                "items": [
                    {"item_code": available_items[0], "planned_qty": random.randint(5, 10), "planned_start_date": today}
                ] + ([
                    {"item_code": available_items[1], "planned_qty": random.randint(3, 8), "planned_start_date": today}
                ] if len(available_items) > 1 else []),
                "description": "Normal Production - Standard workload"
            },
            {
                "name_suffix": "RUSH",
                "posting_date": today,
                "items": [
                    {"item_code": item, "planned_qty": random.randint(10, 20), "planned_start_date": today}
                    for item in available_items[:3]
                ],
                "description": "Rush Order - Tight deadline, high priority"
            },
            {
                "name_suffix": "BREAKDOWN",
                "posting_date": today,
                "items": [
                    {"item_code": available_items[0], "planned_qty": random.randint(5, 12), "planned_start_date": today}
                ] + ([
                    {"item_code": available_items[-1], "planned_qty": random.randint(4, 8), "planned_start_date": today}
                ] if len(available_items) > 1 else []),
                "description": "Machine Breakdown Scenario - For testing rescheduling"
            }
        ]

        created_plans = []
        for plan_config in plans_config:
            plan_name = f"PP-DEMO-{plan_config['name_suffix']}-{today.strftime('%Y%m%d')}"

            # Check if exists
            if frappe.db.exists("Production Plan", plan_name):
                created_plans.append(plan_name)
                continue

            try:
                pp = frappe.get_doc({
                    "doctype": "Production Plan",
                    "posting_date": plan_config["posting_date"],
                    "company": company,
                    "po_items": [
                        {
                            "item_code": item["item_code"],
                            "planned_qty": item["planned_qty"],
                            "warehouse": default_warehouse,
                            "planned_start_date": item["planned_start_date"],
                            "bom_no": frappe.db.get_value("BOM", {"item": item["item_code"], "is_default": 1, "is_active": 1}, "name")
                        }
                        for item in plan_config["items"]
                        if frappe.db.exists("BOM", {"item": item["item_code"], "is_default": 1, "is_active": 1})
                    ]
                })

                if pp.po_items:
                    pp.insert(ignore_permissions=True)
                    pp.submit()
                    created_plans.append(pp.name)

            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Demo: {plan_name}"[:140])

        self.created_production_plans = created_plans
        return created_plans

    def create_work_orders_and_job_cards(self, production_plan: str) -> Dict:
        """Create Work Orders and Job Cards for a Production Plan."""
        work_orders = []
        job_cards = []

        pp = frappe.get_doc("Production Plan", production_plan)

        for item in pp.po_items:
            try:
                # Get BOM
                bom = item.bom_no or frappe.db.get_value("BOM", {"item": item.item_code, "is_default": 1, "is_active": 1}, "name")
                if not bom:
                    continue

                # Calculate dates
                start_date = get_datetime(item.planned_start_date or pp.posting_date)
                # Add some randomness to due dates for testing
                due_days = random.randint(3, 7)
                due_date = add_days(start_date, due_days)

                # Get warehouses
                wip_warehouse = frappe.db.get_single_value("Manufacturing Settings", "default_wip_warehouse")
                fg_warehouse = frappe.db.get_single_value("Manufacturing Settings", "default_fg_warehouse")

                if not wip_warehouse:
                    wip_warehouse = frappe.db.get_value("Warehouse", {"warehouse_name": ["like", "%Work In Progress%"], "company": pp.company}, "name")
                if not fg_warehouse:
                    fg_warehouse = frappe.db.get_value("Warehouse", {"warehouse_name": ["like", "%Finished%"], "company": pp.company}, "name")

                # Fallback to any warehouse
                if not wip_warehouse:
                    wip_warehouse = frappe.db.get_value("Warehouse", {"is_group": 0, "company": pp.company}, "name")
                if not fg_warehouse:
                    fg_warehouse = wip_warehouse

                wo = frappe.get_doc({
                    "doctype": "Work Order",
                    "production_plan": production_plan,
                    "production_item": item.item_code,
                    "qty": item.planned_qty,
                    "bom_no": bom,
                    "company": pp.company,
                    "wip_warehouse": wip_warehouse,
                    "fg_warehouse": fg_warehouse,
                    "planned_start_date": start_date,
                    "expected_delivery_date": due_date,
                    "use_multi_level_bom": 0
                })
                wo.insert(ignore_permissions=True)
                wo.submit()
                work_orders.append(wo.name)

                # Create Job Cards for each operation
                bom_doc = frappe.get_doc("BOM", bom)
                current_start = start_date

                for idx, op in enumerate(bom_doc.operations):
                    try:
                        # Calculate operation duration
                        duration_mins = (op.time_in_mins or 30) * item.planned_qty
                        end_time = current_start + timedelta(minutes=duration_mins)

                        jc = frappe.get_doc({
                            "doctype": "Job Card",
                            "work_order": wo.name,
                            "bom_no": bom,
                            "operation": op.operation,
                            "workstation": op.workstation,
                            "production_item": item.item_code,
                            "for_quantity": item.planned_qty,
                            "wip_warehouse": wip_warehouse,
                            "company": wo.company,
                            "expected_start_date": current_start,
                            "expected_end_date": end_time,
                            "operation_id": op.name,
                            "sequence_id": op.sequence_id or (idx + 1),
                            "time_logs": [
                                {
                                    "from_time": current_start,
                                    "to_time": end_time,
                                    "time_in_mins": duration_mins,
                                    "completed_qty": 0
                                }
                            ]
                        })
                        jc.insert(ignore_permissions=True)
                        job_cards.append(jc.name)

                        # Next operation starts after this one
                        current_start = end_time + timedelta(minutes=10)  # 10 min gap

                    except Exception as e:
                        frappe.log_error(frappe.get_traceback(), f"Demo JC: {wo.name}"[:140])

            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Demo WO: {item.item_code}"[:140])

        self.created_work_orders.extend(work_orders)
        self.created_job_cards.extend(job_cards)

        return {"work_orders": work_orders, "job_cards": job_cards}


@frappe.whitelist()
def generate_demo_data() -> Dict:
    """
    API endpoint to generate demo data.
    Uses existing Workstations, Items, BOMs from the system.
    Only creates: Production Plans, Work Orders, Job Cards
    """
    try:
        generator = DemoDataGenerator()
        result = generator.generate_all()

        if result.get("errors"):
            return {
                "success": False,
                "error": ", ".join(result["errors"]),
                **result
            }

        return {
            "success": True,
            "message": _("Demo data generated successfully using existing Items and BOMs"),
            **result
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Generate Demo Data Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def get_existing_data() -> Dict:
    """
    API endpoint to get existing data that can be used for demo.
    Shows available Items with BOMs and Workstations.
    """
    try:
        generator = DemoDataGenerator()
        existing = generator.load_existing_data()

        # Get more details
        items_detail = []
        for item in existing["items"]:
            bom = frappe.db.get_value("BOM", {"item": item, "is_default": 1, "is_active": 1},
                                      ["name", "quantity"], as_dict=True)
            if bom:
                op_count = frappe.db.count("BOM Operation", {"parent": bom["name"]})
                items_detail.append({
                    "item_code": item,
                    "bom": bom["name"],
                    "operations_count": op_count
                })

        workstations_detail = []
        for ws in generator.existing_workstations:
            workstations_detail.append({
                "name": ws["name"],
                "workstation_name": ws["workstation_name"],
                "status": ws["status"]
            })

        return {
            "success": True,
            "items": items_detail,
            "workstations": workstations_detail,
            "total_items": len(items_detail),
            "total_workstations": len(workstations_detail),
            "ready_for_demo": len(items_detail) > 0 and len(workstations_detail) > 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def get_demo_status() -> Dict:
    """Get status of demo data."""
    try:
        # Count demo data
        demo_pp_count = frappe.db.count("Production Plan", {"name": ["like", "PP-DEMO-%"]})
        demo_wo_count = frappe.db.count("Work Order", {"production_plan": ["like", "PP-DEMO-%"]})

        # Get job cards linked to demo work orders
        demo_work_orders = frappe.get_all(
            "Work Order",
            filters={"production_plan": ["like", "PP-DEMO-%"]},
            pluck="name"
        )
        demo_jc_count = frappe.db.count("Job Card", {"work_order": ["in", demo_work_orders]}) if demo_work_orders else 0

        # Count all data
        return {
            "success": True,
            "demo_data": {
                "production_plans": demo_pp_count,
                "work_orders": demo_wo_count,
                "job_cards": demo_jc_count
            },
            "all_data": {
                "production_plans": frappe.db.count("Production Plan"),
                "work_orders": frappe.db.count("Work Order"),
                "job_cards": frappe.db.count("Job Card"),
                "workstations": frappe.db.count("Workstation"),
                "items_with_bom": frappe.db.count("BOM", {"is_active": 1, "is_default": 1, "with_operations": 1}),
                "scheduling_runs": frappe.db.count("APS Scheduling Run") if frappe.db.table_exists("APS Scheduling Run") else 0
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def cleanup_demo_data() -> Dict:
    """
    API endpoint to cleanup demo data.
    Removes Production Plans, Work Orders, Job Cards created with PP-DEMO- prefix.
    Does NOT delete Items, BOMs, Workstations.
    """
    try:
        deleted = {
            "job_cards": 0,
            "work_orders": 0,
            "production_plans": 0,
            "scheduling_runs": 0
        }

        # Delete Scheduling Runs linked to demo plans
        if frappe.db.table_exists("APS Scheduling Run"):
            demo_runs = frappe.get_all(
                "APS Scheduling Run",
                filters={"production_plan": ["like", "PP-DEMO-%"]},
                pluck="name"
            )
            for run in demo_runs:
                frappe.delete_doc("APS Scheduling Run", run, force=True, ignore_permissions=True)
                deleted["scheduling_runs"] += 1

        # Get demo work orders
        demo_work_orders = frappe.get_all(
            "Work Order",
            filters={"production_plan": ["like", "PP-DEMO-%"]},
            pluck="name"
        )

        # Delete Job Cards linked to demo work orders
        if demo_work_orders:
            job_cards = frappe.get_all(
                "Job Card",
                filters={"work_order": ["in", demo_work_orders]},
                pluck="name"
            )
            for jc in job_cards:
                frappe.delete_doc("Job Card", jc, force=True, ignore_permissions=True)
                deleted["job_cards"] += 1

        # Delete Work Orders
        for wo in demo_work_orders:
            try:
                wo_doc = frappe.get_doc("Work Order", wo)
                if wo_doc.docstatus == 1:
                    wo_doc.flags.ignore_permissions = True
                    wo_doc.cancel()
                frappe.delete_doc("Work Order", wo, force=True, ignore_permissions=True)
                deleted["work_orders"] += 1
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Cleanup WO: {wo}"[:140])

        # Delete Production Plans
        production_plans = frappe.get_all(
            "Production Plan",
            filters={"name": ["like", "PP-DEMO-%"]},
            pluck="name"
        )
        for pp in production_plans:
            try:
                pp_doc = frappe.get_doc("Production Plan", pp)
                if pp_doc.docstatus == 1:
                    pp_doc.flags.ignore_permissions = True
                    pp_doc.cancel()
                frappe.delete_doc("Production Plan", pp, force=True, ignore_permissions=True)
                deleted["production_plans"] += 1
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Cleanup PP: {pp}"[:140])

        frappe.db.commit()

        return {
            "success": True,
            "message": _("Demo data cleaned up successfully"),
            "deleted": deleted
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Cleanup Demo Data Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def simulate_breakdown(workstation: str = None) -> Dict:
    """
    API endpoint to simulate machine breakdown.
    If no workstation specified, picks a random active one.
    """
    try:
        if not workstation:
            # Pick a random active workstation
            workstations = frappe.get_all(
                "Workstation",
                filters={"status": "Production"},
                pluck="name"
            )
            if workstations:
                workstation = random.choice(workstations)
            else:
                return {
                    "success": False,
                    "error": _("No active workstations found")
                }

        # Get current status
        current_status = frappe.db.get_value("Workstation", workstation, "status")

        # Mark as Maintenance
        frappe.db.set_value("Workstation", workstation, "status", "Maintenance")

        # Get affected job cards
        affected_job_cards = frappe.get_all(
            "Job Card",
            filters={
                "workstation": workstation,
                "status": ["in", ["Open", "Work In Progress", "Pending"]]
            },
            fields=["name", "work_order", "operation", "expected_start_date", "expected_end_date", "for_quantity"]
        )

        # Calculate total impact
        total_duration = sum([
            (get_datetime(jc.get("expected_end_date")) - get_datetime(jc.get("expected_start_date"))).total_seconds() / 3600
            for jc in affected_job_cards
            if jc.get("expected_start_date") and jc.get("expected_end_date")
        ])

        frappe.db.commit()

        return {
            "success": True,
            "workstation": workstation,
            "previous_status": current_status,
            "new_status": "Maintenance",
            "affected_job_cards": affected_job_cards,
            "affected_count": len(affected_job_cards),
            "total_duration_hours": round(total_duration, 2),
            "message": _("Workstation {0} marked as Maintenance. {1} job cards affected.").format(
                workstation, len(affected_job_cards)
            )
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def restore_workstation(workstation: str) -> Dict:
    """
    API endpoint to restore a workstation from Maintenance to Production.
    """
    try:
        if not frappe.db.exists("Workstation", workstation):
            return {
                "success": False,
                "error": _("Workstation {0} not found").format(workstation)
            }

        current_status = frappe.db.get_value("Workstation", workstation, "status")
        frappe.db.set_value("Workstation", workstation, "status", "Production")
        frappe.db.commit()

        return {
            "success": True,
            "workstation": workstation,
            "previous_status": current_status,
            "new_status": "Production",
            "message": _("Workstation {0} restored to Production").format(workstation)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
