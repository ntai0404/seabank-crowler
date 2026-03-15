# ============================================================
# agents/vinatex_agent.py — Crawl tin tức từ Vinatex (Tập đoàn Dệt May VN)
#
# Nguồn: http://www.vinatex.com
# Chiến lược:
#   - Crawl trang tin tức (News section) bằng requests + BeautifulSoup
#   - Parse bài viết tiếng Anh và tiếng Việt
#   - Trang WordPress-based, render tĩnh, không cần Playwright
#
# Output schema (tab: vinatex_news):
#   [timestamp, source, title, url, lang, published_date, summary]
# ============================================================

import re
from bs4 import BeautifulSoup

from core.base_agent import BaseAgent


class VinatexAgent(BaseAgent):
    """Agent crawl tin tức từ Tập đoàn Dệt May Việt Nam (Vinatex)."""

    SOURCE_NAME = "vinatex"
    SOURCE_URL  = "http://www.vinatex.com"

    # Dedup theo URL (col 3) để không ghi trùng bài cũ khi chạy lại
    UPSERT_KEY_COLUMNS = {"vinatex_news": [3]}

    _NEWS_PAGES = [
        {"url": "http://www.vinatex.com/news/",        "lang": "en", "category": "News"},
        {"url": "http://www.vinatex.com/tin-tuc/",     "lang": "vi", "category": "Tin tức"},
        {"url": "http://www.vinatex.com/",              "lang": "en", "category": "Homepage"},
    ]

    def crawl(self) -> dict[str, list[list]]:
        rows = []
        seen_urls = set()

        for page_config in self._NEWS_PAGES:
            try:
                resp = self.get(page_config["url"])
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                articles = self._parse_wordpress_articles(
                    soup,
                    base_url=self.SOURCE_URL,
                    lang=page_config["lang"],
                    category=page_config["category"],
                )
                for art in articles:
                    url_key = art.get("url", "")
                    if url_key not in seen_urls:
                        seen_urls.add(url_key)
                        rows.append([
                            self.timestamp,
                            "vinatex.com",
                            art.get("title", ""),
                            art.get("url", ""),
                            art.get("lang", ""),
                            art.get("published_date", ""),
                            art.get("summary", ""),
                        ])
                print(f"[VINATEX] '{page_config['category']}': {len(articles)} bài")
            except Exception as e:
                print(f"[VINATEX] ❌ Lỗi khi crawl '{page_config['url']}': {e}")

        print(f"[VINATEX] Tổng cộng: {len(rows)} bài viết (unique).")
        return {"vinatex_news": rows}

    def _parse_wordpress_articles(
        self, soup: BeautifulSoup, base_url: str, lang: str, category: str
    ) -> list[dict]:
        """Parse bài viết từ WordPress site Vinatex."""
        articles = []
        seen_hrefs = set()

        # WordPress thường dùng article tag, entry-title class, hoặc post class
        wp_selectors = [
            soup.find_all("article"),
            soup.find_all("div", class_=lambda c: c and "post" in (c or "").lower()),
            soup.find_all("div", class_=lambda c: c and "entry" in (c or "").lower()),
            soup.find_all("div", class_=lambda c: c and "item" in (c or "").lower()),
            # Fallback: tìm heading + link
            soup.find_all(["h2","h3"], class_=lambda c: c and "title" in (c or "").lower()),
        ]

        for elements in wp_selectors:
            for el in elements:
                link = el.find("a", href=True)
                if not link:
                    continue

                href = link["href"].strip()
                if not href or href in ("#", "/"):
                    continue
                if href in seen_hrefs:
                    continue
                seen_hrefs.add(href)

                full_url = href if href.startswith("http") else base_url + href.lstrip("/")

                # Skip nếu không phải URL bài viết (bỏ qua nav links)
                if any(x in full_url for x in ["#", "javascript:", "mailto:"]):
                    continue

                # Title
                title_el = el.find(["h1","h2","h3","h4"]) or link
                title = self._clean_text(title_el.get_text())
                if not title or len(title) < 8:
                    continue

                # Summary/excerpt
                excerpt_el = el.find(class_=lambda c: c and "excerpt" in (c or "").lower())
                if not excerpt_el:
                    excerpt_el = el.find("p")
                summary = self._clean_text(excerpt_el.get_text()) if excerpt_el else ""

                # Published date
                date_text = ""
                time_el = el.find("time")
                if time_el:
                    date_text = time_el.get("datetime", "") or self._clean_text(time_el.get_text())
                else:
                    date_match = re.search(
                        r"\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2}",
                        el.get_text()
                    )
                    if date_match:
                        date_text = date_match.group()

                articles.append({
                    "title":          title,
                    "url":            full_url,
                    "lang":           lang,
                    "category":       category,
                    "published_date": date_text,
                    "summary":        summary[:300],
                })

        return articles

    @staticmethod
    def _clean_text(text: str) -> str:
        if not text:
            return ""
        return " ".join(text.split()).strip()
