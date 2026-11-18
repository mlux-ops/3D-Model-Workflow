"""Phase 8, step 8.9: hit lighting carried by the lighting level. Sets the Lumen ray lighting mode of the
unbounded post-process volume LGT_Exposure_Outdoors to hit lighting and reads it back. Does not save;
review/phase8/scripts/j13_save.py saves the lighting level by name."""
import json

import unreal

import wieland_lighting as wl

volume = wl.by_label("LGT_Exposure_Outdoors")
settings = volume.get_editor_property("settings")
before = [bool(settings.get_editor_property("override_lumen_ray_lighting_mode")),
          str(settings.get_editor_property("lumen_ray_lighting_mode"))]
volume.modify()
settings.set_editor_property("override_lumen_ray_lighting_mode", True)
settings.set_editor_property("lumen_ray_lighting_mode", unreal.LumenRayLightingModeOverride.HIT_LIGHTING)
volume.set_editor_property("settings", settings)
after = volume.get_editor_property("settings")
json.dumps({"volume": volume.get_actor_label(), "level": wl.level_of(volume), "unbound": bool(volume.unbound),
            "before": before,
            "after": [bool(after.get_editor_property("override_lumen_ray_lighting_mode")),
                      str(after.get_editor_property("lumen_ray_lighting_mode"))],
            "exposure": wl.read_exposure("LGT_Exposure_Outdoors"), "dirty": wl.dirty()}, default=str)
