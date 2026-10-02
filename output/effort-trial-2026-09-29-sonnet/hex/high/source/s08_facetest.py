import time
from facegen import *

rng = np.random.default_rng(11)
t0 = time.time()
tests = {}
tests["matte"] = gen_matte(rng); print("matte", time.time() - t0)
tests["raw"] = gen_raw(rng); print("raw", time.time() - t0)
tests["chis90"] = gen_chis(rng, 90.0); print("chis", time.time() - t0)
tests["chis30"] = gen_chis(rng, 30.0)


def shade(h, az_deg=200, el_deg=15):
    px_mm = 25.4 / 64.0
    gy, gx = np.gradient(h, px_mm)
    a = np.deg2rad(az_deg); el = np.deg2rad(el_deg)
    l = np.array([np.cos(a) * np.cos(el), np.sin(a) * np.cos(el), np.sin(el)])
    n = np.stack([-gx, -gy, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return np.clip(n @ l, 0, 1)


for k, (col, h) in tests.items():
    print(k, "colour mean", col.reshape(-1, 3).mean(0).round(1), "h std %.3f mm  p1 %.3f p99 %.3f" % (h.std(), *np.percentile(h, [1, 99])))
    lit = shade(h) * 1.0
    img = np.clip(col * (0.35 + 0.9 * lit[..., None]), 0, 255).astype(np.uint8)
    c0 = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).crop((200, 200, 600, 500))
    c1 = Image.fromarray(img).crop((200, 200, 600, 500))
    m = Image.new("RGB", (800, 300))
    m.paste(c0, (0, 0)); m.paste(c1, (400, 0))
    save_img(m, RUN + "/work/facetest_%s.png" % k)
