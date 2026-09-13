"""TwinGrip prototype. Run with Blender 5.x --background --python this_file.
All modeled coordinates and STL coordinates are millimetres.
X = width, Y = up the wall, Z = outward from wall.
"""
import bpy, bmesh, math, json, struct
from mathutils import Vector, Matrix
from pathlib import Path

OUT = Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def box(name, lo, hi):
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple((a+b)/2 for a,b in zip(lo,hi)))
    o=bpy.context.object; o.name=name; o.dimensions=tuple(b-a for a,b in zip(lo,hi))
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return o

def cyl(name, center, radius, depth, axis='Z', vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=center)
    o=bpy.context.object; o.name=name
    if axis=='X': o.rotation_euler[1]=math.pi/2
    if axis=='Y': o.rotation_euler[0]=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    return o

def boolean(a,b,op):
    bpy.context.view_layer.objects.active=a
    m=a.modifiers.new(op,'BOOLEAN'); m.operation=op; m.solver='EXACT'; m.object=b
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(b,do_unlink=True)
    return a

def bevel(o, width=.45):
    bpy.context.view_layer.objects.active=o
    m=o.modifiers.new('Edge relief','BEVEL'); m.width=width; m.segments=3
    m.affect='EDGES'
    bpy.ops.object.modifier_apply(modifier=m.name)
    return o

def slot(name, center, r, travel, travel_axis, hole_axis, depth):
    c=list(center); i='XYZ'.index(travel_axis); c[i]-=travel/2
    a=cyl(name,c,r,depth,hole_axis)
    c=list(center); c[i]+=travel/2
    b=cyl('slot end',c,r,depth,hole_axis)
    boolean(a,b,'UNION')
    lo=[v-r for v in center]; hi=[v+r for v in center]
    lo[i]=center[i]-travel/2; hi[i]=center[i]+travel/2
    j='XYZ'.index(hole_axis);lo[j]=center[j]-depth/2;hi[j]=center[j]+depth/2
    boolean(a,box('slot center',lo,hi),'UNION')
    return a

# Wall foot, narrow rear neck, and 16 x 12 mm solid tongue.
base=box('01_wall_peg',(-8,-37,0),(8,-16,6))
boolean(base,box('neck',(-8,-18,0),(8,0,3)),'UNION')
boolean(base,box('tongue',(-8,-12,0),(8,0,25)),'UNION')
bevel(base,.65)
boolean(base,slot('wall screw slot',(0,-26.5,3),2.4,8,'Y','Z',10),'DIFFERENCE')
# Captive cross-bolt travels the entire 12.7 mm thickness range.
boolean(base,slot('depth adjustment',(0,-6,14.55),1.75,12.7,'Z','X',30),'DIFFERENCE')

# Moving hook uses local front contact plane Z=22; shifts during assembly.
hook=box('02_telescoping_hook',(-13,-15.6,0),(13,3.6,25.2))
boolean(hook,box('retaining lip',(-13,2.9,22),(13,8.6,25.2)),'UNION')
bevel(hook,.4)
boolean(hook,box('tongue bore',(-8.2,-12.2,-1),(8.2,.2,22)),'DIFFERENCE')
# Relief lets the cheek walls close the 0.4 mm sliding clearance when tightened.
boolean(hook,box('clamp relief',(-.8,-16,-1),(.8,-12,22)),'DIFFERENCE')
boolean(hook,cyl('M3 clearance',(0,-6,5),1.75,32,'X'),'DIFFERENCE')
# Nut trap 5.8 mm across flats, 2.6 mm deep, 2.2 mm cheek floor.
nut=cyl('M3 nut trap',(11.8,-6,5),5.8/math.sqrt(3),2.8,'X',6)
boolean(hook,nut,'DIFFERENCE')

# Two loose datum blocks behind the sample establish the 12 mm setback.
pad=bevel(box('03_rear_spacer',(-9,-9,0),(9,9,11.5)),1)
parts=[base,hook,pad]

# Collapse sub-micron Boolean seams before tessellation. Mesh topology alone
# does not catch coincident vertices that become zero-area STL triangles.
for o in parts:
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0001)
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(o.data);bm.free();o.data.update()

def mesh_info(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    bm.normal_update()
    info={'vertices':len(bm.verts),'faces':len(bm.faces),
          'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),
          'volume_mm3':bm.calc_volume(signed=True)}
    seen=set(); components=0
    for v in bm.verts:
        if v in seen: continue
        components+=1; stack=[v];seen.add(v)
        while stack:
            for e in stack.pop().link_edges:
                for w in e.verts:
                    if w not in seen:seen.add(w);stack.append(w)
    info['components']=components;bm.free()
    assert info['non_manifold_edges']==0 and info['components']==1 and info['volume_mm3']>0,info
    return info

def export_stl(o, name, rotation):
    # Explicit export avoids Blender scene unit scaling ambiguity.
    vs=[rotation @ (o.matrix_world @ v.co) for v in o.data.vertices]
    mins=Vector(tuple(min(v[i] for v in vs) for i in range(3)))
    vs=[v-mins for v in vs]
    o.data.calc_loop_triangles()
    with (OUT/name).open('wb') as f:
        f.write(b'TwinGrip millimetres; print orientation'.ljust(80,b' '))
        f.write(struct.pack('<I',len(o.data.loop_triangles)))
        for tri in o.data.loop_triangles:
            a,b,c=[vs[i] for i in tri.vertices]; n=(b-a).cross(c-a).normalized()
            f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
    return [round(max(v[i] for v in vs),3) for i in range(3)]

# Peg and hook side faces on the bed; load-bearing L profiles lie in layer planes.
side=Matrix(((0,0,1),(0,-1,0),(1,0,0)))
report={}
for o in parts:
    report[o.name]=mesh_info(o)
    report[o.name]['print_bounds_mm']=export_stl(o,o.name+'.stl',Matrix.Identity(3) if o==pad else side)

# Geometry fit checks use actual boolean intersections, not bounding boxes.
def intersect_volume(a,b):
    clone=a.copy();clone.data=a.data.copy();bpy.context.collection.objects.link(clone)
    temp=b.copy();temp.data=b.data.copy();bpy.context.collection.objects.link(temp)
    boolean(clone,temp,'INTERSECT')
    bm=bmesh.new();bm.from_mesh(clone.data);vol=abs(bm.calc_volume());bm.free()
    bpy.data.objects.remove(clone,do_unlink=True)
    return vol

fits=[]
for thickness in [12.7,16,19.05,22,25.4]:
    front=12+thickness+.5
    hook.location.z += front-22
    bpy.context.view_layer.update()
    sample=box('sample collision check',(-47.625,3.6,12),(47.625,98.85,12+thickness))
    interference=intersect_volume(base,hook)
    sample_interference=intersect_volume(hook,sample)+intersect_volume(base,sample)
    # Blender single-precision mesh booleans leave tiny signed-volume residuals
    # on coincident contact planes; report them, with a 0.02 mm^3 tolerance.
    assert interference<.02 and sample_interference<.02,(thickness,interference,sample_interference)
    fits.append({'thickness_mm':thickness,'base_hook_overlap_volume_mm3':interference,
        'sample_intersection_mm3':sample_interference,'tongue_engagement_mm':round(25-(front-22),3),
        'bolt_center_z_mm':round(front-17,3),'wall_to_front_mm':round(front+3.2,3)})
    bpy.data.objects.remove(sample,do_unlink=True)
    hook.location.z -= front-22
bpy.context.view_layer.update()
report['fit_checks']=fits
(OUT/'geometry_checks.json').write_text(json.dumps(report,indent=2))

def mat(name,col,metal=0,rough=.5):
    m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    return m
plastic=mat('Warm charcoal PETG',(.045,.065,.068),0,.32)
silver=mat('Steel fasteners',(.48,.53,.56),.85,.23)
stone=mat('Sample stone',(.64,.52,.38),0,.8)
wallmat=mat('Warm white wall',(.8,.79,.75),0,.9)
spacermat=mat('Rear spacers',(.22,.25,.25),0,.7)

def duplicate(o,name,rot=None,offset=(0,0,0),material=None):
    p=o.copy();p.data=o.data.copy();bpy.context.collection.objects.link(p);p.name=name
    p.hide_render=False;p.hide_set(False)
    # Bake original local transforms into vertices first.
    p.data.transform(o.matrix_world);p.matrix_world=Matrix.Identity(4)
    if rot:p.data.transform(rot.to_4x4())
    p.location=offset
    if material:p.data.materials.clear();p.data.materials.append(material)
    return p

for p in parts:p.hide_render=True;p.hide_set(True)
flip=Matrix(((-1,0,0),(0,-1,0),(0,0,1)))
front=12+19.05+.5
assembly=[]
for x in [-28,28]:
    for top in [False,True]:
        r=flip if top else Matrix.Identity(3)
        origin=Vector((x,102.95 if top else 0,0))
        assembly.append(duplicate(base,'Upper peg' if top else 'Lower peg',r,origin,plastic))
        h=duplicate(hook,'Adjustable hook',r,origin+Vector((0,0,front-22)),plastic);assembly.append(h)
        # Cross-bolt, head, washer and nut for honest assembled preview.
        c=origin+r@Vector((0,-6,front-17))
        for o in [cyl('M3 bolt',c,1.5,30,'X'),cyl('M3 head',c+r@Vector((-15,0,0)),2.8,3,'X'),
                  cyl('M3 washer',c+r@Vector((-13.4,0,0)),3.5,.8,'X'),
                  cyl('M3 nut',c+r@Vector((11.7,0,0)),5.5/math.sqrt(3),2.4,'X',6)]:
            o.data.materials.append(silver);assembly.append(o)
        c=origin+r@Vector((0,-26.5,6.6))
        o=cyl('Wall screw washer',c,5.2,1.2);o.data.materials.append(silver);assembly.append(o)
        o=cyl('Wall screw head',c+Vector((0,0,1.7)),3.7,2.4);o.data.materials.append(silver);assembly.append(o)

for x in [-26,26]:assembly.append(duplicate(pad,'Rear datum spacer',offset=(x,51,.5),material=spacermat))
sample=bevel(box('95.25 mm square sample',(-47.625,3.6,12),(47.625,98.85,31.05)),.5)
sample.data.materials.append(stone)
# Subtle procedural stone texture; the sample is reference geometry, never STL.
nodes=stone.node_tree.nodes;links=stone.node_tree.links
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=32
noise.inputs['Detail'].default_value=3
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.2;bump.inputs['Distance'].default_value=.18
links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],nodes.get('Principled BSDF').inputs['Normal'])
wall=box('Wall',(-500,-400,-8),(500,500,-.1));wall.data.materials.append(wallmat)

scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=48
scene.cycles.use_denoising=True
scene.world.color=(.55,.55,.55)
scene.render.resolution_x=1350;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
def aim(o,target):
    f=(Vector(target)-o.location).normalized();r=f.cross(Vector((0,1,0))).normalized();u=r.cross(f)
    o.rotation_euler=Matrix((r,u,-f)).transposed().to_euler()
bpy.ops.object.camera_add(location=(155,120,320));camera=bpy.context.object;aim(camera,(0,51,8))
camera.data.type='ORTHO';camera.data.ortho_scale=225;scene.camera=camera
for loc,power,size in [((-130,220,250),1800000,200),((180,70,120),800000,160)]:
    bpy.ops.object.light_add(type='AREA',location=loc);lamp=bpy.context.object;lamp.data.energy=power;lamp.data.shape='DISK';lamp.data.size=size;aim(lamp,(0,50,0))
scene.render.filepath=str(OUT/'assembly-preview.png');bpy.ops.render.render(write_still=True)
# Save editable assembled scene and second view showing real hidden geometry.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'TwinGrip-assembly.blend'))
sample.hide_render=True
scene.render.filepath=str(OUT/'mechanism-preview.png');bpy.ops.render.render(write_still=True)
print('GEOMETRY_CHECKS',json.dumps(report))
