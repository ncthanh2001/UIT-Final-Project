# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
GNN-based Recommendation Engine for Scheduling

Provides long-term strategic recommendations based on pattern analysis:
- Capacity planning recommendations
- Maintenance scheduling suggestions
- Workflow optimization insights
- Resource allocation improvements
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
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
from uit_aps.scheduling.gnn.predictors import (
    BottleneckPredictor, DurationPredictor, DelayPredictor,
    PredictorConfig
)


def check_torch():
    """Check if PyTorch is available."""
    if not TORCH_AVAILABLE:
        raise ImportError(
            "PyTorch is required for recommendation engine. "
            "Install with: pip install torch"
        )


class RecommendationType(Enum):
    """Types of recommendations."""
    CAPACITY_INCREASE = "capacity_increase"
    CAPACITY_DECREASE = "capacity_decrease"
    MAINTENANCE_SCHEDULE = "maintenance_schedule"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    RESOURCE_REALLOCATION = "resource_reallocation"
    SCHEDULE_BUFFER = "schedule_buffer"
    PARALLEL_PROCESSING = "parallel_processing"
    BATCH_OPTIMIZATION = "batch_optimization"
    PRIORITY_ADJUSTMENT = "priority_adjustment"
    MACHINE_UPGRADE = "machine_upgrade"


class Priority(Enum):
    """Recommendation priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class Recommendation:
    """A single recommendation."""
    id: str
    type: RecommendationType
    priority: Priority
    title: str
    description: str
    impact: str
    affected_resources: List[str]
    estimated_improvement: float  # Percentage improvement
    implementation_effort: str  # "low", "medium", "high"
    confidence: float  # 0-1
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecommendationConfig:
    """Configuration for recommendation engine."""
    # Thresholds
    bottleneck_threshold: float = 0.7
    duration_overrun_threshold: float = 1.15  # 15% overrun
    delay_risk_threshold: float = 0.5
    utilization_high_threshold: float = 0.9
    utilization_low_threshold: float = 0.3

    # Analysis settings
    min_confidence: float = 0.6
    max_recommendations: int = 10
    include_low_priority: bool = False

    # Model settings
    hidden_dim: int = 128
    device: str = "cpu"


class RecommendationEngine:
    """
    Generates strategic recommendations based on GNN analysis.

    Uses pattern recognition and prediction models to suggest:
    - Long-term capacity planning changes
    - Preventive maintenance scheduling
    - Workflow improvements
    - Resource optimization
    """

    def __init__(self, config: RecommendationConfig = None):
        """
        Initialize recommendation engine.

        Args:
            config: Engine configuration
        """
        self.config = config or RecommendationConfig()

        # Initialize predictors if PyTorch available
        if TORCH_AVAILABLE:
            predictor_config = PredictorConfig(
                hidden_dim=self.config.hidden_dim,
                device=self.config.device
            )
            self.bottleneck_predictor = BottleneckPredictor(predictor_config)
            self.duration_predictor = DurationPredictor(predictor_config)
            self.delay_predictor = DelayPredictor(predictor_config)
        else:
            self.bottleneck_predictor = None
            self.duration_predictor = None
            self.delay_predictor = None

        self._recommendation_counter = 0

    def analyze(
        self,
        schedule: List[Dict],
        machines: List[Dict],
        historical_data: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze schedule and generate recommendations.

        Args:
            schedule: List of operation dictionaries
            machines: List of machine dictionaries
            historical_data: Optional historical scheduling data

        Returns:
            Analysis results with recommendations
        """
        recommendations = []

        # Rule-based analysis (always available)
        recommendations.extend(self._analyze_utilization(machines))
        recommendations.extend(self._analyze_workload_balance(schedule, machines))
        recommendations.extend(self._analyze_schedule_slack(schedule))
        recommendations.extend(self._analyze_critical_path(schedule))

        # GNN-based analysis (if available)
        if TORCH_AVAILABLE and self.bottleneck_predictor is not None:
            recommendations.extend(
                self._analyze_with_gnn(schedule, machines)
            )

        # Historical pattern analysis (if data available)
        if historical_data:
            recommendations.extend(
                self._analyze_historical_patterns(historical_data)
            )

        # Filter and sort recommendations
        recommendations = self._filter_recommendations(recommendations)
        recommendations = self._prioritize_recommendations(recommendations)

        # Limit number of recommendations
        recommendations = recommendations[:self.config.max_recommendations]

        return {
            "recommendations": [self._recommendation_to_dict(r) for r in recommendations],
            "summary": self._generate_summary(recommendations),
            "analysis": {
                "num_machines": len(machines),
                "num_operations": len(schedule),
                "analysis_type": "gnn" if TORCH_AVAILABLE else "rule-based"
            }
        }

    def _analyze_utilization(self, machines: List[Dict]) -> List[Recommendation]:
        """Analyze machine utilization patterns."""
        recommendations = []

        high_util_machines = []
        low_util_machines = []

        for machine in machines:
            machine_id = machine.get("machine_id") or machine.get("workstation")
            utilization = machine.get("utilization", 0.5)

            if utilization >= self.config.utilization_high_threshold:
                high_util_machines.append((machine_id, utilization))
            elif utilization <= self.config.utilization_low_threshold:
                low_util_machines.append((machine_id, utilization))

        # High utilization recommendations
        if high_util_machines:
            avg_util = np.mean([u for _, u in high_util_machines])
            recommendations.append(Recommendation(
                id=self._next_id(),
                type=RecommendationType.CAPACITY_INCREASE,
                priority=Priority.HIGH if avg_util > 0.95 else Priority.MEDIUM,
                title="Add capacity to high-utilization machines",
                description=(
                    f"{len(high_util_machines)} machine(s) running at >90% utilization. "
                    f"Average: {avg_util:.0%}. Consider adding capacity to prevent bottlenecks."
                ),
                impact=f"Reduce bottleneck risk by up to {(avg_util - 0.8) * 100:.0f}%",
                affected_resources=[m for m, _ in high_util_machines],
                estimated_improvement=(avg_util - 0.8) * 50,  # Rough estimate
                implementation_effort="high",
                confidence=0.8,
                data={"machines": high_util_machines}
            ))

        # Low utilization recommendations
        if low_util_machines and len(low_util_machines) > 1:
            recommendations.append(Recommendation(
                id=self._next_id(),
                type=RecommendationType.CAPACITY_DECREASE,
                priority=Priority.LOW,
                title="Consolidate underutilized machines",
                description=(
                    f"{len(low_util_machines)} machine(s) running at <30% utilization. "
                    "Consider consolidating workload or repurposing resources."
                ),
                impact="Reduce operational costs",
                affected_resources=[m for m, _ in low_util_machines],
                estimated_improvement=15.0,
                implementation_effort="medium",
                confidence=0.7,
                data={"machines": low_util_machines}
            ))

        return recommendations

    def _analyze_workload_balance(
        self,
        schedule: List[Dict],
        machines: List[Dict]
    ) -> List[Recommendation]:
        """Analyze workload distribution across machines."""
        recommendations = []

        # Calculate workload per machine
        workload = {}
        for op in schedule:
            machine_id = op.get("machine_id") or op.get("workstation")
            if machine_id:
                duration = op.get("duration", 0)
                workload[machine_id] = workload.get(machine_id, 0) + duration

        if not workload:
            return recommendations

        workloads = list(workload.values())
        mean_workload = np.mean(workloads)
        std_workload = np.std(workloads)

        # Check for imbalance
        if std_workload > mean_workload * 0.5:  # High variance
            # Find overloaded and underloaded machines
            overloaded = [(m, w) for m, w in workload.items() if w > mean_workload * 1.3]
            underloaded = [(m, w) for m, w in workload.items() if w < mean_workload * 0.7]

            if overloaded and underloaded:
                recommendations.append(Recommendation(
                    id=self._next_id(),
                    type=RecommendationType.RESOURCE_REALLOCATION,
                    priority=Priority.MEDIUM,
                    title="Balance workload across machines",
                    description=(
                        f"Workload is imbalanced. {len(overloaded)} machine(s) have >30% above average load, "
                        f"while {len(underloaded)} have <70% of average. "
                        "Consider redistributing operations."
                    ),
                    impact="Improve throughput and reduce delays",
                    affected_resources=[m for m, _ in overloaded + underloaded],
                    estimated_improvement=20.0,
                    implementation_effort="medium",
                    confidence=0.75,
                    data={
                        "overloaded": overloaded,
                        "underloaded": underloaded,
                        "mean_workload": mean_workload
                    }
                ))

        return recommendations

    def _analyze_schedule_slack(self, schedule: List[Dict]) -> List[Recommendation]:
        """Analyze schedule slack and buffer time."""
        recommendations = []

        tight_operations = []
        for op in schedule:
            op_id = op.get("operation_id") or op.get("job_card")
            end_time = op.get("end_time", 0)
            due_date = op.get("due_date", float("inf"))

            slack = due_date - end_time
            duration = op.get("duration", 1)

            # Tight if slack is less than 20% of duration
            if slack < duration * 0.2:
                tight_operations.append({
                    "operation_id": op_id,
                    "slack": slack,
                    "duration": duration,
                    "slack_ratio": slack / duration if duration > 0 else 0
                })

        if len(tight_operations) > len(schedule) * 0.3:  # >30% are tight
            recommendations.append(Recommendation(
                id=self._next_id(),
                type=RecommendationType.SCHEDULE_BUFFER,
                priority=Priority.HIGH,
                title="Add buffer time to tight schedule",
                description=(
                    f"{len(tight_operations)} operations ({len(tight_operations) / len(schedule) * 100:.0f}%) "
                    "have less than 20% slack time. Add buffers to absorb disruptions."
                ),
                impact="Reduce risk of cascading delays",
                affected_resources=[op["operation_id"] for op in tight_operations[:5]],
                estimated_improvement=25.0,
                implementation_effort="low",
                confidence=0.85,
                data={"tight_operations": tight_operations[:10]}
            ))

        return recommendations

    def _analyze_critical_path(self, schedule: List[Dict]) -> List[Recommendation]:
        """Analyze critical path operations."""
        recommendations = []

        # Group by job and find sequences
        jobs = {}
        for op in schedule:
            job_id = op.get("job_id") or op.get("work_order")
            if job_id not in jobs:
                jobs[job_id] = []
            jobs[job_id].append(op)

        # Find long critical paths
        long_paths = []
        for job_id, ops in jobs.items():
            if len(ops) >= 5:  # Long sequence
                total_duration = sum(op.get("duration", 0) for op in ops)
                long_paths.append({
                    "job_id": job_id,
                    "num_operations": len(ops),
                    "total_duration": total_duration
                })

        if long_paths:
            recommendations.append(Recommendation(
                id=self._next_id(),
                type=RecommendationType.PARALLEL_PROCESSING,
                priority=Priority.MEDIUM,
                title="Consider parallel processing for long sequences",
                description=(
                    f"{len(long_paths)} job(s) have long operation sequences (5+ operations). "
                    "Review if some operations can run in parallel."
                ),
                impact="Reduce total processing time",
                affected_resources=[p["job_id"] for p in long_paths[:5]],
                estimated_improvement=15.0,
                implementation_effort="high",
                confidence=0.65,
                data={"long_paths": long_paths[:5]}
            ))

        return recommendations

    def _analyze_with_gnn(
        self,
        schedule: List[Dict],
        machines: List[Dict]
    ) -> List[Recommendation]:
        """Analyze using GNN predictors."""
        recommendations = []

        try:
            # Bottleneck analysis
            bottleneck_results = self.bottleneck_predictor.predict(
                schedule, machines, threshold=self.config.bottleneck_threshold
            )

            if bottleneck_results["bottlenecks"]:
                critical = [b for b in bottleneck_results["bottlenecks"]
                           if b["bottleneck_probability"] >= 0.85]

                if critical:
                    recommendations.append(Recommendation(
                        id=self._next_id(),
                        type=RecommendationType.MACHINE_UPGRADE,
                        priority=Priority.CRITICAL,
                        title="Critical bottleneck detected (GNN analysis)",
                        description=(
                            f"{len(critical)} machine(s) predicted as critical bottlenecks "
                            f"with >85% probability. Immediate action recommended."
                        ),
                        impact="Prevent production delays",
                        affected_resources=[b["machine_id"] for b in critical],
                        estimated_improvement=30.0,
                        implementation_effort="high",
                        confidence=0.9,
                        data={"bottlenecks": critical}
                    ))

            # Duration analysis
            duration_results = self.duration_predictor.predict(schedule, machines)

            if duration_results["at_risk"]:
                avg_overrun = duration_results["summary"]["avg_ratio"]
                if avg_overrun > self.config.duration_overrun_threshold:
                    recommendations.append(Recommendation(
                        id=self._next_id(),
                        type=RecommendationType.SCHEDULE_BUFFER,
                        priority=Priority.HIGH,
                        title="Duration overrun predicted (GNN analysis)",
                        description=(
                            f"Operations predicted to run {(avg_overrun - 1) * 100:.0f}% longer "
                            f"than planned. {len(duration_results['at_risk'])} operations at risk."
                        ),
                        impact="Improve schedule accuracy",
                        affected_resources=[op["operation_id"] for op in duration_results["at_risk"][:5]],
                        estimated_improvement=20.0,
                        implementation_effort="low",
                        confidence=0.8,
                        data={"at_risk": duration_results["at_risk"][:5]}
                    ))

            # Delay analysis
            delay_results = self.delay_predictor.predict(
                schedule, machines, delay_threshold=self.config.delay_risk_threshold
            )

            if delay_results["cascade_risks"]:
                recommendations.append(Recommendation(
                    id=self._next_id(),
                    type=RecommendationType.PRIORITY_ADJUSTMENT,
                    priority=Priority.HIGH,
                    title="Cascade delay risk detected (GNN analysis)",
                    description=(
                        f"{len(delay_results['cascade_risks'])} operations may cause cascading delays. "
                        "Consider prioritizing or adding buffers."
                    ),
                    impact="Prevent delay propagation",
                    affected_resources=[op["operation_id"] for op in delay_results["cascade_risks"]],
                    estimated_improvement=25.0,
                    implementation_effort="medium",
                    confidence=0.75,
                    data={"cascade_risks": delay_results["cascade_risks"]}
                ))

        except Exception as e:
            # Log error but don't fail
            pass

        return recommendations

    def _analyze_historical_patterns(
        self,
        historical_data: List[Dict]
    ) -> List[Recommendation]:
        """Analyze historical patterns for recurring issues."""
        recommendations = []

        # Analyze breakdown patterns
        breakdowns = [d for d in historical_data if d.get("type") == "breakdown"]
        if breakdowns:
            # Find frequently breaking machines
            breakdown_count = {}
            for b in breakdowns:
                machine = b.get("machine_id")
                breakdown_count[machine] = breakdown_count.get(machine, 0) + 1

            frequent_breakdowns = [
                (m, c) for m, c in breakdown_count.items() if c >= 3
            ]

            if frequent_breakdowns:
                recommendations.append(Recommendation(
                    id=self._next_id(),
                    type=RecommendationType.MAINTENANCE_SCHEDULE,
                    priority=Priority.HIGH,
                    title="Preventive maintenance recommended",
                    description=(
                        f"{len(frequent_breakdowns)} machine(s) have frequent breakdowns. "
                        "Consider preventive maintenance schedule."
                    ),
                    impact="Reduce unplanned downtime",
                    affected_resources=[m for m, _ in frequent_breakdowns],
                    estimated_improvement=35.0,
                    implementation_effort="medium",
                    confidence=0.85,
                    data={"breakdown_history": frequent_breakdowns}
                ))

        return recommendations

    def _filter_recommendations(
        self,
        recommendations: List[Recommendation]
    ) -> List[Recommendation]:
        """Filter recommendations by confidence and priority."""
        filtered = [
            r for r in recommendations
            if r.confidence >= self.config.min_confidence
        ]

        if not self.config.include_low_priority:
            filtered = [r for r in filtered if r.priority != Priority.LOW]

        return filtered

    def _prioritize_recommendations(
        self,
        recommendations: List[Recommendation]
    ) -> List[Recommendation]:
        """Sort recommendations by priority and impact."""
        return sorted(
            recommendations,
            key=lambda r: (r.priority.value, -r.estimated_improvement)
        )

    def _generate_summary(
        self,
        recommendations: List[Recommendation]
    ) -> Dict[str, Any]:
        """Generate summary of recommendations."""
        if not recommendations:
            return {
                "total": 0,
                "by_priority": {},
                "by_type": {},
                "total_estimated_improvement": 0
            }

        by_priority = {}
        by_type = {}

        for r in recommendations:
            priority_name = r.priority.name
            type_name = r.type.value

            by_priority[priority_name] = by_priority.get(priority_name, 0) + 1
            by_type[type_name] = by_type.get(type_name, 0) + 1

        return {
            "total": len(recommendations),
            "by_priority": by_priority,
            "by_type": by_type,
            "total_estimated_improvement": sum(r.estimated_improvement for r in recommendations)
        }

    def _recommendation_to_dict(self, r: Recommendation) -> Dict[str, Any]:
        """Convert recommendation to dictionary."""
        return {
            "id": r.id,
            "type": r.type.value,
            "priority": r.priority.name,
            "priority_value": r.priority.value,
            "title": r.title,
            "description": r.description,
            "impact": r.impact,
            "affected_resources": r.affected_resources,
            "estimated_improvement": r.estimated_improvement,
            "implementation_effort": r.implementation_effort,
            "confidence": r.confidence,
            "data": r.data
        }

    def _next_id(self) -> str:
        """Generate next recommendation ID."""
        self._recommendation_counter += 1
        return f"REC-{self._recommendation_counter:04d}"


def create_recommendation_engine(
    config: RecommendationConfig = None
) -> RecommendationEngine:
    """
    Factory function to create recommendation engine.

    Args:
        config: Engine configuration

    Returns:
        RecommendationEngine instance
    """
    return RecommendationEngine(config)
