"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'B3-1__1598063830957956/Visual_Comfort_Milan_700BCMLN24WS_LED930_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='0f028911873979a35a6c37d9a2f624584ed18a5a758f098f4ae6ab77a9821fa2'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='0f028911873979a35a6c37d9a2f624584ed18a5a758f098f4ae6ab77a9821fa2'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
