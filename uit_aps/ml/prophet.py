# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
Prophet Model for AI Inventory Forecast
Su dung Facebook Prophet de du doan demand voi seasonality detection
"""

import frappe
from frappe.utils import nowdate
from datetime import date, datetime, timedelta


def safe_import_prophet_packages():
    """Safely import Prophet packages with error handling"""
    try:
        import numpy as np
        import pandas as pd
        from prophet import Prophet

        return np, pd, Prophet, True
    except ImportError as e:
        frappe.log_error(f"Prophet packages not available: {str(e)}")
        return None, None, None, False


class ProphetForecast:
    """
    Prophet Model cho AI Inventory Forecast
    Su dung Facebook Prophet de du doan demand voi auto seasonality detection
    """

    def __init__(self, item_code=None, warehouse=None, company=None):
        """
        Initialize Prophet Forecast model

        Args:
            item_code: Item code
            warehouse: Warehouse name
            company: Company name
        """
        self.item_code = item_code
        self.warehouse = warehouse
        self.company = company

        # Import Prophet packages
        np, pd, Prophet, prophet_available = safe_import_prophet_packages()

        if not prophet_available:
            raise ImportError(
                "Prophet packages (pandas, prophet) are not available. "
                "Install: pip install prophet"
            )

        self.np = np
        self.pd = pd
        self.Prophet = Prophet

    def prepare_data_from_sales_orders(self, sales_order_items):
        """
        Chuan bi du lieu tu Sales Order Items thanh Prophet format

        Args:
            sales_order_items: List of dicts chua delivery_date, qty, etc. from Sales Order

        Returns:
            DataFrame: Prophet format (ds, y columns)
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

        # Convert delivery_date to datetime
        if "delivery_date" in df.columns:
            df["ds"] = self.pd.to_datetime(df["delivery_date"])
        elif "transaction_date" in df.columns:
            df["ds"] = self.pd.to_datetime(df["transaction_date"])
        else:
            return None

        # Ensure qty column exists
        if "qty" not in df.columns:
            return None

        # Group by date and sum qty (demand per day)
        daily_demand = df.groupby("ds")["qty"].sum().reset_index()
        daily_demand.columns = ["ds", "y"]  # Prophet requires 'ds' and 'y' columns
        daily_demand = daily_demand.sort_values("ds")

        # Fill missing dates with 0
        date_range = self.pd.date_range(
            start=daily_demand["ds"].min(), end=daily_demand["ds"].max(), freq="D"
        )
        full_range_df = self.pd.DataFrame({"ds": date_range})
        daily_demand = full_range_df.merge(daily_demand, on="ds", how="left")
        daily_demand["y"] = daily_demand["y"].fillna(0)

        return daily_demand

    def detect_seasonality(self, model):
        """
        Phat hien seasonality tu trained Prophet model

        Args:
            model: Trained Prophet model

        Returns:
            tuple: (seasonality_detected, seasonality_type)
        """
        seasonality_detected = False
        seasonality_types = []

        # Check for weekly seasonality
        if "weekly" in model.seasonalities:
            seasonality_detected = True
            seasonality_types.append("Weekly")

        # Check for yearly seasonality
        if "yearly" in model.seasonalities:
            seasonality_detected = True
            seasonality_types.append("Yearly")

        # Check for monthly seasonality (if added)
        if "monthly" in model.seasonalities:
            seasonality_detected = True
            seasonality_types.append("Monthly")

        if len(seasonality_types) > 1:
            seasonality_type = "Multiple"
        elif len(seasonality_types) == 1:
            seasonality_type = seasonality_types[0]
        else:
            seasonality_type = None

        return seasonality_detected, seasonality_type

    def train_and_predict(
        self,
        prophet_data,
        forecast_period_days=30,
        lead_time_days=14,
        current_stock=0,
    ):
        """
        Train Prophet model va du doan demand

        Args:
            prophet_data: DataFrame voi 'ds' va 'y' columns
            forecast_period_days: So ngay can du doan
            lead_time_days: Lead time cho reorder
            current_stock: Stock hien tai

        Returns:
            dict: Forecast result hoac None neu khong du du lieu
        """
        try:
            if len(prophet_data) < 10:
                return None

            # Initialize Prophet model
            # Suppress Prophet's logging
            import logging

            logging.getLogger("prophet").setLevel(logging.ERROR)
            logging.getLogger("cmdstanpy").setLevel(logging.ERROR)

            model = self.Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality="auto",
                interval_width=0.95,  # 95% confidence interval
            )

            # Add monthly seasonality if enough data
            if len(prophet_data) > 60:  # At least 2 months
                model.add_seasonality(name="monthly", period=30.5, fourier_order=5)

            # Fit model
            model.fit(prophet_data)

            # Make future dataframe
            future = model.make_future_dataframe(periods=forecast_period_days)

            # Predict
            forecast = model.predict(future)

            # Get only future predictions
            future_forecast = forecast.tail(forecast_period_days)

            # Calculate predicted demand
            predicted_demand = float(future_forecast["yhat"].sum())
            predicted_demand = max(0, predicted_demand)  # No negative demand

            # Get confidence intervals
            lower_bound = float(future_forecast["yhat_lower"].sum())
            upper_bound = float(future_forecast["yhat_upper"].sum())
            lower_bound = max(0, lower_bound)

            # Detect seasonality
            seasonality_detected, seasonality_type = self.detect_seasonality(model)

            # Count changepoints (trend changes)
            changepoint_count = len(model.changepoints)

            # Calculate confidence score based on uncertainty
            # Smaller uncertainty = higher confidence
            uncertainty = upper_bound - lower_bound
            avg_prediction = predicted_demand / max(1, forecast_period_days)
            relative_uncertainty = (
                uncertainty / max(1, predicted_demand) if predicted_demand > 0 else 1
            )

            if relative_uncertainty < 0.2:
                confidence_score = 90
            elif relative_uncertainty < 0.5:
                confidence_score = 75
            else:
                confidence_score = 60

            # Calculate daily average from historical data
            total_days = len(prophet_data)
            total_demand = float(prophet_data["y"].sum())
            daily_avg = total_demand / max(1, total_days)

            # Detect trend from Prophet's trend component
            trend_start = (
                forecast["trend"]
                .iloc[len(prophet_data) - 30 : len(prophet_data)]
                .mean()
            )
            trend_end = forecast["trend"].iloc[-forecast_period_days:].mean()
            trend_change = trend_end - trend_start

            if trend_change > avg_prediction * 0.1:
                trend_type = "Upward"
            elif trend_change < -avg_prediction * 0.1:
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
            suggested_qty = max(
                1, int(daily_avg * (forecast_period_days + lead_time_days))
            )

            reorder_alert = current_stock <= reorder_level

            # Create forecast explanation
            seasonality_info = (
                f"Seasonality: {seasonality_type}"
                if seasonality_detected
                else "No seasonality detected"
            )

            forecast_explanation = f"""📊 PROPHET FORECAST ANALYSIS for {self.item_code}

🤖 MACHINE LEARNING INSIGHTS:
• Algorithm: Facebook Prophet
• Training Data: {len(prophet_data)} days of demand data
• Daily Demand Rate: {daily_avg:.2f} units/day
• Trend: {trend_type}
• {seasonality_info}
• Changepoints: {changepoint_count}

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
                "model_used": "Prophet",
                "model_confidence": f"Uncertainty: {relative_uncertainty:.2%}",
                "training_data_points": len(prophet_data),
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
                # Prophet specific
                "prophet_seasonality_detected": seasonality_detected,
                "prophet_seasonality_type": seasonality_type,
                "prophet_changepoint_count": changepoint_count,
                # Explanation
                "forecast_explanation": forecast_explanation,
                "recommendations": f"Based on Prophet model, the item shows {trend_type.lower()} trend with {movement_type.lower()} characteristics. {seasonality_info}.",
            }

        except Exception as e:
            frappe.log_error(f"Prophet forecast calculation failed: {str(e)}")
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
            prophet_data = self.prepare_data_from_sales_orders(sales_order_items)

            if prophet_data is None or len(prophet_data) < 10:
                return None

            # Train and predict
            result = self.train_and_predict(
                prophet_data,
                forecast_period_days,
                lead_time_days,
                current_stock,
            )

            return result

        except Exception as e:
            frappe.log_error(f"Prophet forecast failed: {str(e)}")
            return None
