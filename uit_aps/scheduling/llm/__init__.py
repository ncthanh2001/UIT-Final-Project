# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
LLM Integration for Scheduling Analysis

Provides AI-powered insights and recommendations for scheduling results
using OpenAI GPT models.
"""

from uit_aps.scheduling.llm.advisor import SchedulingAdvisor, get_scheduling_advice

__all__ = ["SchedulingAdvisor", "get_scheduling_advice"]
