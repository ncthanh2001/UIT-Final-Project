# UIT APS - Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Project Structure](#project-structure)
4. [Core Components](#core-components)
5. [Technology Stack](#technology-stack)
6. [Data Models](#data-models)
7. [API Documentation](#api-documentation)
8. [Integration Points](#integration-points)
9. [Deployment Architecture](#deployment-architecture)

---

## Overview

UIT APS (Advanced Planning and Scheduling) is an intelligent production planning system built on top of ERPNext v15+. It combines traditional operations research methods with modern AI/ML techniques to provide:

- **Demand Forecasting**: Multi-model forecasting (ARIMA, Linear Regression, Prophet)
- **Production Planning**: AI-driven production plan generation
- **MRP Optimization**: Intelligent material requirements planning with supplier optimization
- **Hybrid Scheduling**: Three-tier scheduling system (OR-Tools + RL + GNN)

### Key Capabilities
- AI-powered forecast explanations using ChatGPT
- Real-time schedule adjustments using Reinforcement Learning
- Bottleneck prediction using Graph Neural Networks
- Automated purchase suggestions with multi-criteria supplier optimization
- Comprehensive analytics and tracking

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Vue.js 3   │  │  Frappe UI   │  │  Dashboard   │      │
│  │   Frontend   │  │  Components  │  │  Visualizer  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           ↓ REST APIs
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Forecasting │  │  Production  │  │  Scheduling  │      │
│  │    Engine    │  │   Planning   │  │    Engine    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  MRP Engine  │  │  AI Explainer│  │  Background  │      │
│  │              │  │   (ChatGPT)  │  │     Jobs     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                 Data Access Layer (Frappe ORM)               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer (MariaDB)                  │
└─────────────────────────────────────────────────────────────┘
```

### Three-Tier Hybrid Scheduling Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Tier 1: OR-Tools CP-SAT Solver (Offline Optimization)       │
│  ─────────────────────────────────────────────────────────   │
│  • Job Shop Scheduling Problem (JSSP) solver                 │
│  • Constraint programming with precedence, capacity limits   │
│  • Multi-objective: minimize makespan + tardiness            │
│  • Generates optimal baseline schedule                       │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  Tier 2: Reinforcement Learning (Real-Time Adjustments)      │
│  ─────────────────────────────────────────────────────────   │
│  • PPO (Proximal Policy Optimization) agent                  │
│  • SAC (Soft Actor-Critic) agent                             │
│  • Handles disruptions, breakdowns, rush orders              │
│  • Dynamic rescheduling based on shop floor conditions       │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  Tier 3: Graph Neural Networks (Strategic Insights)          │
│  ─────────────────────────────────────────────────────────   │
│  • Bottleneck prediction (future resource constraints)       │
│  • Duration prediction (improved time estimates)             │
│  • Strategic recommendations (capacity planning)             │
│  • GAT (Graph Attention Networks) for dependency modeling    │
└──────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
/home/thanhnc/frappe_uit/apps/uit_aps/
├── uit_aps/                          # Main application module
│   ├── uit_aps/                      # Core APS module
│   │   ├── doctype/                  # Database models (DocTypes)
│   │   │   ├── aps_forecast_history/
│   │   │   ├── aps_forecast_result/
│   │   │   ├── aps_production_plan/
│   │   │   ├── aps_production_plan_item/
│   │   │   ├── aps_mrp_run/
│   │   │   ├── aps_mrp_result/
│   │   │   ├── aps_purchase_suggestion/
│   │   │   ├── aps_scheduling_run/
│   │   │   ├── aps_scheduling_result/
│   │   │   └── aps_chatgpt_settings/
│   │   └── page/                     # UI pages
│   │
│   ├── scheduling/                   # Hybrid scheduling system
│   │   ├── ortools/                  # Tier 1: CP-SAT solver
│   │   │   ├── scheduler.py          # Main OR-Tools scheduler
│   │   │   └── jssp_solver.py        # JSSP constraint model
│   │   ├── rl/                       # Tier 2: RL agents
│   │   │   ├── agent.py              # PPO/SAC agents
│   │   │   ├── environment.py        # Gymnasium environment
│   │   │   └── trainer.py            # Agent training logic
│   │   ├── gnn/                      # Tier 3: GNN models
│   │   │   ├── model.py              # GAT architecture
│   │   │   ├── predictor.py          # Bottleneck/duration prediction
│   │   │   └── recommender.py        # Strategic recommendations
│   │   └── api/                      # Scheduling REST APIs
│   │       └── scheduling_api.py
│   │
│   ├── ml/                           # Machine learning forecasting
│   │   ├── arima_model.py            # ARIMA time series model
│   │   ├── linear_regression_model.py # Linear regression forecaster
│   │   ├── prophet.py                # Facebook Prophet model
│   │   ├── data_helper.py            # Data extraction & validation
│   │   ├── ai_explainer.py           # ChatGPT explanations
│   │   └── ai_background_jobs.py     # Async AI processing
│   │
│   ├── uit_api/                      # REST API endpoints
│   │   ├── run_model.py              # Forecasting APIs
│   │   ├── production_plan.py        # Production planning APIs
│   │   └── mrp_optimization.py       # MRP APIs
│   │
│   ├── utils/                        # Helper utilities
│   ├── aps_ai_inventory/             # AI inventory module
│   ├── uit_aps_manufacturing/        # Manufacturing integration
│   ├── public/                       # Frontend assets
│   │   ├── js/
│   │   ├── css/
│   │   └── images/
│   ├── templates/                    # Jinja2 web templates
│   ├── config/                       # Application configuration
│   │   └── desktop.py
│   └── www/                          # Web pages
│
├── frontend/                         # Vue.js 3 frontend
│   ├── src/
│   │   ├── components/               # Reusable Vue components
│   │   ├── views/                    # Page views
│   │   ├── router/                   # Vue Router
│   │   └── stores/                   # State management
│   ├── public/
│   └── package.json
│
├── vue-it-together/                  # Additional Vue components
│
├── Design Documents/                 # Architecture docs
│   ├── APS Architecture.md
│   ├── Hybrid Scheduling Design.md
│   └── MRP Optimization.md
│
├── hooks.py                          # Frappe app configuration
├── pyproject.toml                    # Python build config
├── requirements.txt                  # Python dependencies
└── README.md
```

---

## Core Components

### 1. Forecasting Engine

**Location**: `uit_aps/ml/`

The forecasting engine provides three models for demand prediction:

#### ARIMA Model (`arima_model.py`)
- **Purpose**: Time series forecasting with seasonality detection
- **Algorithm**: Auto ARIMA with automatic (p,d,q) selection
- **Features**:
  - Automatic seasonality detection
  - AIC-based model selection
  - Confidence intervals via standard error
  - Model parameters stored: p, d, q, AIC

#### Linear Regression Model (`linear_regression_model.py`)
- **Purpose**: Trend-based forecasting for stable demand patterns
- **Algorithm**: Scikit-learn LinearRegression
- **Features**:
  - Simple trend extrapolation
  - R² score for model quality
  - Slope coefficient tracking
  - Fast training and prediction

#### Prophet Model (`prophet.py`)
- **Purpose**: Complex seasonality handling (daily, weekly, monthly, yearly)
- **Algorithm**: Facebook Prophet
- **Features**:
  - Automatic changepoint detection
  - Multiple seasonality patterns
  - Holiday effects
  - Uncertainty intervals

#### AI Explainer (`ai_explainer.py`)
- **Purpose**: Generate human-readable forecast explanations
- **Technology**: OpenAI ChatGPT integration
- **Features**:
  - Automatic explanation generation
  - Recommendation synthesis
  - Background job processing
  - Retry mechanism for failed explanations

**API Endpoints**:
```python
@frappe.whitelist()
def run_forecast(model_name, company, forecast_horizon_days,
                training_period_days, warehouse, item_code, item_group)

@frappe.whitelist()
def get_forecast_results(history_name)

@frappe.whitelist()
def compare_models(item_code, company, forecast_horizon_days,
                  training_period_days, warehouse)
```

---

### 2. Production Planning Module

**Location**: `uit_aps/uit_aps/doctype/aps_production_plan/`

Generates production plans from forecast results or sales orders.

#### Key Features:
- **Source Types**: Forecast, Sales Order, Manual
- **Time Granularity**: Monthly, Quarterly
- **Capacity Planning**: Load analysis and overload detection
- **Status Tracking**: Draft → Planned → Released → Completed/Cancelled

#### Production Plan Item Fields:
```python
- item_code
- forecasted_qty
- planned_production_qty
- planned_period (Month/Quarter)
- planned_start_date
- planned_end_date
- bom (Bill of Materials)
- warehouse
- status
```

**API Endpoints**:
```python
@frappe.whitelist()
def generate_production_plan_from_forecast(forecast_history, plan_name,
    plan_from_period, plan_to_period, time_granularity, company)

@frappe.whitelist()
def refresh_plan_items(production_plan_name)
```

---

### 3. MRP Optimization Engine

**Location**: `uit_aps/uit_api/mrp_optimization.py`

Material Requirements Planning with intelligent supplier selection.

#### Algorithm:
1. **Material Explosion**: BOM-based material requirements calculation
2. **Stock Check**: Available qty vs required qty
3. **Shortage Detection**: Identify materials to purchase
4. **Supplier Optimization**:
   - Score = (0.6 × price_score) + (0.4 × lead_time_score)
   - Lower price is better (normalized)
   - Shorter lead time is better (normalized)

#### Output:
- **APS MRP Result**: Material shortages
- **APS Purchase Suggestion**: Optimized purchase orders

**API Endpoints**:
```python
@frappe.whitelist()
def run_mrp_optimization(production_plan, buffer_days,
                        include_non_stock_items)
```

---

### 4. Hybrid Scheduling System

**Location**: `uit_aps/scheduling/`

#### Tier 1: OR-Tools CP-SAT Solver
**File**: `ortools/scheduler.py`, `ortools/jssp_solver.py`

**Constraints**:
- Precedence: Operations must follow sequence
- No-overlap: One operation per machine at a time
- Capacity: Workstation time limits
- Due dates: Customer delivery deadlines

**Objective Function**:
```
minimize: (makespan_weight × makespan) + (tardiness_weight × total_tardiness)
```

**API**:
```python
@frappe.whitelist()
def run_ortools_scheduling(production_plan, time_limit_seconds,
                          makespan_weight, tardiness_weight)
```

#### Tier 2: Reinforcement Learning Agents
**File**: `rl/agent.py`, `rl/environment.py`

**Agents**:
- **PPO (Proximal Policy Optimization)**: Stable, sample-efficient
- **SAC (Soft Actor-Critic)**: Continuous action space, exploration

**State Representation**:
```python
state = {
    'machine_utilization': [0.0-1.0 per machine],
    'operation_progress': [0.0-1.0 per operation],
    'current_makespan': float,
    'total_tardiness': float,
    'pending_operations': int
}
```

**Action Space**:
- Resequence operations
- Change machine assignment (if flexible)
- Prioritize urgent jobs

**Reward Function**:
```python
reward = -makespan_penalty - tardiness_penalty + completion_bonus
```

**API**:
```python
@frappe.whitelist()
def get_realtime_adjustment(scheduling_run, agent_type)

@frappe.whitelist()
def apply_rl_adjustment(scheduling_run, action_type,
                       target_operation, target_machine)

@frappe.whitelist()
def handle_disruption(disruption_type, affected_resource,
                     scheduling_run, duration_minutes)

@frappe.whitelist()
def train_rl_agent(scheduling_run, agent_type, max_episodes)
```

#### Tier 3: Graph Neural Networks
**File**: `gnn/model.py`, `gnn/predictor.py`, `gnn/recommender.py`

**Graph Structure**:
- **Nodes**: Operations
- **Edges**: Precedence constraints, resource sharing
- **Node Features**: Duration, machine type, item code, status
- **Edge Features**: Precedence type, time lag

**GNN Architecture**:
```python
Input Graph → GAT Layer 1 → ReLU → Dropout →
              GAT Layer 2 → ReLU → Dropout →
              Linear → Output
```

**Predictions**:
1. **Bottleneck Prediction**: Binary classification per operation
2. **Duration Prediction**: Regression for actual operation time
3. **Delay Prediction**: Risk of job lateness
4. **Strategic Recommendations**: Capacity expansion, resource allocation

**API**:
```python
@frappe.whitelist()
def predict_bottlenecks(scheduling_run, threshold)

@frappe.whitelist()
def predict_durations(scheduling_run, confidence_level)

@frappe.whitelist()
def predict_delays(scheduling_run, delay_threshold)

@frappe.whitelist()
def get_recommendations(scheduling_run, max_recommendations)
```

#### Hybrid Scheduler Orchestration
**File**: `scheduling/api/scheduling_api.py`

Combines all three tiers:
```python
@frappe.whitelist()
def run_hybrid_scheduling(production_plan, enable_rl,
                         rl_agent_type, time_limit_seconds):
    # Step 1: Run OR-Tools for baseline
    ortools_result = run_ortools_scheduling(...)

    # Step 2: Apply RL adjustments (if enabled)
    if enable_rl:
        rl_adjustment = get_realtime_adjustment(...)
        apply_rl_adjustment(...)

    # Step 3: Get GNN predictions and recommendations
    bottlenecks = predict_bottlenecks(...)
    recommendations = get_recommendations(...)

    return {
        'schedule': final_schedule,
        'bottlenecks': bottlenecks,
        'recommendations': recommendations
    }
```

---

## Technology Stack

### Backend

#### Core Framework
- **Frappe Framework**: v15.0.0+
  - Python-based web framework
  - Built-in ORM, authentication, REST API
  - Background job queue (RQ)
- **ERPNext**: v15.0.0+
  - Base ERP system
  - Manufacturing, Stock, Purchasing modules

#### Python Dependencies
```
Core:
- frappe>=15.0.0
- python>=3.10
- numpy
- pandas

ML/Forecasting:
- scikit-learn (LinearRegression, preprocessing)
- statsmodels (ARIMA, seasonal_decompose)
- prophet (Facebook Prophet)
- openai (ChatGPT API)
- scipy (confidence intervals)

Optimization/Scheduling:
- ortools (Google OR-Tools CP-SAT)
- torch (PyTorch for RL and GNN)
- gymnasium (RL environment)

Additional:
- requests (HTTP client)
- python-dateutil (date parsing)
```

#### Code Quality Tools
```
- ruff (linter, formatter)
- pyupgrade (Python syntax modernizer)
- pre-commit (git hooks)
```

---

### Frontend

#### Core Framework
```json
{
  "framework": "Vue.js 3.5.13",
  "build_tool": "Vite 6.0.7",
  "language": "JavaScript/TypeScript"
}
```

#### UI Libraries
```json
{
  "component_library": "frappe-ui 0.1.192",
  "ui_primitives": [
    "@radix-ui/react-alert-dialog",
    "@radix-ui/react-dialog",
    "@radix-ui/react-dropdown-menu",
    "@radix-ui/react-label",
    "@radix-ui/react-popover",
    "@radix-ui/react-select",
    "@radix-ui/react-separator",
    "@radix-ui/react-slot",
    "@radix-ui/react-tabs"
  ],
  "charts": "apexcharts 5.3.6",
  "rich_text_editor": "@ckeditor/ckeditor5-react 9.5.0",
  "icons": "lucide-react 0.468.0",
  "animations": "framer-motion 11.18.0"
}
```

#### Styling
```json
{
  "css_framework": "tailwindcss 4.0.0-beta.7",
  "utilities": [
    "class-variance-authority",
    "clsx",
    "tailwind-merge"
  ],
  "preprocessor": "postcss"
}
```

#### State Management
```json
{
  "router": "vue-router 4.5.0",
  "forms": "vee-validate 4.14.7",
  "validation": "yup 1.6.1"
}
```

#### Development Tools
```json
{
  "linter": "@biomejs/biome 1.9.4",
  "type_checking": "vue-tsc 2.2.0",
  "package_manager": "npm"
}
```

---

### Database

**MariaDB** (via Frappe ORM)
- All data access through Frappe's document-based ORM
- Automatic query optimization
- Built-in caching layer
- Transaction management

---

## Data Models

### DocType Hierarchy

```
APS Forecast History (Master)
    └── APS Forecast History Item (Child)
    └── APS Forecast Result (Linked)

APS Production Plan (Master)
    └── APS Production Plan Item (Child)
    └── APS MRP Run (Linked)
    └── APS Scheduling Run (Linked)

APS MRP Run (Master)
    └── APS MRP Result (Child)
    └── APS Purchase Suggestion (Linked)

APS Scheduling Run (Master)
    └── APS Scheduling Result (Child)
```

---

### Core DocTypes

#### 1. APS Forecast History
**Naming**: `FCST-RUN-{YYYY}-{MM}-{DD}-{####}`

```python
{
    # Run Identification
    "run_name": str,
    "company": str (Link to Company),
    "model_used": str (ARIMA/Linear Regression/Prophet),

    # Forecast Parameters
    "forecast_horizon_days": int,
    "start_date": date,
    "end_date": date,
    "training_period_start": date,
    "training_period_end": date,

    # Filters Applied
    "warehouse": str (Link to Warehouse),
    "item_code": str (Link to Item),
    "item_group": str (Link to Item Group),
    "filters_applied": text,

    # Statistics
    "total_sales_orders_used": int,
    "total_items_forecasted": int,
    "total_results_generated": int,
    "successful_forecasts": int,
    "failed_forecasts": int,

    # Accuracy Metrics
    "overall_accuracy_mape": float,  # Mean Absolute Percentage Error
    "avg_confidence_score": float,

    # Execution Tracking
    "run_status": str (Pending/Running/Complete/Failed),
    "run_start_time": datetime,
    "run_end_time": datetime,
    "error_log": text,

    # Model-Specific Parameters
    "parameters_json": text (JSON),

    # AI Analysis
    "ai_analysis": text,  # ChatGPT-generated insights

    # Child Table
    "forecast_results_summary": [
        {
            "item_code": str,
            "forecast_qty": float,
            "confidence_score": float
        }
    ]
}
```

#### 2. APS Forecast Result
**Naming**: Auto-generated

```python
{
    # Linkage
    "forecast_history": str (Link to APS Forecast History),
    "item": str (Link to Item),
    "item_name": str,
    "item_group": str,

    # Forecast Core
    "forecast_period": date,
    "forecast_qty": float,
    "confidence_score": float (0-100),
    "lower_bound": float,
    "upper_bound": float,

    # Model Information
    "model_used": str,
    "model_confidence": float,
    "training_data_points": int,

    # Movement Classification
    "movement_type": str (Fast Moving/Slow Moving/Non Moving),
    "daily_avg_consumption": float,
    "trend_type": str (Upward/Downward/Stable),

    # Inventory Recommendations
    "reorder_level": float,
    "suggested_qty": float,
    "safety_stock": float,
    "current_stock": float,
    "reorder_alert": int (0/1),

    # ARIMA-Specific Fields
    "arima_p": int,
    "arima_d": int,
    "arima_q": int,
    "arima_aic": float,

    # Linear Regression-Specific Fields
    "lr_r2_score": float,
    "lr_slope": float,

    # Prophet-Specific Fields
    "prophet_seasonality_detected": int (0/1),
    "prophet_seasonality_type": str (Weekly/Monthly/Yearly),
    "prophet_changepoint_count": int,

    # Explanations
    "forecast_explanation": text,
    "recommendations": text,
    "notes": text
}
```

#### 3. APS Production Plan
**Naming**: `PROD-PLAN-{YYYY}-{####}`

```python
{
    # Plan Identification
    "plan_name": str,
    "company": str (Link to Company),
    "forecast_history": str (Link to APS Forecast History),

    # Planning Period
    "plan_from_period": date,
    "plan_to_period": date,
    "time_granularity": str (Monthly/Quarterly),

    # Source
    "source_type": str (Forecast/Sales Order/Manual),

    # Status
    "status": str (Draft/Planned/Released/Completed/Cancelled),
    "capacity_status": str (Unknown/OK/Overloaded),

    # Metadata
    "remarks": text,
    "created_by": str (Link to User),
    "creation_date": datetime,

    # Child Table: Production Items
    "items": [
        {
            "item_code": str (Link to Item),
            "item_name": str,
            "forecasted_qty": float,
            "planned_production_qty": float,
            "planned_period": str,
            "planned_start_date": date,
            "planned_end_date": date,
            "bom": str (Link to BOM),
            "warehouse": str (Link to Warehouse),
            "status": str
        }
    ]
}
```

#### 4. APS MRP Run
**Naming**: `MRP-RUN-{YYYY}-{####}`

```python
{
    # Linkage
    "production_plan": str (Link to APS Production Plan),

    # Run Information
    "run_status": str (Pending/Running/Completed/Failed),
    "run_date": datetime,
    "executed_by": str (Link to User),

    # Parameters
    "buffer_days": int,
    "include_non_stock_items": int (0/1),

    # Statistics
    "total_materials": int,
    "total_shortage_qty": float,
    "total_purchase_value": float,

    # Execution Log
    "notes": text,
    "error_log": text
}
```

#### 5. APS MRP Result
**Naming**: Auto-generated

```python
{
    # Linkage
    "mrp_run": str (Link to APS MRP Run),

    # Material Information
    "material_item": str (Link to Item),
    "material_name": str,
    "material_description": text,

    # Quantities
    "required_qty": float,
    "available_qty": float,
    "shortage_qty": float,

    # Timing
    "required_date": date,

    # Source
    "required_for_item": str (Link to Item),
    "required_for_work_order": str (Link to Work Order)
}
```

#### 6. APS Purchase Suggestion
**Naming**: `PURCH-SUGG-{YYYY}-{####}`

```python
{
    # Linkage
    "mrp_run": str (Link to APS MRP Run),
    "mrp_result": str (Link to APS MRP Result),

    # Material
    "material_item": str (Link to Item),
    "material_name": str,

    # Purchase Details
    "purchase_qty": float,
    "required_date": date,

    # Supplier (Optimized Selection)
    "supplier": str (Link to Supplier),
    "supplier_name": str,
    "unit_price": float,
    "lead_time": int (days),
    "total_cost": float,

    # Optimization Score
    "supplier_score": float,  # (0.6 × price_score) + (0.4 × lead_time_score)

    # Status
    "suggestion_status": str (Draft/Approved/Ordered/Rejected),

    # Alternative Suppliers
    "alternative_suppliers": text (JSON),

    # Notes
    "notes": text
}
```

#### 7. APS Scheduling Run
**Naming**: `SCH-RUN-{YYYY}-{####}`

```python
{
    # Linkage
    "production_plan": str (Link to APS Production Plan),

    # Run Information
    "run_status": str (Pending/Running/Completed/Failed),
    "run_date": datetime,
    "executed_by": str (Link to User),

    # Scheduling Strategy
    "scheduling_strategy": str (Forward/Backward/Priority/EDD),
    "scheduling_tier": str (Tier 1 OR-Tools / Tier 2 RL / Tier 3 GNN),

    # OR-Tools Parameters
    "time_limit_seconds": int,
    "min_gap_between_ops": int (minutes),
    "makespan_weight": float,
    "tardiness_weight": float,

    # RL Parameters
    "rl_agent_type": str (PPO/SAC),
    "rl_enabled": int (0/1),

    # Statistics
    "total_job_cards": int,
    "total_operations": int,
    "total_machines": int,
    "total_late_jobs": int,
    "jobs_on_time": int,

    # Solver Results
    "solver_status": str (Optimal/Feasible/Infeasible/Timeout),
    "solve_time_seconds": float,
    "gap_percentage": float,  # Optimality gap

    # Metrics
    "makespan_minutes": float,
    "total_tardiness_minutes": float,
    "machine_utilization": float (0-100%),

    # GNN Predictions
    "predicted_bottlenecks": text (JSON),
    "strategic_recommendations": text (JSON),

    # Execution Log
    "notes": text,
    "error_log": text
}
```

#### 8. APS Scheduling Result
**Naming**: Auto-generated

```python
{
    # Linkage
    "scheduling_run": str (Link to APS Scheduling Run),

    # Operation Identification
    "operation_id": str,
    "job_id": str,
    "job_card_name": str (Link to Job Card),
    "work_order_name": str (Link to Work Order),

    # Item and Operation
    "item_code": str (Link to Item),
    "operation_name": str,
    "machine_id": str (Link to Workstation),

    # Timing
    "start_time": datetime,
    "end_time": datetime,
    "duration_mins": int,

    # Scheduling Metrics
    "sequence": int,
    "is_late": int (0/1),
    "tardiness_mins": int,

    # GNN Predictions
    "is_predicted_bottleneck": int (0/1),
    "predicted_duration_mins": int,
    "bottleneck_probability": float
}
```

#### 9. APS ChatGPT Settings
**Naming**: Single document

```python
{
    # API Configuration
    "api_key": password,
    "model": str (gpt-4/gpt-3.5-turbo),
    "max_tokens": int,
    "temperature": float (0.0-1.0),

    # Prompts
    "system_prompt": text,
    "forecast_explanation_prompt": text,
    "recommendation_prompt": text,

    # Batch Processing
    "batch_size": int,
    "retry_attempts": int,
    "retry_delay_seconds": int,

    # Enable/Disable
    "enabled": int (0/1)
}
```

---

## API Documentation

All APIs are accessed via HTTP POST to:
```
POST /api/method/{module}.{function_name}
Headers:
  Authorization: token {api_key}:{api_secret}
  Content-Type: application/json
```

### Forecasting APIs

#### 1. Run Forecast
```python
@frappe.whitelist()
def run_forecast(model_name, company, forecast_horizon_days,
                training_period_days, warehouse=None,
                item_code=None, item_group=None)
```

**Request**:
```json
{
  "model_name": "ARIMA",
  "company": "UIT Company",
  "forecast_horizon_days": 90,
  "training_period_days": 365,
  "warehouse": "Main Warehouse",
  "item_group": "Raw Materials"
}
```

**Response**:
```json
{
  "message": {
    "forecast_history": "FCST-RUN-2026-01-06-0001",
    "status": "Running",
    "total_items": 45
  }
}
```

#### 2. Get Forecast Results
```python
@frappe.whitelist()
def get_forecast_results(history_name)
```

**Request**:
```json
{
  "history_name": "FCST-RUN-2026-01-06-0001"
}
```

**Response**:
```json
{
  "message": {
    "run_status": "Complete",
    "total_results": 45,
    "results": [
      {
        "item": "ITEM-001",
        "forecast_period": "2026-04-01",
        "forecast_qty": 1250.5,
        "confidence_score": 85.3,
        "lower_bound": 1100.2,
        "upper_bound": 1400.8,
        "movement_type": "Fast Moving",
        "reorder_alert": 1
      }
    ]
  }
}
```

#### 3. Compare Models
```python
@frappe.whitelist()
def compare_models(item_code, company, forecast_horizon_days,
                  training_period_days, warehouse=None)
```

**Request**:
```json
{
  "item_code": "ITEM-001",
  "company": "UIT Company",
  "forecast_horizon_days": 90,
  "training_period_days": 365
}
```

**Response**:
```json
{
  "message": {
    "arima": {"mape": 12.5, "confidence": 85.3},
    "linear_regression": {"mape": 15.2, "confidence": 78.1},
    "prophet": {"mape": 11.8, "confidence": 87.6},
    "recommended_model": "Prophet"
  }
}
```

---

### Production Planning APIs

#### 1. Generate Production Plan from Forecast
```python
@frappe.whitelist()
def generate_production_plan_from_forecast(
    forecast_history, plan_name, plan_from_period,
    plan_to_period, time_granularity, company)
```

**Request**:
```json
{
  "forecast_history": "FCST-RUN-2026-01-06-0001",
  "plan_name": "Q1 2026 Production",
  "plan_from_period": "2026-01-01",
  "plan_to_period": "2026-03-31",
  "time_granularity": "Monthly",
  "company": "UIT Company"
}
```

**Response**:
```json
{
  "message": {
    "production_plan": "PROD-PLAN-2026-0001",
    "total_items": 45,
    "status": "Draft"
  }
}
```

---

### MRP Optimization APIs

#### 1. Run MRP Optimization
```python
@frappe.whitelist()
def run_mrp_optimization(production_plan, buffer_days=0,
                        include_non_stock_items=0)
```

**Request**:
```json
{
  "production_plan": "PROD-PLAN-2026-0001",
  "buffer_days": 7,
  "include_non_stock_items": 0
}
```

**Response**:
```json
{
  "message": {
    "mrp_run": "MRP-RUN-2026-0001",
    "total_materials": 120,
    "total_shortage_qty": 5420.5,
    "purchase_suggestions": 85,
    "status": "Completed"
  }
}
```

---

### Scheduling APIs

#### 1. Run OR-Tools Scheduling (Tier 1)
```python
@frappe.whitelist()
def run_ortools_scheduling(production_plan, time_limit_seconds=300,
                          makespan_weight=0.5, tardiness_weight=0.5)
```

**Request**:
```json
{
  "production_plan": "PROD-PLAN-2026-0001",
  "time_limit_seconds": 600,
  "makespan_weight": 0.6,
  "tardiness_weight": 0.4
}
```

**Response**:
```json
{
  "message": {
    "scheduling_run": "SCH-RUN-2026-0001",
    "solver_status": "Optimal",
    "makespan_minutes": 14520,
    "total_tardiness_minutes": 0,
    "machine_utilization": 78.5,
    "total_operations": 450
  }
}
```

#### 2. Get Real-Time RL Adjustment (Tier 2)
```python
@frappe.whitelist()
def get_realtime_adjustment(scheduling_run, agent_type="PPO")
```

**Request**:
```json
{
  "scheduling_run": "SCH-RUN-2026-0001",
  "agent_type": "PPO"
}
```

**Response**:
```json
{
  "message": {
    "recommended_action": "resequence",
    "target_operation": "OP-12345",
    "new_position": 3,
    "expected_improvement_mins": 45,
    "confidence": 0.87
  }
}
```

#### 3. Predict Bottlenecks (Tier 3)
```python
@frappe.whitelist()
def predict_bottlenecks(scheduling_run, threshold=0.7)
```

**Request**:
```json
{
  "scheduling_run": "SCH-RUN-2026-0001",
  "threshold": 0.7
}
```

**Response**:
```json
{
  "message": {
    "bottlenecks": [
      {
        "operation": "OP-12345",
        "machine": "CNC-01",
        "probability": 0.85,
        "predicted_delay_mins": 120,
        "recommendation": "Consider parallel processing or overtime"
      }
    ]
  }
}
```

#### 4. Run Hybrid Scheduling (All Tiers)
```python
@frappe.whitelist()
def run_hybrid_scheduling(production_plan, enable_rl=1,
                         rl_agent_type="PPO", time_limit_seconds=300)
```

**Request**:
```json
{
  "production_plan": "PROD-PLAN-2026-0001",
  "enable_rl": 1,
  "rl_agent_type": "SAC",
  "time_limit_seconds": 600
}
```

**Response**:
```json
{
  "message": {
    "scheduling_run": "SCH-RUN-2026-0001",
    "tier1_makespan": 14520,
    "tier2_improvement_mins": 180,
    "final_makespan": 14340,
    "bottlenecks": 3,
    "recommendations": [
      "Add capacity to CNC-01 workstation",
      "Cross-train operators for flexibility"
    ]
  }
}
```

---

## Integration Points

### ERPNext Manufacturing Integration

#### Work Order
- **Read**: Fetch operations and workstations
- **Write**: Update scheduled start/end times from APS Scheduling Run

#### Job Card
- **Read**: Get operation status and actual times
- **Write**: Create/update scheduled times

#### Workstation
- **Read**: Capacity, working hours, availability
- **Write**: Update utilization metrics

#### BOM (Bill of Materials)
- **Read**: Material requirements for MRP explosion

---

### ERPNext Stock Integration

#### Item
- **Read**: Item master data, consumption patterns
- **Write**: Update reorder levels from forecast recommendations

#### Bin
- **Read**: Current stock levels for MRP calculations

#### Warehouse
- **Read**: Warehouse configuration for planning

---

### ERPNext Purchasing Integration

#### Supplier
- **Read**: Supplier data for optimization
- **Write**: No direct writes (via Purchase Orders)

#### Item Supplier
- **Read**: Price, lead time for supplier scoring

#### Purchase Order
- **Create**: From APS Purchase Suggestions (manual/auto)

---

### ERPNext Sales Integration

#### Sales Order
- **Read**: Historical demand for forecasting
- **Read**: Future orders for production planning

---

### External Integrations

#### OpenAI ChatGPT
- **API**: `openai.ChatCompletion.create()`
- **Purpose**: AI-powered forecast explanations
- **Authentication**: API key in APS ChatGPT Settings

#### Background Jobs (Redis Queue)
- **Framework**: Frappe's built-in RQ
- **Purpose**: Async processing for AI explanations, model training

---

## Deployment Architecture

### Single-Server Deployment (Development)

```
┌───────────────────────────────────────────────────────┐
│                   Ubuntu/Debian Server                 │
│                                                         │
│  ┌──────────────────────────────────────────────┐    │
│  │  Nginx (Port 80/443)                          │    │
│  │  - Reverse proxy                              │    │
│  │  - Static file serving                        │    │
│  │  - SSL termination                            │    │
│  └──────────────────────────────────────────────┘    │
│                        ↓                               │
│  ┌──────────────────────────────────────────────┐    │
│  │  Gunicorn (WSGI Server)                       │    │
│  │  - Frappe application server                  │    │
│  │  - Multiple workers (4-8)                     │    │
│  └──────────────────────────────────────────────┘    │
│                        ↓                               │
│  ┌──────────────────────────────────────────────┐    │
│  │  Frappe Framework + UIT APS App               │    │
│  │  - Python 3.10+                               │    │
│  │  - Background workers (RQ)                    │    │
│  └──────────────────────────────────────────────┘    │
│                        ↓                               │
│  ┌──────────────────────────────────────────────┐    │
│  │  MariaDB Database                             │    │
│  │  - Port 3306                                  │    │
│  │  - InnoDB storage engine                      │    │
│  └──────────────────────────────────────────────┘    │
│                                                         │
│  ┌──────────────────────────────────────────────┐    │
│  │  Redis                                        │    │
│  │  - Cache (Port 6379)                          │    │
│  │  - Queue (Port 6380)                          │    │
│  └──────────────────────────────────────────────┘    │
│                                                         │
│  ┌──────────────────────────────────────────────┐    │
│  │  Node.js                                      │    │
│  │  - Frappe SocketIO (real-time updates)       │    │
│  └──────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────┘
```

### Production Deployment (Scaled)

```
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer (HAProxy/Nginx)           │
└─────────────────────────────────────────────────────────────┘
                           ↓
        ┌──────────────────┴──────────────────┐
        ↓                                       ↓
┌───────────────────┐                 ┌───────────────────┐
│  App Server 1     │                 │  App Server 2     │
│  - Gunicorn       │                 │  - Gunicorn       │
│  - Frappe + APS   │                 │  - Frappe + APS   │
└───────────────────┘                 └───────────────────┘
        ↓                                       ↓
        └──────────────────┬──────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   Database Cluster (MariaDB)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Primary   │→→│  Replica 1  │  │  Replica 2  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   Redis Cluster                              │
│  ┌─────────────┐  ┌─────────────┐                          │
│  │ Cache Master│  │ Queue Master│                          │
│  │  + Replica  │  │  + Replica  │                          │
│  └─────────────┘  └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                Background Workers (Dedicated Servers)        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ ML Worker 1 │  │ ML Worker 2 │  │ Scheduler   │        │
│  │ (Forecast)  │  │ (Training)  │  │ Worker      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Installation Steps (via Frappe Bench)

```bash
# 1. Install Frappe Bench
pip install frappe-bench

# 2. Initialize a new bench
bench init frappe-bench --frappe-branch version-15
cd frappe-bench

# 3. Create a new site
bench new-site uit.local --admin-password admin --mariadb-root-password root

# 4. Get ERPNext
bench get-app erpnext --branch version-15
bench --site uit.local install-app erpnext

# 5. Get UIT APS
bench get-app uit_aps https://github.com/yourusername/uit_aps.git
bench --site uit.local install-app uit_aps

# 6. Install Python dependencies
pip install -r apps/uit_aps/requirements.txt

# 7. Build frontend assets
cd apps/uit_aps/frontend
npm install
npm run build
cd ../../..

# 8. Start development server
bench start
```

### Environment Variables

```bash
# .env file in bench directory
DB_HOST=localhost
DB_PORT=3306
REDIS_CACHE=redis://localhost:6379
REDIS_QUEUE=redis://localhost:6380
SOCKETIO_PORT=9000

# OpenAI API (set in APS ChatGPT Settings DocType)
OPENAI_API_KEY=sk-...
```

---

## Security Considerations

### Authentication & Authorization
- Frappe's built-in role-based access control (RBAC)
- User roles: System Manager, APS Manager, APS User, Manufacturing User
- Permission levels: Read, Write, Create, Delete, Submit, Cancel

### API Security
- Token-based authentication (API key + secret)
- Rate limiting on API endpoints
- Input validation and sanitization
- SQL injection prevention via Frappe ORM

### Data Protection
- Encrypted database connections (SSL/TLS)
- Password hashing (bcrypt)
- API key encryption in database
- Session management with secure cookies

### AI/ML Security
- OpenAI API key stored encrypted
- No sensitive data sent to external AI services
- Forecast data anonymization option

---

## Performance Optimization

### Database Optimization
- Indexed fields: item, forecast_period, scheduling_run, run_status
- Query optimization via Frappe's query builder
- Regular database maintenance (ANALYZE, OPTIMIZE)

### Caching Strategy
- Redis caching for frequent queries
- Frontend state caching (Vue.js)
- API response caching (short TTL)

### Background Job Queue
- Separate queues: default, long, short
- Priority-based scheduling
- Worker auto-scaling based on queue depth

### ML Model Optimization
- Model serialization for reuse
- Batch prediction for multiple items
- GPU support for PyTorch (RL/GNN)

---

## Monitoring & Logging

### Application Logs
```
logs/
├── web.log          # Gunicorn access logs
├── worker.log       # Background job logs
├── redis_queue.log  # Queue processing logs
└── bench.log        # Bench command logs
```

### Metrics to Monitor
- Forecast accuracy (MAPE trend)
- Scheduling solver time
- MRP run duration
- API response times
- Background job queue length
- Database query performance

### Recommended Tools
- **Logging**: Frappe's built-in logger + ELK stack (optional)
- **Monitoring**: Prometheus + Grafana
- **APM**: New Relic or Datadog
- **Error Tracking**: Sentry

---

## Future Enhancements

### Planned Features
1. **Multi-site forecasting**: Cross-warehouse demand aggregation
2. **Collaborative planning**: Multi-user real-time plan editing
3. **What-if analysis**: Scenario simulation for capacity planning
4. **Advanced KPIs**: OEE, cycle time, throughput dashboards
5. **Mobile app**: iOS/Android for shop floor visibility
6. **IoT integration**: Real-time machine data for scheduling

### Research Areas
1. **Transformer models**: Attention-based forecasting
2. **Multi-agent RL**: Decentralized scheduling
3. **Explainable AI**: SHAP/LIME for GNN predictions
4. **Quantum optimization**: D-Wave for large JSSP instances

---

## Conclusion

UIT APS represents a comprehensive, AI-powered Advanced Planning and Scheduling solution that bridges the gap between traditional ERP systems and modern AI/ML techniques. By combining proven optimization methods (OR-Tools) with cutting-edge AI (RL, GNN), the system delivers:

- **Accurate forecasting** via multi-model ensemble
- **Optimal production planning** with capacity awareness
- **Intelligent MRP** with supplier optimization
- **Hybrid scheduling** that adapts to real-time disruptions
- **Strategic insights** from GNN bottleneck prediction

The modular architecture allows for incremental adoption, starting with basic forecasting and progressing to advanced hybrid scheduling as organizational maturity increases.

---

**Document Version**: 1.0
**Last Updated**: 2026-01-06
**Maintainer**: thanhnc
**Contact**: [your-email@example.com]
