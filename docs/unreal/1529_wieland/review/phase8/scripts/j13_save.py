"""Phase 8, step 8.9: save the lighting level by name after j13_set.py, and report what is still marked."""
import json

import wieland_lighting as wl

level = wl.LIGHT_FOLDER + "/L_Light_SummerAfternoon"
json.dumps({"saved": wl.save([level]), "dirty": wl.dirty()}, default=str)
