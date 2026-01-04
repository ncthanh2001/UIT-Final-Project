# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Graph Neural Network Module for APS Scheduling

Implements Tier 3 of the Hybrid APS system:
- Scheduling Graph construction (jobs, operations, machines as nodes)
- GNN-based feature encoding (GAT, GCN layers)
- Bottleneck prediction
- Duration prediction
- Long-term recommendation engine

The GNN learns structural patterns in the scheduling problem and provides
enhanced state representations for the RL agent.
"""

__version__ = "1.0.0"


# Lazy imports to avoid circular dependencies and missing torch errors
def get_scheduling_graph():
    from uit_aps.scheduling.gnn.graph import SchedulingGraph
    return SchedulingGraph


def get_gnn_encoder():
    from uit_aps.scheduling.gnn.encoder import SchedulingGraphEncoder
    return SchedulingGraphEncoder


def get_bottleneck_predictor():
    from uit_aps.scheduling.gnn.predictors import BottleneckPredictor
    return BottleneckPredictor


def get_duration_predictor():
    from uit_aps.scheduling.gnn.predictors import DurationPredictor
    return DurationPredictor


def get_recommendation_engine():
    from uit_aps.scheduling.gnn.recommendation import RecommendationEngine
    return RecommendationEngine
