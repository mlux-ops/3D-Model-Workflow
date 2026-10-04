"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'BOM1273301__842052721573764/Bomma_Dew_Drops_Silver_Clear_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='5c20dba5938e579572139581d77277a3d842cbd796fb804a6d95bbf3f0a7442c'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='5c20dba5938e579572139581d77277a3d842cbd796fb804a6d95bbf3f0a7442c'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
