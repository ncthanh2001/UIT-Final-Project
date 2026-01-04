# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Production Plan API
API de tao va quan ly Production Plan tu Forecast Results
"""

import frappe
from frappe import _
from frappe.utils import nowdate, getdate, add_days
from collections import defaultdict
from uit_aps.utils.production_plan_helper import (
    calculate_planned_qty,
    get_item_lead_time,
    calculate_planned_start_date,
    get_monthly_periods,
    get_quarterly_periods,
    find_closest_forecast_result,
    get_current_stock,
)


@frappe.whitelist()
def generate_production_plan_from_forecast(
    forecast_history,
    plan_name=None,
    plan_from_period=None,
    plan_to_period=None,
    time_granularity="Monthly",
    company=None,
    include_items=None,
    exclude_items=None,
    production_plan_name=None,
):
    """
    Tu dong tao hoac update Production Plan tu Forecast History
    
    Args:
        forecast_history: Name cua APS Forecast History
        plan_name: Ten ke hoach (neu None thi tu dong tao)
        plan_from_period: Ngay bat dau (neu None thi lay tu forecast)
        plan_to_period: Ngay ket thuc (neu None thi lay tu forecast)
        time_granularity: "Monthly" hoac "Quarterly"
        company: Company
        include_items: Chi tao plan cho cac items nay (optional, JSON string hoac list)
        exclude_items: Loai bo cac items nay (optional, JSON string hoac list)
        production_plan_name: Name cua Production Plan da ton tai (neu co thi se update, khong thi tao moi)
    
    Returns:
        dict: Ket qua tao/update Production Plan
    """
    try:
        # 1. Validate Forecast History
        if not frappe.db.exists("APS Forecast History", forecast_history):
            frappe.throw(_("Forecast History not found"))
        
        history = frappe.get_doc("APS Forecast History", forecast_history)
        
        if history.run_status != "Complete":
            frappe.throw(
                _("Forecast History must be Complete before creating Production Plan")
            )
        
        # 2. Lay company tu history neu chua co
        if not company:
            company = history.company
        
        # 3. Parse include/exclude items
        if include_items:
            if isinstance(include_items, str):
                import json
                include_items = json.loads(include_items)
        if exclude_items:
            if isinstance(exclude_items, str):
                import json
                exclude_items = json.loads(exclude_items)
        
        # 4. Lay forecast results
        filters = {"forecast_history": forecast_history}
        if include_items:
            filters["item"] = ["in", include_items]
        if exclude_items:
            if "item" in filters:
                # Combine with existing filter
                filters["item"] = ["in", [i for i in include_items if i not in exclude_items]]
            else:
                filters["item"] = ["not in", exclude_items]
        
        forecast_results = frappe.get_all(
            "APS Forecast Result",
            filters=filters,
            fields=[
                "name",
                "item",
                "forecast_qty",
                "forecast_period",
                "current_stock",
                "safety_stock",
                "confidence_score",
                "warehouse",
                "company",
            ],
            order_by="item, forecast_period",
        )
        
        if not forecast_results:
            frappe.throw(_("No forecast results found for this Forecast History"))
        
        # 5. Xac dinh plan period
        if not plan_from_period:
            plan_from_period = getdate(history.start_date) if history.start_date else getdate()
        else:
            plan_from_period = getdate(plan_from_period)
        
        if not plan_to_period:
            plan_to_period = getdate(history.end_date) if history.end_date else add_days(plan_from_period, 30)
        else:
            plan_to_period = getdate(plan_to_period)
        
        # Validate periods
        if plan_from_period >= plan_to_period:
            frappe.throw(_("Plan From Period must be before Plan To Period"))
        
        # 6. Tao hoac update Production Plan
        if production_plan_name and frappe.db.exists("APS Production Plan", production_plan_name):
            # Update Production Plan da ton tai
            production_plan = frappe.get_doc("APS Production Plan", production_plan_name)
            
            # Validate status
            if production_plan.status != "Draft":
                frappe.throw(_("Can only generate items when Production Plan status is Draft"))
            
            # Update cac fields neu co
            if plan_name:
                production_plan.plan_name = plan_name
            if plan_from_period:
                production_plan.plan_from_period = plan_from_period
            if plan_to_period:
                production_plan.plan_to_period = plan_to_period
            if time_granularity:
                production_plan.time_granularity = time_granularity
            if company:
                production_plan.company = company
            if forecast_history:
                production_plan.forecast_history = forecast_history
                production_plan.source_type = "Forecast"
            
            # Xoa cac items cu
            production_plan.items = []
        else:
            # Tao Production Plan moi
            if not plan_name:
                plan_name = f"Plan from {forecast_history} - {nowdate()}"
            
            production_plan = frappe.get_doc({
                "doctype": "APS Production Plan",
                "plan_name": plan_name,
                "company": company,
                "forecast_history": forecast_history,
                "plan_from_period": plan_from_period,
                "plan_to_period": plan_to_period,
                "source_type": "Forecast",
                "time_granularity": time_granularity,
                "status": "Draft",
            })
            production_plan.insert()
        
        frappe.db.commit()
        
        # 7. Generate items theo time granularity
        items_created = generate_plan_items(
            production_plan=production_plan,
            forecast_results=forecast_results,
            plan_from_period=plan_from_period,
            plan_to_period=plan_to_period,
            time_granularity=time_granularity,
        )
        
        # 8. Update capacity status
        update_capacity_status(production_plan)
        
        production_plan.save()
        frappe.db.commit()
        
        return {
            "success": True,
            "production_plan": production_plan.name,
            "items_created": items_created,
        }
    
    except Exception as e:
        frappe.log_error(
            f"Generate Production Plan failed: {str(e)}", "Production Plan Error"
        )
        frappe.throw(_("Failed to generate Production Plan: {0}").format(str(e)))


def generate_plan_items(
    production_plan,
    forecast_results,
    plan_from_period,
    plan_to_period,
    time_granularity,
):
    """
    Tao cac items trong Production Plan
    
    Args:
        production_plan: Production Plan document
        forecast_results: List of forecast result dicts
        plan_from_period: Plan start date
        plan_to_period: Plan end date
        time_granularity: "Monthly" or "Quarterly"
    
    Returns:
        int: So luong items da tao
    """
    # Group forecast results by item
    items_dict = defaultdict(list)
    for result in forecast_results:
        items_dict[result.item].append(result)
    
    items_created = 0
    plan_from_period = getdate(plan_from_period)
    plan_to_period = getdate(plan_to_period)
    total_days = (plan_to_period - plan_from_period).days
    
    for item_code, results in items_dict.items():
        try:
            # Lay thong tin item
            item_doc = frappe.get_doc("Item", item_code)
            lead_time_days = get_item_lead_time(item_code)
            
            # Tinh tong forecast qty cho item trong period
            total_forecast_qty = sum([float(r.forecast_qty or 0) for r in results])
            
            # Lay current stock va safety stock (lay tu result dau tien hoac lay tu Bin)
            first_result = results[0]
            current_stock = float(first_result.current_stock or 0)
            safety_stock = float(first_result.safety_stock or 0)
            
            # Neu khong co trong result, lay tu Bin
            if not current_stock:
                current_stock = get_current_stock(
                    item_code, 
                    first_result.warehouse
                )
            
            # Tinh planned qty
            planned_qty = calculate_planned_qty(
                forecast_qty=total_forecast_qty,
                current_stock=current_stock,
                safety_stock=safety_stock,
            )
            
            # Phan bo theo time granularity
            if time_granularity == "Monthly":
                periods = get_monthly_periods(plan_from_period, plan_to_period)
            else:  # Quarterly
                periods = get_quarterly_periods(plan_from_period, plan_to_period)
            
            # Tao item cho moi period
            for period_start, period_end in periods:
                # Tinh phan tram cua period trong tong period
                period_days = (period_end - period_start).days + 1
                ratio = period_days / total_days if total_days > 0 else 1.0 / len(periods)
                
                period_planned_qty = planned_qty * ratio
                
                # Tinh planned start date (tru lead time)
                planned_start_date = calculate_planned_start_date(
                    period_start=period_start,
                    lead_time_days=lead_time_days,
                )
                
                # Tim forecast result gan nhat
                forecast_result = find_closest_forecast_result(
                    results, period_start
                )
                
                # Tinh forecast qty cho period nay
                period_forecast_qty = total_forecast_qty * ratio
                if forecast_result:
                    period_forecast_qty = float(forecast_result.forecast_qty or 0) * ratio
                
                # Tao Production Plan Item
                plan_item = production_plan.append("items", {
                    "item": item_code,
                    "plan_period": period_start,
                    "planned_qty": period_planned_qty,
                    "forecast_result": forecast_result.name if forecast_result else None,
                    "forecast_quantiy": period_forecast_qty,
                    "current_stock": current_stock,
                    "safety_stock": safety_stock,
                    "planned_start_date": planned_start_date,
                    "lead_time_days": lead_time_days,
                })
                
                items_created += 1
        
        except Exception as e:
            frappe.log_error(
                f"Error creating plan item for {item_code}: {str(e)}",
                "Production Plan Item Error"
            )
            continue
    
    return items_created


def update_capacity_status(production_plan):
    """
    Cap nhat capacity status cua Production Plan
    TODO: Implement capacity checking logic voi Work Shift, Machine Downtime
    """
    # Placeholder: Set to OK for now
    # Co the implement sau voi:
    # - Check Work Shift capacity
    # - Check Machine Downtime
    # - Check existing Production Orders
    production_plan.capacity_status = "OK"


@frappe.whitelist()
def get_forecast_period(forecast_history):
    """
    Lay thong tin period tu Forecast History
    
    Args:
        forecast_history: Name cua APS Forecast History
    
    Returns:
        dict: Thong tin period
    """
    try:
        history = frappe.get_doc("APS Forecast History", forecast_history)
        return {
            "start_date": history.start_date,
            "end_date": history.end_date,
            "company": history.company,
            "model_used": history.model_used,
        }
    except Exception:
        frappe.throw(_("Forecast History not found"))


@frappe.whitelist()
def refresh_plan_items(production_plan_name):
    """
    Refresh cac items trong Production Plan tu Forecast Results
    
    Args:
        production_plan_name: Name cua Production Plan
    
    Returns:
        dict: Ket qua refresh
    """
    try:
        production_plan = frappe.get_doc("APS Production Plan", production_plan_name)
        
        if production_plan.status != "Draft":
            frappe.throw(_("Can only refresh items when status is Draft"))
        
        if not production_plan.forecast_history:
            frappe.throw(_("Forecast History is required"))
        
        # Xoa cac items cu
        production_plan.items = []
        
        # Lay forecast results
        forecast_results = frappe.get_all(
            "APS Forecast Result",
            filters={"forecast_history": production_plan.forecast_history},
            fields=[
                "name",
                "item",
                "forecast_qty",
                "forecast_period",
                "current_stock",
                "safety_stock",
                "warehouse",
            ],
            order_by="item, forecast_period",
        )
        
        if not forecast_results:
            frappe.throw(_("No forecast results found"))
        
        # Generate items lai
        items_created = generate_plan_items(
            production_plan=production_plan,
            forecast_results=forecast_results,
            plan_from_period=production_plan.plan_from_period,
            plan_to_period=production_plan.plan_to_period,
            time_granularity=production_plan.time_granularity or "Monthly",
        )
        
        update_capacity_status(production_plan)
        
        production_plan.save()
        frappe.db.commit()
        
        return {
            "success": True,
            "items_created": items_created,
        }
    
    except Exception as e:
        frappe.log_error(
            f"Refresh plan items failed: {str(e)}", "Production Plan Error"
        )
        frappe.throw(_("Failed to refresh plan items: {0}").format(str(e)))

