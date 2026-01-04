# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Data Models for OR-Tools Scheduling

Defines the core data structures used by the CP-SAT solver:
- Operation: Single manufacturing operation
- Job: Collection of operations (Work Order)
- Machine: Workstation with capacity and working hours
- SchedulingProblem: Complete problem definition
- SchedulingSolution: Solver output
"""

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum


class SolverStatus(Enum):
    """Status of the CP-SAT solver."""
    NOT_STARTED = "Not Started"
    RUNNING = "Running"
    OPTIMAL = "Optimal"
    FEASIBLE = "Feasible"
    INFEASIBLE = "Infeasible"
    TIMEOUT = "Timeout"
    ERROR = "Error"


class SchedulingStrategy(Enum):
    """Scheduling strategy types."""
    FORWARD = "Forward Scheduling"
    BACKWARD = "Backward Scheduling"
    EDD = "Earliest Due Date"
    PRIORITY = "Priority Based"


@dataclass
class WorkingHourSlot:
    """A single working hour slot for a machine."""
    start_time: time
    end_time: time

    @property
    def duration_minutes(self) -> int:
        """Calculate duration in minutes."""
        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = datetime.combine(datetime.today(), self.end_time)
        if end_dt < start_dt:
            # Overnight shift
            end_dt += timedelta(days=1)
        return int((end_dt - start_dt).total_seconds() / 60)


@dataclass
class Operation:
    """
    A single manufacturing operation within a job.

    Attributes:
        id: Unique identifier (Job Card name)
        job_id: Parent job ID (Work Order name)
        name: Operation name
        machine_type: Type of machine required (Workstation Type)
        eligible_machines: List of machine IDs that can perform this operation
        duration_mins: Expected duration in minutes
        sequence: Sequence number within the job (1, 2, 3...)
        setup_time_mins: Setup time before operation starts
    """
    id: str
    job_id: str
    name: str
    machine_type: Optional[str]
    eligible_machines: List[str]
    duration_mins: int
    sequence: int
    setup_time_mins: int = 0

    # Scheduling variables (set by solver)
    assigned_machine: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class Job:
    """
    A manufacturing job (Work Order) consisting of multiple operations.

    Attributes:
        id: Unique identifier (Work Order name)
        item_code: Item being manufactured
        qty: Quantity to manufacture
        operations: List of operations in sequence order
        release_date: Earliest start date
        due_date: Required completion date
        priority: Job priority (higher = more important)
    """
    id: str
    item_code: str
    qty: float
    operations: List[Operation]
    release_date: datetime
    due_date: datetime
    priority: int = 1

    # Calculated fields
    @property
    def total_duration_mins(self) -> int:
        """Total processing time for all operations."""
        return sum(op.duration_mins for op in self.operations)

    @property
    def total_setup_time_mins(self) -> int:
        """Total setup time for all operations."""
        return sum(op.setup_time_mins for op in self.operations)


@dataclass
class Machine:
    """
    A machine/workstation that can perform operations.

    Attributes:
        id: Unique identifier (Workstation name)
        name: Display name
        machine_type: Type of workstation
        capacity: Number of parallel jobs (usually 1)
        working_hours: List of working hour slots per day
        holiday_list: Name of holiday list to skip
    """
    id: str
    name: str
    machine_type: Optional[str]
    capacity: int = 1
    working_hours: List[WorkingHourSlot] = field(default_factory=list)
    holiday_list: Optional[str] = None

    # Status
    is_available: bool = True

    @property
    def total_working_mins_per_day(self) -> int:
        """Total working minutes per day."""
        return sum(slot.duration_minutes for slot in self.working_hours)

    def get_working_slots_for_date(self, date: datetime) -> List[Tuple[datetime, datetime]]:
        """
        Get working time slots for a specific date.

        Returns:
            List of (start_datetime, end_datetime) tuples
        """
        slots = []
        for slot in self.working_hours:
            start_dt = datetime.combine(date.date(), slot.start_time)
            end_dt = datetime.combine(date.date(), slot.end_time)
            if end_dt < start_dt:
                end_dt += timedelta(days=1)
            slots.append((start_dt, end_dt))
        return slots


@dataclass
class ScheduledOperation:
    """
    A scheduled operation with assigned machine and time.

    Attributes:
        operation_id: Reference to Operation
        job_id: Reference to Job
        machine_id: Assigned machine
        start_time: Scheduled start datetime
        end_time: Scheduled end datetime
        is_late: Whether this causes the job to be late
        tardiness_mins: Minutes late (0 if on time)
    """
    operation_id: str
    job_id: str
    job_card_name: str
    work_order_name: str
    item_code: str
    operation_name: str
    machine_id: str
    start_time: datetime
    end_time: datetime
    duration_mins: int
    sequence: int
    is_late: bool = False
    tardiness_mins: int = 0


@dataclass
class SchedulingSolution:
    """
    Complete solution from the solver.

    Attributes:
        status: Solver status
        operations: List of scheduled operations
        makespan_mins: Total makespan in minutes
        total_tardiness_mins: Sum of all tardiness
        total_idle_mins: Total machine idle time
        solve_time_secs: Time taken to solve
        gap_percentage: Optimality gap (for feasible solutions)
    """
    status: SolverStatus
    operations: List[ScheduledOperation] = field(default_factory=list)
    makespan_mins: int = 0
    total_tardiness_mins: int = 0
    total_idle_mins: int = 0
    solve_time_secs: float = 0.0
    gap_percentage: float = 0.0

    # Job-level metrics
    jobs_on_time: int = 0
    jobs_late: int = 0

    # Machine utilization
    machine_utilization: Dict[str, float] = field(default_factory=dict)

    @property
    def is_optimal(self) -> bool:
        return self.status == SolverStatus.OPTIMAL

    @property
    def is_feasible(self) -> bool:
        return self.status in [SolverStatus.OPTIMAL, SolverStatus.FEASIBLE]

    @property
    def average_utilization(self) -> float:
        if not self.machine_utilization:
            return 0.0
        return sum(self.machine_utilization.values()) / len(self.machine_utilization)


@dataclass
class ObjectiveWeights:
    """
    Weights for multi-objective optimization.

    Total Objective =
        makespan_weight * Makespan +
        tardiness_weight * Total_Tardiness +
        idle_time_weight * Total_Idle_Time +
        setup_time_weight * Total_Setup_Time
    """
    makespan_weight: float = 1.0
    tardiness_weight: float = 10.0  # High penalty for late jobs
    idle_time_weight: float = 0.5
    setup_time_weight: float = 0.3


@dataclass
class SchedulingConfig:
    """
    Configuration for the scheduler.

    Attributes:
        time_limit_seconds: Maximum solver time
        strategy: Scheduling strategy
        objective_weights: Weights for objectives
        horizon_days: Planning horizon in days
        allow_overtime: Whether to allow work outside hours
        min_gap_between_ops_mins: Minimum gap between operations
    """
    time_limit_seconds: int = 300
    strategy: SchedulingStrategy = SchedulingStrategy.FORWARD
    objective_weights: ObjectiveWeights = field(default_factory=ObjectiveWeights)
    horizon_days: int = 30
    allow_overtime: bool = False
    min_gap_between_ops_mins: int = 10

    # Reference datetime for scheduling
    schedule_start: Optional[datetime] = None

    def __post_init__(self):
        if self.schedule_start is None:
            self.schedule_start = datetime.now()


@dataclass
class SchedulingProblem:
    """
    Complete scheduling problem definition.

    Attributes:
        jobs: List of jobs to schedule
        machines: Available machines
        config: Scheduling configuration
        production_plan: Source APS Production Plan name
    """
    jobs: List[Job]
    machines: List[Machine]
    config: SchedulingConfig = field(default_factory=SchedulingConfig)
    production_plan: Optional[str] = None

    @property
    def total_operations(self) -> int:
        return sum(len(job.operations) for job in self.jobs)

    @property
    def total_jobs(self) -> int:
        return len(self.jobs)

    @property
    def total_machines(self) -> int:
        return len(self.machines)

    def get_machine_by_id(self, machine_id: str) -> Optional[Machine]:
        for machine in self.machines:
            if machine.id == machine_id:
                return machine
        return None

    def get_machines_by_type(self, machine_type: str) -> List[Machine]:
        return [m for m in self.machines if m.machine_type == machine_type]

    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        for job in self.jobs:
            if job.id == job_id:
                return job
        return None
