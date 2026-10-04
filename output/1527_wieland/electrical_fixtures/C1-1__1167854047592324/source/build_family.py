"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'C1-2__6797353581805444/Huxe_Silvio_5_Black_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='0b7246015359040b88a1dfa28da7306ffaf0765a46f989586efa91a128182830'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='0b7246015359040b88a1dfa28da7306ffaf0765a46f989586efa91a128182830'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
