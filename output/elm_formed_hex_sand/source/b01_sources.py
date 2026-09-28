"""Build step 1: prepare the render as a calibrated source.

- Divide out the render's smooth lighting field (quadratic fit, a08) so faces keep only
  their own tone and cloudiness.
- Per render face: owner map, clean mask (>= CLEAN_PX from the joint centreline, inside
  the image), mean colour, and masked (normalised-convolution) low-pass colour, so no
  joint-line or neighbour colour bleeds into a face.
- Raw relief band: band-pass of each face's relative luminance (masked), in the band
  where raw faces carry clearly more energy than matte faces (measured here).
- Chiseled: groove phase (canonical frame) and the folded periodic colour profile.
Writes _work/src_*.npy and _work/sources.json.
"""

import json
import sys

import numpy as np
from scipy import ndimage

from common import (load_lattice, render_rgb, srgb_to_lin, out_path, S3, hex_edge_distance_local)
from a03_fit_lattice import edge_distance

CLEAN_PX = 5.0
PPI_LINE_PX = 1.5              # render joint line width, px (measured profile FWHM ~1.5)
FOLD_BINS = 32


def masked_gauss(a, m, s):
    """Normalised convolution: Gaussian blur of a inside mask m only."""
    num = ndimage.gaussian_filter(a * m, s, mode="constant")
    den = ndimage.gaussian_filter(m.astype(np.float64), s, mode="constant")
    return num / np.maximum(den, 1e-6)


def classify(c):
    if c["coher"] > 0.6:
        return "chiseled"
    if c["hp_std"] > 2.8:
        return "raw"
    return "matte"


def main():
    lat = load_lattice()
    cells = json.load(open(out_path("_work", "cells_raw.json")))
    tone = json.load(open(out_path("_work", "tone.json")))
    light = json.load(open(out_path("_work", "grooves.json")))
    rgb = render_rgb()
    lin = srgb_to_lin(rgb)
    Hr, Wr = lin.shape[:2]
    ys, xs = np.mgrid[0:Hr, 0:Wr].astype(np.float64)
    c = tone["illum_coef"]
    xn, yn = (xs + 0.5) / Wr, (ys + 0.5) / Hr
    field = c[0] + c[1] * xn + c[2] * yn + c[3] * xn ** 2 + c[4] * yn ** 2 + c[5] * xn * yn
    field /= tone["illum_mean"]
    corr = lin / field[..., None]
    e, bi, bj = edge_distance(xs + 0.5, ys + 0.5, (lat["rp"], lat["aniso"], lat["theta_deg"],
                                                  lat["x0"], lat["y0"]))
    owner = np.full((Hr, Wr), -1, dtype=np.int32)
    clean = np.zeros((Hr, Wr), dtype=bool)
    lp = np.zeros_like(corr)
    Yc = 0.2126 * corr[..., 0] + 0.7152 * corr[..., 1] + 0.0722 * corr[..., 2]
    rel = np.zeros((Hr, Wr))
    meta = []
    ppi_r = (lat["rp"] - PPI_LINE_PX) / 10.0
    for cc in cells:
        m_all = (bi == cc["i"]) & (bj == cc["j"])
        m = m_all & (e >= CLEAN_PX)
        if m.sum() < 500:
            continue
        owner[m_all] = cc["id"]
        clean[m] = True
        ys_, xs_ = np.nonzero(m_all)
        y0, y1 = ys_.min(), ys_.max() + 1
        x0, x1 = xs_.min(), xs_.max() + 1
        pad = 40
        Y0, Y1, X0, X1 = max(0, y0 - pad), min(Hr, y1 + pad), max(0, x0 - pad), min(Wr, x1 + pad)
        mm = m[Y0:Y1, X0:X1].astype(np.float64)
        for ch in range(3):
            lp[Y0:Y1, X0:X1, ch] = np.where(m_all[Y0:Y1, X0:X1],
                                           masked_gauss(corr[Y0:Y1, X0:X1, ch], mm, 6.0),
                                           lp[Y0:Y1, X0:X1, ch])
        mean_rgb = corr[m].mean(axis=0)
        Ym = Yc[m].mean()
        rel[m_all] = Yc[m_all] / Ym - 1.0
        meta.append({"id": cc["id"], "i": cc["i"], "j": cc["j"], "cx": cc["cx"], "cy": cc["cy"],
                     "frac": cc["frac"], "type": classify(cc), "npx_clean": int(m.sum()),
                     "mean_lin": mean_rgb.tolist(), "bbox": [int(X0), int(Y0), int(X1), int(Y1)]})
    # ---- band analysis: radial power of relative luminance, raw vs matte (full faces) --
    def radial_power(ids, half=100):
        acc = None
        for mt in meta:
            if mt["id"] not in ids:
                continue
            yy, xx = np.mgrid[-half:half, -half:half]
            P = ndimage.map_coordinates(rel, [yy + mt["cy"] - 0.5, xx + mt["cx"] - 0.5], order=1)
            win = np.hanning(2 * half)[:, None] * np.hanning(2 * half)[None, :]
            F = np.abs(np.fft.fftshift(np.fft.fft2((P - P.mean()) * win))) ** 2
            acc = F if acc is None else acc + F
        f = np.fft.fftshift(np.fft.fftfreq(2 * half))
        fy, fx = np.meshgrid(f, f, indexing="ij")
        fr = np.hypot(fx, fy)
        edges = np.array([1 / 100, 1 / 64, 1 / 40, 1 / 28, 1 / 20, 1 / 14, 1 / 10, 1 / 7,
                          1 / 5, 1 / 3.5, 1 / 2.5, 0.5])
        out = []
        for a, b in zip(edges[:-1], edges[1:]):
            k = (fr >= a) & (fr < b)
            out.append(float(acc[k].mean()))
        return edges, np.array(out)
    full = [mt for mt in meta if mt["frac"] > 0.99]
    raw_ids = [mt["id"] for mt in full if mt["type"] == "raw"]
    mat_ids = [mt["id"] for mt in full if mt["type"] == "matte"]
    edges, pr = radial_power(raw_ids)
    _, pm = radial_power(mat_ids)
    pr /= len(raw_ids); pm /= len(mat_ids)
    print("band (period px)      raw/matte power ratio")
    for k in range(len(pr)):
        print("  %6.1f - %6.1f      %.2f" % (1 / edges[k], 1 / edges[k + 1], pr[k] / pm[k]))
    # ---- raw relief band (masked DoG), sigma chosen from the ratio table ---------------
    S_LO, S_HI = 0.7, 10.0
    hband = np.zeros((Hr, Wr))
    for mt in meta:
        if mt["type"] != "raw":
            continue
        X0, Y0, X1, Y1 = mt["bbox"]
        m = clean[Y0:Y1, X0:X1] & (owner[Y0:Y1, X0:X1] == mt["id"])
        mm = m.astype(np.float64)
        r = rel[Y0:Y1, X0:X1]
        d = masked_gauss(r, mm, S_LO) - masked_gauss(r, mm, S_HI)
        hband[Y0:Y1, X0:X1] = np.where(owner[Y0:Y1, X0:X1] == mt["id"], d, hband[Y0:Y1, X0:X1])
    rawmask = clean & np.isin(owner, [mt["id"] for mt in meta if mt["type"] == "raw"])
    hs = hband[rawmask].std()
    hband /= hs
    print("raw relief band sigma %.1f-%.1f px, std of rel-luma band %.5f (normalised to 1)" % (S_LO, S_HI, hs))
    # ---- chiseled: canonical-frame phase and folded colour profile ----------------------
    per = light["period_px_mean"]
    gfaces = {g["id"]: g for g in light["faces"]}
    tph = {p["id"]: p for p in tone["groove_phase"]}
    for mt in meta:
        if mt["type"] != "chiseled" or mt["id"] not in gfaces:
            continue
        g = gfaces[mt["id"]]
        # measured normal (image axes) -> y-up direction of +u as measured
        u_meas_up = (-g["normal_img_deg"]) % 360.0
        rp2 = tph[mt["id"]]["relphase2_deg"]
        # canonical +u is the direction along which the 2nd-harmonic relative phase is +
        u_can_up = u_meas_up if rp2 > 0 else (u_meas_up + 180.0) % 360.0
        rho = (u_can_up) % 360.0          # canonical +x rotated by rho (y-up, CCW)
        rho_r = round(rho / 60.0) * 60 % 360
        X0, Y0, X1, Y1 = mt["bbox"]
        m = clean[Y0:Y1, X0:X1] & (owner[Y0:Y1, X0:X1] == mt["id"])
        yy, xx = np.nonzero(m)
        dx = xx + X0 + 0.5 - mt["cx"]; dy = yy + Y0 + 0.5 - mt["cy"]
        t = np.deg2rad(u_can_up)
        # +u in image axes: (cos t, -sin t)
        u = (dx * np.cos(t) - dy * np.sin(t)) / per
        v = Yc[Y0:Y1, X0:X1][m]
        v = v / v.mean() - 1.0
        c1 = (v * np.exp(-2j * np.pi * u)).mean()
        c2 = (v * np.exp(-4j * np.pi * u)).mean()
        crest = float((-np.angle(c1) / (2 * np.pi)) % 1.0)      # u (periods) of fundamental max
        ph = np.mod(u, 1.0)
        b = np.minimum((ph * FOLD_BINS).astype(int), FOLD_BINS - 1)
        cnt = np.bincount(b, minlength=FOLD_BINS)
        fold = []
        for ch in range(3):
            vv = corr[Y0:Y1, X0:X1, ch][m]
            f = np.bincount(b, weights=vv, minlength=FOLD_BINS) / np.maximum(cnt, 1)
            fold.append((f / vv.mean() - 1.0).tolist())
        mt.update({"u_can_up": u_can_up, "rho_src": int(rho_r), "rho_src_exact": rho,
                   "crest_phase": crest, "c1": abs(c1), "c2_rel": abs(c2) / abs(c1),
                   "relphase2": float(np.degrees(np.angle(c2 * np.conj(c1) ** 2))),
                   "fold_rel_rgb": fold})
        print("chiseled src %2d: rho %3d (exact %.1f)  crest %.3f  |c1| %.4f  c2/c1 %.3f  rel %+.1f"
              % (mt["id"], rho_r, rho, crest, abs(c1), abs(c2) / abs(c1), mt["relphase2"]))
    np.save(out_path("_work", "src_corr.npy"), corr.astype(np.float32))
    np.save(out_path("_work", "src_lp.npy"), lp.astype(np.float32))
    np.save(out_path("_work", "src_owner.npy"), owner)
    np.save(out_path("_work", "src_clean.npy"), clean)
    np.save(out_path("_work", "src_hband.npy"), hband.astype(np.float32))
    np.save(out_path("_work", "src_rel.npy"), rel.astype(np.float32))
    json.dump({"ppi_render": ppi_r, "clean_px": CLEAN_PX, "period_px": per,
               "period_in": per / ppi_r, "raw_band_sigma_px": [S_LO, S_HI],
               "raw_band_rel_std": hs, "faces": meta,
               "band_ratio_raw_over_matte": {"edges_cyc_per_px": edges.tolist(),
                                             "ratio": (pr / pm).tolist()}},
              open(out_path("_work", "sources.json"), "w"), indent=1)
    print("ppi_render %.3f px/in, groove period %.4f px = %.5f in = %.3f mm"
          % (ppi_r, per, per / ppi_r, per / ppi_r * 25.4))


if __name__ == "__main__":
    sys.exit(main())
