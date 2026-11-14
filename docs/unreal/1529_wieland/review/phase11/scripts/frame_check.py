"""Phase 11, step 11.2: check a move's frames. For each pair of neighbours, the mean absolute difference of the two
pictures (0-255, on a 480 by 270 copy) and a sharpness figure (variance of the Laplacian) of each frame.
Reports missing frames, identical neighbours (difference 0) and the largest jumps.
    python -B review/phase11/scripts/frame_check.py <folder> <name> [first] [last] [--json out.json]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

folder, name = sys.argv[1], sys.argv[2]
first = int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else 0
last = int(sys.argv[4]) if len(sys.argv) > 4 and not sys.argv[4].startswith("--") else 899
out_json = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None


def load(frame):
    path = os.path.join(folder, "%s.%04d.png" % (name, frame))
    if not os.path.exists(path):
        return None
    with Image.open(path) as image:
        small = image.convert("L").resize((480, 270), Image.BILINEAR)
    return np.asarray(small, dtype=np.float32)


def sharp(a):
    lap = a[1:-1, 1:-1] * 4 - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:]
    return float(lap.var())


rows, missing, previous = [], [], None
for frame in range(first, last + 1):
    a = load(frame)
    if a is None:
        missing.append(frame)
        previous = None
        continue
    diff = float(np.abs(a - previous).mean()) if previous is not None else None
    rows.append({"frame": frame, "diff_prev": diff, "sharp": sharp(a), "mean": float(a.mean())})
    previous = a
diffs = [r for r in rows if r["diff_prev"] is not None]
identical = [r["frame"] for r in diffs if r["diff_prev"] == 0.0]
top = sorted(diffs, key=lambda r: -r["diff_prev"])[:8]
summary = {"folder": folder, "name": name, "range": [first, last], "frames_found": len(rows), "missing": missing,
           "identical_to_previous": identical,
           "diff_median": float(np.median([r["diff_prev"] for r in diffs])) if diffs else None,
           "largest_jumps": [(r["frame"], round(r["diff_prev"], 2)) for r in top]}
if out_json:
    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump({"summary": summary, "rows": rows}, handle, indent=1)
print(json.dumps(summary))
for r in rows:
    if r["frame"] in (148, 149, 150, 151, 152, 298, 299, 300, 301, 448, 449, 450, 451, 598, 599, 600, 601, 748, 749, 750, 751) or "--all" in sys.argv:
        print(r["frame"], None if r["diff_prev"] is None else round(r["diff_prev"], 2), round(r["sharp"], 1), round(r["mean"], 1))
