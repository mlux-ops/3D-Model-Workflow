"""Step 10c: relative relief amplitude of Raw and Chiseled faces, from the render.

The two source images carry no depth reference, so the absolute relief is a design value
(design.py). What the render does carry is the *ratio* of the two textures' shading contrast:
  Raw       rms of the light-directional shading of the height estimate (pool_raw_info, slope_l_rms)
  Chiseled  rms of the groove component G of the luminance (pool_info, G_std)
both in render grey levels, measured on the whole faces of the render.
The Chiseled groove is set to CHIS_DEPTH_MM. Its rms slope follows from the pooled groove component.
Raw relief is scaled so the ratio of rms slopes matches the render's ratio of contrasts:
  slope_raw_full / slope_chis = sqrt(2) * (mean slope_l_rms) / (mean G_std)
(sqrt(2): the render shows Raw only along the light axis; isotropic relief has sqrt(2) times more
full-gradient than along-axis slope. The Chiseled groove contrast in the render is the same for all
three groove orientations, including the one almost parallel to the light, so it is compared
across the groove, i.e. on the full gradient.)
Writes work/relief_calibration.json (read by s10b_build_atlas.py)."""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import out_path, save_text  # noqa: E402
from geometry import MM_PER_PX, source_to_atlas_scale  # noqa: E402
from design import CHIS_DEPTH_MM, SQRT2  # noqa: E402
import s10b_faces as F  # noqa: E402


def main():
    info = json.load(open(out_path("work", "pool_info.json")))
    raw_info = json.load(open(out_path("work", "pool_raw_info.json")))
    g_std = np.array([c["G_std"] for c in info["chiseled"]])
    slope_l = np.array([f["slope_l_rms"] for f in raw_info["faces"]])
    ratio = float(g_std.mean() / slope_l.mean())

    P = F.Pools()
    mm_per_src_px = MM_PER_PX * source_to_atlas_scale()
    yy, xx = np.mgrid[0:P.chis_G.shape[1], 0:P.chis_G.shape[2]]
    per_face = []
    for k, cen in enumerate(P.chis_cen):
        G = P.chis_G[k].astype(np.float64)
        w = np.clip((P.G_land - G) / (P.G_land - P.G_groove), 0.0, 1.0)
        h = -CHIS_DEPTH_MM * w
        gy, gx = np.gradient(h, mm_per_src_px)
        m = np.hypot(xx - cen[0], yy - cen[1]) < 140.0
        per_face.append({
            "slope_rms": float(np.sqrt((gx ** 2 + gy ** 2)[m].mean())),
            "depth_p1_p99_mm": float(np.percentile(h[m], 99) - np.percentile(h[m], 1)),
            "groove_weight_mean": float(w[m].mean()),
        })
    slope_chis = float(np.mean([p["slope_rms"] for p in per_face]))
    slope_raw_target = SQRT2 * slope_chis * float(slope_l.mean() / g_std.mean())

    out = {
        "render_G_std_mean": float(g_std.mean()), "render_G_std_per_face": g_std.tolist(),
        "render_raw_slope_l_rms_mean": float(slope_l.mean()), "render_raw_slope_l_rms_per_face": slope_l.tolist(),
        "render_contrast_ratio_chiseled_over_raw": ratio,
        "chiseled_depth_mm": CHIS_DEPTH_MM,
        "chiseled_slope_rms_from_pool": slope_chis,
        "chiseled_pool_faces": per_face,
        "raw_slope_target_full_gradient": slope_raw_target,
        "raw_to_chiseled_slope_ratio": slope_raw_target / slope_chis,
    }
    save_text(json.dumps(out, indent=1), "work", "relief_calibration.json")
    print("render contrast ratio Chiseled/Raw %.2f (G_std %.2f / slope_l %.2f)" % (ratio, g_std.mean(), slope_l.mean()))
    print("Chiseled depth %.2f mm -> rms slope %.3f ; Raw full-gradient rms slope target %.3f (ratio %.2f)"
          % (CHIS_DEPTH_MM, slope_chis, slope_raw_target, slope_raw_target / slope_chis))


if __name__ == "__main__":
    main()
