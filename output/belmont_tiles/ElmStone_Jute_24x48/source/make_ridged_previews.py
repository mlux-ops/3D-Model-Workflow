"""Review images for the finely-ridged bump variant, per the WORKFLOW.md visual
acceptance gate: wrap preview, correctly scaled surface, and grazing light.

Writes into textures/:
  _PREVIEW_ridged_tiling.jpg     2x2 wrap of the shipped Color.png shaded by the new
                                 ridged bump, for seam inspection
  _PREVIEW_ridged_grazing.jpg    the full 48x24 in panel under 12 degree grazing light
  _PREVIEW_ridged_closeup.jpg    a few-inch close-up, so individual ridges are legible
  _REVIEW_ridged_wrap_seam.jpg   the four-way corner, magnified
"""

import json
import os

import numpy as np
from PIL import Image

PRODUCT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(PRODUCT_DIR, "textures")


def out_path(*parts):
    p = os.path.abspath(os.path.join(PRODUCT_DIR, *parts))
    if os.path.commonpath([p, PRODUCT_DIR]) != PRODUCT_DIR:
        raise RuntimeError("refusing to write outside the product dir: %s" % p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def shade(color, height_mm, mm_per_px, elev_deg=15.0, azim_deg=0.0, ambient=0.32):
    gy, gx = np.gradient(height_mm, mm_per_px)
    n = np.dstack([-gx, -gy, np.ones_like(gx)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    e, a = np.deg2rad(elev_deg), np.deg2rad(azim_deg)
    L = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    lam = np.clip((n * L).sum(axis=2), 0.0, 1.0)
    lit = ambient + (1.0 - ambient) * lam
    return np.clip(color.astype(np.float64) * lit[..., None] * 1.5, 0, 255).astype(np.uint8)


def main():
    rep = json.load(open(os.path.join(TEX, "ridged_build_report.json")))
    W, H = rep["pixels"]
    W_IN, H_IN = rep["physical_in"]
    mm_per_px = W_IN * 25.4 / W

    color = np.asarray(Image.open(os.path.join(TEX, "Color.png")).convert("RGB"))
    bump = np.asarray(Image.open(os.path.join(TEX, "Bump_FinelyRidged16.png")))
    height = bump.astype(np.float64) / 65535.0 * rep["relief_mm"]["total_range"]
    print("colour %s, ridged bump %s  mm/px=%.5f  height range %.3f-%.3f mm"
          % (color.shape, bump.shape, mm_per_px, height.min(), height.max()))

    # light perpendicular to the ridges (azim 90 = along +y; ridges run horizontally,
    # parallel to the veining, i.e. constant along x, periodic along y) so the relief
    # reads at its strongest
    lit = shade(color, height, mm_per_px, elev_deg=15.0, azim_deg=90.0)

    two_c = np.tile(color, (2, 2, 1))
    two_l = np.tile(lit, (2, 2, 1))
    both = np.concatenate([two_c, np.full((two_c.shape[0], 16, 3), 255, np.uint8), two_l], axis=1)
    Image.fromarray(both).resize(
        (1800, int(1800 * both.shape[0] / both.shape[1])), Image.LANCZOS
    ).save(out_path("textures", "_PREVIEW_ridged_tiling.jpg"), quality=92)

    Image.fromarray(lit).resize((1600, int(1600 * H / W)), Image.LANCZOS).save(
        out_path("textures", "_PREVIEW_ridged_grazing.jpg"), quality=92)

    # close-up: about 6 inches tall, centred, so individual 2 mm ridges are legible
    # across the height (the axis they're periodic in)
    ch = int(6.0 / H_IN * H)
    cw = int(ch * 1.8)
    cx, cy = W // 2, H // 2
    crop_c = color[cy - ch // 2:cy + ch // 2, cx - cw // 2:cx + cw // 2]
    crop_h = height[cy - ch // 2:cy + ch // 2, cx - cw // 2:cx + cw // 2]
    crop_lit = shade(crop_c, crop_h, mm_per_px, elev_deg=10.0, azim_deg=90.0)
    strip = np.concatenate([crop_c, np.full((crop_c.shape[0], 12, 3), 255, np.uint8), crop_lit], axis=1)
    Image.fromarray(strip).save(out_path("textures", "_PREVIEW_ridged_closeup.jpg"), quality=94)
    print("close-up: %d x %d px = %.2f x %.2f in, ~%.0f ridges across the height"
          % (cw, ch, cw / H * H_IN, ch / H * H_IN, ch / H * H_IN * 25.4 / rep["ridge_pitch_mm"]))

    k = 420
    def four_way(a):
        top = np.concatenate([a[-k:, -k:], a[-k:, :k]], axis=1)
        bot = np.concatenate([a[:k, -k:], a[:k, :k]], axis=1)
        return np.concatenate([top, bot], axis=0)

    corner_c = four_way(color)
    corner_h = four_way(height)
    corner_lit = shade(corner_c, corner_h, mm_per_px, elev_deg=10.0, azim_deg=90.0)
    both_c = np.concatenate([corner_c, np.full((corner_c.shape[0], 12, 3), 255, np.uint8), corner_lit], axis=1)
    Image.fromarray(both_c).save(out_path("textures", "_REVIEW_ridged_wrap_seam.jpg"), quality=94)

    print("wrote 4 preview/review images into textures/")


if __name__ == "__main__":
    main()
