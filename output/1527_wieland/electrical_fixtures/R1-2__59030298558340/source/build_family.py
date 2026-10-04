"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'R1-2__1154902149234564/Modern_Forms_Zephyr_FR_W2006_52L_MB_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='b70e4dd0f9ac9067e95d630aaefb1ab535f56c148b6d236b499104076537ef35'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='b70e4dd0f9ac9067e95d630aaefb1ab535f56c148b6d236b499104076537ef35'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
