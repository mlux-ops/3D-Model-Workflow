"""Independent check of the delivered Medina PNGs. Decodes 16-bit PNGs from bytes (Pillow reduces
RGB16 to 8-bit), re-derives sizes, depths, normal sign, wrap, registration of the three colour
maps (grout in the same place) and the per-colourway colour statistics. Exits non-zero on failure."""
import json
import os
import struct
import sys
import zlib

import numpy as np
from PIL import Image

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(RUN_DIR, "textures")
COLOURS = ["Medina_Fes_Color.png", "Medina_Ifrane_Color.png", "Medina_Fes_Ifrane_Mix_Color.png"]


def read_png16(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, hdr = 8, b"", None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if tag == b"IHDR":
            hdr = struct.unpack(">IIBBBBB", body)
        elif tag == b"IDAT":
            idat += body
        pos += 12 + ln
    w, h, depth, ctype = hdr[:4]
    assert depth == 16, depth
    ch = {0: 1, 2: 3}[ctype]
    rows = np.frombuffer(zlib.decompress(idat), np.uint8).reshape(h, w * ch * 2 + 1)
    assert np.all(rows[:, 0] == 0), "unexpected PNG row filter"
    a = rows[:, 1:].copy().view(">u2").reshape(h, w, ch).astype(np.float64) / 65535.0
    return (a[..., 0] if ch == 1 else a), (w, h, depth, ctype)


def main():
    rep = json.load(open(os.path.join(RUN_DIR, "source", "build_report.json"), encoding="utf-8"))
    mod = int(round(rep["module_mm"] * rep["px_per_mm"]))
    out, g = {}, {}
    nrm, hn = read_png16(os.path.join(TEX, "Medina_Normal16_OpenGL.png"))
    bump, hb = read_png16(os.path.join(TEX, "Medina_Bump16.png"))
    cols = [np.asarray(Image.open(os.path.join(TEX, f)).convert("RGB")).astype(np.float64) for f in COLOURS]
    out["headers"] = {"normal": hn, "bump": hb}
    W = hn[0]
    g["sizes_equal"] = hn[:2] == hb[:2] and all(c.shape[:2] == (hn[1], hn[0]) for c in cols)
    g["size_is_whole_modules"] = W % mod == 0 and W // mod == rep["tiles"][0]
    n = nrm * 2 - 1
    g["normal_unit_length"] = bool(np.abs(np.sqrt((n ** 2).sum(-1)) - 1).max() < 2e-3)
    # sign: at the left edge of a tile face the surface rises to the right -> red below mid
    x_face = mod + int(1.0 * rep["px_per_mm"]) + 2      # just inside the face past the half joint
    r_east = float(nrm[mod // 4:3 * mod // 4, x_face:x_face + 3, 0].mean())
    x_w = 2 * mod - int(1.0 * rep["px_per_mm"]) - 5
    r_west = float(nrm[mod // 4:3 * mod // 4, x_w:x_w + 3, 0].mean())
    y_face = mod + int(1.0 * rep["px_per_mm"]) + 2
    g_south = float(nrm[y_face:y_face + 3, mod // 4:3 * mod // 4, 1].mean())
    out["sign"] = {"red_inside_left_edge": r_east, "red_inside_right_edge": r_west, "green_inside_top_edge": g_south}
    g["red_sign"] = r_east < 0.5 < r_west
    g["green_sign_opengl"] = g_south > 0.5
    # registration: grout pixels (low bump) identical positions; grout colour identical in all colour maps
    grout = bump < np.percentile(bump, 2)
    gc = [c[grout].mean(0) for c in cols]
    out["grout_rgb_per_map"] = [x.round(1).tolist() for x in gc]
    g["colour_maps_registered"] = bool(max(np.abs(gc[0] - gc[1]).max(), np.abs(gc[0] - gc[2]).max()) < 3.0)
    for k, a in {"bump": bump, "normal": nrm, **{f: c for f, c in zip(COLOURS, cols)}}.items():
        typ = float(np.abs(np.diff(a, axis=1)).mean())
        wx = float(np.abs(a[:, 0] - a[:, -1]).mean())
        wy = float(np.abs(a[0] - a[-1]).mean())
        out["wrap_" + k] = [typ, wx, wy]
        g["wrap_" + k] = wx <= 2 * typ and wy <= 2 * typ
    # per-tile centre colours (sRGB) of each map, for the README
    N = rep["tiles"][0]
    c_off = mod // 2
    stats = {}
    for f, c in zip(COLOURS, cols):
        cent = np.array([c[r * mod + c_off - 20:r * mod + c_off + 20, q * mod + c_off - 20:q * mod + c_off + 20].reshape(-1, 3).mean(0)
                         for r in range(N) for q in range(N)])
        stats[f] = {"tile_centre_srgb_min": cent.min(0).round(1).tolist(), "median": np.median(cent, 0).round(1).tolist(),
                    "max": cent.max(0).round(1).tolist(), "lum_sd": round(float(cent.mean(1).std()), 2)}
    out["tile_stats"] = stats
    mix = np.array([cols[2][r * mod + c_off, q * mod + c_off] for r in range(N) for q in range(N)])
    fes_c = np.array([cols[0][r * mod + c_off, q * mod + c_off] for r in range(N) for q in range(N)])
    is_fes = np.all(np.abs(mix - fes_c) < 1, axis=1)
    out["mix_fes_tiles"] = int(is_fes.sum())
    g["mix_matches_layout"] = int(is_fes.sum()) == rep["layout"]["mix_fes_count"]
    out["gates"] = g
    out["pass"] = all(g.values())
    with open(os.path.join(RUN_DIR, "source", "map_validation.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"gates": g, "sign": out["sign"], "tile_stats": stats, "mix_fes_tiles": out["mix_fes_tiles"]}, indent=1))
    if not out["pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
