"""Phase 17, step 17.4: the ground beyond the 300 m square, from the 2022 laser-scan surfaces.

Usage:
    python -B -P phase17_terrain.py <phase17 data folder> <out folder> [step cells 4]

From the 6 ft surface and ground models over the viewshed box (9.1 by 11.0 km) and the county footprints rasterized
by the viewshed (building_ids.npz):
- surface: the ground model under buildings (the buildings are modelled apart), the surface model elsewhere, so
  street trees and park canopy stay as soft relief; the lake (cells the state left empty, and ground at or under
  581.5 ft NAVD 88 connected to them) is a flat water surface at 578.5 ft;
- a grid every <step> cells (24 ft by default), the 300 m square cut out (its ground is the Phase 4 ground), lowered
  by 10 cm so the seam never shows above the site ground, decimated with fast_simplification to 10 percent;
- a flat apron from the box edge out to 25 km at the edge's median ground height, so the world does not end in view;
- the earth-curvature drop seen from D1, as for the towers;
- material numbers: 0 land (the colour map), 1 water;
- UV channel 0: the colour map over the box (0 to 1); the apron takes the map's edge.
Writes <out>/P17G_Terrain.json (the mesh format of phase17_towers.py) and <out>/T_W1529_P17_LandCover.png, a single
4,096 by 4,096 colour map with no repeat: canopy green by canopy height, paved and bare ground grey, ground under
buildings darker, water blue-grey, each with a small seeded variation.
"""

import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wieland_geo as g  # noqa: E402

FT = 0.3048006096
FRAME = os.path.join(HERE, "..", "review", "phase2", "level_frame.json")
D1 = (-1300.0, -1560.0, 1684.0)
SITE = (1174227.19, 1910645.18)
HALF = 492.125
WATER_FT = 578.5


def srgb_to_lin(c):
    return (np.asarray(c, np.float64) / 255.0)


def main(argv):
    base, out = argv[1], argv[2]
    step = int(argv[3]) if len(argv) > 3 else 4
    os.makedirs(out, exist_ok=True)
    frame = g.LevelFrame.load(FRAME)
    dsm = np.load(os.path.join(base, "rasters", "view6ft_dsm.npz"))
    dtm = np.load(os.path.join(base, "rasters", "view6ft_dtm.npz"))
    zs, zt = dsm["z"].astype(np.float64), dtm["z"].astype(np.float64)
    x0, y1, cell = float(dtm["x0"]), float(dtm["y1"]), float(dtm["cell"])
    ids = np.load(os.path.join(base, "viewshed_county", "building_ids.npz"))["ids"]
    h = min(zs.shape[0], zt.shape[0], ids.shape[0])
    w = min(zs.shape[1], zt.shape[1], ids.shape[1])
    zs, zt, ids = zs[:h, :w], zt[:h, :w], ids[:h, :w]
    ex = x0 + (np.arange(w) + 0.5) * cell
    building = ndimage.binary_dilation(ids > 0, iterations=1)
    # The lake: cells the state left empty, and ground at or under 581.5 ft (the lake stood near 580.3 ft NAVD 88 in
    # 2022) that is connected to them; the river and harbours join through the same rule.
    low = np.isnan(zt) | (np.nan_to_num(zt, nan=0.0) <= 581.5)
    lab, _ = ndimage.label(low & ~ndimage.binary_dilation(ids > 0, iterations=1))
    lake_labels = np.unique(lab[np.isnan(zt)])
    water = np.isin(lab, lake_labels[lake_labels > 0]) | np.isnan(zt)
    water = ndimage.binary_opening(water, iterations=1) | np.isnan(zt)
    ground = np.where(np.isnan(zt), WATER_FT, zt)
    surf = np.where(building, ground, np.where(np.isnan(zs), ground, zs))
    surf = np.where(water, WATER_FT, surf)
    canopy = (~building) & (~water) & ((surf - ground) * FT > 2.5)
    # Soften the canopy so trees read as crowns, not as 6 ft columns.
    surf = np.where(canopy, ndimage.uniform_filter(surf, size=3), surf)

    # --- colour map (one unique picture over the box) ---------------------------------------------------------
    rng = np.random.default_rng(15291704)
    tex_n = 4096
    rr = (np.arange(tex_n) + 0.5) / tex_n * h
    cc = (np.arange(tex_n) + 0.5) / tex_n * w
    R, C = np.meshgrid(rr.astype(int).clip(0, h - 1), cc.astype(int).clip(0, w - 1), indexing="ij")
    can_h = ((surf - ground) * FT)[R, C]
    is_can, is_w, is_b = canopy[R, C], water[R, C], building[R, C]
    col = np.empty((tex_n, tex_n, 3))
    paved = np.array([128, 127, 122], float)
    under = np.array([96, 95, 92], float)
    wat = np.array([46, 66, 80], float)
    can_lo, can_hi = np.array([70, 92, 52], float), np.array([40, 62, 34], float)
    t = np.clip((can_h - 2.5) / 15.0, 0, 1)[..., None]
    col[:] = paved
    col[is_b] = under
    col = np.where(is_can[..., None], can_lo * (1 - t) + can_hi * t, col)
    col[is_w] = wat
    noise = ndimage.gaussian_filter(rng.standard_normal((tex_n, tex_n)), 2.0)
    noise = noise / (noise.std() + 1e-9)
    col *= (1.0 + 0.06 * noise)[..., None]
    col += rng.normal(0, 2.0, col.shape)
    Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).save(os.path.join(out, "T_W1529_P17_LandCover.png"))

    # --- mesh ------------------------------------------------------------------------------------------------
    rows = np.arange(0, h, step)
    cols = np.arange(0, w, step)
    gr, gc = np.meshgrid(rows, cols, indexing="ij")
    E = x0 + (gc + 0.5) * cell
    N = y1 - (gr + 0.5) * cell
    Z = surf[gr, gc] - 0.1 / FT
    W = water[gr, gc]
    inside = (np.abs(E - SITE[0]) < HALF) & (np.abs(N - SITE[1]) < HALF)
    nr, nc = gr.shape
    idx = np.arange(nr * nc).reshape(nr, nc)
    a, b = idx[:-1, :-1], idx[:-1, 1:]
    c, d = idx[1:, 1:], idx[1:, :-1]
    keep = ~(inside[:-1, :-1] & inside[:-1, 1:] & inside[1:, 1:] & inside[1:, :-1])
    # a north-west, b north-east, c south-east, d south-west: (a, d, c) and (a, c, b) counter-clockwise from above.
    F = np.vstack([np.column_stack([a[keep], d[keep], c[keep]]), np.column_stack([a[keep], c[keep], b[keep]])])
    P = np.column_stack([E.ravel(), N.ravel(), Z.ravel()])
    import fast_simplification
    centre = P.mean(axis=0)
    pp, ff = fast_simplification.simplify((P - centre).astype(np.float32), F.astype(np.int32), target_reduction=0.9, agg=5)
    pp = pp.astype(np.float64) + centre
    # Water by the triangle's centre.
    cen = pp[ff].mean(axis=1)
    cr = np.clip(((y1 - cen[:, 1]) / cell).astype(int), 0, h - 1)
    ccl = np.clip(((cen[:, 0] - x0) / cell).astype(int), 0, w - 1)
    tri_mat = water[cr, ccl].astype(int)
    # Apron: a ring from the box edge out to 25 km, at the edge's median ground height.
    edge_z = float(np.median(np.concatenate([surf[0], surf[-1], surf[:, 0], surf[:, -1]])))
    bx0, bx1, by0, by1 = x0, x0 + w * cell, y1 - h * cell, y1
    far = 25000.0 / FT
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    inner = [(bx0, by1), (bx0, by0), (bx1, by0), (bx1, by1)]
    outer = [(cx - far, cy + far), (cx - far, cy - far), (cx + far, cy - far), (cx + far, cy + far)]
    base_i = len(pp)
    apron_pts = [(e, n, edge_z - 0.3 / FT) for e, n in inner + outer]
    pp = np.vstack([pp, np.array(apron_pts)])
    apron_f = []
    for k in range(4):
        i0, i1 = base_i + k, base_i + (k + 1) % 4
        o0, o1 = base_i + 4 + k, base_i + 4 + (k + 1) % 4
        # inner ring runs counter-clockwise seen from above (NW, SW, SE, NE); the band outside it faces up.
        apron_f += [(i0, o0, o1), (i0, o1, i1)]
    ff = np.vstack([ff, np.array(apron_f)])
    tri_mat = np.concatenate([tri_mat, np.zeros(len(apron_f), int)])
    # Curvature drop from D1.
    d1e, d1n = frame.map_from_level(D1[0], D1[1])
    pivot = frame.level_from_map(SITE[0], SITE[1], float(np.median(ground)))
    verts, uvs = [], []
    for e, n, z in pp:
        dist = math.hypot(e - d1e, n - d1n) * FT
        drop = dist * dist / (2 * 6371000.0) * (1 - 0.13)
        x, y, zz = frame.level_from_map(e, n, z - drop / FT)
        verts.append((round(x - pivot[0], 1), round(y - pivot[1], 1), round(zz - pivot[2], 1)))
        uvs.append((round(min(max((e - bx0) / (bx1 - bx0), 0.0), 1.0), 6), round(min(max((by1 - n) / (by1 - by0), 0.0), 1.0), 6)))
    tris = [(int(t[0]), int(t[2]), int(t[1])) for t in ff]  # mirrored level frame: flip winding
    data = {"name": "P17G_Terrain", "kind": "ground", "zone": 4, "pivot": [round(v, 2) for v in pivot],
            "vertices": verts, "triangles": tris, "tri_mat": [int(m) for m in tri_mat], "uv0_m": uvs}
    with open(os.path.join(out, "P17G_Terrain.json"), "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    print("vertices", len(verts), "triangles", len(tris), "water triangles", int(tri_mat.sum()), "edge z ft", round(edge_z, 1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
