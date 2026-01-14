# BỔ SUNG ĐỒ ÁN TỐT NGHIỆP - UIT APS

## Module Lập lịch Sản xuất Nâng cao (Advanced Planning & Scheduling)

---

# MỤC LỤC BỔ SUNG

1. [Khảo sát các công trình nghiên cứu liên quan](#1-khảo-sát-các-công-trình-nghiên-cứu-liên-quan)
2. [Tính cấp thiết và tầm quan trọng của đề tài](#2-tính-cấp-thiết-và-tầm-quan-trọng-của-đề-tài)
3. [Lý do chọn đề tài](#3-lý-do-chọn-đề-tài)
4. [Mô tả chi tiết các ràng buộc tối ưu hóa](#4-mô-tả-chi-tiết-các-ràng-buộc-tối-ưu-hóa)
5. [Tiêu chí đánh giá tối ưu](#5-tiêu-chí-đánh-giá-tối-ưu)
6. [Chức năng xuất Gantt Chart với Deadline và Thuật toán tối ưu](#6-chức-năng-xuất-gantt-chart-với-deadline-và-thuật-toán-tối-ưu)
7. [Danh sách tài liệu tham khảo chi tiết](#7-danh-sách-tài-liệu-tham-khảo-chi-tiết)

---

# 1. KHẢO SÁT CÁC CÔNG TRÌNH NGHIÊN CỨU LIÊN QUAN

## 1.1. Tổng quan về lĩnh vực nghiên cứu

Lập lịch sản xuất (Production Scheduling) là một trong những bài toán cổ điển và quan trọng nhất trong lĩnh vực **Operations Research** và **Manufacturing Management**. Bài toán này đã được nghiên cứu từ những năm 1950 và tiếp tục là chủ đề nghiên cứu nóng cho đến ngày nay.

### 1.1.1. Phân loại các hướng nghiên cứu

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CÁC HƯỚNG NGHIÊN CỨU CHÍNH                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────────────┐   │
│  │  EXACT METHODS  │   │   HEURISTICS    │   │   METAHEURISTICS        │   │
│  ├─────────────────┤   ├─────────────────┤   ├─────────────────────────┤   │
│  │ • Branch & Bound│   │ • Dispatching   │   │ • Genetic Algorithm     │   │
│  │ • Dynamic Prog  │   │   Rules (FIFO,  │   │ • Simulated Annealing   │   │
│  │ • Integer Prog  │   │   SPT, EDD)     │   │ • Tabu Search           │   │
│  │ • Constraint    │   │ • Priority-based│   │ • Particle Swarm        │   │
│  │   Programming   │   │ • Greedy        │   │ • Ant Colony            │   │
│  └─────────────────┘   └─────────────────┘   └─────────────────────────┘   │
│           │                    │                        │                  │
│           └────────────────────┼────────────────────────┘                  │
│                                │                                           │
│                                ▼                                           │
│                    ┌─────────────────────────┐                             │
│                    │    MACHINE LEARNING     │                             │
│                    ├─────────────────────────┤                             │
│                    │ • Reinforcement Learning│                             │
│                    │ • Deep Learning         │                             │
│                    │ • Graph Neural Networks │                             │
│                    │ • Hybrid Methods        │                             │
│                    └─────────────────────────┘                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 1.2. Các công trình nghiên cứu tiêu biểu

### 1.2.1. Nghiên cứu về Constraint Programming cho Scheduling

| STT | Tác giả | Năm | Công trình | Nội dung chính | Hạn chế |
|-----|---------|-----|------------|----------------|---------|
| 1 | Baptiste et al. | 2001 | "Constraint-Based Scheduling" | Giới thiệu framework CP cho scheduling, định nghĩa các constraint cơ bản | Chưa tối ưu cho bài toán lớn |
| 2 | Laborie et al. | 2018 | "IBM ILOG CP Optimizer for Scheduling" | Phát triển công cụ thương mại với các kỹ thuật tiên tiến | Closed-source, chi phí cao |
| 3 | Ku & Beck | 2016 | "Mixed Integer Programming vs Constraint Programming" | So sánh hiệu năng MIP và CP cho JSSP | Chỉ test trên benchmark nhỏ |
| 4 | **Da Col & Teppan** | **2022** | **"OR-Tools for Job Shop Scheduling"** | **Sử dụng Google OR-Tools CP-SAT cho JSSP với kết quả SOTA** | **Cần tune hyperparameters** |

**Phân tích công trình [4] - Da Col & Teppan (2022):**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  "Industrial-Size Job Shop Scheduling with Constraint Programming"          │
│  Tác giả: Giacomo Da Col, Erich Teppan                                     │
│  Hội nghị: CPAIOR 2022                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHƯƠNG PHÁP:                                                               │
│  • Sử dụng Google OR-Tools CP-SAT Solver                                   │
│  • Áp dụng Lazy Clause Generation                                          │
│  • Kết hợp symmetry breaking và search strategies                          │
│                                                                             │
│  KẾT QUẢ:                                                                   │
│  • Giải được instances với 2000+ operations                                │
│  • Đạt optimality gap < 5% trong 1 giờ                                     │
│  • Vượt trội so với các CP solvers khác                                    │
│                                                                             │
│  ÁP DỤNG VÀO UIT APS:                                                       │
│  ✓ Sử dụng OR-Tools CP-SAT làm solver chính                                │
│  ✓ Áp dụng các constraint modeling techniques                              │
│  ✓ Implement search strategies từ paper                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2.2. Nghiên cứu về Machine Learning cho Demand Forecasting

| STT | Tác giả | Năm | Công trình | Nội dung chính | Hạn chế |
|-----|---------|-----|------------|----------------|---------|
| 1 | Taylor & Letham | 2018 | "Forecasting at Scale (Prophet)" | Phát triển Facebook Prophet cho time series | Cần nhiều data (>365 days) |
| 2 | Hyndman & Athanasopoulos | 2021 | "Forecasting: Principles and Practice" | Tổng hợp các phương pháp dự báo từ cổ điển đến hiện đại | Textbook, không có implementation |
| 3 | **Makridakis et al.** | **2022** | **"M5 Competition"** | **So sánh 50+ phương pháp dự báo trên dữ liệu retail thực** | **Data specific cho retail** |
| 4 | Salinas et al. | 2020 | "DeepAR: Probabilistic Forecasting" | Deep learning cho probabilistic forecasting | Cần GPU, complex setup |

**Phân tích công trình [3] - M5 Competition (2022):**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  "M5 Accuracy Competition: Results, Findings and Conclusions"               │
│  Tác giả: Makridakis, Spiliotis, Assimakopoulos                            │
│  Journal: International Journal of Forecasting, 2022                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DATASET:                                                                   │
│  • 42,840 time series từ Walmart                                           │
│  • 1,941 ngày dữ liệu bán hàng                                             │
│  • Hierarchical structure (store, category, item)                          │
│                                                                             │
│  KẾT QUẢ SO SÁNH (MAPE):                                                    │
│  ┌────────────────────────┬────────────┐                                    │
│  │ Phương pháp            │   MAPE     │                                    │
│  ├────────────────────────┼────────────┤                                    │
│  │ LightGBM (Winner)      │   12.5%    │                                    │
│  │ Neural Networks        │   14.2%    │                                    │
│  │ Prophet                │   16.8%    │                                    │
│  │ ARIMA                  │   18.3%    │                                    │
│  │ Simple Exponential     │   21.5%    │                                    │
│  │ Naive (Baseline)       │   28.7%    │                                    │
│  └────────────────────────┴────────────┘                                    │
│                                                                             │
│  ÁP DỤNG VÀO UIT APS:                                                       │
│  ✓ Implement ARIMA, Prophet, Linear Regression                             │
│  ✓ Auto-select best model based on data characteristics                    │
│  ✓ Target MAPE < 25% cho manufacturing context                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2.3. Nghiên cứu về Reinforcement Learning cho Scheduling

| STT | Tác giả | Năm | Công trình | Nội dung chính | Hạn chế |
|-----|---------|-----|------------|----------------|---------|
| 1 | Waschneck et al. | 2018 | "Deep RL for Semiconductor Production" | Áp dụng DQN cho wafer fab scheduling | Domain-specific |
| 2 | **Zhang et al.** | **2020** | **"Learning to Dispatch for JSSP"** | **GNN + RL cho job dispatching đạt SOTA** | **Training time cao** |
| 3 | Park et al. | 2021 | "Learning to Schedule using Graph Neural Networks" | Message Passing Neural Network cho scheduling | Cần large dataset |
| 4 | Tassel et al. | 2021 | "Reinforcement Learning Environment for JSSP" | Chuẩn hóa RL environment cho JSSP | Chỉ là framework |

**Phân tích công trình [2] - Zhang et al. (2020):**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  "Learning to Dispatch for Job Shop Scheduling via Deep RL"                 │
│  Tác giả: Zhang, Song, Cao, Zhang, Kitani                                  │
│  Hội nghị: NeurIPS 2020                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  KIẾN TRÚC:                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   Job Features ──┐                                                  │   │
│  │                  ├──▶ Graph Neural Network ──▶ Policy Network       │   │
│  │   Machine State ─┘         (GNN)              (Actor-Critic)        │   │
│  │                              │                       │              │   │
│  │                              ▼                       ▼              │   │
│  │                    Node Embeddings           Action (Job Selection) │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  KẾT QUẢ:                                                                   │
│  • Outperform Priority Dispatching Rules by 10-20%                         │
│  • Generalize to unseen instances                                          │
│  • Real-time inference (< 10ms per decision)                               │
│                                                                             │
│  ÁP DỤNG VÀO UIT APS (Tier 2, 3):                                           │
│  ✓ Design RL environment cho JSSP                                          │
│  ✓ Implement PPO/SAC agents                                                │
│  ✓ Future: GNN integration cho Tier 3                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2.4. Nghiên cứu về APS trong ERP Systems

| STT | Tác giả | Năm | Công trình | Nội dung chính | Hạn chế |
|-----|---------|-----|------------|----------------|---------|
| 1 | Stadtler & Kilger | 2015 | "Supply Chain Management and APS" | Textbook về APS trong SCM | Thiên về lý thuyết |
| 2 | **Dolgui & Proth** | **2010** | **"Supply Chain Engineering"** | **Framework tích hợp Forecasting-Planning-Scheduling** | **Không có implementation** |
| 3 | Moon et al. | 2018 | "APS for Smart Factory" | APS trong bối cảnh Industry 4.0 | Khái niệm chung |
| 4 | Lin et al. | 2021 | "Cloud-based APS System" | Kiến trúc APS trên cloud | Thiếu chi tiết kỹ thuật |

**Phân tích công trình [2] - Dolgui & Proth (2010):**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  "Supply Chain Engineering: Useful Methods and Techniques"                  │
│  Tác giả: Alexandre Dolgui, Jean-Marie Proth                               │
│  Publisher: Springer, 2010                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  APS FRAMEWORK ĐỀ XUẤT:                                                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  STRATEGIC PLANNING (Long-term)                                     │   │
│  │  • Capacity planning                                                │   │
│  │  • Network design                                                   │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                      │                                     │
│                                      ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  TACTICAL PLANNING (Medium-term)                                    │   │
│  │  • Demand Forecasting            ◀──── UIT APS: Forecasting Module  │   │
│  │  • Production Planning           ◀──── UIT APS: Production Plan     │   │
│  │  • Material Planning (MRP)       ◀──── UIT APS: MRP Module          │   │
│  └───────────────────────────────────┬─────────────────────────────────┘   │
│                                      │                                     │
│                                      ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  OPERATIONAL PLANNING (Short-term)                                  │   │
│  │  • Production Scheduling         ◀──── UIT APS: Scheduling Module   │   │
│  │  • Shop Floor Control                                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ÁP DỤNG VÀO UIT APS:                                                       │
│  ✓ Implement 3-layer architecture                                          │
│  ✓ Integration với ERPNext Manufacturing                                   │
│  ✓ Focus on Tactical + Operational layers                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 1.3. Bảng so sánh tổng hợp các công trình

| Công trình | Phương pháp | Ưu điểm | Nhược điểm | Áp dụng vào UIT APS |
|------------|-------------|---------|------------|---------------------|
| Da Col & Teppan (2022) | OR-Tools CP-SAT | SOTA performance, industrial-scale | Cần tune parameters | ✓ Solver chính |
| M5 Competition (2022) | ML Forecasting | Comprehensive comparison | Domain-specific | ✓ Model selection |
| Zhang et al. (2020) | GNN + RL | Real-time, generalizable | Training expensive | ✓ Future Tier 3 |
| Dolgui & Proth (2010) | APS Framework | Holistic view | No implementation | ✓ Architecture design |
| Taylor & Letham (2018) | Prophet | Handles seasonality | Needs >365 data points | ✓ Forecasting option |

## 1.4. Khoảng trống nghiên cứu (Research Gap)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RESEARCH GAP ANALYSIS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. THIẾU TÍCH HỢP TOÀN DIỆN                                               │
│     ├── Các nghiên cứu hiện tại: Focus riêng lẻ vào Forecasting HOẶC       │
│     │   Scheduling HOẶC MRP                                                 │
│     └── UIT APS: Tích hợp cả 3 module trong một hệ thống                   │
│                                                                             │
│  2. THIẾU OPEN-SOURCE SOLUTION                                             │
│     ├── Các giải pháp thương mại: SAP APO, Oracle APS (đắt, closed)        │
│     ├── ERPNext: Chỉ có basic scheduling                                   │
│     └── UIT APS: Open-source, tích hợp sẵn vào ERPNext                     │
│                                                                             │
│  3. THIẾU AI-ASSISTED ANALYSIS                                             │
│     ├── Các hệ thống hiện tại: Chỉ output kết quả scheduling               │
│     └── UIT APS: Tích hợp LLM để phân tích, giải thích kết quả            │
│                                                                             │
│  4. THIẾU MULTI-TIER APPROACH                                              │
│     ├── Phần lớn: Chỉ 1 phương pháp (OR hoặc Heuristic hoặc ML)           │
│     └── UIT APS: 3 tiers (OR-Tools → RL → GNN) để balance                 │
│         speed/quality                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 1.5. Đóng góp của UIT APS so với các công trình hiện có

| Khía cạnh | Công trình hiện có | Đóng góp của UIT APS |
|-----------|-------------------|----------------------|
| **Integration** | Standalone tools | Tích hợp hoàn toàn vào ERPNext |
| **Cost** | Commercial ($10K-$1M/year) | Open-source, miễn phí |
| **AI Analysis** | Không có | Tích hợp ChatGPT |
| **Multi-method** | Single approach | 3-tier architecture |
| **Vietnamese** | Không hỗ trợ | Hỗ trợ đầy đủ tiếng Việt |
| **SME-friendly** | Enterprise-focused | Thiết kế cho SME |

---

# 2. TÍNH CẤP THIẾT VÀ TẦM QUAN TRỌNG CỦA ĐỀ TÀI

## 2.1. Bối cảnh ngành sản xuất Việt Nam

### 2.1.1. Thực trạng ngành sản xuất

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              THỰC TRẠNG NGÀNH SẢN XUẤT VIỆT NAM 2024                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TỔNG QUAN:                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • GDP từ công nghiệp chế biến chế tạo: 24.8% (2023)                 │   │
│  │ • Số doanh nghiệp sản xuất: ~98,000 (trong đó 97% là SME)          │   │
│  │ • Lao động ngành sản xuất: ~10.5 triệu người                       │   │
│  │ • Tốc độ tăng trưởng: 6.5%/năm                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  VẤN ĐỀ ĐANG ĐỐI MẶT:                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   85%        72%        68%        45%                              │   │
│  │   ████       ████       ████       ████                             │   │
│  │   ████       ████       ████       ████                             │   │
│  │   ████       ████       ████       ████                             │   │
│  │   ████       ████       ████       ████                             │   │
│  │   ────       ────       ────       ────                             │   │
│  │   Lập lịch   Dự báo     Tồn kho    Áp dụng                         │   │
│  │   thủ công   kém chính  cao        công nghệ                       │   │
│  │              xác                   4.0                              │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Nguồn: Tổng cục Thống kê, VCCI, 2023                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1.2. Áp lực cạnh tranh

| Áp lực | Mô tả | Tác động |
|--------|-------|----------|
| **Toàn cầu hóa** | Cạnh tranh với Trung Quốc, Ấn Độ, Bangladesh | Cần giảm chi phí 15-20% |
| **Khách hàng** | Yêu cầu giao hàng nhanh, đúng hạn | Lead time giảm từ 4 tuần → 2 tuần |
| **Công nghệ** | Industry 4.0, Smart Manufacturing | Cần số hóa để tồn tại |
| **Nhân sự** | Chi phí lao động tăng 8%/năm | Cần tự động hóa |

## 2.2. Tính cấp thiết của đề tài

### 2.2.1. Vấn đề lập lịch thủ công

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VẤN ĐỀ LẬP LỊCH THỦ CÔNG                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  HIỆN TRẠNG TẠI CÁC DOANH NGHIỆP SME:                                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Sales Order ──▶ [Nhân viên] ──▶ Excel/Giấy ──▶ Phân xưởng        │   │
│  │       │              │              │              │                │   │
│  │       │              │              │              │                │   │
│  │       ▼              ▼              ▼              ▼                │   │
│  │   Ngẫu nhiên    4-8 giờ/ngày   Dễ sai sót    Thiếu tối ưu          │   │
│  │   không có      để lập lịch    conflicts     hiệu suất             │   │
│  │   ưu tiên                                    máy 50-60%            │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  HẬU QUẢ:                                                                   │
│  • 25-35% đơn hàng giao trễ                                                │
│  • Hiệu suất máy chỉ đạt 55-65%                                            │
│  • Tồn kho cao (30-40% vốn lưu động)                                       │
│  • Chi phí overtime tăng 20%                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2.2. Nhu cầu số hóa

**Khảo sát 500 doanh nghiệp sản xuất SME Việt Nam (VCCI, 2023):**

| Câu hỏi | Có | Không |
|---------|-----|-------|
| Có sử dụng phần mềm ERP? | 35% | 65% |
| Có công cụ lập lịch tự động? | 8% | 92% |
| Muốn áp dụng công nghệ lập lịch? | 78% | 22% |
| Sẵn sàng đầu tư <50 triệu VND? | 85% | 15% |
| Cần giải pháp tiếng Việt? | 92% | 8% |

### 2.2.3. Khoảng trống thị trường

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PHÂN KHÚC THỊ TRƯỜNG APS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Chi phí                                                                    │
│    ▲                                                                        │
│    │                      ┌─────────────┐                                   │
│    │  $1M+              │  SAP APO    │                                   │
│    │                      │  Oracle APS │                                   │
│    │                      └─────────────┘                                   │
│    │                                                                        │
│    │  $100K    ┌─────────────────────┐                                     │
│    │           │  Preactor, Asprova  │                                     │
│    │           └─────────────────────┘                                     │
│    │                                                                        │
│    │  $10K     ┌──────────────────────────────┐                            │
│    │           │  Opcenter, PlanetTogether    │                            │
│    │           └──────────────────────────────┘                            │
│    │                                                                        │
│    │           ╔══════════════════════════════╗                            │
│    │  FREE     ║        UIT APS               ║  ◀── TARGET SEGMENT       │
│    │           ║   (Open-source, Vietnamese)  ║      97% SMEs             │
│    │           ╚══════════════════════════════╝                            │
│    │                                                                        │
│    └────────────────────────────────────────────────────────────▶          │
│                                                                  Features   │
│          Basic            Standard           Advanced                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2.3. Tầm quan trọng của đề tài

### 2.3.1. Tầm quan trọng kinh tế

| Khía cạnh | Tác động định lượng | Nguồn |
|-----------|---------------------|-------|
| **Giảm chi phí sản xuất** | 10-15% | McKinsey, 2022 |
| **Tăng hiệu suất máy** | 15-25% | Gartner, 2023 |
| **Giảm tồn kho** | 20-30% | APICS, 2022 |
| **Giảm giao hàng trễ** | 30-50% | Aberdeen, 2023 |
| **ROI trong 12 tháng** | 200-400% | Forrester, 2022 |

### 2.3.2. Tầm quan trọng công nghệ

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              UIT APS TRONG BỐI CẢNH INDUSTRY 4.0                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                        ┌─────────────────────┐                              │
│                        │   INDUSTRY 4.0      │                              │
│                        │   FRAMEWORK         │                              │
│                        └──────────┬──────────┘                              │
│                                   │                                         │
│         ┌─────────────────────────┼─────────────────────────┐               │
│         │                         │                         │               │
│         ▼                         ▼                         ▼               │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐          │
│  │  IoT/OT     │          │  AI/ML      │          │  Cloud      │          │
│  │  Layer      │          │  Layer      │          │  Layer      │          │
│  └──────┬──────┘          └──────┬──────┘          └──────┬──────┘          │
│         │                        │                        │                 │
│         │    ┌───────────────────┼───────────────────┐    │                 │
│         │    │                   │                   │    │                 │
│         │    │   ╔═══════════════╧═══════════════╗   │    │                 │
│         └────┼──▶║         UIT APS               ║◀──┼────┘                 │
│              │   ║  • OR-Tools (Optimization)    ║   │                      │
│              │   ║  • ML (Forecasting)           ║   │                      │
│              │   ║  • LLM (Analysis)             ║   │                      │
│              │   ║  • Cloud-ready                ║   │                      │
│              │   ╚═══════════════════════════════╝   │                      │
│              │                   │                   │                      │
│              │                   ▼                   │                      │
│              │          ┌─────────────┐              │                      │
│              │          │   ERPNext   │              │                      │
│              │          │   (ERP)     │              │                      │
│              │          └─────────────┘              │                      │
│              │                                       │                      │
│              └───────────────────────────────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3.3. Tầm quan trọng xã hội

- **Nâng cao năng lực cạnh tranh** của doanh nghiệp Việt Nam
- **Đào tạo nhân lực** công nghệ cao cho ngành sản xuất
- **Chuyển giao công nghệ** từ nghiên cứu sang ứng dụng
- **Giảm phụ thuộc** vào phần mềm nước ngoài đắt đỏ

---

# 3. LÝ DO CHỌN ĐỀ TÀI

## 3.1. Động lực cá nhân

### 3.1.1. Quan sát thực tế

Trong quá trình thực tập và làm việc với các doanh nghiệp sản xuất, tôi nhận thấy:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    QUAN SÁT THỰC TẾ TẠI DOANH NGHIỆP                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CÔNG TY A (Sản xuất cơ khí, 150 nhân viên):                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Lập lịch bằng Excel, mất 1 ngày/tuần                              │   │
│  │ • 30% đơn hàng giao trễ                                             │   │
│  │ • Hiệu suất máy CNC chỉ 58%                                         │   │
│  │ • Đã thử SAP nhưng chi phí quá cao ($200K/năm)                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  CÔNG TY B (Sản xuất nhựa, 80 nhân viên):                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Dùng ERPNext cho kế toán, kho                                     │   │
│  │ • Module Manufacturing quá cơ bản                                   │   │
│  │ • Muốn có scheduling nhưng không có budget                          │   │
│  │ • Cần giải pháp tiếng Việt                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  CÔNG TY C (Sản xuất điện tử, 300 nhân viên):                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Đang dùng Asprova (Nhật) - $50K/năm                               │   │
│  │ • Không customize được theo nhu cầu                                 │   │
│  │ • Muốn tích hợp AI để dự báo                                        │   │
│  │ • Cần solution có thể mở rộng                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1.2. Sở thích nghiên cứu

| Lĩnh vực | Mức độ quan tâm | Lý do |
|----------|-----------------|-------|
| **Operations Research** | Cao | Bài toán tối ưu hóa có tính ứng dụng cao |
| **Machine Learning** | Cao | Xu hướng AI trong manufacturing |
| **ERP Systems** | Trung bình | Nền tảng để triển khai giải pháp |
| **Open Source** | Cao | Đóng góp cho cộng đồng |

## 3.2. Lý do khách quan

### 3.2.1. Nhu cầu thị trường

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHÂN TÍCH NHU CẦU THỊ TRƯỜNG                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  THỊ TRƯỜNG APS TOÀN CẦU:                                                   │
│  • Quy mô 2023: $2.1 tỷ USD                                                │
│  • Dự báo 2028: $4.8 tỷ USD                                                │
│  • CAGR: 18.2%/năm                                                         │
│  Nguồn: MarketsandMarkets, 2023                                            │
│                                                                             │
│  THỊ TRƯỜNG VIỆT NAM:                                                       │
│  • ~98,000 doanh nghiệp sản xuất SME                                       │
│  • 92% chưa có giải pháp scheduling                                        │
│  • 85% sẵn sàng chi <50 triệu/năm                                          │
│  • Tiềm năng: 85,000 x 50 triệu = 4,250 tỷ VND/năm                         │
│                                                                             │
│  XU HƯỚNG:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   2020      2021      2022      2023      2024      2025           │   │
│  │     │         │         │         │         │         │            │   │
│  │     ▼         ▼         ▼         ▼         ▼         ▼            │   │
│  │    ───      ───       ────      ─────    ──────   ────────         │   │
│  │    5%       8%        12%       18%       25%       35%            │   │
│  │                                                                     │   │
│  │   Tỷ lệ SME Việt Nam sử dụng công cụ scheduling                   │   │
│  │   (Dự báo)                                                         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2.2. Khoảng trống công nghệ

| Tiêu chí | Giải pháp hiện có | UIT APS |
|----------|-------------------|---------|
| **Giá** | $10K - $1M/năm | Miễn phí |
| **Ngôn ngữ** | Anh, Nhật, Đức | Tiếng Việt |
| **Tích hợp ERPNext** | Không | Có |
| **Open Source** | Không | Có |
| **AI/ML** | Có (đắt tiền) | Có (miễn phí) |
| **SME-friendly** | Không | Có |

### 3.2.3. Cơ hội đóng góp

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CƠ HỘI ĐÓNG GÓP                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ĐÓNG GÓP CHO CỘNG ĐỒNG ERPNEXT:                                        │
│     ├── ERPNext có 15,000+ stars trên GitHub                               │
│     ├── 10,000+ implementations worldwide                                  │
│     ├── Module Manufacturing còn thiếu APS                                 │
│     └── UIT APS sẽ là contribution có giá trị                              │
│                                                                             │
│  2. ĐÓNG GÓP CHO NGÀNH SẢN XUẤT VIỆT NAM:                                  │
│     ├── Giải pháp tiếng Việt đầu tiên                                      │
│     ├── Phù hợp với đặc thù SME Việt Nam                                   │
│     ├── Case study cho các nghiên cứu sau                                  │
│     └── Nền tảng cho startup/spin-off                                      │
│                                                                             │
│  3. ĐÓNG GÓP HỌC THUẬT:                                                    │
│     ├── Áp dụng OR-Tools vào bài toán thực tế                              │
│     ├── Tích hợp ML với ERP system                                         │
│     ├── Framework multi-tier scheduling                                    │
│     └── Benchmark cho các nghiên cứu sau                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3.3. Tổng kết lý do chọn đề tài

| # | Lý do | Mức độ quan trọng |
|---|-------|-------------------|
| 1 | **Nhu cầu thực tế cao** - 92% SME chưa có giải pháp | ★★★★★ |
| 2 | **Khoảng trống thị trường** - Không có giải pháp miễn phí, tiếng Việt | ★★★★★ |
| 3 | **Tính ứng dụng** - Có thể triển khai ngay cho doanh nghiệp | ★★★★☆ |
| 4 | **Tính học thuật** - Kết hợp nhiều lĩnh vực (OR, ML, ERP) | ★★★★☆ |
| 5 | **Đóng góp cộng đồng** - Open source, có thể mở rộng | ★★★★☆ |
| 6 | **Sở thích cá nhân** - Phù hợp với định hướng nghề nghiệp | ★★★☆☆ |

---

# 4. MÔ TẢ CHI TIẾT CÁC RÀNG BUỘC TỐI ƯU HÓA

## 4.1. Tổng quan về ràng buộc trong lập lịch sản xuất

### 4.1.1. Phân loại ràng buộc

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHÂN LOẠI RÀNG BUỘC LẬP LỊCH                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    RÀNG BUỘC CỨNG (Hard Constraints)                │   │
│  │               Bắt buộc phải thỏa mãn - Không vi phạm được          │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ • Machine Eligibility: Operation chỉ chạy trên máy phù hợp         │   │
│  │ • Precedence: Thứ tự operations trong một job                       │   │
│  │ • No-Overlap: Máy không xử lý 2 jobs cùng lúc                       │   │
│  │ • No-Preemption: Operation không bị gián đoạn                       │   │
│  │ • Resource Capacity: Không vượt quá năng lực tài nguyên            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    RÀNG BUỘC MỀM (Soft Constraints)                 │   │
│  │              Cố gắng thỏa mãn - Có thể vi phạm với penalty         │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ • Due Dates: Hoàn thành trước deadline (penalty nếu trễ)           │   │
│  │ • Working Hours: Làm việc trong giờ hành chính (overtime penalty)  │   │
│  │ • Setup Time: Thời gian chuẩn bị giữa các jobs                     │   │
│  │ • Priority: Ưu tiên jobs quan trọng                                │   │
│  │ • Load Balancing: Cân bằng tải giữa các máy                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 4.2. Chi tiết từng ràng buộc trong UIT APS

### 4.2.1. Ràng buộc 1: Machine Eligibility (Tính phù hợp của máy)

**Định nghĩa:** Mỗi operation chỉ có thể được thực hiện trên một hoặc một số máy nhất định.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           RÀNG BUỘC MACHINE ELIGIBILITY                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MÔ HÌNH TOÁN HỌC:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Cho:                                                               │   │
│  │  • O = {o₁, o₂, ..., oₙ}: Tập operations                           │   │
│  │  • M = {m₁, m₂, ..., mₘ}: Tập machines                             │   │
│  │  • E(oᵢ) ⊆ M: Tập máy eligible cho operation oᵢ                    │   │
│  │                                                                     │   │
│  │  Ràng buộc:                                                         │   │
│  │  ∀oᵢ ∈ O: assigned_machine(oᵢ) ∈ E(oᵢ)                             │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  VÍ DỤ THỰC TẾ:                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Operation         │ Eligible Machines                              │   │
│  │  ──────────────────┼────────────────────────────────                │   │
│  │  Tiện thô          │ Máy tiện 1, Máy tiện 2                        │   │
│  │  Phay CNC          │ Máy CNC 1, Máy CNC 2, Máy CNC 3               │   │
│  │  Mài tinh          │ Máy mài 1 (chỉ 1 máy)                         │   │
│  │  Kiểm tra          │ Trạm QC 1, Trạm QC 2                          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  IMPLEMENTATION TRONG OR-TOOLS:                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  # Chỉ tạo interval variable cho máy eligible                      │   │
│  │  for op in operations:                                              │   │
│  │      eligible_machines = get_eligible_machines(op)                  │   │
│  │      for machine in eligible_machines:                              │   │
│  │          interval = model.NewOptionalIntervalVar(...)               │   │
│  │          machine_to_intervals[machine].append(interval)             │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  NGUỒN DỮ LIỆU TRONG ERPNEXT:                                               │
│  • DocType: Operation                                                       │
│  • Field: workstation (Link to Workstation)                                │
│  • Hoặc: BOM Operation với workstation mapping                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2.2. Ràng buộc 2: Precedence (Thứ tự công đoạn)

**Định nghĩa:** Các operations trong một job phải được thực hiện theo thứ tự xác định.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           RÀNG BUỘC PRECEDENCE (THỨ TỰ CÔNG ĐOẠN)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MÔ HÌNH TOÁN HỌC:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Cho job Jᵢ với operations {oᵢ₁, oᵢ₂, ..., oᵢₖ} theo thứ tự:      │   │
│  │                                                                     │   │
│  │  Ràng buộc:                                                         │   │
│  │  ∀j ∈ {1, ..., k-1}:                                               │   │
│  │      end_time(oᵢⱼ) ≤ start_time(oᵢ,ⱼ₊₁)                           │   │
│  │                                                                     │   │
│  │  Với gap tối thiểu (min_gap):                                      │   │
│  │      end_time(oᵢⱼ) + min_gap ≤ start_time(oᵢ,ⱼ₊₁)                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  VÍ DỤ MINH HỌA:                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Job: Sản xuất trục máy                                            │   │
│  │                                                                     │   │
│  │  Op1: Cắt phôi ──▶ Op2: Tiện thô ──▶ Op3: Tiện tinh ──▶           │   │
│  │       (30 min)        (60 min)         (45 min)                    │   │
│  │                                                                     │   │
│  │       ──▶ Op4: Mài ──▶ Op5: Kiểm tra                               │   │
│  │            (30 min)      (15 min)                                  │   │
│  │                                                                     │   │
│  │  Timeline:                                                          │   │
│  │  ├──Op1──┼──────Op2──────┼─────Op3─────┼───Op4───┼─Op5─┤           │   │
│  │  0      30              90            135       165   180          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  IMPLEMENTATION TRONG OR-TOOLS:                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  def add_precedence_constraints(model, job):                        │   │
│  │      for i in range(len(job.operations) - 1):                      │   │
│  │          prev_op = job.operations[i]                                │   │
│  │          next_op = job.operations[i + 1]                           │   │
│  │                                                                     │   │
│  │          # End of prev <= Start of next                            │   │
│  │          model.Add(                                                 │   │
│  │              end_vars[prev_op] + min_gap <= start_vars[next_op]    │   │
│  │          )                                                          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  NGUỒN DỮ LIỆU TRONG ERPNEXT:                                               │
│  • DocType: BOM Operation                                                   │
│  • Field: sequence_id (số thứ tự operation)                                │
│  • DocType: Job Card                                                        │
│  • Field: sequence_id (kế thừa từ BOM)                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2.3. Ràng buộc 3: No-Overlap (Không chồng chéo)

**Định nghĩa:** Một máy không thể xử lý hai operations cùng một lúc.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           RÀNG BUỘC NO-OVERLAP (KHÔNG CHỒNG CHÉO)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MÔ HÌNH TOÁN HỌC:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Cho máy m với các operations được assign: O(m) = {o₁, o₂, ...}    │   │
│  │                                                                     │   │
│  │  Ràng buộc:                                                         │   │
│  │  ∀oᵢ, oⱼ ∈ O(m), i ≠ j:                                            │   │
│  │      end_time(oᵢ) ≤ start_time(oⱼ) OR                              │   │
│  │      end_time(oⱼ) ≤ start_time(oᵢ)                                 │   │
│  │                                                                     │   │
│  │  Diễn giải: Hai operations không được overlap trên cùng máy        │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  MINH HỌA TRỰC QUAN:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ✗ VI PHẠM (Overlap):                                              │   │
│  │                                                                     │   │
│  │  Máy M1:  ├────── Op1 ──────┤                                      │   │
│  │                   ├────── Op2 ──────┤                              │   │
│  │           0      30        60       90                              │   │
│  │                   ↑─── Overlap ───↑                                │   │
│  │                                                                     │   │
│  │  ✓ HỢP LỆ (No overlap):                                            │   │
│  │                                                                     │   │
│  │  Máy M1:  ├────── Op1 ──────┤├────── Op2 ──────┤                   │   │
│  │           0                 60                 120                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  IMPLEMENTATION TRONG OR-TOOLS:                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  def add_no_overlap_constraints(model, machine_to_intervals):       │   │
│  │      for machine, intervals in machine_to_intervals.items():        │   │
│  │          if len(intervals) > 1:                                     │   │
│  │              # AddNoOverlap is a global constraint in CP-SAT       │   │
│  │              model.AddNoOverlap(intervals)                          │   │
│  │                                                                     │   │
│  │  # CP-SAT sử dụng cumulative constraint internally                 │   │
│  │  # để enforce no overlap hiệu quả                                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  NGUỒN DỮ LIỆU TRONG ERPNEXT:                                               │
│  • Implicit từ workstation assignment                                      │
│  • Mỗi workstation = 1 resource với capacity = 1                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2.4. Ràng buộc 4: Working Hours (Giờ làm việc)

**Định nghĩa:** Operations phải được lập lịch trong giờ làm việc của workstation/ca làm việc.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           RÀNG BUỘC WORKING HOURS (GIỜ LÀM VIỆC)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MÔ HÌNH TOÁN HỌC:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Cho ca làm việc S với:                                            │   │
│  │  • start_shift: Giờ bắt đầu ca                                     │   │
│  │  • end_shift: Giờ kết thúc ca                                      │   │
│  │                                                                     │   │
│  │  Ràng buộc (cho operation o):                                      │   │
│  │  start_time(o) mod 1440 ≥ start_shift AND                          │   │
│  │  end_time(o) mod 1440 ≤ end_shift                                  │   │
│  │                                                                     │   │
│  │  (1440 = 24 * 60 phút/ngày)                                        │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  VÍ DỤ CA LÀM VIỆC:                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Ca          │ Giờ BĐ │ Giờ KT │ Phút BĐ │ Phút KT │ Ghi chú       │   │
│  │  ────────────┼────────┼────────┼─────────┼─────────┼────────────── │   │
│  │  Ca sáng     │ 06:00  │ 14:00  │   360   │   840   │               │   │
│  │  Ca chiều    │ 14:00  │ 22:00  │   840   │  1320   │               │   │
│  │  Ca đêm      │ 22:00  │ 06:00  │  1320   │   360   │ Qua ngày      │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  IMPLEMENTATION TRONG OR-TOOLS:                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  def add_working_hours_constraints(model, operations, shifts):      │   │
│  │      for op in operations:                                          │   │
│  │          workstation = op.workstation                               │   │
│  │          shift = get_shift_for_workstation(workstation)            │   │
│  │                                                                     │   │
│  │          if shift:                                                  │   │
│  │              # Tạo biến ngày                                       │   │
│  │              day = model.NewIntVar(0, max_days, f'day_{op.id}')    │   │
│  │                                                                     │   │
│  │              # Start time trong ngày                               │   │
│  │              start_in_day = model.NewIntVar(0, 1439, ...)          │   │
│  │              model.AddModuloEquality(                               │   │
│  │                  start_in_day, start_vars[op], 1440                │   │
│  │              )                                                      │   │
│  │                                                                     │   │
│  │              # Enforce trong ca làm việc                           │   │
│  │              model.Add(start_in_day >= shift.start_minutes)        │   │
│  │              model.Add(start_in_day <= shift.end_minutes - duration)│   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  NGUỒN DỮ LIỆU TRONG ERPNEXT:                                               │
│  • DocType: APS Work Shift                                                  │
│  • Fields: start_time, end_time, is_night_shift                            │
│  • DocType: Workstation                                                     │
│  • Field: working_hours (optional link to Work Shift)                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2.5. Ràng buộc 5: Due Dates (Deadline)

**Định nghĩa:** Jobs nên được hoàn thành trước deadline từ hợp đồng/đơn hàng. Đây là ràng buộc mềm với penalty.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           RÀNG BUỘC DUE DATES (DEADLINE TỪ HỢP ĐỒNG)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MÔ HÌNH TOÁN HỌC:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Cho job Jᵢ với:                                                   │   │
│  │  • Cᵢ: Completion time (thời điểm hoàn thành)                      │   │
│  │  • dᵢ: Due date (deadline từ hợp đồng)                             │   │
│  │                                                                     │   │
│  │  Tính toán:                                                         │   │
│  │  • Tardiness: Tᵢ = max(0, Cᵢ - dᵢ)                                 │   │
│  │  • Lateness:  Lᵢ = Cᵢ - dᵢ (có thể âm = sớm hạn)                   │   │
│  │                                                                     │   │
│  │  Soft constraint (penalty trong objective):                        │   │
│  │  Minimize: Σ wᵢ × Tᵢ                                               │   │
│  │  (wᵢ = trọng số theo độ ưu tiên job)                               │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  NGUỒN GỐC DEADLINE:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Hợp đồng / Sales Order                                            │   │
│  │       │                                                             │   │
│  │       ▼                                                             │   │
│  │  Delivery Date (Ngày giao hàng cam kết)                            │   │
│  │       │                                                             │   │
│  │       ▼                                                             │   │
│  │  Production Plan / Work Order                                       │   │
│  │       │                                                             │   │
│  │       ▼                                                             │   │
│  │  expected_delivery_date (Due date cho scheduling)                  │   │
│  │       │                                                             │   │
│  │       ▼                                                             │   │
│  │  Job Card Due Date = Work Order Due Date                           │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  IMPLEMENTATION TRONG OR-TOOLS:                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  def add_due_date_constraints(model, jobs):                         │   │
│  │      tardiness_vars = {}                                            │   │
│  │                                                                     │   │
│  │      for job in jobs:                                               │   │
│  │          if job.due_date:                                           │   │
│  │              due_minutes = date_to_minutes(job.due_date)           │   │
│  │              last_op = job.operations[-1]                          │   │
│  │              completion = end_vars[last_op]                        │   │
│  │                                                                     │   │
│  │              # Tardiness = max(0, completion - due_date)           │   │
│  │              tardiness = model.NewIntVar(0, horizon, f'T_{job.id}')│   │
│  │              model.AddMaxEquality(                                  │   │
│  │                  tardiness,                                         │   │
│  │                  [0, completion - due_minutes]                     │   │
│  │              )                                                      │   │
│  │              tardiness_vars[job.id] = tardiness                    │   │
│  │                                                                     │   │
│  │      return tardiness_vars                                          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  NGUỒN DỮ LIỆU TRONG ERPNEXT:                                               │
│  • DocType: Sales Order                                                     │
│  • Field: delivery_date                                                     │
│  • DocType: Work Order                                                      │
│  • Field: expected_delivery_date                                            │
│  • DocType: Production Plan                                                 │
│  • Field: plan_to_period                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2.6. Ràng buộc 6: Setup Time (Thời gian chuẩn bị)

**Định nghĩa:** Khi chuyển đổi giữa các jobs khác loại trên cùng máy, cần thời gian setup.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           RÀNG BUỘC SETUP TIME (THỜI GIAN CHUẨN BỊ)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MÔ HÌNH TOÁN HỌC:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Cho:                                                               │   │
│  │  • setup(i,j): Thời gian setup khi chuyển từ job type i sang j     │   │
│  │  • type(oₖ): Loại job của operation oₖ                              │   │
│  │                                                                     │   │
│  │  Ràng buộc (trên cùng máy):                                        │   │
│  │  Nếu oᵢ trước oⱼ trên máy m:                                       │   │
│  │      end_time(oᵢ) + setup(type(oᵢ), type(oⱼ)) ≤ start_time(oⱼ)    │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  MA TRẬN SETUP TIME (Ví dụ):                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Setup từ\đến│ Sản phẩm A │ Sản phẩm B │ Sản phẩm C │              │   │
│  │  ────────────┼────────────┼────────────┼────────────┤              │   │
│  │  Sản phẩm A  │     0      │    15 min  │    30 min  │              │   │
│  │  Sản phẩm B  │    20 min  │     0      │    25 min  │              │   │
│  │  Sản phẩm C  │    35 min  │    30 min  │     0      │              │   │
│  │                                                                     │   │
│  │  Giải thích: Setup từ A sang C mất 30 phút (đổi dao, đổi khuôn)   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  IMPLEMENTATION TRONG OR-TOOLS:                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  def add_setup_time_constraints(model, machine_ops, setup_matrix): │   │
│  │      for machine, ops in machine_ops.items():                      │   │
│  │          n = len(ops)                                               │   │
│  │          if n <= 1:                                                 │   │
│  │              continue                                               │   │
│  │                                                                     │   │
│  │          # Biến thứ tự                                             │   │
│  │          for i in range(n):                                        │   │
│  │              for j in range(n):                                    │   │
│  │                  if i != j:                                        │   │
│  │                      # before[i][j] = 1 nếu op[i] trước op[j]     │   │
│  │                      before = model.NewBoolVar(f'before_{i}_{j}') │   │
│  │                                                                     │   │
│  │                      setup = setup_matrix[ops[i].type][ops[j].type]│   │
│  │                                                                     │   │
│  │                      # Nếu i trước j, cần setup time              │   │
│  │                      model.Add(                                     │   │
│  │                          end_vars[ops[i]] + setup                  │   │
│  │                          <= start_vars[ops[j]]                     │   │
│  │                      ).OnlyEnforceIf(before)                       │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  NGUỒN DỮ LIỆU TRONG ERPNEXT:                                               │
│  • DocType: Operation (có thể thêm field setup_time)                       │
│  • Custom DocType: Setup Time Matrix                                        │
│  • Hoặc: Default setup time từ Workstation                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 4.3. Tổng hợp các ràng buộc theo hợp đồng và năng lực

### 4.3.1. Ràng buộc từ Hợp đồng/Đơn hàng

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           RÀNG BUỘC TỪ HỢP ĐỒNG / ĐƠN HÀNG                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        SALES ORDER                                  │   │
│  │                            │                                        │   │
│  │  ┌─────────────────────────┼─────────────────────────┐              │   │
│  │  │                         │                         │              │   │
│  │  ▼                         ▼                         ▼              │   │
│  │  ┌───────────┐      ┌───────────┐      ┌───────────────┐           │   │
│  │  │ Due Date  │      │ Quantity  │      │   Priority    │           │   │
│  │  │(Deadline) │      │  (Số lg)  │      │  (Độ ưu tiên) │           │   │
│  │  └─────┬─────┘      └─────┬─────┘      └───────┬───────┘           │   │
│  │        │                  │                    │                   │   │
│  │        ▼                  ▼                    ▼                   │   │
│  │  ┌───────────────────────────────────────────────────────┐        │   │
│  │  │              RÀNG BUỘC TRONG SCHEDULING               │        │   │
│  │  ├───────────────────────────────────────────────────────┤        │   │
│  │  │ • Due date constraint với tardiness penalty           │        │   │
│  │  │ • Quantity → số operations cần schedule               │        │   │
│  │  │ • Priority → weight trong objective function          │        │   │
│  │  └───────────────────────────────────────────────────────┘        │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  MAPPING DỮ LIỆU:                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ERPNext Field              │ Constraint Parameter                  │   │
│  │  ───────────────────────────┼──────────────────────────────────── │   │
│  │  Sales Order.delivery_date  │ Due date (dᵢ)                        │   │
│  │  Sales Order.priority       │ Weight trong tardiness (wᵢ)          │   │
│  │  Sales Order.qty            │ Số lượng → Work Orders → Job Cards   │   │
│  │  Customer.customer_group    │ Priority multiplier                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3.2. Ràng buộc từ Năng lực (Resource Capacity)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           RÀNG BUỘC TỪ NĂNG LỰC TÀI NGUYÊN                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. NĂNG LỰC MÁY (Machine Capacity):                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  • Working hours/day: Số giờ hoạt động mỗi ngày                    │   │
│  │  • Capacity: Số jobs có thể xử lý song song (thường = 1)           │   │
│  │  • Efficiency: Hệ số hiệu suất máy (80-100%)                       │   │
│  │  • Maintenance: Thời gian bảo trì định kỳ                          │   │
│  │                                                                     │   │
│  │  Constraint:                                                        │   │
│  │  Tổng thời gian trên máy m trong ngày d ≤ working_hours[m][d]     │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. NĂNG LỰC NHÂN VIÊN (Worker Capacity):                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  • Skill level: Cấp độ kỹ năng của nhân viên                       │   │
│  │  • Availability: Lịch làm việc, nghỉ phép                          │   │
│  │  • Multi-skill: Nhân viên có thể vận hành nhiều máy               │   │
│  │                                                                     │   │
│  │  Constraint:                                                        │   │
│  │  ∀ operation o: assigned_worker(o) ∈ qualified_workers(o)         │   │
│  │                                                                     │   │
│  │  (Trong UIT APS v1.0: Giả định 1 workstation = 1 worker)          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. NĂNG LỰC VẬT TƯ (Material Capacity):                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  • Stock availability: Tồn kho nguyên vật liệu                     │   │
│  │  • Lead time: Thời gian chờ mua hàng                               │   │
│  │                                                                     │   │
│  │  Constraint (handled by MRP module):                               │   │
│  │  start_time(o) ≥ material_available_date(o)                        │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  MAPPING DỮ LIỆU:                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ERPNext DocType           │ Capacity Parameter                     │   │
│  │  ──────────────────────────┼─────────────────────────────────────  │   │
│  │  Workstation               │ production_capacity, working_hours    │   │
│  │  Workstation Working Hour  │ start_time, end_time per day          │   │
│  │  Holiday List              │ Non-working days                       │   │
│  │  APS Work Shift            │ Shift timings                          │   │
│  │  Employee                  │ Worker availability (future)          │   │
│  │  Bin (Stock)               │ Material availability                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 4.4. Bảng tổng hợp các ràng buộc

| # | Ràng buộc | Loại | Nguồn dữ liệu | Công thức | Penalty |
|---|-----------|------|---------------|-----------|---------|
| 1 | Machine Eligibility | Hard | Operation.workstation | assigned(o) ∈ E(o) | Infeasible |
| 2 | Precedence | Hard | Job Card.sequence_id | end(oᵢ) ≤ start(oᵢ₊₁) | Infeasible |
| 3 | No-Overlap | Hard | Implicit | Disjunctive constraint | Infeasible |
| 4 | Working Hours | Soft | APS Work Shift | start ∈ [shift_start, shift_end] | Overtime cost |
| 5 | Due Dates | Soft | Work Order.expected_delivery_date | Tᵢ = max(0, Cᵢ - dᵢ) | wᵢ × Tᵢ |
| 6 | Setup Time | Soft | Setup Matrix | end(oᵢ) + setup ≤ start(oⱼ) | Lost time |

---

# 5. TIÊU CHÍ ĐÁNH GIÁ TỐI ƯU

## 5.1. Các metrics đánh giá chất lượng lịch trình

### 5.1.1. Metrics chính

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    METRICS ĐÁNH GIÁ CHẤT LƯỢNG LẬP LỊCH                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. MAKESPAN (Tổng thời gian hoàn thành)                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Định nghĩa: Cₘₐₓ = max(Cᵢ) - Thời gian từ bắt đầu đến khi        │   │
│  │              hoàn thành job cuối cùng                              │   │
│  │                                                                     │   │
│  │  Đơn vị: Phút hoặc Giờ                                             │   │
│  │                                                                     │   │
│  │  Ý nghĩa: Makespan ngắn = Tận dụng tài nguyên tốt                 │   │
│  │                                                                     │   │
│  │  Minh họa:                                                          │   │
│  │  ├────────────────────────────────────────────┤                    │   │
│  │  0                                           Cmax = 480 phút       │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. TOTAL TARDINESS (Tổng độ trễ)                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Định nghĩa: ΣTᵢ = Σmax(0, Cᵢ - dᵢ)                                │   │
│  │              Tổng thời gian trễ của tất cả jobs so với deadline    │   │
│  │                                                                     │   │
│  │  Đơn vị: Phút                                                       │   │
│  │                                                                     │   │
│  │  Ý nghĩa: Tardiness thấp = Giao hàng đúng hẹn                     │   │
│  │                                                                     │   │
│  │  Minh họa:                                                          │   │
│  │  Job 1: Due=100, Complete=90  → T₁ = 0 (đúng hạn)                 │   │
│  │  Job 2: Due=150, Complete=180 → T₂ = 30 (trễ 30 phút)             │   │
│  │  Job 3: Due=200, Complete=195 → T₃ = 0 (đúng hạn)                 │   │
│  │  Total Tardiness = 0 + 30 + 0 = 30 phút                           │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. NUMBER OF LATE JOBS (Số jobs trễ)                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Định nghĩa: ΣUᵢ với Uᵢ = 1 nếu Cᵢ > dᵢ, ngược lại = 0            │   │
│  │              Đếm số jobs không kịp deadline                        │   │
│  │                                                                     │   │
│  │  Đơn vị: Số lượng jobs                                             │   │
│  │                                                                     │   │
│  │  Ý nghĩa: Ít jobs trễ = Ít khách hàng bị ảnh hưởng               │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  4. MACHINE UTILIZATION (Hiệu suất sử dụng máy)                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Định nghĩa: U = Σ(busy_time) / Σ(available_time) × 100%           │   │
│  │              Tỷ lệ thời gian máy hoạt động / thời gian khả dụng   │   │
│  │                                                                     │   │
│  │  Đơn vị: Phần trăm (%)                                             │   │
│  │                                                                     │   │
│  │  Ý nghĩa: Utilization cao = Máy được sử dụng hiệu quả             │   │
│  │                                                                     │   │
│  │  Benchmark:                                                         │   │
│  │  • < 60%: Thấp (máy idle nhiều)                                   │   │
│  │  • 60-80%: Trung bình                                              │   │
│  │  • > 80%: Tốt                                                      │   │
│  │  • > 90%: Rất tốt (nhưng có thể thiếu buffer)                     │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.1.2. Metrics phụ

| Metric | Công thức | Đơn vị | Ý nghĩa |
|--------|-----------|--------|---------|
| **Average Flow Time** | Σ(Cᵢ - rᵢ) / n | Phút | Thời gian trung bình job ở trong hệ thống |
| **Maximum Lateness** | max(Lᵢ) = max(Cᵢ - dᵢ) | Phút | Độ trễ tệ nhất |
| **Weighted Tardiness** | Σwᵢ × Tᵢ | - | Tardiness có trọng số theo priority |
| **Setup Time Ratio** | Σsetup / Σprocessing | % | Tỷ lệ thời gian setup |

## 5.2. So sánh với Baseline (FIFO)

### 5.2.1. Phương pháp FIFO Baseline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHƯƠNG PHÁP FIFO BASELINE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ĐỊNH NGHĨA:                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  FIFO (First In First Out): Jobs được xử lý theo thứ tự đến       │   │
│  │                                                                     │   │
│  │  Thuật toán:                                                        │   │
│  │  1. Sắp xếp jobs theo thời gian tạo (creation_date)                │   │
│  │  2. Với mỗi job, lập lịch các operations tuần tự                   │   │
│  │  3. Mỗi operation được gán vào máy eligible sớm nhất               │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  IMPLEMENTATION:                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  def fifo_schedule(jobs, machines):                                 │   │
│  │      # Sort by arrival time                                         │   │
│  │      jobs = sorted(jobs, key=lambda j: j.creation_date)            │   │
│  │                                                                     │   │
│  │      machine_available = {m: 0 for m in machines}                  │   │
│  │      schedule = []                                                  │   │
│  │                                                                     │   │
│  │      for job in jobs:                                               │   │
│  │          job_end = 0                                                │   │
│  │          for op in job.operations:                                  │   │
│  │              # Find earliest available eligible machine            │   │
│  │              eligible = [m for m in machines if m in op.eligible]  │   │
│  │              machine = min(eligible, key=lambda m: machine_available[m])│
│  │                                                                     │   │
│  │              start = max(machine_available[machine], job_end)      │   │
│  │              end = start + op.duration                              │   │
│  │                                                                     │   │
│  │              schedule.append((op, machine, start, end))            │   │
│  │              machine_available[machine] = end                      │   │
│  │              job_end = end                                          │   │
│  │                                                                     │   │
│  │      return schedule                                                │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  TẠI SAO CHỌN FIFO LÀM BASELINE:                                           │
│  • Phổ biến nhất trong thực tế (dễ hiểu, dễ thực hiện)                    │
│  • Công bằng (jobs đến trước được xử lý trước)                            │
│  • Không cần optimization (baseline thấp nhất)                            │
│  • Dễ so sánh và chứng minh improvement                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2.2. Công thức tính % cải thiện

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CÔNG THỨC TÍNH % CẢI THIỆN                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. MAKESPAN IMPROVEMENT:                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Improvement_makespan = (FIFO_makespan - APS_makespan)             │   │
│  │                         ────────────────────────────── × 100%      │   │
│  │                              FIFO_makespan                          │   │
│  │                                                                     │   │
│  │  Ví dụ: FIFO = 500 phút, APS = 400 phút                           │   │
│  │         Improvement = (500 - 400) / 500 × 100% = 20%               │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. LATE JOBS REDUCTION:                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Reduction_late_jobs = (FIFO_late - APS_late)                      │   │
│  │                        ────────────────────── × 100%               │   │
│  │                             FIFO_late                               │   │
│  │                                                                     │   │
│  │  Ví dụ: FIFO = 10 jobs trễ, APS = 4 jobs trễ                      │   │
│  │         Reduction = (10 - 4) / 10 × 100% = 60%                     │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. TARDINESS REDUCTION:                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Reduction_tardiness = (FIFO_tardiness - APS_tardiness)            │   │
│  │                        ──────────────────────────────── × 100%     │   │
│  │                              FIFO_tardiness                         │   │
│  │                                                                     │   │
│  │  Ví dụ: FIFO = 200 phút tardiness, APS = 80 phút                  │   │
│  │         Reduction = (200 - 80) / 200 × 100% = 60%                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  4. UTILIZATION IMPROVEMENT:                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Improvement_util = APS_utilization - FIFO_utilization             │   │
│  │                     (đơn vị: percentage points)                    │   │
│  │                                                                     │   │
│  │  Ví dụ: FIFO = 62%, APS = 78%                                      │   │
│  │         Improvement = 78% - 62% = +16 percentage points            │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 5.3. Tiêu chí đánh giá "Tối ưu" trong UIT APS

### 5.3.1. Mục tiêu tối ưu (Objective Function)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HÀM MỤC TIÊU TỐI ƯU HÓA                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MULTI-OBJECTIVE FUNCTION:                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Minimize:                                                          │   │
│  │                                                                     │   │
│  │  Z = α × Cmax + β × Σ(wᵢ × Tᵢ)                                     │   │
│  │      ─────────   ─────────────                                      │   │
│  │      Makespan    Weighted Tardiness                                 │   │
│  │                                                                     │   │
│  │  Trong đó:                                                          │   │
│  │  • Cmax: Makespan (thời gian hoàn thành)                           │   │
│  │  • Tᵢ: Tardiness của job i                                         │   │
│  │  • wᵢ: Weight của job i (theo priority)                            │   │
│  │  • α: Makespan weight (default = 1.0)                              │   │
│  │  • β: Tardiness weight (default = 10.0)                            │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Ý NGHĨA CỦA TRỌNG SỐ:                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  α : β = 1 : 10 (default)                                          │   │
│  │  → Ưu tiên giảm tardiness hơn makespan                             │   │
│  │  → Phù hợp khi giao hàng đúng hạn quan trọng hơn                  │   │
│  │                                                                     │   │
│  │  α : β = 1 : 1                                                     │   │
│  │  → Cân bằng giữa makespan và tardiness                             │   │
│  │                                                                     │   │
│  │  α : β = 10 : 1                                                    │   │
│  │  → Ưu tiên giảm makespan                                           │   │
│  │  → Phù hợp khi cần tối đa hóa throughput                          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3.2. Ngưỡng đánh giá "Tối ưu"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NGƯỠNG ĐÁNH GIÁ "TỐI ƯU"                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SOLVER STATUS:                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Status          │ Ý nghĩa                        │ Đánh giá        │   │
│  │  ────────────────┼────────────────────────────────┼───────────────  │   │
│  │  OPTIMAL         │ Chứng minh là lời giải tốt nhất│ Tối ưu hoàn toàn│   │
│  │  FEASIBLE        │ Lời giải khả thi, có thể chưa  │ Tối ưu tương đối│   │
│  │                  │ phải tốt nhất                  │                 │   │
│  │  INFEASIBLE      │ Không tìm được lời giải        │ Thất bại        │   │
│  │  TIMEOUT         │ Hết thời gian, trả về best     │ Acceptable      │   │
│  │                  │ found solution                 │                 │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  OPTIMALITY GAP:                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Gap = (best_found - lower_bound) / lower_bound × 100%             │   │
│  │                                                                     │   │
│  │  Gap          │ Đánh giá                                           │   │
│  │  ─────────────┼───────────────────────────────────────────────     │   │
│  │  0%           │ Optimal (chứng minh được)                         │   │
│  │  < 1%         │ Near-optimal (rất tốt)                            │   │
│  │  1-5%         │ Good (tốt)                                        │   │
│  │  5-10%        │ Acceptable (chấp nhận được)                       │   │
│  │  > 10%        │ May need improvement                              │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  IMPROVEMENT vs BASELINE:                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Metric                │ Minimum Improvement │ Target Improvement   │   │
│  │  ──────────────────────┼─────────────────────┼────────────────────  │   │
│  │  Makespan              │ ≥ 10%               │ ≥ 20%               │   │
│  │  Late Jobs             │ ≥ 20%               │ ≥ 40%               │   │
│  │  Total Tardiness       │ ≥ 30%               │ ≥ 50%               │   │
│  │  Machine Utilization   │ +5 pp               │ +15 pp              │   │
│  │                                                                     │   │
│  │  (pp = percentage points)                                          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  KẾT LUẬN "TỐI ƯU":                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Lịch trình được coi là "TỐI ƯU" khi:                              │   │
│  │                                                                     │   │
│  │  ✓ Solver status = OPTIMAL hoặc FEASIBLE với gap < 5%              │   │
│  │  ✓ Makespan improvement ≥ 10% so với FIFO                          │   │
│  │  ✓ Late jobs reduction ≥ 20% so với FIFO                           │   │
│  │  ✓ Tất cả hard constraints được thỏa mãn                           │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 5.4. Dashboard hiển thị so sánh

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           COMPARISON DASHBOARD (Thiết kế UI)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║                    SCHEDULING COMPARISON                              ║ │
│  ╠═══════════════════════════════════════════════════════════════════════╣ │
│  ║                                                                       ║ │
│  ║  ┌─────────────────────────────────────────────────────────────────┐ ║ │
│  ║  │                     METRICS COMPARISON                          │ ║ │
│  ║  ├─────────────────────────────────────────────────────────────────┤ ║ │
│  ║  │                                                                 │ ║ │
│  ║  │   Metric          │  FIFO      │  UIT APS   │  Improvement     │ ║ │
│  ║  │   ────────────────┼────────────┼────────────┼──────────────    │ ║ │
│  ║  │   Makespan        │  600 min   │  480 min   │  ▼ 20.0%  ✓     │ ║ │
│  ║  │   Late Jobs       │  8         │  3         │  ▼ 62.5%  ✓     │ ║ │
│  ║  │   Total Tardiness │  180 min   │  45 min    │  ▼ 75.0%  ✓     │ ║ │
│  ║  │   Utilization     │  62%       │  78%       │  ▲ +16 pp ✓     │ ║ │
│  ║  │                                                                 │ ║ │
│  ║  └─────────────────────────────────────────────────────────────────┘ ║ │
│  ║                                                                       ║ │
│  ║  ┌─────────────────────────────────────────────────────────────────┐ ║ │
│  ║  │                     VISUAL COMPARISON                           │ ║ │
│  ║  ├─────────────────────────────────────────────────────────────────┤ ║ │
│  ║  │                                                                 │ ║ │
│  ║  │   Makespan:                                                     │ ║ │
│  ║  │   FIFO:    ████████████████████████████████████████ 600        │ ║ │
│  ║  │   UIT APS: ████████████████████████████████ 480                │ ║ │
│  ║  │                                                                 │ ║ │
│  ║  │   Late Jobs:                                                    │ ║ │
│  ║  │   FIFO:    ████████ 8                                          │ ║ │
│  ║  │   UIT APS: ███ 3                                               │ ║ │
│  ║  │                                                                 │ ║ │
│  ║  │   Utilization:                                                  │ ║ │
│  ║  │   FIFO:    ████████████████████████████████ 62%                │ ║ │
│  ║  │   UIT APS: ██████████████████████████████████████████ 78%     │ ║ │
│  ║  │                                                                 │ ║ │
│  ║  └─────────────────────────────────────────────────────────────────┘ ║ │
│  ║                                                                       ║ │
│  ║  ┌─────────────────────────────────────────────────────────────────┐ ║ │
│  ║  │                     OPTIMIZATION STATUS                         │ ║ │
│  ║  ├─────────────────────────────────────────────────────────────────┤ ║ │
│  ║  │                                                                 │ ║ │
│  ║  │   Solver Status:     [  OPTIMAL  ✓ ]                           │ ║ │
│  ║  │   Optimality Gap:    [   0.0%    ✓ ]                           │ ║ │
│  ║  │   Solve Time:        [  45.2 sec   ]                           │ ║ │
│  ║  │   Overall Result:    [ ★★★★★ EXCELLENT ]                       │ ║ │
│  ║  │                                                                 │ ║ │
│  ║  └─────────────────────────────────────────────────────────────────┘ ║ │
│  ║                                                                       ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 6. CHỨC NĂNG XUẤT GANTT CHART VỚI DEADLINE VÀ THUẬT TOÁN TỐI ƯU

## 6.1. Mô tả chức năng Gantt Chart

### 6.1.1. Tổng quan

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GANTT CHART VISUALIZATION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MỤC ĐÍCH:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  • Hiển thị lịch trình sản xuất dưới dạng biểu đồ trực quan       │   │
│  │  • Hiển thị deadline từ hợp đồng/đơn hàng                          │   │
│  │  • Phân biệt jobs đúng hạn và trễ hạn bằng màu sắc                │   │
│  │  • Cho phép export để báo cáo và chia sẻ                          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  CÁC THÀNH PHẦN GANTT:                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌───────────────────────────────────────────────────────────────┐ │   │
│  │  │ TIMELINE HEADER                                               │ │   │
│  │  │ [Day 1] [Day 2] [Day 3] [Day 4] [Day 5] ...                  │ │   │
│  │  ├───────────────────────────────────────────────────────────────┤ │   │
│  │  │                                                               │ │   │
│  │  │ MACHINE ROWS                                                  │ │   │
│  │  │                                                               │ │   │
│  │  │ M1: ████ Job1 ████│████ Job3 ████│    │                      │ │   │
│  │  │                                   │    │                      │ │   │
│  │  │ M2:    │████ Job2 ████████│████ Job4 ████│                   │ │   │
│  │  │        │                  │              │                    │ │   │
│  │  │ M3: ████ Job5 ████│          │████ Job6 ████│                │ │   │
│  │  │                   │          │              │                 │ │   │
│  │  │                   ▼          ▼              ▼                 │ │   │
│  │  │                 [DL1]      [DL2]          [DL3]               │ │   │
│  │  │                Deadline   Deadline       Deadline             │ │   │
│  │  │                                                               │ │   │
│  │  └───────────────────────────────────────────────────────────────┘ │   │
│  │                                                                     │   │
│  │  LEGEND:                                                            │   │
│  │  ████ On-time Job    ████ Late Job ⚠    ▼ Deadline marker         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.1.2. Thông tin hiển thị trên Gantt

| Thành phần | Thông tin | Nguồn dữ liệu |
|------------|-----------|---------------|
| **Task bar** | Job Card, Operation, Duration | APS Scheduling Result |
| **Row** | Machine/Workstation | APS Scheduling Result.workstation |
| **Color** | On-time (green) / Late (red) | APS Scheduling Result.is_late |
| **Deadline marker** | Due date line | Work Order.expected_delivery_date |
| **Tooltip** | Chi tiết job: WO, Item, Qty, Time | Multiple sources |

## 6.2. Thuật toán tối ưu có ràng buộc

### 6.2.1. Quy trình tối ưu hóa

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           QUY TRÌNH TỐI ƯU HÓA LẬP LỊCH VỚI RÀNG BUỘC                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INPUT:                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │  Work Orders │  │ Workstations│  │  Deadlines  │                 │   │
│  │  │  (Jobs)      │  │ (Machines)  │  │ (Due Dates) │                 │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │   │
│  │         │                │                │                         │   │
│  │         │     ┌──────────┴──────────┐     │                         │   │
│  │         │     │                     │     │                         │   │
│  │         ▼     ▼                     ▼     ▼                         │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                 CONSTRAINT BUILDER                          │   │   │
│  │  ├─────────────────────────────────────────────────────────────┤   │   │
│  │  │ 1. Machine Eligibility: Job Card → Workstation mapping     │   │   │
│  │  │ 2. Precedence: BOM Operation sequence                      │   │   │
│  │  │ 3. No-Overlap: Implicit from machine assignment            │   │   │
│  │  │ 4. Working Hours: APS Work Shift → time windows            │   │   │
│  │  │ 5. Due Dates: Work Order → deadline constraints            │   │   │
│  │  │ 6. Setup Time: (Optional) Setup matrix                     │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                      │   │
│  └──────────────────────────────┼──────────────────────────────────────┘   │
│                                 │                                          │
│                                 ▼                                          │
│  OPTIMIZATION:                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │              OR-TOOLS CP-SAT SOLVER                         │   │   │
│  │  ├─────────────────────────────────────────────────────────────┤   │   │
│  │  │                                                             │   │   │
│  │  │  Minimize: α × Makespan + β × Σ(wᵢ × Tardiness)            │   │   │
│  │  │                                                             │   │   │
│  │  │  Subject to:                                                │   │   │
│  │  │  • All hard constraints (Machine, Precedence, No-Overlap)  │   │   │
│  │  │  • Time limit: 300 seconds (configurable)                  │   │   │
│  │  │  • Parallel search: 8 workers                              │   │   │
│  │  │                                                             │   │   │
│  │  │  Techniques:                                                │   │   │
│  │  │  • Lazy Clause Generation                                  │   │   │
│  │  │  • Symmetry Breaking                                       │   │   │
│  │  │  • Search Heuristics                                       │   │   │
│  │  │                                                             │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                      │   │
│  └──────────────────────────────┼──────────────────────────────────────┘   │
│                                 │                                          │
│                                 ▼                                          │
│  OUTPUT:                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │   │
│  │  │ Scheduling      │  │ Gantt Chart     │  │ Comparison      │     │   │
│  │  │ Results         │  │ Data            │  │ Metrics         │     │   │
│  │  │ (DB records)    │  │ (JSON)          │  │ (vs FIFO)       │     │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2.2. Tích hợp deadline từ hợp đồng

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           TÍCH HỢP DEADLINE TỪ HỢP ĐỒNG                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LUỒNG DỮ LIỆU DEADLINE:                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌─────────────────┐                                               │   │
│  │  │  Sales Order    │  delivery_date = "2025-02-15"                 │   │
│  │  │  (Hợp đồng)     │  priority = "High"                            │   │
│  │  │  Customer: ABC  │  customer_group = "VIP"                       │   │
│  │  └────────┬────────┘                                               │   │
│  │           │                                                         │   │
│  │           ▼                                                         │   │
│  │  ┌─────────────────┐                                               │   │
│  │  │ Production Plan │  Tạo từ Forecast hoặc Sales Order             │   │
│  │  │ plan_to_period  │  = delivery_date - buffer_days                │   │
│  │  └────────┬────────┘                                               │   │
│  │           │                                                         │   │
│  │           ▼                                                         │   │
│  │  ┌─────────────────┐                                               │   │
│  │  │  Work Order     │  expected_delivery_date = plan_to_period      │   │
│  │  │  (Lệnh SX)      │  priority = inherited from SO                 │   │
│  │  └────────┬────────┘                                               │   │
│  │           │                                                         │   │
│  │           ▼                                                         │   │
│  │  ┌─────────────────┐                                               │   │
│  │  │  APS Scheduling │  due_date = expected_delivery_date            │   │
│  │  │  (Constraint)   │  weight = priority_to_weight(priority)        │   │
│  │  └────────┬────────┘                                               │   │
│  │           │                                                         │   │
│  │           ▼                                                         │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  Tardiness Calculation:                                     │   │   │
│  │  │  Tᵢ = max(0, completion_time - due_date)                   │   │   │
│  │  │                                                             │   │   │
│  │  │  Weighted Tardiness:                                        │   │   │
│  │  │  WT = Σ weightᵢ × Tᵢ                                       │   │   │
│  │  │                                                             │   │   │
│  │  │  Priority Weights:                                          │   │   │
│  │  │  • Urgent: w = 100                                         │   │   │
│  │  │  • High:   w = 50                                          │   │   │
│  │  │  • Medium: w = 10                                          │   │   │
│  │  │  • Low:    w = 1                                           │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 6.3. Tính chất công việc và năng lực nhân viên

### 6.3.1. Mô hình hóa tính chất công việc

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           TÍNH CHẤT CÔNG VIỆC TRONG LẬP LỊCH                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ĐỘ PHỨC TẠP CÔNG VIỆC (Job Complexity):                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Complexity Level │ Số Operations │ Skill Required │ Duration      │   │
│  │  ─────────────────┼───────────────┼────────────────┼──────────     │   │
│  │  Simple           │ 1-3           │ Basic          │ < 2 hours    │   │
│  │  Medium           │ 4-6           │ Intermediate   │ 2-8 hours    │   │
│  │  Complex          │ 7+            │ Advanced       │ > 8 hours    │   │
│  │                                                                     │   │
│  │  Ảnh hưởng đến scheduling:                                         │   │
│  │  • Complex jobs → cần ưu tiên bắt đầu sớm                         │   │
│  │  • Complex jobs → cần nhân viên có skill cao                      │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. LOẠI CÔNG VIỆC (Job Type):                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Type           │ Characteristics           │ Scheduling Priority  │   │
│  │  ───────────────┼───────────────────────────┼────────────────────  │   │
│  │  Make-to-Order  │ Custom, có deadline cứng  │ Cao (penalty nặng)  │   │
│  │  Make-to-Stock  │ Standard, linh hoạt       │ Trung bình          │   │
│  │  Prototype      │ Không có deadline         │ Thấp                │   │
│  │  Rework         │ Urgent, cần làm lại       │ Rất cao             │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. YÊU CẦU ĐẶC BIỆT:                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  • Batch processing: Một số jobs có thể gom batch                  │   │
│  │  • Sequence-dependent setup: Setup phụ thuộc thứ tự               │   │
│  │  • Alternative routing: Có thể dùng BOM khác                       │   │
│  │  • Split jobs: Có thể chia nhỏ job (future feature)               │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.3.2. Mô hình hóa năng lực nhân viên (Future Enhancement)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           NĂNG LỰC NHÂN VIÊN (WORKER CAPABILITY MODEL)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LƯU Ý: Đây là feature cho phiên bản tương lai (v2.0+)                     │
│  Hiện tại UIT APS v1.0 giả định: 1 Workstation = 1 Worker                  │
│                                                                             │
│  MÔ HÌNH ĐỀ XUẤT:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌─────────────────┐        ┌─────────────────┐                    │   │
│  │  │     Worker      │        │   Skill Matrix  │                    │   │
│  │  ├─────────────────┤        ├─────────────────┤                    │   │
│  │  │ employee_id     │───────▶│ worker_id       │                    │   │
│  │  │ name            │        │ operation_type  │                    │   │
│  │  │ department      │        │ skill_level     │                    │   │
│  │  │ shift           │        │ efficiency      │                    │   │
│  │  │ availability    │        │ certified_date  │                    │   │
│  │  └─────────────────┘        └─────────────────┘                    │   │
│  │           │                          │                              │   │
│  │           │                          │                              │   │
│  │           ▼                          ▼                              │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │              WORKER-OPERATION MATCHING                      │   │   │
│  │  ├─────────────────────────────────────────────────────────────┤   │   │
│  │  │                                                             │   │   │
│  │  │  Constraint:                                                │   │   │
│  │  │  ∀ operation o:                                            │   │   │
│  │  │    assigned_worker(o) ∈ {w | skill(w, o.type) >= o.required}│   │   │
│  │  │                                                             │   │   │
│  │  │  Duration adjustment:                                       │   │   │
│  │  │  actual_duration = base_duration / efficiency(worker)       │   │   │
│  │  │                                                             │   │   │
│  │  │  Example:                                                   │   │   │
│  │  │  • Operation: CNC Milling, required skill = 3              │   │   │
│  │  │  • Worker A: skill = 4, efficiency = 1.1 → 90% thời gian   │   │   │
│  │  │  • Worker B: skill = 3, efficiency = 0.9 → 110% thời gian  │   │   │
│  │  │  • Worker C: skill = 2 → Không đủ điều kiện                │   │   │
│  │  │                                                             │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ERPNEXT INTEGRATION (Future):                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  • DocType: Employee → Worker information                          │   │
│  │  • DocType: Employee Skill Map → Skill matrix                      │   │
│  │  • DocType: Attendance → Availability                              │   │
│  │  • DocType: Leave Application → Planned absence                    │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 6.4. Implementation chi tiết Gantt Export

### 6.4.1. API Gantt Data

```python
# uit_aps/scheduling/api/gantt_api.py

import frappe
from frappe import _
from datetime import datetime, timedelta
import json

@frappe.whitelist()
def get_gantt_chart_data(scheduling_run_name, include_deadlines=True):
    """
    Generate Gantt chart data with deadlines

    Returns:
    {
        "tasks": [...],
        "deadlines": [...],
        "machines": [...],
        "metrics": {...}
    }
    """

    run = frappe.get_doc("APS Scheduling Run", scheduling_run_name)

    # Get scheduling results
    results = frappe.get_all(
        "APS Scheduling Result",
        filters={"scheduling_run": scheduling_run_name},
        fields=["name", "job_card", "workstation", "operation",
               "planned_start_time", "planned_end_time",
               "is_late", "is_applied", "work_shift"]
    )

    tasks = []
    deadlines = []
    machines = set()

    for result in results:
        # Get job card details
        jc = frappe.get_doc("Job Card", result.job_card)
        wo = frappe.get_doc("Work Order", jc.work_order)

        # Task data
        task = {
            "id": result.name,
            "name": f"{wo.name} - {result.operation}",
            "start": result.planned_start_time.isoformat(),
            "end": result.planned_end_time.isoformat(),
            "resource": result.workstation,
            "progress": 0,
            "color": get_task_color(result.is_late, result.is_applied),
            "is_late": result.is_late,
            "is_applied": result.is_applied,

            # Additional info for tooltip
            "work_order": wo.name,
            "item": wo.production_item,
            "qty": wo.qty,
            "job_card": result.job_card,
            "duration_mins": (result.planned_end_time - result.planned_start_time).total_seconds() / 60
        }
        tasks.append(task)
        machines.add(result.workstation)

        # Deadline data (one per work order)
        if include_deadlines and wo.expected_delivery_date:
            deadline_id = f"DL_{wo.name}"
            if not any(d["id"] == deadline_id for d in deadlines):
                deadlines.append({
                    "id": deadline_id,
                    "work_order": wo.name,
                    "date": wo.expected_delivery_date.isoformat() if isinstance(wo.expected_delivery_date, datetime) else wo.expected_delivery_date,
                    "priority": wo.priority or "Medium",
                    "label": f"Due: {wo.name}"
                })

    # Machine list with working hours
    machine_list = []
    for m in machines:
        ws = frappe.get_doc("Workstation", m)
        machine_list.append({
            "id": m,
            "name": ws.workstation_name,
            "working_hours": ws.working_hours_per_day or 8
        })

    # Metrics summary
    metrics = {
        "total_tasks": len(tasks),
        "late_tasks": len([t for t in tasks if t["is_late"]]),
        "on_time_tasks": len([t for t in tasks if not t["is_late"]]),
        "makespan": run.makespan_minutes,
        "utilization": run.machine_utilization,
        "improvement_vs_fifo": run.improvement_makespan_percent
    }

    return {
        "tasks": tasks,
        "deadlines": deadlines,
        "machines": machine_list,
        "metrics": metrics,
        "run_info": {
            "name": run.name,
            "status": run.run_status,
            "solver_status": run.solver_status,
            "strategy": run.scheduling_strategy
        }
    }


def get_task_color(is_late, is_applied):
    """Get color based on task status"""
    if is_late:
        return "#ef4444"  # Red for late
    elif is_applied:
        return "#22c55e"  # Green for applied
    else:
        return "#3b82f6"  # Blue for pending


@frappe.whitelist()
def export_gantt_to_image(scheduling_run_name, format="png", width=1200, height=800):
    """
    Export Gantt chart to image file

    Returns: File URL
    """
    # This would typically use a headless browser or
    # server-side chart library like matplotlib

    gantt_data = get_gantt_chart_data(scheduling_run_name)

    # Generate image using matplotlib or similar
    # (Simplified - actual implementation would be more complex)

    from io import BytesIO
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    fig, ax = plt.subplots(figsize=(width/100, height/100))

    # Plot tasks
    machines = {m["id"]: i for i, m in enumerate(gantt_data["machines"])}
    colors = {"late": "#ef4444", "on_time": "#22c55e", "pending": "#3b82f6"}

    for task in gantt_data["tasks"]:
        y = machines[task["resource"]]
        start = datetime.fromisoformat(task["start"])
        end = datetime.fromisoformat(task["end"])
        duration = (end - start).total_seconds() / 3600  # hours

        color = colors["late"] if task["is_late"] else colors["on_time"]

        ax.barh(y, duration, left=start.timestamp()/3600, height=0.6,
               color=color, edgecolor="black", linewidth=0.5)

    # Plot deadlines
    for deadline in gantt_data["deadlines"]:
        deadline_time = datetime.fromisoformat(deadline["date"]).timestamp() / 3600
        ax.axvline(x=deadline_time, color="red", linestyle="--", linewidth=1)

    # Formatting
    ax.set_yticks(range(len(machines)))
    ax.set_yticklabels([m["name"] for m in gantt_data["machines"]])
    ax.set_xlabel("Time")
    ax.set_title(f"Production Schedule: {scheduling_run_name}")

    # Legend
    legend_patches = [
        mpatches.Patch(color=colors["on_time"], label="On-time"),
        mpatches.Patch(color=colors["late"], label="Late"),
        mpatches.Patch(color="red", label="Deadline", linestyle="--")
    ]
    ax.legend(handles=legend_patches, loc="upper right")

    # Save to file
    buffer = BytesIO()
    plt.savefig(buffer, format=format, dpi=100, bbox_inches="tight")
    buffer.seek(0)

    # Save as Frappe file
    filename = f"gantt_{scheduling_run_name}.{format}"
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "content": buffer.read(),
        "is_private": 0
    })
    file_doc.save()

    plt.close()

    return file_doc.file_url
```

### 6.4.2. Frontend Gantt Component

```javascript
// uit_aps/public/js/gantt_chart.js

frappe.provide("uit_aps.gantt");

uit_aps.gantt.GanttChart = class GanttChart {
    constructor(options) {
        this.scheduling_run = options.scheduling_run;
        this.container = options.container;
        this.data = null;
    }

    async load() {
        // Fetch data from API
        const response = await frappe.call({
            method: "uit_aps.scheduling.api.gantt_api.get_gantt_chart_data",
            args: {
                scheduling_run_name: this.scheduling_run,
                include_deadlines: true
            }
        });

        this.data = response.message;
        this.render();
    }

    render() {
        // Clear container
        this.container.innerHTML = "";

        // Create Gantt using frappe-gantt or custom implementation
        const tasks = this.data.tasks.map(task => ({
            id: task.id,
            name: task.name,
            start: task.start,
            end: task.end,
            progress: task.progress,
            custom_class: task.is_late ? "late-task" : "on-time-task"
        }));

        // Initialize Gantt
        this.gantt = new Gantt(this.container, tasks, {
            view_mode: "Day",
            date_format: "YYYY-MM-DD HH:mm",
            custom_popup_html: (task) => this.getPopupHtml(task),
            on_click: (task) => this.onTaskClick(task),
            on_date_change: (task, start, end) => this.onDateChange(task, start, end)
        });

        // Add deadlines as vertical lines
        this.renderDeadlines();

        // Add metrics summary
        this.renderMetrics();
    }

    getPopupHtml(task) {
        const taskData = this.data.tasks.find(t => t.id === task.id);

        return `
            <div class="gantt-popup">
                <h4>${taskData.name}</h4>
                <table>
                    <tr><td>Work Order:</td><td>${taskData.work_order}</td></tr>
                    <tr><td>Item:</td><td>${taskData.item}</td></tr>
                    <tr><td>Quantity:</td><td>${taskData.qty}</td></tr>
                    <tr><td>Duration:</td><td>${taskData.duration_mins} min</td></tr>
                    <tr><td>Status:</td><td>${taskData.is_late ? "⚠️ Late" : "✓ On-time"}</td></tr>
                </table>
            </div>
        `;
    }

    renderDeadlines() {
        // Add deadline markers
        const svg = this.container.querySelector("svg");

        this.data.deadlines.forEach(deadline => {
            const x = this.gantt.date_utils.convert_to_x(new Date(deadline.date));

            // Vertical line
            const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
            line.setAttribute("x1", x);
            line.setAttribute("x2", x);
            line.setAttribute("y1", 0);
            line.setAttribute("y2", "100%");
            line.setAttribute("stroke", "#ef4444");
            line.setAttribute("stroke-dasharray", "5,5");
            line.setAttribute("class", "deadline-line");

            // Label
            const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
            text.setAttribute("x", x);
            text.setAttribute("y", 15);
            text.setAttribute("fill", "#ef4444");
            text.setAttribute("font-size", "10");
            text.textContent = deadline.label;

            svg.appendChild(line);
            svg.appendChild(text);
        });
    }

    renderMetrics() {
        const metrics = this.data.metrics;

        const metricsHtml = `
            <div class="gantt-metrics">
                <div class="metric">
                    <span class="label">Total Tasks:</span>
                    <span class="value">${metrics.total_tasks}</span>
                </div>
                <div class="metric">
                    <span class="label">On-time:</span>
                    <span class="value text-success">${metrics.on_time_tasks}</span>
                </div>
                <div class="metric">
                    <span class="label">Late:</span>
                    <span class="value text-danger">${metrics.late_tasks}</span>
                </div>
                <div class="metric">
                    <span class="label">Makespan:</span>
                    <span class="value">${metrics.makespan} min</span>
                </div>
                <div class="metric">
                    <span class="label">vs FIFO:</span>
                    <span class="value text-success">↓${metrics.improvement_vs_fifo?.toFixed(1)}%</span>
                </div>
            </div>
        `;

        const metricsContainer = document.createElement("div");
        metricsContainer.innerHTML = metricsHtml;
        this.container.parentElement.insertBefore(metricsContainer, this.container);
    }

    async exportImage(format = "png") {
        frappe.call({
            method: "uit_aps.scheduling.api.gantt_api.export_gantt_to_image",
            args: {
                scheduling_run_name: this.scheduling_run,
                format: format
            },
            callback: (r) => {
                if (r.message) {
                    // Open in new tab or download
                    window.open(r.message, "_blank");
                }
            }
        });
    }
};

// Usage in form
frappe.ui.form.on("APS Scheduling Run", {
    view_gantt_chart: function(frm) {
        const dialog = new frappe.ui.Dialog({
            title: __("Production Schedule - Gantt Chart"),
            size: "extra-large"
        });

        dialog.show();

        const gantt = new uit_aps.gantt.GanttChart({
            scheduling_run: frm.doc.name,
            container: dialog.$body[0]
        });

        gantt.load();

        // Add export button
        dialog.set_primary_action(__("Export PNG"), () => {
            gantt.exportImage("png");
        });
    }
});
```

---

# 7. DANH SÁCH TÀI LIỆU THAM KHẢO CHI TIẾT

## 7.1. Sách và Giáo trình

### 7.1.1. Lập lịch sản xuất (Production Scheduling)

| # | Tác giả | Năm | Tựa sách | NXB | ISBN |
|---|---------|-----|----------|-----|------|
| [1] | Pinedo, M.L. | 2016 | **Scheduling: Theory, Algorithms, and Systems** (5th ed.) | Springer | 978-3-319-26580-3 |
| [2] | Baker, K.R. & Trietsch, D. | 2019 | **Principles of Sequencing and Scheduling** (2nd ed.) | Wiley | 978-1-119-26257-3 |
| [3] | Brucker, P. | 2007 | **Scheduling Algorithms** (5th ed.) | Springer | 978-3-540-69515-8 |
| [4] | Blazewicz, J. et al. | 2019 | **Handbook on Scheduling** (2nd ed.) | Springer | 978-3-319-99848-0 |

### 7.1.2. Constraint Programming và Tối ưu hóa

| # | Tác giả | Năm | Tựa sách | NXB | ISBN |
|---|---------|-----|----------|-----|------|
| [5] | Rossi, F. et al. | 2006 | **Handbook of Constraint Programming** | Elsevier | 978-0-444-52726-4 |
| [6] | Apt, K. | 2003 | **Principles of Constraint Programming** | Cambridge | 978-0-521-82583-2 |
| [7] | Baptiste, P. et al. | 2001 | **Constraint-Based Scheduling** | Springer | 978-1-4020-7514-6 |

### 7.1.3. Machine Learning và Dự báo

| # | Tác giả | Năm | Tựa sách | NXB | ISBN |
|---|---------|-----|----------|-----|------|
| [8] | Hyndman, R.J. & Athanasopoulos, G. | 2021 | **Forecasting: Principles and Practice** (3rd ed.) | OTexts | Online |
| [9] | Box, G.E.P. et al. | 2015 | **Time Series Analysis: Forecasting and Control** (5th ed.) | Wiley | 978-1-118-67502-1 |
| [10] | Sutton, R.S. & Barto, A.G. | 2018 | **Reinforcement Learning: An Introduction** (2nd ed.) | MIT Press | 978-0-262-03924-6 |

### 7.1.4. ERP và Supply Chain

| # | Tác giả | Năm | Tựa sách | NXB | ISBN |
|---|---------|-----|----------|-----|------|
| [11] | Stadtler, H. & Kilger, C. | 2015 | **Supply Chain Management and Advanced Planning** (5th ed.) | Springer | 978-3-642-55308-0 |
| [12] | Dolgui, A. & Proth, J.M. | 2010 | **Supply Chain Engineering: Useful Methods and Techniques** | Springer | 978-1-84996-016-8 |
| [13] | Vollmann, T.E. et al. | 2005 | **Manufacturing Planning and Control for Supply Chain Management** (5th ed.) | McGraw-Hill | 978-0-07-144033-2 |

## 7.2. Bài báo khoa học (Journal & Conference Papers)

### 7.2.1. Constraint Programming cho Scheduling

| # | Tác giả | Năm | Tiêu đề | Nguồn | DOI/Link |
|---|---------|-----|---------|-------|----------|
| [14] | Da Col, G. & Teppan, E. | 2022 | **Industrial-Size Job Shop Scheduling with Constraint Programming** | CPAIOR 2022 | 10.1007/978-3-031-08011-1_12 |
| [15] | Laborie, P. et al. | 2018 | **IBM ILOG CP Optimizer for Scheduling** | Constraints | 10.1007/s10601-018-9281-x |
| [16] | Ku, W.Y. & Beck, J.C. | 2016 | **Mixed Integer Programming Models for Job Shop Scheduling: A Computational Analysis** | Computers & OR | 10.1016/j.cor.2016.04.006 |

### 7.2.2. Machine Learning cho Scheduling

| # | Tác giả | Năm | Tiêu đề | Nguồn | DOI/Link |
|---|---------|-----|---------|-------|----------|
| [17] | Zhang, C. et al. | 2020 | **Learning to Dispatch for Job Shop Scheduling via Deep Reinforcement Learning** | NeurIPS 2020 | arXiv:2010.12367 |
| [18] | Park, J. et al. | 2021 | **Learning to Schedule Job-Shop Problems: Representation and Policy Learning Using Graph Neural Networks** | IJCAI 2021 | 10.24963/ijcai.2021/403 |
| [19] | Waschneck, B. et al. | 2018 | **Deep Reinforcement Learning for Semiconductor Production Scheduling** | MASCOTS 2018 | 10.1109/MASCOTS.2018.00037 |

### 7.2.3. Demand Forecasting

| # | Tác giả | Năm | Tiêu đề | Nguồn | DOI/Link |
|---|---------|-----|---------|-------|----------|
| [20] | Taylor, S.J. & Letham, B. | 2018 | **Forecasting at Scale** | The American Statistician | 10.1080/00031305.2017.1380080 |
| [21] | Makridakis, S. et al. | 2022 | **M5 Accuracy Competition: Results, Findings and Conclusions** | Int. J. Forecasting | 10.1016/j.ijforecast.2021.11.013 |
| [22] | Salinas, D. et al. | 2020 | **DeepAR: Probabilistic Forecasting with Autoregressive Recurrent Networks** | Int. J. Forecasting | 10.1016/j.ijforecast.2019.07.001 |

### 7.2.4. APS và Industry 4.0

| # | Tác giả | Năm | Tiêu đề | Nguồn | DOI/Link |
|---|---------|-----|---------|-------|----------|
| [23] | Moon, Y.B. et al. | 2018 | **Enterprise Systems Integration for Advanced Planning and Scheduling in Smart Factory** | APMS 2018 | 10.1007/978-3-319-99707-0_67 |
| [24] | Lin, J.T. et al. | 2021 | **Cloud-Based Advanced Planning and Scheduling System** | J. Intelligent Manufacturing | 10.1007/s10845-020-01603-3 |
| [25] | Wang, L. et al. | 2021 | **A Survey of AI Approaches for Production Scheduling** | J. Manufacturing Systems | 10.1016/j.jmsy.2021.02.012 |

## 7.3. Tài liệu kỹ thuật và Documentation

### 7.3.1. OR-Tools

| # | Nguồn | Mô tả | Link |
|---|-------|-------|------|
| [26] | Google | OR-Tools Documentation | https://developers.google.com/optimization |
| [27] | Google | CP-SAT Solver Reference | https://developers.google.com/optimization/cp |
| [28] | Google | OR-Tools GitHub Repository | https://github.com/google/or-tools |

### 7.3.2. Frappe & ERPNext

| # | Nguồn | Mô tả | Link |
|---|-------|-------|------|
| [29] | Frappe | Frappe Framework Documentation | https://frappeframework.com/docs |
| [30] | Frappe | ERPNext Documentation | https://docs.erpnext.com |
| [31] | Frappe | ERPNext Manufacturing Module | https://docs.erpnext.com/docs/user/manual/en/manufacturing |
| [32] | Frappe | Frappe GitHub Repository | https://github.com/frappe/frappe |

### 7.3.3. Machine Learning Libraries

| # | Nguồn | Mô tả | Link |
|---|-------|-------|------|
| [33] | Facebook | Prophet Documentation | https://facebook.github.io/prophet |
| [34] | Statsmodels | ARIMA Documentation | https://www.statsmodels.org |
| [35] | OpenAI | OpenAI API Documentation | https://platform.openai.com/docs |
| [36] | Stable-Baselines3 | RL Algorithms Documentation | https://stable-baselines3.readthedocs.io |

## 7.4. Tiêu chuẩn và Báo cáo

| # | Tổ chức | Năm | Tiêu đề | Loại |
|---|---------|-----|---------|------|
| [37] | APICS | 2022 | Supply Chain Operations Reference (SCOR) Model | Standard |
| [38] | ISA | 2018 | ISA-95 Enterprise-Control System Integration | Standard |
| [39] | Gartner | 2023 | Magic Quadrant for Manufacturing Execution Systems | Report |
| [40] | McKinsey | 2022 | The Future of Manufacturing | Report |

## 7.5. Tài liệu Việt Nam

| # | Tác giả/Tổ chức | Năm | Tiêu đề | Nguồn |
|---|-----------------|-----|---------|-------|
| [41] | VCCI | 2023 | Khảo sát doanh nghiệp sản xuất SME | Report |
| [42] | Tổng cục Thống kê | 2023 | Niên giám Thống kê Việt Nam | Statistics |
| [43] | Bộ Công Thương | 2022 | Chiến lược phát triển công nghiệp 4.0 | Policy |

---

# PHỤ LỤC: BẢNG TÓM TẮT CÁC NỘI DUNG BỔ SUNG

| STT | Nội dung | Trang | Ghi chú |
|-----|----------|-------|---------|
| 1 | Khảo sát công trình nghiên cứu liên quan | 1-15 | 25+ công trình, phân tích gap |
| 2 | Tính cấp thiết và tầm quan trọng | 16-22 | Số liệu thị trường, thống kê |
| 3 | Lý do chọn đề tài | 23-26 | 6 lý do chính |
| 4 | Mô tả chi tiết ràng buộc | 27-42 | 6 constraints với công thức |
| 5 | Tiêu chí đánh giá tối ưu | 43-52 | Metrics, formulas, thresholds |
| 6 | Chức năng Gantt với deadline | 53-64 | API, UI, export |
| 7 | Tài liệu tham khảo | 65-70 | 43+ references |

---

**--- HẾT FILE BỔ SUNG ---**

*Ngày tạo: 2025-01-14*
*Phiên bản: 1.0*
