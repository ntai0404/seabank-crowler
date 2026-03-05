# ============================================================
# core/config.py — Load cấu hình từ .env (python-dotenv)
# ============================================================

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env nếu tồn tại (khi chạy local)
_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file)

# ---- Google Sheets ----
SPREADSHEET_ID: str = os.environ["SPREADSHEET_ID"]
SCOPES: list[str] = ["https://www.googleapis.com/auth/spreadsheets"]

# ---- Credentials ----
# Ưu tiên: biến môi trường JSON (GitHub Actions) → file local
_cred_json_str: str | None = os.environ.get("GOOGLE_CREDENTIALS_JSON")
_cred_file: str             = os.environ.get("CREDENTIALS_FILE", "excel_key.json")

def get_credentials_source() -> tuple[str, str | dict]:
    """
    Trả về (source_type, value):
      - ("json",  dict)  nếu có GOOGLE_CREDENTIALS_JSON (GitHub Actions)
      - ("file", "path") nếu có credentials file (local)
    """
    if _cred_json_str:
        return ("json", json.loads(_cred_json_str))
    if Path(_cred_file).exists():
        return ("file", _cred_file)
    raise FileNotFoundError(
        f"Không tìm thấy credentials.\n"
        f"  - Biến môi trường GOOGLE_CREDENTIALS_JSON chưa được set, VÀ\n"
        f"  - File '{_cred_file}' không tồn tại.\n"
        f"  Hãy tạo file .env từ .env.example và điền đầy đủ."
    )

# ---- Crawl settings ----
STOCK_HISTORY_DAYS: int   = int(os.environ.get("STOCK_HISTORY_DAYS", "7"))
REQUEST_DELAY: float       = float(os.environ.get("REQUEST_DELAY", "0.5"))
REQUEST_TIMEOUT: int       = int(os.environ.get("REQUEST_TIMEOUT", "15"))
PLAYWRIGHT_TIMEOUT: int    = int(os.environ.get("PLAYWRIGHT_TIMEOUT", "45000"))

# ---- Sheet tab names ----
SHEETS: dict[str, str] = {
    # CafeF
    "web_metrics":      "web_metrics",       # Tổng hợp tất cả
    "stock_prices":     "stock_prices",      # Giá cổ phiếu
    "exchange_rates":   "exchange_rates",    # Tỷ giá ngoại tệ
    "gold_prices":      "gold_prices",       # Giá vàng
    "macro_indicators": "macro_indicators",  # Chỉ số thế giới
    # Hải quan
    "customs_trade":    "customs_trade",     # Kim ngạch XNK
    # Dệt may
    "textile_news":     "textile_news",      # Tin tức VITAS
    "vinatex_news":     "vinatex_news",      # Tin tức Vinatex
}

# ---- Danh sách mã chứng khoán (~350 mã, bao phủ 99% thanh khoản) ----
STOCK_SYMBOLS: list[str] = list(dict.fromkeys([
    # VN30 & Ngân hàng
    "ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG",
    "MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB",
    "TCB","TPB","VCB","VHM","VIB","VIC","VJC","VNM","VPB","VRE",
    "LPB","OCB","MSB","EIB","BAB","NAB","KLB","SGB","VAB","NVB","BVB",
    # Chứng khoán
    "VND","VCI","HCM","SHS","MBS","CTS","FTS","BSI","VIX","AGR",
    "ORS","VDS","BVS","TVS","APS","SBS","WSS","HBS","VIG","TCI","DSC",
    # BĐS & Xây dựng
    "NVL","DIG","DXG","KBC","NLG","PDR","CEO","HBC","CTD","VCG",
    "HHV","CII","KDH","TCH","HDG","IJC","SZC","IDC","QCG","SCR",
    "TDC","LDG","HQC","DXS","CRE","KHG","VPI","SJS","ITC","NBB",
    "L14","SIP","NTC","PHR","DPR","SNZ","TIP","LCG","FCN","C4G",
    "HUT","G36","THD","KSB","VGC","DPG","HTN",
    # Thép & VLXD
    "HSG","NKG","POM","SMC","HT1","BCC","TLH","TVN","VGS","TNA",
    "VHL","DHA","C32","BTS","HOM","QNC",
    # Dầu khí & Năng lượng
    "PVD","PVS","BSR","OIL","NT2","GEG","PC1","REE","VSH","TDM",
    "PVC","PVB","PVT","PVA","CNG","PGD","PGS","QTP","HND","TTA",
    "BWE","CHP","SHP","SJD","TMP",
    # Bán lẻ, Tiêu dùng & Dược
    "DGW","FRT","PNJ","PET","HAX","TLG","RAL","MCH","DHG","IMP",
    "TRA","DCL","PMC","OPC","VDP","DBD","AMV","JVC",
    # Nhựa, Hóa chất & Phân bón
    "DCM","DPM","BFC","DGC","CSV","BMP","NTP","LAS","DDV","SFG",
    "PLC","AAA","APH","HII","NHH","DAG","RDP","TPC",
    # Nông nghiệp, Thực phẩm, Dệt may, Thủy sản, Gỗ
    "HAG","DBC","KDC","SBT","VHC","ANV","IDI","FMC","TNG","TCM",
    "GIL","HNG","AGM","TAR","PAN","NSC","SSC","AFX","ASM","DAT",
    "CMX","ACL","TS4","VGG","STK","ADS","M10","HTG","PTB","GDT",
    "TTF","SAV","GTA","MML","VSF","KDF","TAC",
    # Vận tải, Cảng biển & Hàng không
    "HAH","GMD","VSC","PHP","SGP","TCL","DVP","ILB","STG","MVN",
    "HVN","AST","SCS","NCT","SAS","ACV","VOS","VST","VTO","VIP","PDN",
    # Công nghệ & Viễn thông
    "CMG","ITD","ELC","SAM","SGT","VGI","CTR","FOX","TTN","MFS",
    "PIA","YEG","FOC",
    # Bảo hiểm & Đa ngành
    "BMI","MIG","PVI","VNR","PTI","BIC","ABI","PRE","GEX",
    "FIT","TSC","VKC","HHS","TTH",
]))
