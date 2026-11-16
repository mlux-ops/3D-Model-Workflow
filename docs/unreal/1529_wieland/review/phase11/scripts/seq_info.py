"""Phase 11, step 11.2: read back a level sequence of this phase (bindings, their parents, tracks, key counts).

Reads review/phase11/seq_job.json = {"asset": "SEQ_W1529_Triplex"[, "remove_binding": "name", "rename": ["old", "new"]]}.
With "remove_binding" it removes that one binding (an empty one left by the build) and saves the sequence;
with "rename" it gives a binding a plain name and saves the sequence.
"""
import json
import unreal

BASE = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase11/"
with open(BASE + "seq_job.json", "r", encoding="utf-8") as handle:
    job = json.load(handle)
path = "/Game/Wieland1529/Delivery/" + job["asset"]
sequence = unreal.EditorAssetLibrary.load_asset(path)
changed = []
for binding in list(sequence.get_bindings()):
    name = str(binding.get_display_name())
    if job.get("remove_binding") == name:
        if binding.get_tracks() or binding.get_child_possessables():
            raise RuntimeError("the binding %s is not empty" % name)
        binding.remove()
        changed.append("removed " + name)
    elif job.get("rename") and job["rename"][0] == name:
        binding.set_display_name(job["rename"][1])
        changed.append("renamed %s to %s" % (name, job["rename"][1]))
saved = bool(unreal.EditorAssetLibrary.save_asset(path, False)) if changed else None
rows = []
for binding in sequence.get_bindings():
    parent = binding.get_parent()
    rows.append({"name": str(binding.get_display_name()),
                 "parent": str(parent.get_display_name()) if parent and parent.is_valid() else None,
                 "class": str(binding.get_possessed_object_class().get_name()) if binding.get_possessed_object_class() else None,
                 "tracks": [[track.get_class().get_name(), [len(channel.get_keys()) for channel in section.get_all_channels()][:7]]
                            for track in binding.get_tracks() for section in track.get_sections()]})
json.dumps({"asset": path, "changed": changed, "saved": saved, "bindings": rows,
            "spawnables": [str(b.get_display_name()) for b in sequence.get_spawnables()],
            "possessables": [str(b.get_display_name()) for b in sequence.get_possessables()],
            "sequence_tracks": [track.get_class().get_name() for track in sequence.get_tracks()]}, default=str)
