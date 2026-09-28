"""Step 7: are the render's faces genuinely different, or copies of one texture?

For every pair of full faces of the same type, correlate the band-passed luma of face A's
central disc against face B under all 12 hexagon symmetries (6 rotations x mirror), over
all translations (FFT normalised cross-correlation). A copied texture shows a peak NCC
near 1; independent surfaces stay low. Also records the orientation of the anisotropy of
each raw face (spectral axis), to tell a directional light from an intrinsic texture axis.
"""

import json
import sys

import numpy as np
from scipy import ndimage

from common import load_lattice, render_rgb, luma, out_path, S3, gaussian


def face_patch(L, c, half):
    x, y = c["cx"], c["cy"]
    ys, xs = np.mgrid[-half:half + 1, -half:half + 1].astype(np.float64)
    return ndimage.map_coordinates(L, [ys + y - 0.5, xs + x - 0.5], order=3, mode="nearest")


def transform(a, k, mirror):
    """Rotate a square patch by k*60 deg about its centre (and mirror in x first)."""
    if mirror:
        a = a[:, ::-1]
    if k == 0:
        return a
    return ndimage.rotate(a, k * 60.0, reshape=False, order=3, mode="nearest")


def ncc_max(A, B, maskr):
    """Max NCC of template A (disc radius maskr) over all translations inside B."""
    h, w = B.shape
    yy, xx = np.mgrid[0:A.shape[0], 0:A.shape[1]]
    cy, cx = (A.shape[0] - 1) / 2.0, (A.shape[1] - 1) / 2.0
    m = ((yy - cy) ** 2 + (xx - cx) ** 2) <= maskr ** 2
    t = np.where(m, A - A[m].mean(), 0.0)
    t /= np.sqrt((t ** 2).sum())
    P = np.zeros((h, w)); P[:A.shape[0], :A.shape[1]] = t
    M = np.zeros((h, w)); M[:A.shape[0], :A.shape[1]] = m
    FB = np.fft.fft2(B); FB2 = np.fft.fft2(B * B)
    num = np.real(np.fft.ifft2(FB * np.conj(np.fft.fft2(P))))
    s1 = np.real(np.fft.ifft2(FB * np.conj(np.fft.fft2(M))))
    s2 = np.real(np.fft.ifft2(FB2 * np.conj(np.fft.fft2(M))))
    n = m.sum()
    var = np.maximum(s2 - s1 ** 2 / n, 1e-9)
    ncc = num / np.sqrt(var)
    # only translations where the template lies fully inside B's valid disc region
    valid = np.zeros((h, w), bool)
    off = (h - A.shape[0])
    valid[:off + 1, :off + 1] = True
    return float(ncc[valid].max())


def main():
    lat = load_lattice()
    cells = json.load(open(out_path("_work", "cells_raw.json")))
    rgb = render_rgb()
    L = luma(rgb)
    band = gaussian(L, 1.0) - gaussian(L, 8.0)
    full = [c for c in cells if c["frac"] > 0.99]
    types = {}
    for c in full:
        t = "chiseled" if c["coher"] > 0.6 else ("raw" if c["hp_std"] > 2.8 else "matte")
        types.setdefault(t, []).append(c)
    print({k: [c["id"] for c in v] for k, v in types.items()})
    half_t = 60     # template disc radius 60 px (~1.9 in)
    half_b = 115    # search window (inside the face's clean region, apothem ~151 px)
    out = {}
    for t in ("raw", "matte", "chiseled"):
        cs = types.get(t, [])
        res = []
        for a in cs:
            A0 = face_patch(band, a, half_t + 20)
            for b in cs:
                if b["id"] == a["id"]:
                    continue
                B = face_patch(band, b, half_b)
                best = -1
                for k in range(6):
                    for mir in (False, True):
                        At = transform(A0, k, mir)[20:-20, 20:-20]
                        v = ncc_max(At, B, half_t)
                        best = max(best, v)
                res.append((a["id"], b["id"], best))
        vals = np.array([r[2] for r in res]) if res else np.array([0.0])
        print("%s: pairs %d  NCC max over transforms+shifts: median %.3f  max %.3f"
              % (t, len(res), np.median(vals), vals.max()))
        top = sorted(res, key=lambda r: -r[2])[:5]
        print("   top pairs:", [(r[0], r[1], round(r[2], 3)) for r in top])
        # self-check: a face against itself rotated 60 deg must score ~1 at k=... (sanity)
        out[t] = {"pairs": res, "median": float(np.median(vals)), "max": float(vals.max())}
    # sanity: same face, own copy
    a = types["raw"][0]
    A0 = face_patch(band, a, half_t + 20)[20:-20, 20:-20]
    B = face_patch(band, a, half_b)
    print("sanity (raw face %d vs itself): %.3f" % (a["id"], ncc_max(A0, B, half_t)))
    # anisotropy axis per raw face (power-spectrum second moment in the 3-20 px band)
    print("raw-face spectral anisotropy (axis of max power, y-up deg; ratio max/min):")
    for c in types["raw"] + types["matte"][:4]:
        P = face_patch(L - gaussian(L, 20.0), c, 100)
        win = np.hanning(P.shape[0])[:, None] * np.hanning(P.shape[1])[None, :]
        F = np.abs(np.fft.fftshift(np.fft.fft2((P - P.mean()) * win))) ** 2
        n = P.shape[0]
        f = np.fft.fftshift(np.fft.fftfreq(n))
        fy, fx = np.meshgrid(f, f, indexing="ij")
        fr = np.hypot(fx, fy)
        bnd = (fr > 1 / 20.0) & (fr < 1 / 3.0)
        # second-moment tensor of the band power (y-up: fy -> -fy)
        wgt = F * bnd
        Txx = (wgt * fx * fx / fr.clip(1e-9) ** 2).sum()
        Tyy = (wgt * fy * fy / fr.clip(1e-9) ** 2).sum()
        Txy = (wgt * fx * (-fy) / fr.clip(1e-9) ** 2).sum()
        ev, evec = np.linalg.eigh(np.array([[Txx, Txy], [Txy, Tyy]]))
        ax = np.degrees(np.arctan2(evec[1, 1], evec[0, 1])) % 180
        print("  id %2d (%s) axis %.1f  ratio %.2f" % (c["id"], "raw" if c in types["raw"] else "matte", ax, ev[1] / ev[0]))
    json.dump(out, open(out_path("_work", "dup_check.json"), "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
