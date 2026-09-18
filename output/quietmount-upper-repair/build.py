from pathlib import Path
import math,struct,json,collections
r=Path(__file__).resolve().parent;N=128
def outer(w,h,cy):
 return [(7+(w/2-6)*(1 if math.cos(a)>=0 else -1)+6*math.cos(a),cy+(h/2-6)*(1 if math.sin(a)>=0 else -1)+6*math.sin(a)) for a in [2*math.pi*i/N for i in range(N)]]
def circle(rad):return [(7+rad*math.cos(2*math.pi*i/N),9.8+rad*math.sin(2*math.pi*i/N)) for i in range(N)]
report=[]
for label,t in zip('ABCDEFGHIJ',[12.7,19.05,19.05,20,22.225,20.5,18.5,18,14,17]):
 L=t+3.75;vs=[];fs=[]
 def ring(points,z):
  start=len(vs);vs.extend((x,y,z) for x,y in points);return list(range(start,start+N))
 def link(a,b,reverse=False):
  for i in range(N):
   j=(i+1)%N
   for f in [(a[i],a[j],b[j]),(a[i],b[j],b[i])]:fs.append(tuple(reversed(f)) if reverse else f)
 foot=outer(14,15.8,7.9);body=outer(14,12,9.8)
 a=ring(foot,0);b=ring(foot,2.2);c=ring(body,2.2);d=ring(body,L)
 e=ring(circle(4.3),0);f=ring(circle(4.3),L-4);g=ring(circle(2.3),L-4);h=ring(circle(2.3),L)
 for x,y in [(a,b),(b,c),(c,d),(d,h),(e,a)]:link(x,y)
 for x,y in [(e,f),(f,g),(g,h)]:link(x,y,True)
 # Weld the tangent shared side of the foot/body transition; discard zero-area faces.
 unique={};new=[];remap={}
 for i,v in enumerate(vs):
  key=tuple(round(x,7) for x in v)
  if key not in unique:unique[key]=len(new);new.append(key)
  remap[i]=unique[key]
 vs=new;faces=[]
 for face in fs:
  q=tuple(remap[i] for i in face)
  if len(set(q))<3:continue
  faces.append(q)
 edges=collections.Counter();signed=0;chunks=[]
 for f in faces:
  a,b,c=[vs[i] for i in f];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);length=math.sqrt(sum(x*x for x in n))
  assert length>1e-10,(label,'degenerate')
  for x,y in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:edges[tuple(sorted((x,y)))]+=1
  signed+=sum(a[i]*n[i] for i in range(3))/6
  chunks.append(struct.pack('<12fH',*(x/length for x in n),*a,*b,*c,0))
 assert all(n==2 for n in edges.values()),(label,collections.Counter(edges.values()))
 assert signed>0,(label,signed)
 name=f'{label}_{t:g}mm_upper_mushroom_REPAIRED.stl'
 (r/name).write_bytes(b'QuietMount analytic manifold upper repair'.ljust(80,b' ')+struct.pack('<I',len(chunks))+b''.join(chunks))
 report.append({'file':name,'closed_edges':True,'volume_mm3':signed,'triangles':len(chunks)})
(r/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
