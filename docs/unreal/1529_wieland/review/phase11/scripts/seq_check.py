"""Phase 11, step 11.2: read-only check of both camera-move sequences: do they exist, how long, and does the
camera they spawn carry the f/8 aperture and the 0.2 motion blur set in seq_build.py after 11:12."""
import json
import unreal

out = {}
for name in ["SEQ_W1529_Triplex", "SEQ_W1529_Penthouse"]:
    path = "/Game/Wieland1529/Delivery/" + name
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        out[name] = "missing"
        continue
    sequence = unreal.EditorAssetLibrary.load_asset(path)
    row = {"start": sequence.get_playback_start(), "end": sequence.get_playback_end(),
           "rate": str(sequence.get_display_rate().numerator), "bindings": [str(b.get_display_name()) for b in sequence.get_bindings()]}
    for spawnable in sequence.get_spawnables():
        template = spawnable.get_object_template()
        row["template"] = str(type(template).__name__)
        if template is None:
            continue
        component = template.get_editor_property("camera_component") if isinstance(template, unreal.CineCameraActor) else None
        if component:
            pp = component.get_editor_property("post_process_settings")
            row["aperture"] = component.get_editor_property("current_aperture")
            row["focal"] = component.get_editor_property("current_focal_length")
            row["motion_blur_override"] = pp.get_editor_property("override_motion_blur_amount")
            row["motion_blur"] = pp.get_editor_property("motion_blur_amount")
            row["exposure_bias"] = pp.get_editor_property("auto_exposure_bias")
    out[name] = row
json.dumps(out, default=str)
