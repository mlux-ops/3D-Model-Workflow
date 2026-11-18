"""Phase 20 round 2: place the added landmark meshes in L_Skyline_P17, the way Phase 17 placed its towers.

Each P17R_<id>.json from meshes_towers_clean becomes a Nanite static mesh under
/Game/Wieland1529/Surroundings/P17/TowersClean/, gets a facade instance MI_P17_T_<id> (made from
M_W1529_P17_Facade; settings from INSTANCE below, refined later from photographs) plus MI_P17_Roof_Grey and
MI_P17_Mast_White, and is placed at its pivot in the sublevel L_Skyline_P17 (made the current level for the
spawn, then the earlier current level is restored), labelled P17T_<id>, folder Skyline/Towers, tagged as the
Phase 17 towers are. Saves only the new assets and L_Skyline_P17, by name.

Run inside the editor:  g = {'__name__': 'imp'}; exec(compile(open(p).read(), p, 'exec'), g); g['RESULT']
"""
import json
import os
import sys

import unreal

TOOLS = r'E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools'
if TOOLS not in sys.path:
    sys.path.append(TOOLS)
import wieland_p17 as wp  # noqa: E402

FOLDER = r'E:/Wieland1529_site_data/phase17/meshes_towers_clean'
MESH_ROOT = '/Game/Wieland1529/Surroundings/P17/TowersClean/'
MAT_ROOT = '/Game/Wieland1529/Surroundings/P17/Materials/'
LEVEL_PACKAGE = '/Game/Wieland1529/Surroundings/L_Skyline_P17'
REFERENCE_ACTOR = 'P17T_889662'   # a Phase 17 tower whose tags and level are copied

# Starting settings by what the building is known to be (refined from photographs in a later step).
GLASS_DARK = {'FloorHeight': 3.4, 'BayWidth': 1.5, 'FrameWidth': 0.1, 'SpandrelHeight': 0.9, 'WindowPattern': 1.0,
              'GlassColor': (0.03, 0.035, 0.04), 'FrameColor': (0.02, 0.022, 0.025)}
STONE_LIGHT = {'FloorHeight': 3.6, 'BayWidth': 1.6, 'FrameWidth': 0.6, 'SpandrelHeight': 1.1, 'WindowPattern': 1.0,
               'GlassColor': (0.03, 0.035, 0.04), 'FrameColor': (0.45, 0.42, 0.37)}
GLASS_LIGHT = {'FloorHeight': 3.3, 'BayWidth': 1.5, 'FrameWidth': 0.12, 'SpandrelHeight': 0.9, 'WindowPattern': 1.0,
               'GlassColor': (0.06, 0.08, 0.10), 'FrameColor': (0.35, 0.36, 0.37)}
ADD = [
    # (mesh name, label, instance settings, what it is)
    ('P17R_817666', 'P17T_817666', STONE_LIGHT, 'One Magnificent Mile'),
    ('P17R_852376', 'P17T_852376', STONE_LIGHT, 'One Bennett Park'),
    ('P17R_828186', 'P17T_828186', STONE_LIGHT, 'Water Tower Place'),
    ('P17R_828450', 'P17T_828450', STONE_LIGHT, 'Water Tower Place, east part'),
    ('P17R_866027', 'P17T_866027', GLASS_LIGHT, 'Aqua'),
    ('P17R_821196', 'P17T_821196', STONE_LIGHT, 'Palmolive Building, base (scan)'),
    ('P17R_osm143756601', 'P17T_osm143756601', STONE_LIGHT, 'Palmolive Building, tower and beacon (assumption)'),
    ('P17R_osm150408224', 'P17T_osm150408224', GLASS_DARK, 'Lake Point Tower (assumption)'),
    ('P17R_osm686187393', 'P17T_osm686187393', GLASS_LIGHT, 'Park Tower (assumption)'),
    ('P17R_osm1333503945', 'P17T_osm1333503945', GLASS_LIGHT, 'NEMA Chicago (assumption)'),
]


def main():
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    actors = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
    ref = actors[REFERENCE_ACTOR]
    level = ref.get_level()
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    previous = les.get_current_level().get_outermost().get_name().split('/')[-1]
    if not les.set_current_level_by_name(LEVEL_PACKAGE.split('/')[-1]):
        raise RuntimeError('could not make L_Skyline_P17 the current level')
    saved, report = [], []
    try:
        for mesh_name, label, params, what in ADD:
            data = json.load(open(os.path.join(FOLDER, mesh_name + '.json'), encoding='utf-8'))
            mi_name = 'MI_P17_T_' + label[5:]
            mi = wp.ensure_instance(mi_name, params)
            path = MESH_ROOT + mesh_name
            mesh = wp._make_mesh(data)
            if unreal.EditorAssetLibrary.does_asset_exist(path):
                sm = unreal.EditorAssetLibrary.load_asset(path)
                opt = unreal.GeometryScriptCopyMeshToAssetOptions()
                opt.enable_recompute_normals = False
                opt.emit_transaction = False
                opt.replace_materials = False
                unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(mesh, sm, opt, unreal.GeometryScriptMeshWriteLOD())
            else:
                opt = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
                opt.enable_nanite = True
                nan = unreal.MeshNaniteSettings()
                nan.enabled = True
                opt.nanite_settings = nan
                opt.enable_collision = False
                opt.enable_recompute_normals = False
                sm, outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh, path, opt)
            mats = [mi, unreal.load_asset(MAT_ROOT + 'MI_P17_Roof_Grey'), unreal.load_asset(MAT_ROOT + 'MI_P17_Mast_White')]
            while len(sm.static_materials) < 3:
                sm.add_material(mats[len(sm.static_materials)])
            for i, m in enumerate(mats):
                sm.set_material(i, m)
            pivot = data['pivot']
            actor = actors.get(label)
            if actor is None:
                actor = eas.spawn_actor_from_object(sm, unreal.Vector(pivot[0], pivot[1], pivot[2]), unreal.Rotator(0.0, 0.0, 0.0))
                actor.set_actor_label(label)
            else:
                actor.static_mesh_component.set_static_mesh(sm)
                actor.set_actor_location(unreal.Vector(pivot[0], pivot[1], pivot[2]), False, False)
            actor.set_folder_path(unreal.Name('Skyline/Towers'))
            actor.tags = list(ref.tags)
            actor.static_mesh_component.set_editor_property('mobility', unreal.ComponentMobility.STATIC)
            o, e = actor.get_actor_bounds(False)
            report.append('%s %s in %s top %.0f cm tris %d nanite %s' % (
                label, what, actor.get_level().get_outer().get_name(), o.z + e.z,
                sm.get_num_triangles(0), sms.get_nanite_settings(sm).enabled))
            saved += [path, MAT_ROOT + mi_name]
    finally:
        les.set_current_level_by_name(previous)
    for p in saved:
        unreal.EditorAssetLibrary.save_asset(p, only_if_is_dirty=False)
    ok = unreal.EditorLoadingAndSavingUtils.save_packages([level.get_outermost()], True)
    report.append('saved %d assets; %s saved %s' % (len(saved), LEVEL_PACKAGE, ok))
    return report


RESULT = '\n'.join(main())
