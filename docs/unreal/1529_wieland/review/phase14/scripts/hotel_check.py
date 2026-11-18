import sys, json, importlib
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase14/scripts")
import p14
importlib.reload(p14)
import wieland_hotel as wh
importlib.reload(wh)
cases = [("reardeck", "summer", 8.0), ("reardeck", "summer", 14.8), ("roofdeck", "winter", 10.5)]
out = {"start_state": wh.state()}
try:
    for deck, day, hour in cases:
        p14.camera(deck)
        s = p14.set_sun(day, hour)
        p14.set_ev(p14.ev_for(s["height"]))
        for label, option in (("off", wh.OPTION_EXISTING), ("on", wh.OPTION_PROPOSED)):
            out["switch_" + label] = wh.switch(option)["state"]
            name = "hotel_%s_%s_%s_%02d" % (label, deck, day, int(hour))
            out[name] = await p14.shoot(p14.FRAMES + "/test/" + name + ".png", settle=5.0)
finally:
    out["end_state"] = wh.switch(wh.OPTION_PROPOSED)["state"]
json.dumps(out, default=str)
