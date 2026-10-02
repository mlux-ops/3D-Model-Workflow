"""Step 09: Matte and Chiseled source pools (source pixels only).

Matte: RGB of each complete Matte hexagon, face mean removed, mirror-extended past the hexagon
       edge (an isotropic cloudiness field, so a mirror is statistically harmless).
Chiseled: the RGB of each complete Chiseled hexagon is kept whole (the groove pattern in the
       render is irregular: groove width, contrast and continuity all wander, so a rebuilt
       ideal pattern would look synthetic). Beside it a groove component G is stored: the
       luminance restricted to a narrow angular wedge around the groove normal u, covering the
       fundamental, its harmonics and their modulation sidebands. G drives the Chiseled bump
       in step 10, so colour and relief share the same groove positions.
The Chiseled residual after notching the groove harmonics is measured only as a diagnostic:
its angular spectrum follows the groove direction, not the light (s09b/s09d), which is the
reason the Chiseled lands carry no relief of their own."""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, save_npy, save_text, out_path  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402
from s03_faces import hex_dist_inside  # noqa: E402
from s04_chisel_measure import CHISELED  # noqa: E402
from s08_raw_height import (padded_window, freq_grids, LUMW, RAW_WHOLE, NWIN)  # noqa: E402

WEDGE_DEG = 14.0
G_F_LO, G_F_HI = 0.08, 0.60


def band_aniso(w, psi_axis, fband=(0.04, 0.22), half_deg=25.0):
    n = w.shape[0]
    FX, FY, FR = freq_grids(n)
    th = np.arctan2(FY, FX)
    P = np.abs(np.fft.fft2(w)) ** 2
    band = (FR > fband[0]) & (FR < fband[1])
    dpar = np.abs(np.angle(np.exp(2j * (th - np.deg2rad(psi_axis))))) / 2.0
    par = band & (dpar < np.deg2rad(half_deg))
    perp = band & (dpar > np.deg2rad(90.0 - half_deg))
    return float(P[par].mean() / P[perp].mean())


def notch(w, f0, u, sigma=0.006, kmax=3):
    n = w.shape[0]
    FX, FY, FR = freq_grids(n)
    keep = np.ones_like(FR)
    for k in range(1, kmax + 1):
        for s in (1.0, -1.0):
            fx0, fy0 = s * k * f0 * u[0], s * k * f0 * u[1]
            keep *= 1.0 - np.exp(-((FX - fx0) ** 2 + (FY - fy0) ** 2) / (2.0 * sigma ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(w) * keep))


def wedge_pass(w, u, half_deg=WEDGE_DEG, f_lo=G_F_LO, f_hi=G_F_HI, ramp_deg=4.0):
    """Keep only spectral energy within +-half_deg of the axis u, for f in [f_lo, f_hi]."""
    n = w.shape[0]
    FX, FY, FR = freq_grids(n)
    th = np.arctan2(FY, FX)
    du = np.abs(np.degrees(np.angle(np.exp(2j * (th - np.arctan2(u[1], u[0])))) / 2.0))
    ang = np.clip((half_deg + ramp_deg - du) / ramp_deg, 0.0, 1.0)
    ang = 0.5 - 0.5 * np.cos(np.pi * ang)
    rad = np.clip((FR - f_lo) / 0.02, 0, 1) * np.clip((f_hi - FR) / 0.05, 0, 1)
    rad = 0.5 - 0.5 * np.cos(np.pi * rad)
    return np.real(np.fft.ifft2(np.fft.fft2(w) * ang * rad))


def classify(f):
    if f["coherence"] > 0.6:
        return "chiseled"
    return "raw" if f["coherence"] > 0.2 else "matte"


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    F = grid["F_px"]
    psi_axis = json.load(open(out_path("work", "light_axis.json")))["psi_deg"]
    psi_l = json.load(open(out_path("work", "pool_raw_info.json")))["psi_toward_light_deg"]
    rgb = load_srgb(RENDER_PATH)
    meas = json.load(open(out_path("work", "chisel_measure.json")))
    faces = json.load(open(out_path("work", "render_faces_raw.json")))
    complete = [f for f in faces if f["frac_visible"] >= 0.995]
    matte = [(f["i"], f["j"]) for f in complete if classify(f) == "matte"]
    raw = [(f["i"], f["j"]) for f in complete if classify(f) == "raw"]
    chis = [(f["i"], f["j"]) for f in complete if classify(f) == "chiseled"]
    print("complete faces: %d matte, %d raw, %d chiseled" % (len(matte), len(raw), len(chis)))
    assert sorted(raw) == sorted(RAW_WHOLE), raw
    assert sorted(chis) == sorted(sum(CHISELED.values(), [])), chis
    ys, xs = np.mgrid[0:NWIN, 0:NWIN]

    pool_m, mean_m, aniso_m = [], [], []
    for (i, j) in matte:
        win, tw, valid, cen = padded_window(rgb, grid, i, j)
        mu = win[valid].mean(0)
        pool_m.append((win - mu).astype(np.float32))
        mean_m.append(mu)
        wl = (win @ LUMW - (win @ LUMW)[valid].mean()) * tw
        aniso_m.append(band_aniso(wl, psi_axis))
    save_npy(np.stack(pool_m), "work", "pool_matte.npy")
    save_npy(np.array(mean_m), "work", "pool_matte_mean.npy")
    print("Matte control anisotropy (par/perp band power): mean %.2f, range %.2f-%.2f"
          % (np.mean(aniso_m), np.min(aniso_m), np.max(aniso_m)))

    pool_rgb, pool_g, mean_c, info_c = [], [], [], []
    for kind, lst in CHISELED.items():
        for (i, j) in lst:
            m = meas["%s_%d_%d" % (kind, i, j)]
            ang = np.deg2rad(m["line_dir_deg_imgcoords"])
            u = np.array([-np.sin(ang), np.cos(ang)])
            win, tw, valid, cen = padded_window(rgb, grid, i, j)
            mu = win[valid].mean(0)
            wl = ((win @ LUMW) - (win @ LUMW)[valid].mean()) * tw
            G = wedge_pass(wl, u)
            vin = hex_dist_inside(xs - cen[0], ys - cen[1], F) > 14
            resl = notch(wl, 1.0 / m["pitch_px"], u)
            an = band_aniso(resl, psi_axis)
            info_c.append({"kind": kind, "i": i, "j": j, "line_dir_deg": m["line_dir_deg_imgcoords"],
                           "pitch_px": m["pitch_px"], "centre": [float(cen[0]), float(cen[1])],
                           "lum_std": float(wl[vin].std()), "G_std": float(G[vin].std()),
                           "G_p03": float(np.percentile(G[vin], 3)), "G_p97": float(np.percentile(G[vin], 97)),
                           "notched_residual_std": float(resl[vin].std()), "notched_residual_aniso_par_perp": an})
            print("Chiseled %-6s (%2d,%d): lum std %.2f, groove component G std %.2f (p3 %.1f, p97 %.1f), rest %.2f"
                  % (kind, i, j, wl[vin].std(), G[vin].std(), np.percentile(G[vin], 3), np.percentile(G[vin], 97),
                     np.sqrt(max(wl[vin].var() - G[vin].var(), 0.0))))
            pool_rgb.append(win.astype(np.float32))
            pool_g.append(G.astype(np.float32))
            mean_c.append(mu)
    save_npy(np.stack(pool_rgb), "work", "pool_chis_rgb.npy")
    save_npy(np.stack(pool_g), "work", "pool_chis_G.npy")
    save_npy(np.array(mean_c), "work", "pool_chis_mean.npy")
    p3 = float(np.mean([c["G_p03"] for c in info_c]))
    p97 = float(np.mean([c["G_p97"] for c in info_c]))
    print("pooled G percentiles: p3 %.2f  p97 %.2f  (spread %.2f levels)" % (p3, p97, p97 - p3))

    raw_mean = np.array([r["mean_rgb"] for r in json.load(open(out_path("work", "pool_raw_info.json")))["faces"]])
    tones = {"matte": np.array(mean_m), "raw": raw_mean, "chiseled": np.array(mean_c)}
    for t, v in tones.items():
        print("%-9s mean RGB %s   face-to-face std %s" % (t, np.round(v.mean(0), 2), np.round(v.std(0), 2)))
    save_text(json.dumps({"matte": matte, "raw": raw, "chiseled": info_c, "matte_aniso": aniso_m,
                          "G_p03": p3, "G_p97": p97, "wedge_deg": WEDGE_DEG, "G_band_cyc_per_px": [G_F_LO, G_F_HI],
                          "tone_mean_rgb": {t: [float(x) for x in v.mean(0)] for t, v in tones.items()},
                          "tone_face_std": {t: [float(x) for x in v.std(0)] for t, v in tones.items()}}, indent=1),
              "work", "pool_info.json")


if __name__ == "__main__":
    main()
