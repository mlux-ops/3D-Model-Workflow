"""Step 3: per-cell texture statistics in the render + labelled contact sheet.

For every lattice cell with enough visible interior: high-pass energy, structure
tensor coherence and dominant groove orientation. Output feeds the manual/visual
classification that is then written to _work/render_faces.json.
"""
import os
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from guard import inp, save_image, write_text, WORK_DIR

R = np.asarray(Image.open(inp("elm_formed_hex_sand_layout_render.webp")).convert("RGB")).astype(np.float64)
H, W, _ = R.shape
lum = R @ np.array([0.2126, 0.7152, 0.0722])
L = json.load(open(os.path.join(WORK_DIR, "render_lattice.json")))
Rc, half_f = L["Rc"], L["half_f"]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)

hp = lum - ndi.gaussian_filter(lum, 6.0)          # fine relief shading
gx = ndi.sobel(ndi.gaussian_filter(lum, 1.0), axis=1)
gy = ndi.sobel(ndi.gaussian_filter(lum, 1.0), axis=0)


def hex_inside(cx, cy, apothem):
    """flat-top hexagon: |y|<=a, and |x*sin60 + |y|*cos60|... use 3 half-planes."""
    dx, dy = np.abs(xx - cx), np.abs(yy - cy)
    return (dy <= apothem) & (dx * np.sqrt(3) / 2 + dy / 2 <= apothem)


stats = []
for c in L["cells"]:
    cx, cy = c["cx"], c["cy"]
    if cx < -Rc or cx > W + Rc or cy < -half_f or cy > H + half_f:
        continue
    x0, x1 = int(max(0, cx - Rc)), int(min(W, cx + Rc + 1))
    y0, y1 = int(max(0, cy - half_f)), int(min(H, cy + half_f + 1))
    sub = (slice(y0, y1), slice(x0, x1))
    mask = hex_inside(cx, cy, half_f - 10)[sub]
    full_area = 2 * np.sqrt(3) * (half_f - 10) ** 2
    vis = mask.sum() / full_area
    if vis < 0.25:
        continue
    e = hp[sub][mask].std()
    Jxx = (gx[sub][mask] ** 2).mean()
    Jyy = (gy[sub][mask] ** 2).mean()
    Jxy = (gx[sub][mask] * gy[sub][mask]).mean()
    coh = np.sqrt((Jxx - Jyy) ** 2 + 4 * Jxy ** 2) / (Jxx + Jyy + 1e-9)
    # gradient dominant angle; groove direction is perpendicular to it
    gang = 0.5 * np.degrees(np.arctan2(2 * Jxy, Jxx - Jyy))
    groove = (gang + 90) % 180
    # tone of the face: mean colour, low-pass std (cloudiness)
    rgb = R[sub][mask].mean(axis=0)
    lp = ndi.gaussian_filter(lum, 12)[sub][mask]
    stats.append({"j": c["j"], "k": c["k"], "cx": cx, "cy": cy, "vis": round(float(vis), 3),
                  "hp_std": round(float(e), 3), "coherence": round(float(coh), 3),
                  "groove_deg_img": round(float(groove), 1),  # image coords, y down: angle measured from +x toward +y
                  "mean_rgb": [round(float(v), 1) for v in rgb], "lp_std": round(float(lp.std()), 3)})

for s in sorted(stats, key=lambda s: s["hp_std"]):
    print("%3d,%3d vis %.2f hp %.2f coh %.3f groove %6.1f rgb %s lp %.2f" % (
        s["j"], s["k"], s["vis"], s["hp_std"], s["coherence"], s["groove_deg_img"], s["mean_rgb"], s["lp_std"]))
write_text(os.path.join(WORK_DIR, "render_cell_stats.json"), json.dumps(stats, indent=1))

# contact sheet: each cell crop, contrast-stretched high-pass, 150 px per cell
tiles = []
for s in stats:
    cx, cy = s["cx"], s["cy"]
    box = (int(cx - Rc), int(cy - half_f), int(cx + Rc), int(cy + half_f))
    crop = Image.fromarray(np.clip(128 + 6 * hp, 0, 255).astype(np.uint8)).crop(box)
    crop = crop.resize((180, 156), Image.LANCZOS).convert("RGB")
    dd = ImageDraw.Draw(crop)
    dd.text((3, 3), "%d,%d hp%.1f c%.2f g%.0f" % (s["j"], s["k"], s["hp_std"], s["coherence"], s["groove_deg_img"]),
            fill=(255, 0, 0))
    tiles.append(crop)
ncol = 4
nrow = (len(tiles) + ncol - 1) // ncol
sheet = Image.new("RGB", (ncol * 180, nrow * 156), (255, 255, 255))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % ncol) * 180, (i // ncol) * 156))
for part in range((nrow + 4) // 5):
    save_image(sheet.crop((0, part * 5 * 156, ncol * 180, min(nrow, (part + 1) * 5) * 156)),
               os.path.join(WORK_DIR, "render_cells_hp_%d.jpg" % part), quality=90)
print("cells", len(stats), "sheets", (nrow + 4) // 5)
