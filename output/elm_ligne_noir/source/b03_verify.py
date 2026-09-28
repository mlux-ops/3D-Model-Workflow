"""Independent verifier: re-derives every gate from the PNG files on disk (not from the builder's
state), writes textures/validation.json, and exits non-zero if any gate fails."""
import json
import struct
import sys

import numpy as np
from PIL import Image

from guard import out_path

Image.MAX_IMAGE_PIXELS = None
PPI = 100
TILE_W, TILE_H, JOINT = 2.75, 9.6875, 0.1875   # drawn length, see b01_build.py
MOD_W, MOD_H = TILE_W + JOINT, TILE_H + JOINT
COLS, ROWS = 12, 4


def ihdr(path):
    b = open(path, "rb").read(33)
    assert b[:8] == b"\x89PNG\r\n\x1a\n" and b[12:16] == b"IHDR"
    w, h, depth, ctype = struct.unpack(">IIBB", b[16:26])
    return {"width": w, "height": h, "bit_depth": depth, "colour_type": ctype}


def main():
    rep = json.load(open(out_path("textures/report.json")))
    full = rep["relief_mm"]["full_scale"]
    gates = {}
    hc, hb = ihdr(out_path("textures/Color.png")), ihdr(out_path("textures/Bump16.png"))
    gates["format"] = {"pass": hc["bit_depth"] == 8 and hc["colour_type"] == 2 and hb["bit_depth"] == 16
                       and hb["colour_type"] == 0 and (hc["width"], hc["height"]) == (hb["width"], hb["height"]),
                       "color": hc, "bump": hb}
    W, H = hc["width"], hc["height"]
    w_in, h_in = COLS * MOD_W, ROWS * MOD_H
    quarter = all(abs(v * 4 - round(v * 4)) < 1e-9 for v in (w_in, h_in))   # Revit shows 1/4 in: must be exact
    gates["aspect"] = {"pass": abs(W - w_in * PPI) <= 0.5 and abs(H - h_in * PPI) <= 0.5 and quarter,
                       "sample_size_exact_quarter_inch": quarter,
                       "px": [W, H], "sample_size_in": [w_in, h_in]}

    c = np.asarray(Image.open(out_path("textures/Color.png"))).astype(np.float64)
    b = np.asarray(Image.open(out_path("textures/Bump16.png"))).astype(np.float64) / 65535 * full
    lum = c.mean(2)

    # joints: bright grout runs; measure widths on 40 scan lines each way
    widths_v, widths_h = [], []
    for y in np.linspace(200, H - 200, 20).astype(int):
        g = lum[y] > 128
        edges = np.flatnonzero(np.diff(g.astype(int)))
        runs = [(edges[i + 1] - edges[i]) for i in range(len(edges) - 1) if g[edges[i] + 1]]
        widths_v += runs
    for x in np.linspace(100, W - 100, 20).astype(int):
        g = lum[:, x] > 128
        edges = np.flatnonzero(np.diff(g.astype(int)))
        runs = [(edges[i + 1] - edges[i]) for i in range(len(edges) - 1) if g[edges[i] + 1]]
        widths_h += runs
    wv, wh = np.array(widths_v), np.array(widths_h)
    gates["joints"] = {"pass": len(wv) == 20 * (COLS - 1) and len(wh) == 20 * (ROWS - 1)
                       and abs(np.median(wv) - JOINT * PPI) <= 1.5 and abs(np.median(wh) - JOINT * PPI) <= 1.5,
                       "interior_vertical_runs": int(len(wv)), "interior_horizontal_runs": int(len(wh)),
                       "median_px": [float(np.median(wv)), float(np.median(wh))], "design_px": JOINT * PPI,
                       "edge_half_joints_px": [int((lum[int(MOD_H * PPI / 2), :40] > 128).sum()),
                                              int((lum[int(MOD_H * PPI / 2), -40:] > 128).sum())]}

    # ribs per tile and clearance, per tile
    ribs, lows, crest, chan = [], [], [], []
    ncc_fields = []
    for r in range(ROWS):
        for k in range(COLS):
            x0 = k * MOD_W + JOINT / 2
            y0 = r * MOD_H + JOINT / 2
            xs = slice(int(np.ceil((x0 + 0.06) * PPI)), int((x0 + TILE_W - 0.06) * PPI))
            ys = slice(int(np.ceil((y0 + 0.06) * PPI)), int((y0 + TILE_H - 0.06) * PPI))
            t = b[ys, xs]
            prof = t[t.shape[0] // 2]
            mid = 0.5 * (prof.max() + prof.min())
            up = np.flatnonzero(np.diff((prof > mid).astype(int)) == 1)
            ribs.append(int(len(up) + (prof[0] > mid)))
            lows.append(float(t.min()))
            crest.append(float(np.percentile(t, 99.5)))
            chan.append(float(np.percentile(t, 2)))
            f = c[ys, xs].mean(2)
            f = f - f.mean(0, keepdims=True)  # remove the designed channel darkening (constant along v)
            ncc_fields.append(f[:900, :250].ravel() / (np.linalg.norm(f[:900, :250]) + 1e-9))
    F = np.array(ncc_fields)
    G = F @ F.T
    np.fill_diagonal(G, 0)
    gates["ribs"] = {"pass": all(n == 10 for n in ribs), "counts_min_max": [min(ribs), max(ribs)]}
    gates["clearance"] = {"pass": min(lows) > 0.5, "lowest_face_mm_min": min(lows),
                          "channel_p2_mm_median": float(np.median(chan)), "crest_p995_mm_median": float(np.median(crest)),
                          "pattern_mm_median": float(np.median(crest) - np.median(chan)), "full_scale_mm": full}
    gates["distinct_faces"] = {"pass": float(np.abs(G).max()) < 0.2, "max_abs_ncc_between_tiles": float(np.abs(G).max())}

    # wrap: step across the image edge vs the same step between two interior columns / rows
    def step(a, axis):
        e = np.abs(np.take(a, 0, axis) - np.take(a, -1, axis)).mean()
        i = [np.abs(np.take(a, j, axis) - np.take(a, j + 1, axis)).mean() for j in (500, 1000, 1500, 2000)]
        return float(e), [float(v) for v in i]
    ce_x, ci_x = step(lum, 1)
    ce_y, ci_y = step(lum, 0)
    be_x, bi_x = step(b, 1)
    be_y, bi_y = step(b, 0)
    gates["wrap"] = {"pass": ce_x <= 2 * max(ci_x) and ce_y <= 2 * max(ci_y) and be_x <= 2 * max(bi_x) + 1e-6
                     and be_y <= 2 * max(bi_y) + 1e-6,
                     "colour_lr": [ce_x, ci_x], "colour_tb": [ce_y, ci_y], "bump_lr_mm": [be_x, bi_x], "bump_tb_mm": [be_y, bi_y]}

    # colour stripe at the rib period: face luminance folded by rib phase, one inner tile
    x0 = 5 * MOD_W + JOINT / 2
    xs = np.arange(int(np.ceil((x0 + 0.06) * PPI)), int((x0 + TILE_W - 0.06) * PPI))
    u = (xs + 0.5) / PPI - x0
    ph = ((u / (TILE_W / 10)) % 1 * 16).astype(int)
    colm = c[1200:2000, xs].mean(2).mean(0)
    fold = np.bincount(ph, colm, 16) / np.bincount(ph, None, 16)
    gates["colour_stripe"] = {"pass": fold.max() / fold.min() < 1.10, "peak_to_trough": float(fold.max() / fold.min()),
                              "note": "designed channel darkening is 4 % in linear light (about 2 % in sRGB)"}

    for g in gates.values():
        g["pass"] = bool(g["pass"])  # numpy bools are not JSON serialisable
    ok = all(g["pass"] for g in gates.values())
    out = {"all_pass": ok, "gates": gates}
    json.dump(out, open(out_path("textures/validation.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
