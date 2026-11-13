"""Phase 9: sample the graphics card's per-pass times at the hold stations and reduce them to the budget rows.

Usage (from a terminal, the editor running):
    python -B gpu_passes.py <label> [<stations, comma separated>] [<console variables as JSON>] [<samples>]

For each station the camera is held under the measuring conditions of tools/phase9_profile_m7.py (tier conditions
unless the console variables say otherwise), 6 seconds pass, and then the editor's GPU profiler tool is called
`samples` times (default 3), one second apart. The trees are written to
profiles/2026-11-13_M7/<label>/gpu_passes_<label>.json in the format of tools/reduce_gpu_passes.py, which is then
run on it. Every setting is put back at the end.
"""

import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, "/")
ROOT = HERE.rsplit("/review/", 1)[0]
TOOLS = ROOT + "/tools"
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True

import ue_call  # noqa: E402

HEAD = ("import sys, json, importlib\nsys.dont_write_bytecode = True\nT = %r\n"
        "if T not in sys.path:\n    sys.path.insert(0, T)\nimport phase9_profile_m7 as m7\n" % TOOLS)


def text_of(message):
    if message is None or "error" in message:
        raise RuntimeError("call failed: %s" % json.dumps(message)[:600])
    result = message.get("result", {})
    text = "".join(item.get("text", "") for item in result.get("content", []) if item.get("type") == "text")
    if result.get("isError"):
        raise RuntimeError("tool error: %s" % text[:600])
    return text


def py(client, source, timeout=120.0):
    arguments = {"script": {"language": "Python", "content": HEAD + source + "\n"}}
    return text_of(client.call("call_tool", {"toolset_name": ue_call.PY_TOOLSET, "tool_name": ue_call.PY_TOOL, "arguments": arguments}, timeout))


def tool(client, toolset, name, arguments):
    return json.loads(text_of(client.call("call_tool", {"toolset_name": toolset, "tool_name": name, "arguments": arguments}, 300.0)))["returnValue"]


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    label = argv[1]
    stations = argv[2].split(",") if len(argv) > 2 and argv[2] else ["S1", "S2", "S6", "D2", "D5"]
    cvars = json.loads(argv[3]) if len(argv) > 3 and argv[3] else None
    count = int(argv[4]) if len(argv) > 4 else 3
    folder = "%s/profiles/2026-11-13_M7/%s" % (ROOT, label)
    os.makedirs(folder, exist_ok=True)
    out_path = "%s/gpu_passes_%s.json" % (folder, label)
    client = ue_call.Client()
    client.open()
    data = {"engine": "5.9", "date": time.strftime("%Y-%m-%d %H:%M"), "level": "/Game/Wieland1529/L_Site_M4", "label": label,
            "quality": "Epic (every sg group at 3), texture pool 1000 MB, Game View on, t.MaxFPS 1000",
            "console_variables": cvars if cvars is not None else "tier conditions (r.Editor.Viewport.ScreenPercentage 82)",
            "method": "PerfToolset.GpuProfilerToolset.TriggerGPUProfile, %d single-frame samples per station, camera held 6 s "
                      "before the first sample, editor asked to the front before each" % count,
            "stations": {}, "samples": []}
    try:
        for station in stations:
            answer = py(client, "json.dumps(m7.pose(%r, %s))" % (station, repr(cvars))).strip().splitlines()[-1]
            posed = json.loads(json.loads(answer)["returnValue"])
            data["stations"][station] = posed
            data["viewport_pixels"] = posed["viewport_pixels"]
            percentage = posed["cvars"].get("r.Editor.Viewport.ScreenPercentage", 100)
            time.sleep(6)
            for sample in range(1, count + 1):
                py(client, "import wieland_profile as wp\nwp.to_front()")
                time.sleep(1)
                timings = tool(client, "PerfToolset.StatsToolset", "GetFrameTimings", {})
                tree = tool(client, "PerfToolset.GpuProfilerToolset", "TriggerGPUProfile", {"minInclusiveMs": 0})
                data["samples"].append({"station": station, "screen_percentage": percentage, "sample": sample,
                                        "frame_timings": timings, "tree": tree})
            print("sampled", station, flush=True)
    finally:
        print(py(client, "json.dumps(m7.unpose())")[-300:])
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    return subprocess.call([sys.executable, "-B", TOOLS + "/reduce_gpu_passes.py", out_path])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
