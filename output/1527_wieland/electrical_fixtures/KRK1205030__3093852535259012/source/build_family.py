"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'KRK1205030__5345652348944260/Tom_Kirk_Reed_Outward_Polished_Nickel_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='c51f0f4dc62eb36e7cf7dc0a68adc71e27c4719962e610158a39e3a9b112f2c3'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='c51f0f4dc62eb36e7cf7dc0a68adc71e27c4719962e610158a39e3a9b112f2c3'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
