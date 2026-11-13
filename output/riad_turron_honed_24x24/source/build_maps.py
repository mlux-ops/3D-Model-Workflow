"""Riad Tile Turron 24x24 Venezia Terrazzo (honed) - colour, 16-bit bump and 16-bit normal maps.

Source: the manufacturer's flat straight-on product swatch TerrazzoTurron24x24.jpg (3000 x 3000).
See ../SOURCE_SELECTION.md. Every pixel of tile face content comes from that one photo.

Atlas: 4 columns x 2 rows of 24 in modules (23-15/16 in tile + 1/16 in joint, half a joint on each
outer edge so the image wraps). A square tile has 8 shape-preserving symmetries (4 rotations x mirror);
terrazzo is isotropic, so each of the 8 cells gets a different one of the 8 transforms -> no cell
is a copy of another cell. Sample Size 96 x 48 in (8'-0" x 4'-0").

Height model (mm, grout floor = 0): joint recess + eased edge, flush honed chips with a hairline
boundary seam, and fine porosity in the cement matrix taken from the photo's own speckle.
Float64 throughout; quantised on export only.
"""
import json
import os
import struct
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "Riad_Turron_Honed_24x24"
SRC = os.path.join(RUN_DIR, "references", "TerrazzoTurron24x24.jpg")

# ---- physical layout ------------------------------------------------------------------------
PX_PER_IN = 64
MODULE_IN = 24.0                       # nominal = installed module (tile + joint)
JOINT_IN = 1.0 / 16.0                  # assumed, not stated by manufacturer
COLS, ROWS = 4, 2
MODULE_PX = int(MODULE_IN * PX_PER_IN)           # 1536
W, H = COLS * MODULE_PX, ROWS * MODULE_PX        # 6144 x 3072
MM_PER_PX = 25.4 / PX_PER_IN                     # 0.396875

# ---- source face crop (measured from silhouette fits, see SOURCE_SELECTION.md) ---------------
FACE_BOX = (378, 372, 2662, 2660)      # x0, y0, x1, y1 of the tile face in the 3000 px swatch
INSET = 22                              # px trimmed each side to drop eased edge / side band
CHIP_DIST = 0.11                        # sRGB distance from matrix colour that counts as chip
CHIP_MIN_PX = 150                       # source px (~10 mm^2); smaller specks are matrix aggregate

# ---- height terms (mm) ------------------------------------------------------------------------
FACE_MM = 1.00          # tile face above grout floor (joint step)
EASE_MM = 0.35          # height lost across the eased edge
EASE_W_MM = 2.0         # width of eased edge transition
PORE_MM = 0.06          # matrix porosity / sand-grain relief amplitude (peak-ish, 3 sigma)
CHIP_SEAM_MM = 0.03     # hairline dip at chip / matrix boundary
CHIP_SMOOTH = 0.15      # fraction of matrix micro-texture left on honed chips

SEED = 20261113
TRANSFORMS = ["r0", "r90", "r180", "r270", "m_r0", "m_r90", "m_r180", "m_r270"]
# Layout found by exhaustive search (one of two solutions with r0 at top-left): at every joint,
# including across the wrap, the two cells present DIFFERENT source edges, and at every four-way
# corner the four cells present four different source corners. Otherwise the same strip of
# chips meets its own mirror image across the joint and reads as a kaleidoscope (rev 1 failed so).
LAYOUT = [["r0", "m_r90", "r180", "m_r270"],
          ["m_r0", "r270", "m_r180", "r90"]]


def edge_labels(t):
    """Which source edge / corner lands on each side / corner of a cell under transform t."""
    n = 5
    a = np.zeros((n, n), int)
    a[0, 1:-1], a[1:-1, -1], a[-1, 1:-1], a[1:-1, 0] = 1, 2, 3, 4
    a[0, 0], a[0, -1], a[-1, -1], a[-1, 0] = 5, 6, 7, 8
    x = apply_t(a, t)
    return {"T": x[0, 2], "R": x[2, -1], "B": x[-1, 2], "L": x[2, 0],
            "TL": x[0, 0], "TR": x[0, -1], "BR": x[-1, -1], "BL": x[-1, 0]}


def layout_ok(g):
    rows, cols = len(g), len(g[0])
    for r in range(rows):
        for c in range(cols):
            A = edge_labels(g[r][c])
            B = edge_labels(g[r][(c + 1) % cols])
            D = edge_labels(g[(r + 1) % rows][c])
            E = edge_labels(g[(r + 1) % rows][(c + 1) % cols])
            if A["R"] == B["L"] or A["B"] == D["T"]:
                return False
            if len({A["BR"], B["BL"], D["TR"], E["TL"]}) < 4:
                return False
    return True


def out_path(*parts):
    p = os.path.abspath(os.path.join(RUN_DIR, *parts))
    if not p.startswith(RUN_DIR + os.sep):
        raise RuntimeError("write outside run dir refused: " + p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def srgb_to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def apply_t(a, t):
    if t.startswith("m_"):
        a = a[:, ::-1]
        t = t[2:]
    k = {"r0": 0, "r90": 1, "r180": 2, "r270": 3}[t]
    return np.rot90(a, k, axes=(0, 1))


def write_png16(path, arr, rgb):
    a = np.clip(np.round(arr * 65535.0), 0, 65535).astype(">u2")
    h, w = a.shape[:2]
    import zlib
    ctype = 2 if rgb else 0
    raw = b"".join(b"\x00" + a[y].tobytes() for y in range(h))

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 16, ctype, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def png_header(path):
    with open(path, "rb") as f:
        b = f.read(26)
    w, h = struct.unpack(">II", b[16:24])
    return {"width": w, "height": h, "bit_depth": b[24], "color_type": b[25]}


def main():
    report = {"name": NAME, "source": os.path.basename(SRC), "seed": SEED}
    rng = np.random.default_rng(SEED)

    # ---------- 1. source face: crop, de-light, segment ----------
    src = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float64) / 255.0
    x0, y0, x1, y1 = FACE_BOX
    face = src[y0 + INSET:y1 - INSET, x0 + INSET:x1 - INSET]
    report["source_crop_px"] = [x0 + INSET, y0 + INSET, x1 - INSET, y1 - INSET]
    lin = srgb_to_lin(face)

    def chip_mask(img, min_px):
        """Chips = pixels far in colour from the cement matrix; tiny components dropped."""
        sat = img.max(2) - img.min(2)
        lum = img.mean(2)
        seed = (sat < np.percentile(sat, 35)) & (lum > np.percentile(lum, 30))
        ref = np.median(img[seed], axis=0)
        m = np.sqrt(((img - ref) ** 2).sum(2)) > CHIP_DIST
        m = ndimage.binary_opening(m, iterations=1)
        m = ndimage.binary_closing(m, iterations=2)
        lab, n = ndimage.label(m)
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        keep = np.zeros(n + 1, bool)
        keep[1:] = sizes >= min_px
        return ndimage.binary_fill_holes(keep[lab]), ref

    # pass 1 on the raw photo, only to find the matrix for the light estimate
    chip0, _ = chip_mask(face, 40)

    # baked studio light: low-frequency luminance of matrix only (normalised convolution)
    matrix = ~ndimage.binary_dilation(chip0, iterations=4)
    ml = lin.mean(2) * matrix
    sig = 180
    num = ndimage.gaussian_filter(ml, sig, mode="reflect")
    den = ndimage.gaussian_filter(matrix.astype(float), sig, mode="reflect")
    field = num / np.maximum(den, 1e-6)
    gain = field.mean() / field
    report["light_field_range"] = [float(field.min() / field.mean()), float(field.max() / field.mean())]
    lin = lin * gain[..., None]
    face_c = lin_to_srgb(lin)

    # pass 2 on the de-lit colour (rev 2: pass 1 alone flagged matrix speckle as chip where the
    # studio light was dimmer, which put seam dips and smoothed porosity into plain matrix)
    chip, mref = chip_mask(face_c, CHIP_MIN_PX)
    report["chip_fraction"] = float(chip.mean())
    report["chip_fraction_pass1_raw"] = float(chip0.mean())
    report["matrix_ref_srgb"] = [round(float(v) * 255, 1) for v in mref]

    # ---------- 2. resample to tile-face pixels ----------
    half_j = JOINT_IN / 2 * PX_PER_IN                 # 2 px
    face_px = int(round(MODULE_PX - 2 * half_j))      # 1532
    def rs(a, mode):
        im = Image.fromarray(a.astype(np.float32), mode="F")
        return np.asarray(im.resize((face_px, face_px), mode), dtype=np.float64)
    lin_r = np.stack([rs(lin[..., c], Image.LANCZOS) for c in range(3)], -1)
    chip_r = rs(chip.astype(float), Image.BILINEAR)
    lum_r = rs(face_c.mean(2), Image.LANCZOS)
    report["resample_scale"] = face_px / face.shape[0]
    scale_err = (face.shape[0] + 2 * INSET) / face.shape[0] - 1
    report["inset_stretch_pct"] = round(100 * scale_err, 2)

    # ---------- 3. per-face height (mm, relative to face) ----------
    matrix_r = 1 - np.clip(chip_r, 0, 1)
    hp = lum_r - ndimage.gaussian_filter(lum_r, 3)                # fine speckle / pores
    # porosity is physically uniform across the face, so normalise speckle contrast locally
    # (photo noise and light fall-off otherwise make it denser on one side of the tile)
    w = (matrix_r > 0.5).astype(float)
    var = ndimage.gaussian_filter(hp ** 2 * w, 40) / np.maximum(ndimage.gaussian_filter(w, 40), 1e-3)
    hp = hp / (3 * np.sqrt(np.maximum(var, 1e-12)))
    micro = np.clip(hp, -1.5, 1.5) * PORE_MM
    micro = micro * (matrix_r + CHIP_SMOOTH * (1 - matrix_r))
    edge = np.abs(ndimage.sobel(ndimage.gaussian_filter(chip_r, 1.0), 0)) + np.abs(ndimage.sobel(ndimage.gaussian_filter(chip_r, 1.0), 1))
    edge = np.clip(edge / np.percentile(edge[edge > 0.01], 90), 0, 1)
    face_h = micro - CHIP_SEAM_MM * edge

    # ---------- 4. atlas ----------
    color_lin = np.zeros((H, W, 3))
    height = np.zeros((H, W))
    jcol = srgb_to_lin(np.array([220, 211, 197]) / 255.0)   # sanded grout matched near matrix tone
    color_lin[:] = jcol
    cells = []
    o = int(round(half_j))
    for r in range(ROWS):
        for c in range(COLS):
            t = LAYOUT[r][c]
            tone = 1 + rng.uniform(-0.015, 0.015)
            col = apply_t(lin_r, t) * tone
            hh = apply_t(face_h, t)
            ys, xs = r * MODULE_PX + o, c * MODULE_PX + o
            color_lin[ys:ys + face_px, xs:xs + face_px] = col
            height[ys:ys + face_px, xs:xs + face_px] = hh
            cells.append({"row": r, "col": c, "transform": t, "tone": round(tone, 4)})
    report["cells"] = cells
    assert len({c["transform"] for c in cells}) == len(cells), "duplicate transform in atlas"
    assert layout_ok(LAYOUT), "a joint or corner meets its own mirror image"

    # joint + eased edge, distance in mm from each module edge (wraps by construction)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    ex = np.minimum(xx % MODULE_PX + 0.5, MODULE_PX - (xx % MODULE_PX) - 0.5) * MM_PER_PX
    ey = np.minimum(yy % MODULE_PX + 0.5, MODULE_PX - (yy % MODULE_PX) - 0.5) * MM_PER_PX
    e = np.minimum(ex, ey)
    half_j_mm = JOINT_IN / 2 * 25.4
    s = np.clip((e - half_j_mm) / EASE_W_MM, 0, 1)
    ease = FACE_MM - EASE_MM * (1 - np.sin(s * np.pi / 2)) ** 2
    grout = e < half_j_mm
    hmm = np.where(grout, 0.0, ease + height)
    # sanded grout texture
    gn = ndimage.gaussian_filter(rng.standard_normal((H, W)), 0.8) * 0.04
    hmm = np.where(grout, 0.05 + gn, hmm)
    face_min = float(hmm[~grout & (s >= 1)].min())
    report["height_mm"] = {"grout_floor": 0.0, "face_nominal": FACE_MM, "face_min_on_flat": face_min,
                           "face_max": float(hmm.max()), "clearance_above_grout_mm": face_min - float(hmm[grout].max()),
                           "porosity_amp": PORE_MM, "chip_seam": CHIP_SEAM_MM, "ease": EASE_MM}

    # ---------- 5. normal from height (OpenGL, +Y up), wrap-aware ----------
    dx = (np.roll(hmm, -1, 1) - np.roll(hmm, 1, 1)) / (2 * MM_PER_PX)
    dy_row = (np.roll(hmm, -1, 0) - np.roll(hmm, 1, 0)) / (2 * MM_PER_PX)
    nx, ny, nz = -dx, dy_row, np.ones_like(hmm)
    inv = 1 / np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    nrm = np.stack([nx * inv, ny * inv, nz * inv], -1) * 0.5 + 0.5

    # ---------- 6. export ----------
    lo, hi = float(hmm.min()), float(hmm.max())
    bump = (hmm - lo) / (hi - lo)
    report["bump_range_mm"] = [lo, hi]
    files = {"color": out_path("textures", NAME + "_Color.png"),
             "bump": out_path("textures", NAME + "_Bump16.png"),
             "normal": out_path("textures", NAME + "_Normal16_OpenGL.png")}
    col8 = np.clip(np.round(lin_to_srgb(color_lin) * 255), 0, 255).astype(np.uint8)
    Image.fromarray(col8, "RGB").save(files["color"], optimize=True)
    write_png16(files["bump"], bump, rgb=False)
    write_png16(files["normal"], nrm, rgb=True)

    # ---------- 7. checks ----------
    hdr = {k: png_header(v) for k, v in files.items()}
    report["png_headers"] = hdr
    chk = {}
    chk["color_8bit_rgb"] = hdr["color"]["bit_depth"] == 8 and hdr["color"]["color_type"] == 2
    chk["bump_16bit_grey"] = hdr["bump"]["bit_depth"] == 16 and hdr["bump"]["color_type"] == 0
    chk["normal_16bit_rgb"] = hdr["normal"]["bit_depth"] == 16 and hdr["normal"]["color_type"] == 2
    chk["aspect_matches_sample_size"] = all(h["width"] * ROWS == h["height"] * COLS for h in hdr.values())
    chk["all_transforms_distinct"] = len({c["transform"] for c in cells}) == len(cells)
    chk["no_self_mirrored_joint_or_corner"] = layout_ok(LAYOUT)
    chk["clearance_positive"] = report["height_mm"]["clearance_above_grout_mm"] > 0
    # wrap seam: edge-to-edge step vs typical neighbour step
    def wrapstats(a):
        a = a if a.ndim == 3 else a[..., None]
        typ = float(np.abs(np.diff(a, axis=1)).mean())
        wx = float(np.abs(a[:, 0] - a[:, -1]).mean())
        wy = float(np.abs(a[0] - a[-1]).mean())
        return {"typical": typ, "wrap_x": wx, "wrap_y": wy}
    report["wrap"] = {"color": wrapstats(color_lin), "height_mm": wrapstats(hmm), "normal": wrapstats(nrm)}
    chk["wrap_seamless"] = all(v["wrap_x"] <= 2 * v["typical"] + 1e-9 and v["wrap_y"] <= 2 * v["typical"] + 1e-9
                               for v in report["wrap"].values())
    report["checks"] = chk
    report["pass"] = all(chk.values())
    report["sample_size"] = {"width_in": COLS * MODULE_IN, "height_in": ROWS * MODULE_IN,
                             "revit": "8'-0\" x 4'-0\""}
    with open(out_path("source", "build_report.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2)

    # ---------- 8. previews (<= 1600 px) ----------
    def save_small(arr8, name, maxw=1600):
        im = Image.fromarray(arr8)
        im.thumbnail((maxw, maxw), Image.LANCZOS)
        im.save(out_path("source", name), quality=90)
    save_small((np.clip(face, 0, 1) * 255).astype(np.uint8), "_REVIEW_source_crop.jpg", 800)
    save_small((chip * 255).astype(np.uint8), "_REVIEW_chip_mask.jpg", 800)
    tile2 = np.tile(col8, (2, 2, 1))
    save_small(tile2, "_PREVIEW_tiling_color_2x2.jpg")
    # grazing light shading from normal, light from left at 10 deg elevation
    L = np.array([-np.cos(np.radians(10)), 0.0, np.sin(np.radians(10))])
    n = nrm * 2 - 1
    sh = np.clip((n * L).sum(-1), 0, None)
    sh = sh / np.percentile(sh, 99.5)
    graz8 = (np.clip(sh, 0, 1) * 255).astype(np.uint8)
    save_small(np.tile(graz8, (2, 2)), "_PREVIEW_grazing_light_2x2.jpg")
    # close-up 6 x 6 in around a four-way corner, colour lit by grazing light
    cy, cx = MODULE_PX, MODULE_PX
    hw = 3 * PX_PER_IN
    lit = lin_to_srgb(color_lin[cy - hw:cy + hw, cx - hw:cx + hw] * (0.35 + 0.9 * np.clip(sh[cy - hw:cy + hw, cx - hw:cx + hw], 0, 1.3))[..., None])
    Image.fromarray((lit * 255).astype(np.uint8)).resize((768, 768), Image.NEAREST).save(
        out_path("source", "_PREVIEW_closeup_corner_grazing.jpg"), quality=92)
    save_small((np.clip(bump, 0, 1) * 255).astype(np.uint8), "_PREVIEW_bump.jpg")
    save_small((np.clip(nrm, 0, 1) * 255).astype(np.uint8), "_PREVIEW_normal.jpg")
    # wrap seam crop: four corners of the image brought together
    q = 128
    cc = np.concatenate([np.concatenate([col8[-q:, -q:], col8[-q:, :q]], 1),
                         np.concatenate([col8[:q, -q:], col8[:q, :q]], 1)], 0)
    Image.fromarray(cc).resize((512, 512), Image.NEAREST).save(out_path("source", "_PREVIEW_wrap_corner.jpg"), quality=92)

    print(json.dumps({"pass": report["pass"], "checks": chk, "height_mm": report["height_mm"],
                      "chip_fraction": report["chip_fraction"], "light_field_range": report["light_field_range"],
                      "inset_stretch_pct": report["inset_stretch_pct"], "wrap": report["wrap"]}, indent=1))
    if not report["pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
