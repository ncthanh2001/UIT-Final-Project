# UIT APS - Database Table Structure

Complete reference for all database tables (DocTypes) in the UIT APS (Advanced Planning & Scheduling) application.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Table Relationship Diagram](#table-relationship-diagram)
3. [Forecasting Tables](#forecasting-tables)
4. [Production Planning Tables](#production-planning-tables)
5. [MRP Tables](#mrp-tables)
6. [Scheduling Tables](#scheduling-tables)
7. [Configuration Tables](#configuration-tables)
8. [Utility Tables](#utility-tables)
9. [ERPNext Integration Points](#erpnext-integration-points)
10. [Index Strategy](#index-strategy)

---

## Overview

The UIT APS application uses **15 DocTypes** (database tables) organized into functional modules:

| Module | Tables | Purpose |
|--------|---------|---------|
| **Forecasting** | 3 tables | AI/ML demand forecasting with ARIMA, LR, Prophet |
| **Production Planning** | 2 tables | Generate optimal production schedules from forecasts |
| **MRP** | 3 tables | Material requirements planning and supplier optimization |
| **Scheduling** | 3 tables | 3-tier hybrid scheduling (OR-Tools, RL, GNN) |
| **Configuration** | 2 tables | System settings and work shift management |
| **Utility** | 2 tables | ML model registry and examples |

**Database Engine:** InnoDB (MySQL/MariaDB)
**Naming Convention:** `tab{DocType Name}` (Frappe standard)
**Change Tracking:** Enabled on most transaction tables

---

## Table Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        UIT APS TABLE RELATIONSHIPS                   │
└─────────────────────────────────────────────────────────────────────┘

FORECASTING MODULE
┌────────────────────────┐
│ APS Forecast History   │ ◄─── Run forecasts, compare models
│ (Parent/Header)        │
│ - run_name             │
│ - model_used           │
│ - run_status           │
│ - overall_accuracy     │
└───────┬────────────────┘
        │ 1:N
        ├────────────────┐
        │                │
        ▼                ▼
┌──────────────────┐  ┌───────────────────────────┐
│ APS Forecast     │  │ APS Forecast Result       │
│ History Item     │  │ (Individual forecasts)    │
│ (Child table)    │  │ - item                    │
└──────────────────┘  │ - forecast_qty            │
                      │ - confidence_score        │
                      │ - model_used              │
                      │ - lower_bound/upper_bound │
                      │ - ARIMA/LR/Prophet params │
                      └─────────┬─────────────────┘
                                │
                                │ Referenced by
                                ▼
PRODUCTION PLANNING MODULE
┌────────────────────────────────────┐
│ APS Production Plan                │ ◄─── Generate from forecasts
│ (Master plan)                      │
│ - plan_name                        │
│ - forecast_history (FK)            │
│ - plan_from_period/plan_to_period  │
│ - source_type (Forecast/SO/Manual) │
│ - status                           │
│ - capacity_status                  │
└────────────┬───────────────────────┘
             │ 1:N
             ▼
┌────────────────────────────────────┐
│ APS Production Plan Item           │
│ (Child table)                      │
│ - item                             │
│ - plan_period                      │
│ - planned_qty                      │
│ - forecast_result (FK)             │
│ - safety_stock                     │
│ - planned_start_date               │
└────────────┬───────────────────────┘
             │
             │ Referenced by
             ├────────────────┐
             │                │
             ▼                ▼
MRP MODULE            SCHEDULING MODULE
┌──────────────┐      ┌─────────────────────┐
│ APS MRP Run  │      │ APS Scheduling Run  │
│ - production │      │ - production_plan   │
│   _plan (FK) │      │ - scheduling_tier   │
│ - run_status │      │ - run_status        │
└──────┬───────┘      │ - makespan_minutes  │
       │ 1:N          │ - solver_status     │
       ▼              │ - llm_analysis      │
┌──────────────────┐  └───────┬─────────────┘
│ APS MRP Result   │          │ 1:N
│ - mrp_run (FK)   │          ▼
│ - material_item  │  ┌──────────────────────────┐
│ - required_qty   │  │ APS Scheduling Result    │
│ - available_qty  │  │ - scheduling_run (FK)    │
│ - shortage_qty   │  │ - job_card (FK)          │
│ - required_date  │  │ - workstation (FK)       │
└──────┬───────────┘  │ - operation (FK)         │
       │              │ - planned_start_time     │
       │              │ - planned_end_time       │
       │ Generates    │ - work_shift (FK)        │
       ▼              │ - is_late                │
┌───────────────────────┐  └──────────────────────────┘
│ APS Purchase          │
│ Suggestion            │  ◄─── Supplier recommendations
│ - mrp_run (FK)        │
│ - material_item       │
│ - supplier            │
│ - suggested_qty       │
│ - estimated_cost      │
└───────────────────────┘

CONFIGURATION & SUPPORT TABLES
┌───────────────────────┐  ┌────────────────────┐
│ APS ChatGPT Settings  │  │ APS Work Shift     │
│ (Single doc)          │  │ - shift_name       │
│ - api_key             │  │ - start_time       │
│ - model_name          │  │ - end_time         │
│ - enabled             │  │ - active_days      │
└───────────────────────┘  └────────────────────┘

┌───────────────────────┐
│ ML Model              │  ◄─── Model version registry
│ - model_name          │
│ - model_type          │
│ - version             │
│ - file_path           │
│ - accuracy_metrics    │
└───────────────────────┘

ERPNEXT INTEGRATION (External Tables)
┌──────────────┐  ┌─────────────┐  ┌───────────┐  ┌──────────┐
│ Sales Order  │  │ Production  │  │ Job Card  │  │ Item     │
│              │  │ Plan        │  │           │  │          │
└──────────────┘  └─────────────┘  └───────────┘  └──────────┘
       ▲                 ▲                ▲             ▲
       │                 │                │             │
       └─────────────────┴────────────────┴─────────────┘
                    Referenced by APS tables
```

---

## Forecasting Tables

### 1. APS Forecast History

**Table Name:** `tabAPS Forecast History`
**Purpose:** Track forecasting runs, store metadata, and aggregate results
**Auto-naming:** `FCST-RUN-{YYYY}-{MM}-{DD}-{####}`

#### Schema

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | VARCHAR(140) | Primary key (auto-generated) | PK, Unique |
| `run_name` | VARCHAR(140) | User-friendly run name | Required |
| `company` | VARCHAR(140) | Link to Company | FK |
| `model_used` | VARCHAR(140) | Model for this run | ARIMA / Linear Regression / Prophet |
| `run_status` | VARCHAR(140) | Execution status | Pending / Running / Complete / Failed |
| `run_start_time` | DATETIME | When forecast started | |
| `run_end_time` | DATETIME | When forecast completed | |
| `forecast_horizon_days` | INT | Number of days to forecast | |
| `start_date` | DATE | Forecast period start | |
| `end_date` | DATE | Forecast period end | |
| `training_period_start` | DATE | Training data start | |
| `training_period_end` | DATE | Training data end | |
| `total_sales_orders_used` | INT | SO count in training | |
| `total_items_forecasted` | INT | Items forecasted | |
| `total_results_generated` | INT | Result records created | |
| `successful_forecasts` | INT | Successful predictions | |
| `failed_forecasts` | INT | Failed predictions | |
| `overall_accuracy_mape_` | FLOAT | Mean Absolute Percentage Error | |
| `avg_confidence_score` | FLOAT | Average confidence % | |
| `model_recommended` | VARCHAR(140) | Best performing model | |
| `parameters_json` | LONGTEXT | Model parameters (JSON) | |
| `filters_applied` | LONGTEXT | Filters used (JSON) | |
| `ai_analysis` | LONGTEXT | ChatGPT explanation | |
| `modified` | DATETIME | Last modified timestamp | |
| `modified_by` | VARCHAR(140) | User who modified | |

#### Relationships
- **1:N** with `APS Forecast History Item` (child table)
- **1:N** with `APS Forecast Result` (linked via `forecast_history`)

#### Indexes
```sql
-- Frappe auto-creates these indexes
CREATE INDEX idx_run_status ON `tabAPS Forecast History`(run_status);
CREATE INDEX idx_modified ON `tabAPS Forecast History`(modified DESC);
CREATE INDEX idx_company ON `tabAPS Forecast History`(company);
```

---

### 2. APS Forecast Result

**Table Name:** `tabAPS Forecast Result`
**Purpose:** Store individual item forecast predictions with confidence intervals
**Auto-naming:** `FCST-{item}-{YYYY}-{MM}-{DD}-{####}`

#### Schema

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | VARCHAR(140) | Primary key | PK, Unique |
| `item` | VARCHAR(140) | Item being forecasted | FK to Item, Required |
| `item_group` | VARCHAR(140) | Fetched from Item | FK to Item Group |
| `forecast_period` | DATE | Period for this forecast | Required |
| `forecast_history` | VARCHAR(140) | Parent forecast run | FK to APS Forecast History |
| `forecast_qty` | FLOAT(2) | Predicted quantity | Required |
| `confidence_score` | FLOAT | Confidence % (0-100) | |
| `model_used` | VARCHAR(140) | Model that generated this | ARIMA / Linear Regression / Prophet |
| **Confidence Interval** | | | |
| `lower_bound` | FLOAT(2) | Pessimistic prediction | |
| `upper_bound` | FLOAT(2) | Optimistic prediction | |
| **Model Metadata** | | | |
| `model_confidence` | VARCHAR(140) | R², AIC, or other metric | |
| `training_data_points` | INT | Training sample size | |
| `movement_type` | VARCHAR(140) | Movement classification | Fast / Slow / Non Moving |
| `daily_avg_consumption` | FLOAT(2) | Units per day | |
| `trend_type` | VARCHAR(140) | Demand trend | Upward / Downward / Stable |
| **Inventory Recommendations** | | | |
| `reorder_level` | FLOAT(2) | Min stock before reorder | |
| `suggested_qty` | INT | Recommended order quantity | |
| `safety_stock` | FLOAT(2) | Buffer stock | |
| `current_stock` | FLOAT(2) | Stock at forecast time | |
| `reorder_alert` | TINYINT | Flag if need to reorder | 0 or 1 |
| **ARIMA Parameters** (if model_used='ARIMA') | | | |
| `arima_p` | INT | AR order | |
| `arima_d` | INT | Differencing | |
| `arima_q` | INT | MA order | |
| `arima_aic` | FLOAT(2) | AIC score | |
| **Linear Regression Parameters** (if model_used='Linear Regression') | | | |
| `lr_r2_score` | FLOAT | R² score (0-100%) | |
| `lr_slope` | FLOAT(4) | Trend slope | |
| **Prophet Parameters** (if model_used='Prophet') | | | |
| `prophet_seasonality_detected` | TINYINT | Has seasonality | 0 or 1 |
| `prophet_seasonality_type` | VARCHAR(140) | Type of seasonality | Weekly / Monthly / Yearly / Multiple |
| `prophet_changepoint_count` | INT | Trend changepoints | |
| **Explanations** | | | |
| `forecast_explanation` | LONGTEXT | Detailed explanation | |
| `recommendations` | LONGTEXT | Action recommendations | |
| `notes` | LONGTEXT | Additional notes | |
| `warehouse` | VARCHAR(140) | Target warehouse | FK to Warehouse |
| `company` | VARCHAR(140) | Company | FK to Company |

#### Indexes
```sql
CREATE INDEX idx_item ON `tabAPS Forecast Result`(item);
CREATE INDEX idx_forecast_period ON `tabAPS Forecast Result`(forecast_period);
CREATE INDEX idx_forecast_history ON `tabAPS Forecast Result`(forecast_history);
CREATE INDEX idx_reorder_alert ON `tabAPS Forecast Result`(reorder_alert);
```

---

### 3. APS Forecast History Item

**Table Name:** `tabAPS Forecast History Item`
**Purpose:** Child table summarizing forecast results per item
**Type:** Child Table (`istable=1`)

#### Schema

| Field | Type | Description |
|-------|------|-------------|
| `parent` | VARCHAR(140) | Link to APS Forecast History |
| `parenttype` | VARCHAR(140) | Always 'APS Forecast History' |
| `parentfield` | VARCHAR(140) | Always 'forecast_results_summary' |
| `idx` | INT | Row number in child table |
| `item_code` | VARCHAR(140) | Item being summarized |
| `total_forecast_qty` | FLOAT | Sum of forecasts |
| `avg_confidence` | FLOAT | Average confidence |
| `best_model` | VARCHAR(140) | Best performing model for this item |

---

## Production Planning Tables

### 4. APS Production Plan

**Table Name:** `tabAPS Production Plan`
**Purpose:** Master production plan generated from forecasts or sales orders
**Auto-naming:** System generated

#### Schema

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | VARCHAR(140) | Primary key | PK, Unique |
| `plan_name` | VARCHAR(140) | Descriptive plan name | Required, e.g., "Kế hoạch Q1-Q2/2025" |
| `company` | VARCHAR(140) | Company | FK to Company, Required |
| `forecast_history` | VARCHAR(140) | Source forecast run | FK to APS Forecast History, Required |
| `plan_from_period` | DATE | Plan start period | Required |
| `plan_to_period` | DATE | Plan end period | Required |
| `source_type` | VARCHAR(140) | Plan source | Forecast / Sales Order / Manual, Required |
| `time_granularity` | VARCHAR(140) | Time resolution | Monthly / Quarterly |
| `status` | VARCHAR(140) | Plan status | Draft / Planned / Released / Completed / Cancelled |
| `capacity_status` | VARCHAR(140) | Capacity vs plan | Unknown / OK / Overloaded |
| `remarks` | TEXT | Additional notes | |
| `modified` | DATETIME | Last modified | |
| `modified_by` | VARCHAR(140) | Modified by user | |

#### Relationships
- **1:N** with `APS Production Plan Item` (child table)
- Referenced by `APS MRP Run` (FK)
- Referenced by `APS Scheduling Run` (FK)

#### Indexes
```sql
CREATE INDEX idx_forecast_history ON `tabAPS Production Plan`(forecast_history);
CREATE INDEX idx_status ON `tabAPS Production Plan`(status);
CREATE INDEX idx_plan_period ON `tabAPS Production Plan`(plan_from_period, plan_to_period);
```

---

### 5. APS Production Plan Item

**Table Name:** `tabAPS Production Plan Item`
**Purpose:** Child table with detailed item production quantities
**Type:** Child Table (`istable=1`)

#### Schema

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `parent` | VARCHAR(140) | Link to APS Production Plan | FK, Required |
| `parenttype` | VARCHAR(140) | Always 'APS Production Plan' | |
| `parentfield` | VARCHAR(140) | Always 'items' | |
| `idx` | INT | Row sequence | |
| `item` | VARCHAR(140) | Item to produce | FK to Item, Required |
| `plan_period` | DATE | Production period | Required |
| `planned_qty` | FLOAT | Quantity to produce | Required |
| `forecast_result` | VARCHAR(140) | Source forecast | FK to APS Forecast Result |
| `forecast_quantiy` | FLOAT | Original forecast qty | Typo in fieldname (preserved for compatibility) |
| `safety_stock` | FLOAT | Added safety stock | |
| `current_stock` | FLOAT | Current inventory | |
| `planned_start_date` | DATE | Production start | |
| `lead_time_days` | FLOAT | Production lead time | |

---

## MRP Tables

### 6. APS MRP Run

**Table Name:** `tabAPS MRP Run`
**Purpose:** Track MRP calculation runs
**Auto-naming:** System generated

#### Schema

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | VARCHAR(140) | Primary key | PK, Unique |
| `production_plan` | VARCHAR(140) | Source production plan | FK to APS Production Plan, Required |
| `run_status` | VARCHAR(140) | Execution status | Pending / Running / Completed / Failed |
| `run_date` | DATETIME | When MRP was executed | Default: Now |
| `executed_by` | VARCHAR(140) | User who ran MRP | FK to User |
| `total_materials` | INT | Materials with shortage | |
| `notes` | TEXT | Additional notes | |
| `modified` | DATETIME | Last modified | |

#### Relationships
- **1:N** with `APS MRP Result`
- **1:N** with `APS Purchase Suggestion`

#### Indexes
```sql
CREATE INDEX idx_production_plan ON `tabAPS MRP Run`(production_plan);
CREATE INDEX idx_run_status ON `tabAPS MRP Run`(run_status);
```

---

### 7. APS MRP Result

**Table Name:** `tabAPS MRP Result`
**Purpose:** Material requirements and shortage details
**Auto-naming:** System generated

#### Schema

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | VARCHAR(140) | Primary key | PK, Unique |
| `mrp_run` | VARCHAR(140) | Parent MRP run | FK to APS MRP Run, Required |
| `material_item` | VARCHAR(140) | Raw material/component | FK to Item, Required |
| `source_plan_item` | VARCHAR(140) | Production plan item | FK to APS Production Plan Item |
| `required_qty` | FLOAT | Total requirement | Required |
| `available_qty` | FLOAT | Current stock snapshot | |
| `shortage_qty` | FLOAT | Deficit amount | Required |
| `required_date` | DATE | When material is needed | |
| `remarks` | TEXT | Notes | |

#### Indexes
```sql
CREATE INDEX idx_mrp_run ON `tabAPS MRP Result`(mrp_run);
CREATE INDEX idx_material_item ON `tabAPS MRP Result`(material_item);
CREATE INDEX idx_shortage ON `tabAPS MRP Result`(shortage_qty);
```

---

### 8. APS Purchase Suggestion

**Table Name:** `tabAPS Purchase Suggestion`
**Purpose:** Supplier recommendations with multi-criteria optimization
**Auto-naming:** System generated

#### Schema

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | VARCHAR(140) | Primary key | PK, Unique |
| `mrp_run` | VARCHAR(140) | Source MRP run | FK to APS MRP Run |
| `material_item` | VARCHAR(140) | Material to purchase | FK to Item |
| `supplier` | VARCHAR(140) | Recommended supplier | FK to Supplier |
| `suggested_qty` | FLOAT | Quantity to order | |
| `estimated_cost` | DECIMAL(18,2) | Total estimated cost | |
| `lead_time_days` | INT | Supplier lead time | |
| `supplier_score` | FLOAT | Multi-criteria score | |
| `price_per_unit` | DECIMAL(18,2) | Unit price | |
| `quality_rating` | FLOAT | Supplier quality (0-5) | |
| `delivery_reliability` | FLOAT | On-time delivery % | |
| `notes` | TEXT | Additional context | |

#### Indexes
```sql
CREATE INDEX idx_mrp_run ON `tabAPS Purchase Suggestion`(mrp_run);
CREATE INDEX idx_supplier ON `tabAPS Purchase Suggestion`(supplier);
CREATE INDEX idx_material ON `tabAPS Purchase Suggestion`(material_item);
```

---

## Scheduling Tables

### 9. APS Scheduling Run

**Table Name:** `tabAPS Scheduling Run`
**Purpose:** Production scheduling execution with 3-tier hybrid approach
**Auto-naming:** System generated
**Description:** Stores parameters, solver status, and performance metrics

#### Schema

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | VARCHAR(140) | Primary key | PK, Unique |
| `production_plan` | VARCHAR(140) | ERPNext Production Plan | FK to Production Plan, Required |
| `run_status` | VARCHAR(140) | Execution status | Pending / Running / Completed / Failed |
| `scheduling_strategy` | VARCHAR(140) | Scheduling approach | Forward / Backward / Priority / EDD |
| `scheduling_tier` | VARCHAR(140) | Hybrid tier used | Tier 1 - OR-Tools / Tier 2 - RL Agent / Tier 3 - GNN |
| `run_date` | DATETIME | Execution timestamp | Default: Now |
| `executed_by` | VARCHAR(140) | User | FK to User |
| **Solver Configuration** | | | |
| `time_limit_seconds` | INT | Max solver time | Default: 300 |
| `min_gap_between_ops` | INT | Buffer time (minutes) | Default: 10 |
| `makespan_weight` | FLOAT | Objective weight | Default: 1.0 |
| `tardiness_weight` | FLOAT | Penalty weight | Default: 10.0 |
| **Results** | | | |
| `total_job_cards` | INT | Jobs scheduled | Read-only |
| `total_late_jobs` | INT | Late jobs | Read-only |
| `jobs_on_time` | INT | On-time jobs | Read-only |
| `solver_status` | VARCHAR(140) | OR-Tools status | Not Started / Optimal / Feasible / Infeasible / Timeout / Error |
| `solve_time_seconds` | FLOAT | Actual solve time | Read-only |
| `gap_percentage` | FLOAT | Optimality gap % | Read-only |
| **Performance Metrics** | | | |
| `makespan_minutes` | INT | Total schedule duration | Read-only |
| `total_tardiness_minutes` | INT | Sum of delays | Read-only |
| `machine_utilization` | FLOAT | Avg utilization % | Read-only |
| **AI Analysis** | | | |
| `llm_analysis_button` | BUTTON | Trigger AI analysis | |
| `llm_analysis_language` | VARCHAR(140) | Language (vi/en) | Default: vi |
| `llm_analysis_date` | DATETIME | When analyzed | Read-only |
| `llm_analysis_model` | VARCHAR(140) | GPT model used | Read-only |
| `llm_analysis_content` | LONGTEXT | AI recommendations | Read-only, HTML |
| `notes` | TEXT | User notes | |

#### Relationships
- **1:N** with `APS Scheduling Result`

#### Indexes
```sql
CREATE INDEX idx_production_plan ON `tabAPS Scheduling Run`(production_plan);
CREATE INDEX idx_run_status ON `tabAPS Scheduling Run`(run_status);
CREATE INDEX idx_scheduling_tier ON `tabAPS Scheduling Run`(scheduling_tier);
```

---

### 10. APS Scheduling Result

**Table Name:** `tabAPS Scheduling Result`
**Purpose:** Individual job card schedule assignments
**Auto-naming:** System generated
**Track Changes:** Enabled

#### Schema

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | VARCHAR(140) | Primary key | PK, Unique |
| `scheduling_run` | VARCHAR(140) | Parent scheduling run | FK to APS Scheduling Run, Required |
| `job_card` | VARCHAR(140) | ERPNext Job Card | FK to Job Card, Required |
| `workstation` | VARCHAR(140) | Assigned workstation | FK to Workstation, Required |
| `operation` | VARCHAR(140) | Operation to perform | FK to Operation, Required |
| `planned_start_time` | DATETIME | Scheduled start | Required |
| `planned_end_time` | DATETIME | Scheduled end | Required |
| `work_shift` | VARCHAR(140) | Assigned shift | FK to APS Work Shift |
| `is_late` | TINYINT | Late job flag | 0 or 1 |
| `delay_reason` | TEXT | Why late | Conditional |
| `remarks` | TEXT | Notes | |

#### Indexes
```sql
CREATE INDEX idx_scheduling_run ON `tabAPS Scheduling Result`(scheduling_run);
CREATE INDEX idx_job_card ON `tabAPS Scheduling Result`(job_card);
CREATE INDEX idx_workstation ON `tabAPS Scheduling Result`(workstation);
CREATE INDEX idx_start_time ON `tabAPS Scheduling Result`(planned_start_time);
```

---

### 11. APS Work Shift

**Table Name:** `tabAPS Work Shift`
**Purpose:** Define work shifts for scheduling constraints
**Auto-naming:** System generated

#### Schema

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | VARCHAR(140) | Primary key | PK, Unique |
| `shift_name` | VARCHAR(140) | Shift name | Required, e.g., "Morning Shift" |
| `start_time` | TIME | Shift start | Required |
| `end_time` | TIME | Shift end | Required |
| `active_days` | TEXT | Working days (JSON) | e.g., ["Monday", "Tuesday", ...] |
| `break_start` | TIME | Break start | Optional |
| `break_end` | TIME | Break end | Optional |
| `capacity_multiplier` | FLOAT | Capacity factor | Default: 1.0 |
| `enabled` | TINYINT | Active shift | 0 or 1 |
| `company` | VARCHAR(140) | Company | FK to Company |

---

## Configuration Tables

### 12. APS ChatGPT Settings

**Table Name:** `tabAPS ChatGPT Settings`
**Purpose:** OpenAI API configuration for AI explanations
**Type:** Single DocType (only one record)

#### Schema

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | VARCHAR(140) | Always "APS ChatGPT Settings" | PK |
| `api_key` | PASSWORD | OpenAI API key | Encrypted |
| `model_name` | VARCHAR(140) | GPT model | e.g., "gpt-4-turbo", "gpt-3.5-turbo" |
| `enabled` | TINYINT | Enable AI features | 0 or 1 |
| `max_tokens` | INT | Max response tokens | Default: 1000 |
| `temperature` | FLOAT | Creativity (0-1) | Default: 0.7 |
| `organization_id` | VARCHAR(140) | OpenAI org ID | Optional |
| `timeout_seconds` | INT | API timeout | Default: 30 |

---

### 13. ML Model

**Table Name:** `tabML Model`
**Purpose:** Registry for ML model versions and metadata
**Auto-naming:** System generated

#### Schema

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | VARCHAR(140) | Primary key | PK, Unique |
| `model_name` | VARCHAR(140) | Model name | Required |
| `model_type` | VARCHAR(140) | Model category | ARIMA / Linear Regression / Prophet / RL / GNN |
| `version` | VARCHAR(140) | Version string | e.g., "v1.2.3" |
| `file_path` | TEXT | Model file location | Absolute path |
| `accuracy_metrics` | LONGTEXT | Performance metrics (JSON) | e.g., {"MAPE": 12.5, "R2": 0.85} |
| `training_date` | DATETIME | When trained | |
| `trained_by` | VARCHAR(140) | User | FK to User |
| `training_dataset_size` | INT | Sample count | |
| `hyperparameters` | LONGTEXT | Model config (JSON) | |
| `is_active` | TINYINT | Currently in use | 0 or 1 |
| `description` | TEXT | Model description | |

---

## Utility Tables

### 14. Code Example

**Table Name:** `tabCode Example`
**Purpose:** Sample code snippets and examples (for development/testing)
**Auto-naming:** System generated

#### Schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | VARCHAR(140) | Primary key |
| `example_name` | VARCHAR(140) | Example title |
| `code_snippet` | LONGTEXT | Sample code |
| `language` | VARCHAR(140) | Programming language |
| `description` | TEXT | What it demonstrates |
| `category` | VARCHAR(140) | Example category |

---

## ERPNext Integration Points

The UIT APS app integrates with standard ERPNext tables:

### Referenced ERPNext Tables

| ERPNext Table | Purpose | Referenced By |
|---------------|---------|---------------|
| **Item** | Products, raw materials | All APS tables with `item`, `material_item` fields |
| **Company** | Multi-company support | Most APS tables |
| **Warehouse** | Stock locations | Forecast Result, Production Plan |
| **Supplier** | Vendor information | APS Purchase Suggestion |
| **Sales Order** | Historical sales data | Forecasting (training data) |
| **Production Plan** | ERPNext production plan | APS Scheduling Run |
| **Work Order** | Manufacturing orders | Created from APS Production Plan |
| **Job Card** | Shop floor tasks | APS Scheduling Result |
| **Workstation** | Manufacturing resources | APS Scheduling Result |
| **Operation** | Manufacturing operations | APS Scheduling Result |
| **User** | System users | Execution tracking |
| **Item Group** | Product categories | Forecasting filters |

### Data Flow

```
Sales Order → APS Forecast History → APS Forecast Result
                        ↓
            APS Production Plan → Production Plan (ERPNext)
                        ↓                    ↓
                  APS MRP Run          Work Order (ERPNext)
                        ↓                    ↓
            APS Purchase Suggestion    Job Card (ERPNext)
                                             ↓
                                  APS Scheduling Result
```

---

## Index Strategy

### Performance Optimization

All APS tables use InnoDB engine with these indexing strategies:

1. **Primary Keys:** Auto-indexed on `name` field
2. **Foreign Keys:** Indexed on all Link fields (`_idx` suffix)
3. **Status Fields:** Indexed for list view filtering
4. **Date Fields:** Indexed for range queries
5. **Modified Timestamp:** Indexed for sorting (DESC)

### Recommended Custom Indexes

For large deployments, consider these additional indexes:

```sql
-- Forecasting performance
CREATE INDEX idx_forecast_item_period
ON `tabAPS Forecast Result`(item, forecast_period);

-- Production planning queries
CREATE INDEX idx_plan_status_period
ON `tabAPS Production Plan`(status, plan_from_period);

-- Scheduling lookups
CREATE INDEX idx_schedule_time_range
ON `tabAPS Scheduling Result`(planned_start_time, planned_end_time);

-- MRP material analysis
CREATE INDEX idx_mrp_material_shortage
ON `tabAPS MRP Result`(material_item, shortage_qty);
```

---

## Data Retention & Archival

### Recommended Retention Policies

| Table | Retention | Archive Strategy |
|-------|-----------|------------------|
| APS Forecast History | 2 years | Archive to cold storage |
| APS Forecast Result | 2 years | Archive with history |
| APS Production Plan | 3 years | Keep for audit |
| APS MRP Run | 1 year | Archive older runs |
| APS Scheduling Run | 1 year | Archive completed runs |
| APS Scheduling Result | 1 year | Archive with run |

### Archive Example

```sql
-- Archive forecasts older than 2 years
INSERT INTO `tabAPS Forecast History Archive`
SELECT * FROM `tabAPS Forecast History`
WHERE run_start_time < DATE_SUB(NOW(), INTERVAL 2 YEAR);

DELETE FROM `tabAPS Forecast History`
WHERE run_start_time < DATE_SUB(NOW(), INTERVAL 2 YEAR);
```

---

## Change Tracking

Tables with `track_changes=1`:
- APS Forecast History
- APS Forecast Result
- APS Scheduling Result

All changes are logged to `tabVersion` (Frappe standard).

---

## Naming Conventions

| Pattern | Example | Usage |
|---------|---------|-------|
| `FCST-RUN-{date}-{seq}` | FCST-RUN-2025-01-07-0001 | Forecast History |
| `FCST-{item}-{date}-{seq}` | FCST-TP-BLV-001-2025-01-07-0001 | Forecast Result |
| System Generated | APS-PROD-00001 | Production Plan |
| System Generated | APS-MRP-00001 | MRP Run |
| System Generated | APS-SCHED-00001 | Scheduling Run |

---

## Database Size Estimates

Typical storage requirements (based on 1000 items, 3 months forecast):

| Table | Records | Size per Record | Total Size |
|-------|---------|-----------------|------------|
| APS Forecast History | ~50 runs | 5 KB | 250 KB |
| APS Forecast Result | ~150,000 | 2 KB | 300 MB |
| APS Production Plan | ~20 plans | 3 KB | 60 KB |
| APS Production Plan Item | ~5,000 | 1 KB | 5 MB |
| APS MRP Result | ~10,000 | 1 KB | 10 MB |
| APS Scheduling Result | ~50,000 | 0.5 KB | 25 MB |
| **Total Estimated** | | | **~340 MB** |

---

## Backup Recommendations

```bash
# Daily backup of APS tables
mysqldump -u root -p --databases erpnext \
  --tables \
  tabAPS\ Forecast\ History \
  tabAPS\ Forecast\ Result \
  tabAPS\ Production\ Plan \
  tabAPS\ Production\ Plan\ Item \
  tabAPS\ MRP\ Run \
  tabAPS\ MRP\ Result \
  tabAPS\ Purchase\ Suggestion \
  tabAPS\ Scheduling\ Run \
  tabAPS\ Scheduling\ Result \
  > aps_backup_$(date +%Y%m%d).sql
```

---

## Version Information

**Document Version:** 1.0.0
**Last Updated:** 2025-01-07
**Compatible with:** ERPNext v15+, Frappe v15+
**Database:** MariaDB 10.3+, MySQL 5.7+

---

## Additional Resources

- **FUNCTIONAL_GUIDE.md** - User workflows and feature documentation
- **ARCHITECTURE.md** - System design and technical architecture
- **API Documentation** - `/apps/uit_aps/uit_aps/uit_api/`
- **Demo Scripts** - `/apps/uit_aps/uit_aps/demo_scripts/`

---

**For technical support or questions about table structures, please refer to the source JSON files in:**
`/apps/uit_aps/uit_aps/uit_aps/doctype/`
