"""Build the ELM Vivid Ligne Noir colour (8-bit sRGB) and bump (16-bit grey) maps.

Facts (see SOURCE_SELECTION.md and _work/measure.json):
  * actual tile 2.75 x 9.66 in (Nemo Vivant brochure, the same product line), 7.4 mm thick.
    Drawn 2.75 x 9.6875 in (9 11/16, +0.7 mm, inside pressed-tile tolerance) so that the Revit
    Sample Size is an exact quarter inch both ways: Revit's Texture Editor rounds to the project's
    1/4 in length units, and 39.39 in became 3'-3 1/2" (owner report 2026-09-26).
  * recommended grout joint 3/16 in (ELM Vivid spec sheet and Nemo brochure)
  * 10 rounded ribs across the 2.75 in face, running the full length (all three ELM images)
  * matte glaze; colour from the single straight-on ELM swatch, de-lit

Layout: tiles vertical (ribs vertical), straight stack, 12 columns x 4 rows, half a joint on every
image edge, so both maps wrap. 100 px/in: 3525 x 3950 px = 35.25 x 39.50 in (2'-11 1/4" x 3'-3 1/2").

Height (mm above the grout floor): tile field BASE_MM, ribs RIB_MM on top, eased tile edge of
EDGE_MM radius. Pattern and joint are separate terms; there is no global multiplier.
Every write goes through guard.out_path.
"""
import json
import sys
import struct
import zlib

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, uniform_filter1d, zoom

from guard import out_path, ref

SEED = 2026092601
PPI = 100
TILE_W, TILE_H, JOINT = 2.75, 9.6875, 0.1875   # drawn length 9 11/16 (actual 9.66), see docstring
MOD_W, MOD_H = TILE_W + JOINT, TILE_H + JOINT
COLS, ROWS = 12, 4
W_IN, H_IN = COLS * MOD_W, ROWS * MOD_H
W_PX, H_PX = int(round(W_IN * PPI)), int(round(H_IN * PPI))
MM = 25.4

N_RIBS = 10
RIB_FRAC = 0.78        # rib share of each 0.275 in pitch; the rest is the flat channel floor
RIB_EXP = 0.6          # cap shape: 0.5 = semi-ellipse, larger = fuller shoulders
BASE_MM = 1.20         # channel floor / flat tile field above the grout floor
RIB_MM = 1.50          # rib crest above the channel floor (pattern depth)
EDGE_MM = 1.20         # eased-edge radius at the tile perimeter
RIB_H_SIGMA = 0.04     # per-tile rib height spread (pressed piece variation)
WAVE_MM = 0.12         # low-frequency face undulation amplitude ("hand made" look)
CHAN_DARK = 0.04       # glaze pools slightly darker in the channel floor (albedo, not shading)
TONE_SIGMA = 0.05      # per-tile log-luminance spread, V1 shade variation
HUE_SIGMA = 0.008
GROUT_SRGB = (229.7, 225.0, 227.4)   # ELM installed photo, joint cores (as photographed)
# grout variants: python b01_build.py <suffix> <R,G,B>  -> textures/Color_<suffix>.png only; the bump is
# recomputed and must equal the delivered Bump16.png byte for byte (same seed, same geometry)
GROUT_VARIANTS = {"charcoal": (68.0, 68.0, 70.0)}   # dark charcoal grey, owner request 2026-09-26
PATCH = 48             # quilt patch (px at 100 ppi) and half-overlap step
STEP = PATCH // 2
STREAK_IN = 0.5        # along-flute running-mean length removed from the glaze residual

SWATCH = "elm_page_main-image_template.jpg"
SWATCH_PERIOD_PX = None  # measured in delight()


def srgb_to_lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return 255.0 * np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def fold_period(profile, lo, hi, steps=4000, bins=32):
    x = np.arange(len(profile))
    best = (0, None)
    for p in np.linspace(lo, hi, steps):
        b = np.minimum((((x / p) % 1.0) * bins).astype(int), bins - 1)
        m = np.bincount(b, profile, bins) / np.maximum(np.bincount(b, None, bins), 1)
        if m.var() > best[0]:
            best = (m.var(), p)
    return best[1]


def delight():
    """Return the de-lit glaze residual (relative, mean 0) at 100 ppi, ribs vertical, plus stats."""
    s = np.asarray(Image.open(ref(SWATCH)).convert("RGB")).astype(np.float64)
    s = s[6:-6, 12:-12]                      # trim the soft photo border
    lin = srgb_to_lin(s)
    lum = lin.mean(2)
    rows = np.arange(lum.shape[0])
    period = fold_period(lum.mean(1) - lum.mean(), 25.0, 45.0)
    # tilt: phase of the flute pattern in column blocks, fitted linearly
    bins = 64
    blocks = []
    ref_prof = None
    for c0 in range(0, lum.shape[1] - 96, 96):
        prof = lum[:, c0:c0 + 96].mean(1)
        if ref_prof is None:
            ref_prof = prof
        cc = [np.corrcoef(prof[20:-20], np.interp(rows[20:-20] + d, rows, ref_prof))[0, 1]
              for d in np.linspace(-6, 6, 241)]
        blocks.append((c0 + 48, np.linspace(-6, 6, 241)[int(np.argmax(cc))]))
    bx, bd = np.array(blocks).T
    tilt = np.polyfit(bx, bd, 1)[0]          # rows of shift per column
    cols = np.arange(lum.shape[1])
    ph = ((rows[:, None] + tilt * (cols[None, :] - bx[0])) / period) % 1.0
    b = np.minimum((ph * bins).astype(int), bins - 1)
    prof_rgb = np.stack([np.bincount(b.ravel(), lin[..., k].ravel(), bins) /
                         np.bincount(b.ravel(), None, bins) for k in range(3)], 1)
    g = lin / prof_rgb[b]
    # length vignette and width gradient: low-order polynomials of the phase-flattened field
    gl = g.mean(2)
    V = np.polyval(np.polyfit(cols, gl.mean(0), 4), cols)
    U = np.polyval(np.polyfit(rows, (gl / V[None, :]).mean(1), 2), rows)
    g = g / (V[None, :, None] * U[:, None, None])
    r = g - 1.0
    # equalise residual variance per phase (dark phases carry amplified noise)
    sd = np.array([r[b == k].std() for k in range(bins)])
    lit = prof_rgb.mean(1) >= np.median(prof_rgb.mean(1))
    s_ref = np.median(sd[lit])
    r = r * (s_ref / sd)[b][..., None]
    # remove streaks that run along the flutes (residual flute shading, not glaze): the source axis 1
    # runs along the flutes, so subtract a STREAK_IN-long running mean along that axis
    sd_before_destreak = float(r.std())
    r = r - uniform_filter1d(r, int(round(STREAK_IN * period / (TILE_W / N_RIBS))), axis=1, mode="reflect")
    # rotate to ribs vertical and resample to 100 ppi
    src_ppi = period / (TILE_W / N_RIBS)
    r = np.transpose(r, (1, 0, 2))
    r = zoom(r, (PPI / src_ppi, PPI / src_ppi, 1), order=3)
    before = float(prof_rgb.mean(1).max() / prof_rgb.mean(1).min())
    fl = (g.mean(2))
    after_prof = np.bincount(b.ravel(), fl.ravel(), bins) / np.bincount(b.ravel(), None, bins)
    stats = {
        "swatch": SWATCH, "trimmed_px": [int(s.shape[1]), int(s.shape[0])],
        "flute_period_px": period, "source_ppi": src_ppi,
        "visible_length_in": s.shape[1] / src_ppi, "visible_width_in": s.shape[0] / src_ppi,
        "tilt_rows_per_col": tilt,
        "flute_shading_peak_to_trough_before": before,
        "flute_profile_after_peak_to_trough": float(after_prof.max() / after_prof.min()),
        "length_vignette_peak_to_trough": float(V.max() / V.min()),
        "residual_sd_rel_before_destreak": sd_before_destreak,
        "residual_sd_rel": float(r.std()),
        "mean_srgb": [float(v) for v in lin_to_srgb(lin.reshape(-1, 3).mean(0))],
        "residual_px_100ppi": [int(r.shape[1]), int(r.shape[0])],
    }
    return r, lin.reshape(-1, 3).mean(0), stats


def quilt(res, rng, h, w):
    """Variance-preserving Hann-window quilt of random source patches (with random flips)."""
    acc = np.zeros((h + 2 * PATCH, w + 2 * PATCH, 3))
    wsum = np.zeros((h + 2 * PATCH, w + 2 * PATCH))
    t = np.sin(np.pi * (np.arange(PATCH) + 0.5) / PATCH) ** 2
    win = np.outer(t, t)
    sh, sw = res.shape[:2]
    margin = 3
    for y in range(0, h + STEP, STEP):
        for x in range(0, w + STEP, STEP):
            py = rng.integers(margin, sh - PATCH - margin)
            px = rng.integers(margin, sw - PATCH - margin)
            p = res[py:py + PATCH, px:px + PATCH]
            k = rng.integers(4)
            if k & 1:
                p = p[::-1]
            if k & 2:
                p = p[:, ::-1]
            acc[y:y + PATCH, x:x + PATCH] += p * win[..., None]
            wsum[y:y + PATCH, x:x + PATCH] += win ** 2
    out = acc[STEP:STEP + h, STEP:STEP + w] / np.sqrt(wsum[STEP:STEP + h, STEP:STEP + w])[..., None]
    return out


def rib_profile(u_in):
    """Height (0..1) of the rib pattern across the tile width; u_in in [0, TILE_W]."""
    pitch = TILE_W / N_RIBS
    t = (u_in % pitch) / pitch                       # 0..1 within a pitch, rib centred at 0.5
    a = (t - 0.5) / (RIB_FRAC / 2)                   # -1..1 across the rib
    cap = np.clip(1 - a * a, 0, 1) ** RIB_EXP
    return cap, np.abs(a) >= 1


def edge_ease(d_mm):
    """Quarter-circle roundover: 0 at the tile edge, 1 once EDGE_MM inside it."""
    q = np.clip(d_mm / EDGE_MM, 0, 1)
    return np.sqrt(1 - (1 - q) ** 2)


def write_png16(path, arr16):
    h, w = arr16.shape
    raw = b"".join(b"\x00" + arr16[y].astype(">u2").tobytes() for y in range(h))

    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 16, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    open(path, "wb").write(png)


def main(grout_srgb=GROUT_SRGB, suffix=""):
    rng = np.random.default_rng(SEED)
    res, swatch_mean_lin, dstats = delight()

    x_in = (np.arange(W_PX) + 0.5) / PPI
    y_in = (np.arange(H_PX) + 0.5) / PPI
    col = np.minimum((x_in // MOD_W).astype(int), COLS - 1)
    row = np.minimum((y_in // MOD_H).astype(int), ROWS - 1)
    u = x_in - col * MOD_W - JOINT / 2               # across the tile, 0..TILE_W on the face
    v = y_in - row * MOD_H - JOINT / 2               # along the tile
    du = np.minimum(u, TILE_W - u)                   # distance to the long edges (in)
    dv = np.minimum(v, TILE_H - v)
    tile_id = row[:, None] * COLS + col[None, :]
    n_tiles = COLS * ROWS

    # per-tile parameters
    rib_scale = 1 + RIB_H_SIGMA * rng.standard_normal(n_tiles)
    tone = np.exp(TONE_SIGMA * rng.standard_normal(n_tiles))
    hue = HUE_SIGMA * rng.standard_normal((n_tiles, 3))
    hue -= hue.mean(1, keepdims=True)
    wave_k = rng.uniform(0.6, 1.6, (n_tiles, 3))      # cycles per tile length
    wave_p = rng.uniform(0, 2 * np.pi, (n_tiles, 3))
    wave_a = rng.normal(0, 1, (n_tiles, 3))
    wave_a /= np.sqrt((wave_a ** 2).sum(1, keepdims=True))
    wave_x = rng.normal(0, 0.35, n_tiles)            # slight tilt of the waves across the tile

    cap, chan = rib_profile(np.clip(u, 0, TILE_W))
    d_mm = np.minimum(du[None, :], dv[:, None]) * MM
    ease = edge_ease(d_mm)
    inside = d_mm > 0

    tv = np.clip(v, 0, TILE_H)[:, None] / TILE_H
    tu = np.clip(u, 0, TILE_W)[None, :] / TILE_W
    wave = np.zeros((H_PX, W_PX))
    for k in range(3):
        wave += wave_a[tile_id, k] * np.sin(2 * np.pi * wave_k[tile_id, k] * (tv + wave_x[tile_id] * tu)
                                             + wave_p[tile_id, k])
    wave *= WAVE_MM / np.sqrt(1.5)
    height = np.where(inside, ease * (BASE_MM + RIB_MM * rib_scale[tile_id] * cap[None, :] + wave), 0.0)
    height = np.maximum(height, 0.0)
    del wave

    # colour
    glaze = quilt(res, rng, H_PX, W_PX)
    base = swatch_mean_lin
    lum = base[None, None, :] * (1 + glaze)
    lum *= (tone[tile_id] * 1.0)[..., None] * np.exp(hue[tile_id])
    lum *= (1 - CHAN_DARK * (1 - cap))[None, :, None]
    del glaze
    grout = srgb_to_lin(np.array(grout_srgb, dtype=np.float64))
    gnoise = gaussian_filter(rng.standard_normal((H_PX, W_PX)), 1.2) * 0.02
    grout_f = grout[None, None, :] * (1 + gnoise[..., None])
    px_mm = MM / PPI
    alpha = np.clip(d_mm / px_mm + 0.5, 0, 1)[..., None]
    colour = alpha * lum + (1 - alpha) * grout_f
    del lum, grout_f
    srgb = np.clip(np.round(lin_to_srgb(colour)), 0, 255).astype(np.uint8)
    del colour

    cpath = out_path("textures/Color%s.png" % ("_" + suffix if suffix else ""))
    Image.fromarray(srgb, "RGB").save(cpath, optimize=True)
    full_mm = float(height.max())
    h16 = np.clip(np.round(height / full_mm * 65535), 0, 65535).astype(np.uint16)
    if suffix:
        delivered = np.asarray(Image.open(out_path("textures/Bump16.png"))).astype(np.uint16)
        if not np.array_equal(delivered, h16):
            raise RuntimeError("variant bump differs from delivered Bump16.png: geometry or seed changed")
        print("bump identical to delivered Bump16.png")
    else:
        bpath = out_path("textures/Bump16.png")
        write_png16(bpath, h16)
        np.save(out_path("_work/tile_id.npy"), tile_id.astype(np.uint8))

    face = inside & (d_mm >= EDGE_MM)
    chan_px = face & chan[None, :]
    report = {
        "product": "ELM Surfaces Vivid Ligne Noir 3x10 (matte relief, 7.4 mm)",
        "seed": SEED, "ppi": PPI,
        "tile_actual_in": [2.75, 9.66], "tile_drawn_in": [TILE_W, TILE_H], "joint_in": JOINT, "module_in": [MOD_W, MOD_H],
        "atlas_tiles": [COLS, ROWS], "pixels": [W_PX, H_PX],
        "sample_size_in": [W_IN, H_IN],
        "orientation": "tiles vertical, ribs vertical, straight stack",
        "ribs_per_tile": N_RIBS, "rib_pitch_mm": TILE_W / N_RIBS * MM,
        "rib_width_mm": RIB_FRAC * TILE_W / N_RIBS * MM,
        "channel_width_mm": (1 - RIB_FRAC) * TILE_W / N_RIBS * MM,
        "relief_mm": {
            "full_scale": full_mm, "grout_floor": 0.0,
            "channel_floor_design": BASE_MM, "rib_crest_design": BASE_MM + RIB_MM,
            "pattern_depth_design": RIB_MM,
            "pattern_depth_measured_p99_minus_channel_p50":
                float(np.percentile(height[face], 99.5) - np.median(height[chan_px])),
            "lowest_face_point_mm": float(height[face].min()),
            "lowest_channel_point_mm": float(height[chan_px].min()),
            "edge_radius": EDGE_MM, "wave_amplitude": WAVE_MM,
            "mm_per_count": full_mm / 65535,
        },
        "colour": {
            "base_linear": [float(c) for c in base],
            "base_srgb": [float(c) for c in lin_to_srgb(base)],
            "face_mean_srgb": [float(c) for c in srgb[face].reshape(-1, 3).mean(0)],
            "grout_srgb": list(grout_srgb),
            "tone_sigma_log": TONE_SIGMA, "channel_darkening": CHAN_DARK,
        },
        "delight": dstats,
    }
    json.dump(report, open(out_path("textures/report%s.json" % ("_" + suffix if suffix else "")), "w"), indent=1)
    print(json.dumps({k: report[k] for k in ("pixels", "sample_size_in", "relief_mm", "colour")}, indent=1))
    print(json.dumps(dstats, indent=1))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
        rgb = tuple(float(v) for v in sys.argv[2].split(",")) if len(sys.argv) > 2 else GROUT_VARIANTS[name]
        main(rgb, name)
    else:
        main()
