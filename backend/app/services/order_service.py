from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from backend.app.models.order import Order, OrderItem
from backend.app.models.product import ProductVariant
from backend.app.models.purchase_order import PurchaseOrderItem
from backend.app.schemas.order import OrderCreate, OrderProfitabilityResponse

class OrderService:
    @staticmethod
    def create_order(db: Session, order_in: OrderCreate) -> Order:
        # 1. Kiểm tra trùng lặp mã đơn sàn
        existing = db.query(Order).filter(Order.order_sn == order_in.order_sn).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã đơn hàng '{order_in.order_sn}' đã tồn tại."
            )

        # 2. Tính tiền thực nhận ví sàn (Net Settlement) nếu đơn thành công
        gross = Decimal(str(order_in.gross_sales))
        fee = Decimal(str(order_in.platform_fee))
        voucher = Decimal(str(order_in.voucher_sponsor))
        ship_shop = Decimal(str(order_in.shipping_fee_shop))

        if order_in.order_status == "RETURNED":
            net_settlement = Decimal("0.00")
        else:
            net_settlement = (gross - fee - voucher - ship_shop).quantize(Decimal("0.01"))

        # 3. Tạo bản ghi Order
        db_order = Order(
            order_sn=order_in.order_sn,
            platform=order_in.platform.upper(),
            gross_sales=gross,
            platform_fee=fee,
            voucher_sponsor=voucher,
            shipping_fee_shop=ship_shop,
            net_settlement_amount=net_settlement,
            order_status=order_in.order_status,
            return_condition=order_in.return_condition,
            return_loss_cost=Decimal(str(order_in.return_loss_cost))
        )
        db.add(db_order)
        db.flush()

        # 4. Duyệt các sản phẩm trong đơn để Trừ kho & Snapshot Giá vốn (COGS Freeze)
        for item_in in order_in.items:
            variant = db.query(ProductVariant).filter(ProductVariant.id == item_in.variant_id).first()
            if not variant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy biến thể sản phẩm ID: {item_in.variant_id}"
                )

            # Kiểm tra tồn kho khả dụng
            if variant.current_stock < item_in.quantity and order_in.order_status != "RETURNED":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"SKU '{variant.sku}' không đủ tồn kho (Còn {variant.current_stock}, yêu cầu {item_in.quantity})."
                )

            # Lấy Giá vốn Landed Cost mới nhất từ lô nhập gần nhất để Snapshot
            latest_po_item = db.query(PurchaseOrderItem)\
                .filter(PurchaseOrderItem.variant_id == variant.id)\
                .order_by(desc(PurchaseOrderItem.id))\
                .first()

            if latest_po_item:
                cogs_snapshot = Decimal(str(latest_po_item.landed_cost))
            else:
                # Giá vốn dự phòng (40% giá niêm yết) nếu chưa có PO
                cogs_snapshot = (Decimal(str(variant.base_price)) * Decimal("0.4")).quantize(Decimal("0.01"))

            sell_price = Decimal(str(item_in.selling_price))
            pkg_expense = Decimal(str(item_in.packaging_expense))
            net_margin = (sell_price - cogs_snapshot - pkg_expense).quantize(Decimal("0.01"))

            # Trừ tồn kho nếu đơn xuất đi
            if order_in.order_status in ["PENDING", "SHIPPED", "DELIVERED"]:
                variant.current_stock -= item_in.quantity

            db_item = OrderItem(
                order_id=db_order.id,
                variant_id=variant.id,
                quantity=item_in.quantity,
                selling_price=sell_price,
                applied_landed_cogs=cogs_snapshot,
                packaging_expense=pkg_expense,
                net_margin=net_margin
            )
            db.add(db_item)

        db.commit()
        db.refresh(db_order)
        return db_order

    @staticmethod
    def get_all_orders(db: Session):
        return db.query(Order).order_by(Order.id.desc()).all()

    @staticmethod
    def get_order_profitability(db: Session, order_id: int) -> OrderProfitabilityResponse:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng.")

        total_cogs = sum(Decimal(str(item.applied_landed_cogs)) * Decimal(str(item.quantity)) for item in order.items)
        total_pkg = sum(Decimal(str(item.packaging_expense)) * Decimal(str(item.quantity)) for item in order.items)
        return_loss = Decimal(str(order.return_loss_cost))

        # True Net Profit Formula
        true_net_profit = (Decimal(str(order.net_settlement_amount)) - total_cogs - total_pkg - return_loss).quantize(Decimal("0.01"))

        return OrderProfitabilityResponse(
            order_id=order.id,
            order_sn=order.order_sn,
            platform=order.platform,
            order_status=order.order_status,
            gross_sales=order.gross_sales,
            platform_fee=order.platform_fee,
            net_settlement_amount=order.net_settlement_amount,
            total_cogs=total_cogs,
            total_packaging=total_pkg,
            return_loss_cost=return_loss,
            true_net_profit=true_net_profit
        )

    @staticmethod
    def process_return(db: Session, order_id: int, return_condition: str, extra_loss: Decimal = Decimal("0.00")):
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng.")

        order.order_status = "RETURNED"
        order.return_condition = return_condition.upper()
        order.net_settlement_amount = Decimal("0.00")

        total_cogs = sum(Decimal(str(item.applied_landed_cogs)) * Decimal(str(item.quantity)) for item in order.items)

        if return_condition.upper() == "INTACT":
            # Hàng nguyên vẹn: Trả lại tồn kho, chỉ mất phí ship 2 chiều + hỏng bao bì
            for item in order.items:
                item.variant.current_stock += item.quantity
            order.return_loss_cost = Decimal("35000.00") + extra_loss
        else:
            # Hàng lỗi/rách/tráo: Mất 100% giá vốn + phí xử lý
            order.return_loss_cost = total_cogs + Decimal("30000.00") + extra_loss

        db.commit()
        db.refresh(order)
        return order
