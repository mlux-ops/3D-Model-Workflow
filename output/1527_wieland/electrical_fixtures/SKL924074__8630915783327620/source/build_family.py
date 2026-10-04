"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'SKL924074__1405002674995076/SkLO_Hold12_LT267_White_Dark_Oxidized_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='880664e6346d6aeafb9c56e60e79e6611ea220851197275b365b4ee6a2589b40'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='880664e6346d6aeafb9c56e60e79e6611ea220851197275b365b4ee6a2589b40'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
