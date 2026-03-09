# Hướng dẫn tích hợp Dữ liệu vào Preset.io (Apache Superset)

Chào bạn, đây là hướng dân để bạn chuyển đổi các bảng dữ liệu "thô" từ Google Sheets thành các Dashboard chuyên nghiệp trên Preset.io, tương tự (hoặc đẹp hơn) các trang CafeF hay Hải quan.

## 1. Hiểu về luồng dữ liệu (Concept)
Bạn không thể "cào" nguyên một cái Dashboard (giao diện) về Preset, vì Preset là công cụ BI tự xây dựng biểu đồ từ **Dữ liệu**. 
- **Bước 1 (Đã xong)**: Hệ thống crawler cào "nguyên liệu" (data) về Google Sheets.
- **Bước 2**: Kết nối Google Sheets vào Preset làm Database.
- **Bước 3**: Trong Preset, bạn chọn loại biểu đồ (Bar, Line, Pie...) để hiển thị dữ liệu đó.

## 2. Các bước thiết lập kết nối

### Bước 1: Chuẩn bị Credentials
Preset cần quyền đọc Google Sheets của bạn.
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/).
2. Tạo một **Service Account** và tải file **JSON Key** (đây là file bạn đã dùng cho crawler).
3. Đảm bảo bạn đã **Share** Google Sheet của mình cho email của Service Account đó (quyền Viewer là đủ).

### Bước 2: Thêm Database vào Preset
1. Đăng nhập vào Preset.io.
2. Chọn **Data** -> **Databases** -> **+ Database**.
3. Chọn loại Database là **Google Sheets**.
4. Dán nội dung file **JSON Key** vào phần cấu hình.

### Bước 3: Tạo Dataset
1. Chọn **Data** -> **Datasets** -> **+ Dataset**.
2. Chọn Database vừa tạo.
3. Trong phần **Schema/Table**, nhập tên Tab trong Google Sheet (VD: `stock_prices`, `bank_interest_rates`).

## 3. Cách "tái tạo" lại Dashboard đẹp như CafeF

### Để có biểu đồ Giá Cổ phiếu (giống CafeF):
- **Loại biểu đồ**: Chọn `Big Number with Trendline` hoặc `Time-series Line Chart`.
- **Query**:
    - Metrics: `AVG(gia_dong_cua)`
    - Time: `timestamp`
    - Group by: `symbol`

### Để có biểu đồ Lãi suất (Soj sánh các Bank):
- **Loại biểu đồ**: `Bar Chart` (Cột đứng hoặc ngang).
- **Query**:
    - Metrics: `rate`
    - Series: `bank_name`
    - Breakdowns: `term` (để so sánh lãi suất các kỳ hạn).

### Để có biểu đồ Xuất nhập khẩu (giống Hải quan):
- **Loại biểu đồ**: `Mixed Chart` (Kết hợp Bar và Line).
- **Query**:
![Customs Example](https://lh3.googleusercontent.com/pw/...) *Dùng cột `export_value` và `import_value` làm 2 trục.*

## 4. Lợi ích khi dùng Preset thay vì xem trực tiếp trên web
1. **Dữ liệu tập trung**: Bạn có thể xem lãi suất Ngân hàng ngay bên cạnh biểu đồ Xuất khẩu Dệt may (điều mà CafeF hay Hải quan không làm chung một chỗ).
2. **Cảnh báo (Alerts)**: Bạn có thể cài đặt nếu Lãi suất một Bank nào đó vọt lên trên 10%, Preset sẽ gửi tin nhắn vào Slack/Email cho bạn.
3. **Tùy biến**: Bạn có thể lọc (filter) theo đúng danh mục mã cổ phiếu mà SeaBank đang quan tâm.

---
**Lời khuyên**: Bạn hãy bắt đầu bằng việc kết nối Tab `bank_interest_rates` trước, vì đây là dữ liệu có cấu trúc đẹp nhất hiện tại để làm Chart!
