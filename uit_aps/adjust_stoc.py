"""
Script điều chỉnh tồn kho thành phẩm về mức 20-100 units
Tạo Stock Entry (Material Issue) để xuất bớt hàng

Cách chạy:
1. bench --site [sitename] console
2. Copy paste toàn bộ script
3. Gọi: adjust_stock_to_normal()
"""

import frappe
from frappe.utils import today, nowtime
import random

def adjust_stock_to_normal():
    """
    Điều chỉnh tồn kho về mức 20-100 units cho mỗi sản phẩm
    """
    
    # Lấy tồn kho hiện tại
    bins = frappe.db.sql("""
        SELECT item_code, warehouse, actual_qty
        FROM `tabBin`
        WHERE item_code LIKE 'TP-%%'
        AND actual_qty > 0
        ORDER BY item_code
    """, as_dict=True)
    
    if not bins:
        print("Khong co ton kho nao!")
        return
    
    print(f"\n{'='*60}")
    print("DIEU CHINH TON KHO VE MUC 20-100 UNITS")
    print(f"{'='*60}\n")
    
    company = frappe.db.get_single_value("Global Defaults", "default_company") or "Bear Manufacturing"
    
    # Tạo Stock Entry - Material Issue để xuất bớt
    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = "Material Issue"
    se.company = company
    se.posting_date = today()
    se.posting_time = nowtime()
    se.set_posting_time = 1
    se.remarks = "Dieu chinh ton kho ve muc hop ly - Stock Adjustment"
    
    total_reduced = 0
    
    print(f"{'Item':<15} | {'Hien tai':>10} | {'Muc tieu':>10} | {'Xuat bot':>10}")
    print("-" * 55)
    
    for b in bins:
        current_qty = b.actual_qty
        # Mục tiêu: random từ 20-100
        target_qty = random.randint(20, 100)
        
        if current_qty > target_qty:
            qty_to_reduce = current_qty - target_qty
            
            # Lấy valuation rate
            valuation_rate = frappe.db.get_value("Item", b.item_code, "valuation_rate") or 0
            if not valuation_rate:
                # Lấy từ Bin
                valuation_rate = frappe.db.get_value("Bin", 
                    {"item_code": b.item_code, "warehouse": b.warehouse}, 
                    "valuation_rate") or 1000000
            
            se.append("items", {
                "item_code": b.item_code,
                "qty": qty_to_reduce,
                "s_warehouse": b.warehouse,
                "basic_rate": valuation_rate,
                "uom": "Nos",
                "stock_uom": "Nos",
                "conversion_factor": 1
            })
            
            total_reduced += qty_to_reduce
            print(f"{b.item_code:<15} | {current_qty:>10,.0f} | {target_qty:>10} | {qty_to_reduce:>10,.0f}")
    
    print("-" * 55)
    print(f"{'TONG':>15} | {'':<10} | {'':<10} | {total_reduced:>10,.0f}")
    
    if not se.items:
        print("\nKhong can dieu chinh!")
        return
    
    try:
        se.insert(ignore_permissions=True)
        se.submit()
        frappe.db.commit()
        
        print(f"\n[OK] Da tao Stock Entry: {se.name}")
        print(f"[OK] Da xuat bot {total_reduced:,.0f} units")
        
        # Kiểm tra lại tồn kho
        print(f"\n{'='*60}")
        print("TON KHO SAU DIEU CHINH")
        print(f"{'='*60}\n")
        
        new_bins = frappe.db.sql("""
            SELECT item_code, actual_qty
            FROM `tabBin`
            WHERE item_code LIKE 'TP-%%'
            ORDER BY item_code
        """, as_dict=True)
        
        for nb in new_bins:
            print(f"{nb.item_code}: {nb.actual_qty:,.0f} units")
        
        return se.name
        
    except Exception as e:
        frappe.db.rollback()
        print(f"\n[LOI] {str(e)}")
        raise e


def check_current_stock():
    """Kiểm tra tồn kho hiện tại"""
    bins = frappe.db.sql("""
        SELECT item_code, warehouse, actual_qty
        FROM `tabBin`
        WHERE item_code LIKE 'TP-%%'
        ORDER BY item_code
    """, as_dict=True)
    
    print("\n=== TON KHO HIEN TAI ===\n")
    for b in bins:
        status = "OK" if 20 <= b.actual_qty <= 100 else "CAO" if b.actual_qty > 100 else "THAP"
        print(f"{b.item_code}: {b.actual_qty:>8,.0f} units | {status}")


# ========== CHAY ==========
# check_current_stock()
# adjust_stock_to_normal()
