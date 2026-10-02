"""Step 10b: assemble textures/Color.png, textures/Bump16.png and textures/face_ids.png.

Atlas 4489 x 4536 px (64 px/in), 8 columns x 7 rows of flat-top hexagons on a torus. Every pixel is
owned by the face with the largest inside-distance, so the image wraps on both axes by construction.
Joint = 8 px band (4 px inside each face edge, module boundary at its centre), drawn at half width
on every outer edge. Heights are built in millimetres above the joint floor:
  joint floor 0 mm, face plane FACE_MM.
  matte     flat at FACE_MM
  raw       FACE_MM + soft-clipped composite of two source heights, one common scale for all Raw faces;
            the scale is set from the rms slope target derived in s10c (relative to the Chiseled groove)
  chiseled  FACE_MM - CHIS_DEPTH_MM * groove weight from the source groove component
Bump16 = height / FULL_SCALE_MM * 65535 (white = high). Constants live in design.py.

Raw colour = de-shaded albedo (the render's shading is not baked in) times a one-sided cavity factor
1 - a*q, where q is the pit depth below the local mean of the finished Raw relief in rms units (clipped at
CAV_CLIP). The gain a is calibrated so that the band-pass luminance std of the Raw faces equals the render's
(work/raw_colour_target.json from s10d_raw_colour_contrast.py); the mean of each face is kept."""

import json
import os
import sys
import time

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import out_path, save_image, save_text  # noqa: E402
from geometry import (W, H, MM_PER_PX, face_centres, hex_inside, window_indices, window_offsets,  # noqa: E402
                      source_to_atlas_scale)
from design import (JOINT_RGB, JOINT_DEPTH_MM as FACE_MM, FULL_SCALE_MM, CHIS_DEPTH_MM, RAW_CLIP_MM,  # noqa: E402
                    EDGE_WIDTH_PX, calibration)
from s08_raw_height import LUMW  # noqa: E402
from s10d_raw_colour_contrast import dog, S1, S2, CORE_SRC_PX  # noqa: E402
import s10b_faces as F  # noqa: E402

RAW_SLOPE_TARGET = calibration()["raw_slope_target_full_gradient"]
HALF = 384
HALF_H = 512
CAV_SIGMA_PX = 12.0     # local-mean scale of the cavity term, atlas px (about 4.8 mm)
CAV_KNEE = 0.5          # softness of the one-sided pit function (softplus knee, rms units of the local relief)
CAV_CLIP = 3.0          # pit depth clip, rms units


def ownership(centres):
    owner = np.zeros((H, W), np.int16)
    best = np.full((H, W), -1e9, np.float32)
    for c in centres:
        x0, y0, xi, yi = window_indices(c["cx"], c["cy"], HALF)
        dx, dy = window_offsets(c["cx"], c["cy"], HALF)
        ins = hex_inside(dx, dy).astype(np.float32)
        ix = np.ix_(yi, xi)
        cur = best[ix]
        upd = ins > cur
        best[ix] = np.where(upd, ins, cur)
        owner[ix] = np.where(upd, np.int16(c["index"]), owner[ix])
    return owner, best


def apply_raw_cavity(colour, hmm, owner, own_in, raw_mask, raw_ids):
    """Darken the pits of the Raw faces in `colour` in place (one-sided, direction independent) and
    return the calibration record. hmm is the finished height in mm; the gain is set so that the
    band-pass luminance std of the Raw faces (mean of the faces) equals the render's."""
    target = json.load(open(out_path("work", "raw_colour_target.json")))["render"]["raw"]["band_std_mean"]
    scale = source_to_atlas_scale()
    core = raw_mask & (own_in > CORE_SRC_PX * scale)
    m = raw_mask.astype(np.float32)
    rel = (hmm - FACE_MM) * m
    local = ndi.gaussian_filter(rel, CAV_SIGMA_PX, mode="wrap") / np.maximum(
        ndi.gaussian_filter(m, CAV_SIGMA_PX, mode="wrap"), 1e-3)
    x = local - rel
    del local, rel
    x /= float(np.sqrt((x[core] ** 2).mean()))
    pit = CAV_KNEE * np.logaddexp(0.0, x / CAV_KNEE) * m
    del x, m
    q = np.minimum(pit / float(np.sqrt((pit[core] ** 2).mean())), CAV_CLIP).astype(np.float32)
    del pit
    lum = colour @ LUMW.astype(np.float32)
    band_lum = dog(lum, S1 * scale, S2 * scale, mode="wrap")
    band_q = dog(q, S1 * scale, S2 * scale, mode="wrap")
    albedo_std, cavity_std = [], []
    for idx in raw_ids:
        sel = core & (owner == idx)
        albedo_std.append(float(band_lum[sel].std()))
        cavity_std.append(float(band_q[sel].std()))
    l_mean = float(lum[core].mean())
    del lum, band_lum, band_q
    alb, cav = float(np.mean(albedo_std)), float(np.mean(cavity_std))
    gain = float(np.sqrt(max(target ** 2 - alb ** 2, 0.0)) / (l_mean * cav))
    for idx in raw_ids:
        own = owner == idx
        mean_q = float(q[core & own].mean())
        f = (1.0 - gain * q[own]) / (1.0 - gain * mean_q)
        colour[own] *= f[:, None]
    return {"target_band_std": target, "albedo_band_std_before": alb, "cavity_band_rms_per_unit_q": cav,
            "mean_luminance": l_mean, "gain_a": gain, "max_darkening_fraction": gain * CAV_CLIP,
            "sigma_px": CAV_SIGMA_PX, "knee_rms": CAV_KNEE, "clip_rms": CAV_CLIP,
            "predicted_band_std_after": float(np.sqrt(alb ** 2 + (gain * l_mean * cav) ** 2))}


def main():
    t0 = time.time()
    layout = json.load(open(out_path("work", "layout.json")))
    faces = layout["faces"]
    centres = face_centres()
    P = F.Pools()
    owner, own_in = ownership(centres)
    print("ownership %.1fs  unowned %d" % (time.time() - t0, int((owner == 0).sum())))

    colour = np.zeros((H, W, 3), np.float32)
    hmm = np.zeros((H, W), np.float32)
    hraw = np.zeros((H, W), np.float32)
    raw_mask = np.zeros((H, W), bool)
    grad_sq_sum, grad_n = 0.0, 0
    face_stats = {}
    for f, c in zip(faces, centres):
        idx = c["index"]
        assert f["index"] == idx, (f["index"], idx)
        _, _, xi, yi = window_indices(c["cx"], c["cy"], HALF)
        ix = np.ix_(yi, xi)
        dx, dy = window_offsets(c["cx"], c["cy"], HALF)
        mine = owner[ix] == idx
        core = mine & (own_in[ix] >= 4.0)
        if f["type"] == "matte":
            rgb, st = F.build_matte(f, P, dx, dy)
            hv = np.full(dx.shape, FACE_MM, np.float32)
            hmm[ix] = np.where(mine, hv, hmm[ix])
        elif f["type"] == "raw":
            rgb, st = F.raw_albedo(f, P, dx, dy)
            dxf, dyf = window_offsets(c["cx"], c["cy"], HALF_H)
            hc, st2 = F.raw_height(f, P, dxf, dyf)
            st.update(st2)
            gy, gx = np.gradient(hc)
            g2 = (gx ** 2 + gy ** 2)[128:-128, 128:-128]
            hcc = hc[128:-128, 128:-128]
            grad_sq_sum += float(g2[core].sum())
            grad_n += int(core.sum())
            hraw[ix] = np.where(mine, (hcc - hcc[core].mean()).astype(np.float32), hraw[ix])
            raw_mask[ix] = raw_mask[ix] | mine
        else:
            rgb, G, st = F.build_chiseled(f, P, dx, dy)
            wgt = np.clip((P.G_land - G) / (P.G_land - P.G_groove), 0.0, 1.0)
            hv = (FACE_MM - CHIS_DEPTH_MM * wgt).astype(np.float32)
            hmm[ix] = np.where(mine, hv, hmm[ix])
        colour[ix] = np.where(mine[..., None], rgb, colour[ix])
        face_stats[str(idx)] = st
        print("face %2d %-8s %s  %.0fs" % (idx, f["type"], f["orientation"] or "", time.time() - t0))

    grad_rms = float(np.sqrt(grad_sq_sum / grad_n))
    K = RAW_SLOPE_TARGET * MM_PER_PX / grad_rms
    hmm[raw_mask] = FACE_MM + RAW_CLIP_MM * np.tanh(K * hraw[raw_mask] / RAW_CLIP_MM)
    print("raw composite rms|grad| %.4f units/px -> K = %.5f mm/unit (slope target %.2f)" % (grad_rms, K, RAW_SLOPE_TARGET))
    del hraw

    cavity = apply_raw_cavity(colour, hmm, owner, own_in, raw_mask, [f["index"] for f in faces if f["type"] == "raw"])
    print("raw cavity: gain a = %.4f (max darkening %.1f %%), band std %.3f -> %.3f (render %.3f)"
          % (cavity["gain_a"], 100.0 * cavity["max_darkening_fraction"], cavity["albedo_band_std_before"],
             cavity["predicted_band_std_after"], cavity["target_band_std"]))

    t = np.clip((own_in - 4.0) / EDGE_WIDTH_PX + 0.5, 0.0, 1.0)
    t = (t * t * (3.0 - 2.0 * t)).astype(np.float32)
    colour = t[..., None] * colour + (1.0 - t[..., None]) * JOINT_RGB
    hfin = t * hmm
    del t, hmm

    color8 = np.clip(np.rint(colour), 0, 255).astype(np.uint8)
    del colour
    level = np.clip(np.rint(hfin / FULL_SCALE_MM * 65535.0), 0, 65535).astype(np.uint16)
    fid = np.where(own_in >= 4.0, owner, 0).astype(np.uint16)
    print("arrays ready %.0fs" % (time.time() - t0))

    save_image(Image.fromarray(color8, "RGB"), "textures", "Color.png")
    save_image(Image.fromarray(level), "textures", "Bump16.png")
    save_image(Image.fromarray(fid), "textures", "face_ids.png")
    print("saved %.0fs" % (time.time() - t0))

    build = {
        "joint_rgb": JOINT_RGB.tolist(), "face_mm": FACE_MM, "full_scale_mm": FULL_SCALE_MM,
        "mm_per_level": FULL_SCALE_MM / 65535.0, "chiseled_depth_mm": CHIS_DEPTH_MM,
        "raw_clip_mm": RAW_CLIP_MM, "raw_slope_target": RAW_SLOPE_TARGET, "raw_grad_rms_units_per_px": grad_rms,
        "raw_scale_mm_per_unit": K, "edge_width_px": EDGE_WIDTH_PX, "raw_cavity": cavity, "faces": face_stats,
    }
    save_text(json.dumps(build, indent=1), "work", "build_stats.json")


if __name__ == "__main__":
    main()
