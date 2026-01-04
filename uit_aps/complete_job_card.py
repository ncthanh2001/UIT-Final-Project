"""
Complete Job Cards cho tất cả Work Orders theo sequence_id
Có xử lý Workstation Overlap - tính toán thời gian theo từng Workstation

Cách sử dụng:
1. Copy file này vào: frappe-bench/apps/uit_aps/uit_aps/
2. Chạy lệnh:
   bench --site [site_name] execute uit_aps.complete_job_cards.complete_all_work_orders

Hoặc complete 1 Work Order cụ thể:
   bench --site [site_name] execute uit_aps.complete_job_cards.complete_work_order --kwargs "{'work_order': 'MFG-WO-2026-00005'}"
"""

import frappe
from frappe.utils import get_datetime, add_to_date, now_datetime


# Global dictionary để track thời gian kết thúc của từng Workstation
workstation_end_times = {}


def get_workstation_available_time(workstation, desired_start_time):
    """
    Lấy thời gian sớm nhất mà Workstation có thể bắt đầu công việc mới
    (phải sau thời gian kết thúc của job trước đó trên cùng Workstation)
    
    Args:
        workstation: Tên Workstation
        desired_start_time: Thời gian muốn bắt đầu
    
    Returns:
        datetime: Thời gian thực tế có thể bắt đầu
    """
    global workstation_end_times
    
    desired_start = get_datetime(desired_start_time)
    
    # Nếu workstation chưa có job nào, hoặc job trước đã kết thúc trước desired_start
    if workstation not in workstation_end_times:
        return desired_start
    
    ws_end_time = workstation_end_times[workstation]
    
    # Trả về max của desired_start và ws_end_time
    if ws_end_time > desired_start:
        return ws_end_time
    else:
        return desired_start


def update_workstation_end_time(workstation, end_time):
    """
    Cập nhật thời gian kết thúc của Workstation
    """
    global workstation_end_times
    
    end_dt = get_datetime(end_time)
    
    if workstation not in workstation_end_times:
        workstation_end_times[workstation] = end_dt
    else:
        # Cập nhật nếu end_time mới muộn hơn
        if end_dt > workstation_end_times[workstation]:
            workstation_end_times[workstation] = end_dt


def reset_workstation_tracker():
    """Reset tracker khi bắt đầu batch mới"""
    global workstation_end_times
    workstation_end_times = {}


def complete_work_order(work_order, start_time=None):
    """
    Complete tất cả Job Cards của 1 Work Order theo sequence_id
    Có xử lý Workstation Overlap
    
    Args:
        work_order: Tên Work Order (vd: "MFG-WO-2026-00005")
        start_time: Thời gian bắt đầu (string hoặc datetime), mặc định là now
    
    Returns:
        datetime: Thời gian kết thúc của Job Card cuối cùng
    """
    if not start_time:
        start_time = now_datetime()
    
    current_time = get_datetime(start_time)
    
    # Lấy tất cả Job Cards của Work Order
    job_cards = frappe.get_all("Job Card",
        filters={"work_order": work_order},
        fields=["name", "operation", "workstation", "for_quantity", "time_required", "sequence_id", "status"],
        order_by="sequence_id asc"
    )
    
    if not job_cards:
        print(f"❌ Không tìm thấy Job Cards cho {work_order}")
        return current_time
    
    print(f"\n{'='*70}")
    print(f"WORK ORDER: {work_order}")
    print(f"Số Job Cards: {len(job_cards)}")
    print(f"Bắt đầu mong muốn: {current_time}")
    print(f"{'='*70}")
    
    completed_count = 0
    skipped_count = 0
    last_end_time = current_time
    
    for jc in job_cards:
        doc = frappe.get_doc("Job Card", jc["name"])
        
        # Skip nếu đã completed
        if doc.status == "Completed":
            print(f"⚠️  Seq {jc['sequence_id']:>2}: {jc['name']} - Đã completed, skip")
            skipped_count += 1
            continue
        
        workstation = jc["workstation"]
        time_req = jc["time_required"] or 0
        
        # Tính thời gian bắt đầu thực tế (phải sau job trước của WO này VÀ sau job trước trên cùng Workstation)
        actual_start = get_workstation_available_time(workstation, last_end_time)
        end_time = add_to_date(actual_start, minutes=time_req)
        
        # Thêm Time Log
        doc.append("time_logs", {
            "from_time": actual_start,
            "to_time": end_time,
            "time_in_mins": time_req,
            "completed_qty": jc["for_quantity"]
        })
        
        # Save và Submit
        doc.save(ignore_permissions=True)
        doc.submit()
        
        # Cập nhật workstation tracker
        update_workstation_end_time(workstation, end_time)
        
        print(f"✅  Seq {jc['sequence_id']:>2}: {jc['operation'][:25]:<25} | {workstation[:20]:<20} | {time_req:>5}m | {str(actual_start)[:16]} → {str(end_time)[:16]}")
        
        last_end_time = end_time
        completed_count += 1
    
    frappe.db.commit()
    
    print(f"\n📊 Kết quả: {completed_count} completed, {skipped_count} skipped")
    print(f"🏁 Kết thúc lúc: {last_end_time}")
    
    return last_end_time


def complete_all_work_orders(start_time=None, work_orders=None):
    """
    Complete tất cả Job Cards của nhiều Work Orders
    Xử lý Workstation Overlap giữa các Work Orders
    
    Args:
        start_time: Thời gian bắt đầu (mặc định: "2026-01-06 07:30:00")
        work_orders: List Work Orders (mặc định: lấy tất cả WO đang In Process/Not Started)
    """
    if not start_time:
        start_time = "2026-01-06 07:30:00"
    
    # Reset workstation tracker
    reset_workstation_tracker()
    
    # Nếu không chỉ định, lấy tất cả Work Orders đang In Process hoặc Not Started
    if not work_orders:
        work_orders = frappe.get_all("Work Order",
            filters={"status": ["in", ["In Process", "Not Started"]], "docstatus": 1},
            fields=["name"],
            order_by="name asc"
        )
        work_orders = [wo["name"] for wo in work_orders]
    
    if not work_orders:
        print("❌ Không tìm thấy Work Orders nào!")
        return
    
    print(f"\n{'#'*70}")
    print(f"COMPLETE TẤT CẢ JOB CARDS (CÓ XỬ LÝ WORKSTATION OVERLAP)")
    print(f"Số Work Orders: {len(work_orders)}")
    print(f"Work Orders: {', '.join(work_orders)}")
    print(f"Thời gian bắt đầu: {start_time}")
    print(f"{'#'*70}")
    
    max_end_time = get_datetime(start_time)
    
    for wo in work_orders:
        # Mỗi WO bắt đầu từ start_time, nhưng workstation tracker sẽ xử lý overlap
        end_time = complete_work_order(wo, start_time)
        if end_time > max_end_time:
            max_end_time = end_time
    
    print(f"\n{'#'*70}")
    print(f"🎉 HOÀN THÀNH TẤT CẢ!")
    print(f"Tổng Work Orders: {len(work_orders)}")
    print(f"Makespan: {start_time} → {max_end_time}")
    print_workstation_summary()
    print(f"{'#'*70}")


def complete_work_orders_parallel(work_orders=None, start_time=None):
    """
    Complete nhiều Work Orders bắt đầu cùng 1 thời điểm (song song)
    Có xử lý Workstation Overlap
    
    Args:
        work_orders: List Work Orders
        start_time: Thời gian bắt đầu chung
    """
    if not start_time:
        start_time = "2026-01-06 07:30:00"
    
    if not work_orders:
        print("❌ Vui lòng chỉ định danh sách Work Orders!")
        return
    
    # Reset workstation tracker
    reset_workstation_tracker()
    
    print(f"\n{'#'*70}")
    print(f"COMPLETE SONG SONG (PARALLEL) - CÓ XỬ LÝ WORKSTATION OVERLAP")
    print(f"Số Work Orders: {len(work_orders)}")
    print(f"Thời gian bắt đầu chung: {start_time}")
    print(f"{'#'*70}")
    
    max_end_time = get_datetime(start_time)
    
    for wo in work_orders:
        end_time = complete_work_order(wo, start_time)
        if end_time > max_end_time:
            max_end_time = end_time
    
    print(f"\n{'#'*70}")
    print(f"🎉 HOÀN THÀNH!")
    print(f"Makespan: {start_time} → {max_end_time}")
    print_workstation_summary()
    print(f"{'#'*70}")


def print_workstation_summary():
    """In tóm tắt thời gian kết thúc của từng Workstation"""
    global workstation_end_times
    
    if not workstation_end_times:
        return
    
    print(f"\n📊 WORKSTATION SUMMARY:")
    print("-" * 50)
    
    sorted_ws = sorted(workstation_end_times.items(), key=lambda x: x[1], reverse=True)
    
    for ws, end_time in sorted_ws:
        print(f"  {ws[:30]:<30} → {str(end_time)[:16]}")


# =====================================================
# FUNCTIONS CHO TỪNG NHÓM DEMO
# =====================================================

def complete_group_a_sequential():
    """
    Complete Nhóm A - Tuần tự (Mặc định ERPNext)
    Work Orders chạy lần lượt, WO trước xong mới đến WO sau
    """
    work_orders = [
        "MFG-WO-2026-00005",  # Bàn LV Gỗ Sồi 120x60 - 20 cái
        "MFG-WO-2026-00006",  # Ghế Ăn Gỗ Căm - 30 cái
        "MFG-WO-2026-00007",  # Ghế VP Gỗ Sồi - 50 cái
    ]
    
    print("\n" + "="*70)
    print("NHÓM A - TUẦN TỰ (MẶC ĐỊNH ERPNEXT)")
    print("="*70)
    
    complete_all_work_orders(
        start_time="2026-01-06 07:30:00",
        work_orders=work_orders
    )


def complete_group_b_optimized():
    """
    Complete Nhóm B - Song song (Tối ưu APS)
    Work Orders bắt đầu cùng lúc, nhưng vẫn xử lý Workstation Overlap
    """
    work_orders = [
        "MFG-WO-2026-00008",  # Ghế Ăn Gỗ Căm - 40 cái
        "MFG-WO-2026-00009",  # Bàn LV Gỗ Sồi - 35 cái
        "MFG-WO-2026-00010",  # Tủ QA 3 Cánh MDF - 25 cái
    ]
    
    print("\n" + "="*70)
    print("NHÓM B - SONG SONG (TỐI ƯU APS)")
    print("="*70)
    
    complete_work_orders_parallel(
        work_orders=work_orders,
        start_time="2026-01-06 07:30:00"
    )


def complete_demo_comparison():
    """
    Complete cả 2 nhóm để so sánh
    """
    print("\n" + "#"*70)
    print("DEMO SO SÁNH APS: MẶC ĐỊNH vs TỐI ƯU")
    print("#"*70)
    
    complete_group_a_sequential()
    complete_group_b_optimized()
    
    print("\n" + "#"*70)
    print("🎉 HOÀN THÀNH DEMO!")
    print("#"*70)
