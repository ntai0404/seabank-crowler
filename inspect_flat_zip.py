import zipfile
from pathlib import Path

zip_path = Path(r"C:\SINHVIEN\myprocj\Seabank-crowler\seabank_preset_assets.zip")
with zipfile.ZipFile(zip_path, 'r') as zf:
    print("ZIP structure:")
    for name in zf.namelist():
        print(f"  {name}")
