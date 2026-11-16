"""Reduce per-pass GPU profiler samples to the rows of the plan's frame-time budget.

Usage:
    python reduce_gpu_passes.py <gpu_passes_stations.json>

The input holds samples taken with the editor's GPU profiler tool
(PerfToolset.GpuProfilerToolset.TriggerGPUProfile): for each station and
screen percentage, several single-frame trees of render passes. This script
assigns every pass to one row of the budget table in PLAN.md ("Frame time,
real-time tier"), takes the median over the samples, prints a table, and
writes <input>.summary.json.

Two cautions for reading the result:
- The graphics card runs two queues at once (Graphics and Compute), so the
  rows add up to more than the frame's wall-clock graphics-card time.
- Shadow projection cannot be separated from direct lighting in the
  profiler's tree, so it is counted under direct light.
"""

import json
import statistics
import sys

ROWS = [
    ("geometry", "Geometry: Nanite visibility and surface pass", 2.0),
    ("shadows", "Shadows: Virtual Shadow Maps", 2.0),
    ("lumen_scene", "Lumen scene update and its lighting caches", 1.5),
    ("gi", "Lumen global illumination", 2.5),
    ("reflections", "Lumen reflections, including glass", 1.5),
    ("direct", "Direct light", 1.0),
    ("sky", "Sky, atmosphere, clouds and fog", 0.8),
    ("translucent", "Translucent surfaces", 0.8),
    ("wind", "Foliage wind", 0.4),
    ("upscaling", "Temporal upscaling", 1.2),
    ("post", "Post-processing and tone mapping", 0.8),
    ("other", "Not in the budget table", None),
    ("editor_ui", "Editor interface (outside the scene)", None),
]

# (test, row, split): the first match wins. split=True means the children are
# classified one by one and only the remainder stays in this row.
RULES = [
    (lambda n: "Reflection" in n, "reflections", False),
    (lambda n: n.startswith("FrontLayerTranslucency"), "reflections", False),
    (lambda n: n.startswith("PostProcessing"), "post", True),
    (lambda n: n.startswith("TemporalSuperResolution"), "upscaling", False),
    (lambda n: n.startswith("RenderDeferredLighting"), "direct", True),
    (lambda n: n.startswith("DiffuseIndirectAndAO"), "gi", True),
    (lambda n: n.startswith("Translucency") and not n.startswith("TranslucencyLightingVolume") and not n.startswith("TranslucencyVolumeLighting"), "translucent", True),
    (lambda n: n.startswith("ShadowDepths") or "VirtualShadowMap" in n or n.startswith("ShadowProjection"), "shadows", False),
    (lambda n: n.startswith("LumenScene") or n.startswith("RayTracingScene") or "Lumen surface cache" in n, "lumen_scene", False),
    (lambda n: n.startswith("Lumen"), "gi", False),
    (lambda n: n.startswith("Nanite") or n.startswith("BasePass") or n.startswith("RenderVelocities") or n.startswith("PrePass") or n.startswith("HZB"), "geometry", False),
    (lambda n: n.startswith("StochasticLighting") or n.startswith("MegaLights") or n.startswith("ComputeLightGrid") or n.startswith("Lights") or n.startswith("LightFunction") or n.startswith("TranslucencyLightingVolume"), "direct", False),
    (lambda n: n.startswith("VolumetricCloud") or n.startswith("VolCloud") or n.startswith("SkyAtmosphere") or n.startswith("CaptureConvolveSkyEnvMap") or "Fog" in n or n.startswith("SkyLight"), "sky", False),
    (lambda n: n.startswith("Skinning") or n.startswith("DynamicWind"), "wind", False),
]


def classify(node, totals, inherited):
    name = node["Name"]
    row, split = inherited, False
    for test, rule_row, rule_split in RULES:
        if test(name):
            row, split = rule_row, rule_split
            break
    children = node.get("Children") or []
    if split and children:
        child_sum = 0.0
        for child in children:
            child_sum += child["InclusiveMs"]
            classify(child, totals, row)
        totals[row] = totals.get(row, 0.0) + max(0.0, node["InclusiveMs"] - child_sum)
    else:
        totals[row] = totals.get(row, 0.0) + node["InclusiveMs"]


def find(node, test):
    if test(node["Name"]):
        return node
    for child in node.get("Children") or []:
        found = find(child, test)
        if found:
            return found
    return None


def reduce_sample(tree):
    totals = {}
    queues = {}
    for queue in tree:
        queues[queue["Name"]] = queue["InclusiveMs"]
        graph = find(queue, lambda n: n.startswith("RenderGraphExecute - /ViewFamilies"))
        if graph is None:
            continue
        for node in graph.get("Children") or []:
            if node["Name"] == "Scene":
                for scene_pass in node.get("Children") or []:
                    classify(scene_pass, totals, "other")
            else:
                classify(node, totals, "other")
        slate = find(queue, lambda n: n.startswith("RenderGraphExecute - Slate"))
        if slate is not None:
            totals["editor_ui"] = totals.get("editor_ui", 0.0) + slate["InclusiveMs"]
    return totals, queues


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = argv[1]
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    groups = {}
    for sample in data["samples"]:
        key = (sample["station"], sample["screen_percentage"])
        totals, queues = reduce_sample(sample["tree"])
        groups.setdefault(key, []).append({"rows": totals, "queues": queues, "frame": sample.get("frame_timings")})
    summary = {"source": path.replace("\\", "/").split("/")[-1], "method": "median of the samples per station and screen percentage; passes assigned to budget rows by name", "budget_rows": [{"key": key, "label": label, "budget_ms": budget} for key, label, budget in ROWS], "results": []}
    for (station, percentage), samples in sorted(groups.items(), key=lambda item: (item[0][1], item[0][0])):
        rows = {key: statistics.median([s["rows"].get(key, 0.0) for s in samples]) for key, _, _ in ROWS}
        entry = {
            "station": station,
            "screen_percentage": percentage,
            "samples": len(samples),
            "rows_ms": {key: round(value, 3) for key, value in rows.items()},
            "sum_of_scene_rows_ms": round(sum(value for key, value in rows.items() if key != "editor_ui"), 3),
            "graphics_queue_ms": round(statistics.median([s["queues"].get("Graphics", 0.0) for s in samples]), 3),
            "compute_queue_ms": round(statistics.median([s["queues"].get("Compute", 0.0) for s in samples]), 3),
            "frame_gpu_ms": round(statistics.median([s["frame"]["gpuMs"] for s in samples if s.get("frame")]), 3),
            "frame_ms": round(statistics.median([s["frame"]["frameMs"] for s in samples if s.get("frame")]), 3),
        }
        summary["results"].append(entry)
    out_path = path[:-5] + ".summary.json" if path.endswith(".json") else path + ".summary.json"
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=1)
    header = "%-46s %7s" % ("Row", "budget") + "".join("  %s@%d" % (r["station"], r["screen_percentage"]) for r in summary["results"])
    print(header)
    for key, label, budget in ROWS:
        line = "%-46s %7s" % (label, ("%.1f" % budget) if budget is not None else "-")
        for result in summary["results"]:
            line += "  %6.2f" % result["rows_ms"][key]
        print(line)
    for label, field in (("Sum of the scene rows", "sum_of_scene_rows_ms"), ("Graphics queue", "graphics_queue_ms"), ("Compute queue", "compute_queue_ms"), ("Frame's graphics-card time", "frame_gpu_ms"), ("Frame time", "frame_ms")):
        line = "%-46s %7s" % (label, "")
        for result in summary["results"]:
            line += "  %6.2f" % result[field]
        print(line)
    print("written", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
