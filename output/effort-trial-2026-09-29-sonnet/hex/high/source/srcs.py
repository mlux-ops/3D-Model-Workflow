"""Build texture source stacks from the layout render (render-scale pixels)."""
import json
import pickle
import os
from scipy import ndimage
from common import *

SQ3 = np.sqrt(3.0)
LAT = json.load(open(RUN + "/work/render_lattice.json"))
RR = LAT["R"]                       # circumradius of the module hexagon, render px
HEXES = json.load(open(RUN + "/work/render_hexes.json"))
LIGHT_AXIS = np.deg2rad(json.load(open(RUN + "/work/raw_light_axis.json"))["light_axis_deg"])
RENDER_PPI = SQ3 * RR / 10.125      # render px per real inch (module = 10.125 in across flats)
F_UP = 64.0 / RENDER_PPI            # render px -> atlas px
INSET_R = 0.955                     # source samples are taken inside this fraction of the module hexagon

_im = np.asarray(Image.open(RENDER).convert("RGB")).astype(np.float64)
LUM = _im @ np.array([0.299, 0.587, 0.114])
HH, WW = LUM.shape


def hex_mask_window(cx, cy, r, x0, y0, w, h):
    yy, xx = np.mgrid[y0:y0 + h, x0:x0 + w]
    dx = np.abs(xx - cx)
    dy = np.abs(yy - cy)
    ap = SQ3 * RR * r / 2
    m = (dy <= ap) & (SQ3 * dx + dy <= SQ3 * RR * r)
    m &= (xx >= 0) & (xx < WW) & (yy >= 0) & (yy < HH)
    return m


def window_of(h, half=None):
    half = half or int(RR + 6)
    x0 = int(round(h["cx"])) - half
    y0 = int(round(h["cy"])) - half
    return x0, y0, 2 * half + 1, 2 * half + 1


def crop(arr, x0, y0, w, hh):
    out = np.zeros((hh, w) + arr.shape[2:], dtype=np.float64)
    xs0, ys0 = max(x0, 0), max(y0, 0)
    xs1, ys1 = min(x0 + w, arr.shape[1]), min(y0 + hh, arr.shape[0])
    out[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0] = arr[ys0:ys1, xs0:xs1]
    return out


def classify(h):
    if h["hp_sd"] > 6 and h["coh"] > 0.6:
        return "chiseled"
    if 2.8 < h["hp_sd"] < 5 and h["coh"] > 0.2:
        return "raw"
    return "matte"


def gauss_masked(a, m, s):
    """normalised gaussian convolution of a (H,W[,C]) using mask m."""
    mf = m.astype(np.float64)
    den = ndimage.gaussian_filter(mf, s)
    if a.ndim == 2:
        num = ndimage.gaussian_filter(a * mf, s)
        return num / np.maximum(den, 1e-6)
    return np.stack([ndimage.gaussian_filter(a[..., c] * mf, s) / np.maximum(den, 1e-6) for c in range(a.shape[2])], -1)


def sfs_height(lbp, mtaper):
    """Wiener inverse of a linear shading model along the measured light axis. lbp: band-passed luminance."""
    n = 512
    a = np.zeros((n, n))
    hh, ww = lbp.shape
    a[:hh, :ww] = lbp * mtaper
    F = np.fft.fft2(a)
    fy = np.fft.fftfreq(n)[:, None]
    fx = np.fft.fftfreq(n)[None, :]
    D = 2 * np.pi * (fx * np.cos(LIGHT_AXIS) + fy * np.sin(LIGHT_AXIS))
    eps = 2 * np.pi * 0.03
    H = -F * (-1j * D) / (D ** 2 + eps ** 2)       # -F / (i D), regularised
    h = np.fft.ifft2(H).real[:hh, :ww]
    return h


def build_raw_or_matte():
    out = {"matte": [], "raw": []}
    for h in HEXES:
        t = classify(h)
        if t == "chiseled":
            continue
        x0, y0, w, hh = window_of(h)
        rgb = crop(_im, x0, y0, w, hh)
        lum = crop(LUM, x0, y0, w, hh)
        m = hex_mask_window(h["cx"], h["cy"], INSET_R, x0, y0, w, hh)
        if m.sum() < 8000:
            continue
        rec = dict(i=h["i"], j=h["j"], type=t, x0=x0, y0=y0, mask=m, rgb=rgb, lum=lum, cov=h["cov"])
        if t == "raw":
            mf = ndimage.gaussian_filter(m.astype(np.float64), 5.0)
            mfull = hex_mask_window(h["cx"], h["cy"], 1.0, x0, y0, w, hh)
            base = gauss_masked(lum, mfull, 14.0)
            lbp = ndimage.gaussian_filter(lum, 1.3) - base
            rec["lbp"] = lbp
            rec["sfs"] = sfs_height(lbp, np.clip(mf * 1.0, 0, 1) * (mf > 0.02))
            rec["albedo"] = gauss_masked(rgb, mfull, 8.0)
        out[t].append(rec)
    return out


def load_or_build(force=False):
    p = RUN + "/work/src_cache.pkl"
    if os.path.exists(p) and not force:
        return pickle.load(open(p, "rb"))
    d = build_raw_or_matte()
    pickle.dump(d, open(guard(p), "wb"))
    return d
