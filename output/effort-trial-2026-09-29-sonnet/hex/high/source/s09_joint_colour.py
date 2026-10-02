"""Measure the joint (grout line) colour in the render: darkest pixel across each edge, and line width."""
import json
from scipy import ndimage
from srcs import *
from srcs import _im

pts = []
t = np.linspace(0.12, 0.88, 14)
for h in HEXES:
    ang = np.deg2rad(np.arange(7) * 60)
    vx = h["cx"] + RR * np.cos(ang)
    vy = h["cy"] + RR * np.sin(ang)
    for k in range(6):
        ex, ey = vx[k + 1] - vx[k], vy[k + 1] - vy[k]
        nx, ny = -ey, ex
        nn = np.hypot(nx, ny); nx, ny = nx / nn, ny / nn
        for tt in t:
            px, py = vx[k] + ex * tt, vy[k] + ey * tt
            if 12 < px < WW - 12 and 12 < py < HH - 12:
                pts.append((px, py, nx, ny))
pts = np.array(pts)
offs = np.arange(-8, 8.01, 0.5)
prof = np.zeros((len(pts), len(offs), 3))
for c in range(3):
    X = pts[:, 0:1] + pts[:, 2:3] * offs[None]
    Y = pts[:, 1:2] + pts[:, 3:4] * offs[None]
    prof[..., c] = ndimage.map_coordinates(_im[..., c], [Y, X], order=1)
lum = prof @ np.array([0.299, 0.587, 0.114])
# centre = argmin luminance within +-3 px
cen = np.abs(offs) <= 3
idx = np.argmin(np.where(cen[None], lum, 1e9), axis=1)
line = prof[np.arange(len(pts)), idx]
face = 0.5 * (prof[:, offs == -7.5].mean(1) + prof[:, offs == 7.5].mean(1))
print("edge samples:", len(pts))
print("line centre RGB median", np.median(line, 0).round(1), " p10", np.percentile(line, 10, axis=0).round(1))
print("flanking face RGB median", np.median(face, 0).round(1))
mp = np.median(prof, axis=0)
mlum = mp @ np.array([0.299, 0.587, 0.114])
print("median cross profile luminance (offset px: lum):")
for o, l in zip(offs, mlum):
    if abs(o) <= 4:
        print("  %4.1f  %.1f" % (o, l))
# FWHM of the dip
base = np.median(face @ np.array([0.299, 0.587, 0.114]))
dip = base - mlum
half = dip.max() / 2
inside = offs[dip >= half]
print("dip depth %.1f lum, FWHM %.2f px (= %.3f in at render scale)" % (dip.max(), inside.max() - inside.min() + 0.5, (inside.max() - inside.min() + 0.5) / RENDER_PPI))
json.dump({"line_centre_median": np.median(line, 0).tolist(), "line_centre_p10": np.percentile(line, 10, axis=0).tolist(),
           "face_flank_median": np.median(face, 0).tolist(), "fwhm_px": float(inside.max() - inside.min() + 0.5)},
          open(guard(RUN + "/work/joint_colour.json"), "w"), indent=1)
