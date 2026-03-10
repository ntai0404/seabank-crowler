# 📦 Hướng dẫn Import Dashboard vào Preset.io

## ✅ Các vấn đề đã được khắc phục (v1.34 - Dataset Parameters Fix)

### 1. **Schema Validation & Manifest**
- ✅ ZIP structure đã được chuyển sang **flat format** (metadata.yaml ở root)
- ✅ metadata.yaml có đúng `type: assets`
- ✅ **metadata.yaml chứa full manifest:** `databases`, `datasources`, `charts`, `dashboards`
- ✅ **Tất cả files sử dụng JSON format** (không phải YAML) để tránh lỗi parsing
- ✅ Tất cả UUID được mapping chính xác giữa Charts, Datasets và Dashboard

### 2. **Database Connection**
- ✅ **Thêm database definition file:** `databases/google_sheets.yaml`
- ✅ Database UUID có thể config qua `config.yaml` (hiện tại: `482b5b73-c5e8-4f35-a665-7236f5a0904b`)
- ✅ Google Sheets connection với spreadsheet_id được inject từ config
- ✅ Schema name: `SeaBank_Data` cho tất cả datasets
- ✅ Thêm đầy đủ `parents` field cho tất cả layout nodes (GRID_ID, ROW-*, CHART-*)
- ✅ Có `DASHBOARD_VERSION_KEY: v2` và `ROOT_ID` structure đúng chuẩn Superset
- ✅ Mỗi chart có đầy đủ `meta` với `uuid`, `height`, `width`, `sliceName`

### 3. **Rendering Crash Prevention**
- ✅ UTF-8 encoding được bảo đảm với `ensure_ascii=False` trong JSON dump
- ✅ JSON format native support Unicode, không cần escape
- ✅ Tất cả tên tiếng Việt hiển thị chính xác

### 4. **Unicode & Encoding**
- ✅ UTF-8 encoding được bảo đảm với `ensure_ascii=False` trong JSON dump
- ✅ JSON format native support Unicode, không cần escape
- ✅ Tất cả tên tiếng Việt hiển thị chính xác

### 5. **Dataset Parameters (Complete)**
- ✅ **All required fields added:**
  - `is_managed_externally`, `cache_timeout`, `offset`, `fetch_values_predicate`
  - `extra` field with resource_type and certification metadata
- ✅ **Enhanced columns:** `is_active`, `filterable`, `groupby`, `expression`, `python_date_format`
- ✅ **Enhanced metrics:** `metric_type`, `d3format`, `warning_text`
- ✅ Schema: `SeaBank_Data` (Google Sheets catalog name)

### 6. **Error Fixes**
- ✅ **"Expecting value: line 1 column 1"** → Fixed: All files use JSON format
- ✅ **"'datasources'"** → Fixed: Added datasources array to metadata
- ✅ **"Dataset parameters are invalid"** → Fixed: Added all required dataset fields
- ✅ **Missing database** → Fixed: Included database connection file

---

## 🚀 Cách Import vào Preset.io

### Bước 1: Kiểm tra Database Connection
1. Đăng nhập vào **Preset.io** workspace của bạn
2. Vào **Settings** > **Database Connections**
3. Tìm database có tên **"SeaBank_Data"** hoặc Google Sheets connection của bạn
4. Copy **Database UUID** (dạng `482b5b73-c5e8-4f35-a665-7236f5a0904b`)
5. Nếu UUID khác, update vào `preset_integration/config.yaml`:
   ```yaml
   database_uuid: "YOUR_UUID_HERE"
   ```
6. Chạy lại: `python preset_integration/preset_builder.py`

### Bước 2: Import ZIP File
1. Vào **Dashboards** tab trên Preset.io
2. Click nút **"Import"** (biểu tượng tải lên)
3. Chọn file `seabank_preset_assets.zip` từ thư mục root project
4. Click **"Import"**

### Bước 3: Xác nhận Import thành công
Sau khi import, bạn sẽ thấy:
- ✅ **5 Datasets** mới:
  - `bank_interest_rates`
  - `stock_prices`
  - `customs_trade`
  - `textile_news`
  - `web_metrics`
  
- ✅ **5 Charts** mới:
  - So sánh Lãi suất huy động giữa các Ngân hàng (Bar Chart)
  - Biến động Giá Cổ phiếu Ngân hàng & BĐS (Line Chart)
  - So sánh Kim ngạch Xuất nhập khẩu (Mixed Chart)
  - Thống kê Tin tức theo Chủ đề (Table)
  - Danh sách Tin tức Ngành Dệt may mới nhất (Table)

- ✅ **1 Dashboard**:
  - SeaBank Financial Monitor (Hệ thống Giám sát Tài chính)

---

## 🛠️ Troubleshooting

### ❌ Lỗi "Dataset parameters are invalid"
**Nguyên nhân:** Dataset definition thiếu các required fields

**Giải pháp:**
- ✅ Đã fix! Dataset giờ có đầy đủ fields (v1.34+)
- Thêm: is_managed_externally, cache_timeout, offset, fetch_values_predicate, extra
- Column/metric enhancements đã được thêm
- Nếu vẫn lỗi, pull code mới nhất và build lại

### ❌ Lỗi "'datasources'"
**Nguyên nhân:** metadata.yaml thiếu datasources array

**Giải pháp:**
- ✅ Đã fix! metadata.yaml giờ chứa full manifest (v1.33+)
- metadata bao gồm: databases, datasources, charts, dashboards
- Nếu vẫn lỗi, pull lại code mới nhất và build lại

### ❌ Lỗi "Expecting value: line 1 column 1 (char 0)"
**Nguyên nhân:** Preset.io yêu cầu JSON format, không phải YAML

**Giải pháp:**
- ✅ Đã fix! Tất cả files bây giờ sử dụng JSON format (v1.32+)
- Nếu vẫn lỗi, pull lại code mới nhất và build lại

### ❌ Lỗi "Missing database" khi xem chart
**Nguyên nhân:** Database UUID trong config không khớp với Preset workspace

**Giải pháp:**
1. Lấy đúng Database UUID từ Preset.io (Settings > Database Connections)
2. Update vào `preset_integration/config.yaml`
3. Build lại: `python preset_integration/preset_builder.py`
4. Re-import ZIP file

### ❌ Lỗi "Invalid metadata format"
**Nguyên nhân:** ZIP structure không đúng

**Giải pháp:**
1. Xác nhận ZIP có structure flat (không có folder cha):
   ```
   metadata.yaml
   charts/
   dashboards/
   datasets/
   ```
2. Nếu có folder cha (vd: `seabank_export_v31/`), code bị rollback. Pull lại git.

### ❌ Dashboard render lỗi (TypeError: background)
**Nguyên nhân:** Thiếu parents field hoặc layout properties

**Giải pháp:**
1. Kiểm tra `assets/dashboards/seabank_monitor.yaml` có đầy đủ `parents` field
2. Nếu không, pull lại git để lấy template mới nhất
3. Build lại preset assets

### ❌ Tên tiếng Việt bị lỗi font
**Nguyên nhân:** Encoding không đúng hoặc Preset theme issue

**Giải pháp:**
1. Preset.io hỗ trợ UTF-8 mặc định, không cần fix gì thêm
2. Nếu vẫn lỗi, check Preset workspace settings > Theme > Font

---

## 📝 Cập nhật Dashboard Title hoặc Config

Để thay đổi tiêu đề dashboard hoặc config khác:

1. Edit file `preset_integration/config.yaml`:
   ```yaml
   dashboard_title: "Tên Dashboard Mới của Bạn"
   spreadsheet_id: "ID_Google_Sheet_Mới"
   database_uuid: "UUID_Database_Mới"
   ```

2. Build lại:
   ```bash
   python preset_integration/preset_builder.py
   ```

3. Import lại ZIP file vào Preset.io, full manifest
├── databases/
│   └── google_sheets.yaml      # Database connection definition

---

## 📊 Asset Structure

```
seabank_preset_assets.zip
├── metadata.yaml               # Version 1.0.0, type: assets
├── charts/
│   ├── interest_rate_bar.yaml
│   ├── stock_trend_line.yaml
│   ├── customs_trade_mixed.yaml
│   ├── web_metrics_table.yaml
│   └── textile_news_table.yaml
├── datasets/
│   ├── bank_interest_rates.yaml
│   ├── stock_prices.yaml
│   ├── customs_trade.yaml
│   ├── web_metrics.yaml
│   └── textile_news.yaml
└── dashboards/
    └── seabank_monitor.yaml    # Layout với đầy đủ parents field
```

---

## 🎯 Next Steps

Sau khi import thành công:
1. Kiểm tra từng2 - JSON Formatông (click vào từng chart)
2. Nếu thiếu data → Run crawler: `python main.py`
3. Configure refresh schedule trên Preset.io (Settings > Refresh)
4. Share dashboard với team (Share button)

---

**Version:** 1.31 - Native Mirror Fix  
**Last Updated:** March 9, 2026  
**Contact:** ntai0404@gmail.com
