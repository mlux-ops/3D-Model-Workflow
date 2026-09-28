"""Identity test between every candidate vein-cut face (are they the same printed face?).

Every face is brought to 8 px/in with veins horizontal, reduced to luminance, and band-passed (DoG 0.8/4 px)
so large lighting gradients and JPEG noise do not count. From each face, 6 patch templates (10 x 6 in) are
cut; each template is slid over every other face at scales 0.92..1.08 and 4 orientations (r0, r180, flipH,
flipV). Pair score = median over the 6 templates of the best NCC. Same print: score >> the surrogate baseline
(phase-randomised copy of the target, same spectrum). Writes _work/dupes.json.

Faces are defined here (crop boxes in native px, px/in from the layout measurements in a02_measure.py)."""
import json
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom
from scipy.signal import fftconvolve

from guard import out_path, ref

Image.MAX_IMAGE_PIXELS = None
T_PPI = 8.0
B = "E:/Claude/3D-Model-Workflow/"
FACES = {
    # name: (path, crop (x0,y0,x1,y1) or None, rotate k*90 CCW, native px/in)
    "u09": (ref("user_supplied/u09_flat_veincut_swatch.webp"), None, 0, 1890 / 48.0),
    "old05": (B + "output/belmont_tiles/ElmStone_Jute_24x48/references/05_new_flat_veincut.jpg", None, 0, 1890 / 48.0),
    "jute_original": (B + "references/belmont_tiles/jute_original.jpg", None, 0, 1890 / 48.0),
    "w01_elm": (ref("web/w01_elm_jute_veincut_24x48_01.jpg"), None, 0, 1890 / 48.0),
    "w04_ms": (ref("web/w04_ms_ecostone_jute_veincut_24x48_01.jpg"), None, 0, 1890 / 48.0),
    "w05_r0full": (ref("web/w05_ms_ecostone_veincut_jute_24x48_panel.jpg"), (4, 4, 2394, 1194), 0, 49.96),
    "w05_r0half": (ref("web/w05_ms_ecostone_veincut_jute_24x48_panel.jpg"), (2402, 4, 3596, 1194), 0, 49.96),
    "w05_r1half": (ref("web/w05_ms_ecostone_veincut_jute_24x48_panel.jpg"), (4, 1203, 1195, 2396), 0, 49.96),
    "w05_r1full": (ref("web/w05_ms_ecostone_veincut_jute_24x48_panel.jpg"), (1203, 1203, 3596, 2396), 0, 49.96),
    "w14_48x110": (ref("web/w14_ms_jute_veincut_48x110_04.jpg"), None, 1, 2039 / 48.0),
    "w11_12x24": (ref("web/w11_ms_jute_veincut_12x24_03.jpg"), None, 0, 945 / 24.0),
    "primarybath": (B + "references/belmont_tiles/PrimaryBath_Wall_ELM_ElmStone_Jute_Vein-Cut_24x48.jpg", None, 0, 1890 / 48.0),
    "manu03": (B + "output/belmont_tiles/ElmStone_Jute_24x48/references/manufacturer_03_flat_swatch.webp", None, 0, 2000 / 48.0),
    "x06_crosscut": (B + "output/belmont_tiles/ElmStone_Jute_24x48/references/06_new_fluted_crosscut.webp", None, 0, 2000 / 48.0),
}


def load(name):
    p, crop, rot, ppi = FACES[name]
    a = np.asarray(Image.open(p).convert("RGB")).astype(np.float64)
    if crop:
        x0, y0, x1, y1 = crop
        a = a[y0:y1, x0:x1]
    a = np.rot90(a, rot)
    L = a @ np.array([0.2126, 0.7152, 0.0722])
    L = zoom(gaussian_filter(L, 0.5 * ppi / T_PPI), T_PPI / ppi, order=1)
    return gaussian_filter(L, 0.8) - gaussian_filter(L, 4.0)


def ncc_map(img, tpl):
    t = tpl - tpl.mean()
    tn = np.sqrt((t * t).sum())
    num = fftconvolve(img, t[::-1, ::-1], mode="valid")
    o = np.ones_like(t)
    s1 = fftconvolve(img, o, mode="valid")
    s2 = fftconvolve(img * img, o, mode="valid")
    return num / (np.sqrt(np.maximum(s2 - s1 * s1 / t.size, 1e-9)) * tn)


def templates(F):
    h, w = F.shape
    th, tw = int(6 * T_PPI), int(10 * T_PPI)
    out = []
    for fy in (0.25, 0.7):
        for fx in (0.2, 0.5, 0.8):
            y0 = int(fy * h - th / 2)
            x0 = int(fx * w - tw / 2)
            y0, x0 = max(0, min(y0, h - th)), max(0, min(x0, w - tw))
            out.append(F[y0:y0 + th, x0:x0 + tw])
    return out


def surrogate(F, rng):
    f = np.fft.fft2(F)
    ph = np.exp(1j * rng.uniform(0, 2 * np.pi, F.shape))
    return np.real(np.fft.ifft2(np.abs(f) * ph))


def best(target, tpls, scales=(0.92, 0.96, 1.0, 1.04, 1.08)):
    res = []
    for t in tpls:
        b = -1
        for s in scales:
            ts = zoom(t, s, order=1)
            for tt in (ts, ts[::-1, ::-1], ts[:, ::-1], ts[::-1]):
                if target.shape[0] > tt.shape[0] and target.shape[1] > tt.shape[1]:
                    b = max(b, float(ncc_map(target, tt).max()))
        res.append(b)
    return float(np.median(res)), res


def main():
    names = sys.argv[1:] or list(FACES)
    F = {n: load(n) for n in names}
    rng = np.random.default_rng(7)
    out = {"t_ppi": T_PPI, "pairs": {}, "shape_8ppi": {n: list(F[n].shape) for n in names}}
    for a in names:
        tp = templates(F[a])
        for b in names:
            if a == b:
                continue
            s, per = best(F[b], tp)
            out["pairs"]["%s->%s" % (a, b)] = {"score": s, "per_template": per}
        sur = surrogate(F[names[0] if a != names[0] else names[1]], rng)
        out["pairs"]["%s->surrogate" % a] = {"score": best(sur, tp)[0]}
        print(a, "done", flush=True)
    json.dump(out, open(out_path("_work/dupes%s.json" % ("_" + "_".join(sys.argv[1:]) if sys.argv[1:] else "")), "w"), indent=1)
    print("%-12s" % "", " ".join("%8s" % n[:8] for n in names))
    for a in names:
        row = []
        for b in names:
            row.append("   -    " if a == b else "%8.3f" % out["pairs"]["%s->%s" % (a, b)]["score"])
        print("%-12s" % a[:12], " ".join(row), " sur %.3f" % out["pairs"]["%s->surrogate" % a]["score"])


if __name__ == "__main__":
    main()
