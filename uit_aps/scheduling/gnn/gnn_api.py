# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
GNN API Endpoints for Scheduling

Provides Frappe API endpoints for GNN-based scheduling features:
- Bottleneck prediction
- Duration prediction
- Delay prediction
- Strategic recommendations
"""

import frappe
from frappe import _
from frappe.utils import now_datetime
from typing import List, Dict, Optional, Any
import json

# Check PyTorch availability
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def check_gnn_available():
    """Check if GNN features are available."""
    if not TORCH_AVAILABLE:
        frappe.throw(
            _("PyTorch is not installed. GNN features require PyTorch. "
              "Install with: pip install torch"),
            title=_("GNN Not Available")
        )


@frappe.whitelist()
def get_gnn_status() -> dict:
    """
    Get status of GNN tier.

    Returns:
        dict with GNN availability and capabilities
    """
    status = {
        "available": TORCH_AVAILABLE,
        "version": "1.0.0",
        "capabilities": []
    }

    if TORCH_AVAILABLE:
        import torch
        status["pytorch_version"] = torch.__version__
        status["device"] = "cuda" if torch.cuda.is_available() else "cpu"
        status["capabilities"] = [
            "bottleneck_prediction",
            "duration_prediction",
            "delay_prediction",
            "recommendations",
            "graph_encoding",
            "rl_integration"
        ]
        status["status"] = "Ready"
    else:
        status["status"] = "PyTorch not installed"

    return status


@frappe.whitelist()
def predict_bottlenecks(
    scheduling_run: str = None,
    schedule_data: str = None,
    machines_data: str = None,
    threshold: float = 0.7
) -> dict:
    """
    Predict which machines will become bottlenecks.

    Args:
        scheduling_run: APS Scheduling Run name (loads data from this)
        schedule_data: JSON string of schedule operations (alternative to scheduling_run)
        machines_data: JSON string of machines (alternative to scheduling_run)
        threshold: Probability threshold for bottleneck classification

    Returns:
        dict with bottleneck predictions
    """
    check_gnn_available()

    from uit_aps.scheduling.gnn.predictors import BottleneckPredictor, PredictorConfig

    # Load data
    schedule, machines = _load_schedule_data(
        scheduling_run, schedule_data, machines_data
    )

    # Create predictor and predict
    config = PredictorConfig()
    predictor = BottleneckPredictor(config)

    result = predictor.predict(schedule, machines, threshold=threshold)

    # Add metadata
    result["scheduling_run"] = scheduling_run
    result["timestamp"] = str(now_datetime())
    result["threshold"] = threshold

    return result


@frappe.whitelist()
def predict_durations(
    scheduling_run: str = None,
    schedule_data: str = None,
    machines_data: str = None,
    confidence_level: float = 0.95
) -> dict:
    """
    Predict actual vs expected processing durations.

    Args:
        scheduling_run: APS Scheduling Run name
        schedule_data: JSON string of schedule operations
        machines_data: JSON string of machines
        confidence_level: Confidence level for intervals

    Returns:
        dict with duration predictions
    """
    check_gnn_available()

    from uit_aps.scheduling.gnn.predictors import DurationPredictor, PredictorConfig

    # Load data
    schedule, machines = _load_schedule_data(
        scheduling_run, schedule_data, machines_data
    )

    # Create predictor and predict
    config = PredictorConfig()
    predictor = DurationPredictor(config)

    result = predictor.predict(schedule, machines, confidence_level=confidence_level)

    # Add metadata
    result["scheduling_run"] = scheduling_run
    result["timestamp"] = str(now_datetime())
    result["confidence_level"] = confidence_level

    return result


@frappe.whitelist()
def predict_delays(
    scheduling_run: str = None,
    schedule_data: str = None,
    machines_data: str = None,
    delay_threshold: float = 0.5
) -> dict:
    """
    Predict potential delays in the schedule.

    Args:
        scheduling_run: APS Scheduling Run name
        schedule_data: JSON string of schedule operations
        machines_data: JSON string of machines
        delay_threshold: Probability threshold for flagging delays

    Returns:
        dict with delay predictions
    """
    check_gnn_available()

    from uit_aps.scheduling.gnn.predictors import DelayPredictor, PredictorConfig

    # Load data
    schedule, machines = _load_schedule_data(
        scheduling_run, schedule_data, machines_data
    )

    # Create predictor and predict
    config = PredictorConfig()
    predictor = DelayPredictor(config)

    result = predictor.predict(schedule, machines, delay_threshold=delay_threshold)

    # Add metadata
    result["scheduling_run"] = scheduling_run
    result["timestamp"] = str(now_datetime())
    result["delay_threshold"] = delay_threshold

    return result


@frappe.whitelist()
def get_all_predictions(
    scheduling_run: str = None,
    schedule_data: str = None,
    machines_data: str = None
) -> dict:
    """
    Get all predictions (bottleneck, duration, delay) in one call.

    Args:
        scheduling_run: APS Scheduling Run name
        schedule_data: JSON string of schedule operations
        machines_data: JSON string of machines

    Returns:
        dict with all predictions
    """
    check_gnn_available()

    from uit_aps.scheduling.gnn.predictors import SchedulingPredictor, PredictorConfig

    # Load data
    schedule, machines = _load_schedule_data(
        scheduling_run, schedule_data, machines_data
    )

    # Create combined predictor
    config = PredictorConfig()
    predictor = SchedulingPredictor(config)

    result = predictor.predict_all(schedule, machines)

    # Add metadata
    result["scheduling_run"] = scheduling_run
    result["timestamp"] = str(now_datetime())

    return result


@frappe.whitelist()
def get_critical_insights(
    scheduling_run: str = None,
    schedule_data: str = None,
    machines_data: str = None
) -> dict:
    """
    Get the most critical insights from all predictions.

    Args:
        scheduling_run: APS Scheduling Run name
        schedule_data: JSON string of schedule operations
        machines_data: JSON string of machines

    Returns:
        dict with critical insights and recommendations
    """
    check_gnn_available()

    from uit_aps.scheduling.gnn.predictors import SchedulingPredictor, PredictorConfig

    # Load data
    schedule, machines = _load_schedule_data(
        scheduling_run, schedule_data, machines_data
    )

    # Get critical insights
    config = PredictorConfig()
    predictor = SchedulingPredictor(config)

    result = predictor.get_critical_insights(schedule, machines)

    # Add metadata
    result["scheduling_run"] = scheduling_run
    result["timestamp"] = str(now_datetime())

    return result


@frappe.whitelist()
def get_recommendations(
    scheduling_run: str = None,
    schedule_data: str = None,
    machines_data: str = None,
    historical_data: str = None,
    max_recommendations: int = 10
) -> dict:
    """
    Get strategic recommendations based on GNN analysis.

    Args:
        scheduling_run: APS Scheduling Run name
        schedule_data: JSON string of schedule operations
        machines_data: JSON string of machines
        historical_data: JSON string of historical data (optional)
        max_recommendations: Maximum number of recommendations

    Returns:
        dict with recommendations
    """
    from uit_aps.scheduling.gnn.recommendation import (
        RecommendationEngine, RecommendationConfig
    )

    # Load data
    schedule, machines = _load_schedule_data(
        scheduling_run, schedule_data, machines_data
    )

    # Parse historical data if provided
    history = None
    if historical_data:
        try:
            history = json.loads(historical_data)
        except json.JSONDecodeError:
            pass

    # Create engine and analyze
    config = RecommendationConfig(max_recommendations=max_recommendations)
    engine = RecommendationEngine(config)

    result = engine.analyze(schedule, machines, history)

    # Add metadata
    result["scheduling_run"] = scheduling_run
    result["timestamp"] = str(now_datetime())

    return result


@frappe.whitelist()
def encode_schedule_graph(
    scheduling_run: str = None,
    schedule_data: str = None,
    machines_data: str = None
) -> dict:
    """
    Encode schedule as graph embedding.

    This is useful for:
    - Similarity search between schedules
    - Clustering of schedule patterns
    - Feature extraction for downstream models

    Args:
        scheduling_run: APS Scheduling Run name
        schedule_data: JSON string of schedule operations
        machines_data: JSON string of machines

    Returns:
        dict with graph embedding and metadata
    """
    check_gnn_available()

    from uit_aps.scheduling.gnn.encoder import SchedulingGraphEncoder, EncoderConfig
    from uit_aps.scheduling.gnn.graph import build_graph_from_schedule

    # Load data
    schedule, machines = _load_schedule_data(
        scheduling_run, schedule_data, machines_data
    )

    # Build graph
    graph = build_graph_from_schedule(schedule, machines)

    # Encode
    config = EncoderConfig()
    encoder = SchedulingGraphEncoder(config)

    # Import torch here after check_gnn_available() has verified it's installed
    import torch
    with torch.no_grad():
        embedding = encoder.encode_graph(graph)

    return {
        "embedding": embedding.tolist(),
        "embedding_dim": len(embedding),
        "graph_info": {
            "num_jobs": graph.num_jobs,
            "num_operations": graph.num_operations,
            "num_machines": graph.num_machines,
            "num_edges": len(graph.edges)
        },
        "scheduling_run": scheduling_run,
        "timestamp": str(now_datetime())
    }


@frappe.whitelist()
def get_operation_embeddings(
    scheduling_run: str = None,
    schedule_data: str = None,
    machines_data: str = None
) -> dict:
    """
    Get GNN embeddings for each operation.

    Useful for:
    - Finding similar operations
    - Operation clustering
    - Anomaly detection

    Args:
        scheduling_run: APS Scheduling Run name
        schedule_data: JSON string of schedule operations
        machines_data: JSON string of machines

    Returns:
        dict with operation embeddings
    """
    check_gnn_available()

    from uit_aps.scheduling.gnn.encoder import SchedulingGraphEncoder, EncoderConfig
    from uit_aps.scheduling.gnn.graph import build_graph_from_schedule

    # Load data
    schedule, machines = _load_schedule_data(
        scheduling_run, schedule_data, machines_data
    )

    # Build graph and get embeddings
    graph = build_graph_from_schedule(schedule, machines)
    config = EncoderConfig()
    encoder = SchedulingGraphEncoder(config)

    # Import torch here after check_gnn_available() has verified it's installed
    import torch
    with torch.no_grad():
        embeddings = encoder.get_node_embeddings(graph)

    op_embeddings = embeddings.get("operations")

    if op_embeddings is None:
        return {
            "operations": [],
            "scheduling_run": scheduling_run,
            "timestamp": str(now_datetime())
        }

    # Build result with operation IDs
    result = {
        "operations": [],
        "embedding_dim": op_embeddings.shape[1] if len(op_embeddings.shape) > 1 else 0,
        "scheduling_run": scheduling_run,
        "timestamp": str(now_datetime())
    }

    for i, op in enumerate(schedule):
        op_id = op.get("operation_id") or op.get("job_card")
        if i < len(op_embeddings):
            result["operations"].append({
                "operation_id": op_id,
                "job_id": op.get("job_id") or op.get("work_order"),
                "embedding": op_embeddings[i].tolist()
            })

    return result


@frappe.whitelist()
def train_gnn_model(
    model_type: str = "combined",
    training_runs: str = None,
    epochs: int = 100,
    learning_rate: float = 1e-4
) -> dict:
    """
    Train a GNN prediction model.

    Args:
        model_type: "bottleneck", "duration", "delay", or "combined"
        training_runs: Comma-separated list of scheduling run names
        epochs: Number of training epochs
        learning_rate: Learning rate

    Returns:
        dict with training results
    """
    check_gnn_available()

    import os
    from uit_aps.scheduling.gnn.predictors import create_predictor, PredictorConfig

    # Parse training runs
    run_names = []
    if training_runs:
        run_names = [r.strip() for r in training_runs.split(",")]

    if not run_names:
        return {
            "success": False,
            "message": "No training runs specified"
        }

    # Load training data
    training_data = []
    for run_name in run_names:
        try:
            schedule, machines = _load_schedule_data(run_name, None, None)
            training_data.append({
                "schedule": schedule,
                "machines": machines,
                "run_name": run_name
            })
        except Exception as e:
            frappe.log_error(str(e), f"Failed to load training data: {run_name}")

    if not training_data:
        return {
            "success": False,
            "message": "Failed to load any training data"
        }

    # Create and train model
    config = PredictorConfig(learning_rate=learning_rate)
    predictor = create_predictor(model_type, config)

    # Note: Actual training would require labeled data (actual outcomes)
    # This is a placeholder for the training logic

    # Save model
    model_dir = frappe.get_site_path("private", "files", "gnn_models")
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, f"{model_type}_model.pt")

    try:
        # Import torch here after check_gnn_available() has verified it's installed
        import torch
        torch.save(predictor.state_dict(), model_path)
    except Exception as e:
        frappe.log_error(str(e), "Failed to save GNN model")

    return {
        "success": True,
        "model_type": model_type,
        "training_runs": run_names,
        "model_path": model_path,
        "message": f"Model placeholder created at {model_path}. "
                   "Note: Full training requires labeled outcome data."
    }


def _load_schedule_data(
    scheduling_run: str,
    schedule_data: str,
    machines_data: str
) -> tuple:
    """
    Load schedule and machine data from various sources.

    Args:
        scheduling_run: APS Scheduling Run name
        schedule_data: JSON string of schedule
        machines_data: JSON string of machines

    Returns:
        Tuple of (schedule list, machines list)
    """
    schedule = []
    machines = []

    # Try to load from JSON strings first
    if schedule_data:
        try:
            schedule = json.loads(schedule_data)
        except json.JSONDecodeError:
            frappe.throw(_("Invalid schedule_data JSON"))

    if machines_data:
        try:
            machines = json.loads(machines_data)
        except json.JSONDecodeError:
            frappe.throw(_("Invalid machines_data JSON"))

    # If scheduling_run provided and data not already loaded
    if scheduling_run and (not schedule or not machines):
        schedule, machines = _load_from_scheduling_run(scheduling_run)

    if not schedule:
        frappe.throw(_("No schedule data available"))

    if not machines:
        # Try to extract machines from schedule
        machines = _extract_machines_from_schedule(schedule)

    return schedule, machines


def _load_from_scheduling_run(scheduling_run: str) -> tuple:
    """Load data from an APS Scheduling Run document."""
    schedule = []
    machines = []

    # Check if document exists
    if not frappe.db.exists("APS Scheduling Run", scheduling_run):
        frappe.throw(_("Scheduling run {0} not found").format(scheduling_run))

    # Load scheduling results with correct field names from APS Scheduling Result doctype
    # Fields: job_card, workstation, operation, planned_start_time, planned_end_time, is_late
    results = frappe.get_all(
        "APS Scheduling Result",
        filters={"scheduling_run": scheduling_run},
        fields=[
            "name", "job_card", "workstation", "operation",
            "planned_start_time", "planned_end_time", "is_late"
        ]
    )

    for idx, r in enumerate(results):
        # Calculate duration from start and end times
        duration = 0
        start_mins = 0
        end_mins = 0

        if r.planned_start_time and r.planned_end_time:
            duration = int((r.planned_end_time - r.planned_start_time).total_seconds() / 60)
            start_mins = r.planned_start_time.timestamp() / 60
            end_mins = r.planned_end_time.timestamp() / 60

        # Get work_order from job_card if available
        work_order = None
        if r.job_card:
            work_order = frappe.db.get_value("Job Card", r.job_card, "work_order")

        schedule.append({
            "operation_id": r.job_card,
            "job_id": work_order or r.job_card,  # Use work_order if available, else job_card
            "machine_id": r.workstation,
            "start_time": start_mins,
            "end_time": end_mins,
            "duration": duration,
            "status": "late" if r.is_late else "on_time",
            "sequence": idx  # Use index as sequence
        })

    # Load unique workstations
    workstations = set(r.workstation for r in results if r.workstation)

    for ws_name in workstations:
        try:
            ws = frappe.get_doc("Workstation", ws_name)
            machines.append({
                "machine_id": ws_name,
                "machine_type": ws.workstation_type or "default",
                "capacity": 1.0,
                "status": "available"
            })
        except frappe.DoesNotExistError:
            machines.append({
                "machine_id": ws_name,
                "machine_type": "unknown",
                "capacity": 1.0,
                "status": "available"
            })

    return schedule, machines


def _extract_machines_from_schedule(schedule: List[Dict]) -> List[Dict]:
    """Extract unique machines from schedule data."""
    machines = {}

    for op in schedule:
        machine_id = op.get("machine_id") or op.get("workstation")
        if machine_id and machine_id not in machines:
            machines[machine_id] = {
                "machine_id": machine_id,
                "machine_type": op.get("machine_type", "default"),
                "capacity": 1.0,
                "status": "available"
            }

    return list(machines.values())
