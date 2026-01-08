# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Training Logger for RL Agents

Provides real-time logging of training progress to Frappe database,
allowing users to monitor training through the UI.
"""

import frappe
from frappe.utils import now_datetime
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import time


class TrainingLogger:
    """
    Logger for RL training that saves progress to APS RL Training Log.

    Usage:
        logger = TrainingLogger(scheduling_run="SR-001", agent_type="ppo")
        logger.start_training(max_episodes=100, config={...})

        for episode in range(max_episodes):
            # ... training code ...
            logger.log_episode(episode, reward, loss, metrics)

        logger.complete_training(model_path="path/to/model")
    """

    def __init__(self, scheduling_run: str = None, agent_type: str = "ppo"):
        """
        Initialize training logger.

        Args:
            scheduling_run: Reference to APS Scheduling Run
            agent_type: Type of agent (ppo, sac)
        """
        self.scheduling_run = scheduling_run
        self.agent_type = agent_type
        self.log_name = None
        self.start_time = None
        self.reward_history: List[float] = []
        self.loss_history: List[float] = []
        self.best_reward = float('-inf')
        self.best_makespan = float('inf')
        self.best_tardiness = float('inf')
        self.total_steps = 0
        self._last_update_time = 0
        self._update_interval = 2  # Update DB every 2 seconds

    def start_training(
        self,
        max_episodes: int,
        config: Dict[str, Any] = None
    ) -> str:
        """
        Start a new training session and create log entry.

        Args:
            max_episodes: Maximum number of episodes
            config: Training configuration

        Returns:
            Name of the created training log
        """
        config = config or {}
        self.start_time = time.time()

        # Create training log document
        log_doc = frappe.get_doc({
            "doctype": "APS RL Training Log",
            "scheduling_run": self.scheduling_run,
            "agent_type": self.agent_type,
            "training_status": "Running",
            "started_at": now_datetime(),
            "max_episodes": max_episodes,
            "learning_rate": config.get("learning_rate", 0.0003),
            "gamma": config.get("gamma", 0.99),
            "hidden_sizes": json.dumps(config.get("hidden_sizes", [256, 256])),
            "batch_size": config.get("batch_size", 64),
            "current_episode": 0,
            "progress_percentage": 0,
            "obs_dim": config.get("obs_dim", 0),
            "action_dim": config.get("action_dim", 7)
        })
        log_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        self.log_name = log_doc.name
        return self.log_name

    def log_episode(
        self,
        episode: int,
        reward: float,
        loss: float = None,
        metrics: Dict[str, Any] = None
    ):
        """
        Log a single episode result.

        Args:
            episode: Episode number (0-indexed)
            reward: Total reward for the episode
            loss: Training loss (optional)
            metrics: Additional metrics like makespan, tardiness
        """
        if not self.log_name:
            return

        metrics = metrics or {}

        # Update history
        self.reward_history.append(float(reward))
        if loss is not None:
            self.loss_history.append(float(loss))

        # Track best values
        if reward > self.best_reward:
            self.best_reward = reward

        makespan = metrics.get("makespan", float('inf'))
        tardiness = metrics.get("tardiness", float('inf'))

        if makespan < self.best_makespan:
            self.best_makespan = makespan
        if tardiness < self.best_tardiness:
            self.best_tardiness = tardiness

        self.total_steps += metrics.get("steps", 0)

        # Throttle database updates
        current_time = time.time()
        if current_time - self._last_update_time >= self._update_interval:
            self._update_database(episode + 1)
            self._last_update_time = current_time

    def _update_database(self, current_episode: int):
        """Update the database with current progress."""
        if not self.log_name:
            return

        try:
            elapsed_time = time.time() - self.start_time
            max_episodes = frappe.db.get_value(
                "APS RL Training Log", self.log_name, "max_episodes"
            ) or 100

            # Calculate metrics
            progress = (current_episode / max_episodes) * 100
            eps_per_sec = current_episode / max(elapsed_time, 1)
            remaining_episodes = max_episodes - current_episode
            est_remaining_secs = remaining_episodes / max(eps_per_sec, 0.01)

            # Format time remaining
            if est_remaining_secs > 3600:
                est_remaining = f"{est_remaining_secs/3600:.1f} hours"
            elif est_remaining_secs > 60:
                est_remaining = f"{est_remaining_secs/60:.1f} mins"
            else:
                est_remaining = f"{est_remaining_secs:.0f} secs"

            # Calculate average reward for last 100 episodes
            avg_reward_100 = 0
            if self.reward_history:
                last_100 = self.reward_history[-100:]
                avg_reward_100 = sum(last_100) / len(last_100)

            # Calculate average loss
            avg_loss = 0
            if self.loss_history:
                avg_loss = sum(self.loss_history[-100:]) / len(self.loss_history[-100:])

            # Update document
            updates = {
                "current_episode": current_episode,
                "progress_percentage": progress,
                "episodes_per_second": round(eps_per_sec, 2),
                "estimated_time_remaining": est_remaining,
                "best_reward": round(self.best_reward, 4),
                "avg_reward_last_100": round(avg_reward_100, 4),
                "total_steps": self.total_steps,
                "avg_loss": round(avg_loss, 6) if avg_loss else None,
                # Only store last 500 points for chart
                "reward_history": json.dumps(self.reward_history[-500:]),
                "loss_history": json.dumps(self.loss_history[-500:]) if self.loss_history else None
            }

            if self.best_makespan != float('inf'):
                updates["best_makespan"] = round(self.best_makespan, 2)
            if self.best_tardiness != float('inf'):
                updates["best_tardiness"] = round(self.best_tardiness, 2)

            frappe.db.set_value("APS RL Training Log", self.log_name, updates)
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(str(e), "Training Logger Update Error")

    def complete_training(
        self,
        model_path: str = None,
        model_size_mb: float = None,
        final_metrics: Dict[str, Any] = None
    ):
        """
        Mark training as completed.

        Args:
            model_path: Path where model is saved
            model_size_mb: Size of saved model in MB
            final_metrics: Final training metrics
        """
        if not self.log_name:
            return

        final_metrics = final_metrics or {}
        elapsed_time = time.time() - self.start_time
        max_episodes = frappe.db.get_value(
            "APS RL Training Log", self.log_name, "max_episodes"
        ) or 100

        updates = {
            "training_status": "Completed",
            "completed_at": now_datetime(),
            "total_duration_seconds": round(elapsed_time, 2),
            "current_episode": max_episodes,
            "progress_percentage": 100,
            "model_path": model_path,
            "model_size_mb": model_size_mb,
            "reward_history": json.dumps(self.reward_history[-500:]),
            "loss_history": json.dumps(self.loss_history[-500:]) if self.loss_history else None
        }

        # Add any final metrics
        if "obs_dim" in final_metrics:
            updates["obs_dim"] = final_metrics["obs_dim"]
        if "action_dim" in final_metrics:
            updates["action_dim"] = final_metrics["action_dim"]

        frappe.db.set_value("APS RL Training Log", self.log_name, updates)
        frappe.db.commit()

    def fail_training(self, error_message: str):
        """
        Mark training as failed.

        Args:
            error_message: Error message
        """
        if not self.log_name:
            return

        elapsed_time = time.time() - self.start_time if self.start_time else 0

        frappe.db.set_value("APS RL Training Log", self.log_name, {
            "training_status": "Failed",
            "completed_at": now_datetime(),
            "total_duration_seconds": round(elapsed_time, 2)
        })
        frappe.db.commit()

        # Log error
        frappe.log_error(error_message, f"RL Training Failed: {self.log_name}")

    def cancel_training(self):
        """Mark training as cancelled."""
        if not self.log_name:
            return

        elapsed_time = time.time() - self.start_time if self.start_time else 0

        frappe.db.set_value("APS RL Training Log", self.log_name, {
            "training_status": "Cancelled",
            "completed_at": now_datetime(),
            "total_duration_seconds": round(elapsed_time, 2)
        })
        frappe.db.commit()


def get_training_progress(training_log: str) -> Dict[str, Any]:
    """
    Get current training progress.

    Args:
        training_log: Name of APS RL Training Log

    Returns:
        Dict with training progress info
    """
    doc = frappe.get_doc("APS RL Training Log", training_log)

    return {
        "status": doc.training_status,
        "current_episode": doc.current_episode,
        "max_episodes": doc.max_episodes,
        "progress_percentage": doc.progress_percentage,
        "episodes_per_second": doc.episodes_per_second,
        "estimated_time_remaining": doc.estimated_time_remaining,
        "best_reward": doc.best_reward,
        "avg_reward_last_100": doc.avg_reward_last_100,
        "best_makespan": doc.best_makespan,
        "best_tardiness": doc.best_tardiness,
        "total_steps": doc.total_steps,
        "started_at": doc.started_at,
        "elapsed_seconds": doc.total_duration_seconds
    }


def get_all_training_logs(
    scheduling_run: str = None,
    agent_type: str = None,
    status: str = None,
    limit: int = 20
) -> List[Dict]:
    """
    Get all training logs with optional filters.

    Args:
        scheduling_run: Filter by scheduling run
        agent_type: Filter by agent type
        status: Filter by status
        limit: Maximum number of records

    Returns:
        List of training log summaries
    """
    filters = {}
    if scheduling_run:
        filters["scheduling_run"] = scheduling_run
    if agent_type:
        filters["agent_type"] = agent_type
    if status:
        filters["training_status"] = status

    logs = frappe.get_all(
        "APS RL Training Log",
        filters=filters,
        fields=[
            "name", "scheduling_run", "agent_type", "training_status",
            "current_episode", "max_episodes", "progress_percentage",
            "best_reward", "best_makespan", "started_at", "completed_at",
            "total_duration_seconds"
        ],
        order_by="creation desc",
        limit=limit
    )

    return logs
