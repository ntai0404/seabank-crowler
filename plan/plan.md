# Plan: Agent CafeF → Google Sheets → Preset.io

## 1. Tổng quan kiến trúc

```
[CafeF.vn]          → CafeFAgent   → stock_prices, exchange_rates, gold_prices, macro_indicators
[customs.gov.vn]    → CustomsAgent → customs_trade
[vietnamtextile..]  → TextileAgent → textile_news
[vinatex.com]       → VinatexAgent → vinatex_news
       │
       ▼  (Google Sheets API v4 — service account)
[Google Sheets — Data Hub]  (1 Spreadsheet, 8 tabs)
       │
       ▼  (Shillelagh / Google Sheets connector)
[Preset.io — BI Dashboard]
       │
       ▼  (GitHub Actions — cron 2 lần/ngày)
[.github/workflows/daily_crawl.yml]
```

**Repo GitHub:** [ntai0404/seabank-crowler](https://github.com/ntai0404/seabank-crowler)
**BI Tool:** [Preset.io](https://preset.io/) (Superset-as-a-Service, free tier)
**Spreadsheet:** `1QBbKfdaEPsAwNWjIS9g71bnLoqAOMX75kQAM4KeJwng`

---

## 2. Cấu trúc thư mục

```
Seabank-crowler/
├── .github/
│   └── workflows/
│       └── daily_crawl.yml    ← GitHub Actions (2 lần/ngày)
├── agents/
│   ├── __init__.py
│   ├── cafef_agent.py         ← CafeF (4 loại data, thuần JSON API)
│   ├── customs_agent.py       ← Hải quan VN (XNK)
│   ├── textile_agent.py       ← VITAS (tin tức dệt may)
│   └── vinatex_agent.py       ← Vinatex (tin tức tập đoàn)
├── core/
│   ├── __init__.py
│   ├── base_agent.py          ← Abstract base class (HTTP retry, run() template)
│   ├── config.py              ← Load .env, STOCK_SYMBOLS, SHEETS config
│   └── sheets_manager.py      ← append_rows(), setup_all_sheets(), clear_sheet_data()
├── plan/
│   └── plan.md                ← File này
├── .env                       ← Secrets local (KHÔNG commit)
├── .env.example               ← Template (commit được)
├── .gitignore
├── main.py                    ← Orchestrator CLI (--agents, --setup)
├── requirements.txt
└── setup_sheets.py            ← CLI setup tabs + headers
```

---

## 3. Schema 8 Tab Google Sheets

| Tab | Columns | Nguồn |
|-----|---------|-------|
| `web_metrics` | timestamp, source, metric_name, metric_value, meta_json | Tổng hợp |
| `stock_prices` | timestamp, symbol, ngay, gia_mo_cua, gia_cao_nhat, gia_thap_nhat, gia_dong_cua, thay_doi, khoi_luong, gia_tri | CafeF |
| `exchange_rates` | timestamp, currency, buy_cash, buy_transfer, sell | CafeF |
| `gold_prices` | timestamp, gold_type, buy_price, sell_price | CafeF |
| `macro_indicators` | timestamp, index_name, price, change_percent | CafeF |
| `customs_trade` | timestamp, source, category, period, value_usd, unit, meta_json | Hải quan |
| `textile_news` | timestamp, source, title, url, category, published_date, summary | VITAS |
| `vinatex_news` | timestamp, source, title, url, lang, published_date, summary | Vinatex |

---

## 4. GitHub Actions — Automation

**File:** `.github/workflows/daily_crawl.yml`

| Trigger | Thời gian VN |
|---------|-------------|
| Cron 1 | 8:00 AM (sáng) |
| Cron 2 | 2:00 PM (chiều) |
| Manual | Dispatch với tham số `agents` và `setup` |

**GitHub Secrets cần thiết:**
- `SPREADSHEET_ID` — ID của Google Sheet
- `GOOGLE_CREDENTIALS_JSON` — Nội dung file `excel_key.json` (dạng string JSON)

---

## 5. Kết nối Preset.io

**Bước thực hiện (thủ công 1 lần):**
1. Đăng ký [preset.io](https://preset.io/) (free tier)
2. **Settings → Database Connections → + Database → Google Sheets**
3. Paste URL Sheet: `https://docs.google.com/spreadsheets/d/1QBbKfdaEPsAwNWjIS9g71bnLoqAOMX75kQAM4KeJwng`
4. **Data → Datasets → + Dataset** — tạo dataset từng tab
5. **Charts → + Chart** — tạo chart từng dataset
6. **Dashboards → + Dashboard** — gộp charts

**Lưu ý:** Sheet cần được share "Anyone with the link can view" để Preset đọc được.

---

## 6. Roadmap

```
Phase 1 — ✅ DONE: Setup & Structure
  [x] Cấu trúc thư mục chuyên nghiệp
  [x] .env + .env.example
  [x] core/config.py (Python-dotenv)
  [x] core/sheets_manager.py (8 tabs)
  [x] core/base_agent.py (abstract)
  [x] GitHub Actions workflow

Phase 2 — ✅ DONE: Implement Agents
  [x] agents/cafef_agent.py (JSON API thuần, bỏ Playwright)
  [x] agents/customs_agent.py (HTML parse)
  [x] agents/textile_agent.py (BeautifulSoup)
  [x] agents/vinatex_agent.py (WordPress parse)
  [x] main.py orchestrator (CLI)

Phase 3 — 🔴 TODO: Test & Verify
  [ ] python setup_sheets.py (tạo 8 tabs)
  [ ] python main.py --agents cafef (test CafeF trước)
  [ ] python main.py --agents all (test toàn bộ)
  [ ] Fix nếu có lỗi API/parse

Phase 4 — 🔴 TODO: Kết nối Preset.io
  [ ] Đăng ký Preset.io
  [ ] Share Google Sheet "Anyone with link"
  [ ] Tạo database connection + 8 datasets
  [ ] Build charts & dashboard

Phase 5 — 🔴 TODO: Deploy GitHub Actions
  [ ] Push code lên repo ntai0404/seabank-crowler
  [ ] Thêm GitHub Secrets (SPREADSHEET_ID, GOOGLE_CREDENTIALS_JSON)
  [ ] Test manual trigger
  [ ] Verify cron chạy đúng giờ
```

---

## 7. Ghi chú kỹ thuật

- **CafeF Forex/Gold:** Đã chuyển **hoàn toàn sang JSON API** thay vì Playwright, không còn `sleep(10)`, nhanh hơn ~10x và ổn định hơn.
- **Playwright:** Vẫn còn trong requirements nhưng không được dùng trong pipeline hiện tại. Có thể bỏ nếu không cần fallback.
- **Rate limit:** ~350 mã cổ phiếu × 0.5s delay ≈ 3 phút. Trong giới hạn Google Sheets API (300 req/min).
- **GitHub Actions timeout:** 45 phút, đủ cho toàn bộ pipeline.
- **Idempotent:** Hiện tại append-only (không dedup). Nếu chạy 2 lần/ngày sẽ có 2 snapshot — đây là behavior mong muốn.
