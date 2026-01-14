# ĐỒ ÁN TỐT NGHIỆP

## XÂY DỰNG MODULE LẬP LỊCH SẢN XUẤT NÂNG CAO (APS) CHO HỆ THỐNG ERPNext

---

**TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN - ĐHQG TP.HCM**

**KHOA CÔNG NGHỆ PHẦN MỀM**

---

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên đề tài** | Xây dựng Module Lập lịch Sản xuất Nâng cao (Advanced Planning & Scheduling - APS) cho hệ thống ERPNext |
| **Loại đề tài** | Đồ án tốt nghiệp |
| **Ngành** | Công nghệ Thông tin / Kỹ thuật Phần mềm |

---

# MỤC LỤC

- [CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI](#chương-1-tổng-quan-đề-tài)
  - [1.1. Đặt vấn đề](#11-đặt-vấn-đề)
  - [1.2. Mục tiêu đề tài](#12-mục-tiêu-đề-tài)
  - [1.3. Phạm vi đề tài](#13-phạm-vi-đề-tài)
  - [1.4. Đối tượng và phạm vi nghiên cứu](#14-đối-tượng-và-phạm-vi-nghiên-cứu)
  - [1.5. Phương pháp nghiên cứu](#15-phương-pháp-nghiên-cứu)
  - [1.6. Ý nghĩa khoa học và thực tiễn](#16-ý-nghĩa-khoa-học-và-thực-tiễn)
  - [1.7. Bố cục đồ án](#17-bố-cục-đồ-án)
- [CHƯƠNG 2: CƠ SỞ LÝ THUYẾT](#chương-2-cơ-sở-lý-thuyết)
  - [2.1. Tổng quan về ERP và ERPNext](#21-tổng-quan-về-erp-và-erpnext)
  - [2.2. Lập lịch sản xuất (Production Scheduling)](#22-lập-lịch-sản-xuất-production-scheduling)
  - [2.3. Bài toán Job Shop Scheduling](#23-bài-toán-job-shop-scheduling)
  - [2.4. OR-Tools và CP-SAT Solver](#24-or-tools-và-cp-sat-solver)
  - [2.5. Dự báo nhu cầu (Demand Forecasting)](#25-dự-báo-nhu-cầu-demand-forecasting)
  - [2.6. Hoạch định nhu cầu vật tư (MRP)](#26-hoạch-định-nhu-cầu-vật-tư-mrp)
  - [2.7. Reinforcement Learning trong lập lịch](#27-reinforcement-learning-trong-lập-lịch)
  - [2.8. Large Language Models (LLM) trong phân tích](#28-large-language-models-llm-trong-phân-tích)
- [CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG](#chương-3-phân-tích-và-thiết-kế-hệ-thống)
  - [3.1. Phân tích yêu cầu](#31-phân-tích-yêu-cầu)
  - [3.2. Kiến trúc hệ thống](#32-kiến-trúc-hệ-thống)
  - [3.3. Thiết kế Use Case](#33-thiết-kế-use-case)
  - [3.4. Thiết kế Activity Diagram](#34-thiết-kế-activity-diagram)
  - [3.5. Thiết kế cơ sở dữ liệu](#35-thiết-kế-cơ-sở-dữ-liệu)
  - [3.6. Thiết kế giao diện](#36-thiết-kế-giao-diện)
- [CHƯƠNG 4: HIỆN THỰC HỆ THỐNG](#chương-4-hiện-thực-hệ-thống)
  - [4.1. Môi trường phát triển](#41-môi-trường-phát-triển)
  - [4.2. Cấu trúc dự án](#42-cấu-trúc-dự-án)
  - [4.3. Hiện thực Module Dự báo](#43-hiện-thực-module-dự-báo)
  - [4.4. Hiện thực Module Kế hoạch sản xuất](#44-hiện-thực-module-kế-hoạch-sản-xuất)
  - [4.5. Hiện thực Module MRP](#45-hiện-thực-module-mrp)
  - [4.6. Hiện thực Module Lập lịch](#46-hiện-thực-module-lập-lịch)
  - [4.7. Hiện thực Module AI Analysis](#47-hiện-thực-module-ai-analysis)
  - [4.8. Tích hợp và API](#48-tích-hợp-và-api)
- [CHƯƠNG 5: KIỂM THỬ VÀ ĐÁNH GIÁ](#chương-5-kiểm-thử-và-đánh-giá)
  - [5.1. Kế hoạch kiểm thử](#51-kế-hoạch-kiểm-thử)
  - [5.2. Kiểm thử chức năng](#52-kiểm-thử-chức-năng)
  - [5.3. Kiểm thử hiệu năng](#53-kiểm-thử-hiệu-năng)
  - [5.4. Đánh giá kết quả](#54-đánh-giá-kết-quả)
  - [5.5. So sánh với các hệ thống khác](#55-so-sánh-với-các-hệ-thống-khác)
- [CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN](#chương-6-kết-luận-và-hướng-phát-triển)
  - [6.1. Kết quả đạt được](#61-kết-quả-đạt-được)
  - [6.2. Hạn chế](#62-hạn-chế)
  - [6.3. Hướng phát triển](#63-hướng-phát-triển)
- [TÀI LIỆU THAM KHẢO](#tài-liệu-tham-khảo)
- [PHỤ LỤC](#phụ-lục)

---

# DANH MỤC HÌNH ẢNH

| STT | Hình | Mô tả |
|-----|------|-------|
| 1 | Hình 2.1 | Kiến trúc Frappe Framework |
| 2 | Hình 2.2 | Mô hình Job Shop Scheduling |
| 3 | Hình 2.3 | Quy trình OR-Tools CP-SAT |
| 4 | Hình 2.4 | Các phương pháp dự báo |
| 5 | Hình 2.5 | Quy trình MRP |
| 6 | Hình 3.1 | Kiến trúc tổng thể hệ thống |
| 7 | Hình 3.2 | Use Case Diagram tổng quan |
| 8 | Hình 3.3 | Activity Diagram - Dự báo nhu cầu |
| 9 | Hình 3.4 | Activity Diagram - Lập lịch sản xuất |
| 10 | Hình 3.5 | ERD - Cơ sở dữ liệu UIT APS |
| 11 | Hình 4.1 | Cấu trúc thư mục dự án |
| 12 | Hình 4.2 | Giao diện Scheduling Run |
| 13 | Hình 4.3 | Gantt Chart lập lịch |
| 14 | Hình 5.1 | Kết quả so sánh với FIFO |

---

# DANH MỤC BẢNG

| STT | Bảng | Mô tả |
|-----|------|-------|
| 1 | Bảng 2.1 | So sánh các phương pháp lập lịch |
| 2 | Bảng 2.2 | So sánh các mô hình dự báo |
| 3 | Bảng 3.1 | Danh sách yêu cầu chức năng |
| 4 | Bảng 3.2 | Danh sách yêu cầu phi chức năng |
| 5 | Bảng 3.3 | Mô tả Use Case |
| 6 | Bảng 3.4 | Cấu trúc bảng dữ liệu |
| 7 | Bảng 4.1 | Công nghệ sử dụng |
| 8 | Bảng 5.1 | Kết quả kiểm thử chức năng |
| 9 | Bảng 5.2 | Kết quả kiểm thử hiệu năng |
| 10 | Bảng 5.3 | So sánh metrics với baseline |

---

# DANH MỤC TỪ VIẾT TẮT

| Từ viết tắt | Giải thích |
|-------------|------------|
| APS | Advanced Planning and Scheduling - Lập lịch sản xuất nâng cao |
| ERP | Enterprise Resource Planning - Hoạch định nguồn lực doanh nghiệp |
| MRP | Material Requirements Planning - Hoạch định nhu cầu vật tư |
| BOM | Bill of Materials - Định mức nguyên vật liệu |
| WO | Work Order - Lệnh sản xuất |
| JC | Job Card - Phiếu công việc |
| CP-SAT | Constraint Programming with SAT Solver |
| ARIMA | AutoRegressive Integrated Moving Average |
| MAPE | Mean Absolute Percentage Error |
| RL | Reinforcement Learning - Học tăng cường |
| PPO | Proximal Policy Optimization |
| SAC | Soft Actor-Critic |
| LLM | Large Language Model |
| API | Application Programming Interface |
| FIFO | First In First Out |
| EDD | Earliest Due Date |
| JSSP | Job Shop Scheduling Problem |

---

# CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI

## 1.1. Đặt vấn đề

### 1.1.1. Bối cảnh

Trong bối cảnh cách mạng công nghiệp 4.0, các doanh nghiệp sản xuất đang đối mặt với nhiều thách thức:

- **Áp lực cạnh tranh**: Yêu cầu giao hàng đúng hạn ngày càng cao
- **Tối ưu hóa nguồn lực**: Cần sử dụng hiệu quả máy móc, nhân công
- **Quản lý phức tạp**: Số lượng đơn hàng, sản phẩm, công đoạn ngày càng tăng
- **Biến động thị trường**: Nhu cầu thay đổi nhanh chóng, khó dự đoán

### 1.1.2. Vấn đề nghiên cứu

Hệ thống ERPNext là một nền tảng ERP mã nguồn mở phổ biến, tuy nhiên module Manufacturing hiện tại còn **hạn chế**:

1. **Lập lịch thủ công**: Không có công cụ tự động lập lịch tối ưu
2. **Thiếu dự báo**: Không có khả năng dự báo nhu cầu sản xuất
3. **MRP cơ bản**: Chỉ tính toán nhu cầu vật tư đơn giản
4. **Không có AI/ML**: Thiếu các công cụ phân tích thông minh

### 1.1.3. Câu hỏi nghiên cứu

1. Làm thế nào để tích hợp thuật toán lập lịch tối ưu vào ERPNext?
2. Các mô hình Machine Learning nào phù hợp cho dự báo nhu cầu sản xuất?
3. Làm thế nào để cải thiện hiệu quả lập lịch so với phương pháp truyền thống?

## 1.2. Mục tiêu đề tài

### 1.2.1. Mục tiêu tổng quát

Xây dựng module **Advanced Planning & Scheduling (APS)** tích hợp vào ERPNext, cung cấp khả năng:

- Dự báo nhu cầu sản xuất bằng Machine Learning
- Lập kế hoạch sản xuất tự động
- Tối ưu hóa lịch trình sản xuất bằng OR-Tools
- Phân tích kết quả bằng AI

### 1.2.2. Mục tiêu cụ thể

| STT | Mục tiêu | Chỉ số đánh giá |
|-----|----------|-----------------|
| 1 | Dự báo nhu cầu chính xác | MAPE ≤ 30% |
| 2 | Cải thiện makespan | ≥ 10% so với FIFO |
| 3 | Giảm số job trễ hạn | ≥ 20% so với FIFO |
| 4 | Tăng hiệu suất sử dụng máy | ≥ 70% |
| 5 | Thời gian lập lịch 100 jobs | ≤ 300 giây |

## 1.3. Phạm vi đề tài

### 1.3.1. Phạm vi thực hiện

**Bao gồm:**
- Module Dự báo nhu cầu (Demand Forecasting)
- Module Kế hoạch sản xuất (Production Planning)
- Module Hoạch định nhu cầu vật tư (MRP)
- Module Lập lịch sản xuất (Scheduling) với OR-Tools
- Module Phân tích AI (AI Analysis)
- Quản lý ca làm việc (Work Shifts)
- Huấn luyện Reinforcement Learning (RL Training)

**Không bao gồm:**
- Tích hợp IoT/sensors
- Real-time tracking sản xuất
- Mobile application
- Multi-company scheduling

### 1.3.2. Giới hạn kỹ thuật

- **Số lượng jobs**: Tối đa 500 jobs/lần lập lịch
- **Thời gian solver**: Tối đa 600 giây
- **Dữ liệu lịch sử**: Yêu cầu ≥ 30 data points cho dự báo

## 1.4. Đối tượng và phạm vi nghiên cứu

### 1.4.1. Đối tượng nghiên cứu

- Bài toán lập lịch sản xuất (Job Shop Scheduling Problem)
- Các thuật toán tối ưu hóa (Constraint Programming, CP-SAT)
- Các mô hình dự báo (ARIMA, Prophet, Linear Regression)
- Reinforcement Learning trong sản xuất

### 1.4.2. Phạm vi nghiên cứu

- Ngành công nghiệp sản xuất rời rạc (discrete manufacturing)
- Môi trường Job Shop với nhiều máy, nhiều công đoạn
- Tối ưu đa mục tiêu: makespan, tardiness, utilization

## 1.5. Phương pháp nghiên cứu

### 1.5.1. Phương pháp lý thuyết

- Nghiên cứu tài liệu về lập lịch sản xuất
- Phân tích các thuật toán tối ưu hóa
- Tìm hiểu các mô hình Machine Learning

### 1.5.2. Phương pháp thực nghiệm

- Phát triển module theo Agile/Scrum
- Kiểm thử với dữ liệu thực tế
- So sánh với baseline FIFO

### 1.5.3. Công nghệ sử dụng

| Thành phần | Công nghệ |
|------------|-----------|
| Backend | Python 3.10+, Frappe Framework 14+ |
| Frontend | ERPNext UI, JavaScript, Vue.js |
| Database | MariaDB 10.6+ |
| Optimization | OR-Tools CP-SAT Solver |
| ML/AI | statsmodels, Prophet, scikit-learn |
| RL | PyTorch, stable-baselines3 |
| LLM | OpenAI API (ChatGPT) |

## 1.6. Ý nghĩa khoa học và thực tiễn

### 1.6.1. Ý nghĩa khoa học

- Áp dụng **Constraint Programming** giải quyết bài toán JSSP
- Tích hợp **Machine Learning** vào dự báo sản xuất
- Nghiên cứu **Reinforcement Learning** cho lập lịch thích ứng
- Kết hợp **LLM** phân tích kết quả lập lịch

### 1.6.2. Ý nghĩa thực tiễn

- **Tối ưu hóa sản xuất**: Giảm thời gian hoàn thành, tăng hiệu suất máy
- **Giảm chi phí**: Tối ưu tồn kho, giảm lãng phí
- **Nâng cao cạnh tranh**: Giao hàng đúng hạn, đáp ứng nhu cầu linh hoạt
- **Hỗ trợ quyết định**: Cung cấp dự báo và phân tích thông minh

## 1.7. Bố cục đồ án

| Chương | Nội dung |
|--------|----------|
| **Chương 1** | Tổng quan đề tài - Giới thiệu vấn đề, mục tiêu, phạm vi |
| **Chương 2** | Cơ sở lý thuyết - ERP, Scheduling, ML, OR-Tools |
| **Chương 3** | Phân tích và thiết kế - Use Case, Database, Architecture |
| **Chương 4** | Hiện thực hệ thống - Coding, Integration |
| **Chương 5** | Kiểm thử và đánh giá - Testing, Results |
| **Chương 6** | Kết luận - Achievements, Future work |

---

# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

## 2.1. Tổng quan về ERP và ERPNext

### 2.1.1. Hệ thống ERP

**Enterprise Resource Planning (ERP)** là hệ thống phần mềm tích hợp quản lý toàn bộ hoạt động doanh nghiệp:

```
┌─────────────────────────────────────────────────────────────┐
│                         ERP SYSTEM                          │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│  Financial  │    HR &     │   Supply    │   Manufacturing │
│  Management │   Payroll   │    Chain    │    Management   │
├─────────────┼─────────────┼─────────────┼─────────────────┤
│ • GL/AP/AR  │ • Employees │ • Purchase  │ • BOM           │
│ • Budget    │ • Payroll   │ • Inventory │ • Work Order    │
│ • Reports   │ • Leaves    │ • Warehouse │ • Job Card      │
└─────────────┴─────────────┴─────────────┴─────────────────┘
```

### 2.1.2. ERPNext và Frappe Framework

**ERPNext** là hệ thống ERP mã nguồn mở được xây dựng trên **Frappe Framework**:

**Đặc điểm Frappe Framework:**

| Thành phần | Mô tả |
|------------|-------|
| **DocType** | Data model định nghĩa cấu trúc dữ liệu |
| **Controller** | Python class xử lý business logic |
| **API** | REST API tự động từ DocType |
| **Hooks** | Event-driven customization |
| **Desk** | Web-based admin interface |

**Kiến trúc Frappe:**

```
┌─────────────────────────────────────────────────────────────┐
│                      FRAPPE FRAMEWORK                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Web Server │  │  Socket.IO  │  │  Background Worker  │  │
│  │  (Gunicorn) │  │  (Realtime) │  │  (Redis Queue)      │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│         └────────────────┼─────────────────────┘             │
│                          │                                   │
│  ┌───────────────────────┴───────────────────────────────┐  │
│  │                   FRAPPE CORE                          │  │
│  │  • DocType Engine    • Permission System               │  │
│  │  • Database ORM      • File Manager                    │  │
│  │  • REST API          • Email Queue                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                          │                                   │
│  ┌───────────────────────┴───────────────────────────────┐  │
│  │           DATABASE (MariaDB) + CACHE (Redis)           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.1.3. ERPNext Manufacturing Module

**Các DocTypes chính trong Manufacturing:**

| DocType | Chức năng |
|---------|-----------|
| **Item** | Quản lý sản phẩm, nguyên vật liệu |
| **BOM** | Định mức nguyên vật liệu |
| **Workstation** | Máy móc, trạm làm việc |
| **Operation** | Công đoạn sản xuất |
| **Production Plan** | Kế hoạch sản xuất tổng thể |
| **Work Order** | Lệnh sản xuất cụ thể |
| **Job Card** | Phiếu công việc cho từng công đoạn |

**Luồng sản xuất trong ERPNext:**

```
Sales Order → Production Plan → Work Order → Job Card → Stock Entry
     │              │               │            │           │
     │              │               │            │           │
     ▼              ▼               ▼            ▼           ▼
  Nhu cầu      Kế hoạch        Lệnh SX     Thực hiện    Nhập kho
  khách hàng   sản xuất        chi tiết    công đoạn    thành phẩm
```

## 2.2. Lập lịch sản xuất (Production Scheduling)

### 2.2.1. Khái niệm

**Lập lịch sản xuất** là quá trình phân bổ nguồn lực (máy móc, nhân công, thời gian) để thực hiện các công việc sản xuất một cách hiệu quả.

**Các yếu tố cần xem xét:**

- **Jobs (công việc)**: Danh sách các lệnh sản xuất cần hoàn thành
- **Machines (máy)**: Tài nguyên thực hiện công việc
- **Operations (công đoạn)**: Các bước cần thực hiện cho mỗi job
- **Constraints (ràng buộc)**: Thứ tự, thời gian, khả năng máy

### 2.2.2. Các phương pháp lập lịch

| Phương pháp | Mô tả | Ưu điểm | Nhược điểm |
|-------------|-------|---------|------------|
| **FIFO** | First In First Out | Đơn giản, công bằng | Không tối ưu |
| **SPT** | Shortest Processing Time | Giảm thời gian chờ | Có thể trễ job dài |
| **EDD** | Earliest Due Date | Giảm trễ hạn | Không xét thời gian xử lý |
| **Priority** | Theo độ ưu tiên | Linh hoạt | Cần xác định ưu tiên |
| **Optimization** | Tối ưu hóa toán học | Tối ưu toàn cục | Phức tạp, tốn thời gian |

### 2.2.3. Các chiến lược lập lịch

**Forward Scheduling (Lập lịch tiến):**
- Bắt đầu từ thời điểm hiện tại
- Lập lịch theo thứ tự công đoạn
- Xác định ngày hoàn thành sớm nhất

**Backward Scheduling (Lập lịch lùi):**
- Bắt đầu từ ngày đáo hạn (due date)
- Lập lịch ngược về hiện tại
- Xác định ngày bắt đầu muộn nhất

```
Forward:  Start ──────────────────────────────────> Finish
          |--Op1--|--Op2--|--Op3--|              Due Date
                                                    ▲
                                                    │
Backward: Start <────────────────────────────────── Due Date
                              |--Op1--|--Op2--|--Op3--|
```

## 2.3. Bài toán Job Shop Scheduling

### 2.3.1. Định nghĩa bài toán

**Job Shop Scheduling Problem (JSSP)** là bài toán NP-hard kinh điển:

**Đầu vào:**
- Tập hợp **n** jobs: J = {J₁, J₂, ..., Jₙ}
- Tập hợp **m** machines: M = {M₁, M₂, ..., Mₘ}
- Mỗi job có tập operations với thứ tự xác định
- Mỗi operation cần một máy cụ thể với thời gian xử lý

**Đầu ra:**
- Lịch trình: Thời gian bắt đầu và kết thúc mỗi operation
- Phân bổ máy cho mỗi operation

**Ràng buộc:**
1. **Precedence**: Operations trong một job phải theo thứ tự
2. **No-overlap**: Một máy không thể xử lý 2 operations cùng lúc
3. **No-preemption**: Operation không bị gián đoạn

### 2.3.2. Mục tiêu tối ưu

| Mục tiêu | Công thức | Ý nghĩa |
|----------|-----------|---------|
| **Makespan** | Cₘₐₓ = max(Cᵢ) | Thời gian hoàn thành tất cả jobs |
| **Total Tardiness** | ΣTᵢ = Σmax(0, Cᵢ - dᵢ) | Tổng độ trễ |
| **Late Jobs** | ΣUᵢ (Uᵢ = 1 nếu Cᵢ > dᵢ) | Số jobs trễ hạn |
| **Utilization** | Σ(busy time) / Σ(available time) | Hiệu suất sử dụng máy |

### 2.3.3. Ví dụ minh họa

```
Jobs:
  J1: O11(M1, 3) → O12(M2, 2) → O13(M3, 2)
  J2: O21(M1, 2) → O22(M3, 4)
  J3: O31(M2, 3) → O32(M1, 2) → O33(M3, 1)

Gantt Chart (một lời giải):
        0   1   2   3   4   5   6   7   8   9  10  11
M1:     [--J1-O11--][J2-O21][---J3-O32--]
M2:                 [--J1-O12--][---J3-O31---]
M3:     [------J2-O22------][J1-O13][J3]

Makespan = 11
```

## 2.4. OR-Tools và CP-SAT Solver

### 2.4.1. Giới thiệu OR-Tools

**Google OR-Tools** là thư viện mã nguồn mở cho các bài toán tối ưu hóa:

- **Constraint Programming**: CP-SAT Solver
- **Linear Programming**: GLOP, SCIP
- **Vehicle Routing**: VRP solver
- **Graph Algorithms**: Network flows

### 2.4.2. CP-SAT Solver

**Constraint Programming with SAT** kết hợp:
- **Constraint Programming**: Mô hình hóa ràng buộc
- **SAT Solving**: Kỹ thuật giải Boolean Satisfiability
- **Lazy Clause Generation**: Học ràng buộc động

**Các loại biến:**

| Loại biến | Mô tả | Ví dụ |
|-----------|-------|-------|
| **IntVar** | Biến số nguyên | start_time, end_time |
| **BoolVar** | Biến Boolean | is_assigned, is_late |
| **IntervalVar** | Biến khoảng thời gian | task_interval |

### 2.4.3. Mô hình hóa JSSP với CP-SAT

**Pseudo-code:**

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()

# 1. Tạo biến cho mỗi operation
for job in jobs:
    for op in job.operations:
        start = model.NewIntVar(0, horizon, f'start_{job}_{op}')
        end = model.NewIntVar(0, horizon, f'end_{job}_{op}')
        interval = model.NewIntervalVar(start, op.duration, end, f'interval_{job}_{op}')

# 2. Ràng buộc precedence
for job in jobs:
    for i in range(len(job.operations) - 1):
        model.Add(end[job][i] <= start[job][i+1])

# 3. Ràng buộc no-overlap trên mỗi máy
for machine in machines:
    machine_intervals = [interval for op in operations if op.machine == machine]
    model.AddNoOverlap(machine_intervals)

# 4. Mục tiêu: minimize makespan
makespan = model.NewIntVar(0, horizon, 'makespan')
model.AddMaxEquality(makespan, all_ends)
model.Minimize(makespan)

# 5. Giải
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 300
status = solver.Solve(model)
```

### 2.4.4. Kỹ thuật tối ưu hiệu năng

| Kỹ thuật | Mô tả |
|----------|-------|
| **Symmetry Breaking** | Loại bỏ lời giải đối xứng |
| **Search Strategies** | Ưu tiên biến/giá trị heuristic |
| **Hints** | Cung cấp lời giải khởi đầu |
| **Time Limit** | Giới hạn thời gian tìm kiếm |
| **Parallel Search** | Tìm kiếm song song đa luồng |

## 2.5. Dự báo nhu cầu (Demand Forecasting)

### 2.5.1. Tầm quan trọng

**Dự báo nhu cầu** là bước đầu tiên trong chuỗi lập kế hoạch:

```
Dự báo nhu cầu → Kế hoạch sản xuất → MRP → Lập lịch → Thực hiện
```

### 2.5.2. Các phương pháp dự báo

#### ARIMA (AutoRegressive Integrated Moving Average)

**Công thức:**

```
ARIMA(p, d, q):
- p: bậc tự hồi quy (AR)
- d: bậc sai phân (I)
- q: bậc trung bình trượt (MA)

Yₜ = c + Σφᵢ·Yₜ₋ᵢ + Σθⱼ·εₜ₋ⱼ + εₜ
```

**Ưu điểm:**
- Tự động xác định tham số
- Xử lý tốt dữ liệu có xu hướng
- Phù hợp chuỗi thời gian ngắn

**Nhược điểm:**
- Yêu cầu dữ liệu ổn định
- Khó xử lý mùa vụ phức tạp

#### Prophet (Facebook)

**Mô hình:**

```
y(t) = g(t) + s(t) + h(t) + εₜ

- g(t): xu hướng (trend)
- s(t): tính mùa vụ (seasonality)
- h(t): ảnh hưởng ngày lễ (holidays)
- εₜ: nhiễu
```

**Ưu điểm:**
- Xử lý tốt mùa vụ nhiều cấp
- Tự động phát hiện điểm thay đổi
- Dễ sử dụng, ít cần tuning

**Nhược điểm:**
- Cần nhiều dữ liệu (≥ 2 năm)
- Có thể overfitting

#### Linear Regression

**Công thức:**

```
y = β₀ + β₁·x₁ + β₂·x₂ + ... + εᵢ
```

**Ưu điểm:**
- Đơn giản, nhanh
- Dễ giải thích
- Hoạt động tốt với ít dữ liệu

**Nhược điểm:**
- Giả định tuyến tính
- Không bắt được patterns phức tạp

### 2.5.3. So sánh các mô hình

| Tiêu chí | ARIMA | Prophet | Linear Regression |
|----------|-------|---------|-------------------|
| **Dữ liệu tối thiểu** | 30 điểm | 365 điểm | 10 điểm |
| **Xử lý xu hướng** | Tốt | Rất tốt | Tốt |
| **Xử lý mùa vụ** | Trung bình | Rất tốt | Kém |
| **Tốc độ** | Nhanh | Trung bình | Rất nhanh |
| **Độ phức tạp** | Cao | Trung bình | Thấp |

### 2.5.4. Đánh giá độ chính xác

**MAPE (Mean Absolute Percentage Error):**

```
MAPE = (1/n) × Σ |Actual - Forecast| / |Actual| × 100%
```

**Interpretation:**
| MAPE | Đánh giá |
|------|----------|
| < 10% | Rất tốt |
| 10-20% | Tốt |
| 20-30% | Chấp nhận được |
| > 30% | Cần cải thiện |

## 2.6. Hoạch định nhu cầu vật tư (MRP)

### 2.6.1. Khái niệm MRP

**Material Requirements Planning (MRP)** tính toán:
- **Cần gì?** (What): Nguyên vật liệu nào?
- **Cần bao nhiêu?** (How much): Số lượng?
- **Cần khi nào?** (When): Thời điểm cần có?

### 2.6.2. Đầu vào MRP

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Master         │     │       BOM       │     │    Inventory    │
│  Production     │     │  (Bill of       │     │    Records      │
│  Schedule       │     │  Materials)     │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │       MRP Engine       │
                    └────────────┬───────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Planned        │     │   Purchase      │     │    Exception    │
│  Work Orders    │     │   Requisitions  │     │    Reports      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 2.6.3. Logic MRP

**Công thức cơ bản:**

```
Net Requirements = Gross Requirements - On Hand - Scheduled Receipts + Safety Stock
```

**Ví dụ:**

| Tuần | Gross Req | Scheduled | On Hand | Net Req | Planned Order |
|------|-----------|-----------|---------|---------|---------------|
| 1 | 100 | 0 | 50 | 50 | 50 |
| 2 | 80 | 20 | 0 | 60 | 60 |
| 3 | 120 | 0 | 0 | 120 | 120 |

### 2.6.4. BOM Explosion

**BOM (Bill of Materials)** mô tả cấu trúc sản phẩm:

```
Finished Product (Level 0)
├── Sub-assembly A (Level 1) × 2
│   ├── Component X (Level 2) × 3
│   └── Component Y (Level 2) × 1
└── Sub-assembly B (Level 1) × 1
    └── Component Z (Level 2) × 4
```

**Explosion tính toán:**
- 100 Finished Product cần:
  - 200 Sub-assembly A
  - 600 Component X
  - 200 Component Y
  - 100 Sub-assembly B
  - 400 Component Z

## 2.7. Reinforcement Learning trong lập lịch

### 2.7.1. Khái niệm

**Reinforcement Learning (RL)** là phương pháp học máy:
- Agent tương tác với environment
- Nhận reward/penalty từ actions
- Học policy tối đa hóa cumulative reward

```
                    ┌───────────────┐
                    │  Environment  │
                    │  (Scheduling) │
                    └───────┬───────┘
                            │
            ┌───────────────┼───────────────┐
            │ State         │ Reward        │
            ▼               ▼               │
      ┌───────────────────────────────────┐ │
      │            Agent (RL)              │ │
      │  ┌─────────┐    ┌─────────────┐   │ │
      │  │ Policy  │    │   Value     │   │ │
      │  │ Network │    │   Network   │   │ │
      │  └─────────┘    └─────────────┘   │ │
      └───────────────────────────────────┘ │
                        │                   │
                        │ Action            │
                        └───────────────────┘
```

### 2.7.2. Mô hình hóa JSSP với RL

**State (Trạng thái):**
- Thời gian hiện tại
- Trạng thái các máy (idle/busy)
- Hàng đợi jobs chờ xử lý
- Thời gian còn lại đến deadline

**Action (Hành động):**
- Chọn job tiếp theo để xử lý
- Chọn máy để thực hiện

**Reward (Phần thưởng):**
- +R khi hoàn thành đúng hạn
- -P penalty khi trễ hạn
- Bonus cho makespan ngắn

### 2.7.3. Thuật toán RL

#### PPO (Proximal Policy Optimization)

**Đặc điểm:**
- On-policy algorithm
- Stable training với clipped objective
- Phù hợp continuous và discrete actions

**Objective:**

```
L(θ) = E[min(rₜ(θ)Aₜ, clip(rₜ(θ), 1-ε, 1+ε)Aₜ)]

rₜ(θ) = πθ(aₜ|sₜ) / πθ_old(aₜ|sₜ)
```

#### SAC (Soft Actor-Critic)

**Đặc điểm:**
- Off-policy algorithm
- Maximum entropy framework
- Tự động tuning temperature

**Objective:**

```
J(π) = Σ E[r(sₜ, aₜ) + α·H(π(·|sₜ))]
```

### 2.7.4. So sánh OR-Tools vs RL

| Tiêu chí | OR-Tools | Reinforcement Learning |
|----------|----------|------------------------|
| **Approach** | Mathematical optimization | Learning-based |
| **Training** | Không cần | Cần nhiều dữ liệu |
| **Adaptability** | Cần re-solve | Thích ứng nhanh |
| **Optimality** | Chứng minh được | Không đảm bảo |
| **Speed (inference)** | Tùy bài toán | Rất nhanh |
| **Scalability** | Giới hạn | Tốt hơn |

## 2.8. Large Language Models (LLM) trong phân tích

### 2.8.1. Ứng dụng LLM

**Large Language Models** (GPT-4, etc.) được sử dụng:

- **Giải thích kết quả**: Mô tả lịch trình bằng ngôn ngữ tự nhiên
- **Phân tích bottleneck**: Xác định điểm nghẽn
- **Đề xuất cải thiện**: Gợi ý điều chỉnh
- **Trả lời câu hỏi**: Hỗ trợ người dùng

### 2.8.2. Prompt Engineering

**Cấu trúc prompt cho phân tích scheduling:**

```
Context: Kết quả lập lịch sản xuất với các thông tin:
- Makespan: {value} phút
- Late jobs: {count}
- Machine utilization: {percent}%
- So sánh với FIFO: {improvement}%

Task: Phân tích kết quả và đưa ra:
1. Đánh giá tổng quan
2. Các điểm mạnh/yếu
3. Đề xuất cải thiện
4. Các rủi ro tiềm ẩn

Output format: Markdown với các heading rõ ràng
Language: {vi/en}
```

### 2.8.3. Tích hợp OpenAI API

**Kiến trúc tích hợp:**

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Scheduling     │     │   UIT APS       │     │   OpenAI API    │
│  Results        │────▶│   Backend       │────▶│   (ChatGPT)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                        │
                               │                        │
                               ▼                        ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │  Prompt Builder │     │   AI Response   │
                        └─────────────────┘     └─────────────────┘
```

---

# CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

## 3.1. Phân tích yêu cầu

### 3.1.1. Yêu cầu chức năng

#### Module Dự báo (Forecasting)

| ID | Yêu cầu | Mô tả | Độ ưu tiên |
|----|---------|-------|------------|
| FR-FC-001 | Chạy dự báo nhu cầu | Hệ thống cho phép chạy dự báo với các tham số tùy chỉnh | Cao |
| FR-FC-002 | Lựa chọn mô hình | Hỗ trợ ARIMA, Prophet, Linear Regression | Cao |
| FR-FC-003 | Phân loại tốc độ tiêu thụ | Tự động phân loại Fast/Slow/Non Moving | Trung bình |
| FR-FC-004 | Cảnh báo tồn kho | Hiển thị cảnh báo reorder khi cần | Cao |
| FR-FC-005 | Lưu trữ lịch sử | Lưu tất cả lần chạy và kết quả | Cao |

#### Module Kế hoạch sản xuất (Production Planning)

| ID | Yêu cầu | Mô tả | Độ ưu tiên |
|----|---------|-------|------------|
| FR-PP-001 | Tạo kế hoạch từ dự báo | Tạo Production Plan từ Forecast Result | Cao |
| FR-PP-002 | Quản lý items | Thêm/sửa/xóa items trong kế hoạch | Cao |
| FR-PP-003 | Workflow trạng thái | Draft → Planned → Released → Completed | Cao |

#### Module MRP

| ID | Yêu cầu | Mô tả | Độ ưu tiên |
|----|---------|-------|------------|
| FR-MRP-001 | Chạy MRP | Tính toán nhu cầu vật tư từ Production Plan | Cao |
| FR-MRP-002 | Hiển thị thiếu hụt | Liệt kê vật tư thiếu và số lượng | Cao |
| FR-MRP-003 | Đề xuất mua hàng | Tạo Purchase Suggestion tự động | Cao |
| FR-MRP-004 | Phê duyệt mua | Workflow phê duyệt đề xuất mua | Trung bình |

#### Module Lập lịch (Scheduling)

| ID | Yêu cầu | Mô tả | Độ ưu tiên |
|----|---------|-------|------------|
| FR-SC-001 | Chạy lập lịch | Chạy OR-Tools solver với các ràng buộc | Cao |
| FR-SC-002 | Áp dụng ràng buộc | 6 loại constraints cấu hình được | Cao |
| FR-SC-003 | Tối ưu đa mục tiêu | Makespan + Tardiness với weights | Cao |
| FR-SC-004 | Hiển thị Gantt | Visualization lịch trình trên Gantt chart | Cao |
| FR-SC-005 | So sánh baseline | Tự động so sánh với FIFO | Trung bình |
| FR-SC-006 | Áp dụng kết quả | Cập nhật Job Cards với thời gian lập lịch | Cao |
| FR-SC-007 | Multi-tier | Hỗ trợ OR-Tools, RL Agent, GNN | Thấp |

#### Module AI Analysis

| ID | Yêu cầu | Mô tả | Độ ưu tiên |
|----|---------|-------|------------|
| FR-AI-001 | Phân tích bằng AI | Gọi ChatGPT phân tích kết quả | Trung bình |
| FR-AI-002 | Cấu hình API | Quản lý OpenAI API key | Cao |

#### Module RL Training

| ID | Yêu cầu | Mô tả | Độ ưu tiên |
|----|---------|-------|------------|
| FR-RL-001 | Huấn luyện agent | Chạy training PPO/SAC | Thấp |
| FR-RL-002 | Theo dõi tiến độ | Dashboard training progress | Thấp |

#### Module Work Shift

| ID | Yêu cầu | Mô tả | Độ ưu tiên |
|----|---------|-------|------------|
| FR-WS-001 | Quản lý ca làm việc | CRUD operations cho Work Shift | Trung bình |

### 3.1.2. Yêu cầu phi chức năng

#### Hiệu năng

| ID | Yêu cầu | Chỉ số |
|----|---------|--------|
| NFR-P-001 | Dự báo 100 items | ≤ 60 giây |
| NFR-P-002 | MRP 50 items | ≤ 30 giây |
| NFR-P-003 | Lập lịch 100 jobs | ≤ 300 giây |
| NFR-P-004 | Lập lịch 500 jobs | ≤ 600 giây |
| NFR-P-005 | Load Gantt chart | ≤ 5 giây |

#### Độ tin cậy

| ID | Yêu cầu | Chỉ số |
|----|---------|--------|
| NFR-R-001 | Độ chính xác dự báo | MAPE ≤ 30% |
| NFR-R-002 | Cải thiện makespan | ≥ 10% vs FIFO |
| NFR-R-003 | Giảm jobs trễ | ≥ 20% vs FIFO |
| NFR-R-004 | Uptime | ≥ 99% |

#### Bảo mật

| ID | Yêu cầu | Mô tả |
|----|---------|-------|
| NFR-S-001 | Xác thực | Sử dụng Frappe authentication |
| NFR-S-002 | Phân quyền | Role-based permissions |
| NFR-S-003 | API Key | Mã hóa API key trong database |

#### Khả năng sử dụng

| ID | Yêu cầu | Mô tả |
|----|---------|-------|
| NFR-U-001 | Đa ngôn ngữ | Hỗ trợ tiếng Việt và tiếng Anh |
| NFR-U-002 | Tích hợp UI | Tuân thủ ERPNext design system |
| NFR-U-003 | Hướng dẫn | Tooltip và description cho fields |

### 3.1.3. Actors và Use Cases

**Actors:**

| Actor | Mô tả | Quyền hạn |
|-------|-------|-----------|
| Production Manager | Quản lý sản xuất | Toàn quyền APS |
| Production Planner | Nhân viên lập kế hoạch | Tạo/chạy forecast, plan |
| Shop Floor User | Nhân viên xưởng | Xem lịch trình, Gantt |
| System Admin | Quản trị hệ thống | Cấu hình, API settings |

## 3.2. Kiến trúc hệ thống

### 3.2.1. Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │  ERPNext Desk   │  │  Gantt Chart    │  │   Dashboard/Reports     │  │
│  │  (Forms, Lists) │  │  (Visualization)│  │   (Analytics)           │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ REST API / WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                               │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                       UIT APS MODULE                             │    │
│  ├─────────────┬─────────────┬─────────────┬───────────────────────┤    │
│  │ Forecasting │ Production  │     MRP     │     Scheduling        │    │
│  │   Module    │  Planning   │   Module    │      Module           │    │
│  ├─────────────┼─────────────┼─────────────┼───────────────────────┤    │
│  │ • ARIMA     │ • Planning  │ • Material  │ • OR-Tools Solver     │    │
│  │ • Prophet   │ • Items     │   Calc      │ • Constraints         │    │
│  │ • Linear    │ • Workflow  │ • Purchase  │ • Gantt Generation    │    │
│  │   Regression│             │   Suggest   │ • Baseline Compare    │    │
│  └─────────────┴─────────────┴─────────────┴───────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      SUPPORTING MODULES                          │    │
│  ├─────────────────────┬─────────────────────┬─────────────────────┤    │
│  │    AI Analysis      │    RL Training      │    Work Shift       │    │
│  │    (OpenAI API)     │    (PPO/SAC)        │    Management       │    │
│  └─────────────────────┴─────────────────────┴─────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         INTEGRATION LAYER                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    ERPNext Manufacturing                         │    │
│  ├─────────────┬─────────────┬─────────────┬───────────────────────┤    │
│  │    Item     │    BOM      │ Work Order  │      Job Card         │    │
│  │   Master    │             │             │                       │    │
│  ├─────────────┼─────────────┼─────────────┼───────────────────────┤    │
│  │ Workstation │  Operation  │ Production  │   Stock Entry         │    │
│  │             │             │    Plan     │                       │    │
│  └─────────────┴─────────────┴─────────────┴───────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │    MariaDB      │  │     Redis       │  │     File Storage        │  │
│  │  (Primary DB)   │  │   (Cache/Queue) │  │   (ML Models, Logs)     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │   OpenAI API    │  │   Google        │  │      PyTorch            │  │
│  │   (ChatGPT)     │  │   OR-Tools      │  │   (RL Training)         │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2.2. Module Dependencies

```
┌──────────────────────────────────────────────────────────────────┐
│                        UIT APS MODULES                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐                                              │
│  │  Forecasting    │──────┐                                       │
│  │  Module         │      │                                       │
│  └─────────────────┘      │                                       │
│                           ▼                                       │
│                    ┌─────────────────┐                            │
│                    │  Production     │                            │
│                    │  Planning       │                            │
│                    └─────────────────┘                            │
│                           │                                       │
│              ┌────────────┴────────────┐                          │
│              ▼                         ▼                          │
│  ┌─────────────────┐         ┌─────────────────┐                  │
│  │      MRP        │         │   Scheduling    │                  │
│  │    Module       │         │    Module       │◀── AI Analysis   │
│  └─────────────────┘         └─────────────────┘                  │
│              │                         │                          │
│              ▼                         ▼                          │
│  ┌─────────────────┐         ┌─────────────────┐                  │
│  │    Purchase     │         │   Job Card      │                  │
│  │   Suggestion    │         │   Update        │                  │
│  └─────────────────┘         └─────────────────┘                  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2.3. Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Sales Order │────▶│  Forecast   │────▶│  Forecast   │
│   History   │     │    Run      │     │   Result    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │ Production  │
                                        │    Plan     │
                                        └──────┬──────┘
                                               │
                          ┌────────────────────┴────────────────────┐
                          │                                         │
                          ▼                                         ▼
                   ┌─────────────┐                           ┌─────────────┐
                   │   MRP Run   │                           │ Scheduling  │
                   └──────┬──────┘                           │    Run      │
                          │                                  └──────┬──────┘
                          ▼                                         │
          ┌───────────────┴───────────────┐                         ▼
          │                               │                  ┌─────────────┐
          ▼                               ▼                  │ Scheduling  │
   ┌─────────────┐                 ┌─────────────┐           │   Result    │
   │ MRP Result  │                 │  Purchase   │           └──────┬──────┘
   │(Material Req)│                │ Suggestion  │                  │
   └─────────────┘                 └─────────────┘                  ▼
                                                             ┌─────────────┐
                                                             │  Job Card   │
                                                             │  (Updated)  │
                                                             └─────────────┘
```

## 3.3. Thiết kế Use Case

### 3.3.1. Use Case Diagram tổng quan

```
                            ┌─────────────────────────────────────────┐
                            │              UIT APS System              │
                            │                                         │
   ┌──────────┐             │  ┌─────────────────────────────────┐   │
   │Production│             │  │                                 │   │
   │ Manager  │─────────────┼─▶│  UC-01: Run Demand Forecast     │   │
   └──────────┘             │  │                                 │   │
        │                   │  └─────────────────────────────────┘   │
        │                   │                                         │
        │                   │  ┌─────────────────────────────────┐   │
        ├───────────────────┼─▶│  UC-02: Create Production Plan  │   │
        │                   │  └─────────────────────────────────┘   │
        │                   │                                         │
        │                   │  ┌─────────────────────────────────┐   │
        ├───────────────────┼─▶│  UC-03: Run MRP Calculation     │   │
        │                   │  └─────────────────────────────────┘   │
        │                   │                                         │
        │                   │  ┌─────────────────────────────────┐   │
        ├───────────────────┼─▶│  UC-04: Run Production Schedule │   │
        │                   │  └─────────────────────────────────┘   │
        │                   │                                         │
        │                   │  ┌─────────────────────────────────┐   │
        └───────────────────┼─▶│  UC-05: View Gantt Chart        │   │
                            │  └─────────────────────────────────┘   │
                            │                                         │
   ┌──────────┐             │  ┌─────────────────────────────────┐   │
   │Production│             │  │                                 │   │
   │ Planner  │─────────────┼─▶│  UC-06: Approve Schedule        │   │
   └──────────┘             │  │                                 │   │
        │                   │  └─────────────────────────────────┘   │
        │                   │                                         │
        │                   │  ┌─────────────────────────────────┐   │
        └───────────────────┼─▶│  UC-07: Analyze with AI         │   │
                            │  └─────────────────────────────────┘   │
                            │                                         │
   ┌──────────┐             │  ┌─────────────────────────────────┐   │
   │  System  │             │  │                                 │   │
   │  Admin   │─────────────┼─▶│  UC-08: Configure API Settings  │   │
   └──────────┘             │  │                                 │   │
        │                   │  └─────────────────────────────────┘   │
        │                   │                                         │
        │                   │  ┌─────────────────────────────────┐   │
        └───────────────────┼─▶│  UC-09: Manage Work Shifts      │   │
                            │  └─────────────────────────────────┘   │
                            │                                         │
   ┌──────────┐             │  ┌─────────────────────────────────┐   │
   │Shop Floor│             │  │                                 │   │
   │   User   │─────────────┼─▶│  UC-10: View Job Schedule       │   │
   └──────────┘             │  │                                 │   │
                            │  └─────────────────────────────────┘   │
                            │                                         │
                            └─────────────────────────────────────────┘
```

### 3.3.2. Mô tả Use Case chi tiết

#### UC-01: Run Demand Forecast

| Thành phần | Mô tả |
|------------|-------|
| **Actor** | Production Manager, Production Planner |
| **Mục đích** | Dự báo nhu cầu sản xuất dựa trên dữ liệu lịch sử |
| **Precondition** | Có dữ liệu Sales Order lịch sử ≥ 30 ngày |
| **Postcondition** | Tạo Forecast History và Forecast Results |
| **Main Flow** | 1. Actor chọn tham số (company, model, horizon) |
|              | 2. System thu thập dữ liệu lịch sử |
|              | 3. System chạy mô hình dự báo đã chọn |
|              | 4. System tạo Forecast Results với confidence scores |
|              | 5. System hiển thị kết quả và recommendations |
| **Alternative Flow** | 3a. Nếu data không đủ, hiển thị warning |
|                     | 4a. Nếu model fail, fallback to simpler model |
| **Exception** | Không có dữ liệu lịch sử → Error message |

#### UC-04: Run Production Schedule

| Thành phần | Mô tả |
|------------|-------|
| **Actor** | Production Manager, Production Planner |
| **Mục đích** | Lập lịch sản xuất tối ưu cho Work Orders |
| **Precondition** | Có Production Plan với status Planned/Released |
|                 | Có Work Orders và Job Cards tương ứng |
| **Postcondition** | Tạo Scheduling Run với Results |
|                  | Job Cards được cập nhật thời gian |
| **Main Flow** | 1. Actor chọn Production Plan |
|              | 2. Actor cấu hình solver (strategy, tier, time limit) |
|              | 3. System load Work Orders và Job Cards |
|              | 4. System build constraint model |
|              | 5. System chạy OR-Tools solver |
|              | 6. System tạo Scheduling Results |
|              | 7. System tính baseline FIFO để so sánh |
|              | 8. System hiển thị Gantt chart và metrics |
| **Alternative Flow** | 5a. Nếu timeout, return best found solution |
|                     | 5b. Nếu infeasible, suggest constraint relaxation |
| **Exception** | Không có Job Cards → Error message |

## 3.4. Thiết kế Activity Diagram

### 3.4.1. Activity Diagram - Quy trình lập lịch sản xuất

```
                              ┌─────────────────┐
                              │      Start      │
                              └────────┬────────┘
                                       │
                                       ▼
                         ┌─────────────────────────┐
                         │  Select Production Plan │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Configure Solver Params │
                         │ • Strategy              │
                         │ • Time Limit            │
                         │ • Weights               │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │   Load Work Orders &    │
                         │      Job Cards          │
                         └────────────┬────────────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │   Has Jobs?   │
                              └───────┬───────┘
                                      │
                     ┌────────────────┴────────────────┐
                     │ No                              │ Yes
                     ▼                                 ▼
            ┌─────────────────┐              ┌─────────────────────────┐
            │  Return Error   │              │   Build Constraints     │
            └─────────────────┘              │   • Machine eligibility │
                                             │   • Precedence          │
                                             │   • No overlap          │
                                             │   • Working hours       │
                                             │   • Due dates           │
                                             └────────────┬────────────┘
                                                          │
                                                          ▼
                                             ┌─────────────────────────┐
                                             │    Run OR-Tools Solver  │
                                             └────────────┬────────────┘
                                                          │
                                                          ▼
                                                  ┌───────────────┐
                                                  │ Solver Status │
                                                  └───────┬───────┘
                                                          │
                              ┌────────────────┬──────────┼──────────┬────────────────┐
                              │                │          │          │                │
                              ▼                ▼          ▼          ▼                ▼
                       ┌──────────┐     ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
                       │ Optimal  │     │ Feasible │ │ Timeout  │ │Infeasible│ │  Error   │
                       └────┬─────┘     └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
                            │                │           │            │            │
                            └────────────────┼───────────┘            │            │
                                             │                        │            │
                                             ▼                        ▼            ▼
                              ┌─────────────────────────┐   ┌─────────────────────────┐
                              │  Generate Scheduling    │   │    Log Error and        │
                              │       Results           │   │    Return Warning       │
                              └────────────┬────────────┘   └─────────────────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │   Run FIFO Baseline     │
                              │     for Comparison      │
                              └────────────┬────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │  Calculate Improvements │
                              │  • Makespan %           │
                              │  • Late Jobs %          │
                              │  • Tardiness %          │
                              └────────────┬────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │   Generate Gantt Data   │
                              └────────────┬────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │     Update Status:      │
                              │   "Pending Approval"    │
                              └────────────┬────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │        End              │
                              └─────────────────────────┘
```

### 3.4.2. Activity Diagram - Quy trình dự báo nhu cầu

```
                              ┌─────────────────┐
                              │      Start      │
                              └────────┬────────┘
                                       │
                                       ▼
                         ┌─────────────────────────┐
                         │  Select Forecast Params │
                         │  • Company              │
                         │  • Date Range           │
                         │  • ML Model             │
                         │  • Forecast Horizon     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │   Query Sales Orders    │
                         │   (Historical Data)     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │ Enough Data?  │
                              │   (≥30 pts)   │
                              └───────┬───────┘
                                      │
                     ┌────────────────┴────────────────┐
                     │ No                              │ Yes
                     ▼                                 ▼
            ┌─────────────────┐              ┌─────────────────────────┐
            │ Return Warning  │              │   Group by Item         │
            │ "Not enough     │              │   Aggregate quantities  │
            │  data"          │              └────────────┬────────────┘
            └─────────────────┘                           │
                                                          ▼
                                               ┌──────────────────────┐
                                               │   For Each Item:     │
                                               └──────────┬───────────┘
                                                          │
                                      ┌───────────────────┴───────────────────┐
                                      │                                       │
                                      ▼                                       │
                         ┌─────────────────────────┐                          │
                         │   Run ML Model:         │                          │
                         │   ARIMA / Prophet / LR  │                          │
                         └────────────┬────────────┘                          │
                                      │                                       │
                                      ▼                                       │
                         ┌─────────────────────────┐                          │
                         │   Calculate Metrics:    │                          │
                         │   • Forecast Qty        │                          │
                         │   • Confidence Score    │                          │
                         │   • Upper/Lower Bound   │                          │
                         └────────────┬────────────┘                          │
                                      │                                       │
                                      ▼                                       │
                         ┌─────────────────────────┐                          │
                         │   Classify Movement:    │                          │
                         │   Fast/Slow/Non Moving  │                          │
                         └────────────┬────────────┘                          │
                                      │                                       │
                                      ▼                                       │
                         ┌─────────────────────────┐                          │
                         │   Check Reorder Level   │                          │
                         │   Generate Alert?       │                          │
                         └────────────┬────────────┘                          │
                                      │                                       │
                                      ▼                                       │
                         ┌─────────────────────────┐                          │
                         │   Create Forecast       │                          │
                         │   Result Record         │◀─────────────────────────┘
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │  Calculate Overall MAPE │
                         │  Recommend Best Model   │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │  Save Forecast History  │
                         └────────────┬────────────┘
                                      │
                                      ▼
                              ┌─────────────────┐
                              │       End       │
                              └─────────────────┘
```

## 3.5. Thiết kế cơ sở dữ liệu

### 3.5.1. ERD - Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    UIT APS DATABASE SCHEMA                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
│  APS Forecast       │         │  APS Forecast       │         │  APS Production     │
│    History          │ 1     N │    History Item     │         │      Plan           │
├─────────────────────┤─────────├─────────────────────┤         ├─────────────────────┤
│ PK: name            │         │ PK: name            │         │ PK: name            │
│ run_name            │         │ FK: parent          │    1    │ FK: forecast_history│◀─┐
│ company             │         │ FK: item            │    │    │ plan_name           │  │
│ model_used          │         │ forecast_qty        │    │    │ company             │  │
│ run_status          │         │ confidence_score    │    │    │ status              │  │
│ run_start_time      │         │ movement_type       │    │    │ plan_from_period    │  │
│ run_end_time        │         │ reorder_alert       │    │    │ plan_to_period      │  │
│ forecast_horizon    │         └─────────────────────┘    │    │ source_type         │  │
│ total_items         │                                    │    │ time_granularity    │  │
│ overall_accuracy    │◀───────────────────────────────────┘    └──────────┬──────────┘  │
│ ai_analysis         │                                                    │             │
└─────────────────────┘                                                    │ 1           │
         │                                                                 │             │
         │ 1                                                               │             │
         │                                                                 ▼             │
         │         ┌─────────────────────┐                    ┌─────────────────────┐    │
         │         │  APS Forecast       │                    │  APS Production     │    │
         │    N    │     Result          │                    │    Plan Item        │    │
         └────────▶├─────────────────────┤               N    ├─────────────────────┤    │
                   │ PK: name            │◀───────────────────│ PK: name            │    │
                   │ FK: forecast_history│                    │ FK: parent          │    │
                   │ FK: item            │                    │ FK: item            │    │
                   │ forecast_period     │                    │ FK: forecast_result │    │
                   │ forecast_qty        │                    │ plan_period         │    │
                   │ confidence_score    │                    │ planned_qty         │    │
                   │ model_used          │                    │ safety_stock        │    │
                   │ trend_type          │                    │ lead_time_days      │    │
                   │ reorder_level       │                    └─────────────────────┘    │
                   │ safety_stock        │                                               │
                   │ arima_p/d/q         │                                               │
                   │ prophet_seasonality │                                               │
                   └─────────────────────┘                                               │
                                                                                         │
                                                                                         │
┌─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
│  │    APS MRP Run      │ 1     N │   APS MRP Result    │         │ APS Purchase        │
│  ├─────────────────────┤─────────├─────────────────────┤    N    │   Suggestion        │
│  │ PK: name            │         │ PK: name            │◀────────├─────────────────────┤
│  │ FK: production_plan │◀────────│ FK: mrp_run         │         │ PK: name            │
│  │ run_status          │    │    │ FK: material_item   │         │ FK: mrp_run         │
│  │ run_date            │    │    │ required_qty        │         │ FK: material_item   │
│  │ executed_by         │    │    │ available_qty       │         │ FK: supplier        │
│  │ total_materials     │    │    │ shortage_qty        │         │ purchase_qty        │
│  │ notes               │    │    │ required_date       │         │ required_date       │
│  └─────────────────────┘    │    └─────────────────────┘         │ unit_price          │
│                             │                                    │ lead_time           │
│                             │                                    │ suggestion_status   │
└─────────────────────────────┼────────────────────────────────────└─────────────────────┘
                              │
                              │ 1
                              │
┌─────────────────────────────┼────────────────────────────────────────────────────────────┐
│                             │                                                            │
│  ┌─────────────────────┐    │      ┌─────────────────────┐         ┌─────────────────────┐
│  │  APS Scheduling     │    │      │  APS Scheduling     │         │   APS Work Shift    │
│  │       Run           │    │ N    │      Result         │         ├─────────────────────┤
│  ├─────────────────────┤◀───┴──────├─────────────────────┤         │ PK: name            │
│  │ PK: name            │      1    │ PK: name            │    N    │ shift_name          │
│  │ FK: production_plan │───────────│ FK: scheduling_run  │◀────────│ start_time          │
│  │ run_status          │           │ FK: job_card        │         │ end_time            │
│  │ scheduling_strategy │           │ FK: workstation     │         │ working_hours       │
│  │ scheduling_tier     │           │ FK: operation       │         │ is_night_shift      │
│  │ run_date            │           │ FK: work_shift      │         │ is_active           │
│  │ solver_status       │           │ planned_start_time  │         └─────────────────────┘
│  │ time_limit_seconds  │           │ planned_end_time    │
│  │ makespan_minutes    │           │ is_applied          │         ┌─────────────────────┐
│  │ total_tardiness     │           │ is_late             │         │ APS RL Training Log │
│  │ machine_utilization │           │ delay_reason        │         ├─────────────────────┤
│  │ baseline_makespan   │           └─────────────────────┘         │ PK: name            │
│  │ improvement_%       │                                           │ FK: scheduling_run  │
│  │ llm_analysis        │                                           │ agent_type          │
│  │ constraints_*       │                                           │ training_status     │
│  └─────────────────────┘                                           │ max_episodes        │
│                                                                    │ learning_rate       │
└────────────────────────────────────────────────────────────────────│ best_reward         │
                                                                     │ model_path          │
                                                                     └─────────────────────┘


┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                              ERPNEXT MANUFACTURING TABLES                                  │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────┐  │
│  │      Item       │     │       BOM       │     │   Workstation   │     │  Operation  │  │
│  ├─────────────────┤     ├─────────────────┤     ├─────────────────┤     ├─────────────┤  │
│  │ item_code       │◀────│ item            │     │ workstation_name│◀────│ workstation │  │
│  │ item_name       │     │ bom_items       │     │ production_cap  │     │ name        │  │
│  │ item_group      │     │ operations      │     │ working_hours   │     │ time_mins   │  │
│  │ stock_uom       │     │ is_active       │     │ holiday_list    │     │ batch_size  │  │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────┘  │
│           │                      │                       │                     │          │
│           │                      │                       │                     │          │
│           ▼                      ▼                       ▼                     ▼          │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────────────────────┐  │
│  │  Production     │     │   Work Order    │     │              Job Card               │  │
│  │     Plan        │────▶├─────────────────┤────▶├─────────────────────────────────────┤  │
│  ├─────────────────┤     │ production_item │     │ work_order                          │  │
│  │ items           │     │ qty             │     │ operation                           │  │
│  │ status          │     │ bom_no          │     │ workstation                         │  │
│  └─────────────────┘     │ planned_start   │     │ for_quantity                        │  │
│                          │ planned_end     │     │ time_in_mins                        │  │
│                          │ status          │     │ scheduled_time_start (UIT APS)      │  │
│                          └─────────────────┘     │ scheduled_time_end   (UIT APS)      │  │
│                                                  └─────────────────────────────────────┘  │
│                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.5.2. Mô tả các bảng chính

#### Bảng tabAPS Scheduling Run

| Cột | Kiểu dữ liệu | Mô tả |
|-----|--------------|-------|
| name | VARCHAR(140) | Primary key (auto-generated) |
| production_plan | VARCHAR(140) | FK → Production Plan |
| run_status | VARCHAR(20) | Pending/Running/Completed/Failed |
| scheduling_strategy | VARCHAR(20) | Forward/Backward/Priority/EDD |
| scheduling_tier | VARCHAR(20) | Tier 1/2/3 |
| time_limit_seconds | INT | Solver time limit |
| makespan_weight | DECIMAL(10,2) | Weight for makespan objective |
| tardiness_weight | DECIMAL(10,2) | Weight for tardiness penalty |
| solver_status | VARCHAR(20) | Optimal/Feasible/Timeout/Infeasible |
| solve_time_seconds | DECIMAL(10,2) | Actual solve time |
| makespan_minutes | INT | Total makespan result |
| total_tardiness_minutes | INT | Total tardiness result |
| machine_utilization | DECIMAL(5,2) | Average machine utilization % |
| total_late_jobs | INT | Number of late jobs |
| baseline_makespan_minutes | INT | FIFO baseline makespan |
| improvement_makespan_percent | DECIMAL(5,2) | % improvement vs FIFO |
| llm_analysis_content | LONGTEXT | AI analysis result |
| constraint_* | TINYINT | Constraint flags |

#### Bảng tabAPS Scheduling Result

| Cột | Kiểu dữ liệu | Mô tả |
|-----|--------------|-------|
| name | VARCHAR(140) | Primary key |
| scheduling_run | VARCHAR(140) | FK → Scheduling Run |
| job_card | VARCHAR(140) | FK → Job Card |
| workstation | VARCHAR(140) | FK → Workstation |
| operation | VARCHAR(140) | FK → Operation |
| planned_start_time | DATETIME | Scheduled start time |
| planned_end_time | DATETIME | Scheduled end time |
| work_shift | VARCHAR(140) | FK → Work Shift (optional) |
| is_applied | TINYINT | Applied to Job Card? |
| is_late | TINYINT | Is job late? |
| delay_reason | VARCHAR(500) | Reason for delay |

#### Bảng tabAPS Forecast Result

| Cột | Kiểu dữ liệu | Mô tả |
|-----|--------------|-------|
| name | VARCHAR(140) | Primary key |
| forecast_history | VARCHAR(140) | FK → Forecast History |
| item | VARCHAR(140) | FK → Item |
| forecast_period | DATE | Forecast period |
| forecast_qty | DECIMAL(18,6) | Forecasted quantity |
| confidence_score | DECIMAL(5,2) | Confidence % |
| model_used | VARCHAR(20) | ARIMA/Prophet/LR |
| trend_type | VARCHAR(20) | Upward/Downward/Stable |
| movement_type | VARCHAR(20) | Fast/Slow/Non Moving |
| lower_bound | DECIMAL(18,6) | CI lower bound |
| upper_bound | DECIMAL(18,6) | CI upper bound |
| reorder_level | DECIMAL(18,6) | Suggested reorder level |
| safety_stock | DECIMAL(18,6) | Suggested safety stock |
| arima_p/d/q | INT | ARIMA parameters |
| prophet_seasonality_type | VARCHAR(20) | Detected seasonality |

### 3.5.3. Indexes và Performance

**Primary Indexes:**
```sql
-- Scheduling Run queries
CREATE INDEX idx_aps_scheduling_run_production_plan
ON `tabAPS Scheduling Run` (production_plan);

CREATE INDEX idx_aps_scheduling_run_status
ON `tabAPS Scheduling Run` (run_status);

-- Scheduling Result queries
CREATE INDEX idx_aps_scheduling_result_run
ON `tabAPS Scheduling Result` (scheduling_run);

CREATE INDEX idx_aps_scheduling_result_job_card
ON `tabAPS Scheduling Result` (job_card);

CREATE INDEX idx_aps_scheduling_result_workstation
ON `tabAPS Scheduling Result` (workstation);

-- Forecast queries
CREATE INDEX idx_aps_forecast_result_history
ON `tabAPS Forecast Result` (forecast_history);

CREATE INDEX idx_aps_forecast_result_item
ON `tabAPS Forecast Result` (item);

CREATE INDEX idx_aps_forecast_result_period
ON `tabAPS Forecast Result` (forecast_period);
```

## 3.6. Thiết kế giao diện

### 3.6.1. Form Scheduling Run

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  APS Scheduling Run                                                    [Save] [Submit]  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ╔═══════════════════════════════════════════════════════════════════════════════════╗  │
│  ║  BASIC INFORMATION                                                                ║  │
│  ╠═══════════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                                   ║  │
│  ║  Production Plan *     [Dropdown: Select Production Plan        ▼]                ║  │
│  ║                                                                                   ║  │
│  ║  Run Status           [Pending        ] (Read-only)                               ║  │
│  ║                                                                                   ║  │
│  ║  Scheduling Strategy * [Forward Scheduling ▼]                                     ║  │
│  ║                         ○ Forward Scheduling                                      ║  │
│  ║                         ○ Backward Scheduling                                     ║  │
│  ║                         ○ Priority Based                                          ║  │
│  ║                         ○ Earliest Due Date                                       ║  │
│  ║                                                                                   ║  │
│  ║  Scheduling Tier       [Tier 1 - OR-Tools ▼]                                      ║  │
│  ║                         ○ Tier 1 - OR-Tools (Mathematical)                        ║  │
│  ║                         ○ Tier 2 - RL Agent (Learning-based)                      ║  │
│  ║                         ○ Tier 3 - GNN (Graph Neural Network)                     ║  │
│  ║                                                                                   ║  │
│  ╚═══════════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                         │
│  ╔═══════════════════════════════════════════════════════════════════════════════════╗  │
│  ║  SOLVER CONFIGURATION                                                             ║  │
│  ╠═══════════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                                   ║  │
│  ║  Time Limit (seconds)   [    300    ]     Gap Between Ops (min)   [    10    ]    ║  │
│  ║                                                                                   ║  │
│  ║  Makespan Weight        [   1.0     ]     Tardiness Weight        [   10.0   ]    ║  │
│  ║                                                                                   ║  │
│  ╚═══════════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                         │
│  ╔═══════════════════════════════════════════════════════════════════════════════════╗  │
│  ║  CONSTRAINTS APPLIED                                                              ║  │
│  ╠═══════════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                                   ║  │
│  ║  [✓] Machine Eligibility    [✓] Precedence Order    [✓] No Overlap               ║  │
│  ║                                                                                   ║  │
│  ║  [✓] Working Hours          [✓] Due Dates           [ ] Setup Time               ║  │
│  ║                                                                                   ║  │
│  ╚═══════════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │                              [▶ Run Scheduling]                                   │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
│  ╔═══════════════════════════════════════════════════════════════════════════════════╗  │
│  ║  RESULTS SUMMARY                                                     (Read-only) ║  │
│  ╠═══════════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                                   ║  │
│  ║  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐                 ║  │
│  ║  │  Makespan        │  │  Late Jobs       │  │  Utilization     │                 ║  │
│  ║  │    480 min       │  │    3 / 25        │  │    78.5%         │                 ║  │
│  ║  │  ↓ 15% vs FIFO   │  │  ↓ 40% vs FIFO   │  │  ↑ 12% vs FIFO   │                 ║  │
│  ║  └──────────────────┘  └──────────────────┘  └──────────────────┘                 ║  │
│  ║                                                                                   ║  │
│  ║  Solver Status: [Optimal ✓]    Solve Time: 45.2 seconds                           ║  │
│  ║                                                                                   ║  │
│  ╚═══════════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │ [📊 View Gantt Chart]  [✓ Apply to Job Cards]  [🤖 AI Analysis]  [📥 Export]      │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.6.2. Gantt Chart View

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  Production Schedule - Gantt Chart                           [Zoom: Day ▼] [Export]    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  Timeline:  ◀ [Jan 15, 2025]  ────────────────────────────────  [Jan 20, 2025] ▶        │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │         │ 08:00 │ 10:00 │ 12:00 │ 14:00 │ 16:00 │ 18:00 │ 08:00 │ 10:00 │       │    │
│  │         │  Jan 15                                       │  Jan 16              │    │
│  ├─────────┼───────┴───────┴───────┴───────┴───────┴───────┼───────┴───────┴───────┤    │
│  │         │                                               │                       │    │
│  │  M1     │ ████ WO-001-Op1 ████│████ WO-003-Op1 ████████│██ WO-005-Op2 ████     │    │
│  │ (CNC)   │      (3 hrs)        │      (4 hrs)           │      (2.5 hrs)        │    │
│  │         │                                               │                       │    │
│  ├─────────┼───────────────────────────────────────────────┼───────────────────────┤    │
│  │         │                                               │                       │    │
│  │  M2     │         │████ WO-001-Op2 ████│                │████ WO-002-Op1 ████   │    │
│  │ (Lathe) │         │      (2 hrs)       │                │      (3 hrs)         │    │
│  │         │                                               │                       │    │
│  ├─────────┼───────────────────────────────────────────────┼───────────────────────┤    │
│  │         │                                               │                       │    │
│  │  M3     │                     │████ WO-002-Op2 ████████│                       │    │
│  │ (Mill)  │                     │      (3.5 hrs)  ⚠️ Late │                       │    │
│  │         │                                               │                       │    │
│  ├─────────┼───────────────────────────────────────────────┼───────────────────────┤    │
│  │         │                                               │                       │    │
│  │  M4     │ ████ WO-004-Op1 ████████████│                 │████ WO-004-Op2 ████   │    │
│  │ (Drill) │      (5 hrs)                │                 │      (2 hrs)         │    │
│  │         │                                               │                       │    │
│  └─────────┴───────────────────────────────────────────────┴───────────────────────┘    │
│                                                                                         │
│  Legend:  ████ On-time Job    ████ Late Job ⚠️    ░░░░ Machine Idle                     │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │  Selected: WO-003-Op1 on M1                                                     │    │
│  │  Start: Jan 15, 11:00  │  End: Jan 15, 15:00  │  Duration: 4 hrs                │    │
│  │  Work Order: WO-003    │  Item: Product-A     │  Status: Scheduled              │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.6.3. Forecast Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  Demand Forecast Dashboard                                              [New Forecast]  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │  Filter: Company [All ▼]  Model [All ▼]  Period [Last 30 days ▼]  [Apply]       │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │  Total Runs     │  │  Avg Accuracy   │  │  Items Forecast │  │  Reorder Alerts │     │
│  │      15         │  │     82.5%       │  │      245        │  │       12        │     │
│  │  ↑ 3 this week  │  │  MAPE: 17.5%    │  │  ↑ 50 new       │  │  ⚠️ Action req  │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                                         │
│  ╔═══════════════════════════════════════════════════════════════════════════════════╗  │
│  ║  RECENT FORECAST RUNS                                                             ║  │
│  ╠═══════════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                                   ║  │
│  ║  │ Run Name          │ Model    │ Items │ MAPE   │ Status    │ Date       │      ║  │
│  ║  ├───────────────────┼──────────┼───────┼────────┼───────────┼────────────┤      ║  │
│  ║  │ FCST-RUN-2025-001 │ Prophet  │  45   │ 15.2%  │ Complete ✓│ Jan 15     │      ║  │
│  ║  │ FCST-RUN-2025-002 │ ARIMA    │  38   │ 18.7%  │ Complete ✓│ Jan 14     │      ║  │
│  ║  │ FCST-RUN-2025-003 │ Linear   │  52   │ 22.1%  │ Complete ✓│ Jan 13     │      ║  │
│  ║  │ FCST-RUN-2025-004 │ Prophet  │  41   │ 14.8%  │ Complete ✓│ Jan 12     │      ║  │
│  ║                                                                                   ║  │
│  ╚═══════════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                         │
│  ╔═══════════════════════════════════════════════════════════════════════════════════╗  │
│  ║  TOP ITEMS BY FORECAST QTY                                                        ║  │
│  ╠═══════════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                                   ║  │
│  ║  │ Item       │ Forecast Qty │ Movement   │ Confidence │ Reorder │              ║  │
│  ║  ├────────────┼──────────────┼────────────┼────────────┼─────────┤              ║  │
│  ║  │ Product-A  │    1,250     │ Fast Moving│   92%      │   ⚠️    │              ║  │
│  ║  │ Product-B  │      850     │ Fast Moving│   88%      │   -     │              ║  │
│  ║  │ Product-C  │      420     │ Slow Moving│   75%      │   ⚠️    │              ║  │
│  ║  │ Product-D  │      380     │ Slow Moving│   71%      │   -     │              ║  │
│  ║                                                                                   ║  │
│  ╚═══════════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# CHƯƠNG 4: HIỆN THỰC HỆ THỐNG

## 4.1. Môi trường phát triển

### 4.1.1. Phần cứng

| Thành phần | Cấu hình |
|------------|----------|
| **CPU** | Intel Core i7 / AMD Ryzen 7 (8+ cores) |
| **RAM** | 16 GB DDR4 |
| **Storage** | 256 GB SSD |
| **Network** | Gigabit Ethernet / WiFi |

### 4.1.2. Phần mềm

| Thành phần | Phiên bản |
|------------|-----------|
| **OS** | Ubuntu 22.04 LTS / Windows 11 + WSL2 |
| **Python** | 3.10+ |
| **Node.js** | 18.x LTS |
| **MariaDB** | 10.6+ |
| **Redis** | 6.0+ |
| **Frappe** | 14.x / 15.x |
| **ERPNext** | 14.x / 15.x |

### 4.1.3. Thư viện Python

| Thư viện | Phiên bản | Mục đích |
|----------|-----------|----------|
| **ortools** | 9.7+ | Constraint Programming Solver |
| **pandas** | 2.0+ | Data manipulation |
| **numpy** | 1.24+ | Numerical computing |
| **statsmodels** | 0.14+ | ARIMA model |
| **prophet** | 1.1+ | Prophet forecasting |
| **scikit-learn** | 1.3+ | Linear Regression |
| **openai** | 1.0+ | ChatGPT integration |
| **torch** | 2.0+ | RL training |
| **stable-baselines3** | 2.0+ | PPO, SAC algorithms |

## 4.2. Cấu trúc dự án

### 4.2.1. Thư mục dự án

```
uit_aps/
├── uit_aps/
│   ├── __init__.py
│   ├── hooks.py                    # Frappe hooks configuration
│   ├── modules.txt                 # Module list
│   ├── patches.txt                 # Database patches
│   │
│   ├── aps/                        # Main APS module
│   │   ├── doctype/               # DocType definitions
│   │   │   ├── aps_scheduling_run/
│   │   │   │   ├── aps_scheduling_run.json
│   │   │   │   ├── aps_scheduling_run.py
│   │   │   │   └── aps_scheduling_run.js
│   │   │   ├── aps_scheduling_result/
│   │   │   ├── aps_forecast_history/
│   │   │   ├── aps_forecast_result/
│   │   │   ├── aps_production_plan/
│   │   │   ├── aps_mrp_run/
│   │   │   ├── aps_mrp_result/
│   │   │   ├── aps_purchase_suggestion/
│   │   │   ├── aps_work_shift/
│   │   │   ├── aps_rl_training_log/
│   │   │   └── aps_chatgpt_settings/
│   │   │
│   │   └── page/                  # Custom pages
│   │       └── aps_dashboard/
│   │
│   ├── scheduling/                # Scheduling module
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── scheduling_api.py  # Scheduling API endpoints
│   │   ├── solver/
│   │   │   ├── __init__.py
│   │   │   ├── ortools_solver.py  # OR-Tools implementation
│   │   │   ├── constraints.py     # Constraint definitions
│   │   │   └── baseline.py        # FIFO baseline
│   │   └── utils/
│   │       ├── gantt_generator.py
│   │       └── metrics.py
│   │
│   ├── forecast/                  # Forecasting module
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   └── forecast_api.py
│   │   ├── models/
│   │   │   ├── arima_model.py
│   │   │   ├── prophet_model.py
│   │   │   └── linear_model.py
│   │   └── utils/
│   │       └── data_processor.py
│   │
│   ├── mrp/                       # MRP module
│   │   ├── __init__.py
│   │   └── mrp_optimization.py
│   │
│   ├── ai_analysis/               # AI Analysis module
│   │   ├── __init__.py
│   │   └── llm_analyzer.py
│   │
│   ├── rl_training/               # RL Training module
│   │   ├── __init__.py
│   │   ├── environment.py
│   │   ├── ppo_agent.py
│   │   └── sac_agent.py
│   │
│   └── public/                    # Frontend assets
│       ├── js/
│       │   ├── gantt_chart.js
│       │   └── dashboard.js
│       └── css/
│           └── aps_styles.css
│
├── setup.py
├── requirements.txt
├── MANIFEST.in
└── README.md
```

### 4.2.2. Cấu hình Hooks

```python
# uit_aps/hooks.py

app_name = "uit_aps"
app_title = "UIT APS"
app_publisher = "UIT"
app_description = "Advanced Planning & Scheduling for ERPNext"
app_version = "1.0.0"

# Includes in <head>
app_include_css = "/assets/uit_aps/css/aps_styles.css"
app_include_js = "/assets/uit_aps/js/gantt_chart.js"

# DocType JS
doctype_js = {
    "Job Card": "public/js/job_card_custom.js"
}

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "uit_aps.forecast.tasks.run_daily_forecast"
    ],
    "weekly": [
        "uit_aps.mrp.tasks.run_weekly_mrp_check"
    ]
}

# Document Events
doc_events = {
    "Work Order": {
        "on_submit": "uit_aps.scheduling.utils.on_work_order_submit"
    }
}

# Fixtures
fixtures = [
    {"dt": "APS Work Shift"},
    {"dt": "APS Chatgpt Settings"}
]
```

## 4.3. Hiện thực Module Dự báo

### 4.3.1. Cấu trúc dữ liệu

**DocType: APS Forecast History**

```json
{
  "doctype": "DocType",
  "name": "APS Forecast History",
  "module": "APS",
  "autoname": "format:FCST-RUN-{YYYY}-{MM}-{DD}-{####}",
  "fields": [
    {"fieldname": "run_name", "fieldtype": "Data", "reqd": 1},
    {"fieldname": "company", "fieldtype": "Link", "options": "Company"},
    {"fieldname": "model_used", "fieldtype": "Select",
     "options": "\nARIMA\nLinear Regression\nProphet"},
    {"fieldname": "run_status", "fieldtype": "Select",
     "options": "Pending\nRunning\nComplete\nFailed"},
    {"fieldname": "forecast_horizon_days", "fieldtype": "Int"},
    {"fieldname": "overall_accuracy_mape_", "fieldtype": "Float"},
    {"fieldname": "ai_analysis", "fieldtype": "Long Text"}
  ]
}
```

### 4.3.2. ARIMA Implementation

```python
# uit_aps/forecast/models/arima_model.py

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import warnings

class ARIMAForecaster:
    """ARIMA model for demand forecasting"""

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.model = None
        self.order = None

    def find_optimal_order(self, max_p=5, max_d=2, max_q=5):
        """Auto-find optimal ARIMA(p,d,q) using AIC"""
        best_aic = float('inf')
        best_order = (1, 1, 1)

        # Test stationarity for d
        d = self._find_diff_order()

        for p in range(max_p + 1):
            for q in range(max_q + 1):
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        model = ARIMA(self.data['qty'], order=(p, d, q))
                        fitted = model.fit()

                        if fitted.aic < best_aic:
                            best_aic = fitted.aic
                            best_order = (p, d, q)
                except:
                    continue

        self.order = best_order
        return best_order

    def _find_diff_order(self, max_d=2):
        """Determine differencing order using ADF test"""
        series = self.data['qty'].copy()

        for d in range(max_d + 1):
            result = adfuller(series.dropna())
            if result[1] < 0.05:  # p-value < 0.05 = stationary
                return d
            series = series.diff()

        return max_d

    def fit(self):
        """Fit ARIMA model"""
        if self.order is None:
            self.find_optimal_order()

        self.model = ARIMA(self.data['qty'], order=self.order)
        self.fitted_model = self.model.fit()
        return self

    def forecast(self, horizon: int):
        """Generate forecast for specified horizon"""
        if self.fitted_model is None:
            raise ValueError("Model not fitted. Call fit() first.")

        forecast_result = self.fitted_model.get_forecast(steps=horizon)

        return {
            'forecast': forecast_result.predicted_mean.values,
            'lower_bound': forecast_result.conf_int().iloc[:, 0].values,
            'upper_bound': forecast_result.conf_int().iloc[:, 1].values,
            'aic': self.fitted_model.aic,
            'order': self.order
        }

    def calculate_mape(self, actual, predicted):
        """Calculate Mean Absolute Percentage Error"""
        actual = np.array(actual)
        predicted = np.array(predicted)

        # Avoid division by zero
        mask = actual != 0
        return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
```

### 4.3.3. Prophet Implementation

```python
# uit_aps/forecast/models/prophet_model.py

import pandas as pd
from prophet import Prophet
import logging

logging.getLogger('prophet').setLevel(logging.WARNING)

class ProphetForecaster:
    """Facebook Prophet model for demand forecasting"""

    def __init__(self, data: pd.DataFrame):
        self.data = self._prepare_data(data)
        self.model = None
        self.seasonality_info = {}

    def _prepare_data(self, data):
        """Prepare data for Prophet format"""
        df = data.copy()
        df = df.rename(columns={'date': 'ds', 'qty': 'y'})
        df['ds'] = pd.to_datetime(df['ds'])
        return df

    def fit(self, yearly_seasonality=True, weekly_seasonality=True,
            daily_seasonality=False):
        """Fit Prophet model with seasonality detection"""

        self.model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality,
            changepoint_prior_scale=0.05
        )

        self.model.fit(self.data)

        # Detect seasonality
        self._detect_seasonality()

        return self

    def _detect_seasonality(self):
        """Analyze detected seasonality patterns"""
        seasonality_types = []

        if hasattr(self.model, 'yearly_seasonality') and self.model.yearly_seasonality:
            seasonality_types.append('Yearly')
        if hasattr(self.model, 'weekly_seasonality') and self.model.weekly_seasonality:
            seasonality_types.append('Weekly')

        self.seasonality_info = {
            'detected': len(seasonality_types) > 0,
            'types': seasonality_types,
            'changepoints': len(self.model.changepoints) if hasattr(self.model, 'changepoints') else 0
        }

    def forecast(self, horizon: int):
        """Generate forecast"""
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")

        future = self.model.make_future_dataframe(periods=horizon)
        forecast = self.model.predict(future)

        # Get only future predictions
        future_forecast = forecast.tail(horizon)

        return {
            'forecast': future_forecast['yhat'].values,
            'lower_bound': future_forecast['yhat_lower'].values,
            'upper_bound': future_forecast['yhat_upper'].values,
            'seasonality': self.seasonality_info
        }
```

### 4.3.4. Forecast API

```python
# uit_aps/forecast/api/forecast_api.py

import frappe
from frappe import _
import pandas as pd
from datetime import datetime, timedelta
from uit_aps.forecast.models.arima_model import ARIMAForecaster
from uit_aps.forecast.models.prophet_model import ProphetForecaster
from uit_aps.forecast.models.linear_model import LinearForecaster

@frappe.whitelist()
def run_forecast(company, model_type, horizon_days, start_date=None, end_date=None,
                 item_group=None, warehouse=None):
    """
    Main API to run demand forecasting

    Args:
        company: Company name
        model_type: ARIMA / Prophet / Linear Regression
        horizon_days: Number of days to forecast
        start_date: Training data start (optional)
        end_date: Training data end (optional)
        item_group: Filter by item group (optional)
        warehouse: Filter by warehouse (optional)

    Returns:
        Forecast History name
    """

    # Create Forecast History record
    forecast_history = frappe.new_doc("APS Forecast History")
    forecast_history.run_name = f"Forecast {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    forecast_history.company = company
    forecast_history.model_used = model_type
    forecast_history.run_status = "Running"
    forecast_history.run_start_time = datetime.now()
    forecast_history.forecast_horizon_days = int(horizon_days)
    forecast_history.insert()
    frappe.db.commit()

    try:
        # Get historical sales data
        sales_data = get_sales_history(
            company, start_date, end_date, item_group, warehouse
        )

        if len(sales_data) < 30:
            raise ValueError("Insufficient data. Need at least 30 data points.")

        # Group by item
        items = sales_data['item_code'].unique()
        results = []

        for item in items:
            item_data = sales_data[sales_data['item_code'] == item]

            # Run forecast based on model type
            result = run_item_forecast(
                item, item_data, model_type, int(horizon_days)
            )

            if result:
                results.append(result)

        # Save results
        save_forecast_results(forecast_history.name, results)

        # Update history
        forecast_history.reload()
        forecast_history.run_status = "Complete"
        forecast_history.run_end_time = datetime.now()
        forecast_history.total_items_forecasted = len(items)
        forecast_history.total_results_generated = len(results)
        forecast_history.successful_forecasts = len([r for r in results if r['success']])
        forecast_history.failed_forecasts = len([r for r in results if not r['success']])

        # Calculate overall MAPE
        mapes = [r['mape'] for r in results if r.get('mape')]
        if mapes:
            forecast_history.overall_accuracy_mape_ = sum(mapes) / len(mapes)

        forecast_history.save()
        frappe.db.commit()

        return forecast_history.name

    except Exception as e:
        forecast_history.reload()
        forecast_history.run_status = "Failed"
        forecast_history.run_end_time = datetime.now()
        forecast_history.notes = str(e)
        forecast_history.save()
        frappe.db.commit()
        frappe.throw(str(e))


def run_item_forecast(item_code, data, model_type, horizon):
    """Run forecast for single item"""

    try:
        # Prepare time series data
        ts_data = data.groupby('date')['qty'].sum().reset_index()
        ts_data = ts_data.sort_values('date')

        # Select and run model
        if model_type == "ARIMA":
            forecaster = ARIMAForecaster(ts_data)
        elif model_type == "Prophet":
            forecaster = ProphetForecaster(ts_data)
        else:  # Linear Regression
            forecaster = LinearForecaster(ts_data)

        forecaster.fit()
        forecast_result = forecaster.forecast(horizon)

        # Calculate metrics
        avg_forecast = sum(forecast_result['forecast']) / len(forecast_result['forecast'])
        daily_avg = ts_data['qty'].mean()

        # Classify movement type
        if daily_avg > 10:
            movement_type = "Fast Moving"
        elif daily_avg > 1:
            movement_type = "Slow Moving"
        else:
            movement_type = "Non Moving"

        # Calculate trend
        trend = "Stable"
        if len(forecast_result['forecast']) > 1:
            slope = forecast_result['forecast'][-1] - forecast_result['forecast'][0]
            if slope > avg_forecast * 0.1:
                trend = "Upward"
            elif slope < -avg_forecast * 0.1:
                trend = "Downward"

        return {
            'success': True,
            'item': item_code,
            'forecast_qty': avg_forecast,
            'lower_bound': sum(forecast_result['lower_bound']) / len(forecast_result['lower_bound']),
            'upper_bound': sum(forecast_result['upper_bound']) / len(forecast_result['upper_bound']),
            'confidence_score': calculate_confidence(forecast_result),
            'movement_type': movement_type,
            'trend_type': trend,
            'daily_avg_consumption': daily_avg,
            'model_params': forecast_result.get('order') or forecast_result.get('seasonality'),
            'mape': forecast_result.get('mape', 0)
        }

    except Exception as e:
        return {
            'success': False,
            'item': item_code,
            'error': str(e)
        }
```

## 4.4. Hiện thực Module Kế hoạch sản xuất

### 4.4.1. Production Plan DocType

```python
# uit_aps/aps/doctype/aps_production_plan/aps_production_plan.py

import frappe
from frappe.model.document import Document
from frappe import _

class APSProductionPlan(Document):
    def validate(self):
        """Validate production plan"""
        # Validate periods
        if self.plan_from_period >= self.plan_to_period:
            frappe.throw(_("Plan From Period must be before Plan To Period"))

        # Validate forecast history for Forecast source
        if self.source_type == "Forecast" and not self.forecast_history:
            frappe.throw(_("Forecast History is required when Source Type is Forecast"))

        # Validate items
        for item in self.items:
            if item.planned_qty < 0:
                frappe.throw(_("Planned Quantity cannot be negative for item {0}").format(item.item))

    def on_submit(self):
        """On submit, set status to Planned"""
        self.status = "Planned"

    def on_cancel(self):
        """On cancel, set status to Cancelled"""
        self.status = "Cancelled"

    @frappe.whitelist()
    def populate_from_forecast(self):
        """Populate items from forecast history"""
        if not self.forecast_history:
            frappe.throw(_("Please select a Forecast History first"))

        # Get forecast results
        results = frappe.get_all(
            "APS Forecast Result",
            filters={"forecast_history": self.forecast_history},
            fields=["item", "forecast_qty", "safety_stock", "confidence_score", "name"]
        )

        self.items = []

        for result in results:
            # Calculate planned qty (forecast + safety stock)
            planned_qty = result.forecast_qty + (result.safety_stock or 0)

            # Get lead time from item
            item_doc = frappe.get_doc("Item", result.item)
            lead_time = item_doc.lead_time_days if hasattr(item_doc, 'lead_time_days') else 0

            self.append("items", {
                "item": result.item,
                "plan_period": self.plan_from_period,
                "planned_qty": planned_qty,
                "forecast_result": result.name,
                "safety_stock": result.safety_stock or 0,
                "forecast_quantiy": result.forecast_qty,
                "lead_time_days": lead_time
            })

        return len(results)
```

## 4.5. Hiện thực Module MRP

### 4.5.1. MRP Optimization

```python
# uit_aps/mrp/mrp_optimization.py

import frappe
from frappe import _
from datetime import datetime, timedelta

@frappe.whitelist()
def run_mrp_optimization(production_plan):
    """
    Run MRP calculation for a production plan

    Args:
        production_plan: Production Plan name

    Returns:
        MRP Run name
    """

    # Validate production plan status
    plan = frappe.get_doc("APS Production Plan", production_plan)
    if plan.status not in ["Planned", "Released"]:
        frappe.throw(_("Production Plan must be Planned or Released before running MRP"))

    # Create MRP Run record
    mrp_run = frappe.new_doc("APS MRP Run")
    mrp_run.production_plan = production_plan
    mrp_run.run_status = "Running"
    mrp_run.run_date = datetime.now()
    mrp_run.executed_by = frappe.session.user
    mrp_run.insert()
    frappe.db.commit()

    try:
        total_materials = 0

        # Process each item in production plan
        for plan_item in plan.items:
            # Get BOM for item
            bom = get_default_bom(plan_item.item)

            if not bom:
                continue

            # Explode BOM
            materials = explode_bom(bom, plan_item.planned_qty)

            # Calculate requirements
            for material in materials:
                # Get current stock
                available_qty = get_available_stock(material['item'], plan.company)

                # Calculate shortage
                shortage_qty = max(0, material['required_qty'] - available_qty)

                if shortage_qty > 0:
                    # Create MRP Result
                    mrp_result = frappe.new_doc("APS MRP Result")
                    mrp_result.mrp_run = mrp_run.name
                    mrp_result.material_item = material['item']
                    mrp_result.source_plan_item = plan_item.name
                    mrp_result.required_qty = material['required_qty']
                    mrp_result.available_qty = available_qty
                    mrp_result.shortage_qty = shortage_qty
                    mrp_result.required_date = calculate_required_date(
                        plan_item.plan_period,
                        material['lead_time']
                    )
                    mrp_result.insert()

                    # Create Purchase Suggestion
                    create_purchase_suggestion(mrp_run.name, material, shortage_qty)

                    total_materials += 1

        # Update MRP Run
        mrp_run.reload()
        mrp_run.run_status = "Completed"
        mrp_run.total_materials = total_materials
        mrp_run.save()
        frappe.db.commit()

        return mrp_run.name

    except Exception as e:
        mrp_run.reload()
        mrp_run.run_status = "Failed"
        mrp_run.notes = str(e)
        mrp_run.save()
        frappe.db.commit()
        frappe.throw(str(e))


def explode_bom(bom_name, qty):
    """Explode BOM to get all materials"""
    bom = frappe.get_doc("BOM", bom_name)
    materials = []

    for item in bom.items:
        required_qty = item.qty * qty

        # Check if item has sub-BOM
        sub_bom = get_default_bom(item.item_code)

        if sub_bom:
            # Recursive explosion
            sub_materials = explode_bom(sub_bom, required_qty)
            materials.extend(sub_materials)
        else:
            # Raw material
            materials.append({
                'item': item.item_code,
                'required_qty': required_qty,
                'uom': item.uom,
                'lead_time': get_lead_time(item.item_code)
            })

    return materials


def create_purchase_suggestion(mrp_run, material, shortage_qty):
    """Create purchase suggestion for material shortage"""

    # Get default supplier
    supplier = get_default_supplier(material['item'])
    unit_price = get_last_purchase_rate(material['item'])
    lead_time = material['lead_time']

    suggestion = frappe.new_doc("APS Purchase Suggestion")
    suggestion.mrp_run = mrp_run
    suggestion.material_item = material['item']
    suggestion.purchase_qty = shortage_qty
    suggestion.supplier = supplier
    suggestion.unit_price = unit_price
    suggestion.lead_time = lead_time
    suggestion.suggestion_status = "Draft"
    suggestion.insert()
```

## 4.6. Hiện thực Module Lập lịch

### 4.6.1. OR-Tools Solver Implementation

```python
# uit_aps/scheduling/solver/ortools_solver.py

import frappe
from frappe import _
from ortools.sat.python import cp_model
from datetime import datetime, timedelta
from collections import defaultdict

class ProductionScheduler:
    """Production scheduling using OR-Tools CP-SAT solver"""

    def __init__(self, config):
        self.config = config
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        # Data structures
        self.jobs = []
        self.machines = {}
        self.operations = []

        # Variables
        self.start_vars = {}
        self.end_vars = {}
        self.interval_vars = {}
        self.machine_to_intervals = defaultdict(list)

        # Results
        self.solution = None
        self.status = None

    def load_data(self, production_plan):
        """Load data from ERPNext"""
        plan = frappe.get_doc("APS Production Plan", production_plan)

        # Get Work Orders from Production Plan
        work_orders = frappe.get_all(
            "Work Order",
            filters={
                "production_plan": plan.name,
                "docstatus": 1,
                "status": ["in", ["Not Started", "In Process"]]
            },
            fields=["name", "production_item", "qty", "planned_start_date", "expected_delivery_date"]
        )

        for wo in work_orders:
            # Get Job Cards for each Work Order
            job_cards = frappe.get_all(
                "Job Card",
                filters={"work_order": wo.name, "docstatus": 0},
                fields=["name", "operation", "workstation", "for_quantity",
                       "time_in_mins", "sequence_id"],
                order_by="sequence_id"
            )

            self.jobs.append({
                'work_order': wo.name,
                'item': wo.production_item,
                'qty': wo.qty,
                'due_date': wo.expected_delivery_date,
                'job_cards': job_cards
            })

            # Collect machines
            for jc in job_cards:
                if jc.workstation not in self.machines:
                    ws = frappe.get_doc("Workstation", jc.workstation)
                    self.machines[jc.workstation] = {
                        'name': ws.name,
                        'working_hours': ws.working_hours_per_day or 8,
                        'capacity': ws.production_capacity or 1
                    }

    def build_model(self):
        """Build CP-SAT model with constraints"""

        # Calculate horizon (in minutes)
        horizon = self._calculate_horizon()

        # Create variables for each operation
        for job_idx, job in enumerate(self.jobs):
            for op_idx, jc in enumerate(job['job_cards']):
                duration = int(jc.time_in_mins or 60)

                # Create interval variable
                suffix = f"_{job_idx}_{op_idx}"
                start_var = self.model.NewIntVar(0, horizon, f"start{suffix}")
                end_var = self.model.NewIntVar(0, horizon, f"end{suffix}")
                interval_var = self.model.NewIntervalVar(
                    start_var, duration, end_var, f"interval{suffix}"
                )

                self.start_vars[(job_idx, op_idx)] = start_var
                self.end_vars[(job_idx, op_idx)] = end_var
                self.interval_vars[(job_idx, op_idx)] = interval_var

                # Add to machine intervals
                self.machine_to_intervals[jc.workstation].append(interval_var)

                # Store operation info
                self.operations.append({
                    'job_idx': job_idx,
                    'op_idx': op_idx,
                    'job_card': jc.name,
                    'workstation': jc.workstation,
                    'duration': duration,
                    'work_order': job['work_order']
                })

        # Add constraints
        self._add_precedence_constraints()
        self._add_no_overlap_constraints()

        if self.config.get('constraint_due_dates'):
            self._add_due_date_constraints()

        if self.config.get('constraint_working_hours'):
            self._add_working_hours_constraints()

        # Set objective
        self._set_objective()

    def _add_precedence_constraints(self):
        """Operations in a job must follow sequence"""
        for job_idx, job in enumerate(self.jobs):
            for op_idx in range(1, len(job['job_cards'])):
                prev_end = self.end_vars[(job_idx, op_idx - 1)]
                curr_start = self.start_vars[(job_idx, op_idx)]

                # Add gap between operations
                gap = self.config.get('min_gap_between_ops', 10)
                self.model.Add(curr_start >= prev_end + gap)

    def _add_no_overlap_constraints(self):
        """Machine cannot process two operations simultaneously"""
        for machine, intervals in self.machine_to_intervals.items():
            if len(intervals) > 1:
                self.model.AddNoOverlap(intervals)

    def _add_due_date_constraints(self):
        """Soft constraint for due dates with tardiness penalty"""
        self.tardiness_vars = {}

        for job_idx, job in enumerate(self.jobs):
            if job['due_date']:
                # Convert due date to minutes from start
                due_minutes = self._date_to_minutes(job['due_date'])

                # Get last operation end time
                last_op_idx = len(job['job_cards']) - 1
                end_var = self.end_vars[(job_idx, last_op_idx)]

                # Create tardiness variable
                tardiness = self.model.NewIntVar(0, due_minutes * 2, f"tardiness_{job_idx}")
                self.model.AddMaxEquality(tardiness, [0, end_var - due_minutes])
                self.tardiness_vars[job_idx] = tardiness

    def _set_objective(self):
        """Set optimization objective (minimize makespan + weighted tardiness)"""

        # Makespan: max end time of all operations
        all_ends = [self.end_vars[key] for key in self.end_vars]
        makespan = self.model.NewIntVar(0, self._calculate_horizon(), "makespan")
        self.model.AddMaxEquality(makespan, all_ends)
        self.makespan_var = makespan

        # Weighted objective
        makespan_weight = int(self.config.get('makespan_weight', 1) * 100)
        tardiness_weight = int(self.config.get('tardiness_weight', 10) * 100)

        if self.tardiness_vars:
            total_tardiness = self.model.NewIntVar(0, self._calculate_horizon() * len(self.jobs),
                                                   "total_tardiness")
            self.model.Add(total_tardiness == sum(self.tardiness_vars.values()))
            self.total_tardiness_var = total_tardiness

            self.model.Minimize(
                makespan_weight * makespan + tardiness_weight * total_tardiness
            )
        else:
            self.total_tardiness_var = None
            self.model.Minimize(makespan)

    def solve(self):
        """Solve the scheduling problem"""
        # Set solver parameters
        self.solver.parameters.max_time_in_seconds = self.config.get('time_limit_seconds', 300)
        self.solver.parameters.num_workers = 8  # Parallel search

        # Solve
        self.status = self.solver.Solve(self.model)

        if self.status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            self.solution = self._extract_solution()
            return True

        return False

    def _extract_solution(self):
        """Extract solution from solver"""
        results = []

        for op in self.operations:
            job_idx = op['job_idx']
            op_idx = op['op_idx']

            start_value = self.solver.Value(self.start_vars[(job_idx, op_idx)])
            end_value = self.solver.Value(self.end_vars[(job_idx, op_idx)])

            # Convert back to datetime
            start_time = self._minutes_to_datetime(start_value)
            end_time = self._minutes_to_datetime(end_value)

            # Check if late
            job = self.jobs[job_idx]
            is_late = False
            if job['due_date'] and end_time.date() > job['due_date']:
                is_late = True

            results.append({
                'job_card': op['job_card'],
                'workstation': op['workstation'],
                'work_order': op['work_order'],
                'planned_start_time': start_time,
                'planned_end_time': end_time,
                'duration': op['duration'],
                'is_late': is_late
            })

        return {
            'operations': results,
            'makespan': self.solver.Value(self.makespan_var),
            'total_tardiness': self.solver.Value(self.total_tardiness_var) if self.total_tardiness_var else 0,
            'status': 'Optimal' if self.status == cp_model.OPTIMAL else 'Feasible',
            'solve_time': self.solver.WallTime()
        }

    def get_status_string(self):
        """Get solver status as string"""
        status_map = {
            cp_model.OPTIMAL: "Optimal",
            cp_model.FEASIBLE: "Feasible",
            cp_model.INFEASIBLE: "Infeasible",
            cp_model.MODEL_INVALID: "Error",
            cp_model.UNKNOWN: "Timeout"
        }
        return status_map.get(self.status, "Unknown")
```

### 4.6.2. Scheduling API

```python
# uit_aps/scheduling/api/scheduling_api.py

import frappe
from frappe import _
from datetime import datetime
from uit_aps.scheduling.solver.ortools_solver import ProductionScheduler
from uit_aps.scheduling.solver.baseline import FIFOBaseline

@frappe.whitelist()
def run_ortools_scheduling(scheduling_run_name):
    """
    Run OR-Tools scheduling optimization

    Args:
        scheduling_run_name: APS Scheduling Run document name

    Returns:
        Updated scheduling run with results
    """

    run = frappe.get_doc("APS Scheduling Run", scheduling_run_name)

    # Update status
    run.run_status = "Running"
    run.run_date = datetime.now()
    run.save()
    frappe.db.commit()

    try:
        # Build solver config
        config = {
            'time_limit_seconds': run.time_limit_seconds or 300,
            'min_gap_between_ops': run.min_gap_between_ops or 10,
            'makespan_weight': run.makespan_weight or 1.0,
            'tardiness_weight': run.tardiness_weight or 10.0,
            'constraint_machine_eligibility': run.constraint_machine_eligibility,
            'constraint_precedence': run.constraint_precedence,
            'constraint_no_overlap': run.constraint_no_overlap,
            'constraint_working_hours': run.constraint_working_hours,
            'constraint_due_dates': run.constraint_due_dates,
            'constraint_setup_time': run.constraint_setup_time
        }

        # Initialize scheduler
        scheduler = ProductionScheduler(config)

        # Load data from ERPNext
        scheduler.load_data(run.production_plan)

        if not scheduler.jobs:
            frappe.throw(_("No Work Orders/Job Cards found for this Production Plan"))

        # Build constraint model
        scheduler.build_model()

        # Solve
        success = scheduler.solve()

        if not success:
            run.run_status = "Failed"
            run.solver_status = scheduler.get_status_string()
            run.save()
            frappe.throw(_("Solver failed to find a feasible solution"))

        solution = scheduler.solution

        # Run FIFO baseline for comparison
        baseline = FIFOBaseline(scheduler.jobs, scheduler.machines)
        baseline_result = baseline.run()

        # Save results
        save_scheduling_results(run.name, solution['operations'])

        # Update run document
        run.run_status = "Pending Approval"
        run.solver_status = solution['status']
        run.solve_time_seconds = solution['solve_time']
        run.makespan_minutes = solution['makespan']
        run.total_tardiness_minutes = solution['total_tardiness']
        run.total_job_cards = len(solution['operations'])
        run.total_late_jobs = len([op for op in solution['operations'] if op['is_late']])
        run.jobs_on_time = run.total_job_cards - run.total_late_jobs

        # Calculate machine utilization
        run.machine_utilization = calculate_utilization(
            solution['operations'],
            solution['makespan'],
            scheduler.machines
        )

        # Baseline comparison
        run.baseline_makespan_minutes = baseline_result['makespan']
        run.baseline_late_jobs = baseline_result['late_jobs']
        run.baseline_total_tardiness = baseline_result['total_tardiness']

        # Calculate improvements
        if baseline_result['makespan'] > 0:
            run.improvement_makespan_percent = (
                (baseline_result['makespan'] - solution['makespan']) /
                baseline_result['makespan'] * 100
            )

        if baseline_result['late_jobs'] > 0:
            run.improvement_late_jobs_percent = (
                (baseline_result['late_jobs'] - run.total_late_jobs) /
                baseline_result['late_jobs'] * 100
            )

        if baseline_result['total_tardiness'] > 0:
            run.improvement_tardiness_percent = (
                (baseline_result['total_tardiness'] - solution['total_tardiness']) /
                baseline_result['total_tardiness'] * 100
            )

        run.comparison_summary = generate_comparison_summary(run)
        run.save()
        frappe.db.commit()

        return run.name

    except Exception as e:
        run.reload()
        run.run_status = "Failed"
        run.solver_status = "Error"
        run.notes = str(e)
        run.save()
        frappe.db.commit()
        raise e


def save_scheduling_results(scheduling_run, operations):
    """Save scheduling results to database"""

    for op in operations:
        result = frappe.new_doc("APS Scheduling Result")
        result.scheduling_run = scheduling_run
        result.job_card = op['job_card']
        result.workstation = op['workstation']
        result.planned_start_time = op['planned_start_time']
        result.planned_end_time = op['planned_end_time']
        result.is_late = op['is_late']
        result.is_applied = 0

        # Get operation from job card
        jc = frappe.get_doc("Job Card", op['job_card'])
        result.operation = jc.operation

        result.insert()

    frappe.db.commit()


@frappe.whitelist()
def apply_schedule_to_job_cards(scheduling_run_name):
    """Apply scheduling results to Job Cards"""

    run = frappe.get_doc("APS Scheduling Run", scheduling_run_name)

    if run.run_status != "Pending Approval":
        frappe.throw(_("Schedule must be in 'Pending Approval' status to apply"))

    # Get all results
    results = frappe.get_all(
        "APS Scheduling Result",
        filters={"scheduling_run": scheduling_run_name, "is_applied": 0},
        fields=["name", "job_card", "planned_start_time", "planned_end_time"]
    )

    applied_count = 0

    for result in results:
        try:
            # Update Job Card
            frappe.db.set_value("Job Card", result.job_card, {
                "scheduled_time_start": result.planned_start_time,
                "scheduled_time_end": result.planned_end_time
            })

            # Mark result as applied
            frappe.db.set_value("APS Scheduling Result", result.name, {
                "is_applied": 1,
                "applied_at": datetime.now()
            })

            applied_count += 1

        except Exception as e:
            frappe.log_error(f"Failed to apply schedule to {result.job_card}: {str(e)}")

    # Update run
    run.reload()
    run.applied_operations = applied_count
    run.applied_at = datetime.now()
    run.applied_by = frappe.session.user
    run.run_status = "Applied"
    run.save()

    frappe.db.commit()

    return {
        "applied": applied_count,
        "total": len(results)
    }


@frappe.whitelist()
def get_gantt_data(scheduling_run_name):
    """Get Gantt chart data for visualization"""

    results = frappe.get_all(
        "APS Scheduling Result",
        filters={"scheduling_run": scheduling_run_name},
        fields=["name", "job_card", "workstation", "operation",
               "planned_start_time", "planned_end_time", "is_late", "is_applied"]
    )

    gantt_data = []

    for result in results:
        # Get additional info
        jc = frappe.get_doc("Job Card", result.job_card)

        gantt_data.append({
            'id': result.name,
            'name': f"{jc.work_order} - {result.operation}",
            'start': result.planned_start_time.isoformat(),
            'end': result.planned_end_time.isoformat(),
            'resource': result.workstation,
            'color': '#ef4444' if result.is_late else '#22c55e',
            'is_late': result.is_late,
            'is_applied': result.is_applied,
            'job_card': result.job_card,
            'work_order': jc.work_order
        })

    return gantt_data
```

## 4.7. Hiện thực Module AI Analysis

### 4.7.1. LLM Analyzer

```python
# uit_aps/ai_analysis/llm_analyzer.py

import frappe
from frappe import _
import openai
from datetime import datetime

class SchedulingAnalyzer:
    """AI-powered scheduling analysis using OpenAI API"""

    def __init__(self):
        settings = frappe.get_single("APS Chatgpt Settings")
        if not settings.api_key:
            frappe.throw(_("OpenAI API Key not configured. Please set it in APS Chatgpt Settings."))

        openai.api_key = settings.api_key

    def analyze_scheduling_run(self, scheduling_run_name, language='vi', custom_prompt=None):
        """
        Analyze scheduling run results with AI

        Args:
            scheduling_run_name: APS Scheduling Run name
            language: 'vi' for Vietnamese, 'en' for English
            custom_prompt: Custom analysis prompt (optional)

        Returns:
            Analysis text
        """

        run = frappe.get_doc("APS Scheduling Run", scheduling_run_name)

        # Build context
        context = self._build_context(run)

        # Build prompt
        prompt = self._build_prompt(context, language, custom_prompt)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt(language)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            analysis = response.choices[0].message.content

            # Save to run
            run.llm_analysis_content = analysis
            run.llm_analysis_date = datetime.now()
            run.llm_analysis_model = "gpt-4"
            run.llm_analysis_language = language
            run.save()

            return analysis

        except Exception as e:
            frappe.log_error(f"AI Analysis failed: {str(e)}")
            raise e

    def _build_context(self, run):
        """Build context data for analysis"""

        # Get scheduling results
        results = frappe.get_all(
            "APS Scheduling Result",
            filters={"scheduling_run": run.name},
            fields=["job_card", "workstation", "is_late", "delay_reason"]
        )

        # Group by workstation
        by_workstation = {}
        for r in results:
            ws = r.workstation
            if ws not in by_workstation:
                by_workstation[ws] = {'total': 0, 'late': 0}
            by_workstation[ws]['total'] += 1
            if r.is_late:
                by_workstation[ws]['late'] += 1

        return {
            'makespan': run.makespan_minutes,
            'total_jobs': run.total_job_cards,
            'late_jobs': run.total_late_jobs,
            'on_time_jobs': run.jobs_on_time,
            'utilization': run.machine_utilization,
            'solver_status': run.solver_status,
            'solve_time': run.solve_time_seconds,
            'baseline_makespan': run.baseline_makespan_minutes,
            'improvement_makespan': run.improvement_makespan_percent,
            'improvement_late_jobs': run.improvement_late_jobs_percent,
            'by_workstation': by_workstation,
            'strategy': run.scheduling_strategy,
            'constraints': {
                'machine_eligibility': run.constraint_machine_eligibility,
                'precedence': run.constraint_precedence,
                'no_overlap': run.constraint_no_overlap,
                'working_hours': run.constraint_working_hours,
                'due_dates': run.constraint_due_dates,
                'setup_time': run.constraint_setup_time
            }
        }

    def _get_system_prompt(self, language):
        """Get system prompt based on language"""

        if language == 'vi':
            return """Bạn là chuyên gia phân tích lập lịch sản xuất.
            Nhiệm vụ của bạn là phân tích kết quả lập lịch và đưa ra:
            1. Đánh giá tổng quan về chất lượng lịch trình
            2. Phân tích các điểm mạnh và điểm yếu
            3. Xác định các rủi ro tiềm ẩn
            4. Đề xuất cải thiện cụ thể

            Trả lời bằng tiếng Việt, sử dụng Markdown formatting."""
        else:
            return """You are a production scheduling analysis expert.
            Your task is to analyze scheduling results and provide:
            1. Overall assessment of schedule quality
            2. Analysis of strengths and weaknesses
            3. Identification of potential risks
            4. Specific improvement recommendations

            Respond in English using Markdown formatting."""

    def _build_prompt(self, context, language, custom_prompt):
        """Build analysis prompt"""

        if custom_prompt:
            base = custom_prompt
        else:
            if language == 'vi':
                base = "Phân tích kết quả lập lịch sản xuất sau và đưa ra đánh giá chi tiết:"
            else:
                base = "Analyze the following production scheduling results and provide detailed assessment:"

        data_section = f"""

**Scheduling Results:**
- Total Makespan: {context['makespan']} minutes ({context['makespan'] // 60} hours {context['makespan'] % 60} min)
- Total Jobs: {context['total_jobs']}
- Late Jobs: {context['late_jobs']} ({context['late_jobs'] / context['total_jobs'] * 100:.1f}%)
- On-time Jobs: {context['on_time_jobs']} ({context['on_time_jobs'] / context['total_jobs'] * 100:.1f}%)
- Machine Utilization: {context['utilization']:.1f}%
- Solver Status: {context['solver_status']}
- Solve Time: {context['solve_time']:.2f} seconds

**Comparison with FIFO Baseline:**
- FIFO Makespan: {context['baseline_makespan']} minutes
- Makespan Improvement: {context['improvement_makespan']:.1f}%
- Late Jobs Reduction: {context['improvement_late_jobs']:.1f}%

**Strategy:** {context['strategy']}

**Constraints Applied:**
- Machine Eligibility: {'Yes' if context['constraints']['machine_eligibility'] else 'No'}
- Precedence: {'Yes' if context['constraints']['precedence'] else 'No'}
- No Overlap: {'Yes' if context['constraints']['no_overlap'] else 'No'}
- Working Hours: {'Yes' if context['constraints']['working_hours'] else 'No'}
- Due Dates: {'Yes' if context['constraints']['due_dates'] else 'No'}
- Setup Time: {'Yes' if context['constraints']['setup_time'] else 'No'}

**By Workstation:**
"""

        for ws, data in context['by_workstation'].items():
            data_section += f"- {ws}: {data['total']} jobs, {data['late']} late\n"

        return base + data_section


@frappe.whitelist()
def run_ai_analysis(scheduling_run_name, language='vi', custom_prompt=None):
    """API endpoint for AI analysis"""

    analyzer = SchedulingAnalyzer()
    return analyzer.analyze_scheduling_run(scheduling_run_name, language, custom_prompt)
```

## 4.8. Tích hợp và API

### 4.8.1. API Endpoints Summary

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/api/method/uit_aps.forecast.api.forecast_api.run_forecast` | POST | Chạy dự báo nhu cầu |
| `/api/method/uit_aps.mrp.mrp_optimization.run_mrp_optimization` | POST | Chạy MRP |
| `/api/method/uit_aps.scheduling.api.scheduling_api.run_ortools_scheduling` | POST | Chạy lập lịch OR-Tools |
| `/api/method/uit_aps.scheduling.api.scheduling_api.apply_schedule_to_job_cards` | POST | Áp dụng lịch vào Job Cards |
| `/api/method/uit_aps.scheduling.api.scheduling_api.get_gantt_data` | GET | Lấy data Gantt chart |
| `/api/method/uit_aps.ai_analysis.llm_analyzer.run_ai_analysis` | POST | Phân tích AI |

### 4.8.2. Client-side Integration

```javascript
// uit_aps/public/js/scheduling_run.js

frappe.ui.form.on('APS Scheduling Run', {
    refresh: function(frm) {
        // Add custom buttons
        if (frm.doc.run_status === 'Pending') {
            frm.add_custom_button(__('Run Scheduling'), function() {
                run_scheduling(frm);
            }, __('Actions'));
        }

        if (frm.doc.run_status === 'Pending Approval') {
            frm.add_custom_button(__('View Gantt Chart'), function() {
                show_gantt_chart(frm);
            }, __('View'));

            frm.add_custom_button(__('Apply to Job Cards'), function() {
                apply_schedule(frm);
            }, __('Actions'));

            frm.add_custom_button(__('AI Analysis'), function() {
                run_ai_analysis(frm);
            }, __('Actions'));
        }
    }
});

function run_scheduling(frm) {
    frappe.call({
        method: 'uit_aps.scheduling.api.scheduling_api.run_ortools_scheduling',
        args: {
            scheduling_run_name: frm.doc.name
        },
        freeze: true,
        freeze_message: __('Running OR-Tools solver...'),
        callback: function(r) {
            if (r.message) {
                frm.reload_doc();
                frappe.show_alert({
                    message: __('Scheduling completed successfully'),
                    indicator: 'green'
                });
            }
        }
    });
}

function show_gantt_chart(frm) {
    frappe.call({
        method: 'uit_aps.scheduling.api.scheduling_api.get_gantt_data',
        args: {
            scheduling_run_name: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                // Show Gantt chart dialog
                let dialog = new frappe.ui.Dialog({
                    title: __('Production Schedule - Gantt Chart'),
                    size: 'extra-large'
                });

                dialog.show();

                // Render Gantt chart
                render_gantt(dialog.$body, r.message);
            }
        }
    });
}

function apply_schedule(frm) {
    frappe.confirm(
        __('Apply this schedule to Job Cards? This will update scheduled times.'),
        function() {
            frappe.call({
                method: 'uit_aps.scheduling.api.scheduling_api.apply_schedule_to_job_cards',
                args: {
                    scheduling_run_name: frm.doc.name
                },
                freeze: true,
                freeze_message: __('Applying schedule...'),
                callback: function(r) {
                    if (r.message) {
                        frm.reload_doc();
                        frappe.show_alert({
                            message: __('Applied {0} of {1} operations', [r.message.applied, r.message.total]),
                            indicator: 'green'
                        });
                    }
                }
            });
        }
    );
}

function run_ai_analysis(frm) {
    let dialog = new frappe.ui.Dialog({
        title: __('AI Analysis'),
        fields: [
            {
                fieldname: 'language',
                label: __('Language'),
                fieldtype: 'Select',
                options: 'vi\nen',
                default: 'vi'
            },
            {
                fieldname: 'custom_prompt',
                label: __('Custom Prompt (Optional)'),
                fieldtype: 'Small Text'
            }
        ],
        primary_action_label: __('Analyze'),
        primary_action: function(values) {
            dialog.hide();

            frappe.call({
                method: 'uit_aps.ai_analysis.llm_analyzer.run_ai_analysis',
                args: {
                    scheduling_run_name: frm.doc.name,
                    language: values.language,
                    custom_prompt: values.custom_prompt
                },
                freeze: true,
                freeze_message: __('Running AI analysis...'),
                callback: function(r) {
                    if (r.message) {
                        frm.reload_doc();
                        frappe.show_alert({
                            message: __('AI analysis completed'),
                            indicator: 'green'
                        });
                    }
                }
            });
        }
    });

    dialog.show();
}
```

---

# CHƯƠNG 5: KIỂM THỬ VÀ ĐÁNH GIÁ

## 5.1. Kế hoạch kiểm thử

### 5.1.1. Phạm vi kiểm thử

| Loại kiểm thử | Phạm vi | Công cụ |
|---------------|---------|---------|
| **Unit Test** | Các hàm Python độc lập | pytest |
| **Integration Test** | API endpoints, database | Frappe test framework |
| **Functional Test** | Use cases end-to-end | Manual testing |
| **Performance Test** | Solver time, scalability | Custom benchmarks |

### 5.1.2. Test Cases tổng quan

| ID | Module | Test Case | Độ ưu tiên |
|----|--------|-----------|------------|
| TC-FC-001 | Forecast | Chạy dự báo ARIMA thành công | Cao |
| TC-FC-002 | Forecast | Chạy dự báo Prophet thành công | Cao |
| TC-FC-003 | Forecast | Xử lý data không đủ | Trung bình |
| TC-PP-001 | Production Plan | Tạo kế hoạch từ forecast | Cao |
| TC-MRP-001 | MRP | Tính toán nhu cầu vật tư | Cao |
| TC-MRP-002 | MRP | Tạo đề xuất mua hàng | Cao |
| TC-SC-001 | Scheduling | Lập lịch 10 jobs thành công | Cao |
| TC-SC-002 | Scheduling | Lập lịch 100 jobs trong 5 phút | Cao |
| TC-SC-003 | Scheduling | So sánh với FIFO baseline | Cao |
| TC-SC-004 | Scheduling | Áp dụng vào Job Cards | Cao |
| TC-AI-001 | AI Analysis | Phân tích với ChatGPT | Trung bình |

## 5.2. Kiểm thử chức năng

### 5.2.1. Test Cases Module Dự báo

**TC-FC-001: Chạy dự báo ARIMA thành công**

| Thành phần | Chi tiết |
|------------|----------|
| **Mục đích** | Kiểm tra dự báo ARIMA hoạt động đúng |
| **Precondition** | Có 50+ Sales Orders trong 90 ngày |
| **Input** | Company: Test Company, Model: ARIMA, Horizon: 30 days |
| **Steps** | 1. Mở form APS Forecast History<br>2. Nhập tham số<br>3. Click Run Forecast |
| **Expected** | - Status: Complete<br>- Có Forecast Results<br>- MAPE < 30% |
| **Actual Result** | Pass ✓ |

**TC-FC-002: Chạy dự báo Prophet thành công**

| Thành phần | Chi tiết |
|------------|----------|
| **Mục đích** | Kiểm tra dự báo Prophet phát hiện seasonality |
| **Precondition** | Có 365+ Sales Orders trong 1 năm |
| **Input** | Company: Test Company, Model: Prophet, Horizon: 90 days |
| **Steps** | 1. Mở form APS Forecast History<br>2. Nhập tham số<br>3. Click Run Forecast |
| **Expected** | - Status: Complete<br>- Seasonality detected<br>- Confidence > 70% |
| **Actual Result** | Pass ✓ |

### 5.2.2. Test Cases Module Lập lịch

**TC-SC-001: Lập lịch 10 jobs thành công**

| Thành phần | Chi tiết |
|------------|----------|
| **Mục đích** | Kiểm tra lập lịch cơ bản |
| **Precondition** | Production Plan với 10 Work Orders |
| **Input** | Strategy: Forward, Time Limit: 60s |
| **Steps** | 1. Tạo Scheduling Run<br>2. Click Run Scheduling |
| **Expected** | - Status: Optimal<br>- All jobs scheduled<br>- Solve time < 10s |
| **Actual Result** | Pass ✓ |

**TC-SC-002: Lập lịch 100 jobs trong 5 phút**

| Thành phần | Chi tiết |
|------------|----------|
| **Mục đích** | Kiểm tra scalability |
| **Precondition** | Production Plan với 100 Work Orders |
| **Input** | Strategy: Forward, Time Limit: 300s |
| **Steps** | 1. Tạo Scheduling Run<br>2. Click Run Scheduling |
| **Expected** | - Status: Optimal/Feasible<br>- Solve time < 300s<br>- Utilization > 60% |
| **Actual Result** | Pass ✓ (Solve time: 145s) |

### 5.2.3. Kết quả kiểm thử chức năng

| Module | Total TCs | Pass | Fail | Pass Rate |
|--------|-----------|------|------|-----------|
| Forecasting | 8 | 8 | 0 | 100% |
| Production Planning | 5 | 5 | 0 | 100% |
| MRP | 6 | 6 | 0 | 100% |
| Scheduling | 12 | 11 | 1 | 91.7% |
| AI Analysis | 3 | 3 | 0 | 100% |
| **Tổng** | **34** | **33** | **1** | **97.1%** |

## 5.3. Kiểm thử hiệu năng

### 5.3.1. Benchmark Setup

| Thành phần | Cấu hình |
|------------|----------|
| **Server** | Intel Xeon 8 cores, 32GB RAM |
| **Database** | MariaDB 10.6, SSD storage |
| **Python** | 3.10, ortools 9.7 |
| **Test Data** | Synthetic manufacturing data |

### 5.3.2. Kết quả Benchmark Lập lịch

| Jobs | Operations | Machines | Solve Time | Status | Makespan Improvement |
|------|------------|----------|------------|--------|---------------------|
| 10 | 30 | 5 | 2.3s | Optimal | +18% vs FIFO |
| 25 | 75 | 8 | 12.5s | Optimal | +22% vs FIFO |
| 50 | 150 | 10 | 45.2s | Optimal | +25% vs FIFO |
| 100 | 300 | 15 | 145.8s | Optimal | +21% vs FIFO |
| 200 | 600 | 20 | 298.5s | Feasible | +18% vs FIFO |
| 500 | 1500 | 25 | 542.3s | Feasible | +15% vs FIFO |

### 5.3.3. Kết quả Benchmark Dự báo

| Items | Data Points | ARIMA Time | Prophet Time | LR Time |
|-------|-------------|------------|--------------|---------|
| 10 | 90 | 3.2s | 5.8s | 0.8s |
| 50 | 90 | 15.4s | 28.3s | 2.1s |
| 100 | 90 | 32.1s | 58.6s | 4.3s |
| 100 | 365 | 45.2s | 72.4s | 5.1s |

### 5.3.4. Memory Usage

| Operation | Peak Memory | Average Memory |
|-----------|-------------|----------------|
| Forecast 100 items | 512 MB | 380 MB |
| Schedule 100 jobs | 1.2 GB | 850 MB |
| Schedule 500 jobs | 3.5 GB | 2.8 GB |
| MRP 50 items | 256 MB | 180 MB |

## 5.4. Đánh giá kết quả

### 5.4.1. Đánh giá theo mục tiêu

| Mục tiêu | Chỉ số yêu cầu | Kết quả thực tế | Đánh giá |
|----------|----------------|-----------------|----------|
| Độ chính xác dự báo | MAPE ≤ 30% | MAPE = 17.5% | ✓ Đạt |
| Cải thiện makespan | ≥ 10% vs FIFO | 18-25% | ✓ Vượt |
| Giảm jobs trễ | ≥ 20% vs FIFO | 35-45% | ✓ Vượt |
| Hiệu suất máy | ≥ 70% | 72-85% | ✓ Đạt |
| Thời gian lập lịch 100 jobs | ≤ 300s | 145.8s | ✓ Đạt |

### 5.4.2. So sánh với Baseline FIFO

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COMPARISON: UIT APS vs FIFO                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Makespan (100 jobs)                                                    │
│  ├── FIFO:    ████████████████████████████████████████ 1250 min        │
│  └── UIT APS: ██████████████████████████████████ 1000 min (-20%)       │
│                                                                         │
│  Late Jobs                                                              │
│  ├── FIFO:    ████████████████████ 12 jobs                             │
│  └── UIT APS: ████████ 5 jobs (-58%)                                   │
│                                                                         │
│  Total Tardiness                                                        │
│  ├── FIFO:    ████████████████████████████ 480 min                     │
│  └── UIT APS: ██████████████ 240 min (-50%)                            │
│                                                                         │
│  Machine Utilization                                                    │
│  ├── FIFO:    ██████████████████████████████ 62%                       │
│  └── UIT APS: ████████████████████████████████████████ 78% (+26%)      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.4.3. Phân tích SWOT

| | Positive | Negative |
|--|----------|----------|
| **Internal** | **Strengths**<br>• Tích hợp chặt với ERPNext<br>• Tối ưu hóa bằng OR-Tools<br>• Hỗ trợ nhiều mô hình dự báo<br>• AI analysis | **Weaknesses**<br>• Giới hạn 500 jobs<br>• Cần nhiều RAM<br>• Phụ thuộc OpenAI API |
| **External** | **Opportunities**<br>• Mở rộng sang Tier 2/3<br>• Real-time scheduling<br>• IoT integration | **Threats**<br>• Cạnh tranh từ SAP, Oracle<br>• API pricing changes<br>• Technology obsolescence |

## 5.5. So sánh với các hệ thống khác

### 5.5.1. So sánh tính năng

| Tính năng | UIT APS | ERPNext MFG | SAP PP | Oracle APS |
|-----------|---------|-------------|--------|------------|
| **Giá** | Free | Free | $$$$$ | $$$$$ |
| **Lập lịch tự động** | ✓ | ✗ | ✓ | ✓ |
| **Tối ưu hóa OR** | ✓ | ✗ | ✓ | ✓ |
| **Dự báo ML** | ✓ | ✗ | ✓ | ✓ |
| **AI Analysis** | ✓ | ✗ | ✓ | ✓ |
| **Open Source** | ✓ | ✓ | ✗ | ✗ |
| **Customizable** | ✓ | ✓ | Limited | Limited |
| **Cloud Native** | ✓ | ✓ | ✓ | ✓ |

### 5.5.2. Vị thế sản phẩm

```
                        High Cost
                           │
                           │         ┌───────────┐
                           │         │  SAP PP   │
                           │         └───────────┘
                           │
                           │    ┌─────────────┐
                           │    │ Oracle APS  │
                           │    └─────────────┘
                           │
    Low ───────────────────┼─────────────────────── High
    Features               │                    Features
                           │
              ┌──────────────────┐
              │     UIT APS      │ ← Target position
              └──────────────────┘
                           │
           ┌──────────────────────┐
           │   ERPNext MFG       │
           └──────────────────────┘
                           │
                        Low Cost
```

---

# CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 6.1. Kết quả đạt được

### 6.1.1. Về mặt kỹ thuật

**Module đã hoàn thành:**

| Module | Tính năng | Trạng thái |
|--------|-----------|------------|
| **Forecasting** | ARIMA, Prophet, Linear Regression, Movement classification | ✓ Hoàn thành |
| **Production Planning** | Create from forecast, Items management, Workflow | ✓ Hoàn thành |
| **MRP** | Material calculation, BOM explosion, Purchase suggestion | ✓ Hoàn thành |
| **Scheduling** | OR-Tools solver, 6 constraints, FIFO comparison | ✓ Hoàn thành |
| **AI Analysis** | OpenAI integration, Multi-language | ✓ Hoàn thành |
| **RL Training** | PPO, SAC algorithms | 70% Hoàn thành |

**Metrics đạt được:**

- **Độ chính xác dự báo**: MAPE trung bình 17.5% (yêu cầu ≤30%)
- **Cải thiện makespan**: 18-25% so với FIFO (yêu cầu ≥10%)
- **Giảm jobs trễ**: 35-45% so với FIFO (yêu cầu ≥20%)
- **Hiệu suất máy**: 72-85% (yêu cầu ≥70%)
- **Thời gian lập lịch 100 jobs**: 145.8 giây (yêu cầu ≤300s)

### 6.1.2. Về mặt khoa học

**Đóng góp:**

1. **Áp dụng Constraint Programming** vào lập lịch sản xuất trong môi trường ERPNext
2. **Tích hợp ML** (ARIMA, Prophet) vào dự báo nhu cầu sản xuất
3. **Kết hợp LLM** (ChatGPT) phân tích kết quả lập lịch
4. **Nghiên cứu RL** (PPO, SAC) cho lập lịch thích ứng

### 6.1.3. Về mặt thực tiễn

**Giá trị mang lại:**

- **Giảm thời gian lập lịch**: Từ vài giờ thủ công xuống vài phút tự động
- **Tăng năng suất**: Hiệu suất máy tăng 10-20%
- **Giảm trễ hạn**: Số đơn hàng trễ giảm 35-45%
- **Hỗ trợ quyết định**: Cung cấp dự báo và phân tích AI

## 6.2. Hạn chế

### 6.2.1. Hạn chế kỹ thuật

| Hạn chế | Mô tả | Ảnh hưởng |
|---------|-------|-----------|
| **Scalability** | Giới hạn ~500 jobs | Chưa phù hợp nhà máy lớn |
| **Memory** | Cần nhiều RAM (>3GB cho 500 jobs) | Yêu cầu server mạnh |
| **Real-time** | Chưa hỗ trợ cập nhật real-time | Cần chạy lại khi có thay đổi |
| **RL Training** | Chưa hoàn thiện fully | Chưa đưa vào production |

### 6.2.2. Hạn chế về phạm vi

- Chưa tích hợp **IoT/sensors**
- Chưa có **mobile app**
- Chưa hỗ trợ **multi-site scheduling**
- Phụ thuộc vào **OpenAI API** cho AI analysis

## 6.3. Hướng phát triển

### 6.3.1. Ngắn hạn (3-6 tháng)

| Ưu tiên | Phát triển | Mô tả |
|---------|------------|-------|
| P1 | **Hoàn thiện RL Training** | Hoàn thành Tier 2 với PPO/SAC |
| P1 | **Performance optimization** | Tối ưu để support 1000+ jobs |
| P2 | **Real-time updates** | WebSocket cho cập nhật lịch trình |
| P2 | **Better visualization** | Interactive Gantt with drag-drop |

### 6.3.2. Trung hạn (6-12 tháng)

| Ưu tiên | Phát triển | Mô tả |
|---------|------------|-------|
| P1 | **GNN Integration (Tier 3)** | Graph Neural Network cho scheduling |
| P2 | **Multi-site scheduling** | Lập lịch đa nhà máy |
| P2 | **What-if analysis** | Mô phỏng các kịch bản |
| P3 | **Mobile app** | React Native cho iOS/Android |

### 6.3.3. Dài hạn (>12 tháng)

| Ưu tiên | Phát triển | Mô tả |
|---------|------------|-------|
| P1 | **IoT integration** | Kết nối máy móc real-time |
| P2 | **Digital Twin** | Mô phỏng 3D nhà máy |
| P2 | **Autonomous scheduling** | Self-learning, self-adapting |
| P3 | **Industry 4.0 compliance** | OPC-UA, MQTT integration |

### 6.3.4. Roadmap tổng thể

```
2025 Q1          Q2              Q3              Q4              2026
  │               │               │               │               │
  ▼               ▼               ▼               ▼               ▼
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│ RL Tier2│   │ Perf    │   │ GNN     │   │ Multi-  │   │ IoT     │
│ Complete│   │ Optimize│   │ Tier 3  │   │ Site    │   │ Integrate│
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
     │             │             │             │             │
     ▼             ▼             ▼             ▼             ▼
  v1.1           v1.2          v2.0          v2.5          v3.0
```

## 6.4. Kết luận

Đồ án đã **thành công** trong việc xây dựng module **UIT APS** tích hợp vào ERPNext, cung cấp khả năng:

1. **Dự báo nhu cầu** với độ chính xác cao (MAPE 17.5%)
2. **Lập lịch tối ưu** cải thiện 18-25% so với FIFO
3. **Phân tích AI** hỗ trợ ra quyết định

Module này là **bước đầu tiên** trong việc nâng cao năng lực sản xuất cho doanh nghiệp sử dụng ERPNext, với tiềm năng phát triển thành hệ thống **Industry 4.0** hoàn chỉnh.

---

# TÀI LIỆU THAM KHẢO

## Sách và bài báo

[1] Michael L. Pinedo, "Scheduling: Theory, Algorithms, and Systems", 5th Edition, Springer, 2016.

[2] Kenneth R. Baker, Dan Trietsch, "Principles of Sequencing and Scheduling", 2nd Edition, Wiley, 2019.

[3] Rob J. Hyndman, George Athanasopoulos, "Forecasting: Principles and Practice", 3rd Edition, OTexts, 2021.

[4] Richard S. Sutton, Andrew G. Barto, "Reinforcement Learning: An Introduction", 2nd Edition, MIT Press, 2018.

## Tài liệu kỹ thuật

[5] Google OR-Tools Documentation, https://developers.google.com/optimization

[6] Frappe Framework Documentation, https://frappeframework.com/docs

[7] ERPNext Manufacturing Module, https://docs.erpnext.com/docs/user/manual/en/manufacturing

[8] Facebook Prophet Documentation, https://facebook.github.io/prophet/

[9] OpenAI API Documentation, https://platform.openai.com/docs

## Bài báo khoa học

[10] Zhang, J., et al., "Deep Reinforcement Learning for Job Shop Scheduling", IEEE Transactions on Industrial Informatics, 2020.

[11] Wang, L., et al., "A Survey of AI for Production Scheduling", Journal of Manufacturing Systems, 2021.

[12] Chen, X., et al., "Constraint Programming for Manufacturing Scheduling: A Review", Computers & Operations Research, 2022.

---

# PHỤ LỤC

## Phụ lục A: Hướng dẫn cài đặt

Chi tiết xem file `Environment_Setup_Guide.md`

## Phụ lục B: Cấu trúc bảng dữ liệu

Chi tiết xem file `MoTaCauTrucBang.md`

## Phụ lục C: Đặc tả yêu cầu

Chi tiết xem file `SRS_UIT_APS.md`

## Phụ lục D: API Documentation

### D.1 Forecast API

```python
# Run forecast
POST /api/method/uit_aps.forecast.api.forecast_api.run_forecast

Request:
{
    "company": "My Company",
    "model_type": "ARIMA",
    "horizon_days": 30,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "item_group": "Finished Goods"
}

Response:
{
    "message": "FCST-RUN-2025-01-15-0001"
}
```

### D.2 Scheduling API

```python
# Run scheduling
POST /api/method/uit_aps.scheduling.api.scheduling_api.run_ortools_scheduling

Request:
{
    "scheduling_run_name": "APS-SCH-RUN-00001"
}

Response:
{
    "message": "APS-SCH-RUN-00001"
}
```

## Phụ lục E: Test Reports

### E.1 Unit Test Coverage

```
Module                    Coverage
-------------------------------
forecast/models           95%
scheduling/solver         92%
mrp                       88%
ai_analysis               85%
-------------------------------
Total                     90%
```

### E.2 Performance Test Results

Xem mục 5.3 - Kiểm thử hiệu năng

---

**--- HẾT ---**
