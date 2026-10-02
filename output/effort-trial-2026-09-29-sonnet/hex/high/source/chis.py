"""Chiseled sources: rotate each source face into a groove-vertical frame, complex-demodulate the groove carrier."""
import json
import os
import pickle
from scipy import ndimage
from srcs import *
from srcs import _im

P_SRC = 6.180                   # groove period in render px (measured, median of 9 faces)
K_SRC = 2 * np.pi / P_SRC
FRAME = 344                     # frame size in render px
SIG_C = 3.6                     # demodulation envelope sigma (px)
GM = json.load(open(RUN + "/work/groove_meas.json"))


def frame_coords(cx, cy, ang_deg):
    a = np.deg2rad(ang_deg)
    u = np.array([np.cos(a), np.sin(a)])
    v = np.array([-np.sin(a), np.cos(a)])
    s = np.arange(FRAME) - FRAME / 2 + 0.5
    S, T = np.meshgrid(s, s, indexing="ij")     # rows = s (along grooves), cols = t (across)
    X = cx + S * u[0] + T * v[0]
    Y = cy + S * u[1] + T * v[1]
    return S, T, X, Y


def build_chiseled():
    recs = []
    for g in GM:
        h = [q for q in HEXES if q["i"] == g["i"] and q["j"] == g["j"]][0]
        S, T, X, Y = frame_coords(h["cx"], h["cy"], g["dir"])
        lum = ndimage.map_coordinates(LUM, [Y, X], order=1, mode="nearest")
        rgb = np.stack([ndimage.map_coordinates(_im[..., c], [Y, X], order=1, mode="nearest") for c in range(3)], -1)
        # valid mask: inside inset module hexagon in image coordinates
        dx = np.abs(X - h["cx"]); dy = np.abs(Y - h["cy"])
        ap = SQ3 * RR * INSET_R / 2
        m = (dy <= ap) & (SQ3 * dx + dy <= SQ3 * RR * INSET_R)
        base = gauss_masked(lum, m, 10.0)
        lbp = lum - base
        carrier = np.exp(-1j * K_SRC * T)
        c1 = 2 * gauss_masked((lbp * carrier).real, m, SIG_C) + 2j * gauss_masked((lbp * carrier).imag, m, SIG_C)
        c2 = 2 * gauss_masked((lbp * carrier ** 2).real, m, SIG_C * 1.6) + 2j * gauss_masked((lbp * carrier ** 2).imag, m, SIG_C * 1.6)
        periodic = (c1 * np.exp(1j * K_SRC * T)).real
        resid = lbp - periodic
        alb = gauss_masked(rgb, m, 10.0)
        recs.append(dict(i=g["i"], j=g["j"], dir=g["dir"], mask=m, c1=c1, c2=c2, resid=resid, albedo=alb, lum=lum, rgb=rgb))
    return recs


def load_or_build(force=False):
    p = RUN + "/work/chis_cache.pkl"
    if os.path.exists(p) and not force:
        return pickle.load(open(p, "rb"))
    d = build_chiseled()
    pickle.dump(d, open(guard(p), "wb"))
    return d


if __name__ == "__main__":
    d = load_or_build(force=True)
    num = 0j
    den = 0.0
    amps = []
    for r in d:
        m = r["mask"]
        c1, c2 = r["c1"][m], r["c2"][m]
        num += (c2 * np.conj(c1) ** 2).sum()
        den += (np.abs(c1) ** 3).sum()
        amps.append(np.abs(c1).mean())
    rho = num / den
    print("second-harmonic ratio |rho2|=%.3f  phase=%.1f deg" % (abs(rho), np.rad2deg(np.angle(rho))))
    print("mean |c1| per face:", np.round(amps, 2))
    allr = np.concatenate([r["resid"][r["mask"]] for r in d])
    allp = np.concatenate([np.abs(r["c1"][r["mask"]]) for r in d])
    print("residual std %.2f  |c1| mean %.2f  median %.2f  p10 %.2f p90 %.2f" % (allr.std(), allp.mean(), np.median(allp), *np.percentile(allp, [10, 90])))
    json.dump({"rho2": [float(rho.real), float(rho.imag)], "c1_median": float(np.median(allp)), "resid_std": float(allr.std()),
               "P_src": P_SRC}, open(guard(RUN + "/work/chis_stats.json"), "w"))
    # phase-wobble statistic: std of the phase gradient along s (deg per px) where amplitude is healthy
    ph_std = []
    for r in d:
        m = r["mask"] & (np.abs(r["c1"]) > np.median(allp) * 0.6)
        ph = np.angle(r["c1"])
        dph = np.angle(np.exp(1j * (ph[1:] - ph[:-1])))
        mm = m[1:] & m[:-1]
        ph_std.append(np.rad2deg(dph[mm].std()))
    print("phase step along groove (deg/px) std:", np.round(ph_std, 1))
