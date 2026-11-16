"""Offline source audit of the restored immediate neighbours; never imports unreal.

Run from any directory. Reconstructs the Phase 7 fit only (raw+shift+lift,
removed triangles), so later fitted-mesh repairs require a native dump for
verification. Writes audit_source.json/csv beside the current review images.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from shapely import contains_xy
from shapely.geometry import Polygon
from shapely.ops import unary_union

from wieland_geo import LevelFrame

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "review/phase20/nearby_detail/neighbours"
SHIFT = np.array([15482.32, 5053.7, 0.0])
IDS = {780226: "1533 north", 781632: "1525 south"}


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as h:
        return list(csv.DictReader(h))


def rounded(a):
    return np.round(a, 3).tolist()


def raster_triangles(coords, points):
    """Top intersections of explicit triangles at supplied XY points; no editor."""
    top = np.full(len(points), np.nan)
    for q in coords:
        a, b, c = q
        v0, v1 = b[:2]-a[:2], c[:2]-a[:2]
        den = v0[0]*v1[1]-v0[1]*v1[0]
        if abs(den) < 1e-8:
            continue
        v2 = points-a[:2]
        u = (v2[:,0]*v1[1]-v2[:,1]*v1[0])/den
        v = (v0[0]*v2[:,1]-v0[1]*v2[:,0])/den
        inside = (u >= -1e-9) & (v >= -1e-9) & (u+v <= 1+1e-9)
        z = a[2]+u*(b[2]-a[2])+v*(c[2]-a[2])
        top[inside] = np.fmax(top[inside],z[inside])
    return top


def roof_controls():
    result = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "pointwise roof control, existing permitted 2022 measured clean-roof model; no geometry changes",
        "survey_authority": "August2025 plat governs horizontal neighbour wall ties. No neighbour roof elevations were found in the recorded survey ties; county Height is the highest point minus ground, not the main roof level.",
        "sampling": "25cm XY grid only where both legacy and measured clean roof have a triangle; heights in level centimetres",
        "roof_material_review": {
            "image": "1533_roof_repaired_saved_realtime.0000.png",
            "verdict": "FAIL: long streaks remain; image texture changed across precisely the targeted foreground roof, confirming slot4 is the visible surface",
            "code_evidence": "wieland_parents.py _WORLD_UV picks projection from VertexNormalWS. It uses XY for a Z-facing normal, otherwise XZ/YZ. Native geometric triangle normals are nearly vertical, but imported vertex-normal overlay was not dumped.",
            "diagnosis": "Suspected inherited vertex normals choose a wall projection: only69cm Z variation is then spread across24m roof. This is a testable hypothesis, not a runtime-normal measurement.",
            "next_test": "Roof-only parent using explicit world XY texture coordinates, independent of VertexNormalWS; colour map, rotated/scaled second sample, non-repeating cloud blend, roughness, modest relief. Do not modify the shared Opaque parent. Readback and neutral/grazing render required.",
        },
        "neighbours": [],
    }
    for oid, part, slot in [(780226,"R15_PART_opaque_xm05_yp01_part01",4),(781632,"R15_PART_opaque_xm04_yp01_part01",3)]:
        raw = np.load(ROOT / "review/phase7/fit/raw" / (part+".npz"))
        plan = np.load(ROOT / "review/phase7/fit/plan" / (part+".npz"))
        p = raw["positions"]+SHIFT
        p[:,2] += plan["lift"]
        keep = np.ones(len(raw["triangles"]),dtype=bool)
        keep[plan["remove"]] = False
        sel = keep & (raw["material_ids"]==slot)
        legacy = p[raw["triangles"][sel]]
        clean_path = Path("E:/Wieland1529_site_data/phase17/meshes_zone12_clean") / ("P17RZ_"+str(oid)+".json")
        clean = json.loads(clean_path.read_text())
        v = np.array(clean["vertices"])+np.array(clean["pivot"])
        t = np.array(clean["triangles"])
        m = np.array(clean["tri_mat"])
        measured = v[t[m==1]]
        x0,y0 = legacy[:,:,:2].min(axis=(0,1))
        x1,y1 = legacy[:,:,:2].max(axis=(0,1))
        xx,yy = np.meshgrid(np.arange(x0+12.5,x1,25),np.arange(y0+12.5,y1,25))
        xy = np.column_stack([xx.ravel(),yy.ravel()])
        old_top = raster_triangles(legacy,xy)
        new_top = raster_triangles(measured,xy)
        both = np.isfinite(old_top)&np.isfinite(new_top)
        cross = np.cross(legacy[:,1]-legacy[:,0],legacy[:,2]-legacy[:,0])
        nz = np.abs(cross[:,2])/np.linalg.norm(cross,axis=1)
        def stats(z):
            z=z[np.isfinite(z)]
            return {"samples":len(z),"p10_cm":round(float(np.percentile(z,10)),2),"median_cm":round(float(np.median(z)),2),"p90_cm":round(float(np.percentile(z,90)),2),"maximum_abs_cm":round(float(np.abs(z).max()),2)} if len(z) else None
        item = {"object_id":oid,"name":IDS[oid],"clean_mesh_source":str(clean_path),"legacy_roof_slot":slot,
                "legacy_roof_geometric_normal_absZ":rounded(nz),"legacy_roof_z_extent_cm":rounded(np.array([legacy[:,:,2].min(),legacy[:,:,2].max()])),
                "clean_roof_z_extent_cm":rounded(np.array([measured[:,:,2].min(),measured[:,:,2].max()])),
                "legacy_minus_full_measured_roof":stats(old_top[both]-new_top[both]),"common_sampled_area_sq_m":round(float(both.sum())*.0625,3)}
        if oid==781632:
            # Verified from P17RZ_781632.json: first four triangles form its two main gable planes.
            main = v[t[:4]]
            main_top = raster_triangles(main,xy)
            same = both & np.isfinite(main_top)
            addon = same & (new_top-main_top>30)
            base_only = same & ~addon
            item.update({"main_gable_clean_triangle_indices":[0,1,2,3],"main_gable_clean_z_extent_cm":rounded(np.array([main[:,:,2].min(),main[:,:,2].max()])),
                         "legacy_minus_measured_main_gable_only":stats(old_top[base_only]-main_top[base_only]),
                         "common_samples_under_measured_addons":int(addon.sum()),"common_addon_sample_area_sq_m":round(float(addon.sum())*.0625,3),
                         "legacy_minus_addon_tops":stats(old_top[addon]-new_top[addon]),
                         "recommendation":"Do not raise the complete building by1.02m. That scalar median conflates missing raised roof features and the main gable. Fit main planes and measured rooftop additions separately; preserve surveyed walls/foot and detailed facade. Current measured clean roof has two raised structures absent from legacy roof; do not infer their exact facade finish or openings."})
        else:
            item["recommendation"] = "A real main flat-roof height mismatch remains. On new copies only, correct roof/upper facade/glass/coping together to the measured flat roof near1364.14cm; preserve foot, surveyed XY walls, stoops and fences. Ground-anchored vertical mapping of isolated building geometry avoids moving the merged tile and disconnected window pieces. Preserve parapet relative thickness as a labelled model assumption; thin parapet height is not resolved by the old scan. Validate 0.3m pointwise roof agreement and facade continuity."
        result["neighbours"].append(item)
    path = OUT / "audit_roof_controls.json"
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    county_path = Path("E:/Wieland1529_site_data/county_footprints_2022.json")
    county = json.loads(county_path.read_text())
    frame = LevelFrame.load(str(ROOT / "review/phase2/level_frame.json"))
    site = json.loads((ROOT / "review/phase2/site_analysis.json").read_text())
    lot = Polygon([(site["governing_lot"]["corners"][n]["level_x_cm"],
                    site["governing_lot"]["corners"][n]["level_y_cm"])
                   for n in ["south_west", "north_west", "north_east", "south_east"]])
    swaps = {a["part"]: a for a in read_csv(ROOT / "review/phase7/r15_fit_swaps.csv")}
    historical = {a["building"]: a for a in read_csv(ROOT / "review/phase10/neighbours_now.csv")}
    materials = read_csv(ROOT / "review/phase7/audit_fixes.csv")
    ties = read_csv(ROOT / "review/phase10/survey_ties_now.csv")
    features = {f["attributes"]["OBJECTID"]: f for f in county["features"] if f["attributes"]["OBJECTID"] in IDS}
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "offline cache audit; no editor state changed, no native originals changed",
        "roof_repair_status": "PENDING root native material apply, readback and visual neutral/grazing review; no geometry shift",
        "source_policy": "County 2022 footprints, 2022 scan-derived project audits and existing model geometry only. No Google content, no external imagery, no invented physical-site detail. Render appearance is evidence of model condition, not evidence of the real building's condition.",
        "coordinate_frame": "level centimetres; north -X east -Y; raw vertices plus SHIFT plus per-vertex fit lift",
        "source_limit": "Phase7 raw+fit reconstruction excludes later16-triangle1525 siding backing repair. Native fitted mesh dump required before changing material IDs or judging latest geometry.",
        "sources": [str(p) for p in [county_path, ROOT / "review/phase7/fit/raw", ROOT / "review/phase7/fit/plan", ROOT / "review/phase7/audit_fixes.csv", ROOT / "review/phase10/neighbours_now.csv", ROOT / "review/phase10/survey_ties_now.csv"]],
        "review_findings": [
            {"view": "1533_roof_realtime", "kind": "material defect", "finding": "Long stretched/streaky roof texture visible across large flat roof; replace roof material on placed copy with a colour-map world-mapped material and grazing-light review. Native dump confirms all slot4 triangles belong to this roof; a component override is sufficient."},
            {"view": "1533_lot_side_realtime", "kind": "camera issue", "finding": "Wall fills image; no wall perimeter or lot tie visible. Retake with whole wall and survey corners in frame."},
            {"view": "1525_lot_side_realtime", "kind": "camera issue", "finding": "Dark lap-siding close-up without edges; insufficient framing for geometry acceptance."},
            {"view": "1525_roof_realtime", "kind": "camera issue", "finding": "Project wall blocks the neighbour roof. Hide project for diagnostic view then restore visibility exactly."},
            {"view": "1533_street_realtime / 1525_street_realtime", "kind": "retained detail", "finding": "Windows, trim, brick/slats, stoops and railings are modelled. Tree occlusion prevents full facade assessment. No physical-site accuracy claim from these renders."},
        ],
        "neighbours": [],
        "minimal_repair_plan": [
            "Fix diagnostic cameras before accepting geometry; project visibility changed only temporarily and restored.",
            "Native dump confirms slot4 contains only the1533 roof: component material override slot4 is sufficient. Preserve every other slot and existing placed brick overrides. Mesh clone is unnecessary for this material repair.",
            "Use world mapping, colour map, non-repeating detail, neutral+grazing proof; no inferred roof plant or physical details without permitted source.",
            "Re-read native mesh counts, triangle positions and original package hashes; geometry must be unchanged by roof-material repair. If cloning is nevertheless chosen, append slot31 and assign only native triangle IDs7534-7537.",
            "Keep measured height mismatches visible as limitations. No geometry shift in this repair; do not move the whole merged tile to resolve a per-building height discrepancy.",
        ],
        "checks": [
            "Original assets unchanged; copied mesh vertex positions and triangle indices byte-equal to fitted source for material-only repair.",
            "Material IDs outside selected1533 roof triangles byte-equal;1537 roof and all other buildings in merged part unchanged.",
            "1533 south wall on X=-1508.76cm;1525 north wall follows survey ties(20.7,-198.4) and(11.3,-1679.5)cm. Judge walls, not coping/eaves.",
            "No new projected triangle area inside governing lot beyond the existing baseline; compare native dump before/after.",
            "If height correction is done: rerasterise roof at0.5m, compare median only where scan and model both have building, limit0.3m; separately assess pitched roof ridge and dormer against building returns, excluding vegetation.",
        ],
    }
    flat = []
    for oid, title in IDS.items():
        feature = features[oid]
        xy = [frame.level_from_map(*p)[:2] for p in feature["geometry"]["rings"][0]]
        polygon = Polygon(xy)
        search = polygon.buffer(30.0)
        region = {
            "object_id": oid, "name": title, "county_attributes": feature["attributes"],
            "county_roof_outline_level_cm": rounded(np.array(xy)),
            "county_outline_intrusion_into_governing_lot_sq_m": round(polygon.intersection(lot).area / 10000, 5),
            "historical_phase10_fitted_vs_lidar": historical.get("SB_" + str(oid)),
            "historical_survey_ties": [a for a in ties if str(title[:4]) in a["tie"]],
            "prior_repair_records": [a for a in materials if title[:4] in str(a)],
            "cached_parts": [],
        }
        for raw_path in sorted((ROOT / "review/phase7/fit/raw").glob("R15_PART_*.npz")):
            part = raw_path.stem
            plan_path = ROOT / "review/phase7/fit/plan" / raw_path.name
            if not plan_path.exists():
                continue
            raw = np.load(raw_path)
            p = raw["positions"].copy() + SHIFT
            plan = np.load(plan_path)
            p[:, 2] += plan["lift"]
            tri = raw["triangles"]
            keep = np.ones(len(tri), dtype=bool)
            keep[plan["remove"]] = False
            tri_ids = np.flatnonzero(keep)
            t = tri[keep]
            centers = p[t].mean(axis=1)
            selected = contains_xy(search, centers[:, 0], centers[:, 1])
            if not selected.any():
                continue
            t = t[selected]
            raw_ids = tri_ids[selected]
            coords = p[t]
            mm = raw["material_ids"][raw_ids]
            cross = np.cross(coords[:, 1] - coords[:, 0], coords[:, 2] - coords[:, 0])
            areas = np.linalg.norm(cross, axis=1) / 2
            nz = np.abs(cross[:, 2]) / np.maximum(np.linalg.norm(cross, axis=1), 1e-9)
            item = {"part": part, "fitted_mesh": swaps.get(part, {}).get("fitted_mesh"),
                    "selected_by": "triangle centroid within county roof outline +30cm; search only, not legal/survey classification",
                    "selected_triangles": len(t), "bbox_cm": rounded(np.array([coords.min(axis=(0,1)), coords.max(axis=(0,1))])), "slots": []}
            for slot in np.unique(mm):
                index = int(slot)
                mask = mm == slot
                sn = str(raw["slot_names"][index])
                roof = mask & (nz > 0.7) & (coords.min(axis=1)[:,2] > 500)
                entry = {"slot": index, "name": sn, "source_material": str(raw["slot_materials"][index]),
                         "selected_triangles": int(mask.sum()), "surface_area_sq_m": round(float(areas[mask].sum()/10000), 4),
                         "all_kept_slot_triangles": int((raw["material_ids"][keep] == index).sum()),
                         "bbox_cm": rounded(np.array([coords[mask].min(axis=(0,1)), coords[mask].max(axis=(0,1))]))}
                if "roof" in sn.lower() or "shingle" in sn.lower():
                    ids = raw_ids[roof]
                    roof_polys = [Polygon(x[:, :2]) for x in coords[roof] if Polygon(x[:, :2]).area > 0]
                    entry.update({"roof_raw_triangle_ids": ids.tolist(),
                                  "roof_candidates": len(ids), "roof_union_projected_area_sq_m": round(unary_union(roof_polys).area/10000, 4) if roof_polys else 0,
                                  "roof_candidate_bbox_cm": rounded(np.array([coords[roof].min(axis=(0,1)),coords[roof].max(axis=(0,1))])) if roof.any() else None})
                item["slots"].append(entry)
                flat.append({"object_id":oid,"neighbour":title,"part":part,"slot":index,"name":sn,"source_material":entry["source_material"],"selected_triangles":entry["selected_triangles"],"all_kept_slot_triangles":entry["all_kept_slot_triangles"],"surface_area_sq_m":entry["surface_area_sq_m"]})
            region["cached_parts"].append(item)
        report["neighbours"].append(region)
    native_path = OUT / "audit_current_1533_opaque.npz"
    if native_path.exists():
        native = np.load(native_path)
        p = native["positions"] + SHIFT
        tri, ids = native["triangles"], native["material_ids"]
        sel = np.flatnonzero(ids == 4)
        q = p[tri[sel]]
        roof_union = unary_union([Polygon(t[:, :2]) for t in q])
        polygon = Polygon(report["neighbours"][0]["county_roof_outline_level_cm"])
        raw = np.load(ROOT / "review/phase7/fit/raw/R15_PART_opaque_xm05_yp01_part01.npz")
        raw_roof = raw["positions"][raw["triangles"][raw["material_ids"] == 4]]
        plan = np.load(ROOT / "review/phase7/fit/plan/R15_PART_opaque_xm05_yp01_part01.npz")
        reconstructed = raw["positions"] + SHIFT
        reconstructed[:,2] += plan["lift"]
        keep = np.ones(len(raw["triangles"]), dtype=bool)
        keep[plan["remove"]] = False
        cached_tri_positions = reconstructed[raw["triangles"][keep]]
        native_tri_positions = p[tri]
        maximum_delta = float(np.max(np.abs(cached_tri_positions-native_tri_positions))) if cached_tri_positions.shape == native_tri_positions.shape else None
        report["native_1533_roof_contract"] = {
            "native_dump": str(native_path),
            "file_sha256": hashlib.sha256(native_path.read_bytes()).hexdigest(),
            "array_sha256": {k: hashlib.sha256(np.ascontiguousarray(native[k]).tobytes()).hexdigest() for k in native.files},
            "vertex_count": len(p), "triangle_count": len(tri), "slot_count": len(native["slot_names"]),
            "slot": 4, "slot_name": str(native["slot_names"][4]), "source_material": str(native["slot_materials"][4]),
            "maximum_cached_fit_to_native_triangle_vertex_difference_cm": maximum_delta,
            "all_triangle_indices_in_slot": sel.tolist(),
            "triangle_world_coordinates_cm": rounded(q),
            "roof_projected_area_sq_m": round(roof_union.area/10000,4),
            "roof_inside_county_outline_sq_m": round(roof_union.intersection(polygon).area/10000,4),
            "roof_outside_county_outline_sq_m": round(roof_union.difference(polygon).area/10000,4),
            "roof_inside_governing_lot_sq_m": round(roof_union.intersection(lot).area/10000,8),
            "fitted_roof_z_extent_cm": rounded(np.array([q[:,:,2].min(),q[:,:,2].max()])),
            "pre_fit_source_roof_z_extent_cm": rounded(np.array([raw_roof[:,:,2].min(),raw_roof[:,:,2].max()])),
            "interpretation": "The native roof has a 68.99 cm height spread while its pre-fit source roof was horizontal. This follows the per-vertex smooth-ground fit and is not a measured roof slope. Historical raster roof mismatch is +1.10 m versus the 2022 scan. No height correction is made by this audit.",
            "preferred_operation": "set_material(4,new_roof_material) on placed fitted actor only; snapshot/readback every material override and preserve slots0/1 brick overrides",
            "copy_only_alternative": "duplicate current fitted StaticMesh to new package, preserve original31 slots and all arrays, append roof material at31, change material_ids only at7534..7537 from4 to31, preserve component overrides when swapping placed copy",
            "forbidden_operation": "global material replacement or original imported/production asset mutation",
            "acceptance": "material-only change: position/triangle hashes identical; slot4 only override changed; original31 mesh slot/material arrays untouched; close+wide+grazing review pending",
        }
    path = OUT / "audit_source.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    with (OUT / "audit_slots.csv").open("w", newline="", encoding="utf-8") as h:
        writer = csv.DictWriter(h, fieldnames=list(flat[0]))
        writer.writeheader()
        writer.writerows(flat)
    print(json.dumps({"written": [str(path), str(OUT / "audit_slots.csv")], "neighbours": [{"name":n["name"], "parts":len(n["cached_parts"]), "roof_slots":[{"part":p["part"], **s} for p in n["cached_parts"] for s in p["slots"] if "roof" in s["name"].lower() or "shingle" in s["name"].lower()]} for n in report["neighbours"]],"native_roof":report.get("native_1533_roof_contract")}, indent=2))


if __name__ == "__main__":
    main()
    print(json.dumps(roof_controls(),indent=2))
