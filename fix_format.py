import sys
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import SPREADSHEET_ID, CREDENTIALS_FILE

def fix_format():
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    sheets_service = build("sheets", "v4", credentials=creds)

    print(f"Ket noi Spreadsheet ID: {SPREADSHEET_ID}")
    
    # Get all sheets
    try:
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    except Exception as e:
        print(f"Loi ket noi: {e}")
        return

    requests_body = []
    
    for sheet in spreadsheet.get("sheets", []):
        sheet_id = sheet["properties"]["sheetId"]
        
        # Reset formatting for everything from row index 1 (row 2) 
        # to the end of the sheet to normal white background and black text
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

    print("Dang gui request xoa format spam...")
    try:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": requests_body},
        ).execute()
        print("Sua loi format thanh cong!")
    except HttpError as e:
        print(f"Loi the hien format: {e}")

if __name__ == "__main__":
    fix_format()
