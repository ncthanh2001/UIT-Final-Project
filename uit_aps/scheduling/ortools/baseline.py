# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Baseline Scheduling Algorithms

Provides simple baseline scheduling algorithms (FIFO, EDD) for comparison
with optimized schedules from OR-Tools solver.

These baselines help demonstrate the improvement gained from optimization.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

from uit_aps.scheduling.ortools.models import (
    SchedulingProblem,
    SchedulingSolution,
    ScheduledOperation,
    SolverStatus,
    Job,
    Operation,
)


@dataclass
class BaselineResult:
    """Results from baseline scheduling algorithm."""
    makespan_minutes: int = 0
    total_tardiness_minutes: int = 0
    late_jobs: int = 0
    jobs_on_time: int = 0
    operations: List[ScheduledOperation] = None
    algorithm: str = "FIFO"

    def __post_init__(self):
        if self.operations is None:
            self.operations = []


class BaselineScheduler:
    """
    Simple baseline scheduling algorithms for comparison.

    Supports:
    - FIFO (First In First Out): Schedule jobs in order of arrival/creation
    - EDD (Earliest Due Date): Schedule jobs by due date
    """

    def __init__(self, problem: SchedulingProblem):
        """
        Initialize baseline scheduler.

        Args:
            problem: SchedulingProblem with jobs and machines
        """
        self.problem = problem
        self.schedule_start = problem.config.schedule_start or datetime.now()

    def compute_fifo_baseline(self) -> BaselineResult:
        """
        Compute FIFO (First In First Out) baseline schedule.

        FIFO schedules jobs in the order they were created/submitted,
        without any optimization. Each operation is scheduled as soon as
        possible on its assigned machine.

        Returns:
            BaselineResult with metrics
        """
        # Sort jobs by ID/creation order (assuming ID reflects creation order)
        sorted_jobs = sorted(self.problem.jobs, key=lambda j: j.id)

        return self._compute_schedule(sorted_jobs, "FIFO")

    def compute_edd_baseline(self) -> BaselineResult:
        """
        Compute EDD (Earliest Due Date) baseline schedule.

        EDD schedules jobs by their due date, prioritizing jobs with
        earlier deadlines. This is a simple heuristic that often performs
        well for minimizing tardiness.

        Returns:
            BaselineResult with metrics
        """
        # Sort jobs by due date (earliest first)
        sorted_jobs = sorted(self.problem.jobs, key=lambda j: j.due_date or datetime.max)

        return self._compute_schedule(sorted_jobs, "EDD")

    def _compute_schedule(
        self,
        sorted_jobs: List[Job],
        algorithm: str
    ) -> BaselineResult:
        """
        Compute schedule for sorted jobs using a simple greedy approach.

        For each job in order:
        - Schedule operations in sequence order
        - Each operation starts at the earliest available time on its machine

        Args:
            sorted_jobs: Jobs in scheduling order
            algorithm: Name of algorithm for labeling

        Returns:
            BaselineResult with metrics
        """
        # Track machine availability (next available time in minutes from start)
        machine_available: Dict[str, int] = {
            m.id: 0 for m in self.problem.machines
        }

        # Track job completion times
        scheduled_operations: List[ScheduledOperation] = []
        makespan = 0
        total_tardiness = 0
        late_jobs = 0
        jobs_on_time = 0

        min_gap = self.problem.config.min_gap_between_ops_mins

        for job in sorted_jobs:
            # Sort operations by sequence
            sorted_ops = sorted(job.operations, key=lambda o: o.sequence)

            # Track the end time of the previous operation in this job
            job_prev_end = 0
            job_is_late = False
            job_end_time = 0

            for op in sorted_ops:
                # Determine the machine for this operation
                # Use first eligible machine (same as solver)
                machine_id = op.eligible_machines[0] if op.eligible_machines else None

                if machine_id is None:
                    # No machine available, skip
                    continue

                # Calculate earliest start time
                # Must be after: machine available AND previous op in job + gap
                earliest_start = max(
                    machine_available.get(machine_id, 0),
                    job_prev_end + (min_gap if job_prev_end > 0 else 0)
                )

                # Schedule the operation
                start_mins = earliest_start
                end_mins = start_mins + op.duration_mins

                # Update machine availability
                machine_available[machine_id] = end_mins

                # Update job tracking
                job_prev_end = end_mins
                job_end_time = end_mins

                # Convert to datetime
                start_dt = self.schedule_start + timedelta(minutes=start_mins)
                end_dt = self.schedule_start + timedelta(minutes=end_mins)

                # Check if this is the last operation and if job is late
                is_last_op = op.sequence == max(o.sequence for o in job.operations)
                is_late = is_last_op and job.due_date and end_dt > job.due_date
                tardiness_mins = 0

                if is_late:
                    tardiness_mins = int((end_dt - job.due_date).total_seconds() / 60)
                    job_is_late = True

                scheduled_op = ScheduledOperation(
                    operation_id=op.id,
                    job_id=job.id,
                    job_card_name=op.id,
                    work_order_name=job.id,
                    item_code=job.item_code,
                    operation_name=op.name,
                    machine_id=machine_id,
                    start_time=start_dt,
                    end_time=end_dt,
                    duration_mins=op.duration_mins,
                    sequence=op.sequence,
                    is_late=is_late,
                    tardiness_mins=tardiness_mins
                )
                scheduled_operations.append(scheduled_op)

            # Update job-level metrics
            if job_end_time > makespan:
                makespan = job_end_time

            if job_is_late:
                late_jobs += 1
                # Calculate total tardiness for this job
                if job.due_date:
                    job_end_dt = self.schedule_start + timedelta(minutes=job_end_time)
                    if job_end_dt > job.due_date:
                        total_tardiness += int((job_end_dt - job.due_date).total_seconds() / 60)
            else:
                jobs_on_time += 1

        return BaselineResult(
            makespan_minutes=makespan,
            total_tardiness_minutes=total_tardiness,
            late_jobs=late_jobs,
            jobs_on_time=jobs_on_time,
            operations=scheduled_operations,
            algorithm=algorithm
        )


@dataclass
class OptimizationComparison:
    """Comparison between optimized and baseline schedules."""
    # Baseline metrics
    baseline_makespan_minutes: int = 0
    baseline_late_jobs: int = 0
    baseline_total_tardiness: int = 0
    baseline_algorithm: str = "FIFO"

    # Optimized metrics
    optimized_makespan_minutes: int = 0
    optimized_late_jobs: int = 0
    optimized_total_tardiness: int = 0

    # Improvement percentages (positive = better)
    improvement_makespan_percent: float = 0.0
    improvement_late_jobs_percent: float = 0.0
    improvement_tardiness_percent: float = 0.0

    # Summary
    summary: str = ""

    def calculate_improvements(self) -> None:
        """Calculate improvement percentages."""
        # Makespan improvement
        if self.baseline_makespan_minutes > 0:
            self.improvement_makespan_percent = (
                (self.baseline_makespan_minutes - self.optimized_makespan_minutes)
                / self.baseline_makespan_minutes * 100
            )

        # Late jobs reduction
        if self.baseline_late_jobs > 0:
            self.improvement_late_jobs_percent = (
                (self.baseline_late_jobs - self.optimized_late_jobs)
                / self.baseline_late_jobs * 100
            )
        elif self.optimized_late_jobs == 0:
            self.improvement_late_jobs_percent = 100.0  # No late jobs is perfect

        # Tardiness reduction
        if self.baseline_total_tardiness > 0:
            self.improvement_tardiness_percent = (
                (self.baseline_total_tardiness - self.optimized_total_tardiness)
                / self.baseline_total_tardiness * 100
            )
        elif self.optimized_total_tardiness == 0:
            self.improvement_tardiness_percent = 100.0  # No tardiness is perfect

    def generate_summary(self, language: str = "vi") -> str:
        """
        Generate human-readable summary.

        Args:
            language: "vi" for Vietnamese, "en" for English

        Returns:
            Summary string
        """
        if language == "vi":
            lines = [
                f"So sánh với lập lịch {self.baseline_algorithm} (thông thường):",
                "",
                f"• Makespan: {self.baseline_makespan_minutes} phút → {self.optimized_makespan_minutes} phút "
                f"({'+' if self.improvement_makespan_percent < 0 else '-'}{abs(self.improvement_makespan_percent):.1f}%)",
                "",
                f"• Số job trễ: {self.baseline_late_jobs} → {self.optimized_late_jobs} "
                f"(giảm {self.improvement_late_jobs_percent:.1f}%)" if self.improvement_late_jobs_percent > 0
                else f"• Số job trễ: {self.baseline_late_jobs} → {self.optimized_late_jobs}",
                "",
                f"• Tổng độ trễ: {self.baseline_total_tardiness} phút → {self.optimized_total_tardiness} phút "
                f"(giảm {self.improvement_tardiness_percent:.1f}%)" if self.improvement_tardiness_percent > 0
                else f"• Tổng độ trễ: {self.baseline_total_tardiness} phút → {self.optimized_total_tardiness} phút",
            ]

            # Overall assessment
            if self.improvement_makespan_percent > 0 or self.improvement_late_jobs_percent > 0:
                lines.append("")
                lines.append("✓ Lập lịch tối ưu hiệu quả hơn so với lập lịch thông thường.")
            else:
                lines.append("")
                lines.append("○ Lập lịch tối ưu tương đương hoặc chưa cải thiện nhiều.")
        else:
            lines = [
                f"Comparison with {self.baseline_algorithm} scheduling (baseline):",
                "",
                f"• Makespan: {self.baseline_makespan_minutes} mins → {self.optimized_makespan_minutes} mins "
                f"({'+' if self.improvement_makespan_percent < 0 else '-'}{abs(self.improvement_makespan_percent):.1f}%)",
                "",
                f"• Late jobs: {self.baseline_late_jobs} → {self.optimized_late_jobs} "
                f"(reduced by {self.improvement_late_jobs_percent:.1f}%)" if self.improvement_late_jobs_percent > 0
                else f"• Late jobs: {self.baseline_late_jobs} → {self.optimized_late_jobs}",
                "",
                f"• Total tardiness: {self.baseline_total_tardiness} mins → {self.optimized_total_tardiness} mins "
                f"(reduced by {self.improvement_tardiness_percent:.1f}%)" if self.improvement_tardiness_percent > 0
                else f"• Total tardiness: {self.baseline_total_tardiness} mins → {self.optimized_total_tardiness} mins",
            ]

            if self.improvement_makespan_percent > 0 or self.improvement_late_jobs_percent > 0:
                lines.append("")
                lines.append("✓ Optimized schedule performs better than baseline.")
            else:
                lines.append("")
                lines.append("○ Optimized schedule is similar or no significant improvement.")

        self.summary = "\n".join(lines)
        return self.summary


def compute_baseline_comparison(
    problem: SchedulingProblem,
    optimized_solution: SchedulingSolution,
    baseline_algorithm: str = "FIFO"
) -> OptimizationComparison:
    """
    Compute comparison between optimized solution and baseline.

    Args:
        problem: SchedulingProblem
        optimized_solution: Solution from OR-Tools solver
        baseline_algorithm: "FIFO" or "EDD"

    Returns:
        OptimizationComparison with all metrics
    """
    baseline_scheduler = BaselineScheduler(problem)

    if baseline_algorithm == "EDD":
        baseline = baseline_scheduler.compute_edd_baseline()
    else:
        baseline = baseline_scheduler.compute_fifo_baseline()

    comparison = OptimizationComparison(
        baseline_makespan_minutes=baseline.makespan_minutes,
        baseline_late_jobs=baseline.late_jobs,
        baseline_total_tardiness=baseline.total_tardiness_minutes,
        baseline_algorithm=baseline_algorithm,
        optimized_makespan_minutes=optimized_solution.makespan_mins,
        optimized_late_jobs=optimized_solution.jobs_late,
        optimized_total_tardiness=optimized_solution.total_tardiness_mins,
    )

    comparison.calculate_improvements()
    comparison.generate_summary()

    return comparison
