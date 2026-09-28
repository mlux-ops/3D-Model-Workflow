"""Chip tone statistics for the 1x3 mosaic.

Targets: the manufacturer's straight-on sheet w07 (4 x 12 chips, 34.5 px/in) and the user's installed wall u11
(chip grid measured in a02). For each chip (inset 20 % of its height from the joints) we measure
  m  = log mean linear luminance, relative to the image's large-scale trend (plane fit removed first), and
  t  = texture: std of DoG(0.6 px, 3 px @ 16 px/in) band of luminance / chip mean.
The same statistics are measured on random 1x3 crops of the real vein-cut faces (A = u09, W = w14 minus A).
extra_sigma = sqrt(max(0, sd_target(m)^2 - sd_crops(m)^2)) is the per-chip tone jitter needed on top of the
variation the crops already carry. Writes _work/mosaic_stats.json."""
import json

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom

from guard import out_path, ref

Image.MAX_IMAGE_PIXELS = None


def lin(a):
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def load_lum(p, rot=0):
    a = np.asarray(Image.open(p).convert("RGB")).astype(np.float64)
    a = np.rot90(a, rot)
    return lin(a) @ np.array([0.2126, 0.7152, 0.0722])


def detrend(L):
    yy, xx = np.mgrid[0:L.shape[0], 0:L.shape[1]]
    G = np.stack([np.ones(L.size), xx.ravel() / L.shape[1], yy.ravel() / L.shape[0]], 1)
    c, *_ = np.linalg.lstsq(G, np.log(L.ravel() + 1e-4), rcond=None)
    return L / np.exp(G @ c).reshape(L.shape) * np.exp(c[0])


def chip_stats(L, boxes, ppi):
    s = 16.0 / ppi
    out = []
    for x0, y0, x1, y1 in boxes:
        c = L[int(y0):int(y1), int(x0):int(x1)]
        if c.size < 20:
            continue
        cz = zoom(c, s, order=1) if abs(s - 1) > 1e-6 else c
        band = gaussian_filter(cz, 0.6) - gaussian_filter(cz, 3.0)
        out.append((float(np.log(c.mean())), float(band.std() / c.mean())))
    return np.array(out)


def grid_boxes(x_edges, y_edges, inset):
    boxes = []
    for i in range(len(y_edges) - 1):
        for j in range(len(x_edges) - 1):
            x0, x1 = x_edges[j], x_edges[j + 1]
            y0, y1 = y_edges[i], y_edges[i + 1]
            d = inset * (y1 - y0)
            boxes.append((x0 + d, y0 + d, x1 - d, y1 - d))
    return boxes


def main():
    meas = json.load(open(out_path("_work/measure.json")))
    res = {}
    # w07: joints measured (columns 100.8/205/309.7, rows every 34.88 from 30.9)
    L = detrend(load_lum(ref("web/w07_ms_jute_veincut_1x3mosaic_01.jpg")))
    xv = [0.0, 100.8, 205.0, 309.7, 414.0]
    yh = [0.0] + [j["centre"] for j in meas["w07"]["horizontal_joints"]] + [414.0]
    st = chip_stats(L, grid_boxes(xv, yh, 0.2), 34.5)
    res["w07_sheet"] = st
    # u11: fit a regular grid to the measured joints (pitch_x 46.83, pitch_y = pitch_x / 3)
    L = detrend(load_lum(ref("user_supplied/u11_mosaic_1x3_installed.png")))
    px = meas["u11"]["pitch_x"]
    vx = np.array([j["centre"] for j in meas["u11"]["vertical_joints"]])
    ox = float(np.median(((vx + px / 2) % px) - px / 2))
    py = px / 3.0
    hy = np.array([j["centre"] for j in meas["u11"]["horizontal_joints"]])
    ph = ((hy + py / 2) % py) - py / 2
    oy = float(np.median(ph))
    xs = [ox + k * px for k in range(-1, 20) if 0 <= ox + k * px <= L.shape[1]]
    ys = [oy + k * py for k in range(-1, 40) if 0 <= oy + k * py <= L.shape[0]]
    res["u11_grid"] = {"pitch_x": px, "pitch_y": py, "origin": [ox, oy],
                       "h_joint_residuals_px": [float(v) for v in ph]}
    st = chip_stats(L, grid_boxes(xs, ys, 0.2), px / 3.0)
    res["u11_installed"] = st
    # lighting in an installed photo is not planar: also measure chip means relative to the median of the
    # 5 x 5 chip neighbourhood (local high-pass on the chip grid)
    g = st[:, 0].reshape(len(ys) - 1, len(xs) - 1)
    from scipy.ndimage import median_filter
    res["u11_local_sd_logmean"] = float((g - median_filter(g, 5, mode="nearest")).std())
    gw = res["w07_sheet"][:, 0].reshape(len(yh) - 1, 4)
    res["w07_local_sd_logmean"] = float((gw - median_filter(gw, 5, mode="nearest")).std())
    # crops of the real faces at their native px/in, 2.9375 x 0.9375 in
    rng = np.random.default_rng(3)
    crops = []
    for p, rot, ppi, excl in ((ref("user_supplied/u09_flat_veincut_swatch.webp"), 0, 40.0, None),
                              (ref("web/w14_ms_jute_veincut_48x110_04.jpg"), 1, 41.45, (1423, 501, 3381, 1478))):
        L = detrend(load_lum(p, rot))
        w, h = 2.9375 * ppi, 0.9375 * ppi
        boxes = []
        while len(boxes) < 300:
            x0 = rng.uniform(0, L.shape[1] - w)
            y0 = rng.uniform(0, L.shape[0] - h)
            if excl and not (x0 + w < excl[0] or x0 > excl[2] or y0 + h < excl[1] or y0 > excl[3]):
                continue
            boxes.append((x0, y0, x0 + w, y0 + h))
        d = 0.2 * h
        cs = chip_stats(L, [(a + d, b + d, c - d, e - d) for a, b, c, e in boxes], ppi)
        res.setdefault("per_source_sd_logmean", []).append(float(cs[:, 0].std()))
        res.setdefault("per_source_corr", []).append(float(np.corrcoef(cs[:, 0], cs[:, 1])[0, 1]))
        cs[:, 0] -= cs[:, 0].mean()          # remove the exposure difference between sources
        crops.append(cs)
    res["face_crops"] = np.concatenate(crops)
    out = {}
    for k in ("w07_sheet", "u11_installed", "face_crops"):
        st = res[k]
        out[k] = {"n": int(len(st)), "sd_logmean": float(st[:, 0].std()), "texture_mean": float(st[:, 1].mean()),
                  "texture_sd": float(st[:, 1].std()),
                  "corr_mean_texture": float(np.corrcoef(st[:, 0], st[:, 1])[0, 1]),
                  "logmean_p5_p95": [float(np.percentile(st[:, 0] - st[:, 0].mean(), 5)),
                                     float(np.percentile(st[:, 0] - st[:, 0].mean(), 95))]}
    sd_c = out["face_crops"]["sd_logmean"]
    for k in ("w07_sheet", "u11_installed"):
        out[k]["extra_sigma_needed"] = float(np.sqrt(max(0.0, out[k]["sd_logmean"] ** 2 - sd_c ** 2)))
    out["u11_grid"] = res["u11_grid"]
    out["u11_local_sd_logmean"] = res["u11_local_sd_logmean"]
    out["crops_per_source_sd_logmean"] = res["per_source_sd_logmean"]
    out["crops_per_source_corr_mean_texture"] = res["per_source_corr"]
    out["w07_local_sd_logmean"] = res["w07_local_sd_logmean"]
    json.dump(out, open(out_path("_work/mosaic_stats.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "u11_grid"}, indent=1))
    print("local sd u11 %.4f  w07 %.4f" % (out["u11_local_sd_logmean"], out["w07_local_sd_logmean"]))
    print("u11 grid", {k: v for k, v in out["u11_grid"].items() if k != "h_joint_residuals_px"})


if __name__ == "__main__":
    main()
