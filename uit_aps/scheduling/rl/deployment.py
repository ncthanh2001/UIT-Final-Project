# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Phase 4: Deployment Module

Handles production deployment of trained RL agents:
1. Model serving and inference
2. A/B testing between agents/heuristics
3. Rollback capabilities
4. Version management
"""

import os
import json
import shutil
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from enum import Enum


class DeploymentStatus(Enum):
    """Deployment status."""
    PENDING = "pending"
    ACTIVE = "active"
    SHADOW = "shadow"  # Running but not making decisions
    ROLLBACK = "rollback"
    RETIRED = "retired"


@dataclass
class ModelVersion:
    """Represents a versioned model."""
    version_id: str
    agent_type: str
    created_at: str
    model_path: str
    training_config: Dict
    evaluation_metrics: Dict
    status: DeploymentStatus = DeploymentStatus.PENDING
    deployment_history: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "version_id": self.version_id,
            "agent_type": self.agent_type,
            "created_at": self.created_at,
            "model_path": self.model_path,
            "training_config": self.training_config,
            "evaluation_metrics": self.evaluation_metrics,
            "status": self.status.value,
            "deployment_history": self.deployment_history
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ModelVersion":
        """Create from dictionary."""
        return cls(
            version_id=data["version_id"],
            agent_type=data["agent_type"],
            created_at=data["created_at"],
            model_path=data["model_path"],
            training_config=data.get("training_config", {}),
            evaluation_metrics=data.get("evaluation_metrics", {}),
            status=DeploymentStatus(data.get("status", "pending")),
            deployment_history=data.get("deployment_history", [])
        )


@dataclass
class DeploymentConfig:
    """Configuration for deployment."""
    models_dir: str = "models/production"
    versions_file: str = "model_versions.json"
    max_versions_to_keep: int = 5
    enable_ab_testing: bool = False
    ab_test_ratio: float = 0.1  # 10% traffic to new model
    shadow_mode_duration_hours: int = 24
    auto_rollback_threshold: float = 0.8  # Rollback if performance drops 20%


class ModelRegistry:
    """
    Manages model versions and deployment lifecycle.
    """

    def __init__(self, config: DeploymentConfig = None):
        """Initialize registry."""
        self.config = config or DeploymentConfig()
        self.versions: Dict[str, ModelVersion] = {}
        self.active_version: Optional[str] = None

        os.makedirs(self.config.models_dir, exist_ok=True)
        self._load_versions()

    def _load_versions(self):
        """Load versions from file."""
        versions_path = os.path.join(self.config.models_dir, self.config.versions_file)
        if os.path.exists(versions_path):
            with open(versions_path, "r") as f:
                data = json.load(f)
                for v in data.get("versions", []):
                    version = ModelVersion.from_dict(v)
                    self.versions[version.version_id] = version
                self.active_version = data.get("active_version")

    def _save_versions(self):
        """Save versions to file."""
        versions_path = os.path.join(self.config.models_dir, self.config.versions_file)
        data = {
            "versions": [v.to_dict() for v in self.versions.values()],
            "active_version": self.active_version,
            "updated_at": datetime.now().isoformat()
        }
        with open(versions_path, "w") as f:
            json.dump(data, f, indent=2)

    def register_model(
        self,
        agent_type: str,
        model_path: str,
        training_config: Dict = None,
        evaluation_metrics: Dict = None
    ) -> str:
        """
        Register a new model version.

        Args:
            agent_type: Type of agent (ppo, sac)
            model_path: Path to trained model
            training_config: Training configuration used
            evaluation_metrics: Evaluation results

        Returns:
            Version ID
        """
        # Generate version ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_id = f"v_{agent_type}_{timestamp}"

        # Copy model to production directory
        dest_path = os.path.join(self.config.models_dir, version_id)
        if os.path.isdir(model_path):
            shutil.copytree(model_path, dest_path)
        else:
            os.makedirs(dest_path, exist_ok=True)
            shutil.copy(model_path, dest_path)

        # Create version entry
        version = ModelVersion(
            version_id=version_id,
            agent_type=agent_type,
            created_at=datetime.now().isoformat(),
            model_path=dest_path,
            training_config=training_config or {},
            evaluation_metrics=evaluation_metrics or {},
            status=DeploymentStatus.PENDING
        )

        self.versions[version_id] = version
        self._save_versions()

        # Cleanup old versions
        self._cleanup_old_versions()

        return version_id

    def deploy(
        self,
        version_id: str,
        shadow_mode: bool = True
    ) -> bool:
        """
        Deploy a model version.

        Args:
            version_id: Version to deploy
            shadow_mode: Start in shadow mode first

        Returns:
            Success status
        """
        if version_id not in self.versions:
            print(f"Version {version_id} not found")
            return False

        version = self.versions[version_id]

        # Record deployment
        version.deployment_history.append({
            "action": "deploy",
            "timestamp": datetime.now().isoformat(),
            "shadow_mode": shadow_mode,
            "previous_active": self.active_version
        })

        if shadow_mode:
            version.status = DeploymentStatus.SHADOW
        else:
            # Retire previous active version
            if self.active_version and self.active_version in self.versions:
                self.versions[self.active_version].status = DeploymentStatus.RETIRED

            version.status = DeploymentStatus.ACTIVE
            self.active_version = version_id

        self._save_versions()
        return True

    def promote_to_active(self, version_id: str) -> bool:
        """
        Promote a shadow version to active.

        Args:
            version_id: Version to promote

        Returns:
            Success status
        """
        if version_id not in self.versions:
            return False

        version = self.versions[version_id]
        if version.status != DeploymentStatus.SHADOW:
            print(f"Version {version_id} is not in shadow mode")
            return False

        # Retire previous active
        if self.active_version and self.active_version in self.versions:
            self.versions[self.active_version].status = DeploymentStatus.RETIRED

        version.status = DeploymentStatus.ACTIVE
        version.deployment_history.append({
            "action": "promote",
            "timestamp": datetime.now().isoformat()
        })
        self.active_version = version_id

        self._save_versions()
        return True

    def rollback(self, to_version: str = None) -> bool:
        """
        Rollback to a previous version.

        Args:
            to_version: Specific version to rollback to, or previous active

        Returns:
            Success status
        """
        current_version = self.versions.get(self.active_version)
        if current_version:
            current_version.status = DeploymentStatus.ROLLBACK
            current_version.deployment_history.append({
                "action": "rollback",
                "timestamp": datetime.now().isoformat()
            })

        # Find version to rollback to
        if to_version and to_version in self.versions:
            target = to_version
        else:
            # Find most recent retired version
            retired = [
                v for v in self.versions.values()
                if v.status == DeploymentStatus.RETIRED
            ]
            if not retired:
                print("No previous version to rollback to")
                return False
            target = max(retired, key=lambda v: v.created_at).version_id

        self.versions[target].status = DeploymentStatus.ACTIVE
        self.active_version = target
        self._save_versions()

        return True

    def get_active_model_path(self) -> Optional[str]:
        """Get path to currently active model."""
        if self.active_version and self.active_version in self.versions:
            return self.versions[self.active_version].model_path
        return None

    def get_version_info(self, version_id: str = None) -> Optional[Dict]:
        """Get information about a version."""
        version_id = version_id or self.active_version
        if version_id and version_id in self.versions:
            return self.versions[version_id].to_dict()
        return None

    def list_versions(self) -> List[Dict]:
        """List all versions."""
        return [v.to_dict() for v in sorted(
            self.versions.values(),
            key=lambda v: v.created_at,
            reverse=True
        )]

    def _cleanup_old_versions(self):
        """Remove old versions exceeding max limit."""
        sorted_versions = sorted(
            self.versions.values(),
            key=lambda v: v.created_at,
            reverse=True
        )

        # Keep active and shadow versions
        to_keep = {self.active_version}
        for v in sorted_versions:
            if v.status in [DeploymentStatus.ACTIVE, DeploymentStatus.SHADOW]:
                to_keep.add(v.version_id)

        # Keep top N versions
        for v in sorted_versions[:self.config.max_versions_to_keep]:
            to_keep.add(v.version_id)

        # Remove old versions
        for v in sorted_versions:
            if v.version_id not in to_keep:
                # Delete model files
                if os.path.exists(v.model_path):
                    shutil.rmtree(v.model_path)
                del self.versions[v.version_id]

        self._save_versions()


class ProductionServer:
    """
    Serves models in production with monitoring.
    """

    def __init__(
        self,
        registry: ModelRegistry,
        monitor=None  # ProductionMonitor from evaluation.py
    ):
        """Initialize server."""
        self.registry = registry
        self.monitor = monitor
        self.agent = None
        self.shadow_agent = None
        self._load_active_agent()

    def _load_active_agent(self):
        """Load the active agent."""
        model_path = self.registry.get_active_model_path()
        if model_path:
            self.agent = self._load_agent(model_path)

    def _load_agent(self, model_path: str):
        """Load agent from path."""
        try:
            # Determine agent type from version info
            for version in self.registry.versions.values():
                if version.model_path == model_path:
                    agent_type = version.agent_type
                    break
            else:
                agent_type = "ppo"  # Default

            # Import and load agent
            if agent_type == "ppo":
                from uit_aps.scheduling.rl.agents.ppo import PPOAgent, PPOConfig
                config = PPOConfig()
                # Get dimensions from saved config if available
                agent = PPOAgent(obs_dim=3216, action_dim=7, config=config)
            else:
                from uit_aps.scheduling.rl.agents.sac import SACAgent, SACConfig
                config = SACConfig()
                agent = SACAgent(obs_dim=3216, action_dim=7, config=config)

            agent.load(model_path)
            return agent

        except Exception as e:
            print(f"Failed to load agent: {e}")
            return None

    def predict(
        self,
        state: np.ndarray,
        valid_actions: np.ndarray = None,
        deterministic: bool = True
    ) -> Tuple[np.ndarray, Dict]:
        """
        Get action prediction from the model.

        Args:
            state: Current state
            valid_actions: Valid action mask
            deterministic: Use deterministic policy

        Returns:
            Tuple of (action, metadata)
        """
        if self.agent is None:
            # Fallback to default action
            return np.array([0, 0, 0, 0]), {"error": "No active agent"}

        action, info = self.agent.select_action(
            state,
            valid_actions=valid_actions,
            deterministic=deterministic
        )

        metadata = {
            "version": self.registry.active_version,
            "confidence": info.get("confidence", 0.0),
            "agent_type": self.registry.get_version_info().get("agent_type", "unknown")
        }

        # Log decision if monitor available
        if self.monitor:
            self.monitor.log_decision(
                state=state,
                action=action,
                confidence=metadata["confidence"],
                context=metadata
            )

        # Shadow mode comparison
        if self.shadow_agent:
            shadow_action, shadow_info = self.shadow_agent.select_action(
                state, valid_actions, deterministic
            )
            metadata["shadow_action"] = shadow_action.tolist()
            metadata["shadow_confidence"] = shadow_info.get("confidence", 0.0)

        return action, metadata

    def reload(self):
        """Reload the active agent."""
        self._load_active_agent()

    def enable_shadow_mode(self, version_id: str):
        """Enable shadow mode for a version."""
        if version_id in self.registry.versions:
            version = self.registry.versions[version_id]
            self.shadow_agent = self._load_agent(version.model_path)

    def disable_shadow_mode(self):
        """Disable shadow mode."""
        self.shadow_agent = None


class ABTestManager:
    """
    Manages A/B testing between model versions.
    """

    def __init__(self, registry: ModelRegistry, config: DeploymentConfig = None):
        """Initialize A/B test manager."""
        self.registry = registry
        self.config = config or DeploymentConfig()
        self.test_results: Dict[str, List[Dict]] = {}
        self.active_test: Optional[Dict] = None

    def start_test(
        self,
        control_version: str,
        treatment_version: str,
        test_ratio: float = None
    ) -> bool:
        """
        Start an A/B test.

        Args:
            control_version: Control group version (current)
            treatment_version: Treatment group version (new)
            test_ratio: Ratio of traffic for treatment

        Returns:
            Success status
        """
        if control_version not in self.registry.versions:
            print(f"Control version {control_version} not found")
            return False
        if treatment_version not in self.registry.versions:
            print(f"Treatment version {treatment_version} not found")
            return False

        self.active_test = {
            "control": control_version,
            "treatment": treatment_version,
            "ratio": test_ratio or self.config.ab_test_ratio,
            "started_at": datetime.now().isoformat(),
            "results": {"control": [], "treatment": []}
        }

        return True

    def get_version_for_request(self) -> str:
        """
        Get which version to use for a request.

        Returns:
            Version ID to use
        """
        if not self.active_test:
            return self.registry.active_version

        # Random assignment
        if np.random.random() < self.active_test["ratio"]:
            return self.active_test["treatment"]
        return self.active_test["control"]

    def record_result(self, version: str, metrics: Dict):
        """Record result for a version."""
        if not self.active_test:
            return

        if version == self.active_test["control"]:
            self.active_test["results"]["control"].append(metrics)
        elif version == self.active_test["treatment"]:
            self.active_test["results"]["treatment"].append(metrics)

    def get_test_results(self) -> Optional[Dict]:
        """Get A/B test results."""
        if not self.active_test:
            return None

        control_results = self.active_test["results"]["control"]
        treatment_results = self.active_test["results"]["treatment"]

        if not control_results or not treatment_results:
            return {"status": "insufficient_data"}

        # Compute metrics
        control_rewards = [r.get("reward", 0) for r in control_results]
        treatment_rewards = [r.get("reward", 0) for r in treatment_results]

        return {
            "control": {
                "version": self.active_test["control"],
                "sample_size": len(control_results),
                "mean_reward": np.mean(control_rewards),
                "std_reward": np.std(control_rewards)
            },
            "treatment": {
                "version": self.active_test["treatment"],
                "sample_size": len(treatment_results),
                "mean_reward": np.mean(treatment_rewards),
                "std_reward": np.std(treatment_rewards)
            },
            "improvement": (np.mean(treatment_rewards) - np.mean(control_rewards)) / max(abs(np.mean(control_rewards)), 0.01) * 100,
            "started_at": self.active_test["started_at"]
        }

    def end_test(self, promote_winner: bool = True) -> Dict:
        """
        End A/B test and optionally promote winner.

        Args:
            promote_winner: Whether to promote the winning version

        Returns:
            Test summary
        """
        results = self.get_test_results()
        if not results or results.get("status") == "insufficient_data":
            self.active_test = None
            return {"status": "ended_no_winner"}

        winner = (
            self.active_test["treatment"]
            if results["improvement"] > 0
            else self.active_test["control"]
        )

        if promote_winner and winner == self.active_test["treatment"]:
            self.registry.promote_to_active(winner)

        self.active_test = None

        return {
            "status": "completed",
            "winner": winner,
            "results": results
        }


# Frappe API endpoints for deployment
def get_deployment_status() -> Dict:
    """
    Get current deployment status.

    Returns:
        Deployment status information
    """
    try:
        registry = ModelRegistry()
        return {
            "success": True,
            "active_version": registry.active_version,
            "active_version_info": registry.get_version_info(),
            "all_versions": registry.list_versions()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def deploy_model(
    version_id: str,
    shadow_mode: bool = True
) -> Dict:
    """
    Deploy a model version.

    Args:
        version_id: Version to deploy
        shadow_mode: Start in shadow mode

    Returns:
        Deployment result
    """
    try:
        registry = ModelRegistry()
        success = registry.deploy(version_id, shadow_mode)
        return {
            "success": success,
            "version": version_id,
            "shadow_mode": shadow_mode
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def rollback_deployment(to_version: str = None) -> Dict:
    """
    Rollback to a previous version.

    Args:
        to_version: Specific version to rollback to

    Returns:
        Rollback result
    """
    try:
        registry = ModelRegistry()
        success = registry.rollback(to_version)
        return {
            "success": success,
            "active_version": registry.active_version
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
