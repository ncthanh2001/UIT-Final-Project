# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
AI Background Jobs
Xu ly AI explanation trong background de khong lam cham forecast
"""

import frappe
from uit_aps.ml.ai_explainer import (
    generate_item_forecast_explanation,
    generate_history_analysis,
    is_ai_enabled,
)


def process_ai_explanations_for_history(history_name):
    """
    Background job: Generate AI explanations cho tat ca results va history
    
    Args:
        history_name: Ten cua APS Forecast History record
    """
    if not is_ai_enabled():
        frappe.log_error(
            "AI not enabled but background job was triggered", 
            "AI Background Job"
        )
        return
    
    try:
        # Get all forecast results for this history
        results = frappe.get_all(
            "APS Forecast Result",
            filters={"forecast_history": history_name},
            fields=["name", "item", "model_used"],
        )
        
        if not results:
            frappe.log_error(
                f"No results found for history {history_name}",
                "AI Background Job"
            )
            return
        
        processed = 0
        failed = 0
        
        # Process each result
        for result in results:
            try:
                process_ai_explanation_for_result(result.name)
                processed += 1
                frappe.db.commit()  # Commit sau moi item de tranh mat het neu loi
            except Exception as e:
                failed += 1
                frappe.log_error(
                    f"AI explanation failed for result {result.name}: {str(e)}",
                    "AI Background Job"
                )
        
        # Generate overall history analysis
        try:
            history_doc = frappe.get_doc("APS Forecast History", history_name)
            ai_analysis = generate_history_analysis(history_doc)
            
            if ai_analysis:
                history_doc.ai_analysis = ai_analysis
                history_doc.save(ignore_permissions=True)
                frappe.db.commit()
                
                frappe.logger().info(
                    f"AI analysis generated for history {history_name}"
                )
        except Exception as e:
            frappe.log_error(
                f"History AI analysis failed for {history_name}: {str(e)}",
                "AI Background Job"
            )
        
        # Log summary
        frappe.logger().info(
            f"AI Background Job completed for {history_name}: "
            f"{processed} processed, {failed} failed"
        )
        
    except Exception as e:
        frappe.log_error(
            f"AI background job failed for history {history_name}: {str(e)}",
            "AI Background Job"
        )


def process_ai_explanation_for_result(result_name):
    """
    Generate AI explanation cho 1 forecast result cu the
    
    Args:
        result_name: Ten cua APS Forecast Result record
    """
    try:
        result_doc = frappe.get_doc("APS Forecast Result", result_name)
        
        # Prepare forecast data from result
        forecast_data = {
            "forecast_qty": result_doc.forecast_qty,
            "confidence_score": result_doc.confidence_score,
            "lower_bound": result_doc.lower_bound,
            "upper_bound": result_doc.upper_bound,
            "movement_type": result_doc.movement_type,
            "daily_avg_consumption": result_doc.daily_avg_consumption,
            "trend_type": result_doc.trend_type,
            "current_stock": result_doc.current_stock,
            "reorder_level": result_doc.reorder_level,
            "safety_stock": result_doc.safety_stock,
            "suggested_qty": result_doc.suggested_qty,
            "reorder_alert": result_doc.reorder_alert,
            "training_data_points": result_doc.training_data_points,
        }
        
        # Generate AI explanation
        ai_explanation = generate_item_forecast_explanation(
            forecast_data=forecast_data,
            item_code=result_doc.item,
            model_name=result_doc.model_used,
        )
        
        if ai_explanation:
            # Update forecast_explanation with AI version
            result_doc.forecast_explanation = ai_explanation
            result_doc.save(ignore_permissions=True)
            
            frappe.logger().info(
                f"AI explanation generated for result {result_name}"
            )
        
    except Exception as e:
        frappe.log_error(
            f"Failed to generate AI explanation for {result_name}: {str(e)}",
            "AI Background Job"
        )
        raise


def enqueue_ai_explanations(history_name, queue="default", timeout=3600):
    """
    Enqueue AI explanation job vao background queue
    
    Args:
        history_name: Ten cua APS Forecast History
        queue: Queue name - Chi co 3 options:
            - "short": High priority, nhanh (cho retry, urgent)
            - "default": Normal priority (mac dinh)
            - "long": Low priority, cham (cho batch lon)
        timeout: Timeout in seconds (default 1 hour)
    """
    try:
        frappe.enqueue(
            method="uit_aps.ml.ai_background_jobs.process_ai_explanations_for_history",
            queue=queue,
            timeout=timeout,
            is_async=True,
            history_name=history_name,
        )
        
        frappe.logger().info(
            f"AI explanation job enqueued for history {history_name}"
        )
        
        return True
        
    except Exception as e:
        frappe.log_error(
            f"Failed to enqueue AI job for {history_name}: {str(e)}",
            "AI Background Job"
        )
        return False


def get_ai_job_status(history_name):
    """
    Kiem tra trang thai cua AI background job
    
    Args:
        history_name: Ten cua APS Forecast History
        
    Returns:
        dict: Status information
    """
    # Check if job is in queue
    queued_jobs = frappe.get_all(
        "RQ Job",
        filters={
            "method": "uit_aps.ml.ai_background_jobs.process_ai_explanations_for_history",
            "status": ["in", ["queued", "started"]],
        },
        fields=["name", "status", "creation", "modified"],
    )
    
    # Check for related jobs
    related_jobs = [
        job for job in queued_jobs 
        if history_name in str(job.get("name", ""))
    ]
    
    if related_jobs:
        job = related_jobs[0]
        return {
            "status": "processing",
            "job_status": job.status,
            "created": job.creation,
            "updated": job.modified,
        }
    
    # Check if results have AI explanations
    results_with_ai = frappe.db.count(
        "APS Forecast Result",
        filters={
            "forecast_history": history_name,
            "forecast_explanation": ["!=", ""],
        },
    )
    
    total_results = frappe.db.count(
        "APS Forecast Result",
        filters={"forecast_history": history_name},
    )
    
    # Check if history has AI analysis
    history_has_ai = frappe.db.get_value(
        "APS Forecast History",
        history_name,
        "ai_analysis",
    )
    
    if results_with_ai == total_results and history_has_ai:
        return {
            "status": "completed",
            "results_processed": results_with_ai,
            "total_results": total_results,
        }
    elif results_with_ai > 0:
        return {
            "status": "partial",
            "results_processed": results_with_ai,
            "total_results": total_results,
        }
    else:
        return {
            "status": "not_started",
            "results_processed": 0,
            "total_results": total_results,
        }

