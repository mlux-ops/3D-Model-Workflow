import json
from common import *

hexes = json.load(open(RUN + "/work/render_hexes.json"))
im = Image.open(RENDER).convert("RGB")


def hexof(i, j):
    return [h for h in hexes if h["i"] == i and h["j"] == j][0]


def crop(i, j, half=130, z=6, name=""):
    h = hexof(i, j)
    box = (int(h["cx"] - half), int(h["cy"] - half), int(h["cx"] + half), int(h["cy"] + half))
    c = im.crop(box)
    a = np.asarray(c).astype(float)
    # contrast stretch for viewing
    lo, hi = np.percentile(a, 1), np.percentile(a, 99.5)
    a = np.clip((a - lo) / (hi - lo) * 255, 0, 255).astype(np.uint8)
    c = Image.fromarray(a).resize((c.width * 3, c.height * 3), Image.LANCZOS)
    save_img(c, RUN + "/work/zoom_%s.png" % name)


crop(0, 3, 130, name="chis_vert")       # vertical grooves
crop(1, 4, 130, name="chis_diag")       # 30 deg
crop(0, 0, 130, name="raw_a")
crop(0, 1, 130, name="matte_a")

# folded profile of the vertical hex
d = np.load(RUN + "/work/groove_profile_i0_j3.npy")
t, m = d
P = 6.184
ph = (t % P) / P
bins = np.linspace(0, 1, 25)
idx = np.digitize(ph, bins) - 1
prof = np.array([np.nanmean(m[idx == k]) for k in range(24)])
print("folded profile (24 bins over one period):")
print(np.round(prof, 2))
