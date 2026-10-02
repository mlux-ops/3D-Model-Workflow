"""Step 03: face inventory of the layout render.

Uses the lattice from step 02. For every hexagon whose module lies completely inside
the render, compute texture features on the face interior (inset from the joint) and
save the face crops. Also builds a labelled contact sheet for visual classification.
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, save_image, save_text, save_npy, out_path  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402

LUMW = np.array([0.2126, 0.7152, 0.0722])


def hex_dist_inside(dx, dy, F):
    """Signed distance (px) from the boundary of a flat-top hexagon of across-flats F
    (positive inside): F/2 - max over the three edge-normal projections."""
    c30, s30 = np.cos(np.deg2rad(30.0)), np.sin(np.deg2rad(30.0))
    u1 = np.abs(dy)
    u2 = np.abs(dx * c30 + dy * s30)
    u3 = np.abs(dx * c30 - dy * s30)
    return F / 2.0 - np.maximum(np.maximum(u1, u2), u3)


def lattice_centres(grid, W, H):
    F = grid["F_px"]
    R = grid["R_px"]
    cp = grid["col_pitch_px"]
    out = []
    for i in range(-3, 9):
        cx = grid["x0"] + i * cp
        yoff = (F / 2.0) if (i % 2) else 0.0
        for j in range(-2, 9):
            cy = grid["y0"] + yoff + j * F
            out.append({"i": i, "j": j, "cx": cx, "cy": cy})
    return out


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    rgb = load_srgb(RENDER_PATH)
    H, W = rgb.shape[:2]
    F, R = grid["F_px"], grid["R_px"]
    lum = rgb @ LUMW

    faces = []
    for c in lattice_centres(grid, W, H):
        cx, cy = c["cx"], c["cy"]
        # fraction of the module hexagon inside the image
        x0, x1 = int(np.floor(cx - R)), int(np.ceil(cx + R))
        y0, y1 = int(np.floor(cy - F / 2)), int(np.ceil(cy + F / 2))
        if x1 < 0 or y1 < 0 or x0 > W or y0 > H:
            continue
        ys, xs = np.mgrid[max(y0, 0):min(y1, H), max(x0, 0):min(x1, W)]
        inside = hex_dist_inside(xs - cx, ys - cy, F) > 0
        area_full = 0.866025 * F * F
        frac = inside.sum() / area_full
        full = (x0 >= 0 and y0 >= 0 and x1 <= W and y1 <= H)
        c["full"] = bool(full)
        c["frac_visible"] = float(frac)
        if frac < 0.30:
            continue
        faces.append(c)

    print("lattice hexes with >=30%% visible: %d (full: %d)"
          % (len(faces), sum(f["full"] for f in faces)))

    # features on face interior, inset 8 px from the joint centreline
    inset = 8.0
    feats = []
    sm3 = ndi.gaussian_filter(lum, 3.0)
    hp = lum - sm3
    gx = ndi.sobel(ndi.gaussian_filter(lum, 1.0), axis=1) / 8.0
    gy = ndi.sobel(ndi.gaussian_filter(lum, 1.0), axis=0) / 8.0
    for f in faces:
        cx, cy = f["cx"], f["cy"]
        x0, x1 = max(int(np.floor(cx - R)), 0), min(int(np.ceil(cx + R)), W)
        y0, y1 = max(int(np.floor(cy - F / 2)), 0), min(int(np.ceil(cy + F / 2)), H)
        ys, xs = np.mgrid[y0:y1, x0:x1]
        m = hex_dist_inside(xs - cx, ys - cy, F) > inset
        f["n_px"] = int(m.sum())
        v = hp[y0:y1, x0:x1][m]
        f["hf_std"] = float(v.std())
        f["mean_rgb"] = [float(x) for x in rgb[y0:y1, x0:x1][m].mean(0)]
        f["lum_std"] = float(lum[y0:y1, x0:x1][m].std())
        # structure tensor coherence of the high-passed image
        g1 = gx[y0:y1, x0:x1][m]
        g2 = gy[y0:y1, x0:x1][m]
        jxx, jyy, jxy = (g1 * g1).mean(), (g2 * g2).mean(), (g1 * g2).mean()
        tr = jxx + jyy
        disc = np.sqrt(max((jxx - jyy) ** 2 + 4 * jxy * jxy, 0.0))
        f["coherence"] = float(disc / (tr + 1e-9))
        # gradient direction (dominant), degrees, direction of the LINES is +90 from it
        ang = 0.5 * np.degrees(np.arctan2(2 * jxy, jxx - jyy))
        f["grad_angle_deg"] = float(ang)
        f["grad_energy"] = float(tr)
        feats.append(f)

    hdr = "%3s %3s %4s %7s %7s %7s %7s %8s %8s  %s" % (
        "i", "j", "full", "vis", "hf_std", "lum_sd", "coher", "gradE", "gradAng", "meanRGB")
    print(hdr)
    for f in feats:
        print("%3d %3d %4s %7.2f %7.3f %7.3f %7.3f %8.3f %8.1f  %s" % (
            f["i"], f["j"], "Y" if f["full"] else "-", f["frac_visible"], f["hf_std"],
            f["lum_std"], f["coherence"], f["grad_energy"], f["grad_angle_deg"],
            "%.0f,%.0f,%.0f" % tuple(f["mean_rgb"])))
    save_text(json.dumps(feats, indent=1), "work", "render_faces_raw.json")

    # contact sheet with (i,j) labels, 800 px wide
    s = 800.0 / W
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).resize(
        (800, int(round(H * s))), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    for f in feats:
        d.text((f["cx"] * s - 12, f["cy"] * s - 5), "%d,%d" % (f["i"], f["j"]), fill=(200, 0, 0))
    save_image(im, "work", "thumbs", "render_labelled.png")


if __name__ == "__main__":
    main()
