"""Step 4: measure Chiseled groove geometry in the render.

For each chiseled face: local orientation map (straight vs curved grooves),
groove pitch from the 1D spectrum across the grooves, and a mean groove
profile. Also writes 1:1 crops for visual inspection.
"""
import os
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from guard import inp, save_image, write_text, WORK_DIR

R = np.asarray(Image.open(inp("elm_formed_hex_sand_layout_render.webp")).convert("RGB")).astype(np.float64)
H, W, _ = R.shape
lum = R @ np.array([0.2126, 0.7152, 0.0722])
L = json.load(open(os.path.join(WORK_DIR, "render_lattice.json")))
S = json.load(open(os.path.join(WORK_DIR, "render_cell_stats.json")))
Rc, half_f = L["Rc"], L["half_f"]
PXIN = L["px_per_in"]
print("render px/in (assumed 10.125 in module) %.3f" % PXIN)

chis = [s for s in S if s["coherence"] > 0.6]
hp = lum - ndi.gaussian_filter(lum, 8.0)
out = {}
for s in chis:
    cx, cy = s["cx"], s["cy"]
    r = int(half_f - 14)
    x0, y0 = int(round(cx)) - r, int(round(cy)) - r
    if x0 < 0 or y0 < 0 or x0 + 2 * r > W or y0 + 2 * r > H:
        # half-visible face: use the visible part only for orientation
        continue
    patch = hp[y0:y0 + 2 * r, x0:x0 + 2 * r]
    # local orientation in 3x3 blocks (curvature test)
    g = ndi.gaussian_filter(patch, 1.0)
    gx, gy = ndi.sobel(g, 1), ndi.sobel(g, 0)
    blocks = []
    n = 4
    bs = 2 * r // n
    for by in range(n):
        for bx in range(n):
            sl = (slice(by * bs, (by + 1) * bs), slice(bx * bs, (bx + 1) * bs))
            # only blocks inside the inscribed circle
            ccx, ccy = (bx + 0.5) * bs - r, (by + 0.5) * bs - r
            if ccx * ccx + ccy * ccy > (0.8 * r) ** 2:
                continue
            jxx, jyy, jxy = (gx[sl] ** 2).mean(), (gy[sl] ** 2).mean(), (gx[sl] * gy[sl]).mean()
            ang = (0.5 * np.degrees(np.arctan2(2 * jxy, jxx - jyy)) + 90) % 180
            blocks.append(((bx, by), round(float(ang), 1)))
    # rotate so grooves are vertical, then average rows -> profile across grooves
    ang = s["groove_deg_img"]
    rot = ndi.rotate(patch, ang - 90, reshape=False, order=1)   # bring groove direction to 90 deg
    c = r
    band = rot[int(c - 0.45 * r):int(c + 0.45 * r), int(c - 0.6 * r):int(c + 0.6 * r)]
    prof = band.mean(axis=0)
    prof = prof - prof.mean()
    # spectrum with zero padding
    N = 8192
    spec = np.abs(np.fft.rfft(prof * np.hanning(len(prof)), N))
    freqs = np.fft.rfftfreq(N)
    ok = (freqs > 1 / 40.0) & (freqs < 1 / 2.5)
    fpk = freqs[ok][np.argmax(spec[ok])]
    period_px = 1 / fpk
    # autocorrelation check along the band rows (average per-row autocorr)
    ac = np.zeros(60)
    for row in band:
        rr = row - row.mean()
        full = np.correlate(rr, rr, "full")[len(rr) - 1:len(rr) - 1 + 60]
        ac += full / (full[0] + 1e-9)
    ac /= len(band)
    lag = 3 + np.argmax(ac[3:40])
    # straightness: correlate profile of top third vs bottom third of the band (shift)
    top = rot[int(c - 0.6 * r):int(c - 0.2 * r), int(c - 0.5 * r):int(c + 0.5 * r)].mean(axis=0)
    bot = rot[int(c + 0.2 * r):int(c + 0.6 * r), int(c - 0.5 * r):int(c + 0.5 * r)].mean(axis=0)
    xc = [np.corrcoef(np.roll(top, k)[20:-20], bot[20:-20])[0, 1] for k in range(-12, 13)]
    shift = int(np.argmax(xc)) - 12
    out["%d,%d" % (s["j"], s["k"])] = {
        "groove_deg_img": ang, "blocks_deg": [b[1] for b in blocks],
        "period_px_fft": round(float(period_px), 3), "period_px_ac": int(lag),
        "period_in": round(float(period_px / PXIN), 4), "period_mm": round(float(period_px / PXIN * 25.4), 3),
        "rows_per_face_contrast": round(float(prof.std()), 3),
        "top_bot_shift_px": shift, "top_bot_corr": round(float(max(xc)), 3)}
    print("%s ang %.1f blocks %s" % ("%d,%d" % (s["j"], s["k"]), ang, [b[1] for b in blocks]))
    print("   period fft %.2f px (%.2f mm)  ac lag %d  contrast %.2f  straightness shift %d corr %.2f" % (
        period_px, period_px / PXIN * 25.4, lag, prof.std(), shift, max(xc)))
    # 1:1 crop (centre 240x240) and a rotated/grooves-vertical crop
    cc = Image.fromarray(np.clip(R[int(cy) - 120:int(cy) + 120, int(cx) - 120:int(cx) + 120], 0, 255).astype(np.uint8))
    save_image(cc, os.path.join(WORK_DIR, "chis_%d_%d_1to1.png" % (s["j"], s["k"])))
    np.save(os.path.join(WORK_DIR, "chis_%d_%d_prof.npy" % (s["j"], s["k"])), prof)
write_text(os.path.join(WORK_DIR, "chiseled_measure.json"), json.dumps(out, indent=1))
