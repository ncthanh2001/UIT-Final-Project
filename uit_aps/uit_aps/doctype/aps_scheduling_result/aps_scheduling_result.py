# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.desk.reportview import get_filters_cond


class APSSchedulingResult(Document):
	def get_subject(self):
		"""Tao subject field cho Gantt chart"""
		subject_parts = []
		if self.job_card:
			subject_parts.append(f"Job Card: {self.job_card}")
		if self.workstation:
			subject_parts.append(f"Workstation: {self.workstation}")
		if self.operation:
			subject_parts.append(f"Operation: {self.operation}")
		if self.is_late and self.delay_reason:
			subject_parts.append(f"⚠️ {self.delay_reason}")
		
		return " | ".join(subject_parts) if subject_parts else self.name
	
	def get_color(self):
		"""Tra ve mau sac dua tren trang thai"""
		if self.is_late:
			return "#ef4444"  # Red for late jobs
		return "#22c55e"  # Green for on-time jobs


@frappe.whitelist()
def get_events(doctype, start, end, field_map=None, filters=None, fields=None):
	"""Get events for calendar and Gantt chart view"""
	events = []

	# Mau sac cho cac trang thai khac nhau
	event_color = {
		"Late": "#ef4444",  # Red for late jobs
		"On Time": "#22c55e",  # Green for on-time jobs
		"At Risk": "#facc15",  # Yellow for at-risk jobs
	}

	# Parse filters neu la string
	if isinstance(filters, str):
		filters = frappe.parse_json(filters) if filters else []

	conditions = get_filters_cond("APS Scheduling Result", filters, [])

	# Query de lay du lieu
	scheduling_results = frappe.db.sql(
		f"""
		SELECT 
			name,
			scheduling_run,
			job_card,
			workstation,
			operation,
			planned_start_time,
			planned_end_time,
			is_late,
			delay_reason,
			remarks
		FROM `tabAPS Scheduling Result`
		WHERE
			planned_start_time IS NOT NULL
			AND planned_end_time IS NOT NULL
			AND planned_start_time <= %(end)s
			AND planned_end_time >= %(start)s
			{conditions}
		ORDER BY planned_start_time
		""",
		values={"start": start, "end": end},
		as_dict=1,
	)

	for d in scheduling_results:
		# Xac dinh mau sac dua tren trang thai
		if d.is_late:
			color = event_color.get("Late", "#ef4444")
		else:
			# Co the them logic de xac dinh "At Risk" neu can
			color = event_color.get("On Time", "#22c55e")

		# Tao subject/title cho event
		subject_parts = []
		if d.job_card:
			subject_parts.append(f"Job Card: {d.job_card}")
		if d.workstation:
			subject_parts.append(f"Workstation: {d.workstation}")
		if d.operation:
			subject_parts.append(f"Operation: {d.operation}")
		if d.is_late and d.delay_reason:
			subject_parts.append(f"⚠️ {d.delay_reason}")

		subject = " | ".join(subject_parts) if subject_parts else d.name

		# Tra ve dung ten field theo field_map
		event_data = {
			"name": d.name,
			"subject": subject,
			"planned_start_time": d.planned_start_time,
			"planned_end_time": d.planned_end_time,
			"color": color,
			"allDay": False,
			"progress": 0,  # Co the tinh progress neu co du lieu
		}

		events.append(event_data)

	return events
