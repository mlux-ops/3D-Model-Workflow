"""Phase 8, J14: open the site top level L_Site_M2 (discarding the unsaved mark the temporary render camera
left on L_Site_M4) and read what it holds. Changes nothing."""
import importlib
import json

import unreal

import wieland_levels as wlv
import wieland_lighting as wl

importlib.reload(wl)
out = {"before": wl.world_path(), "dirty_before": wl.dirty()}
if wl.world_path() != wl.SITE_LEVEL:
    out["opened"] = wlv.open_level(wl.SITE_LEVEL, discard=True)
out["after"] = wl.world_path()
out["levels"] = sorted(wl.levels())
out["placeholders"] = wl.placeholders()
out["lights"] = [[a.get_actor_label(), a.get_class().get_name(), wl.level_of(a), [str(t) for t in a.tags]]
                 for a in wl.actors()
                 if isinstance(a, (unreal.DirectionalLight, unreal.SkyLight, unreal.SkyAtmosphere,
                                   unreal.ExponentialHeightFog, unreal.PostProcessVolume, unreal.VolumetricCloud))]
out["dirty"] = wl.dirty()
json.dumps(out, default=str)
