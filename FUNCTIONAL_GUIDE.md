# UIT APS - Functional Guide & User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Demand Forecasting](#demand-forecasting)
4. [Production Planning](#production-planning)
5. [MRP Optimization](#mrp-optimization)
6. [Production Scheduling](#production-scheduling)
7. [Complete Workflow Examples](#complete-workflow-examples)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Introduction

### What is UIT APS?

UIT APS (Advanced Planning and Scheduling) is an intelligent manufacturing planning system that helps you:

- **Forecast demand** using AI/ML models to predict future product requirements
- **Plan production** based on forecasts or actual sales orders
- **Optimize materials** by calculating exact material requirements and suggesting optimal suppliers
- **Schedule operations** using advanced algorithms that minimize production time and delays

### Key Benefits

- **Reduced stockouts**: Accurate forecasting prevents running out of inventory
- **Lower costs**: Optimal supplier selection and reduced excess inventory
- **Faster delivery**: Intelligent scheduling minimizes production time
- **Better decisions**: AI-powered insights and recommendations
- **Real-time adaptation**: Dynamic rescheduling when disruptions occur

---

## Getting Started

### Prerequisites

Before using UIT APS, ensure you have:

1. **ERPNext v15+** installed and configured
2. **Basic master data** set up:
   - Items with item codes and descriptions
   - BOMs (Bill of Materials) for manufactured items
   - Workstations with capacity and working hours
   - Suppliers with pricing and lead times
   - Warehouses for stock management
3. **Historical data**:
   - At least 3-6 months of Sales Order history for accurate forecasting
   - Item prices from suppliers
   - Past production records (optional, for better scheduling)

### Initial Setup

#### 1. Configure ChatGPT Settings (Optional)

For AI-powered explanations, configure OpenAI integration:

1. Go to **UIT APS > APS ChatGPT Settings**
2. Enter your OpenAI API key
3. Select model (GPT-4 recommended for better accuracy)
4. Configure parameters:
   - Max tokens: 2000-4000
   - Temperature: 0.7 (balance between creativity and consistency)
5. Save the settings

#### 2. Verify Master Data

Check that you have:
- Items with proper classification (item groups)
- Active suppliers for purchased items
- BOMs for all manufactured items
- Workstations configured with operations

---

## Demand Forecasting

### Overview

The forecasting module predicts future demand for your items based on historical sales data. It uses three different AI/ML models and automatically selects the best one.

### How Forecasting Works

```
Historical Sales Orders → Data Extraction → Model Training →
Forecast Generation → Confidence Scoring → AI Explanation → Results
```

#### Step-by-Step Process:

1. **Data Collection**: System pulls historical sales order data
2. **Preprocessing**: Cleans and aggregates data by time periods
3. **Model Training**: Trains three models (ARIMA, Linear Regression, Prophet)
4. **Prediction**: Each model generates forecasts with confidence intervals
5. **Evaluation**: Calculates accuracy metrics (MAPE - Mean Absolute Percentage Error)
6. **Explanation**: ChatGPT generates human-readable insights
7. **Recommendations**: System suggests reorder levels and safety stock

### The Three Forecasting Models

#### 1. ARIMA (AutoRegressive Integrated Moving Average)

**Best for**: Items with clear seasonal patterns and trends

**How it works**:
- Analyzes historical patterns in your sales data
- Automatically detects seasonality (weekly, monthly, yearly)
- Uses past values and past errors to predict future values
- Calculates optimal parameters (p, d, q) automatically

**Example**:
- Ice cream sales that spike in summer and drop in winter
- Office supplies with monthly purchasing cycles

**Model Parameters**:
- `p` (AR order): How many past values to consider
- `d` (Differencing): How many times to difference the data to make it stationary
- `q` (MA order): How many past errors to consider
- `AIC` (Akaike Information Criterion): Lower is better quality

#### 2. Linear Regression

**Best for**: Items with stable, linear growth or decline trends

**How it works**:
- Fits a straight line through historical data points
- Extends the line into the future for predictions
- Simple and fast, works well for consistent trends
- Calculates R² score to measure how well the line fits

**Example**:
- New product with steady growth
- Declining product being phased out
- Commodity items with consistent demand

**Model Metrics**:
- `R² score`: 0-1, higher means better fit (>0.7 is good)
- `Slope`: Positive (growing), negative (declining), or near-zero (stable)

#### 3. Prophet (Facebook Prophet)

**Best for**: Items with multiple seasonal patterns and special events

**How it works**:
- Decomposes time series into trend + seasonality + holidays
- Handles multiple seasonality levels (daily, weekly, monthly, yearly)
- Automatically detects changepoints (when trends shift)
- Robust to missing data and outliers

**Example**:
- Retail items affected by holidays and promotions
- Products with both weekly and yearly seasonality
- Items with sudden trend changes

**Model Metrics**:
- `Seasonality type`: Weekly, Monthly, Yearly, or Multiple
- `Changepoint count`: Number of trend shifts detected

### Running a Forecast

#### Method 1: Via UI

1. Go to **UIT APS > APS Forecast History**
2. Click **New**
3. Fill in the form:

**Basic Settings**:
- **Company**: Select your company
- **Model Used**: Choose one (or run all three and compare)
  - ARIMA: For seasonal patterns
  - Linear Regression: For stable trends
  - Prophet: For complex seasonality

**Time Periods**:
- **Forecast Horizon Days**: How far into the future (e.g., 90 days = 3 months)
- **Training Period Days**: How much historical data to use (recommended: 365+ days)

**Filters** (optional - leave blank to forecast all items):
- **Warehouse**: Specific warehouse
- **Item Code**: Single item
- **Item Group**: All items in a category

4. Click **Save**
5. Click **Run Forecast** button
6. Wait for processing (can take several minutes for many items)

#### Method 2: Via API

```python
import requests

url = "https://your-site.com/api/method/uit_aps.uit_api.run_model.run_forecast"
headers = {
    "Authorization": "token YOUR_API_KEY:YOUR_API_SECRET",
    "Content-Type": "application/json"
}
data = {
    "model_name": "ARIMA",
    "company": "UIT Company",
    "forecast_horizon_days": 90,
    "training_period_days": 365,
    "item_group": "Raw Materials"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()
print(f"Forecast Run: {result['message']['forecast_history']}")
```

### Understanding Forecast Results

After the forecast completes, click on the **Forecast History** record to see results.

#### Key Metrics in Forecast History:

- **Overall Accuracy (MAPE)**: Lower is better
  - <10% = Excellent
  - 10-20% = Good
  - 20-50% = Acceptable
  - >50% = Poor (consider more data or different model)

- **Average Confidence Score**: 0-100%, higher is better
  - >80% = High confidence
  - 60-80% = Medium confidence
  - <60% = Low confidence (be cautious)

- **Successful vs Failed Forecasts**: How many items were successfully forecasted

#### Forecast Results Table:

Each item gets a detailed forecast result with:

**Forecast Data**:
- **Forecast Period**: The date for this prediction
- **Forecast Qty**: Predicted quantity needed
- **Confidence Score**: How confident the model is (0-100%)
- **Lower Bound**: Worst-case scenario (use for safety stock)
- **Upper Bound**: Best-case scenario

**Movement Classification**:
- **Fast Moving**: High consumption, critical to keep in stock
- **Slow Moving**: Low consumption, order less frequently
- **Non Moving**: No recent sales, consider discontinuing

**Trend Analysis**:
- **Upward**: Demand is increasing, plan for growth
- **Downward**: Demand is decreasing, reduce orders
- **Stable**: Consistent demand, maintain current levels

**Inventory Recommendations**:
- **Reorder Level**: When stock hits this level, order more
- **Suggested Qty**: How much to order
- **Safety Stock**: Buffer inventory for unexpected demand
- **Reorder Alert**: Flag if current stock is below reorder level

**AI Explanation** (if ChatGPT is configured):
- Human-readable explanation of the forecast
- Key factors affecting the prediction
- Actionable recommendations

### Comparing Models

To find the best model for a specific item:

1. Go to **UIT APS > Compare Forecast Models**
2. Select the item
3. Enter forecast and training periods
4. Click **Compare**

The system will:
- Run all three models on the same data
- Show accuracy metrics (MAPE) for each
- Recommend the best model
- Display side-by-side predictions

**When to use each model**:
- High seasonality → **ARIMA** or **Prophet**
- Simple trend → **Linear Regression**
- Complex patterns + holidays → **Prophet**
- Unsure → Run comparison and use the recommended model

### Forecast Workflow Tips

1. **Start with a small test**:
   - Forecast one item group first
   - Review accuracy before scaling up
   - Adjust training period if needed

2. **Check data quality**:
   - Ensure sales orders are properly dated
   - Clean up any duplicate or test data
   - Need at least 30-60 data points for reliable forecasts

3. **Refine over time**:
   - Re-run forecasts monthly or quarterly
   - Track actual vs predicted to measure accuracy
   - Adjust models based on performance

4. **Use AI explanations**:
   - Review ChatGPT insights for business context
   - Share recommendations with planning team
   - Document lessons learned

---

## Production Planning

### Overview

Production planning converts forecast results (or sales orders) into concrete production plans with quantities and timelines.

### How Production Planning Works

```
Forecast Results / Sales Orders → Plan Generation →
BOM Explosion → Capacity Check → Production Plan Items
```

#### Planning Process:

1. **Source Selection**: Choose forecast or sales orders as input
2. **Period Aggregation**: Group by month or quarter
3. **BOM Lookup**: Find manufacturing BOM for each item
4. **Quantity Calculation**: Aggregate forecasted/ordered quantities
5. **Timeline Assignment**: Set planned start and end dates
6. **Capacity Validation**: Check if workstations can handle the load

### Creating a Production Plan

#### From Forecast Results:

1. Go to **UIT APS > APS Production Plan**
2. Click **New**
3. Fill in the form:

**Basic Info**:
- **Plan Name**: Descriptive name (e.g., "Q1 2026 Production")
- **Company**: Your company
- **Forecast History**: Select a completed forecast run

**Planning Period**:
- **Plan From Period**: Start date (e.g., 2026-01-01)
- **Plan To Period**: End date (e.g., 2026-03-31)
- **Time Granularity**:
  - **Monthly**: One plan item per item per month
  - **Quarterly**: One plan item per item per quarter

**Source**:
- **Source Type**: Select "Forecast"

4. Click **Save**
5. Click **Generate Plan** button
6. Review the generated plan items

#### From Sales Orders:

1. Create a new **APS Production Plan**
2. Set **Source Type** to "Sales Order"
3. Select date range to include sales orders
4. Click **Generate Plan**

The system will pull actual sales orders instead of forecasts.

#### Manual Planning:

1. Create a new **APS Production Plan**
2. Set **Source Type** to "Manual"
3. Manually add items in the **Items** table:
   - Item Code
   - Planned Production Qty
   - Planned Period
   - Warehouse

### Understanding Production Plan Items

Each item in the plan has:

**Item Details**:
- **Item Code**: What to produce
- **Item Name**: Item description
- **BOM**: Bill of Materials (auto-fetched or select manually)

**Quantities**:
- **Forecasted Qty**: From forecast (if source is forecast)
- **Planned Production Qty**: Actual quantity to produce (can be adjusted)

**Timing**:
- **Planned Period**: Month/Quarter for this production
- **Planned Start Date**: When to start manufacturing
- **Planned End Date**: Target completion date

**Location**:
- **Warehouse**: Where to store finished goods

**Status**:
- Draft → Planned → Released → Completed → Cancelled

### Plan Status Workflow

```
Draft (editing) → Planned (finalized) → Released (sent to shop floor) →
Completed (production done) or Cancelled (plan abandoned)
```

**Status Descriptions**:

- **Draft**: Still editing, can modify freely
- **Planned**: Finalized but not yet released to manufacturing
- **Released**: Sent to shop floor, Work Orders can be created
- **Completed**: All production finished
- **Cancelled**: Plan cancelled, no production

### Capacity Planning

The system can check if your workstations have enough capacity:

**Capacity Status**:
- **Unknown**: Capacity check not run yet
- **OK**: All workstations have sufficient capacity
- **Overloaded**: Some workstations over capacity (need action)

**How to check capacity**:
1. Open the production plan
2. Click **Check Capacity** button
3. Review the capacity report
4. If overloaded:
   - Reduce planned quantities
   - Extend timeline
   - Add overtime/extra shifts
   - Outsource some operations

### Production Plan Actions

**Refresh Plan Items**:
- Recalculates quantities from source data
- Updates if forecast results changed
- Use when you've re-run forecasts

**Release Plan**:
- Changes status to "Released"
- Locks the plan from edits
- Ready for Work Order creation

**Create Work Orders**:
- Generates ERPNext Work Orders from plan items
- One Work Order per plan item
- Links back to production plan

---

## MRP Optimization

### Overview

MRP (Material Requirements Planning) calculates exactly what materials you need to buy to fulfill the production plan. It includes intelligent supplier selection to minimize costs and lead times.

### How MRP Works

```
Production Plan → BOM Explosion → Stock Check →
Shortage Calculation → Supplier Optimization → Purchase Suggestions
```

#### MRP Process:

1. **BOM Explosion**: For each production plan item, expand BOM to get raw materials
2. **Quantity Calculation**: Calculate total material needed across all jobs
3. **Stock Check**: Check current inventory levels
4. **Shortage Detection**: Required qty - Available qty = Shortage
5. **Supplier Scoring**: Evaluate all suppliers for each material
6. **Optimization**: Select best supplier based on price and lead time
7. **Suggestions**: Generate purchase suggestions

### Running MRP Optimization

1. Open a **Production Plan** (status should be Planned or Released)
2. Click **Run MRP** button
3. Configure settings:

**MRP Parameters**:
- **Buffer Days**: Extra days to add to material requirements (safety margin)
  - 0 days: Just-in-time, risky if delays occur
  - 7 days: One week buffer (recommended)
  - 14+ days: Large safety margin for critical items

- **Include Non-Stock Items**:
  - Yes: Include services and non-inventory items
  - No: Only physical materials

4. Click **Run MRP Optimization**
5. Wait for processing
6. Review MRP results

### Understanding MRP Results

#### APS MRP Run Summary:

- **Total Materials**: How many different materials are needed
- **Total Shortage Qty**: Total quantity to purchase
- **Total Purchase Value**: Estimated cost (if supplier prices available)
- **Run Status**: Pending → Running → Completed / Failed

#### APS MRP Result (Material Shortages):

Each shortage record shows:

- **Material Item**: What raw material is needed
- **Required Qty**: Total quantity needed
- **Available Qty**: Current stock on hand
- **Shortage Qty**: How much to buy (Required - Available)
- **Required Date**: When you need this material
- **Required For Item**: Which finished good needs this material
- **Required For Work Order**: Which job needs it (if Work Orders exist)

### Supplier Optimization Algorithm

For each material shortage, the system evaluates all available suppliers:

#### Scoring Formula:

```
Supplier Score = (0.6 × Price Score) + (0.4 × Lead Time Score)
```

**Price Score** (normalized):
- Lower price = Higher score
- Calculated as: 1 - (supplier_price / max_price_among_all_suppliers)

**Lead Time Score** (normalized):
- Shorter lead time = Higher score
- Calculated as: 1 - (supplier_lead_time / max_lead_time_among_all_suppliers)

**Weights**:
- Price: 60% weight (cost is primary concern)
- Lead Time: 40% weight (speed matters, but cost matters more)

**Example**:

Material: Steel Plate (need 100 kg)

| Supplier | Price/kg | Lead Time | Price Score | Lead Time Score | Total Score | Rank |
|----------|----------|-----------|-------------|-----------------|-------------|------|
| Supplier A | $10 | 7 days | 0.67 | 0.53 | 0.61 | 🥈 2nd |
| Supplier B | $8 | 14 days | 1.00 | 0.00 | 0.60 | 🥉 3rd |
| Supplier C | $9 | 5 days | 0.83 | 0.64 | 0.75 | 🥇 **Best** |

**Winner**: Supplier C (good balance of price and speed)

### Purchase Suggestions

After optimization, the system creates **APS Purchase Suggestion** records:

**Suggestion Details**:
- **Material Item**: What to buy
- **Purchase Qty**: How much to buy
- **Required Date**: When you need it
- **Supplier**: Optimized supplier (best score)
- **Unit Price**: Price per unit from this supplier
- **Lead Time**: Delivery time in days
- **Total Cost**: Purchase Qty × Unit Price

**Suggestion Status**:
- **Draft**: Initial suggestion
- **Approved**: Reviewed and approved by purchasing team
- **Ordered**: Purchase Order created
- **Rejected**: Suggestion declined (manual override)

**Alternative Suppliers**:
- Stored in JSON format
- Shows 2nd and 3rd best suppliers
- Use if primary supplier is unavailable

### Using Purchase Suggestions

#### Option 1: Manual Purchase Order Creation

1. Review suggestions in **APS Purchase Suggestion** list
2. For each approved suggestion:
   - Go to **Buying > Purchase Order > New**
   - Fill in supplier and items from suggestion
   - Submit the Purchase Order
3. Update suggestion status to "Ordered"

#### Option 2: Bulk Purchase Order Creation

1. Filter suggestions with status "Approved"
2. Select multiple suggestions
3. Click **Create Purchase Orders** (bulk action)
4. System creates one PO per supplier, grouping items
5. Review and submit POs in ERPNext

### MRP Best Practices

**Before Running MRP**:
- Ensure all BOMs are up-to-date
- Verify current stock levels (run stock reconciliation)
- Update supplier prices and lead times
- Set realistic buffer days based on supplier reliability

**After MRP Results**:
- Review shortages for reasonableness
- Check if optimized suppliers are actually available
- Consider strategic factors (supplier relationships, quality)
- Adjust purchase quantities for MOQ (Minimum Order Quantity)
- Consolidate orders to save on shipping

**Handling Special Cases**:

**Long Lead Time Items**:
- Increase buffer days for these materials
- Consider safety stock policies
- Place orders early in the planning cycle

**Critical Materials**:
- Don't rely solely on MRP score
- Use proven suppliers even if slightly more expensive
- Consider backup suppliers

**Seasonal Materials**:
- Account for supplier availability
- May need to order early during peak seasons

---

## Production Scheduling

### Overview

Production scheduling assigns specific start and end times to each manufacturing operation, optimizing machine usage and meeting delivery deadlines.

UIT APS uses a **three-tier hybrid scheduling system**:
- **Tier 1**: OR-Tools optimization (baseline schedule)
- **Tier 2**: Reinforcement Learning (real-time adjustments)
- **Tier 3**: Graph Neural Networks (strategic insights)

### How Scheduling Works

#### Tier 1: OR-Tools CP-SAT Solver (Baseline Optimization)

**What it does**:
- Creates the initial optimal schedule
- Solves the Job Shop Scheduling Problem (JSSP)
- Uses constraint programming to find the best solution

**Constraints enforced**:
1. **Precedence**: Operations must happen in sequence (can't paint before welding)
2. **No Overlap**: One job per machine at a time
3. **Capacity**: Respect machine availability and working hours
4. **Due Dates**: Try to meet customer delivery deadlines

**Optimization objective**:
```
Minimize: (Makespan Weight × Total Time) + (Tardiness Weight × Total Lateness)
```

- **Makespan**: Total time from start to finish of all jobs
- **Tardiness**: How late jobs are compared to due dates

**How it works**:
```
Input: Job Cards with operations
↓
Build Constraint Model:
  - Variables: Start time of each operation
  - Constraints: Precedence, capacity, no-overlap
  - Objective: Minimize makespan + tardiness
↓
CP-SAT Solver searches for optimal solution
↓
Output: Scheduled start/end times for each operation
```

**Solver Status**:
- **Optimal**: Found the best possible solution
- **Feasible**: Found a good solution but might not be absolute best
- **Infeasible**: No solution exists (constraints too tight)
- **Timeout**: Ran out of time before finding optimal (uses best found so far)

#### Tier 2: Reinforcement Learning (Real-Time Adjustments)

**What it does**:
- Adapts the schedule when disruptions occur
- Learns from experience to make better decisions
- Handles unexpected events in real-time

**Use cases**:
- Machine breakdown: Reassign operations to another machine
- Rush order: Prioritize urgent job
- Longer than expected: Resequence remaining operations
- Material delay: Reschedule dependent operations

**RL Agents available**:

**PPO (Proximal Policy Optimization)**:
- Stable and sample-efficient
- Good for general-purpose rescheduling
- Recommended for most use cases

**SAC (Soft Actor-Critic)**:
- Better exploration of alternatives
- Handles continuous action spaces
- Use for complex, multi-objective scenarios

**How RL agent works**:
```
Observe Current State:
  - Machine utilization
  - Operation progress
  - Current makespan
  - Tardiness
  - Pending operations
↓
RL Agent decides action:
  - Resequence operations
  - Change machine assignment
  - Prioritize specific job
↓
Apply action and measure reward:
  - Positive: Makespan reduced, on-time delivery
  - Negative: Increased delay, low efficiency
↓
Agent learns from outcome
```

#### Tier 3: Graph Neural Networks (Strategic Insights)

**What it does**:
- Predicts future bottlenecks before they occur
- Estimates operation durations more accurately
- Provides strategic recommendations

**GNN Predictions**:

**1. Bottleneck Prediction**:
- Identifies which operations will cause delays
- Probability score (0-1) for each operation
- Allows proactive intervention

**2. Duration Prediction**:
- Estimates actual operation time (often differs from standard time)
- Based on item type, machine, operator skill
- Improves schedule accuracy

**3. Delay Prediction**:
- Forecasts which jobs will be late
- Risk score for each job
- Early warning system

**4. Strategic Recommendations**:
- "Add capacity to CNC-01 workstation"
- "Cross-train operators for flexibility"
- "Consider outsourcing Operation XYZ"

**How GNN works**:
```
Build Operation Graph:
  - Nodes: Each operation
  - Edges: Dependencies and resource sharing
  - Node features: Duration, machine, item, status
↓
Graph Attention Network (GAT) processes graph:
  - Layer 1: Learn local patterns
  - Layer 2: Learn global dependencies
↓
Predictions:
  - Bottleneck probability per operation
  - Estimated duration per operation
  - Recommendations for capacity planning
```

### Running Scheduling

#### Basic Scheduling (Tier 1 only):

1. Open a **Production Plan** (Released status)
2. Click **Schedule Production** button
3. Configure OR-Tools parameters:

**Time Limit**:
- 60 seconds: Quick solution, may not be optimal
- 300 seconds (5 min): Recommended for most cases
- 600+ seconds: For complex scenarios with many jobs

**Objective Weights**:
- **Makespan Weight** (0-1): How much to prioritize finishing quickly
- **Tardiness Weight** (0-1): How much to prioritize on-time delivery
- Common settings:
  - Equal priority: 0.5 / 0.5
  - Speed focus: 0.7 / 0.3
  - Deadline focus: 0.3 / 0.7

**Scheduling Strategy**:
- **Forward**: Start ASAP, push deadlines if needed
- **Backward**: Start from due date, work backwards
- **Priority**: High-priority jobs first
- **EDD**: Earliest Due Date first

4. Click **Run Schedule**
5. Wait for solver to complete
6. Review scheduling results

#### Hybrid Scheduling (All Tiers):

1. Open a **Production Plan**
2. Click **Run Hybrid Scheduling**
3. Configure:

**Enable RL**: Yes/No
- Yes: Apply RL agent adjustments after OR-Tools
- No: Use only OR-Tools baseline

**RL Agent Type**: PPO or SAC (if RL enabled)

**OR-Tools Settings**: Same as basic scheduling

4. Click **Run Hybrid Schedule**

The system will:
1. Run OR-Tools for baseline (Tier 1)
2. Apply RL adjustments if enabled (Tier 2)
3. Generate GNN predictions and recommendations (Tier 3)
4. Create final schedule with all insights

### Understanding Scheduling Results

#### APS Scheduling Run Summary:

**Job Statistics**:
- **Total Job Cards**: How many jobs scheduled
- **Total Operations**: Total operation count
- **Total Machines**: Workstations used
- **Jobs On Time**: Met delivery deadline
- **Total Late Jobs**: Missed deadline

**Solver Performance**:
- **Solver Status**: Optimal, Feasible, Infeasible, Timeout
- **Solve Time**: How long it took (seconds)
- **Gap Percentage**: How far from optimal (0% = optimal)

**Schedule Metrics**:
- **Makespan (minutes)**: Total time to complete all jobs
- **Total Tardiness (minutes)**: Sum of all lateness
- **Machine Utilization (%)**: Average machine usage

**GNN Insights** (if Tier 3 ran):
- **Predicted Bottlenecks**: List of risky operations
- **Strategic Recommendations**: Actionable suggestions

#### APS Scheduling Result (Operation Details):

Each operation gets a scheduled time:

- **Operation ID**: Unique identifier
- **Job Card Name**: Link to ERPNext Job Card
- **Work Order Name**: Parent Work Order
- **Item Code**: What's being produced
- **Operation Name**: Specific operation (Cutting, Welding, etc.)
- **Machine ID**: Assigned workstation
- **Start Time**: When to start this operation
- **End Time**: When it should finish
- **Duration (mins)**: How long it takes
- **Sequence**: Order within the job
- **Is Late**: Flag if this operation contributes to job lateness
- **Tardiness (mins)**: How many minutes late (if any)
- **Is Predicted Bottleneck**: GNN prediction flag
- **Predicted Duration**: GNN's estimate vs standard time

### Using Scheduling Results

#### Update Job Cards:

1. After successful scheduling, click **Update Job Cards**
2. System pushes scheduled times to ERPNext Job Cards
3. Job Cards now show planned start/end times
4. Shop floor can see the schedule

#### Visualize Schedule (Gantt Chart):

1. Open **Scheduling Result** list
2. Click **Gantt View** button
3. See visual timeline:
   - X-axis: Time
   - Y-axis: Machines/Workstations
   - Colored blocks: Operations
   - Identify machine bottlenecks visually

#### Export Schedule:

1. Open **APS Scheduling Run**
2. Click **Export to Excel**
3. Share with production managers
4. Print for shop floor display

### Real-Time Adjustments (RL)

When disruptions occur during production:

#### Scenario: Machine Breakdown

1. Machine CNC-01 breaks down for 2 hours
2. Go to **APS Scheduling Run** (the active schedule)
3. Click **Handle Disruption**
4. Fill in disruption details:
   - **Disruption Type**: Machine Breakdown
   - **Affected Resource**: CNC-01
   - **Duration**: 120 minutes
5. Click **Get RL Recommendation**

The RL agent will:
- Analyze current state
- Evaluate options (reassign, delay, resequence)
- Recommend best action
- Show expected impact

6. Review recommendation
7. Click **Apply RL Adjustment**
8. Schedule is updated with new times

#### Scenario: Rush Order

1. Customer calls with urgent order
2. Create high-priority Job Card
3. Go to active **APS Scheduling Run**
4. Click **Handle Disruption**
5. Disruption Type: Rush Order
6. Affected Job: New urgent job
7. Get RL recommendation
8. Apply adjustment

The schedule resequences to accommodate the rush order while minimizing impact on other jobs.

### Training RL Agents

For better performance over time:

1. Go to **UIT APS > RL Agent Training**
2. Select **Scheduling Run** (historical data to learn from)
3. Select **Agent Type**: PPO or SAC
4. Set **Max Episodes**: 1000+ (more episodes = better learning)
5. Click **Train Agent**
6. Wait for training (can take hours for thorough training)
7. Trained agent is saved and used for future recommendations

**Training Tips**:
- Use historical data with various disruptions
- More diverse training data = better generalization
- Re-train periodically as production patterns change

### Bottleneck Analysis (GNN)

To identify and prevent bottlenecks:

1. Open **APS Scheduling Run**
2. Click **Predict Bottlenecks**
3. Set **Threshold**: 0.7 (70% probability to flag)
4. Review bottleneck predictions:

**For each predicted bottleneck**:
- Operation details
- Probability score
- Predicted delay (minutes)
- Recommendation

5. Take proactive action:
   - Add overtime for bottleneck workstation
   - Reassign operation to alternate machine
   - Outsource the operation
   - Adjust schedule to give more time

### Scheduling Best Practices

**Before Scheduling**:
- Ensure all Job Cards have operations defined
- Verify workstation calendars (holidays, maintenance)
- Check BOM routings are correct
- Set realistic operation time standards

**Choosing Weights**:
- Manufacturing to stock: Higher makespan weight (finish fast)
- Make-to-order: Higher tardiness weight (meet deadlines)
- Balanced: Equal weights

**Solver Time Limits**:
- Small shop (<50 operations): 60-120 seconds
- Medium shop (50-200 operations): 300 seconds
- Large shop (>200 operations): 600+ seconds
- Complex constraints: Increase time limit

**When to Use RL**:
- Frequent disruptions: Enable RL for dynamic adjustment
- Stable environment: OR-Tools alone may suffice
- Learning phase: Disable RL until agent is trained

**When to Use GNN**:
- Capacity planning: Always use for bottleneck predictions
- New product: Use duration predictions for better estimates
- Strategic decisions: Review recommendations quarterly

**Continuous Improvement**:
- Compare scheduled vs actual times
- Track on-time delivery rate
- Analyze bottleneck predictions vs actual
- Re-train RL agents with new data
- Adjust weights based on business priorities

---

## Complete Workflow Examples

### Example 1: Full Planning Cycle (Forecast to Schedule)

**Scenario**: Electronics manufacturer planning Q2 2026 production

#### Step 1: Run Demand Forecast

```
Action: Create APS Forecast History
Settings:
  - Model: Prophet (multiple seasonality)
  - Company: ABC Electronics
  - Forecast Horizon: 90 days
  - Training Period: 365 days
  - Item Group: Finished Goods
Result:
  - 45 items forecasted
  - Average MAPE: 15.2% (Good)
  - Average Confidence: 82%
```

#### Step 2: Review Forecast Results

```
Top Items by Forecast Qty:
  1. Smartphone X: 5,200 units (Upward trend, High confidence)
  2. Tablet Pro: 3,800 units (Stable, Medium confidence)
  3. Laptop Slim: 2,100 units (Downward trend, High confidence)

Action Items from AI:
  - Smartphone X: Increase safety stock by 20% due to trend
  - Tablet Pro: Maintain current inventory levels
  - Laptop Slim: Reduce orders, possibly discontinue
```

#### Step 3: Create Production Plan

```
Action: Create APS Production Plan
Settings:
  - Plan Name: "Q2 2026 Production"
  - Forecast History: FCST-RUN-2026-01-06-0001
  - Period: 2026-04-01 to 2026-06-30
  - Time Granularity: Monthly
  - Source Type: Forecast

Generated Plan Items:
  - Smartphone X (April): 1,800 units
  - Smartphone X (May): 1,700 units
  - Smartphone X (June): 1,700 units
  ... (similar for other items)

Capacity Check: OK (80% utilization)
```

#### Step 4: Run MRP Optimization

```
Action: Run MRP from Production Plan
Settings:
  - Buffer Days: 7
  - Include Non-Stock: No

Results:
  - Total Materials: 230 different components
  - Material Shortages: 85 items
  - Total Purchase Value: $420,000

Top Purchase Suggestions:
  1. LCD Display 5": 12,000 pcs from Supplier C ($18/pc, 10 days)
  2. Battery Pack Li-Ion: 8,500 pcs from Supplier A ($25/pc, 14 days)
  3. PCB Assembly: 6,200 pcs from Supplier B ($45/pc, 7 days)

Action: Approve all suggestions, create Purchase Orders
```

#### Step 5: Schedule Production

```
Action: Run Hybrid Scheduling
Settings:
  - Scheduling Strategy: Priority (urgent orders first)
  - Time Limit: 300 seconds
  - Makespan Weight: 0.4
  - Tardiness Weight: 0.6 (deadline focus)
  - Enable RL: Yes
  - RL Agent: PPO

Tier 1 (OR-Tools) Results:
  - Solver Status: Optimal
  - Makespan: 21,450 minutes (14.9 days)
  - Total Tardiness: 0 minutes
  - Machine Utilization: 82%

Tier 2 (RL) Adjustments:
  - Resequenced 12 operations
  - Improved makespan by 180 minutes
  - Final Makespan: 21,270 minutes (14.7 days)

Tier 3 (GNN) Predictions:
  - Bottlenecks: 3 operations flagged
    • Assembly Line 2 (Operation: Final Assembly)
    • Testing Station 1 (Operation: Quality Test)
  - Recommendations:
    • Add second shift to Assembly Line 2
    • Cross-train testers for Testing Station 1
```

#### Step 6: Execute Production

```
Action: Update Job Cards with schedule
Action: Release Production Plan

Shop Floor Actions:
  - Job Cards show scheduled times
  - Materials ordered arrive on time
  - Production runs according to schedule
  - Monitor for disruptions

If Disruption Occurs:
  - Use RL agent for real-time rescheduling
  - Update Job Cards with new times
```

#### Step 7: Monitor and Improve

```
Track Metrics:
  - Forecast Accuracy: Compare actual sales vs forecast
  - Schedule Adherence: Actual vs scheduled completion
  - On-Time Delivery: % of jobs completed on time
  - Material Availability: % of materials arrived on time

Continuous Improvement:
  - Re-forecast monthly with latest data
  - Adjust MRP buffer days based on supplier performance
  - Re-train RL agent with actual production data
  - Review GNN bottleneck predictions vs actual
```

**Outcome**:
- 95% on-time delivery for Q2
- $420K in optimized purchases (saved 12% vs previous quarter)
- 14.7 days total production time vs 18 days previously
- Identified and resolved 2 bottlenecks proactively

---

### Example 2: Quick Replan for Rush Order

**Scenario**: Existing production schedule, customer orders urgent batch

#### Current State:

```
Active Schedule: SCH-RUN-2026-0015
  - 25 jobs in production
  - Makespan: 8 days
  - All on-time for delivery
```

#### Disruption:

```
New Order: 500 units of Product Z
Due Date: 3 days from now
Priority: Critical (VIP customer)
```

#### Response Steps:

**Step 1: Create Job Card**
```
- Create Work Order for Product Z (500 units)
- Create Job Card with operations
- Set Priority: High
```

**Step 2: Handle Disruption with RL**
```
Action: Open SCH-RUN-2026-0015
Click: Handle Disruption
  - Disruption Type: Rush Order
  - Affected Resource: New Job Card JOB-00125
  - Required Completion: 3 days

Click: Get RL Recommendation

RL Agent Analysis:
  - Current jobs can be delayed by 1 day without penalties
  - Machine CNC-02 has capacity for rush job
  - Recommended sequence: Insert Job-00125 at position 3
  - Expected impact: +1 day to 2 non-critical jobs
```

**Step 3: Apply Adjustment**
```
Click: Apply RL Adjustment

New Schedule:
  - Rush job starts immediately on CNC-02
  - 2 jobs delayed by 1 day (still on-time)
  - Rush job completes in 2.5 days
  - Customer deadline met with 0.5 day buffer
```

**Step 4: Update Shop Floor**
```
Click: Update Job Cards
Notify: Production team of new priority job
Monitor: Progress on rush order
```

**Outcome**:
- Rush order delivered in 2.5 days (0.5 days early)
- Only 2 jobs affected, still met their deadlines
- Customer satisfaction maintained
- Minimal disruption to overall schedule

---

### Example 3: Bottleneck Resolution

**Scenario**: Recurring late deliveries, need to identify root cause

#### Step 1: Run Scheduling with GNN

```
Action: Schedule next month's production with Tier 3 enabled
Settings:
  - Enable all three tiers
  - Bottleneck threshold: 0.6 (60% probability)
```

#### Step 2: Analyze Bottleneck Predictions

```
GNN Predictions:
  - Operation: Welding on Welder-01
    • Probability: 0.85 (High risk)
    • Predicted Delay: 3.5 hours
    • Affected Jobs: 8 jobs

  - Operation: Painting on Paint-Booth-A
    • Probability: 0.72 (Medium-High risk)
    • Predicted Delay: 2.1 hours
    • Affected Jobs: 5 jobs
```

#### Step 3: Review Recommendations

```
Strategic Recommendations from GNN:

1. Welder-01 Bottleneck:
   "Add capacity to Welder-01 workstation"
   Options:
   - Add second welder machine ($50K investment)
   - Outsource welding operations ($15/unit)
   - Add overtime shift (1.5x labor cost)

2. Paint-Booth-A Bottleneck:
   "Cross-train operators for flexibility"
   Options:
   - Train 2 additional painters ($2K training cost)
   - Rent second paint booth ($5K/month)
   - Batch painting operations for efficiency
```

#### Step 4: Implement Solutions

**Short-term (Immediate)**:
```
- Add overtime shift to Welder-01 (2 hours/day)
- Cross-train 2 operators for painting
- Cost: ~$3K/month
```

**Long-term (Strategic)**:
```
- Purchase second welder machine
- Install additional paint booth
- Hire dedicated welder
- Cost: $70K capex + $4K/month opex
```

#### Step 5: Measure Impact

**Before (Previous Month)**:
```
- On-time delivery: 78%
- Average tardiness: 4.2 hours
- Bottleneck delays: 15 instances
```

**After (Next Month)**:
```
- On-time delivery: 94% (+16%)
- Average tardiness: 0.8 hours (-81%)
- Bottleneck delays: 3 instances (-80%)
```

**ROI Calculation**:
```
Investment: $70K + ($4K × 12) = $118K/year
Savings:
  - Reduced late penalties: $25K/year
  - Increased throughput: $180K/year revenue
  - Improved customer retention: $50K/year

Net Benefit: $255K - $118K = $137K/year
Payback Period: 6.2 months
```

---

## Troubleshooting

### Forecasting Issues

#### Problem: "No sales order data found"

**Cause**: No historical sales orders for the selected filters

**Solutions**:
1. Check date range: Need at least 30-60 days of data
2. Verify filters: Remove item/warehouse filters to test
3. Check Sales Order status: System only uses Submitted orders
4. Verify item codes: Ensure items exist in sales orders

#### Problem: "Forecast accuracy is very low (<50% MAPE)"

**Cause**: Insufficient or erratic data, wrong model selection

**Solutions**:
1. Increase training period (try 365+ days)
2. Try different model:
   - Erratic data → Try Prophet
   - Seasonal data → Try ARIMA
   - Stable trend → Try Linear Regression
3. Clean data: Remove outliers or one-time bulk orders
4. Check for data quality issues (duplicates, wrong quantities)

#### Problem: "AI explanation generation failed"

**Cause**: OpenAI API issues or configuration problems

**Solutions**:
1. Check ChatGPT Settings:
   - Valid API key
   - Sufficient API credits
   - Model selected (gpt-4 or gpt-3.5-turbo)
2. Click "Retry AI Explanations" button
3. Check error log for specific API error message
4. Verify internet connectivity from server

#### Problem: "Confidence scores are very low"

**Cause**: High variability in historical data

**Solutions**:
1. Normal for new products (little history)
2. Review forecast explanation for context
3. Consider using upper bound for safety stock
4. Combine with sales team judgment
5. Re-forecast with more data over time

---

### Production Planning Issues

#### Problem: "No BOM found for item"

**Cause**: Item doesn't have a default BOM configured

**Solutions**:
1. Go to ERPNext > BOM > Create BOM for the item
2. Set BOM as default (Is Default = Yes)
3. Or manually select BOM in production plan item

#### Problem: "Capacity status shows Overloaded"

**Cause**: Workstation capacity insufficient for planned production

**Solutions**:
1. Extend timeline (increase plan period)
2. Reduce planned quantities
3. Add shifts/overtime to workstations
4. Upgrade workstation capacity in ERPNext
5. Consider outsourcing some operations

#### Problem: "Production plan items not generating"

**Cause**: Forecast results have issues or no data

**Solutions**:
1. Check forecast history status (must be Complete)
2. Verify forecast results exist for selected period
3. Ensure forecast items have BOMs
4. Check filters: Period dates must overlap forecast dates

---

### MRP Issues

#### Problem: "No material shortages found, but I know we need materials"

**Cause**: Stock levels not updated or BOM issues

**Solutions**:
1. Run Stock Reconciliation in ERPNext
2. Check BOM for production items (must have raw materials)
3. Verify warehouse selection in production plan
4. Check if "Available Qty" is correct in Bin records

#### Problem: "Supplier optimization shows 'No suppliers found'"

**Cause**: No Item Supplier records or Item Price records

**Solutions**:
1. Go to ERPNext > Buying > Item Supplier
2. Create supplier links for each material
3. Add prices in Item Price or Supplier Quotation
4. Re-run MRP optimization

#### Problem: "MRP run is very slow"

**Cause**: Large number of items or complex BOMs

**Solutions**:
1. Plan by item group instead of all items at once
2. Simplify multi-level BOMs if possible
3. Run MRP during off-peak hours
4. Consider server hardware upgrade for large operations

#### Problem: "Suggested supplier doesn't match my preference"

**Cause**: Optimization based purely on price/lead time

**Solutions**:
1. Review alternative suppliers in suggestion
2. Manually override supplier selection
3. Adjust Item Price to favor preferred supplier
4. Update lead times to reflect reality
5. Use "Rejected" status and create manual PO

---

### Scheduling Issues

#### Problem: "Solver status shows Infeasible"

**Cause**: Constraints are too tight, no valid solution exists

**Solutions**:
1. Check due dates: May be impossible to meet
2. Review workstation capacity: May need more capacity
3. Extend deadline constraints
4. Remove or relax some constraints
5. Check if operations have valid workstations assigned

#### Problem: "Solver timeout, only Feasible solution"

**Cause**: Problem is very complex, needs more time

**Solutions**:
1. Increase time limit (try 600-1800 seconds)
2. Adjust weights to guide solver faster
3. Reduce problem size (schedule fewer jobs at once)
4. Simplify operation sequences if possible
5. Feasible solution is still usable, just not proven optimal

#### Problem: "Schedule has very low machine utilization"

**Cause**: Too much capacity or inefficient sequence

**Solutions**:
1. Increase makespan weight (tighten schedule)
2. Check for large gaps in workstation calendars
3. Review operation time standards (may be overestimated)
4. Consider batch sizing to reduce setup times

#### Problem: "Many jobs showing late even in optimal schedule"

**Cause**: Due dates are unrealistic given capacity

**Solutions**:
1. Extend due dates (negotiate with customers)
2. Add capacity (overtime, extra machines)
3. Outsource some operations
4. Prioritize critical jobs (adjust strategy)
5. Review time standards (may be underestimated)

#### Problem: "RL adjustment makes schedule worse"

**Cause**: RL agent not sufficiently trained

**Solutions**:
1. Train RL agent with more historical data
2. Increase training episodes (1000+ recommended)
3. Use OR-Tools only until agent is trained
4. Review RL reward function parameters
5. Try different agent type (PPO vs SAC)

#### Problem: "GNN bottleneck predictions are inaccurate"

**Cause**: Model not trained on your specific production patterns

**Solutions**:
1. Collect more historical scheduling data
2. Re-train GNN model with actual results
3. Adjust prediction threshold (lower for more warnings)
4. Use predictions as guidance, not absolute truth
5. Validate predictions against domain knowledge

---

## Best Practices

### Data Management

**Keep Master Data Clean**:
- Regular audits of item master data
- Archive obsolete items instead of deleting
- Maintain accurate BOMs and routings
- Update supplier prices quarterly
- Verify workstation capacities regularly

**Historical Data Quality**:
- Clean up test sales orders
- Ensure proper transaction dates
- Reconcile stock levels monthly
- Document any bulk or one-time orders
- Keep 12+ months of history for forecasting

**Documentation**:
- Document BOM changes with reasons
- Log workstation downtime and maintenance
- Track forecast vs actual regularly
- Record scheduling disruptions and responses
- Maintain supplier performance metrics

### Planning Cycles

**Recommended Frequencies**:

- **Forecasting**: Monthly for most items, weekly for fast-moving
- **Production Planning**: Monthly or quarterly depending on lead times
- **MRP**: Run with each production plan update
- **Scheduling**: Weekly or bi-weekly, daily for high-mix environments
- **RL Training**: Quarterly with accumulated data
- **GNN Model Update**: Every 6 months or when patterns change

**Planning Horizon**:

- **Short-term** (1-4 weeks): Detailed scheduling, firm orders
- **Medium-term** (1-3 months): Production planning, MRP
- **Long-term** (3-12 months): Demand forecasting, capacity planning

### Performance Optimization

**For Large Datasets**:
- Forecast by item group, not all at once
- Schedule in batches (weekly buckets)
- Use filters to reduce problem size
- Run heavy computations during off-peak hours
- Consider dedicated worker processes for ML tasks

**For Accuracy**:
- Use at least 6-12 months of training data
- Compare models before selecting one
- Validate forecasts against sales team input
- Track actual vs predicted metrics
- Adjust parameters based on performance

**For Speed**:
- Start with shorter time limits and increase if needed
- Use cached results when data hasn't changed
- Pre-train RL agents during implementation
- Optimize database queries for large BOMs

### Change Management

**When Implementing UIT APS**:

1. **Phase 1: Pilot** (1-2 months)
   - Select one product line or item group
   - Run parallel with existing process
   - Compare results and build confidence
   - Train key users

2. **Phase 2: Expansion** (2-3 months)
   - Expand to additional product lines
   - Integrate with existing ERP workflows
   - Establish review processes
   - Train wider user base

3. **Phase 3: Optimization** (3-6 months)
   - Fine-tune model parameters
   - Train RL agents on real data
   - Establish KPIs and dashboards
   - Document standard operating procedures

4. **Phase 4: Continuous Improvement** (Ongoing)
   - Monthly review of forecast accuracy
   - Quarterly model retraining
   - Annual process audits
   - Ongoing user training

**User Adoption**:
- Involve planners early in design decisions
- Provide clear training materials
- Show concrete benefits with metrics
- Start simple, add complexity gradually
- Celebrate wins and learn from misses

### Integration with ERPNext

**Workflow Integration**:

```
UIT APS Forecast → APS Production Plan → ERPNext Work Orders →
ERPNext Job Cards (scheduled by APS) → Production → Stock Entry →
Delivery → Actual vs Forecast Analysis
```

**Best Practices**:
- Keep ERPNext master data as source of truth
- Use APS for planning, ERPNext for execution
- Sync regularly (don't let data drift)
- Use ERPNext roles and permissions for APS access
- Leverage ERPNext reports for combined analytics

**Data Flow**:
- **From ERPNext to APS**: Items, BOMs, Sales Orders, Stock Levels, Suppliers
- **From APS to ERPNext**: Scheduled times in Job Cards, Purchase suggestions for POs
- **Bidirectional**: Production plan status, work order updates

### Security and Access Control

**Role-Based Access**:

- **System Manager**: Full access, configuration
- **APS Manager**: Run forecasts, create plans, manage schedules
- **APS User**: View forecasts and schedules, limited editing
- **Manufacturing User**: View schedules only
- **Purchasing User**: View MRP results and purchase suggestions

**Sensitive Data**:
- Protect supplier pricing data
- Control access to forecast results (competitive info)
- Encrypt OpenAI API keys
- Audit trail for plan changes
- Backup scheduling data regularly

### Monitoring and KPIs

**Key Metrics to Track**:

**Forecast Performance**:
- MAPE (Mean Absolute Percentage Error): Target <20%
- Forecast bias: Should be near 0% (not consistently over/under)
- Forecast vs actual by item: Identify problem items
- Confidence score trend: Should improve over time

**Planning Performance**:
- Plan fulfillment rate: % of plan completed
- Plan change frequency: How often plans are revised
- Capacity utilization: Target 75-85% (not too high or low)

**MRP Performance**:
- Material availability: % of materials arriving on time
- Purchase cost variance: Actual vs suggested supplier
- Shortage incidents: Count of stockouts
- Supplier optimization savings: $ saved by optimal selection

**Scheduling Performance**:
- On-time delivery rate: Target >95%
- Schedule adherence: Actual vs scheduled completion
- Average tardiness: Minutes late per job
- Machine utilization: Target 75-85%
- Makespan reduction: vs previous scheduling method

**RL Agent Performance**:
- Adjustment success rate: % of RL adjustments that improved schedule
- Response time: How fast RL suggests solution
- Learning curve: Improvement over training episodes

**GNN Prediction Performance**:
- Bottleneck prediction accuracy: % correctly identified
- Duration prediction error: Actual vs predicted operation time
- False positive rate: Bottlenecks predicted but didn't occur

**Dashboard Recommendations**:
- Daily: Schedule adherence, machine utilization
- Weekly: Forecast vs actual sales, on-time delivery
- Monthly: Forecast accuracy, plan fulfillment, cost savings
- Quarterly: Model performance trends, RL agent improvements

---

## Conclusion

UIT APS provides a comprehensive, AI-powered solution for manufacturing planning and scheduling. By following this functional guide, you can:

- **Forecast demand accurately** using the right ML model for your data
- **Plan production efficiently** based on reliable forecasts
- **Optimize material procurement** with intelligent supplier selection
- **Schedule operations optimally** using hybrid AI/OR techniques
- **Adapt in real-time** when disruptions occur
- **Improve continuously** with data-driven insights

### Getting Help

**Documentation**:
- Architecture Guide: Technical system details
- API Reference: Integration and automation
- This Functional Guide: How to use the system

**Support**:
- Check error logs in each DocType for specific issues
- Review forecast explanations for insights
- Use GNN recommendations for strategic guidance
- Consult ERPNext community for base ERP questions

**Training**:
- Hands-on practice with pilot item group
- Review example workflows in this guide
- Experiment with model parameters
- Start simple, add advanced features gradually

### Next Steps

1. **Set up master data** in ERPNext
2. **Run your first forecast** on a small item group
3. **Review forecast results** and compare models
4. **Create a production plan** from the forecast
5. **Run MRP optimization** to see purchase suggestions
6. **Try basic scheduling** with OR-Tools
7. **Gradually enable** RL and GNN as you gain confidence
8. **Measure results** against your current process
9. **Iterate and improve** based on data

Success with UIT APS comes from consistent use, regular review of results, and continuous refinement of your planning process. Start simple, measure everything, and let the data guide your improvements.

---

**Document Version**: 1.0
**Last Updated**: 2026-01-06
**For UIT APS Version**: 1.0+
**Maintained by**: thanhnc
