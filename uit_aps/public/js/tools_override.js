// Override frappe.tools to add Excel export support
// This ensures downloadify_excel is available even if frappe core doesn't have it

frappe.provide("frappe.tools");

// Ham xuat Excel - su dung XLSX neu co, neu khong thi tai tu CDN hoac fallback ve CSV
if (!frappe.tools.downloadify_excel) {
	frappe.tools.downloadify_excel = function (data, roles, title) {
		if (roles && roles.length && !has_common(roles, roles)) {
			frappe.msgprint(
				__("Export not allowed. You need {0} role to export.", [
					frappe.utils.comma_or(roles),
				]),
			);
			return;
		}

		var filename = title + ".xlsx";

		// Kiem tra xem co XLSX library khong
		if (typeof XLSX !== "undefined") {
			// Su dung XLSX library de tao file Excel
			var wb = XLSX.utils.book_new();
			var ws = XLSX.utils.aoa_to_sheet(data);
			XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
			XLSX.writeFile(wb, filename);
		} else {
			// Neu khong co XLSX, kiem tra xem da tai script chua
			if (document.querySelector('script[src*="xlsx"]')) {
				// Script dang duoc tai, cho doi
				setTimeout(function () {
					frappe.tools.downloadify_excel(data, roles, title);
				}, 100);
				return;
			}

			// Tai XLSX tu CDN
			var script = document.createElement("script");
			script.src = "https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js";
			script.onload = function () {
				// Sau khi tai xong, goi lai ham
				frappe.tools.downloadify_excel(data, roles, title);
			};
			script.onerror = function () {
				// Neu khong tai duoc, fallback ve CSV
				frappe.msgprint({
					message: __("Cannot load Excel library. Exporting as CSV instead."),
					indicator: "orange",
				});
				frappe.tools.downloadify(data, roles, title);
			};
			document.head.appendChild(script);
		}
	};
}
