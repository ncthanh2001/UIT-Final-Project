# Gantt Chart Integration - Hướng dẫn

## Tổng quan

GanttChart.vue đã được tích hợp để hiển thị dữ liệu thực từ:
1. **Job Card** (expected_start_date, expected_end_date)
2. **APS Scheduling Result** (khi có scheduling_run parameter)
3. **Plant Floor & Workstation** (từ DocType)

## API Endpoints

### 1. Get Gantt Data
```python
uit_aps.scheduling.api.gantt_api.get_job_cards_for_gantt(scheduling_run=None)
```

**Parameters:**
- `scheduling_run` (optional): Name của APS Scheduling Run

**Returns:**
```json
{
  "jobs": [
    {
      "id": "JC-001",
      "jobCode": "SO-00023",
      "operation": "OP-10",
      "machine": "M01",
      "startTime": "2025-01-06 09:00:00",
      "endTime": "2025-01-08 17:00:00",
      "durationHours": 40,
      "status": "ontime",
      "progress": 50,
      "priority": "high",
      "jobCard": "JC-001"
    }
  ],
  "workstations": [
    {
      "floor": "Floor A - Assembly",
      "description": "Main assembly line",
      "workstations": [
        {
          "id": "WS-001",
          "name": "CNC Machine 01",
          "status": "Production",
          "utilization": 87
        }
      ]
    }
  ],
  "kpi": {
    "makespan": 12,
    "lateJobs": 2,
    "avgUtilization": 78,
    "scheduleStability": 85
  },
  "schedulingRun": {
    "name": "SCH-RUN-001",
    "status": "Complete",
    "startTime": "2025-01-06",
    "productionPlan": "PP-001"
  }
}
```

## Cách sử dụng

### 1. Xem tất cả Job Cards
```
http://localhost:8000/gantt
```
→ Hiển thị tất cả Job Cards có expected_start_date/expected_end_date

### 2. Xem Scheduled Jobs từ APS Scheduling Run
```
http://localhost:8000/gantt?scheduling_run=SCH-RUN-2025-01-06-0001
```
→ Hiển thị jobs đã được schedule bởi APS Scheduling Run

### 3. Từ APS Scheduling Run DocType
Trong `aps_scheduling_run.js`, thêm button:

```javascript
frappe.ui.form.on('APS Scheduling Run', {
    refresh(frm) {
        if (frm.doc.run_status === 'Complete') {
            frm.add_custom_button(__('View Gantt Chart'), function() {
                frappe.set_route('gantt', { scheduling_run: frm.doc.name });
            });
        }
    }
});
```

## Data Flow

### Mode 1: All Job Cards (không có scheduling_run)
```
Job Card
  ├─ expected_start_date
  ├─ expected_end_date
  ├─ workstation
  ├─ operation
  └─ work_order
```

### Mode 2: Scheduled Jobs (có scheduling_run)
```
APS Scheduling Run
  └─ APS Scheduling Result (child table)
      ├─ job_card (Link)
      ├─ workstation
      ├─ scheduled_start_time
      ├─ scheduled_end_time
      ├─ duration_hours
      └─ priority
```

### Workstations Data
```
Plant Floor
  └─ Workstation (filtered by plant_floor)
      ├─ workstation_name
      ├─ status (Production/Idle/Maintenance)
      └─ production_capacity
```

## Status Colors

### Risk Status
- **ontime** (green): Job on track
- **atrisk** (yellow): Behind schedule or low slack
- **late** (red): Past due date

### Workstation Status
- **Production** (green dot): Running
- **Idle** (gray dot): Not producing
- **Maintenance** (yellow dot): Under maintenance

## KPI Calculation

### 1. Makespan
- Từ Scheduling Run: `run_doc.makespan_days`
- Default: Unique work orders count

### 2. Late Jobs
- Từ Scheduling Run: `run_doc.total_late_jobs`
- Default: Count jobs với status="late"

### 3. Avg Utilization
- Từ Scheduling Run: `run_doc.avg_machine_utilization`
- Per Workstation: `(active_jobs / capacity) * 100`

### 4. Schedule Stability
- Mock value: 85% (có thể tính từ schedule changes)

## Drag & Drop (Future)

API đã có function để update schedule:

```python
uit_aps.scheduling.api.gantt_api.update_job_schedule(
    job_id="JC-001",
    start_time="2025-01-07 09:00:00",
    end_time="2025-01-09 17:00:00"
)
```

Sẽ update:
- **APS Scheduling Result** nếu job_id là scheduling result
- **Job Card** nếu job_id là job card

## Ví dụ Integration

### 1. Từ Production Plan
```python
# Sau khi tạo Job Cards từ Production Plan
frappe.msgprint(
    "Job Cards created. <a href='/gantt'>View Gantt Chart</a>",
    title="Success"
)
```

### 2. Từ APS Scheduling Run
```python
# Sau khi chạy scheduling
frappe.msgprint(
    f"Scheduling completed. <a href='/gantt?scheduling_run={run.name}'>View Gantt Chart</a>",
    title="Success"
)
```

### 3. Button trong List View
```javascript
// In APS Scheduling Run list view
frappe.listview_settings['APS Scheduling Run'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Gantt View'), function() {
            frappe.set_route('gantt');
        });
    }
};
```

## Testing

### 1. Test với Job Cards
```python
# Tạo test Job Card
doc = frappe.get_doc({
    "doctype": "Job Card",
    "work_order": "WO-001",
    "operation": "Cutting",
    "workstation": "CNC-01",
    "expected_start_date": "2025-01-06 09:00:00",
    "expected_end_date": "2025-01-08 17:00:00"
})
doc.insert()
```

### 2. Test với Scheduling Run
```python
# Chạy scheduling
from uit_aps.scheduling.api.scheduling_api import run_ortools_scheduling

result = run_ortools_scheduling(
    production_plan="PP-001",
    scheduling_strategy="Forward Scheduling"
)

print(f"View: /gantt?scheduling_run={result['scheduling_run']}")
```

## Notes

- Gantt Chart tự động calculate `startDay` và `startHour` từ timestamps
- Base date là hôm qua (để thấy timeline)
- Hours working: 8:00 - 20:00 (12 hours/shift)
- View modes: Quarter Day, Half Day, Day, Week, Month, Year
- AI Recommendations panel giữ nguyên (sẽ bổ sung sau)

## Troubleshooting

### Không thấy jobs
- Check Job Cards có `expected_start_date` không
- Check permissions trên Job Card
- Check console logs

### Không thấy workstations
- Check Plant Floor và Workstation đã tạo chưa
- Check field `plant_floor` trong Workstation

### KPI = 0
- Với Job Cards: KPI tính từ data thực tế (có thể = 0)
- Với Scheduling Run: Check các fields `makespan_days`, `total_late_jobs`, etc.










