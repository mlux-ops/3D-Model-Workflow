"""Build the source libraries from the render: matte residual faces, raw faces (isotropic relief cue + chroma), chiseled amplitude maps, tones.

Channels of the matte / raw libraries (native render resolution, float32):
  0: z   luminance residual (plane removed, band-passed, angular-spectrum equalised for raw), in render levels
  1..3: chroma residual (R,G,B deviations orthogonal to luminance), in render levels
"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage as ndi
import guard
import render_grid as rg

LW = np.array([0.299, 0.587, 0.114])
im = rg.load_render()
H, W = im.shape[:2]
PAD = 230
imp = np.pad(im, ((PAD, PAD), (PAD, PAD), (0, 0)), mode="edge")
valid = np.pad(np.ones((H, W), bool), PAD, constant_values=False)
yy, xx = np.mgrid[0:H + 2 * PAD, 0:W + 2 * PAD].astype(np.float64)
yy -= PAD
xx -= PAD
feats = json.load(open(rg.WORK + "render_faces_raw.json"))
RAD = 178


def ftype(f):
    if f["hf"] > 4.5:
        return "chiseled"
    if f["coh"] > 0.2:
        return "raw"
    return "matte"


def window(f):
    cx, cy = f["cx"], f["cy"]
    y0, x0 = int(round(cy)) + PAD - RAD, int(round(cx)) + PAD - RAD
    sl = (slice(y0, y0 + 2 * RAD + 1), slice(x0, x0 + 2 * RAD + 1))
    d = rg.hex_dist(xx[sl], yy[sl], cx, cy)
    m = (d < 0.93) & valid[sl]
    return sl, d, m


def plane_remove(chan, m, sl):
    """Least-squares plane fit over the mask; returns residual (zero outside mask)."""
    X = xx[sl][m]
    Y = yy[sl][m]
    A = np.stack([X - X.mean(), Y - Y.mean(), np.ones_like(X)], axis=1)
    coef, *_ = np.linalg.lstsq(A, chan[m], rcond=None)
    full = (xx[sl] - X.mean()) * coef[0] + (yy[sl] - Y.mean()) * coef[1] + coef[2]
    return np.where(m, chan - full, 0.0), coef


def norm_gauss(a, m, s):
    return ndi.gaussian_filter(a * m, s) / np.maximum(ndi.gaussian_filter(m.astype(np.float64), s), 1e-6)


lib = {"matte": [], "raw": [], "chiseled": []}
tones = {"matte": [], "raw": [], "chiseled": []}
for f in feats:
    typ = ftype(f)
    if f["visfrac"] < 0.30 and typ != "matte":
        continue
    if f["visfrac"] < 0.12:
        continue
    sl, d, m = window(f)
    if m.sum() < 8000:
        continue
    rgb = imp[sl]
    tone = rgb[m].mean(axis=0)
    tones[typ].append(dict(i=f["i"], j=f["j"], vis=f["visfrac"], rgb=[float(v) for v in tone]))
    lib[typ].append(dict(i=f["i"], j=f["j"], vis=f["visfrac"], sl=sl, m=m, d=d))
for k in lib:
    print(k, "faces in library:", len(lib[k]), " complete:", sum(1 for e in lib[k] if e["vis"] > 0.95))

# ---------------------------------------------------------------- matte + raw residual channels
def base_channels(e, sigma_low, sigma_dn):
    sl, m = e["sl"], e["m"]
    rgb = imp[sl]
    L = rgb @ LW
    Lr, _ = plane_remove(L, m, sl)
    mf = m.astype(np.float64)
    low = norm_gauss(Lr, mf, sigma_low)
    z = ndi.gaussian_filter(np.where(m, Lr - low, 0.0), sigma_dn)
    chroma = []
    for c in range(3):
        r, _ = plane_remove(rgb[..., c], m, sl)
        chroma.append(r)
    chroma = np.stack(chroma, axis=-1)
    Lc = chroma @ LW
    chroma = chroma - Lc[..., None]
    for c in range(3):
        chroma[..., c] = norm_gauss(chroma[..., c], mf, 1.0)
    return z, chroma, Lr


out = {}
# ---- matte: keep the cloud (only remove very-low-frequency plane), light denoise
mats = []
for e in lib["matte"]:
    z, chroma, Lr = base_channels(e, 60.0, 0.5)
    m = e["m"]
    mats.append(dict(i=e["i"], j=e["j"], z=z, chroma=chroma, m=m, vis=e["vis"]))
zs = np.concatenate([e["z"][e["m"]] for e in mats])
print("matte luminance residual std %.3f levels ; p1 %.2f p99 %.2f" % (zs.std(), np.percentile(zs, 1), np.percentile(zs, 99)))
cs = np.concatenate([e["chroma"][e["m"]] for e in mats])
print("matte chroma residual std per channel", np.round(cs.std(axis=0), 3))

# ---- raw: relief cue = band-passed luminance; equalise the angular spectrum
raws = []
for e in lib["raw"]:
    z, chroma, Lr = base_channels(e, 10.0, 0.7)
    raws.append(dict(i=e["i"], j=e["j"], z=z, chroma=chroma, m=e["m"], vis=e["vis"], d=e["d"]))
N = 2 * RAD + 1
fy = np.fft.fftfreq(N)[:, None] * np.ones((1, N))
fx = np.fft.fftfreq(N)[None, :] * np.ones((N, 1))
fr = np.hypot(fx, fy)
th = np.degrees(np.arctan2(fy, fx)) % 180
band = (fr > 1 / 40.0) & (fr < 1 / 3.0)
nb = 12
ang_energy = np.zeros(nb)
for e in raws:
    if e["vis"] < 0.95:
        continue
    tap = np.clip((0.93 - e["d"]) / 0.08, 0, 1)
    S = np.abs(np.fft.fft2(e["z"] * tap)) ** 2
    for b in range(nb):
        sel = band & (th >= b * 180 / nb) & (th < (b + 1) * 180 / nb)
        ang_energy[b] += S[sel].sum()
ang_energy /= ang_energy.sum()
print("raw angular spectrum share per 15deg bin (0 = horizontal wave vector, y down):", np.round(ang_energy * 100, 1))
print("max/min", ang_energy.max() / ang_energy.min())
# smooth periodic gain profile on the circle of orientations
gain_b = np.sqrt((1.0 / nb) / ang_energy)
gain_b = np.clip(gain_b, 0.6, 1.8)
ctr = (np.arange(nb) + 0.5) * 180 / nb
gain_map = np.interp(th, np.concatenate([[ctr[-1] - 180], ctr, [ctr[0] + 180]]), np.concatenate([[gain_b[-1]], gain_b, [gain_b[0]]]))
gain_map = np.where(band, gain_map, 1.0)
print("equalising gain per bin", np.round(gain_b, 2))
for e in raws:
    tap = np.clip((0.93 - e["d"]) / 0.08, 0, 1)
    zf = np.real(np.fft.ifft2(np.fft.fft2(e["z"] * tap) * gain_map))
    e["z_raw"] = e["z"].copy()
    e["z"] = np.where(e["m"], zf / np.maximum(tap, 0.35), 0.0)
zr = np.concatenate([e["z"][e["m"]] for e in raws if e["vis"] > 0.95])
zr0 = np.concatenate([e["z_raw"][e["m"]] for e in raws if e["vis"] > 0.95])
print("raw luminance residual std before %.3f after equalising %.3f ; skew %.3f  p0.5 %.2f p99.5 %.2f" % (zr0.std(), zr.std(), ((zr - zr.mean()) ** 3).mean() / zr.std() ** 3, np.percentile(zr, 0.5), np.percentile(zr, 99.5)))
cr = np.concatenate([e["chroma"][e["m"]] for e in raws])
print("raw chroma residual std per channel", np.round(cr.std(axis=0), 3))
# structure-tensor coherence check after equalising
for e in raws[:3]:
    g = ndi.gaussian_filter(e["z"], 1.0)
    gy_, gx_ = np.gradient(g)
    mm = e["m"]
    jxx, jyy, jxy = (gx_[mm] ** 2).mean(), (gy_[mm] ** 2).mean(), (gx_[mm] * gy_[mm]).mean()
    print(" face i%d j%d coherence after equalising %.3f" % (e["i"], e["j"], np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / (jxx + jyy)))

# ---- chiseled: groove amplitude maps (demodulated at the measured pitch), oriented as in the render
gm = json.load(open(rg.WORK + "groove_measure.json"))
gp = json.load(open(rg.WORK + "groove_profile.json"))
per = gp["period_px"]
chis = []
for e in lib["chiseled"]:
    if e["vis"] < 0.9:
        continue
    f = [g for g in feats if g["i"] == e["i"] and g["j"] == e["j"]][0]
    g = f["gang"] % 180
    wave = min([0.0, 60.0, 120.0], key=lambda a: min(abs((g - a) % 180), 180 - abs((g - a) % 180)))
    k = np.array([np.cos(np.radians(wave)), np.sin(np.radians(wave))]) / per
    sl, m = e["sl"], e["m"]
    L = imp[sl] @ LW
    hp = L - ndi.gaussian_filter(L, 6.0)
    z = hp * np.exp(-2j * np.pi * (k[0] * xx[sl] + k[1] * yy[sl]))
    zs_ = ndi.gaussian_filter(z.real, 3.5) + 1j * ndi.gaussian_filter(z.imag, 3.5)
    a = 2 * np.abs(zs_)
    resid = hp - np.real(2 * zs_ * np.exp(2j * np.pi * (k[0] * xx[sl] + k[1] * yy[sl])))
    tap = np.clip((0.90 - e["d"]) / 0.08, 0, 1)
    Sg = np.fft.fft2(resid * tap)
    for h in (1, 2, 3):
        for sgn in (1, -1):
            Sg[np.hypot(fx - sgn * h * k[0], fy - sgn * h * k[1]) < 0.045] = 0
    grain = ndi.gaussian_filter(np.real(np.fft.ifft2(Sg)), 0.5)
    mg = m & (e["d"] < 0.86)
    gg, gx2 = np.gradient(ndi.gaussian_filter(grain, 1.0))
    coh = np.sqrt(((gx2[mg] ** 2).mean() - (gg[mg] ** 2).mean()) ** 2 + 4 * (gx2[mg] * gg[mg]).mean() ** 2) / ((gx2[mg] ** 2).mean() + (gg[mg] ** 2).mean())
    chis.append(dict(i=e["i"], j=e["j"], amp=a.astype(np.float32), m=m & (e["d"] < 0.90), wave=wave, grain=np.where(m, grain, 0).astype(np.float32)))
    print(" chiseled i%d j%d wave %.0f amp mean %.2f  residual std %.2f  grain (notched) std %.2f coherence %.3f" % (e["i"], e["j"], wave, a[m].mean(), resid[m].std(), grain[mg].std(), coh))

# ---------------------------------------------------------------- save
save = {}
for name, group in (("matte", mats), ("raw", raws)):
    save[name + "_n"] = np.array(len(group))
    for n_, e in enumerate(group):
        save["%s_%d_ch" % (name, n_)] = np.concatenate([e["z"][..., None], e["chroma"]], axis=-1).astype(np.float32)
        save["%s_%d_m" % (name, n_)] = e["m"]
        save["%s_%d_id" % (name, n_)] = np.array([e["i"], e["j"], int(round(e["vis"] * 100))])
save["chis_n"] = np.array(len(chis))
for n_, e in enumerate(chis):
    save["chis_%d_amp" % n_] = e["amp"]
    save["chis_%d_m" % n_] = e["m"]
    save["chis_%d_grain" % n_] = e["grain"]
    save["chis_%d_id" % n_] = np.array([e["i"], e["j"], int(e["wave"])])
np.savez_compressed(guard.safe(rg.WORK + "libs.npz"), **save)

tone_summary = {}
for typ, rows in tones.items():
    if not rows:
        continue
    comp = [r for r in rows if r["vis"] > 0.95] or rows
    arr = np.array([r["rgb"] for r in comp])
    tone_summary[typ] = dict(n=len(comp), mean=arr.mean(axis=0).tolist(), std=arr.std(axis=0).tolist(), cov=np.cov(arr.T).tolist() if len(arr) > 3 else None)
    print(typ, "face-mean RGB mean", np.round(arr.mean(axis=0), 2), "std", np.round(arr.std(axis=0), 2), "n", len(arr))
json.dump(dict(tones=tone_summary, gain_bins=gain_b.tolist(), ang_energy=ang_energy.tolist(), matte_z_std=float(zs.std()), raw_z_std=float(zr.std()), raw_z_std_before=float(zr0.std())),
          open(guard.safe(rg.WORK + "lib_summary.json"), "w"), indent=1)
