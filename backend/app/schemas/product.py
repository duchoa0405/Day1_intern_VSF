from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional, List
from datetime import datetime

class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    description: Optional[str] = None


class ProductVariantBase(BaseModel):
    sku: str
    color: str
    size: str
    barcode: str
    base_price: Decimal
    current_stock: int


class ProductVariantResponse(ProductVariantBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    created_at: Optional[datetime] = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_code: str
    name: str
    material: Optional[str] = None
    description: Optional[str] = None
    variants: List[ProductVariantResponse] = []
