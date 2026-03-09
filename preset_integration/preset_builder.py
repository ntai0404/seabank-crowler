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

    # 2. Database UUID (Đã "dò" thấy)
    MANUAL_DB_UUID = "482b5b73-c5e8-4f35-a665-7236f5a0904b"
    
    # 3. UUID cố định (Dãy 131...) mới hoàn toàn cho v1.31
    U_DS_INTEREST = "1318f6ce-d922-4857-8478-41d81a929111"
    U_DS_STOCK    = "1318f6ce-d922-4857-8478-41d81a929112"
    U_DS_NEWS     = "1318f6ce-d922-4857-8478-41d81a929113"
    U_DS_METRICS  = "1318f6ce-d922-4857-8478-41d81a929114"
    U_DS_CUSTOMS  = "1318f6ce-d922-4857-8478-41d81a929115"
    U_DASH        = "1318f6ce-d922-4857-8478-41d81a929116"
    
    CHART_UUIDS = {
        "interest_rate_bar.yaml":   "1318f6ce-d922-4857-8478-41d81a929121",
        "stock_trend_line.yaml":    "1318f6ce-d922-4857-8478-41d81a929122",
        "customs_trade_mixed.yaml": "1318f6ce-d922-4857-8478-41d81a929123",
        "web_metrics_table.yaml":   "1318f6ce-d922-4857-8478-41d81a929124",
        "textile_news_table.yaml":  "1318f6ce-d922-4857-8478-41d81a929125"
    }

    CHART_MAP = {
        "interest_rate_bar.yaml":   U_DS_INTEREST,
        "stock_trend_line.yaml":    U_DS_STOCK,
        "customs_trade_mixed.yaml": U_DS_CUSTOMS,
        "web_metrics_table.yaml":   U_DS_METRICS,
        "textile_news_table.yaml":  U_DS_NEWS
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
                
                # HEADLESS: Bỏ qua folder database
                if rel_path.name == "databases" or file == "google_sheets.yaml":
                    continue

                target_subdir = build_dir / rel_path
                target_subdir.mkdir(parents=True, exist_ok=True)
                
                source_file = Path(root) / file
                target_file = target_subdir / file
                
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content = content.replace("${DASHBOARD_TITLE}", dashboard_title)
                
                data = yaml.safe_load(content)
                data["version"] = "1.0.0"

                # A. DATASETS
                if rel_path.name == "datasets":
                    data["database_uuid"] = MANUAL_DB_UUID
                    data["schema"] = "SeaBank_Data"
                    if "interest" in file: data["uuid"] = U_DS_INTEREST
                    elif "stock" in file: data["uuid"] = U_DS_STOCK
                    elif "news" in file: data["uuid"] = U_DS_NEWS
                    elif "metrics" in file: data["uuid"] = U_DS_METRICS
                    elif "customs" in file: data["uuid"] = U_DS_CUSTOMS
                
                # B. CHARTS
                elif rel_path.name == "charts":
                    data["uuid"] = CHART_UUIDS.get(file, str(uuid.uuid4()))
                    data["dataset_uuid"] = CHART_MAP.get(file, U_DS_METRICS)
                
                # C. DASHBOARD
                elif rel_path.name == "dashboards":
                    data["uuid"] = U_DASH
                    data["dashboard_title"] = dashboard_title
                    if "position" in data:
                        for k, v in data["position"].items():
                            if k.startswith("CHART-"):
                                ck = {"CHART-1":"interest_rate_bar.yaml","CHART-2":"stock_trend_line.yaml","CHART-3":"customs_trade_mixed.yaml","CHART-4":"web_metrics_table.yaml","CHART-5":"textile_news_table.yaml"}.get(k)
                                if ck in CHART_UUIDS: 
                                    v["meta"]["uuid"] = CHART_UUIDS[ck]

                with open(target_file, 'w', encoding='utf-8', newline='\n') as f:
                    yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, width=20000, indent=2, allow_unicode=True)
                print(f"  ✅ {rel_path if str(rel_path) != '.' else ''}/{file}")

    # 5. Đóng gói ZIP 
    zip_fn = str(base_dir.parent / "seabank_preset_assets.zip")
    with zipfile.ZipFile(zip_fn, 'w', zipfile.ZIP_DEFLATED) as z:
        metadata = {"version": "1.0.0", "type": "Dashboard", "timestamp": datetime.now().isoformat()}
        z.writestr(f"{root_name}/metadata.yaml", yaml.dump(metadata).replace("\r\n", "\n"))
        
        base_dist = base_dir / "dist"
        for root, _, files in os.walk(base_dist):
            for file in files:
                abs_p = Path(root) / file
                rel_p = abs_p.relative_to(base_dist).as_posix()
                with open(abs_p, 'r', encoding='utf-8') as f:
                    z.writestr(rel_p, f.read().replace("\r\n", "\n"))

    print(f"--- ✨ HOÀN TẤT: {zip_fn} v1.31 (Native Mirror Fix) ---")

if __name__ == "__main__":
    build_preset_assets()
