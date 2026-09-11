import sys
from decimal import Decimal
from backend.app.core.database import SessionLocal
from backend.app.services.landed_cost_service import LandedCostService
from backend.app.services.order_service import OrderService
from backend.app.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderItemCreate
from backend.app.schemas.order import OrderCreate, OrderItemCreate
from backend.app.models.product import ProductVariant

def run_tests():
    sys.stdout.reconfigure(encoding='utf-8')
    db = SessionLocal()
    print("========== 1. KIỂM THỬ KẾT NỐI VÀ DỮ LIỆU BAN ĐẦU ==========")
    v1 = db.query(ProductVariant).filter(ProductVariant.sku == "AT-OVS-DEN-M").first()
    initial_stock = v1.current_stock
    print(f"SKU: {v1.sku} | Tồn kho ban đầu: {initial_stock}")

    print("\n========== 2. KIỂM THỬ CORE ENGINE 1: INBOUND & LANDED COST ==========")
    import time
    po_code = f"PO-TEST-{int(time.time())}"
    po_in = PurchaseOrderCreate(
        po_code=po_code,
        supplier_id=1,
        shipping_fee=Decimal("600000.00"),
        other_fees=Decimal("0.00"),
        notes="Lô nhập kiểm thử phân bổ cước",
        items=[
            PurchaseOrderItemCreate(variant_id=v1.id, quantity=300, unit_cost=Decimal("70000.00"), packaging_cost=Decimal("1000.00"))
        ]
    )
    po = LandedCostService.create_purchase_order(db=db, po_in=po_in)
    po_item = po.items[0]
    expected_freight = Decimal("2000.00") # 600k / 300
    expected_landed = Decimal("73000.00") # 70k + 2k + 1k
    print(f"Phiếu nhập: {po.po_code} | Tổng số lượng: {po.total_quantity}")
    print(f"Cước phân bổ thực tế: {po_item.allocated_freight} (Kỳ vọng: {expected_freight})")
    print(f"Landed Cost thực tế: {po_item.landed_cost} (Kỳ vọng: {expected_landed})")
    assert po_item.allocated_freight == expected_freight, "Sai cước phân bổ!"
    assert po_item.landed_cost == expected_landed, "Sai Landed Cost!"
    
    db.refresh(v1)
    print(f"Tồn kho sau khi nhập PO: {v1.current_stock} (Kỳ vọng: {initial_stock + 300})")
    assert v1.current_stock == initial_stock + 300, "Tồn kho không tăng đúng!"
    print("=> Core Engine 1 (Landed Cost Allocation): PASSED!")

    print("\n========== 3. KIỂM THỬ CORE ENGINE 2: SALES FULFILLMENT & NET PROFIT ==========")
    order_sn = f"SP-TEST-{int(time.time())}"
    order_in = OrderCreate(
        order_sn=order_sn,
        platform="SHOPEE",
        gross_sales=Decimal("189000.00"),
        platform_fee=Decimal("18900.00"),
        voucher_sponsor=Decimal("10000.00"),
        shipping_fee_shop=Decimal("0.00"),
        order_status="DELIVERED",
        items=[
            OrderItemCreate(variant_id=v1.id, quantity=1, selling_price=Decimal("189000.00"), packaging_expense=Decimal("3000.00"))
        ]
    )
    order = OrderService.create_order(db=db, order_in=order_in)
    order_item = order.items[0]
    print(f"Đơn hàng: {order.order_sn} | Nền tảng: {order.platform}")
    print(f"Tiền thực nhận ví sàn: {order.net_settlement_amount}")
    print(f"COGS Snapshot đóng băng: {order_item.applied_landed_cogs} (Đúng chuẩn Landed Cost mới nhất)")
    print(f"Net Margin của item: {order_item.net_margin}")

    profitability = OrderService.get_order_profitability(db=db, order_id=order.id)
    # Net Profit = 160,100 (net settlement) - 73,000 (cogs) - 3,000 (pkg) = 84,100
    expected_profit = Decimal("84100.00")
    print(f"Lợi nhuận ròng đơn (True Net Profit): {profitability.true_net_profit} (Kỳ vọng: {expected_profit})")
    assert profitability.true_net_profit == expected_profit, "Sai Lợi nhuận Ròng!"

    db.refresh(v1)
    print(f"Tồn kho sau khi xuất đơn: {v1.current_stock} (Đã trừ 1)")
    assert v1.current_stock == initial_stock + 299, "Tồn kho không giảm đúng!"
    print("=> Core Engine 2 (COGS Snapshot & Net Profit): PASSED!")

    print("\n=======================================================")
    print("🎉 TẤT CẢ CÁC KIỂM THỬ CORE ENGINES ĐỀU ĐẠT CHUẨN 100%!")
    print("=======================================================")
    db.close()

if __name__ == "__main__":
    run_tests()
