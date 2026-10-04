"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'B1-2__1457326342602628/Visual_Comfort_Pylon_Natural_Brass_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='3a1c2c013c79daf7225c0db4d3be7bede1664abf863005ee10278a2c5483fff7'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='3a1c2c013c79daf7225c0db4d3be7bede1664abf863005ee10278a2c5483fff7'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
