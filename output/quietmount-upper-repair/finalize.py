from pathlib import Path
import json,shutil,zipfile
r=Path(__file__).resolve().parent
d=json.loads((r/'sliced/result.json').read_text());assert d['return_code']==0
with zipfile.ZipFile(r/'sliced/QuietMount_BC_Replacement_READY.3mf') as z:
 assert z.testzip() is None
 assert any(n.endswith('.gcode') for n in z.namelist())
s=(r/'package.py').read_text();exec(s[s.index("shutil.copyfile(r/'sliced"):])
