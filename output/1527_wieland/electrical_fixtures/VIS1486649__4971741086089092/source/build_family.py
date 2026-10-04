"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'VIS1486649__3656802488680324/Vistosi_Jube_AP_S_Smoke_Black_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='a95279ebc11a43c9cf3099387b904f0617c984a8b460304d647362940f81e660'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='a95279ebc11a43c9cf3099387b904f0617c984a8b460304d647362940f81e660'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
