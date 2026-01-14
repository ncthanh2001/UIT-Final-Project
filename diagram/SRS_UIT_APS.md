# ĐẶC TẢ YÊU CẦU HỆ THỐNG (SRS)
# Software Requirements Specification

## Hệ thống UIT APS - Advanced Planning & Scheduling
### Module Lập lịch Sản xuất Nâng cao cho ERPNext Manufacturing

---

**Phiên bản:** 1.0
**Ngày tạo:** 13/01/2026
**Tác giả:** UIT - Đồ án tốt nghiệp

---

## MỤC LỤC

1. [Giới thiệu](#1-giới-thiệu)
2. [Mô tả tổng quan](#2-mô-tả-tổng-quan)
3. [Yêu cầu chức năng](#3-yêu-cầu-chức-năng)
4. [Yêu cầu phi chức năng](#4-yêu-cầu-phi-chức-năng)
5. [Yêu cầu giao diện](#5-yêu-cầu-giao-diện)
6. [Ràng buộc thiết kế](#6-ràng-buộc-thiết-kế)
7. [Ma trận truy vết yêu cầu](#7-ma-trận-truy-vết-yêu-cầu)

---

## 1. GIỚI THIỆU

### 1.1. Mục đích

Tài liệu này đặc tả các yêu cầu phần mềm cho hệ thống UIT APS (Advanced Planning & Scheduling) - một module mở rộng cho ERPNext Manufacturing, cung cấp khả năng lập lịch sản xuất tối ưu sử dụng các thuật toán tối ưu hóa (OR-Tools), Machine Learning và Reinforcement Learning.

### 1.2. Phạm vi

Hệ thống UIT APS bao gồm các module chính:
- **Module Dự báo nhu cầu (Demand Forecasting)**: Sử dụng ML để dự báo nhu cầu sản phẩm
- **Module Lập kế hoạch sản xuất (Production Planning)**: Tạo kế hoạch sản xuất từ dự báo
- **Module MRP (Material Requirement Planning)**: Tính toán nhu cầu nguyên vật liệu
- **Module Lập lịch sản xuất (Production Scheduling)**: Lập lịch chi tiết cho các Job Card
- **Module Phân tích AI (AI Analysis)**: Phân tích và đề xuất cải thiện

### 1.3. Định nghĩa, từ viết tắt và thuật ngữ

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| APS | Advanced Planning & Scheduling - Hệ thống lập kế hoạch và lập lịch nâng cao |
| ERPNext | Hệ thống ERP mã nguồn mở được xây dựng trên Frappe Framework |
| Frappe | Framework Python dùng để xây dựng các ứng dụng web |
| OR-Tools | Google Optimization Tools - Thư viện tối ưu hóa của Google |
| MRP | Material Requirement Planning - Hoạch định nhu cầu nguyên vật liệu |
| Job Card | Phiếu công việc - đơn vị công việc nhỏ nhất trong sản xuất |
| Work Order | Lệnh sản xuất |
| BOM | Bill of Materials - Định mức nguyên vật liệu |
| Workstation | Máy móc/Trạm làm việc trong nhà máy |
| Makespan | Tổng thời gian hoàn thành tất cả công việc |
| Tardiness | Độ trễ so với deadline |
| ARIMA | AutoRegressive Integrated Moving Average - Mô hình dự báo chuỗi thời gian |
| Prophet | Thư viện dự báo chuỗi thời gian của Facebook |
| RL | Reinforcement Learning - Học tăng cường |
| PPO | Proximal Policy Optimization - Thuật toán RL |
| SAC | Soft Actor-Critic - Thuật toán RL |
| MAPE | Mean Absolute Percentage Error - Sai số phần trăm tuyệt đối trung bình |

### 1.4. Tài liệu tham khảo

- ERPNext Manufacturing Documentation
- Frappe Framework Documentation
- Google OR-Tools Documentation
- Tài liệu thiết kế hệ thống UIT APS

### 1.5. Tổng quan tài liệu

Tài liệu được tổ chức theo chuẩn IEEE 830-1998 với các phần chính:
- Phần 2: Mô tả tổng quan về sản phẩm
- Phần 3: Yêu cầu chức năng chi tiết
- Phần 4: Yêu cầu phi chức năng
- Phần 5: Yêu cầu giao diện
- Phần 6: Ràng buộc thiết kế

---

## 2. MÔ TẢ TỔNG QUAN

### 2.1. Góc nhìn sản phẩm

UIT APS là một module mở rộng (Frappe App) được tích hợp vào hệ thống ERPNext Manufacturing. Hệ thống kế thừa và mở rộng các chức năng sản xuất có sẵn của ERPNext.

```
┌─────────────────────────────────────────────────────────────┐
│                      ERPNext System                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Sales     │  │  Inventory  │  │   Buying    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│  ┌─────────────────────────────────────────────────┐        │
│  │           ERPNext Manufacturing                  │        │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────┐ │        │
│  │  │   BOM   │ │Work Order│ │Job Card │ │Workst.│ │        │
│  │  └─────────┘ └─────────┘ └─────────┘ └───────┘ │        │
│  └─────────────────────────────────────────────────┘        │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────┐        │
│  │              UIT APS Module                      │        │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │        │
│  │  │Forecasting│ │Production│ │   MRP    │        │        │
│  │  │          │ │ Planning │ │          │        │        │
│  │  └──────────┘ └──────────┘ └──────────┘        │        │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │        │
│  │  │Scheduling│ │    AI    │ │    RL    │        │        │
│  │  │(OR-Tools)│ │ Analysis │ │ Training │        │        │
│  │  └──────────┘ └──────────┘ └──────────┘        │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 2.2. Chức năng sản phẩm

#### 2.2.1. Module Dự báo nhu cầu (Demand Forecasting)
- Dự báo nhu cầu sản phẩm dựa trên dữ liệu lịch sử bán hàng
- Hỗ trợ nhiều model ML: ARIMA, Prophet, Linear Regression
- Cung cấp khoảng tin cậy và phân tích xu hướng
- Khuyến nghị mức tồn kho an toàn

#### 2.2.2. Module Lập kế hoạch sản xuất (Production Planning)
- Tạo kế hoạch sản xuất từ kết quả dự báo
- Hỗ trợ độ phân giải theo tháng/quý
- Kiểm tra năng lực sản xuất

#### 2.2.3. Module MRP (Material Requirement Planning)
- Tính toán nhu cầu nguyên vật liệu từ kế hoạch sản xuất
- Xác định số lượng thiếu hụt
- Đề xuất mua hàng tự động

#### 2.2.4. Module Lập lịch sản xuất (Production Scheduling)
- Lập lịch chi tiết cho các Job Card sử dụng OR-Tools CP-SAT Solver
- Hỗ trợ nhiều chiến lược: Forward, Backward, EDD, Priority-based
- Tối ưu đa mục tiêu: Makespan, Tardiness
- So sánh với baseline FIFO

#### 2.2.5. Module Phân tích AI (AI Analysis)
- Phân tích kết quả lập lịch bằng ChatGPT API
- Đề xuất cải thiện và cảnh báo rủi ro
- Hỗ trợ đa ngôn ngữ (Tiếng Việt, Tiếng Anh)

### 2.3. Đặc điểm người dùng

| Loại người dùng | Mô tả | Chức năng sử dụng |
|-----------------|-------|-------------------|
| Quản lý sản xuất | Người quản lý toàn bộ quy trình sản xuất | Tất cả các module |
| Nhân viên kế hoạch | Người lập kế hoạch sản xuất | Forecasting, Production Planning, MRP |
| Điều độ sản xuất | Người điều phối công việc hàng ngày | Scheduling, AI Analysis |
| System Manager | Quản trị viên hệ thống | Cấu hình, quản lý |

### 2.4. Ràng buộc

- Phải tương thích với ERPNext version 14+
- Phải chạy trên Frappe Framework version 14+
- Sử dụng MariaDB/MySQL làm CSDL
- Python 3.10+
- Yêu cầu kết nối internet để sử dụng AI Analysis (ChatGPT API)

### 2.5. Giả định và phụ thuộc

**Giả định:**
- Dữ liệu master (Item, BOM, Workstation, Operation) đã được thiết lập đầy đủ trong ERPNext
- Người dùng đã quen thuộc với quy trình sản xuất và ERPNext
- Có đủ dữ liệu lịch sử bán hàng để dự báo (tối thiểu 30 ngày)

**Phụ thuộc:**
- ERPNext Manufacturing module
- Thư viện OR-Tools
- Thư viện statsmodels (ARIMA)
- Thư viện Prophet
- OpenAI API (cho AI Analysis)
- PyTorch (cho RL Training)

---

## 3. YÊU CẦU CHỨC NĂNG

### 3.1. Module Dự báo nhu cầu (Demand Forecasting)

#### FR-FC-001: Chạy dự báo nhu cầu
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-FC-001 |
| **Tên** | Chạy dự báo nhu cầu sản phẩm |
| **Mô tả** | Hệ thống cho phép người dùng chạy dự báo nhu cầu cho các sản phẩm dựa trên dữ liệu lịch sử bán hàng |
| **Đầu vào** | - Tên lần chạy dự báo<br>- Công ty<br>- Model sử dụng (ARIMA/Prophet/Linear Regression)<br>- Số ngày dự báo<br>- Khoảng thời gian training<br>- Bộ lọc (item_group, warehouse) |
| **Xử lý** | 1. Lấy dữ liệu Sales Order trong khoảng training<br>2. Tiền xử lý dữ liệu theo chuỗi thời gian<br>3. Train model với dữ liệu lịch sử<br>4. Dự báo cho số ngày yêu cầu<br>5. Tính toán khoảng tin cậy<br>6. Lưu kết quả |
| **Đầu ra** | - Bản ghi APS Forecast History<br>- Các bản ghi APS Forecast Result cho từng item |
| **Điều kiện tiên quyết** | - Có đủ dữ liệu Sales Order (≥30 ngày)<br>- Item đã được thiết lập |
| **Độ ưu tiên** | Cao |

#### FR-FC-002: Xem kết quả dự báo
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-FC-002 |
| **Tên** | Xem chi tiết kết quả dự báo |
| **Mô tả** | Hệ thống cho phép người dùng xem chi tiết kết quả dự báo bao gồm số lượng, khoảng tin cậy, tham số model |
| **Đầu vào** | Mã Forecast Result |
| **Đầu ra** | - Số lượng dự báo<br>- Khoảng tin cậy (lower_bound, upper_bound)<br>- Confidence score<br>- Tham số model (ARIMA: p,d,q; LR: R², slope; Prophet: seasonality)<br>- Khuyến nghị tồn kho |
| **Độ ưu tiên** | Cao |

#### FR-FC-003: So sánh các model dự báo
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-FC-003 |
| **Tên** | So sánh hiệu suất các model |
| **Mô tả** | Hệ thống cho phép so sánh độ chính xác giữa các model để chọn model tốt nhất |
| **Đầu vào** | Nhiều lần chạy dự báo với các model khác nhau |
| **Đầu ra** | - MAPE của từng model<br>- Model được khuyến nghị |
| **Độ ưu tiên** | Trung bình |

#### FR-FC-004: Phân loại tốc độ tiêu thụ
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-FC-004 |
| **Tên** | Phân loại sản phẩm theo tốc độ tiêu thụ |
| **Mô tả** | Hệ thống tự động phân loại sản phẩm thành Fast Moving, Slow Moving, Non Moving |
| **Đầu vào** | Dữ liệu bán hàng lịch sử |
| **Đầu ra** | movement_type cho từng item |
| **Độ ưu tiên** | Trung bình |

#### FR-FC-005: Cảnh báo đặt hàng
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-FC-005 |
| **Tên** | Cảnh báo cần đặt hàng |
| **Mô tả** | Hệ thống tự động đánh dấu cảnh báo khi tồn kho dự kiến xuống dưới mức an toàn |
| **Đầu vào** | - Tồn kho hiện tại<br>- Dự báo nhu cầu<br>- Safety stock |
| **Đầu ra** | reorder_alert = True/False |
| **Độ ưu tiên** | Cao |

---

### 3.2. Module Lập kế hoạch sản xuất (Production Planning)

#### FR-PP-001: Tạo kế hoạch sản xuất từ dự báo
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-PP-001 |
| **Tên** | Tạo kế hoạch sản xuất từ kết quả dự báo |
| **Mô tả** | Hệ thống cho phép tạo kế hoạch sản xuất tự động từ kết quả dự báo nhu cầu |
| **Đầu vào** | - Tên kế hoạch<br>- Công ty<br>- Forecast History<br>- Kỳ kế hoạch (from/to)<br>- Độ phân giải (Monthly/Quarterly) |
| **Xử lý** | 1. Lấy kết quả dự báo từ Forecast History<br>2. Tính số lượng sản xuất = Forecast Qty + Safety Stock - Current Stock<br>3. Tạo các dòng Production Plan Item |
| **Đầu ra** | Bản ghi APS Production Plan với các items |
| **Độ ưu tiên** | Cao |

#### FR-PP-002: Kiểm tra năng lực sản xuất
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-PP-002 |
| **Tên** | Kiểm tra năng lực sản xuất |
| **Mô tả** | Hệ thống kiểm tra xem kế hoạch có vượt quá năng lực sản xuất không |
| **Đầu vào** | APS Production Plan |
| **Đầu ra** | capacity_status (OK/Overloaded/Unknown) |
| **Độ ưu tiên** | Trung bình |

#### FR-PP-003: Quản lý trạng thái kế hoạch
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-PP-003 |
| **Tên** | Quản lý workflow trạng thái |
| **Mô tả** | Hệ thống hỗ trợ workflow: Draft → Planned → Released → Completed/Cancelled |
| **Đầu vào** | Hành động chuyển trạng thái |
| **Đầu ra** | Trạng thái mới của kế hoạch |
| **Độ ưu tiên** | Trung bình |

---

### 3.3. Module MRP (Material Requirement Planning)

#### FR-MRP-001: Chạy MRP
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-MRP-001 |
| **Tên** | Chạy tính toán MRP |
| **Mô tả** | Hệ thống tính toán nhu cầu nguyên vật liệu từ kế hoạch sản xuất |
| **Đầu vào** | - APS Production Plan<br>- Người thực hiện |
| **Xử lý** | 1. Lấy danh sách items trong kế hoạch<br>2. Với mỗi item, lấy BOM tương ứng<br>3. Tính nhu cầu NVL = Planned Qty × BOM Qty<br>4. Lấy tồn kho hiện tại<br>5. Tính số lượng thiếu = Required - Available<br>6. Lưu kết quả |
| **Đầu ra** | - Bản ghi APS MRP Run<br>- Các bản ghi APS MRP Result |
| **Điều kiện tiên quyết** | - Production Plan đã được tạo<br>- BOM đã được thiết lập cho các items |
| **Độ ưu tiên** | Cao |

#### FR-MRP-002: Xem kết quả MRP
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-MRP-002 |
| **Tên** | Xem chi tiết kết quả MRP |
| **Mô tả** | Hệ thống hiển thị danh sách NVL thiếu với số lượng và ngày cần |
| **Đầu vào** | MRP Run |
| **Đầu ra** | Danh sách MRP Results với required_qty, available_qty, shortage_qty, required_date |
| **Độ ưu tiên** | Cao |

#### FR-MRP-003: Tạo đề xuất mua hàng
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-MRP-003 |
| **Tên** | Tạo đề xuất mua hàng tự động |
| **Mô tả** | Hệ thống tự động tạo đề xuất mua hàng cho các NVL thiếu |
| **Đầu vào** | MRP Results với shortage_qty > 0 |
| **Xử lý** | 1. Lấy supplier mặc định cho item<br>2. Lấy giá và lead time từ Item Supplier<br>3. Tạo Purchase Suggestion |
| **Đầu ra** | Các bản ghi APS Purchase Suggestion |
| **Độ ưu tiên** | Trung bình |

#### FR-MRP-004: Phê duyệt đề xuất mua hàng
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-MRP-004 |
| **Tên** | Phê duyệt/Từ chối đề xuất mua hàng |
| **Mô tả** | Hệ thống cho phép phê duyệt hoặc từ chối đề xuất mua hàng |
| **Đầu vào** | - Purchase Suggestion<br>- Hành động (Approve/Reject) |
| **Đầu ra** | suggestion_status cập nhật |
| **Độ ưu tiên** | Trung bình |

---

### 3.4. Module Lập lịch sản xuất (Production Scheduling)

#### FR-SC-001: Chạy lập lịch sản xuất
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-SC-001 |
| **Tên** | Chạy lập lịch sản xuất tối ưu |
| **Mô tả** | Hệ thống lập lịch chi tiết cho các Job Card sử dụng OR-Tools CP-SAT Solver |
| **Đầu vào** | - Production Plan (ERPNext)<br>- Chiến lược lập lịch (Forward/Backward/EDD/Priority)<br>- Scheduling Tier (OR-Tools/RL/GNN)<br>- Cấu hình solver (time_limit, weights) |
| **Xử lý** | 1. Lấy danh sách Job Cards từ Production Plan<br>2. Lấy thông tin Workstation, Operation<br>3. Xây dựng mô hình CP-SAT với các ràng buộc<br>4. Chạy solver tối ưu hóa<br>5. So sánh với baseline FIFO<br>6. Lưu kết quả |
| **Đầu ra** | - Bản ghi APS Scheduling Run<br>- Các bản ghi APS Scheduling Result |
| **Điều kiện tiên quyết** | - Production Plan đã tạo Work Orders và Job Cards<br>- Workstation đã được thiết lập |
| **Độ ưu tiên** | Rất cao |

#### FR-SC-002: Áp dụng các ràng buộc lập lịch
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-SC-002 |
| **Tên** | Áp dụng các ràng buộc lập lịch |
| **Mô tả** | Hệ thống hỗ trợ các ràng buộc lập lịch sản xuất |
| **Ràng buộc** | - Machine Eligibility: Mỗi operation chỉ chạy trên máy phù hợp<br>- Precedence: Các operation trong cùng Work Order theo thứ tự<br>- No Overlap: Mỗi máy chỉ xử lý 1 operation tại 1 thời điểm<br>- Working Hours: Lập lịch trong giờ làm việc<br>- Due Dates: Ưu tiên hoàn thành trước deadline<br>- Setup Time: Tính thời gian setup khi chuyển đổi |
| **Độ ưu tiên** | Rất cao |

#### FR-SC-003: Tối ưu đa mục tiêu
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-SC-003 |
| **Tên** | Tối ưu hóa đa mục tiêu |
| **Mô tả** | Hệ thống tối ưu hóa theo nhiều mục tiêu với trọng số có thể cấu hình |
| **Mục tiêu** | - Minimize Makespan (tổng thời gian hoàn thành)<br>- Minimize Total Tardiness (tổng độ trễ) |
| **Đầu vào** | makespan_weight, tardiness_weight |
| **Độ ưu tiên** | Cao |

#### FR-SC-004: So sánh với baseline
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-SC-004 |
| **Tên** | So sánh kết quả với baseline FIFO |
| **Mô tả** | Hệ thống tự động so sánh kết quả tối ưu với phương pháp FIFO đơn giản |
| **Đầu ra** | - baseline_makespan, baseline_late_jobs, baseline_tardiness<br>- improvement_makespan_percent<br>- improvement_late_jobs_percent<br>- improvement_tardiness_percent |
| **Độ ưu tiên** | Cao |

#### FR-SC-005: Xem kết quả lập lịch
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-SC-005 |
| **Tên** | Xem chi tiết kết quả lập lịch |
| **Mô tả** | Hệ thống hiển thị chi tiết lịch trình cho từng Job Card |
| **Đầu ra** | Danh sách Scheduling Results với:<br>- Job Card, Workstation, Operation<br>- Planned Start/End Time<br>- Work Shift<br>- Is Late flag |
| **Độ ưu tiên** | Cao |

#### FR-SC-006: Áp dụng kết quả lập lịch
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-SC-006 |
| **Tên** | Áp dụng lịch trình vào Job Card |
| **Mô tả** | Hệ thống cho phép áp dụng kết quả lập lịch vào các Job Card thực tế trong ERPNext |
| **Đầu vào** | - Scheduling Run với trạng thái Pending Approval<br>- Người phê duyệt |
| **Xử lý** | 1. Cập nhật planned_start_date, planned_end_date của Job Card<br>2. Đánh dấu is_applied = True cho Scheduling Results<br>3. Cập nhật trạng thái Scheduling Run = Applied |
| **Đầu ra** | Job Cards được cập nhật thời gian |
| **Độ ưu tiên** | Cao |

#### FR-SC-007: Hiển thị Gantt Chart
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-SC-007 |
| **Tên** | Hiển thị biểu đồ Gantt |
| **Mô tả** | Hệ thống hiển thị kết quả lập lịch dưới dạng biểu đồ Gantt |
| **Đầu ra** | Gantt Chart với:<br>- Trục Y: Danh sách Workstation<br>- Trục X: Thời gian<br>- Các thanh: Job Cards với màu theo Work Order |
| **Độ ưu tiên** | Trung bình |

---

### 3.5. Module Phân tích AI (AI Analysis)

#### FR-AI-001: Phân tích kết quả lập lịch bằng AI
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-AI-001 |
| **Tên** | Phân tích kết quả lập lịch bằng ChatGPT |
| **Mô tả** | Hệ thống gửi dữ liệu lập lịch đến ChatGPT API để phân tích và đề xuất |
| **Đầu vào** | - Scheduling Run<br>- Prompt tùy chỉnh<br>- Ngôn ngữ (vi/en) |
| **Xử lý** | 1. Thu thập metrics từ Scheduling Run<br>2. Tạo prompt với context<br>3. Gọi ChatGPT API<br>4. Lưu kết quả phân tích |
| **Đầu ra** | llm_analysis_content với:<br>- Đánh giá tổng quan<br>- Điểm mạnh/điểm yếu<br>- Khuyến nghị cải thiện<br>- Cảnh báo rủi ro |
| **Điều kiện tiên quyết** | API Key đã được cấu hình |
| **Độ ưu tiên** | Trung bình |

#### FR-AI-002: Cấu hình API Key
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-AI-002 |
| **Tên** | Cấu hình OpenAI API Key |
| **Mô tả** | Hệ thống cho phép cấu hình API Key cho ChatGPT |
| **Đầu vào** | OpenAI API Key |
| **Đầu ra** | Lưu vào APS Chatgpt Settings |
| **Độ ưu tiên** | Cao |

---

### 3.6. Module Huấn luyện RL (RL Training)

#### FR-RL-001: Huấn luyện RL Agent
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-RL-001 |
| **Tên** | Huấn luyện Reinforcement Learning Agent |
| **Mô tả** | Hệ thống cho phép huấn luyện RL agent (PPO/SAC) để lập lịch |
| **Đầu vào** | - Scheduling Run<br>- Agent type (PPO/SAC)<br>- Hyperparameters (episodes, learning_rate, gamma, hidden_sizes, batch_size) |
| **Xử lý** | 1. Tạo môi trường Gym từ dữ liệu Job Shop<br>2. Khởi tạo agent với hyperparameters<br>3. Huấn luyện theo số episodes<br>4. Lưu model và metrics |
| **Đầu ra** | - APS RL Training Log<br>- Model file (.pt) |
| **Độ ưu tiên** | Thấp |

#### FR-RL-002: Theo dõi tiến độ huấn luyện
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-RL-002 |
| **Tên** | Theo dõi tiến độ huấn luyện realtime |
| **Mô tả** | Hệ thống hiển thị tiến độ huấn luyện bao gồm episode hiện tại, reward, loss |
| **Đầu ra** | - current_episode, progress_percentage<br>- best_reward, avg_reward_last_100<br>- reward_history, loss_history (charts) |
| **Độ ưu tiên** | Thấp |

---

### 3.7. Quản lý Ca làm việc

#### FR-WS-001: Quản lý ca làm việc
| Thuộc tính | Mô tả |
|------------|-------|
| **ID** | FR-WS-001 |
| **Tên** | Quản lý thông tin ca làm việc |
| **Mô tả** | Hệ thống cho phép tạo và quản lý các ca làm việc trong nhà máy |
| **Đầu vào** | - Tên ca<br>- Giờ bắt đầu/kết thúc<br>- Có phải ca đêm không |
| **Đầu ra** | Bản ghi APS Work Shift |
| **Độ ưu tiên** | Trung bình |

---

## 4. YÊU CẦU PHI CHỨC NĂNG

### 4.1. Hiệu năng (Performance)

| ID | Yêu cầu | Tiêu chí |
|----|---------|----------|
| NFR-PF-001 | Thời gian chạy dự báo | Hoàn thành dự báo cho 100 items trong ≤ 60 giây |
| NFR-PF-002 | Thời gian chạy MRP | Hoàn thành MRP cho 1000 dòng BOM trong ≤ 30 giây |
| NFR-PF-003 | Thời gian lập lịch | Tìm lời giải feasible cho 100 Job Cards trong ≤ 300 giây |
| NFR-PF-004 | Thời gian phản hồi UI | Tải trang trong ≤ 3 giây |
| NFR-PF-005 | Xử lý đồng thời | Hỗ trợ ≥ 10 người dùng đồng thời |

### 4.2. Độ tin cậy (Reliability)

| ID | Yêu cầu | Tiêu chí |
|----|---------|----------|
| NFR-RL-001 | Độ chính xác dự báo | MAPE ≤ 30% cho dữ liệu có pattern rõ ràng |
| NFR-RL-002 | Chất lượng lập lịch | Cải thiện ≥ 10% makespan so với FIFO |
| NFR-RL-003 | Xử lý lỗi | Ghi log đầy đủ khi xảy ra lỗi |
| NFR-RL-004 | Khôi phục | Có thể retry khi solver timeout |

### 4.3. Khả dụng (Availability)

| ID | Yêu cầu | Tiêu chí |
|----|---------|----------|
| NFR-AV-001 | Uptime | Hệ thống khả dụng ≥ 99% trong giờ làm việc |
| NFR-AV-002 | Backup | Dữ liệu được backup định kỳ theo chính sách ERPNext |

### 4.4. Bảo mật (Security)

| ID | Yêu cầu | Tiêu chí |
|----|---------|----------|
| NFR-SC-001 | Xác thực | Sử dụng cơ chế xác thực của Frappe Framework |
| NFR-SC-002 | Phân quyền | Chỉ System Manager có quyền truy cập APS |
| NFR-SC-003 | Bảo mật API Key | API Key được lưu trữ an toàn, không hiển thị plain text |
| NFR-SC-004 | Audit trail | Ghi lại lịch sử thay đổi các bản ghi quan trọng |

### 4.5. Khả năng bảo trì (Maintainability)

| ID | Yêu cầu | Tiêu chí |
|----|---------|----------|
| NFR-MT-001 | Modular design | Các module độc lập, có thể bật/tắt riêng |
| NFR-MT-002 | Logging | Log chi tiết cho debug và troubleshooting |
| NFR-MT-003 | Documentation | Code có docstring và comment đầy đủ |
| NFR-MT-004 | Version control | Theo dõi phiên bản và changelog |

### 4.6. Khả năng mở rộng (Scalability)

| ID | Yêu cầu | Tiêu chí |
|----|---------|----------|
| NFR-SC-001 | Horizontal scaling | Hỗ trợ chạy background job trên nhiều worker |
| NFR-SC-002 | Data volume | Xử lý được ≥ 10,000 Job Cards trong database |
| NFR-SC-003 | Model extensibility | Dễ dàng thêm model dự báo mới |

### 4.7. Khả năng sử dụng (Usability)

| ID | Yêu cầu | Tiêu chí |
|----|---------|----------|
| NFR-US-001 | Ngôn ngữ | Hỗ trợ Tiếng Việt và Tiếng Anh |
| NFR-US-002 | Giao diện nhất quán | Tuân thủ UI/UX guidelines của ERPNext |
| NFR-US-003 | Hướng dẫn | Có tooltip và description cho các field |
| NFR-US-004 | Thông báo | Hiển thị thông báo rõ ràng khi thành công/thất bại |

---

## 5. YÊU CẦU GIAO DIỆN

### 5.1. Giao diện người dùng (User Interface)

#### UI-001: Giao diện chính APS
- Tích hợp vào desk ERPNext với module riêng "UIT APS"
- Có shortcuts đến các DocType chính
- Dashboard tổng quan với số liệu thống kê

#### UI-002: Form Scheduling Run
- Hiển thị đầy đủ thông tin cấu hình và kết quả
- Section collapsible cho các nhóm thông tin
- Button "Run Scheduling" với confirm dialog
- Button "Apply Results" với preview trước khi áp dụng
- Button "Get AI Analysis" để phân tích

#### UI-003: List View
- Các DocType có list view với các cột quan trọng
- Filter và sort theo các field thông dụng
- Color coding cho trạng thái (Pending=Yellow, Running=Blue, Completed=Green, Failed=Red)

#### UI-004: Gantt Chart View
- Hiển thị kết quả lập lịch dạng Gantt
- Có thể zoom in/out theo thời gian
- Tooltip hiển thị chi tiết khi hover

### 5.2. Giao diện phần mềm (Software Interface)

#### SI-001: ERPNext Integration
- Đọc dữ liệu từ: Production Plan, Work Order, Job Card, Item, BOM, Workstation, Operation
- Ghi dữ liệu vào: Job Card (planned dates)

#### SI-002: OR-Tools Integration
- Sử dụng OR-Tools CP-SAT Solver
- Truyền dữ liệu qua Python API

#### SI-003: OpenAI API Integration
- RESTful API call đến ChatGPT
- Xử lý rate limiting và error handling

#### SI-004: ML Libraries Integration
- statsmodels cho ARIMA
- Prophet cho Prophet model
- scikit-learn cho Linear Regression
- PyTorch cho RL Training

### 5.3. Giao diện phần cứng (Hardware Interface)

Không có yêu cầu đặc biệt về phần cứng. Hệ thống chạy trên server tiêu chuẩn với:
- CPU: ≥ 4 cores (khuyến nghị 8 cores cho solver)
- RAM: ≥ 8GB (khuyến nghị 16GB)
- Storage: ≥ 50GB

### 5.4. Giao diện truyền thông (Communication Interface)

- HTTPS cho web interface
- Frappe REST API cho integration
- WebSocket cho realtime updates (training progress)

---

## 6. RÀNG BUỘC THIẾT KẾ

### 6.1. Ràng buộc công nghệ

| Ràng buộc | Mô tả |
|-----------|-------|
| Framework | Frappe Framework 14+ |
| ERP | ERPNext 14+ |
| Database | MariaDB 10.6+ / MySQL 8.0+ |
| Python | Python 3.10+ |
| Frontend | Frappe UI (Vue.js based) |

### 6.2. Ràng buộc kiến trúc

- Module phải được đóng gói dưới dạng Frappe App
- Sử dụng DocType cho tất cả các entity
- Sử dụng Frappe hooks cho các event handler
- Background jobs sử dụng Frappe Job Queue (RQ)

### 6.3. Ràng buộc tích hợp

- Không modify core ERPNext code
- Sử dụng ERPNext API để đọc/ghi dữ liệu
- Tương thích với ERPNext Manufacturing workflow

### 6.4. Ràng buộc triển khai

- Hỗ trợ cài đặt qua bench command
- Có thể cài đặt bổ sung vào site ERPNext hiện có
- Không yêu cầu restart server sau khi cài đặt

---

## 7. MA TRẬN TRUY VẾT YÊU CẦU

### 7.1. Mapping Use Case - Functional Requirements

| Use Case | Functional Requirements |
|----------|------------------------|
| UC-FC-01: Chạy dự báo | FR-FC-001, FR-FC-004, FR-FC-005 |
| UC-FC-02: Xem kết quả dự báo | FR-FC-002, FR-FC-003 |
| UC-PP-01: Tạo kế hoạch sản xuất | FR-PP-001, FR-PP-002, FR-PP-003 |
| UC-MRP-01: Chạy MRP | FR-MRP-001, FR-MRP-002 |
| UC-MRP-02: Quản lý đề xuất mua hàng | FR-MRP-003, FR-MRP-004 |
| UC-SC-01: Chạy lập lịch | FR-SC-001, FR-SC-002, FR-SC-003, FR-SC-004 |
| UC-SC-02: Xem và áp dụng lịch | FR-SC-005, FR-SC-006, FR-SC-007 |
| UC-AI-01: Phân tích AI | FR-AI-001, FR-AI-002 |
| UC-RL-01: Huấn luyện RL | FR-RL-001, FR-RL-002 |

### 7.2. Mapping Functional Requirements - DocTypes

| Functional Requirement | DocTypes liên quan |
|----------------------|-------------------|
| FR-FC-001, FR-FC-002 | APS Forecast History, APS Forecast Result, APS Forecast History Item |
| FR-PP-001, FR-PP-002 | APS Production Plan, APS Production Plan Item |
| FR-MRP-001, FR-MRP-002 | APS MRP Run, APS MRP Result |
| FR-MRP-003, FR-MRP-004 | APS Purchase Suggestion |
| FR-SC-001 - FR-SC-006 | APS Scheduling Run, APS Scheduling Result, APS Work Shift |
| FR-AI-001, FR-AI-002 | APS Chatgpt Settings |
| FR-RL-001, FR-RL-002 | APS RL Training Log |

### 7.3. Độ ưu tiên yêu cầu

| Độ ưu tiên | Functional Requirements |
|------------|------------------------|
| Rất cao | FR-SC-001, FR-SC-002 |
| Cao | FR-FC-001, FR-FC-002, FR-FC-005, FR-PP-001, FR-MRP-001, FR-MRP-002, FR-SC-003, FR-SC-004, FR-SC-005, FR-SC-006, FR-AI-002 |
| Trung bình | FR-FC-003, FR-FC-004, FR-PP-002, FR-PP-003, FR-MRP-003, FR-MRP-004, FR-SC-007, FR-AI-001, FR-WS-001 |
| Thấp | FR-RL-001, FR-RL-002 |

---

## PHỤ LỤC

### A. Danh sách DocTypes

1. APS Scheduling Run
2. APS Scheduling Result
3. APS Work Shift
4. APS Forecast History
5. APS Forecast History Item (Child Table)
6. APS Forecast Result
7. APS Production Plan
8. APS Production Plan Item (Child Table)
9. APS MRP Run
10. APS MRP Result
11. APS Purchase Suggestion
12. APS RL Training Log
13. APS Chatgpt Settings (Single DocType)

### B. Danh sách ERPNext DocTypes sử dụng

1. Company
2. User
3. Item
4. Item Group
5. BOM
6. BOM Item
7. Workstation
8. Operation
9. Production Plan
10. Work Order
11. Job Card
12. Supplier
13. Warehouse
14. Sales Order

### C. Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 13/01/2026 | UIT | Initial version |

---

*Tài liệu này được tạo cho mục đích Đồ án tốt nghiệp - UIT*
