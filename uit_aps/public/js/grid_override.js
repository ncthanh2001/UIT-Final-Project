// Override Grid class methods for Excel export/import support
// This file extends the Grid class from frappe to add Excel support

frappe.provide("uit_aps.grid_override");

// Function to apply overrides to Grid prototype
uit_aps.grid_override.apply_overrides = function () {
	// Strategy: Patch Grid prototype by intercepting when Grid instances are created
	// Since Grid is ES6 default export and may be bundled, we'll patch via ControlTable

	var patch_via_control_table = function () {
		// Patch ControlTable.make() to intercept Grid creation
		if (frappe.ui && frappe.ui.form && frappe.ui.form.ControlTable) {
			var ControlTable = frappe.ui.form.ControlTable;

			// Check if already patched
			if (ControlTable.prototype._uit_aps_make_patched) {
				return true;
			}

			var original_make = ControlTable.prototype.make;

			ControlTable.prototype.make = function () {
				// Patch Grid class BEFORE creating instance
				// This ensures setup_download is already overridden when called
				if (frappe.ui && frappe.ui.form && frappe.ui.form.ControlTable) {
					// Try to get Grid from import if possible
					// Since Grid is imported in table.js, we need to patch it there
					// For now, patch after creation but before setup_download is called
				}

				// Call original make first
				original_make.call(this);

				// After Grid is created, patch it immediately
				if (this.grid && this.grid.constructor) {
					var GridClass = this.grid.constructor;
					console.log("[UIT_APS] Grid instance created, patching prototype");
					uit_aps.grid_override.patch_grid_prototype(GridClass.prototype);

					// Patch instance methods directly to ensure they're overridden
					if (this.grid.setup_download) {
						console.log("[UIT_APS] Overriding setup_download on grid instance");
						this.grid.setup_download = uit_aps.grid_override.create_setup_download();
					}
					if (this.grid.setup_allow_bulk_edit) {
						console.log("[UIT_APS] Overriding setup_allow_bulk_edit on grid instance");
						var original_bulk_edit = this.grid.setup_allow_bulk_edit;
						this.grid.setup_allow_bulk_edit = function () {
							console.log("[UIT_APS] setup_allow_bulk_edit called on instance");
							// Call original first to setup download button
							original_bulk_edit.call(this);
							// Then override setup_download if it was just called
							if (this.setup_download) {
								this.setup_download =
									uit_aps.grid_override.create_setup_download();
							}
						};
					}
				}
			};

			ControlTable.prototype._uit_aps_make_patched = true;
			console.log("[UIT_APS] Patched ControlTable.make() to intercept Grid creation");
			return true;
		}
		return false;
	};

	var check_and_patch = function () {
		// Try to find Grid class
		var Grid = null;

		// Approach 1: Check frappe.ui.form
		if (frappe.ui && frappe.ui.form && frappe.ui.form.Grid) {
			Grid = frappe.ui.form.Grid;
		}
		// Approach 2: Check window
		else if (window.Grid) {
			Grid = window.Grid;
		}
		// Approach 3: Try to find Grid from existing instances
		if (!Grid && frappe.ui && frappe.ui.form) {
			// Try to find from cur_frm if available
			if (window.cur_frm && window.cur_frm.grids) {
				for (var fieldname in window.cur_frm.grids) {
					var grid = window.cur_frm.grids[fieldname];
					if (grid && grid.constructor) {
						Grid = grid.constructor;
						break;
					}
				}
			}
		}

		if (Grid && Grid.prototype) {
			// Found Grid class, apply patches
			uit_aps.grid_override.patch_grid_prototype(Grid.prototype);
			return true;
		} else {
			// Not found yet, retry
			return false;
		}
	};

	// Try to patch via ControlTable first (most reliable)
	var patched_via_control = patch_via_control_table();

	// Also try direct patch
	var patched = check_and_patch();

	if (!patched && !patched_via_control) {
		// If not found, retry with intervals
		var retry_count = 0;
		var max_retries = 50; // Try for 5 seconds (50 * 100ms)
		var retry_interval = setInterval(function () {
			retry_count++;
			if (check_and_patch() || retry_count >= max_retries) {
				clearInterval(retry_interval);
			}
		}, 100);
	}

	// Also try to patch when forms are loaded
	if (typeof $(document) !== "undefined") {
		$(document).on("form-load", function () {
			setTimeout(check_and_patch, 100);
		});
	}
};

// Patch Grid prototype with our overrides
uit_aps.grid_override.patch_grid_prototype = function (prototype) {
	// Only patch if not already patched
	if (prototype._uit_aps_patched) {
		console.log("[UIT_APS] Grid already patched, skipping");
		return;
	}
	prototype._uit_aps_patched = true;
	console.log("[UIT_APS] Patching Grid prototype for Excel support");

	// Create setup_download function that can be used for both prototype and instance
	uit_aps.grid_override.create_setup_download = function (grid_instance) {
		return function () {
			console.log("[UIT_APS] setup_download called - using override");
			let title = this.df.label || frappe.model.unscrub(this.df.fieldname);
			let me = this;
			$(this.wrapper)
				.find(".grid-download")
				.removeClass("hidden")
				.off("click") // Remove any existing handlers
				.on("click", () => {
					console.log("[UIT_APS] Download button clicked");
					// Hien thi dialog de chon dinh dang
					let d = new frappe.ui.Dialog({
						title: __("Export {0}", [title]),
						fields: [
							{
								label: __("File Format"),
								fieldname: "file_format",
								fieldtype: "Select",
								options: ["CSV", "Excel"],
								default: "CSV",
								reqd: 1,
							},
						],
						primary_action_label: __("Export"),
						primary_action(values) {
							console.log("[UIT_APS] Export format selected:", values.file_format);
							d.hide();
							me.export_data(values.file_format, title);
						},
					});
					d.show();
					return false;
				});
		};
	};

	// Override setup_download method
	var original_setup_download = prototype.setup_download;
	prototype.setup_download = uit_aps.grid_override.create_setup_download();

	// Add export_data method
	prototype.export_data = function (file_format, title) {
		var data = [];
		var docfields = [];
		data.push([__("Bulk Edit {0}", [title])]);
		data.push([]);
		data.push([]);
		data.push([]);
		data.push([__("The CSV format is case sensitive")]);
		data.push([__("Do not edit headers which are preset in the template")]);
		data.push(["------"]);
		$.each(frappe.get_meta(this.df.options).fields, (i, df) => {
			// don't include the read-only field in the template
			if (frappe.model.is_value_type(df.fieldtype)) {
				data[1].push(df.label);
				data[2].push(df.fieldname);
				let description = (df.description || "") + " ";
				if (df.fieldtype === "Date") {
					description += frappe.boot.sysdefaults.date_format;
				}
				data[3].push(description);
				docfields.push(df);
			}
		});

		// add data
		$.each(this.frm.doc[this.df.fieldname] || [], (i, d) => {
			var row = [];
			$.each(data[2], (i, fieldname) => {
				var value = d[fieldname];

				// format date
				if (docfields[i].fieldtype === "Date" && value) {
					value = frappe.datetime.str_to_user(value);
				}

				row.push(value || "");
			});
			data.push(row);
		});

		// Xuat file theo dinh dang da chon
		if (file_format === "Excel") {
			frappe.tools.downloadify_excel(data, null, title);
		} else {
			frappe.tools.downloadify(data, null, title);
		}
	};

	// Override setup_allow_bulk_edit method
	var original_setup_allow_bulk_edit = prototype.setup_allow_bulk_edit;
	prototype.setup_allow_bulk_edit = function () {
		console.log("[UIT_APS] setup_allow_bulk_edit called - using override");

		// IMPORTANT: Override setup_download BEFORE calling original
		// because original_setup_allow_bulk_edit will call this.setup_download()
		this.setup_download = uit_aps.grid_override.create_setup_download();
		let me = this;
		if (this.frm && this.frm.get_docfield(this.df.fieldname)?.allow_bulk_edit) {
			// download
			this.setup_download();

			const value_formatter_map = {
				Date: (val) => (val ? frappe.datetime.user_to_str(val) : val),
				Int: (val) => cint(val),
				Check: (val) => cint(val),
				Float: (val) => flt(val),
				Currency: (val) => flt(val),
			};

			// upload
			frappe.flags.no_socketio = true;
			$(this.wrapper)
				.find(".grid-upload")
				.removeClass("hidden")
				.on("click", () => {
					new frappe.ui.FileUploader({
						as_dataurl: true,
						allow_multiple: false,
						restrictions: {
							allowed_file_types: [".csv", ".xlsx", ".xls"],
						},
						on_success(file) {
							// Kiem tra loai file
							var file_ext = file.name.toLowerCase().split(".").pop();
							var is_excel = file_ext === "xlsx" || file_ext === "xls";

							// Ham xu ly du lieu sau khi doc file
							var process_data = function (data) {
								if (cint(data.length) - 7 > 5000) {
									frappe.throw(
										__("Cannot import table with more than 5000 rows."),
									);
								}
								// row #2 contains fieldnames;
								var fieldnames = data[2];
								me.frm.clear_table(me.df.fieldname);
								$.each(data, (i, row) => {
									if (i > 6) {
										var blank_row = true;
										$.each(row, function (ci, value) {
											if (value) {
												blank_row = false;
												return false;
											}
										});

										if (!blank_row) {
											var d = me.frm.add_child(me.df.fieldname);
											$.each(row, (ci, value) => {
												var fieldname = fieldnames[ci];
												var df = frappe.meta.get_docfield(
													me.df.options,
													fieldname,
												);
												if (df) {
													d[fieldnames[ci]] = value_formatter_map[
														df.fieldtype
													]
														? value_formatter_map[df.fieldtype](value)
														: value;
												}
											});
										}
									}
								});

								me.frm.refresh_field(me.df.fieldname);
								frappe.msgprint({
									message: __("Table updated"),
									title: __("Success"),
									indicator: "green",
								});
							};

							// Xu ly file CSV
							if (!is_excel) {
								var data = frappe.utils.csv_to_array(
									frappe.utils.get_decoded_string(file.dataurl),
								);
								process_data(data);
							} else {
								// Xu ly file Excel
								me.read_excel_file(file, process_data);
							}
						},
					});
					return false;
				});
		}
	};

	// Add read_excel_file method
	prototype.read_excel_file = function (file, callback) {
		var me = this;

		// Ham xu ly doc file Excel
		var process_excel = function () {
			try {
				var workbook;

				// Neu co file object goc, su dung no
				if (file.file_obj) {
					var reader = new FileReader();
					reader.onload = function (e) {
						try {
							var data = new Uint8Array(e.target.result);
							workbook = XLSX.read(data, { type: "array" });
							var result = me.convert_workbook_to_array(workbook);
							callback(result);
						} catch (error) {
							frappe.msgprint({
								message: __("Error reading Excel file: {0}", [error.message]),
								title: __("Error"),
								indicator: "red",
							});
						}
					};
					reader.onerror = function () {
						frappe.msgprint({
							message: __("Error reading file"),
							title: __("Error"),
							indicator: "red",
						});
					};
					reader.readAsArrayBuffer(file.file_obj);
				} else if (file.dataurl) {
					// Neu chi co dataurl, doc tu base64
					var base64_data = file.dataurl.split(",")[1];
					var binary_string = atob(base64_data);
					var bytes = new Uint8Array(binary_string.length);
					for (var i = 0; i < binary_string.length; i++) {
						bytes[i] = binary_string.charCodeAt(i);
					}

					workbook = XLSX.read(bytes, { type: "array" });
					var result = me.convert_workbook_to_array(workbook);
					callback(result);
				} else {
					frappe.msgprint({
						message: __("Cannot read file data"),
						title: __("Error"),
						indicator: "red",
					});
				}
			} catch (error) {
				frappe.msgprint({
					message: __("Error reading Excel file: {0}", [error.message]),
					title: __("Error"),
					indicator: "red",
				});
			}
		};

		// Kiem tra xem co XLSX library khong
		if (typeof XLSX !== "undefined") {
			process_excel();
		} else {
			// Neu khong co XLSX, kiem tra xem da tai script chua
			if (document.querySelector('script[src*="xlsx"]')) {
				// Script dang duoc tai, cho doi
				setTimeout(function () {
					me.read_excel_file(file, callback);
				}, 100);
				return;
			}

			// Tai XLSX tu CDN
			var script = document.createElement("script");
			script.src = "https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js";
			script.onload = function () {
				// Sau khi tai xong, goi lai ham
				me.read_excel_file(file, callback);
			};
			script.onerror = function () {
				frappe.msgprint({
					message: __(
						"Cannot load Excel library. Please try uploading a CSV file instead.",
					),
					title: __("Error"),
					indicator: "red",
				});
			};
			document.head.appendChild(script);
		}
	};

	// Add convert_workbook_to_array method
	prototype.convert_workbook_to_array = function (workbook) {
		var first_sheet_name = workbook.SheetNames[0];
		var worksheet = workbook.Sheets[first_sheet_name];
		var data = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: "" });

		// Chuyen doi thanh array 2 chieu
		var result = [];
		for (var i = 0; i < data.length; i++) {
			var row = data[i];
			var arr_row = [];
			// Tim do dai toi da cua cac row de dam bao tat ca cac row co cung so cot
			var max_cols = 0;
			for (var j = 0; j < data.length; j++) {
				if (data[j] && data[j].length > max_cols) {
					max_cols = data[j].length;
				}
			}

			for (var j = 0; j < max_cols; j++) {
				arr_row.push(row[j] !== undefined && row[j] !== null ? row[j] : "");
			}
			result.push(arr_row);
		}

		return result;
	};
};

// Apply overrides when frappe is ready
// Use multiple approaches to ensure it runs at the right time
(function () {
	console.log("[UIT_APS] Applying grid overrides");
	var apply_overrides_when_ready = function () {
		// Wait a bit for Grid module to be loaded
		setTimeout(function () {
			uit_aps.grid_override.apply_overrides();
		}, 500);
	};

	// Approach 1: Use jQuery document ready
	if (typeof $ !== "undefined") {
		$(document).ready(function () {
			// Wait for app_ready event
			$(document).one("app_ready", apply_overrides_when_ready);

			// Fallback: if app already initialized, apply after delay
			if (typeof frappe !== "undefined" && frappe.app) {
				setTimeout(apply_overrides_when_ready, 1000);
			} else {
				// If app not ready, wait a bit longer
				setTimeout(apply_overrides_when_ready, 2000);
			}
		});
	} else {
		// If jQuery not available yet, wait for it
		if (document.readyState === "loading") {
			document.addEventListener("DOMContentLoaded", function () {
				setTimeout(apply_overrides_when_ready, 1000);
			});
		} else {
			// DOM already loaded
			setTimeout(apply_overrides_when_ready, 1000);
		}
	}
})();
