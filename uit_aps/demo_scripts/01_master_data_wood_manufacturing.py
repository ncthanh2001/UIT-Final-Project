"""
Demo Script 1: Master Data Setup for Wood Manufacturing Company
================================================================

This script creates all master data for a complete wood furniture manufacturing business:
- Company structure
- Warehouses
- Item Groups and Items (Raw materials, Sub-assemblies, Finished goods)
- Suppliers
- Customers (Multiple segments)
- Workstations (Complete production floor)
- Employees
- BOMs (Bill of Materials)
- Work shifts

Usage:
------
Method 1 - Bench Console:
  bench --site [sitename] console
  exec(open('apps/uit_aps/uit_aps/demo_scripts/01_master_data_wood_manufacturing.py').read())

Method 2 - Direct execution:
  bench --site [sitename] execute apps.uit_aps.uit_aps.demo_scripts.01_master_data_wood_manufacturing.create_all_master_data

Created for: UIT APS (Advanced Planning & Scheduling)
Company Context: Premium Wood Furniture Manufacturing
Last Updated: 2025-01-06
"""

import frappe
from frappe.utils import nowdate, cint
from datetime import datetime
import random

# ============================================================================
# CONFIGURATION SECTION
# ============================================================================

COMPANY_CONFIG = {
    "name": "Bear Manufacturing",
    "abbr": "BM",
    "country": "Vietnam",
    "default_currency": "VND",
    "domain": "Manufacturing"
}

WAREHOUSES = [
    {"name": "Stores", "type": "Stores", "desc": "Raw materials and components"},
    {"name": "Work In Progress", "type": "Work In Progress", "desc": "WIP goods in production"},
    {"name": "Finished Goods", "type": "Finished Goods", "desc": "Completed products ready for sale"},
    {"name": "Kho NVL Go Soi", "type": "Stores", "parent": "Stores", "desc": "Oak wood storage"},
    {"name": "Kho NVL Go Thong", "type": "Stores", "parent": "Stores", "desc": "Pine wood storage"},
    {"name": "Kho NVL Go Cam", "type": "Stores", "parent": "Stores", "desc": "Ebony wood storage"},
    {"name": "Kho Thanh Pham", "type": "Finished Goods", "parent": "Finished Goods", "desc": "Finished products warehouse"},
]

# Item Groups Hierarchy
ITEM_GROUPS = [
    {"name": "Raw Materials", "parent": "All Item Groups"},
    {"name": "Go Nguyen Lieu", "parent": "Raw Materials"},
    {"name": "Phu Kien Kim Loai", "parent": "Raw Materials"},
    {"name": "Hoa Chat", "parent": "Raw Materials"},
    {"name": "Sub Assemblies", "parent": "All Item Groups"},
    {"name": "Linh Kien Go", "parent": "Sub Assemblies"},
    {"name": "Finished Products", "parent": "All Item Groups"},
    {"name": "Ban Lam Viec", "parent": "Finished Products"},
    {"name": "Ghe", "parent": "Finished Products"},
    {"name": "Tu", "parent": "Finished Products"},
    {"name": "Giuong", "parent": "Finished Products"},
]

# Raw Materials
RAW_MATERIALS = [
    # Wood types
    {"code": "NVL-GO-SOI-01", "name": "Go Soi Nguyen Lieu 2m x 0.2m x 0.05m", "group": "Go Nguyen Lieu", "uom": "Cay", "price": 450000, "min_order": 10},
    {"code": "NVL-GO-THONG-01", "name": "Go Thong Nguyen Lieu 2m x 0.2m x 0.05m", "group": "Go Nguyen Lieu", "uom": "Cay", "price": 280000, "min_order": 20},
    {"code": "NVL-GO-CAM-01", "name": "Go Cam Nguyen Lieu 1.5m x 0.15m x 0.04m", "group": "Go Nguyen Lieu", "uom": "Cay", "price": 620000, "min_order": 5},
    {"code": "NVL-MDF-01", "name": "Tam MDF 18mm 1220x2440mm", "group": "Go Nguyen Lieu", "uom": "Tam", "price": 380000, "min_order": 10},
    {"code": "NVL-PLYWOOD-01", "name": "Go Dan 12mm 1220x2440mm", "group": "Go Nguyen Lieu", "uom": "Tam", "price": 420000, "min_order": 10},

    # Hardware
    {"code": "PK-VIT-01", "name": "Vit Go 4x40mm", "group": "Phu Kien Kim Loai", "uom": "Hop", "price": 25000, "min_order": 50},
    {"code": "PK-VIT-02", "name": "Vit Go 5x50mm", "group": "Phu Kien Kim Loai", "uom": "Hop", "price": 35000, "min_order": 50},
    {"code": "PK-BAN-LE-01", "name": "Ban Le Go 35mm", "group": "Phu Kien Kim Loai", "uom": "Cai", "price": 8000, "min_order": 100},
    {"code": "PK-RAY-TU-01", "name": "Ray Truot Tu 450mm", "group": "Phu Kien Kim Loai", "uom": "Bo", "price": 120000, "min_order": 20},
    {"code": "PK-TAY-NAM-01", "name": "Tay Nam Inox", "group": "Phu Kien Kim Loai", "uom": "Cai", "price": 45000, "min_order": 50},

    # Chemicals
    {"code": "HC-KEO-01", "name": "Keo Dan Go D3", "group": "Hoa Chat", "uom": "Lit", "price": 85000, "min_order": 20},
    {"code": "HC-SON-LOT-01", "name": "Son Lot PU", "group": "Hoa Chat", "uom": "Lit", "price": 95000, "min_order": 20},
    {"code": "HC-SON-PHU-01", "name": "Son Phu PU Bong", "group": "Hoa Chat", "uom": "Lit", "price": 125000, "min_order": 20},
    {"code": "HC-DAU-MO-01", "name": "Dau Mo Go", "group": "Hoa Chat", "uom": "Lit", "price": 75000, "min_order": 10},
]

# Sub-assemblies
SUB_ASSEMBLIES = [
    {"code": "LK-MAT-BAN-120", "name": "Mat Ban 120x60cm Da Gia Cong", "group": "Linh Kien Go", "uom": "Cai"},
    {"code": "LK-MAT-BAN-100", "name": "Mat Ban 100x50cm Da Gia Cong", "group": "Linh Kien Go", "uom": "Cai"},
    {"code": "LK-CHAN-BAN-70", "name": "Chan Ban 70cm Da Gia Cong", "group": "Linh Kien Go", "uom": "Cai"},
    {"code": "LK-LUNG-GHE", "name": "Lung Ghe Da Gia Cong", "group": "Linh Kien Go", "uom": "Cai"},
    {"code": "LK-MAT-GHE", "name": "Mat Ghe Da Gia Cong", "group": "Linh Kien Go", "uom": "Cai"},
    {"code": "LK-CHAN-GHE", "name": "Chan Ghe Da Gia Cong", "group": "Linh Kien Go", "uom": "Cai"},
    {"code": "LK-CANH-TU", "name": "Canh Tu Da Gia Cong", "group": "Linh Kien Go", "uom": "Cai"},
    {"code": "LK-MAU-GIUONG", "name": "Mau Giuong Da Gia Cong", "group": "Linh Kien Go", "uom": "Cai"},
]

# Finished Products (13 wood furniture items)
FINISHED_PRODUCTS = [
    {"code": "TP-BLV-001", "name": "Ban Lam Viec Go Soi 120x60", "group": "Ban Lam Viec", "uom": "Cai", "price": 3700000},
    {"code": "TP-BLV-002", "name": "Ban Lam Viec Go Thong 100x50", "group": "Ban Lam Viec", "uom": "Cai", "price": 1600000},
    {"code": "TP-BAN-001", "name": "Ban An Go Cam 6 Cho", "group": "Ban Lam Viec", "uom": "Cai", "price": 5560000},
    {"code": "TP-GVP-001", "name": "Ghe Van Phong Go Soi", "group": "Ghe", "uom": "Cai", "price": 1590000},
    {"code": "TP-GAN-001", "name": "Ghe An Go Cam", "group": "Ghe", "uom": "Cai", "price": 1430000},
    {"code": "TP-GBT-001", "name": "Ghe Bar Go Thong", "group": "Ghe", "uom": "Cai", "price": 840000},
    {"code": "TP-TQA-001", "name": "Tu Quan Ao 2 Canh Go Soi", "group": "Tu", "uom": "Cai", "price": 10700000},
    {"code": "TP-TQA-002", "name": "Tu Quan Ao 3 Canh MDF", "group": "Tu", "uom": "Cai", "price": 9370000},
    {"code": "TP-THS-001", "name": "Tu Ho So Van Phong", "group": "Tu", "uom": "Cai", "price": 4570000},
    {"code": "TP-GN16-001", "name": "Giuong Ngu Go Soi 1m6", "group": "Giuong", "uom": "Cai", "price": 9160000},
    {"code": "TP-GN18-001", "name": "Giuong Ngu Go Soi 1m8", "group": "Giuong", "uom": "Cai", "price": 10600000},
    {"code": "TP-GN12-001", "name": "Giuong Don Go Thong 1m2", "group": "Giuong", "uom": "Cai", "price": 2770000},
    {"code": "TP-GT2T-001", "name": "Giuong Tang 2 Tang Go Thong", "group": "Giuong", "uom": "Cai", "price": 5980000},
]

# Suppliers
SUPPLIERS = [
    {"name": "Cong Ty Go Soi Bac Ninh", "group": "Raw Material", "country": "Vietnam"},
    {"name": "Nha Cung Cap Go Thong Lam Dong", "group": "Raw Material", "country": "Vietnam"},
    {"name": "Kim Khi Phat Dat", "group": "Hardware", "country": "Vietnam"},
    {"name": "Hoa Chat Son Nam Long", "group": "Chemical", "country": "Vietnam"},
    {"name": "MDF Import Vietnam Co", "group": "Raw Material", "country": "Vietnam"},
]

# Customers (Multiple segments)
CUSTOMERS = [
    # Export customers
    {"name": "IKEA Vietnam", "group": "Xuat Khau", "country": "Vietnam", "territory": "Vietnam"},
    {"name": "Wayfair Export Co", "group": "Xuat Khau", "country": "United States", "territory": "Rest Of The World"},
    {"name": "Home24 Europe", "group": "Xuat Khau", "country": "Germany", "territory": "Rest Of The World"},

    # Distributors
    {"name": "Noi That Hoa Phat", "group": "Dai Ly", "country": "Vietnam", "territory": "Vietnam"},
    {"name": "Noi That Xuan Hoa", "group": "Dai Ly", "country": "Vietnam", "territory": "Vietnam"},
    {"name": "Showroom Noi That Binh Duong", "group": "Dai Ly", "country": "Vietnam", "territory": "Vietnam"},

    # Contractors
    {"name": "Nha Thau Xay Dung An Phat", "group": "Nha Thau Cong Trinh", "country": "Vietnam", "territory": "Vietnam"},
    {"name": "Cong Ty TNHH Noi That Minh Long", "group": "Nha Thau Cong Trinh", "country": "Vietnam", "territory": "Vietnam"},

    # Wholesale
    {"name": "Cong Ty TNHH Go Truong Thanh", "group": "Khach Si", "country": "Vietnam", "territory": "Vietnam"},

    # Retail
    {"name": "Anh Nguyen Van A", "group": "Khach Le", "country": "Vietnam", "territory": "Vietnam"},
    {"name": "Chi Tran Thi B", "group": "Khach Le", "country": "Vietnam", "territory": "Vietnam"},
]

# Manufacturing Operations
OPERATIONS = [
    {"name": "Cat Go", "workstation": "May Cat Panel Saw 01", "time_mins": 15},
    {"name": "Bao Go", "workstation": "May Bao 2 Mat 01", "time_mins": 20},
    {"name": "Phay Rãnh", "workstation": "May Phay CNC 01", "time_mins": 25},
    {"name": "Khoan Lỗ", "workstation": "May Khoan CNC 01", "time_mins": 10},
    {"name": "Cha Nham", "workstation": "May Cha Nham Bang 01", "time_mins": 30},
    {"name": "Phun Son Lot", "workstation": "Buong Phun Son 01", "time_mins": 40},
    {"name": "Say Son Lot", "workstation": "Phong Say Son 01", "time_mins": 120},
    {"name": "Phun Son Phu", "workstation": "Buong Phun Son 02", "time_mins": 40},
    {"name": "Say Son Phu", "workstation": "Phong Say Son 01", "time_mins": 180},
    {"name": "Lap Rap", "workstation": "Ban Lap Rap 01", "time_mins": 60},
    {"name": "Kiem Tra", "workstation": "Ban QC 01", "time_mins": 15},
    {"name": "Dong Goi", "workstation": "Ban Dong Goi 01", "time_mins": 20},
]

# Employees
EMPLOYEES = [
    {"name": "Nguyen Van An", "gender": "Male", "department": "Che Bien Go", "designation": "Tho May"},
    {"name": "Tran Thi Binh", "gender": "Female", "department": "Son", "designation": "Tho Son"},
    {"name": "Le Van Cuong", "gender": "Male", "department": "Lap Rap", "designation": "Tho Lap Rap"},
    {"name": "Pham Thi Dung", "gender": "Female", "department": "QC", "designation": "Nhan Vien Kiem Tra"},
    {"name": "Hoang Van Em", "gender": "Male", "department": "Che Bien Go", "designation": "Tho May"},
    {"name": "Vo Thi Phuong", "gender": "Female", "department": "Dong Goi", "designation": "Nhan Vien Dong Goi"},
    {"name": "Dang Van Giang", "gender": "Male", "department": "CNC", "designation": "Ky Thuat Vien CNC"},
    {"name": "Bui Thi Hoa", "gender": "Female", "department": "Son", "designation": "Tho Son"},
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def log(message, level="INFO"):
    """Print formatted log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"[{timestamp}] {symbols.get(level, 'ℹ')} {message}")

def create_company():
    """Create company if not exists"""
    if frappe.db.exists("Company", COMPANY_CONFIG["name"]):
        log(f"Company '{COMPANY_CONFIG['name']}' already exists", "INFO")
        return

    log(f"Creating company: {COMPANY_CONFIG['name']}")
    company = frappe.new_doc("Company")
    company.company_name = COMPANY_CONFIG["name"]
    company.abbr = COMPANY_CONFIG["abbr"]
    company.country = COMPANY_CONFIG["country"]
    company.default_currency = COMPANY_CONFIG["default_currency"]
    company.domain = COMPANY_CONFIG["domain"]
    company.insert(ignore_permissions=True)
    frappe.db.commit()
    log(f"Company created successfully", "SUCCESS")

def create_warehouses():
    """Create warehouse structure"""
    log("Creating warehouses...")
    count = 0
    company_abbr = COMPANY_CONFIG["abbr"]

    for wh in WAREHOUSES:
        full_name = f"{wh['name']} - {company_abbr}"
        if frappe.db.exists("Warehouse", full_name):
            continue

        warehouse = frappe.new_doc("Warehouse")
        warehouse.warehouse_name = wh["name"]
        warehouse.company = COMPANY_CONFIG["name"]
        warehouse.warehouse_type = wh.get("type")

        if wh.get("parent"):
            warehouse.parent_warehouse = f"{wh['parent']} - {company_abbr}"

        warehouse.insert(ignore_permissions=True)
        count += 1

    frappe.db.commit()
    log(f"Created {count} warehouses", "SUCCESS")

def create_item_groups():
    """Create item group hierarchy"""
    log("Creating item groups...")
    count = 0

    for ig in ITEM_GROUPS:
        if frappe.db.exists("Item Group", ig["name"]):
            continue

        item_group = frappe.new_doc("Item Group")
        item_group.item_group_name = ig["name"]
        item_group.parent_item_group = ig["parent"]
        item_group.insert(ignore_permissions=True)
        count += 1

    frappe.db.commit()
    log(f"Created {count} item groups", "SUCCESS")

def create_items():
    """Create all items (raw materials, sub-assemblies, finished products)"""
    log("Creating items...")
    count = 0

    # Create raw materials
    for item_data in RAW_MATERIALS:
        if frappe.db.exists("Item", item_data["code"]):
            continue

        item = frappe.new_doc("Item")
        item.item_code = item_data["code"]
        item.item_name = item_data["name"]
        item.item_group = item_data["group"]
        item.stock_uom = item_data["uom"]
        item.is_stock_item = 1
        item.is_purchase_item = 1
        item.standard_rate = item_data["price"]
        item.min_order_qty = item_data.get("min_order", 1)
        item.insert(ignore_permissions=True)
        count += 1

    # Create sub-assemblies
    for item_data in SUB_ASSEMBLIES:
        if frappe.db.exists("Item", item_data["code"]):
            continue

        item = frappe.new_doc("Item")
        item.item_code = item_data["code"]
        item.item_name = item_data["name"]
        item.item_group = item_data["group"]
        item.stock_uom = item_data["uom"]
        item.is_stock_item = 1
        item.is_sub_contracted_item = 0
        item.insert(ignore_permissions=True)
        count += 1

    # Create finished products
    for item_data in FINISHED_PRODUCTS:
        if frappe.db.exists("Item", item_data["code"]):
            continue

        item = frappe.new_doc("Item")
        item.item_code = item_data["code"]
        item.item_name = item_data["name"]
        item.item_group = item_data["group"]
        item.stock_uom = item_data["uom"]
        item.is_stock_item = 1
        item.is_sales_item = 1
        item.standard_rate = item_data["price"]
        item.insert(ignore_permissions=True)
        count += 1

    frappe.db.commit()
    log(f"Created {count} items", "SUCCESS")

def create_suppliers():
    """Create suppliers"""
    log("Creating suppliers...")
    count = 0

    for supp in SUPPLIERS:
        if frappe.db.exists("Supplier", supp["name"]):
            continue

        supplier = frappe.new_doc("Supplier")
        supplier.supplier_name = supp["name"]
        supplier.supplier_group = supp["group"]
        supplier.country = supp["country"]
        supplier.insert(ignore_permissions=True)
        count += 1

    frappe.db.commit()
    log(f"Created {count} suppliers", "SUCCESS")

def create_customers():
    """Create customers"""
    log("Creating customers...")
    count = 0

    for cust in CUSTOMERS:
        if frappe.db.exists("Customer", cust["name"]):
            continue

        customer = frappe.new_doc("Customer")
        customer.customer_name = cust["name"]
        customer.customer_group = cust["group"]
        customer.territory = cust["territory"]
        customer.customer_type = "Company" if cust["group"] != "Khach Le" else "Individual"
        customer.insert(ignore_permissions=True)
        count += 1

    frappe.db.commit()
    log(f"Created {count} customers", "SUCCESS")

def create_operations_and_workstations():
    """Create operations linked to workstations (workstations should already exist from CSV)"""
    log("Creating operations...")
    count = 0

    for op in OPERATIONS:
        if frappe.db.exists("Operation", op["name"]):
            continue

        # Check if workstation exists
        if not frappe.db.exists("Workstation", op["workstation"]):
            log(f"Workstation '{op['workstation']}' not found, skipping operation '{op['name']}'", "WARNING")
            continue

        operation = frappe.new_doc("Operation")
        operation.operation = op["name"]
        operation.workstation = op["workstation"]

        # Add workstation row
        operation.append("workstations", {
            "workstation": op["workstation"],
            "time_in_mins": op["time_mins"]
        })

        operation.insert(ignore_permissions=True)
        count += 1

    frappe.db.commit()
    log(f"Created {count} operations", "SUCCESS")

def create_employees():
    """Create employees"""
    log("Creating employees...")
    count = 0

    for emp in EMPLOYEES:
        # Check if employee already exists
        exists = frappe.db.exists("Employee", {"employee_name": emp["name"]})
        if exists:
            continue

        employee = frappe.new_doc("Employee")
        employee.first_name = emp["name"].split()[0]
        employee.last_name = " ".join(emp["name"].split()[1:])
        employee.employee_name = emp["name"]
        employee.gender = emp["gender"]
        employee.company = COMPANY_CONFIG["name"]
        employee.status = "Active"
        employee.date_of_birth = "1990-01-01"
        employee.date_of_joining = "2023-01-01"
        employee.department = emp.get("department")
        employee.designation = emp.get("designation")
        employee.naming_series = "HR-EMP-"
        employee.flags.ignore_mandatory = True
        employee.insert(ignore_permissions=True)
        count += 1

    frappe.db.commit()
    log(f"Created {count} employees", "SUCCESS")

def create_basic_boms():
    """Create simple BOMs for finished products"""
    log("Creating BOMs...")
    count = 0

    # Example BOM structure for TP-BLV-001 (Ban Lam Viec Go Soi 120x60)
    bom_data = [
        {
            "item": "TP-BLV-001",
            "qty": 1,
            "items": [
                {"item_code": "NVL-GO-SOI-01", "qty": 3, "rate": 450000},
                {"item_code": "PK-VIT-01", "qty": 2, "rate": 25000},
                {"item_code": "HC-KEO-01", "qty": 0.5, "rate": 85000},
                {"item_code": "HC-SON-LOT-01", "qty": 0.3, "rate": 95000},
                {"item_code": "HC-SON-PHU-01", "qty": 0.3, "rate": 125000},
            ],
            "operations": ["Cat Go", "Bao Go", "Phay Rãnh", "Khoan Lỗ", "Cha Nham",
                          "Phun Son Lot", "Say Son Lot", "Phun Son Phu", "Say Son Phu",
                          "Lap Rap", "Kiem Tra", "Dong Goi"]
        },
        {
            "item": "TP-BLV-002",
            "qty": 1,
            "items": [
                {"item_code": "NVL-GO-THONG-01", "qty": 2, "rate": 280000},
                {"item_code": "PK-VIT-01", "qty": 1, "rate": 25000},
                {"item_code": "HC-KEO-01", "qty": 0.3, "rate": 85000},
                {"item_code": "HC-SON-LOT-01", "qty": 0.2, "rate": 95000},
                {"item_code": "HC-SON-PHU-01", "qty": 0.2, "rate": 125000},
            ],
            "operations": ["Cat Go", "Bao Go", "Khoan Lỗ", "Cha Nham",
                          "Phun Son Lot", "Say Son Lot", "Phun Son Phu", "Say Son Phu",
                          "Lap Rap", "Kiem Tra", "Dong Goi"]
        },
        {
            "item": "TP-GVP-001",
            "qty": 1,
            "items": [
                {"item_code": "NVL-GO-SOI-01", "qty": 1, "rate": 450000},
                {"item_code": "PK-VIT-02", "qty": 1, "rate": 35000},
                {"item_code": "HC-KEO-01", "qty": 0.2, "rate": 85000},
                {"item_code": "HC-DAU-MO-01", "qty": 0.1, "rate": 75000},
            ],
            "operations": ["Cat Go", "Bao Go", "Phay Rãnh", "Khoan Lỗ", "Cha Nham",
                          "Lap Rap", "Kiem Tra", "Dong Goi"]
        },
    ]

    for bom in bom_data:
        bom_name = f"BOM-{bom['item']}-001"
        if frappe.db.exists("BOM", bom_name):
            continue

        # Check if item exists
        if not frappe.db.exists("Item", bom["item"]):
            log(f"Item {bom['item']} not found, skipping BOM", "WARNING")
            continue

        bom_doc = frappe.new_doc("BOM")
        bom_doc.item = bom["item"]
        bom_doc.quantity = bom["qty"]
        bom_doc.company = COMPANY_CONFIG["name"]

        # Add raw materials
        for item in bom["items"]:
            if frappe.db.exists("Item", item["item_code"]):
                bom_doc.append("items", {
                    "item_code": item["item_code"],
                    "qty": item["qty"],
                    "rate": item["rate"]
                })

        # Add operations
        for idx, op_name in enumerate(bom["operations"], start=1):
            if frappe.db.exists("Operation", op_name):
                bom_doc.append("operations", {
                    "operation": op_name,
                    "time_in_mins": OPERATIONS[[o["name"] for o in OPERATIONS].index(op_name)]["time_mins"],
                    "sequence_id": idx
                })

        bom_doc.insert(ignore_permissions=True)
        bom_doc.submit()
        count += 1

    frappe.db.commit()
    log(f"Created {count} BOMs", "SUCCESS")

# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def create_all_master_data():
    """Main function to create all master data"""
    log("=" * 70)
    log("WOOD MANUFACTURING DEMO - MASTER DATA CREATION")
    log("=" * 70)

    try:
        create_company()
        create_warehouses()
        create_item_groups()
        create_items()
        create_suppliers()
        create_customers()
        create_employees()
        create_operations_and_workstations()
        create_basic_boms()

        log("=" * 70)
        log("MASTER DATA CREATION COMPLETED SUCCESSFULLY!", "SUCCESS")
        log("=" * 70)
        log("Next steps:")
        log("1. Import Workstations from CSV (if not already done)")
        log("2. Run demo script 02 to create transactional data")
        log("3. Run demo script 03 for complete APS workflow")

    except Exception as e:
        log(f"Error occurred: {str(e)}", "ERROR")
        frappe.db.rollback()
        raise

# Auto-execute when script is run
if __name__ == "__main__":
    create_all_master_data()
