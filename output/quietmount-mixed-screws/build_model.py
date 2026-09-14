from pathlib import Path
import json
r=Path(__file__).resolve().parent
source=(r.parent/'quietmount-v5-capsule/build_model.py').read_text()
prefix=source.split('for t in TS:')[0]
prefix=prefix.replace("Path(__file__).resolve().parent.parent/'quietmount-v3-screwless/geometry_helpers.py'", "Path(__file__).resolve().parent.parent/'quietmount-v3-screwless/geometry_helpers.py'")
exec(prefix)
covercode=source[source.index('def cover('):source.index("lowercap=cover('lower')")]
covercode=covercode.replace('radius1=3.84','radius1=4.14').replace('3.08,5','3.38,5')
exec(covercode)
exec(source[source.index('def export('):source.index('bodyrot=')])
ts=[12.7,19.05,19.05,20,22.225,20.5,18.5,18,14,17]
inventory=[]
for i,t in enumerate(ts):
 for kind,width,lipw,liph in [('lower',30,10,2.6),('upper',14,10,3.8)]:
  head='tapered' if kind=='lower' and i<9 else 'mushroom'
  name=f'{chr(65+i)}_{t:g}mm_{kind}_{head}'
  F=BACK+t+GAP;L=F+2.2
  o=capsule(name,width,0,L);a=lipw/2
  boolean(o,prism_z('lip',[(-a,-2),(a,-2),(a,0),(a-liph,liph),(-a+liph,liph),(-a,0)],F,L),'UNION')
  bevel(o,.2);bore(o,2.3,-1,L+1)
  if head=='mushroom':
   bore(o,4.3,4,L+1)
  else:
   # Actual measured cone: 8 mm head, 4 mm shaft, 4 mm axial taper.
   # Matching slope with radial clearance: cone meets 4.6 mm shaft bore at z=2.
   bpy.ops.mesh.primitive_cone_add(vertices=96,radius1=2.3,radius2=4.3,depth=4,location=(0,-6,4))
   boolean(o,bpy.context.object,'DIFFERENCE');bore(o,4.3,6,L+1)
  clean(o);parts[name]=o
  inventory.append({'set':chr(65+i),'thickness_mm':t,'kind':kind,'head':head,'file':name+'.stl'})
cover('lower',8.8,'_snug_revised');cover('upper',8.8,'_snug_revised')
bodyrot=Matrix(((0,0,1),(0,-1,0),(1,0,0)));caprot=Matrix(((1,0,0),(0,-1,0),(0,0,-1)))
for name,o in parts.items():
 bm=bmesh.new();bm.from_mesh(o.data)
 bmesh.ops.dissolve_limit(bm,angle_limit=.0005,use_dissolve_boundaries=False,verts=list(bm.verts),edges=list(bm.edges))
 bm.to_mesh(o.data);bm.free();clean(o)
 export(o,caprot if 'cover' in name else bodyrot)
(r/'inventory.json').write_text(json.dumps(inventory,indent=2))
print('Exported 20 bodies and two revised cover masters; extended checks skipped by request.')
