"""Step 07: joint colour / width and overall Sand tone, from the render (orthographic) and
the lifestyle image (tone cross-check only).

Across-joint profile: for every lattice hexagon of the render, the signed distance d to the
module boundary (d = 0 on the joint centreline, positive towards the face centre) is
computed for every pixel; RGB is averaged in bins of d. Pixels near hexagon corners
(junctions) are excluded."""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, LIFESTYLE_PATH, save_text, out_path  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402
from s03_faces import hex_dist_inside  # noqa: E402

PX_PER_IN = 31.0916


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    rgb = load_srgb(RENDER_PATH)
    H, W = rgb.shape[:2]
    F, R, cp = grid["F_px"], grid["R_px"], grid["col_pitch_px"]
    nb = 64
    edges = np.linspace(-1.0, 15.0, nb + 1)      # d bins, 0.25 px
    acc = np.zeros((nb, 3))
    cnt = np.zeros(nb)
    ang = np.deg2rad(np.arange(6) * 60.0)
    for i in range(-1, 8):
        cx = grid["x0"] + i * cp
        for j in range(-1, 8):
            cy = grid["y0"] + ((F / 2.0) if (i % 2) else 0.0) + j * F
            x0, x1 = int(np.floor(cx - R)), int(np.ceil(cx + R))
            y0, y1 = int(np.floor(cy - F / 2)), int(np.ceil(cy + F / 2))
            if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
                continue
            ys, xs = np.mgrid[y0:y1, x0:x1]
            dx, dy = xs - cx, ys - cy
            d = hex_dist_inside(dx, dy, F)
            near_corner = np.zeros(d.shape, bool)
            for a in ang:
                near_corner |= np.hypot(dx - R * np.cos(a), dy - R * np.sin(a)) < 22.0
            ok = (d > -1.0) & (d < 15.0) & (~near_corner)
            idx = np.clip(((d[ok] - edges[0]) / (edges[1] - edges[0])).astype(int), 0, nb - 1)
            px = rgb[y0:y1, x0:x1][ok]
            for c in range(3):
                acc[:, c] += np.bincount(idx, weights=px[:, c], minlength=nb)
            cnt += np.bincount(idx, minlength=nb)
    prof = acc / np.maximum(cnt, 1)[:, None]
    ctr = 0.5 * (edges[:-1] + edges[1:])
    face_level = prof[ctr > 8.0].mean(0)
    print("d(px)    R      G      B     lum    n")
    for k in range(0, nb, 2):
        if ctr[k] < -0.5 or ctr[k] > 10:
            continue
        lum = prof[k] @ np.array([0.2126, 0.7152, 0.0722])
        print("%5.2f  %6.1f %6.1f %6.1f  %6.1f  %d" % (ctr[k], *prof[k], lum, cnt[k]))
    print("face level (d>8):", np.round(face_level, 2))
    lum_p = prof @ np.array([0.2126, 0.7152, 0.0722])
    lum_face = face_level @ np.array([0.2126, 0.7152, 0.0722])
    kmin = int(np.argmin(np.where((ctr > -0.5) & (ctr < 6), lum_p, 1e9)))
    kmax = int(np.argmax(np.where((ctr > -0.5) & (ctr < 6), lum_p, -1e9)))
    print("darkest bin d=%.2f lum %.1f ; brightest bin d=%.2f lum %.1f ; face lum %.1f"
          % (ctr[kmin], lum_p[kmin], ctr[kmax], lum_p[kmax], lum_face))
    res = {"d_centres": [float(x) for x in ctr], "profile_rgb": prof.tolist(), "count": cnt.tolist(),
           "face_level_rgb": [float(x) for x in face_level]}
    save_text(json.dumps(res), "work", "joint_profile.json")

    # tone by face type on the interior of the complete faces (render)
    fs = json.load(open(out_path("work", "render_faces_raw.json")))
    types = {"matte": [], "raw": [], "chiseled": []}
    for f in fs:
        if f["frac_visible"] < 0.999:
            continue
        t = "chiseled" if f["coherence"] > 0.6 else ("raw" if f["coherence"] > 0.2 else "matte")
        types[t].append(f["mean_rgb"])
    for t, v in types.items():
        v = np.array(v)
        print("%-9s n=%2d mean RGB %s  (face-to-face std %s)" % (t, len(v), np.round(v.mean(0), 2), np.round(v.std(0), 2)))
    allrgb = np.array(sum(types.values(), []))
    print("all complete faces mean RGB", np.round(allrgb.mean(0), 2))

    # lifestyle tone, sunlit flat Matte faces (boxes chosen on plain Matte hexagons)
    lif = load_srgb(LIFESTYLE_PATH)
    boxes = {"matte_top": (330, 30, 120, 160), "matte_mid": (420, 420, 100, 120),
             "matte_lo": (720, 1030, 150, 100)}
    for n, (x0, y0, w, h) in boxes.items():
        v = lif[y0:y0 + h, x0:x0 + w].reshape(-1, 3)
        print("lifestyle %-10s mean %s std %s" % (n, np.round(v.mean(0), 1), np.round(v.std(0), 1)))


if __name__ == "__main__":
    main()
