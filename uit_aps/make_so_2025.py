"""
Script tạo Sales Order, Delivery Note, Sales Invoice 
Từ tháng 7/2025 đến tháng 11/2025
Mỗi tháng 10-12 đơn, đã hoàn thành (Completed)

Cách chạy:
1. bench --site [sitename] console
2. Copy paste toàn bộ script
3. Gọi: create_demo_sales_jul_nov_2025()
"""

import frappe
from frappe.utils import nowtime, flt, add_days
from datetime import datetime, timedelta
import random

# Import hàm tạo DN và SI
from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note, make_sales_invoice


# ========== CẤU HÌNH ==========
COMPANY = "Bear Manufacturing"
WAREHOUSE = "Kho Thanh Pham - BM"
PRICE_LIST = "Standard Selling"
CURRENCY = "VND"

# Danh sách khách hàng
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

# Danh sách sản phẩm với giá
ITEMS = [
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


def get_random_customer():
    """Chọn khách hàng ngẫu nhiên theo weight"""
    weighted_list = []
    for c in CUSTOMERS:
        weighted_list.extend([c["name"]] * c["weight"])
    return random.choice(weighted_list)


def get_random_items(customer_group):
    """Tạo danh sách items ngẫu nhiên cho đơn hàng"""
    # Số lượng loại sản phẩm trong đơn
    if customer_group in ["Xuat Khau", "Khach Si"]:
        num_items = random.randint(3, 6)  # Đơn lớn
        qty_multiplier = random.uniform(2, 5)
    elif customer_group in ["Dai Ly", "Nha Thau Cong Trinh"]:
        num_items = random.randint(2, 4)
        qty_multiplier = random.uniform(1.5, 3)
    else:  # Khách lẻ
        num_items = random.randint(1, 3)
        qty_multiplier = random.uniform(0.5, 1.5)
    
    selected_items = random.sample(ITEMS, min(num_items, len(ITEMS)))
    
    result = []
    for item in selected_items:
        qty = max(1, int(random.randint(1, item["max_qty"]) * qty_multiplier))
        result.append({
            "item_code": item["code"],
            "item_name": item["name"],
            "qty": qty,
            "rate": item["price"],
            "warehouse": WAREHOUSE
        })
    
    return result


def generate_dates_for_month(year, month, num_orders):
    """Tạo danh sách ngày ngẫu nhiên trong tháng"""
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    
    last_day = (next_month - timedelta(days=1)).day
    
    # Tạo các ngày ngẫu nhiên, tránh cuối tuần
    dates = []
    attempts = 0
    while len(dates) < num_orders and attempts < 100:
        day = random.randint(1, last_day)
        date = datetime(year, month, day)
        # Tránh thứ 7, CN
        if date.weekday() < 5:
            dates.append(date.strftime('%Y-%m-%d'))
        attempts += 1
    
    dates.sort()
    return dates


def create_so_with_dn_si(customer, items, transaction_date):
    """Tạo SO, DN, SI hoàn chỉnh"""
    
    # 1. Tạo Sales Order
    so = frappe.new_doc("Sales Order")
    so.customer = customer
    so.company = COMPANY
    so.transaction_date = transaction_date
    so.delivery_date = transaction_date
    so.selling_price_list = PRICE_LIST
    so.currency = CURRENCY
    so.set_warehouse = WAREHOUSE
    
    for item in items:
        so.append("items", {
            "item_code": item["item_code"],
            "item_name": item["item_name"],
            "qty": item["qty"],
            "rate": item["rate"],
            "warehouse": item["warehouse"],
            "delivery_date": transaction_date
        })
    
    so.insert(ignore_permissions=True)
    so.submit()
    
    # 2. Tạo Delivery Note từ SO
    dn = make_delivery_note(so.name)
    dn.posting_date = transaction_date
    dn.posting_time = "10:00:00"
    dn.set_posting_time = 1
    
    for item in dn.items:
        if not item.warehouse:
            item.warehouse = WAREHOUSE
    
    dn.insert(ignore_permissions=True)
    dn.submit()
    
    # 3. Tạo Sales Invoice từ SO
    si = make_sales_invoice(so.name)
    si.posting_date = transaction_date
    si.posting_time = "14:00:00"
    si.set_posting_time = 1
    si.update_stock = 0
    
    # Link với DN
    for si_item in si.items:
        for dn_item in dn.items:
            if si_item.item_code == dn_item.item_code and si_item.so_detail == dn_item.so_detail:
                si_item.delivery_note = dn.name
                si_item.dn_detail = dn_item.name
                break
    
    si.insert(ignore_permissions=True)
    si.submit()
    
    return {
        "so": so.name,
        "dn": dn.name,
        "si": si.name,
        "customer": customer,
        "grand_total": so.grand_total
    }


def create_demo_sales_jul_nov_2025():
    """
    Tạo đơn hàng demo từ tháng 7 đến tháng 11 năm 2025
    Mỗi tháng 10-12 đơn
    """
    
    print(f"\n{'='*70}")
    print("TAO DON HANG DEMO - THANG 7 DEN THANG 11/2025")
    print(f"{'='*70}\n")
    
    # Tháng và số đơn
    months = [
        (2025, 7, random.randint(10, 12)),
        (2025, 8, random.randint(10, 12)),
        (2025, 9, random.randint(10, 12)),
        (2025, 10, random.randint(10, 12)),
        (2025, 11, random.randint(10, 12)),
    ]
    
    total_orders = 0
    total_revenue = 0
    all_results = []
    
    for year, month, num_orders in months:
        month_name = datetime(year, month, 1).strftime('%B %Y')
        print(f"\n--- {month_name}: {num_orders} don ---")
        
        dates = generate_dates_for_month(year, month, num_orders)
        month_revenue = 0
        
        for i, date in enumerate(dates, 1):
            customer = get_random_customer()
            customer_group = next((c["group"] for c in CUSTOMERS if c["name"] == customer), "Khach Le")
            items = get_random_items(customer_group)
            
            try:
                result = create_so_with_dn_si(customer, items, date)
                month_revenue += result["grand_total"]
                total_orders += 1
                
                print(f"  [{i}] {date} | {result['so']} | {customer[:25]:<25} | {result['grand_total']:>15,.0f} VND")
                
                all_results.append(result)
                frappe.db.commit()
                
            except Exception as e:
                print(f"  [x] {date} | LOI: {str(e)[:50]}")
                frappe.db.rollback()
                continue
        
        total_revenue += month_revenue
        print(f"  >> Tong thang: {month_revenue:,.0f} VND")
    
    # Tổng kết
    print(f"\n{'='*70}")
    print("TONG KET")
    print(f"{'='*70}")
    print(f"Tong so don hang: {total_orders}")
    print(f"Tong doanh thu:   {total_revenue:,.0f} VND")
    print(f"{'='*70}\n")
    
    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "results": all_results
    }


def create_stock_for_new_orders():
    """
    Tạo stock entry để có đủ hàng cho các đơn mới
    Chạy trước khi tạo đơn hàng
    """
    from frappe.utils import add_days
    
    print("Tao Stock Entry nhap kho...")
    
    # Tính tổng số lượng cần (ước tính)
    # 55 đơn x trung bình 5 items x trung bình 20 qty = 5500 units mỗi loại
    
    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = "Material Receipt"
    se.company = COMPANY
    se.posting_date = "2025-06-30"  # Trước tháng 7
    se.posting_time = "08:00:00"
    se.set_posting_time = 1
    se.remarks = "Nhap kho cho demo T7-T11/2025"
    
    for item in ITEMS:
        se.append("items", {
            "item_code": item["code"],
            "qty": 2000,  # Nhập 2000 mỗi loại
            "uom": "Nos",
            "stock_uom": "Nos",
            "conversion_factor": 1,
            "t_warehouse": WAREHOUSE,
            "basic_rate": item["price"] * 0.6,  # Giá vốn = 60% giá bán
            "allow_zero_valuation_rate": 0
        })
    
    se.insert(ignore_permissions=True)
    se.submit()
    frappe.db.commit()
    
    print(f"Da tao Stock Entry: {se.name}")
    return se.name


# ========== CHAY ==========
# Buoc 1: Tao stock truoc
# create_stock_for_new_orders()

# Buoc 2: Tao don hang
# create_demo_sales_jul_nov_2025()
