"""Phase 8, step 8.8: difference between the real-time picture and the path-traced ground truth of a view.

    python -B compare_tiers.py <ground truth folder> <real-time folder> <output folder> [real-time suffix]

Reads <view>_pathtraced.0000.png and <view>_realtime<suffix>.0000.png (both 3840 by 2160, written by
tools/wieland_truth.py with the same camera and the same fixed exposure) and writes, per view, a sheet
(ground truth, real-time, difference map) and one row of numbers; all rows go to compare<suffix>.json and
compare<suffix>.csv in the output folder.

What is measured, and its limits:

- Brightness is the luminance of the finished picture with its sRGB curve undone. The pictures are
  tone-mapped (the renderer's film curve is in them), so a "stop" here is a factor of two in picture
  luminance. In the middle tones that equals a stop of scene light; near white the film curve flattens, so
  differences there are understated.
- "Facade and ground" is every pixel that is not sky and not burnt out in both pictures. Sky is taken from the
  ground truth: blue clearly above red and not dark. Pixels at 250 of 255 or more in both pictures (cloud
  tops, windows seen from inside at the interior exposure) carry no information and are left out as well.
  Trees stay in.
- Mean brightness difference: (mean real-time - mean ground truth) / mean ground truth over those pixels.
- Regions: the frame is cut into 40 by 40 pixel blocks (96 by 54 blocks). A block is off when the two block
  means differ by more than one stop; 0.003 is added to both first, so that noise in near-black blocks does
  not count. Off blocks of the same sign that touch along an edge form a region. A region larger than 2
  percent of the frame fails; each is listed with its place in the frame.
"""
import csv
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

VIEWS = ("S1", "S2", "S3", "S4", "S5", "S6", "S9", "D1", "D2", "D3", "D4", "D5")
BLOCK = 40
FLOOR = 0.003
REGION_LIMIT = 0.02
MEAN_LIMIT = 0.10


def linear(srgb):
    c = srgb.astype(np.float32) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def luminance(rgb):
    lin = linear(rgb)
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def regions(off, sign):
    """Connected groups of off blocks with the same sign; returns a list of lists of (row, column)."""
    rows, cols = off.shape
    seen = np.zeros(off.shape, dtype=bool)
    found = []
    for r in range(rows):
        for c in range(cols):
            if not off[r, c] or seen[r, c]:
                continue
            want = sign[r, c]
            stack = [(r, c)]
            seen[r, c] = True
            group = []
            while stack:
                y, x = stack.pop()
                group.append((y, x))
                for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                    if 0 <= ny < rows and 0 <= nx < cols and off[ny, nx] and not seen[ny, nx] and sign[ny, nx] == want:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            found.append(group)
    return found


def place(group, rows, cols):
    ys = [g[0] for g in group]
    xs = [g[1] for g in group]
    cy = (sum(ys) / len(ys) + 0.5) / rows
    cx = (sum(xs) / len(xs) + 0.5) / cols
    vertical = "top" if cy < 1 / 3 else ("middle" if cy < 2 / 3 else "bottom")
    horizontal = "left" if cx < 1 / 3 else ("centre" if cx < 2 / 3 else "right")
    return "%s %s" % (vertical, horizontal), [min(xs) * BLOCK, min(ys) * BLOCK, (max(xs) + 1) * BLOCK, (max(ys) + 1) * BLOCK]


def compare(view, truth_folder, real_folder, out_folder, suffix):
    truth_path = os.path.join(truth_folder, "%s_pathtraced.0000.png" % view)
    real_path = os.path.join(real_folder, "%s_realtime%s.0000.png" % (view, suffix))
    if not (os.path.exists(truth_path) and os.path.exists(real_path)):
        return {"view": view, "missing": [p for p in (truth_path, real_path) if not os.path.exists(p)]}
    truth_image = Image.open(truth_path).convert("RGB")
    real_image = Image.open(real_path).convert("RGB")
    if truth_image.size != real_image.size:
        return {"view": view, "error": "sizes differ: %s and %s" % (truth_image.size, real_image.size)}
    truth = np.asarray(truth_image)
    real = np.asarray(real_image)
    height, width = truth.shape[:2]
    lum_truth = luminance(truth)
    lum_real = luminance(real)

    t = truth.astype(np.float32)
    sky = (t[..., 2] > t[..., 0] * 1.15) & (t[..., 2] > 90)
    burnt = (truth.min(axis=2) >= 250) & (real.min(axis=2) >= 250)
    mask = ~(sky | burnt)
    mean_truth = float(lum_truth[mask].mean())
    mean_real = float(lum_real[mask].mean())
    mean_difference = (mean_real - mean_truth) / mean_truth

    rows, cols = height // BLOCK, width // BLOCK
    def blocks(a):
        return a[:rows * BLOCK, :cols * BLOCK].reshape(rows, BLOCK, cols, BLOCK).mean(axis=(1, 3))
    block_truth = blocks(lum_truth)
    block_real = blocks(lum_real)
    block_used = blocks(mask.astype(np.float32)) >= 0.5
    stops = np.log2((block_real + FLOOR) / (block_truth + FLOOR))
    off = (np.abs(stops) > 1.0) & block_used
    sign = np.sign(stops)
    failing = []
    largest = 0.0
    for group in regions(off, sign):
        share = len(group) / float(rows * cols)
        largest = max(largest, share)
        if share > REGION_LIMIT:
            where, box = place(group, rows, cols)
            values = [stops[y, x] for y, x in group]
            failing.append({"share_of_frame_percent": round(share * 100, 2), "where": where, "box_pixels": box,
                            "real_time_is": "brighter" if values[0] > 0 else "darker",
                            "mean_stops": round(float(np.mean(values)), 2)})
    failing.sort(key=lambda f: -f["share_of_frame_percent"])

    # Sheet: ground truth, real-time, difference map (red: real-time brighter, blue: darker; full colour at 2 stops).
    panel = (1280, 720)
    scale = panel[0] / float(width)
    clipped = np.clip(stops / 2.0, -1.0, 1.0)
    grey = np.full(clipped.shape, 235.0)
    red = np.where(clipped > 0, 235.0, 235.0 * (1 + clipped))
    blue = np.where(clipped < 0, 235.0, 235.0 * (1 - clipped))
    green = grey * (1 - np.abs(clipped))
    diff = np.stack([red, green, blue], axis=2)
    diff[~block_used] = (120, 120, 120)
    diff_image = Image.fromarray(diff.astype(np.uint8)).resize(panel, Image.NEAREST)
    draw = ImageDraw.Draw(diff_image)
    for f in failing:
        x0, y0, x1, y1 = [v * scale for v in f["box_pixels"]]
        draw.rectangle([x0, y0, x1 - 1, y1 - 1], outline=(0, 0, 0), width=3)
    sheet = Image.new("RGB", (panel[0] * 3, panel[1] + 44), (255, 255, 255))
    sheet.paste(truth_image.resize(panel, Image.LANCZOS), (0, 44))
    sheet.paste(real_image.resize(panel, Image.LANCZOS), (panel[0], 44))
    sheet.paste(diff_image, (panel[0] * 2, 44))
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 14), "%s  ground truth (path traced)" % view, fill=(0, 0, 0))
    draw.text((panel[0] + 12, 14), "%s  real-time%s   mean brightness difference %+.1f %%" % (
        view, (" " + suffix.strip("_")) if suffix else "", mean_difference * 100), fill=(0, 0, 0))
    draw.text((panel[0] * 2 + 12, 14), "difference: red = real-time brighter, blue = darker, full colour at 2 stops; "
              "grey = sky or burnt out; boxes = failing regions", fill=(0, 0, 0))
    os.makedirs(out_folder, exist_ok=True)
    sheet_path = os.path.join(out_folder, "%s_sheet%s.jpg" % (view, suffix))
    sheet.save(sheet_path, quality=88)

    return {"view": view,
            "mean_truth": round(mean_truth, 4), "mean_real_time": round(mean_real, 4),
            "mean_difference_percent": round(mean_difference * 100, 1),
            "mean_within_10_percent": abs(mean_difference) <= MEAN_LIMIT,
            "pixels_used_percent": round(float(mask.mean()) * 100, 1),
            "blocks_off_by_over_one_stop_percent": round(float(off.sum()) / (rows * cols) * 100, 2),
            "largest_region_percent": round(largest * 100, 2),
            "regions_over_2_percent": failing,
            "passes": abs(mean_difference) <= MEAN_LIMIT and not failing,
            "sheet": sheet_path.replace("\\", "/")}


def main():
    truth_folder, real_folder, out_folder = sys.argv[1:4]
    suffix = sys.argv[4] if len(sys.argv) > 4 else ""
    results = [compare(view, truth_folder, real_folder, out_folder, suffix) for view in VIEWS]
    os.makedirs(out_folder, exist_ok=True)
    with open(os.path.join(out_folder, "compare%s.json" % suffix), "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=1)
    with open(os.path.join(out_folder, "compare%s.csv" % suffix), "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["view", "mean_difference_percent", "mean_within_10_percent", "pixels_used_percent",
                         "blocks_off_by_over_one_stop_percent", "largest_region_percent", "regions_over_2_percent",
                         "passes", "failing_regions"])
        for r in results:
            if "mean_difference_percent" not in r:
                writer.writerow([r["view"], "", "", "", "", "", "", "", json.dumps(r)])
                continue
            writer.writerow([r["view"], r["mean_difference_percent"], r["mean_within_10_percent"], r["pixels_used_percent"],
                             r["blocks_off_by_over_one_stop_percent"], r["largest_region_percent"],
                             len(r["regions_over_2_percent"]), r["passes"],
                             "; ".join("%s %s %.1f%% of frame %+.2f stops" % (
                                 f["where"], f["real_time_is"], f["share_of_frame_percent"], f["mean_stops"])
                                 for f in r["regions_over_2_percent"])])
    for r in results:
        print(json.dumps({k: v for k, v in r.items() if k != "sheet"}))


if __name__ == "__main__":
    main()
