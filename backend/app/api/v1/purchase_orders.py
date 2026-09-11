from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderResponse
from backend.app.services.landed_cost_service import LandedCostService

router = APIRouter()

@router.post(
    "",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo Phiếu Nhập Hàng & Tự Động Phân Bổ Landed Cost (Inbound Engine)"
)
def create_purchase_order(po_in: PurchaseOrderCreate, db: Session = Depends(get_db)):
    """
    **Nghiệp vụ cốt lõi:**
    - Nhận danh sách SKU nhập từ nhà cung cấp.
    - Nhập tiền hàng, tiền xe cước kiện chuyển về kho.
    - Hệ thống tự động chia đều cước xe vào đơn giá từng chiếc áo.
    - Tự động tăng số lượng tồn kho khả dụng của từng biến thể SKU.
    """
    return LandedCostService.create_purchase_order(db=db, po_in=po_in)

@router.get(
    "",
    response_model=List[PurchaseOrderResponse],
    summary="Lấy danh sách các Phiếu Nhập Hàng (PO)"
)
def get_all_purchase_orders(db: Session = Depends(get_db)):
    return LandedCostService.get_all_purchase_orders(db=db)

@router.get(
    "/{id}",
    response_model=PurchaseOrderResponse,
    summary="Xem chi tiết Phiếu Nhập & Bảng phân bổ Landed Cost"
)
def get_purchase_order(id: int, db: Session = Depends(get_db)):
    return LandedCostService.get_purchase_order_by_id(db=db, po_id=id)
