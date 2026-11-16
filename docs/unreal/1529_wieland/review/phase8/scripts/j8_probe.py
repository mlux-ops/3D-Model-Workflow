import sys
sys.dont_write_bytecode = True
T = 'E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools'
if T not in sys.path:
    sys.path.insert(0, T)
import importlib
import unreal
import wieland_lighting as wl
import wieland_fixtures as wf
importlib.reload(wf)
out = {}
seen = {}
for (level, name), members in wf._groups().items():
    fixture, meta = members[0][2], members[0][3]
    fam = meta.get('Element*Family', '')
    if fam in seen:
        continue
    # the main light: largest value
    actor, comp = max(members, key=lambda m: m[1].intensity)[:2]
    loc = comp.get_world_location()
    origin, extent = fixture.get_actor_bounds(False)
    hits = []
    for dz, label in ((-1.0, 'down'), (1.0, 'up')):
        hit = unreal.SystemLibrary.line_trace_single(wl.world(), loc, loc + unreal.Vector(0, 0, dz * 400.0),
                                                     unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, False)
        if hit:
            t = hit.to_tuple()
            hits.append((label, round(t[3], 1), t[9].get_actor_label()[:40] if t[9] else None))
        else:
            hits.append((label, None))
    meshes = [c.static_mesh.get_name()[:40] for c in fixture.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh]
    kids = [a.get_class().get_name() for a in fixture.get_attached_actors()]
    seen[fam] = {'fixture': fixture.get_actor_label()[:50], 'id': wf._revit_id(fixture), 'light_z': round(loc.z, 1),
                 'bounds_z': (round(origin.z - extent.z, 1), round(origin.z + extent.z, 1)),
                 'bounds_xy': (round(extent.x * 2, 1), round(extent.y * 2, 1)), 'hits': hits, 'meshes': meshes[:3], 'kids': kids[:6],
                 'cls': fixture.get_class().get_name()}
str(seen)
