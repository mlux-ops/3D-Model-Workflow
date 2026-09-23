"""Build the seamless, non-repeating colour and bump maps for the 9 in blush terrazzo
hexagon tile, from a single isolated product photo (references/01_single_tile_isolated.jpg).

Geometry: same flat-top hexagon Voronoi-lattice-on-a-torus construction used for
output/hex_10in_dimensional (nearest-centre assigns each pixel to a cell; the
perpendicular-bisector distance to the second-nearest centre gives an exact analytic
distance to the joint centreline). Centres are enumerated on a torus, so the image
wraps by construction with no border fade.

Non-repetition, 100% photo-based (per the user's standing instruction on the ElmStone
Jute job this same session: procedural chip synthesis is not acceptable; real photo
content is required). Unlike a rectangular tile, a REGULAR HEXAGON has the full 12-
member dihedral symmetry group (6 rotations x mirror) that maps the hexagon shape
exactly onto itself -- so, unlike ElmStone's rectangular panels (only 4 of 8 symmetries
kept the 2:1 aspect), all 12 transforms of this source photo are usable here with zero
distortion.

There is only one real photo of this tile (no larger swatch to crop different regions
from, unlike Poke's mosaic sheet), so the atlas is sized to exactly 12 cells (4 columns
x 3 rows) -- one cell per dihedral transform, assigned by a derangement so no two
adjacent cells share a transform. This guarantees NO TWO CELLS IN THE WHOLE ATLAS ARE
IDENTICAL, which a larger atlas (more cells than the 12 available transforms) could not
promise without either repeating a transform somewhere or inventing content that is not
in the photo. Each cell also gets an independent, subtle tone/warmth jitter, matching
real terrazzo panels' normal small batch-to-batch shade variation.

Nominal-size note: "9 inch hexagon" is ambiguous for a hexagon (see the 10 in hex job's
README precedent). Taken here as 9 in ACROSS THE FLATS, matching that precedent, not
measured from any stated spec. If the manufacturer means 9 in point-to-point, every
dimension below scales by 0.866; a single constant change and rebuild.

Joint: no manufacturer width was given and the installed mockup
(references/02_installed_hex_grid_mockup.webp) shows no visible grout line at all at
the resolution available -- a near-hairline joint. Modelled as 1/16 in, coloured to
match the tile's own measured cement-base tone, so it reads as understated as the
mockup shows rather than inventing a contrasting grout that isn't there.

Outputs
-------
textures/BlushTerrazzo_Hex9_Color.png    8-bit sRGB
textures/BlushTerrazzo_Hex9_Bump16.png   16-bit greyscale
textures/build_report.json
"""

import hashlib
import json
import os

import numpy as np
from PIL import Image

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def out_path(*parts):
    p = os.path.abspath(os.path.join(RUN_DIR, *parts))
    if os.path.commonpath([p, RUN_DIR]) != RUN_DIR:
        raise RuntimeError("refusing to write outside the run dir: %s" % p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


SRC_PATH = os.path.join(RUN_DIR, "references", "01_single_tile_isolated.jpg")

# --- source hexagon, measured from the isolated photo (non-white bounding box) -------
SRC_BBOX = (12, 89, 1185, 1111)          # x0, y0, x1, y1 -- tile extent on white bg
SRC_ACROSS_FLATS_PX = SRC_BBOX[3] - SRC_BBOX[1]     # 1022 px = vertical extent

# --- product -----------------------------------------------------------------
FLATS_IN = 9.0                        # hexagon across-flats, nominal ASSUMPTION -- see docstring
JOINT_IN = 0.0625                     # 1/16 in, assumed -- no width stated, mockup shows a hairline joint
ATLAS_COLS, ATLAS_ROWS = 4, 3         # = 12 cells = 12 dihedral transforms, exactly, no duplicates
PPI = SRC_ACROSS_FLATS_PX / FLATS_IN  # native scale: the identity transform needs no resampling

MODULE_F = FLATS_IN + JOINT_IN
MODULE_C = MODULE_F * 2.0 / np.sqrt(3.0)
COL_PITCH_IN = MODULE_C * 0.75
ROW_PITCH_IN = MODULE_F
ATLAS_W_IN = ATLAS_COLS * COL_PITCH_IN
ATLAS_H_IN = ATLAS_ROWS * ROW_PITCH_IN
W = int(round(ATLAS_W_IN * PPI))
H = int(round(ATLAS_H_IN * PPI))
COL_PITCH_PX = W / float(ATLAS_COLS)
ROW_PITCH_PX = H / float(ATLAS_ROWS)

# --- relief, flat tile: subtle micro-relief + joint recess only (no sculpted pattern) --
TOTAL_MM = 0.35
BASE_MM = 0.25                        # tile face plane
BEVEL_MM = 1.2                        # chamfer width at the tile edge, mm
MICRO_MM = 0.025                      # matte micro-relief amplitude, derived from tone

TONE_JITTER = 0.018
WARM_JITTER = 0.007
GROUT_DARKEN = 0.94                   # grout reads a touch flatter/darker than the tile face

STRIP = 512
SEED = 20260920


def h32(*vals):
    s = "|".join(str(v) for v in vals) + "|%d" % SEED
    d = hashlib.blake2b(s.encode("ascii"), digest_size=8).digest()
    return int.from_bytes(d, "big") / float(1 << 64)


def load_source():
    im = np.asarray(Image.open(SRC_PATH).convert("RGB"), dtype=np.float64)
    x0, y0, x1, y1 = SRC_BBOX
    crop = im[y0:y1, x0:x1]
    across_corners_px = SRC_ACROSS_FLATS_PX * 2.0 / np.sqrt(3.0)
    target = np.asarray(
        Image.fromarray(crop.astype(np.uint8)).resize(
            (int(round(across_corners_px)), SRC_ACROSS_FLATS_PX), Image.LANCZOS),
        dtype=np.float64,
    )
    return target   # shape (SRC_ACROSS_FLATS_PX, across_corners_px, 3); hexagon inscribed


def dihedral_transforms():
    """12 (angle_deg, flip) pairs -- the full symmetry group of a regular hexagon."""
    return [(a, f) for f in (False, True) for a in (0, 60, 120, 180, 240, 300)]


def assign_transforms(rng):
    """One of the 12 transforms per cell, each used exactly once, no two adjacent cells
    sharing a transform (trivially true here since every transform is unique, but the
    spatial ORDER is still shuffled so e.g. identity and its own reflection don't
    default to sitting next to each other)."""
    cells = [(i, j) for j in range(ATLAS_ROWS) for i in range(ATLAS_COLS)]
    xforms = dihedral_transforms()
    order = list(range(len(xforms)))
    rng.shuffle(order)
    return {cells[k]: xforms[order[k]] for k in range(len(cells))}


def sample_bilinear(img, x, y):
    h, w = img.shape[:2]
    xc = np.clip(x, 0, w - 1.001)
    yc = np.clip(y, 0, h - 1.001)
    x0 = np.floor(xc).astype(np.int64)
    y0 = np.floor(yc).astype(np.int64)
    x1 = x0 + 1
    y1 = y0 + 1
    fx = (xc - x0)[..., None]
    fy = (yc - y0)[..., None]
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x1] * fx * (1 - fy) +
            img[y1, x0] * (1 - fx) * fy + img[y1, x1] * fx * fy)


def inverse_map(lx_mm, ly_mm, angle_deg, flip):
    """Given a local coordinate (mm, relative to a lattice cell's centre) and the
    cell's chosen dihedral transform, return the coordinate to sample from the
    UNTRANSFORMED source image (also mm, relative to the source's own centre)."""
    t = np.deg2rad(angle_deg)
    x, y = lx_mm, ly_mm
    if flip:
        x = -x
    # inverse rotation: rotate by -angle
    xr = x * np.cos(-t) - y * np.sin(-t)
    yr = x * np.sin(-t) + y * np.cos(-t)
    return xr, yr


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-12), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def main():
    src = load_source()
    src_h, src_w = src.shape[:2]
    src_cx, src_cy = src_w / 2.0, src_h / 2.0
    mm_per_px_src = FLATS_IN * 25.4 / SRC_ACROSS_FLATS_PX

    rng = np.random.default_rng(SEED)
    transforms = assign_transforms(rng)
    print("atlas %d x %d hexagons (= %d dihedral transforms, each used exactly once)"
          % (ATLAS_COLS, ATLAS_ROWS, len(dihedral_transforms())))
    print("%d px x %d px, %.3f x %.3f in, native PPI %.3f" % (W, H, ATLAS_W_IN, ATLAS_H_IN, PPI))

    cell = {}
    for (i, j), (angle, flip) in transforms.items():
        cell[(i, j)] = {
            "angle": angle, "flip": flip,
            "tone": 1.0 + (h32("tone", i, j) * 2 - 1) * TONE_JITTER,
            "warm": (h32("warm", i, j) * 2 - 1) * WARM_JITTER,
        }

    cpx = W / float(ATLAS_COLS)
    rpx = H / float(ATLAS_ROWS)
    mm_per_px = ATLAS_W_IN * 25.4 / W
    half_joint_mm = JOINT_IN * 25.4 / 2.0

    color = np.zeros((H, W, 3), dtype=np.uint8)
    bump = np.zeros((H, W), dtype=np.uint16)
    min_face_mm = [9e9]

    for y0 in range(0, H, STRIP):
        y1 = min(y0 + STRIP, H)
        ys, xs = np.mgrid[y0:y1, 0:W].astype(np.float64)
        ys += 0.5
        xs += 0.5

        ci = np.round(xs / cpx).astype(np.int64)
        d1 = np.full(xs.shape, np.inf)
        d2 = np.full(xs.shape, np.inf)
        bi = np.zeros(xs.shape, dtype=np.int64)
        bj = np.zeros(xs.shape, dtype=np.int64)
        bcx = np.zeros(xs.shape)
        bcy = np.zeros(xs.shape)
        for di in (-1, 0, 1):
            i_ = ci + di
            cx = i_ * cpx
            yoff = np.where(i_ % 2 != 0, rpx * 0.5, 0.0)
            j_ = np.round((ys - yoff) / rpx).astype(np.int64)
            for dj in (-1, 0, 1):
                jj = j_ + dj
                cy = yoff + jj * rpx
                dx = xs - cx
                dy = ys - cy
                d = np.sqrt(dx * dx + dy * dy)
                closer = d < d1
                d2 = np.minimum(d2, np.where(closer, d1, d))
                bi = np.where(closer, i_, bi)
                bj = np.where(closer, jj, bj)
                bcx = np.where(closer, cx, bcx)
                bcy = np.where(closer, cy, bcy)
                d1 = np.where(closer, d, d1)
        edge_px = (d2 - d1) * 0.5
        edge_mm = edge_px * mm_per_px
        wi = np.mod(bi, ATLAS_COLS)
        wj = np.mod(bj, ATLAS_ROWS)

        lx_mm = (xs - bcx) * mm_per_px
        ly_mm = (ys - bcy) * mm_per_px

        rgb = np.zeros((y1 - y0, W, 3))
        micro = np.zeros((y1 - y0, W))

        for (i, j), p in cell.items():
            m = (wi == i) & (wj == j)
            if not m.any():
                continue
            sx, sy = inverse_map(lx_mm[m], ly_mm[m], p["angle"], p["flip"])
            src_px = sx / mm_per_px_src + src_cx
            src_py = sy / mm_per_px_src + src_cy
            samp = sample_bilinear(src, src_px, src_py)
            tone = p["tone"]
            warm = p["warm"]
            samp = samp * tone
            samp[:, 0] *= 1.0 + warm
            samp[:, 2] *= 1.0 - warm
            rgb[m] = samp
            luma = samp.mean(axis=1)
            micro[m] = (luma - luma.mean()) / 255.0

        # joint: flat recessed floor, then a chamfer up to the tile plane
        shoulder = half_joint_mm
        top = half_joint_mm + BEVEL_MM
        wall = smoothstep(shoulder - 0.12, shoulder + 0.12, edge_mm)
        in_face = smoothstep(shoulder + 0.12, top, edge_mm)
        chamfer = BASE_MM * 0.5
        face_mm = BASE_MM + micro * MICRO_MM / 0.02
        tile_h = chamfer * (1.0 - in_face) + face_mm * in_face
        height = np.clip(tile_h * wall, 0.0, TOTAL_MM)

        onface = edge_mm > top
        if onface.any():
            min_face_mm[0] = min(min_face_mm[0], float(height[onface].min()))

        bump[y0:y1] = np.round(np.clip(height / TOTAL_MM, 0, 1) * 65535.0).astype(np.uint16)

        grout_tint = GROUT_DARKEN + (1.0 - GROUT_DARKEN) * smoothstep(0.0, shoulder, edge_mm)
        out_rgb = rgb * wall[..., None] + (rgb * grout_tint[..., None]) * (1 - wall[..., None])
        color[y0:y1] = np.round(np.clip(out_rgb, 0, 255)).astype(np.uint8)
        print("  rows %d-%d done" % (y0, y1))

    Image.fromarray(color, mode="RGB").save(
        out_path("textures", "BlushTerrazzo_Hex9_Color.png"))
    Image.fromarray(bump).save(out_path("textures", "BlushTerrazzo_Hex9_Bump16.png"))

    report = {
        "atlas_hexagons": [ATLAS_COLS, ATLAS_ROWS],
        "image_px": [W, H],
        "ppi": PPI,
        "sample_size_in": [ATLAS_W_IN, ATLAS_H_IN],
        "hexagon_across_flats_in": FLATS_IN,
        "hexagon_across_corners_in": FLATS_IN * 2.0 / np.sqrt(3.0),
        "joint_in": JOINT_IN,
        "dihedral_transforms_used": len(dihedral_transforms()),
        "duplicate_cells_possible": False,
        "relief_mm": {
            "total_range": TOTAL_MM,
            "tile_base_plane": BASE_MM,
            "grout_step": BASE_MM,
            "lowest_face_point_above_grout_floor": min_face_mm[0],
        },
        "seed": SEED,
    }
    json.dump(report, open(out_path("textures", "build_report.json"), "w"), indent=2)
    print("lowest face point above grout floor: %.4f mm" % min_face_mm[0])
    print("wrote textures/BlushTerrazzo_Hex9_Color.png, "
          "textures/BlushTerrazzo_Hex9_Bump16.png, textures/build_report.json")


if __name__ == "__main__":
    main()
