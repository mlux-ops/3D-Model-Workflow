"""Production step c02: compare Chiseled ridge roughness in an atlas against the lifestyle image.

Both are judged as SHADING images under raking light, because that is all the lifestyle
image offers. For each Chiseled patch:
  r         relative luminance (patch / its 8 px low-pass - 1)
  periodic  local reconstruction of the groove fundamental + 2nd harmonic (demodulated,
            low-passed over 0.8 period)
  ratio     std(r - periodic) / (2 x mean local fundamental amplitude)
            = how strong the non-periodic roughness is against the groove stripes themselves.
The atlas is shaded by one Lambert routine with the light at the same angle to the grooves
as in the lifestyle patch (15 deg elevation), then resampled so its groove period equals the
lifestyle's. Usage: python c02_ridge_roughness_ratio.py [Color.png Bump16.png face_ids.png report.json]
(defaults: this folder's textures/). Prints the lifestyle ratio and the atlas ratio per face.
"""
import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from guard import LIFESTYLE_PATH, out_path
from c01_measure_ridge_irregularity import luma, wave_vector

Image.MAX_IMAGE_PIXELS = None
SIG = 0.8
LIFE_BOX = (687, 720, 847, 880)           # diagonal_a from c01 (clean, shadow-free)
LIGHT_AZ_LIFE_DEG = 180.0                 # lifestyle light comes from the left (window side)
ELEV = 15.0
H_RANGE_MM = 2.60
PPI = 64.0


def ratio(r, m, k):
    kx, ky = k
    period = 1.0 / np.hypot(kx, ky)
    h, w = r.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    ph = 2 * np.pi * (kx * xx + ky * yy)
    s = SIG * period
    den = np.maximum(ndi.gaussian_filter(m.astype(np.float64), s), 1e-6)
    rec = np.zeros_like(r)
    amp1 = None
    for n in (1, 2):
        z = r * np.exp(-1j * n * ph) * m
        A = (ndi.gaussian_filter(z.real, s) + 1j * ndi.gaussian_filter(z.imag, s)) / den
        rec += 2 * np.real(A * np.exp(1j * n * ph))
        if n == 1:
            amp1 = np.abs(A)
    inner = ndi.binary_erosion(m, iterations=int(3 * s) + 1)
    res = (r - rec)[inner]
    return float(res.std() / (2 * amp1[inner].mean())), float(period)


def rel(Y, m):
    den = np.maximum(ndi.gaussian_filter(m.astype(np.float64), 8.0), 1e-6)
    lp = ndi.gaussian_filter(Y * m, 8.0) / den
    return np.where(m, Y / np.maximum(lp, 1e-6) - 1.0, 0.0)


def shade(h_px, az_deg):
    gy, gx = np.gradient(h_px)
    n = np.dstack([-gx, -gy, np.ones_like(h_px)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    el, az = np.radians(ELEV), np.radians(az_deg)
    L = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    return 0.3 + 0.7 * np.clip(n @ L, 0, None) / np.sin(el)


def main():
    args = sys.argv[1:]
    if args:
        cpath, bpath, fpath, rpath = args
    else:
        cpath, bpath, fpath, rpath = (out_path("textures", n) for n in ("Color.png", "Bump16.png", "face_ids.png", "report.json"))
    life = np.asarray(Image.open(LIFESTYLE_PATH).convert("RGB")).astype(np.float64) / 255.0
    x0, y0, x1, y1 = LIFE_BOX
    Yl = luma(life[y0:y1, x0:x1])
    ml = np.ones(Yl.shape, bool)
    rl = rel(Yl, ml)
    kl = wave_vector(rl)
    R_life, P_life = ratio(rl, ml, kl)
    # angle between the lifestyle light azimuth and its groove normal (image axes, y down)
    n_life = np.degrees(np.arctan2(kl[1], kl[0]))
    d_ang = LIGHT_AZ_LIFE_DEG - n_life
    print("lifestyle: period %.2f px, groove normal %.1f deg, light-normal offset %.1f deg, ratio %.3f" % (P_life, n_life, d_ang, R_life))
    col = np.asarray(Image.open(cpath).convert("RGB")).astype(np.float64) / 255.0
    b = np.asarray(Image.open(bpath)).astype(np.float64) / 65535.0 * H_RANGE_MM / 25.4 * PPI   # height in px
    ids = np.asarray(Image.open(fpath)).astype(np.int32)
    rep = json.load(open(rpath, encoding="utf-8"))
    chis = [f["index"] for f in rep["faces"] if f["type"] == "chiseled"]
    out = {"lifestyle_ratio": R_life, "faces": {}}
    Hh, Ww = ids.shape
    for k in chis:
        yy, xx = np.nonzero(ids == k)
        ay = np.angle(np.exp(2j * np.pi * yy / Hh).mean()) / (2 * np.pi) * Hh
        ax = np.angle(np.exp(2j * np.pi * xx / Ww).mean()) / (2 * np.pi) * Ww
        cy, cx = int(round(ay)) % Hh, int(round(ax)) % Ww
        S = 300
        ys = np.arange(cy - S // 2, cy + S // 2) % Hh
        xs = np.arange(cx - S // 2, cx + S // 2) % Ww
        m = ids[np.ix_(ys, xs)] == k
        hp_ = b[np.ix_(ys, xs)]
        Yc = luma(col[np.ix_(ys, xs)])
        # atlas groove normal from its own spectrum, then light at the lifestyle's offset
        ka = wave_vector(rel(hp_ - hp_.mean() + 100.0, m))
        n_at = np.degrees(np.arctan2(ka[1], ka[0]))
        sh = shade(hp_, n_at + d_ang) * Yc
        # resample so the atlas period equals the lifestyle period
        p_at = 1.0 / np.hypot(*ka)
        z = P_life / p_at
        shz = ndi.zoom(ndi.gaussian_filter(sh, max(0.0, 0.5 / z - 0.5)), z, order=1)
        mz = ndi.zoom(m.astype(np.float64), z, order=0) > 0.5
        rz = rel(shz, mz)
        R, P = ratio(rz, mz, wave_vector(rz))
        out["faces"][k] = R
        print("atlas face %2d: period %.2f px after resample, ratio %.3f" % (k, P, R))
    v = np.array(list(out["faces"].values()))
    print("atlas ratio median %.3f (min %.3f, max %.3f) vs lifestyle %.3f" % (np.median(v), v.min(), v.max(), R_life))
    return out


if __name__ == "__main__":
    main()
