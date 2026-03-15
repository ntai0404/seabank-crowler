# ============================================================
# core/base_agent.py — Abstract base class cho mọi crawler agent
# ============================================================

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.config import REQUEST_DELAY, REQUEST_TIMEOUT


class BaseAgent(ABC):
    """
    Base class chuẩn cho mọi crawler agent trong pipeline.

    Subclass cần implement:
        - crawl() -> dict[str, list[list]]:
              Key = tên sheet tab, Value = list[list] rows theo schema tab đó.

    Subclass có thể override:
        - SOURCE_URL, SOURCE_NAME
    """

    SOURCE_NAME: str = "unknown"
    SOURCE_URL: str  = ""
    REPLACE_SHEETS: set[str] = set()
    UPSERT_KEY_COLUMNS: dict[str, list[int]] = {}

    def __init__(self):
        self.timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._session: Optional[requests.Session] = None

    # ----------------------------------------------------------
    # HTTP helpers (requests với retry tự động)
    # ----------------------------------------------------------
    @property
    def session(self) -> requests.Session:
        """Lazily create requests.Session với retry."""
        if self._session is None:
            s = requests.Session()
            retry = Retry(
                total=5,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            s.mount("https://", HTTPAdapter(max_retries=retry))
            s.mount("http://",  HTTPAdapter(max_retries=retry))
            s.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
            })
            self._session = s
        return self._session

    def get(self, url: str, **kwargs) -> requests.Response:
        """GET với timeout mặc định."""
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        return self.session.get(url, **kwargs)

    def get_json(self, url: str, **kwargs) -> dict | list:
        """GET và parse JSON, raise nếu lỗi."""
        resp = self.get(url, **kwargs)
        resp.raise_for_status()
        return resp.json()

    # ----------------------------------------------------------
    # Abstract interface
    # ----------------------------------------------------------
    @abstractmethod
    def crawl(self) -> dict[str, list[list]]:
        """
        Thực hiện crawl và trả về dict:
          { "sheet_tab_name": [ [row1_col1, row1_col2, ...], [row2...], ... ] }
        """

    # ----------------------------------------------------------
    # Run (template method)
    # ----------------------------------------------------------
    def run(self) -> dict[str, int]:
        """
        Chạy crawl và ghi toàn bộ dữ liệu vào Google Sheets.
        Trả về summary: { sheet_name: số_hàng_đã_ghi }.
        """
        from core.sheets_manager import append_rows, clear_sheet_data, delete_existing_rows_by_key

        print(f"\n{'='*55}")
        print(f"[{self.SOURCE_NAME.upper()}] Bắt đầu crawl: {self.SOURCE_URL}")
        print(f"{'='*55}")

        try:
            data = self.crawl()
        except Exception as e:
            print(f"[{self.SOURCE_NAME.upper()}] ❌ Lỗi nghiêm trọng: {e}")
            import traceback; traceback.print_exc()
            return {}

        summary: dict[str, int] = {}
        for sheet_name, rows in data.items():
            if rows:
                if sheet_name in self.REPLACE_SHEETS:
                    clear_sheet_data(sheet_name)
                key_cols = self.UPSERT_KEY_COLUMNS.get(sheet_name)
                if key_cols:
                    delete_existing_rows_by_key(sheet_name, rows, key_cols)
                append_rows(sheet_name, rows)
                summary[sheet_name] = len(rows)
            else:
                print(f"[{self.SOURCE_NAME.upper()}] ⚠️  Không có dữ liệu cho tab '{sheet_name}'")
                summary[sheet_name] = 0

        return summary
