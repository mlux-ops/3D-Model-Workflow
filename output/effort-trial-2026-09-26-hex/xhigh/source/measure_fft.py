"""Step 5: precise chiseled geometry from the 2D spectrum, groove profile by phase folding,
joint colour, and per-type pool area in the render.

Writes _work/render_measure.json, used by build_maps.py.
"""
import os
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from guard import inp, save_image, write_text, WORK_DIR

R = np.asarray(Image.open(inp("elm_formed_hex_sand_layout_render.webp")).convert("RGB")).astype(np.float64)
H, W, _ = R.shape
lum = R @ np.array([0.2126, 0.7152, 0.0722])
L = json.load(open(os.path.join(WORK_DIR, "render_lattice.json")))
S = json.load(open(os.path.join(WORK_DIR, "render_cell_stats.json")))
Rc, half_f, x0, y0, pitch = L["Rc"], L["half_f"], L["x0"], L["y0"], L["col_pitch"]
PXIN = L["px_per_in"]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)

# ---------------- nearest-centre assignment over the whole render -------------------
cents = np.array([[c["cx"], c["cy"]] for c in L["cells"]])
best = np.full((H, W), 1e18)
second = np.full((H, W), 1e18)
owner = np.full((H, W), -1, dtype=np.int32)
for n, (cx, cy) in enumerate(cents):
    d = (xx - cx) ** 2 + (yy - cy) ** 2
    upd = d < best
    second = np.where(upd, best, np.minimum(second, d))
    owner = np.where(upd, n, owner)
    best = np.where(upd, d, best)
# distance to the Voronoi boundary between nearest and second nearest centre;
# neighbouring centres are 2*half_f apart, so (d2 - d1) / (2 * 2 * half_f) is exact on the bisector
edge_d = (second - best) / (4.0 * half_f)
key = {n: "%d,%d" % (c["j"], c["k"]) for n, c in enumerate(L["cells"])}
stat = {"%d,%d" % (s["j"], s["k"]): s for s in S}


def ctype(s):
    if s["coherence"] > 0.6:
        return "chiseled"
    if s["hp_std"] > 3.0:
        return "raw"
    return "matte"


# ---------------- joint colour: pixels on the joint centreline -------------------------
jmask = edge_d < 0.6
core = R[jmask]
face_ring = R[(edge_d > 8) & (edge_d < 14)]
joint_rgb = np.median(core, axis=0)
print("joint centreline median RGB", np.round(joint_rgb, 1), " n", len(core))
print("face ring (8-14 px in) median RGB", np.round(np.median(face_ring, axis=0), 1))
prof_edge = []
for d0 in np.arange(0, 12, 0.5):
    sel = (edge_d >= d0) & (edge_d < d0 + 0.5)
    prof_edge.append((float(d0), [round(float(v), 1) for v in np.median(R[sel], axis=0)]))
print("median RGB vs distance from joint centreline (px):")
for d0, v in prof_edge:
    print("   %.1f  %s" % (d0, v))

# ---------------- per type pool area (interior > 6 px from the joint centreline) --------
area = {"matte": 0, "raw": 0, "chiseled": 0}
face_px = 2 * np.sqrt(3) * (half_f - 6) ** 2
own_type = np.full((H, W), "", dtype=object)
for n, k in key.items():
    if k in stat:
        t = ctype(stat[k])
    else:
        t = None
    if t is None:
        continue
    a = ((owner == n) & (edge_d > 6)).sum()
    area[t] += a
print("pool area in full-face units (interior >6 px from joint):",
      {k: round(v / face_px, 2) for k, v in area.items()})

# ---------------- chiseled: 2D spectrum peak --------------------------------------------
hp = lum - ndi.gaussian_filter(lum, 8.0)
meas = {}
for k, s in stat.items():
    if ctype(s) != "chiseled":
        continue
    n = [i for i, kk in key.items() if kk == k][0]
    cx, cy = cents[n]
    r = 128
    if cx - r < 0 or cy - r < 0 or cx + r > W or cy + r > H:
        continue
    p = hp[int(cy) - r:int(cy) + r, int(cx) - r:int(cx) + r]
    win = np.outer(np.hanning(2 * r), np.hanning(2 * r))
    N = 2048
    F = np.abs(np.fft.fftshift(np.fft.fft2(p * win, (N, N))))
    fy, fx = np.meshgrid(np.fft.fftshift(np.fft.fftfreq(N)), np.fft.fftshift(np.fft.fftfreq(N)), indexing="ij")
    fr = np.hypot(fx, fy)
    band = (fr > 1 / 9.0) & (fr < 1 / 4.5) & (fx >= 0)
    i = np.argmax(np.where(band, F, 0))
    kx, ky = fx.flat[i], fy.flat[i]
    period = 1 / np.hypot(kx, ky)
    normal = np.degrees(np.arctan2(ky, kx))            # image coords, y down
    groove = (normal + 90) % 180
    # phase fold across grooves: coordinate along the normal
    u = ((xx[int(cy) - r:int(cy) + r, int(cx) - r:int(cx) + r] - cx) * np.cos(np.radians(normal)) +
         (yy[int(cy) - r:int(cy) + r, int(cx) - r:int(cx) + r] - cy) * np.sin(np.radians(normal)))
    ph = (u / period) % 1.0
    circ = ((xx[int(cy) - r:int(cy) + r, int(cx) - r:int(cx) + r] - cx) ** 2 +
            (yy[int(cy) - r:int(cy) + r, int(cx) - r:int(cx) + r] - cy) ** 2) < (0.95 * r) ** 2
    bins = np.linspace(0, 1, 25)
    idx = np.digitize(ph[circ], bins) - 1
    lp = lum[int(cy) - r:int(cy) + r, int(cx) - r:int(cx) + r][circ]
    prof = np.array([lp[idx == b].mean() for b in range(24)])
    # local phase stability: fold in 4 quadrants separately, compare the phase of the fundamental
    phs = []
    for qy in (0, 1):
        for qx in (0, 1):
            q = np.zeros_like(circ)
            q[qy * r:(qy + 1) * r, qx * r:(qx + 1) * r] = True
            q &= circ
            z = (lum[int(cy) - r:int(cy) + r, int(cx) - r:int(cx) + r][q] * np.exp(-2j * np.pi * ph[q])).mean()
            phs.append(np.degrees(np.angle(z)))
    # amplitude modulation along grooves: complex demodulation
    z = hp[int(cy) - r:int(cy) + r, int(cx) - r:int(cx) + r] * np.exp(-2j * np.pi * u / period)
    zs = ndi.gaussian_filter(z.real, period) + 1j * ndi.gaussian_filter(z.imag, period)
    amp = np.abs(zs)[circ]
    meas[k] = {"groove_deg_img": round(float(groove), 2), "period_px": round(float(period), 3),
               "period_mm": round(float(period / PXIN * 25.4), 3),
               "profile_lum": [round(float(v), 2) for v in prof],
               "quadrant_phase_deg": [round(float(v), 1) for v in phs],
               "amp_mod_cv": round(float(amp.std() / amp.mean()), 3),
               "mean_rgb": s["mean_rgb"]}
    print("%s groove %.2f deg  period %.3f px = %.3f mm  quad phases %s  amp cv %.2f" % (
        k, groove, period, period / PXIN * 25.4, np.round(phs, 0), amp.std() / amp.mean()))
    print("    profile", np.round(prof - prof.mean(), 1))

write_text(os.path.join(WORK_DIR, "render_measure.json"), json.dumps(
    {"joint_rgb": joint_rgb.tolist(), "edge_profile": prof_edge, "pool_faces": {k: v / face_px for k, v in area.items()},
     "chiseled": meas}, indent=1))
np.save(os.path.join(WORK_DIR, "render_owner.npy"), owner)
np.save(os.path.join(WORK_DIR, "render_edge_d.npy"), edge_d.astype(np.float32))
