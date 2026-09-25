"""ELM Surfaces Vivid "Ligne Noir" 3x10 fluted tile -- seamless colour + 16-bit bump for Revit.

    python build_ligne_noir.py          (CPython 3, numpy + pillow)

Deliverable (textures/):
    ELM_Ligne_Noir_3x10_Color.png    8-bit sRGB, 3600 x 4000
    ELM_Ligne_Noir_3x10_Bump16.png   16-bit grey, same layout
Sample Size: 36 x 40 in (3'-0" x 3'-4"): 12 columns x 4 rows of the 3 x 10 in module,
tiles vertical (flutes vertical), straight stack, 1/16 in joint, half a joint on
every outer edge so both maps wrap.

Colour is 100 % real photo pixels (standing instruction 2026-09-20: "it needs to be the
photo based version"): the manufacturer's flat Ligne Noir swatch, with its studio
lighting removed (length vignette + per-flute shading), cut into whole-flute strips at
the groove and re-sequenced per tile. Relief is procedural from measured geometry
(10 straight, parallel, full-length flutes per tile), never from photographed light.
Every write goes through out_path(), which refuses anything outside output/elm_ligne_noir.
"""
import hashlib
import json
import math
import os
import struct
import sys
import zlib

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.normpath(os.path.join(HERE, '..'))
REF = os.path.join(RUN, 'references')
_RUN_NORM = os.path.normpath(RUN)

MM = 25.4
# --- product facts (elmsurfaces.com/product/ligne-noir, 2026-09-25): 3 x 10, matte, 7.5 mm
MODULE_W_IN, MODULE_L_IN = 3.0, 10.0       # nominal = installed module (skill rule 1)
JOINT_IN = 1.0 / 16.0                      # measured: joint = 0.21 flute widths in the wall photo
FLUTES = 10                                # measured: 10.21 flute periods per 3 in pitch -> 10 + joint
# --- atlas
PPI = 100
COLS, ROWS = 12, 4                         # 36 x 40 in, 48 tiles
SEED = 2026092501
# --- relief (mm above the grout floor); dimensional-tile rule: pattern and joint are
#     separate terms and the deepest pattern point stays above the grout floor.
#     Reeded profile measured on the frontal wall photo: each 0.294 in unit is a rounded
#     convex rib (~55 %) and a flat channel (~45 %); units start/end at channel centres.
H_CREST = 1.90                             # rib top
H_VALLEY = 0.50                            # channel floor -> 0.50 mm clearance above the grout
RIB_FRACTION = 0.55
RIB_EXPONENT = 0.65                        # elliptical cap, slightly filleted at the channel
EDGE_ROUND_MM = 1.2
CHANNEL_TINT = 0.08                        # colour 8 % darker in the channels, tied to the profile


def out_path(*parts):
    target = os.path.normpath(os.path.join(RUN, *parts))
    if not target.startswith(_RUN_NORM + os.sep):
        raise RuntimeError('write escapes the run directory: ' + target)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    return target


def srgb_to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def png_header(path):
    with open(path, 'rb') as h:
        head = h.read(26)
    if head[:8] != b'\x89PNG\r\n\x1a\n':
        raise RuntimeError('not a PNG: ' + path)
    w, ht = struct.unpack('>II', head[16:24])
    return {'width': w, 'height': ht, 'bit_depth': head[24], 'colour_type': head[25]}


def save_gray16(path, a01):
    data = np.asarray(np.clip(a01, 0, 1) * 65535 + .5, dtype='>u2')
    h, w = data.shape

    def chunk(kind, payload):
        return (struct.pack('>I', len(payload)) + kind + payload
                + struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff))
    raw = b''.join(b'\x00' + row.tobytes() for row in data)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 16, 0, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))


def bilinear(img, xs, ys):
    """Sample img (H, W, C) at float coordinates (clamped)."""
    H, W = img.shape[:2]
    xs = np.clip(xs, 0, W - 1.000001)
    ys = np.clip(ys, 0, H - 1.000001)
    x0 = np.floor(xs).astype(int)
    y0 = np.floor(ys).astype(int)
    fx = (xs - x0)[..., None]
    fy = (ys - y0)[..., None]
    a = img[y0, x0]
    b = img[y0, x0 + 1]
    c = img[y0 + 1, x0]
    d = img[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def gauss_1d(a, sigma, axis):
    """Gaussian blur along one axis (reflect padding)."""
    r = int(math.ceil(3 * sigma))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r, r)
    b = np.pad(a, pad, mode='reflect')
    return np.apply_along_axis(lambda v: np.convolve(v, k, mode='valid'), axis, b)


def fold_period(profile, lo, hi, step=0.002):
    """Epoch folding: the period whose folded mean profile has the largest variance."""
    n = len(profile)
    y = np.arange(n)
    best = None
    for p in np.arange(lo, hi, step):
        ph = np.mod(y / p, 1.0)
        bins = np.minimum((ph * 48).astype(int), 47)
        m = np.bincount(bins, profile, 48) / np.maximum(np.bincount(bins, None, 48), 1)
        v = m.var()
        if best is None or v > best[1]:
            best = (p, v)
    return best[0]


# ---------------------------------------------------------------------- source
def load_swatch(report):
    path = os.path.join(REF, 'elm_page_main-image_template.jpg')
    raw = np.asarray(Image.open(path).convert('RGB')).astype(np.float64) / 255.0
    H, W = raw.shape[:2]
    lum = raw.mean(axis=2)
    colm, rowm = lum.mean(axis=0), lum.mean(axis=1)
    # trim dark photographic border rows/columns (row 0 mean 0.02, column 0 mean 0.08)
    x0 = next(i for i in range(W) if colm[i] > 0.8 * np.median(colm))
    x1 = W - next(i for i in range(W) if colm[W - 1 - i] > 0.8 * np.median(colm))
    y0 = next(i for i in range(H) if rowm[i] > 0.35 * np.median(rowm))
    y1 = H - next(i for i in range(H) if rowm[H - 1 - i] > 0.35 * np.median(rowm))
    x0, x1, y0, y1 = x0 + 2, x1 - 2, y0 + 1, y1 - 1
    sw = srgb_to_lin(raw[y0:y1, x0:x1])
    report['swatch'] = {'file': 'references/elm_page_main-image_template.jpg', 'pixels': [W, H],
                        'trim_xyxy': [int(x0), int(y0), int(x1), int(y1)],
                        'mean_srgb_255': [round(float(v) * 255, 1) for v in raw[y0:y1, x0:x1].reshape(-1, 3).mean(0)]}
    return sw


def delight(sw, report):
    H, W = sw.shape[:2]
    lum = sw.mean(axis=2)
    # 1. length-direction studio vignette: quadratic fit to column means, divided out
    xs = np.arange(W)
    colm = lum.mean(axis=0)
    cfit = np.polyval(np.polyfit(xs, colm, 2), xs)
    vign = cfit / cfit.mean()
    sw = sw / vign[None, :, None]
    # 2. flute period (epoch folding over the row profile) and tilt (per-third phase)
    rowp = sw.mean(axis=2).mean(axis=1)
    p = fold_period(rowp - rowp.mean(), 30.0, 42.0)
    thirds = []
    for i in range(3):
        seg = sw[:, i * W // 3:(i + 1) * W // 3].mean(axis=2).mean(axis=1)
        z = np.sum((seg - seg.mean()) * np.exp(-2j * np.pi * np.arange(H) / p))
        thirds.append(np.angle(z))
    dphi = np.angle(np.exp(1j * (thirds[2] - thirds[0])))
    slope = -dphi / (2 * np.pi) * p / (2 * W / 3.0)        # rows of drift per column
    # 3. per-flute shading: fold every pixel on its (tilt-corrected) phase, divide out
    yy, xx = np.mgrid[:H, :W]
    ycorr = yy - slope * (xx - W / 2.0)
    NB = 72
    ph = np.mod(ycorr / p, 1.0)
    bins = np.minimum((ph * NB).astype(int), NB - 1)
    G = np.zeros((NB, 3))
    for c in range(3):
        G[:, c] = np.bincount(bins.ravel(), sw[..., c].ravel(), NB) / np.bincount(bins.ravel(), None, NB)
    G /= G.mean(axis=0, keepdims=True)
    # smooth periodic interpolation of G at each pixel
    gx = ph * NB - 0.5
    g0 = np.floor(gx).astype(int)
    f = (gx - g0)[..., None]
    shade = G[np.mod(g0, NB)] * (1 - f) + G[np.mod(g0 + 1, NB)] * f
    d = sw / shade
    # 3b. the darkest phases (deep channel shadow) carry little colour and dividing them
    #     out amplified JPEG noise into bright specks on every channel centre (first build,
    #     2026-09-25). Where the photographed shading is below 0.8 of its mean, blend toward
    #     a copy smoothed along the flute (sigma 6 px along, 1 px across).
    gl = G.mean(axis=1)
    rel_bins = np.clip((gl - 0.35) / (0.80 - 0.35), 0, 1)
    rel = rel_bins[np.mod(g0, NB)] * (1 - f[..., 0]) + rel_bins[np.mod(g0 + 1, NB)] * f[..., 0]
    ds = np.stack([gauss_1d(gauss_1d(d[..., c], 6.0, axis=1), 1.0, axis=0) for c in range(3)], axis=2)
    d = rel[..., None] * d + (1 - rel[..., None]) * ds
    # 4. residual width-direction gradient (linear), divided out
    rows = d.mean(axis=2).mean(axis=1)
    rfit = np.polyval(np.polyfit(np.arange(H), rows, 1), np.arange(H))
    d = d / (rfit / rfit.mean())[:, None, None]
    groove_phase = (np.argmin(G.mean(axis=1)) + 0.5) / NB
    residual = np.abs(np.fft.rfft(d.mean(axis=2).mean(axis=1) - d.mean()))
    report['delight'] = {
        'vignette_peak_to_trough': round(float(vign.max() / vign.min()), 4),
        'flute_period_px': round(float(p), 4), 'tilt_rows_per_column': round(float(slope), 6),
        'flute_shading_peak_to_trough': round(float(G.mean(axis=1).max() / G.mean(axis=1).min()), 3),
        'groove_phase': round(float(groove_phase), 4),
        'row_profile_flute_harmonic_before_after': [
            round(float(np.abs(np.sum((rowp - rowp.mean()) * np.exp(-2j * np.pi * np.arange(H) / p)))), 3),
            round(float(np.abs(np.sum((d.mean(axis=2).mean(axis=1) - d.mean()) * np.exp(-2j * np.pi * np.arange(H) / p)))), 3)],
        'width_gradient_fit_slope_per_px': float(np.polyfit(np.arange(H), rows, 1)[0]),
        'max_residual_row_spectrum': round(float(residual[1:].max()), 3),
        'dark_phase_fraction_blended': round(float((rel_bins < 1).mean()), 3),
    }
    return d, p, slope, groove_phase, G


def photo3_stats(report):
    """Tile-to-tile tone spread and grout colour from the frontal installed photo (measurement only)."""
    rgb8 = np.asarray(Image.open(os.path.join(REF, 'elm_ligne-noir_3.jpg')).convert('RGB')).astype(np.float64)
    ph = srgb_to_lin(rgb8 / 255.0)
    L8 = rgb8.mean(axis=2)
    xs = [157, 341, 524, 708, 889, 1072]
    ys = [0, 603, 1241, 1876]
    prop = (723, 1635)          # fruit-stand prop occupies x > 723, y > 1635
    vals, cx, cy = [], [], []
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            x0, x1 = xs[i] + 12, xs[i + 1] - 12
            y0, y1 = ys[j] + 20, ys[j + 1] - 20
            if x1 > prop[0] and y1 > prop[1]:
                y1 = prop[1] - 20
            if y1 - y0 < 200:
                continue
            vals.append(np.percentile(L8[y0:y1, x0:x1], 80))     # lit rib tops
            cx.append((x0 + x1) / 2.0)
            cy.append((y0 + y1) / 2.0)
    v, cx, cy = np.log(np.array(vals)), np.array(cx), np.array(cy)
    # the room light falls off strongly toward the top of the photo: quadratic surface
    A = np.c_[np.ones_like(cx), cx, cy, cx ** 2, cy ** 2, cx * cy]
    coef, *_ = np.linalg.lstsq(A, v, rcond=None)
    resid = v - A @ coef
    sigma_srgb = float(np.std(resid, ddof=1))
    sigma_lin = 2.2 * sigma_srgb
    # grout: joint core pixels (1 px either side of each detected joint), away from the prop
    g = []
    for x in xs[1:-1]:
        g.append(ph[40:1600, x - 1:x + 2].reshape(-1, 3))
    for y in ys[1:3]:
        g.append(ph[y - 1:y + 2, 170:1060].reshape(-1, 3))
    g = np.concatenate(g)
    lum = g.mean(axis=1)
    core = g[lum > np.percentile(lum, 60)]          # the bright core, not the shadowed shoulders
    grout = np.median(core, axis=0)
    report['photo3'] = {'file': 'references/elm_ligne-noir_3.jpg', 'tiles_sampled': int(len(vals)),
                        'statistic': '80th percentile sRGB luminance per tile (lit rib tops)',
                        'raw_sigma_log': round(float(np.std(v, ddof=1)), 4),
                        'quadratic_detrended_sigma_log_srgb': round(sigma_srgb, 4),
                        'tile_tone_sigma_log_linear': round(sigma_lin, 4),
                        'grout_linear_rgb': [round(float(x), 4) for x in grout]}
    return sigma_lin, grout, None


# ---------------------------------------------------------------------- atlas
def periodic_noise(h, w, scale_px, rng):
    """Band-limited noise that wraps exactly (built in the Fourier domain)."""
    f = np.fft.rfft2(rng.standard_normal((h, w)))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    f *= np.exp(-(fx ** 2 + fy ** 2) * (scale_px ** 2) * 2)
    n = np.fft.irfft2(f, s=(h, w))
    return n / (n.std() + 1e-12)


def build():
    rng = np.random.default_rng(SEED)
    report = {'product': 'ELM Surfaces Vivid Ligne Noir 3x10 (matte, 7.5 mm)',
              'source_page': 'https://www.elmsurfaces.com/product/ligne-noir',
              'module_in': [MODULE_W_IN, MODULE_L_IN], 'joint_in': JOINT_IN, 'flutes_per_tile': FLUTES,
              'ppi': PPI, 'atlas_tiles': [COLS, ROWS], 'seed': SEED}
    sw = load_swatch(report)
    d, p, slope, groove_phase, G = delight(sw, report)
    sigma, grout_p3, tile_p3 = photo3_stats(report)
    Hs, Ws = d.shape[:2]

    face_w_in = MODULE_W_IN - JOINT_IN
    face_l_in = MODULE_L_IN - JOINT_IN
    flute_in = face_w_in / FLUTES
    ppi_src = p / flute_in
    len_src_true = face_l_in * ppi_src                  # source px spanning one tile length
    len_src = min(len_src_true, Ws - 1.0)               # swatch is 0.3 % short: stretch, don't clamp
    # groove-aligned strip bank: complete flutes between groove lines (at the swatch centre column)
    y_first = (groove_phase * p) % p
    n_strips = int(math.floor((Hs - 1 - y_first) / p))
    slack = Ws - 1 - len_src
    report['source_scale'] = {'flute_pitch_in': round(flute_in, 5), 'source_ppi': round(float(ppi_src), 3),
                              'tile_length_in_source_px': round(float(len_src_true), 2),
                              'length_stretch': round(float(len_src_true / len_src), 5),
                              'length_slack_px': round(float(slack), 2),
                              'complete_flute_strips': n_strips, 'first_groove_row': round(float(y_first), 3)}
    if slack < -0.02 * len_src:
        raise RuntimeError('swatch shorter than one tile length: %.1f px short' % -slack)
    slack = max(slack, 0.0)

    # per-tile variants. Distinct 10-flute strip sequences from three walks through the
    # strip bank -- cyclic forward, cyclic backward, reflected (0..n-1, n-2..1) -- deduplicated
    # as actual sequences (a backward reflected walk equals a forward one, so it is not
    # counted twice), each used with and without a length flip. No sequence+flip pair is
    # used twice; neighbours (including across the wrap) never share a sequence.
    seqs = set()
    for s0 in range(n_strips):
        seqs.add(tuple((s0 + k) % n_strips for k in range(FLUTES)))
        seqs.add(tuple((s0 - k) % n_strips for k in range(FLUTES)))
    period = 2 * n_strips - 2
    for s0 in range(period):
        seqs.add(tuple(((s0 + k) % period) if ((s0 + k) % period) < n_strips else period - ((s0 + k) % period)
                       for k in range(FLUTES)))
    seqs = sorted(seqs)
    pairs = [(q, fl) for q in range(len(seqs)) for fl in (False, True)]
    if len(pairs) < COLS * ROWS:
        raise RuntimeError('only %d distinct sequence/flip pairs for %d tiles' % (len(pairs), COLS * ROWS))
    grid = {}
    for attempt in range(2000):
        pool = [pairs[i] for i in rng.permutation(len(pairs))]
        grid, ok = {}, True
        for t in range(COLS * ROWS):
            c_, r_ = t % COLS, t // COLS
            banned = set()
            for dc, dr_ in ((-1, 0), (0, -1), (1, 0), (0, 1)):
                nb = ((c_ + dc) % COLS, (r_ + dr_) % ROWS)
                if nb in grid:
                    banned.add(grid[nb][0])
            pick = next((i for i, pr in enumerate(pool) if pr[0] not in banned), None)
            if pick is None:
                ok = False
                break
            grid[(c_, r_)] = pool.pop(pick)
        if ok:
            break
    if not ok:
        raise RuntimeError('could not place distinct neighbours')
    variants = []
    for t in range(COLS * ROWS):
        q, fl = grid[(t % COLS, t // COLS)]
        tone = float(np.exp(np.clip(rng.normal(0, sigma), -2 * sigma, 2 * sigma)))
        hue = float(rng.normal(0, 0.012))
        off = float(rng.uniform(0, slack))
        variants.append({'tile': t, 'col': t % COLS, 'row': t // COLS, 'sequence': q,
                         'strips': list(seqs[q]), 'flip_length': fl, 'tone': round(tone, 4),
                         'hue': round(hue, 4), 'length_offset_px': round(off, 2)})
    report['variant_pool'] = {'distinct_sequences': len(seqs), 'sequence_flip_pairs': len(pairs),
                              'placement_attempts': attempt + 1}

    W = int(round(COLS * MODULE_W_IN * PPI))
    H = int(round(ROWS * MODULE_L_IN * PPI))
    mpx = MM / PPI
    X, Y = np.meshgrid((np.arange(W) + 0.5) * mpx, (np.arange(H) + 0.5) * mpx)
    mw, ml, jm = MODULE_W_IN * MM, MODULE_L_IN * MM, JOINT_IN * MM
    col = np.minimum((X // mw).astype(int), COLS - 1)
    row = np.minimum((Y // ml).astype(int), ROWS - 1)
    a_mm = X - col * mw - jm / 2.0                      # across the tile face
    b_mm = Y - row * ml - jm / 2.0                      # along the tile face
    fw, fl_mm = face_w_in * MM, face_l_in * MM
    fcoord = np.clip(a_mm / (fw / FLUTES), 0, FLUTES - 1e-9)
    k = np.floor(fcoord).astype(int)
    phi = fcoord - k

    tid = row * COLS + col
    strips = np.array([v['strips'] for v in variants])            # (T, 10)
    s_idx = strips[tid, k]
    flip = np.array([v['flip_length'] for v in variants])[tid]
    off = np.array([v['length_offset_px'] for v in variants])[tid]
    bl = np.clip(b_mm / fl_mm, 0, 1)
    bl = np.where(flip, 1 - bl, bl)
    x_src = off + bl * len_src
    y_src = y_first + (s_idx + phi) * p + slope * (x_src - Ws / 2.0)
    face = bilinear(d, x_src, y_src)

    tone = np.array([v['tone'] for v in variants])[tid]
    hue = np.array([v['hue'] for v in variants])[tid]
    face = face * tone[..., None] * (1 + hue[..., None] * np.array([1.0, 0.0, -1.0]))
    xr = (phi - 0.5) / (RIB_FRACTION / 2.0)
    rib = np.clip(1 - xr ** 2, 0, 1) ** RIB_EXPONENT     # 0 in the channel, 1 on the rib top
    channel = np.clip(1 - rib * 4.0, 0, 1)                # 1 on the flat channel floor
    face = face * (1 - CHANNEL_TINT * channel)[..., None]
    # keep the swatch's own overall colour (Remedy precedent: assembled mean -> swatch mean)
    face_mean = face.reshape(-1, 3).mean(0)
    face = face * (sw.reshape(-1, 3).mean(0) / face_mean)

    # grout: the installed photo's joint-core colour as photographed (light grey), with
    # subtle wrap-exact noise. (A grout/tile ratio transfer was tried first and clipped
    # to white: the wall photo's tiles are far darker than the swatch exposure.)
    grout_lin = grout_p3
    gnoise = periodic_noise(H, W, 6.0, rng)
    grout = grout_lin[None, None, :] * (1 + 0.025 * gnoise[..., None])
    report['grout'] = {'linear_rgb': [round(float(v), 4) for v in grout_lin],
                       'srgb_255': [round(float(v) * 255, 1) for v in lin_to_srgb(grout_lin)],
                       'method': 'installed-photo joint-core median, as photographed'}

    # joint mask in mm (edge distance to the module boundary)
    ex = np.minimum(X - col * mw, (col + 1) * mw - X)
    ey = np.minimum(Y - row * ml, (row + 1) * ml - Y)
    edge = np.minimum(ex, ey)                           # distance to the nearest module edge
    t = np.clip((edge - jm / 2.0) / (0.6 * mpx) + 0.5, 0, 1)   # ~1 px anti-aliased joint edge
    colour_lin = grout * (1 - t[..., None]) + face * t[..., None]
    colour = np.uint8(np.clip(lin_to_srgb(colour_lin), 0, 1) * 255 + 0.5)

    # relief: reeded ribs over flat channels, rounded tile edges, flat grout floor
    h = H_VALLEY + (H_CREST - H_VALLEY) * rib
    dface = np.minimum(np.minimum(a_mm, fw - a_mm), np.minimum(b_mm, fl_mm - b_mm))
    te = np.clip(dface / EDGE_ROUND_MM, 0, 1)
    h = h * np.sqrt(np.clip(1 - (1 - te) ** 2, 0, 1))
    h = np.where(dface <= 0, 0.0, h)
    bump01 = h / H_CREST

    tex = out_path('textures', 'ELM_Ligne_Noir_3x10_Color.png')
    bmp = out_path('textures', 'ELM_Ligne_Noir_3x10_Bump16.png')
    Image.fromarray(colour).save(tex, optimize=True)
    save_gray16(bmp, bump01)
    report['maps'] = {'color': os.path.relpath(tex, RUN).replace(os.sep, '/'), 'bump': os.path.relpath(bmp, RUN).replace(os.sep, '/'),
                      'pixels': [W, H], 'color_header': png_header(tex), 'bump_header': png_header(bmp),
                      'color_bytes': os.path.getsize(tex), 'bump_bytes': os.path.getsize(bmp)}
    report['sample_size'] = {'width_in': COLS * MODULE_W_IN, 'height_in': ROWS * MODULE_L_IN,
                             'revit': "3'-0\" x 3'-4\"", 'pixel_aspect': W / float(H),
                             'physical_aspect': (COLS * MODULE_W_IN) / (ROWS * MODULE_L_IN)}
    report['relief_mm'] = {'height_range': H_CREST, 'flute_crest': H_CREST, 'flute_valley': H_VALLEY,
                           'pattern_relief': round(H_CREST - H_VALLEY, 3), 'grout_floor': 0.0,
                           'grout_step_crest_to_floor': H_CREST, 'clearance_valley_above_floor': H_VALLEY,
                           'edge_round': EDGE_ROUND_MM, 'rib_exponent': RIB_EXPONENT,
                           'rib_fraction': RIB_FRACTION, 'rib_width_mm': round(RIB_FRACTION * flute_in * MM, 3),
                           'channel_width_mm': round((1 - RIB_FRACTION) * flute_in * MM, 3)}
    report['variants'] = variants
    return report, colour, bump01, d, sw


# ---------------------------------------------------------------------- checks
def checks(report, colour, bump01):
    c = colour.astype(np.float64)
    out = {}
    # wrap: step across the wrap seam vs typical neighbour step (both axes)
    for name, a in (('color', c), ('bump', bump01[..., None] * 255.0)):
        seam_x = np.abs(a[:, 0] - a[:, -1]).mean()
        seam_y = np.abs(a[0] - a[-1]).mean()
        typ_x = np.abs(np.diff(a, axis=1)).mean()
        typ_y = np.abs(np.diff(a, axis=0)).mean()
        out[name + '_wrap'] = {'seam_step_x': round(float(seam_x), 4), 'typical_step_x': round(float(typ_x), 4),
                               'seam_step_y': round(float(seam_y), 4), 'typical_step_y': round(float(typ_y), 4),
                               'pass': bool(seam_x <= 1.5 * typ_x and seam_y <= 1.5 * typ_y)}
    # uniqueness: variant tuples and downsampled face hashes
    tuples = {(v['sequence'], v['flip_length']) for v in report['variants']}
    mw, ml = int(MODULE_W_IN * PPI), int(MODULE_L_IN * PPI)
    hashes = set()
    for r in range(ROWS):
        for q in range(COLS):
            cell = colour[r * ml + 12:(r + 1) * ml - 12, q * mw + 12:(q + 1) * mw - 12]
            hashes.add(hashlib.sha1(np.ascontiguousarray(cell[::4, ::4]).tobytes()).hexdigest())
    out['unique_tiles'] = {'variant_tuples': len(tuples), 'pixel_hashes': len(hashes), 'tiles': COLS * ROWS,
                           'pass': len(tuples) == len(hashes) == COLS * ROWS}
    # flute count per tile from the bump (crest runs along one row through each tile's middle)
    counts = []
    for r in range(ROWS):
        yrow = r * ml + ml // 2
        for q in range(COLS):
            seg = bump01[yrow, q * mw:(q + 1) * mw]
            crest = (seg > (H_VALLEY + 0.85 * (H_CREST - H_VALLEY)) / H_CREST).astype(int)
            counts.append(int(np.sum(np.diff(crest) == 1)))
    out['flutes_per_tile'] = {'min': min(counts), 'max': max(counts), 'pass': min(counts) == max(counts) == FLUTES}
    # clearance measured on the tile face interior (away from the rounded edge): the deepest
    # pattern point must sit above the grout floor
    mpx = MM / PPI
    xx = (np.arange(bump01.shape[1]) + 0.5) * mpx
    yy = (np.arange(bump01.shape[0]) + 0.5) * mpx
    mw_mm, ml_mm, jm = MODULE_W_IN * MM, MODULE_L_IN * MM, JOINT_IN * MM
    ax = np.mod(xx, mw_mm) - jm / 2.0
    by = np.mod(yy, ml_mm) - jm / 2.0
    inx = (ax > EDGE_ROUND_MM) & (ax < mw_mm - jm - EDGE_ROUND_MM)
    iny = (by > EDGE_ROUND_MM) & (by < ml_mm - jm - EDGE_ROUND_MM)
    interior = bump01[np.ix_(iny, inx)] * H_CREST
    floor = float(bump01.min() * H_CREST)
    out['relief'] = {'face_min_mm': round(float(interior.min()), 4), 'face_max_mm': round(float(interior.max()), 4),
                     'pattern_relief_mm': round(float(interior.max() - interior.min()), 4),
                     'grout_floor_mm': round(floor, 4),
                     'clearance_mm': round(float(interior.min()) - floor, 4),
                     'pass': bool(interior.min() - floor > 0.2)}
    ch, bh = report['maps']['color_header'], report['maps']['bump_header']
    out['headers'] = {'pass': ch['bit_depth'] == 8 and ch['colour_type'] == 2 and bh['bit_depth'] == 16
                      and bh['colour_type'] == 0 and (ch['width'], ch['height']) == (bh['width'], bh['height'])}
    ss = report['sample_size']
    out['aspect'] = {'pass': abs(ss['pixel_aspect'] - ss['physical_aspect']) < 1e-9}
    out['all_pass'] = all(v.get('pass', True) for v in out.values() if isinstance(v, dict))
    report['checks'] = out
    return out


# ---------------------------------------------------------------------- previews
def shade(colour8, bump01, light, spec_k=0.25, amb=0.35, exag=1.0):
    base = srgb_to_lin(colour8.astype(np.float64) / 255.0)
    mpx = MM / PPI
    dy, dx = np.gradient(bump01 * H_CREST * exag, mpx, mpx)
    n = np.stack([-dx, -dy, np.ones_like(dx)], axis=2)
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    L = np.asarray(light, float)
    L /= np.linalg.norm(L)
    hv = L + np.array([0, 0, 1.0])
    hv /= np.linalg.norm(hv)
    diff = np.maximum(0, n @ L)
    spec = np.maximum(0, n @ hv) ** 30
    lin = base * (amb + 1.6 * diff[..., None]) + spec_k * spec[..., None] * 0.2
    return np.uint8(np.clip(lin_to_srgb(lin), 0, 1) * 255 + 0.5)


def previews(report, colour, bump01, d, sw):
    # source review: original swatch / de-lit swatch / strip bank boundaries
    raw = np.asarray(Image.open(os.path.join(REF, 'elm_page_main-image_template.jpg')).convert('RGB'))
    x0, y0, x1, y1 = report['swatch']['trim_xyxy']
    raw = raw[y0:y1, x0:x1]
    gain = 0.18 / max(sw.mean(), 1e-6)                     # same display gain for both
    a = np.uint8(np.clip(lin_to_srgb(sw * gain), 0, 1) * 255 + .5)
    b = np.uint8(np.clip(lin_to_srgb(d * gain), 0, 1) * 255 + .5)
    c = b.copy()
    p = report['delight']['flute_period_px']
    yf = report['source_scale']['first_groove_row']
    for s in range(report['source_scale']['complete_flute_strips'] + 1):
        yy = int(round(yf + s * p))
        if 0 <= yy < c.shape[0]:
            c[yy, :] = [230, 40, 40]
    stack = np.concatenate([raw, np.full((6, raw.shape[1], 3), 255, np.uint8), a,
                            np.full((6, raw.shape[1], 3), 255, np.uint8), b,
                            np.full((6, raw.shape[1], 3), 255, np.uint8), c], axis=0)
    Image.fromarray(stack).save(out_path('textures', '_REVIEW_source_ligne_noir.jpg'), quality=92)
    # 2x2 wraps
    def tile2(img):
        return np.tile(img, (2, 2, 1)) if img.ndim == 3 else np.tile(img, (2, 2))
    Image.fromarray(tile2(colour)).resize((1440, 1600), Image.LANCZOS).save(
        out_path('textures', '_PREVIEW_tiling_ligne_noir.jpg'), quality=90)
    Image.fromarray(np.uint8(tile2(bump01) * 255)).resize((1440, 1600), Image.LANCZOS).save(
        out_path('textures', '_PREVIEW_bump_tiling_ligne_noir.jpg'), quality=90)
    # grazing light across the flutes (flutes run along Y; light from +X, 12 deg above the surface)
    g = shade(colour, bump01, (math.cos(math.radians(12)), 0.15, math.sin(math.radians(12))), amb=0.12)
    Image.fromarray(tile2(g)).resize((1440, 1600), Image.LANCZOS).save(
        out_path('textures', '_PREVIEW_grazing_light_ligne_noir.jpg'), quality=90)
    # four-way wrap corner at 2x (seams must be invisible)
    t = tile2(colour)
    Hh, Ww = colour.shape[:2]
    corner = t[Hh - 200:Hh + 200, Ww - 200:Ww + 200]
    Image.fromarray(corner).resize((800, 800), Image.NEAREST).save(
        out_path('textures', '_PREVIEW_corner_wrap_ligne_noir.jpg'), quality=92)
    # flute close-up: one tile's middle, grazing + frontal key light
    cu = shade(colour, bump01, (0.9, 0.2, 0.35), amb=0.18)
    ml, mw = int(MODULE_L_IN * PPI), int(MODULE_W_IN * PPI)
    crop = cu[ml + 200:ml + 500, 2 * mw - 60:3 * mw + 60]
    Image.fromarray(crop).resize((crop.shape[1] * 3, crop.shape[0] * 3), Image.LANCZOS).save(
        out_path('textures', '_PREVIEW_flute_profile_closeup.jpg'), quality=93)
    # room scale: 8 ft x 8 ft wall at 12 px/in, soft light from upper left
    rs = shade(colour, bump01, (0.45, -0.35, 0.82), amb=0.3)
    small = np.asarray(Image.fromarray(rs).resize((432, 480), Image.LANCZOS))
    wall = np.tile(small, (3, 3, 1))[:1152, :1152]
    Image.fromarray(wall).save(out_path('textures', '_PREVIEW_room_scale_8ft_ligne_noir.jpg'), quality=90)


def main():
    report, colour, bump01, d, sw = build()
    res = checks(report, colour, bump01)
    previews(report, colour, bump01, d, sw)
    with open(out_path('textures', 'ligne_noir_build_report.json'), 'w') as fh:
        json.dump(report, fh, indent=2)
    print(json.dumps({k: report[k] for k in ('swatch', 'delight', 'source_scale', 'photo3', 'grout', 'maps',
                                              'sample_size', 'relief_mm')}, indent=1))
    print(json.dumps(res, indent=1))
    return 0 if res['all_pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
