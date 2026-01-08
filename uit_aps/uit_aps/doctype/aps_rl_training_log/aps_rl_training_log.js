// Copyright (c) 2025, thanhnc and contributors
// For license information, please see license.txt

frappe.ui.form.on("APS RL Training Log", {
    refresh(frm) {
        // Add progress bar
        frm.add_training_progress_bar();

        // Add chart for reward history
        if (frm.doc.reward_history) {
            frm.add_reward_chart();
        }

        // Add refresh button for running trainings
        if (frm.doc.training_status === "Running") {
            frm.add_custom_button(__("Refresh Progress"), function() {
                frm.reload_doc();
            }, __("Actions"));

            // Auto-refresh every 5 seconds
            if (!frm.auto_refresh_interval) {
                frm.auto_refresh_interval = setInterval(function() {
                    if (frm.doc.training_status === "Running") {
                        frm.reload_doc();
                    } else {
                        clearInterval(frm.auto_refresh_interval);
                        frm.auto_refresh_interval = null;
                    }
                }, 5000);
            }
        }

        // Add view model button if completed
        if (frm.doc.training_status === "Completed" && frm.doc.model_path) {
            frm.add_custom_button(__("Deploy Model"), function() {
                frm.deploy_trained_model();
            }, __("Actions"));
        }
    },

    onload(frm) {
        // Clear auto-refresh on load
        if (frm.auto_refresh_interval) {
            clearInterval(frm.auto_refresh_interval);
            frm.auto_refresh_interval = null;
        }
    }
});

// Custom methods
$.extend(frappe.ui.form.on["APS RL Training Log"], {
    add_training_progress_bar: function(frm) {
        // Remove existing progress bar
        frm.fields_dict.progress_percentage.$wrapper.find(".training-progress-container").remove();

        if (frm.doc.training_status === "Running" || frm.doc.training_status === "Completed") {
            let progress = frm.doc.progress_percentage || 0;
            let color = frm.doc.training_status === "Completed" ? "green" : "blue";

            let html = `
                <div class="training-progress-container" style="margin-top: 10px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span><b>Episode ${frm.doc.current_episode || 0} / ${frm.doc.max_episodes || 0}</b></span>
                        <span>${progress.toFixed(1)}%</span>
                    </div>
                    <div class="progress" style="height: 25px;">
                        <div class="progress-bar progress-bar-${color}" role="progressbar"
                             style="width: ${progress}%;" aria-valuenow="${progress}"
                             aria-valuemin="0" aria-valuemax="100">
                        </div>
                    </div>
                    ${frm.doc.estimated_time_remaining ? `<div style="margin-top: 5px; color: #666;">
                        Est. remaining: ${frm.doc.estimated_time_remaining}
                    </div>` : ''}
                </div>
            `;

            frm.fields_dict.progress_percentage.$wrapper.append(html);
        }
    },

    add_reward_chart: function(frm) {
        // Remove existing chart
        frm.fields_dict.reward_history.$wrapper.find(".reward-chart-container").remove();

        try {
            let rewards = JSON.parse(frm.doc.reward_history || "[]");
            if (rewards.length === 0) return;

            // Create chart container
            let chartHtml = `
                <div class="reward-chart-container" style="margin-top: 15px;">
                    <h5>Reward Over Episodes</h5>
                    <canvas id="reward-chart" width="400" height="200"></canvas>
                </div>
            `;
            frm.fields_dict.reward_history.$wrapper.append(chartHtml);

            // Use frappe chart if available, otherwise simple visualization
            if (typeof Chart !== 'undefined') {
                let ctx = document.getElementById('reward-chart').getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: rewards.map((_, i) => i + 1),
                        datasets: [{
                            label: 'Reward',
                            data: rewards,
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1,
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { title: { display: true, text: 'Episode' } },
                            y: { title: { display: true, text: 'Reward' } }
                        }
                    }
                });
            } else {
                // Simple SVG chart fallback
                let width = 600, height = 200;
                let minR = Math.min(...rewards);
                let maxR = Math.max(...rewards);
                let range = maxR - minR || 1;

                let points = rewards.map((r, i) => {
                    let x = (i / (rewards.length - 1)) * width;
                    let y = height - ((r - minR) / range) * height;
                    return `${x},${y}`;
                }).join(' ');

                let svgHtml = `
                    <svg width="${width}" height="${height}" style="border: 1px solid #ddd;">
                        <polyline points="${points}" fill="none" stroke="#4bc0c0" stroke-width="2"/>
                    </svg>
                    <div style="display: flex; justify-content: space-between; font-size: 11px; color: #666;">
                        <span>Min: ${minR.toFixed(2)}</span>
                        <span>Max: ${maxR.toFixed(2)}</span>
                    </div>
                `;
                frm.fields_dict.reward_history.$wrapper.find(".reward-chart-container").html(`
                    <h5>Reward Over Episodes</h5>
                    ${svgHtml}
                `);
            }
        } catch (e) {
            console.error("Error parsing reward history:", e);
        }
    },

    deploy_trained_model: function(frm) {
        frappe.confirm(
            __("Deploy this trained model to production?"),
            function() {
                frappe.call({
                    method: "uit_aps.scheduling.rl.evaluation_api.register_trained_model",
                    args: {
                        agent_type: frm.doc.agent_type,
                        model_path: frm.doc.model_path,
                        training_summary: JSON.stringify({
                            config: {
                                max_episodes: frm.doc.max_episodes,
                                learning_rate: frm.doc.learning_rate,
                                gamma: frm.doc.gamma
                            },
                            metrics: {
                                best_reward: frm.doc.best_reward,
                                best_makespan: frm.doc.best_makespan,
                                best_tardiness: frm.doc.best_tardiness
                            }
                        })
                    },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({
                                message: __("Model registered: {0}", [r.message.version_id]),
                                indicator: "green"
                            });
                        } else {
                            frappe.msgprint({
                                title: __("Error"),
                                message: r.message ? r.message.error : __("Failed to register model"),
                                indicator: "red"
                            });
                        }
                    }
                });
            }
        );
    }
});
