from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Optional, List
from datetime import datetime

class OrderItemCreate(BaseModel):
    variant_id: int
    quantity: int = Field(..., gt=0, description="Số lượng chiếc mua")
    selling_price: Decimal = Field(..., ge=0, description="Giá bán thực tế cho khách/chiếc")
    packaging_expense: Decimal = Field(default=Decimal("3000.00"), ge=0, description="Chi phí túi gói hàng và băng dính lúc gửi đi")


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    variant_id: int
    quantity: int
    selling_price: Decimal
    applied_landed_cogs: Decimal
    packaging_expense: Decimal
    net_margin: Decimal


class OrderCreate(BaseModel):
    order_sn: str = Field(..., description="Mã đơn hàng sàn, vd: TT-998811 hoặc SP-112233")
    platform: str = Field(..., description="TIKTOK | SHOPEE | FACEBOOK | OFFLINE")
    gross_sales: Decimal = Field(..., ge=0, description="Tổng tiền khách thanh toán")
    platform_fee: Decimal = Field(default=Decimal("0.00"), ge=0, description="Tổng phí sàn trừ ngầm")
    voucher_sponsor: Decimal = Field(default=Decimal("0.00"), ge=0, description="Voucher shop tài trợ")
    shipping_fee_shop: Decimal = Field(default=Decimal("0.00"), ge=0, description="Phí ship shop bù")
    order_status: str = Field(default="DELIVERED", description="DELIVERED | RETURNED | PENDING | CANCELLED")
    return_condition: Optional[str] = Field(default="NONE", description="NONE | INTACT | DAMAGED")
    return_loss_cost: Decimal = Field(default=Decimal("0.00"), ge=0, description="Chi phí tổn thất do hoàn hàng")
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Danh sách sản phẩm trong đơn")


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_sn: str
    platform: str
    gross_sales: Decimal
    platform_fee: Decimal
    net_settlement_amount: Decimal
    order_status: str
    return_condition: Optional[str]
    return_loss_cost: Decimal
    order_date: Optional[datetime] = None
    items: List[OrderItemResponse] = []


class OrderProfitabilityResponse(BaseModel):
    order_id: int
    order_sn: str
    platform: str
    order_status: str
    gross_sales: Decimal
    platform_fee: Decimal
    net_settlement_amount: Decimal
    total_cogs: Decimal
    total_packaging: Decimal
    return_loss_cost: Decimal
    true_net_profit: Decimal
