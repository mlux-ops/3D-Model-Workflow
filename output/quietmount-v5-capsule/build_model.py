"""Capsule saddle. Blender 5.x; dimensions in mm. X across, Y up, Z out of wall."""
from pathlib import Path
exec((Path(__file__).resolve().parent.parent/'quietmount-v3-screwless/geometry_helpers.py').read_text())
OUT=Path(__file__).resolve().parent
BACK=1.2; HEIGHT=95.25; GAP=.35; TOP_GAP=1.2
TS=[12.7,19.05,20,22.225]
parts={}; report={}
base_clean=clean
def clean(o):
 base_clean(o)
 bm=bmesh.new();bm.from_mesh(o.data)
 # Boolean/bevel cleanup may leave zero-area wire remnants; no faces are removed.
 loose=[e for e in bm.edges if not e.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='EDGES')
 loose=[v for v in bm.verts if not v.link_edges]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 bm.to_mesh(o.data);bm.free();o.data.update()

def duplicate(o,name):
 p=o.copy();p.data=o.data.copy();bpy.context.collection.objects.link(p);p.name=name
 p.data.transform(o.matrix_world);p.matrix_world=Matrix.Identity(4);return p

def capsule(name,width,z0,z1):
 r=6.;c=width/2-r
 o=box(name,(-c,-12,z0),(c,0,z1))
 for x in [-c,c]:boolean(o,cyl('round end',(x,-6,(z0+z1)/2),r,z1-z0,n=96),'UNION')
 # Small flat end provides a stable print face. It removes only 0.5 mm each end.
 cut(o,(-50,-30,z0-1),(-width/2+.5,20,z1+1))
 cut(o,(width/2-.5,-30,z0-1),(50,20,z1+1))
 return o

def prism_z(name,points,z0,z1):
 n=len(points);v=[(x,y,z) for z in [z0,z1] for x,y in points]
 f=[tuple(reversed(range(n))),tuple(range(n,2*n))]
 f.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.update()
 o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);clean(o);return o

def bore(o,r,z0,z1):
 # Circular clearance plus a 45-degree roof in the print direction (+X).
 boolean(o,cyl('round screw bore',(0,-6,(z0+z1)/2),r,z1-z0,n=80),'DIFFERENCE')
 d=r/math.sqrt(2)
 boolean(o,prism_z('self-supporting bore roof',[(d,-6-d),(r*math.sqrt(2),-6),(d,-6+d)],z0,z1),'DIFFERENCE')

for t in TS:
 F=BACK+t+GAP;L=F+2.2
 for kind,width,lipw,liph in [('lower',30,10,2.6),('upper',14,10,3.8)]:
  o=capsule(f'{kind}_{t:g}mm',width,0,L)
  # Rounded bevel follows a 45-degree outline so the lip grows from the body
  # in the side-print direction instead of beginning as an unsupported island.
  a=lipw/2
  boolean(o,prism_z('retaining lip',[(-a,-2),(a,-2),(a,0),(a-liph,liph),(-a+liph,liph),(-a,0)],F,L),'UNION')
  bevel(o,.2)
  bore(o,2.2,-1,L+1)
  bore(o,4,L-6.5,L+1)
  clean(o);parts[o.name]=o

def cover(kind,diameter=8.1,suffix=''):
 width=30 if kind=='lower' else 14
 o=capsule(kind+'_cover'+suffix,width,.2,1.6);bevel(o,.15)
 # Four short, split tapered petals retain the cosmetic cover in the head recess.
 bpy.ops.mesh.primitive_cone_add(vertices=96,radius1=3.84,radius2=diameter/2,depth=3.1,location=(0,-6,-1.25))
 ring=bpy.context.object
 boolean(ring,cyl('hollow plug',(0,-6,-1.25),3.08,5,n=96),'DIFFERENCE')
 cut(ring,(-.45,-12,-3.2),(.45,0,.4))
 cut(ring,(-6,-6.45,-3.2),(6,-5.55,.4))
 boolean(o,ring,'UNION')
 # Hidden fingernail purchase underneath the visible capsule face.
 cut(o,(-2.3,-13,-.5),(2.3,-11.35,.65))
 clean(o);parts[o.name]=o;return o

lowercap=cover('lower');uppercap=cover('upper')
cover('lower',8.0,'_easy');cover('lower',8.2,'_snug')
cover('upper',8.0,'_easy');cover('upper',8.2,'_snug')
# Optional shallow gauge duplicates the real head recess and actual print direction.
g=capsule('cover_fit_gauge',14,0,9);bevel(g,.2);bore(g,2.2,-1,10);bore(g,4,2.5,10);clean(g);parts[g.name]=g

def intersection(a,b):
 aa=duplicate(a,'check A');bb=duplicate(b,'check B');boolean(aa,bb,'INTERSECT')
 bm=bmesh.new();bm.from_mesh(aa.data);v=abs(bm.calc_volume());bm.free()
 bpy.data.objects.remove(aa,do_unlink=True);return v

def mesh_info(o):
 bm=bmesh.new();bm.from_mesh(o.data)
 v={'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_mm3':bm.calc_volume()}
 if v['non_manifold_edges']:print('EDGE DETAIL',o.name,[(len(e.link_faces),[tuple(p.co) for p in e.verts]) for e in bm.edges if not e.is_manifold],flush=True)
 bm.free()
 assert v['non_manifold_edges']==0 and v['volume_mm3']>0,(o.name,v)
 return v

def export(o,rotation):
 vs=[rotation@(o.matrix_world@v.co) for v in o.data.vertices]
 mn=Vector([min(v[i] for v in vs) for i in range(3)]);vs=[v-mn for v in vs]
 o.data.calc_loop_triangles()
 with (OUT/(o.name+'.stl')).open('wb') as f:
  f.write(b'QuietMount Capsule; mm; preoriented'.ljust(80,b' '));f.write(struct.pack('<I',len(o.data.loop_triangles)))
  for tri in o.data.loop_triangles:
   a,b,c=[vs[i] for i in tri.vertices];n=(b-a).cross(c-a).normalized()
   f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
 return [max(v[i] for v in vs) for i in range(3)]

bodyrot=Matrix(((0,0,1),(0,-1,0),(1,0,0)))
caprot=Matrix(((1,0,0),(0,-1,0),(0,0,-1)))
for name,o in parts.items():
 bm=bmesh.new();bm.from_mesh(o.data)
 bmesh.ops.dissolve_limit(bm,angle_limit=.0005,use_dissolve_boundaries=False,verts=list(bm.verts),edges=list(bm.edges))
 bm.to_mesh(o.data);bm.free()
 clean(o);report[name]=mesh_info(o)
 report[name]['print_dimensions_mm']=export(o,caprot if 'cover' in name and name!='cover_fit_gauge' else bodyrot)

checks=[]
for t in TS:
 F=BACK+t+GAP;L=F+2.2
 lower=parts[f'lower_{t:g}mm'];upper=duplicate(parts[f'upper_{t:g}mm'],'installed upper')
 # Invert in the wall plane, preserving outward Z.
 upper.matrix_world=Matrix.Translation((0,HEIGHT+TOP_GAP,0))@Matrix.Rotation(math.pi,4,'Z')
 sample=box('sample',(-47.625,0,BACK),(47.625,HEIGHT,BACK+t))
 bpy.context.view_layer.update()
 c={'thickness_mm':t,'sample_lower_intersection_mm3':intersection(sample,lower),'sample_upper_intersection_mm3':intersection(sample,upper)}
 assert c['sample_lower_intersection_mm3']<.001 and c['sample_upper_intersection_mm3']<.001,c
 # The entire top keeper can pivot away from the square after loosening its screw.
 pivot=Vector((0,HEIGHT+TOP_GAP+6,0));original=upper.matrix_world.copy()
 c['release_sweep_sample_intersection_mm3']=[]
 for angle in [0,15,30,45,60,75,90]:
  upper.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(angle),4,'Z')@Matrix.Translation(-pivot)@original
  bpy.context.view_layer.update();v=intersection(sample,upper)
  assert v<.001,(t,angle,v)
  c['release_sweep_sample_intersection_mm3'].append(v)
 c['rotated_keeper_min_y_mm']=min((upper.matrix_world@v.co).y for v in upper.data.vertices)
 assert c['rotated_keeper_min_y_mm']>HEIGHT+.3,c
 # Validate hardware envelope and keep cover petals clear of the actual screw head.
 shaft=cyl('screw shaft envelope',(0,-6,(L-6.5-25)/2),1.75,L-6.5+25)
 head=cyl('screw head envelope',(0,-6,L-6.5+1.4),3.75,2.8)
 c['lower_screw_intersection_mm3']=intersection(lower,shaft)+intersection(lower,head)
 c['upper_screw_intersection_mm3']=intersection(parts[f'upper_{t:g}mm'],shaft)+intersection(parts[f'upper_{t:g}mm'],head)
 assert max(c['lower_screw_intersection_mm3'],c['upper_screw_intersection_mm3'])<.001,c
 for kind,cap in [('lower',lowercap),('upper',uppercap)]:
  p=duplicate(cap,'fitted cap');p.location.z=L;bpy.context.view_layer.update()
  c[kind+'_cap_screw_clearance_intersection_mm3']=intersection(p,head)
  assert c[kind+'_cap_screw_clearance_intersection_mm3']<.001,c
  c[kind+'_intentional_petals_interference_mm3']=intersection(p,parts[f'{kind}_{t:g}mm'])
  assert c[kind+'_intentional_petals_interference_mm3']<1,c
  bpy.data.objects.remove(p,do_unlink=True)
 c['front_clearance_mm']=GAP;c['upper_front_overlap_mm']=3.8-TOP_GAP
 checks.append(c)
 for o in [sample,upper,shaft,head]:bpy.data.objects.remove(o,do_unlink=True)
report['assembly_checks']=checks
(OUT/'geometry_checks.json').write_text(json.dumps(report,indent=2))
import sys
if '--geometry-only' in sys.argv:
 print('Geometry and assembly checks passed.');sys.exit(0)

# Render the actual geometry; render-only sample is tinted transparent glass.
def mat(name,color,rough=.4):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 return m
plastic=mat('Matte warm grey',(.30,.29,.26),.55);wallmat=mat('Warm painted wall',(.78,.76,.70),.85)
glass=mat('Transparent sample illustration',(.65,.80,.76),.08)
glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=1
glass.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.46
for o in parts.values():o.hide_render=True
L=BACK+20+GAP+2.2
assembled=[]
for kind,cap in [('lower',lowercap),('upper',uppercap)]:
 b=duplicate(parts[f'{kind}_20mm'],kind+' assembled');c=duplicate(cap,kind+' cap assembled');c.location.z=L
 if kind=='upper':
  tr=Matrix.Translation((0,HEIGHT+TOP_GAP,0))@Matrix.Rotation(math.pi,4,'Z')
  b.matrix_world=tr;c.matrix_world=tr@Matrix.Translation((0,0,L))
 for o in [b,c]:o.hide_render=False;o.data.materials.append(plastic);assembled.append(o)
s=bevel(box('Illustrative transparent sample',(-47.625,0,BACK),(47.625,HEIGHT,BACK+20)),.3);s.data.materials.append(glass)
w=box('Wall',(-500,-400,-5),(500,500,0));w.data.materials.append(wallmat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.world.color=(.5,.5,.5);scene.view_settings.view_transform='AgX'
scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
def aim(o,target):
 f=(Vector(target)-o.location).normalized();r=f.cross(Vector((0,1,0))).normalized();u=r.cross(f)
 o.rotation_euler=Matrix((r,u,-f)).transposed().to_euler()
bpy.ops.object.camera_add(location=(70,85,330));cam=bpy.context.object;aim(cam,(0,46,8));cam.data.type='ORTHO';cam.data.ortho_scale=145;scene.camera=cam
for loc,power,size in [((-120,240,250),1500000,210),((200,45,120),600000,160)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;aim(o,(0,45,8))
scene.render.filepath=str(OUT/'capsule-installed.png');bpy.ops.render.render(write_still=True)
s.hide_render=True
for o in assembled:
 if 'cap assembled' in o.name:o.location.z+=16
scene.render.filepath=str(OUT/'capsule-covers-removed.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'QuietMount_Capsule.blend'))
print('Capsule meshes, sample fit, keeper release and hardware envelopes checked.')
