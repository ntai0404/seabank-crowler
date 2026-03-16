# SeaBank Crawler v2.0 - Extended Plan

## Overview
Building upon the core engine established in `herewegoagain.md`, version 2.0 (branch `crowlerV2`) focuses on data depth, reliability, and expanded analytics.

## Schema Enhancements (Tentative)
- **Sentiment Analysis**: Add `sentiment_score` to `textile_news` and `web_metrics`.
- **Competitor Tracking**: Add `competitor_bank_rates` for broader comparison.
- **Historical Trends**: Optimize `stock_prices` for long-term historical storage.

## Development Goals
1. **Robust Error Handling**: Enhance agent recovery from UI changes.
2. **Performance Optimization**: Reduce crawl time by parallelizing browser instances.
3. **Advanced Preset Dashboards**: Implement drill-down features in Preset.io.

## Success Metrics
- 99% crawl success rate.
- < 1% data duplication in Google Sheets.
- Dashboard refresh latency < 30 seconds.
