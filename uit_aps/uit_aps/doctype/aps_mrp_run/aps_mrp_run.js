// Copyright (c) 2025, thanhnc and contributors
// For license information, please see license.txt

frappe.ui.form.on("APS MRP Run", {
	refresh(frm) {
		// Button run MRP Optimization
		if (frm.doc.production_plan && frm.doc.run_status === "Pending") {
			frm.add_custom_button(__("Run MRP Optimization"), function() {
				run_mrp_optimization(frm);
			});
		}
		
		// Button view MRP Results
		if (frm.doc.name && frm.doc.run_status === "Completed") {
			frm.add_custom_button(__("View MRP Results"), function() {
				frappe.set_route("List", "APS MRP Result", {
					"mrp_run": frm.doc.name
				});
			});
			
			frm.add_custom_button(__("View Purchase Suggestions"), function() {
				frappe.set_route("List", "APS Purchase Suggestion", {
					"mrp_run": frm.doc.name
				});
			});
		}
	},
	
	production_plan(frm) {
		// Auto fill thong tin tu Production Plan
		if (frm.doc.production_plan) {
			frappe.db.get_doc("APS Production Plan", frm.doc.production_plan)
				.then(function(prod_plan) {
					// Co the auto fill thong tin neu can
				});
		}
	}
});

function run_mrp_optimization(frm) {
	if (!frm.doc.production_plan) {
		frappe.msgprint(__("Please select Production Plan first"));
		return;
	}
	
	frappe.confirm(
		__("This will run MRP Optimization to calculate material requirements and create Purchase Suggestions. Continue?"),
		function() {
			// Yes
			frappe.call({
				method: "uit_aps.uit_api.mrp_optimization.run_mrp_optimization",
				args: {
					production_plan: frm.doc.production_plan,
					buffer_days: 0,  // Co the them field de user nhap
					include_non_stock_items: false,
				},
				freeze: true,
				freeze_message: __("Running MRP Optimization..."),
				callback: function(r) {
					if (r.message && r.message.success) {
						frappe.show_alert({
							message: __("MRP Optimization completed. Created {0} MRP Results and {1} Purchase Suggestions", 
								[r.message.mrp_results_created, r.message.purchase_suggestions_created]),
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
