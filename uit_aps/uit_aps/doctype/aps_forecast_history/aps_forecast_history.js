// Copyright (c) 2025, thanhnc and contributors
// For license information, please see license.txt

frappe.ui.form.on("APS Forecast History", {
	refresh(frm) {
            frm.add_custom_button(__("Generate from Forecast"), function() {
               frappe.msgprint(__("Generate from Forecast"));
            });
	},
});
