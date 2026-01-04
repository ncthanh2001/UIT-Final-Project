# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
OR-Tools Scheduling Module

Implements CP-SAT (Constraint Programming - SAT) solver for
optimal production scheduling with:
- Precedence constraints (operation sequence)
- No-overlap constraints (one job per machine at a time)
- Capacity constraints (machine production capacity)
- Working hours constraints (shift schedules)
- Due date handling with tardiness penalties
"""

from uit_aps.scheduling.ortools.scheduler import ORToolsScheduler
from uit_aps.scheduling.ortools.models import (
    Job,
    Operation,
    Machine,
    SchedulingProblem,
    SchedulingSolution,
    ScheduledOperation,
)

__all__ = [
    "ORToolsScheduler",
    "Job",
    "Operation",
    "Machine",
    "SchedulingProblem",
    "SchedulingSolution",
    "ScheduledOperation",
]
