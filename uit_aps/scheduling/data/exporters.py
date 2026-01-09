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
    SchedulingConfig,
)
from uit_aps.scheduling.ortools.baseline import OptimizationComparison


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
        update_job_cards: bool = False,
        create_results: bool = True,
        baseline_comparison: OptimizationComparison = None,
        config: SchedulingConfig = None
    ) -> dict:
        """
        Export complete solution to ERPNext.

        IMPORTANT: By default, update_job_cards=False to allow user review
        before applying recommendations. User must explicitly approve and
        apply using the apply_scheduling_results API.

        Args:
            solution: SchedulingSolution from solver
            update_job_cards: Whether to update Job Card scheduled times (default False)
            create_results: Whether to create APS Scheduling Result records
            baseline_comparison: OptimizationComparison with baseline metrics
            config: SchedulingConfig with constraint settings

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
                    self._create_scheduling_result(scheduled_op, is_applied=update_job_cards)
                    stats["results_created"] += 1

            except Exception as e:
                error_msg = f"Error exporting {scheduled_op.job_card_name}: {str(e)}"
                stats["errors"].append(error_msg)
                frappe.log_error(error_msg, "Scheduling Export Error")

        frappe.db.commit()

        # Update scheduling run with metrics, constraints, and baseline comparison
        if self.scheduling_run:
            self._update_scheduling_run(
                solution,
                stats,
                applied=update_job_cards,
                baseline_comparison=baseline_comparison,
                config=config
            )

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

    def _create_scheduling_result(self, scheduled_op: ScheduledOperation, is_applied: bool = False) -> None:
        """
        Create APS Scheduling Result record.

        Args:
            scheduled_op: Scheduled operation data
            is_applied: Whether this result has been applied to Job Card (default False)
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
            result.is_applied = 1 if is_applied else 0
            result.applied_at = now_datetime() if is_applied else None
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
                "delay_reason": f"Tardiness: {scheduled_op.tardiness_mins} mins" if scheduled_op.is_late else "",
                "is_applied": 1 if is_applied else 0,
                "applied_at": now_datetime() if is_applied else None
            })
            result.insert(ignore_permissions=True)

    def _update_scheduling_run(
        self,
        solution: SchedulingSolution,
        stats: dict,
        applied: bool = False,
        baseline_comparison: OptimizationComparison = None,
        config: SchedulingConfig = None
    ) -> None:
        """
        Update APS Scheduling Run with solution metrics, constraints, and comparison.

        Uses db_set to avoid document version conflicts when the form is open.

        Args:
            solution: SchedulingSolution
            stats: Export statistics
            applied: Whether results have been applied to Job Cards
            baseline_comparison: OptimizationComparison with baseline metrics
            config: SchedulingConfig with constraint settings
        """
        try:
            # Determine run status based on feasibility and applied state
            if not solution.is_feasible:
                run_status = "Failed"
            elif applied:
                run_status = "Applied"
            else:
                run_status = "Pending Approval"

            # Use db_set to avoid version conflicts with open documents
            # This bypasses the document versioning system
            update_values = {
                "run_status": run_status,
                "total_job_cards": len(solution.operations),
                "total_operations": len(solution.operations),
                "applied_operations": stats["job_cards_updated"] if applied else 0,
                "total_late_jobs": solution.jobs_late,
                "jobs_on_time": solution.jobs_on_time,
                "makespan_minutes": solution.makespan_mins,
                "solver_status": solution.status.value,
                "solve_time_seconds": solution.solve_time_secs,
                "machine_utilization": solution.average_utilization,
                "gap_percentage": solution.gap_percentage
            }

            # Add constraint information
            update_values["constraint_machine_eligibility"] = 1  # Always applied
            update_values["constraint_precedence"] = 1  # Always applied
            update_values["constraint_no_overlap"] = 1  # Always applied
            update_values["constraint_due_dates"] = 1  # Always applied

            # Working hours constraint depends on config
            if config:
                update_values["constraint_working_hours"] = 0 if config.allow_overtime else 1
                update_values["constraint_setup_time"] = 1 if config.min_gap_between_ops_mins > 0 else 0
            else:
                update_values["constraint_working_hours"] = 1
                update_values["constraint_setup_time"] = 0

            # Generate constraints description
            constraints_desc = self._generate_constraints_description(config)
            update_values["constraints_description"] = constraints_desc

            # Add baseline comparison data
            if baseline_comparison:
                update_values["baseline_makespan_minutes"] = baseline_comparison.baseline_makespan_minutes
                update_values["baseline_late_jobs"] = baseline_comparison.baseline_late_jobs
                update_values["baseline_total_tardiness"] = baseline_comparison.baseline_total_tardiness
                update_values["improvement_makespan_percent"] = round(baseline_comparison.improvement_makespan_percent, 2)
                update_values["improvement_late_jobs_percent"] = round(baseline_comparison.improvement_late_jobs_percent, 2)
                update_values["improvement_tardiness_percent"] = round(baseline_comparison.improvement_tardiness_percent, 2)
                update_values["comparison_summary"] = baseline_comparison.summary

            # Add applied info if applied
            if applied:
                update_values["applied_at"] = now_datetime()
                update_values["applied_by"] = frappe.session.user

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

    def _generate_constraints_description(self, config: SchedulingConfig = None) -> str:
        """
        Generate human-readable description of applied constraints.

        Args:
            config: SchedulingConfig with constraint settings

        Returns:
            Formatted description string
        """
        lines = [
            "Các ràng buộc được áp dụng trong quá trình tối ưu hóa:",
            "",
            "1. Machine Eligibility (Phù hợp máy): Mỗi operation chỉ được lập lịch trên máy (workstation) có khả năng thực hiện operation đó.",
            "",
            "2. Operation Precedence (Thứ tự ưu tiên): Các operation trong cùng một Work Order phải được thực hiện theo đúng thứ tự quy định trong BOM.",
            "",
            "3. No Overlap (Không chồng lấn): Mỗi máy chỉ có thể xử lý một operation tại một thời điểm.",
            "",
            "4. Due Date Respect (Tôn trọng deadline): Ưu tiên tối ưu hóa để hoàn thành job trước deadline, giảm thiểu số job trễ và tổng thời gian trễ.",
        ]

        if config:
            if not config.allow_overtime:
                lines.append("")
                lines.append("5. Working Hours (Giờ làm việc): Lập lịch trong giờ làm việc của workstation (nếu có cấu hình).")

            if config.min_gap_between_ops_mins > 0:
                lines.append("")
                lines.append(f"6. Setup/Gap Time (Thời gian setup): Khoảng cách tối thiểu {config.min_gap_between_ops_mins} phút giữa các operation.")

            lines.append("")
            lines.append(f"Hàm mục tiêu: Minimize (Makespan × {config.objective_weights.makespan_weight} + Tardiness × {config.objective_weights.tardiness_weight})")
        else:
            lines.append("")
            lines.append("Hàm mục tiêu: Minimize (Makespan + Tardiness)")

        return "\n".join(lines)


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
