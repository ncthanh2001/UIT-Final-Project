frappe.views.calendar["APS Scheduling Result"] = {
	field_map: {
		start: "planned_start_time",
		end: "planned_end_time",
		id: "name",
		title: "job_card",
		color: "color",
		allDay: "allDay",
		progress: "progress",
	},
	gantt: {
		field_map: {
			start: "planned_start_time",
			end: "planned_end_time",
			id: "name",
			title: "job_card",
			color: "color",
			allDay: "allDay",
			progress: "progress",
		},
	},
	filters: [
		{
			fieldtype: "Link",
			fieldname: "scheduling_run",
			options: "APS Scheduling Run",
			label: __("Scheduling Run"),
		},
		{
			fieldtype: "Link",
			fieldname: "workstation",
			options: "Workstation",
			label: __("Workstation"),
		},
		{
			fieldtype: "Link",
			fieldname: "job_card",
			options: "Job Card",
			label: __("Job Card"),
		},
	],
	get_events_method: "uit_aps.doctype.aps_scheduling_result.aps_scheduling_result.get_events",
};
