"""Phase 20 round 2: Two Prudential Plaza's spire, a clean built element the laser scan does not hold.

The scan (P17T_869122) ends at the top of the peaked crown (260.8 m above its ground). Photographs show the
slender spire above it; the owner's sheet puts the crown at 915 ft and the spire tip at 995 ft, so the spire is
80 ft (24.4 m) long. It is added on the scan's highest point (found by downward traces), as a square needle
2.4 m wide at its foot tapering to 0.3 m, in the mast material; the scan's own heights are not changed.
Mesh /Game/Wieland1529/Surroundings/P17/TowersClean/SM_P17_869122_Spire, actor P17T_869122_Spire in
L_Skyline_P17. Run inside the editor.
"""
import unreal

TOWER = 'P17T_869122'
LABEL = 'P17T_869122_Spire'
MESH = '/Game/Wieland1529/Surroundings/P17/TowersClean/SM_P17_869122_Spire'
MAST_MI = '/Game/Wieland1529/Surroundings/P17/Materials/MI_P17_Mast_White'
SPIRE_CM = 80.0 * 30.48
HALF_FOOT, HALF_TIP = 120.0, 15.0


def top_point(actor):
    comp = actor.static_mesh_component
    o, e = actor.get_actor_bounds(False)
    best = None
    n = 41
    for i in range(n):
        for j in range(n):
            x = o.x - e.x + (i + 0.5) * 2 * e.x / n
            y = o.y - e.y + (j + 0.5) * 2 * e.y / n
            r = comp.line_trace_component(unreal.Vector(x, y, o.z + e.z + 500), unreal.Vector(x, y, o.z - e.z), True, False, False)
            if r is None:
                continue
            loc = r[0] if isinstance(r[0], unreal.Vector) else r[1]
            if best is None or loc.z > best.z:
                best = loc
    return best


def build(top):
    desc = unreal.StaticMesh.create_static_mesh_description(None)
    pg = desc.create_polygon_group()
    desc.set_polygon_group_material_slot_name(pg, 'Mast')
    z0, z1 = -100.0, SPIRE_CM            # relative to the actor, which stands on the crown's top point
    ring0 = [(-HALF_FOOT, -HALF_FOOT), (HALF_FOOT, -HALF_FOOT), (HALF_FOOT, HALF_FOOT), (-HALF_FOOT, HALF_FOOT)]
    ring1 = [(-HALF_TIP, -HALF_TIP), (HALF_TIP, -HALF_TIP), (HALF_TIP, HALF_TIP), (-HALF_TIP, HALF_TIP)]
    quads = []
    for k in range(4):
        a, b = ring0[k], ring0[(k + 1) % 4]
        c, d = ring1[(k + 1) % 4], ring1[k]
        quads.append([(a[0], a[1], z0), (b[0], b[1], z0), (c[0], c[1], z1), (d[0], d[1], z1)])
    quads.append([(p[0], p[1], z1) for p in ring1])
    for q in quads:
        vis = []
        for p in q:
            v = desc.create_vertex()
            desc.set_vertex_position(v, unreal.Vector(*p))
            vi = desc.create_vertex_instance(v)
            desc.set_vertex_instance_uv(vi, unreal.Vector2D(p[0] / 100.0, p[2] / 100.0), 0)
            vis.append(vi)
        # Points are counter-clockwise seen from outside (right-hand outward); the engine's front is the reverse.
        desc.create_triangle(pg, [vis[0], vis[2], vis[1]])
        desc.create_triangle(pg, [vis[0], vis[3], vis[2]])
    if unreal.EditorAssetLibrary.does_asset_exist(MESH):
        sm = unreal.load_asset(MESH)
    else:
        sm = unreal.AssetToolsHelpers.get_asset_tools().create_asset(MESH.split('/')[-1], MESH.rsplit('/', 1)[0], unreal.StaticMesh, None)
    sm.set_editor_property('static_materials', [unreal.StaticMaterial(material_interface=unreal.load_asset(MAST_MI), material_slot_name='Mast')])
    sm.build_from_static_mesh_descriptions([desc], False, False)
    unreal.EditorAssetLibrary.save_asset(MESH, only_if_is_dirty=False)
    return sm


def main():
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
    tower = actors[TOWER]
    top = top_point(tower)
    sm = build(top)
    previous = les.get_current_level().get_outermost().get_name().split('/')[-1]
    les.set_current_level_by_name('L_Skyline_P17')
    try:
        spire = actors.get(LABEL)
        if spire is None:
            spire = eas.spawn_actor_from_object(sm, top, unreal.Rotator(0, 0, 0))
            spire.set_actor_label(LABEL)
        else:
            spire.static_mesh_component.set_static_mesh(sm)
            spire.set_actor_location(top, False, False)
        spire.set_folder_path(unreal.Name('Skyline/Towers'))
        spire.tags = list(tower.tags)
        spire.static_mesh_component.set_editor_property('mobility', unreal.ComponentMobility.STATIC)
    finally:
        les.set_current_level_by_name(previous)
    ok = unreal.EditorLoadingAndSavingUtils.save_packages([tower.get_level().get_outermost()], True)
    o, e = spire.get_actor_bounds(False)
    return 'crown top %.0f, %.0f, %.0f cm; spire top %.0f cm; level %s saved %s' % (
        top.x, top.y, top.z, o.z + e.z, spire.get_level().get_outermost().get_name(), ok)


RESULT = main()
