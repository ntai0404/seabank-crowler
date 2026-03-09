import zipfile
from pathlib import Path

zip_path = Path(r"C:\SINHVIEN\myprocj\Seabank-crowler\seabank_preset_assets.zip")

with zipfile.ZipFile(zip_path, 'r') as zf:
    print(f"FILES IN ZIP: {zf.namelist()}")
    
    with zf.open('metadata.yaml') as f:
        print(f"\nmetadata.yaml:\n{f.read().decode('utf-8')}")

    with zf.open('databases/google_sheets.yaml') as f:
        print(f"\ngoogle_sheets.yaml (first 500 chars):\n{f.read().decode('utf-8')[:500]}")
