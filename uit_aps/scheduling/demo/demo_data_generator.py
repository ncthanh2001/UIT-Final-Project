# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Demo Data Generator for APS Scheduling

Creates sample data for demonstrating the APS scheduling system:
- 3 Production Plans with different scenarios
- Work Orders and Job Cards
- Workstations with varying capacities
- Simulated machine breakdowns
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
    """

    def __init__(self):
        self.created_items = []
        self.created_workstations = []
        self.created_work_orders = []
        self.created_job_cards = []
        self.created_production_plans = []

    def generate_all(self) -> Dict:
        """
        Generate all demo data.

        Returns:
            Dict with summary of created records
        """
        results = {
            "workstations": [],
            "items": [],
            "boms": [],
            "production_plans": [],
            "work_orders": [],
            "job_cards": [],
            "errors": []
        }

        try:
            # Step 1: Create Workstations
            workstations = self.create_workstations()
            results["workstations"] = workstations

            # Step 2: Create Items and BOMs
            items_boms = self.create_items_and_boms()
            results["items"] = items_boms["items"]
            results["boms"] = items_boms["boms"]

            # Step 3: Create 3 Production Plans with different scenarios
            production_plans = self.create_production_plans()
            results["production_plans"] = production_plans

            # Step 4: Create Work Orders and Job Cards for each plan
            for pp in production_plans:
                wo_jc = self.create_work_orders_and_job_cards(pp)
                results["work_orders"].extend(wo_jc["work_orders"])
                results["job_cards"].extend(wo_jc["job_cards"])

            frappe.db.commit()

        except Exception as e:
            frappe.log_error(str(e), "Demo Data Generator Error")
            results["errors"].append(str(e))

        return results

    def create_workstations(self) -> List[str]:
        """Create demo workstations with different capabilities."""
        workstations_config = [
            {
                "name": "WS-CNC-01",
                "workstation_name": "CNC Machine 01",
                "production_capacity": 8,
                "working_hours": 16,
                "status": "Production"
            },
            {
                "name": "WS-CNC-02",
                "workstation_name": "CNC Machine 02",
                "production_capacity": 8,
                "working_hours": 16,
                "status": "Production"
            },
            {
                "name": "WS-LATHE-01",
                "workstation_name": "Lathe Machine 01",
                "production_capacity": 6,
                "working_hours": 16,
                "status": "Production"
            },
            {
                "name": "WS-LATHE-02",
                "workstation_name": "Lathe Machine 02",
                "production_capacity": 6,
                "working_hours": 16,
                "status": "Maintenance"  # Simulated breakdown
            },
            {
                "name": "WS-MILL-01",
                "workstation_name": "Milling Machine 01",
                "production_capacity": 10,
                "working_hours": 16,
                "status": "Production"
            },
            {
                "name": "WS-DRILL-01",
                "workstation_name": "Drilling Machine 01",
                "production_capacity": 12,
                "working_hours": 16,
                "status": "Production"
            },
            {
                "name": "WS-ASSEMBLY-01",
                "workstation_name": "Assembly Line 01",
                "production_capacity": 20,
                "working_hours": 16,
                "status": "Production"
            },
            {
                "name": "WS-QC-01",
                "workstation_name": "Quality Control Station",
                "production_capacity": 15,
                "working_hours": 16,
                "status": "Production"
            }
        ]

        created = []
        for ws_config in workstations_config:
            if not frappe.db.exists("Workstation", ws_config["name"]):
                ws = frappe.get_doc({
                    "doctype": "Workstation",
                    "name": ws_config["name"],
                    "workstation_name": ws_config["workstation_name"],
                    "production_capacity": ws_config["production_capacity"],
                    "status": ws_config["status"]
                })
                ws.insert(ignore_permissions=True)
                created.append(ws_config["name"])
            else:
                created.append(ws_config["name"])

        self.created_workstations = created
        return created

    def create_items_and_boms(self) -> Dict:
        """Create demo items and BOMs."""
        items_config = [
            # Raw Materials
            {"item_code": "RM-STEEL-001", "item_name": "Steel Bar 10mm", "item_group": "Raw Material", "is_stock_item": 1},
            {"item_code": "RM-STEEL-002", "item_name": "Steel Plate 5mm", "item_group": "Raw Material", "is_stock_item": 1},
            {"item_code": "RM-ALUM-001", "item_name": "Aluminum Rod 8mm", "item_group": "Raw Material", "is_stock_item": 1},

            # Sub-assemblies
            {"item_code": "SA-SHAFT-001", "item_name": "Drive Shaft Assembly", "item_group": "Sub Assemblies", "is_stock_item": 1},
            {"item_code": "SA-GEAR-001", "item_name": "Gear Assembly", "item_group": "Sub Assemblies", "is_stock_item": 1},
            {"item_code": "SA-HOUSING-001", "item_name": "Motor Housing", "item_group": "Sub Assemblies", "is_stock_item": 1},

            # Finished Goods
            {"item_code": "FG-MOTOR-001", "item_name": "Electric Motor Type A", "item_group": "Products", "is_stock_item": 1},
            {"item_code": "FG-PUMP-001", "item_name": "Hydraulic Pump", "item_group": "Products", "is_stock_item": 1},
            {"item_code": "FG-GEARBOX-001", "item_name": "Industrial Gearbox", "item_group": "Products", "is_stock_item": 1},
        ]

        created_items = []
        for item_config in items_config:
            if not frappe.db.exists("Item", item_config["item_code"]):
                # Check if item group exists
                if not frappe.db.exists("Item Group", item_config["item_group"]):
                    frappe.get_doc({
                        "doctype": "Item Group",
                        "item_group_name": item_config["item_group"],
                        "parent_item_group": "All Item Groups"
                    }).insert(ignore_permissions=True)

                item = frappe.get_doc({
                    "doctype": "Item",
                    "item_code": item_config["item_code"],
                    "item_name": item_config["item_name"],
                    "item_group": item_config["item_group"],
                    "is_stock_item": item_config["is_stock_item"],
                    "stock_uom": "Nos"
                })
                item.insert(ignore_permissions=True)
                created_items.append(item_config["item_code"])
            else:
                created_items.append(item_config["item_code"])

        # Create BOMs
        boms_config = [
            {
                "item": "FG-MOTOR-001",
                "operations": [
                    {"operation": "Cutting", "workstation": "WS-CNC-01", "time_in_mins": 30},
                    {"operation": "Turning", "workstation": "WS-LATHE-01", "time_in_mins": 45},
                    {"operation": "Milling", "workstation": "WS-MILL-01", "time_in_mins": 60},
                    {"operation": "Assembly", "workstation": "WS-ASSEMBLY-01", "time_in_mins": 40},
                    {"operation": "QC Inspection", "workstation": "WS-QC-01", "time_in_mins": 15},
                ]
            },
            {
                "item": "FG-PUMP-001",
                "operations": [
                    {"operation": "Cutting", "workstation": "WS-CNC-02", "time_in_mins": 25},
                    {"operation": "Drilling", "workstation": "WS-DRILL-01", "time_in_mins": 35},
                    {"operation": "Milling", "workstation": "WS-MILL-01", "time_in_mins": 50},
                    {"operation": "Assembly", "workstation": "WS-ASSEMBLY-01", "time_in_mins": 55},
                    {"operation": "QC Inspection", "workstation": "WS-QC-01", "time_in_mins": 20},
                ]
            },
            {
                "item": "FG-GEARBOX-001",
                "operations": [
                    {"operation": "Cutting", "workstation": "WS-CNC-01", "time_in_mins": 40},
                    {"operation": "Turning", "workstation": "WS-LATHE-02", "time_in_mins": 60},  # Uses broken machine
                    {"operation": "Drilling", "workstation": "WS-DRILL-01", "time_in_mins": 30},
                    {"operation": "Milling", "workstation": "WS-MILL-01", "time_in_mins": 70},
                    {"operation": "Assembly", "workstation": "WS-ASSEMBLY-01", "time_in_mins": 80},
                    {"operation": "QC Inspection", "workstation": "WS-QC-01", "time_in_mins": 25},
                ]
            }
        ]

        created_boms = []
        for bom_config in boms_config:
            bom_name = f"BOM-{bom_config['item']}-001"
            if not frappe.db.exists("BOM", {"item": bom_config["item"], "is_default": 1}):
                # First create operations if not exist
                for op in bom_config["operations"]:
                    if not frappe.db.exists("Operation", op["operation"]):
                        frappe.get_doc({
                            "doctype": "Operation",
                            "name": op["operation"],
                            "workstation": op["workstation"]
                        }).insert(ignore_permissions=True)

                bom = frappe.get_doc({
                    "doctype": "BOM",
                    "item": bom_config["item"],
                    "quantity": 1,
                    "is_default": 1,
                    "is_active": 1,
                    "with_operations": 1,
                    "operations": [
                        {
                            "operation": op["operation"],
                            "workstation": op["workstation"],
                            "time_in_mins": op["time_in_mins"],
                            "sequence_id": idx + 1
                        }
                        for idx, op in enumerate(bom_config["operations"])
                    ]
                })
                bom.insert(ignore_permissions=True)
                bom.submit()
                created_boms.append(bom.name)
            else:
                existing = frappe.db.get_value("BOM", {"item": bom_config["item"], "is_default": 1}, "name")
                created_boms.append(existing)

        self.created_items = created_items
        return {"items": created_items, "boms": created_boms}

    def create_production_plans(self) -> List[str]:
        """
        Create 3 Production Plans with different scenarios:
        1. Normal production - standard load
        2. Rush order - tight deadlines
        3. Machine breakdown scenario - needs rescheduling
        """
        today = getdate()
        plans_config = [
            {
                "name_suffix": "NORMAL",
                "posting_date": today,
                "items": [
                    {"item_code": "FG-MOTOR-001", "planned_qty": 10, "planned_start_date": today},
                    {"item_code": "FG-PUMP-001", "planned_qty": 8, "planned_start_date": today},
                ],
                "description": "Normal Production - Standard workload"
            },
            {
                "name_suffix": "RUSH",
                "posting_date": today,
                "items": [
                    {"item_code": "FG-MOTOR-001", "planned_qty": 15, "planned_start_date": today},
                    {"item_code": "FG-PUMP-001", "planned_qty": 12, "planned_start_date": today},
                    {"item_code": "FG-GEARBOX-001", "planned_qty": 5, "planned_start_date": today},
                ],
                "description": "Rush Order - Tight deadline, high priority"
            },
            {
                "name_suffix": "BREAKDOWN",
                "posting_date": today,
                "items": [
                    {"item_code": "FG-GEARBOX-001", "planned_qty": 8, "planned_start_date": today},
                    {"item_code": "FG-MOTOR-001", "planned_qty": 6, "planned_start_date": today},
                ],
                "description": "Machine Breakdown Scenario - WS-LATHE-02 is down"
            }
        ]

        created_plans = []
        for plan_config in plans_config:
            plan_name = f"PP-DEMO-{plan_config['name_suffix']}-{today.strftime('%Y%m%d')}"

            # Check if exists
            if frappe.db.exists("Production Plan", plan_name):
                created_plans.append(plan_name)
                continue

            pp = frappe.get_doc({
                "doctype": "Production Plan",
                "posting_date": plan_config["posting_date"],
                "company": frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company"),
                "po_items": [
                    {
                        "item_code": item["item_code"],
                        "planned_qty": item["planned_qty"],
                        "warehouse": frappe.db.get_single_value("Stock Settings", "default_warehouse") or "Stores - " + (frappe.db.get_default("company_abbr") or ""),
                        "planned_start_date": item["planned_start_date"]
                    }
                    for item in plan_config["items"]
                ]
            })
            pp.insert(ignore_permissions=True)
            created_plans.append(pp.name)

        self.created_production_plans = created_plans
        return created_plans

    def create_work_orders_and_job_cards(self, production_plan: str) -> Dict:
        """Create Work Orders and Job Cards for a Production Plan."""
        work_orders = []
        job_cards = []

        pp = frappe.get_doc("Production Plan", production_plan)

        for item in pp.po_items:
            # Create Work Order
            wo_name = f"WO-{item.item_code}-{production_plan}"

            if frappe.db.exists("Work Order", wo_name):
                work_orders.append(wo_name)
                # Get existing job cards
                existing_jcs = frappe.get_all("Job Card", filters={"work_order": wo_name}, pluck="name")
                job_cards.extend(existing_jcs)
                continue

            # Get BOM
            bom = frappe.db.get_value("BOM", {"item": item.item_code, "is_default": 1, "is_active": 1}, "name")
            if not bom:
                continue

            # Calculate dates
            start_date = get_datetime(item.planned_start_date or pp.posting_date)
            # Add some randomness to due dates for testing
            due_days = random.randint(3, 7)
            due_date = add_days(start_date, due_days)

            wo = frappe.get_doc({
                "doctype": "Work Order",
                "production_plan": production_plan,
                "production_item": item.item_code,
                "qty": item.planned_qty,
                "bom_no": bom,
                "company": pp.company,
                "wip_warehouse": frappe.db.get_single_value("Manufacturing Settings", "default_wip_warehouse") or "Work In Progress - " + (frappe.db.get_default("company_abbr") or ""),
                "fg_warehouse": frappe.db.get_single_value("Manufacturing Settings", "default_fg_warehouse") or "Finished Goods - " + (frappe.db.get_default("company_abbr") or ""),
                "planned_start_date": start_date,
                "expected_delivery_date": due_date
            })
            wo.insert(ignore_permissions=True)
            wo.submit()
            work_orders.append(wo.name)

            # Create Job Cards for each operation
            bom_doc = frappe.get_doc("BOM", bom)
            current_start = start_date

            for idx, op in enumerate(bom_doc.operations):
                jc_name = f"JC-{wo.name}-{op.operation[:10]}-{idx+1}"

                if frappe.db.exists("Job Card", jc_name):
                    job_cards.append(jc_name)
                    continue

                # Calculate operation duration
                duration_mins = op.time_in_mins * item.planned_qty
                end_time = current_start + timedelta(minutes=duration_mins)

                jc = frappe.get_doc({
                    "doctype": "Job Card",
                    "work_order": wo.name,
                    "operation": op.operation,
                    "workstation": op.workstation,
                    "production_item": item.item_code,
                    "for_quantity": item.planned_qty,
                    "wip_warehouse": wo.wip_warehouse,
                    "company": wo.company,
                    "expected_start_date": current_start,
                    "expected_end_date": end_time,
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

        self.created_work_orders.extend(work_orders)
        self.created_job_cards.extend(job_cards)

        return {"work_orders": work_orders, "job_cards": job_cards}

    def simulate_machine_breakdown(self, workstation: str) -> Dict:
        """
        Simulate a machine breakdown.

        Args:
            workstation: Workstation name to mark as broken

        Returns:
            Dict with affected job cards
        """
        # Mark workstation as Maintenance/Broken
        if frappe.db.exists("Workstation", workstation):
            frappe.db.set_value("Workstation", workstation, "status", "Maintenance")

        # Get affected job cards
        affected_job_cards = frappe.get_all(
            "Job Card",
            filters={
                "workstation": workstation,
                "status": ["in", ["Open", "Work In Progress"]]
            },
            fields=["name", "work_order", "operation", "expected_start_date", "expected_end_date"]
        )

        return {
            "workstation": workstation,
            "status": "Maintenance",
            "affected_job_cards": affected_job_cards,
            "affected_count": len(affected_job_cards)
        }

    def cleanup_demo_data(self) -> Dict:
        """Remove all demo data created by this generator."""
        deleted = {
            "job_cards": 0,
            "work_orders": 0,
            "production_plans": 0,
            "boms": 0,
            "items": 0,
            "workstations": 0
        }

        # Delete in reverse order of creation
        # Job Cards
        for jc in self.created_job_cards:
            if frappe.db.exists("Job Card", jc):
                frappe.delete_doc("Job Card", jc, force=True)
                deleted["job_cards"] += 1

        # Work Orders
        for wo in self.created_work_orders:
            if frappe.db.exists("Work Order", wo):
                frappe.db.set_value("Work Order", wo, "docstatus", 2)
                frappe.delete_doc("Work Order", wo, force=True)
                deleted["work_orders"] += 1

        # Production Plans
        for pp in self.created_production_plans:
            if frappe.db.exists("Production Plan", pp):
                frappe.delete_doc("Production Plan", pp, force=True)
                deleted["production_plans"] += 1

        frappe.db.commit()
        return deleted


@frappe.whitelist()
def generate_demo_data() -> Dict:
    """API endpoint to generate demo data."""
    generator = DemoDataGenerator()
    return generator.generate_all()


@frappe.whitelist()
def simulate_breakdown(workstation: str = "WS-LATHE-02") -> Dict:
    """API endpoint to simulate machine breakdown."""
    generator = DemoDataGenerator()
    return generator.simulate_machine_breakdown(workstation)


@frappe.whitelist()
def get_demo_status() -> Dict:
    """Get status of demo data."""
    return {
        "production_plans": frappe.db.count("Production Plan", {"name": ["like", "PP-DEMO-%"]}),
        "work_orders": frappe.db.count("Work Order", {"production_plan": ["like", "PP-DEMO-%"]}),
        "job_cards": frappe.db.count("Job Card", {"work_order": ["like", "WO-FG-%"]}),
        "workstations": frappe.db.count("Workstation", {"name": ["like", "WS-%"]}),
        "scheduling_runs": frappe.db.count("APS Scheduling Run", {"production_plan": ["like", "PP-DEMO-%"]})
    }
