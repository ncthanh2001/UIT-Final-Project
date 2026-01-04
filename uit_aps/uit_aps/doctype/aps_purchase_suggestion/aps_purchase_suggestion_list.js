// Copyright (c) 2025, thanhnc and contributors
// For license information, please see license.txt

frappe.listview_settings['APS Purchase Suggestion'] = {
	add_fields: ["suggestion_status", "supplier"],
	
	get_indicator: function(doc) {
		var colors = {
			"Draft": "grey",
			"Approved": "blue",
			"Ordered": "green",
			"Rejected": "red"
		};
		return [__(doc.suggestion_status), colors[doc.suggestion_status], "suggestion_status,=," + doc.suggestion_status];
	},
	
	onload: function(listview) {
		// Bulk action: Create Purchase Orders
		listview.page.add_menu_item(__("Create Purchase Orders"), function() {
			create_purchase_orders_from_selected(listview);
		});
	}
};

function create_purchase_orders_from_selected(listview) {
	let selected = listview.get_checked_items();
	
	if (selected.length === 0) {
		frappe.msgprint(__("Please select at least one Purchase Suggestion"));
		return;
	}
	
	// Filter only suggestions that can be converted
	let valid_suggestions = selected.filter(function(sug) {
		return sug.suggestion_status !== "Ordered" && sug.supplier;
	});
	
	if (valid_suggestions.length === 0) {
		frappe.msgprint(__("No valid suggestions selected. Please ensure suggestions have supplier and are not already Ordered"));
		return;
	}
	
	// Check if there are suggestions without supplier
	let without_supplier = selected.filter(function(sug) {
		return sug.suggestion_status !== "Ordered" && !sug.supplier;
	});
	
	if (without_supplier.length > 0) {
		frappe.msgprint({
			message: __("{0} suggestions do not have supplier and will be skipped", [without_supplier.length]),
			indicator: "orange"
		});
	}
	
	frappe.confirm(
		__("Create Purchase Orders for {0} selected suggestion(s)?", [valid_suggestions.length]),
		function() {
			// Yes
			let suggestion_names = valid_suggestions.map(function(sug) {
				return sug.name;
			});
			
			frappe.call({
				method: "uit_aps.uit_aps.doctype.aps_purchase_suggestion.aps_purchase_suggestion.make_purchase_orders_from_suggestions",
				args: {
					suggestion_names: suggestion_names
				},
				freeze: true,
				freeze_message: __("Creating Purchase Orders..."),
				callback: function(r) {
					if (r.message && r.message.success) {
						frappe.show_alert({
							message: __("Created {0} Purchase Order(s)", [r.message.count]),
							indicator: "green"
						});
						
						// Refresh list
						listview.refresh();
						
						// Optionally navigate to Purchase Orders
						if (r.message.purchase_orders && r.message.purchase_orders.length > 0) {
							frappe.set_route("List", "Purchase Order", {
								"name": ["in", r.message.purchase_orders]
							});
						}
					}
				}
			});
		},
		function() {
			// No
		}
	);
}

