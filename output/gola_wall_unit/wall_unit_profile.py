# -*- coding: utf-8 -*-
"""Richelieu Gola Wall Unit Profile (ART. 268, 20 x 20 mm) cross-section, shared by builder and verifier.

Drawing frame (mm), as on the manufacturer data sheet 1344403: x_d to the right, y_d up, origin at
the web's outer face / bottom of the 20 mm dimension. The door edge abuts the web at x_d = 0 from
the left; its 3 x 8 mm groove takes the tongue at y_d = 10 (centre of an 18 mm door spanning
y_d 1..19). The flange at y_d = 20 continues the door front 1 mm proud and ends in the 6.5 mm curl.

Measured from the 4x render (20.5 px/mm): overall 20 x 20, curl 6.5, wall ~1.1 mm, tongue ~7 mm with
a ~3 mm barb. Curves (scoop, curl, teardrop hole) are drawing-derived approximations; every edge
is >= 0.9 mm (Revit short-curve limit ~0.8 mm).

Segments: a point (x, y) is a line end; ('a', mid, end) is an arc through mid to end.
"""
import math

OUTER = [(0.0, 0.0), (0.0, 9.4), (-2.6, 9.4), (-2.6, 8.5), (-6.9, 10.0), (-2.6, 11.5), (-2.6, 10.6), (0.0, 10.6),
         (0.0, 19.0), (-0.9, 19.0), (-0.9, 20.0), (16.8, 20.0),
         ('a', (20.0, 16.8), (16.8, 13.6)),             # curl, centre (16.8, 16.8) r 3.2
         (10.1, 17.7), (3.9, 18.7),
         ('a', (3.9 - 2.8 / math.sqrt(2), 15.9 + 2.8 / math.sqrt(2)), (1.1, 15.9)),   # scoop fillet, centre (3.9, 15.9) r 2.8
         (1.1, 0.0)]
HOLE = [(13.8, 18.3), (17.2, 18.7),
        ('a', (19.0, 16.9), (17.2, 15.1)),              # teardrop, centre (17.2, 16.9) r 1.8
        (15.9, 15.9)]
DOOR_FACE_YD = 19.0     # door front face in drawing y_d
FACE_BASE_MM = 50.0     # door face sits at family z = 50 mm; Placement Plane at 50 - Door Face Offset


PROFILE_H = 20.0        # leg bottom to web top (door bottom edge), drawing x_d 0..20


def to_local(p):
    """Drawing (x_d, y_d) -> family local (y, z). The placement line is the bottom of the profile
    (the cabinet box's bottom front edge): y up from the line, so the leg bottom is y = 0, the web
    (door bottom edge) y = 20 and the tongue tip y = 26.9; z out of the door / cabinet face."""
    return (PROFILE_H - p[0], p[1] - DOOR_FACE_YD + FACE_BASE_MM)


def _area_of(loop):
    """Signed area of a loop of lines and 3-point arcs (shoelace plus circular-segment terms)."""
    pts = []
    a = 0.0
    cur = loop[0]
    seq = loop[1:] + [loop[0]]
    for item in seq:
        if isinstance(item[0], str):
            mid, end = item[1], item[2]
            a += cur[0] * end[1] - end[0] * cur[1]
            # circle through cur, mid, end
            ax, ay = cur; bx, by = mid; cx, cy = end
            d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
            ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
            uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
            r = math.hypot(ax - ux, ay - uy)
            chord = math.hypot(cx - ax, cy - ay)
            theta = 2 * math.asin(min(1.0, chord / (2 * r)))
            seg = 0.5 * r * r * (theta - math.sin(theta))
            # sign: segment bulges to the side of mid relative to chord
            side = (cx - ax) * (by - ay) - (cy - ay) * (bx - ax)
            a += 2 * seg * (-1 if side > 0 else 1)
            cur = end
        else:
            a += cur[0] * item[1] - item[0] * cur[1]
            cur = item
    return a / 2.0


def section_area_mm2():
    return abs(_area_of(OUTER)) - abs(_area_of(HOLE))
