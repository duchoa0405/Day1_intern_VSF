from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_sn = Column(String(100), unique=True, nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    gross_sales = Column(Numeric(15, 2), nullable=False, default=0.00)
    platform_fee = Column(Numeric(15, 2), nullable=False, default=0.00)
    voucher_sponsor = Column(Numeric(15, 2), nullable=False, default=0.00)
    shipping_fee_shop = Column(Numeric(15, 2), nullable=False, default=0.00)
    net_settlement_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    order_status = Column(String(50), nullable=False, default="DELIVERED")
    return_condition = Column(String(30), nullable=True, default="NONE")
    return_loss_cost = Column(Numeric(15, 2), nullable=False, default=0.00)
    order_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    settlement_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False)
    selling_price = Column(Numeric(15, 2), nullable=False)
    applied_landed_cogs = Column(Numeric(15, 2), nullable=False, default=0.00)
    packaging_expense = Column(Numeric(15, 2), nullable=False, default=0.00)
    net_margin = Column(Numeric(15, 2), nullable=False, default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="items")
    variant = relationship("ProductVariant", back_populates="order_items")
