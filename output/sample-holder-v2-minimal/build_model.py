"""QuietMount v2: fixed-height concealed frame, interchangeable depth clips.
Blender 5.x --background --python build_model.py. All STL coordinates are mm.
X=across wall, Y=up wall, Z=outward. Sample bottom Y=0, rear Z=10.5.
"""
import bpy,bmesh,math,struct,json
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(__file__).resolve().parent
THICKNESSES=[12.7,15.875,19.05,22.225,25.4] # Add measured thicknesses here and regenerate.
SAMPLE_HEIGHT=95.25
BACK=10.5
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def box(name,lo,hi):
    bpy.ops.mesh.primitive_cube_add(size=1,location=tuple((a+b)/2 for a,b in zip(lo,hi)))
    o=bpy.context.object;o.name=name;o.dimensions=tuple(b-a for a,b in zip(lo,hi))
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def cyl(name,c,r,d,axis='Z',n=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=d,location=c)
    o=bpy.context.object;o.name=name
    if axis=='X':o.rotation_euler[1]=math.pi/2
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);return o
def boolean(a,b,operation):
    bpy.context.view_layer.objects.active=a;m=a.modifiers.new(operation,'BOOLEAN')
    m.operation=operation;m.solver='EXACT';m.object=b;bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(b,do_unlink=True);return a
def add(a,lo,hi):return boolean(a,box('joined solid',lo,hi),'UNION')
def cut(a,lo,hi):return boolean(a,box('cutout',lo,hi),'DIFFERENCE')
def bevel(o,w=.25):
    bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Edge relief','BEVEL')
    m.width=w;m.segments=3;bpy.ops.object.modifier_apply(modifier=m.name);return o
def profile(name,points):
    n=len(points);verts=[(x,y,z) for x in [-3,3] for y,z in points]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    return o
def clean(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0001)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
def countersink(o,x,y):
    boolean(o,cyl('M2.5 shank',(x,y,6),1.4,12),'DIFFERENCE')
    # Extend the cutter past both mating surfaces; avoid coincident cone/cylinder rims.
    bpy.ops.mesh.primitive_cone_add(vertices=64,radius1=1.2,radius2=3,depth=1.8,location=(x,y,7.3))
    boolean(o,bpy.context.object,'DIFFERENCE')

# Two wall screws, four rear-captive M2.5 nuts, and an integral T guide.
frame=box('01_concealed_frame',(-6,5,0),(6,88,4))
add(frame,(-33,3,0),(33,20,4))
add(frame,(-26,33,0),(26,44,4))
add(frame,(-20,70,0),(20,76,4))
add(frame,(-5,50,3),(5,88,6.5))
add(frame,(-8,50,4),(8,88,6.5))
# Carriage stop is independent of screw position: height is fixed.
add(frame,(-11,73,0),(11,76,9.5))
add(frame,(12,70,3.1),(20,76,9.9))
for x in [-16,16]:add(frame,(x-4,7,3.5),(x+4,18,BACK))
add(frame,(-20,70,3.5),(-12,76,BACK))
bevel(frame,.25)
for x in [-20,20]:boolean(frame,cyl('Wall fixing',(x,38.5,3),2.4,10),'DIFFERENCE')
for x in [-28,28]:
    for y in [7,16]:
        boolean(frame,cyl('M2.5 clearance',(x,y,2),1.4,8),'DIFFERENCE')
        boolean(frame,cyl('M2.5 nut trap',(x,y,1),5.3/math.sqrt(3),2.4,n=6),'DIFFERENCE')
boolean(frame,cyl('Retainer screw',(16,73,6.5),1.7,12,'Y'),'DIFFERENCE')
boolean(frame,cyl('M3 nut seat',(16,74.8,6.5),5.8/math.sqrt(3),2.8,'Y',6),'DIFFERENCE')

# Universal top carriage: drop to hard stop, retain with an accessible screw.
carriage=box('02_top_carriage',(-11,76,.2),(11,95,9.5))
add(carriage,(10,83.5,3.5),(21,89.5,9.5))
bevel(carriage,.2)
cut(carriage,(-6.2,75,-1),(6.2,88.5,4.2))
cut(carriage,(-8.2,75,3.8),(8.2,88.5,6.7))
# Rectangular keyed socket for the small, separately printed top hook.
cut(carriage,(-3.2,88.8,3.3),(3.2,96,8.2))
boolean(carriage,cyl('Top hook cross bolt',(0,92,6),1.7,28,'X'),'DIFFERENCE')
boolean(carriage,cyl('Cross bolt nut trap',(9.9,92,6),5.8/math.sqrt(3),2.6,'X',6),'DIFFERENCE')
boolean(carriage,cyl('Lift retaining screw',(16,86.5,6.5),1.7,12,'Y'),'DIFFERENCE')

parts=[frame,carriage]; sets={}
for t in THICKNESSES:
    tag=f'{t:.2f}mm';front=BACK+t+.3
    lower=profile('lower_'+tag,[(-4.5,4),(20,4),(20,8),(0,8),(0,front),(3,front),(3,front+2),(-4.5,front+2)])
    bevel(lower,.25)
    for y in [7,16]:countersink(lower,0,y)
    upper=profile('upper_'+tag,[(89,3.5),(SAMPLE_HEIGHT+4.3,3.5),
        (SAMPLE_HEIGHT+4.3,front+2),(SAMPLE_HEIGHT-3,front+2),
        (SAMPLE_HEIGHT-3,front),(SAMPLE_HEIGHT+.8,front),(SAMPLE_HEIGHT+.8,8),(89,8)])
    bevel(upper,.2)
    boolean(upper,cyl('M3 cross bolt',(0,92,6),1.7,12,'X'),'DIFFERENCE')
    parts.extend([lower,upper]);sets[t]=(lower,upper)
for o in parts:clean(o)
bpy.context.view_layer.update()

def info(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    d={'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_mm3':bm.calc_volume()}
    bm.free();assert d['non_manifold_edges']==0 and d['volume_mm3']>0,(o.name,d);return d
def stl(o,rotation):
    vs=[rotation@(o.matrix_world@v.co) for v in o.data.vertices]
    m=Vector([min(v[i] for v in vs) for i in range(3)]);vs=[v-m for v in vs]
    o.data.calc_loop_triangles()
    with (OUT/(o.name+'.stl')).open('wb') as f:
        f.write(b'QuietMount v2, mm, print orientation'.ljust(80,b' '));f.write(struct.pack('<I',len(o.data.loop_triangles)))
        for tri in o.data.loop_triangles:
            a,b,c=[vs[i] for i in tri.vertices];n=(b-a).cross(c-a).normalized()
            f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
    return [round(max(v[i] for v in vs),3) for i in range(3)]
side=Matrix(((0,0,1),(0,-1,0),(1,0,0)))
report={}
for o in parts:
    report[o.name]=info(o);report[o.name]['print_dimensions_mm']=stl(o,Matrix.Identity(3) if o==frame else side)

def copy(o,name,shift=(0,0,0)):
    p=o.copy();p.data=o.data.copy();bpy.context.collection.objects.link(p);p.name=name
    p.hide_render=False;p.hide_set(False)
    p.data.transform(o.matrix_world);p.matrix_world=Matrix.Identity(4);p.location=shift;return p
def intersection(a,b):
    a=copy(a,'test A');b=copy(b,'test B');boolean(a,b,'INTERSECT')
    bm=bmesh.new();bm.from_mesh(a.data);v=abs(bm.calc_volume());bm.free();bpy.data.objects.remove(a,do_unlink=True);return v
fits=[]
for t,(lower,upper) in sets.items():
    l=copy(lower,'left lower',(-28,0,0));r=copy(lower,'right lower',(28,0,0))
    sample=box('test sample',(-47.625,0,BACK),(47.625,SAMPLE_HEIGHT,BACK+t))
    bpy.context.view_layer.update()
    checks={}
    for a,b in [(frame,l),(frame,r),(frame,carriage),(carriage,upper),(frame,sample),(l,sample),(r,sample),(upper,sample),(carriage,sample)]:
        checks[a.name+' / '+b.name]=intersection(a,b)
    lifted_carriage=copy(carriage,'Lifted carriage',(0,6,0));lifted_hook=copy(upper,'Lifted hook',(0,6,0))
    bpy.context.view_layer.update()
    checks['Opening carriage / frame']=intersection(lifted_carriage,frame)
    checks['Opening hook / sample']=intersection(lifted_hook,sample)
    for o in [lifted_carriage,lifted_hook]:bpy.data.objects.remove(o,do_unlink=True)
    assert max(checks.values())<.04,(t,checks)
    # The upper hook clears the sample by 3 mm after a 6 mm lift.
    assert SAMPLE_HEIGHT-3+6 > SAMPLE_HEIGHT
    fits.append({'thickness_mm':t,'intersections_mm3':checks,'tolerance_mm3':.04,
      'top_clearance_mm':.8,'face_overlap_mm':3,'wall_to_front_mm':round(BACK+t+2.3,3)})
    for o in [l,r,sample]:bpy.data.objects.remove(o,do_unlink=True)
report['assembly_checks']=fits
(OUT/'geometry_checks.json').write_text(json.dumps(report,indent=2))

def material(name,c,metal=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=.45;return m
plastic=material('Warm graphite PETG',(.07,.08,.075));stone=material('Material sample',(.64,.54,.4))
steel=material('Metal hardware',(.5,.52,.54),.8);wallmat=material('Wall',(.8,.79,.76))
for p in parts:p.hide_render=True;p.hide_set(True)
assembly=[copy(frame,'Concealed wall frame'),copy(carriage,'Top loading carriage')]
lo,up=sets[19.05]
assembly.extend([copy(lo,'Lower left',(-28,0,0)),copy(lo,'Lower right',(28,0,0)),copy(up,'Top tab')])
for o in assembly:o.data.materials.clear();o.data.materials.append(plastic)
for x in [-28,28]:
    for y in [7,16]:
        o=cyl('M2.5 flat screw head',(x,y,7.5),2.5,1);o.data.materials.append(steel)
for x in [-20,20]:
    for o in [cyl('Wall screw washer',(x,38.5,4.4),4.5,.8),cyl('Wall screw head',(x,38.5,5.7),3,2)]:o.data.materials.append(steel)
for o in [cyl('Top cross bolt',(0,92,6),1.5,25,'X'),cyl('Cross bolt head',(-12.5,92,6),2.8,3,'X'),
          cyl('Cross bolt nut',(9.9,92,6),5.5/math.sqrt(3),2.4,'X',6),
          cyl('Retainer screw',(16,77,6.5),1.5,25,'Y'),cyl('Retainer head',(16,91,6.5),2.8,3,'Y')]:o.data.materials.append(steel)
sample=bevel(box('Reference sample',(-47.625,0,BACK),(47.625,SAMPLE_HEIGHT,BACK+19.05)),.35)
sample.data.materials.append(stone)
wall=box('Wall',(-500,-400,-8),(500,500,-.1));wall.data.materials.append(wallmat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.world.color=(.5,.5,.5);scene.view_settings.view_transform='AgX'
scene.render.resolution_x=1350;scene.render.resolution_y=1250;scene.render.resolution_percentage=100
def aim(o,target):
    f=(Vector(target)-o.location).normalized();r=f.cross(Vector((0,1,0))).normalized();u=r.cross(f)
    o.rotation_euler=Matrix((r,u,-f)).transposed().to_euler()
bpy.ops.object.camera_add(location=(90,85,360));camera=bpy.context.object;aim(camera,(0,47,12))
camera.data.type='ORTHO';camera.data.ortho_scale=135;scene.camera=camera
for loc,power,size in [((-130,220,250),1700000,200),((180,70,120),650000,160)]:
    bpy.ops.object.light_add(type='AREA',location=loc);lamp=bpy.context.object;lamp.data.energy=power;lamp.data.size=size;aim(lamp,(0,45,0))
scene.render.filepath=str(OUT/'minimal-preview.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'QuietMount-assembly.blend'))
sample.hide_render=True
scene.render.filepath=str(OUT/'concealed-mechanism.png');bpy.ops.render.render(write_still=True)
print('CHECKS',json.dumps(report))
