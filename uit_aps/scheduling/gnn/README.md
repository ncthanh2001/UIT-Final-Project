# Tier 3: Graph Neural Networks for Scheduling

## Overview

Tier 3 of the Hybrid APS system uses **Graph Neural Networks (GNN)** to learn structural patterns in scheduling problems. While Tier 1 (OR-Tools) finds optimal schedules and Tier 2 (RL) handles real-time adjustments, Tier 3 provides:

- **Pattern Recognition**: Learn recurring patterns in scheduling data
- **Bottleneck Prediction**: Predict which machines will become bottlenecks
- **Duration Prediction**: Predict actual vs expected processing times
- **Strategic Recommendations**: Long-term capacity and workflow suggestions

### When to Use Tier 3

| Scenario | Use Tier 3? |
|----------|-------------|
| Identify future bottlenecks | ✅ Yes |
| Predict processing delays | ✅ Yes |
| Capacity planning decisions | ✅ Yes |
| Schedule similarity analysis | ✅ Yes |
| Enhanced RL state encoding | ✅ Yes |
| Real-time rescheduling | ❌ Use Tier 2 |
| Initial schedule creation | ❌ Use Tier 1 |

## Architecture

```
gnn/
├── __init__.py           # Module initialization
├── README.md             # This file
├── graph.py              # Graph construction
├── layers.py             # GNN layers (GAT, GCN)
├── encoder.py            # Graph encoding
├── predictors.py         # Prediction models
├── recommendation.py     # Recommendation engine
├── rl_integration.py     # RL integration
└── gnn_api.py            # Frappe API endpoints
```

## Installation

```bash
# Install PyTorch (required for Tier 3)
pip install torch

# Optional: Install scipy for confidence intervals
pip install scipy

# Verify installation
python -c "import torch; print(f'PyTorch {torch.__version__} installed')"
```

**Note:** Tier 3 is optional. If PyTorch is not installed, Tiers 1 and 2 will still work.

---

## Quick Start

### 1. Predict Bottlenecks

```python
import frappe

result = frappe.call(
    "uit_aps.scheduling.gnn.gnn_api.predict_bottlenecks",
    scheduling_run="SCH-RUN-00001",
    threshold=0.7
)

if result["bottlenecks"]:
    for b in result["bottlenecks"]:
        print(f"{b['machine_id']}: {b['bottleneck_probability']:.0%} probability")
```

### 2. Get Strategic Recommendations

```python
result = frappe.call(
    "uit_aps.scheduling.gnn.gnn_api.get_recommendations",
    scheduling_run="SCH-RUN-00001",
    max_recommendations=5
)

for rec in result["recommendations"]:
    print(f"[{rec['priority']}] {rec['title']}")
    print(f"  Impact: {rec['impact']}")
```

### 3. Encode Schedule for Analysis

```python
result = frappe.call(
    "uit_aps.scheduling.gnn.gnn_api.encode_schedule_graph",
    scheduling_run="SCH-RUN-00001"
)

embedding = result["embedding"]  # Fixed-size vector
print(f"Schedule encoded to {result['embedding_dim']}-dim vector")
```

---

## Graph Representation

### Node Types

| Type | Description | Features |
|------|-------------|----------|
| **Job** | Production job | Due date, priority, num_ops, status |
| **Operation** | Individual operation | Start, end, duration, machine, sequence |
| **Machine** | Workstation | Type, capacity, utilization, status |

### Edge Types

| Type | Description |
|------|-------------|
| **JOB_TO_OPERATION** | Job contains operation |
| **PRECEDENCE** | Operation sequence constraint |
| **MACHINE_ASSIGNMENT** | Operation assigned to machine |
| **MACHINE_CAPABLE** | Machine can process operation |
| **TEMPORAL** | Operations close in time |

### Building a Graph

```python
from uit_aps.scheduling.gnn.graph import build_graph_from_schedule

schedule = [
    {"operation_id": "OP-001", "job_id": "JOB-001", "machine_id": "WS-001",
     "start_time": 0, "end_time": 60, "duration": 60},
    # ... more operations
]

machines = [
    {"machine_id": "WS-001", "machine_type": "cutting", "utilization": 0.8},
    # ... more machines
]

graph = build_graph_from_schedule(schedule, machines)
print(graph)  # SchedulingGraph(jobs=1, operations=1, machines=1, edges=2)
```

---

## GNN Layers

### Graph Attention Network (GAT)

```python
from uit_aps.scheduling.gnn.layers import GraphAttentionLayer, GATLayerConfig

config = GATLayerConfig(
    in_features=64,
    out_features=64,
    num_heads=4,
    dropout=0.1,
    edge_dim=8  # Use edge features
)

gat_layer = GraphAttentionLayer(config)
```

### Graph Convolutional Network (GCN)

```python
from uit_aps.scheduling.gnn.layers import GraphConvLayer, GCNLayerConfig

config = GCNLayerConfig(
    in_features=64,
    out_features=64,
    normalize=True
)

gcn_layer = GraphConvLayer(config)
```

### Scheduling GNN Block

```python
from uit_aps.scheduling.gnn.layers import SchedulingGNNBlock

gnn_block = SchedulingGNNBlock(
    hidden_dim=128,
    edge_dim=8,
    num_heads=4,
    num_layers=3,
    dropout=0.1
)
```

---

## Graph Encoder

Converts graphs to fixed-size vector embeddings.

```python
from uit_aps.scheduling.gnn.encoder import SchedulingGraphEncoder, EncoderConfig

config = EncoderConfig(
    hidden_dim=128,
    output_dim=256,
    num_gnn_layers=3,
    num_attention_heads=4,
    pooling="attention"  # or "mean", "max", "set2set"
)

encoder = SchedulingGraphEncoder(config)

# Encode graph
graph_data = graph.to_tensors()
result = encoder(graph_data)

embedding = result["embedding"]  # [256]
node_embeddings = result["node_embeddings"]  # [N, 128]
```

---

## Prediction Models

### Bottleneck Predictor

Predicts probability of each machine becoming a bottleneck.

```python
from uit_aps.scheduling.gnn.predictors import BottleneckPredictor, PredictorConfig

predictor = BottleneckPredictor(PredictorConfig())
result = predictor.predict(schedule, machines, threshold=0.7)

# result["bottlenecks"] - List of bottleneck machines
# result["all_machines"] - All machines with probabilities
# result["summary"] - Statistics
```

### Duration Predictor

Predicts actual vs expected processing duration.

```python
from uit_aps.scheduling.gnn.predictors import DurationPredictor

predictor = DurationPredictor(PredictorConfig())
result = predictor.predict(schedule, machines, confidence_level=0.95)

# result["operations"] - Duration predictions per operation
# result["at_risk"] - Operations likely to overrun
# result["summary"] - Statistics
```

### Delay Predictor

Predicts delays and cascade effects.

```python
from uit_aps.scheduling.gnn.predictors import DelayPredictor

predictor = DelayPredictor(PredictorConfig())
result = predictor.predict(schedule, machines, delay_threshold=0.5)

# result["high_risk"] - High delay risk operations
# result["cascade_risks"] - Operations that can cascade delays
# result["summary"] - Total expected delay
```

### Combined Predictor

```python
from uit_aps.scheduling.gnn.predictors import SchedulingPredictor

predictor = SchedulingPredictor(PredictorConfig())

# Get all predictions
result = predictor.predict_all(schedule, machines)

# Get critical insights with recommendations
insights = predictor.get_critical_insights(schedule, machines)
```

---

## Recommendation Engine

Generates strategic recommendations based on pattern analysis.

```python
from uit_aps.scheduling.gnn.recommendation import RecommendationEngine, RecommendationConfig

config = RecommendationConfig(
    bottleneck_threshold=0.7,
    utilization_high_threshold=0.9,
    max_recommendations=10
)

engine = RecommendationEngine(config)
result = engine.analyze(schedule, machines, historical_data=None)

for rec in result["recommendations"]:
    print(f"[{rec['priority']}] {rec['title']}")
    print(f"  Type: {rec['type']}")
    print(f"  Impact: {rec['impact']}")
    print(f"  Effort: {rec['implementation_effort']}")
    print(f"  Confidence: {rec['confidence']:.0%}")
```

### Recommendation Types

| Type | Description |
|------|-------------|
| `CAPACITY_INCREASE` | Add capacity to overloaded machines |
| `CAPACITY_DECREASE` | Consolidate underutilized machines |
| `MAINTENANCE_SCHEDULE` | Preventive maintenance suggestions |
| `WORKFLOW_OPTIMIZATION` | Process improvement opportunities |
| `RESOURCE_REALLOCATION` | Balance workload distribution |
| `SCHEDULE_BUFFER` | Add buffer time for tight schedules |
| `PARALLEL_PROCESSING` | Parallelize long sequences |
| `PRIORITY_ADJUSTMENT` | Adjust job priorities |
| `MACHINE_UPGRADE` | Upgrade critical machines |

---

## RL Integration

### GNN-Enhanced State Encoder

Provides richer state representation for RL agents.

```python
from uit_aps.scheduling.gnn.rl_integration import GNNStateEncoder, GNNRLConfig

config = GNNRLConfig(
    gnn_hidden_dim=128,
    use_gnn_state=True,
    update_gnn_frequency=10  # Update every 10 steps
)

encoder = GNNStateEncoder(config)

# Get state embedding
embedding = encoder.encode(schedule, machines)
```

### GNN-Enhanced Policy

Policy network that uses GNN embeddings for decision making.

```python
from uit_aps.scheduling.gnn.rl_integration import GNNEnhancedPolicy

policy = GNNEnhancedPolicy(
    flat_state_dim=3216,  # From RL environment
    action_dim=7,
    config=GNNRLConfig()
)

# Get action
action, log_prob = policy.get_action(flat_state, schedule, machines)
```

### GNN Action Selector

Uses GNN to select specific operations and machines.

```python
from uit_aps.scheduling.gnn.rl_integration import GNNActionSelector

selector = GNNActionSelector(GNNRLConfig())

# Select operation to act on
op_idx, confidence = selector.select_operation(schedule, machines)

# Select machine to reassign to
machine_idx, confidence = selector.select_machine(schedule, machines, op_idx)
```

---

## API Reference

### `get_gnn_status()`

Check GNN tier availability.

```python
frappe.call("uit_aps.scheduling.gnn.gnn_api.get_gnn_status")
```

**Response:**
```json
{
    "available": true,
    "pytorch_version": "2.0.1",
    "device": "cpu",
    "capabilities": ["bottleneck_prediction", "duration_prediction", ...],
    "status": "Ready"
}
```

### `predict_bottlenecks()`

Predict machine bottlenecks.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `scheduling_run` | str | No | APS Scheduling Run name |
| `schedule_data` | str | No | JSON schedule data |
| `machines_data` | str | No | JSON machines data |
| `threshold` | float | No | Probability threshold (default: 0.7) |

### `predict_durations()`

Predict processing durations.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `scheduling_run` | str | No | APS Scheduling Run name |
| `schedule_data` | str | No | JSON schedule data |
| `machines_data` | str | No | JSON machines data |
| `confidence_level` | float | No | Confidence level (default: 0.95) |

### `predict_delays()`

Predict schedule delays.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `scheduling_run` | str | No | APS Scheduling Run name |
| `schedule_data` | str | No | JSON schedule data |
| `machines_data` | str | No | JSON machines data |
| `delay_threshold` | float | No | Delay threshold (default: 0.5) |

### `get_recommendations()`

Get strategic recommendations.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `scheduling_run` | str | No | APS Scheduling Run name |
| `schedule_data` | str | No | JSON schedule data |
| `machines_data` | str | No | JSON machines data |
| `historical_data` | str | No | JSON historical data |
| `max_recommendations` | int | No | Max recommendations (default: 10) |

### `encode_schedule_graph()`

Encode schedule as embedding vector.

**Response:**
```json
{
    "embedding": [0.1, 0.2, ...],
    "embedding_dim": 256,
    "graph_info": {
        "num_jobs": 5,
        "num_operations": 20,
        "num_machines": 8,
        "num_edges": 45
    }
}
```

---

## JavaScript Integration

### Get Bottleneck Predictions

```javascript
frappe.call({
    method: "uit_aps.scheduling.gnn.gnn_api.predict_bottlenecks",
    args: {
        scheduling_run: cur_frm.doc.name,
        threshold: 0.7
    },
    callback: function(r) {
        if (r.message.bottlenecks.length > 0) {
            show_bottleneck_warning(r.message.bottlenecks);
        }
    }
});
```

### Get Recommendations

```javascript
frappe.call({
    method: "uit_aps.scheduling.gnn.gnn_api.get_recommendations",
    args: {
        scheduling_run: cur_frm.doc.name,
        max_recommendations: 5
    },
    callback: function(r) {
        show_recommendations_dialog(r.message.recommendations);
    }
});

function show_recommendations_dialog(recommendations) {
    let html = '<ul>';
    recommendations.forEach(rec => {
        html += `<li>
            <strong>[${rec.priority}]</strong> ${rec.title}<br>
            <small>${rec.description}</small>
        </li>`;
    });
    html += '</ul>';

    frappe.msgprint({
        title: __('Strategic Recommendations'),
        message: html,
        indicator: 'blue'
    });
}
```

---

## Configuration

### Encoder Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `hidden_dim` | 128 | Hidden layer dimension |
| `output_dim` | 256 | Output embedding dimension |
| `num_gnn_layers` | 3 | Number of GNN layers |
| `num_attention_heads` | 4 | Attention heads |
| `pooling` | "attention" | Pooling method |
| `dropout` | 0.1 | Dropout rate |

### Predictor Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `hidden_dim` | 128 | Hidden dimension |
| `predictor_hidden_dim` | 64 | Predictor layer dimension |
| `num_predictor_layers` | 2 | Predictor layers |
| `learning_rate` | 1e-4 | Training learning rate |

### Recommendation Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `bottleneck_threshold` | 0.7 | Bottleneck probability threshold |
| `utilization_high_threshold` | 0.9 | High utilization threshold |
| `utilization_low_threshold` | 0.3 | Low utilization threshold |
| `min_confidence` | 0.6 | Minimum recommendation confidence |
| `max_recommendations` | 10 | Maximum recommendations |

---

## Hybrid Integration

### Three-Tier Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                     Production Plan                          │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Tier 3: GNN Analysis                                        │
│  ├─ Bottleneck Prediction                                    │
│  ├─ Duration Prediction                                      │
│  └─ Strategic Recommendations                                │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Tier 1: OR-Tools                                            │
│  └─ Optimal Schedule (with Tier 3 insights)                  │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Tier 2: RL Agent (with GNN state encoding)                  │
│  └─ Real-time Adjustments                                    │
└─────────────────────────────────────────────────────────────┘
```

### Using All Three Tiers

```python
from uit_aps.scheduling.hybrid_scheduler import HybridScheduler, HybridSchedulerConfig
from uit_aps.scheduling.gnn.predictors import SchedulingPredictor
from uit_aps.scheduling.gnn.recommendation import RecommendationEngine

# Step 1: GNN Analysis
predictor = SchedulingPredictor()
insights = predictor.get_critical_insights(schedule, machines)

engine = RecommendationEngine()
recommendations = engine.analyze(schedule, machines)

# Step 2: Apply insights to Tier 1 scheduling
# (e.g., add buffer time, adjust weights for bottleneck machines)

# Step 3: Run hybrid scheduling with GNN-enhanced RL
config = HybridSchedulerConfig(
    enable_rl_adjustments=True,
    rl_agent_type="ppo"
)
scheduler = HybridScheduler(config)
result = scheduler.schedule(production_plan="PP-2025-001")
```

---

## Troubleshooting

### PyTorch Not Found

```
Error: PyTorch not installed
Solution: pip install torch
```

### Out of Memory

```
Error: CUDA out of memory
Solutions:
1. Use CPU: config.device = "cpu"
2. Reduce hidden_dim
3. Reduce num_gnn_layers
```

### Slow Predictions

```
Issue: Predictions taking too long
Solutions:
1. Reduce num_gnn_layers (3 → 2)
2. Reduce hidden_dim (128 → 64)
3. Use simpler pooling ("mean" instead of "attention")
```

### No Recommendations

```
Issue: Engine returns empty recommendations
Causes:
- All metrics within normal ranges
- Confidence below threshold

Solutions:
1. Lower min_confidence threshold
2. Include low priority recommendations
```

---

## Performance Tips

1. **Cache embeddings**: Use `update_gnn_frequency` to avoid recalculating every step
2. **Batch predictions**: Process multiple schedules together when possible
3. **Use appropriate complexity**: Start with fewer layers and increase if needed
4. **GPU acceleration**: Use CUDA if available for large graphs

---

## References

- [Graph Attention Networks](https://arxiv.org/abs/1710.10903) - Velickovic et al., 2018
- [Semi-Supervised Classification with GCN](https://arxiv.org/abs/1609.02907) - Kipf & Welling, 2017
- [PyTorch Geometric](https://pytorch-geometric.readthedocs.io/)
- [Job Shop Scheduling with GNN](https://arxiv.org/abs/2003.01604)

---

## License

MIT License - See project root for details.

## Author

thanhnc - UIT APS Project
