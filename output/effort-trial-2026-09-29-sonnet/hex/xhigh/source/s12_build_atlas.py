"""Build Color.png, Bump16.png and face_ids.png for the ELM Formed Hexagon Sand atlas.

Atlas: 8 columns x 7 rows of flat-top hexagons, 64 px/in, 4489 x 4536 px, wrapping on both axes.
Face (i, j): column i, row j. Centre x = i * 561.125; y = (j + 0.5) * 648 for even i, j * 648 for odd i.
Face index = j * 8 + i + 1. Hex distance d = max(|dy|, |dx| * sqrt(3)/2 + |dy|/2) in atlas px:
face if d <= 320 (10.000 in across flats), module edge at d = 324 (10.125 in), so the joint is 8 px (1/8 in).

Matte and raw faces are image-quilted from the render's own faces at native render resolution and then
resampled to the atlas. Chiseled faces get a procedural groove field at the measured pitch and profile, with
amplitude and grain quilted from the render's chiseled faces (rotated into a canonical frame).
Height (mm above the joint floor): face plane 1.6 mm, 2.6 mm = 65535.
"""
import json
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
import guard
import render_grid as rg
import quilt

PPI = 64.0
NC, NR = 8, 7
W, H = 4489, 4536
COLP = W / NC
ROWP = 648.0
FACE_R = 320.0
MOD_R = 324.0
WIN = 376
S_UP = PPI / rg.PX_PER_IN

FULL_MM = 2.6
PLANE_MM = 1.6
JOINT_RGB = np.array([218.0, 209.0, 195.0])
K_MATTE_H = 0.006
K_RAW_H = 0.03
RAW_CLIP_MM = 1.0
CHIS_DEPTH_MM = 0.30
CHIS_M_MAX = 1.5
CHIS_M_MIN = 0.35
K_GRAIN_H = 0.02
K_RAW_COL = 1.15
K_GRAIN_COL = 1.1
K_GROOVE_COL = 0.95
RAMP_PX = 2.5

RNG_BASE = 20260929


def load_libs():
    Zf = np.load(rg.WORK + "libs.npz")
    libs = {}
    for name, block, ov in (("matte", 56, 14), ("raw", 36, 10)):
        n = int(Zf[name + "_n"])
        stack = quilt.pad_windows([Zf["%s_%d_ch" % (name, k)] for k in range(n)])
        masks = quilt.pad_windows([Zf["%s_%d_m" % (name, k)] for k in range(n)], False)
        ids = [tuple(int(v) for v in Zf["%s_%d_id" % (name, k)][:2]) for k in range(n)]
        lib = quilt.Library(stack, masks, block)
        lib.scale[0] /= np.sqrt(3.0)
        libs[name] = dict(lib=lib, ov=ov, ids=ids)
    # chiseled: canonical frame (groove wave vector along +x)
    n = int(Zf["chis_n"])
    N = Zf["chis_0_amp"].shape[0]
    rad = N // 2
    c = np.arange(N) - rad
    cy, cx = np.meshgrid(c, c, indexing="ij")
    chans, masks, ids = [], [], []
    for k in range(n):
        wave = float(Zf["chis_%d_id" % k][2])
        w = np.radians(wave)
        qx = np.cos(w) * cx - np.sin(w) * cy + rad
        qy = np.sin(w) * cx + np.cos(w) * cy + rad
        amp = ndi.map_coordinates(Zf["chis_%d_amp" % k], [qy, qx], order=3, mode="constant")
        grain = ndi.map_coordinates(Zf["chis_%d_grain" % k], [qy, qx], order=3, mode="constant")
        m = ndi.map_coordinates(Zf["chis_%d_m" % k].astype(np.float32), [qy, qx], order=1, mode="constant") > 0.99
        m = ndi.binary_erosion(m, iterations=2)
        chans.append(np.stack([np.clip(amp, 0, None), grain], axis=-1))
        masks.append(m)
        ids.append((int(Zf["chis_%d_id" % k][0]), int(Zf["chis_%d_id" % k][1])))
    lib = quilt.Library(np.stack(chans), np.stack(masks), 48, allowed_t=(0, 2, 4, 6))
    libs["chis"] = dict(lib=lib, ov=12, ids=ids)
    return libs


def profile_tables(gp):
    p16 = np.array(gp["profile16"], np.float64)
    Fc = np.fft.rfft(p16) / 16.0
    grid = np.linspace(0, 1, 4097)
    tab = np.full_like(grid, Fc[0].real)
    for h in range(1, 8):
        tab += 2 * np.real(Fc[h] * np.exp(2j * np.pi * h * (grid - 0.5 / 16)))
    tab += np.real(Fc[8] * np.exp(2j * np.pi * 8 * (grid - 0.5 / 16)))
    a1 = 2 * np.abs(Fc[1])
    norm_lum = tab / a1
    height = (tab - tab.max()) / (tab.max() - tab.min())
    return grid, norm_lum, height, a1


def fbm_phase(rng, wobble_lags, wobble_std, n=2048):
    """Toroidal fractional-Gaussian phase field (in groove periods) with the measured structure function."""
    lags = np.array(wobble_lags[1:], float)
    sd = np.array(wobble_std[1:], float)
    hexp = np.polyfit(np.log(lags), np.log(sd), 1)[0]
    f = np.hypot(np.fft.fftfreq(n)[:, None], np.fft.fftfreq(n)[None, :])
    f[0, 0] = np.inf
    spec = f ** (-(hexp + 1.0))
    field = np.real(np.fft.ifft2(np.fft.fft2(rng.standard_normal((n, n))) * spec))
    lag_atlas = int(round(wobble_lags[-1] * S_UP))
    dx = field[:, lag_atlas:] - field[:, :-lag_atlas]
    dy = field[lag_atlas:, :] - field[:-lag_atlas, :]
    emp = np.sqrt(0.5 * (dx.std() ** 2 + dy.std() ** 2))
    return field * (wobble_std[-1] / emp), hexp


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def sample_tone(rng, tones, typ):
    t = tones[typ]
    mean = np.array(t["mean"])
    cov = np.array(t["cov"])
    dev = rng.multivariate_normal(np.zeros(3), cov)
    maha = np.sqrt(dev @ np.linalg.solve(cov, dev))
    if maha > 2.0:
        dev *= 2.0 / maha
    return mean + dev


def quilt_face(lib_entry, rng, out_h, out_w):
    canvas, placed = quilt.quilt(lib_entry["lib"], out_h, out_w, lib_entry["ov"], rng)
    src = sorted(set(lib_entry["ids"][p[0]] for p in placed))
    tcount = {}
    for p in placed:
        tcount[p[3]] = tcount.get(p[3], 0) + 1
    return canvas, dict(n_blocks=len(placed), source_faces=[list(s) for s in src], transforms={str(k): v for k, v in sorted(tcount.items())})


def main():
    t_start = time.time()
    layout = json.load(open(rg.WORK + "layout.json"))
    summ = json.load(open(rg.WORK + "lib_summary.json"))
    gp = json.load(open(rg.WORK + "groove_profile.json"))
    libs = load_libs()
    print("libraries loaded in %.1f s; candidates: %s" % (time.time() - t_start, {k: len(v["lib"].cand) for k, v in libs.items()}))
    grid, norm_lum, height_prof, a1 = profile_tables(gp)
    pitch_px = gp["period_in"] * PPI
    print("groove pitch %.4f atlas px, first-harmonic amplitude of the measured profile %.3f levels, upsample %.4f" % (pitch_px, a1, S_UP))
    amp_mean = gp["amp_mean"]

    color = np.zeros((H, W, 3), np.uint8)
    color[:] = np.round(JOINT_RGB).astype(np.uint8)
    bump = np.zeros((H, W), np.uint16)
    ids = np.zeros((H, W), np.uint16)
    faces = []

    ix = np.arange(2 * WIN + 1)
    for j in range(NR):
        for i in range(NC):
            idx = j * NC + i + 1
            typ = {0: "matte", 1: "raw", 2: "chiseled"}[layout["types"]["%d,%d" % (i, j)]]
            wave = int(layout["orient"]["%d,%d" % (i, j)])
            rng = np.random.default_rng([RNG_BASE, idx])
            cx = i * COLP
            cy = (j + 0.5) * ROWP if i % 2 == 0 else j * ROWP
            px0, py0 = int(np.floor(cx)) - WIN, int(np.floor(cy)) - WIN
            U, V = np.meshgrid(px0 + ix + 0.5 - cx, py0 + ix + 0.5 - cy)
            d = np.maximum(np.abs(V), np.abs(U) * (np.sqrt(3) / 2) + np.abs(V) / 2)
            tone = sample_tone(rng, summ["tones"], typ)
            rec = dict(index=idx, i=i, j=j, type=typ, cx=cx, cy=cy, tone=[float(v) for v in tone], rotation_deg=0, mirrored=False)

            if typ in ("matte", "raw"):
                entry = libs[typ]
                canvas, qinfo = quilt_face(entry, rng, 336, 384)
                r0 = (canvas.shape[0] - 1) / 2.0
                c0 = (canvas.shape[1] - 1) / 2.0
                coords = [V / S_UP + r0, U / S_UP + c0]
                ch = np.stack([ndi.map_coordinates(canvas[..., k], coords, order=3, mode="nearest") for k in range(4)], axis=-1)
                z, chroma = ch[..., 0], ch[..., 1:]
                if typ == "matte":
                    rgb = tone[None, None, :] + z[..., None] + chroma
                    hf = PLANE_MM + K_MATTE_H * z
                else:
                    rgb = tone[None, None, :] + K_RAW_COL * z[..., None] + chroma
                    hf = PLANE_MM + RAW_CLIP_MM * np.tanh(K_RAW_H * z / RAW_CLIP_MM)
                rec["source"] = "image quilt of %d blocks from render faces %s (dihedral transform counts %s)" % (qinfo["n_blocks"], qinfo["source_faces"], qinfo["transforms"])
                rec["quilt"] = qinfo
            else:
                entry = libs["chis"]
                canvas, qinfo = quilt_face(entry, rng, 400, 400)
                r0 = (canvas.shape[0] - 1) / 2.0
                c0 = (canvas.shape[1] - 1) / 2.0
                w = np.radians(wave)
                cxc = np.cos(w) * U + np.sin(w) * V
                cyc = -np.sin(w) * U + np.cos(w) * V
                coords = [cyc / S_UP + r0, cxc / S_UP + c0]
                amp = np.clip(ndi.map_coordinates(canvas[..., 0], coords, order=3, mode="nearest"), 0, None)
                grain = ndi.map_coordinates(canvas[..., 1], coords, order=3, mode="nearest")
                wob, hexp = fbm_phase(rng, gp["wobble_lags"], gp["wobble_std_periods"])
                oy = int(rng.integers(0, wob.shape[0] - ix.size))
                ox = int(rng.integers(0, wob.shape[1] - ix.size))
                psi = wob[oy:oy + ix.size, ox:ox + ix.size]
                phase = cxc / pitch_px + psi + rng.random()
                ph = np.mod(phase, 1.0)
                lum = np.interp(ph, grid, norm_lum)
                hp = np.interp(ph, grid, height_prof)
                rgb = tone[None, None, :] + (K_GROOVE_COL * amp * lum + K_GRAIN_COL * grain)[..., None]
                m = np.clip(amp / amp_mean, CHIS_M_MIN, CHIS_M_MAX)
                hf = PLANE_MM + CHIS_DEPTH_MM * (m * (hp + 0.5) - 0.5) + K_GRAIN_H * grain
                rec["rotation_deg"] = wave
                rec["groove_wave_angle_deg"] = wave
                rec["wobble_hurst"] = float(hexp)
                rec["source"] = ("procedural grooves at the measured %.4f in pitch and measured profile, wave angle %d deg (image coordinates, y down), phase-wobble field (measured structure function); "
                                 "amplitude and fine grain from an image quilt of %d blocks from render chiseled faces %s, rotated into a canonical frame" % (gp["period_in"], wave, qinfo["n_blocks"], qinfo["source_faces"]))
                rec["quilt"] = qinfo

            alpha = np.clip(FACE_R + 1.0 - d, 0.0, 1.0)
            rgb = alpha[..., None] * rgb + (1 - alpha[..., None]) * JOINT_RGB[None, None, :]
            ramp = 1.0 - smoothstep((d - FACE_R) / RAMP_PX)
            hmm = hf * ramp
            code = np.clip(np.round(hmm / FULL_MM * 65535.0), 0, 65535).astype(np.uint16)
            mod = d <= MOD_R
            face = d <= FACE_R
            ys = (py0 + ix) % H
            xs = (px0 + ix) % W
            sel = np.ix_(ys, xs)
            c_sub = color[sel]
            c_sub[mod] = np.clip(np.round(rgb[mod]), 0, 255).astype(np.uint8)
            color[sel] = c_sub
            b_sub = bump[sel]
            b_sub[mod] = code[mod]
            bump[sel] = b_sub
            i_sub = ids[sel]
            i_sub[face] = idx
            ids[sel] = i_sub
            faces.append(rec)
            print("face %2d (%d,%d) %-8s wave %3d  %.1f s" % (idx, i, j, typ, wave, time.time() - t_start), flush=True)

    guard.save_image(Image.fromarray(color, "RGB"), guard.RUN + "/textures/Color.png")
    guard.save_image(Image.fromarray(bump), guard.RUN + "/textures/Bump16.png")
    guard.save_image(Image.fromarray(ids), guard.RUN + "/textures/face_ids.png")
    json.dump(dict(faces=faces, params=dict(PPI=PPI, W=W, H=H, COLP=COLP, ROWP=ROWP, FACE_R=FACE_R, MOD_R=MOD_R, FULL_MM=FULL_MM, PLANE_MM=PLANE_MM, JOINT_RGB=JOINT_RGB.tolist(),
                                            K_MATTE_H=K_MATTE_H, K_RAW_H=K_RAW_H, RAW_CLIP_MM=RAW_CLIP_MM, CHIS_DEPTH_MM=CHIS_DEPTH_MM, CHIS_M_MAX=CHIS_M_MAX, CHIS_M_MIN=CHIS_M_MIN,
                                            K_GRAIN_H=K_GRAIN_H, K_RAW_COL=K_RAW_COL, K_GRAIN_COL=K_GRAIN_COL, K_GROOVE_COL=K_GROOVE_COL, RAMP_PX=RAMP_PX, S_UP=S_UP, pitch_px=pitch_px, rng_base=RNG_BASE)),
              open(guard.safe(rg.WORK + "face_info.json"), "w"), indent=1)
    print("done in %.1f s" % (time.time() - t_start))


if __name__ == "__main__":
    main()
