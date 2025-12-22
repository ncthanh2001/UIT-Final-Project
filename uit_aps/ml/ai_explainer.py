# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

"""
AI Explainer Module
Su dung OpenAI de tao phan tich forecast thong minh
"""

import frappe
import json


def is_ai_enabled():
    """Kiem tra xem AI explanation co duoc bat khong"""
    try:
        # Check if APS Chatgpt Settings exists and has API key
        if frappe.db.exists("APS Chatgpt Settings", "APS Chatgpt Settings"):
            api_key = frappe.db.get_single_value("APS Chatgpt Settings", "api_key")
            return bool(api_key)
        return False
    except Exception:
        return False


def get_openai_client():
    """Lay OpenAI client"""
    try:
        from openai import OpenAI
        
        api_key = frappe.db.get_single_value("APS Chatgpt Settings", "api_key")
        if not api_key:
            return None
            
        return OpenAI(api_key=api_key)
    except ImportError:
        frappe.log_error("OpenAI package not installed. Run: pip install openai")
        return None
    except Exception as e:
        frappe.log_error(f"Failed to create OpenAI client: {str(e)}")
        return None


def generate_item_forecast_explanation(forecast_data, item_code, model_name):
    """
    Tao AI explanation cho forecast cua 1 item cu the
    
    Args:
        forecast_data: Dict chua tat ca metrics
        item_code: Item code
        model_name: Model name
        
    Returns:
        str: AI-generated explanation hoac template fallback
    """
    if not is_ai_enabled():
        return None  # Se dung template explanation tu model
    
    client = get_openai_client()
    if not client:
        return None
    
    try:
        prompt = create_item_forecast_prompt(forecast_data, item_code, model_name)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Ban la mot chuyen gia phan tich supply chain va du bao.
Nhiem vu cua ban la phan tich ket qua du bao va dua ra insights, danh gia rui ro,
va de xuat hanh dong cu the. Viet bang TIENG VIET KHONG DAU, ngan gon, de hieu."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        frappe.log_error(f"AI explanation failed for {item_code}: {str(e)}")
        return None


def create_item_forecast_prompt(forecast_data, item_code, model_name):
    """Tao prompt cho phan tich forecast cua 1 item"""
    
    reorder_status = "CO - CAN DAT HANG NGAY!" if forecast_data.get('reorder_alert') else "KHONG"
    
    prompt = f"""
Phan tich ket qua du bao sau va dua ra explanation:

THONG TIN SAN PHAM:
- Ma san pham: {item_code}
- Model su dung: {model_name}

DU LIEU DU BAO:
- Du bao 30 ngay: {forecast_data.get('forecast_qty', 0):.1f} don vi
- Do tin cay: {forecast_data.get('confidence_score', 0):.1f}%
- Khoang tin cay: [{forecast_data.get('lower_bound', 0):.1f}, {forecast_data.get('upper_bound', 0):.1f}]
- Xu huong: {forecast_data.get('trend_type', 'Stable')}
- Phan loai: {forecast_data.get('movement_type', 'Unknown')}
- Tieu thu TB hang ngay: {forecast_data.get('daily_avg_consumption', 0):.2f} don vi/ngay
- Du lieu training: {forecast_data.get('training_data_points', 0)} ngay

THONG TIN TON KHO:
- Ton kho hien tai: {forecast_data.get('current_stock', 0):.1f} don vi
- Muc dat hang lai: {forecast_data.get('reorder_level', 0):.1f} don vi
- Ton kho an toan: {forecast_data.get('safety_stock', 0):.1f} don vi
- De xuat dat hang: {forecast_data.get('suggested_qty', 0)} don vi
- Canh bao dat hang: {reorder_status}

YEU CAU OUTPUT (VIET TIENG VIET KHONG DAU):
1. Insight chinh (2-3 cau ngan gon)
2. Danh gia rui ro neu co (1-2 cau)
3. De xuat hanh dong cu the (2-3 diem)
4. Su dung emoji phu hop
5. NEU co reorder alert, NHAN MANH can dat hang ngay

Format:
📊 PHAN TICH DU BAO

🎯 INSIGHT CHINH:
[Phan tich ngan gon]

⚠️ RUI RO:
[Rui ro neu co, hoac viet "Khong co rui ro dang ke"]

💼 DE XUAT HANH DONG:
1. [Hanh dong 1]
2. [Hanh dong 2]
"""
    return prompt


def generate_history_analysis(history_doc):
    """
    Tao AI analysis tong the cho lan chay forecast (APS Forecast History)
    
    Args:
        history_doc: APS Forecast History document
        
    Returns:
        str: AI-generated overall analysis
    """
    if not is_ai_enabled():
        return generate_default_history_analysis(history_doc)
    
    client = get_openai_client()
    if not client:
        return generate_default_history_analysis(history_doc)
    
    try:
        # Get summary statistics from forecast results
        results_summary = get_results_summary(history_doc.name)
        
        prompt = create_history_analysis_prompt(history_doc, results_summary)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Ban la mot chuyen gia quan ly supply chain va inventory.
Nhiem vu cua ban la phan tich tong the ket qua du bao cho tat ca san pham,
danh gia hieu qua cua model, va dua ra khuyen nghi chien luoc.
Viet bang TIENG VIET KHONG DAU, chuyen nghiep nhung de hieu."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        frappe.log_error(f"AI history analysis failed: {str(e)}")
        return generate_default_history_analysis(history_doc)


def get_results_summary(history_name):
    """Lay thong ke tong hop tu forecast results"""
    
    results = frappe.get_all(
        "APS Forecast Result",
        filters={"forecast_history": history_name},
        fields=[
            "forecast_qty",
            "confidence_score",
            "movement_type",
            "trend_type",
            "reorder_alert",
            "model_used"
        ]
    )
    
    if not results:
        return {}
    
    # Calculate statistics
    total_forecast = sum(r.get('forecast_qty', 0) for r in results)
    avg_confidence = sum(r.get('confidence_score', 0) for r in results) / len(results)
    
    reorder_items = sum(1 for r in results if r.get('reorder_alert'))
    
    movement_counts = {}
    trend_counts = {}
    
    for r in results:
        movement = r.get('movement_type', 'Unknown')
        trend = r.get('trend_type', 'Stable')
        
        movement_counts[movement] = movement_counts.get(movement, 0) + 1
        trend_counts[trend] = trend_counts.get(trend, 0) + 1
    
    return {
        "total_items": len(results),
        "total_forecast_qty": total_forecast,
        "avg_confidence": avg_confidence,
        "reorder_items_count": reorder_items,
        "movement_breakdown": movement_counts,
        "trend_breakdown": trend_counts
    }


def create_history_analysis_prompt(history_doc, results_summary):
    """Tao prompt cho phan tich tong the history"""
    
    prompt = f"""
Phan tich tong the lan chay du bao sau:

THONG TIN CHUNG:
- Ten lan chay: {history_doc.run_name}
- Model su dung: {history_doc.model_used}
- Thoi gian chay: {history_doc.run_start_time} den {history_doc.run_end_time}
- Trang thai: {history_doc.run_status}

KET QUA TONG HOP:
- Tong so items du bao: {results_summary.get('total_items', 0)}
- Thanh cong: {history_doc.successful_forecasts or 0}
- That bai: {history_doc.failed_forecasts or 0}
- Do tin cay trung binh: {results_summary.get('avg_confidence', 0):.1f}%

PHAN TICH CHI TIET:
- Tong nhu cau du bao: {results_summary.get('total_forecast_qty', 0):.1f} don vi
- So items CAN DAT HANG: {results_summary.get('reorder_items_count', 0)} items
- Phan loai Movement: {json.dumps(results_summary.get('movement_breakdown', {}), ensure_ascii=False)}
- Phan loai Trend: {json.dumps(results_summary.get('trend_breakdown', {}), ensure_ascii=False)}

DU LIEU TRAINING:
- Tu ngay: {history_doc.training_period_start}
- Den ngay: {history_doc.training_period_end}
- Horizon du bao: {history_doc.forecast_horizon_days} ngay

YEU CAU OUTPUT (VIET TIENG VIET KHONG DAU):
1. Tom tat tong quan (2-3 cau)
2. Danh gia hieu qua model (1-2 cau)
3. Phan tich xu huong chung (2-3 cau)
4. Canh bao va uu tien (neu co items can reorder)
5. Khuyen nghi hanh dong chien luoc (3-4 diem)
6. Su dung emoji phu hop

Format:
📊 PHAN TICH TONG THE LAN CHAY DU BAO

📋 TOM TAT TONG QUAN:
[Tom tat ngan gon]

✅ HIEU QUA MODEL:
[Danh gia model]

📈 XU HUONG CHUNG:
[Phan tich xu huong]

⚠️ CANH BAO VA UU TIEN:
[Cac van de can chu y]

🎯 KHUYEN NGHI CHIEN LUOC:
1. [Khuyen nghi 1]
2. [Khuyen nghi 2]
3. [Khuyen nghi 3]
"""
    return prompt


def generate_default_history_analysis(history_doc):
    """Tao phan tich mac dinh neu AI khong available"""
    
    results_summary = get_results_summary(history_doc.name)
    
    analysis = f"""📊 PHAN TICH TONG THE LAN CHAY DU BAO

📋 TOM TAT TONG QUAN:
Lan chay du bao "{history_doc.run_name}" da hoan thanh voi {history_doc.successful_forecasts or 0} items thanh cong 
va {history_doc.failed_forecasts or 0} items that bai. Model {history_doc.model_used} da duoc su dung de du bao 
{history_doc.forecast_horizon_days} ngay toi.

✅ HIEU QUA MODEL:
Do tin cay trung binh dat {results_summary.get('avg_confidence', 0):.1f}%. 
Ty le thanh cong: {(history_doc.successful_forecasts or 0) / max(1, results_summary.get('total_items', 1)) * 100:.1f}%

📈 THONG KE:
- Tong items: {results_summary.get('total_items', 0)}
- Can dat hang: {results_summary.get('reorder_items_count', 0)} items
- Tong nhu cau: {results_summary.get('total_forecast_qty', 0):.1f} don vi

⚠️ CANH BAO:
{"Co " + str(results_summary.get('reorder_items_count', 0)) + " items can dat hang ngay!" if results_summary.get('reorder_items_count', 0) > 0 else "Khong co items can dat hang khan cap"}

🎯 KHUYEN NGHI:
1. Kiem tra cac items co reorder alert
2. Lap ke hoach dat hang cho cac items Fast Moving
3. Theo doi do chinh xac cua forecast trong thoi gian toi
"""
    
    return analysis

