"""Porcelanosa / L'Antic Colonial Medina Fes + Medina Ifrane, 16 x 16 cm ("6x6") glossy ceramic.

Outputs (all pixel-registered, one shared tile layout):
  Medina_Fes_Color.png, Medina_Ifrane_Color.png, Medina_Fes_Ifrane_Mix_Color.png  (8-bit sRGB)
  Medina_Normal16_OpenGL.png  (16-bit RGB, shared by all three)
  Medina_Bump16.png           (16-bit grey, same height field, companion)

Colour: per-tile body colours measured from the manufacturer's frontal wall images
(extract_tiles.py -> tile_samples.npz), one exposure gain per colourway (white basin -> sRGB 235),
tile-to-tile ratios kept exactly as measured, each cell drawn uniformly with replacement.
In-tile clouding: low-reflection measured fields of the same colourway. Fine glaze detail:
each colourway's own studio swatch (store image), high-pass only.
Relief: procedural handmade glaze -- irregular rounded (pillowed) edges, per-tile bow, glaze
waviness, pinholes. Spec says relief "No": amplitudes kept modest.
"""
import json
import os
import struct
import sys
import zlib

import numpy as np
from PIL import Image
from scipy import ndimage

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(RUN_DIR, "references")

TILE_MM = 160.0               # tech sheet 6-77/256 in; catalog 16 x 16 cm
JOINT_MM = 2.0                # not stated; consistent with the ~6.5 mm visible line incl. rounded edges
MODULE_MM = TILE_MM + JOINT_MM
N = 16                        # 16 x 16 tiles (rev 2: 10 x 10 repeat was visible at room scale)
PX_PER_MM = 2.0
MOD_PX = int(round(MODULE_MM * PX_PER_MM))        # 324
W = H = N * MOD_PX                                 # 5184
MM_PER_PX = MODULE_MM / MOD_PX

# exposure anchor and grout colour
BASIN_SRGB = 235.0            # white basin in each source scene mapped to this
GROUT_SRGB = (168, 166, 162)  # Colorstuk Rapid Gris N, neutral mid-light grey (assumed tone)

# relief (mm, grout floor = 0)
FACE_MM = 2.00                # glaze face above grout
EDGE_DROP_MM = 0.90           # pillowed edge roll-off height
ROLL_MM = 3.5                 # width of the roll-off
CORNER_R_MM = 2.5
EDGE_JITTER_MM = 0.45         # irregular edge outline amplitude
BOW_MM = 0.30                 # per-tile bow / tilt amplitude
WAVE_MM = 0.12                # glaze waviness RMS
WAVE_LAMBDA_MM = (20.0, 70.0) # band of waviness wavelengths (rev 2: 8-40 mm read as orange peel)
PIN_DEPTH_MM = 0.12
PIN_PER_TILE = 6
SEED = 20261113

TRANSFORMS = ["r0", "r90", "r180", "r270", "m_r0", "m_r90", "m_r180", "m_r270"]
SWATCH = {"fes": "100365178_T.jpg", "ifrane": "100365179_T.jpg"}
SWATCH_BOX = (570, 333, 1319, 1083)   # x0 y0 x1 y1 tile in the 1920 x 1440 store image
NAMES = {"fes": "Medina_Fes", "ifrane": "Medina_Ifrane", "mix": "Medina_Fes_Ifrane_Mix"}


def out_path(*parts):
    p = os.path.abspath(os.path.join(RUN_DIR, *parts))
    if not p.startswith(RUN_DIR + os.sep):
        raise RuntimeError("write outside run dir refused: " + p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def srgb_to_lin(c):
    c = np.asarray(c, dtype=np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def apply_t(a, t):
    if t.startswith("m_"):
        a = a[:, ::-1]
        t = t[2:]
    return np.rot90(a, {"r0": 0, "r90": 1, "r180": 2, "r270": 3}[t], axes=(0, 1))


def resize_f(a, size):
    if a.ndim == 2:
        return np.asarray(Image.fromarray(a.astype(np.float32), "F").resize(size, Image.BICUBIC), dtype=np.float64)
    return np.stack([resize_f(a[..., k], size) for k in range(a.shape[2])], -1)


def write_png16(path, arr, rgb):
    a = np.clip(np.round(arr * 65535.0), 0, 65535).astype(">u2")
    h, w = a.shape[:2]
    raw = b"".join(b"\x00" + a[y].tobytes() for y in range(h))

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 16, 2 if rgb else 0, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def png_header(path):
    with open(path, "rb") as f:
        b = f.read(26)
    w, h = struct.unpack(">II", b[16:24])
    return {"width": w, "height": h, "bit_depth": b[24], "color_type": b[25]}


def periodic_band_noise(rng, shape, lam_mm, mm_per_px):
    """Seamless (periodic) noise band-limited to wavelengths lam_mm, unit RMS."""
    f = np.fft.fft2(rng.standard_normal(shape))
    fy = np.fft.fftfreq(shape[0], d=mm_per_px)[:, None]
    fx = np.fft.fftfreq(shape[1], d=mm_per_px)[None, :]
    fr = np.sqrt(fx ** 2 + fy ** 2)
    lo, hi = 1 / lam_mm[1], 1 / lam_mm[0]
    filt = np.exp(-0.5 * ((np.log(np.maximum(fr, 1e-9)) - np.log(np.sqrt(lo * hi))) / (0.5 * np.log(hi / lo))) ** 2)
    filt[0, 0] = 0
    n = np.real(np.fft.ifft2(f * filt))
    return n / n.std()


def smooth_1d(rng, n_px, corr_px):
    x = ndimage.gaussian_filter1d(rng.standard_normal(n_px + 4 * corr_px), corr_px, mode="wrap")[2 * corr_px:2 * corr_px + n_px]
    return x / (x.std() + 1e-12)


def layout_samples(rng, n_samples):
    """N x N sample indices, uniform with replacement, no equal 4-neighbours (wrap)."""
    g = -np.ones((N, N), int)
    for r in range(N):
        for c in range(N):
            for _ in range(1000):
                k = int(rng.integers(n_samples))
                nb = {g[(r - 1) % N, c], g[r, (c - 1) % N], g[(r + 1) % N, c], g[r, (c + 1) % N]}
                if k not in nb:
                    g[r, c] = k
                    break
            else:
                raise RuntimeError("could not place sample without an equal neighbour")
    return g


def adjacent_equal(g):
    return int((g == np.roll(g, 1, 0)).sum() + (g == np.roll(g, 1, 1)).sum())


def main():
    rng = np.random.default_rng(SEED)
    rep = {"seed": SEED, "tile_mm": TILE_MM, "joint_mm": JOINT_MM, "module_mm": MODULE_MM, "tiles": [N, N],
           "px": [W, H], "px_per_mm": MOD_PX / MODULE_MM}
    S = json.load(open(os.path.join(RUN_DIR, "source", "tile_samples.json"), encoding="utf-8"))
    D = np.load(os.path.join(RUN_DIR, "source", "tile_samples.npz"))

    face_px = MOD_PX  # cell canvas; face outline cut by the edge SDF below
    # ---------- per-colourway inputs ----------
    cw = {}
    for k in ("fes", "ifrane"):
        wb = np.array(S[k]["white_balance_gain"])
        basin = srgb_to_lin(np.array(S[k]["neutral_srgb"]) / 255.0) * wb
        gain = float(srgb_to_lin(BASIN_SRGB / 255.0) / basin.mean())
        cols = D[k + "_colour_lin"] * gain
        refl = D[k + "_refl"]
        fields = D[k + "_field"][refl <= np.median(refl)]          # low-reflection clouding only
        # studio swatch: high-pass luminance detail
        sw = np.asarray(Image.open(os.path.join(REF, SWATCH[k])).convert("RGB")).astype(np.float64) / 255.0
        x0, y0, x1, y1 = SWATCH_BOX
        sw = srgb_to_lin(sw[y0 + 30:y1 - 30, x0 + 30:x1 - 30]).mean(2)
        det = sw / ndimage.gaussian_filter(sw, 6)
        det = np.clip(det, 0.80, 1.15)
        det = resize_f(det, (face_px, face_px))
        det = det / det.mean()                                      # detail never shifts tile colour
        cw[k] = {"gain": gain, "cols": cols, "fields": fields, "detail": det}
        s8 = lin_to_srgb(cols) * 255
        rep[k] = {"exposure_gain": round(gain, 4), "samples": len(cols), "clouding_fields": len(fields),
                  "colour_srgb_min": s8.min(0).round(1).tolist(), "colour_srgb_median": np.median(s8, 0).round(1).tolist(),
                  "colour_srgb_max": s8.max(0).round(1).tolist()}

    # ---------- layout (shared) ----------
    samp = {k: layout_samples(rng, len(cw[k]["cols"])) for k in ("fes", "ifrane")}
    choose_fes = rng.random((N, N)) < 0.5
    t_field = rng.integers(8, size=(N, N, 2))           # transform for clouding field, per colourway
    t_det = rng.integers(8, size=(N, N, 2))
    f_idx = {k: rng.integers(len(cw[k]["fields"]), size=(N, N)) for k in ("fes", "ifrane")}
    rep["layout"] = {"fes_samples": samp["fes"].tolist(), "ifrane_samples": samp["ifrane"].tolist(),
                     "mix_is_fes": choose_fes.astype(int).tolist(), "mix_fes_count": int(choose_fes.sum())}

    # ---------- height field (shared) ----------
    yy, xx = np.mgrid[0:H, 0:W]
    u = (xx % MOD_PX + 0.5) * MM_PER_PX            # mm within module
    v = (yy % MOD_PX + 0.5) * MM_PER_PX
    tc, tr = xx // MOD_PX, yy // MOD_PX
    half = JOINT_MM / 2
    jit = np.zeros((4, N, N, MOD_PX))
    for i in range(4):
        for r in range(N):
            for c in range(N):
                jit[i, r, c] = smooth_1d(rng, MOD_PX, int(18 * PX_PER_MM)) * EDGE_JITTER_MM
    pi = (yy % MOD_PX)
    pj = (xx % MOD_PX)
    dl = u - half - np.abs(jit[0, tr, tc, pi])
    dr = MODULE_MM - half - u - np.abs(jit[1, tr, tc, pi])
    dt = v - half - np.abs(jit[2, tr, tc, pj])
    db = MODULE_MM - half - v - np.abs(jit[3, tr, tc, pj])
    dx = np.minimum(dl, dr)
    dy = np.minimum(dt, db)
    R = CORNER_R_MM
    d = np.where((dx < R) & (dy < R), R - np.hypot(np.maximum(R - dx, 0), np.maximum(R - dy, 0)), np.minimum(dx, dy))
    face = d > 0
    # per-tile bow: tilt + quadratic, random per tile
    cu, cv = (u - MODULE_MM / 2) / (MODULE_MM / 2), (v - MODULE_MM / 2) / (MODULE_MM / 2)
    co = rng.uniform(-1, 1, size=(N, N, 4))
    bow = BOW_MM * 0.25 * (co[tr, tc, 0] * cu + co[tr, tc, 1] * cv + co[tr, tc, 2] * (cu ** 2 + cv ** 2 - 0.67)
                          + co[tr, tc, 3] * cu * cv)
    wave = periodic_band_noise(rng, (H, W), WAVE_LAMBDA_MM, MM_PER_PX) * WAVE_MM
    pins = np.zeros((H, W))
    sig_px = 0.35 * PX_PER_MM
    for r in range(N):
        for c in range(N):
            for _ in range(rng.poisson(PIN_PER_TILE)):
                py = int(r * MOD_PX + rng.uniform(8, 154) * PX_PER_MM)
                px = int(c * MOD_PX + rng.uniform(8, 154) * PX_PER_MM)
                pins[py, px] = 1.0
    pins = ndimage.gaussian_filter(pins, sig_px, mode="wrap")
    pins = pins / max(pins.max(), 1e-12) * PIN_DEPTH_MM
    roll = np.clip(d / ROLL_MM, 0, 1)
    edge = EDGE_DROP_MM * (1 - roll) ** 2
    h_face = FACE_MM + bow + wave - pins - edge
    grout_tex = ndimage.gaussian_filter(rng.standard_normal((H, W)), 0.8, mode="wrap") * 0.03
    # smooth step across the outline (0.5 mm) to avoid aliasing cliffs
    a = np.clip(d / 0.5 + 0.5, 0, 1)
    hmm = a * h_face + (1 - a) * (0.15 + grout_tex)
    face_min = float(h_face[face].min())
    rep["height_mm"] = {"grout_floor": 0.15, "face_nominal": FACE_MM, "edge_drop": EDGE_DROP_MM, "roll_width": ROLL_MM,
                        "edge_jitter": EDGE_JITTER_MM, "bow_amp": BOW_MM, "wave_rms": WAVE_MM,
                        "wave_lambda_mm": list(WAVE_LAMBDA_MM), "pin_depth": PIN_DEPTH_MM,
                        "face_min": face_min, "face_max": float(h_face[face].max()),
                        "clearance_above_grout": face_min - float((0.15 + grout_tex).max())}

    # ---------- normal + bump ----------
    gx = (np.roll(hmm, -1, 1) - np.roll(hmm, 1, 1)) / (2 * MM_PER_PX)
    gy = (np.roll(hmm, -1, 0) - np.roll(hmm, 1, 0)) / (2 * MM_PER_PX)
    nrm = np.stack([-gx, gy, np.ones_like(hmm)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    lo, hi = float(hmm.min()), float(hmm.max())
    rep["bump_range_mm"] = [lo, hi]

    # ---------- colour maps ----------
    grout = srgb_to_lin(np.array(GROUT_SRGB) / 255.0)
    maps = {}
    placed = {"fes": [], "ifrane": []}
    for key in ("fes", "ifrane", "mix"):
        img = np.zeros((H, W, 3))
        for r in range(N):
            for c in range(N):
                k = key if key != "mix" else ("fes" if choose_fes[r, c] else "ifrane")
                ki = 0 if k == "fes" else 1
                col = cw[k]["cols"][samp[k][r, c]]
                fld = apply_t(cw[k]["fields"][f_idx[k][r, c]], TRANSFORMS[t_field[r, c, ki]])
                fld = resize_f(fld, (face_px, face_px))
                det = apply_t(cw[k]["detail"], TRANSFORMS[t_det[r, c, ki]])
                img[r * MOD_PX:(r + 1) * MOD_PX, c * MOD_PX:(c + 1) * MOD_PX] = col * fld * det[..., None]
                if key != "mix":
                    placed[k].append(col)
        img = a[..., None] * img + (1 - a[..., None]) * grout
        maps[key] = img
    # placed vs measured colour per cell: face interior (>5 mm from the outline), linear RGB ratio
    inner = d > 5.0
    for key in ("fes", "ifrane", "mix"):
        ratios = []
        for r in range(N):
            for c in range(N):
                k = key if key != "mix" else ("fes" if choose_fes[r, c] else "ifrane")
                sl = (slice(r * MOD_PX, (r + 1) * MOD_PX), slice(c * MOD_PX, (c + 1) * MOD_PX))
                m = inner[sl]
                ratios.append(maps[key][sl][m].mean(0) / cw[k]["cols"][samp[k][r, c]])
        ratios = np.array(ratios)
        rep.setdefault("placed_colour_ratio", {})[key] = {"mean": ratios.mean(0).round(4).tolist(),
                                                           "sd": ratios.std(0).round(4).tolist()}
    for k in ("fes", "ifrane"):
        p = np.array(placed[k])
        meas = cw[k]["cols"]
        rep[k]["placed_vs_measured_lum_mean"] = [float(p.mean(1).mean()), float(meas.mean(1).mean())]
        rep[k]["placed_vs_measured_lum_sd"] = [float(p.mean(1).std()), float(meas.mean(1).std())]
        rep[k]["distinct_samples_used"] = int(len(np.unique(samp[k])))

    # ---------- export ----------
    tex = {}
    for key, img in maps.items():
        tex[key] = out_path("textures", NAMES[key] + "_Color.png")
        Image.fromarray(np.clip(np.round(lin_to_srgb(img) * 255), 0, 255).astype(np.uint8), "RGB").save(tex[key], optimize=True)
    tex["normal"] = out_path("textures", "Medina_Normal16_OpenGL.png")
    tex["bump"] = out_path("textures", "Medina_Bump16.png")
    write_png16(tex["normal"], nrm * 0.5 + 0.5, rgb=True)
    write_png16(tex["bump"], (hmm - lo) / (hi - lo), rgb=False)

    # ---------- checks ----------
    hdr = {k: png_header(p) for k, p in tex.items()}
    rep["png_headers"] = hdr
    chk = {}
    chk["colour_8bit_rgb"] = all(hdr[k]["bit_depth"] == 8 and hdr[k]["color_type"] == 2 for k in ("fes", "ifrane", "mix"))
    chk["normal_16bit_rgb"] = hdr["normal"]["bit_depth"] == 16 and hdr["normal"]["color_type"] == 2
    chk["bump_16bit_grey"] = hdr["bump"]["bit_depth"] == 16 and hdr["bump"]["color_type"] == 0
    chk["all_same_size_square"] = len({(h["width"], h["height"]) for h in hdr.values()}) == 1 and W == H
    chk["no_equal_neighbour_samples"] = adjacent_equal(samp["fes"]) == 0 and adjacent_equal(samp["ifrane"]) == 0
    chk["clearance_positive"] = rep["height_mm"]["clearance_above_grout"] > 0
    chk["placed_colour_matches_measured"] = all(
        max(abs(m - 1) for m in v["mean"]) < 0.01 and max(v["sd"]) < 0.01 for v in rep["placed_colour_ratio"].values())

    def wrap(a):
        a = a if a.ndim == 3 else a[..., None]
        typ = float(np.abs(np.diff(a, axis=1)).mean())
        return {"typical": typ, "wrap_x": float(np.abs(a[:, 0] - a[:, -1]).mean()),
                "wrap_y": float(np.abs(a[0] - a[-1]).mean())}
    rep["wrap"] = {"height": wrap(hmm), "normal": wrap(nrm), **{k: wrap(maps[k]) for k in maps}}
    chk["wrap_seamless"] = all(w_["wrap_x"] <= 2 * w_["typical"] + 1e-9 and w_["wrap_y"] <= 2 * w_["typical"] + 1e-9
                               for w_ in rep["wrap"].values())
    rep["checks"] = chk
    rep["pass"] = all(chk.values())
    rep["sample_size"] = {"mm": N * MODULE_MM, "in": round(N * MODULE_MM / 25.4, 3)}
    with open(out_path("source", "build_report.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, indent=1)

    # ---------- previews ----------
    def small(img_lin, name, size=1600):
        im = Image.fromarray((lin_to_srgb(img_lin) * 255).astype(np.uint8))
        im.thumbnail((size, size), Image.LANCZOS)
        im.save(out_path("source", name), quality=90)
    for key, img in maps.items():
        small(img, f"_PREVIEW_{NAMES[key]}_Color.jpg", 1400)
        s = Image.fromarray((lin_to_srgb(img) * 255).astype(np.uint8)).resize((W // 8, H // 8), Image.LANCZOS)
        Image.fromarray(np.tile(np.asarray(s), (3, 3, 1))).save(out_path("source", f"_PREVIEW_{NAMES[key]}_room_3x3.jpg"), quality=88)
    # reflection preview: glossy surface seen at a glancing angle reflecting a bright window strip set
    n = nrm
    a_el = np.radians(25)
    vdir = np.array([0.0, np.cos(a_el), -np.sin(a_el)])       # looking along +y (image up), down onto surface
    vdir = vdir / np.linalg.norm(vdir)
    dot = (n * vdir).sum(-1, keepdims=True)
    rv = vdir - 2 * dot * n
    el = np.degrees(np.arcsin(np.clip(rv[..., 2], -1, 1)))
    az = np.degrees(np.arctan2(rv[..., 0], rv[..., 1]))
    win = ((np.abs(el - 25) < 4) & (np.abs((az + 15) % 30 - 15) < 6)).astype(float)   # flat face sits in a window band
    win = ndimage.gaussian_filter(win, 0.7)
    base = lin_to_srgb(maps["mix"]) * 0.75
    refl_img = np.clip(base + 0.9 * win[..., None], 0, 1)
    crop = refl_img[:3 * MOD_PX, :3 * MOD_PX]
    Image.fromarray((crop * 255).astype(np.uint8)).resize((1200, 1200), Image.LANCZOS).save(
        out_path("source", "_PREVIEW_reflection_3x3_tiles.jpg"), quality=90)
    # grazing diffuse close-up of one four-way corner
    L = np.array([-np.cos(np.radians(12)), 0.3, np.sin(np.radians(12))])
    L /= np.linalg.norm(L)
    sh = np.clip((n * L).sum(-1), 0, None)
    cy = cx = MOD_PX * 2
    hw = int(60 * PX_PER_MM)
    c2 = sh[cy - hw:cy + hw, cx - hw:cx + hw]
    c2 = np.clip(c2 / np.percentile(c2, 99.5), 0, 1)
    Image.fromarray((c2 * 255).astype(np.uint8)).resize((900, 900), Image.LANCZOS).save(
        out_path("source", "_PREVIEW_grazing_corner_120mm.jpg"), quality=92)
    nc = (n[cy - hw:cy + hw, cx - hw:cx + hw] * 0.5 + 0.5)
    Image.fromarray((nc * 255).astype(np.uint8)).resize((900, 900), Image.LANCZOS).save(
        out_path("source", "_PREVIEW_normal_corner_120mm.jpg"), quality=92)

    print(json.dumps({"pass": rep["pass"], "checks": chk, "height_mm": rep["height_mm"],
                      "fes": rep["fes"], "ifrane": rep["ifrane"], "mix_fes_count": rep["layout"]["mix_fes_count"],
                      "sample_size": rep["sample_size"]}, indent=1))
    if not rep["pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
