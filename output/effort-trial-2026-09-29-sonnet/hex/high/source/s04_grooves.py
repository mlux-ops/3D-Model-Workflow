"""Measure chiseled groove period, orientation, profile from the render (perpendicular-to-groove mean profile)."""
import json
from scipy import ndimage
from common import *

hexes = json.load(open(RUN + "/work/render_hexes.json"))
L = json.load(open(RUN + "/work/render_lattice.json"))
R = L["R"]
SQ3 = np.sqrt(3.0)
im = np.asarray(Image.open(RENDER).convert("RGB")).astype(np.float64)
lum = im @ np.array([0.299, 0.587, 0.114])

chis = [h for h in hexes if h["hp_sd"] > 6 and h["cov"] > 0.9]
print(len(chis), "full chiseled hexes")
out = []
for h in chis:
    cx, cy = h["cx"], h["cy"]
    # crop a square of half-size 0.55 R * ... rotate so grooves are vertical, sample inside inscribed circle
    best = None
    for ang in np.arange(-8, 8.01, 0.25):
        a = np.deg2rad(h["groove_dir"] + ang)      # groove direction in image coords (x right, y down)
        ux, uy = np.cos(a), np.sin(a)              # along groove
        vx, vy = -uy, ux                           # across groove
        # sample a grid in (s along, t across) within radius 0.75*apothem
        rad = 0.80 * SQ3 * R / 2
        s = np.arange(-rad, rad, 1.0)
        t = np.arange(-rad, rad, 0.25)
        S, T = np.meshgrid(s, t, indexing="ij")
        X = cx + S * ux + T * vx
        Y = cy + S * uy + T * vy
        v = ndimage.map_coordinates(lum, [Y, X], order=1)
        inside = (S ** 2 + T ** 2) < rad ** 2
        prof = np.where(inside, v, np.nan)
        m = np.nanmean(prof, axis=0)      # mean along grooves -> profile across
        m = m - np.nanmean(m)
        contrast = np.nanstd(m)
        if best is None or contrast > best[0]:
            best = (contrast, ang, t, m)
    contrast, ang, t, m = best
    m0 = np.nan_to_num(m)
    # period from autocorrelation
    win = np.hanning(len(m0))
    f = np.abs(np.fft.rfft(m0 * win, n=len(m0) * 8)) ** 2
    fr = np.fft.rfftfreq(len(m0) * 8, d=0.25)           # cycles per px
    sel = (fr > 1 / 20.0) & (fr < 1 / 3.0)
    pk = fr[sel][np.argmax(f[sel])]
    period = 1 / pk
    out.append(dict(i=h["i"], j=h["j"], dir=h["groove_dir"] + ang, period_px=period, contrast=contrast))
    print("i%d j%d dir %.2f  refine %.2f  period %.3f px  contrast %.2f" % (h["i"], h["j"], h["groove_dir"] + ang, ang, period, contrast))
    np.save(guard(RUN + "/work/groove_profile_i%d_j%d.npy" % (h["i"], h["j"])), np.stack([t, m]))
json.dump(out, open(guard(RUN + "/work/groove_meas.json"), "w"), indent=1)
