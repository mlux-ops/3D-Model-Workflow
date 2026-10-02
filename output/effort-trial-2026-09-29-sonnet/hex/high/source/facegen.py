"""Per-face texture generators (colour + height in mm) built from render source pixels by quilting."""
import json
from scipy import ndimage
import srcs
import chis
from srcs import *
from synth import quilt

WT, HT = 800, 700                                   # face window at atlas scale (px)
WS, HS = int(np.ceil(WT / F_UP)) + 2, int(np.ceil(HT / F_UP)) + 2   # same window at render scale

# ---- relief design values (mm). Pattern depth and joint depth are separate terms.
RAW_SIGMA_MM = 0.17          # raw relief rms; 1..99 percentile span ~ 0.8 mm
CHIS_GROOVE_PP_MM = 0.50     # chiseled groove peak-to-valley of the fundamental
CHIS_RESID_MM = 0.035       # chiseled organic roughness rms (source residual)
MATTE_SIGMA_MM = 0.015       # matte micro relief rms
JOINT_DEPTH_MM = 1.6
CHIS_COLOUR_GAIN = 0.06      # groove shading in colour, fraction of albedo at the ridge/valley

_cache = {}
_USED = {"matte": {}, "raw": {}, "chis": {}}      # source-area usage shared by all faces of a type (cross-face reuse penalty)
REUSE_W = 0.3


def reset_usage():
    for d in _USED.values():
        d.clear()


def _sources():
    if "s" in _cache:
        return _cache["s"]
    d = srcs.load_or_build()
    out = {}
    # ---- matte
    mat = d["matte"]
    mean_m = np.concatenate([r["rgb"][r["mask"]] for r in mat]).mean(0)
    out["matte_mean"] = mean_m
    out["matte"] = [((r["rgb"] - mean_m).astype(np.float32), r["mask"]) for r in mat]
    out["matte_lab"] = ["i%dj%d" % (r["i"], r["j"]) for r in mat]
    # ---- raw
    raws = d["raw"]
    s_sfs = np.concatenate([r["sfs"][r["mask"]] for r in raws]).std()
    s_lbp = np.concatenate([r["lbp"][r["mask"]] for r in raws]).std()
    comb = [0.6 * r["sfs"] / s_sfs + 0.4 * r["lbp"] / s_lbp for r in raws]
    allc = np.concatenate([c[r["mask"]] for c, r in zip(comb, raws)])
    cm, cs = allc.mean(), allc.std()
    mean_a = np.concatenate([r["albedo"][r["mask"]] for r in raws]).mean(0)
    alum = np.concatenate([(r["albedo"][r["mask"]] - mean_a).mean(1) for r in raws]).std()
    out["raw_mean"] = mean_a
    out["raw_alb_std"] = alum
    w_alb = 0.35 / max(alum, 1e-3)
    out["raw"] = []
    out["raw_lab"] = ["i%dj%d" % (r["i"], r["j"]) for r in raws]
    for c, r in zip(comb, raws):
        arr = np.concatenate([((c - cm) / cs)[..., None], (r["albedo"] - mean_a) * w_alb], -1).astype(np.float32)
        out["raw"].append((arr, r["mask"]))
    out["raw_w_alb"] = w_alb
    # ---- chiseled
    ch = chis.load_or_build()
    med = np.median(np.concatenate([np.abs(r["c1"][r["mask"]]) for r in ch]))
    rs = np.concatenate([r["resid"][r["mask"]] for r in ch]).std()
    mean_c = np.concatenate([r["albedo"][r["mask"]] for r in ch]).mean(0)
    calum = np.concatenate([(r["albedo"][r["mask"]] - mean_c).mean(1) for r in ch]).std()
    out["chis_mean"] = mean_c
    out["chis_alb_w"] = 0.25 / max(calum, 1e-3)
    out["chis_med"] = med
    out["chis"] = []
    out["chis_lab"] = ["i%dj%d" % (r["i"], r["j"]) for r in ch]
    for r in ch:
        arr = np.concatenate([(r["c1"].real / med)[..., None], (r["c1"].imag / med)[..., None], (r["resid"] / rs)[..., None],
                              (r["albedo"] - mean_c) * (0.25 / max(calum, 1e-3))], -1).astype(np.float32)
        out["chis"].append((arr, r["mask"]))
    st = json.load(open(RUN + "/work/chis_stats.json"))
    out["rho2"] = complex(st["rho2"][0], st["rho2"][1])
    _cache["s"] = out
    return out


def summ(prov, labels):
    cnt = {}
    for pr in prov:
        cnt[labels[pr[2]]] = cnt.get(labels[pr[2]], 0) + 1
    return cnt


def up(a, size=(WT, HT)):
    """bicubic upsample a (H,W) float array to size (w,h)."""
    im = Image.fromarray(a.astype(np.float32), mode="F").resize(size, Image.BICUBIC)
    return np.asarray(im)


def up3(a, size=(WT, HT)):
    return np.stack([up(a[..., c], size) for c in range(a.shape[2])], -1)


def unsharp(a, s, amt):
    return a + amt * (a - ndimage.gaussian_filter(a, s))


def gen_matte(rng):
    S = _sources()
    q, prov = quilt(S["matte"], (HS, WS), 72, 20, rng, n_cand=120, weights=[1, 1, 1], used=_USED["matte"], reuse_w=REUSE_W)
    rgb = S["matte_mean"] + q                                   # render-scale colour
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    hp = lum - ndimage.gaussian_filter(lum, 3.0)
    hp = hp / 1.5
    col = up3(rgb)
    h = MATTE_SIGMA_MM * up(hp)
    return col.astype(np.float32), h.astype(np.float32), summ(prov, S["matte_lab"])


def gen_raw(rng):
    S = _sources()
    q, prov = quilt(S["raw"], (HS, WS), 64, 20, rng, n_cand=140, weights=[1.0, 1, 1, 1], used=_USED["raw"], reuse_w=REUSE_W)
    z = q[..., 0]
    alb = q[..., 1:4] / S["raw_w_alb"]
    z = (z - z.mean())
    zt = unsharp(up(z), 1.6, 0.5)                                # gentle sharpening after 2.06x upsampling
    zt = zt / zt.std()
    h = RAW_SIGMA_MM * zt
    # cavity darkening: recesses are a little darker, rims a little lighter (gain ~ +-2.5 % at +-2 sigma)
    col = S["raw_mean"] + up3(alb)
    col = col * (1 + 0.0125 * np.clip(zt, -3, 3))[..., None]
    return col.astype(np.float32), h.astype(np.float32), summ(prov, S["raw_lab"])


def gen_chis(rng, ang_deg):
    S = _sources()
    q, prov = quilt(S["chis"], (chis.FRAME, chis.FRAME), 56, 16, rng, n_cand=120,
                 weights=[1, 1, 0.35, 1, 1, 1], cplx=[(0, 1)], allowed=("flipud",), used=_USED["chis"], reuse_w=REUSE_W)
    c1 = (q[..., 0] + 1j * q[..., 1])
    res = q[..., 2]
    alb = q[..., 3:6] / S["chis_alb_w"]
    # atlas-scale window coordinates
    ox = np.arange(WT) - WT / 2 + 0.5
    oy = np.arange(HT) - HT / 2 + 0.5
    X, Y = np.meshgrid(ox, oy)
    a = np.deg2rad(ang_deg)
    u = np.array([np.cos(a), np.sin(a)])
    v = np.array([-np.sin(a), np.cos(a)])
    s_t = X * u[0] + Y * u[1]
    t_t = X * v[0] + Y * v[1]
    fr = chis.FRAME
    srow = s_t / F_UP + fr / 2 - 0.5
    tcol = t_t / F_UP + fr / 2 - 0.5
    coords = [srow, tcol]

    def samp(f, order=1):
        return ndimage.map_coordinates(f, coords, order=order, mode="reflect")

    cr, ci = samp(c1.real), samp(c1.imag)
    c = cr + 1j * ci
    amp = np.abs(c)
    e = c / np.maximum(amp, 0.3)
    aa = np.clip(amp ** 0.85, 0.45, 1.55)
    phase0 = float(rng.uniform(0, 2 * np.pi))
    Kt = chis.K_SRC / F_UP
    E = np.exp(1j * (Kt * t_t + phase0))
    rho2 = S["rho2"]
    prof = (e * E).real + (rho2 * (e * E) ** 2).real
    prof = prof / 1.0
    a0 = CHIS_GROOVE_PP_MM / 2.0
    hg = a0 * aa * prof
    resid = unsharp(samp(res, 1), 1.2, 0.4)
    h = hg + CHIS_RESID_MM * resid
    albedo = np.stack([samp(alb[..., k]) for k in range(3)], -1)
    col = S["chis_mean"] + albedo
    col = col * (1 + CHIS_COLOUR_GAIN * np.clip(hg / a0, -1.5, 1.5))[..., None]
    return col.astype(np.float32), h.astype(np.float32), summ(prov, S["chis_lab"])
