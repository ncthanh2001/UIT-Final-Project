# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Frappe API endpoints for LLM Scheduling Advisor

Provides REST API for:
1. Getting AI-powered scheduling analysis
2. Quick summaries
3. Specific recommendations
"""

import frappe
from frappe import _
from typing import Dict, Any


@frappe.whitelist()
def get_scheduling_advice(
    scheduling_run: str,
    language: str = "vi",
    custom_prompt: str = None,
    api_key: str = None
) -> Dict[str, Any]:
    """
    Get AI-powered advice for a scheduling run.

    Args:
        scheduling_run: APS Scheduling Run name
        language: Response language (vi=Vietnamese, en=English)
        custom_prompt: Custom user prompt/question to ask AI (optional)
        api_key: Optional OpenAI API key (uses settings if not provided)

    Returns:
        Dict with analysis and recommendations:
        {
            "success": bool,
            "scheduling_run": str,
            "analysis": {
                "overall_assessment": str,
                "bottlenecks": [str],
                "suggestions": [str],
                "risks": [str],
                "priorities": [str]
            },
            "raw_response": str,
            "model": str,
            "language": str
        }
    """
    try:
        from uit_aps.scheduling.llm.advisor import SchedulingAdvisor

        # Validate scheduling run exists
        if not frappe.db.exists("APS Scheduling Run", scheduling_run):
            return {
                "success": False,
                "error": _("Scheduling Run '{0}' not found").format(scheduling_run)
            }

        # Create advisor and get analysis
        advisor = SchedulingAdvisor(api_key=api_key)
        result = advisor.analyze_scheduling_run(scheduling_run, language, custom_prompt)

        return result

    except ImportError as e:
        return {
            "success": False,
            "error": _("Missing dependency: {0}. Install with: pip install openai").format(str(e))
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "LLM Advice Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def get_quick_summary(
    scheduling_run: str,
    language: str = "vi",
    api_key: str = None
) -> Dict[str, Any]:
    """
    Get a quick AI-generated summary of scheduling results.

    Args:
        scheduling_run: APS Scheduling Run name
        language: Response language (vi/en)
        api_key: Optional OpenAI API key

    Returns:
        Dict with summary:
        {
            "success": bool,
            "scheduling_run": str,
            "summary": str
        }
    """
    try:
        from uit_aps.scheduling.llm.advisor import SchedulingAdvisor

        # Validate
        if not frappe.db.exists("APS Scheduling Run", scheduling_run):
            return {
                "success": False,
                "error": _("Scheduling Run '{0}' not found").format(scheduling_run)
            }

        advisor = SchedulingAdvisor(api_key=api_key)
        summary = advisor.get_quick_summary(scheduling_run, language)

        return {
            "success": True,
            "scheduling_run": scheduling_run,
            "summary": summary
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "LLM Summary Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def analyze_bottlenecks(
    scheduling_run: str,
    language: str = "vi",
    api_key: str = None
) -> Dict[str, Any]:
    """
    Get AI analysis specifically focused on bottlenecks.

    Args:
        scheduling_run: APS Scheduling Run name
        language: Response language
        api_key: Optional OpenAI API key

    Returns:
        Dict with bottleneck analysis
    """
    try:
        from uit_aps.scheduling.llm.advisor import SchedulingAdvisor

        if not frappe.db.exists("APS Scheduling Run", scheduling_run):
            return {
                "success": False,
                "error": _("Scheduling Run '{0}' not found").format(scheduling_run)
            }

        advisor = SchedulingAdvisor(api_key=api_key)
        data = advisor._load_scheduling_data(scheduling_run)

        if not data:
            return {
                "success": False,
                "error": _("Failed to load scheduling data")
            }

        # Focus prompt on bottlenecks
        if language == "vi":
            prompt = f"""Phân tích điểm nghẽn (bottleneck) trong lịch trình sản xuất:

Workstation Load:
"""
            for ws, load in data['workstation_load'].items():
                late_pct = round(load['late_count'] / max(load['count'], 1) * 100, 1)
                prompt += f"- {ws}: {load['count']} ops, {round(load['total_mins']/60, 1)}h, {late_pct}% trễ\n"

            prompt += f"""
Tổng: {data['total_operations']} operations, {data['late_operations']} trễ ({100-data['on_time_rate']}%)

Hãy xác định:
1. Workstation nào là điểm nghẽn chính?
2. Tại sao nó là điểm nghẽn?
3. Giải pháp cụ thể để giảm tải?

Trả lời ngắn gọn bằng tiếng Việt."""
        else:
            prompt = f"""Analyze bottlenecks in production schedule:

Workstation Load:
"""
            for ws, load in data['workstation_load'].items():
                late_pct = round(load['late_count'] / max(load['count'], 1) * 100, 1)
                prompt += f"- {ws}: {load['count']} ops, {round(load['total_mins']/60, 1)}h, {late_pct}% late\n"

            prompt += f"""
Total: {data['total_operations']} operations, {data['late_operations']} late ({100-data['on_time_rate']}%)

Identify:
1. Which workstation is the main bottleneck?
2. Why is it a bottleneck?
3. Specific solutions to reduce load?

Respond concisely in English."""

        if not advisor.client:
            return {
                "success": False,
                "error": _("OpenAI client not initialized")
            }

        response = advisor.client.chat.completions.create(
            model=advisor.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500
        )

        return {
            "success": True,
            "scheduling_run": scheduling_run,
            "bottleneck_analysis": response.choices[0].message.content,
            "workstation_load": data['workstation_load']
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Bottleneck Analysis Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def get_improvement_suggestions(
    scheduling_run: str,
    focus_area: str = "all",
    language: str = "vi",
    api_key: str = None
) -> Dict[str, Any]:
    """
    Get specific improvement suggestions.

    Args:
        scheduling_run: APS Scheduling Run name
        focus_area: Area to focus on (all, efficiency, on_time, utilization)
        language: Response language
        api_key: Optional OpenAI API key

    Returns:
        Dict with improvement suggestions
    """
    try:
        from uit_aps.scheduling.llm.advisor import SchedulingAdvisor

        if not frappe.db.exists("APS Scheduling Run", scheduling_run):
            return {
                "success": False,
                "error": _("Scheduling Run '{0}' not found").format(scheduling_run)
            }

        advisor = SchedulingAdvisor(api_key=api_key)
        data = advisor._load_scheduling_data(scheduling_run)

        if not data:
            return {
                "success": False,
                "error": _("Failed to load scheduling data")
            }

        # Build focus-specific prompt
        focus_prompts = {
            "efficiency": "hiệu suất và giảm makespan" if language == "vi" else "efficiency and reducing makespan",
            "on_time": "tăng tỷ lệ đúng hạn" if language == "vi" else "improving on-time delivery rate",
            "utilization": "tối ưu sử dụng máy móc" if language == "vi" else "optimizing machine utilization",
            "all": "tổng thể" if language == "vi" else "overall improvement"
        }

        focus_text = focus_prompts.get(focus_area, focus_prompts["all"])

        if language == "vi":
            prompt = f"""Đưa ra 5 đề xuất cải thiện CỤ THỂ cho lịch trình sản xuất, tập trung vào: {focus_text}

Thông tin:
- Tổng operations: {data['total_operations']}
- Trễ: {data['late_operations']} ({100-data['on_time_rate']}%)
- Makespan: {data['makespan_hours']} giờ
- Số workstations: {len(data['workstation_load'])}

Mỗi đề xuất cần:
- Cụ thể và khả thi
- Ước tính mức độ cải thiện (%)
- Bước thực hiện đầu tiên

Trả lời bằng tiếng Việt."""
        else:
            prompt = f"""Provide 5 SPECIFIC improvement suggestions for production schedule, focusing on: {focus_text}

Data:
- Total operations: {data['total_operations']}
- Late: {data['late_operations']} ({100-data['on_time_rate']}%)
- Makespan: {data['makespan_hours']} hours
- Workstations: {len(data['workstation_load'])}

Each suggestion should:
- Be specific and actionable
- Estimate improvement (%)
- Include first action step

Respond in English."""

        if not advisor.client:
            return {
                "success": False,
                "error": _("OpenAI client not initialized")
            }

        response = advisor.client.chat.completions.create(
            model=advisor.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )

        return {
            "success": True,
            "scheduling_run": scheduling_run,
            "focus_area": focus_area,
            "suggestions": response.choices[0].message.content
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Improvement Suggestions Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def check_llm_status() -> Dict[str, Any]:
    """
    Check if LLM advisor is properly configured.

    Returns:
        Dict with configuration status
    """
    try:
        from uit_aps.scheduling.llm.advisor import SchedulingAdvisor

        advisor = SchedulingAdvisor()

        has_api_key = bool(advisor.api_key)
        has_client = advisor.client is not None

        # Test connection if configured
        connection_ok = False
        if has_client:
            try:
                # Simple test call
                response = advisor.client.models.list()
                connection_ok = True
            except Exception as e:
                connection_ok = False

        return {
            "success": True,
            "status": {
                "api_key_configured": has_api_key,
                "client_initialized": has_client,
                "connection_ok": connection_ok,
                "model": advisor.model
            },
            "message": _("LLM Advisor is ready") if connection_ok else _("LLM Advisor needs configuration")
        }

    except ImportError:
        return {
            "success": False,
            "error": _("OpenAI package not installed. Run: pip install openai")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
