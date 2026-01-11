frappe.pages['aps_demo_dashboard'] = frappe.pages['aps_demo_dashboard'] || {};

frappe.pages['aps_demo_dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'APS Demo Dashboard',
        single_column: true
    });

    // Add page actions
    page.set_primary_action(__('Refresh'), function() {
        page.aps_dashboard.refresh();
    }, 'refresh');

    page.set_secondary_action(__('Go to Scheduling'), function() {
        frappe.set_route('List', 'APS Scheduling Run');
    });

    // Initialize dashboard
    page.aps_dashboard = new APSDemoDashboard(page);
};

frappe.pages['aps_demo_dashboard'].refresh = function(wrapper) {
    if (wrapper.page.aps_dashboard) {
        wrapper.page.aps_dashboard.refresh();
    }
};

class APSDemoDashboard {
    constructor(page) {
        this.page = page;
        this.wrapper = $(page.body);
        this.init();
    }

    init() {
        this.render();
        this.bind_events();
        this.load_data();
    }

    render() {
        this.wrapper.html(`
            <div class="aps-demo-dashboard">
                <style>
                    .aps-demo-dashboard {
                        padding: 20px;
                    }
                    .dashboard-section {
                        background: white;
                        border-radius: 8px;
                        padding: 20px;
                        margin-bottom: 20px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    }
                    .section-title {
                        font-size: 18px;
                        font-weight: 600;
                        color: #2c3e50;
                        margin-bottom: 15px;
                        padding-bottom: 10px;
                        border-bottom: 2px solid #3498db;
                    }
                    .btn-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                        gap: 15px;
                    }
                    .action-card {
                        background: #f8f9fa;
                        border: 1px solid #e9ecef;
                        border-radius: 8px;
                        padding: 15px;
                        text-align: center;
                        cursor: pointer;
                        transition: all 0.2s;
                    }
                    .action-card:hover {
                        background: #e9ecef;
                        transform: translateY(-2px);
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    }
                    .action-card .icon {
                        font-size: 32px;
                        margin-bottom: 10px;
                        color: #3498db;
                    }
                    .action-card .title {
                        font-weight: 600;
                        margin-bottom: 5px;
                    }
                    .action-card .description {
                        font-size: 12px;
                        color: #6c757d;
                    }
                    .action-card.primary {
                        background: #3498db;
                        color: white;
                        border-color: #2980b9;
                    }
                    .action-card.primary:hover {
                        background: #2980b9;
                    }
                    .action-card.primary .icon,
                    .action-card.primary .description {
                        color: white;
                    }
                    .action-card.success {
                        background: #27ae60;
                        color: white;
                        border-color: #1e8449;
                    }
                    .action-card.success:hover {
                        background: #1e8449;
                    }
                    .action-card.success .icon,
                    .action-card.success .description {
                        color: white;
                    }
                    .action-card.warning {
                        background: #f39c12;
                        color: white;
                        border-color: #d68910;
                    }
                    .action-card.warning:hover {
                        background: #d68910;
                    }
                    .action-card.warning .icon,
                    .action-card.warning .description {
                        color: white;
                    }
                    .action-card.danger {
                        background: #e74c3c;
                        color: white;
                        border-color: #c0392b;
                    }
                    .action-card.danger:hover {
                        background: #c0392b;
                    }
                    .action-card.danger .icon,
                    .action-card.danger .description {
                        color: white;
                    }
                    .stats-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                        gap: 15px;
                        margin-bottom: 20px;
                    }
                    .stat-card {
                        background: white;
                        border: 1px solid #e9ecef;
                        border-radius: 8px;
                        padding: 15px;
                        text-align: center;
                    }
                    .stat-card .value {
                        font-size: 28px;
                        font-weight: bold;
                        color: #2c3e50;
                    }
                    .stat-card .label {
                        font-size: 12px;
                        color: #6c757d;
                        margin-top: 5px;
                    }
                    .recent-runs {
                        margin-top: 15px;
                    }
                    .recent-runs table {
                        width: 100%;
                    }
                    .recent-runs th {
                        background: #f8f9fa;
                        padding: 10px;
                        text-align: left;
                        font-weight: 600;
                    }
                    .recent-runs td {
                        padding: 10px;
                        border-bottom: 1px solid #e9ecef;
                    }
                    .badge {
                        display: inline-block;
                        padding: 3px 8px;
                        border-radius: 12px;
                        font-size: 11px;
                        font-weight: 600;
                    }
                    .badge-success { background: #d4edda; color: #155724; }
                    .badge-warning { background: #fff3cd; color: #856404; }
                    .badge-danger { background: #f8d7da; color: #721c24; }
                    .badge-info { background: #d1ecf1; color: #0c5460; }
                    .badge-primary { background: #cce5ff; color: #004085; }
                    .log-area {
                        background: #1e1e1e;
                        color: #d4d4d4;
                        border-radius: 8px;
                        padding: 15px;
                        font-family: 'Consolas', 'Monaco', monospace;
                        font-size: 12px;
                        max-height: 300px;
                        overflow-y: auto;
                        margin-top: 15px;
                    }
                    .log-area .log-entry {
                        margin-bottom: 5px;
                    }
                    .log-area .log-time {
                        color: #6a9955;
                    }
                    .log-area .log-success {
                        color: #4ec9b0;
                    }
                    .log-area .log-error {
                        color: #f14c4c;
                    }
                    .log-area .log-info {
                        color: #569cd6;
                    }
                </style>

                <!-- Stats Overview -->
                <div class="dashboard-section">
                    <div class="section-title">
                        <i class="fa fa-chart-bar"></i> Overview Statistics
                    </div>
                    <div class="stats-grid" id="stats-grid">
                        <div class="stat-card">
                            <div class="value" id="stat-production-plans">-</div>
                            <div class="label">Production Plans</div>
                        </div>
                        <div class="stat-card">
                            <div class="value" id="stat-scheduling-runs">-</div>
                            <div class="label">Scheduling Runs</div>
                        </div>
                        <div class="stat-card">
                            <div class="value" id="stat-workstations">-</div>
                            <div class="label">Workstations</div>
                        </div>
                        <div class="stat-card">
                            <div class="value" id="stat-job-cards">-</div>
                            <div class="label">Job Cards</div>
                        </div>
                    </div>
                </div>

                <!-- Demo Data Section -->
                <div class="dashboard-section">
                    <div class="section-title">
                        <i class="fa fa-database"></i> Demo Data Management
                    </div>
                    <div class="btn-grid">
                        <div class="action-card primary" data-action="generate-demo-data">
                            <div class="icon"><i class="fa fa-magic"></i></div>
                            <div class="title">Generate Demo Data</div>
                            <div class="description">Create 3 Production Plans with test data</div>
                        </div>
                        <div class="action-card" data-action="view-demo-status">
                            <div class="icon"><i class="fa fa-info-circle"></i></div>
                            <div class="title">View Demo Status</div>
                            <div class="description">Check current demo data status</div>
                        </div>
                        <div class="action-card danger" data-action="cleanup-demo-data">
                            <div class="icon"><i class="fa fa-trash"></i></div>
                            <div class="title">Cleanup Demo Data</div>
                            <div class="description">Remove all demo data</div>
                        </div>
                    </div>
                </div>

                <!-- Scheduling Section -->
                <div class="dashboard-section">
                    <div class="section-title">
                        <i class="fa fa-calendar-alt"></i> Scheduling Operations
                    </div>
                    <div class="btn-grid">
                        <div class="action-card success" data-action="run-scheduling">
                            <div class="icon"><i class="fa fa-play"></i></div>
                            <div class="title">Run Scheduling</div>
                            <div class="description">Run OR-Tools optimization</div>
                        </div>
                        <div class="action-card" data-action="view-gantt">
                            <div class="icon"><i class="fa fa-tasks"></i></div>
                            <div class="title">View Gantt Chart</div>
                            <div class="description">Open Gantt visualization</div>
                        </div>
                        <div class="action-card" data-action="compare-schedules">
                            <div class="icon"><i class="fa fa-balance-scale"></i></div>
                            <div class="title">Compare Schedules</div>
                            <div class="description">Compare two scheduling runs</div>
                        </div>
                    </div>
                </div>

                <!-- Machine Breakdown Section -->
                <div class="dashboard-section">
                    <div class="section-title">
                        <i class="fa fa-exclamation-triangle"></i> Machine Breakdown Management
                    </div>
                    <div class="btn-grid">
                        <div class="action-card warning" data-action="simulate-breakdown">
                            <div class="icon"><i class="fa fa-tools"></i></div>
                            <div class="title">Simulate Breakdown</div>
                            <div class="description">Test machine failure scenario</div>
                        </div>
                        <div class="action-card danger" data-action="reschedule-breakdown">
                            <div class="icon"><i class="fa fa-sync"></i></div>
                            <div class="title">Reschedule</div>
                            <div class="description">Reschedule with exclusions</div>
                        </div>
                        <div class="action-card" data-action="view-affected">
                            <div class="icon"><i class="fa fa-search"></i></div>
                            <div class="title">View Affected Jobs</div>
                            <div class="description">See impacted operations</div>
                        </div>
                    </div>
                </div>

                <!-- Reports Section -->
                <div class="dashboard-section">
                    <div class="section-title">
                        <i class="fa fa-file-alt"></i> Reports & Export
                    </div>
                    <div class="btn-grid">
                        <div class="action-card success" data-action="export-excel">
                            <div class="icon"><i class="fa fa-file-excel"></i></div>
                            <div class="title">Export Excel Report</div>
                            <div class="description">Full comparison report</div>
                        </div>
                        <div class="action-card" data-action="export-gantt-excel">
                            <div class="icon"><i class="fa fa-table"></i></div>
                            <div class="title">Export Gantt Data</div>
                            <div class="description">Gantt chart data to Excel</div>
                        </div>
                        <div class="action-card" data-action="view-report-preview">
                            <div class="icon"><i class="fa fa-eye"></i></div>
                            <div class="title">Report Preview</div>
                            <div class="description">Preview scheduling report</div>
                        </div>
                        <div class="action-card primary" data-action="print-report">
                            <div class="icon"><i class="fa fa-print"></i></div>
                            <div class="title">Print Report</div>
                            <div class="description">Print PDF report</div>
                        </div>
                    </div>
                </div>

                <!-- AI Analysis Section -->
                <div class="dashboard-section">
                    <div class="section-title">
                        <i class="fa fa-brain"></i> AI Analysis & Recommendations
                    </div>
                    <div class="btn-grid">
                        <div class="action-card primary" data-action="get-ai-analysis">
                            <div class="icon"><i class="fa fa-robot"></i></div>
                            <div class="title">Get AI Analysis</div>
                            <div class="description">Analyze with GPT</div>
                        </div>
                        <div class="action-card" data-action="predict-bottlenecks">
                            <div class="icon"><i class="fa fa-chart-line"></i></div>
                            <div class="title">Predict Bottlenecks</div>
                            <div class="description">GNN bottleneck prediction</div>
                        </div>
                        <div class="action-card" data-action="train-rl">
                            <div class="icon"><i class="fa fa-graduation-cap"></i></div>
                            <div class="title">Train RL Agent</div>
                            <div class="description">Train reinforcement learning</div>
                        </div>
                    </div>
                </div>

                <!-- Recent Runs -->
                <div class="dashboard-section">
                    <div class="section-title">
                        <i class="fa fa-history"></i> Recent Scheduling Runs
                    </div>
                    <div class="recent-runs" id="recent-runs">
                        <p class="text-muted">Loading...</p>
                    </div>
                </div>

                <!-- Activity Log -->
                <div class="dashboard-section">
                    <div class="section-title">
                        <i class="fa fa-terminal"></i> Activity Log
                    </div>
                    <div class="log-area" id="activity-log">
                        <div class="log-entry">
                            <span class="log-time">[${new Date().toLocaleTimeString()}]</span>
                            <span class="log-info">Dashboard initialized</span>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    bind_events() {
        let me = this;

        // Action card clicks
        this.wrapper.find('.action-card').on('click', function() {
            let action = $(this).data('action');
            me.handle_action(action);
        });
    }

    handle_action(action) {
        let me = this;

        switch(action) {
            case 'generate-demo-data':
                me.generate_demo_data();
                break;
            case 'view-demo-status':
                me.view_demo_status();
                break;
            case 'cleanup-demo-data':
                me.cleanup_demo_data();
                break;
            case 'run-scheduling':
                me.run_scheduling();
                break;
            case 'view-gantt':
                me.view_gantt();
                break;
            case 'compare-schedules':
                me.compare_schedules();
                break;
            case 'simulate-breakdown':
                me.simulate_breakdown();
                break;
            case 'reschedule-breakdown':
                me.reschedule_breakdown();
                break;
            case 'view-affected':
                me.view_affected_operations();
                break;
            case 'export-excel':
                me.export_excel();
                break;
            case 'export-gantt-excel':
                me.export_gantt_excel();
                break;
            case 'view-report-preview':
                me.view_report_preview();
                break;
            case 'print-report':
                me.print_report();
                break;
            case 'get-ai-analysis':
                me.get_ai_analysis();
                break;
            case 'predict-bottlenecks':
                me.predict_bottlenecks();
                break;
            case 'train-rl':
                me.train_rl_agent();
                break;
            default:
                frappe.msgprint(__('Action not implemented: {0}', [action]));
        }
    }

    log(message, type = 'info') {
        let time = new Date().toLocaleTimeString();
        let typeClass = `log-${type}`;
        let logEntry = `<div class="log-entry"><span class="log-time">[${time}]</span> <span class="${typeClass}">${message}</span></div>`;
        this.wrapper.find('#activity-log').prepend(logEntry);
    }

    load_data() {
        this.load_stats();
        this.load_recent_runs();
    }

    refresh() {
        this.load_data();
        this.log('Dashboard refreshed', 'info');
    }

    load_stats() {
        let me = this;

        // Load Production Plans count
        frappe.call({
            method: 'frappe.client.get_count',
            args: { doctype: 'Production Plan' },
            async: false,
            callback: function(r) {
                me.wrapper.find('#stat-production-plans').text(r.message || 0);
            }
        });

        // Load Scheduling Runs count
        frappe.call({
            method: 'frappe.client.get_count',
            args: { doctype: 'APS Scheduling Run' },
            async: false,
            callback: function(r) {
                me.wrapper.find('#stat-scheduling-runs').text(r.message || 0);
            }
        });

        // Load Workstations count
        frappe.call({
            method: 'frappe.client.get_count',
            args: { doctype: 'Workstation' },
            async: false,
            callback: function(r) {
                me.wrapper.find('#stat-workstations').text(r.message || 0);
            }
        });

        // Load Job Cards count
        frappe.call({
            method: 'frappe.client.get_count',
            args: { doctype: 'Job Card' },
            async: false,
            callback: function(r) {
                me.wrapper.find('#stat-job-cards').text(r.message || 0);
            }
        });
    }

    load_recent_runs() {
        let me = this;

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'APS Scheduling Run',
                fields: ['name', 'production_plan', 'run_status', 'makespan_minutes', 'total_late_jobs', 'run_date'],
                order_by: 'creation desc',
                limit_page_length: 10
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let html = `
                        <table>
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Production Plan</th>
                                    <th>Status</th>
                                    <th>Makespan</th>
                                    <th>Late Jobs</th>
                                    <th>Run Date</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;

                    r.message.forEach(run => {
                        let statusClass = {
                            'Completed': 'success',
                            'Pending Approval': 'warning',
                            'Applied': 'primary',
                            'Running': 'info',
                            'Failed': 'danger',
                            'Pending': 'info'
                        }[run.run_status] || 'info';

                        html += `
                            <tr>
                                <td><a href="/app/aps-scheduling-run/${run.name}">${run.name}</a></td>
                                <td>${run.production_plan || '-'}</td>
                                <td><span class="badge badge-${statusClass}">${run.run_status}</span></td>
                                <td>${run.makespan_minutes || 0} mins</td>
                                <td>${run.total_late_jobs || 0}</td>
                                <td>${run.run_date ? frappe.datetime.str_to_user(run.run_date) : '-'}</td>
                                <td>
                                    <button class="btn btn-xs btn-default btn-export-run" data-run="${run.name}">
                                        <i class="fa fa-download"></i>
                                    </button>
                                    <button class="btn btn-xs btn-default btn-view-run" data-run="${run.name}">
                                        <i class="fa fa-eye"></i>
                                    </button>
                                </td>
                            </tr>
                        `;
                    });

                    html += '</tbody></table>';
                    me.wrapper.find('#recent-runs').html(html);

                    // Bind action buttons
                    me.wrapper.find('.btn-export-run').on('click', function() {
                        let run = $(this).data('run');
                        me.export_run_excel(run);
                    });

                    me.wrapper.find('.btn-view-run').on('click', function() {
                        let run = $(this).data('run');
                        frappe.set_route('Form', 'APS Scheduling Run', run);
                    });
                } else {
                    me.wrapper.find('#recent-runs').html('<p class="text-muted">No scheduling runs found</p>');
                }
            }
        });
    }

    // =========================================
    // Demo Data Actions
    // =========================================
    generate_demo_data() {
        let me = this;

        frappe.confirm(
            __('This will create demo Production Plans, Work Orders, and Job Cards. Continue?'),
            function() {
                me.log('Generating demo data...', 'info');

                frappe.call({
                    method: 'uit_aps.scheduling.demo.demo_data_generator.generate_demo_data',
                    freeze: true,
                    freeze_message: __('Generating demo data...'),
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            me.log('Demo data generated successfully!', 'success');
                            frappe.show_alert({
                                message: __('Demo data generated! Created {0} Production Plans', [r.message.production_plans?.length || 0]),
                                indicator: 'green'
                            });
                            me.refresh();
                        } else {
                            me.log('Failed to generate demo data: ' + (r.message?.error || 'Unknown error'), 'error');
                            frappe.msgprint({
                                title: __('Error'),
                                message: r.message?.error || __('Failed to generate demo data'),
                                indicator: 'red'
                            });
                        }
                    },
                    error: function(r) {
                        me.log('Error generating demo data', 'error');
                    }
                });
            }
        );
    }

    view_demo_status() {
        let me = this;

        frappe.call({
            method: 'uit_aps.scheduling.demo.demo_data_generator.get_demo_status',
            callback: function(r) {
                if (r.message) {
                    let data = r.message;
                    let html = `
                        <div class="demo-status">
                            <table class="table table-bordered">
                                <tr><td><strong>Workstations</strong></td><td>${data.workstations || 0}</td></tr>
                                <tr><td><strong>Items</strong></td><td>${data.items || 0}</td></tr>
                                <tr><td><strong>Production Plans</strong></td><td>${data.production_plans || 0}</td></tr>
                                <tr><td><strong>Work Orders</strong></td><td>${data.work_orders || 0}</td></tr>
                                <tr><td><strong>Job Cards</strong></td><td>${data.job_cards || 0}</td></tr>
                                <tr><td><strong>Scheduling Runs</strong></td><td>${data.scheduling_runs || 0}</td></tr>
                            </table>
                        </div>
                    `;

                    frappe.msgprint({
                        title: __('Demo Data Status'),
                        message: html,
                        indicator: 'blue'
                    });

                    me.log('Viewed demo status', 'info');
                }
            }
        });
    }

    cleanup_demo_data() {
        let me = this;

        frappe.confirm(
            __('This will DELETE all demo data (Production Plans, Work Orders, Job Cards). This cannot be undone. Continue?'),
            function() {
                me.log('Cleaning up demo data...', 'info');

                frappe.call({
                    method: 'uit_aps.scheduling.demo.demo_data_generator.cleanup_demo_data',
                    freeze: true,
                    freeze_message: __('Cleaning up demo data...'),
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            me.log('Demo data cleaned up successfully!', 'success');
                            frappe.show_alert({
                                message: __('Demo data cleaned up successfully'),
                                indicator: 'green'
                            });
                            me.refresh();
                        } else {
                            me.log('Failed to cleanup: ' + (r.message?.error || 'Unknown error'), 'error');
                        }
                    }
                });
            }
        );
    }

    // =========================================
    // Scheduling Actions
    // =========================================
    run_scheduling() {
        let me = this;

        // Show dialog to select Production Plan
        let d = new frappe.ui.Dialog({
            title: __('Run Scheduling'),
            fields: [
                {
                    label: __('Production Plan'),
                    fieldname: 'production_plan',
                    fieldtype: 'Link',
                    options: 'Production Plan',
                    reqd: 1,
                    get_query: function() {
                        return {
                            filters: {
                                docstatus: 1
                            }
                        };
                    }
                },
                {
                    label: __('Scheduling Strategy'),
                    fieldname: 'strategy',
                    fieldtype: 'Select',
                    options: 'Forward Scheduling\nBackward Scheduling\nMinimize Makespan\nMinimize Tardiness',
                    default: 'Forward Scheduling'
                },
                {
                    label: __('Time Limit (seconds)'),
                    fieldname: 'time_limit',
                    fieldtype: 'Int',
                    default: 300
                }
            ],
            primary_action_label: __('Run'),
            primary_action: function(values) {
                d.hide();
                me.log('Starting scheduling for ' + values.production_plan, 'info');

                // First create scheduling run
                frappe.call({
                    method: 'frappe.client.insert',
                    args: {
                        doc: {
                            doctype: 'APS Scheduling Run',
                            production_plan: values.production_plan,
                            scheduling_strategy: values.strategy,
                            scheduling_tier: 'Tier 1 - OR-Tools',
                            time_limit_seconds: values.time_limit
                        }
                    },
                    callback: function(r) {
                        if (r.message) {
                            // Now run scheduling
                            frappe.call({
                                method: 'uit_aps.scheduling.api.scheduling_api.run_ortools_scheduling',
                                args: {
                                    scheduling_run: r.message.name,
                                    scheduling_strategy: values.strategy,
                                    time_limit_seconds: values.time_limit
                                },
                                freeze: true,
                                freeze_message: __('Running OR-Tools solver...'),
                                callback: function(r2) {
                                    if (r2.message && r2.message.success) {
                                        me.log('Scheduling completed: ' + r2.message.scheduling_run, 'success');
                                        frappe.show_alert({
                                            message: __('Scheduling completed! Makespan: {0} mins', [r2.message.makespan_minutes]),
                                            indicator: 'green'
                                        });
                                        me.refresh();
                                    } else {
                                        me.log('Scheduling failed: ' + (r2.message?.message || 'Unknown error'), 'error');
                                    }
                                }
                            });
                        }
                    }
                });
            }
        });
        d.show();
    }

    view_gantt() {
        frappe.set_route('aps_gantt_chart');
    }

    compare_schedules() {
        let me = this;

        let d = new frappe.ui.Dialog({
            title: __('Compare Scheduling Runs'),
            fields: [
                {
                    label: __('First Run'),
                    fieldname: 'run1',
                    fieldtype: 'Link',
                    options: 'APS Scheduling Run',
                    reqd: 1
                },
                {
                    label: __('Second Run'),
                    fieldname: 'run2',
                    fieldtype: 'Link',
                    options: 'APS Scheduling Run',
                    reqd: 1
                }
            ],
            primary_action_label: __('Compare'),
            primary_action: function(values) {
                d.hide();

                frappe.call({
                    method: 'uit_aps.scheduling.reports.report_api.compare_scheduling_runs',
                    args: {
                        run1: values.run1,
                        run2: values.run2
                    },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            let comp = r.message.comparison;
                            let html = `
                                <table class="table table-bordered">
                                    <thead>
                                        <tr>
                                            <th>Metric</th>
                                            <th>${comp.run1.name}</th>
                                            <th>${comp.run2.name}</th>
                                            <th>Difference</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td><strong>Makespan</strong></td>
                                            <td>${comp.run1.makespan || 0} mins</td>
                                            <td>${comp.run2.makespan || 0} mins</td>
                                            <td class="${comp.differences.makespan_diff < 0 ? 'text-success' : 'text-danger'}">
                                                ${comp.differences.makespan_diff > 0 ? '+' : ''}${comp.differences.makespan_diff} mins
                                            </td>
                                        </tr>
                                        <tr>
                                            <td><strong>Late Jobs</strong></td>
                                            <td>${comp.run1.late_jobs || 0}</td>
                                            <td>${comp.run2.late_jobs || 0}</td>
                                            <td class="${comp.differences.late_jobs_diff < 0 ? 'text-success' : 'text-danger'}">
                                                ${comp.differences.late_jobs_diff > 0 ? '+' : ''}${comp.differences.late_jobs_diff}
                                            </td>
                                        </tr>
                                        <tr>
                                            <td><strong>Utilization</strong></td>
                                            <td>${(comp.run1.utilization || 0).toFixed(1)}%</td>
                                            <td>${(comp.run2.utilization || 0).toFixed(1)}%</td>
                                            <td class="${comp.differences.utilization_diff > 0 ? 'text-success' : 'text-danger'}">
                                                ${comp.differences.utilization_diff > 0 ? '+' : ''}${comp.differences.utilization_diff.toFixed(1)}%
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                                <div class="alert alert-info">
                                    <strong>Winner:</strong><br>
                                    Makespan: ${comp.winners.makespan}<br>
                                    Late Jobs: ${comp.winners.late_jobs}<br>
                                    Utilization: ${comp.winners.utilization}
                                </div>
                            `;

                            frappe.msgprint({
                                title: __('Comparison Results'),
                                message: html,
                                indicator: 'blue',
                                wide: true
                            });

                            me.log('Compared ' + values.run1 + ' vs ' + values.run2, 'info');
                        }
                    }
                });
            }
        });
        d.show();
    }

    // =========================================
    // Breakdown Actions
    // =========================================
    simulate_breakdown() {
        let me = this;

        let d = new frappe.ui.Dialog({
            title: __('Simulate Machine Breakdown'),
            fields: [
                {
                    label: __('Workstation'),
                    fieldname: 'workstation',
                    fieldtype: 'Link',
                    options: 'Workstation',
                    reqd: 1
                },
                {
                    label: __('Production Plan'),
                    fieldname: 'production_plan',
                    fieldtype: 'Link',
                    options: 'Production Plan'
                }
            ],
            primary_action_label: __('Simulate'),
            primary_action: function(values) {
                d.hide();
                me.log('Simulating breakdown for ' + values.workstation, 'info');

                frappe.call({
                    method: 'uit_aps.scheduling.api.scheduling_api.simulate_breakdown_scenario',
                    args: {
                        workstation: values.workstation,
                        production_plan: values.production_plan
                    },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            let data = r.message;
                            let impact = data.impact_analysis || {};

                            let html = `
                                <div class="alert alert-warning">
                                    <strong>Simulated Breakdown:</strong> ${data.workstation_name} (${data.workstation})
                                </div>
                                <h5>Impact Analysis</h5>
                                <table class="table table-bordered">
                                    <tr><td>Affected Job Cards</td><td><strong>${impact.affected_job_cards || 0}</strong></td></tr>
                                    <tr><td>Total Duration</td><td><strong>${impact.total_duration_hours || 0} hours</strong></td></tr>
                                </table>
                                <h5>Alternative Workstations</h5>
                                <ul>
                            `;

                            if (data.alternative_workstations && data.alternative_workstations.length > 0) {
                                data.alternative_workstations.forEach(ws => {
                                    html += `<li>${ws.name}: ${ws.workstation_name}</li>`;
                                });
                            } else {
                                html += `<li>No alternatives found</li>`;
                            }

                            html += `</ul><div class="alert alert-info">${data.recommendation}</div>`;

                            frappe.msgprint({
                                title: __('Breakdown Impact Analysis'),
                                message: html,
                                indicator: 'orange',
                                wide: true
                            });

                            me.log('Breakdown simulation completed', 'success');
                        }
                    }
                });
            }
        });
        d.show();
    }

    reschedule_breakdown() {
        let me = this;

        let d = new frappe.ui.Dialog({
            title: __('Reschedule with Exclusions'),
            fields: [
                {
                    label: __('Scheduling Run'),
                    fieldname: 'scheduling_run',
                    fieldtype: 'Link',
                    options: 'APS Scheduling Run',
                    reqd: 1
                },
                {
                    label: __('Broken Workstations (comma-separated)'),
                    fieldname: 'broken_workstations',
                    fieldtype: 'Data',
                    description: __('E.g., WS-CNC-01, WS-LATHE-02')
                },
                {
                    label: __('Time Limit (seconds)'),
                    fieldname: 'time_limit',
                    fieldtype: 'Int',
                    default: 300
                }
            ],
            primary_action_label: __('Reschedule'),
            primary_action: function(values) {
                d.hide();
                me.log('Rescheduling with exclusions...', 'info');

                frappe.call({
                    method: 'uit_aps.scheduling.api.scheduling_api.reschedule_on_breakdown',
                    args: {
                        scheduling_run: values.scheduling_run,
                        broken_workstations: values.broken_workstations,
                        time_limit_seconds: values.time_limit
                    },
                    freeze: true,
                    freeze_message: __('Rescheduling...'),
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            me.log('Reschedule completed: ' + r.message.scheduling_run, 'success');
                            frappe.show_alert({
                                message: __('Reschedule completed! New run: {0}', [r.message.scheduling_run]),
                                indicator: 'green'
                            });
                            me.refresh();
                        } else {
                            me.log('Reschedule failed: ' + (r.message?.error || 'Unknown error'), 'error');
                        }
                    }
                });
            }
        });
        d.show();
    }

    view_affected_operations() {
        let me = this;

        let d = new frappe.ui.Dialog({
            title: __('View Affected Operations'),
            fields: [
                {
                    label: __('Workstations (comma-separated)'),
                    fieldname: 'workstations',
                    fieldtype: 'Data',
                    reqd: 1
                }
            ],
            primary_action_label: __('View'),
            primary_action: function(values) {
                d.hide();

                frappe.call({
                    method: 'uit_aps.scheduling.api.scheduling_api.get_affected_operations',
                    args: {
                        workstations: values.workstations
                    },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            let data = r.message;
                            let html = `
                                <div class="alert alert-warning">
                                    <strong>${data.affected_count}</strong> Job Cards affected
                                </div>
                                <table class="table table-sm">
                                    <thead>
                                        <tr><th>Job Card</th><th>Operation</th><th>Workstation</th><th>Status</th></tr>
                                    </thead>
                                    <tbody>
                            `;

                            if (data.affected_job_cards) {
                                data.affected_job_cards.slice(0, 20).forEach(jc => {
                                    html += `<tr>
                                        <td>${jc.name}</td>
                                        <td>${jc.operation}</td>
                                        <td>${jc.workstation}</td>
                                        <td>${jc.status}</td>
                                    </tr>`;
                                });
                            }

                            html += `</tbody></table>`;

                            frappe.msgprint({
                                title: __('Affected Operations'),
                                message: html,
                                indicator: 'orange',
                                wide: true
                            });

                            me.log('Viewed affected operations', 'info');
                        }
                    }
                });
            }
        });
        d.show();
    }

    // =========================================
    // Report Actions
    // =========================================
    export_excel() {
        let me = this;

        let d = new frappe.ui.Dialog({
            title: __('Export Excel Report'),
            fields: [
                {
                    label: __('Scheduling Run'),
                    fieldname: 'scheduling_run',
                    fieldtype: 'Link',
                    options: 'APS Scheduling Run',
                    reqd: 1
                }
            ],
            primary_action_label: __('Export'),
            primary_action: function(values) {
                d.hide();
                me.export_run_excel(values.scheduling_run);
            }
        });
        d.show();
    }

    export_run_excel(scheduling_run) {
        let me = this;
        me.log('Exporting Excel for ' + scheduling_run, 'info');

        frappe.call({
            method: 'uit_aps.scheduling.reports.report_api.export_comparison_excel',
            args: {
                scheduling_run: scheduling_run
            },
            freeze: true,
            freeze_message: __('Generating Excel report...'),
            callback: function(r) {
                if (r.message && r.message.success) {
                    me.log('Excel exported: ' + r.message.file_name, 'success');
                    window.open(r.message.file_url, '_blank');
                } else {
                    me.log('Export failed: ' + (r.message?.error || 'Unknown error'), 'error');
                    frappe.msgprint({
                        title: __('Export Failed'),
                        message: r.message?.error || __('Failed to export'),
                        indicator: 'red'
                    });
                }
            }
        });
    }

    export_gantt_excel() {
        let me = this;

        let d = new frappe.ui.Dialog({
            title: __('Export Gantt Data'),
            fields: [
                {
                    label: __('Scheduling Run'),
                    fieldname: 'scheduling_run',
                    fieldtype: 'Link',
                    options: 'APS Scheduling Run',
                    reqd: 1
                }
            ],
            primary_action_label: __('Export'),
            primary_action: function(values) {
                d.hide();
                me.log('Exporting Gantt data for ' + values.scheduling_run, 'info');

                frappe.call({
                    method: 'uit_aps.scheduling.reports.report_api.export_gantt_excel',
                    args: {
                        scheduling_run: values.scheduling_run
                    },
                    freeze: true,
                    freeze_message: __('Exporting Gantt data...'),
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            me.log('Gantt data exported', 'success');
                            window.open(r.message.file_url, '_blank');
                        } else {
                            me.log('Export failed', 'error');
                        }
                    }
                });
            }
        });
        d.show();
    }

    view_report_preview() {
        let me = this;

        let d = new frappe.ui.Dialog({
            title: __('Report Preview'),
            fields: [
                {
                    label: __('Scheduling Run'),
                    fieldname: 'scheduling_run',
                    fieldtype: 'Link',
                    options: 'APS Scheduling Run',
                    reqd: 1
                }
            ],
            primary_action_label: __('Preview'),
            primary_action: function(values) {
                d.hide();

                frappe.call({
                    method: 'uit_aps.scheduling.reports.report_api.get_report_preview',
                    args: {
                        scheduling_run: values.scheduling_run
                    },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            let data = r.message;
                            let summary = data.summary || {};
                            let comparison = data.comparison || {};
                            let constraints = data.constraints || {};

                            let html = `
                                <h5>Summary</h5>
                                <table class="table table-bordered table-sm">
                                    <tr><td>Production Plan</td><td>${summary.production_plan}</td></tr>
                                    <tr><td>Status</td><td>${summary.run_status}</td></tr>
                                    <tr><td>Total Job Cards</td><td>${summary.total_job_cards}</td></tr>
                                    <tr><td>Jobs On Time</td><td>${summary.jobs_on_time}</td></tr>
                                    <tr><td>Late Jobs</td><td>${summary.late_jobs}</td></tr>
                                    <tr><td>Makespan</td><td>${summary.makespan_minutes} mins</td></tr>
                                </table>

                                <h5>FIFO vs APS Comparison</h5>
                                <table class="table table-bordered table-sm">
                                    <tr>
                                        <td>Makespan Improvement</td>
                                        <td class="${(comparison.improvement_makespan || 0) > 0 ? 'text-success' : 'text-danger'}">
                                            ${(comparison.improvement_makespan || 0).toFixed(1)}%
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Late Jobs Improvement</td>
                                        <td class="${(comparison.improvement_late_jobs || 0) > 0 ? 'text-success' : 'text-danger'}">
                                            ${(comparison.improvement_late_jobs || 0).toFixed(1)}%
                                        </td>
                                    </tr>
                                </table>

                                <h5>Constraints Applied</h5>
                                <ul>
                                    <li>${constraints.machine_eligibility ? '✅' : '❌'} Machine Eligibility</li>
                                    <li>${constraints.precedence ? '✅' : '❌'} Precedence</li>
                                    <li>${constraints.no_overlap ? '✅' : '❌'} No Overlap</li>
                                    <li>${constraints.working_hours ? '✅' : '❌'} Working Hours</li>
                                    <li>${constraints.due_dates ? '✅' : '❌'} Due Dates</li>
                                    <li>${constraints.setup_time ? '✅' : '❌'} Setup Time</li>
                                </ul>
                            `;

                            frappe.msgprint({
                                title: __('Report Preview: {0}', [values.scheduling_run]),
                                message: html,
                                indicator: 'blue',
                                wide: true
                            });

                            me.log('Viewed report preview', 'info');
                        }
                    }
                });
            }
        });
        d.show();
    }

    print_report() {
        let me = this;

        let d = new frappe.ui.Dialog({
            title: __('Print Report'),
            fields: [
                {
                    label: __('Scheduling Run'),
                    fieldname: 'scheduling_run',
                    fieldtype: 'Link',
                    options: 'APS Scheduling Run',
                    reqd: 1
                }
            ],
            primary_action_label: __('Print'),
            primary_action: function(values) {
                d.hide();
                me.log('Printing report for ' + values.scheduling_run, 'info');

                // Open print view
                let print_url = `/printview?doctype=APS%20Scheduling%20Run&name=${values.scheduling_run}&format=APS%20Scheduling%20Report`;
                window.open(print_url, '_blank');
            }
        });
        d.show();
    }

    // =========================================
    // AI Actions
    // =========================================
    get_ai_analysis() {
        let me = this;

        let d = new frappe.ui.Dialog({
            title: __('Get AI Analysis'),
            fields: [
                {
                    label: __('Scheduling Run'),
                    fieldname: 'scheduling_run',
                    fieldtype: 'Link',
                    options: 'APS Scheduling Run',
                    reqd: 1
                },
                {
                    label: __('Custom Question'),
                    fieldname: 'custom_prompt',
                    fieldtype: 'Small Text',
                    description: __('Leave empty for default analysis')
                },
                {
                    label: __('Language'),
                    fieldname: 'language',
                    fieldtype: 'Select',
                    options: 'vi\nen',
                    default: 'vi'
                }
            ],
            primary_action_label: __('Analyze'),
            primary_action: function(values) {
                d.hide();
                me.log('Getting AI analysis...', 'info');

                frappe.call({
                    method: 'uit_aps.scheduling.llm.llm_api.get_scheduling_advice',
                    args: {
                        scheduling_run: values.scheduling_run,
                        language: values.language,
                        custom_prompt: values.custom_prompt
                    },
                    freeze: true,
                    freeze_message: __('Getting AI analysis from OpenAI...'),
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            me.log('AI analysis completed', 'success');
                            frappe.msgprint({
                                title: __('AI Analysis'),
                                message: r.message.raw_response,
                                indicator: 'green',
                                wide: true
                            });
                        } else {
                            me.log('AI analysis failed: ' + (r.message?.error || 'Unknown error'), 'error');
                        }
                    }
                });
            }
        });
        d.show();
    }

    predict_bottlenecks() {
        let me = this;

        let d = new frappe.ui.Dialog({
            title: __('Predict Bottlenecks'),
            fields: [
                {
                    label: __('Scheduling Run'),
                    fieldname: 'scheduling_run',
                    fieldtype: 'Link',
                    options: 'APS Scheduling Run',
                    reqd: 1
                }
            ],
            primary_action_label: __('Predict'),
            primary_action: function(values) {
                d.hide();
                me.log('Predicting bottlenecks...', 'info');

                frappe.call({
                    method: 'uit_aps.scheduling.gnn.gnn_api.predict_bottlenecks',
                    args: {
                        scheduling_run: values.scheduling_run
                    },
                    freeze: true,
                    freeze_message: __('Analyzing with GNN...'),
                    callback: function(r) {
                        if (r.message) {
                            me.log('Bottleneck prediction completed', 'success');

                            let html = `<h5>Bottlenecks Detected: ${r.message.summary?.num_bottlenecks || 0}</h5>`;

                            if (r.message.bottlenecks && r.message.bottlenecks.length > 0) {
                                html += '<table class="table table-sm"><thead><tr><th>Machine</th><th>Probability</th></tr></thead><tbody>';
                                r.message.bottlenecks.forEach(b => {
                                    html += `<tr><td>${b.machine_id}</td><td>${(b.bottleneck_probability * 100).toFixed(0)}%</td></tr>`;
                                });
                                html += '</tbody></table>';
                            }

                            frappe.msgprint({
                                title: __('Bottleneck Prediction'),
                                message: html,
                                indicator: r.message.bottlenecks?.length > 0 ? 'orange' : 'green'
                            });
                        }
                    }
                });
            }
        });
        d.show();
    }

    train_rl_agent() {
        let me = this;

        let d = new frappe.ui.Dialog({
            title: __('Train RL Agent'),
            fields: [
                {
                    label: __('Scheduling Run'),
                    fieldname: 'scheduling_run',
                    fieldtype: 'Link',
                    options: 'APS Scheduling Run',
                    reqd: 1
                },
                {
                    label: __('Agent Type'),
                    fieldname: 'agent_type',
                    fieldtype: 'Select',
                    options: 'ppo\nsac',
                    default: 'ppo'
                },
                {
                    label: __('Episodes'),
                    fieldname: 'max_episodes',
                    fieldtype: 'Int',
                    default: 100
                }
            ],
            primary_action_label: __('Start Training'),
            primary_action: function(values) {
                d.hide();
                me.log('Starting RL training...', 'info');

                frappe.call({
                    method: 'uit_aps.scheduling.rl.training_api.start_training',
                    args: {
                        scheduling_run: values.scheduling_run,
                        agent_type: values.agent_type,
                        max_episodes: values.max_episodes,
                        run_in_background: true
                    },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            me.log('Training started in background', 'success');
                            frappe.show_alert({
                                message: __('Training started in background'),
                                indicator: 'blue'
                            });
                        } else {
                            me.log('Training failed to start', 'error');
                        }
                    }
                });
            }
        });
        d.show();
    }
}
