"""Measure the manufacturer's OBJ units and separate named shape groups."""
from pathlib import Path
from collections import Counter
import json
ROOT=Path(__file__).resolve().parents[1]
path=next(ROOT.glob('SKL*/source/SkLO_Hold12_manufacturer_3D/*.obj'))
verts=[];groups={};current='default'
for line in path.read_text(encoding='utf-8',errors='replace').replace('\\\n',' ').splitlines():
    fields=line.split()
    if not fields:continue
    if fields[0]=='v':verts.append([float(x) for x in fields[1:4]])
    elif fields[0] in ('g','o','usemtl'):current=' '.join(fields[1:]);groups.setdefault(current,[])
    elif fields[0]=='f':groups.setdefault(current,[]).append([int(x.split('/')[0])-1 for x in fields[1:]])
records=[]
for key,faces in groups.items():
    if not faces:continue
    indices=set(i for face in faces for i in face)
    pts=[verts[i] for i in indices]
    box=[min(p[a] for p in pts) for a in range(3)]+[max(p[a] for p in pts) for a in range(3)]
    edges=Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in faces for i in range(len(f)))
    records.append(dict(name=key,faces=len(faces),bounds=box,nonmanifold_edges=sum(n!=2 for n in edges.values()),polygon_sizes=dict(Counter(map(len,faces)))))
output={'source':str(path),'vertices':len(verts),'groups':records}
(ROOT/'SKLO_OBJ_INSPECTION.json').write_text(json.dumps(output,indent=2))
print(json.dumps(output,indent=2))
