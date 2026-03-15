# ============================================================
# preset_integration/preset_builder.py
# Đóng gói bộ Assets chuẩn "Native Export" (Preset.io) v1.31
# ============================================================

import os
import shutil
import zipfile
import yaml
import json
import uuid
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def build_preset_assets():
    print("--- 🚀 Preset Asset Builder v1.31 (Native Mirror Fix) ---")
    
    # 1. Config load
    base_dir = Path(__file__).parent
    config_path = base_dir / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    spreadsheet_id = config.get("spreadsheet_id")
    dashboard_title = config.get("dashboard_title", "SeaBank Monitor")
    
    # 2. Database UUID (Lấy từ config hoặc fallback)
    MANUAL_DB_UUID = config.get("database_uuid", "482b5b73-c5e8-4f35-a665-7236f5a0904b")
    
    # 3. UUID cố định (Dãy 551...) mới hoàn toàn cho v1.56
    U_DS_INTEREST  = "5518f6ce-d922-4857-8478-41d81a929111"
    U_DS_STOCK     = "5518f6ce-d922-4857-8478-41d81a929212"
    U_DS_NEWS      = "5518f6ce-d922-4857-8478-41d81a929113"
    U_DS_METRICS   = "5518f6ce-d922-4857-8478-41d81a929114"
    U_DS_CUSTOMS   = "5518f6ce-d922-4857-8478-41d81a929115"
    U_DASH         = "5518f6ce-d922-4857-8478-41d81a929116"
    U_DASH_LONG    = "5518f6ce-d922-4857-8478-41d81a929216"
    U_DS_EXCHANGE  = "5518f6ce-d922-4857-8478-41d81a929117"
    U_DS_BANKING   = "5518f6ce-d922-4857-8478-41d81a929118"
    U_DS_GOLD      = "5518f6ce-d922-4857-8478-41d81a929119"
    U_DS_COMMODITY = "5518f6ce-d922-4857-8478-41d81a929120"
    U_DS_DIRECTORY = "5518f6ce-d922-4857-8478-41d81a929130"

    DATASET_UUIDS = {
        "bank_interest_rates.yaml": U_DS_INTEREST,
        "stock_prices.yaml": U_DS_STOCK,
        "textile_news.yaml": U_DS_NEWS,
        "web_metrics.yaml": U_DS_METRICS,
        "customs_trade.yaml": U_DS_CUSTOMS,
        "exchange_rates.yaml": U_DS_EXCHANGE,
        "banking_news.yaml": U_DS_BANKING,
        "gold_prices.yaml": U_DS_GOLD,
        "customs_commodity_details.yaml": U_DS_COMMODITY,
        "textile_directory.yaml": U_DS_DIRECTORY,
    }
    
    CHART_UUIDS = {
        "interest_rate_bar.yaml":      "5518f6ce-d922-4857-8478-41d81a929121",
        "stock_trend_line.yaml":       "5518f6ce-d922-4857-8478-41d81a929201",
        "customs_trade_mixed.yaml":    "5518f6ce-d922-4857-8478-41d81a929202",
        "banking_news_table.yaml":     "5518f6ce-d922-4857-8478-41d81a929154",
        "textile_news_table.yaml":     "5518f6ce-d922-4857-8478-41d81a929125",
        "exchange_rates_table.yaml":   "5518f6ce-d922-4857-8478-41d81a929152",
        "bank_stocks_table.yaml":      "5518f6ce-d922-4857-8478-41d81a929153",
        "interest_rate_12m_bar.yaml":  "5518f6ce-d922-4857-8478-41d81a929149",
        "gold_prices_trend_line.yaml": "5518f6ce-d922-4857-8478-41d81a929221",
        "customs_export_by_period.yaml": "5518f6ce-d922-4857-8478-41d81a929222",
        "customs_import_by_period.yaml": "5518f6ce-d922-4857-8478-41d81a929223",
        "textile_directory_type_bar.yaml": "5518f6ce-d922-4857-8478-41d81a929224",
    }

    CHART_MAP = {
        "interest_rate_bar.yaml":      U_DS_INTEREST,
        "stock_trend_line.yaml":       U_DS_STOCK,
        "customs_trade_mixed.yaml":    U_DS_CUSTOMS,
        "banking_news_table.yaml":     U_DS_BANKING,
        "textile_news_table.yaml":     U_DS_NEWS,
        "exchange_rates_table.yaml":   U_DS_EXCHANGE,
        "bank_stocks_table.yaml":      U_DS_STOCK,
        "interest_rate_12m_bar.yaml":  U_DS_INTEREST,
        "gold_prices_trend_line.yaml": U_DS_GOLD,
        "customs_export_by_period.yaml": U_DS_COMMODITY,
        "customs_import_by_period.yaml": U_DS_COMMODITY,
        "textile_directory_type_bar.yaml": U_DS_DIRECTORY,
    }

    DASHBOARD_UUIDS = {
        "seabank_monitor.yaml": U_DASH,
        "seabank_longterm_monitor.yaml": U_DASH_LONG,
    }

    template_dir = base_dir / "assets"
    root_name = "seabank_export_v31"
    build_dir = base_dir / "dist" / root_name
    
    if base_dir.joinpath("dist").exists(): shutil.rmtree(base_dir / "dist")
    build_dir.mkdir(parents=True)

    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith(".yaml"):
                rel_path = Path(root).relative_to(template_dir)
                
                # Rename datasets folder to datasources for Preset
                if rel_path.name == "datasets":
                    target_subdir = build_dir / "datasources"
                else:
                    target_subdir = build_dir / rel_path
                target_subdir.mkdir(parents=True, exist_ok=True)
                
                source_file = Path(root) / file
                target_file = target_subdir / file
                
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace placeholders
                content = content.replace("${DASHBOARD_TITLE}", dashboard_title)
                content = content.replace("${DATABASE_UUID}", MANUAL_DB_UUID)
                spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
                content = content.replace("${SPREADSHEET_URL}", spreadsheet_url)
                
                data = yaml.safe_load(content)

                # A. DATASETS - Match exact Preset.io export format & field order
                if rel_path.name == "datasets":
                    # Create ordered dict matching Preset export field order
                    ordered_data = {}
                    
                    # 1-4: Basic identification fields
                    ordered_data["table_name"] = data.get("table_name")
                    ordered_data["main_dttm_col"] = data.get("main_dttm_col")
                    ordered_data["currency_code_column"] = None
                    ordered_data["description"] = data.get("description")
                    
                    # 5-9: Configuration fields
                    ordered_data["default_endpoint"] = None
                    ordered_data["offset"] = 0
                    ordered_data["cache_timeout"] = None
                    ordered_data["catalog"] = None
                    ordered_data["schema"] = data.get("schema")
                    
                    # 14-19: Behavior flags
                    ordered_data["filter_select_enabled"] = True
                    ordered_data["fetch_values_predicate"] = None
                    ordered_data["extra"] = None
                    ordered_data["normalize_columns"] = False
                    ordered_data["always_filter_main_dttm"] = False
                    ordered_data["folders"] = None
                    
                    # 20: UUID (assign based on filename)
                    ordered_data["uuid"] = DATASET_UUIDS.get(file, data.get("uuid"))
                    
                    # 21: Metrics (with proper fields)
                    if "metrics" in data:
                        ordered_metrics = []
                        for metric in data["metrics"]:
                            m = {}
                            m["metric_name"] = metric.get("metric_name")
                            m["verbose_name"] = metric.get("verbose_name")
                            m["metric_type"] = None
                            m["expression"] = metric.get("expression")
                            m["description"] = None
                            m["d3format"] = None
                            m["currency"] = None
                            m["extra"] = None
                            m["warning_text"] = None
                            ordered_metrics.append(m)
                        ordered_data["metrics"] = ordered_metrics
                    
                    # 22: Columns (with proper field order and values)
                    if "columns" in data:
                        ordered_columns = []
                        for col in data["columns"]:
                            c = {}
                            c["column_name"] = col.get("column_name")
                            c["verbose_name"] = col.get("verbose_name")
                            # Set is_dttm based on type
                            c["is_dttm"] = col.get("is_dttm", col.get("type") == "DATETIME")
                            c["is_active"] = True
                            c["type"] = col.get("type")
                            c["advanced_data_type"] = None
                            c["groupby"] = True
                            c["filterable"] = True
                            c["expression"] = None
                            c["description"] = None
                            c["python_date_format"] = None
                            c["datetime_format"] = None
                            c["extra"] = None
                            ordered_columns.append(c)
                        ordered_data["columns"] = ordered_columns
                    
                    # 23: Preserve SQL for virtual datasets / typed casts used by charts
                    ordered_data["sql"] = data.get("sql")

                    # 24-25: Last fields (version and database_uuid at END!)
                    ordered_data["version"] = "1.0.0"
                    ordered_data["database_uuid"] = MANUAL_DB_UUID
                    
                    # Replace data with ordered version
                    data = ordered_data
                
                # B. CHARTS
                elif rel_path.name == "charts":
                    data["uuid"] = CHART_UUIDS.get(file, str(uuid.uuid4()))
                    data["dataset_uuid"] = CHART_MAP.get(file, U_DS_METRICS)
                
                # C. DASHBOARD
                elif rel_path.name == "dashboards":
                    data["uuid"] = DASHBOARD_UUIDS.get(file, data.get("uuid", str(uuid.uuid4())))
                    if "position" in data:
                        for k, v in data["position"].items():
                            if k.startswith("CHART-"):
                                ck = {
                                    "CHART-1": "interest_rate_bar.yaml",
                                    "CHART-2": "stock_trend_line.yaml",
                                    "CHART-3": "customs_trade_mixed.yaml",
                                    "CHART-4": "banking_news_table.yaml",
                                    "CHART-5": "textile_news_table.yaml",
                                    "CHART-6": "exchange_rates_table.yaml",
                                    "CHART-7": "interest_rate_12m_bar.yaml",
                                    "CHART-8": "bank_stocks_table.yaml",
                                    "CHART-101": "gold_prices_trend_line.yaml",
                                    "CHART-102": "customs_export_by_period.yaml",
                                    "CHART-103": "customs_import_by_period.yaml",
                                    "CHART-104": "textile_directory_type_bar.yaml",
                                }.get(k)
                                if ck in CHART_UUIDS:
                                    v["meta"]["uuid"] = CHART_UUIDS[ck]
                
                # D. DATABASES
                elif rel_path.name == "databases":
                    # UUID already replaced via placeholder
                    # Spreadsheet URL already replaced via placeholder
                    pass

                # Write as YAML format (matching Preset export format)
                with open(target_file, 'w', encoding='utf-8', newline='\n') as f:
                    yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
                
                # Print with correct folder name
                display_path = "datasources" if rel_path.name == "datasets" else str(rel_path if str(rel_path) != '.' else '')
                print(f"  ✅ {display_path}/{file}")

    # 5. Đóng gói ZIP (Dashboard Export Structure - full export with charts & dashboards)
    export_name = f"seabank_dashboard_{datetime.now().strftime('%Y%m%dT%H%M%S')}"
    zip_fn = str(base_dir.parent / f"{export_name}.zip")
    database_name = "Seabank_Manual"
    
    with zipfile.ZipFile(zip_fn, 'w', zipfile.ZIP_DEFLATED) as z:
        # Metadata.yaml - Dashboard type
        metadata = {
            "version": "1.0.0",
            "type": "Dashboard",
            "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '+00:00'
        }
        metadata_content = yaml.dump(metadata, allow_unicode=True, default_flow_style=False, sort_keys=False)
        z.writestr(f"{export_name}/metadata.yaml", metadata_content)
        
        # Database file: databases/DatabaseName.yaml
        db_path = build_dir / "databases" / "google_sheets.yaml"
        if db_path.exists():
            with open(db_path, 'r', encoding='utf-8') as f:
                db_content = f.read()
            z.writestr(f"{export_name}/databases/{database_name}.yaml", db_content)
        
        # Dataset files: datasets/DatabaseName/table.yaml
        datasets_dir = build_dir / "datasources"
        if datasets_dir.exists():
            for dataset_file in datasets_dir.glob("*.yaml"):
                with open(dataset_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                z.writestr(f"{export_name}/datasets/{database_name}/{dataset_file.name}", content)
        
        # Chart files: charts/chart.yaml
        charts_dir = build_dir / "charts"
        if charts_dir.exists():
            for chart_file in charts_dir.glob("*.yaml"):
                with open(chart_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                z.writestr(f"{export_name}/charts/{chart_file.name}", content)
        
        # Dashboard files: dashboards/dashboard.yaml
        dashboards_dir = build_dir / "dashboards"
        if dashboards_dir.exists():
            for dashboard_file in dashboards_dir.glob("*.yaml"):
                with open(dashboard_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                z.writestr(f"{export_name}/dashboards/{dashboard_file.name}", content)

    print(f"--- ✨ HOÀN TẤT: {zip_fn} v1.48 (Dashboard Export with Charts) ---")

if __name__ == "__main__":
    build_preset_assets()
