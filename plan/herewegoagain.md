# Project Milestone & Status Report: SeaBank Crawler

## 🚀 Milestones Đã Hoàn Thành

### 1. Core Crawler Engine (Agent-based)
- Xây dựng thành công hệ thống Agent đa nhiệm: `CafeFAgent`, `CustomsAgent`, `TextileAgent`, `VinatexAgent`.
- Khả năng cào dữ liệu đa phương thức: JSON API, HTML Parsing và Playwright Browser Automation.
- Cơ chế xử lý số liệu (Parsing) chịu lỗi tốt, hỗ trợ format tiếng Việt.

### 2. Google Sheets Integration
- Tự động hóa việc khởi tạo tab, ghi Header và Append dữ liệu định kỳ.
- Xây dựng công cụ `reset_all_data.py` để quản trị dữ liệu sạch.

### 3. GitHub Actions Automation (v2.0)
- Tự động hóa hoàn toàn việc cào dữ liệu 2 lần/ngày trên Cloud.
- Tự động cài đặt môi trường trình duyệt (Playwright) và xử lý bảo mật (Secrets) an toàn.
- Cơ chế chống lỗi "404 Not Found" do ký tự rác trong cấu hình.

---

## ⚠️ Vấn Đề Duy Nhất Hiện Tại: Preset Integration

Mặc dù hệ thống dữ liệu đã chạy rất mượt, nhưng phần **Tích hợp Dashboard lên Preset.io** vẫn đang là "nút thắt cổ chai" với các vấn đề sau:

### 1. Schema Validation (metadata.yaml)
- Preset yêu cầu cấu trúc file ZIP cực kỳ khắt khe (phẳng vs phân cấp).
- Lỗi liên tục về trường `version`, `type: Dashboard` và các UUID mapping giữa Chart và Dataset.

### 2. Rendering Crash (TypeError: background)
- Các asset import lên đôi khi làm sập giao diện Superset do thiếu các thuộc tính layout mặc định (`ROOT_ID`, `v2`, `parents`).
- Xung đột CSS tùy chỉnh làm lỗi render trên môi trường Preset Cloud.

### 3. Unicode & Theme Escape
- Tên tiếng Việt trong các file YAML đôi khi bị mã hóa sai sau khi nén ZIP, dẫn đến Preset không thể nạp được các thuộc tính theme/font.

### 4. Database Connection Mapping
- Việc map UUID của Database thủ công trên Preset với các Dataset tự động tạo ra vẫn chưa đạt độ ổn định 100%, thỉnh thoảng gây lỗi "Missing table" khi xem biểu đồ.

---
**📍 Hướng xử lý tiếp theo:** Tập trung vào giải pháp "Native Mirror" (Bản gương tối giản) - chỉ trích xuất những gì Preset thực sự cần, loại bỏ mọi tham số layout phức tạp để ưu tiên việc nạp thành công Dashboard trước.
