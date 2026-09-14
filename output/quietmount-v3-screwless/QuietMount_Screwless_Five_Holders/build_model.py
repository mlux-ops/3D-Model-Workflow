from pathlib import Path
exec((Path(__file__).resolve().parent/'geometry_helpers.py').read_text())
OUT=Path(__file__).resolve().parent
BACK=13.5
THICKNESSES=[12.7,19.05,20,22.225]

wall=box('01_adhesive_wallplate',(-35,6,0),(35,90,3.2))
for x in [-23,23]:add(wall,(x-11,10,-1.6),(x+11,84,.2))
bevel(wall,.25)
for y in [30,65]:
    cut(wall,(-3.75,y-3.25,-2),(3.75,y+13.25,5))
    cut(wall,(-7.3,y+6.75,-2),(7.3,y+13.25,5))

base=box('base',(-8,8,3.5),(8,89,7))
add(base,(-32,6,3.5),(32,17,7))
add(base,(-23,70,3.5),(23,77,7))
for x in [-20,20]:
    add(base,(x-3.5,8,6.5),(x+3.5,14,BACK))
    add(base,(x-3.5,71,6.5),(x+3.5,76,BACK))
for y in [30,65]:
    add(base,(-3.5,y-3,-.2),(3.5,y+3,3.8))
    add(base,(-7,y-3,-1.2),(7,y+3,0))
# Top hook slides on a T rail, with a hard lower stop.
add(base,(-3.5,62,7),(3.5,89,8.7))
add(base,(-6,62,8.5),(6,89,10.2))
add(base,(-10,72,6.5),(10,76,13))
clean(base);bevel(base,.2);clean(base)
cut(base,(-12,80.45,7.15),(12,83.55,10.6));clean(base)
bm=bmesh.new();bm.from_mesh(base.data);print('BASE BAD',sum(not e.is_manifold for e in bm.edges));bm.free()

def duplicate(o,name,shift=(0,0,0)):
    p=o.copy();p.data=o.data.copy();bpy.context.collection.objects.link(p);p.name=name
    p.data.transform(o.matrix_world);p.matrix_world=Matrix.Identity(4);p.location=shift
    return p

frames={};tops={}
def engrave(o,label,y,z,max_width=12):
    bpy.ops.object.text_add(location=(0,y,z-.3))
    txt=bpy.context.object;txt.data.body=label;txt.data.align_x='CENTER';txt.data.size=3.2;txt.data.extrude=.6
    bpy.context.view_layer.update()
    if txt.dimensions.x>max_width:txt.scale.x=max_width/txt.dimensions.x
    bpy.ops.object.convert(target='MESH');boolean(o,bpy.context.object,'DIFFERENCE')
for t in THICKNESSES:
    tag=f'{t:.3f}'.rstrip('0').rstrip('.')
    front=BACK+t+.4
    f=duplicate(base,'frame_'+tag+'mm')
    for x in [-28,28]:
        p=profile('integral lower hook',[(-5.5,3.45),(25,3.45),(25,8),(0,8),
          (0,front),(3,front),(3,front+2.4),(-5.5,front+2.4)])
        p.location.x=x;bevel(p,.25);boolean(f,p,'UNION')
        bm=bmesh.new();bm.from_mesh(f.data);print('UNION BAD',x,sum(not e.is_manifold for e in bm.edges));bm.free()
    frames[t]=f
    engrave(f,tag,42,7)
    top=box('top_'+tag+'mm',(-9.5,76,7.25),(9.5,94.5,13))
    bevel(top,.2)
    cut(top,(-3.75,75,6),(3.75,90,8.95))
    cut(top,(-6.25,75,8.25),(6.25,90,10.45))
    p=profile('top hook',[(89,10.7),(99.55,10.7),(99.55,front+2.4),
        (92.25,front+2.4),(92.25,front),(96.05,front),(96.05,13),(89,13)])
    bevel(p,.2);boolean(top,p,'UNION')
    cut(top,(-12,80.45,7.05),(12,83.55,9.95))
    engrave(top,tag,85,13,14)
    tops[t]=top
bpy.data.objects.remove(base,do_unlink=True)

# An L handle reaches the top edge behind the sample. The final 2 mm of
# insertion wedges gently; the key carries no steady sample weight.
verts=[]
for x,w in [(-9.3,2.7),(5.8,2.9),(10.8,3.3)]:
    verts.extend([(x,82-w/2,7.5),(x,82+w/2,7.5),(x,82+w/2,9.7),(x,82-w/2,9.7)])
faces=[(3,2,1,0),(8,9,10,11)]
for ring in range(2):
    for j in range(4):faces.append((ring*4+j,ring*4+(j+1)%4,(ring+1)*4+(j+1)%4,(ring+1)*4+j))
m=bpy.data.meshes.new('key');m.from_pydata(verts,[],faces);m.update()
key=bpy.data.objects.new('02_locking_key',m);bpy.context.collection.objects.link(key)
add(key,(10,80.4,7.5),(15,94.5,9.7));bevel(key,.15)

parts=[wall,key]+list(frames.values())+list(tops.values())
def info(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    result={'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_mm3':bm.calc_volume()}
    if result['non_manifold_edges']:print('BAD EDGES',o.name,[[tuple(round(v,3) for v in p.co) for p in e.verts] for e in bm.edges if not e.is_manifold])
    bm.free();assert result['non_manifold_edges']==0 and result['volume_mm3']>0,(o.name,result)
    return result
def stl(o,rotation):
    vs=[rotation@(o.matrix_world@v.co) for v in o.data.vertices]
    mn=Vector([min(v[i] for v in vs) for i in range(3)]);vs=[v-mn for v in vs]
    o.data.calc_loop_triangles()
    with (OUT/(o.name+'.stl')).open('wb') as f:
        f.write(b'QuietMount v3 screwless, mm'.ljust(80,b' '));f.write(struct.pack('<I',len(o.data.loop_triangles)))
        for tri in o.data.loop_triangles:
            a,b,c=[vs[i] for i in tri.vertices];n=(b-a).cross(c-a).normalized()
            f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
    return [round(max(v[i] for v in vs),3) for i in range(3)]
report={}
for p in parts:
    bm=bmesh.new();bm.from_mesh(p.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
    bmesh.ops.dissolve_limit(bm,angle_limit=.0005,use_dissolve_boundaries=False,verts=list(bm.verts),edges=list(bm.edges))
    bm.to_mesh(p.data);bm.free()
    clean(p);report[p.name]=info(p)
    rot=Matrix.Identity(3)
    if p==wall:rot=Matrix(((1,0,0),(0,-1,0),(0,0,-1)))
    elif p in tops.values():rot=Matrix(((0,0,1),(0,-1,0),(1,0,0)))
    report[p.name]['print_dimensions_mm']=stl(p,rot)

def intersection(a,b):
    a=duplicate(a,'check A');b=duplicate(b,'check B');boolean(a,b,'INTERSECT')
    bm=bmesh.new();bm.from_mesh(a.data);v=abs(bm.calc_volume());bm.free();bpy.data.objects.remove(a,do_unlink=True)
    return v
checks=[]
for t in THICKNESSES:
    sample=box('test sample',(-47.625,0,BACK),(47.625,95.25,BACK+t))
    f=frames[t];top=tops[t]
    bpy.context.view_layer.update()
    c={}
    for a,b in [(f,wall),(top,f),(top,sample),(f,sample),(key,sample),(key,f)]:
        c[a.name+' / '+b.name]=intersection(a,b)
    assert max(c.values())<.04,(t,c)
    wedge_overlap=intersection(key,top)
    assert wedge_overlap<.3,('intentional key wedge contact',wedge_overlap)
    moved=duplicate(f,'forward frame',(0,0,1));bpy.context.view_layer.update()
    assert intersection(moved,wall)>1,'Wall plate must capture frame against outward pull'
    bpy.data.objects.remove(moved,do_unlink=True)
    moved=duplicate(key,'raised key',(0,2,0));bpy.context.view_layer.update()
    assert intersection(moved,f)>1,'Key must block the top hook from rising'
    bpy.data.objects.remove(moved,do_unlink=True)
    for dy in [2,4,6,10]:
        raised=duplicate(f,'raised frame',(0,dy,0));bpy.context.view_layer.update()
        v=intersection(raised,wall);assert v<.04,('wall insertion',t,dy,v)
        bpy.data.objects.remove(raised,do_unlink=True)
    for dy in [2,4,6,14]:
        raised=duplicate(top,'raised hook',(0,dy,0));bpy.context.view_layer.update()
        v=intersection(raised,f);assert v<.04,('hook lift',t,dy,v)
        bpy.data.objects.remove(raised,do_unlink=True)
    checks.append({'thickness_mm':t,'intersections_mm3':c,'intentional_key_wedge_overlap_mm3':wedge_overlap,
                   'frame_outward_capture':True,'key_blocks_lift':True,'front_clearance_mm':.4,'top_clearance_mm':.8})
    bpy.data.objects.remove(sample,do_unlink=True)
report['assembly_checks']=checks
(OUT/'geometry_checks.json').write_text(json.dumps(report,indent=2))

def material(name,c):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.5
    return m
plastic=material('Graphite PolyTerra',(.045,.055,.05));stone=material('Terrazzo sample',(.65,.58,.46))
wallmat=material('Warm wall',(.8,.79,.76));stripmat=material('Command strip reference',(.92,.92,.88))
for p in parts:p.hide_render=True
assembly=[duplicate(wall,'Wall plate'),duplicate(frames[20],'Frame'),duplicate(tops[20],'Top hook'),duplicate(key,'Lock key')]
for p in assembly:p.hide_render=False;p.data.materials.clear();p.data.materials.append(plastic)
sample=bevel(box('Reference sample',(-47.625,0,BACK),(47.625,95.25,BACK+20)),.35);sample.data.materials.append(stone)
strips=[]
for x in [-23,23]:
    p=box('Medium strip pair reference',(x-9.525,12,-4.5),(x+9.525,81.85,-1.6));p.data.materials.append(stripmat);strips.append(p)
w=box('Wall',(-400,-350,-8),(400,450,-4.5));w.data.materials.append(wallmat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.world.color=(.6,.6,.6);scene.view_settings.view_transform='AgX'
scene.render.resolution_x=1300;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
def aim(o,target):
    f=(Vector(target)-o.location).normalized();r=f.cross(Vector((0,1,0))).normalized();u=r.cross(f)
    o.rotation_euler=Matrix((r,u,-f)).transposed().to_euler()
bpy.ops.object.camera_add(location=(80,90,350));cam=bpy.context.object;aim(cam,(0,47,10));cam.data.type='ORTHO';cam.data.ortho_scale=140;scene.camera=cam
for loc,power,size in [((-130,220,250),1700000,200),((180,70,120),650000,160)]:
    bpy.ops.object.light_add(type='AREA',location=loc);p=bpy.context.object;p.data.energy=power;p.data.size=size;aim(p,(0,45,0))
scene.render.filepath=str(OUT/'installed-preview.png');bpy.ops.render.render(write_still=True)
sample.hide_render=True;scene.render.filepath=str(OUT/'mechanism-preview.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'QuietMount_Screwless.blend'))
print('GEOMETRY VERIFIED',json.dumps(report))
