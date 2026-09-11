-- ==============================================================================
-- FashionRev-Ops: Seed Data (Mock Data cho kịch bản kinh doanh thời trang thực tế)
-- ==============================================================================

-- 1. Thêm danh mục sản phẩm
INSERT INTO categories (id, name, code, description) VALUES
(1, 'Áo Thun & Polo', 'CAT-TOP', 'Các dòng áo thun basic, oversize, polo nam nữ'),
(2, 'Váy & Đầm Nữ', 'CAT-DRESS', 'Váy hoa, đầm xòe, đầm chữ A bắt trend'),
(3, 'Quần & Chân Váy', 'CAT-BOTTOM', 'Quần ống rộng, jeans, baggy, chân váy ngắn')
ON CONFLICT (id) DO NOTHING;

-- 2. Thêm nhà cung cấp / xưởng may
INSERT INTO suppliers (id, name, contact_person, phone, address) VALUES
(1, 'Xưởng May Tân Bình - Sài Gòn', 'Anh Hoàng', '0901234567', 'Khu Công Nghiệp Tân Bình, TP.HCM'),
(2, 'Tổng Kho Sỉ Ninh Hiệp', 'Chị Lan', '0987654321', 'Chợ Ninh Hiệp, Gia Lâm, Hà Nội')
ON CONFLICT (id) DO NOTHING;

-- 3. Thêm sản phẩm cha
INSERT INTO products (id, category_id, product_code, name, material, description) VALUES
(1, 1, 'PROD-AT-OVS', 'Áo Thun Form Rộng Unisex 100% Cotton', 'Cotton 100% 250gsm', 'Mẫu áo thun hot trend mùa hè, không xù lông'),
(2, 2, 'PROD-VAY-HOA', 'Váy Hoa Nhí Vintage Cổ Vuông Tay Phồng', 'Voan lụa 2 lớp cao cấp', 'Mẫu váy nữ tính dáng dài che khuyết điểm')
ON CONFLICT (id) DO NOTHING;

-- 4. Thêm biến thể sản phẩm (SKU & Barcode)
INSERT INTO product_variants (id, product_id, sku, color, size, barcode, base_price, current_stock) VALUES
(1, 1, 'AT-OVS-DEN-M', 'Đen', 'M', '893600100101', 189000.00, 150),
(2, 1, 'AT-OVS-DEN-L', 'Đen', 'L', '893600100102', 189000.00, 200),
(3, 1, 'AT-OVS-TRANG-M', 'Trắng', 'M', '893600100103', 189000.00, 120),
(4, 1, 'AT-OVS-TRANG-L', 'Trắng', 'L', '893600100104', 189000.00, 180),
(5, 2, 'VAY-HOA-VANG-S', 'Vàng Nhạt', 'S', '893600200201', 299000.00, 80),
(6, 2, 'VAY-HOA-VANG-M', 'Vàng Nhạt', 'M', '893600200202', 299000.00, 95)
ON CONFLICT (id) DO NOTHING;

-- 5. Thêm Phiếu Nhập Hàng (PO) - Chứng minh công thức phân bổ Landed Cost
-- Lô nhập 650 cái, tổng cước xe 1.300.000đ -> Phân bổ cước = 1.300.000 / 650 = 2.000đ / cái
INSERT INTO purchase_orders (id, po_code, supplier_id, total_merchandise_cost, shipping_fee, other_fees, total_quantity, status, inbound_date, notes) VALUES
(1, 'PO-20260901-01', 1, 48750000.00, 1300000.00, 650000.00, 650, 'RECEIVED', '2026-09-01 10:00:00+07', 'Nhập lô áo thun chuẩn bị chạy chiến dịch Sale 9.9')
ON CONFLICT (id) DO NOTHING;

-- 6. Chi tiết Phiếu nhập: Landed Cost = Giá sỉ 75k + Cước phân bổ 2k + Phí bọc zip 1k = 78.000đ
INSERT INTO purchase_order_items (po_id, variant_id, quantity, unit_cost, allocated_freight, packaging_cost, landed_cost) VALUES
(1, 1, 150, 75000.00, 2000.00, 1000.00, 78000.00),
(1, 2, 200, 75000.00, 2000.00, 1000.00, 78000.00),
(1, 3, 120, 75000.00, 2000.00, 1000.00, 78000.00),
(1, 4, 180, 75000.00, 2000.00, 1000.00, 78000.00);

-- 7. Thêm Đơn Hàng Mẫu Đa Kênh (Shopee, TikTok Shop)
INSERT INTO orders (id, order_sn, platform, gross_sales, platform_fee, voucher_sponsor, shipping_fee_shop, net_settlement_amount, order_status, return_condition, return_loss_cost, order_date, settlement_date) VALUES
-- Đơn 1: TikTok Shop thành công
(1, 'TT-20260909-8812', 'TIKTOK', 189000.00, 18900.00, 10000.00, 0.00, 160100.00, 'DELIVERED', 'NONE', 0.00, '2026-09-09 14:20:00+07', '2026-09-11 08:00:00+07'),
-- Đơn 2: Shopee thành công (mua 2 áo)
(2, 'SP-20260909-4421', 'SHOPEE', 378000.00, 37800.00, 20000.00, 15000.00, 305200.00, 'DELIVERED', 'NONE', 0.00, '2026-09-09 16:45:00+07', '2026-09-11 08:30:00+07'),
-- Đơn 3: Hoàn hàng nguyên vẹn (Mất cước ship 2 chiều + hỏng túi zip = 35.000đ)
(3, 'SP-20260908-1190', 'SHOPEE', 189000.00, 0.00, 0.00, 0.00, 0.00, 'RETURNED', 'INTACT', 35000.00, '2026-09-08 11:10:00+07', '2026-09-11 09:00:00+07'),
-- Đơn 4: Hoàn hàng rách/hỏng (Mất trắng 100% Landed Cost = 78.000đ + phí vận chuyển 30.000đ = 108.000đ)
(4, 'TT-20260907-9932', 'TIKTOK', 189000.00, 0.00, 0.00, 0.00, 0.00, 'RETURNED', 'DAMAGED', 108000.00, '2026-09-07 09:05:00+07', '2026-09-11 09:30:00+07')
ON CONFLICT (id) DO NOTHING;

-- 8. Chi tiết Order Items gắn Snapshot Giá Vốn (applied_landed_cogs = 78.000đ)
INSERT INTO order_items (order_id, variant_id, quantity, selling_price, applied_landed_cogs, packaging_expense, net_margin) VALUES
(1, 1, 1, 189000.00, 78000.00, 3000.00, 108000.00),
(2, 2, 1, 189000.00, 78000.00, 3000.00, 108000.00),
(2, 4, 1, 189000.00, 78000.00, 3000.00, 108000.00),
(3, 1, 1, 189000.00, 78000.00, 3000.00, 0.00),
(4, 2, 1, 189000.00, 78000.00, 3000.00, -108000.00);

-- Reset serial sequences
SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories));
SELECT setval('suppliers_id_seq', (SELECT MAX(id) FROM suppliers));
SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));
SELECT setval('product_variants_id_seq', (SELECT MAX(id) FROM product_variants));
SELECT setval('purchase_orders_id_seq', (SELECT MAX(id) FROM purchase_orders));
SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders));
