# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
GNN-based Predictors for Scheduling

Implements prediction models using GNN embeddings:
- Bottleneck Predictor: Identifies machines likely to become bottlenecks
- Duration Predictor: Predicts actual vs expected processing duration
- Delay Predictor: Predicts potential delays in the schedule
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
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
from uit_aps.scheduling.gnn.encoder import (
    SchedulingGraphEncoder, EncoderConfig,
    MachineEncoder, OperationEncoder
)


def check_torch():
    """Check if PyTorch is available."""
    if not TORCH_AVAILABLE:
        raise ImportError(
            "PyTorch is required for GNN predictors. "
            "Install with: pip install torch"
        )


@dataclass
class PredictorConfig:
    """Configuration for prediction models."""
    # Encoder config
    hidden_dim: int = 128
    output_dim: int = 256
    num_gnn_layers: int = 3
    num_attention_heads: int = 4
    dropout: float = 0.1

    # Predictor-specific
    predictor_hidden_dim: int = 64
    num_predictor_layers: int = 2

    # Training
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5

    # Device
    device: str = "cpu"


class BottleneckPredictor(nn.Module):
    """
    Predicts which machines will become bottlenecks.

    Bottleneck is defined as:
    - High utilization (>90%)
    - Long queue of waiting operations
    - Critical path dependency
    - Historical breakdown frequency

    Output: Probability [0, 1] for each machine being a bottleneck.
    """

    def __init__(self, config: PredictorConfig = None):
        """
        Initialize bottleneck predictor.

        Args:
            config: Predictor configuration
        """
        check_torch()
        super().__init__()

        self.config = config or PredictorConfig()

        # Build encoder config
        encoder_config = EncoderConfig(
            hidden_dim=self.config.hidden_dim,
            output_dim=self.config.output_dim,
            num_gnn_layers=self.config.num_gnn_layers,
            num_attention_heads=self.config.num_attention_heads,
            dropout=self.config.dropout,
            device=self.config.device
        )

        # Machine encoder
        self.machine_encoder = MachineEncoder(encoder_config)

        # Prediction head
        layers = []
        in_dim = self.config.hidden_dim
        for i in range(self.config.num_predictor_layers - 1):
            layers.extend([
                nn.Linear(in_dim, self.config.predictor_hidden_dim),
                nn.ReLU(),
                nn.Dropout(self.config.dropout)
            ])
            in_dim = self.config.predictor_hidden_dim

        layers.append(nn.Linear(in_dim, 1))
        layers.append(nn.Sigmoid())

        self.prediction_head = nn.Sequential(*layers)

        self.to(self.config.device)

    def forward(
        self,
        graph_data: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """
        Predict bottleneck probability for each machine.

        Args:
            graph_data: Dictionary from SchedulingGraph.to_tensors()

        Returns:
            Bottleneck probabilities [num_machines]
        """
        # Get machine embeddings
        machine_embeddings = self.machine_encoder(graph_data)

        if machine_embeddings.size(0) == 0:
            return torch.zeros(0, device=self.config.device)

        # Predict bottleneck probability
        probs = self.prediction_head(machine_embeddings).squeeze(-1)

        return probs

    def predict(
        self,
        schedule: List[Dict],
        machines: List[Dict],
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        High-level prediction interface.

        Args:
            schedule: List of operation dictionaries
            machines: List of machine dictionaries
            threshold: Bottleneck probability threshold

        Returns:
            Dictionary with predictions and analysis
        """
        self.eval()

        # Build graph
        graph = build_graph_from_schedule(schedule, machines)
        graph_data = graph.to_tensors()

        # Predict
        with torch.no_grad():
            probs = self.forward(graph_data)

        # Build results
        results = {
            "bottlenecks": [],
            "all_machines": [],
            "summary": {}
        }

        for i, machine in enumerate(machines):
            machine_id = machine.get("machine_id") or machine.get("workstation")
            prob = probs[i].item() if i < len(probs) else 0.0

            machine_result = {
                "machine_id": machine_id,
                "machine_type": machine.get("machine_type", "unknown"),
                "bottleneck_probability": prob,
                "is_bottleneck": prob >= threshold,
                "current_utilization": machine.get("utilization", 0.0)
            }

            results["all_machines"].append(machine_result)

            if prob >= threshold:
                results["bottlenecks"].append(machine_result)

        # Summary
        results["summary"] = {
            "num_machines": len(machines),
            "num_bottlenecks": len(results["bottlenecks"]),
            "avg_probability": float(probs.mean()) if len(probs) > 0 else 0.0,
            "max_probability": float(probs.max()) if len(probs) > 0 else 0.0
        }

        return results


class DurationPredictor(nn.Module):
    """
    Predicts actual processing duration vs expected.

    Learns patterns from historical data to predict:
    - Duration deviation ratio (actual / expected)
    - Confidence interval

    This helps with:
    - Better schedule accuracy
    - Identifying operations that consistently run long
    - Adjusting time estimates
    """

    def __init__(self, config: PredictorConfig = None):
        """
        Initialize duration predictor.

        Args:
            config: Predictor configuration
        """
        check_torch()
        super().__init__()

        self.config = config or PredictorConfig()

        # Build encoder config
        encoder_config = EncoderConfig(
            hidden_dim=self.config.hidden_dim,
            output_dim=self.config.output_dim,
            num_gnn_layers=self.config.num_gnn_layers,
            num_attention_heads=self.config.num_attention_heads,
            dropout=self.config.dropout,
            device=self.config.device
        )

        # Operation encoder
        self.op_encoder = OperationEncoder(encoder_config)

        # Prediction head for duration ratio (mean and variance)
        self.mean_head = nn.Sequential(
            nn.Linear(self.config.hidden_dim, self.config.predictor_hidden_dim),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(self.config.predictor_hidden_dim, 1)
        )

        # Variance prediction for uncertainty
        self.var_head = nn.Sequential(
            nn.Linear(self.config.hidden_dim, self.config.predictor_hidden_dim),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(self.config.predictor_hidden_dim, 1),
            nn.Softplus()  # Ensure positive variance
        )

        self.to(self.config.device)

    def forward(
        self,
        graph_data: Dict[str, torch.Tensor]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Predict duration ratio for each operation.

        Args:
            graph_data: Dictionary from SchedulingGraph.to_tensors()

        Returns:
            Tuple of (mean_ratio, variance) for each operation
            mean_ratio: [num_ops] - Expected actual/planned ratio (1.0 = on time)
            variance: [num_ops] - Uncertainty in prediction
        """
        # Get operation embeddings
        op_embeddings = self.op_encoder(graph_data)

        if op_embeddings.size(0) == 0:
            return (
                torch.zeros(0, device=self.config.device),
                torch.zeros(0, device=self.config.device)
            )

        # Predict mean ratio (centered at 1.0)
        mean_ratio = 1.0 + self.mean_head(op_embeddings).squeeze(-1)

        # Predict variance
        variance = self.var_head(op_embeddings).squeeze(-1)

        return mean_ratio, variance

    def predict(
        self,
        schedule: List[Dict],
        machines: List[Dict],
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        High-level prediction interface.

        Args:
            schedule: List of operation dictionaries
            machines: List of machine dictionaries
            confidence_level: Confidence level for intervals

        Returns:
            Dictionary with predictions and analysis
        """
        self.eval()

        # Build graph
        graph = build_graph_from_schedule(schedule, machines)
        graph_data = graph.to_tensors()

        # Predict
        with torch.no_grad():
            mean_ratio, variance = self.forward(graph_data)

        # Z-score for confidence interval
        from scipy import stats
        z_score = stats.norm.ppf((1 + confidence_level) / 2)

        # Build results
        results = {
            "operations": [],
            "at_risk": [],  # Operations likely to overrun
            "summary": {}
        }

        for i, op in enumerate(schedule):
            op_id = op.get("operation_id") or op.get("job_card")
            expected_duration = op.get("duration", 0)

            if i < len(mean_ratio):
                ratio = mean_ratio[i].item()
                var = variance[i].item()
                std = np.sqrt(var)

                predicted_duration = expected_duration * ratio
                lower = expected_duration * max(0.5, ratio - z_score * std)
                upper = expected_duration * (ratio + z_score * std)

                is_at_risk = ratio > 1.1  # >10% overrun expected
            else:
                ratio = 1.0
                std = 0.0
                predicted_duration = expected_duration
                lower = expected_duration
                upper = expected_duration
                is_at_risk = False

            op_result = {
                "operation_id": op_id,
                "expected_duration": expected_duration,
                "predicted_duration": predicted_duration,
                "duration_ratio": ratio,
                "uncertainty": std,
                "confidence_interval": {
                    "lower": lower,
                    "upper": upper,
                    "level": confidence_level
                },
                "is_at_risk": is_at_risk
            }

            results["operations"].append(op_result)

            if is_at_risk:
                results["at_risk"].append(op_result)

        # Summary
        if len(mean_ratio) > 0:
            results["summary"] = {
                "num_operations": len(schedule),
                "num_at_risk": len(results["at_risk"]),
                "avg_ratio": float(mean_ratio.mean()),
                "max_ratio": float(mean_ratio.max()),
                "avg_uncertainty": float(variance.mean().sqrt())
            }
        else:
            results["summary"] = {
                "num_operations": len(schedule),
                "num_at_risk": 0,
                "avg_ratio": 1.0,
                "max_ratio": 1.0,
                "avg_uncertainty": 0.0
            }

        return results


class DelayPredictor(nn.Module):
    """
    Predicts potential delays in the schedule.

    Predicts:
    - Probability of delay for each operation
    - Expected delay magnitude (minutes)
    - Cascade effects on downstream operations
    """

    def __init__(self, config: PredictorConfig = None):
        """
        Initialize delay predictor.

        Args:
            config: Predictor configuration
        """
        check_torch()
        super().__init__()

        self.config = config or PredictorConfig()

        # Build encoder config
        encoder_config = EncoderConfig(
            hidden_dim=self.config.hidden_dim,
            output_dim=self.config.output_dim,
            num_gnn_layers=self.config.num_gnn_layers,
            num_attention_heads=self.config.num_attention_heads,
            dropout=self.config.dropout,
            device=self.config.device
        )

        # Graph encoder for global context
        self.graph_encoder = SchedulingGraphEncoder(encoder_config)

        # Delay probability head
        self.delay_prob_head = nn.Sequential(
            nn.Linear(self.config.hidden_dim + self.config.output_dim, self.config.predictor_hidden_dim),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(self.config.predictor_hidden_dim, 1),
            nn.Sigmoid()
        )

        # Delay magnitude head (in minutes)
        self.delay_magnitude_head = nn.Sequential(
            nn.Linear(self.config.hidden_dim + self.config.output_dim, self.config.predictor_hidden_dim),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(self.config.predictor_hidden_dim, 1),
            nn.ReLU()  # Delay is non-negative
        )

        # Cascade impact head (how much delay propagates)
        self.cascade_head = nn.Sequential(
            nn.Linear(self.config.hidden_dim + self.config.output_dim, self.config.predictor_hidden_dim),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(self.config.predictor_hidden_dim, 1),
            nn.Sigmoid()
        )

        self.to(self.config.device)

    def forward(
        self,
        graph_data: Dict[str, torch.Tensor]
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Predict delay for each operation.

        Args:
            graph_data: Dictionary from SchedulingGraph.to_tensors()

        Returns:
            Tuple of (delay_prob, delay_magnitude, cascade_impact)
        """
        # Get graph encoding
        result = self.graph_encoder(graph_data)

        op_indices = graph_data["operation_indices"].to(self.config.device)

        if len(op_indices) == 0:
            empty = torch.zeros(0, device=self.config.device)
            return empty, empty, empty

        # Get operation embeddings with graph context
        op_embeddings = result["node_embeddings"][op_indices]
        graph_embedding = result["embedding"].unsqueeze(0).expand(len(op_indices), -1)
        combined = torch.cat([op_embeddings, graph_embedding], dim=-1)

        # Predict
        delay_prob = self.delay_prob_head(combined).squeeze(-1)
        delay_magnitude = self.delay_magnitude_head(combined).squeeze(-1) * 60  # Scale to minutes
        cascade_impact = self.cascade_head(combined).squeeze(-1)

        return delay_prob, delay_magnitude, cascade_impact

    def predict(
        self,
        schedule: List[Dict],
        machines: List[Dict],
        delay_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        High-level prediction interface.

        Args:
            schedule: List of operation dictionaries
            machines: List of machine dictionaries
            delay_threshold: Probability threshold for flagging delays

        Returns:
            Dictionary with predictions and analysis
        """
        self.eval()

        # Build graph
        graph = build_graph_from_schedule(schedule, machines)
        graph_data = graph.to_tensors()

        # Predict
        with torch.no_grad():
            delay_prob, delay_magnitude, cascade_impact = self.forward(graph_data)

        # Build results
        results = {
            "operations": [],
            "high_risk": [],  # Operations with high delay probability
            "cascade_risks": [],  # Operations that can cascade delays
            "summary": {}
        }

        for i, op in enumerate(schedule):
            op_id = op.get("operation_id") or op.get("job_card")
            job_id = op.get("job_id") or op.get("work_order")

            if i < len(delay_prob):
                prob = delay_prob[i].item()
                magnitude = delay_magnitude[i].item()
                cascade = cascade_impact[i].item()
            else:
                prob = 0.0
                magnitude = 0.0
                cascade = 0.0

            is_high_risk = prob >= delay_threshold
            is_cascade_risk = cascade >= 0.7 and prob >= 0.3

            op_result = {
                "operation_id": op_id,
                "job_id": job_id,
                "delay_probability": prob,
                "expected_delay_minutes": magnitude,
                "cascade_impact": cascade,
                "is_high_risk": is_high_risk,
                "is_cascade_risk": is_cascade_risk
            }

            results["operations"].append(op_result)

            if is_high_risk:
                results["high_risk"].append(op_result)
            if is_cascade_risk:
                results["cascade_risks"].append(op_result)

        # Summary
        if len(delay_prob) > 0:
            expected_total_delay = (delay_prob * delay_magnitude).sum().item()
            results["summary"] = {
                "num_operations": len(schedule),
                "num_high_risk": len(results["high_risk"]),
                "num_cascade_risks": len(results["cascade_risks"]),
                "avg_delay_probability": float(delay_prob.mean()),
                "expected_total_delay_minutes": expected_total_delay,
                "max_expected_delay": float(delay_magnitude.max())
            }
        else:
            results["summary"] = {
                "num_operations": len(schedule),
                "num_high_risk": 0,
                "num_cascade_risks": 0,
                "avg_delay_probability": 0.0,
                "expected_total_delay_minutes": 0.0,
                "max_expected_delay": 0.0
            }

        return results


class SchedulingPredictor(nn.Module):
    """
    Combined predictor that integrates all prediction models.

    Provides a unified interface for all scheduling predictions.
    """

    def __init__(self, config: PredictorConfig = None):
        """
        Initialize combined predictor.

        Args:
            config: Predictor configuration
        """
        check_torch()
        super().__init__()

        self.config = config or PredictorConfig()

        self.bottleneck_predictor = BottleneckPredictor(config)
        self.duration_predictor = DurationPredictor(config)
        self.delay_predictor = DelayPredictor(config)

        self.to(self.config.device)

    def predict_all(
        self,
        schedule: List[Dict],
        machines: List[Dict]
    ) -> Dict[str, Any]:
        """
        Run all predictions.

        Args:
            schedule: List of operation dictionaries
            machines: List of machine dictionaries

        Returns:
            Combined prediction results
        """
        return {
            "bottlenecks": self.bottleneck_predictor.predict(schedule, machines),
            "durations": self.duration_predictor.predict(schedule, machines),
            "delays": self.delay_predictor.predict(schedule, machines)
        }

    def get_critical_insights(
        self,
        schedule: List[Dict],
        machines: List[Dict]
    ) -> Dict[str, Any]:
        """
        Get the most critical insights from all predictions.

        Args:
            schedule: List of operation dictionaries
            machines: List of machine dictionaries

        Returns:
            Critical insights summary
        """
        all_predictions = self.predict_all(schedule, machines)

        # Extract critical items
        critical_machines = [
            m for m in all_predictions["bottlenecks"]["all_machines"]
            if m["bottleneck_probability"] >= 0.8
        ]

        at_risk_ops = all_predictions["durations"]["at_risk"][:5]  # Top 5
        high_delay_risk = all_predictions["delays"]["high_risk"][:5]  # Top 5
        cascade_risks = all_predictions["delays"]["cascade_risks"][:3]  # Top 3

        return {
            "critical_bottlenecks": critical_machines,
            "at_risk_operations": at_risk_ops,
            "high_delay_risk": high_delay_risk,
            "cascade_risks": cascade_risks,
            "summary": {
                "num_bottleneck_machines": len(critical_machines),
                "num_at_risk_operations": len(all_predictions["durations"]["at_risk"]),
                "num_high_delay_risk": len(all_predictions["delays"]["high_risk"]),
                "expected_total_delay": all_predictions["delays"]["summary"]["expected_total_delay_minutes"]
            },
            "recommendations": self._generate_recommendations(all_predictions)
        }

    def _generate_recommendations(self, predictions: Dict) -> List[str]:
        """Generate actionable recommendations from predictions."""
        recommendations = []

        # Bottleneck recommendations
        bottlenecks = predictions["bottlenecks"]["bottlenecks"]
        if len(bottlenecks) > 0:
            top_bottleneck = max(bottlenecks, key=lambda x: x["bottleneck_probability"])
            recommendations.append(
                f"Consider adding capacity to {top_bottleneck['machine_id']} "
                f"(bottleneck probability: {top_bottleneck['bottleneck_probability']:.0%})"
            )

        # Duration recommendations
        at_risk = predictions["durations"]["at_risk"]
        if len(at_risk) > 0:
            avg_ratio = predictions["durations"]["summary"]["avg_ratio"]
            if avg_ratio > 1.1:
                recommendations.append(
                    f"Consider adding buffer time to operations "
                    f"(avg duration ratio: {avg_ratio:.2f}x)"
                )

        # Delay recommendations
        cascade_risks = predictions["delays"]["cascade_risks"]
        if len(cascade_risks) > 0:
            recommendations.append(
                f"Monitor {len(cascade_risks)} operations that may cascade delays"
            )

        expected_delay = predictions["delays"]["summary"]["expected_total_delay_minutes"]
        if expected_delay > 60:
            recommendations.append(
                f"Expected total delay: {expected_delay:.0f} minutes. "
                "Consider schedule optimization."
            )

        return recommendations


def create_predictor(
    predictor_type: str = "combined",
    config: PredictorConfig = None
) -> nn.Module:
    """
    Factory function to create a predictor.

    Args:
        predictor_type: "bottleneck", "duration", "delay", or "combined"
        config: Predictor configuration

    Returns:
        Predictor instance
    """
    config = config or PredictorConfig()

    if predictor_type == "bottleneck":
        return BottleneckPredictor(config)
    elif predictor_type == "duration":
        return DurationPredictor(config)
    elif predictor_type == "delay":
        return DelayPredictor(config)
    else:
        return SchedulingPredictor(config)
