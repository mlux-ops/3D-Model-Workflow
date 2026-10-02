"""Step 02: ICC profile check and hexagon-grid detection in the layout render.

Finds the flat-top hexagon lattice (across-flats F, origin) that best explains the
thin light joint lines, using a ridge-response image and a lattice search.
"""

import io
import json
import os
import sys

import numpy as np
from PIL import Image, ImageCms
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, LIFESTYLE_PATH, save_text, save_npy  # noqa: E402


def profile_name(path):
    im = Image.open(path)
    icc = im.info.get("icc_profile")
    if not icc:
        return None
    p = ImageCms.ImageCmsProfile(io.BytesIO(icc))
    return ImageCms.getProfileDescription(p).strip()


def load_srgb(path):
    """RGB float array in sRGB (converted from the embedded profile if it is not sRGB)."""
    im = Image.open(path)
    icc = im.info.get("icc_profile")
    im = im.convert("RGB")
    if icc:
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        dst = ImageCms.createProfile("sRGB")
        desc = ImageCms.getProfileDescription(src).strip().lower()
        if "srgb" not in desc:
            im = ImageCms.profileToProfile(im, src, dst, outputMode="RGB")
    return np.asarray(im, dtype=np.float64)


def ridge_map(lum):
    """Positive where a thin line differs from its local surroundings (either sign)."""
    bg = ndi.uniform_filter(lum, size=9)
    return np.abs(ndi.gaussian_filter(lum, 0.8) - bg)


def hex_joint_points(F, x0, y0, W, H, step=1.0):
    """Sample points along the joint centrelines of a flat-top lattice, across-flats F.
    Module hexagon: circumradius R = F/sqrt(3); column pitch 1.5R; row pitch F."""
    R = F / np.sqrt(3.0)
    cp = 1.5 * R
    pts = []
    ncol = int(W / cp) + 4
    nrow = int(H / F) + 4
    for i in range(-2, ncol):
        cx = x0 + i * cp
        yoff = (F / 2.0) if (i % 2) else 0.0
        for j in range(-2, nrow):
            cy = y0 + yoff + j * F
            # six vertices of the flat-top hexagon
            ang = np.deg2rad(np.arange(6) * 60.0)
            vx = cx + R * np.cos(ang)
            vy = cy + R * np.sin(ang)
            for k in range(6):
                ax, ay = vx[k], vy[k]
                bx, by = vx[(k + 1) % 6], vy[(k + 1) % 6]
                n = max(2, int(np.hypot(bx - ax, by - ay) / step))
                t = np.linspace(0.1, 0.9, n)
                pts.append(np.stack([ax + (bx - ax) * t, ay + (by - ay) * t], axis=1))
    P = np.concatenate(pts, axis=0)
    ok = (P[:, 0] > 3) & (P[:, 0] < W - 4) & (P[:, 1] > 3) & (P[:, 1] < H - 4)
    return P[ok]


def score(ridge, F, x0, y0):
    H, W = ridge.shape
    P = hex_joint_points(F, x0, y0, W, H, step=3.0)
    v = ndi.map_coordinates(ridge, [P[:, 1], P[:, 0]], order=1, mode="nearest")
    return v.mean()


def main():
    print("render profile   :", profile_name(RENDER_PATH))
    print("lifestyle profile:", profile_name(LIFESTYLE_PATH))
    rgb = load_srgb(RENDER_PATH)
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722])
    H, W = lum.shape
    print("render size", W, H, "mean RGB", rgb.reshape(-1, 3).mean(0))
    ridge = ridge_map(lum)

    # coarse search: F in 300..330, x0 in [0, cp), y0 in [0, F)
    best = (-1, None)
    for F in np.arange(306.0, 326.0, 2.0):
        R = F / np.sqrt(3.0)
        cp = 1.5 * R
        for x0 in np.arange(0, 2 * cp, 8.0):
            for y0 in np.arange(0, F, 8.0):
                s = score(ridge, F, x0, y0)
                if s > best[0]:
                    best = (s, (F, x0, y0))
    print("coarse best", best)
    F, x0, y0 = best[1]
    # refine
    for span, step in ((10, 2.0), (3, 0.5), (1.0, 0.125), (0.3, 0.05)):
        cand = []
        for dF in np.arange(-span * 0.3, span * 0.3 + 1e-9, step * 0.3):
            for dx in np.arange(-span, span + 1e-9, step):
                for dy in np.arange(-span, span + 1e-9, step):
                    cand.append((F + dF, x0 + dx, y0 + dy))
        sc = [score(ridge, *c) for c in cand]
        k = int(np.argmax(sc))
        F, x0, y0 = cand[k]
        print("refined span", span, "->", (round(F, 3), round(x0, 3), round(y0, 3)), round(sc[k], 4))
    R = F / np.sqrt(3.0)
    res = {"F_px": F, "R_px": R, "col_pitch_px": 1.5 * R, "x0": x0, "y0": y0,
           "px_per_in_if_10in_flats": F / 10.125}
    print(json.dumps(res, indent=2))
    save_text(json.dumps(res, indent=2), "work", "render_grid.json")
    save_npy(ridge.astype(np.float32), "work", "render_ridge.npy")


if __name__ == "__main__":
    main()
