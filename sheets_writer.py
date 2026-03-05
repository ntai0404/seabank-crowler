# ============================================================
# sheets_writer.py — Ghi dữ liệu vào Google Sheets
# Sử dụng Service Account xác thực qua excel_key.json
# Schema sheet: timestamp | source | metric_name | metric_value | meta_json
# ============================================================

import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import SPREADSHEET_ID, SCOPES, CREDENTIALS_FILE


def _get_sheets_service():
    """
    Khởi tạo Google Sheets API service bằng Service Account.

    Returns:
        googleapiclient.discovery.Resource — Sheets API service object.

    Raises:
        FileNotFoundError: Nếu file credentials không tồn tại.
    """
    # Kiểm tra file credentials tồn tại
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"Không tìm thấy file xác thực: {CREDENTIALS_FILE}\n"
            "Hãy đảm bảo file excel_key.json đã có trong thư mục project."
        )

    # Tạo credentials từ Service Account key
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
    )

    # Build Sheets API service
    service = build("sheets", "v4", credentials=creds)
    return service


def append_rows(sheet_name: str, rows: list[list]) -> dict | None:
    """
    Ghi (append) dữ liệu vào Google Sheets.

    Mỗi row phải tuân theo schema:
        [timestamp, source, metric_name, metric_value, meta_json]

    Args:
        sheet_name: Tên sheet cần ghi (vd: "web_metrics").
        rows: Dữ liệu dạng mảng 2 chiều — list[list].

    Returns:
        dict — Response từ API nếu thành công, None nếu lỗi.

    Cấu hình:
        - valueInputOption = "RAW"         → Ghi nguyên value, format ở Superset
        - insertDataOption = "INSERT_ROWS" → Chèn hàng mới, không ghi đè
    """
    # Kiểm tra dữ liệu đầu vào
    if not rows:
        print(f"[SHEETS] Khong co du lieu de ghi vao sheet '{sheet_name}'.")
        return None

    try:
        service = _get_sheets_service()

        # Build list of lists for API (bỏ meta_json column if None)
        # Ghi dữ liệu vào sheet (Append)
        body = {"values": rows}
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{sheet_name}!A1",
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )
        print(f"[SHEETS] Cap nhat thanh cong '{sheet_name}'. So hang: {len(rows)}, So o thay doi: {result.get('updates', {}).get('updatedCells', 0)}.")
        return result

    except FileNotFoundError as e:
        print(f"[SHEETS] {e}")
        return None
    except HttpError as err:
        print(f"[SHEETS] Loi API khi ghi vao sheet '{sheet_name}': {err}")
        return None
    except Exception as e:
        print(f"[SHEETS] Loi khong xac dinh khi ghi sheet '{sheet_name}': {e}")
        return None
