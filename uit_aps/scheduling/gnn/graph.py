# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Scheduling Graph Construction

Converts scheduling problems into graph representations for GNN processing.
The graph structure captures:
- Jobs, operations, and machines as nodes
- Precedence constraints as edges
- Machine assignments as edges
- Temporal relationships as edge features
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import numpy as np

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class NodeType(Enum):
    """Types of nodes in the scheduling graph."""
    JOB = 0
    OPERATION = 1
    MACHINE = 2


class EdgeType(Enum):
    """Types of edges in the scheduling graph."""
    JOB_TO_OPERATION = 0      # Job contains operation
    PRECEDENCE = 1             # Operation must precede another
    MACHINE_ASSIGNMENT = 2     # Operation assigned to machine
    MACHINE_CAPABLE = 3        # Machine can process operation
    TEMPORAL = 4               # Temporal relationship


@dataclass
class NodeFeatures:
    """Features for a graph node."""
    node_type: NodeType
    node_id: str
    features: np.ndarray  # Feature vector

    # Node-specific attributes
    job_id: str = None
    operation_id: str = None
    machine_id: str = None

    # Scheduling attributes
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    due_date: float = 0.0
    priority: int = 0
    status: str = "pending"


@dataclass
class EdgeFeatures:
    """Features for a graph edge."""
    edge_type: EdgeType
    source_idx: int
    target_idx: int
    features: np.ndarray  # Feature vector

    # Edge-specific attributes
    weight: float = 1.0
    temporal_gap: float = 0.0  # Time gap between connected nodes


@dataclass
class SchedulingGraphConfig:
    """Configuration for scheduling graph construction."""
    # Node feature dimensions
    job_feature_dim: int = 8
    operation_feature_dim: int = 16
    machine_feature_dim: int = 12

    # Edge feature dimensions
    edge_feature_dim: int = 8

    # Graph structure options
    include_machine_capability_edges: bool = True
    include_temporal_edges: bool = True
    temporal_edge_threshold_mins: float = 60.0  # Connect operations within this time

    # Normalization
    normalize_features: bool = True
    max_time_horizon_mins: float = 1440.0  # 24 hours
    max_duration_mins: float = 480.0  # 8 hours


class SchedulingGraph:
    """
    Graph representation of a scheduling problem.

    The graph structure:
    - Job nodes: Represent production jobs with aggregated features
    - Operation nodes: Individual operations with detailed features
    - Machine nodes: Available machines/workstations

    Edges connect:
    - Jobs to their operations
    - Operations in precedence order
    - Operations to assigned/capable machines
    """

    def __init__(self, config: SchedulingGraphConfig = None):
        """
        Initialize the scheduling graph.

        Args:
            config: Graph configuration
        """
        self.config = config or SchedulingGraphConfig()

        # Node storage
        self.nodes: List[NodeFeatures] = []
        self.node_id_to_idx: Dict[str, int] = {}

        # Edge storage
        self.edges: List[EdgeFeatures] = []

        # Indices by type
        self.job_indices: List[int] = []
        self.operation_indices: List[int] = []
        self.machine_indices: List[int] = []

        # Metadata
        self.num_jobs = 0
        self.num_operations = 0
        self.num_machines = 0

    def add_job_node(
        self,
        job_id: str,
        due_date: float,
        priority: int,
        num_operations: int,
        status: str = "pending",
        **kwargs
    ) -> int:
        """
        Add a job node to the graph.

        Args:
            job_id: Unique job identifier
            due_date: Job due date (minutes from start)
            priority: Job priority (higher = more important)
            num_operations: Number of operations in job
            status: Job status
            **kwargs: Additional features

        Returns:
            Node index
        """
        # Build feature vector
        features = np.zeros(self.config.job_feature_dim, dtype=np.float32)
        features[0] = self._normalize_time(due_date)
        features[1] = priority / 10.0  # Normalize priority
        features[2] = num_operations / 20.0  # Normalize operation count
        features[3] = self._encode_status(status)
        features[4] = kwargs.get("total_duration", 0) / self.config.max_duration_mins
        features[5] = kwargs.get("slack", 0) / self.config.max_time_horizon_mins
        features[6] = 1.0 if status == "late" else 0.0
        features[7] = kwargs.get("completion_ratio", 0.0)

        node = NodeFeatures(
            node_type=NodeType.JOB,
            node_id=job_id,
            features=features,
            job_id=job_id,
            due_date=due_date,
            priority=priority,
            status=status
        )

        idx = len(self.nodes)
        self.nodes.append(node)
        self.node_id_to_idx[job_id] = idx
        self.job_indices.append(idx)
        self.num_jobs += 1

        return idx

    def add_operation_node(
        self,
        operation_id: str,
        job_id: str,
        start_time: float,
        end_time: float,
        duration: float,
        due_date: float,
        priority: int,
        status: str = "pending",
        assigned_machine: str = None,
        sequence_idx: int = 0,
        **kwargs
    ) -> int:
        """
        Add an operation node to the graph.

        Args:
            operation_id: Unique operation identifier
            job_id: Parent job identifier
            start_time: Scheduled start time
            end_time: Scheduled end time
            duration: Processing duration
            due_date: Due date (from job)
            priority: Priority (from job)
            status: Operation status
            assigned_machine: Assigned workstation
            sequence_idx: Position in job sequence
            **kwargs: Additional features

        Returns:
            Node index
        """
        # Build feature vector
        features = np.zeros(self.config.operation_feature_dim, dtype=np.float32)
        features[0] = self._normalize_time(start_time)
        features[1] = self._normalize_time(end_time)
        features[2] = duration / self.config.max_duration_mins
        features[3] = self._normalize_time(due_date)
        features[4] = priority / 10.0
        features[5] = self._encode_status(status)
        features[6] = sequence_idx / 10.0
        features[7] = 1.0 if status == "late" else 0.0
        features[8] = kwargs.get("slack", 0) / self.config.max_time_horizon_mins
        features[9] = 1.0 if assigned_machine else 0.0
        features[10] = kwargs.get("wait_time", 0) / self.config.max_duration_mins
        features[11] = kwargs.get("utilization", 0.0)
        features[12] = kwargs.get("num_capable_machines", 1) / 10.0
        features[13] = kwargs.get("is_critical_path", 0.0)
        features[14] = kwargs.get("flexibility", 0.5)
        features[15] = kwargs.get("estimated_delay", 0) / self.config.max_duration_mins

        node = NodeFeatures(
            node_type=NodeType.OPERATION,
            node_id=operation_id,
            features=features,
            job_id=job_id,
            operation_id=operation_id,
            machine_id=assigned_machine,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            due_date=due_date,
            priority=priority,
            status=status
        )

        idx = len(self.nodes)
        self.nodes.append(node)
        self.node_id_to_idx[operation_id] = idx
        self.operation_indices.append(idx)
        self.num_operations += 1

        # Add edge from job to operation
        if job_id in self.node_id_to_idx:
            job_idx = self.node_id_to_idx[job_id]
            self.add_edge(job_idx, idx, EdgeType.JOB_TO_OPERATION)

        return idx

    def add_machine_node(
        self,
        machine_id: str,
        machine_type: str,
        capacity: float = 1.0,
        status: str = "available",
        utilization: float = 0.0,
        **kwargs
    ) -> int:
        """
        Add a machine node to the graph.

        Args:
            machine_id: Unique machine identifier
            machine_type: Type of machine
            capacity: Machine capacity
            status: Machine status
            utilization: Current utilization
            **kwargs: Additional features

        Returns:
            Node index
        """
        # Build feature vector
        features = np.zeros(self.config.machine_feature_dim, dtype=np.float32)
        features[0] = self._encode_machine_status(status)
        features[1] = capacity
        features[2] = utilization
        features[3] = self._hash_machine_type(machine_type)
        features[4] = kwargs.get("current_load", 0) / 10.0
        features[5] = kwargs.get("avg_processing_time", 0) / self.config.max_duration_mins
        features[6] = kwargs.get("breakdown_probability", 0.0)
        features[7] = kwargs.get("efficiency", 1.0)
        features[8] = kwargs.get("queue_length", 0) / 10.0
        features[9] = kwargs.get("available_time", 0) / self.config.max_time_horizon_mins
        features[10] = kwargs.get("setup_time", 0) / 60.0  # Normalize by 1 hour
        features[11] = 1.0 if status == "available" else 0.0

        node = NodeFeatures(
            node_type=NodeType.MACHINE,
            node_id=machine_id,
            features=features,
            machine_id=machine_id,
            status=status
        )

        idx = len(self.nodes)
        self.nodes.append(node)
        self.node_id_to_idx[machine_id] = idx
        self.machine_indices.append(idx)
        self.num_machines += 1

        return idx

    def add_edge(
        self,
        source_idx: int,
        target_idx: int,
        edge_type: EdgeType,
        weight: float = 1.0,
        temporal_gap: float = 0.0,
        **kwargs
    ) -> int:
        """
        Add an edge between nodes.

        Args:
            source_idx: Source node index
            target_idx: Target node index
            edge_type: Type of edge
            weight: Edge weight
            temporal_gap: Time gap between nodes
            **kwargs: Additional features

        Returns:
            Edge index
        """
        # Build feature vector
        features = np.zeros(self.config.edge_feature_dim, dtype=np.float32)
        features[0] = edge_type.value / len(EdgeType)
        features[1] = weight
        features[2] = temporal_gap / self.config.max_time_horizon_mins
        features[3] = kwargs.get("is_critical", 0.0)
        features[4] = kwargs.get("flexibility", 0.5)
        features[5] = kwargs.get("setup_required", 0.0)
        features[6] = kwargs.get("priority_diff", 0.0)
        features[7] = kwargs.get("machine_compatibility", 1.0)

        edge = EdgeFeatures(
            edge_type=edge_type,
            source_idx=source_idx,
            target_idx=target_idx,
            features=features,
            weight=weight,
            temporal_gap=temporal_gap
        )

        self.edges.append(edge)
        return len(self.edges) - 1

    def add_precedence_edge(
        self,
        from_operation_id: str,
        to_operation_id: str,
        **kwargs
    ):
        """Add a precedence constraint edge between operations."""
        if from_operation_id not in self.node_id_to_idx:
            return
        if to_operation_id not in self.node_id_to_idx:
            return

        from_idx = self.node_id_to_idx[from_operation_id]
        to_idx = self.node_id_to_idx[to_operation_id]

        from_node = self.nodes[from_idx]
        to_node = self.nodes[to_idx]

        temporal_gap = to_node.start_time - from_node.end_time

        self.add_edge(
            from_idx,
            to_idx,
            EdgeType.PRECEDENCE,
            weight=1.0,
            temporal_gap=temporal_gap,
            **kwargs
        )

    def add_machine_assignment_edge(
        self,
        operation_id: str,
        machine_id: str,
        **kwargs
    ):
        """Add a machine assignment edge."""
        if operation_id not in self.node_id_to_idx:
            return
        if machine_id not in self.node_id_to_idx:
            return

        op_idx = self.node_id_to_idx[operation_id]
        machine_idx = self.node_id_to_idx[machine_id]

        self.add_edge(
            op_idx,
            machine_idx,
            EdgeType.MACHINE_ASSIGNMENT,
            weight=1.0,
            **kwargs
        )

    def add_machine_capability_edge(
        self,
        operation_id: str,
        machine_id: str,
        compatibility: float = 1.0,
        **kwargs
    ):
        """Add a machine capability edge (machine can process operation)."""
        if operation_id not in self.node_id_to_idx:
            return
        if machine_id not in self.node_id_to_idx:
            return

        op_idx = self.node_id_to_idx[operation_id]
        machine_idx = self.node_id_to_idx[machine_id]

        self.add_edge(
            machine_idx,
            op_idx,
            EdgeType.MACHINE_CAPABLE,
            weight=compatibility,
            machine_compatibility=compatibility,
            **kwargs
        )

    def build_temporal_edges(self):
        """Build temporal edges between operations within time threshold."""
        if not self.config.include_temporal_edges:
            return

        threshold = self.config.temporal_edge_threshold_mins

        for i, idx_i in enumerate(self.operation_indices):
            node_i = self.nodes[idx_i]

            for idx_j in self.operation_indices[i+1:]:
                node_j = self.nodes[idx_j]

                # Check if operations are temporally close
                gap_ij = node_j.start_time - node_i.end_time
                gap_ji = node_i.start_time - node_j.end_time

                if 0 <= gap_ij <= threshold:
                    self.add_edge(
                        idx_i,
                        idx_j,
                        EdgeType.TEMPORAL,
                        temporal_gap=gap_ij
                    )
                elif 0 <= gap_ji <= threshold:
                    self.add_edge(
                        idx_j,
                        idx_i,
                        EdgeType.TEMPORAL,
                        temporal_gap=gap_ji
                    )

    def to_tensors(self) -> Dict[str, Any]:
        """
        Convert graph to PyTorch tensors.

        Returns:
            Dictionary with node features, edge indices, edge features
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for tensor conversion")

        # Node features by type
        job_features = torch.tensor(
            [self.nodes[i].features for i in self.job_indices],
            dtype=torch.float32
        ) if self.job_indices else torch.zeros(0, self.config.job_feature_dim)

        op_features = torch.tensor(
            [self.nodes[i].features for i in self.operation_indices],
            dtype=torch.float32
        ) if self.operation_indices else torch.zeros(0, self.config.operation_feature_dim)

        machine_features = torch.tensor(
            [self.nodes[i].features for i in self.machine_indices],
            dtype=torch.float32
        ) if self.machine_indices else torch.zeros(0, self.config.machine_feature_dim)

        # Edge index (COO format)
        if self.edges:
            edge_index = torch.tensor(
                [[e.source_idx for e in self.edges],
                 [e.target_idx for e in self.edges]],
                dtype=torch.long
            )
            edge_features = torch.tensor(
                [e.features for e in self.edges],
                dtype=torch.float32
            )
            edge_types = torch.tensor(
                [e.edge_type.value for e in self.edges],
                dtype=torch.long
            )
        else:
            edge_index = torch.zeros(2, 0, dtype=torch.long)
            edge_features = torch.zeros(0, self.config.edge_feature_dim)
            edge_types = torch.zeros(0, dtype=torch.long)

        return {
            "job_features": job_features,
            "operation_features": op_features,
            "machine_features": machine_features,
            "edge_index": edge_index,
            "edge_features": edge_features,
            "edge_types": edge_types,
            "num_jobs": self.num_jobs,
            "num_operations": self.num_operations,
            "num_machines": self.num_machines,
            "job_indices": torch.tensor(self.job_indices, dtype=torch.long),
            "operation_indices": torch.tensor(self.operation_indices, dtype=torch.long),
            "machine_indices": torch.tensor(self.machine_indices, dtype=torch.long)
        }

    def to_homogeneous(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert to homogeneous graph (single node type).
        Pads all node features to same dimension.

        Returns:
            Tuple of (node_features, edge_index, edge_features)
        """
        max_dim = max(
            self.config.job_feature_dim,
            self.config.operation_feature_dim,
            self.config.machine_feature_dim
        )

        # Pad all features to max dimension
        node_features = []
        for node in self.nodes:
            padded = np.zeros(max_dim, dtype=np.float32)
            padded[:len(node.features)] = node.features
            node_features.append(padded)

        node_features = np.array(node_features)

        # Edge index
        edge_index = np.array([
            [e.source_idx for e in self.edges],
            [e.target_idx for e in self.edges]
        ], dtype=np.int64)

        # Edge features
        edge_features = np.array([e.features for e in self.edges])

        return node_features, edge_index, edge_features

    def _normalize_time(self, time_mins: float) -> float:
        """Normalize time to [0, 1] range."""
        return min(1.0, max(0.0, time_mins / self.config.max_time_horizon_mins))

    def _encode_status(self, status: str) -> float:
        """Encode operation/job status as float."""
        status_map = {
            "pending": 0.0,
            "queued": 0.2,
            "in_progress": 0.5,
            "completed": 1.0,
            "late": -0.5,
            "cancelled": -1.0
        }
        return status_map.get(status.lower(), 0.0)

    def _encode_machine_status(self, status: str) -> float:
        """Encode machine status as float."""
        status_map = {
            "available": 1.0,
            "busy": 0.5,
            "maintenance": 0.2,
            "breakdown": 0.0
        }
        return status_map.get(status.lower(), 0.5)

    def _hash_machine_type(self, machine_type: str) -> float:
        """Hash machine type to [0, 1] range."""
        return (hash(machine_type) % 1000) / 1000.0

    def __len__(self) -> int:
        """Return total number of nodes."""
        return len(self.nodes)

    def __repr__(self) -> str:
        return (
            f"SchedulingGraph(jobs={self.num_jobs}, "
            f"operations={self.num_operations}, "
            f"machines={self.num_machines}, "
            f"edges={len(self.edges)})"
        )


def build_graph_from_schedule(
    schedule: List[Dict],
    machines: List[Dict],
    jobs: List[Dict] = None,
    config: SchedulingGraphConfig = None
) -> SchedulingGraph:
    """
    Build a scheduling graph from schedule data.

    Args:
        schedule: List of operation dictionaries
        machines: List of machine dictionaries
        jobs: List of job dictionaries (optional, derived from operations)
        config: Graph configuration

    Returns:
        SchedulingGraph instance
    """
    graph = SchedulingGraph(config)

    # Group operations by job
    ops_by_job: Dict[str, List[Dict]] = {}
    for op in schedule:
        job_id = op.get("job_id") or op.get("work_order")
        if job_id not in ops_by_job:
            ops_by_job[job_id] = []
        ops_by_job[job_id].append(op)

    # Add job nodes
    for job_id, ops in ops_by_job.items():
        # Calculate job-level features
        due_date = max(op.get("due_date", 0) for op in ops)
        priority = max(op.get("priority", 0) for op in ops)
        total_duration = sum(op.get("duration", 0) for op in ops)

        completed = sum(1 for op in ops if op.get("status") == "completed")
        completion_ratio = completed / len(ops) if ops else 0

        any_late = any(op.get("status") == "late" for op in ops)

        graph.add_job_node(
            job_id=job_id,
            due_date=due_date,
            priority=priority,
            num_operations=len(ops),
            status="late" if any_late else "pending",
            total_duration=total_duration,
            completion_ratio=completion_ratio
        )

    # Add machine nodes
    for machine in machines:
        machine_id = machine.get("machine_id") or machine.get("workstation")
        graph.add_machine_node(
            machine_id=machine_id,
            machine_type=machine.get("machine_type", "default"),
            capacity=machine.get("capacity", 1.0),
            status=machine.get("status", "available"),
            utilization=machine.get("utilization", 0.0),
            current_load=machine.get("current_load", 0),
            efficiency=machine.get("efficiency", 1.0)
        )

    # Add operation nodes
    for job_id, ops in ops_by_job.items():
        # Sort by sequence
        sorted_ops = sorted(ops, key=lambda x: x.get("sequence", 0))

        prev_op_id = None
        for seq_idx, op in enumerate(sorted_ops):
            op_id = op.get("operation_id") or op.get("job_card")

            graph.add_operation_node(
                operation_id=op_id,
                job_id=job_id,
                start_time=op.get("start_time", 0),
                end_time=op.get("end_time", 0),
                duration=op.get("duration", 0),
                due_date=op.get("due_date", 0),
                priority=op.get("priority", 0),
                status=op.get("status", "pending"),
                assigned_machine=op.get("machine_id") or op.get("workstation"),
                sequence_idx=seq_idx
            )

            # Add precedence edge
            if prev_op_id:
                graph.add_precedence_edge(prev_op_id, op_id)
            prev_op_id = op_id

            # Add machine assignment edge
            machine_id = op.get("machine_id") or op.get("workstation")
            if machine_id:
                graph.add_machine_assignment_edge(op_id, machine_id)

    # Build temporal edges
    graph.build_temporal_edges()

    return graph
