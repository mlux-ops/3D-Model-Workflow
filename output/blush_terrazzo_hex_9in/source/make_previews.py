"""Review images for the blush terrazzo hexagon texture, per the WORKFLOW.md visual
acceptance gate: wrap preview, correctly scaled surface, grazing light, four-way corner.

Writes into textures/:
  _PREVIEW_atlas_full.jpg      the whole 12-hexagon atlas
  _PREVIEW_tiling_2x2.jpg      2x2 repeat (48 virtual hexagons)
  _PREVIEW_grazing_light.jpg   the atlas lit from a low angle
  _REVIEW_wrap_seam.jpg        the four-way corner, magnified
  _PREVIEW_wall_scale.jpg      a large wall-scale repeat, for room-distance inspection
"""

import json
import os

import numpy as np
from PIL import Image

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(RUN_DIR, "textures")


def out_path(*parts):
    p = os.path.abspath(os.path.join(RUN_DIR, *parts))
    if os.path.commonpath([p, RUN_DIR]) != RUN_DIR:
        raise RuntimeError("refusing to write outside the run dir: %s" % p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def shade(color, height_mm, mm_per_px, elev_deg=15.0, azim_deg=135.0, ambient=0.35):
    gy, gx = np.gradient(height_mm, mm_per_px)
    n = np.dstack([-gx, -gy, np.ones_like(gx)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    e = np.deg2rad(elev_deg)
    a = np.deg2rad(azim_deg)
    L = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    lam = np.clip((n * L).sum(axis=2), 0.0, 1.0)
    lit = ambient + (1.0 - ambient) * lam
    return np.clip(color.astype(np.float64) * lit[..., None] * 1.4, 0, 255).astype(np.uint8)


def main():
    rep = json.load(open(os.path.join(TEX, "build_report.json")))
    W, H = rep["image_px"]
    mm_per_px = rep["sample_size_in"][0] * 25.4 / W
    total_mm = rep["relief_mm"]["total_range"]

    color = np.asarray(Image.open(os.path.join(TEX, "BlushTerrazzo_Hex9_Color.png")))
    bump = np.asarray(Image.open(os.path.join(TEX, "BlushTerrazzo_Hex9_Bump16.png")))
    height = bump.astype(np.float64) / 65535.0 * total_mm
    print("colour %s, bump %s  (%.4f mm/px)  height range %.3f-%.3f mm"
          % (color.shape, bump.shape, mm_per_px, height.min(), height.max()))

    Image.fromarray(color).resize((1400, int(1400 * H / W)), Image.LANCZOS).save(
        out_path("textures", "_PREVIEW_atlas_full.jpg"), quality=92)

    two = np.tile(color, (2, 2, 1))
    Image.fromarray(two).resize((1600, int(1600 * two.shape[0] / two.shape[1])),
                                Image.LANCZOS).save(
        out_path("textures", "_PREVIEW_tiling_2x2.jpg"), quality=90)

    lit = shade(color, height, mm_per_px)
    Image.fromarray(lit).resize((1400, int(1400 * H / W)), Image.LANCZOS).save(
        out_path("textures", "_PREVIEW_grazing_light.jpg"), quality=92)

    k = 380
    def four_way(a):
        top = np.concatenate([a[-k:, -k:], a[-k:, :k]], axis=1)
        bot = np.concatenate([a[:k, -k:], a[:k, :k]], axis=1)
        return np.concatenate([top, bot], axis=0)
    corner_c = four_way(color)
    corner_h = four_way(height)
    corner_lit = shade(corner_c, corner_h, mm_per_px, elev_deg=10.0)
    both = np.concatenate([corner_c, np.full((corner_c.shape[0], 12, 3), 255, np.uint8), corner_lit], axis=1)
    Image.fromarray(both).save(out_path("textures", "_REVIEW_wrap_seam.jpg"), quality=94)

    # wall-scale: 8 ft x 6 ft
    wall_w_in, wall_h_in = 96.0, 72.0
    scale = 1400.0 / wall_w_in
    small = Image.fromarray(color).resize(
        (max(1, int(rep["sample_size_in"][0] * scale)),
         max(1, int(rep["sample_size_in"][1] * scale))), Image.LANCZOS)
    wall = Image.new("RGB", (int(wall_w_in * scale), int(wall_h_in * scale)))
    for x in range(0, wall.width, small.width):
        for y in range(0, wall.height, small.height):
            wall.paste(small, (x, y))
    wall.save(out_path("textures", "_PREVIEW_wall_scale.jpg"), quality=90)
    print("wall preview: %.0f x %.0f in, %.1f x %.1f atlas repeats"
          % (wall_w_in, wall_h_in, wall_w_in / rep["sample_size_in"][0],
             wall_h_in / rep["sample_size_in"][1]))

    a = color.astype(np.int64)
    print("colour L/R wrap step %.3f  T/B wrap step %.3f  typical neighbour step %.3f"
          % (np.abs(a[:, 0] - a[:, -1]).mean(), np.abs(a[0, :] - a[-1, :]).mean(),
             np.abs(a[:, 10].astype(np.int64) - a[:, 11].astype(np.int64)).mean()))
    bh = height
    print("bump L/R wrap step %.4f  T/B wrap step %.4f  typical neighbour step %.4f"
          % (np.abs(bh[:, 0] - bh[:, -1]).mean(), np.abs(bh[0, :] - bh[-1, :]).mean(),
             np.abs(bh[:, 10] - bh[:, 11]).mean()))
    print("wrote 5 preview/review images into textures/")


if __name__ == "__main__":
    main()
