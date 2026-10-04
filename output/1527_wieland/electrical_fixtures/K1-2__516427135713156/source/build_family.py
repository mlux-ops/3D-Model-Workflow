"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'K1-2__4773108898267012/Kuzco_Trinity_PD62014_BK_SM_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='fe93576ee113f76d89281584986e0ab231f6dde55ea078bbcf1596fa358541cb'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='fe93576ee113f76d89281584986e0ab231f6dde55ea078bbcf1596fa358541cb'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
