# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Proximal Policy Optimization (PPO) Agent for Scheduling

Implements PPO algorithm for real-time scheduling adjustments.
PPO is an on-policy algorithm that uses clipped surrogate objective
for stable policy updates.

Reference: Schulman et al. "Proximal Policy Optimization Algorithms" (2017)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import os
import json

from uit_aps.scheduling.rl.agents.base import (
    BaseAgent, AgentConfig, RolloutBuffer, compute_gae, normalize
)


def safe_import_torch():
    """Safely import PyTorch with error handling."""
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
        import torch.nn.functional as F
        from torch.distributions import Categorical
        return torch, nn, optim, F, Categorical, None
    except ImportError as e:
        return None, None, None, None, None, str(e)


@dataclass
class PPOConfig(AgentConfig):
    """Configuration for PPO agent."""
    # PPO specific
    clip_epsilon: float = 0.2
    value_loss_coef: float = 0.5
    entropy_coef: float = 0.01
    max_grad_norm: float = 0.5

    # Training
    n_epochs: int = 10
    n_steps: int = 2048
    gae_lambda: float = 0.95

    # Network
    hidden_sizes: List[int] = field(default_factory=lambda: [256, 256])
    shared_network: bool = True

    # Action space
    num_action_types: int = 7
    max_operations: int = 100
    max_machines: int = 20


class PPOAgent(BaseAgent):
    """
    PPO Agent for real-time scheduling adjustments.

    The agent learns a policy that maps scheduling states to actions.
    Actions include reassigning machines, rescheduling operations,
    and adjusting priorities.

    Architecture:
    - Actor network: outputs action probabilities
    - Critic network: estimates state value
    - Shared feature extractor (optional)
    """

    def __init__(
        self,
        obs_dim: int,
        action_dim: int,
        config: PPOConfig = None
    ):
        """
        Initialize PPO agent.

        Args:
            obs_dim: Observation space dimension
            action_dim: Action space dimension
            config: PPO configuration
        """
        super().__init__(obs_dim, action_dim, config or PPOConfig())

        # Import PyTorch
        torch, nn, optim, F, Categorical, error = safe_import_torch()
        if torch is None:
            raise ImportError(
                f"PyTorch not installed. Please run: pip install torch\n"
                f"Error: {error}"
            )

        self.torch = torch
        self.nn = nn
        self.optim = optim
        self.F = F
        self.Categorical = Categorical

        self.device = torch.device(self.config.device)

        # Build networks
        self._build_networks()

        # Rollout buffer
        self.buffer = RolloutBuffer()

        # Training state
        self.update_count = 0

    def _build_networks(self):
        """Build actor and critic networks."""
        nn = self.nn
        torch = self.torch

        config = self.config
        hidden_sizes = config.hidden_sizes

        # Shared feature extractor
        if config.shared_network:
            layers = []
            prev_size = self.obs_dim
            for hidden_size in hidden_sizes[:-1]:
                layers.append(nn.Linear(prev_size, hidden_size))
                layers.append(nn.ReLU())
                prev_size = hidden_size

            self.feature_extractor = nn.Sequential(*layers).to(self.device)
            feature_dim = hidden_sizes[-2] if len(hidden_sizes) > 1 else self.obs_dim
        else:
            self.feature_extractor = None
            feature_dim = self.obs_dim

        # Actor heads (one for each action component)
        self.action_type_head = nn.Sequential(
            nn.Linear(feature_dim, hidden_sizes[-1]),
            nn.ReLU(),
            nn.Linear(hidden_sizes[-1], config.num_action_types)
        ).to(self.device)

        self.operation_head = nn.Sequential(
            nn.Linear(feature_dim, hidden_sizes[-1]),
            nn.ReLU(),
            nn.Linear(hidden_sizes[-1], config.max_operations)
        ).to(self.device)

        self.machine_head = nn.Sequential(
            nn.Linear(feature_dim, hidden_sizes[-1]),
            nn.ReLU(),
            nn.Linear(hidden_sizes[-1], config.max_machines)
        ).to(self.device)

        # Critic head
        self.critic = nn.Sequential(
            nn.Linear(feature_dim, hidden_sizes[-1]),
            nn.ReLU(),
            nn.Linear(hidden_sizes[-1], 1)
        ).to(self.device)

        # Optimizer
        params = []
        if self.feature_extractor:
            params.extend(self.feature_extractor.parameters())
        params.extend(self.action_type_head.parameters())
        params.extend(self.operation_head.parameters())
        params.extend(self.machine_head.parameters())
        params.extend(self.critic.parameters())

        self.optimizer = self.optim.Adam(params, lr=config.learning_rate)

    def _get_features(self, state: np.ndarray) -> "torch.Tensor":
        """Extract features from state."""
        torch = self.torch

        if isinstance(state, np.ndarray):
            state = torch.FloatTensor(state).to(self.device)

        if state.dim() == 1:
            state = state.unsqueeze(0)

        if self.feature_extractor:
            return self.feature_extractor(state)
        return state

    def _get_action_probs(
        self,
        features: "torch.Tensor"
    ) -> Tuple["torch.Tensor", "torch.Tensor", "torch.Tensor"]:
        """Get action probabilities from features."""
        F = self.F

        action_type_logits = self.action_type_head(features)
        operation_logits = self.operation_head(features)
        machine_logits = self.machine_head(features)

        action_type_probs = F.softmax(action_type_logits, dim=-1)
        operation_probs = F.softmax(operation_logits, dim=-1)
        machine_probs = F.softmax(machine_logits, dim=-1)

        return action_type_probs, operation_probs, machine_probs

    def _get_value(self, features: "torch.Tensor") -> "torch.Tensor":
        """Get value estimate from features."""
        return self.critic(features)

    def select_action(
        self,
        state: np.ndarray,
        valid_actions: List[Tuple[int, int, int]] = None,
        deterministic: bool = False
    ) -> Tuple[Tuple[int, int, int], Dict[str, Any]]:
        """
        Select action given current state.

        Args:
            state: Current observation
            valid_actions: List of valid actions (optional)
            deterministic: Whether to act deterministically

        Returns:
            Tuple of (action, info_dict)
        """
        torch = self.torch
        Categorical = self.Categorical

        with torch.no_grad():
            features = self._get_features(state)
            action_type_probs, operation_probs, machine_probs = self._get_action_probs(features)
            value = self._get_value(features)

            if deterministic:
                action_type = action_type_probs.argmax(dim=-1).item()
                operation_idx = operation_probs.argmax(dim=-1).item()
                machine_idx = machine_probs.argmax(dim=-1).item()
                log_prob = 0.0
            else:
                # Sample from distributions
                action_type_dist = Categorical(action_type_probs)
                operation_dist = Categorical(operation_probs)
                machine_dist = Categorical(machine_probs)

                action_type = action_type_dist.sample().item()
                operation_idx = operation_dist.sample().item()
                machine_idx = machine_dist.sample().item()

                # Calculate log probability
                log_prob = (
                    action_type_dist.log_prob(torch.tensor(action_type)) +
                    operation_dist.log_prob(torch.tensor(operation_idx)) +
                    machine_dist.log_prob(torch.tensor(machine_idx))
                ).item()

            # Apply valid action mask if provided
            if valid_actions and not deterministic:
                # Filter to valid actions
                valid_types = set(a[0] for a in valid_actions)
                valid_ops = set(a[1] for a in valid_actions)
                valid_machines = set(a[2] for a in valid_actions)

                if action_type not in valid_types:
                    action_type = list(valid_types)[0] if valid_types else 0
                if operation_idx not in valid_ops:
                    operation_idx = list(valid_ops)[0] if valid_ops else 0
                if machine_idx not in valid_machines:
                    machine_idx = list(valid_machines)[0] if valid_machines else 0

        action = (action_type, operation_idx, machine_idx)

        info = {
            "value": value.item(),
            "log_prob": log_prob,
            "action_type_probs": action_type_probs.cpu().numpy().flatten(),
            "operation_probs": operation_probs.cpu().numpy().flatten()[:10],  # First 10
            "machine_probs": machine_probs.cpu().numpy().flatten()[:5]  # First 5
        }

        self.step_count += 1

        return action, info

    def store_transition(
        self,
        state: np.ndarray,
        action: Tuple[int, int, int],
        reward: float,
        value: float,
        log_prob: float,
        done: bool
    ):
        """
        Store transition in rollout buffer.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            value: Value estimate
            log_prob: Log probability of action
            done: Whether episode ended
        """
        self.buffer.push(state, action, reward, value, log_prob, done)

    def update(self, batch: Dict[str, np.ndarray] = None) -> Dict[str, float]:
        """
        Update policy using PPO algorithm.

        Args:
            batch: Optional batch (if None, uses rollout buffer)

        Returns:
            Dictionary with training metrics
        """
        torch = self.torch
        Categorical = self.Categorical

        if batch is None:
            batch = self.buffer.get()

        if len(batch["states"]) == 0:
            return {}

        # Convert to tensors
        states = torch.FloatTensor(batch["states"]).to(self.device)
        actions = torch.LongTensor(batch["actions"]).to(self.device)
        old_log_probs = torch.FloatTensor(batch["log_probs"]).to(self.device)
        rewards = batch["rewards"]
        values = batch["values"]
        dones = batch["dones"]

        # Compute advantages and returns
        advantages, returns = compute_gae(
            rewards, values, dones,
            self.config.gamma, self.config.gae_lambda
        )

        advantages = torch.FloatTensor(normalize(advantages)).to(self.device)
        returns = torch.FloatTensor(returns).to(self.device)

        # PPO update epochs
        metrics = {
            "policy_loss": 0.0,
            "value_loss": 0.0,
            "entropy": 0.0,
            "approx_kl": 0.0,
            "clip_fraction": 0.0
        }

        n_samples = len(states)
        batch_size = min(self.config.batch_size, n_samples)

        for epoch in range(self.config.n_epochs):
            # Shuffle indices
            indices = np.random.permutation(n_samples)

            for start in range(0, n_samples, batch_size):
                end = min(start + batch_size, n_samples)
                batch_indices = indices[start:end]

                batch_states = states[batch_indices]
                batch_actions = actions[batch_indices]
                batch_old_log_probs = old_log_probs[batch_indices]
                batch_advantages = advantages[batch_indices]
                batch_returns = returns[batch_indices]

                # Get current policy outputs
                features = self._get_features(batch_states)
                action_type_probs, operation_probs, machine_probs = self._get_action_probs(features)
                values_pred = self._get_value(features).squeeze(-1)

                # Calculate new log probs
                action_type_dist = Categorical(action_type_probs)
                operation_dist = Categorical(operation_probs)
                machine_dist = Categorical(machine_probs)

                new_log_probs = (
                    action_type_dist.log_prob(batch_actions[:, 0]) +
                    operation_dist.log_prob(batch_actions[:, 1]) +
                    machine_dist.log_prob(batch_actions[:, 2])
                )

                # Calculate entropy
                entropy = (
                    action_type_dist.entropy() +
                    operation_dist.entropy() +
                    machine_dist.entropy()
                ).mean()

                # Calculate ratio and clipped ratio
                ratio = torch.exp(new_log_probs - batch_old_log_probs)
                clipped_ratio = torch.clamp(
                    ratio,
                    1 - self.config.clip_epsilon,
                    1 + self.config.clip_epsilon
                )

                # Policy loss
                policy_loss = -torch.min(
                    ratio * batch_advantages,
                    clipped_ratio * batch_advantages
                ).mean()

                # Value loss
                value_loss = self.F.mse_loss(values_pred, batch_returns)

                # Total loss
                loss = (
                    policy_loss +
                    self.config.value_loss_coef * value_loss -
                    self.config.entropy_coef * entropy
                )

                # Update
                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    self._get_all_params(),
                    self.config.max_grad_norm
                )
                self.optimizer.step()

                # Accumulate metrics
                with torch.no_grad():
                    approx_kl = (batch_old_log_probs - new_log_probs).mean()
                    clip_fraction = (torch.abs(ratio - 1) > self.config.clip_epsilon).float().mean()

                metrics["policy_loss"] += policy_loss.item()
                metrics["value_loss"] += value_loss.item()
                metrics["entropy"] += entropy.item()
                metrics["approx_kl"] += approx_kl.item()
                metrics["clip_fraction"] += clip_fraction.item()

        # Average metrics
        n_updates = self.config.n_epochs * (n_samples // batch_size + 1)
        for key in metrics:
            metrics[key] /= n_updates

        # Clear buffer
        self.buffer.clear()
        self.update_count += 1

        return metrics

    def _get_all_params(self):
        """Get all trainable parameters."""
        params = []
        if self.feature_extractor:
            params.extend(self.feature_extractor.parameters())
        params.extend(self.action_type_head.parameters())
        params.extend(self.operation_head.parameters())
        params.extend(self.machine_head.parameters())
        params.extend(self.critic.parameters())
        return params

    def save(self, path: str):
        """
        Save agent to disk.

        Args:
            path: Directory path to save to
        """
        torch = self.torch

        os.makedirs(path, exist_ok=True)

        # Save networks
        state_dict = {
            "action_type_head": self.action_type_head.state_dict(),
            "operation_head": self.operation_head.state_dict(),
            "machine_head": self.machine_head.state_dict(),
            "critic": self.critic.state_dict(),
            "optimizer": self.optimizer.state_dict()
        }

        if self.feature_extractor:
            state_dict["feature_extractor"] = self.feature_extractor.state_dict()

        torch.save(state_dict, os.path.join(path, "ppo_model.pt"))

        # Save config and training state
        config_dict = {
            "obs_dim": self.obs_dim,
            "action_dim": self.action_dim,
            "step_count": self.step_count,
            "episode_count": self.episode_count,
            "update_count": self.update_count,
            "config": self.config.__dict__
        }

        with open(os.path.join(path, "ppo_config.json"), "w") as f:
            json.dump(config_dict, f, indent=2)

        # Save training history
        self.save_training_history(os.path.join(path, "ppo_history.json"))

    def load(self, path: str):
        """
        Load agent from disk.

        Args:
            path: Directory path to load from
        """
        torch = self.torch

        # Load networks
        state_dict = torch.load(
            os.path.join(path, "ppo_model.pt"),
            map_location=self.device
        )

        self.action_type_head.load_state_dict(state_dict["action_type_head"])
        self.operation_head.load_state_dict(state_dict["operation_head"])
        self.machine_head.load_state_dict(state_dict["machine_head"])
        self.critic.load_state_dict(state_dict["critic"])
        self.optimizer.load_state_dict(state_dict["optimizer"])

        if self.feature_extractor and "feature_extractor" in state_dict:
            self.feature_extractor.load_state_dict(state_dict["feature_extractor"])

        # Load config
        with open(os.path.join(path, "ppo_config.json"), "r") as f:
            config_dict = json.load(f)
            self.step_count = config_dict.get("step_count", 0)
            self.episode_count = config_dict.get("episode_count", 0)
            self.update_count = config_dict.get("update_count", 0)

        # Load training history
        self.load_training_history(os.path.join(path, "ppo_history.json"))

    def get_policy_info(self, state: np.ndarray) -> Dict[str, Any]:
        """
        Get detailed policy information for debugging.

        Args:
            state: Current observation

        Returns:
            Dictionary with policy details
        """
        torch = self.torch

        with torch.no_grad():
            features = self._get_features(state)
            action_type_probs, operation_probs, machine_probs = self._get_action_probs(features)
            value = self._get_value(features)

            return {
                "value": value.item(),
                "action_type_distribution": action_type_probs.cpu().numpy().flatten().tolist(),
                "top_operations": operation_probs.topk(5).indices.cpu().numpy().flatten().tolist(),
                "top_machines": machine_probs.topk(3).indices.cpu().numpy().flatten().tolist(),
                "entropy": {
                    "action_type": -(action_type_probs * action_type_probs.log()).sum().item(),
                    "operation": -(operation_probs * operation_probs.log()).sum().item(),
                    "machine": -(machine_probs * machine_probs.log()).sum().item()
                }
            }
