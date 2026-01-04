# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
MRP Helper Functions
Cac ham helper de tinh toan MRP, BOM, supplier optimization
"""

import frappe
from frappe import _
from frappe.utils import getdate, add_days, flt
from collections import defaultdict


def get_bom_for_item(item_code, company=None):
    """
    Lay BOM cho item (default BOM hoac active BOM)
    
    Args:
        item_code: Item code
        company: Company (optional)
    
    Returns:
        str: BOM name hoac None
    """
    try:
        item = frappe.get_doc("Item", item_code)
        
        # Lay default BOM
        if item.default_bom:
            bom = frappe.get_doc("BOM", item.default_bom)
            if bom.is_active and bom.docstatus == 1:
                return bom.name
        
        # Tim active BOM
        filters = {
            "item": item_code,
            "is_active": 1,
            "docstatus": 1,
        }
        if company:
            filters["company"] = company
        
        boms = frappe.get_all(
            "BOM",
            filters=filters,
            fields=["name", "is_default"],
            order_by="is_default desc, creation desc",
            limit=1,
        )
        
        if boms:
            return boms[0].name
        
        return None
    except Exception:
        return None


def get_exploded_bom_items(bom_name, qty=1, include_non_stock_items=False):
    """
    Lay tat ca items trong BOM (exploded - bao gom sub-assemblies)
    
    Args:
        bom_name: BOM name
        qty: So luong san pham can san xuat
        include_non_stock_items: Co bao gom non-stock items khong
    
    Returns:
        list: List of dicts voi item_code, qty, uom, etc.
    """
    try:
        from erpnext.manufacturing.doctype.bom.bom import get_bom_items_as_dict
        
        bom = frappe.get_doc("BOM", bom_name)
        company = bom.company
        
        # Su dung ERPNext function de lay exploded BOM
        items_dict = get_bom_items_as_dict(
            bom=bom_name,
            company=company,
            qty=qty,
            fetch_exploded=1,  # Exploded BOM
            fetch_scrap_items=0,
            include_non_stock_items=include_non_stock_items,
        )
        
        # Convert dict sang list
        items = []
        for item_code, item_data in items_dict.items():
            items.append({
                "item_code": item_code,
                "qty": flt(item_data.get("qty", 0)),
                "stock_uom": item_data.get("stock_uom"),
                "item_name": item_data.get("item_name"),
                "warehouse": item_data.get("default_warehouse"),
            })
        
        return items
    except Exception as e:
        frappe.log_error(f"Error getting exploded BOM items: {str(e)}", "MRP Helper Error")
        return []


def get_current_stock(item_code, warehouse=None):
    """
    Lay ton kho hien tai cua item
    
    Args:
        item_code: Item code
        warehouse: Warehouse (optional, neu None thi lay tong ton kho)
    
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


def get_optimal_supplier(item_code, required_qty, required_date, company=None):
    """
    Tim supplier toi uu cho item (toi uu theo gia va lead time)
    
    Args:
        item_code: Item code
        required_qty: So luong can mua
        required_date: Ngay can co
        company: Company
    
    Returns:
        dict: Supplier info voi supplier, unit_price, lead_time, score
    """
    try:
        # 1. Lay suppliers tu Item Supplier
        item_suppliers = frappe.get_all(
            "Item Supplier",
            filters={"parent": item_code},
            fields=["supplier", "supplier_part_no"],
        )
        
        if not item_suppliers:
            return None
        
        suppliers_data = []
        suppliers_without_info = []  # Suppliers khong co du thong tin
        
        for item_supplier in item_suppliers:
            supplier = item_supplier.supplier
            
            # 2. Lay gia tu Item Price hoac Supplier Quotation
            unit_price = get_supplier_price(item_code, supplier, company)
            
            # 3. Lay lead time
            lead_time = get_supplier_lead_time(item_code, supplier)
            
            # 4. Neu co du ca gia va lead time, tinh score
            if unit_price and lead_time:
                # Normalize score (gia thap hon = score cao hon, lead time ngan hon = score cao hon)
                # Gia su max price = 1000000, max lead time = 365
                max_price = 1000000
                max_lead_time = 365
                
                price_score = (1 / (unit_price / max_price)) if unit_price > 0 else 0
                lead_time_score = (1 / (lead_time / max_lead_time)) if lead_time > 0 else 0
                
                # Weight: gia quan trong hon (60%), lead time (40%)
                total_score = (price_score * 0.6) + (lead_time_score * 0.4)
                
                suppliers_data.append({
                    "supplier": supplier,
                    "unit_price": unit_price,
                    "lead_time": lead_time,
                    "score": total_score,
                    "total_cost": unit_price * required_qty,
                })
            else:
                # Luu supplier khong co du thong tin (se dung sau neu khong co supplier nao co du thong tin)
                suppliers_without_info.append({
                    "supplier": supplier,
                    "unit_price": unit_price,
                    "lead_time": lead_time,
                    "score": 0,  # Khong co score
                })
        
        # 5. Neu co suppliers voi du thong tin, chon toi uu
        if suppliers_data:
            suppliers_data.sort(key=lambda x: x["score"], reverse=True)
            return suppliers_data[0]  # Tra ve supplier toi uu nhat
        
        # 6. Neu khong co supplier nao co du thong tin, tra ve supplier dau tien (neu co)
        if suppliers_without_info:
            # Tra ve supplier dau tien, co the khong co gia hoac lead_time
            return suppliers_without_info[0]
        
        # 7. Khong co supplier nao
        return None
    
    except Exception as e:
        frappe.log_error(f"Error getting optimal supplier: {str(e)}", "MRP Helper Error")
        return None


def get_supplier_price(item_code, supplier, company=None):
    """
    Lay gia cua item tu supplier
    
    Args:
        item_code: Item code
        supplier: Supplier name
        company: Company
    
    Returns:
        float: Unit price hoac None
    """
    try:
        # 1. Thu lay tu Item Price (supplier-specific)
        item_price = frappe.get_all(
            "Item Price",
            filters={
                "item_code": item_code,
                "supplier": supplier,
                "buying": 1,
            },
            fields=["price_list_rate"],
            order_by="valid_from desc",
            limit=1,
        )
        
        if item_price and item_price[0].price_list_rate:
            return float(item_price[0].price_list_rate)
        
        # 2. Thu lay tu Supplier Quotation (gan day nhat)
        sq_items = frappe.get_all(
            "Supplier Quotation Item",
            filters={
                "item_code": item_code,
                "parent": ["in", frappe.get_all(
                    "Supplier Quotation",
                    filters={"supplier": supplier, "docstatus": 1},
                    fields=["name"],
                    limit=10,
                )],
            },
            fields=["rate"],
            order_by="parent desc",
            limit=1,
        )
        
        if sq_items and sq_items[0].rate:
            return float(sq_items[0].rate)
        
        # 3. Thu lay tu Item (last purchase rate)
        item = frappe.get_doc("Item", item_code)
        if item.last_purchase_rate:
            return float(item.last_purchase_rate)
        
        return None
    
    except Exception:
        return None


def get_supplier_lead_time(item_code, supplier=None):
    """
    Lay lead time cua supplier cho item
    
    Args:
        item_code: Item code
        supplier: Supplier name (optional, neu None thi lay default lead time)
    
    Returns:
        int: Lead time in days
    """
    try:
        # Neu co supplier, thu lay tu supplier-specific sources
        if supplier:
            # 1. Thu lay tu Item Supplier
            item_supplier = frappe.get_all(
                "Item Supplier",
                filters={"parent": item_code, "supplier": supplier},
                fields=["lead_time_days"],
                limit=1,
            )
            
            if item_supplier and item_supplier[0].lead_time_days:
                return int(item_supplier[0].lead_time_days)
            
            # 2. Thu lay tu Supplier Quotation Item
            sq_items = frappe.get_all(
                "Supplier Quotation Item",
                filters={
                    "item_code": item_code,
                    "parent": ["in", frappe.get_all(
                        "Supplier Quotation",
                        filters={"supplier": supplier, "docstatus": 1},
                        fields=["name"],
                        limit=10,
                    )],
                },
                fields=["lead_time_days"],
                order_by="parent desc",
                limit=1,
            )
            
            if sq_items and sq_items[0].lead_time_days:
                return int(sq_items[0].lead_time_days)
        
        # 3. Thu lay tu Item (default lead time)
        item = frappe.get_doc("Item", item_code)
        if item.lead_time_days:
            return int(item.lead_time_days)
        
        # Default: 7 days
        return 7
    
    except Exception:
        return 7


def calculate_required_date(planned_start_date, lead_time_days, buffer_days=0):
    """
    Tinh ngay can co NVL (tru lead time va buffer)
    
    Args:
        planned_start_date: Ngay bat dau san xuat
        lead_time_days: Lead time cua supplier
        buffer_days: So ngay buffer (optional)
    
    Returns:
        date: Required date
    """
    # Ensure lead_time_days and buffer_days are numbers
    lead_time_days = int(lead_time_days) if lead_time_days else 0
    buffer_days = int(buffer_days) if buffer_days else 0
    
    total_days = lead_time_days + buffer_days
    required_date = add_days(planned_start_date, -total_days)
    return required_date


def aggregate_material_requirements(material_requirements):
    """
    Tong hop nhu cau NVL (group theo item_code)
    
    Args:
        material_requirements: List of dicts voi item_code, qty, required_date
    
    Returns:
        dict: {item_code: {total_qty, earliest_required_date, latest_required_date}}
    """
    aggregated = defaultdict(lambda: {
        "total_qty": 0.0,
        "earliest_required_date": None,
        "latest_required_date": None,
    })
    
    for req in material_requirements:
        item_code = req.get("item_code")
        qty = flt(req.get("qty", 0))
        required_date = req.get("required_date")
        
        if item_code:
            aggregated[item_code]["total_qty"] += qty
            
            if required_date:
                # Ensure required_date is date object
                if isinstance(required_date, str):
                    required_date = getdate(required_date)
                
                if not aggregated[item_code]["earliest_required_date"]:
                    aggregated[item_code]["earliest_required_date"] = required_date
                    aggregated[item_code]["latest_required_date"] = required_date
                else:
                    earliest = getdate(aggregated[item_code]["earliest_required_date"])
                    latest = getdate(aggregated[item_code]["latest_required_date"])
                    
                    if required_date < earliest:
                        aggregated[item_code]["earliest_required_date"] = required_date
                    if required_date > latest:
                        aggregated[item_code]["latest_required_date"] = required_date
    
    return dict(aggregated)

