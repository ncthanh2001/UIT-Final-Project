# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class APSSchedulingRun(Document):
    """
    APS Scheduling Run Document Controller.

    Manages scheduling runs using the OR-Tools CP-SAT solver.
    """

    def validate(self):
        """Validate before saving."""
        if not self.run_date:
            self.run_date = now_datetime()

        if not self.executed_by:
            self.executed_by = frappe.session.user

    def before_insert(self):
        """Set defaults before insert."""
        self.run_status = "Pending"
        self.solver_status = "Not Started"

    @frappe.whitelist()
    def run_scheduling(self):
        """
        Execute the scheduling algorithm.

        Uses OR-Tools CP-SAT solver to optimize the production schedule.
        """
        if self.run_status == "Running":
            frappe.throw(_("Scheduling is already running"))

        # Update status to running
        self.run_status = "Running"
        self.solver_status = "Running"
        self.save(ignore_permissions=True)
        frappe.db.commit()

        try:
            # Import scheduling modules
            from uit_aps.scheduling.ortools.models import (
                SchedulingConfig,
                ObjectiveWeights,
            )
            from uit_aps.scheduling.data.erpnext_loader import ERPNextDataLoader
            from uit_aps.scheduling.ortools.scheduler import ORToolsScheduler
            from uit_aps.scheduling.data.exporters import SchedulingExporter

            # Build configuration from document fields
            weights = ObjectiveWeights(
                makespan_weight=self.makespan_weight or 1.0,
                tardiness_weight=self.tardiness_weight or 10.0
            )

            config = SchedulingConfig(
                time_limit_seconds=self.time_limit_seconds or 300,
                objective_weights=weights,
                min_gap_between_ops_mins=self.min_gap_between_ops or 10
            )

            # Load data from ERPNext
            loader = ERPNextDataLoader()
            problem = loader.load_from_production_plan(
                self.production_plan,
                config
            )

            if not problem.jobs:
                frappe.throw(_("No jobs found to schedule in production plan"))

            # Run the scheduler
            scheduler = ORToolsScheduler(config)
            scheduler.load_data(problem)
            scheduler.build_model()

            solution = scheduler.solve(self.time_limit_seconds or 300)

            # Export results
            exporter = SchedulingExporter(scheduling_run=self.name)
            stats = exporter.export_solution(
                solution,
                update_job_cards=True,
                create_results=True
            )

            # Update document with results
            self.run_status = "Completed" if solution.is_feasible else "Failed"
            self.solver_status = solution.status.value
            self.solve_time_seconds = solution.solve_time_secs
            self.gap_percentage = solution.gap_percentage

            self.total_job_cards = len(solution.operations)
            self.total_late_jobs = solution.jobs_late
            self.jobs_on_time = solution.jobs_on_time

            self.makespan_minutes = solution.makespan_mins
            self.total_tardiness_minutes = solution.total_tardiness_mins
            self.machine_utilization = solution.average_utilization

            # Add any export errors to notes
            if stats.get("errors"):
                self.notes = (self.notes or "") + "\n\nExport Errors:\n" + "\n".join(stats["errors"][:5])

            self.save(ignore_permissions=True)
            frappe.db.commit()

            return {
                "success": True,
                "status": solution.status.value,
                "message": _("Scheduling completed successfully"),
                "stats": {
                    "jobs_scheduled": len(solution.operations),
                    "jobs_on_time": solution.jobs_on_time,
                    "jobs_late": solution.jobs_late,
                    "makespan_minutes": solution.makespan_mins,
                    "solve_time_seconds": solution.solve_time_secs
                }
            }

        except Exception as e:
            # Handle errors
            self.run_status = "Failed"
            self.solver_status = "Error"
            self.notes = (self.notes or "") + f"\n\nError: {str(e)}"
            self.save(ignore_permissions=True)
            frappe.db.commit()

            frappe.log_error(
                f"Scheduling failed for {self.name}: {str(e)}",
                "APS Scheduling Error"
            )

            return {
                "success": False,
                "status": "Error",
                "message": str(e)
            }

    @frappe.whitelist()
    def get_gantt_data(self):
        """
        Get Gantt chart data for visualization.

        Returns:
            List of Gantt chart data items
        """
        from uit_aps.scheduling.api.scheduling_api import get_gantt_data
        return get_gantt_data(self.name)

    @frappe.whitelist()
    def get_machine_timeline(self):
        """
        Get machine timeline data for visualization.

        Returns:
            Dict mapping machine_id to list of scheduled operations
        """
        from uit_aps.scheduling.api.scheduling_api import get_machine_timeline
        return get_machine_timeline(self.name)


@frappe.whitelist()
def run_scheduling_for_plan(production_plan, time_limit_seconds=300):
    """
    Convenience method to create and run scheduling for a production plan.

    Args:
        production_plan: Name of APS Production Plan
        time_limit_seconds: Solver time limit

    Returns:
        Scheduling run result
    """
    # Create new scheduling run
    run = frappe.get_doc({
        "doctype": "APS Scheduling Run",
        "production_plan": production_plan,
        "scheduling_strategy": "Forward Scheduling",
        "scheduling_tier": "Tier 1 - OR-Tools",
        "time_limit_seconds": time_limit_seconds
    })
    run.insert(ignore_permissions=True)
    frappe.db.commit()

    # Run scheduling
    result = run.run_scheduling()

    return {
        "scheduling_run": run.name,
        "result": result
    }
