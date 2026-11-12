import sys, importlib, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.append(T)
import unreal
import wieland_site as ws
import wieland_lighting as wl
importlib.reload(wl)

# J4: the sun raised so that the flat card reads about 85,000 lux under the hazier sky, then three fog
# amounts looked at from S1, S2 and S6 (pictures only; nothing is saved here).
out = {"windows_restored": wl.window_restore()}
wl.by_label("LGT_Sun").light_component.set_editor_property("intensity", 160000.0)
FOG = unreal.ExponentialHeightFogComponent
ws.shots_begin(3)
try:
    for name, density in (("fog020", 0.02), ("fog005", 0.005), ("fog000", 0.0)):
        wl.props("LGT_HeightFog", FOG, [], {"fog_density": density})
        await wl.wait_frames(2.0)
        out[name] = str(await ws.shots(["S1", "S2", "S6"], wl.REVIEW + "/sky", "_j4_" + name, 1280, 720))
finally:
    ws.shots_end()
out["dirty"] = wl.dirty()
json.dumps(out)
