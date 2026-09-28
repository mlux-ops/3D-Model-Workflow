"""Production step c01: measure how irregular the Chiseled ridges are, in the render and in
the lifestyle image, so the rebuilt grooves can be roughened by a measured amount.

Method (the same for both images): take a patch of one Chiseled face, find its groove wave
vector, demodulate the relative luminance at the groove fundamental, low-pass the complex
result over ~1 period, and read
  amp_cv    std / mean of the local fundamental amplitude (ridge strength varying along a ridge,
            i.e. weak or broken stretches)
  phase_sd  circular std of the local phase in periods (ridges wandering sideways)
A white-noise patch with the same spectrum level is demodulated the same way, so the noise floor
is known. Results go to _work/ridge_irregularity.json; patch views to _work/ridge_patches.png.
"""
import json

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from guard import RENDER_PATH, LIFESTYLE_PATH, out_path, save_image

SIGMA_PERIODS = 0.8


def luma(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def wave_vector(r):
    """Dominant (kx, ky) in cycles/px of a detrended patch, refined by a parabolic peak fit."""
    h, w = r.shape
    win = np.outer(np.hanning(h), np.hanning(w))
    F = np.abs(np.fft.fftshift(np.fft.fft2((r - r.mean()) * win))) ** 2
    cy, cx = h // 2, w // 2
    yy, xx = np.mgrid[0:h, 0:w]
    rad = np.hypot((yy - cy) / h, (xx - cx) / w)
    F[rad < 0.06] = 0          # periods longer than ~16 px are not grooves
    F[rad > 0.40] = 0
    F[:, :cx] = 0              # keep one half-plane (the spectrum is symmetric)
    py, px = np.unravel_index(np.argmax(F), F.shape)

    def refine(a, b, c):
        d = a - 2 * b + c
        return 0.0 if d == 0 else 0.5 * (a - c) / d
    dy = refine(F[py - 1, px], F[py, px], F[py + 1, px])
    dx = refine(F[py, px - 1], F[py, px], F[py, px + 1])
    return (px + dx - cx) / w, (py + dy - cy) / h


def demod_stats(r, m, k):
    kx, ky = k
    period = 1.0 / np.hypot(kx, ky)
    h, w = r.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    z = r * np.exp(-2j * np.pi * (kx * xx + ky * yy)) * m
    s = SIGMA_PERIODS * period
    den = ndi.gaussian_filter(m.astype(np.float64), s)
    A = (ndi.gaussian_filter(z.real, s) + 1j * ndi.gaussian_filter(z.imag, s)) / np.maximum(den, 1e-6)
    inner = ndi.binary_erosion(m, iterations=int(3 * s) + 1)
    a = np.abs(A)[inner]
    ph = A[inner] / np.maximum(np.abs(A[inner]), 1e-12)
    R = np.abs(ph.mean())
    phase_sd = np.sqrt(-2 * np.log(max(R, 1e-9))) / (2 * np.pi)
    return {"period_px": float(period), "amp_mean": float(a.mean()), "amp_cv": float(a.std() / a.mean()),
            "phase_sd_periods": float(phase_sd), "n": int(inner.sum())}


def measure(patch_rgb, mask):
    Y = luma(patch_rgb)
    lp = ndi.gaussian_filter(Y, 8.0)
    r = Y / lp - 1.0
    r = np.where(mask, r, 0.0)
    k = wave_vector(r)
    st = demod_stats(r, mask, k)
    # noise floor: white noise with the patch's residual variance, same demodulation
    rng = np.random.default_rng(1)
    hp = r - ndi.gaussian_filter(r, 1.0)
    nz = rng.normal(0, hp[mask].std() if mask.any() else 1.0, r.shape) * mask
    stn = demod_stats(nz, mask, k)
    st["noise_amp_mean"] = stn["amp_mean"]
    st["snr"] = st["amp_mean"] / max(stn["amp_mean"], 1e-12)
    st["k_cyc_per_px"] = [float(k[0]), float(k[1])]
    return st


def main():
    ren = np.asarray(Image.open(RENDER_PATH).convert("RGB")).astype(np.float64) / 255.0
    life = np.asarray(Image.open(LIFESTYLE_PATH).convert("RGB")).astype(np.float64) / 255.0
    src = json.load(open(out_path("_work", "sources.json")))
    owner = np.load(out_path("_work", "src_owner.npy"))
    clean = np.load(out_path("_work", "src_clean.npy"))
    out = {"sigma_periods": SIGMA_PERIODS, "render": {}, "lifestyle": {}}
    views = []
    for f in src["faces"]:
        if f["type"] != "chiseled" or f["frac"] < 0.99:
            continue
        X0, Y0, X1, Y1 = f["bbox"]
        m = clean[Y0:Y1, X0:X1] & (owner[Y0:Y1, X0:X1] == f["id"])
        m = ndi.binary_erosion(m, iterations=6)
        out["render"][str(f["id"])] = measure(ren[Y0:Y1, X0:X1], m)
        if len(views) < 2:
            views.append(ren[Y0:Y1, X0:X1][100:260, 100:260])
    # lifestyle: two shadow-free patches inside the diagonal Chiseled face and one in the
    # vertical Chiseled face above it (native pixel boxes x0, y0, x1, y1; chosen by eye on
    # the native crop, and saved to ridge_patches.png for the record)
    boxes = {"diagonal_a": (687, 720, 847, 880), "diagonal_b": (640, 900, 780, 1040),
             "vertical": (660, 505, 880, 640)}
    for name, (x0, y0, x1, y1) in boxes.items():
        p = life[y0:y1, x0:x1]
        out["lifestyle"][name] = measure(p, np.ones(p.shape[:2], bool))
        views.append(p)
    json.dump(out, open(out_path("_work", "ridge_irregularity.json"), "w"), indent=1)
    # patch sheet at 3x
    tiles = [Image.fromarray((np.clip(v, 0, 1) * 255).astype(np.uint8)).resize((v.shape[1] * 2, v.shape[0] * 2), Image.NEAREST) for v in views]
    wsum = sum(t.size[0] for t in tiles) + 8 * len(tiles)
    sheet = Image.new("RGB", (min(wsum, 1600), max(t.size[1] for t in tiles)), (255, 255, 255))
    x = 0
    for t in tiles:
        sheet.paste(t, (x, 0))
        x += t.size[0] + 8
    sheet.thumbnail((800, 800))
    save_image(sheet, "_work", "ridge_patches.png")
    for grp in ("render", "lifestyle"):
        for k, v in out[grp].items():
            print("%-9s %-10s period %.2f px  amp_cv %.3f  phase_sd %.3f per  snr %.1f" % (
                grp, k, v["period_px"], v["amp_cv"], v["phase_sd_periods"], v["snr"]))


if __name__ == "__main__":
    main()
