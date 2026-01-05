// Copyright (c) 2025, thanhnc and contributors
// For license information, please see license.txt

frappe.listview_settings["APS Scheduling Result"] = {
	// Them field subject vao data de Gantt view co the hien thi
	onload: function(listview) {
		listview.page.add_inner_button(__("Gantt"), function() {
			frappe.set_route("List", "APS Scheduling Result", "Gantt");
		});
		
		// Override prepare_tasks de tinh toan title
		if (listview.view_name === "Gantt") {
			const original_prepare_tasks = listview.prepare_tasks;
			listview.prepare_tasks = function() {
				original_prepare_tasks.call(this);
				
				// Tinh toan subject cho moi task
				this.tasks = this.tasks.map((task) => {
					const item = this.data.find((d) => d.name === task.id);
					if (item) {
						const subject_parts = [];
						if (item.job_card) {
							subject_parts.push(`Job Card: ${item.job_card}`);
						}
						if (item.workstation) {
							subject_parts.push(`Workstation: ${item.workstation}`);
						}
						if (item.operation) {
							subject_parts.push(`Operation: ${item.operation}`);
						}
						if (item.is_late && item.delay_reason) {
							subject_parts.push(`⚠️ ${item.delay_reason}`);
						}
						
						task.name = subject_parts.length > 0 
							? subject_parts.join(" | ") 
							: item.name;
					}
					return task;
				});
			};
		}
	}
};
