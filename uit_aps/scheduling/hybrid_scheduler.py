# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Hybrid APS Scheduler

Integrates multiple scheduling tiers:
- Tier 1: OR-Tools CP-SAT for optimal offline scheduling
- Tier 2: RL Agent (PPO/SAC) for real-time adjustments
- Tier 3: GNN Encoder for pattern learning (future)

The hybrid approach combines the strengths of each method:
- Optimization-based methods for finding globally optimal solutions
- Learning-based methods for handling dynamic disruptions
"""

import frappe
from frappe import _
from frappe.utils import now_datetime
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class SchedulingTier(Enum):
    """Available scheduling tiers."""
    TIER1_ORTOOLS = "Tier 1 - OR-Tools"
    TIER2_RL = "Tier 2 - RL Agent"
    TIER3_GNN = "Tier 3 - GNN"


@dataclass
class HybridSchedulerConfig:
    """Configuration for hybrid scheduler."""
    # Tier selection
    primary_tier: SchedulingTier = SchedulingTier.TIER1_ORTOOLS
    enable_rl_adjustments: bool = True
    rl_agent_type: str = "ppo"  # "ppo" or "sac"

    # Tier 1 settings
    ortools_time_limit: int = 300
    makespan_weight: float = 1.0
    tardiness_weight: float = 10.0

    # Tier 2 settings
    rl_adjustment_threshold: float = 0.7  # Confidence threshold
    max_rl_adjustments: int = 10
    rl_model_path: str = None

    # Disruption handling
    auto_handle_disruptions: bool = True
    disruption_response_delay_mins: int = 5


class HybridScheduler:
    """
    Hybrid scheduler combining OR-Tools and RL for production scheduling.

    Workflow:
    1. Run Tier 1 (OR-Tools) for initial optimal schedule
    2. Monitor for disruptions
    3. Use Tier 2 (RL) for real-time adjustments when disruptions occur
    4. (Future) Use Tier 3 (GNN) for pattern-based predictions
    """

    def __init__(self, config: HybridSchedulerConfig = None):
        """
        Initialize hybrid scheduler.

        Args:
            config: Scheduler configuration
        """
        self.config = config or HybridSchedulerConfig()
        self._rl_agent = None
        self._env = None

    def schedule(
        self,
        production_plan: str = None,
        work_orders: List[str] = None,
        scheduling_run: str = None
    ) -> Dict[str, Any]:
        """
        Run the full hybrid scheduling pipeline.

        Args:
            production_plan: ERPNext Production Plan name (auto-creates Work Orders and Job Cards)
            work_orders: List of Work Order names
            scheduling_run: Existing APS Scheduling Run to update

        Returns:
            dict with scheduling results
        """
        result = {
            "success": False,
            "tier1_result": None,
            "tier2_adjustments": [],
            "final_schedule": [],
            "metrics": {}
        }

        # Step 1: Run Tier 1 (OR-Tools)
        tier1_result = self._run_tier1(production_plan, work_orders, scheduling_run)
        result["tier1_result"] = tier1_result

        if not tier1_result.get("success"):
            result["message"] = tier1_result.get("message", "Tier 1 scheduling failed")
            return result

        result["success"] = True
        result["final_schedule"] = tier1_result.get("operations", [])
        result["metrics"] = {
            "makespan_mins": tier1_result.get("makespan_minutes", 0),
            "jobs_on_time": tier1_result.get("jobs_on_time", 0),
            "jobs_late": tier1_result.get("jobs_late", 0),
            "solver_status": tier1_result.get("status", "Unknown")
        }

        # Step 2: Initialize Tier 2 (RL) if enabled
        if self.config.enable_rl_adjustments:
            try:
                self._initialize_rl_agent()
                result["tier2_status"] = "initialized"
            except Exception as e:
                result["tier2_status"] = f"initialization_failed: {str(e)}"
                frappe.log_error(str(e), "Tier 2 RL Initialization Error")

        result["message"] = _("Hybrid scheduling completed successfully")

        return result

    def _run_tier1(
        self,
        production_plan: str = None,
        work_orders: List[str] = None,
        scheduling_run: str = None
    ) -> Dict[str, Any]:
        """Run Tier 1 OR-Tools scheduling."""
        from uit_aps.scheduling.api.scheduling_api import run_ortools_scheduling

        return run_ortools_scheduling(
            production_plan=production_plan,
            work_orders=",".join(work_orders) if work_orders else None,
            scheduling_run=scheduling_run,
            time_limit_seconds=self.config.ortools_time_limit,
            makespan_weight=self.config.makespan_weight,
            tardiness_weight=self.config.tardiness_weight
        )

    def _initialize_rl_agent(self):
        """Initialize Tier 2 RL agent."""
        from uit_aps.scheduling.rl.environment import SchedulingEnv, EnvironmentConfig
        from uit_aps.scheduling.rl.agents.ppo import PPOAgent, PPOConfig
        from uit_aps.scheduling.rl.agents.sac import SACAgent, SACConfig
        import os

        # Create environment
        env_config = EnvironmentConfig()
        self._env = SchedulingEnv(env_config)

        # Create agent
        obs_dim = self._env.obs_dim
        action_dim = self._env.action_dim

        if self.config.rl_agent_type.lower() == "sac":
            agent_config = SACConfig()
            self._rl_agent = SACAgent(obs_dim, action_dim, agent_config)
        else:
            agent_config = PPOConfig()
            self._rl_agent = PPOAgent(obs_dim, action_dim, agent_config)

        # Load saved model if available
        if self.config.rl_model_path and os.path.exists(self.config.rl_model_path):
            self._rl_agent.load(self.config.rl_model_path)
            self._rl_agent.eval()

    def handle_disruption(
        self,
        disruption_type: str,
        affected_resource: str,
        scheduling_run: str,
        current_schedule: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Handle a disruption using Tier 2 RL agent.

        Args:
            disruption_type: Type of disruption
            affected_resource: Affected machine or operation
            scheduling_run: Current scheduling run
            current_schedule: Current schedule state

        Returns:
            dict with adjustment recommendations
        """
        from uit_aps.scheduling.rl.realtime_api import handle_disruption

        return handle_disruption(
            disruption_type=disruption_type,
            affected_resource=affected_resource,
            scheduling_run=scheduling_run,
            duration_minutes=60
        )

    def get_rl_recommendation(
        self,
        scheduling_run: str,
        current_state: Dict = None
    ) -> Dict[str, Any]:
        """
        Get RL-based adjustment recommendation.

        Args:
            scheduling_run: Current scheduling run
            current_state: Current state information

        Returns:
            dict with recommendation
        """
        from uit_aps.scheduling.rl.realtime_api import get_realtime_adjustment

        return get_realtime_adjustment(
            scheduling_run=scheduling_run,
            agent_type=self.config.rl_agent_type
        )

    def apply_rl_adjustment(
        self,
        scheduling_run: str,
        action_type: int,
        target_operation: str,
        target_machine: str = None
    ) -> Dict[str, Any]:
        """
        Apply RL-recommended adjustment.

        Args:
            scheduling_run: Scheduling run name
            action_type: Action type ID
            target_operation: Target Job Card
            target_machine: Target workstation

        Returns:
            dict with result
        """
        from uit_aps.scheduling.rl.realtime_api import apply_rl_adjustment

        return apply_rl_adjustment(
            scheduling_run=scheduling_run,
            action_type=action_type,
            target_operation=target_operation,
            target_machine=target_machine
        )

    def train_rl_agent(
        self,
        scheduling_run: str,
        max_episodes: int = 100
    ) -> Dict[str, Any]:
        """
        Train RL agent on historical data.

        Args:
            scheduling_run: Reference scheduling run
            max_episodes: Training episodes

        Returns:
            Training summary
        """
        from uit_aps.scheduling.rl.realtime_api import train_rl_agent

        return train_rl_agent(
            scheduling_run=scheduling_run,
            agent_type=self.config.rl_agent_type,
            max_episodes=max_episodes
        )


@frappe.whitelist()
def run_hybrid_scheduling(
    production_plan: str = None,
    work_orders: str = None,
    scheduling_run: str = None,
    enable_rl: bool = True,
    rl_agent_type: str = "ppo",
    time_limit_seconds: int = 300
) -> dict:
    """
    Frappe API for hybrid scheduling.

    Args:
        production_plan: ERPNext Production Plan name (auto-creates Work Orders and Job Cards)
        work_orders: Comma-separated Work Order names (alternative)
        scheduling_run: Existing APS Scheduling Run name to update (if provided, uses this record)
        enable_rl: Enable Tier 2 RL adjustments
        rl_agent_type: "ppo" or "sac"
        time_limit_seconds: OR-Tools time limit

    Returns:
        dict with scheduling results
    """
    from frappe import _
    from frappe.utils import now_datetime

    # If scheduling_run is provided, use that record and get production_plan from it
    if scheduling_run:
        if not frappe.db.exists("APS Scheduling Run", scheduling_run):
            frappe.throw(_("APS Scheduling Run {0} not found").format(scheduling_run))

        # Get production_plan from the existing record
        production_plan = frappe.db.get_value("APS Scheduling Run", scheduling_run, "production_plan")

        # Update status to Running using frappe.db.set_value to avoid version conflicts
        # This bypasses document versioning and won't cause "Document has been modified" errors
        frappe.db.set_value(
            "APS Scheduling Run",
            scheduling_run,
            {
                "run_status": "Running",
                "run_date": now_datetime(),
                "executed_by": frappe.session.user
            },
            update_modified=False  # Don't update modified timestamp yet
        )
        frappe.db.commit()

    config = HybridSchedulerConfig(
        enable_rl_adjustments=enable_rl,
        rl_agent_type=rl_agent_type,
        ortools_time_limit=time_limit_seconds
    )

    scheduler = HybridScheduler(config)

    work_order_list = None
    if work_orders:
        work_order_list = [wo.strip() for wo in work_orders.split(",")]

    return scheduler.schedule(
        production_plan=production_plan,
        work_orders=work_order_list,
        scheduling_run=scheduling_run
    )


@frappe.whitelist()
def get_tier_status() -> dict:
    """
    Get status of all scheduling tiers.

    Returns:
        dict with tier availability and status
    """
    status = {
        "tier1_ortools": {
            "available": False,
            "status": "Unknown"
        },
        "tier2_rl": {
            "available": False,
            "status": "Unknown",
            "agents": []
        },
        "tier3_gnn": {
            "available": False,
            "status": "Unknown",
            "capabilities": []
        }
    }

    # Check Tier 1 (OR-Tools)
    try:
        from ortools.sat.python import cp_model
        status["tier1_ortools"]["available"] = True
        status["tier1_ortools"]["status"] = "Ready"
    except ImportError:
        status["tier1_ortools"]["status"] = "OR-Tools not installed"

    # Check Tier 2 (RL - PyTorch)
    try:
        import torch
        status["tier2_rl"]["available"] = True
        status["tier2_rl"]["status"] = f"Ready (PyTorch {torch.__version__})"
        status["tier2_rl"]["agents"] = ["PPO", "SAC"]

        # Check for saved models
        import os
        model_dir = frappe.get_site_path("private", "files", "rl_models")
        if os.path.exists(model_dir):
            for agent_type in ["ppo", "sac"]:
                agent_dir = os.path.join(model_dir, agent_type, "best")
                if os.path.exists(agent_dir):
                    status["tier2_rl"][f"{agent_type}_model"] = "Trained"

    except ImportError:
        status["tier2_rl"]["status"] = "PyTorch not installed"

    # Check Tier 3 (GNN - PyTorch)
    try:
        import torch
        status["tier3_gnn"]["available"] = True
        status["tier3_gnn"]["status"] = f"Ready (PyTorch {torch.__version__})"
        status["tier3_gnn"]["capabilities"] = [
            "bottleneck_prediction",
            "duration_prediction",
            "delay_prediction",
            "recommendations",
            "graph_encoding",
            "rl_integration"
        ]

        # Check for saved GNN models
        import os
        model_dir = frappe.get_site_path("private", "files", "gnn_models")
        if os.path.exists(model_dir):
            for model_type in ["bottleneck", "duration", "delay", "combined"]:
                model_path = os.path.join(model_dir, f"{model_type}_model.pt")
                if os.path.exists(model_path):
                    status["tier3_gnn"][f"{model_type}_model"] = "Trained"

    except ImportError:
        status["tier3_gnn"]["status"] = "PyTorch not installed"

    return status
