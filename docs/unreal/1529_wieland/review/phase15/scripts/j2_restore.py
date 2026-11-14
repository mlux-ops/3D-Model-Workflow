"""Phase 15, J2 (no saving here): remove the list "Neighbour development" from LVS_W1529_Surroundings; switch on the option
already in use of the list "Surroundings" ("Earlier detailed buildings") and read back the two parts of 1525 N. Wieland;
show SB_782868 directly (no list binds it). Returns the lists left, the three objects' Visible, and the unsaved packages."""
import json
import unreal
VML = unreal.VariantManagerLibrary
sa = unreal.load_asset("/Game/Wieland1529/Surroundings/LVS_W1529_Surroundings")
out = {"removed": 0}
sa.modify()
for i in reversed(range(sa.get_num_variant_sets())):
    vs = sa.get_variant_set(i)
    if str(vs.get_display_text()) == "Neighbour development":
        VML.remove_variant_set(sa, vs)
        out["removed"] += 1
out["lists_left"] = [str(sa.get_variant_set(i).get_display_text()) for i in range(sa.get_num_variant_sets())]
switched = None
for i in range(sa.get_num_variant_sets()):
    vs = sa.get_variant_set(i)
    if str(vs.get_display_text()) == "Surroundings":
        for j in range(vs.get_num_variants()):
            v = vs.get_variant(j)
            if str(v.get_display_text()) == "Earlier detailed buildings":
                switched = bool(v.switch_on())
out["switched_surroundings_earlier"] = switched
def lvl(a):
    return a.get_outer().get_outer().get_path_name().split(".")[0]
want = {"SB_782868": "/Game/Wieland1529/Surroundings/L_Surroundings",
        "R15_PART_opaque_xm04_yp01_part01": "/Game/Wieland1529/Surroundings/L_Surroundings_R15",
        "R15_PART_glass_xm04_yp01_part01": "/Game/Wieland1529/Surroundings/L_Surroundings_R15"}
state = {}
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    lab = a.get_actor_label()
    if lab in want and lvl(a) == want[lab]:
        c = a.get_component_by_class(unreal.StaticMeshComponent)
        before = bool(c.get_editor_property("visible"))
        if lab == "SB_782868" and not before:
            a.modify()
            c.modify()
            c.set_visibility(True, False)
        state[lab] = {"before_step": before, "now": bool(c.get_editor_property("visible"))}
out["objects"] = state
utils = unreal.EditorLoadingAndSavingUtils
out["dirty"] = sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))
json.dumps(out)
