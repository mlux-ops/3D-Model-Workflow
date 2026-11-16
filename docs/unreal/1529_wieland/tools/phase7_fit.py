"""Phase 7, step 7.0: work out how each earlier part must change to sit on the surveyed ground.

Reads   review/phase7/fit/raw/<part>.npz      raw mesh data written by wieland_site.dump_parts
        review/phase7/heights/combined.npz    height maps written by phase7_heights.py
Writes  review/phase7/fit/plan/<part>.npz     triangles to leave out and the move up or down of every point
        review/phase7/fit/fit_plan.csv        one line per part
        review/phase7/fit/fit_summary.json    totals and how well the moved buildings meet the ground
        review/phase7/fit/lift_field.npy      the smooth move field on the 0.5 m grid (cm)

Three rules decide what is left out of a part:
  ground   the earlier parts' own ground (street, paving, lawn, mulch, gravel, parking paint): the Phase 4
           ground from the 2022 laser scan is kept instead, and step 7.2 gives it its materials;
  lot      everything that stands inside the lot of 1529 (white slab, cedar fence, short iron fences, bins,
           sunken steps): audit finding A1, the new house stands there;
  nothing else is left out.
Every point that stays is moved up or down by a smooth field: the Phase 4 ground, taken at its lower side
and smoothed over about 10 m, minus the earlier ground level (0). A building therefore follows the surveyed
ground as a whole, without visible bending, and its foot sits on or slightly in the ground, never above it.

Run from the plan folder:  python -B tools/phase7_fit.py
Nothing in Unreal is touched.
"""

import csv
import glob
import json
import os

import numpy as np
from scipy import ndimage

ROOT = "review/phase7"
SHIFT = np.array([15482.32, 5053.7, 0.0])
CELL = 50.0
NONE = -99999.0

GROUND_ALWAYS = ("MI_R15_asphalt_03_World", "MI_R15_turf_World", "MI_R15_dirt_floor_World", "MI_R15_wood_chips_World",
                 "B_MAT_Limestone_gravel", "SS_R01_FadedParkingPaint_001")
GROUND_WHEN_LOW = ("MI_R15_concrete_floor_03_World", "MI_R15_concrete_floor_03_UV", "B_MAT_Joint_recess")
LOW_CM = 25.0            # a paving triangle that nowhere rises above this is ground (kerbs and slabs included)
LOT = (-1508.5, 6.0, -3115.5, 60.0)   # x_min, x_max, y_min, y_max in level cm: the governing lot, to the back of the sidewalk
MIN_FILTER_CELLS = 7     # 3.5 m: the lower side of the ground
SIGMA_CELLS = 8.0        # 4 m: smoothing of the move field


def lift_field():
    data = np.load(ROOT + "/heights/combined.npz")
    ground = data["ground_p4"].astype(np.float64)
    i0, j0 = int(data["i0"]), int(data["j0"])
    missing = ground < NONE / 2
    # Fill the cells without ground (the lot's cut-out and the rim) from the nearest cell that has ground.
    _, nearest = ndimage.distance_transform_edt(missing, return_indices=True)
    filled = ground[nearest[0], nearest[1]]
    lower = ndimage.minimum_filter(filled, size=MIN_FILTER_CELLS, mode="nearest")
    smooth = ndimage.gaussian_filter(lower, sigma=SIGMA_CELLS, mode="nearest")
    return smooth, filled, i0, j0, data


def sample(field, i0, j0, x, y):
    """Bilinear reading of a grid whose cell (i, j) has its centre at ((i + 0.5) * CELL, (j + 0.5) * CELL)."""
    u = x / CELL - 0.5 - i0
    v = y / CELL - 0.5 - j0
    u = np.clip(u, 0.0, field.shape[0] - 1.001)
    v = np.clip(v, 0.0, field.shape[1] - 1.001)
    a = np.floor(u).astype(int)
    b = np.floor(v).astype(int)
    fu = u - a
    fv = v - b
    return (field[a, b] * (1 - fu) * (1 - fv) + field[a + 1, b] * fu * (1 - fv)
            + field[a, b + 1] * (1 - fu) * fv + field[a + 1, b + 1] * fu * fv)


def main():
    smooth, filled, i0, j0, data = lift_field()
    os.makedirs(ROOT + "/fit/plan", exist_ok=True)
    np.save(ROOT + "/fit/lift_field.npy", smooth.astype(np.float32))
    rows = []
    totals = {"triangles": 0, "left_out_as_ground": 0, "left_out_inside_the_lot": 0, "kept": 0, "parts_left_empty": []}
    lifts = []
    for path in sorted(glob.glob(ROOT + "/fit/raw/R15_PART_*.npz")):
        part = os.path.basename(path)[:-4]
        raw = np.load(path)
        p = raw["positions"] + SHIFT
        t = raw["triangles"]
        m = raw["material_ids"]
        names = [str(x).split("/")[-1] for x in raw["slot_materials"]]
        a, b, c = p[t[:, 0]], p[t[:, 1]], p[t[:, 2]]
        z_top = np.maximum(np.maximum(a[:, 2], b[:, 2]), c[:, 2])
        always = np.isin(m, [k for k, n in enumerate(names) if n in GROUND_ALWAYS])
        low = np.isin(m, [k for k, n in enumerate(names) if n in GROUND_WHEN_LOW]) & (z_top <= LOW_CM)
        ground = always | low

        def inside(q):
            return (q[:, 0] >= LOT[0]) & (q[:, 0] <= LOT[1]) & (q[:, 1] >= LOT[2]) & (q[:, 1] <= LOT[3])

        lot = inside(a) & inside(b) & inside(c) & ~ground
        remove = ground | lot
        lift = sample(smooth, i0, j0, p[:, 0], p[:, 1])
        used = np.zeros(p.shape[0], dtype=bool)
        used[t[~remove].ravel()] = True
        kept = int((~remove).sum())
        np.savez_compressed(ROOT + "/fit/plan/" + part + ".npz", remove=np.nonzero(remove)[0].astype(np.int32),
                            lift=lift.astype(np.float64), vertices=p.shape[0], triangles=t.shape[0])
        row = {"part": part, "triangles": int(t.shape[0]), "left_out_as_ground": int(ground.sum()),
               "left_out_inside_the_lot": int(lot.sum()), "kept": kept,
               "lowest_move_cm": round(float(lift[used].min()), 1) if kept else "",
               "highest_move_cm": round(float(lift[used].max()), 1) if kept else "",
               "foot_before_cm": round(float(p[used][:, 2].min()), 1) if kept else ""}
        rows.append(row)
        totals["triangles"] += row["triangles"]
        totals["left_out_as_ground"] += row["left_out_as_ground"]
        totals["left_out_inside_the_lot"] += row["left_out_inside_the_lot"]
        totals["kept"] += kept
        if kept == 0:
            totals["parts_left_empty"].append(part)
        else:
            lifts.append(lift[used])
    with open(ROOT + "/fit/fit_plan.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # How the moved buildings meet the ground: along the outline of the earlier building shapes, the Phase 4
    # ground minus the moved earlier ground level. Positive: the foot is that far in the ground. Negative: above it.
    building = data["r15_building"]
    ring = ndimage.binary_dilation(building, iterations=2) & ~building
    owner = data["owner"]
    ring &= owner < 0   # not where a Phase 4 building stands
    meet = (filled - smooth)[ring]
    before = (filled - 0.0)[ring]
    q = lambda v: [round(float(x), 1) for x in np.percentile(v, [1, 5, 25, 50, 75, 95, 99])]
    all_lift = np.concatenate(lifts)
    gy, gx = np.gradient(smooth, CELL)
    slope = np.hypot(gx, gy)[building]
    totals.update({
        "move_cm_lowest_and_highest": [round(float(all_lift.min()), 1), round(float(all_lift.max()), 1)],
        "outline_cells": int(ring.sum()),
        "ground_minus_foot_before_cm_percentiles_1_5_25_50_75_95_99": q(before),
        "ground_minus_foot_after_cm_percentiles_1_5_25_50_75_95_99": q(meet),
        "share_of_outline_above_ground_by_over_3cm_before": round(float((before < -3).mean()), 3),
        "share_of_outline_above_ground_by_over_3cm_after": round(float((meet < -3).mean()), 3),
        "share_of_outline_in_ground_by_over_15cm_before": round(float((before > 15).mean()), 3),
        "share_of_outline_in_ground_by_over_15cm_after": round(float((meet > 15).mean()), 3),
        "tilt_of_move_field_under_buildings_percent_median_and_largest": [round(float(np.median(slope)) * 100, 2), round(float(slope.max()) * 100, 2)],
    })
    with open(ROOT + "/fit/fit_summary.json", "w", encoding="utf-8") as handle:
        json.dump(totals, handle, indent=1)
    print(json.dumps(totals, indent=1))


if __name__ == "__main__":
    main()
