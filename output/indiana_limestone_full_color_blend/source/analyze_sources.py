"""Measure the two supplied Indiana Limestone Full Color Blend colour maps.

Splits each map into a buff/gray zone field, a mid-band mottle layer and a fine
grain residual, and writes the numbers the builder needs to analysis.json.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
REFS = [ROOT / "references/01_supplied_colormap_A_47x94.webp",
        ROOT / "references/02_supplied_colormap_B_47x94.webp"]
PHYS_IN = (47.0, 94.0)

SIG_GRAIN = 3.0    # px: below this is grain
SIG_ZONE = 40.0    # px: above this is the buff/gray zone field


def load(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(np.float64) / 255.0


def blur(a, s):
    return ndi.gaussian_filter(a, (s, s, 0) if a.ndim == 3 else s, mode="reflect")


def main():
    out = {"sources": []}
    buff_px, gray_px, grain_all, mid_buff, mid_gray = [], [], [], [], []
    for p in REFS:
        a = load(p)
        h, w, _ = a.shape
        low = blur(a, SIG_ZONE)
        chroma = low[..., 0] - low[..., 2]
        # Otsu-like split on chroma
        v = chroma.ravel()
        best, thr = -1, v.mean()
        for t in np.linspace(np.percentile(v, 5), np.percentile(v, 95), 200):
            m = v > t
            if m.all() or (~m).all():
                continue
            s = m.mean() * (1 - m.mean()) * (v[m].mean() - v[~m].mean()) ** 2
            if s > best:
                best, thr = s, t
        buff = chroma > thr
        core_b = ndi.binary_erosion(buff, iterations=60)
        core_g = ndi.binary_erosion(~buff, iterations=60)
        g3 = blur(a, SIG_GRAIN)
        grain = a - g3
        mid = g3 - low
        buff_px.append(low[core_b]); gray_px.append(low[core_g])
        grain_all.append(grain.reshape(-1, 3))
        mid_buff.append(mid[core_b]); mid_gray.append(mid[core_g])
        out["sources"].append({
            "file": p.name, "px": [w, h], "px_per_in": w / PHYS_IN[0],
            "chroma_threshold": float(thr), "buff_fraction": float(buff.mean()),
            "buff_core_px": int(core_b.sum()), "gray_core_px": int(core_g.sum()),
            "mean_rgb": a.reshape(-1, 3).mean(0).tolist(),
        })
        Image.fromarray((buff * 255).astype(np.uint8)).resize((250, 500)).save(
            ROOT / f"source/_zone_mask_{p.stem}.png")
    bp = np.concatenate(buff_px); gp = np.concatenate(gray_px)
    gr = np.concatenate(grain_all)
    mb = np.concatenate(mid_buff); mg = np.concatenate(mid_gray)
    # principal colour direction of the buff mottle
    cov = np.cov(mb.T); evals, evecs = np.linalg.eigh(cov)
    out.update({
        "buff_rgb_mean": bp.mean(0).tolist(), "buff_rgb_std": bp.std(0).tolist(),
        "gray_rgb_mean": gp.mean(0).tolist(), "gray_rgb_std": gp.std(0).tolist(),
        "grain_rgb_std": gr.std(0).tolist(),
        "mid_buff_std": mb.std(0).tolist(), "mid_gray_std": mg.std(0).tolist(),
        "mid_buff_pc1": evecs[:, -1].tolist(), "mid_buff_pc_var": evals[::-1].tolist(),
        "overall_buff_fraction": float(np.mean([s["buff_fraction"] for s in out["sources"]])),
    })
    (ROOT / "source/analysis.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
