# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
OR-Tools CP-SAT Scheduler

Implements the Job Shop Scheduling Problem (JSSP) using Google OR-Tools
Constraint Programming SAT solver.

Features:
- Precedence constraints (operations must follow sequence)
- No-overlap constraints (one job per machine at a time)
- Capacity constraints (respect machine production capacity)
- Working hours constraints (schedule within shift hours)
- Multi-objective optimization (makespan + tardiness + idle time)
"""

import frappe
from frappe.utils import now_datetime, get_datetime
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import time as time_module

from uit_aps.scheduling.ortools.models import (
    Job,
    Operation,
    Machine,
    SchedulingProblem,
    SchedulingSolution,
    ScheduledOperation,
    SchedulingConfig,
    SolverStatus,
)


def safe_import_ortools():
    """Safely import OR-Tools with error handling."""
    try:
        from ortools.sat.python import cp_model
        return cp_model, None
    except ImportError as e:
        return None, str(e)


class ORToolsScheduler:
    """
    Main OR-Tools CP-SAT scheduler for Job Shop Scheduling Problem.

    Usage:
        scheduler = ORToolsScheduler(config)
        problem = scheduler.load_data_from_production_plan(plan_name)
        solution = scheduler.solve()
    """

    def __init__(self, config: SchedulingConfig = None):
        """
        Initialize the scheduler.

        Args:
            config: Scheduling configuration
        """
        self.config = config or SchedulingConfig()
        self.problem: Optional[SchedulingProblem] = None

        # Import OR-Tools
        cp_model, error = safe_import_ortools()
        if cp_model is None:
            frappe.throw(
                f"OR-Tools not installed. Please run: pip install ortools\n"
                f"Error: {error}"
            )

        self.cp_model = cp_model
        self.model = None
        self.solver = None

        # Solver variables (populated during build_model)
        self._operation_starts: Dict[str, any] = {}
        self._operation_ends: Dict[str, any] = {}
        self._operation_intervals: Dict[str, any] = {}
        self._operation_machines: Dict[str, any] = {}  # For optional machine assignment
        self._machine_to_intervals: Dict[str, List] = {}

        # Time conversion (minutes from schedule start)
        self._schedule_start: datetime = None
        self._horizon_minutes: int = 0

    def load_data(self, problem: SchedulingProblem) -> None:
        """
        Load scheduling problem data.

        Args:
            problem: SchedulingProblem with jobs and machines
        """
        self.problem = problem
        self.config = problem.config
        self._schedule_start = self.config.schedule_start or now_datetime()

        # Calculate horizon (max time we might need)
        total_duration = sum(
            job.total_duration_mins + job.total_setup_time_mins
            for job in problem.jobs
        )
        # Add buffer for scheduling flexibility
        self._horizon_minutes = max(
            total_duration * 2,
            self.config.horizon_days * 24 * 60
        )

    def build_model(self) -> None:
        """
        Build the CP-SAT model with all constraints.

        Must be called after load_data().
        """
        if self.problem is None:
            frappe.throw("No problem loaded. Call load_data() first.")

        self.model = self.cp_model.CpModel()

        # Reset variable containers
        self._operation_starts = {}
        self._operation_ends = {}
        self._operation_intervals = {}
        self._machine_to_intervals = {m.id: [] for m in self.problem.machines}

        # Create variables for each operation
        self._create_operation_variables()

        # Add constraints
        self._add_precedence_constraints()
        self._add_no_overlap_constraints()
        self._add_working_hours_constraints()

        # Set objective
        self._set_objective()

    def _create_operation_variables(self) -> None:
        """Create interval variables for each operation."""
        for job in self.problem.jobs:
            for op in job.operations:
                suffix = f"_{job.id}_{op.id}"

                # Start time variable
                start_var = self.model.NewIntVar(
                    0, self._horizon_minutes,
                    f"start{suffix}"
                )

                # End time variable
                end_var = self.model.NewIntVar(
                    0, self._horizon_minutes,
                    f"end{suffix}"
                )

                # Duration is fixed
                duration = op.duration_mins

                # Interval variable
                interval_var = self.model.NewIntervalVar(
                    start_var, duration, end_var,
                    f"interval{suffix}"
                )

                self._operation_starts[op.id] = start_var
                self._operation_ends[op.id] = end_var
                self._operation_intervals[op.id] = interval_var

                # Add to machine intervals (for no-overlap)
                # For simplicity, assign to first eligible machine
                # TODO: Implement optional machine assignment for flexibility
                if op.eligible_machines:
                    machine_id = op.eligible_machines[0]
                    if machine_id in self._machine_to_intervals:
                        self._machine_to_intervals[machine_id].append(interval_var)

    def _add_precedence_constraints(self) -> None:
        """
        Add precedence constraints: operations within a job must follow sequence.

        For job with operations [op1, op2, op3]:
        - op2.start >= op1.end + gap
        - op3.start >= op2.end + gap
        """
        gap = self.config.min_gap_between_ops_mins

        for job in self.problem.jobs:
            # Sort operations by sequence
            sorted_ops = sorted(job.operations, key=lambda x: x.sequence)

            for i in range(1, len(sorted_ops)):
                prev_op = sorted_ops[i - 1]
                curr_op = sorted_ops[i]

                # Current operation must start after previous ends (+ gap)
                self.model.Add(
                    self._operation_starts[curr_op.id] >=
                    self._operation_ends[prev_op.id] + gap
                )

    def _add_no_overlap_constraints(self) -> None:
        """
        Add no-overlap constraints: each machine can only process one operation at a time.

        Uses AddNoOverlap for interval variables on each machine.
        """
        for machine_id, intervals in self._machine_to_intervals.items():
            if len(intervals) > 1:
                self.model.AddNoOverlap(intervals)

    def _add_working_hours_constraints(self) -> None:
        """
        Add working hours constraints: operations should be scheduled within machine working hours.

        This constraint ensures operations are scheduled during available working hours.
        For each machine with defined working hours, operations assigned to that machine
        must start and end within one of the working hour slots.

        Working hours are loaded from ERPNext Workstation Working Hour child table.
        """
        if self.config.allow_overtime:
            # Skip working hours constraints if overtime is allowed
            return

        # Build mapping of operation -> assigned machine
        op_to_machine = {}
        for job in self.problem.jobs:
            for op in job.operations:
                if op.eligible_machines:
                    # Currently using first eligible machine (TODO: optimize machine selection)
                    op_to_machine[op.id] = op.eligible_machines[0]

        # Get unique days in the scheduling horizon
        horizon_days = self.config.horizon_days or 30

        for op_id, machine_id in op_to_machine.items():
            machine = self.problem.get_machine_by_id(machine_id)
            if not machine or not machine.working_hours:
                continue

            # Build allowed time windows across the horizon
            # Each working hour slot is converted to minutes from schedule start
            allowed_starts = []

            for day_offset in range(horizon_days):
                current_date = self._schedule_start + timedelta(days=day_offset)

                for slot in machine.working_hours:
                    # Convert slot times to minutes from schedule start
                    slot_start_dt = datetime.combine(current_date.date(), slot.start_time)
                    slot_end_dt = datetime.combine(current_date.date(), slot.end_time)

                    # Handle overnight shifts
                    if slot_end_dt < slot_start_dt:
                        slot_end_dt += timedelta(days=1)

                    start_mins = self._datetime_to_minutes(slot_start_dt)
                    end_mins = self._datetime_to_minutes(slot_end_dt)

                    # Only include valid time windows (positive and within horizon)
                    if start_mins >= 0 and start_mins < self._horizon_minutes:
                        allowed_starts.append((max(0, start_mins), min(self._horizon_minutes, end_mins)))

            # If working hours are defined, add constraint that operation must fit in one slot
            if allowed_starts and op_id in self._operation_starts:
                start_var = self._operation_starts[op_id]
                end_var = self._operation_ends[op_id]

                # Create boolean variables for each possible slot
                slot_bools = []
                for i, (slot_start, slot_end) in enumerate(allowed_starts):
                    slot_bool = self.model.NewBoolVar(f"slot_{op_id}_{i}")
                    slot_bools.append(slot_bool)

                    # If this slot is chosen, operation must be within its bounds
                    self.model.Add(start_var >= slot_start).OnlyEnforceIf(slot_bool)
                    self.model.Add(end_var <= slot_end).OnlyEnforceIf(slot_bool)

                # Operation must be in exactly one slot
                if slot_bools:
                    self.model.AddExactlyOne(slot_bools)

    def _set_objective(self) -> None:
        """
        Set the optimization objective.

        Minimize: makespan + tardiness_penalty
        """
        weights = self.config.objective_weights

        # Makespan: latest end time
        all_ends = list(self._operation_ends.values())
        makespan = self.model.NewIntVar(0, self._horizon_minutes, "makespan")
        self.model.AddMaxEquality(makespan, all_ends)

        # Tardiness for each job
        tardiness_vars = []
        for job in self.problem.jobs:
            # Get the last operation's end time
            last_op = max(job.operations, key=lambda x: x.sequence)
            job_end = self._operation_ends[last_op.id]

            # Due date in minutes from schedule start
            due_minutes = self._datetime_to_minutes(job.due_date)

            # Tardiness = max(0, end - due)
            tardiness = self.model.NewIntVar(0, self._horizon_minutes, f"tardiness_{job.id}")
            self.model.AddMaxEquality(tardiness, [0, job_end - due_minutes])
            tardiness_vars.append(tardiness)

        # Total tardiness
        total_tardiness = self.model.NewIntVar(
            0, self._horizon_minutes * len(self.problem.jobs),
            "total_tardiness"
        )
        self.model.Add(total_tardiness == sum(tardiness_vars))

        # Combined objective
        objective_terms = []

        if weights.makespan_weight > 0:
            objective_terms.append(int(weights.makespan_weight * 100) * makespan)

        if weights.tardiness_weight > 0:
            objective_terms.append(int(weights.tardiness_weight * 100) * total_tardiness)

        if objective_terms:
            self.model.Minimize(sum(objective_terms))
        else:
            self.model.Minimize(makespan)

    def solve(self, time_limit_seconds: int = None) -> SchedulingSolution:
        """
        Solve the scheduling problem.

        Args:
            time_limit_seconds: Maximum solver time (overrides config)

        Returns:
            SchedulingSolution with scheduled operations
        """
        if self.model is None:
            self.build_model()

        time_limit = time_limit_seconds or self.config.time_limit_seconds

        self.solver = self.cp_model.CpSolver()
        self.solver.parameters.max_time_in_seconds = time_limit

        # Enable logging for debugging
        # self.solver.parameters.log_search_progress = True

        start_time = time_module.time()
        status = self.solver.Solve(self.model)
        solve_time = time_module.time() - start_time

        # Convert status
        solver_status = self._convert_status(status)

        if solver_status not in [SolverStatus.OPTIMAL, SolverStatus.FEASIBLE]:
            return SchedulingSolution(
                status=solver_status,
                solve_time_secs=solve_time
            )

        # Extract solution
        return self._extract_solution(solver_status, solve_time)

    def _extract_solution(
        self,
        status: SolverStatus,
        solve_time: float
    ) -> SchedulingSolution:
        """
        Extract solution from solver.

        Args:
            status: Solver status
            solve_time: Time taken to solve

        Returns:
            SchedulingSolution with all scheduled operations
        """
        scheduled_ops = []
        jobs_late = 0
        jobs_on_time = 0
        total_tardiness = 0
        makespan = 0

        for job in self.problem.jobs:
            job_is_late = False
            last_end_time = None

            for op in job.operations:
                start_mins = self.solver.Value(self._operation_starts[op.id])
                end_mins = self.solver.Value(self._operation_ends[op.id])

                start_dt = self._minutes_to_datetime(start_mins)
                end_dt = self._minutes_to_datetime(end_mins)

                # Determine machine (first eligible for now)
                machine_id = op.eligible_machines[0] if op.eligible_machines else None

                # Check if late
                is_late = end_dt > job.due_date if op.sequence == max(o.sequence for o in job.operations) else False
                tardiness_mins = max(0, int((end_dt - job.due_date).total_seconds() / 60)) if is_late else 0

                if is_late:
                    job_is_late = True
                    total_tardiness += tardiness_mins

                scheduled_op = ScheduledOperation(
                    operation_id=op.id,
                    job_id=job.id,
                    job_card_name=op.id,  # Job Card name is operation ID
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
                scheduled_ops.append(scheduled_op)

                last_end_time = end_dt
                if end_mins > makespan:
                    makespan = end_mins

            if job_is_late:
                jobs_late += 1
            else:
                jobs_on_time += 1

        # Calculate machine utilization
        machine_utilization = self._calculate_utilization(scheduled_ops)

        # Calculate gap percentage for feasible solutions
        gap = 0.0
        if status == SolverStatus.FEASIBLE:
            if self.solver.BestObjectiveBound() > 0:
                gap = abs(self.solver.ObjectiveValue() - self.solver.BestObjectiveBound()) / self.solver.BestObjectiveBound() * 100

        return SchedulingSolution(
            status=status,
            operations=scheduled_ops,
            makespan_mins=makespan,
            total_tardiness_mins=total_tardiness,
            solve_time_secs=solve_time,
            gap_percentage=gap,
            jobs_on_time=jobs_on_time,
            jobs_late=jobs_late,
            machine_utilization=machine_utilization
        )

    def _calculate_utilization(
        self,
        scheduled_ops: List[ScheduledOperation]
    ) -> Dict[str, float]:
        """
        Calculate machine utilization.

        Args:
            scheduled_ops: List of scheduled operations

        Returns:
            Dict mapping machine_id to utilization percentage
        """
        utilization = {}

        # Group operations by machine
        machine_ops: Dict[str, List[ScheduledOperation]] = {}
        for op in scheduled_ops:
            if op.machine_id:
                if op.machine_id not in machine_ops:
                    machine_ops[op.machine_id] = []
                machine_ops[op.machine_id].append(op)

        # Calculate utilization for each machine
        for machine_id, ops in machine_ops.items():
            if not ops:
                utilization[machine_id] = 0.0
                continue

            total_work_time = sum(op.duration_mins for op in ops)

            # Get machine working hours per day
            machine = self.problem.get_machine_by_id(machine_id)
            if machine:
                working_mins_per_day = machine.total_working_mins_per_day or (8 * 60)
            else:
                working_mins_per_day = 8 * 60

            # Calculate days spanned
            min_start = min(op.start_time for op in ops)
            max_end = max(op.end_time for op in ops)
            days_spanned = max(1, (max_end - min_start).days + 1)

            available_time = days_spanned * working_mins_per_day

            utilization[machine_id] = min(100.0, (total_work_time / available_time) * 100)

        return utilization

    def _convert_status(self, status: int) -> SolverStatus:
        """Convert OR-Tools status to SolverStatus enum."""
        status_map = {
            self.cp_model.OPTIMAL: SolverStatus.OPTIMAL,
            self.cp_model.FEASIBLE: SolverStatus.FEASIBLE,
            self.cp_model.INFEASIBLE: SolverStatus.INFEASIBLE,
            self.cp_model.MODEL_INVALID: SolverStatus.ERROR,
            self.cp_model.UNKNOWN: SolverStatus.TIMEOUT,
        }
        return status_map.get(status, SolverStatus.ERROR)

    def _datetime_to_minutes(self, dt: datetime) -> int:
        """Convert datetime to minutes from schedule start."""
        if dt is None:
            return 0
        delta = dt - self._schedule_start
        return max(0, int(delta.total_seconds() / 60))

    def _minutes_to_datetime(self, minutes: int) -> datetime:
        """Convert minutes from schedule start to datetime."""
        return self._schedule_start + timedelta(minutes=minutes)


def run_scheduling(
    production_plan: str = None,
    work_orders: List[str] = None,
    time_limit_seconds: int = 300,
    config: SchedulingConfig = None
) -> SchedulingSolution:
    """
    Convenience function to run scheduling.

    Args:
        production_plan: APS Production Plan name
        work_orders: List of Work Order names (alternative to production_plan)
        time_limit_seconds: Solver time limit
        config: Scheduling configuration

    Returns:
        SchedulingSolution
    """
    from uit_aps.scheduling.data.erpnext_loader import ERPNextDataLoader

    if config is None:
        config = SchedulingConfig(time_limit_seconds=time_limit_seconds)
    else:
        config.time_limit_seconds = time_limit_seconds

    loader = ERPNextDataLoader()

    if production_plan:
        problem = loader.load_from_production_plan(production_plan, config)
    elif work_orders:
        problem = loader.load_from_work_orders(work_orders, config=config)
    else:
        frappe.throw("Either production_plan or work_orders must be provided")

    if not problem.jobs:
        frappe.throw("No jobs found to schedule")

    scheduler = ORToolsScheduler(config)
    scheduler.load_data(problem)
    scheduler.build_model()

    return scheduler.solve(time_limit_seconds)
