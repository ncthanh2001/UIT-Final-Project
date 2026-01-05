# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Scheduling API

Frappe whitelisted methods for OR-Tools scheduling operations.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, getdate, cint, flt
from datetime import datetime, timedelta
from typing import List, Optional


@frappe.whitelist()
def run_ortools_scheduling(
    production_plan: str = None,
    work_orders: str = None,
    scheduling_strategy: str = "Forward Scheduling",
    time_limit_seconds: int = 300,
    makespan_weight: float = 1.0,
    tardiness_weight: float = 10.0,
    create_scheduling_run: bool = True
) -> dict:
    """
    Run OR-Tools optimal scheduling.

    Args:
        production_plan: Name of ERPNext Production Plan (creates Work Orders and Job Cards automatically)
        work_orders: Comma-separated list of Work Order names (alternative to production_plan)
        scheduling_strategy: Strategy type
        time_limit_seconds: Solver time limit
        makespan_weight: Weight for makespan objective
        tardiness_weight: Weight for tardiness objective
        create_scheduling_run: Whether to create APS Scheduling Run record

    Returns:
        dict: {
            success: bool,
            scheduling_run: str (if created),
            status: str,
            makespan_minutes: int,
            total_jobs: int,
            jobs_on_time: int,
            jobs_late: int,
            solve_time_seconds: float,
            message: str
        }
    """
    from uit_aps.scheduling.ortools.models import SchedulingConfig, ObjectiveWeights
    from uit_aps.scheduling.ortools.scheduler import ORToolsScheduler
    from uit_aps.scheduling.data.erpnext_loader import ERPNextDataLoader
    from uit_aps.scheduling.data.exporters import SchedulingExporter

    # Validate inputs
    if not production_plan and not work_orders:
        frappe.throw(_("Either production_plan or work_orders must be provided"))

    # Parse work orders if provided as string
    work_order_list = None
    if work_orders:
        work_order_list = [wo.strip() for wo in work_orders.split(",") if wo.strip()]

    # Create scheduling run record
    scheduling_run_name = None
    if create_scheduling_run:
        scheduling_run = frappe.get_doc({
            "doctype": "APS Scheduling Run",
            "production_plan": production_plan,
            "run_status": "Running",
            "scheduling_strategy": scheduling_strategy,
            "run_date": now_datetime(),
            "executed_by": frappe.session.user
        })
        scheduling_run.insert(ignore_permissions=True)
        scheduling_run_name = scheduling_run.name
        frappe.db.commit()

    try:
        # Configure scheduler
        config = SchedulingConfig(
            time_limit_seconds=cint(time_limit_seconds) or 300,
            objective_weights=ObjectiveWeights(
                makespan_weight=flt(makespan_weight) or 1.0,
                tardiness_weight=flt(tardiness_weight) or 10.0
            )
        )

        # Load data
        loader = ERPNextDataLoader()
        if production_plan:
            problem = loader.load_from_production_plan(production_plan, config)
        else:
            problem = loader.load_from_work_orders(work_order_list, config=config)

        if not problem.jobs:
            raise ValueError("No jobs found to schedule")

        # Run scheduler
        scheduler = ORToolsScheduler(config)
        scheduler.load_data(problem)
        scheduler.build_model()
        solution = scheduler.solve(cint(time_limit_seconds))

        # Export results
        exporter = SchedulingExporter(scheduling_run=scheduling_run_name)
        export_stats = exporter.export_solution(
            solution,
            update_job_cards=True,
            create_results=True
        )

        # Prepare response
        result = {
            "success": solution.is_feasible,
            "scheduling_run": scheduling_run_name,
            "status": solution.status.value,
            "makespan_minutes": solution.makespan_mins,
            "total_jobs": len(problem.jobs),
            "total_operations": len(solution.operations),
            "jobs_on_time": solution.jobs_on_time,
            "jobs_late": solution.jobs_late,
            "total_tardiness_minutes": solution.total_tardiness_mins,
            "average_utilization": round(solution.average_utilization, 2),
            "solve_time_seconds": round(solution.solve_time_secs, 2),
            "job_cards_updated": export_stats["job_cards_updated"],
            "message": _("Scheduling completed successfully") if solution.is_feasible else _("No feasible solution found")
        }

        return result

    except Exception as e:
        # Update scheduling run with error
        if scheduling_run_name:
            frappe.db.set_value("APS Scheduling Run", scheduling_run_name, {
                "run_status": "Failed",
                "notes": str(e)[:500]
            })
            frappe.db.commit()

        frappe.log_error(str(e), "OR-Tools Scheduling Error")
        raise


@frappe.whitelist()
def get_scheduling_results(scheduling_run: str) -> dict:
    """
    Get scheduling results for a run.

    Args:
        scheduling_run: APS Scheduling Run name

    Returns:
        dict with run info and results
    """
    run = frappe.get_doc("APS Scheduling Run", scheduling_run)

    results = frappe.get_all(
        "APS Scheduling Result",
        filters={"scheduling_run": scheduling_run},
        fields=[
            "name", "job_card", "workstation", "operation",
            "planned_start_time", "planned_end_time",
            "is_late", "delay_reason"
        ],
        order_by="planned_start_time asc"
    )

    return {
        "scheduling_run": {
            "name": run.name,
            "production_plan": run.production_plan,
            "status": run.run_status,
            "strategy": run.scheduling_strategy,
            "total_job_cards": run.total_job_cards,
            "total_late_jobs": run.total_late_jobs,
            "run_date": run.run_date
        },
        "results": results
    }


@frappe.whitelist()
def get_gantt_data(scheduling_run: str) -> List[dict]:
    """
    Get Gantt chart data for a scheduling run.

    Args:
        scheduling_run: APS Scheduling Run name

    Returns:
        List of Gantt chart items
    """
    results = frappe.get_all(
        "APS Scheduling Result",
        filters={"scheduling_run": scheduling_run},
        fields=[
            "name", "job_card", "workstation", "operation",
            "planned_start_time", "planned_end_time", "is_late"
        ],
        order_by="planned_start_time asc"
    )

    gantt_data = []
    for r in results:
        # Get additional info from Job Card
        job_card = frappe.get_doc("Job Card", r.job_card)

        gantt_data.append({
            "id": r.name,
            "name": f"{job_card.production_item or ''} - {r.operation or 'Operation'}",
            "start": r.planned_start_time.isoformat() if r.planned_start_time else None,
            "end": r.planned_end_time.isoformat() if r.planned_end_time else None,
            "progress": 0,
            "custom_class": "bar-late" if r.is_late else "bar-normal",
            "resource": r.workstation,
            "job_card": r.job_card,
            "work_order": job_card.work_order
        })

    return gantt_data


@frappe.whitelist()
def get_machine_timeline(scheduling_run: str) -> dict:
    """
    Get machine timeline data for a scheduling run.

    Args:
        scheduling_run: APS Scheduling Run name

    Returns:
        Dict mapping machine_id to scheduled operations
    """
    results = frappe.get_all(
        "APS Scheduling Result",
        filters={"scheduling_run": scheduling_run},
        fields=[
            "name", "job_card", "workstation", "operation",
            "planned_start_time", "planned_end_time", "is_late"
        ],
        order_by="workstation asc, planned_start_time asc"
    )

    timeline = {}
    for r in results:
        machine_id = r.workstation or "Unassigned"

        if machine_id not in timeline:
            timeline[machine_id] = []

        # Get Job Card info
        job_card = frappe.get_doc("Job Card", r.job_card)

        duration_mins = 0
        if r.planned_start_time and r.planned_end_time:
            duration_mins = int((r.planned_end_time - r.planned_start_time).total_seconds() / 60)

        timeline[machine_id].append({
            "result_id": r.name,
            "job_card": r.job_card,
            "work_order": job_card.work_order,
            "item_code": job_card.production_item,
            "operation": r.operation,
            "start_time": r.planned_start_time.isoformat() if r.planned_start_time else None,
            "end_time": r.planned_end_time.isoformat() if r.planned_end_time else None,
            "duration_mins": duration_mins,
            "is_late": r.is_late
        })

    return timeline


@frappe.whitelist()
def reschedule_from_job_card(
    job_card: str,
    new_workstation: str = None,
    new_start_time: str = None
) -> dict:
    """
    Reschedule a single Job Card (manual adjustment).

    Args:
        job_card: Job Card name
        new_workstation: New workstation assignment
        new_start_time: New start time (datetime string)

    Returns:
        dict with update status
    """
    jc = frappe.get_doc("Job Card", job_card)

    if new_workstation:
        jc.workstation = new_workstation

    if new_start_time:
        start_dt = datetime.fromisoformat(new_start_time)
        duration_mins = jc.time_in_mins or 60

        jc.expected_start_date = start_dt
        jc.expected_end_date = start_dt + timedelta(minutes=duration_mins)

        # Update scheduled time logs
        jc.scheduled_time_logs = []
        jc.append("scheduled_time_logs", {
            "from_time": start_dt,
            "to_time": jc.expected_end_date,
            "time_in_mins": duration_mins
        })

    jc.flags.ignore_validate_update_after_submit = True
    jc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "job_card": job_card,
        "workstation": jc.workstation,
        "expected_start_date": jc.expected_start_date,
        "expected_end_date": jc.expected_end_date
    }


@frappe.whitelist()
def get_scheduling_statistics(production_plan: str = None, days: int = 30) -> dict:
    """
    Get scheduling statistics and KPIs.

    Args:
        production_plan: Filter by production plan
        days: Number of days to analyze

    Returns:
        dict with statistics
    """
    from frappe.utils import add_days

    filters = {"run_status": "Completed"}
    if production_plan:
        filters["production_plan"] = production_plan

    # Get recent runs
    runs = frappe.get_all(
        "APS Scheduling Run",
        filters=filters,
        fields=[
            "name", "total_job_cards", "total_late_jobs",
            "run_date", "scheduling_strategy"
        ],
        order_by="run_date desc",
        limit=100
    )

    if not runs:
        return {
            "total_runs": 0,
            "average_jobs_per_run": 0,
            "average_on_time_rate": 0,
            "most_used_strategy": None
        }

    total_jobs = sum(r.total_job_cards or 0 for r in runs)
    total_late = sum(r.total_late_jobs or 0 for r in runs)

    on_time_rate = ((total_jobs - total_late) / total_jobs * 100) if total_jobs > 0 else 0

    # Most used strategy
    strategy_counts = {}
    for r in runs:
        strategy = r.scheduling_strategy or "Unknown"
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

    most_used = max(strategy_counts.items(), key=lambda x: x[1])[0] if strategy_counts else None

    return {
        "total_runs": len(runs),
        "total_jobs_scheduled": total_jobs,
        "total_late_jobs": total_late,
        "average_jobs_per_run": round(total_jobs / len(runs), 1) if runs else 0,
        "average_on_time_rate": round(on_time_rate, 1),
        "most_used_strategy": most_used,
        "strategy_breakdown": strategy_counts
    }
