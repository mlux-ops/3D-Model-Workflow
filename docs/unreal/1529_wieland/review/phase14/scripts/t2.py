import sys, json, importlib
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase14/scripts")
import p14
importlib.reload(p14)
unreal = p14.unreal
out = {}
span = p14.sun_at("winter", 12.0)[0].sunrise_time
out["span_dir"] = [x for x in dir(span) if not x.startswith("_")]
out["span_str"] = str(span.to_dict()) if hasattr(span, "to_dict") else ""
p14.camera("roofdeck")
p14.set_sun("winter", 12.0 + 10 / 60.0)
p14.set_ev(14.644)
# top-down view of the roof deck and the rear patios
p14.look("roofdeck", yaw=1.18, pitch=-89.0, loc=(-754.0, -1900.0, 3600.0))
out["a"] = await p14.shoot(p14.FRAMES + "/test/top_roof.png", settle=4.0)
p14.look("roofdeck", yaw=1.18, pitch=-89.0, loc=(-754.0, -2600.0, 2800.0))
out["b"] = await p14.shoot(p14.FRAMES + "/test/top_rear.png", settle=3.0)
json.dumps(out, default=str)
