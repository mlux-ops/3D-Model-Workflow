"""Step 2: fit the render's flat-top hex lattice and export per-face stats + contact sheet.

Horizontal joints were found at y = 157 + k*157.35 (k = 0..10). Here we fit the
column phase from the horizontal joint segments, then enumerate every hexagon
whose interior is fully inside the render and dump crops for classification.
"""
import os
import json
import numpy as np
from PIL import Image, ImageDraw
from guard import inp, save_image, write_text, WORK_DIR

R = np.asarray(Image.open(inp("elm_formed_hex_sand_layout_render.webp")).convert("RGB")).astype(np.float64)
H, W, _ = R.shape
chroma = R[..., 0] - R[..., 2]
m = chroma < 30

# refine the row pitch by least squares on joint-row peaks
rows = m.mean(axis=1)
peaks = []
for k in range(11):
    guess = 157 + k * 157.35
    lo, hi = int(guess - 8), int(guess + 8)
    seg = rows[lo:hi]
    ys = np.arange(lo, hi)
    wgt = np.clip(seg - np.median(rows), 0, None)
    peaks.append((ys * wgt).sum() / wgt.sum())
peaks = np.array(peaks)
A = np.vstack([np.ones(11), np.arange(11)]).T
(y0, half_f), res, _, _ = np.linalg.lstsq(A, peaks, rcond=None)
F = 2 * half_f
print("joint row peaks", np.round(peaks, 2))
print("y0 %.2f  half-F %.3f  F(across flats module) %.3f px" % (y0, half_f, F))
Rc = F / np.sqrt(3.0)          # circumradius of the module hexagon
col_pitch = 1.5 * Rc
print("module circumradius %.3f px, column pitch %.3f px" % (Rc, col_pitch))

# column phase: along a horizontal joint row, joint segments are centred on hex centres
# of the columns whose top/bottom edges lie on that row. Correlate a comb.
best = None
for phase in np.arange(0, 2 * col_pitch, 0.5):
    score = 0.0
    for k in range(11):
        yy = int(round(peaks[k]))
        band = m[yy - 1:yy + 2].mean(axis=0)
        # columns with edges on this row: parity alternates with k
        xs = np.arange(W)
        # centres of columns: phase + j*col_pitch; parity j%2 == k%2 has horizontal edge here
        j = np.round((xs - phase) / col_pitch)
        dx = xs - (phase + j * col_pitch)
        on = (np.abs(dx) < Rc / 2 - 6) & ((j.astype(int) % 2) == (k % 2))
        off = (np.abs(dx) < Rc / 2 - 6) & ((j.astype(int) % 2) != (k % 2))
        score += band[on].mean() - band[off].mean()
    if best is None or score > best[0]:
        best = (score, phase)
x0 = best[1]
print("column phase x0 = %.2f (score %.3f)" % (x0, best[0]))


def centre(j, k2):
    """column j, half-row index k2 (even j -> centres at y0 + (2i+1)*half_f ...)."""
    return x0 + j * col_pitch, k2


cells = []
for j in range(-1, int(W / col_pitch) + 2):
    cx = x0 + j * col_pitch
    # columns whose horizontal edges lie on even k have centres at odd k
    par = j % 2
    for kk in range(-2, 14):
        if (kk % 2) == par:
            continue
        cy = y0 + kk * half_f
        inside = (cx - Rc >= 0) and (cx + Rc <= W - 1) and (cy - half_f >= 0) and (cy + half_f <= H - 1)
        cells.append({"j": j, "k": kk, "cx": cx, "cy": cy, "full": bool(inside)})
full = [c for c in cells if c["full"]]
print("full hexagons inside render:", len(full))

json_out = {"y0": y0, "half_f": half_f, "F": F, "Rc": Rc, "col_pitch": col_pitch, "x0": x0,
            "px_per_in": F / 10.125, "cells": cells}
write_text(os.path.join(WORK_DIR, "render_lattice.json"), json.dumps(json_out, indent=1))

# overlay of lattice on render thumbnail with cell numbers
im = Image.fromarray(R.astype(np.uint8))
d = ImageDraw.Draw(im)
for n, c in enumerate(cells):
    cx, cy = c["cx"], c["cy"]
    pts = [(cx + Rc * np.cos(np.radians(a)), cy + Rc * np.sin(np.radians(a))) for a in range(0, 360, 60)]
    d.polygon(pts, outline=(255, 0, 0))
    d.text((cx - 10, cy - 6), "%d,%d" % (c["j"], c["k"]), fill=(200, 0, 0) if c["full"] else (0, 0, 255))
im.thumbnail((800, 800), Image.LANCZOS)
save_image(im, os.path.join(WORK_DIR, "render_lattice_overlay.jpg"), quality=90)
