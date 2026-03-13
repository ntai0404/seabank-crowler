import argparse
from datetime import datetime

from core.sheets_manager import _build_service, SHEET_HEADERS
from core.config import SPREADSHEET_ID


def parse_target_date(date_text: str):
    """Accept dd/mm/yyyy or yyyy-mm-dd and normalize to date object."""
    date_text = (date_text or "").strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_text, fmt).date()
        except ValueError:
            continue
    raise ValueError("Date must be dd/mm/yyyy or yyyy-mm-dd")


def parse_timestamp_cell(value: str):
    """Extract date from timestamp-like cell values in multiple common formats."""
    text = str(value or "").strip()
    if not text:
        return None

    # Fast path for typical crawler timestamp format: YYYY-MM-DD HH:MM:SS
    head = text[:10]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(head, fmt).date()
        except ValueError:
            continue

    # Fallback: try full datetime formats
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    return None


def build_contiguous_ranges(row_numbers):
    """Convert sorted row numbers into contiguous [start, end] ranges."""
    if not row_numbers:
        return []

    ranges = []
    start = prev = row_numbers[0]
    for n in row_numbers[1:]:
        if n == prev + 1:
            prev = n
            continue
        ranges.append((start, prev))
        start = prev = n
    ranges.append((start, prev))
    return ranges


def main():
    parser = argparse.ArgumentParser(
        description="Delete rows whose timestamp is on a target date across selected sheets."
    )
    parser.add_argument(
        "--date",
        required=True,
        help="Target date in dd/mm/yyyy or yyyy-mm-dd, e.g. 13/03/2026",
    )
    parser.add_argument(
        "--sheets",
        nargs="+",
        default=[
            "web_metrics",
            "stock_prices",
            "exchange_rates",
            "gold_prices",
            "macro_indicators",
            "customs_trade",
            "bank_interest_rates",
            "textile_news",
            "vinatex_news",
            "banking_news",
        ],
        help="Sheets to process. Default is common crawler output tabs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print rows to be deleted, do not delete anything.",
    )
    args = parser.parse_args()

    target_date = parse_target_date(args.date)
    service = _build_service()

    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    all_sheets = {
        s["properties"]["title"]: s["properties"]["sheetId"]
        for s in spreadsheet.get("sheets", [])
    }

    total_rows_deleted = 0

    for sheet_name in args.sheets:
        if sheet_name not in all_sheets:
            print(f"[SKIP] Sheet not found: {sheet_name}")
            continue
        if sheet_name not in SHEET_HEADERS:
            print(f"[SKIP] Sheet not in known schema: {sheet_name}")
            continue

        sheet_id = all_sheets[sheet_name]
        # Column A contains timestamp in this project schema.
        values_resp = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!A2:A",
        ).execute()

        values = values_resp.get("values", [])
        if not values:
            print(f"[OK] {sheet_name}: no data")
            continue

        # Actual row number = index + 2 because data starts at row 2
        matched_rows = []
        for idx, row in enumerate(values):
            cell = row[0] if row else ""
            row_date = parse_timestamp_cell(cell)
            if row_date == target_date:
                matched_rows.append(idx + 2)

        if not matched_rows:
            print(f"[OK] {sheet_name}: no rows on {target_date}")
            continue

        print(f"[MATCH] {sheet_name}: {len(matched_rows)} rows on {target_date}")

        if args.dry_run:
            continue

        # Delete bottom-up to keep row indexes stable.
        ranges = build_contiguous_ranges(matched_rows)
        requests = []
        for start, end in reversed(ranges):
            requests.append(
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "ROWS",
                            "startIndex": start - 1,
                            "endIndex": end,
                        }
                    }
                }
            )

        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": requests},
        ).execute()

        total_rows_deleted += len(matched_rows)
        print(f"[DELETE] {sheet_name}: removed {len(matched_rows)} rows")

    print(f"\n[DONE] Total removed rows: {total_rows_deleted}")


if __name__ == "__main__":
    main()
