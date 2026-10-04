"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'HNM1353351__6471552255786884/Hollis_Morris_Oyster_BSS_FR_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='fe9707d37aa839d3b2fbf8893b7745d9879d0b8c9f703d1244c3b514a8a7a1a6'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='fe9707d37aa839d3b2fbf8893b7745d9879d0b8c9f703d1244c3b514a8a7a1a6'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
