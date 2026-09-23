"""Build the seamless, non-repeating colour and bump maps for the 10 in hexagon tile.

Geometry
--------
Flat-top regular hexagons, across-flats 10.000 in (see README for the nominal-size
assumption), 1/8 in joint. The hexagon lattice is the Voronoi diagram of a triangular
lattice of centres, so the nearest centre gives the cell and the perpendicular-bisector
distance gives an exact, analytic distance to the joint centreline. Centres are
enumerated on a torus, which makes the image wrap seamlessly by construction rather
than by a fade at the border.

The atlas is 8 columns x 7 rows = 56 hexagons. Every hexagon gets an independent face
type, comb direction, mottle crop offset, mottle rotation and tone jitter, keyed off a
hash of its wrapped (column, row), so the variation wraps too.

Faces
-----
plain    the matte field only
stipple  coarse pitted relief
comb     parallel striations, 3.61 mm pitch (measured off the reference), running
         perpendicular to one of the three edge pairs

Relief budget, in a 2.00 mm total height range:
  grout floor       0.00 mm
  tile base plane   1.50 mm      -> 1.50 mm grout step
  comb valley      -0.35 mm      comb crest +0.10 mm  (0.45 mm peak-to-peak)
  stipple pit      -0.50 mm      stipple crest +0.05 mm
  deepest pattern point sits 1.00 mm above the grout floor (clearance, > 0)

Outputs
-------
textures/Hex10_Dimensional_Color.png    8-bit sRGB
textures/Hex10_Dimensional_Bump16.png   16-bit greyscale
textures/build_report.json
"""

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def out_path(*parts):
    p = os.path.abspath(os.path.join(RUN_DIR, *parts))
    if os.path.commonpath([p, RUN_DIR]) != RUN_DIR:
        raise RuntimeError("refusing to write outside the run dir: %s" % p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


# --- product -----------------------------------------------------------------
FLATS_IN = 10.0                       # hexagon across-flats, nominal
JOINT_IN = 0.125                      # 1/8 in
COLS, ROWS = 8, 7                     # hexagons in the atlas
PPI = 64.0                            # pixels per inch

MODULE_F = FLATS_IN + JOINT_IN                        # 10.125 in, flats direction
MODULE_C = MODULE_F * 2.0 / np.sqrt(3.0)              # across-corners of the module
COL_PITCH = MODULE_C * 0.75                           # 8.76848 in
ROW_PITCH = MODULE_F                                  # 10.125 in
ATLAS_W_IN = COLS * COL_PITCH                         # 70.1478 in
ATLAS_H_IN = ROWS * ROW_PITCH                         # 70.875 in
W = int(round(ATLAS_W_IN * PPI))
H = int(round(ATLAS_H_IN * PPI))

# --- relief, in mm above the grout floor -------------------------------------
TOTAL_MM = 2.00
BASE_MM = 1.50                        # tile face plane
BEVEL_MM = 2.0                        # chamfer width at the tile edge, measured in
CHAMFER_DROP_MM = 0.30                # how far the chamfer falls before the joint
COMB_PITCH_MM = 3.61                  # measured, source/reference_stats.json
COMB_CREST_MM = 0.10
COMB_VALLEY_MM = -0.35
STIPPLE_FINE_MM = 2.0                 # pit wavelength, fine component
STIPPLE_COARSE_MM = 5.0               # pit wavelength, coarse component
STIPPLE_CREST_MM = 0.05
STIPPLE_PIT_MM = -0.50
GRAIN_MM = 0.030                      # matte micro-relief on every face

# --- colour ------------------------------------------------------------------
# Base albedo sits between the two references: the installed photo's well-lit plain
# faces read (215..224, 201..209, 178..187) and the flat layout art reads (244,231,207).
# The user identified the photo as the accurate tone, so the base leans to it.
BASE_RGB = np.array([220.0, 206.0, 184.0])
GROUT_RGB = np.array([188.0, 178.0, 164.0])
MOTTLE_GAIN = 1.6                     # x the mottle extracted from the flat reference
GRAIN_GAIN = 0.8                      # x the fine grain extracted from the photo
TONE_JITTER = 0.014                   # per-hexagon luminance spread; both
                                      # references show a fairly uniform shade, so this
                                      # stays subtle and the non-repetition is carried
                                      # by the face mix and the mottle offsets instead
WARM_JITTER = 0.008                   # per-hexagon warm/cool spread
CAVITY_GAIN = 0.18                    # how much local relief darkens the colour
# Whole-face cavity occlusion. A pitted or combed face traps light across its entire
# area, so it reads a little deeper in tone than a plain face even from across a room
# - which is how the textured faces stay legible in the references at room distance.
# Isotropic pits occlude more than open parallel channels.
FACE_AO = {"plain": 1.000, "comb": 0.970, "stipple": 0.952}

MOTTLE_TILE_IN = 200.0 / 43.65        # 4.58 in: the flat reference's own scale
GRAIN_TILE_IN = 2.12                  # estimated from the photo, see README

# --- face mix, read off source/_REVIEW_reference_mask.png --------------------
MIX = {"plain": 0.40, "stipple": 0.30, "comb": 0.30}
# Direction the comb lines RUN, measured from the image x-axis. The reference
# shows vertical lines on a flat-top hexagon, i.e. perpendicular to the top edge, and
# the same tile rotated gives the other two.
COMB_ANGLES_DEG = (90.0, 30.0, 150.0)

STRIP = 512                           # rows processed at a time
SEED = 20260919


def h32(*vals):
    """Stable hash -> float in [0,1). Keyed on wrapped cell indices, so it tiles."""
    s = "|".join(str(v) for v in vals) + "|%d" % SEED
    d = hashlib.blake2b(s.encode("ascii"), digest_size=8).digest()
    return int.from_bytes(d, "big") / float(1 << 64)


def neighbours(i, j):
    """The six lattice neighbours of a flat-top cell, wrapped onto the atlas torus."""
    if i % 2 == 0:
        offs = [(0, -1), (0, 1), (-1, -1), (-1, 0), (1, -1), (1, 0)]
    else:
        offs = [(0, -1), (0, 1), (-1, 0), (-1, 1), (1, 0), (1, 1)]
    return [((i + di) % COLS, (j + dj) % ROWS) for di, dj in offs]


def assign_faces():
    """Face type and comb angle per cell, avoiding like-next-to-like.

    COLS is even, so wrapping in the column direction preserves the parity that the
    row offset depends on and the assignment stays valid across the seam.
    """
    kinds = list(MIX)
    rng = np.random.default_rng(SEED)

    # Exact counts, so the repair pass below cannot drift the mix: it only swaps two
    # cells or re-rolls a comb angle, never converts one face type into another.
    n = COLS * ROWS
    want = {k: int(round(MIX[k] * n)) for k in kinds}
    want[kinds[0]] += n - sum(want.values())
    bagof = [k for k in kinds for _ in range(want[k])]
    rng.shuffle(bagof)

    face = {}
    for idx, (i, j) in enumerate((i, j) for i in range(COLS) for j in range(ROWS)):
        k = bagof[idx]
        a = COMB_ANGLES_DEG[int(rng.integers(0, 3))] if k == "comb" else None
        face[(i, j)] = [k, a]

    def cost(i, j):
        """Only genuinely repetitive adjacencies are penalised.

        Six neighbours and three face types means same-kind contact is unavoidable, and
        adjacent plain faces are what the product actually looks like. What reads as a
        repeat is two combed faces sharing a joint with their lines running the same
        way, so that carries the weight; touching stipple faces are mildly discouraged
        because their pit fields would merge across the joint.
        """
        k, a = face[(i, j)]
        c = 0
        for n in neighbours(i, j):
            nk, na = face[n]
            if k == "comb" and nk == "comb" and na == a:
                c += 4
            elif k == "stipple" and nk == "stipple":
                c += 1
        return c

    def total():
        return sum(cost(*c) for c in face)

    cells = list(face)
    for _ in range(600):
        t = total()
        if t == 0:
            break
        worst = max(cells, key=lambda c: cost(*c))
        # cheapest repair first: a combed face can just turn its lines
        if face[worst][0] == "comb":
            for a in COMB_ANGLES_DEG:
                old = face[worst][1]
                face[worst][1] = a
                if total() < t:
                    break
                face[worst][1] = old
            if total() < t:
                continue
        # otherwise swap it with another cell, which leaves the mix untouched
        best = None
        for other in cells:
            if other == worst or face[other][0] == face[worst][0]:
                continue
            face[worst], face[other] = face[other], face[worst]
            v = total()
            face[worst], face[other] = face[other], face[worst]
            if best is None or v < best[0]:
                best = (v, other)
        if best is None or best[0] >= t:
            break
        o = best[1]
        face[worst], face[o] = face[o], face[worst]

    bad = total()
    counts = {k: sum(1 for v in face.values() if v[0] == k) for k in kinds}
    return face, counts, bad


def load_tile(name, tile_in):
    """Load a zero-mean ratio field saved by extract_source.py, rescaled to PPI."""
    a = np.asarray(Image.open(os.path.join(RUN_DIR, "source", name)), dtype=np.float64)
    a = (a / 65535.0 - 0.5) / 4.0
    n = int(round(tile_in * PPI))
    a = np.asarray(Image.fromarray(a.astype(np.float32), mode="F").resize(
        (n, n), Image.BICUBIC), dtype=np.float64)
    return a - a.mean()


def stipple_tile(size_px, rng):
    """Periodic band-limited noise for the pitted face, shaped to favour pits.

    Banded on wavelength in millimetres, not on raw pixel frequency: the photo's
    pitting is a fine sand at roughly 2 mm with a coarser mottle behind it near 5 mm.
    """
    n = np.fft.rfft2(rng.standard_normal((size_px, size_px)))
    fy = np.fft.fftfreq(size_px)[:, None]
    fx = np.fft.rfftfreq(size_px)[None, :]
    f_px = np.sqrt(fy ** 2 + fx ** 2)                      # cycles per pixel
    lam_mm = 25.4 / np.maximum(f_px * PPI, 1e-9)           # wavelength in mm
    band = np.exp(-((np.log(lam_mm) - np.log(STIPPLE_FINE_MM)) ** 2) / (2 * 0.45 ** 2))
    band += 0.55 * np.exp(-((np.log(lam_mm) - np.log(STIPPLE_COARSE_MM)) ** 2) / (2 * 0.40 ** 2))
    band[0, 0] = 0.0
    a = np.fft.irfft2(n * band, s=(size_px, size_px))
    a = (a - a.mean()) / a.std()
    # skew downward: the face is pitted, not embossed
    a = np.where(a < 0, a * 1.35, a * 0.55)
    # normalise on a high percentile, not the maximum: dividing by a single extreme
    # outlier flattens the whole field and the pitting stops reading
    return np.clip(a / np.percentile(np.abs(a), 97.0), -1.15, 1.15)


def sample(tile, u, v):
    """Bilinear sample of a square tile at pixel coordinates, wrapping."""
    n = tile.shape[0]
    u = np.mod(u, n)
    v = np.mod(v, n)
    u0 = np.floor(u).astype(np.int64)
    v0 = np.floor(v).astype(np.int64)
    fu = u - u0
    fv = v - v0
    u1 = (u0 + 1) % n
    v1 = (v0 + 1) % n
    return (tile[v0, u0] * (1 - fu) * (1 - fv) + tile[v0, u1] * fu * (1 - fv) +
            tile[v1, u0] * (1 - fu) * fv + tile[v1, u1] * fu * fv)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-12), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def main():
    face, counts, bad = assign_faces()
    print("atlas %d x %d hexagons, %d px x %d px, %.3f x %.3f in"
          % (COLS, ROWS, W, H, ATLAS_W_IN, ATLAS_H_IN))
    print("face mix:", counts, " adjacency violations:", bad)

    rng = np.random.default_rng(SEED + 1)
    mottle = load_tile("mottle_tile.png", MOTTLE_TILE_IN)
    grain = load_tile("grain_tile.png", GRAIN_TILE_IN)
    stip = stipple_tile(int(round(6.0 * PPI)), rng)      # 6 in periodic noise field
    print("mottle tile %d px, grain tile %d px, stipple field %d px"
          % (mottle.shape[0], grain.shape[0], stip.shape[0]))

    # per-cell parameters
    cell = {}
    for i in range(COLS):
        for j in range(ROWS):
            k, a = face[(i, j)]
            cell[(i, j)] = {
                "kind": k,
                "angle": a,
                "mrot": h32("mrot", i, j) * 2 * np.pi,
                "mox": h32("mox", i, j) * mottle.shape[0],
                "moy": h32("moy", i, j) * mottle.shape[0],
                "gox": h32("gox", i, j) * grain.shape[0],
                "goy": h32("goy", i, j) * grain.shape[0],
                "sox": h32("sox", i, j) * stip.shape[0],
                "soy": h32("soy", i, j) * stip.shape[0],
                "srot": int(h32("srot", i, j) * 6) * np.pi / 3.0,
                "tone": (h32("tone", i, j) * 2 - 1) * TONE_JITTER,
                "warm": (h32("warm", i, j) * 2 - 1) * WARM_JITTER,
                "cphase": h32("cphase", i, j),
                "ao": FACE_AO[k],
            }

    # exact pixel pitches, so the lattice is periodic in the image to the pixel
    cpx = W / float(COLS)
    rpx = H / float(ROWS)
    mm_per_px_x = ATLAS_W_IN * 25.4 / W
    half_joint_mm = JOINT_IN * 25.4 / 2.0

    color = np.zeros((H, W, 3), dtype=np.uint8)
    bump = np.zeros((H, W), dtype=np.uint16)
    stats = {"min_face_mm": 9e9, "min_pattern_mm": 9e9}

    for y0 in range(0, H, STRIP):
        y1 = min(y0 + STRIP, H)
        ys, xs = np.mgrid[y0:y1, 0:W].astype(np.float64)
        ys += 0.5
        xs += 0.5

        # nearest lattice centre on the torus -> cell id, and the exact distance to
        # the Voronoi boundary from the two nearest centres
        ci = np.round(xs / cpx).astype(np.int64)
        d1 = np.full(xs.shape, np.inf)
        d2 = np.full(xs.shape, np.inf)
        bi = np.zeros(xs.shape, dtype=np.int64)
        bj = np.zeros(xs.shape, dtype=np.int64)
        bcx = np.zeros(xs.shape)
        bcy = np.zeros(xs.shape)
        for di in (-1, 0, 1):
            i = ci + di
            cx = i * cpx
            yoff = np.where(i % 2 != 0, rpx * 0.5, 0.0)
            j = np.round((ys - yoff) / rpx).astype(np.int64)
            for dj in (-1, 0, 1):
                jj = j + dj
                cy = yoff + jj * rpx
                # wrap the offset to the nearest image copy
                dx = xs - cx
                dy = ys - cy
                d = np.sqrt(dx * dx + dy * dy)
                closer = d < d1
                d2 = np.minimum(d2, np.where(closer, d1, d))
                bi = np.where(closer, i, bi)
                bj = np.where(closer, jj, bj)
                bcx = np.where(closer, cx, bcx)
                bcy = np.where(closer, cy, bcy)
                d1 = np.where(closer, d, d1)
        edge_px = (d2 - d1) * 0.5
        edge_mm = edge_px * mm_per_px_x
        wi = np.mod(bi, COLS)
        wj = np.mod(bj, ROWS)

        # local coordinates inside the hexagon, in mm
        lx = (xs - bcx) * mm_per_px_x
        ly = (ys - bcy) * mm_per_px_x

        height = np.zeros(xs.shape)          # mm above the grout floor
        pattern = np.zeros(xs.shape)         # mm relative to the tile base plane
        mott = np.zeros(xs.shape)
        grn = np.zeros(xs.shape)
        tone = np.zeros(xs.shape)
        warm = np.zeros(xs.shape)
        ao = np.ones(xs.shape)

        for (i, j), p in cell.items():
            m = (wi == i) & (wj == j)
            if not m.any():
                continue
            X = lx[m] / mm_per_px_x          # back to px for tile sampling
            Y = ly[m] / mm_per_px_x
            ca, sa = np.cos(p["mrot"]), np.sin(p["mrot"])
            mott[m] = sample(mottle, X * ca - Y * sa + p["mox"], X * sa + Y * ca + p["moy"])
            grn[m] = sample(grain, X * ca + Y * sa + p["gox"], -X * sa + Y * ca + p["goy"])
            tone[m] = p["tone"]
            warm[m] = p["warm"]
            ao[m] = p["ao"]

            if p["kind"] == "stipple":
                cb, sb = np.cos(p["srot"]), np.sin(p["srot"])
                s = sample(stip, X * cb - Y * sb + p["sox"], X * sb + Y * cb + p["soy"])
                pattern[m] = np.where(s < 0, -s * STIPPLE_PIT_MM, s * STIPPLE_CREST_MM)
            elif p["kind"] == "comb":
                t = np.deg2rad(p["angle"])
                # measure across the lines, so the lines themselves run along t
                u = (lx[m] * np.sin(t) - ly[m] * np.cos(t)) / COMB_PITCH_MM + p["cphase"]
                # rounded ridge, flat-bottomed groove: cos shaped, biased low
                c = np.cos(2 * np.pi * u)
                c = np.sign(c) * np.abs(c) ** 0.75
                pattern[m] = np.where(c > 0, c * COMB_CREST_MM, -c * COMB_VALLEY_MM)

        # matte micro-relief everywhere on the face
        micro = (mott * 1.2 + grn) * GRAIN_MM / 0.02
        face_mm = BASE_MM + pattern + micro

        # Joint profile, from the joint centreline outwards: a slightly dished grout
        # floor, the tile's edge wall, its chamfer, then the face. Both transitions are
        # smoothed over a fraction of a millimetre so neither edge aliases.
        shoulder = half_joint_mm
        top = half_joint_mm + BEVEL_MM
        wall = smoothstep(shoulder - 0.35, shoulder + 0.35, edge_mm)   # grout -> tile
        in_face = smoothstep(shoulder + 0.35, top, edge_mm)            # chamfer -> face
        chamfer = BASE_MM - CHAMFER_DROP_MM
        grout_h = smoothstep(0.0, shoulder, edge_mm) * 0.12
        tile_h = chamfer * (1.0 - in_face) + face_mm * in_face
        height = np.clip(grout_h * (1.0 - wall) + tile_h * wall, 0.0, TOTAL_MM)

        onface = edge_mm > top
        if onface.any():
            stats["min_face_mm"] = min(stats["min_face_mm"], float(height[onface].min()))
            stats["min_pattern_mm"] = min(stats["min_pattern_mm"],
                                          float(pattern[onface].min()))

        bump[y0:y1] = np.round(np.clip(height / TOTAL_MM, 0, 1) * 65535.0).astype(np.uint16)

        # ---- colour ----------------------------------------------------------
        field = (1.0 + mott * MOTTLE_GAIN + grn * GRAIN_GAIN + tone) * ao
        cavity = 1.0 + CAVITY_GAIN * np.clip(pattern / 0.45, -1.2, 0.4)
        rgb = BASE_RGB[None, None, :] * (field * cavity)[..., None]
        rgb[..., 0] *= 1.0 + warm
        rgb[..., 2] *= 1.0 - warm

        grout = GROUT_RGB[None, None, :] * (1.0 + 0.5 * tone)[..., None]
        grout = grout * (0.90 + 0.10 * smoothstep(0.0, shoulder, edge_mm))[..., None]
        blend = wall[..., None]
        rgb = grout * (1 - blend) + rgb * blend
        # the chamfer catches less light than the face in any real install
        rgb *= (0.94 + 0.06 * in_face)[..., None]

        color[y0:y1] = np.round(np.clip(rgb, 0, 255)).astype(np.uint8)
        print("  rows %d-%d done" % (y0, y1))

    Image.fromarray(color, mode="RGB").save(
        out_path("textures", "Hex10_Dimensional_Color.png"))
    Image.fromarray(bump).save(out_path("textures", "Hex10_Dimensional_Bump16.png"))

    clearance = stats["min_face_mm"]
    report = {
        "atlas_hexagons": [COLS, ROWS],
        "image_px": [W, H],
        "ppi": PPI,
        "sample_size_in": [ATLAS_W_IN, ATLAS_H_IN],
        "hexagon_across_flats_in": FLATS_IN,
        "hexagon_across_corners_in": FLATS_IN * 2.0 / np.sqrt(3.0),
        "joint_in": JOINT_IN,
        "face_counts": counts,
        "adjacency_violations": bad,
        "comb_pitch_mm": COMB_PITCH_MM,
        "comb_angles_deg": list(COMB_ANGLES_DEG),
        "relief_mm": {
            "total_range": TOTAL_MM,
            "tile_base_plane": BASE_MM,
            "grout_step": BASE_MM,
            "comb_peak_to_peak": COMB_CREST_MM - COMB_VALLEY_MM,
            "stipple_peak_to_peak": STIPPLE_CREST_MM - STIPPLE_PIT_MM,
            "deepest_pattern_below_base": stats["min_pattern_mm"],
            "lowest_face_point_above_grout_floor": clearance,
        },
        "base_rgb": BASE_RGB.tolist(),
        "grout_rgb": GROUT_RGB.tolist(),
        "face_ao": FACE_AO,
        "seed": SEED,
    }
    json.dump(report, open(out_path("textures", "build_report.json"), "w"), indent=2)
    print("deepest pattern %.3f mm below the tile plane; lowest face point %.3f mm "
          "above the grout floor" % (stats["min_pattern_mm"], clearance))
    if clearance <= 0:
        raise RuntimeError("pattern punches through the grout floor")
    print("wrote textures/Hex10_Dimensional_Color.png, "
          "textures/Hex10_Dimensional_Bump16.png, textures/build_report.json")


if __name__ == "__main__":
    main()
