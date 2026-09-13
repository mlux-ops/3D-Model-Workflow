from pathlib import Path
exec((Path(__file__).resolve().parent.parent/'quietmount-v3-screwless/geometry_helpers.py').read_text())
OUT=Path(__file__).resolve().parent
report={}
for t in [12.7,19.05,20,22.225]:
 for kind in ['lower','upper']:
  front=1.5+t+.4
  o=profile(f'{kind}_{t:g}mm', [(-22,0),(0,0),(0,front),(3,front),(3,front+2.4),(-5,front+2.4),(-5,4),(-22,4)])
  # Twelve mm extrusion: lay the broad side on the bed to keep arm fibers continuous.
  for v in o.data.vertices:v.co.x*=2
  bevel(o,.35)
  if kind=='lower':boolean(o,cyl('screw clearance',(0,-14,2),2.2,8),'DIFFERENCE')
  else:
   cutter=cyl('slot',(0,-17,2),2.2,8)
   boolean(cutter,cyl('slot end',(0,-11,2),2.2,8),'UNION')
   add(cutter,(-2.2,-17,-2),(2.2,-11,6))
   boolean(o,cutter,'DIFFERENCE')
  clean(o)
  bm=bmesh.new();bm.from_mesh(o.data)
  report[o.name]={'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_mm3':bm.calc_volume()};bm.free()
  assert report[o.name]['non_manifold_edges']==0 and report[o.name]['volume_mm3']>0
  vs=[Vector((v.co.z,v.co.y,v.co.x+6)) for v in o.data.vertices]
  mn=Vector([min(v[i] for v in vs) for i in range(3)]);vs=[v-mn for v in vs]
  o.data.calc_loop_triangles()
  with (OUT/(o.name+'.stl')).open('wb') as f:
   f.write(b'QuietMount independent clips; mm'.ljust(80,b' '));f.write(struct.pack('<I',len(o.data.loop_triangles)))
   for tri in o.data.loop_triangles:
    a,c,b=[vs[i] for i in tri.vertices];n=(b-a).cross(c-a).normalized()
    f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
  bpy.data.objects.remove(o,do_unlink=True)
(OUT/'geometry_checks.json').write_text(json.dumps(report,indent=2))
print('Eight closed positive-volume clip meshes exported.')
