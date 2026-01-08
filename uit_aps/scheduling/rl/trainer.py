# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Training Pipeline for RL Scheduling Agents

Handles the training loop, evaluation, and model management.
Supports both PPO and SAC agents with configurable training parameters.
"""

import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any, Type
import os
import json
import time


@dataclass
class TrainerConfig:
    """Configuration for the training pipeline."""
    # Training parameters
    max_episodes: int = 1000
    max_steps_per_episode: int = 200
    eval_frequency: int = 50
    eval_episodes: int = 10
    save_frequency: int = 100

    # Early stopping
    early_stopping: bool = True
    patience: int = 100
    min_improvement: float = 0.01

    # Logging
    log_frequency: int = 10
    verbose: bool = True

    # Paths (will be set to Frappe site path if running in Frappe context)
    save_dir: str = ""  # Empty means use default Frappe path
    log_dir: str = ""   # Empty means use default Frappe path

    # Agent selection
    agent_type: str = "ppo"  # "ppo" or "sac"


class RLTrainer:
    """
    Training pipeline for RL scheduling agents.

    Handles:
    - Training loop with environment interaction
    - Policy updates
    - Evaluation and metrics tracking
    - Model checkpointing
    - Early stopping
    """

    def __init__(
        self,
        env,
        agent,
        config: TrainerConfig = None
    ):
        """
        Initialize the trainer.

        Args:
            env: SchedulingEnv environment
            agent: PPOAgent or SACAgent
            config: Training configuration
        """
        self.env = env
        self.agent = agent
        self.config = config or TrainerConfig()

        # Training state
        self.episode = 0
        self.total_steps = 0
        self.best_reward = float("-inf")
        self.patience_counter = 0

        # Metrics
        self.training_metrics: List[Dict] = []
        self.eval_metrics: List[Dict] = []

        # Create directories
        os.makedirs(self.config.save_dir, exist_ok=True)
        os.makedirs(self.config.log_dir, exist_ok=True)

    def train(
        self,
        initial_schedule: List[Dict] = None,
        machines: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Run the training loop.

        Args:
            initial_schedule: Initial schedule from Tier 1 OR-Tools
            machines: Available machines

        Returns:
            Dictionary with training summary
        """
        self._log("Starting training...")
        start_time = time.time()

        for episode in range(self.config.max_episodes):
            self.episode = episode

            # Run episode
            episode_metrics = self._run_episode(initial_schedule, machines)
            self.training_metrics.append(episode_metrics)

            # Update agent (for PPO)
            if hasattr(self.agent, "buffer") and len(self.agent.buffer) > 0:
                update_metrics = self.agent.update()
                episode_metrics.update(update_metrics)

            # Logging
            if episode % self.config.log_frequency == 0:
                self._log_episode(episode_metrics)

            # Evaluation
            if episode % self.config.eval_frequency == 0:
                eval_metrics = self._evaluate(initial_schedule, machines)
                self.eval_metrics.append(eval_metrics)

                # Check for improvement
                if eval_metrics["mean_reward"] > self.best_reward + self.config.min_improvement:
                    self.best_reward = eval_metrics["mean_reward"]
                    self.patience_counter = 0
                    self._save_best()
                else:
                    self.patience_counter += 1

                # Early stopping
                if self.config.early_stopping and self.patience_counter >= self.config.patience:
                    self._log(f"Early stopping at episode {episode}")
                    break

            # Checkpointing
            if episode % self.config.save_frequency == 0:
                self._save_checkpoint(episode)

            # Decay exploration
            self.agent.decay_epsilon()

        # Final save
        self._save_checkpoint(self.episode)
        self._save_metrics()

        training_time = time.time() - start_time

        summary = {
            "total_episodes": self.episode + 1,
            "total_steps": self.total_steps,
            "best_reward": self.best_reward,
            "training_time_seconds": training_time,
            "final_metrics": self.training_metrics[-1] if self.training_metrics else {}
        }

        self._log(f"Training completed: {summary}")

        return summary

    def _run_episode(
        self,
        initial_schedule: List[Dict] = None,
        machines: List[Dict] = None
    ) -> Dict[str, float]:
        """
        Run a single training episode.

        Args:
            initial_schedule: Initial schedule
            machines: Available machines

        Returns:
            Episode metrics
        """
        # Reset environment
        obs, info = self.env.reset(
            initial_schedule=initial_schedule,
            machines=machines,
            seed=self.episode
        )

        episode_reward = 0.0
        episode_length = 0
        actions_taken = []

        for step in range(self.config.max_steps_per_episode):
            # Select action
            valid_actions = self.env.get_valid_actions()
            action, action_info = self.agent.select_action(
                obs,
                valid_actions=valid_actions,
                deterministic=False
            )

            # Take step
            next_obs, reward, terminated, truncated, step_info = self.env.step(action)
            done = terminated or truncated

            # Store transition
            if hasattr(self.agent, "store_transition"):
                # Check agent type to use correct signature
                if self.config.agent_type.lower() == "sac":
                    # SAC signature: (state, action, reward, next_state, done)
                    self.agent.store_transition(obs, action, reward, next_obs, done)
                else:
                    # PPO signature: (state, action, reward, value, log_prob, done)
                    self.agent.store_transition(
                        obs, action, reward,
                        action_info.get("value", 0.0),
                        action_info.get("log_prob", 0.0),
                        done
                    )

            # Update metrics
            episode_reward += reward
            episode_length += 1
            actions_taken.append(action[0])  # Action type
            self.total_steps += 1

            obs = next_obs

            # For SAC, update after each step
            if self.config.agent_type == "sac":
                if self.total_steps % self.agent.config.update_interval == 0:
                    self.agent.update()

            if done:
                break

        # Log episode
        self.agent.log_episode({
            "total_reward": episode_reward,
            "episode_length": episode_length,
            "success": step_info.get("late_jobs", 0) == 0
        })

        return {
            "episode": self.episode,
            "reward": episode_reward,
            "length": episode_length,
            "completed": step_info.get("completed_operations", 0),
            "late_jobs": step_info.get("late_jobs", 0),
            "tardiness": step_info.get("total_tardiness_mins", 0),
            "utilization": step_info.get("average_utilization", 0.0),
            "action_distribution": {
                i: actions_taken.count(i) for i in range(7)
            }
        }

    def _evaluate(
        self,
        initial_schedule: List[Dict] = None,
        machines: List[Dict] = None
    ) -> Dict[str, float]:
        """
        Evaluate current policy.

        Args:
            initial_schedule: Initial schedule
            machines: Available machines

        Returns:
            Evaluation metrics
        """
        self.agent.eval()

        rewards = []
        successes = []
        tardiness_list = []
        utilizations = []

        for ep in range(self.config.eval_episodes):
            obs, info = self.env.reset(
                initial_schedule=initial_schedule,
                machines=machines,
                seed=10000 + ep  # Different seeds for evaluation
            )

            episode_reward = 0.0

            for step in range(self.config.max_steps_per_episode):
                valid_actions = self.env.get_valid_actions()
                action, _ = self.agent.select_action(
                    obs,
                    valid_actions=valid_actions,
                    deterministic=True  # Deterministic for evaluation
                )

                obs, reward, terminated, truncated, step_info = self.env.step(action)
                episode_reward += reward

                if terminated or truncated:
                    break

            rewards.append(episode_reward)
            successes.append(step_info.get("late_jobs", 0) == 0)
            tardiness_list.append(step_info.get("total_tardiness_mins", 0))
            utilizations.append(step_info.get("average_utilization", 0.0))

        self.agent.train()

        eval_metrics = {
            "episode": self.episode,
            "mean_reward": np.mean(rewards),
            "std_reward": np.std(rewards),
            "success_rate": np.mean(successes),
            "mean_tardiness": np.mean(tardiness_list),
            "mean_utilization": np.mean(utilizations)
        }

        self._log(f"Evaluation: {eval_metrics}")

        return eval_metrics

    def _save_checkpoint(self, episode: int):
        """Save training checkpoint."""
        checkpoint_dir = os.path.join(self.config.save_dir, f"checkpoint_{episode}")
        self.agent.save(checkpoint_dir)
        self._log(f"Saved checkpoint at episode {episode}")

    def _save_best(self):
        """Save best model."""
        best_dir = os.path.join(self.config.save_dir, "best")
        self.agent.save(best_dir)
        self._log(f"Saved new best model with reward {self.best_reward:.2f}")

    def _save_metrics(self):
        """Save training and evaluation metrics."""
        metrics = {
            "training": self.training_metrics,
            "evaluation": self.eval_metrics,
            "config": self.config.__dict__
        }

        metrics_path = os.path.join(self.config.log_dir, "metrics.json")
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2, default=str)

    def _log(self, message: str):
        """Log message if verbose."""
        if self.config.verbose:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {message}")

    def _log_episode(self, metrics: Dict):
        """Log episode metrics."""
        self._log(
            f"Episode {metrics['episode']}: "
            f"reward={metrics['reward']:.2f}, "
            f"length={metrics['length']}, "
            f"late={metrics['late_jobs']}, "
            f"tardiness={metrics['tardiness']:.0f}min"
        )

    def load_best(self):
        """Load best saved model."""
        best_dir = os.path.join(self.config.save_dir, "best")
        if os.path.exists(best_dir):
            self.agent.load(best_dir)
            self._log("Loaded best model")
        else:
            self._log("No best model found")

    def load_checkpoint(self, episode: int):
        """Load specific checkpoint."""
        checkpoint_dir = os.path.join(self.config.save_dir, f"checkpoint_{episode}")
        if os.path.exists(checkpoint_dir):
            self.agent.load(checkpoint_dir)
            self._log(f"Loaded checkpoint from episode {episode}")
        else:
            self._log(f"Checkpoint {episode} not found")


def create_trainer(
    env,
    agent_type: str = "ppo",
    config: TrainerConfig = None,
    agent_config: Any = None
) -> Tuple[RLTrainer, Any]:
    """
    Factory function to create trainer with agent.

    Args:
        env: SchedulingEnv environment
        agent_type: "ppo" or "sac"
        config: Trainer configuration
        agent_config: Agent-specific configuration

    Returns:
        Tuple of (trainer, agent)
    """
    from uit_aps.scheduling.rl.agents.ppo import PPOAgent, PPOConfig
    from uit_aps.scheduling.rl.agents.sac import SACAgent, SACConfig

    # Get observation dimension
    obs_dim = env.obs_dim
    action_dim = env.action_dim

    # Create agent
    if agent_type.lower() == "ppo":
        agent_config = agent_config or PPOConfig()
        agent = PPOAgent(obs_dim, action_dim, agent_config)
    elif agent_type.lower() == "sac":
        agent_config = agent_config or SACConfig()
        agent = SACAgent(obs_dim, action_dim, agent_config)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

    # Create trainer
    if config is None:
        config = TrainerConfig(agent_type=agent_type)

    trainer = RLTrainer(env, agent, config)

    return trainer, agent


def train_from_ortools(
    scheduling_solution,
    machines: List[Dict],
    agent_type: str = "ppo",
    max_episodes: int = 500,
    save_dir: str = None
) -> Tuple[Any, Dict]:
    """
    Train RL agent starting from OR-Tools solution.

    Args:
        scheduling_solution: SchedulingSolution from Tier 1
        machines: List of machine configurations
        agent_type: "ppo" or "sac"
        max_episodes: Number of training episodes
        save_dir: Directory to save models

    Returns:
        Tuple of (trained_agent, training_summary)
    """
    from uit_aps.scheduling.rl.environment import SchedulingEnv, EnvironmentConfig

    # Convert solution to schedule format
    initial_schedule = []
    for op in scheduling_solution.operations:
        initial_schedule.append({
            "operation_id": op.operation_id,
            "job_id": op.job_id,
            "job_card": op.job_card_name,
            "operation_name": op.operation_name,
            "machine_id": op.machine_id,
            "start_time": op.start_time,
            "end_time": op.end_time,
            "duration_mins": op.duration_mins,
            "due_date": None,  # Would need to get from job
            "priority": 1
        })

    # Create environment
    env_config = EnvironmentConfig(
        max_operations=max(100, len(initial_schedule) + 20),
        max_machines=max(20, len(machines) + 5)
    )
    env = SchedulingEnv(env_config)

    # Create trainer with proper save directory
    # Try to use Frappe site path if available
    if not save_dir:
        try:
            import frappe
            save_dir = frappe.get_site_path("private", "files", "rl_models", agent_type, "best")
        except ImportError:
            save_dir = f"models/rl_{agent_type}"

    trainer_config = TrainerConfig(
        max_episodes=max_episodes,
        agent_type=agent_type,
        save_dir=save_dir
    )

    trainer, agent = create_trainer(env, agent_type, trainer_config)

    # Train
    summary = trainer.train(initial_schedule, machines)

    return agent, summary
