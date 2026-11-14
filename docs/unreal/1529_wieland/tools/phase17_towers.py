"""Phase 17, step 17.2: stepped ("terraced") tower meshes from the 2022 laser-scan surface model.

Usage:
    python -B -P phase17_towers.py <phase17 data folder> <out folder> [county id ...]

For each target of targets.csv (or the ids given), from its 1 ft surface model (rasters/bldg1ft/<id>_dsm.npz),
the 6 ft ground model, and its Cook County 2022 outline:

1. Ground: median of the ground model inside the outline.
2. Building cells: inside the outline grown by 2 ft, and more than 2.5 m above the ground. So the plan edge is
   where the scan finds the roof edge, not the county line.
3. Heights are median-filtered over 3 by 3 ft (removes single-return spikes) and quantized to 0.5 m. A height
   becomes a terrace top when at least MIN_AREA_FT2 of roof stands at it; tops closer than 0.75 m are merged.
   Each cell takes the highest top at or below its height + 0.5 m. Each terrace i is a vertical prism from the
   top below it to its own top, over the cells whose terrace is i or higher, outlined by row runs, opened by
   0.7 ft to remove one-cell noise and simplified to 1 ft.
4. Masts and spires: raw (unfiltered) heights more than 4 m above the terrace surface in blobs of at most 600 sq ft
   become octagonal prisms at the blob's centre, of the blob's equivalent radius (at least 0.5 m), up to the blob's
   highest raw height. The point cloud check (phase17_check_towers.py) compares these with the returns.
5. Earth curvature with refraction: every height is lowered by d^2 / (2R) * (1 - 0.13), d from D1, so the tower
   stands in the flat level as it appears from the roof deck. True and placed heights are both recorded.

Writes one mesh file per building, <out>/P17T_<id>.json, in the format of build_surroundings.py (vertices in level
cm relative to the pivot, triangles, pivot, name, kind, zone), plus tri_mat (0 wall, 1 roof, 2 mast) and a record
line in <out>/towers_record.jsonl.
"""

import csv
import json
import math
import os
import sys

import numpy as np
import shapely
from PIL import Image, ImageDraw
from scipy import ndimage
from shapely.geometry import MultiPolygon, Polygon, box as sbox
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wieland_geo as g  # noqa: E402

FT = 0.3048006096
CM_PER_FT = 30.48006096
R_EARTH_M = 6371000.0
K_REFRACTION = 0.13
MIN_AREA_FT2 = 150.0
USE_PC_GRID = False
FRAME = os.path.join(HERE, "..", "review", "phase2", "level_frame.json")
D1 = (-1300.0, -1560.0, 1684.0)


def load(path):
    d = np.load(path)
    return d["z"].astype(np.float32), float(d["x0"]), float(d["y1"]), float(d["cell"])


def region_polygon(mask, x0, y1, cell):
    """Union of row runs of a boolean mask as a shapely geometry in map feet."""
    rects = []
    for r in range(mask.shape[0]):
        row = mask[r]
        if not row.any():
            continue
        d = np.diff(np.concatenate([[0], row.view(np.int8), [0]]))
        starts, ends = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
        n_top, n_bot = y1 - r * cell, y1 - (r + 1) * cell
        for a, b in zip(starts, ends):
            rects.append(sbox(x0 + a * cell, n_bot, x0 + b * cell, n_top))
    if not rects:
        return Polygon()
    return unary_union(rects)


def clean(geom, min_area):
    geom = geom.buffer(-0.7, join_style=2).buffer(0.7, join_style=2).simplify(1.0, preserve_topology=True)
    parts = [p for p in getattr(geom, "geoms", [geom]) if isinstance(p, Polygon) and p.area >= min_area]
    return MultiPolygon(parts) if parts else Polygon()


class MeshOut:
    def __init__(self, frame, pivot_map, drop_fn):
        self.v, self.t, self.m = [], [], []
        self.frame, self.drop = frame, drop_fn
        self.pivot = frame.level_from_map(pivot_map[0], pivot_map[1], pivot_map[2])

    def vert(self, e, n, z_ft):
        x, y, z = self.frame.level_from_map(e, n, z_ft - self.drop(e, n) / FT)
        self.v.append((round(x - self.pivot[0], 2), round(y - self.pivot[1], 2), round(z - self.pivot[2], 2)))
        return len(self.v) - 1

    def walls(self, poly, z0, z1, mat):
        for ring in [poly.exterior] + list(poly.interiors):
            pts = list(ring.coords)[:-1]
            if not ring.is_ccw ^ (ring is not poly.exterior):
                pts = pts[::-1]  # exterior counter-clockwise seen from above, holes clockwise: walls face out
            for i in range(len(pts)):
                a, b = pts[i], pts[(i + 1) % len(pts)]
                i0, i1 = self.vert(a[0], a[1], z0), self.vert(b[0], b[1], z0)
                i2, i3 = self.vert(b[0], b[1], z1), self.vert(a[0], a[1], z1)
                # Level frame is mirrored (east = -Y), so winding seen in the level flips: emit as (i0, i2, i1).
                self.t += [(i0, i2, i1), (i0, i3, i2)]
                self.m += [mat, mat]

    def cap(self, poly, z, mat):
        tris = shapely.constrained_delaunay_triangles(poly)
        for tri in getattr(tris, "geoms", []):
            c = list(tri.exterior.coords)[:3]
            if Polygon(c).area < 1e-6:
                continue
            if not Polygon(c).exterior.is_ccw:
                c = c[::-1]
            ids = [self.vert(e, n, z) for e, n in c]
            self.t.append((ids[0], ids[2], ids[1]))
            self.m.append(mat)


PC_FOLDER = "D:/Wieland1529_lidar/derived"
_PC_CACHE = {}


def point_cloud(bid):
    """Points of this building's box from any streamed tile (x, y, z feet, cls), or None."""
    import glob
    xs, ys, zs, cs = [], [], [], []
    for path in glob.glob(os.path.join(PC_FOLDER, "pc_*.npz")):
        if not os.path.exists(path + ".source.txt"):
            continue  # still being written by the batch (its record file is written last)
        if path not in _PC_CACHE:
            d = np.load(path)
            _PC_CACHE[path] = {k: d[k] for k in ("x", "y", "z", "cls", "box", "labels")}
        d = _PC_CACHE[path]
        labels = list(d["labels"])
        if bid not in labels:
            continue
        sel = d["box"] == labels.index(bid)
        xs.append(d["x"][sel]); ys.append(d["y"][sel]); zs.append(d["z"][sel]); cs.append(d["cls"][sel])
    if not xs:
        return None
    return {"x": np.concatenate(xs), "y": np.concatenate(ys), "z": np.concatenate(zs), "cls": np.concatenate(cs)}


def pc_masts(pc, ground_ft, terrace, x0, y1, cell, topmask, top_m):
    """Masts from returns more than 4 m above the highest terrace within 3 ft, over the building, in clusters of
    at least 5 returns on a 3 ft grid. Top: the second-highest return of the cluster (one stray return is not a top)."""
    h, w = terrace.shape
    c = ((pc["x"] - x0) / cell).astype(int)
    r = ((y1 - pc["y"]) / cell).astype(int)
    ok = (c >= 0) & (c < w) & (r >= 0) & (r < h) & np.isin(pc["cls"], [1, 6, 19, 11, 14, 15])
    # Only over the top roof (grown by 5 ft): masts and spires that make the skyline. Returns from walls lower
    # down are not masts.
    tmax = np.full(terrace.shape, top_m)
    grown = ndimage.binary_dilation(topmask, iterations=5)
    hm = (pc["z"] - ground_ft) * FT
    sel = np.zeros(len(hm), bool)
    sel[ok] = grown[r[ok], c[ok]] & (hm[ok] - top_m > 4.0)
    if sel.sum() < 5:
        return []
    occ = np.zeros((h // 3 + 2, w // 3 + 2), np.int32)
    np.add.at(occ, (r[sel] // 3, c[sel] // 3), 1)
    lab, n = ndimage.label(occ > 0, structure=np.ones((3, 3)))
    pl = lab[r[sel] // 3, c[sel] // 3]
    xs, ys, zs = pc["x"][sel], pc["y"][sel], hm[sel]
    masts = []
    for i in range(1, n + 1):
        k = pl == i
        if k.sum() < 5 or (lab == i).sum() * 9.0 > 900.0:
            continue
        zz = np.sort(zs[k])
        top = float(zz[-2])
        e, nn = float(np.median(xs[k])), float(np.median(ys[k]))
        rad = max(0.5 / FT, float(np.sqrt(np.var(xs[k]) + np.var(ys[k]))) * 1.2)
        rad = min(rad, 12.0)
        cc, rr = int((e - x0) / cell), int((y1 - nn) / cell)
        base = float(tmax[min(max(rr, 0), h - 1), min(max(cc, 0), w - 1)])
        masts.append({"east": e, "north": nn, "radius_ft": rad, "base_m": base, "top_m": top, "returns": int(k.sum())})
    return masts


def build(bid, row, base, frame, county, dtm6, out):
    dsm, x0, y1, cell = load(os.path.join(base, "rasters", "bldg1ft", "%s_dsm.npz" % bid))
    rings = county[bid]["geometry"]["rings"]
    outline = unary_union([Polygon(r).buffer(0) for r in rings])
    h, w = dsm.shape
    pic = Image.new("L", (w, h), 0)
    dr = ImageDraw.Draw(pic)
    for ring in rings:
        dr.polygon([((e - x0) / cell, (y1 - n) / cell) for e, n in ring], fill=1)
    inside = np.asarray(pic, dtype=bool)
    # Ground: median of the 6 ft ground model inside the outline.
    gz, gx0, gy1, gcell = dtm6
    minx, miny, maxx, maxy = outline.bounds
    c0, c1 = int((minx - gx0) / gcell), int((maxx - gx0) / gcell) + 1
    r0, r1 = int((gy1 - maxy) / gcell), int((gy1 - miny) / gcell) + 1
    gwin = gz[max(r0, 0):r1, max(c0, 0):c1]
    ground_ft = float(np.nanmedian(gwin)) if np.isfinite(gwin).any() else float(county[bid]["attributes"]["Ground_Z"])
    pc = point_cloud(bid)
    height_source = "ISGS 1 ft surface model"
    if pc is not None and USE_PC_GRID:
        # Tried on Willis and not used: the highest return per 1 ft cell picks up facade returns one cell outside the
        # walls and makes false steps (63.5 and 123.5 m); the closed surface model matched the published 75 ft tubes
        # within 1 to 4 percent of area, the point grid within 6 to 17 percent. It also keeps the point cloud
        # independent of the geometry, for the checks.
        grid = np.full(dsm.shape, np.nan, np.float64)
        cc = ((pc["x"] - x0) / cell).astype(int)
        rr = ((y1 - pc["y"]) / cell).astype(int)
        ok = (cc >= 0) & (cc < dsm.shape[1]) & (rr >= 0) & (rr < dsm.shape[0])
        flatidx = rr[ok] * dsm.shape[1] + cc[ok]
        mx = np.full(dsm.size, -np.inf)
        np.maximum.at(mx, flatidx, pc["z"][ok])
        mx = mx.reshape(dsm.shape)
        filled = np.isfinite(mx)
        if filled.mean() > 0.5:
            grid[filled] = mx[filled]
            dsm = np.where(filled, grid, np.nan).astype(np.float32)
            height_source = "point cloud, highest return per 1 ft cell"
    raw_m = (dsm - ground_ft) * FT
    grown = ndimage.binary_dilation(inside, iterations=2)
    # The 1 ft surface model is speckled over tall roofs: many cells fall low (no roof return in the cell). A grey
    # closing over 5 by 5 ft (local maximum, then local minimum) fills the low specks without moving roof edges;
    # a 3 by 3 median then removes single high spikes.
    closed = ndimage.grey_closing(np.nan_to_num(raw_m, nan=0.0), size=(5, 5))
    med = ndimage.median_filter(closed, size=3)
    bmask = grown & (med > 2.5)
    lab, nlab = ndimage.label(bmask)
    if nlab == 0:
        return None
    sizes = ndimage.sum(bmask, lab, range(1, nlab + 1))
    keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s * cell * cell >= 50.0])
    bmask &= keep
    if not bmask.any():
        return None
    # Only flat roof cells define a step height: in the surface model a wall is not vertical but a ramp a few cells
    # wide, and every half-metre of the ramp would otherwise become a false step.
    local_sd = np.sqrt(np.maximum(ndimage.uniform_filter(med * med, 5) - ndimage.uniform_filter(med, 5) ** 2, 0.0))
    flat = bmask & (local_sd < 0.4)
    if flat.sum() * cell * cell < MIN_AREA_FT2:
        flat = bmask
    q = np.round(med[flat] * 2.0) / 2.0
    vals, counts = np.unique(q, return_counts=True)
    areas = counts * cell * cell
    tops = [float(v) for v, a in zip(vals, areas) if a >= MIN_AREA_FT2]
    if not tops:
        tops = [float(np.percentile(med[bmask], 90))]
    merged = []
    for t in sorted(tops):
        if merged and t - merged[-1][-1] < 0.75:
            merged[-1].append(t)
        else:
            merged.append([t])
    # Each merged group's top: the value with the largest area in the group.
    area_of = dict(zip(vals.tolist(), areas.tolist()))
    tops = [max(grp, key=lambda t: area_of.get(t, 0.0)) for grp in merged]
    # Each cell takes the nearest step, so a ramp is split at its middle, which is where the wall stands.
    tarr = np.array(tops)
    nearest = np.abs(med[..., None] - tarr[None, None, :]).argmin(axis=-1)
    level = np.where(bmask, nearest, -1).astype(np.int32)
    # Masts: raw heights well above the terrace surface, in small blobs.
    terrace = np.where(level >= 0, np.array(tops + [0.0])[level], 0.0)
    # A mast stands above everything around it: compare with the highest terrace within 3 ft, so the edges of
    # upper terraces (where the 3 by 3 median pulls the terrace down) are not taken for masts.
    over = bmask & np.isfinite(raw_m) & (raw_m - ndimage.maximum_filter(terrace, size=7) > 4.0)
    mlab, mn = ndimage.label(over)
    masts = []
    for i in range(1, mn + 1):
        cells = mlab == i
        area = cells.sum() * cell * cell
        if area > 600.0:
            continue
        rr, cc = np.nonzero(cells)
        top_m = float(np.nanmax(raw_m[cells]))
        base_m = float(np.max(terrace[cells]))
        e = x0 + (cc.mean() + 0.5) * cell
        n = y1 - (rr.mean() + 0.5) * cell
        masts.append({"east": e, "north": n, "radius_ft": max(0.5 / FT, math.sqrt(area / math.pi)),
                      "base_m": base_m, "top_m": top_m, "area_ft2": area})
    # Masts from the point cloud where the tile was streamed: they outrank the surface model, which loses thin masts
    # (Willis: 460 m in the surface model, 525.5 m in the returns, 527 m published).
    mast_source = "surface model"
    if pc is not None:
        masts = pc_masts(pc, ground_ft, terrace, x0, y1, cell, level == len(tops) - 1, tops[-1])
        mast_source = "point cloud"
    # Curvature drop from D1.
    d1e, d1n = frame.map_from_level(D1[0], D1[1])

    def drop(e, n):
        d = math.hypot(e - d1e, n - d1n) * FT
        return d * d / (2.0 * R_EARTH_M) * (1.0 - K_REFRACTION)

    c = outline.centroid
    mesh = MeshOut(frame, (c.x, c.y, ground_ft), drop)
    prisms = []
    base_ft = ground_ft - 1.0 / FT  # 1 m below the ground so no gap shows where the ground model is coarser
    prev_ft = base_ft
    for i, t in enumerate(tops):
        region = clean(region_polygon(level >= i, x0, y1, cell), MIN_AREA_FT2 if i > 0 else 50.0)
        if region.is_empty:
            continue
        top_ft = ground_ft + t / FT
        for poly in region.geoms:
            mesh.walls(poly, prev_ft, top_ft, 0)
            mesh.cap(poly, top_ft, 1)
        prisms.append({"top_m": t, "area_ft2": round(region.area, 1)})
        prev_ft = top_ft
    for m in masts:
        poly = Polygon([(m["east"] + m["radius_ft"] * math.cos(a), m["north"] + m["radius_ft"] * math.sin(a))
                        for a in np.linspace(0, 2 * math.pi, 9)[:-1]])
        z0 = ground_ft + m["base_m"] / FT - 0.5 / FT
        z1 = ground_ft + m["top_m"] / FT
        mesh.walls(poly, z0, z1, 2)
        mesh.cap(poly, z1, 2)
    if not mesh.t:
        return None
    dist = math.hypot(c.x - d1e, c.y - d1n) * FT
    name = "P17T_%s" % bid
    data = {"name": name, "kind": "building", "zone": 4 if dist > 1000 else 3, "pivot": [round(v, 2) for v in mesh.pivot],
            "vertices": mesh.v, "triangles": mesh.t, "tri_mat": mesh.m}
    with open(os.path.join(out, name + ".json"), "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    top_roof = max(p["top_m"] for p in prisms) if prisms else 0.0
    top_all = max([top_roof] + [m["top_m"] for m in masts])
    rec = {"id": bid, "name": name, "distance_m": round(dist, 1), "ground_ft": round(ground_ft, 2),
           "terraces": len(prisms), "roof_top_m": round(top_roof, 2), "mast_count": len(masts),
           "top_incl_masts_m": round(top_all, 2), "curvature_drop_m": round(drop(c.x, c.y), 3),
           "placed_top_m": round(top_all - drop(c.x, c.y), 2), "triangles": len(mesh.t),
           "mast_source": mast_source, "height_source": height_source, "plan_area_ft2": round(float(bmask.sum()) * cell * cell, 0), "county_height_ft": county[bid]["attributes"]["Height"],
           "county_max_point_ft": county[bid]["attributes"]["Max_Point"], "masts": masts, "prisms": prisms}
    return rec


def main(argv):
    base, out = argv[1], argv[2]
    os.makedirs(out, exist_ok=True)
    frame = g.LevelFrame.load(FRAME)
    with open(os.path.join(base, "county", "county_footprints_2022_viewbox.json")) as handle:
        county = {str(f["attributes"]["OBJECTID"]): f for f in json.load(handle)["features"]}
    rows = {r["bldg_id"]: r for r in csv.DictReader(open(os.path.join(base, "targets.csv"), encoding="utf-8"))}
    dtm6 = load(os.path.join(base, "rasters", "view6ft_dtm.npz"))
    ids = argv[3:] or list(rows.keys())
    with open(os.path.join(out, "towers_record.jsonl"), "a", encoding="utf-8") as rec_file:
        for bid in ids:
            if not os.path.exists(os.path.join(base, "rasters", "bldg1ft", "%s_dsm.npz" % bid)):
                print("no 1 ft surface yet", bid)
                continue
            rec = build(bid, rows.get(bid, {}), base, frame, county, dtm6, out)
            if rec is None:
                print("nothing built", bid)
                continue
            rec_file.write(json.dumps(rec) + "\n")
            print(bid, "terraces", rec["terraces"], "roof %.1f m" % rec["roof_top_m"], "masts", rec["mast_count"],
                  "top %.1f m" % rec["top_incl_masts_m"], "tris", rec["triangles"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
