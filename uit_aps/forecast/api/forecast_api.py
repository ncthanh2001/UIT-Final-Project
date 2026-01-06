# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Forecast API

Frappe whitelisted methods for APS Forecast operations.
"""

import frappe
from frappe import _
from frappe.utils import flt, cint, getdate
from typing import Dict, List, Optional
import json


@frappe.whitelist()
def get_forecast_history_list(
    limit: int = 20,
    offset: int = 0,
    company: str = None,
    model_used: str = None,
    status: str = None
) -> Dict:
    """
    Lay danh sach lich su forecast
    
    Args:
        limit: So luong record toi da
        offset: Vi tri bat dau
        company: Loc theo company
        model_used: Loc theo model
        status: Loc theo trang thai
        
    Returns:
        dict: {
            data: List of forecast history records,
            total: Total count,
            limit: Limit used,
            offset: Offset used
        }
    """
    # Build filters
    filters = {}
    if company:
        filters["company"] = company
    if model_used:
        filters["model_used"] = model_used
    if status:
        filters["run_status"] = status
    
    # Get total count
    total = frappe.db.count("APS Forecast History", filters)
    
    # Get data
    fields = [
        "name",
        "run_name", 
        "company",
        "model_used",
        "run_status",
        "run_start_time",
        "run_end_time",
        "total_items_forecasted",
        "successful_forecasts",
        "failed_forecasts",
        "avg_confidence_score",
        "forecast_horizon_days",
        "start_date",
        "end_date"
    ]
    
    data = frappe.get_all(
        "APS Forecast History",
        filters=filters,
        fields=fields,
        order_by="run_start_time desc",
        limit=cint(limit),
        start=cint(offset)
    )
    
    return {
        "data": data,
        "total": total,
        "limit": cint(limit),
        "offset": cint(offset)
    }


@frappe.whitelist()
def get_forecast_dashboard_data(forecast_history: str) -> Dict:
    """
    Lay du lieu dashboard cho mot forecast history cu the
    
    Args:
        forecast_history: Ten cua APS Forecast History record
        
    Returns:
        dict: Dashboard data bao gom KPI, charts, tables
    """
    if not frappe.db.exists("APS Forecast History", forecast_history):
        frappe.throw(_("Forecast History {0} not found").format(forecast_history))
    
    # Lay thong tin forecast history
    history = frappe.get_doc("APS Forecast History", forecast_history)
    
    # Lay tat ca forecast results lien quan
    results = frappe.get_all(
        "APS Forecast Result",
        filters={"forecast_history": forecast_history},
        fields=[
            "name",
            "item",
            "item_group", 
            "forecast_period",
            "forecast_qty",
            "confidence_score",
            "model_used",
            "movement_type",
            "trend_type",
            "current_stock",
            "reorder_level",
            "suggested_qty",
            "safety_stock",
            "reorder_alert",
            "daily_avg_consumption",
            "lower_bound",
            "upper_bound"
        ]
    )
    
    # Tinh toan KPI
    kpi_data = calculate_kpi_data(history, results)
    
    # Tao du lieu cho charts
    chart_data = generate_chart_data(history, results)
    
    # Tao bang reorder alerts
    reorder_alerts = get_reorder_alerts(results)
    
    # Tao recommendations
    recommendations = generate_recommendations(history, results)
    
    return {
        "history": {
            "name": history.name,
            "run_name": history.run_name,
            "company": history.company,
            "model_used": history.model_used,
            "run_status": history.run_status,
            "run_start_time": history.run_start_time,
            "run_end_time": history.run_end_time,
            "ai_analysis": history.ai_analysis
        },
        "kpi": kpi_data,
        "charts": chart_data,
        "reorder_alerts": reorder_alerts,
        "recommendations": recommendations,
        "results": results
    }


def calculate_kpi_data(history, results: List[Dict]) -> Dict:
    """Tinh toan cac chi so KPI"""
    total_forecast_qty = sum([flt(r.get("forecast_qty", 0)) for r in results])
    avg_confidence = flt(history.avg_confidence_score or 0)
    reorder_alerts_count = len([r for r in results if r.get("reorder_alert")])
    
    # Tinh trung binh stock coverage (days)
    coverage_days = []
    for r in results:
        current_stock = flt(r.get("current_stock", 0))
        daily_avg = flt(r.get("daily_avg_consumption", 0))
        if daily_avg > 0:
            coverage = current_stock / daily_avg
            coverage_days.append(coverage)
    
    avg_coverage = sum(coverage_days) / len(coverage_days) if coverage_days else 0
    
    return {
        "totalForecastQty": total_forecast_qty,
        "avgConfidence": avg_confidence,
        "reorderAlerts": reorder_alerts_count,
        "avgStockCoverage": avg_coverage,
        "forecastRuns": 1,
        "periods": cint(history.forecast_horizon_days or 0) // 30,  # Convert days to months
        "items": len(results)
    }


def generate_chart_data(history, results: List[Dict]) -> Dict:
    """Tao du lieu cho cac bieu do"""
    
    # 1. Forecast over time - nhom theo thang
    forecast_by_period = {}
    for r in results:
        period = r.get("forecast_period")
        if period:
            period_str = getdate(period).strftime("%Y-%m")
            if period_str not in forecast_by_period:
                forecast_by_period[period_str] = 0
            forecast_by_period[period_str] += flt(r.get("forecast_qty", 0))
    
    forecast_over_time = [
        {"date": k, "qty": v}
        for k, v in sorted(forecast_by_period.items())
    ]
    
    # 2. Reorder alerts by item group
    alerts_by_group = {}
    for r in results:
        if r.get("reorder_alert"):
            group = r.get("item_group") or "Other"
            alerts_by_group[group] = alerts_by_group.get(group, 0) + 1
    
    # Lay top 10 groups
    reorder_by_group = [
        {"name": k, "alerts": v}
        for k, v in sorted(alerts_by_group.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    # Them cac groups khong co alert
    all_groups = set([r.get("item_group") for r in results if r.get("item_group")])
    for group in list(all_groups)[:10]:  # Limit to 10 groups
        if group not in alerts_by_group:
            reorder_by_group.append({"name": group, "alerts": 0})
    
    # 3. Top items by forecast qty
    top_items = sorted(results, key=lambda x: flt(x.get("forecast_qty", 0)), reverse=True)[:10]
    top_items_data = [
        {"item": r.get("item"), "qty": flt(r.get("forecast_qty", 0))}
        for r in top_items
    ]
    
    # 4. Confidence score distribution
    confidence_ranges = {}
    for r in results:
        conf = flt(r.get("confidence_score", 0))
        # Lam tron den 5%
        range_key = round(conf / 5) * 5
        confidence_ranges[range_key] = confidence_ranges.get(range_key, 0) + 1
    
    confidence_distribution = [
        {"range": str(k), "count": v}
        for k, v in sorted(confidence_ranges.items())
    ]
    
    return {
        "forecastOverTime": forecast_over_time,
        "reorderAlertsByGroup": reorder_by_group,
        "topItemsByForecast": top_items_data,
        "confidenceScore": confidence_distribution
    }


def get_reorder_alerts(results: List[Dict]) -> List[Dict]:
    """Lay danh sach reorder alerts"""
    alerts = []
    for r in results:
        if r.get("reorder_alert"):
            current_stock = flt(r.get("current_stock", 0))
            daily_avg = flt(r.get("daily_avg_consumption", 0))
            coverage_days = current_stock / daily_avg if daily_avg > 0 else 0
            
            alerts.append({
                "item": r.get("item"),
                "forecastDate": getdate(r.get("forecast_period")).strftime("%Y-%m") if r.get("forecast_period") else "",
                "forecastQty": flt(r.get("forecast_qty", 0)),
                "currentStock": current_stock,
                "reorderQty": flt(r.get("reorder_level", 0)),
                "suggestedQty": flt(r.get("suggested_qty", 0)),
                "coverageDays": coverage_days
            })
    
    return alerts


def generate_recommendations(history, results: List[Dict]) -> List[Dict]:
    """Tao cac khuyen nghi tu du lieu"""
    recommendations = []
    
    # Phan tich movement types
    movement_counts = {}
    for r in results:
        movement = r.get("movement_type") or "Unknown"
        movement_counts[movement] = movement_counts.get(movement, 0) + 1
    
    slow_moving = movement_counts.get("Slow Moving", 0)
    fast_moving = movement_counts.get("Fast Moving", 0)
    
    # Khuyen nghi 1: Dieu chinh model neu confidence thap
    avg_conf = flt(history.avg_confidence_score or 0)
    if avg_conf < 60:
        recommendations.append({
            "title": "Dieu chinh Model Du doan",
            "description": "Xem xet su dung phuong phap khac hoac ket hop voi cac mo hinh du doan khac de tang do tin cay.",
            "icon": "Target",
            "badge": "High Priority",
            "badgeColor": "bg-violet-500/20 text-violet-600",
            "impact": f"+{100-avg_conf:.0f}% accuracy potential"
        })
    
    # Khuyen nghi 2: Quan ly slow moving items
    if slow_moving > 0:
        recommendations.append({
            "title": "Quan ly Slow Moving Items",
            "description": f"Theo doi {slow_moving} items slow moving de lap ke hoach nhap hang phu hop, tranh ton kho.",
            "icon": "TrendingDown",
            "badge": "Medium Priority",
            "badgeColor": "bg-purple-500/20 text-purple-600",
            "impact": "-20% inventory cost"
        })
    
    # Khuyen nghi 3: Phat trien fast moving items
    if fast_moving > 0:
        recommendations.append({
            "title": "Phat trien Fast Moving Items",
            "description": f"Duy tri va mo rong {fast_moving} items fast moving de gia tang doanh thu.",
            "icon": "TrendingUp",
            "badge": "Quick Win",
            "badgeColor": "bg-pink-500/20 text-pink-600",
            "impact": "+12% revenue"
        })
    
    # Khuyen nghi 4: Phan tich dinh ky
    recommendations.append({
        "title": "Phan tich Thi truong Dinh ky",
        "description": "Cap nhat du lieu thi truong dinh ky de toi uu ke hoach nhap hang va phan phoi.",
        "icon": "BarChart3",
        "badge": "Strategic",
        "badgeColor": "bg-indigo-500/20 text-indigo-600",
        "impact": "Long-term growth"
    })
    
    return recommendations


@frappe.whitelist()
def get_forecast_result_details(forecast_result: str) -> Dict:
    """
    Lay chi tiet mot forecast result
    
    Args:
        forecast_result: Ten cua APS Forecast Result record
        
    Returns:
        dict: Chi tiet forecast result
    """
    if not frappe.db.exists("APS Forecast Result", forecast_result):
        frappe.throw(_("Forecast Result {0} not found").format(forecast_result))
    
    result = frappe.get_doc("APS Forecast Result", forecast_result)
    
    return result.as_dict()


@frappe.whitelist()
def get_companies() -> List[str]:
    """Lay danh sach companies"""
    return [d.name for d in frappe.get_all("Company", fields=["name"])]


@frappe.whitelist()
def get_forecast_models() -> List[str]:
    """Lay danh sach models"""
    return ["ARIMA", "Linear Regression", "Prophet"]

