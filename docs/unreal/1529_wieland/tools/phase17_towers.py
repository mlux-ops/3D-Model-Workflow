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
MIN_AREA_FT2 = float(os.environ.get("P17_MIN_AREA", "150"))  # Zone 1 and 2 runs keep roof items down to 16 sq ft
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
    """Triangles in level cm about a pivot, with UV channel 0 in metres (walls: along the wall and up from the
    ground; roofs: east and north from the pivot), a material number per triangle (0 wall, 1 roof, 2 mast), and the
    same vertices in map feet at their true height (mv), for the check raster."""

    def __init__(self, frame, pivot_map, drop_fn):
        self.v, self.t, self.m, self.uv, self.mv = [], [], [], [], []
        self.frame, self.drop = frame, drop_fn
        self.pe, self.pn, self.ground = pivot_map
        self.pivot = frame.level_from_map(pivot_map[0], pivot_map[1], pivot_map[2])

    def vert(self, e, n, z_ft, u, w):
        x, y, z = self.frame.level_from_map(e, n, z_ft - self.drop(e, n) / FT)
        self.v.append((round(x - self.pivot[0], 2), round(y - self.pivot[1], 2), round(z - self.pivot[2], 2)))
        self.uv.append((round(u, 3), round(w, 3)))
        self.mv.append((e, n, z_ft))
        return len(self.v) - 1

    def walls(self, poly, z0, z1, mat):
        h0, h1 = (z0 - self.ground) * FT, (z1 - self.ground) * FT
        for ring in [poly.exterior] + list(poly.interiors):
            pts = list(ring.coords)[:-1]
            if not ring.is_ccw ^ (ring is not poly.exterior):
                pts = pts[::-1]  # exterior counter-clockwise seen from above, holes clockwise: walls face out
            along = 0.0
            for i in range(len(pts)):
                a, b = pts[i], pts[(i + 1) % len(pts)]
                length = math.hypot(b[0] - a[0], b[1] - a[1]) * FT
                i0, i1 = self.vert(a[0], a[1], z0, along, h0), self.vert(b[0], b[1], z0, along + length, h0)
                i2, i3 = self.vert(b[0], b[1], z1, along + length, h1), self.vert(a[0], a[1], z1, along, h1)
                along += length
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
            ids = [self.vert(e, n, z, (e - self.pe) * FT, (n - self.pn) * FT) for e, n in c]
            self.t.append((ids[0], ids[2], ids[1]))
            self.m.append(mat)

    def soup(self, pts_ft, faces):
        """Add triangles given in map feet (e, n, z), counter-clockwise seen from outside. Each triangle gets its own
        vertices: roofs (normal more than 60 degrees up) are mapped east and north, walls by the horizontal axis they
        face least, so a facade grid stays upright on every wall."""
        for f in faces:
            a, b, c = pts_ft[f[0]], pts_ft[f[1]], pts_ft[f[2]]
            nrm = np.cross(b - a, c - a)
            ln = float(np.linalg.norm(nrm))
            if ln < 1e-9:
                continue
            nrm = nrm / ln
            ids = []
            for p in (a, b, c):
                if abs(nrm[2]) > 0.5:
                    u, w = (p[0] - self.pe) * FT, (p[1] - self.pn) * FT
                elif abs(nrm[0]) > abs(nrm[1]):
                    u, w = (p[1] - self.pn) * FT, (p[2] - self.ground) * FT
                else:
                    u, w = (p[0] - self.pe) * FT, (p[2] - self.ground) * FT
                ids.append(self.vert(float(p[0]), float(p[1]), float(p[2]), u, w))
            self.t.append((ids[0], ids[2], ids[1]))
            self.m.append(1 if nrm[2] > 0.5 else 0)


def raster_top(mv, tris, x0, y1, w, h, ground_ft):
    """Highest non-vertical surface of a mesh over a 1 ft grid, in metres above ground (NaN where none)."""
    z = np.full((h, w), -np.inf)
    P = np.asarray(mv, dtype=np.float64)
    for t in tris:
        a, b, c = P[t[0]], P[t[1]], P[t[2]]
        den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-6:
            continue  # vertical in plan
        c0 = max(int(math.floor(min(a[0], b[0], c[0]) - x0)), 0)
        c1 = min(int(math.ceil(max(a[0], b[0], c[0]) - x0)), w)
        r0 = max(int(math.floor(y1 - max(a[1], b[1], c[1]))), 0)
        r1 = min(int(math.ceil(y1 - min(a[1], b[1], c[1]))), h)
        if c1 <= c0 or r1 <= r0:
            continue
        X, Y = np.meshgrid(x0 + np.arange(c0, c1) + 0.5, y1 - np.arange(r0, r1) - 0.5)
        l1 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / den
        l2 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / den
        l3 = 1.0 - l1 - l2
        inside = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        if not inside.any():
            continue
        sub = z[r0:r1, c0:c1]
        np.maximum(sub, np.where(inside, l1 * a[2] + l2 * b[2] + l3 * c[2], -np.inf), out=sub)
    z = (z - ground_ft) * FT
    z[~np.isfinite(z)] = np.nan
    return z


def interior_cells(hgrid, valid):
    """Cells at least 2 ft from a height step of more than 2 m (walls are judged by the plan check instead)."""
    g0 = np.nan_to_num(hgrid, nan=0.0)
    step = ndimage.maximum_filter(g0, size=5) - ndimage.minimum_filter(g0, size=5)
    return valid & (step < 2.0)


def heightfield(med, bmask, x0, y1, cell, ground_ft, base_ft):
    """A closed surface from the filtered 1 ft heights: a vertex at every cell corner touching the building, at the
    highest of its building cells, two triangles per cell, and a skirt down to the base around the outline; then
    decimated with fast_simplification as far as the 95th-percentile vertical error over the roof stays at or under
    0.25 m. Returns (points in map feet, faces, reduction used, p95 error in m)."""
    import fast_simplification
    h, w = bmask.shape
    hz = np.where(bmask, med, -np.inf)
    pad = np.pad(hz, 1, constant_values=-np.inf)
    corner = np.maximum.reduce([pad[:-1, :-1], pad[:-1, 1:], pad[1:, :-1], pad[1:, 1:]])  # (h+1, w+1)
    used = np.isfinite(corner)
    idx = -np.ones(corner.shape, np.int64)
    idx[used] = np.arange(int(used.sum()))
    rr, cc = np.nonzero(used)
    top = np.column_stack([x0 + cc * cell, y1 - rr * cell, ground_ft + corner[used] / FT])
    nt = len(top)
    br, bc = np.nonzero(bmask)
    a, b, c, d = idx[br, bc], idx[br, bc + 1], idx[br + 1, bc + 1], idx[br + 1, bc]
    # a north-west, b north-east, c south-east, d south-west: (a, d, c) and (a, c, b) run counter-clockwise from above.
    faces = [np.column_stack([a, d, c]), np.column_stack([a, c, b])]
    bot_index = {}

    def bottom(i):
        if i not in bot_index:
            bot_index[i] = nt + len(bot_index)
        return bot_index[i]
    m = np.pad(bmask, 1)
    sk = []
    # For each side of a building cell that faces a non-building cell: the side's two corners, in the order that runs
    # counter-clockwise around the building seen from above (so the wall faces out).
    sides = (((-1, 0), (0, 1), (0, 0)),   # north side: from north-east corner to north-west corner
             ((1, 0), (1, 0), (1, 1)),    # south side: south-west to south-east
             ((0, -1), (0, 0), (1, 0)),   # west side: north-west to south-west
             ((0, 1), (1, 1), (0, 1)))    # east side: south-east to north-east
    for (dr, dc), c1, c2 in sides:
        side = bmask & ~m[1 + dr:1 + dr + h, 1 + dc:1 + dc + w]
        for r, cl in zip(*np.nonzero(side)):
            p, q = int(idx[r + c1[0], cl + c1[1]]), int(idx[r + c2[0], cl + c2[1]])
            sk.append((p, q, bottom(q), bottom(p)))
    pts = [top]
    if sk:
        order = sorted(bot_index, key=bot_index.get)
        bots = top[order].copy()
        bots[:, 2] = base_ft
        pts.append(bots)
        sk = np.array(sk)
        # Outward wall seen from outside: p (top), q (top), bottom(q), bottom(p) runs counter-clockwise.
        faces += [np.column_stack([sk[:, 0], sk[:, 3], sk[:, 2]]), np.column_stack([sk[:, 0], sk[:, 2], sk[:, 1]])]
    P = np.vstack(pts)
    F = np.vstack(faces).astype(np.int64)
    centre = P.mean(axis=0)
    local = P - centre
    ref = np.where(bmask, med, np.nan)
    inner = interior_cells(ref, bmask)
    zr = raster_top(P, F, x0, y1, w, h, ground_ft)
    err = np.abs(zr - ref)[inner]
    err = err[np.isfinite(err)]
    full_p95 = float(np.percentile(err, 95)) if len(err) else 99.0
    # The undecimated surface already differs from the cells by its corner heights (each corner takes the highest
    # of its cells); decimation may add at most 0.05 m to that, and never pass 0.25 m unless the undecimated does.
    bar = max(0.25, full_p95 + 0.05)
    for red in (0.97, 0.93, 0.85, 0.7):
        pp, ff = fast_simplification.simplify(local.astype(np.float32), F.astype(np.int32), target_reduction=red, agg=5)
        pp = pp.astype(np.float64) + centre
        zr = raster_top(pp, ff, x0, y1, w, h, ground_ft)
        err = np.abs(zr - ref)[inner]
        err = err[np.isfinite(err)]
        p95 = float(np.percentile(err, 95)) if len(err) else 99.0
        if p95 <= bar and len(err) > 0.8 * inner.sum():
            return pp, ff, red, p95
    return P, F, 0.0, full_p95


PC_FOLDER = "D:/Wieland1529_lidar/derived"
ZONES = {}
_PC_LABELS = {}
_PC_CACHE = {}  # at most two tiles' arrays in memory (each up to 4 GB unpacked); run the ids grouped by tile


def _tile_arrays(path):
    if path not in _PC_CACHE:
        while len(_PC_CACHE) >= 2:
            _PC_CACHE.pop(next(iter(_PC_CACHE)))
        d = np.load(path)
        _PC_CACHE[path] = {k: d[k] for k in ("x", "y", "z", "cls", "box")}
    return _PC_CACHE[path]


def point_cloud(bid, box=None):
    """Points of this building's box from any streamed tile (x, y, z feet, cls), or None. A Zone 1 or 2 building has
    no box of its own: its points are those of the "SITE300" box (the 300 m square) inside box (map feet)."""
    import glob
    xs, ys, zs, cs = [], [], [], []
    for path in sorted(glob.glob(os.path.join(PC_FOLDER, "pc_*.npz"))):
        if not os.path.exists(path + ".source.txt") or path.endswith("_willis.npz"):
            continue  # still being written by the batch (its record file is written last), or the trial copy
        if path not in _PC_LABELS:
            _PC_LABELS[path] = [str(v) for v in np.load(path)["labels"]]
        labels = _PC_LABELS[path]
        if bid in labels:
            d = _tile_arrays(path)
            sel = d["box"] == labels.index(bid)
        elif box is not None and "SITE300" in labels:
            d = _tile_arrays(path)
            sel = (d["box"] == labels.index("SITE300")) & (d["x"] >= box[0]) & (d["x"] <= box[2]) & (d["y"] >= box[1]) & (d["y"] <= box[3])
        else:
            continue
        xs.append(d["x"][sel]); ys.append(d["y"][sel]); zs.append(d["z"][sel]); cs.append(d["cls"][sel])
    if not xs:
        return None
    return {"x": np.concatenate(xs), "y": np.concatenate(ys), "z": np.concatenate(zs), "cls": np.concatenate(cs)}


def pc_masts(pc, ground_ft, terrace, x0, y1, cell, topmask, top_m, surface=None):
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
        # Not a mast: a taller wall within 15 ft (a neighbour's facade returns), or a large blob on a low roof (a
        # crane standing in 2022).
        blob = lab == i
        ring_ = ndimage.binary_dilation(blob, iterations=5) & ~ndimage.binary_dilation(blob, iterations=1)
        rr3, cc3 = np.nonzero(ring_)
        rr1 = np.clip(rr3 * 3 + 1, 0, h - 1)
        cc1 = np.clip(cc3 * 3 + 1, 0, w - 1)
        if surface is not None and len(rr1) and float(np.nanmax(surface[rr1, cc1])) > base + 0.5 * (top - base):
            continue
        if rad >= 10.0 and top_m < 100.0:
            continue
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
    pc = point_cloud(bid, (x0, y1 - h * cell, x0 + w * cell, y1))
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
    # Trees: the surface model holds the canopy over low roofs (up to 12 m too high near the site). Where the returns
    # say a cell's top is vegetation (classes 3 to 5 above everything else by 1 m), the cell takes the height of the
    # nearest cell whose top is a building return.
    veg_cells = 0
    if pc is not None:
        pcc = ((pc["x"] - x0) / cell).astype(int)
        prr = ((y1 - pc["y"]) / cell).astype(int)
        inb = (pcc >= 0) & (pcc < w) & (prr >= 0) & (prr < h)
        hv = (pc["z"] - ground_ft) * FT
        isveg = np.isin(pc["cls"], [3, 4, 5])
        nonveg = ~np.isin(pc["cls"], [2, 3, 4, 5, 9])
        vg = np.full(h * w, -np.inf)
        bg = np.full(h * w, -np.inf)
        np.maximum.at(vg, prr[inb & isveg] * w + pcc[inb & isveg], hv[inb & isveg])
        np.maximum.at(bg, prr[inb & nonveg] * w + pcc[inb & nonveg], hv[inb & nonveg])
        vg, bg = vg.reshape(h, w), bg.reshape(h, w)
        tree = np.isfinite(vg) & (vg > np.where(np.isfinite(bg), bg, -1e9) + 1.0) & (med > 2.5)
        tree = ndimage.binary_dilation(tree, iterations=1) & ~(np.isfinite(bg) & (bg >= med - 1.0))
        good = np.isfinite(bg) & ~tree
        if tree.any() and good.any():
            _, (ir, ic) = ndimage.distance_transform_edt(~good, return_indices=True)
            fill = np.where(np.isfinite(bg[ir, ic]), bg[ir, ic], 0.0)
            med = np.where(tree, fill, med)
            veg_cells = int(tree.sum())
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
    # Each top is then set to the median of the flat roof cells that took it, so the 0.5 m quantum does not remain.
    for i in range(len(tops)):
        own = flat & (level == i)
        if own.sum() * cell * cell >= MIN_AREA_FT2:
            tops[i] = round(float(np.median(med[own])), 2)
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
        masts = pc_masts(pc, ground_ft, terrace, x0, y1, cell, level == len(tops) - 1, tops[-1], surface=raw_m)
        mast_source = "point cloud"
    # Curvature drop from D1.
    d1e, d1n = frame.map_from_level(D1[0], D1[1])

    def drop(e, n):
        d = math.hypot(e - d1e, n - d1n) * FT
        return d * d / (2.0 * R_EARTH_M) * (1.0 - K_REFRACTION)

    c = outline.centroid
    base_ft = ground_ft - 1.0 / FT  # 1 m below the ground so no gap shows where the ground model is coarser
    mesh = MeshOut(frame, (c.x, c.y, ground_ft), drop)
    prisms = []
    prev_ft = base_ft
    for i, t in enumerate(tops):
        region = clean(region_polygon(level >= i, x0, y1, cell), MIN_AREA_FT2 if i > 0 else 50.0)
        if region.is_empty:
            continue
        top_ft = ground_ft + t / FT
        for poly in region.geoms:
            mesh.walls(poly, prev_ft, top_ft, 0)
            mesh.cap(poly, top_ft, 1)
        prisms.append({"top_m": t, "area_ft2": round(region.area, 1), "wkt": shapely.to_wkt(region, rounding_precision=1)})
        prev_ft = top_ft
    if not mesh.t:
        return None
    # How well the terraces follow the filtered surface: 95th percentile of the vertical difference over the roof,
    # away from walls. Where it is over 0.5 m (sloped or tapered crowns, pitched roofs), a height field is built
    # from the same surface and the one with the smaller difference is kept.
    ref = np.where(bmask, med, np.nan)
    inner = interior_cells(ref, bmask)

    def p95_of(mv, tris):
        zr = raster_top(mv, tris, x0, y1, w, h, ground_ft)
        err = np.abs(zr - ref)[inner]
        err = err[np.isfinite(err)]
        return float(np.percentile(err, 95)) if len(err) else 99.0, zr
    prism_p95, prism_grid = p95_of(mesh.mv, mesh.t)
    form, hf_info, model_grid = "terraces", None, prism_grid
    if prism_p95 > float(os.environ.get("P17_FORM_P95", "0.5")):
        # The filtered surface shaves narrow crowns (St Regis: 349.8 m against 353.7 m in the returns). Where the
        # building's returns were streamed, each building cell takes the higher of the surface and the highest
        # return in the cell (median over 3 by 3 ft, so a single stray return does not count). Masts stay apart.
        hmed = med
        if pc is not None:
            pg = np.full(dsm.size, -np.inf)
            pcc = ((pc["x"] - x0) / cell).astype(int)
            prr = ((y1 - pc["y"]) / cell).astype(int)
            pok = (pcc >= 0) & (pcc < w) & (prr >= 0) & (prr < h) & ~np.isin(pc["cls"], [2, 3, 4, 5, 9])
            np.maximum.at(pg, prr[pok] * w + pcc[pok], (pc["z"][pok] - ground_ft) * FT)
            pg = pg.reshape(h, w)
            pgf = ndimage.median_filter(np.where(np.isfinite(pg), pg, med), size=3)
            near_mast = np.zeros((h, w), bool)
            for m in masts:
                mc, mr = int((m["east"] - x0) / cell), int((y1 - m["north"]) / cell)
                rad = int(m["radius_ft"] / cell) + 3
                near_mast[max(mr - rad, 0):mr + rad + 1, max(mc - rad, 0):mc + rad + 1] = True
            hmed = np.where(bmask & ~near_mast, np.maximum(med, pgf), med)
        pts, faces, red, hf_p95 = heightfield(hmed, bmask, x0, y1, cell, ground_ft, base_ft)
        hf_info = {"reduction": red, "p95_m": round(hf_p95, 3), "faces": int(len(faces))}
        if hf_p95 < prism_p95:
            mesh = MeshOut(frame, (c.x, c.y, ground_ft), drop)
            mesh.soup(pts, faces)
            form = "height field"
            _, model_grid = p95_of(mesh.mv, mesh.t)
    for m in masts:
        poly = Polygon([(m["east"] + m["radius_ft"] * math.cos(a), m["north"] + m["radius_ft"] * math.sin(a))
                        for a in np.linspace(0, 2 * math.pi, 9)[:-1]])
        z0 = ground_ft + m["base_m"] / FT - 0.5 / FT
        z1 = ground_ft + m["top_m"] / FT
        mesh.walls(poly, z0, z1, 2)
        mesh.cap(poly, z1, 2)
    dist = math.hypot(c.x - d1e, c.y - d1n) * FT
    name = "%s_%s" % (os.environ.get("P17_PREFIX", "P17T"), bid)
    zone = ZONES.get(bid) or (4 if dist > 1000 else 3)
    data = {"name": name, "kind": "building", "zone": zone, "pivot": [round(v, 2) for v in mesh.pivot],
            "vertices": mesh.v, "triangles": mesh.t, "tri_mat": mesh.m, "uv0_m": mesh.uv}
    with open(os.path.join(out, name + ".json"), "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    # The model's top surface on the 1 ft grid (true heights, before the curvature drop), for the point-cloud check.
    np.savez_compressed(os.path.join(out, name + "_grid.npz"), z=model_grid.astype(np.float32), x0=x0, y1=y1, cell=cell,
                        ground_ft=ground_ft, tops=np.array(tops))
    top_roof = max(tops)
    top_all = max([top_roof] + [m["top_m"] for m in masts])
    rec = {"id": bid, "name": name, "distance_m": round(dist, 1), "ground_ft": round(ground_ft, 4), "form": form,
           "terrace_p95_m": round(prism_p95, 3), "heightfield": hf_info,
           "terraces": len(prisms), "roof_top_m": round(top_roof, 2), "mast_count": len(masts),
           "top_incl_masts_m": round(top_all, 2), "curvature_drop_m": round(drop(c.x, c.y), 3),
           "placed_top_m": round(top_all - drop(c.x, c.y), 2), "triangles": len(mesh.t),
           "mast_source": mast_source, "height_source": height_source, "tree_cells_replaced": veg_cells, "plan_area_ft2": round(float(bmask.sum()) * cell * cell, 0), "county_height_ft": county[bid]["attributes"]["Height"],
           "county_max_point_ft": county[bid]["attributes"]["Max_Point"], "masts": masts, "prisms": prisms}
    return rec


def main(argv):
    base, out = argv[1], argv[2]
    os.makedirs(out, exist_ok=True)
    frame = g.LevelFrame.load(FRAME)
    with open(os.path.join(base, "county", "county_footprints_2022_viewbox.json")) as handle:
        county = {str(f["attributes"]["OBJECTID"]): f for f in json.load(handle)["features"]}
    rows = {r["bldg_id"]: r for r in csv.DictReader(open(os.path.join(base, os.environ.get("P17_TARGETS", "targets.csv")), encoding="utf-8"))}
    if os.environ.get("P17_ZONES"):
        ZONES.update(json.load(open(os.path.join(base, os.environ["P17_ZONES"]))))
    dtm6 = load(os.path.join(base, "rasters", "view6ft_dtm.npz"))
    ids = argv[3:] or list(rows.keys())
    with open(os.path.join(out, "towers_record.jsonl"), "a", encoding="utf-8", buffering=1) as rec_file:
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
                  "top %.1f m" % rec["top_incl_masts_m"], "tris", rec["triangles"], rec["form"], "terrace p95", rec["terrace_p95_m"], rec["heightfield"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
