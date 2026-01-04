# HUONG DAN SU DUNG FORECAST MODELS

## 1. CAI DAT

### 1.1. Cai dat cac thu vien can thiet

```bash
# Vao bench directory
cd /path/to/frappe-bench

# Activate virtual environment
source env/bin/activate

# Cai dat cac package
pip install numpy pandas scikit-learn statsmodels prophet
pip install openai

```

### 1.2. Cap nhat DocTypes

Ban can apply cac JSON files moi cho DocTypes:

1. **APS Forecast Result**: Su dung file `aps_forecast_result_NEW.json`
2. **APS Forecast History**: Su dung file `aps_forecast_history_NEW.json`
3. **APS Forecast History Item**: Tao child doctype tu file `APS_FORECAST_HISTORY_ITEM_CHILD.json`

Cach apply:

```bash
# Copy cac file JSON vao thu muc doctype tuong ung
# Sau do chay migrate
bench --site [site-name] migrate
```

---

## 2. CAC MODEL

### 2.1. ARIMA Model

- **File**: `apps/uit_aps/uit_aps/ml/arima_model.py`
- **Phu hop cho**: Time series co tinh stationary, seasonal patterns
- **Uu diem**: Tot cho du lieu co trend va seasonality
- **Nhuoc diem**: Can nhieu du lieu (>30 data points), tinh toan cham

### 2.2. Linear Regression Model

- **File**: `apps/uit_aps/uit_aps/ml/linear_regression_model.py`
- **Phu hop cho**: Trend tuyen tinh, du lieu don gian
- **Uu diem**: Nhanh, don gian, de hieu
- **Nhuoc diem**: Khong xu ly tot seasonality

### 2.3. Prophet Model

- **File**: `apps/uit_aps/uit_aps/ml/prophet.py`
- **Phu hop cho**: Du lieu co seasonality phuc tap, missing data
- **Uu diem**: Tu dong phat hien seasonality, xu ly outliers tot
- **Nhuoc diem**: Can cai dat thu vien Prophet

---

## 3. CACH SU DUNG

### 3.1. Chay forecast cho 1 item

```python
import frappe
from uit_aps.uit_api.run_model import run_forecast

# Chay forecast cho 1 item cu the
result = run_forecast(
    model_name="ARIMA",  # hoac "Linear Regression", "Prophet"
    company="Your Company",
    item_code="ITEM-001",
    forecast_horizon_days=30,  # Du doan 30 ngay
    training_period_days=180,  # Su dung 180 ngay du lieu
    warehouse=None  # Optional
)

print(result)
```

### 3.2. Chay forecast cho nhieu items

```python
# Chay cho tat ca items trong Sales Orders
result = run_forecast(
    model_name="Prophet",
    company="Your Company",
    forecast_horizon_days=30,
    training_period_days=180,
    item_group="Raw Material"  # Optional: chi forecast nhom nay
)

print(f"Total items: {result['total_items']}")
print(f"Successful: {result['successful']}")
print(f"Failed: {result['failed']}")
```

### 3.3. So sanh cac models

```python
from uit_aps.uit_api.run_model import compare_models

# So sanh ket qua cua 3 models cho cung 1 item
comparison = compare_models(
    item_code="ITEM-001",
    company="Your Company",
    forecast_horizon_days=30,
    training_period_days=180
)

print(comparison)
```

### 3.4. Goi qua API (REST)

```bash
# Chay forecast
curl -X POST "http://your-site/api/method/uit_aps.uit_api.run_model.run_forecast" \
  -H "Authorization: token YOUR_API_KEY:YOUR_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "ARIMA",
    "company": "Your Company",
    "item_code": "ITEM-001",
    "forecast_horizon_days": 30,
    "training_period_days": 180
  }'

# So sanh models
curl -X POST "http://your-site/api/method/uit_aps.uit_api.run_model.compare_models" \
  -H "Authorization: token YOUR_API_KEY:YOUR_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "item_code": "ITEM-001",
    "company": "Your Company"
  }'
```

---

## 4. XEM KET QUA

### 4.1. Xem tat ca forecast runs

Vao ERPNext > UIT APS > APS Forecast History

Tai day ban co the xem:

- Cac lan chay forecast
- Model duoc su dung
- Thoi gian chay
- So luong items da forecast
- Ty le thanh cong/that bai

### 4.2. Xem chi tiet forecast results

Vao ERPNext > UIT APS > APS Forecast Result

Hoac tu APS Forecast History, click vao "View Results"

Moi result se hien thi:

- Item code
- Forecast quantity
- Confidence score
- Movement type (Fast/Slow/Non Moving)
- Trend type (Upward/Downward/Stable)
- Reorder recommendations
- Model-specific metrics

### 4.3. Lay ket qua qua code

```python
from uit_aps.uit_api.run_model import get_forecast_results

# Lay tat ca results cua 1 history run
results = get_forecast_results(history_name="FCST-RUN-2025-12-22-0001")

for result in results:
    print(f"{result['item']}: {result['forecast_qty']} units")
    print(f"  Confidence: {result['confidence_score']}%")
    print(f"  Movement: {result['movement_type']}")
    if result['reorder_alert']:
        print(f"  ⚠️ REORDER ALERT!")
```

---

## 5. OUTPUT FIELDS

Moi forecast result se co cac fields sau:

### Core Forecast

- `forecast_qty`: So luong du doan
- `confidence_score`: Do tin cay (%)
- `lower_bound`: Bien duoi cua khoang tin cay
- `upper_bound`: Bien tren cua khoang tin cay

### Model Information

- `model_used`: Model da su dung (ARIMA/Linear Regression/Prophet)
- `model_confidence`: Chi so tin cay cua model
- `training_data_points`: So data points da train

### Movement & Trend

- `movement_type`: Fast Moving / Slow Moving / Non Moving
- `daily_avg_consumption`: Tieu thu trung binh hang ngay
- `trend_type`: Upward / Downward / Stable

### Inventory Recommendations

- `reorder_level`: Muc ton kho can dat hang lai
- `suggested_qty`: So luong de xuat dat hang
- `safety_stock`: Ton kho an toan
- `current_stock`: Ton kho hien tai
- `reorder_alert`: Canh bao can dat hang (Yes/No)

### Model-Specific (ARIMA)

- `arima_p`: AR order
- `arima_d`: Differencing order
- `arima_q`: MA order
- `arima_aic`: AIC score

### Model-Specific (Linear Regression)

- `lr_r2_score`: R² score (%)
- `lr_slope`: Do doc cua trend

### Model-Specific (Prophet)

- `prophet_seasonality_detected`: Co phat hien seasonality khong
- `prophet_seasonality_type`: Loai seasonality (Weekly/Monthly/Yearly)
- `prophet_changepoint_count`: So diem thay doi trend

### Explanations

- `forecast_explanation`: Giai thich chi tiet
- `recommendations`: Khuyen nghi hanh dong
- `notes`: Ghi chu

---

## 6. TUONG TAC VOI HE THONG

### 6.1. Tich hop voi Sales Order

Cac model tu dong lay du lieu tu Sales Order voi `docstatus=1` (da submit).

Du lieu su dung:

- `delivery_date`: Ngay giao hang (de xac dinh demand pattern)
- `qty`: So luong (demand quantity)
- `item_code`: San pham
- `warehouse`: Kho

### 6.2. Lay thong tin ton kho

System tu dong lay:

- Current stock tu Bin table
- Lead time tu Item Supplier

### 6.3. Auto-update recommendations

Moi forecast se tu dong tinh:

- Reorder level = (Daily avg × Lead time) × Safety factor
- Safety stock = Daily avg × Lead time × 0.3
- Suggested qty = Daily avg × (Forecast period + Lead time)
- Reorder alert = Current stock <= Reorder level

---

## 7. BEST PRACTICES

### 7.1. Chon model phu hop

- **ARIMA**: Du lieu co >60 data points, co seasonality ro rang
- **Linear Regression**: Du lieu co trend tuyen tinh, can ket qua nhanh
- **Prophet**: Du lieu co seasonality phuc tap, missing data, outliers

### 7.2. Training period

- Toi thieu: 90 ngay (3 thang)
- Khuyen nghi: 180 ngay (6 thang)
- Toi uu: 365 ngay (1 nam) - de phat hien seasonality yearly

### 7.3. Forecast horizon

- Short-term: 7-14 ngay
- Medium-term: 30 ngay (1 thang)
- Long-term: 90 ngay (3 thang)

### 7.4. Monitoring

- Chay forecast dinh ky (hang tuan hoac hang thang)
- So sanh actual demand vs predicted demand
- Adjust models neu accuracy thap

---

## 8. TROUBLESHOOTING

### 8.1. "Insufficient data" error

- **Nguyen nhan**: Khong du Sales Orders trong training period
- **Giai phap**: Tang training_period_days hoac kiem tra Sales Orders co docstatus=1

### 8.2. "Prophet packages not available"

- **Nguyen nhan**: Chua cai dat Prophet
- **Giai phap**: `pip install prophet`

### 8.3. Forecast accuracy thap

- **Nguyen nhan**: Du lieu khong tot, seasonality phuc tap
- **Giai phap**:
  - Tang training period
  - Thu model khac
  - Kiem tra data quality

### 8.4. Performance issue

- **Nguyen nhan**: Qua nhieu items, model phuc tap
- **Giai phap**:
  - Chay forecast theo batch (theo item_group)
  - Su dung Linear Regression cho fast results
  - Chay background job

---

## 9. VI DU THUC TE

### 9.1. Forecast cho Raw Materials

```python
# Chay forecast cho tat ca raw materials
result = run_forecast(
    model_name="Prophet",  # Tot cho seasonality
    company="ABC Company",
    item_group="Raw Material",
    forecast_horizon_days=30,
    training_period_days=180
)

# Xem cac items can reorder
reorder_items = frappe.get_all(
    "APS Forecast Result",
    filters={
        "forecast_history": result["history_name"],
        "reorder_alert": 1
    },
    fields=["item", "forecast_qty", "current_stock", "suggested_qty"]
)

for item in reorder_items:
    print(f"⚠️ {item['item']}")
    print(f"   Current: {item['current_stock']}")
    print(f"   Suggested: {item['suggested_qty']}")
```

### 9.2. Weekly forecast routine

```python
# Chay moi thu 2 hang tuan
def weekly_forecast():
    companies = frappe.get_all("Company", pluck="name")

    for company in companies:
        try:
            # Chay Prophet cho all items
            result = run_forecast(
                model_name="Prophet",
                company=company,
                forecast_horizon_days=30,
                training_period_days=180
            )

            # Send notification neu co reorder alerts
            alerts = frappe.db.count(
                "APS Forecast Result",
                filters={
                    "forecast_history": result["history_name"],
                    "reorder_alert": 1
                }
            )

            if alerts > 0:
                # Send email notification
                frappe.sendmail(
                    recipients=["purchasing@company.com"],
                    subject=f"Reorder Alert: {alerts} items need reordering",
                    message=f"Please check APS Forecast Result for {company}"
                )
        except Exception as e:
            frappe.log_error(f"Weekly forecast failed for {company}: {str(e)}")
```

---

## 10. KET LUAN

He thong forecast nay giup ban:

- ✅ Du doan demand tu Sales Order history
- ✅ Tu dong phat hien trend va seasonality
- ✅ Recommendation ve reorder level va quantity
- ✅ So sanh hieu qua cua cac models
- ✅ Luu tru lich su forecast de phan tich

Chuc ban thanh cong! 🚀
