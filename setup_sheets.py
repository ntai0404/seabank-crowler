# ============================================================
# setup_sheets.py — Khởi tạo tất cả Google Sheets tabs + headers
#
# Chạy 1 lần duy nhất khi:
#   - Setup project lần đầu
#   - Thêm tab mới vào Google Sheets
#
# Sử dụng: python setup_sheets.py [--reset sheet_name]
# ============================================================

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Setup Google Sheets cho SeaBank Crawler")
    parser.add_argument(
        "--reset",
        nargs="*",
        metavar="SHEET",
        help="Xóa dữ liệu (giữ header) của các sheet chỉ định, hoặc '--reset' để xóa tất cả",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Liệt kê tất cả sheet tabs và schema của chúng",
    )
    args = parser.parse_args()

    from core.sheets_manager import setup_all_sheets, clear_sheet_data, SHEET_HEADERS

    if args.list:
        print("\n📋 Danh sách tất cả Sheet Tabs:\n")
        for name, headers in SHEET_HEADERS.items():
            print(f"  📄 {name}")
            print(f"     Columns: {' | '.join(headers)}\n")
        return

    if args.reset is not None:
        targets = args.reset if args.reset else list(SHEET_HEADERS.keys())
        print(f"\n🗑️  Xóa dữ liệu (giữ header) của: {', '.join(targets)}")
        confirm = input("Xác nhận? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Hủy.")
            return
        for sheet_name in targets:
            clear_sheet_data(sheet_name)
        print("✅ Hoàn tất reset.")
        return

    # Mặc định: setup tất cả
    print("\n🚀 Đang setup Google Sheets...")
    print("   Spreadsheet: https://docs.google.com/spreadsheets/d/1QBbKfdaEPsAwNWjIS9g71bnLoqAOMX75kQAM4KeJwng\n")
    setup_all_sheets()
    print("\n✅ Setup hoàn tất! Bạn có thể chạy: python main.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nĐã hủy.")
        sys.exit(0)
