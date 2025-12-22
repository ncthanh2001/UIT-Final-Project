# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Data Helper Functions
Lay du lieu tu Sales Order de chay forecast models
"""

import frappe
from frappe.utils import add_days, getdate


def get_sales_order_items_for_item(
    item_code,
    company=None,
    start_date=None,
    end_date=None,
    warehouse=None,
):
    """
    Lay Sales Order Items cho mot item cu the

    Args:
        item_code: Item code can lay du lieu
        company: Filter theo company (optional)
        start_date: Ngay bat dau (optional)
        end_date: Ngay ket thuc (optional)
        warehouse: Filter theo warehouse (optional)

    Returns:
        List[dict]: Danh sach Sales Order Items
    """
    filters = {
        "item_code": item_code,
        "docstatus": 1,  # Chi lay Sales Orders da submit
    }

    # Add date filters
    date_filters = []
    if start_date:
        date_filters.append(["Sales Order", "transaction_date", ">=", start_date])
    if end_date:
        date_filters.append(["Sales Order", "transaction_date", "<=", end_date])

    # Add company filter
    if company:
        date_filters.append(["Sales Order", "company", "=", company])

    # Add warehouse filter
    if warehouse:
        filters["warehouse"] = warehouse

    # Query Sales Order Items
    items = frappe.get_all(
        "Sales Order Item",
        filters=filters,
        fields=[
            "name",
            "parent",
            "item_code",
            "item_name",
            "qty",
            "delivered_qty",
            "delivery_date",
            "warehouse",
            "rate",
            "amount",
        ],
        order_by="delivery_date asc",
    )

    # Get parent Sales Order info
    for item in items:
        so = frappe.get_cached_doc("Sales Order", item["parent"])
        item["transaction_date"] = so.transaction_date
        item["customer"] = so.customer
        item["company"] = so.company

    return items


def get_all_items_from_sales_orders(
    company=None,
    start_date=None,
    end_date=None,
    warehouse=None,
    item_group=None,
):
    """
    Lay tat ca items tu Sales Orders trong khoang thoi gian

    Args:
        company: Filter theo company (optional)
        start_date: Ngay bat dau (optional)
        end_date: Ngay ket thuc (optional)
        warehouse: Filter theo warehouse (optional)
        item_group: Filter theo item group (optional)

    Returns:
        List[str]: Danh sach item codes
    """
    filters = {"docstatus": 1}

    if company:
        filters["company"] = company

    if start_date:
        filters["transaction_date"] = [">=", start_date]

    if end_date:
        if "transaction_date" in filters:
            filters["transaction_date"] = ["between", [start_date, end_date]]
        else:
            filters["transaction_date"] = ["<=", end_date]

    # Get all Sales Orders in date range
    sales_orders = frappe.get_all(
        "Sales Order",
        filters=filters,
        fields=["name"],
    )

    if not sales_orders:
        return []

    # Get items from these Sales Orders
    so_names = [so.name for so in sales_orders]

    item_filters = {"parent": ["in", so_names]}

    if warehouse:
        item_filters["warehouse"] = warehouse

    items = frappe.get_all(
        "Sales Order Item",
        filters=item_filters,
        fields=["item_code"],
        distinct=True,
    )

    item_codes = [item.item_code for item in items]

    # Filter by item_group if provided
    if item_group and item_codes:
        item_codes = frappe.get_all(
            "Item",
            filters={"name": ["in", item_codes], "item_group": item_group},
            pluck="name",
        )

    return item_codes


def get_current_stock(item_code, warehouse=None):
    """
    Lay ton kho hien tai cua item

    Args:
        item_code: Item code
        warehouse: Warehouse (optional)

    Returns:
        float: So luong ton kho
    """
    if warehouse:
        stock = frappe.db.get_value(
            "Bin",
            {"item_code": item_code, "warehouse": warehouse},
            "actual_qty",
        )
        return float(stock or 0)
    else:
        # Get total stock across all warehouses
        stock = frappe.db.sql(
            """
            SELECT SUM(actual_qty)
            FROM `tabBin`
            WHERE item_code = %s
        """,
            (item_code,),
        )
        return float(stock[0][0] or 0) if stock else 0


def get_item_lead_time(item_code):
    """
    Lay lead time cua item

    Args:
        item_code: Item code

    Returns:
        int: Lead time in days
    """
    # Get lead_time_days from Item doctype
    lead_time = frappe.db.get_value("Item", item_code, "lead_time_days")

    if lead_time and lead_time > 0:
        return int(lead_time)

    # Default to 14 days if not specified
    return 14


def validate_sales_order_data(sales_order_items, min_records=10):
    """
    Validate xem du lieu Sales Order co du de chay forecast khong

    Args:
        sales_order_items: List of Sales Order Items
        min_records: So ban ghi toi thieu

    Returns:
        tuple: (is_valid, error_message)
    """
    if not sales_order_items:
        return False, "No sales order data found"

    if len(sales_order_items) < min_records:
        return (
            False,
            f"Insufficient data. Need at least {min_records} records, got {len(sales_order_items)}",
        )

    # Check if data has qty
    if not any(item.get("qty", 0) > 0 for item in sales_order_items):
        return False, "No valid quantity data found"

    # Check if data has dates
    if not any(
        item.get("delivery_date") or item.get("transaction_date")
        for item in sales_order_items
    ):
        return False, "No valid date data found"

    return True, None
