import os
import yaml
import json
from pathlib import Path

dist_dir = Path(r"C:\SINHVIEN\myprocj\Seabank-crowler\preset_integration\dist")
assets_zip = Path(r"C:\SINHVIEN\myprocj\Seabank-crowler\seabank_preset_assets.zip")

print(f"Checking files in {dist_dir}:")
for root, dirs, files in os.walk(dist_dir):
    for file in files:
        if file.endswith(".yaml"):
            p = Path(root) / file
            print(f"File: {p.relative_to(dist_dir)}")
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        print("  ❌ ERROR: File is EMPTY")
                        continue
                    data = yaml.safe_load(content)
                    print(f"  ✅ YAML valid. Size: {len(content)} bytes")
                    
                    # Check for potential JSON string issues
                    if "extra" in data and isinstance(data["extra"], str):
                        try:
                            json.loads(data["extra"])
                            print("    ✅ extra JSON valid")
                        except Exception as e:
                            print(f"    ❌ extra JSON invalid: {e}")
                            
                    if "encrypted_extra" in data and isinstance(data["encrypted_extra"], str):
                        try:
                            json.loads(data["encrypted_extra"])
                            print("    ✅ encrypted_extra JSON valid")
                        except Exception as e:
                            print(f"    ❌ encrypted_extra JSON invalid: {e}")
            except Exception as e:
                print(f"  ❌ YAML invalid: {e}")

from zipfile import ZipFile
print(f"\nChecking metadata.yaml in {assets_zip}:")
try:
    with ZipFile(assets_zip, 'r') as zf:
        with zf.open('metadata.yaml') as f:
            content = f.read().decode('utf-8')
            print(f"Content:\n{content}")
            yaml.safe_load(content)
            print("  ✅ metadata.yaml valid")
except Exception as e:
    print(f"  ❌ metadata.yaml invalid or missing: {e}")
