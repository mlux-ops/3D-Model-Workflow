import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
w = wl.world()
def trace(a, b):
    r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(*a), unreal.Vector(*b), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    # tuple or struct depending on binding
    return r
out = {}
pts = {"terrace_N": (-1200, -2300, 1340), "terrace_S": (-400, -2300, 1340), "patio_unc_N": (-1190, -2750, 360), "patio_cov_N": (-1190, -2262, 363),
       "roof_N": (-1330, -1411, 1681), "roof_D1": (-1300, -1560, 1684), "patio_unc_S": (-420, -2750, 360)}
for k, p in pts.items():
    hit = trace(p, (p[0], p[1], p[2] + 4000))
    try:
        hr = hit[1] if isinstance(hit, tuple) else hit
        out[k] = {"raw": str(hit)[:300]}
    except Exception as e:
        out[k] = str(e)
json.dumps(out, default=str)
