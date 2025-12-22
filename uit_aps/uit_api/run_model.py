# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Run Model API
Chay cac forecast models va luu ket qua vao APS Forecast Result va APS Forecast History
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, nowdate, add_days, getdate
from uit_aps.ml.arima_model import ARIMAForecast
from uit_aps.ml.linear_regression_model import LinearRegressionForecast
from uit_aps.ml.prophet import ProphetForecast
from uit_aps.ml.data_helper import (
    get_sales_order_items_for_item,
    get_all_items_from_sales_orders,
    get_current_stock,
    get_item_lead_time,
    validate_sales_order_data,
)
from uit_aps.ml.ai_explainer import is_ai_enabled
from uit_aps.ml.ai_background_jobs import (
    enqueue_ai_explanations,
    get_ai_job_status,
)


@frappe.whitelist()
def run_forecast(
    model_name,
    company=None,
    forecast_horizon_days=30,
    training_period_days=180,
    warehouse=None,
    item_code=None,
    item_group=None,
):
    """
    Chay forecast cho mot hoac nhieu items

    Args:
        model_name: Ten model (ARIMA, Linear Regression, Prophet)
        company: Company name
        forecast_horizon_days: So ngay du bao
        training_period_days: So ngay du lieu training
        warehouse: Warehouse (optional)
        item_code: Item code cu the (optional) - neu co thi chi forecast item nay
        item_group: Item group (optional) - filter theo nhom

    Returns:
        dict: Ket qua forecast run
    """
    try:
        # Validate model name
        valid_models = ["ARIMA", "Linear Regression", "Prophet"]
        if model_name not in valid_models:
            frappe.throw(
                _("Invalid model name. Choose from: {0}").format(
                    ", ".join(valid_models)
                )
            )

        # Calculate date range
        end_date = getdate()
        start_date = add_days(end_date, -training_period_days)

        # Create Forecast History record
        history = create_forecast_history(
            model_name=model_name,
            company=company,
            forecast_horizon_days=forecast_horizon_days,
            training_start=start_date,
            training_end=end_date,
        )

        frappe.db.commit()

        # Get items to forecast
        if item_code:
            items_to_forecast = [item_code]
        else:
            items_to_forecast = get_all_items_from_sales_orders(
                company=company,
                start_date=start_date,
                end_date=end_date,
                warehouse=warehouse,
                item_group=item_group,
            )

        if not items_to_forecast:
            update_forecast_history(
                history.name, status="Failed", error="No items found"
            )
            frappe.throw(_("No items found for forecasting"))

        # Update history
        history.total_items_forecasted = len(items_to_forecast)
        history.save()
        frappe.db.commit()

        # Run forecast for each item
        results = []
        successful = 0
        failed = 0

        for item in items_to_forecast:
            try:
                result = run_forecast_for_item(
                    item_code=item,
                    model_name=model_name,
                    company=company,
                    warehouse=warehouse,
                    forecast_horizon_days=forecast_horizon_days,
                    training_start=start_date,
                    training_end=end_date,
                    history_name=history.name,
                )

                if result:
                    results.append(result)
                    successful += 1
                else:
                    failed += 1

            except Exception as e:
                frappe.log_error(
                    f"Forecast failed for item {item}: {str(e)}", "Forecast Error"
                )
                failed += 1

        # Update history with final results
        update_forecast_history(
            history.name,
            status="Complete",
            total_results=len(results),
            successful=successful,
            failed=failed,
        )

        # Enqueue AI explanation job in background (khong lam cham forecast)
        ai_job_enqueued = False
        if is_ai_enabled():
            ai_job_enqueued = enqueue_ai_explanations(
                history_name=history.name,
                queue="default",  # default queue
                timeout=3600,  # 1 hour timeout
            )

        return {
            "success": True,
            "history_name": history.name,
            "total_items": len(items_to_forecast),
            "successful": successful,
            "failed": failed,
            "results": results,
            "ai_job_enqueued": ai_job_enqueued,
        }

    except Exception as e:
        frappe.log_error(f"Forecast run failed: {str(e)}", "Forecast Run Error")
        if "history" in locals():
            update_forecast_history(history.name, status="Failed", error=str(e))
        frappe.throw(_("Forecast run failed: {0}").format(str(e)))


def run_forecast_for_item(
    item_code,
    model_name,
    company=None,
    warehouse=None,
    forecast_horizon_days=30,
    training_start=None,
    training_end=None,
    history_name=None,
):
    """
    Chay forecast cho mot item cu the

    Args:
        item_code: Item code
        model_name: Model name
        company: Company
        warehouse: Warehouse
        forecast_horizon_days: Forecast period
        training_start: Training start date
        training_end: Training end date
        history_name: Link to forecast history

    Returns:
        str: Name of created APS Forecast Result record
    """
    # Get Sales Order data for this item
    sales_order_items = get_sales_order_items_for_item(
        item_code=item_code,
        company=company,
        start_date=training_start,
        end_date=training_end,
        warehouse=warehouse,
    )

    # Validate data
    is_valid, error_msg = validate_sales_order_data(sales_order_items, min_records=10)
    if not is_valid:
        frappe.log_error(
            f"Insufficient data for {item_code}: {error_msg}", "Forecast Data Error"
        )
        return None

    # Get current stock and lead time
    current_stock = get_current_stock(item_code, warehouse)
    lead_time_days = get_item_lead_time(item_code)

    # Initialize model
    if model_name == "ARIMA":
        model = ARIMAForecast(item_code=item_code, warehouse=warehouse, company=company)
    elif model_name == "Linear Regression":
        model = LinearRegressionForecast(
            item_code=item_code, warehouse=warehouse, company=company
        )
    elif model_name == "Prophet":
        model = ProphetForecast(
            item_code=item_code, warehouse=warehouse, company=company
        )
    else:
        return None

    # Run forecast
    forecast_output = model.forecast(
        sales_order_items=sales_order_items,
        forecast_period_days=forecast_horizon_days,
        lead_time_days=lead_time_days,
        current_stock=current_stock,
    )

    if not forecast_output:
        return None

    # Note: AI explanation se duoc generate trong background job
    # Khong generate o day de tranh lam cham forecast process

    # Create APS Forecast Result
    result_name = create_forecast_result(
        item_code=item_code,
        forecast_output=forecast_output,
        history_name=history_name,
        company=company,
        warehouse=warehouse,
        forecast_period_start=add_days(training_end, 1),
        forecast_period_end=add_days(training_end, forecast_horizon_days),
    )

    return result_name


def create_forecast_history(
    model_name,
    company=None,
    forecast_horizon_days=30,
    training_start=None,
    training_end=None,
):
    """
    Tao APS Forecast History record

    Args:
        model_name: Model name
        company: Company
        forecast_horizon_days: Forecast horizon
        training_start: Training period start
        training_end: Training period end

    Returns:
        Document: APS Forecast History doc
    """
    doc = frappe.get_doc(
        {
            "doctype": "APS Forecast History",
            "run_name": f"{model_name} - {nowdate()}",
            "company": company,
            "model_used": model_name,
            "forecast_horizon_days": forecast_horizon_days,
            "training_period_start": training_start,
            "training_period_end": training_end,
            "start_date": add_days(training_end, 1) if training_end else None,
            "end_date": (
                add_days(training_end, forecast_horizon_days) if training_end else None
            ),
            "run_status": "Running",
            "run_start_time": now_datetime(),
        }
    )
    doc.insert(ignore_permissions=True)
    return doc


def update_forecast_history(
    history_name,
    status=None,
    total_results=None,
    successful=None,
    failed=None,
    error=None,
):
    """
    Cap nhat APS Forecast History record

    Args:
        history_name: History record name
        status: New status
        total_results: Total results generated
        successful: Number of successful forecasts
        failed: Number of failed forecasts
        error: Error message
    """
    doc = frappe.get_doc("APS Forecast History", history_name)

    if status:
        doc.run_status = status
        if status in ["Complete", "Failed"]:
            doc.run_end_time = now_datetime()

    if total_results is not None:
        doc.total_results_generated = total_results

    if successful is not None:
        doc.successful_forecasts = successful

    if failed is not None:
        doc.failed_forecasts = failed

    if error:
        doc.notes = error

    doc.save(ignore_permissions=True)
    frappe.db.commit()


def create_forecast_result(
    item_code,
    forecast_output,
    history_name=None,
    company=None,
    warehouse=None,
    forecast_period_start=None,
    forecast_period_end=None,
):
    """
    Tao APS Forecast Result record tu model output

    Args:
        item_code: Item code
        forecast_output: Dict output tu model
        history_name: Link to forecast history
        company: Company
        warehouse: Warehouse
        forecast_period_start: Forecast period start date
        forecast_period_end: Forecast period end date

    Returns:
        str: Name of created record
    """
    doc = frappe.get_doc(
        {
            "doctype": "APS Forecast Result",
            # Basic info
            "item": item_code,
            "forecast_period": forecast_period_start or nowdate(),
            "forecast_history": history_name,
            "company": company,
            "warehouse": warehouse,
            # Core forecast
            "forecast_qty": forecast_output.get("forecast_qty"),
            "confidence_score": forecast_output.get("confidence_score"),
            "lower_bound": forecast_output.get("lower_bound"),
            "upper_bound": forecast_output.get("upper_bound"),
            # Model info
            "model_used": forecast_output.get("model_used"),
            "model_confidence": forecast_output.get("model_confidence"),
            "training_data_points": forecast_output.get("training_data_points"),
            # Movement and trend
            "movement_type": forecast_output.get("movement_type"),
            "daily_avg_consumption": forecast_output.get("daily_avg_consumption"),
            "trend_type": forecast_output.get("trend_type"),
            # Inventory recommendations
            "reorder_level": forecast_output.get("reorder_level"),
            "suggested_qty": forecast_output.get("suggested_qty"),
            "safety_stock": forecast_output.get("safety_stock"),
            "current_stock": forecast_output.get("current_stock"),
            "reorder_alert": forecast_output.get("reorder_alert", 0),
            # Model-specific: ARIMA
            "arima_p": forecast_output.get("arima_p"),
            "arima_d": forecast_output.get("arima_d"),
            "arima_q": forecast_output.get("arima_q"),
            "arima_aic": forecast_output.get("arima_aic"),
            # Model-specific: Linear Regression
            "lr_r2_score": forecast_output.get("lr_r2_score"),
            "lr_slope": forecast_output.get("lr_slope"),
            # Model-specific: Prophet
            "prophet_seasonality_detected": forecast_output.get(
                "prophet_seasonality_detected", 0
            ),
            "prophet_seasonality_type": forecast_output.get("prophet_seasonality_type"),
            "prophet_changepoint_count": forecast_output.get(
                "prophet_changepoint_count"
            ),
            # Explanation
            "forecast_explanation": forecast_output.get("forecast_explanation"),
            "recommendations": forecast_output.get("recommendations"),
        }
    )

    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return doc.name


@frappe.whitelist()
def get_forecast_results(history_name):
    """
    Lay tat ca forecast results cua mot history run

    Args:
        history_name: Forecast history name

    Returns:
        list: Danh sach forecast results
    """
    results = frappe.get_all(
        "APS Forecast Result",
        filters={"forecast_history": history_name},
        fields=[
            "name",
            "item",
            "forecast_qty",
            "confidence_score",
            "movement_type",
            "reorder_alert",
            "model_used",
        ],
        order_by="forecast_qty desc",
    )

    return results


@frappe.whitelist()
def compare_models(
    item_code,
    company=None,
    forecast_horizon_days=30,
    training_period_days=180,
    warehouse=None,
):
    """
    So sanh ket qua cua 3 models cho cung 1 item

    Args:
        item_code: Item code
        company: Company
        forecast_horizon_days: Forecast period
        training_period_days: Training period
        warehouse: Warehouse

    Returns:
        dict: Comparison results
    """
    end_date = getdate()
    start_date = add_days(end_date, -training_period_days)

    # Get data
    sales_order_items = get_sales_order_items_for_item(
        item_code=item_code,
        company=company,
        start_date=start_date,
        end_date=end_date,
        warehouse=warehouse,
    )

    is_valid, error_msg = validate_sales_order_data(sales_order_items)
    if not is_valid:
        frappe.throw(_(error_msg))

    current_stock = get_current_stock(item_code, warehouse)
    lead_time_days = get_item_lead_time(item_code)

    results = {}

    # Try each model
    for model_name in ["ARIMA", "Linear Regression", "Prophet"]:
        try:
            if model_name == "ARIMA":
                model = ARIMAForecast(
                    item_code=item_code, warehouse=warehouse, company=company
                )
            elif model_name == "Linear Regression":
                model = LinearRegressionForecast(
                    item_code=item_code, warehouse=warehouse, company=company
                )
            elif model_name == "Prophet":
                model = ProphetForecast(
                    item_code=item_code, warehouse=warehouse, company=company
                )

            output = model.forecast(
                sales_order_items=sales_order_items,
                forecast_period_days=forecast_horizon_days,
                lead_time_days=lead_time_days,
                current_stock=current_stock,
            )

            if output:
                results[model_name] = {
                    "forecast_qty": output.get("forecast_qty"),
                    "confidence_score": output.get("confidence_score"),
                    "movement_type": output.get("movement_type"),
                    "trend_type": output.get("trend_type"),
                    "model_confidence": output.get("model_confidence"),
                }
            else:
                results[model_name] = {"error": "Forecast failed - insufficient data"}

        except Exception as e:
            results[model_name] = {"error": str(e)}

    return {
        "item_code": item_code,
        "results": results,
        "data_points": len(sales_order_items),
    }


@frappe.whitelist()
def get_ai_explanation_status(history_name):
    """
    Kiem tra trang thai cua AI explanation job

    Args:
        history_name: Ten cua APS Forecast History

    Returns:
        dict: Status information
    """
    if not is_ai_enabled():
        return {"ai_enabled": False, "message": "AI Explanation is not enabled"}

    status = get_ai_job_status(history_name)
    status["ai_enabled"] = True

    return status


@frappe.whitelist()
def retry_ai_explanations(history_name):
    """
    Retry AI explanation job neu that bai

    Args:
        history_name: Ten cua APS Forecast History

    Returns:
        dict: Result
    """
    if not is_ai_enabled():
        frappe.throw(_("AI Explanation is not enabled"))

    # Check if history exists
    if not frappe.db.exists("APS Forecast History", history_name):
        frappe.throw(_("Forecast History not found"))

    # Enqueue new job
    job_enqueued = enqueue_ai_explanations(
        history_name=history_name,
        queue="short",  # short queue for retry (faster)
        timeout=3600,
    )

    if job_enqueued:
        return {
            "success": True,
            "message": "AI explanation job has been queued for retry",
        }
    else:
        return {"success": False, "message": "Failed to queue AI explanation job"}
