# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Gantt Chart API

Frappe whitelisted methods for Gantt Chart data.
"""

import frappe
from frappe import _
from frappe.utils import getdate, get_datetime, flt, cint
from typing import Dict, List
import json


@frappe.whitelist()
def get_job_cards_for_gantt(scheduling_run: str = None, production_plan: str = None) -> Dict:
    """
    Lay danh sach Job Cards de hien thi tren Gantt Chart
    
    Args:
        scheduling_run: Ten cua APS Scheduling Run (optional)
        production_plan: Ten cua Production Plan (optional)
        
    Returns:
        dict: Job cards data va workstations
    """
    
    if scheduling_run:
        # Neu co scheduling_run, lay tu APS Scheduling Result
        return get_scheduled_jobs(scheduling_run)
    else:
        # Khong co scheduling_run, lay tat ca Job Cards
        return get_all_job_cards(production_plan=production_plan)


def get_scheduled_jobs(scheduling_run: str) -> Dict:
    """Lay jobs tu APS Scheduling Result"""
    
    if not frappe.db.exists("APS Scheduling Run", scheduling_run):
        frappe.throw(_("APS Scheduling Run {0} not found").format(scheduling_run))
    
    # Lay scheduling run info
    run_doc = frappe.get_doc("APS Scheduling Run", scheduling_run)
    
    # Lay tat ca scheduling results
    results = frappe.get_all(
        "APS Scheduling Result",
        filters={"parent": scheduling_run},
        fields=[
            "name",
            "job_card",
            "workstation",
            "scheduled_start_time",
            "scheduled_end_time",
            "duration_hours",
            "status",
            "priority"
        ],
        order_by="scheduled_start_time"
    )
    
    jobs = []
    for result in results:
        # Lay thong tin job card
        job_card = frappe.db.get_value(
            "Job Card",
            result.job_card,
            ["name", "work_order", "operation", "status"],
            as_dict=True
        )
        
        if not job_card:
            continue
        
        # Tinh toan risk status
        status = calculate_risk_status(result, job_card)
        
        jobs.append({
            "id": result.name,
            "jobCode": job_card.work_order or "N/A",
            "operation": job_card.operation or "N/A",
            "machine": result.workstation or "N/A",
            "startTime": result.scheduled_start_time,
            "endTime": result.scheduled_end_time,
            "durationHours": flt(result.duration_hours),
            "status": status,
            "progress": get_job_progress(job_card),
            "priority": result.priority or "medium",
            "jobCard": result.job_card
        })
    
    # Lay workstations
    workstations = get_workstations_data()
    
    # Lay KPI
    kpi = calculate_kpi_from_run(run_doc)
    
    return {
        "jobs": jobs,
        "workstations": workstations,
        "kpi": kpi,
        "schedulingRun": {
            "name": run_doc.name,
            "status": run_doc.run_status,
            "startTime": run_doc.run_date,
            "productionPlan": run_doc.production_plan
        }
    }


def get_all_job_cards(production_plan: str = None) -> Dict:
    """Lay tat ca Job Cards chua schedule"""
    
    # Build filters
    filters = {
        "docstatus": ["<", 2],  # Chua cancel
        "expected_start_date": ["is", "set"],
        "status": ["!=", "Completed"]  # Khong lay job cards da complete
    }
    
    # Neu co production_plan, filter theo production_plan
    if production_plan:
        # Lay danh sach work orders thuoc production plan
        work_orders = get_work_orders_from_production_plan(production_plan)
        
        if work_orders:
            filters["work_order"] = ["in", work_orders]
        else:
            # Neu khong co work orders, tra ve empty
            return {
                "jobs": [],
                "workstations": get_workstations_data(),
                "kpi": {
                    "makespan": 0,
                    "lateJobs": 0,
                    "avgUtilization": 0,
                    "scheduleStability": 0
                },
                "schedulingRun": None
            }
    
    # Lay job cards co expected dates va chua complete
    job_cards = frappe.get_all(
        "Job Card",
        filters=filters,
        fields=[
            "name",
            "work_order",
            "operation",
            "workstation",
            "expected_start_date",
            "expected_end_date",
            "total_time_in_mins",
            "status"
        ],
        order_by="expected_start_date",
        limit=100
    )
    
    jobs = []
    for jc in job_cards:
        # Tinh duration
        if jc.expected_end_date and jc.expected_start_date:
            start = get_datetime(jc.expected_start_date)
            end = get_datetime(jc.expected_end_date)
            duration_hours = (end - start).total_seconds() / 3600
        else:
            duration_hours = flt(jc.total_time_in_mins or 0) / 60
        
        # Risk status
        status = get_status_from_job_card(jc)
        
        jobs.append({
            "id": jc.name,
            "jobCode": jc.work_order or "N/A",
            "operation": jc.operation or "N/A",
            "machine": jc.workstation or "N/A",
            "startTime": jc.expected_start_date,
            "endTime": jc.expected_end_date,
            "durationHours": duration_hours,
            "status": status,
            "progress": get_job_card_progress(jc),
            "priority": "medium",  # Default
            "jobCard": jc.name
        })
    
    # Lay workstations
    workstations = get_workstations_data()
    
    # KPI mac dinh
    kpi = {
        "makespan": len(set([j["jobCode"] for j in jobs])),
        "lateJobs": len([j for j in jobs if j["status"] == "late"]),
        "avgUtilization": 75,
        "scheduleStability": 80
    }
    
    return {
        "jobs": jobs,
        "workstations": workstations,
        "kpi": kpi,
        "schedulingRun": None
    }


def get_workstations_data() -> List[Dict]:
    """Lay danh sach Plant Floor va Workstations"""
    
    # Check xem Plant Floor doctype co ton tai khong
    if not frappe.db.exists("DocType", "Plant Floor"):
        # Neu khong co Plant Floor, tra ve empty hoac tao mock data
        return get_mock_workstations()
    
    try:
        # Lay Plant Floor fields that exist
        floors = frappe.get_all(
            "Plant Floor",
            fields=["name"],
            order_by="name"
        )
    except Exception as e:
        frappe.log_error(f"Error getting Plant Floor: {str(e)}")
        return get_mock_workstations()
    
    result = []
    for floor in floors:
        # Lay workstations cua floor nay
        try:
            workstations = frappe.get_all(
                "Workstation",
                filters={"plant_floor": floor.name},
                fields=[
                    "name",
                    "workstation_name",
                    "status",
                    "production_capacity"
                ],
                order_by="name"
            )
        except Exception as e:
            # Neu khong co field plant_floor, lay tat ca workstations
            workstations = frappe.get_all(
                "Workstation",
                fields=[
                    "name",
                    "workstation_name",
                    "status",
                    "production_capacity"
                ],
                order_by="name",
                limit=10
            )
        
        ws_list = []
        for ws in workstations:
            # Tinh utilization
            utilization = calculate_workstation_utilization(ws.name)
            
            ws_list.append({
                "id": ws.name,
                "name": ws.workstation_name or ws.name,
                "status": ws.status or "Production",
                "utilization": utilization
            })
        
        result.append({
            "floor": floor.name,
            "description": "",
            "workstations": ws_list
        })
    
    # Neu khong co floors, tra ve tat ca workstations
    if not result:
        return get_workstations_without_floors()
    
    return result


def get_mock_workstations() -> List[Dict]:
    """Tra ve mock workstations neu khong co Plant Floor"""
    
    # Lay tat ca workstations
    try:
        workstations = frappe.get_all(
            "Workstation",
            fields=[
                "name",
                "workstation_name",
                "status",
                "production_capacity"
            ],
            order_by="name",
            limit=20
        )
    except Exception as e:
        frappe.log_error(f"Error getting Workstations: {str(e)}")
        return []
    
    ws_list = []
    for ws in workstations:
        utilization = calculate_workstation_utilization(ws.name)
        
        ws_list.append({
            "id": ws.name,
            "name": ws.workstation_name or ws.name,
            "status": ws.status or "Production",
            "utilization": utilization
        })
    
    return [{
        "floor": "All Workstations",
        "description": "No Plant Floor configured",
        "workstations": ws_list
    }]


def get_workstations_without_floors() -> List[Dict]:
    """Lay workstations khong phan theo floor"""
    return get_mock_workstations()


def get_work_orders_from_production_plan(production_plan: str) -> List[str]:
    """
    Lay danh sach Work Orders tu Production Plan
    
    Args:
        production_plan: Ten cua Production Plan
        
    Returns:
        List[str]: Danh sach Work Order names
    """
    
    if not frappe.db.exists("Production Plan", production_plan):
        return []
    
    # Lay work orders tu Production Plan
    # Work Orders duoc tao tu Production Plan Item (child table)
    work_orders = frappe.get_all(
        "Work Order",
        filters={
            "production_plan": production_plan,
            "docstatus": ["<", 2]  # Chua cancel
        },
        fields=["name"],
        pluck="name"
    )
    
    return work_orders


def calculate_workstation_utilization(workstation: str) -> float:
    """Tinh utilization cua workstation"""
    
    # Dem so job cards dang chay tren workstation
    active_jobs = frappe.db.count(
        "Job Card",
        {
            "workstation": workstation,
            "status": ["in", ["Work In Progress", "Open"]],
            "docstatus": 1
        }
    )
    
    # Capacity cua workstation
    capacity = frappe.db.get_value("Workstation", workstation, "production_capacity") or 1
    
    # Tinh %
    utilization = (active_jobs / capacity * 100) if capacity > 0 else 0
    
    return min(utilization, 100)


def calculate_risk_status(result, job_card) -> str:
    """Tinh toan risk status"""
    
    # Neu job card da late
    if job_card.status == "Completed":
        return "ontime"
    
    # Check xem co at risk khong
    now = get_datetime()
    start = get_datetime(result.scheduled_start_time)
    end = get_datetime(result.scheduled_end_time)
    
    if now > end:
        return "late"
    elif now > start and now < end:
        # Dang chay, check progress
        progress = get_job_progress(job_card)
        expected_progress = ((now - start).total_seconds() / (end - start).total_seconds()) * 100
        
        if progress < expected_progress - 20:
            return "atrisk"
    
    return "ontime"


def get_status_from_job_card(job_card) -> str:
    """Lay status tu job card"""
    
    if job_card.status == "Completed":
        return "ontime"
    
    # Check expected_end_date
    if job_card.expected_end_date:
        end = getdate(job_card.expected_end_date)
        today = getdate()
        
        if today > end:
            return "late"
        elif (end - today).days <= 1:
            return "atrisk"
    
    return "ontime"


def get_job_progress(job_card) -> int:
    """Lay progress cua job"""
    
    if isinstance(job_card, dict):
        status = job_card.get("status")
    else:
        status = job_card.status
    
    status_progress = {
        "Open": 0,
        "Work In Progress": 50,
        "Completed": 100,
        "On Hold": 25
    }
    
    return status_progress.get(status, 0)


def get_job_card_progress(job_card) -> int:
    """Lay progress tu job card object"""
    return get_job_progress(job_card)


def calculate_kpi_from_run(run_doc) -> Dict:
    """Tinh KPI tu scheduling run"""
    
    return {
        "makespan": cint(run_doc.makespan_days or 0),
        "lateJobs": cint(run_doc.total_late_jobs or 0),
        "avgUtilization": flt(run_doc.avg_machine_utilization or 0),
        "scheduleStability": 85  # Mock value
    }


@frappe.whitelist()
def update_job_schedule(job_id: str, start_time: str, end_time: str) -> Dict:
    """
    Cap nhat schedule cua job
    
    Args:
        job_id: ID cua job (APS Scheduling Result name hoac Job Card name)
        start_time: New start time
        end_time: New end time
        
    Returns:
        dict: Success status
    """
    
    # Check xem la Scheduling Result hay Job Card
    if frappe.db.exists("APS Scheduling Result", job_id):
        doc = frappe.get_doc("APS Scheduling Result", job_id)
        doc.scheduled_start_time = start_time
        doc.scheduled_end_time = end_time
        doc.save(ignore_permissions=True)
    elif frappe.db.exists("Job Card", job_id):
        doc = frappe.get_doc("Job Card", job_id)
        doc.expected_start_date = start_time
        doc.expected_end_date = end_time
        doc.save(ignore_permissions=True)
    else:
        frappe.throw(_("Job {0} not found").format(job_id))
    
    frappe.db.commit()
    
    return {"success": True, "message": "Updated successfully"}


@frappe.whitelist()
def get_production_plans() -> List[str]:
    """
    Lay danh sach Production Plans de filter
    
    Returns:
        list: Danh sach Production Plan names
    """
    try:
        production_plans = frappe.get_all(
            "Production Plan",
            filters={
                "docstatus": ["<", 2]  # Khong lay cancelled
            },
            fields=["name"],
            order_by="modified desc",
            limit=100
        )
        
        return [pp["name"] for pp in production_plans]
    except Exception as e:
        frappe.log_error(f"Error fetching production plans: {str(e)}", "GET_PRODUCTION_PLANS")
        return []

