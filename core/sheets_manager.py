# ============================================================
# core/sheets_manager.py — Quản lý Google Sheets (append, setup, clear)
# ============================================================

import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials

from core.config import SPREADSHEET_ID, SCOPES, get_credentials_source

# ---- Schema headers cho từng tab ----
SHEET_HEADERS: dict[str, list[str]] = {
    "web_metrics":      ["timestamp", "source", "metric_name", "metric_value", "meta_json"],
    "stock_prices":     ["timestamp", "symbol", "ngay", "gia_mo_cua", "gia_cao_nhat",
                         "gia_thap_nhat", "gia_dong_cua", "thay_doi", "khoi_luong", "gia_tri"],
    "exchange_rates":   ["timestamp", "currency", "buy_cash", "buy_transfer", "sell"],
    "gold_prices":      ["timestamp", "gold_type", "buy_price", "sell_price"],
    "macro_indicators": ["timestamp", "index_name", "price", "change_percent"],
    "customs_trade":    ["timestamp", "source", "category", "period",
                         "value_usd", "unit", "meta_json"],
    "textile_news":     ["timestamp", "source", "title", "url",
                         "category", "published_date", "summary"],
    "vinatex_news":     ["timestamp", "source", "title", "url",
                         "lang", "published_date", "summary"],
    "banking_news":     ["timestamp", "source", "title", "url",
                         "category", "published_date", "summary"],
    "bank_interest_rates": ["timestamp", "bank_name", "term", "rate", "type"],
    "customs_commodity_details": ["timestamp", "category", "period", "export_value", "import_value", "change_pct"],
    "textile_directory": ["timestamp", "company_name", "business_type", "address", "website"],
}


def _build_service():
    """Khởi tạo Google Sheets API service (hỗ trợ cả local file & GitHub Actions JSON)."""
    source_type, value = get_credentials_source()
    if source_type == "json":
        creds = Credentials.from_service_account_info(value, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(value, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def append_rows(sheet_name: str, rows: list[list]) -> dict | None:
    """
    Append dữ liệu vào tab Google Sheets.

    Args:
        sheet_name: Tên tab (vd: "stock_prices")
        rows: Dữ liệu dạng list[list]

    Returns:
        API response dict hoặc None nếu lỗi.
    """
    if not rows:
        print(f"[SHEETS] Bỏ qua '{sheet_name}': không có dữ liệu.")
        return None
    try:
        service = _build_service()
        body = {"values": rows}
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{sheet_name}!A1",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )
        updated = result.get("updates", {}).get("updatedCells", 0)
        print(f"[SHEETS] ✅ '{sheet_name}': +{len(rows)} hàng ({updated} ô)")
        return result
    except HttpError as e:
        print(f"[SHEETS] ❌ Lỗi API '{sheet_name}': {e}")
    except Exception as e:
        print(f"[SHEETS] ❌ Lỗi không xác định '{sheet_name}': {e}")
    return None


def setup_all_sheets() -> None:
    """
    Tạo tất cả tab sheets và ghi header row nếu tab chưa có dữ liệu.
    Gọi khi chạy lần đầu hoặc reset project.
    """
    service = _build_service()
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    existing = {s["properties"]["title"] for s in spreadsheet.get("sheets", [])}

    requests_batch = []
    for sheet_name in SHEET_HEADERS:
        if sheet_name not in existing:
            requests_batch.append({
                "addSheet": {"properties": {"title": sheet_name}}
            })
            print(f"[SETUP] Tạo tab mới: '{sheet_name}'")
        else:
            print(f"[SETUP] Tab đã tồn tại: '{sheet_name}'")

    if requests_batch:
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": requests_batch},
        ).execute()

    # Ghi header cho tab nào chưa có
    for sheet_name, headers in SHEET_HEADERS.items():
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=SPREADSHEET_ID, range=f"{sheet_name}!A1:A1")
            .execute()
        )
        if not result.get("values"):
            append_rows(sheet_name, [headers])
            print(f"[SETUP] Đã ghi header cho '{sheet_name}'")

    print("[SETUP] ✅ Hoàn tất setup tất cả sheet tabs.")


def clear_sheet_data(sheet_name: str) -> None:
    """Xóa dữ liệu (giữ header) của một tab."""
    try:
        service = _build_service()
        # Lấy range A2 đến cuối
        service.spreadsheets().values().clear(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!A2:ZZ",
        ).execute()
        print(f"[SHEETS] 🗑️  Đã xóa dữ liệu tab '{sheet_name}' (giữ header).")
    except HttpError as e:
        print(f"[SHEETS] ❌ Lỗi khi xóa '{sheet_name}': {e}")
