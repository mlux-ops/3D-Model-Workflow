"""Verify the binary STL exports and pack the deliverable using Python stdlib."""
from pathlib import Path
import struct, json, math, collections, zipfile
ROOT=Path(__file__).resolve().parent
def read(path):
    data=path.read_bytes(); n=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*n
    return [struct.unpack_from('<12fH',data,84+50*i) for i in range(n)]
def check(records,expected_components):
    edge=collections.Counter(); directed=collections.Counter(); adj=collections.defaultdict(set)
    volume=0;verts=set();degenerate=0
    for rec in records:
        a,b,c=[tuple(round(v,5) for v in rec[j:j+3]) for j in [3,6,9]]
        u=tuple(b[i]-a[i] for i in range(3));v=tuple(c[i]-a[i] for i in range(3))
        cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        if sum(w*w for w in cross)<1e-14:degenerate+=1
        volume+=sum(a[i]*cross[i] for i in range(3))/6
        for p,q in [(a,b),(b,c),(c,a)]:
            edge[tuple(sorted((p,q)))]+=1;directed[(p,q)]+=1
            adj[p].add(q);adj[q].add(p);verts.update([p,q])
    bad=sum(n!=2 for n in edge.values())
    winding=sum(directed[(a,b)]!=directed[(b,a)] for a,b in edge)
    remaining=set(verts);components=0
    while remaining:
        components+=1;todo=[remaining.pop()]
        while todo:
            new=adj[todo.pop()] & remaining;remaining.difference_update(new);todo.extend(new)
    result={'triangles':len(records),'non_manifold_edges':bad,'inconsistent_edge_winding':winding,
        'degenerate_triangles':degenerate,'connected_shells':components,'volume_mm3':round(volume,3),
        'dimensions_mm':[round(max(p[i] for p in verts)-min(p[i] for p in verts),3) for i in range(3)]}
    assert bad==winding==degenerate==0 and components==expected_components and volume>0,result
    return result

files=['01_concealed_frame.stl','02_top_carriage.stl']+[p.name for p in sorted(ROOT.glob('lower_*.stl'))]+[p.name for p in sorted(ROOT.glob('upper_*.stl'))]
report={name:check(read(ROOT/name),1) for name in files}
plates=[]
for lower in sorted(ROOT.glob('lower_*.stl')):
    tag=lower.stem.removeprefix('lower_');plate=[]
    layout=[(files[0],0,0),(files[1],75,0),(lower.name,75,28),(lower.name,75,58),('upper_'+tag+'.stl',0,94)]
    for name,x,y in layout:
        for rec in read(ROOT/name):
            r=list(rec)
            for j in [3,6,9]:r[j]+=x;r[j+1]+=y
            plate.append(r)
    path=ROOT/('plate_'+tag+'.stl')
    with path.open('wb') as f:
        f.write(b'QuietMount 5 components for ONE sample; mm'.ljust(80,b' '));f.write(struct.pack('<I',len(plate)))
        for r in plate:f.write(struct.pack('<12fH',*r))
    report[path.name]=check(read(path),5);plates.append(path.name)
(ROOT/'stl_checks.json').write_text(json.dumps(report,indent=2))
extras=['README.md','minimal-preview.png','concealed-mechanism.png','QuietMount-assembly.blend',
        'build_model.py','package_model.py','geometry_checks.json','stl_checks.json']
with zipfile.ZipFile(ROOT/'QuietMount-minimal-STLs.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in files+plates+extras:z.write(ROOT/name,'QuietMount/'+name)
with zipfile.ZipFile(ROOT/'QuietMount-minimal-STLs.zip') as z:assert z.testzip() is None
print(json.dumps(report,indent=2))
print('Verified',len(files),'individual STLs and',len(plates),'print plates. ZIP integrity passed.')
