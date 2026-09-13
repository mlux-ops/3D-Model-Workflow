from pathlib import Path
import json
s=(Path(__file__).resolve().parent.parent/'sample-holder-v2-minimal/package_model.py').read_text()
exec(s[:s.index('files=')])
r=Path(__file__).resolve().parent
report={}
for p in r.glob('*.stl'):
    records=read(p)
    try:report[p.name]=check(records,1)
    except AssertionError:
        for rec in records:
            a,b,c=[tuple(round(v,5) for v in rec[j:j+3]) for j in [3,6,9]]
            u=tuple(b[i]-a[i] for i in range(3));v=tuple(c[i]-a[i] for i in range(3))
            cr=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
            if sum(w*w for w in cr)<1e-14: print('Degenerate',p.name,a,b,c)
        raise
(r/'stl_checks.json').write_text(json.dumps(report,indent=2))
print('Verified',len(report),'closed, single-shell STL files with no degenerate triangles.')
