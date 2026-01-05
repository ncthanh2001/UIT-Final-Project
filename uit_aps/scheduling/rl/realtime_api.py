# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Real-Time Scheduling Adjustment API

Provides Frappe-compatible API for real-time scheduling adjustments
using trained RL agents. This is the interface between ERPNext and
the Tier 2 RL system.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, cint, flt
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import os
import json


# Global agent cache
_agent_cache: Dict[str, Any] = {}


def _get_operation_duration(job_card) -> int:
    """
    Get operation duration from Job Card or Work Order.

    Priority: Job Card time_required > Work Order operation time_in_mins > default

    Args:
        job_card: Job Card document

    Returns:
        Duration in minutes (default 60 if not found)
    """
    # First try Job Card's time_required field
    if hasattr(job_card, 'time_required') and cint(job_card.time_required):
        return cint(job_card.time_required)

    # Fallback to Work Order operation time_in_mins
    if not job_card.work_order:
        return 60

    try:
        wo = frappe.get_doc("Work Order", job_card.work_order)
        for op in wo.operations:
            if op.operation == job_card.operation:
                return cint(op.time_in_mins) or 60
    except Exception:
        pass

    return 60


def get_rl_agent(agent_type: str = "ppo", model_path: str = None):
    """
    Get or load RL agent from cache.

    Args:
        agent_type: "ppo" or "sac"
        model_path: Path to saved model

    Returns:
        Loaded agent
    """
    cache_key = f"{agent_type}_{model_path or 'default'}"

    if cache_key not in _agent_cache:
        try:
            if agent_type.lower() == "ppo":
                from uit_aps.scheduling.rl.agents.ppo import PPOAgent, PPOConfig
                config = PPOConfig()
                # Determine observation dimension from environment
                obs_dim = 100 * 32 + 20 * 16 + 16  # Default dimensions
                agent = PPOAgent(obs_dim, 7, config)
            else:
                from uit_aps.scheduling.rl.agents.sac import SACAgent, SACConfig
                config = SACConfig()
                obs_dim = 100 * 32 + 20 * 16 + 16
                agent = SACAgent(obs_dim, 7, config)

            # Load saved model if available
            if model_path and os.path.exists(model_path):
                agent.load(model_path)
                agent.eval()

            _agent_cache[cache_key] = agent

        except ImportError as e:
            frappe.throw(
                f"Failed to load RL agent. Ensure PyTorch is installed: pip install torch\n"
                f"Error: {str(e)}"
            )

    return _agent_cache[cache_key]


@frappe.whitelist()
def get_realtime_adjustment(
    scheduling_run: str,
    current_state: str = None,
    agent_type: str = "ppo"
) -> dict:
    """
    Get real-time scheduling adjustment recommendation.

    Called when disruptions occur or manual intervention is needed.

    Args:
        scheduling_run: APS Scheduling Run name
        current_state: JSON string of current state (optional)
        agent_type: "ppo" or "sac"

    Returns:
        dict: {
            success: bool,
            recommendation: {
                action_type: str,
                target_operation: str,
                target_machine: str,
                confidence: float,
                reason: str
            },
            alternatives: [...]
        }
    """
    from uit_aps.scheduling.rl.environment import SchedulingEnv, EnvironmentConfig, ActionType
    from uit_aps.scheduling.rl.state_encoder import StateEncoder, EncoderConfig

    try:
        # Load current schedule
        results = frappe.get_all(
            "APS Scheduling Result",
            filters={"scheduling_run": scheduling_run},
            fields=["*"],
            order_by="planned_start_time asc"
        )

        if not results:
            return {
                "success": False,
                "message": _("No scheduling results found")
            }

        # Load machines
        machines = _load_machines()

        # Convert to environment format
        operations = _convert_results_to_operations(results)

        # Create state encoder
        encoder = StateEncoder(EncoderConfig())
        encoder.set_reference_time(now_datetime())

        # Encode state
        state = encoder.encode(
            operations,
            machines,
            now_datetime(),
            disruptions=[]
        )

        # Get agent recommendation
        model_path = _get_model_path(agent_type)
        agent = get_rl_agent(agent_type, model_path)

        action, info = agent.select_action(state, deterministic=True)

        action_type, op_idx, machine_idx = action

        # Get action details
        action_name = ActionType(action_type).name
        target_op = operations[op_idx] if op_idx < len(operations) else None
        target_machine = machines[machine_idx] if machine_idx < len(machines) else None

        # Build recommendation
        recommendation = {
            "action_type": action_name,
            "action_type_id": action_type,
            "target_operation": target_op.get("job_card", "") if target_op else "",
            "target_operation_name": target_op.get("name", "") if target_op else "",
            "target_machine": target_machine.get("id", "") if target_machine else "",
            "target_machine_name": target_machine.get("name", "") if target_machine else "",
            "confidence": float(max(info.get("action_type_probs", [0]))),
            "value_estimate": info.get("value", 0.0),
            "reason": _get_action_reason(action_type, target_op, target_machine)
        }

        # Get alternatives (top 3 actions)
        alternatives = _get_alternative_actions(info, operations, machines)

        return {
            "success": True,
            "recommendation": recommendation,
            "alternatives": alternatives,
            "state_info": {
                "num_operations": len([o for o in operations if o.get("status") != "empty"]),
                "num_machines": len([m for m in machines if m.get("id")]),
                "current_time": now_datetime().isoformat()
            }
        }

    except Exception as e:
        frappe.log_error(str(e), "RL Adjustment Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def apply_rl_adjustment(
    scheduling_run: str,
    action_type: int,
    target_operation: str,
    target_machine: str = None,
    new_start_time: str = None
) -> dict:
    """
    Apply RL-recommended adjustment to the schedule.

    Args:
        scheduling_run: APS Scheduling Run name
        action_type: Action type ID
        target_operation: Job Card name
        target_machine: New workstation (for reassignment)
        new_start_time: New start time (for rescheduling)

    Returns:
        dict with update status
    """
    from uit_aps.scheduling.rl.environment import ActionType

    try:
        action = ActionType(int(action_type))

        if action == ActionType.NO_OP:
            return {"success": True, "message": _("No action needed")}

        # Get Job Card
        if not frappe.db.exists("Job Card", target_operation):
            return {"success": False, "message": _("Job Card not found")}

        jc = frappe.get_doc("Job Card", target_operation)

        if action == ActionType.REASSIGN_MACHINE:
            if not target_machine:
                return {"success": False, "message": _("Target machine required")}

            jc.workstation = target_machine
            jc.flags.ignore_validate_update_after_submit = True
            jc.save(ignore_permissions=True)

            # Update scheduling result
            _update_scheduling_result(scheduling_run, target_operation, {
                "workstation": target_machine
            })

            return {
                "success": True,
                "message": _("Machine reassigned successfully"),
                "new_workstation": target_machine
            }

        elif action == ActionType.RESCHEDULE_EARLIER:
            new_start = jc.expected_start_date - timedelta(minutes=30)
            if new_start < now_datetime():
                new_start = now_datetime()

            # Get duration from Work Order operation since Job Card doesn't have time_in_mins
            duration_mins = _get_operation_duration(jc)
            new_end = new_start + timedelta(minutes=duration_mins)

            jc.expected_start_date = new_start
            jc.expected_end_date = new_end
            jc.flags.ignore_validate_update_after_submit = True
            jc.save(ignore_permissions=True)

            _update_scheduling_result(scheduling_run, target_operation, {
                "planned_start_time": new_start,
                "planned_end_time": new_end
            })

            return {
                "success": True,
                "message": _("Rescheduled 30 minutes earlier"),
                "new_start": new_start.isoformat(),
                "new_end": new_end.isoformat()
            }

        elif action == ActionType.RESCHEDULE_LATER:
            new_start = jc.expected_start_date + timedelta(minutes=30)

            # Get duration from Work Order operation since Job Card doesn't have time_in_mins
            duration_mins = _get_operation_duration(jc)
            new_end = new_start + timedelta(minutes=duration_mins)

            jc.expected_start_date = new_start
            jc.expected_end_date = new_end
            jc.flags.ignore_validate_update_after_submit = True
            jc.save(ignore_permissions=True)

            _update_scheduling_result(scheduling_run, target_operation, {
                "planned_start_time": new_start,
                "planned_end_time": new_end
            })

            return {
                "success": True,
                "message": _("Rescheduled 30 minutes later"),
                "new_start": new_start.isoformat(),
                "new_end": new_end.isoformat()
            }

        elif action == ActionType.PRIORITIZE_JOB:
            # Increase priority in Work Order
            if jc.work_order:
                wo = frappe.get_doc("Work Order", jc.work_order)
                current_priority = cint(wo.get("priority") or 1)
                wo.db_set("priority", min(10, current_priority + 1))

            return {
                "success": True,
                "message": _("Job priority increased")
            }

        else:
            return {
                "success": False,
                "message": _("Action type not implemented: {}").format(action.name)
            }

    except Exception as e:
        frappe.log_error(str(e), "RL Adjustment Apply Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def handle_disruption(
    disruption_type: str,
    affected_resource: str,
    scheduling_run: str = None,
    duration_minutes: int = 60
) -> dict:
    """
    Handle a disruption event and get adjustment recommendations.

    Args:
        disruption_type: Type of disruption (machine_breakdown, rush_order, etc.)
        affected_resource: Affected machine or operation
        scheduling_run: Current scheduling run
        duration_minutes: Expected disruption duration

    Returns:
        dict with recommendations and auto-applied fixes
    """
    from uit_aps.scheduling.rl.environment import DisruptionType

    try:
        disruption_map = {
            "machine_breakdown": DisruptionType.MACHINE_BREAKDOWN,
            "rush_order": DisruptionType.RUSH_ORDER,
            "processing_delay": DisruptionType.PROCESSING_DELAY,
            "material_shortage": DisruptionType.MATERIAL_SHORTAGE
        }

        dtype = disruption_map.get(disruption_type.lower(), DisruptionType.NONE)

        if dtype == DisruptionType.NONE:
            return {
                "success": False,
                "message": _("Unknown disruption type")
            }

        # Log disruption
        frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "APS Scheduling Run",
            "reference_name": scheduling_run,
            "content": f"Disruption: {disruption_type} affecting {affected_resource} "
                      f"(expected duration: {duration_minutes} min)"
        }).insert(ignore_permissions=True)

        # Get affected operations
        affected_ops = []

        if dtype == DisruptionType.MACHINE_BREAKDOWN:
            affected_ops = frappe.get_all(
                "APS Scheduling Result",
                filters={
                    "scheduling_run": scheduling_run,
                    "workstation": affected_resource,
                    "planned_start_time": [">=", now_datetime()]
                },
                pluck="job_card"
            )

        # Get RL recommendations for each affected operation
        recommendations = []

        for job_card in affected_ops[:5]:  # Limit to 5 recommendations
            rec_result = get_realtime_adjustment(scheduling_run, agent_type="ppo")
            if rec_result.get("success"):
                rec = rec_result["recommendation"]
                rec["affected_job_card"] = job_card
                recommendations.append(rec)

        return {
            "success": True,
            "disruption": {
                "type": disruption_type,
                "affected_resource": affected_resource,
                "duration_minutes": duration_minutes,
                "timestamp": now_datetime().isoformat()
            },
            "affected_operations": affected_ops,
            "recommendations": recommendations,
            "message": _("Disruption logged. {} operations affected.").format(len(affected_ops))
        }

    except Exception as e:
        frappe.log_error(str(e), "Disruption Handler Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def train_rl_agent(
    scheduling_run: str,
    agent_type: str = "ppo",
    max_episodes: int = 100
) -> dict:
    """
    Train RL agent on historical scheduling data.

    This should be run periodically to improve the agent.

    Args:
        scheduling_run: Reference scheduling run for training data
        agent_type: "ppo" or "sac"
        max_episodes: Number of training episodes

    Returns:
        dict with training summary
    """
    try:
        from uit_aps.scheduling.rl.trainer import train_from_ortools
        from uit_aps.scheduling.ortools.models import SchedulingSolution, ScheduledOperation, SolverStatus

        # Load scheduling results
        results = frappe.get_all(
            "APS Scheduling Result",
            filters={"scheduling_run": scheduling_run},
            fields=["*"]
        )

        if not results:
            return {
                "success": False,
                "message": _("No scheduling results to train on")
            }

        # Convert to solution format
        operations = []
        for r in results:
            operations.append(ScheduledOperation(
                operation_id=r.name,
                job_id=r.job_card,
                job_card_name=r.job_card,
                work_order_name="",
                item_code="",
                operation_name=r.operation,
                machine_id=r.workstation,
                start_time=r.planned_start_time,
                end_time=r.planned_end_time,
                duration_mins=int((r.planned_end_time - r.planned_start_time).total_seconds() / 60) if r.planned_end_time and r.planned_start_time else 60,
                sequence=1,
                is_late=r.is_late,
                tardiness_mins=0
            ))

        solution = SchedulingSolution(
            status=SolverStatus.OPTIMAL,
            operations=operations
        )

        machines = _load_machines()

        # Train agent
        save_dir = frappe.get_site_path("private", "files", "rl_models", agent_type)
        agent, summary = train_from_ortools(
            solution,
            machines,
            agent_type=agent_type,
            max_episodes=max_episodes,
            save_dir=save_dir
        )

        # Clear cache to reload new model
        global _agent_cache
        _agent_cache = {}

        return {
            "success": True,
            "summary": summary,
            "model_path": save_dir,
            "message": _("Training completed successfully")
        }

    except Exception as e:
        frappe.log_error(str(e), "RL Training Error")
        return {
            "success": False,
            "message": str(e)
        }


def _load_machines() -> List[Dict]:
    """Load workstations as machine configurations."""
    workstations = frappe.get_all(
        "Workstation",
        filters={"disabled": 0},
        fields=["name", "workstation_name", "workstation_type", "production_capacity"]
    )

    machines = []
    for ws in workstations:
        machines.append({
            "id": ws.name,
            "name": ws.workstation_name or ws.name,
            "type": ws.workstation_type,
            "capacity": cint(ws.production_capacity) or 1,
            "status": "available",
            "utilization": 0.0
        })

    return machines


def _convert_results_to_operations(results: List[Dict]) -> List[Dict]:
    """Convert APS Scheduling Results to operation format."""
    operations = []

    for r in results:
        # Get additional info from Job Card
        jc = frappe.get_doc("Job Card", r.job_card)

        operations.append({
            "id": r.name,
            "job_id": jc.work_order,
            "job_card": r.job_card,
            "name": r.operation or "Operation",
            "machine_id": r.workstation,
            "start_time": r.planned_start_time,
            "end_time": r.planned_end_time,
            "duration_mins": int((r.planned_end_time - r.planned_start_time).total_seconds() / 60) if r.planned_end_time and r.planned_start_time else 60,
            "due_date": jc.expected_end_date,
            "priority": 1,
            "status": "pending" if r.planned_start_time > now_datetime() else "in_progress",
            "is_late": r.is_late,
            "tardiness_mins": 0
        })

    return operations


def _get_model_path(agent_type: str) -> Optional[str]:
    """Get path to saved model."""
    model_dir = frappe.get_site_path("private", "files", "rl_models", agent_type, "best")
    if os.path.exists(model_dir):
        return model_dir
    return None


def _get_action_reason(action_type: int, target_op: Dict, target_machine: Dict) -> str:
    """Generate human-readable reason for action."""
    from uit_aps.scheduling.rl.environment import ActionType

    action = ActionType(action_type)
    reasons = {
        ActionType.NO_OP: "No adjustment needed at this time",
        ActionType.REASSIGN_MACHINE: f"Reassign to {target_machine.get('name', 'another machine')} for better load balancing",
        ActionType.RESCHEDULE_EARLIER: "Move earlier to reduce risk of delay",
        ActionType.RESCHEDULE_LATER: "Postpone to allow priority work to complete",
        ActionType.PRIORITIZE_JOB: "Increase priority to ensure timely completion",
        ActionType.SPLIT_BATCH: "Split into smaller batches for flexibility",
        ActionType.MERGE_OPERATIONS: "Combine with related operations for efficiency"
    }

    return reasons.get(action, "Optimization adjustment")


def _get_alternative_actions(info: Dict, operations: List[Dict], machines: List[Dict]) -> List[Dict]:
    """Get alternative action recommendations."""
    from uit_aps.scheduling.rl.environment import ActionType

    alternatives = []
    probs = info.get("action_type_probs", [])

    if len(probs) > 0:
        # Get top 3 action types (excluding the selected one)
        sorted_indices = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)

        for idx in sorted_indices[1:4]:  # Skip first (already selected)
            if probs[idx] > 0.1:  # Only include if probability > 10%
                alternatives.append({
                    "action_type": ActionType(idx).name,
                    "action_type_id": idx,
                    "confidence": float(probs[idx]),
                    "reason": _get_action_reason(idx, operations[0] if operations else {}, machines[0] if machines else {})
                })

    return alternatives


def _update_scheduling_result(scheduling_run: str, job_card: str, updates: Dict):
    """Update APS Scheduling Result record."""
    result = frappe.db.exists("APS Scheduling Result", {
        "scheduling_run": scheduling_run,
        "job_card": job_card
    })

    if result:
        frappe.db.set_value("APS Scheduling Result", result, updates)
        frappe.db.commit()
