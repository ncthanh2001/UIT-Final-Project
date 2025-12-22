# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Linear Regression Model for AI Inventory Forecast
Su dung Linear Regression de du doan consumption dua tren time series
"""

import frappe
from frappe.utils import nowdate
from datetime import date, datetime


def safe_import_ml_packages():
    """Safely import ML packages with error handling"""
    try:
        import numpy as np
        import pandas as pd
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import StandardScaler

        return np, pd, LinearRegression, StandardScaler, True
    except ImportError as e:
        frappe.log_error(f"ML packages not available: {str(e)}")
        return None, None, None, None, False


class LinearRegressionForecast:
    """
    Linear Regression Model cho AI Inventory Forecast
    Su dung time series linear regression de du doan consumption
    """

    def __init__(self, item_code=None, warehouse=None, company=None):
        """
        Initialize Linear Regression Forecast model

        Args:
            item_code: Item code
            warehouse: Warehouse name
            company: Company name
        """
        self.item_code = item_code
        self.warehouse = warehouse
        self.company = company

        # Import ML packages
        np, pd, LinearRegression, StandardScaler, ml_available = (
            safe_import_ml_packages()
        )

        if not ml_available:
            raise ImportError("ML packages (numpy, pandas, sklearn) are not available")

        self.np = np
        self.pd = pd
        self.LinearRegression = LinearRegression
        self.StandardScaler = StandardScaler

    def prepare_data_from_sales_orders(self, sales_order_items):
        """
        Chuan bi du lieu tu Sales Order Items thanh format phu hop cho ML

        Args:
            sales_order_items: List of dicts chua delivery_date, qty, etc. from Sales Order

        Returns:
            DataFrame: Demand records voi days_from_start
        """
        if not sales_order_items or len(sales_order_items) < 5:
            return None

        # Chuyen doi datetime.date objects thanh string de tranh loi pandas
        cleaned_data = []
        for row in sales_order_items:
            cleaned_row = {}
            for key, value in row.items():
                # Chuyen datetime.date va datetime.datetime thanh string
                if isinstance(value, (date, datetime)):
                    cleaned_row[key] = str(value)
                # Chuyen None thanh empty string hoac 0 tuy theo kieu
                elif value is None:
                    cleaned_row[key] = (
                        0 if isinstance(row.get(key, 0), (int, float)) else ""
                    )
                else:
                    cleaned_row[key] = value
            cleaned_data.append(cleaned_row)

        # Convert to DataFrame
        df = self.pd.DataFrame(cleaned_data)

        # Convert delivery_date to datetime for calculations
        if "delivery_date" in df.columns:
            df["date"] = self.pd.to_datetime(df["delivery_date"])
        elif "transaction_date" in df.columns:
            df["date"] = self.pd.to_datetime(df["transaction_date"])
        else:
            return None

        # Ensure qty column exists
        if "qty" not in df.columns:
            return None

        # Prepare data for ML - aggregate by date
        demand_records = df.groupby("date")["qty"].sum().reset_index()
        demand_records = demand_records.sort_values("date")

        if len(demand_records) < 5:
            return None

        # Calculate days from start
        demand_records["days_from_start"] = (
            demand_records["date"] - demand_records["date"].min()
        ).dt.days

        return demand_records

    def train_and_predict(
        self,
        demand_records,
        forecast_period_days=30,
        lead_time_days=14,
        current_stock=0,
    ):
        """
        Train Linear Regression model va du doan demand

        Args:
            demand_records: DataFrame chua demand data
            forecast_period_days: So ngay can du doan
            lead_time_days: Lead time cho reorder
            current_stock: Stock hien tai

        Returns:
            dict: Forecast result hoac None neu khong du du lieu
        """
        # Linear regression on time series
        X = demand_records[["days_from_start"]].values
        y = demand_records["qty"].values

        if len(X) < 3:
            return None

        # Train model
        model = self.LinearRegression()
        model.fit(X, y)

        # Get model parameters
        slope = float(model.coef_[0])
        intercept = float(model.intercept_)
        r2_score = model.score(X, y)

        # Predict future demand (day-by-day for better accuracy)
        max_days = float(X.max())
        future_days = self.np.array(
            [[max_days + i] for i in range(1, forecast_period_days + 1)]
        )
        future_predictions = model.predict(future_days)
        future_predictions = self.np.maximum(0, future_predictions)  # No negative demand
        
        predicted_demand = float(future_predictions.sum())

        # Calculate confidence intervals (simple approach using std of residuals)
        residuals = y - model.predict(X)
        std_error = self.np.std(residuals)
        margin = 1.96 * std_error * self.np.sqrt(forecast_period_days)  # 95% CI
        
        lower_bound = max(0, predicted_demand - margin)
        upper_bound = predicted_demand + margin

        # Calculate confidence based on R² score
        confidence_score = max(50, min(95, r2_score * 100))

        # Calculate daily average from historical data
        total_days = max(1, int(X.max() - X.min()))
        total_demand = float(y.sum())
        daily_avg = total_demand / max(1, total_days)

        # Detect trend based on slope
        if slope > 0.1:
            trend_type = "Upward"
        elif slope < -0.1:
            trend_type = "Downward"
        else:
            trend_type = "Stable"

        # Determine movement type
        if daily_avg > 2:
            movement_type = "Fast Moving"
        elif daily_avg > 0.5:
            movement_type = "Slow Moving"
        else:
            movement_type = "Non Moving"

        # Calculate reorder parameters
        safety_factor = 1.5 if movement_type == "Fast Moving" else 1.2
        reorder_level = (daily_avg * lead_time_days) * safety_factor
        safety_stock = daily_avg * lead_time_days * 0.3  # 30% of lead time demand
        suggested_qty = max(1, int(daily_avg * (forecast_period_days + lead_time_days)))

        reorder_alert = current_stock <= reorder_level

        # Create forecast explanation
        forecast_explanation = f"""📊 LINEAR REGRESSION FORECAST ANALYSIS for {self.item_code}

🤖 MACHINE LEARNING INSIGHTS:
• Algorithm: Linear Regression
• Training Data: {len(demand_records)} demand records
• Model Accuracy (R²): {r2_score:.3f}
• Daily Demand Rate: {daily_avg:.2f} units/day
• Trend: {trend_type} (slope: {slope:.4f})

🔮 PREDICTIONS:
• Predicted Demand ({forecast_period_days} days): {predicted_demand:.2f} units
• Confidence Interval: [{lower_bound:.2f}, {upper_bound:.2f}]
• Movement Classification: {movement_type}
• Confidence Level: {confidence_score:.1f}%

📦 INVENTORY RECOMMENDATIONS:
• Current Stock: {current_stock} units
• Reorder Level: {reorder_level:.2f} units
• Safety Stock: {safety_stock:.2f} units
• Suggested Order Qty: {suggested_qty} units
• Reorder Alert: {'🚨 YES' if reorder_alert else '✅ NO'}

🏢 Company: {self.company}
📦 Warehouse: {self.warehouse}
📅 Analysis Date: {nowdate()}"""

        return {
            # Core forecast
            "predicted_consumption": predicted_demand,
            "forecast_qty": predicted_demand,
            "confidence_score": confidence_score,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            
            # Model info
            "model_used": "Linear Regression",
            "model_confidence": f"R²: {r2_score:.3f}",
            "training_data_points": len(demand_records),
            
            # Movement and trend
            "movement_type": movement_type,
            "daily_avg_consumption": daily_avg,
            "trend_type": trend_type,
            
            # Inventory recommendations
            "reorder_level": reorder_level,
            "suggested_qty": suggested_qty,
            "safety_stock": safety_stock,
            "current_stock": current_stock,
            "reorder_alert": reorder_alert,
            
            # Linear Regression specific
            "lr_r2_score": r2_score * 100,  # Convert to percentage
            "lr_slope": slope,
            
            # Explanation
            "forecast_explanation": forecast_explanation,
            "recommendations": f"Based on Linear Regression model (R²={r2_score:.2f}), the item shows {trend_type.lower()} trend with {movement_type.lower()} characteristics.",
        }

    def forecast(
        self,
        sales_order_items,
        forecast_period_days=30,
        lead_time_days=14,
        current_stock=0,
    ):
        """
        Main forecast method - chuan bi data tu Sales Orders, train model va du doan

        Args:
            sales_order_items: List of dicts chua Sales Order Items (delivery_date, qty, etc.)
            forecast_period_days: So ngay can du doan
            lead_time_days: Lead time cho reorder
            current_stock: Stock hien tai

        Returns:
            dict: Forecast result hoac None neu khong du du lieu
        """
        try:
            # Prepare data from Sales Orders
            demand_records = self.prepare_data_from_sales_orders(sales_order_items)

            if demand_records is None:
                return None

            # Train and predict
            result = self.train_and_predict(
                demand_records,
                forecast_period_days,
                lead_time_days,
                current_stock,
            )

            return result

        except Exception as e:
            frappe.log_error(f"Linear Regression forecast failed: {str(e)}")
            return None
