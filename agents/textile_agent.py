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
from bs4 import BeautifulSoup

from core.base_agent import BaseAgent


class TextileAgent(BaseAgent):
    """Agent crawl tin tức ngành dệt may từ Hiệp hội VITAS."""

    SOURCE_NAME = "vitas"
    SOURCE_URL  = "http://www.vietnamtextile.org.vn"

    _PAGES = [
        {"url": "http://www.vietnamtextile.org.vn/tin-tuc-su-kien_p1_1-1.html",
         "category": "Tin tức sự kiện"},
        {"url": "http://www.vietnamtextile.org.vn/thi-truong_p1_1-1_2-3.html",
         "category": "Thị trường"},
        {"url": "http://www.vietnamtextile.org.vn/chinh-sach-phap-luat_p1_1-1_2-5.html",
         "category": "Chính sách pháp luật"},
        {"url": "http://www.vietnamtextile.org.vn/",
         "category": "Trang chủ"},
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
                    if url_key not in seen_urls:
                        seen_urls.add(url_key)
                        rows.append([
                            self.timestamp,
                            "vietnamtextile.org.vn",
                            article.get("title", ""),
                            article.get("url", ""),
                            article.get("category", ""),
                            article.get("published_date", ""),
                            article.get("summary", ""),
                        ])
                print(f"[VITAS] '{page_config['category']}': {len(articles)} bài")
            except Exception as e:
                print(f"[VITAS] ❌ Lỗi khi crawl '{page_config['url']}': {e}")

        print(f"[VITAS] Tổng cộng: {len(rows)} bài viết (unique).")
        return {"textile_news": rows}

    def _parse_articles(self, soup: BeautifulSoup, base_url: str, category: str) -> list[dict]:
        """Parse danh sách bài viết từ trang VITAS."""
        articles = []

        # VITAS dùng tag <article>, <li> và <div class="news-item">
        selectors = [
            soup.find_all("article"),
            soup.find_all("div", class_=lambda c: c and "news" in c.lower()),
            soup.find_all("li", class_=lambda c: c and "item" in c.lower()),
        ]

        seen_hrefs = set()
        for selector_results in selectors:
            for el in selector_results:
                link = el.find("a", href=True)
                if not link:
                    continue
                href = link["href"].strip()
                if href in seen_hrefs:
                    continue
                seen_hrefs.add(href)

                title = self._clean_text(link.get_text())
                if not title or len(title) < 10:
                    # Try to find h2/h3 inside element
                    heading = el.find(["h1","h2","h3","h4"])
                    if heading:
                        title = self._clean_text(heading.get_text())

                if not title or len(title) < 10:
                    continue

                full_url = href if href.startswith("http") else base_url + "/" + href.lstrip("/")

                # Tìm summary
                summary_el = el.find("p") or el.find("div", class_=lambda c: c and "desc" in (c or "").lower())
                summary = self._clean_text(summary_el.get_text()) if summary_el else ""

                # Tìm ngày đăng
                date_text = ""
                date_el = el.find(class_=lambda c: c and any(d in (c or "").lower() for d in ["date","time","ngay"]))
                if date_el:
                    date_text = self._clean_text(date_el.get_text())
                else:
                    # Try to find date pattern in text
                    match = re.search(r"\d{1,2}/\d{1,2}/\d{4}", el.get_text())
                    if match:
                        date_text = match.group()

                articles.append({
                    "title":          title,
                    "url":            full_url,
                    "category":       category,
                    "published_date": date_text,
                    "summary":        summary[:300],
                })

        return articles

    @staticmethod
    def _clean_text(text: str) -> str:
        """Chuẩn hoá text: bỏ khoảng trắng thừa."""
        if not text:
            return ""
        return " ".join(text.split()).strip()
