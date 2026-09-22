"""Measure what the flat layout reference can actually tell us about the product.

The layout art draws the joints and the sculpted surface textures in a slightly cooler
grey than the cream glaze, so (R - B) < WARM_T isolates both from the plain tile field.
That mask is the basis for every number below.

Measured here:
  * hexagon orientation and pitch in the reference (read off the joint grid)
  * comb line pitch, by FFT across named comb faces, converted to mm
  * how much of the field carries a texture rather than being plain
  * plain, joint-free square patches the colour pipeline samples for mottling

Not measured here, and recorded as inspection-derived in README.md: the stipple / comb
split and the comb directions. Automated blob classification was tried and abandoned -
adjacent textured hexagons merge across their shared joint and the counts came out
unstable, so the mix was read off _REVIEW_reference_mask.png by eye instead.

Nothing spatial is taken from the installed photo: it is in perspective.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from extract_source import gaussian_blur

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def out_path(*parts):
    p = os.path.abspath(os.path.join(RUN_DIR, *parts))
    if os.path.commonpath([p, RUN_DIR]) != RUN_DIR:
        raise RuntimeError("refusing to write outside the run dir: %s" % p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


REF1 = os.path.join(RUN_DIR, "references", "user_supplied_01_flat_layout_variation.webp")
WARM_T = 31.0
# Flat-top hexagons. Column pitch read off the joint grid in the R-B mask; the row
# pitch of a regular hexagon follows from it.
COL_PITCH_PX = 378.0
ROW_PITCH_PX = COL_PITCH_PX * 2.0 / 3.0 * np.sqrt(3.0)   # = across-flats, 436.4 px
NOMINAL_FLATS_IN = 10.0

# Crops sitting inside combed faces, picked by eye off the mask review image.
COMB_CROPS = [(940, 1120, 200, 400), (920, 1100, 1130, 1300), (45, 225, 975, 1130)]


def comb_pitch(g, x0, x1, y0, y1):
    """Dominant line pitch across a combed face, in px."""
    p = g[y0:y1, x0:x1].astype(np.float64)
    best = None
    for axis in (0, 1):
        prof = p.mean(axis=axis)
        prof = (prof - prof.mean()) * np.hanning(len(prof))
        spec = np.abs(np.fft.rfft(prof))
        k = int(np.argmax(spec[6:]) + 6)
        strength = float(spec[k] / (spec[6:].mean() + 1e-9))
        if best is None or strength > best[0]:
            best = (strength, len(prof) / k)
    return best


def main():
    rgb = np.asarray(Image.open(REF1).convert("RGB"), dtype=np.float64)
    H, W = rgb.shape[:2]
    grey = rgb.mean(axis=2)
    mask = (rgb[:, :, 0] - rgb[:, :, 2]) < WARM_T
    dens = gaussian_blur(mask.astype(np.float64), 6.0)
    textured = gaussian_blur((dens > 0.15).astype(np.float64), 22.0) > 0.45

    print("reference %dx%d px" % (W, H))
    print("R-B mask (joints + drawn texture): %.1f%% of image" % (100 * mask.mean()))
    print("textured-face regions, hole-filled: %.1f%% of image area" % (100 * textured.mean()))
    print("hexagons in frame: %.1f (col pitch %.1f px, across-flats %.1f px)"
          % (W * H / (COL_PITCH_PX * ROW_PITCH_PX), COL_PITCH_PX, ROW_PITCH_PX))

    mm_per_px = NOMINAL_FLATS_IN * 25.4 / ROW_PITCH_PX
    pitches = []
    for x0, x1, y0, y1 in COMB_CROPS:
        s, px = comb_pitch(grey, x0, x1, y0, y1)
        pitches.append(px)
        print("comb crop x%d-%d y%d-%d: pitch %.2f px = %.2f mm  (peak/mean %.1f)"
              % (x0, x1, y0, y1, px, px * mm_per_px, s))
    pitch_mm = float(np.median(pitches)) * mm_per_px
    print("comb line pitch, median: %.2f mm (%.4f in) at a %.0f in across-flats hexagon"
          % (pitch_mm, pitch_mm / 25.4, NOMINAL_FLATS_IN))

    size = 260
    ii = np.pad(mask.astype(np.float64).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    plain = []
    for y in range(0, H - size, 40):
        for x in range(0, W - size, 40):
            s = ii[y + size, x + size] - ii[y, x + size] - ii[y + size, x] + ii[y, x]
            if s / float(size * size) < 0.03:
                if all(abs(x - a) >= size or abs(y - b) >= size for a, b in plain):
                    plain.append((x, y))
    print("plain joint-free %d px patches found: %d" % (size, len(plain)))

    vis = np.zeros((H, W, 3), dtype=np.uint8)
    vis[..., 0] = np.where(textured, 90, 0)
    vis[..., 2] = np.where(textured, 30, 0)
    vis[mask] = (255, 255, 255)
    im = Image.fromarray(vis)
    im.resize((900, int(900 * H / W)), Image.LANCZOS).save(
        out_path("source", "_REVIEW_reference_mask.png"))

    json.dump({
        "reference": os.path.basename(REF1),
        "reference_px": [W, H],
        "hexagon_orientation": "flat-top",
        "col_pitch_px": COL_PITCH_PX,
        "across_flats_px": ROW_PITCH_PX,
        "across_corners_px": COL_PITCH_PX * 4.0 / 3.0,
        "mm_per_px_at_10in_flats": mm_per_px,
        "comb_pitch_px": pitches,
        "comb_pitch_mm": pitch_mm,
        "comb_pitch_in": pitch_mm / 25.4,
        "mask_area_fraction": float(mask.mean()),
        "textured_region_area_fraction": float(textured.mean()),
        "plain_patches_xy": plain,
        "plain_patch_px": size,
    }, open(out_path("source", "reference_stats.json"), "w"), indent=2)
    print("wrote source/reference_stats.json, source/_REVIEW_reference_mask.png")


if __name__ == "__main__":
    main()
