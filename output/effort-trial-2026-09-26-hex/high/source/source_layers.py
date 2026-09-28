"""Step 3: per-face source layers from the layout render (render resolution, 31.1 px/in).

Every lattice cell that is at least 10 % visible in the render becomes a pool entry
(full faces and partial edge faces). For each entry:

  colour   render RGB with part of the high-frequency baked shading removed
           (raw 75 %, chiseled 70 %, matte 100 % kept) so that faces can be rotated
           without their baked light direction fighting the bump map.
  height   type-specific, in source units (normalised to mm later in build_atlas.py):
    raw       the render's Raw relief is shaded by a directional light whose axis is
              measured from the structure tensor (lower-left <-> upper-right). The
              high-passed luminance is integrated along that axis in the Fourier
              domain (regularised), giving a height field, plus a small share of the
              luminance itself for the finest grain.
    chiseled  measured groove geometry: dominant frequency vector from a windowed 2-D
              FFT (sub-bin refined), local amplitude and phase by complex
              demodulation, and a groove cross-section profile measured by folding
              the face's own pixels over phase (sub-pixel, 48 bins). The atlas
              re-evaluates that profile at 64 px/in, so grooves stay crisp; the
              residual (source minus groove model) is kept for irregularity.
    matte     fine grain only (difference of Gaussians); Matte stays essentially flat.
"""

import json

import numpy as np
from PIL import Image
from scipy import ndimage

import render_geom as g
from common import RENDER_PATH, hexnorm, out_path

SAFE_N = g.F / 2.0 - 3.0          # render px: face pixels clear of the drawn joint line
LIGHT_GRAD_DEG = 150.0            # y-down image angle of the dominant Raw shading gradient
COLOUR_DETAIL_KEEP = {"raw": 0.75, "chiseled": 0.7, "matte": 1.0}
PROFILE_BINS = 48


def classify(hp_std, coh):
    if coh > 0.6:
        return "chiseled"
    if hp_std > 0.0105:
        return "raw"
    return "matte"


def build():
    rgb = np.asarray(Image.open(RENDER_PATH).convert("RGB")).astype(np.float64) / 255.0
    L = rgb @ np.array([0.2126, 0.7152, 0.0722])
    Hs, Ws = L.shape
    Y, X = np.mgrid[0:Hs, 0:Ws].astype(np.float64)
    dist, bcx, bcy = g.nearest_centre(X, Y)
    safe = dist < SAFE_N

    # enumerate pool entries (every centre whose cell touches the image)
    entries = []
    seen = {}
    for par in (0, 1):
        for c in range(-3, 6):
            for r in range(-3, 8):
                cx = g.X0 + par * g.COLP + c * 2 * g.COLP
                cy = g.Y0 + par * g.F / 2.0 + r * g.F
                key = (round(cx, 1), round(cy, 1))
                if key in seen:
                    continue
                seen[key] = 1
                entries.append([cx, cy])
    idmap = np.full((Hs, Ws), -1, np.int32)
    for k, (cx, cy) in enumerate(entries):
        idmap[(np.abs(bcx - cx) < 0.5) & (np.abs(bcy - cy) < 0.5)] = k
    full_area = 2.0 * np.sqrt(3.0) * (SAFE_N ** 2)      # hexagon area from apothem
    hp = L - ndimage.gaussian_filter(L, 3.0)
    gx = ndimage.sobel(ndimage.gaussian_filter(L, 0.7), axis=1)
    gy = ndimage.sobel(ndimage.gaussian_filter(L, 0.7), axis=0)

    pool = []
    for k, (cx, cy) in enumerate(entries):
        m = (idmap == k) & safe
        frac = m.sum() / full_area
        if frac < 0.10:
            continue
        inner = m & (dist < SAFE_N - 0.3 * g.RPPI)
        a, b, c = (gx[inner] ** 2).sum(), (gy[inner] ** 2).sum(), (gx[inner] * gy[inner]).sum()
        l1 = 0.5 * (a + b + np.sqrt((a - b) ** 2 + 4 * c * c))
        l2 = 0.5 * (a + b - np.sqrt((a - b) ** 2 + 4 * c * c))
        coh = (l1 - l2) / (l1 + l2)
        pool.append({"entry": k, "cx": cx, "cy": cy, "frac": float(min(frac, 1.0)),
                     "full": bool(frac > 0.97), "type": classify(float(hp[inner].std()), float(coh)),
                     "hp_std": float(hp[inner].std()), "coherence": float(coh)})

    colour = np.zeros_like(rgb)
    height = np.zeros((Hs, Ws))
    chis = {}
    zfield = np.zeros((Hs, Ws), np.complex128)
    lowc = np.stack([ndimage.gaussian_filter(rgb[..., i], 4.0) for i in range(3)], -1)

    th = np.radians(LIGHT_GRAD_DEG)
    lx, ly = np.cos(th), np.sin(th)
    pad = 24
    for p in pool:
        k = p["entry"]
        m = (idmap == k) & safe
        ys, xs = np.nonzero(m)
        y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, Hs)
        x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, Ws)
        mw = m[y0:y1, x0:x1]
        typ = p["type"]
        keep = COLOUR_DETAIL_KEEP[typ]
        cw = lowc[y0:y1, x0:x1] + keep * (rgb[y0:y1, x0:x1] - lowc[y0:y1, x0:x1])
        colour[y0:y1, x0:x1][mw] = cw[mw]

        Lw = L[y0:y1, x0:x1]
        # masked high-pass (normalised Gaussian so the joint/neighbours don't leak in)
        wgt = ndimage.gaussian_filter(mw.astype(float), 3.0) + 1e-9
        low = ndimage.gaussian_filter(np.where(mw, Lw, 0.0), 3.0) / wgt
        hpw = np.where(mw, Lw - low, 0.0)
        if typ == "raw":
            h, w = hpw.shape
            fy = np.fft.fftfreq(h)[:, None]
            fx = np.fft.fftfreq(w)[None, :]
            d = 2j * np.pi * (lx * fx + ly * fy)
            k2 = (2 * np.pi) ** 2 * (fx ** 2 + fy ** 2)
            # wider band than the other types: Raw relief has 0.3-0.8 in forms
            wb = ndimage.gaussian_filter(mw.astype(float), 12.0) + 1e-9
            lw12 = ndimage.gaussian_filter(np.where(mw, Lw, 0.0), 12.0) / wb
            sm = ndimage.gaussian_filter(np.where(mw, Lw, 0.0), 0.7) / (ndimage.gaussian_filter(mw.astype(float), 0.7) + 1e-9)
            band_hp = np.where(mw, sm - lw12, 0.0)
            S = np.fft.fft2(band_hp)
            Hf = S * np.conj(d) / (np.abs(d) ** 2 + 0.08 * k2 + 1e-4)
            hh = np.real(np.fft.ifft2(Hf))
            wl = ndimage.gaussian_filter(mw.astype(float), 25.0) + 1e-9
            hh = hh - ndimage.gaussian_filter(np.where(mw, hh, 0.0), 25.0) / wl
            hh = hh / (hh[mw].std() + 1e-12) + 0.15 * hpw / (hpw[mw].std() + 1e-12)
            height[y0:y1, x0:x1][mw] = hh[mw]
        elif typ == "matte":
            dog = ndimage.gaussian_filter(np.where(mw, Lw, 0.0), 0.7) / (ndimage.gaussian_filter(mw.astype(float), 0.7) + 1e-9) - low
            height[y0:y1, x0:x1][mw] = dog[mw]
        else:
            # windowed 2-D FFT of the face's high-pass -> groove frequency vector
            win = ndimage.gaussian_filter(mw.astype(float), 8.0) * mw
            N = 2048
            Fz = np.fft.fft2(hpw * win, s=(N, N))
            P = np.abs(Fz) ** 2
            fyv = np.fft.fftfreq(N)[:, None]
            fxv = np.fft.fftfreq(N)[None, :]
            fr = np.sqrt(fxv ** 2 + fyv ** 2)
            band = (fr > 1 / 8.0) & (fr < 1 / 4.8) & (fxv >= 0)
            Pb = np.where(band, P, 0)
            iy, ix = np.unravel_index(np.argmax(Pb), P.shape)

            def para(a_, b_, c_):
                den = a_ - 2 * b_ + c_
                return 0.0 if den == 0 else 0.5 * (a_ - c_) / den
            dy = para(P[(iy - 1) % N, ix], P[iy, ix], P[(iy + 1) % N, ix])
            dx = para(P[iy, (ix - 1) % N], P[iy, ix], P[iy, (ix + 1) % N])
            fvx = np.fft.fftfreq(N)[ix] + dx / N
            fvy = np.fft.fftfreq(N)[iy] + dy / N
            period = 1.0 / np.hypot(fvx, fvy)
            # grooves run perpendicular to the frequency vector; report CCW (y-up) angle
            groove_deg = (np.degrees(np.arctan2(-fvy, fvx)) + 90.0) % 180.0
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float64)
            carrier = np.exp(-2j * np.pi * (fvx * xx + fvy * yy))
            sig = 1.6 * period
            wz = ndimage.gaussian_filter(mw.astype(float), sig) + 1e-9
            z = (ndimage.gaussian_filter(np.real(hpw * carrier), sig) + 1j * ndimage.gaussian_filter(np.imag(hpw * carrier), sig)) / wz
            phase = 2 * np.pi * (fvx * xx + fvy * yy) + np.angle(z)
            amp = np.abs(z)
            # fold the face's own pixels over phase -> measured groove cross-section
            bins = (np.mod(phase[mw], 2 * np.pi) / (2 * np.pi) * PROFILE_BINS).astype(int) % PROFILE_BINS
            val = hpw[mw] / (amp[mw] + 1e-6)
            prof = np.bincount(bins, weights=val, minlength=PROFILE_BINS) / np.maximum(np.bincount(bins, minlength=PROFILE_BINS), 1)
            prof = prof - prof.mean()
            model = amp * np.interp(np.mod(phase, 2 * np.pi), (np.arange(PROFILE_BINS) + 0.5) / PROFILE_BINS * 2 * np.pi, prof, period=2 * np.pi)
            resid = np.where(mw, hpw - model, 0.0)
            height[y0:y1, x0:x1][mw] = resid[mw]            # residual only; model is re-evaluated at 64 ppi
            zfield[y0:y1, x0:x1][mw] = z[mw]
            ph_pos = (np.argmax(prof) + 0.5) / PROFILE_BINS
            chis[k] = {"f": [float(fvx), float(fvy)], "period_px": float(period), "period_in": float(period / g.RPPI),
                       "period_mm": float(period / g.RPPI * 25.4), "groove_deg": float(groove_deg),
                       "profile": [float(v) for v in prof], "amp_median": float(np.median(amp[mw])),
                       "ridge_phase_frac": float(ph_pos), "resid_std_ratio": float(resid[mw].std() / hpw[mw].std())}
            p.update({k2_: v for k2_, v in chis[k].items() if k2_ != "profile"})

    # extend every layer past the safe face boundary with its nearest safe pixel, so
    # bicubic sampling at the face edge never mixes in the joint line or empty pixels
    _, (iy, ix) = ndimage.distance_transform_edt(~safe, return_indices=True)
    colour = colour[iy, ix]
    height = height[iy, ix]
    zfield = zfield[iy, ix]

    return {"rgb": rgb, "colour": colour, "height": height, "idmap": idmap, "safe": safe,
            "dist": dist, "pool": pool, "entries": entries, "chis": chis, "z": zfield, "size": (Ws, Hs)}


if __name__ == "__main__":
    S = build()
    pool = S["pool"]
    for p in pool:
        extra = ""
        if p["type"] == "chiseled":
            extra = " groove %.1f deg period %.3f px = %.3f in (%.2f mm) resid %.2f" % (
                p["groove_deg"], p["period_px"], p["period_in"], p["period_mm"], p["resid_std_ratio"])
        print(p["entry"], "full" if p["full"] else "part%.2f" % p["frac"], p["type"], "(%.0f,%.0f)" % (p["cx"], p["cy"]), extra)
    cnt = {}
    for p in pool:
        if p["full"]:
            cnt[p["type"]] = cnt.get(p["type"], 0) + 1
    print("full-face counts", cnt)
    json.dump({"pool": pool, "chiseled_profiles": {str(k): v for k, v in S["chis"].items()}},
              open(out_path("source", "data", "render_pool.json"), "w"), indent=1)
