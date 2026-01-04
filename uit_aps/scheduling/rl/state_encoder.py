# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
State Encoder for RL Scheduling Agent

Encodes the scheduling state into feature vectors suitable for neural networks.
Supports multiple encoding strategies:
- Flat encoding: Simple concatenation of features
- Graph encoding: For GNN-based agents (Tier 3)
- Attention encoding: For transformer-based agents
"""

import numpy as np
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum


class EncodingType(Enum):
    """Types of state encoding."""
    FLAT = "flat"
    GRAPH = "graph"
    ATTENTION = "attention"


@dataclass
class EncoderConfig:
    """Configuration for the state encoder."""
    # Dimensions
    operation_embed_dim: int = 32
    machine_embed_dim: int = 16
    global_embed_dim: int = 16

    # Normalization
    max_duration_mins: int = 480
    max_tardiness_mins: int = 1440
    max_priority: int = 10
    max_machines: int = 20
    max_operations: int = 100

    # Encoding type
    encoding_type: EncodingType = EncodingType.FLAT

    # Time reference
    time_horizon_hours: int = 24


class StateEncoder:
    """
    Encodes scheduling state into neural network-friendly representations.

    The encoder transforms raw scheduling data (operations, machines, time)
    into normalized feature vectors that can be processed by RL agents.
    """

    def __init__(self, config: EncoderConfig = None):
        """
        Initialize the state encoder.

        Args:
            config: Encoder configuration
        """
        self.config = config or EncoderConfig()
        self.reference_time: Optional[datetime] = None

    def set_reference_time(self, reference_time: datetime):
        """Set the reference time for temporal encoding."""
        self.reference_time = reference_time

    def encode(
        self,
        operations: List[Dict],
        machines: List[Dict],
        current_time: datetime,
        disruptions: List[Dict] = None
    ) -> np.ndarray:
        """
        Encode the full scheduling state.

        Args:
            operations: List of operation dictionaries
            machines: List of machine dictionaries
            current_time: Current simulation time
            disruptions: Active disruptions

        Returns:
            Encoded state vector
        """
        if self.reference_time is None:
            self.reference_time = current_time

        if self.config.encoding_type == EncodingType.FLAT:
            return self._encode_flat(operations, machines, current_time, disruptions)
        elif self.config.encoding_type == EncodingType.GRAPH:
            return self._encode_graph(operations, machines, current_time, disruptions)
        elif self.config.encoding_type == EncodingType.ATTENTION:
            return self._encode_attention(operations, machines, current_time, disruptions)

        return self._encode_flat(operations, machines, current_time, disruptions)

    def _encode_flat(
        self,
        operations: List[Dict],
        machines: List[Dict],
        current_time: datetime,
        disruptions: List[Dict] = None
    ) -> np.ndarray:
        """
        Flat encoding: concatenate all features into a single vector.

        Returns:
            1D numpy array of features
        """
        features = []

        # Encode operations
        for op in operations[:self.config.max_operations]:
            op_features = self.encode_operation(op, current_time)
            features.extend(op_features)

        # Pad if necessary
        padding_needed = self.config.max_operations - len(operations)
        if padding_needed > 0:
            features.extend([0.0] * padding_needed * self.config.operation_embed_dim)

        # Encode machines
        for machine in machines[:self.config.max_machines]:
            machine_features = self.encode_machine(machine, current_time)
            features.extend(machine_features)

        # Pad if necessary
        padding_needed = self.config.max_machines - len(machines)
        if padding_needed > 0:
            features.extend([0.0] * padding_needed * self.config.machine_embed_dim)

        # Encode global state
        global_features = self.encode_global(
            operations, machines, current_time, disruptions
        )
        features.extend(global_features)

        return np.array(features, dtype=np.float32)

    def _encode_graph(
        self,
        operations: List[Dict],
        machines: List[Dict],
        current_time: datetime,
        disruptions: List[Dict] = None
    ) -> Dict[str, np.ndarray]:
        """
        Graph encoding for GNN-based agents.

        Returns:
            Dictionary with node features and edge indices
        """
        # Node features
        op_features = []
        machine_features = []

        for op in operations:
            if op.get("status") != "empty":
                op_features.append(self.encode_operation(op, current_time))

        for machine in machines:
            if machine.get("id"):
                machine_features.append(self.encode_machine(machine, current_time))

        # Edge indices (operation -> machine assignments)
        edge_index = []
        for i, op in enumerate(operations):
            if op.get("status") != "empty" and op.get("machine_id"):
                for j, machine in enumerate(machines):
                    if machine.get("id") == op["machine_id"]:
                        edge_index.append([i, len(operations) + j])
                        edge_index.append([len(operations) + j, i])

        # Job precedence edges
        job_ops = {}
        for i, op in enumerate(operations):
            job_id = op.get("job_id")
            if job_id:
                if job_id not in job_ops:
                    job_ops[job_id] = []
                job_ops[job_id].append(i)

        for job_id, op_indices in job_ops.items():
            for k in range(len(op_indices) - 1):
                edge_index.append([op_indices[k], op_indices[k + 1]])

        return {
            "operation_features": np.array(op_features, dtype=np.float32) if op_features else np.zeros((0, self.config.operation_embed_dim)),
            "machine_features": np.array(machine_features, dtype=np.float32) if machine_features else np.zeros((0, self.config.machine_embed_dim)),
            "edge_index": np.array(edge_index, dtype=np.int64).T if edge_index else np.zeros((2, 0), dtype=np.int64),
            "global_features": np.array(self.encode_global(operations, machines, current_time, disruptions), dtype=np.float32)
        }

    def _encode_attention(
        self,
        operations: List[Dict],
        machines: List[Dict],
        current_time: datetime,
        disruptions: List[Dict] = None
    ) -> Dict[str, np.ndarray]:
        """
        Attention-based encoding for transformer agents.

        Returns:
            Dictionary with sequence features and masks
        """
        # Operation sequence
        op_sequence = []
        op_mask = []

        for op in operations[:self.config.max_operations]:
            if op.get("status") != "empty":
                op_sequence.append(self.encode_operation(op, current_time))
                op_mask.append(1.0)
            else:
                op_sequence.append([0.0] * self.config.operation_embed_dim)
                op_mask.append(0.0)

        # Machine sequence
        machine_sequence = []
        machine_mask = []

        for machine in machines[:self.config.max_machines]:
            if machine.get("id"):
                machine_sequence.append(self.encode_machine(machine, current_time))
                machine_mask.append(1.0)
            else:
                machine_sequence.append([0.0] * self.config.machine_embed_dim)
                machine_mask.append(0.0)

        return {
            "operation_sequence": np.array(op_sequence, dtype=np.float32),
            "operation_mask": np.array(op_mask, dtype=np.float32),
            "machine_sequence": np.array(machine_sequence, dtype=np.float32),
            "machine_mask": np.array(machine_mask, dtype=np.float32),
            "global_features": np.array(self.encode_global(operations, machines, current_time, disruptions), dtype=np.float32)
        }

    def encode_operation(self, op: Dict, current_time: datetime) -> List[float]:
        """
        Encode a single operation into features.

        Features:
        - Temporal: start_offset, end_offset, due_offset, duration
        - Status: one-hot encoding of status
        - Priority: normalized priority
        - Machine: machine index
        - Tardiness: current tardiness

        Args:
            op: Operation dictionary
            current_time: Current time

        Returns:
            List of normalized features
        """
        features = []

        # Empty operation
        if op.get("status") == "empty":
            return [0.0] * self.config.operation_embed_dim

        # Temporal features (4 features)
        start_offset = self._time_to_offset(op.get("start_time"), current_time)
        end_offset = self._time_to_offset(op.get("end_time"), current_time)
        due_offset = self._time_to_offset(op.get("due_date"), current_time)
        duration_norm = (op.get("duration_mins", 0)) / self.config.max_duration_mins

        features.extend([
            np.clip(start_offset, -1.0, 1.0),
            np.clip(end_offset, -1.0, 1.0),
            np.clip(due_offset, -1.0, 1.0),
            np.clip(duration_norm, 0.0, 1.0)
        ])

        # Status features (4 features - one-hot)
        status = op.get("status", "pending")
        status_encoding = {
            "pending": [1, 0, 0, 0],
            "in_progress": [0, 1, 0, 0],
            "completed": [0, 0, 1, 0],
            "delayed": [0, 0, 0, 1]
        }
        features.extend(status_encoding.get(status, [0, 0, 0, 0]))

        # Priority feature (1 feature)
        priority = op.get("priority", 1) / self.config.max_priority
        features.append(np.clip(priority, 0.0, 1.0))

        # Tardiness features (2 features)
        tardiness = op.get("tardiness_mins", 0) / self.config.max_tardiness_mins
        is_late = 1.0 if op.get("is_late", False) else 0.0
        features.extend([np.clip(tardiness, 0.0, 1.0), is_late])

        # Urgency feature (1 feature) - time until due date
        urgency = 0.0
        if op.get("due_date") and current_time:
            time_to_due = (op["due_date"] - current_time).total_seconds() / 3600
            urgency = np.clip(1.0 - (time_to_due / self.config.time_horizon_hours), 0.0, 1.0)
        features.append(urgency)

        # Slack feature (1 feature) - due date - (current time + remaining duration)
        slack = 0.0
        if op.get("due_date") and current_time:
            remaining = op.get("duration_mins", 0) if status != "completed" else 0
            finish_time = current_time + timedelta(minutes=remaining)
            slack_mins = (op["due_date"] - finish_time).total_seconds() / 60
            slack = np.clip(slack_mins / self.config.max_tardiness_mins, -1.0, 1.0)
        features.append(slack)

        # Pad to embed_dim
        while len(features) < self.config.operation_embed_dim:
            features.append(0.0)

        return features[:self.config.operation_embed_dim]

    def encode_machine(self, machine: Dict, current_time: datetime) -> List[float]:
        """
        Encode a single machine into features.

        Features:
        - Status: one-hot encoding
        - Utilization: current utilization
        - Remaining time: time until available
        - Capacity: normalized capacity

        Args:
            machine: Machine dictionary
            current_time: Current time

        Returns:
            List of normalized features
        """
        features = []

        # Empty machine
        if not machine.get("id"):
            return [0.0] * self.config.machine_embed_dim

        # Status features (4 features - one-hot)
        status = machine.get("status", "available")
        status_encoding = {
            "available": [1, 0, 0, 0],
            "busy": [0, 1, 0, 0],
            "breakdown": [0, 0, 1, 0],
            "maintenance": [0, 0, 0, 1]
        }
        features.extend(status_encoding.get(status, [0, 0, 0, 0]))

        # Utilization feature (1 feature)
        utilization = machine.get("utilization", 0.0)
        features.append(np.clip(utilization, 0.0, 1.0))

        # Remaining time feature (1 feature)
        remaining = machine.get("remaining_time_mins", 0) / self.config.max_duration_mins
        features.append(np.clip(remaining, 0.0, 1.0))

        # Capacity feature (1 feature)
        capacity = machine.get("capacity", 1) / 5.0  # Assume max capacity of 5
        features.append(np.clip(capacity, 0.0, 1.0))

        # Time until available (1 feature)
        time_until_available = 0.0
        if machine.get("breakdown_until") and current_time:
            time_delta = (machine["breakdown_until"] - current_time).total_seconds() / 60
            time_until_available = np.clip(time_delta / self.config.max_duration_mins, 0.0, 1.0)
        features.append(time_until_available)

        # Current workload (1 feature) - number of pending operations
        # This would need to be calculated from operations
        features.append(0.0)  # Placeholder

        # Pad to embed_dim
        while len(features) < self.config.machine_embed_dim:
            features.append(0.0)

        return features[:self.config.machine_embed_dim]

    def encode_global(
        self,
        operations: List[Dict],
        machines: List[Dict],
        current_time: datetime,
        disruptions: List[Dict] = None
    ) -> List[float]:
        """
        Encode global state features.

        Features:
        - Time progress
        - Pending/completed ratios
        - Disruption count
        - Overall metrics

        Args:
            operations: List of operations
            machines: List of machines
            current_time: Current time
            disruptions: Active disruptions

        Returns:
            List of global features
        """
        features = []

        # Time progress (1 feature)
        if self.reference_time:
            elapsed = (current_time - self.reference_time).total_seconds() / 3600
            time_progress = elapsed / self.config.time_horizon_hours
        else:
            time_progress = 0.0
        features.append(np.clip(time_progress, 0.0, 1.0))

        # Operation status counts (4 features)
        total_ops = sum(1 for op in operations if op.get("status") != "empty")
        pending = sum(1 for op in operations if op.get("status") == "pending")
        in_progress = sum(1 for op in operations if op.get("status") == "in_progress")
        completed = sum(1 for op in operations if op.get("status") == "completed")
        delayed = sum(1 for op in operations if op.get("status") == "delayed")

        if total_ops > 0:
            features.extend([
                pending / total_ops,
                in_progress / total_ops,
                completed / total_ops,
                delayed / total_ops
            ])
        else:
            features.extend([0.0, 0.0, 0.0, 0.0])

        # Late jobs ratio (1 feature)
        late_jobs = sum(1 for op in operations if op.get("is_late", False))
        late_ratio = late_jobs / max(1, total_ops)
        features.append(np.clip(late_ratio, 0.0, 1.0))

        # Total tardiness (1 feature)
        total_tardiness = sum(op.get("tardiness_mins", 0) for op in operations)
        tardiness_norm = total_tardiness / (self.config.max_tardiness_mins * max(1, total_ops))
        features.append(np.clip(tardiness_norm, 0.0, 1.0))

        # Machine availability (1 feature)
        total_machines = sum(1 for m in machines if m.get("id"))
        available_machines = sum(1 for m in machines if m.get("status") == "available")
        availability = available_machines / max(1, total_machines)
        features.append(np.clip(availability, 0.0, 1.0))

        # Average utilization (1 feature)
        utilizations = [m.get("utilization", 0.0) for m in machines if m.get("id")]
        avg_utilization = np.mean(utilizations) if utilizations else 0.0
        features.append(np.clip(avg_utilization, 0.0, 1.0))

        # Disruption count (1 feature)
        disruption_count = len(disruptions) if disruptions else 0
        disruption_norm = disruption_count / 5.0  # Assume max 5 concurrent disruptions
        features.append(np.clip(disruption_norm, 0.0, 1.0))

        # Workload balance (1 feature) - std dev of machine utilization
        if len(utilizations) > 1:
            workload_balance = 1.0 - np.std(utilizations)
        else:
            workload_balance = 1.0
        features.append(np.clip(workload_balance, 0.0, 1.0))

        # Pad to embed_dim
        while len(features) < self.config.global_embed_dim:
            features.append(0.0)

        return features[:self.config.global_embed_dim]

    def _time_to_offset(
        self,
        time: Optional[datetime],
        current_time: datetime
    ) -> float:
        """
        Convert datetime to normalized offset from current time.

        Args:
            time: Target datetime
            current_time: Reference time

        Returns:
            Normalized offset in range [-1, 1]
        """
        if time is None or current_time is None:
            return 0.0

        delta_mins = (time - current_time).total_seconds() / 60
        horizon_mins = self.config.time_horizon_hours * 60

        return delta_mins / horizon_mins

    def get_observation_dim(self) -> int:
        """Get the total observation dimension for flat encoding."""
        return (
            self.config.max_operations * self.config.operation_embed_dim +
            self.config.max_machines * self.config.machine_embed_dim +
            self.config.global_embed_dim
        )

    def decode_action(
        self,
        action: np.ndarray,
        operations: List[Dict],
        machines: List[Dict]
    ) -> Tuple[int, int, int]:
        """
        Decode network output to action tuple.

        Args:
            action: Network output
            operations: Current operations
            machines: Current machines

        Returns:
            Tuple of (action_type, operation_idx, machine_idx)
        """
        if len(action) == 3:
            # Direct output
            action_type = int(action[0])
            op_idx = int(action[1])
            machine_idx = int(action[2])
        else:
            # Softmax output - take argmax
            action_type = int(np.argmax(action[:7]))
            op_idx = int(np.argmax(action[7:7 + self.config.max_operations]))
            machine_idx = int(np.argmax(action[7 + self.config.max_operations:]))

        # Validate indices
        op_idx = min(op_idx, len(operations) - 1)
        machine_idx = min(machine_idx, len(machines) - 1)

        return action_type, op_idx, machine_idx
