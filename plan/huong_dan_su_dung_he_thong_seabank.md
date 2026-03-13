HƯỚNG DẪN SỬ DỤNG HỆ THỐNG SEABANK DATA CRAWLER

Tài liệu này dành cho nhân viên SeaBank sử dụng hệ thống theo dõi dữ liệu tài chính tự động bằng Google Sheets và Preset Dashboard, đồng thời hỗ trợ kỹ thuật viên khi cần tự triển khai phiên bản mới.

Thông tin truy cập hiện tại

Link Google Sheets:
https://docs.google.com/spreadsheets/d/1QBbKfdaEPsAwNWjIS9g71bnLoqAOMX75kQAM4KeJwng

Link Preset Dashboard:
https://86253470.us2a.app.preset.io/superset/dashboard/seabank-monitor/

Link GitHub Repository:
https://github.com/ntai0404/seabank-crowler

1. Giới thiệu các thành phần của hệ thống

1.1. Google Sheets: các bảng dữ liệu và ý nghĩa cột

Hệ thống hiện ghi dữ liệu vào nhiều tab trong cùng một Google Sheet. Dưới đây là ý nghĩa nghiệp vụ của từng tab và các cột quan trọng.

A. Tab bank_interest_rates - Lãi suất ngân hàng

Mục đích: Theo dõi lãi suất huy động theo ngân hàng và kỳ hạn.

Các cột:
- timestamp: thời điểm crawler ghi dữ liệu.
- bank_name: tên ngân hàng.
- term: kỳ hạn, ví dụ 1 tháng, 3 tháng, 12 tháng.
- rate: lãi suất theo phần trăm một năm.
- type: loại lãi suất huy động.

B. Tab stock_prices - Giá cổ phiếu

Mục đích: Theo dõi giá của danh sách mã ngân hàng và các mã liên quan.

Các cột:
- timestamp: thời điểm crawler ghi dữ liệu.
- symbol: mã cổ phiếu như VCB, BID, CTG, MBB, ACB, TCB.
- ngay: ngày giao dịch từ nguồn dữ liệu.
- gia_mo_cua: giá mở cửa.
- gia_cao_nhat: giá cao nhất.
- gia_thap_nhat: giá thấp nhất.
- gia_dong_cua: giá đóng cửa.
- thay_doi: mức thay đổi.
- khoi_luong: khối lượng giao dịch.
- gia_tri: giá trị giao dịch.

C. Tab exchange_rates - Tỷ giá

Mục đích: Theo dõi tỷ giá mua bán ngoại tệ, ưu tiên nguồn Vietcombank và CafeF.

Các cột:
- timestamp: thời điểm crawler ghi dữ liệu.
- currency: mã ngoại tệ như USD, EUR, AUD.
- buy_cash: giá mua tiền mặt.
- buy_transfer: giá mua chuyển khoản.
- sell: giá bán.

D. Tab customs_trade - Xuất nhập khẩu Hải quan

Mục đích: Theo dõi số liệu xuất nhập khẩu từ Tổng cục Hải quan.

Các cột:
- timestamp: thời điểm crawler ghi dữ liệu.
- source: nguồn dữ liệu.
- category: nhóm thống kê.
- period: kỳ dữ liệu ngày hoặc tháng.
- value_usd: giá trị USD.
- unit: đơn vị.
- meta_json: thông tin mở rộng.

E. Tab textile_news - Tin dệt may VITAS

Mục đích: Theo dõi tin tức dệt may mới nhất.

Các cột:
- timestamp: thời điểm ghi dữ liệu.
- source: nguồn tin.
- title: tiêu đề bài viết.
- url: liên kết bài viết.
- category: chuyên mục.
- published_date: ngày đăng.
- summary: tóm tắt.

F. Tab web_metrics - Tin tức hoặc metrics tổng hợp

Mục đích: Tổng hợp metric hoặc tin tức theo chủ đề tài chính.

Các cột:
- timestamp
- source
- metric_name
- metric_value
- meta_json

G. Các tab phụ khác

- macro_indicators: chỉ số vĩ mô quốc tế.
- gold_prices: giá vàng nếu nguồn có dữ liệu hợp lệ.
- vinatex_news: tin từ Vinatex.
- customs_commodity_details và textile_directory: tab mở rộng theo nhu cầu.

1.2. Agent bot: code đang chạy trên GitHub Actions

Hệ thống có 4 agent chính, được điều phối bởi file main.py:

- CafeFAgent: lấy dữ liệu cổ phiếu, tỷ giá, vàng, chỉ số vĩ mô.
- CustomsAgent: lấy dữ liệu hải quan xuất nhập khẩu.
- TextileAgent: lấy tin tức từ VITAS.
- VinatexAgent: lấy tin tức từ Vinatex.

Luồng chạy của hệ thống:

1. GitHub Actions kích hoạt theo lịch hoặc chạy thủ công.
2. Môi trường chạy cài Python, thư viện phụ thuộc và Playwright Chromium.
3. Hệ thống chạy lệnh python main.py --agents all hoặc chỉ định từng agent.
4. Các agent crawl dữ liệu, chuẩn hóa dữ liệu và ghi vào Google Sheets.

Lịch chạy hiện tại trong GitHub Actions:

- 01:00 UTC, tương đương 08:00 giờ Việt Nam.
- 07:00 UTC, tương đương 14:00 giờ Việt Nam.

Workflow có hỗ trợ chạy tay với các tham số:

- agents: chọn all hoặc từng agent.
- setup: true hoặc false để tạo tab và header lần đầu.

1.3. Preset: các biểu đồ hiện có

Dashboard hiện có 8 biểu đồ chính:

1. So sánh lãi suất huy động giữa các ngân hàng.
2. Biến động giá cổ phiếu ngân hàng và các mã liên quan.
3. So sánh kim ngạch xuất nhập khẩu Hải quan.
4. Thống kê tin tức theo chủ đề trong 24 giờ gần nhất.
5. Danh sách tin tức ngành dệt may mới nhất.
6. Tỷ giá ngoại tệ Vietcombank theo giá mua và giá bán.
7. So sánh lãi suất tiền gửi kỳ hạn 12 tháng.
8. Bảng giá cổ phiếu ngân hàng như VCB, BID, CTG, MBB, ACB, TCB.

Lưu ý:

Preset đôi khi cache chart cũ theo UUID. Khi có lỗi hiển thị kéo dài, quản trị có thể phải import bản mới hoặc cập nhật lại chart trong bộ asset.

2. Cách sử dụng hệ thống hiện tại

Mục tiêu phần này là người dùng chỉ cần email công việc để được cấp quyền, không cần cài đặt kỹ thuật.

Bước 1. Gửi email để được cấp quyền

Người dùng gửi cho quản trị hệ thống các thông tin sau:

- Email công việc SeaBank để được cấp quyền Google Sheets.
- Email dùng cho Preset, nếu khác email công việc thì ghi rõ.

Quản trị sẽ thêm người dùng vào:

- Google Sheets với quyền xem hoặc chỉnh sửa tùy vai trò.
- Preset workspace với quyền phù hợp.

Bước 2. Truy cập và sử dụng Google Sheets

- Mở link Google Sheets của dự án.
- Chọn tab dữ liệu cần xem như bank_interest_rates, stock_prices, exchange_rates, customs_trade.
- Có thể dùng bộ lọc hoặc sắp xếp theo timestamp hoặc symbol để đối chiếu số liệu.

Bước 3. Truy cập và sử dụng Dashboard Preset

- Mở dashboard Preset của hệ thống SeaBank Monitor.
- Theo dõi 8 biểu đồ theo nhu cầu nghiệp vụ.
- Nếu thấy số liệu cũ, bấm refresh dashboard. Nếu vẫn chưa cập nhật, báo quản trị để kiểm tra lịch chạy crawler hoặc cache Preset.

Bước 4. Quy trình báo lỗi chuẩn

Khi phát hiện dữ liệu bất thường, gửi cho quản trị các thông tin sau:

- Tên biểu đồ hoặc tab bị lỗi.
- Thời điểm phát hiện.
- Ảnh chụp màn hình nếu có.
- Ví dụ dữ liệu sai, khoảng 1 đến 2 dòng cụ thể.

3. Cách tự setup phiên bản mới

Phần này dành cho trường hợp cần triển khai hệ thống mới hoàn toàn: Sheet mới, Preset mới và repo riêng.

3.1. Tạo Google Sheet mới và Service Account JSON key mới

1. Tạo Google Sheet mới và đặt tên theo dự án.
2. Tạo Service Account trong Google Cloud hoặc dùng Service Account mới.
3. Tạo JSON key và tải file về, ví dụ excel_key.json.
4. Chia sẻ Google Sheet cho email service account với quyền Editor.
5. Lấy SPREADSHEET_ID từ URL của sheet.

3.2. Fork repo và setup GitHub Actions

Toàn bộ việc crawl dữ liệu tự động chạy trên server của GitHub, không cần máy tính cá nhân.

1. Đăng nhập GitHub bằng tài khoản hoặc tổ chức mới.
2. Truy cập repo gốc tại https://github.com/ntai0404/seabank-crowler.
3. Bấm nút Fork ở góc trên bên phải, chọn tài khoản đích và xác nhận fork.
4. Sau khi fork xong, vào repo vừa fork trên GitHub.
5. Mở Settings, vào Secrets and variables, chọn Actions.
6. Tạo 2 secrets bắt buộc:

- SPREADSHEET_ID: sheet ID mới đã tạo ở bước 3.1.
- GOOGLE_CREDENTIALS_JSON: toàn bộ nội dung file JSON key mới (mở file bằng Notepad và copy hết).

7. Vào tab Actions, enable workflow Daily Data Crawl nếu có thông báo yêu cầu.
8. Chạy thử bằng cách bấm Run workflow, chọn nhánh main, điền agents=all và bấm Run.
9. Theo dõi log chạy, xác nhận tất cả các bước hiển thị tích xanh và dữ liệu đã ghi vào sheet mới.

Lưu ý: Từ bước này trở đi hệ thống sẽ tự chạy 2 lần mỗi ngày lúc 08:00 và 14:00 giờ Việt Nam mà không cần thao tác thêm.

3.3. Setup trên Preset account mới

Lưu ý quan trọng: Toàn bộ cấu hình dashboard bao gồm biểu đồ, dataset và layout đều được tạo tự động bởi file code preset_integration/preset_builder.py có sẵn trong repo. Script này đọc các file cấu hình YAML trong thư mục assets, ghép lại và đóng gói thành file ZIP để import vào Preset. Người dùng không cần tạo biểu đồ thủ công trên giao diện Preset.

Để thực hiện phần này, cần kéo code về máy tính trước.

Bước A. Kéo code về máy tính

1. Cài Python 3.10 trở lên nếu chưa có.
2. Mở terminal hoặc Command Prompt, chạy lệnh sau để clone repo về máy:

git clone https://github.com/<ten-tai-khoan>/seabank-crowler.git

Thay <ten-tai-khoan> bằng tên tài khoản GitHub đã fork ở bước 3.2.

3. Di chuyển vào thư mục vừa clone:

cd seabank-crowler

4. Cài thư viện phụ thuộc:

pip install -r requirements.txt

Bước B. Cấu hình và build file dashboard

1. Mở file preset_integration/config.yaml bằng bất kỳ trình soạn thảo nào và cập nhật 2 thông tin:

- spreadsheet_id: điền sheet ID mới đã tạo ở bước 3.1.
- database_uuid: điền UUID lấy từ file ZIP export database của Preset (xem bước C bên dưới).

2. Build file ZIP dashboard bằng lệnh:

python preset_integration/preset_builder.py

3. Lệnh này sẽ tạo ra file có tên dạng seabank_dashboard_YYYYMMDDTHHMMSS.zip trong thư mục dự án.

Bước C. Lấy database_uuid từ Preset

Lưu ý quan trọng: Nhiều workspace Preset không hiển thị UUID database trên giao diện edit database. Cách chắc chắn nhất là lấy UUID từ file ZIP export.

1. Đăng nhập Preset, vào Settings, chọn Import/Export, sau đó export Database connection bạn vừa tạo.
2. Tải file ZIP export về máy, ví dụ database_export_YYYYMMDDTHHMMSS.zip.
3. Giải nén file ZIP.
4. Mở file trong thư mục databases, ví dụ:

databases/Seabank_Manual.yaml

5. Tìm dòng bắt đầu bằng uuid:, ví dụ:

uuid: 482b5b73-c5e8-4f35-a665-7236f5a0904b

6. Copy giá trị UUID này và dán vào preset_integration/config.yaml tại trường database_uuid.

Mẹo kiểm tra nhanh bằng PowerShell trong thư mục đã giải nén:

Select-String -Path .\databases\*.yaml -Pattern "^uuid:"

Bước D. Import dashboard vào Preset

1. Đăng nhập Preset, vào Settings, chọn Import.
2. Upload file ZIP vừa build.
3. Nếu có thông báo trùng tên dashboard, chọn Overwrite.
4. Mở dashboard SeaBank Monitor và kiểm tra từng biểu đồ hiển thị đúng dữ liệu.

3.4. Cài đặt local để chạy thủ công hoặc phát triển thêm

Phần này chỉ dành cho kỹ thuật viên muốn chạy crawler trên máy tính cá nhân hoặc mở rộng code.

1. Clone repo về máy:

git clone https://github.com/<ten-tai-khoan>/seabank-crowler.git

2. Cài dependencies:

pip install -r requirements.txt
playwright install chromium

3. Tạo file .env trong thư mục dự án và khai báo tối thiểu:

SPREADSHEET_ID=<sheet_id_moi>
CREDENTIALS_FILE=excel_key.json

4. Chạy setup tab và header lần đầu:

python main.py --setup --agents all

5. Chạy thử crawl:

python main.py --agents all

Phụ lục: Checklist bàn giao nhanh

- Đã có Google Sheet mới và service account có quyền Editor.
- Repo fork đã cập nhật secrets Actions.
- Workflow chạy thành công ít nhất 1 lần thủ công.
- Preset import dashboard thành công, các chart load được.
- Người dùng cuối đã được add email vào Sheet và Preset.

Tài liệu này có thể copy trực tiếp sang Word .docx để phát hành nội bộ.
