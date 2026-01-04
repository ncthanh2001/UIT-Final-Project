"""
Script tạo data mẫu cho APS System
Chạy trong bench console: bench --site [sitename] console
Sau đó: exec(open('/path/to/generate_aps_data.py').read())

Hoặc copy nội dung và paste vào bench console
"""

import frappe
from frappe.utils import nowdate, add_days, add_months, getdate, get_datetime, now_datetime
from datetime import datetime, timedelta
import random

# ============ CONFIGURATION ============
COMPANY = "Bear Manufacturing"
FG_WAREHOUSE = "Finished Goods - BM"
WIP_WAREHOUSE = "Work In Progress - BM"
SOURCE_WAREHOUSE = "Stores - BM"

# Products to manufacture (with BOM)
PRODUCTS = [
    {"item": "TP-BLV-001", "bom": "BOM-TP-BLV-001-001", "name": "Ban Lam Viec Go Soi 120x60"},
    {"item": "TP-GVP-001", "bom": "BOM-TP-GVP-001-001", "name": "Ghe Van Phong Go Soi"},
    {"item": "TP-GAN-001", "bom": "BOM-TP-GAN-001-001", "name": "Ghe An Go Cam"},
    {"item": "TP-TQA-001", "bom": "BOM-TP-TQA-001-001", "name": "Tu Quan Ao 2 Canh Go Soi"},
    {"item": "TP-GBT-001", "bom": "BOM-TP-GBT-001-001", "name": "Ghe Bar Go Thong"},
]

# Employees for time logs
EMPLOYEES = []

# Workstations for downtime
WORKSTATIONS = []

def get_employees():
    """Get or create employees"""
    global EMPLOYEES
    employees = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name"])
    if employees:
        EMPLOYEES = [e.name for e in employees]
    else:
        # Create employees if not exist
        emp_data = [
            {"name": "Nguyen Van An", "gender": "Male"},
            {"name": "Tran Thi Binh", "gender": "Female"},
            {"name": "Le Van Cuong", "gender": "Male"},
            {"name": "Pham Thi Dung", "gender": "Female"},
            {"name": "Hoang Van Em", "gender": "Male"},
        ]
        for emp in emp_data:
            doc = frappe.new_doc("Employee")
            doc.naming_series = "HR-EMP-"
            doc.employee_name = emp["name"]
            doc.first_name = emp["name"].split()[0]
            doc.gender = emp["gender"]
            doc.date_of_birth = "1990-01-01"
            doc.date_of_joining = "2020-01-01"
            doc.company = COMPANY
            doc.status = "Active"
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_permissions=True)
            EMPLOYEES.append(doc.name)
        frappe.db.commit()
    print(f"✓ Found/Created {len(EMPLOYEES)} employees")
    return EMPLOYEES

def get_workstations():
    """Get all workstations"""
    global WORKSTATIONS
    ws = frappe.get_all("Workstation", fields=["name"])
    WORKSTATIONS = [w.name for w in ws]
    print(f"✓ Found {len(WORKSTATIONS)} workstations")
    return WORKSTATIONS

def create_work_order_with_operations(item_code, bom_no, qty, planned_start, production_plan=None):
    """Create Work Order with operations from BOM"""
    # Get BOM operations
    bom = frappe.get_doc("BOM", bom_no)
    
    wo = frappe.new_doc("Work Order")
    wo.naming_series = "MFG-WO-.YYYY.-"
    wo.company = COMPANY
    wo.production_item = item_code
    wo.bom_no = bom_no
    wo.qty = qty
    wo.fg_warehouse = FG_WAREHOUSE
    wo.wip_warehouse = WIP_WAREHOUSE
    wo.source_warehouse = SOURCE_WAREHOUSE
    wo.planned_start_date = planned_start
    wo.expected_delivery_date = add_days(planned_start, 7)
    wo.use_multi_level_bom = 1
    wo.skip_transfer = 1
    
    if production_plan:
        wo.production_plan = production_plan
    
    # Add operations from BOM (sequence_id must start from 1)
    for idx, op in enumerate(bom.operations, start=1):
        wo.append("operations", {
            "operation": op.operation,
            "workstation": op.workstation,
            "time_in_mins": op.time_in_mins * qty,  # Total time for all qty
            "hour_rate": op.hour_rate,
            "sequence_id": idx,  # Must be 1, 2, 3... not 10, 20, 30...
            "description": op.description,
            "batch_size": op.batch_size or 1
        })
    
    wo.insert(ignore_permissions=True)
    return wo

def create_job_cards_for_work_order(wo_name):
    """Create Job Cards for Work Order operations"""
    wo = frappe.get_doc("Work Order", wo_name)
    job_cards = []
    
    current_time = get_datetime(wo.planned_start_date)
    
    for idx, op in enumerate(wo.operations, start=1):
        jc = frappe.new_doc("Job Card")
        jc.naming_series = "PO-JOB.#####"
        jc.work_order = wo.name
        jc.bom_no = wo.bom_no
        jc.production_item = wo.production_item
        jc.company = wo.company
        jc.for_quantity = wo.qty
        jc.operation = op.operation
        jc.workstation = op.workstation
        jc.wip_warehouse = WIP_WAREHOUSE
        jc.expected_start_date = current_time
        jc.time_required = op.time_in_mins
        jc.sequence_id = idx  # Use sequential index
        
        # Calculate expected end time
        end_time = current_time + timedelta(minutes=op.time_in_mins)
        jc.expected_end_date = end_time
        
        jc.insert(ignore_permissions=True)
        job_cards.append(jc)
        
        # Next operation starts after this one (simplified - no parallel)
        current_time = end_time + timedelta(minutes=10)  # 10 min gap
    
    return job_cards

def complete_job_card_with_time_log(jc_name, variance_percent=0.15):
    """Complete a job card with realistic time logs"""
    jc = frappe.get_doc("Job Card", jc_name)
    
    if not EMPLOYEES:
        get_employees()
    
    # Random employee
    employee = random.choice(EMPLOYEES)
    
    # Actual time with variance (-15% to +20%)
    variance = random.uniform(-variance_percent, variance_percent + 0.05)
    actual_mins = jc.time_required * (1 + variance)
    
    # Start and end times
    start_time = get_datetime(jc.expected_start_date)
    end_time = start_time + timedelta(minutes=actual_mins)
    
    # Add time log
    jc.append("time_logs", {
        "employee": employee,
        "from_time": start_time,
        "to_time": end_time,
        "completed_qty": jc.for_quantity,
        "time_in_mins": actual_mins
    })
    
    jc.total_completed_qty = jc.for_quantity
    jc.save(ignore_permissions=True)
    
    # Submit job card
    jc.submit()
    
    return jc, actual_mins

def create_downtime_entries(num_entries=20):
    """Create historical downtime entries"""
    if not WORKSTATIONS:
        get_workstations()
    if not EMPLOYEES:
        get_employees()
    
    stop_reasons = [
        "Excessive machine set up time",
        "Unplanned machine maintenance", 
        "Machine operator errors",
        "Machine malfunction",
        "Electricity down",
        "Other"
    ]
    
    downtime_entries = []
    
    # Create entries over last 3 months
    for i in range(num_entries):
        # Random date in last 90 days
        days_ago = random.randint(1, 90)
        dt_date = add_days(nowdate(), -days_ago)
        
        # Random time
        hour = random.randint(7, 17)
        minute = random.randint(0, 59)
        
        from_time = datetime.strptime(f"{dt_date} {hour:02d}:{minute:02d}:00", "%Y-%m-%d %H:%M:%S")
        
        # Duration 15-180 minutes
        duration = random.randint(15, 180)
        to_time = from_time + timedelta(minutes=duration)
        
        dt = frappe.new_doc("Downtime Entry")
        dt.naming_series = "DT-"
        dt.workstation = random.choice(WORKSTATIONS)
        dt.operator = random.choice(EMPLOYEES)
        dt.from_time = from_time
        dt.to_time = to_time
        dt.stop_reason = random.choice(stop_reasons)
        dt.remarks = f"Auto-generated historical data - Entry {i+1}"
        
        dt.insert(ignore_permissions=True)
        downtime_entries.append(dt.name)
    
    frappe.db.commit()
    print(f"✓ Created {len(downtime_entries)} Downtime Entries")
    return downtime_entries

def generate_historical_data(months_back=3, orders_per_month=5):
    """Main function to generate all historical data"""
    print("="*60)
    print("GENERATING HISTORICAL DATA FOR APS SYSTEM")
    print("="*60)
    
    # Step 1: Get employees and workstations
    get_employees()
    get_workstations()
    
    # Step 2: Create Production Plans, Work Orders, Job Cards
    all_work_orders = []
    all_job_cards = []
    
    for month_offset in range(months_back, 0, -1):
        month_start = add_months(nowdate(), -month_offset)
        print(f"\n--- Processing Month: {month_start[:7]} ---")
        
        for order_num in range(orders_per_month):
            # Random product
            product = random.choice(PRODUCTS)
            
            # Random qty (5-25)
            qty = random.randint(5, 25)
            
            # Random start date within month
            day_offset = random.randint(0, 25)
            planned_start = add_days(month_start, day_offset)
            planned_start_dt = f"{planned_start} 08:00:00"
            
            try:
                # Create Work Order
                wo = create_work_order_with_operations(
                    product["item"],
                    product["bom"],
                    qty,
                    planned_start_dt
                )
                
                # Submit Work Order
                wo.submit()
                all_work_orders.append(wo.name)
                
                # Create Job Cards
                job_cards = create_job_cards_for_work_order(wo.name)
                
                # Complete Job Cards with time logs
                for jc in job_cards:
                    completed_jc, actual_time = complete_job_card_with_time_log(jc.name)
                    all_job_cards.append(completed_jc.name)
                
                # Update Work Order status
                wo.reload()
                wo.db_set("produced_qty", qty)
                wo.db_set("status", "Completed")
                
                print(f"  ✓ WO: {wo.name} | {product['item']} x {qty} | {len(job_cards)} Job Cards")
                
            except Exception as e:
                print(f"  ✗ Error creating WO for {product['item']}: {str(e)}")
                frappe.db.rollback()
                continue
            
            frappe.db.commit()
    
    # Step 3: Create Downtime Entries
    print("\n--- Creating Downtime Entries ---")
    create_downtime_entries(25)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Work Orders created: {len(all_work_orders)}")
    print(f"Job Cards created: {len(all_job_cards)}")
    print(f"Employees: {len(EMPLOYEES)}")
    print(f"Workstations: {len(WORKSTATIONS)}")
    print("="*60)
    
    return {
        "work_orders": all_work_orders,
        "job_cards": all_job_cards
    }

# Run the script
if __name__ == "__main__":
    result = generate_historical_data(months_back=3, orders_per_month=5)
