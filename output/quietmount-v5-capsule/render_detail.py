import bpy,math
from pathlib import Path
from mathutils import Vector,Matrix
r=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(r/'QuietMount_Capsule.blend'))
for o in bpy.data.objects:
 if 'upper' in o.name:o.hide_render=True
cap=bpy.data.objects['lower cap assembled'];cap.location.x=38;cap.location.z=31.75
L=23.75
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=3.5,depth=2.6,location=(0,-6,L-6.5+1.3))
head=bpy.context.object;head.name='Illustrative screw head'
for dims in [(4.5,1.2,1),(1.2,4.5,1)]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-6,L-6.5+2.5));c=bpy.context.object;c.dimensions=dims
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bpy.context.view_layer.objects.active=head;m=head.modifiers.new('Drive recess','BOOLEAN');m.operation='DIFFERENCE';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
metal=bpy.data.materials.new('Screw metal');metal.use_nodes=True;p=metal.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.06,.06,.06,1);p.inputs['Metallic'].default_value=.8;p.inputs['Roughness'].default_value=.35;head.data.materials.append(metal)
scene=bpy.context.scene;cam=scene.camera;cam.location=(80,35,140);target=Vector((18,-4,17))
f=(target-cam.location).normalized();rr=f.cross(Vector((0,1,0))).normalized();u=rr.cross(f);cam.rotation_euler=Matrix((rr,u,-f)).transposed().to_euler();cam.data.ortho_scale=75
scene.render.resolution_x=1200;scene.render.resolution_y=650;scene.cycles.samples=24
scene.render.filepath=str(r/'capsule-mechanism.png');bpy.ops.render.render(write_still=True)
