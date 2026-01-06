# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
LLM Scheduling Advisor

Uses OpenAI GPT models to analyze scheduling results and provide
actionable recommendations for production planning.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime, cint, flt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json


class SchedulingAdvisor:
    """
    LLM-powered advisor for scheduling analysis and recommendations.

    Uses OpenAI API to analyze scheduling results and provide:
    - Performance insights
    - Bottleneck identification
    - Optimization suggestions
    - Risk warnings
    """

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the advisor.

        Args:
            api_key: OpenAI API key (if None, reads from settings)
            model: OpenAI model to use (if None, reads from settings)
        """
        self.api_key = api_key or self._get_api_key()
        self.model = model or self._get_model()
        self.client = None

        if self.api_key:
            self._init_client()

    def _get_api_key(self) -> Optional[str]:
        """Get OpenAI API key from Frappe settings."""
        # Try multiple sources for API key

        # 1. Try APS Chatgpt Settings doctype (primary source)
        if frappe.db.exists("DocType", "APS Chatgpt Settings"):
            api_key = frappe.db.get_single_value("APS Chatgpt Settings", "api_key")
            if api_key:
                return api_key

        # 2. Try site_config.json
        api_key = frappe.conf.get("openai_api_key")
        if api_key:
            return api_key

        # 3. Try environment variable
        import os
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            return api_key

        return None

    def _get_model(self) -> str:
        """Get LLM model from settings or use default."""
        # Default to gpt-4o-mini for cost efficiency
        # Can be extended to read from APS Chatgpt Settings if model field is added
        return "gpt-4o-mini"

    def _init_client(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            frappe.log_error(
                "OpenAI package not installed. Run: pip install openai",
                "LLM Advisor - Import Error"
            )
            self.client = None

    def analyze_scheduling_run(
        self,
        scheduling_run: str,
        language: str = "vi"
    ) -> Dict[str, Any]:
        """
        Analyze a scheduling run and provide recommendations.

        Args:
            scheduling_run: APS Scheduling Run name
            language: Response language (vi=Vietnamese, en=English)

        Returns:
            Dict with analysis results and recommendations
        """
        if not self.client:
            return {
                "success": False,
                "error": _("OpenAI client not initialized. Check API key configuration.")
            }

        # Load scheduling data
        data = self._load_scheduling_data(scheduling_run)
        if not data:
            return {
                "success": False,
                "error": _("Failed to load scheduling data")
            }

        # Build analysis prompt
        prompt = self._build_analysis_prompt(data, language)

        # Get LLM response
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(language)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )

            advice = response.choices[0].message.content

            # Parse structured response if possible
            parsed = self._parse_response(advice)

            return {
                "success": True,
                "scheduling_run": scheduling_run,
                "analysis": parsed,
                "raw_response": advice,
                "model": self.model,
                "language": language
            }

        except Exception as e:
            frappe.log_error(str(e), "LLM Advisor - API Error")
            return {
                "success": False,
                "error": str(e)
            }

    def _load_scheduling_data(self, scheduling_run: str) -> Optional[Dict]:
        """Load and prepare scheduling data for analysis."""
        try:
            run_doc = frappe.get_doc("APS Scheduling Run", scheduling_run)

            # Get scheduling results
            results = frappe.get_all(
                "APS Scheduling Result",
                filters={"scheduling_run": scheduling_run},
                fields=[
                    "name", "job_card", "workstation", "operation",
                    "planned_start_time", "planned_end_time", "is_late"
                ],
                order_by="planned_start_time asc"
            )

            # Calculate metrics
            total_ops = len(results)
            late_ops = sum(1 for r in results if r.is_late)

            # Group by workstation
            workstation_load = {}
            for r in results:
                ws = r.workstation or "Unassigned"
                if ws not in workstation_load:
                    workstation_load[ws] = {
                        "count": 0,
                        "total_mins": 0,
                        "late_count": 0
                    }
                workstation_load[ws]["count"] += 1
                if r.planned_start_time and r.planned_end_time:
                    duration = (r.planned_end_time - r.planned_start_time).total_seconds() / 60
                    workstation_load[ws]["total_mins"] += duration
                if r.is_late:
                    workstation_load[ws]["late_count"] += 1

            # Get time range
            start_times = [r.planned_start_time for r in results if r.planned_start_time]
            end_times = [r.planned_end_time for r in results if r.planned_end_time]

            schedule_start = min(start_times) if start_times else None
            schedule_end = max(end_times) if end_times else None

            makespan_mins = 0
            if schedule_start and schedule_end:
                makespan_mins = (schedule_end - schedule_start).total_seconds() / 60

            # Get job details
            job_cards = []
            for r in results[:20]:  # Limit to first 20 for prompt size
                try:
                    jc = frappe.get_doc("Job Card", r.job_card)
                    job_cards.append({
                        "job_card": r.job_card,
                        "work_order": jc.work_order,
                        "item": jc.production_item,
                        "operation": r.operation,
                        "workstation": r.workstation,
                        "start": r.planned_start_time.isoformat() if r.planned_start_time else None,
                        "end": r.planned_end_time.isoformat() if r.planned_end_time else None,
                        "is_late": r.is_late
                    })
                except Exception:
                    pass

            return {
                "scheduling_run": scheduling_run,
                "production_plan": run_doc.production_plan,
                "run_date": run_doc.run_date,
                "strategy": run_doc.scheduling_strategy,
                "total_operations": total_ops,
                "late_operations": late_ops,
                "on_time_rate": round((total_ops - late_ops) / max(total_ops, 1) * 100, 1),
                "makespan_minutes": round(makespan_mins),
                "makespan_hours": round(makespan_mins / 60, 1),
                "workstation_load": workstation_load,
                "schedule_start": schedule_start.isoformat() if schedule_start else None,
                "schedule_end": schedule_end.isoformat() if schedule_end else None,
                "job_details": job_cards
            }

        except Exception as e:
            frappe.log_error(str(e), "LLM Advisor - Data Load Error")
            return None

    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt based on language."""
        if language == "vi":
            return """Bạn là chuyên gia tư vấn lập lịch sản xuất (Production Scheduling Expert).
Nhiệm vụ của bạn là phân tích kết quả lập lịch và đưa ra lời khuyên hữu ích cho quản lý sản xuất.

Khi phân tích, hãy tập trung vào:
1. Đánh giá hiệu suất tổng thể
2. Xác định các điểm nghẽn (bottleneck)
3. Đề xuất cải thiện cụ thể
4. Cảnh báo rủi ro tiềm ẩn
5. Ưu tiên hành động

Trả lời bằng tiếng Việt, ngắn gọn và dễ hiểu.
Sử dụng bullet points và heading để dễ đọc.
Đưa ra các con số và phần trăm cụ thể khi phân tích."""
        else:
            return """You are a Production Scheduling Expert.
Your task is to analyze scheduling results and provide actionable recommendations.

Focus on:
1. Overall performance assessment
2. Bottleneck identification
3. Specific improvement suggestions
4. Risk warnings
5. Action priorities

Respond in clear, concise English.
Use bullet points and headings for readability.
Include specific numbers and percentages in your analysis."""

    def _build_analysis_prompt(self, data: Dict, language: str) -> str:
        """Build the analysis prompt with scheduling data."""
        if language == "vi":
            prompt = f"""Phân tích kết quả lập lịch sản xuất sau:

## Thông tin tổng quan
- Scheduling Run: {data['scheduling_run']}
- Production Plan: {data['production_plan']}
- Ngày chạy: {data['run_date']}
- Chiến lược: {data['strategy']}

## Metrics
- Tổng số operations: {data['total_operations']}
- Operations trễ: {data['late_operations']}
- Tỷ lệ đúng hạn: {data['on_time_rate']}%
- Makespan: {data['makespan_hours']} giờ ({data['makespan_minutes']} phút)
- Thời gian bắt đầu: {data['schedule_start']}
- Thời gian kết thúc: {data['schedule_end']}

## Tải trạm làm việc (Workstation Load)
"""
            for ws, load in data['workstation_load'].items():
                late_pct = round(load['late_count'] / max(load['count'], 1) * 100, 1)
                prompt += f"- {ws}: {load['count']} operations, {round(load['total_mins']/60, 1)} giờ, {late_pct}% trễ\n"

            prompt += f"""
## Chi tiết công việc (mẫu {len(data['job_details'])} đầu tiên)
"""
            for jc in data['job_details'][:10]:
                status = "TRỄ" if jc['is_late'] else "OK"
                prompt += f"- [{status}] {jc['item']} | {jc['operation']} | {jc['workstation']} | {jc['start']} → {jc['end']}\n"

            prompt += """
---
Hãy phân tích và đưa ra:
1. **Đánh giá tổng quan**: Lịch trình này tốt hay cần cải thiện?
2. **Điểm nghẽn**: Workstation nào đang quá tải?
3. **Đề xuất cải thiện**: 3-5 hành động cụ thể để cải thiện
4. **Cảnh báo rủi ro**: Các vấn đề tiềm ẩn cần lưu ý
5. **Ưu tiên hành động**: Việc gì nên làm trước?
"""
        else:
            prompt = f"""Analyze the following production scheduling results:

## Overview
- Scheduling Run: {data['scheduling_run']}
- Production Plan: {data['production_plan']}
- Run Date: {data['run_date']}
- Strategy: {data['strategy']}

## Metrics
- Total Operations: {data['total_operations']}
- Late Operations: {data['late_operations']}
- On-Time Rate: {data['on_time_rate']}%
- Makespan: {data['makespan_hours']} hours ({data['makespan_minutes']} minutes)
- Schedule Start: {data['schedule_start']}
- Schedule End: {data['schedule_end']}

## Workstation Load
"""
            for ws, load in data['workstation_load'].items():
                late_pct = round(load['late_count'] / max(load['count'], 1) * 100, 1)
                prompt += f"- {ws}: {load['count']} ops, {round(load['total_mins']/60, 1)}h work, {late_pct}% late\n"

            prompt += f"""
## Job Details (first {len(data['job_details'])} samples)
"""
            for jc in data['job_details'][:10]:
                status = "LATE" if jc['is_late'] else "OK"
                prompt += f"- [{status}] {jc['item']} | {jc['operation']} | {jc['workstation']} | {jc['start']} → {jc['end']}\n"

            prompt += """
---
Please provide:
1. **Overall Assessment**: Is this schedule good or needs improvement?
2. **Bottlenecks**: Which workstations are overloaded?
3. **Improvement Suggestions**: 3-5 specific actions to improve
4. **Risk Warnings**: Potential issues to watch out for
5. **Action Priorities**: What should be done first?
"""

        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        # Try to extract sections from the response
        sections = {
            "overall_assessment": "",
            "bottlenecks": [],
            "suggestions": [],
            "risks": [],
            "priorities": []
        }

        current_section = None
        lines = response.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            lower_line = line.lower()

            # Detect section headers
            if any(x in lower_line for x in ["đánh giá tổng quan", "overall assessment", "tổng quan"]):
                current_section = "overall_assessment"
            elif any(x in lower_line for x in ["điểm nghẽn", "bottleneck", "quá tải"]):
                current_section = "bottlenecks"
            elif any(x in lower_line for x in ["đề xuất", "suggestion", "cải thiện", "improvement"]):
                current_section = "suggestions"
            elif any(x in lower_line for x in ["cảnh báo", "rủi ro", "risk", "warning"]):
                current_section = "risks"
            elif any(x in lower_line for x in ["ưu tiên", "priority", "hành động"]):
                current_section = "priorities"
            elif current_section:
                # Add content to current section
                if line.startswith(("-", "*", "•", "+")):
                    line = line.lstrip("-*•+ ")

                if current_section == "overall_assessment":
                    if sections["overall_assessment"]:
                        sections["overall_assessment"] += " " + line
                    else:
                        sections["overall_assessment"] = line
                elif current_section in sections and isinstance(sections[current_section], list):
                    if line and not line.startswith("#"):
                        sections[current_section].append(line)

        return sections

    def get_quick_summary(
        self,
        scheduling_run: str,
        language: str = "vi"
    ) -> str:
        """
        Get a quick one-paragraph summary of the scheduling results.

        Args:
            scheduling_run: APS Scheduling Run name
            language: Response language

        Returns:
            Summary string
        """
        if not self.client:
            return _("LLM not available. Check OpenAI API key configuration.")

        data = self._load_scheduling_data(scheduling_run)
        if not data:
            return _("Failed to load scheduling data")

        if language == "vi":
            prompt = f"""Tóm tắt ngắn gọn (2-3 câu) về kết quả lập lịch:
- Tổng: {data['total_operations']} operations
- Trễ: {data['late_operations']} ({100 - data['on_time_rate']}%)
- Makespan: {data['makespan_hours']} giờ
- Workstations: {len(data['workstation_load'])}

Chỉ đưa ra 2-3 câu tóm tắt ngắn gọn bằng tiếng Việt."""
        else:
            prompt = f"""Provide a brief 2-3 sentence summary of scheduling results:
- Total: {data['total_operations']} operations
- Late: {data['late_operations']} ({100 - data['on_time_rate']}%)
- Makespan: {data['makespan_hours']} hours
- Workstations: {len(data['workstation_load'])}

Only provide 2-3 sentences in English."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"


def get_scheduling_advice(
    scheduling_run: str,
    language: str = "vi",
    api_key: str = None
) -> Dict[str, Any]:
    """
    Convenience function to get scheduling advice.

    Args:
        scheduling_run: APS Scheduling Run name
        language: Response language (vi/en)
        api_key: Optional OpenAI API key

    Returns:
        Dict with analysis and recommendations
    """
    advisor = SchedulingAdvisor(api_key=api_key)
    return advisor.analyze_scheduling_run(scheduling_run, language)
