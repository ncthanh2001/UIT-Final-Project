# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Base Agent for RL Scheduling

Abstract base class for all RL agents.
"""

import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
import json
import os


@dataclass
class AgentConfig:
    """Base configuration for RL agents."""
    # Network architecture
    hidden_sizes: List[int] = None
    activation: str = "relu"

    # Training
    learning_rate: float = 3e-4
    gamma: float = 0.99
    batch_size: int = 64

    # Exploration
    initial_epsilon: float = 1.0
    final_epsilon: float = 0.01
    epsilon_decay: float = 0.995

    # Memory
    buffer_size: int = 100000

    # Device
    device: str = "cpu"

    def __post_init__(self):
        if self.hidden_sizes is None:
            self.hidden_sizes = [256, 256]


class ReplayBuffer:
    """Experience replay buffer for off-policy learning."""

    def __init__(self, capacity: int = 100000):
        """
        Initialize replay buffer.

        Args:
            capacity: Maximum number of experiences to store
        """
        self.capacity = capacity
        self.buffer: List[Dict] = []
        self.position = 0

    def push(
        self,
        state: np.ndarray,
        action: Tuple[int, int, int],
        reward: float,
        next_state: np.ndarray,
        done: bool
    ):
        """
        Add experience to buffer.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode ended
        """
        experience = {
            "state": state,
            "action": action,
            "reward": reward,
            "next_state": next_state,
            "done": done
        }

        if len(self.buffer) < self.capacity:
            self.buffer.append(experience)
        else:
            self.buffer[self.position] = experience

        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size: int) -> Dict[str, np.ndarray]:
        """
        Sample a batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            Dictionary with batched experiences
        """
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)

        states = np.array([self.buffer[i]["state"] for i in indices])
        actions = np.array([self.buffer[i]["action"] for i in indices])
        rewards = np.array([self.buffer[i]["reward"] for i in indices])
        next_states = np.array([self.buffer[i]["next_state"] for i in indices])
        dones = np.array([self.buffer[i]["done"] for i in indices])

        return {
            "states": states,
            "actions": actions,
            "rewards": rewards,
            "next_states": next_states,
            "dones": dones
        }

    def __len__(self) -> int:
        return len(self.buffer)


class RolloutBuffer:
    """Rollout buffer for on-policy learning (PPO)."""

    def __init__(self):
        """Initialize rollout buffer."""
        self.states: List[np.ndarray] = []
        self.actions: List[Tuple[int, int, int]] = []
        self.rewards: List[float] = []
        self.values: List[float] = []
        self.log_probs: List[float] = []
        self.dones: List[bool] = []

    def push(
        self,
        state: np.ndarray,
        action: Tuple[int, int, int],
        reward: float,
        value: float,
        log_prob: float,
        done: bool
    ):
        """Add experience to buffer."""
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
        self.dones.append(done)

    def get(self) -> Dict[str, np.ndarray]:
        """Get all experiences as numpy arrays."""
        return {
            "states": np.array(self.states),
            "actions": np.array(self.actions),
            "rewards": np.array(self.rewards),
            "values": np.array(self.values),
            "log_probs": np.array(self.log_probs),
            "dones": np.array(self.dones)
        }

    def clear(self):
        """Clear the buffer."""
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.log_probs = []
        self.dones = []

    def __len__(self) -> int:
        return len(self.states)


class BaseAgent(ABC):
    """
    Abstract base class for RL scheduling agents.

    All agents must implement:
    - select_action: Choose action given state
    - update: Update policy from experiences
    - save/load: Persistence methods
    """

    def __init__(
        self,
        obs_dim: int,
        action_dim: int,
        config: AgentConfig = None
    ):
        """
        Initialize base agent.

        Args:
            obs_dim: Observation space dimension
            action_dim: Action space dimension
            config: Agent configuration
        """
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.config = config or AgentConfig()

        # Training state
        self.training = True
        self.step_count = 0
        self.episode_count = 0
        self.epsilon = self.config.initial_epsilon

        # Logging
        self.training_history: List[Dict] = []

    @abstractmethod
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
        pass

    @abstractmethod
    def update(self, batch: Dict[str, np.ndarray]) -> Dict[str, float]:
        """
        Update policy from batch of experiences.

        Args:
            batch: Dictionary with experience batch

        Returns:
            Dictionary with training metrics
        """
        pass

    @abstractmethod
    def save(self, path: str):
        """
        Save agent to disk.

        Args:
            path: Directory path to save to
        """
        pass

    @abstractmethod
    def load(self, path: str):
        """
        Load agent from disk.

        Args:
            path: Directory path to load from
        """
        pass

    def train(self):
        """Set agent to training mode."""
        self.training = True

    def eval(self):
        """Set agent to evaluation mode."""
        self.training = False

    def decay_epsilon(self):
        """Decay exploration epsilon."""
        self.epsilon = max(
            self.config.final_epsilon,
            self.epsilon * self.config.epsilon_decay
        )

    def log_episode(self, episode_info: Dict):
        """
        Log episode information.

        Args:
            episode_info: Dictionary with episode metrics
        """
        episode_info["episode"] = self.episode_count
        episode_info["epsilon"] = self.epsilon
        episode_info["timestamp"] = datetime.now().isoformat()

        self.training_history.append(episode_info)
        self.episode_count += 1

    def get_training_summary(self) -> Dict:
        """
        Get summary of training progress.

        Returns:
            Dictionary with training statistics
        """
        if not self.training_history:
            return {}

        recent = self.training_history[-100:]

        return {
            "total_episodes": self.episode_count,
            "total_steps": self.step_count,
            "current_epsilon": self.epsilon,
            "avg_reward_100": np.mean([e.get("total_reward", 0) for e in recent]),
            "avg_length_100": np.mean([e.get("episode_length", 0) for e in recent]),
            "success_rate_100": np.mean([e.get("success", False) for e in recent])
        }

    def save_training_history(self, path: str):
        """
        Save training history to JSON file.

        Args:
            path: File path
        """
        with open(path, "w") as f:
            json.dump(self.training_history, f, indent=2)

    def load_training_history(self, path: str):
        """
        Load training history from JSON file.

        Args:
            path: File path
        """
        if os.path.exists(path):
            with open(path, "r") as f:
                self.training_history = json.load(f)
                if self.training_history:
                    self.episode_count = self.training_history[-1].get("episode", 0) + 1


def compute_gae(
    rewards: np.ndarray,
    values: np.ndarray,
    dones: np.ndarray,
    gamma: float = 0.99,
    lam: float = 0.95
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute Generalized Advantage Estimation (GAE).

    Args:
        rewards: Reward sequence
        values: Value estimates
        dones: Done flags
        gamma: Discount factor
        lam: GAE lambda

    Returns:
        Tuple of (advantages, returns)
    """
    n = len(rewards)
    advantages = np.zeros(n)
    last_gae = 0

    for t in reversed(range(n)):
        if t == n - 1:
            next_value = 0
        else:
            next_value = values[t + 1]

        delta = rewards[t] + gamma * next_value * (1 - dones[t]) - values[t]
        advantages[t] = last_gae = delta + gamma * lam * (1 - dones[t]) * last_gae

    returns = advantages + values

    return advantages, returns


def normalize(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """
    Normalize array to zero mean and unit variance.

    Args:
        x: Input array
        eps: Small constant for numerical stability

    Returns:
        Normalized array
    """
    return (x - np.mean(x)) / (np.std(x) + eps)
