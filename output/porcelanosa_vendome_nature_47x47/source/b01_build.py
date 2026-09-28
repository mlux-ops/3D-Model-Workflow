"""Build the Porcelanosa Vendome Nature 120x120 (47x47, code 100348304) colour (8-bit sRGB) and bump (16-bit grey)
maps, three sets that share one drawn module:

  designed  the manufacturer's two looping strips, stack bond, 4 x 2 tiles:
              row 0 = strip A  1 - 6 - 7 - 8   (8 -> 1 continues across the horizontal wrap)
              row 1 = strip B  2 - 3 - 4 - 5   (5 -> 2 continues across the horizontal wrap)
            all pieces r0 (as supplied); rows repeat A/B/A/B vertically; horizontal joints have no designed
            vein continuity (a01_edges.py: best physically possible vertical score 0.24, random p99 0.17).
  free_mix  4 x 4 tiles: each of the 8 pieces twice, in two different 90-degree rotations; the two copies of a
            piece never touch (8-neighbourhood, wrapped). Rotations only: a printed tile cannot be mirrored.
  pieces    8 one-module maps, piece N centred with a half joint on every edge (Piece_N_Color.png / _Bump16.png)

Facts (README.md, SOURCE_SELECTION.md): actual tile 1200 x 1200 mm (47.244 in, Porcelanosa FTEC sheet), 6 mm,
Nature = unglazed matte, "Relief: NO", rectified, V3. Joint: FTEC "minimum joint of 1,5 mm"; 1/16 in (1.5875 mm)
used. Drawn tile 47.1875 in (-1.44 mm, -0.12 %) so the module is exactly 47.25 in and every Sample Size is a
quarter-inch multiple. 32 px/in: module 1512 px, face 1510 px, joint 2 px (1 px half joint on every map edge).
Colour: 100 % supplied pixels, Adobe RGB (1998) decoded to linear sRGB in float64 (colour_io.py), resampled
1417 -> 1510 px (x1.0656, cubic) so the full photo fills the drawn face, rotated by exact 90-degree array
rotation only. No de-lighting: a02_lighting_joints.py found no common gradient/vignette above the content noise
and matching edge tone across every designed joint (see SOURCE_SELECTION.md).
Height (mm above the grout floor): face FACE_MM, quarter-round eased edge EDGE_MM, photo-derived micro-relief
(luminance DoG of the piece's own pixels, normalised by one global sd, tanh-bounded) that rotates with the piece.

Usage:  python b01_build.py                    -> all sets: Color.png, Bump16.png, report.json per set
        python b01_build.py <suffix> R,G,B     -> colour only, Color_<suffix>.png (and Piece_N_Color_<suffix>.png),
                                                  same plan; raises if any recomputed bump differs from the delivered
Every write goes through guard.out_path."""
import itertools
import json
import sys
import time

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates

from colour_io import load_face_lin, lum
from common import MM, lin_to_srgb, srgb_to_lin, write_png16
from guard import out_path

Image.MAX_IMAGE_PIXELS = None
SEED = 2026092747
PPI = 32
TILE_ACTUAL_IN = 1200 / MM                     # 47.2441 in
JOINT = 1.0 / 16.0
MOD = 47.25                                    # drawn module (in), quarter-inch exact
TILE = MOD - JOINT                             # 47.1875 in drawn face
MPX = int(round(MOD * PPI))                    # 1512
JPX = int(round(JOINT * PPI))                  # 2
FPX = MPX - JPX                                # 1510
assert MPX == MOD * PPI and JPX == JOINT * PPI and JPX % 2 == 0
HJ = JPX // 2                                  # 1 px half joint on each module edge

STRIP_A = [1, 6, 7, 8]
STRIP_B = [2, 3, 4, 5]
FACE_MM = 1.50
EDGE_MM = 1.00
MICRO_SD_MM = 0.03
MICRO_MAX_MM = 0.10
FULL_MM = FACE_MM + MICRO_MAX_MM               # fixed full scale 1.60 mm
GROUT_SRGB = (200.0, 199.0, 195.0)             # light pearl grey (Butech Colorstuk Rapid "Perla" recommended by Porcelanosa)
REVIT_BUMP = 60                                # editor value; 100 <-> 2.6 mm calibration, 60 used for 1.6 mm flat porcelain
FREE_N = 4
ROTS = [0, 90, 180, 270]


def resample_face(src):
    """Full source photo (covers the actual tile face) -> drawn face FPX x FPX, pixel-centre mapping, cubic."""
    n = src.shape[0]
    f = (np.arange(FPX) + 0.5) * (n / FPX) - 0.5
    gy, gx = np.meshgrid(f, f, indexing="ij")
    out = np.empty((FPX, FPX, 3))
    for ch in range(3):
        out[..., ch] = map_coordinates(src[..., ch], [gy, gx], order=3, mode="nearest")
    return np.clip(out, 0, 1)


def edge_profile():
    """Height profile of the face (FPX x FPX) without micro-relief: FACE_MM minus the quarter-round edge drop."""
    d_px = np.minimum(np.arange(FPX), FPX - 1 - np.arange(FPX)) + 0.5
    d = np.minimum(d_px[None, :], d_px[:, None]) / PPI * MM
    q = np.clip(d / EDGE_MM, 0, 1)
    return FACE_MM - EDGE_MM * (1 - np.sqrt(1 - (1 - q) ** 2))


def rot(a, deg):
    return np.rot90(a, -deg // 90)     # clockwise, exact


def free_plan(rng):
    """16 cells, 8 pieces x 2. Hard: the two copies of a piece are not 8-neighbours on the 4 x 4 torus and use
    different rotations. Soft (minimised): same-rotation 4-neighbours, adjacent pair of the two most-veined
    pieces, designed-strip neighbour pairs reproduced in the same rotation (would rebuild a designed vein)."""
    heavy = {1, 2, 4, 8}
    designed_pairs = {(a, b) for s in (STRIP_A, STRIP_B) for a, b in zip(s, s[1:] + s[:1])}

    def nb8(i, j):
        (r1, c1), (r2, c2) = divmod(i, FREE_N), divmod(j, FREE_N)
        dr, dc = (r1 - r2) % FREE_N, (c1 - c2) % FREE_N
        return i != j and dr in (0, 1, FREE_N - 1) and dc in (0, 1, FREE_N - 1)
    best = None
    for _ in range(30000):
        p = list(rng.permutation([k for k in range(1, 9) for _ in (0, 1)]))
        pos = {k: [i for i, v in enumerate(p) if v == k] for k in range(1, 9)}
        if any(nb8(*pos[k]) for k in pos):
            continue
        r = [0] * 16
        for k in pos:
            a = int(rng.integers(0, 4))
            b = (a + int(rng.choice([1, 2, 2, 3]))) % 4
            r[pos[k][0]], r[pos[k][1]] = ROTS[a], ROTS[b]
        cost = [0, 0, 0]
        for i in range(16):
            ri, ci = divmod(i, FREE_N)
            for j in (ri * FREE_N + (ci + 1) % FREE_N, ((ri + 1) % FREE_N) * FREE_N + ci):
                cost[0] += r[i] == r[j]
                cost[1] += p[i] in heavy and p[j] in heavy
            j = ri * FREE_N + (ci + 1) % FREE_N
            cost[2] += (p[i], p[j]) in designed_pairs and r[i] == r[j] == 0
        key = (cost[2], cost[1], cost[0])
        if best is None or key < best[0]:
            best = (key, p, r)
    key, p, r = best
    cells = [[{"piece": int(p[i * FREE_N + c]), "rot_cw_deg": int(r[i * FREE_N + c])} for c in range(FREE_N)] for i in range(FREE_N)]
    return cells, {"designed_pairs_rebuilt": key[0], "heavy_heavy_adjacent": key[1], "same_rotation_adjacent": key[2]}


def module_block(face_lin, face_h, grout_lin):
    """One module: face (FPX^2) inside HJ px of grout on every side."""
    col = np.empty((MPX, MPX, 3))
    col[:] = grout_lin
    col[HJ:HJ + FPX, HJ:HJ + FPX] = face_lin
    h = np.zeros((MPX, MPX))
    h[HJ:HJ + FPX, HJ:HJ + FPX] = face_h
    return col, h


def assemble(cells, faces, heights, grout_lin):
    nr, nc = len(cells), len(cells[0])
    srgb = np.zeros((nr * MPX, nc * MPX, 3), np.uint8)
    h = np.zeros((nr * MPX, nc * MPX))
    for r, c in itertools.product(range(nr), range(nc)):
        k, deg = cells[r][c]["piece"], cells[r][c]["rot_cw_deg"]
        col, hh = module_block(rot(faces[k], deg), rot(heights[k], deg), grout_lin)
        ys, xs = slice(r * MPX, (r + 1) * MPX), slice(c * MPX, (c + 1) * MPX)
        srgb[ys, xs] = np.clip(np.round(lin_to_srgb(col)), 0, 255).astype(np.uint8)
        h[ys, xs] = hh
    return srgb, h


def to16(h):
    assert h.max() <= FULL_MM + 1e-9 and h.min() >= 0
    return np.clip(np.round(h / FULL_MM * 65535), 0, 65535).astype(np.uint16)


def save_pair(d, name, srgb, h16, suffix):
    cname = "%s/%sColor%s.png" % (d, name, "_" + suffix if suffix else "")
    Image.fromarray(srgb, "RGB").save(out_path(cname), optimize=True)
    bname = "%s/%sBump16.png" % (d, name)
    if suffix:
        delivered = np.asarray(Image.open(out_path(bname))).astype(np.uint16)
        if not np.array_equal(delivered, h16):
            raise RuntimeError("variant bump differs from delivered %s: geometry or seed changed" % bname)
    else:
        write_png16(out_path(bname), h16)
    return cname, bname


def main(grout_srgb=GROUT_SRGB, suffix=""):
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    free_cells, free_cost = free_plan(rng)
    gamut = {}
    faces, heights, bands = {}, {}, {}
    base_h = edge_profile()
    for k in range(1, 9):
        faces[k] = resample_face(load_face_lin(k, gamut))
        Lg = np.log(lum(faces[k]) + 1e-4)
        bands[k] = gaussian_filter(Lg, 0.7, mode="nearest") - gaussian_filter(Lg, 3.0, mode="nearest")
    inner = base_h >= FACE_MM - 1e-12
    sd = float(np.std(np.concatenate([bands[k][inner] for k in bands])))
    for k in bands:
        micro = MICRO_MAX_MM * np.tanh(bands[k] / sd * MICRO_SD_MM / MICRO_MAX_MM)
        heights[k] = np.clip(base_h + micro, 0, None)
    gl = srgb_to_lin(np.array(grout_srgb, float))

    sets = {"designed": [[{"piece": k, "rot_cw_deg": 0} for k in STRIP_A], [{"piece": k, "rot_cw_deg": 0} for k in STRIP_B]],
            "free_mix": free_cells}
    common = {"product": "Porcelanosa Vendome Nature 120x120 (47x47 in), code 100348304, model VENDOME NAT.PV6 120X120(A)",
              "seed": SEED, "ppi": PPI, "tile_actual_in": TILE_ACTUAL_IN, "tile_actual_mm": 1200.0,
              "tile_actual_basis": "Porcelanosa FTEC technical data sheet 100348304: length 1200 mm, width 1200 mm, 6 mm",
              "tile_drawn_in": TILE, "drawn_minus_actual_mm": (TILE - TILE_ACTUAL_IN) * MM,
              "drawn_minus_actual_pct": 100 * (TILE / TILE_ACTUAL_IN - 1),
              "joint_in": JOINT, "joint_mm": JOINT * MM, "joint_basis": "FTEC: minimum joint 1.5 mm; 1/16 in used",
              "module_in": MOD, "module_px": MPX, "face_px": FPX, "joint_px": JPX,
              "source_px": 1417, "resample_factor": FPX / 1417.0, "source_px_per_in_actual": 1417 / TILE_ACTUAL_IN,
              "first_tile_face_offset_from_origin_in": [JOINT / 2, JOINT / 2],
              "relief_mm": {"full_scale": FULL_MM, "grout_floor": 0.0, "face_design": FACE_MM, "joint_depth": FACE_MM,
                            "edge_radius": EDGE_MM, "micro_sd_design": MICRO_SD_MM, "micro_bound": MICRO_MAX_MM,
                            "micro_band_sd_log": sd, "mm_per_count": FULL_MM / 65535},
              "revit_bump_amount_editor": REVIT_BUMP, "grout_srgb": list(grout_srgb),
              "source_colour_space": "Adobe RGB (1998) -> linear sRGB (float64)", "gamut_clip_share": gamut,
              "delighting": "none (no measurable baked lighting; see _work/lighting.json)"}
    out = {}
    for name, cells in sets.items():
        srgb, h = assemble(cells, faces, heights, gl)
        h16 = to16(h)
        cname, bname = save_pair(name, "", srgb, h16, suffix)
        face_px = h > 0
        rep = dict(common, set=name, cells=cells, atlas_tiles=[len(cells[0]), len(cells)],
                   pixels=[srgb.shape[1], srgb.shape[0]], sample_size_in=[srgb.shape[1] / PPI, srgb.shape[0] / PPI],
                   face_relief_mm_min_max=[float(h[face_px].min()), float(h[face_px].max())],
                   face_mean_srgb=[float(v) for v in srgb[face_px].reshape(-1, 3).mean(0)],
                   files=[cname, bname])
        if name == "free_mix":
            rep["plan_soft_costs"] = free_cost
        if name == "designed":
            rep["layout"] = ("stack bond; row 0 strip A 1-6-7-8, row 1 strip B 2-3-4-5, all as supplied (r0); strips loop "
                             "horizontally (8->1, 5->2 across the wrap); rows repeat A/B vertically; no designed vertical continuity")
        json.dump(rep, open(out_path("%s/report%s.json" % (name, "_" + suffix if suffix else "")), "w"), indent=1)
        out[name] = {k: rep[k] for k in ("pixels", "sample_size_in", "face_relief_mm_min_max")}
        del srgb, h
    prep = dict(common, set="pieces", atlas_tiles=[1, 1], pixels=[MPX, MPX], sample_size_in=[MOD, MOD], pieces={})
    for k in range(1, 9):
        srgb, h = assemble([[{"piece": k, "rot_cw_deg": 0}]], faces, heights, gl)
        cname, bname = save_pair("pieces", "Piece_%d_" % k, srgb, to16(h), suffix)
        prep["pieces"][str(k)] = {"files": [cname, bname], "face_mean_srgb": [float(v) for v in srgb[h > 0].mean(0)]}
    json.dump(prep, open(out_path("pieces/report%s.json" % ("_" + suffix if suffix else "")), "w"), indent=1)
    out["pieces"] = {"pixels": [MPX, MPX], "sample_size_in": [MOD, MOD]}
    out["free_cells"] = free_cells
    out["free_cost"] = free_cost
    out["gamut"] = gamut
    out["seconds"] = time.time() - t0
    print(json.dumps(out, indent=None))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        rgb = tuple(float(x) for x in sys.argv[2].split(","))
        main(rgb, sys.argv[1])
    else:
        main()
