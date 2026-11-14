"""Phase 17: the skyline and Zone 1 tables for phase17_results.md, from the checker's outputs.

Usage: python -B -P phase17_tables.py <out markdown>
Reads the clean-roof rebuild (meshes_*_clean, review/phase17/*_check_clean.csv, J22 onward).
Skyline towers: beyond 1 km and 60 m or taller to the top (the acceptance's "towers inside the view").
Zone 1: the 23 county buildings within 40 m of the lot centre.
"""

import csv
import json
import sys

DOCS = r"E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland"
DATA = r"E:\Wieland1529_site_data\phase17"


def f(v, nd=2):
    try:
        return ("%." + str(nd) + "f") % float(v)
    except (TypeError, ValueError):
        return "-"


def err(a, b):
    try:
        return float(a) - float(b)
    except (TypeError, ValueError):
        return None


def main(out):
    names = {r["bldg_id"]: r["name"] for r in csv.DictReader(open(DATA + r"\tower_materials.csv", encoding="utf-8"))}
    recs = {}
    for line in open(DATA + r"\meshes_towers_clean\towers_record.jsonl", encoding="utf-8"):
        r = json.loads(line)
        recs[r["id"]] = r
    rows = list(csv.DictReader(open(DOCS + r"\review\phase17\tower_check_clean.csv", encoding="utf-8")))
    sky = [r for r in rows if float(r["distance_m"]) >= 1000 and float(recs.get(r["id"], {}).get("top_incl_masts_m", 0) or 0) >= 60]
    sky.sort(key=lambda r: -float(recs[r["id"]]["top_incl_masts_m"]))
    lines = ["| Tower (county id) | Distance (m) | Main roof modelled (m) | Measured (m) | Error (m) | Highest structure modelled (m) | Measured (m) | Error (m) | Top incl. masts (m) | Mast error (m) | Plan edge mean (m) | Built form |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    stats = {"n": len(sky), "with_returns": 0, "roof_1m": 0, "roof_n": 0, "high_1m": 0, "high_n": 0, "plan_2m": 0, "plan_n": 0, "mast_1m": 0, "mast_n": 0}
    for r in sky:
        has = r["returns"] not in ("", "0") and float(r.get("coverage") or 0) > 0
        e_roof = err(r["roof_model_m"], r["roof_measured_m"]) if has else None
        hi_meas = r.get("highest_return_4m2_m") or r["highest_return_not_mast_m"]
        e_high = err(r["highest_model_not_mast_m"], hi_meas) if has else None
        masts = [float(x) for x in r["mast_err_m"].split(";") if x not in ("",)] if has and r["mast_err_m"] else []
        plan = float(r["upper_edge_mean_m"]) if has and r["upper_edge_mean_m"] else None
        if has:
            stats["with_returns"] += 1
        if e_roof is not None:
            stats["roof_n"] += 1
            stats["roof_1m"] += abs(e_roof) <= 1.0
        if e_high is not None:
            stats["high_n"] += 1
            stats["high_1m"] += abs(e_high) <= 1.0
        if plan is not None:
            stats["plan_n"] += 1
            stats["plan_2m"] += plan <= 2.0
        for m in masts:
            stats["mast_n"] += 1
            stats["mast_1m"] += abs(m) <= 1.0
        name = names.get(r["id"]) or "unnamed"
        lines.append("| %s (%s) | %.0f | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            name, r["id"], float(r["distance_m"]), f(r["roof_model_m"]), f(r["roof_measured_m"]) if has else "no returns",
            f(e_roof) if e_roof is not None else "-", f(r["highest_model_not_mast_m"]), f(hi_meas) if has else "-",
            f(e_high) if e_high is not None else "-", f(recs[r["id"]]["top_incl_masts_m"]),
            ", ".join(f(m) for m in masts) if masts else "-", f(plan) if plan is not None else "-", recs[r["id"]]["form"]))
    z = list(csv.DictReader(open(DOCS + r"\review\phase17\zone12_check_clean.csv", encoding="utf-8")))
    zones = json.load(open(DATA + r"\zones_zone12.json", encoding="utf-8"))
    zm = {r["bldg_id"]: r for r in csv.DictReader(open(DATA + r"\zone12_materials_v2.csv", encoding="utf-8"))}
    z1 = [r for r in z if str(zones.get(r["id"])) == "1"]
    z1.sort(key=lambda r: float(r["distance_m"]))
    zrec = {}
    for line in open(DATA + r"\meshes_zone12_clean\towers_record.jsonl", encoding="utf-8"):
        rr = json.loads(line)
        zrec[rr["id"]] = rr
    zl = ["| Building (county id) | Distance (m) | Main roof modelled (m) | Measured (m) | Error (m) | Highest point modelled (m) | Measured, items of 4 sq m or more (m) | Error (m) | Free-wall plan mean (m) | Built form | Wall material (source) | Colour |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    zs = {"n": len(z1), "roof_03": 0, "high_03": 0, "plan_03": 0, "plan_n": 0}
    for r in z1:
        e_roof = err(r["roof_model_m"], r["roof_measured_m"])
        hz = r.get("highest_return_4m2_m") or r["highest_return_not_mast_m"]
        e_high = err(r["highest_model_not_mast_m"], hz)
        zs["roof_03"] += e_roof is not None and abs(e_roof) <= 0.3
        zs["high_03"] += e_high is not None and abs(e_high) <= 0.3
        if r["free_edge_mean_m"]:
            zs["plan_n"] += 1
            zs["plan_03"] += float(r["free_edge_mean_m"]) <= 0.3
        m = zm.get(r["id"], {})
        src = "Assessor" if "Assessor" in m.get("wall_material_source", "") else ("OSM" if "OpenStreetMap" in m.get("wall_material_source", "") else "assumed")
        zl.append("| %s (%s) | %.0f | %s | %s | %s | %s | %s | %s | %s | %s | %s (%s) | %s, assumed |" % (
            m.get("name") or "unnamed", r["id"], float(r["distance_m"]), f(r["roof_model_m"]), f(r["roof_measured_m"]), f(e_roof),
            f(r["highest_model_not_mast_m"]), f(hz), f(e_high), f(r["free_edge_mean_m"]), zrec.get(r["id"], {}).get("form", ""),
            m.get("wall_material", ""), src, m.get("wall_colour_hex", "")))
    with open(out, "w", encoding="utf-8", newline="\n") as h:
        h.write("# Phase 17 tables\n\nCompanion to `phase17_results.md`. Heights are above the scan's ground at each building; \"measured\" is the 2022 point cloud (median of flat roof returns for the main roof; for the highest point, the highest returns of an item of 4 sq m or more, the size the roof rule builds; masts apart). Plan: mean distance between the model's and the returns' outlines over the levels seen from the decks (skyline) or along free walls (Zone 1).\n\n")
        h.write("## Skyline towers (beyond 1 km, 60 m or taller)\n\n" + json.dumps(stats) + "\n\n" + "\n".join(lines) + "\n\n")
        h.write("## Zone 1 buildings\n\n" + json.dumps(zs) + "\n\n" + "\n".join(zl) + "\n")
    print(json.dumps({"skyline": stats, "zone1": zs}))


if __name__ == "__main__":
    main(sys.argv[1])
