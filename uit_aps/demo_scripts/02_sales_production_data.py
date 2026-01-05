"""
Demo Script 2: Sales & Production Transactional Data
====================================================

This script creates realistic transactional data for wood furniture manufacturing:
- Historical Sales Orders (3-6 months back)
- Production Plans
- Work Orders with operations
- Job Cards with time logs
- Stock Entries
- Delivery Notes and Sales Invoices

Usage:
------
Method 1 - Bench Console:
  bench --site [sitename] console
  exec(open('apps/uit_aps/uit_aps/demo_scripts/02_sales_production_data.py').read())

Method 2 - Direct execution:
  bench --site [sitename] execute apps.uit_aps.uit_aps.demo_scripts.02_sales_production_data.create_transactional_data --kwargs "{'months': 3, 'orders_per_month': 12}"

Prerequisites:
--------------
- Run script 01_master_data_wood_manufacturing.py first
- Ensure Workstations are imported from CSV

Created for: UIT APS (Advanced Planning & Scheduling)
Last Updated: 2025-01-06
"""

import frappe
from frappe.utils import nowdate, add_days, add_months, getdate, get_datetime, now_datetime, flt, nowtime
from datetime import datetime, timedelta
import random

# ============================================================================
# CONFIGURATION
# ============================================================================

COMPANY = "Bear Manufacturing"
FG_WAREHOUSE = "Finished Goods - BM"
WIP_WAREHOUSE = "Work In Progress - BM"
SOURCE_WAREHOUSE = "Stores - BM"
SELLING_WAREHOUSE = "Kho Thanh Pham - BM"
PRICE_LIST = "Standard Selling"
CURRENCY = "VND"

# Products with BOMs
PRODUCTS = [
    {"item": "TP-BLV-001", "bom": "BOM-TP-BLV-001-001", "name": "Ban Lam Viec Go Soi 120x60", "price": 3700000, "max_qty": 20},
    {"item": "TP-BLV-002", "bom": "BOM-TP-BLV-002-001", "name": "Ban Lam Viec Go Thong 100x50", "price": 1600000, "max_qty": 25},
    {"item": "TP-GVP-001", "bom": "BOM-TP-GVP-001-001", "name": "Ghe Van Phong Go Soi", "price": 1590000, "max_qty": 50},
]

# All finished products for sales orders
ALL_PRODUCTS = [
    {"code": "TP-BLV-001", "name": "Ban Lam Viec Go Soi 120x60", "price": 3700000, "max_qty": 20},
    {"code": "TP-BLV-002", "name": "Ban Lam Viec Go Thong 100x50", "price": 1600000, "max_qty": 25},
    {"code": "TP-BAN-001", "name": "Ban An Go Cam 6 Cho", "price": 5560000, "max_qty": 15},
    {"code": "TP-GVP-001", "name": "Ghe Van Phong Go Soi", "price": 1590000, "max_qty": 50},
    {"code": "TP-GAN-001", "name": "Ghe An Go Cam", "price": 1430000, "max_qty": 40},
    {"code": "TP-GBT-001", "name": "Ghe Bar Go Thong", "price": 840000, "max_qty": 30},
    {"code": "TP-TQA-001", "name": "Tu Quan Ao 2 Canh Go Soi", "price": 10700000, "max_qty": 10},
    {"code": "TP-TQA-002", "name": "Tu Quan Ao 3 Canh MDF", "price": 9370000, "max_qty": 12},
    {"code": "TP-THS-001", "name": "Tu Ho So Van Phong", "price": 4570000, "max_qty": 15},
    {"code": "TP-GN16-001", "name": "Giuong Ngu Go Soi 1m6", "price": 9160000, "max_qty": 8},
    {"code": "TP-GN18-001", "name": "Giuong Ngu Go Soi 1m8", "price": 10600000, "max_qty": 8},
    {"code": "TP-GN12-001", "name": "Giuong Don Go Thong 1m2", "price": 2770000, "max_qty": 15},
    {"code": "TP-GT2T-001", "name": "Giuong Tang 2 Tang Go Thong", "price": 5980000, "max_qty": 10},
]

# Customers with weights
CUSTOMERS = [
    {"name": "IKEA Vietnam", "group": "Xuat Khau", "weight": 3},
    {"name": "Wayfair Export Co", "group": "Xuat Khau", "weight": 3},
    {"name": "Noi That Hoa Phat", "group": "Dai Ly", "weight": 2},
    {"name": "Noi That Xuan Hoa", "group": "Dai Ly", "weight": 2},
    {"name": "Showroom Noi That Binh Duong", "group": "Dai Ly", "weight": 2},
    {"name": "Nha Thau Xay Dung An Phat", "group": "Nha Thau Cong Trinh", "weight": 2},
    {"name": "Cong Ty TNHH Noi That Minh Long", "group": "Nha Thau Cong Trinh", "weight": 2},
    {"name": "Cong Ty TNHH Go Truong Thanh", "group": "Khach Si", "weight": 2},
    {"name": "Anh Nguyen Van A", "group": "Khach Le", "weight": 1},
    {"name": "Chi Tran Thi B", "group": "Khach Le", "weight": 1},
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def log(message, level="INFO"):
    """Print formatted log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"[{timestamp}] {symbols.get(level, 'ℹ')} {message}")

def get_random_customer():
    """Select random customer based on weight"""
    weighted_list = []
    for c in CUSTOMERS:
        weighted_list.extend([c] * c["weight"])
    return random.choice(weighted_list)

def get_random_items_for_so(customer_group):
    """Get random items for sales order based on customer group"""
    if customer_group in ["Xuat Khau", "Khach Si"]:
        num_items = random.randint(3, 6)
        qty_multiplier = random.uniform(2, 5)
    elif customer_group in ["Dai Ly", "Nha Thau Cong Trinh"]:
        num_items = random.randint(2, 4)
        qty_multiplier = random.uniform(1.5, 3)
    else:  # Khach Le
        num_items = random.randint(1, 3)
        qty_multiplier = random.uniform(0.5, 1.5)

    selected = random.sample(ALL_PRODUCTS, min(num_items, len(ALL_PRODUCTS)))

    items = []
    for prod in selected:
        qty = max(1, int(random.randint(1, prod["max_qty"]) * qty_multiplier))
        items.append({
            "item_code": prod["code"],
            "qty": qty,
            "rate": prod["price"]
        })

    return items

def generate_random_dates(start_date, end_date, count):
    """Generate random dates between start and end"""
    start = getdate(start_date)
    end = getdate(end_date)
    delta = (end - start).days

    dates = []
    for _ in range(count):
        random_days = random.randint(0, delta)
        dates.append(add_days(start, random_days))

    return sorted(dates)

def create_sales_orders(months_back=3, orders_per_month=12):
    """Create historical sales orders"""
    log(f"Creating sales orders for past {months_back} months...")

    start_date = add_months(nowdate(), -months_back)
    end_date = nowdate()

    # Generate random dates
    total_orders = months_back * orders_per_month
    order_dates = generate_random_dates(start_date, end_date, total_orders)

    created = 0
    for order_date in order_dates:
        try:
            customer_data = get_random_customer()
            items = get_random_items_for_so(customer_data["group"])

            so = frappe.new_doc("Sales Order")
            so.naming_series = "SAL-ORD-.YYYY.-"
            so.customer = customer_data["name"]
            so.transaction_date = order_date
            so.delivery_date = add_days(order_date, random.randint(7, 21))
            so.company = COMPANY
            so.currency = CURRENCY
            so.selling_price_list = PRICE_LIST

            for item in items:
                # Check if item exists
                if not frappe.db.exists("Item", item["item_code"]):
                    continue

                so.append("items", {
                    "item_code": item["item_code"],
                    "qty": item["qty"],
                    "rate": item["rate"],
                    "delivery_date": so.delivery_date,
                    "warehouse": SELLING_WAREHOUSE
                })

            if so.items:
                so.insert(ignore_permissions=True)
                so.submit()
                created += 1

                if created % 10 == 0:
                    frappe.db.commit()

        except Exception as e:
            log(f"Error creating SO: {str(e)}", "WARNING")
            continue

    frappe.db.commit()
    log(f"Created {created} sales orders", "SUCCESS")
    return created

def create_production_plans_from_sales(limit=5):
    """Create production plans from sales orders"""
    log("Creating production plans...")

    # Get recent submitted sales orders
    sales_orders = frappe.get_all(
        "Sales Order",
        filters={"docstatus": 1, "status": ["!=", "Closed"]},
        order_by="transaction_date desc",
        limit=limit,
        fields=["name"]
    )

    created = 0
    for so in sales_orders:
        try:
            pp = frappe.new_doc("Production Plan")
            pp.naming_series = "MFG-PP-.YYYY.-"
            pp.company = COMPANY
            pp.posting_date = nowdate()
            pp.get_items_from = "Sales Order"

            # Add sales order
            pp.append("sales_orders", {
                "sales_order": so.name
            })

            pp.insert(ignore_permissions=True)

            # Get items from SO
            pp.get_items()

            pp.save()
            pp.submit()
            created += 1

        except Exception as e:
            log(f"Error creating Production Plan: {str(e)}", "WARNING")
            continue

    frappe.db.commit()
    log(f"Created {created} production plans", "SUCCESS")
    return created

def create_work_orders(limit=10):
    """Create work orders for items with BOM"""
    log("Creating work orders...")

    created = 0
    start_date = add_days(nowdate(), -30)

    for i in range(limit):
        try:
            product = random.choice(PRODUCTS)

            # Check if BOM exists
            if not frappe.db.exists("BOM", product["bom"]):
                continue

            # Get BOM
            bom = frappe.get_doc("BOM", product["bom"])

            wo = frappe.new_doc("Work Order")
            wo.naming_series = "MFG-WO-.YYYY.-"
            wo.company = COMPANY
            wo.production_item = product["item"]
            wo.bom_no = product["bom"]
            wo.qty = random.randint(5, 15)
            wo.fg_warehouse = FG_WAREHOUSE
            wo.wip_warehouse = WIP_WAREHOUSE
            wo.source_warehouse = SOURCE_WAREHOUSE
            wo.planned_start_date = add_days(start_date, i * 2)
            wo.expected_delivery_date = add_days(wo.planned_start_date, 7)
            wo.use_multi_level_bom = 1
            wo.skip_transfer = 1

            # Add operations from BOM
            for idx, op in enumerate(bom.operations, start=1):
                wo.append("operations", {
                    "operation": op.operation,
                    "workstation": op.workstation,
                    "time_in_mins": op.time_in_mins,
                    "sequence_id": idx
                })

            wo.insert(ignore_permissions=True)
            wo.submit()
            created += 1

        except Exception as e:
            log(f"Error creating Work Order: {str(e)}", "WARNING")
            continue

    frappe.db.commit()
    log(f"Created {created} work orders", "SUCCESS")
    return created

def create_job_cards_for_work_orders(limit=5):
    """Create job cards for work orders"""
    log("Creating job cards...")

    # Get submitted work orders without job cards
    work_orders = frappe.get_all(
        "Work Order",
        filters={"docstatus": 1, "status": ["in", ["Not Started", "In Process"]]},
        limit=limit,
        fields=["name"]
    )

    created = 0
    employees = frappe.get_all("Employee", filters={"status": "Active"}, pluck="name")

    if not employees:
        log("No active employees found", "WARNING")
        return 0

    for wo_data in work_orders:
        try:
            wo = frappe.get_doc("Work Order", wo_data.name)

            for operation in wo.operations:
                # Check if job card already exists
                existing = frappe.db.exists("Job Card", {
                    "work_order": wo.name,
                    "operation": operation.operation
                })

                if existing:
                    continue

                jc = frappe.new_doc("Job Card")
                jc.work_order = wo.name
                jc.production_item = wo.production_item
                jc.operation = operation.operation
                jc.workstation = operation.workstation
                jc.for_quantity = wo.qty
                jc.posting_date = nowdate()
                jc.company = COMPANY

                # Add time log
                employee = random.choice(employees)
                start_time = now_datetime()
                time_mins = operation.time_in_mins * wo.qty
                end_time = start_time + timedelta(minutes=time_mins)

                jc.append("time_logs", {
                    "employee": employee,
                    "from_time": start_time,
                    "to_time": end_time,
                    "completed_qty": wo.qty,
                    "time_in_mins": time_mins
                })

                jc.insert(ignore_permissions=True)
                created += 1

        except Exception as e:
            log(f"Error creating Job Card: {str(e)}", "WARNING")
            continue

    frappe.db.commit()
    log(f"Created {created} job cards", "SUCCESS")
    return created

def create_stock_entries(limit=10):
    """Create stock entries for raw materials"""
    log("Creating stock entries...")

    raw_materials = [
        "NVL-GO-SOI-01", "NVL-GO-THONG-01", "NVL-GO-CAM-01",
        "PK-VIT-01", "PK-VIT-02", "HC-KEO-01", "HC-SON-LOT-01", "HC-SON-PHU-01"
    ]

    created = 0
    for i in range(limit):
        try:
            item_code = random.choice(raw_materials)

            # Check if item exists
            if not frappe.db.exists("Item", item_code):
                continue

            se = frappe.new_doc("Stock Entry")
            se.stock_entry_type = "Material Receipt"
            se.company = COMPANY
            se.posting_date = add_days(nowdate(), -random.randint(1, 60))
            se.to_warehouse = SOURCE_WAREHOUSE

            se.append("items", {
                "item_code": item_code,
                "qty": random.randint(50, 200),
                "t_warehouse": SOURCE_WAREHOUSE,
                "basic_rate": frappe.db.get_value("Item", item_code, "standard_rate") or 100000
            })

            se.insert(ignore_permissions=True)
            se.submit()
            created += 1

        except Exception as e:
            log(f"Error creating Stock Entry: {str(e)}", "WARNING")
            continue

    frappe.db.commit()
    log(f"Created {created} stock entries", "SUCCESS")
    return created

# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def create_transactional_data(months=3, orders_per_month=12, work_orders=10, job_cards=5, stock_entries=10):
    """Main function to create transactional data"""
    log("=" * 70)
    log("WOOD MANUFACTURING DEMO - TRANSACTIONAL DATA CREATION")
    log("=" * 70)

    try:
        # Create raw material stock first
        create_stock_entries(stock_entries)

        # Create sales orders
        create_sales_orders(months, orders_per_month)

        # Create production plans
        create_production_plans_from_sales(5)

        # Create work orders
        create_work_orders(work_orders)

        # Create job cards
        create_job_cards_for_work_orders(job_cards)

        log("=" * 70)
        log("TRANSACTIONAL DATA CREATION COMPLETED!", "SUCCESS")
        log("=" * 70)
        log("Summary:")
        log("- Sales Orders: Created for past {} months".format(months))
        log("- Production Plans: Created from recent SOs")
        log("- Work Orders: {} created".format(work_orders))
        log("- Job Cards: Created for work orders")
        log("- Stock Entries: {} created for raw materials".format(stock_entries))
        log("")
        log("Next steps:")
        log("1. Run APS Forecast to predict future demand")
        log("2. Run Production Planning optimization")
        log("3. Run MRP Optimization for material requirements")
        log("4. Run Scheduling Engine to optimize production schedule")

    except Exception as e:
        log(f"Error occurred: {str(e)}", "ERROR")
        frappe.db.rollback()
        raise

# Auto-execute when script is run
if __name__ == "__main__":
    create_transactional_data()
