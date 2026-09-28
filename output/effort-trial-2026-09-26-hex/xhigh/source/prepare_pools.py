"""Prepare source pools from the orthographic layout render.

Inputs: the render, _work/render_lattice.json, render_cell_stats.json, render_measure.json,
render_owner.npy, render_edge_d.npy (from analyze_lattice.py, classify_render.py,
measure_fft.py).

Outputs (_work/pools.npz + _work/pools.json):
  * per-pixel colour residual (render colour minus the render's global illumination trend,
    minus the source face's own mean), so blocks from different source faces can be
    stitched without tone jumps; per-face tone offsets are kept separately
  * raw relief source (band-passed luminance, bright = high), matte micro-relief source
  * pool masks per face type (interior > MARGIN px from the joint centreline)
  * joint colour, per-type mean colours, face tone offsets
  * chiseled profile fit (profile exponent gamma, in-phase albedo amplitude)
"""
import os
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from guard import inp, write_text, WORK_DIR, safe

MARGIN = 5.0          # render px from the joint centreline excluded from pools (joint line ~2 px + AA);
                      # the refit lattice's edge colour profile is flat from 1.5 px outward

R = np.asarray(Image.open(inp("elm_formed_hex_sand_layout_render.webp")).convert("RGB")).astype(np.float64)
Hr, Wr, _ = R.shape
L = json.load(open(os.path.join(WORK_DIR, "render_lattice.json")))
S = {"%d,%d" % (s["j"], s["k"]): s for s in json.load(open(os.path.join(WORK_DIR, "render_cell_stats.json")))}
M = json.load(open(os.path.join(WORK_DIR, "render_measure.json")))
owner = np.load(os.path.join(WORK_DIR, "render_owner.npy"))
edge_d = np.load(os.path.join(WORK_DIR, "render_edge_d.npy")).astype(np.float64)
cells = L["cells"]
key = ["%d,%d" % (c["j"], c["k"]) for c in cells]
yy, xx = np.mgrid[0:Hr, 0:Wr].astype(np.float64)


def ctype(s):
    if s["coherence"] > 0.6:
        return "chiseled"
    if s["hp_std"] > 3.0:
        return "raw"
    return "matte"


types = {k: ctype(S[k]) for k in key if k in S}
TYPES = ("matte", "raw", "chiseled")
tcode = {t: i + 1 for i, t in enumerate(TYPES)}
tmap = np.zeros((Hr, Wr), np.int8)
for n, k in enumerate(key):
    if k in types:
        tmap[owner == n] = tcode[types[k]]

# ---------------- global illumination trend of the render ------------------------------
# face means (interior) -> least squares: quadratic in (x, y) + per-type offset
rows, tgt, fkeys = [], [], []
for n, k in enumerate(key):
    if k not in types:
        continue
    sel = (owner == n) & (edge_d > 12)
    if sel.sum() < 20000:          # only faces with most of their interior visible
        continue
    cx, cy = xx[sel].mean() / Wr - 0.5, yy[sel].mean() / Hr - 0.5
    oh = [1.0 if types[k] == t else 0.0 for t in TYPES[1:]]
    rows.append([1, cx, cy, cx * cx, cy * cy, cx * cy] + oh)
    tgt.append(R[sel].mean(axis=0))
    fkeys.append(k)
A, T = np.array(rows), np.array(tgt)
coef, *_ = np.linalg.lstsq(A, T, rcond=None)
pred = A @ coef
print("trend fit residual std per channel", np.round((T - pred).std(axis=0), 2))
X, Y = xx / Wr - 0.5, yy / Hr - 0.5
basis = np.stack([np.ones_like(X), X, Y, X * X, Y * Y, X * Y])
trend = np.einsum("khw,kc->hwc", basis, coef[:6])
trend_mean = trend.reshape(-1, 3).mean(axis=0)
det = R - trend + trend_mean
print("trend range per channel (max-min over render)", np.round(np.ptp(trend.reshape(-1, 3), axis=0), 2))

# ---------------- per-face means, offsets, residual --------------------------------------
face_mean = {}
for n, k in enumerate(key):
    if k not in types:
        continue
    sel = (owner == n) & (edge_d > MARGIN)
    if sel.sum() < 2000:
        continue
    face_mean[k] = det[sel].mean(axis=0)
type_mean = {}
offsets = {}
for t in TYPES:
    ks = [k for k in face_mean if types[k] == t and k in fkeys]
    arr = np.array([face_mean[k] for k in ks])
    type_mean[t] = arr.mean(axis=0)
    offsets[t] = {k: (face_mean[k] - type_mean[t]).tolist() for k in ks}
    print("%-8s n=%2d mean RGB %s  offset std %s" % (t, len(ks), np.round(type_mean[t], 2),
                                                    np.round(arr.std(axis=0), 2)))
resid = np.zeros_like(det)
for n, k in enumerate(key):
    if k in face_mean:
        sel = owner == n
        resid[sel] = det[sel] - face_mean[k]

# ---------------- pool masks and relief sources ------------------------------------------
lum_w = np.array([0.2126, 0.7152, 0.0722])
Yres = resid @ lum_w
inner = edge_d > 3.0


def masked_gauss(img, mask, sigma):
    num = ndi.gaussian_filter(np.where(mask, img, 0.0), sigma)
    den = ndi.gaussian_filter(mask.astype(np.float64), sigma)
    return num / np.maximum(den, 1e-6)


# per type masked filtering so nothing bleeds across joints or between face types
h_raw = np.zeros((Hr, Wr))
h_micro = np.zeros((Hr, Wr))
lowY = np.zeros((Hr, Wr))
for t in TYPES:
    mk = (tmap == tcode[t]) & inner
    # relief bands chosen by calibrate_raw_band.py so the feature scale under raking light matches the
    # lifestyle image (spectral centroid 0.264 / 0.279 cyc/mm vs lifestyle 0.305 / 0.270 for Raw / Matte)
    g05, g3, g12 = (masked_gauss(Yres, mk, s) for s in (0.5, 3.0, 12.0))
    h_raw = np.where(mk, (g05 - g3) + 0.3 * (g3 - g12), h_raw)
    h_micro = np.where(mk, g05 - g3, h_micro)
    lowY = np.where(mk, masked_gauss(Yres, mk, 3.0), lowY)
pool = {t: (tmap == tcode[t]) & (edge_d > MARGIN) for t in TYPES}
stats = {}
for t in TYPES:
    stats[t] = {"pool_px": int(pool[t].sum()),
                "h_raw_std": float(h_raw[pool[t]].std()), "h_micro_std": float(h_micro[pool[t]].std()),
                "h_raw_p": np.percentile(h_raw[pool[t]], [0.5, 1, 5, 50, 95, 99, 99.5]).tolist(),
                "Yres_std": float(Yres[pool[t]].std()), "lowY_std": float(lowY[pool[t]].std())}
    print(t, {k: (np.round(v, 3) if not isinstance(v, list) else np.round(v, 2).tolist()) for k, v in stats[t].items()})

# ---------------- joint colour --------------------------------------------------------------
core = edge_d < 1.0
lum = R @ lum_w
thr = np.percentile(lum[core], 20)
joint_rgb = np.median(R[core & (lum <= thr)], axis=0)
print("joint colour (darkest 20 %% of centreline pixels, median):", np.round(joint_rgb, 1))

# ---------------- chiseled profile fit -----------------------------------------------------
# luminance across grooves = a * h'(phi) + b * h(phi) + c, h = ((1 + cos 2 pi phi) / 2) ** gamma,
# blurred by the render's sampling (gaussian, sigma 0.75 render px), fitted jointly over faces.
ch = M["chiseled"]
nb = 48


def model_profile(gamma, sig_frac):
    ph = (np.arange(nb) + 0.5) / nb
    h = ((1 + np.cos(2 * np.pi * ph)) / 2.0) ** gamma
    # circular gaussian blur
    k = np.fft.rfftfreq(nb, 1.0 / nb)
    hb = np.fft.irfft(np.fft.rfft(h) * np.exp(-0.5 * (2 * np.pi * k * sig_frac) ** 2), nb)
    return hb


profiles = {}
for k, m in ch.items():
    s = S[k]
    n = key.index(k)
    cx, cy = cells[n]["cx"], cells[n]["cy"]
    normal = np.radians(m["groove_deg_img"] - 90.0)
    sel = (owner == n) & (edge_d > 12)
    u = (xx[sel] - cx) * np.cos(normal) + (yy[sel] - cy) * np.sin(normal)
    ph = (u / m["period_px"]) % 1.0
    v = (resid @ lum_w)[sel]
    b = np.floor(ph * nb).astype(int) % nb
    prof = np.bincount(b, weights=v, minlength=nb) / np.maximum(np.bincount(b, minlength=nb), 1)
    profiles[k] = prof
best = None
gamma_curve = {}
for gamma in np.arange(0.3, 2.01, 0.05):
    for sig_px in (0.6, 0.9):
        tot = 0.0
        fits = {}
        for k, prof in profiles.items():
            sf = sig_px / ch[k]["period_px"]
            hb = model_profile(gamma, sf)
            dh = (np.roll(hb, -1) - np.roll(hb, 1)) / 2.0
            bestk = None
            for sh in range(nb):
                h_s, d_s = np.roll(hb, sh), np.roll(dh, sh)
                Am = np.stack([d_s, h_s - h_s.mean(), np.ones(nb)], 1)
                c, res, *_ = np.linalg.lstsq(Am, prof, rcond=None)
                r = ((Am @ c - prof) ** 2).sum()
                if bestk is None or r < bestk[0]:
                    bestk = (r, sh, c)
            tot += bestk[0]
            fits[k] = bestk
        gamma_curve.setdefault(round(float(gamma), 2), []).append(tot)
        if best is None or tot < best[0]:
            best = (tot, gamma, sig_px, fits)
tot, gamma, sig_px, fits = best
var_tot = sum(((p - p.mean()) ** 2).sum() for p in profiles.values())
gamma_r2 = {g: round(1 - min(v) / var_tot, 5) for g, v in gamma_curve.items()}
print("profile fit R^2 by exponent:", {g: gamma_r2[g] for g in (0.5, 0.75, 1.0, 1.25, 1.5, 1.65, 2.0) if g in gamma_r2})
b_amp = np.median([abs(f[2][1]) for f in fits.values()])
b_sign = np.sign(np.median([f[2][1] for f in fits.values()]))
print("chiseled profile fit: gamma %.2f  blur %.1f px  R^2 %.3f  in-phase (albedo/AO) amplitude %.2f levels, sign %+d"
      % (gamma, sig_px, 1 - tot / var_tot, b_amp, b_sign))
# how much of the modulation is in-phase (albedo) vs derivative (shading)
for k, f in fits.items():
    print("   %s shading coef %+.2f  in-phase coef %+.2f" % (k, f[2][0], f[2][1]))

np.savez_compressed(safe(os.path.join(WORK_DIR, "pools.npz")),
                    resid=resid.astype(np.float32), h_raw=h_raw.astype(np.float32),
                    h_micro=h_micro.astype(np.float32), lowY=lowY.astype(np.float32),
                    pool_matte=pool["matte"], pool_raw=pool["raw"], pool_chiseled=pool["chiseled"],
                    owner=owner.astype(np.int16))
info = {"margin_px": MARGIN, "types": types, "type_mean_rgb": {t: v.tolist() for t, v in type_mean.items()},
        "face_offsets": offsets, "trend_coef": coef.tolist(), "trend_range": np.ptp(trend.reshape(-1, 3), axis=0).tolist(),
        "joint_rgb": joint_rgb.tolist(), "stats": stats, "keys": key,
        "chiseled_fit": {"gamma": float(gamma), "blur_px": float(sig_px), "r2": float(1 - tot / var_tot),
                         "r2_by_gamma": {str(g): v for g, v in gamma_r2.items()},
                         "inphase_amp_levels": float(b_amp), "inphase_sign": float(b_sign),
                         "per_face": {k: {"shading": float(f[2][0]), "inphase": float(f[2][1])} for k, f in fits.items()}},
        "chiseled_measure": ch}
write_text(os.path.join(WORK_DIR, "pools.json"), json.dumps(info, indent=1))
