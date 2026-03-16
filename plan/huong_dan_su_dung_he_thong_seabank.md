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

G. Tab gold_prices - Giá vàng SJC

Mục đích: Theo dõi giá mua bán vàng SJC theo từng loại sản phẩm.

Các cột:
- timestamp: thời điểm crawler ghi dữ liệu.
- gold_type: tên loại vàng, ví dụ Vàng SJC 1L, 10L, 1KG.
- buy_price: giá mua vào.
- sell_price: giá bán ra.

H. Tab customs_commodity_details - Chi tiết xuất nhập khẩu theo kỳ

Mục đích: Theo dõi kim ngạch xuất khẩu và nhập khẩu theo từng kỳ báo cáo của Tổng cục Hải quan.

Các cột:
- timestamp: thời điểm crawler ghi dữ liệu.
- category: nhóm dữ liệu, ví dụ Xuất khẩu hoặc Nhập khẩu.
- period: kỳ báo cáo, ví dụ K1-T2-2026.
- export_value: kim ngạch xuất khẩu tỷ USD.
- import_value: kim ngạch nhập khẩu tỷ USD.
- change_pct: biến động so với kỳ trước.

I. Tab textile_directory - Danh bạ hội viên VITAS

Mục đích: Lưu thông tin các doanh nghiệp hội viên của Hiệp hội Dệt may Việt Nam VITAS.

Các cột:
- timestamp: thời điểm crawler ghi dữ liệu.
- company_name: tên doanh nghiệp.
- business_type: loại hình sản xuất, ví dụ May mặc, Dệt vải, Nhuộm, Kéo sợi.
- address: địa chỉ.
- phone: số điện thoại.

J. Các tab phụ khác

- macro_indicators: chỉ số vĩ mô quốc tế.
- vinatex_news: tin tức từ Vinatex.
- banking_news: tin tức ngân hàng và bất động sản từ CafeF.

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

Cơ chế bảo vệ dữ liệu lịch sử:

Tất cả các agent đều có UPSERT_KEY_COLUMNS. Trước khi ghi dữ liệu mới, hệ thống tự động xóa các hàng trùng key trong cùng ngày rồi mới append. Nhờ đó dữ liệu của các ngày trước không bao giờ bị ảnh hưởng khi chạy lại agent nhiều lần trong cùng một ngày.

Lịch chạy hiện tại trong GitHub Actions:

- 01:00 UTC, tương đương 08:00 giờ Việt Nam.
- 07:00 UTC, tương đương 14:00 giờ Việt Nam.

Workflow có hỗ trợ chạy tay với các tham số:

- agents: chọn all hoặc từng agent.
- setup: true hoặc false để tạo tab và header lần đầu.

1.3. Preset: các biểu đồ hiện có

Dashboard hiện có 11 biểu đồ, mỗi biểu đồ nằm trên một hàng riêng để hiển thị rõ ràng:

Biểu đồ 1 - So sánh Lãi suất huy động giữa các Ngân hàng

Loại biểu đồ: Cột nhóm theo kỳ hạn (1 tháng, 3 tháng, 6 tháng, 12 tháng...).
Nội dung: So sánh lãi suất huy động của nhiều ngân hàng trên cùng một khung nhìn. Mỗi nhóm cột là một kỳ hạn, mỗi cột là một ngân hàng.
Dùng để làm gì: Nhận diện nhanh ngân hàng nào đang trả lãi cao nhất hoặc thấp nhất theo từng kỳ hạn, phục vụ theo dõi cạnh tranh lãi suất huy động trên thị trường.

Biểu đồ 2 - Biến động % Cổ phiếu Ngân hàng (Top 12 mã)

Loại biểu đồ: Đường thời gian (line chart) theo ngày.
Nội dung: Hiển thị 12 mã cổ phiếu ngân hàng lớn gồm VCB, BID, CTG, MBB, ACB, TCB, VPB, STB, LPB, HDB, SHB, TPB. Trục dọc là phần trăm tăng hoặc giảm so với phiên đầu tiên trong bộ dữ liệu, không phải giá tuyệt đối.
Lý do dùng %: Vì các mã có giá rất khác nhau, ví dụ VCB ở vùng 90 trong khi có mã chỉ ở vùng 10, nếu vẽ theo giá tuyệt đối thì các mã thấp giá sẽ bị nén sát trục và không đọc được biến động. Dùng % giúp so sánh hiệu suất thực sự của các mã trên cùng một thước đo.
Dùng để làm gì: Theo dõi xu hướng nhóm cổ phiếu ngân hàng trong trung và dài hạn, phát hiện mã nào vượt trội hoặc tụt hậu so với nhóm.
Lưu ý: Muốn xem giá đóng cửa cụ thể từng phiên, dùng biểu đồ số 8.

Biểu đồ 3 - So sánh Kim ngạch Xuất nhập khẩu Hải quan

Loại biểu đồ: Cột nhóm.
Nội dung: Hiển thị tổng kim ngạch xuất khẩu và nhập khẩu theo dữ liệu tổng hợp từ Tổng cục Hải quan, đơn vị tỷ USD.
Dùng để làm gì: Theo dõi cán cân thương mại, so sánh xuất siêu hay nhập siêu qua từng kỳ cập nhật.

Biểu đồ 4 - Danh sách Tin tức Ngân hàng và Bất động sản mới nhất

Loại biểu đồ: Bảng dữ liệu có thể nhấp vào tiêu đề để mở bài viết.
Nội dung: Liệt kê các bài viết mới nhất được thu thập từ CafeF về chủ đề ngân hàng và bất động sản. Mỗi dòng gồm tiêu đề, ngày đăng và đường dẫn bài viết.
Dùng để làm gì: Cập nhật nhanh tin tức thị trường tài chính và bất động sản mà không cần rời khỏi dashboard.

Biểu đồ 5 - Danh sách Tin tức Ngành Dệt may mới nhất

Loại biểu đồ: Bảng dữ liệu tương tự biểu đồ 4.
Nội dung: Tin tức từ nguồn VITAS về ngành dệt may, sợi, nguyên phụ liệu và thị trường xuất khẩu.
Dùng để làm gì: Theo dõi diễn biến ngành dệt may phục vụ đánh giá rủi ro cho vay doanh nghiệp dệt may.

Biểu đồ 6 - Tỷ giá Ngoại tệ Vietcombank

Loại biểu đồ: Bảng tra cứu.
Nội dung: Tỷ giá mua vào và bán ra của các ngoại tệ phổ biến như USD, EUR, JPY, AUD được cập nhật từ bảng tỷ giá Vietcombank.
Dùng để làm gì: Tra cứu nhanh tỷ giá tham chiếu phục vụ nghiệp vụ ngoại hối hoặc so sánh với tỷ giá nội bộ của ngân hàng.

Biểu đồ 7 - So sánh Lãi suất Tiền gửi kỳ hạn 12 tháng

Loại biểu đồ: Cột nằm ngang hoặc cột đứng theo ngân hàng.
Nội dung: So sánh riêng lãi suất tiền gửi kỳ hạn 12 tháng giữa các ngân hàng, tách biệt với biểu đồ 1 để dễ nhìn hơn cho kỳ hạn dài.
Dùng để làm gì: Đánh giá vị thế cạnh tranh lãi suất tiền gửi trung dài hạn, phục vụ họp hội đồng lãi suất hoặc báo cáo định kỳ cho ban lãnh đạo.

Biểu đồ 8 - Bảng Giá Cổ phiếu Ngân hàng chi tiết

Loại biểu đồ: Bảng tra cứu có tìm kiếm và sắp xếp.
Nội dung: Hiển thị dữ liệu từng phiên giao dịch gồm giá mở cửa, giá cao nhất, giá thấp nhất, giá đóng cửa và phần trăm thay đổi. Bao gồm 24 mã cổ phiếu ngân hàng trong danh sách theo dõi.
Dùng để làm gì: Tra cứu giá cụ thể của một mã trong một ngày bất kỳ, xuất dữ liệu cho báo cáo phân tích riêng.

Biểu đồ 9 - Giá vàng SJC mới nhất theo loại

Loại biểu đồ: Thanh ngang (horizontal bar), sắp xếp giảm dần theo giá bán.
Nội dung: Hiển thị giá bán ra của từng loại vàng SJC trong ngày gần nhất, đơn vị triệu VND trên lượng. Tên loại vàng được rút gọn để dễ đọc, ví dụ SJC 1L-1KG, Nhẫn 99.99 1-5 chỉ.
Dùng để làm gì: Theo dõi diễn biến giá vàng trong nước, tham chiếu khi xử lý nghiệp vụ liên quan đến tài sản đảm bảo là vàng.

Biểu đồ 10 - Xuất khẩu vs Nhập khẩu theo kỳ báo cáo

Loại biểu đồ: Cột nhóm đứng, mỗi nhóm là một kỳ báo cáo.
Nội dung: Hiển thị kim ngạch xuất khẩu và nhập khẩu theo từng kỳ ngắn hạn của Tổng cục Hải quan như K1-T2/26, K2-T2/26, đơn vị tỷ USD. Trục thời gian sắp xếp theo thứ tự kỳ báo cáo từ cũ đến mới.
Dùng để làm gì: Nhìn thấy xu hướng ngắn hạn của hoạt động ngoại thương trong tháng hiện tại, phát hiện biến động bất thường giữa các nửa tháng.

Biểu đồ 11 - Cơ cấu Hội viên VITAS Top6 + Khác

Loại biểu đồ: Thanh ngang (horizontal bar), sắp xếp từ nhiều doanh nghiệp nhất đến ít nhất.
Nội dung: Phân loại các doanh nghiệp hội viên VITAS theo nhóm ngành sản xuất gồm May mặc, Dệt vải, Nhuộm/hoàn tất, Kéo sợi, Nguyên phụ liệu, Máy thiết bị và nhóm Khác. Hiển thị 6 nhóm lớn nhất và gộp phần còn lại vào nhóm Khác.
Dùng để làm gì: Hiểu cơ cấu ngành dệt may Việt Nam theo số lượng doanh nghiệp, phục vụ phân tích danh mục cho vay và đánh giá mức độ tập trung rủi ro theo phân ngành.

Lưu ý về Preset cache:

Preset cache chart cũ theo UUID slice. Khi import bản mới, luôn chọn Overwrite và hard refresh trình duyệt sau khi import để tránh thấy biểu đồ phiên bản cũ. Nếu chart vẫn hiển thị tên hoặc dữ liệu cũ sau khi import, thử xóa cache trình duyệt hoặc mở tab ẩn danh.

Cập nhật dashboard:

Mỗi lần cần cập nhật cấu hình hiển thị, kỹ thuật viên chạy lại `python preset_integration/preset_builder.py` trên máy cục bộ để tạo file ZIP mới, rồi import vào Preset với tùy chọn Overwrite. Không cần sửa chart trực tiếp trên giao diện Preset.

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
- Theo dõi 11 biểu đồ theo nhu cầu nghiệp vụ.
- Nếu thấy số liệu cũ, bấm refresh dashboard. Nếu vẫn chưa cập nhật, báo quản trị để kiểm tra lịch chạy crawler hoặc cache Preset.
- Lưu ý đặc biệt: Biểu đồ cổ phiếu số 2 hiển thị % biến động so với đầu kỳ, không phải giá tuyệt đối. Muốn xem giá cụ thể từng phiên, dùng bảng giá cổ phiếu số 8.

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
