from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.models.product import Product, ProductVariant
from backend.app.schemas.product import ProductResponse, ProductVariantResponse, ProductVariantCreate

router = APIRouter()

@router.get("/variants", response_model=List[ProductVariantResponse], summary="Lấy danh sách biến thể SKU, mã Barcode và Tồn kho")
def get_variants(db: Session = Depends(get_db)):
    return db.query(ProductVariant).all()

@router.get("/products", response_model=List[ProductResponse], summary="Lấy danh sách sản phẩm và các biến thể")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@router.post("/variants", response_model=ProductVariantResponse, summary="Thêm biến thể SKU mới vào hệ thống")
def create_variant(variant_in: ProductVariantCreate, db: Session = Depends(get_db)):
    # 1. Kiểm tra mã SKU đã tồn tại chưa
    existing_variant = db.query(ProductVariant).filter(ProductVariant.sku == variant_in.sku).first()
    if existing_variant:
        return existing_variant

    # 2. Tìm hoặc tạo sản phẩm cha
    product = db.query(Product).filter(Product.name == variant_in.product_name).first()
    if not product:
        import re
        code_slug = "PROD-" + re.sub(r'[^A-Za-z0-9]+', '-', variant_in.product_name).strip('-').upper()[:20]
        product = Product(
            category_id=1,
            product_code=code_slug,
            name=variant_in.product_name,
            material=variant_in.material or "Cotton Blend",
            description=f"Sản phẩm {variant_in.product_name}"
        )
        db.add(product)
        db.flush()

    # 3. Tạo barcode ngẫu nhiên nếu không có
    import time
    barcode = variant_in.barcode or f"893{int(time.time()) % 1000000000:09d}"

    # 4. Tạo ProductVariant
    new_variant = ProductVariant(
        product_id=product.id,
        sku=variant_in.sku,
        color=variant_in.color or "Standard",
        size=variant_in.size,
        barcode=barcode,
        base_price=variant_in.base_price,
        current_stock=variant_in.initial_stock
    )
    db.add(new_variant)
    db.commit()
    db.refresh(new_variant)
    return new_variant
