"""Reproduce this row from its hash-verified native canonical family."""
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / 'Best_option_-_Orion_Tube_Pendant__1967952628416388/Lee_Broom_Orion_Tube_ORI0120_Horizontal_Assumed_R2025.rfa'
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()=='e60ed6c59964d49099d36944a839f243c80a6c216572637f8bd3d15867e39ba2'
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()=='e60ed6c59964d49099d36944a839f243c80a6c216572637f8bd3d15867e39ba2'
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
