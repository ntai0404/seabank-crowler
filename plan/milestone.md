# SeaBank Crawler - Data Milestones

Tài liệu này tổng hợp các nguồn dữ liệu, bảng (sheets) và cấu trúc thông tin (fields) mà hệ thống SeaBank Crawler đang khai thác.

## 1. Nguồn dữ liệu: CafeF (cafef.vn)
Nguồn dữ liệu chính về tài chính, chứng khoán và kinh tế vĩ mô.

### Bảng: `stock_prices` (Giá Cổ phiếu)
Theo dõi biến động giá của 271+ mã chứng khoán (nhóm ngân hàng, bất động sản, VN30...).
- `timestamp`: Thời gian cào dữ liệu.
- `symbol`: Mã chứng khoán (VD: ACB, VHM).
- `ngay`: Ngày giao dịch.
- `gia_mo_cua`: Giá mở cửa.
- `gia_cao_nhat`: Giá cao nhất trong phiên.
- `gia_thap_nhat`: Giá thấp nhất trong phiên.
- `gia_dong_cua`: Giá đóng cửa (giá khớp).
- `thay_doi`: Phần trăm thay đổi.
- `khoi_luong`: Khối lượng khớp lệnh.
- `gia_tri`: Tổng giá trị giao dịch.

### Bảng: `exchange_rates` (Tỷ giá ngoại tệ)
- `timestamp`: Thời gian cào.
- `currency`: Loại ngoại tệ (USD, EUR, JPY...).
- `buy_cash`: Giá mua tiền mặt.
- `buy_transfer`: Giá mua chuyển khoản.
- `sell`: Giá bán ra.

### Bảng: `macro_indicators` (Chỉ số vĩ mô)
Theo dõi các chỉ số thế giới và trong nước.
- `timestamp`: Thời gian cào.
- `index_name`: Tên chỉ số (VD: S&P 500, Nikkei 225).
- `price`: Giá trị hiện tại.
- `change_percent`: % Biến động.

### Bảng: `bank_interest_rates` (Lãi suất Ngân hàng)
- `timestamp`: Thời gian cào.
- `bank_name`: Tên ngân hàng.
- `term`: Kỳ hạn (VD: 1 tháng, 12 tháng...).
- `rate`: Lãi suất (%/năm).
- `type`: Loại lãi suất (VD: Huy động).

### Bảng: `web_metrics` (Chỉ số đo lường tin tức)
- `timestamp`: Thời gian cào.
- `source`: Nguồn tin (cafef.vn).
- `metric_name`: Tên metric (VD: news_count_banking).
- `metric_value`: Số lượng bài viết mới được ghi nhận.
- `meta_json`: Thông tin bổ sung (JSON).

---

## 2. Nguồn dữ liệu: Tổng cục Hải quan (customs.gov.vn)
Dữ liệu thống kê xuất nhập khẩu hàng hóa.

### Bảng: `customs_trade` (Thống kê XNK chung)
- `timestamp`: Thời gian cào.
- `source`: Nguồn (customs.gov.vn).
- `category`: Loại hình (Xuất khẩu/Nhập khẩu).
- `period`: Kỳ báo cáo (Tháng/Năm).
- `value_usd`: Giá trị tính bằng USD.
- `unit`: Đơn vị tính.
- `meta_json`: Metadata bổ sung.

### Bảng: `customs_commodity_details` (Chi tiết mặt hàng XNK)
Tập trung vào các mặt hàng SeaBank quan tâm (Dệt may, Thủy sản, Da giày...).
- `timestamp`: Thời gian cào.
- `category`: Tên mặt hàng (VD: Dệt may).
- `period`: Kỳ báo cáo.
- `export_value`: Trị giá xuất khẩu.
- `import_value`: Trị giá nhập khẩu.
- `change_pct`: % Thay đổi so với kỳ trước.

---

## 3. Nguồn dữ liệu: Hiệp hội Dệt may Việt Nam (VITAS - vietnamtextile.org.vn)
Dữ liệu về doanh nghiệp và tin tức ngành dệt may.

### Bảng: `textile_directory` (Danh bạ Hội viên)
Danh sách khách hàng tiềm năng cho mảng Corporate Banking.
- `timestamp`: Thời gian cào.
- `company_name`: Tên doanh nghiệp.
- `business_type`: Lĩnh vực kinh doanh.
- `address`: Địa chỉ trụ sở.
- `website`: Trang web (nếu có).

### Bảng: `textile_news` (Tin tức ngành Dệt may)
- `timestamp`: Thời gian cào.
- `source`: Nguồn tin.
- `title`: Tiêu đề bài báo.
- `url`: Đường dẫn chi tiết.
- `category`: Phân loại tin.
- `published_date`: Ngày đăng.
- `summary`: Tóm tắt nội dung.

---

## 4. Nguồn dữ liệu: Tập đoàn Dệt may Việt Nam (Vinatex - vinatex.com.vn)

### Bảng: `vinatex_news` (Tin tức Vinatex)
- `timestamp`: Thời gian cào.
- `source`: vinatex.com.vn.
- `title`: Tiêu đề bài viết.
- `url`: Link bài viết.
- `lang`: Ngôn ngữ (vi/en).
- `published_date`: Ngày xuất bản.
- `summary`: Nội dung tóm tắt.

---

## 5. Nguồn dữ liệu khác (Vàng - Webgia.com / PNJ)

### Bảng: `gold_prices` (Giá vàng)
- `timestamp`: Thời gian cào.
- `gold_type`: Loại vàng (SJC, 9999...).
- `buy_price`: Giá mua vào.
- `sell_price`: Giá bán ra.
