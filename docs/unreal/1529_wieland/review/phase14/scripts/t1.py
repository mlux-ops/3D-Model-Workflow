import sys, json, importlib
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase14/scripts")
import p14
importlib.reload(p14)
unreal = p14.unreal
out = {"window": p14.wl.window_restore(), "snap": p14.snapshot_state()}
out["times"] = {d: p14.sun_times(d) for d in p14.DAYS}
unreal.SystemLibrary.execute_console_command(p14.wl.world(), "viewmode lit")
unreal.SystemLibrary.execute_console_command(p14.wl.world(), "sg.ViewDistanceQuality 3")
cam = p14.camera("roofdeck")
s = p14.set_sun("winter", 12.0 + 10 / 60.0)
out["sun"] = s
p14.set_ev(p14.ev_for(s["height"]))
ok = await p14.shoot(p14.FRAMES + "/test/roof_winter_noon.png", settle=6.0)
out["shot"] = ok
json.dumps(out, default=str)
