"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'B3-2__7654954174709636/Kuzco_Rona_VL17024_Chrome_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='48944d5ceaf0ab47810ad0e582ec0c05a6d90a46848e782b73841c4c2656f163'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='48944d5ceaf0ab47810ad0e582ec0c05a6d90a46848e782b73841c4c2656f163'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
