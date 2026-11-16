"""New native street copies, separate from preserved near-site works."""
import asyncio
import json
from pathlib import Path
import unreal
import wieland_p17 as p17
import wieland_site as ws
import wieland_parents as wp

DATA=Path('E:/Wieland1529_site_data/phase20/nearby_detail/streets')
OUT=Path(__file__).resolve().parent.parent/'review/phase20/nearby_detail'
ROOT='/Game/Wieland1529/Surroundings/NearbyDetail/Streets'
TASK=None
STATE={}

def materials():
    mask=ROOT+'/T_NS_AllWalk'
    if not unreal.EditorAssetLibrary.does_asset_exist(mask):
        wp.import_textures([[str(DATA/'T_NS_AllWalk.png'),ROOT,'T_NS_AllWalk','mask']])
    walkpath=ROOT+'/MI_NS_Sidewalk'
    walk=unreal.load_asset(walkpath) if unreal.EditorAssetLibrary.does_asset_exist(walkpath) else unreal.EditorAssetLibrary.duplicate_asset('/Game/Wieland1529/Site/Materials/MI_W1529_SiteGround',walkpath)
    if not unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(walk,'CoverMap',unreal.load_asset(mask)):raise RuntimeError('CoverMap missing')
    unreal.MaterialEditingLibrary.update_material_instance(walk)
    unreal.EditorAssetLibrary.save_loaded_asset(walk,False)
    return [unreal.load_asset('/Game/Wieland1529/Site/Materials/MI_W1529_SiteRoad'),walk,unreal.load_asset('/Game/Wieland1529/Site/Materials/MI_W1529_SiteKerb')]

async def run(names):
    if ws.world_path()!='/Game/Wieland1529/L_Site_M4':raise RuntimeError('Wrong world')
    editor=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not editor.set_current_level_by_name('L_Nearby_Detail'):raise RuntimeError('Detail level missing')
    mats=materials();await asyncio.sleep(0)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    existing={a.get_actor_label():a for a in ws.actors()};rows=[]
    try:
        for name in names:
            d=json.loads((DATA/(name+'.json')).read_text(encoding='utf-8'))
            if len(d['pivot'])!=3:raise RuntimeError('Unnormalized pivot '+name)
            path=ROOT+'/'+name
            if unreal.EditorAssetLibrary.does_asset_exist(path):sm=unreal.load_asset(path)
            else:
                mesh=p17._make_mesh(d)
                opts=unreal.GeometryScriptCreateNewStaticMeshAssetOptions();opts.enable_nanite=True
                settings=unreal.MeshNaniteSettings();settings.enabled=True;opts.nanite_settings=settings
                opts.enable_collision=False;opts.enable_recompute_normals=False
                sm,result=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh,path,opts)
                if sm is None:raise RuntimeError(str(result))
            for slot,mat in enumerate(mats):sm.set_material(slot,mat)
            actor=existing.get(name) or actors.spawn_actor_from_object(sm,unreal.Vector(*d['pivot']),unreal.Rotator())
            actor.set_actor_label(name);actor.set_folder_path('NearbyDetail/Streets')
            actor.tags=['W1529.NearbyStreet','W1529.InferredStreetWidth']
            actor.static_mesh_component.set_visibility(True,False)
            actual=sm.get_static_mesh_description(0).get_triangle_count()
            if actual!=len(d['triangles']):raise RuntimeError('Triangle mismatch '+name)
            if not unreal.EditorAssetLibrary.save_loaded_asset(sm,False):raise RuntimeError('Save failed '+name)
            rows.append({'name':name,'asset':sm.get_path_name(),'triangles':actual})
            STATE['completed']=len(rows)
            await asyncio.sleep(0)
        package=next(a.get_outermost() for a in ws.actors() if ws.level_of(a)=='/Game/Wieland1529/Surroundings/L_Nearby_Detail')
        if not unreal.EditorLoadingAndSavingUtils.save_packages([package],True):raise RuntimeError('Level save failed')
        (OUT/'street_native_records.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
        STATE.update(active=False,result={'count':len(rows)})
    finally:editor.set_current_level_by_name('L_Site_M4')

def start(names):
    global TASK
    if STATE.get('active'):raise RuntimeError('Already running')
    STATE.clear();STATE.update(active=True,completed=0,total=len(names))
    TASK=asyncio.create_task(run(names));return dict(STATE)

def status():
    if TASK is not None and TASK.done() and TASK.exception():STATE.update(active=False,error=repr(TASK.exception()))
    return dict(STATE)
