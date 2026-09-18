from pathlib import Path
import struct,collections,json
r=Path(__file__).resolve().parent
result=[]
for p in r.glob('*upper_mushroom.stl'):
 d=p.read_bytes();edges=collections.Counter();vol=0;verts=[]
 for i in range(struct.unpack_from('<I',d,80)[0]):
  v=struct.unpack_from('<12fH',d,84+i*50);a,b,c=[tuple(round(x,5) for x in v[j:j+3]) for j in [3,6,9]];verts.extend([a,b,c])
  for x,y in [(a,b),(b,c),(c,a)]:edges[tuple(sorted([x,y]))]+=1
  vol+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
 row={'file':p.name,'volume':round(vol,2),'bad_edges':sum(n!=2 for n in edges.values()),'edge_counts':dict(collections.Counter(edges.values())),'bounds':[[min(v[j] for v in verts),max(v[j] for v in verts)] for j in range(3)]};result.append(row)
print(json.dumps(result,indent=2));(r/'mesh_audit.json').write_text(json.dumps(result,indent=2))
