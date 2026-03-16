# Project Milestone & Status Report: SeaBank Crawler

> **Cập nhật lần cuối:** 2026-03-16 | **Commit hiện tại:** `2528dca`

---

## 🚀 Milestones Đã Hoàn Thành

### 1. Core Crawler Engine (Agent-based)
- Xây dựng thành công hệ thống Agent đa nhiệm: `CafeFAgent`, `CustomsAgent`, `TextileAgent`, `VinatexAgent`.
- Khả năng cào dữ liệu đa phương thức: JSON API, HTML Parsing và Playwright Browser Automation.
- Cơ chế xử lý số liệu (Parsing) chịu lỗi tốt, hỗ trợ format tiếng Việt.

### 2. Google Sheets Integration
- Tự động hóa việc khởi tạo tab, ghi Header và Append dữ liệu định kỳ.
- Xây dựng công cụ `reset_all_data.py` để quản trị dữ liệu sạch.
- **Spreadsheet ID:** `1QBbKfdaEPsAwNWjIS9g71bnLoqAOMX75kQAM4KeJwng` (locale: `en_US`)

### 3. GitHub Actions Automation (v2.0)
- Tự động hóa hoàn toàn việc cào dữ liệu 2 lần/ngày trên Cloud.
- Tự động cài đặt môi trường trình duyệt (Playwright) và xử lý bảo mật (Secrets) an toàn.
- Cơ chế chống lỗi "404 Not Found" do ký tự rác trong cấu hình.


### 4. Preset.io Dashboard (now 11 charts) ✅
- **Workspace:** `86253470.us2a.app.preset.io`
- **preset_builder.py** đọc `assets/` → build `dist/` → đóng gói ZIP → import vào Preset
- Dashboard hiện có **11 charts** trên nhiều hàng (full-width khi cần):

| Row | Tên chart | Dataset | Width |
|-----|-----------|---------|-------|
| ROW-1 | So sánh Lãi suất huy động (các kỳ hạn) | bank_interest_rates | 6 |
| ROW-1 | Biến động % Cổ phiếu Ngân hàng (Top 12) | stock_prices | 6 |
| ROW-2 | So sánh Kim ngạch Xuất nhập khẩu (Hải quan) | customs_trade | 12 |
| ROW-3 | Danh sách Tin tức Ngân hàng & BĐS | web_metrics | 12 |
| ROW-3 | Danh sách Tin tức Ngành Dệt may | textile_news | 12 |
| ROW-4 | Tỷ giá Ngoại tệ Vietcombank (Mua/Bán) | exchange_rates | 5 |
| ROW-4 | So sánh Lãi suất Tiền gửi 12 tháng | bank_interest_rates | 7 |
| ROW-5 | Bảng Giá Cổ phiếu chi tiết (24 mã) | stock_prices | 12 |
| ROW-6 | Giá vàng SJC mới nhất theo loại | gold_prices | 6 |
| ROW-6 | Xuất khẩu vs Nhập khẩu theo kỳ | customs_commodity_details | 6 |
| ROW-7 | Cơ cấu Hội viên VITAS Top6 + Khác | textile_directory | 12 |

---

## 📦 Cấu trúc UUID cố định (5518f6ce series)

| Asset | UUID suffix |
|-------|-------------|
| Database (Google Sheets) | `...929110` |
| DS: bank_interest_rates | `...929111` |
| DS: stock_prices | `...929112` |
| DS: textile_news | `...929113` |
| DS: web_metrics | `...929114` |
| DS: customs_trade | `...929115` |
| DS: exchange_rates | `...929117` |
| CHART: interest_rate_bar | `...929121` |
| CHART: stock_trend_line | `...929122` |
| CHART: customs_trade_mixed | `...929123` |
| CHART: web_metrics_table | `...929124` |
| CHART: textile_news_table | `...929125` |
| CHART: exchange_rates_table | `...929126` |
| CHART: bank_stocks_table | `...929127` |
| CHART: interest_rate_12m_bar | `...929149` ← đổi nhiều lần do Preset cache |

> ⚠️ **Lưu ý quan trọng:** Khi chart bị cache cứng trong Preset (import đè không ăn), phải **đổi UUID** sang số mới để Preset tạo chart hoàn toàn mới. Pattern UUID: `5518f6ce-d922-4857-8478-41d81a9291XX` (XX tăng dần).

---

## 🗂️ Schema Google Sheets (SHEET_HEADERS trong core/sheets_manager.py)

| Tab | Columns |
|-----|---------|
| `stock_prices` | timestamp, symbol, ngay, gia_mo_cua, gia_cao_nhat, gia_thap_nhat, gia_dong_cua, thay_doi, khoi_luong, gia_tri |
| `exchange_rates` | timestamp, currency, buy_cash, buy_transfer, sell |
| `bank_interest_rates` | timestamp, bank_name, term, rate, type |
| `customs_trade` | timestamp, ... (7 bản ghi/lần crawl) |
| `textile_news` | timestamp, title, url, category, summary, date, source |
| `web_metrics` | timestamp, category, title, url, ... |
| `macro_indicators` | timestamp, source, name, value, meta |

---

## 🐛 Lịch sử Bug quan trọng & Cách fix

### Bug 1 — Textile news hiển thị nav items thay vì bài báo
- **Nguyên nhân:** Selector `div.pl_item` cũng bắt photo gallery/navigation
- **Fix:** Đổi sang `div.pl_c` (featured cards) + `div.ucHotPost > .pl_display_list`
- **Dedup:** Theo article ID `_4-NNNN` trong URL (không dùng full URL)
- **Date:** Fetch từ trang bài viết riêng (`pc_datetime`)

### Bug 2 — Lỗi decimal parsing ("," thay vì ".")
- **Fix:** `cafef_agent._parse_num()` xử lý cả dấu phẩy lẫn dấu chấm

### Bug 3 — Google Sheets locale vi_VN → số viết dạng "1.234,56"
- **Fix:** Đổi locale sheets sang `en_US` trong `setup_sheets.py`

### Bug 4 — Chart `interest_rate_12m_bar` lỗi liên tiếp:
1. `viz_type: bar` → "Datetime column required" → đổi sang `dist_bar`
2. `dist_bar` với `columns: []` → "Duplicate label: bank_name" (Preset migrate thành `bar` mới, set bank_name ở cả x_axis lẫn groupby)
3. `echarts_bar` → "Item with key echarts_bar is not registered" (không hỗ trợ)
- **Fix cuối cùng:** Dùng `dist_bar` + `columns: [term]` + `groupby: [bank_name]` + `WHERE term = '12 tháng'` — giống hệt pattern của chart `interest_rate_bar` đang chạy tốt, đổi UUID mới `...929149` để tránh Preset cache cũ.

### Bug 5 — Columns missing trong `bank_stocks_table`
- **Nguyên nhân:** `stock_prices` dataset YAML chỉ khai báo 2 columns (symbol, gia_dong_cua), thiếu ngay, gia_mo_cua, gia_cao_nhat, gia_thap_nhat
- **Fix:** Bổ sung đủ 9 columns vào `assets/datasets/stock_prices.yaml`

---

## 📍 Trạng thái hiện tại (2026-03-11)

### ✅ Đã hoàn thành
- 8 charts định nghĩa đầy đủ trong YAML
- preset_builder.py build thành công ZIP
- ZIP mới nhất: `seabank_dashboard_20260311T110205.zip`
- Tất cả fixes đã push lên GitHub (commit `2540157`)

### ⏳ Đang chờ xác nhận
- Import ZIP `seabank_dashboard_20260311T110205.zip` vào Preset → Verify chart lãi suất 12 tháng hiển thị đúng
- Sync columns cho `stock_prices` dataset trong Preset UI (nếu bank_stocks_table vẫn báo missing columns)

### 🔧 Nếu chart lãi suất 12 tháng vẫn lỗi sau import
Vào Preset UI: **Charts** → tìm chart cũ UUID `...929128`, `...929139` → **Delete** thủ công → import lại ZIP.

---

## 🔑 Thông tin kết nối

- **Google Sheets ID:** `1QBbKfdaEPsAwNWjIS9g71bnLoqAOMX75kQAM4KeJwng`
- **Preset workspace:** `86253470.us2a.app.preset.io/superset/dashboard/seabank-monitor/`
- **GitHub repo:** `https://github.com/ntai0404/seabank-crowler.git`
- **Python:** `C:\Users\pc\AppData\Local\Programs\Python\Python310\python.exe`

---

## 📋 Quy trình làm việc chuẩn

```powershell
# 1. Reset + crawl lại toàn bộ
python reset_all_data.py
python main.py

# 2. Rebuild ZIP
python preset_integration/preset_builder.py

# 3. Push GitHub
git add -A
git commit -m "..."
git push

# 4. Import ZIP vào Preset
# Settings → Import → chọn seabank_dashboard_*.zip (mới nhất) → Overwrite
# Sau import: Force Refresh dashboard để xóa cache
```
