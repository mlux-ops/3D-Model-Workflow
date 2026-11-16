"""Swap only the placed terrain to a new bare-earth copy; preserve original mesh."""
import json
from pathlib import Path
import unreal
import wieland_site as ws
import wieland_p17 as p17

def apply():
    actor=next(a for a in ws.actors() if a.get_actor_label()=='P17G_Terrain')
    component=actor.static_mesh_component
    original=component.static_mesh
    mats=[component.get_material(i) for i in range(component.get_num_materials())]
    path='/Game/Wieland1529/Surroundings/NearbyDetail/NeighbourMeshes/SM_Nearby_Ground_DTM'
    data=json.loads(Path('E:/Wieland1529_site_data/phase20/nearby_detail/ground/Nearby_Ground_DTM.json').read_text())
    if unreal.EditorAssetLibrary.does_asset_exist(path):mesh=unreal.load_asset(path)
    else:
        dynamic=p17._make_mesh(data)
        opts=unreal.GeometryScriptCreateNewStaticMeshAssetOptions();opts.enable_nanite=True
        settings=unreal.MeshNaniteSettings();settings.enabled=True;opts.nanite_settings=settings
        opts.enable_collision=False;opts.enable_recompute_normals=False
        mesh,result=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dynamic,path,opts)
        if mesh is None:raise RuntimeError(str(result))
    for i,mat in enumerate(mats):mesh.set_material(i,mat)
    if not unreal.EditorAssetLibrary.save_loaded_asset(mesh,False):raise RuntimeError('Ground mesh save failed')
    component.modify();component.set_static_mesh(mesh)
    if component.get_editor_property('cast_shadow'):raise RuntimeError('Ground must retain shadow casting off')
    record={'actor':actor.get_path_name(),'old_asset':original.get_path_name(),'new_asset':mesh.get_path_name(),'triangles':mesh.get_static_mesh_description(0).get_triangle_count(),'shadow_casting':False}
    (Path(__file__).resolve().parent.parent/'review/phase20/nearby_detail/ground_native_swap.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    if not unreal.EditorLoadingAndSavingUtils.save_packages([actor.get_outermost()],True):raise RuntimeError('Ground level save failed')
    return record
