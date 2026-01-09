// Copyright (c) 2025, thanhnc and contributors
// For license information, please see license.txt

frappe.ui.form.on("APS Scheduling Run", {
    refresh(frm) {
        // Add custom buttons based on status
        frm.add_custom_button_group();

        // Check tier status on load
        if (!frm.tier_status_checked) {
            frm.check_tier_status();
            frm.tier_status_checked = true;
        }

        // Add status indicator
        frm.update_status_indicator();
    },

    onload(frm) {
        // Initialize tier status
        frm.tier_status = {
            tier1: false,
            tier2: false,
            tier3: false
        };
    },

    scheduling_tier(frm) {
        // Update UI based on selected tier
        frm.update_tier_visibility();
    },

    llm_analysis_button(frm) {
        // Handle "Get AI Analysis" button click
        if (frm.doc.run_status !== "Completed" && frm.doc.run_status !== "Pending Approval" && frm.doc.run_status !== "Applied") {
            frappe.msgprint({
                title: __("Cannot Analyze"),
                message: __("Please run scheduling first. Analysis is only available after scheduling is completed."),
                indicator: "orange"
            });
            return;
        }

        // Get custom prompt from field
        let customPrompt = frm.doc.llm_analysis_prompt || "";

        frappe.call({
            method: "uit_aps.scheduling.llm.llm_api.get_scheduling_advice",
            args: {
                scheduling_run: frm.doc.name,
                language: frm.doc.llm_analysis_language || "vi",
                custom_prompt: customPrompt
            },
            freeze: true,
            freeze_message: __("Getting AI analysis from OpenAI..."),
            callback: function(r) {
                if (r.message && r.message.success) {
                    // Update fields with the analysis result
                    frm.set_value("llm_analysis_content", r.message.raw_response);
                    frm.set_value("llm_analysis_date", frappe.datetime.now_datetime());
                    frm.set_value("llm_analysis_model", r.message.model || "gpt-4o-mini");
                    frm.save();

                    frappe.show_alert({
                        message: __("AI analysis completed and saved!"),
                        indicator: "green"
                    });
                } else {
                    frappe.msgprint({
                        title: __("Analysis Failed"),
                        message: r.message ? r.message.error : __("Unknown error. Please check OpenAI API key in APS Chatgpt Settings."),
                        indicator: "red"
                    });
                }
            },
            error: function() {
                frappe.msgprint({
                    title: __("Error"),
                    message: __("Failed to connect to LLM service. Please check your OpenAI API key configuration."),
                    indicator: "red"
                });
            }
        });
    }
});

// Extend the form object with custom methods
frappe.ui.form.on("APS Scheduling Run", {
    // This runs after the standard refresh
});

// Custom form methods
$.extend(cur_frm, {
    add_custom_button_group: function() {
        let frm = this;

        // Clear existing custom buttons
        frm.clear_custom_buttons();

        // ============================================
        // APPROVAL: Apply Schedule to Job Cards
        // ============================================
        if (frm.doc.run_status === "Pending Approval") {
            frm.add_custom_button(__("Apply Schedule"), function() {
                frm.apply_scheduling_to_jobcards();
            }).addClass("btn-primary-dark");

            frm.add_custom_button(__("Review Results"), function() {
                frm.review_pending_results();
            });
        }

        // ============================================
        // TIER 1: OR-Tools Scheduling
        // ============================================
        if (frm.doc.run_status === "Pending" || frm.doc.run_status === "Failed") {
            frm.add_custom_button(__("Run OR-Tools Scheduling"), function() {
                frm.run_tier1_scheduling();
            }, __("Tier 1 - OR-Tools"));

            frm.add_custom_button(__("Run Hybrid Scheduling"), function() {
                frm.run_hybrid_scheduling();
            }, __("Tier 1 - OR-Tools"));
        }

        // ============================================
        // TIER 2: RL Agent
        // ============================================
        if (frm.doc.run_status === "Completed") {
            frm.add_custom_button(__("Get RL Recommendation"), function() {
                frm.get_rl_recommendation();
            }, __("Tier 2 - RL Agent"));

            frm.add_custom_button(__("Handle Disruption"), function() {
                frm.show_disruption_dialog();
            }, __("Tier 2 - RL Agent"));

            frm.add_custom_button(__("Train RL Agent"), function() {
                frm.show_training_dialog();
            }, __("Tier 2 - RL Agent"));
        }

        // ============================================
        // TIER 3: GNN Analysis
        // ============================================
        if (frm.doc.run_status === "Completed" || frm.doc.run_status === "Pending") {
            frm.add_custom_button(__("Predict Bottlenecks"), function() {
                frm.predict_bottlenecks();
            }, __("Tier 3 - GNN Analysis"));

            frm.add_custom_button(__("Predict Delays"), function() {
                frm.predict_delays();
            }, __("Tier 3 - GNN Analysis"));

            frm.add_custom_button(__("Get Recommendations"), function() {
                frm.get_gnn_recommendations();
            }, __("Tier 3 - GNN Analysis"));

            frm.add_custom_button(__("Critical Insights"), function() {
                frm.get_critical_insights();
            }, __("Tier 3 - GNN Analysis"));
        }

        // ============================================
        // PHASE 4: Evaluation & Deployment
        // ============================================
        if (frm.doc.run_status === "Completed") {
            frm.add_custom_button(__("Evaluate vs Heuristics"), function() {
                frm.evaluate_against_heuristics();
            }, __("Phase 4 - Evaluation"));

            frm.add_custom_button(__("Compare with OR-Tools"), function() {
                frm.compare_with_ortools();
            }, __("Phase 4 - Evaluation"));

            frm.add_custom_button(__("Deployment Status"), function() {
                frm.show_deployment_status();
            }, __("Phase 4 - Deployment"));

            frm.add_custom_button(__("Monitoring Summary"), function() {
                frm.show_monitoring_summary();
            }, __("Phase 4 - Deployment"));
        }

        // ============================================
        // Utility Buttons
        // ============================================
        frm.add_custom_button(__("Check Tier Status"), function() {
            frm.check_tier_status(true);
        }, __("Utilities"));

        if (frm.doc.run_status === "Completed" || frm.doc.run_status === "Pending Approval" || frm.doc.run_status === "Applied") {
            frm.add_custom_button(__("View Results"), function() {
                frm.view_scheduling_results();
            }, __("Utilities"));

            frm.add_custom_button(__("Export to Gantt"), function() {
                frm.export_to_gantt();
            }, __("Utilities"));

            frm.add_custom_button(__("View Optimization Analysis"), function() {
                frm.show_optimization_analysis();
            }, __("Utilities"));
        }
    },

    // ============================================
    // APPROVAL WORKFLOW: Apply Schedule Methods
    // ============================================
    apply_scheduling_to_jobcards: function() {
        let frm = this;

        frappe.confirm(
            __("Apply all scheduling recommendations to Job Cards? This will update expected start/end dates on the Job Cards."),
            function() {
                frappe.call({
                    method: "uit_aps.scheduling.api.scheduling_api.apply_scheduling_results",
                    args: {
                        scheduling_run: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __("Applying scheduling recommendations to Job Cards..."),
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({
                                message: __("Successfully applied {0} scheduling recommendations to Job Cards!", [r.message.applied_count]),
                                indicator: "green"
                            });
                            frm.reload_doc();
                        } else {
                            frappe.msgprint({
                                title: __("Apply Failed"),
                                message: r.message ? r.message.message : __("Failed to apply recommendations"),
                                indicator: "red"
                            });
                        }
                    },
                    error: function() {
                        frappe.msgprint({
                            title: __("Error"),
                            message: __("Failed to apply scheduling recommendations"),
                            indicator: "red"
                        });
                    }
                });
            }
        );
    },

    review_pending_results: function() {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.api.scheduling_api.get_pending_results",
            args: {
                scheduling_run: frm.doc.name
            },
            freeze: true,
            freeze_message: __("Loading scheduling recommendations..."),
            callback: function(r) {
                if (r.message && r.message.success) {
                    frm.show_pending_results_dialog(r.message.results, r.message.summary);
                } else {
                    frappe.msgprint({
                        title: __("Error"),
                        message: r.message ? r.message.message : __("Failed to load results"),
                        indicator: "red"
                    });
                }
            }
        });
    },

    show_pending_results_dialog: function(results, summary) {
        let frm = this;

        let html = `
            <div class="pending-results-review">
                <div class="alert alert-info mb-3">
                    <div class="row">
                        <div class="col-sm-3">
                            <strong>${summary.total || 0}</strong>
                            <br><small>${__("Total Recommendations")}</small>
                        </div>
                        <div class="col-sm-3">
                            <strong>${summary.pending || 0}</strong>
                            <br><small>${__("Pending")}</small>
                        </div>
                        <div class="col-sm-3">
                            <strong>${summary.applied || 0}</strong>
                            <br><small>${__("Already Applied")}</small>
                        </div>
                        <div class="col-sm-3">
                            <strong>${summary.late_jobs || 0}</strong>
                            <br><small class="text-danger">${__("Late Jobs")}</small>
                        </div>
                    </div>
                </div>

                <table class="table table-sm table-bordered table-hover">
                    <thead>
                        <tr>
                            <th>${__("Job Card")}</th>
                            <th>${__("Operation")}</th>
                            <th>${__("Workstation")}</th>
                            <th>${__("Planned Start")}</th>
                            <th>${__("Planned End")}</th>
                            <th>${__("Status")}</th>
                        </tr>
                    </thead>
                    <tbody>`;

        if (results && results.length > 0) {
            results.forEach(result => {
                let statusBadge = result.is_applied
                    ? '<span class="badge badge-success">Applied</span>'
                    : '<span class="badge badge-warning">Pending</span>';

                let lateBadge = result.is_late
                    ? ' <span class="badge badge-danger">Late</span>'
                    : '';

                let startTime = result.planned_start_time
                    ? frappe.datetime.str_to_user(result.planned_start_time)
                    : '-';
                let endTime = result.planned_end_time
                    ? frappe.datetime.str_to_user(result.planned_end_time)
                    : '-';

                html += `
                    <tr>
                        <td><a href="/app/job-card/${result.job_card}">${result.job_card}</a></td>
                        <td>${result.operation || '-'}</td>
                        <td>${result.workstation || '-'}</td>
                        <td>${startTime}</td>
                        <td>${endTime}</td>
                        <td>${statusBadge}${lateBadge}</td>
                    </tr>`;
            });
        } else {
            html += `<tr><td colspan="6" class="text-center">${__("No results found")}</td></tr>`;
        }

        html += `
                    </tbody>
                </table>
            </div>`;

        let d = new frappe.ui.Dialog({
            title: __("Review Scheduling Recommendations"),
            size: "extra-large",
            fields: [
                {
                    fieldtype: "HTML",
                    fieldname: "results_html",
                    options: html
                }
            ],
            primary_action_label: __("Apply All Recommendations"),
            primary_action: function() {
                d.hide();
                frm.apply_scheduling_to_jobcards();
            },
            secondary_action_label: __("View in List"),
            secondary_action: function() {
                d.hide();
                frappe.set_route("List", "APS Scheduling Result", {
                    scheduling_run: frm.doc.name
                });
            }
        });
        d.show();
    },

    // ============================================
    // TIER 1: OR-Tools Methods
    // ============================================
    run_tier1_scheduling: function() {
        let frm = this;

        // Check if form has unsaved changes
        if (frm.is_dirty()) {
            frappe.msgprint({
                title: __("Unsaved Changes"),
                message: __("Please save the document first before running scheduling."),
                indicator: "orange"
            });
            return;
        }

        frappe.confirm(
            __("Run OR-Tools scheduling for this production plan?"),
            function() {
                // API will handle status updates - no need to save here
                frappe.call({
                    method: "uit_aps.scheduling.api.scheduling_api.run_ortools_scheduling",
                    args: {
                        // Pass existing scheduling_run name - API will use this record
                        scheduling_run: frm.doc.name,
                        scheduling_strategy: frm.doc.scheduling_strategy || "Forward Scheduling",
                        time_limit_seconds: frm.doc.time_limit_seconds || 300,
                        makespan_weight: frm.doc.makespan_weight || 1.0,
                        tardiness_weight: frm.doc.tardiness_weight || 10.0
                    },
                    freeze: true,
                    freeze_message: __("Running OR-Tools CP-SAT solver..."),
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({
                                message: __("Scheduling completed successfully!"),
                                indicator: "green"
                            });
                            // Reload form to get updated values from server
                            frm.reload_doc();
                        } else {
                            frappe.msgprint({
                                title: __("Scheduling Failed"),
                                message: r.message ? r.message.message : __("Unknown error"),
                                indicator: "red"
                            });
                            // Reload to get current status
                            frm.reload_doc();
                        }
                    },
                    error: function(r) {
                        frappe.msgprint({
                            title: __("Error"),
                            message: __("Failed to run scheduling"),
                            indicator: "red"
                        });
                        frm.reload_doc();
                    }
                });
            }
        );
    },

    run_hybrid_scheduling: function() {
        let frm = this;

        // Check if form has unsaved changes
        if (frm.is_dirty()) {
            frappe.msgprint({
                title: __("Unsaved Changes"),
                message: __("Please save the document first before running scheduling."),
                indicator: "orange"
            });
            return;
        }

        let d = new frappe.ui.Dialog({
            title: __("Run Hybrid Scheduling"),
            fields: [
                {
                    label: __("Enable RL Adjustments"),
                    fieldname: "enable_rl",
                    fieldtype: "Check",
                    default: 1
                },
                {
                    label: __("RL Agent Type"),
                    fieldname: "rl_agent_type",
                    fieldtype: "Select",
                    options: "ppo\nsac",
                    default: "ppo",
                    depends_on: "eval:doc.enable_rl"
                },
                {
                    label: __("Time Limit (seconds)"),
                    fieldname: "time_limit",
                    fieldtype: "Int",
                    default: frm.doc.time_limit_seconds || 300
                }
            ],
            primary_action_label: __("Run"),
            primary_action: function(values) {
                d.hide();
                // API will handle status updates - no need to save here
                frappe.call({
                    method: "uit_aps.scheduling.hybrid_scheduler.run_hybrid_scheduling",
                    args: {
                        // Pass existing scheduling_run name - API will use this record
                        scheduling_run: frm.doc.name,
                        enable_rl: values.enable_rl,
                        rl_agent_type: values.rl_agent_type,
                        time_limit_seconds: values.time_limit
                    },
                    freeze: true,
                    freeze_message: __("Running hybrid scheduling (Tier 1 + Tier 2)..."),
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({
                                message: __("Hybrid scheduling completed!"),
                                indicator: "green"
                            });
                            // Reload form to get updated values from server
                            frm.reload_doc();
                        } else {
                            frappe.msgprint({
                                title: __("Scheduling Failed"),
                                message: r.message ? r.message.message : __("Unknown error"),
                                indicator: "red"
                            });
                            frm.reload_doc();
                        }
                    },
                    error: function(r) {
                        frappe.msgprint({
                            title: __("Error"),
                            message: __("Failed to run hybrid scheduling"),
                            indicator: "red"
                        });
                        frm.reload_doc();
                    }
                });
            }
        });
        d.show();
    },

    // Note: update_from_scheduling_result is no longer used - API updates directly
    update_from_scheduling_result: function(result) {
        // Deprecated - API now updates the record directly
        // Keeping for backwards compatibility
        let frm = this;
        frm.reload_doc();
    },

    update_from_hybrid_result: function(result) {
        let frm = this;
        let metrics = result.metrics || {};
        frm.set_value("run_status", "Completed");
        frm.set_value("solver_status", metrics.solver_status || "Optimal");
        frm.set_value("total_job_cards", result.tier1_result?.total_operations || 0);
        frm.set_value("jobs_on_time", metrics.jobs_on_time || 0);
        frm.set_value("total_late_jobs", metrics.jobs_late || 0);
        frm.set_value("makespan_minutes", metrics.makespan_mins || 0);
        frm.set_value("notes", "Tier 2 Status: " + (result.tier2_status || "N/A"));
        frm.save();
    },

    // ============================================
    // TIER 2: RL Agent Methods
    // ============================================
    get_rl_recommendation: function() {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.rl.realtime_api.get_realtime_adjustment",
            args: {
                scheduling_run: frm.doc.name,
                agent_type: "ppo"
            },
            freeze: true,
            freeze_message: __("Getting RL recommendation..."),
            callback: function(r) {
                if (r.message && r.message.success) {
                    frm.show_rl_recommendation_dialog(r.message);
                } else {
                    frappe.msgprint({
                        title: __("No Recommendation"),
                        message: r.message ? r.message.message : __("No action needed"),
                        indicator: "blue"
                    });
                }
            }
        });
    },

    show_rl_recommendation_dialog: function(result) {
        let frm = this;
        let rec = result.recommendation;

        let html = `
            <div class="rl-recommendation">
                <h4>${__("Recommended Action")}</h4>
                <table class="table table-bordered">
                    <tr>
                        <td><strong>${__("Action Type")}</strong></td>
                        <td><span class="badge badge-primary">${rec.action_type}</span></td>
                    </tr>
                    <tr>
                        <td><strong>${__("Target Operation")}</strong></td>
                        <td>${rec.target_operation || "-"}</td>
                    </tr>
                    <tr>
                        <td><strong>${__("Target Machine")}</strong></td>
                        <td>${rec.target_machine || "-"}</td>
                    </tr>
                    <tr>
                        <td><strong>${__("Confidence")}</strong></td>
                        <td>
                            <div class="progress" style="margin: 0;">
                                <div class="progress-bar" style="width: ${(rec.confidence * 100)}%">
                                    ${(rec.confidence * 100).toFixed(0)}%
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td><strong>${__("Reason")}</strong></td>
                        <td>${rec.reason || "-"}</td>
                    </tr>
                </table>
        `;

        if (result.alternatives && result.alternatives.length > 0) {
            html += `<h5>${__("Alternatives")}</h5><ul>`;
            result.alternatives.forEach(alt => {
                html += `<li>${alt.action_type} (${(alt.confidence * 100).toFixed(0)}% confidence)</li>`;
            });
            html += `</ul>`;
        }

        html += `</div>`;

        let d = new frappe.ui.Dialog({
            title: __("RL Recommendation"),
            fields: [
                {
                    fieldtype: "HTML",
                    fieldname: "recommendation_html",
                    options: html
                }
            ],
            primary_action_label: __("Apply Recommendation"),
            primary_action: function() {
                d.hide();
                frm.apply_rl_recommendation(rec);
            },
            secondary_action_label: __("Dismiss")
        });
        d.show();
    },

    apply_rl_recommendation: function(rec) {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.rl.realtime_api.apply_rl_adjustment",
            args: {
                scheduling_run: frm.doc.name,
                action_type: rec.action_type_id,
                target_operation: rec.target_operation,
                target_machine: rec.target_machine
            },
            freeze: true,
            freeze_message: __("Applying adjustment..."),
            callback: function(r) {
                if (r.message && r.message.success) {
                    frappe.show_alert({
                        message: r.message.message,
                        indicator: "green"
                    });
                    frm.reload_doc();
                } else {
                    frappe.msgprint({
                        title: __("Failed"),
                        message: r.message ? r.message.message : __("Failed to apply adjustment"),
                        indicator: "red"
                    });
                }
            }
        });
    },

    show_disruption_dialog: function() {
        let frm = this;

        let d = new frappe.ui.Dialog({
            title: __("Report Disruption"),
            fields: [
                {
                    label: __("Disruption Type"),
                    fieldname: "disruption_type",
                    fieldtype: "Select",
                    options: "machine_breakdown\nrush_order\nprocessing_delay\nmaterial_shortage\nworker_absence\nquality_issue",
                    reqd: 1
                },
                {
                    label: __("Affected Resource"),
                    fieldname: "affected_resource",
                    fieldtype: "Link",
                    options: "Workstation",
                    reqd: 1
                },
                {
                    label: __("Expected Duration (minutes)"),
                    fieldname: "duration_minutes",
                    fieldtype: "Int",
                    default: 60
                },
                {
                    label: __("Notes"),
                    fieldname: "notes",
                    fieldtype: "Small Text"
                }
            ],
            primary_action_label: __("Report & Get Recommendations"),
            primary_action: function(values) {
                d.hide();
                frm.handle_disruption(values);
            }
        });
        d.show();
    },

    handle_disruption: function(values) {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.rl.realtime_api.handle_disruption",
            args: {
                disruption_type: values.disruption_type,
                affected_resource: values.affected_resource,
                scheduling_run: frm.doc.name,
                duration_minutes: values.duration_minutes
            },
            freeze: true,
            freeze_message: __("Analyzing disruption and generating recommendations..."),
            callback: function(r) {
                if (r.message) {
                    frm.show_disruption_recommendations(r.message);
                }
            }
        });
    },

    show_disruption_recommendations: function(result) {
        let frm = this;

        let html = `
            <div class="disruption-result">
                <div class="alert alert-warning">
                    <strong>${__("Disruption Recorded")}</strong><br>
                    ${__("Type")}: ${result.disruption?.type || "-"}<br>
                    ${__("Affected")}: ${result.disruption?.affected_resource || "-"}<br>
                    ${__("Duration")}: ${result.disruption?.duration_minutes || 0} ${__("minutes")}
                </div>

                <h5>${__("Affected Operations")}: ${result.affected_operations?.length || 0}</h5>
        `;

        if (result.recommendations && result.recommendations.length > 0) {
            html += `<h5>${__("Recommendations")}</h5>
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>${__("Action")}</th>
                            <th>${__("Target")}</th>
                            <th>${__("Confidence")}</th>
                        </tr>
                    </thead>
                    <tbody>`;
            result.recommendations.forEach(rec => {
                html += `
                    <tr>
                        <td>${rec.action_type}</td>
                        <td>${rec.target_operation || "-"}</td>
                        <td>${(rec.confidence * 100).toFixed(0)}%</td>
                    </tr>`;
            });
            html += `</tbody></table>`;
        }

        html += `</div>`;

        frappe.msgprint({
            title: __("Disruption Analysis"),
            message: html,
            indicator: "orange",
            wide: true
        });
    },

    show_training_dialog: function() {
        let frm = this;

        let d = new frappe.ui.Dialog({
            title: __("Train RL Agent"),
            fields: [
                {
                    label: __("Agent Type"),
                    fieldname: "agent_type",
                    fieldtype: "Select",
                    options: "ppo\nsac",
                    default: "ppo",
                    reqd: 1,
                    description: __("PPO: Stable, good for most cases. SAC: Better exploration.")
                },
                {
                    label: __("Training Episodes"),
                    fieldname: "max_episodes",
                    fieldtype: "Int",
                    default: 100,
                    description: __("More episodes = better learning but longer training time")
                },
                {
                    label: __("Learning Rate"),
                    fieldname: "learning_rate",
                    fieldtype: "Float",
                    default: 0.0003,
                    description: __("Higher = faster learning but less stable")
                },
                {
                    label: __("Discount Factor (Gamma)"),
                    fieldname: "gamma",
                    fieldtype: "Float",
                    default: 0.99,
                    description: __("How much to value future rewards (0.9-0.999)")
                },
                {
                    fieldtype: "Section Break",
                    label: __("Training History")
                },
                {
                    fieldname: "training_history_html",
                    fieldtype: "HTML"
                }
            ],
            primary_action_label: __("Start Training"),
            primary_action: function(values) {
                d.hide();
                frm.start_training_with_progress(values);
            },
            secondary_action_label: __("View History"),
            secondary_action: function() {
                frm.show_training_history();
            }
        });

        // Load training history in dialog
        frappe.call({
            method: "uit_aps.scheduling.rl.training_api.get_training_history",
            args: {
                scheduling_run: frm.doc.name,
                limit: 5
            },
            callback: function(r) {
                if (r.message && r.message.success && r.message.logs.length > 0) {
                    let html = `<table class="table table-sm table-bordered" style="font-size: 11px;">
                        <thead><tr>
                            <th>${__("Agent")}</th>
                            <th>${__("Episodes")}</th>
                            <th>${__("Best Reward")}</th>
                            <th>${__("Status")}</th>
                        </tr></thead><tbody>`;

                    r.message.logs.forEach(log => {
                        let statusClass = {
                            "Completed": "success",
                            "Running": "primary",
                            "Failed": "danger",
                            "Cancelled": "warning"
                        }[log.training_status] || "secondary";

                        html += `<tr>
                            <td>${log.agent_type.toUpperCase()}</td>
                            <td>${log.current_episode}/${log.max_episodes}</td>
                            <td>${(log.best_reward || 0).toFixed(2)}</td>
                            <td><span class="badge badge-${statusClass}">${log.training_status}</span></td>
                        </tr>`;
                    });

                    html += `</tbody></table>`;
                    d.fields_dict.training_history_html.$wrapper.html(html);
                } else {
                    d.fields_dict.training_history_html.$wrapper.html(
                        `<p class="text-muted">${__("No training history for this scheduling run.")}</p>`
                    );
                }
            }
        });

        d.show();
    },

    start_training_with_progress: function(values) {
        let frm = this;

        // Start training in background
        frappe.call({
            method: "uit_aps.scheduling.rl.training_api.start_training",
            args: {
                scheduling_run: frm.doc.name,
                agent_type: values.agent_type,
                max_episodes: values.max_episodes,
                learning_rate: values.learning_rate,
                gamma: values.gamma,
                run_in_background: true
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    frappe.show_alert({
                        message: __("Training started in background"),
                        indicator: "blue"
                    });

                    // Show progress dialog
                    frm.show_training_progress_dialog(values.agent_type);
                } else {
                    frappe.msgprint({
                        title: __("Training Failed to Start"),
                        message: r.message ? r.message.error : __("Unknown error"),
                        indicator: "red"
                    });
                }
            }
        });
    },

    show_training_progress_dialog: function(agent_type) {
        let frm = this;

        let progress_dialog = new frappe.ui.Dialog({
            title: __("Training Progress - {0}", [agent_type.toUpperCase()]),
            size: "large",
            fields: [
                {
                    fieldname: "progress_html",
                    fieldtype: "HTML"
                }
            ]
        });

        // Function to update progress
        let update_progress = function() {
            frappe.call({
                method: "uit_aps.scheduling.rl.training_api.get_training_history",
                args: {
                    scheduling_run: frm.doc.name,
                    agent_type: agent_type,
                    limit: 1
                },
                callback: function(r) {
                    if (r.message && r.message.success && r.message.logs.length > 0) {
                        let log = r.message.logs[0];
                        let progress = log.progress_percentage || 0;
                        let statusClass = log.training_status === "Running" ? "primary" :
                                         log.training_status === "Completed" ? "success" : "danger";

                        let html = `
                            <div class="training-progress-view">
                                <div class="row mb-3">
                                    <div class="col-sm-6">
                                        <h5>${__("Status")}:
                                            <span class="badge badge-${statusClass}">${log.training_status}</span>
                                        </h5>
                                    </div>
                                    <div class="col-sm-6 text-right">
                                        <h5>${__("Episode")}: ${log.current_episode || 0} / ${log.max_episodes || 0}</h5>
                                    </div>
                                </div>

                                <div class="progress mb-3" style="height: 30px;">
                                    <div class="progress-bar progress-bar-striped ${log.training_status === 'Running' ? 'progress-bar-animated' : ''}"
                                         role="progressbar"
                                         style="width: ${progress}%; background-color: var(--${statusClass === 'primary' ? 'blue' : statusClass === 'success' ? 'green' : 'red'});"
                                         aria-valuenow="${progress}"
                                         aria-valuemin="0"
                                         aria-valuemax="100">
                                        ${progress.toFixed(1)}%
                                    </div>
                                </div>

                                <div class="row mb-3">
                                    <div class="col-sm-3">
                                        <div class="stat-card text-center p-2 border rounded">
                                            <h3 class="text-success">${(log.best_reward || 0).toFixed(2)}</h3>
                                            <small>${__("Best Reward")}</small>
                                        </div>
                                    </div>
                                    <div class="col-sm-3">
                                        <div class="stat-card text-center p-2 border rounded">
                                            <h3 class="text-info">${(log.avg_reward_last_100 || 0).toFixed(2)}</h3>
                                            <small>${__("Avg Reward (100)")}</small>
                                        </div>
                                    </div>
                                    <div class="col-sm-3">
                                        <div class="stat-card text-center p-2 border rounded">
                                            <h3 class="text-primary">${log.best_makespan ? log.best_makespan.toFixed(0) + ' min' : '-'}</h3>
                                            <small>${__("Best Makespan")}</small>
                                        </div>
                                    </div>
                                    <div class="col-sm-3">
                                        <div class="stat-card text-center p-2 border rounded">
                                            <h3 class="text-warning">${log.best_tardiness ? log.best_tardiness.toFixed(0) + ' min' : '-'}</h3>
                                            <small>${__("Best Tardiness")}</small>
                                        </div>
                                    </div>
                                </div>

                                <div class="row">
                                    <div class="col-sm-6">
                                        <p><strong>${__("Speed")}:</strong> ${(log.episodes_per_second || 0).toFixed(2)} eps/sec</p>
                                        <p><strong>${__("Est. Remaining")}:</strong> ${log.estimated_time_remaining || '-'}</p>
                                    </div>
                                    <div class="col-sm-6">
                                        <p><strong>${__("Total Steps")}:</strong> ${log.total_steps || 0}</p>
                                        <p><strong>${__("Started")}:</strong> ${log.started_at || '-'}</p>
                                    </div>
                                </div>

                                ${log.training_status === "Completed" ? `
                                    <div class="alert alert-success mt-3">
                                        <strong>${__("Training Completed!")}</strong>
                                        ${__("The model has been saved and is ready for use.")}
                                        <br>
                                        <a href="/app/aps-rl-training-log/${log.name}" class="btn btn-sm btn-success mt-2">
                                            ${__("View Full Training Log")}
                                        </a>
                                    </div>
                                ` : ''}

                                ${log.training_status === "Failed" ? `
                                    <div class="alert alert-danger mt-3">
                                        <strong>${__("Training Failed!")}</strong>
                                        ${__("Please check the error log for details.")}
                                    </div>
                                ` : ''}
                            </div>
                        `;

                        progress_dialog.fields_dict.progress_html.$wrapper.html(html);

                        // Stop polling if training is complete
                        if (log.training_status !== "Running") {
                            if (frm._training_poll_interval) {
                                clearInterval(frm._training_poll_interval);
                                frm._training_poll_interval = null;
                            }
                        }
                    } else {
                        progress_dialog.fields_dict.progress_html.$wrapper.html(
                            `<p class="text-muted">${__("Waiting for training to start...")}</p>`
                        );
                    }
                }
            });
        };

        // Initial update
        update_progress();

        // Poll every 3 seconds
        frm._training_poll_interval = setInterval(update_progress, 3000);

        // Clear interval when dialog closes
        progress_dialog.onhide = function() {
            if (frm._training_poll_interval) {
                clearInterval(frm._training_poll_interval);
                frm._training_poll_interval = null;
            }
        };

        progress_dialog.show();
    },

    show_training_history: function() {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.rl.training_api.get_training_history",
            args: {
                scheduling_run: frm.doc.name,
                limit: 20
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    let logs = r.message.logs;

                    if (logs.length === 0) {
                        frappe.msgprint({
                            title: __("Training History"),
                            message: __("No training history found for this scheduling run."),
                            indicator: "blue"
                        });
                        return;
                    }

                    let html = `
                        <div class="training-history">
                            <table class="table table-bordered table-hover">
                                <thead>
                                    <tr>
                                        <th>${__("Log")}</th>
                                        <th>${__("Agent")}</th>
                                        <th>${__("Episodes")}</th>
                                        <th>${__("Best Reward")}</th>
                                        <th>${__("Makespan")}</th>
                                        <th>${__("Duration")}</th>
                                        <th>${__("Status")}</th>
                                    </tr>
                                </thead>
                                <tbody>`;

                    logs.forEach(log => {
                        let statusClass = {
                            "Completed": "success",
                            "Running": "primary",
                            "Failed": "danger",
                            "Cancelled": "warning",
                            "Pending": "secondary"
                        }[log.training_status] || "secondary";

                        let duration = log.total_duration_seconds ?
                            (log.total_duration_seconds > 60 ?
                                (log.total_duration_seconds / 60).toFixed(1) + ' min' :
                                log.total_duration_seconds.toFixed(0) + ' sec') : '-';

                        html += `
                            <tr style="cursor: pointer;" onclick="frappe.set_route('Form', 'APS RL Training Log', '${log.name}')">
                                <td><a href="/app/aps-rl-training-log/${log.name}">${log.name}</a></td>
                                <td><strong>${log.agent_type.toUpperCase()}</strong></td>
                                <td>${log.current_episode || 0} / ${log.max_episodes || 0}</td>
                                <td>${(log.best_reward || 0).toFixed(2)}</td>
                                <td>${log.best_makespan ? log.best_makespan.toFixed(0) + ' min' : '-'}</td>
                                <td>${duration}</td>
                                <td><span class="badge badge-${statusClass}">${log.training_status}</span></td>
                            </tr>`;
                    });

                    html += `
                                </tbody>
                            </table>
                        </div>`;

                    frappe.msgprint({
                        title: __("Training History"),
                        message: html,
                        indicator: "blue",
                        wide: true
                    });
                }
            }
        });
    },

    train_rl_agent: function(values) {
        // Legacy function - redirect to new training with progress
        this.start_training_with_progress(values);
    },

    // ============================================
    // TIER 3: GNN Analysis Methods
    // ============================================
    predict_bottlenecks: function() {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.gnn.gnn_api.predict_bottlenecks",
            args: {
                scheduling_run: frm.doc.name,
                threshold: 0.7
            },
            freeze: true,
            freeze_message: __("Analyzing bottlenecks with GNN..."),
            callback: function(r) {
                if (r.message) {
                    frm.show_bottleneck_results(r.message);
                }
            }
        });
    },

    show_bottleneck_results: function(result) {
        let html = `
            <div class="bottleneck-results">
                <div class="row">
                    <div class="col-sm-6">
                        <div class="stat-box">
                            <h3>${result.summary?.num_bottlenecks || 0}</h3>
                            <p>${__("Bottlenecks Detected")}</p>
                        </div>
                    </div>
                    <div class="col-sm-6">
                        <div class="stat-box">
                            <h3>${((result.summary?.avg_probability || 0) * 100).toFixed(0)}%</h3>
                            <p>${__("Avg Probability")}</p>
                        </div>
                    </div>
                </div>
        `;

        if (result.bottlenecks && result.bottlenecks.length > 0) {
            html += `
                <h5 class="mt-3">${__("Bottleneck Machines")}</h5>
                <table class="table table-sm table-bordered">
                    <thead>
                        <tr>
                            <th>${__("Machine")}</th>
                            <th>${__("Probability")}</th>
                            <th>${__("Utilization")}</th>
                        </tr>
                    </thead>
                    <tbody>`;
            result.bottlenecks.forEach(b => {
                let prob = (b.bottleneck_probability * 100).toFixed(0);
                let color = prob >= 85 ? "danger" : prob >= 70 ? "warning" : "info";
                html += `
                    <tr>
                        <td>${b.machine_id}</td>
                        <td><span class="badge badge-${color}">${prob}%</span></td>
                        <td>${((b.current_utilization || 0) * 100).toFixed(0)}%</td>
                    </tr>`;
            });
            html += `</tbody></table>`;
        } else {
            html += `<div class="alert alert-success mt-3">${__("No bottlenecks detected!")}</div>`;
        }

        html += `</div>`;

        frappe.msgprint({
            title: __("Bottleneck Prediction (GNN)"),
            message: html,
            indicator: result.bottlenecks?.length > 0 ? "orange" : "green",
            wide: true
        });
    },

    predict_delays: function() {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.gnn.gnn_api.predict_delays",
            args: {
                scheduling_run: frm.doc.name,
                delay_threshold: 0.5
            },
            freeze: true,
            freeze_message: __("Analyzing potential delays with GNN..."),
            callback: function(r) {
                if (r.message) {
                    frm.show_delay_results(r.message);
                }
            }
        });
    },

    show_delay_results: function(result) {
        let summary = result.summary || {};

        let html = `
            <div class="delay-results">
                <div class="row">
                    <div class="col-sm-4">
                        <div class="stat-box">
                            <h3>${summary.num_high_risk || 0}</h3>
                            <p>${__("High Risk Operations")}</p>
                        </div>
                    </div>
                    <div class="col-sm-4">
                        <div class="stat-box">
                            <h3>${summary.num_cascade_risks || 0}</h3>
                            <p>${__("Cascade Risks")}</p>
                        </div>
                    </div>
                    <div class="col-sm-4">
                        <div class="stat-box">
                            <h3>${(summary.expected_total_delay_minutes || 0).toFixed(0)} min</h3>
                            <p>${__("Expected Total Delay")}</p>
                        </div>
                    </div>
                </div>
        `;

        if (result.high_risk && result.high_risk.length > 0) {
            html += `
                <h5 class="mt-3">${__("High Risk Operations")}</h5>
                <table class="table table-sm table-bordered">
                    <thead>
                        <tr>
                            <th>${__("Operation")}</th>
                            <th>${__("Job")}</th>
                            <th>${__("Delay Prob")}</th>
                            <th>${__("Expected Delay")}</th>
                        </tr>
                    </thead>
                    <tbody>`;
            result.high_risk.slice(0, 10).forEach(op => {
                html += `
                    <tr>
                        <td>${op.operation_id}</td>
                        <td>${op.job_id || "-"}</td>
                        <td>${(op.delay_probability * 100).toFixed(0)}%</td>
                        <td>${(op.expected_delay_minutes || 0).toFixed(0)} min</td>
                    </tr>`;
            });
            html += `</tbody></table>`;
        }

        html += `</div>`;

        frappe.msgprint({
            title: __("Delay Prediction (GNN)"),
            message: html,
            indicator: summary.num_high_risk > 0 ? "orange" : "green",
            wide: true
        });
    },

    get_gnn_recommendations: function() {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.gnn.gnn_api.get_recommendations",
            args: {
                scheduling_run: frm.doc.name,
                max_recommendations: 10
            },
            freeze: true,
            freeze_message: __("Generating strategic recommendations..."),
            callback: function(r) {
                if (r.message) {
                    frm.show_gnn_recommendations(r.message);
                }
            }
        });
    },

    show_gnn_recommendations: function(result) {
        let html = `<div class="gnn-recommendations">`;

        if (result.recommendations && result.recommendations.length > 0) {
            result.recommendations.forEach((rec, idx) => {
                let priorityClass = {
                    "CRITICAL": "danger",
                    "HIGH": "warning",
                    "MEDIUM": "info",
                    "LOW": "secondary"
                }[rec.priority] || "secondary";

                html += `
                    <div class="card mb-2">
                        <div class="card-header">
                            <span class="badge badge-${priorityClass}">${rec.priority}</span>
                            <strong>${rec.title}</strong>
                        </div>
                        <div class="card-body">
                            <p>${rec.description}</p>
                            <div class="row">
                                <div class="col-sm-4">
                                    <small><strong>${__("Impact")}:</strong> ${rec.impact}</small>
                                </div>
                                <div class="col-sm-4">
                                    <small><strong>${__("Effort")}:</strong> ${rec.implementation_effort}</small>
                                </div>
                                <div class="col-sm-4">
                                    <small><strong>${__("Confidence")}:</strong> ${(rec.confidence * 100).toFixed(0)}%</small>
                                </div>
                            </div>
                        </div>
                    </div>`;
            });
        } else {
            html += `<div class="alert alert-info">${__("No recommendations at this time.")}</div>`;
        }

        html += `
            <div class="mt-3">
                <strong>${__("Summary")}:</strong>
                <ul>
                    <li>${__("Total Recommendations")}: ${result.summary?.total || 0}</li>
                    <li>${__("Estimated Improvement")}: ${(result.summary?.total_estimated_improvement || 0).toFixed(0)}%</li>
                </ul>
            </div>
        </div>`;

        frappe.msgprint({
            title: __("Strategic Recommendations (GNN)"),
            message: html,
            indicator: "blue",
            wide: true
        });
    },

    get_critical_insights: function() {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.gnn.gnn_api.get_critical_insights",
            args: {
                scheduling_run: frm.doc.name
            },
            freeze: true,
            freeze_message: __("Analyzing critical insights..."),
            callback: function(r) {
                if (r.message) {
                    frm.show_critical_insights(r.message);
                }
            }
        });
    },

    show_critical_insights: function(result) {
        let summary = result.summary || {};

        let html = `
            <div class="critical-insights">
                <div class="alert alert-info">
                    <h5>${__("Executive Summary")}</h5>
                    <div class="row">
                        <div class="col-sm-3">
                            <strong>${summary.num_bottleneck_machines || 0}</strong>
                            <br><small>${__("Bottleneck Machines")}</small>
                        </div>
                        <div class="col-sm-3">
                            <strong>${summary.num_at_risk_operations || 0}</strong>
                            <br><small>${__("At-Risk Operations")}</small>
                        </div>
                        <div class="col-sm-3">
                            <strong>${summary.num_high_delay_risk || 0}</strong>
                            <br><small>${__("High Delay Risk")}</small>
                        </div>
                        <div class="col-sm-3">
                            <strong>${(summary.expected_total_delay || 0).toFixed(0)} min</strong>
                            <br><small>${__("Expected Delay")}</small>
                        </div>
                    </div>
                </div>
        `;

        if (result.recommendations && result.recommendations.length > 0) {
            html += `<h5>${__("Top Recommendations")}</h5><ul>`;
            result.recommendations.forEach(rec => {
                html += `<li>${rec}</li>`;
            });
            html += `</ul>`;
        }

        if (result.critical_bottlenecks && result.critical_bottlenecks.length > 0) {
            html += `
                <h5 class="text-danger">${__("Critical Bottlenecks")}</h5>
                <ul>`;
            result.critical_bottlenecks.forEach(b => {
                html += `<li><strong>${b.machine_id}</strong>: ${(b.bottleneck_probability * 100).toFixed(0)}% probability</li>`;
            });
            html += `</ul>`;
        }

        html += `</div>`;

        frappe.msgprint({
            title: __("Critical Insights (GNN Analysis)"),
            message: html,
            indicator: summary.num_bottleneck_machines > 0 ? "red" : "green",
            wide: true
        });
    },

    // ============================================
    // Utility Methods
    // ============================================
    check_tier_status: function(show_message) {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.hybrid_scheduler.get_tier_status",
            callback: function(r) {
                if (r.message) {
                    frm.tier_status = {
                        tier1: r.message.tier1_ortools?.available || false,
                        tier2: r.message.tier2_rl?.available || false,
                        tier3: r.message.tier3_gnn?.available || false
                    };

                    if (show_message) {
                        let html = `
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>${__("Tier")}</th>
                                        <th>${__("Status")}</th>
                                        <th>${__("Details")}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><strong>Tier 1</strong> - OR-Tools</td>
                                        <td>${frm.tier_status.tier1 ?
                                            '<span class="badge badge-success">Available</span>' :
                                            '<span class="badge badge-danger">Not Available</span>'}</td>
                                        <td>${r.message.tier1_ortools?.status || "-"}</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Tier 2</strong> - RL Agent</td>
                                        <td>${frm.tier_status.tier2 ?
                                            '<span class="badge badge-success">Available</span>' :
                                            '<span class="badge badge-danger">Not Available</span>'}</td>
                                        <td>${r.message.tier2_rl?.status || "-"}<br>
                                            ${r.message.tier2_rl?.agents?.join(", ") || ""}</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Tier 3</strong> - GNN</td>
                                        <td>${frm.tier_status.tier3 ?
                                            '<span class="badge badge-success">Available</span>' :
                                            '<span class="badge badge-danger">Not Available</span>'}</td>
                                        <td>${r.message.tier3_gnn?.status || "-"}</td>
                                    </tr>
                                </tbody>
                            </table>
                        `;

                        frappe.msgprint({
                            title: __("Hybrid APS Tier Status"),
                            message: html,
                            indicator: "blue"
                        });
                    }
                }
            }
        });
    },

    view_scheduling_results: function() {
        let frm = this;

        frappe.set_route("List", "APS Scheduling Result", {
            scheduling_run: frm.doc.name
        });
    },

    export_to_gantt: function() {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.api.scheduling_api.get_gantt_data",
            args: {
                scheduling_run: frm.doc.name
            },
            callback: function(r) {
                if (r.message) {
                    // Open Gantt view in new dialog or page
                    frm.show_gantt_chart(r.message);
                }
            }
        });
    },

    show_gantt_chart: function(data) {
        // Placeholder for Gantt chart visualization
        frappe.msgprint({
            title: __("Gantt Chart"),
            message: __("Gantt chart visualization coming soon. {0} operations loaded.", [data.length || 0]),
            indicator: "blue"
        });
    },

    update_status_indicator: function() {
        let frm = this;

        // Add visual status indicator
        let statusColor = {
            "Pending": "orange",
            "Running": "blue",
            "Pending Approval": "yellow",
            "Applied": "green",
            "Completed": "green",
            "Failed": "red"
        }[frm.doc.run_status] || "gray";

        frm.page.set_indicator(frm.doc.run_status, statusColor);
    },

    update_tier_visibility: function() {
        let frm = this;
        // Additional logic to show/hide fields based on tier selection
    },

    show_optimization_analysis: function() {
        let frm = this;

        // Build constraints section
        let constraintsHtml = `
            <div class="optimization-analysis">
                <h5 class="text-primary mb-3">${__("Scheduling Constraints Applied")}</h5>
                <div class="row mb-3">
                    <div class="col-sm-6">
                        <ul class="list-unstyled">
                            <li>${frm.doc.constraint_machine_eligibility ? '✅' : '❌'} ${__("Machine Eligibility")}</li>
                            <li>${frm.doc.constraint_precedence ? '✅' : '❌'} ${__("Operation Precedence")}</li>
                            <li>${frm.doc.constraint_no_overlap ? '✅' : '❌'} ${__("No Overlap (Machine)")}</li>
                        </ul>
                    </div>
                    <div class="col-sm-6">
                        <ul class="list-unstyled">
                            <li>${frm.doc.constraint_working_hours ? '✅' : '❌'} ${__("Working Hours")}</li>
                            <li>${frm.doc.constraint_due_dates ? '✅' : '❌'} ${__("Due Date Respect")}</li>
                            <li>${frm.doc.constraint_setup_time ? '✅' : '❌'} ${__("Setup Time")}</li>
                        </ul>
                    </div>
                </div>

                ${frm.doc.constraints_description ? `
                    <div class="well" style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; font-size: 12px; white-space: pre-wrap;">
                        ${frm.doc.constraints_description}
                    </div>
                ` : ''}

                <h5 class="text-primary mb-3">${__("Optimization Comparison (vs FIFO Baseline)")}</h5>
                <table class="table table-bordered">
                    <thead>
                        <tr class="bg-light">
                            <th>${__("Metric")}</th>
                            <th>${__("FIFO Baseline")}</th>
                            <th>${__("APS Optimized")}</th>
                            <th>${__("Improvement")}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>${__("Makespan")}</strong></td>
                            <td>${frm.doc.baseline_makespan_minutes || 0} ${__("mins")}</td>
                            <td>${frm.doc.makespan_minutes || 0} ${__("mins")}</td>
                            <td class="${(frm.doc.improvement_makespan_percent || 0) > 0 ? 'text-success' : 'text-danger'}">
                                ${(frm.doc.improvement_makespan_percent || 0) > 0 ? '↓' : '↑'}
                                ${Math.abs(frm.doc.improvement_makespan_percent || 0).toFixed(1)}%
                            </td>
                        </tr>
                        <tr>
                            <td><strong>${__("Late Jobs")}</strong></td>
                            <td>${frm.doc.baseline_late_jobs || 0}</td>
                            <td>${frm.doc.total_late_jobs || 0}</td>
                            <td class="${(frm.doc.improvement_late_jobs_percent || 0) > 0 ? 'text-success' : 'text-danger'}">
                                ${(frm.doc.improvement_late_jobs_percent || 0) > 0 ? '↓' : '↑'}
                                ${Math.abs(frm.doc.improvement_late_jobs_percent || 0).toFixed(1)}%
                            </td>
                        </tr>
                        <tr>
                            <td><strong>${__("Total Tardiness")}</strong></td>
                            <td>${frm.doc.baseline_total_tardiness || 0} ${__("mins")}</td>
                            <td>${frm.doc.total_tardiness_minutes || 0} ${__("mins")}</td>
                            <td class="${(frm.doc.improvement_tardiness_percent || 0) > 0 ? 'text-success' : 'text-danger'}">
                                ${(frm.doc.improvement_tardiness_percent || 0) > 0 ? '↓' : '↑'}
                                ${Math.abs(frm.doc.improvement_tardiness_percent || 0).toFixed(1)}%
                            </td>
                        </tr>
                    </tbody>
                </table>

                ${frm.doc.comparison_summary ? `
                    <div class="alert ${(frm.doc.improvement_makespan_percent || 0) > 0 || (frm.doc.improvement_late_jobs_percent || 0) > 0 ? 'alert-success' : 'alert-warning'}">
                        <pre style="white-space: pre-wrap; margin: 0; font-family: inherit;">${frm.doc.comparison_summary}</pre>
                    </div>
                ` : ''}

                <h5 class="text-primary mb-3">${__("Solver Performance")}</h5>
                <div class="row">
                    <div class="col-sm-4">
                        <div class="stat-card text-center p-2 border rounded">
                            <h4 class="text-primary">${frm.doc.solver_status || 'N/A'}</h4>
                            <small>${__("Solver Status")}</small>
                        </div>
                    </div>
                    <div class="col-sm-4">
                        <div class="stat-card text-center p-2 border rounded">
                            <h4 class="text-info">${(frm.doc.solve_time_seconds || 0).toFixed(2)}s</h4>
                            <small>${__("Solve Time")}</small>
                        </div>
                    </div>
                    <div class="col-sm-4">
                        <div class="stat-card text-center p-2 border rounded">
                            <h4 class="text-warning">${(frm.doc.machine_utilization || 0).toFixed(1)}%</h4>
                            <small>${__("Machine Utilization")}</small>
                        </div>
                    </div>
                </div>
            </div>
        `;

        frappe.msgprint({
            title: __("Optimization Analysis"),
            message: constraintsHtml,
            indicator: (frm.doc.improvement_makespan_percent || 0) > 0 || (frm.doc.improvement_late_jobs_percent || 0) > 0 ? "green" : "orange",
            wide: true
        });
    },

    // ============================================
    // PHASE 4: Evaluation & Deployment Methods
    // ============================================
    evaluate_against_heuristics: function() {
        let frm = this;

        let d = new frappe.ui.Dialog({
            title: __("Evaluate Agent vs Heuristics"),
            fields: [
                {
                    label: __("Agent Type"),
                    fieldname: "agent_type",
                    fieldtype: "Select",
                    options: "ppo\nsac",
                    default: "ppo"
                },
                {
                    label: __("Number of Test Scenarios"),
                    fieldname: "num_scenarios",
                    fieldtype: "Int",
                    default: 20
                },
                {
                    label: __("Compare with Heuristics"),
                    fieldname: "heuristics",
                    fieldtype: "MultiCheck",
                    options: [
                        {label: "SPT (Shortest Processing Time)", value: "spt", checked: 1},
                        {label: "EDD (Earliest Due Date)", value: "edd", checked: 1},
                        {label: "FCFS (First Come First Served)", value: "fcfs", checked: 1},
                        {label: "LPT (Longest Processing Time)", value: "lpt", checked: 0},
                        {label: "CR (Critical Ratio)", value: "cr", checked: 0}
                    ]
                }
            ],
            primary_action_label: __("Run Evaluation"),
            primary_action: function(values) {
                d.hide();
                let heuristics = values.heuristics.join(",");

                frappe.call({
                    method: "uit_aps.scheduling.rl.evaluation_api.evaluate_agent",
                    args: {
                        scheduling_run: frm.doc.name,
                        agent_type: values.agent_type,
                        num_scenarios: values.num_scenarios,
                        compare_heuristics: heuristics
                    },
                    freeze: true,
                    freeze_message: __("Running evaluation... This may take a few minutes."),
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frm.show_evaluation_results(r.message.analysis);
                        } else {
                            frappe.msgprint({
                                title: __("Evaluation Failed"),
                                message: r.message?.error || __("Unknown error"),
                                indicator: "red"
                            });
                        }
                    }
                });
            }
        });
        d.show();
    },

    show_evaluation_results: function(analysis) {
        let rl_stats = analysis.rl_agent || {};
        let summary = analysis.summary || {};

        let html = `
            <div class="evaluation-results">
                <div class="alert alert-info">
                    <h5>${__("RL Agent Performance")}</h5>
                    <div class="row">
                        <div class="col-sm-3">
                            <strong>${(rl_stats.reward?.mean || 0).toFixed(2)}</strong>
                            <br><small>${__("Mean Reward")}</small>
                        </div>
                        <div class="col-sm-3">
                            <strong>${((rl_stats.on_time_rate?.mean || 0) * 100).toFixed(1)}%</strong>
                            <br><small>${__("On-Time Rate")}</small>
                        </div>
                        <div class="col-sm-3">
                            <strong>${(rl_stats.makespan?.mean || 0).toFixed(0)} min</strong>
                            <br><small>${__("Avg Makespan")}</small>
                        </div>
                        <div class="col-sm-3">
                            <strong>${(rl_stats.tardiness?.mean || 0).toFixed(0)} min</strong>
                            <br><small>${__("Avg Tardiness")}</small>
                        </div>
                    </div>
                </div>

                <h5>${__("Comparison with Heuristics")}</h5>
                <table class="table table-sm table-bordered">
                    <thead>
                        <tr>
                            <th>${__("Heuristic")}</th>
                            <th>${__("Reward Improvement")}</th>
                            <th>${__("Win Rate")}</th>
                            <th>${__("Result")}</th>
                        </tr>
                    </thead>
                    <tbody>`;

        if (analysis.comparisons) {
            Object.values(analysis.comparisons).forEach(comp => {
                let improvement = comp.reward_improvement_pct;
                let color = improvement > 0 ? "success" : "danger";
                html += `
                    <tr>
                        <td>${comp.heuristic.toUpperCase()}</td>
                        <td class="text-${color}">${improvement > 0 ? "+" : ""}${improvement.toFixed(1)}%</td>
                        <td>${(comp.win_rate * 100).toFixed(0)}%</td>
                        <td><span class="badge badge-${comp.rl_better ? "success" : "warning"}">
                            ${comp.rl_better ? __("RL Better") : __("Heuristic Better")}
                        </span></td>
                    </tr>`;
            });
        }

        html += `
                    </tbody>
                </table>

                <div class="alert alert-${summary.recommendation === "RL Agent" ? "success" : "warning"}">
                    <strong>${__("Recommendation")}:</strong> ${summary.recommendation}
                    <br><small>${__("RL beats")} ${summary.beats_heuristics} ${__("heuristics")}</small>
                </div>
            </div>`;

        frappe.msgprint({
            title: __("Evaluation Results"),
            message: html,
            indicator: "blue",
            wide: true
        });
    },

    compare_with_ortools: function() {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.rl.evaluation_api.compare_with_ortools",
            args: {
                scheduling_run: frm.doc.name
            },
            freeze: true,
            freeze_message: __("Comparing with OR-Tools..."),
            callback: function(r) {
                if (r.message && r.message.success) {
                    let data = r.message;
                    let html = `
                        <div class="comparison-results">
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>${__("Metric")}</th>
                                        <th>${__("OR-Tools")}</th>
                                        <th>${__("RL Agent")}</th>
                                        <th>${__("Difference")}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>${__("Makespan")}</td>
                                        <td>${data.ortools.makespan_minutes} min</td>
                                        <td>${data.rl_agent.makespan_minutes} min</td>
                                        <td>${data.comparison.makespan_improvement.toFixed(1)}%</td>
                                    </tr>
                                    <tr>
                                        <td>${__("Total Tardiness")}</td>
                                        <td>${data.ortools.total_tardiness_minutes} min</td>
                                        <td>${data.rl_agent.total_tardiness_minutes} min</td>
                                        <td>${data.comparison.tardiness_improvement.toFixed(1)}%</td>
                                    </tr>
                                    <tr>
                                        <td>${__("Solve Time")}</td>
                                        <td>${data.ortools.solve_time_seconds} s</td>
                                        <td>${data.rl_agent.inference_time_ms} ms</td>
                                        <td>${data.comparison.speed_improvement.toFixed(0)}x faster</td>
                                    </tr>
                                </tbody>
                            </table>
                            <div class="alert alert-info">
                                <strong>${__("Recommendation")}:</strong> ${data.recommendation}
                            </div>
                        </div>`;

                    frappe.msgprint({
                        title: __("OR-Tools vs RL Agent Comparison"),
                        message: html,
                        indicator: "blue"
                    });
                } else {
                    frappe.msgprint({
                        title: __("Comparison Failed"),
                        message: r.message?.error || __("Unknown error"),
                        indicator: "red"
                    });
                }
            }
        });
    },

    show_deployment_status: function() {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.rl.evaluation_api.get_deployment_status",
            callback: function(r) {
                if (r.message && r.message.success) {
                    let data = r.message;
                    let html = `
                        <div class="deployment-status">
                            <div class="alert alert-info">
                                <strong>${__("Active Version")}:</strong> ${data.active_version || __("None")}
                            </div>

                            <h5>${__("All Versions")}</h5>
                            <table class="table table-sm table-bordered">
                                <thead>
                                    <tr>
                                        <th>${__("Version")}</th>
                                        <th>${__("Agent Type")}</th>
                                        <th>${__("Status")}</th>
                                        <th>${__("Created")}</th>
                                    </tr>
                                </thead>
                                <tbody>`;

                    if (data.versions && data.versions.length > 0) {
                        data.versions.forEach(v => {
                            let statusClass = {
                                "active": "success",
                                "shadow": "warning",
                                "pending": "info",
                                "retired": "secondary"
                            }[v.status] || "secondary";

                            html += `
                                <tr>
                                    <td>${v.version_id}</td>
                                    <td>${v.agent_type.toUpperCase()}</td>
                                    <td><span class="badge badge-${statusClass}">${v.status}</span></td>
                                    <td>${v.created_at}</td>
                                </tr>`;
                        });
                    } else {
                        html += `<tr><td colspan="4">${__("No versions found")}</td></tr>`;
                    }

                    html += `
                                </tbody>
                            </table>
                            <p><small>${__("Total versions")}: ${data.total_versions || 0}</small></p>
                        </div>`;

                    frappe.msgprint({
                        title: __("Model Deployment Status"),
                        message: html,
                        indicator: "blue",
                        wide: true
                    });
                }
            }
        });
    },

    show_monitoring_summary: function() {
        let frm = this;

        frappe.call({
            method: "uit_aps.scheduling.rl.evaluation_api.get_monitoring_summary",
            args: {
                last_n: 100
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    let summary = r.message.summary || {};

                    let html = `
                        <div class="monitoring-summary">
                            <div class="row">`;

                    if (summary.total_reward) {
                        html += `
                            <div class="col-sm-4">
                                <div class="stat-box">
                                    <h3>${(summary.total_reward?.mean || 0).toFixed(2)}</h3>
                                    <p>${__("Avg Reward")}</p>
                                    <small>${__("Trend")}: ${summary.total_reward?.trend || "stable"}</small>
                                </div>
                            </div>`;
                    }

                    if (summary.total_tardiness_mins) {
                        html += `
                            <div class="col-sm-4">
                                <div class="stat-box">
                                    <h3>${(summary.total_tardiness_mins?.mean || 0).toFixed(0)} min</h3>
                                    <p>${__("Avg Tardiness")}</p>
                                </div>
                            </div>`;
                    }

                    html += `
                            <div class="col-sm-4">
                                <div class="stat-box">
                                    <h3>${summary.num_decisions || 0}</h3>
                                    <p>${__("Total Decisions")}</p>
                                </div>
                            </div>
                        </div>`;

                    if (summary.num_alerts > 0) {
                        html += `
                            <div class="alert alert-warning mt-3">
                                <strong>${__("Alerts")}:</strong> ${summary.num_alerts} ${__("recent alerts")}
                            </div>`;
                    }

                    html += `</div>`;

                    frappe.msgprint({
                        title: __("Production Monitoring Summary"),
                        message: html,
                        indicator: summary.num_alerts > 0 ? "orange" : "green"
                    });
                }
            }
        });
    }
});
