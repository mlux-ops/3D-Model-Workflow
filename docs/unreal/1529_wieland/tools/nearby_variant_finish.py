"""Extend existing surroundings options without replacing any option list."""
import asyncio
import json
from pathlib import Path
import unreal
import wieland_site as ws
import nearby_facade_import as fi

OUT=Path('E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase20/nearby_detail')
TASK=None
STATE={}
HYBRID='Earlier local buildings + updated skyline'

async def run():
    try:
        asset=ws.variant_asset();lib=unreal.VariantManagerLibrary
        vset=next(asset.get_variant_set(i) for i in range(asset.get_num_variant_sets()) if str(asset.get_variant_set(i).get_display_text())==ws.VARIANT_LIST)
        additions=[a for a in ws.actors() if a.get_actor_label().startswith(('NDF_','NS_')) or a.get_actor_label()=='Neighbour1525_RoofFeatures']
        before=[str(vset.get_variant(i).get_display_text()) for i in range(vset.get_num_variants())]
        rows=[]
        for i in range(vset.get_num_variants()):
            variant=vset.get_variant(i);name=str(variant.get_display_text())
            bound={variant.get_actor(j).get_path_name() for j in range(variant.get_num_actors()) if variant.get_actor(j) is not None}
            targets=list(additions)
            if name==HYBRID:
                active=fi._ids([a.get_actor_label().removeprefix('NDF_') for a in additions if a.get_actor_label().startswith('NDF_')])
                actors={a.get_actor_label():a for a in ws.actors()}
                for bid in active:
                    for prefix in ('P17Z_','P17T_'):
                        actor=actors.get(prefix+bid)
                        if actor is not None and ws.level_of(actor) in fi.REPLACEMENT_LEVELS:targets.append(actor)
            checked=0
            for actor in targets:
                label=actor.get_actor_label()
                visible=name==HYBRID and not label.startswith(('P17Z_','P17T_'))
                if label=='Neighbour1525_RoofFeatures' and name=='Earlier detailed buildings':visible=True
                if actor.get_path_name() not in bound:
                    lib.add_actor_binding(variant,actor);bound.add(actor.get_path_name())
                props=lib.get_captured_properties(variant,actor)
                matches=[p for p in props if str(p.get_full_display_string())==ws.VISIBLE_PROPERTY]
                prop=matches[0] if matches else lib.capture_property(variant,actor,ws.VISIBLE_PROPERTY)
                if prop is None:raise RuntimeError('Capture failed '+name+' '+label)
                lib.set_value_bool(prop,visible)
                if bool(lib.get_value_bool(prop))!=visible:raise RuntimeError('Capture readback failed '+label)
                checked+=1
                if checked%25==0:await asyncio.sleep(0)
            rows.append({'option':name,'verified_bindings':checked,'total_bindings':variant.get_num_actors()})
        if before!=[str(vset.get_variant(i).get_display_text()) for i in range(vset.get_num_variants())]:raise RuntimeError('Original option names changed')
        if not unreal.EditorAssetLibrary.save_loaded_asset(asset,False):raise RuntimeError('Variant save failed')
        material_paths=[p for p in ws.dirty() if p.startswith('/Game/Wieland1529/Surroundings/NearbyDetail/Materials/')]
        saved=[]
        for p in material_paths:
            if not unreal.EditorAssetLibrary.save_loaded_asset(unreal.load_asset(p),False):raise RuntimeError('MI save failed '+p)
            saved.append(p);await asyncio.sleep(0)
        paths={'/Game/Wieland1529/L_Site_M4','/Game/Wieland1529/Surroundings/L_Nearby_Detail','/Game/Wieland1529/Surroundings/L_Surroundings_R15','/Game/Wieland1529/Surroundings/L_Surroundings_P17','/Game/Wieland1529/Surroundings/L_Skyline_P17'}
        packages={ws.level_of(a):a.get_outermost() for a in ws.actors() if ws.level_of(a) in paths}
        if not unreal.EditorLoadingAndSavingUtils.save_packages(list(packages.values()),True):raise RuntimeError('Named level save failed')
        result={'asset':asset.get_path_name(),'options':rows,'saved_new_materials':saved,'saved_levels':sorted(packages),'dirty':ws.dirty()}
        (OUT/'variant_extension.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        STATE.update(active=False,result=result)
    except Exception as exc:STATE.update(active=False,error=repr(exc))

def start():
    global TASK
    if STATE.get('active'):raise RuntimeError('Already active')
    STATE.clear();STATE.update(active=True);TASK=asyncio.create_task(run());return dict(STATE)

def status():return dict(STATE)
