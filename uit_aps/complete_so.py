"""
Script tạo Delivery Note và Sales Invoice cho tất cả Sales Order chưa hoàn thành
Version 2: Sửa lỗi import

Cách chạy trong bench console:
1. bench --site [sitename] console
2. Copy paste toàn bộ script này vào console
3. Gọi: complete_all_sales_orders()
"""

import frappe
from frappe.utils import today, nowtime

# Import các hàm tạo DN và SI từ ERPNext
from erpnext.selling.doctype.sales_order.sales_order import (
    make_delivery_note,
    make_sales_invoice,
)


def complete_all_sales_orders():
    """
    Tạo Delivery Note và Sales Invoice cho tất cả Sales Order
    có per_delivered = 0 và per_billed = 0
    """

    # Lấy tất cả SO cần xử lý
    sales_orders = frappe.get_all(
        "Sales Order",
        filters={
            "docstatus": 1,
            "per_delivered": 0,
            "per_billed": 0,
            "status": ["not in", ["Closed", "Cancelled"]],
        },
        fields=["name", "customer", "transaction_date", "grand_total"],
        order_by="transaction_date asc",
    )

    total = len(sales_orders)
    success_count = 0
    error_count = 0
    errors = []

    print(f"\n{'='*60}")
    print(f"BAT DAU XU LY {total} SALES ORDER")
    print(f"{'='*60}\n")

    for idx, so in enumerate(sales_orders, 1):
        so_name = so.name
        print(f"[{idx}/{total}] Dang xu ly: {so_name} - {so.customer}")

        try:
            # ========== BƯỚC 1: Tạo Delivery Note ==========
            dn_doc = make_delivery_note(so_name)
            dn_doc.posting_date = so.transaction_date  # Dùng ngày của SO
            dn_doc.posting_time = nowtime()
            dn_doc.set_posting_time = 1

            # Đảm bảo tất cả items có warehouse
            for item in dn_doc.items:
                if not item.warehouse:
                    item.warehouse = (
                        frappe.db.get_single_value(
                            "Stock Settings", "default_warehouse"
                        )
                        or "Kho Thanh Pham - BM"
                    )

            dn_doc.insert(ignore_permissions=True)
            dn_doc.submit()
            print(f"    + Da tao DN: {dn_doc.name}")

            # ========== BƯỚC 2: Tạo Sales Invoice ==========
            si_doc = make_sales_invoice(so_name)
            si_doc.posting_date = so.transaction_date  # Dùng ngày của SO
            si_doc.posting_time = nowtime()
            si_doc.set_posting_time = 1
            si_doc.update_stock = 0  # Không cập nhật stock vì đã có DN

            # Link với Delivery Note vừa tạo
            for si_item in si_doc.items:
                # Tìm item tương ứng trong DN
                for dn_item in dn_doc.items:
                    if (
                        si_item.item_code == dn_item.item_code
                        and si_item.so_detail == dn_item.so_detail
                    ):
                        si_item.delivery_note = dn_doc.name
                        si_item.dn_detail = dn_item.name
                        break

            si_doc.insert(ignore_permissions=True)
            si_doc.submit()
            print(f"    + Da tao SI: {si_doc.name}")

            # Commit sau mỗi SO để tránh mất data nếu lỗi
            frappe.db.commit()
            success_count += 1
            print(f"    + Hoan thanh SO: {so_name}")

        except Exception as e:
            error_count += 1
            error_msg = f"{so_name}: {str(e)}"
            errors.append(error_msg)
            print(f"    x LOI: {str(e)}")
            frappe.db.rollback()
            continue

    # ========== KẾT QUẢ ==========
    print(f"\n{'='*60}")
    print("KET QUA XU LY")
    print(f"{'='*60}")
    print(f"Tong SO: {total}")
    print(f"Thanh cong: {success_count}")
    print(f"Loi: {error_count}")

    if errors:
        print(f"\nDanh sach loi:")
        for err in errors[:20]:  # Chỉ hiện 20 lỗi đầu
            print(f"  - {err}")
        if len(errors) > 20:
            print(f"  ... va {len(errors) - 20} loi khac")

    print(f"\n{'='*60}")
    print("HOAN TAT!")
    print(f"{'='*60}\n")

    return {
        "total": total,
        "success": success_count,
        "errors": error_count,
        "error_list": errors,
    }


def complete_single_so(so_name):
    """
    Xử lý một Sales Order cụ thể
    Dùng để test hoặc xử lý lại SO bị lỗi
    """
    so = frappe.get_doc("Sales Order", so_name)

    print(f"Xu ly SO: {so_name}")
    print(f"  Customer: {so.customer}")
    print(f"  Grand Total: {so.grand_total:,.0f} VND")

    # Tạo DN
    dn_doc = make_delivery_note(so_name)
    dn_doc.posting_date = so.transaction_date
    dn_doc.posting_time = nowtime()
    dn_doc.set_posting_time = 1

    for item in dn_doc.items:
        if not item.warehouse:
            item.warehouse = "Kho Thanh Pham - BM"

    dn_doc.insert(ignore_permissions=True)
    dn_doc.submit()
    print(f"  + DN: {dn_doc.name}")

    # Tạo SI
    si_doc = make_sales_invoice(so_name)
    si_doc.posting_date = so.transaction_date
    si_doc.posting_time = nowtime()
    si_doc.set_posting_time = 1
    si_doc.update_stock = 0

    for si_item in si_doc.items:
        for dn_item in dn_doc.items:
            if (
                si_item.item_code == dn_item.item_code
                and si_item.so_detail == dn_item.so_detail
            ):
                si_item.delivery_note = dn_doc.name
                si_item.dn_detail = dn_item.name
                break

    si_doc.insert(ignore_permissions=True)
    si_doc.submit()
    print(f"  + SI: {si_doc.name}")

    frappe.db.commit()
    print(f"  + Hoan thanh!")

    return {"dn": dn_doc.name, "si": si_doc.name}


# ========== CHẠY NGAY KHI PASTE VÀO CONSOLE ==========
# Bỏ comment dòng dưới nếu muốn chạy tự động
# complete_all_sales_orders()
