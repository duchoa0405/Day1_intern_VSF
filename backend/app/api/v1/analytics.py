from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from typing import List, Dict, Any
from backend.app.core.database import get_db

router = APIRouter()

@router.get("/summary", summary="Báo cáo Tổng hợp Tài chính & Lãi Ròng Thực Tế (P&L Dashboard)")
def get_financial_summary(db: Session = Depends(get_db)):
    """
    Truy vấn View tài chính tính toán tổng hợp toàn bộ các chỉ số P&L:
    - Tổng Doanh Thu Sàn
    - Tổng Phí Sàn Đã Bị Trừ
    - Tiền Thực Nhận Ví Sàn
    - Tổng Giá Vốn Đã Xuất (COGS)
    - Tổng Chi Phí Bao Bì Đóng Hàng
    - Tổng Tổn Thất Hàng Hoàn
    - LỢI NHUẬN RÒNG THỰC TẾ (True Net Profit)
    """
    query = text("""
        SELECT 
            COALESCE(SUM(gross_sales), 0) AS total_gross_sales,
            COALESCE(SUM(platform_fee), 0) AS total_platform_fee,
            COALESCE(SUM(net_settlement_amount), 0) AS total_settlement,
            COALESCE(SUM(total_cogs), 0) AS total_cogs,
            COALESCE(SUM(total_packaging), 0) AS total_packaging,
            COALESCE(SUM(return_loss_cost), 0) AS total_return_loss,
            COALESCE(SUM(true_net_profit), 0) AS total_net_profit
        FROM view_order_profitability;
    """)
    row = db.execute(query).mappings().first()

    gross = Decimal(str(row["total_gross_sales"]))
    net_profit = Decimal(str(row["total_net_profit"]))
    net_margin_pct = ((net_profit / gross) * 100).quantize(Decimal("0.1")) if gross > 0 else Decimal("0.0")

    return {
        "total_gross_sales": row["total_gross_sales"],
        "total_platform_fee": row["total_platform_fee"],
        "total_settlement": row["total_settlement"],
        "total_cogs": row["total_cogs"],
        "total_packaging": row["total_packaging"],
        "total_return_loss": row["total_return_loss"],
        "total_net_profit": row["total_net_profit"],
        "net_profit_margin_percent": float(net_margin_pct)
    }

@router.get("/by-platform", summary="So sánh Hiệu Quả Lợi Nhuận Đa Kênh (TikTok Shop vs Shopee vs FB)")
def get_profit_by_platform(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    query = text("""
        SELECT 
            platform,
            COUNT(order_id) AS total_orders,
            COALESCE(SUM(gross_sales), 0) AS platform_gross,
            COALESCE(SUM(platform_fee), 0) AS platform_fees,
            COALESCE(SUM(total_cogs), 0) AS platform_cogs,
            COALESCE(SUM(true_net_profit), 0) AS platform_net_profit
        FROM view_order_profitability
        GROUP BY platform;
    """)
    rows = db.execute(query).mappings().all()
    return [dict(r) for r in rows]

@router.get("/deadstock-alert", summary="Cảnh báo Tồn Kho Lâu Ngày (Deadstock Intelligence)")
def get_deadstock_alerts(db: Session = Depends(get_db)):
    """
    Phát hiện các mẫu / size có số lượng tồn kho còn nhiều nhưng không phát sinh đơn bán
    để kịp thời chạy chương trình Flash Sale xả lỗ, thu hồi vốn cho mẫu mới.
    """
    query = text("""
        SELECT 
            pv.id,
            p.name AS product_name,
            pv.sku,
            pv.color,
            pv.size,
            pv.current_stock,
            pv.base_price,
            (pv.current_stock * pv.base_price) AS capital_stuck_value
        FROM product_variants pv
        JOIN products p ON pv.product_id = p.id
        WHERE pv.current_stock > 100
        ORDER BY pv.current_stock DESC;
    """)
    rows = db.execute(query).mappings().all()
    return [dict(r) for r in rows]
