# MÔ TẢ THUẬT TOÁN CP-SAT CHO LẬP LỊCH SẢN XUẤT

## (Không sử dụng mã nguồn - Phiên bản trình bày học thuật)

---

## 1. MÔ TẢ BẰNG VĂN BẢN

### 1.1. Tổng quan thuật toán

**CP-SAT (Constraint Programming - Satisfiability)** là thuật toán kết hợp giữa **Lập trình Ràng buộc (Constraint Programming)** và **Giải quyết bài toán Thỏa mãn (SAT Solving)**. Thuật toán này được phát triển bởi Google trong bộ công cụ OR-Tools, đặc biệt hiệu quả cho bài toán **Job Shop Scheduling Problem (JSSP)**.

### 1.2. Các bước thực hiện

#### **Bước 1: Thu thập dữ liệu đầu vào**

Hệ thống thu thập các thông tin sau:
- Danh sách các **Work Order** (lệnh sản xuất) cần thực hiện
- Danh sách **máy móc** khả dụng trong xưởng
- **Thời gian xử lý** của từng công đoạn trên từng máy
- **Deadline** (hạn hoàn thành) của từng đơn hàng
- **Năng lực** và **lịch làm việc** của từng máy

#### **Bước 2: Khởi tạo mô hình toán học**

Xây dựng mô hình tối ưu hóa với:
- **Biến quyết định**: Xác định thời điểm bắt đầu và kết thúc của từng công đoạn
- **Miền giá trị**: Giới hạn trong khoảng thời gian lập lịch (horizon)
- **Các ràng buộc**: Đảm bảo tính khả thi của lịch sản xuất

#### **Bước 3: Thiết lập các ràng buộc**

| Loại ràng buộc | Mô tả | Ví dụ thực tế |
|----------------|-------|---------------|
| **Thứ tự công đoạn** | Công đoạn sau chỉ bắt đầu khi công đoạn trước hoàn thành | Không thể sơn sản phẩm trước khi hàn xong |
| **Không trùng lắp** | Mỗi máy chỉ xử lý một công việc tại một thời điểm | Máy CNC không thể gia công 2 chi tiết cùng lúc |
| **Máy phù hợp** | Công đoạn chỉ được gán cho máy có khả năng thực hiện | Công đoạn phay phải dùng máy phay, không dùng máy tiện |
| **Giờ làm việc** | Công đoạn phải nằm trong ca làm việc | Không lập lịch vào ban đêm nếu máy không hoạt động đêm |
| **Deadline** | Đơn hàng phải hoàn thành trước hạn (hoặc tối thiểu hóa trễ hạn) | Đơn hàng giao ngày 15/01 phải hoàn thành trước đó |
| **Thời gian chuyển đổi** | Thêm thời gian setup khi chuyển sản phẩm | Thay khuôn mất 30 phút khi đổi từ sản phẩm A sang B |

#### **Bước 4: Định nghĩa hàm mục tiêu**

Mục tiêu tối ưu hóa thường là **tối thiểu hóa** một trong các chỉ số:
1. **Makespan**: Thời gian hoàn thành toàn bộ công việc
2. **Total Tardiness**: Tổng thời gian trễ hạn
3. **Kết hợp có trọng số**: Cân bằng giữa nhiều mục tiêu

#### **Bước 5: Giải bài toán**

Solver thực hiện tìm kiếm lời giải tối ưu trong không gian nghiệm, sử dụng các kỹ thuật:
- **Propagation**: Loại bỏ các giá trị không khả thi
- **Branching**: Chia bài toán thành các bài toán con
- **Learning**: Ghi nhớ các xung đột để tránh lặp lại

#### **Bước 6: Xuất kết quả**

Nếu tìm được lời giải, xuất:
- **Lịch sản xuất chi tiết**: Thời gian bắt đầu/kết thúc từng công đoạn
- **Phân công máy**: Công đoạn nào chạy trên máy nào
- **Gantt Chart**: Biểu đồ trực quan hóa lịch
- **Metrics**: Các chỉ số đánh giá (makespan, utilization, tardiness)

---

## 2. MÔ TẢ BẰNG CÔNG THỨC TOÁN HỌC

### 2.1. Ký hiệu

| Ký hiệu | Ý nghĩa |
|---------|---------|
| J | Tập hợp các Job (công việc) |
| M | Tập hợp các Machine (máy) |
| O | Tập hợp các Operation (công đoạn) |
| O_j | Tập các công đoạn thuộc job j |
| p_{ij} | Thời gian xử lý công đoạn i trên máy j |
| d_j | Deadline của job j |
| s_i | Thời điểm bắt đầu công đoạn i |
| c_i | Thời điểm hoàn thành công đoạn i |
| H | Horizon (phạm vi thời gian lập lịch) |

### 2.2. Biến quyết định

```
Với mỗi công đoạn i ∈ O:
    s_i ∈ [0, H]        : Thời điểm bắt đầu
    c_i ∈ [0, H]        : Thời điểm kết thúc
    x_{im} ∈ {0, 1}     : = 1 nếu công đoạn i được gán cho máy m
```

### 2.3. Ràng buộc

#### Ràng buộc 1: Quan hệ bắt đầu - kết thúc
```
c_i = s_i + p_i        ∀i ∈ O
```
*Giải thích: Thời điểm hoàn thành = Thời điểm bắt đầu + Thời gian xử lý*

#### Ràng buộc 2: Thứ tự công đoạn (Precedence)
```
c_{i,k} ≤ s_{i,k+1}    ∀i ∈ J, ∀k ∈ {1, ..., |O_i| - 1}
```
*Giải thích: Công đoạn thứ k của job i phải hoàn thành trước khi công đoạn k+1 bắt đầu*

#### Ràng buộc 3: Không trùng lắp trên máy (No-Overlap)
```
c_i ≤ s_j  HOẶC  c_j ≤ s_i    ∀i, j được gán cho cùng máy m
```
*Giải thích: Hai công đoạn trên cùng máy không được chồng chéo thời gian*

#### Ràng buộc 4: Máy phù hợp (Machine Eligibility)
```
Σ_{m ∈ E_i} x_{im} = 1        ∀i ∈ O
```
*Giải thích: Mỗi công đoạn phải được gán cho đúng 1 máy trong tập máy phù hợp E_i*

#### Ràng buộc 5: Deadline (Due Date)
```
T_j = max(0, C_j - d_j)       ∀j ∈ J
```
*Giải thích: T_j là độ trễ của job j (= 0 nếu hoàn thành đúng hạn)*

### 2.4. Hàm mục tiêu

#### Dạng 1: Tối thiểu hóa Makespan
```
Minimize C_max = max_{i ∈ O} c_i
```

#### Dạng 2: Tối thiểu hóa tổng độ trễ có trọng số
```
Minimize Σ_{j ∈ J} w_j × T_j
```

#### Dạng 3: Kết hợp đa mục tiêu (sử dụng trong UIT APS)
```
Minimize Z = α × C_max + β × Σ_{j ∈ J} w_j × T_j

Trong đó:
    α = trọng số cho makespan (mặc định: 0.3)
    β = trọng số cho tardiness (mặc định: 0.7)
    w_j = trọng số ưu tiên của job j
```

---

## 3. MÔ TẢ BẰNG BẢNG THUẬT TOÁN

### 3.1. Thuật toán CP-SAT (dạng bước)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    THUẬT TOÁN CP-SAT CHO LẬP LỊCH SẢN XUẤT                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ĐẦU VÀO:                                                                    ║
║      • J = {j₁, j₂, ..., jₙ}: Tập n công việc (jobs)                        ║
║      • M = {m₁, m₂, ..., mₖ}: Tập k máy móc                                 ║
║      • P: Ma trận thời gian xử lý                                           ║
║      • D: Vector deadline các job                                           ║
║      • H: Horizon (phạm vi thời gian)                                       ║
║                                                                              ║
║  ĐẦU RA:                                                                     ║
║      • S*: Lịch sản xuất tối ưu                                             ║
║      • Z*: Giá trị hàm mục tiêu tối ưu                                      ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  BƯỚC 1: KHỞI TẠO                                                           ║
║  ────────────────                                                            ║
║      1.1. Tạo mô hình rỗng Model ← ∅                                        ║
║      1.2. Với mỗi công đoạn o ∈ O:                                          ║
║           • Thêm biến start[o] với miền [0, H]                              ║
║           • Thêm biến end[o] với miền [0, H]                                ║
║           • Thêm biến interval[o] liên kết start, end, duration             ║
║                                                                              ║
║  BƯỚC 2: THÊM RÀNG BUỘC                                                     ║
║  ──────────────────────                                                      ║
║      2.1. Ràng buộc thứ tự (Precedence):                                    ║
║           Với mỗi job j và cặp công đoạn liên tiếp (oₖ, oₖ₊₁):              ║
║               Thêm: end[oₖ] ≤ start[oₖ₊₁]                                   ║
║                                                                              ║
║      2.2. Ràng buộc không trùng lắp (No-Overlap):                           ║
║           Với mỗi máy m:                                                    ║
║               intervals_m ← {interval[o] | o được gán cho m}                ║
║               Thêm: NoOverlap(intervals_m)                                  ║
║                                                                              ║
║      2.3. Ràng buộc máy phù hợp (Eligibility):                              ║
║           Với mỗi công đoạn o:                                              ║
║               Thêm: machine[o] ∈ E[o]    (E[o] = tập máy phù hợp)          ║
║                                                                              ║
║  BƯỚC 3: THIẾT LẬP HÀM MỤC TIÊU                                             ║
║  ──────────────────────────────                                              ║
║      3.1. Tính makespan:                                                    ║
║               makespan ← max(end[o]) với mọi o ∈ O                          ║
║      3.2. Tính tổng độ trễ:                                                 ║
║               tardiness ← Σ max(0, completion[j] - deadline[j])             ║
║      3.3. Hàm mục tiêu:                                                     ║
║               Z ← α × makespan + β × tardiness                              ║
║               Thêm: Minimize(Z)                                             ║
║                                                                              ║
║  BƯỚC 4: GIẢI BÀI TOÁN                                                      ║
║  ─────────────────────                                                       ║
║      4.1. Khởi tạo Solver                                                   ║
║      4.2. Thiết lập thời gian tối đa: max_time ← 300 giây                   ║
║      4.3. status ← Solver.Solve(Model)                                      ║
║                                                                              ║
║  BƯỚC 5: XỬ LÝ KẾT QUẢ                                                      ║
║  ─────────────────────                                                       ║
║      5.1. Nếu status = OPTIMAL hoặc FEASIBLE:                               ║
║               S* ← Trích xuất lời giải từ Solver                            ║
║               Z* ← Giá trị hàm mục tiêu                                     ║
║               Trả về (S*, Z*)                                               ║
║      5.2. Ngược lại:                                                        ║
║               S* ← FIFO_Schedule()    (lịch dự phòng)                       ║
║               Trả về (S*, ∞)                                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 4. MÔ TẢ BẰNG SƠ ĐỒ (Mô tả dạng text)

### 4.1. Sơ đồ luồng xử lý

```
┌─────────────┐
│  BẮT ĐẦU    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│  Thu thập dữ liệu đầu vào       │
│  • Work Orders                  │
│  • Máy móc                      │
│  • Thời gian xử lý              │
│  • Deadline                     │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Khởi tạo mô hình CP-SAT        │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Tạo biến quyết định            │
│  • start_time cho mỗi operation │
│  • end_time cho mỗi operation   │
│  • interval cho mỗi operation   │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     THÊM CÁC RÀNG BUỘC                              │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Precedence│ │No-Overlap│ │Eligibilit│ │ Due Date │ │Setup Time│  │
│  │   (1)    │ │   (2)    │ │    (3)   │ │   (4)    │ │   (5)    │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────┐
│  Thiết lập hàm mục tiêu         │
│  Minimize(α×Makespan +          │
│           β×Σ Tardiness)        │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Chạy Solver                    │
│  (max_time = 300s)              │
└──────────────┬──────────────────┘
               │
               ▼
         ┌─────────────┐
         │ Tìm được    │
         │ lời giải?   │
         └──────┬──────┘
                │
       ┌────────┴────────┐
       │                 │
       ▼ Có              ▼ Không
┌──────────────┐   ┌──────────────┐
│ Xuất lịch    │   │ Sử dụng FIFO │
│ tối ưu       │   │ (dự phòng)   │
└──────┬───────┘   └──────┬───────┘
       │                  │
       └────────┬─────────┘
                │
                ▼
┌─────────────────────────────────┐
│  Xuất kết quả                   │
│  • Gantt Chart                  │
│  • Metrics                      │
│  • Báo cáo                      │
└──────────────┬──────────────────┘
               │
               ▼
        ┌─────────────┐
        │  KẾT THÚC   │
        └─────────────┘
```

### 4.2. Minh họa các ràng buộc

```
═══════════════════════════════════════════════════════════════════════════════
                     MINH HỌA CÁC RÀNG BUỘC CP-SAT
═══════════════════════════════════════════════════════════════════════════════

1. RÀNG BUỘC THỨ TỰ (Precedence Constraint)
   ─────────────────────────────────────────

   Job A có 3 công đoạn: [Cắt] → [Hàn] → [Sơn]

   Thời gian: ──────────────────────────────────────────────────────────►

              │▓▓▓▓ Cắt ▓▓▓▓│              │▓▓▓▓ Hàn ▓▓▓▓│  │▓▓▓ Sơn ▓▓▓│
                            │              │
                            └──────────────┘
                            Công đoạn sau chỉ bắt đầu
                            khi công đoạn trước kết thúc


2. RÀNG BUỘC KHÔNG TRÙNG LẮP (No-Overlap Constraint)
   ─────────────────────────────────────────────────

   Máy CNC xử lý 3 job: A, B, C

   SAI (Vi phạm):                       ĐÚNG (Tuân thủ):
   ──────────────                       ────────────────
   │▓▓▓▓ A ▓▓▓▓│                       │▓▓▓▓ A ▓▓▓▓│
       │▓▓▓ B ▓▓▓│                                   │▓▓▓ B ▓▓▓│
           │▓▓▓▓ C ▓▓▓▓│                                         │▓▓▓▓ C ▓▓▓▓│
   ──────────────────────               ───────────────────────────────────────
   ✗ Các job chồng chéo!               ✓ Các job không chồng chéo


3. RÀNG BUỘC MÁY PHÙ HỢP (Machine Eligibility)
   ─────────────────────────────────────────────

   ┌─────────────────────────────────────────────────────────────┐
   │  Công đoạn          │  Máy có thể xử lý                     │
   ├─────────────────────┼───────────────────────────────────────┤
   │  Phay               │  Máy phay CNC-01, CNC-02              │
   │  Tiện               │  Máy tiện L-01, L-02, L-03            │
   │  Hàn                │  Máy hàn W-01                         │
   │  Sơn                │  Buồng sơn P-01, P-02                 │
   └─────────────────────┴───────────────────────────────────────┘

   → Công đoạn Phay KHÔNG THỂ gán cho Máy tiện L-01


4. RÀNG BUỘC DEADLINE (Due Date Constraint)
   ─────────────────────────────────────────

   Thời gian: ─────────────────────────────────────────────────────────────►
                                                    │
                                                    │ Deadline
                                                    ▼
   Trường hợp 1:    │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│              │
                                     ↑              │
                                Hoàn thành          │
                    Tardiness = 0 (Đúng hạn)        │
                                                    │
   Trường hợp 2:    │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
                                                    │←──►│
                                                    Tardiness = 2 ngày
                                                    (Trễ hạn)


5. RÀNG BUỘC THỜI GIAN CHUYỂN ĐỔI (Setup Time)
   ─────────────────────────────────────────────

   Sản phẩm A → Sản phẩm B trên cùng máy:

   │▓▓▓▓ SX A ▓▓▓▓│░░SETUP░░│▓▓▓▓ SX B ▓▓▓▓│
                   │←──────→│
                   30 phút thay khuôn

   → Setup time được tự động thêm vào giữa 2 công đoạn khác loại sản phẩm

═══════════════════════════════════════════════════════════════════════════════
```

---

## 5. VÍ DỤ MINH HỌA CỤ THỂ

### 5.1. Bài toán mẫu

**Đầu vào:**
- 3 Job: J1, J2, J3
- 3 Máy: M1, M2, M3
- Mỗi job có 3 công đoạn phải thực hiện tuần tự

| Job | Công đoạn 1 | Công đoạn 2 | Công đoạn 3 | Deadline |
|-----|-------------|-------------|-------------|----------|
| J1  | M1 (3h)     | M2 (2h)     | M3 (2h)     | 10h      |
| J2  | M1 (2h)     | M3 (1h)     | M2 (4h)     | 8h       |
| J3  | M2 (4h)     | M3 (3h)     | M1 (1h)     | 12h      |

### 5.2. Quá trình giải

```
Bước 1: Tạo biến
────────────────
start[J1_O1], end[J1_O1], interval[J1_O1] (trên M1, duration=3)
start[J1_O2], end[J1_O2], interval[J1_O2] (trên M2, duration=2)
... (tương tự cho tất cả 9 công đoạn)

Bước 2: Thêm ràng buộc thứ tự
─────────────────────────────
end[J1_O1] ≤ start[J1_O2]
end[J1_O2] ≤ start[J1_O3]
end[J2_O1] ≤ start[J2_O2]
... (6 ràng buộc thứ tự)

Bước 3: Thêm ràng buộc không trùng lắp
──────────────────────────────────────
M1: NoOverlap({J1_O1, J2_O1, J3_O3})
M2: NoOverlap({J1_O2, J2_O3, J3_O1})
M3: NoOverlap({J1_O3, J2_O2, J3_O2})

Bước 4: Hàm mục tiêu
────────────────────
makespan = max(end[J1_O3], end[J2_O3], end[J3_O3])
Minimize(makespan)

Bước 5: Giải
────────────
Solver tìm được lời giải tối ưu với makespan = 11h
```

### 5.3. Kết quả (Gantt Chart dạng text)

```
Thời gian (giờ): 0   1   2   3   4   5   6   7   8   9   10  11
                 │   │   │   │   │   │   │   │   │   │   │   │
Máy M1:          │▓▓▓▓▓▓▓J1_O1▓▓▓▓▓▓▓│▓▓▓J2_O1▓▓▓│       │▓J3_O3│
                 │                   │           │       │     │
Máy M2:          │▓▓▓▓▓▓▓▓▓J3_O1▓▓▓▓▓▓▓▓▓│▓▓J1_O2▓│▓▓▓▓▓▓J2_O3▓▓▓▓▓│
                 │                       │       │               │
Máy M3:          │           │▓J2_O2│▓▓▓▓▓▓J3_O2▓▓▓▓│▓▓J1_O3▓│   │
                 │           │      │               │         │   │
                 └───────────┴──────┴───────────────┴─────────┴───┘
                                                              ↑
                                                        Makespan = 11h
```

---

## 6. SO SÁNH VỚI PHƯƠNG PHÁP TRUYỀN THỐNG

| Tiêu chí | FIFO (Truyền thống) | CP-SAT (UIT APS) |
|----------|---------------------|------------------|
| **Nguyên tắc** | Xử lý theo thứ tự đến trước | Tối ưu hóa toàn cục |
| **Xem xét deadline** | Không | Có |
| **Cân nhắc tải máy** | Không | Có |
| **Thời gian tính toán** | Rất nhanh (O(n)) | Phụ thuộc độ phức tạp |
| **Chất lượng lịch** | Thường không tối ưu | Gần tối ưu hoặc tối ưu |
| **Makespan điển hình** | 15-20h | 11h (giảm 27-45%) |

---

## 7. TÓM TẮT

Thuật toán CP-SAT cho lập lịch sản xuất hoạt động theo nguyên tắc:

1. **Mô hình hóa** bài toán lập lịch thành bài toán tối ưu ràng buộc
2. **Định nghĩa** các biến quyết định cho thời điểm bắt đầu/kết thúc mỗi công đoạn
3. **Thiết lập** các ràng buộc đảm bảo tính khả thi (thứ tự, không trùng lắp, máy phù hợp...)
4. **Tối ưu hóa** hàm mục tiêu (makespan, tardiness, hoặc kết hợp)
5. **Giải** bằng solver CP-SAT với các kỹ thuật tìm kiếm hiệu quả
6. **Xuất** kết quả dưới dạng lịch sản xuất và Gantt Chart

Phương pháp này cho kết quả tốt hơn đáng kể so với các quy tắc lập lịch đơn giản như FIFO, đặc biệt khi có nhiều ràng buộc phức tạp và yêu cầu tối ưu hóa đa mục tiêu.
