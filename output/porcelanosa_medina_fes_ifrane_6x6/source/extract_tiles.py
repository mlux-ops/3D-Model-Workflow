"""Extract per-tile colour samples for Medina Fes and Medina Ifrane from the manufacturer's
near-frontal wall images (see ../SOURCE_SELECTION.md).

Per tile: robust mean colour (linear RGB, specular highlights excluded) and the tile's own
low-frequency glaze clouding (32 x 32 field of colour relative to the tile mean, highlights
masked and filled). White balance per image from a white object in the same scene (the basin).

Writes source/tile_samples.npz, source/tile_samples.json and review contact sheets.
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(RUN_DIR, "references")
FIELD = 32
INSET = 0.16          # fraction of the tile trimmed each side (irregular edges, grout bleed)
FIELD_CLAMP = 0.12    # clouding limited to +-12 % of the tile colour

# Grid boundaries measured with grout-line detection (see SOURCE_SELECTION.md), full-image px.
# Each source lists one or more grids; "neutral" is a white object in the same image used for
# white balance (grout is NOT used: in these renders it carries tile colour and shadow).
SOURCES = {
    "fes": {
        "file": os.path.join(REF, "catalog_imgs", "p11_0.png"),     # catalog: "Wall Covering: Medina Fes"
        "neutral": (870, 960, 600, 720),                             # white basin, y0 y1 x0 x1
        "grids": [{
            "xs": [117, 241, 368, 490, 614, 738, 862, 986, 1110, 1234],
            "ys": [75, 199, 323, 447, 571, 695, 819, 944, 1068, 1192],
            # right of the mirror all rows; above the mirror row 0 only
            "use": lambda c, r: (c >= 5) or (r == 0),
        }],
    },
    "ifrane": {
        "file": os.path.join(REF, "catalog_imgs", "p8_0.png"),      # catalog: only pink colourway = Ifrane
        "neutral": (820, 870, 960, 1180),                            # white basin
        "grids": [
            {"xs": [773, 859, 952, 1036, 1130, 1215],                # wall under the counter
             "ys": [1043, 1129, 1222, 1307, 1396],
             "use": lambda c, r: True},
            {"xs": [707, 805, 905, 1005, 1105, 1205],                # counter apron (same plane)
             "ys": [890, 988],
             "use": lambda c, r: True},
        ],
    },
}
REJECT_FILE = os.path.join(RUN_DIR, "source", "rejected_tiles.json")


def out_path(*parts):
    p = os.path.abspath(os.path.join(RUN_DIR, *parts))
    if not p.startswith(RUN_DIR + os.sep):
        raise RuntimeError("write outside run dir refused: " + p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def srgb_to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def main():
    rejected = {}
    if os.path.exists(REJECT_FILE):
        with open(REJECT_FILE, encoding="utf-8") as f:
            rejected = json.load(f)
    report = {}
    arrays = {}
    for name, s in SOURCES.items():
        img = np.asarray(Image.open(s["file"]).convert("RGB")).astype(np.float64) / 255.0
        y0n, y1n, x0n, x1n = s["neutral"]
        g = np.median(img[y0n:y1n, x0n:x1n].reshape(-1, 3), axis=0)
        g_lin = srgb_to_lin(g)
        wb = g_lin.mean() / g_lin                      # neutralise the white object, keep luminance
        lin = srgb_to_lin(img) * wb
        colours, fields, ids, spec_frac = [], [], [], []
        thumbs = []
        for gi, grid in enumerate(s["grids"]):
          for ci in range(len(grid["xs"]) - 1):
            for ri in range(len(grid["ys"]) - 1):
                if not grid["use"](ci, ri):
                    continue
                tid = f"{name}_g{gi}c{ci}r{ri}"
                if tid in rejected.get(name, []):
                    continue
                x0, x1 = grid["xs"][ci], grid["xs"][ci + 1]
                y0, y1 = grid["ys"][ri], grid["ys"][ri + 1]
                dx, dy = int((x1 - x0) * INSET), int((y1 - y0) * INSET)
                t = lin[y0 + dy:y1 - dy, x0 + dx:x1 - dx]
                lum = t.mean(2)
                p10, p15, p45, p50, p60, p90 = np.percentile(lum, [10, 15, 45, 50, 60, 90])
                # Gloss reflections only ADD light, so the body colour is the darker part of the
                # tile. Take the 15-45th luminance percentile band: above pinholes/specks, below
                # reflected sky. Applied identically to every tile of both colourways.
                band = (lum >= p15) & (lum <= p45)
                col = t[band].mean(axis=0)
                refl = float((p90 - p10) / p50)        # reflection / clouding spread score
                # low-frequency clouding: pixels above p60 treated as possible reflection, filled
                keep = lum <= p60
                spec = ~keep
                w = keep.astype(float)
                num = np.stack([ndimage.gaussian_filter(t[..., k] * w, 4) for k in range(3)], -1)
                den = ndimage.gaussian_filter(w, 4)[..., None]
                filled = np.where(keep[..., None], t, num / np.maximum(den, 1e-6))
                sm = np.stack([ndimage.gaussian_filter(filled[..., k], 3) for k in range(3)], -1)
                rel = sm / col
                rel_r = np.stack([np.asarray(Image.fromarray(rel[..., k].astype(np.float32), "F").resize(
                    (FIELD, FIELD), Image.BILINEAR)) for k in range(3)], -1).astype(np.float64)
                # rev 2: speck / grout-corner outliers were blown up into black blobs in the maps;
                # keep only smooth clouding: median filter, clamp, light blur
                rel_r = np.stack([ndimage.gaussian_filter(ndimage.median_filter(rel_r[..., k], 5, mode="nearest"),
                                                          1.5, mode="nearest") for k in range(3)], -1)
                rel_r = np.clip(rel_r, 1 - FIELD_CLAMP, 1 + FIELD_CLAMP)
                # rev 3: mean exactly 1 per channel, so clouding redistributes colour within the
                # tile but never shifts the tile's measured colour (it brightened/tinted tiles before)
                rel_r = rel_r / rel_r.mean(axis=(0, 1))
                colours.append(col)
                fields.append(rel_r)
                ids.append(tid)
                spec_frac.append(refl)
                thumbs.append((tid, lin_to_srgb(t), col))
        colours = np.array(colours)
        arrays[name + "_colour_lin"] = colours
        arrays[name + "_field"] = np.array(fields)
        arrays[name + "_refl"] = np.array(spec_frac)
        srgb = lin_to_srgb(colours) * 255
        report[name] = {
            "source": os.path.relpath(s["file"], RUN_DIR),
            "neutral_srgb": [round(float(v) * 255, 1) for v in g],
            "white_balance_gain": [round(float(v), 4) for v in wb],
            "tiles": len(ids),
            "ids": ids,
            "colour_srgb": [[round(float(v), 1) for v in c] for c in srgb],
            "reflection_score": [round(v, 3) for v in spec_frac],
            "colour_srgb_min": [round(float(v), 1) for v in srgb.min(0)],
            "colour_srgb_max": [round(float(v), 1) for v in srgb.max(0)],
            "colour_srgb_median": [round(float(v), 1) for v in np.median(srgb, 0)],
        }
        # contact sheet: crop | flat measured colour
        n = len(thumbs)
        cols = 8
        rows = (n + cols - 1) // cols
        cw = 150
        sheet = Image.new("RGB", (cols * cw, rows * (cw + 18)), "white")
        d = ImageDraw.Draw(sheet)
        for i, (tid, crop, col) in enumerate(thumbs):
            x, y = (i % cols) * cw, (i // cols) * (cw + 18)
            c8 = Image.fromarray((crop * 255).astype(np.uint8)).resize((cw - 10, 95))
            sheet.paste(c8, (x + 5, y + 16))
            sw = Image.new("RGB", (cw - 10, 38), tuple(int(v) for v in lin_to_srgb(col) * 255))
            sheet.paste(sw, (x + 5, y + 112))
            d.text((x + 5, y + 2), tid, fill="black")
        sheet.save(out_path("source", f"_REVIEW_tile_samples_{name}.jpg"), quality=90)
    np.savez_compressed(out_path("source", "tile_samples.npz"), **arrays)
    with open(out_path("source", "tile_samples.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=1)
    for k, v in report.items():
        print(k, "tiles", v["tiles"], "neutral", v["neutral_srgb"], "wb", v["white_balance_gain"],
              "min", v["colour_srgb_min"], "med", v["colour_srgb_median"], "max", v["colour_srgb_max"])


if __name__ == "__main__":
    main()
