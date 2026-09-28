"""Build step 4: render the 4489 x 4536 atlas - Color.png, Bump16.png, face_ids.png.

Every face pixel is mapped straight to the calibrated render (single cubic interpolation):
  matte    low band (tone + cloudiness) of source A + high band (speckle) of source B,
           each under its own hexagon symmetry, sampled at 0.968 scale inside the source face so the
           render's joint halo is never sampled; bump = face plane + tiny micro-relief.
  raw      quilted patches (b03); colour = source colour normalised by its face mean x
           the atlas face's tone; bump = the render's Raw relief band x RAW_SIGMA_MM.
  chiseled procedural grooves from the measured geometry (period 5.014 mm, direction set
           90/150/30 deg, asymmetric profile from the measured 2nd harmonic); colour =
           source chiseled face with its own periodic profile divided out (keeps tone,
           cloudiness and ragged detail), then any remaining groove stripes removed by local
           demodulation (albedo only: the stripes in the render are shading); bump = groove
           profile whose ridge strength and sideways position follow the source face's own
           measured irregularity (local demodulated fundamental), plus source grain scaled so
           the roughness-to-groove ratio under raking light approaches the lifestyle image's.
Production changes vs the max trial arm (2026-09-26 blind review fixes 1-2) are marked PROD.
Heights are built in millimetres as separate terms (joint depth, pattern relief, eased
edge) and quantised once at export; joints are 1/8 in (half on each tile side).
"""

import json
import sys
import time

import numpy as np
from PIL import Image
from scipy import ndimage

from common import (COLS, ROWS, W, H, PX_PER_IN_X, PX_PER_IN_Y, COL_PITCH_IN, ROW_PITCH_IN,
                    SAMPLE_W_IN, SAMPLE_H_IN, HALF_JOINT_IN, S3, lin_to_srgb, srgb_to_lin,
                    out_path, hex_edge_distance_local)
from guard import save_image

# ---- relief terms (mm) -----------------------------------------------------------------
JOINT_DEPTH_MM = 1.60        # face plane above the joint floor
RAW_SIGMA_MM = 0.30          # Raw relief per unit std of the render relief band
RAW_CLIP_MM = 1.00           # soft clip (tanh) of Raw relief about the face plane
CHIS_DEPTH_MM = 0.70         # Chiseled crest-to-groove-bottom depth (calibrated: ~43 % of a
                             # vertical groove period shadowed at 20 deg, ~59 % at 15 deg;
                             # lifestyle shows ~40 %)
GRAIN_SIGMA_MM = 0.20        # PROD: Chiseled organic grain (from source residual); was 0.07.
                             # Calibrated with c02_ridge_roughness_ratio.py against the lifestyle
GRAIN_CLIP_NEG = 3.0         # PROD: grain clip in sigma units, deep side (chips, material removed)
GRAIN_CLIP_POS = 1.0         # PROD: grain clip in sigma units, raised side (chiselling only removes)
CREST_MOD_K = 1.0            # PROD: ridge-strength modulation = source's own local fundamental
                             # amplitude (render amp_cv 0.18-0.25, lifestyle 0.18; c01)
CREST_MOD_MAX = 1.25
PHASE_K = 1.0                # PROD: ridge sideways wander = source's own local phase
                             # (render 0.03-0.04 period sd, lifestyle 0.04-0.07; c01)
MOD_SIGMA_PERIODS = 0.8      # PROD: low-pass of the source demodulation (as measured in c01)
DESTRIPE_SIGMA_PERIODS = 1.0 # PROD: local demodulation window for removing colour stripes
CH_SHRINK = 0.94             # PROD: chiseled source sampling scale: (apothem 156.6 render px - 5 px
                             # clean margin - 4 px validity feather) / 156.6
MATTE_MICRO_SIGMA_MM = 0.008
MATTE_MICRO_CLIP_MM = 0.025
EASE_MM = 0.25               # eased tile edge: drop at the arris
EASE_W_IN = 0.04             # width of the eased edge (~1 mm)
H_RANGE_MM = 2.60            # 16-bit full scale: 0 = joint floor, 65535 = 2.60 mm
# ---- chiseled profile (measured): fundamental + 2nd harmonic at +100 deg relative phase
CH_A2 = 0.30                 # measured 0.20 at render sharpness; x1.5 de-blur
CH_PSI2_DEG = 100.0
COL_GROOVE_GAIN = 0.0        # PROD: was 1.10 (re-added the render's groove shading to colour);
                             # the reviewer found the stripes baked into albedo, so none is added
JOINT_SRGB = (206.0, 198.0, 184.0)   # render joint core, darkest 10 %
SEAM_LOW_SIGMA = 3.0         # raw seam blending: band split, render px
SEAM_WIDE_SIGMA = 5.0        # raw seam blending: low-band feather, render px
MATTE_SHRINK = None          # set from sources: (apothem - clean margin) / apothem


def sample(arr, px, py, order=3):
    """arr (H,W[,C]) sampled at image coords px, py (pixel centres at +0.5)."""
    if arr.ndim == 2:
        return ndimage.map_coordinates(arr, [py - 0.5, px - 0.5], order=order, mode="nearest")
    return np.stack([ndimage.map_coordinates(arr[..., c], [py - 0.5, px - 0.5], order=order,
                                             mode="nearest") for c in range(arr.shape[2])], -1)


def rot(a_deg):
    t = np.deg2rad(a_deg)
    return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])


def groove_profile(u):
    g = -np.cos(2 * np.pi * u) + CH_A2 * np.cos(4 * np.pi * u + np.deg2rad(CH_PSI2_DEG))
    uu = np.linspace(0, 1, 4001)
    gg = -np.cos(2 * np.pi * uu) + CH_A2 * np.cos(4 * np.pi * uu + np.deg2rad(CH_PSI2_DEG))
    return (g - gg.min()) / (gg.max() - gg.min()), gg


def source_modulation(src, corr, lp, owner, clean):
    """PROD. Per render Chiseled face: the local complex amplitude of the groove fundamental in
    relative luminance, normalised so its face mean is 1+0j. |An| is the local ridge strength
    (weak or broken stretches), arg(An) the local sideways shift of the ridges. Pixels outside
    every Chiseled face stay 1+0j (no modulation)."""
    An = np.ones(corr.shape[:2], dtype=np.complex64)
    Yc = 0.2126 * corr[..., 0] + 0.7152 * corr[..., 1] + 0.0722 * corr[..., 2]
    Yl = 0.2126 * lp[..., 0] + 0.7152 * lp[..., 1] + 0.0722 * lp[..., 2]
    sig = MOD_SIGMA_PERIODS * src["period_px"]
    stats = {}
    for f in src["faces"]:
        if f["type"] != "chiseled" or "fold_rel_rgb" not in f:
            continue
        X0, Y0, X1, Y1 = f["bbox"]
        m = clean[Y0:Y1, X0:X1] & (owner[Y0:Y1, X0:X1] == f["id"])
        if m.sum() < 200:
            continue
        yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float64)
        t = np.deg2rad(f["u_can_up"])
        u = ((xx + 0.5 - f["cx"]) * np.cos(t) - (yy + 0.5 - f["cy"]) * np.sin(t)) / src["period_px"]
        r = np.where(m, Yc[Y0:Y1, X0:X1] / Yl[Y0:Y1, X0:X1] - 1.0, 0.0)
        z = r * np.exp(-2j * np.pi * u)
        den = np.maximum(ndimage.gaussian_filter(m.astype(np.float64), sig), 1e-6)
        A = (ndimage.gaussian_filter(z.real, sig) + 1j * ndimage.gaussian_filter(z.imag, sig)) / den
        ref = A[m].mean()
        An_f = A / (np.abs(A[m]).mean() * ref / abs(ref))
        own = owner[Y0:Y1, X0:X1] == f["id"]
        An[Y0:Y1, X0:X1] = np.where(own, An_f, An[Y0:Y1, X0:X1])
        a = np.abs(An_f[m])
        ph = np.angle(An_f[m])
        stats[f["id"]] = {"amp_cv": float(a.std() / a.mean()), "phase_sd_periods": float(ph.std() / (2 * np.pi))}
    return An, stats


def destripe(col, fid, U, k, period_px):
    """PROD. Remove the groove fundamental and 2nd harmonic from one Chiseled face's colour by
    local demodulation at the face's own groove phase U (wrap-aware crop). Tone, cloudiness and
    non-periodic ragged detail stay."""
    yy, xx = np.nonzero(fid == k)
    ay = np.angle(np.exp(2j * np.pi * yy / H).mean()) / (2 * np.pi) * H
    ax = np.angle(np.exp(2j * np.pi * xx / W).mean()) / (2 * np.pi) * W
    uy = ((yy - ay + H / 2) % H) - H / 2 + ay
    ux = ((xx - ax + W / 2) % W) - W / 2 + ax
    r = int(max(np.abs(uy - uy.mean()).max(), np.abs(ux - ux.mean()).max())) + 4
    ys = np.arange(int(uy.mean()) - r, int(uy.mean()) + r + 1) % H
    xs = np.arange(int(ux.mean()) - r, int(ux.mean()) + r + 1) % W
    m = fid[np.ix_(ys, xs)] == k
    Uc = U[np.ix_(ys, xs)].astype(np.float64)
    C = col[np.ix_(ys, xs)].astype(np.float64)
    mf = m.astype(np.float64)
    den_lp = np.maximum(ndimage.gaussian_filter(mf, 2.0 * period_px), 1e-6)
    sig = DESTRIPE_SIGMA_PERIODS * period_px
    den = np.maximum(ndimage.gaussian_filter(mf, sig), 1e-6)
    before, after = [], []
    for ch in range(3):
        c = C[..., ch]
        base = ndimage.gaussian_filter(c * mf, 2.0 * period_px) / den_lp
        rel = np.where(m, c / np.maximum(base, 1e-6) - 1.0, 0.0)
        stripe = np.zeros_like(rel)
        for n in (1, 2):
            e = np.exp(-2j * np.pi * n * Uc)
            z = rel * e * mf
            A = (ndimage.gaussian_filter(z.real, sig) + 1j * ndimage.gaussian_filter(z.imag, sig)) / den
            stripe += 2.0 * np.real(A / e)
            if n == 1 and ch == 1:
                before.append(float(np.abs(A[m]).mean()))
        C[..., ch] = np.where(m, c / (1.0 + stripe), c)
        if ch == 1:
            z = (C[..., ch] / np.maximum(base, 1e-6) - 1.0) * np.exp(-2j * np.pi * Uc) * mf
            A = (ndimage.gaussian_filter(z.real, sig) + 1j * ndimage.gaussian_filter(z.imag, sig)) / den
            after.append(float(np.abs(A[m]).mean()))
    sub = col[np.ix_(ys, xs)]
    sub[m] = C[m].astype(col.dtype)
    col[np.ix_(ys, xs)] = sub
    return before[0], after[0]


def geometry():
    """Per pixel: face index 1..56 (0 = joint), local offsets dx, dy (in, image axes, y
    down) from the owning centre, distance e to the joint centreline (in)."""
    fid = np.zeros((H, W), dtype=np.int16)
    DX = np.zeros((H, W), dtype=np.float32)
    DY = np.zeros((H, W), dtype=np.float32)
    E = np.zeros((H, W), dtype=np.float32)
    apo = ROW_PITCH_IN / 2.0
    for y0 in range(0, H, 256):
        y1 = min(H, y0 + 256)
        ys, xs = np.mgrid[y0:y1, 0:W].astype(np.float64)
        X = (xs + 0.5) / PX_PER_IN_X
        Y = (ys + 0.5) / PX_PER_IN_Y
        best = np.full(X.shape, -np.inf)
        bi = np.zeros(X.shape, dtype=np.int64); bj = np.zeros(X.shape, dtype=np.int64)
        bdx = np.zeros(X.shape); bdy = np.zeros(X.shape)
        ci = np.floor(X / COL_PITCH_IN).astype(np.int64)
        for di in (-1, 0, 1, 2):
            i = ci + di
            cx = (i + 0.5) * COL_PITCH_IN
            yoff = np.where(np.mod(i, 2) == 1, ROW_PITCH_IN / 2.0, 0.0)
            j0 = np.floor((Y - yoff) / ROW_PITCH_IN).astype(np.int64)
            for dj in (-1, 0, 1):
                j = j0 + dj
                cy = (j + 0.5) * ROW_PITCH_IN + yoff
                dx = X - cx; dy = Y - cy
                e = hex_edge_distance_local(dx, dy, apo)
                b = e > best
                best = np.where(b, e, best)
                bi = np.where(b, i, bi); bj = np.where(b, j, bj)
                bdx = np.where(b, dx, bdx); bdy = np.where(b, dy, bdy)
        idx = np.mod(bj, ROWS) * COLS + np.mod(bi, COLS) + 1
        face = best >= HALF_JOINT_IN
        fid[y0:y1] = np.where(face, idx, 0)
        DX[y0:y1] = bdx; DY[y0:y1] = bdy; E[y0:y1] = best
    return fid, DX, DY, E


def main():
    t0 = time.time()
    src = json.load(open(out_path("_work", "sources.json")))
    lay = json.load(open(out_path("_work", "layout.json")))
    qmeta = json.load(open(out_path("_work", "raw_quilt.json")))
    q = np.load(out_path("_work", "raw_quilt.npz"))
    corr = np.load(out_path("_work", "src_corr.npy")).astype(np.float64)
    lp = np.load(out_path("_work", "src_lp.npy")).astype(np.float64)
    hband = np.load(out_path("_work", "src_hband.npy")).astype(np.float64)
    owner = np.load(out_path("_work", "src_owner.npy"))
    clean = np.load(out_path("_work", "src_clean.npy"))
    faces = {f["id"]: f for f in src["faces"]}
    ppi_r = src["ppi_render"]
    per_in = src["period_in"]
    hp = corr - lp
    Ycorr = 0.2126 * corr[..., 0] + 0.7152 * corr[..., 1] + 0.0722 * corr[..., 2]
    Ylp = 0.2126 * lp[..., 0] + 0.7152 * lp[..., 1] + 0.0722 * lp[..., 2]
    # clean distance (render px) inside each face, for feathering source validity
    cdist = ndimage.distance_transform_edt(clean)
    shrink = (5.0 - src["clean_px"] / ppi_r) / 5.0
    fid, DX, DY, E = geometry()
    print("geometry %.0fs" % (time.time() - t0))
    col = np.zeros((H, W, 3), dtype=np.float32)
    hgt = np.zeros((H, W), dtype=np.float32)
    joint_lin = srgb_to_lin(np.array(JOINT_SRGB))
    col[fid == 0] = joint_lin
    order = np.argsort(fid.ravel(), kind="stable")
    counts = np.bincount(fid.ravel(), minlength=COLS * ROWS + 1)
    starts = np.concatenate([[0], np.cumsum(counts)])
    matte_ids = [f["id"] for f in src["faces"] if f["type"] == "matte"]
    # global normalisers
    raw_ids = [f["id"] for f in src["faces"] if f["type"] == "raw"]
    raw_base = np.mean([faces[i]["mean_lin"] for i in raw_ids if faces[i]["frac"] > 0.99], axis=0)
    mm = clean & np.isin(owner, matte_ids)
    matte_micro_std = float((0.2126 * hp[..., 0] + 0.7152 * hp[..., 1] + 0.0722 * hp[..., 2])[mm].std()
                            / Ylp[mm].mean())
    chis_ids = [f["id"] for f in src["faces"] if f["type"] == "chiseled"]
    report_faces = []
    stats = {"matte": [], "raw": [], "chiseled": []}
    _, gg = groove_profile(np.zeros(1))
    gn_mean = float(((gg - gg.min()) / (gg.max() - gg.min())).mean())
    # measured std of the chiseled residual (periodic profile divided out), render res
    res_all = []
    for f in src["faces"]:
        if f["type"] != "chiseled" or "fold_rel_rgb" not in f or f["frac"] < 0.99:
            continue
        X0, Y0, X1, Y1 = f["bbox"]
        m = clean[Y0:Y1, X0:X1] & (owner[Y0:Y1, X0:X1] == f["id"])
        yy, xx = np.nonzero(m)
        ddx = xx + X0 + 0.5 - f["cx"]; ddy = yy + Y0 + 0.5 - f["cy"]
        t = np.deg2rad(f["u_can_up"])
        u = np.mod((ddx * np.cos(t) - ddy * np.sin(t)) / src["period_px"], 1.0)
        fold = np.array(f["fold_rel_rgb"]); nb = fold.shape[1]
        xb = (np.arange(nb) + 0.5) / nb
        Fy = sum(wc * np.interp(u, np.r_[xb - 1, xb, xb + 1], np.tile(fold[ch], 3))
                 for ch, wc in enumerate((0.2126, 0.7152, 0.0722)))
        Yv = Ycorr[Y0:Y1, X0:X1][m] / (1.0 + Fy)
        res_all.append(Yv / Ylp[Y0:Y1, X0:X1][m] - 1.0)
    grain_std = float(np.concatenate(res_all).std())
    print("chiseled residual std (relative luma) %.4f" % grain_std)
    An, mod_stats = source_modulation(src, corr, lp, owner, clean)          # PROD
    An_re = An.real.astype(np.float64); An_im = An.imag.astype(np.float64)
    del An
    print("source ridge modulation per face: %s" % json.dumps({k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in mod_stats.items()}))
    U_full = np.zeros((H, W), dtype=np.float32)                               # PROD: groove phase
    period_atlas_px = per_in * PX_PER_IN_X
    # raw faces: masked low-pass (sigma 3 px) of colour and relief band, for seam blending
    corr_low = np.zeros_like(corr)
    hb_low = np.zeros_like(hband)
    for f in src["faces"]:
        if f["type"] != "raw":
            continue
        X0, Y0, X1, Y1 = f["bbox"]
        own = owner[Y0:Y1, X0:X1] == f["id"]
        m = (clean[Y0:Y1, X0:X1] & own).astype(np.float64)
        den = ndimage.gaussian_filter(m, SEAM_LOW_SIGMA, mode="constant")
        for ch in range(3):
            num = ndimage.gaussian_filter(corr[Y0:Y1, X0:X1, ch] * m, SEAM_LOW_SIGMA, mode="constant")
            corr_low[Y0:Y1, X0:X1, ch] = np.where(own, num / np.maximum(den, 1e-6), corr_low[Y0:Y1, X0:X1, ch])
        num = ndimage.gaussian_filter(hband[Y0:Y1, X0:X1] * m, SEAM_LOW_SIGMA, mode="constant")
        hb_low[Y0:Y1, X0:X1] = np.where(own, num / np.maximum(den, 1e-6), hb_low[Y0:Y1, X0:X1])
    for cell in lay["cells"]:
        k = cell["index"]
        sel = order[starts[k]:starts[k + 1]]
        py_, px_ = np.divmod(sel, W)
        dx = DX.ravel()[sel].astype(np.float64); dy = DY.ravel()[sel].astype(np.float64)
        t_in = E.ravel()[sel].astype(np.float64) - HALF_JOINT_IN
        Xu, Yu = dx, -dy                                   # y-up local inches
        typ = cell["type"]
        if typ == "matte":
            outs = []
            for band in ("low", "high"):
                s = faces[cell[band + "_src"]]
                Xm = -Xu if cell[band + "_mirror"] else Xu
                R = rot(cell[band + "_rot"])
                Xs = (R[0, 0] * Xm + R[0, 1] * Yu) * shrink
                Ys = (R[1, 0] * Xm + R[1, 1] * Yu) * shrink
                pxs = s["cx"] + Xs * ppi_r
                pys = s["cy"] - Ys * ppi_r
                outs.append((pxs, pys))
            (pxA, pyA), (pxB, pyB) = outs
            low = sample(lp, pxA, pyA)
            high = sample(hp, pxB, pyB)
            c = low + high
            yl = 0.2126 * low[:, 0] + 0.7152 * low[:, 1] + 0.0722 * low[:, 2]
            yh = 0.2126 * high[:, 0] + 0.7152 * high[:, 1] + 0.0722 * high[:, 2]
            micro = np.clip((yh / yl) / matte_micro_std * MATTE_MICRO_SIGMA_MM,
                            -MATTE_MICRO_CLIP_MM, MATTE_MICRO_CLIP_MM)
            pat = micro
            desc = ("low band (tone+cloudiness): render matte face %d rot %d%s; high band "
                    "(speckle): render matte face %d rot %d%s; sampled at %.4f scale inside the "
                    "clean face" % (cell["low_src"], cell["low_rot"], " mirrored" if cell["low_mirror"] else "",
                                    cell["high_src"], cell["high_rot"], " mirrored" if cell["high_mirror"] else "",
                                    shrink))
            rotd, mir = cell["low_rot"], cell["low_mirror"]
        elif typ == "raw":
            G_h, G_w = qmeta["faces"][str(k)]["G"]
            pt = qmeta["faces"][str(k)]["patches"]
            vers = qmeta["versions"]
            L1 = q["L1_%d" % k]; L2 = q["L2_%d" % k]; W1 = q["W1_%d" % k]
            Nq = qmeta["N"]
            gx = dx * ppi_r + G_w / 2.0
            gy = dy * ppi_r + G_h / 2.0
            gix = np.clip(np.floor(gx).astype(int), 0, G_w - 1)
            giy = np.clip(np.floor(gy).astype(int), 0, G_h - 1)
            l1 = L1[giy, gix]; l2 = L2[giy, gix]; w1 = W1[giy, gix]
            if (l1 < 0).any():
                raise RuntimeError("raw face %d: %d pixels without a patch" % (k, int((l1 < 0).sum())))
            # two-band seam blending: the low band (sigma 3 render px) is blended with wide
            # weights (the min-cut weights blurred by sigma 5 px), the high band keeps the
            # narrow min-cut weights, so tone steps vanish without ghosting fine relief
            npch = len(pt)
            wide = np.zeros((npch, G_h, G_w))
            for pid in range(npch):
                wp = np.where(L1 == pid, W1, 0.0) + np.where(L2 == pid, 1.0 - W1, 0.0)
                if wp.any():
                    wide[pid] = ndimage.gaussian_filter(wp, SEAM_WIDE_SIGMA, mode="nearest")
            top = np.argsort(-wide, axis=0)[:4]
            topw = np.take_along_axis(wide, top, axis=0)
            topw /= np.maximum(topw.sum(axis=0, keepdims=True), 1e-9)
            del wide
            lw = top[:, giy, gix]; ww_ = topw[:, giy, gix]
            n = len(sel)
            c_hi = np.zeros((n, 3)); c_lo = np.zeros((n, 3)); w_hi = np.zeros(n); w_lo = np.zeros(n)
            h_hi = np.zeros(n); h_lo = np.zeros(n)
            tone = raw_base * (cell["tone"] / 1.0033)
            need_p = np.unique(np.concatenate([l1, l2[l2 >= 0], lw[ww_ > 1e-4]]))
            for pid in need_p:
                wn = np.where(l1 == pid, w1, 0.0) + np.where(l2 == pid, 1.0 - w1, 0.0)
                wl = ((lw == pid) * ww_).sum(axis=0)
                m = (wn > 0) | (wl > 1e-4)
                if not m.any():
                    continue
                p = pt[pid]
                v = vers[p["vi"]]
                M = np.array(v["M"])
                Xt = (gx[m] - p["px0"] + p["ax"]) - Nq / 2.0
                Yt = -((gy[m] - p["py0"] + p["ay"]) - Nq / 2.0)
                Xs = M[0, 0] * Xt + M[0, 1] * Yt
                Ys = M[1, 0] * Xt + M[1, 1] * Yt
                s = faces[p["src"]]
                pxs = s["cx"] + Xs
                pys = s["cy"] - Ys
                norm = tone / np.array(s["mean_lin"])
                cs = sample(corr, pxs, pys) * norm
                cl = sample(corr_low, pxs, pys) * norm
                hs = sample(hband, pxs, pys)
                hl = sample(hb_low, pxs, pys)
                a, b = wn[m], wl[m]
                c_hi[m] += (cs - cl) * a[:, None]; w_hi[m] += a; h_hi[m] += (hs - hl) * a
                c_lo[m] += cl * b[:, None]; w_lo[m] += b; h_lo[m] += hl * b
            c = c_lo / w_lo[:, None] + c_hi / w_hi[:, None]
            hsum = h_lo / w_lo + h_hi / w_hi
            pat = RAW_CLIP_MM * np.tanh(hsum * RAW_SIGMA_MM / RAW_CLIP_MM)
            srcs = sorted({p["src"] for p in pt})
            nt = {}
            for p in pt:
                key = "%s%+d" % (p["tau"], int(p["jit"]))
                nt[key] = nt.get(key, 0) + 1
            desc = ("quilt of %d patches (2.04 in, min-error seams) cut from render raw faces %s; "
                    "patch orientations %s (texture axis kept as in the render)"
                    % (len(pt), srcs, dict(sorted(nt.items()))))
            rotd, mir = 0, False
        else:   # chiseled
            s = faces[cell["src"]]
            rho_t = cell["rho"]
            qx = np.cos(np.deg2rad(-rho_t)) * Xu - np.sin(np.deg2rad(-rho_t)) * Yu
            qy = np.sin(np.deg2rad(-rho_t)) * Xu + np.cos(np.deg2rad(-rho_t)) * Yu
            u_t = qx / per_in
            if cell["mirror_v"]:
                qy = -qy
            delta = (s["crest_phase"] - 0.5) * per_in
            qsx = qx + delta
            rs = s["rho_src_exact"]
            Xs = np.cos(np.deg2rad(rs)) * qsx - np.sin(np.deg2rad(rs)) * qy
            Ys = np.sin(np.deg2rad(rs)) * qsx + np.cos(np.deg2rad(rs)) * qy
            # PROD: sample CH_SHRINK inside the source face so the atlas face's rim also draws on
            # clean source pixels (at 1.0 the outer ~0.2 in fell in the source's unusable margin
            # and showed perfectly regular, grain-free grooves); groove geometry is unaffected
            pxs = s["cx"] + Xs * ppi_r * CH_SHRINK
            pys = s["cy"] - Ys * ppi_r * CH_SHRINK
            S = sample(corr, pxs, pys)
            LPs = sample(lp, pxs, pys)
            # source periodic profile at the source's own phase of each sampled point
            # (u_s = CH_SHRINK x (u_t + crest - 0.5); identical to the trial formula at 1.0)
            u_s = np.mod(CH_SHRINK * (u_t + s["crest_phase"] - 0.5), 1.0)
            fold = np.array(s["fold_rel_rgb"])            # (3, 32) relative, bin centres
            nb = fold.shape[1]
            xb = (np.arange(nb) + 0.5) / nb
            F = np.stack([np.interp(u_s, np.r_[xb - 1, xb, xb + 1], np.tile(fold[ch], 3)) for ch in range(3)], -1)
            Rres = S / (1.0 + F)
            # validity of the source sample (clean interior of THIS face, 2 px feather);
            # outside the face (corner slivers past the render joint) fall back to its tone
            cd = sample(cdist, pxs, pys, order=1)
            own = sample(owner.astype(np.float64), pxs, pys, order=0) == s["id"]
            wv = (np.clip((cd - 2.0) / 2.0, 0.0, 1.0) * own)[:, None]
            LPs = np.where(own[:, None], LPs, np.array(s["mean_lin"])[None, :])
            base = Rres * wv + LPs * (1 - wv)
            # PROD: ridge irregularity from the source face's own local fundamental: strength
            # |Az| lowers crests where the source ridge is weak or broken, arg(Az) shifts ridges
            # sideways; where the source sample is invalid there is no modulation
            Az = (sample(An_re, pxs, pys, order=1) + 1j * sample(An_im, pxs, pys, order=1)) * wv[:, 0] + (1.0 - wv[:, 0])
            cm = np.clip(1.0 + CREST_MOD_K * (np.abs(Az) - 1.0), 0.0, CREST_MOD_MAX)
            u_eff = u_t + PHASE_K * np.angle(Az) / (2.0 * np.pi)
            g, _ = groove_profile(u_eff)
            U_full.ravel()[sel] = u_eff
            # PROD: colour is the source with its periodic profile divided out, no groove
            # modulation added (COL_GROOVE_GAIN = 0); residual stripes are removed after the loop
            gm = g - gn_mean
            amp = 2.0 * s["c1"] * COL_GROOVE_GAIN * (gg.max() - gg.min())
            c = base * (1.0 + amp * gm)[:, None]
            # grain: residual relative luminance, band-limited by the render itself
            Yr = 0.2126 * Rres[:, 0] + 0.7152 * Rres[:, 1] + 0.0722 * Rres[:, 2]
            Yl = 0.2126 * LPs[:, 0] + 0.7152 * LPs[:, 1] + 0.0722 * LPs[:, 2]
            gr = (Yr / Yl - 1.0) * wv[:, 0]
            pat_groove = -CHIS_DEPTH_MM + CHIS_DEPTH_MM * g * cm
            pat = pat_groove + GRAIN_SIGMA_MM * np.clip(gr / grain_std, -GRAIN_CLIP_NEG, GRAIN_CLIP_POS)
            desc = ("procedural grooves: period %.3f mm, tile rotation %d deg (grooves at %d deg), "
                    "asymmetric profile (2nd harmonic %.2f at %+d deg); ridge strength and sideways "
                    "wander from the source face's measured local fundamental; colour tone, cloudiness "
                    "and ragged detail from render chiseled face %d (rho %d), groove stripes removed%s"
                    % (per_in * 25.4, rho_t, (90 + rho_t) % 180, CH_A2, CH_PSI2_DEG, cell["src"],
                       s["rho_src"], ", mirrored along the grooves" if cell["mirror_v"] else ""))
            rotd, mir = rho_t, bool(cell["mirror_v"])
        ease = np.where(t_in < EASE_W_IN, EASE_MM * (1.0 - np.clip(t_in, 0, None) / EASE_W_IN) ** 2, 0.0)
        hmm = JOINT_DEPTH_MM + pat - ease
        col.reshape(-1, 3)[sel] = c
        hgt.ravel()[sel] = hmm
        stats[typ].append(pat)
        report_faces.append({"index": k, "type": typ, "rotation_deg": int(rotd), "mirrored": bool(mir),
                             "source": desc, "i": cell["i"], "j": cell["j"],
                             "pattern_mm_min": float(pat.min()), "pattern_mm_max": float(pat.max())})
    print("faces done %.0fs" % (time.time() - t0))
    # PROD: remove residual groove stripes from every Chiseled face's colour (albedo only)
    destripe_log = {}
    for cell in lay["cells"]:
        if cell["type"] == "chiseled":
            b_, a_ = destripe(col, fid, U_full, cell["index"], period_atlas_px)
            destripe_log[cell["index"]] = {"fundamental_before": round(b_, 5), "fundamental_after": round(a_, 5)}
    print("destripe (relative G fundamental, before -> after): %s" % json.dumps(destripe_log))
    print("destripe done %.0fs" % (time.time() - t0))
    # PROD: tone. The owner judged the installed (lifestyle) tile darker and warmer than the CG
    # render; c03 measured the lit Matte faces there. One per-channel linear gain moves the
    # atlas's Matte mean onto that target; faces and joints keep all relative variation.
    tone = json.load(open(out_path("_work", "lifestyle_tone.json")))
    target_lin = np.array(tone["target_lin"])
    matte_cells = [c_["index"] for c_ in lay["cells"] if c_["type"] == "matte"]
    mmask = np.isin(fid, matte_cells)
    matte_mean_lin = col[mmask].astype(np.float64).mean(axis=0)
    tone_gain = target_lin / matte_mean_lin
    col *= tone_gain.astype(np.float32)[None, None, :]
    np.clip(col, 0.0, 1.0, out=col)
    print("tone: atlas Matte mean sRGB %s -> target %s, linear gain %s" % (
        np.round(lin_to_srgb(matte_mean_lin), 1).tolist(), tone["target_srgb"], np.round(tone_gain, 4).tolist()))
    # ---- export ---------------------------------------------------------------------------
    srgb = np.round(lin_to_srgb(col)).astype(np.uint8)
    save_image(Image.fromarray(srgb, "RGB"), "textures", "Color.png", optimize=False)
    b16 = np.round(np.clip(hgt / H_RANGE_MM, 0, 1) * 65535.0).astype(np.uint16)
    save_image(Image.fromarray(b16), "textures", "Bump16.png")
    save_image(Image.fromarray(fid.astype(np.uint16)), "textures", "face_ids.png")
    np.save(out_path("_work", "height_mm.npy"), hgt)
    clipped = int((hgt > H_RANGE_MM).sum() + (hgt < 0).sum())
    json.dump({"faces": report_faces,
               "params_mm": {"joint_depth": JOINT_DEPTH_MM, "raw_sigma": RAW_SIGMA_MM, "raw_clip": RAW_CLIP_MM,
                             "chis_depth": CHIS_DEPTH_MM, "grain_sigma": GRAIN_SIGMA_MM, "chis_source_shrink": CH_SHRINK,
                             "grain_clip_sigma_units": [-GRAIN_CLIP_NEG, GRAIN_CLIP_POS],
                             "crest_mod_k": CREST_MOD_K, "crest_mod_max": CREST_MOD_MAX, "phase_k": PHASE_K,
                             "col_groove_gain": COL_GROOVE_GAIN,
                             "matte_micro_sigma": MATTE_MICRO_SIGMA_MM,
                             "matte_micro_clip": MATTE_MICRO_CLIP_MM, "ease": EASE_MM,
                             "ease_width_in": EASE_W_IN, "h_range": H_RANGE_MM},
               "chiseled_profile": {"a2": CH_A2, "psi2_deg": CH_PSI2_DEG, "period_in": per_in},
               "joint_srgb": JOINT_SRGB, "matte_shrink": shrink, "clipped_px": clipped,
               "source_ridge_modulation": {str(k): v for k, v in mod_stats.items()},
               "destripe": {str(k): v for k, v in destripe_log.items()},
               "tone": {"target_srgb": tone["target_srgb"], "matte_mean_before_srgb": lin_to_srgb(matte_mean_lin).round(1).tolist(),
                        "linear_gain": tone_gain.tolist(), "joint_srgb_after": lin_to_srgb(srgb_to_lin(np.array(JOINT_SRGB)) * tone_gain).round(1).tolist()}},
              open(out_path("_work", "build_faces.json"), "w"), indent=1)
    print("wrote maps; clipped height px %d; total %.0fs" % (clipped, time.time() - t0))


if __name__ == "__main__":
    sys.exit(main())
