# Đặc Tả Chức Năng Hệ Thống (Functional Specifications)

> **Hệ thống:** FashionRev-Ops - Quản trị Dòng tiền, Giá vốn & Lợi nhuận Ròng Shop Thời Trang  
> **Phiên bản:** MVP 3 Tính Năng Cốt Lõi (12/09/2026)

---

## TỔNG QUAN 3 TÍNH NĂNG CỐT LÕI (MVP SCOPE)

| STT | Tên tính năng | Tên tiếng Anh | Phân hệ màn hình | Vai trò chính |
| :---: | :--- | :--- | :---: | :--- |
| **F1** | **Phân Bổ Giá Vốn Cập Kho Tự Động** | *Inbound Landed Cost Engine* | Tab 1, Tab 2 | Thủ kho, Chủ shop |
| **F2** | **Quản Lý & Thêm Mẫu Mới Vào Lô Động** | *Dynamic Inbound SKU Management* | Tab 2 (Modal) | Thủ kho, Kế toán kho |
| **F3** | **Thác Nước Lợi Nhuận Ròng Từng Đơn** | *Order Net Profit Waterfall Ledger* | Tab 1, Tab 3 | Chủ shop, Kế toán tài chính |

*(Ghi chú: Tính năng Phân loại & Chốt lỗ hàng hoàn được xếp vào Kế hoạch mở rộng Giai đoạn 2).*

---

## 1. TÍNH NĂNG F1: PHÂN BỔ GIÁ VỐN CẬP KHO TỰ ĐỘNG (INBOUND LANDED COST ENGINE)

### 1.1. Mục đích nghiệp vụ & User Story
- **Vấn đề:** Shop thời trang nhập 500 cái áo từ xưởng với giá sỉ 75.000đ/cái. Tiền xe tải chở hàng hết 1.000.000đ, tiền túi zip tem mác 1.000đ/cái. Nếu chỉ lấy giá 75.000đ làm giá vốn thì shop sẽ bị hụt lãi ẩn 3.000đ/chiếc (mất 1.500.000đ tiền lãi thực).
- **User Story:** *"Là một Chủ shop / Thủ kho, tôi muốn khi nhập số tiền cước xe và phụ phí, hệ thống phải tự động chia đều tiền cước vào từng chiếc áo để tôi có giá vốn cập kho chính xác 100% trước khi mở bán đa kênh."*

### 1.2. Bảng đặc tả dữ liệu Vào / Xử lý / Ra (I-P-O)

| Thành phần | Chi tiết đặc tả | Ràng buộc & Kiểu dữ liệu |
| :--- | :--- | :--- |
| **Đầu vào (Input)** | • `shipping_fee`: Cước xe tải vận chuyển kiện hàng về kho.<br>• `other_fees`: Phụ phí bốc dỡ, kiểm đếm tại bến bãi.<br>• `packaging_cost`: Chi phí túi zip bao bì & tem barcode.<br>• `items[i].unit_cost`: Đơn giá mua sỉ gốc trên hóa đơn xưởng.<br>• `items[i].quantity`: Số lượng chiếc của từng SKU trong lô. | • `shipping_fee` $\ge 0$, Decimal(15, 2)<br>• `other_fees` $\ge 0$, Decimal(15, 2)<br>• `packaging_cost` $\ge 0$, mặc định `1.000 ₫`<br>• `unit_cost` $> 0$, `quantity` $\ge 1$ |
| **Thuật toán xử lý (Processing)** | 1. Tính tổng sản lượng lô: $\text{Total Qty} = \sum_{i=1}^n \text{quantity}_i$<br>2. Tính tổng quỹ cước vận chuyển: $\text{Freight Pool} = \text{shipping\_fee} + \text{other\_fees}$<br>3. Tính cước bổ đầu bình quân: $\text{Allocated Freight} = \frac{\text{Freight Pool}}{\text{Total Qty}}$<br>4. Tính Landed Cost từng biến thể SKU: $$\text{Landed Cost}_i = \text{unit\_cost}_i + \text{Allocated Freight} + \text{packaging\_cost}$$ | Làm tròn đến số nguyên tiền đồng (VND). Tự động kích hoạt tính toán tức thì (Real-time recalculation) khi có bất kỳ thay đổi nào từ ô input mà không cần tải lại trang. |
| **Đầu ra (Output)** | • Hiển thị khung tiêu điểm Spotlight: `78.000 ₫ / pc`.<br>• Cột `ALLOCATED FREIGHT` trên bảng hiển thị: `+2.000 ₫`.<br>• Cột `UNIT LANDED COST` hiển thị huy hiệu xanh: `78.000 ₫`.<br>• Thanh tổng kết giá trị lô hàng: $\text{Total Landed Value} = \sum (\text{Landed Cost}_i \times \text{quantity}_i)$. | Cập nhật đồng bộ lên Dashboard và sẵn sàng đóng băng giá vốn cho đơn hàng bán ra. |

---

## 2. TÍNH NĂNG F2: QUẢN LÝ & THÊM MẪU MỚI VÀO LÔ HÀNG ĐỘNG (DYNAMIC SKU MANAGEMENT)

### 2.1. Mục đích nghiệp vụ & User Story
- **Vấn đề:** Trong thực tế nhập hàng xưởng, ngoài các mẫu áo quen thuộc, chủ shop thường phát sinh nhập thêm các mẫu mới (màu mới, size XL, mẫu váy mới...). Nếu hệ thống cố định cứng danh mục thì không phản ánh đúng thực tế kiện hàng.
- **User Story:** *"Là một Thủ kho, tôi muốn có thể bấm nút thêm một mẫu thời trang mới ngay trên giao diện (gồm SKU, tên áo, size, số lượng, giá sỉ), và hệ thống phải tự động cộng dồn sản lượng và chia lại cước cho toàn bộ các mẫu còn lại."*

### 2.2. Bảng đặc tả dữ liệu Vào / Xử lý / Ra (I-P-O)

| Thành phần | Chi tiết đặc tả | Ràng buộc & Kiểu dữ liệu |
| :--- | :--- | :--- |
| **Đầu vào (Input)** | • `sku`: Mã biến thể thời trang (VD: `AT-BEG-M`, `VAY-HOA-L`).<br>• `product_name`: Tên sản phẩm thời trang.<br>• `material`: Chất liệu vải (VD: `Cotton 280gsm`, `Lụa tơ tằm`).<br>• `size`: Phân loại kích cỡ (`Size S`, `M`, `L`, `XL`, `2XL`, `Free Size`).<br>• `quantity`: Số lượng chiếc nhập của mẫu mới này.<br>• `wholesale_price`: Giá mua sỉ từ xưởng.<br>• `initial_stock`: Tồn kho ban đầu trước khi nhập. | • `sku`: Text, không trùng với SKU đã có trong lô.<br>• `product_name`: Bắt buộc, không để trống.<br>• `quantity`: Integer $\ge 1$.<br>• `wholesale_price`: Decimal $\ge 0$. |
| **Thuật toán xử lý (Processing)** | 1. Kiểm tra tính hợp lệ dữ liệu trên Modal.<br>2. Tính trước giá vốn dự kiến của mẫu mới (Projected Landed Cost) ngay trong modal:<br>   $\text{Projected} = \text{wholesale} + \frac{\text{Cước xe}}{\text{Tổng Qty cũ} + \text{Qty mới}} + \text{Túi zip}$<br>3. Bấm xác nhận: Đẩy phần tử mới vào danh sách SKU lô hàng.<br>4. Kích hoạt tự động phân bổ lại cước (F1) cho toàn bộ $N+1$ mẫu.<br>5. Bổ sung size mới vào thanh nút lọc Size nếu chưa tồn tại.<br>6. Gọi API `POST /api/v1/catalog/variants` để lưu mẫu mới vào database. | Hỗ trợ xóa mẫu `[✕]`: Nếu xóa bớt một mẫu, tổng sản lượng giảm đi, cước xe chia lại cho các mẫu còn lại tự động tăng lên tương ứng. |
| **Đầu ra (Output)** | • Dòng SKU mới xuất hiện trên bảng chi tiết có đầy đủ giá vốn.<br>• Tổng sản lượng lô nhảy số (ví dụ $650 \rightarrow 800$ cái).<br>• Cước bình quân nhảy số (ví dụ $+2.000₫ \rightarrow +1.625₫$).<br>• Toast thông báo thành công: ` Added SKU [MÃ] ([SL] pcs) to batch!`. | Bảng dữ liệu đồng bộ và hiển thị tức thì. |

---

## 3. TÍNH NĂNG F3: THÁC NƯỚC LỢI NHUẬN RÒNG TỪNG ĐƠN (WATERFALL LEDGER & MULTI-CHANNEL)

### 3.1. Mục đích nghiệp vụ & User Story
- **Vấn đề:** Bán hàng đa kênh (TikTok Shop, Shopee, Facebook POS) thường mắc bẫy *"Doanh thu tiền tỷ nhưng ví rỗng"* do phí sàn 9-12%, voucher đồng tài trợ, chi phí bao bì hộp carton và giá vốn thực tế ăn mòn hết lợi nhuận.
- **User Story:** *"Là một Chủ shop, tôi muốn nhìn thấy rõ từng dòng tiền bị khấu trừ của từng đơn hàng từ lúc khách trả đến số tiền thực tế vào tài khoản ngân hàng của tôi."*

### 3.2. Bảng đặc tả dữ liệu Vào / Xử lý / Ra (I-P-O)

| Thành phần | Chi tiết đặc tả | Ràng buộc & Kiểu dữ liệu |
| :--- | :--- | :--- |
| **Đầu vào (Input)** | • `gross_sales`: Tổng doanh thu khách hàng thanh toán cho đơn.<br>• `platform_fee`: Hoa hồng sàn, phí thanh toán, voucher shop tài trợ.<br>• `applied_landed_cogs`: Giá vốn cập kho đã đóng băng của món đồ.<br>• `packaging_expense`: Chi phí hộp carton, túi bọc hàng niêm phong.<br>• `platform`: Kênh bán hàng (`TIKTOK`, `SHOPEE`, `FACEBOOK`). | Dữ liệu đồng bộ từ sàn TMĐT hoặc webhook đối soát đơn hàng. |
| **Thuật toán xử lý (Processing)** | 1. Bóc tách thác nước chi phí theo thứ tự 5 bước:<br>   $$\text{Lợi Nhuận Ròng} = \text{gross\_sales} - \text{platform\_fee} - \text{applied\_landed\_cogs} - \text{packaging\_expense}$$<br>2. Tính tỷ suất lợi nhuận ròng (Net Profit Margin %):<br>   $$\text{Margin \%} = \left(\frac{\text{Lợi Nhuận Ròng}}{\text{gross\_sales}}\right) \times 100\%$$<br>3. Phân loại đơn theo biên lãi: Lãi cao ($>40\%$), Lãi thấp ($<20\%$). | Gắn nhãn màu trực quan: Xanh lá cho lãi cao, Cam cho lãi mỏng. |
| **Đầu ra (Output)** | • Bảng Waterfall Ledger 7 cột hiển thị chi tiết từng khoản trừ.<br>• Huy hiệu Lãi ròng đút túi: `+139.100 ₫ (46.5%)` kèm thanh progress bar.<br>• Bộ lọc kênh bán: Xem riêng doanh thu/lãi ròng từng sàn TMĐT.<br>• Tổng hợp lên thẻ KPI: `TRUE NET PROFIT: 72.900.000 ₫ (Net Margin 39.3%)`. | Dữ liệu kế toán chuẩn mực, minh bạch từng đồng. |

---

##  4. TÍNH NĂNG MỞ RỘNG GIAI ĐOẠN 2 (FUTURE ROADMAP): XỬ LÝ HÀNG HOÀN
- **Mô tả:** Phân loại kiện hàng bưu tá trả về shop thành 2 luồng: Hàng nguyên tem (nhập lại kho, chỉ lỗ cước ship) và Hàng rách/hỏng (mất đứt 100% giá vốn món đồ).
- **Lý do hoãn:** Tối ưu hóa thời gian phát triển MVP, tập trung dồn lực hoàn thiện trọn vẹn 3 tính năng tính đúng giá vốn và bóc tách lợi nhuận ròng trước.
