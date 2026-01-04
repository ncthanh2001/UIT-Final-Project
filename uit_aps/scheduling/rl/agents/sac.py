# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Soft Actor-Critic (SAC) Agent for Scheduling

Implements SAC algorithm for real-time scheduling adjustments.
SAC is an off-policy algorithm that maximizes both expected reward
and entropy for better exploration.

Reference: Haarnoja et al. "Soft Actor-Critic: Off-Policy Maximum Entropy
           Deep Reinforcement Learning with a Stochastic Actor" (2018)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import os
import json
import copy

from uit_aps.scheduling.rl.agents.base import (
    BaseAgent, AgentConfig, ReplayBuffer
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
class SACConfig(AgentConfig):
    """Configuration for SAC agent."""
    # SAC specific
    tau: float = 0.005              # Soft update coefficient
    alpha: float = 0.2              # Entropy coefficient
    auto_entropy_tuning: bool = True  # Automatic entropy tuning
    target_entropy_scale: float = 0.98

    # Training
    update_interval: int = 1
    gradient_steps: int = 1

    # Network
    hidden_sizes: List[int] = field(default_factory=lambda: [256, 256])

    # Action space
    num_action_types: int = 7
    max_operations: int = 100
    max_machines: int = 20


class SACAgent(BaseAgent):
    """
    SAC Agent for real-time scheduling adjustments.

    SAC uses two Q-networks and a policy network with entropy regularization.
    This promotes exploration while learning a stable policy.

    Architecture:
    - Actor network: outputs action probabilities (stochastic policy)
    - Twin Q-networks: estimates Q-values (clipped double Q-learning)
    - Target Q-networks: provides stable targets
    """

    def __init__(
        self,
        obs_dim: int,
        action_dim: int,
        config: SACConfig = None
    ):
        """
        Initialize SAC agent.

        Args:
            obs_dim: Observation space dimension
            action_dim: Action space dimension
            config: SAC configuration
        """
        super().__init__(obs_dim, action_dim, config or SACConfig())

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

        # Replay buffer
        self.buffer = ReplayBuffer(self.config.buffer_size)

        # Entropy tuning
        if self.config.auto_entropy_tuning:
            self._setup_entropy_tuning()

        # Training state
        self.update_count = 0

    def _build_networks(self):
        """Build actor, critic, and target networks."""
        nn = self.nn
        torch = self.torch

        config = self.config
        hidden_sizes = config.hidden_sizes

        # Actor network (policy)
        self.actor = self._build_actor().to(self.device)

        # Twin Q-networks
        self.q1 = self._build_critic().to(self.device)
        self.q2 = self._build_critic().to(self.device)

        # Target Q-networks
        self.q1_target = self._build_critic().to(self.device)
        self.q2_target = self._build_critic().to(self.device)

        # Copy parameters to targets
        self.q1_target.load_state_dict(self.q1.state_dict())
        self.q2_target.load_state_dict(self.q2.state_dict())

        # Optimizers
        self.actor_optimizer = self.optim.Adam(
            self.actor.parameters(), lr=config.learning_rate
        )
        self.q1_optimizer = self.optim.Adam(
            self.q1.parameters(), lr=config.learning_rate
        )
        self.q2_optimizer = self.optim.Adam(
            self.q2.parameters(), lr=config.learning_rate
        )

    def _build_actor(self) -> "nn.Module":
        """Build actor network."""
        nn = self.nn
        config = self.config
        hidden_sizes = config.hidden_sizes

        class Actor(nn.Module):
            def __init__(self, obs_dim, hidden_sizes, num_actions, max_ops, max_machines):
                super().__init__()

                # Shared feature extractor
                layers = []
                prev_size = obs_dim
                for hidden_size in hidden_sizes:
                    layers.append(nn.Linear(prev_size, hidden_size))
                    layers.append(nn.ReLU())
                    prev_size = hidden_size

                self.features = nn.Sequential(*layers)

                # Action heads
                self.action_type_head = nn.Linear(prev_size, num_actions)
                self.operation_head = nn.Linear(prev_size, max_ops)
                self.machine_head = nn.Linear(prev_size, max_machines)

            def forward(self, state):
                features = self.features(state)

                action_type_logits = self.action_type_head(features)
                operation_logits = self.operation_head(features)
                machine_logits = self.machine_head(features)

                return action_type_logits, operation_logits, machine_logits

            def get_action(self, state, deterministic=False):
                action_type_logits, operation_logits, machine_logits = self(state)

                action_type_probs = nn.functional.softmax(action_type_logits, dim=-1)
                operation_probs = nn.functional.softmax(operation_logits, dim=-1)
                machine_probs = nn.functional.softmax(machine_logits, dim=-1)

                if deterministic:
                    action_type = action_type_probs.argmax(dim=-1)
                    operation = operation_probs.argmax(dim=-1)
                    machine = machine_probs.argmax(dim=-1)
                else:
                    action_type = torch.multinomial(action_type_probs, 1).squeeze(-1)
                    operation = torch.multinomial(operation_probs, 1).squeeze(-1)
                    machine = torch.multinomial(machine_probs, 1).squeeze(-1)

                # Calculate log probabilities
                log_prob_type = torch.log(action_type_probs.gather(-1, action_type.unsqueeze(-1)) + 1e-8)
                log_prob_op = torch.log(operation_probs.gather(-1, operation.unsqueeze(-1)) + 1e-8)
                log_prob_machine = torch.log(machine_probs.gather(-1, machine.unsqueeze(-1)) + 1e-8)

                log_prob = log_prob_type + log_prob_op + log_prob_machine

                return action_type, operation, machine, log_prob.squeeze(-1), action_type_probs, operation_probs, machine_probs

        return Actor(
            self.obs_dim,
            hidden_sizes,
            config.num_action_types,
            config.max_operations,
            config.max_machines
        )

    def _build_critic(self) -> "nn.Module":
        """Build Q-network."""
        nn = self.nn
        config = self.config
        hidden_sizes = config.hidden_sizes

        class Critic(nn.Module):
            def __init__(self, obs_dim, hidden_sizes, num_actions, max_ops, max_machines):
                super().__init__()

                # State encoder
                layers = []
                prev_size = obs_dim
                for hidden_size in hidden_sizes:
                    layers.append(nn.Linear(prev_size, hidden_size))
                    layers.append(nn.ReLU())
                    prev_size = hidden_size

                self.features = nn.Sequential(*layers)

                # Q-value heads (for each action component)
                self.q_type = nn.Linear(prev_size, num_actions)
                self.q_operation = nn.Linear(prev_size, max_ops)
                self.q_machine = nn.Linear(prev_size, max_machines)

            def forward(self, state):
                features = self.features(state)

                q_type = self.q_type(features)
                q_operation = self.q_operation(features)
                q_machine = self.q_machine(features)

                return q_type, q_operation, q_machine

            def get_q_value(self, state, action_type, operation, machine):
                q_type, q_operation, q_machine = self(state)

                q_value = (
                    q_type.gather(-1, action_type.unsqueeze(-1)) +
                    q_operation.gather(-1, operation.unsqueeze(-1)) +
                    q_machine.gather(-1, machine.unsqueeze(-1))
                ) / 3.0  # Average across action components

                return q_value.squeeze(-1)

        return Critic(
            self.obs_dim,
            hidden_sizes,
            config.num_action_types,
            config.max_operations,
            config.max_machines
        )

    def _setup_entropy_tuning(self):
        """Setup automatic entropy coefficient tuning."""
        torch = self.torch

        # Target entropy (heuristic)
        target_entropy_type = -np.log(1.0 / self.config.num_action_types) * self.config.target_entropy_scale
        target_entropy_op = -np.log(1.0 / self.config.max_operations) * self.config.target_entropy_scale
        target_entropy_machine = -np.log(1.0 / self.config.max_machines) * self.config.target_entropy_scale

        self.target_entropy = target_entropy_type + target_entropy_op + target_entropy_machine

        # Learnable log alpha
        self.log_alpha = torch.zeros(1, requires_grad=True, device=self.device)
        self.alpha_optimizer = self.optim.Adam([self.log_alpha], lr=self.config.learning_rate)

    @property
    def alpha(self):
        """Get current entropy coefficient."""
        if self.config.auto_entropy_tuning:
            return self.log_alpha.exp().item()
        return self.config.alpha

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

        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

            action_type, operation, machine, log_prob, type_probs, op_probs, machine_probs = \
                self.actor.get_action(state_tensor, deterministic=deterministic)

            action_type = action_type.item()
            operation = operation.item()
            machine = machine.item()

            # Get Q-values for info
            q1_type, q1_op, q1_machine = self.q1(state_tensor)

            # Apply valid action mask if provided
            if valid_actions and not deterministic:
                valid_types = set(a[0] for a in valid_actions)
                valid_ops = set(a[1] for a in valid_actions)
                valid_machines = set(a[2] for a in valid_actions)

                if action_type not in valid_types:
                    action_type = list(valid_types)[0] if valid_types else 0
                if operation not in valid_ops:
                    operation = list(valid_ops)[0] if valid_ops else 0
                if machine not in valid_machines:
                    machine = list(valid_machines)[0] if valid_machines else 0

        action = (action_type, operation, machine)

        info = {
            "log_prob": log_prob.item(),
            "q1_value": q1_type[0, action_type].item(),
            "alpha": self.alpha,
            "action_type_probs": type_probs.cpu().numpy().flatten()[:7],
            "operation_probs": op_probs.cpu().numpy().flatten()[:10],
            "machine_probs": machine_probs.cpu().numpy().flatten()[:5]
        }

        self.step_count += 1

        return action, info

    def store_transition(
        self,
        state: np.ndarray,
        action: Tuple[int, int, int],
        reward: float,
        next_state: np.ndarray,
        done: bool
    ):
        """
        Store transition in replay buffer.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode ended
        """
        self.buffer.push(state, action, reward, next_state, done)

    def update(self, batch: Dict[str, np.ndarray] = None) -> Dict[str, float]:
        """
        Update policy using SAC algorithm.

        Args:
            batch: Optional batch (if None, samples from buffer)

        Returns:
            Dictionary with training metrics
        """
        torch = self.torch

        if len(self.buffer) < self.config.batch_size:
            return {}

        if batch is None:
            batch = self.buffer.sample(self.config.batch_size)

        # Convert to tensors
        states = torch.FloatTensor(batch["states"]).to(self.device)
        actions = torch.LongTensor(batch["actions"]).to(self.device)
        rewards = torch.FloatTensor(batch["rewards"]).to(self.device)
        next_states = torch.FloatTensor(batch["next_states"]).to(self.device)
        dones = torch.FloatTensor(batch["dones"]).to(self.device)

        # Extract action components
        action_types = actions[:, 0]
        operations = actions[:, 1]
        machines = actions[:, 2]

        # Update Q-networks
        q1_loss, q2_loss = self._update_critics(
            states, action_types, operations, machines,
            rewards, next_states, dones
        )

        # Update actor
        actor_loss, alpha_loss = self._update_actor(states)

        # Soft update target networks
        self._soft_update()

        self.update_count += 1

        return {
            "q1_loss": q1_loss,
            "q2_loss": q2_loss,
            "actor_loss": actor_loss,
            "alpha_loss": alpha_loss,
            "alpha": self.alpha
        }

    def _update_critics(
        self,
        states,
        action_types,
        operations,
        machines,
        rewards,
        next_states,
        dones
    ):
        """Update Q-networks."""
        torch = self.torch

        with torch.no_grad():
            # Get next actions and log probs from current policy
            next_action_type, next_op, next_machine, next_log_prob, _, _, _ = \
                self.actor.get_action(next_states)

            # Get target Q-values
            next_q1 = self.q1_target.get_q_value(next_states, next_action_type, next_op, next_machine)
            next_q2 = self.q2_target.get_q_value(next_states, next_action_type, next_op, next_machine)
            next_q = torch.min(next_q1, next_q2)

            # Compute target with entropy bonus
            target_q = rewards + (1 - dones) * self.config.gamma * (next_q - self.alpha * next_log_prob)

        # Current Q-values
        current_q1 = self.q1.get_q_value(states, action_types, operations, machines)
        current_q2 = self.q2.get_q_value(states, action_types, operations, machines)

        # Q-network losses
        q1_loss = self.F.mse_loss(current_q1, target_q)
        q2_loss = self.F.mse_loss(current_q2, target_q)

        # Update Q1
        self.q1_optimizer.zero_grad()
        q1_loss.backward()
        self.q1_optimizer.step()

        # Update Q2
        self.q2_optimizer.zero_grad()
        q2_loss.backward()
        self.q2_optimizer.step()

        return q1_loss.item(), q2_loss.item()

    def _update_actor(self, states):
        """Update actor network."""
        torch = self.torch

        # Get actions and log probs
        action_type, operation, machine, log_prob, type_probs, op_probs, machine_probs = \
            self.actor.get_action(states)

        # Get Q-values
        q1 = self.q1.get_q_value(states, action_type, operation, machine)
        q2 = self.q2.get_q_value(states, action_type, operation, machine)
        q = torch.min(q1, q2)

        # Actor loss (maximize Q - alpha * log_prob)
        actor_loss = (self.alpha * log_prob - q).mean()

        # Update actor
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        # Update alpha (entropy coefficient)
        alpha_loss = 0.0
        if self.config.auto_entropy_tuning:
            alpha_loss = -(self.log_alpha.exp() * (log_prob + self.target_entropy).detach()).mean()

            self.alpha_optimizer.zero_grad()
            alpha_loss.backward()
            self.alpha_optimizer.step()
            alpha_loss = alpha_loss.item()

        return actor_loss.item(), alpha_loss

    def _soft_update(self):
        """Soft update target networks."""
        tau = self.config.tau

        for target_param, param in zip(self.q1_target.parameters(), self.q1.parameters()):
            target_param.data.copy_(tau * param.data + (1 - tau) * target_param.data)

        for target_param, param in zip(self.q2_target.parameters(), self.q2.parameters()):
            target_param.data.copy_(tau * param.data + (1 - tau) * target_param.data)

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
            "actor": self.actor.state_dict(),
            "q1": self.q1.state_dict(),
            "q2": self.q2.state_dict(),
            "q1_target": self.q1_target.state_dict(),
            "q2_target": self.q2_target.state_dict(),
            "actor_optimizer": self.actor_optimizer.state_dict(),
            "q1_optimizer": self.q1_optimizer.state_dict(),
            "q2_optimizer": self.q2_optimizer.state_dict()
        }

        if self.config.auto_entropy_tuning:
            state_dict["log_alpha"] = self.log_alpha
            state_dict["alpha_optimizer"] = self.alpha_optimizer.state_dict()

        torch.save(state_dict, os.path.join(path, "sac_model.pt"))

        # Save config and training state
        config_dict = {
            "obs_dim": self.obs_dim,
            "action_dim": self.action_dim,
            "step_count": self.step_count,
            "episode_count": self.episode_count,
            "update_count": self.update_count,
            "config": self.config.__dict__
        }

        with open(os.path.join(path, "sac_config.json"), "w") as f:
            json.dump(config_dict, f, indent=2)

        # Save training history
        self.save_training_history(os.path.join(path, "sac_history.json"))

    def load(self, path: str):
        """
        Load agent from disk.

        Args:
            path: Directory path to load from
        """
        torch = self.torch

        # Load networks
        state_dict = torch.load(
            os.path.join(path, "sac_model.pt"),
            map_location=self.device
        )

        self.actor.load_state_dict(state_dict["actor"])
        self.q1.load_state_dict(state_dict["q1"])
        self.q2.load_state_dict(state_dict["q2"])
        self.q1_target.load_state_dict(state_dict["q1_target"])
        self.q2_target.load_state_dict(state_dict["q2_target"])
        self.actor_optimizer.load_state_dict(state_dict["actor_optimizer"])
        self.q1_optimizer.load_state_dict(state_dict["q1_optimizer"])
        self.q2_optimizer.load_state_dict(state_dict["q2_optimizer"])

        if self.config.auto_entropy_tuning and "log_alpha" in state_dict:
            self.log_alpha = state_dict["log_alpha"]
            self.alpha_optimizer.load_state_dict(state_dict["alpha_optimizer"])

        # Load config
        with open(os.path.join(path, "sac_config.json"), "r") as f:
            config_dict = json.load(f)
            self.step_count = config_dict.get("step_count", 0)
            self.episode_count = config_dict.get("episode_count", 0)
            self.update_count = config_dict.get("update_count", 0)

        # Load training history
        self.load_training_history(os.path.join(path, "sac_history.json"))

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
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

            _, _, _, log_prob, type_probs, op_probs, machine_probs = \
                self.actor.get_action(state_tensor)

            q1_type, q1_op, q1_machine = self.q1(state_tensor)
            q2_type, q2_op, q2_machine = self.q2(state_tensor)

            return {
                "log_prob": log_prob.item(),
                "alpha": self.alpha,
                "action_type_distribution": type_probs.cpu().numpy().flatten().tolist(),
                "q1_values": {
                    "type": q1_type.mean().item(),
                    "operation": q1_op.mean().item(),
                    "machine": q1_machine.mean().item()
                },
                "q2_values": {
                    "type": q2_type.mean().item(),
                    "operation": q2_op.mean().item(),
                    "machine": q2_machine.mean().item()
                },
                "entropy": {
                    "action_type": -(type_probs * type_probs.log()).sum().item(),
                    "operation": -(op_probs * op_probs.log()).sum().item(),
                    "machine": -(machine_probs * machine_probs.log()).sum().item()
                }
            }
