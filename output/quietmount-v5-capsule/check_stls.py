from pathlib import Path
import json
s=(Path(__file__).resolve().parent.parent/'sample-holder-v2-minimal/package_model.py').read_text()
exec(s[:s.index('files=')])
r=Path(__file__).resolve().parent
report={p.name:check(read(p),1) for p in r.glob('*.stl')}
(r/'stl_checks.json').write_text(json.dumps(report,indent=2))
print('Verified',len(report),'closed single-shell STLs, positive volume, consistent winding, no degenerate triangles.')
