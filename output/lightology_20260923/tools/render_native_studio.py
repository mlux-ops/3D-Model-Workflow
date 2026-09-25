"""Studio proof of saved-RFA meshes. No geometry reconstruction or image generation.
The material mapping is a documented approximation between Revit Generic and Cycles.
"""
import bpy,sys,os,json,gzip,math,argparse,traceback
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
parser=argparse.ArgumentParser();parser.add_argument('--only',default='');parser.add_argument('--item',default='');parser.add_argument('--samples',type=int,default=96)
opts=parser.parse_args(args)

def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4

def coords(v,host):return Vector((v[0],-v[2],v[1])) if host=='wall' else Vector((v[0],-v[1],-v[2]))

def look(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def make_mat(key,info):
    m=bpy.data.materials.new(info['name']);m.use_nodes=True;nt=m.node_tree
    shader=nt.nodes.get('Principled BSDF');rgb=info.get('generic_diffuse',info['rgb'])[:3]
    shader.inputs['Base Color'].default_value=tuple(linear(float(c)) for c in rgb)+(1,)
    gloss=float(info.get('generic_glossiness',.3));shader.inputs['Roughness'].default_value=max(.035,(1-gloss)*.7)
    metal=info.get('class')=='Metal';paint=any(x in info['name'].lower() for x in ['black','coal','cord'])
    shader.inputs['Metallic'].default_value=.78 if metal and not paint else .02
    transparency=float(info.get('generic_transparency',info.get('graphics_transparency',0)))
    shader.inputs['Transmission Weight'].default_value=transparency
    shader.inputs['IOR'].default_value=max(1.0,float(info.get('generic_refraction_index',1.5)))
    emission=float(info.get('generic_self_illum_luminance',0))
    ergb=info.get('generic_self_illum_filter_map',rgb)[:3]
    shader.inputs['Emission Color'].default_value=tuple(linear(float(c)) for c in ergb)+(1,)
    shader.inputs['Emission Strength'].default_value=emission/100.
    if info.get('bitmap') and os.path.isfile(info['bitmap']):
        img=nt.nodes.new('ShaderNodeTexImage');img.image=bpy.data.images.load(info['bitmap'],check_existing=True)
        uvnode=nt.nodes.new('ShaderNodeTexCoord')
        img.projection='BOX';img.projection_blend=.1
        nt.links.new(uvnode.outputs['Generated'],img.inputs['Vector'])
        nt.links.new(img.outputs['Color'],shader.inputs['Base Color'])
    if info.get('emission_bitmap') and os.path.isfile(info['emission_bitmap']):
        glow=nt.nodes.new('ShaderNodeTexImage');glow.image=bpy.data.images.load(info['emission_bitmap'],check_existing=True)
        uvnode=nt.nodes.new('ShaderNodeTexCoord')
        glow.projection='BOX';glow.projection_blend=.1
        nt.links.new(uvnode.outputs['Generated'],glow.inputs['Vector'])
        nt.links.new(glow.outputs['Color'],shader.inputs['Emission Color'])
        if info.get('class')=='Stone':
            emitter=nt.nodes.new('ShaderNodeEmission')
            emitter.inputs['Strength'].default_value=2.5
            nt.links.new(glow.outputs['Color'],emitter.inputs['Color'])
            nt.links.new(emitter.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])
    return m

index=json.loads((ROOT/'native_mesh_index.json').read_text())
results=[]
for row in index:
    if not row.get('success') or (opts.only and opts.only not in row['folder']) or (opts.item and opts.item not in row['name']):continue
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        with gzip.open(row['mesh'],'rt',encoding='utf8') as f:data=json.load(f)
        host=row['host'];materials={k:make_mat(k,v) for k,v in data['materials'].items()};objects=[];worldpoints=[]
        for i,part in enumerate(data['parts']):
            vertices=[coords(v,host) for v in part['vertices']]
            mesh=bpy.data.meshes.new('RFA mesh '+str(i));mesh.from_pydata(vertices,[],part['triangles']);mesh.update()
            obj=bpy.data.objects.new('Revit element '+str(part['element'])+' solid '+str(part['solid']),mesh);bpy.context.collection.objects.link(obj);objects.append(obj);worldpoints.extend(vertices)
            keys=list(dict.fromkeys(part['material_ids']))
            for k in keys:mesh.materials.append(materials[k])
            for polygon,k in zip(mesh.polygons,part['material_ids']):polygon.material_index=keys.index(k);polygon.use_smooth=True
            # Source face vertices are already split at native face boundaries.
            # Polygon smoothing within each native face avoids Blender custom-normal crashes.
            uv=mesh.uv_layers.new(name='Revit physical scale')
            for poly in mesh.polygons:
                key=keys[poly.material_index];info=data['materials'][key]
                sx=float(info.get('texture_RealWorldScaleX',1.0))*.3048;sy=float(info.get('texture_RealWorldScaleY',1.0))*.3048
                sx=max(sx,.01);sy=max(sy,.01)
                for li in poly.loop_indices:
                    local=part['vertices'][mesh.loops[li].vertex_index];uv.data[li].uv=(local[0]/sx+.5,local[1]/sy+.5)
            mesh.update()
        minimum=Vector(tuple(min(p[i] for p in worldpoints) for i in range(3)));maximum=Vector(tuple(max(p[i] for p in worldpoints) for i in range(3)))
        center=(minimum+maximum)/2;dimensions=maximum-minimum;span=max(dimensions)
        scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=opts.samples;scene.cycles.use_denoising=True
        scene.cycles.max_bounces=12;scene.cycles.transmission_bounces=12;scene.cycles.transparent_max_bounces=12
        prefs=bpy.context.preferences.addons['cycles'].preferences;device='CPU'
        try:
            prefs.compute_device_type='OPTIX';prefs.get_devices()
            devices=[d for d in prefs.devices if d.type=='OPTIX']
            if devices:
                for d in prefs.devices:d.use=d.type=='OPTIX'
                scene.cycles.device='GPU';device=', '.join(d.name for d in devices)
        except Exception:pass
        world=bpy.data.worlds.new('Neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.8,.8,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45;scene.world=world
        hostmat=bpy.data.materials.new('Neutral host');hostmat.use_nodes=True;hostmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.8,.8,.8,1);hostmat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.85
        bpy.ops.mesh.primitive_plane_add(size=span*12,location=(0,.0005,center.z) if host=='wall' else (0,0,.0005))
        plane=bpy.context.object;plane.name='Studio host, not part of family'
        if host=='wall':plane.rotation_euler=(math.pi/2,0,0)
        plane.data.materials.append(hostmat)
        camdata=bpy.data.cameras.new('Camera');camera=bpy.data.objects.new('Camera',camdata);bpy.context.collection.objects.link(camera)
        offset=Vector((.75,-1.8,.60)) if host=='wall' else Vector((1.0,-1.7,-.80))
        camera.location=center+offset*span;look(camera,center);camdata.type='ORTHO';scene.camera=camera
        inverse=camera.matrix_world.inverted();bpy.context.view_layer.update();inverse=camera.matrix_world.inverted()
        corners=[inverse@Vector((x,y,z)) for x in [minimum.x,maximum.x] for y in [minimum.y,maximum.y] for z in [minimum.z,maximum.z]]
        width=max(p.x for p in corners)-min(p.x for p in corners);height=max(p.y for p in corners)-min(p.y for p in corners)
        aspect=max(.6,min(1.8,width/max(height,.001)));scene.render.resolution_x=1500 if aspect>=1 else int(1500*aspect);scene.render.resolution_y=int(1500/aspect) if aspect>=1 else 1500;scene.render.resolution_percentage=100
        camdata.ortho_scale=(max(width,height*aspect) if aspect>=1 else max(height,width/aspect))*1.18
        def area(name,offset,energy,scale):
            ld=bpy.data.lights.new(name,'AREA');ld.energy=energy*(span/.3)**2;ld.shape='DISK';ld.size=span*scale
            lo=bpy.data.objects.new(name,ld);bpy.context.collection.objects.link(lo);lo.location=center+Vector(offset)*span;look(lo,center)
        if host=='wall':
            area('Large key',(-1.1,-1.9,1.7),30,2.5);area('Soft fill',(1.7,-1.1,.4),16,2.1);area('Top strip',(.2,-.3,2.0),12,1.4)
        else:
            area('Large key',(-1.3,-1.8,-1.3),42,2.7);area('Soft fill',(1.4,.2,-1.0),25,2.5);area('Edge',(0,1.5,-.4),18,1.8)
        scene.view_settings.view_transform='AgX';scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
        target=Path(row['mesh']).parent/(row['name']+'_Studio.png');scene.render.filepath=str(target)
        if row['folder'].startswith('f10'):
            scene.view_settings.exposure=0.0
        material_diag=[]
        for mat in materials.values():
            material_diag.append({'name':mat.name,'nodes':[{'type':n.type,'image':n.image.filepath if n.type=='TEX_IMAGE' and n.image else None,'size':list(n.image.size) if n.type=='TEX_IMAGE' and n.image else None,'pixel_sample':list(n.image.pixels[0:4]) if n.type=='TEX_IMAGE' and n.image else None} for n in mat.node_tree.nodes],'links':[(l.from_node.type,l.from_socket.name,l.to_node.type,l.to_socket.name) for l in mat.node_tree.links]})
        (target.parent/(row['name']+'_StudioMaterials.json')).write_text(json.dumps(material_diag,indent=2))
        diagnostics=[]
        for ob in objects:
            layer=ob.data.uv_layers.active
            diagnostics.append({'object':ob.name,'uv_count':len(layer.data),'uv_min':[min(x.uv[i] for x in layer.data) for i in range(2)],'uv_max':[max(x.uv[i] for x in layer.data) for i in range(2)]})
        (target.parent/(row['name']+'_StudioUV.json')).write_text(json.dumps(diagnostics,indent=2))
        bpy.ops.render.render(write_still=True)
        results.append({'rfa':row['rfa'],'rfa_sha256':row['sha256'],'image':str(target),'renderer':bpy.app.version_string+' Cycles','device':device,'samples':opts.samples,'status':'rendered','method':'actual native RFA mesh and saved appearance inputs; Cycles shader translation approximate; luminous stone shown with its saved luminous-color bitmap under normalized emission'})
    except Exception:results.append({'rfa':row['rfa'],'status':'failed','error':traceback.format_exc()})
    (ROOT/('studio_render_results'+('_'+opts.item if opts.item else ('_'+opts.only if opts.only else ''))+'.json')).write_text(json.dumps(results,indent=2))