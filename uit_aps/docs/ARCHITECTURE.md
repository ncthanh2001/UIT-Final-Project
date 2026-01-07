# Hybrid APS System - Kiến Trúc Tổng Quan

## 1. Giới Thiệu

**Hybrid APS (Advanced Planning and Scheduling)** là hệ thống lập lịch sản xuất thông minh, kết hợp 3 tầng công nghệ:

1. **Tier 1: OR-Tools** - Tối ưu hóa toán học (Constraint Programming)
2. **Tier 2: Reinforcement Learning** - Học tăng cường (PPO/SAC Agents)
3. **Tier 3: Graph Neural Network** - Mạng nơ-ron đồ thị (Dự đoán & Phân tích)

Hệ thống được tích hợp với **ERPNext/Frappe Framework** để quản lý dữ liệu sản xuất.

---

## 2. Kiến Trúc Tổng Quan

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ERPNext / Frappe                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Production  │  │ Work Order  │  │  Job Card   │  │    Workstation      │ │
│  │    Plan     │  │             │  │             │  │  (Working Hours)    │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────┼────────────────────┼────────────┘
          │                │                │                    │
          ▼                ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           UIT APS Module                                     │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      Data Layer (erpnext_loader.py)                    │ │
│  │  • Load Production Plans, Work Orders, Job Cards                       │ │
│  │  • Load Workstations với Working Hours                                 │ │
│  │  • Convert to Scheduling Data Format                                   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    TIER 1: OR-Tools Scheduling                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐  │ │
│  │  │   Scheduler  │  │  CP-SAT      │  │     Constraints              │  │ │
│  │  │   (models)   │──│  Solver      │──│  • Machine capacity          │  │ │
│  │  │              │  │              │  │  • Working hours             │  │ │
│  │  └──────────────┘  └──────────────┘  │  • Job precedence            │  │ │
│  │                                       │  • Due dates                 │  │ │
│  │  Objective: Minimize(makespan × w1 + tardiness × w2)                  │  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    TIER 2: RL Agent (Real-time)                        │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐  │ │
│  │  │    State     │  │   PPO/SAC    │  │     Actions                  │  │ │
│  │  │   Encoder    │──│   Agent      │──│  • REASSIGN_MACHINE          │  │ │
│  │  │              │  │              │  │  • RESCHEDULE_EARLIER/LATER  │  │ │
│  │  └──────────────┘  └──────────────┘  │  • PRIORITIZE_JOB            │  │ │
│  │                                       │  • SPLIT_BATCH               │  │ │
│  │  Features: Disruption handling, Real-time adjustment                  │  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    TIER 3: GNN Analysis                                │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐  │ │
│  │  │    Graph     │  │     GNN      │  │     Predictions              │  │ │
│  │  │   Builder    │──│   Model      │──│  • Bottleneck detection      │  │ │
│  │  │              │  │              │  │  • Delay prediction          │  │ │
│  │  └──────────────┘  └──────────────┘  │  • Resource optimization     │  │ │
│  │                                       │  • Critical path analysis    │  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    Output: APS Scheduling Result                       │ │
│  │  • Job Card assignments                                                │ │
│  │  • Planned Start/End Times                                             │ │
│  │  • Workstation allocations                                             │ │
│  │  • Late job warnings                                                   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    LLM Advisor (OpenAI Integration)                    │ │
│  │  • Phân tích lịch trình bằng AI                                        │ │
│  │  • Đưa ra khuyến nghị tối ưu                                           │ │
│  │  • Hỗ trợ tiếng Việt/Anh                                               │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Chi Tiết Các Tầng

### 3.1 Tier 1: OR-Tools Scheduling

**Mục đích:** Tạo lịch trình tối ưu ban đầu sử dụng Constraint Programming.

**Thành phần chính:**

```
uit_aps/scheduling/ortools/
├── scheduler.py          # Main scheduler class
├── models.py             # Data models (ScheduledOperation, SchedulingSolution)
├── constraints.py        # Constraint builders
└── objectives.py         # Objective functions
```

**Luồng xử lý:**

```
Input:                              Processing:                    Output:
┌─────────────┐                    ┌─────────────┐                ┌─────────────┐
│ Jobs        │                    │ CP-SAT      │                │ Scheduled   │
│ Machines    │───────────────────▶│ Solver      │───────────────▶│ Operations  │
│ Constraints │                    │             │                │             │
│ Objectives  │                    └─────────────┘                └─────────────┘
└─────────────┘
```

**Constraints được hỗ trợ:**
- **Machine Capacity:** Mỗi máy chỉ xử lý 1 job tại 1 thời điểm
- **Working Hours:** Chỉ schedule trong giờ làm việc của máy
- **Job Precedence:** Thứ tự operations trong cùng Work Order
- **Due Date:** Deadline của từng job

**Objective Function:**
```python
Minimize: makespan_weight × max(end_times) + tardiness_weight × sum(tardiness)
```

**Configuration:**
```python
@dataclass
class SchedulingConfig:
    time_limit_seconds: int = 300      # Giới hạn thời gian solver
    allow_overtime: bool = False        # Cho phép làm ngoài giờ
    objective_weights: ObjectiveWeights # Trọng số objective
```

---

### 3.2 Tier 2: Reinforcement Learning Agent

**Mục đích:** Điều chỉnh lịch trình real-time và xử lý disruptions.

**Thành phần chính:**

```
uit_aps/scheduling/rl/
├── environment.py        # Gym-compatible scheduling environment
├── state_encoder.py      # Encode state to vector
├── agents/
│   ├── ppo.py           # Proximal Policy Optimization agent
│   └── sac.py           # Soft Actor-Critic agent
├── trainer.py           # Training utilities
├── realtime_api.py      # Frappe API endpoints
└── evaluation.py        # Agent evaluation & heuristics comparison
```

**State Space:**
```python
State Vector = [
    Operation Features (max_ops × 32),   # time, machine, priority, status...
    Machine Features (max_machines × 16), # utilization, status, capacity...
    Global Features (16)                  # current_time, total_ops, disruptions...
]
```

**Action Space:**
| ID | Action | Mô tả |
|----|--------|-------|
| 0 | NO_OP | Không làm gì |
| 1 | REASSIGN_MACHINE | Chuyển operation sang máy khác |
| 2 | RESCHEDULE_EARLIER | Dời sớm hơn 30 phút |
| 3 | RESCHEDULE_LATER | Dời trễ hơn 30 phút |
| 4 | PRIORITIZE_JOB | Ưu tiên job (dời sớm 60 phút) |
| 5 | SPLIT_BATCH | Chia nhỏ lô hàng |
| 6 | MERGE_OPERATIONS | Gộp operations liên tiếp |

**Reward Function:**
```python
reward = (
    - tardiness_penalty × total_tardiness
    - makespan_penalty × makespan_increase
    + on_time_bonus × jobs_completed_on_time
    + utilization_bonus × machine_utilization_balance
)
```

**Disruption Types:**
- `MACHINE_BREAKDOWN` - Máy hỏng
- `RUSH_ORDER` - Đơn hàng gấp
- `PROCESSING_DELAY` - Chậm trễ xử lý
- `MATERIAL_SHORTAGE` - Thiếu nguyên vật liệu

---

### 3.3 Tier 3: Graph Neural Network

**Mục đích:** Phân tích và dự đoán bottlenecks, delays sử dụng cấu trúc đồ thị.

**Thành phần chính:**

```
uit_aps/scheduling/gnn/
├── graph_builder.py      # Build scheduling graph
├── models.py             # GNN architectures (GCN, GAT, GraphSAGE)
├── predictor.py          # Prediction utilities
└── gnn_api.py            # Frappe API endpoints
```

**Graph Structure:**
```
Nodes:                          Edges:
┌─────────────┐                 ┌─────────────────────────┐
│ Operations  │                 │ Precedence (job order)  │
│ Machines    │                 │ Assignment (op→machine) │
│ Jobs        │                 │ Resource sharing        │
└─────────────┘                 └─────────────────────────┘
```

**Predictions:**
- **Bottleneck Detection:** Xác định máy nào đang là bottleneck
- **Delay Prediction:** Dự đoán operations có nguy cơ trễ
- **Critical Path:** Xác định đường găng của schedule
- **Resource Optimization:** Đề xuất tối ưu tài nguyên

---

## 4. Data Flow

### 4.1 Scheduling Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCHEDULING WORKFLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

    User creates                Load data from              Build optimization
    Production Plan             ERPNext                     model
         │                           │                           │
         ▼                           ▼                           ▼
    ┌─────────┐              ┌─────────────┐              ┌─────────────┐
    │ Create  │              │   Load      │              │   Build     │
    │ APS     │─────────────▶│   Jobs,     │─────────────▶│   CP-SAT    │
    │ Sched   │              │   Machines  │              │   Model     │
    │ Run     │              │             │              │             │
    └─────────┘              └─────────────┘              └─────────────┘
                                                                │
    ┌─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────┐              ┌─────────────┐              ┌─────────────┐
│   Solve     │              │   Apply     │              │   Save      │
│   with      │─────────────▶│   RL        │─────────────▶│   Results   │
│   OR-Tools  │              │   Adjust    │              │   to DB     │
│             │              │   (optional)│              │             │
└─────────────┘              └─────────────┘              └─────────────┘
                                                                │
                                                                ▼
                                                         ┌─────────────┐
                                                         │ Update Job  │
                                                         │ Cards in    │
                                                         │ ERPNext     │
                                                         └─────────────┘
```

### 4.2 Real-time Adjustment Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        REAL-TIME ADJUSTMENT WORKFLOW                         │
└─────────────────────────────────────────────────────────────────────────────┘

    Disruption occurs           Encode current              Get RL
    (machine breakdown,         state                       recommendation
    rush order, etc.)
         │                           │                           │
         ▼                           ▼                           ▼
    ┌─────────┐              ┌─────────────┐              ┌─────────────┐
    │ Report  │              │   State     │              │   RL Agent  │
    │ Disrup  │─────────────▶│   Encoder   │─────────────▶│   Select    │
    │ tion    │              │             │              │   Action    │
    └─────────┘              └─────────────┘              └─────────────┘
                                                                │
    ┌─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────┐              ┌─────────────┐              ┌─────────────┐
│   Show      │              │   User      │              │   Apply     │
│   Recommend │─────────────▶│   Approves  │─────────────▶│   Changes   │
│   ation     │              │             │              │   to DB     │
└─────────────┘              └─────────────┘              └─────────────┘
```

---

## 5. API Endpoints

### 5.1 Tier 1 APIs (OR-Tools)

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `scheduling_api.run_ortools_scheduling` | POST | Chạy OR-Tools scheduling |
| `scheduling_api.get_gantt_data` | GET | Lấy dữ liệu Gantt chart |

### 5.2 Tier 2 APIs (RL Agent)

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `realtime_api.get_realtime_adjustment` | POST | Lấy RL recommendation |
| `realtime_api.apply_rl_adjustment` | POST | Áp dụng adjustment |
| `realtime_api.handle_disruption` | POST | Xử lý disruption |
| `realtime_api.train_rl_agent` | POST | Train RL agent |

### 5.3 Tier 3 APIs (GNN)

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `gnn_api.predict_bottlenecks` | POST | Dự đoán bottlenecks |
| `gnn_api.predict_delays` | POST | Dự đoán delays |
| `gnn_api.get_recommendations` | POST | Lấy strategic recommendations |
| `gnn_api.get_critical_insights` | POST | Phân tích critical insights |

### 5.4 Evaluation APIs (Phase 4)

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `evaluation_api.evaluate_agent` | POST | So sánh RL với heuristics |
| `evaluation_api.get_heuristic_schedule` | POST | Tạo schedule bằng heuristic |
| `evaluation_api.compare_with_ortools` | POST | So sánh RL với OR-Tools |
| `evaluation_api.get_deployment_status` | GET | Trạng thái deployment |

### 5.5 LLM APIs

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `llm_api.get_scheduling_advice` | POST | Phân tích schedule bằng AI |
| `llm_api.get_quick_summary` | POST | Tóm tắt nhanh |
| `llm_api.analyze_bottlenecks` | POST | Phân tích bottlenecks |

---

## 6. Database Schema

### 6.1 Custom DocTypes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APS Scheduling Run                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ • production_plan (Link → Production Plan)                                  │
│ • scheduling_strategy (Select: Forward/Backward/Priority/EDD)               │
│ • scheduling_tier (Select: Tier 1/2/3)                                      │
│ • run_status (Select: Pending/Running/Completed/Failed)                     │
│ • Solver Config: time_limit, makespan_weight, tardiness_weight              │
│ • Results: total_job_cards, late_jobs, makespan, utilization                │
│ • LLM Analysis: llm_analysis_content, llm_analysis_date                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ 1:N
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          APS Scheduling Result                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ • scheduling_run (Link → APS Scheduling Run)                                │
│ • job_card (Link → Job Card)                                                │
│ • work_order (Link → Work Order)                                            │
│ • workstation (Link → Workstation)                                          │
│ • planned_start_time (Datetime)                                             │
│ • planned_end_time (Datetime)                                               │
│ • is_late (Check)                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         APS Chatgpt Settings                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ • api_key (Code) - OpenAI API Key                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 ERPNext Integration

```
Sử dụng các DocTypes có sẵn của ERPNext:

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Production Plan │────▶│   Work Order    │────▶│    Job Card     │
│                 │     │                 │     │                 │
│ • items         │     │ • operations    │     │ • operation     │
│ • planned_qty   │     │ • required_qty  │     │ • workstation   │
│ • status        │     │ • planned_dates │     │ • for_quantity  │
└─────────────────┘     └─────────────────┘     │ • time_required │
                                                 └─────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │   Workstation   │
                                                 │                 │
                                                 │ • working_hours │
                                                 │ • holiday_list  │
                                                 │ • status        │
                                                 └─────────────────┘
```

---

## 7. Configuration

### 7.1 Module Configuration

```python
# hooks.py
app_name = "uit_aps"
app_title = "UIT APS"
app_publisher = "thanhnc"

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "uit_aps.tasks.cleanup_old_results"
    ]
}
```

### 7.2 Solver Configuration

```python
# Default solver configuration
DEFAULT_CONFIG = {
    "time_limit_seconds": 300,      # 5 minutes
    "makespan_weight": 1.0,
    "tardiness_weight": 10.0,       # Prioritize on-time delivery
    "allow_overtime": False,
    "min_gap_between_ops": 10       # minutes
}
```

### 7.3 RL Agent Configuration

```python
# PPO Configuration
PPOConfig = {
    "hidden_sizes": [256, 256],
    "learning_rate": 3e-4,
    "gamma": 0.99,
    "clip_epsilon": 0.2,
    "max_operations": 100,
    "max_machines": 20
}

# SAC Configuration
SACConfig = {
    "hidden_sizes": [256, 256],
    "learning_rate": 3e-4,
    "gamma": 0.99,
    "tau": 0.005,
    "alpha": 0.2
}
```

---

## 8. Deployment

### 8.1 Requirements

```
# Python packages
frappe>=14.0.0
ortools>=9.0.0
torch>=1.9.0
numpy>=1.20.0
openai>=1.0.0

# Optional for GNN
torch-geometric>=2.0.0
```

### 8.2 Installation

```bash
# Clone repository
cd frappe-bench/apps
git clone <repo-url> uit_aps

# Install app
cd ..
bench get-app uit_aps
bench --site <site-name> install-app uit_aps

# Run migrations
bench --site <site-name> migrate
```

### 8.3 Model Storage

```
<site>/private/files/rl_models/
├── ppo/
│   └── best/
│       ├── actor.pth
│       ├── critic.pth
│       └── ppo_config.json
└── sac/
    └── best/
        ├── actor.pth
        ├── critic1.pth
        ├── critic2.pth
        └── sac_config.json
```

---

## 9. Performance Considerations

### 9.1 Scalability

| Metric | Small | Medium | Large |
|--------|-------|--------|-------|
| Operations | < 100 | 100-500 | 500+ |
| Machines | < 10 | 10-50 | 50+ |
| Solver Time | < 30s | 30s-5min | 5min+ |

### 9.2 Optimization Tips

1. **OR-Tools:**
   - Tăng `time_limit_seconds` cho problems lớn
   - Sử dụng `hint` từ previous solutions

2. **RL Agent:**
   - Train với đủ dữ liệu (>1000 episodes)
   - Sử dụng model caching

3. **Database:**
   - Index các trường thường query
   - Cleanup old scheduling results định kỳ

---

## 10. Future Enhancements

- [ ] Multi-objective optimization với Pareto front
- [ ] Integration với IoT sensors để real-time machine status
- [ ] Predictive maintenance integration
- [ ] Mobile app cho shop floor
- [ ] Advanced visualization (3D Gantt, Heatmaps)
- [ ] Multi-site/Multi-factory support

---

## 11. References

- [OR-Tools Documentation](https://developers.google.com/optimization)
- [Stable Baselines3](https://stable-baselines3.readthedocs.io/)
- [PyTorch Geometric](https://pytorch-geometric.readthedocs.io/)
- [Frappe Framework](https://frappeframework.com/)
- [ERPNext Documentation](https://docs.erpnext.com/)
