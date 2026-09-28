"""Check the floor-photo rectification and write textures/_REVIEW_floor_rectified.jpg.

Checks, all in the rectified plane:
  1. depth joints are straight and parallel: joint centre X measured per 1 in band of depth
  2. depth joints are evenly spaced at the 24.0625 in pitch
  3. the level cross joint lands on Z = 0 across the full width
  4. texture isotropy after rectification matches the swatch (calibration target)
  5. implied camera is physically plausible (focal length, height)
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

from floor_geom import CALIB, FLOOR, RUN, FloorGeom, load_gray, load_rgb

R = 32.0


def main():
    geo = FloorGeom()
    g = load_gray(FLOOR)
    Xj = geo.joint_X
    out = {"alpha": geo.alpha, "K_in": geo.K, "vp_px": [geo.x_vp, geo.y_vp],
           "image_space_joint_fit_rms_px": geo.joint_rms}
    ztop = geo.alpha * (1 / (15 - geo.y_vp) - 1 / geo.u_j)
    zbot = geo.alpha * (1 / (347 - geo.y_vp) - 1 / geo.u_j)
    rect, XX, ZZ, x, y = geo.rectify(g, R, Xj[0] - 3, Xj[-1] + 3, zbot, ztop)
    hp = rect - ndi.gaussian_filter(np.nan_to_num(rect, nan=np.nanmean(rect)), 3)
    # 1-2: joint centre per 1 in depth band
    per_joint = []
    for k, xj in enumerate(Xj):
        cols = np.nonzero(np.abs(XX[0] - xj) < 0.75)[0]
        xs = []
        for z0 in np.arange(np.floor(zbot) + 1, np.floor(ztop) - 1, 1.0):
            rows = np.nonzero((ZZ[:, 0] > z0) & (ZZ[:, 0] <= z0 + 1) & (np.abs(ZZ[:, 0]) > 0.5))[0]
            if len(rows) == 0:
                continue
            prof = hp[np.ix_(rows, cols)]
            if not np.isfinite(prof).all():
                continue
            prof = prof.mean(0)
            i = int(np.argmin(prof))
            if prof[i] > -1.0 or i in (0, len(prof) - 1):
                continue
            d = prof[i - 1] - 2 * prof[i] + prof[i + 1]
            xs.append(XX[0, cols[i]] + (0.5 * (prof[i - 1] - prof[i + 1]) / d) / R)
        xs = np.array(xs)
        per_joint.append({"joint": k, "n_bands": int(len(xs)), "mean_X_in": float(xs.mean()),
                          "std_X_in": float(xs.std()), "range_X_in": float(xs.max() - xs.min())})
    means = np.array([p["mean_X_in"] for p in per_joint])
    out["rectified_depth_joints"] = per_joint
    out["rectified_joint_spacing_in"] = np.diff(means).round(4).tolist()
    out["rectified_joint_spacing_error_in"] = float(np.abs(np.diff(means) - 24.0625).max())
    out["rectified_joint_max_std_in"] = float(max(p["std_X_in"] for p in per_joint))
    # 3: cross joint row
    rows = np.nonzero(np.abs(ZZ[:, 0]) < 1.0)[0]
    zs = []
    for k in range(len(Xj) - 1):
        cols = np.nonzero((XX[0] > Xj[k] + 1) & (XX[0] < Xj[k + 1] - 1))[0]
        prof = np.nanmean(hp[np.ix_(rows, cols)], axis=1)
        i = int(np.nanargmin(prof))
        zs.append(float(ZZ[rows[i], 0]))
    out["cross_joint_Z_per_column_in"] = [round(z, 3) for z in zs]
    # 5: implied camera
    c = geo.K ** 2 / geo.alpha             # = camera height / focal length
    out["implied_camera"] = {"H_over_f": c, "H_over_cos_pitch_in": geo.K,
                             "focal_px_if_height_equals_K": geo.K / c,
                             "hfov_deg_over_2000px": float(np.degrees(2 * np.arctan(1000 / (geo.K / c))))}
    calib = json.load(open(CALIB))
    out["isotropy_calibration_spread"] = calib["alpha_spread"]
    out["visible_depth_in"] = calib["visible_depth_in"]
    out["far_row_depth_below_tile_length"] = calib["visible_depth_in"]["far_row"] < 48.0
    out["pass"] = (out["rectified_joint_spacing_error_in"] < 0.1 and out["rectified_joint_max_std_in"] < 0.1
                   and max(abs(z) for z in zs) < 0.2 and out["far_row_depth_below_tile_length"])
    with open(os.path.join(RUN, "textures", "_floor_validation.json"), "w") as f:
        json.dump(out, f, indent=1)
    # review image: rectified floor at 21 px/in with 24 in grid overlay and mask tint
    rgb = load_rgb(FLOOR)
    r21 = 21.0
    img, XX, ZZ, x, y = geo.rectify(rgb, r21, -72, 54, zbot, ztop)
    ok = geo.valid_mask(XX, ZZ, x, y, joint_clear=0.4) & (y < 347.5) & (y > 15) & np.isfinite(img[..., 0])
    im = np.where(np.isfinite(img), img, 255.0)
    im[~ok] = im[~ok] * 0.55 + np.array([255, 60, 60]) * 0.45
    pil = Image.fromarray(np.clip(im, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(pil)
    for xj in Xj:
        px = (xj + 72) * r21
        for yy in range(0, pil.size[1], 12):
            d.line([(px, yy), (px, yy + 5)], fill=(0, 90, 255), width=1)
    pz = ztop * r21
    for xx in range(0, pil.size[0], 12):
        d.line([(xx, pz), (xx + 5, pz)], fill=(0, 90, 255), width=1)
    d.text((8, 8), "Floor photo rectified to the floor plane, 21 px/in. Dashed blue = ideal joints at 24.0625 in "
           "pitch and Z=0. Red tint = excluded (joints, shadows, frame).", fill=(0, 0, 0))
    pil.save(os.path.join(RUN, "textures", "_REVIEW_floor_rectified.jpg"), quality=92)
    print(json.dumps({k: out[k] for k in ("rectified_joint_spacing_in", "rectified_joint_spacing_error_in",
                                          "rectified_joint_max_std_in", "cross_joint_Z_per_column_in",
                                          "implied_camera", "pass")}, indent=1))


if __name__ == "__main__":
    main()
