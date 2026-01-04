# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
MRP Optimization API
Chay MRP Optimization de tinh toan NVL can thiet va tao Purchase Suggestions
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, getdate, add_days, flt
from collections import defaultdict
from uit_aps.utils.mrp_helper import (
    get_bom_for_item,
    get_exploded_bom_items,
    get_current_stock,
    get_optimal_supplier,
    calculate_required_date,
    aggregate_material_requirements,
    get_supplier_lead_time,
)


@frappe.whitelist()
def run_mrp_optimization(
    production_plan,
    buffer_days=0,
    include_non_stock_items=False,
):
    """
    Chay MRP Optimization cho Production Plan
    
    Args:
        production_plan: Name cua APS Production Plan
        buffer_days: So ngay buffer truoc khi can NVL (default: 0)
        include_non_stock_items: Co bao gom non-stock items khong (default: False)
    
    Returns:
        dict: Ket qua MRP Optimization
    """
    try:
        # Ensure buffer_days is int
        buffer_days = int(buffer_days) if buffer_days else 0
        include_non_stock_items = bool(include_non_stock_items)
        # 1. Validate Production Plan
        if not frappe.db.exists("APS Production Plan", production_plan):
            frappe.throw(_("Production Plan not found"))
        
        prod_plan = frappe.get_doc("APS Production Plan", production_plan)
        
        if not prod_plan.items:
            frappe.throw(_("Production Plan has no items"))
        
        company = prod_plan.company
        
        # 2. Tao MRP Run
        mrp_run = frappe.get_doc({
            "doctype": "APS MRP Run",
            "production_plan": production_plan,
            "run_status": "Running",
            "run_date": now_datetime(),
            "executed_by": frappe.session.user,
        })
        mrp_run.insert()
        frappe.db.commit()
        
        # 3. Tinh toan material requirements
        material_requirements = []
        mrp_results = []
        
        for plan_item in prod_plan.items:
            item_code = plan_item.item
            planned_qty = plan_item.planned_qty
            planned_start_date = plan_item.planned_start_date or plan_item.plan_period
            
            # Kiem tra co BOM khong
            bom_name = get_bom_for_item(item_code, company)
            
            if not bom_name:
                # Khong co BOM, bo qua
                continue
            
            # Lay exploded BOM items
            bom_items = get_exploded_bom_items(
                bom_name=bom_name,
                qty=planned_qty,
                include_non_stock_items=include_non_stock_items,
            )
            
            # Tinh toan material requirements
            for bom_item in bom_items:
                material_item = bom_item["item_code"]
                material_qty = bom_item["qty"]
                
                # Lay ton kho hien tai
                current_stock = get_current_stock(material_item)
                
                # Ensure material_qty and current_stock are floats
                material_qty = flt(material_qty) if material_qty else 0.0
                current_stock = flt(current_stock) if current_stock else 0.0
                
                # Tinh shortage
                shortage_qty = max(0, material_qty - current_stock)
                
                if shortage_qty > 0:
                    # Tinh required date (tru lead time)
                    # Lay lead time tu item (se optimize supplier sau)
                    item_lead_time = get_supplier_lead_time(material_item, None) or 7
                    item_lead_time = int(item_lead_time) if item_lead_time else 7
                    
                    # Ensure planned_start_date is date
                    if isinstance(planned_start_date, str):
                        planned_start_date = getdate(planned_start_date)
                    
                    required_date = calculate_required_date(
                        planned_start_date,
                        item_lead_time,
                        buffer_days,
                    )
                    
                    material_requirements.append({
                        "item_code": material_item,
                        "qty": shortage_qty,
                        "required_date": required_date,
                        "source_plan_item": plan_item.name,
                    })
        
        # 4. Aggregate material requirements (group theo item_code)
        aggregated_requirements = aggregate_material_requirements(material_requirements)
        
        # 5. Tao MRP Results va optimize suppliers
        purchase_suggestions = []
        
        for item_code, req_data in aggregated_requirements.items():
            total_qty = flt(req_data["total_qty"]) if req_data.get("total_qty") else 0.0
            required_date = req_data.get("earliest_required_date")
            if isinstance(required_date, str):
                required_date = getdate(required_date)
            current_stock = flt(get_current_stock(item_code))
            
            # Tinh shortage qty
            shortage_qty = max(0, total_qty - current_stock)
            
            # Tao MRP Result
            mrp_result = frappe.get_doc({
                "doctype": "APS MRP Result",
                "mrp_run": mrp_run.name,
                "material_item": item_code,
                "required_qty": total_qty,
                "available_qty": current_stock,
                "shortage_qty": shortage_qty,
                "required_date": required_date,
            })
            mrp_result.insert()
            mrp_results.append(mrp_result.name)
            
            # 6. Tim supplier toi uu
            optimal_supplier = get_optimal_supplier(
                item_code=item_code,
                required_qty=total_qty,
                required_date=required_date,
                company=company,
            )
            
            # 7. Chi tao Purchase Suggestion neu co shortage
            if shortage_qty > 0:
                # 8. Tao Purchase Suggestion
                purchase_suggestion = frappe.get_doc({
                    "doctype": "APS Purchase Suggestion",
                    "mrp_run": mrp_run.name,
                    "material_item": item_code,
                    "purchase_qty": shortage_qty,
                    "required_date": required_date,
                    "supplier": optimal_supplier["supplier"] if optimal_supplier else None,
                    "unit_price": optimal_supplier["unit_price"] if optimal_supplier else None,
                    "lead_time": optimal_supplier["lead_time"] if optimal_supplier else None,
                    "suggestion_status": "Draft",
                })
                purchase_suggestion.insert()
                purchase_suggestions.append(purchase_suggestion.name)
        
        # 9. Update MRP Run
        mrp_run.run_status = "Completed"
        mrp_run.total_materials = len(aggregated_requirements)
        mrp_run.save()
        frappe.db.commit()
        
        return {
            "success": True,
            "mrp_run": mrp_run.name,
            "mrp_results_created": len(mrp_results),
            "purchase_suggestions_created": len(purchase_suggestions),
            "total_materials": len(aggregated_requirements),
        }
    
    except Exception as e:
        frappe.log_error(
            f"MRP Optimization failed: {str(e)}", "MRP Optimization Error"
        )
        if "mrp_run" in locals():
            mrp_run.run_status = "Failed"
            mrp_run.notes = str(e)
            mrp_run.save()
        frappe.throw(_("MRP Optimization failed: {0}").format(str(e)))



