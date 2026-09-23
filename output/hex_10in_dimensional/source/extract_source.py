"""Extract the product's own surface character from the two supplied references.

Outputs (all inside output/hex_10in_dimensional/):
  source/mottle_tile.png          seamless high-pass mottle field taken from the flat
                                  layout reference (reference 01), 16-bit grey, zero-mean
                                  encoded around 32768
  source/_REVIEW_source_crop.jpg  the exact patches used, side by side
  source/source_stats.json        measured numbers other scripts consume

Reference 01 (flat, orthographic layout art) supplies geometry and surface mottling.
Reference 02 (installed photo, raking light) supplies tone only; its geometry is
perspective-distorted and its lighting is baked, so nothing spatial is taken from it.
"""

import json
import os

import numpy as np
from PIL import Image

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def out_path(*parts):
    """Every write goes through here; raises if it would escape the product dir."""
    p = os.path.abspath(os.path.join(RUN_DIR, *parts))
    if os.path.commonpath([p, RUN_DIR]) != RUN_DIR:
        raise RuntimeError("refusing to write outside the run dir: %s" % p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


REF1 = os.path.join(RUN_DIR, "references", "user_supplied_01_flat_layout_variation.webp")
REF2 = os.path.join(RUN_DIR, "references", "user_supplied_02_installed_photo_tone_depth.webp")

PATCH = 200          # px, square patch taken from the flat reference
                     # (4.58 in of real tile; the largest square that fits inside a
                     #  hexagon of the reference clear of every joint)
HP_SIGMA = 28.0      # px, high-pass cutoff: removes joint lines and tile-to-tile tone


def gaussian_blur(a, sigma):
    """Separable FFT gaussian, float64, wrap-free (reflect-padded)."""
    pad = int(sigma * 4) + 1
    b = np.pad(a, pad, mode="reflect")
    n = b.shape[0]
    m = b.shape[1]
    ky = np.fft.fftfreq(n)
    kx = np.fft.fftfreq(m)
    g = np.exp(-2.0 * (np.pi * sigma) ** 2 * (ky[:, None] ** 2 + kx[None, :] ** 2))
    out = np.real(np.fft.ifft2(np.fft.fft2(b) * g))
    return out[pad:pad + a.shape[0], pad:pad + a.shape[1]]


def score_patch(g):
    """Low score = flat, plain, joint-free tile face."""
    lo = gaussian_blur(g, 18.0)
    structure = float(lo.std())                     # joints / tile borders
    hp = g - lo
    prof = hp.mean(axis=0)
    prof = prof - prof.mean()
    spec = np.abs(np.fft.rfft(prof * np.hanning(len(prof))))
    comb = float(spec[6:].max() / (spec[6:].mean() + 1e-9))   # combed striations
    prof2 = hp.mean(axis=1)
    prof2 = prof2 - prof2.mean()
    spec2 = np.abs(np.fft.rfft(prof2 * np.hanning(len(prof2))))
    comb = max(comb, float(spec2[6:].max() / (spec2[6:].mean() + 1e-9)))
    grain = float(hp.std())                          # stipple pitting is loud
    return structure + 0.6 * comb + 0.8 * grain, structure, comb, grain


def line_response(g, angles=(0, 60, 120), run=81, sigma=5.0):
    """Response to long straight dark lines at the given orientations.

    The joints run at 0 and +/-60 degrees and hold their dip for hundreds of pixels,
    while the drawn surface texture and the field noise are short and random, so a
    long box average along the line direction separates them cleanly.
    """
    d = gaussian_blur(g, sigma) - g
    h, w = d.shape
    out = np.zeros_like(d)
    for a in angles:
        im = Image.fromarray(d.astype(np.float32), mode="F").rotate(
            -a, resample=Image.BILINEAR, expand=True)
        r = np.asarray(im, dtype=np.float64)
        k = np.ones(run) / run
        acc = np.apply_along_axis(lambda v: np.convolve(v, k, mode="same"), 1, r)
        back = Image.fromarray(acc.astype(np.float32), mode="F").rotate(
            a, resample=Image.BILINEAR, expand=True)
        b = np.asarray(back, dtype=np.float64)
        oy = (b.shape[0] - h) // 2
        ox = (b.shape[1] - w) // 2
        out = np.maximum(out, b[oy:oy + h, ox:ox + w])
    return out


def find_plain_patches(g, size, want, bad, max_bad=0.03, x_lim=None, y_lim=None, step=20):
    """Joint-free, comb-free, plain tile interiors. Returns [(x, y), ...].

    `bad` marks everything that is not plain glaze - joints and drawn/photographed
    surface texture. A patch is rejected outright if more than max_bad of it is bad.
    """
    ii = bad.astype(np.float64).cumsum(axis=0).cumsum(axis=1)
    ii = np.pad(ii, ((1, 0), (1, 0)))

    def joints_in(x, y):
        return ii[y + size, x + size] - ii[y, x + size] - ii[y + size, x] + ii[y, x]

    h, w = g.shape
    xmax = (x_lim if x_lim else w) - size
    ymax = (y_lim if y_lim else h) - size
    cands = []
    for y in range(0, ymax, step):
        for x in range(0, xmax, step):
            if joints_in(x, y) / float(size * size) > max_bad:
                continue
            s = score_patch(g[y:y + size, x:x + size])
            cands.append((s[0], x, y, s[1], s[2], s[3]))
    cands.sort()
    picked = []
    for s, x, y, st, cb, gr in cands:
        if all(abs(x - px) >= size or abs(y - py) >= size for px, py in picked):
            picked.append((x, y))
            print("  plain patch @ (%4d,%4d)  score=%.2f structure=%.2f comb=%.1f grain=%.2f"
                  % (x, y, s, st, cb, gr))
        if len(picked) == want:
            break
    if not picked:
        raise RuntimeError("no joint-free plain patch found")
    return picked


def make_tileable(a, band_frac=0.22):
    """Offset by half, cross-fade the seam. Safe on zero-mean high-pass content."""
    h, w = a.shape
    b = np.roll(np.roll(a, h // 2, axis=0), w // 2, axis=1)
    bw = int(w * band_frac)
    bh = int(h * band_frac)
    out = b.copy()
    # horizontal seam sits at x = w/2 after the roll; blend with the un-rolled copy
    ramp = np.linspace(0.0, 1.0, bw)
    x0 = w // 2 - bw // 2
    out[:, x0:x0 + bw] = b[:, x0:x0 + bw] * (1 - ramp)[None, :] + a[:, x0:x0 + bw] * ramp[None, :]
    ramp = np.linspace(0.0, 1.0, bh)
    y0 = h // 2 - bh // 2
    out[y0:y0 + bh, :] = out[y0:y0 + bh, :] * (1 - ramp)[:, None] + a[y0:y0 + bh, :] * ramp[:, None]
    # force exact wrap: feather the outer 1/8 against the opposite edge
    f = int(min(h, w) * 0.10)
    t = np.linspace(0.0, 1.0, f)
    out[:, :f] = out[:, :f] * t[None, :] + out[:, -f:][:, ::-1] * (1 - t)[None, :]
    out[:, -f:] = out[:, -f:] * (1 - t)[None, :] + out[:, :f][:, ::-1] * t[None, :]
    out[:f, :] = out[:f, :] * t[:, None] + out[-f:, :][::-1, :] * (1 - t)[:, None]
    out[-f:, :] = out[-f:, :] * (1 - t)[:, None] + out[:f, :][::-1, :] * t[:, None]
    return out


def main():
    ref1 = np.asarray(Image.open(REF1).convert("RGB"), dtype=np.float64)
    ref2 = np.asarray(Image.open(REF2).convert("RGB"), dtype=np.float64)
    g1 = ref1.mean(axis=2)

    # --- search the flat reference for the plainest tile interiors -------------
    # (R - B) isolates the joints and the drawn surface textures from the cream glaze
    # A joint is a continuous 2 px line, so a small blur of that mask leaves a ridge
    # well above the scattered noise of the plain field. Reject a patch that contains
    # any of it at all: a joint clipping one corner is only ~1% of a 260 px square and
    # slips through an area threshold, but it ruins the mottle tile.
    bad1 = line_response(g1) > 4.0
    print("flat layout reference: joint-line pixels %.2f%% of image" % (100 * bad1.mean()))
    picked = find_plain_patches(g1, PATCH, 4, bad1, max_bad=0.0, step=10)

    # --- build the mottle tile from the best patch ----------------------------
    px, py = picked[0]
    patch = g1[py:py + PATCH, px:px + PATCH]
    hp = patch - gaussian_blur(patch, HP_SIGMA)
    hp = hp / patch.mean()                     # ratio units, zero mean
    tile = make_tileable(hp)
    tile = tile - tile.mean()
    src_rms = float(tile.std())
    print("mottle tile: %dpx  rms=%.5f (ratio)  p1=%.5f p99=%.5f"
          % (PATCH, src_rms, float(np.percentile(tile, 1)), float(np.percentile(tile, 99))))

    enc = np.clip(tile * 4.0 + 0.5, 0.0, 1.0)  # x4 headroom, mid at 32768
    Image.fromarray(np.round(enc * 65535.0).astype(np.uint16)).save(
        out_path("source", "mottle_tile.png"))

    # --- fine surface grain from the installed photo --------------------------
    # The flat layout art is smooth vector-like work and carries almost no micro
    # texture; the photo shows the real matte/sandy face. High-passing removes the
    # raking light and the falloff, leaving albedo-scale grain only.
    g2 = ref2.mean(axis=2)
    print("installed photo (tile-only region):")
    # in the photo the textures read as local contrast, not as a colour shift
    det2 = np.abs(g2 - gaussian_blur(g2, 12.0))
    bad2 = det2 > 3.0 * np.median(det2[:1500, :860])
    gp = find_plain_patches(g2, PATCH, 2, bad2, max_bad=0.12, x_lim=860, y_lim=1500)
    qx, qy = gp[0]
    gpatch = g2[qy:qy + PATCH, qx:qx + PATCH]
    grain = gpatch - gaussian_blur(gpatch, 10.0)
    grain = grain / gpatch.mean()
    grain_tile = make_tileable(grain)
    grain_tile = grain_tile - grain_tile.mean()
    grain_rms = float(grain_tile.std())
    print("grain tile: %dpx  rms=%.5f (ratio)" % (PATCH, grain_rms))
    genc = np.clip(grain_tile * 4.0 + 0.5, 0.0, 1.0)
    Image.fromarray(np.round(genc * 65535.0).astype(np.uint16)).save(
        out_path("source", "grain_tile.png"))

    # --- tone from the installed photo ---------------------------------------
    # Well-lit, prop-free, plain tile faces only. Perspective and falloff make any
    # single patch unreliable, so take the high percentile of a lit band.
    band = ref2[80:520, 60:380].reshape(-1, 3)
    lit = np.percentile(band, 70, axis=0)
    band2 = ref2[260:700, 120:360].reshape(-1, 3)
    lit2 = np.percentile(band2, 70, axis=0)
    print("photo lit plain face p70:", lit.round(1), lit2.round(1))
    print("flat layout ref median:", np.median(ref1.reshape(-1, 3), axis=0).round(1))

    # --- review image ---------------------------------------------------------
    cells = []
    for x, y in picked:
        cells.append(Image.fromarray(g1[y:y + PATCH, x:x + PATCH].astype(np.uint8)))
    for x, y in gp:
        cells.append(Image.fromarray(g2[y:y + PATCH, x:x + PATCH].astype(np.uint8)))
    vis = (tile / (4.0 * src_rms) * 60.0 + 128.0).clip(0, 255)
    cells.append(Image.fromarray(vis.astype(np.uint8)))
    vis2 = (grain_tile / (4.0 * grain_rms) * 60.0 + 128.0).clip(0, 255)
    cells.append(Image.fromarray(vis2.astype(np.uint8)))
    strip = Image.new("L", (PATCH * len(cells) + 10 * (len(cells) - 1), PATCH), 255)
    for i, c in enumerate(cells):
        strip.paste(c, (i * (PATCH + 10), 0))
    strip.convert("RGB").save(out_path("source", "_REVIEW_source_crop.jpg"), quality=92)

    json.dump({
        "flat_reference": os.path.basename(REF1),
        "flat_reference_px": [int(ref1.shape[1]), int(ref1.shape[0])],
        "photo_reference": os.path.basename(REF2),
        "photo_reference_px": [int(ref2.shape[1]), int(ref2.shape[0])],
        "plain_patches_xy": [[int(a), int(b)] for a, b in picked],
        "patch_px": PATCH,
        "mottle_rms_ratio": src_rms,
        "grain_rms_ratio": grain_rms,
        "photo_grain_patch_xy": [[int(a),int(b)] for a,b in gp],
        "mottle_encoding": "grey16 = clip(hp_ratio*4 + 0.5)",
        "photo_lit_plain_p70_rgb": [lit.tolist(), lit2.tolist()],
        "flat_layout_median_rgb": np.median(ref1.reshape(-1, 3), axis=0).tolist(),
    }, open(out_path("source", "source_stats.json"), "w"), indent=2)
    print("wrote source/mottle_tile.png, source/_REVIEW_source_crop.jpg, source/source_stats.json")


if __name__ == "__main__":
    main()
