# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Scheduling Exporters

Exports scheduling results back to ERPNext:
- Updates Job Card scheduled_time_logs
- Creates APS Scheduling Result records
- Updates APS Scheduling Run with metrics
"""

import frappe
from frappe.utils import now_datetime, get_datetime
from datetime import datetime
from typing import List, Optional

from uit_aps.scheduling.ortools.models import (
    SchedulingSolution,
    ScheduledOperation,
    SolverStatus,
)


class SchedulingExporter:
    """
    Exports scheduling solutions to ERPNext.
    """

    def __init__(self, scheduling_run: str = None):
        """
        Initialize exporter.

        Args:
            scheduling_run: Name of APS Scheduling Run record
        """
        self.scheduling_run = scheduling_run

    def export_solution(
        self,
        solution: SchedulingSolution,
        update_job_cards: bool = True,
        create_results: bool = True
    ) -> dict:
        """
        Export complete solution to ERPNext.

        Args:
            solution: SchedulingSolution from solver
            update_job_cards: Whether to update Job Card scheduled times
            create_results: Whether to create APS Scheduling Result records

        Returns:
            dict with export statistics
        """
        stats = {
            "job_cards_updated": 0,
            "results_created": 0,
            "errors": []
        }

        if not solution.is_feasible:
            return stats

        for scheduled_op in solution.operations:
            try:
                if update_job_cards:
                    self._update_job_card(scheduled_op)
                    stats["job_cards_updated"] += 1

                if create_results and self.scheduling_run:
                    self._create_scheduling_result(scheduled_op)
                    stats["results_created"] += 1

            except Exception as e:
                error_msg = f"Error exporting {scheduled_op.job_card_name}: {str(e)}"
                stats["errors"].append(error_msg)
                frappe.log_error(error_msg, "Scheduling Export Error")

        frappe.db.commit()

        # Update scheduling run with metrics
        if self.scheduling_run:
            self._update_scheduling_run(solution, stats)

        return stats

    def _update_job_card(self, scheduled_op: ScheduledOperation) -> None:
        """
        Update Job Card with scheduled times.

        Args:
            scheduled_op: Scheduled operation data
        """
        job_card = frappe.get_doc("Job Card", scheduled_op.job_card_name)

        # Update expected dates
        job_card.expected_start_date = scheduled_op.start_time
        job_card.expected_end_date = scheduled_op.end_time

        # Update time logs if the child table exists
        # ERPNext Job Card uses "time_logs" for actual time tracking
        # We update expected dates which is standard ERPNext behavior
        if hasattr(job_card, "time_logs") and not job_card.time_logs:
            # Only add time log if none exist (don't overwrite actual time logs)
            job_card.append("time_logs", {
                "from_time": scheduled_op.start_time,
                "to_time": scheduled_op.end_time,
                "time_in_mins": scheduled_op.duration_mins,
                "completed_qty": 0
            })

        # Update workstation if assigned
        if scheduled_op.machine_id:
            job_card.workstation = scheduled_op.machine_id

        job_card.flags.ignore_validate_update_after_submit = True
        job_card.save(ignore_permissions=True)

    def _create_scheduling_result(self, scheduled_op: ScheduledOperation) -> None:
        """
        Create APS Scheduling Result record.

        Args:
            scheduled_op: Scheduled operation data
        """
        # Check if result already exists
        existing = frappe.db.exists("APS Scheduling Result", {
            "scheduling_run": self.scheduling_run,
            "job_card": scheduled_op.job_card_name
        })

        if existing:
            # Update existing
            result = frappe.get_doc("APS Scheduling Result", existing)
            result.workstation = scheduled_op.machine_id
            result.planned_start_time = scheduled_op.start_time
            result.planned_end_time = scheduled_op.end_time
            result.is_late = 1 if scheduled_op.is_late else 0
            result.delay_reason = f"Tardiness: {scheduled_op.tardiness_mins} mins" if scheduled_op.is_late else ""
            result.save(ignore_permissions=True)
        else:
            # Create new
            result = frappe.get_doc({
                "doctype": "APS Scheduling Result",
                "scheduling_run": self.scheduling_run,
                "job_card": scheduled_op.job_card_name,
                "workstation": scheduled_op.machine_id,
                "operation": scheduled_op.operation_name,
                "planned_start_time": scheduled_op.start_time,
                "planned_end_time": scheduled_op.end_time,
                "is_late": 1 if scheduled_op.is_late else 0,
                "delay_reason": f"Tardiness: {scheduled_op.tardiness_mins} mins" if scheduled_op.is_late else ""
            })
            result.insert(ignore_permissions=True)

    def _update_scheduling_run(
        self,
        solution: SchedulingSolution,
        stats: dict
    ) -> None:
        """
        Update APS Scheduling Run with solution metrics.

        Uses db_set to avoid document version conflicts when the form is open.

        Args:
            solution: SchedulingSolution
            stats: Export statistics
        """
        try:
            # Use db_set to avoid version conflicts with open documents
            # This bypasses the document versioning system
            update_values = {
                "run_status": "Completed" if solution.is_feasible else "Failed",
                "total_job_cards": len(solution.operations),
                "total_late_jobs": solution.jobs_late,
                "jobs_on_time": solution.jobs_on_time,
                "makespan_minutes": solution.makespan_mins,
                "solver_status": solution.status.value,
                "solve_time_seconds": solution.solve_time_secs,
                "machine_utilization": solution.average_utilization,
                "gap_percentage": solution.gap_percentage
            }

            # Add notes about errors if any
            if stats["errors"]:
                existing_notes = frappe.db.get_value(
                    "APS Scheduling Run", self.scheduling_run, "notes"
                ) or ""
                update_values["notes"] = existing_notes + "\n\nExport Errors:\n" + "\n".join(stats["errors"][:5])

            # Update using db_set_value to avoid version conflicts
            frappe.db.set_value(
                "APS Scheduling Run",
                self.scheduling_run,
                update_values,
                update_modified=True
            )

        except Exception as e:
            frappe.log_error(
                f"Failed to update scheduling run: {str(e)}",
                "Scheduling Run Update Error"
            )


def export_to_gantt_data(solution: SchedulingSolution) -> List[dict]:
    """
    Convert solution to Gantt chart data format.

    Args:
        solution: SchedulingSolution

    Returns:
        List of Gantt chart data items
    """
    gantt_data = []

    for op in solution.operations:
        gantt_item = {
            "id": op.operation_id,
            "name": f"{op.item_code} - {op.operation_name}",
            "start": op.start_time.isoformat() if op.start_time else None,
            "end": op.end_time.isoformat() if op.end_time else None,
            "progress": 0,
            "dependencies": "",
            "custom_class": "bar-late" if op.is_late else "bar-normal",
            "resource": op.machine_id,
            "work_order": op.work_order_name,
            "job_card": op.job_card_name
        }
        gantt_data.append(gantt_item)

    return gantt_data


def export_to_machine_timeline(solution: SchedulingSolution) -> dict:
    """
    Convert solution to machine timeline format.

    Args:
        solution: SchedulingSolution

    Returns:
        Dict mapping machine_id to list of scheduled operations
    """
    timeline = {}

    for op in solution.operations:
        if op.machine_id not in timeline:
            timeline[op.machine_id] = []

        timeline[op.machine_id].append({
            "operation_id": op.operation_id,
            "job_id": op.job_id,
            "item_code": op.item_code,
            "operation_name": op.operation_name,
            "start_time": op.start_time.isoformat() if op.start_time else None,
            "end_time": op.end_time.isoformat() if op.end_time else None,
            "duration_mins": op.duration_mins,
            "is_late": op.is_late
        })

    # Sort each machine's operations by start time
    for machine_id in timeline:
        timeline[machine_id].sort(key=lambda x: x["start_time"] or "")

    return timeline
