from common import *

im = Image.open(RENDER).convert("RGB")
# 1:1 crops of interest (full-res coordinates), 780 px max
crops = {
    "A_topleft": (0, 0, 780, 780),
    "B_mid": (500, 300, 1280, 1080),
}
for k, box in crops.items():
    save_img(im.crop(box), RUN + "/work/crop_render_%s.png" % k)

a = np.asarray(im).astype(float)
print("mean RGB overall", a.reshape(-1, 3).mean(0))
lf = Image.open(LIFESTYLE).convert("RGB")
save_img(lf.crop((250, 0, 1030, 780)), RUN + "/work/crop_life_A.png")
save_img(lf.crop((300, 700, 1080, 1480)), RUN + "/work/crop_life_B.png")
