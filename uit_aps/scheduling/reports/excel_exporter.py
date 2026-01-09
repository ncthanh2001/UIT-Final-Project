# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Excel Report Exporter for APS Scheduling

Exports scheduling results and comparisons to Excel format:
- Before/After optimization comparison
- Gantt chart data
- Constraint documentation
- Performance metrics
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, getdate, get_datetime, format_datetime
from datetime import datetime
from typing import Dict, List, Any, Optional
import io


def export_scheduling_comparison_excel(scheduling_run: str) -> Dict[str, Any]:
    """
    Export scheduling comparison report to Excel.

    Args:
        scheduling_run: Name of APS Scheduling Run

    Returns:
        Dict with file data and metadata
    """
    try:
        import xlsxwriter
    except ImportError:
        return {
            "success": False,
            "error": _("xlsxwriter package not installed. Run: pip install xlsxwriter")
        }

    # Validate scheduling run exists
    if not frappe.db.exists("APS Scheduling Run", scheduling_run):
        return {
            "success": False,
            "error": _("Scheduling Run '{0}' not found").format(scheduling_run)
        }

    # Load scheduling run data
    run_doc = frappe.get_doc("APS Scheduling Run", scheduling_run)

    # Load scheduling results
    results = frappe.get_all(
        "APS Scheduling Result",
        filters={"scheduling_run": scheduling_run},
        fields=[
            "job_card", "workstation", "operation",
            "planned_start_time", "planned_end_time",
            "is_late", "delay_reason", "is_applied"
        ],
        order_by="planned_start_time asc"
    )

    # Get original job card data (before optimization)
    original_data = []
    for result in results:
        jc = frappe.get_doc("Job Card", result.job_card)
        original_data.append({
            "job_card": result.job_card,
            "work_order": jc.work_order,
            "operation": jc.operation,
            "workstation": jc.workstation,
            "original_start": jc.expected_start_date,
            "original_end": jc.expected_end_date,
            "optimized_start": result.planned_start_time,
            "optimized_end": result.planned_end_time,
            "optimized_workstation": result.workstation,
            "is_late": result.is_late,
            "delay_reason": result.delay_reason,
            "is_applied": result.is_applied
        })

    # Create Excel file in memory
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})

    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })

    cell_format = workbook.add_format({
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })

    number_format = workbook.add_format({
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'num_format': '#,##0'
    })

    percent_format = workbook.add_format({
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'num_format': '0.0%'
    })

    datetime_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'num_format': 'yyyy-mm-dd hh:mm'
    })

    good_format = workbook.add_format({
        'border': 1,
        'bg_color': '#C6EFCE',
        'font_color': '#006100',
        'align': 'right',
        'valign': 'vcenter'
    })

    bad_format = workbook.add_format({
        'border': 1,
        'bg_color': '#FFC7CE',
        'font_color': '#9C0006',
        'align': 'right',
        'valign': 'vcenter'
    })

    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'left'
    })

    subtitle_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'bg_color': '#D9E2F3',
        'border': 1
    })

    # ========== Sheet 1: Summary ==========
    summary_sheet = workbook.add_worksheet('Summary')
    summary_sheet.set_column('A:A', 35)
    summary_sheet.set_column('B:C', 20)

    row = 0
    summary_sheet.write(row, 0, f"APS Scheduling Report - {scheduling_run}", title_format)
    row += 2

    # Basic Info
    summary_sheet.write(row, 0, "Basic Information", subtitle_format)
    summary_sheet.write(row, 1, "", subtitle_format)
    row += 1

    info_data = [
        ("Production Plan", run_doc.production_plan),
        ("Scheduling Strategy", run_doc.scheduling_strategy),
        ("Scheduling Tier", run_doc.scheduling_tier),
        ("Run Date", format_datetime(run_doc.run_date) if run_doc.run_date else ""),
        ("Executed By", run_doc.executed_by),
        ("Run Status", run_doc.run_status),
        ("Solver Status", run_doc.solver_status),
        ("Solve Time (seconds)", run_doc.solve_time_seconds),
    ]

    for label, value in info_data:
        summary_sheet.write(row, 0, label, cell_format)
        summary_sheet.write(row, 1, value if value else "", cell_format)
        row += 1

    row += 1

    # Optimization Comparison
    summary_sheet.write(row, 0, "Optimization Comparison (FIFO vs APS)", subtitle_format)
    summary_sheet.write(row, 1, "FIFO Baseline", subtitle_format)
    summary_sheet.write(row, 2, "APS Optimized", subtitle_format)
    summary_sheet.write(row, 3, "Improvement", subtitle_format)
    row += 1

    comparison_data = [
        (
            "Makespan (minutes)",
            run_doc.baseline_makespan_minutes,
            run_doc.makespan_minutes,
            run_doc.improvement_makespan_percent
        ),
        (
            "Late Jobs",
            run_doc.baseline_late_jobs,
            run_doc.total_late_jobs,
            run_doc.improvement_late_jobs_percent
        ),
        (
            "Total Tardiness (minutes)",
            run_doc.baseline_total_tardiness,
            run_doc.total_tardiness_minutes,
            run_doc.improvement_tardiness_percent
        ),
    ]

    for label, baseline, optimized, improvement in comparison_data:
        summary_sheet.write(row, 0, label, cell_format)
        summary_sheet.write(row, 1, baseline or 0, number_format)
        summary_sheet.write(row, 2, optimized or 0, number_format)

        # Color code improvement
        if improvement and improvement > 0:
            summary_sheet.write(row, 3, f"+{improvement:.1f}%", good_format)
        elif improvement and improvement < 0:
            summary_sheet.write(row, 3, f"{improvement:.1f}%", bad_format)
        else:
            summary_sheet.write(row, 3, "0.0%", cell_format)
        row += 1

    row += 1

    # Summary Stats
    summary_sheet.write(row, 0, "Summary Statistics", subtitle_format)
    summary_sheet.write(row, 1, "", subtitle_format)
    row += 1

    stats_data = [
        ("Total Job Cards", run_doc.total_job_cards),
        ("Jobs On Time", run_doc.jobs_on_time),
        ("Late Jobs", run_doc.total_late_jobs),
        ("On-Time Rate (%)", f"{(run_doc.jobs_on_time / max(run_doc.total_job_cards, 1) * 100):.1f}%" if run_doc.total_job_cards else "N/A"),
        ("Machine Utilization (%)", f"{run_doc.machine_utilization:.1f}%" if run_doc.machine_utilization else "N/A"),
        ("Optimality Gap (%)", f"{run_doc.gap_percentage:.2f}%" if run_doc.gap_percentage else "N/A"),
    ]

    for label, value in stats_data:
        summary_sheet.write(row, 0, label, cell_format)
        summary_sheet.write(row, 1, value if value else 0, cell_format)
        row += 1

    # ========== Sheet 2: Constraints ==========
    constraints_sheet = workbook.add_worksheet('Constraints')
    constraints_sheet.set_column('A:A', 30)
    constraints_sheet.set_column('B:B', 15)
    constraints_sheet.set_column('C:C', 80)

    row = 0
    constraints_sheet.write(row, 0, "Scheduling Constraints Applied", title_format)
    row += 2

    constraints_sheet.write(row, 0, "Constraint", header_format)
    constraints_sheet.write(row, 1, "Applied", header_format)
    constraints_sheet.write(row, 2, "Description", header_format)
    row += 1

    constraints_data = [
        ("Machine Eligibility", run_doc.constraint_machine_eligibility,
         "Mỗi operation chỉ được lập lịch trên máy (workstation) có khả năng thực hiện operation đó."),
        ("Operation Precedence", run_doc.constraint_precedence,
         "Các operation trong cùng một Work Order phải được thực hiện theo đúng thứ tự quy định trong BOM."),
        ("No Overlap (Machine)", run_doc.constraint_no_overlap,
         "Mỗi máy chỉ có thể xử lý một operation tại một thời điểm."),
        ("Working Hours", run_doc.constraint_working_hours,
         "Lập lịch trong giờ làm việc của workstation (nếu có cấu hình)."),
        ("Due Date Respect", run_doc.constraint_due_dates,
         "Ưu tiên tối ưu hóa để hoàn thành job trước deadline."),
        ("Setup Time", run_doc.constraint_setup_time,
         "Tính thời gian setup/gap giữa các operation trên cùng máy."),
    ]

    for name, applied, desc in constraints_data:
        constraints_sheet.write(row, 0, name, cell_format)
        constraints_sheet.write(row, 1, "Yes" if applied else "No",
                               good_format if applied else cell_format)
        constraints_sheet.write(row, 2, desc, cell_format)
        row += 1

    row += 2

    # Solver Configuration
    constraints_sheet.write(row, 0, "Solver Configuration", subtitle_format)
    constraints_sheet.write(row, 1, "", subtitle_format)
    constraints_sheet.write(row, 2, "", subtitle_format)
    row += 1

    solver_config = [
        ("Time Limit (seconds)", run_doc.time_limit_seconds),
        ("Min Gap Between Ops (mins)", run_doc.min_gap_between_ops),
        ("Makespan Weight", run_doc.makespan_weight),
        ("Tardiness Weight", run_doc.tardiness_weight),
    ]

    for label, value in solver_config:
        constraints_sheet.write(row, 0, label, cell_format)
        constraints_sheet.write(row, 1, value if value else "", cell_format)
        row += 1

    # Full constraints description
    if run_doc.constraints_description:
        row += 2
        constraints_sheet.write(row, 0, "Full Constraints Description:", subtitle_format)
        row += 1
        constraints_sheet.write(row, 0, run_doc.constraints_description, cell_format)

    # ========== Sheet 3: Schedule Comparison ==========
    comparison_sheet = workbook.add_worksheet('Schedule Comparison')
    comparison_sheet.set_column('A:A', 25)  # Job Card
    comparison_sheet.set_column('B:B', 20)  # Work Order
    comparison_sheet.set_column('C:C', 15)  # Operation
    comparison_sheet.set_column('D:D', 18)  # Original Workstation
    comparison_sheet.set_column('E:F', 18)  # Original Start/End
    comparison_sheet.set_column('G:G', 18)  # Optimized Workstation
    comparison_sheet.set_column('H:I', 18)  # Optimized Start/End
    comparison_sheet.set_column('J:J', 10)  # Late
    comparison_sheet.set_column('K:K', 10)  # Applied

    row = 0
    comparison_sheet.write(row, 0, "Before/After Optimization Schedule", title_format)
    row += 2

    # Headers
    headers = [
        "Job Card", "Work Order", "Operation",
        "Original WS", "Original Start", "Original End",
        "Optimized WS", "Optimized Start", "Optimized End",
        "Is Late", "Applied"
    ]
    for col, header in enumerate(headers):
        comparison_sheet.write(row, col, header, header_format)
    row += 1

    # Data rows
    for data in original_data:
        comparison_sheet.write(row, 0, data["job_card"], cell_format)
        comparison_sheet.write(row, 1, data["work_order"], cell_format)
        comparison_sheet.write(row, 2, data["operation"], cell_format)
        comparison_sheet.write(row, 3, data["workstation"] or "", cell_format)

        # Original dates
        if data["original_start"]:
            comparison_sheet.write_datetime(row, 4, get_datetime(data["original_start"]), datetime_format)
        else:
            comparison_sheet.write(row, 4, "", cell_format)

        if data["original_end"]:
            comparison_sheet.write_datetime(row, 5, get_datetime(data["original_end"]), datetime_format)
        else:
            comparison_sheet.write(row, 5, "", cell_format)

        comparison_sheet.write(row, 6, data["optimized_workstation"] or "", cell_format)

        # Optimized dates
        if data["optimized_start"]:
            comparison_sheet.write_datetime(row, 7, get_datetime(data["optimized_start"]), datetime_format)
        else:
            comparison_sheet.write(row, 7, "", cell_format)

        if data["optimized_end"]:
            comparison_sheet.write_datetime(row, 8, get_datetime(data["optimized_end"]), datetime_format)
        else:
            comparison_sheet.write(row, 8, "", cell_format)

        comparison_sheet.write(row, 9, "Yes" if data["is_late"] else "No",
                              bad_format if data["is_late"] else good_format)
        comparison_sheet.write(row, 10, "Yes" if data["is_applied"] else "No",
                              good_format if data["is_applied"] else cell_format)
        row += 1

    # ========== Sheet 4: Gantt Data ==========
    gantt_sheet = workbook.add_worksheet('Gantt Data')
    gantt_sheet.set_column('A:A', 25)
    gantt_sheet.set_column('B:B', 20)
    gantt_sheet.set_column('C:C', 18)
    gantt_sheet.set_column('D:E', 18)
    gantt_sheet.set_column('F:F', 12)
    gantt_sheet.set_column('G:G', 10)

    row = 0
    gantt_sheet.write(row, 0, "Gantt Chart Data (Optimized Schedule)", title_format)
    row += 2

    headers = ["Job Card", "Operation", "Workstation", "Start Time", "End Time", "Duration (mins)", "Late"]
    for col, header in enumerate(headers):
        gantt_sheet.write(row, col, header, header_format)
    row += 1

    for result in results:
        gantt_sheet.write(row, 0, result.job_card, cell_format)
        gantt_sheet.write(row, 1, result.operation, cell_format)
        gantt_sheet.write(row, 2, result.workstation or "", cell_format)

        if result.planned_start_time:
            gantt_sheet.write_datetime(row, 3, get_datetime(result.planned_start_time), datetime_format)
        else:
            gantt_sheet.write(row, 3, "", cell_format)

        if result.planned_end_time:
            gantt_sheet.write_datetime(row, 4, get_datetime(result.planned_end_time), datetime_format)
        else:
            gantt_sheet.write(row, 4, "", cell_format)

        # Calculate duration
        if result.planned_start_time and result.planned_end_time:
            duration = (get_datetime(result.planned_end_time) - get_datetime(result.planned_start_time)).total_seconds() / 60
            gantt_sheet.write(row, 5, int(duration), number_format)
        else:
            gantt_sheet.write(row, 5, "", cell_format)

        gantt_sheet.write(row, 6, "Yes" if result.is_late else "No",
                         bad_format if result.is_late else good_format)
        row += 1

    # ========== Sheet 5: AI Analysis ==========
    if run_doc.llm_analysis_content:
        ai_sheet = workbook.add_worksheet('AI Analysis')
        ai_sheet.set_column('A:A', 100)

        row = 0
        ai_sheet.write(row, 0, "AI Analysis & Recommendations", title_format)
        row += 2

        ai_sheet.write(row, 0, f"Analysis Date: {format_datetime(run_doc.llm_analysis_date) if run_doc.llm_analysis_date else 'N/A'}", cell_format)
        row += 1
        ai_sheet.write(row, 0, f"Model Used: {run_doc.llm_analysis_model or 'N/A'}", cell_format)
        row += 2

        ai_sheet.write(row, 0, "User Prompt:", subtitle_format)
        row += 1
        ai_sheet.write(row, 0, run_doc.llm_analysis_prompt or "", cell_format)
        row += 2

        ai_sheet.write(row, 0, "AI Response:", subtitle_format)
        row += 1

        # Write AI content - handle HTML by stripping tags for Excel
        import re
        plain_text = re.sub('<[^<]+?>', '', run_doc.llm_analysis_content or "")
        ai_sheet.write(row, 0, plain_text, cell_format)

    # Close workbook
    workbook.close()

    # Get file data
    output.seek(0)
    file_data = output.getvalue()

    # Create file in Frappe
    file_name = f"APS_Report_{scheduling_run}_{getdate().strftime('%Y%m%d')}.xlsx"

    _file = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "content": file_data,
        "is_private": 0,
        "attached_to_doctype": "APS Scheduling Run",
        "attached_to_name": scheduling_run
    })
    _file.save(ignore_permissions=True)

    return {
        "success": True,
        "file_url": _file.file_url,
        "file_name": file_name,
        "scheduling_run": scheduling_run
    }


def export_gantt_data_excel(scheduling_run: str) -> Dict[str, Any]:
    """
    Export just the Gantt chart data to Excel (simpler format).

    Args:
        scheduling_run: Name of APS Scheduling Run

    Returns:
        Dict with file data and metadata
    """
    try:
        import xlsxwriter
    except ImportError:
        return {
            "success": False,
            "error": _("xlsxwriter package not installed. Run: pip install xlsxwriter")
        }

    # Validate scheduling run exists
    if not frappe.db.exists("APS Scheduling Run", scheduling_run):
        return {
            "success": False,
            "error": _("Scheduling Run '{0}' not found").format(scheduling_run)
        }

    # Load scheduling results
    results = frappe.get_all(
        "APS Scheduling Result",
        filters={"scheduling_run": scheduling_run},
        fields=[
            "job_card", "workstation", "operation",
            "planned_start_time", "planned_end_time",
            "is_late", "is_applied"
        ],
        order_by="planned_start_time asc"
    )

    # Create Excel file
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})

    # Formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'border': 1
    })
    cell_format = workbook.add_format({'border': 1})
    datetime_format = workbook.add_format({
        'border': 1,
        'num_format': 'yyyy-mm-dd hh:mm'
    })

    # Create worksheet
    worksheet = workbook.add_worksheet('Gantt Data')
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 15)
    worksheet.set_column('C:C', 18)
    worksheet.set_column('D:E', 18)
    worksheet.set_column('F:F', 10)

    # Headers
    headers = ["Job Card", "Operation", "Workstation", "Start", "End", "Late"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)

    # Data
    for row, result in enumerate(results, start=1):
        worksheet.write(row, 0, result.job_card, cell_format)
        worksheet.write(row, 1, result.operation, cell_format)
        worksheet.write(row, 2, result.workstation or "", cell_format)

        if result.planned_start_time:
            worksheet.write_datetime(row, 3, get_datetime(result.planned_start_time), datetime_format)
        if result.planned_end_time:
            worksheet.write_datetime(row, 4, get_datetime(result.planned_end_time), datetime_format)

        worksheet.write(row, 5, "Yes" if result.is_late else "No", cell_format)

    workbook.close()

    # Get file data
    output.seek(0)
    file_data = output.getvalue()

    file_name = f"Gantt_{scheduling_run}_{getdate().strftime('%Y%m%d')}.xlsx"

    _file = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "content": file_data,
        "is_private": 0,
        "attached_to_doctype": "APS Scheduling Run",
        "attached_to_name": scheduling_run
    })
    _file.save(ignore_permissions=True)

    return {
        "success": True,
        "file_url": _file.file_url,
        "file_name": file_name,
        "scheduling_run": scheduling_run
    }
