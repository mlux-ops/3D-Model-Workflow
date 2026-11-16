"""Repair the copied north neighbour's stretched roof using a new world-mapped MI."""
import json
from pathlib import Path
import unreal
import wieland_site as ws

OUT=Path(__file__).resolve().parent.parent/'review/phase20/nearby_detail/neighbours'
FOLDER='/Game/Wieland1529/Surroundings/NearbyDetail/Materials'
NAME='MI_Neighbour1533_Roof'

def roof_parent():
    path=FOLDER+'/M_Nearby_RoofXY'
    parent=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else unreal.EditorAssetLibrary.duplicate_asset('/Game/Wieland1529/Materials/Parents/M_W1529_Opaque',path)
    if parent is None:raise RuntimeError('Roof parent copy failed')
    expressions=unreal.MaterialEditingLibrary.get_material_expressions(parent)
    node=next(x for x in expressions if isinstance(x,unreal.MaterialExpressionCustom) and str(x.get_editor_property('description'))=='World mapping in metres')
    node.set_editor_property('code','float yaw=YawDeg*0.01745329; float c=cos(yaw),s=sin(yaw); float2 uv=float2(WP.x*c+WP.y*s,-WP.y*c+WP.x*s)*0.01; return Swap>0.5?uv.yx:uv;')
    unreal.MaterialEditingLibrary.recompile_material(parent)
    if not unreal.EditorAssetLibrary.save_loaded_asset(parent,False):raise RuntimeError('Roof parent save failed')
    return parent

def apply():
    if ws.world_path()!='/Game/Wieland1529/L_Site_M4':raise RuntimeError('Wrong working level')
    actor=next(a for a in ws.actors() if a.get_actor_label()=='R15_PART_opaque_xm05_yp01_part01')
    if ws.level_of(actor)!=ws.R15_LEVEL:raise RuntimeError('Not the copied surroundings level')
    comp=actor.static_mesh_component
    before=[comp.get_material(i).get_path_name() if comp.get_material(i) else None for i in range(comp.get_num_materials())]
    snapshot=OUT/'roof_material_before.json'
    if not snapshot.exists():snapshot.write_text(json.dumps({'actor':actor.get_path_name(),'materials':before},indent=2),encoding='utf-8')
    path=FOLDER+'/'+NAME
    mi=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().create_asset(NAME,FOLDER,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    mel=unreal.MaterialEditingLibrary
    mel.set_material_instance_parent(mi,roof_parent())
    textures={'BaseColorMap':'/Game/Wieland/R15_Materials/PolyHaven/asphalt_03/T_R15_asphalt_03_BaseColor',
              'NormalMap':'/Game/Wieland/R15_Materials/PolyHaven/asphalt_03/T_R15_asphalt_03_Normal',
              'RoughnessMap':'/Game/Wieland1529/Materials/Textures/T_W1529_WhiteLinear'}
    scalars={'SizeU_m':2.0,'SizeV_m':2.0,'WorldYawDeg':1.18,'RoughnessScale':.82,
             'MacroVariation':.035,'VariationSize_m':4.0,'NormalStrength':.4,'Metallic':0.0,'Specular':.25}
    for key,value in textures.items():
        tex=unreal.load_asset(value)
        if tex is None or not mel.set_material_instance_texture_parameter_value(mi,key,tex):raise RuntimeError('Texture '+key)
    for key,value in scalars.items():
        if not mel.set_material_instance_scalar_parameter_value(mi,key,value):raise RuntimeError('Scalar '+key)
    mel.set_material_instance_vector_parameter_value(mi,'Tint',unreal.LinearColor(.7,.7,.68,1))
    for key,value in {'UseMeshUV':False,'AntiRepeat':True,'Weathering':False}.items():
        mel.set_material_instance_static_switch_parameter_value(mi,key,value,update_material_instance=False)
    mel.update_material_instance(mi)
    if not unreal.EditorAssetLibrary.save_loaded_asset(mi,False):raise RuntimeError('MI save failed')
    comp.modify();comp.set_material(4,mi)
    after=[comp.get_material(i).get_path_name() if comp.get_material(i) else None for i in range(comp.get_num_materials())]
    changed=[i for i,(a,b) in enumerate(zip(before,after)) if a!=b]
    if any(i!=4 for i in changed):raise RuntimeError('Unexpected material slot change')
    result={'actor':actor.get_path_name(),'asset':mi.get_path_name(),'slot':4,'changed_slots':changed,
            'scalars_readback':{k:mel.get_material_instance_scalar_parameter_value(mi,k) for k in scalars},
            'switches_readback':{k:mel.get_material_instance_static_switch_parameter_value(mi,k) for k in ('UseMeshUV','AntiRepeat','Weathering')},
            'geometry_changed':False,'source_assets_changed':False}
    (OUT/'roof_material_fix.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

def save_level():
    actor=next(a for a in ws.actors() if a.get_actor_label()=='R15_PART_opaque_xm05_yp01_part01')
    return bool(unreal.EditorLoadingAndSavingUtils.save_packages([actor.get_outermost()],True))
