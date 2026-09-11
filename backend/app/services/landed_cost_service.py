from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from backend.app.models.product import ProductVariant
from backend.app.schemas.purchase_order import PurchaseOrderCreate

class LandedCostService:
    @staticmethod
    def create_purchase_order(db: Session, po_in: PurchaseOrderCreate) -> PurchaseOrder:
        # 1. Kiểm tra xem mã PO đã tồn tại chưa
        existing_po = db.query(PurchaseOrder).filter(PurchaseOrder.po_code == po_in.po_code).first()
        if existing_po:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã phiếu nhập '{po_in.po_code}' đã tồn tại trong hệ thống."
            )

        # 2. Tính tổng số lượng hàng trong toàn bộ lô nhập
        total_quantity = sum(item.quantity for item in po_in.items)
        if total_quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tổng số lượng hàng nhập phải lớn hơn 0."
            )

        # 3. Phân bổ chi phí phụ (Cước vận chuyển kiện + Phí khác) cho từng sản phẩm
        total_freight_pool = Decimal(str(po_in.shipping_fee)) + Decimal(str(po_in.other_fees))
        allocated_freight_per_unit = (total_freight_pool / Decimal(str(total_quantity))).quantize(Decimal("0.01"))

        # 4. Tính tổng tiền hàng sỉ
        total_merchandise_cost = Decimal("0.00")

        # 5. Tạo đối tượng PurchaseOrder
        db_po = PurchaseOrder(
            po_code=po_in.po_code,
            supplier_id=po_in.supplier_id,
            shipping_fee=po_in.shipping_fee,
            other_fees=po_in.other_fees,
            total_quantity=total_quantity,
            status="RECEIVED",
            notes=po_in.notes
        )
        db.add(db_po)
        db.flush() # Lấy db_po.id

        # 6. Duyệt từng SKU để tính Landed Cost và cập nhật Tồn kho
        for item_in in po_in.items:
            variant = db.query(ProductVariant).filter(ProductVariant.id == item_in.variant_id).first()
            if not variant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy biến thể sản phẩm có ID: {item_in.variant_id}"
                )

            unit_cost = Decimal(str(item_in.unit_cost))
            pkg_cost = Decimal(str(item_in.packaging_cost))
            
            # Landed Cost = Giá sỉ + Cước phân bổ + Bao bì tem mác
            landed_cost = (unit_cost + allocated_freight_per_unit + pkg_cost).quantize(Decimal("0.01"))
            total_merchandise_cost += unit_cost * Decimal(str(item_in.quantity))

            po_item = PurchaseOrderItem(
                po_id=db_po.id,
                variant_id=variant.id,
                quantity=item_in.quantity,
                unit_cost=unit_cost,
                allocated_freight=allocated_freight_per_unit,
                packaging_cost=pkg_cost,
                landed_cost=landed_cost
            )
            db.add(po_item)

            # Tự động tăng tồn kho khả dụng của biến thể
            variant.current_stock += item_in.quantity

        db_po.total_merchandise_cost = total_merchandise_cost
        db.commit()
        db.refresh(db_po)
        return db_po

    @staticmethod
    def get_all_purchase_orders(db: Session):
        return db.query(PurchaseOrder).order_by(PurchaseOrder.id.desc()).all()

    @staticmethod
    def get_purchase_order_by_id(db: Session, po_id: int):
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if not po:
            raise HTTPException(status_code=404, detail="Không tìm thấy phiếu nhập hàng.")
        return po
