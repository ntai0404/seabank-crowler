import sys
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import SPREADSHEET_ID, CREDENTIALS_FILE

def reset_spreadsheet():
    """Xóa toàn bộ dữ liệu (từ dòng 2) và reset format màu nền về trắng."""
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    sheets_service = build("sheets", "v4", credentials=creds)

    print(f"Ket noi Spreadsheet ID: {SPREADSHEET_ID}")
    
    try:
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    except Exception as e:
        print(f"Loi ket noi: {e}")
        return

    requests_body = []
    
    # tabs cần xử lý
    target_sheets = ["web_metrics", "stock_prices", "exchange_rates", "gold_prices", "macro_indicators", "customs_trade", "bank_interest_rates", "textile_news", "banking_news"]
    
    for sheet in spreadsheet.get("sheets", []):
        sheet_name = sheet["properties"]["title"]
        if sheet_name not in target_sheets:
            continue
            
        sheet_id = sheet["properties"]["sheetId"]
        
        # 1. Clear data from row 2 (index 1) onwards
        requests_body.append({
            "updateCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1
                },
                "fields": "userEnteredValue"
            }
        })
        
        # 2. Reset format to white background, normal text
        requests_body.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                        "textFormat": {
                            "bold": False,
                            "foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0}
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        })

    print("Dang thuc hien Reset toan bo Sheet (Clear data & Color)...")
    try:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": requests_body},
        ).execute()
        print("Reset thanh cong! Sheet gio da sach se.")
    except HttpError as e:
        print(f"Loi: {e}")

if __name__ == "__main__":
    reset_spreadsheet()
