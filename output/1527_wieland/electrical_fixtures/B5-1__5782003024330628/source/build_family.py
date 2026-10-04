"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'B3-2__2025454640496516/Astro_Duo_1184057_5048001_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='a4ad17ff2a9b448172a2e72b020ee812dec7c159f0bc3934123419efac3e7267'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='a4ad17ff2a9b448172a2e72b020ee812dec7c159f0bc3934123419efac3e7267'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
