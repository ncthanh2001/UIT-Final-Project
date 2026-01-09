# Kịch Bản Test Hệ Thống Hybrid APS

## Tổng Quan

Tài liệu này mô tả các kịch bản test end-to-end cho hệ thống Hybrid APS, bao gồm:
1. Dự báo nhu cầu → Lên kế hoạch sản xuất
2. Kiểm tra NVL → Tạo đơn mua hàng → Nhập kho
3. Production Plan → OR-Tools tối ưu lịch trình
4. Xử lý sự cố máy hỏng (RL Agent)
5. Training RL Agent từ dữ liệu thực

---

## Kịch Bản 1: Dự Báo Nhu Cầu → Lên Kế Hoạch

### Mục tiêu
Test chức năng dự báo nhu cầu và tự động tạo kế hoạch sản xuất.

### Dữ liệu test
```
Sản phẩm: TP-GN16-001 (Giường Ngủ Gỗ Sồi 1m6)
Lịch sử bán hàng: 30 đơn hàng trong 3 tháng qua
Dự báo: 15 sản phẩm cho tháng tới
```

### Các bước thực hiện

#### Bước 1: Tạo Sales Orders (Dữ liệu đầu vào)
```python
# API call via MCP
{
    "doctype": "Sales Order",
    "customer": "Khách hàng A",
    "delivery_date": "2026-01-20",
    "items": [
        {
            "item_code": "TP-GN16-001",
            "qty": 5,
            "rate": 15000000
        }
    ]
}
```

#### Bước 2: Chạy Forecast
```
URL: http://192.168.110.146:8000/app/aps-forecast-run
1. Chọn Item Group: "Giuong"
2. Forecast Period: 30 ngày
3. Forecast Method: "Auto" (tự động chọn model tốt nhất)
4. Click "Run Forecast"
```

#### Bước 3: Kiểm tra kết quả
- Xem `APS Forecast Result` → So sánh dự báo với thực tế
- Accuracy Score >= 70%
- MAPE (Mean Absolute Percentage Error) < 30%

#### Bước 4: Tạo Production Plan từ Forecast
```
1. Vào APS Production Plan
2. Get Items From: "Forecast"
3. Chọn Forecast Result vừa tạo
4. Click "Get Finished Goods for Manufacture"
5. Submit Production Plan
```

### Kết quả mong đợi
| Metric | Expected |
|--------|----------|
| Forecast Accuracy | >= 70% |
| Production Plan Created | Yes |
| Work Orders Generated | 15 |

---

## Kịch Bản 2: Kiểm Tra NVL → Mua Hàng → Nhập Kho

### Mục tiêu
Test quy trình MRP: kiểm tra nguyên vật liệu, tạo đề xuất mua hàng, và nhập kho.

### Dữ liệu test
```
Sản phẩm: TP-GN16-001 (Giường Ngủ Gỗ Sồi 1m6)
BOM gồm:
  - Go Soi Thanh 5x10x200cm: 8 thanh/giường
  - Oc Vit 5x50mm: 40 con/giường
  - Keo Dan Go: 0.5 lít/giường
  - Giay Nham P120: 2 tờ/giường

Số lượng sản xuất: 10 giường
Tồn kho hiện tại:
  - Go Soi: 50 thanh (cần 80, thiếu 30)
  - Oc Vit: 500 con (đủ)
  - Keo: 3 lít (cần 5, thiếu 2)
  - Giấy nhám: 30 tờ (đủ)
```

### Các bước thực hiện

#### Bước 1: Chạy MRP Check
```
URL: http://192.168.110.146:8000/app/aps-mrp-run

1. Chọn Production Plan: "MFG-PP-2026-00006"
2. Click "Run MRP Check"
3. Hệ thống phân tích BOM và tồn kho
```

#### Bước 2: Xem kết quả MRP
```
APS MRP Result sẽ hiển thị:
┌─────────────────────┬──────────┬──────────┬──────────┬──────────┐
│ Nguyên vật liệu     │ Cần      │ Tồn kho  │ Thiếu    │ Đề xuất  │
├─────────────────────┼──────────┼──────────┼──────────┼──────────┤
│ Go Soi Thanh        │ 80       │ 50       │ 30       │ Mua      │
│ Oc Vit 5x50mm       │ 400      │ 500      │ 0        │ Đủ       │
│ Keo Dan Go          │ 5 lít    │ 3 lít    │ 2 lít    │ Mua      │
│ Giay Nham P120      │ 20 tờ    │ 30 tờ    │ 0        │ Đủ       │
└─────────────────────┴──────────┴──────────┴──────────┴──────────┘
```

#### Bước 3: Tạo Purchase Order
```python
# Từ APS Purchase Suggestion, tạo PO:
{
    "doctype": "Purchase Order",
    "supplier": "NCC Go Soi",
    "items": [
        {
            "item_code": "NVL-GS-001",
            "qty": 30,
            "rate": 150000,
            "warehouse": "Kho NVL - UIT"
        }
    ],
    "schedule_date": "2026-01-12"
}
```

#### Bước 4: Nhận hàng và nhập kho
```python
# Tạo Purchase Receipt
{
    "doctype": "Purchase Receipt",
    "supplier": "NCC Go Soi",
    "items": [
        {
            "item_code": "NVL-GS-001",
            "qty": 30,
            "warehouse": "Kho NVL - UIT",
            "purchase_order": "PO-00001"
        }
    ]
}
```

#### Bước 5: Xác nhận tồn kho đủ
```
1. Vào Stock Balance Report
2. Filter: Item = "NVL-GS-001"
3. Xác nhận: Qty = 80 (50 cũ + 30 mới)
4. Quay lại MRP Run → "Recheck Material"
5. Kết quả: "All materials available"
```

### Kết quả mong đợi
| Bước | Expected Result |
|------|-----------------|
| MRP Check | Identify 2 shortages |
| Purchase Suggestion | 2 items suggested |
| PO Created | 2 Purchase Orders |
| PR Completed | Stock updated |
| Recheck | All materials available |

---

## Kịch Bản 3: Production Plan → OR-Tools Tối Ưu

### Mục tiêu
Test quy trình tối ưu hóa lịch trình sản xuất bằng OR-Tools.

### Dữ liệu test
```
Production Plan: MFG-PP-2026-00006
Work Orders: 10 đơn
Job Cards: 40 công việc (4 công đoạn/sản phẩm)
Workstations: 8 máy
  - May Phay CNC 01 (capacity: 1)
  - May Bao 2 Mat 01 (capacity: 1)
  - May Bao 2 Mat 02 (capacity: 1)
  - Phong Son (capacity: 3)
  - May Khoan (capacity: 2)
  - May Cua (capacity: 1)
  - Ban Lap Rap 01 (capacity: 2)
  - Ban Lap Rap 02 (capacity: 2)
```

### Các bước thực hiện

#### Bước 1: Tạo APS Scheduling Run
```
URL: http://192.168.110.146:8000/app/aps-scheduling-run/new

1. Production Plan: MFG-PP-2026-00006
2. Scheduling Strategy: "Hybrid (OR-Tools + RL)"
3. Optimization Objective:
   - Minimize Makespan: Weight = 0.4
   - Minimize Tardiness: Weight = 0.4
   - Maximize Utilization: Weight = 0.2
4. Solver Time Limit: 60 seconds
5. Click "Run Scheduling"
```

#### Bước 2: Theo dõi quá trình solving
```
Console/Log sẽ hiển thị:
[INFO] Loading 40 operations, 8 machines
[INFO] Building CP-SAT model...
[INFO] Adding precedence constraints: 30
[INFO] Adding no-overlap constraints: 8
[INFO] Adding capacity constraints: 2
[INFO] Solving... Time limit: 60s
[INFO] Solution found: OPTIMAL
[INFO] Makespan: 2880 minutes (48 hours)
[INFO] Tardiness: 0 minutes
[INFO] Utilization: 78%
```

#### Bước 3: Xem kết quả scheduling
```
APS Scheduling Result sẽ hiển thị Gantt Chart:

Timeline: Jan 7 - Jan 9, 2026
┌────────────────────────────────────────────────────────────┐
│ May Phay CNC 01  [JOB001-Op1][JOB002-Op1][JOB003-Op1]...  │
│ May Bao 01       [JOB001-Op2]     [JOB002-Op2]    ...      │
│ May Bao 02            [JOB004-Op2][JOB005-Op2]    ...      │
│ Phong Son        [J1][J2][J3]  [J4][J5][J6]  [J7][J8]...  │
│ Ban Lap Rap 01   ...          [JOB001-Op4][JOB002-Op4]    │
│ Ban Lap Rap 02   ...          [JOB003-Op4][JOB004-Op4]    │
└────────────────────────────────────────────────────────────┘
```

#### Bước 4: Apply schedule vào ERPNext
```
1. Click "Apply Schedule"
2. Hệ thống cập nhật:
   - Job Card: expected_start_date, expected_end_date
   - Workstation assignment
3. Xác nhận trong Job Card List
```

#### Bước 5: So sánh với baseline
```
So sánh kết quả OR-Tools vs Heuristics:

┌─────────────────┬───────────┬───────────┬───────────┐
│ Metric          │ OR-Tools  │ FCFS      │ EDD       │
├─────────────────┼───────────┼───────────┼───────────┤
│ Makespan (hrs)  │ 48        │ 72        │ 56        │
│ Tardiness (hrs) │ 0         │ 8         │ 2         │
│ Utilization %   │ 78%       │ 52%       │ 65%       │
└─────────────────┴───────────┴───────────┴───────────┘
```

### Kết quả mong đợi
| Metric | Expected |
|--------|----------|
| Solution Status | OPTIMAL or FEASIBLE |
| Makespan Improvement | >= 20% vs FCFS |
| Zero Tardiness | Yes (if possible) |
| No Constraint Violations | Yes |

---

## Kịch Bản 4: Máy Hỏng → RL Agent Xử Lý

### Mục tiêu
Test khả năng RL Agent xử lý disruption khi máy hỏng đột ngột.

### Dữ liệu test
```
Trạng thái ban đầu:
- Schedule đang chạy theo kế hoạch
- May Bao 2 Mat 01 đang chạy JOB005-Op2
- Queue: JOB006-Op2, JOB007-Op2, JOB008-Op2

Sự kiện:
- Thời điểm: 10:30 AM
- Máy: May Bao 2 Mat 01
- Loại sự cố: Breakdown (hỏng motor)
- Dự kiến sửa: 4 giờ
```

### Các bước thực hiện

#### Bước 1: Tạo Downtime Entry
```python
# Tạo record máy hỏng
{
    "doctype": "Downtime Entry",
    "workstation": "May Bao 2 Mat 01",
    "from_time": "2026-01-08 10:30:00",
    "to_time": "2026-01-08 14:30:00",  # Dự kiến 4 giờ
    "stop_reason": "Breakdown",
    "remarks": "Motor hỏng, đang chờ thay"
}
```

#### Bước 2: Trigger RL Agent
```
URL: http://192.168.110.146:8000/api/method/uit_aps.scheduling.rl.realtime_api.handle_disruption

Request:
{
    "scheduling_run": "profoqg0m2",
    "disruption_type": "machine_breakdown",
    "affected_machine": "May Bao 2 Mat 01",
    "expected_downtime_mins": 240
}
```

#### Bước 3: RL Agent phân tích và quyết định
```
RL Agent sẽ:

1. Observe State:
   - Machine "May Bao 2 Mat 01": BREAKDOWN
   - Affected jobs: JOB005 (đang chạy), JOB006, JOB007, JOB008 (queue)
   - Alternative machines: "May Bao 2 Mat 02" (utilization: 60%)
   - Slack time của affected jobs: JOB005 (+2h), JOB006 (+4h), JOB007 (+1h), JOB008 (+6h)

2. Evaluate Actions:
   - ACTION_1: Migrate jobs to May Bao 02
     → Estimated delay: 30 mins (setup time)
     → Risk: May overload May Bao 02

   - ACTION_2: Wait for repair
     → Estimated delay: 240 mins
     → Risk: JOB007 will be late

   - ACTION_3: Trigger full re-schedule
     → Estimated delay: 0 (optimal)
     → Cost: High computation, disruption to other jobs

3. Decision: ACTION_1 (Migrate to May Bao 02)
   - Reason: Balances delay vs disruption
   - Confidence: 85%
```

#### Bước 4: Execute Action
```python
# RL Agent thực hiện migration
{
    "action_type": "MIGRATE_JOB",
    "job_card": "PO-JOB00205",
    "from_machine": "May Bao 2 Mat 01",
    "to_machine": "May Bao 2 Mat 02",
    "new_start_time": "2026-01-08 10:45:00"
}
```

#### Bước 5: Verify kết quả
```
Kiểm tra sau khi RL Agent xử lý:

1. Job Cards đã được update:
   - JOB005-Op2: workstation = "May Bao 2 Mat 02"
   - JOB006-Op2: workstation = "May Bao 2 Mat 02", start += 30min

2. Không có job nào bị trễ deadline

3. Utilization của May Bao 02: 75% → 90%

4. Reward received: +15 (job migrated successfully, no tardiness)
```

### Kết quả mong đợi
| Metric | Expected |
|--------|----------|
| Response Time | < 5 seconds |
| Jobs Migrated | 4 |
| New Tardiness | 0 |
| Decision Confidence | >= 70% |

---

## Kịch Bản 5: Training RL Agent

### Mục tiêu
Test quy trình training RL Agent từ dữ liệu lịch sử và simulation.

### Dữ liệu test
```
Training Data:
- 50 historical scheduling runs
- 200 disruption events (máy hỏng, rush orders, delays)
- Baseline performance từ OR-Tools

Training Config:
- Agent Type: PPO
- Episodes: 500
- Learning Rate: 0.0003
- Gamma (Discount): 0.99
```

### Các bước thực hiện

#### Bước 1: Chuẩn bị Training Data
```python
# Lấy historical data từ ERPNext
historical_runs = frappe.get_all("APS Scheduling Run",
    filters={"status": "Completed"},
    fields=["name", "production_plan", "makespan", "tardiness", "utilization"]
)

# Lấy disruption events
disruptions = frappe.get_all("Downtime Entry",
    filters={"from_time": [">", "2025-01-01"]},
    fields=["workstation", "from_time", "to_time", "stop_reason"]
)
```

#### Bước 2: Configure Training
```
URL: http://192.168.110.146:8000/app/aps-scheduling-run/profoqg0m2

1. Click "Train RL Agent"
2. Dialog mở ra:
   - Agent Type: PPO
   - Max Episodes: 500
   - Learning Rate: 0.0003
   - Discount Factor (Gamma): 0.99
3. Click "Start Training"
```

#### Bước 3: Monitor Training Progress
```
Training Progress Dialog hiển thị:

┌──────────────────────────────────────────────────────────┐
│  RL Agent Training Progress                              │
├──────────────────────────────────────────────────────────┤
│  Status: Running                                         │
│  Episode: 125 / 500                                      │
│  Progress: [████████████░░░░░░░░░░░░░░] 25%             │
│                                                          │
│  Metrics:                                                │
│  ├─ Best Reward: 156.4                                  │
│  ├─ Avg Reward (last 100): 89.2                         │
│  ├─ Best Makespan: 2650 mins                            │
│  └─ Best Tardiness: 45 mins                             │
│                                                          │
│  Speed: 2.5 episodes/sec                                │
│  Est. Time Remaining: 2.5 mins                          │
└──────────────────────────────────────────────────────────┘
```

#### Bước 4: Xem Training History
```
Sau khi training xong:

APS RL Training Log:
┌────────────┬────────┬─────────┬─────────────┬────────────┐
│ Timestamp  │ Agent  │ Episodes│ Best Reward │ Status     │
├────────────┼────────┼─────────┼─────────────┼────────────┤
│ 2026-01-09 │ PPO    │ 500     │ 245.8       │ Completed  │
│ 2026-01-08 │ PPO    │ 300     │ 198.2       │ Completed  │
│ 2026-01-07 │ SAC    │ 500     │ 212.5       │ Completed  │
└────────────┴────────┴─────────┴─────────────┴────────────┘

Model được lưu tại:
- Best: private/files/rl_models/ppo/best/
- History: private/files/rl_models/ppo/history/20260109_143025/
```

#### Bước 5: Evaluate Trained Agent
```
1. Click "Evaluate Agent"
2. Chọn số scenarios: 20
3. So sánh với heuristics: EDD, FCFS, SPT

Kết quả:
┌─────────────────┬───────────┬───────────┬───────────┬───────────┐
│ Metric          │ RL Agent  │ EDD       │ FCFS      │ SPT       │
├─────────────────┼───────────┼───────────┼───────────┼───────────┤
│ Avg Reward      │ 156.4     │ 98.2      │ 85.6      │ 92.1      │
│ Makespan (min)  │ 2720      │ 3100      │ 3450      │ 3200      │
│ Tardiness (min) │ 45        │ 120       │ 180       │ 95        │
│ Win Rate        │ 85%       │ 45%       │ 30%       │ 40%       │
└─────────────────┴───────────┴───────────┴───────────┴───────────┘

RL Agent tốt hơn heuristics trong 85% scenarios!
```

### Kết quả mong đợi
| Metric | Expected |
|--------|----------|
| Training Completed | Yes |
| Final Reward | > Baseline |
| Model Saved | Yes |
| Win Rate vs Heuristics | >= 70% |

---

## Kịch Bản 6: End-to-End Full Workflow

### Mục tiêu
Test toàn bộ quy trình từ đầu đến cuối.

### Timeline
```
Day 1 (Monday):
  08:00 - Forecast chạy, dự báo nhu cầu tuần tới
  09:00 - MRP check, phát hiện thiếu NVL
  10:00 - Tạo PO cho NVL thiếu

Day 2 (Tuesday):
  08:00 - Nhận NVL, nhập kho
  09:00 - Production Plan được tạo
  10:00 - OR-Tools tối ưu lịch trình
  11:00 - Apply schedule, bắt đầu sản xuất

Day 3 (Wednesday):
  10:30 - Máy Bào 01 hỏng!
  10:31 - RL Agent detect và xử lý
  10:35 - Jobs được migrate sang máy khác
  14:30 - Máy Bào 01 sửa xong, trở lại hoạt động

Day 4 (Thursday):
  14:00 - Rush order đến (5 sản phẩm, giao trong 2 ngày)
  14:05 - RL Agent quyết định insert rush order
  14:10 - Partial re-schedule cho affected jobs

Day 5 (Friday):
  17:00 - Sản xuất hoàn thành
  17:30 - Review KPIs, training data collected
  18:00 - RL Agent được retrain với data mới
```

### Verification Checklist

```
□ Forecast accuracy >= 70%
□ MRP correctly identified shortages
□ PO created and received on time
□ OR-Tools found optimal/feasible solution
□ Schedule applied to Job Cards
□ Machine breakdown handled within 5 mins
□ No jobs missed deadline due to breakdown
□ Rush order inserted without major disruption
□ RL Agent training completed
□ New model performance >= old model
```

---

## Script Tự Động Test

### test_full_workflow.py
```python
"""
Automated test script for Hybrid APS system
Run: python test_full_workflow.py
"""

import frappe
import requests
from datetime import datetime, timedelta

# Config
SITE_URL = "http://192.168.110.146:8000"
API_KEY = "65b8baab2dd725a"
API_SECRET = "7428569c4a26f6a"

headers = {
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Content-Type": "application/json"
}

def test_forecast():
    """Test 1: Forecast"""
    print("=" * 50)
    print("TEST 1: FORECAST")
    print("=" * 50)

    # Create forecast run
    response = requests.post(
        f"{SITE_URL}/api/method/uit_aps.forecast.api.run_forecast",
        headers=headers,
        json={
            "item_group": "Giuong",
            "forecast_days": 30,
            "method": "auto"
        }
    )

    result = response.json()
    assert result.get("message", {}).get("success"), "Forecast failed"
    print(f"✓ Forecast completed. Accuracy: {result['message']['accuracy']}%")
    return result["message"]["forecast_run"]

def test_mrp_check(production_plan):
    """Test 2: MRP Check"""
    print("\n" + "=" * 50)
    print("TEST 2: MRP CHECK")
    print("=" * 50)

    response = requests.post(
        f"{SITE_URL}/api/method/uit_aps.mrp.api.run_mrp",
        headers=headers,
        json={"production_plan": production_plan}
    )

    result = response.json()
    assert result.get("message", {}).get("success"), "MRP check failed"

    shortages = result["message"]["shortages"]
    print(f"✓ MRP completed. Found {len(shortages)} shortages")
    return shortages

def test_scheduling(scheduling_run):
    """Test 3: OR-Tools Scheduling"""
    print("\n" + "=" * 50)
    print("TEST 3: OR-TOOLS SCHEDULING")
    print("=" * 50)

    response = requests.post(
        f"{SITE_URL}/api/method/uit_aps.scheduling.api.run_scheduling",
        headers=headers,
        json={
            "scheduling_run": scheduling_run,
            "strategy": "hybrid",
            "time_limit": 60
        }
    )

    result = response.json()
    assert result.get("message", {}).get("success"), "Scheduling failed"

    print(f"✓ Scheduling completed")
    print(f"  Makespan: {result['message']['makespan']} mins")
    print(f"  Tardiness: {result['message']['tardiness']} mins")
    return result["message"]

def test_machine_breakdown(scheduling_run):
    """Test 4: Machine Breakdown Handling"""
    print("\n" + "=" * 50)
    print("TEST 4: MACHINE BREAKDOWN")
    print("=" * 50)

    # Simulate breakdown
    response = requests.post(
        f"{SITE_URL}/api/method/uit_aps.scheduling.rl.realtime_api.handle_disruption",
        headers=headers,
        json={
            "scheduling_run": scheduling_run,
            "disruption_type": "machine_breakdown",
            "affected_machine": "May Bao 2 Mat 01",
            "expected_downtime_mins": 240
        }
    )

    result = response.json()
    assert result.get("message", {}).get("success"), "Disruption handling failed"

    print(f"✓ Disruption handled")
    print(f"  Action: {result['message']['action']}")
    print(f"  Jobs migrated: {result['message']['jobs_affected']}")
    return result["message"]

def test_rl_training(scheduling_run):
    """Test 5: RL Agent Training"""
    print("\n" + "=" * 50)
    print("TEST 5: RL TRAINING")
    print("=" * 50)

    response = requests.post(
        f"{SITE_URL}/api/method/uit_aps.scheduling.rl.training_api.start_training",
        headers=headers,
        json={
            "scheduling_run": scheduling_run,
            "agent_type": "ppo",
            "max_episodes": 100,
            "learning_rate": 0.0003,
            "gamma": 0.99
        }
    )

    result = response.json()
    assert result.get("message", {}).get("success"), "Training failed to start"

    training_log = result["message"]["training_log"]
    print(f"✓ Training started: {training_log}")

    # Wait for completion (polling)
    import time
    while True:
        progress = requests.get(
            f"{SITE_URL}/api/method/uit_aps.scheduling.rl.training_api.get_training_progress",
            headers=headers,
            params={"training_log": training_log}
        ).json()

        status = progress["message"]["status"]
        if status == "Completed":
            print(f"✓ Training completed!")
            print(f"  Best Reward: {progress['message']['best_reward']}")
            break
        elif status == "Failed":
            raise Exception("Training failed")

        print(f"  Progress: {progress['message']['progress']}%")
        time.sleep(5)

    return progress["message"]

def main():
    print("=" * 60)
    print("   HYBRID APS SYSTEM - AUTOMATED TEST SUITE")
    print("=" * 60)

    try:
        # Run tests
        test_forecast()
        test_mrp_check("MFG-PP-2026-00006")
        test_scheduling("profoqg0m2")
        test_machine_breakdown("profoqg0m2")
        test_rl_training("profoqg0m2")

        print("\n" + "=" * 60)
        print("   ALL TESTS PASSED!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        raise

if __name__ == "__main__":
    main()
```

---

## Appendix: API Endpoints Reference

### Forecast APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/method/uit_aps.forecast.api.run_forecast` | POST | Chạy dự báo |
| `/api/method/uit_aps.forecast.api.get_forecast_result` | GET | Lấy kết quả |

### MRP APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/method/uit_aps.mrp.api.run_mrp` | POST | Chạy MRP check |
| `/api/method/uit_aps.mrp.api.get_suggestions` | GET | Lấy đề xuất mua |

### Scheduling APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/method/uit_aps.scheduling.api.run_scheduling` | POST | Chạy OR-Tools |
| `/api/method/uit_aps.scheduling.api.apply_schedule` | POST | Apply kết quả |

### RL Agent APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/method/uit_aps.scheduling.rl.realtime_api.handle_disruption` | POST | Xử lý sự cố |
| `/api/method/uit_aps.scheduling.rl.realtime_api.get_recommendation` | GET | Lấy khuyến nghị |
| `/api/method/uit_aps.scheduling.rl.training_api.start_training` | POST | Bắt đầu training |
| `/api/method/uit_aps.scheduling.rl.training_api.get_training_progress` | GET | Xem tiến trình |
| `/api/method/uit_aps.scheduling.rl.evaluation_api.evaluate_agent` | POST | Đánh giá agent |
