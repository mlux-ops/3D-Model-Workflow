"""Offline orthographic preview of the clamp as clamp_spec.py defines it (CPython 3 + Pillow).

Draws room-side (+Y) elevation, shower-side (-Y) elevation with the screw heads, and a
plan section through Glass Mid with the two 1/2 in glass panels and the 1/16 in joint.
Scale 100 px/in. Geometry-intent check only; the Revit exports are the real evidence.
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import clamp_spec as S  # noqa: E402

PX = 100.0
OUT = os.path.normpath(os.path.join(HERE, '..', 'preview'))
BRONZE = tuple(S.MATERIAL['color'])
EDGE = (40, 30, 20)
GLASS = (200, 225, 230)


def panel(draw, ox, oy, title):
    draw.text((ox, oy - 22), title, fill=(0, 0, 0))


def main():
    v = S.resolve()
    w, h, d, s = v['Clamp_Width'], v['Clamp_Height'], v['Cap_Diameter'], v['Cap_Offset']
    yb = S.y_bands(v)
    img = Image.new('RGB', (1500, 1000), (255, 255, 255))
    dr = ImageDraw.Draw(img)

    def rect(ox, oy, x0, y0, x1, y1, fill):
        dr.rectangle([ox + x0 * PX, oy - y1 * PX, ox + x1 * PX, oy - y0 * PX], fill=fill, outline=EDGE, width=2)

    # elevations: origin at clamp centre
    for ox, title, screws in ((300, 'Room side (+Y, "Front" per task sheet) - plain', False),
                              (1000, 'Shower side (-Y) - 2 screw heads (24-sided, 1/2 across flats), locked to Screw CL planes', True)):
        oy = 220
        panel(dr, ox - 250, oy - 100 - 10, title)
        rect(ox, oy, -w / 2, -h / 2, w / 2, h / 2, BRONZE)
        dr.line([ox, oy - 130, ox, oy + 130], fill=(200, 0, 0), width=1)       # Joint CL
        if screws:
            for cx in (-s, s):
                pts = [(ox + p[0] * PX, oy - p[2] * PX) for p in S.cap_polygon(cx, 0.0, v)]
                dr.polygon(pts, fill=(140, 112, 84), outline=EDGE)
            for name, x in (('Screw L CL', -s), ('Screw R CL', s)):
                dr.line([ox + x * PX, oy - 130, ox + x * PX, oy + 130], fill=(0, 0, 200), width=1)
        dr.text((ox - 60, oy + 110), '%.3g x %.3g in' % (w, h), fill=(0, 0, 0))
    # plan section at Z = 0 (Glass Mid), plan y up = +Y (room)
    ox, oy = 750, 700
    panel(dr, 150, 480, 'Plan section at Glass Mid: glass 1/2, joint gap 1/16, plates 1/8 (ASSUMED), heads 1/16 proud')
    g, gap = v['Glass_Thickness'], v['Joint_Gap']
    rect(ox, oy, -7.0, -g / 2, -gap / 2, g / 2, GLASS)
    rect(ox, oy, gap / 2, -g / 2, 7.0, g / 2, GLASS)
    rect(ox, oy, -w / 2, yb['plate_front'][0], w / 2, yb['plate_front'][1], BRONZE)
    rect(ox, oy, -w / 2, yb['plate_back'][0], w / 2, yb['plate_back'][1], BRONZE)
    for cx in (-s, s):
        rect(ox, oy, cx - d / 2, yb['cap'][0], cx + d / 2, yb['cap'][1], (140, 112, 84))
        dr.line([ox + cx * PX, oy - 120, ox + cx * PX, oy + 120], fill=(0, 0, 200), width=1)
    dr.line([ox, oy - 150, ox, oy + 150], fill=(200, 0, 0), width=1)
    dr.text((ox + s * PX + 6, oy + 100), 'screw CL %.4g in from joint' % s, fill=(0, 0, 200))
    dr.text((ox + 6, oy - 150), 'Joint CL', fill=(200, 0, 0))
    dr.text((ox - 700, oy - 60), '+Y room side', fill=(0, 0, 0))
    dr.text((ox - 700, oy + 50), '-Y shower side', fill=(0, 0, 0))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, 'analytic_preview.png')
    img.save(path)
    print(path)


if __name__ == '__main__':
    main()
