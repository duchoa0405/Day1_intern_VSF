-- ==============================================================================
-- FashionRev-Ops: Database Schema (PostgreSQL 16)
-- Domain: Fast-Fashion E-commerce Revenue & Landed Cost Management
-- ==============================================================================

-- Bật extension UUID nếu cần
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. BẢNG DANH MỤC SẢN PHẨM (Categories)
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. BẢNG SẢN PHẨM CHA (Products)
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    category_id INT REFERENCES categories(id) ON DELETE RESTRICT,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    material VARCHAR(100), -- Ví dụ: Cotton 100%, Lụa Hàn, Jean co giãn
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. BẢNG BIẾN THỂ SẢN PHẨM (Product Variants - SKU & Barcode)
CREATE TABLE IF NOT EXISTS product_variants (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sku VARCHAR(100) NOT NULL UNIQUE, -- VD: AT-OVS-DEN-L (Áo thun oversize đen size L)
    color VARCHAR(50) NOT NULL,
    size VARCHAR(20) NOT NULL,
    barcode VARCHAR(100) NOT NULL UNIQUE, -- Mã vạch dán túi zip
    base_price DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Giá niêm yết bán lẻ
    current_stock INT NOT NULL DEFAULT 0 CHECK (current_stock >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. BẢNG NHÀ CUNG CẤP / XƯỞNG MAY (Suppliers)
CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. BẢNG PHIẾU NHẬP HÀNG (Purchase Orders - PO)
CREATE TABLE IF NOT EXISTS purchase_orders (
    id SERIAL PRIMARY KEY,
    po_code VARCHAR(50) NOT NULL UNIQUE, -- VD: PO-20260911-001
    supplier_id INT NOT NULL REFERENCES suppliers(id) ON DELETE RESTRICT,
    total_merchandise_cost DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Tổng tiền hàng sỉ
    shipping_fee DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Tiền xe cước kiện chuyển về shop
    other_fees DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Phí kiểm đếm, bao bì, bốc xếp
    total_quantity INT NOT NULL DEFAULT 0, -- Tổng số lượng chiếc trong lô
    status VARCHAR(30) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'CONFIRMED', 'RECEIVED', 'CANCELLED')),
    inbound_date TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. BẢNG CHI TIẾT PHIẾU NHẬP (Purchase Order Items & Landed Cost Calculation)
CREATE TABLE IF NOT EXISTS purchase_order_items (
    id SERIAL PRIMARY KEY,
    po_id INT NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    variant_id INT NOT NULL REFERENCES product_variants(id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_cost DECIMAL(15, 2) NOT NULL CHECK (unit_cost >= 0), -- Giá mua sỉ 1 chiếc
    allocated_freight DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Cước xe phân bổ cho 1 chiếc
    packaging_cost DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Tiền túi zip + tem mác riêng
    landed_cost DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Landed Cost = unit_cost + allocated_freight + packaging_cost
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. BẢNG ĐƠN HÀNG BÁN ĐA KÊNH (Orders)
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_sn VARCHAR(100) NOT NULL UNIQUE, -- Mã đơn từ sàn: Shopee, TikTok Shop, FB
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('TIKTOK', 'SHOPEE', 'FACEBOOK', 'OFFLINE')),
    gross_sales DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Tổng tiền khách trả
    platform_fee DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Phí sàn thu (phí cố định + thanh toán)
    voucher_sponsor DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Voucher shop chịu
    shipping_fee_shop DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Phí ship shop chịu bù
    net_settlement_amount DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Tiền thực nhận về ví sàn
    order_status VARCHAR(50) NOT NULL DEFAULT 'DELIVERED' CHECK (order_status IN ('PENDING', 'SHIPPED', 'DELIVERED', 'RETURNED', 'CANCELLED')),
    return_condition VARCHAR(30) DEFAULT 'NONE' CHECK (return_condition IN ('NONE', 'INTACT', 'DAMAGED')),
    return_loss_cost DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Chi phí mất do hoàn (ship 2 chiều / mất đứt vốn)
    order_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    settlement_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. BẢNG CHI TIẾT SẢN PHẨM TRONG ĐƠN (Order Items & COGS Snapshot)
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    variant_id INT NOT NULL REFERENCES product_variants(id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    selling_price DECIMAL(15, 2) NOT NULL CHECK (selling_price >= 0),
    applied_landed_cogs DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Giá vốn Landed Cost đóng băng tại lúc xuất kho
    packaging_expense DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Chi phí túi đóng hàng lúc gửi đi
    net_margin DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Lợi nhuận ròng của item = (selling_price - applied_landed_cogs - packaging_expense)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- INDEXING CHO HIỆU NĂNG TÌM KIẾM CAO
-- ==============================================================================
CREATE INDEX IF NOT EXISTS idx_product_variants_sku ON product_variants(sku);
CREATE INDEX IF NOT EXISTS idx_product_variants_barcode ON product_variants(barcode);
CREATE INDEX IF NOT EXISTS idx_orders_platform_status ON orders(platform, order_status);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_purchase_order_items_po_id ON purchase_order_items(po_id);

-- ==============================================================================
-- VIEW TÍNH TOÁN BÁO CÁO TÀI CHÍNH & LÃI RÒNG THỰC TẾ (P&L Views)
-- ==============================================================================
CREATE OR REPLACE VIEW view_order_profitability AS
SELECT 
    o.id AS order_id,
    o.order_sn,
    o.platform,
    o.order_status,
    o.order_date,
    o.gross_sales,
    o.platform_fee,
    o.net_settlement_amount,
    COALESCE(SUM(oi.applied_landed_cogs * oi.quantity), 0) AS total_cogs,
    COALESCE(SUM(oi.packaging_expense * oi.quantity), 0) AS total_packaging,
    o.return_loss_cost,
    (o.net_settlement_amount - COALESCE(SUM(oi.applied_landed_cogs * oi.quantity), 0) - COALESCE(SUM(oi.packaging_expense * oi.quantity), 0) - o.return_loss_cost) AS true_net_profit
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, o.order_sn, o.platform, o.order_status, o.order_date, o.gross_sales, o.platform_fee, o.net_settlement_amount, o.return_loss_cost;
