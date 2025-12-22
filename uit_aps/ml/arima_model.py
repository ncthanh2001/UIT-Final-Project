# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
ARIMA Model for AI Inventory Forecast
Su dung ARIMA (AutoRegressive Integrated Moving Average) de du doan consumption
"""

import frappe
from frappe.utils import nowdate
from datetime import date, datetime


def safe_import_arima_packages():
    """Safely import ARIMA packages with error handling"""
    try:
        import numpy as np
        import pandas as pd
        from statsmodels.tsa.arima.model import ARIMA
        from statsmodels.tsa.stattools import adfuller

        return np, pd, ARIMA, adfuller, True
    except ImportError as e:
        frappe.log_error(f"ARIMA packages not available: {str(e)}")
        return None, None, None, None, False


class ARIMAForecast:
    """
    ARIMA Model cho AI Inventory Forecast
    Su dung ARIMA time series model de du doan consumption
    """

    def __init__(self, item_code=None, warehouse=None, company=None):
        """
        Initialize ARIMA Forecast model

        Args:
            item_code: Item code
            warehouse: Warehouse name
            company: Company name
        """
        self.item_code = item_code
        self.warehouse = warehouse
        self.company = company

        # Import ARIMA packages
        np, pd, ARIMA, adfuller, arima_available = safe_import_arima_packages()

        if not arima_available:
            raise ImportError(
                "ARIMA packages (numpy, pandas, statsmodels) are not available"
            )

        self.np = np
        self.pd = pd
        self.ARIMA = ARIMA
        self.adfuller = adfuller

    def prepare_data_from_sales_orders(self, sales_order_items):
        """
        Chuan bi du lieu tu Sales Order Items thanh time series format cho ARIMA

        Args:
            sales_order_items: List of dicts chua delivery_date, qty, etc. from Sales Order

        Returns:
            Series: Time series demand data voi daily frequency
        """
        if not sales_order_items or len(sales_order_items) < 10:
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
            df["delivery_date"] = self.pd.to_datetime(df["delivery_date"])
            df["date"] = df["delivery_date"].dt.date
        elif "transaction_date" in df.columns:
            df["transaction_date"] = self.pd.to_datetime(df["transaction_date"])
            df["date"] = df["transaction_date"].dt.date
        else:
            return None

        # Ensure qty column exists
        if "qty" not in df.columns:
            return None

        # Group by date and sum qty (demand per day)
        daily_demand = df.groupby("date")["qty"].sum().reset_index()
        daily_demand["date"] = self.pd.to_datetime(daily_demand["date"])

        # Create time series with daily frequency
        daily_demand = daily_demand.set_index("date")
        daily_demand = daily_demand.sort_index()

        # Fill missing dates with 0 (no demand on those days)
        date_range = self.pd.date_range(
            start=daily_demand.index.min(), end=daily_demand.index.max(), freq="D"
        )
        time_series = self.pd.Series(0, index=date_range)
        time_series.update(daily_demand["qty"])

        return time_series

    def check_stationarity(self, time_series):
        """
        Kiem tra tinh stationary cua time series bang Augmented Dickey-Fuller test

        Args:
            time_series: pandas Series

        Returns:
            bool: True neu stationary, False neu khong
        """
        try:
            result = self.adfuller(time_series.dropna())
            # p-value < 0.05 thi stationary
            return result[1] < 0.05
        except Exception:
            return False

    def make_stationary(self, time_series):
        """
        Lam cho time series stationary bang differencing

        Args:
            time_series: pandas Series

        Returns:
            tuple: (stationary_series, diff_order)
        """
        diff_order = 0
        current_series = time_series.copy()

        # Toi da 2 lan differencing
        for i in range(3):
            if self.check_stationarity(current_series):
                return current_series, diff_order

            current_series = current_series.diff().dropna()
            diff_order += 1

        # Neu van khong stationary, tra ve differenced series
        return current_series, diff_order

    def find_best_arima_params(self, time_series, max_p=3, max_d=2, max_q=3):
        """
        Tim best ARIMA parameters bang grid search

        Args:
            time_series: pandas Series
            max_p: Max AR order
            max_d: Max differencing order
            max_q: Max MA order

        Returns:
            tuple: (best_p, best_d, best_q, best_aic)
        """
        best_aic = float("inf")
        best_params = (1, 1, 1)

        # Simplify: chi thu mot so combinations pho bien
        # De tranh timeout, chi thu cac combinations co xac suat cao
        test_params = [
            (1, 1, 1),
            (1, 1, 0),
            (0, 1, 1),
            (2, 1, 1),
            (1, 1, 2),
            (2, 1, 0),
            (0, 1, 2),
        ]

        for p, d, q in test_params:
            try:
                model = self.ARIMA(time_series, order=(p, d, q))
                fitted_model = model.fit()
                aic = fitted_model.aic

                if aic < best_aic:
                    best_aic = aic
                    best_params = (p, d, q)
            except Exception:
                continue

        return best_params[0], best_params[1], best_params[2], best_aic

    def train_and_predict(
        self,
        time_series,
        forecast_period_days=30,
        lead_time_days=14,
        current_stock=0,
    ):
        """
        Train ARIMA model va du doan demand

        Args:
            time_series: pandas Series chua demand data
            forecast_period_days: So ngay can du doan
            lead_time_days: Lead time cho reorder
            current_stock: Stock hien tai

        Returns:
            dict: Forecast result hoac None neu khong du du lieu
        """
        try:
            # Kiem tra do dai time series
            # ARIMA can it nhat 10-15 data points de hoat dong tot
            if len(time_series) < 10:
                return None

            # Fill NaN values (neu co) bang 0
            time_series = time_series.fillna(0)

            # Find best ARIMA parameters
            p, d, q, aic = self.find_best_arima_params(time_series)

            # Train ARIMA model
            model = self.ARIMA(time_series, order=(p, d, q))
            fitted_model = model.fit()

            # Forecast future demand
            forecast = fitted_model.forecast(steps=forecast_period_days)

            # Get confidence intervals
            forecast_result = fitted_model.get_forecast(steps=forecast_period_days)
            forecast_summary = forecast_result.summary_frame(
                alpha=0.05
            )  # 95% confidence

            predicted_demand = float(forecast.sum())
            lower_bound = float(forecast_summary["mean_ci_lower"].sum())
            upper_bound = float(forecast_summary["mean_ci_upper"].sum())

            # Calculate confidence based on model fit
            # ARIMA khong co R² score, dung AIC de tinh confidence
            # AIC thap hon = model tot hon
            # Chuyen doi AIC thanh confidence score (heuristic)
            base_confidence = 70
            if aic < 100:
                confidence_score = min(95, base_confidence + 15)
            elif aic < 500:
                confidence_score = base_confidence
            else:
                confidence_score = max(50, base_confidence - 10)

            # Determine movement type and trend based on data
            total_days = max(
                1, (time_series.index.max() - time_series.index.min()).days
            )
            total_demand = float(time_series.sum())
            daily_avg = total_demand / max(1, total_days)

            # Detect trend using linear fit on time series
            if len(time_series) > 2:
                x = self.np.arange(len(time_series))
                y = time_series.values
                slope = self.np.polyfit(x, y, 1)[0]

                if slope > 0.1:
                    trend_type = "Upward"
                elif slope < -0.1:
                    trend_type = "Downward"
                else:
                    trend_type = "Stable"
            else:
                trend_type = "Stable"
                slope = 0

            # Movement type classification
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
            suggested_qty = max(
                1, int(daily_avg * (forecast_period_days + lead_time_days))
            )

            reorder_alert = current_stock <= reorder_level

            # Create forecast explanation
            forecast_explanation = f"""📊 ARIMA FORECAST ANALYSIS for {self.item_code}

🤖 MACHINE LEARNING INSIGHTS:
• Algorithm: ARIMA({p},{d},{q})
• Training Data: {len(time_series)} days of demand data
• Model AIC: {aic:.2f}
• Daily Demand Rate: {daily_avg:.2f} units/day
• Trend: {trend_type}

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
                "lower_bound": max(0, lower_bound),
                "upper_bound": upper_bound,
                # Model info
                "model_used": "ARIMA",
                "model_confidence": f"AIC: {aic:.2f}",
                "training_data_points": len(time_series),
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
                # ARIMA specific
                "arima_params": {"p": p, "d": d, "q": q},
                "arima_p": p,
                "arima_d": d,
                "arima_q": q,
                "arima_aic": aic,
                # Explanation
                "forecast_explanation": forecast_explanation,
                "recommendations": f"Based on ARIMA({p},{d},{q}) model, the item shows {trend_type.lower()} trend with {movement_type.lower()} characteristics.",
            }

        except Exception as e:
            frappe.log_error(f"ARIMA forecast calculation failed: {str(e)}")
            return None

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
            time_series = self.prepare_data_from_sales_orders(sales_order_items)

            if time_series is None or len(time_series) < 10:
                return None

            # Train and predict
            result = self.train_and_predict(
                time_series,
                forecast_period_days,
                lead_time_days,
                current_stock,
            )

            return result

        except Exception as e:
            frappe.log_error(f"ARIMA forecast failed: {str(e)}")
            return None
