# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
UIT APS Scheduling Module

This module implements the Hybrid APS (Advanced Planning and Scheduling) system
with three tiers:
- Tier 1: OR-Tools CP-SAT Solver for offline optimal scheduling
- Tier 2: RL Agent (PPO/SAC) for real-time adjustments (future)
- Tier 3: GNN Encoder for pattern learning (future)
"""

__version__ = "1.0.0"
