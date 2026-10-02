"""Step 10d: grain of the Raw colour versus the render.

Band-pass luminance standard deviation (difference of Gaussians, sigma 1 and 6 source px; multiplied by
the render->atlas scale for atlas pixels), in grey levels, inside the face interiors (core: at least
CORE_SRC_PX source px from the joint).

  main()             render (Raw / Matte / Chiseled faces) and the de-shaded Raw albedo pool
                     -> work/raw_colour_target.json  (s10b_build_atlas.py calibrates the Raw cavity term to it)
  atlas_band_std()   the same measure on finished atlas luminance (used by s11_verify.py)

python s10d_raw_colour_contrast.py      (run before s10b_build_atlas.py)"""

import json
import os
import sys

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, out_path, save_text  # noqa: E402
from geometry import face_centres, hex_inside, window_indices, window_offsets, source_to_atlas_scale  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402
from s03_faces import hex_dist_inside  # noqa: E402
from s08_raw_height import LUMW, padded_window, NWIN  # noqa: E402
from s10b_faces import win_centre  # noqa: E402

S1, S2 = 1.0, 6.0          # source px
CORE_SRC_PX = 30.0         # keep this far inside the face (source px): clear of the joint and the padding


def dog(a, s1, s2, mode="reflect"):
    return ndi.gaussian_filter(a, s1, mode=mode) - ndi.gaussian_filter(a, s2, mode=mode)


def atlas_band_std(lum, fid, types):
    """lum: atlas luminance (H, W); fid: face_ids array; types: {face index: type}.
    Returns {type: {"n", "band_std_mean", "band_std_each"}}."""
    scale = source_to_atlas_scale()
    band = dog(lum.astype(np.float32), S1 * scale, S2 * scale, mode="wrap")
    acc = {"raw": [], "matte": [], "chiseled": []}
    for c in face_centres():
        _, _, xi, yi = window_indices(c["cx"], c["cy"], 384)
        dx, dy = window_offsets(c["cx"], c["cy"], 384)
        ix = np.ix_(yi, xi)
        core = (fid[ix] == c["index"]) & (hex_inside(dx, dy) > CORE_SRC_PX * scale)
        acc[types[c["index"]]].append(float(band[ix][core].std()))
    return {k: {"n": len(v), "band_std_mean": float(np.mean(v)), "band_std_each": [round(x, 3) for x in v]}
            for k, v in acc.items()}


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    info = json.load(open(out_path("work", "pool_info.json")))
    raw_info = json.load(open(out_path("work", "pool_raw_info.json")))
    F = grid["F_px"]
    lum = load_srgb(RENDER_PATH) @ LUMW
    ys, xs = np.mgrid[0:NWIN, 0:NWIN].astype(np.float64)
    out = {"band_sigma_source_px": [S1, S2], "core_source_px": CORE_SRC_PX, "render": {}}

    for kind, faces in (("raw", [(f["i"], f["j"]) for f in raw_info["faces"]]),
                        ("matte", [tuple(x) for x in info["matte"]]),
                        ("chiseled", [(c["i"], c["j"]) for c in info["chiseled"]])):
        vals, means = [], []
        for (i, j) in faces:
            win, _, _, cen = padded_window(lum, grid, i, j)
            core = hex_dist_inside(xs - cen[0], ys - cen[1], F) > CORE_SRC_PX
            vals.append(float(dog(win, S1, S2)[core].std()))
            means.append(float(win[core].mean()))
        out["render"][kind] = {"n": len(vals), "band_std_mean": float(np.mean(vals)),
                               "band_std_each": [round(v, 3) for v in vals], "mean_luminance": float(np.mean(means))}

    alb = np.load(out_path("work", "pool_raw_alb.npy"))
    pool = []
    for k, f in enumerate(raw_info["faces"]):
        cen = win_centre(grid, f["i"], f["j"])
        core = hex_dist_inside(xs - cen[0], ys - cen[1], F) > CORE_SRC_PX
        pool.append(round(float(dog(alb[k] @ LUMW, S1, S2)[core].std()), 3))
    out["albedo_pool_raw"] = {"band_std_each": pool, "band_std_mean": float(np.mean(pool))}
    save_text(json.dumps(out, indent=1), "work", "raw_colour_target.json")
    for kind in ("raw", "matte", "chiseled"):
        print("render %-9s band std %.3f  (%d faces)" % (kind, out["render"][kind]["band_std_mean"], out["render"][kind]["n"]))
    print("de-shaded Raw albedo pool band std %.3f" % out["albedo_pool_raw"]["band_std_mean"])


if __name__ == "__main__":
    main()
