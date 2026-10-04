"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'RG-C811A__240438544629636/Panasonic_WhisperChoice_RG_C811A_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='964037726335371d1af9c007f723ec7ac951ce97af68fd526a22fa36ee97df87'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='964037726335371d1af9c007f723ec7ac951ce97af68fd526a22fa36ee97df87'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
