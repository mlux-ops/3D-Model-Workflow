"""Build the MSI Soreno Ivory Matte 24x48 (NSORIVO2448) colour (8-bit sRGB) and bump (16-bit grey) maps.

Facts (SOURCE_SELECTION.md, README.md):
  * actual size is not published by MSI or any dealer found (2026-09-26). Evidence for the metric
    rectified convention: Italian origin (villohome spec table), 0.39 in = 10 mm thickness on dealer
    tables and 9.90 mm on Home Depot, rectified edge (MSI flyer). Used: 600 x 1200 mm = 23.622 x 47.244 in.
  * joint 1/8 in: MSI Soreno flyer, "1/8" Grout Size is recommended".
  * layout 1/3-offset running bond, long side horizontal (flyer: "less than 33% staggered brick lay").
  * drawn tile 47.2083 x 23.625 in (-0.91 mm / +0.08 mm vs actual, both < 0.5 %) so that 3 x 6 tiles
    give a Sample Size of exactly 142.00 x 142.50 in (11'-10" x 11'-10 1/2"): Revit's Texture Editor
    rounds Sample Size to the project's 1/4 in units.
  * only two independent printed faces exist in every published swatch (a05_dupes.py); the 18 atlas
    faces are synthesised by min-cut patch quilting from those two faces (8 in patches, 8 dihedral
    orientations, usage penalty so no source region is over-used), then given modest per-tile tone.

24 px/in: 3408 x 3420 px. Horizontal joints centred on y = k*570 px, vertical joints of row r on
x = r*378.667 + k*1136 px, half a joint on every image edge where a joint meets it; both maps wrap.
Height (mm above the grout floor): face FACE_MM, eased edge radius EDGE_MM, bounded micro-relief.
Usage:  python b01_build.py                 -> textures/Color.png, Bump16.png, report.json
        python b01_build.py <suffix> R,G,B  -> textures/Color_<suffix>.png only (same seed; asserts the
                                                recomputed bump equals the delivered Bump16.png byte for byte)
Every write goes through guard.out_path.
"""
import json
import struct
import sys
import time
import zlib

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates, uniform_filter
from scipy.signal import fftconvolve

from guard import out_path, ref

SEED = 2026092611
PPI = 24
MM = 25.4
TILE_ACTUAL = (47.2441, 23.6220)          # 1200 x 600 mm, see docstring
TILE_W, TILE_H, JOINT = 47.0 + 5.0 / 24.0, 23.625, 0.125   # drawn 47.2083 x 23.625 in
MOD_W, MOD_H = TILE_W + JOINT, TILE_H + JOINT               # 47.3333 x 23.75 in
COLS, ROWS = 3, 6
OFFSET = MOD_W / 3.0                     # 1/3 running bond, each row steps +1/3 module to the right
W_IN, H_IN = COLS * MOD_W, ROWS * MOD_H  # 142.00 x 142.50 in
W_PX, H_PX = int(round(W_IN * PPI)), int(round(H_IN * PPI))

PATCH_IN, OVERLAP_IN = 8.0, 2.5
N_BEST = 12              # random choice among the N best-matching candidates
USAGE_LAMBDA = 0.6       # weight of the source-usage penalty (relative to the median overlap error)
LOWRES_PENALTY = 1.3     # cost factor for the upsampled (11.2 px/in) left half of face B
MARGIN = 4               # synthesis margin (px at master resolution) around each face

TONE_SIGMA = 0.015       # per-tile log-luminance spread (A vs B faces differ by 1.0 %; MSI web "Low")
HUE_SIGMA = 0.003
FACE_MM = 1.50           # tile face above the grout floor (grout struck ~1.5 mm below the face)
EDGE_MM = 1.00           # eased-edge radius (rectified porcelain)
MICRO_SD_MM = 0.03       # micro-relief standard deviation before bounding
MICRO_MAX_MM = 0.10      # hard bound (tanh) on micro-relief
GROUT_SRGB = (200.0, 194.0, 184.0)       # light warm grey, ~12 % darker than the tile field
GROUT_VARIANTS = {"warmgrey": GROUT_SRGB}


def srgb_to_lin(c):
    c = np.asarray(c, dtype=np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return 255.0 * np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def lum(a):
    return a @ np.array([0.2126, 0.7152, 0.0722])


def write_png16(path, arr16):
    h, w = arr16.shape
    raw = b"".join(b"\x00" + arr16[y].astype(">u2").tobytes() for y in range(h))

    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 16, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    open(path, "wb").write(png)


# ----------------------------------------------------------------------------------------------
# sources
# ----------------------------------------------------------------------------------------------
def planar_delight(a):
    """Remove only a planar (first-order) luminance trend; returns corrected array and trend size."""
    L = gaussian_filter(lum(a), 10)
    yy, xx = np.mgrid[0:L.shape[0], 0:L.shape[1]]
    xn, yn = xx / L.shape[1] - 0.5, yy / L.shape[0] - 0.5
    G = np.stack([np.ones_like(xn), xn, yn], -1).reshape(-1, 3)
    c, *_ = np.linalg.lstsq(G, L.ravel(), rcond=None)
    plane = (G @ c).reshape(L.shape) / c[0]
    return a / plane[..., None], float(plane.max() / plane.min() - 1)


def band_sd(L):
    return float((gaussian_filter(L, 0.7) - gaussian_filter(L, 2.0)).std())


def build_sources():
    """Four roughly square source regions at master resolution (~16.7 px/in), de-lit."""
    master = json.load(open(out_path("_work/master.json")))
    mA = np.load(out_path("_work/master_A.npy"))
    mB = np.load(out_path("_work/master_B.npy"))
    maskA = np.load(out_path("_work/master_hires_mask_A.npy"))
    maskB = np.load(out_path("_work/master_hires_mask_B.npy"))
    q = master["quads"]
    srcs = []
    trim = 3
    # A left / A right / B right: the native hi-res quadrants as pasted into the masters (full weight zone)
    for name, face, m in (("A_left", mA, maskA), ("A_right", mA, maskA), ("B_right", mB, maskB)):
        ox, oy = q[name]["origin_in_upsampled_face"]
        cw, ch = q[name]["crop_px"]
        x0, y0 = max(ox, 0) + 10 + trim, max(oy, 0) + 10 + trim
        x1, y1 = min(ox + cw, face.shape[1]) - 10 - trim, min(oy + ch, face.shape[0]) - 10 - trim
        sub = face[y0:y1, x0:x1]
        assert m[y0:y1, x0:x1].min() > 0.99, name
        srcs.append({"name": name, "img": sub, "lowres": False, "box": [int(x0), int(y0), int(x1), int(y1)]})
    # B left: upsampled 24x48 swatch pixels only (mask == 0), high band matched to the hi-res pool
    ox = q["B_right"]["origin_in_upsampled_face"][0]
    x1 = ox - trim
    sub = mB[trim:mB.shape[0] - trim, trim:x1]
    assert maskB[trim:mB.shape[0] - trim, trim:x1].max() < 1e-9
    srcs.append({"name": "B_left", "img": sub, "lowres": True, "box": [trim, trim, int(x1), int(mB.shape[0] - trim)]})
    ref_sd = np.mean([band_sd(lum(s["img"])) for s in srcs[:3]])
    L = lum(srcs[3]["img"])
    gain = float(np.clip(ref_sd / band_sd(L), 1.0, 1.6))
    img = srcs[3]["img"]
    hb = img - gaussian_filter(img, (2.0, 2.0, 0))
    srcs[3]["img"] = img + (gain - 1.0) * hb
    stats = {"master_ppi": master["master_ppi"], "highband_sd_hires": ref_sd,
             "highband_sd_B_left_before": band_sd(L), "B_left_highband_gain": gain}
    for s in srcs:
        s["img"], s["planar_trend"] = planar_delight(s["img"])
        s["lum"] = lum(s["img"])
        s["usage"] = np.zeros(s["lum"].shape)
    stats["sources"] = [{"name": s["name"], "px": [int(s["img"].shape[1]), int(s["img"].shape[0])],
                         "box_in_master": s["box"], "lowres": s["lowres"],
                         "planar_trend_removed_rel": s["planar_trend"],
                         "mean_srgb": [float(v) for v in s["img"].reshape(-1, 3).mean(0)]} for s in srcs]
    return srcs, stats


def dihedral(a, k):
    """k in 0..7: rotation by k%4 * 90 deg, then transpose-flip if k >= 4."""
    r = np.rot90(a, k % 4, axes=(0, 1))
    return r[:, ::-1] if k >= 4 else r


def undihedral_usage(u_var, k, shape):
    """Map a usage increment drawn in variant space back to source space."""
    r = u_var[:, ::-1] if k >= 4 else u_var
    r = np.rot90(r, -(k % 4), axes=(0, 1))
    assert r.shape == shape
    return r


# ----------------------------------------------------------------------------------------------
# quilting
# ----------------------------------------------------------------------------------------------
def min_cut_mask(err, axis):
    """Minimum-error boundary through an overlap error surface. axis=1: vertical cut (left overlap),
    returns mask (1 = take new patch) of err.shape."""
    e = err if axis == 1 else err.T
    h, w = e.shape
    cost = e.copy()
    back = np.zeros((h, w), dtype=np.int64)
    for y in range(1, h):
        prev = cost[y - 1]
        left = np.r_[np.inf, prev[:-1]]
        right = np.r_[prev[1:], np.inf]
        stack = np.stack([left, prev, right])
        arg = stack.argmin(0)
        cost[y] += stack[arg, np.arange(w)]
        back[y] = arg - 1
    path = np.zeros(h, dtype=np.int64)
    path[-1] = int(cost[-1].argmin())
    for y in range(h - 1, 0, -1):
        path[y - 1] = np.clip(path[y] + back[y, path[y]], 0, w - 1)
    m = (np.arange(w)[None, :] >= path[:, None]).astype(np.float64)
    return m if axis == 1 else m.T


def synth_face(srcs, rng, fw, fh, P, OV, stats):
    step = P - OV
    nx = int(np.ceil((fw - OV) / step))
    ny = int(np.ceil((fh - OV) / step))
    CW, CH = nx * step + OV, ny * step + OV
    canvas = np.zeros((CH, CW, 3))
    have = np.zeros((CH, CW), dtype=bool)
    variants = [(si, k) for si in range(len(srcs)) for k in range(8)]
    for j in range(ny):
        for i in range(nx):
            y, x = j * step, i * step
            tgt = canvas[y:y + P, x:x + P]
            M = have[y:y + P, x:x + P].astype(np.float64)
            tl = lum(tgt) * M
            cands = []
            for si, k in variants:
                S = dihedral(srcs[si]["lum"], k)
                if S.shape[0] < P or S.shape[1] < P:
                    continue
                U = dihedral(srcs[si]["usage"], k)
                um = uniform_filter(U, P, mode="constant")[P // 2:S.shape[0] - (P - 1 - P // 2),
                                                           P // 2:S.shape[1] - (P - 1 - P // 2)]
                if M.sum() > 0:
                    s2 = fftconvolve(S * S, M[::-1, ::-1], mode="valid")
                    st = fftconvolve(S, tl[::-1, ::-1], mode="valid")
                    ssd = (s2 - 2 * st + (tl * tl).sum()) / M.sum()
                else:
                    ssd = np.zeros((S.shape[0] - P + 1, S.shape[1] - P + 1))
                ssd = np.maximum(ssd, 0)
                if srcs[si]["lowres"]:
                    ssd = ssd * LOWRES_PENALTY
                cands.append((si, k, ssd, um[:ssd.shape[0], :ssd.shape[1]]))
            med = np.median(np.concatenate([c[2][::7, ::7].ravel() for c in cands]))
            scale = med if med > 0 else 1.0
            flat = []
            for ci, (si, k, ssd, um) in enumerate(cands):
                tot = ssd + USAGE_LAMBDA * scale * um * (1.0 if M.sum() > 0 else 4.0)
                if M.sum() == 0:
                    tot = tot + scale * 0.05 * rng.random(tot.shape)
                idx = np.argpartition(tot.ravel(), N_BEST)[:N_BEST]
                for t in idx:
                    flat.append((tot.ravel()[t], ci, int(t)))
            flat.sort(key=lambda r: r[0])
            pick = flat[int(rng.integers(N_BEST))]
            si, k, ssd, um = cands[pick[1]]
            py, px = divmod(pick[2], ssd.shape[1])
            Sv = dihedral(srcs[si]["img"], k)
            patch = Sv[py:py + P, px:px + P]
            mask = np.ones((P, P))
            if i > 0:
                err = ((patch[:, :OV] - tgt[:, :OV]) ** 2).sum(2)
                mask[:, :OV] = np.minimum(mask[:, :OV], min_cut_mask(err, 1))
            if j > 0:
                err = ((patch[:OV, :] - tgt[:OV, :]) ** 2).sum(2)
                mask[:OV, :] = np.minimum(mask[:OV, :], min_cut_mask(err, 0))
            mask = np.where(M > 0, gaussian_filter(mask, 0.8), 1.0)
            canvas[y:y + P, x:x + P] = mask[..., None] * patch + (1 - mask[..., None]) * tgt
            have[y:y + P, x:x + P] = True
            # usage: +1 over the used window, in source coordinates
            Uv = np.zeros(dihedral(srcs[si]["usage"], k).shape)
            Uv[py:py + P, px:px + P] = 1.0
            srcs[si]["usage"] += undihedral_usage(Uv, k, srcs[si]["usage"].shape)
            stats["patches"] += 1
            stats["per_source"][srcs[si]["name"]] = stats["per_source"].get(srcs[si]["name"], 0) + 1
            stats["per_orient"][k] = stats["per_orient"].get(k, 0) + 1
    return canvas[:fh, :fw]


# ----------------------------------------------------------------------------------------------
# layout
# ----------------------------------------------------------------------------------------------
def layout():
    """Per output pixel: tile id, local u,v (in, from the tile's top-left face corner), signed distance
    to the tile edge d (in; < 0 inside the joint)."""
    x_in = (np.arange(W_PX) + 0.5) / PPI
    y_in = (np.arange(H_PX) + 0.5) / PPI
    row = np.minimum((y_in // MOD_H).astype(int), ROWS - 1)
    v = y_in - row * MOD_H - JOINT / 2                              # 0..TILE_H on the face
    xs = x_in[None, :] - row[:, None] * OFFSET                     # (H, W)
    col = np.floor(xs / MOD_W).astype(int)
    u = xs - col * MOD_W - JOINT / 2
    col = col % COLS
    tile = row[:, None] * COLS + col
    du = np.minimum(u, TILE_W - u)
    dv = np.minimum(v, TILE_H - v)[:, None]
    d = np.minimum(du, dv)
    return tile, u, np.broadcast_to(v[:, None], u.shape), d, row


def main(grout_srgb=GROUT_SRGB, suffix=""):
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    srcs, sstats = build_sources()
    mppi = sstats["master_ppi"]
    P = int(round(PATCH_IN * mppi))
    OV = int(round(OVERLAP_IN * mppi))
    fw = int(np.ceil(TILE_W * mppi)) + 2 * MARGIN
    fh = int(np.ceil(TILE_H * mppi)) + 2 * MARGIN
    qstats = {"patches": 0, "per_source": {}, "per_orient": {}, "patch_px": P, "overlap_px": OV,
              "face_px": [fw, fh]}
    n_tiles = COLS * ROWS
    faces = []
    for t in range(n_tiles):
        faces.append(synth_face(srcs, rng, fw, fh, P, OV, qstats))
        print("face %d/%d  %.0f s" % (t + 1, n_tiles, time.time() - t0), flush=True)
    np.save(out_path("_work/synth_faces.npy"), np.stack(faces))
    usage = {s["name"]: {"max": float(s["usage"].max()), "mean": float(s["usage"].mean())} for s in srcs}

    tone = np.exp(TONE_SIGMA * rng.standard_normal(n_tiles))
    hue = HUE_SIGMA * rng.standard_normal((n_tiles, 3))
    hue -= hue.mean(1, keepdims=True)
    micro_white = rng.standard_normal((H_PX, W_PX))

    tile, u, v, d, row = layout()
    lin = np.zeros((H_PX, W_PX, 3))
    for t in range(n_tiles):
        m = tile == t
        fi = u[m] * mppi + MARGIN - 0.5
        fj = v[m] * mppi + MARGIN - 0.5
        fl = srgb_to_lin(faces[t])
        for c in range(3):
            lin[..., c][m] = map_coordinates(fl[..., c], [fj, fi], order=3, mode="nearest")
        lin[m] *= (tone[t] * np.exp(hue[t]))[None, :]
    lin = np.clip(lin, 0, 1)
    face_lin = lin.copy()

    # grout and edge anti-aliasing
    px_in = 1.0 / PPI
    alpha = np.clip(d / px_in + 0.5, 0, 1)
    gl = srgb_to_lin(np.array(grout_srgb))
    gnoise = gaussian_filter(rng.standard_normal((H_PX, W_PX)), 1.0, mode="wrap") * 0.015
    grout = gl[None, None, :] * (1 + gnoise[..., None])
    colour = alpha[..., None] * lin + (1 - alpha[..., None]) * grout
    del lin, grout
    srgb = np.clip(np.round(lin_to_srgb(colour)), 0, 255).astype(np.uint8)
    del colour

    # height (mm above the grout floor)
    micro = (gaussian_filter(micro_white, 1.2, mode="wrap") / 0.235 * 0.7
             + gaussian_filter(micro_white, 4.0, mode="wrap") / 0.0705 * 0.3)
    micro = micro / micro.std() * MICRO_SD_MM
    micro = MICRO_MAX_MM * np.tanh(micro / MICRO_MAX_MM)
    d_mm = d * MM
    q = np.clip(d_mm / EDGE_MM, 0, 1)
    drop = EDGE_MM * (1 - np.sqrt(1 - (1 - q) ** 2))              # quarter-circle roundover
    face_h = FACE_MM + micro
    height = alpha * np.maximum(face_h - drop, 0.0)
    full_mm = float(height.max())
    h16 = np.clip(np.round(height / full_mm * 65535), 0, 65535).astype(np.uint16)

    cname = "textures/Color%s.png" % ("_" + suffix if suffix else "")
    Image.fromarray(srgb, "RGB").save(out_path(cname), optimize=True)
    if suffix:
        delivered = np.asarray(Image.open(out_path("textures/Bump16.png"))).astype(np.uint16)
        if not np.array_equal(delivered, h16):
            raise RuntimeError("variant bump differs from delivered Bump16.png: geometry or seed changed")
        print("bump identical to delivered Bump16.png")
    else:
        write_png16(out_path("textures/Bump16.png"), h16)
        np.save(out_path("_work/tile_id.npy"), tile.astype(np.uint8))

    face = d_mm >= EDGE_MM
    report = {
        "product": "MSI Soreno Ivory Matte porcelain 24x48, SKU NSORIVO2448 (rectified, 10 mm)",
        "seed": SEED, "ppi": PPI, "pixels": [W_PX, H_PX],
        "tile_actual_in": list(TILE_ACTUAL), "tile_actual_basis": "600 x 1200 mm metric rectified convention (not published)",
        "tile_drawn_in": [TILE_W, TILE_H],
        "drawn_minus_actual_mm": [(TILE_W - TILE_ACTUAL[0]) * MM, (TILE_H - TILE_ACTUAL[1]) * MM],
        "drawn_minus_actual_pct": [100 * (TILE_W / TILE_ACTUAL[0] - 1), 100 * (TILE_H / TILE_ACTUAL[1] - 1)],
        "joint_in": JOINT, "module_in": [MOD_W, MOD_H], "row_offset_in": OFFSET,
        "layout": "1/3-offset running bond, long side horizontal, each row steps +1/3 module to the right",
        "atlas_tiles": [COLS, ROWS], "sample_size_in": [W_IN, H_IN],
        "relief_mm": {"full_scale": full_mm, "grout_floor": 0.0, "face_design": FACE_MM,
                      "edge_radius": EDGE_MM, "micro_sd_design": MICRO_SD_MM, "micro_bound": MICRO_MAX_MM,
                      "micro_measured_sd": float(micro.std()), "micro_measured_range": [float(micro.min()), float(micro.max())],
                      "face_min_outside_ease": float(height[face].min()),
                      "face_max": float(height[face].max()),
                      "clearance_face_above_grout_min": float(height[face].min()),
                      "height_at_tile_edge_design": FACE_MM - EDGE_MM,
                      "mm_per_count": full_mm / 65535},
        "colour": {"grout_srgb": list(grout_srgb), "tone_sigma_log": TONE_SIGMA, "hue_sigma": HUE_SIGMA,
                   "tile_tone_factors": [float(v) for v in tone],
                   "face_mean_srgb": [float(c) for c in srgb[face].reshape(-1, 3).mean(0)],
                   "face_mean_linear": [float(c) for c in face_lin[face].reshape(-1, 3).mean(0)]},
        "sources": sstats, "quilt": {**qstats, "per_orient": {str(k): v for k, v in qstats["per_orient"].items()},
                                     "usage": usage, "n_best": N_BEST, "usage_lambda": USAGE_LAMBDA,
                                     "lowres_penalty": LOWRES_PENALTY, "patch_in": PATCH_IN, "overlap_in": OVERLAP_IN},
        "build_seconds": time.time() - t0,
    }
    json.dump(report, open(out_path("textures/report%s.json" % ("_" + suffix if suffix else "")), "w"), indent=1)
    print(json.dumps({k: report[k] for k in ("pixels", "sample_size_in", "relief_mm", "colour")}, indent=1))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
        rgb = tuple(float(x) for x in sys.argv[2].split(",")) if len(sys.argv) > 2 else GROUT_VARIANTS[name]
        main(rgb, name)
    else:
        main()
