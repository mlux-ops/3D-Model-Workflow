"""Native staging of measured nearby forms. New assets only, hidden until approved for the final hybrid."""
import asyncio
import json
from pathlib import Path

import unreal
import wieland_p17 as p17
import wieland_site as ws

ROOT='/Game/Wieland1529/Surroundings/NearbyDetail/Meshes/'
LEVEL='/Game/Wieland1529/Surroundings/L_Nearby_Detail'
DATA=Path('E:/Wieland1529_site_data/phase20/nearby_detail/meshes_clean')
DOCS=Path(__file__).resolve().parent.parent
TASK=None
STATE={}


async def batch(names):
    if ws.world_path()!='/Game/Wieland1529/L_Site_M4':raise RuntimeError('Working site level required')
    editor=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not editor.set_current_level_by_name('L_Nearby_Detail'):raise RuntimeError('Cannot select new detail level')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    mesh_sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    existing={a.get_actor_label():a for a in ws.actors()}
    gray=unreal.EditorAssetLibrary.load_asset(p17.MAT_ROOT+'MI_P17_Roof_Grey')
    out=[]
    for name in names:
        d=json.loads((DATA/(name+'.json')).read_text(encoding='utf-8'))
        path=ROOT+name
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            sm=unreal.EditorAssetLibrary.load_asset(path)
        else:
            mesh=p17._make_mesh(d)
            opts=unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
            opts.enable_nanite=True
            nanite=unreal.MeshNaniteSettings();nanite.enabled=True
            opts.nanite_settings=nanite
            opts.enable_collision=False
            opts.enable_recompute_normals=False
            sm,outcome=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh,path,opts)
            if sm is None:raise RuntimeError('Mesh creation failed '+name+' '+str(outcome))
            for slot in range(3):sm.set_material(slot,gray)
        actor=existing.get(name)
        if actor is None:
            actor=actors.spawn_actor_from_object(sm,unreal.Vector(*d['pivot']),unreal.Rotator(0,0,0))
        if actor is None:raise RuntimeError('Actor creation failed '+name)
        actor.set_actor_label(name)
        actor.set_folder_path('NearbyDetail/MeasuredStaging')
        actor.tags=['W1529.NearbyDetail','W1529.County.'+name.removeprefix('ND_')]
        actor.static_mesh_component.set_visibility(False,False)
        desc=sm.get_static_mesh_description(0)
        record={'name':name,'asset':sm.get_path_name(),'actor':actor.get_path_name(),
                'triangles':desc.get_triangle_count(),'expected_triangles':len(d['triangles']),
                'uv_channels':mesh_sub.get_num_uv_channels(sm,0),'nanite':bool(mesh_sub.get_nanite_settings(sm).enabled),
                'visible':bool(actor.static_mesh_component.get_editor_property('visible'))}
        if record['triangles']!=record['expected_triangles'] or record['uv_channels']<1 or not record['nanite']:
            raise RuntimeError('Validation failed '+json.dumps(record))
        if not unreal.EditorAssetLibrary.save_loaded_asset(sm,False):raise RuntimeError('Asset save failed '+name)
        out.append(record)
        STATE['completed']=len(out)
        await asyncio.sleep(0)
    package=next(a.get_outermost() for a in ws.actors() if ws.level_of(a)==LEVEL)
    if not unreal.EditorLoadingAndSavingUtils.save_packages([package],True):raise RuntimeError('Staging level save failed')
    dest=DOCS/'review/phase20/nearby_detail/import_records.jsonl'
    with dest.open('a',encoding='utf-8') as log:
        for r in out:log.write(json.dumps(r)+chr(10))
    editor.set_current_level_by_name('L_Site_M4')
    return out


async def _run(names):
    try:
        result=await batch(names)
        STATE.update(active=False,result={'count':len(result),'records':result[:3]})
    except Exception as exc:STATE.update(active=False,error=repr(exc))


def start(names):
    global TASK
    if STATE.get('active'):raise RuntimeError('Import already active')
    STATE.clear();STATE.update(active=True,total=len(names),completed=0)
    TASK=asyncio.create_task(_run(names))
    return dict(STATE)


def status():return dict(STATE)
