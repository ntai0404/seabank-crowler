# ============================================================
# agents/customs_agent.py — Crawl kim ngạch XNK từ Hải quan VN
#
# Nguồn: https://www.customs.gov.vn
# Chiến lược:
#   - Crawl trang thống kê nhanh (số liệu tổng hợp)
#   - Parse bảng HTML bằng BeautifulSoup
#   - Tìm file Excel/báo cáo định kỳ nếu có
#
# Output schema (tab: customs_trade):
# Output schema (tab: customs_trade):
#   [timestamp, source, category, period, value_usd, unit, meta_json]
# ============================================================

import json
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from core.base_agent import BaseAgent


class CustomsAgent(BaseAgent):
    """Agent crawl số liệu kim ngạch xuất nhập khẩu từ Tổng cục Hải quan VN."""

    SOURCE_NAME = "customs"
    SOURCE_URL  = "https://www.customs.gov.vn"

    # Trang thống kê nhanh hàng ngày
    _URL_QUICK_STATS  = "https://www.customs.gov.vn/index.jsp?pageCode=THONG_KE_NHANH"
    # Trang tìm kiếm báo cáo thống kê
    _URL_STATS_LIST   = "https://www.customs.gov.vn/index.jsp?pageCode=THONG_KE_CHINH_THUC"

    def crawl(self) -> dict[str, list[list]]:
        rows = []
        rows.extend(self._crawl_quick_stats())
        rows.extend(self._crawl_monthly_report())

        return {"customs_trade": rows}

    # ----------------------------------------------------------
    # 1. Thống kê nhanh (tổng XNK hàng ngày/tháng)
    # ----------------------------------------------------------
    def _crawl_quick_stats(self) -> list[list]:
        """Crawl trang thống kê nhanh — sử dụng Playwright Interception để lấy JSON."""
        print("[CUSTOMS] Crawl thống kê nhanh XNK (Playwright Intercept)...")
        rows = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
                page = context.new_page()

                captured_json = []
                def handle_response(response):
                    if "json" in response.headers.get("content-type", "").lower():
                        try:
                            # Tìm các request có tên liên quan đến thống kê
                            if any(k in response.url.lower() for k in ["baocao", "thongke", "data", "grid"]):
                                captured_json.append(response.json())
                        except Exception:
                            pass

                page.on("response", handle_response)
                
                # Đi tới trang và chờ load xong
                page.goto(self._URL_QUICK_STATS, timeout=60000, wait_until="networkidle")
                
                # Cuộn trang để kích hoạt lazy loading nếu có
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(3)

                # Process captured JSONs
                for data in captured_json:
                    rows.extend(self._parse_customs_json(data, source="quick_stats_api"))

                # Fallback nếu không bắt được JSON: Parse HTML như cũ
                if not rows:
                    soup = BeautifulSoup(page.content(), "html.parser")
                    tables = soup.find_all("table")
                    for table in tables:
                        rows.extend(self._parse_stats_table(table, source="quick_stats_html"))
                    if not rows:
                        rows.extend(self._parse_text_stats(soup))
                    
                browser.close()

        except Exception as e:
            print(f"[CUSTOMS] ❌ Lỗi thống kê nhanh (PW Intercept): {str(e)[:150]}")

        print(f"[CUSTOMS] Thống kê nhanh: {len(rows)} bản ghi.")
        return rows

    def _parse_customs_json(self, data, source: str) -> list[list]:
        """Helper to parse raw JSON from Customs API if captured."""
        rows = []
        # Tùy biến schema theo thực tế JSON bắt được (giả định cấu hình phổ biến)
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("Data", []) or data.get("rows", []) or data.get("items", [])
        else:
            return []

        for item in items:
            if not isinstance(item, dict): continue
            # Giả định các field thường thấy ở kendo grid
            cat = item.get("TenChiTieu") or item.get("Category") or item.get("Name")
            val = item.get("GiaTri") or item.get("Value") or item.get("Amount")
            period = item.get("KyBaoCao") or item.get("Period") or "current"
            
            if cat and val:
                meta = {"raw_json": item, "source": source}
                rows.append([
                    self.timestamp, "customs.gov.vn",
                    cat, period, self._parse_number(val), "triệu USD",
                    json.dumps(meta, ensure_ascii=False)
                ])
        return rows

    # ----------------------------------------------------------
    # 2. Báo cáo thống kê tháng/năm
    # ----------------------------------------------------------
    def _crawl_monthly_report(self) -> list[list]:
        """Crawl danh sách báo cáo tháng, lấy báo cáo mới nhất."""
        print("[CUSTOMS] Crawl báo cáo thống kê tháng...")
        rows = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.goto(self._URL_STATS_LIST, timeout=60000, wait_until="networkidle")
                
                soup = BeautifulSoup(page.content(), "html.parser")

                # Tìm link báo cáo mới nhất
                links = soup.find_all("a", href=True)
                report_links = [
                    a["href"] for a in links
                    if any(kw in a.get_text().lower() for kw in
                           ["thống kê", "xuất khẩu", "nhập khẩu", "kim ngạch", "tháng"])
                ][:5]  # Lấy 5 bài đầu

                for link_href in report_links:
                    if not link_href.startswith("http"):
                        link_href = self.SOURCE_URL + link_href
                    try:
                        page.goto(link_href, timeout=45000, wait_until="networkidle")
                        s = BeautifulSoup(page.content(), "html.parser")
                        # Trích xuất số liệu từ bài viết
                        rows.extend(self._extract_trade_numbers(s, url=link_href))
                    except Exception as inner_e:
                        print(f"  [!] Bỏ qua bài báo cáo do lỗi: {str(inner_e)[:50]}")
                        pass
                
                browser.close()

        except Exception as e:
            print(f"[CUSTOMS] ❌ Lỗi báo cáo tháng (Playwright): {str(e)[:150]}")

        print(f"[CUSTOMS] Báo cáo tháng: {len(rows)} bản ghi.")
        return rows

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------
    def _parse_stats_table(self, table, source: str = "") -> list[list]:
        """Parse bảng HTML thống kê XNK."""
        rows = []
        try:
            all_rows = table.find_all("tr")
            headers = []
            for i, tr in enumerate(all_rows):
                cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
                if i == 0:
                    headers = cells
                    continue
                if len(cells) < 2:
                    continue
                category = cells[0] if cells else ""
                # Tìm giá trị số trong các cột
                for j, cell in enumerate(cells[1:], 1):
                    val = self._parse_number(cell)
                    if val and val > 0:
                        period = headers[j] if j < len(headers) else f"col_{j}"
                        meta = {
                            "category": category,
                            "period": period,
                            "raw_value": cell,
                            "source_type": source,
                        }
                        rows.append([
                            self.timestamp, "customs.gov.vn",
                            category, period, val, "triệu USD",
                            json.dumps(meta, ensure_ascii=False),
                        ])
        except Exception:
            pass
        return rows

    def _parse_text_stats(self, soup: BeautifulSoup) -> list[list]:
        """Fallback: Tìm số liệu kim ngạch XNK trong text."""
        rows = []
        text = soup.get_text()
        # Pattern: tìm các con số tỷ USD hoặc triệu USD
        patterns = [
            (r"xuất khẩu[^\d]*(\d[\d\.,]+)\s*(tỷ|triệu)\s*USD", "export"),
            (r"nhập khẩu[^\d]*(\d[\d\.,]+)\s*(tỷ|triệu)\s*USD", "import"),
            (r"xuất siêu[^\d]*(\d[\d\.,]+)\s*(tỷ|triệu)\s*USD", "trade_surplus"),
            (r"nhập siêu[^\d]*(\d[\d\.,]+)\s*(tỷ|triệu)\s*USD", "trade_deficit"),
        ]
        period = datetime.now().strftime("%Y-%m")
        for pattern, category in patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    val = self._parse_number(m.group(1))
                    unit = m.group(2)
                    if val:
                        if unit == "tỷ":
                            val *= 1000  # Quy về triệu USD
                        meta = {"category": category, "period": period, "unit": f"{unit} USD"}
                        rows.append([
                            self.timestamp, "customs.gov.vn",
                            category, period, val, "triệu USD",
                            json.dumps(meta, ensure_ascii=False),
                        ])
                except Exception:
                    pass
        return rows

    def _extract_trade_numbers(self, soup: BeautifulSoup, url: str = "") -> list[list]:
        """Trích xuất số liệu thương mại từ bài viết báo cáo."""
        rows = []
        text = soup.get_text()
        period = datetime.now().strftime("%Y-%m")

        # Tìm period trong tiêu đề/nội dung
        period_match = re.search(r"tháng\s*(\d{1,2})[/\-](\d{4})", text, re.IGNORECASE)
        if period_match:
            period = f"{period_match.group(2)}-{period_match.group(1).zfill(2)}"

        # Parse bảng nếu có
        for table in soup.find_all("table"):
            rows.extend(self._parse_stats_table(table, source=url))

        # Fallback text parsing
        if not rows:
            rows.extend(self._parse_text_stats(soup))

        return rows

    @staticmethod
    def _parse_number(text: str) -> float | None:
        """Parse số từ string (xử lý dấu chấm/phẩy VN)."""
        try:
            cleaned = re.sub(r"[^\d,\.]", "", str(text))
            # Xử lý định dạng VN: 1.234,56 → 1234.56
            if "," in cleaned and "." in cleaned:
                cleaned = cleaned.replace(".", "").replace(",", ".")
            elif "," in cleaned:
                cleaned = cleaned.replace(",", ".")
            elif "." in cleaned and cleaned.count(".") > 1:
                cleaned = cleaned.replace(".", "")
            return float(cleaned) if cleaned else None
        except (ValueError, TypeError):
            return None
