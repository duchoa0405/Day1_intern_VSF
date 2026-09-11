from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from backend.app.core.database import get_db
from backend.app.schemas.order import OrderCreate, OrderResponse, OrderProfitabilityResponse
from backend.app.services.order_service import OrderService

router = APIRouter()

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo Đơn Bán Mới & Tự Động Snapshot Giá Vốn (COGS Freeze Engine)"
)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)):
    """
    **Nghiệp vụ cốt lõi:**
    - Trừ tồn kho biến thể SKU tương ứng.
    - Lấy Landed Cost mới nhất của từng SKU để **đóng băng (snapshot)** vào đơn hàng.
    - Tự động trừ các loại phí sàn (Shopee/TikTok).
    - Tính lãi ròng từng sản phẩm và lưu lại lịch sử.
    """
    return OrderService.create_order(db=db, order_in=order_in)

@router.get(
    "",
    response_model=List[OrderResponse],
    summary="Lấy danh sách tất cả các đơn hàng bán"
)
def get_all_orders(db: Session = Depends(get_db)):
    return OrderService.get_all_orders(db=db)

@router.get(
    "/{id}/profitability",
    response_model=OrderProfitabilityResponse,
    summary="Xem báo cáo bóc tách Lãi/Lỗ ròng (True Net Profit) của đơn hàng"
)
def get_order_profitability(id: int, db: Session = Depends(get_db)):
    return OrderService.get_order_profitability(db=db, order_id=id)

@router.patch(
    "/{id}/return",
    response_model=OrderResponse,
    summary="Xử lý Hàng Hoàn & Hạch toán Tổn thất (Return Loss Accounting)"
)
def process_order_return(
    id: int,
    condition: str = Query(..., description="INTACT (Nguyên vẹn) hoặc DAMAGED (Hàng rách/hỏng/bị tráo)"),
    extra_loss: Decimal = Query(Decimal("0.00"), description="Chi phí phát sinh thêm (nếu có)"),
    db: Session = Depends(get_db)
):
    return OrderService.process_return(db=db, order_id=id, return_condition=condition, extra_loss=extra_loss)
