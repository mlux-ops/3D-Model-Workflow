"""Render the review images for the hexagon texture, and check the maps numerically.

Writes into textures/:
  _PREVIEW_tiling_hex10.jpg        2 x 2 wrap of the colour map, for seam inspection
  _PREVIEW_grazing_light_hex10.jpg the atlas lit from 15 degrees, where relief either
                                   reads or does not
  _PREVIEW_face_closeup_hex10.jpg  one plain, one stipple and one comb face, grazing
  _PREVIEW_wall_scale_hex10.jpg    a 12 ft x 9 ft wall at true scale, for repetition
  _REVIEW_wrap_seam_hex10.jpg      the four-way corner, magnified
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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


def shade(color, height_mm, mm_per_px, elev_deg=15.0, azim_deg=135.0, ambient=0.30):
    """Lambert shading of the height field, applied to the colour map."""
    gy, gx = np.gradient(height_mm, mm_per_px)
    n = np.dstack([-gx, -gy, np.ones_like(gx)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    e = np.deg2rad(elev_deg)
    a = np.deg2rad(azim_deg)
    L = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    lam = np.clip((n * L).sum(axis=2), 0.0, 1.0)
    lit = ambient + (1.0 - ambient) * lam
    out = color.astype(np.float64) * lit[..., None] * 1.55
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    rep = json.load(open(os.path.join(TEX, "build_report.json")))
    W, H = rep["image_px"]
    ppi = rep["ppi"]
    mm_per_px = rep["sample_size_in"][0] * 25.4 / W
    total_mm = rep["relief_mm"]["total_range"]

    color = np.asarray(Image.open(os.path.join(TEX, "Hex10_Dimensional_Color.png")))
    bump = np.asarray(Image.open(os.path.join(TEX, "Hex10_Dimensional_Bump16.png")))
    height = bump.astype(np.float64) / 65535.0 * total_mm
    print("colour %s %s, bump %s %s  (%.4f mm/px)"
          % (color.shape, color.dtype, bump.shape, bump.dtype, mm_per_px))
    print("bump range %.3f - %.3f mm" % (height.min(), height.max()))

    # 1. tiling wrap
    two = np.tile(color, (2, 2, 1))
    Image.fromarray(two).resize((1600, int(1600 * two.shape[0] / two.shape[1])),
                                Image.LANCZOS).save(
        out_path("textures", "_PREVIEW_tiling_hex10.jpg"), quality=92)

    # 2. grazing light over the whole atlas
    lit = shade(color, height, mm_per_px)
    Image.fromarray(lit).resize((1500, int(1500 * H / W)), Image.LANCZOS).save(
        out_path("textures", "_PREVIEW_grazing_light_hex10.jpg"), quality=92)

    # 3. face close-ups: three hexagon centres, one of each type
    cpx = W / rep["atlas_hexagons"][0]
    rpx = H / rep["atlas_hexagons"][1]
    half = int(rpx * 0.46)
    picks = []
    for i in range(rep["atlas_hexagons"][0]):
        for j in range(rep["atlas_hexagons"][1]):
            cx = int(i * cpx + (0 if i % 2 == 0 else 0))
            cy = int(j * rpx + (rpx * 0.5 if i % 2 else 0))
            if cx - half < 0 or cx + half >= W or cy - half < 0 or cy + half >= H:
                continue
            picks.append((cx, cy))
    # pick three that look most different: lowest, middle and highest face roughness
    rough = []
    for cx, cy in picks:
        h = height[cy - half:cy + half, cx - half:cx + half]
        rough.append((float(h[h > 1.0].std()), cx, cy))
    rough.sort()
    chosen = [rough[0], rough[len(rough) // 2], rough[-1]]
    cells = []
    for _, cx, cy in chosen:
        c = color[cy - half:cy + half, cx - half:cx + half]
        h = height[cy - half:cy + half, cx - half:cx + half]
        cells.append(shade(c, h, mm_per_px, elev_deg=12.0))
    strip = np.concatenate([np.pad(c, ((0, 0), (0, 12), (0, 0)), constant_values=255)
                            for c in cells], axis=1)
    Image.fromarray(strip).save(out_path("textures", "_PREVIEW_face_closeup_hex10.jpg"),
                                quality=94)
    print("close-up face relief std (mm): %s"
          % [round(r[0], 4) for r in chosen])

    # 4. wall at true scale, 12 ft x 9 ft
    wall_w_in, wall_h_in = 240.0, 144.0      # 20 ft x 12 ft
    scale = 1400.0 / wall_w_in                 # preview px per inch
    small = Image.fromarray(lit).resize(
        (max(1, int(rep["sample_size_in"][0] * scale)),
         max(1, int(rep["sample_size_in"][1] * scale))), Image.LANCZOS)
    wall = Image.new("RGB", (int(wall_w_in * scale), int(wall_h_in * scale)))
    for x in range(0, wall.width, small.width):
        for y in range(0, wall.height, small.height):
            wall.paste(small, (x, y))
    wall.save(out_path("textures", "_PREVIEW_wall_scale_hex10.jpg"), quality=90)
    print("wall preview: %.0f x %.0f in, %.1f x %.1f atlas repeats"
          % (wall_w_in, wall_h_in, wall_w_in / rep["sample_size_in"][0],
             wall_h_in / rep["sample_size_in"][1]))

    # 5. four-way corner, magnified: the wrap seam if there is one
    k = 420
    def four_way(a):
        top = np.concatenate([a[-k:, -k:], a[-k:, :k]], axis=1)
        bot = np.concatenate([a[:k, -k:], a[:k, :k]], axis=1)
        return np.concatenate([top, bot], axis=0)

    corner = four_way(color)
    hcorner = four_way(height)
    lit_c = shade(corner, hcorner, mm_per_px, elev_deg=12.0)
    both = np.concatenate([np.pad(corner, ((0, 0), (0, 12), (0, 0)), constant_values=255),
                           lit_c], axis=1)
    Image.fromarray(both).save(out_path("textures", "_REVIEW_wrap_seam_hex10.jpg"),
                               quality=94)

    # numeric seam check: the map must wrap without a step
    for lbl, a, b in [("colour left/right", color[:, 0].astype(float), color[:, -1].astype(float)),
                      ("colour top/bottom", color[0].astype(float), color[-1].astype(float)),
                      ("bump left/right", height[:, 0], height[:, -1]),
                      ("bump top/bottom", height[0], height[-1])]:
        # compare the wrap step against the step between two adjacent interior columns
        if a.ndim == 2:
            inner = np.abs(color[:, 10].astype(float) - color[:, 11].astype(float)).mean()
        else:
            inner = np.abs(height[:, 10] - height[:, 11]).mean()
        print("%-20s wrap step %.4f   typical neighbour step %.4f"
              % (lbl, np.abs(a - b).mean(), inner))
    print("wrote 5 preview/review images into textures/")


if __name__ == "__main__":
    main()
