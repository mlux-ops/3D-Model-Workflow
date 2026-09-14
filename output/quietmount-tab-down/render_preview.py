import bpy
from pathlib import Path
from mathutils import Matrix,Vector
r=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for name in ['A_12.7mm_lower_tapered','A_12.7mm_upper_mushroom']:
 bpy.ops.wm.stl_import(filepath=str(r/(name+'.stl')));bpy.context.object.name=name
bodyrot=Matrix.Identity(4)
for o in list(bpy.data.objects):
 if o.name not in ['A_12.7mm_lower_tapered','A_12.7mm_upper_mushroom']:bpy.data.objects.remove(o,do_unlink=True)
for j,o in enumerate(list(bpy.data.objects)):
 o.data.transform(bodyrot);o.matrix_world=Matrix.Identity(4)
 mn=min(v.co.z for v in o.data.vertices);o.location=Vector((j*40,0,-mn))
 m=bpy.data.materials.new('PolyTerra muted green');m.diffuse_color=(.24,.43,.34,1);o.data.materials.append(m)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
scene.world.color=(.65,.65,.65);scene.view_settings.view_transform='AgX'
scene.render.resolution_x=1200;scene.render.resolution_y=750;scene.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(55,-75,65));cam=bpy.context.object;cam.rotation_euler=(Vector((18,4,7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=76;scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(5,-25,65));bpy.context.object.data.energy=90000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=50
scene.render.filepath=str(r/'tab-down-preview.png');bpy.ops.render.render(write_still=True)
