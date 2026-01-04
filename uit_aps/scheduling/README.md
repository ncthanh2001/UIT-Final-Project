# UIT APS Scheduling Module

## Overview

This module implements the **Hybrid APS (Advanced Planning & Scheduling)** system with multiple tiers:

| Tier | Technology | Purpose | Status |
|------|------------|---------|--------|
| **Tier 1** | OR-Tools CP-SAT | Optimal offline scheduling | ✅ Implemented |
| **Tier 2** | RL (PPO/SAC) | Real-time adjustments | ✅ Implemented |
| **Tier 3** | GNN Encoder | Pattern learning & predictions | ✅ Implemented |

The scheduling system solves the **Job Shop Scheduling Problem (JSSP)** - assigning manufacturing operations to machines while respecting constraints and optimizing objectives.

## Architecture

```
scheduling/
├── __init__.py                 # Module initialization
├── README.md                   # This file
├── hybrid_scheduler.py         # Unified hybrid scheduler
├── ortools/                    # Tier 1: OR-Tools CP-SAT
│   ├── __init__.py
│   ├── models.py               # Data models and structures
│   └── scheduler.py            # CP-SAT solver implementation
├── rl/                         # Tier 2: Reinforcement Learning
│   ├── __init__.py
│   ├── environment.py          # Gymnasium-compatible env
│   ├── state_encoder.py        # State feature encoding
│   ├── reward.py               # Reward functions
│   ├── trainer.py              # Training pipeline
│   ├── realtime_api.py         # Real-time adjustment API
│   └── agents/
│       ├── __init__.py
│       ├── base.py             # Base agent class
│       ├── ppo.py              # PPO implementation
│       └── sac.py              # SAC implementation
├── gnn/                        # Tier 3: Graph Neural Networks
│   ├── __init__.py
│   ├── graph.py                # Graph construction
│   ├── layers.py               # GNN layers (GAT, GCN)
│   ├── encoder.py              # Graph encoding
│   ├── predictors.py           # Bottleneck/Duration predictors
│   ├── recommendation.py       # Strategic recommendations
│   ├── rl_integration.py       # GNN-RL integration
│   └── gnn_api.py              # Frappe API endpoints
├── data/
│   ├── __init__.py
│   ├── erpnext_loader.py       # ERPNext data extraction
│   └── exporters.py            # Result export to ERPNext
└── api/
    ├── __init__.py
    └── scheduling_api.py       # Frappe REST API endpoints
```

## Requirements

### Python Dependencies

```bash
# Tier 1: OR-Tools (required)
pip install ortools

# Tier 2 & 3: PyTorch (optional, for RL agents and GNN)
pip install torch

# Optional: scipy for confidence intervals (Tier 3)
pip install scipy

# Full installation
pip install ortools torch numpy scipy
```

### ERPNext Dependencies

The module integrates with ERPNext Manufacturing doctypes:
- **Work Order** - Production jobs
- **Job Card** - Individual operations
- **Workstation** - Machines/resources
- **BOM** - Bill of Materials

And custom UIT APS doctypes:
- **APS Production Plan** - Production planning
- **APS Scheduling Run** - Scheduling execution records
- **APS Scheduling Result** - Individual operation results

---

# Tier 1: OR-Tools CP-SAT Solver

## Overview

Tier 1 uses Google OR-Tools Constraint Programming SAT solver for finding optimal production schedules. It's best for:
- Initial schedule creation
- Batch scheduling problems
- When optimality is critical

## Constraints

| Constraint | Description |
|------------|-------------|
| **Precedence** | Operations within a job follow sequence order |
| **No-Overlap** | Each machine processes one operation at a time |
| **Capacity** | Operations assigned to eligible machines |

## Objective Function

```
Minimize: makespan_weight × Makespan + tardiness_weight × Total_Tardiness
```

Default weights: `makespan_weight=1.0`, `tardiness_weight=10.0`

## API Reference

### `run_ortools_scheduling()`

```python
frappe.call({
    method: "uit_aps.scheduling.api.scheduling_api.run_ortools_scheduling",
    args: {
        production_plan: "PP-2025-001",
        time_limit_seconds: 300,
        makespan_weight: 1.0,
        tardiness_weight: 10.0
    }
})
```

### Response
```json
{
    "success": true,
    "scheduling_run": "SCH-RUN-00001",
    "status": "Optimal",
    "makespan_minutes": 480,
    "jobs_on_time": 4,
    "jobs_late": 1,
    "solve_time_seconds": 2.34
}
```

---

# Tier 2: RL Agents (PPO/SAC)

## Overview

Tier 2 uses Reinforcement Learning agents for real-time scheduling adjustments. It handles:
- Machine breakdowns
- Rush orders
- Processing delays
- Dynamic rescheduling

## Available Agents

| Agent | Type | Best For |
|-------|------|----------|
| **PPO** | On-policy | Stable learning, discrete actions |
| **SAC** | Off-policy | Sample efficient, continuous exploration |

## RL Environment

The `SchedulingEnv` simulates a dynamic job shop with:
- Discrete time steps (configurable, default 15 min)
- Stochastic disruptions
- Multi-component action space

### Observation Space

| Component | Features | Description |
|-----------|----------|-------------|
| Operations | 8 per op | start, end, duration, due, priority, status, machine, is_late |
| Machines | 6 per machine | status, utilization, current_op, remaining, capacity, type |
| Global | 5 | time, pending, disruptions, tardiness, completed |

### Action Space

| Action | Description |
|--------|-------------|
| NO_OP | No action needed |
| REASSIGN_MACHINE | Move operation to different machine |
| RESCHEDULE_EARLIER | Move operation 30 min earlier |
| RESCHEDULE_LATER | Move operation 30 min later |
| PRIORITIZE_JOB | Increase job priority |
| SPLIT_BATCH | Split large batch |
| MERGE_OPERATIONS | Combine operations |

## Reward Function

Multiple reward strategies available:

| Strategy | Description |
|----------|-------------|
| **Sparse** | Reward only at episode end |
| **Dense** | Reward at each step |
| **Shaped** | Potential-based shaping |
| **Multi-objective** | Separate objectives |

Components:
- Tardiness penalty: -1.0 per minute
- Late job penalty: -10.0 per job
- Completion reward: +5.0 per job
- On-time bonus: +10.0 per on-time job
- Utilization reward: +1.0 × utilization

## API Reference

### `get_realtime_adjustment()`

Get RL-based adjustment recommendation.

```python
frappe.call({
    method: "uit_aps.scheduling.rl.realtime_api.get_realtime_adjustment",
    args: {
        scheduling_run: "SCH-RUN-00001",
        agent_type: "ppo"
    }
})
```

**Response:**
```json
{
    "success": true,
    "recommendation": {
        "action_type": "REASSIGN_MACHINE",
        "target_operation": "JC-00001",
        "target_machine": "WS-CUT-02",
        "confidence": 0.85,
        "reason": "Reassign for better load balancing"
    },
    "alternatives": [...]
}
```

### `apply_rl_adjustment()`

Apply the recommended adjustment.

```python
frappe.call({
    method: "uit_aps.scheduling.rl.realtime_api.apply_rl_adjustment",
    args: {
        scheduling_run: "SCH-RUN-00001",
        action_type: 1,
        target_operation: "JC-00001",
        target_machine: "WS-CUT-02"
    }
})
```

### `handle_disruption()`

Handle a disruption event.

```python
frappe.call({
    method: "uit_aps.scheduling.rl.realtime_api.handle_disruption",
    args: {
        disruption_type: "machine_breakdown",
        affected_resource: "WS-CUT-01",
        scheduling_run: "SCH-RUN-00001",
        duration_minutes: 60
    }
})
```

### `train_rl_agent()`

Train RL agent on historical data.

```python
frappe.call({
    method: "uit_aps.scheduling.rl.realtime_api.train_rl_agent",
    args: {
        scheduling_run: "SCH-RUN-00001",
        agent_type: "ppo",
        max_episodes: 100
    }
})
```

---

# Tier 3: GNN Encoder

## Overview

Tier 3 uses **Graph Neural Networks (GNN)** to learn structural patterns in scheduling problems. It provides:

- **Bottleneck Prediction**: Predict which machines will become bottlenecks
- **Duration Prediction**: Predict actual vs expected processing times
- **Delay Prediction**: Predict potential delays and cascade effects
- **Strategic Recommendations**: Long-term capacity and workflow suggestions
- **Enhanced RL State**: Provide richer state representations for Tier 2

## Graph Representation

The scheduling problem is represented as a heterogeneous graph:

| Node Type | Features |
|-----------|----------|
| **Job** | Due date, priority, num_ops, status |
| **Operation** | Start, end, duration, machine, sequence |
| **Machine** | Type, capacity, utilization, status |

| Edge Type | Description |
|-----------|-------------|
| **Precedence** | Operation sequence constraints |
| **Assignment** | Operation-to-machine assignment |
| **Capability** | Machine can process operation |
| **Temporal** | Operations close in time |

## Prediction Models

### Bottleneck Predictor

```python
frappe.call({
    method: "uit_aps.scheduling.gnn.gnn_api.predict_bottlenecks",
    args: {
        scheduling_run: "SCH-RUN-00001",
        threshold: 0.7
    }
})
```

**Response:**
```json
{
    "bottlenecks": [
        {"machine_id": "WS-001", "bottleneck_probability": 0.85}
    ],
    "summary": {"num_bottlenecks": 1, "avg_probability": 0.65}
}
```

### Duration Predictor

```python
frappe.call({
    method: "uit_aps.scheduling.gnn.gnn_api.predict_durations",
    args: {
        scheduling_run: "SCH-RUN-00001",
        confidence_level: 0.95
    }
})
```

### Delay Predictor

```python
frappe.call({
    method: "uit_aps.scheduling.gnn.gnn_api.predict_delays",
    args: {
        scheduling_run: "SCH-RUN-00001",
        delay_threshold: 0.5
    }
})
```

## Recommendation Engine

```python
frappe.call({
    method: "uit_aps.scheduling.gnn.gnn_api.get_recommendations",
    args: {
        scheduling_run: "SCH-RUN-00001",
        max_recommendations: 5
    }
})
```

**Response:**
```json
{
    "recommendations": [
        {
            "priority": "HIGH",
            "type": "capacity_increase",
            "title": "Add capacity to high-utilization machines",
            "impact": "Reduce bottleneck risk by 15%",
            "confidence": 0.85
        }
    ]
}
```

## GNN-RL Integration

Tier 3 enhances Tier 2 with richer state representations:

```python
from uit_aps.scheduling.gnn.rl_integration import GNNEnhancedPolicy, GNNRLConfig

policy = GNNEnhancedPolicy(
    flat_state_dim=3216,
    action_dim=7,
    config=GNNRLConfig(use_gnn_state=True)
)

action, log_prob = policy.get_action(flat_state, schedule, machines)
```

For detailed documentation, see [gnn/README.md](gnn/README.md).

---

# Hybrid Scheduling

## Overview

The `HybridScheduler` combines all three tiers for optimal results:

1. **Tier 3 Analysis** (optional): Get predictions and recommendations
2. **Run Tier 1** for initial optimal schedule
3. **Monitor** for disruptions
4. **Use Tier 2** (with GNN-enhanced state) for real-time adjustments

## API Reference

### `run_hybrid_scheduling()`

```python
frappe.call({
    method: "uit_aps.scheduling.hybrid_scheduler.run_hybrid_scheduling",
    args: {
        production_plan: "PP-2025-001",
        enable_rl: true,
        rl_agent_type: "ppo",
        time_limit_seconds: 300
    }
})
```

### `get_tier_status()`

Check availability of all tiers.

```python
frappe.call({
    method: "uit_aps.scheduling.hybrid_scheduler.get_tier_status"
})
```

**Response:**
```json
{
    "tier1_ortools": {
        "available": true,
        "status": "Ready"
    },
    "tier2_rl": {
        "available": true,
        "status": "Ready (PyTorch 2.0)",
        "agents": ["PPO", "SAC"]
    },
    "tier3_gnn": {
        "available": true,
        "status": "Ready",
        "capabilities": ["bottleneck_prediction", "duration_prediction", "recommendations"]
    }
}
```

---

## Usage Examples

### Python Backend

```python
from uit_aps.scheduling.hybrid_scheduler import HybridScheduler, HybridSchedulerConfig

# Configure
config = HybridSchedulerConfig(
    ortools_time_limit=300,
    enable_rl_adjustments=True,
    rl_agent_type="ppo"
)

# Create scheduler
scheduler = HybridScheduler(config)

# Run hybrid scheduling
result = scheduler.schedule(production_plan="PP-2025-001")

if result["success"]:
    print(f"Makespan: {result['metrics']['makespan_mins']} min")
    print(f"Tier 2 status: {result.get('tier2_status')}")
```

### Training RL Agent

```python
from uit_aps.scheduling.rl.trainer import create_trainer, TrainerConfig
from uit_aps.scheduling.rl.environment import SchedulingEnv, EnvironmentConfig

# Create environment
env = SchedulingEnv(EnvironmentConfig())

# Create trainer with PPO agent
trainer_config = TrainerConfig(
    max_episodes=500,
    agent_type="ppo",
    save_dir="models/scheduling_ppo"
)
trainer, agent = create_trainer(env, "ppo", trainer_config)

# Train
summary = trainer.train(initial_schedule=schedule, machines=machines)
print(f"Best reward: {summary['best_reward']}")
```

### JavaScript Frontend

```javascript
// Run hybrid scheduling
frappe.call({
    method: "uit_aps.scheduling.hybrid_scheduler.run_hybrid_scheduling",
    args: {
        production_plan: cur_frm.doc.name,
        enable_rl: true
    },
    freeze: true,
    freeze_message: __("Running hybrid scheduling..."),
    callback: function(r) {
        if (r.message.success) {
            frappe.show_alert({
                message: __("Scheduling completed!"),
                indicator: "green"
            });
        }
    }
});

// Handle disruption
frappe.call({
    method: "uit_aps.scheduling.rl.realtime_api.handle_disruption",
    args: {
        disruption_type: "machine_breakdown",
        affected_resource: "WS-001",
        scheduling_run: cur_frm.doc.name
    },
    callback: function(r) {
        if (r.message.recommendations) {
            // Show recommendations dialog
            show_recommendations(r.message.recommendations);
        }
    }
});
```

---

## Configuration

### Tier 1 Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `time_limit_seconds` | 300 | Max solver time |
| `makespan_weight` | 1.0 | Makespan objective weight |
| `tardiness_weight` | 10.0 | Tardiness penalty weight |
| `min_gap_between_ops_mins` | 10 | Gap between operations |

### Tier 2 Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `agent_type` | "ppo" | Agent type ("ppo" or "sac") |
| `hidden_sizes` | [256, 256] | Neural network architecture |
| `learning_rate` | 3e-4 | Learning rate |
| `gamma` | 0.99 | Discount factor |
| `batch_size` | 64 | Training batch size |

### PPO-Specific

| Parameter | Default | Description |
|-----------|---------|-------------|
| `clip_epsilon` | 0.2 | PPO clipping range |
| `n_epochs` | 10 | Update epochs |
| `gae_lambda` | 0.95 | GAE lambda |

### SAC-Specific

| Parameter | Default | Description |
|-----------|---------|-------------|
| `tau` | 0.005 | Soft update coefficient |
| `alpha` | 0.2 | Entropy coefficient |
| `auto_entropy_tuning` | True | Auto-tune entropy |

---

## Performance Tips

### Tier 1 (OR-Tools)
1. Start with 60-120 seconds for small problems
2. Increase time limit for larger problem sizes
3. Adjust weights based on business priorities

### Tier 2 (RL)
1. Train on diverse historical data
2. Use PPO for stability, SAC for sample efficiency
3. Retrain periodically as patterns change
4. Set appropriate confidence threshold for adjustments

### General
1. Use Tier 1 for initial scheduling
2. Enable Tier 2 for dynamic environments
3. Monitor and log all adjustments
4. Validate RL recommendations before applying

---

## Troubleshooting

### OR-Tools Not Found
```
Error: OR-Tools not installed
Solution: pip install ortools
```

### PyTorch Not Found
```
Error: PyTorch not installed
Solution: pip install torch
Note: Tier 2 features will be disabled
```

### No Jobs Found
```
Error: No jobs found to schedule
Solution: Ensure Work Orders exist with Job Cards
```

### RL Model Not Found
```
Warning: No trained model found
Solution: Train model with train_rl_agent()
```

---

## References

### Tier 1 (OR-Tools)
- [Google OR-Tools](https://developers.google.com/optimization)
- [CP-SAT Solver](https://developers.google.com/optimization/cp/cp_solver)

### Tier 2 (RL)
- [PPO Algorithm](https://arxiv.org/abs/1707.06347) - Schulman et al., 2017
- [SAC Algorithm](https://arxiv.org/abs/1801.01290) - Haarnoja et al., 2018
- [Gymnasium Documentation](https://gymnasium.farama.org/)

### Tier 3 (GNN)
- [Graph Attention Networks](https://arxiv.org/abs/1710.10903) - Velickovic et al., 2018
- [Graph Convolutional Networks](https://arxiv.org/abs/1609.02907) - Kipf & Welling, 2017
- [GNN for Scheduling](https://arxiv.org/abs/2003.01604)

### General
- [Job Shop Scheduling](https://en.wikipedia.org/wiki/Job-shop_scheduling)
- [PyTorch Documentation](https://pytorch.org/docs/)

---

## License

MIT License - See project root for details.

## Author

thanhnc - UIT APS Project
