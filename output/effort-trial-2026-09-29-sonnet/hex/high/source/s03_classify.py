"""Classify each hexagon in the render: matte / raw / chiseled, with groove orientation."""
import json
from scipy import ndimage
from PIL import ImageDraw, ImageFont
from common import *

L = json.load(open(RUN + "/work/render_lattice.json"))
R, ox, oy = L["R"], L["ox"], L["oy"]
SQ3 = np.sqrt(3.0)
im = np.asarray(Image.open(RENDER).convert("RGB")).astype(np.float64)
lum = im @ np.array([0.299, 0.587, 0.114])
Hh, Ww = lum.shape
hp = lum - ndimage.gaussian_filter(lum, 3.0)

# structure tensor for orientation
gx = ndimage.sobel(ndimage.gaussian_filter(lum, 0.8), axis=1)
gy = ndimage.sobel(ndimage.gaussian_filter(lum, 0.8), axis=0)
Jxx = ndimage.gaussian_filter(gx * gx, 6)
Jyy = ndimage.gaussian_filter(gy * gy, 6)
Jxy = ndimage.gaussian_filter(gx * gy, 6)

yy, xx = np.mgrid[0:Hh, 0:Ww]


def hex_mask(cx, cy, r):
    # flat-top hexagon of circumradius r (flat-to-flat = sqrt3 r)
    dx = np.abs(xx - cx)
    dy = np.abs(yy - cy)
    ap = SQ3 * r / 2
    return (dy <= ap) & (SQ3 * dx + dy <= SQ3 * r)


hexes = []
for i in range(-2, 24):
    for j in range(-2, 14):
        cx = ox + 1.5 * R * i
        cy = oy + SQ3 * R * (j + 0.5 * (i % 2))
        if cx < -R or cx > Ww + R or cy < -R or cy > Hh + R:
            continue
        m_full = hex_mask(cx, cy, R * 0.92)
        cov = m_full.sum() / (SQ3 * 1.5 * (R * 0.92) ** 2) / 1.0
        # fraction of the full hexagon area inside the image
        area_full = 3 * SQ3 / 2 * (R * 0.92) ** 2
        cov = m_full.sum() / area_full
        if cov < 0.15:
            continue
        m = m_full
        sd = float(hp[m].std())
        jxx, jyy, jxy = Jxx[m].mean(), Jyy[m].mean(), Jxy[m].mean()
        # dominant gradient orientation
        theta = 0.5 * np.arctan2(2 * jxy, jxx - jyy)      # gradient direction (rad)
        coh = float(np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / (jxx + jyy + 1e-9))
        groove_dir = (np.rad2deg(theta) + 90) % 180        # direction the grooves run along (image coords, y down)
        hexes.append(dict(i=i, j=j, cx=cx, cy=cy, cov=float(cov), hp_sd=sd, coh=coh, groove_dir=float(groove_dir),
                          mean=[float(v) for v in im[m].mean(0)]))
print(len(hexes), "hexes")
for h in hexes:
    print("i%2d j%2d  cov %.2f  hp_sd %5.2f  coh %.2f  dir %6.1f  RGB %s" % (
        h["i"], h["j"], h["cov"], h["hp_sd"], h["coh"], h["groove_dir"], np.round(h["mean"]).astype(int)))
json.dump(hexes, open(guard(RUN + "/work/render_hexes.json"), "w"), indent=1)

# labelled overview
th = Image.open(RENDER).convert("RGB")
d = ImageDraw.Draw(th)
try:
    f = ImageFont.truetype("arial.ttf", 44)
except Exception:
    f = ImageFont.load_default()
for k, h in enumerate(hexes):
    d.text((h["cx"] - 60, h["cy"] - 30), "%d\n%.1f/%.2f" % (k, h["hp_sd"], h["coh"]), fill=(200, 0, 0), font=f)
s = 800 / max(th.size)
save_img(th.resize((round(th.width * s), round(th.height * s)), Image.LANCZOS), RUN + "/work/render_hex_labels.png")
