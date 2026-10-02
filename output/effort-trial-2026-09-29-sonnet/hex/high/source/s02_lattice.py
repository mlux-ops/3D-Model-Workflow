"""Fit the flat-top hexagon lattice in the layout render (joint-line ridge response)."""
import json
from scipy import ndimage, optimize
from common import *

im = np.asarray(Image.open(RENDER).convert("RGB")).astype(np.float64)
lum = im @ np.array([0.299, 0.587, 0.114])
# joints are thin light-grey lines: they are LOWER in R than the cream face (grey vs cream)
# use blue-red difference? Check via ridge on luminance (dark ridge) with small sigma
bl = ndimage.gaussian_filter(lum, 1.0)
bg = ndimage.gaussian_filter(lum, 6.0)
ridge = bg - bl            # positive where darker than surroundings
ridge = np.clip(ridge, 0, None)
save_npy(ridge.astype(np.float32), RUN + "/work/render_ridge.npy")

Hh, Ww = lum.shape
SQ3 = np.sqrt(3.0)


def edges(R, ox, oy, ncol=24, nrow=14):
    """Return sample points along all hexagon edges. Flat-top: centre (ox+1.5R i, oy+SQ3 R j + (i%2)*SQ3R/2)."""
    pts = []
    t = np.linspace(0.08, 0.92, 12)
    for i in range(-2, ncol):
        for j in range(-2, nrow):
            cx = ox + 1.5 * R * i
            cy = oy + SQ3 * R * (j + 0.5 * (i % 2))
            ang = np.deg2rad(np.arange(7) * 60)
            vx = cx + R * np.cos(ang)
            vy = cy + R * np.sin(ang)
            for k in range(6):
                pts.append((vx[k] + (vx[k + 1] - vx[k]) * t, vy[k] + (vy[k + 1] - vy[k]) * t))
    px = np.concatenate([p[0] for p in pts])
    py = np.concatenate([p[1] for p in pts])
    return px, py


def score(p):
    R, ox, oy = p
    px, py = edges(R, ox, oy)
    ok = (px > 3) & (px < Ww - 4) & (py > 3) & (py < Hh - 4)
    v = ndimage.map_coordinates(ridge, [py[ok], px[ok]], order=1)
    return -v.mean()


best = None
for R in np.arange(178, 188, 1.0):
    for ox in np.arange(0, 1.5 * R, 12):
        for oy in np.arange(0, SQ3 * R, 12):
            s = score((R, ox, oy))
            if best is None or s < best[0]:
                best = (s, R, ox, oy)
print("coarse", best)
res = optimize.minimize(score, best[1:], method="Nelder-Mead", options={"xatol": 0.02, "fatol": 1e-6, "maxiter": 600})
R, ox, oy = res.x
print("fit R=%.3f ox=%.3f oy=%.3f score=%.4f" % (R, ox, oy, res.fun))
print("flat-to-flat px", SQ3 * R, " px/in", SQ3 * R / 10.0)
json.dump({"R": R, "ox": ox, "oy": oy, "flat_px": SQ3 * R, "px_per_in_render": SQ3 * R / 10.0},
          open(guard(RUN + "/work/render_lattice.json"), "w"), indent=1)
