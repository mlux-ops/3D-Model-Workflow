"""Independent verifier: re-derives every gate from the delivered Color.png on disk. Exits non-zero on any failure and
writes validation.json.

Gates (limits fixed before measuring):
 1 ihdr            8-bit, colour type 2 (RGB), non-interlaced, 3072 x 1536
 2 sample_size     width/ppi and height/ppi are exact quarter-inch multiples (Revit rounds to 1/4 in), = 48 x 24 in
 3 aspect          pixel aspect W/H equals physical aspect exactly (integer px/in)
 4 wrap_x, wrap_y  mean |step| across the wrap edge <= 1.25 x the median interior step on that axis, and the
                   32 px tone step across the wrap <= the 99th percentile of the same statistic at interior positions
 5 self_similarity every 6 x 3 in window (half-window stride) vs every other position on the torus, at 32 px/in,
                   band-passed luminance with the along-grain mean removed, templates also flipped (flipH, flipV,
                   r180) so mirrored reuse is caught; max off-self NCC < 0.50. Metric self-test: a planted copy
                   must score > 0.90 or the gate fails.
 6 grain_angle     structure-tensor grain direction within +-3 deg of horizontal (whole map) and within +-5 deg
                   in every 12 x 6 in block
 7 tone_drift      low-pass (sigma 1 in) log-luminance: column profile (along-grain drift) peak-to-peak <= 0.05;
                   first periodic harmonic amplitude along x and along y <= 0.02 (no lighting gradient left);
                   row profile (leaf-to-leaf tone) peak-to-peak <= 0.12 (reported natural leaf variation)"""
import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from common import ihdr, lum, srgb_to_lin
from guard import out_path

PPI = 64
EXPECT = (3072, 1536)


def circ_ncc_all(F_img, S1, S2, tpl, n):
    """Circular NCC of template tpl (h x w) against the whole torus image; returns the map at every offset."""
    H, W = F_img.shape
    t = tpl - tpl.mean()
    tn = np.sqrt((t * t).sum())
    T = np.zeros((H, W))
    T[:t.shape[0], :t.shape[1]] = t
    num = np.real(np.fft.ifft2(F_img * np.conj(np.fft.fft2(T))))
    den = np.sqrt(np.maximum(S2 - S1 * S1 / n, 1e-12)) * tn
    return num / den


def main():
    p = out_path("Color.png")
    res, ok = {}, True

    def gate(name, passed, **kw):
        nonlocal ok
        res[name] = {"pass": bool(passed), **kw}
        ok &= bool(passed)

    hd = ihdr(p)
    gate("ihdr", hd["bit_depth"] == 8 and hd["colour_type"] == 2 and hd["interlace"] == 0
         and (hd["w"], hd["h"]) == EXPECT, **hd)
    w_in, h_in = hd["w"] / PPI, hd["h"] / PPI
    gate("sample_size", (w_in * 4).is_integer() and (h_in * 4).is_integer() and (w_in, h_in) == (48.0, 24.0),
         ppi=PPI, width_in=w_in, height_in=h_in, revit="4'-0\" x 2'-0\"")
    gate("aspect", hd["w"] * h_in == hd["h"] * w_in, pixel_aspect=hd["w"] / hd["h"], physical_aspect=w_in / h_in)

    img = np.asarray(Image.open(p).convert("RGB"), dtype=np.float64)
    L8 = img @ np.array([0.2126, 0.7152, 0.0722])
    H, W = L8.shape
    # wrap gates
    for ax, name in ((1, "wrap_x"), (0, "wrap_y")):
        d = np.abs(np.diff(L8, axis=ax)).mean(axis=1 - ax)                      # interior steps per boundary
        wrap = float(np.abs(np.take(L8, 0, axis=ax) - np.take(L8, -1, axis=ax)).mean())
        k = 32
        c = np.cumsum(np.concatenate([np.take(L8, range(-k, 0), axis=ax), L8], axis=ax), axis=ax)
        blk = lambda i: (np.take(c, i + k, axis=ax) - np.take(c, i, axis=ax)) / k   # mean of k lines ending before i+k
        n_ax = L8.shape[ax]
        # tone step between the k lines before and the k lines after each boundary, per position along the edge
        steps = []
        for i in range(k, n_ax - k, 8):
            a_ = (np.take(c, i + k - 1 + k, axis=ax) - np.take(c, i - 1 + k, axis=ax)) / k
            b_ = (np.take(c, i - 1 + k, axis=ax) - np.take(c, i - 1, axis=ax)) / k
            steps.append(float(np.abs(a_ - b_).mean()))
        after = np.take(L8, range(0, k), axis=ax).mean(axis=ax)
        before = np.take(L8, range(n_ax - k, n_ax), axis=ax).mean(axis=ax)
        wrap_tone = float(np.abs(after - before).mean())
        med = float(np.median(d))
        p99 = float(np.percentile(steps, 99))
        gate(name, wrap <= 1.25 * med and wrap_tone <= p99, wrap_step=round(wrap, 3), interior_median=round(med, 3),
             interior_p95=round(float(np.percentile(d, 95)), 3), ratio=round(wrap / med, 3),
             wrap_tone_step_32px=round(wrap_tone, 3), interior_tone_step_p50=round(float(np.median(steps)), 3),
             interior_tone_step_p99=round(p99, 3))

    # self-similarity at 32 px/in
    lin = srgb_to_lin(img)
    L = np.log(np.maximum(lum(lin), 1e-5))
    L32 = L.reshape(H // 2, 2, W // 2, 2).mean((1, 3))
    Fb = ndi.gaussian_filter(L32, 0.8, mode="wrap") - ndi.gaussian_filter(L32, 12, mode="wrap")
    Fb = Fb - ndi.uniform_filter1d(Fb, 96, axis=1, mode="wrap")          # remove along-grain mean (3 in)
    h32, w32 = Fb.shape
    tw, th = 192, 96                                                       # 6 x 3 in
    ones = np.zeros((h32, w32))
    ones[:th, :tw] = 1
    Fo = np.conj(np.fft.fft2(ones))
    FI = np.fft.fft2(Fb)
    S1 = np.real(np.fft.ifft2(FI * Fo))
    S2 = np.real(np.fft.ifft2(np.fft.fft2(Fb * Fb) * Fo))
    yy, xx = np.mgrid[:h32, :w32]
    # metric self-test: plant a copy of one window elsewhere
    pl = Fb.copy()
    src = Fb[300:300 + th, 700:700 + tw].copy()
    pl[100:100 + th, 200:200 + tw] = src
    FIp = np.fft.fft2(pl)
    S1p = np.real(np.fft.ifft2(FIp * Fo))
    S2p = np.real(np.fft.ifft2(np.fft.fft2(pl * pl) * Fo))
    mp = circ_ncc_all(FIp, S1p, S2p, src, th * tw)
    planted = float(mp[100, 200])
    results = []
    for y in range(0, h32, th // 2):
        for x in range(0, w32, tw // 2):
            t = np.roll(np.roll(Fb, -y, 0), -x, 1)[:th, :tw]
            dy = np.minimum((yy - y) % h32, (y - yy) % h32)
            dx = np.minimum((xx - x) % w32, (x - xx) % w32)
            best = (-1.0, None)
            for tn, tt in (("r0", t), ("flipH", t[:, ::-1]), ("flipV", t[::-1]), ("r180", t[::-1, ::-1])):
                mm = circ_ncc_all(FI, S1, S2, tt, th * tw)
                if tn == "r0":
                    mm = np.where((dy < th) & (dx < tw), -1, mm)
                v = float(mm.max())
                if v > best[0]:
                    yb, xb = np.unravel_index(int(np.argmax(mm)), mm.shape)
                    best = (v, (tn, int(yb), int(xb)))
            results.append((best[0], y, x, best[1]))
    results.sort(key=lambda r: -r[0])
    vals = np.array([r[0] for r in results])
    gate("self_similarity", vals.max() < 0.50 and planted > 0.90, max_ncc=round(float(vals.max()), 4),
         threshold=0.50, p95=round(float(np.percentile(vals, 95)), 4), median=round(float(np.median(vals)), 4),
         windows=len(results), planted_copy_selftest=round(planted, 4),
         top5=[{"ncc": round(r[0], 4), "window_yx_32ppi": [r[1], r[2]], "match": r[3]} for r in results[:5]])

    # grain orientation
    def angle(A):
        B = ndi.gaussian_filter(A, 1.0) - ndi.gaussian_filter(A, 8)
        gy, gx = np.gradient(B)
        jxx, jyy, jxy = (gx * gx).mean(), (gy * gy).mean(), (gx * gy).mean()
        th_ = 0.5 * np.degrees(np.arctan2(2 * jxy, jxx - jyy)) + 90
        return float((th_ + 90) % 180 - 90), float(np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / (jxx + jyy))
    a_all, coh = angle(L)
    blocks = []
    bh, bw = 6 * PPI, 12 * PPI
    for y in range(0, H, bh):
        for x in range(0, W, bw):
            blocks.append(angle(L[y:y + bh, x:x + bw])[0])
    gate("grain_angle", abs(a_all) <= 3 and max(abs(b) for b in blocks) <= 5, whole_map_deg=round(a_all, 2),
         coherence=round(coh, 3), block_deg_min=round(min(blocks), 2), block_deg_max=round(max(blocks), 2),
         blocks=len(blocks))

    # tone drift
    lp = ndi.gaussian_filter(L, PPI, mode="wrap")
    col = lp.mean(0)
    row = lp.mean(1)
    h1x = float(2 * np.abs(np.fft.rfft(col - col.mean())[1]) / len(col))
    h1y = float(2 * np.abs(np.fft.rfft(row - row.mean())[1]) / len(row))
    gate("tone_drift", np.ptp(col) <= 0.05 and h1x <= 0.02 and h1y <= 0.02 and np.ptp(row) <= 0.12,
         along_grain_col_profile_ptp=round(float(np.ptp(col)), 4), first_harmonic_x=round(h1x, 4),
         first_harmonic_y=round(h1y, 4), leaf_row_profile_ptp=round(float(np.ptp(row)), 4),
         limits={"col_ptp": 0.05, "harmonic": 0.02, "row_ptp": 0.12}, units="natural log of luminance")

    out = {"file": p, "all_pass": bool(ok), "gates": res}
    json.dump(out, open(out_path("validation.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
