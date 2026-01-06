# APS Forecast Module

Module nay cung cap API va giao dien de quan ly va xem ket qua du doan nhu cau hang hoa.

## API Endpoints

### 1. Get Forecast History List
```python
uit_aps.forecast.api.forecast_api.get_forecast_history_list(
    limit=20,
    offset=0,
    company=None,
    model_used=None,
    status=None
)
```

Lay danh sach lich su forecast voi bo loc.

**Parameters:**
- `limit`: So luong record toi da (default: 20)
- `offset`: Vi tri bat dau (default: 0)
- `company`: Loc theo company (optional)
- `model_used`: Loc theo model (ARIMA/Linear Regression/Prophet) (optional)
- `status`: Loc theo trang thai (Complete/Running/Failed/Pending) (optional)

**Returns:**
```json
{
    "data": [...],
    "total": 100,
    "limit": 20,
    "offset": 0
}
```

### 2. Get Forecast Dashboard Data
```python
uit_aps.forecast.api.forecast_api.get_forecast_dashboard_data(
    forecast_history="FCST-RUN-2025-01-06-0001"
)
```

Lay du lieu dashboard cho mot forecast history cu the.

**Parameters:**
- `forecast_history`: Ten cua APS Forecast History record

**Returns:**
```json
{
    "history": {...},
    "kpi": {
        "totalForecastQty": 10314,
        "avgConfidence": 50.0,
        "reorderAlerts": 2,
        "avgStockCoverage": 45.7,
        "forecastRuns": 1,
        "periods": 1,
        "items": 13
    },
    "charts": {
        "forecastOverTime": [...],
        "reorderAlertsByGroup": [...],
        "topItemsByForecast": [...],
        "confidenceScore": [...]
    },
    "reorder_alerts": [...],
    "recommendations": [...]
}
```

### 3. Get Forecast Result Details
```python
uit_aps.forecast.api.forecast_api.get_forecast_result_details(
    forecast_result="FCST-TP-GAN-001-2025-01-06-0001"
)
```

Lay chi tiet mot forecast result.

### 4. Helper Methods
```python
# Lay danh sach companies
uit_aps.forecast.api.forecast_api.get_companies()

# Lay danh sach models
uit_aps.forecast.api.forecast_api.get_forecast_models()
```

## Frontend Pages

### 1. Forecast History Page
**Route:** `/forecast-history`

Hien thi danh sach tat ca cac lan chay forecast voi:
- Bo loc theo company, model, trang thai
- Bang danh sach voi thong tin chi tiet
- Nut "Coi ket qua" de xem dashboard

### 2. Dashboard Page
**Route:** `/dashboard?history=FCST-RUN-2025-01-06-0001`

Hien thi dashboard chi tiet cho mot lan chay forecast:
- KPI cards (Total Forecast Qty, Avg Confidence, Reorder Alerts, Stock Coverage)
- Bieu do Forecast Over Time
- Bieu do Reorder Alerts by Group
- Bieu do Top Items
- Bieu do Confidence Score Distribution
- Bang Reorder Alerts chi tiet
- Phan tich tong the va khuyen nghi AI

## Cach su dung

1. **Xem danh sach lich su forecast:**
   - Truy cap `/forecast-history`
   - Su dung bo loc de tim kiem
   - Nhan nut "Coi ket qua" de xem chi tiet

2. **Xem dashboard:**
   - Dashboard tu dong load du lieu tu API
   - Hien thi cac bieu do va bang du lieu
   - Cung cap khuyen nghi AI

3. **Navigation:**
   - Su dung Sidebar de di chuyen giua cac trang
   - "Forecast History" link trong Main menu

## Ket noi DocTypes

- **APS Forecast History**: Luu thong tin lan chay forecast
- **APS Forecast Result**: Luu ket qua chi tiet cho tung item
- **Relationship**: Mot History co nhieu Results (1-to-many)

