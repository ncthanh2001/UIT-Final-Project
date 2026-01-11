# CLAUDE.md - UIT APS (Advanced Planning & Scheduling)

## Project Overview

**UIT APS** là một Frappe/ERPNext app để lập lịch sản xuất nâng cao (Advanced Planning & Scheduling) cho ERPNext Manufacturing module. Sử dụng OR-Tools, AI/ML để tối ưu hóa lịch sản xuất.

## Cấu trúc Project

```
UIT-Final-Project/
├── uit_aps/                    # Main Frappe app
│   ├── scheduling/             # Core scheduling engine
│   │   ├── api/               # REST APIs
│   │   │   └── scheduling_api.py   # Main scheduling endpoints
│   │   ├── solver/            # OR-Tools constraint programming
│   │   │   ├── ortools_solver.py   # CP-SAT solver
│   │   │   └── fifo_baseline.py    # FIFO baseline comparison
│   │   ├── data/              # Data loaders
│   │   │   └── erpnext_loader.py   # Load từ ERPNext
│   │   ├── models/            # Data models
│   │   │   └── scheduling_models.py
│   │   ├── llm/               # AI/LLM integration
│   │   │   └── llm_api.py     # OpenAI GPT integration
│   │   ├── gnn/               # Graph Neural Network
│   │   │   └── gnn_api.py     # Bottleneck prediction
│   │   ├── rl/                # Reinforcement Learning
│   │   │   └── training_api.py
│   │   ├── reports/           # Excel export & reports
│   │   │   ├── excel_exporter.py
│   │   │   └── report_api.py
│   │   └── demo/              # Demo data generator
│   │       └── demo_data_generator.py
│   └── uit_aps/               # Frappe DocTypes & Pages
│       ├── doctype/
│       │   ├── aps_scheduling_run/     # Main scheduling run DocType
│       │   ├── aps_scheduled_job/      # Scheduled job result
│       │   └── aps_settings/           # App settings
│       └── page/
│           ├── aps_gantt_chart/        # Gantt chart visualization
│           └── aps_demo_dashboard/     # Demo dashboard UI
```

## Các API Endpoints Đã Tạo

### Scheduling APIs (`uit_aps.scheduling.api.scheduling_api`)
- `run_ortools_scheduling()` - Chạy OR-Tools solver
- `reschedule_on_breakdown()` - Lập lịch lại khi máy hỏng
- `get_affected_operations()` - Lấy các job bị ảnh hưởng
- `simulate_breakdown_scenario()` - Mô phỏng sự cố máy

### Report APIs (`uit_aps.scheduling.reports.report_api`)
- `export_comparison_excel()` - Export báo cáo so sánh APS vs FIFO
- `export_gantt_excel()` - Export Gantt data ra Excel
- `get_report_preview()` - Preview báo cáo
- `compare_scheduling_runs()` - So sánh 2 scheduling runs

### Demo APIs (`uit_aps.scheduling.demo.demo_data_generator`)
- `generate_demo_data()` - Tạo 3 Production Plans demo
- `cleanup_demo_data()` - Xóa demo data
- `get_demo_status()` - Kiểm tra demo data status

### LLM APIs (`uit_aps.scheduling.llm.llm_api`)
- `get_scheduling_advice()` - AI analysis với GPT
- Hỗ trợ custom prompt, ngôn ngữ vi/en

## Frappe DocTypes

### APS Scheduling Run
- **Fields chính**: production_plan, scheduling_strategy, run_status, makespan_minutes, total_late_jobs
- **Trạng thái**: Pending → Running → Completed/Failed → Pending Approval → Applied
- **Child table**: APS Scheduled Job (kết quả lịch từng job)

### APS Settings
- OpenAI API Key
- Default time limits
- Weights cho objective function

## UI Pages

### APS Demo Dashboard (`/app/aps_demo_dashboard`)
Dashboard với các nút:
- Demo Data: Generate, View Status, Cleanup
- Scheduling: Run, View Gantt, Compare
- Breakdown: Simulate, Reschedule, View Affected
- Reports: Export Excel, Print
- AI: Analysis, Bottleneck Prediction, RL Training

### APS Gantt Chart (`/app/aps_gantt_chart`)
- Gantt chart visualization với frappe-gantt
- Filter theo Production Plan, Workstation

## Constraints đã implement

1. **Machine Eligibility** - Job chỉ chạy trên máy phù hợp
2. **Precedence** - Thứ tự operations trong Work Order
3. **No Overlap** - Máy không chạy 2 job cùng lúc
4. **Working Hours** - Giờ làm việc của Workstation
5. **Due Dates** - Deadline từ Work Order
6. **Setup Time** - Thời gian setup giữa các job

## Development Commands

```bash
# Frappe bench commands
bench start                           # Start development server
bench --site [site] migrate           # Run migrations
bench build --app uit_aps             # Build assets
bench clear-cache                     # Clear cache

# Testing
bench --site [site] console           # Python console

# Trong console
from uit_aps.scheduling.api import scheduling_api
scheduling_api.run_ortools_scheduling(production_plan="PP-00001")
```

## MCP Configuration

File `.claude/settings.json`:
```json
{
  "mcpServers": {
    "frappe": {
      "command": "cmd",
      "args": ["/c", "path/to/.claude/run_mcp.bat"]
    }
  }
}
```

## Server Info
- **Frappe URL**: http://192.168.89.107:8000
- **API Token**: 65b8baab2dd725a:06fe9244ab2190b

## Current Session Notes

### Đang làm:
- Dashboard page `/app/aps_demo_dashboard` - đã fix JS error
- MCP integration với Frappe - đang config

### TODO:
- [ ] Test dashboard page sau khi bench build
- [ ] Hoàn thiện MCP connection
- [ ] Test demo data generation
- [ ] Test Excel export
