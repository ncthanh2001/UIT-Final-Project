# THIET KE APS MRP OPTIMIZATION

## 1. TONG QUAN

**APS MRP Optimization** la chuc nang tu dong tinh toan nhu cau nguyen vat lieu (NVL) dua tren Production Plan, kiem tra ton kho, va tao Purchase Suggestions voi supplier toi uu.

### 1.1. Luu do hoat dong

```
1. User chon Production Plan (status = Planned/Released)
   ↓
2. User tao MRP Run va click "Run MRP Optimization"
   ↓
3. System:
   - Lay tat ca items trong Production Plan
   - Voi moi item, kiem tra co BOM khong
   - Neu co BOM, lay exploded BOM items (bao gom sub-assemblies)
   - Tinh toan tong NVL can thiet
   - Kiem tra ton kho hien tai
   - Tinh shortage qty
   - Tim supplier toi uu (gia + lead time)
   - Tao MRP Results
   - Tao Purchase Suggestions voi supplier toi uu
   ↓
4. User review Purchase Suggestions va approve/order
```

## 2. CAU TRUC FILE

### 2.1. Files da tao

```
apps/uit_aps/uit_aps/
├── utils/
│   └── mrp_helper.py              ← TAO MOI: Helper functions
├── uit_api/
│   └── mrp_optimization.py        ← TAO MOI: API methods
└── uit_aps/doctype/aps_mrp_run/
    ├── aps_mrp_run.py             ← SUA: Validate logic
    └── aps_mrp_run.js             ← SUA: UI handlers
```

### 2.2. Helper Functions (`mrp_helper.py`)

- `get_bom_for_item()`: Lay BOM cho item
- `get_exploded_bom_items()`: Lay tat ca items trong BOM (exploded)
- `get_current_stock()`: Lay ton kho hien tai
- `get_optimal_supplier()`: Tim supplier toi uu (gia + lead time)
- `get_supplier_price()`: Lay gia tu supplier
- `get_supplier_lead_time()`: Lay lead time tu supplier
- `calculate_required_date()`: Tinh ngay can co NVL
- `aggregate_material_requirements()``: Tong hop nhu cau NVL

### 2.3. API Methods (`mrp_optimization.py`)

- `run_mrp_optimization()`: Chay MRP Optimization

## 3. LOGIC TINH TOAN

### 3.1. BOM Explosion

- Lay BOM cua item (default BOM hoac active BOM)
- Explode BOM de lay tat ca NVL (bao gom sub-assemblies)
- Tinh so luong NVL can thiet = BOM qty * Production Plan qty

### 3.2. Material Requirements Calculation

```python
# Voi moi item trong Production Plan:
for plan_item in production_plan.items:
    bom_items = get_exploded_bom_items(bom_name, plan_item.planned_qty)
    
    for bom_item in bom_items:
        material_qty = bom_item.qty
        current_stock = get_current_stock(material_item)
        shortage_qty = max(0, material_qty - current_stock)
        
        if shortage_qty > 0:
            # Add to material requirements
```

### 3.3. Supplier Optimization

Supplier duoc danh gia theo:
- **Gia** (weight: 60%): Gia thap hon = tot hon
- **Lead Time** (weight: 40%): Lead time ngan hon = tot hon

```python
score = (price_score * 0.6) + (lead_time_score * 0.4)
```

Nguon lay gia:
1. Item Price (supplier-specific)
2. Supplier Quotation (gan day nhat)
3. Item.last_purchase_rate

Nguon lay lead time:
1. Item Supplier.lead_time_days
2. Supplier Quotation Item.lead_time_days
3. Item.lead_time_days
4. Default: 7 days

### 3.4. Required Date Calculation

```python
required_date = planned_start_date - lead_time - buffer_days
```

## 4. CACH SU DUNG

### 4.1. Qua UI

1. Tao Production Plan va submit (status = Planned)
2. Tao MRP Run moi
3. Chon Production Plan
4. Click button **"Run MRP Optimization"**
5. System se:
   - Tinh toan NVL can thiet
   - Tao MRP Results
   - Tao Purchase Suggestions voi supplier toi uu
6. Review Purchase Suggestions
7. Approve hoac tao Purchase Order

### 4.2. Qua API

```python
import frappe
from uit_aps.uit_api.mrp_optimization import run_mrp_optimization

result = run_mrp_optimization(
    production_plan="PROD-PLAN-2025-01-15-0001",
    buffer_days=0,
    include_non_stock_items=False
)

print(result)
# {
#     "success": True,
#     "mrp_run": "MRP-RUN-2025-01-15-0001",
#     "mrp_results_created": 25,
#     "purchase_suggestions_created": 18,
#     "total_materials": 25
# }
```

## 5. OUTPUT

### 5.1. APS MRP Result

- `material_item`: NVL
- `required_qty`: Tong nhu cau
- `available_qty`: Ton kho hien tai
- `shortage_qty`: So luong thieu
- `required_date`: Ngay can co

### 5.2. APS Purchase Suggestion

- `material_item`: NVL can mua
- `purchase_qty`: So luong can mua
- `required_date`: Ngay can co
- `supplier`: Supplier toi uu (duoc chon tu dong)
- `unit_price`: Gia don vi (tu supplier)
- `lead_time`: Lead time (tu supplier)
- `suggestion_status`: Draft/Approved/Ordered/Rejected

## 6. TINH NANG TOI UU

### 6.1. Supplier Selection

- Tu dong chon supplier toi uu dua tren:
  - Gia (60% weight)
  - Lead time (40% weight)
- Neu khong co supplier, de trong (user co the chon sau)

### 6.2. Time Optimization

- Tinh `required_date` dua tren:
  - `planned_start_date` cua Production Plan Item
  - `lead_time` cua supplier
  - `buffer_days` (neu co)

### 6.3. Cost Optimization

- Tinh tong chi phi cho moi Purchase Suggestion
- Co the so sanh giua cac suppliers

## 7. VALIDATION

### 7.1. MRP Run Level

- Production Plan phai co status = "Planned" hoac "Released"
- Production Plan phai co items

### 7.2. BOM Requirements

- Item phai co BOM (neu khong co BOM thi bo qua)
- BOM phai active va docstatus = 1

## 8. NOTES

- MRP Optimization chi tinh cho items co BOM
- Non-stock items co the duoc bao gom neu `include_non_stock_items = True`
- Purchase Suggestions chi duoc tao cho NVL co shortage
- Supplier optimization dua tren thong tin hien co (Item Price, Supplier Quotation, Item Supplier)
- Neu khong co supplier nao, Purchase Suggestion se khong co supplier (user chon sau)

## 9. TINH NANG MO RONG (TODO)

### 9.1. Advanced Supplier Selection

- Tich hop voi Supplier Performance (on-time delivery, quality)
- Tich hop voi Supplier Rating
- Consider minimum order quantity (MOQ)

### 9.2. Multi-Supplier Optimization

- Chia nho order giua nhieu suppliers
- Optimize theo total cost (gia + shipping)

### 9.3. Inventory Optimization

- Consider safety stock
- Consider reorder level
- Consider economic order quantity (EOQ)

### 9.4. Integration

- Tu dong tao Purchase Order tu Purchase Suggestions
- Integration voi Supplier Quotation
- Integration voi Purchase Order workflow

