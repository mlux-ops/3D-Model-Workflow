# -*- coding: utf-8 -*-
"""Contrast-stretched, gridded crops of the white-finish side/oblique references (image work, outside Revit)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import safe_path
import numpy as np
from PIL import Image, ImageDraw

IN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/'
OUT = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/work/'


def stretched(name, lo, hi, box, scale, grid, tag):
    im = Image.open(IN + name).convert('L')
    a = np.asarray(im).astype(float)
    a = np.clip((a - lo) / (hi - lo), 0, 1) * 255
    im2 = Image.fromarray(a.astype('uint8')).convert('RGB').crop(box)
    im2 = im2.resize((int(im2.width * scale), int(im2.height * scale)), Image.LANCZOS)
    d = ImageDraw.Draw(im2)
    x0, y0, x1, y1 = box
    gx = (x0 // grid + 1) * grid
    while gx < x1:
        X = (gx - x0) * scale
        d.line([(X, 0), (X, im2.height)], fill=(255, 0, 0), width=1)
        d.text((X + 2, 2), str(gx), fill=(255, 0, 0))
        gx += grid
    gy = (y0 // grid + 1) * grid
    while gy < y1:
        Y = (gy - y0) * scale
        d.line([(0, Y), (im2.width, Y)], fill=(0, 0, 255), width=1)
        d.text((2, Y + 2), str(gy), fill=(0, 0, 255))
        gy += grid
    out = OUT + tag + '.png'
    im2.save(safe_path(out))
    print(out, im2.size)


# side view: whole fixture, stretched to show the white body against the white ground
stretched('KW1041_MWT_side_reference.jpg', 200, 255, (450, 450, 2050, 1750), 0.5, 100, 'side_stretched')
stretched('KW1041_MWT_side_reference.jpg', 150, 255, (1000, 900, 1500, 1500), 1.3, 50, 'side_neck_zoom')
