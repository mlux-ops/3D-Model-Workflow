"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'L4-0__8334187740856196/Maxim_Trim_57670WTBK_Black_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='07b6f3713c99677a21afc7cf5aa0a9680361e34d1e9f645dc75b8224a5a2a086'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='07b6f3713c99677a21afc7cf5aa0a9680361e34d1e9f645dc75b8224a5a2a086'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
