"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'B3-2__7086825876815748/Visual_Comfort_Tris_700BCTRS3C_LED930_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='5099c2ace2925d401013041cc0bb73dd081cf01651e4e3a87de4dbd20c3e55b3'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='5099c2ace2925d401013041cc0bb73dd081cf01651e4e3a87de4dbd20c3e55b3'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
