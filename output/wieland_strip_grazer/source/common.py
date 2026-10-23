# -*- coding: utf-8 -*-
"""Shared constants and helpers for the Wieland strip grazer build and validation scripts (IronPython 2.7 inside Revit 2025)."""
import os
import sys
import json
import math
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

OUT = os.path.normpath('E:/Claude/3D-Model-Workflow/output/wieland_strip_grazer')
RFA_NAME = 'Wieland_Hidden_Linear_Wall_Grazer_4-10_2800K_R2025_Rev2.rfa'
RFA_REV1 = os.path.join(OUT, 'Wieland_Hidden_Linear_Wall_Grazer_4-10_2800K_R2025.rfa')   # superseded: tilt 0, cone points along the fixture (-X)
RFA = os.path.join(OUT, RFA_NAME)
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
TYPE_NAME = '4-10 Grazer 2800K'
IN = 12.0

# ---- spec values (inches unless noted). Family axes: X along the facade (fixture length), Y across the ledge, Z out of the host face.
BODY_L = 58.0             # 4'-10"
BODY_W = 2.0
BODY_H = 1.5
SOURCE_Z = BODY_H + 0.25  # 1 3/4 in above the host face, 1/4 in above the body top
LINE_LENGTH = BODY_L      # Emit from Line Length 4'-10"
BEAM_DEG = 10.0
FIELD_DEG = 30.0          # spec range 25-30 deg
TILT_DEG = 90.0           # Rev2: a Line + Spot cone points along the line (-X) at tilt 0, and straight up (+Z) at 90 once the source is rotated 180 deg about X (measured, explore_aim.py)
FLUX_LM = 2500.0
CCT_K = 2800.0
LOSS = 1.0
MATERIAL_PARAM = 'Body Finish'


def guard(path):
    p = os.path.normpath(path)
    if not p.lower().startswith(OUT.lower() + os.sep):
        raise RuntimeError('write outside run folder refused: ' + p)
    return p


def write_json(name, data):
    with open(guard(os.path.join(OUT, name)), 'w') as f:
        json.dump(data, f, indent=2, default=str)


def xyz(x, y, z):
    return DB.XYZ(x / IN, y / IN, z / IN)


def box_solid(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from inches."""
    loop = DB.CurveLoop()
    pts = [xyz(x0, y0, z0), xyz(x1, y0, z0), xyz(x1, y1, z0), xyz(x0, y1, z0)]
    for i in range(4):
        loop.Append(DB.Line.CreateBound(pts[i], pts[(i + 1) % 4]))
    return DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]), DB.XYZ.BasisZ, (z1 - z0) / IN)


def all_solids(geometry):
    for item in geometry:
        if isinstance(item, DB.Solid) and item.Volume > 1e-12:
            yield item
        elif isinstance(item, DB.GeometryInstance):
            for s in all_solids(item.GetInstanceGeometry()):
                yield s
