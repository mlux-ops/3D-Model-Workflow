import json,gzip,collections
from pathlib import Path
root=Path(__file__).resolve().parents[1]
index=json.loads((root/'native_mesh_index.json').read_text())
row=next(x for x in index if x['folder'].startswith('f10'))
with gzip.open(row['mesh'],'rt') as f:data=json.load(f)
for key,mat in data['materials'].items():print('MATERIAL',key,mat)
for p in data['parts']:
    print('PART',p['element'],'Z',[min(v[2] for v in p['vertices'])/.0254,max(v[2] for v in p['vertices'])/.0254],'MATERIAL_COUNTS',dict(collections.Counter(p['material_ids'])))
    normals=collections.Counter()
    for face,key in zip(p['triangles'],p['material_ids']):
        avg=sum(p['normals'][i][2] for i in face)/3
        if abs(avg)>.99:normals[(key,round(avg,2))]+=1
    print('CAP_NORMALS',dict(normals))