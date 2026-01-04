# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class APSProductionPlan(Document):
	def validate(self):
		"""Validate Production Plan"""
		# Validate periods
		if self.plan_from_period and self.plan_to_period:
			if getdate(self.plan_from_period) >= getdate(self.plan_to_period):
				frappe.throw(_("Plan From Period must be before Plan To Period"))
		
		# Validate forecast history
		if self.source_type == "Forecast" and not self.forecast_history:
			frappe.throw(_("Forecast History is required when Source Type is Forecast"))
		
		# Validate items
		if self.items:
			for item in self.items:
				if item.planned_qty < 0:
					frappe.throw(
						_("Planned Quantity cannot be negative for item {0}").format(
							item.item
						)
					)
	
	def on_submit(self):
		"""Khi submit Production Plan"""
		if self.status == "Draft":
			self.status = "Planned"
	
	def on_cancel(self):
		"""Khi cancel Production Plan"""
		if self.status == "Planned":
			self.status = "Cancelled"
