# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Graph Neural Network Layers for Scheduling

Implements GNN layers specialized for scheduling problems:
- Graph Attention Network (GAT) layers
- Graph Convolutional Network (GCN) layers
- Heterogeneous GNN layers for multi-type nodes
- Message passing layers with edge features
"""

import math
from typing import Optional, Tuple
from dataclasses import dataclass

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # Create placeholder classes for when PyTorch is not available
    class nn:
        class Module:
            pass


def check_torch():
    """Check if PyTorch is available."""
    if not TORCH_AVAILABLE:
        raise ImportError(
            "PyTorch is required for GNN layers. "
            "Install with: pip install torch"
        )


@dataclass
class GATLayerConfig:
    """Configuration for GAT layer."""
    in_features: int = 64
    out_features: int = 64
    num_heads: int = 4
    dropout: float = 0.1
    alpha: float = 0.2  # LeakyReLU negative slope
    concat: bool = True  # Concatenate attention heads
    bias: bool = True
    edge_dim: int = 0  # Edge feature dimension (0 = no edge features)


@dataclass
class GCNLayerConfig:
    """Configuration for GCN layer."""
    in_features: int = 64
    out_features: int = 64
    bias: bool = True
    normalize: bool = True
    add_self_loops: bool = True


class GraphAttentionLayer(nn.Module):
    """
    Graph Attention Layer (GAT).

    Implements attention mechanism over graph neighbors as described in:
    "Graph Attention Networks" (Velickovic et al., 2018)

    Features:
    - Multi-head attention
    - Optional edge features
    - LeakyReLU activation
    """

    def __init__(self, config: GATLayerConfig = None):
        """
        Initialize GAT layer.

        Args:
            config: Layer configuration
        """
        check_torch()
        super().__init__()

        self.config = config or GATLayerConfig()
        self.in_features = self.config.in_features
        self.out_features = self.config.out_features
        self.num_heads = self.config.num_heads
        self.concat = self.config.concat
        self.dropout = self.config.dropout
        self.alpha = self.config.alpha
        self.edge_dim = self.config.edge_dim

        # Linear transformations for each head
        self.W = nn.Parameter(
            torch.zeros(self.num_heads, self.in_features, self.out_features)
        )
        self.a_src = nn.Parameter(
            torch.zeros(self.num_heads, self.out_features, 1)
        )
        self.a_dst = nn.Parameter(
            torch.zeros(self.num_heads, self.out_features, 1)
        )

        # Edge features
        if self.edge_dim > 0:
            self.edge_lin = nn.Linear(self.edge_dim, self.num_heads)

        if self.config.bias:
            if self.concat:
                self.bias = nn.Parameter(
                    torch.zeros(self.num_heads * self.out_features)
                )
            else:
                self.bias = nn.Parameter(torch.zeros(self.out_features))
        else:
            self.register_parameter("bias", None)

        self.leaky_relu = nn.LeakyReLU(self.alpha)
        self.dropout_layer = nn.Dropout(self.dropout)

        self._reset_parameters()

    def _reset_parameters(self):
        """Initialize parameters."""
        nn.init.xavier_uniform_(self.W)
        nn.init.xavier_uniform_(self.a_src)
        nn.init.xavier_uniform_(self.a_dst)
        if self.bias is not None:
            nn.init.zeros_(self.bias)

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Node features [N, in_features]
            edge_index: Edge indices [2, E]
            edge_attr: Edge features [E, edge_dim] (optional)

        Returns:
            Updated node features [N, num_heads * out_features] if concat
            else [N, out_features]
        """
        N = x.size(0)

        # Linear transformation: [N, heads, out_features]
        h = torch.einsum("ni,hio->nho", x, self.W)

        # Compute attention scores
        # Source and target attention: [N, heads, 1]
        attn_src = torch.einsum("nho,hoi->nhi", h, self.a_src)
        attn_dst = torch.einsum("nho,hoi->nhi", h, self.a_dst)

        # Get source and target indices
        src, dst = edge_index[0], edge_index[1]

        # Compute edge attention: [E, heads]
        edge_attn = attn_src[src].squeeze(-1) + attn_dst[dst].squeeze(-1)

        # Add edge features if available
        if edge_attr is not None and self.edge_dim > 0:
            edge_attn = edge_attn + self.edge_lin(edge_attr)

        # Apply LeakyReLU
        edge_attn = self.leaky_relu(edge_attn)

        # Softmax over neighbors
        edge_attn = self._sparse_softmax(edge_attn, dst, N)

        # Apply dropout
        edge_attn = self.dropout_layer(edge_attn)

        # Aggregate messages
        # h_src: [E, heads, out_features]
        h_src = h[src]

        # Weighted messages: [E, heads, out_features]
        messages = h_src * edge_attn.unsqueeze(-1)

        # Aggregate to target nodes: [N, heads, out_features]
        out = torch.zeros(N, self.num_heads, self.out_features, device=x.device)
        out.scatter_add_(0, dst.view(-1, 1, 1).expand_as(messages), messages)

        # Reshape output
        if self.concat:
            out = out.view(N, self.num_heads * self.out_features)
        else:
            out = out.mean(dim=1)

        # Add bias
        if self.bias is not None:
            out = out + self.bias

        return out

    def _sparse_softmax(
        self,
        edge_attn: torch.Tensor,
        index: torch.Tensor,
        num_nodes: int
    ) -> torch.Tensor:
        """Compute softmax over neighbors."""
        # Subtract max for numerical stability
        max_val = torch.zeros(num_nodes, edge_attn.size(1), device=edge_attn.device)
        max_val.scatter_reduce_(0, index.view(-1, 1).expand_as(edge_attn),
                                 edge_attn, reduce="amax", include_self=False)
        edge_attn = edge_attn - max_val[index]

        # Exp and sum
        edge_attn = torch.exp(edge_attn)
        sum_val = torch.zeros(num_nodes, edge_attn.size(1), device=edge_attn.device)
        sum_val.scatter_add_(0, index.view(-1, 1).expand_as(edge_attn), edge_attn)

        # Normalize
        return edge_attn / (sum_val[index] + 1e-8)


class GraphConvLayer(nn.Module):
    """
    Graph Convolutional Layer (GCN).

    Implements the layer as described in:
    "Semi-Supervised Classification with Graph Convolutional Networks"
    (Kipf & Welling, 2017)
    """

    def __init__(self, config: GCNLayerConfig = None):
        """
        Initialize GCN layer.

        Args:
            config: Layer configuration
        """
        check_torch()
        super().__init__()

        self.config = config or GCNLayerConfig()
        self.in_features = self.config.in_features
        self.out_features = self.config.out_features
        self.normalize = self.config.normalize
        self.add_self_loops = self.config.add_self_loops

        self.weight = nn.Parameter(
            torch.zeros(self.in_features, self.out_features)
        )

        if self.config.bias:
            self.bias = nn.Parameter(torch.zeros(self.out_features))
        else:
            self.register_parameter("bias", None)

        self._reset_parameters()

    def _reset_parameters(self):
        """Initialize parameters."""
        nn.init.xavier_uniform_(self.weight)
        if self.bias is not None:
            nn.init.zeros_(self.bias)

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_weight: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Node features [N, in_features]
            edge_index: Edge indices [2, E]
            edge_weight: Edge weights [E] (optional)

        Returns:
            Updated node features [N, out_features]
        """
        N = x.size(0)
        src, dst = edge_index[0], edge_index[1]

        # Add self-loops
        if self.add_self_loops:
            self_loop_idx = torch.arange(N, device=edge_index.device)
            src = torch.cat([src, self_loop_idx])
            dst = torch.cat([dst, self_loop_idx])
            if edge_weight is not None:
                edge_weight = torch.cat([
                    edge_weight,
                    torch.ones(N, device=edge_weight.device)
                ])

        # Compute degree normalization
        if self.normalize:
            deg = torch.zeros(N, device=x.device)
            if edge_weight is not None:
                deg.scatter_add_(0, dst, edge_weight)
            else:
                ones = torch.ones(len(dst), device=x.device)
                deg.scatter_add_(0, dst, ones)

            deg_inv_sqrt = deg.pow(-0.5)
            deg_inv_sqrt[deg_inv_sqrt == float("inf")] = 0

            # Symmetric normalization: D^{-1/2} A D^{-1/2}
            norm = deg_inv_sqrt[src] * deg_inv_sqrt[dst]
            if edge_weight is not None:
                norm = norm * edge_weight
        else:
            norm = edge_weight if edge_weight is not None else torch.ones(len(dst), device=x.device)

        # Transform features
        h = x @ self.weight

        # Aggregate messages
        out = torch.zeros_like(h)
        out.scatter_add_(0, dst.view(-1, 1).expand(-1, h.size(1)), h[src] * norm.view(-1, 1))

        # Add bias
        if self.bias is not None:
            out = out + self.bias

        return out


class MessagePassingLayer(nn.Module):
    """
    General Message Passing Layer with edge features.

    Implements: h_i' = UPDATE(h_i, AGG({MESSAGE(h_i, h_j, e_ij)}))
    """

    def __init__(
        self,
        node_dim: int,
        edge_dim: int,
        hidden_dim: int = 64,
        aggr: str = "mean"
    ):
        """
        Initialize message passing layer.

        Args:
            node_dim: Node feature dimension
            edge_dim: Edge feature dimension
            hidden_dim: Hidden layer dimension
            aggr: Aggregation method (mean, sum, max)
        """
        check_torch()
        super().__init__()

        self.aggr = aggr

        # Message function: MLP(h_i || h_j || e_ij)
        self.message_mlp = nn.Sequential(
            nn.Linear(node_dim * 2 + edge_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        # Update function: MLP(h_i || aggregated_messages)
        self.update_mlp = nn.Sequential(
            nn.Linear(node_dim + hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, node_dim)
        )

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: torch.Tensor
    ) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Node features [N, node_dim]
            edge_index: Edge indices [2, E]
            edge_attr: Edge features [E, edge_dim]

        Returns:
            Updated node features [N, node_dim]
        """
        N = x.size(0)
        src, dst = edge_index[0], edge_index[1]

        # Compute messages
        x_src = x[src]
        x_dst = x[dst]
        messages = self.message_mlp(torch.cat([x_src, x_dst, edge_attr], dim=-1))

        # Aggregate messages
        aggr_out = torch.zeros(N, messages.size(1), device=x.device)

        if self.aggr == "mean":
            aggr_out.scatter_add_(0, dst.view(-1, 1).expand_as(messages), messages)
            count = torch.zeros(N, device=x.device)
            count.scatter_add_(0, dst, torch.ones(len(dst), device=x.device))
            aggr_out = aggr_out / (count.view(-1, 1) + 1e-8)
        elif self.aggr == "sum":
            aggr_out.scatter_add_(0, dst.view(-1, 1).expand_as(messages), messages)
        elif self.aggr == "max":
            aggr_out.scatter_reduce_(0, dst.view(-1, 1).expand_as(messages),
                                      messages, reduce="amax", include_self=False)

        # Update node features
        out = self.update_mlp(torch.cat([x, aggr_out], dim=-1))

        return out


class HeterogeneousGNNLayer(nn.Module):
    """
    Heterogeneous GNN Layer for multi-type nodes and edges.

    Handles different node types (jobs, operations, machines) and
    edge types (precedence, assignment, capability).
    """

    def __init__(
        self,
        node_dims: dict,
        edge_dim: int,
        hidden_dim: int = 64,
        num_heads: int = 4
    ):
        """
        Initialize heterogeneous GNN layer.

        Args:
            node_dims: Dict mapping node type to feature dimension
            edge_dim: Edge feature dimension
            hidden_dim: Hidden dimension for all types
            num_heads: Number of attention heads
        """
        check_torch()
        super().__init__()

        self.node_dims = node_dims
        self.hidden_dim = hidden_dim

        # Projection layers for each node type
        self.projections = nn.ModuleDict({
            node_type: nn.Linear(dim, hidden_dim)
            for node_type, dim in node_dims.items()
        })

        # GAT layer for heterogeneous graph
        gat_config = GATLayerConfig(
            in_features=hidden_dim,
            out_features=hidden_dim // num_heads,
            num_heads=num_heads,
            edge_dim=edge_dim
        )
        self.gat = GraphAttentionLayer(gat_config)

        # Output projections for each node type
        self.out_projections = nn.ModuleDict({
            node_type: nn.Linear(hidden_dim, hidden_dim)
            for node_type in node_dims.keys()
        })

    def forward(
        self,
        x_dict: dict,
        edge_index: torch.Tensor,
        edge_attr: torch.Tensor,
        node_type_tensor: torch.Tensor
    ) -> dict:
        """
        Forward pass.

        Args:
            x_dict: Dict mapping node type to features
            edge_index: Edge indices [2, E]
            edge_attr: Edge features [E, edge_dim]
            node_type_tensor: Node type for each node [N]

        Returns:
            Dict mapping node type to updated features
        """
        # Project all nodes to common dimension
        x_list = []
        node_type_indices = {}
        offset = 0

        for node_type, x in x_dict.items():
            x_proj = self.projections[node_type](x)
            x_list.append(x_proj)
            node_type_indices[node_type] = (offset, offset + x.size(0))
            offset += x.size(0)

        x_all = torch.cat(x_list, dim=0)

        # Apply GAT
        x_all = self.gat(x_all, edge_index, edge_attr)

        # Split back to node types and apply output projection
        out_dict = {}
        for node_type, (start, end) in node_type_indices.items():
            out_dict[node_type] = self.out_projections[node_type](x_all[start:end])

        return out_dict


class SchedulingGNNBlock(nn.Module):
    """
    GNN block specialized for scheduling problems.

    Combines multiple layers with residual connections and layer normalization.
    """

    def __init__(
        self,
        hidden_dim: int = 64,
        edge_dim: int = 8,
        num_heads: int = 4,
        num_layers: int = 3,
        dropout: float = 0.1
    ):
        """
        Initialize scheduling GNN block.

        Args:
            hidden_dim: Hidden dimension
            edge_dim: Edge feature dimension
            num_heads: Number of attention heads
            num_layers: Number of GNN layers
            dropout: Dropout rate
        """
        check_torch()
        super().__init__()

        self.num_layers = num_layers

        # GAT layers
        self.gat_layers = nn.ModuleList()
        for i in range(num_layers):
            gat_config = GATLayerConfig(
                in_features=hidden_dim,
                out_features=hidden_dim // num_heads,
                num_heads=num_heads,
                dropout=dropout,
                edge_dim=edge_dim,
                concat=True
            )
            self.gat_layers.append(GraphAttentionLayer(gat_config))

        # Layer normalization
        self.layer_norms = nn.ModuleList([
            nn.LayerNorm(hidden_dim) for _ in range(num_layers)
        ])

        # Dropout
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Forward pass with residual connections.

        Args:
            x: Node features [N, hidden_dim]
            edge_index: Edge indices [2, E]
            edge_attr: Edge features [E, edge_dim]

        Returns:
            Updated node features [N, hidden_dim]
        """
        for i in range(self.num_layers):
            # GAT layer
            h = self.gat_layers[i](x, edge_index, edge_attr)

            # Residual connection
            h = h + x

            # Layer normalization
            h = self.layer_norms[i](h)

            # Dropout (except last layer)
            if i < self.num_layers - 1:
                h = self.dropout(F.relu(h))

            x = h

        return x
