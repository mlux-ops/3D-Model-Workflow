"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'T1-2__2768226949398404/DVI_Courcelette_DVP27002GR_CL_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='39453542763c18cc368afff004c15df86db4111aaab00e856d173997a5dd8b31'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='39453542763c18cc368afff004c15df86db4111aaab00e856d173997a5dd8b31'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
