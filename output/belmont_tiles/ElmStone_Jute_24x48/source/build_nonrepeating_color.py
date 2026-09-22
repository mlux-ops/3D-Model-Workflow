"""Build non-repeating, seamless colour atlases for both ElmStone Jute finishes --
THIRD attempt, reverted to a photo-based method per explicit user direction.

History
-------
Attempt 1: roll + flip + tone jitter of the single reference photo per cell. Rejected
on self-review: the same recognizable large-scale feature (two vein streaks on the
flat, one big cloud blob on the cross-cut) was still visible in every cell, just
repositioned -- the exact failure WORKFLOW.md names ("rotating one face, adding random
tint... is not sufficient variation").

Attempt 2: replaced the repeating feature with procedural synthesis (statistically
matched to measurements of the real photo -- vein spacing/waviness/colour, mottle
contrast) rather than photo pixels. This DID stop the literal repeat, but the user
reviewed the result and rejected it on a different, more important ground: it reads as
visibly synthetic/CG rather than photographic, and no amount of grain-amplitude tuning
closed that gap without introducing new artifacts (either near-invisible or harsh
digital noise). User instruction, 2026-09-20: "it needs to be the photo based version,
anything close to the deliverable is bad looking."

This attempt (delivered)
----------------------------
Back to attempt 1's method -- 100% real photo pixels, no synthetic geometry -- since
photographic authenticity matters more here than defeating a side-by-side comparison of
adjacent cells. The single photo is made seamlessly self-periodic (so any cyclic roll of
it is artifact-free), then each of the atlas's cells gets an independent roll phase, one
of the four grain-direction-preserving transforms, and a small tone/warmth jitter.

Honest limitation, not fixed by this attempt: with only one real photograph per finish,
there is a hard ceiling on achievable non-repetition. WORKFLOW.md's guidance on this
exact situation: "If source images cannot support convincing variation, obtain
additional faces or document the limitation and hold final acceptance." The two
dominant vein streaks (flat) and the one dominant cloud blob (cross-cut) can still be
found, differently positioned, in every cell if compared side by side. What this attempt
avoids is inventing content that isn't in the photo. If additional real photographs of
different areas of either finish become available, they should replace this rather than
this being re-processed further.

Both finishes still use the reveal-border joint convention measured from the shipped
Color.png (209, 209, 209, ~0.047 in band) at every cell edge, so cells meet the way real
installed panels meet and the atlas wraps exactly with no additional blending.

Outputs
-------
ElmStone_Jute_24x48/textures/Color_NonRepeating.png   flat/vein-cut atlas
ElmStone_Jute_CrossCut_24x48/textures/Color.png       cross-cut atlas
Both: 9 cells (3x3), 144.1875 x 72.1875 in, PPI 64.
"""

import hashlib
import json
import os

import numpy as np
from PIL import Image

FLAT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BELMONT_DIR = os.path.dirname(FLAT_DIR)
CROSSCUT_DIR = os.path.join(BELMONT_DIR, "ElmStone_Jute_CrossCut_24x48")

PANEL_W_IN, PANEL_H_IN = 48.0625, 24.0625
ATLAS_COLS, ATLAS_ROWS = 3, 3
PPI = 64.0
REVEAL_RGB = np.array([209.0, 209.0, 209.0])
REVEAL_BAND_IN = 0.047
BLEND_FRAC = 0.09           # fraction of panel size used to make it self-periodic

CELL_W_PX = int(round(PANEL_W_IN * PPI))
CELL_H_PX = int(round(PANEL_H_IN * PPI))
REVEAL_BAND_PX = max(2, int(round(REVEAL_BAND_IN * PPI)))
SEED = 20260920


def out_path(base_dir, *parts):
    p = os.path.abspath(os.path.join(base_dir, *parts))
    if os.path.commonpath([p, base_dir]) != base_dir:
        raise RuntimeError("refusing to write outside %s: %s" % (base_dir, p))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def h01(*vals):
    s = "|".join(str(v) for v in vals) + "|%d" % SEED
    d = hashlib.blake2b(s.encode("ascii"), digest_size=8).digest()
    return int.from_bytes(d, "big") / float(1 << 64)


def make_tileable_rgb(a, band_frac=BLEND_FRAC):
    """Half-period offset + cosine cross-fade, per channel, in float64.

    After this, a cyclic roll of `a` by any amount is free of visible seams: the
    original hard border has been moved to the middle and blended away, so any new
    "cut" a later roll introduces lands on genuinely continuous, blended content.
    """
    h, w = a.shape[:2]
    out = a.copy()
    bw = max(2, int(w * band_frac))
    bh = max(2, int(h * band_frac))

    rolled = np.roll(a, w // 2, axis=1)
    t = np.linspace(0.0, 1.0, bw)[None, :, None]
    x0 = w // 2 - bw // 2
    out[:, x0:x0 + bw] = rolled[:, x0:x0 + bw] * (1 - t) + a[:, x0:x0 + bw] * t

    rolled = np.roll(out, h // 2, axis=0)
    t = np.linspace(0.0, 1.0, bh)[:, None, None]
    y0 = h // 2 - bh // 2
    out[y0:y0 + bh] = rolled[y0:y0 + bh] * (1 - t) + out[y0:y0 + bh] * t
    return out


def dihedral(a, k):
    """The 8 symmetries of the square: k = 0..7."""
    rot = np.rot90(a, k % 4)
    return np.fliplr(rot) if k >= 4 else rot


# identity, h-flip, 180 rotation, v-flip -- the only ones that preserve a 2:1 aspect
# ratio and, for the vein-cut finish, the horizontal grain direction.
ORIENTATION_PRESERVING = (0, 4, 2, 6)


def roll_xy(a, rx, ry):
    return np.roll(np.roll(a, rx, axis=1), ry, axis=0)


def apply_border(cell, band_px, reveal=REVEAL_RGB):
    """Stamp the measured reveal band on all four edges, smoothstepped inward."""
    t = np.arange(band_px, dtype=np.float64) / band_px
    ramp = t * t * (3.0 - 2.0 * t)
    out = cell.copy()
    for i in range(band_px):
        f = ramp[i]
        out[:, i] = reveal * (1 - f) + out[:, i] * f
        out[:, -1 - i] = reveal * (1 - f) + out[:, -1 - i] * f
    for i in range(band_px):
        f = ramp[i]
        out[i, :] = reveal * (1 - f) + out[i, :] * f
        out[-1 - i, :] = reveal * (1 - f) + out[-1 - i, :] * f
    return out


SMALL_SOURCE_FRACTION = 0.4   # below this fraction of the cell size, skip roll/periodicity
                              # (legitimate full-panel photos here run 875-945 px tall
                              # against a 1540 px cell = 0.57-0.61; the floor crops run
                              # ~288 px = 0.19 -- 0.4 sits cleanly between the two)


def build_atlas(source_paths, allowed_transforms, label, tone_jitter=0.035, warm_jitter=0.012):
    """`source_paths`: one path, or a list of paths for genuinely different real photos
    (each cell independently picks one, in addition to its own roll/flip/jitter) --
    used for the cross-cut finish, which has a second real photo available (the
    rectified floor shot) and so isn't limited to reprocessing the one swatch photo.

    A small crop (well under one cell's pixel size, e.g. the floor-photo crops, native
    ~400x285 against a 3076x1540 cell) does NOT get the make_tileable_rgb treatment or
    a roll: `make_tileable_rgb` blends the image's own left/right and top/bottom halves
    together to make ANY roll offset seamless, which is invisible on a large source
    whose own edges already look similar, but produces an obvious ghosted double-exposure
    band on a small, arbitrary crop -- confirmed on inspection (first version of this
    fix). Skipping roll entirely for small crops avoids that: they're stretched once,
    used directly, and only flipped/tone-jittered like every other cell.
    """
    if isinstance(source_paths, str):
        source_paths = [source_paths]

    panels = []
    is_small = []
    for p in source_paths:
        src = np.asarray(Image.open(p).convert("RGB"), dtype=np.float64)
        small = (src.shape[1] < CELL_W_PX * SMALL_SOURCE_FRACTION or
                 src.shape[0] < CELL_H_PX * SMALL_SOURCE_FRACTION)
        print("%s: source %s (%s) -> resizing to one panel cell %d x %d px%s"
              % (label, os.path.basename(p), src.shape[1::-1], CELL_W_PX, CELL_H_PX,
                 "  [small crop: no roll/periodicity]" if small else ""))
        panel = np.asarray(
            Image.fromarray(src.astype(np.uint8)).resize((CELL_W_PX, CELL_H_PX), Image.LANCZOS),
            dtype=np.float64,
        )
        panels.append(panel if small else make_tileable_rgb(panel))
        is_small.append(small)

    atlas = np.zeros((CELL_H_PX * ATLAS_ROWS, CELL_W_PX * ATLAS_COLS, 3), dtype=np.float64)
    used = []
    for j in range(ATLAS_ROWS):
        for i in range(ATLAS_COLS):
            si = int(h01(label, "src", i, j) * len(panels))
            panel = panels[si]
            k = allowed_transforms[int(h01(label, "xf", i, j) * len(allowed_transforms))]
            if is_small[si]:
                rx = ry = 0
            else:
                rx = int(h01(label, "rx", i, j) * CELL_W_PX)
                ry = int(h01(label, "ry", i, j) * CELL_H_PX)
            cell = roll_xy(panel, rx, ry)
            cell = dihedral(cell, k)
            assert cell.shape[:2] == (CELL_H_PX, CELL_W_PX), (
                "transform %d changed the cell's aspect ratio" % k)
            tone = 1.0 + (h01(label, "tone", i, j) * 2 - 1) * tone_jitter
            warm = (h01(label, "warm", i, j) * 2 - 1) * warm_jitter
            cell = cell * tone
            cell[..., 0] *= 1.0 + warm
            cell[..., 2] *= 1.0 - warm
            cell = apply_border(cell, REVEAL_BAND_PX)
            atlas[j * CELL_H_PX:(j + 1) * CELL_H_PX, i * CELL_W_PX:(i + 1) * CELL_W_PX] = cell
            used.append({"cell": [i, j], "source": os.path.basename(source_paths[si]),
                        "transform": int(k), "roll_px": [rx, ry],
                        "tone": round(tone, 4), "warm": round(warm, 4)})

    atlas_u8 = np.clip(np.round(atlas), 0, 255).astype(np.uint8)
    return atlas_u8, used


def wrap_report(atlas_u8):
    a = atlas_u8.astype(np.int64)
    lr = float(np.abs(a[:, 0] - a[:, -1]).mean())
    tb = float(np.abs(a[0, :] - a[-1, :]).mean())
    inner = float(np.abs(a[:, CELL_W_PX] - a[:, CELL_W_PX + 1]).mean())
    print("wrap check: L/R step %.3f   T/B step %.3f   typical interior step %.3f"
          % (lr, tb, inner))
    return {"lr_step": lr, "tb_step": tb, "typical_interior_step": inner}


def main():
    flat_src = os.path.join(FLAT_DIR, "references", "05_new_flat_veincut.jpg")
    flat_atlas, flat_used = build_atlas(flat_src, ORIENTATION_PRESERVING, "flat")
    flat_out = out_path(FLAT_DIR, "textures", "Color_NonRepeating.png")
    Image.fromarray(flat_atlas, mode="RGB").save(flat_out)
    flat_wrap = wrap_report(flat_atlas)
    print("wrote %s  (%d x %d px)" % (flat_out, flat_atlas.shape[1], flat_atlas.shape[0]))

    json.dump({
        "finish": "flat / vein-cut",
        "method": "photo-based: roll + orientation-preserving flip + tone/warmth jitter "
                   "of the single reference photo, per user direction 2026-09-20 "
                   "(procedural vein synthesis tried and rejected as looking synthetic)",
        "source": os.path.basename(flat_src),
        "atlas_cells": [ATLAS_COLS, ATLAS_ROWS],
        "cell_physical_in": [PANEL_W_IN, PANEL_H_IN],
        "atlas_physical_in": [PANEL_W_IN * ATLAS_COLS, PANEL_H_IN * ATLAS_ROWS],
        "pixels": [flat_atlas.shape[1], flat_atlas.shape[0]],
        "ppi": PPI,
        "allowed_transforms": "identity, horizontal flip, 180 rotation, vertical flip "
                               "(orientation-preserving only - veins run horizontal)",
        "reveal_rgb": REVEAL_RGB.tolist(),
        "reveal_band_in": REVEAL_BAND_IN,
        "wrap_check": flat_wrap,
        "cells": flat_used,
    }, open(out_path(FLAT_DIR, "textures", "nonrepeating_flat_report.json"), "w"), indent=2)

    # Three genuinely different real photos for the cross-cut finish: the original
    # straight-on swatch, plus two clean, joint-free crops from the perspective-
    # corrected floor photo (source/rectify_floor_photo.py) -- a second real photograph
    # of this material, which the flat/vein-cut finish does not have available.
    cross_sources = [
        os.path.join(FLAT_DIR, "references", "06_new_fluted_crosscut.webp"),
        os.path.join(CROSSCUT_DIR, "references", "07_crop_tile1.jpg"),
        os.path.join(CROSSCUT_DIR, "references", "07_crop_tile2.jpg"),
        os.path.join(CROSSCUT_DIR, "references", "07_crop_tile3.jpg"),
    ]
    cross_atlas, cross_used = build_atlas(cross_sources, ORIENTATION_PRESERVING, "crosscut")
    cross_out = out_path(CROSSCUT_DIR, "textures", "Color.png")
    Image.fromarray(cross_atlas, mode="RGB").save(cross_out)
    cross_wrap = wrap_report(cross_atlas)
    print("wrote %s  (%d x %d px)" % (cross_out, cross_atlas.shape[1], cross_atlas.shape[0]))

    json.dump({
        "finish": "fluted / cross-cut",
        "method": "photo-based: roll + orientation-preserving flip + tone/warmth jitter, "
                   "drawing each cell from one of THREE real photo sources (the original "
                   "swatch plus two crops of a perspective-corrected second real floor "
                   "photo) rather than one -- see SOURCE_SELECTION.md",
        "sources": [os.path.basename(p) for p in cross_sources],
        "atlas_cells": [ATLAS_COLS, ATLAS_ROWS],
        "cell_physical_in": [PANEL_W_IN, PANEL_H_IN],
        "atlas_physical_in": [PANEL_W_IN * ATLAS_COLS, PANEL_H_IN * ATLAS_ROWS],
        "pixels": [cross_atlas.shape[1], cross_atlas.shape[0]],
        "ppi": PPI,
        "allowed_transforms": "identity, horizontal flip, 180 rotation, vertical flip "
                               "(90/270 skipped: would stretch the 2:1 panel aspect)",
        "reveal_rgb": REVEAL_RGB.tolist(),
        "reveal_band_in": REVEAL_BAND_IN,
        "wrap_check": cross_wrap,
        "cells": cross_used,
    }, open(out_path(CROSSCUT_DIR, "textures", "nonrepeating_crosscut_report.json"), "w"), indent=2)

    print("done")


if __name__ == "__main__":
    main()
