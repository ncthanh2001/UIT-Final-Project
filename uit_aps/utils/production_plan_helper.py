# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Production Plan Helper Functions
Cac ham helper de tinh toan va xu ly Production Plan
"""

import frappe
from frappe import _
from frappe.utils import getdate, add_days, add_months, get_first_day, get_last_day


def calculate_planned_qty(forecast_qty, current_stock, safety_stock):
    """
    Tinh so luong san xuat can thiet dua tren forecast, current stock va safety stock
    
    Args:
        forecast_qty: So luong du bao (tu Forecast Result)
        current_stock: Ton kho hien tai
        safety_stock: Ton kho an toan
    
    Returns:
        float: So luong can san xuat
    """
    # Tinh nhu cau thuc te (forecast - current stock)
    net_demand = forecast_qty - current_stock
    
    # Neu da du ton kho, chi can giu safety stock
    if net_demand <= 0:
        planned_qty = max(safety_stock, 0)
    else:
        # Can san xuat = net demand + safety stock
        planned_qty = net_demand + safety_stock
    
    return max(planned_qty, 0)  # Khong am


def get_item_lead_time(item_code):
    """
    Lay lead time cua item (days)
    
    Args:
        item_code: Item code
    
    Returns:
        float: Lead time in days
    """
    try:
        item = frappe.get_doc("Item", item_code)
        # Lay tu Item hoac Item Default
        lead_time = item.lead_time_days or 0
        if not lead_time:
            # Thu lay tu Item Default
            item_defaults = frappe.get_all(
                "Item Default",
                filters={"parent": item_code},
                fields=["lead_time_days"],
                limit=1
            )
            if item_defaults:
                lead_time = item_defaults[0].lead_time_days or 0
        return float(lead_time)
    except Exception:
        return 0


def calculate_planned_start_date(period_start, lead_time_days):
    """
    Tinh ngay bat dau san xuat (tru lead time)
    
    Args:
        period_start: Ngay bat dau cua period
        lead_time_days: So ngay lead time
    
    Returns:
        date: Ngay bat dau san xuat
    """
    if lead_time_days and lead_time_days > 0:
        start_date = add_days(period_start, -int(lead_time_days))
        return start_date
    return period_start


def get_monthly_periods(start_date, end_date):
    """
    Lay danh sach cac thang trong period
    
    Args:
        start_date: Ngay bat dau
        end_date: Ngay ket thuc
    
    Returns:
        list: List of tuples (period_start, period_end)
    """
    periods = []
    current = get_first_day(start_date)
    end_date = getdate(end_date)
    start_date = getdate(start_date)
    
    while current <= end_date:
        period_start = max(current, start_date)
        period_end = min(get_last_day(current), end_date)
        periods.append((period_start, period_end))
        current = add_months(current, 1)
    
    return periods


def get_quarterly_periods(start_date, end_date):
    """
    Lay danh sach cac quy trong period
    
    Args:
        start_date: Ngay bat dau
        end_date: Ngay ket thuc
    
    Returns:
        list: List of tuples (period_start, period_end)
    """
    periods = []
    start_date = getdate(start_date)
    end_date = getdate(end_date)
    
    # Tinh quy dau tien
    quarter_start_month = ((start_date.month - 1) // 3) * 3 + 1
    current = getdate(f"{start_date.year}-{quarter_start_month:02d}-01")
    
    while current <= end_date:
        # Tinh ngay ket thuc quy
        quarter_end_month = quarter_start_month + 2
        quarter_end_year = current.year
        
        # Tinh period start va end
        period_start = max(current, start_date)
        
        # Tinh ngay cuoi cung cua quy
        if quarter_end_month == 12:
            quarter_last_day = getdate(f"{quarter_end_year}-12-31")
        else:
            quarter_last_day = get_last_day(f"{quarter_end_year}-{quarter_end_month:02d}-01")
        
        period_end = min(quarter_last_day, end_date)
        
        periods.append((period_start, period_end))
        
        # Chuyen sang quy tiep theo
        if quarter_end_month == 12:
            current = getdate(f"{current.year + 1}-01-01")
            quarter_start_month = 1
        else:
            current = getdate(f"{current.year}-{quarter_end_month + 1:02d}-01")
            quarter_start_month = quarter_end_month + 1
    
    return periods


def find_closest_forecast_result(results, target_date):
    """
    Tim forecast result gan nhat voi target_date
    
    Args:
        results: List of forecast result dicts
        target_date: Target date
    
    Returns:
        dict: Closest forecast result or None
    """
    if not results:
        return None
    
    closest = None
    min_diff = float('inf')
    target_date = getdate(target_date)
    
    for result in results:
        result_date = getdate(result.get("forecast_period"))
        diff = abs((target_date - result_date).days)
        if diff < min_diff:
            min_diff = diff
            closest = result
    
    return closest


def get_current_stock(item_code, warehouse=None):
    """
    Lay ton kho hien tai cua item
    
    Args:
        item_code: Item code
        warehouse: Warehouse (optional)
    
    Returns:
        float: Current stock quantity
    """
    try:
        filters = {"item_code": item_code}
        if warehouse:
            filters["warehouse"] = warehouse
        
        bins = frappe.get_all(
            "Bin",
            filters=filters,
            fields=["sum(actual_qty) as actual_qty"],
        )
        
        if bins and bins[0].actual_qty:
            return float(bins[0].actual_qty)
        return 0.0
    except Exception:
        return 0.0

