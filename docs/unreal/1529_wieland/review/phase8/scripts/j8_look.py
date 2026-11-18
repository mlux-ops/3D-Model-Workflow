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

def describe(a, depth=0):
    comps = [(c.get_class().get_name(), c.get_name()) for c in a.get_components_by_class(unreal.SceneComponent)]
    loc = a.get_actor_location()
    rot = a.get_actor_rotation()
    lines = ['%s%s [%s] %s loc(%.1f %.1f %.1f) rot(p%.0f y%.0f r%.0f) comps=%s' % ('  ' * depth, a.get_actor_label()[:60], a.get_class().get_name(), a.get_name(),
             loc.x, loc.y, loc.z, rot.pitch, rot.yaw, rot.roll, comps)]
    for child in a.get_attached_actors():
        lines += describe(child, depth + 1)
    return lines

seen = {}
out = []
for (level, name), members in sorted(wf._groups().items()):
    fixture, meta = members[0][2], members[0][3]
    fam = meta.get('Element*Family', '')
    if fam in seen:
        continue
    seen[fam] = 1
    parent = fixture.get_attach_parent_actor()
    out.append('== %s | id %s | parent %s [%s]' % (fam, wf._revit_id(fixture), parent.get_actor_label()[:40] if parent else None, parent.get_class().get_name() if parent else None))
    out += describe(fixture)
    # what is right under the main light
    actor, comp = max(members, key=lambda m: m[1].intensity)[:2]
    loc = comp.get_world_location()
    hit = unreal.SystemLibrary.line_trace_single(wl.world(), loc, loc + unreal.Vector(0, 0, -400.0), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, False)
    if hit:
        t = hit.to_tuple()
        out.append('   under light: %.1f cm %s [%s] comp %s' % (t[3], t[9].get_actor_label()[:50] if t[9] else None, t[9].get_class().get_name() if t[9] else None, t[10].get_name() if t[10] else None))
'\n'.join(out)
