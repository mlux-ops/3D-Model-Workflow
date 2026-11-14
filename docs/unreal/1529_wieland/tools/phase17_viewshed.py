"""Phase 17, step 17.1: what each viewpoint really sees, over the 2022 laser-scan surface model.

Usage:
    python -B -P phase17_viewshed.py <rasters folder> <city footprints geojson> <out folder>

Method. Radial line of sight on the coarse surface model (`view6ft_dsm.npz`, 6 ft cells, nearest-neighbour from
the 1 ft source). From each viewpoint, rays are cast every 0.025 degree of azimuth (D1) or 0.1 degree (the others),
sampled every 3 ft out to the edge of the box. A cell is visible when the elevation angle to the top of the cell is
at least the largest angle met so far along the ray. Heights are lowered for earth curvature with refraction,
d^2 / (2R) * (1 - 0.13). The lot itself (the two houses of 2022, since demolished) is set to the ground model so
that the old houses do not block the new building's own views. Trees are in the surface model as they stood in
the leaf-off spring of 2022; a second run with trees removed (surface replaced by ground wherever no city building
footprint lies) gives the upper bound "visible through bare branches".

Outputs, per viewpoint: a visibility mask (npz), a PNG map, and a CSV row per city building footprint with any
visible cell: building id, name, address, stories, year built, distance, azimuth, roof height above ground from the
surface model, visible cells (with and without trees), and the highest visible elevation angle.
"""

import csv
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wieland_geo as g  # noqa: E402

FT = 0.3048006096
R_EARTH_FT = 6371000.0 / FT
K_REFRACTION = 0.13
FRAME = os.path.join(HERE, "..", "review", "phase2", "level_frame.json")
LOT_X = (-1508.8, 0.0)       # level cm, lot is 15.088 m north-south (x from -1508.8 to 0)
LOT_Y = (-3115.1, 0.0)       # 31.151 m deep, east is -Y

# Viewpoints in level cm (x, y, z): D-table of REFERENCE_VIEWS.md; D1S is D1 mirrored to the south penthouse deck
# about the lot's centre line x = -754.4. Stations from review/phase2/stations.csv, eye 160 cm over the ground.
VIEWPOINTS = {
    "D1": (-1300.0, -1560.0, 1684.0, 0.025),
    "D1S": (-208.8, -1560.0, 1684.0, 0.1),
    "D2": (-960.0, -840.0, 1339.0, 0.1),
    "D5": (-1190.0, -2262.0, 363.0, 0.1),
}


def stations():
    path = os.path.join(HERE, "..", "review", "phase2", "stations.csv")
    out = {}
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            name = row["station"].split()[0]
            if name in ("S7", "S8") or not row["new_level_x_cm"]:
                continue
            out[name] = (float(row["new_level_x_cm"]), float(row["new_level_y_cm"]), None, 0.1)
    return out


def load(path):
    d = np.load(path)
    return d["z"].astype(np.float32), float(d["x0"]), float(d["y1"]), float(d["cell"])


def viewshed(z, x0, y1, cell, east, north, eye_ft, step_deg, max_ft):
    h, w = z.shape
    az = np.deg2rad(np.arange(0.0, 360.0, step_deg))
    se, ce = np.sin(az), np.cos(az)  # grid azimuth: east = sin, north = cos
    vis = np.zeros((h, w), np.uint8)
    best = np.full(az.shape, -np.inf)
    top_angle = np.full((h, w), -np.inf, np.float32)
    ds = np.arange(cell, max_ft, cell / 2.0)
    for d in ds:
        e = east + se * d
        n = north + ce * d
        c = ((e - x0) / cell).astype(np.int64)
        r = ((y1 - n) / cell).astype(np.int64)
        ok = (c >= 0) & (c < w) & (r >= 0) & (r < h)
        if not ok.any():
            break
        zz = np.full(az.shape, np.nan)
        zz[ok] = z[r[ok], c[ok]]
        drop = d * d / (2.0 * R_EARTH_FT) * (1.0 - K_REFRACTION)
        ang = np.arctan2(zz - drop - eye_ft, d)
        good = ok & np.isfinite(ang)
        seen = good & (ang >= best)
        vis[r[seen], c[seen]] = 1
        np.maximum.at(top_angle, (r[seen], c[seen]), ang[seen].astype(np.float32))
        best = np.where(good, np.maximum(best, ang), best)
    return vis, top_angle


def footprints(path, frame_box):
    with open(path) as handle:
        data = json.load(handle)
    out = []
    for f in data["features"]:
        p = f.get("properties", {})
        geom = f.get("geometry")
        if not geom:
            continue
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        rings = []
        for poly in polys:
            ring = [g.state_plane_from_lat_lon(lat, lon) for lon, lat in poly[0]]
            rings.append(ring)
        out.append((p, rings))
    return out


def main(argv):
    rasters, fp_path, out = argv[1], argv[2], argv[3]
    os.makedirs(out, exist_ok=True)
    dsm, x0, y1, cell = load(os.path.join(rasters, "view6ft_dsm.npz"))
    dtm, _, _, _ = load(os.path.join(rasters, "view6ft_dtm.npz"))
    h, w = dsm.shape
    frame = g.LevelFrame.load(FRAME)

    # Lot set to ground.
    corners = [frame.map_from_level(x, y) for x in LOT_X for y in LOT_Y]
    es = [c[0] for c in corners]
    ns = [c[1] for c in corners]
    c0, c1 = int((min(es) - x0) / cell), int((max(es) - x0) / cell) + 1
    r0, r1 = int((y1 - max(ns)) / cell), int((y1 - min(ns)) / cell) + 1
    dsm[r0:r1, c0:c1] = dtm[r0:r1, c0:c1]

    # Building ids raster from the city footprints.
    fps = footprints(fp_path, None)
    ids = Image.new("I", (w, h), 0)
    draw = ImageDraw.Draw(ids)
    for k, (p, rings) in enumerate(fps, start=1):
        for ring in rings:
            draw.polygon([((e - x0) / cell, (y1 - n) / cell) for e, n in ring], fill=k)
    ids = np.asarray(ids, dtype=np.int32)
    bare = np.where(ids > 0, dsm, dtm)  # trees removed
    np.savez_compressed(os.path.join(out, "building_ids.npz"), ids=ids)

    views = dict(VIEWPOINTS)
    views.update(stations())
    summary = {}
    for name, (x, y, zc, step) in views.items():
        east, north = frame.map_from_level(x, y)[:2]
        col, row = int((east - x0) / cell), int((y1 - north) / cell)
        ground = float(dtm[row, col])
        eye_ft = frame.origin_height_ft + zc / 30.48006 if zc is not None else ground + 160.0 / 30.48006
        max_ft = 40000.0 if name.startswith("D1") else 12000.0
        vis, top = viewshed(dsm, x0, y1, cell, east, north, eye_ft, step, max_ft)
        vis_bare, _ = viewshed(bare, x0, y1, cell, east, north, eye_ft, step, max_ft)
        np.savez_compressed(os.path.join(out, "vis_%s.npz" % name), vis=vis, vis_bare=vis_bare, top=top)
        # Per building.
        rows = []
        flat = ids.ravel()
        for label, mask in (("trees", vis), ("bare", vis_bare)):
            counts = np.bincount(flat[mask.ravel() > 0], minlength=len(fps) + 1)
            summary.setdefault(name, {})[label] = counts
        counts, counts_bare = summary[name]["trees"], summary[name]["bare"]
        maxang = np.full(len(fps) + 1, -np.inf)
        sel = vis.ravel() > 0
        np.maximum.at(maxang, flat[sel], top.ravel()[sel])
        height = dsm - dtm
        hmax = np.zeros(len(fps) + 1)
        np.maximum.at(hmax, flat, np.nan_to_num(height.ravel(), nan=0.0))
        for k in np.nonzero((counts_bare > 0) | (counts > 0))[0]:
            if k == 0:
                continue
            p, rings = fps[k - 1]
            ce = sum(e for e, _ in rings[0]) / len(rings[0])
            cn = sum(n for _, n in rings[0]) / len(rings[0])
            dist = math.hypot(ce - east, cn - north) * FT
            azg = math.degrees(math.atan2(ce - east, cn - north)) % 360.0
            rows.append({
                "bldg_id": p.get("bldg_id"), "name": (p.get("bldg_name1") or "").strip(),
                "address": " ".join(str(p.get(k2) or "") for k2 in ("f_add1", "pre_dir1", "st_name1", "st_type1")).strip(),
                "stories": p.get("stories") or p.get("no_stories"), "year_built": p.get("year_built"),
                "distance_m": round(dist, 1), "grid_azimuth_deg": round(azg, 2),
                "roof_height_m_dsm6ft": round(hmax[k] * FT, 1),
                "visible_cells": int(counts[k]), "visible_cells_bare_trees": int(counts_bare[k]),
                "max_elev_angle_deg": round(math.degrees(maxang[k]), 3) if np.isfinite(maxang[k]) else "",
            })
        rows.sort(key=lambda r: -r["visible_cells_bare_trees"])
        with open(os.path.join(out, "visible_buildings_%s.csv" % name), "w", newline="", encoding="utf-8") as handle:
            if rows:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
        # Map picture: grey hillshade-ish height, visible cells red (with trees) and orange (bare only).
        hh = np.nan_to_num(np.clip((dsm - dtm) / 100.0, 0, 1))
        img = np.stack([hh * 180 + 40] * 3, axis=-1).astype(np.uint8)
        img[np.isnan(dsm)] = (40, 60, 110)
        img[(vis_bare > 0) & (vis == 0)] = (255, 170, 0)
        img[vis > 0] = (230, 20, 20)
        picture = Image.fromarray(img)
        d2 = ImageDraw.Draw(picture)
        d2.ellipse([col - 8, row - 8, col + 8, row + 8], outline=(0, 255, 0), width=3)
        picture.thumbnail((2500, 3000))
        picture.save(os.path.join(out, "viewshed_%s.png" % name))
        print(name, "eye %.1f ft" % eye_ft, "visible cells", int(vis.sum()), "bare", int(vis_bare.sum()),
              "buildings", len(rows), "with >=4 cells", sum(1 for r in rows if r["visible_cells"] >= 4))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
