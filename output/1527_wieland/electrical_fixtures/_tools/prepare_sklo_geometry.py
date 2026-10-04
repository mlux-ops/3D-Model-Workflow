"""Recover welded manufacturer glass topology and align it to current nominal sizes."""
from pathlib import Path
from collections import Counter
import json
ROOT=Path(__file__).resolve().parents[1]
path=next(ROOT.glob('SKL*/source/SkLO_Hold12_manufacturer_3D/*.obj'))
vertices=[];faces=[];current=''
for line in path.read_text(encoding='utf-8',errors='replace').replace('\\\n',' ').splitlines():
    f=line.split()
    if not f:continue
    if f[0]=='v':vertices.append([float(x) for x in f[1:4]])
    elif f[0] in ('g','o','usemtl'):current=' '.join(f[1:])
    elif f[0]=='f' and current=='GLASS':faces.append([int(x.split('/')[0])-1 for x in f[1:]])
unique={};points=[];converted=[]
for face in faces:
    ids=[]
    for idx in face:
        p=vertices[idx];key=tuple(round(x,4) for x in p)
        if key not in unique:unique[key]=len(points);points.append(p)
        ids.append(unique[key])
    if len(set(ids))==len(ids):converted.append(ids)
edges=Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in converted for i in range(len(f)))
box=[min(p[a] for p in points) for a in range(3)]+[max(p[a] for p in points) for a in range(3)]
mapped=[[(p[1]-(box[1]+box[4])/2)*5/(box[4]-box[1]),-9+(p[2]-box[2])*12/(box[5]-box[2]),2+(p[0]-box[0])*3.5/(box[3]-box[0])] for p in points]
result=dict(source=str(path),source_units='millimetres',source_bounds_mm=box,
    adjustment='Current manufacturer nominal 5-inch glass width and 12-inch height. Source OBJ width is larger than nominal; mapped expressly to the current nominal silhouette. Glass depth 3.5 inches and forward placement are drawing-derived.',
    vertices_in=mapped,faces=converted,boundary_edges=sum(n==1 for n in edges.values()),nonmanifold_edges=sum(n!=2 for n in edges.values()))
dest=path.parents[1]/'sklo_glass_nominal_mesh.json';dest.write_text(json.dumps(result,separators=(',',':')))
print(json.dumps({k:v for k,v in result.items() if k not in ('vertices_in','faces')},indent=2))
print('Welded vertices',len(points),'faces',len(converted),'staged',dest)
