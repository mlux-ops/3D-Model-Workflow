"""Viewing aid: colour (unstretched) and grazing crops of the top repeat-search pairs, 2x zoom, <= 800 px wide."""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import guard
import render_grid as rg

TEX = guard.RUN + "/textures/"
color = np.asarray(Image.open(TEX + "Color.png").convert("RGB"))
graz = np.asarray(Image.open(rg.WORK + "grazing_full.png").convert("RGB"))
Ha, Wa = color.shape[:2]
rs = json.load(open(rg.WORK + "repeat_search.json"))
top = sorted(rs["patches"], key=lambda r: -r["max_ncc"])[:8]
S = 128
PAD = 32


def win(a, y, x):
    return a[np.ix_(np.arange(y - PAD, y + S + PAD) % Ha, np.arange(x - PAD, x + S + PAD) % Wa)]


def dihedral(p, t):
    q = np.rot90(p, t & 3, axes=(0, 1))
    return q[:, ::-1] if t & 4 else q


sel = [int(v) for v in sys.argv[1:]] or [0, 1, 4, 5]
rows = []
for n in sel:
    r = top[n]
    y0, x0 = (2 * v for v in r["start_half_res"])
    my, mx = (2 * v for v in r["match"]["at_start_px_half_res"])
    t = r["match"]["transform"]
    a = dihedral(win(color, y0, x0), t)
    b = win(color, my, mx)
    ga = dihedral(win(graz, y0, x0), t)
    gb = win(graz, my, mx)
    row = np.concatenate([a, b, ga, gb], axis=1)
    rows.append(row)
    print(n, "face", r["face"], "->", r["match"]["matched_face"], r["match"]["matched_type"], "t", t, "ncc %.3f" % r["max_ncc"])
img = np.concatenate(rows, axis=0)
im = Image.fromarray(img)
im = im.resize((min(800, im.size[0] * 1), int(im.size[1] * min(800, im.size[0]) / im.size[0])), Image.LANCZOS)
guard.save_image(im, rg.WORK + "thumbs/v_pairs.png")
print(im.size)
