# THIET KE LAI CAC MODEL DU DOAN VA BANG DU LIEU

## 1. TONG QUAN

### 1.1. Nguon du lieu
- **Sales Order** voi `docstatus = 1` (da submit)
- Lay du lieu tu cac item trong Sales Order Item
- Tinh toan consumption dua tren qty va delivery_date

### 1.2. Cac Model
1. **ARIMA** - AutoRegressive Integrated Moving Average
2. **Linear Regression** - Hoi quy tuyen tinh
3. **Prophet** - Facebook Prophet model

---

## 2. CAU TRUC BANG APS FORECAST RESULT (DA CAI TIEN)

### 2.1. Cac truong HIEN TAI
```
- item (Link to Item) ✓
- forecast_period (Date) ✓
- forecast_history (Link to APS Forecast History) ✓
- forecast_qty (Float) ✓
- confidence_score (Percent) ✓
- lower_bound (Float) ✓
- upper_bound (Float) ✓
```

### 2.2. Cac truong CAN THEM

#### Section: Model Information
```json
{
  "model_used": {
    "fieldtype": "Select",
    "options": "ARIMA\nLinear Regression\nProphet",
    "label": "Model Used",
    "description": "Model duoc su dung de du doan"
  },
  "model_confidence": {
    "fieldtype": "Data",
    "label": "Model Confidence Metric",
    "description": "R² score cho LR, AIC cho ARIMA, hoac metric khac"
  },
  "training_data_points": {
    "fieldtype": "Int",
    "label": "Training Data Points",
    "description": "So luong data points duoc dung de train model"
  }
}
```

#### Section: Forecast Details
```json
{
  "movement_type": {
    "fieldtype": "Select",
    "options": "Fast Moving\nSlow Moving\nNon Moving",
    "label": "Movement Type",
    "description": "Phan loai toc do tieu thu"
  },
  "daily_avg_consumption": {
    "fieldtype": "Float",
    "label": "Daily Avg Consumption",
    "description": "Tieu thu trung binh hang ngay (units/day)",
    "precision": 2
  },
  "trend_type": {
    "fieldtype": "Select",
    "options": "Upward\nDownward\nStable",
    "label": "Trend Type",
    "description": "Xu huong tieu thu"
  }
}
```

#### Section: Inventory Recommendations
```json
{
  "reorder_level": {
    "fieldtype": "Float",
    "label": "Reorder Level",
    "description": "Muc ton kho toi thieu de dat hang lai",
    "precision": 2
  },
  "suggested_qty": {
    "fieldtype": "Int",
    "label": "Suggested Order Qty",
    "description": "So luong de xuat dat hang"
  },
  "reorder_alert": {
    "fieldtype": "Check",
    "label": "Reorder Alert",
    "description": "Canh bao can dat hang ngay",
    "default": 0
  },
  "safety_stock": {
    "fieldtype": "Float",
    "label": "Safety Stock",
    "description": "Ton kho an toan",
    "precision": 2
  },
  "current_stock": {
    "fieldtype": "Float",
    "label": "Current Stock",
    "description": "Ton kho hien tai khi chay forecast",
    "precision": 2
  }
}
```

#### Section: Additional Context
```json
{
  "warehouse": {
    "fieldtype": "Link",
    "options": "Warehouse",
    "label": "Warehouse",
    "description": "Kho luu tru (neu can)"
  },
  "company": {
    "fieldtype": "Link",
    "options": "Company",
    "label": "Company",
    "description": "Cong ty"
  },
  "item_group": {
    "fieldtype": "Link",
    "options": "Item Group",
    "label": "Item Group",
    "fetch_from": "item.item_group",
    "read_only": 1
  }
}
```

#### Section: Model-Specific Metrics (ARIMA)
```json
{
  "arima_p": {
    "fieldtype": "Int",
    "label": "ARIMA p (AR order)",
    "depends_on": "eval:doc.model_used=='ARIMA'"
  },
  "arima_d": {
    "fieldtype": "Int",
    "label": "ARIMA d (Differencing)",
    "depends_on": "eval:doc.model_used=='ARIMA'"
  },
  "arima_q": {
    "fieldtype": "Int",
    "label": "ARIMA q (MA order)",
    "depends_on": "eval:doc.model_used=='ARIMA'"
  },
  "arima_aic": {
    "fieldtype": "Float",
    "label": "AIC Score",
    "depends_on": "eval:doc.model_used=='ARIMA'",
    "precision": 2
  }
}
```

#### Section: Model-Specific Metrics (Linear Regression)
```json
{
  "lr_r2_score": {
    "fieldtype": "Percent",
    "label": "R² Score",
    "depends_on": "eval:doc.model_used=='Linear Regression'",
    "description": "Do chinh xac cua model (0-100%)"
  },
  "lr_slope": {
    "fieldtype": "Float",
    "label": "Trend Slope",
    "depends_on": "eval:doc.model_used=='Linear Regression'",
    "precision": 4
  }
}
```

#### Section: Model-Specific Metrics (Prophet)
```json
{
  "prophet_seasonality_detected": {
    "fieldtype": "Check",
    "label": "Seasonality Detected",
    "depends_on": "eval:doc.model_used=='Prophet'",
    "default": 0
  },
  "prophet_seasonality_type": {
    "fieldtype": "Select",
    "options": "Weekly\nMonthly\nYearly\nMultiple",
    "label": "Seasonality Type",
    "depends_on": "eval:doc.model_used=='Prophet'"
  },
  "prophet_changepoint_count": {
    "fieldtype": "Int",
    "label": "Changepoint Count",
    "depends_on": "eval:doc.model_used=='Prophet'",
    "description": "So diem thay doi xu huong"
  }
}
```

#### Section: Detailed Explanation
```json
{
  "forecast_explanation": {
    "fieldtype": "Long Text",
    "label": "Forecast Explanation",
    "description": "Giai thich chi tiet ve ket qua du doan"
  },
  "recommendations": {
    "fieldtype": "Long Text",
    "label": "Recommendations",
    "description": "Cac khuyen nghi hanh dong"
  },
  "notes": {
    "fieldtype": "Long Text",
    "label": "Notes",
    "description": "Ghi chu them"
  }
}
```

---

## 3. CAU TRUC BANG APS FORECAST HISTORY (DA CAI TIEN)

### 3.1. Cac truong HIEN TAI
```
- run_name (Data) ✓
- company (Link to Company) ✓
- model_recommended (Data) ✓
- model_used (Link to ML Model) ✓
- forecast_horizon_days (Int) ✓
- start_date (Date) ✓
- end_date (Date) ✓
- total_sales_orders_used (Int) ✓
- overall_accuracy_mape (Float) ✓
- run_status (Select) ✓
- run_start_time (Datetime) ✓
- run_end_time (Datetime) ✓
```

### 3.2. Cac truong CAN THEM

#### Section: Training Data Period
```json
{
  "training_period_start": {
    "fieldtype": "Date",
    "label": "Training Period Start",
    "description": "Ngay bat dau cua du lieu training"
  },
  "training_period_end": {
    "fieldtype": "Date",
    "label": "Training Period End",
    "description": "Ngay ket thuc cua du lieu training"
  },
  "total_items_forecasted": {
    "fieldtype": "Int",
    "label": "Total Items Forecasted",
    "description": "Tong so item da forecast"
  },
  "total_results_generated": {
    "fieldtype": "Int",
    "label": "Total Results Generated",
    "description": "Tong so ket qua da tao"
  }
}
```

#### Section: Model Performance
```json
{
  "avg_confidence_score": {
    "fieldtype": "Percent",
    "label": "Avg Confidence Score",
    "description": "Diem tin cay trung binh cua tat ca forecast"
  },
  "successful_forecasts": {
    "fieldtype": "Int",
    "label": "Successful Forecasts",
    "description": "So forecast thanh cong"
  },
  "failed_forecasts": {
    "fieldtype": "Int",
    "label": "Failed Forecasts",
    "description": "So forecast that bai"
  }
}
```

#### Section: Parameters Used
```json
{
  "parameters_json": {
    "fieldtype": "Long Text",
    "label": "Parameters (JSON)",
    "description": "Cac tham so duoc su dung khi chay forecast (JSON format)"
  },
  "filters_applied": {
    "fieldtype": "Long Text",
    "label": "Filters Applied",
    "description": "Cac bo loc duoc ap dung (item_group, warehouse, etc.)"
  }
}
```

#### Child Table: Forecast Results Summary (Optional)
```json
{
  "forecast_results_summary": {
    "fieldtype": "Table",
    "label": "Forecast Results Summary",
    "options": "APS Forecast History Item",
    "description": "Bang tong hop cac ket qua forecast"
  }
}
```

---

## 4. OUTPUT CUA CAC MODEL

### 4.1. Output chung cho tat ca models
```python
{
    "predicted_consumption": float,      # => forecast_qty
    "movement_type": str,               # => movement_type
    "confidence_score": float,          # => confidence_score
    "reorder_level": float,             # => reorder_level
    "suggested_qty": int,               # => suggested_qty
    "reorder_alert": bool,              # => reorder_alert
    "forecast_explanation": str,        # => forecast_explanation
    "daily_avg_consumption": float,     # => daily_avg_consumption
    "lower_bound": float,               # => lower_bound (optional)
    "upper_bound": float,               # => upper_bound (optional)
}
```

### 4.2. Output rieng cho ARIMA
```python
{
    "arima_params": {
        "p": int,                       # => arima_p
        "d": int,                       # => arima_d
        "q": int,                       # => arima_q
    },
    "aic": float,                       # => arima_aic
    "model_confidence": str             # => model_confidence (f"AIC: {aic}")
}
```

### 4.3. Output rieng cho Linear Regression
```python
{
    "r2_score": float,                  # => lr_r2_score
    "slope": float,                     # => lr_slope
    "trend_type": str,                  # => trend_type
    "model_confidence": str             # => model_confidence (f"R²: {r2}")
}
```

### 4.4. Output rieng cho Prophet
```python
{
    "seasonality_detected": bool,       # => prophet_seasonality_detected
    "seasonality_type": str,            # => prophet_seasonality_type
    "changepoint_count": int,           # => prophet_changepoint_count
    "trend_type": str,                  # => trend_type
    "model_confidence": str             # => model_confidence
}
```

---

## 5. WORKFLOW DU DOAN

### 5.1. Lay du lieu tu Sales Order
```python
def get_sales_order_data(company, start_date, end_date):
    """
    Lay du lieu tu Sales Order da submit (docstatus=1)
    
    Returns:
        List[dict]: Danh sach cac sales order items
    """
    sales_orders = frappe.get_all(
        "Sales Order",
        filters={
            "docstatus": 1,
            "company": company,
            "transaction_date": ["between", [start_date, end_date]]
        },
        fields=["name", "transaction_date", "customer"]
    )
    
    # Lay chi tiet items
    items_data = []
    for so in sales_orders:
        items = frappe.get_all(
            "Sales Order Item",
            filters={"parent": so.name},
            fields=[
                "item_code",
                "item_name", 
                "qty",
                "delivery_date",
                "warehouse"
            ]
        )
        for item in items:
            item["transaction_date"] = so.transaction_date
            item["customer"] = so.customer
            items_data.append(item)
    
    return items_data
```

### 5.2. Chuan bi du lieu cho model
```python
def prepare_data_for_model(sales_order_data, item_code):
    """
    Chuyen doi sales order data thanh time series cho model
    
    Args:
        sales_order_data: Danh sach sales order items
        item_code: Item can du doan
    
    Returns:
        DataFrame/Series: Time series data
    """
    # Filter theo item_code
    item_data = [d for d in sales_order_data if d["item_code"] == item_code]
    
    # Convert to DataFrame
    df = pd.DataFrame(item_data)
    df["date"] = pd.to_datetime(df["delivery_date"])
    
    # Group by date va sum qty
    daily_demand = df.groupby("date")["qty"].sum()
    
    return daily_demand
```

### 5.3. Chay forecast va luu ket qua
```python
def run_forecast_and_save(
    company,
    model_name,
    forecast_horizon_days=30,
    training_start_date=None,
    training_end_date=None
):
    """
    Chay forecast cho tat ca items va luu ket qua
    
    Returns:
        str: Ten cua APS Forecast History record
    """
    # 1. Tao forecast history record
    history = frappe.get_doc({
        "doctype": "APS Forecast History",
        "run_name": f"Forecast_{nowdate()}_{model_name}",
        "company": company,
        "model_used": model_name,
        "forecast_horizon_days": forecast_horizon_days,
        "run_status": "Running",
        "run_start_time": now_datetime()
    })
    history.insert()
    frappe.db.commit()
    
    # 2. Lay sales order data
    sales_data = get_sales_order_data(
        company, 
        training_start_date, 
        training_end_date
    )
    
    # 3. Lay danh sach items
    items = list(set([d["item_code"] for d in sales_data]))
    
    # 4. Chay forecast cho tung item
    results = []
    for item_code in items:
        try:
            # Prepare data
            time_series = prepare_data_for_model(sales_data, item_code)
            
            # Select model
            if model_name == "ARIMA":
                model = ARIMAForecast(item_code, None, company)
            elif model_name == "Linear Regression":
                model = LinearRegressionForecast(item_code, None, company)
            elif model_name == "Prophet":
                model = ProphetForecast(item_code, None, company)
            
            # Run forecast
            result = model.forecast(
                time_series,
                forecast_period_days=forecast_horizon_days
            )
            
            if result:
                # Save result
                forecast_result = create_forecast_result(
                    item_code,
                    result,
                    history.name,
                    model_name
                )
                results.append(forecast_result)
                
        except Exception as e:
            frappe.log_error(f"Forecast failed for {item_code}: {str(e)}")
    
    # 5. Update history
    history.run_status = "Complete"
    history.run_end_time = now_datetime()
    history.total_results_generated = len(results)
    history.save()
    
    return history.name
```

### 5.4. Tao forecast result record
```python
def create_forecast_result(item_code, forecast_output, history_name, model_name):
    """
    Tao APS Forecast Result tu output cua model
    """
    doc = frappe.get_doc({
        "doctype": "APS Forecast Result",
        "item": item_code,
        "forecast_period": forecast_output.get("forecast_period_start"),
        "forecast_history": history_name,
        "forecast_qty": forecast_output.get("predicted_consumption"),
        "confidence_score": forecast_output.get("confidence_score"),
        "lower_bound": forecast_output.get("lower_bound"),
        "upper_bound": forecast_output.get("upper_bound"),
        "model_used": model_name,
        "movement_type": forecast_output.get("movement_type"),
        "daily_avg_consumption": forecast_output.get("daily_avg_consumption"),
        "reorder_level": forecast_output.get("reorder_level"),
        "suggested_qty": forecast_output.get("suggested_qty"),
        "reorder_alert": forecast_output.get("reorder_alert"),
        "forecast_explanation": forecast_output.get("forecast_explanation"),
        
        # Model-specific fields
        "arima_p": forecast_output.get("arima_params", {}).get("p"),
        "arima_d": forecast_output.get("arima_params", {}).get("d"),
        "arima_q": forecast_output.get("arima_params", {}).get("q"),
        "arima_aic": forecast_output.get("aic"),
        "lr_r2_score": forecast_output.get("r2_score"),
        "lr_slope": forecast_output.get("slope"),
        "prophet_seasonality_detected": forecast_output.get("seasonality_detected"),
        "prophet_seasonality_type": forecast_output.get("seasonality_type"),
    })
    doc.insert()
    return doc.name
```

---

## 6. KET LUAN

Voi thiet ke nay:
- **APS Forecast History**: Luu thong tin ve lan chay forecast (tham so, thoi gian, model, ket qua tong the)
- **APS Forecast Result**: Luu chi tiet ket qua du doan cho tung item, bao gom:
  - Du doan consumption
  - Cac chi so confidence
  - Recommendation (reorder level, suggested qty)
  - Model-specific metrics
  - Explanation chi tiet

He thong co the:
1. Chay forecast cho nhieu items cung luc
2. Luu tru day du thong tin de phan tich sau nay
3. So sanh hieu qua cua cac model khac nhau
4. Export reports va visualization
5. Tich hop vao inventory management workflow

