# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate
from collections import defaultdict


class APSPurchaseSuggestion(Document):
	def validate(self):
		"""Validate Purchase Suggestion"""
		if self.purchase_qty <= 0:
			frappe.throw(_("Purchase Quantity must be greater than 0"))
		
		if self.suggestion_status == "Ordered" and not self.supplier:
			frappe.throw(_("Supplier is required when status is Ordered"))


@frappe.whitelist()
def make_purchase_order_from_suggestion(suggestion_name):
	"""
	Tao Purchase Order tu 1 APS Purchase Suggestion
	
	Args:
		suggestion_name: Name cua APS Purchase Suggestion
	
	Returns:
		dict: Purchase Order name
	"""
	try:
		suggestion = frappe.get_doc("APS Purchase Suggestion", suggestion_name)
		
		# Validate
		if suggestion.suggestion_status == "Ordered":
			frappe.throw(_("Purchase Order already created for this suggestion"))
		
		if not suggestion.supplier:
			frappe.throw(_("Please select a supplier first"))
		
		# Lay company tu Production Plan
		company = get_company_from_suggestion(suggestion)
		if not company:
			frappe.throw(_("Could not determine company. Please check MRP Run and Production Plan"))
		
		# Tinh transaction_date va schedule_date
		transaction_date = nowdate()
		required_date = suggestion.required_date or transaction_date
		
		# Ensure schedule_date >= transaction_date
		if getdate(required_date) < getdate(transaction_date):
			schedule_date = transaction_date
		else:
			schedule_date = required_date
		
		# Tao Purchase Order
		po = frappe.get_doc({
			"doctype": "Purchase Order",
			"company": company,
			"supplier": suggestion.supplier,
			"transaction_date": transaction_date,
			"schedule_date": schedule_date,
		})
		
		# Lay warehouse cho item
		warehouse = get_item_warehouse(suggestion.material_item, company)
		
		# Add item
		item_dict = {
			"item_code": suggestion.material_item,
			"qty": suggestion.purchase_qty,
			"rate": suggestion.unit_price or 0,
			"schedule_date": schedule_date,
		}
		
		# Chi them warehouse neu item la stock item
		item = frappe.get_doc("Item", suggestion.material_item)
		if item.is_stock_item:
			if not warehouse:
				frappe.throw(
					_("Warehouse is required for stock item {0}. Please set default warehouse in Item Default or Stock Settings").format(
						suggestion.material_item
					)
				)
			item_dict["warehouse"] = warehouse
		
		po.append("items", item_dict)
		
		po.insert()
		po.save()
		frappe.db.commit()
		
		# Update suggestion status
		suggestion.suggestion_status = "Ordered"
		suggestion.save()
		frappe.db.commit()
		
		return {
			"success": True,
			"purchase_order": po.name,
		}
	
	except Exception as e:
		frappe.log_error(
			f"Error creating Purchase Order from suggestion: {str(e)}",
			"Purchase Order Creation Error"
		)
		frappe.throw(_("Failed to create Purchase Order: {0}").format(str(e)))


@frappe.whitelist()
def make_purchase_orders_from_suggestions(suggestion_names):
	"""
	Tao Purchase Orders tu nhieu APS Purchase Suggestions
	Group theo supplier de tao nhieu Purchase Orders
	
	Args:
		suggestion_names: List of suggestion names (JSON string hoac list)
	
	Returns:
		dict: List of Purchase Orders created
	"""
	try:
		# Parse suggestion names
		if isinstance(suggestion_names, str):
			import json
			suggestion_names = json.loads(suggestion_names)
		
		if not suggestion_names:
			frappe.throw(_("No suggestions selected"))
		
		# Load suggestions
		suggestions = frappe.get_all(
			"APS Purchase Suggestion",
			filters={"name": ["in", suggestion_names]},
			fields=[
				"name",
				"material_item",
				"purchase_qty",
				"required_date",
				"supplier",
				"unit_price",
				"suggestion_status",
			],
		)
		
		if not suggestions:
			frappe.throw(_("No valid suggestions found"))
		
		# Validate
		for sug in suggestions:
			if sug.suggestion_status == "Ordered":
				frappe.throw(
					_("Purchase Order already created for suggestion {0}").format(sug.name)
				)
			if not sug.supplier:
				frappe.throw(
					_("Please select supplier for suggestion {0}").format(sug.name)
				)
		
		# Group theo supplier
		supplier_groups = defaultdict(list)
		for sug in suggestions:
			supplier_groups[sug.supplier].append(sug)
		
		# Lay company (lay tu suggestion dau tien)
		first_suggestion = frappe.get_doc("APS Purchase Suggestion", suggestions[0].name)
		company = get_company_from_suggestion(first_suggestion)
		if not company:
			frappe.throw(_("Could not determine company"))
		
		# Tao Purchase Orders (moi supplier 1 PO)
		purchase_orders = []
		transaction_date = nowdate()
		
		for supplier, supplier_suggestions in supplier_groups.items():
			# Tim earliest required_date
			earliest_date = None
			for sug in supplier_suggestions:
				if sug.required_date:
					if not earliest_date or getdate(sug.required_date) < getdate(earliest_date):
						earliest_date = sug.required_date
			
			# Ensure schedule_date >= transaction_date
			if earliest_date and getdate(earliest_date) < getdate(transaction_date):
				schedule_date = transaction_date
			else:
				schedule_date = earliest_date or transaction_date
			
			# Tao Purchase Order cho supplier nay
			po = frappe.get_doc({
				"doctype": "Purchase Order",
				"company": company,
				"supplier": supplier,
				"transaction_date": transaction_date,
				"schedule_date": schedule_date,
			})
			
			# Add items
			for sug in supplier_suggestions:
				# Ensure item schedule_date >= transaction_date
				item_required_date = sug.required_date or schedule_date
				if getdate(item_required_date) < getdate(transaction_date):
					item_schedule_date = transaction_date
				else:
					item_schedule_date = item_required_date
				
				# Lay warehouse cho item
				warehouse = get_item_warehouse(sug.material_item, company)
				
				# Add item
				item_dict = {
					"item_code": sug.material_item,
					"qty": sug.purchase_qty,
					"rate": sug.unit_price or 0,
					"schedule_date": item_schedule_date,
				}
				
				# Chi them warehouse neu item la stock item
				item = frappe.get_doc("Item", sug.material_item)
				if item.is_stock_item:
					if not warehouse:
						frappe.throw(
							_("Warehouse is required for stock item {0}. Please set default warehouse in Item Default or Stock Settings").format(
								sug.material_item
							)
						)
					item_dict["warehouse"] = warehouse
				
				po.append("items", item_dict)
			
			po.insert()
			po.save()
			purchase_orders.append(po.name)
			
			# Update suggestion status
			for sug in supplier_suggestions:
				suggestion_doc = frappe.get_doc("APS Purchase Suggestion", sug.name)
				suggestion_doc.suggestion_status = "Ordered"
				suggestion_doc.save()
		
		frappe.db.commit()
		
		return {
			"success": True,
			"purchase_orders": purchase_orders,
			"count": len(purchase_orders),
		}
	
	except Exception as e:
		frappe.log_error(
			f"Error creating Purchase Orders from suggestions: {str(e)}",
			"Purchase Order Creation Error"
		)
		frappe.throw(_("Failed to create Purchase Orders: {0}").format(str(e)))


def get_company_from_suggestion(suggestion):
	"""
	Lay company tu Purchase Suggestion thong qua MRP Run -> Production Plan
	
	Args:
		suggestion: APS Purchase Suggestion document
	
	Returns:
		str: Company name hoac None
	"""
	try:
		if suggestion.mrp_run:
			mrp_run = frappe.get_doc("APS MRP Run", suggestion.mrp_run)
			if mrp_run.production_plan:
				prod_plan = frappe.get_doc("APS Production Plan", mrp_run.production_plan)
				return prod_plan.company
		return None
	except Exception:
		return None


def get_item_warehouse(item_code, company):
	"""
	Lay warehouse cho item (tu Item Default hoac Stock Settings)
	
	Args:
		item_code: Item code
		company: Company
	
	Returns:
		str: Warehouse name hoac None
	"""
	try:
		# 1. Lay tu Item Default
		item_defaults = frappe.get_all(
			"Item Default",
			filters={"parent": item_code, "company": company},
			fields=["default_warehouse"],
			limit=1,
		)
		
		if item_defaults and item_defaults[0].default_warehouse:
			warehouse_name = item_defaults[0].default_warehouse
			# Check warehouse khong bi disabled
			warehouse_disabled = frappe.db.get_value("Warehouse", warehouse_name, "disabled")
			if not warehouse_disabled:
				return warehouse_name
		
		# 2. Lay tu Item Group Default
		item = frappe.get_doc("Item", item_code)
		if item.item_group:
			item_group_defaults = frappe.get_all(
				"Item Default",
				filters={"parent": item.item_group, "company": company},
				fields=["default_warehouse"],
				limit=1,
			)
			
			if item_group_defaults and item_group_defaults[0].default_warehouse:
				warehouse_name = item_group_defaults[0].default_warehouse
				# Check warehouse khong bi disabled
				warehouse_disabled = frappe.db.get_value("Warehouse", warehouse_name, "disabled")
				if not warehouse_disabled:
					return warehouse_name
		
		# 3. Lay tu Stock Settings
		default_warehouse = frappe.get_single_value("Stock Settings", "default_warehouse")
		if default_warehouse:
			# Check warehouse belongs to company and not disabled
			warehouse_info = frappe.db.get_value(
				"Warehouse",
				default_warehouse,
				["company", "disabled"],
				as_dict=True
			)
			if warehouse_info and warehouse_info.company == company and not warehouse_info.disabled:
				return default_warehouse
		
		# 4. Tim bat ky warehouse nao cua company (khong disabled)
		warehouses = frappe.get_all(
			"Warehouse",
			filters={"company": company, "is_group": 0, "disabled": 0},
			fields=["name"],
			limit=1,
		)
		
		if warehouses:
			return warehouses[0].name
		
		return None
	except Exception:
		return None
