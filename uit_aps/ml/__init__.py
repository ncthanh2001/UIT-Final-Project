# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
ML Models for AI Inventory Forecast
"""

from uit_aps.ml.linear_regression_model import LinearRegressionForecast
from uit_aps.ml.arima_model import ARIMAForecast

__all__ = ["LinearRegressionForecast", "ARIMAForecast"]
