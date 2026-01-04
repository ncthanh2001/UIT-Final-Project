# THIET KE APS PRODUCTION PLAN

## 1. TONG QUAN

**APS Production Plan** la chuc nang tu dong tao ke hoach san xuat dua tren ket qua du bao tu **APS Forecast**.

### 1.1. Luu do hoat dong

```
1. User chon Forecast History (da Complete)
   ↓
2. System auto-fill plan_from_period, plan_to_period, company
   ↓
3. User chon time_granularity (Monthly/Quarterly)
   ↓
4. User click "Generate from Forecast"
   ↓
5. System:
   - Lay tat ca Forecast Results tu Forecast History
   - Group theo item
   - Tinh planned_qty cho moi item
   - Phan bo theo time_granularity
   - Tao Production Plan Items
   - Tinh capacity status
   ↓
6. User review va adjust neu can
   ↓
7. User submit Production Plan
```

## 2. CAU TRUC FILE

### 2.1. Files da tao

```
apps/uit_aps/uit_aps/
├── utils/
│   └── production_plan_helper.py       ← TAO MOI: Helper functions
├── uit_api/
│   └── production_plan.py              ← TAO MOI: API methods
└── uit_aps/doctype/aps_production_plan/
    ├── aps_production_plan.py           ← SUA: Validate logic
    └── aps_production_plan.js           ← SUA: UI handlers
```

### 2.2. Helper Functions (`production_plan_helper.py`)

- `calculate_planned_qty()`: Tinh so luong san xuat can thiet
- `get_item_lead_time()`: Lay lead time cua item
- `calculate_planned_start_date()`: Tinh ngay bat dau san xuat
- `get_monthly_periods()`: Lay danh sach cac thang
- `get_quarterly_periods()`: Lay danh sach cac quy
- `find_closest_forecast_result()`: Tim forecast result gan nhat
- `get_current_stock()`: Lay ton kho hien tai

### 2.3. API Methods (`production_plan.py`)

- `generate_production_plan_from_forecast()`: Tao Production Plan tu Forecast
- `get_forecast_period()`: Lay thong tin period tu Forecast History
- `refresh_plan_items()`: Refresh items trong Production Plan

## 3. CONG THUC TINH TOAN

### 3.1. Planned Quantity

```python
# Planned Qty = Forecast Demand - Current Stock + Safety Stock
# Neu Forecast Demand < Current Stock thi planned_qty = Safety Stock

net_demand = forecast_qty - current_stock

if net_demand <= 0:
    planned_qty = max(safety_stock, 0)
else:
    planned_qty = net_demand + safety_stock
```

### 3.2. Phan bo theo Time Granularity

- **Monthly**: Chia forecast qty theo thang, tinh theo so ngay trong moi thang
- **Quarterly**: Chia forecast qty theo quy, tinh theo so ngay trong moi quy

### 3.3. Planned Start Date

```python
planned_start_date = period_start - lead_time_days
```

## 4. CACH SU DUNG

### 4.1. Qua UI

1. Tao Production Plan moi
2. Chon **Forecast History** (se auto-fill period va company)
3. Chon **Time Granularity** (Monthly/Quarterly)
4. Click button **"Generate from Forecast"**
5. System se tu dong tao cac items
6. Review va adjust neu can
7. Submit Production Plan

### 4.2. Qua API

```python
import frappe
from uit_aps.uit_api.production_plan import generate_production_plan_from_forecast

result = generate_production_plan_from_forecast(
    forecast_history="FCST-RUN-2025-01-15-0001",
    plan_name="Ke hoach Q1 2025",
    plan_from_period="2025-01-01",
    plan_to_period="2025-03-31",
    time_granularity="Monthly",
    company="Your Company"
)

print(result)
# {
#     "success": True,
#     "production_plan": "PROD-PLAN-2025-01-15-0001",
#     "items_created": 45
# }
```

### 4.3. Refresh Items

```python
from uit_aps.uit_api.production_plan import refresh_plan_items

result = refresh_plan_items("PROD-PLAN-2025-01-15-0001")
```

## 5. VALIDATION

### 5.1. Production Plan Level

- `plan_from_period` phai truoc `plan_to_period`
- Neu `source_type = "Forecast"` thi phai co `forecast_history`
- Forecast History phai co status = "Complete"

### 5.2. Production Plan Item Level

- `planned_qty` khong duoc am
- `item` la required
- `plan_period` la required

## 6. STATUS WORKFLOW

```
Draft → Planned → Released → Completed
         ↓
      Cancelled
```

- **Draft**: Ke hoach dang duoc tao/chinh sua
- **Planned**: Ke hoach da duoc submit, san sang cho MRP/Scheduling
- **Released**: Ke hoach da duoc release cho san xuat
- **Completed**: Ke hoach da hoan thanh
- **Cancelled**: Ke hoach da bi huy

## 7. TINH NANG MO RONG (TODO)

### 7.1. Capacity Checking

- Tich hop voi **APS Work Shift** de check capacity
- Tich hop voi **APS Machine Downtime** de check availability
- Tinh toan capacity status (OK/Overloaded)

### 7.2. Integration voi MRP

- Tu Production Plan co the trigger MRP Run
- Link Production Plan voi MRP Result

### 7.3. Integration voi Scheduling

- Tu Production Plan co the trigger Scheduling Run
- Link Production Plan voi Scheduling Result

## 8. NOTES

- Production Plan items se duoc tao tu dong khi generate
- User co the manual edit items sau khi generate
- Refresh items se xoa tat ca items cu va tao lai
- Forecast Results phai co status = "Complete" moi co the tao Production Plan

