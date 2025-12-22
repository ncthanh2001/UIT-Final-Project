# FORECAST MODELS - TONG KET THAY DOI

## 📋 TONG QUAN

Da hoan thanh viec thiet ke lai 3 models (ARIMA, Linear Regression, Prophet) de su dung du lieu tu **Sales Order** (docstatus=1) thay vi Stock Ledger Entry.

---

## ✅ CAC FILE DA TAO/SUA

### 1. Models (DA SUA)
- ✅ `apps/uit_aps/uit_aps/ml/arima_model.py` - ARIMA model
- ✅ `apps/uit_aps/uit_aps/ml/linear_regression_model.py` - Linear Regression model  
- ✅ `apps/uit_aps/uit_aps/ml/prophet.py` - Prophet model (TAO MOI)

### 2. Helper & API Files (TAO MOI)
- ✅ `apps/uit_aps/uit_aps/ml/data_helper.py` - Helper functions lay du lieu Sales Order
- ✅ `apps/uit_aps/uit_aps/uit_api/run_model.py` - Main API de chay forecast va luu ket qua

### 3. DocType Definitions (TAO MOI)
- ✅ `apps/uit_aps/uit_aps/uit_aps/doctype/aps_forecast_result/aps_forecast_result_NEW.json`
- ✅ `apps/uit_aps/uit_aps/uit_aps/doctype/aps_forecast_history/aps_forecast_history_NEW.json`
- ✅ `apps/uit_aps/APS_FORECAST_HISTORY_ITEM_CHILD.json`

### 4. Documentation (TAO MOI)
- ✅ `apps/uit_aps/DESIGN_APS_FORECAST.md` - Thiet ke chi tiet
- ✅ `apps/uit_aps/HUONG_DAN_SU_DUNG.md` - Huong dan su dung
- ✅ `apps/uit_aps/README_FORECAST_MODELS.md` - File nay

---

## 🔄 THAY DOI CHINH

### Truoc day:
- Su dung Stock Ledger Entry (actual_qty < 0)
- Output don gian: predicted_consumption, movement_type, confidence_score
- Khong luu vao database

### Bay gio:
- ✅ Su dung Sales Order Items (docstatus=1)
- ✅ Output day du: 30+ fields bao gom model metrics, inventory recommendations
- ✅ Tu dong luu vao APS Forecast Result va APS Forecast History
- ✅ Phat hien trend va seasonality
- ✅ Tinh confidence intervals (lower_bound, upper_bound)
- ✅ Khuyen nghi reorder level, safety stock, suggested qty

---

## 📊 CAC FIELDS OUTPUT MOI

### APS Forecast Result (30+ fields)

**Basic Info:**
- item, item_group, forecast_period, forecast_history
- company, warehouse

**Core Forecast:**
- forecast_qty, confidence_score
- lower_bound, upper_bound

**Model Info:**
- model_used (ARIMA/Linear Regression/Prophet)
- model_confidence
- training_data_points

**Movement & Trend:**
- movement_type (Fast/Slow/Non Moving)
- daily_avg_consumption
- trend_type (Upward/Downward/Stable)

**Inventory Recommendations:**
- reorder_level
- suggested_qty
- safety_stock
- current_stock
- reorder_alert

**ARIMA Specific:**
- arima_p, arima_d, arima_q
- arima_aic

**Linear Regression Specific:**
- lr_r2_score
- lr_slope

**Prophet Specific:**
- prophet_seasonality_detected
- prophet_seasonality_type
- prophet_changepoint_count

**Explanations:**
- forecast_explanation
- recommendations
- notes

### APS Forecast History (15+ fields)

- run_name, company, model_used
- run_status, run_start_time, run_end_time
- forecast_horizon_days
- training_period_start, training_period_end
- start_date, end_date
- total_items_forecasted
- total_results_generated
- successful_forecasts, failed_forecasts
- avg_confidence_score
- overall_accuracy_mape_
- parameters_json, filters_applied
- forecast_results_summary (child table)

---

## 🚀 CACH SU DUNG

### 1. Cai dat packages

```bash
cd /path/to/frappe-bench
source env/bin/activate
pip install numpy pandas scikit-learn statsmodels prophet
```

### 2. Apply DocTypes

```bash
# Copy cac file JSON vao thu muc doctype tuong ung
# Hoac su dung Frappe Desk de import JSON

# Sau do migrate
bench --site [site-name] migrate
```

### 3. Chay forecast

**Qua Python:**
```python
from uit_aps.uit_api.run_model import run_forecast

result = run_forecast(
    model_name="Prophet",
    company="Your Company",
    forecast_horizon_days=30,
    training_period_days=180,
    item_code="ITEM-001"  # Optional: chi forecast item nay
)
```

**Qua REST API:**
```bash
curl -X POST "http://your-site/api/method/uit_aps.uit_api.run_model.run_forecast" \
  -H "Authorization: token KEY:SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "ARIMA",
    "company": "Your Company",
    "forecast_horizon_days": 30
  }'
```

### 4. So sanh models

```python
from uit_aps.uit_api.run_model import compare_models

comparison = compare_models(
    item_code="ITEM-001",
    company="Your Company"
)
```

---

## 📁 CAU TRUC FILE

```
apps/uit_aps/
├── uit_aps/
│   ├── ml/
│   │   ├── arima_model.py              ← DA SUA
│   │   ├── linear_regression_model.py  ← DA SUA
│   │   ├── prophet.py                  ← TAO MOI
│   │   └── data_helper.py              ← TAO MOI
│   ├── uit_api/
│   │   └── run_model.py                ← TAO MOI
│   └── uit_aps/doctype/
│       ├── aps_forecast_result/
│       │   └── aps_forecast_result_NEW.json  ← TAO MOI
│       └── aps_forecast_history/
│           └── aps_forecast_history_NEW.json ← TAO MOI
├── DESIGN_APS_FORECAST.md              ← TAO MOI
├── HUONG_DAN_SU_DUNG.md               ← TAO MOI
└── README_FORECAST_MODELS.md           ← TAO MOI
```

---

## 🎯 TINH NANG CHINH

### 1. Tu dong lay du lieu Sales Order
- Lay Sales Order Items voi docstatus=1
- Filter theo company, warehouse, item_group
- Su dung delivery_date hoac transaction_date

### 2. 3 Models voi strengths khac nhau
- **ARIMA**: Tot cho seasonality, trend phuc tap
- **Linear Regression**: Nhanh, don gian, tuyen tinh
- **Prophet**: Tu dong phat hien seasonality, xu ly missing data

### 3. Day du metrics va recommendations
- Confidence intervals
- Trend detection
- Movement classification
- Reorder recommendations
- Safety stock calculation

### 4. Luu tru va tracking
- APS Forecast History: Luu thong tin ve lan chay
- APS Forecast Result: Luu chi tiet ket qua cho tung item
- Link giua History va Results

### 5. API endpoints
- `run_forecast()`: Chay forecast cho 1 hoac nhieu items
- `compare_models()`: So sanh 3 models
- `get_forecast_results()`: Lay ket qua

---

## 💡 VI DU SU DUNG

### Vi du 1: Forecast cho tat ca Raw Materials

```python
result = run_forecast(
    model_name="Prophet",
    company="ABC Company",
    item_group="Raw Material",
    forecast_horizon_days=30,
    training_period_days=180
)

print(f"Forecasted {result['successful']} items")
print(f"History: {result['history_name']}")
```

### Vi du 2: Xem items can reorder

```python
reorder_items = frappe.get_all(
    "APS Forecast Result",
    filters={"reorder_alert": 1},
    fields=["item", "current_stock", "suggested_qty", "reorder_level"],
    order_by="forecast_qty desc"
)

for item in reorder_items:
    print(f"⚠️ {item['item']}: Order {item['suggested_qty']} units")
```

### Vi du 3: So sanh 3 models

```python
comparison = compare_models(
    item_code="ITEM-001",
    company="ABC Company"
)

for model, result in comparison['results'].items():
    print(f"\n{model}:")
    print(f"  Forecast: {result.get('forecast_qty')} units")
    print(f"  Confidence: {result.get('confidence_score')}%")
    print(f"  Trend: {result.get('trend_type')}")
```

---

## 📝 NOTES

### Model Recommendations

- **Du lieu it (<30 days)**: Dung Linear Regression
- **Du lieu vua (30-90 days)**: Dung Linear Regression hoac ARIMA
- **Du lieu nhieu (>90 days)**: Dung ARIMA hoac Prophet
- **Co seasonality ro rang**: Dung Prophet
- **Can ket qua nhanh**: Dung Linear Regression

### Data Requirements

- **Toi thieu**: 10 Sales Order Items
- **Khuyen nghi**: 30+ Sales Order Items
- **Toi uu**: 60+ Sales Order Items (2+ months)

### Confidence Score Interpretation

- **>85%**: Rat tin cay, co the su dung truc tiep
- **70-85%**: Tin cay, nen kiem tra them
- **50-70%**: Trung binh, can xem xet
- **<50%**: Thap, khong nen su dung

---

## 🔧 NEXT STEPS

1. ✅ **Apply DocTypes** - Copy JSON files va migrate
2. ✅ **Cai dat packages** - pip install requirements
3. ✅ **Test voi 1 item** - Chay forecast cho 1 item test
4. ⏳ **Setup scheduled job** - Tu dong chay hang tuan
5. ⏳ **Create reports** - Tao reports de visualize results
6. ⏳ **Integration** - Tich hop voi Purchase Order workflow

---

## 📞 SUPPORT

Neu gap van de, hay kiem tra:
1. `HUONG_DAN_SU_DUNG.md` - Huong dan chi tiet
2. `DESIGN_APS_FORECAST.md` - Thiet ke ky thuat
3. Error logs trong Frappe
4. Data quality trong Sales Orders

---

**Chuc ban thanh cong voi Forecast Models! 🚀**

