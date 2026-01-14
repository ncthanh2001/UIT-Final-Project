# MÔ TẢ CẤU TRÚC BẢNG DỮ LIỆU

## Hệ thống UIT APS - Advanced Planning & Scheduling

---

## PHẦN 1: CÁC BẢNG ERPNEXT LIÊN QUAN

### 1.1. Bảng tabCompany (Công ty)

Bảng lưu trữ thông tin các công ty trong hệ thống ERPNext.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính, mã định danh công ty |
| 2 | company_name | VARCHAR(140) | Tên đầy đủ của công ty |
| 3 | abbr | VARCHAR(140) | Tên viết tắt của công ty |
| 4 | default_currency | VARCHAR(140) | Đơn vị tiền tệ mặc định |
| 5 | country | VARCHAR(140) | Quốc gia của công ty |
| 6 | default_warehouse | VARCHAR(140) | FK - Kho mặc định của công ty |
| 7 | cost_center | VARCHAR(140) | Trung tâm chi phí mặc định |
| 8 | default_holiday_list | VARCHAR(140) | Danh sách ngày nghỉ mặc định |
| 9 | creation | DATETIME(6) | Thời điểm tạo bản ghi |
| 10 | modified | DATETIME(6) | Thời điểm cập nhật cuối |

---

### 1.2. Bảng tabUser (Người dùng)

Bảng lưu trữ thông tin người dùng hệ thống, dùng để xác định ai thực hiện các thao tác trong APS.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính, email của người dùng |
| 2 | full_name | VARCHAR(140) | Họ và tên đầy đủ |
| 3 | first_name | VARCHAR(140) | Tên |
| 4 | last_name | VARCHAR(140) | Họ |
| 5 | email | VARCHAR(140) | Địa chỉ email |
| 6 | enabled | TINYINT(1) | Trạng thái kích hoạt (0/1) |
| 7 | user_type | VARCHAR(140) | Loại người dùng (System User, Website User) |
| 8 | role_profile_name | VARCHAR(140) | Hồ sơ quyền của người dùng |
| 9 | creation | DATETIME(6) | Thời điểm tạo tài khoản |
| 10 | last_login | DATETIME(6) | Thời điểm đăng nhập cuối |

---

### 1.3. Bảng tabSupplier (Nhà cung cấp)

Bảng lưu trữ thông tin nhà cung cấp, dùng trong module MRP để đề xuất mua hàng.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính, mã nhà cung cấp |
| 2 | supplier_name | VARCHAR(140) | Tên nhà cung cấp |
| 3 | supplier_group | VARCHAR(140) | FK - Nhóm nhà cung cấp |
| 4 | supplier_type | VARCHAR(140) | Loại nhà cung cấp (Company/Individual) |
| 5 | country | VARCHAR(140) | Quốc gia |
| 6 | default_currency | VARCHAR(140) | Đơn vị tiền tệ mặc định |
| 7 | default_price_list | VARCHAR(140) | Bảng giá mặc định |
| 8 | lead_time_days | INT(11) | Thời gian giao hàng trung bình (ngày) |
| 9 | disabled | TINYINT(1) | Trạng thái vô hiệu hóa (0/1) |
| 10 | creation | DATETIME(6) | Thời điểm tạo bản ghi |

---

### 1.4. Bảng tabWarehouse (Kho hàng)

Bảng lưu trữ thông tin kho hàng, dùng để theo dõi tồn kho trong dự báo và MRP.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính, mã kho (dạng phân cấp) |
| 2 | warehouse_name | VARCHAR(140) | Tên kho hàng |
| 3 | company | VARCHAR(140) | FK - Công ty sở hữu kho |
| 4 | parent_warehouse | VARCHAR(140) | FK - Kho cha (cấu trúc phân cấp) |
| 5 | warehouse_type | VARCHAR(140) | Loại kho (Stores/Manufacturing/Transit) |
| 6 | is_group | TINYINT(1) | Có phải kho nhóm không (0/1) |
| 7 | disabled | TINYINT(1) | Trạng thái vô hiệu hóa (0/1) |
| 8 | account | VARCHAR(140) | Tài khoản kế toán liên kết |
| 9 | creation | DATETIME(6) | Thời điểm tạo bản ghi |
| 10 | modified | DATETIME(6) | Thời điểm cập nhật cuối |

---

## PHẦN 2: CÁC BẢNG ERPNEXT SẢN XUẤT

### 2.1. Bảng tabItem (Sản phẩm/Vật tư)

Bảng lưu trữ thông tin sản phẩm và nguyên vật liệu, là bảng trung tâm của hệ thống.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính, mã sản phẩm |
| 2 | item_name | VARCHAR(140) | Tên sản phẩm |
| 3 | item_group | VARCHAR(140) | FK - Nhóm sản phẩm |
| 4 | stock_uom | VARCHAR(140) | Đơn vị tính tồn kho |
| 5 | is_stock_item | TINYINT(1) | Có quản lý tồn kho không |
| 6 | default_bom | VARCHAR(140) | FK - BOM mặc định |
| 7 | default_warehouse | VARCHAR(140) | FK - Kho mặc định |
| 8 | lead_time_days | INT(11) | Thời gian sản xuất/mua hàng (ngày) |
| 9 | safety_stock | DECIMAL(21,9) | Mức tồn kho an toàn |
| 10 | disabled | TINYINT(1) | Trạng thái vô hiệu hóa |

---

### 2.2. Bảng tabBOM (Bill of Materials - Định mức nguyên vật liệu)

Bảng lưu trữ định mức nguyên vật liệu và công đoạn sản xuất cho mỗi sản phẩm.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính, mã BOM |
| 2 | item | VARCHAR(140) | FK - Sản phẩm đầu ra |
| 3 | quantity | DECIMAL(21,9) | Số lượng sản phẩm đầu ra |
| 4 | is_active | TINYINT(1) | BOM có đang hoạt động |
| 5 | is_default | TINYINT(1) | Có phải BOM mặc định |
| 6 | company | VARCHAR(140) | FK - Công ty |
| 7 | with_operations | TINYINT(1) | BOM có công đoạn sản xuất |
| 8 | operating_cost | DECIMAL(21,9) | Chi phí vận hành |
| 9 | raw_material_cost | DECIMAL(21,9) | Chi phí nguyên vật liệu |
| 10 | total_cost | DECIMAL(21,9) | Tổng chi phí |

---

### 2.3. Bảng tabWorkstation (Máy/Trạm làm việc)

Bảng lưu trữ thông tin máy móc và trạm làm việc trong nhà máy, là đối tượng chính của lập lịch.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính, mã máy |
| 2 | workstation_name | VARCHAR(140) | Tên máy/trạm làm việc |
| 3 | production_capacity | DECIMAL(21,9) | Công suất sản xuất |
| 4 | hour_rate | DECIMAL(21,9) | Chi phí vận hành theo giờ |
| 5 | hour_rate_electricity | DECIMAL(21,9) | Chi phí điện theo giờ |
| 6 | hour_rate_labour | DECIMAL(21,9) | Chi phí nhân công theo giờ |
| 7 | working_hours | TEXT | Giờ làm việc (child table) |
| 8 | holiday_list | VARCHAR(140) | FK - Danh sách ngày nghỉ |
| 9 | description | TEXT | Mô tả máy |
| 10 | disabled | TINYINT(1) | Trạng thái vô hiệu hóa |

---

### 2.4. Bảng tabOperation (Công đoạn sản xuất)

Bảng lưu trữ các công đoạn sản xuất, định nghĩa các bước trong quy trình sản xuất.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính, mã công đoạn |
| 2 | workstation | VARCHAR(140) | FK - Máy thực hiện công đoạn |
| 3 | description | TEXT | Mô tả công đoạn |
| 4 | batch_size | INT(11) | Kích thước lô sản xuất |
| 5 | quality_inspection_template | VARCHAR(140) | Mẫu kiểm tra chất lượng |
| 6 | is_corrective_operation | TINYINT(1) | Có phải công đoạn sửa chữa |
| 7 | sub_operations | TEXT | Các công đoạn con |
| 8 | creation | DATETIME(6) | Thời điểm tạo |
| 9 | modified | DATETIME(6) | Thời điểm cập nhật |
| 10 | disabled | TINYINT(1) | Trạng thái vô hiệu hóa |

---

### 2.5. Bảng tabProduction Plan (Kế hoạch sản xuất ERPNext)

Bảng lưu trữ kế hoạch sản xuất gốc từ ERPNext, là đầu vào cho APS Scheduling.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính, mã kế hoạch |
| 2 | company | VARCHAR(140) | FK - Công ty |
| 3 | posting_date | DATE | Ngày lập kế hoạch |
| 4 | status | VARCHAR(140) | Trạng thái (Draft/Submitted/...) |
| 5 | get_items_from | VARCHAR(140) | Nguồn lấy sản phẩm (Sales Order/MRP) |
| 6 | total_planned_qty | DECIMAL(21,9) | Tổng số lượng kế hoạch |
| 7 | total_produced_qty | DECIMAL(21,9) | Tổng số lượng đã sản xuất |
| 8 | for_warehouse | VARCHAR(140) | FK - Kho đích |
| 9 | from_date | DATE | Ngày bắt đầu kế hoạch |
| 10 | to_date | DATE | Ngày kết thúc kế hoạch |

---

### 2.6. Bảng tabWork Order (Lệnh sản xuất)

Bảng lưu trữ lệnh sản xuất, được tạo từ Production Plan.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính, mã lệnh sản xuất |
| 2 | production_plan | VARCHAR(140) | FK - Kế hoạch sản xuất |
| 3 | production_item | VARCHAR(140) | FK - Sản phẩm cần sản xuất |
| 4 | bom_no | VARCHAR(140) | FK - BOM sử dụng |
| 5 | qty | DECIMAL(21,9) | Số lượng cần sản xuất |
| 6 | produced_qty | DECIMAL(21,9) | Số lượng đã sản xuất |
| 7 | status | VARCHAR(140) | Trạng thái (Draft/In Process/Completed) |
| 8 | planned_start_date | DATETIME(6) | Ngày bắt đầu dự kiến |
| 9 | planned_end_date | DATETIME(6) | Ngày kết thúc dự kiến |
| 10 | expected_delivery_date | DATE | Ngày giao hàng dự kiến |

---

### 2.7. Bảng tabJob Card (Phiếu công việc)

Bảng lưu trữ phiếu công việc cho từng công đoạn, là đối tượng chính được APS lập lịch.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính, mã phiếu công việc |
| 2 | work_order | VARCHAR(140) | FK - Lệnh sản xuất |
| 3 | operation | VARCHAR(140) | FK - Công đoạn thực hiện |
| 4 | workstation | VARCHAR(140) | FK - Máy thực hiện |
| 5 | for_quantity | DECIMAL(21,9) | Số lượng cần hoàn thành |
| 6 | total_completed_qty | DECIMAL(21,9) | Số lượng đã hoàn thành |
| 7 | status | VARCHAR(140) | Trạng thái (Open/Work In Progress/Completed) |
| 8 | time_required | DECIMAL(21,9) | Thời gian yêu cầu (phút) |
| 9 | started_time | DATETIME(6) | Thời điểm bắt đầu thực tế |
| 10 | total_time_in_mins | DECIMAL(21,9) | Tổng thời gian thực tế (phút) |

---

## PHẦN 3: CÁC BẢNG UIT APS

### 3.1. Bảng tabAPS Scheduling Run (Lịch sử chạy lập lịch)

Bảng lưu trữ thông tin mỗi lần chạy lập lịch sản xuất bằng OR-Tools hoặc RL Agent.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính, mã lần chạy |
| 2 | production_plan | VARCHAR(140) | FK - Kế hoạch sản xuất ERPNext |
| 3 | run_status | VARCHAR(140) | Trạng thái (Pending/Running/Pending Approval/Applied/Completed/Failed) |
| 4 | scheduling_strategy | VARCHAR(140) | Chiến lược lập lịch (Forward Scheduling/Backward Scheduling/Priority Based/EDD) |
| 5 | scheduling_tier | VARCHAR(140) | Tier sử dụng (Tier 1 - OR-Tools/Tier 2 - RL Agent/Tier 3 - GNN) |
| 6 | run_date | DATETIME(6) | Thời điểm chạy lập lịch |
| 7 | executed_by | VARCHAR(140) | FK - Người thực hiện (User) |
| 8 | total_operations | INT(11) | Tổng số operations được khuyến nghị |
| 9 | applied_operations | INT(11) | Số operations đã áp dụng |
| 10 | applied_at | DATETIME(6) | Thời điểm áp dụng lịch |
| 11 | applied_by | VARCHAR(140) | FK - Người áp dụng (User) |
| 12 | constraint_machine_eligibility | TINYINT(1) | Ràng buộc máy phù hợp với operation |
| 13 | constraint_precedence | TINYINT(1) | Ràng buộc thứ tự công đoạn |
| 14 | constraint_no_overlap | TINYINT(1) | Ràng buộc không chồng chéo trên máy |
| 15 | constraint_working_hours | TINYINT(1) | Ràng buộc giờ làm việc |
| 16 | constraint_due_dates | TINYINT(1) | Ràng buộc deadline |
| 17 | constraint_setup_time | TINYINT(1) | Ràng buộc thời gian setup |
| 18 | constraints_description | TEXT | Mô tả chi tiết các ràng buộc |
| 19 | baseline_makespan_minutes | INT(11) | Makespan khi lập lịch theo FIFO (baseline) |
| 20 | baseline_late_jobs | INT(11) | Số job trễ khi dùng FIFO |
| 21 | baseline_total_tardiness | INT(11) | Tổng độ trễ khi dùng FIFO |
| 22 | improvement_makespan_percent | DECIMAL(21,9) | % cải thiện makespan so với FIFO |
| 23 | improvement_late_jobs_percent | DECIMAL(21,9) | % giảm số job trễ so với FIFO |
| 24 | improvement_tardiness_percent | DECIMAL(21,9) | % giảm tổng độ trễ so với FIFO |
| 25 | comparison_summary | TEXT | Tóm tắt so sánh hiệu quả tối ưu hóa |
| 26 | time_limit_seconds | INT(11) | Giới hạn thời gian solver (giây) |
| 27 | min_gap_between_ops | INT(11) | Khoảng cách tối thiểu giữa các operations (phút) |
| 28 | makespan_weight | DECIMAL(21,9) | Trọng số cho mục tiêu makespan |
| 29 | tardiness_weight | DECIMAL(21,9) | Trọng số cho phạt trễ hạn |
| 30 | total_job_cards | INT(11) | Tổng số Job Card được lập lịch |
| 31 | total_late_jobs | INT(11) | Số Job Card có nguy cơ trễ hạn |
| 32 | jobs_on_time | INT(11) | Số job đúng hạn |
| 33 | solver_status | VARCHAR(140) | Trạng thái solver (Not Started/Running/Optimal/Feasible/Infeasible/Timeout/Error) |
| 34 | solve_time_seconds | DECIMAL(21,9) | Thời gian chạy solver (giây) |
| 35 | gap_percentage | DECIMAL(21,9) | Gap so với lời giải tối ưu (%) |
| 36 | makespan_minutes | INT(11) | Tổng makespan của lịch trình (phút) |
| 37 | total_tardiness_minutes | INT(11) | Tổng độ trễ (phút) |
| 38 | machine_utilization | DECIMAL(21,9) | Hiệu suất sử dụng máy trung bình (%) |
| 39 | llm_analysis_prompt | TEXT | Prompt gửi cho AI phân tích |
| 40 | llm_analysis_language | VARCHAR(140) | Ngôn ngữ phân tích (vi/en) |
| 41 | llm_analysis_date | DATETIME(6) | Thời điểm phân tích AI |
| 42 | llm_analysis_model | VARCHAR(140) | Model AI sử dụng |
| 43 | llm_analysis_content | LONGTEXT | Nội dung phân tích và khuyến nghị AI |
| 44 | notes | TEXT | Ghi chú |

---

### 3.2. Bảng tabAPS Scheduling Result (Kết quả lập lịch)

Bảng lưu trữ kết quả lập lịch chi tiết cho từng Job Card.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính |
| 2 | scheduling_run | VARCHAR(140) | FK - Lần chạy lập lịch (APS Scheduling Run) |
| 3 | job_card | VARCHAR(140) | FK - Phiếu công việc (Job Card) |
| 4 | workstation | VARCHAR(140) | FK - Máy được phân bổ (Workstation) |
| 5 | operation | VARCHAR(140) | FK - Công đoạn thực hiện (Operation) |
| 6 | planned_start_time | DATETIME(6) | Thời điểm bắt đầu theo lịch khuyến nghị |
| 7 | planned_end_time | DATETIME(6) | Thời điểm kết thúc theo lịch khuyến nghị |
| 8 | work_shift | VARCHAR(140) | FK - Ca làm việc (APS Work Shift) |
| 9 | is_applied | TINYINT(1) | Đánh dấu khuyến nghị đã được áp dụng vào Job Card |
| 10 | applied_at | DATETIME(6) | Thời điểm áp dụng khuyến nghị |
| 11 | is_late | TINYINT(1) | Đánh dấu Job Card bị trễ so với kế hoạch |
| 12 | delay_reason | TEXT | Lý do trễ (nếu is_late = 1) |
| 13 | remarks | TEXT | Ghi chú |

---

### 3.3. Bảng tabAPS Work Shift (Ca làm việc)

Bảng định nghĩa các ca làm việc trong nhà máy, được sử dụng trong ràng buộc lập lịch.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính |
| 2 | shift_name | VARCHAR(140) | Tên ca làm việc (ví dụ: Ca sáng, Ca chiều, Ca đêm) |
| 3 | start_time | TIME(6) | Giờ bắt đầu ca làm việc |
| 4 | end_time | TIME(6) | Giờ kết thúc ca làm việc |
| 5 | working_hours | DECIMAL(21,9) | Tổng số giờ làm việc của ca (tự động tính) |
| 6 | is_night_shift | TINYINT(1) | Đánh dấu ca đêm (qua ngày hôm sau) |
| 7 | is_active | TINYINT(1) | Trạng thái hoạt động của ca |
| 8 | remarks | TEXT | Ghi chú |

---

### 3.4. Bảng tabAPS Forecast History (Lịch sử dự báo)

Bảng lưu trữ thông tin mỗi lần chạy dự báo nhu cầu sử dụng các model ML (ARIMA, Prophet, Linear Regression).

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính, mã lần chạy dự báo (format: FCST-RUN-YYYY-MM-DD-####) |
| 2 | run_name | VARCHAR(140) | Tên lần chạy dự báo |
| 3 | company | VARCHAR(140) | FK - Công ty (Company) |
| 4 | model_used | VARCHAR(140) | Model ML sử dụng (ARIMA/Linear Regression/Prophet) |
| 5 | run_status | VARCHAR(140) | Trạng thái (Pending/Running/Complete/Failed) |
| 6 | run_start_time | DATETIME(6) | Thời điểm bắt đầu chạy |
| 7 | run_end_time | DATETIME(6) | Thời điểm kết thúc chạy |
| 8 | forecast_horizon_days | INT(11) | Số ngày dự báo |
| 9 | start_date | DATE | Ngày bắt đầu kỳ dự báo |
| 10 | end_date | DATE | Ngày kết thúc kỳ dự báo |
| 11 | training_period_start | DATE | Ngày bắt đầu của dữ liệu training |
| 12 | training_period_end | DATE | Ngày kết thúc của dữ liệu training |
| 13 | total_sales_orders_used | INT(11) | Tổng số Sales Orders đã sử dụng |
| 14 | total_items_forecasted | INT(11) | Tổng số items đã dự báo |
| 15 | total_results_generated | INT(11) | Tổng số kết quả đã tạo |
| 16 | successful_forecasts | INT(11) | Số forecast thành công |
| 17 | failed_forecasts | INT(11) | Số forecast thất bại |
| 18 | overall_accuracy_mape_ | DECIMAL(21,9) | Độ chính xác tổng thể (MAPE %) |
| 19 | avg_confidence_score | DECIMAL(21,9) | Điểm tin cậy trung bình của tất cả forecast (%) |
| 20 | model_recommended | VARCHAR(140) | Model được khuyến nghị sử dụng |
| 21 | parameters_json | LONGTEXT | Các tham số được sử dụng khi chạy forecast (JSON format) |
| 22 | filters_applied | LONGTEXT | Các bộ lọc được áp dụng (item_group, warehouse, etc.) |
| 23 | forecast_results_summary | - | Child Table - Bảng tổng hợp các kết quả forecast (APS Forecast History Item) |
| 24 | ai_analysis | LONGTEXT | Phân tích tổng thể bằng AI cho lần chạy dự báo này |

---

### 3.4.1. Bảng tabAPS Forecast History Item (Chi tiết tóm tắt dự báo - Child Table)

Bảng con lưu trữ tóm tắt kết quả dự báo theo từng item trong APS Forecast History.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính |
| 2 | parent | VARCHAR(140) | FK - Bản ghi cha (APS Forecast History) |
| 3 | parentfield | VARCHAR(140) | Tên field trong bản ghi cha |
| 4 | parenttype | VARCHAR(140) | Loại DocType cha |
| 5 | idx | INT(11) | Thứ tự dòng trong bảng |
| 6 | item | VARCHAR(140) | FK - Sản phẩm (Item) |
| 7 | item_name | VARCHAR(140) | Tên sản phẩm (fetch từ Item) |
| 8 | forecast_qty | DECIMAL(21,9) | Số lượng dự báo |
| 9 | confidence_score | DECIMAL(21,9) | Điểm tin cậy (%) |
| 10 | movement_type | VARCHAR(140) | Phân loại tốc độ tiêu thụ (Fast Moving/Slow Moving/Non Moving) |
| 11 | reorder_alert | TINYINT(1) | Cảnh báo cần đặt hàng lại |

---

### 3.5. Bảng tabAPS Forecast Result (Kết quả dự báo)

Bảng lưu trữ kết quả dự báo chi tiết cho từng sản phẩm, bao gồm các tham số model và khuyến nghị tồn kho.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính (format: FCST-{item}-YYYY-MM-DD-####) |
| 2 | item | VARCHAR(140) | FK - Sản phẩm được dự báo (Item) |
| 3 | item_group | VARCHAR(140) | FK - Nhóm sản phẩm (fetch từ Item) |
| 4 | forecast_period | DATE | Khoảng thời gian áp dụng kết quả dự báo |
| 5 | forecast_history | VARCHAR(140) | FK - Lần chạy dự báo (APS Forecast History) |
| 6 | forecast_qty | DECIMAL(21,9) | Số lượng nhu cầu dự báo cho sản phẩm |
| 7 | confidence_score | DECIMAL(21,9) | Mức độ tin cậy tổng thể của kết quả dự báo (%) |
| 8 | model_used | VARCHAR(140) | Model được sử dụng để dự báo (ARIMA/Linear Regression/Prophet) |
| 9 | model_confidence | VARCHAR(140) | Chỉ số độ tin cậy của model (R², AIC, etc.) |
| 10 | training_data_points | INT(11) | Số lượng data points được dùng để train model |
| 11 | movement_type | VARCHAR(140) | Phân loại tốc độ tiêu thụ (Fast Moving/Slow Moving/Non Moving) |
| 12 | daily_avg_consumption | DECIMAL(21,9) | Tiêu thụ trung bình hàng ngày (units/day) |
| 13 | trend_type | VARCHAR(140) | Xu hướng tiêu thụ (Upward/Downward/Stable) |
| 14 | lower_bound | DECIMAL(21,9) | Giá trị dự báo thấp nhất (biên dưới) |
| 15 | upper_bound | DECIMAL(21,9) | Giá trị dự báo cao nhất (biên trên) |
| 16 | reorder_level | DECIMAL(21,9) | Mức tồn kho tối thiểu để đặt hàng lại |
| 17 | suggested_qty | INT(11) | Số lượng đề xuất đặt hàng |
| 18 | safety_stock | DECIMAL(21,9) | Tồn kho an toàn |
| 19 | current_stock | DECIMAL(21,9) | Tồn kho hiện tại khi chạy forecast |
| 20 | reorder_alert | TINYINT(1) | Cảnh báo cần đặt hàng ngay |
| 21 | warehouse | VARCHAR(140) | FK - Kho lưu trữ (Warehouse) |
| 22 | company | VARCHAR(140) | FK - Công ty (Company) |
| 23 | arima_p | INT(11) | ARIMA parameter p (AR order) - chỉ khi model_used='ARIMA' |
| 24 | arima_d | INT(11) | ARIMA parameter d (Differencing) - chỉ khi model_used='ARIMA' |
| 25 | arima_q | INT(11) | ARIMA parameter q (MA order) - chỉ khi model_used='ARIMA' |
| 26 | arima_aic | DECIMAL(21,9) | AIC Score (lower is better) - chỉ khi model_used='ARIMA' |
| 27 | lr_r2_score | DECIMAL(21,9) | R² Score - độ chính xác của model (0-100%) - chỉ khi model_used='Linear Regression' |
| 28 | lr_slope | DECIMAL(21,9) | Trend Slope - hệ số góc đường trend - chỉ khi model_used='Linear Regression' |
| 29 | prophet_seasonality_detected | TINYINT(1) | Đã phát hiện tính mùa vụ - chỉ khi model_used='Prophet' |
| 30 | prophet_seasonality_type | VARCHAR(140) | Loại mùa vụ (Weekly/Monthly/Yearly/Multiple) - chỉ khi model_used='Prophet' |
| 31 | prophet_changepoint_count | INT(11) | Số điểm thay đổi xu hướng - chỉ khi model_used='Prophet' |
| 32 | forecast_explanation | LONGTEXT | Giải thích chi tiết về kết quả dự báo |
| 33 | recommendations | LONGTEXT | Các khuyến nghị hành động |
| 34 | notes | LONGTEXT | Ghi chú thêm |

---

### 3.6. Bảng tabAPS Production Plan (Kế hoạch sản xuất APS)

Bảng lưu trữ kế hoạch sản xuất được tạo từ kết quả dự báo hoặc Sales Order.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính |
| 2 | plan_name | VARCHAR(140) | Tên kế hoạch sản xuất (ví dụ: Kế hoạch Q1–Q2/2025) |
| 3 | company | VARCHAR(140) | FK - Công ty (Company) |
| 4 | forecast_history | VARCHAR(140) | FK - Lần chạy dự đoán được dùng để tạo kế hoạch (APS Forecast History) |
| 5 | plan_from_period | DATE | Kỳ bắt đầu của kế hoạch (ví dụ: đầu Q1) |
| 6 | plan_to_period | DATE | Kỳ kết thúc của kế hoạch (ví dụ: cuối Q2) |
| 7 | source_type | VARCHAR(140) | Nguồn dữ liệu tạo kế hoạch (Forecast/Sales Order/Manual) |
| 8 | time_granularity | VARCHAR(140) | Độ phân giải thời gian của kế hoạch (Monthly/Quarterly) |
| 9 | status | VARCHAR(140) | Trạng thái (Draft/Planned/Released/Completed/Cancelled) |
| 10 | capacity_status | VARCHAR(140) | Tình trạng năng lực tổng thể so với kế hoạch (Unknown/OK/Overloaded) |
| 11 | remarks | TEXT | Ghi chú hoặc giải thích thêm cho kế hoạch |
| 12 | items | - | Child Table - Danh sách các sản phẩm trong kế hoạch (APS Production Plan Item) |

---

### 3.6.1. Bảng tabAPS Production Plan Item (Chi tiết kế hoạch sản xuất - Child Table)

Bảng con lưu trữ chi tiết các sản phẩm trong kế hoạch sản xuất APS.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính |
| 2 | parent | VARCHAR(140) | FK - Bản ghi cha (APS Production Plan) |
| 3 | parentfield | VARCHAR(140) | Tên field trong bản ghi cha |
| 4 | parenttype | VARCHAR(140) | Loại DocType cha |
| 5 | idx | INT(11) | Thứ tự dòng trong bảng |
| 6 | item | VARCHAR(140) | FK - Sản phẩm (Item) |
| 7 | plan_period | DATE | Kỳ kế hoạch tương ứng (ví dụ: đầu quý) |
| 8 | planned_qty | DECIMAL(21,9) | Số lượng sản xuất dự kiến cho sản phẩm trong kỳ này |
| 9 | forecast_result | VARCHAR(140) | FK - Tham chiếu tới kết quả dự đoán tương ứng (APS Forecast Result) |
| 10 | safety_stock | DECIMAL(21,9) | Tồn kho an toàn được cộng thêm (nếu có) |
| 11 | forecast_quantiy | DECIMAL(21,9) | Số lượng dự báo gốc |
| 12 | current_stock | DECIMAL(21,9) | Tồn kho hiện tại |
| 13 | planned_start_date | DATE | Ngày bắt đầu sản xuất |
| 14 | lead_time_days | DECIMAL(21,9) | Thời gian sản xuất (ngày) |

---

### 3.7. Bảng tabAPS MRP Run (Lịch sử chạy MRP)

Bảng lưu trữ thông tin mỗi lần chạy MRP (Material Requirement Planning) dựa trên kế hoạch sản xuất.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính |
| 2 | production_plan | VARCHAR(140) | FK - Kế hoạch sản xuất được dùng để chạy MRP (APS Production Plan) |
| 3 | run_status | VARCHAR(140) | Trạng thái (Pending/Running/Completed/Failed) |
| 4 | run_date | DATETIME(6) | Thời điểm chạy MRP |
| 5 | executed_by | VARCHAR(140) | FK - Người thực hiện (User) |
| 6 | total_materials | INT(11) | Số dòng nguyên vật liệu bị thiếu |
| 7 | notes | TEXT | Ghi chú |

---

### 3.8. Bảng tabAPS MRP Result (Kết quả MRP)

Bảng lưu trữ kết quả tính toán nhu cầu nguyên vật liệu từ mỗi lần chạy MRP.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính |
| 2 | mrp_run | VARCHAR(140) | FK - Lần chạy MRP (APS MRP Run) |
| 3 | material_item | VARCHAR(140) | FK - Nguyên vật liệu (Item) |
| 4 | source_plan_item | VARCHAR(140) | FK - Dòng kế hoạch sản xuất gây ra nhu cầu vật tư (APS Production Plan Item) |
| 5 | required_qty | DECIMAL(21,9) | Tổng nhu cầu nguyên vật liệu |
| 6 | available_qty | DECIMAL(21,9) | Tồn kho hiện tại tại thời điểm chạy MRP (snapshot) |
| 7 | shortage_qty | DECIMAL(21,9) | Số lượng nguyên vật liệu bị thiếu |
| 8 | required_date | DATE | Ngày nguyên vật liệu cần có để kịp tiến độ sản xuất |
| 9 | remarks | TEXT | Ghi chú |

---

### 3.9. Bảng tabAPS Purchase Suggestion (Đề xuất mua hàng)

Bảng lưu trữ các đề xuất mua hàng được tạo từ kết quả MRP để đảm bảo đủ nguyên vật liệu cho sản xuất.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính |
| 2 | mrp_run | VARCHAR(140) | FK - Lần chạy MRP (APS MRP Run) |
| 3 | material_item | VARCHAR(140) | FK - Vật tư cần mua (Item) |
| 4 | purchase_qty | DECIMAL(21,9) | Số lượng đề xuất mua |
| 5 | required_date | DATE | Ngày cần có vật tư để đảm bảo tiến độ sản xuất |
| 6 | supplier | VARCHAR(140) | FK - Nhà cung cấp đề xuất (Supplier) |
| 7 | unit_price | DECIMAL(21,9) | Đơn giá |
| 8 | lead_time | INT(11) | Thời gian giao hàng (ngày) |
| 9 | suggestion_status | VARCHAR(140) | Trạng thái (Draft/Approved/Ordered/Rejected) |
| 10 | notes | TEXT | Ghi chú |

---

### 3.10. Bảng tabAPS RL Training Log (Log huấn luyện RL)

Bảng lưu trữ thông tin huấn luyện Reinforcement Learning agent cho module lập lịch (Tier 2).

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | name | VARCHAR(140) | Khóa chính |
| 2 | scheduling_run | VARCHAR(140) | FK - Lần chạy lập lịch liên quan (APS Scheduling Run) |
| 3 | agent_type | VARCHAR(140) | Loại agent (ppo/sac) |
| 4 | training_status | VARCHAR(140) | Trạng thái (Pending/Running/Completed/Failed/Cancelled) |
| 5 | started_at | DATETIME(6) | Thời điểm bắt đầu huấn luyện |
| 6 | completed_at | DATETIME(6) | Thời điểm hoàn thành huấn luyện |
| 7 | total_duration_seconds | DECIMAL(21,9) | Tổng thời gian huấn luyện (giây) |
| 8 | max_episodes | INT(11) | Số episode tối đa |
| 9 | learning_rate | DECIMAL(21,9) | Tốc độ học |
| 10 | gamma | DECIMAL(21,9) | Discount Factor (Gamma) |
| 11 | hidden_sizes | VARCHAR(140) | Kích thước các hidden layer (JSON array, ví dụ: [256, 256]) |
| 12 | batch_size | INT(11) | Batch size |
| 13 | current_episode | INT(11) | Episode hiện tại |
| 14 | progress_percentage | DECIMAL(21,9) | Tiến độ huấn luyện (%) |
| 15 | episodes_per_second | DECIMAL(21,9) | Tốc độ huấn luyện (episodes/giây) |
| 16 | estimated_time_remaining | VARCHAR(140) | Thời gian ước tính còn lại |
| 17 | best_reward | DECIMAL(21,9) | Reward tốt nhất đạt được |
| 18 | avg_reward_last_100 | DECIMAL(21,9) | Reward trung bình 100 episode gần nhất |
| 19 | total_steps | INT(11) | Tổng số steps đã thực hiện |
| 20 | best_makespan | DECIMAL(21,9) | Makespan tốt nhất (phút) |
| 21 | best_tardiness | DECIMAL(21,9) | Tardiness tốt nhất (phút) |
| 22 | avg_loss | DECIMAL(21,9) | Loss trung bình |
| 23 | reward_history | LONGTEXT | Lịch sử reward theo episode (JSON) |
| 24 | loss_history | LONGTEXT | Lịch sử loss theo episode (JSON) |
| 25 | model_path | VARCHAR(140) | Đường dẫn lưu model đã train |
| 26 | model_size_mb | DECIMAL(21,9) | Kích thước model (MB) |
| 27 | obs_dim | INT(11) | Observation Dimension - số chiều của state space |
| 28 | action_dim | INT(11) | Action Dimension - số chiều của action space |

---

### 3.11. Bảng tabSingles - APS Chatgpt Settings (Cài đặt ChatGPT - Single DocType)

Single DocType lưu trữ cấu hình OpenAI API cho tính năng AI Analysis trong APS. Dữ liệu được lưu trong bảng tabSingles với doctype='APS Chatgpt Settings'.

| STT | Tên thuộc tính | Kiểu dữ liệu | Ý nghĩa |
|-----|----------------|--------------|---------|
| 1 | doctype | VARCHAR(140) | Tên DocType = 'APS Chatgpt Settings' |
| 2 | field | VARCHAR(140) | Tên field |
| 3 | value | TEXT | Giá trị của field |
| - | api_key | Code/TEXT | API Key của OpenAI để gọi ChatGPT API |

---

## Ghi chú

- **PK**: Primary Key (Khóa chính)
- **FK**: Foreign Key (Khóa ngoại)
- **VARCHAR(140)**: Chuỗi ký tự tối đa 140 ký tự
- **INT(11)**: Số nguyên
- **DECIMAL(21,9)**: Số thực với 21 chữ số, 9 chữ số thập phân
- **TINYINT(1)**: Boolean (0 hoặc 1)
- **DATE**: Ngày (YYYY-MM-DD)
- **DATETIME(6)**: Ngày giờ với độ chính xác microsecond
- **TIME(6)**: Thời gian với độ chính xác microsecond
- **TEXT**: Văn bản ngắn
- **LONGTEXT**: Văn bản dài
