# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Frappe API endpoints for APS Scheduling Reports

Provides REST API for:
1. Exporting scheduling comparison to Excel
2. Exporting Gantt data
3. Getting report preview data
"""

import frappe
from frappe import _
from typing import Dict, Any


@frappe.whitelist()
def export_comparison_excel(scheduling_run: str) -> Dict[str, Any]:
    """
    Export scheduling comparison report to Excel.

    Args:
        scheduling_run: APS Scheduling Run name

    Returns:
        Dict with file URL or error:
        {
            "success": bool,
            "file_url": str,
            "file_name": str,
            "error": str (if failed)
        }
    """
    try:
        from uit_aps.scheduling.reports.excel_exporter import export_scheduling_comparison_excel

        if not frappe.db.exists("APS Scheduling Run", scheduling_run):
            return {
                "success": False,
                "error": _("Scheduling Run '{0}' not found").format(scheduling_run)
            }

        result = export_scheduling_comparison_excel(scheduling_run)
        return result

    except ImportError as e:
        return {
            "success": False,
            "error": _("Missing dependency: {0}. Install with: pip install xlsxwriter").format(str(e))
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Export Excel Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def export_gantt_excel(scheduling_run: str) -> Dict[str, Any]:
    """
    Export Gantt chart data to Excel.

    Args:
        scheduling_run: APS Scheduling Run name

    Returns:
        Dict with file URL or error
    """
    try:
        from uit_aps.scheduling.reports.excel_exporter import export_gantt_data_excel

        if not frappe.db.exists("APS Scheduling Run", scheduling_run):
            return {
                "success": False,
                "error": _("Scheduling Run '{0}' not found").format(scheduling_run)
            }

        result = export_gantt_data_excel(scheduling_run)
        return result

    except ImportError as e:
        return {
            "success": False,
            "error": _("Missing dependency: {0}. Install with: pip install xlsxwriter").format(str(e))
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Export Gantt Excel Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def get_report_preview(scheduling_run: str) -> Dict[str, Any]:
    """
    Get preview data for scheduling report.

    Args:
        scheduling_run: APS Scheduling Run name

    Returns:
        Dict with report preview data
    """
    try:
        if not frappe.db.exists("APS Scheduling Run", scheduling_run):
            return {
                "success": False,
                "error": _("Scheduling Run '{0}' not found").format(scheduling_run)
            }

        # Load scheduling run
        run_doc = frappe.get_doc("APS Scheduling Run", scheduling_run)

        # Load scheduling results
        results = frappe.get_all(
            "APS Scheduling Result",
            filters={"scheduling_run": scheduling_run},
            fields=[
                "job_card", "workstation", "operation",
                "planned_start_time", "planned_end_time",
                "is_late", "is_applied"
            ],
            order_by="planned_start_time asc",
            limit=50  # Limit for preview
        )

        # Summary data
        summary = {
            "scheduling_run": scheduling_run,
            "production_plan": run_doc.production_plan,
            "run_status": run_doc.run_status,
            "strategy": run_doc.scheduling_strategy,
            "tier": run_doc.scheduling_tier,
            "total_job_cards": run_doc.total_job_cards,
            "jobs_on_time": run_doc.jobs_on_time,
            "late_jobs": run_doc.total_late_jobs,
            "makespan_minutes": run_doc.makespan_minutes,
            "machine_utilization": run_doc.machine_utilization,
        }

        # Baseline comparison
        comparison = {
            "baseline_makespan": run_doc.baseline_makespan_minutes,
            "baseline_late_jobs": run_doc.baseline_late_jobs,
            "baseline_tardiness": run_doc.baseline_total_tardiness,
            "improvement_makespan": run_doc.improvement_makespan_percent,
            "improvement_late_jobs": run_doc.improvement_late_jobs_percent,
            "improvement_tardiness": run_doc.improvement_tardiness_percent,
            "summary": run_doc.comparison_summary,
        }

        # Constraints
        constraints = {
            "machine_eligibility": run_doc.constraint_machine_eligibility,
            "precedence": run_doc.constraint_precedence,
            "no_overlap": run_doc.constraint_no_overlap,
            "working_hours": run_doc.constraint_working_hours,
            "due_dates": run_doc.constraint_due_dates,
            "setup_time": run_doc.constraint_setup_time,
            "description": run_doc.constraints_description,
        }

        return {
            "success": True,
            "summary": summary,
            "comparison": comparison,
            "constraints": constraints,
            "results_preview": results,
            "total_results": frappe.db.count("APS Scheduling Result", {"scheduling_run": scheduling_run})
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Report Preview Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def get_workstation_utilization(scheduling_run: str) -> Dict[str, Any]:
    """
    Get workstation utilization breakdown for a scheduling run.

    Args:
        scheduling_run: APS Scheduling Run name

    Returns:
        Dict with utilization data per workstation
    """
    try:
        if not frappe.db.exists("APS Scheduling Run", scheduling_run):
            return {
                "success": False,
                "error": _("Scheduling Run '{0}' not found").format(scheduling_run)
            }

        # Get all results grouped by workstation
        results = frappe.db.sql("""
            SELECT
                workstation,
                COUNT(*) as operation_count,
                SUM(TIMESTAMPDIFF(MINUTE, planned_start_time, planned_end_time)) as total_minutes,
                SUM(CASE WHEN is_late = 1 THEN 1 ELSE 0 END) as late_count,
                MIN(planned_start_time) as earliest_start,
                MAX(planned_end_time) as latest_end
            FROM `tabAPS Scheduling Result`
            WHERE scheduling_run = %s
            GROUP BY workstation
            ORDER BY total_minutes DESC
        """, (scheduling_run,), as_dict=True)

        # Calculate utilization for each workstation
        utilization_data = []
        for row in results:
            if row.earliest_start and row.latest_end:
                span_minutes = (row.latest_end - row.earliest_start).total_seconds() / 60
                utilization = (row.total_minutes / span_minutes * 100) if span_minutes > 0 else 0
            else:
                utilization = 0

            utilization_data.append({
                "workstation": row.workstation,
                "operation_count": row.operation_count,
                "total_minutes": row.total_minutes or 0,
                "late_count": row.late_count or 0,
                "utilization_percent": round(utilization, 1),
                "late_percent": round(row.late_count / max(row.operation_count, 1) * 100, 1) if row.operation_count else 0
            })

        return {
            "success": True,
            "scheduling_run": scheduling_run,
            "workstation_utilization": utilization_data
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Utilization Report Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def compare_scheduling_runs(run1: str, run2: str) -> Dict[str, Any]:
    """
    Compare two scheduling runs.

    Args:
        run1: First APS Scheduling Run name
        run2: Second APS Scheduling Run name

    Returns:
        Dict with comparison data
    """
    try:
        if not frappe.db.exists("APS Scheduling Run", run1):
            return {"success": False, "error": _("Scheduling Run '{0}' not found").format(run1)}
        if not frappe.db.exists("APS Scheduling Run", run2):
            return {"success": False, "error": _("Scheduling Run '{0}' not found").format(run2)}

        doc1 = frappe.get_doc("APS Scheduling Run", run1)
        doc2 = frappe.get_doc("APS Scheduling Run", run2)

        comparison = {
            "run1": {
                "name": run1,
                "strategy": doc1.scheduling_strategy,
                "tier": doc1.scheduling_tier,
                "makespan": doc1.makespan_minutes,
                "late_jobs": doc1.total_late_jobs,
                "jobs_on_time": doc1.jobs_on_time,
                "utilization": doc1.machine_utilization,
                "solve_time": doc1.solve_time_seconds,
            },
            "run2": {
                "name": run2,
                "strategy": doc2.scheduling_strategy,
                "tier": doc2.scheduling_tier,
                "makespan": doc2.makespan_minutes,
                "late_jobs": doc2.total_late_jobs,
                "jobs_on_time": doc2.jobs_on_time,
                "utilization": doc2.machine_utilization,
                "solve_time": doc2.solve_time_seconds,
            },
            "differences": {
                "makespan_diff": (doc1.makespan_minutes or 0) - (doc2.makespan_minutes or 0),
                "late_jobs_diff": (doc1.total_late_jobs or 0) - (doc2.total_late_jobs or 0),
                "utilization_diff": (doc1.machine_utilization or 0) - (doc2.machine_utilization or 0),
            }
        }

        # Determine winner for each metric
        comparison["winners"] = {
            "makespan": run1 if (doc1.makespan_minutes or float('inf')) < (doc2.makespan_minutes or float('inf')) else run2,
            "late_jobs": run1 if (doc1.total_late_jobs or float('inf')) < (doc2.total_late_jobs or float('inf')) else run2,
            "utilization": run1 if (doc1.machine_utilization or 0) > (doc2.machine_utilization or 0) else run2,
        }

        return {
            "success": True,
            "comparison": comparison
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Compare Runs Error")
        return {
            "success": False,
            "error": str(e)
        }
