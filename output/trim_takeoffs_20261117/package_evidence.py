from pathlib import Path
import zipfile,json
p=Path(r"C:\Users\found\Documents\3\3D-Model-Workflow\output\trim_takeoffs_20261117")
with zipfile.ZipFile(p/'Trim_Source_Review_651_Belmont_1529_Wieland_2026-11-17.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in [p/'README - Draft scope and holds.txt']+sorted(p.glob('sheet_*.png')):
  z.write(f,f.name)
print('Evidence archive created.')
