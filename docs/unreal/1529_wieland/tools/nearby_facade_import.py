"""Stage owner-approved presentation facades on measured nearby forms.

Editor-side helper; call start(ids), then poll status(). New assets and the named
staging level only are saved. Activation is separate and reversible. Original
R15 pieces, skyline actors, Datasmith assets and parent materials are untouched.
"""
import asyncio
import csv
import datetime
import json
from pathlib import Path

import unreal
import phase7_massing as palette
import wieland_p17 as p17
import wieland_site as ws

DOCS = Path(__file__).resolve().parent.parent
WORK = Path('E:/Wieland1529_site_data/phase20/nearby_detail')
DATA = WORK / 'meshes_facade'
OUT = DOCS / 'review/phase20/nearby_detail'
ROOT = '/Game/Wieland1529/Surroundings/NearbyDetail/Facades'
MATERIALS = '/Game/Wieland1529/Surroundings/NearbyDetail/Materials'
LEVEL = '/Game/Wieland1529/Surroundings/L_Nearby_Detail'
P17_LEVEL = '/Game/Wieland1529/Surroundings/L_Surroundings_P17'
REPLACEMENT_LEVELS = {P17_LEVEL, '/Game/Wieland1529/Surroundings/L_Skyline_P17'}
PARENT = '/Game/Wieland1529/Surroundings/Materials/M_W1529_Massing'
OPAQUE = '/Game/Wieland1529/Materials/Parents/M_W1529_Opaque'
TEXTURES = '/Game/Wieland1529/Materials/Textures/'
BITUMEN = '/Game/Wieland/R15_Materials/PolyHaven/asphalt_03/T_R15_asphalt_03_'
EXCLUDED = {'781075', '781331'}
TASK = None
STATE = {}
_CACHE = {}


def _ids(values):
    active = {r['bldg_id'] for r in csv.DictReader((WORK / 'active_targets.csv').open(encoding='utf-8'))}
    result = list(dict.fromkeys(str(v).removeprefix('NDF_').removeprefix('ND_') for v in values))
    bad = set(result) - active
    if bad or set(result) & EXCLUDED:
        raise RuntimeError('Refused non-active facade targets: ' + repr(sorted(bad | (set(result) & EXCLUDED))))
    return result


def _asset(path):
    result = unreal.load_asset(path)
    if result is None:
        raise RuntimeError('Required asset missing: ' + path)
    return result


def _instance(name, parent, scalars=None, vectors=None, textures=None, switches=None):
    if name in _CACHE:
        return _CACHE[name]
    path = MATERIALS + '/' + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        instance = _asset(path)
    else:
        instance = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, MATERIALS, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    if instance is None:
        raise RuntimeError('Material creation failed: ' + name)
    mel = unreal.MaterialEditingLibrary
    mel.set_material_instance_parent(instance, _asset(parent))
    for key, value in (scalars or {}).items():
        if not mel.set_material_instance_scalar_parameter_value(instance, key, float(value)):
            raise RuntimeError('Scalar parameter missing: ' + name + '.' + key)
    for key, value in (vectors or {}).items():
        if not mel.set_material_instance_vector_parameter_value(instance, key, unreal.LinearColor(*value)):
            raise RuntimeError('Vector parameter missing: ' + name + '.' + key)
    for key, value in (textures or {}).items():
        if not mel.set_material_instance_texture_parameter_value(instance, key, _asset(value)):
            raise RuntimeError('Texture parameter missing: ' + name + '.' + key)
    # These switch names are verified in the existing Opaque parent's source.
    for key, value in (switches or {}).items():
        if not mel.set_material_instance_static_switch_parameter_value(
                instance, key, bool(value), update_material_instance=False):
            raise RuntimeError('Static switch update failed: ' + name + '.' + key)
    mel.update_material_instance(instance)
    if not unreal.EditorAssetLibrary.save_loaded_asset(instance, False):
        raise RuntimeError('Material save failed: ' + name)
    _CACHE[name] = instance
    return instance


def _opaque(name, tint, roughness=.75, metallic=0., normal=0., colour=None, relief=None, size=1., macro=0.):
    return _instance(name, OPAQUE,
        scalars={'SizeU_m':size, 'SizeV_m':size, 'WorldYawDeg':0.,
                 'RoughnessScale':roughness, 'MacroVariation':macro,
                 'VariationSize_m':4., 'NormalStrength':normal, 'Metallic':metallic, 'Specular':.5},
        vectors={'Tint':list(tint)+[1.]},
        textures={'BaseColorMap':colour or TEXTURES+'T_W1529_White',
                  'NormalMap':relief or TEXTURES+'T_W1529_FlatNormal',
                  'RoughnessMap':TEXTURES+'T_W1529_WhiteLinear'},
        switches={'UseMeshUV':False, 'AntiRepeat':True, 'Weathering':False})


def materials(record):
    """Return six slot materials and the applied inferred palette, without editing any parent."""
    appearance = record['appearance']
    family = appearance['family']
    if family not in palette.FAMILIES:
        raise RuntimeError('Unknown facade family: ' + family)
    colour, normal, rough, rough_red, size_u, size_v, _, _ = palette.FAMILIES[family]
    # A shared 0.1-linear-unit palette avoids hundreds of near-identical instances.
    tint = [round(round(float(v)/.1)*.1, 2) for v in appearance['wall_tint']]
    key = family.replace(' ', '_') + '_' + '_'.join(str(round(v*10)) for v in tint)
    wall = _instance('MI_NDF_Wall_'+key, PARENT,
        scalars={'WindowAmount':0., 'Wall_SizeU_m':size_u, 'Wall_SizeV_m':size_v,
                 'RoughFromRed':rough_red, 'Wall_RoughnessScale':1., 'WorldYawDeg':0.,
                 'MacroVariation':.06, 'VariationSize_m':4., 'BaseDirt':0., 'Roof_Size_m':2.},
        vectors={'Wall_Tint':tint+[1.], 'Roof_Colour':[.14,.14,.135,1.]},
        textures={'Wall_BaseColorMap':colour, 'Wall_NormalMap':normal, 'Wall_RoughnessMap':rough})
    roof = _opaque('MI_NDF_Roof', (.55,.55,.53), .82, normal=.35,
                   colour=BITUMEN+'BaseColor', relief=BITUMEN+'Normal', size=2., macro=.035)
    glass = _opaque('MI_NDF_Glass', (.025,.045,.060), .14, metallic=.25)
    frame_name = appearance['frame']
    frames = {'bronze':(.035,.028,.020), 'dark bronze':(.035,.028,.020),
              'white':(.70,.70,.67), 'black':(.015,.015,.015)}
    if frame_name not in frames:
        raise RuntimeError('Unknown facade frame: ' + frame_name)
    frame = _opaque('MI_NDF_Frame_'+frame_name.replace(' ','_'), frames[frame_name], .4, metallic=.15)
    mast = _opaque('MI_NDF_Metal', (.11,.12,.13), .4, metallic=.65)
    trim = _opaque('MI_NDF_Trim', (.75,.73,.68), .78, normal=.3,
                   colour=TEXTURES+'T_W1529_Concrete046_C', relief=TEXTURES+'T_W1529_Concrete046_N',
                   size=2.4, macro=.025)
    return [wall,roof,mast,glass,frame,trim], {'family':family,'wall_tint':tint,'frame':frame_name,
                                            'status':'Owner-approved inferred presentation palette'}


def _save_levels(paths):
    packages = {}
    for actor in ws.actors():
        level = ws.level_of(actor)
        if level in paths:
            packages[level] = actor.get_outermost()
    missing = set(paths) - set(packages)
    if missing:
        raise RuntimeError('Cannot find loaded named level packages: ' + repr(sorted(missing)))
    if not unreal.EditorLoadingAndSavingUtils.save_packages(list(packages.values()), True):
        raise RuntimeError('Named level save failed: ' + repr(sorted(packages)))
    return sorted(packages)


async def batch(ids):
    ids = _ids(ids)
    if ws.world_path() != '/Game/Wieland1529/L_Site_M4':
        raise RuntimeError('Working site level required')
    editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not editor.set_current_level_by_name('L_Nearby_Detail'):
        raise RuntimeError('Cannot select facade staging level')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    mesh_sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    existing = {a.get_actor_label():a for a in ws.actors()}
    out = []
    OUT.mkdir(parents=True, exist_ok=True)
    logpath = OUT / 'importfacade_records.jsonl'
    try:
        for bid in ids:
            name = 'NDF_'+bid
            data = json.loads((DATA/(name+'.json')).read_text(encoding='utf-8'))
            source = json.loads((DATA/(name+'.record.json')).read_text(encoding='utf-8'))
            mats, applied_palette = materials(source)
            await asyncio.sleep(0)
            path = ROOT+'/'+name
            if unreal.EditorAssetLibrary.does_asset_exist(path):
                sm = _asset(path)
            else:
                mesh = p17._make_mesh(data)
                opts = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
                opts.enable_nanite = True
                nanite = unreal.MeshNaniteSettings()
                nanite.enabled = True
                opts.nanite_settings = nanite
                opts.enable_collision = False
                opts.enable_recompute_normals = False
                sm, outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh,path,opts)
                if sm is None:
                    raise RuntimeError('Mesh creation failed '+name+' '+str(outcome))
            while len(sm.static_materials) < len(mats):
                sm.add_material(mats[len(sm.static_materials)])
            for slot, material in enumerate(mats):
                sm.set_material(slot, material)
            actor = existing.get(name)
            if actor is None:
                actor = actors.spawn_actor_from_object(sm,unreal.Vector(*data['pivot']),unreal.Rotator(0,0,0))
                if actor is None:
                    raise RuntimeError('Actor creation failed '+name)
            if ws.level_of(actor) != LEVEL:
                raise RuntimeError('Facade actor belongs to unexpected level: '+name)
            actor.set_actor_label(name)
            actor.set_folder_path('NearbyDetail/Facades')
            actor.tags = ['W1529.NearbyFacade','W1529.County.'+bid,'W1529.AssumedFacade']
            actor.static_mesh_component.set_static_mesh(sm)
            actor.set_actor_location(unreal.Vector(*data['pivot']),False,False)
            actor.static_mesh_component.set_visibility(False,False)
            desc = sm.get_static_mesh_description(0)
            result = {'name':name, 'county_id':bid, 'asset':sm.get_path_name(), 'actor':actor.get_path_name(),
                      'triangles':desc.get_triangle_count(), 'expected_triangles':len(data['triangles']),
                      'uv_channels':mesh_sub.get_num_uv_channels(sm,0),
                      'nanite':bool(mesh_sub.get_nanite_settings(sm).enabled), 'visible':False,
                      'materials':[m.get_path_name() for m in mats], 'applied_palette':applied_palette,
                      'windows':source['windows'], 'doors':source['doors'],
                      'measured_top_cm':source['measured_top_cm'], 'output_top_cm':source['output_top_cm']}
            if result['triangles']!=result['expected_triangles'] or result['uv_channels']<1 or not result['nanite']:
                raise RuntimeError('Facade validation failed: '+json.dumps(result))
            if not unreal.EditorAssetLibrary.save_loaded_asset(sm,False):
                raise RuntimeError('Mesh save failed '+name)
            with logpath.open('a',encoding='utf-8') as log:
                log.write(json.dumps(result)+chr(10))
            out.append(result)
            STATE['completed'] = len(out)
            STATE['last'] = name
            await asyncio.sleep(0)
        _save_levels({LEVEL})
    finally:
        editor.set_current_level_by_name('L_Site_M4')
    return out


async def _run(ids):
    try:
        result = await batch(ids)
        STATE.update(active=False,result={'count':len(result),'records':result[:3]})
    except Exception as exc:
        STATE.update(active=False,error=repr(exc))


def start(ids):
    global TASK
    if STATE.get('active'):
        raise RuntimeError('Facade import already active')
    ids = _ids(ids)
    STATE.clear()
    STATE.update(active=True,total=len(ids),completed=0)
    TASK = asyncio.create_task(_run(ids))
    return dict(STATE)


def status():
    return dict(STATE)


def activate(ids, save=False):
    """Show selected facade copies and hide only their measured ND/P17 replacements.

    Does not change any R15 or skyline visibility. Snapshot precedes mutation.
    save=True saves only the staging and affected local P17 levels by name.
    """
    ids = set(_ids(ids))
    if ws.world_path() != '/Game/Wieland1529/L_Site_M4':
        raise RuntimeError('Working site level required')
    actors = {a.get_actor_label():a for a in ws.actors()}
    missing = [bid for bid in ids if 'NDF_'+bid not in actors]
    if missing:
        raise RuntimeError('Cannot activate absent facades: '+repr(sorted(missing)))
    plan = []
    for bid in sorted(ids):
        for prefix,show in (('NDF_',True),('ND_',False),('P17Z_',False),('P17T_',False)):
            actor = actors.get(prefix+bid)
            if actor is None:
                continue
            level = ws.level_of(actor)
            allowed = {LEVEL} if prefix in ('NDF_','ND_') else REPLACEMENT_LEVELS
            if level not in allowed:
                if prefix.startswith('P17'):
                    continue
                raise RuntimeError('Refused visibility change outside detail level: '+actor.get_path_name())
            comp = actor.get_component_by_class(unreal.StaticMeshComponent)
            if comp is None:
                raise RuntimeError('Missing static mesh component: '+actor.get_actor_label())
            plan.append((actor,comp,show))
    before = [{'label':a.get_actor_label(),'actor':a.get_path_name(),'level':ws.level_of(a),
               'before':bool(c.get_editor_property('visible')),'after':show} for a,c,show in plan]
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    path = OUT/('facade_visibility_'+stamp+'.json')
    path.write_text(json.dumps(before,indent=2),encoding='utf-8')
    changed = []
    for actor,comp,show in plan:
        if bool(comp.get_editor_property('visible')) != show:
            comp.modify()
            comp.set_visibility(show,False)
            changed.append(actor.get_actor_label())
        if bool(comp.get_editor_property('visible')) != show:
            raise RuntimeError('Visibility readback failed: '+actor.get_actor_label())
    saved = _save_levels({ws.level_of(a) for a,c,show in plan}) if save else []
    return {'targets':len(ids),'changed':changed,'snapshot':str(path),'saved_levels':saved,
            'readback':readback(ids)}


def readback(ids):
    ids = set(_ids(ids))
    actors = {a.get_actor_label():a for a in ws.actors()}
    active = []
    overlaps = []
    missing = []
    for bid in sorted(ids):
        facade = actors.get('NDF_'+bid)
        if facade is None:
            missing.append(bid)
            continue
        if facade.static_mesh_component.get_editor_property('visible'):
            active.append(bid)
            for prefix in ('ND_','P17Z_','P17T_'):
                other = actors.get(prefix+bid)
                if other is not None and ws.level_of(other) in ({LEVEL}|REPLACEMENT_LEVELS):
                    comp = other.get_component_by_class(unreal.StaticMeshComponent)
                    if comp is not None and comp.get_editor_property('visible'):
                        overlaps.append(other.get_actor_label())
    return {'targets':len(ids),'visible_facades':len(active),'missing':missing,'visible_source_overlaps':overlaps}
