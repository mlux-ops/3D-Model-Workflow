"""Step 3: fit the flat-top hexagon lattice of the manufacturer layout render.

Joint score: the render draws each joint as a ~1 px light-grey line that is darker and
less saturated (R-B smaller) than the Sand face either side of it. Score = local
darkness x local de-saturation. The lattice (row pitch, column pitch, rotation, origin)
is found by folding the score image into one 2-hexagon unit cell and maximising the
sharpness of the folded pattern, then refined on the analytic hex edge-distance model.

Writes _work/lattice.json and a check overlay _work/lattice_overlay.png.
"""

import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage, optimize

from guard import RENDER_PATH, out_path, save_image

S3 = np.sqrt(3.0)


def joint_score(rgb):
    f = rgb.astype(np.float64)
    L = 0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2]
    c = f[..., 0] - f[..., 2]
    dark = np.clip(ndimage.uniform_filter(L, 7) - L, 0, None)
    desat = np.clip(ndimage.uniform_filter(c, 7) - c, 0, None)
    return np.sqrt(dark * desat), L


def edge_distance(xs, ys, p):
    """Distance (px) from each point to the nearest joint centreline, and the cell ids.

    p = (rp, aniso, theta_deg, x0, y0). Flat-top hexagons, column pitch cp = rp*sqrt(3)/2
    * aniso, odd columns shifted down by rp/2. Coordinates are rotated by -theta about the
    image origin before the lattice test."""
    rp, an, th, x0, y0 = p
    cp = rp * S3 / 2.0 * an
    t = np.deg2rad(th)
    xr = xs * np.cos(t) + ys * np.sin(t)
    yr = -xs * np.sin(t) + ys * np.cos(t)
    u = (xr - x0) / an          # undo anisotropy so hexagons are regular in (u, yr)
    cpu = cp / an
    best_e = np.full(xs.shape, -np.inf)
    bi = np.zeros(xs.shape, dtype=np.int64)
    bj = np.zeros(xs.shape, dtype=np.int64)
    ci = np.round(u / cpu).astype(np.int64)
    for di in (-1, 0, 1):
        i = ci + di
        yoff = np.where(i % 2 != 0, rp * 0.5, 0.0)
        j0 = np.round((yr - y0 - yoff) / rp).astype(np.int64)
        for dj in (-1, 0, 1):
            j = j0 + dj
            dx = u - i * cpu
            dy = yr - (y0 + yoff + j * rp)
            e = rp * 0.5 - np.maximum(np.abs(dy), np.abs(dx) * S3 / 2.0 + np.abs(dy) * 0.5)
            better = e > best_e
            best_e = np.where(better, e, best_e)
            bi = np.where(better, i, bi)
            bj = np.where(better, j, bj)
    return best_e, bi, bj


def fold_sharpness(S, rp, an, th):
    H, W = S.shape
    cp = rp * S3 / 2.0 * an
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
    t = np.deg2rad(th)
    xr = xs * np.cos(t) + ys * np.sin(t)
    yr = -xs * np.sin(t) + ys * np.cos(t)
    ux = np.mod(xr, 2.0 * cp)
    uy = np.mod(yr, rp)
    nb_x = int(np.ceil(2.0 * cp))
    nb_y = int(np.ceil(rp))
    idx = np.floor(uy).astype(np.int64) * nb_x + np.floor(ux).astype(np.int64)
    acc = np.bincount(idx.ravel(), weights=S.ravel(), minlength=nb_x * nb_y)
    cnt = np.bincount(idx.ravel(), minlength=nb_x * nb_y)
    fold = (acc / np.maximum(cnt, 1)).reshape(nb_y, nb_x)
    return float((fold ** 2).mean()), fold


def main():
    rgb = np.asarray(Image.open(RENDER_PATH).convert("RGB"))
    S, L = joint_score(rgb)
    H, W = S.shape
    # row projection -> half row pitch (horizontal flats every rp/2)
    prof = S.mean(axis=1) - S.mean()
    ac = np.correlate(prof, prof, mode="full")[len(prof) - 1:]
    lag = int(np.argmax(ac[100:220]) + 100)
    print("row-projection autocorrelation peak lag %d px -> rp ~ %d" % (lag, 2 * lag))
    # coarse search of rp (and a little anisotropy / rotation) by fold sharpness
    Sd = S[::2, ::2]
    best = None
    for rp in np.arange(2 * lag - 8, 2 * lag + 8.01, 0.5):
        v, _ = fold_sharpness(Sd, rp / 2.0, 1.0, 0.0)
        if best is None or v > best[0]:
            best = (v, rp)
    rp0 = best[1]
    best = None
    for rp in np.arange(rp0 - 0.6, rp0 + 0.61, 0.1):
        for an in (0.995, 0.9975, 1.0, 1.0025, 1.005):
            for th in (-0.2, -0.1, 0.0, 0.1, 0.2):
                v, _ = fold_sharpness(Sd, rp / 2.0, an, th)
                if best is None or v > best[0]:
                    best = (v, rp, an, th)
    _, rp1, an1, th1 = best
    print("fold search: rp %.2f aniso %.4f theta %.2f" % (rp1, an1, th1))
    # phase: evaluate the model score on a sparse set of strong-score pixels
    thr = np.percentile(S, 99.0)
    yy, xx = np.nonzero(S > thr)
    ww = S[yy, xx]
    xs = xx.astype(np.float64) + 0.5
    ys = yy.astype(np.float64) + 0.5
    cp1 = rp1 * S3 / 2.0 * an1

    def score(p, sig=1.2):
        e, _, _ = edge_distance(xs, ys, p)
        return float((ww * np.exp(-0.5 * (e / sig) ** 2)).sum() / ww.sum())

    grid = []
    for y0 in np.arange(0, rp1, 2.0):
        for x0 in np.arange(0, 2 * cp1, 2.0):
            grid.append((score((rp1, an1, th1, x0, y0), sig=2.0), x0, y0))
    grid.sort(reverse=True)
    _, gx, gy = grid[0]
    print("grid phase x0 %.1f y0 %.1f score %.4f" % (gx, gy, grid[0][0]))
    res = optimize.minimize(lambda q: -score(q, sig=1.0), np.array([rp1, an1, th1, gx, gy]),
                            method="Nelder-Mead",
                            options={"xatol": 1e-3, "fatol": 1e-6, "maxiter": 4000})
    rp, an, th, x0, y0 = res.x
    print("refined: rp %.3f aniso %.5f theta %.4f x0 %.3f y0 %.3f score %.4f"
          % (rp, an, th, x0, y0, -res.fun))
    cp = rp * S3 / 2.0 * an
    # joint line width estimate: mean darkness profile vs edge distance over all pixels
    ys2, xs2 = np.mgrid[0:H, 0:W].astype(np.float64)
    e, bi, bj = edge_distance(xs2 + 0.5, ys2 + 0.5, (rp, an, th, x0, y0))
    prof = []
    for k in range(0, 24):
        m = (e >= k * 0.5 - 0.25) & (e < k * 0.5 + 0.25)
        prof.append((k * 0.5, float(L[m].mean()), float((rgb[..., 0].astype(float) - rgb[..., 2])[m].mean())))
    print("edge-distance profile (e px, mean luma, mean R-B):")
    for q in prof:
        print("  %.1f  %.2f  %.2f" % q)
    lat = {"rp": rp, "cp": cp, "aniso": an, "theta_deg": th, "x0": x0, "y0": y0,
           "image_wh": [W, H], "profile": prof,
           "note": "flat-top; column i centre x = x0 + i*cp (rotated frame), odd columns +rp/2 in y"}
    json.dump(lat, open(out_path("_work", "lattice.json"), "w"), indent=2)
    # overlay for visual check: model joint centreline in red on a thumbnail
    ov = rgb.copy()
    ov[np.abs(e) < 0.8] = [255, 0, 0]
    im = Image.fromarray(ov)
    save_image(im.resize((800, int(round(800 * H / W))), Image.LANCZOS), "_work", "lattice_overlay.png")
    save_image(Image.fromarray(ov[0:400, 0:400]).resize((800, 800), Image.NEAREST), "_work", "lattice_overlay_tl.png")
    save_image(Image.fromarray(ov[H - 400:H, W - 400:W]).resize((800, 800), Image.NEAREST), "_work", "lattice_overlay_br.png")


if __name__ == "__main__":
    sys.exit(main())
