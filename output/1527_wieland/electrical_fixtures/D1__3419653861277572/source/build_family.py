"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'D1__5671453674962820/Juno_4BEMW_SWW5_90CRI_M6_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='5b266b753d2c31dc73e833b4fba205e551fbf0e42d105074b06c69b3e35016b9'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='5b266b753d2c31dc73e833b4fba205e551fbf0e42d105074b06c69b3e35016b9'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
