# SETUP AI EXPLANATION CHO FORECAST MODELS

## 🤖 TONG QUAN

Tinh nang AI Explanation su dung OpenAI GPT-4o-mini de tao phan tich forecast thong minh va de hieu hon.

### Uu diem:
- ✅ Phan tich bang ngon ngu tu nhien (Tieng Viet khong dau)
- ✅ Insight sau sac hon template
- ✅ De xuat hanh dong cu the
- ✅ Phan tich tong the cho lan chay forecast

---

## 📋 BUOC 1: CAI DAT OPENAI PACKAGE

```bash
cd /path/to/frappe-bench
source env/bin/activate
pip install openai
```

---

## 📋 BUOC 2: LAY OPENAI API KEY

1. Truy cap: https://platform.openai.com/api-keys
2. Dang nhap hoac dang ky tai khoan
3. Click "Create new secret key"
4. Copy API key (bat dau bang `sk-...`)
5. **LUU Y**: Luu lai key vi chi hien thi 1 lan!

---

## 📋 BUOC 3: CAU HINH TRONG ERPNEXT

### Option 1: Qua UI

1. Vao ERPNext
2. Search "APS Chatgpt Settings"
3. Nhap API key vao field `api_key`
4. Save

### Option 2: Qua Console

```python
import frappe

# Tao hoac update settings
if not frappe.db.exists("APS Chatgpt Settings", "APS Chatgpt Settings"):
    doc = frappe.get_doc({
        "doctype": "APS Chatgpt Settings",
        "api_key": "sk-proj-your-api-key-here"
    })
    doc.insert()
else:
    doc = frappe.get_doc("APS Chatgpt Settings", "APS Chatgpt Settings")
    doc.api_key = "sk-proj-your-api-key-here"
    doc.save()

frappe.db.commit()
print("✅ API key da duoc luu!")
```

---

## 📋 BUOC 4: KIEM TRA

```python
import frappe
from uit_aps.ml.ai_explainer import is_ai_enabled, get_openai_client

# Kiem tra AI co bat khong
if is_ai_enabled():
    print("✅ AI Explanation da duoc bat!")
    
    # Test connection
    client = get_openai_client()
    if client:
        print("✅ OpenAI client ket noi thanh cong!")
    else:
        print("❌ Khong the ket noi OpenAI client")
else:
    print("❌ AI Explanation chua duoc bat. Hay kiem tra API key!")
```

---

## 🚀 SU DUNG

### Background Processing (Khong lam cham forecast!)

AI explanation chay trong **BACKGROUND JOB** nen:
- ✅ Forecast chay nhanh, khong bi cham
- ✅ AI explanation duoc xu ly sau
- ✅ Co the retry neu that bai
- ✅ Khong anh huong toi user experience

### Tu dong su dung

Sau khi setup xong, AI explanation se **TU DONG** duoc enqueue khi chay forecast:

```python
from uit_aps.uit_api.run_model import run_forecast

# Chay forecast binh thuong
result = run_forecast(
    model_name="Prophet",
    company="Your Company",
    item_code="ITEM-001",
    forecast_horizon_days=30,
    training_period_days=180
)

# Ket qua se co AI explanation trong:
# 1. APS Forecast Result -> forecast_explanation (cho moi item)
# 2. APS Forecast History -> ai_analysis (tong the lan chay)
```

### Kiem tra trang thai AI job

```python
from uit_aps.uit_api.run_model import get_ai_explanation_status

# Kiem tra status
status = get_ai_explanation_status("FCST-RUN-2025-12-22-0001")
print(status)

# Output:
# {
#   "status": "processing",  # hoac "completed", "partial", "not_started"
#   "results_processed": 15,
#   "total_results": 50
# }
```

### Retry neu that bai

```python
from uit_aps.uit_api.run_model import retry_ai_explanations

# Retry AI job
result = retry_ai_explanations("FCST-RUN-2025-12-22-0001")
print(result["message"])
```

### Xem ket qua

**Item-level explanation:**
```python
# Lay 1 forecast result (sau khi AI job hoan thanh)
result = frappe.get_doc("APS Forecast Result", "FCST-ITEM-001-2025-12-22-0001")
print(result.forecast_explanation)
```

**History-level analysis:**
```python
# Lay forecast history
history = frappe.get_doc("APS Forecast History", "FCST-RUN-2025-12-22-0001")
print(history.ai_analysis)
```

---

## 🔄 WORKFLOW

### Quy trinh Background Processing:

```
1. User chay forecast
   └─> Forecast chay va luu results (NHANH!)
   └─> Tra ket qua ngay cho user
   └─> Enqueue AI job vao background

2. Background worker xu ly
   └─> Generate AI explanation cho tung item
   └─> Generate AI analysis tong the cho history
   └─> Update records voi AI content

3. User xem ket qua
   └─> Co the xem ngay forecast results (co template explanation)
   └─> Sau vai phut, AI explanation se hien thi
   └─> Co the check status hoac retry neu can
```

### Timeline:

- **Forecast complete**: ~1-5 giay (khong doi AI)
- **AI job start**: Ngay sau khi forecast xong
- **AI job complete**: 
  - 10 items: ~30-60 giay
  - 50 items: ~2-4 phut
  - 100 items: ~5-8 phut

---

## 💰 CHI PHI

### GPT-4o-mini Pricing
- **Input**: $0.15 / 1M tokens
- **Output**: $0.60 / 1M tokens

### Uoc tinh chi phi

**Item-level explanation:**
- ~300 tokens input + ~200 tokens output
- Cost per item: ~$0.0002 (~5 VND)

**History-level analysis:**
- ~500 tokens input + ~300 tokens output
- Cost per history: ~$0.0003 (~7 VND)

**Vi du thuc te:**
- 100 items forecast = 100 * $0.0002 + 1 * $0.0003 = **$0.023** (~575 VND)
- 1000 items/thang = **~$0.23** (~5,750 VND/thang)

➡️ **KET LUAN**: Chi phi rat thap, chi khoang 5-10k VND/thang cho 1000 forecasts!

---

## 🎯 OUTPUT MAU

### Item-level Explanation

```
📊 PHAN TICH DU BAO

🎯 INSIGHT CHINH:
San pham TP-BAN-001 dang co xu huong tang truong on dinh voi nhu cau 
trung binh 5.2 don vi/ngay. Du bao 30 ngay toi la 150.5 don vi 
(khoang tin cay: 120-180 don vi), do tin cay 85%.

⚠️ RUI RO:
Ton kho hien tai (80 don vi) CHI DU cho 15 ngay. Voi lead time 14 ngay,
can dat hang NGAY de tranh het hang.

💼 DE XUAT HANH DONG:
1. 🚨 DAT HANG NGAY: 230 don vi (du cho 44 ngay + safety stock)
2. Xem xet tang safety stock len 25% do xu huong tang
3. Theo doi sat vi day la Fast Moving item
```

### History-level Analysis

```
📊 PHAN TICH TONG THE LAN CHAY DU BAO

📋 TOM TAT TONG QUAN:
Lan chay du bao "Prophet - 2025-12-22" da hoan thanh thanh cong 
45/50 items (ty le 90%). Tong nhu cau du bao cho 30 ngay toi la 
15,234 don vi.

✅ HIEU QUA MODEL:
Model Prophet dat do tin cay trung binh 82.5%, cho thay du bao 
kha chuan xac. Ty le thanh cong cao (90%) chung to du lieu 
Sales Order chat luong tot.

📈 XU HUONG CHUNG:
- 25 items (55%) dang co xu huong TANG
- 15 items (33%) on dinh
- 5 items (12%) giam
- 18 items thuoc Fast Moving, can uu tien

⚠️ CANH BAO VA UU TIEN:
CO 12 ITEMS CAN DAT HANG NGAY de tranh het hang. Trong do 8 items 
la Fast Moving, can uu tien cao nhat.

🎯 KHUYEN NGHI CHIEN LUOC:
1. Xu ly ngay 12 reorder alerts, uu tien Fast Moving items
2. Tang safety stock cho cac items co xu huong tang manh
3. Xem xet giam ton kho cac items Non Moving
4. Lap ke hoach dat hang theo batch de toi uu chi phi
```

---

## 🔧 TROUBLESHOOTING

### Loi: "OpenAI package not installed"

```bash
pip install openai
```

### Loi: "API key not found"

Kiem tra:
1. APS Chatgpt Settings da duoc tao chua
2. Field `api_key` co gia tri chua
3. API key dung format (bat dau bang `sk-`)

### AI Explanation khong hien thi

1. Kiem tra `is_ai_enabled()` return True
2. Kiem tra log errors: ERPNext > Error Log
3. Neu AI fail, he thong tu dong fallback ve template explanation

### Chi phi qua cao

1. Model GPT-4o-mini da rat re (~5-10k/thang)
2. Neu van qua cao, co the:
   - Chi bat AI cho important items
   - Giam forecast frequency
   - Cache results

---

## 📊 SO SANH TEMPLATE VS AI

| Feature | Template | AI (GPT-4o-mini) |
|---------|----------|------------------|
| **Chi phi** | Mien phi | ~5-10k VND/thang |
| **Toc do** | Instant | +1-2s/forecast |
| **Noi dung** | Co dinh | Linh hoat |
| **Insight** | Co ban | Sau sac |
| **Ngon ngu** | Technical | Tu nhien |
| **Context-aware** | ❌ | ✅ |
| **Recommendations** | Generic | Cu the |

---

## ✅ CHECKLIST HOAN THANH

- [ ] Cai dat openai package
- [ ] Lay OpenAI API key
- [ ] Tao/update APS Chatgpt Settings
- [ ] Luu API key
- [ ] Test voi `is_ai_enabled()`
- [ ] Chay forecast test
- [ ] Kiem tra AI explanation trong results
- [ ] Kiem tra AI analysis trong history

---

## 🎓 TIM HIEU THEM

### OpenAI Documentation
https://platform.openai.com/docs

### Pricing
https://openai.com/api/pricing/

### Best Practices
1. Bao mat API key (khong commit vao git)
2. Monitor usage tren OpenAI dashboard
3. Set spending limits tren OpenAI account

---

**Chuc ban thanh cong voi AI Explanation! 🚀**

