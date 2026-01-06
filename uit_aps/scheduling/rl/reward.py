# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Reward Functions for RL Scheduling Agent

Implements reward calculation for the scheduling environment.
Supports multiple reward shaping strategies:
- Sparse: Reward only at episode end
- Dense: Reward at each step
- Shaped: Intermediate rewards to guide learning
"""

import numpy as np
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum


class RewardType(Enum):
    """Types of reward calculation."""
    SPARSE = "sparse"
    DENSE = "dense"
    SHAPED = "shaped"
    MULTI_OBJECTIVE = "multi_objective"


@dataclass
class RewardConfig:
    """Configuration for reward calculation."""
    reward_type: RewardType = RewardType.SHAPED

    # Penalty weights (negative rewards)
    tardiness_penalty: float = -1.0       # Per minute of tardiness
    late_job_penalty: float = -10.0       # Per late job
    makespan_penalty: float = -0.01       # Per minute of makespan
    idle_time_penalty: float = -0.1       # Per minute of machine idle time
    disruption_penalty: float = -5.0      # Per unhandled disruption

    # Reward weights (positive rewards)
    completion_reward: float = 5.0        # Per completed job
    on_time_reward: float = 10.0          # Per on-time completion
    utilization_reward: float = 1.0       # For high utilization
    action_success_reward: float = 0.5    # For successful action
    disruption_handled_reward: float = 2.0  # For handling disruption

    # Normalization
    max_tardiness_mins: int = 1440
    max_makespan_mins: int = 2880
    reward_scale: float = 1.0

    # Shaping parameters
    potential_discount: float = 0.99
    slack_reward_scale: float = 0.1


class RewardCalculator:
    """
    Calculates rewards for the RL scheduling agent.

    The reward function balances multiple objectives:
    - Minimize tardiness
    - Maximize on-time delivery
    - Maximize machine utilization
    - Handle disruptions effectively
    """

    def __init__(self, config: RewardConfig = None):
        """
        Initialize the reward calculator.

        Args:
            config: Reward configuration
        """
        self.config = config or RewardConfig()

        # State tracking for shaped rewards
        self.previous_potential: float = 0.0
        self.previous_tardiness: float = 0.0
        self.previous_completed: int = 0

    def reset(self):
        """Reset state for new episode."""
        self.previous_potential = 0.0
        self.previous_tardiness = 0.0
        self.previous_completed = 0

    def calculate(
        self,
        operations: List[Dict],
        machines: List[Dict],
        current_time: datetime,
        action_success: bool,
        disruptions_handled: int = 0,
        is_terminal: bool = False
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate reward for the current state.

        Args:
            operations: Current operation states
            machines: Current machine states
            current_time: Current simulation time
            action_success: Whether the last action succeeded
            disruptions_handled: Number of disruptions handled this step
            is_terminal: Whether this is the final state

        Returns:
            Tuple of (total_reward, reward_components)
        """
        if self.config.reward_type == RewardType.SPARSE:
            return self._calculate_sparse(operations, is_terminal)
        elif self.config.reward_type == RewardType.DENSE:
            return self._calculate_dense(
                operations, machines, action_success, disruptions_handled
            )
        elif self.config.reward_type == RewardType.SHAPED:
            return self._calculate_shaped(
                operations, machines, current_time, action_success, disruptions_handled
            )
        elif self.config.reward_type == RewardType.MULTI_OBJECTIVE:
            return self._calculate_multi_objective(
                operations, machines, current_time, action_success, disruptions_handled
            )

        return 0.0, {}

    def _calculate_sparse(
        self,
        operations: List[Dict],
        is_terminal: bool
    ) -> Tuple[float, Dict[str, float]]:
        """
        Sparse reward: Only reward at episode end.

        Args:
            operations: Current operation states
            is_terminal: Whether this is the final state

        Returns:
            Tuple of (total_reward, reward_components)
        """
        if not is_terminal:
            return 0.0, {"type": "sparse", "is_terminal": False}

        components = {}

        # Count completed and late jobs
        completed = sum(1 for op in operations if op.get("status") == "completed")
        late = sum(1 for op in operations if op.get("is_late", False))
        on_time = completed - late

        # Total tardiness
        total_tardiness = sum(op.get("tardiness_mins", 0) for op in operations)

        # Calculate rewards
        components["completion"] = completed * self.config.completion_reward
        components["on_time"] = on_time * self.config.on_time_reward
        components["late_penalty"] = late * self.config.late_job_penalty
        components["tardiness_penalty"] = (
            total_tardiness / self.config.max_tardiness_mins *
            self.config.tardiness_penalty * 100
        )

        total_reward = sum(components.values()) * self.config.reward_scale

        return total_reward, components

    def _calculate_dense(
        self,
        operations: List[Dict],
        machines: List[Dict],
        action_success: bool,
        disruptions_handled: int
    ) -> Tuple[float, Dict[str, float]]:
        """
        Dense reward: Reward at each step based on current state.

        Args:
            operations: Current operation states
            machines: Current machine states
            action_success: Whether the last action succeeded
            disruptions_handled: Number of disruptions handled

        Returns:
            Tuple of (total_reward, reward_components)
        """
        components = {}

        # Completion rewards (incremental)
        completed = sum(1 for op in operations if op.get("status") == "completed")
        new_completed = completed - self.previous_completed
        self.previous_completed = completed

        components["completion"] = new_completed * self.config.completion_reward

        # On-time bonus for newly completed
        if new_completed > 0:
            recent_on_time = sum(
                1 for op in operations
                if op.get("status") == "completed" and not op.get("is_late", False)
            )
            components["on_time"] = (recent_on_time / max(1, completed)) * self.config.on_time_reward

        # Tardiness penalty (incremental)
        current_tardiness = sum(op.get("tardiness_mins", 0) for op in operations)
        tardiness_delta = current_tardiness - self.previous_tardiness
        self.previous_tardiness = current_tardiness

        if tardiness_delta > 0:
            components["tardiness_penalty"] = (
                tardiness_delta / self.config.max_tardiness_mins *
                self.config.tardiness_penalty * 10
            )

        # Utilization reward
        utilizations = [m.get("utilization", 0.0) for m in machines if m.get("id")]
        if utilizations:
            avg_util = np.mean(utilizations)
            components["utilization"] = avg_util * self.config.utilization_reward

        # Action success reward
        if action_success:
            components["action_success"] = self.config.action_success_reward

        # Disruption handling reward
        if disruptions_handled > 0:
            components["disruption_handled"] = (
                disruptions_handled * self.config.disruption_handled_reward
            )

        total_reward = sum(components.values()) * self.config.reward_scale

        return total_reward, components

    def _calculate_shaped(
        self,
        operations: List[Dict],
        machines: List[Dict],
        current_time: datetime,
        action_success: bool,
        disruptions_handled: int
    ) -> Tuple[float, Dict[str, float]]:
        """
        Shaped reward: Use potential-based reward shaping.

        Uses the difference in potential function to provide
        intermediate guidance while maintaining optimal policy.

        Args:
            operations: Current operation states
            machines: Current machine states
            current_time: Current simulation time
            action_success: Whether the last action succeeded
            disruptions_handled: Number of disruptions handled

        Returns:
            Tuple of (total_reward, reward_components)
        """
        components = {}

        # Calculate current potential
        current_potential = self._calculate_potential(operations, machines, current_time)

        # Shaping reward from potential difference
        shaping_reward = (
            self.config.potential_discount * current_potential -
            self.previous_potential
        )
        self.previous_potential = current_potential

        components["shaping"] = shaping_reward

        # Add dense components
        dense_reward, dense_components = self._calculate_dense(
            operations, machines, action_success, disruptions_handled
        )

        for key, value in dense_components.items():
            components[f"dense_{key}"] = value

        # Slack-based reward (encourage maintaining slack)
        slack_reward = self._calculate_slack_reward(operations, current_time)
        components["slack"] = slack_reward * self.config.slack_reward_scale

        total_reward = sum(components.values()) * self.config.reward_scale

        return total_reward, components

    def _calculate_multi_objective(
        self,
        operations: List[Dict],
        machines: List[Dict],
        current_time: datetime,
        action_success: bool,
        disruptions_handled: int
    ) -> Tuple[float, Dict[str, float]]:
        """
        Multi-objective reward: Return multiple objectives separately.

        This is useful for multi-objective RL algorithms.

        Args:
            operations: Current operation states
            machines: Current machine states
            current_time: Current simulation time
            action_success: Whether the last action succeeded
            disruptions_handled: Number of disruptions handled

        Returns:
            Tuple of (total_reward, reward_components)
        """
        components = {}

        # Objective 1: Minimize tardiness
        total_tardiness = sum(op.get("tardiness_mins", 0) for op in operations)
        components["tardiness"] = -total_tardiness / self.config.max_tardiness_mins

        # Objective 2: Maximize on-time delivery
        completed = sum(1 for op in operations if op.get("status") == "completed")
        on_time = sum(
            1 for op in operations
            if op.get("status") == "completed" and not op.get("is_late", False)
        )
        components["on_time_rate"] = on_time / max(1, completed)

        # Objective 3: Maximize utilization
        utilizations = [m.get("utilization", 0.0) for m in machines if m.get("id")]
        components["utilization"] = np.mean(utilizations) if utilizations else 0.0

        # Objective 4: Minimize makespan (estimated)
        end_times = [
            op.get("end_time") for op in operations
            if op.get("end_time") and op.get("status") != "empty"
        ]
        if end_times and current_time:
            max_end = max(end_times)
            makespan_mins = (max_end - current_time).total_seconds() / 60
            components["makespan"] = -makespan_mins / self.config.max_makespan_mins
        else:
            components["makespan"] = 0.0

        # Objective 5: Disruption resilience
        pending_ops = sum(1 for op in operations if op.get("status") == "pending")
        delayed_ops = sum(1 for op in operations if op.get("status") == "delayed")
        components["resilience"] = 1.0 - (delayed_ops / max(1, pending_ops + delayed_ops))

        # Weighted sum for total reward
        weights = {
            "tardiness": 0.3,
            "on_time_rate": 0.25,
            "utilization": 0.2,
            "makespan": 0.15,
            "resilience": 0.1
        }

        total_reward = sum(
            components[key] * weights.get(key, 0.0)
            for key in components
        ) * self.config.reward_scale

        return total_reward, components

    def _calculate_potential(
        self,
        operations: List[Dict],
        machines: List[Dict],
        current_time: datetime
    ) -> float:
        """
        Calculate potential function for reward shaping.

        The potential represents how "good" the current state is.
        Higher potential = better state.

        Args:
            operations: Current operation states
            machines: Current machine states
            current_time: Current simulation time

        Returns:
            Potential value
        """
        potential = 0.0

        # Completion potential
        total_ops = sum(1 for op in operations if op.get("status") != "empty")
        completed = sum(1 for op in operations if op.get("status") == "completed")
        if total_ops > 0:
            potential += (completed / total_ops) * 10.0

        # Slack potential (more slack = higher potential)
        for op in operations:
            if op.get("status") in ["pending", "in_progress"]:
                slack = self._get_operation_slack(op, current_time)
                potential += np.clip(slack / 60, -1.0, 1.0)  # Normalize to hours

        # Utilization potential
        utilizations = [m.get("utilization", 0.0) for m in machines if m.get("id")]
        if utilizations:
            potential += np.mean(utilizations) * 5.0

        # Tardiness penalty
        total_tardiness = sum(op.get("tardiness_mins", 0) for op in operations)
        potential -= (total_tardiness / self.config.max_tardiness_mins) * 10.0

        return potential

    def _calculate_slack_reward(
        self,
        operations: List[Dict],
        current_time: datetime
    ) -> float:
        """
        Calculate reward based on maintaining slack (buffer time).

        Operations with more slack are more resilient to disruptions.

        Args:
            operations: Current operation states
            current_time: Current simulation time

        Returns:
            Slack-based reward
        """
        total_slack = 0.0
        count = 0

        for op in operations:
            if op.get("status") in ["pending", "in_progress"]:
                slack = self._get_operation_slack(op, current_time)
                if slack > 0:
                    total_slack += np.log1p(slack)  # Log scale for diminishing returns
                else:
                    total_slack += slack / 60  # Penalty for negative slack
                count += 1

        return total_slack / max(1, count)

    def _get_operation_slack(self, op: Dict, current_time: datetime) -> float:
        """
        Calculate slack time for an operation.

        Slack = Due date - Expected completion time

        Args:
            op: Operation dictionary
            current_time: Current time

        Returns:
            Slack in minutes
        """
        if not op.get("due_date"):
            return 0.0

        if op.get("status") == "completed":
            if op.get("end_time"):
                return (op["due_date"] - op["end_time"]).total_seconds() / 60
            return 0.0

        # Estimate completion time
        # Convert numpy.int64 to int for timedelta
        duration_mins = int(op.get("duration_mins", 60))
        if op.get("end_time"):
            expected_end = op["end_time"]
        elif op.get("start_time"):
            duration = timedelta(minutes=duration_mins)
            expected_end = op["start_time"] + duration
        else:
            expected_end = current_time + timedelta(minutes=duration_mins)

        return (op["due_date"] - expected_end).total_seconds() / 60

    def get_reward_summary(
        self,
        operations: List[Dict],
        machines: List[Dict]
    ) -> Dict[str, float]:
        """
        Get summary of reward-related metrics.

        Args:
            operations: Operation states
            machines: Machine states

        Returns:
            Dictionary of metrics
        """
        total_ops = sum(1 for op in operations if op.get("status") != "empty")
        completed = sum(1 for op in operations if op.get("status") == "completed")
        late = sum(1 for op in operations if op.get("is_late", False))
        on_time = completed - late

        total_tardiness = sum(op.get("tardiness_mins", 0) for op in operations)

        utilizations = [m.get("utilization", 0.0) for m in machines if m.get("id")]

        return {
            "total_operations": total_ops,
            "completed": completed,
            "completion_rate": completed / max(1, total_ops),
            "on_time": on_time,
            "on_time_rate": on_time / max(1, completed) if completed > 0 else 0.0,
            "late": late,
            "total_tardiness_mins": total_tardiness,
            "avg_tardiness_mins": total_tardiness / max(1, late) if late > 0 else 0.0,
            "avg_utilization": np.mean(utilizations) if utilizations else 0.0,
            "utilization_std": np.std(utilizations) if len(utilizations) > 1 else 0.0
        }
