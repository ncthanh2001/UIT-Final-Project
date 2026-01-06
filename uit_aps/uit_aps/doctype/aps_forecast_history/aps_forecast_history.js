// Copyright (c) 2025, thanhnc and contributors
// For license information, please see license.txt

frappe.ui.form.on("APS Forecast History", {
	refresh(frm) {
            frm.add_custom_button(__("View Dashboard"), function() {
                window.open(`/frontend/dashboard?history=${frm.doc.name}`, "_blank");
            });
	},
});
