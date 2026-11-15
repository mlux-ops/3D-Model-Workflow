"""Owner-requested local detailed buildings with the measured Phase 20 skyline.

Existing meshes and Datasmith assets are never edited. Visibility is on placed copies only.
"""
import json
from pathlib import Path

import unreal
import wieland_p17 as p17
import wieland_site as ws

DOCS = Path(__file__).resolve().parent.parent
OUT = DOCS / 'review/phase20/nearby_detail'
OPTION = 'Earlier local buildings + updated skyline'


def targets():
    hidden_ids = {name.removeprefix('SB_') for name in ws.hidden_names()}
    groups = p17.surroundings_groups()
    plan = []
    for key, actors in groups.items():
        for actor in actors:
            label = actor.get_actor_label()
            visible = key == 'r15' or (key == 'p17' and label.removeprefix('P17Z_') not in hidden_ids)
            comp = actor.get_component_by_class(unreal.StaticMeshComponent)
            if comp is not None:
                plan.append((actor, comp, visible, key))
    return plan


def snapshot():
    OUT.mkdir(parents=True, exist_ok=True)
    result = [{'actor':a.get_path_name(), 'label':a.get_actor_label(), 'group':group,
               'before':bool(c.get_editor_property('visible')), 'hybrid':show,
               'level':ws.level_of(a)} for a,c,show,group in targets()]
    dest = OUT / 'hybrid_visibility_before.json'
    if dest.exists():
        raise RuntimeError('Snapshot already exists; reconcile before retrying')
    dest.write_text(json.dumps(result,indent=2),encoding='utf-8')
    return {'snapshot':str(dest), 'actors':len(result), 'dirty':ws.dirty()}


def apply():
    plan = targets()
    changed = []
    for actor, comp, show, group in plan:
        if bool(comp.get_editor_property('visible')) != show:
            comp.modify()
            comp.set_visibility(show, False)
            changed.append(actor.get_actor_label())
    return {'changed':changed, 'readback':readback()}


def readback():
    plan = targets()
    counts = {}
    wrong = []
    for actor, comp, show, group in plan:
        seen = bool(comp.get_editor_property('visible'))
        counts.setdefault(group,{'total':0,'visible':0})
        counts[group]['total'] += 1
        counts[group]['visible'] += int(seen)
        if seen != show:
            wrong.append(actor.get_actor_label())
    result = {'counts':counts, 'mismatches':wrong}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'hybrid_readback.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


def add_option():
    asset = ws.variant_asset()
    vset = next(asset.get_variant_set(i) for i in range(asset.get_num_variant_sets())
                if str(asset.get_variant_set(i).get_display_text()) == ws.VARIANT_LIST)
    if vset.get_variant_by_name(OPTION) is not None:
        raise RuntimeError('Hybrid option already exists; reconcile before retrying')
    variant = unreal.Variant()
    variant.set_display_text(OPTION)
    lib = unreal.VariantManagerLibrary
    lib.add_variant(vset,variant)
    count = 0
    for actor, comp, visible, group in targets():
        lib.add_actor_binding(variant,actor)
        value = lib.capture_property(variant,actor,ws.VISIBLE_PROPERTY)
        if value is None:
            raise RuntimeError('Cannot capture visibility: '+actor.get_actor_label())
        lib.set_value_bool(value,visible)
        count += 1
    return {'asset':asset.get_path_name(),'option':OPTION,'bindings':count,
            'saved':bool(unreal.EditorAssetLibrary.save_loaded_asset(asset,False))}


def save_levels():
    paths = {ws.R15_LEVEL,'/Game/Wieland1529/Surroundings/L_Surroundings_P17'}
    packages = {a.get_outermost().get_name():a.get_outermost() for a,c,s,g in targets()
                if ws.level_of(a) in paths}
    result = unreal.EditorLoadingAndSavingUtils.save_packages(list(packages.values()),True)
    return {'saved':result,'packages':sorted(packages),'readback':readback()}
