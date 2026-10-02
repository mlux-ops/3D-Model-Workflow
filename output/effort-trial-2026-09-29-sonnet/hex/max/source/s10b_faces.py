"""Step 10b: per-face content builders for the atlas (colour and height), all from source pixels.

Every atlas face is a composite of two distinct render faces (A and B), each moved into the atlas
frame by a rotation about the face centre, an optional mirror and the render->atlas scale
(64 px/in over the render's px/in), sampled with cubic interpolation from the mirror-extended
512 px windows made in steps 08/09.

matte     RGB fluctuation of two Matte faces, smooth ramp blend with variance-preserving weights;
          face tone from the sources' own face tones (variance preserved); height flat.
raw       height: Wiener height of two Raw faces mixed direction by direction with weights taken from
          the measured angular gain of the shading inversion, so each source supplies the wave
          directions the other one is blind to; albedo: ramp blend as for matte.
chiseled  colour: RGB of two Chiseled faces moved into the target groove orientation by D6
          elements, pitch-normalised, phase-aligned along the groove normal and ramp-blended
          (weights sum to 1 because the grooves are coherent); groove component G blended alike."""

import json
import os
import sys

import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import out_path  # noqa: E402
from geometry import source_to_atlas_scale, hex_inside  # noqa: E402
from s08_raw_height import face_centre, NWIN  # noqa: E402

SCALE = source_to_atlas_scale()
CR = 384                       # half size of the crop written per face (module circumradius 374.1 px)
HL = 512                       # half size of the raw spectral working window
TAPER_R0, TAPER_R1 = 440.0, 512.0
HP_LO, HP_HI = 0.030, 0.060    # raw height high-pass, cycles per render pixel
LOCAL_PHASE_SIGMA_PX = 40.0    # smoothing of the local groove-phase difference between the two Chiseled sources
TARGET_DIR_DEG = {"vert": 90.0, "diagS": 30.0, "diagF": 150.0}


def win_centre(grid, i, j):
    cx, cy = face_centre(grid, i, j)
    x0, y0 = int(round(cx)) - NWIN // 2, int(round(cy)) - NWIN // 2
    return (cx - x0, cy - y0)


class Pools:
    def __init__(self):
        grid = json.load(open(out_path("work", "render_grid.json")))
        info = json.load(open(out_path("work", "pool_info.json")))
        raw_info = json.load(open(out_path("work", "pool_raw_info.json")))
        self.info = info
        self.psi_axis = raw_info["psi_axis_deg"]
        self.matte = np.load(out_path("work", "pool_matte.npy"))
        self.matte_mean = np.load(out_path("work", "pool_matte_mean.npy"))
        self.matte_cen = [win_centre(grid, i, j) for i, j in info["matte"]]
        self.raw_h = np.load(out_path("work", "pool_raw_h.npy"))
        self.raw_alb = np.load(out_path("work", "pool_raw_alb.npy"))
        self.raw_cen = [win_centre(grid, f["i"], f["j"]) for f in raw_info["faces"]]
        self.raw_mean = np.array([f["mean_rgb"] for f in raw_info["faces"]])
        self.chis_rgb = np.load(out_path("work", "pool_chis_rgb.npy"))
        self.chis_G = np.load(out_path("work", "pool_chis_G.npy"))
        self.chis_cen = [tuple(c["centre"]) for c in info["chiseled"]]
        self.chis_pitch_mean = float(np.mean([c["pitch_px"] for c in info["chiseled"]]))
        self.tone = {k: np.array(v) for k, v in info["tone_mean_rgb"].items()}
        self.G_land, self.G_groove = info["G_p97"], info["G_p03"]
        gain = json.load(open(out_path("work", "angular_gain.json")))
        edges = np.array(gain["delta_edges_deg"])
        self.gain_x = 0.5 * (edges[:-1] + edges[1:])
        self.gain_y = np.mean([np.array(v) for v in gain["bands"].values()], axis=0)
        yy, xx = np.mgrid[0:NWIN, 0:NWIN]
        self.raw_alb_mean = []
        for k, cen in enumerate(self.raw_cen):
            m = np.hypot(xx - cen[0], yy - cen[1]) < 140.0
            self.raw_alb_mean.append(self.raw_alb[k][m].mean(0))
        self.raw_alb_mean = np.array(self.raw_alb_mean)

    def g2(self, delta_deg):
        return np.interp(delta_deg, self.gain_x, self.gain_y)


def src_coords(dx, dy, alpha_deg, mirror, cen, kappa=1.0, u_src=None, shift=(0.0, 0.0)):
    """Atlas offsets (px from the face centre) -> (row, col) in a source window.
    atlas = R(alpha) M^m source, so source = M^m R(-alpha) atlas / SCALE."""
    ax, ay = dx - shift[0], dy - shift[1]
    a = np.deg2rad(alpha_deg)
    c, s = np.cos(a), np.sin(a)
    rx = c * ax + s * ay
    ry = -s * ax + c * ay
    if mirror:
        ry = -ry
    sx, sy = rx / SCALE, ry / SCALE
    if kappa != 1.0:
        p = sx * u_src[0] + sy * u_src[1]
        sx = sx + (kappa - 1.0) * p * u_src[0]
        sy = sy + (kappa - 1.0) * p * u_src[1]
    return cen[1] + sy, cen[0] + sx


def sample(arr, rows, cols, order=3):
    coords = np.stack([rows, cols])
    if arr.ndim == 2:
        return ndimage.map_coordinates(arr, coords, order=order, mode="reflect")
    return np.stack([ndimage.map_coordinates(arr[..., c], coords, order=order, mode="reflect")
                     for c in range(arr.shape[2])], axis=-1)


def ramp_weight(dx, dy, blend):
    phi = np.deg2rad(blend["phi_deg"])
    t = (dx * np.cos(phi) + dy * np.sin(phi) - blend["offset_px"]) / blend["ramp_px"] + 0.5
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def vp_blend(a, b, w):
    w3 = w[..., None]
    return (w3 * a + (1.0 - w3) * b) / np.sqrt(w3 ** 2 + (1.0 - w3) ** 2)


def face_tone(w, dx, dy, mu_a, mu_b, type_mean):
    inside = hex_inside(dx, dy) > 4.0
    mw = float(w[inside].mean())
    dev = (mw * (mu_a - type_mean) + (1.0 - mw) * (mu_b - type_mean)) / np.sqrt(mw ** 2 + (1.0 - mw) ** 2)
    return type_mean + dev


def build_matte(face, P, dx, dy):
    A, B = face["A"], face["B"]
    fa = sample(P.matte[A["k"]], *src_coords(dx, dy, A["rotation_deg"], A["mirrored"], P.matte_cen[A["k"]]))
    fb = sample(P.matte[B["k"]], *src_coords(dx, dy, B["rotation_deg"], B["mirrored"], P.matte_cen[B["k"]]))
    w = ramp_weight(dx, dy, face["blend"])
    tone = face_tone(w, dx, dy, P.matte_mean[A["k"]], P.matte_mean[B["k"]], P.tone["matte"])
    return (tone + vp_blend(fa, fb, w)).astype(np.float32), {"tone_rgb": [float(x) for x in tone]}


def raw_albedo(face, P, dx, dy):
    A, B = face["A"], face["B"]
    ca, cb = P.raw_cen[A["k"]], P.raw_cen[B["k"]]
    fa = sample(P.raw_alb[A["k"]], *src_coords(dx, dy, A["rotation_deg"], A["mirrored"], ca)) - P.raw_alb_mean[A["k"]]
    fb = sample(P.raw_alb[B["k"]], *src_coords(dx, dy, B["rotation_deg"], B["mirrored"], cb)) - P.raw_alb_mean[B["k"]]
    w = ramp_weight(dx, dy, face["blend"])
    tone = face_tone(w, dx, dy, P.raw_alb_mean[A["k"]], P.raw_alb_mean[B["k"]], P.raw_alb_mean.mean(0))
    return (tone + vp_blend(fa, fb, w)).astype(np.float32), {"tone_rgb": [float(x) for x in tone]}


def raw_height(face, P, dxf, dyf):
    """Unscaled composite height (render level*px units) on the full 2*HL window."""
    n = 2 * HL
    r = np.hypot(dxf, dyf)
    tap = np.clip((TAPER_R1 - r) / (TAPER_R1 - TAPER_R0), 0.0, 1.0)
    tap = 0.5 - 0.5 * np.cos(np.pi * tap)
    specs, psis = [], []
    for role in ("A", "B"):
        s = face[role]
        h = sample(P.raw_h[s["k"]], *src_coords(dxf, dyf, s["rotation_deg"], s["mirrored"], P.raw_cen[s["k"]]))
        h = (h - h[r < 374.0].mean()) * tap
        specs.append(np.fft.fft2(h))
        psis.append((-P.psi_axis if s["mirrored"] else P.psi_axis) + s["rotation_deg"])
    fx = np.fft.fftfreq(n)
    FX, FY = np.meshgrid(fx, fx)
    th = np.degrees(np.arctan2(FY, FX))
    fr = np.hypot(FX, FY) * SCALE
    dA = np.abs(((th - psis[0] + 90.0) % 180.0) - 90.0)
    dB = np.abs(((th - psis[1] + 90.0) % 180.0) - 90.0)
    gA, gB = P.g2(dA), P.g2(dB)
    cA, cB = np.sqrt(gA / (gA + gB)), np.sqrt(gB / (gA + gB))
    expected = (gA ** 2 + gB ** 2) / (gA + gB)
    nrm = 1.0 / np.sqrt(np.clip(expected, 0.5, 1.0))
    hp = np.clip((fr - HP_LO) / (HP_HI - HP_LO), 0.0, 1.0)
    hp = 0.5 - 0.5 * np.cos(np.pi * hp)
    hc = np.real(np.fft.ifft2(nrm * (cA * specs[0] + cB * specs[1]) * hp))
    return hc, {"psi_A_deg": float(psis[0] % 180.0), "psi_B_deg": float(psis[1] % 180.0)}


def ncc(a, b):
    a = a - a.mean()
    b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-12))


def build_chiseled(face, P, dx, dy):
    tgt = np.deg2rad(TARGET_DIR_DEG[face["orientation"]])
    ut = np.array([-np.sin(tgt), np.cos(tgt)])
    atlas_pitch = P.chis_pitch_mean * SCALE
    w = ramp_weight(dx, dy, face["blend"])
    A, B = face["A"], face["B"]

    def coords(s, ddx, ddy, shift):
        th = np.deg2rad(s["line_dir_src_deg"])
        u_s = np.array([-np.sin(th), np.cos(th)])
        kappa = s["pitch_src_px"] / P.chis_pitch_mean
        return src_coords(ddx, ddy, s["rotation_deg"], s["mirrored"], P.chis_cen[s["k"]], kappa, u_s, shift)

    rgbA = sample(P.chis_rgb[A["k"]], *coords(A, dx, dy, (0.0, 0.0)))
    GA = sample(P.chis_G[A["k"]], *coords(A, dx, dy, (0.0, 0.0)))
    phi = np.deg2rad(face["blend"]["phi_deg"])
    t_lin = (dx * np.cos(phi) + dy * np.sin(phi) - face["blend"]["offset_px"]) / face["blend"]["ramp_px"]
    inside = hex_inside(dx, dy) > 12.0
    zone = inside & (np.abs(t_lin) < 0.6)
    ys, xs = np.nonzero(zone)
    ys, xs = ys[::3], xs[::3]
    pdx, pdy = dx[ys, xs], dy[ys, xs]
    n_ph = 24
    scores = np.zeros(n_ph)
    for j in range(n_ph):
        d = j * atlas_pitch / n_ph
        rows, cols = coords(B, pdx, pdy, (d * ut[0], d * ut[1]))
        g = ndimage.map_coordinates(P.chis_G[B["k"]], np.stack([rows, cols]), order=1, mode="reflect")
        scores[j] = ncc(GA[ys, xs], g)
    b = int(np.argmax(scores))
    sm, s0, sp = scores[(b - 1) % n_ph], scores[b], scores[(b + 1) % n_ph]
    den = sm - 2.0 * s0 + sp
    frac = 0.5 * (sm - sp) / den if den < -1e-9 else 0.0
    d0 = ((b + float(np.clip(frac, -0.5, 0.5))) % n_ph) * atlas_pitch / n_ph
    shift = (d0 * ut[0], d0 * ut[1])
    GB0 = sample(P.chis_G[B["k"]], *coords(B, dx, dy, shift))
    ncc_global = ncc(GA[zone], GB0[zone])

    k_rad = 2.0 * np.pi / atlas_pitch
    carrier = k_rad * (dx * ut[0] + dy * ut[1])
    ce, se = np.cos(carrier), np.sin(carrier)
    sig = LOCAL_PHASE_SIGMA_PX
    zr = ndimage.gaussian_filter(GA * ce, sig) * ndimage.gaussian_filter(GB0 * ce, sig) \
        + ndimage.gaussian_filter(GA * se, sig) * ndimage.gaussian_filter(GB0 * se, sig)
    zi = ndimage.gaussian_filter(GA * ce, sig) * ndimage.gaussian_filter(GB0 * se, sig) \
        - ndimage.gaussian_filter(GA * se, sig) * ndimage.gaussian_filter(GB0 * ce, sig)
    dphi = np.arctan2(zi, zr)
    keep = np.exp(-(t_lin / 1.1) ** 4)
    d1 = -0.30 * atlas_pitch * np.tanh(dphi / (2.0 * np.pi) / 0.30) * keep
    shift2 = (shift[0] + d1 * ut[0], shift[1] + d1 * ut[1])
    rgbB = sample(P.chis_rgb[B["k"]], *coords(B, dx, dy, shift2))
    GB = sample(P.chis_G[B["k"]], *coords(B, dx, dy, shift2))
    ncc_local = ncc(GA[zone], GB[zone])
    w3 = w[..., None]
    rgb = w3 * rgbA + (1.0 - w3) * rgbB
    G = w * GA + (1.0 - w) * GB
    return rgb.astype(np.float32), G.astype(np.float32), {
        "phase_shift_px": float(d0), "phase_ncc_global": float(ncc_global), "phase_ncc_local": float(ncc_local),
        "phase_ncc_worst_candidate": float(scores.min()), "local_shift_rms_px": float(np.sqrt((d1[zone] ** 2).mean())),
        "atlas_pitch_px": float(atlas_pitch)}
