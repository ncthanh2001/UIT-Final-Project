// Copyright (c) 2025, thanhnc and contributors
// For license information, please see license.txt

frappe.ui.form.on("APS Production Plan", {
	refresh(frm) {
		// Button generate tu Forecast
		if (frm.doc.forecast_history && frm.doc.status === "Draft") {
			frm.add_custom_button(__("Generate from Forecast"), function() {
				generate_from_forecast(frm);
			});
		}
		
		// Button refresh items
		if (frm.doc.forecast_history && frm.doc.status === "Draft") {
			frm.add_custom_button(__("Refresh Items"), function() {
				refresh_plan_items(frm);
			});
		}
	},
	
	forecast_history(frm) {
		// Auto fill plan period tu forecast history
		if (frm.doc.forecast_history) {
			frappe.call({
				method: "uit_aps.uit_api.production_plan.get_forecast_period",
				args: {
					forecast_history: frm.doc.forecast_history
				},
				callback: function(r) {
					if (r.message) {
						if (r.message.start_date) {
							frm.set_value("plan_from_period", r.message.start_date);
						}
						if (r.message.end_date) {
							frm.set_value("plan_to_period", r.message.end_date);
						}
						if (r.message.company && !frm.doc.company) {
							frm.set_value("company", r.message.company);
						}
					}
				}
			});
		}
	}
});

function generate_from_forecast(frm) {
	if (!frm.doc.forecast_history) {
		frappe.msgprint(__("Please select Forecast History first"));
		return;
	}
	
	if (!frm.doc.plan_from_period || !frm.doc.plan_to_period) {
		frappe.msgprint(__("Please set Plan From Period and Plan To Period first"));
		return;
	}
	
	// Neu chua save, phai save truoc
	if (!frm.doc.name) {
		frappe.msgprint(__("Please save the Production Plan first"));
		return;
	}
	
	// Check status
	if (frm.doc.status !== "Draft") {
		frappe.msgprint(__("Can only generate items when status is Draft"));
		return;
	}
	
	var confirm_message = __("This will generate Production Plan items from Forecast Results.");
	if (frm.doc.items && frm.doc.items.length > 0) {
		confirm_message += __(" Existing items will be replaced. Continue?");
	} else {
		confirm_message += __(" Continue?");
	}
	
	frappe.confirm(
		confirm_message,
		function() {
			// Yes
			frappe.call({
				method: "uit_aps.uit_api.production_plan.generate_production_plan_from_forecast",
				args: {
					forecast_history: frm.doc.forecast_history,
					plan_name: frm.doc.plan_name,
					plan_from_period: frm.doc.plan_from_period,
					plan_to_period: frm.doc.plan_to_period,
					time_granularity: frm.doc.time_granularity || "Monthly",
					company: frm.doc.company,
					production_plan_name: frm.doc.name, // Truyen name de update Production Plan hien tai
				},
				freeze: true,
				freeze_message: __("Generating Production Plan items..."),
				callback: function(r) {
					if (r.message && r.message.success) {
						frappe.show_alert({
							message: __("Generated {0} items", [r.message.items_created]),
							indicator: "green"
						});
						frm.reload_doc();
					}
				}
			});
		},
		function() {
			// No
		}
	);
}

function refresh_plan_items(frm) {
	if (!frm.doc.name) {
		frappe.msgprint(__("Please save the Production Plan first"));
		return;
	}
	
	if (frm.doc.status !== "Draft") {
		frappe.msgprint(__("Can only refresh items when status is Draft"));
		return;
	}
	
	frappe.confirm(
		__("This will replace all existing items. Continue?"),
		function() {
			// Yes
			frappe.call({
				method: "uit_aps.uit_api.production_plan.refresh_plan_items",
				args: {
					production_plan_name: frm.doc.name
				},
				freeze: true,
				freeze_message: __("Refreshing items..."),
				callback: function(r) {
					if (r.message && r.message.success) {
						frappe.show_alert({
							message: __("Refreshed {0} items", [r.message.items_created]),
							indicator: "green"
						});
						frm.reload_doc();
					}
				}
			});
		},
		function() {
			// No
		}
	);
}
