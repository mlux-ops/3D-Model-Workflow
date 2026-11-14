"""Phase 17: measure built towers and buildings against the 2022 laser-scan point cloud.

Usage:
    python -B -P phase17_check_towers.py <mesh folder> <out csv> [point-cloud folder] [id ...]

For each record in <mesh folder>/towers_record.jsonl (the last line per building wins) whose building has streamed
returns (pc_*.npz with a .source.txt, see phase17_las_stream.py), using the model's top surface on the 1 ft grid
(<name>_grid.npz, written by phase17_towers.py, true heights before the curvature drop):

1. Measured grid: the highest return per 1 ft cell, ground (2), vegetation (3-5), water (9) and noise left out,
   in metres above the record's ground.
2. Roof height: the median of the measured cells over the model's highest roof (cells within 0.5 m of the model's
   top, away from walls) minus the model's roof top there. Also the highest return over the roof that is not a mast.
3. Surface: the 95th percentile of the absolute vertical difference, model minus measured, over every cell where
   either is building and the returns have data, away from walls (2 ft from any step of more than 2 m in either
   grid); walls are judged by the plan check.
4. Plan, per level (the footprint at 2.5 m, then each terrace top with at least 1,000 sq ft): the model's outline
   at the level less 1 m against the measured outline at the same level (closed over 3 ft, kept within 15 ft of the
   model). Distances from each outline's edge cells to the other's: mean and 95th percentile; the footprint is
   reported apart, since neighbours that touch it make its measured outline larger.
5. Masts: the second-highest return within the mast radius plus 3 ft, against the modelled mast top (the masts are
   taken from the same returns, so this is a consistency check only).
"""

import csv
import glob
import json
import os
import sys

import numpy as np
from scipy import ndimage

FT = 0.3048006096
SKIP_CLASSES = [2, 3, 4, 5, 7, 9, 18]


class Tiles:
    """The streamed tiles: their labels read once; the arrays of at most two tiles kept unpacked at a time."""

    def __init__(self, folder):
        self.paths = [p for p in sorted(glob.glob(os.path.join(folder, "pc_*.npz")))
                      if os.path.exists(p + ".source.txt") and not p.endswith("_willis.npz")]
        self.labels, self.tile, self.cache = {}, {}, {}
        for p in self.paths:
            d = np.load(p)
            self.labels[p] = [str(v) for v in d["labels"]]
            self.tile[p] = str(d["tile"])

    def arrays(self, p):
        if p not in self.cache:
            while len(self.cache) >= 2:
                self.cache.pop(next(iter(self.cache)))
            d = np.load(p)
            self.cache[p] = {k: d[k] for k in ("x", "y", "z", "cls", "box")}
        return self.cache[p]

    def first(self, bid):
        for p in self.paths:
            if bid in self.labels[p]:
                return p
        return "zzz"


def points_for(bid, pcs):
    """Returns of one building's box from every streamed tile, and the squares (2,500 ft tiles) they came from."""
    xs, ys, zs, tiles = [], [], [], []
    for p in pcs.paths:
        labels = pcs.labels[p]
        if bid not in labels:
            continue
        d = pcs.arrays(p)
        sel = (d["box"] == labels.index(bid)) & ~np.isin(d["cls"], SKIP_CLASSES)
        xs.append(d["x"][sel]); ys.append(d["y"][sel]); zs.append(d["z"][sel])
        t = pcs.tile[p]
        tiles.append((int(t[:4]) * 100 + 1e6, int(t[4:]) * 100 + 1e6))
    if not xs:
        return None
    return np.concatenate(xs), np.concatenate(ys), np.concatenate(zs), tiles


def edge(mask):
    return mask & ~ndimage.binary_erosion(mask)


def outline_distances(model, meas):
    """Distances in metres from each outline's edge cells to the other outline's edge: mean and 95th percentile."""
    em, es = edge(model), edge(meas)
    if not em.any() or not es.any():
        return None
    dm = ndimage.distance_transform_edt(~es)[em]
    ds = ndimage.distance_transform_edt(~em)[es]
    allv = np.concatenate([dm, ds]) * FT
    return float(allv.mean()), float(np.percentile(allv, 95))


def check(rec, grid, pcs, visible_m=None):
    pts = points_for(rec["id"], pcs)
    if pts is None:
        return None
    x, y, z, tiles = pts
    zm = grid["z"].astype(np.float64)
    x0, y1 = float(grid["x0"]), float(grid["y1"])
    h, w = zm.shape
    # Only the part of the grid inside the streamed tiles is judged (a building on a tile edge may have one tile).
    cov = np.zeros((h, w), bool)
    for te, tn in tiles:
        c0, c1 = int(max(te - x0, 0)), int(min(te + 2500 - x0, w))
        r0, r1 = int(max(y1 - (tn + 2500), 0)), int(min(y1 - tn, h))
        if c1 > c0 and r1 > r0:
            cov[r0:r1, c0:c1] = True
    zm[~cov] = np.nan
    c = np.floor(x - x0).astype(int)
    r = np.floor(y1 - y).astype(int)
    ok = (c >= 0) & (c < w) & (r >= 0) & (r < h)
    meas = np.full(h * w, -np.inf)
    np.maximum.at(meas, r[ok] * w + c[ok], (z[ok] - rec["ground_ft"]) * FT)
    meas = meas.reshape(h, w)
    has = np.isfinite(meas)
    meas[~has] = np.nan
    # Mast cells (and 3 ft around) are left out of the roof and surface figures; masts are checked apart.
    mast_cells = np.zeros((h, w), bool)
    for m in rec.get("masts", []):
        cc, rr = int(m["east"] - x0), int(y1 - m["north"])
        rad = int(m["radius_ft"] + 3)
        mast_cells[max(rr - rad, 0):rr + rad + 1, max(cc - rad, 0):cc + rad + 1] = True
    res = {"id": rec["id"], "name": rec["name"], "form": rec.get("form", ""), "distance_m": rec["distance_m"],
           "returns": int(len(x)), "model_roof_m": rec["roof_top_m"], "model_top_m": rec["top_incl_masts_m"],
           "coverage": round(float(cov.mean()), 3)}
    model_b = np.nan_to_num(zm, nan=0.0) > 2.5
    meas_b = np.nan_to_num(meas, nan=0.0) > 2.5

    def flat(g):
        g0 = np.nan_to_num(g, nan=0.0)
        return (ndimage.maximum_filter(g0, size=5) - ndimage.minimum_filter(g0, size=5)) < 2.0
    away = flat(zm) & flat(np.where(has, meas, np.nan)) & ~mast_cells
    # Roof: cells of the model within 1 m of its main roof (the highest terrace of 150 sq ft or more, the record's
    # roof_top_m), where both grids are building, away from walls and masts.
    top = float(rec["roof_top_m"])
    both = model_b & meas_b & has
    roofc = (np.abs(np.nan_to_num(zm, nan=-1e9) - top) < 1.0) & away & both
    if roofc.sum() < 20:
        roofc = (np.abs(np.nan_to_num(zm, nan=-1e9) - top) < 1.0) & both & ~mast_cells
    if roofc.any():
        res["roof_model_m"] = round(float(np.median(zm[roofc])), 2)
        res["roof_measured_m"] = round(float(np.median(meas[roofc])), 2)
        res["roof_err_m"] = round(res["roof_model_m"] - res["roof_measured_m"], 2)
        res["roof_cells"] = int(roofc.sum())
        over = both & ~mast_cells
        if over.any():
            res["highest_model_not_mast_m"] = round(float(np.nanmax(np.where(over, zm, np.nan))), 2)
            res["highest_return_not_mast_m"] = round(float(np.nanmax(meas[over])), 2)
    # Vertical error where both grids are building: plan misses belong to the plan check.
    surf = both & away
    if surf.sum() >= 20:
        d = np.abs(np.nan_to_num(zm, nan=0.0) - meas)[surf]
        res["surface_p95_m"] = round(float(np.percentile(d, 95)), 2)
        res["surface_median_m"] = round(float(np.median(d)), 2)
    # Measured cells at a level: highest return per cell, holes between scan lines closed over 3 ft and filled.
    mg = ndimage.grey_closing(np.nan_to_num(meas, nan=-50.0), size=(3, 3))
    # Plan levels: the footprint at 2.5 m, then the middle height of each section between successive terrace tops
    # (an outline compared at exactly a roof's own height is decided by a few centimetres of roof).
    tops_sorted = sorted(float(t) for t in grid["tops"] if t > 2.5)
    levels = [2.5] + [round((lo + hi) / 2.0, 2) for lo, hi in zip([0.0] + tops_sorted[:-1], tops_sorted)]
    # Levels the roof deck sees: those above the roof less the visible height from targets.csv.
    highest = float(np.nanmax(np.where(mast_cells, np.nan, zm)))
    lowest_seen = highest - visible_m if visible_m else 0.0
    res["lowest_level_seen_m"] = round(lowest_seen, 1)
    # Also three levels evenly spread over the part that is seen, for shapes with few flat roofs (curved or tapered).
    lo = max(lowest_seen, 2.5)
    levels = sorted(set(levels + [round(lo + k * (highest - lo) / 4.0, 2) for k in (1, 2, 3)]))
    plans = []
    zm0 = np.nan_to_num(zm, nan=0.0)
    for i, lv in enumerate(levels):
        thr = lv
        mm = ndimage.binary_fill_holes(zm0 >= thr) & cov
        if mm.sum() < (1 if i == 0 else 1000) or (i > 0 and lv < lowest_seen):
            continue
        near = ndimage.binary_dilation(mm, iterations=15)
        ms = ndimage.binary_fill_holes(ndimage.binary_closing(mg >= thr, iterations=3)) & near & cov
        dd = outline_distances(mm, ms)
        if dd is None:
            continue
        plans.append({"level_m": round(lv, 2), "mean_m": round(dd[0], 2), "p95_m": round(dd[1], 2)})
    if plans:
        res["footprint_edge_mean_m"] = plans[0]["mean_m"]
        res["footprint_edge_p95_m"] = plans[0]["p95_m"]
        upper = plans[1:] or plans
        worst = max(upper, key=lambda p: p["p95_m"])
        res["upper_edge_p95_worst_m"] = worst["p95_m"]
        res["upper_edge_worst_level_m"] = worst["level_m"]
        res["upper_edge_mean_m"] = round(float(np.mean([p["mean_m"] for p in upper])), 2)
    mres = []
    for m in rec.get("masts", []):
        rad = m["radius_ft"] + 3.0
        sel = (x - m["east"]) ** 2 + (y - m["north"]) ** 2 <= rad * rad
        if sel.sum() >= 2:
            zz = np.sort((z[sel] - rec["ground_ft"]) * FT)
            mres.append(round(float(zz[-2]) - m["top_m"], 2))
    res["mast_err_m"] = ";".join(str(v) for v in mres)
    res["detail"] = json.dumps({"plans": plans})
    return res


KEYS = ["id", "name", "form", "distance_m", "returns", "coverage", "model_roof_m", "model_top_m", "roof_model_m",
        "roof_measured_m", "roof_err_m", "roof_cells", "highest_model_not_mast_m", "highest_return_not_mast_m",
        "lowest_level_seen_m", "surface_median_m", "surface_p95_m",
        "footprint_edge_mean_m", "footprint_edge_p95_m", "upper_edge_mean_m", "upper_edge_p95_worst_m",
        "upper_edge_worst_level_m", "mast_err_m", "detail"]


def main(argv):
    folder, out_csv = argv[1], argv[2]
    pcf = argv[3] if len(argv) > 3 else "D:/Wieland1529_lidar/derived"
    only = set(argv[4:])
    pcs = Tiles(pcf)
    visible = {}
    tpath = os.path.join(os.path.dirname(os.path.normpath(folder)), "targets.csv")
    if os.path.exists(tpath):
        visible = {r["bldg_id"]: r["visible_height_m_bare"] for r in csv.DictReader(open(tpath, encoding="utf-8"))}
    recs = {}
    for line in open(os.path.join(folder, "towers_record.jsonl"), encoding="utf-8"):
        rec = json.loads(line)
        recs[rec["id"]] = rec
    rows = []
    for bid, rec in sorted(recs.items(), key=lambda kv: pcs.first(kv[0])):
        if only and bid not in only:
            continue
        gpath = os.path.join(folder, rec["name"] + "_grid.npz")
        if not os.path.exists(gpath):
            continue
        vis = visible.get(bid)
        res = check(rec, np.load(gpath), pcs, float(vis) if vis else None)
        if res is None:
            print("no returns", bid)
            continue
        rows.append(res)
        print({k: v for k, v in res.items() if k != "detail"})
    with open(out_csv, "w", newline="", encoding="utf-8") as handle:
        wr = csv.DictWriter(handle, fieldnames=KEYS)
        wr.writeheader()
        for row in rows:
            wr.writerow({k: row.get(k, "") for k in KEYS})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
