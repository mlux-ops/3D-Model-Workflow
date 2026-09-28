"""(1) Baked-lighting check: is there a lighting gradient / vignette common to the 8 faces, or across a designed
joint?  (2) 1:1 crops of the 8 designed joints of the source faces (before any build), for viewing.

Lighting test: 16 x 16 block medians of log-luminance per face; mean over the 8 faces; a common vignette or
gradient survives the mean while the random marble content averages down by sqrt(8). The mean map is fitted
with plane + radial terms; its amplitude is compared with the between-face scatter / sqrt(8).
Edge-tone test: for each designed joint, the low-pass (sigma 40 px) luminance profiles of the 24 px strips
either side of the joint: mean ratio and RMS log-difference, against the same statistic for two strips 48 px
apart inside a face (the content's own tone change over that distance).
Writes _work/lighting.json, _work/joints_src/_VIEW_<a>_<b>.jpg.  Usage: python a02_lighting_joints.py"""
import json

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d

from colour_io import load_face_lin, lum
from common import lin_to_srgb
from guard import out_path

STRIPS = {"A": [1, 6, 7, 8], "B": [2, 3, 4, 5]}
NB = 16


def main():
    F = {i: load_face_lin(i) for i in range(1, 9)}
    L = {i: lum(F[i]) for i in F}
    n = L[1].shape[0]
    bs = n // NB
    maps = []
    for i in range(1, 9):
        lg = np.log(L[i][:bs * NB, :bs * NB] + 1e-4)
        maps.append(np.median(lg.reshape(NB, bs, NB, bs).transpose(0, 2, 1, 3).reshape(NB, NB, -1), axis=2))
    maps = np.array(maps)
    mean = maps.mean(0) - maps.mean()
    se = maps.std(0).mean() / np.sqrt(8)
    c = (np.arange(NB) + 0.5) / NB - 0.5
    yy, xx = np.meshgrid(c, c, indexing="ij")
    A = np.stack([np.ones(NB * NB), xx.ravel(), yy.ravel(), (xx * xx + yy * yy).ravel()], 1)
    coef, *_ = np.linalg.lstsq(A, mean.ravel(), rcond=None)
    fit = (A @ coef).reshape(NB, NB)
    corner = np.exp(fit[[0, 0, -1, -1], [0, -1, 0, -1]].mean() - fit[NB // 2 - 1:NB // 2 + 1, NB // 2 - 1:NB // 2 + 1].mean()) - 1
    res = {"common_map_sd_log": float(mean.std()), "block_se_log": float(se),
           "fit_coef_plane_x_y_radial": [float(v) for v in coef[1:]],
           "common_corner_vs_centre_pct": float(100 * corner),
           "gradient_x_edge_to_edge_pct": float(100 * (np.exp(coef[1]) - 1)),
           "gradient_y_edge_to_edge_pct": float(100 * (np.exp(coef[2]) - 1))}
    # edge tone continuity across designed joints
    joints = []
    for s, seq in STRIPS.items():
        for k in range(4):
            a, b = seq[k], seq[(k + 1) % 4]
            pa = gaussian_filter1d(np.log(L[a][:, -24:].mean(1)), 40)
            pb = gaussian_filter1d(np.log(L[b][:, :24].mean(1)), 40)
            joints.append({"strip": s, "a": a, "b": b, "mean_ratio_b_over_a": float(np.exp(pb.mean() - pa.mean())),
                           "rms_logdiff": float(np.sqrt(((pb - pa) ** 2).mean()))})
    base = []
    for i in range(1, 9):
        for x in range(100, n - 150, 100):
            p1 = gaussian_filter1d(np.log(L[i][:, x:x + 24].mean(1)), 40)
            p2 = gaussian_filter1d(np.log(L[i][:, x + 48:x + 72].mean(1)), 40)
            base.append(np.sqrt(((p2 - p1) ** 2).mean()))
    res["designed_joints_edge_tone"] = joints
    res["interior_48px_rms_logdiff_mean_p90"] = [float(np.mean(base)), float(np.percentile(base, 90))]
    res["face_mean_srgb"] = {i: [float(v) for v in lin_to_srgb(F[i].reshape(-1, 3).mean(0))] for i in F}
    res["all_faces_mean_srgb"] = [float(v) for v in lin_to_srgb(np.mean([F[i].reshape(-1, 3).mean(0) for i in F], 0))]
    # field tone (exclude veins: pixels between the 40th and 90th luminance percentile of each face)
    fld = []
    for i in F:
        l = L[i]
        lo, hi = np.percentile(l, [40, 90])
        m = (l >= lo) & (l <= hi)
        fld.append(F[i][m].mean(0))
    res["field_mean_srgb"] = [float(v) for v in lin_to_srgb(np.mean(fld, 0))]
    json.dump(res, open(out_path("_work/lighting.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "designed_joints_edge_tone"}, indent=1))
    for j in joints:
        print(j)
    # 1:1 joint crops: 200 px either side, 700 rows centred on the most vein-energetic part of the joint
    for s, seq in STRIPS.items():
        for k in range(4):
            a, b = seq[k], seq[(k + 1) % 4]
            e = np.abs(np.diff(L[a][:, -6:], axis=0)).sum(1) + np.abs(np.diff(L[b][:, :6], axis=0)).sum(1)
            e = np.convolve(e, np.ones(700), "valid")
            y0 = int(np.argmax(e))
            crop = np.concatenate([F[a][y0:y0 + 700, -200:], np.full((700, 2, 3), 1.0), F[b][y0:y0 + 700, :200]], 1)
            Image.fromarray(np.round(lin_to_srgb(crop)).astype(np.uint8)).save(
                out_path("_work/joints_src/_VIEW_%d_%d.jpg" % (a, b)), quality=92)
            print("crop", a, b, "rows", y0, y0 + 700)


if __name__ == "__main__":
    main()
