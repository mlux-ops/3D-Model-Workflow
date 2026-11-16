"""Measured clean roof additions on 1525, preserving the detailed main gable."""
import json
from pathlib import Path
import unreal
import wieland_site as ws
import wieland_p17 as p17

def build():
    source=Path('E:/Wieland1529_site_data/phase17/meshes_zone12_clean/P17RZ_781632.json')
    data=json.loads(source.read_text(encoding='utf-8'))
    data['triangles']=data['triangles'][16:]
    data['tri_mat']=data['tri_mat'][16:]
    path='/Game/Wieland1529/Surroundings/NearbyDetail/NeighbourMeshes/SM_Neighbour1525_RoofFeatures'
    if unreal.EditorAssetLibrary.does_asset_exist(path):mesh=unreal.load_asset(path)
    else:
        dynamic=p17._make_mesh(data)
        opts=unreal.GeometryScriptCreateNewStaticMeshAssetOptions();opts.enable_nanite=True
        settings=unreal.MeshNaniteSettings();settings.enabled=True;opts.nanite_settings=settings
        opts.enable_collision=False;opts.enable_recompute_normals=False
        mesh,result=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dynamic,path,opts)
        if mesh is None:raise RuntimeError(str(result))
    mesh.set_material(0,unreal.load_asset('/Game/Wieland1529/Surroundings/NearbyDetail/Materials/MI_NDF_Trim'))
    mesh.set_material(1,unreal.load_asset('/Game/Wieland1529/Surroundings/NearbyDetail/Materials/MI_Neighbour1533_Roof'))
    editor=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    editor.set_current_level_by_name('L_Nearby_Detail')
    actor=next((a for a in ws.actors() if a.get_actor_label()=='Neighbour1525_RoofFeatures'),None)
    if actor is None:actor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_object(mesh,unreal.Vector(*data['pivot']),unreal.Rotator())
    actor.set_actor_label('Neighbour1525_RoofFeatures');actor.tags=['W1529.NeighbourRoofFeatures','W1529.MeasuredRoof','W1529.AssumedRoofFinish']
    actor.set_folder_path('NearbyDetail/Neighbours')
    editor.set_current_level_by_name('L_Site_M4')
    saved=unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
    record={'asset':mesh.get_path_name(),'triangles':mesh.get_static_mesh_description(0).get_triangle_count(),'source':str(source),'source_triangle_range':[16,47],'main_gable_changed':False,'appearance':'Inferred light trim and granular flat-roof finish; measured dimensions retained','saved':bool(saved)}
    out=Path(__file__).resolve().parent.parent/'review/phase20/nearby_detail/neighbours/south_roof_features.json'
    out.write_text(json.dumps(record,indent=2),encoding='utf-8')
    return record
