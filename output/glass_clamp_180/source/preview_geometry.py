# -*- coding: utf-8 -*-
"""Offline preview of the analytic clamp model (CPython 3 + Pillow). NOT a Revit render.

Draws the front elevation, plan and side elevation of SHB_Glass Clamp 180 Square from
clamp_geometry.py - the same numbers the builder targets and the verifier re-derives - so the
proportions can be judged before the native run. Two glass thicknesses are drawn in plan.

    python preview_geometry.py       -> ../preview/PREVIEW_geometry_offline.png
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import clamp_geometry as G  # noqa: E402

OUT = os.path.normpath(os.path.join(HERE, '..', 'preview', 'PREVIEW_geometry_offline.png'))
S = 110.0                                   # pixels per inch
BRONZE, BRONZE_DK, CAP = (156, 122, 88), (70, 52, 36), (188, 150, 108)
GLASS, GLASS_LN, BG, INK = (206, 226, 234), (110, 150, 168), (250, 249, 246), (40, 40, 40)


def font(size):
    for name in ('DejaVuSans.ttf', 'arial.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def panel(draw, box, title, note):
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline=(200, 196, 188), width=2)
    draw.text((x0 + 12, y0 + 8), title, fill=INK, font=font(20))
    draw.text((x0 + 12, y1 - 30), note, fill=(110, 106, 98), font=font(14))


def to_px(cx, cy, x, y, flip_y=True):
    return cx + x * S, cy - y * S if flip_y else cy + y * S


def rect(draw, cx, cy, xr, yr, fill, outline, width=2):
    a = to_px(cx, cy, xr[0], yr[1])
    b = to_px(cx, cy, xr[1], yr[0])
    draw.rectangle([a[0], a[1], b[0], b[1]], fill=fill, outline=outline, width=width)


def main():
    st = G.state()
    solids = G.solids(st)
    w2, h2 = st['Clamp_Width'] / 2.0, st['Clamp_Height'] / 2.0
    img = Image.new('RGB', (1720, 900), BG)
    d = ImageDraw.Draw(img)
    d.text((24, 14), 'SHB_Glass Clamp 180 Square - offline analytic preview (not a Revit render). 1/2 in glass, defaults.',
           fill=INK, font=font(22))

    # ---- front elevation (X right, Z up), viewed from +Y, the task's front
    box = (20, 60, 680, 880)
    panel(d, box, 'Front elevation (from +Y)', 'plate 5 x 2 in; 2 caps visible; back plate and caps hidden')
    cx, cy = 350, 470
    for sx in (-1, 1):
        rect(d, cx, cy, (0.0625 * sx, 2.9 * sx) if sx > 0 else (2.9 * sx, 0.0625 * sx), (-1.3, 1.3), GLASS, GLASS_LN)
    rect(d, cx, cy, (-w2, w2), (-h2, h2), BRONZE, BRONZE_DK, 3)
    for key in ('cap_front_left', 'cap_front_right'):
        s = solids[key]
        x, r = s['cx'], (s['x'][1] - s['x'][0]) / 2.0
        a, b = to_px(cx, cy, x - r, r), to_px(cx, cy, x + r, -r)
        d.ellipse([a[0], a[1], b[0], b[1]], fill=CAP, outline=BRONZE_DK, width=3)
    d.line([cx, cy - 1.45 * S, cx, cy + 1.45 * S], fill=(200, 60, 60), width=1)
    d.text((cx + 6, cy - 1.42 * S), 'Joint CL', fill=(200, 60, 60), font=font(14))
    d.line(to_px(cx, cy, -w2, -1.2) + to_px(cx, cy, w2, -1.2), fill=INK, width=2)
    d.text((cx - 22, cy + 1.22 * S), '5.000', fill=INK, font=font(16))
    d.line(to_px(cx, cy, w2 + 0.35, -h2) + to_px(cx, cy, w2 + 0.35, h2), fill=INK, width=2)
    d.text((cx + (w2 + 0.42) * S, cy - 10), '2.000', fill=INK, font=font(16))
    d.text((cx - 1.5 * S - 30, cy + 0.55 * S), 'spacing 3.000', fill=INK, font=font(14))
    d.text((cx + 1.3 * S, cy - 0.58 * S), 'cap D 0.750', fill=INK, font=font(14))

    # ---- plan (X right, +Y up = toward the room), both glass thicknesses
    box = (700, 60, 1360, 470)
    panel(d, box, 'Plan (from above): 1/2 in glass, then 3/8 in glass', 'front plate + caps toward +Y, mirrored at -Y')
    for row, (name, glass) in enumerate(G.TYPES):
        s2 = G.solids(G.state(glass=glass))
        cx, cy = 1030, 185 + row * 155
        g2 = glass / 2.0
        for sx in (-1, 1):
            rect(d, cx, cy, (0.0625 * sx, 2.9 * sx) if sx > 0 else (2.9 * sx, 0.0625 * sx), (-g2, g2), GLASS, GLASS_LN)
        for key, sol in s2.items():
            fill = BRONZE if sol['kind'] == 'plate' else CAP
            rect(d, cx, cy, sol['x'], sol['y'], fill, BRONZE_DK)
        d.text((box[0] + 14, cy + 0.62 * S), '%s (%.3f in glass), overall Y %.3f in' % (
            name, glass, G.overall_extents(G.state(glass=glass))[1]), fill=INK, font=font(14))

    # ---- side elevation (Y right, Z up), viewed from +X
    box = (1380, 60, 1700, 470)
    panel(d, box, 'Side (from +X)', 'plates 1/8 in, caps 1/8 in')
    cx, cy = 1540, 270
    g2 = st['Glass_Thickness'] / 2.0
    rect(d, cx, cy, (-g2, g2), (-1.3, 1.3), GLASS, GLASS_LN)
    for key in ('plate_front', 'plate_back'):
        rect(d, cx, cy, solids[key]['y'], solids[key]['z'], BRONZE, BRONZE_DK)
    for key in ('cap_front_right', 'cap_back_right'):
        rect(d, cx, cy, solids[key]['y'], solids[key]['z'], CAP, BRONZE_DK)

    # ---- legend / numbers
    box = (700, 490, 1700, 880)
    panel(d, box, 'Numbers the builder targets and the verifier re-derives', 'ASSUMED values are not manufacturer data')
    lines = ['VERIFIED (task file / CRL): height 2 in, width 5 in, glass 3/8-1/2 in, finish Brushed Bronze',
             'ASSUMED: plate 1/8 in, joint gap 1/8 in, cap D 3/4 in, cap H 1/8 in, 2 caps per side',
             'Front = +Y (toward the room). Origin: centre of the joint gap at mid-height.',
             '', 'Solid                 X range          Y range          Z range     volume in^3']
    for key in ('plate_front', 'plate_back', 'cap_front_left', 'cap_front_right', 'cap_back_left', 'cap_back_right'):
        s = solids[key]
        lines.append('%-20s %6.3f..%6.3f  %6.3f..%6.3f  %6.3f..%6.3f  %7.4f' % (
            key, s['x'][0], s['x'][1], s['y'][0], s['y'][1], s['z'][0], s['z'][1], s['volume']))
    ex = G.overall_extents(st)
    lines += ['', 'Overall extents: X %.3f  Y %.3f  Z %.3f in' % ex]
    mono = ImageFont.load_default()
    for name in ('DejaVuSansMono.ttf', 'cour.ttf'):
        try:
            mono = ImageFont.truetype(name, 15)
            break
        except OSError:
            pass
    for i, line in enumerate(lines):
        d.text((720, 540 + i * 24), line, fill=INK, font=mono)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print(OUT)


if __name__ == '__main__':
    main()
