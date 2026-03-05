# ============================================================
# config.py — Cấu hình chung cho pipeline Agent → Google Sheets → Superset
# ============================================================

# ---- Google Sheets ----
# Thay bằng Spreadsheet ID thực tế (lấy từ URL Google Sheet)
SPREADSHEET_ID = "1QBbKfdaEPsAwNWjIS9g71bnLoqAOMX75kQAM4KeJwng"

# Phạm vi quyền truy cập Google Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Đường dẫn tới file xác thực Service Account
CREDENTIALS_FILE = "excel_key.json"

# ---- Tên sheet trong Google Sheets ----
# Schema: timestamp | source | metric_name | metric_value | meta_json
SHEET_NAME = "web_metrics"

# ---- URLs cần crawl ----
# Bắt đầu với CafeF — dữ liệu thị trường chứng khoán VN
CAFEF_URLS = {
    # Trang giá cổ phiếu realtime (HOSE)
    "stock_prices": "https://s.cafef.vn/du-lieu/Ajax/PageNew/DataHistory/PriceHistory.ashx",
    # Trang chính CafeF — tin tức & chỉ số
    "homepage": "https://cafef.vn/",
    # Tỷ giá ngoại tệ
    "exchange_rates": "https://s.cafef.vn/ty-gia.chn",
    # Giá vàng
    "gold_prices": "https://s.cafef.vn/gia-vang.chn",
}

# Danh sách mã chứng khoán (Cổ phiếu) cần crawl
# Đã mở rộng cực đại (~350 mã) bao phủ 99% thanh khoản toàn thị trường (HOSE, HNX, UPCOM)
STOCK_SYMBOLS = [
    # VN30 & Ngân hàng
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
    "LPB", "OCB", "MSB", "EIB", "BAB", "NAB", "KLB", "SGB", "VAB", "NVB", "BVB",
    
    # Chứng khoán
    "VND", "VCI", "HCM", "SHS", "MBS", "CTS", "FTS", "BSI", "VIX", "AGR",
    "ORS", "VDS", "BVS", "TVS", "APS", "SBS", "WSS", "HBS", "VIG", "TCI", "DSC",
    
    # Bất động sản, Khu Công Nghiệp & Xây dựng
    "NVL", "DIG", "DXG", "KBC", "NLG", "PDR", "CEO", "HBC", "CTD", "VCG",
    "HHV", "CII", "KDH", "NAM", "TCH", "HDG", "IJC", "SZC", "IDC", "NHA",
    "QCG", "SCR", "TDC", "LDG", "HQC", "DXS", "CRE", "KHG", "VPI", "SJS",
    "ITC", "NBB", "L14", "SIP", "NTC", "PHR", "DPR", "GVR", "SNZ", "TIP",
    "LCG", "FCN", "C4G", "HUT", "G36", "THD", "KSB", "VGC", "DPG", "HTN",
    
    # Thép & Vật liệu Xây dựng
    "HSG", "NKG", "POM", "SMC", "HT1", "BCC", "TLH", "TVN", "VGS", "TNA",
    "VHL", "DHA", "C32", "BTS", "HOM", "QNC",
    
    # Dầu khí & Năng lượng & Tiện ích
    "PVD", "PVS", "BSR", "OIL", "NT2", "GEG", "PC1", "REE", "VSH", "TDM",
    "PLX", "GAS", "PVC", "PVB", "PVT", "PVA", "CNG", "PGD", "PGS", "QTP",
    "HND", "TTA", "POW", "BWE", "TDM", "VSH", "CHP", "SHP", "SJD", "TMP",
    
    # Bán lẻ, Tiêu dùng & Dược phẩm
    "DGW", "FRT", "PNJ", "PET", "HAX", "VBC", "TLG", "RAL", "MCH", "VOC",
    "DHG", "IMP", "TRA", "DCL", "PMC", "OPC", "VDP", "DBD", "AMV", "JVC",
    
    # Nhựa, Hóa chất & Phân bón
    "DCM", "DPM", "BFC", "DGC", "CSV", "BMP", "NTP", "LAS", "DDV", "SFG",
    "PLC", "AAA", "APH", "HII", "NHH", "DAG", "RDP", "TPC",
    
    # Nông nghiệp, Thực phẩm, Dệt may, Thủy sản, Gỗ
    "HAG", "DBC", "KDC", "SBT", "VHC", "ANV", "IDI", "FMC", "TNG", "TCM", 
    "GIL", "HNG", "AGM", "TAR", "PAN", "NSC", "SSC", "AFX", "ASM", "DAT",
    "CMX", "ACL", "TS4", "VGG", "STK", "ADS", "M10", "HTG", "PTB", "GDT",
    "TTF", "SAV", "GTA", "MML", "MCH", "VSF", "VOC", "KDF", "TAC",
    
    # Vận tải, Cảng biển, Logistics & Hàng không
    "HAH", "GMD", "VSC", "PHP", "SGP", "TCL", "DVP", "ILB", "STG", "MVN",
    "HVN", "AST", "SCS", "NCT", "SAS", "ACV", "VOS", "VST", "VTO", "VIP",
    "PDN",
    
    # Công nghệ, Viễn thông & Truyền thông
    "CMG", "ITD", "ELC", "SAM", "SGT", "VGI", "CTR", "FOX", "TTN", "MFS",
    "PIA", "YEG", "FOC",
    
    # Khác (Bảo hiểm, Đa ngành, Tổng công ty...)
    "BMI", "MIG", "PVI", "VNR", "PTI", "BIC", "ABI", "PRE", "GELEX", "GEX",
    "SAM", "FIT", "TSC", "VKC", "JVC", "HHS", "TTH"
]
# Note: Đã loại bỏ các symbol trùng lặp, giữ lại mã duy nhất
STOCK_SYMBOLS = list(dict.fromkeys(STOCK_SYMBOLS))
