#!/usr/bin/env python3
"""Generate single-tile textures for the 1529 Wieland bathroom viewer.

Each sheet is a small field of INDIVIDUAL tiles (one tile per cell, straight
stack, half a grout joint on every side so the sheet wraps seamlessly). Every
tile in a sheet is generated separately, so neighbouring tiles differ the way
real pieces do. The vendor photographs are NOT used as the tile image; they
were used once, offline, only to measure each product's body colour (values
recorded below with their source).

Outputs (src/tiles/): <key>.jpg colour, <key>_n.jpg tangent-space normal map,
tiles.json manifest, _preview.png contact sheet for review.

Needs numpy and Pillow.  python -B tools/gen_tile_textures.py
"""
import json
import pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = pathlib.Path(__file__).resolve().parent.parent / "src" / "tiles"
JOINT_IN = 1 / 16          # illustrative joint, same as the viewer used before; not an owner selection
GROUT = np.array([146, 142, 135], np.float32)


def smooth(h, w, cell_y, cell_x, rng):
    """Smooth noise, roughly unit variance, feature size cell_y x cell_x px."""
    gh, gw = max(2, int(round(h / cell_y)) + 2), max(2, int(round(w / cell_x)) + 2)
    a = rng.standard_normal((gh, gw)).astype(np.float32)
    im = Image.fromarray(a, mode="F").resize((w, h), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32)


def fbm(h, w, cell_y, cell_x, rng, octaves=4, gain=0.5):
    out = np.zeros((h, w), np.float32)
    amp, norm = 1.0, 0.0
    for i in range(octaves):
        out += amp * smooth(h, w, max(1.5, cell_y / 2 ** i), max(1.5, cell_x / 2 ** i), rng)
        norm += amp * amp
        amp *= gain
    return out / np.sqrt(norm)


def edge_distance(h, w):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    return np.minimum(np.minimum(x, w - 1 - x), np.minimum(y, h - 1 - y)) + 0.5


# ---------------------------------------------------------------- recipes
# every recipe returns (rgb float HxWx3 0..255, height HxW in inches) for ONE tile

def glazed(h, w, ppi, rng, base, tone_sd, mottle, edge_shift, undulate, streak=0.5):
    """Pressed-edge glossy ceramic with a hand-made look: each piece its own
    tone, soft mottling, glaze drawn slightly along the length, glaze thin at
    the cushioned edge."""
    tone = float(np.clip(rng.normal(0, tone_sd), -2.2 * tone_sd, 2.2 * tone_sd))
    long_y = h >= w
    cy, cx = (h * 0.45, w * 1.1) if long_y else (h * 1.1, w * 0.45)
    m = fbm(h, w, cy, cx, rng, 3) * mottle
    fine = smooth(h, w, 0.5 * ppi if long_y else 0.12 * ppi, 0.12 * ppi if long_y else 0.5 * ppi, rng) * mottle * 0.10 * streak
    d = edge_distance(h, w) / ppi                     # inches from the tile edge
    e = np.exp(-d / 0.07)
    lum = 1 + tone + m + fine
    hue = rng.normal(0, tone_sd * 0.25)
    rgb = np.empty((h, w, 3), np.float32)
    for k in range(3):
        ch = base[k] * lum * (1 + hue * (k - 1))
        rgb[..., k] = ch + edge_shift[k] * e
    height = (1 - np.exp(-d / 0.09)) * 0.035 + fbm(h, w, h * 0.5, w * 0.5, rng, 2) * undulate
    return rgb, height


def concrete(h, w, ppi, rng, base, tone_sd=0.004, cloud=0.012):
    tone = rng.normal(0, tone_sd)
    c = fbm(h, w, 9 * ppi, 9 * ppi, rng, 4) * cloud
    trowel = fbm(h, w, 1.2 * ppi, 5 * ppi, rng, 2) * cloud * 0.35
    grain = rng.standard_normal((h, w)).astype(np.float32) * 0.0035
    lum = 1 + tone + c + trowel + grain
    warm = fbm(h, w, 14 * ppi, 14 * ppi, rng, 2) * 0.004
    rgb = np.stack([base[0] * (lum + warm), base[1] * lum, base[2] * (lum - warm)], -1)
    d = edge_distance(h, w) / ppi
    height = (1 - np.exp(-d / 0.02)) * 0.012 + grain * 0.15
    return rgb, height


def travertine(h, w, ppi, rng, base):
    """Cross-cut travertine look: soft clouds, faint drifting bands along the
    length, small filled pits."""
    long_y = h >= w
    tone = rng.normal(0, 0.006)
    cloud = fbm(h, w, 7 * ppi, 7 * ppi, rng, 4) * 0.018
    band = fbm(h, w, 6 * ppi if long_y else 2.5 * ppi, 2.5 * ppi if long_y else 6 * ppi, rng, 3) * 0.007
    pits_n = smooth(h, w, 0.5 * ppi if long_y else 0.16 * ppi, 0.16 * ppi if long_y else 0.5 * ppi, rng)
    pits = np.clip((pits_n - 1.75) * 2.2, 0, 1)
    grain = rng.standard_normal((h, w)).astype(np.float32) * 0.004
    lum = 1 + tone + cloud + band + grain + pits * 0.035
    warm = fbm(h, w, 10 * ppi, 10 * ppi, rng, 2) * 0.006
    rgb = np.stack([base[0] * (lum + warm), base[1] * lum, base[2] * (lum - warm * 1.4)], -1)
    d = edge_distance(h, w) / ppi
    height = (1 - np.exp(-d / 0.02)) * 0.012 - pits * 0.004
    return rgb, height


def terrazzo(h, w, ppi, rng, base):
    tone = rng.normal(0, 0.004)
    im = Image.new("RGB", (w, h), tuple(int(v * (1 + tone)) for v in base))
    dr = ImageDraw.Draw(im)
    chips = [(232, 228, 224), (224, 219, 214), (199, 193, 187), (205, 197, 188), (190, 184, 178), (214, 206, 198)]
    weights = np.array([0.26, 0.24, 0.18, 0.16, 0.06, 0.10])
    n = int(h * w / (ppi * ppi) * 3.2)
    for _ in range(n):
        size = float(np.clip(rng.lognormal(np.log(0.32), 0.6), 0.08, 1.6)) * ppi
        cx, cy = rng.uniform(0, w), rng.uniform(0, h)
        k = int(rng.integers(5, 8))
        ang = np.sort(rng.uniform(0, 2 * np.pi, k))
        rad = size / 2 * rng.uniform(0.55, 1.0, k)
        asp = rng.uniform(0.55, 1.0)
        rot = rng.uniform(0, np.pi)
        pts = []
        for a, r in zip(ang, rad):
            x, y = r * np.cos(a), r * np.sin(a) * asp
            pts.append((cx + x * np.cos(rot) - y * np.sin(rot), cy + x * np.sin(rot) + y * np.cos(rot)))
        dr.polygon(pts, fill=chips[int(rng.choice(len(chips), p=weights))])
    im = im.filter(ImageFilter.GaussianBlur(0.7))
    rgb = np.asarray(im, np.float32)
    rgb = rgb * (1 + fbm(h, w, 8 * ppi, 8 * ppi, rng, 3)[..., None] * 0.008 + rng.standard_normal((h, w, 1)).astype(np.float32) * 0.004)
    d = edge_distance(h, w) / ppi
    return rgb, (1 - np.exp(-d / 0.02)) * 0.012


def flat(h, w, ppi, rng, base):
    lum = 1 + rng.normal(0, 0.004) + fbm(h, w, 10 * ppi, 10 * ppi, rng, 3) * 0.007 + rng.standard_normal((h, w)).astype(np.float32) * 0.003
    rgb = np.stack([base[k] * lum for k in range(3)], -1)
    d = edge_distance(h, w) / ppi
    return rgb, (1 - np.exp(-d / 0.02)) * 0.012


def ribbed(h, w, ppi, rng, base, groove, bead, pitch_in, mode):
    """Hand-made 3D relief tile. mode 'lines': ribs run along the tile length.
    mode 'edge': ribs follow two edges and meet on the diagonal."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    warp = fbm(h, w, 2.5 * ppi, 2.5 * ppi, rng, 2) * 0.05 * ppi
    if mode == "lines":
        across = (x if h >= w else y) + warp
    else:
        across = np.maximum(x, (h - 1 - y)) + warp      # L-shaped ribs meeting on a diagonal
    phase = 2 * np.pi * across / (pitch_in * ppi)
    rib = 0.5 + 0.5 * np.cos(phase)                      # 1 on the crest
    tone = rng.normal(0, 0.03)
    blot = smooth(h, w, 0.16 * ppi, 0.16 * ppi, rng) + 0.5 * smooth(h, w, 0.6 * ppi, 0.6 * ppi, rng)
    glaze = np.clip((blot - 0.35) * 1.4, 0, 1) * rib ** 2     # glossy glaze pooled on the crests
    lum = (1 + tone + fbm(h, w, 3 * ppi, 3 * ppi, rng, 2) * 0.04)
    rgb = np.empty((h, w, 3), np.float32)
    for k in range(3):
        body = groove[k] + (base[k] - groove[k]) * rib ** 0.8
        rgb[..., k] = (body * (1 - glaze * 0.75) + bead[k] * glaze * 0.75) * lum
    d = edge_distance(h, w) / ppi
    height = (1 - np.exp(-d / 0.06)) * 0.03 + rib * 0.045 + glaze * 0.01
    return rgb, height


# ---------------------------------------------------------------- products
# colour = median tile-body colour measured from the vendor photo embedded in the
# frozen record (grout lines and, for room scenes, everything but the tile
# masked out). finish/edge/size/look are from the vendor product pages, read
# 2026-11-09.
PRODUCTS = [
    dict(key="labelle_antique_blue", match="la belle antique blue", size=[3, 12], grid=[8, 2], ppi=32, glossy=True,
         note="F&D 100507706: ceramic, high gloss, pressed edge, 3x12, 8.5 mm, suggested joint 1/16 in. Colour from the F&D layout photo, grout masked: body about (38,59,70), pieces range (30,50,58)-(45,68,80).",
         recipe=lambda h, w, p, r: glazed(h, w, p, r, (38, 59, 70), 0.09, 0.045, (26, 30, 30), 0.006)),
    dict(key="labelle_purity", match="la belle purity", size=[3, 12], grid=[8, 2], ppi=32, glossy=True,
         note="F&D 100507722: ceramic, high gloss, 3x12. Colour from the F&D layout photo, grout masked: (237,234,228), range (234,229,223)-(240,238,233).",
         recipe=lambda h, w, p, r: glazed(h, w, p, r, (237, 234, 228), 0.010, 0.008, (-9, -10, -12), 0.006)),
    dict(key="elm_tones_sapphire", match="tones sapphire", size=[2, 20], grid=[10, 2], ppi=28, glossy=True,
         note="Elm Surfaces Tones Sapphire: hand-made-look ceramic, glossy, 2x20, 8.5 mm. The only vendor image is a dimly lit restaurant scene; colour taken from its lit band of the tiled wall, about (38,56,84). LEAST CERTAIN colour of the set - check against a sample.",
         recipe=lambda h, w, p, r: glazed(h, w, p, r, (38, 56, 84), 0.09, 0.045, (24, 28, 30), 0.008)),
    dict(key="elm_tones_sandstone", match="tones sandstone", size=[2, 20], grid=[10, 2], ppi=28, glossy=True,
         note="Elm Surfaces Tones Sandstone: hand-made-look ceramic, glossy, 2x20, 8.5 mm. The vendor image is a mixed chevron installation (Sandstone with Sapphire and Copper); colour measured from the beige pieces only: (172,152,138), range (159,138,122)-(185,166,152).",
         recipe=lambda h, w, p, r: glazed(h, w, p, r, (172, 152, 138), 0.05, 0.03, (16, 16, 15), 0.008)),
    dict(key="luxe_sand_24x48", match="luxe sand", size=[24, 48], grid=[2, 2], ppi=16, glossy=False,
         note="F&D Luxe Sand Matte 101317865: porcelain, matte, concrete look, rectified, 24x48 (actual 23.70x47.40), 8 mm, colour listed as Ivory. Colour from the F&D layout photo: (239,237,234).",
         recipe=lambda h, w, p, r: concrete(h, w, p, r, (239, 237, 234))),
    dict(key="luxe_sand_24x24", match="luxe sand", size=[24, 24], grid=[2, 2], ppi=16, glossy=False,
         note="F&D Luxe Sand Matte 101317949: porcelain, matte, concrete look, rectified, 24x24, 8 mm. Same body as the 24x48.",
         recipe=lambda h, w, p, r: concrete(h, w, p, r, (239, 237, 234))),
    dict(key="pienza_terra_24x48", match="pienza terra", size=[24, 48], grid=[2, 2], ppi=16, glossy=False,
         note="F&D Pienza Terra 110850387: porcelain, matte, travertine look, rectified, 24x48 (actual 23.59x47.30), 9 mm, colour listed as Beige. Colour from the F&D layout photo: (198,198,191), range (192,191,183)-(204,204,199).",
         recipe=lambda h, w, p, r: travertine(h, w, p, r, (198, 198, 191))),
    dict(key="pienza_terra_48x24", match="pienza terra", size=[48, 24], grid=[2, 2], ppi=16, glossy=False,
         note="Pienza Terra laid with its long side across (the viewer's floor convention).",
         recipe=lambda h, w, p, r: travertine(h, w, p, r, (198, 198, 191))),
    dict(key="de_rossi_ivory", match="de rossi ivory", size=[24, 24], grid=[2, 2], ppi=16, glossy=False,
         note="F&D De Rossi Ivory 100996800: porcelain, matte, terrazzo look, rectified, 24x24 (actual 23.50), 10.5 mm. Colour from the F&D layout photo: field (213,208,205), chips (206,201,197)-(221,215,213) and lighter.",
         recipe=lambda h, w, p, r: terrazzo(h, w, p, r, (213, 208, 205))),
    dict(key="perimeter_gray", match="perimeter gray", size=[24, 48], grid=[2, 2], ppi=16, glossy=False,
         note="F&D Perimeter Gray Matte 101239218 (historic unselected alternative): 24x48. Colour from the F&D layout photo, grout masked: (107,102,95), nearly uniform.",
         recipe=lambda h, w, p, r: flat(h, w, p, r, (107, 102, 95))),
    dict(key="vera_forma_earth_lines", match="earth lines", size=[2, 10], grid=[12, 3], ppi=36, glossy=True, relief=True,
         note="Elm Surfaces Vera Forma Earth Lines: hand-made 3D ceramic, glossy, 2x10, 8.6 mm. Vendor close-up shows parallel ribs about 0.18 in apart with glossy glaze on the crests: body (133,118,103), grooves (80,66,54), glaze (176,164,150). Ribs are ASSUMED to run along the tile length.",
         recipe=lambda h, w, p, r: ribbed(h, w, p, r, (133, 118, 103), (80, 66, 54), (176, 164, 150), 0.18, "lines")),
    dict(key="vera_forma_indigo_edge", match="indigo edge", size=[6, 6], grid=[4, 4], ppi=32, glossy=True, relief=True,
         note="Elm Surfaces Vera Forma Indigo Edge: hand-made 3D ceramic, glossy, 6x6, 8.6 mm. Vendor photo shows ribs following two edges and meeting on the diagonal: body (113,117,132), grooves (84,88,104). Photographed in direct sun, so the colour may read lighter than a sample.",
         recipe=lambda h, w, p, r: ribbed(h, w, p, r, (113, 117, 132), (84, 88, 104), (150, 154, 170), 0.18, "edge")),
]


def build(prod, seed):
    rng = np.random.default_rng(seed)
    tw, th = prod["size"]
    cols, rows = prod["grid"]
    ppi = prod["ppi"]
    cw, ch = int(round(tw * ppi)), int(round(th * ppi))
    W, H = cw * cols, ch * rows
    colour = np.empty((H, W, 3), np.float32)
    height = np.zeros((H, W), np.float32)
    half = JOINT_IN * ppi / 2                       # half joint each side, in px
    soft = prod.get("glossy") and not prod.get("relief")
    for r in range(rows):
        for c in range(cols):
            rgb, hgt = prod["recipe"](ch, cw, ppi, rng)
            d = edge_distance(ch, cw)
            if prod.get("glossy"):                   # pressed, hand-made edge: slightly irregular outline
                d = d + smooth(ch, cw, 0.9 * ppi, 0.9 * ppi, rng) * 0.012 * ppi
            a = np.clip(d - half + 0.5, 0, 1)[..., None]
            if soft:                                 # eased corners
                yy, xx = np.mgrid[0:ch, 0:cw].astype(np.float32)
                rad = 0.06 * ppi
                dx = np.clip(rad + half - np.minimum(xx, cw - 1 - xx), 0, None)
                dy = np.clip(rad + half - np.minimum(yy, ch - 1 - yy), 0, None)
                a = a * np.clip(rad - np.hypot(dx, dy) + 0.5, 0, 1)[..., None]
            grout = GROUT * (1 + rng.standard_normal((ch, cw, 1)).astype(np.float32) * 0.015)
            ys, xs = slice(r * ch, (r + 1) * ch), slice(c * cw, (c + 1) * cw)
            colour[ys, xs] = rgb * a + grout * (1 - a)
            height[ys, xs] = hgt * a[..., 0] - 0.03 * (1 - a[..., 0])
    colour = np.clip(colour, 0, 255).astype(np.uint8)
    # tangent-space normal map from the height field (inches -> px slope)
    gy, gx = np.gradient(height * ppi)
    strength = 1.0
    nx, ny, nz = -gx * strength, gy * strength, np.ones_like(gx)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    normal = np.stack([nx / ln, ny / ln, nz / ln], -1)
    normal = np.clip((normal * 0.5 + 0.5) * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(colour), Image.fromarray(normal)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest, previews = [], []
    for i, prod in enumerate(PRODUCTS):
        colour, normal = build(prod, 1529 + i * 97)
        colour.save(OUT / (prod["key"] + ".jpg"), quality=84, optimize=True)
        if not prod.get("relief"):
            normal = normal.resize((normal.width // 2, normal.height // 2), Image.LANCZOS)
        normal.save(OUT / (prod["key"] + "_n.jpg"), quality=90, optimize=True)
        manifest.append({k: prod[k] for k in ("key", "match", "size", "grid", "glossy", "note")} | {"relief": bool(prod.get("relief")), "px": [colour.width, colour.height]})
        thumb = colour.copy()
        thumb.thumbnail((420, 420))
        previews.append((prod["key"], thumb))
        print(prod["key"], colour.size, (OUT / (prod["key"] + ".jpg")).stat().st_size, (OUT / (prod["key"] + "_n.jpg")).stat().st_size)
    (OUT / "tiles.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    sheet = Image.new("RGB", (4 * 440, ((len(previews) + 3) // 4) * 440), "white")
    for i, (_, t) in enumerate(previews):
        sheet.paste(t, ((i % 4) * 440 + 10, (i // 4) * 440 + 10))
    sheet.save(OUT / "_preview.png")


if __name__ == "__main__":
    main()
