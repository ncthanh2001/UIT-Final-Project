# UIT APS Demo Scripts - Wood Manufacturing

Complete demonstration scripts for the UIT APS (Advanced Planning & Scheduling) system using a wood furniture manufacturing business scenario.

## 📋 Overview

These demo scripts create a complete, realistic manufacturing environment for **Bear Manufacturing**, a premium wood furniture company. The scripts demonstrate all core features of the UIT APS system:

- **AI-Powered Demand Forecasting** (ARIMA, Linear Regression, Prophet)
- **Intelligent Production Planning**
- **MRP Optimization** with multi-criteria supplier selection
- **Hybrid Production Scheduling** (OR-Tools + RL + GNN)
- **Real-time Schedule Adjustments**

## 🏭 Business Context

**Company:** Bear Manufacturing
**Industry:** Premium Wood Furniture Manufacturing
**Products:** 13 finished furniture items including desks, chairs, wardrobes, and beds
**Materials:** Oak, Pine, Ebony wood, MDF, hardware, finishes
**Customers:** Export companies, distributors, contractors, wholesale, retail

## 📁 Script Files

### Script 01: Master Data Setup
**File:** `01_master_data_wood_manufacturing.py`

Creates all foundational master data:
- ✅ Company structure
- ✅ Warehouse hierarchy (7 warehouses)
- ✅ Item groups (3-level hierarchy)
- ✅ Items (19 raw materials, 8 sub-assemblies, 13 finished products)
- ✅ Suppliers (5 vendors)
- ✅ Customers (11 across 5 segments)
- ✅ Operations (12 manufacturing operations)
- ✅ Employees (8 workers)
- ✅ BOMs (Bill of Materials with operations)

**Execution Time:** ~2-3 minutes
**Records Created:** ~70+ master records

### Script 02: Transactional Data
**File:** `02_sales_production_data.py`

Creates realistic transactional history:
- ✅ Historical Sales Orders (configurable months)
- ✅ Production Plans
- ✅ Work Orders with operations
- ✅ Job Cards with time logs
- ✅ Stock Entries for raw materials

**Execution Time:** ~3-5 minutes (default: 3 months)
**Records Created:** ~50-100+ transactions

### Script 03: APS Workflow Demo
**File:** `03_aps_workflow_demo.py`

Demonstrates complete APS workflow:
1. **Demand Forecasting** - Run 3 ML models (ARIMA, LR, Prophet)
2. **Production Planning** - Generate optimal production plan
3. **MRP Optimization** - Calculate material requirements
4. **Production Scheduling** - 3-tier hybrid scheduling
5. **Work Order Generation** - Create executable work orders

**Execution Time:** ~2-4 minutes
**Demonstrates:** All core APS features

## 🚀 Quick Start

### Method 1: Individual Scripts

```bash
# Step 1: Create master data
bench --site [your-site] console
```

```python
exec(open('apps/uit_aps/uit_aps/demo_scripts/01_master_data_wood_manufacturing.py').read())
```

```bash
# Step 2: Create transactional data
bench --site [your-site] console
```

```python
exec(open('apps/uit_aps/uit_aps/demo_scripts/02_sales_production_data.py').read())
```

```bash
# Step 3: Run APS workflow
bench --site [your-site] console
```

```python
exec(open('apps/uit_aps/uit_aps/demo_scripts/03_aps_workflow_demo.py').read())
```

### Method 2: Direct Execution

```bash
# Script 01
bench --site [your-site] execute apps.uit_aps.uit_aps.demo_scripts.01_master_data_wood_manufacturing.create_all_master_data

# Script 02 (with custom parameters)
bench --site [your-site] execute apps.uit_aps.uit_aps.demo_scripts.02_sales_production_data.create_transactional_data --kwargs "{'months': 6, 'orders_per_month': 15}"

# Script 03
bench --site [your-site] execute apps.uit_aps.uit_aps.demo_scripts.03_aps_workflow_demo.run_complete_aps_workflow
```

### Method 3: All-in-One Setup

```python
# In bench console
exec(open('apps/uit_aps/uit_aps/demo_scripts/03_aps_workflow_demo.py').read())
quick_start()  # Runs all 3 scripts in sequence
```

## ⚙️ Configuration Options

### Script 01 - Master Data
Edit configuration section at the top of the file:

```python
COMPANY_CONFIG = {
    "name": "Bear Manufacturing",
    "abbr": "BM",
    "country": "Vietnam",
    "default_currency": "VND"
}

# Modify product lists, suppliers, customers as needed
```

### Script 02 - Transactional Data
Parameters:

```python
create_transactional_data(
    months=3,              # Historical data months
    orders_per_month=12,   # Sales orders per month
    work_orders=10,        # Number of work orders
    job_cards=5,           # Job cards to create
    stock_entries=10       # Stock receipt entries
)
```

### Script 03 - APS Workflow
Configuration options:

```python
FORECAST_CONFIG = {
    "forecast_months": 3,
    "models": ["arima", "linear_regression", "prophet"],
    "use_ai_explanation": False  # Requires ChatGPT API
}

SCHEDULING_CONFIG = {
    "algorithm": "hybrid",  # ortools, rl, gnn, hybrid
    "objective": "minimize_makespan",
    "enable_realtime_adjustment": True
}
```

## 📊 Sample Data Details

### Products (13 Finished Items)

| Code | Product Name | Price (VND) | Type |
|------|--------------|-------------|------|
| TP-BLV-001 | Ban Lam Viec Go Soi 120x60 | 3,700,000 | Desk |
| TP-BLV-002 | Ban Lam Viec Go Thong 100x50 | 1,600,000 | Desk |
| TP-BAN-001 | Ban An Go Cam 6 Cho | 5,560,000 | Table |
| TP-GVP-001 | Ghe Van Phong Go Soi | 1,590,000 | Chair |
| TP-GAN-001 | Ghe An Go Cam | 1,430,000 | Chair |
| TP-GBT-001 | Ghe Bar Go Thong | 840,000 | Chair |
| TP-TQA-001 | Tu Quan Ao 2 Canh Go Soi | 10,700,000 | Wardrobe |
| TP-TQA-002 | Tu Quan Ao 3 Canh MDF | 9,370,000 | Wardrobe |
| TP-THS-001 | Tu Ho So Van Phong | 4,570,000 | Cabinet |
| TP-GN16-001 | Giuong Ngu Go Soi 1m6 | 9,160,000 | Bed |
| TP-GN18-001 | Giuong Ngu Go Soi 1m8 | 10,600,000 | Bed |
| TP-GN12-001 | Giuong Don Go Thong 1m2 | 2,770,000 | Bed |
| TP-GT2T-001 | Giuong Tang 2 Tang Go Thong | 5,980,000 | Bed |

### Raw Materials (19 Items)

- **Wood Types:** Oak, Pine, Ebony, MDF, Plywood
- **Hardware:** Screws, hinges, drawer slides, handles
- **Chemicals:** Wood glue, primer, topcoat, wood oil

### Workstations (25 from CSV)

Production floor organized into zones:
- **Khu Che Bien Go:** Panel saws, planers (3 machines)
- **Khu Gia Cong CNC:** CNC mills, routers, drills (4 machines)
- **Khu Cha Nham:** Sanding machines (3 types)
- **Khu Lap Rap:** Assembly benches (4 stations)
- **Khu Son:** Spray booths (2 units)
- **Khu Say:** Drying rooms (2 rooms)
- **Khu QC va Dong Goi:** QC benches, packing stations (4 stations)

### Customer Segments

1. **Xuat Khau (Export):** IKEA Vietnam, Wayfair, Home24
2. **Dai Ly (Distributors):** Hoa Phat, Xuan Hoa, Showrooms
3. **Nha Thau (Contractors):** Construction companies
4. **Khach Si (Wholesale):** Wood trading companies
5. **Khach Le (Retail):** Individual customers

## 🔍 What Gets Created

### After Script 01:
- ✅ Complete company setup with chart of accounts
- ✅ 7-level warehouse structure
- ✅ 40 items across all categories
- ✅ 5 suppliers with contact info
- ✅ 11 customers in 5 segments
- ✅ 8 employees in various departments
- ✅ 12 operations linked to workstations
- ✅ 3 BOMs with full operation routing

### After Script 02:
- ✅ 36+ sales orders (3 months × 12 orders/month)
- ✅ 5 production plans from sales orders
- ✅ 10 work orders with operations
- ✅ Job cards with employee time logs
- ✅ 10 stock entries for raw materials
- ✅ Realistic production history for ML training

### After Script 03:
- ✅ 1 APS Forecast History with 3 model results
- ✅ 1 APS Production Plan optimized
- ✅ 1 APS MRP Run with material requirements
- ✅ 1 APS Scheduling Run with optimized schedule
- ✅ 3 new Work Orders from schedule
- ✅ Complete audit trail of APS workflow

## 🎯 Use Cases Demonstrated

### 1. Demand Forecasting
- Multiple ML models comparison
- Seasonal pattern detection
- Forecast accuracy metrics
- AI explanations (optional)

### 2. Production Planning
- Forecast-driven planning
- Capacity-aware scheduling
- Safety stock calculations
- Multi-level BOM explosion

### 3. MRP Optimization
- Material requirement calculation
- Stock availability check
- Multi-criteria supplier selection
- Lead time optimization

### 4. Production Scheduling
- **OR-Tools:** Constraint programming (JSSP)
- **RL Agent:** Real-time adaptive scheduling
- **GNN:** Bottleneck prediction and critical path analysis
- **Hybrid:** Combined approach for best results

### 5. Work Order Management
- Automatic WO generation from schedule
- Operation sequencing
- Workstation assignment
- Time estimation

## 🧪 Testing Scenarios

### Scenario 1: Basic Workflow
1. Run scripts 01 → 02 → 03 in order
2. Review forecast accuracy in Forecast History
3. Check production plan feasibility
4. Analyze MRP suggestions
5. View optimized schedule

### Scenario 2: Demand Spike
1. Run script 02 with high order volume
2. Run forecasting to detect trend
3. See how APS adjusts production plan
4. Check if MRP identifies material shortages

### Scenario 3: Capacity Constraint
1. Reduce workstation availability (set to "Off")
2. Run scheduling
3. Observe how system routes around bottlenecks
4. See GNN predictions for delays

### Scenario 4: Real-time Adjustment
1. Create initial schedule
2. Simulate machine breakdown
3. Use RL agent for rescheduling
4. Compare before/after makespan

## 📈 Performance Benchmarks

Typical execution times (on standard hardware):

| Script | Records | Time | Memory |
|--------|---------|------|--------|
| Script 01 | ~70 | 2-3 min | Low |
| Script 02 | ~100 | 3-5 min | Medium |
| Script 03 | ~20 | 2-4 min | High (ML models) |
| **Total** | **~190** | **7-12 min** | - |

## 🔧 Troubleshooting

### Common Issues

**Issue:** "Company not found"
**Solution:** Run script 01 first

**Issue:** "Item does not exist"
**Solution:** Ensure script 01 completed successfully

**Issue:** "Workstation not found"
**Solution:** Import Workstation.csv before running scripts

**Issue:** "Insufficient permissions"
**Solution:** Run in bench console or as Administrator

**Issue:** "No historical data for forecast"
**Solution:** Run script 02 first, ensure at least 3 months of sales orders

### Resetting Demo Data

To completely reset and start over:

```sql
-- WARNING: This deletes all demo data!
-- Run in bench mariadb

DELETE FROM `tabSales Order` WHERE company = 'Bear Manufacturing';
DELETE FROM `tabWork Order` WHERE company = 'Bear Manufacturing';
DELETE FROM `tabJob Card` WHERE company = 'Bear Manufacturing';
DELETE FROM `tabProduction Plan` WHERE company = 'Bear Manufacturing';
DELETE FROM `tabStock Entry` WHERE company = 'Bear Manufacturing';
DELETE FROM `tabAPS Forecast History` WHERE company = 'Bear Manufacturing';
DELETE FROM `tabAPS Production Plan` WHERE company = 'Bear Manufacturing';
DELETE FROM `tabAPS MRP Run` WHERE company = 'Bear Manufacturing';
DELETE FROM `tabAPS Scheduling Run` WHERE company = 'Bear Manufacturing';

-- Then run scripts again
```

## 📚 Next Steps

After running the demo scripts:

1. **Explore the UI:**
   - Go to UIT APS workspace
   - Review forecast charts and metrics
   - Analyze production schedules
   - Check MRP recommendations

2. **Modify Parameters:**
   - Edit forecast horizon
   - Change scheduling algorithm
   - Adjust safety stock levels
   - Test different supplier criteria

3. **Create Custom Scenarios:**
   - Add new products and BOMs
   - Simulate demand variations
   - Test capacity constraints
   - Experiment with RL training

4. **Integration Testing:**
   - Connect to real ERPNext data
   - Link with procurement workflow
   - Integrate with shopfloor system
   - Set up automated forecast runs

## 🤝 Contributing

To add more demo scenarios:

1. Create new script file in `demo_scripts/` folder
2. Follow naming convention: `##_scenario_name.py`
3. Add configuration section at top
4. Include logging and error handling
5. Update this README with usage instructions

## 📝 License

These demo scripts are part of the UIT APS application.
See main application license for details.

## 📧 Support

For issues or questions:
- Check FUNCTIONAL_GUIDE.md for feature documentation
- Review ARCHITECTURE.md for technical details
- See individual script docstrings for specific usage

---

**Version:** 1.0.0
**Last Updated:** 2025-01-06
**Compatible with:** ERPNext v15+, Frappe v15+
