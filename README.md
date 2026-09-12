# 👗 FashionRev-Ops: Hệ Thống Quản Lý Doanh Thu & Lợi Nhuận Thực Tế (Shop Thời Trang Online)

> **Giải pháp chuyển đổi số và quản trị tài chính - dòng tiền chuyên sâu dành cho mô hình kinh doanh quần áo may sẵn / nhập hàng sẵn (Fast-Fashion E-commerce).**  
> **Kiến trúc hệ thống:** Xây dựng xoay quanh **3 Tính Năng Cốt Lõi** bám sát quy trình vận hành và đối soát thực tế.

---

## 📌 1. Bối Cảnh & Bài Toán Kinh Doanh Cốt Lõi (Top-Down & Core Pain Points)

Kinh doanh thời trang online theo mô hình **nhập hàng may sẵn** có tốc độ xoay vòng vốn cực nhanh nhưng cũng tiềm ẩn rủi ro thất thoát biên lợi nhuận cao nhất trong ngành E-commerce:

1. **Vòng đời sản phẩm ngắn (Hot Trend 2–4 tuần):** Không có giá vốn chuẩn xác và không đo lường được lãi ròng theo từng biến thể (Size/Màu), lợi nhuận của đợt bán trước sẽ bị chôn vùi vào tiền nhập hàng tồn đọng (*Bẫy "Doanh thu ảo - Tiền mặt âm"*).
2. **Giá vốn biến động liên tục (Dynamic Landed Cost):** Cùng 1 mẫu áo, đợt 1 nhập giá sỉ khác, đợt 2 nhập bổ sung cước xe tải tăng. Nếu lấy giá sỉ hóa đơn làm giá vốn sẽ bị "ăn mòn" 3.000đ – 5.000đ tiền cước trên mỗi sản phẩm.
3. **Phí sàn trừ ngầm (Platform Fee Creep):** Hoa hồng sàn (9%–12%), voucher tài trợ, phụ phí đóng gói ăn mòn phần lớn lợi nhuận khiến shop lầm tưởng bán được nhiều là có lãi nếu không kiểm soát ở cấp độ đơn vị sản phẩm.

```mermaid
flowchart TD
    A[Nhà Cung Cấp / Xưởng May] -->|1. PO + Cước xe tải| B(Hệ Thống Phân Bổ Landed Cost)
    B -->|2. Thêm Mẫu Mới & Nhập Kho| C[Kho Hàng / Tồn Kho Đa Biến Thể]
    C -->|3. Đóng Đơn & Snapshot COGS| D[Kênh Bán: TikTok / Shopee / FB]
    D -->|4. Đối Soát Đơn Hàng| E[Thác Nước Lợi Nhuận Ròng]
    E --> G[Executive Financial Dashboard]
```

---

## 🚀 2. Ba Tính Năng Cốt Lõi (Core Functional Engines - MVP Scope)

Hệ thống được thiết kế top-down tập trung giải quyết triệt để **3 Tính Năng Cốt Lõi** xoay quanh bài toán giá vốn và lợi nhuận thực tế:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   FASHIONREV-OPS: 3 TÍNH NĂNG CỐT LÕI (MVP)                     │
├───────────────────────────────┬──────────────────────────────────────────────────┤
│ 1. Inbound Landed Cost Engine │ 2. Dynamic Inbound SKU Management                │
│    • Phân bổ tự động cước xe  │    • Thêm mẫu mới/size mới vào lô động           │
│    • Công thức tính chuẩn xác │    • Xem trước giá vốn dự kiến trên Modal        │
│    • Tiêu điểm Landed Cost    │    • Tự động chia lại cước cho toàn bộ lô        │
├───────────────────────────────┴──────────────────────────────────────────────────┤
│ 3. Order Net Profit Waterfall Ledger (Đa Kênh TMĐT)                              │
│    • Bóc tách 5 bước dòng tiền: Khách trả -> Phí sàn -> Landed COGS -> Bao bì    │
│    • Phân tích biên lợi nhuận ròng đút túi (Net Margin %)                        │
│    • Bộ lọc thông minh: TikTok Shop, Shopee, Facebook POS                        │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 🔹 Tính Năng 1: Phân Bổ Giá Vốn Cập Kho Tự Động (Inbound Landed Cost Engine)
* **Bài toán giải quyết:** Tự động chia đều chi phí cước xe tải và phụ phí bốc dỡ vào từng chiếc áo nhập kho.
* **Công thức toán học minh bạch:**
  $$\text{Landed Cost}_{\text{SKU}} = \text{Giá Mua Sỉ} + \frac{\text{Cước Xe Tải} + \text{Phí Bốc Dỡ}}{\text{Tổng Số Lượng Chiếc Nhập}} + \text{Phí Túi Zip \& Tem}$$
* **Trực quan hóa:** Khung tiêu điểm *Landed Cost Spotlight* và thanh cơ cấu chi phí 3 màu (Giá sỉ 96.1% • Cước xe 2.6% • Bao bì 1.3%).

### 🔹 Tính Năng 2: Quản Lý & Thêm Mẫu Mới Vào Lô Hàng Động (Dynamic Inbound SKU Management)
* **Bài toán giải quyết:** Cho phép chủ shop / thủ kho phát sinh thêm bất kỳ mẫu áo, màu, size mới nào vào lô hàng đang nhập.
* **Cơ chế vận hành:**
  - Hộp thoại Modal: Nhập mã SKU, tên mẫu áo, chất liệu vải, size (`Size S` $\rightarrow$ `Free Size`), số lượng và giá sỉ.
  - **Live Projected Landed Cost:** Tự tính trước giá vốn dự kiến ngay trên Modal trước khi thêm.
  - **Tự động chia lại cước:** Khi thêm mẫu mới, tổng sản lượng lô tăng lên, hệ thống tự động tính lại cước bổ đầu và cập nhật lại toàn bộ bảng giá vốn của các mẫu còn lại.
  - Hỗ trợ nút xóa mẫu `[✕]` trên từng dòng và đồng bộ tức thì sang Database catalog qua `POST /api/v1/catalog/variants`.

### 🔹 Tính Năng 3: Thác Nước Lợi Nhuận Ròng Từng Đơn (Order Net Profit Waterfall Ledger)
* **Bài toán giải quyết:** Bóc tách từng đồng chi phí bị trừ ngầm để biết chính xác mỗi đơn hàng thực nhận bao nhiêu tiền vào tài khoản.
* **Luồng khấu trừ 5 bước (Waterfall):**
  $$\text{Doanh Thu Khách Trả} \rightarrow -\text{Phí Sàn \& Voucher} \rightarrow -\text{Giá Vốn Landed COGS} \rightarrow -\text{Hộp Gói Hàng} = \mathbf{\text{Lợi Nhuận Ròng Thực Tế}}$$
* **Bộ lọc thông minh:** Lọc theo kênh bán (*TikTok Shop, Shopee, Facebook POS*) và lọc theo biên lãi (*Lãi cao >40%, Lãi mỏng <20%, Đơn hòa vốn/lỗ*).

> **Lộ trình Mở rộng Giai đoạn 2 (Future Roadmap):**  
> *Tính năng 4: Phân loại vật lý và chốt lỗ kế toán hàng hoàn (Return Loss Triage & Accounting)* được dời sang Phase 2 để ưu tiên tập trung tối ưu hóa 3 tính năng cốt lõi trên.

---

## 👥 3. Phân Tích Vai Trò & Sơ Đồ Use Case (Roles & Use Case Diagram)

Xem tài liệu chi tiết tại: [docs/usecase.md](file:///c:/AI_thuc_chien_khoa_3/VSF/Day1_intern_VSF/docs/usecase.md)

### Danh Sách Actors
- **Thủ kho / Vận hành (Ops Staff):** Nhập phiếu hàng, khai báo cước xe, thêm mẫu mới vào lô, điều chỉnh số lượng và in mã vạch barcode.
- **Chủ shop / Kế toán (Shop Owner / Finance):** Giám sát bảng Thác nước lợi nhuận đa sàn, đối soát ví sàn, theo dõi 4 KPI tài chính và tối ưu danh mục sản phẩm sinh lời.

### Sơ Đồ Mermaid Use Case
```mermaid
graph LR
    UserOps(["👷 Thủ kho / Vận hành"])
    UserOwner(["👑 Chủ shop / Tài chính"])

    subgraph System ["Hệ thống FashionRev-Ops (3 Tính Năng Cốt Lõi)"]
        UC1["1. Tạo Phiếu Nhập Hàng PO"]
        UC2["2. Phân Bổ Cước Xe Landed Cost"]
        UC3["3. Thêm Mẫu Mới Vào Lô (Dynamic SKU)"]
        UC4["4. Điều Chỉnh / Xóa Mẫu Khỏi Lô"]
        UC5["5. Xem Thác Nước Lãi Ròng Từng Đơn"]
        UC6["6. Lọc Đơn Hàng Đa Sàn (TikTok/Shopee/FB)"]
        UC7["7. Giám Sát 4 KPI Tài Chính Cốt Lõi"]
    end

    UserOps --> UC1
    UserOps --> UC2
    UserOps --> UC3
    UserOps --> UC4

    UserOwner --> UC1
    UserOwner --> UC5
    UserOwner --> UC6
    UserOwner --> UC7

    UC1 -.->|include| UC2
    UC3 -.->|tự động chia lại cước| UC2
    UC4 -.->|cập nhật sản lượng| UC2
    UC5 -.->|tổng hợp doanh thu & lãi| UC7
```

---

## 🏛️ 4. Kiến Trúc Thông Tin (Information Architecture - IA)

Xem tài liệu chi tiết tại: [docs/information_architecture.md](file:///c:/AI_thuc_chien_khoa_3/VSF/Day1_intern_VSF/docs/information_architecture.md)

Cấu trúc phân tầng dữ liệu qua 3 Màn hình Tabs:
```plaintext
CẤU TRÚC HỆ THỐNG (INFORMATION ARCHITECTURE)
├── [Tab 1] Overview Dashboard (Tổng quan Hoạt động & Lợi nhuận)
│   ├── Khối 4 KPI Tài chính: Doanh thu sàn | Giá vốn COGS | Phí sàn & bao bì | Lợi nhuận ròng thực
│   ├── Khối tóm tắt Nhập hàng & Landed Cost (Công thức, bảng SKU, nút tạo mới)
│   └── Khối tóm tắt Đơn bán & Thác nước chi phí đa sàn (TikTok Shop, Shopee, FB POS)
│
├── [Tab 2] Inbound Landed Cost (Chi tiết Phiếu Nhập & Phân Bổ Giá Vốn)
│   ├── Breadcrumbs điều hướng & Nút đồng bộ kế toán ERP
│   ├── Cột trái: Thông số lô hàng (Xưởng may, Cước xe, Phí bốc dỡ, Phí túi zip)
│   ├── Cột phải: Xem trước phân bổ thời gian thực (Cước bổ đầu, Tiêu điểm Landed Cost)
│   ├── Bảng SKU chi tiết: Tìm kiếm, Lọc Size, Nút [➕ Add New SKU to Batch], Nút xóa [✕]
│   └── Modal Thêm Mẫu Mới: Điền SKU, Size, Tên áo, Vải, SL, Giá sỉ -> Tự động chia lại cước
│
└── [Tab 3] Order Net Profit (Thác Nước Lợi Nhuận Đơn Hàng Đa Sàn)
    ├── Thẻ chỉ số: Tỷ suất biên lãi ròng trung bình (45.2%) | Tổng đơn hoàn thành (2,450 đơn)
    ├── Bộ lọc đa chiều: Lọc theo kênh bán, Kỳ đối soát, Lọc theo biên lãi (>40%, <20%, đơn lỗ)
    └── Bảng Waterfall Ledger 7 cột: Bóc tách từng khoản trừ từ Doanh thu đến Lãi đút túi
```

---

## 🖼️ 5. Hình Ảnh Giao Diện Thực Tế (UI/UX Mockups & Screenshots)

Giao diện được thiết kế theo phong cách **Light SaaS tối giản, tinh tế** và hiển thị 100% bằng tiếng Anh chuẩn e-commerce:

### 5.1. Màn Hình 1: Tổng Quan Dashboard (Overview Dashboard)
![Overview Dashboard](docs/screenshots/dashboard_overview.png)
*Tích hợp 4 KPI tài chính trên cùng, bộ tính Landed Cost bên trái, Thác nước chi phí đơn hàng bên phải.*

---

### 5.2. Màn Hình 2: Chi Tiết Phiếu Nhập & Phân Bổ Giá Vốn (Inbound Landed Cost)
![Inbound Landed Cost](docs/screenshots/inbound_landed_cost.png)
*Bộ thông số cước xe, thuật toán phân bổ thời gian thực, bảng danh mục biến thể SKU có nút **`[➕ Add New SKU to Batch]`** để thêm mẫu mới.*

---

### 5.3. Màn Hình 3: Thác Nước Lợi Nhuận Đơn Hàng (Order Net Profit Waterfall Ledger)
![Order Net Profit](docs/screenshots/order_net_profit.png)
*Bảng Waterfall Ledger bóc tách dòng tiền từng đơn hàng đa sàn từ Doanh thu khách trả, Phí hoa hồng sàn, Landed COGS và Túi bọc hàng để tính chính xác Lãi ròng đút túi.*

---

## 🗄️ 6. Thiết Kế Cơ Sở Dữ Liệu (Database Schema & DBML)

- File thiết kế chuẩn DBML: [docs/schema.dbml](file:///c:/AI_thuc_chien_khoa_3/VSF/Day1_intern_VSF/docs/schema.dbml)  
  *(Dán toàn bộ mã trong file này vào [dbdiagram.io](https://dbdiagram.io/) để xuất biểu đồ quan hệ ERD trực quan).*
- File mã nguồn SQL DDL: `init-scripts/01_schema.sql` (PostgreSQL 16).

```mermaid
erDiagram
    CATEGORIES ||--|{ PRODUCTS : classifies
    SUPPLIERS ||--|{ PURCHASE_ORDERS : provides
    PRODUCTS ||--|{ PRODUCT_VARIANTS : has_variants
    PRODUCT_VARIANTS ||--o{ PURCHASE_ORDER_ITEMS : contains
    PURCHASE_ORDERS ||--|{ PURCHASE_ORDER_ITEMS : includes
    PRODUCT_VARIANTS ||--o{ ORDER_ITEMS : ordered_in
    ORDERS ||--|{ ORDER_ITEMS : contains

    PRODUCT_VARIANTS {
        int id PK
        string sku UK
        string color
        string size
        string barcode UK
        decimal base_price
        int current_stock
    }

    PURCHASE_ORDERS {
        int id PK
        string po_code UK
        decimal shipping_fee
        decimal other_fees
        int total_quantity
        string status
    }

    PURCHASE_ORDER_ITEMS {
        int id PK
        decimal unit_cost
        decimal allocated_freight
        decimal landed_cost
    }

    ORDERS {
        int id PK
        string order_sn UK
        string platform
        decimal gross_sales
        decimal platform_fee
        string return_condition
        decimal return_loss_cost
    }

    ORDER_ITEMS {
        int id PK
        decimal applied_landed_cogs
        decimal packaging_expense
        decimal net_margin
    }
```

---

## ⚙️ 7. Hướng Dẫn Cài Đặt & Chạy Hệ Thống (Getting Started)

### Yêu Cầu Môi Trường
- **Python:** 3.11+
- **Docker & Docker Compose:** Dùng để chạy PostgreSQL 16
- **Trình duyệt web:** Chrome, Edge, Safari

### Các Bước Khởi Động

#### 1. Khởi động Cơ sở dữ liệu PostgreSQL
```bash
docker compose up -d
```
Database chạy tại cổng `5433` (được ánh xạ từ cổng container 5432) với thông tin kết nối trong `.env`:
`postgresql://postgres:postgrespassword@localhost:5433/fashionrev_db`

#### 2. Khởi động Backend FastAPI
```bash
# Cài đặt thư viện phụ thuộc
pip install -r requirements.txt

# Khởi động máy chủ backend trên cổng 8088
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8088 --reload
```

#### 3. Truy Cập Hệ Thống
- **Giao diện Web UI:** [http://localhost:8088/](http://localhost:8088/)
- **Tài liệu API Swagger:** [http://localhost:8088/docs](http://localhost:8088/docs)
- **Kiểm tra trạng thái Health:** [http://localhost:8088/api/v1/health](http://localhost:8088/api/v1/health)

---

