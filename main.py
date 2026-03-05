# ============================================================
# main.py — Orchestrator: chạy tất cả 4 agents → Google Sheets
#
# Pipeline:
#   CafeFAgent   → stock_prices, exchange_rates, gold_prices, macro_indicators, web_metrics
#   CustomsAgent → customs_trade
#   TextileAgent → textile_news
#   VinatexAgent → vinatex_news
#
# Chạy: python main.py [--agents cafef customs textile vinatex]
# ============================================================

import sys
import time
import argparse
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(
        description="SeaBank Data Crawler — Agent Pipeline"
    )
    parser.add_argument(
        "--agents",
        nargs="+",
        choices=["cafef", "customs", "textile", "vinatex", "all"],
        default=["all"],
        help="Chọn agent cần chạy (mặc định: all)",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Chạy setup Google Sheets (tạo tabs + headers) trước khi crawl",
    )
    return parser.parse_args()


def run_pipeline(agents_to_run: list[str], setup: bool = False) -> dict:
    """
    Chạy các agent được chỉ định và gộp kết quả.
    Trả về summary tổng hợp { sheet_name: total_rows }.
    """
    from core.sheets_manager import setup_all_sheets
    from agents.cafef_agent   import CafeFAgent
    from agents.customs_agent import CustomsAgent
    from agents.textile_agent import TextileAgent
    from agents.vinatex_agent import VinatexAgent

    if setup:
        print("\n[MAIN] Chạy setup Google Sheets...")
        setup_all_sheets()

    AGENT_MAP = {
        "cafef":   CafeFAgent,
        "customs": CustomsAgent,
        "textile": TextileAgent,
        "vinatex": VinatexAgent,
    }

    run_all = "all" in agents_to_run
    summary: dict[str, int] = {}

    for name, AgentClass in AGENT_MAP.items():
        if run_all or name in agents_to_run:
            print(f"\n{'━'*55}")
            print(f"  🤖 Khởi động agent: {name.upper()}")
            print(f"{'━'*55}")
            agent = AgentClass()
            result = agent.run()
            for sheet, count in result.items():
                summary[sheet] = summary.get(sheet, 0) + count

    return summary


def main():
    args  = parse_args()
    start = time.time()

    print("=" * 60)
    print("  SeaBank Data Crawler — Agent Pipeline")
    print(f"  Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Agents: {', '.join(args.agents)}")
    print("=" * 60)

    try:
        summary = run_pipeline(args.agents, setup=args.setup)
    except KeyboardInterrupt:
        print("\n\n[!] Đã hủy bởi người dùng.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Lỗi nghiêm trọng: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)

    elapsed = time.time() - start
    total   = sum(summary.values())

    print("\n" + "=" * 60)
    print("  ✅ HOÀN THÀNH PIPELINE")
    print("=" * 60)
    print(f"\n  {'Sheet Tab':<22} {'Số hàng':>8}")
    print(f"  {'-'*32}")
    for sheet, count in sorted(summary.items()):
        icon = "✅" if count > 0 else "⚠️ "
        print(f"  {icon} {sheet:<20} {count:>8,}")
    print(f"  {'-'*32}")
    print(f"  {'TỔNG CỘNG':<22} {total:>8,}")
    print(f"\n  ⏱  Thời gian: {elapsed:.1f}s")
    print(f"  📊 Xem dữ liệu: https://docs.google.com/spreadsheets/d/1QBbKfdaEPsAwNWjIS9g71bnLoqAOMX75kQAM4KeJwng")


if __name__ == "__main__":
    main()
