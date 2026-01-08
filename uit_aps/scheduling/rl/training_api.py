# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Frappe API endpoints for RL Training

Provides REST API for:
1. Starting training jobs
2. Monitoring training progress
3. Managing training history
"""

import frappe
from frappe import _
from frappe.utils import now_datetime
from typing import Dict, List, Any
import json


@frappe.whitelist()
def start_training(
    scheduling_run: str,
    agent_type: str = "ppo",
    max_episodes: int = 100,
    learning_rate: float = 0.0003,
    gamma: float = 0.99,
    run_in_background: bool = True
) -> Dict:
    """
    Start RL agent training.

    Args:
        scheduling_run: APS Scheduling Run to train from
        agent_type: Type of agent (ppo, sac)
        max_episodes: Number of training episodes
        learning_rate: Learning rate
        gamma: Discount factor
        run_in_background: Run as background job

    Returns:
        Training job info
    """
    try:
        # Validate scheduling run exists and is completed
        if not frappe.db.exists("APS Scheduling Run", scheduling_run):
            return {"success": False, "error": _("Scheduling run not found")}

        run_status = frappe.db.get_value("APS Scheduling Run", scheduling_run, "run_status")
        if run_status != "Completed":
            return {
                "success": False,
                "error": _("Scheduling run must be completed before training")
            }

        # Check if training is already running for this run
        existing = frappe.db.exists("APS RL Training Log", {
            "scheduling_run": scheduling_run,
            "training_status": "Running"
        })
        if existing:
            return {
                "success": False,
                "error": _("Training already in progress for this scheduling run"),
                "training_log": existing
            }

        if run_in_background:
            # Enqueue background job
            from frappe.utils.background_jobs import enqueue

            job = enqueue(
                "uit_aps.scheduling.rl.training_api._run_training_job",
                queue="long",
                timeout=3600,  # 1 hour timeout
                scheduling_run=scheduling_run,
                agent_type=agent_type,
                max_episodes=int(max_episodes),
                learning_rate=float(learning_rate),
                gamma=float(gamma)
            )

            return {
                "success": True,
                "message": _("Training job started in background"),
                "job_id": job.id if hasattr(job, 'id') else None,
                "scheduling_run": scheduling_run,
                "agent_type": agent_type
            }
        else:
            # Run synchronously (for testing)
            result = _run_training_job(
                scheduling_run=scheduling_run,
                agent_type=agent_type,
                max_episodes=int(max_episodes),
                learning_rate=float(learning_rate),
                gamma=float(gamma)
            )
            return result

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Training Start Error")
        return {"success": False, "error": str(e)}


def _run_training_job(
    scheduling_run: str,
    agent_type: str,
    max_episodes: int,
    learning_rate: float,
    gamma: float
) -> Dict:
    """
    Internal function to run training job.
    Called either directly or as background job.
    """
    from uit_aps.scheduling.rl.training_logger import TrainingLogger
    from uit_aps.scheduling.rl.environment import SchedulingEnv, EnvironmentConfig
    from uit_aps.scheduling.data.erpnext_loader import load_scheduling_data
    import os

    logger = TrainingLogger(scheduling_run=scheduling_run, agent_type=agent_type)

    try:
        # Load scheduling data
        schedule_data = load_scheduling_data(scheduling_run)
        if not schedule_data:
            logger.fail_training("Failed to load scheduling data")
            return {"success": False, "error": "Failed to load scheduling data"}

        # Create environment
        env_config = EnvironmentConfig(
            max_operations=100,
            max_machines=20
        )
        env = SchedulingEnv(env_config)

        # Get observation dimension
        obs_dim = env.obs_dim
        action_dim = env.action_dim

        # Create agent
        if agent_type.lower() == "ppo":
            from uit_aps.scheduling.rl.agents.ppo import PPOAgent, PPOConfig

            config = PPOConfig(
                learning_rate=learning_rate,
                gamma=gamma,
                hidden_sizes=[256, 256]
            )
            agent = PPOAgent(obs_dim, action_dim, config)
        else:
            from uit_aps.scheduling.rl.agents.sac import SACAgent, SACConfig

            config = SACConfig(
                learning_rate=learning_rate,
                gamma=gamma,
                hidden_sizes=[256, 256]
            )
            agent = SACAgent(obs_dim, action_dim, config)

        # Start logging
        training_config = {
            "learning_rate": learning_rate,
            "gamma": gamma,
            "hidden_sizes": [256, 256],
            "batch_size": 64,
            "obs_dim": obs_dim,
            "action_dim": action_dim
        }
        log_name = logger.start_training(max_episodes, training_config)

        # Training loop
        best_reward = float('-inf')
        for episode in range(max_episodes):
            # Reset environment with schedule data
            state = env.reset(
                operations=schedule_data.get("operations", []),
                machines=schedule_data.get("machines", [])
            )

            episode_reward = 0
            episode_steps = 0
            done = False

            while not done:
                # Select action
                action, info = agent.select_action(state)

                # Take step
                next_state, reward, done, step_info = env.step(action)

                # Store transition for learning
                agent.store_transition(state, action, reward, next_state, done)

                episode_reward += reward
                episode_steps += 1
                state = next_state

                # Prevent infinite loops
                if episode_steps > 1000:
                    break

            # Update agent
            loss = agent.update()

            # Get metrics from environment
            metrics = {
                "steps": episode_steps,
                "makespan": env.get_makespan(),
                "tardiness": env.get_total_tardiness()
            }

            # Log episode
            logger.log_episode(episode, episode_reward, loss, metrics)

            # Track best reward for saving
            if episode_reward > best_reward:
                best_reward = episode_reward

        # Save model
        save_dir = frappe.get_site_path("private", "files", "rl_models", agent_type, "best")
        os.makedirs(save_dir, exist_ok=True)
        agent.save(save_dir)

        # Get model size
        model_size = 0
        for f in os.listdir(save_dir):
            model_size += os.path.getsize(os.path.join(save_dir, f))
        model_size_mb = model_size / (1024 * 1024)

        # Complete training
        logger.complete_training(
            model_path=save_dir,
            model_size_mb=round(model_size_mb, 2),
            final_metrics={"obs_dim": obs_dim, "action_dim": action_dim}
        )

        return {
            "success": True,
            "training_log": log_name,
            "model_path": save_dir,
            "best_reward": best_reward,
            "total_episodes": max_episodes
        }

    except Exception as e:
        logger.fail_training(str(e))
        frappe.log_error(frappe.get_traceback(), "Training Job Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_training_progress(training_log: str) -> Dict:
    """
    Get current training progress.

    Args:
        training_log: Name of APS RL Training Log

    Returns:
        Training progress info
    """
    try:
        from uit_aps.scheduling.rl.training_logger import get_training_progress as _get_progress
        return {"success": True, "progress": _get_progress(training_log)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_training_history(
    scheduling_run: str = None,
    agent_type: str = None,
    limit: int = 20
) -> Dict:
    """
    Get training history.

    Args:
        scheduling_run: Filter by scheduling run
        agent_type: Filter by agent type
        limit: Maximum records

    Returns:
        List of training logs
    """
    try:
        from uit_aps.scheduling.rl.training_logger import get_all_training_logs

        logs = get_all_training_logs(
            scheduling_run=scheduling_run,
            agent_type=agent_type,
            limit=int(limit)
        )

        return {"success": True, "logs": logs, "total": len(logs)}

    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def cancel_training(training_log: str) -> Dict:
    """
    Cancel a running training job.

    Args:
        training_log: Name of APS RL Training Log

    Returns:
        Cancellation result
    """
    try:
        status = frappe.db.get_value("APS RL Training Log", training_log, "training_status")

        if status != "Running":
            return {
                "success": False,
                "error": _("Training is not running. Current status: {0}").format(status)
            }

        frappe.db.set_value("APS RL Training Log", training_log, {
            "training_status": "Cancelled",
            "completed_at": now_datetime()
        })
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Training cancelled"),
            "training_log": training_log
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_reward_chart_data(training_log: str) -> Dict:
    """
    Get reward history data for charting.

    Args:
        training_log: Name of APS RL Training Log

    Returns:
        Chart data
    """
    try:
        reward_history = frappe.db.get_value(
            "APS RL Training Log", training_log, "reward_history"
        )

        if not reward_history:
            return {"success": True, "data": [], "labels": []}

        rewards = json.loads(reward_history)

        # Downsample if too many points
        if len(rewards) > 100:
            step = len(rewards) // 100
            rewards = rewards[::step]

        labels = list(range(1, len(rewards) + 1))

        return {
            "success": True,
            "data": rewards,
            "labels": labels,
            "min": min(rewards) if rewards else 0,
            "max": max(rewards) if rewards else 0,
            "avg": sum(rewards) / len(rewards) if rewards else 0
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def compare_training_runs(training_logs: str) -> Dict:
    """
    Compare multiple training runs.

    Args:
        training_logs: Comma-separated list of training log names

    Returns:
        Comparison data
    """
    try:
        log_names = [l.strip() for l in training_logs.split(",")]

        comparisons = []
        for log_name in log_names:
            doc = frappe.get_doc("APS RL Training Log", log_name)
            comparisons.append({
                "name": log_name,
                "agent_type": doc.agent_type,
                "max_episodes": doc.max_episodes,
                "best_reward": doc.best_reward,
                "avg_reward_last_100": doc.avg_reward_last_100,
                "best_makespan": doc.best_makespan,
                "best_tardiness": doc.best_tardiness,
                "total_duration_seconds": doc.total_duration_seconds,
                "training_status": doc.training_status
            })

        return {"success": True, "comparisons": comparisons}

    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_model_info(agent_type: str = "ppo") -> Dict:
    """
    Get information about the currently deployed model.

    Args:
        agent_type: Type of agent

    Returns:
        Model info
    """
    try:
        import os

        model_dir = frappe.get_site_path("private", "files", "rl_models", agent_type, "best")

        if not os.path.exists(model_dir):
            return {
                "success": True,
                "exists": False,
                "message": _("No trained model found for {0}").format(agent_type)
            }

        # Get model files
        files = []
        total_size = 0
        for f in os.listdir(model_dir):
            fpath = os.path.join(model_dir, f)
            size = os.path.getsize(fpath)
            files.append({"name": f, "size_bytes": size})
            total_size += size

        # Try to load config
        config = {}
        config_file = os.path.join(model_dir, f"{agent_type}_config.json")
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = json.load(f)

        # Get last training log for this model
        last_training = frappe.get_all(
            "APS RL Training Log",
            filters={
                "agent_type": agent_type,
                "training_status": "Completed",
                "model_path": model_dir
            },
            fields=["name", "completed_at", "best_reward", "max_episodes"],
            order_by="completed_at desc",
            limit=1
        )

        return {
            "success": True,
            "exists": True,
            "agent_type": agent_type,
            "model_path": model_dir,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "files": files,
            "config": config,
            "last_training": last_training[0] if last_training else None
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
