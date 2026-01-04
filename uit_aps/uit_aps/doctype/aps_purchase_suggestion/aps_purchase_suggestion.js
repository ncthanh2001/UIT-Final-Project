// Copyright (c) 2025, thanhnc and contributors
// For license information, please see license.txt

frappe.ui.form.on("APS Purchase Suggestion", {
	refresh(frm) {
		// Button tao Purchase Order (chi khi status chua phai Ordered)
		if (frm.doc.suggestion_status !== "Ordered" && frm.doc.supplier) {
			frm.add_custom_button(__("Create Purchase Order"), function() {
				create_purchase_order(frm);
			});
		}
		
		// Button view Purchase Order neu da tao
		if (frm.doc.suggestion_status === "Ordered") {
			frm.add_custom_button(__("View Purchase Orders"), function() {
				frappe.set_route("List", "Purchase Order", {
					"supplier": frm.doc.supplier
				});
			});
		}
	},
	
	suggestion_status(frm) {
		// Validate khi set status = Ordered
		if (frm.doc.suggestion_status === "Ordered" && !frm.doc.supplier) {
			frappe.msgprint(__("Please select a supplier before setting status to Ordered"));
			frm.set_value("suggestion_status", "Draft");
		}
	}
});

function create_purchase_order(frm) {
	if (!frm.doc.supplier) {
		frappe.msgprint(__("Please select a supplier first"));
		return;
	}
	
	if (frm.doc.suggestion_status === "Ordered") {
		frappe.msgprint(__("Purchase Order already created for this suggestion"));
		return;
	}
	
	frappe.confirm(
		__("Create Purchase Order for this suggestion?"),
		function() {
			// Yes
			frappe.call({
				method: "uit_aps.uit_aps.doctype.aps_purchase_suggestion.aps_purchase_suggestion.make_purchase_order_from_suggestion",
				args: {
					suggestion_name: frm.doc.name
				},
				freeze: true,
				freeze_message: __("Creating Purchase Order..."),
				callback: function(r) {
					if (r.message && r.message.success) {
						frappe.show_alert({
							message: __("Purchase Order {0} created", [r.message.purchase_order]),
							indicator: "green"
						});
						// Reload form to update status
						frm.reload_doc();
						// Navigate to Purchase Order
						frappe.set_route("Form", "Purchase Order", r.message.purchase_order);
					}
				}
			});
		},
		function() {
			// No
		}
	);
}
