"""Diagnostic: locate the strongest 0/60/120 deg dark-line responses inside Matte and Raw faces and
save 1:1 contrast-stretched crops of the top three (_work/view_ghost_<n>.png) for visual review."""
import os
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.signal import fftconvolve
import common as C
from guard import TEX_DIR, WORK_DIR, save_image

col = np.asarray(Image.open(os.path.join(TEX_DIR, "Color.png")).convert("RGB")).astype(np.float64)
fid = np.asarray(Image.open(os.path.join(TEX_DIR, "face_ids.png"))).astype(np.int64)
rep = json.load(open(os.path.join(TEX_DIR, "report.json")))
types = {f["index"]: f["type"] for f in rep["faces"]}
lum = col @ np.array([0.2126, 0.7152, 0.0722])
H2, W2 = C.H // 2, C.W // 2
l2 = lum[:2 * H2, :2 * W2].reshape(H2, 2, W2, 2).mean(axis=(1, 3))
fh = fid[0:2 * H2:2, 0:2 * W2:2]
_, ed, _, _ = C.lattice_maps()
ed2 = ed[0:2 * H2:2, 0:2 * W2:2] / 2.0
dark = np.clip(ndi.gaussian_filter(l2, 2.0) - l2, 0, None)
Lk = 31
resp = []
for ang in (0, 60, 120):
    k = np.zeros((Lk, Lk))
    c = Lk // 2
    for t in np.linspace(-c, c, 4 * Lk):
        k[int(round(c + t * np.sin(np.radians(ang)))), int(round(c + t * np.cos(np.radians(ang))))] = 1
    k /= k.sum()
    resp.append(fftconvolve(np.pad(dark, c, mode="wrap"), k, mode="valid"))
resp = np.max(resp, axis=0)
ok = np.vectorize(lambda f: types.get(f, "") in ("matte", "raw"))(fh) & (ed2 > 12)
v = np.where(ok, resp, 0)
for i in range(3):
    j = int(np.argmax(v))
    y, x = divmod(j, v.shape[1])
    print("resp %.2f at full-res (%d, %d), face %d %s" % (v[y, x], 2 * x, 2 * y, fh[y, x], types[fh[y, x]]))
    cc = col[max(0, 2 * y - 150):2 * y + 150, max(0, 2 * x - 150):2 * x + 150]
    m = cc.reshape(-1, 3).mean(0)
    save_image(Image.fromarray(np.clip(m + (cc - m) * 3, 0, 255).astype(np.uint8)),
               os.path.join(WORK_DIR, "view_ghost_%d.png" % i))
    v[max(0, y - 40):y + 40, max(0, x - 40):x + 40] = 0
