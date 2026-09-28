"""Step 6: groove cross-profile and render light direction, from a forward model.

The render shades each Chiseled face with (a) a symmetric darkening in the groove
(ambient-occlusion-like, sign-definite: recessed = darker) and (b) a directional term
proportional to the groove wall slope times cos(light azimuth - groove normal). The three
groove families sit at 60 deg to each other, so fitting all faces jointly separates the
two terms, gives the groove width / bottom shape, and fixes the light azimuth AND sign.

Model over one period, u in periods, groove centred at 0.5 + phase_face:
  depth(u) = (1 - r^2)^p  for r = |u - c| / (w/2) < 1, else 0        (0..1)
  B(u)     = b0_face - k_ao * depth(u) + k_dir * cos(alpha - theta_u) * d depth / du
  then Gaussian blur sigma (periods) and 32-bin averaging.
B is linear luma relative to the face mean. theta_u is the +u direction (y-up degrees).
Writes _work/light_fit.json and _work/light_fit.png (model vs measured).
"""

import json
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import optimize

from common import load_lattice, render_rgb, srgb_to_lin, out_path, S3, hex_edge_distance_local
from guard import save_image

NB = 32
OS = 16          # oversampling of the model inside one bin


def face_fold(lat, c, Llin, phi_deg, per, clean=6.0):
    rp = lat["rp"]
    R = rp / S3
    Hr, Wr = Llin.shape
    X0 = max(0, int(c["cx"] - R - 2)); X1 = min(Wr, int(c["cx"] + R + 2))
    Y0 = max(0, int(c["cy"] - rp / 2 - 2)); Y1 = min(Hr, int(c["cy"] + rp / 2 + 2))
    ys, xs = np.mgrid[Y0:Y1, X0:X1].astype(np.float64)
    dx = xs + 0.5 - c["cx"]; dy = ys + 0.5 - c["cy"]
    m = hex_edge_distance_local(dx, dy, rp * 0.5) >= clean
    v = Llin[Y0:Y1, X0:X1][m]
    t = np.deg2rad(phi_deg)
    u = (dx[m] * np.cos(t) + dy[m] * np.sin(t)) / per
    ph = np.mod(u, 1.0)
    b = np.minimum((ph * NB).astype(int), NB - 1)
    fold = np.bincount(b, weights=v, minlength=NB) / np.bincount(b, minlength=NB)
    return fold / v.mean() - 1.0


def model_profile(w, p, k_ao, k_dir_eff, sigma, phase):
    n = NB * OS
    u = (np.arange(n) + 0.5) / n
    d = np.mod(u - 0.5 - phase + 0.5, 1.0) - 0.5      # signed distance to groove centre
    r = np.abs(d) / (w / 2.0)
    inside = r < 1.0
    depth = np.where(inside, np.clip(1.0 - r ** 2, 0, None) ** p, 0.0)
    # derivative d depth / du (periods^-1)
    dd = np.where(inside, -p * np.clip(1.0 - r ** 2, 1e-9, None) ** (p - 1.0) * 2.0 * r
                  / (w / 2.0) * np.sign(d), 0.0)
    B = -k_ao * depth + k_dir_eff * dd
    # circular Gaussian blur
    f = np.fft.rfftfreq(n, d=1.0 / n)
    Bf = np.fft.irfft(np.fft.rfft(B) * np.exp(-2 * (np.pi * f * sigma) ** 2), n)
    return Bf.reshape(NB, OS).mean(axis=1)


def main():
    lat = load_lattice()
    gr = json.load(open(out_path("_work", "grooves.json")))
    cells = {c["id"]: c for c in json.load(open(out_path("_work", "cells_raw.json")))}
    rgb = render_rgb()
    lin = srgb_to_lin(rgb)
    Llin = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    per = gr["period_px_mean"]
    faces = []
    for g in gr["faces"]:
        c = cells[g["id"]]
        fold = face_fold(lat, c, Llin, g["normal_img_deg"], per)
        theta_u = (-g["normal_img_deg"]) % 360.0
        faces.append({"id": g["id"], "fold": fold, "theta_u": theta_u, "frac": g["frac"]})
    nf = len(faces)

    def unpack(q):
        w, p, k_ao, k_dir, alpha, sigma = q[:6]
        rest = q[6:].reshape(nf, 2)
        return w, p, k_ao, k_dir, alpha, sigma, rest

    def resid(q):
        w, p, k_ao, k_dir, alpha, sigma, rest = unpack(q)
        out = []
        for f, (b0, ph) in zip(faces, rest):
            ce = np.cos(np.deg2rad(alpha - f["theta_u"]))
            mp = model_profile(w, p, k_ao, k_dir * ce, sigma, ph)
            out.append((mp + b0 - f["fold"]) * np.sqrt(max(f["frac"], 0.3)))
        return np.concatenate(out)

    best = None
    for alpha0 in (0, 45, 90, 135, 180, 225, 270, 315):
        for w0 in (0.35, 0.5, 0.65):
            q0 = [w0, 1.0, 0.1, 0.01, alpha0, 0.12]
            for f in faces:
                q0 += [0.0, (np.argmin(f["fold"]) + 0.5) / NB - 0.5]
            lb = [0.1, 0.1, 0.0, 0.0, -720, 0.02] + [-1, -2] * nf
            ub = [0.95, 4.0, 2.0, 2.0, 720, 0.4] + [1, 2] * nf
            try:
                r = optimize.least_squares(resid, np.array(q0), bounds=(lb, ub), max_nfev=4000)
            except Exception as e:
                print("fit failed", alpha0, w0, e)
                continue
            if best is None or r.cost < best.cost:
                best = r
    w, p, k_ao, k_dir, alpha, sigma, rest = unpack(best.x)
    alpha = alpha % 360.0
    rms = np.sqrt(np.mean(best.fun ** 2))
    print("best fit: groove width %.3f of period, bottom exponent p %.2f, k_ao %.4f, "
          "k_dir %.5f, light azimuth %.1f deg (y-up, toward light), blur %.3f periods, rms %.5f"
          % (w, p, k_ao, k_dir, alpha, sigma, rms))
    # the sign test: refit with azimuth forced to the opposite half-plane
    q = best.x.copy()
    q[4] = alpha + 180.0

    def resid_fixed(qq):
        z = np.concatenate([qq[:4], [alpha + 180.0], qq[4:]])
        return resid(z)
    q1 = np.concatenate([best.x[:4], best.x[5:]])
    lb = [0.1, 0.1, 0.0, 0.0, 0.02] + [-1, -2] * nf
    ub = [0.95, 4.0, 2.0, 2.0, 0.4] + [1, 2] * nf
    r2 = optimize.least_squares(resid_fixed, q1, bounds=(lb, ub), max_nfev=4000)
    rms2 = np.sqrt(np.mean(r2.fun ** 2))
    print("forced opposite azimuth %.1f: rms %.5f (best %.5f), k_dir there %.5f"
          % ((alpha + 180) % 360, rms2, rms, r2.x[3]))
    # per-family contrast summary
    res = {"groove_width_frac": w, "bottom_exponent_p": p, "k_ao": k_ao, "k_dir": k_dir,
           "light_azimuth_deg_yup": alpha, "blur_periods": sigma, "rms": rms,
           "opposite_azimuth_rms": rms2, "period_px": per,
           "faces": [{"id": f["id"], "theta_u": f["theta_u"], "b0": float(b0), "phase": float(ph)}
                     for f, (b0, ph) in zip(faces, rest)]}
    json.dump(res, open(out_path("_work", "light_fit.json"), "w"), indent=1)
    # plot
    im = Image.new("RGB", (800, 100 * ((nf + 1) // 2)), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    for k, (f, (b0, ph)) in enumerate(zip(faces, rest)):
        ox = 400 * (k % 2); oy = 100 * (k // 2) + 50
        ce = np.cos(np.deg2rad(alpha - f["theta_u"]))
        mp = model_profile(w, p, k_ao, k_dir * ce, sigma, ph) + b0
        for arr, col in ((f["fold"], (0, 0, 0)), (mp, (220, 0, 0))):
            pts = [(ox + 10 + i * 380 / (NB - 1), oy - 900 * arr[i]) for i in range(NB)]
            dr.line(pts, fill=col, width=2)
        dr.text((ox + 10, oy - 45), "id %d  u %.0f" % (f["id"], f["theta_u"]), fill=(0, 0, 200))
    save_image(im, "_work", "light_fit.png")


if __name__ == "__main__":
    sys.exit(main())
