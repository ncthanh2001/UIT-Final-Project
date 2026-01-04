# Tier 2: Reinforcement Learning for Real-Time Scheduling

## Overview

Tier 2 of the Hybrid APS system uses **Reinforcement Learning (RL)** agents to handle real-time scheduling adjustments. While Tier 1 (OR-Tools) provides optimal offline schedules, Tier 2 learns to adapt schedules when disruptions occur.

### When to Use Tier 2

| Scenario | Use Tier 2? |
|----------|-------------|
| Initial schedule creation | ❌ Use Tier 1 |
| Machine breakdown | ✅ Yes |
| Rush order arrives | ✅ Yes |
| Processing delay detected | ✅ Yes |
| Material shortage | ✅ Yes |
| Worker absence | ✅ Yes |
| Quality issue requiring rework | ✅ Yes |

## Architecture

```
rl/
├── __init__.py           # Module initialization
├── README.md             # This file
├── environment.py        # SchedulingEnv - Gymnasium environment
├── state_encoder.py      # Feature encoding for neural networks
├── reward.py             # Reward calculation strategies
├── trainer.py            # Training pipeline
├── realtime_api.py       # Frappe API endpoints
└── agents/
    ├── __init__.py
    ├── base.py           # Base agent class
    ├── ppo.py            # PPO agent
    └── sac.py            # SAC agent
```

## Installation

```bash
# Install PyTorch (required for Tier 2)
pip install torch

# Verify installation
python -c "import torch; print(f'PyTorch {torch.__version__} installed')"
```

**Note:** Tier 2 is optional. If PyTorch is not installed, Tier 1 (OR-Tools) will still work.

---

## Quick Start

### 1. Get Adjustment Recommendation

```python
import frappe

# When a disruption occurs, get RL recommendation
result = frappe.call(
    "uit_aps.scheduling.rl.realtime_api.get_realtime_adjustment",
    scheduling_run="SCH-RUN-00001",
    agent_type="ppo"
)

if result["success"]:
    rec = result["recommendation"]
    print(f"Action: {rec['action_type']}")
    print(f"Target: {rec['target_operation']}")
    print(f"Confidence: {rec['confidence']:.0%}")
    print(f"Reason: {rec['reason']}")
```

### 2. Apply the Adjustment

```python
# Apply the recommended adjustment
result = frappe.call(
    "uit_aps.scheduling.rl.realtime_api.apply_rl_adjustment",
    scheduling_run="SCH-RUN-00001",
    action_type=1,  # REASSIGN_MACHINE
    target_operation="JC-00001",
    target_machine="WS-CUT-02"
)

if result["success"]:
    print(f"Adjustment applied: {result['message']}")
```

### 3. Handle Disruption Event

```python
# Report a machine breakdown
result = frappe.call(
    "uit_aps.scheduling.rl.realtime_api.handle_disruption",
    disruption_type="machine_breakdown",
    affected_resource="WS-CUT-01",
    scheduling_run="SCH-RUN-00001",
    duration_minutes=60
)

print(f"Affected operations: {len(result['affected_operations'])}")
for rec in result["recommendations"]:
    print(f"  - {rec['action_type']}: {rec['target_operation']}")
```

---

## Available Agents

### PPO (Proximal Policy Optimization)

**Best for:** Stable learning, production environments

```python
from uit_aps.scheduling.rl.agents.ppo import PPOAgent, PPOConfig

config = PPOConfig(
    hidden_sizes=[256, 256],
    learning_rate=3e-4,
    clip_epsilon=0.2,
    n_epochs=10,
    gae_lambda=0.95
)

agent = PPOAgent(obs_dim=3216, action_dim=7, config=config)
```

**Key Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `clip_epsilon` | 0.2 | Clipping range for policy updates |
| `n_epochs` | 10 | Update epochs per batch |
| `gae_lambda` | 0.95 | GAE lambda for advantage estimation |
| `value_loss_coef` | 0.5 | Value function loss weight |
| `entropy_coef` | 0.01 | Entropy bonus for exploration |

### SAC (Soft Actor-Critic)

**Best for:** Sample efficiency, continuous exploration

```python
from uit_aps.scheduling.rl.agents.sac import SACAgent, SACConfig

config = SACConfig(
    hidden_sizes=[256, 256],
    learning_rate=3e-4,
    tau=0.005,
    alpha=0.2,
    auto_entropy_tuning=True
)

agent = SACAgent(obs_dim=3216, action_dim=7, config=config)
```

**Key Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `tau` | 0.005 | Soft update coefficient |
| `alpha` | 0.2 | Entropy coefficient |
| `auto_entropy_tuning` | True | Automatically tune entropy |
| `buffer_size` | 100000 | Replay buffer size |

### Choosing Between PPO and SAC

| Criteria | PPO | SAC |
|----------|-----|-----|
| Stability | ⭐⭐⭐ | ⭐⭐ |
| Sample Efficiency | ⭐⭐ | ⭐⭐⭐ |
| Exploration | ⭐⭐ | ⭐⭐⭐ |
| Training Speed | ⭐⭐⭐ | ⭐⭐ |
| Production Use | ⭐⭐⭐ | ⭐⭐ |

**Recommendation:** Start with PPO for production. Use SAC if you have limited training data.

---

## Action Space

The RL agent can take these actions:

| ID | Action | Description | When to Use |
|----|--------|-------------|-------------|
| 0 | `NO_OP` | No action needed | Schedule is optimal |
| 1 | `REASSIGN_MACHINE` | Move to different machine | Machine overloaded/broken |
| 2 | `RESCHEDULE_EARLIER` | Move 30 min earlier | Risk of delay |
| 3 | `RESCHEDULE_LATER` | Move 30 min later | Predecessor delayed |
| 4 | `PRIORITIZE_JOB` | Increase job priority | Critical order |
| 5 | `SPLIT_BATCH` | Split into smaller batches | Large batch blocking |
| 6 | `MERGE_OPERATIONS` | Combine operations | Efficiency gain |

---

## Observation Space

The agent observes:

### Operation Features (8 per operation)

| Feature | Range | Description |
|---------|-------|-------------|
| start_offset | [-1, 1] | Time until start (normalized) |
| end_offset | [-1, 1] | Time until end (normalized) |
| duration | [0, 1] | Duration (normalized) |
| due_offset | [-1, 1] | Time until due (normalized) |
| priority | [0, 1] | Job priority (normalized) |
| status | [-0.5, 1] | Operation status encoding |
| machine_idx | [0, 1] | Assigned machine index |
| is_late | {0, 1} | Whether operation is late |

### Machine Features (6 per machine)

| Feature | Range | Description |
|---------|-------|-------------|
| status | [0, 1] | Machine status encoding |
| utilization | [0, 1] | Current utilization |
| current_op | [0, 1] | Current operation index |
| remaining_time | [0, 1] | Time until available |
| capacity | [0, 1] | Machine capacity |
| type_hash | [0, 1] | Machine type encoding |

### Global Features (5 total)

| Feature | Range | Description |
|---------|-------|-------------|
| time_progress | [0, 1] | Simulation progress |
| pending_ratio | [0, 1] | Pending operations ratio |
| disruption_ratio | [0, 1] | Active disruptions ratio |
| tardiness_ratio | [0, 1] | Total tardiness ratio |
| completion_ratio | [0, 1] | Completed operations ratio |

---

## Reward Function

### Reward Components

| Component | Weight | Description |
|-----------|--------|-------------|
| Tardiness penalty | -1.0 | Per minute of tardiness |
| Late job penalty | -10.0 | Per late job |
| Completion reward | +5.0 | Per completed job |
| On-time bonus | +10.0 | Per on-time completion |
| Utilization reward | +1.0 | Per unit utilization |
| Action success | +0.5 | Successful action |
| Disruption handled | +2.0 | Per handled disruption |

### Reward Strategies

```python
from uit_aps.scheduling.rl.reward import RewardCalculator, RewardConfig, RewardType

# Sparse: Only reward at episode end
config = RewardConfig(reward_type=RewardType.SPARSE)

# Dense: Reward at each step
config = RewardConfig(reward_type=RewardType.DENSE)

# Shaped: Potential-based shaping (recommended)
config = RewardConfig(reward_type=RewardType.SHAPED)

# Multi-objective: Separate objectives
config = RewardConfig(reward_type=RewardType.MULTI_OBJECTIVE)

calculator = RewardCalculator(config)
```

---

## Training the Agent

### Using the Training Pipeline

```python
from uit_aps.scheduling.rl.environment import SchedulingEnv, EnvironmentConfig
from uit_aps.scheduling.rl.trainer import create_trainer, TrainerConfig

# 1. Create environment
env_config = EnvironmentConfig(
    time_step_minutes=15,
    horizon_hours=24,
    max_operations=100,
    max_machines=20,
    disruption_probability=0.05
)
env = SchedulingEnv(env_config)

# 2. Create trainer
trainer_config = TrainerConfig(
    max_episodes=500,
    max_steps_per_episode=200,
    eval_frequency=50,
    save_frequency=100,
    agent_type="ppo",
    save_dir="models/scheduling_ppo"
)

trainer, agent = create_trainer(env, "ppo", trainer_config)

# 3. Train with initial schedule from Tier 1
summary = trainer.train(
    initial_schedule=tier1_schedule,
    machines=machines
)

print(f"Training complete!")
print(f"Best reward: {summary['best_reward']:.2f}")
print(f"Total episodes: {summary['total_episodes']}")
```

### Training via API

```python
import frappe

result = frappe.call(
    "uit_aps.scheduling.rl.realtime_api.train_rl_agent",
    scheduling_run="SCH-RUN-00001",  # Use this run's data
    agent_type="ppo",
    max_episodes=100
)

if result["success"]:
    print(f"Model saved to: {result['model_path']}")
```

### Training Tips

1. **Start with historical data**: Use past scheduling runs for training
2. **Simulate disruptions**: Set `disruption_probability` to match reality
3. **Use shaped rewards**: Better learning than sparse rewards
4. **Train regularly**: Retrain as production patterns change
5. **Evaluate before deploying**: Always test on held-out data

---

## Integration with Tier 1

### Hybrid Workflow

```python
from uit_aps.scheduling.hybrid_scheduler import HybridScheduler, HybridSchedulerConfig

# Configure hybrid scheduler
config = HybridSchedulerConfig(
    # Tier 1 settings
    ortools_time_limit=300,
    makespan_weight=1.0,
    tardiness_weight=10.0,

    # Tier 2 settings
    enable_rl_adjustments=True,
    rl_agent_type="ppo",
    rl_adjustment_threshold=0.7,  # Confidence threshold
    auto_handle_disruptions=True
)

scheduler = HybridScheduler(config)

# Run hybrid scheduling
result = scheduler.schedule(production_plan="PP-2025-001")

# Handle disruptions with RL
if disruption_detected:
    adjustment = scheduler.handle_disruption(
        disruption_type="machine_breakdown",
        affected_resource="WS-001",
        scheduling_run=result["scheduling_run"]
    )
```

### Workflow Diagram

```
┌─────────────────┐
│  Production     │
│  Plan           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tier 1:        │
│  OR-Tools       │──────► Initial Optimal Schedule
│  (Offline)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Execute        │
│  Schedule       │
└────────┬────────┘
         │
    Disruption?
         │
    Yes  │  No
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌─────────┐
│ Tier 2: │ │Continue │
│ RL Agent│ │Execution│
│ (Online)│ └─────────┘
└────┬────┘
     │
     ▼
┌─────────────────┐
│  Adjust         │
│  Schedule       │
└─────────────────┘
```

---

## API Reference

### `get_realtime_adjustment()`

Get RL-based adjustment recommendation.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `scheduling_run` | str | Yes | APS Scheduling Run name |
| `current_state` | str | No | JSON state (auto-loaded if not provided) |
| `agent_type` | str | No | "ppo" or "sac" (default: "ppo") |

**Response:**

```json
{
    "success": true,
    "recommendation": {
        "action_type": "REASSIGN_MACHINE",
        "action_type_id": 1,
        "target_operation": "JC-00001",
        "target_operation_name": "Cutting",
        "target_machine": "WS-CUT-02",
        "target_machine_name": "Cutting Machine 2",
        "confidence": 0.85,
        "value_estimate": 12.5,
        "reason": "Reassign to WS-CUT-02 for better load balancing"
    },
    "alternatives": [
        {
            "action_type": "RESCHEDULE_EARLIER",
            "action_type_id": 2,
            "confidence": 0.65,
            "reason": "Move earlier to reduce risk of delay"
        }
    ],
    "state_info": {
        "num_operations": 45,
        "num_machines": 8,
        "current_time": "2025-01-15T10:30:00"
    }
}
```

### `apply_rl_adjustment()`

Apply the recommended adjustment.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `scheduling_run` | str | Yes | APS Scheduling Run name |
| `action_type` | int | Yes | Action type ID (0-6) |
| `target_operation` | str | Yes | Job Card name |
| `target_machine` | str | No | New workstation (for reassign) |
| `new_start_time` | str | No | New start time (for reschedule) |

**Response:**

```json
{
    "success": true,
    "message": "Machine reassigned successfully",
    "new_workstation": "WS-CUT-02"
}
```

### `handle_disruption()`

Handle a disruption event.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `disruption_type` | str | Yes | Type: machine_breakdown, rush_order, processing_delay, material_shortage |
| `affected_resource` | str | Yes | Machine or operation affected |
| `scheduling_run` | str | No | Current scheduling run |
| `duration_minutes` | int | No | Expected duration (default: 60) |

**Response:**

```json
{
    "success": true,
    "disruption": {
        "type": "machine_breakdown",
        "affected_resource": "WS-CUT-01",
        "duration_minutes": 60,
        "timestamp": "2025-01-15T10:30:00"
    },
    "affected_operations": ["JC-00001", "JC-00002", "JC-00003"],
    "recommendations": [
        {
            "action_type": "REASSIGN_MACHINE",
            "target_operation": "JC-00001",
            "confidence": 0.9
        }
    ],
    "message": "Disruption logged. 3 operations affected."
}
```

### `train_rl_agent()`

Train RL agent on historical data.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `scheduling_run` | str | Yes | Reference run for training data |
| `agent_type` | str | No | "ppo" or "sac" (default: "ppo") |
| `max_episodes` | int | No | Training episodes (default: 100) |

**Response:**

```json
{
    "success": true,
    "summary": {
        "total_episodes": 100,
        "best_reward": 45.6,
        "training_time_seconds": 3600
    },
    "model_path": "/private/files/rl_models/ppo/best",
    "message": "Training completed successfully"
}
```

---

## JavaScript Integration

### Get Recommendation on Disruption

```javascript
// When user reports a disruption
frappe.call({
    method: "uit_aps.scheduling.rl.realtime_api.handle_disruption",
    args: {
        disruption_type: "machine_breakdown",
        affected_resource: cur_frm.doc.workstation,
        scheduling_run: cur_frm.doc.scheduling_run,
        duration_minutes: 60
    },
    callback: function(r) {
        if (r.message.success) {
            show_recommendations_dialog(r.message.recommendations);
        }
    }
});

function show_recommendations_dialog(recommendations) {
    let html = '<table class="table">';
    html += '<tr><th>Action</th><th>Target</th><th>Confidence</th></tr>';

    recommendations.forEach(rec => {
        html += `<tr>
            <td>${rec.action_type}</td>
            <td>${rec.target_operation}</td>
            <td>${(rec.confidence * 100).toFixed(0)}%</td>
        </tr>`;
    });
    html += '</table>';

    frappe.msgprint({
        title: __('RL Recommendations'),
        message: html,
        indicator: 'blue'
    });
}
```

### Apply Adjustment

```javascript
frappe.call({
    method: "uit_aps.scheduling.rl.realtime_api.apply_rl_adjustment",
    args: {
        scheduling_run: cur_frm.doc.name,
        action_type: 1,  // REASSIGN_MACHINE
        target_operation: "JC-00001",
        target_machine: "WS-CUT-02"
    },
    callback: function(r) {
        if (r.message.success) {
            frappe.show_alert({
                message: r.message.message,
                indicator: 'green'
            });
            cur_frm.reload_doc();
        }
    }
});
```

---

## Troubleshooting

### PyTorch Not Installed

```
Error: PyTorch not installed
Solution: pip install torch
```

### No Trained Model

```
Warning: No trained model found, using random policy
Solution: Train with train_rl_agent() first
```

### Low Confidence Recommendations

```
Issue: All recommendations have low confidence (<50%)
Causes:
- Model not trained enough
- Current state very different from training data
- Multiple good options available

Solution:
1. Train with more episodes
2. Include similar scenarios in training
3. Consider using Tier 1 for re-optimization
```

### Out of Memory

```
Error: CUDA out of memory
Solutions:
1. Reduce batch_size in config
2. Use CPU: config.device = "cpu"
3. Reduce hidden_sizes
```

---

## Best Practices

### 1. Training

- Train on diverse disruption scenarios
- Use realistic disruption probabilities
- Validate on held-out scheduling runs
- Retrain monthly or when patterns change

### 2. Deployment

- Set confidence threshold (e.g., 70%)
- Log all recommendations and outcomes
- Allow human override
- Monitor model performance

### 3. Maintenance

- Track recommendation acceptance rate
- Monitor tardiness and utilization metrics
- Retrain if performance degrades
- Keep training history for analysis

---

## Phase 4: Evaluation & Deployment

Phase 4 provides comprehensive evaluation, deployment, and monitoring capabilities.

### Architecture

```
rl/
├── evaluation.py         # Evaluation framework
├── deployment.py         # Model deployment management
└── evaluation_api.py     # Frappe API endpoints
```

### Heuristic Comparison

Compare RL agent performance against classical scheduling heuristics:

| Heuristic | Description |
|-----------|-------------|
| **SPT** | Shortest Processing Time |
| **LPT** | Longest Processing Time |
| **EDD** | Earliest Due Date |
| **FCFS** | First Come First Served |
| **CR** | Critical Ratio |
| **SLACK** | Minimum Slack Time |

```python
from uit_aps.scheduling.rl.evaluation import run_full_evaluation, EvaluationConfig

config = EvaluationConfig(
    num_scenarios=50,
    compare_heuristics=["spt", "edd", "fcfs"]
)

analysis = run_full_evaluation(
    env=env,
    agent=trained_agent,
    config=config
)

print(f"RL beats {analysis['summary']['beats_heuristics']} heuristics")
print(f"Recommendation: {analysis['summary']['recommendation']}")
```

### Model Deployment

Manage model versions and deployments:

```python
from uit_aps.scheduling.rl.deployment import ModelRegistry, DeploymentConfig

# Register trained model
registry = ModelRegistry()
version_id = registry.register_model(
    agent_type="ppo",
    model_path="models/ppo/best",
    evaluation_metrics={"reward": 45.6, "on_time_rate": 0.95}
)

# Deploy in shadow mode
registry.deploy(version_id, shadow_mode=True)

# Promote to active after validation
registry.promote_to_active(version_id)

# Rollback if issues
registry.rollback()
```

### Production Monitoring

Track agent performance in production:

```python
from uit_aps.scheduling.rl.evaluation import ProductionMonitor

monitor = ProductionMonitor()

# Log decisions
monitor.log_decision(state, action, confidence=0.85)

# Log performance
monitor.log_performance({
    "total_tardiness_mins": 30,
    "late_rate": 0.05,
    "reward": 12.5
})

# Get summary
summary = monitor.get_summary(last_n=100)
print(f"Avg reward: {summary['total_reward']['mean']}")

# Export report
report_path = monitor.export_report()
```

### Phase 4 API Reference

#### `evaluate_agent()`

Evaluate RL agent against heuristics.

```python
frappe.call({
    method: "uit_aps.scheduling.rl.evaluation_api.evaluate_agent",
    args: {
        scheduling_run: "SCH-RUN-00001",
        agent_type: "ppo",
        num_scenarios: 20,
        compare_heuristics: "spt,edd,fcfs"
    }
})
```

#### `get_deployment_status()`

Get current deployment status.

```python
frappe.call({
    method: "uit_aps.scheduling.rl.evaluation_api.get_deployment_status"
})
```

#### `deploy_model()`

Deploy a model version.

```python
frappe.call({
    method: "uit_aps.scheduling.rl.evaluation_api.deploy_model",
    args: {
        version_id: "v_ppo_20250115_120000",
        shadow_mode: true
    }
})
```

#### `rollback_model()`

Rollback to previous version.

```python
frappe.call({
    method: "uit_aps.scheduling.rl.evaluation_api.rollback_model",
    args: {
        to_version: "v_ppo_20250114_100000"  # Optional
    }
})
```

#### `get_monitoring_summary()`

Get production monitoring summary.

```python
frappe.call({
    method: "uit_aps.scheduling.rl.evaluation_api.get_monitoring_summary",
    args: {
        last_n: 100
    }
})
```

---

## References

- [PPO Paper](https://arxiv.org/abs/1707.06347) - Schulman et al., 2017
- [SAC Paper](https://arxiv.org/abs/1801.01290) - Haarnoja et al., 2018
- [Gymnasium Documentation](https://gymnasium.farama.org/)
- [PyTorch Documentation](https://pytorch.org/docs/)

---

## License

MIT License - See project root for details.

## Author

thanhnc - UIT APS Project
