"""Build Color / Bump16 / Roughness for ELM Fog Cross-Cut Chevron, 24 x 48 module.

Atlas: 3 columns x 4 rows of 48 x 24 in landscape tiles, stacked (grid) layout,
144 x 96 in, 6144 x 4096 px (42.667 px/in). Even row count so the chevron band
direction alternates cleanly across every horizontal joint, including the wrap.

Colour: real product pixels only. Seven genuinely different 48 x 24 faces
  - four non-overlapping cuts of ELM's 48 x 110 slab swatch, with its baked
    groove shading removed (grooves.degroove_slab),
  - ELM's Fog Cross-Cut 24 x 48 swatch face,
  - two full faces from MILE stone's flat 24 x 48 layout panel (Florim),
tone-matched to the chevron swatch, planar tilt removed, mild per-tile shade
jitter (V2). Five faces appear twice, always two rows apart, in another column
and rotated 180 degrees.

Relief: each tile is a 24 in cut of the slab's measured chevron structure
(A = slab top half, B = bottom half, 3 bands each, spines at the tile edges).
Every groove is the measured band profile extruded along a straight line.

Float64 throughout; quantised only on export.
"""
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

import chevron_common as cc
import grooves

OUT_DIR = os.path.join(cc.PROD, "textures")
NAME = "ELM_Fog_CrossCut_Chevron_24x48"
SEED = 20260923
PANEL_SRC = os.path.join(cc.REF, "MILE_stone_EcoStone_Cross-Cut_Fog_24x48_Panel.jpg")
INCH_MM = 25.4


def out_path(name):
    p = os.path.abspath(os.path.join(OUT_DIR, name))
    if not p.startswith(os.path.abspath(cc.PROD) + os.sep):
        raise RuntimeError("refusing to write outside the product folder: " + p)
    return p


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# --------------------------------------------------------------------------- faces
def planar_detrend(img):
    """Remove only a best-fit planar luminance tilt (directional shading)."""
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    L = cc.lum(img)
    A = np.c_[np.ones(h * w), (xx.ravel() - w / 2) / w, (yy.ravel() - h / 2) / h]
    coef, *_ = np.linalg.lstsq(A, L.ravel(), rcond=None)
    tilt = (A[:, 1:] @ coef[1:]).reshape(h, w)
    return img * (1.0 - tilt / coef[0])[..., None], coef


class Face:
    def __init__(self, key, img, rect, note):
        self.key, self.img, self.rect, self.note = key, img, rect, note   # rect px x0,y0,x1,y1

    def sample(self, xt, yt, rot180, tone):
        x0, y0, x1, y1 = self.rect
        u = xt / cc.MODULE_IN[0]
        v = yt / cc.MODULE_IN[1]
        if rot180:
            u, v = 1.0 - u, 1.0 - v
        px = x0 + u * (x1 - x0) - 0.5
        py = y0 + v * (y1 - y0) - 0.5
        out = np.empty(xt.shape + (3,))
        for c in range(3):
            out[..., c] = ndi.map_coordinates(self.img[..., c], [py, px], order=3, mode="nearest")
        return out * tone


def load_faces(slab_dg):
    sx = slab_dg.shape[1] / cc.SLAB_IN[0]
    faces, info = {}, {}
    target = None
    face24 = cc.load_rgb(cc.FACE24_SRC)
    panel = cc.load_rgb(PANEL_SRC)
    mid = SPINES[3]
    raw = {
        "A0": (slab_dg, (0.0, 0.0, 48 * sx, mid), "slab top half, x 0-48 in"),
        "A48": (slab_dg, (48 * sx, 0.0, 96 * sx, mid), "slab top half, x 48-96 in"),
        "B0": (slab_dg, (0.0, mid, 48 * sx, slab_dg.shape[0]), "slab bottom half, x 0-48 in"),
        "B48": (slab_dg, (48 * sx, mid, 96 * sx, slab_dg.shape[0]), "slab bottom half, x 48-96 in"),
        "F24": (face24, (0.0, 0.0, face24.shape[1], face24.shape[0]), "ELM Fog Cross-Cut 24x48 swatch"),
        "TL": (panel, (0.0, 0.0, 2395.0, 1195.0), "MILE stone panel, top-left full tile"),
        "BR": (panel, (1203.0, 1203.0, 3600.0, 2400.0), "MILE stone panel, bottom-right full tile"),
    }
    # target colour: the de-grooved chevron slab itself (the product asked for)
    target = slab_dg.reshape(-1, 3).mean(0)
    for key, (img, rect, note) in raw.items():
        x0, y0, x1, y1 = [int(round(v)) for v in rect]
        crop = img[y0:y1, x0:x1].copy()
        crop, coef = planar_detrend(crop)
        m = crop.reshape(-1, 3).mean(0)
        crop *= (target / m)[None, None, :]
        faces[key] = Face(key, crop, (0.0, 0.0, crop.shape[1], crop.shape[0]), note)
        info[key] = {"note": note, "source_rect_px": [x0, y0, x1, y1],
                     "px_per_in": (x1 - x0) / cc.MODULE_IN[0],
                     "planar_tilt_rel": [float(coef[1] / coef[0]), float(coef[2] / coef[0])],
                     "mean_rgb_before_match": m.tolist()}
    return faces, info, target.tolist()


FINE_TARGET = MID_TARGET = None     # set in main(): median over the faces at output sampling


def harmonise_detail(img):
    """Equalise fine-grain energy between faces from differently compressed sources.

    First review: slab faces from ELM's JPEG (0.65 bit/px, 8x8 blocking) carried
    fine-band std 2.5-3.0 against 5.1-6.1 for the panel and 24x48 faces, so those
    tiles read as a different material up close. Fixed at the source (Florim's
    better-encoded copy of the same swatch); this step only evens out what is left,
    towards the median face. Gains are clamped; coarse structure (the stone's
    clouds, >4 px) is never touched.
    """
    L = cc.lum(img)
    b1, b4 = ndi.gaussian_filter(L, 1.0), ndi.gaussian_filter(L, 4.0)
    gf = float(np.clip(FINE_TARGET / (L - b1).std(), 0.67, 1.5))
    gm = float(np.clip(MID_TARGET / (b1 - b4).std(), 0.8, 1.25))
    out = np.empty_like(img)
    for c in range(3):
        ch = img[..., c]
        c1, c4 = ndi.gaussian_filter(ch, 1.0), ndi.gaussian_filter(ch, 4.0)
        out[..., c] = c4 + gm * (c1 - c4) + gf * (ch - c1)
    return out, gf, gm


# ------------------------------------------------------------------------ layout
# row type: A = slab top half (bands 0,1,2), B = bottom half (bands 3,4,5)
ROW_TYPE = ["A", "B", "A", "B"]
LAYOUT = [  # (face, rot180, groove slab offset X0 in; None -> faithful cut / seeded)
    [("A0", False, 0.0), ("F24", False, None), ("TL", False, None)],
    [("B0", False, 0.0), ("B48", False, 48.0), ("BR", False, None)],
    [("TL", True, None), ("A48", False, 48.0), ("F24", True, None)],
    [("BR", True, None), ("B0", True, None), ("B48", True, None)],
]


def check_layout():
    """Same face never in 8-neighbourhood on the torus; repeats 2 rows apart."""
    R, C = len(LAYOUT), len(LAYOUT[0])
    for r in range(R):
        for c in range(C):
            f = LAYOUT[r][c][0]
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    if LAYOUT[(r + dr) % R][(c + dc) % C][0] == f:
                        raise RuntimeError("face %s adjacent to itself at %d,%d" % (f, r, c))
    for r in range(R):
        for c in range(C):
            f = LAYOUT[r][c][0]
            if f[0] in "AB" and f[0] != ROW_TYPE[r]:
                raise RuntimeError("slab face %s in a %s row" % (f, ROW_TYPE[r]))


# -------------------------------------------------------------------------- relief
def groove_s(profiles, spines, sx, row_type, X0, xt, yt):
    """Normalised groove surface s: 1 = tile plane (crest), 0 = p1 groove floor."""
    h0, h1 = (spines[0], spines[3]) if row_type == "A" else (spines[3], spines[6])
    xs = (X0 + xt) * sx
    ys = h0 + yt / cc.MODULE_IN[1] * (h1 - h0)
    s = np.zeros(xt.shape)
    ks = range(0, 3) if row_type == "A" else range(3, 6)
    for k in ks:
        m = (ys >= spines[k]) & (ys < spines[k + 1])
        if k == ks[-1]:
            m |= ys >= spines[k + 1]
        if not m.any():
            continue
        bp = profiles[k]
        P = bp(xs[m], ys[m])
        lo, hi = NORM[k]
        z = (P - lo) / (hi - lo)
        # soft limits: wiggles above the plateau compressed to <= +0.10,
        # outliers below the p1 floor to >= -0.15
        z = np.where(z > 1, 1 + 0.10 * np.tanh((z - 1) / 0.10), z)
        z = np.where(z < 0, -0.15 * np.tanh(-z / 0.15), z)
        s[m] = z
    return s


def periodic_noise(h, w, lam_lo_px, lam_hi_px, seed):
    rng = np.random.default_rng(seed)
    F = np.fft.rfft2(rng.standard_normal((h, w)))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    r = np.hypot(fx, fy)
    band = (r >= 1.0 / lam_hi_px) & (r <= 1.0 / lam_lo_px)
    n = np.fft.irfft2(F * band, s=(h, w))
    return n / n.std()


# ---------------------------------------------------------------------------- main
def main():
    global SPINES, NORM
    check_layout()
    slab = cc.load_slab()
    # the pixel source must be the same image as the analysed ELM swatch
    ref = cc.lum(cc.load_rgb(cc.SLAB_SRC))
    reg_r = float(np.corrcoef(ndi.gaussian_filter(cc.lum(slab), 8).ravel(), ndi.gaussian_filter(ref, 8).ravel())[0, 1])
    if reg_r < 0.98:
        raise RuntimeError("slab pixel source is not registered with the analysed swatch: r=%.3f" % reg_r)
    slab_dg, dg_rep, profiles, SPINES = grooves.degroove_slab(slab)
    dg_rep["registration_lowpass_r_vs_elm_swatch"] = reg_r
    import degroove
    dg_rep["groove_band_energy_raw"] = degroove.oriented_energy(cc.lum(slab))
    dg_rep["groove_band_energy_degrooved"] = degroove.oriented_energy(cc.lum(slab_dg))
    dg_rep["groove_band_energy_groove_free_render"] = degroove.oriented_energy(cc.lum(cc.load_rgb(cc.GROOVE_FREE_CHECK)))
    NORM = [(float(np.percentile(p.prof, 1)), float(np.percentile(p.prof, 90))) for p in profiles]
    sx = slab.shape[1] / cc.SLAB_IN[0]
    faces, face_info, target = load_faces(slab_dg)

    PPI = cc.PPI
    cw, ch = int(round(cc.MODULE_IN[0] * PPI)), int(round(cc.MODULE_IN[1] * PPI))
    R, C = len(LAYOUT), len(LAYOUT[0])
    W, H = C * cw, R * ch
    px_mm = INCH_MM / PPI
    rng = np.random.default_rng(SEED)

    color = np.zeros((H, W, 3))
    height = np.zeros((H, W))
    rough = np.zeros((H, W))
    micro = periodic_noise(H, W, 0.8 / px_mm, 4.0 / px_mm, SEED + 1)       # 0.8-4 mm
    rnoise = periodic_noise(H, W, 2.0 / px_mm, 20.0 / px_mm, SEED + 2)      # 2-20 mm

    j, i = np.mgrid[0:ch, 0:cw].astype(np.float64)
    xt = (i + 0.5) / PPI
    yt = (j + 0.5) / PPI
    global FINE_TARGET, MID_TARGET
    fs, ms = [], []
    for f in faces.values():
        L0 = cc.lum(f.sample(xt, yt, False, 1.0))
        b1, b4 = ndi.gaussian_filter(L0, 1.0), ndi.gaussian_filter(L0, 4.0)
        fs.append(float((L0 - b1).std()))
        ms.append(float((b1 - b4).std()))
    FINE_TARGET, MID_TARGET = float(np.median(fs)), float(np.median(ms))
    detail = {"fine_std_per_face": dict(zip(faces, fs)), "mid_std_per_face": dict(zip(faces, ms)),
              "fine_target": FINE_TARGET, "mid_target": MID_TARGET}
    e_mm = np.minimum.reduce([xt, cc.MODULE_IN[0] - xt, yt, cc.MODULE_IN[1] - yt]) * INCH_MM
    hj = cc.JOINT_IN * INCH_MM / 2.0
    w_tile = np.clip((e_mm - hj) / px_mm + 0.5, 0.0, 1.0)            # AA coverage of the tile
    t = np.clip((e_mm - hj) / cc.CHAMFER_W_MM, 0.0, 1.0)
    # eased arris: a cap that rounds the ridge tops near the edge only; groove floors
    # keep their depth. At t = 1 the cap sits above any face height (no effect).
    top = cc.TILE_PLANE_MM + 0.10 * cc.GROOVE_DEPTH_MM + cc.MICRO_MM
    ease_cap = top - (top - (cc.TILE_PLANE_MM - cc.CHAMFER_MM)) * (1.0 - t) ** 2

    grout_lin = cc.srgb_to_lin(np.array(cc.GROUT_RGB))
    cells = []
    # V2 shade variation: evenly spread, permuted offsets (no outlier tile that would
    # become a repeating landmark at wall scale). First build drew N(0, 1 %) and gave a
    # 3.8 % luminance spread; rejected on the 3x3 review.
    n = R * C
    lum_set = rng.permutation(np.linspace(-0.006, 0.006, n))
    warm_set = rng.permutation(np.linspace(-0.002, 0.002, n))
    groove_tint = float(np.mean([(hi - lo) / 240.0 for lo, hi in NORM]))  # swatch groove contrast
    for r in range(R):
        for c in range(C):
            key, rot, X0 = LAYOUT[r][c]
            if X0 is None:
                X0 = float(np.round(rng.uniform(2.0, cc.SLAB_IN[0] - cc.MODULE_IN[0] - 2.0), 3))
            lum_j = float(lum_set[r * C + c])
            warm_j = float(warm_set[r * C + c])
            tone = np.array([1 + lum_j + warm_j, 1 + lum_j, 1 + lum_j - warm_j])
            s = groove_s(profiles, SPINES, sx, ROW_TYPE[r], X0, xt, yt)
            face = faces[key].sample(xt, yt, rot, tone)
            face, g_fine, g_mid = harmonise_detail(face)
            # colour: registered groove darkening at the swatch's own measured contrast,
            # zero-mean over the tile so the overall value stays the swatch's value
            g = np.clip(1.0 - s, 0.0, 1.15)
            face = face * (1.0 - groove_tint * (g - g.mean()))[..., None]
            h_face = cc.TILE_PLANE_MM - cc.GROOVE_DEPTH_MM * (1.0 - s)
            sl = (slice(r * ch, (r + 1) * ch), slice(c * cw, (c + 1) * cw))
            h_face = h_face + cc.MICRO_MM * np.clip(micro[sl] / 2.0, -1.0, 1.0)
            h_face = np.minimum(h_face, ease_cap)
            height[sl] = w_tile * h_face + (1 - w_tile) * cc.GROUT_FLOOR_MM
            lin = cc.srgb_to_lin(face)
            color[sl] = cc.lin_to_srgb(w_tile[..., None] * lin + (1 - w_tile[..., None]) * grout_lin)
            r_face = cc.ROUGH_FACE + cc.ROUGH_VALLEY_ADD * np.clip(1.0 - s, 0.0, 1.15) + 0.012 * rnoise[sl]
            rough[sl] = w_tile * r_face + (1 - w_tile) * cc.ROUGH_GROUT
            cells.append({"row": r, "col": c, "row_type": ROW_TYPE[r], "face": key, "rot180": rot,
                          "groove_slab_offset_in": X0, "lum_jitter": lum_j, "warm_jitter": warm_j,
                          "detail_gain_fine": g_fine, "detail_gain_mid": g_mid})

    # ------------------------------------------------------------------ export
    os.makedirs(OUT_DIR, exist_ok=True)
    p_col = out_path(NAME + "_Color.png")
    p_bmp = out_path(NAME + "_Bump16.png")
    p_rgh = out_path(NAME + "_Roughness.png")
    Image.fromarray(np.clip(np.round(color), 0, 255).astype(np.uint8), "RGB").save(p_col, optimize=True)
    q = np.clip(np.round(height / cc.HEIGHT_RANGE_MM * 65535.0), 0, 65535).astype(np.uint16)
    Image.fromarray(q).save(p_bmp)
    Image.fromarray(np.clip(np.round(rough * 255.0), 0, 255).astype(np.uint8), "L").save(p_rgh, optimize=True)

    # realised relief, read back from the exported 16-bit map
    hq = np.asarray(Image.open(p_bmp)).astype(np.float64) / 65535.0 * cc.HEIGHT_RANGE_MM
    tile_px = np.zeros((H, W), bool)
    core = np.zeros((H, W), bool)
    full_face = w_tile >= 1.0
    grout_core = w_tile <= 0.0
    for r in range(R):
        for c in range(C):
            sl = (slice(r * ch, (r + 1) * ch), slice(c * cw, (c + 1) * cw))
            tile_px[sl] = full_face
            core[sl] = grout_core
    face_h = hq[tile_px]
    interior = np.zeros((H, W), bool)
    inner = e_mm > hj + cc.CHAMFER_W_MM
    for r in range(R):
        for c in range(C):
            interior[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw] = inner
    relief = {
        "height_range_mm": cc.HEIGHT_RANGE_MM,
        "grout_floor_mm": float(np.median(hq[core])),
        "grout_floor_max_mm": float(hq[core].max()),
        "tile_plane_mm_nominal": cc.TILE_PLANE_MM,
        "tile_plane_mm_realised_p90": float(np.percentile(hq[interior], 90)),
        "grout_step_mm": float(np.percentile(hq[interior], 90) - np.median(hq[core])),
        "groove_depth_mm_nominal_at_p1_floor": cc.GROOVE_DEPTH_MM,
        "groove_relief_mm_realised_p90_minus_p1": float(np.percentile(hq[interior], 90) - np.percentile(hq[interior], 1)),
        "deepest_face_point_mm": float(face_h.min()),
        "deepest_face_point_below_plane_mm": float(cc.TILE_PLANE_MM - face_h.min()),
        "clearance_above_grout_floor_mm": float(face_h.min() - np.median(hq[core])),
        "highest_point_mm": float(hq.max()),
        "micro_relief_mm": cc.MICRO_MM,
        "edge_ease_mm": [cc.CHAMFER_MM, cc.CHAMFER_W_MM],
        "groove_colour_darkening_at_floor": groove_tint,
    }
    if relief["clearance_above_grout_floor_mm"] <= 0:
        raise RuntimeError("groove pattern reaches the grout floor")
    if relief["highest_point_mm"] >= cc.HEIGHT_RANGE_MM:
        raise RuntimeError("relief clipped at the top of the bump range")

    report = {
        "product": "ELM Surfaces ElmStone Fog Cross-Cut Chevron (Florim USA / MILE stone EcoStone Chevron Deco)",
        "module_in": list(cc.MODULE_IN), "joint_in": cc.JOINT_IN, "layout": "stacked grid",
        "atlas_tiles": [C, R], "atlas_in": [C * cc.MODULE_IN[0], R * cc.MODULE_IN[1]],
        "revit_sample_size": "%d'-0\" x %d'-0\"" % (C * cc.MODULE_IN[0] / 12, R * cc.MODULE_IN[1] / 12),
        "pixels": [W, H], "px_per_in": PPI, "seed": SEED,
        "files": {}, "cells": cells, "faces": face_info, "target_mean_rgb": target,
        "degroove": dg_rep, "detail_harmonisation": detail, "profile_norm_p1_p90": NORM,
        "band_line_deg": cc.BAND_LINE_DEG, "band_pitch_px": cc.BAND_PITCH_PX,
        "spines_px": SPINES, "relief": relief,
        "roughness": {"face": cc.ROUGH_FACE, "groove_floor_add": cc.ROUGH_VALLEY_ADD, "grout": cc.ROUGH_GROUT,
                      "realised_face_mean": float(rough[tile_px].mean())},
        "sources": {os.path.relpath(p, cc.PROD): sha256(p) for p in
                    (cc.SLAB_PIXELS_SRC, cc.SLAB_SRC, cc.FACE24_SRC, PANEL_SRC)},
    }
    for p in (p_col, p_bmp, p_rgh):
        report["files"][os.path.basename(p)] = {"png_ihdr": cc.png_header(p), "bytes": os.path.getsize(p),
                                                "sha256": sha256(p)}
    with open(out_path("build_report.json"), "w") as fh:
        json.dump(report, fh, indent=1)
    print(json.dumps({k: report[k] for k in ("atlas_in", "revit_sample_size", "pixels", "relief", "files")}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
