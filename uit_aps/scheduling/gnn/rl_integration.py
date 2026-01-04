# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
GNN-RL Integration Module

Integrates GNN encodings with RL agents for enhanced decision making.
The GNN provides structural understanding of the scheduling problem,
while the RL agent makes sequential decisions.
"""

from dataclasses import dataclass
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

from uit_aps.scheduling.gnn.graph import SchedulingGraph, build_graph_from_schedule
from uit_aps.scheduling.gnn.encoder import SchedulingGraphEncoder, EncoderConfig


def check_torch():
    """Check if PyTorch is available."""
    if not TORCH_AVAILABLE:
        raise ImportError(
            "PyTorch is required for GNN-RL integration. "
            "Install with: pip install torch"
        )


@dataclass
class GNNRLConfig:
    """Configuration for GNN-RL integration."""
    # GNN encoder settings
    gnn_hidden_dim: int = 128
    gnn_output_dim: int = 256
    gnn_num_layers: int = 3
    gnn_num_heads: int = 4

    # RL integration settings
    use_gnn_state: bool = True
    gnn_state_weight: float = 0.5  # Weight for GNN features in combined state
    update_gnn_frequency: int = 10  # Steps between GNN updates

    # Device
    device: str = "cpu"


class GNNStateEncoder(nn.Module):
    """
    Encodes scheduling state using GNN for RL agent.

    Provides a more structured representation of the scheduling problem
    compared to flat state vectors.
    """

    def __init__(self, config: GNNRLConfig = None):
        """
        Initialize GNN state encoder.

        Args:
            config: Configuration
        """
        check_torch()
        super().__init__()

        self.config = config or GNNRLConfig()

        # GNN encoder
        encoder_config = EncoderConfig(
            hidden_dim=self.config.gnn_hidden_dim,
            output_dim=self.config.gnn_output_dim,
            num_gnn_layers=self.config.gnn_num_layers,
            num_attention_heads=self.config.gnn_num_heads,
            device=self.config.device
        )
        self.gnn_encoder = SchedulingGraphEncoder(encoder_config)

        # Cache for efficiency
        self._cached_graph = None
        self._cached_embedding = None
        self._step_counter = 0

        self.to(self.config.device)

    def encode(
        self,
        schedule: List[Dict],
        machines: List[Dict],
        force_update: bool = False
    ) -> torch.Tensor:
        """
        Encode current scheduling state.

        Args:
            schedule: List of operation dictionaries
            machines: List of machine dictionaries
            force_update: Force GNN update even if cached

        Returns:
            State embedding [output_dim]
        """
        self._step_counter += 1

        # Check if we need to update GNN encoding
        should_update = (
            force_update or
            self._cached_embedding is None or
            self._step_counter % self.config.update_gnn_frequency == 0
        )

        if should_update:
            # Build graph
            graph = build_graph_from_schedule(schedule, machines)
            graph_data = graph.to_tensors()

            # Encode
            with torch.no_grad():
                result = self.gnn_encoder(graph_data)
                self._cached_embedding = result["embedding"]
                self._cached_graph = graph

        return self._cached_embedding

    def get_operation_embeddings(
        self,
        schedule: List[Dict],
        machines: List[Dict]
    ) -> torch.Tensor:
        """
        Get embeddings for each operation.

        Args:
            schedule: List of operation dictionaries
            machines: List of machine dictionaries

        Returns:
            Operation embeddings [num_ops, hidden_dim]
        """
        graph = build_graph_from_schedule(schedule, machines)
        embeddings = self.gnn_encoder.get_node_embeddings(graph)
        return embeddings.get("operations")

    def get_machine_embeddings(
        self,
        schedule: List[Dict],
        machines: List[Dict]
    ) -> torch.Tensor:
        """
        Get embeddings for each machine.

        Args:
            schedule: List of operation dictionaries
            machines: List of machine dictionaries

        Returns:
            Machine embeddings [num_machines, hidden_dim]
        """
        graph = build_graph_from_schedule(schedule, machines)
        embeddings = self.gnn_encoder.get_node_embeddings(graph)
        return embeddings.get("machines")

    def reset_cache(self):
        """Reset cached embeddings."""
        self._cached_graph = None
        self._cached_embedding = None
        self._step_counter = 0


class GNNEnhancedStateEncoder(nn.Module):
    """
    Combines flat state representation with GNN embeddings.

    Provides a richer state representation for RL agents by:
    1. Encoding the flat state (from RL environment)
    2. Encoding the graph structure (via GNN)
    3. Combining both representations
    """

    def __init__(
        self,
        flat_state_dim: int,
        output_dim: int,
        config: GNNRLConfig = None
    ):
        """
        Initialize enhanced state encoder.

        Args:
            flat_state_dim: Dimension of flat state vector
            output_dim: Output dimension
            config: Configuration
        """
        check_torch()
        super().__init__()

        self.config = config or GNNRLConfig()
        self.flat_state_dim = flat_state_dim
        self.output_dim = output_dim

        # GNN encoder
        self.gnn_encoder = GNNStateEncoder(config)

        # Flat state encoder
        self.flat_encoder = nn.Sequential(
            nn.Linear(flat_state_dim, self.config.gnn_hidden_dim),
            nn.ReLU(),
            nn.Linear(self.config.gnn_hidden_dim, self.config.gnn_output_dim)
        )

        # Combiner
        combined_dim = self.config.gnn_output_dim * 2
        self.combiner = nn.Sequential(
            nn.Linear(combined_dim, output_dim),
            nn.ReLU(),
            nn.Linear(output_dim, output_dim)
        )

        # Attention for combining
        self.attention = nn.Sequential(
            nn.Linear(combined_dim, 2),
            nn.Softmax(dim=-1)
        )

        self.to(self.config.device)

    def forward(
        self,
        flat_state: torch.Tensor,
        schedule: List[Dict],
        machines: List[Dict]
    ) -> torch.Tensor:
        """
        Encode state using both flat and GNN representations.

        Args:
            flat_state: Flat state vector [flat_state_dim]
            schedule: List of operation dictionaries
            machines: List of machine dictionaries

        Returns:
            Combined state embedding [output_dim]
        """
        # Encode flat state
        flat_embedding = self.flat_encoder(flat_state.to(self.config.device))

        # Encode graph state
        if self.config.use_gnn_state:
            gnn_embedding = self.gnn_encoder.encode(schedule, machines)
        else:
            gnn_embedding = torch.zeros_like(flat_embedding)

        # Combine with attention
        combined = torch.cat([flat_embedding, gnn_embedding], dim=-1)

        if self.config.use_gnn_state:
            # Learn attention weights
            weights = self.attention(combined)
            weighted_flat = flat_embedding * weights[0]
            weighted_gnn = gnn_embedding * weights[1]
            attended = torch.cat([weighted_flat, weighted_gnn], dim=-1)
        else:
            attended = combined

        # Final combination
        output = self.combiner(attended)

        return output


class GNNEnhancedPolicy(nn.Module):
    """
    Policy network enhanced with GNN state encoding.

    Uses GNN embeddings to make more informed action decisions.
    """

    def __init__(
        self,
        flat_state_dim: int,
        action_dim: int,
        config: GNNRLConfig = None
    ):
        """
        Initialize GNN-enhanced policy.

        Args:
            flat_state_dim: Dimension of flat state
            action_dim: Number of actions
            config: Configuration
        """
        check_torch()
        super().__init__()

        self.config = config or GNNRLConfig()

        # State encoder
        self.state_encoder = GNNEnhancedStateEncoder(
            flat_state_dim=flat_state_dim,
            output_dim=self.config.gnn_hidden_dim,
            config=config
        )

        # Policy network
        self.policy = nn.Sequential(
            nn.Linear(self.config.gnn_hidden_dim, self.config.gnn_hidden_dim),
            nn.ReLU(),
            nn.Linear(self.config.gnn_hidden_dim, action_dim)
        )

        # Value network (for actor-critic)
        self.value = nn.Sequential(
            nn.Linear(self.config.gnn_hidden_dim, self.config.gnn_hidden_dim),
            nn.ReLU(),
            nn.Linear(self.config.gnn_hidden_dim, 1)
        )

        self.to(self.config.device)

    def forward(
        self,
        flat_state: torch.Tensor,
        schedule: List[Dict],
        machines: List[Dict]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Get action logits and value estimate.

        Args:
            flat_state: Flat state vector
            schedule: List of operation dictionaries
            machines: List of machine dictionaries

        Returns:
            Tuple of (action_logits, value)
        """
        # Encode state
        state_embedding = self.state_encoder(flat_state, schedule, machines)

        # Get action logits and value
        action_logits = self.policy(state_embedding)
        value = self.value(state_embedding)

        return action_logits, value

    def get_action(
        self,
        flat_state: torch.Tensor,
        schedule: List[Dict],
        machines: List[Dict],
        deterministic: bool = False
    ) -> Tuple[int, torch.Tensor]:
        """
        Sample action from policy.

        Args:
            flat_state: Flat state vector
            schedule: List of operation dictionaries
            machines: List of machine dictionaries
            deterministic: If True, return argmax action

        Returns:
            Tuple of (action, log_prob)
        """
        action_logits, _ = self.forward(flat_state, schedule, machines)
        probs = F.softmax(action_logits, dim=-1)

        if deterministic:
            action = probs.argmax().item()
            log_prob = torch.log(probs[action])
        else:
            dist = torch.distributions.Categorical(probs)
            action = dist.sample().item()
            log_prob = dist.log_prob(torch.tensor(action))

        return action, log_prob


class GNNActionSelector(nn.Module):
    """
    Uses GNN embeddings to select actions for specific operations/machines.

    Provides operation-aware and machine-aware action selection.
    """

    def __init__(self, config: GNNRLConfig = None):
        """
        Initialize GNN action selector.

        Args:
            config: Configuration
        """
        check_torch()
        super().__init__()

        self.config = config or GNNRLConfig()

        # GNN encoder
        encoder_config = EncoderConfig(
            hidden_dim=self.config.gnn_hidden_dim,
            output_dim=self.config.gnn_output_dim,
            num_gnn_layers=self.config.gnn_num_layers,
            num_attention_heads=self.config.gnn_num_heads,
            device=self.config.device
        )
        self.gnn_encoder = SchedulingGraphEncoder(encoder_config)

        # Operation selector: which operation to act on
        self.operation_selector = nn.Sequential(
            nn.Linear(self.config.gnn_hidden_dim, self.config.gnn_hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(self.config.gnn_hidden_dim // 2, 1)
        )

        # Machine selector: which machine to reassign to
        self.machine_selector = nn.Sequential(
            nn.Linear(self.config.gnn_hidden_dim * 2, self.config.gnn_hidden_dim),
            nn.ReLU(),
            nn.Linear(self.config.gnn_hidden_dim, 1)
        )

        self.to(self.config.device)

    def select_operation(
        self,
        schedule: List[Dict],
        machines: List[Dict],
        mask: torch.Tensor = None
    ) -> Tuple[int, float]:
        """
        Select which operation to act on.

        Args:
            schedule: List of operation dictionaries
            machines: List of machine dictionaries
            mask: Optional mask for invalid operations

        Returns:
            Tuple of (operation_index, confidence)
        """
        # Build graph and get embeddings
        graph = build_graph_from_schedule(schedule, machines)
        graph_data = graph.to_tensors()

        with torch.no_grad():
            result = self.gnn_encoder(graph_data)

        op_indices = graph_data["operation_indices"].to(self.config.device)

        if len(op_indices) == 0:
            return 0, 0.0

        op_embeddings = result["node_embeddings"][op_indices]

        # Score each operation
        scores = self.operation_selector(op_embeddings).squeeze(-1)

        if mask is not None:
            scores = scores.masked_fill(~mask, float("-inf"))

        probs = F.softmax(scores, dim=0)
        selected_idx = probs.argmax().item()
        confidence = probs[selected_idx].item()

        return selected_idx, confidence

    def select_machine(
        self,
        schedule: List[Dict],
        machines: List[Dict],
        operation_idx: int,
        mask: torch.Tensor = None
    ) -> Tuple[int, float]:
        """
        Select which machine to reassign operation to.

        Args:
            schedule: List of operation dictionaries
            machines: List of machine dictionaries
            operation_idx: Index of operation to reassign
            mask: Optional mask for invalid machines

        Returns:
            Tuple of (machine_index, confidence)
        """
        # Build graph and get embeddings
        graph = build_graph_from_schedule(schedule, machines)
        graph_data = graph.to_tensors()

        with torch.no_grad():
            result = self.gnn_encoder(graph_data)

        op_indices = graph_data["operation_indices"].to(self.config.device)
        machine_indices = graph_data["machine_indices"].to(self.config.device)

        if len(machine_indices) == 0:
            return 0, 0.0

        # Get operation embedding
        op_embedding = result["node_embeddings"][op_indices[operation_idx]]

        # Get machine embeddings
        machine_embeddings = result["node_embeddings"][machine_indices]

        # Combine operation embedding with each machine
        op_expanded = op_embedding.unsqueeze(0).expand(len(machine_indices), -1)
        combined = torch.cat([op_expanded, machine_embeddings], dim=-1)

        # Score each machine
        scores = self.machine_selector(combined).squeeze(-1)

        if mask is not None:
            scores = scores.masked_fill(~mask, float("-inf"))

        probs = F.softmax(scores, dim=0)
        selected_idx = probs.argmax().item()
        confidence = probs[selected_idx].item()

        return selected_idx, confidence


def create_gnn_enhanced_policy(
    flat_state_dim: int,
    action_dim: int,
    config: GNNRLConfig = None
) -> GNNEnhancedPolicy:
    """
    Factory function to create GNN-enhanced policy.

    Args:
        flat_state_dim: Dimension of flat state
        action_dim: Number of actions
        config: Configuration

    Returns:
        GNNEnhancedPolicy instance
    """
    return GNNEnhancedPolicy(flat_state_dim, action_dim, config)


def create_gnn_state_encoder(config: GNNRLConfig = None) -> GNNStateEncoder:
    """
    Factory function to create GNN state encoder.

    Args:
        config: Configuration

    Returns:
        GNNStateEncoder instance
    """
    return GNNStateEncoder(config)
