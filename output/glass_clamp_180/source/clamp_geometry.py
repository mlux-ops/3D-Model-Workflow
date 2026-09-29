# -*- coding: utf-8 -*-
"""Shared constants and analytic expectations for SHB_Glass Clamp 180 Square.

Imported by build_glass_clamp.py (IronPython 2.7 inside Revit), verify_glass_clamp.py
and preview_geometry.py (CPython 3), so it stays py2/py3 safe: no f-strings, no
annotations, true division.

Coordinates (task file, Family Setup 5): origin = centre of the joint gap at mid-height,
+X along the joint row, +Z up, FRONT = +Y (toward the room), BACK = -Y. This is the task's
front; Revit's template 'Front' elevation looks the other way (-Y is the template front).
The clamp is symmetric front/back, so nothing visible depends on it.

All lengths are inches here; the builder converts to Revit's internal feet.
"""
from __future__ import division

import math

FAMILY_NAME = 'SHB_Glass Clamp 180 Square'
RFA_NAME = FAMILY_NAME + '.rfa'
CATALOG_NAME = FAMILY_NAME + '.txt'
RUN_NAME = 'glass_clamp_180'

MANUFACTURER = 'CRL'
MODEL = 'SGC180BBRZ'
DESCRIPTION = 'Square 180 Deg Glass-to-Glass Clamp'
TYPE_COMMENTS = 'SGC180BBRZ - Brushed Bronze'

MATERIAL_NAME = 'Brushed Bronze'
MATERIAL_RGB = (110, 86, 62)
MATERIAL_ROUGHNESS = 0.35            # task file; Revit Generic uses glossiness = 1 - roughness
MATERIAL_GLOSSINESS = 1.0 - MATERIAL_ROUGHNESS
MATERIAL_METALLIC = 1.0              # task file; Revit Generic: generic_is_metal = True
MATERIAL_REFL_0 = 0.40               # inferred, see INFERENCES.md
MATERIAL_REFL_90 = 0.80              # inferred, see INFERENCES.md

SUBCATEGORY_PLATE = 'Clamp Plate'
SUBCATEGORY_CAP = 'Clamp Cap'

# ----------------------------------------------------------------- parameters
# (name, kind, default inches or None, formula or None, source status)
# 'kind' is the Revit spec: length | material | text.  Status reproduces the task file.
PARAMETERS = [
    ('Glass_Thickness', 'length', 0.5, None, 'type-varying (3/8" and 1/2" catalog rows)'),
    ('Plate_Thickness', 'length', 0.125, None, 'ASSUMED'),
    ('Clamp_Width', 'length', 5.0, None, 'VERIFIED (CRL)'),
    ('Clamp_Height', 'length', 2.0, None, 'VERIFIED (CRL)'),
    ('Joint_Gap', 'length', 0.125, None, 'ASSUMED; informational, drives no solid'),
    ('Cap_Diameter', 'length', 0.75, None, 'ASSUMED'),
    ('Cap_Height', 'length', 0.125, None, 'ASSUMED'),
    ('Cap_Spacing', 'length', None, 'Clamp_Width - 2 in', 'ASSUMED (task formula)'),
]
# Helper formula parameters. Not in the task's table; needed because a reference plane
# is positioned by dimension labels only, while the plate extrusions take START/END
# offsets, which can only be associated with parameters.
HELPERS = [
    ('Cap_Radius', 'Cap_Diameter / 2'),
    ('Glass_Face_Front_Y', 'Glass_Thickness / 2'),
    ('Plate_Outer_Front_Y', 'Glass_Thickness / 2 + Plate_Thickness'),
    ('Glass_Face_Back_Y', '-Glass_Thickness / 2'),
    ('Plate_Outer_Back_Y', '-Glass_Thickness / 2 - Plate_Thickness'),
]
MATERIAL_PARAMETER = 'Clamp_Material'
TYPES = [('1-2 Glass', 0.5), ('3-8 Glass', 0.375)]      # first = default / current at save
DEFAULT_TYPE = TYPES[0][0]

VERIFIED = {'overall_height_in': 2.0, 'overall_width_in': 5.0,
            'glass_range_in': (0.375, 0.5), 'finish': 'Brushed Bronze'}
ASSUMED = {'plate_thickness_in': 0.125, 'joint_gap_in': 0.125,
           'cap_diameter_in': 0.75, 'cap_height_in': 0.125, 'caps_per_side': 2}

# ----------------------------------------------------------------- reference planes
# name -> (normal axis, description). The first six are the task's exact names.
TASK_PLANES = ['Joint CL', 'Glass Mid', 'Glass Face Front', 'Glass Face Back',
               'Plate Outer Front', 'Plate Outer Back']
EXTRA_PLANES = ['Clamp Left', 'Clamp Right', 'Clamp Top', 'Clamp Bottom',
                'Cap Center Left', 'Cap Center Right', 'Cap Radius Top',
                'Cap Top Front', 'Cap Top Back']
TEMPLATE_Y_PLANE = 'Center (Front/Back)'     # Y = 0, kept under its template name
TEMPLATE_X_PLANE = 'Center (Left/Right)'     # X = 0, renamed to 'Joint CL' when Revit allows

# ----------------------------------------------------------------- flex plan
REQUIRED_FLEX = [('Glass_Thickness', [0.375, 0.5]), ('Clamp_Width', [4.0, 6.0, 5.0])]
INFO_FLEX = [('Clamp_Height', [1.5, 2.5, 2.0]), ('Cap_Diameter', [0.5, 1.0, 0.75]),
             ('Cap_Height', [0.25, 0.125]), ('Plate_Thickness', [0.1875, 0.125])]

FILE_SIZE_LIMIT_BYTES = 500 * 1024
DIM_TOL_IN = 0.0005
GEOM_TOL_IN = 0.01           # measured solid bounds; a tessellated cylinder's extremes can sit a hair inside


def state(glass=0.5, plate=0.125, width=5.0, height=2.0, cap_d=0.75, cap_h=0.125):
    """Parameter state in inches, with the task's Cap_Spacing formula applied."""
    return {'Glass_Thickness': glass, 'Plate_Thickness': plate, 'Clamp_Width': width,
            'Clamp_Height': height, 'Cap_Diameter': cap_d, 'Cap_Height': cap_h,
            'Cap_Spacing': width - 2.0}


def with_change(base, name, value):
    out = dict(base)
    out[name] = value
    out['Cap_Spacing'] = out['Clamp_Width'] - 2.0
    return out


def plane_positions(st):
    """name -> (axis, position inches) for every reference plane at parameter state st."""
    g2 = st['Glass_Thickness'] / 2.0
    p = st['Plate_Thickness']
    w2 = st['Clamp_Width'] / 2.0
    h2 = st['Clamp_Height'] / 2.0
    s2 = st['Cap_Spacing'] / 2.0
    ch = st['Cap_Height']
    return {
        'Joint CL': ('x', 0.0), 'Glass Mid': ('z', 0.0),
        'Glass Face Front': ('y', g2), 'Glass Face Back': ('y', -g2),
        'Plate Outer Front': ('y', g2 + p), 'Plate Outer Back': ('y', -(g2 + p)),
        'Clamp Left': ('x', -w2), 'Clamp Right': ('x', w2),
        'Clamp Top': ('z', h2), 'Clamp Bottom': ('z', -h2),
        'Cap Center Left': ('x', -s2), 'Cap Center Right': ('x', s2),
        'Cap Radius Top': ('z', st['Cap_Diameter'] / 2.0),
        'Cap Top Front': ('y', g2 + p + ch), 'Cap Top Back': ('y', -(g2 + p + ch)),
    }


def solids(st):
    """key -> dict(kind, x, y, z ranges in inches, volume cubic inches, centre x/z)."""
    g2 = st['Glass_Thickness'] / 2.0
    p, w2, h2 = st['Plate_Thickness'], st['Clamp_Width'] / 2.0, st['Clamp_Height'] / 2.0
    s2, ch, r = st['Cap_Spacing'] / 2.0, st['Cap_Height'], st['Cap_Diameter'] / 2.0
    out = {
        'plate_front': {'kind': 'plate', 'x': (-w2, w2), 'y': (g2, g2 + p), 'z': (-h2, h2)},
        'plate_back': {'kind': 'plate', 'x': (-w2, w2), 'y': (-(g2 + p), -g2), 'z': (-h2, h2)},
    }
    for key in ('plate_front', 'plate_back'):
        s = out[key]
        s['volume'] = (s['x'][1] - s['x'][0]) * (s['y'][1] - s['y'][0]) * (s['z'][1] - s['z'][0])
    for side, y0, y1 in (('front', g2 + p, g2 + p + ch), ('back', -(g2 + p + ch), -(g2 + p))):
        for hand, cx in (('left', -s2), ('right', s2)):
            out['cap_%s_%s' % (side, hand)] = {
                'kind': 'cap', 'x': (cx - r, cx + r), 'y': (y0, y1), 'z': (-r, r),
                'cx': cx, 'cz': 0.0, 'volume': math.pi * r * r * ch}
    return out


def overall_extents(st):
    """Bounding extents of the whole family: (dx, dy, dz) inches."""
    g2 = st['Glass_Thickness'] / 2.0
    ys = g2 + st['Plate_Thickness'] + st['Cap_Height']
    return (max(st['Clamp_Width'], st['Cap_Spacing'] + st['Cap_Diameter']), 2.0 * ys,
            max(st['Clamp_Height'], st['Cap_Diameter']))


def classify(cx, cy, cz, st=None, tol=0.03):
    """Map a solid's centroid (inches) at parameter state st (default: the default state) to its
    key, or None. Plate and cap centroids are more than 0.06 in apart at every state used."""
    for key, s in solids(st or state()).items():
        mx, my = sum(s['x']) / 2.0, sum(s['y']) / 2.0
        if abs(cx - mx) < tol and abs(cy - my) < tol and abs(cz) < tol:
            return key
    return None


def catalog_text():
    """Revit type catalog, CRLF, ASCII: header row then one row per glass thickness."""
    lines = [',Glass_Thickness##length##inches']
    for name, glass in TYPES[::-1]:            # 3/8" row first, as the task lists it
        lines.append('%s,%s' % (name, ('%.4f' % glass).rstrip('0').rstrip('.')))
    return '\r\n'.join(lines) + '\r\n'
