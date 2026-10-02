"""Raw faces: estimate light axis, derive height from shading (Wiener inverse along light axis), compare with luminance-as-height."""
import json
from scipy import ndimage
from common import *

hexes = json.load(open(RUN + "/work/render_hexes.json"))
L = json.load(open(RUN + "/work/render_lattice.json"))
R = L["R"]
SQ3 = np.sqrt(3.0)
im = np.asarray(Image.open(RENDER).convert("RGB")).astype(np.float64)
lum = im @ np.array([0.299, 0.587, 0.114])
Hh, Ww = lum.shape

raws = [h for h in hexes if 2.8 < h["hp_sd"] < 5 and h["coh"] > 0.2]
print("raw:", [(h["i"], h["j"], round(h["cov"], 2)) for h in raws])
mattes = [h for h in hexes if h["hp_sd"] < 2.2 and h["coh"] < 0.06 and h["cov"] > 0.9]
print("matte full:", len(mattes))

# light axis: average structure tensor over raw faces (band-limited)
hp = lum - ndimage.gaussian_filter(lum, 4.0)
hp = ndimage.gaussian_filter(hp, 1.0)
gx = ndimage.sobel(hp, axis=1)
gy = ndimage.sobel(hp, axis=0)
yy, xx = np.mgrid[0:Hh, 0:Ww]


def inner(h, r=0.85):
    dx = np.abs(xx - h["cx"])
    dy = np.abs(yy - h["cy"])
    ap = SQ3 * R * r / 2
    return (dy <= ap) & (SQ3 * dx + dy <= SQ3 * R * r)


sxx = syy = sxy = 0
for h in raws:
    m = inner(h)
    sxx += (gx[m] ** 2).sum(); syy += (gy[m] ** 2).sum(); sxy += (gx[m] * gy[m]).sum()
th = 0.5 * np.arctan2(2 * sxy, sxx - syy)
print("raw gradient axis (deg, y down): %.1f  coherence %.3f" % (np.rad2deg(th), np.sqrt((sxx - syy) ** 2 + 4 * sxy ** 2) / (sxx + syy)))
# spectral check: power along axis vs perpendicular
json.dump({"light_axis_deg": float(np.rad2deg(th))}, open(guard(RUN + "/work/raw_light_axis.json"), "w"))
