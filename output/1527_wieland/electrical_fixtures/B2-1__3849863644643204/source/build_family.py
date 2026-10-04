"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'B2-2__8673064965046148/Kuzco_Cedar_WS52505_BK_CL_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='69a5901fcf9fa0731a7a4e06b12aae257641dc61f014cdd9c7eaa3753549f81b'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='69a5901fcf9fa0731a7a4e06b12aae257641dc61f014cdd9c7eaa3753549f81b'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
