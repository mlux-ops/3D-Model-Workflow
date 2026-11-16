"""Phase 7, step 7.1, off line: what each Phase 4 building gets as a stand-in material.

Reads   review/phase4/surroundings_manifest.json     the 144 Phase 4 buildings (ground, roof heights, footprint)
        review/phase7/buildings_compare.csv          which of them the earlier detailed buildings cover
        review/phase7/heights/p4b/*.json, *.f32      each building's top surface on 0.5 m cells (step J3)
        review/phase7/ground/cover.npz               the roadway (step J7), to tell which way a building fronts
        review/phase7/ground/sources.npz             the 2025 aerial photograph in the level frame (roof colour)
Writes  review/phase7/phase4_building_materials.csv  one line per building: what it gets and why
        review/phase7/massing/plan.json              the same as numbers, for tools/wieland_massing.py

Nothing here is evidence of what a building looks like, apart from three things that are measured: the height of
the walls (2022 laser scan), which way the building fronts (nearest roadway) and the mean colour of its roof in the
2025 aerial photograph. Wall material, window size and spacing follow a fixed rule from height and footprint, with
a fixed draw from the building's county number so that the street is not all one brick. Every building dressed
this way is a stand-in "from data, not from a photograph".

Run:  python -B tools/phase7_massing.py
"""

import csv
import hashlib
import json
import os

import numpy as np
from scipy import ndimage

ROOT = "review/phase7"
OUT = ROOT + "/massing"
NONE = -99999.0
POLYHAVEN = "/Game/Wieland/R15_Materials/PolyHaven"
PHASE5 = "/Game/Wieland1529/Materials/Textures"

# family: (colour image, relief image, roughness image, roughness is in the red channel, size u m, size v m, tint, words)
FAMILIES = {
    "red brick": (POLYHAVEN + "/factory_brick/T_R15_factory_brick_BaseColor", POLYHAVEN + "/factory_brick/T_R15_factory_brick_Normal",
                  POLYHAVEN + "/factory_brick/T_R15_factory_brick_ARM", 0, 1.0, 1.0, (0.95, 0.80, 0.74),
                  "Poly Haven factory_brick (CC0), one repeat 1.0 m (13 courses counted)"),
    "red brick 2": (PHASE5 + "/T_W1529_Bricks086_C", PHASE5 + "/T_W1529_Bricks086_N", PHASE5 + "/T_W1529_Bricks086_R", 1, 2.6, 1.3,
                    (1.0, 1.0, 1.0), "ambientCG Bricks086 (CC0), 2.6 by 1.3 m as in Phase 5"),
    "dark brick": (POLYHAVEN + "/brick_wall_08/T_R15_brick_wall_08_BaseColor", POLYHAVEN + "/brick_wall_08/T_R15_brick_wall_08_Normal",
                   POLYHAVEN + "/brick_wall_08/T_R15_brick_wall_08_ARM", 0, 2.05, 2.05, (1.0, 0.88, 0.80),
                   "Poly Haven brick_wall_08 (CC0), one repeat 2.05 m (27 courses counted), tinted warm"),
    "common brick": (POLYHAVEN + "/yellow_brick/T_R15_yellow_brick_BaseColor", POLYHAVEN + "/yellow_brick/T_R15_yellow_brick_Normal",
                     POLYHAVEN + "/yellow_brick/T_R15_yellow_brick_ARM", 0, 2.5, 2.5, (0.92, 0.88, 0.84),
                     "Poly Haven yellow_brick (CC0), one repeat 2.5 m (33 courses counted)"),
    "limestone": (POLYHAVEN + "/white_sandstone_blocks_02/T_R15_white_sandstone_blocks_02_BaseColor",
                  POLYHAVEN + "/white_sandstone_blocks_02/T_R15_white_sandstone_blocks_02_Normal",
                  POLYHAVEN + "/white_sandstone_blocks_02/T_R15_white_sandstone_blocks_02_ARM", 0, 2.1, 2.1, (0.86, 0.87, 0.88),
                  "Poly Haven white_sandstone_blocks_02 (CC0), one repeat 2.1 m (7 courses of 30 cm), tinted grey"),
    "concrete": (PHASE5 + "/T_W1529_Concrete046_C", PHASE5 + "/T_W1529_Concrete046_N", PHASE5 + "/T_W1529_Concrete046_R", 1, 2.4, 2.4,
                 (0.85, 0.85, 0.84), "ambientCG Concrete046 (CC0), 2.4 m as in Phase 5"),
    "siding": (PHASE5 + "/T_W1529_White", PHASE5 + "/T_W1529_Siding_N", PHASE5 + "/T_W1529_WhiteLinear", 0, 1.0, 0.1778,
               (0.62, 0.62, 0.58), "own relief of lap siding, one course 7 in (Phase 5), flat colour"),
}
SIDING_TINTS = [(0.62, 0.62, 0.58), (0.50, 0.53, 0.56), (0.70, 0.66, 0.55), (0.42, 0.46, 0.42), (0.74, 0.74, 0.72)]
FRAMES = [("dark bronze", (0.035, 0.03, 0.028)), ("white", (0.68, 0.68, 0.66)), ("black", (0.015, 0.015, 0.015))]


def draws(object_id, count=12):
    """Fixed numbers between 0 and 1 from the building's county number."""
    digest = hashlib.md5(("W1529-%d" % object_id).encode("ascii")).digest()
    return [digest[k] / 255.0 for k in range(count)]


def to_linear(value):
    value = value / 255.0
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def pick(value, table):
    total = 0.0
    for name, share in table:
        total += share
        if value <= total:
            return name
    return table[-1][0]


def main():
    os.makedirs(OUT, exist_ok=True)
    with open("review/phase4/surroundings_manifest.json", encoding="utf-8") as handle:
        manifest = json.load(handle)
    with open(ROOT + "/buildings_compare.csv", encoding="utf-8", newline="") as handle:
        covered = {row["phase4_building"]: row["covered"] == "yes" for row in csv.DictReader(handle)}
    cover = np.load(ROOT + "/ground/cover.npz")
    sources = np.load(ROOT + "/ground/sources.npz")
    x0, y0, step = float(cover["x0"]), float(cover["y0"]), float(cover["step"])
    road = cover["road"]
    n_i, n_j = road.shape
    # For every cell: where the nearest roadway cell is.
    _, nearest = ndimage.distance_transform_edt(~road, return_indices=True)
    ortho = sources["ortho"]
    # The aerial photograph is sunlit, not a measure of colour: its roadway is taken as asphalt (0.07 linear)
    # and every roof is scaled by the same factor.
    on_road = road & (ortho[:, :, 3] > 0)
    road_mean = [to_linear(float(np.mean(ortho[:, :, k][on_road]))) for k in range(3)]
    photo_factor = 0.07 / (0.3 * road_mean[0] + 0.59 * road_mean[1] + 0.11 * road_mean[2])
    print("photo factor %.3f" % photo_factor)
    plan, rows = {}, []
    for building in manifest["buildings"]:
        name, object_id = building["name"], building["object_id"]
        with open(ROOT + "/heights/p4b/" + name + ".json", encoding="utf-8") as handle:
            header = json.load(handle)
        tops = np.fromfile(ROOT + "/heights/p4b/" + name + ".f32", dtype=np.float32).reshape(header["ni"], header["nj"])
        ii, jj = np.nonzero(tops > NONE + 1.0)
        xs = (header["i0"] + ii + 0.5) * header["cell_cm"]
        ys = (header["j0"] + jj + 0.5) * header["cell_cm"]
        ci = np.clip(((xs - x0) / step).astype(int), 0, n_i - 1)
        cj = np.clip(((ys - y0) / step).astype(int), 0, n_j - 1)
        centre_i, centre_j = int(np.median(ci)), int(np.median(cj))
        to_road_x = (nearest[0][centre_i, centre_j] - centre_i) * step
        to_road_y = (nearest[1][centre_i, centre_j] - centre_j) * step
        front_x = 1.0 if abs(to_road_x) > abs(to_road_y) else 0.0
        seen = ortho[ci, cj, 3] > 0
        if seen.sum() >= 8:
            mean = [float(np.mean(ortho[ci[seen], cj[seen], k])) for k in range(3)]
        else:
            mean = [90.0, 88.0, 86.0]
        linear = [to_linear(v) for v in mean]
        grey = 0.3 * linear[0] + 0.59 * linear[1] + 0.11 * linear[2]
        roof = [round(min(max(photo_factor * (0.7 * v + 0.3 * grey), 0.03), 0.30), 3) for v in linear]

        ground = building["ground_cm"]
        height = (building["roof_typical_cm"] - ground) / 100.0
        wall_top = (building["roof_typical_cm"] - ground) / 100.0 - 0.3
        footprint = building["footprint_sq_m"]
        d = draws(object_id)
        windows, side, why = 1.0, 0.0, ""
        if height >= 28.0:
            family = "concrete"
            floor, period, width, tall, sill = 3.0, 3.0, 2.2, 1.7, 0.85
            side = 1.0
            why = "taller than 28 m: concrete frame with wide windows on all sides"
        elif footprint < 70.0 and height < 5.5:
            family = pick(d[0], [("common brick", 0.5), ("siding", 0.3), ("red brick", 0.2)])
            floor, period, width, tall, sill = 3.2, 2.4, 1.0, 1.2, 1.0
            windows = 0.0
            why = "under 70 m2 and under 5.5 m: garage or coach house, no windows drawn"
        else:
            table = [("red brick", 0.35), ("red brick 2", 0.20), ("dark brick", 0.15), ("common brick", 0.12), ("limestone", 0.10),
                     ("siding", 0.08)]
            family = pick(d[0], table)
            if family == "siding" and (height >= 11.0 or footprint >= 220.0):
                family = "red brick"
            floor = 3.3 if height >= 7.5 else max(2.7, height / max(1.0, round(height / 3.0)))
            period = 2.2 + 0.6 * d[1]
            width = 1.0 + 0.2 * d[2]
            tall, sill = 1.8, 0.8
            if footprint > 500.0 or height > 20.0:
                side = 1.0
                why = "house or flats in masonry by a fixed draw; large or tall, so windows on all sides"
            else:
                why = "house or flats in masonry by a fixed draw; windows on the street and rear walls only"
        colour_map, normal_map, rough_map, rough_red, size_u, size_v, tint, words = FAMILIES[family]
        if family == "siding":
            tint = SIDING_TINTS[int(d[3] * 4.999)]
        shade = 0.88 + 0.22 * d[4]
        tint = [round(tint[0] * shade * (0.98 + 0.04 * d[5]), 3), round(tint[1] * shade, 3), round(tint[2] * shade * (0.98 + 0.04 * d[6]), 3)]
        frame_name, frame = FRAMES[0 if d[7] < 0.5 else (1 if d[7] < 0.85 else 2)]
        if family == "siding":
            frame_name, frame = FRAMES[1]
        stone = list(frame) if family == "siding" else [0.60, 0.58, 0.53]
        plan[name] = {
            "object_id": object_id, "covered_by_earlier": bool(covered.get(name, False)), "family": family,
            "scalars": {
                "BaseZ_cm": round(ground, 1), "WallTop_m": round(wall_top, 2), "FrontX": front_x, "SideWindows": side,
                "WindowAmount": windows, "FloorHeight_m": round(floor, 2), "WindowPeriod_m": round(period, 2),
                "WindowWidth_m": round(width, 2), "WindowHeight_m": tall, "Sill_m": sill, "WindowOffset_m": round(d[8] * period, 2),
                "Seed": round(d[9] * 97.0, 2), "Wall_SizeU_m": size_u, "Wall_SizeV_m": size_v, "RoughFromRed": float(rough_red),
            },
            "vectors": {"Wall_Tint": tint + [1.0], "Roof_Colour": roof + [1.0], "Frame_Colour": list(frame) + [1.0],
                        "Stone_Colour": stone + [1.0]},
            "textures": {"Wall_BaseColorMap": colour_map, "Wall_NormalMap": normal_map, "Wall_RoughnessMap": rough_map},
        }
        rows.append({
            "phase4_building": name, "county_object_id": object_id,
            "covered_by_earlier_building": "yes" if covered.get(name, False) else "no",
            "height_above_ground_m": round(height, 1), "footprint_sq_m": round(footprint, 1),
            "wall_stand_in": family, "wall_image": words, "wall_tint": " ".join("%.2f" % v for v in tint),
            "windows": "none" if windows == 0.0 else ("all sides" if side else "street and rear walls"),
            "fronts": "north or south (level X)" if front_x else "east or west (level Y)",
            "floor_height_m": round(floor, 2), "window_spacing_m": round(period, 2), "window_w_by_h_m": "%.2f by %.2f" % (width, tall),
            "window_frame": frame_name, "roof": "Poly Haven bitumen (CC0) at 2.0 m, coloured to the roof's mean in the 2025 aerial photograph",
            "roof_colour_linear": " ".join("%.3f" % v for v in roof),
            "measured": "wall height (2022 laser scan), frontage direction (nearest roadway), roof colour (2025 aerial photograph)",
            "not_measured": "wall material, colour, window size, number and position",
            "status": "PLACEHOLDER: stand-in from data, not from a photograph", "rule": why,
            "material_instance": "/Game/Wieland1529/Surroundings/Materials/Buildings/MI_W1529_" + name,
        })
    with open(OUT + "/plan.json", "w", encoding="utf-8") as handle:
        json.dump(plan, handle, indent=1)
    with open(ROOT + "/phase4_building_materials.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    count = {}
    for row in rows:
        count[row["wall_stand_in"]] = count.get(row["wall_stand_in"], 0) + 1
    print(json.dumps({"buildings": len(rows), "not_covered": sum(1 for r in rows if r["covered_by_earlier_building"] == "no"),
                      "families": count, "front_x": sum(1 for p in plan.values() if p["scalars"]["FrontX"]),
                      "no_windows": sum(1 for p in plan.values() if p["scalars"]["WindowAmount"] == 0.0)}))


if __name__ == "__main__":
    main()
