# 🚀 UIT APS Demo - Quick Start Guide

## 5-Minute Setup

### Prerequisites
```bash
# Ensure UIT APS app is installed
bench --site [your-site] list-apps
# You should see: uit_aps

# Ensure you have Workstation.csv in the project root
ls /home/thanhnc/frappe_uit/Workstation.csv
```

### Step 1: Import Workstations (One-time)
```bash
# In Frappe UI
# Go to: Workstation List > Menu > Import
# Upload: /home/thanhnc/frappe_uit/Workstation.csv
# Click: Start Import
```

### Step 2: Run All Demo Scripts

```bash
bench --site [your-site] console
```

Then paste this code:

```python
# One-command complete setup
exec(open('apps/uit_aps/uit_aps/demo_scripts/03_aps_workflow_demo.py').read())
quick_start()
```

⏱️ **Total time:** 10-15 minutes

---

## ✅ What You'll Get

After completion, you'll have:

- ✅ Complete company: Bear Manufacturing
- ✅ 40 items (raw materials → finished products)
- ✅ 11 customers across 5 segments
- ✅ 5 suppliers
- ✅ 8 employees
- ✅ 25 workstations (from CSV)
- ✅ 3 BOMs with full routing
- ✅ 36+ sales orders (3 months history)
- ✅ 10 work orders with operations
- ✅ Complete APS workflow demonstration

---

## 🎯 Verify Setup

### Check Master Data
```sql
-- In bench mariadb
SELECT COUNT(*) FROM `tabItem` WHERE item_group LIKE '%Go Nguyen Lieu%';
-- Should return: 5 (wood types)

SELECT COUNT(*) FROM `tabSales Order` WHERE company = 'Bear Manufacturing';
-- Should return: 36+ (sales orders)

SELECT COUNT(*) FROM `tabWorkstation`;
-- Should return: 25 (from CSV)
```

### Check Workflow Results
```python
# In bench console
import frappe

# Check forecast
forecasts = frappe.get_all("APS Forecast History", limit=1)
print(f"Forecasts created: {len(forecasts)}")

# Check production plans
plans = frappe.get_all("APS Production Plan", limit=1)
print(f"Production plans: {len(plans)}")

# Check work orders
wos = frappe.get_all("Work Order", {"company": "Bear Manufacturing"}, limit=5)
print(f"Work orders: {len(wos)}")
```

---

## 📊 Explore the Results

### 1. View Demand Forecast
```
UIT APS → APS Forecast History → [Latest Record]
```
- See 3 ML model predictions
- Compare forecasts for 5 items
- View confidence intervals

### 2. Review Production Plan
```
UIT APS → APS Production Plan → [Latest Record]
```
- Planned quantities per item
- Production timeline
- BOM requirements

### 3. Check MRP Results
```
UIT APS → APS MRP Run → [Latest Record]
```
- Material requirements
- Stock availability
- Purchase suggestions

### 4. Analyze Schedule
```
UIT APS → APS Scheduling Run → [Latest Record]
```
- Operation sequences
- Workstation assignments
- Makespan optimization

### 5. View Work Orders
```
Manufacturing → Work Order → [Filter: Bear Manufacturing]
```
- Scheduled start/end times
- Operations with workstations
- Material requirements

---

## 🔄 Alternative: Step-by-Step Setup

If you prefer to run each script separately:

### Script 1: Master Data (2-3 min)
```python
exec(open('apps/uit_aps/uit_aps/demo_scripts/01_master_data_wood_manufacturing.py').read())
```

### Script 2: Transactional Data (3-5 min)
```python
exec(open('apps/uit_aps/uit_aps/demo_scripts/02_sales_production_data.py').read())
```

### Script 3: APS Workflow (2-4 min)
```python
exec(open('apps/uit_aps/uit_aps/demo_scripts/03_aps_workflow_demo.py').read())
```

---

## 🎨 Customization Options

### More Historical Data
```python
exec(open('apps/uit_aps/uit_aps/demo_scripts/02_sales_production_data.py').read())
create_transactional_data(months=6, orders_per_month=20)
```

### Different Scheduling Algorithm
Edit `03_aps_workflow_demo.py`:
```python
SCHEDULING_CONFIG = {
    "algorithm": "ortools",  # or "rl", "gnn", "hybrid"
    "objective": "minimize_tardiness",
    "enable_realtime_adjustment": True
}
```

### Add More Products
Edit `01_master_data_wood_manufacturing.py`:
```python
FINISHED_PRODUCTS = [
    # Add your custom products here
    {"code": "TP-XXX-001", "name": "Your Product", "group": "...", "price": ...},
]
```

---

## 🧹 Clean Up Demo Data

### Option 1: Delete Company
```python
# This will delete ALL related records
import frappe
company = frappe.get_doc("Company", "Bear Manufacturing")
company.delete()
frappe.db.commit()
```

### Option 2: Selective Deletion
```sql
-- Keep master data, delete transactions only
DELETE FROM `tabSales Order` WHERE company = 'Bear Manufacturing';
DELETE FROM `tabWork Order` WHERE company = 'Bear Manufacturing';
DELETE FROM `tabAPS Forecast History` WHERE company = 'Bear Manufacturing';
```

---

## 🐛 Troubleshooting

### Problem: Scripts fail with "Item not found"
**Solution:**
```python
# Check if master data was created
import frappe
items = frappe.get_all("Item", {"item_code": "TP-BLV-001"})
if not items:
    print("Run script 01 first!")
```

### Problem: "No sales orders found"
**Solution:**
```python
# Check sales order count
import frappe
count = frappe.db.count("Sales Order", {"company": "Bear Manufacturing"})
print(f"Sales Orders: {count}")
# If < 10, run script 02
```

### Problem: "Workstation not found in operation"
**Solution:**
```bash
# Import workstations CSV first
# UI: Workstation List > Import > Upload Workstation.csv
```

### Problem: Forecast fails with "Insufficient data"
**Solution:**
```python
# Need at least 3 months of sales history
# Run script 02 with more months:
exec(open('apps/uit_aps/uit_aps/demo_scripts/02_sales_production_data.py').read())
create_transactional_data(months=6)
```

---

## 📖 Next Steps

1. **Read Full Documentation:**
   - `README.md` - Complete guide
   - `FUNCTIONAL_GUIDE.md` - Feature documentation
   - `ARCHITECTURE.md` - Technical details

2. **Try Advanced Features:**
   - Configure ChatGPT for AI explanations
   - Train custom RL models
   - Set up automated forecast scheduling

3. **Customize for Your Business:**
   - Replace products with your items
   - Adjust BOMs and operations
   - Configure your workstations

4. **Integration:**
   - Connect to real sales data
   - Link with procurement
   - Set up shopfloor integration

---

## 💡 Tips

- **Performance:** Scripts run faster with fewer records initially
- **Data Quality:** More historical data = better forecasts
- **Testing:** Use separate test site for experiments
- **Backups:** Take database backup before running on production

---

## 📞 Need Help?

- Check script docstrings for detailed usage
- Review error messages in bench console
- See main README.md for troubleshooting guide

---

**Happy Scheduling! 🎉**

Version: 1.0.0
Last Updated: 2025-01-06
