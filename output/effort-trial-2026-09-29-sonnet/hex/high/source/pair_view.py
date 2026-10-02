"""Side-by-side view of the best-matching patch pairs found by verify.py (contrast stretched high-pass luminance)."""
import json
from scipy import ndimage
from common import *
Image.MAX_IMAGE_PIXELS = None
col = np.asarray(Image.open(RUN + "/textures/Color.png")).astype(np.float32)
lum = col @ np.array([0.299, 0.587, 0.114])
hp = lum - ndimage.gaussian_filter(lum, 8.0)
P = 112
def get(y, x, tr=0):
    ys = (np.arange(y - P // 2, y + P // 2)) % H; xs = (np.arange(x - P // 2, x + P // 2)) % W
    p = hp[np.ix_(ys, xs)]
    p = np.rot90(p, tr % 4)
    if tr >= 4: p = p[:, ::-1]
    return p
rows = []
d = json.load(open(RUN + "/work/matte_patch_matches.json"))
d = sorted(d, key=lambda r: -r["ncc"])[:2]
for r in d:
    a = get(r["y"], r["x"]); ym, xm, tr = r["match"]
    b = get(ym, xm)                       # match window in the atlas frame (transform applied to the query)
    q = get(r["y"], r["x"], tr)
    sd = a.std() * 3
    tiles = [np.clip(128 + 127 * t / sd, 0, 255) for t in (a, q, b)]
    rows.append(np.concatenate(tiles, 1))
img = np.concatenate(rows, 0).astype(np.uint8)
save_img(Image.fromarray(img).resize((img.shape[1] * 2, img.shape[0] * 2), Image.NEAREST), RUN + "/work/matte_pairs.png")
