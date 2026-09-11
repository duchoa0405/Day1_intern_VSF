from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.models.product import Product, ProductVariant
from backend.app.schemas.product import ProductResponse, ProductVariantResponse

router = APIRouter()

@router.get("/variants", response_model=List[ProductVariantResponse], summary="Lấy danh sách biến thể SKU, mã Barcode và Tồn kho")
def get_variants(db: Session = Depends(get_db)):
    return db.query(ProductVariant).all()

@router.get("/products", response_model=List[ProductResponse], summary="Lấy danh sách sản phẩm và các biến thể")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()
