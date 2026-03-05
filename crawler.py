# ============================================================
# crawler.py — WebCrawlAgent: Crawl dữ liệu tài chính từ CafeF
#
# Chiến lược crawl:
#   - Giá cổ phiếu: JSON API (requests) — nhanh & ổn định
#   - Tỷ giá ngoại tệ: Playwright (headless) — trang render JS
#   - Giá vàng: Playwright (headless) — trang render JS
#
# Output theo schema web_metrics:
#   [timestamp, source, metric_name, metric_value, meta_json]
# ============================================================

import json
import requests
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from sheets_writer import append_rows
from config import STOCK_SYMBOLS, SHEET_NAME


class WebCrawlAgent:
    """
    Agent crawl dữ liệu tài chính từ CafeF.
    Pattern theo hướng dẫn PDF: crawl → parse → append_rows().
    """

    def __init__(self):
        self.source = "cafef.vn"
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
        }

    # ----------------------------------------------------------
    # Crawl 1: Giá cổ phiếu qua JSON API (requests — không cần Playwright)
    # ----------------------------------------------------------
    def crawl_stock_prices(self) -> list[list]:
        """
        Crawl giá cổ phiếu từ CafeF JSON API.
        Endpoint: s.cafef.vn/Ajax/PageNew/DataHistory/PriceHistory.ashx

        Returns:
            list[list] — schema: [timestamp, source, metric_name, metric_value, meta_json]
        """
        print(f"[AGENT] Crawl gia co phieu — {len(STOCK_SYMBOLS)} ma...")
        rows: list[list] = []

        # Lấy dữ liệu 7 ngày gần nhất
        end_date = datetime.now().strftime("%d/%m/%Y")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%d/%m/%Y")

        # Thiết lập session với retry logic
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))

        for symbol in STOCK_SYMBOLS:
            url = (
                f"https://s.cafef.vn/Ajax/PageNew/DataHistory/PriceHistory.ashx"
                f"?Symbol={symbol}"
                f"&StartDate={start_date}"
                f"&EndDate={end_date}"
                f"&PageIndex=1&PageSize=5"
            )

            try:
                # Thêm delay nhỏ để tránh bị block khi cào lượng lớn mã
                time.sleep(0.5) 
                
                resp = session.get(url, headers=self.headers, timeout=15)
                resp.raise_for_status()
                data = resp.json()

                # Parse JSON response
                records = data.get("Data", {}).get("Data", [])
                if not records:
                    print(f"  [!] {symbol}: Khong co du lieu")
                    continue

                # Lấy bản ghi mới nhất
                latest = records[0]
                price = latest.get("GiaDongCua", 0)
                meta = {
                    "symbol": symbol,
                    "ngay": latest.get("Ngay", ""),
                    "gia_mo_cua": latest.get("GiaMoCua", 0),
                    "gia_cao_nhat": latest.get("GiaCaoNhat", 0),
                    "gia_thap_nhat": latest.get("GiaThapNhat", 0),
                    "gia_dong_cua": price,
                    "thay_doi": latest.get("ThayDoi", ""),
                    "khoi_luong": latest.get("KhoiLuongKhopLenh", 0),
                    "gia_tri": latest.get("GiaTriKhopLenh", 0),
                }

                rows.append([
                    self.timestamp,
                    self.source,
                    f"stock_price_{symbol}",
                    price,
                    json.dumps(meta, ensure_ascii=False),
                ])
                print(f"  [+] {symbol}: {price}")

            except requests.RequestException as e:
                print(f"  [-] {symbol}: Loi request — {e}")
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                print(f"  [-] {symbol}: Loi parse JSON — {e}")

        print(f"[AGENT] Ket qua: {len(rows)}/{len(STOCK_SYMBOLS)} ma thanh cong.")
        return rows

    # ----------------------------------------------------------
    # Crawl 2: Tỷ giá ngoại tệ (Playwright — trang chính cafef.vn)
    # ----------------------------------------------------------
    def crawl_exchange_rates(self) -> list[list]:
        """Crawl tỷ giá ngoại tệ từ trang chủ CafeF."""
        url = "https://cafef.vn/"
        print(f"[AGENT] Crawl ty gia ngoai te tu: {url}")
        rows: list[list] = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                time.sleep(10) # Wait for ticker to load

                body_text = page.inner_text("body")
                lines = [l.strip() for l in body_text.split("\n") if l.strip()]

                currencies = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHR", "CNY"]
                import re

                for cur in currencies:
                    # Strategy 1: Look for exact word line matches
                    found = False
                    for i, line in enumerate(lines):
                        if line.upper() == cur.upper():
                            for j in range(i + 1, min(len(lines), i + 8)):
                                try:
                                    val_str = lines[j].replace(".", "").replace(",", ".")
                                    val = float(val_str)
                                    if val > 10:
                                        rows.append([self.timestamp, self.source, f"exchange_rate_{cur}", val, json.dumps({"currency": cur, "rate": val}, ensure_ascii=False)])
                                        print(f"  [+] FX: {cur} = {val}")
                                        found = True; break
                                except ValueError: pass
                            if found: break
                    
                    if not found:
                        # Strategy 2: Regex in full body
                        patterns = [
                            rf"{cur}\s*[:\-]?\s*([\d\.,]+)",
                            rf"([\d\.,]+)\s*{cur}"
                        ]
                        for pattern in patterns:
                            match = re.search(pattern, body_text, re.IGNORECASE)
                            if match:
                                try:
                                    val_str = match.group(1).replace(".", "").replace(",", ".")
                                    val = float(val_str)
                                    if val > 10:
                                        rows.append([self.timestamp, self.source, f"exchange_rate_{cur}", val, json.dumps({"currency": cur, "rate": val, "regex": True}, ensure_ascii=False)])
                                        print(f"  [+] FX (Regex): {cur} = {val}")
                                        break
                                except ValueError: pass

                browser.close()
            return rows
        except Exception as e:
            print(f"[AGENT] Loi crawl ty gia: {e}")
            return []

    # ----------------------------------------------------------
    # Crawl 3: Giá vàng (Playwright — cafef.vn homepage widget)
    # ----------------------------------------------------------
    def crawl_gold_prices(self) -> list[list]:
        """Crawl giá vàng từ trang chủ CafeF."""
        url = "https://cafef.vn/"
        print(f"[AGENT] Crawl gia vang tu: {url}")
        rows: list[list] = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                time.sleep(10)

                body_text = page.inner_text("body")
                lines = [l.strip() for l in body_text.split("\n") if l.strip()]
                import re

                gold_keywords = ["SJC", "DOJI", "PNJ", "Vàng thế giới"]
                for keyword in gold_keywords:
                    found = False
                    for i, line in enumerate(lines):
                        if keyword.lower() in line.lower() and len(line) < 30:
                            for j in range(i + 1, min(len(lines), i + 8)):
                                try:
                                    val_str = lines[j].replace(".", "").replace(",", ".")
                                    val = float(val_str)
                                    if val > 1000:
                                        rows.append([self.timestamp, self.source, f"gold_price_{keyword}", val, json.dumps({"gold_type": keyword, "price": val}, ensure_ascii=False)])
                                        print(f"  [+] Gold: {keyword} = {val}")
                                        found = True; break
                                except ValueError: pass
                            if found: break
                    
                    if not found:
                        match = re.search(rf"{keyword}[^\d]*([\d\.,]+)", body_text, re.IGNORECASE)
                        if match:
                            try:
                                val_str = match.group(1).replace(".", "").replace(",", ".")
                                val = float(val_str)
                                if val > 1000:
                                    rows.append([self.timestamp, self.source, f"gold_price_{keyword}", val, json.dumps({"gold_type": keyword, "price": val, "regex": True}, ensure_ascii=False)])
                                    print(f"  [+] Gold (Regex): {keyword} = {val}")
                            except ValueError: pass

                browser.close()
            return rows
        except Exception as e:
            print(f"[AGENT] Loi crawl gia vang: {e}")
            return []

    # ----------------------------------------------------------
    # Crawl 4: Chỉ số vĩ mô & Thế giới (JSON API — cafef.vn)
    # ----------------------------------------------------------
    def crawl_macro_indicators(self) -> list[list]:
        """
        Crawl chỉ số thế giới (DJ, Nikkei, Vàng thế giới, Dầu...)
        API: cafef.vn/du-lieu/ajax/mobile/smart/ajaxchisothegioi.ashx

        Returns:
            list[list] — schema: [timestamp, source, metric_name, metric_value, meta_json]
        """
        url = "https://cafef.vn/du-lieu/ajax/mobile/smart/ajaxchisothegioi.ashx"
        print(f"[AGENT] Crawl chi so vi mo/the gioi tu: {url}")
        rows: list[list] = []

        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            # API trả về object có field 'Data' là list các chỉ số
            items = data.get("Data", [])
            for item in items:
                index_name = item.get("index", "")
                price = item.get("last", 0)
                change_pct = item.get("changePercent", 0)

                if not index_name:
                    continue

                meta = {
                    "index_name": index_name,
                    "price": price,
                    "change": item.get("change", 0),
                    "change_percent": change_pct,
                    "high": item.get("high", 0),
                    "low": item.get("low", 0),
                    "last_update": item.get("lastUpdate", ""),
                }

                rows.append([
                    self.timestamp,
                    self.source,
                    f"macro_{index_name.lower().replace(' ', '_')}",
                    price,
                    json.dumps(meta, ensure_ascii=False),
                ])
                # In ra log 1 số mã tiêu biểu
                if any(x in index_name for x in ["Dow Jones", "Nikkei", "S&P 500", "Vàng", "Dầu", "Bitcoin"]):
                    print(f"  [+] Macro: {index_name} = {price} ({change_pct}%)")

            print(f"[AGENT] Ket qua: {len(rows)} chi so vi mo.")
            return rows

        except Exception as e:
            print(f"[AGENT] Loi crawl vi mo: {e}")
            return []

    # ----------------------------------------------------------
    # Orchestrator: chạy tất cả crawl → ghi Sheets
    # ----------------------------------------------------------
    def run(self) -> dict:
        """
        Chạy pipeline:
          1. Crawl giá cổ phiếu (JSON API — nhanh & chính xác)
          2. Crawl tỷ giá ngoại tệ (Playwright)
          3. Crawl giá vàng (Playwright)
          4. Ghi tất cả vào Google Sheets ở các tab tương ứng

        Returns:
            dict — tổng kết số hàng từ mỗi nguồn.
        """
        summary = {}

        # --- Giá cổ phiếu ---
        stock_rows = self.crawl_stock_prices()
        if stock_rows:
            # Ghi vào tab riêng: timestamp, symbol, ngay, gia_mo_cua, gia_cao_nhat, gia_thap_nhat, gia_dong_cua, thay_doi, khoi_luong, gia_tri
            dedicated_stock_rows = []
            for row in stock_rows:
                meta = json.loads(row[4])
                dedicated_stock_rows.append([
                    row[0],             # timestamp
                    meta["symbol"],
                    meta["ngay"],
                    meta["gia_mo_cua"],
                    meta["gia_cao_nhat"],
                    meta["gia_thap_nhat"],
                    meta["gia_dong_cua"],
                    meta["thay_doi"],
                    meta["khoi_luong"],
                    meta["gia_tri"]
                ])
            append_rows("stock_prices", dedicated_stock_rows)
            # Vẫn ghi 1 bản vào web_metrics tổng hợp
            append_rows("web_metrics", stock_rows)
        summary["stock_prices"] = len(stock_rows)

        # --- Tỷ giá ngoại tệ ---
        fx_rows = self.crawl_exchange_rates()
        if fx_rows:
            dedicated_fx_rows = []
            for row in fx_rows:
                meta = json.loads(row[4])
                dedicated_fx_rows.append([
                    row[0],                 # timestamp
                    meta["currency"],       # currency
                    meta.get("rate", 0),    # buy_cash (tạm dùng rate)
                    meta.get("rate", 0),    # buy_transfer
                    meta.get("rate", 0),    # sell
                ])
            append_rows("exchange_rates", dedicated_fx_rows)
            append_rows("web_metrics", fx_rows)
        summary["exchange_rates"] = len(fx_rows)

        # --- Giá vàng ---
        gold_rows = self.crawl_gold_prices()
        if gold_rows:
            dedicated_gold_rows = []
            for row in gold_rows:
                meta = json.loads(row[4])
                dedicated_gold_rows.append([
                    row[0],                 # timestamp
                    meta["gold_type"],      # gold_type
                    meta.get("price", 0),   # buy_price
                    meta.get("price", 0),   # sell_price
                ])
            append_rows("gold_prices", dedicated_gold_rows)
            append_rows("web_metrics", gold_rows)
        summary["gold_prices"] = len(gold_rows)

        # --- Chỉ số vĩ mô & Thế giới ---
        macro_rows = self.crawl_macro_indicators()
        if macro_rows:
            dedicated_macro_rows = []
            for row in macro_rows:
                meta = json.loads(row[4])
                dedicated_macro_rows.append([
                    row[0],                     # timestamp
                    meta["index_name"],         # index_name
                    meta["price"],              # price
                    meta["change_percent"],     # change_percent
                ])
            append_rows("macro_indicators", dedicated_macro_rows)
            append_rows("web_metrics", macro_rows)
        summary["macro_indicators"] = len(macro_rows)

        return summary
