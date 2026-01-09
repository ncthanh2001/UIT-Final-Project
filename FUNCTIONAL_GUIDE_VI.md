# UIT APS - Hướng Dẫn Chức Năng & Sử Dụng

## Mục Lục
1. [Giới Thiệu](#giới-thiệu)
2. [Bắt Đầu](#bắt-đầu)
3. [Dự Báo Nhu Cầu](#dự-báo-nhu-cầu)
4. [Lập Kế Hoạch Sản Xuất](#lập-kế-hoạch-sản-xuất)
5. [Tối Ưu Hóa MRP](#tối-ưu-hóa-mrp)
6. [Lập Lịch Sản Xuất](#lập-lịch-sản-xuất)
7. [Các Ví Dụ Quy Trình Hoàn Chỉnh](#các-ví-dụ-quy-trình-hoàn-chỉnh)
8. [Xử Lý Sự Cố](#xử-lý-sự-cố)
9. [Phương Pháp Hay Nhất](#phương-pháp-hay-nhất)

---

## Giới Thiệu

### UIT APS là gì?

UIT APS (Advanced Planning and Scheduling - Lập Kế Hoạch và Lịch Trình Tiên Tiến) là một hệ thống lập kế hoạch sản xuất thông minh giúp bạn:

- **Dự báo nhu cầu** sử dụng các mô hình AI/ML để dự đoán yêu cầu sản phẩm trong tương lai
- **Lập kế hoạch sản xuất** dựa trên dự báo hoặc đơn hàng bán hàng thực tế
- **Tối ưu hóa vật liệu** bằng cách tính toán chính xác yêu cầu vật tư và đề xuất nhà cung cấp tối ưu
- **Lập lịch vận hành** sử dụng các thuật toán tiên tiến giúp giảm thiểu thời gian sản xuất và độ trễ

### Lợi Ích Chính

- **Giảm tình trạng hết hàng**: Dự báo chính xác ngăn ngừa tình trạng thiếu hàng tồn kho
- **Chi phí thấp hơn**: Lựa chọn nhà cung cấp tối ưu và giảm tồn kho thừa
- **Giao hàng nhanh hơn**: Lập lịch thông minh giảm thiểu thời gian sản xuất
- **Quyết định tốt hơn**: Thông tin chi tiết và khuyến nghị được hỗ trợ bởi AI
- **Thích ứng theo thời gian thực**: Lập lịch lại động khi xảy ra gián đoạn

---

## Bắt Đầu

### Yêu Cầu Trước Khi Sử Dụng

Trước khi sử dụng UIT APS, hãy đảm bảo bạn có:

1. **ERPNext v15+** đã được cài đặt và cấu hình
2. **Dữ liệu chính cơ bản** đã được thiết lập:
   - Các mặt hàng với mã và mô tả sản phẩm
   - BOM (Danh Mục Vật Tư) cho các sản phẩm được sản xuất
   - Trạm làm việc với công suất và giờ làm việc
   - Nhà cung cấp với giá cả và thời gian giao hàng
   - Kho hàng để quản lý tồn kho
3. **Dữ liệu lịch sử**:
   - Ít nhất 3-6 tháng lịch sử Đơn Hàng Bán để dự báo chính xác
   - Giá sản phẩm từ nhà cung cấp
   - Hồ sơ sản xuất trong quá khứ (tùy chọn, để lập lịch tốt hơn)

### Thiết Lập Ban Đầu

#### 1. Cấu Hình ChatGPT Settings (Tùy Chọn)

Để có giải thích được hỗ trợ bởi AI, cấu hình tích hợp OpenAI:

1. Vào **UIT APS > APS ChatGPT Settings**
2. Nhập OpenAI API key của bạn
3. Chọn mô hình (khuyến nghị GPT-4 để độ chính xác cao hơn)
4. Cấu hình các tham số:
   - Max tokens: 2000-4000
   - Temperature: 0.7 (cân bằng giữa sáng tạo và nhất quán)
5. Lưu cài đặt

#### 2. Xác Minh Dữ Liệu Chính

Kiểm tra rằng bạn có:
- Các mặt hàng với phân loại phù hợp (nhóm mặt hàng)
- Nhà cung cấp hoạt động cho các mặt hàng mua vào
- BOM cho tất cả các mặt hàng được sản xuất
- Trạm làm việc được cấu hình với các hoạt động

---

## Dự Báo Nhu Cầu

### Tổng Quan

Module dự báo dự đoán nhu cầu tương lai cho các mặt hàng của bạn dựa trên dữ liệu bán hàng lịch sử. Nó sử dụng ba mô hình AI/ML khác nhau và tự động chọn mô hình tốt nhất.

### Cách Thức Dự Báo Hoạt Động

```
Đơn Hàng Bán Lịch Sử → Trích Xuất Dữ Liệu → Huấn Luyện Mô Hình →
Tạo Dự Báo → Chấm Điểm Độ Tin Cậy → Giải Thích AI → Kết Quả
```

#### Quy Trình Từng Bước:

1. **Thu Thập Dữ Liệu**: Hệ thống lấy dữ liệu đơn hàng bán lịch sử
2. **Tiền Xử Lý**: Làm sạch và tổng hợp dữ liệu theo các khoảng thời gian
3. **Huấn Luyện Mô Hình**: Huấn luyện ba mô hình (ARIMA, Linear Regression, Prophet)
4. **Dự Đoán**: Mỗi mô hình tạo ra dự báo với các khoảng tin cậy
5. **Đánh Giá**: Tính toán các chỉ số chính xác (MAPE - Phần Trăm Sai Số Tuyệt Đối Trung Bình)
6. **Giải Thích**: ChatGPT tạo ra những thông tin chi tiết có thể đọc được
7. **Khuyến Nghị**: Hệ thống đề xuất mức đặt hàng lại và tồn kho an toàn

### Ba Mô Hình Dự Báo

#### 1. ARIMA (AutoRegressive Integrated Moving Average)

**Tốt nhất cho**: Các mặt hàng có mô hình theo mùa và xu hướng rõ ràng

**Cách hoạt động**:
- Phân tích các mô hình lịch sử trong dữ liệu bán hàng của bạn
- Tự động phát hiện tính theo mùa (hàng tuần, hàng tháng, hàng năm)
- Sử dụng các giá trị trong quá khứ và lỗi trong quá khứ để dự đoán giá trị tương lai
- Tự động tính toán các tham số tối ưu (p, d, q)

**Ví dụ**:
- Doanh số kem tăng vọt vào mùa hè và giảm vào mùa đông
- Văn phòng phẩm với chu kỳ mua hàng hàng tháng

**Tham Số Mô Hình**:
- `p` (AR order): Có bao nhiêu giá trị quá khứ được xem xét
- `d` (Differencing): Số lần làm sai phân dữ liệu để làm cho nó dừng
- `q` (MA order): Có bao nhiêu lỗi quá khứ được xem xét
- `AIC` (Akaike Information Criterion): Càng thấp càng tốt về chất lượng

#### 2. Linear Regression (Hồi Quy Tuyến Tính)

**Tốt nhất cho**: Các mặt hàng có xu hướng tăng trưởng hoặc giảm tuyến tính ổn định

**Cách hoạt động**:
- Vẽ một đường thẳng qua các điểm dữ liệu lịch sử
- Mở rộng đường thẳng vào tương lai để dự đoán
- Đơn giản và nhanh chóng, hoạt động tốt với các xu hướng nhất quán
- Tính toán điểm R² để đo lường mức độ phù hợp của đường thẳng

**Ví dụ**:
- Sản phẩm mới với tăng trưởng đều đặn
- Sản phẩm đang giảm dần bị loại bỏ dần
- Các mặt hàng hàng hóa với nhu cầu nhất quán

**Chỉ Số Mô Hình**:
- `R² score`: 0-1, cao hơn nghĩa là phù hợp hơn (>0.7 là tốt)
- `Slope`: Dương (tăng trưởng), âm (giảm), hoặc gần bằng không (ổn định)

#### 3. Prophet (Facebook Prophet)

**Tốt nhất cho**: Các mặt hàng có nhiều mô hình theo mùa và sự kiện đặc biệt

**Cách hoạt động**:
- Phân tách chuỗi thời gian thành xu hướng + tính theo mùa + ngày lễ
- Xử lý nhiều mức độ tính theo mùa (hàng ngày, hàng tuần, hàng tháng, hàng năm)
- Tự động phát hiện các điểm thay đổi (khi xu hướng thay đổi)
- Mạnh mẽ với dữ liệu thiếu và ngoại lệ

**Ví dụ**:
- Các mặt hàng bán lẻ bị ảnh hưởng bởi ngày lễ và khuyến mãi
- Sản phẩm có cả tính theo mùa hàng tuần và hàng năm
- Các mặt hàng có thay đổi xu hướng đột ngột

**Chỉ Số Mô Hình**:
- `Seasonality type`: Hàng tuần, Hàng tháng, Hàng năm, hoặc Nhiều loại
- `Changepoint count`: Số lượng thay đổi xu hướng được phát hiện

### Chạy Dự Báo

#### Phương Pháp 1: Qua Giao Diện

1. Vào **UIT APS > APS Forecast History**
2. Nhấp **New**
3. Điền vào biểu mẫu:

**Cài Đặt Cơ Bản**:
- **Company**: Chọn công ty của bạn
- **Model Used**: Chọn một mô hình (hoặc chạy cả ba và so sánh)
  - ARIMA: Cho mô hình theo mùa
  - Linear Regression: Cho xu hướng ổn định
  - Prophet: Cho tính theo mùa phức tạp

**Khoảng Thời Gian**:
- **Forecast Horizon Days**: Bao xa vào tương lai (ví dụ: 90 ngày = 3 tháng)
- **Training Period Days**: Dùng bao nhiêu dữ liệu lịch sử (khuyến nghị: 365+ ngày)

**Bộ Lọc** (tùy chọn - để trống để dự báo tất cả mặt hàng):
- **Warehouse**: Kho cụ thể
- **Item Code**: Một mặt hàng duy nhất
- **Item Group**: Tất cả mặt hàng trong một danh mục

4. Nhấp **Save**
5. Nhấp nút **Run Forecast**
6. Đợi xử lý (có thể mất vài phút cho nhiều mặt hàng)

#### Phương Pháp 2: Qua API

```python
import requests

url = "https://your-site.com/api/method/uit_aps.uit_api.run_model.run_forecast"
headers = {
    "Authorization": "token YOUR_API_KEY:YOUR_API_SECRET",
    "Content-Type": "application/json"
}
data = {
    "model_name": "ARIMA",
    "company": "UIT Company",
    "forecast_horizon_days": 90,
    "training_period_days": 365,
    "item_group": "Raw Materials"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()
print(f"Forecast Run: {result['message']['forecast_history']}")
```

### Hiểu Kết Quả Dự Báo

Sau khi dự báo hoàn thành, nhấp vào bản ghi **Forecast History** để xem kết quả.

#### Chỉ Số Chính trong Forecast History:

- **Overall Accuracy (MAPE)**: Càng thấp càng tốt
  - <10% = Xuất sắc
  - 10-20% = Tốt
  - 20-50% = Chấp nhận được
  - >50% = Kém (cân nhắc thêm dữ liệu hoặc mô hình khác)

- **Average Confidence Score**: 0-100%, càng cao càng tốt
  - >80% = Độ tin cậy cao
  - 60-80% = Độ tin cậy trung bình
  - <60% = Độ tin cậy thấp (cần thận trọng)

- **Successful vs Failed Forecasts**: Bao nhiêu mặt hàng đã được dự báo thành công

#### Bảng Kết Quả Dự Báo:

Mỗi mặt hàng nhận được kết quả dự báo chi tiết với:

**Dữ Liệu Dự Báo**:
- **Forecast Period**: Ngày cho dự đoán này
- **Forecast Qty**: Số lượng dự đoán cần thiết
- **Confidence Score**: Mức độ tin cậy của mô hình (0-100%)
- **Lower Bound**: Tình huống xấu nhất (dùng cho tồn kho an toàn)
- **Upper Bound**: Tình huống tốt nhất

**Phân Loại Biến Động**:
- **Fast Moving**: Tiêu thụ cao, quan trọng để giữ trong kho
- **Slow Moving**: Tiêu thụ thấp, đặt hàng ít thường xuyên hơn
- **Non Moving**: Không có doanh số gần đây, cân nhắc ngừng sản xuất

**Phân Tích Xu Hướng**:
- **Upward**: Nhu cầu đang tăng, lập kế hoạch cho tăng trưởng
- **Downward**: Nhu cầu đang giảm, giảm đơn hàng
- **Stable**: Nhu cầu nhất quán, duy trì mức hiện tại

**Khuyến Nghị Tồn Kho**:
- **Reorder Level**: Khi hàng tồn kho đạt mức này, đặt hàng thêm
- **Suggested Qty**: Số lượng nên đặt
- **Safety Stock**: Tồn kho đệm cho nhu cầu bất ngờ
- **Reorder Alert**: Cờ nếu tồn kho hiện tại dưới mức đặt hàng lại

**AI Explanation** (nếu ChatGPT được cấu hình):
- Giải thích dễ hiểu về dự báo
- Các yếu tố chính ảnh hưởng đến dự đoán
- Khuyến nghị có thể thực hiện

### So Sánh Các Mô Hình

Để tìm mô hình tốt nhất cho một mặt hàng cụ thể:

1. Vào **UIT APS > Compare Forecast Models**
2. Chọn mặt hàng
3. Nhập khoảng thời gian dự báo và huấn luyện
4. Nhấp **Compare**

Hệ thống sẽ:
- Chạy cả ba mô hình trên cùng dữ liệu
- Hiển thị chỉ số chính xác (MAPE) cho mỗi mô hình
- Khuyến nghị mô hình tốt nhất
- Hiển thị dự đoán song song

**Khi nào sử dụng mỗi mô hình**:
- Tính theo mùa cao → **ARIMA** hoặc **Prophet**
- Xu hướng đơn giản → **Linear Regression**
- Mô hình phức tạp + ngày lễ → **Prophet**
- Không chắc chắn → Chạy so sánh và sử dụng mô hình được khuyến nghị

### Mẹo Quy Trình Dự Báo

1. **Bắt đầu với một bài kiểm tra nhỏ**:
   - Dự báo một nhóm mặt hàng trước
   - Xem xét độ chính xác trước khi mở rộng
   - Điều chỉnh khoảng thời gian huấn luyện nếu cần

2. **Kiểm tra chất lượng dữ liệu**:
   - Đảm bảo đơn hàng bán được ghi ngày đúng
   - Làm sạch bất kỳ dữ liệu trùng lặp hoặc kiểm tra nào
   - Cần ít nhất 30-60 điểm dữ liệu cho dự báo đáng tin cậy

3. **Tinh chỉnh theo thời gian**:
   - Chạy lại dự báo hàng tháng hoặc hàng quý
   - Theo dõi thực tế so với dự đoán để đo lường độ chính xác
   - Điều chỉnh mô hình dựa trên hiệu suất

4. **Sử dụng giải thích AI**:
   - Xem xét thông tin chi tiết từ ChatGPT cho bối cảnh kinh doanh
   - Chia sẻ khuyến nghị với đội lập kế hoạch
   - Ghi chép những bài học kinh nghiệm

---

## Lập Kế Hoạch Sản Xuất

### Tổng Quan

Lập kế hoạch sản xuất chuyển đổi kết quả dự báo (hoặc đơn hàng bán) thành các kế hoạch sản xuất cụ thể với số lượng và thời gian.

### Cách Thức Lập Kế Hoạch Sản Xuất Hoạt Động

```
Kết Quả Dự Báo / Đơn Hàng Bán → Tạo Kế Hoạch →
Khai Triển BOM → Kiểm Tra Công Suất → Các Hạng Mục Kế Hoạch Sản Xuất
```

#### Quy Trình Lập Kế Hoạch:

1. **Lựa Chọn Nguồn**: Chọn dự báo hoặc đơn hàng bán làm đầu vào
2. **Tổng Hợp Kỳ**: Nhóm theo tháng hoặc quý
3. **Tra Cứu BOM**: Tìm BOM sản xuất cho mỗi mặt hàng
4. **Tính Toán Số Lượng**: Tổng hợp số lượng được dự báo/đặt hàng
5. **Phân Bổ Thời Gian**: Đặt ngày bắt đầu và kết thúc theo kế hoạch
6. **Xác Minh Công Suất**: Kiểm tra xem trạm làm việc có thể xử lý khối lượng công việc không

### Tạo Kế Hoạch Sản Xuất

#### Từ Kết Quả Dự Báo:

1. Vào **UIT APS > APS Production Plan**
2. Nhấp **New**
3. Điền vào biểu mẫu:

**Thông Tin Cơ Bản**:
- **Plan Name**: Tên mô tả (ví dụ: "Q1 2026 Production")
- **Company**: Công ty của bạn
- **Forecast History**: Chọn một lần chạy dự báo đã hoàn thành

**Kỳ Lập Kế Hoạch**:
- **Plan From Period**: Ngày bắt đầu (ví dụ: 2026-01-01)
- **Plan To Period**: Ngày kết thúc (ví dụ: 2026-03-31)
- **Time Granularity**:
  - **Monthly**: Một hạng mục kế hoạch cho mỗi mặt hàng mỗi tháng
  - **Quarterly**: Một hạng mục kế hoạch cho mỗi mặt hàng mỗi quý

**Nguồn**:
- **Source Type**: Chọn "Forecast"

4. Nhấp **Save**
5. Nhấp nút **Generate Plan**
6. Xem xét các hạng mục kế hoạch được tạo

#### Từ Đơn Hàng Bán:

1. Tạo một **APS Production Plan** mới
2. Đặt **Source Type** thành "Sales Order"
3. Chọn phạm vi ngày để bao gồm các đơn hàng bán
4. Nhấp **Generate Plan**

Hệ thống sẽ lấy các đơn hàng bán thực tế thay vì dự báo.

#### Lập Kế Hoạch Thủ Công:

1. Tạo một **APS Production Plan** mới
2. Đặt **Source Type** thành "Manual"
3. Thêm thủ công các mặt hàng trong bảng **Items**:
   - Item Code
   - Planned Production Qty
   - Planned Period
   - Warehouse

### Hiểu Các Hạng Mục Kế Hoạch Sản Xuất

Mỗi mặt hàng trong kế hoạch có:

**Chi Tiết Mặt Hàng**:
- **Item Code**: Sản xuất cái gì
- **Item Name**: Mô tả mặt hàng
- **BOM**: Danh Mục Vật Tư (tự động lấy hoặc chọn thủ công)

**Số Lượng**:
- **Forecasted Qty**: Từ dự báo (nếu nguồn là dự báo)
- **Planned Production Qty**: Số lượng thực tế cần sản xuất (có thể điều chỉnh)

**Thời Gian**:
- **Planned Period**: Tháng/Quý cho sản xuất này
- **Planned Start Date**: Khi bắt đầu sản xuất
- **Planned End Date**: Ngày hoàn thành mục tiêu

**Địa Điểm**:
- **Warehouse**: Nơi lưu trữ hàng hoàn thành

**Trạng Thái**:
- Draft → Planned → Released → Completed → Cancelled

### Quy Trình Trạng Thái Kế Hoạch

```
Draft (chỉnh sửa) → Planned (hoàn thiện) → Released (gửi đến xưởng) →
Completed (sản xuất xong) hoặc Cancelled (hủy kế hoạch)
```

**Mô Tả Trạng Thái**:

- **Draft**: Vẫn đang chỉnh sửa, có thể sửa đổi tự do
- **Planned**: Đã hoàn thiện nhưng chưa được phát hành cho sản xuất
- **Released**: Đã gửi đến xưởng, có thể tạo Work Orders
- **Completed**: Tất cả sản xuất đã hoàn thành
- **Cancelled**: Kế hoạch bị hủy, không sản xuất

### Lập Kế Hoạch Công Suất

Hệ thống có thể kiểm tra xem trạm làm việc của bạn có đủ công suất không:

**Trạng Thái Công Suất**:
- **Unknown**: Chưa chạy kiểm tra công suất
- **OK**: Tất cả trạm làm việc có công suất đủ
- **Overloaded**: Một số trạm làm việc quá tải (cần hành động)

**Cách kiểm tra công suất**:
1. Mở kế hoạch sản xuất
2. Nhấp nút **Check Capacity**
3. Xem xét báo cáo công suất
4. Nếu quá tải:
   - Giảm số lượng theo kế hoạch
   - Mở rộng thời gian
   - Thêm làm thêm giờ/ca bổ sung
   - Gia công phụ một số hoạt động

### Các Hành Động Kế Hoạch Sản Xuất

**Refresh Plan Items**:
- Tính toán lại số lượng từ dữ liệu nguồn
- Cập nhật nếu kết quả dự báo thay đổi
- Sử dụng khi bạn đã chạy lại dự báo

**Release Plan**:
- Thay đổi trạng thái thành "Released"
- Khóa kế hoạch khỏi chỉnh sửa
- Sẵn sàng để tạo Work Order

**Create Work Orders**:
- Tạo ERPNext Work Orders từ các hạng mục kế hoạch
- Một Work Order cho mỗi hạng mục kế hoạch
- Liên kết ngược lại với kế hoạch sản xuất

---

## Tối Ưu Hóa MRP

### Tổng Quan

MRP (Material Requirements Planning - Lập Kế Hoạch Yêu Cầu Vật Liệu) tính toán chính xác vật liệu bạn cần mua để thực hiện kế hoạch sản xuất. Nó bao gồm lựa chọn nhà cung cấp thông minh để giảm thiểu chi phí và thời gian giao hàng.

### Cách Thức MRP Hoạt Động

```
Kế Hoạch Sản Xuất → Khai Triển BOM → Kiểm Tra Tồn Kho →
Tính Toán Thiếu Hụt → Tối Ưu Nhà Cung Cấp → Đề Xuất Mua Hàng
```

#### Quy Trình MRP:

1. **Khai Triển BOM**: Đối với mỗi hạng mục kế hoạch sản xuất, mở rộng BOM để lấy nguyên vật liệu
2. **Tính Toán Số Lượng**: Tính tổng vật liệu cần thiết cho tất cả các công việc
3. **Kiểm Tra Tồn Kho**: Kiểm tra mức tồn kho hiện tại
4. **Phát Hiện Thiếu Hụt**: Số lượng yêu cầu - Số lượng có sẵn = Thiếu hụt
5. **Chấm Điểm Nhà Cung Cấp**: Đánh giá tất cả nhà cung cấp cho mỗi vật liệu
6. **Tối Ưu Hóa**: Chọn nhà cung cấp tốt nhất dựa trên giá và thời gian giao hàng
7. **Đề Xuất**: Tạo đề xuất mua hàng

### Chạy Tối Ưu Hóa MRP

1. Mở một **Production Plan** (trạng thái nên là Planned hoặc Released)
2. Nhấp nút **Run MRP**
3. Cấu hình cài đặt:

**Tham Số MRP**:
- **Buffer Days**: Số ngày bổ sung cho yêu cầu vật liệu (biên độ an toàn)
  - 0 ngày: Đúng thời điểm, rủi ro nếu có trễ
  - 7 ngày: Đệm một tuần (khuyến nghị)
  - 14+ ngày: Biên độ an toàn lớn cho các mặt hàng quan trọng

- **Include Non-Stock Items**:
  - Yes: Bao gồm dịch vụ và mặt hàng không thuộc tồn kho
  - No: Chỉ vật liệu vật lý

4. Nhấp **Run MRP Optimization**
5. Đợi xử lý
6. Xem xét kết quả MRP

### Hiểu Kết Quả MRP

#### Tóm Tắt APS MRP Run:

- **Total Materials**: Có bao nhiêu vật liệu khác nhau cần thiết
- **Total Shortage Qty**: Tổng số lượng cần mua
- **Total Purchase Value**: Chi phí ước tính (nếu có giá nhà cung cấp)
- **Run Status**: Pending → Running → Completed / Failed

#### APS MRP Result (Thiếu Hụt Vật Liệu):

Mỗi bản ghi thiếu hụt hiển thị:

- **Material Item**: Nguyên vật liệu nào cần thiết
- **Required Qty**: Tổng số lượng cần thiết
- **Available Qty**: Tồn kho hiện tại
- **Shortage Qty**: Cần mua bao nhiêu (Yêu cầu - Có sẵn)
- **Required Date**: Khi bạn cần vật liệu này
- **Required For Item**: Hàng hoàn thành nào cần vật liệu này
- **Required For Work Order**: Công việc nào cần nó (nếu Work Orders tồn tại)

### Thuật Toán Tối Ưu Nhà Cung Cấp

Đối với mỗi thiếu hụt vật liệu, hệ thống đánh giá tất cả nhà cung cấp có sẵn:

#### Công Thức Chấm Điểm:

```
Điểm Nhà Cung Cấp = (0.6 × Điểm Giá) + (0.4 × Điểm Thời Gian Giao Hàng)
```

**Điểm Giá** (chuẩn hóa):
- Giá thấp hơn = Điểm cao hơn
- Tính toán là: 1 - (giá_nhà_cung_cấp / giá_tối_đa_trong_tất_cả_nhà_cung_cấp)

**Điểm Thời Gian Giao Hàng** (chuẩn hóa):
- Thời gian giao hàng ngắn hơn = Điểm cao hơn
- Tính toán là: 1 - (thời_gian_giao_hàng_nhà_cung_cấp / thời_gian_giao_hàng_tối_đa_trong_tất_cả_nhà_cung_cấp)

**Trọng Số**:
- Giá: 60% trọng số (chi phí là mối quan tâm chính)
- Thời gian giao hàng: 40% trọng số (tốc độ quan trọng, nhưng chi phí quan trọng hơn)

**Ví dụ**:

Vật liệu: Tấm thép (cần 100 kg)

| Nhà Cung Cấp | Giá/kg | Thời gian giao | Điểm Giá | Điểm Thời gian | Tổng Điểm | Xếp hạng |
|--------------|--------|----------------|----------|----------------|-----------|----------|
| Nhà cung cấp A | $10 | 7 ngày | 0.67 | 0.53 | 0.61 | 🥈 2 |
| Nhà cung cấp B | $8 | 14 ngày | 1.00 | 0.00 | 0.60 | 🥉 3 |
| Nhà cung cấp C | $9 | 5 ngày | 0.83 | 0.64 | 0.75 | 🥇 **Tốt nhất** |

**Người chiến thắng**: Nhà cung cấp C (cân bằng tốt về giá và tốc độ)

### Đề Xuất Mua Hàng

Sau khi tối ưu hóa, hệ thống tạo các bản ghi **APS Purchase Suggestion**:

**Chi Tiết Đề Xuất**:
- **Material Item**: Mua gì
- **Purchase Qty**: Mua bao nhiêu
- **Required Date**: Khi bạn cần nó
- **Supplier**: Nhà cung cấp được tối ưu hóa (điểm tốt nhất)
- **Unit Price**: Giá mỗi đơn vị từ nhà cung cấp này
- **Lead Time**: Thời gian giao hàng tính bằng ngày
- **Total Cost**: Số lượng mua × Giá đơn vị

**Trạng Thái Đề Xuất**:
- **Draft**: Đề xuất ban đầu
- **Approved**: Đã được đội mua hàng xem xét và phê duyệt
- **Ordered**: Đã tạo Purchase Order
- **Rejected**: Đề xuất bị từ chối (ghi đè thủ công)

**Nhà Cung Cấp Thay Thế**:
- Lưu trữ ở định dạng JSON
- Hiển thị nhà cung cấp đứng thứ 2 và 3
- Sử dụng nếu nhà cung cấp chính không có sẵn

### Sử Dụng Đề Xuất Mua Hàng

#### Tùy Chọn 1: Tạo Purchase Order Thủ Công

1. Xem xét các đề xuất trong danh sách **APS Purchase Suggestion**
2. Đối với mỗi đề xuất được phê duyệt:
   - Vào **Buying > Purchase Order > New**
   - Điền nhà cung cấp và mặt hàng từ đề xuất
   - Gửi Purchase Order
3. Cập nhật trạng thái đề xuất thành "Ordered"

#### Tùy Chọn 2: Tạo Purchase Order Hàng Loạt

1. Lọc các đề xuất với trạng thái "Approved"
2. Chọn nhiều đề xuất
3. Nhấp **Create Purchase Orders** (hành động hàng loạt)
4. Hệ thống tạo một PO cho mỗi nhà cung cấp, nhóm các mặt hàng
5. Xem xét và gửi các PO trong ERPNext

### Phương Pháp Hay Nhất cho MRP

**Trước Khi Chạy MRP**:
- Đảm bảo tất cả BOM được cập nhật
- Xác minh mức tồn kho hiện tại (chạy đối chiếu tồn kho)
- Cập nhật giá và thời gian giao hàng của nhà cung cấp
- Đặt số ngày đệm thực tế dựa trên độ tin cậy của nhà cung cấp

**Sau Kết Quả MRP**:
- Xem xét thiếu hụt để đảm bảo hợp lý
- Kiểm tra xem nhà cung cấp được tối ưu hóa có thực sự có sẵn không
- Cân nhắc các yếu tố chiến lược (mối quan hệ nhà cung cấp, chất lượng)
- Điều chỉnh số lượng mua cho MOQ (Số Lượng Đặt Hàng Tối Thiểu)
- Hợp nhất đơn hàng để tiết kiệm chi phí vận chuyển

**Xử Lý Các Trường Hợp Đặc Biệt**:

**Mặt Hàng Có Thời Gian Giao Hàng Dài**:
- Tăng số ngày đệm cho các vật liệu này
- Cân nhắc chính sách tồn kho an toàn
- Đặt hàng sớm trong chu kỳ lập kế hoạch

**Vật Liệu Quan Trọng**:
- Không chỉ dựa vào điểm MRP
- Sử dụng nhà cung cấp đã được chứng minh ngay cả khi đắt hơn một chút
- Cân nhắc nhà cung cấp dự phòng

**Vật Liệu Theo Mùa**:
- Tính đến tính sẵn có của nhà cung cấp
- Có thể cần đặt hàng sớm trong các mùa cao điểm

---

## Lập Lịch Sản Xuất

### Tổng Quan

Lập lịch sản xuất gán thời gian bắt đầu và kết thúc cụ thể cho mỗi hoạt động sản xuất, tối ưu hóa việc sử dụng máy móc và đáp ứng thời hạn giao hàng.

UIT APS sử dụng **hệ thống lập lịch kết hợp ba tầng**:
- **Tầng 1**: Tối ưu hóa OR-Tools (lịch trình cơ sở)
- **Tầng 2**: Reinforcement Learning (điều chỉnh thời gian thực)
- **Tầng 3**: Graph Neural Networks (thông tin chiến lược)

### Cách Thức Lập Lịch Hoạt Động

#### Tầng 1: OR-Tools CP-SAT Solver (Tối Ưu Hóa Cơ Sở)

**Nó làm gì**:
- Tạo lịch trình tối ưu ban đầu
- Giải quyết Bài toán Lập Lịch Xưởng Sản Xuất (JSSP)
- Sử dụng lập trình ràng buộc để tìm giải pháp tốt nhất

**Các ràng buộc được thực thi**:
1. **Precedence**: Các hoạt động phải xảy ra theo trình tự (không thể sơn trước khi hàn)
2. **No Overlap**: Một công việc trên mỗi máy tại một thời điểm
3. **Capacity**: Tôn trọng tính sẵn có của máy và giờ làm việc
4. **Due Dates**: Cố gắng đáp ứng thời hạn giao hàng cho khách hàng

**Mục tiêu tối ưu hóa**:
```
Tối thiểu hóa: (Trọng số Makespan × Tổng Thời Gian) + (Trọng số Tardiness × Tổng Trễ)
```

- **Makespan**: Tổng thời gian từ bắt đầu đến kết thúc của tất cả công việc
- **Tardiness**: Mức độ trễ của công việc so với ngày đến hạn

**Cách hoạt động**:
```
Đầu vào: Job Cards với các hoạt động
↓
Xây dựng Mô hình Ràng buộc:
  - Biến: Thời gian bắt đầu của mỗi hoạt động
  - Ràng buộc: Ưu tiên, công suất, không chồng chéo
  - Mục tiêu: Tối thiểu hóa makespan + tardiness
↓
CP-SAT Solver tìm kiếm giải pháp tối ưu
↓
Đầu ra: Thời gian bắt đầu/kết thúc đã lập lịch cho mỗi hoạt động
```

**Trạng Thái Solver**:
- **Optimal**: Đã tìm thấy giải pháp tốt nhất có thể
- **Feasible**: Đã tìm thấy giải pháp tốt nhưng có thể không phải là tốt nhất tuyệt đối
- **Infeasible**: Không tồn tại giải pháp (ràng buộc quá chặt)
- **Timeout**: Hết thời gian trước khi tìm được tối ưu (sử dụng tốt nhất được tìm thấy cho đến nay)

#### Tầng 2: Reinforcement Learning (Điều Chỉnh Thời Gian Thực)

**Nó làm gì**:
- Điều chỉnh lịch trình khi xảy ra gián đoạn
- Học hỏi từ kinh nghiệm để đưa ra quyết định tốt hơn
- Xử lý các sự kiện bất ngờ trong thời gian thực

**Các trường hợp sử dụng**:
- Hỏng máy: Phân công lại hoạt động cho máy khác
- Đơn hàng gấp: Ưu tiên công việc khẩn cấp
- Lâu hơn dự kiến: Sắp xếp lại các hoạt động còn lại
- Trễ vật liệu: Lập lịch lại các hoạt động phụ thuộc

**RL Agents có sẵn**:

**PPO (Proximal Policy Optimization)**:
- Ổn định và hiệu quả mẫu
- Tốt cho lập lịch lại đa mục đích
- Khuyến nghị cho hầu hết các trường hợp sử dụng

**SAC (Soft Actor-Critic)**:
- Khám phá các giải pháp thay thế tốt hơn
- Xử lý không gian hành động liên tục
- Sử dụng cho các kịch bản phức tạp, đa mục tiêu

**Cách RL agent hoạt động**:
```
Quan sát Trạng Thái Hiện Tại:
  - Mức sử dụng máy
  - Tiến độ hoạt động
  - Makespan hiện tại
  - Tardiness
  - Các hoạt động đang chờ
↓
RL Agent quyết định hành động:
  - Sắp xếp lại các hoạt động
  - Thay đổi phân công máy
  - Ưu tiên công việc cụ thể
↓
Áp dụng hành động và đo lường phần thưởng:
  - Dương: Giảm makespan, giao hàng đúng hạn
  - Âm: Tăng trễ, hiệu suất thấp
↓
Agent học hỏi từ kết quả
```

#### Tầng 3: Graph Neural Networks (Thông Tin Chiến Lược)

**Nó làm gì**:
- Dự đoán các nút thắt cổ chai trong tương lai trước khi chúng xảy ra
- Ước tính thời lượng hoạt động chính xác hơn
- Cung cấp khuyến nghị chiến lược

**Dự Đoán GNN**:

**1. Dự Đoán Nút Thắt**:
- Xác định các hoạt động nào sẽ gây ra trễ
- Điểm xác suất (0-1) cho mỗi hoạt động
- Cho phép can thiệp chủ động

**2. Dự Đoán Thời Lượng**:
- Ước tính thời gian hoạt động thực tế (thường khác với thời gian tiêu chuẩn)
- Dựa trên loại mặt hàng, máy móc, kỹ năng nhân viên
- Cải thiện độ chính xác của lịch trình

**3. Dự Đoán Trễ**:
- Dự báo công việc nào sẽ bị trễ
- Điểm rủi ro cho mỗi công việc
- Hệ thống cảnh báo sớm

**4. Khuyến Nghị Chiến Lược**:
- "Thêm công suất cho trạm làm việc CNC-01"
- "Đào tạo chéo nhân viên để linh hoạt"
- "Cân nhắc gia công phụ Operation XYZ"

**Cách GNN hoạt động**:
```
Xây dựng Đồ Thị Hoạt Động:
  - Nút: Mỗi hoạt động
  - Cạnh: Phụ thuộc và chia sẻ tài nguyên
  - Đặc điểm nút: Thời lượng, máy, mặt hàng, trạng thái
↓
Graph Attention Network (GAT) xử lý đồ thị:
  - Tầng 1: Học các mô hình cục bộ
  - Tầng 2: Học các phụ thuộc toàn cục
↓
Dự đoán:
  - Xác suất nút thắt cho mỗi hoạt động
  - Thời lượng ước tính cho mỗi hoạt động
  - Khuyến nghị cho lập kế hoạch công suất
```

### Chạy Lập Lịch

#### Lập Lịch Cơ Bản (Chỉ Tầng 1):

1. Mở một **Production Plan** (trạng thái Released)
2. Nhấp nút **Schedule Production**
3. Cấu hình các tham số OR-Tools:

**Giới Hạn Thời Gian**:
- 60 giây: Giải pháp nhanh, có thể không tối ưu
- 300 giây (5 phút): Khuyến nghị cho hầu hết các trường hợp
- 600+ giây: Cho các kịch bản phức tạp với nhiều công việc

**Trọng Số Mục Tiêu**:
- **Makespan Weight** (0-1): Mức độ ưu tiên hoàn thành nhanh
- **Tardiness Weight** (0-1): Mức độ ưu tiên giao hàng đúng hạn
- Cài đặt thông dụng:
  - Ưu tiên bằng nhau: 0.5 / 0.5
  - Tập trung tốc độ: 0.7 / 0.3
  - Tập trung thời hạn: 0.3 / 0.7

**Chiến Lược Lập Lịch**:
- **Forward**: Bắt đầu càng sớm càng tốt, đẩy thời hạn nếu cần
- **Backward**: Bắt đầu từ ngày đến hạn, làm việc ngược lại
- **Priority**: Công việc ưu tiên cao trước
- **EDD**: Ngày Đến Hạn Sớm Nhất trước

4. Nhấp **Run Schedule**
5. Đợi solver hoàn thành
6. Xem xét kết quả lập lịch

#### Lập Lịch Kết Hợp (Tất Cả Các Tầng):

1. Mở một **Production Plan**
2. Nhấp **Run Hybrid Scheduling**
3. Cấu hình:

**Enable RL**: Yes/No
- Yes: Áp dụng điều chỉnh RL agent sau OR-Tools
- No: Chỉ sử dụng OR-Tools cơ sở

**RL Agent Type**: PPO hoặc SAC (nếu RL được bật)

**OR-Tools Settings**: Giống như lập lịch cơ bản

4. Nhấp **Run Hybrid Schedule**

Hệ thống sẽ:
1. Chạy OR-Tools cho cơ sở (Tầng 1)
2. Áp dụng điều chỉnh RL nếu được bật (Tầng 2)
3. Tạo dự đoán GNN và khuyến nghị (Tầng 3)
4. Tạo lịch trình cuối cùng với tất cả thông tin chi tiết

### Hiểu Kết Quả Lập Lịch

#### Tóm Tắt APS Scheduling Run:

**Thống Kê Công Việc**:
- **Total Job Cards**: Bao nhiêu công việc được lập lịch
- **Total Operations**: Tổng số hoạt động
- **Total Machines**: Trạm làm việc được sử dụng
- **Jobs On Time**: Đã đáp ứng thời hạn giao hàng
- **Total Late Jobs**: Bị trễ thời hạn

**Hiệu Suất Solver**:
- **Solver Status**: Optimal, Feasible, Infeasible, Timeout
- **Solve Time**: Mất bao lâu (giây)
- **Gap Percentage**: Cách xa tối ưu (0% = tối ưu)

**Chỉ Số Lịch Trình**:
- **Makespan (minutes)**: Tổng thời gian để hoàn thành tất cả công việc
- **Total Tardiness (minutes)**: Tổng tất cả độ trễ
- **Machine Utilization (%)**: Mức sử dụng máy trung bình

**Thông Tin GNN** (nếu Tầng 3 chạy):
- **Predicted Bottlenecks**: Danh sách các hoạt động rủi ro
- **Strategic Recommendations**: Đề xuất có thể thực hiện

#### APS Scheduling Result (Chi Tiết Hoạt Động):

Mỗi hoạt động nhận được thời gian đã lập lịch:

- **Operation ID**: Định danh duy nhất
- **Job Card Name**: Liên kết đến ERPNext Job Card
- **Work Order Name**: Work Order cha
- **Item Code**: Sản phẩm đang được sản xuất
- **Operation Name**: Hoạt động cụ thể (Cắt, Hàn, v.v.)
- **Machine ID**: Trạm làm việc được phân công
- **Start Time**: Khi bắt đầu hoạt động này
- **End Time**: Khi nó nên kết thúc
- **Duration (mins)**: Mất bao lâu
- **Sequence**: Thứ tự trong công việc
- **Is Late**: Cờ nếu hoạt động này góp phần vào độ trễ của công việc
- **Tardiness (mins)**: Trễ bao nhiêu phút (nếu có)
- **Is Predicted Bottleneck**: Cờ dự đoán GNN
- **Predicted Duration**: Ước tính của GNN so với thời gian tiêu chuẩn

### Sử Dụng Kết Quả Lập Lịch

#### Cập Nhật Job Cards:

1. Sau khi lập lịch thành công, nhấp **Update Job Cards**
2. Hệ thống đẩy thời gian đã lập lịch đến ERPNext Job Cards
3. Job Cards hiện hiển thị thời gian bắt đầu/kết thúc theo kế hoạch
4. Xưởng có thể xem lịch trình

#### Trực Quan Hóa Lịch Trình (Biểu Đồ Gantt):

1. Mở danh sách **Scheduling Result**
2. Nhấp nút **Gantt View**
3. Xem dòng thời gian trực quan:
   - Trục X: Thời gian
   - Trục Y: Máy/Trạm làm việc
   - Khối màu: Các hoạt động
   - Xác định nút thắt máy một cách trực quan

#### Xuất Lịch Trình:

1. Mở **APS Scheduling Run**
2. Nhấp **Export to Excel**
3. Chia sẻ với người quản lý sản xuất
4. In để hiển thị tại xưởng

### Điều Chỉnh Thời Gian Thực (RL)

Khi xảy ra gián đoạn trong sản xuất:

#### Kịch Bản: Hỏng Máy

1. Máy CNC-01 hỏng trong 2 giờ
2. Vào **APS Scheduling Run** (lịch trình đang hoạt động)
3. Nhấp **Handle Disruption**
4. Điền chi tiết gián đoạn:
   - **Disruption Type**: Machine Breakdown
   - **Affected Resource**: CNC-01
   - **Duration**: 120 phút
5. Nhấp **Get RL Recommendation**

RL agent sẽ:
- Phân tích trạng thái hiện tại
- Đánh giá các tùy chọn (phân công lại, trễ, sắp xếp lại)
- Khuyến nghị hành động tốt nhất
- Hiển thị tác động dự kiến

6. Xem xét khuyến nghị
7. Nhấp **Apply RL Adjustment**
8. Lịch trình được cập nhật với thời gian mới

#### Kịch Bản: Đơn Hàng Gấp

1. Khách hàng gọi với đơn hàng khẩn cấp
2. Tạo Job Card ưu tiên cao
3. Vào **APS Scheduling Run** đang hoạt động
4. Nhấp **Handle Disruption**
5. Disruption Type: Rush Order
6. Affected Job: Job Card khẩn cấp mới
7. Nhận khuyến nghị RL
8. Áp dụng điều chỉnh

Lịch trình sắp xếp lại để phù hợp với đơn hàng gấp trong khi giảm thiểu tác động đến các công việc khác.

### Huấn Luyện RL Agents

Để có hiệu suất tốt hơn theo thời gian:

1. Vào **UIT APS > RL Agent Training**
2. Chọn **Scheduling Run** (dữ liệu lịch sử để học hỏi)
3. Chọn **Agent Type**: PPO hoặc SAC
4. Đặt **Max Episodes**: 1000+ (nhiều tập hơn = học tốt hơn)
5. Nhấp **Train Agent**
6. Đợi huấn luyện (có thể mất hàng giờ cho huấn luyện kỹ lưỡng)
7. Agent được huấn luyện được lưu và sử dụng cho các khuyến nghị trong tương lai

**Mẹo Huấn Luyện**:
- Sử dụng dữ liệu lịch sử với nhiều gián đoạn khác nhau
- Dữ liệu huấn luyện đa dạng hơn = tổng quát hóa tốt hơn
- Huấn luyện lại định kỳ khi các mô hình sản xuất thay đổi

### Phân Tích Nút Thắt (GNN)

Để xác định và ngăn ngừa nút thắt:

1. Mở **APS Scheduling Run**
2. Nhấp **Predict Bottlenecks**
3. Đặt **Threshold**: 0.7 (xác suất 70% để đánh dấu)
4. Xem xét dự đoán nút thắt:

**Đối với mỗi nút thắt dự đoán**:
- Chi tiết hoạt động
- Điểm xác suất
- Trễ dự đoán (phút)
- Khuyến nghị

5. Thực hiện hành động chủ động:
   - Thêm làm thêm giờ cho trạm làm việc nút thắt
   - Phân công lại hoạt động cho máy thay thế
   - Gia công phụ hoạt động
   - Điều chỉnh lịch trình để có thêm thời gian

### Phương Pháp Hay Nhất cho Lập Lịch

**Trước Khi Lập Lịch**:
- Đảm bảo tất cả Job Cards có hoạt động được xác định
- Xác minh lịch trạm làm việc (ngày lễ, bảo trì)
- Kiểm tra BOM routings đúng
- Đặt tiêu chuẩn thời gian hoạt động thực tế

**Chọn Trọng Số**:
- Sản xuất để lưu kho: Trọng số makespan cao hơn (hoàn thành nhanh)
- Sản xuất theo đơn: Trọng số tardiness cao hơn (đáp ứng thời hạn)
- Cân bằng: Trọng số bằng nhau

**Giới Hạn Thời Gian Solver**:
- Xưởng nhỏ (<50 hoạt động): 60-120 giây
- Xưởng trung bình (50-200 hoạt động): 300 giây
- Xưởng lớn (>200 hoạt động): 600+ giây
- Ràng buộc phức tạp: Tăng giới hạn thời gian

**Khi Nào Sử Dụng RL**:
- Gián đoạn thường xuyên: Bật RL cho điều chỉnh động
- Môi trường ổn định: Chỉ OR-Tools có thể đủ
- Giai đoạn học: Tắt RL cho đến khi agent được huấn luyện

**Khi Nào Sử Dụng GNN**:
- Lập kế hoạch công suất: Luôn sử dụng cho dự đoán nút thắt
- Sản phẩm mới: Sử dụng dự đoán thời lượng để ước tính tốt hơn
- Quyết định chiến lược: Xem xét khuyến nghị hàng quý

**Cải Tiến Liên Tục**:
- So sánh thời gian đã lập lịch với thực tế
- Theo dõi tỷ lệ giao hàng đúng hạn
- Phân tích dự đoán nút thắt so với thực tế
- Huấn luyện lại RL agents với dữ liệu mới
- Điều chỉnh trọng số dựa trên ưu tiên kinh doanh

---

## Các Ví Dụ Quy Trình Hoàn Chỉnh

### Ví Dụ 1: Chu Kỳ Lập Kế Hoạch Đầy Đủ (Từ Dự Báo đến Lập Lịch)

**Kịch bản**: Nhà sản xuất điện tử lập kế hoạch sản xuất Q2 2026

#### Bước 1: Chạy Dự Báo Nhu Cầu

```
Hành động: Tạo APS Forecast History
Cài đặt:
  - Model: Prophet (nhiều tính theo mùa)
  - Company: ABC Electronics
  - Forecast Horizon: 90 ngày
  - Training Period: 365 ngày
  - Item Group: Finished Goods
Kết quả:
  - 45 mặt hàng được dự báo
  - MAPE trung bình: 15.2% (Tốt)
  - Độ tin cậy trung bình: 82%
```

#### Bước 2: Xem Xét Kết Quả Dự Báo

```
Top Items theo Forecast Qty:
  1. Smartphone X: 5,200 đơn vị (Xu hướng tăng, Độ tin cậy cao)
  2. Tablet Pro: 3,800 đơn vị (Ổn định, Độ tin cậy trung bình)
  3. Laptop Slim: 2,100 đơn vị (Xu hướng giảm, Độ tin cậy cao)

Các hành động từ AI:
  - Smartphone X: Tăng tồn kho an toàn 20% do xu hướng
  - Tablet Pro: Duy trì mức tồn kho hiện tại
  - Laptop Slim: Giảm đơn hàng, có thể ngừng sản xuất
```

#### Bước 3: Tạo Kế Hoạch Sản Xuất

```
Hành động: Tạo APS Production Plan
Cài đặt:
  - Plan Name: "Q2 2026 Production"
  - Forecast History: FCST-RUN-2026-01-06-0001
  - Period: 2026-04-01 đến 2026-06-30
  - Time Granularity: Monthly
  - Source Type: Forecast

Các hạng mục kế hoạch được tạo:
  - Smartphone X (April): 1,800 đơn vị
  - Smartphone X (May): 1,700 đơn vị
  - Smartphone X (June): 1,700 đơn vị
  ... (tương tự cho các mặt hàng khác)

Kiểm tra công suất: OK (80% utilization)
```

#### Bước 4: Chạy Tối Ưu Hóa MRP

```
Hành động: Chạy MRP từ Production Plan
Cài đặt:
  - Buffer Days: 7
  - Include Non-Stock: No

Kết quả:
  - Total Materials: 230 vật liệu khác nhau
  - Material Shortages: 85 mặt hàng
  - Total Purchase Value: $420,000

Đề xuất mua hàng hàng đầu:
  1. LCD Display 5": 12,000 cái từ Supplier C ($18/cái, 10 ngày)
  2. Battery Pack Li-Ion: 8,500 cái từ Supplier A ($25/cái, 14 ngày)
  3. PCB Assembly: 6,200 cái từ Supplier B ($45/cái, 7 ngày)

Hành động: Phê duyệt tất cả đề xuất, tạo Purchase Orders
```

#### Bước 5: Lập Lịch Sản Xuất

```
Hành động: Chạy Hybrid Scheduling
Cài đặt:
  - Scheduling Strategy: Priority (đơn hàng khẩn cấp trước)
  - Time Limit: 300 giây
  - Makespan Weight: 0.4
  - Tardiness Weight: 0.6 (tập trung thời hạn)
  - Enable RL: Yes
  - RL Agent: PPO

Kết quả Tầng 1 (OR-Tools):
  - Solver Status: Optimal
  - Makespan: 21,450 phút (14.9 ngày)
  - Total Tardiness: 0 phút
  - Machine Utilization: 82%

Điều chỉnh Tầng 2 (RL):
  - Sắp xếp lại 12 hoạt động
  - Cải thiện makespan 180 phút
  - Makespan cuối cùng: 21,270 phút (14.7 ngày)

Dự đoán Tầng 3 (GNN):
  - Bottlenecks: 3 hoạt động được đánh dấu
    • Assembly Line 2 (Operation: Final Assembly)
    • Testing Station 1 (Operation: Quality Test)
  - Khuyến nghị:
    • Thêm ca thứ hai cho Assembly Line 2
    • Đào tạo chéo người kiểm tra cho Testing Station 1
```

#### Bước 6: Thực Hiện Sản Xuất

```
Hành động: Cập nhật Job Cards với lịch trình
Hành động: Release Production Plan

Hành động xưởng:
  - Job Cards hiển thị thời gian đã lập lịch
  - Vật liệu đã đặt đến đúng hạn
  - Sản xuất chạy theo lịch trình
  - Giám sát các gián đoạn

Nếu có gián đoạn:
  - Sử dụng RL agent để lập lịch lại thời gian thực
  - Cập nhật Job Cards với thời gian mới
```

#### Bước 7: Giám Sát và Cải Tiến

```
Theo dõi chỉ số:
  - Độ chính xác dự báo: So sánh doanh số thực tế với dự báo
  - Tuân thủ lịch trình: Hoàn thành thực tế so với đã lập lịch
  - Giao hàng đúng hạn: % công việc hoàn thành đúng hạn
  - Tính sẵn có của vật liệu: % vật liệu đến đúng hạn

Cải tiến liên tục:
  - Dự báo lại hàng tháng với dữ liệu mới nhất
  - Điều chỉnh số ngày đệm MRP dựa trên hiệu suất nhà cung cấp
  - Huấn luyện lại RL agent với dữ liệu sản xuất thực tế
  - Xem xét dự đoán nút thắt GNN so với thực tế
```

**Kết quả**:
- Giao hàng đúng hạn 95% cho Q2
- $420K trong mua hàng được tối ưu hóa (tiết kiệm 12% so với quý trước)
- 14.7 ngày tổng thời gian sản xuất so với 18 ngày trước đây
- Xác định và giải quyết 2 nút thắt một cách chủ động

---

### Ví Dụ 2: Lập Kế Hoạch Lại Nhanh cho Đơn Hàng Gấp

**Kịch bản**: Lịch trình sản xuất hiện tại, khách hàng đặt hàng lô khẩn cấp

#### Trạng Thái Hiện Tại:

```
Lịch trình đang hoạt động: SCH-RUN-2026-0015
  - 25 công việc đang sản xuất
  - Makespan: 8 ngày
  - Tất cả đúng hạn để giao hàng
```

#### Gián Đoạn:

```
Đơn hàng mới: 500 đơn vị Product Z
Ngày đến hạn: 3 ngày từ bây giờ
Ưu tiên: Quan trọng (khách hàng VIP)
```

#### Các Bước Đáp Ứng:

**Bước 1: Tạo Job Card**
```
- Tạo Work Order cho Product Z (500 đơn vị)
- Tạo Job Card với các hoạt động
- Đặt Priority: High
```

**Bước 2: Xử Lý Gián Đoạn với RL**
```
Hành động: Mở SCH-RUN-2026-0015
Click: Handle Disruption
  - Disruption Type: Rush Order
  - Affected Resource: Job Card mới JOB-00125
  - Required Completion: 3 ngày

Click: Get RL Recommendation

Phân tích RL Agent:
  - Các công việc hiện tại có thể trễ 1 ngày mà không bị phạt
  - Máy CNC-02 có công suất cho công việc gấp
  - Trình tự khuyến nghị: Chèn Job-00125 tại vị trí 3
  - Tác động dự kiến: +1 ngày cho 2 công việc không quan trọng
```

**Bước 3: Áp Dụng Điều Chỉnh**
```
Click: Apply RL Adjustment

Lịch trình mới:
  - Công việc gấp bắt đầu ngay trên CNC-02
  - 2 công việc trễ 1 ngày (vẫn đúng hạn)
  - Công việc gấp hoàn thành trong 2.5 ngày
  - Đáp ứng thời hạn khách hàng với đệm 0.5 ngày
```

**Bước 4: Cập Nhật Xưởng**
```
Click: Update Job Cards
Thông báo: Đội sản xuất về công việc ưu tiên mới
Giám sát: Tiến độ đơn hàng gấp
```

**Kết quả**:
- Đơn hàng gấp được giao trong 2.5 ngày (sớm 0.5 ngày)
- Chỉ 2 công việc bị ảnh hưởng, vẫn đáp ứng thời hạn của họ
- Duy trì sự hài lòng của khách hàng
- Gián đoạn tối thiểu cho lịch trình tổng thể

---

### Ví Dụ 3: Giải Quyết Nút Thắt

**Kịch bản**: Giao hàng trễ tái diễn, cần xác định nguyên nhân gốc rễ

#### Bước 1: Chạy Lập Lịch với GNN

```
Hành động: Lập lịch sản xuất tháng tới với Tầng 3 được bật
Cài đặt:
  - Bật cả ba tầng
  - Ngưỡng nút thắt: 0.6 (xác suất 60%)
```

#### Bước 2: Phân Tích Dự Đoán Nút Thắt

```
Dự đoán GNN:
  - Operation: Welding trên Welder-01
    • Xác suất: 0.85 (Rủi ro cao)
    • Trễ dự đoán: 3.5 giờ
    • Công việc bị ảnh hưởng: 8 công việc

  - Operation: Painting trên Paint-Booth-A
    • Xác suất: 0.72 (Rủi ro trung bình-cao)
    • Trễ dự đoán: 2.1 giờ
    • Công việc bị ảnh hưởng: 5 công việc
```

#### Bước 3: Xem Xét Khuyến Nghị

```
Khuyến nghị chiến lược từ GNN:

1. Nút thắt Welder-01:
   "Thêm công suất cho trạm làm việc Welder-01"
   Tùy chọn:
   - Thêm máy hàn thứ hai (đầu tư $50K)
   - Gia công phụ các hoạt động hàn ($15/đơn vị)
   - Thêm ca làm thêm giờ (chi phí lao động 1.5x)

2. Nút thắt Paint-Booth-A:
   "Đào tạo chéo nhân viên để linh hoạt"
   Tùy chọn:
   - Đào tạo thêm 2 thợ sơn ($2K chi phí đào tạo)
   - Thuê buồng sơn thứ hai ($5K/tháng)
   - Gộp các hoạt động sơn để hiệu quả
```

#### Bước 4: Triển Khai Giải Pháp

**Ngắn hạn (Ngay lập tức)**:
```
- Thêm ca làm thêm giờ cho Welder-01 (2 giờ/ngày)
- Đào tạo chéo 2 nhân viên cho sơn
- Chi phí: ~$3K/tháng
```

**Dài hạn (Chiến lược)**:
```
- Mua máy hàn thứ hai
- Lắp đặt buồng sơn bổ sung
- Thuê thợ hàn chuyên nghiệp
- Chi phí: $70K vốn + $4K/tháng hoạt động
```

#### Bước 5: Đo Lường Tác Động

**Trước (Tháng Trước)**:
```
- Giao hàng đúng hạn: 78%
- Độ trễ trung bình: 4.2 giờ
- Trễ do nút thắt: 15 trường hợp
```

**Sau (Tháng Sau)**:
```
- Giao hàng đúng hạn: 94% (+16%)
- Độ trễ trung bình: 0.8 giờ (-81%)
- Trễ do nút thắt: 3 trường hợp (-80%)
```

**Tính ROI**:
```
Đầu tư: $70K + ($4K × 12) = $118K/năm
Tiết kiệm:
  - Giảm phạt trễ: $25K/năm
  - Tăng năng suất: $180K/năm doanh thu
  - Cải thiện duy trì khách hàng: $50K/năm

Lợi ích ròng: $255K - $118K = $137K/năm
Thời gian hoàn vốn: 6.2 tháng
```

---

## Xử Lý Sự Cố

### Vấn Đề Dự Báo

#### Vấn đề: "No sales order data found"

**Nguyên nhân**: Không có đơn hàng bán lịch sử cho các bộ lọc đã chọn

**Giải pháp**:
1. Kiểm tra phạm vi ngày: Cần ít nhất 30-60 ngày dữ liệu
2. Xác minh bộ lọc: Xóa bộ lọc mặt hàng/kho để kiểm tra
3. Kiểm tra trạng thái Sales Order: Hệ thống chỉ sử dụng các đơn hàng đã Submitted
4. Xác minh mã mặt hàng: Đảm bảo các mặt hàng tồn tại trong đơn hàng bán

#### Vấn đề: "Forecast accuracy is very low (<50% MAPE)"

**Nguyên nhân**: Dữ liệu không đủ hoặc không đều, chọn mô hình sai

**Giải pháp**:
1. Tăng kỳ huấn luyện (thử 365+ ngày)
2. Thử mô hình khác:
   - Dữ liệu không đều → Thử Prophet
   - Dữ liệu theo mùa → Thử ARIMA
   - Xu hướng ổn định → Thử Linear Regression
3. Làm sạch dữ liệu: Xóa các ngoại lệ hoặc đơn hàng số lượng lớn một lần
4. Kiểm tra vấn đề chất lượng dữ liệu (trùng lặp, số lượng sai)

#### Vấn đề: "AI explanation generation failed"

**Nguyên nhân**: Vấn đề OpenAI API hoặc vấn đề cấu hình

**Giải pháp**:
1. Kiểm tra ChatGPT Settings:
   - API key hợp lệ
   - Đủ API credits
   - Mô hình đã chọn (gpt-4 hoặc gpt-3.5-turbo)
2. Nhấp nút "Retry AI Explanations"
3. Kiểm tra error log cho thông báo lỗi API cụ thể
4. Xác minh kết nối internet từ máy chủ

#### Vấn đề: "Confidence scores are very low"

**Nguyên nhân**: Biến động cao trong dữ liệu lịch sử

**Giải pháp**:
1. Bình thường cho sản phẩm mới (ít lịch sử)
2. Xem xét giải thích dự báo cho bối cảnh
3. Cân nhắc sử dụng giới hạn trên cho tồn kho an toàn
4. Kết hợp với đánh giá của đội bán hàng
5. Dự báo lại với nhiều dữ liệu hơn theo thời gian

---

### Vấn Đề Lập Kế Hoạch Sản Xuất

#### Vấn đề: "No BOM found for item"

**Nguyên nhân**: Mặt hàng không có BOM mặc định được cấu hình

**Giải pháp**:
1. Vào ERPNext > BOM > Tạo BOM cho mặt hàng
2. Đặt BOM làm mặc định (Is Default = Yes)
3. Hoặc chọn BOM thủ công trong hạng mục kế hoạch sản xuất

#### Vấn đề: "Capacity status shows Overloaded"

**Nguyên nhân**: Công suất trạm làm việc không đủ cho sản xuất theo kế hoạch

**Giải pháp**:
1. Mở rộng thời gian (tăng kỳ kế hoạch)
2. Giảm số lượng theo kế hoạch
3. Thêm ca/làm thêm giờ cho trạm làm việc
4. Nâng cấp công suất trạm làm việc trong ERPNext
5. Cân nhắc gia công phụ một số hoạt động

#### Vấn đề: "Production plan items not generating"

**Nguyên nhân**: Kết quả dự báo có vấn đề hoặc không có dữ liệu

**Giải pháp**:
1. Kiểm tra trạng thái lịch sử dự báo (phải là Complete)
2. Xác minh kết quả dự báo tồn tại cho kỳ đã chọn
3. Đảm bảo các mặt hàng dự báo có BOM
4. Kiểm tra bộ lọc: Ngày kỳ phải chồng chéo với ngày dự báo

---

### Vấn Đề MRP

#### Vấn đề: "No material shortages found, but I know we need materials"

**Nguyên nhân**: Mức tồn kho không được cập nhật hoặc vấn đề BOM

**Giải pháp**:
1. Chạy Stock Reconciliation trong ERPNext
2. Kiểm tra BOM cho các mặt hàng sản xuất (phải có nguyên vật liệu)
3. Xác minh lựa chọn kho trong kế hoạch sản xuất
4. Kiểm tra xem "Available Qty" có đúng trong bản ghi Bin không

#### Vấn đề: "Supplier optimization shows 'No suppliers found'"

**Nguyên nhân**: Không có bản ghi Item Supplier hoặc Item Price

**Giải pháp**:
1. Vào ERPNext > Buying > Item Supplier
2. Tạo liên kết nhà cung cấp cho mỗi vật liệu
3. Thêm giá trong Item Price hoặc Supplier Quotation
4. Chạy lại MRP optimization

#### Vấn đề: "MRP run is very slow"

**Nguyên nhân**: Số lượng lớn mặt hàng hoặc BOM phức tạp

**Giải pháp**:
1. Lập kế hoạch theo nhóm mặt hàng thay vì tất cả mặt hàng cùng lúc
2. Đơn giản hóa BOM nhiều cấp nếu có thể
3. Chạy MRP trong giờ thấp điểm
4. Cân nhắc nâng cấp phần cứng máy chủ cho hoạt động lớn

#### Vấn đề: "Suggested supplier doesn't match my preference"

**Nguyên nhân**: Tối ưu hóa dựa hoàn toàn trên giá/thời gian giao hàng

**Giải pháp**:
1. Xem xét nhà cung cấp thay thế trong đề xuất
2. Ghi đè thủ công lựa chọn nhà cung cấp
3. Điều chỉnh Item Price để ưu tiên nhà cung cấp ưa thích
4. Cập nhật thời gian giao hàng để phản ánh thực tế
5. Sử dụng trạng thái "Rejected" và tạo PO thủ công

---

### Vấn Đề Lập Lịch

#### Vấn đề: "Solver status shows Infeasible"

**Nguyên nhân**: Các ràng buộc quá chặt, không tồn tại giải pháp hợp lệ

**Giải pháp**:
1. Kiểm tra ngày đến hạn: Có thể không thể đáp ứng
2. Xem xét công suất trạm làm việc: Có thể cần thêm công suất
3. Mở rộng ràng buộc thời hạn
4. Xóa hoặc nới lỏng một số ràng buộc
5. Kiểm tra xem các hoạt động có trạm làm việc hợp lệ được gán không

#### Vấn đề: "Solver timeout, only Feasible solution"

**Nguyên nhân**: Vấn đề rất phức tạp, cần thêm thời gian

**Giải pháp**:
1. Tăng giới hạn thời gian (thử 600-1800 giây)
2. Điều chỉnh trọng số để hướng dẫn solver nhanh hơn
3. Giảm kích thước vấn đề (lập lịch ít công việc hơn cùng lúc)
4. Đơn giản hóa trình tự hoạt động nếu có thể
5. Giải pháp khả thi vẫn có thể sử dụng, chỉ là chưa được chứng minh là tối ưu

#### Vấn đề: "Schedule has very low machine utilization"

**Nguyên nhân**: Quá nhiều công suất hoặc trình tự không hiệu quả

**Giải pháp**:
1. Tăng trọng số makespan (thắt chặt lịch trình)
2. Kiểm tra các khoảng trống lớn trong lịch trạm làm việc
3. Xem xét tiêu chuẩn thời gian hoạt động (có thể bị đánh giá quá cao)
4. Cân nhắc batch sizing để giảm thời gian thiết lập

#### Vấn đề: "Many jobs showing late even in optimal schedule"

**Nguyên nhân**: Ngày đến hạn không thực tế với công suất đã cho

**Giải pháp**:
1. Mở rộng ngày đến hạn (thương lượng với khách hàng)
2. Thêm công suất (làm thêm giờ, máy bổ sung)
3. Gia công phụ một số hoạt động
4. Ưu tiên các công việc quan trọng (điều chỉnh chiến lược)
5. Xem xét tiêu chuẩn thời gian (có thể bị đánh giá thấp)

#### Vấn đề: "RL adjustment makes schedule worse"

**Nguyên nhân**: RL agent chưa được huấn luyện đầy đủ

**Giải pháp**:
1. Huấn luyện RL agent với nhiều dữ liệu lịch sử hơn
2. Tăng tập huấn luyện (khuyến nghị 1000+)
3. Chỉ sử dụng OR-Tools cho đến khi agent được huấn luyện
4. Xem xét các tham số hàm phần thưởng RL
5. Thử loại agent khác (PPO vs SAC)

#### Vấn đề: "GNN bottleneck predictions are inaccurate"

**Nguyên nhân**: Mô hình chưa được huấn luyện trên các mô hình sản xuất cụ thể của bạn

**Giải pháp**:
1. Thu thập nhiều dữ liệu lập lịch lịch sử hơn
2. Huấn luyện lại mô hình GNN với kết quả thực tế
3. Điều chỉnh ngưỡng dự đoán (thấp hơn để có thêm cảnh báo)
4. Sử dụng dự đoán như hướng dẫn, không phải sự thật tuyệt đối
5. Xác thực dự đoán với kiến thức chuyên môn

---

## Phương Pháp Hay Nhất

### Quản Lý Dữ Liệu

**Giữ Dữ Liệu Chính Sạch**:
- Kiểm toán định kỳ dữ liệu chính mặt hàng
- Lưu trữ các mặt hàng lỗi thời thay vì xóa
- Duy trì BOM và routings chính xác
- Cập nhật giá nhà cung cấp hàng quý
- Xác minh công suất trạm làm việc thường xuyên

**Chất Lượng Dữ Liệu Lịch Sử**:
- Làm sạch các đơn hàng bán thử nghiệm
- Đảm bảo ngày giao dịch phù hợp
- Đối chiếu mức tồn kho hàng tháng
- Ghi chép bất kỳ đơn hàng số lượng lớn hoặc một lần
- Giữ 12+ tháng lịch sử để dự báo

**Tài Liệu**:
- Ghi chép thay đổi BOM với lý do
- Ghi log thời gian ngừng và bảo trì trạm làm việc
- Theo dõi dự báo so với thực tế thường xuyên
- Ghi lại các gián đoạn lập lịch và phản ứng
- Duy trì chỉ số hiệu suất nhà cung cấp

### Chu Kỳ Lập Kế Hoạch

**Tần Suất Khuyến Nghị**:

- **Dự báo**: Hàng tháng cho hầu hết mặt hàng, hàng tuần cho mặt hàng di chuyển nhanh
- **Lập kế hoạch sản xuất**: Hàng tháng hoặc hàng quý tùy thuộc vào thời gian giao hàng
- **MRP**: Chạy với mỗi lần cập nhật kế hoạch sản xuất
- **Lập lịch**: Hàng tuần hoặc hai tuần một lần, hàng ngày cho môi trường mix cao
- **Huấn luyện RL**: Hàng quý với dữ liệu tích lũy
- **Cập nhật mô hình GNN**: Mỗi 6 tháng hoặc khi các mô hình thay đổi

**Phạm Vi Lập Kế Hoạch**:

- **Ngắn hạn** (1-4 tuần): Lập lịch chi tiết, đơn hàng chắc chắn
- **Trung hạn** (1-3 tháng): Lập kế hoạch sản xuất, MRP
- **Dài hạn** (3-12 tháng): Dự báo nhu cầu, lập kế hoạch công suất

### Tối Ưu Hóa Hiệu Suất

**Cho Dữ Liệu Lớn**:
- Dự báo theo nhóm mặt hàng, không phải tất cả cùng lúc
- Lập lịch theo đợt (nhóm hàng tuần)
- Sử dụng bộ lọc để giảm kích thước vấn đề
- Chạy các phép tính nặng trong giờ thấp điểm
- Cân nhắc quy trình worker chuyên dụng cho các tác vụ ML

**Cho Độ Chính Xác**:
- Sử dụng ít nhất 6-12 tháng dữ liệu huấn luyện
- So sánh các mô hình trước khi chọn một
- Xác thực dự báo với đầu vào của đội bán hàng
- Theo dõi chỉ số thực tế so với dự đoán
- Điều chỉnh tham số dựa trên hiệu suất

**Cho Tốc Độ**:
- Bắt đầu với giới hạn thời gian ngắn hơn và tăng nếu cần
- Sử dụng kết quả được lưu cache khi dữ liệu chưa thay đổi
- Huấn luyện trước RL agents trong quá trình triển khai
- Tối ưu hóa truy vấn cơ sở dữ liệu cho BOM lớn

### Quản Lý Thay Đổi

**Khi Triển Khai UIT APS**:

1. **Giai đoạn 1: Thí điểm** (1-2 tháng)
   - Chọn một dòng sản phẩm hoặc nhóm mặt hàng
   - Chạy song song với quy trình hiện tại
   - So sánh kết quả và xây dựng niềm tin
   - Đào tạo người dùng chính

2. **Giai đoạn 2: Mở rộng** (2-3 tháng)
   - Mở rộng sang các dòng sản phẩm bổ sung
   - Tích hợp với quy trình làm việc ERP hiện tại
   - Thiết lập quy trình xem xét
   - Đào tạo cơ sở người dùng rộng hơn

3. **Giai đoạn 3: Tối ưu hóa** (3-6 tháng)
   - Tinh chỉnh các tham số mô hình
   - Huấn luyện RL agents trên dữ liệu thực
   - Thiết lập KPI và dashboard
   - Ghi chép quy trình vận hành tiêu chuẩn

4. **Giai đoạn 4: Cải tiến liên tục** (Đang diễn ra)
   - Xem xét hàng tháng độ chính xác dự báo
   - Huấn luyện lại mô hình hàng quý
   - Kiểm toán quy trình hàng năm
   - Đào tạo người dùng liên tục

**Áp Dụng Người Dùng**:
- Liên quan các planner sớm trong các quyết định thiết kế
- Cung cấp tài liệu đào tạo rõ ràng
- Hiển thị lợi ích cụ thể với chỉ số
- Bắt đầu đơn giản, thêm độ phức tạp dần dần
- Tôn vinh chiến thắng và học hỏi từ thất bại

### Tích Hợp với ERPNext

**Tích Hợp Quy Trình Làm Việc**:

```
UIT APS Forecast → APS Production Plan → ERPNext Work Orders →
ERPNext Job Cards (được lập lịch bởi APS) → Production → Stock Entry →
Delivery → Phân tích thực tế so với dự báo
```

**Phương Pháp Hay Nhất**:
- Giữ dữ liệu chính ERPNext làm nguồn sự thật
- Sử dụng APS để lập kế hoạch, ERPNext để thực thi
- Đồng bộ thường xuyên (không để dữ liệu lệch)
- Sử dụng vai trò và quyền ERPNext cho quyền truy cập APS
- Tận dụng báo cáo ERPNext cho phân tích kết hợp

**Luồng Dữ Liệu**:
- **Từ ERPNext đến APS**: Items, BOMs, Sales Orders, Stock Levels, Suppliers
- **Từ APS đến ERPNext**: Thời gian đã lập lịch trong Job Cards, Đề xuất mua hàng cho POs
- **Hai chiều**: Trạng thái kế hoạch sản xuất, cập nhật work order

### Bảo Mật và Kiểm Soát Truy Cập

**Quyền Truy Cập Dựa Trên Vai Trò**:

- **System Manager**: Quyền truy cập đầy đủ, cấu hình
- **APS Manager**: Chạy dự báo, tạo kế hoạch, quản lý lịch trình
- **APS User**: Xem dự báo và lịch trình, chỉnh sửa hạn chế
- **Manufacturing User**: Chỉ xem lịch trình
- **Purchasing User**: Xem kết quả MRP và đề xuất mua hàng

**Dữ Liệu Nhạy Cảm**:
- Bảo vệ dữ liệu giá nhà cung cấp
- Kiểm soát quyền truy cập vào kết quả dự báo (thông tin cạnh tranh)
- Mã hóa OpenAI API keys
- Audit trail cho các thay đổi kế hoạch
- Sao lưu dữ liệu lập lịch thường xuyên

### Giám Sát và KPI

**Chỉ Số Chính Cần Theo Dõi**:

**Hiệu Suất Dự Báo**:
- MAPE (Phần Trăm Sai Số Tuyệt Đối Trung Bình): Mục tiêu <20%
- Bias dự báo: Nên gần 0% (không liên tục cao/thấp)
- Dự báo so với thực tế theo mặt hàng: Xác định các mặt hàng có vấn đề
- Xu hướng điểm tin cậy: Nên cải thiện theo thời gian

**Hiệu Suất Lập Kế Hoạch**:
- Tỷ lệ hoàn thành kế hoạch: % kế hoạch được hoàn thành
- Tần suất thay đổi kế hoạch: Kế hoạch được sửa đổi thường xuyên như thế nào
- Mức sử dụng công suất: Mục tiêu 75-85% (không quá cao hoặc thấp)

**Hiệu Suất MRP**:
- Tính sẵn có của vật liệu: % vật liệu đến đúng hạn
- Phương sai chi phí mua hàng: Thực tế so với nhà cung cấp được đề xuất
- Sự cố thiếu hụt: Số lần hết hàng
- Tiết kiệm tối ưu hóa nhà cung cấp: $ tiết kiệm được bằng lựa chọn tối ưu

**Hiệu Suất Lập Lịch**:
- Tỷ lệ giao hàng đúng hạn: Mục tiêu >95%
- Tuân thủ lịch trình: Hoàn thành thực tế so với đã lập lịch
- Độ trễ trung bình: Phút trễ cho mỗi công việc
- Mức sử dụng máy: Mục tiêu 75-85%
- Giảm makespan: so với phương pháp lập lịch trước đây

**Hiệu Suất RL Agent**:
- Tỷ lệ thành công điều chỉnh: % điều chỉnh RL cải thiện lịch trình
- Thời gian phản ứng: RL đề xuất giải pháp nhanh như thế nào
- Đường cong học: Cải thiện qua các tập huấn luyện

**Hiệu Suất Dự Đoán GNN**:
- Độ chính xác dự đoán nút thắt: % được xác định chính xác
- Lỗi dự đoán thời lượng: Thời gian hoạt động thực tế so với dự đoán
- Tỷ lệ dương tính giả: Nút thắt được dự đoán nhưng không xảy ra

**Khuyến Nghị Dashboard**:
- Hàng ngày: Tuân thủ lịch trình, mức sử dụng máy
- Hàng tuần: Dự báo so với doanh số thực tế, giao hàng đúng hạn
- Hàng tháng: Độ chính xác dự báo, hoàn thành kế hoạch, tiết kiệm chi phí
- Hàng quý: Xu hướng hiệu suất mô hình, cải thiện RL agent

---

## Kết Luận

UIT APS cung cấp một giải pháp toàn diện, được hỗ trợ bởi AI cho lập kế hoạch và lập lịch sản xuất. Bằng cách làm theo hướng dẫn chức năng này, bạn có thể:

- **Dự báo nhu cầu chính xác** sử dụng mô hình ML phù hợp cho dữ liệu của bạn
- **Lập kế hoạch sản xuất hiệu quả** dựa trên dự báo đáng tin cậy
- **Tối ưu hóa mua sắm vật liệu** với lựa chọn nhà cung cấp thông minh
- **Lập lịch vận hành tối ưu** sử dụng kỹ thuật AI/OR kết hợp
- **Thích ứng theo thời gian thực** khi xảy ra gián đoạn
- **Cải tiến liên tục** với thông tin chi tiết dựa trên dữ liệu

### Nhận Trợ Giúp

**Tài Liệu**:
- Architecture Guide: Chi tiết kỹ thuật hệ thống
- API Reference: Tích hợp và tự động hóa
- Functional Guide này: Cách sử dụng hệ thống

**Hỗ Trợ**:
- Kiểm tra error logs trong mỗi DocType cho các vấn đề cụ thể
- Xem xét giải thích dự báo để có thông tin chi tiết
- Sử dụng khuyến nghị GNN để hướng dẫn chiến lược
- Tham khảo cộng đồng ERPNext cho câu hỏi về ERP cơ bản

**Đào Tạo**:
- Thực hành trực tiếp với nhóm mặt hàng thí điểm
- Xem xét các quy trình làm việc mẫu trong hướng dẫn này
- Thử nghiệm với các tham số mô hình
- Bắt đầu đơn giản, thêm các tính năng nâng cao dần dần

### Các Bước Tiếp Theo

1. **Thiết lập dữ liệu chính** trong ERPNext
2. **Chạy dự báo đầu tiên** trên một nhóm mặt hàng nhỏ
3. **Xem xét kết quả dự báo** và so sánh các mô hình
4. **Tạo kế hoạch sản xuất** từ dự báo
5. **Chạy tối ưu hóa MRP** để xem đề xuất mua hàng
6. **Thử lập lịch cơ bản** với OR-Tools
7. **Bật dần RL và GNN** khi bạn đạt được sự tự tin
8. **Đo lường kết quả** so với quy trình hiện tại của bạn
9. **Lặp lại và cải thiện** dựa trên dữ liệu

Thành công với UIT APS đến từ việc sử dụng nhất quán, xem xét thường xuyên kết quả, và cải tiến liên tục quy trình lập kế hoạch của bạn. Bắt đầu đơn giản, đo lường mọi thứ, và để dữ liệu hướng dẫn các cải tiến của bạn.

---

**Phiên Bản Tài Liệu**: 1.0
**Cập Nhật Lần Cuối**: 2026-01-06
**Cho Phiên Bản UIT APS**: 1.0+
**Được Duy Trì Bởi**: thanhnc
