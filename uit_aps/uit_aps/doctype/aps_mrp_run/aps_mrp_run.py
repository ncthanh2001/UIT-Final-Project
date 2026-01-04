# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class APSMRPRun(Document):
	def validate(self):
		"""Validate MRP Run"""
		# Validate Production Plan
		if self.production_plan:
			prod_plan = frappe.get_doc("APS Production Plan", self.production_plan)
			if prod_plan.status not in ["Planned", "Released"]:
				frappe.throw(
					_("Production Plan must be Planned or Released before running MRP")
				)
