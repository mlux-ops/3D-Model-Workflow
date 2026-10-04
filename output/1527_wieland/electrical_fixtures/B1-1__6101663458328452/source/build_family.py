"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'B1-2__1395409177739140/Minka_Verto_3114_732_L_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='1c0e49202f970f0fc31dd282bd56ad333711ae96a0232405b4e94a26dc02c8de'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='1c0e49202f970f0fc31dd282bd56ad333711ae96a0232405b4e94a26dc02c8de'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
