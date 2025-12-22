"""
Script tạo Stock Entry (Material Receipt) để nhập kho thành phẩm
Chạy script này TRƯỚC KHI chạy complete_sales_orders

Cách chạy:
1. bench --site [sitename] console
2. Copy paste toàn bộ script này vào console
3. Gọi: create_stock_for_demo()
"""

import frappe
from frappe.utils import today, nowdate, flt

def create_stock_for_demo():
    """
    Tạo Stock Entry nhập kho cho tất cả sản phẩm cần giao trong SO
    Nhập số lượng = qty_needed * 1.2 (dư 20% để an toàn)
    """
    
    # Lấy số lượng cần giao theo item
    items_needed = frappe.db.sql("""
        SELECT 
            soi.item_code,
            soi.item_name,
            soi.warehouse,
            SUM(soi.qty - soi.delivered_qty) as qty_needed
        FROM `tabSales Order Item` soi
        INNER JOIN `tabSales Order` so ON so.name = soi.parent
        WHERE so.docstatus = 1 
            AND so.per_delivered < 100
            AND so.status NOT IN ('Closed', 'Cancelled')
        GROUP BY soi.item_code, soi.warehouse
        ORDER BY qty_needed DESC
    """, as_dict=True)
    
    if not items_needed:
        print("Khong co item nao can nhap kho!")
        return
    
    print(f"\n{'='*60}")
    print(f"TAO STOCK ENTRY NHAP KHO CHO {len(items_needed)} ITEMS")
    print(f"{'='*60}\n")
    
    # Lấy thông tin company
    company = frappe.db.get_single_value("Global Defaults", "default_company") or "Bear Manufacturing"
    
    # Lấy ngày posting - dùng ngày đầu tiên của SO để có stock từ đầu
    earliest_so_date = frappe.db.sql("""
        SELECT MIN(transaction_date) as min_date
        FROM `tabSales Order`
        WHERE docstatus = 1 AND per_delivered < 100
    """, as_dict=True)
    
    posting_date = earliest_so_date[0].min_date if earliest_so_date else today()
    # Lùi thêm 1 ngày để đảm bảo có stock trước SO
    from datetime import timedelta
    posting_date = (posting_date - timedelta(days=1)).strftime('%Y-%m-%d') if posting_date else today()
    
    print(f"Company: {company}")
    print(f"Posting Date: {posting_date}")
    print(f"Warehouse: Kho Thanh Pham - BM\n")
    
    # Tạo Stock Entry - Material Receipt
    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = "Material Receipt"
    se.company = company
    se.posting_date = posting_date
    se.posting_time = "08:00:00"
    se.set_posting_time = 1
    se.remarks = "Nhap kho thanh pham cho demo - Auto generated"
    
    total_value = 0
    
    for item in items_needed:
        # Nhập 120% số lượng cần để dư
        qty_to_receive = flt(item.qty_needed * 1.2, 0)
        
        # Lấy valuation rate từ Item hoặc dùng mặc định
        valuation_rate = frappe.db.get_value("Item", item.item_code, "valuation_rate") or 0
        if not valuation_rate:
            # Lấy từ last purchase rate hoặc standard rate
            valuation_rate = frappe.db.get_value("Item", item.item_code, "last_purchase_rate") or \
                           frappe.db.get_value("Item", item.item_code, "standard_rate") or 1000000
        
        se.append("items", {
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": qty_to_receive,
            "uom": "Nos",
            "stock_uom": "Nos",
            "conversion_factor": 1,
            "t_warehouse": item.warehouse or "Kho Thanh Pham - BM",
            "basic_rate": valuation_rate,
            "valuation_rate": valuation_rate,
            "allow_zero_valuation_rate": 0 if valuation_rate else 1
        })
        
        item_value = qty_to_receive * valuation_rate
        total_value += item_value
        
        print(f"  + {item.item_code}: {qty_to_receive:,.0f} units @ {valuation_rate:,.0f} = {item_value:,.0f} VND")
    
    print(f"\n{'='*60}")
    print(f"TONG GIA TRI NHAP KHO: {total_value:,.0f} VND")
    print(f"{'='*60}\n")
    
    try:
        se.insert(ignore_permissions=True)
        se.submit()
        frappe.db.commit()
        
        print(f"[OK] Da tao Stock Entry: {se.name}")
        print(f"[OK] Trang thai: Submitted")
        print(f"\nBay gio ban co the chay lai script complete_sales_orders!")
        
        return se.name
        
    except Exception as e:
        frappe.db.rollback()
        print(f"[LOI] Khong the tao Stock Entry: {str(e)}")
        raise e


def check_stock_balance():
    """
    Kiểm tra tồn kho hiện tại của các sản phẩm thành phẩm
    """
    stock = frappe.db.sql("""
        SELECT 
            item_code,
            warehouse,
            SUM(actual_qty) as qty
        FROM `tabBin`
        WHERE warehouse = 'Kho Thanh Pham - BM'
        GROUP BY item_code
        ORDER BY item_code
    """, as_dict=True)
    
    print("\n=== TON KHO HIEN TAI - Kho Thanh Pham ===\n")
    print(f"{'Item Code':<20} {'Qty':>15}")
    print("-" * 40)
    
    for s in stock:
        print(f"{s.item_code:<20} {s.qty:>15,.0f}")
    
    if not stock:
        print("(Chua co ton kho)")
    
    return stock


# ========== CHẠY ==========
# create_stock_for_demo()
# check_stock_balance()
