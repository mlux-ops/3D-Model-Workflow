"""Phase 15, read-only: live Visible of the objects bound in the list "Surroundings", grouped by level, and of every
plain block SB_* in L_Surroundings that the list does not bind. Shows which option is on and what SB_782868's peers look like."""
import json
import unreal
sa = unreal.load_asset("/Game/Wieland1529/Surroundings/LVS_W1529_Surroundings")
def lvl(a):
    return a.get_outer().get_outer().get_path_name().split(".")[0].split("/")[-1]
def vis(a):
    c = a.get_component_by_class(unreal.StaticMeshComponent)
    return bool(c.get_editor_property("visible")) if c else None
bound = {}
for i in range(sa.get_num_variant_sets()):
    vs = sa.get_variant_set(i)
    if str(vs.get_display_text()) != "Surroundings":
        continue
    v = vs.get_variant(0)
    for k in range(v.get_num_actors()):
        a = v.get_actor(k)
        if a:
            bound[a.get_path_name()] = a
groups = {}
for a in bound.values():
    key = lvl(a)
    g = groups.setdefault(key, {"visible": 0, "hidden": 0, "hidden_labels": []})
    if vis(a):
        g["visible"] += 1
    else:
        g["hidden"] += 1
        g["hidden_labels"].append(a.get_actor_label())
unbound_sb = {"visible": 0, "hidden": [], "count": 0}
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if lvl(a) == "L_Surroundings" and a.get_actor_label().startswith("SB_") and a.get_path_name() not in bound:
        unbound_sb["count"] += 1
        if vis(a):
            unbound_sb["visible"] += 1
        else:
            unbound_sb["hidden"].append(a.get_actor_label())
json.dumps({"surroundings_bound_by_level": groups, "unbound_SB_in_L_Surroundings": unbound_sb})
