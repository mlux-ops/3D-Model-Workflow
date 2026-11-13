"""Phase 13, step 13.8: the exterior path of profiles M4/M6/M7 (60 s, Phase 9 tier conditions, tools/phase9_profile_m7.py)
recorded once with the option "Existing buildings (as surveyed)" (label P13_existing) and once with
"Duke of Wells (proposed)" (label P13_proposed). The first warm-up walk is skipped as in Phase 9's state C2.
Run: python -B tools/ue_call.py py review/phase13/scripts/profile_exterior.py 900
Records: profiles/2026-11-13_P13/; reduce with tools/analyze_profile_csv.py.
"""
import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import phase9_profile_m7 as m7
import wieland_hotel as wh
importlib.reload(m7)
OUT = T.rsplit("/", 1)[0] + "/profiles/2026-11-13_P13"
result = {}
try:
    for key, option in (("existing", wh.OPTION_EXISTING), ("proposed", wh.OPTION_PROPOSED)):
        result[key + "_switch"] = wh.switch(option)
        result[key] = await m7.run(OUT + "/" + key, "P13" + key, parts=("exterior",), skip_first_walk=True,
                                   note="Phase 13: hotel option " + option)
finally:
    result["final"] = wh.switch(wh.OPTION_PROPOSED)
json.dumps(result, default=str)
