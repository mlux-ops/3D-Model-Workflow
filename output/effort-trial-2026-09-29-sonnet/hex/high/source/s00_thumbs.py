from common import *

for name, path in (("render", RENDER), ("life", LIFESTYLE)):
    im = Image.open(path).convert("RGB")
    print(name, im.size)
    s = 800 / max(im.size)
    t = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    save_img(t, RUN + "/work/thumb_%s.png" % name)
