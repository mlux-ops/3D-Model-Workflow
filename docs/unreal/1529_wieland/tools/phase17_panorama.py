"""Phase 17: the labelled skyline panorama sheet from the roof deck.

Usage:
    python -B -P phase17_panorama.py <frames json> <out png> [min height m 90]

<frames json>: {"loc": [x, y, z] level cm, "fov": horizontal degrees, "frames": [{"yaw": deg, "pitch": deg,
"image": png}, ...]} in order from left (east) to right (west). Each frame is pasted side by side (no blending),
and every skyline tower (beyond 1 km and at least <min height> m to its top, from towers_record.jsonl) whose top
falls in a frame is marked at its top with its name (tower_materials.csv) and its modelled height above ground.
The top is the highest vertex of the tower's mesh (masts included), lowered by the curvature drop as in the level.
A strip under each frame gives its yaw and pitch.
"""

import csv
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MESH = "E:/Wieland1529_site_data/phase17/meshes_towers"
MATS = "E:/Wieland1529_site_data/phase17/tower_materials.csv"


def tops(min_h):
    names = {r["bldg_id"]: r["name"] for r in csv.DictReader(open(MATS, encoding="utf-8"))}
    out = []
    for line in open(os.path.join(MESH, "towers_record.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        if r["distance_m"] < 1000 or r["top_incl_masts_m"] < min_h:
            continue
        d = json.load(open(os.path.join(MESH, r["name"] + ".json"), encoding="utf-8"))
        v = np.asarray(d["vertices"], dtype=np.float64)
        k = int(np.argmax(v[:, 2]))
        p = v[k] + np.asarray(d["pivot"])
        out.append({"id": r["id"], "name": names.get(r["id"]) or r["id"], "top_m": r["top_incl_masts_m"], "p": p})
    return out


def project(loc, yaw, pitch, fov, W, H, p):
    d = np.asarray(p) - np.asarray(loc)
    pr, yr = math.radians(pitch), math.radians(yaw)
    fwd = np.array([math.cos(pr) * math.cos(yr), math.cos(pr) * math.sin(yr), math.sin(pr)])
    right = np.array([-math.sin(yr), math.cos(yr), 0.0])
    up = np.array([-math.sin(pr) * math.cos(yr), -math.sin(pr) * math.sin(yr), math.cos(pr)])
    z = d @ fwd
    if z <= 0:
        return None
    f = (W / 2.0) / math.tan(math.radians(fov) / 2.0)
    return W / 2.0 + (d @ right) / z * f, H / 2.0 - (d @ up) / z * f


def main(argv):
    job = json.load(open(argv[1]))
    out = argv[2]
    min_h = float(argv[3]) if len(argv) > 3 else 90.0
    towers = tops(min_h)
    frames = [Image.open(f["image"]).convert("RGB") for f in job["frames"]]
    W, H = frames[0].size
    strip = 60
    sheet = Image.new("RGB", (W * len(frames), H + strip), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", max(14, W // 110))
    except OSError:
        font = ImageFont.load_default()
    placed = []
    for i, (f, im) in enumerate(zip(job["frames"], frames)):
        sheet.paste(im, (i * W, 0))
        draw.text((i * W + 10, H + 10), "yaw %.1f deg, pitch %.1f deg, horizontal field %.1f deg" % (f["yaw"], f["pitch"], job["fov"]),
                  fill=(0, 0, 0), font=font)
        hits = []
        for t in towers:
            uv = project(job["loc"], f["yaw"], f["pitch"], job["fov"], W, H, t["p"])
            if uv is None or not (0 <= uv[0] < W and 0 <= uv[1] < H):
                continue
            hits.append((uv, t))
        hits.sort(key=lambda h: h[0][0])
        lane_end = {}
        for (u, v), t in hits:
            x, y = i * W + u, v
            draw.line([(x, y), (x, y - 14)], fill=(255, 220, 0), width=2)
            label = "%s %.0f m" % (t["name"][:28], t["top_m"])
            tw = draw.textlength(label, font=font)
            lane = 0
            while lane_end.get(lane, -1e9) > x - 4:
                lane += 1
            lane_end[lane] = x + tw
            ty = max(4, y - 34 - lane * (font.size + 6))
            draw.line([(x, y - 14), (x, ty + font.size)], fill=(255, 220, 0), width=1)
            draw.rectangle([x - 2, ty - 2, x + tw + 2, ty + font.size + 2], fill=(0, 0, 0))
            draw.text((x, ty), label, fill=(255, 255, 255), font=font)
            placed.append({"frame": i, "id": t["id"], "name": t["name"], "top_m": t["top_m"], "u": round(u, 1), "v": round(v, 1)})
    sheet.save(out)
    with open(os.path.splitext(out)[0] + "_labels.json", "w", encoding="utf-8") as h:
        json.dump(placed, h, indent=1)
    print("towers labelled", len(placed), "of", len(towers))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
