"""Compare luminance texture energy per face type: render hexes vs atlas faces resampled to render scale."""
import json
from scipy import ndimage
from common import *
import srcs
Image.MAX_IMAGE_PIXELS = None
LUMV = np.array([0.299, 0.587, 0.114])
col = np.asarray(Image.open(RUN + "/textures/Color.png")).astype(np.float32)
ids = np.asarray(Image.open(RUN + "/textures/face_ids.png")).astype(np.int32)
meta = json.load(open(RUN + "/work/build_meta.json"))
hexes = json.load(open(RUN + "/work/render_hexes.json"))
lumA = col @ LUMV
sc = 1.0 / srcs.F_UP
def hp(l, s1=1.5, s2=12.0):
    return ndimage.gaussian_filter(l, s1) - ndimage.gaussian_filter(l, s2)
# atlas at render scale
small = ndimage.zoom(lumA, sc, order=1)
idsm = ids[::1, ::1]
idsS = ndimage.zoom(ids.astype(np.float32), sc, order=0).astype(np.int32)
hpA = hp(small)
inner = ndimage.binary_erosion(idsS > 0, iterations=int(14 * 1.0))
res = {}
for t in ("matte", "raw", "chiseled"):
    sel = [m["index"] for m in meta if m["type"] == t]
    vals = np.concatenate([hpA[(idsS == k) & inner] for k in sel])
    res[t] = float(vals.std())
print("atlas hp std by type", res)
lumR = np.asarray(srcs._im).astype(np.float32) @ LUMV
hpR = hp(lumR)
cls = {}
for h in hexes:
    cls.setdefault(h.get("type", "?"), []).append(h)
print({k: len(v) for k, v in cls.items()}, list(hexes[0].keys()))

rres = {}
for t in ("matte", "raw", "chiseled"):
    vals = []
    for h in hexes:
        if srcs.classify(h) != t:
            continue
        x0, y0, w, hh = srcs.window_of(h)
        hpw = srcs.crop(hpR, x0, y0, w, hh)
        m = srcs.hex_mask_window(h["cx"], h["cy"], 0.85, x0, y0, w, hh)
        if m.sum() > 6000:
            vals.append(hpw[m])
    rres[t] = (float(np.concatenate(vals).std()), len(vals))
print("render hp std by type (std, n)", rres)
