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
    scheduling_run: str = None,
    scheduling_strategy: str = "Forward Scheduling",
    time_limit_seconds: int = 300,
    makespan_weight: float = 1.0,
    tardiness_weight: float = 10.0,
    allow_overtime: bool = False
) -> dict:
    """
    Run OR-Tools optimal scheduling.

    Args:
        production_plan: Name of ERPNext Production Plan (creates Work Orders and Job Cards automatically)
        work_orders: Comma-separated list of Work Order names (alternative to production_plan)
        scheduling_run: Existing APS Scheduling Run name to update (if provided, uses this record)
        scheduling_strategy: Strategy type
        time_limit_seconds: Solver time limit
        makespan_weight: Weight for makespan objective
        tardiness_weight: Weight for tardiness objective
        allow_overtime: Whether to allow scheduling outside working hours (default False)

    Returns:
        dict: {
            success: bool,
            scheduling_run: str,
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

    # If scheduling_run is provided, use that record and get production_plan from it
    scheduling_run_name = None
    if scheduling_run:
        if not frappe.db.exists("APS Scheduling Run", scheduling_run):
            frappe.throw(_("APS Scheduling Run {0} not found").format(scheduling_run))

        # Get production_plan from the existing record
        production_plan = frappe.db.get_value("APS Scheduling Run", scheduling_run, "production_plan")
        scheduling_run_name = scheduling_run

        # Update status to Running using frappe.db.set_value to avoid version conflicts
        # This bypasses document versioning and won't cause "Document has been modified" errors
        frappe.db.set_value(
            "APS Scheduling Run",
            scheduling_run,
            {
                "run_status": "Running",
                "run_date": now_datetime(),
                "executed_by": frappe.session.user
            },
            update_modified=False  # Don't update modified timestamp yet
        )
        frappe.db.commit()

    # Validate inputs
    if not production_plan and not work_orders:
        frappe.throw(_("Either production_plan or work_orders must be provided"))

    # Parse work orders if provided as string
    work_order_list = None
    if work_orders:
        work_order_list = [wo.strip() for wo in work_orders.split(",") if wo.strip()]

    try:
        # Configure scheduler
        # Note: allow_overtime controls whether operations can be scheduled
        # outside of machine working hours. Set to False to enforce working hours.
        # If allow_overtime=False and no feasible solution is found, it may be due to:
        # - Operation duration > working slot duration
        # - Not enough working hour slots for all operations
        # - Workstation Working Hour not properly configured

        # Convert allow_overtime from string to boolean (Frappe passes strings)
        overtime_allowed = allow_overtime in [True, "true", "True", 1, "1"]

        config = SchedulingConfig(
            time_limit_seconds=cint(time_limit_seconds) or 300,
            objective_weights=ObjectiveWeights(
                makespan_weight=flt(makespan_weight) or 1.0,
                tardiness_weight=flt(tardiness_weight) or 10.0
            ),
            allow_overtime=overtime_allowed
        )

        # Load data
        loader = ERPNextDataLoader()
        if production_plan:
            problem = loader.load_from_production_plan(production_plan, config)
        else:
            problem = loader.load_from_work_orders(work_order_list, config=config)

        if not problem.jobs:
            raise ValueError("No jobs found to schedule")

        # Validate problem data before solving
        validation_errors = []

        # Check if we have jobs
        if not problem.jobs:
            validation_errors.append("No jobs to schedule")

        # Check if we have machines
        if not problem.machines:
            validation_errors.append("No machines/workstations available")

        # Check each job has operations with eligible machines
        for job in problem.jobs:
            if not job.operations:
                validation_errors.append(f"Job {job.id} has no operations")
            for op in job.operations:
                if not op.eligible_machines:
                    validation_errors.append(f"Operation {op.id} has no eligible machines")

        if validation_errors:
            error_msg = "Scheduling validation failed:\n" + "\n".join(validation_errors)
            frappe.log_error(error_msg, "Scheduling Validation Error")
            raise ValueError(error_msg)

        # Run scheduler
        scheduler = ORToolsScheduler(config)
        scheduler.load_data(problem)
        scheduler.build_model()
        solution = scheduler.solve(cint(time_limit_seconds))

        # If no feasible solution, provide diagnostic info
        if not solution.is_feasible:
            diag_info = []
            diag_info.append(f"Jobs: {len(problem.jobs)}")
            diag_info.append(f"Total operations: {sum(len(j.operations) for j in problem.jobs)}")
            diag_info.append(f"Machines: {len(problem.machines)}")
            diag_info.append(f"Solver status: {solution.status.value}")
            diag_info.append(f"Solve time: {solution.solve_time_secs:.2f}s")

            # Check for potential issues
            for job in problem.jobs:
                if job.due_date < now_datetime():
                    diag_info.append(f"WARNING: Job {job.id} has past due date: {job.due_date}")

            frappe.log_error(
                "No feasible solution found.\n" + "\n".join(diag_info),
                "Scheduling - Infeasible"
            )

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

        # Get duration - priority: Job Card time_required > Work Order operation time_in_mins > default
        duration_mins = cint(jc.time_required) if hasattr(jc, 'time_required') and jc.time_required else 60
        if not duration_mins and jc.work_order:
            wo = frappe.get_doc("Work Order", jc.work_order)
            for op in wo.operations:
                if op.operation == jc.operation:
                    duration_mins = cint(op.time_in_mins) or 60
                    break

        jc.expected_start_date = start_dt
        jc.expected_end_date = start_dt + timedelta(minutes=duration_mins)

        # Update time logs (Job Card Time Log child table for tracking)
        if hasattr(jc, "time_logs") and not jc.time_logs:
            jc.append("time_logs", {
                "from_time": start_dt,
                "to_time": jc.expected_end_date,
                "time_in_mins": duration_mins,
                "completed_qty": 0
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
