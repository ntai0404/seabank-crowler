import zipfile
from pathlib import Path

zip_path = Path(r"C:\SINHVIEN\myprocj\Seabank-crowler\seabank_preset_assets.zip")

with zipfile.ZipFile(zip_path, 'r') as zf:
    print(f"FILES IN ZIP: {zf.namelist()}")
    
    if 'metadata.yaml' in zf.namelist():
        with zf.open('metadata.yaml') as f:
            content = f.read()
            print(f"\nmetadata.yaml RAW: {content}")
            print(f"metadata.yaml DECODED: {content.decode('utf-8')}")
            print(f"metadata.yaml REPR: {repr(content.decode('utf-8'))}")
    else:
        print("\n❌ metadata.yaml MISSING from ZIP root!")

    # Check google_sheets.yaml too
    gs_path = 'databases/google_sheets.yaml'
    if gs_path in zf.namelist():
        with zf.open(gs_path) as f:
            content = f.read()
            print(f"\n{gs_path} Size: {len(content)} bytes")
            # Print first 100 chars
            print(f"{gs_path} REPR (first 100): {repr(content[:100].decode('utf-8'))}")
