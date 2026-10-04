"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'B2-2__5960925969973124/RBW_Dimple_S1_AA04_White_Interior_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='ade1d78f8a0178f0063119a6193659f4a079fccf8d03b96df48ea2048e9c2c15'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='ade1d78f8a0178f0063119a6193659f4a079fccf8d03b96df48ea2048e9c2c15'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
