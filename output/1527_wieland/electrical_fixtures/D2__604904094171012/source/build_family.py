"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'D2__7923253488648068/Juno_QC4_J6_Housing_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='8067608b45dc67d4d0222c11fd94e4073eb5cfcc3e00e2964d6ec9d730d97638'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='8067608b45dc67d4d0222c11fd94e4073eb5cfcc3e00e2964d6ec9d730d97638'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
