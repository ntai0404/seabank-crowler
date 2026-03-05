# 🏦 SeaBank Data Crawler

Hệ thống tự động thu thập dữ liệu tài chính, xuất nhập khẩu và tin tức ngành hàng ngày, phục vụ cho việc phân tích và hiển thị trên Dashboard (Preset.io).

## 🚀 Tính năng chính

Hệ thống bao gồm 4 Agent chuyên biệt, tự động hóa toàn bộ quy trình từ thu thập đến lưu trữ:

1.  **Agent CafeF**:
    *   Thu thập giá của ~300 mã cổ phiếu lớn (VN30, HOSE, HNX).
    *   Cập nhật tỷ giá ngoại tệ từ Vietcombank.
    *   Cập nhật giá vàng SJC và trang sức từ các nguồn tin cậy (SJC, PNJ, WebGia).
    *   Cập nhật các chỉ số vĩ mô thế giới (Dow Jones, Nikkei, Bitcoin, Dầu thô...).
2.  **Agent Hải Quan (Customs)**:
    *   Thu thập số liệu kim ngạch xuất nhập khẩu hàng ngày/tháng từ Tổng cục Hải quan.
    *   Sử dụng công nghệ Playwright Interception để vượt qua các lớp bảo vệ bot nghiệp dư.
3.  **Agent Dệt May (VITAS)**:
    *   Thu thập tin tức mới nhất từ Hiệp hội Dệt may Việt Nam.
4.  **Agent Vinatex**:
    *   Thu thập thông tin hoạt động và thông báo từ Tập đoàn Dệt may Việt Nam.

## 🛠️ Hướng dẫn cài đặt

### 1. Cài đặt Python & Dependencies
Đảm bảo bạn đã cài đặt Python 3.10+.
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Cấu hình Môi trường
Tạo file `.env` từ `.env.example` và điền các thông tin:
*   `SPREADSHEET_ID`: ID của Google Sheet.
*   `GOOGLE_CREDENTIALS_JSON`: Nội dung file JSON chứng chỉ Google (hoặc để file `excel_key.json` cùng thư mục).

## 📖 Hướng dẫn sử dụng (Local)

### Chạy toàn bộ hệ thống
```bash
python main.py --agents all
```

### Thiết lập bảng tính (Tạo 8 Tabs và Headers)
```bash
python main.py --setup --agents all
```

### Chạy riêng lẻ từng Agent
```bash
python main.py --agents customs
python main.py --agents cafef
```

## 🤖 Tự động hóa với GitHub Actions

Hệ thống đã được cấu hình tự động chạy vào **8:00** và **14:00** hàng ngày (giờ Việt Nam).

**Để kích hoạt, bạn cần thêm 2 Secrets vào GitHub Repository:**
1.  `SPREADSHEET_ID`: ID của Google Sheet.
2.  `GOOGLE_CREDENTIALS_JSON`: Nội dung file JSON (excel_key.json).

## 📁 Cấu trúc thư mục
*   `agents/`: Chứa mã nguồn của các crawler.
*   `core/`: Chứa các module quản lý cấu hình, base class và Google Sheets.
*   `.github/workflows/`: Cấu hình chạy tự động hàng ngày.
*   `logs/`: Chứa log các lần chạy.
