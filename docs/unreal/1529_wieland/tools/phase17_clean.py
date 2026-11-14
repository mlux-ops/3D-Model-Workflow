"""Phase 17: buildings with clean, built roof forms, measured from the 2022 laser scan (owner, 2026-11-14: "the roofs
of all the new buildings are jagged and unrealistic").

Usage:
    python -B -P phase17_clean.py <phase17 data folder> <out folder> [county id ...]

Environment (as phase17_towers.py): P17_TARGETS, P17_ZONES (Zone 1 and 2 run), P17_PREFIX (default P17R),
P17_MIN_AREA (smallest roof level, sq ft).

The scan is used only to measure; every visible surface is a built form:

1. Inputs from phase17_towers.prepare(): the 1 ft surface model filtered and freed of tree canopy, the building cells,
   the ground, the classified returns.
2. Main direction of the building: the length-weighted direction of its Cook County outline's edges (modulo 90 deg).
   Every outline is opened by 0.7 ft, simplified (1.5 ft towers, 1.0 ft Zone 1-2), and each edge within the snap angle
   (12 deg towers, 5 deg Zone 1-2) of the main direction or its normal is turned onto it; corners are the
   intersections of successive edges. Curved or irregular shapes keep the simplified outline (straight segments).
3. Roof surface for grouping: a grey opening over 5 by 5 ft removes parapets, chimneys and other thin items, so they
   do not become roof levels.
4. Pitched parts: cells sloped 12 to 65 deg, locally planar, in areas of 100 sq ft or more. Planes are fitted to the
   building returns over the part (RANSAC, 0.15 m, the returns within 2 ft of the outline left out), and the roof is
   the lowest of the planes at each point, which gives straight ridges and hips where planes meet (gable, hip,
   pyramid, shed, mansard). Accepted only where it follows the returns (90th percentile within 0.3 m in Zone 1-2,
   1.0 m for towers) and clearly better than one flat roof. Otherwise a rectilinear part is split at its inside
   corners into rectangles, each fitted alone (cross gables); what still fails goes to step 5.
5. Flat and stepped parts: the opened heights of flat cells are grouped into levels (0.5 m bins with at least the
   minimum area, groups closer than 0.75 m merged; 0.6 m in Zone 1-2); each level is a prism nested in the one below,
   its roof one plane at the median of its own flat cells. A level part smaller than the "big" area (1,500 sq ft
   towers, 150 sq ft Zone 1-2) is a rooftop structure: kept when 1.5 m or more above the level below and 4 sq m or
   more, as a box (its minimum rectangle) or a cylinder (when round), otherwise left out.
6. Parapets: on every flat roof of 300 sq ft or more, the band within 2.5 ft inside the outline; when it stands 0.3 to
   2.5 m above the roof over at least half the band, a parapet ring of the measured height (80th percentile) and
   thickness (band cells above half that height per foot of outline, 0.2 to 0.6 m) is extruded on the outline.
7. Masts and spires: from the returns (phase17_towers.pc_masts) or the surface model, as 12-sided cylinders.
8. Earth curvature from D1, mesh format, record and check grid as phase17_towers.py (material slots: 0 wall,
   1 roof, 2 mast), so phase17_check_towers.py measures the clean forms.
"""

import csv
import json
import math
import os
import sys

import numpy as np
import shapely
import shapely.affinity
from scipy import ndimage
from shapely.geometry import MultiPolygon, Point, Polygon, box as sbox
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wieland_geo as g  # noqa: E402
import phase17_towers as T  # noqa: E402

FT = T.FT
ZONE12 = bool(os.environ.get("P17_ZONES"))
TOL_FT = 1.0 if ZONE12 else 1.5
SNAP_DEG = 5.0 if ZONE12 else 12.0
FIT_P90_M = 0.5 if ZONE12 else 1.0  # to choose the form; the acceptance (0.3 m, 1 m) is measured after, by the check
LEVEL_MIN_FT2 = float(os.environ.get("P17_MIN_AREA", "43" if ZONE12 else "150"))
MERGE_M = 0.6 if ZONE12 else 0.75
BIG_FT2 = 150.0 if ZONE12 else 1500.0
STRUCT_MIN_FT2 = 43.0   # 4 sq m
STRUCT_MIN_M = 1.5
RANSAC_M = 0.15
SLOPE_MIN, SLOPE_MAX = 12.0, 65.0
PITCH_MIN_FT2 = 100.0
NOT_BUILDING = [2, 3, 4, 5, 7, 9, 18]


# ----------------------------------------------------------------------------------------------- outlines

def main_direction(outline):
    """Length-weighted direction of the outline's edges, modulo 90 deg (radians)."""
    sx = sy = 0.0
    for poly in getattr(outline, "geoms", [outline]):
        for ring in [poly.exterior] + list(poly.interiors):
            c = np.asarray(ring.coords)
            d = np.diff(c, axis=0)
            ln = np.hypot(d[:, 0], d[:, 1])
            a = np.arctan2(d[:, 1], d[:, 0]) * 4.0
            sx += float((ln * np.cos(a)).sum())
            sy += float((ln * np.sin(a)).sum())
    return math.atan2(sy, sx) / 4.0


def _reg_ring(coords, theta, tol, snap):
    pts = [np.array(p, dtype=np.float64) for p in coords[:-1]]
    n = len(pts)
    if n < 4:
        return None
    lines = []  # (direction unit vector, offset along the normal, length, original start, original end)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        d = b - a
        ln = float(np.hypot(*d))
        if ln < 1e-6:
            continue
        ang = math.atan2(d[1], d[0])
        rel = (ang - theta) % (math.pi / 2.0)
        dev = min(rel, math.pi / 2.0 - rel)
        if math.degrees(dev) <= snap:
            k = round((ang - theta) / (math.pi / 2.0))
            ang = theta + k * math.pi / 2.0
        u = np.array([math.cos(ang), math.sin(ang)])
        nrm = np.array([-u[1], u[0]])
        mid = (a + b) / 2.0
        lines.append([u, float(mid @ nrm), ln, a, b])
    # Merge successive edges that now run the same way at nearly the same offset.
    merged = []
    for L in lines:
        if merged and float(merged[-1][0] @ L[0]) > 0.99999 and abs(merged[-1][1] - L[1]) < tol:
            M = merged[-1]
            M[1] = (M[1] * M[2] + L[1] * L[2]) / (M[2] + L[2])
            M[2] += L[2]
            M[4] = L[4]
        else:
            merged.append(L)
    if len(merged) > 1 and float(merged[-1][0] @ merged[0][0]) > 0.99999 and abs(merged[-1][1] - merged[0][1]) < tol:
        M, L = merged[0], merged.pop()
        M[1] = (M[1] * M[2] + L[1] * L[2]) / (M[2] + L[2])
        M[2] += L[2]
        M[3] = L[3]
    if len(merged) < 3:
        return None
    out = []
    m = len(merged)
    for i in range(m):
        A, B = merged[i - 1], merged[i]
        ua, ub = A[0], B[0]
        na, nb = np.array([-ua[1], ua[0]]), np.array([-ub[1], ub[0]])
        junction = B[3]
        det = na[0] * nb[1] - na[1] * nb[0]
        if abs(det) > 1e-6:
            p = np.linalg.solve(np.array([na, nb]), np.array([A[1], B[1]]))
            if float(np.hypot(*(p - junction))) <= 4.0 * tol + 2.0:
                out.append(p)
                continue
        # Parallel (a jog) or a far intersection: the junction projected onto each line.
        out.append(junction - na * (float(junction @ na) - A[1]))
        out.append(junction - nb * (float(junction @ nb) - B[1]))
    return [tuple(p) for p in out]


def regularize(poly, theta, tol=None, snap=None):
    """Straight walls and real corners: simplified, edges snapped to the main directions (see the module notes)."""
    tol = TOL_FT if tol is None else tol
    snap = SNAP_DEG if snap is None else snap
    s = poly.simplify(tol, preserve_topology=True)
    if s.is_empty or not isinstance(s, Polygon):
        return s
    ext = _reg_ring(list(s.exterior.coords), theta, tol, snap)
    if ext is None:
        return s
    holes = []
    for r in s.interiors:
        if Polygon(r).area < 100.0:
            continue
        hr = _reg_ring(list(r.coords), theta, tol, snap)
        if hr is not None:
            holes.append(hr)
    try:
        cand = Polygon(ext, holes).buffer(0)
    except Exception:
        return s
    if isinstance(cand, MultiPolygon):
        cand = max(cand.geoms, key=lambda q: q.area)
    if cand.is_empty or not (0.92 < cand.area / max(s.area, 1e-6) < 1.08) or cand.hausdorff_distance(s) > 2.0 * tol + 1.0:
        return s
    return cand.simplify(0.05, preserve_topology=True)


def fit_outline(poly, meas, Xg, Yg):
    """The county outline's walls, each moved along its normal onto the edge the returns show (median signed distance
    of the measured edge cells within 5 ft of the wall, at least 8 of them); a wall with no measured edge near it (a
    party wall) stays. Corners are the intersections of successive moved walls, so they stay true corners."""
    em = meas & ~ndimage.binary_erosion(meas)
    ex, ey = Xg[em], Yg[em]
    pts = list(poly.exterior.coords)[:-1]
    if not shapely.geometry.LinearRing(pts).is_ccw:
        pts = pts[::-1]
    n = len(pts)
    if n < 3 or not len(ex):
        return poly, []
    lines, shifts = [], []
    for i in range(n):
        a, b = np.array(pts[i]), np.array(pts[(i + 1) % n])
        d = b - a
        L = float(np.hypot(*d))
        u = d / max(L, 1e-9)
        nr = np.array([u[1], -u[0]])  # outward for a counter-clockwise ring
        rel = np.stack([ex - a[0], ey - a[1]], 1)
        t = rel @ u
        s = rel @ nr
        sel = (t > min(2.0, 0.2 * L)) & (t < L - min(2.0, 0.2 * L)) & (np.abs(s) < 5.0)
        off = float(np.median(s[sel])) + 0.5 if sel.sum() >= 8 else 0.0
        shifts.append(round(off * FT, 2))
        lines.append((u, nr, float(a @ nr) + off, a, b))
    out = []
    for i in range(n):
        A, Bl = lines[i - 1], lines[i]
        det = A[1][0] * Bl[1][1] - A[1][1] * Bl[1][0]
        if abs(det) > 1e-6:
            q = np.linalg.solve(np.array([A[1], Bl[1]]), np.array([A[2], Bl[2]]))
            if float(np.hypot(*(q - Bl[3]))) < 8.0:
                out.append(tuple(q))
                continue
        j = Bl[3]
        out.append(tuple(j + A[1] * (A[2] - float(j @ A[1]))))
        out.append(tuple(j + Bl[1] * (Bl[2] - float(j @ Bl[1]))))
    cand = Polygon(out).buffer(0)
    if isinstance(cand, MultiPolygon):
        cand = max(cand.geoms, key=lambda r: r.area)
    if cand.is_empty or not (0.8 < cand.area / max(poly.area, 1e-6) < 1.35):
        return poly, []
    return cand.simplify(0.05), shifts


def mask_polygons(mask, x0, y1, cell, min_area):
    geom = T.region_polygon(mask, x0, y1, cell)
    geom = geom.buffer(-0.7, join_style=2).buffer(0.7, join_style=2)
    out = []
    for p in getattr(geom, "geoms", [geom]):
        if isinstance(p, Polygon) and p.area >= min_area:
            out.append(Polygon(p.exterior, [r for r in p.interiors if Polygon(r).area >= 100.0]))
    return out


def poly_mask(poly, x0, y1, w, h):
    X, Y = np.meshgrid(x0 + np.arange(w) + 0.5, y1 - np.arange(h) - 0.5)
    return shapely.contains_xy(poly, X, Y)


# ----------------------------------------------------------------------------------------------- planes

def ransac_planes(E, N, Z, max_planes=8, seed=7):
    """Planes z = a e + b n + c (e, n in feet about their mean, z in m) fitted one after another by RANSAC
    (RANSAC_M), each kept to its largest connected patch on a 1 ft grid, at least 25 returns and 4 percent of all."""
    rng = np.random.default_rng(seed)
    e0, n0 = float(E.mean()), float(N.mean())
    e, n, z = E - e0, N - n0, Z.copy()
    alive = np.ones(len(z), bool)
    planes = []
    need = max(25, int(0.04 * len(z)))
    for _ in range(max_planes):
        idx = np.nonzero(alive)[0]
        if len(idx) < need:
            break
        sub = idx if len(idx) <= 20000 else rng.choice(idx, 20000, replace=False)
        S = rng.choice(sub, (500, 3))
        A = np.stack([e[S], n[S], np.ones_like(e[S])], axis=-1)
        ok = np.abs(np.linalg.det(A)) > 1e-3
        if not ok.any():
            break
        coef = np.linalg.solve(A[ok], z[S][ok][..., None])[..., 0]
        res = np.abs(e[sub][None, :] * coef[:, 0:1] + n[sub][None, :] * coef[:, 1:2] + coef[:, 2:3] - z[sub][None, :])
        best = coef[int((res < RANSAC_M).sum(axis=1).argmax())]
        for _ in range(2):
            r = np.abs(e[idx] * best[0] + n[idx] * best[1] + best[2] - z[idx])
            inl = idx[r < RANSAC_M]
            if len(inl) < 3:
                break
            best = np.linalg.lstsq(np.stack([e[inl], n[inl], np.ones(len(inl))], 1), z[inl], rcond=None)[0]
        r = np.abs(e[idx] * best[0] + n[idx] * best[1] + best[2] - z[idx])
        inl = idx[r < RANSAC_M]
        if len(inl) < need:
            break
        # Largest connected patch of inliers.
        ce, cn = np.floor(e[inl] - e[inl].min()).astype(int), np.floor(n[inl] - n[inl].min()).astype(int)
        occ = np.zeros((cn.max() + 1, ce.max() + 1), bool)
        occ[cn, ce] = True
        lab, nl = ndimage.label(ndimage.binary_closing(occ, iterations=1) | occ, structure=np.ones((3, 3)))
        pl = lab[cn, ce]
        if nl > 1:
            big = np.bincount(pl[pl > 0]).argmax()
            patch = inl[pl == big]
        else:
            patch = inl
        alive[inl] = False
        if len(patch) < need:
            continue
        slope = math.degrees(math.atan(math.hypot(best[0], best[1]) / FT))
        if slope > 70.0:
            continue
        c = best[2] - best[0] * e0 - best[1] * n0  # back to absolute e, n
        planes.append((float(best[0]), float(best[1]), float(c), int(len(patch))))
    return planes


def plane_z(pl, e, n):
    return pl[0] * e + pl[1] * n + pl[2]


def clip_halfplane(coords, fa, fb, fc):
    """Convex polygon (list of (e, n)) clipped to fa e + fb n + fc <= 0 (Sutherland-Hodgman)."""
    out = []
    m = len(coords)
    for i in range(m):
        P, Q = coords[i], coords[(i + 1) % m]
        fp, fq = fa * P[0] + fb * P[1] + fc, fa * Q[0] + fb * Q[1] + fc
        if fp <= 0:
            out.append(P)
        if (fp < 0 < fq) or (fq < 0 < fp):
            t = fp / (fp - fq)
            out.append((P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])))
    return out


def envelope_regions(poly, planes):
    """For each plane, the part of poly where it is the lowest of the planes. Shared edges are where two planes meet
    (ridges and hips), so the faces join without steps."""
    minx, miny, maxx, maxy = poly.bounds
    boxc = [(minx - 10, miny - 10), (maxx + 10, miny - 10), (maxx + 10, maxy + 10), (minx - 10, maxy + 10)]
    regs = []
    for i, pi in enumerate(planes):
        cv = list(boxc)
        for j, pj in enumerate(planes):
            if i == j or not cv:
                continue
            fa, fb, fc = pi[0] - pj[0], pi[1] - pj[1], pi[2] - pj[2]
            if abs(fa) < 1e-9 and abs(fb) < 1e-9:
                if fc > 0 or (fc == 0 and j < i):
                    cv = []
                continue
            cv = clip_halfplane(cv, fa, fb, fc)
        if len(cv) < 3:
            continue
        r = poly.intersection(Polygon(cv))
        parts = [q for q in getattr(r, "geoms", [r]) if isinstance(q, Polygon) and q.area > 1.0]
        if parts:
            regs.append((i, parts))
    return regs


def env_grid(planes, X, Y):
    return np.min(np.stack([plane_z(p, X, Y) for p in planes]), axis=0)


def slope_deg(pl):
    return math.degrees(math.atan(math.hypot(pl[0], pl[1]) / FT))


def fit_part(pts, qm, Xg, Yg, ref, addons=True, full=None, planes=None):
    """Planes for one part (cells qm) from its returns; accepted when the lowest-plane roof follows the reference
    surface within FIT_P90_M (90th percentile) and beats a single flat roof. Dormers and other raised items (cells
    0.3 m or more above the planes, in patches of 4 sq m or more) are left out of the judgement and returned as a mask,
    to be built as parts of their own. Returns (planes, p90 of planes, p90 flat, raised-items mask) or None."""
    E, N, Z = pts
    if qm.sum() < 20:
        return None
    given = planes is not None
    if not given:
        if len(Z) < 40:
            return None
        planes = ransac_planes(E, N, Z)
    if not planes:
        return None
    Xc, Yc, Zc = Xg[qm], Yg[qm], ref[qm]
    zf = float(np.median(Zc))
    p90_flat = float(np.percentile(np.abs(Zc - zf), 90))

    def score(pls):
        # 75th percentile while choosing planes, so raised items (a dormer's own plane) do not decide.
        return float(np.percentile(np.abs(env_grid(pls, Xc, Yc) - Zc), 75))
    best = score(planes)
    # A plane below the others over much of the part (a dormer's flat top) cuts the ridge: leave planes out one at a
    # time while that helps.
    improved = not given
    while improved and len(planes) > 1:
        improved = False
        for k in range(len(planes)):
            trial = planes[:k] + planes[k + 1:]
            st = score(trial)
            if st < best - 0.02:
                planes, best, improved = trial, st, True
                break
    if all(slope_deg(pl) < 3.0 for pl in planes):
        return None  # flat: the flat path builds it, with its parapet
    full = qm if full is None else (full | qm)
    zen = np.full(qm.shape, np.nan)
    zen[full] = env_grid(planes, Xg[full], Yg[full])
    raised = np.zeros(qm.shape, bool)
    if addons:
        above = full & (ref - np.nan_to_num(zen, nan=1e9) > 0.3)
        lab, nl = ndimage.label(ndimage.binary_opening(above, iterations=1))
        for i in range(1, nl + 1):
            comp = lab == i
            if comp.sum() >= STRUCT_MIN_FT2:
                raised |= comp
    judge = qm & ~ndimage.binary_dilation(raised, iterations=1)
    if judge.sum() < 20:
        return None
    p90 = float(np.percentile(np.abs(zen[judge] - ref[judge]), 90))
    if os.environ.get("P17_DEBUG"):
        print("  fit: planes", [(round(slope_deg(pl), 1), pl[3]) for pl in planes], "p90 %.3f flat %.3f raised %d cells %d"
              % (p90, p90_flat, int(raised.sum()), int(qm.sum())))
    if p90 <= FIT_P90_M and p90 < 0.6 * p90_flat:
        return planes, p90, p90_flat, raised
    return None


def rect_pieces(poly, theta):
    """A rectilinear outline split at its inside corners into rectangles (slabs along whichever axis gives fewer
    pieces). None when the outline is not rectilinear."""
    rot = shapely.affinity.rotate(poly, -theta, origin=(0, 0), use_radians=True)
    c = np.asarray(rot.exterior.coords)
    d = np.diff(c, axis=0)
    if not np.all((np.abs(d[:, 0]) < 0.05) | (np.abs(d[:, 1]) < 0.05)):
        return None
    best = None
    for axis in (0, 1):
        cuts = sorted(set(np.round(c[:, axis], 2)))
        pieces = []
        for a, b in zip(cuts[:-1], cuts[1:]):
            slab = sbox(a, -1e7, b, 1e7) if axis == 0 else sbox(-1e7, a, 1e7, b)
            r = rot.intersection(slab)
            for q in getattr(r, "geoms", [r]):
                if isinstance(q, Polygon) and q.area > 1.0:
                    pieces.append(q.envelope)
        # Merge neighbours with the same extent across the slab.
        merged = []
        for q in sorted(pieces, key=lambda q: q.bounds[axis]):
            for i, m in enumerate(merged):
                mb, qb = m.bounds, q.bounds
                o = 1 - axis
                if abs(mb[o] - qb[o]) < 0.1 and abs(mb[o + 2] - qb[o + 2]) < 0.1 and abs(mb[axis + 2] - qb[axis]) < 0.1:
                    merged[i] = m.union(q).envelope
                    break
            else:
                merged.append(q)
        if best is None or len(merged) < len(best):
            best = merged
    if not best or len(best) < 2 or len(best) > 6:
        return None
    return [shapely.affinity.rotate(q, theta, origin=(0, 0), use_radians=True) for q in best]


# ----------------------------------------------------------------------------------------------- mesh

class CleanMesh(T.MeshOut):
    """MeshOut with planar roof faces and walls whose top follows a roof."""

    def tri(self, P3, uv, mat):
        """One triangle given counter-clockwise seen from outside, points (e, n, z_ft)."""
        ids = [self.vert(p[0], p[1], p[2], u[0], u[1]) for p, u in zip(P3, uv)]
        self.t.append((ids[0], ids[2], ids[1]))
        self.m.append(mat)

    def roof_face(self, poly, zfun, grad, mat=1):
        """Planar roof over poly (plan), z_ft = zfun(e, n). UV: along the eave and up the slope, in metres of surface."""
        ga, gb = grad
        gl = math.hypot(ga, gb)
        if gl > 1e-9:
            up = (ga / gl, gb / gl)
            stretch = math.sqrt(1.0 + (gl / FT) ** 2)
        else:
            up, stretch = (0.0, 1.0), 1.0
        along = (up[1], -up[0])
        tris = shapely.constrained_delaunay_triangles(poly)
        for t in getattr(tris, "geoms", []):
            c = list(t.exterior.coords)[:3]
            if Polygon(c).area < 1e-4:
                continue
            if not Polygon(c).exterior.is_ccw:
                c = c[::-1]
            P3 = [(e, n, zfun(e, n)) for e, n in c]
            uv = [(((e - self.pe) * along[0] + (n - self.pn) * along[1]) * FT,
                   ((e - self.pe) * up[0] + (n - self.pn) * up[1]) * FT * stretch) for e, n in c]
            self.tri(P3, uv, mat)

    def follow_walls(self, ring_pts, base_ft, top_fun, mat=0):
        """Walls on a ring given counter-clockwise from above (outward facing), from base_ft up to top_fun(e, n)."""
        along = 0.0
        m = len(ring_pts)
        for i in range(m):
            a, b = ring_pts[i], ring_pts[(i + 1) % m]
            ln = math.hypot(b[0] - a[0], b[1] - a[1]) * FT
            if ln < 1e-4:
                continue
            za, zb = top_fun(*a), top_fun(*b)
            h0 = (base_ft - self.ground) * FT
            i0 = self.vert(a[0], a[1], base_ft, along, h0)
            i1 = self.vert(b[0], b[1], base_ft, along + ln, h0)
            i2 = self.vert(b[0], b[1], zb, along + ln, (zb - self.ground) * FT)
            i3 = self.vert(a[0], a[1], za, along, (za - self.ground) * FT)
            along += ln
            self.t += [(i0, i2, i1), (i0, i3, i2)]
            self.m += [mat, mat]


def ring_with_points(ring, extra, eps=0.01):
    """Ring coordinates (counter-clockwise, open) with every extra point that lies on one of its edges inserted."""
    pts = list(ring.coords)[:-1]
    if not shapely.geometry.LinearRing(pts).is_ccw:
        pts = pts[::-1]
    out = []
    ex = np.asarray(extra) if len(extra) else np.zeros((0, 2))
    for i in range(len(pts)):
        a, b = np.array(pts[i]), np.array(pts[(i + 1) % len(pts)])
        out.append(tuple(a))
        d = b - a
        L2 = float(d @ d)
        if L2 < 1e-12 or not len(ex):
            continue
        t = ((ex - a) @ d) / L2
        proj = a + np.outer(t, d)
        dist = np.hypot(*(ex - proj).T)
        sel = (t > 1e-4) & (t < 1 - 1e-4) & (dist < eps)
        for tt in sorted(set(np.round(t[sel], 6))):
            out.append(tuple(a + tt * d))
    return out


def poly_with_points(poly, extra):
    ext = ring_with_points(poly.exterior, extra)
    holes = [ring_with_points(r, extra)[::-1] for r in poly.interiors]
    return Polygon(ext, holes)


def circular(poly):
    return 4.0 * math.pi * poly.area / max(poly.length ** 2, 1e-9) > 0.85


def ngon(cx, cy, r, k):
    return Polygon([(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, k + 1)[:-1]])


# ----------------------------------------------------------------------------------------------- building

def build(bid, base, frame, county, dtm6, out):
    p = T.prepare(bid, base, county, dtm6)
    if p is None:
        return None
    x0, y1, cell, h, w = p["x0"], p["y1"], p["cell"], p["h"], p["w"]
    outline, ground_ft, pc, raw_m, med, bmask = p["outline"], p["ground_ft"], p["pc"], p["raw_m"], p["med"], p["bmask"]
    theta = main_direction(outline)
    Xg, Yg = np.meshgrid(x0 + np.arange(w) + 0.5, y1 - np.arange(h) - 0.5)
    # Roof surface for grouping: thin raised items (parapets, chimneys) opened away.
    med0 = np.where(bmask, med, 0.0)
    roofz = np.where(bmask, ndimage.grey_opening(med0, size=(5, 5)), 0.0)
    dt = ndimage.distance_transform_edt(bmask)
    # Building returns, metres above ground.
    if pc is not None:
        keep = ~np.isin(pc["cls"], NOT_BUILDING)
        PE, PN, PZ = pc["x"][keep], pc["y"][keep], (pc["z"][keep] - ground_ft) * FT
        pcc = np.floor(PE - x0).astype(int)
        prr = np.floor(y1 - PN).astype(int)
        inb = (pcc >= 0) & (pcc < w) & (prr >= 0) & (prr < h)
        PE, PN, PZ, pcc, prr = PE[inb], PN[inb], PZ[inb], pcc[inb], prr[inb]
        rgrid = np.full(h * w, -np.inf)
        np.maximum.at(rgrid, prr * w + pcc, PZ)
        rgrid = rgrid.reshape(h, w)
        # Judging surface: the highest building return per cell, 3 by 3 median (the surface model is smoothed).
        refz = ndimage.median_filter(np.where(np.isfinite(rgrid), rgrid, med), size=3)
    else:
        PE = PN = PZ = pcc = prr = None
        rgrid, refz = None, med
    parts_rec = []

    # ---- pitched parts
    sm = ndimage.gaussian_filter(roofz, 1.0)
    gy_, gx_ = np.gradient(sm)
    slope = np.degrees(np.arctan(np.hypot(gx_, gy_) / FT))
    lap = np.abs(ndimage.laplace(sm))
    sloped = bmask & (dt > 2) & (slope >= SLOPE_MIN) & (slope <= SLOPE_MAX) & (lap < 0.08)
    sloped = ndimage.binary_opening(sloped, iterations=1)
    sloped = ndimage.binary_closing(sloped, iterations=2)
    lab, nl = ndimage.label(sloped)
    # Footprint: the county outline, regularized, each wall moved onto the edge the returns show.
    if PE is not None:
        meas = ndimage.binary_fill_holes(ndimage.binary_closing(rgrid > 2.5, iterations=1))
    else:
        meas = bmask
    near = ndimage.binary_dilation(poly_mask(outline.buffer(6.0), x0, y1, w, h), iterations=1)
    meas = meas & near
    bpolys, wall_shifts = [], []
    for cp in getattr(outline, "geoms", [outline]):
        if not isinstance(cp, Polygon) or cp.area < 50.0:
            continue
        fp, sh_ = fit_outline(regularize(cp, theta), meas, Xg, Yg)
        if isinstance(fp, Polygon) and not fp.is_empty:
            bpolys.append(fp)
            wall_shifts += sh_
    fp_union = unary_union(bpolys) if bpolys else None
    if fp_union is not None:
        fpm = poly_mask(fp_union, x0, y1, w, h)
        bmask = bmask & fpm if (bmask & fpm).sum() >= 50 else bmask
    pitched_polys = []   # (polygon, planes, p90, p90_flat, kind)
    raised_all = []

    def fit_poly(q, addons, planes=None):
        inner = q.buffer(-2.0, join_style=2)
        if inner.is_empty:
            return None
        qm = poly_mask(inner, x0, y1, w, h) & bmask
        full = poly_mask(q, x0, y1, w, h) & bmask
        if PE is not None:
            sel = qm[prr, pcc] & (np.abs(PZ - med[prr, pcc]) < 1.5)
            pts = (PE[sel], PN[sel], PZ[sel])
        else:
            pts = (Xg[qm], Yg[qm], med[qm])
        return fit_part(pts, qm, Xg, Yg, refz, addons, full, planes)
    for i in range(1, nl + 1):
        comp = lab == i
        if comp.sum() < PITCH_MIN_FT2:
            continue
        region = ndimage.binary_fill_holes(comp)
        region = ndimage.binary_dilation(region, structure=np.ones((3, 3)), iterations=4) & bmask
        for poly in mask_polygons(region, x0, y1, cell, PITCH_MIN_FT2):
            poly = regularize(poly, theta)
            # A pitched part that covers most of a building outline takes that outline whole (its true corners).
            for bp in bpolys:
                if bp.intersection(poly).area >= 0.85 * bp.area:
                    poly = bp
                    break
            else:
                poly = poly.intersection(unary_union(bpolys)) if bpolys else poly
                if isinstance(poly, MultiPolygon):
                    poly = max(poly.geoms, key=lambda r: r.area)
            if poly.is_empty or not isinstance(poly, Polygon):
                continue
            todo = [(poly, "pitched")]
            while todo:
                q, kind = todo.pop()
                fit = fit_poly(q, True)
                if fit is not None:
                    # The same planes tried over the whole footprint part that holds most of q: kept when they fit it.
                    for bp in bpolys:
                        if bp is not q and bp.intersection(q).area >= 0.3 * q.area:
                            fb = fit_poly(bp, True, fit[0])
                            if fb is not None:
                                q, fit = bp, fb
                            break
                    pitched_polys.append((q, fit[0], fit[1], fit[2], kind))
                    raised_all.append(fit[3])
                elif kind == "pitched":
                    pieces = rect_pieces(q, theta)
                    if pieces:
                        todo += [(r, "pitched, split at inside corners") for r in pieces]
    # Pitched parts must not overlap: later (smaller) ones are cut by earlier ones.
    clean_pitched = []
    taken = Polygon()
    for q, planes, p90, p90f, kind in sorted(pitched_polys, key=lambda t: -t[0].area):
        q2 = q.difference(taken)
        if isinstance(q2, MultiPolygon):
            q2 = max(q2.geoms, key=lambda r: r.area)
        if q2.is_empty or q2.area < PITCH_MIN_FT2 * 0.5:
            continue
        q2 = q2.simplify(0.05)
        clean_pitched.append((q2, planes, p90, p90f, kind))
        taken = taken.union(q2)
    pitched_mask = poly_mask(taken, x0, y1, w, h) if not taken.is_empty else np.zeros((h, w), bool)

    # ---- flat and stepped parts
    fmask = bmask & ~pitched_mask
    local_sd = np.sqrt(np.maximum(ndimage.uniform_filter(roofz * roofz, 5) - ndimage.uniform_filter(roofz, 5) ** 2, 0.0))
    flat = fmask & (local_sd < 0.4)
    if flat.sum() < LEVEL_MIN_FT2:
        flat = fmask
    tops = []
    if fmask.sum() >= 50:
        q = np.round(roofz[flat] * 2.0) / 2.0
        vals, counts = np.unique(q, return_counts=True)
        tops = [float(v) for v, a in zip(vals, counts) if a >= LEVEL_MIN_FT2 and v > 2.5]
        if not tops and flat.any():
            tops = [float(np.median(roofz[flat]))]
        merged = []
        for t in sorted(tops):
            if merged and t - merged[-1][-1] < MERGE_M:
                merged[-1].append(t)
            else:
                merged.append([t])
        area_of = dict(zip(vals.tolist(), counts.tolist()))
        tops = [max(grp, key=lambda t: area_of.get(t, 0)) for grp in merged]
    level = np.full((h, w), -1, np.int32)
    if tops:
        tarr = np.array(tops)
        level = np.where(fmask, np.abs(roofz[..., None] - tarr[None, None, :]).argmin(axis=-1), -1).astype(np.int32)
        for i in range(len(tops)):
            own = flat & (level == i)
            if own.sum() >= max(LEVEL_MIN_FT2 * 0.5, 10):
                tops[i] = round(float(np.median(roofz[own])), 2)
    d1e, d1n = frame.map_from_level(T.D1[0], T.D1[1])

    def drop(e, n):
        d = math.hypot(e - d1e, n - d1n) * FT
        return d * d / (2.0 * T.R_EARTH_M) * (1.0 - T.K_REFRACTION)

    c = outline.centroid
    base_ft = ground_ft - 1.0 / FT
    mesh = CleanMesh(frame, (c.x, c.y, ground_ft), drop)
    zft = lambda m_: ground_ft + m_ / FT  # noqa: E731
    prisms = []
    structures = []
    # Level parts, nested: each part of level i stands on the part of level i-1 that holds it.
    parents = [(None, base_ft, -1)]  # (polygon or None for the whole building, its top in feet, level)
    level_polys = {}
    for i, t in enumerate(tops):
        polys = mask_polygons(fmask & (level >= i), x0, y1, cell, STRUCT_MIN_FT2)
        made = []
        for raw in polys:
            # Its parent: the lower part that holds most of it.
            par_poly, par_top, par_lv = None, base_ft, -1
            for lv in range(i - 1, -1, -1):
                for pp, ptop in level_polys.get(lv, []):
                    if pp.intersection(raw).area > 0.5 * raw.area:
                        par_poly, par_top, par_lv = pp, ptop, lv
                        break
                if par_poly is not None:
                    break
            dh = t - ((par_top - ground_ft) * FT if par_poly is not None else 0.0)
            top_ft = zft(t)
            if par_poly is not None and raw.area < BIG_FT2:
                # A rooftop structure.
                if dh < STRUCT_MIN_M or raw.area < STRUCT_MIN_FT2:
                    continue
                if circular(raw):
                    cc_ = raw.centroid
                    shape = ngon(cc_.x, cc_.y, math.sqrt(raw.area / math.pi), 24)
                    kind = "cylinder"
                else:
                    shape = raw.minimum_rotated_rectangle
                    kind = "box"
                shape = shape.intersection(par_poly)
                if shape.is_empty or not isinstance(shape, Polygon):
                    continue
                shape = shape.simplify(0.05)
                mesh.walls(shape, par_top - 0.1 / FT, top_ft, 0)
                mesh.cap(shape, top_ft, 1)
                structures.append({"kind": kind, "top_m": t, "height_m": round(dh, 2), "area_ft2": round(shape.area, 1)})
                continue
            if par_poly is None and i > 0 and raw.area < BIG_FT2 and dh < STRUCT_MIN_M:
                continue
            poly = regularize(raw, theta)
            if par_poly is None and fp_union is not None:
                for bp in bpolys:
                    if bp.intersection(raw).area >= 0.7 * bp.area:
                        poly = bp
                        break
                else:
                    poly = poly.intersection(fp_union)
                    if isinstance(poly, MultiPolygon):
                        poly = max(poly.geoms, key=lambda r: r.area)
            if par_poly is not None:
                poly = poly.intersection(par_poly)
                poly = poly.buffer(-0.2, join_style=2).buffer(0.2, join_style=2)
                if isinstance(poly, MultiPolygon):
                    poly = max(poly.geoms, key=lambda r: r.area)
                if poly.is_empty or not isinstance(poly, Polygon):
                    continue
                poly = poly.simplify(0.05)
            if not taken.is_empty:
                poly = poly.difference(taken).buffer(-1.5, join_style=2).buffer(1.5, join_style=2)
            for pq in getattr(poly, "geoms", [poly]):
                if not isinstance(pq, Polygon) or pq.area < STRUCT_MIN_FT2:
                    continue
                pq = pq.simplify(0.05)
                bottom = par_top if par_poly is not None else base_ft
                # Parapet: band within 2.5 ft inside the outline, against the level's roof.
                par = None
                if pq.area >= 300.0:
                    band_poly = pq.difference(pq.buffer(-2.5, join_style=2))
                    bm = poly_mask(band_poly, x0, y1, w, h) & bmask
                    if bm.sum() >= 20:
                        rel = med[bm] - t
                        hp = float(np.percentile(rel, 80))
                        if 0.3 <= hp <= 2.5 and float(np.mean(rel > 0.5 * hp)) >= 0.5:
                            th_ft = float(np.sum(rel > 0.5 * hp)) / max(pq.exterior.length, 1.0)
                            th_ft = min(max(th_ft, 0.2 / FT), 0.6 / FT)
                            par = (round(hp, 2), round(th_ft * FT, 2))
                mesh.walls(pq, bottom, top_ft, 0)
                if par is not None:
                    inner = pq.buffer(-par[1] / FT, join_style=2)
                    inner = max(inner.geoms, key=lambda r: r.area) if isinstance(inner, MultiPolygon) else inner
                    if inner.is_empty:
                        mesh.cap(pq, top_ft, 1)
                        par = None
                    else:
                        ring = pq.difference(inner)
                        mesh.cap(inner, top_ft, 1)
                        for rq in getattr(ring, "geoms", [ring]):
                            if isinstance(rq, Polygon):
                                mesh.walls(rq, top_ft, top_ft + par[0] / FT, 0)
                                mesh.cap(rq, top_ft + par[0] / FT, 0)
                else:
                    mesh.cap(pq, top_ft, 1)
                made.append((pq, top_ft))
                prisms.append({"level": i, "top_m": t, "area_ft2": round(pq.area, 1), "parapet_m": par,
                               "wkt": shapely.to_wkt(pq, rounding_precision=1)})
        level_polys[i] = made
    # Pitched parts.
    for q, planes, p90, p90f, kind in clean_pitched:
        regs = envelope_regions(q, planes)
        allpts = [pt for _, ps in regs for r in ps for pt in r.exterior.coords]
        allpts += list(q.exterior.coords)
        for k, ps in regs:
            pl = planes[k]
            for r in ps:
                r2 = poly_with_points(r, allpts)
                mesh.roof_face(r2, lambda e, n, pl=pl: zft(plane_z(pl, e, n)), (pl[0], pl[1]))
        ring = ring_with_points(q.exterior, allpts)
        mesh.follow_walls(ring, base_ft, lambda e, n: zft(min(plane_z(pl, e, n) for pl in planes)))
        ridge = max(min(plane_z(pl, e, n) for pl in planes) for e, n in allpts)
        eave = min(min(plane_z(pl, e, n) for pl in planes) for e, n in q.exterior.coords)
        parts_rec.append({"kind": kind, "planes": len(planes), "fit_p90_m": round(p90, 3), "flat_p90_m": round(p90f, 3),
                          "ridge_m": round(ridge, 2), "eave_m": round(eave, 2), "area_ft2": round(q.area, 1),
                          "wkt": shapely.to_wkt(q, rounding_precision=1)})
        prisms.append({"level": "pitched", "top_m": round(ridge, 2), "area_ft2": round(q.area, 1), "parapet_m": None,
                       "wkt": shapely.to_wkt(q, rounding_precision=1)})
    # Dormers and other raised items on pitched roofs: each a rectangle with its own fitted planes, or a flat box.
    raised = np.zeros((h, w), bool)
    for rm in raised_all:
        raised |= rm
    for comp_poly in mask_polygons(raised, x0, y1, cell, STRUCT_MIN_FT2):
        shape = regularize(comp_poly, theta)
        mrr = shape.minimum_rotated_rectangle
        if shape.area / max(mrr.area, 1e-6) > 0.8:
            shape = mrr
        shape = shape.intersection(taken)
        if isinstance(shape, MultiPolygon):
            shape = max(shape.geoms, key=lambda r: r.area)
        if shape.is_empty or not isinstance(shape, Polygon) or shape.area < STRUCT_MIN_FT2:
            continue
        shape = shape.simplify(0.05)
        sm_ = poly_mask(shape, x0, y1, w, h) & bmask
        fit = fit_poly(shape, False)
        if fit is not None:
            planes = fit[0]
            regs = envelope_regions(shape, planes)
            allpts = [pt for _, ps in regs for r in ps for pt in r.exterior.coords] + list(shape.exterior.coords)
            for k, ps in regs:
                pl = planes[k]
                for r in ps:
                    mesh.roof_face(poly_with_points(r, allpts), lambda e, n, pl=pl: zft(plane_z(pl, e, n)), (pl[0], pl[1]))
            mesh.follow_walls(ring_with_points(shape.exterior, allpts), base_ft,
                              lambda e, n, planes=planes: zft(min(plane_z(pl, e, n) for pl in planes)))
            top_m = max(min(plane_z(pl, e, n) for pl in planes) for e, n in allpts)
            structures.append({"kind": "dormer, pitched", "top_m": round(top_m, 2), "fit_p90_m": round(fit[1], 3),
                               "area_ft2": round(shape.area, 1)})
        elif sm_.sum() >= 10:
            top_m = round(float(np.median(med[sm_])), 2)
            mesh.walls(shape, base_ft, zft(top_m), 0)
            mesh.cap(shape, zft(top_m), 1)
            structures.append({"kind": "dormer, flat", "top_m": top_m, "area_ft2": round(shape.area, 1)})
    if not mesh.t:
        return None
    model_grid = T.raster_top(mesh.mv, mesh.t, x0, y1, w, h, ground_ft)
    # Masts.
    mg0 = np.nan_to_num(model_grid, nan=0.0)
    big_tops = [pr["top_m"] for pr in prisms if pr["area_ft2"] >= 150.0] or [pr["top_m"] for pr in prisms]
    top_roof = max(big_tops)
    topmask = bmask & (np.abs(mg0 - top_roof) < 1.0)
    if not topmask.any():
        topmask = bmask & (mg0 >= np.percentile(mg0[bmask], 90))
    if pc is not None:
        masts = T.pc_masts(pc, ground_ft, mg0, x0, y1, cell, topmask, top_roof, surface=raw_m)
        mast_source = "point cloud"
    else:
        masts = []
        over = bmask & np.isfinite(raw_m) & (raw_m - ndimage.maximum_filter(mg0, size=7) > 4.0)
        mlab, mn = ndimage.label(over)
        for i in range(1, mn + 1):
            cells = mlab == i
            area = float(cells.sum())
            if area > 600.0:
                continue
            rr, cc = np.nonzero(cells)
            masts.append({"east": x0 + cc.mean() + 0.5, "north": y1 - rr.mean() - 0.5,
                          "radius_ft": max(0.5 / FT, math.sqrt(area / math.pi)),
                          "base_m": float(np.max(mg0[cells])), "top_m": float(np.nanmax(raw_m[cells])), "area_ft2": area})
        mast_source = "surface model"
    for m in masts:
        shape = ngon(m["east"], m["north"], m["radius_ft"], 12)
        z0 = zft(m["base_m"] - 0.5)
        z1 = zft(m["top_m"])
        mesh.walls(shape, z0, z1, 2)
        mesh.cap(shape, z1, 2)
    dist = math.hypot(c.x - d1e, c.y - d1n) * FT
    name = "%s_%s" % (os.environ.get("P17_PREFIX", "P17R"), bid)
    zone = T.ZONES.get(bid) or (4 if dist > 1000 else 3)
    data = {"name": name, "kind": "building", "zone": zone, "pivot": [round(v, 2) for v in mesh.pivot],
            "vertices": mesh.v, "triangles": mesh.t, "tri_mat": mesh.m, "uv0_m": mesh.uv}
    with open(os.path.join(out, name + ".json"), "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    grid_tops = sorted(set([pr["top_m"] for pr in prisms]))
    np.savez_compressed(os.path.join(out, name + "_grid.npz"), z=model_grid.astype(np.float32), x0=x0, y1=y1, cell=cell,
                        ground_ft=ground_ft, tops=np.array(grid_tops))
    kinds = []
    if any(pr["level"] != "pitched" for pr in prisms):
        nlev = len(set(pr["top_m"] for pr in prisms if pr["level"] != "pitched"))
        kinds.append("flat" if nlev == 1 else "stepped (%d levels)" % nlev)
    if any(pr.get("parapet_m") for pr in prisms):
        kinds.append("parapet")
    kinds += sorted(set(pt["kind"] for pt in parts_rec))
    if structures:
        kinds.append("%d rooftop structures" % len(structures))
    if masts:
        kinds.append("%d masts" % len(masts))
    top_all = max([max(grid_tops)] + [m["top_m"] for m in masts] + [s_["top_m"] for s_ in structures])
    rec = {"id": bid, "name": name, "distance_m": round(dist, 1), "ground_ft": round(ground_ft, 4),
           "form": "; ".join(kinds), "main_direction_deg": round(math.degrees(theta), 2),
           "terraces": len(prisms), "roof_top_m": round(top_roof, 2), "mast_count": len(masts),
           "top_incl_masts_m": round(top_all, 2), "curvature_drop_m": round(drop(c.x, c.y), 3),
           "placed_top_m": round(top_all - drop(c.x, c.y), 2), "triangles": len(mesh.t),
           "mast_source": mast_source, "height_source": p["height_source"], "returns": pc is not None,
           "tree_cells_replaced": p["veg_cells"], "plan_area_ft2": round(float(bmask.sum()), 0),
           "masts": masts, "prisms": prisms, "wall_shifts_m": wall_shifts, "pitched": parts_rec, "structures": structures}
    return rec


def main(argv):
    base, out = argv[1], argv[2]
    os.makedirs(out, exist_ok=True)
    frame = g.LevelFrame.load(T.FRAME)
    with open(os.path.join(base, "county", "county_footprints_2022_viewbox.json")) as handle:
        county = {str(f["attributes"]["OBJECTID"]): f for f in json.load(handle)["features"]}
    rows = {r["bldg_id"]: r for r in csv.DictReader(open(os.path.join(base, os.environ.get("P17_TARGETS", "targets.csv")), encoding="utf-8"))}
    if os.environ.get("P17_ZONES"):
        T.ZONES.update(json.load(open(os.path.join(base, os.environ["P17_ZONES"]))))
    dtm6 = T.load(os.path.join(base, "rasters", "view6ft_dtm.npz"))
    ids = argv[3:] or list(rows.keys())
    with open(os.path.join(out, "towers_record.jsonl"), "a", encoding="utf-8", buffering=1) as rec_file:
        for bid in ids:
            if not os.path.exists(os.path.join(base, "rasters", "bldg1ft", "%s_dsm.npz" % bid)):
                print("no 1 ft surface yet", bid)
                continue
            try:
                rec = build(bid, base, frame, county, dtm6, out)
            except Exception as exc:  # one failed building must not stop a batch; it is listed and rerun
                print("FAILED", bid, repr(exc))
                continue
            if rec is None:
                print("nothing built", bid)
                continue
            rec_file.write(json.dumps(rec) + "\n")
            print(bid, rec["form"], "roof %.2f m" % rec["roof_top_m"], "top %.2f m" % rec["top_incl_masts_m"],
                  "tris", rec["triangles"], [(pt["kind"], pt["fit_p90_m"]) for pt in rec["pitched"]])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
