from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Optional, List
from datetime import datetime

class PurchaseOrderItemCreate(BaseModel):
    variant_id: int
    quantity: int = Field(..., gt=0, description="Số lượng chiếc nhập")
    unit_cost: Decimal = Field(..., ge=0, description="Giá mua sỉ 1 chiếc từ xưởng")
    packaging_cost: Decimal = Field(default=Decimal("1000.00"), ge=0, description="Phí túi zip + tem barcode riêng")


class PurchaseOrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    variant_id: int
    quantity: int
    unit_cost: Decimal
    allocated_freight: Decimal
    packaging_cost: Decimal
    landed_cost: Decimal


class PurchaseOrderCreate(BaseModel):
    po_code: str = Field(..., description="Mã phiếu nhập, vd: PO-20260911-01")
    supplier_id: int
    shipping_fee: Decimal = Field(default=Decimal("0.00"), ge=0, description="Tổng tiền cước xe tải chuyển hàng")
    other_fees: Decimal = Field(default=Decimal("0.00"), ge=0, description="Phụ phí kiểm đếm/bốc xếp")
    notes: Optional[str] = None
    items: List[PurchaseOrderItemCreate] = Field(..., min_length=1, description="Danh sách SKU nhập")


class PurchaseOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    po_code: str
    supplier_id: int
    total_merchandise_cost: Decimal
    shipping_fee: Decimal
    other_fees: Decimal
    total_quantity: int
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    items: List[PurchaseOrderItemResponse] = []
