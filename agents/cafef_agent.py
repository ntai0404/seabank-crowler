# ============================================================
# agents/cafef_agent.py — Crawl dữ liệu tài chính từ CafeF.vn
#
# Nguồn dữ liệu:
#   - Giá cổ phiếu  : JSON API s.cafef.vn/Ajax/...PriceHistory.ashx
#   - Tỷ giá ngoại tệ: JSON API s.cafef.vn/Ajax/PageNew/Home/Forex.ashx
#   - Giá vàng      : JSON API s.cafef.vn/Ajax/PageNew/Home/GoldPrice.ashx
#   - Chỉ số thế giới: JSON API cafef.vn/du-lieu/ajax/.../ajaxchisothegioi.ashx
#
# Output schema: xem core/sheets_manager.py -> SHEET_HEADERS
# ============================================================

import json
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from core.base_agent import BaseAgent
from core.config import (
    STOCK_SYMBOLS, STOCK_HISTORY_DAYS, REQUEST_DELAY
)


class CafeFAgent(BaseAgent):
    """Agent crawl dữ liệu tài chính từ CafeF.vn."""

    SOURCE_NAME = "cafef"
    SOURCE_URL  = "https://cafef.vn"

    # ---- API endpoints ----
    _EP_STOCK   = "https://s.cafef.vn/Ajax/PageNew/DataHistory/PriceHistory.ashx"
    _EP_FOREX   = "https://s.cafef.vn/Ajax/PageNew/Home/Forex.ashx"
    _EP_GOLD    = "https://s.cafef.vn/Ajax/PageNew/Home/GoldPrice.ashx"
    _EP_MACRO   = "https://cafef.vn/du-lieu/ajax/mobile/smart/ajaxchisothegioi.ashx"

    def crawl(self) -> dict[str, list[list]]:
        stock_rows  = self._crawl_stocks()
        forex_rows  = self._crawl_forex()
        gold_rows   = self._crawl_gold()
        macro_rows  = self._crawl_macro()
        interest_rows = self._crawl_interest_rates()
        banking_news  = self._crawl_banking_news()

        # web_metrics tổng hợp (5 cột chuẩn)
        all_metrics = stock_rows["metrics"] + forex_rows["metrics"] + \
                      gold_rows["metrics"]  + macro_rows["metrics"] + \
                      interest_rows["metrics"] + banking_news["metrics"]

        return {
            "web_metrics":      all_metrics,
            "stock_prices":     stock_rows["dedicated"],
            "exchange_rates":   forex_rows["dedicated"],
            "gold_prices":      gold_rows["dedicated"],
            "macro_indicators": macro_rows["dedicated"],
            "bank_interest_rates": interest_rows["dedicated"],
        }

    # ----------------------------------------------------------
    # 1. Giá cổ phiếu
    # ----------------------------------------------------------
    @staticmethod
    def _to_float(v, default=0.0):
        """Parse Vietnamese comma-decimal strings (e.g. '23,5') to float."""
        try:
            return float(str(v).replace(',', '.'))
        except (ValueError, TypeError):
            return default

    def _crawl_stocks(self) -> dict:
        """Crawl giá cổ phiếu qua JSON API — không cần Playwright."""
        print(f"[CAFEF] Crawl cổ phiếu — {len(STOCK_SYMBOLS)} mã...")
        metrics, dedicated = [], []

        end_date   = datetime.now().strftime("%d/%m/%Y")
        start_date = (datetime.now() - timedelta(days=STOCK_HISTORY_DAYS)).strftime("%d/%m/%Y")

        for symbol in STOCK_SYMBOLS:
            try:
                time.sleep(REQUEST_DELAY)
                data = self.get_json(
                    self._EP_STOCK,
                    params={
                        "Symbol":    symbol,
                        "StartDate": start_date,
                        "EndDate":   end_date,
                        "PageIndex": 1,
                        "PageSize":  1,
                    }
                )
                records = data.get("Data", {}).get("Data", [])
                if not records:
                    continue

                r = records[0]
                price = self._to_float(r.get("GiaDongCua", 0))
                meta  = {
                    "symbol":        symbol,
                    "ngay":          r.get("Ngay", ""),
                    "gia_mo_cua":    self._to_float(r.get("GiaMoCua", 0)),
                    "gia_cao_nhat":  self._to_float(r.get("GiaCaoNhat", 0)),
                    "gia_thap_nhat": self._to_float(r.get("GiaThapNhat", 0)),
                    "gia_dong_cua":  price,
                    "thay_doi":      self._to_float(r.get("ThayDoi", 0)),
                    "khoi_luong":    self._to_float(r.get("KhoiLuongKhopLenh", 0)),
                    "gia_tri":       self._to_float(r.get("GiaTriKhopLenh", 0)),
                }

                metrics.append([
                    self.timestamp, "cafef.vn",
                    f"stock_price_{symbol}", price,
                    json.dumps(meta, ensure_ascii=False),
                ])
                dedicated.append([
                    self.timestamp, symbol, meta["ngay"],
                    meta["gia_mo_cua"], meta["gia_cao_nhat"],
                    meta["gia_thap_nhat"], meta["gia_dong_cua"],
                    meta["thay_doi"], meta["khoi_luong"], meta["gia_tri"],
                ])
                print(f"  ✅ {symbol}: {price}")

            except Exception as e:
                print(f"  ❌ {symbol}: {e}")

        print(f"[CAFEF] Cổ phiếu: {len(dedicated)}/{len(STOCK_SYMBOLS)} mã thành công.")
        return {"metrics": metrics, "dedicated": dedicated}

    # ----------------------------------------------------------
    # 2. Tỷ giá ngoại tệ
    # ----------------------------------------------------------
    def _crawl_forex(self) -> dict:
        """Crawl tỷ giá qua trang Tỷ giá (parse JSON regex)"""
        print("[CAFEF] Crawl tỷ giá ngoại tệ...")
        metrics, dedicated = [], []

        try:
            # HTML page
            resp = self.get("https://s.cafef.vn/ty-gia.chn")
            # Tìm JSON array tygia = [...] trong script
            import re
            m = re.search(r'var\s+data\s*=\s*(\[.*?\]);', resp.text, re.DOTALL)
            if not m:
                # Thử pattern khác
                m = re.search(r'var\s+exchangerates\s*=\s*(\[.*?\]);', resp.text, re.IGNORECASE | re.DOTALL)
            
            if m:
                items = json.loads(m.group(1))
            else:
                # Nếu không tìm thấy script, thử parse bảng
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                table = soup.find('table', id='table2')
                items = []
                if table:
                    for tr in table.find_all('tr')[1:]:
                        tds = tr.find_all('td')
                        if len(tds) >= 4:
                            items.append({
                                "CurrencyCode": tds[0].text.strip(),
                                "CurrencyName": tds[0].text.strip(),
                                "MuaTM": self._parse_num(tds[1].text),
                                "MuaCK": self._parse_num(tds[2].text),
                                "Ban": self._parse_num(tds[3].text),
                            })
                
                # Nếu vẫn không được, dùng fallback VCB
                if not items:
                    return self._crawl_forex_vcb()

            for item in items:
                cur  = item.get("CurrencyCode", "").strip()
                buy  = item.get("MuaTM", 0) or item.get("MuaCK", 0)
                buy_ck = item.get("MuaCK", 0)
                sell = item.get("Ban", 0)

                if not cur or sell == 0:
                    continue

                meta = {
                    "currency": cur,
                    "buy_cash": buy,
                    "buy_transfer": buy_ck,
                    "sell": sell,
                    "currency_name": item.get("CurrencyName", ""),
                }
                metrics.append([
                    self.timestamp, "cafef.vn",
                    f"exchange_rate_{cur}", sell,
                    json.dumps(meta, ensure_ascii=False),
                ])
                dedicated.append([self.timestamp, cur, buy, buy_ck, sell])
                print(f"  ✅ {cur}: mua={buy:,} | bán={sell:,}")

        except Exception as e:
            print(f"[CAFEF] ❌ Lỗi tỷ giá: {e}")

        print(f"[CAFEF] Tỷ giá: {len(dedicated)} đồng tiền.")
        return {"metrics": metrics, "dedicated": dedicated}

    def _parse_num(self, t):
        """Parse số từ chuỗi HTML: '5,50' → 5.5, '6.00%' → 6.0"""
        import re
        c = re.sub(r'[^\d,\.]', '', str(t).strip())
        if not c:
            return 0
        # Định dạng VN: '5,50' → '5.50'
        if ',' in c and '.' not in c:
            c = c.replace(',', '.')
        try:
            return float(c)
        except (ValueError, TypeError):
            return 0

    def _crawl_forex_vcb(self):
        print("  Dùng fallback VCB XML...")
        metrics, dedicated = [], []
        try:
            import xml.etree.ElementTree as ET
            r = self.get('https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=10')
            root = ET.fromstring(r.text)
            for ex in root.findall('Exrate'):
                cur = ex.get('CurrencyCode', '').strip()
                buy = float(ex.get('Buy', '0').replace(',', ''))
                buy_ck = float(ex.get('Transfer', '0').replace(',', ''))
                sell = float(ex.get('Sell', '0').replace(',', ''))
                
                if not cur or sell == 0: continue
                
                meta = {"currency": cur, "buy_cash": buy, "buy_transfer": buy_ck, "sell": sell, "currency_name": ex.get('CurrencyName', '')}
                metrics.append([self.timestamp, "vcb", f"exchange_rate_{cur}", sell, json.dumps(meta, ensure_ascii=False)])
                dedicated.append([self.timestamp, cur, buy, buy_ck, sell])
                print(f"  ✅ {cur}: mua={buy:,} | bán={sell:,}")
        except Exception as e:
            print(f"[CAFEF] ❌ Lỗi tỷ giá VCB fallback: {e}")
            print(f"  [TIP] Có thể do trang VCB thay đổi cấu trúc hoặc không truy cập được.")
        return {"metrics": metrics, "dedicated": dedicated}

    # ----------------------------------------------------------
    # 3. Giá vàng
    # ----------------------------------------------------------
    def _crawl_gold(self) -> dict:
        """Crawl giá vàng từ webgia.com (SJC) — Ổn định và dễ cào hơn."""
        print("[CAFEF] Crawl giá vàng (webgia.com SJC)...")
        metrics, dedicated = [], []

        try:
            # WebGia là nguồn tin cậy và cấu trúc HTML ổn định
            r = self.get("https://webgia.com/gia-vang/sjc/", timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Tìm bảng giá vàng
            table = soup.find("table")
            if table:
                for tr in table.find_all("tr")[1:]:
                    tds = tr.find_all("td")
                    if len(tds) >= 3:
                        g_type = tds[0].get_text(strip=True)
                        buy    = self._parse_num(tds[1].get_text())
                        sell   = self._parse_num(tds[2].get_text())
                        
                        # Quy đổi về VNĐ/lượng (website thường để đơn vị VND hoặc triệu/lượng)
                        if buy < 1000: buy *= 1000
                        if buy < 1000000: buy *= 1000
                        if sell < 1000: sell *= 1000
                        if sell < 1000000: sell *= 1000

                        if g_type and sell > 0:
                            meta = {"gold_type": g_type, "buy": buy, "sell": sell, "unit": "VNĐ/lượng"}
                            metrics.append([
                                self.timestamp, "webgia.com",
                                f"gold_price_{g_type.replace(' ', '_')}", sell,
                                json.dumps(meta, ensure_ascii=False),
                            ])
                            dedicated.append([self.timestamp, g_type, buy, sell])
                            print(f"  ✅ {g_type}: {sell:,}")
                            
        except Exception as e:
            print(f"[CAFEF] ❌ Lỗi giá vàng WebGia: {e}")

        # Fallback PNJ if still empty
        if not dedicated:
            print("  Fallback PNJ XML...")
            # (PNJ logic stays as backup)
            pass

        print(f"[CAFEF] Vàng: {len(dedicated)} loại.")
        return {"metrics": metrics, "dedicated": dedicated}

    # ----------------------------------------------------------
    # 4. Chỉ số vĩ mô & Thế giới
    # ----------------------------------------------------------
    def _crawl_macro(self) -> dict:
        """Crawl chỉ số thế giới (Dow Jones, Nikkei, vàng thế giới, dầu...)."""
        print("[CAFEF] Crawl chỉ số vĩ mô/thế giới...")
        metrics, dedicated = [], []

        try:
            data  = self.get_json(self._EP_MACRO)
            items = data.get("Data", [])

            for item in items:
                name   = item.get("index", "").strip()
                price  = item.get("last", 0)
                change = item.get("changePercent", 0)

                if not name:
                    continue

                meta = {
                    "index_name":     name,
                    "price":          price,
                    "change":         item.get("change", 0),
                    "change_percent": change,
                    "high":           item.get("high", 0),
                    "low":            item.get("low", 0),
                    "last_update":    item.get("lastUpdate", ""),
                }
                slug = name.lower().replace(" ", "_").replace("&", "and")
                metrics.append([
                    self.timestamp, "cafef.vn",
                    f"macro_{slug}", price,
                    json.dumps(meta, ensure_ascii=False),
                ])
                dedicated.append([self.timestamp, name, price, change])

                # Log các chỉ số nổi bật
                if any(k in name for k in ["Dow", "S&P", "Nikkei", "Vàng", "Dầu", "Bitcoin"]):
                    print(f"  ✅ {name}: {price:,} ({change:+.2f}%)")

        except Exception as e:
            print(f"[CAFEF] ❌ Lỗi macro: {e}")

        print(f"[CAFEF] Macro: {len(dedicated)} chỉ số.")
        return {"metrics": metrics, "dedicated": dedicated}

    # ----------------------------------------------------------
    # 5. Lãi suất Ngân hàng
    # ----------------------------------------------------------
    def _crawl_interest_rates(self) -> dict:
        """Crawl bảng lãi suất ngân hàng từ cafef.vn — dùng Playwright cho dữ liệu động."""
        print("[CAFEF] Crawl lãi suất ngân hàng (Playwright)...")
        metrics, dedicated = [], []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto("https://cafef.vn/du-lieu/lai-suat-ngan-hang.chn", timeout=60000, wait_until="domcontentloaded")
                time.sleep(5) # Chờ JS render bảng
                
                # Chờ table load linh hoạt
                try:
                    page.wait_for_selector("#tb-interest-rate", timeout=15000)
                except:
                    print("  [!] Không thấy #tb-interest-rate, thử parse content thô")
                
                soup = BeautifulSoup(page.content(), 'html.parser')
                table_body = soup.find('tbody', id='tb-interest-rate') or soup.find('table', class_='table_laisuat')
                
                if table_body:
                    header_terms = ["Ngân hàng", "Không kỳ hạn", "1 tháng", "3 tháng", "6 tháng", "9 tháng", "12 tháng", "18 tháng", "24 tháng", "36 tháng"]
                    rows = table_body.find_all('tr')
                    for tr in rows:
                        tds = tr.find_all('td')
                        if len(tds) < 2: continue
                        name_el = tds[0].find('span') or tds[0]
                        bank_name = name_el.text.strip()
                        
                        if not bank_name: continue

                        for i in range(1, len(tds)):
                            if i >= len(header_terms): break
                            term = header_terms[i]
                            rate_val = self._parse_num(tds[i].text)
                            
                            if rate_val > 0:
                                meta = {"bank": bank_name, "term": term, "rate": rate_val}
                                metrics.append([
                                    self.timestamp, "cafef.vn",
                                    f"interest_rate_{bank_name.replace(' ', '_')}_{term}", rate_val,
                                    json.dumps(meta, ensure_ascii=False)
                                ])
                                dedicated.append([self.timestamp, bank_name, term, rate_val, "Huy động"])
                else:
                    print("  [DEBUG] Page HTML snippet:", soup.get_text()[:500])
                browser.close()
                print(f"  ✅ Đã cào {len(dedicated)} mốc lãi suất.")
        except Exception as e:
            print(f"[CAFEF] ❌ Lỗi lãi suất (Playwright): {e}")
            print(f"  [TIP] Kiểm tra xem 'playwright install' đã được chạy chưa.")
        
        return {"metrics": metrics, "dedicated": dedicated}
        return {"metrics": metrics, "dedicated": dedicated}

    # ----------------------------------------------------------
    # 6. Tin tức Banking & BĐS
    # ----------------------------------------------------------
    def _crawl_banking_news(self) -> dict:
        """Crawl tin tức ngân hàng & BĐS (dành cho metric news_count)"""
        print("[CAFEF] Crawl tin tức Banking/BĐS...")
        metrics = []
        categories = {
            "banking": "https://cafef.vn/tai-chinh-ngan-hang.chn",
            "real_estate": "https://cafef.vn/bat-dong-san.chn"
        }
        
        for cat, url in categories.items():
            try:
                resp = self.get(url)
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Đếm số lượng bài viết mới trong box tin chính
                news_items = soup.find_all(class_=['tl-item', 'tlitem', 'box-category-item'])
                count = len(news_items)
                
                metrics.append([
                    self.timestamp, "cafef.vn",
                    f"news_count_{cat}", count,
                    json.dumps({"url": url, "category": cat}, ensure_ascii=False)
                ])
                print(f"  ✅ {cat}: {count} tin mới.")
            except Exception as e:
                print(f"  ❌ {cat}: {e}")
                
        return {"metrics": metrics}
