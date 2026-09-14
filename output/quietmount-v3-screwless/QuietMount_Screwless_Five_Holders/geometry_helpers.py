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
