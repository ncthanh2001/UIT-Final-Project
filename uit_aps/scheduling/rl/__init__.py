# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Reinforcement Learning Module for APS Scheduling

Implements Tier 2 of the Hybrid APS system:
- PPO (Proximal Policy Optimization) agent
- SAC (Soft Actor-Critic) agent
- Real-time scheduling adjustments
- Disruption handling

Phase 4 (Evaluation & Deployment):
- Scenario-based evaluation
- Heuristic comparison (SPT, EDD, FCFS)
- Production monitoring
- Model versioning and deployment

The RL agents learn to make scheduling decisions in dynamic environments
where disruptions (machine breakdowns, rush orders, delays) occur.
"""

__version__ = "1.0.0"

# Lazy imports to avoid circular dependencies and missing torch errors
def get_scheduling_env():
    from uit_aps.scheduling.rl.environment import SchedulingEnv
    return SchedulingEnv

def get_state_encoder():
    from uit_aps.scheduling.rl.state_encoder import StateEncoder
    return StateEncoder

def get_reward_calculator():
    from uit_aps.scheduling.rl.reward import RewardCalculator
    return RewardCalculator

def get_ppo_agent():
    from uit_aps.scheduling.rl.agents.ppo import PPOAgent
    return PPOAgent

def get_sac_agent():
    from uit_aps.scheduling.rl.agents.sac import SACAgent
    return SACAgent

# Phase 4: Evaluation & Deployment
def get_evaluator():
    from uit_aps.scheduling.rl.evaluation import ScenarioEvaluator
    return ScenarioEvaluator

def get_heuristic_scheduler():
    from uit_aps.scheduling.rl.evaluation import HeuristicScheduler
    return HeuristicScheduler

def get_production_monitor():
    from uit_aps.scheduling.rl.evaluation import ProductionMonitor
    return ProductionMonitor

def get_model_registry():
    from uit_aps.scheduling.rl.deployment import ModelRegistry
    return ModelRegistry

def get_production_server():
    from uit_aps.scheduling.rl.deployment import ProductionServer
    return ProductionServer

def run_full_evaluation(env, agent, **kwargs):
    from uit_aps.scheduling.rl.evaluation import run_full_evaluation as _run
    return _run(env, agent, **kwargs)
