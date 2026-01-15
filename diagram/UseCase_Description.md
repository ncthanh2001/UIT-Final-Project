# 3.3.2. Mo Ta Use Case Chi Tiet - UIT APS Module

## UC-01: Run Demand Forecast

| Thanh phan | Mo ta |
|------------|-------|
| **UC ID** | UC-01 |
| **Ten UC** | Run Demand Forecast |
| **Actor** | Production Manager, Production Planner |
| **Muc dich** | Du bao nhu cau san xuat dua tren du lieu lich su ban hang |
| **Priority** | High |
| **Frequency** | Hang thang hoac khi can lap ke hoach moi |
| **Precondition** | - Co du lieu Sales Order lich su >= 30 ngay<br>- User da dang nhap vao he thong<br>- Co quyen truy cap module Forecasting |
| **Postcondition** | - Tao Forecast History record moi<br>- Tao Forecast Results voi du bao theo thoi gian<br>- Luu confidence scores va recommendations |
| **Main Flow** | 1. Actor truy cap menu Forecasting<br>2. Actor chon tham so: Company, Forecast Model (Prophet/ARIMA/Holt-Winters), Horizon (so ngay du bao)<br>3. Actor nhan nut "Run Forecast"<br>4. System thu thap du lieu Sales Order lich su<br>5. System tien xu ly va lam sach du lieu<br>6. System chay mo hinh du bao da chon<br>7. System tinh toan confidence scores<br>8. System tao Forecast Results voi predictions<br>9. System hien thi bieu do du bao va recommendations<br>10. Actor xem ket qua va export neu can |
| **Alternative Flow** | 3a. Neu data khong du 30 ngay:<br>&nbsp;&nbsp;&nbsp;&nbsp;- System hien thi warning<br>&nbsp;&nbsp;&nbsp;&nbsp;- Cho phep tiep tuc voi canh bao do chinh xac thap<br>6a. Neu model chinh fail:<br>&nbsp;&nbsp;&nbsp;&nbsp;- System tu dong fallback sang Simple Moving Average<br>&nbsp;&nbsp;&nbsp;&nbsp;- Thong bao cho user ve viec su dung model don gian hon |
| **Exception** | - Khong co du lieu lich su -> Hien thi error message "Khong co du lieu de du bao"<br>- Loi ket noi database -> Hien thi error va ghi log |

---

## UC-02: Create Production Plan

| Thanh phan | Mo ta |
|------------|-------|
| **UC ID** | UC-02 |
| **Ten UC** | Create Production Plan |
| **Actor** | Production Manager |
| **Muc dich** | Tao ke hoach san xuat dua tren du bao nhu cau hoac don hang |
| **Priority** | High |
| **Frequency** | Hang tuan hoac khi co don hang moi |
| **Precondition** | - Co Forecast Results hoac Sales Orders can san xuat<br>- Co danh sach Item (san pham) trong he thong<br>- User co quyen tao Production Plan |
| **Postcondition** | - Tao Production Plan moi voi status "Draft"<br>- Tao cac Production Plan Items tuong ung<br>- San sang de chuyen sang MRP hoac Scheduling |
| **Main Flow** | 1. Actor truy cap menu Production Planning<br>2. Actor nhan "Create New Plan"<br>3. Actor nhap thong tin: Plan Name, Company, Planned Start/End Date<br>4. Actor chon nguon du lieu: tu Forecast hoac Manual Input<br>5. System load danh sach Items can san xuat<br>6. Actor dieu chinh so luong neu can<br>7. Actor nhan "Save" de luu Plan<br>8. System tao Production Plan voi status "Draft"<br>9. System tao Production Plan Items<br>10. Actor co the Submit de chuyen status sang "Planned" |
| **Alternative Flow** | 4a. Neu chon tu Forecast:<br>&nbsp;&nbsp;&nbsp;&nbsp;- System load Forecast Results gan nhat<br>&nbsp;&nbsp;&nbsp;&nbsp;- Tu dong dien so luong du bao<br>4b. Neu chon Manual:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Actor nhap truc tiep so luong cho tung Item<br>7a. Neu co loi validation:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Hien thi danh sach loi<br>&nbsp;&nbsp;&nbsp;&nbsp;- Cho phep sua truoc khi luu |
| **Exception** | - Khong co Item nao trong he thong -> Error "Vui long tao Item truoc"<br>- Ngay ket thuc < Ngay bat dau -> Validation error |

---

## UC-03: Run MRP Calculation

| Thanh phan | Mo ta |
|------------|-------|
| **UC ID** | UC-03 |
| **Ten UC** | Run MRP Calculation |
| **Actor** | Production Planner |
| **Muc dich** | Tinh toan nhu cau nguyen vat lieu (Material Requirements Planning) |
| **Priority** | High |
| **Frequency** | Sau khi tao Production Plan hoac khi ton kho thay doi |
| **Precondition** | - Co Production Plan voi status "Planned" hoac "Released"<br>- Co BOM (Bill of Materials) cho cac Item<br>- Co du lieu ton kho hien tai |
| **Postcondition** | - Tao MRP Run record<br>- Tao danh sach Material Requirements<br>- Tao Purchase Suggestions neu thieu nguyen lieu |
| **Main Flow** | 1. Actor truy cap menu MRP<br>2. Actor chon Production Plan can tinh MRP<br>3. Actor cau hinh tham so: Include Safety Stock, Lead Time consideration<br>4. Actor nhan "Run MRP"<br>5. System load Production Plan Items<br>6. System explode BOM cho tung Item (tinh nguyen lieu can)<br>7. System kiem tra ton kho hien tai<br>8. System tinh Net Requirements = Gross - On Hand - On Order<br>9. System tao Material Requirements list<br>10. System tao Purchase Suggestions cho nguyen lieu thieu<br>11. System hien thi ket qua MRP |
| **Alternative Flow** | 6a. Neu Item khong co BOM:<br>&nbsp;&nbsp;&nbsp;&nbsp;- System bo qua Item do<br>&nbsp;&nbsp;&nbsp;&nbsp;- Ghi warning vao log<br>8a. Neu Net Requirement <= 0:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Khong tao Purchase Suggestion cho nguyen lieu do |
| **Exception** | - Khong co BOM nao -> Error "Vui long tao BOM truoc khi chay MRP"<br>- Loi tinh toan -> Rollback va hien thi error |

---

## UC-04: Run Production Schedule

| Thanh phan | Mo ta |
|------------|-------|
| **UC ID** | UC-04 |
| **Ten UC** | Run Production Schedule |
| **Actor** | Production Planner |
| **Muc dich** | Lap lich san xuat toi uu cho cac Work Orders |
| **Priority** | High |
| **Frequency** | Hang ngay hoac khi co Work Orders moi |
| **Precondition** | - Co Production Plan voi status "Planned" hoac "Released"<br>- Co Work Orders va Job Cards tuong ung<br>- Co thong tin Workstations va Work Shifts |
| **Postcondition** | - Tao Scheduling Run record moi<br>- Tao Scheduling Results voi lich chi tiet<br>- Job Cards duoc cap nhat thoi gian bat dau/ket thuc |
| **Main Flow** | 1. Actor truy cap menu Scheduling<br>2. Actor chon Production Plan can lap lich<br>3. Actor cau hinh Solver Settings:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Strategy: Minimize Makespan / Minimize Tardiness / Balance<br>&nbsp;&nbsp;&nbsp;&nbsp;- Solver Tier: Quick (30s) / Standard (120s) / Deep (300s)<br>&nbsp;&nbsp;&nbsp;&nbsp;- Time Limit (seconds)<br>4. Actor nhan "Run Schedule"<br>5. System load Work Orders va Job Cards<br>6. System load Workstations va Work Shifts<br>7. System build Constraint Model:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Precedence constraints (thu tu operations)<br>&nbsp;&nbsp;&nbsp;&nbsp;- No-overlap constraints (may khong lam 2 job cung luc)<br>&nbsp;&nbsp;&nbsp;&nbsp;- Machine eligibility (job chi chay tren may phu hop)<br>&nbsp;&nbsp;&nbsp;&nbsp;- Due date constraints<br>&nbsp;&nbsp;&nbsp;&nbsp;- Setup time constraints<br>8. System chay OR-Tools CP-SAT Solver<br>9. System tao Scheduling Results<br>10. System tinh baseline FIFO de so sanh<br>11. System hien thi Gantt chart va metrics (Makespan, Tardiness, Utilization) |
| **Alternative Flow** | 8a. Neu Solver timeout:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Return best solution found so far<br>&nbsp;&nbsp;&nbsp;&nbsp;- Danh dau status "Sub-optimal"<br>8b. Neu bai toan Infeasible:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Hien thi nguyen nhan (constraint nao conflict)<br>&nbsp;&nbsp;&nbsp;&nbsp;- Goi y cach relax constraints |
| **Exception** | - Khong co Job Cards -> Error "Khong co cong viec de lap lich"<br>- Khong co Workstation -> Error "Vui long cau hinh Workstation" |

---

## UC-05: View Gantt Chart

| Thanh phan | Mo ta |
|------------|-------|
| **UC ID** | UC-05 |
| **Ten UC** | View Gantt Chart |
| **Actor** | Production Planner, Production Manager |
| **Muc dich** | Xem truc quan lich san xuat duoi dang bieu do Gantt |
| **Priority** | Medium |
| **Frequency** | Hang ngay, nhieu lan trong ngay |
| **Precondition** | - Co Scheduling Results da duoc tao<br>- User co quyen xem Scheduling |
| **Postcondition** | - Hien thi Gantt chart tuong tac<br>- Khong thay doi du lieu |
| **Main Flow** | 1. Actor truy cap menu Scheduling Results<br>2. Actor chon Scheduling Run can xem<br>3. System load Scheduling Results<br>4. System render Gantt chart:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Truc Y: Danh sach Workstations<br>&nbsp;&nbsp;&nbsp;&nbsp;- Truc X: Timeline (ngay/gio)<br>&nbsp;&nbsp;&nbsp;&nbsp;- Bars: Job Cards voi mau theo Work Order<br>5. Actor co the tuong tac:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Zoom in/out timeline<br>&nbsp;&nbsp;&nbsp;&nbsp;- Hover de xem chi tiet Job<br>&nbsp;&nbsp;&nbsp;&nbsp;- Filter theo Workstation/Work Order<br>6. Actor co the export Gantt chart |
| **Alternative Flow** | 5a. Neu chon che do "Compare":<br>&nbsp;&nbsp;&nbsp;&nbsp;- Hien thi 2 Gantt charts song song<br>&nbsp;&nbsp;&nbsp;&nbsp;- So sanh OR-Tools vs FIFO baseline |
| **Exception** | - Khong co Scheduling Results -> Hien thi message "Chua co lich san xuat" |

---

## UC-06: Approve Schedule

| Thanh phan | Mo ta |
|------------|-------|
| **UC ID** | UC-06 |
| **Ten UC** | Approve Schedule |
| **Actor** | Production Manager |
| **Muc dich** | Phe duyet lich san xuat de ap dung vao san xuat thuc te |
| **Priority** | High |
| **Frequency** | Sau moi lan lap lich thanh cong |
| **Precondition** | - Co Scheduling Results voi status "Completed"<br>- User co quyen Approve (Production Manager) |
| **Postcondition** | - Scheduling Run chuyen status sang "Approved"<br>- Job Cards duoc cap nhat thoi gian chinh thuc<br>- Thong bao gui den Shop Floor |
| **Main Flow** | 1. Actor truy cap Scheduling Results<br>2. Actor xem xet lich san xuat (Gantt chart, metrics)<br>3. Actor kiem tra cac chi so:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Makespan co chap nhan duoc khong<br>&nbsp;&nbsp;&nbsp;&nbsp;- Tardiness co trong gioi han khong<br>&nbsp;&nbsp;&nbsp;&nbsp;- Utilization co hop ly khong<br>4. Actor nhan "Approve Schedule"<br>5. System yeu cau xac nhan<br>6. Actor xac nhan phe duyet<br>7. System cap nhat Scheduling Run status = "Approved"<br>8. System cap nhat Job Cards voi thoi gian chinh thuc<br>9. System gui thong bao den Shop Floor Users<br>10. System ghi Audit Log |
| **Alternative Flow** | 4a. Neu Actor khong hai long:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Actor nhan "Reject"<br>&nbsp;&nbsp;&nbsp;&nbsp;- Nhap ly do reject<br>&nbsp;&nbsp;&nbsp;&nbsp;- Status chuyen sang "Rejected"<br>&nbsp;&nbsp;&nbsp;&nbsp;- Planner can chay lai voi tham so khac |
| **Exception** | - Scheduling Run da duoc approve truoc do -> Error "Lich nay da duoc phe duyet" |

---

## UC-07: Analyze with AI

| Thanh phan | Mo ta |
|------------|-------|
| **UC ID** | UC-07 |
| **Ten UC** | Analyze with AI |
| **Actor** | Production Planner, Production Manager |
| **Muc dich** | Su dung AI (ChatGPT) de phan tich va dua ra khuyen nghi ve lich san xuat |
| **Priority** | Medium |
| **Frequency** | Khi can phan tich sau hoac gap van de |
| **Precondition** | - Co Scheduling Results da hoan thanh<br>- API Key cua OpenAI da duoc cau hinh<br>- User co quyen su dung AI Analysis |
| **Postcondition** | - Tao AI Analysis record<br>- Luu recommendations va insights |
| **Main Flow** | 1. Actor truy cap Scheduling Results<br>2. Actor nhan "Analyze with AI"<br>3. System thu thap context:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Scheduling metrics (Makespan, Tardiness, Utilization)<br>&nbsp;&nbsp;&nbsp;&nbsp;- Job distribution across machines<br>&nbsp;&nbsp;&nbsp;&nbsp;- Bottleneck identification<br>4. System build prompt voi context<br>5. System goi OpenAI ChatGPT API<br>6. System nhan response tu AI<br>7. System parse va format response<br>8. System hien thi AI recommendations:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Danh gia tong quan<br>&nbsp;&nbsp;&nbsp;&nbsp;- Cac van de phat hien<br>&nbsp;&nbsp;&nbsp;&nbsp;- Goi y cai thien<br>9. System luu AI Analysis vao database |
| **Alternative Flow** | 5a. Neu API call fail:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Retry toi da 3 lan<br>&nbsp;&nbsp;&nbsp;&nbsp;- Neu van fail, hien thi error<br>6a. Neu response qua dai:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Truncate va hien thi phan quan trong nhat |
| **Exception** | - API Key khong hop le -> Error "Vui long cau hinh API Key"<br>- Rate limit exceeded -> Error "Vui long thu lai sau" |

---

## UC-08: Configure API Settings

| Thanh phan | Mo ta |
|------------|-------|
| **UC ID** | UC-08 |
| **Ten UC** | Configure API Settings |
| **Actor** | System Admin |
| **Muc dich** | Cau hinh API keys va settings cho cac dich vu ben ngoai |
| **Priority** | Low |
| **Frequency** | Mot lan khi setup, hoac khi can thay doi |
| **Precondition** | - User co quyen System Admin<br>- Co API keys tu cac dich vu (OpenAI, etc.) |
| **Postcondition** | - API Settings duoc luu vao database<br>- Cac module co the su dung API |
| **Main Flow** | 1. Actor truy cap menu Settings > API Configuration<br>2. System hien thi form cau hinh:<br>&nbsp;&nbsp;&nbsp;&nbsp;- OpenAI API Key<br>&nbsp;&nbsp;&nbsp;&nbsp;- OpenAI Model (gpt-3.5-turbo / gpt-4)<br>&nbsp;&nbsp;&nbsp;&nbsp;- Max Tokens<br>&nbsp;&nbsp;&nbsp;&nbsp;- Temperature<br>3. Actor nhap/cap nhat cac gia tri<br>4. Actor nhan "Test Connection" de kiem tra<br>5. System goi API de verify<br>6. System hien thi ket qua test<br>7. Actor nhan "Save" de luu<br>8. System ma hoa va luu API keys<br>9. System hien thi thong bao thanh cong |
| **Alternative Flow** | 4a. Neu test that bai:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Hien thi error message cu the<br>&nbsp;&nbsp;&nbsp;&nbsp;- Cho phep sua va test lai |
| **Exception** | - API Key trong -> Validation error<br>- Khong co quyen Admin -> Access denied |

---

## UC-09: Manage Work Shifts

| Thanh phan | Mo ta |
|------------|-------|
| **UC ID** | UC-09 |
| **Ten UC** | Manage Work Shifts |
| **Actor** | System Admin |
| **Muc dich** | Quan ly ca lam viec cho cac Workstations |
| **Priority** | Medium |
| **Frequency** | Khi setup ban dau hoac thay doi chinh sach |
| **Precondition** | - User co quyen System Admin<br>- Co Workstations da duoc tao |
| **Postcondition** | - Work Shifts duoc tao/cap nhat<br>- Scheduling se su dung thong tin ca lam viec |
| **Main Flow** | 1. Actor truy cap menu Settings > Work Shifts<br>2. System hien thi danh sach Work Shifts hien tai<br>3. Actor chon "Add New Shift" hoac edit shift co<br>4. Actor nhap thong tin:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Shift Name (e.g., "Ca sang", "Ca chieu")<br>&nbsp;&nbsp;&nbsp;&nbsp;- Start Time, End Time<br>&nbsp;&nbsp;&nbsp;&nbsp;- Applicable Days (T2-T6, T2-T7, etc.)<br>&nbsp;&nbsp;&nbsp;&nbsp;- Workstations ap dung<br>5. Actor nhan "Save"<br>6. System validate du lieu<br>7. System luu Work Shift<br>8. System hien thi danh sach cap nhat |
| **Alternative Flow** | 3a. Neu chon Delete:<br>&nbsp;&nbsp;&nbsp;&nbsp;- System kiem tra shift co dang duoc su dung<br>&nbsp;&nbsp;&nbsp;&nbsp;- Neu co, hien thi warning<br>&nbsp;&nbsp;&nbsp;&nbsp;- Yeu cau xac nhan truoc khi xoa |
| **Exception** | - Thoi gian End < Start -> Validation error<br>- Shift trung lap -> Warning va yeu cau xac nhan |

---

## UC-10: View Job Schedule

| Thanh phan | Mo ta |
|------------|-------|
| **UC ID** | UC-10 |
| **Ten UC** | View Job Schedule |
| **Actor** | Shop Floor User |
| **Muc dich** | Xem lich cong viec duoc phan cong cho tung Workstation |
| **Priority** | High |
| **Frequency** | Hang ngay, nhieu lan trong ngay |
| **Precondition** | - Co Scheduling Results da duoc Approved<br>- User duoc gan voi Workstation cu the |
| **Postcondition** | - Hien thi danh sach Jobs can lam<br>- Khong thay doi du lieu |
| **Main Flow** | 1. Actor dang nhap vao he thong<br>2. System tu dong xac dinh Workstation cua Actor<br>3. System load Jobs duoc phan cong cho Workstation<br>4. System hien thi danh sach Jobs:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Job Card ID<br>&nbsp;&nbsp;&nbsp;&nbsp;- Work Order reference<br>&nbsp;&nbsp;&nbsp;&nbsp;- Item (san pham)<br>&nbsp;&nbsp;&nbsp;&nbsp;- Planned Start Time<br>&nbsp;&nbsp;&nbsp;&nbsp;- Planned End Time<br>&nbsp;&nbsp;&nbsp;&nbsp;- Status<br>5. Actor co the loc theo ngay/status<br>6. Actor co the xem chi tiet tung Job<br>7. Actor co the cap nhat trang thai Job (Started/Completed) |
| **Alternative Flow** | 2a. Neu Actor quan ly nhieu Workstations:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Hien thi dropdown chon Workstation<br>&nbsp;&nbsp;&nbsp;&nbsp;- Load Jobs theo Workstation da chon<br>7a. Khi cap nhat status:<br>&nbsp;&nbsp;&nbsp;&nbsp;- System ghi nhan actual start/end time<br>&nbsp;&nbsp;&nbsp;&nbsp;- Gui notification cho Planner neu tre |
| **Exception** | - Khong co Jobs nao -> Hien thi "Khong co cong viec hom nay"<br>- Workstation chua duoc gan -> Error "Lien he Admin de duoc phan cong" |

---

## Bang Tong Hop Use Cases

| UC ID | Ten Use Case | Actor Chinh | Priority |
|-------|--------------|-------------|----------|
| UC-01 | Run Demand Forecast | Production Manager | High |
| UC-02 | Create Production Plan | Production Manager | High |
| UC-03 | Run MRP Calculation | Production Planner | High |
| UC-04 | Run Production Schedule | Production Planner | High |
| UC-05 | View Gantt Chart | Production Planner | Medium |
| UC-06 | Approve Schedule | Production Manager | High |
| UC-07 | Analyze with AI | Production Planner | Medium |
| UC-08 | Configure API Settings | System Admin | Low |
| UC-09 | Manage Work Shifts | System Admin | Medium |
| UC-10 | View Job Schedule | Shop Floor User | High |

---

## Ma Tran Actor - Use Case

| Use Case | Production Manager | Production Planner | System Admin | Shop Floor User |
|----------|:------------------:|:------------------:|:------------:|:---------------:|
| UC-01 | X | X | | |
| UC-02 | X | | | |
| UC-03 | | X | | |
| UC-04 | | X | | |
| UC-05 | X | X | | |
| UC-06 | X | | | |
| UC-07 | X | X | | |
| UC-08 | | | X | |
| UC-09 | | | X | |
| UC-10 | | | | X |

**Ghi chu:**
- X = Actor co the thuc hien Use Case nay
- Production Manager: Chiu trach nhiem tong the, phe duyet
- Production Planner: Thuc hien cac nghiep vu lap ke hoach va lap lich
- System Admin: Quan tri he thong, cau hinh
- Shop Floor User: Xem va cap nhat trang thai cong viec
