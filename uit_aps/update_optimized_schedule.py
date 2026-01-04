"""
APS Optimization: Đổi Workstation cho Nhóm B trước khi Submit
=============================================================
Sử dụng frappe.db.set_value để bypass Work Order validation

Nhóm A (Mặc định): WO-05, WO-07 - Giữ nguyên, dùng máy 01
Nhóm B (Tối ưu):   WO-06, WO-08 - Đổi sang máy 02 để chạy song song

Cách sử dụng:
1. Copy file vào: frappe-bench/apps/uit_aps/uit_aps/
2. Chạy: bench execute uit_aps.optimize_workstations_v2.optimize_group_b
"""

import frappe


# Mapping đổi Workstation: Máy 01 → Máy 02
WORKSTATION_MAPPING = {
    # Máy cắt
    "May Cat Panel Saw 01": "May Cat Panel Saw 02",
    
    # Máy phay - dùng máy khác
    "May Phay Tay 01": "May Phay CNC 01",
    "May Phay CNC 02": "May Phay CNC 01",
    
    # Bàn lắp ráp
    "Ban Lap Rap 01": "Ban Lap Rap 02",
    "Ban Lap Rap 03": "Ban Lap Rap 04",
    
    # Bàn QC
    "Ban QC 02": "Ban QC 01",
    
    # Bàn đóng gói
    "Ban Dong Goi 01": "Ban Dong Goi 02",
}


def optimize_work_order(work_order_name):
    """
    Đổi Workstation cho 1 Work Order bằng cách update trực tiếp database
    Bypass Work Order validation
    """
    # Kiểm tra Work Order
    wo = frappe.get_doc("Work Order", work_order_name)
    
    if wo.docstatus != 0:
        print(f"❌ {work_order_name}: Không thể sửa vì đã Submit (docstatus={wo.docstatus})")
        return False
    
    print(f"\n{'='*60}")
    print(f"WORK ORDER: {work_order_name}")
    print(f"Sản phẩm: {wo.item_name}")
    print(f"Số lượng: {wo.qty}")
    print(f"Số Operations: {len(wo.operations)}")
    print(f"{'='*60}")
    
    changed_count = 0
    
    # Lấy danh sách operations từ child table
    operations = frappe.get_all(
        "Work Order Operation",
        filters={"parent": work_order_name},
        fields=["name", "idx", "operation", "workstation"],
        order_by="idx asc"
    )
    
    for op in operations:
        old_ws = op["workstation"]
        
        if old_ws in WORKSTATION_MAPPING:
            new_ws = WORKSTATION_MAPPING[old_ws]
            
            # Update trực tiếp vào database, bypass validation
            frappe.db.set_value(
                "Work Order Operation",
                op["name"],
                "workstation",
                new_ws,
                update_modified=False
            )
            
            changed_count += 1
            print(f"✅ Op {op['idx']:>2}: {op['operation'][:25]:<25} | {old_ws} → {new_ws}")
        else:
            print(f"⏸️  Op {op['idx']:>2}: {op['operation'][:25]:<25} | {old_ws} (giữ nguyên)")
    
    print(f"\n📊 Đã đổi {changed_count}/{len(operations)} operations")
    return True


def optimize_group_b():
    """
    Tối ưu Workstation cho Nhóm B: WO-06 và WO-08
    """
    group_b = ["MFG-WO-2026-00006", "MFG-WO-2026-00008"]
    
    print("\n" + "#"*60)
    print("APS OPTIMIZATION: ĐỔI WORKSTATION CHO NHÓM B")
    print("#"*60)
    print(f"\nNhóm B: {', '.join(group_b)}")
    print("Mục tiêu: Đổi sang máy khác để chạy song song với Nhóm A")
    
    for wo in group_b:
        optimize_work_order(wo)
    
    frappe.db.commit()
    
    print("\n" + "#"*60)
    print("🎉 HOÀN THÀNH!")
    print("#"*60)
    print("""
BƯỚC TIẾP THEO:
1. Submit tất cả 4 Work Orders (WO-05, WO-06, WO-07, WO-08)
2. Kiểm tra Gantt Chart của Job Cards
3. So sánh Makespan giữa Nhóm A và Nhóm B

KỲ VỌNG:
- Nhóm A (WO-05, WO-07): Dùng máy 01
- Nhóm B (WO-06, WO-08): Dùng máy 02
- Nhóm B sẽ hoàn thành NHANH HƠN vì không phải chờ máy của Nhóm A
""")


def show_workstation_comparison():
    """
    Hiển thị so sánh Workstation giữa 2 nhóm
    """
    print("\n" + "="*80)
    print("SO SÁNH WORKSTATION GIỮA NHÓM A VÀ NHÓM B")
    print("="*80)
    
    work_orders = {
        "MFG-WO-2026-00005": "A",
        "MFG-WO-2026-00006": "B", 
        "MFG-WO-2026-00007": "A",
        "MFG-WO-2026-00008": "B"
    }
    
    for wo_name, group in work_orders.items():
        operations = frappe.get_all(
            "Work Order Operation",
            filters={"parent": wo_name},
            fields=["operation", "workstation"],
            order_by="idx asc"
        )
        
        wo = frappe.get_doc("Work Order", wo_name)
        group_label = "Mặc định" if group == "A" else "Tối ưu"
        
        print(f"\n📦 {wo_name} - Nhóm {group} ({group_label})")
        print(f"   Sản phẩm: {wo.item_name}")
        
        # Lấy unique workstations
        ws_set = set()
        for op in operations:
            ws_set.add(op["workstation"])
        
        print(f"   Workstations ({len(ws_set)}):")
        for ws in sorted(ws_set):
            print(f"     - {ws}")


def reset_group_b():
    """
    Reset Workstation của Nhóm B về mặc định (giống Nhóm A)
    """
    # Mapping ngược lại
    REVERSE_MAPPING = {v: k for k, v in WORKSTATION_MAPPING.items()}
    
    group_b = ["MFG-WO-2026-00006", "MFG-WO-2026-00008"]
    
    print("\n" + "#"*60)
    print("RESET WORKSTATION CHO NHÓM B VỀ MẶC ĐỊNH")
    print("#"*60)
    
    for wo_name in group_b:
        wo = frappe.get_doc("Work Order", wo_name)
        
        if wo.docstatus != 0:
            print(f"❌ {wo_name}: Không thể sửa vì đã Submit")
            continue
        
        operations = frappe.get_all(
            "Work Order Operation",
            filters={"parent": wo_name},
            fields=["name", "workstation"]
        )
        
        for op in operations:
            if op["workstation"] in REVERSE_MAPPING:
                frappe.db.set_value(
                    "Work Order Operation",
                    op["name"],
                    "workstation",
                    REVERSE_MAPPING[op["workstation"]],
                    update_modified=False
                )
        
        print(f"✅ {wo_name}: Đã reset về mặc định")
    
    frappe.db.commit()
    print("\n🎉 Hoàn thành reset!")
