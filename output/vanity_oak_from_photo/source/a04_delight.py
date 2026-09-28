"""De-light the rectified crops (remove shading gradients only), measure grain orientation, and record tones.

0. Specular veil (see deveil()): subtract a neutral additive sheen from the crops that show one.
1. Front-wide lighting: the photo is lit from the left, so a crop's mean log-luminance falls with its front-plane
   position. Fit log L = a + b*u + c*v over the ten panel means (u, v = panel centre in front-plane inches) and
   remove that plane (keeps the overall mean).
2b. Then flatten the along-grain column-mean profile (smoothed, sigma 4 px) so reveal edge fall-off and lighting
   along the grain are gone at the along-grain ends where the quilt joins are cut.
2. Within each crop: fit a quadratic surface to the heavily blurred log-luminance and divide it out, keeping the
   crop mean, so per-leaf tone differences survive but gradients inside a leaf do not. All channels are scaled by
   the same factor (chroma unchanged). Linear light, float64.
3. Grain angle per crop from the structure tensor of the band-passed luminance (0 deg = horizontal).

Writes _work/delit/<name>.npy, _work/delight.json and _PREVIEW_source_crops_delit.jpg (contact sheet)."""
import json

import numpy as np
from scipy import ndimage as ndi

from common import lum, lin_to_srgb, thumb
from guard import out_path

NAMES = ["drawer_L1", "drawer_L2", "drawer_L3", "drawer_R1", "drawer_R2", "drawer_R3", "door_L", "door_R", "apron",
         "bottom_rail"]


def grain_angle(rgb):
    L = np.log(np.maximum(lum(rgb), 1e-4))
    L = ndi.gaussian_filter(L, 1.0) - ndi.gaussian_filter(L, 8)
    gy, gx = np.gradient(L)
    Jxx, Jyy, Jxy = (gx * gx).mean(), (gy * gy).mean(), (gx * gy).mean()
    # dominant gradient direction is across grain; grain direction is perpendicular
    theta_g = 0.5 * np.degrees(np.arctan2(2 * Jxy, Jxx - Jyy))
    ang = theta_g + 90.0
    ang = (ang + 90) % 180 - 90
    coh = np.sqrt((Jxx - Jyy) ** 2 + 4 * Jxy ** 2) / (Jxx + Jyy)
    return float(ang), float(coh)


def quad_fit(logL, blur):
    H, W = logL.shape
    S = ndi.gaussian_filter(logL, blur, mode="reflect")
    yy, xx = np.mgrid[:H, :W]
    x = (xx - W / 2) / (W / 2)
    y = (yy - H / 2) / max(H / 2, 1)
    A = np.stack([np.ones_like(x), x, y, x * x, x * y, y * y], -1).reshape(-1, 6)
    if H < 100:          # thin strips: along-grain quadratic, across-grain linear only
        A = A[:, [0, 1, 2, 3]]
    coef, *_ = np.linalg.lstsq(A, S.reshape(-1), rcond=None)
    surf = (A @ coef).reshape(H, W)
    return surf - coef[0], coef


def deveil(crops):
    """Specular veil: a sheen adds a near-neutral constant to a panel (raw = shading*albedo + veil), which lowers both
    its saturation and its grain contrast. drawer_R1, drawer_R2 and the apron are brighter, greyer and flatter than
    the rest. Estimate the neutral veil v per crop from its mean chromaticity: (R-v)/(B-v) = reference R/B, where the
    reference is the median R/B of all crops; only crops more than 0.05 below the reference are corrected. The model
    is checked, not assumed: the resulting G/B must land near the reference G/B too (reported)."""
    m = {n: c.reshape(-1, 3).mean(0) for n, c in crops.items()}
    rb_ref = float(np.median([v[0] / v[2] for v in m.values()]))
    gb_ref = float(np.median([v[1] / v[2] for v in m.values()]))
    rep = {"reference_R_over_B": round(rb_ref, 4), "reference_G_over_B": round(gb_ref, 4), "crops": {}}
    out = {}
    for n, c in crops.items():
        r, g, b = m[n]
        v = 0.0
        if r / b < rb_ref - 0.05:
            v = (rb_ref * b - r) / (rb_ref - 1)
        d = np.clip(c - v, 1e-4, None)
        md = d.reshape(-1, 3).mean(0)
        rep["crops"][n] = {"veil_lin": round(float(v), 5), "R_over_B_before": round(float(r / b), 4),
                           "G_over_B_before": round(float(g / b), 4), "G_over_B_after": round(float(md[1] / md[2]), 4)}
        out[n] = d
    return out, rep


def main():
    meta = json.load(open(out_path("_work/crops.json")))["crops"]
    crops = {n: np.load(out_path("_work/crops/%s.npy" % n)) for n in NAMES}
    crops, veil_rep = deveil(crops)
    mlog = {n: float(np.mean(np.log(np.maximum(lum(c), 1e-4)))) for n, c in crops.items()}
    U = np.array([[1, meta[n]["centre_in"][0], meta[n]["centre_in"][1]] for n in NAMES])
    y = np.array([mlog[n] for n in NAMES])
    g, *_ = np.linalg.lstsq(U, y, rcond=None)
    plane = U @ g
    plane -= plane.mean()
    info = {"veil": veil_rep, "front_plane_fit": {"a": g[0], "per_in_u": g[1], "per_in_v": g[2],
                                                  "note": "log-luminance per inch; removed, mean kept"}, "crops": {}}
    print(json.dumps(veil_rep))
    delit = {}
    for i, n in enumerate(NAMES):
        c = crops[n]
        logL = np.log(np.maximum(lum(c), 1e-4))
        surf, coef = quad_fit(logL, blur=24)
        corr = np.exp(-(surf + plane[i]))[..., None]
        d = c * corr
        # along-grain flattening: the column-mean log-luminance (averaged across the whole leaf) carries the reveal
        # edge fall-off and any lighting gradient along the grain; remove its smoothed profile, keep the mean.
        # The across-grain stripe profile (the grain itself) is untouched.
        cp = np.log(np.maximum(lum(d), 1e-4)).mean(0)
        cps = ndi.gaussian_filter1d(cp, 4, mode="nearest")
        d = d * np.exp(-(cps - cps.mean()))[None, :, None]
        # chroma shading: coloured light (under-counter bounce, cool fill) tints parts of a crop. Remove the smooth
        # (quadratic) and along-grain components of each channel's log-chromaticity, keeping the crop's mean colour.
        Ld = np.log(np.maximum(lum(d), 1e-4))
        for ch in range(3):
            rc = np.log(np.maximum(d[..., ch], 1e-4)) - Ld
            s_c, _ = quad_fit(rc, blur=24)
            rc2 = rc - s_c
            cpc = ndi.gaussian_filter1d(rc2.mean(0), 4, mode="nearest")
            d[..., ch] *= np.exp(-s_c - (cpc - cpc.mean())[None, :])
        if n in ("apron", "bottom_rail"):
            # the long thin rails carry lighting that changes along their 42 in length per row (counter shadow and
            # the post shading at the ends): flatten each row's along-grain low-pass (sigma 48 px = 1.5 in),
            # keeping each row's mean, i.e. the across-grain grain profile.
            Ld = np.log(np.maximum(lum(d), 1e-4))
            lp = ndi.gaussian_filter1d(Ld, 48, axis=1, mode="nearest")
            d = d * np.exp(-(lp - lp.mean(1, keepdims=True)))[..., None]
        delit[n] = d
        np.save(out_path("_work/delit/%s.npy" % n), d)
        a0, c0 = grain_angle(c)
        a1, c1 = grain_angle(d)
        Ld = np.log(np.maximum(lum(d), 1e-4))
        lf = ndi.gaussian_filter(Ld, 24)
        info["crops"][n] = {"mean_log_lum_raw": round(mlog[n], 4), "front_plane_removed": round(float(plane[i]), 4),
                            "intra_gradient_range_removed": round(float(np.ptp(surf)), 4),
                            "residual_lowfreq_ptp": round(float(np.ptp(lf[24:-24, 24:-24] if lf.shape[0] > 60 else lf)), 4),
                            "mean_srgb_after": [round(float(v), 1) for v in lin_to_srgb(d.reshape(-1, 3).mean(0))],
                            "grain_angle_deg": round(a1, 2), "coherence": round(c1, 3)}
        print(n, info["crops"][n])
    allpix = np.concatenate([d.reshape(-1, 3) for d in delit.values()])
    info["overall_mean_srgb"] = [round(float(v), 1) for v in lin_to_srgb(allpix.mean(0))]
    json.dump(info, open(out_path("_work/delight.json"), "w"), indent=1)
    # contact sheet in a fixed layout
    order = [["drawer_L1", "drawer_L2", "drawer_L3", "drawer_R1"], ["drawer_R2", "drawer_R3"], ["door_L"], ["door_R"],
             ["apron"], ["bottom_rail"]]
    rows = []
    for ln in order:
        h = max(delit[n].shape[0] for n in ln)
        w = sum(delit[n].shape[1] for n in ln) + 12 * (len(ln) - 1)
        row = np.ones((h, w, 3))
        x = 0
        for n in ln:
            row[:delit[n].shape[0], x:x + delit[n].shape[1]] = delit[n]
            x += delit[n].shape[1] + 12
        rows.append(row)
    W = max(r.shape[1] for r in rows)
    sheet = np.ones((sum(r.shape[0] for r in rows) + 12 * len(rows), W, 3))
    yv = 0
    for r in rows:
        sheet[yv:yv + r.shape[0], :r.shape[1]] = r
        yv += r.shape[0] + 12
    thumb(lin_to_srgb(sheet), out_path("_PREVIEW_source_crops_delit.jpg"))
    print(info["front_plane_fit"], info["overall_mean_srgb"])


if __name__ == "__main__":
    main()
