"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'VIS1256139__8160402116050820/Vistosi_Faro_SP_P_Crystal_Black_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='6ef0573d12bef816aa6f03d0f03ecbe3d73019d81b938d3d1828b0ae3f2b99d2'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='6ef0573d12bef816aa6f03d0f03ecbe3d73019d81b938d3d1828b0ae3f2b99d2'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
