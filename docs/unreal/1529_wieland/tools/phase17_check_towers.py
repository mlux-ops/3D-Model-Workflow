"""Phase 17: measure built towers and buildings against the 2022 laser-scan point cloud.

Usage:
    python -B -P phase17_check_towers.py <towers_record.jsonl> <out csv> [point-cloud folder]

For each record line (written by phase17_towers.py, with each terrace's outline as WKT) whose building has
streamed returns (pc_*.npz with a .source.txt, see phase17_las_stream.py):

1. A 1 ft grid of the highest return per cell, ground (2), vegetation (3-5) and water (9) left out, as height above
   the record's ground.
2. Height error per terrace: over the part of the plan where that terrace is the top surface, eroded by 3 ft so the
   edges do not count, the median return height minus the modelled top. The roof error is the top terrace's; the
   worst error is the largest over terraces with at least 300 sq ft of eroded roof and 50 cells of returns.
3. Plan error per terrace with at least 1,000 sq ft: the cells whose returns reach the terrace top less 1 m, closed
   over 3 ft, kept within 15 ft of the model outline, as an outline; the mean edge offset is the area between the two
   outlines divided by the model outline's perimeter. The footprint uses 2.5 m. The worst is reported.
4. Masts: second-highest return within the mast radius plus 3 ft, against the modelled mast top.

The returns are the same survey as the 1 ft surface model the terraces come from, but a different product (the
surface model is gridded and filled by the state); the masts come from the returns, so their check is a
consistency check only and says so.
"""

import csv
import glob
import json
import math
import os
import sys

import numpy as np
import shapely
from shapely import wkt as swkt
from shapely.geometry import MultiPolygon, Polygon, box as sbox
from shapely.ops import unary_union
from scipy import ndimage

FT = 0.3048006096
SKIP_CLASSES = [2, 3, 4, 5, 7, 9, 18]


def load_pc(folder):
    out = {}
    for path in sorted(glob.glob(os.path.join(folder, "pc_*.npz"))):
        if not os.path.exists(path + ".source.txt") or path.endswith("_willis.npz"):
            continue
        d = np.load(path)
        out[path] = d
    return out


def points_for(bid, pcs):
    xs, ys, zs = [], [], []
    for path, d in pcs.items():
        labels = [str(v) for v in d["labels"]]
        if bid not in labels:
            continue
        box = d["box"]
        sel = (box == labels.index(bid)) & ~np.isin(d["cls"], SKIP_CLASSES)
        xs.append(d["x"][sel]); ys.append(d["y"][sel]); zs.append(d["z"][sel])
    if not xs:
        return None
    return np.concatenate(xs), np.concatenate(ys), np.concatenate(zs)


def region_from_mask(mask, x0, y1):
    rects = []
    for r in range(mask.shape[0]):
        row = mask[r]
        if not row.any():
            continue
        d = np.diff(np.concatenate([[0], row.view(np.int8), [0]]))
        for a, b in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
            rects.append(sbox(x0 + a, y1 - r - 1, x0 + b, y1 - r))
    return unary_union(rects) if rects else Polygon()


def check(rec, pcs):
    pts = points_for(rec["id"], pcs)
    if pts is None:
        return None
    x, y, z = pts
    polys = [swkt.loads(p["wkt"]) for p in rec["prisms"]]
    tops = [p["top_m"] for p in rec["prisms"]]
    allp = unary_union(polys)
    minx, miny, maxx, maxy = allp.buffer(20).bounds
    x0, y1 = math.floor(minx), math.ceil(maxy)
    w, h = int(math.ceil(maxx) - x0), int(y1 - math.floor(miny))
    c = np.floor(x - x0).astype(int)
    r = np.floor(y1 - y).astype(int)
    ok = (c >= 0) & (c < w) & (r >= 0) & (r < h)
    grid = np.full(h * w, -np.inf)
    np.maximum.at(grid, r[ok] * w + c[ok], (z[ok] - rec["ground_ft"]) * FT)
    grid = grid.reshape(h, w)
    has = np.isfinite(grid)
    cx = x0 + np.arange(w) + 0.5
    cy = y1 - np.arange(h) - 0.5
    gx, gy = np.meshgrid(cx, cy)
    inside = [shapely.contains_xy(p, gx, gy) for p in polys]
    model_level = np.full((h, w), -1)
    for i, m in enumerate(inside):
        model_level[m] = i
    res = {"id": rec["id"], "name": rec["name"], "distance_m": rec["distance_m"], "returns": int(len(x)),
           "model_roof_m": rec["roof_top_m"], "model_top_m": rec["top_incl_masts_m"]}
    terr = []
    for i, t in enumerate(tops):
        own = ndimage.binary_erosion(model_level == i, iterations=3)
        cells = own & has
        if own.sum() < 300 or cells.sum() < 50:
            continue
        med = float(np.median(grid[cells]))
        terr.append({"i": i, "top_m": t, "measured_m": round(med, 2), "err_m": round(med - t, 2),
                     "cells": int(cells.sum())})
    res["terraces_checked"] = len(terr)
    if terr:
        top = max(terr, key=lambda d: d["top_m"])
        worst = max(terr, key=lambda d: abs(d["err_m"]))
        res.update({"roof_measured_m": top["measured_m"], "roof_err_m": top["err_m"],
                    "worst_terrace_err_m": worst["err_m"], "worst_terrace_top_m": worst["top_m"]})
    filled = ndimage.binary_closing(has, iterations=2)
    hgrid = np.where(has, grid, -np.inf)
    hgrid = ndimage.grey_closing(np.where(np.isfinite(hgrid), hgrid, -50.0), size=(3, 3))
    plans = []
    for i, (t, p) in enumerate(zip(tops, polys)):
        if p.area < 1000:
            continue
        thr = 2.5 if i == 0 else t - 1.0
        mask = ndimage.binary_closing(filled & (hgrid >= thr), iterations=3)
        meas = region_from_mask(mask, x0, y1).intersection(p.buffer(15))
        meas = meas.buffer(-0.7, join_style=2).buffer(0.7, join_style=2)
        if meas.is_empty:
            continue
        off = meas.symmetric_difference(p).area / max(p.length, 1.0) * FT
        plans.append({"top_m": t, "offset_m": round(off, 2), "hausdorff_m": round(meas.hausdorff_distance(p) * FT, 2)})
    if plans:
        res["footprint_offset_m"] = plans[0]["offset_m"]
        worst = max(plans, key=lambda d: d["offset_m"])
        res["worst_plan_offset_m"] = worst["offset_m"]
        res["worst_plan_terrace_m"] = worst["top_m"]
        res["top_plan_offset_m"] = plans[-1]["offset_m"]
    mres = []
    for m in rec.get("masts", []):
        rad = m["radius_ft"] + 3.0
        sel = (x - m["east"]) ** 2 + (y - m["north"]) ** 2 <= rad * rad
        if sel.sum() >= 2:
            zz = np.sort((z[sel] - rec["ground_ft"]) * FT)
            mres.append(round(float(zz[-2]) - m["top_m"], 2))
    res["mast_err_m"] = ";".join(str(v) for v in mres)
    res["detail"] = json.dumps({"terraces": terr, "plans": plans})
    return res


def main(argv):
    rec_path, out_csv = argv[1], argv[2]
    folder = argv[3] if len(argv) > 3 else "D:/Wieland1529_lidar/derived"
    pcs = load_pc(folder)
    recs = {}
    for line in open(rec_path, encoding="utf-8"):
        rec = json.loads(line)
        if all("wkt" in p for p in rec["prisms"]):
            recs[rec["id"]] = rec  # last record of an id wins
    rows = []
    for bid, rec in recs.items():
        res = check(rec, pcs)
        if res is None:
            print("no returns", bid)
            continue
        rows.append(res)
        print(bid, {k: v for k, v in res.items() if k != "detail"})
    keys = ["id", "name", "distance_m", "returns", "model_roof_m", "model_top_m", "terraces_checked", "roof_measured_m",
            "roof_err_m", "worst_terrace_err_m", "worst_terrace_top_m", "footprint_offset_m", "top_plan_offset_m",
            "worst_plan_offset_m", "worst_plan_terrace_m", "mast_err_m", "detail"]
    with open(out_csv, "w", newline="", encoding="utf-8") as handle:
        wr = csv.DictWriter(handle, fieldnames=keys)
        wr.writeheader()
        for row in rows:
            wr.writerow({k: row.get(k, "") for k in keys})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
