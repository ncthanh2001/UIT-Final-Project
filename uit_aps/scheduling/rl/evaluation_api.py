# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Frappe API endpoints for Phase 4: Evaluation & Deployment

Provides REST API for:
1. Running evaluations against heuristics
2. Managing model deployments
3. Monitoring production performance
4. A/B testing
"""

import frappe
from frappe import _
from typing import Dict, List, Optional, Any
import numpy as np


def convert_numpy_types(obj):
    """
    Recursively convert numpy types to native Python types for JSON serialization.

    Args:
        obj: Object to convert (can be dict, list, or scalar)

    Returns:
        Object with all numpy types converted to native Python types
    """
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


@frappe.whitelist()
def evaluate_agent(
    scheduling_run: str,
    agent_type: str = "ppo",
    num_scenarios: int = 20,
    compare_heuristics: str = "spt,edd,fcfs"
) -> Dict:
    """
    Evaluate RL agent against heuristics on test scenarios.

    Args:
        scheduling_run: Reference scheduling run
        agent_type: Type of agent (ppo, sac)
        num_scenarios: Number of test scenarios
        compare_heuristics: Comma-separated list of heuristics

    Returns:
        Evaluation results
    """
    try:
        from uit_aps.scheduling.rl.evaluation import (
            EvaluationConfig,
            ScenarioEvaluator,
            ComparativeAnalyzer,
            HeuristicType,
            run_full_evaluation
        )
        from uit_aps.scheduling.rl.environment import SchedulingEnv, EnvironmentConfig
        from uit_aps.scheduling.rl.agents.ppo import PPOAgent, PPOConfig
        from uit_aps.scheduling.rl.agents.sac import SACAgent, SACConfig
        from uit_aps.scheduling.data.erpnext_loader import load_scheduling_data

        # Load scheduling data
        schedule_data = load_scheduling_data(scheduling_run)
        if not schedule_data:
            return {"success": False, "error": "Failed to load scheduling data"}

        # Create environment
        env_config = EnvironmentConfig(
            max_operations=100,
            max_machines=20
        )
        env = SchedulingEnv(env_config)

        # Create agent
        if agent_type.lower() == "ppo":
            config = PPOConfig()
            agent = PPOAgent(env.obs_dim, env.action_dim, config)
        else:
            config = SACConfig()
            agent = SACAgent(env.obs_dim, env.action_dim, config)

        # Try to load trained model from Frappe site path
        model_path = frappe.get_site_path("private", "files", "rl_models", agent_type.lower(), "best")
        try:
            import os
            if os.path.exists(model_path):
                agent.load(model_path)
            else:
                frappe.log_error(f"Model path not found: {model_path}", "Evaluation - No Model")
        except Exception as e:
            frappe.log_error(f"No trained model found: {str(e)}", "Evaluation - Load Error")

        # Configure evaluation
        eval_config = EvaluationConfig(
            num_scenarios=int(num_scenarios),
            compare_heuristics=compare_heuristics.split(","),
            output_dir=f"evaluation_results/{scheduling_run}"
        )

        # Run evaluation
        analysis = run_full_evaluation(
            env=env,
            agent=agent,
            initial_schedule=schedule_data.get("operations", []),
            machines=schedule_data.get("machines", []),
            config=eval_config
        )

        # Convert numpy types to native Python types for JSON serialization
        analysis = convert_numpy_types(analysis)

        return {
            "success": True,
            "scheduling_run": scheduling_run,
            "agent_type": agent_type,
            "analysis": analysis
        }

    except ImportError as e:
        return {
            "success": False,
            "error": f"Missing dependency: {str(e)}",
            "message": "Install required packages: pip install numpy"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Evaluation Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_heuristic_schedule(
    scheduling_run: str,
    heuristic: str = "edd"
) -> Dict:
    """
    Get schedule using a specific heuristic.

    Args:
        scheduling_run: Reference scheduling run
        heuristic: Heuristic to use (spt, edd, fcfs, lpt, cr, slack)

    Returns:
        Heuristic-generated schedule
    """
    try:
        from uit_aps.scheduling.rl.evaluation import HeuristicScheduler, HeuristicType
        from uit_aps.scheduling.data.erpnext_loader import load_scheduling_data

        # Load data
        schedule_data = load_scheduling_data(scheduling_run)
        if not schedule_data:
            return {"success": False, "error": "Failed to load scheduling data"}

        # Parse heuristic type
        try:
            heuristic_type = HeuristicType(heuristic.lower())
        except ValueError:
            return {
                "success": False,
                "error": f"Unknown heuristic: {heuristic}",
                "available": [h.value for h in HeuristicType]
            }

        # Generate schedule
        scheduled_ops = HeuristicScheduler.schedule(
            operations=schedule_data.get("operations", []),
            machines=schedule_data.get("machines", []),
            heuristic=heuristic_type,
            current_time=0
        )

        # Calculate metrics
        makespan = max((op.get("end_time", 0) for op in scheduled_ops), default=0)
        total_tardiness = sum(
            max(0, op.get("end_time", 0) - op.get("due_date", float("inf")))
            for op in scheduled_ops
            if op.get("due_date")
        )

        # Convert numpy types to native Python types for JSON serialization
        scheduled_ops = convert_numpy_types(scheduled_ops)

        return {
            "success": True,
            "heuristic": heuristic,
            "schedule": scheduled_ops,
            "metrics": {
                "makespan": float(makespan) if makespan else 0,
                "total_tardiness": float(total_tardiness) if total_tardiness else 0,
                "num_operations": len(scheduled_ops)
            }
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Heuristic Scheduling Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_deployment_status() -> Dict:
    """
    Get current model deployment status.

    Returns:
        Deployment status information
    """
    try:
        from uit_aps.scheduling.rl.deployment import ModelRegistry

        registry = ModelRegistry()
        versions = registry.list_versions()

        return {
            "success": True,
            "active_version": registry.active_version,
            "active_info": registry.get_version_info(),
            "versions": versions,
            "total_versions": len(versions)
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Deployment Status Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def deploy_model(
    version_id: str,
    shadow_mode: bool = True
) -> Dict:
    """
    Deploy a model version.

    Args:
        version_id: Version to deploy
        shadow_mode: Start in shadow mode (default True)

    Returns:
        Deployment result
    """
    try:
        from uit_aps.scheduling.rl.deployment import ModelRegistry

        registry = ModelRegistry()
        shadow = shadow_mode in [True, "true", "True", 1, "1"]

        success = registry.deploy(version_id, shadow_mode=shadow)

        if success:
            return {
                "success": True,
                "message": f"Deployed version {version_id}",
                "shadow_mode": shadow,
                "active_version": registry.active_version
            }
        else:
            return {
                "success": False,
                "error": f"Failed to deploy version {version_id}"
            }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Model Deployment Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def promote_shadow_model(version_id: str) -> Dict:
    """
    Promote a shadow model to active.

    Args:
        version_id: Version to promote

    Returns:
        Promotion result
    """
    try:
        from uit_aps.scheduling.rl.deployment import ModelRegistry

        registry = ModelRegistry()
        success = registry.promote_to_active(version_id)

        if success:
            return {
                "success": True,
                "message": f"Promoted version {version_id} to active",
                "active_version": registry.active_version
            }
        else:
            return {
                "success": False,
                "error": "Failed to promote. Version may not be in shadow mode."
            }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Model Promotion Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def rollback_model(to_version: str = None) -> Dict:
    """
    Rollback to a previous model version.

    Args:
        to_version: Specific version to rollback to (optional)

    Returns:
        Rollback result
    """
    try:
        from uit_aps.scheduling.rl.deployment import ModelRegistry

        registry = ModelRegistry()
        previous_active = registry.active_version

        success = registry.rollback(to_version)

        if success:
            return {
                "success": True,
                "message": "Rollback successful",
                "previous_version": previous_active,
                "current_version": registry.active_version
            }
        else:
            return {
                "success": False,
                "error": "No previous version to rollback to"
            }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Model Rollback Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def register_trained_model(
    agent_type: str,
    model_path: str,
    training_summary: str = None
) -> Dict:
    """
    Register a newly trained model.

    Args:
        agent_type: Type of agent (ppo, sac)
        model_path: Path to trained model
        training_summary: JSON string of training summary

    Returns:
        Registration result
    """
    try:
        import json
        from uit_aps.scheduling.rl.deployment import ModelRegistry

        registry = ModelRegistry()

        # Parse training summary
        training_config = {}
        eval_metrics = {}
        if training_summary:
            try:
                summary = json.loads(training_summary)
                training_config = summary.get("config", {})
                eval_metrics = summary.get("metrics", {})
            except json.JSONDecodeError:
                pass

        version_id = registry.register_model(
            agent_type=agent_type,
            model_path=model_path,
            training_config=training_config,
            evaluation_metrics=eval_metrics
        )

        return {
            "success": True,
            "version_id": version_id,
            "message": f"Registered model as {version_id}"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Model Registration Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_monitoring_summary(last_n: int = 100) -> Dict:
    """
    Get production monitoring summary.

    Args:
        last_n: Number of recent entries to analyze

    Returns:
        Monitoring summary
    """
    try:
        from uit_aps.scheduling.rl.evaluation import ProductionMonitor, MonitoringConfig

        config = MonitoringConfig(log_dir="logs/production")
        monitor = ProductionMonitor(config)

        summary = monitor.get_summary(int(last_n))

        # Convert numpy types to native Python types for JSON serialization
        summary = convert_numpy_types(summary)

        return {
            "success": True,
            "summary": summary
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Monitoring Summary Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def export_evaluation_report(scheduling_run: str = None) -> Dict:
    """
    Export evaluation report.

    Args:
        scheduling_run: Optional scheduling run reference

    Returns:
        Report file path
    """
    try:
        from uit_aps.scheduling.rl.evaluation import ProductionMonitor, MonitoringConfig

        config = MonitoringConfig(log_dir="logs/production")
        monitor = ProductionMonitor(config)

        report_path = monitor.export_report()

        return {
            "success": True,
            "report_path": report_path,
            "message": f"Report exported to {report_path}"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Report Export Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def compare_with_ortools(scheduling_run: str) -> Dict:
    """
    Compare RL agent performance with OR-Tools solution.

    Args:
        scheduling_run: Reference scheduling run

    Returns:
        Comparison results
    """
    try:
        from uit_aps.scheduling.data.erpnext_loader import load_scheduling_data

        # Load scheduling run data
        run_doc = frappe.get_doc("APS Scheduling Run", scheduling_run)

        # Get OR-Tools results from the run
        ortools_metrics = {
            "makespan_minutes": run_doc.makespan_minutes or 0,
            "total_tardiness_minutes": run_doc.total_tardiness_minutes or 0,
            "jobs_on_time": run_doc.jobs_on_time or 0,
            "total_late_jobs": run_doc.total_late_jobs or 0,
            "solve_time_seconds": run_doc.solve_time_seconds or 0
        }

        # TODO: Get RL metrics from the latest RL run
        rl_metrics = {
            "makespan_minutes": 0,
            "total_tardiness_minutes": 0,
            "jobs_on_time": 0,
            "total_late_jobs": 0,
            "inference_time_ms": 0
        }

        # Calculate comparison
        comparison = {
            "makespan_improvement": float(
                (ortools_metrics["makespan_minutes"] - rl_metrics["makespan_minutes"])
                / max(ortools_metrics["makespan_minutes"], 1) * 100
            ),
            "tardiness_improvement": float(
                (ortools_metrics["total_tardiness_minutes"] - rl_metrics["total_tardiness_minutes"])
                / max(ortools_metrics["total_tardiness_minutes"], 1) * 100
            ),
            "speed_improvement": float(
                ortools_metrics["solve_time_seconds"] * 1000 / max(rl_metrics["inference_time_ms"], 1)
            )
        }

        # Convert numpy types to native Python types for JSON serialization
        ortools_metrics = convert_numpy_types(ortools_metrics)
        rl_metrics = convert_numpy_types(rl_metrics)
        comparison = convert_numpy_types(comparison)

        return {
            "success": True,
            "ortools": ortools_metrics,
            "rl_agent": rl_metrics,
            "comparison": comparison,
            "recommendation": "RL Agent" if comparison["tardiness_improvement"] > 0 else "OR-Tools"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "OR-Tools Comparison Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_phase4_status() -> Dict:
    """
    Get Phase 4 (Evaluation & Deployment) implementation status.

    Returns:
        Status of all Phase 4 components
    """
    components = {
        "evaluation": {
            "scenario_evaluator": True,
            "heuristic_comparison": True,
            "statistical_analysis": True
        },
        "deployment": {
            "model_registry": True,
            "version_management": True,
            "shadow_mode": True,
            "rollback": True,
            "ab_testing": True
        },
        "monitoring": {
            "decision_logging": True,
            "performance_tracking": True,
            "alerting": True,
            "report_export": True
        },
        "heuristics": {
            "spt": True,  # Shortest Processing Time
            "lpt": True,  # Longest Processing Time
            "edd": True,  # Earliest Due Date
            "fcfs": True,  # First Come First Served
            "cr": True,   # Critical Ratio
            "slack": True  # Minimum Slack
        }
    }

    return {
        "success": True,
        "phase": "Phase 4: Evaluation & Deployment",
        "status": "Implemented",
        "components": components,
        "api_endpoints": [
            "/api/method/uit_aps.scheduling.rl.evaluation_api.evaluate_agent",
            "/api/method/uit_aps.scheduling.rl.evaluation_api.get_heuristic_schedule",
            "/api/method/uit_aps.scheduling.rl.evaluation_api.get_deployment_status",
            "/api/method/uit_aps.scheduling.rl.evaluation_api.deploy_model",
            "/api/method/uit_aps.scheduling.rl.evaluation_api.rollback_model",
            "/api/method/uit_aps.scheduling.rl.evaluation_api.get_monitoring_summary"
        ]
    }
