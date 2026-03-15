# ============================================================
# agents/textile_agent.py — Crawl tin tức từ VITAS (Hiệp hội Dệt May VN)
#
# Nguồn: http://www.vietnamtextile.org.vn
# Chiến lược:
#   - Crawl trang chủ & trang tin tức bằng requests + BeautifulSoup
#   - Parse tiêu đề, URL, ngày đăng, tóm tắt bài viết
#   - Không cần Playwright (site render tĩnh)
#
# Output schema (tab: textile_news):
#   [timestamp, source, title, url, category, published_date, summary]
# ============================================================

import json
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup

from core.base_agent import BaseAgent


class TextileAgent(BaseAgent):
    """Agent crawl tin tức ngành dệt may từ Hiệp hội VITAS."""

    SOURCE_NAME = "vitas"
    SOURCE_URL  = "http://www.vietnamtextile.org.vn"

    @staticmethod
    def _normalize_published_date(raw_date: str) -> str:
        """Chuẩn hoá ngày về YYYY-MM-DD và loại bỏ mốc năm bất thường."""
        if not raw_date:
            return ""
        text = str(raw_date).strip()

        # Ưu tiên format chuẩn đang dùng trong sheet.
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                dt = datetime.strptime(text, fmt)
                # VITAS là tin tức hiện đại, năm quá cũ thường là parse lỗi.
                if 2000 <= dt.year <= datetime.now().year + 1:
                    return dt.strftime("%Y-%m-%d")
                return ""
            except ValueError:
                continue
        return ""

    # Crawl 3 trang đầu mỗi chuyên mục để có ~20-25 bài
    _PAGES = [
        {"url": "http://www.vietnamtextile.org.vn/tin-tuc-su-kien_p1_1-1.html",  "category": "Tin tức sự kiện"},
        {"url": "http://www.vietnamtextile.org.vn/tin-tuc-su-kien_p1_1-2.html",  "category": "Tin tức sự kiện"},
        {"url": "http://www.vietnamtextile.org.vn/tin-tuc-su-kien_p1_1-3.html",  "category": "Tin tức sự kiện"},
        {"url": "http://www.vietnamtextile.org.vn/thi-truong_p1_1-1_2-3.html",   "category": "Thị trường"},
        {"url": "http://www.vietnamtextile.org.vn/thi-truong_p1_1-2_2-3.html",   "category": "Thị trường"},
        {"url": "http://www.vietnamtextile.org.vn/chinh-sach-phap-luat_p1_1-1_2-5.html", "category": "Chính sách pháp luật"},
        {"url": "http://www.vietnamtextile.org.vn/chinh-sach-phap-luat_p1_1-2_2-5.html", "category": "Chính sách pháp luật"},
        {"url": "http://www.vietnamtextile.org.vn/",                              "category": "Trang chủ"},
    ]

    def crawl(self) -> dict[str, list[list]]:
        rows = []
        seen_urls = set()

        for page_config in self._PAGES:
            try:
                resp = self.get(page_config["url"])
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                articles = self._parse_articles(
                    soup,
                    base_url=self.SOURCE_URL,
                    category=page_config["category"],
                )
                for article in articles:
                    url_key = article.get("url", "")
                    # Chống trùng theo _4-ID bài (cùng bài có thể có _3-XX khác nhau)
                    _m = re.search(r"_4-(\d+)", url_key)
                    dedup_key = _m.group(1) if _m else url_key
                    if dedup_key not in seen_urls:
                        seen_urls.add(dedup_key)
                        # Nếu không có ngày từ tóm tắt, fetch trang bài để lấy pc_datetime
                        date = article.get("published_date", "")
                        date = self._normalize_published_date(date)
                        if not date and url_key:
                            try:
                                art_resp = self.get(url_key)
                                art_soup = BeautifulSoup(art_resp.text, "html.parser")
                                dt_el = art_soup.find(class_="pc_datetime")
                                if dt_el:
                                    dm2 = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})",
                                                    dt_el.get_text())
                                    if dm2:
                                        parsed = (f"{dm2.group(3)}-{dm2.group(2).zfill(2)}"
                                                  f"-{dm2.group(1).zfill(2)}")
                                        date = self._normalize_published_date(parsed)
                            except Exception:
                                pass
                        rows.append([
                            self.timestamp,
                            "vietnamtextile.org.vn",
                            article.get("title", ""),
                            url_key,
                            article.get("category", ""),
                            date or self.timestamp[:10],
                            article.get("summary", "") or "—",
                        ])
                print(f"[VITAS] '{page_config['category']}': {len(articles)} bài")
            except Exception as e:
                print(f"[VITAS] ❌ Lỗi khi crawl '{page_config['url']}': {e}")

        print(f"[VITAS] Tổng cộng: {len(rows)} bài viết (unique).")
        
        # Cào danh bạ hội viên
        directory_rows = self._crawl_directory()

        return {
            "textile_news": rows,
            "textile_directory": directory_rows
        }

    def _crawl_directory(self) -> list[list]:
        """Cào danh bạ doanh nghiệp từ VITAS — dùng Playwright."""
        print("[VITAS] Crawl danh bạ hội viên (Playwright)...")
        rows = []
        url_dir = "http://www.vietnamtextile.org.vn/DanhBa.aspx"
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url_dir, timeout=60000, wait_until="domcontentloaded")
                time.sleep(5)
                
                # Chờ các item danh bạ load
                try:
                    page.wait_for_selector("a.pl_vanban_title", timeout=15000)
                except:
                    print("  [!] Không thấy selector danh bạ, thử parse thô")
                
                # Duyệt qua các tab content_ptab_1 đến content_ptab_4
                for tab_idx in range(1, 5):
                    tab_selector = f"#content_ptab_{tab_idx}"
                    print(f"    [VITAS] Đang kiểm tra tab: {tab_selector}")
                    
                    # Thử click vào tab nếu cần (giả định tab render khi visible)
                    try:
                        page.click(f"li#ptab_{tab_idx} a", timeout=2000)
                        time.sleep(1)
                    except:
                        pass

                    soup = BeautifulSoup(page.content(), "html.parser")
                    tab_container = soup.select_one(tab_selector)
                    if tab_container:
                        items = tab_container.select("a.pl_vanban_title h2")
                        for item in items:
                            name = self._clean_text(item.get_text())
                            if name and len(name) > 5:
                                info = ""
                                parent_link = item.find_parent("a")
                                if parent_link:
                                    desc = parent_link.find_next("div", class_="pl_vanban_desc")
                                    if desc: info = self._clean_text(desc.get_text())
                                
                                rows.append([
                                    self.timestamp, name, "Dệt may", info[:200], ""
                                ])
                browser.close()
            
            # Remove duplicates
            unique_rows = []
            seen = set()
            for r in rows:
                if r[1] not in seen:
                    seen.add(r[1])
                    unique_rows.append(r)
            
            print(f"  ✅ Đã tìm thấy {len(unique_rows)} doanh nghiệp duy nhất.")
            return unique_rows
        except Exception as e:
            print(f"[VITAS] ❌ Lỗi cào danh bạ (Playwright): {e}")
            print(f"  [TIP] Kiểm tra xem 'playwright install' đã được chạy chưa.")
            return rows

    def _parse_articles(self, soup: BeautifulSoup, base_url: str, category: str) -> list[dict]:
        """Parse danh sách bài viết từ trang VITAS.

        Cấu trúc VITAS:
          - div.pl_c  : card bài nổi bật (có tóm tắt, đôi khi có ngày trong text)
          - div#*ucHotPost* > div.pl_display_list > div.pl_item : danh sách bài mới nhất (title-only)
        Tránh div.pl_item nằm trong gallery ảnh (div.pl_display_top-detail).
        """
        articles = []
        seen_hrefs = set()

        # 1. pl_c featured cards — có summary và đôi khi date trong text tóm tắt
        for card in soup.find_all("div", class_="pl_c"):
            link = card.find("a", href=re.compile(r"_4-\d+"))
            if not link:
                continue
            href = link["href"].strip()
            if href in seen_hrefs:
                continue
            seen_hrefs.add(href)

            heading = card.find("h2")
            title = self._clean_text((heading or link).get_text())
            if not title or len(title) < 10:
                continue

            full_url = href if href.startswith("http") else base_url + href

            # Summary: text of the second div inside pl_brief (after pl_right_c)
            brief_el = card.find(class_="pl_brief")
            summary = ""
            if brief_el:
                right_c = brief_el.find(class_="pl_right_c")
                if right_c:
                    for sib in right_c.next_siblings:
                        t = self._clean_text(getattr(sib, "get_text", lambda: "")())
                        if len(t) > 20:
                            summary = t[:250]
                            break

            # Date: embedded in summary text as dd/mm/yyyy
            date_text = ""
            dm = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", summary)
            if dm:
                parsed = f"{dm.group(3)}-{dm.group(2).zfill(2)}-{dm.group(1).zfill(2)}"
                date_text = self._normalize_published_date(parsed)

            articles.append({
                "title":          title,
                "url":            full_url,
                "category":       category,
                "published_date": date_text,
                "summary":        summary,
            })

        # 2. ucHotPost listing — title-only entries không có trong pl_c
        for box in soup.find_all(id=re.compile(r"ucHotPost")):
            listing = box.find("div", class_="pl_display_list")
            if not listing:
                continue
            for item in listing.find_all("div", class_="pl_item"):
                link = item.find("a", href=re.compile(r"_4-\d+"))
                if not link:
                    continue
                href = link["href"].strip()
                if href in seen_hrefs:
                    continue
                seen_hrefs.add(href)

                heading = item.find(["h2", "h3"])
                title = self._clean_text((heading or link).get_text())
                if not title or len(title) < 10:
                    continue

                full_url = href if href.startswith("http") else base_url + href
                articles.append({
                    "title":          title,
                    "url":            full_url,
                    "category":       category,
                    "published_date": "",
                    "summary":        "",
                })

        return articles

    @staticmethod
    def _clean_text(text: str) -> str:
        """Chuẩn hoá text: bỏ khoảng trắng thừa."""
        if not text:
            return ""
        return " ".join(text.split()).strip()
