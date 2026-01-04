# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Scheduling Environment for Reinforcement Learning

Implements a Gymnasium-compatible environment for production scheduling.
The agent learns to make real-time scheduling decisions in response to:
- Machine breakdowns
- Rush orders
- Processing delays
- Resource constraints
"""

import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from enum import IntEnum


class ActionType(IntEnum):
    """Types of scheduling actions the agent can take."""
    NO_OP = 0                    # Do nothing
    REASSIGN_MACHINE = 1         # Move operation to different machine
    RESCHEDULE_EARLIER = 2       # Move operation earlier in schedule
    RESCHEDULE_LATER = 3         # Move operation later in schedule
    PRIORITIZE_JOB = 4           # Increase job priority
    SPLIT_BATCH = 5              # Split large batch into smaller ones
    MERGE_OPERATIONS = 6         # Combine sequential operations


class DisruptionType(IntEnum):
    """Types of disruptions that can occur."""
    NONE = 0
    MACHINE_BREAKDOWN = 1
    RUSH_ORDER = 2
    PROCESSING_DELAY = 3
    MATERIAL_SHORTAGE = 4
    WORKER_ABSENCE = 5
    QUALITY_ISSUE = 6


@dataclass
class SchedulingState:
    """
    Current state of the scheduling environment.

    Attributes:
        current_time: Current simulation time
        operations: List of operation states
        machines: List of machine states
        pending_jobs: Jobs waiting to be scheduled
        active_disruptions: Current active disruptions
    """
    current_time: datetime
    operations: List[Dict]
    machines: List[Dict]
    pending_jobs: List[Dict]
    active_disruptions: List[Dict]

    # Metrics
    total_tardiness: float = 0.0
    completed_jobs: int = 0
    late_jobs: int = 0
    machine_utilization: Dict[str, float] = field(default_factory=dict)


@dataclass
class EnvironmentConfig:
    """Configuration for the scheduling environment."""
    # Time settings
    time_step_minutes: int = 15
    horizon_hours: int = 24

    # State space
    max_operations: int = 100
    max_machines: int = 20
    max_jobs: int = 50

    # Action space
    num_action_types: int = 7

    # Disruption settings
    disruption_probability: float = 0.05
    mean_breakdown_duration_mins: int = 60

    # Reward weights
    tardiness_penalty: float = -10.0
    completion_reward: float = 5.0
    utilization_reward: float = 1.0
    makespan_penalty: float = -0.1

    # Normalization
    max_duration_mins: int = 480
    max_tardiness_mins: int = 1440


class SchedulingEnv:
    """
    Gymnasium-compatible environment for production scheduling.

    The environment simulates a dynamic job shop where:
    - Operations need to be assigned to machines
    - Disruptions can occur (breakdowns, rush orders, delays)
    - The agent makes real-time adjustments

    Observation Space:
        - Operation features: [start_time, duration, due_date, priority, status, machine_id]
        - Machine features: [status, current_op, remaining_time, utilization]
        - Global features: [current_time, pending_jobs, active_disruptions]

    Action Space:
        Discrete actions: (action_type, target_operation, target_machine)
    """

    def __init__(self, config: EnvironmentConfig = None):
        """
        Initialize the scheduling environment.

        Args:
            config: Environment configuration
        """
        self.config = config or EnvironmentConfig()

        # State components
        self.state: Optional[SchedulingState] = None
        self.initial_schedule: List[Dict] = []
        self.current_step: int = 0
        self.done: bool = False

        # Random generator for disruptions
        self.rng = np.random.default_rng()

        # History for analysis
        self.action_history: List[Dict] = []
        self.reward_history: List[float] = []
        self.disruption_history: List[Dict] = []

        # Define spaces
        self._define_spaces()

    def _define_spaces(self):
        """Define observation and action spaces."""
        # Observation space dimensions
        self.operation_features = 8  # [start, end, duration, due, priority, status, machine, is_late]
        self.machine_features = 6    # [status, utilization, current_op, remaining, capacity, type]
        self.global_features = 5     # [time, pending, disruptions, tardiness, completed]

        # Total observation size
        self.obs_dim = (
            self.config.max_operations * self.operation_features +
            self.config.max_machines * self.machine_features +
            self.global_features
        )

        # Action space: (action_type, operation_idx, machine_idx)
        self.action_dim = self.config.num_action_types
        self.num_operations = self.config.max_operations
        self.num_machines = self.config.max_machines

    def reset(
        self,
        initial_schedule: List[Dict] = None,
        machines: List[Dict] = None,
        start_time: datetime = None,
        seed: int = None
    ) -> Tuple[np.ndarray, Dict]:
        """
        Reset the environment to initial state.

        Args:
            initial_schedule: Initial schedule from Tier 1 OR-Tools
            machines: Available machines
            start_time: Simulation start time
            seed: Random seed

        Returns:
            observation: Initial observation
            info: Additional information
        """
        if seed is not None:
            self.rng = np.random.default_rng(seed)

        # Initialize time
        self.start_time = start_time or datetime.now()
        self.current_time = self.start_time
        self.current_step = 0
        self.done = False

        # Initialize schedule
        self.initial_schedule = initial_schedule or []
        self.operations = self._init_operations(initial_schedule)
        self.machines = self._init_machines(machines)

        # Initialize state
        self.state = SchedulingState(
            current_time=self.current_time,
            operations=self.operations,
            machines=self.machines,
            pending_jobs=[],
            active_disruptions=[]
        )

        # Clear history
        self.action_history = []
        self.reward_history = []
        self.disruption_history = []

        # Get observation
        obs = self._get_observation()
        info = self._get_info()

        return obs, info

    def step(self, action: Tuple[int, int, int]) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        Execute one step in the environment.

        Args:
            action: Tuple of (action_type, operation_idx, machine_idx)

        Returns:
            observation: New observation
            reward: Reward for this step
            terminated: Whether episode is done
            truncated: Whether episode was truncated
            info: Additional information
        """
        action_type, op_idx, machine_idx = action

        # Execute action
        action_success = self._execute_action(action_type, op_idx, machine_idx)

        # Generate disruptions
        disruptions = self._generate_disruptions()

        # Handle disruptions
        for disruption in disruptions:
            self._handle_disruption(disruption)

        # Advance time
        self._advance_time()

        # Update state
        self._update_state()

        # Calculate reward
        reward = self._calculate_reward(action_success, disruptions)

        # Check termination
        terminated = self._check_termination()
        truncated = self.current_step >= self.config.horizon_hours * 4  # Max steps

        # Record history
        self.action_history.append({
            "step": self.current_step,
            "action": action,
            "success": action_success,
            "reward": reward
        })
        self.reward_history.append(reward)

        # Get observation
        obs = self._get_observation()
        info = self._get_info()

        self.current_step += 1
        self.done = terminated or truncated

        return obs, reward, terminated, truncated, info

    def _init_operations(self, schedule: List[Dict]) -> List[Dict]:
        """Initialize operation states from schedule."""
        operations = []

        for idx, op in enumerate(schedule or []):
            operations.append({
                "id": op.get("operation_id", f"op_{idx}"),
                "job_id": op.get("job_id", ""),
                "job_card": op.get("job_card", ""),
                "name": op.get("operation_name", ""),
                "machine_id": op.get("machine_id", ""),
                "start_time": op.get("start_time"),
                "end_time": op.get("end_time"),
                "duration_mins": op.get("duration_mins", 60),
                "due_date": op.get("due_date"),
                "priority": op.get("priority", 1),
                "status": "pending",  # pending, in_progress, completed, delayed
                "original_start": op.get("start_time"),
                "original_machine": op.get("machine_id", ""),
                "tardiness_mins": 0,
                "is_late": False
            })

        # Pad to max_operations
        while len(operations) < self.config.max_operations:
            operations.append(self._empty_operation())

        return operations[:self.config.max_operations]

    def _empty_operation(self) -> Dict:
        """Return an empty operation placeholder."""
        return {
            "id": "",
            "job_id": "",
            "job_card": "",
            "name": "",
            "machine_id": "",
            "start_time": None,
            "end_time": None,
            "duration_mins": 0,
            "due_date": None,
            "priority": 0,
            "status": "empty",
            "original_start": None,
            "original_machine": "",
            "tardiness_mins": 0,
            "is_late": False
        }

    def _init_machines(self, machines: List[Dict]) -> List[Dict]:
        """Initialize machine states."""
        machine_list = []

        for m in (machines or []):
            machine_list.append({
                "id": m.get("id", ""),
                "name": m.get("name", ""),
                "type": m.get("machine_type", ""),
                "status": "available",  # available, busy, breakdown, maintenance
                "current_operation": None,
                "remaining_time_mins": 0,
                "utilization": 0.0,
                "capacity": m.get("capacity", 1),
                "breakdown_until": None
            })

        # Pad to max_machines
        while len(machine_list) < self.config.max_machines:
            machine_list.append(self._empty_machine())

        return machine_list[:self.config.max_machines]

    def _empty_machine(self) -> Dict:
        """Return an empty machine placeholder."""
        return {
            "id": "",
            "name": "",
            "type": "",
            "status": "empty",
            "current_operation": None,
            "remaining_time_mins": 0,
            "utilization": 0.0,
            "capacity": 0,
            "breakdown_until": None
        }

    def _get_observation(self) -> np.ndarray:
        """
        Build observation vector from current state.

        Returns:
            Flattened observation array
        """
        obs = []

        # Operation features
        for op in self.operations:
            op_features = self._encode_operation(op)
            obs.extend(op_features)

        # Machine features
        for machine in self.machines:
            machine_features = self._encode_machine(machine)
            obs.extend(machine_features)

        # Global features
        global_features = self._encode_global_state()
        obs.extend(global_features)

        return np.array(obs, dtype=np.float32)

    def _encode_operation(self, op: Dict) -> List[float]:
        """Encode operation into feature vector."""
        if op["status"] == "empty":
            return [0.0] * self.operation_features

        # Normalize times relative to current time
        start_offset = 0.0
        end_offset = 0.0
        due_offset = 0.0

        if op["start_time"]:
            start_delta = (op["start_time"] - self.current_time).total_seconds() / 60
            start_offset = start_delta / self.config.max_duration_mins

        if op["end_time"]:
            end_delta = (op["end_time"] - self.current_time).total_seconds() / 60
            end_offset = end_delta / self.config.max_duration_mins

        if op["due_date"]:
            due_delta = (op["due_date"] - self.current_time).total_seconds() / 60
            due_offset = due_delta / self.config.max_tardiness_mins

        # Status encoding
        status_map = {"pending": 0.0, "in_progress": 0.5, "completed": 1.0, "delayed": -0.5}
        status_val = status_map.get(op["status"], 0.0)

        # Machine ID encoding (normalized index)
        machine_idx = 0.0
        for i, m in enumerate(self.machines):
            if m["id"] == op["machine_id"]:
                machine_idx = (i + 1) / self.config.max_machines
                break

        return [
            np.clip(start_offset, -1.0, 1.0),
            np.clip(end_offset, -1.0, 1.0),
            op["duration_mins"] / self.config.max_duration_mins,
            np.clip(due_offset, -1.0, 1.0),
            op["priority"] / 10.0,
            status_val,
            machine_idx,
            1.0 if op["is_late"] else 0.0
        ]

    def _encode_machine(self, machine: Dict) -> List[float]:
        """Encode machine into feature vector."""
        if machine["status"] == "empty":
            return [0.0] * self.machine_features

        # Status encoding
        status_map = {"available": 1.0, "busy": 0.5, "breakdown": 0.0, "maintenance": 0.25}
        status_val = status_map.get(machine["status"], 0.0)

        # Current operation encoding
        current_op_idx = 0.0
        if machine["current_operation"]:
            for i, op in enumerate(self.operations):
                if op["id"] == machine["current_operation"]:
                    current_op_idx = (i + 1) / self.config.max_operations
                    break

        return [
            status_val,
            machine["utilization"],
            current_op_idx,
            machine["remaining_time_mins"] / self.config.max_duration_mins,
            machine["capacity"] / 5.0,  # Assume max capacity of 5
            hash(machine["type"]) % 100 / 100.0 if machine["type"] else 0.0
        ]

    def _encode_global_state(self) -> List[float]:
        """Encode global state features."""
        # Time progress
        elapsed = (self.current_time - self.start_time).total_seconds() / 3600
        time_progress = elapsed / self.config.horizon_hours

        # Pending jobs count
        pending = sum(1 for op in self.operations if op["status"] == "pending")
        pending_ratio = pending / self.config.max_operations

        # Active disruptions
        disruption_count = len(self.state.active_disruptions) if self.state else 0
        disruption_ratio = disruption_count / 5.0  # Assume max 5 concurrent disruptions

        # Total tardiness
        tardiness = sum(op["tardiness_mins"] for op in self.operations)
        tardiness_ratio = tardiness / (self.config.max_tardiness_mins * len(self.operations))

        # Completed jobs
        completed = sum(1 for op in self.operations if op["status"] == "completed")
        completion_ratio = completed / max(1, sum(1 for op in self.operations if op["status"] != "empty"))

        return [
            np.clip(time_progress, 0.0, 1.0),
            np.clip(pending_ratio, 0.0, 1.0),
            np.clip(disruption_ratio, 0.0, 1.0),
            np.clip(tardiness_ratio, 0.0, 1.0),
            np.clip(completion_ratio, 0.0, 1.0)
        ]

    def _execute_action(self, action_type: int, op_idx: int, machine_idx: int) -> bool:
        """
        Execute the selected action.

        Args:
            action_type: Type of action
            op_idx: Target operation index
            machine_idx: Target machine index

        Returns:
            Whether the action was successful
        """
        # Validate indices
        if op_idx >= len(self.operations) or machine_idx >= len(self.machines):
            return False

        op = self.operations[op_idx]
        machine = self.machines[machine_idx]

        if op["status"] == "empty":
            return False

        action = ActionType(action_type)

        if action == ActionType.NO_OP:
            return True

        elif action == ActionType.REASSIGN_MACHINE:
            return self._reassign_machine(op_idx, machine_idx)

        elif action == ActionType.RESCHEDULE_EARLIER:
            return self._reschedule_earlier(op_idx)

        elif action == ActionType.RESCHEDULE_LATER:
            return self._reschedule_later(op_idx)

        elif action == ActionType.PRIORITIZE_JOB:
            return self._prioritize_job(op_idx)

        elif action == ActionType.SPLIT_BATCH:
            return self._split_batch(op_idx)

        elif action == ActionType.MERGE_OPERATIONS:
            return self._merge_operations(op_idx)

        return False

    def _reassign_machine(self, op_idx: int, machine_idx: int) -> bool:
        """Reassign operation to a different machine."""
        op = self.operations[op_idx]
        machine = self.machines[machine_idx]

        # Check if operation can be reassigned
        if op["status"] not in ["pending", "delayed"]:
            return False

        # Check if machine is available
        if machine["status"] in ["breakdown", "empty"]:
            return False

        # Reassign
        op["machine_id"] = machine["id"]
        return True

    def _reschedule_earlier(self, op_idx: int) -> bool:
        """Move operation earlier in the schedule."""
        op = self.operations[op_idx]

        if op["status"] not in ["pending", "delayed"]:
            return False

        if op["start_time"]:
            # Move 30 minutes earlier
            new_start = op["start_time"] - timedelta(minutes=30)
            if new_start >= self.current_time:
                op["start_time"] = new_start
                op["end_time"] = new_start + timedelta(minutes=op["duration_mins"])
                return True

        return False

    def _reschedule_later(self, op_idx: int) -> bool:
        """Move operation later in the schedule."""
        op = self.operations[op_idx]

        if op["status"] not in ["pending", "delayed"]:
            return False

        if op["start_time"]:
            # Move 30 minutes later
            new_start = op["start_time"] + timedelta(minutes=30)
            op["start_time"] = new_start
            op["end_time"] = new_start + timedelta(minutes=op["duration_mins"])
            return True

        return False

    def _prioritize_job(self, op_idx: int) -> bool:
        """Increase job priority."""
        op = self.operations[op_idx]

        if op["status"] == "empty":
            return False

        op["priority"] = min(10, op["priority"] + 1)
        return True

    def _split_batch(self, op_idx: int) -> bool:
        """Split a large operation into smaller batches."""
        op = self.operations[op_idx]

        # Only split if duration is large enough
        if op["duration_mins"] < 120:
            return False

        # Split in half
        op["duration_mins"] = op["duration_mins"] // 2
        if op["end_time"] and op["start_time"]:
            op["end_time"] = op["start_time"] + timedelta(minutes=op["duration_mins"])

        return True

    def _merge_operations(self, op_idx: int) -> bool:
        """Merge with next operation if possible."""
        # Find next operation for same job
        op = self.operations[op_idx]

        for i, next_op in enumerate(self.operations):
            if (next_op["job_id"] == op["job_id"] and
                next_op["id"] != op["id"] and
                next_op["status"] == "pending"):
                # Merge durations
                op["duration_mins"] += next_op["duration_mins"]
                next_op["status"] = "empty"
                return True

        return False

    def _generate_disruptions(self) -> List[Dict]:
        """Generate random disruptions based on probability."""
        disruptions = []

        if self.rng.random() < self.config.disruption_probability:
            disruption_type = self.rng.choice(list(DisruptionType)[1:])  # Exclude NONE

            disruption = {
                "type": disruption_type,
                "time": self.current_time,
                "duration_mins": self.rng.integers(30, 120),
                "severity": self.rng.uniform(0.3, 1.0)
            }

            # Add specific details based on type
            if disruption_type == DisruptionType.MACHINE_BREAKDOWN:
                available_machines = [m for m in self.machines if m["status"] == "busy"]
                if available_machines:
                    disruption["machine_id"] = self.rng.choice(available_machines)["id"]
                    disruptions.append(disruption)

            elif disruption_type == DisruptionType.RUSH_ORDER:
                disruption["priority"] = 10
                disruption["duration_mins"] = self.rng.integers(60, 240)
                disruptions.append(disruption)

            elif disruption_type == DisruptionType.PROCESSING_DELAY:
                in_progress = [op for op in self.operations if op["status"] == "in_progress"]
                if in_progress:
                    disruption["operation_id"] = self.rng.choice(in_progress)["id"]
                    disruption["delay_mins"] = self.rng.integers(15, 60)
                    disruptions.append(disruption)

        # Record disruptions
        for d in disruptions:
            self.disruption_history.append(d)
            if self.state:
                self.state.active_disruptions.append(d)

        return disruptions

    def _handle_disruption(self, disruption: Dict):
        """Handle a disruption event."""
        dtype = disruption["type"]

        if dtype == DisruptionType.MACHINE_BREAKDOWN:
            machine_id = disruption.get("machine_id")
            for machine in self.machines:
                if machine["id"] == machine_id:
                    machine["status"] = "breakdown"
                    machine["breakdown_until"] = (
                        self.current_time +
                        timedelta(minutes=disruption["duration_mins"])
                    )

                    # Mark affected operation as delayed
                    if machine["current_operation"]:
                        for op in self.operations:
                            if op["id"] == machine["current_operation"]:
                                op["status"] = "delayed"
                    break

        elif dtype == DisruptionType.PROCESSING_DELAY:
            op_id = disruption.get("operation_id")
            delay_mins = disruption.get("delay_mins", 30)

            for op in self.operations:
                if op["id"] == op_id:
                    if op["end_time"]:
                        op["end_time"] += timedelta(minutes=delay_mins)
                        op["duration_mins"] += delay_mins
                    break

        elif dtype == DisruptionType.RUSH_ORDER:
            # Add a high-priority pending operation
            for op in self.operations:
                if op["status"] == "empty":
                    op.update({
                        "id": f"rush_{self.current_step}",
                        "job_id": f"rush_job_{self.current_step}",
                        "name": "Rush Order",
                        "duration_mins": disruption["duration_mins"],
                        "priority": 10,
                        "status": "pending",
                        "start_time": self.current_time,
                        "end_time": self.current_time + timedelta(minutes=disruption["duration_mins"]),
                        "due_date": self.current_time + timedelta(hours=4)
                    })
                    break

    def _advance_time(self):
        """Advance simulation time by one step."""
        self.current_time += timedelta(minutes=self.config.time_step_minutes)

        # Update machine states
        for machine in self.machines:
            if machine["status"] == "breakdown":
                if machine["breakdown_until"] and self.current_time >= machine["breakdown_until"]:
                    machine["status"] = "available"
                    machine["breakdown_until"] = None

            if machine["remaining_time_mins"] > 0:
                machine["remaining_time_mins"] -= self.config.time_step_minutes
                if machine["remaining_time_mins"] <= 0:
                    machine["status"] = "available"
                    machine["current_operation"] = None

        # Update operation states
        for op in self.operations:
            if op["status"] == "empty":
                continue

            # Check if operation should start
            if op["status"] == "pending" and op["start_time"]:
                if self.current_time >= op["start_time"]:
                    # Find assigned machine
                    for machine in self.machines:
                        if machine["id"] == op["machine_id"] and machine["status"] == "available":
                            op["status"] = "in_progress"
                            machine["status"] = "busy"
                            machine["current_operation"] = op["id"]
                            machine["remaining_time_mins"] = op["duration_mins"]
                            break

            # Check if operation completed
            if op["status"] == "in_progress" and op["end_time"]:
                if self.current_time >= op["end_time"]:
                    op["status"] = "completed"

                    # Check tardiness
                    if op["due_date"] and self.current_time > op["due_date"]:
                        op["is_late"] = True
                        op["tardiness_mins"] = int(
                            (self.current_time - op["due_date"]).total_seconds() / 60
                        )

    def _update_state(self):
        """Update state metrics."""
        if not self.state:
            return

        self.state.current_time = self.current_time
        self.state.operations = self.operations
        self.state.machines = self.machines

        # Update metrics
        self.state.total_tardiness = sum(
            op["tardiness_mins"] for op in self.operations
        )
        self.state.completed_jobs = sum(
            1 for op in self.operations if op["status"] == "completed"
        )
        self.state.late_jobs = sum(
            1 for op in self.operations if op["is_late"]
        )

        # Machine utilization
        for machine in self.machines:
            if machine["id"]:
                busy_time = sum(
                    op["duration_mins"] for op in self.operations
                    if op["machine_id"] == machine["id"] and op["status"] == "completed"
                )
                elapsed = (self.current_time - self.start_time).total_seconds() / 60
                machine["utilization"] = busy_time / max(1, elapsed)
                self.state.machine_utilization[machine["id"]] = machine["utilization"]

        # Clean up resolved disruptions
        self.state.active_disruptions = [
            d for d in self.state.active_disruptions
            if d["time"] + timedelta(minutes=d["duration_mins"]) > self.current_time
        ]

    def _calculate_reward(self, action_success: bool, disruptions: List[Dict]) -> float:
        """
        Calculate reward for the current step.

        Reward components:
        - Negative reward for tardiness
        - Positive reward for completing jobs on time
        - Positive reward for high machine utilization
        - Bonus for successfully handling disruptions

        Args:
            action_success: Whether the action was executed successfully
            disruptions: Disruptions that occurred this step

        Returns:
            Total reward
        """
        reward = 0.0

        # Tardiness penalty
        tardiness_delta = sum(
            op["tardiness_mins"] for op in self.operations
        )
        reward += self.config.tardiness_penalty * (tardiness_delta / 1000.0)

        # Completion reward
        completed_this_step = sum(
            1 for op in self.operations
            if op["status"] == "completed" and not op.get("rewarded", False)
        )
        for op in self.operations:
            if op["status"] == "completed" and not op.get("rewarded", False):
                if not op["is_late"]:
                    reward += self.config.completion_reward
                else:
                    reward += self.config.completion_reward * 0.5
                op["rewarded"] = True

        # Utilization reward
        avg_utilization = np.mean([
            m["utilization"] for m in self.machines if m["id"]
        ]) if any(m["id"] for m in self.machines) else 0.0
        reward += self.config.utilization_reward * avg_utilization

        # Action success bonus
        if action_success and ActionType(self.action_history[-1]["action"][0] if self.action_history else 0) != ActionType.NO_OP:
            reward += 0.5

        # Disruption handling bonus
        if disruptions and action_success:
            reward += 1.0

        return reward

    def _check_termination(self) -> bool:
        """Check if episode should terminate."""
        # All operations completed
        active_ops = [op for op in self.operations if op["status"] not in ["empty", "completed"]]
        if not active_ops:
            return True

        # Time limit reached
        elapsed = (self.current_time - self.start_time).total_seconds() / 3600
        if elapsed >= self.config.horizon_hours:
            return True

        return False

    def _get_info(self) -> Dict:
        """Get additional information about the current state."""
        return {
            "current_time": self.current_time.isoformat() if self.current_time else None,
            "step": self.current_step,
            "completed_operations": sum(1 for op in self.operations if op["status"] == "completed"),
            "pending_operations": sum(1 for op in self.operations if op["status"] == "pending"),
            "delayed_operations": sum(1 for op in self.operations if op["status"] == "delayed"),
            "late_jobs": sum(1 for op in self.operations if op["is_late"]),
            "total_tardiness_mins": sum(op["tardiness_mins"] for op in self.operations),
            "active_disruptions": len(self.state.active_disruptions) if self.state else 0,
            "average_utilization": np.mean([m["utilization"] for m in self.machines if m["id"]]) if any(m["id"] for m in self.machines) else 0.0
        }

    def render(self) -> str:
        """Render current state as string for debugging."""
        lines = [
            f"=== Scheduling Environment State ===",
            f"Time: {self.current_time}",
            f"Step: {self.current_step}",
            f"",
            "Operations:",
        ]

        for op in self.operations[:10]:  # Show first 10
            if op["status"] != "empty":
                lines.append(
                    f"  {op['id']}: {op['status']} on {op['machine_id']} "
                    f"(priority={op['priority']}, late={op['is_late']})"
                )

        lines.append("")
        lines.append("Machines:")
        for m in self.machines[:5]:  # Show first 5
            if m["id"]:
                lines.append(
                    f"  {m['id']}: {m['status']} (util={m['utilization']:.2f})"
                )

        lines.append("")
        lines.append(f"Active Disruptions: {len(self.state.active_disruptions) if self.state else 0}")
        lines.append(f"Total Reward: {sum(self.reward_history):.2f}")

        return "\n".join(lines)

    def get_valid_actions(self) -> List[Tuple[int, int, int]]:
        """Get list of valid actions in current state."""
        valid = [(ActionType.NO_OP.value, 0, 0)]

        for op_idx, op in enumerate(self.operations):
            if op["status"] in ["pending", "delayed"]:
                # Can reassign to available machines
                for m_idx, machine in enumerate(self.machines):
                    if machine["status"] == "available":
                        valid.append((ActionType.REASSIGN_MACHINE.value, op_idx, m_idx))

                # Can reschedule
                valid.append((ActionType.RESCHEDULE_EARLIER.value, op_idx, 0))
                valid.append((ActionType.RESCHEDULE_LATER.value, op_idx, 0))
                valid.append((ActionType.PRIORITIZE_JOB.value, op_idx, 0))

        return valid
