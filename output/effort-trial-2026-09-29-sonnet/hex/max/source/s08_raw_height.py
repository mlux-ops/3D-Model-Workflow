"""Step 08: Raw relief from the render.

Shading model (single directional light, small slopes): I = I0 - K dh/dl + n, where l is the
image-plane direction toward the light. The height is recovered by a Wiener inversion whose
signal-to-noise ratio rho(f) is measured from the render itself (Raw versus Matte spectra, s05).
Frequencies perpendicular to the light carry no shading signal, so the estimate there is
shrunk to zero; the composition step (s10) fills that wedge from another face rotated by 90 deg.

Units: h' = K*h in (grey level * source pixel). Conversion to mm is a single global factor
chosen in s10 from the slope statistics (see README)."""

import json
import os
import sys

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, save_npy, save_text, out_path  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402
from s03_faces import hex_dist_inside  # noqa: E402
from s04_chisel_measure import crop_padded  # noqa: E402

LUMW = np.array([0.2126, 0.7152, 0.0722])
RAW_WHOLE = [(-1, 0), (0, 3), (1, 1), (1, 4), (2, 3), (4, 1), (4, 2), (5, 4)]
NWIN = 512
INSET0 = 5.0          # source px kept clear of the joint (valid face interior)
TAPER = 45.0          # px over which the reflected padding fades to zero

# SNR of the shading signal in the light-parallel direction, per band (from s05: (P_raw/P_matte - 1)/0.9)
RHO_F = np.array([0.0234, 0.0395, 0.0607, 0.0857, 0.1214, 0.1714, 0.2429, 0.3536])
RHO_V = np.array([8.9, 11.6, 11.1, 11.9, 10.1, 8.9, 7.0, 4.6])
F_LO = 0.02           # below this the shading is treated as albedo cloudiness
F_HI = 0.42


def rho_of_f(f):
    r = np.interp(np.log(np.maximum(f, 1e-6)), np.log(RHO_F), RHO_V)
    lo = np.clip(f / F_LO, 0.0, 1.0) ** 3
    hi = np.clip((F_HI - f) / 0.06, 0.0, 1.0)
    return r * lo * hi


def face_centre(grid, i, j):
    F = grid["F_px"]
    cx = grid["x0"] + i * grid["col_pitch_px"]
    cy = grid["y0"] + ((F / 2.0) if (i % 2) else 0.0) + j * F
    return cx, cy


def edge_normals():
    c30, s30 = np.cos(np.deg2rad(30.0)), np.sin(np.deg2rad(30.0))
    return np.array([[0.0, 1.0], [c30, s30], [c30, -s30]])


def reflect_into_hexagon(dx, dy, a0):
    """Map points outside the hexagon (inradius a0) to inside by reflecting across the most
    violated edge, repeated; any point that is still outside is shrunk onto the boundary."""
    N = edge_normals()
    px, py = dx.copy(), dy.copy()
    for _ in range(3):
        t = np.stack([px * n[0] + py * n[1] for n in N])           # (3, ...)
        k = np.argmax(np.abs(t), axis=0)
        tk = np.take_along_axis(t, k[None], 0)[0]
        v = np.abs(tk) - a0
        out = v > 0
        if not out.any():
            break
        nx = N[k, 0]
        ny = N[k, 1]
        s = np.sign(tk)
        px = np.where(out, px - 2.0 * v * s * nx, px)
        py = np.where(out, py - 2.0 * v * s * ny, py)
    t = np.stack([np.abs(px * n[0] + py * n[1]) for n in N])
    m = t.max(axis=0)
    sh = np.where(m > a0, a0 / np.maximum(m, 1e-9), 1.0)
    return px * sh, py * sh


def padded_window(img, grid, i, j, n=NWIN, visible=None):
    """Window of `img` (H,W[,3]) centred on face (i,j); everything outside the valid hexagon
    (module hexagon inset by INSET0) is replaced by a mirrored copy of the face interior and
    faded to the face mean. Returns (win, taper_weight, valid_mask, centre_in_window)."""
    F = grid["F_px"]
    cx, cy = face_centre(grid, i, j)
    x0, y0 = int(round(cx)) - n // 2, int(round(cy)) - n // 2
    ccx, ccy = cx - x0, cy - y0
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float64)
    dx, dy = xs - ccx, ys - ccy
    d = hex_dist_inside(dx, dy, F)
    a0 = F / 2.0 - INSET0
    rx, ry = reflect_into_hexagon(dx, dy, a0)
    srcx, srcy = rx + ccx + x0, ry + ccy + y0
    H, W = img.shape[:2]
    srcx = np.clip(srcx, 0, W - 1.001)
    srcy = np.clip(srcy, 0, H - 1.001)
    if img.ndim == 2:
        win = ndi.map_coordinates(img, [srcy, srcx], order=1)
    else:
        win = np.stack([ndi.map_coordinates(img[..., c], [srcy, srcx], order=1) for c in range(3)], -1)
    valid = d >= INSET0
    v = np.maximum(INSET0 - d, 0.0)
    tw = np.where(v <= 0, 1.0, np.where(v >= TAPER, 0.0, 0.5 * (1 + np.cos(np.pi * v / TAPER))))
    return win, tw, valid, (ccx, ccy)


def freq_grids(n):
    f1 = np.fft.fftfreq(n)
    FX, FY = np.meshgrid(f1, f1)
    return FX, FY, np.hypot(FX, FY)


def wiener(win, tw, valid, psi_deg):
    """Return (h_prime, shade, albedo_res) for a luminance window.
    h_prime: height estimate (grey level * px); shade: part of I explained by the height;
    albedo_res: I - shade (mean restored)."""
    n = win.shape[0]
    FX, FY, FR = freq_grids(n)
    lx, ly = np.cos(np.deg2rad(psi_deg)), np.sin(np.deg2rad(psi_deg))
    mean = win[valid].mean()
    w = (win - mean) * tw
    Iw = np.fft.fft2(w)
    f = np.maximum(FR, 1e-9)
    c = (FX * lx + FY * ly) / f
    rho = rho_of_f(FR)
    g = rho * c * c / (rho * c * c + 1.0)                 # Wiener gain of the shading component
    Hf = 1j * rho * (FX * lx + FY * ly) / (2 * np.pi * f * f * (rho * c * c + 1.0)) * Iw
    Hf[0, 0] = 0.0
    h = np.real(np.fft.ifft2(Hf))
    shade = np.real(np.fft.ifft2(g * Iw))
    alb = w - shade
    return h, shade, alb + mean, mean


def estimate_light_axis(lum, grid, faces):
    """Second angular harmonic of the band power gives the light axis (model A + B cos^2)."""
    n = 256
    f1 = np.fft.fftshift(np.fft.fftfreq(n))
    FX, FY = np.meshgrid(f1, f1)
    FR = np.hypot(FX, FY)
    TH = np.arctan2(FY, FX)
    band = (FR > 0.04) & (FR < 0.22)
    res = []
    tot = 0.0
    for (i, j) in faces:
        win, tw, valid, _ = padded_window(lum, grid, i, j, n=n)
        w = (win - win[valid].mean()) * tw
        w = w - ndi.gaussian_filter(w, 12.0) * tw
        P = np.abs(np.fft.fftshift(np.fft.fft2(w))) ** 2
        C = (P[band] * np.exp(2j * TH[band])).sum()
        res.append(0.5 * np.degrees(np.angle(C)))
        tot = tot + C
    return 0.5 * np.degrees(np.angle(tot)), res


def mirror_extend(arr, cen, F):
    """Replace everything outside the valid hexagon by the mirror image of the valid interior
    (heights and albedo are legitimate surfaces when mirrored; shaded luminance is not)."""
    n = arr.shape[0]
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float64)
    rx, ry = reflect_into_hexagon(xs - cen[0], ys - cen[1], F / 2.0 - INSET0)
    sx, sy = rx + cen[0], ry + cen[1]
    if arr.ndim == 2:
        return ndi.map_coordinates(arr, [sy, sx], order=1, mode="nearest")
    return np.stack([ndi.map_coordinates(arr[..., c], [sy, sx], order=1, mode="nearest") for c in range(3)], -1)


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    rgb = load_srgb(RENDER_PATH)
    lum = rgb @ LUMW
    psi, per_face = estimate_light_axis(lum, grid, RAW_WHOLE)
    print("light axis psi (image coords, y down): pooled %.2f deg; per face %s"
          % (psi, np.round(per_face, 1)))
    save_text(json.dumps({"psi_deg": psi, "per_face_deg": per_face}), "work", "light_axis.json")
    sign_path = out_path("work", "light_sign.json")
    lower_left = os.path.exists(sign_path) and json.load(open(sign_path))["toward_lower_left"]
    psi_l = psi + (180.0 if lower_left else 0.0)
    print("light toward %s (psi_l = %.2f deg)" % ("lower-left" if lower_left else "upper-right (default, s08c not run yet)", psi_l))
    F = grid["F_px"]
    H_all, A_all, M_all, info = [], [], [], []
    for (i, j) in RAW_WHOLE:
        win, tw, valid, cen = padded_window(lum, grid, i, j)
        h, shade, alb, mean = wiener(win, tw, valid, psi_l)
        win_rgb, _, _, _ = padded_window(rgb, grid, i, j)
        mrgb = win_rgb[valid].mean(0)
        alb_rgb = win_rgb - shade[..., None] * (mrgb / (mrgb @ LUMW))[None, None, :]
        ys, xs = np.mgrid[0:NWIN, 0:NWIN].astype(np.float64)
        d = hex_dist_inside(xs - cen[0], ys - cen[1], F)
        vin = d > 14
        lx, ly = np.cos(np.deg2rad(psi_l)), np.sin(np.deg2rad(psi_l))
        gx = ndi.sobel(h, axis=1) / 8.0
        gy = ndi.sobel(h, axis=0) / 8.0
        sl = (gx * lx + gy * ly)[vin]
        expl = float(np.var(shade[vin]) / np.var((win - mean)[vin]))
        h_ext = mirror_extend(h, cen, F)
        a_ext = mirror_extend(alb_rgb, cen, F)
        H_all.append(h_ext.astype(np.float32))
        A_all.append(a_ext.astype(np.float32))
        M_all.append(mrgb)
        info.append({"i": i, "j": j, "h_rms": float(h[vin].std()), "slope_l_rms": float(sl.std()),
                     "shading_variance_explained": expl, "mean_rgb": [float(x) for x in mrgb],
                     "alb_res_std_lum": float((alb_rgb @ LUMW)[vin].std())})
        print("face (%2d,%d): h' rms %.2f  slope' rms(l) %.3f  shading variance explained %.2f  albedo-residual std %.2f"
              % (i, j, h[vin].std(), sl.std(), expl, (alb_rgb @ LUMW)[vin].std()))
    save_npy(np.stack(H_all), "work", "pool_raw_h.npy")
    save_npy(np.stack(A_all), "work", "pool_raw_alb.npy")
    save_text(json.dumps({"faces": info, "psi_axis_deg": psi, "psi_toward_light_deg": psi_l}, indent=1),
              "work", "pool_raw_info.json")


if __name__ == "__main__":
    main()
