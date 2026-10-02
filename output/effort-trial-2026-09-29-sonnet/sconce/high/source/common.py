# -*- coding: utf-8 -*-
"""Shared constants and helpers for the KW1041MBK build and validation scripts (IronPython 2.7 inside Revit 2025)."""
import os
import sys
import json
import math
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

OUT = os.path.normpath('E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/high')
RFA_NAME = 'Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa'
RFA = os.path.join(OUT, RFA_NAME)
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
TYPE_NAME = 'KW1041MBK - Midnight Black / Milk'

# ---- geometry (inches). Family axes: X across the wall, Y up the wall, Z out of the wall (host face is Z = 0).
BACK_R = 2.625            # published: backplate 5.25 in diameter
BACK_T = 0.125            # published: 0.125 in deep
BODY_R = 2.125            # measured from the side photo: 4.25 in drum diameter (4.25 +/- 0.05)
DISC_R = 4.0              # published overall width 8.00 in = disc diameter
DISC_T = 0.06             # inferred sheet-steel thickness
SHADE_R = 1.75            # published: 3.5 in maximum diameter
SHADE_AXIAL = 3.25        # published: 3.25 in along the shade axis
SHADE_WALL = 0.08         # inferred glass wall thickness
S0 = 0.20                 # inferred: shade neck plane distance from the slanted face, along the shade axis
COLLAR_R = 0.775          # measured: socket collar about 1.55 in diameter
STEM_R = 0.55             # inferred lamp-holder stem
STEM_LEN = 0.60           # inferred lamp-holder stem length beyond the neck plane
H_PUBLISHED = 7.63
D_PUBLISHED = 5.50
W_PUBLISHED = 8.00

A_C = S0 + (SHADE_AXIAL - SHADE_R)          # shade sphere centre along the axis from the face centre


def solve_theta():
    """Tilt from vertical so that the tilted disc (8 in circle, DISC_T thick) is exactly H_PUBLISHED tall."""
    lo, hi = 0.0, math.radians(40.0)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        h = 2 * DISC_R * math.cos(mid) + DISC_T * math.sin(mid)
        if h > H_PUBLISHED:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


THETA = solve_theta()
COS = math.cos(THETA)
SIN = math.sin(THETA)
D0 = D_PUBLISHED - A_C * COS - SHADE_R      # depth of the slanted-face centre so the shade front lands on 5.50 in
N_AXIS = (0.0, -SIN, COS)                    # out of the slanted face: outward and tilted down
V_UP = (0.0, COS, SIN)                       # up the slanted face


def guard(path):
    p = os.path.normpath(path)
    if not p.lower().startswith(OUT.lower() + os.sep):
        raise RuntimeError('write outside run folder refused: ' + p)
    return p


def write_json(name, data):
    with open(guard(os.path.join(OUT, name)), 'w') as f:
        json.dump(data, f, indent=2, default=str)


def xyz(x, y, z):
    return DB.XYZ(x / 12.0, y / 12.0, z / 12.0)


def vec(t):
    return DB.XYZ(t[0], t[1], t[2])


FACE_CENTER = xyz(0.0, 0.0, D0)              # feet
AXIS = vec(N_AXIS)
UP = vec(V_UP)


def revolve_profile(segs, origin=None, axis=None, radial=None):
    """Revolve a closed profile of ('L', (r0,a0), (r1,a1)) / ('A', (r0,a0), (r1,a1), (rm,am)) segments
    (r radial and a axial, inches) a full turn about the line through origin along axis."""
    origin = origin or FACE_CENTER
    axis = axis or AXIS
    radial = radial or DB.XYZ.BasisX

    def at(p):
        return origin.Add(radial.Multiply(p[0] / 12.0)).Add(axis.Multiply(p[1] / 12.0))
    loop = DB.CurveLoop()
    for s in segs:
        if s[0] == 'L':
            loop.Append(DB.Line.CreateBound(at(s[1]), at(s[2])))
        else:
            loop.Append(DB.Arc.Create(at(s[1]), at(s[2]), at(s[3])))
    frame = DB.Frame(origin, radial, axis.CrossProduct(radial), axis)
    return DB.GeometryCreationUtilities.CreateRevolvedGeometry(frame, List[DB.CurveLoop]([loop]), 0, 2 * math.pi)


def circle_loop(center, x_axis, y_axis, r_in):
    loop = DB.CurveLoop()
    r = r_in / 12.0
    loop.Append(DB.Arc.Create(center, r, 0, math.pi, x_axis, y_axis))
    loop.Append(DB.Arc.Create(center, r, math.pi, 2 * math.pi, x_axis, y_axis))
    return loop


def rect_loop(center, x_axis, y_axis, half_x, half_y):
    def at(a, b):
        return center.Add(x_axis.Multiply(a / 12.0)).Add(y_axis.Multiply(b / 12.0))
    pts = [at(-half_x, -half_y), at(half_x, -half_y), at(half_x, half_y), at(-half_x, half_y)]
    loop = DB.CurveLoop()
    for i in range(4):
        loop.Append(DB.Line.CreateBound(pts[i], pts[(i + 1) % 4]))
    return loop


def extrude(loops, direction, length_in):
    return DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop](loops), direction, length_in / 12.0)


def all_solids(geometry):
    for item in geometry:
        if isinstance(item, DB.Solid) and item.Volume > 1e-12:
            yield item
        elif isinstance(item, DB.GeometryInstance):
            for s in all_solids(item.GetInstanceGeometry()):
                yield s
