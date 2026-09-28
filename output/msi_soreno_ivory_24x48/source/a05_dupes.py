"""Are the candidate tile faces independent photographs/prints, or the same face re-used?

Every face (full or partial, >= 30 % of a tile) from _work/grid.json is cut 5 px inside its joints,
rescaled to a common 533 px tile pitch, converted to luminance and high-passed (sigma 4 px).
For each pair, a central template from the smaller face is slid over the other face (normalised
cross-correlation, every translation), at 0/180 deg and with horizontal/vertical flips; 90/270 deg
are tested with a square template. max NCC >= 0.5 means the same printed face.
Writes _work/faces/<id>.png (colour face crops at native pixels) and _work/dupes.json.
"""
import itertools
import json

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom
from scipy.signal import fftconvolve

from guard import out_path, ref

COMMON_PITCH = 533.0
INSET = 5
SAME = 0.5


def ncc_max(img, tpl):
    """Max normalised cross-correlation of tpl over img (valid positions)."""
    th, tw = tpl.shape
    if img.shape[0] < th or img.shape[1] < tw:
        return -1.0
    t = tpl - tpl.mean()
    tn = np.sqrt((t * t).sum())
    num = fftconvolve(img, t[::-1, ::-1], mode="valid")
    ones = np.ones_like(t)
    s1 = fftconvolve(img, ones, mode="valid")
    s2 = fftconvolve(img * img, ones, mode="valid")
    var = np.maximum(s2 - s1 * s1 / t.size, 1e-9)
    return float((num / (np.sqrt(var) * tn)).max())


def main():
    grid = json.load(open(out_path("_work/grid.json")))
    faces = []
    for gi, g in enumerate(grid):
        rgb = np.asarray(Image.open(ref(g["image"])).convert("RGB")).astype(np.float64)
        s = COMMON_PITCH / g["pitch_px"][0]
        for fi, f in enumerate(g["faces"]):
            if f["frac_w"] < 0.3 or f["frac_h"] < 0.8:
                continue
            x0, y0, x1, y1 = f["box"]
            a, b = int(np.ceil(y0)) + INSET, int(np.floor(y1)) - INSET
            c, d = int(np.ceil(x0)) + INSET, int(np.floor(x1)) - INSET
            if y0 < 1:
                a = 0
            if x0 < 1:
                c = 0
            if y1 > rgb.shape[0] - 1:
                b = rgb.shape[0]
            if x1 > rgb.shape[1] - 1:
                d = rgb.shape[1]
            crop = rgb[a:b, c:d]
            fid = "g%d_f%d" % (gi, fi)
            Image.fromarray(np.clip(crop, 0, 255).astype(np.uint8)).save(out_path("_work/faces/%s.png" % fid))
            L = crop @ np.array([0.2126, 0.7152, 0.0722])
            L = zoom(L, s, order=1)
            hp = L - gaussian_filter(L, 4)
            faces.append({"id": fid, "image": g["image"], "box": f["box"], "frac_w": f["frac_w"],
                          "frac_h": f["frac_h"], "native_px": [int(d - c), int(b - a)], "hp": hp})
    res = []
    for A, B in itertools.combinations(faces, 2):
        small, big = (A, B) if A["hp"].size <= B["hp"].size else (B, A)
        h, w = small["hp"].shape
        th, tw = int(h * 0.7), int(min(w * 0.7, 1.4 * h))
        y, x = (h - th) // 2, (w - tw) // 2
        tpl = small["hp"][y:y + th, x:x + tw]
        best = {}
        for name, t in (("r0", tpl), ("r180", tpl[::-1, ::-1]), ("flipH", tpl[:, ::-1]), ("flipV", tpl[::-1])):
            best[name] = ncc_max(big["hp"], t)
        q = min(th, tw, big["hp"].shape[0] - 2, big["hp"].shape[1] - 2)
        sq = small["hp"][(h - q) // 2:(h - q) // 2 + q, (w - q) // 2:(w - q) // 2 + q]
        best["r90"] = ncc_max(big["hp"], np.rot90(sq, 1))
        best["r270"] = ncc_max(big["hp"], np.rot90(sq, 3))
        k = max(best, key=best.get)
        res.append({"a": A["id"], "b": B["id"], "max_ncc": best[k], "orient": k,
                    "all": {kk: round(v, 3) for kk, v in best.items()}})
    # clusters of identical faces (union-find on max_ncc >= SAME)
    parent = {f["id"]: f["id"] for f in faces}

    def find(u):
        while parent[u] != u:
            u = parent[u]
        return u
    for r in res:
        if r["max_ncc"] >= SAME:
            parent[find(r["a"])] = find(r["b"])
    clusters = {}
    for f in faces:
        clusters.setdefault(find(f["id"]), []).append(f["id"])
    out = {"threshold": SAME,
           "faces": [{k: v for k, v in f.items() if k != "hp"} for f in faces],
           "pairs": sorted(res, key=lambda r: -r["max_ncc"]),
           "clusters": list(clusters.values())}
    json.dump(out, open(out_path("_work/dupes.json"), "w"), indent=1)
    for f in out["faces"]:
        print(f["id"], f["image"][:45], "native", f["native_px"], "frac %.2f x %.2f" % (f["frac_w"], f["frac_h"]))
    print("pairs >= 0.3:")
    for r in out["pairs"]:
        if r["max_ncc"] >= 0.3:
            print("  %s %s %.3f %s" % (r["a"], r["b"], r["max_ncc"], r["orient"]))
    nd = [r["max_ncc"] for r in out["pairs"] if r["max_ncc"] < SAME]
    print("max NCC among distinct pairs: %.3f" % max(nd))
    print("clusters (%d):" % len(clusters))
    for c in clusters.values():
        print("  ", c)


if __name__ == "__main__":
    main()
