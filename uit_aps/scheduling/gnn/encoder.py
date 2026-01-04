# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Scheduling Graph Encoder

Encodes scheduling graphs into fixed-size vector representations
that can be used by RL agents or for downstream prediction tasks.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    class nn:
        class Module:
            pass

from uit_aps.scheduling.gnn.graph import SchedulingGraph, SchedulingGraphConfig
from uit_aps.scheduling.gnn.layers import (
    GraphAttentionLayer, GATLayerConfig,
    GraphConvLayer, GCNLayerConfig,
    SchedulingGNNBlock
)


def check_torch():
    """Check if PyTorch is available."""
    if not TORCH_AVAILABLE:
        raise ImportError(
            "PyTorch is required for GNN encoder. "
            "Install with: pip install torch"
        )


@dataclass
class EncoderConfig:
    """Configuration for Scheduling Graph Encoder."""
    # Input dimensions (from graph config)
    job_feature_dim: int = 8
    operation_feature_dim: int = 16
    machine_feature_dim: int = 12
    edge_feature_dim: int = 8

    # Architecture
    hidden_dim: int = 128
    output_dim: int = 256  # Final embedding dimension
    num_gnn_layers: int = 3
    num_attention_heads: int = 4

    # Pooling
    pooling: str = "attention"  # "mean", "max", "attention", "set2set"

    # Regularization
    dropout: float = 0.1

    # Device
    device: str = "cpu"


class NodeTypeEncoder(nn.Module):
    """Encodes different node types to common dimension."""

    def __init__(
        self,
        job_dim: int,
        op_dim: int,
        machine_dim: int,
        hidden_dim: int
    ):
        """
        Initialize node type encoder.

        Args:
            job_dim: Job feature dimension
            op_dim: Operation feature dimension
            machine_dim: Machine feature dimension
            hidden_dim: Common hidden dimension
        """
        check_torch()
        super().__init__()

        self.job_encoder = nn.Sequential(
            nn.Linear(job_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        self.op_encoder = nn.Sequential(
            nn.Linear(op_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        self.machine_encoder = nn.Sequential(
            nn.Linear(machine_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

    def forward(
        self,
        job_features: torch.Tensor,
        op_features: torch.Tensor,
        machine_features: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Encode node features.

        Args:
            job_features: Job features [num_jobs, job_dim]
            op_features: Operation features [num_ops, op_dim]
            machine_features: Machine features [num_machines, machine_dim]

        Returns:
            Tuple of encoded features, each [num_nodes, hidden_dim]
        """
        job_h = self.job_encoder(job_features) if job_features.size(0) > 0 else job_features
        op_h = self.op_encoder(op_features) if op_features.size(0) > 0 else op_features
        machine_h = self.machine_encoder(machine_features) if machine_features.size(0) > 0 else machine_features

        return job_h, op_h, machine_h


class AttentionPooling(nn.Module):
    """Attention-based graph pooling."""

    def __init__(self, hidden_dim: int):
        """
        Initialize attention pooling.

        Args:
            hidden_dim: Hidden dimension
        """
        check_torch()
        super().__init__()

        self.attention = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1)
        )

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        """
        Pool graph to single vector using attention.

        Args:
            x: Node features [N, hidden_dim]
            mask: Optional mask [N]

        Returns:
            Pooled vector [hidden_dim]
        """
        # Compute attention weights
        attn = self.attention(x).squeeze(-1)  # [N]

        if mask is not None:
            attn = attn.masked_fill(~mask, float("-inf"))

        attn = F.softmax(attn, dim=0)  # [N]

        # Weighted sum
        pooled = (x * attn.unsqueeze(-1)).sum(dim=0)  # [hidden_dim]

        return pooled


class Set2SetPooling(nn.Module):
    """Set2Set pooling for permutation-invariant graph embedding."""

    def __init__(self, hidden_dim: int, processing_steps: int = 3):
        """
        Initialize Set2Set pooling.

        Args:
            hidden_dim: Hidden dimension
            processing_steps: Number of LSTM processing steps
        """
        check_torch()
        super().__init__()

        self.hidden_dim = hidden_dim
        self.processing_steps = processing_steps

        self.lstm = nn.LSTM(hidden_dim * 2, hidden_dim, batch_first=True)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        """
        Pool graph to single vector using Set2Set.

        Args:
            x: Node features [N, hidden_dim]
            mask: Optional mask [N]

        Returns:
            Pooled vector [hidden_dim * 2]
        """
        N = x.size(0)
        h = torch.zeros(1, 1, self.hidden_dim, device=x.device)
        c = torch.zeros(1, 1, self.hidden_dim, device=x.device)

        q_star = x.new_zeros(self.hidden_dim * 2)

        for _ in range(self.processing_steps):
            # Read
            q = h.squeeze(0).squeeze(0)  # [hidden_dim]

            # Attention
            e = (x * q.unsqueeze(0)).sum(dim=-1)  # [N]
            if mask is not None:
                e = e.masked_fill(~mask, float("-inf"))
            a = F.softmax(e, dim=0)  # [N]

            r = (a.unsqueeze(-1) * x).sum(dim=0)  # [hidden_dim]

            # LSTM step
            lstm_input = torch.cat([q, r]).unsqueeze(0).unsqueeze(0)  # [1, 1, 2*hidden_dim]
            _, (h, c) = self.lstm(lstm_input, (h, c))

            q_star = torch.cat([h.squeeze(0).squeeze(0), r])

        return q_star


class SchedulingGraphEncoder(nn.Module):
    """
    Main encoder that converts scheduling graphs to vector embeddings.

    Architecture:
    1. Node type encoders project different node types to common dimension
    2. GNN layers propagate information across the graph
    3. Pooling layer aggregates node features to graph-level embedding
    4. Output layer produces final embedding
    """

    def __init__(self, config: EncoderConfig = None):
        """
        Initialize scheduling graph encoder.

        Args:
            config: Encoder configuration
        """
        check_torch()
        super().__init__()

        self.config = config or EncoderConfig()

        # Node type encoder
        self.node_encoder = NodeTypeEncoder(
            job_dim=self.config.job_feature_dim,
            op_dim=self.config.operation_feature_dim,
            machine_dim=self.config.machine_feature_dim,
            hidden_dim=self.config.hidden_dim
        )

        # Node type embedding
        self.node_type_embedding = nn.Embedding(3, self.config.hidden_dim)

        # GNN block
        self.gnn = SchedulingGNNBlock(
            hidden_dim=self.config.hidden_dim,
            edge_dim=self.config.edge_feature_dim,
            num_heads=self.config.num_attention_heads,
            num_layers=self.config.num_gnn_layers,
            dropout=self.config.dropout
        )

        # Pooling layer
        if self.config.pooling == "attention":
            self.pooling = AttentionPooling(self.config.hidden_dim)
            pool_output_dim = self.config.hidden_dim
        elif self.config.pooling == "set2set":
            self.pooling = Set2SetPooling(self.config.hidden_dim)
            pool_output_dim = self.config.hidden_dim * 2
        else:
            self.pooling = None  # mean or max
            pool_output_dim = self.config.hidden_dim

        # Type-specific pooling for heterogeneous output
        self.job_pool = AttentionPooling(self.config.hidden_dim)
        self.op_pool = AttentionPooling(self.config.hidden_dim)
        self.machine_pool = AttentionPooling(self.config.hidden_dim)

        # Output layer
        self.output_layer = nn.Sequential(
            nn.Linear(pool_output_dim + self.config.hidden_dim * 3, self.config.output_dim),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(self.config.output_dim, self.config.output_dim)
        )

        self.to(self.config.device)

    def forward(
        self,
        graph_data: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """
        Encode scheduling graph.

        Args:
            graph_data: Dictionary from SchedulingGraph.to_tensors()
                - job_features: [num_jobs, job_dim]
                - operation_features: [num_ops, op_dim]
                - machine_features: [num_machines, machine_dim]
                - edge_index: [2, E]
                - edge_features: [E, edge_dim]
                - edge_types: [E]
                - job_indices, operation_indices, machine_indices

        Returns:
            Dictionary with:
                - embedding: Graph-level embedding [output_dim]
                - node_embeddings: Node embeddings [N, hidden_dim]
                - job_embedding: Pooled job embedding [hidden_dim]
                - op_embedding: Pooled operation embedding [hidden_dim]
                - machine_embedding: Pooled machine embedding [hidden_dim]
        """
        job_features = graph_data["job_features"].to(self.config.device)
        op_features = graph_data["operation_features"].to(self.config.device)
        machine_features = graph_data["machine_features"].to(self.config.device)
        edge_index = graph_data["edge_index"].to(self.config.device)
        edge_features = graph_data["edge_features"].to(self.config.device)

        job_indices = graph_data["job_indices"].to(self.config.device)
        op_indices = graph_data["operation_indices"].to(self.config.device)
        machine_indices = graph_data["machine_indices"].to(self.config.device)

        # Encode node types
        job_h, op_h, machine_h = self.node_encoder(
            job_features, op_features, machine_features
        )

        # Build combined node features
        num_nodes = graph_data["num_jobs"] + graph_data["num_operations"] + graph_data["num_machines"]
        node_features = torch.zeros(num_nodes, self.config.hidden_dim, device=self.config.device)

        # Assign to correct positions
        if len(job_indices) > 0:
            node_features[job_indices] = job_h
        if len(op_indices) > 0:
            node_features[op_indices] = op_h
        if len(machine_indices) > 0:
            node_features[machine_indices] = machine_h

        # Add node type embeddings
        node_types = torch.zeros(num_nodes, dtype=torch.long, device=self.config.device)
        if len(job_indices) > 0:
            node_types[job_indices] = 0
        if len(op_indices) > 0:
            node_types[op_indices] = 1
        if len(machine_indices) > 0:
            node_types[machine_indices] = 2

        node_features = node_features + self.node_type_embedding(node_types)

        # Apply GNN
        node_embeddings = self.gnn(node_features, edge_index, edge_features)

        # Pool by node type
        job_embedding = self.job_pool(node_embeddings[job_indices]) if len(job_indices) > 0 else torch.zeros(self.config.hidden_dim, device=self.config.device)
        op_embedding = self.op_pool(node_embeddings[op_indices]) if len(op_indices) > 0 else torch.zeros(self.config.hidden_dim, device=self.config.device)
        machine_embedding = self.machine_pool(node_embeddings[machine_indices]) if len(machine_indices) > 0 else torch.zeros(self.config.hidden_dim, device=self.config.device)

        # Global pooling
        if self.pooling is not None:
            global_pool = self.pooling(node_embeddings)
        elif self.config.pooling == "mean":
            global_pool = node_embeddings.mean(dim=0)
        else:  # max
            global_pool = node_embeddings.max(dim=0)[0]

        # Combine and produce final embedding
        combined = torch.cat([global_pool, job_embedding, op_embedding, machine_embedding])
        embedding = self.output_layer(combined)

        return {
            "embedding": embedding,
            "node_embeddings": node_embeddings,
            "job_embedding": job_embedding,
            "op_embedding": op_embedding,
            "machine_embedding": machine_embedding
        }

    def encode_graph(self, graph: SchedulingGraph) -> torch.Tensor:
        """
        Convenience method to encode a SchedulingGraph object.

        Args:
            graph: SchedulingGraph instance

        Returns:
            Graph embedding [output_dim]
        """
        graph_data = graph.to_tensors()
        result = self.forward(graph_data)
        return result["embedding"]

    def get_node_embeddings(self, graph: SchedulingGraph) -> Dict[str, torch.Tensor]:
        """
        Get embeddings for each node type.

        Args:
            graph: SchedulingGraph instance

        Returns:
            Dictionary with node embeddings by type
        """
        graph_data = graph.to_tensors()
        result = self.forward(graph_data)

        job_indices = graph_data["job_indices"]
        op_indices = graph_data["operation_indices"]
        machine_indices = graph_data["machine_indices"]

        return {
            "jobs": result["node_embeddings"][job_indices] if len(job_indices) > 0 else None,
            "operations": result["node_embeddings"][op_indices] if len(op_indices) > 0 else None,
            "machines": result["node_embeddings"][machine_indices] if len(machine_indices) > 0 else None
        }


class OperationEncoder(nn.Module):
    """
    Encodes individual operations with context from the graph.

    Used for operation-level predictions (duration, bottleneck probability).
    """

    def __init__(self, config: EncoderConfig = None):
        """
        Initialize operation encoder.

        Args:
            config: Encoder configuration
        """
        check_torch()
        super().__init__()

        self.config = config or EncoderConfig()

        # Shared graph encoder
        self.graph_encoder = SchedulingGraphEncoder(config)

        # Operation-specific layers
        self.op_layers = nn.Sequential(
            nn.Linear(self.config.hidden_dim + self.config.output_dim, self.config.hidden_dim),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(self.config.hidden_dim, self.config.hidden_dim)
        )

    def forward(
        self,
        graph_data: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """
        Encode operations with graph context.

        Args:
            graph_data: Dictionary from SchedulingGraph.to_tensors()

        Returns:
            Operation embeddings [num_ops, hidden_dim]
        """
        # Get graph encoding
        result = self.graph_encoder(graph_data)

        op_indices = graph_data["operation_indices"].to(self.config.device)

        if len(op_indices) == 0:
            return torch.zeros(0, self.config.hidden_dim, device=self.config.device)

        # Get operation node embeddings
        op_embeddings = result["node_embeddings"][op_indices]

        # Concatenate with graph embedding
        graph_embedding = result["embedding"].unsqueeze(0).expand(len(op_indices), -1)
        combined = torch.cat([op_embeddings, graph_embedding], dim=-1)

        # Apply operation-specific layers
        op_features = self.op_layers(combined)

        return op_features


class MachineEncoder(nn.Module):
    """
    Encodes machines with context from the graph.

    Used for machine-level predictions (bottleneck, workload).
    """

    def __init__(self, config: EncoderConfig = None):
        """
        Initialize machine encoder.

        Args:
            config: Encoder configuration
        """
        check_torch()
        super().__init__()

        self.config = config or EncoderConfig()

        # Shared graph encoder
        self.graph_encoder = SchedulingGraphEncoder(config)

        # Machine-specific layers
        self.machine_layers = nn.Sequential(
            nn.Linear(self.config.hidden_dim + self.config.output_dim, self.config.hidden_dim),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(self.config.hidden_dim, self.config.hidden_dim)
        )

    def forward(
        self,
        graph_data: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """
        Encode machines with graph context.

        Args:
            graph_data: Dictionary from SchedulingGraph.to_tensors()

        Returns:
            Machine embeddings [num_machines, hidden_dim]
        """
        # Get graph encoding
        result = self.graph_encoder(graph_data)

        machine_indices = graph_data["machine_indices"].to(self.config.device)

        if len(machine_indices) == 0:
            return torch.zeros(0, self.config.hidden_dim, device=self.config.device)

        # Get machine node embeddings
        machine_embeddings = result["node_embeddings"][machine_indices]

        # Concatenate with graph embedding
        graph_embedding = result["embedding"].unsqueeze(0).expand(len(machine_indices), -1)
        combined = torch.cat([machine_embeddings, graph_embedding], dim=-1)

        # Apply machine-specific layers
        machine_features = self.machine_layers(combined)

        return machine_features


def create_encoder(config: EncoderConfig = None) -> SchedulingGraphEncoder:
    """
    Factory function to create a scheduling graph encoder.

    Args:
        config: Encoder configuration

    Returns:
        SchedulingGraphEncoder instance
    """
    return SchedulingGraphEncoder(config)
