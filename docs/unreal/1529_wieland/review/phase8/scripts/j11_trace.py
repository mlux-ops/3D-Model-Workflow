"""Phase 8, step 8.9: what lies behind a pixel of a view. Sends one ray from the view's camera through the
picture fraction (u, v) and lists everything it crosses, with each material's two-sided flag and whether
the surface faces the camera. Reads review/phase8/realtime/trace.json = {"view": "S9", "u": 0.1, "v": 0.12}.
Changes nothing."""
import json
import math
import os

import unreal

import wieland_lighting as wl
import wieland_truth as wt

with open(os.path.join(wl.REVIEW, "realtime", "trace.json"), "r", encoding="utf-8") as handle:
    job = json.load(handle)
location, rotation = wt.view(job["view"])
half = math.tan(math.radians(wt.FOV / 2.0))
x = (job["u"] * 2.0 - 1.0) * half
z = (1.0 - job["v"] * 2.0) * half * 9.0 / 16.0
forward = unreal.MathLibrary.get_forward_vector(rotation)
right = unreal.MathLibrary.get_right_vector(rotation)
up = unreal.MathLibrary.get_up_vector(rotation)
direction = (forward + right * x + up * z).normal()
out = []
start = location
for _ in range(12):
    hit = unreal.SystemLibrary.line_trace_single(wl.world(), start, start + direction * 30000.0,
                                                 unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [],
                                                 unreal.DrawDebugTrace.NONE, True)
    if hit is None:
        break
    data = hit.to_tuple()
    record = dict(zip(("blocking", "initial_overlap", "time", "distance", "location", "impact_point", "normal",
                       "impact_normal", "phys_mat", "actor", "component", "bone", "bone2", "item", "element",
                       "face", "trace_start", "trace_end"), data))
    component = record["component"]
    actor = record["actor"]
    materials = []
    if component is not None and hasattr(component, "get_materials"):
        for material in component.get_materials():
            if material is None:
                continue
            base = material.get_base_material()
            materials.append([material.get_name(), bool(base.get_editor_property("two_sided")),
                              str(base.get_editor_property("blend_mode"))])
    normal = record["impact_normal"]
    out.append({"actor": actor.get_actor_label() if actor else None,
                "level": actor.get_outer().get_outer().get_name() if actor else None,
                "distance_m": round((record["impact_point"] - location).length() / 100.0, 2),
                "faces_camera": bool(normal.dot(direction) < 0.0),
                "materials": materials[:4], "material_count": len(materials)})
    start = record["impact_point"] + direction * 2.0
json.dumps(out)
