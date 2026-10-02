# -*- coding: utf-8 -*-
"""Shared constants for SHB_Glass Clamp 180 Square (CRL SGC180BBRZ stand-in).

Imported by build_clamp.py (IronPython 2.7 inside Revit) and verify_clamp.py /
selftest_offline.py (CPython 3). Keep it Python-2/3 neutral: no f-strings, no
keyword-only arguments, standard library only.

Units are inches unless a name says otherwise. Every value carries its source
class; only VERIFIED values may be described as manufacturer data.
"""

import math

FAMILY_NAME = 'SHB_Glass Clamp 180 Square'
RFA_NAME = FAMILY_NAME + '.rfa'
CATALOG_NAME = FAMILY_NAME + '.txt'
DEFAULT_TYPE = '1-2 Glass'
TYPES = [('3-8 Glass', 0.375), ('1-2 Glass', 0.5)]   # (type name, Glass_Thickness in)

# source classes
VERIFIED = 'VERIFIED CRL'            # printed on the CRL product page or template PDF
DERIVED = 'DERIVED from CRL values'  # arithmetic on printed values only
PROJECT = 'PROJECT record'           # 651 Belmont finish database / IFC note
ASSUMED = 'ASSUMED'                  # no manufacturer value found; check before release

# name, kind, default (in / text), formula or None, source, note
PARAMETERS = [
    ('Glass_Thickness', 'length', 0.5, None, PROJECT,
     'IFC A0.2 General Note 45: all 651 Belmont shower glass 1/2 in minimum (finish database, 2026-09-28). '
     'CRL range 3/8-1/2 in.'),
    ('Plate_Thickness', 'length', 0.125, None, ASSUMED,
     'Not printed by CRL; schematic template section scales 0.14-0.18 in (unreliable).'),
    ('Clamp_Width', 'length', 5.0, None, VERIFIED, 'CRL: Width 5 in (127 mm).'),
    ('Clamp_Height', 'length', 2.0, None, VERIFIED, 'CRL: Height 2 in (51 mm).'),
    ('Joint_Gap', 'length', 0.0625, '0.0625"', VERIFIED,
     'CRL template: 1/16 in (1.5 mm) gap. Task sheet assumed 1/8. Formula-locked: no glass is modelled.'),
    ('Hole_Edge_Distance', 'length', 1.59375, '1.59375"', VERIFIED,
     'CRL template: hole centre 1-19/32 in (41 mm) from glass edge. Formula-locked: screw positions are fixed.'),
    ('Cap_Diameter', 'length', 0.5, '0.5"', ASSUMED,
     'Screw head across flats; CRL rear isometric scales about 0.46 in. Task sheet assumed 3/4. Formula-locked '
     'constant; labels the head reference-plane dimensions.'),
    ('Cap_Height', 'length', 0.0625, None, ASSUMED,
     'CRL draws the heads flush; 1/16 in proud is a visual reveal only. Task sheet assumed 1/8.'),
    ('Cap_Spacing', 'length', 3.25, '3.25"', DERIVED,
     'Screw centres = glass-hole centres = 2 x Hole_Edge_Distance + Joint_Gap. Task sheet formula '
     'Clamp_Width - 2 in gave 3 in. Constant formula (a dependent formula evaluated to 0.0625 natively, '
     '2026-10-02); labels the dimension that places both screw heads.'),
    ('Clamp_Material', 'material', None, None, PROJECT, 'Default material below.'),
    ('Model Accuracy Notes', 'text', None, None, None, 'See ACCURACY_NOTE.'),
]
LENGTH_DEFAULTS = dict((p[0], p[2]) for p in PARAMETERS if p[1] == 'length')
# Constant-formula parameters (no formula depends on another: dependent formulas evaluated wrongly natively).
# Joint_Gap and Hole_Edge_Distance only document CRL data; Cap_Spacing and Cap_Diameter label dimensions.
LOCKED_PARAMETERS = ('Joint_Gap', 'Hole_Edge_Distance', 'Cap_Diameter', 'Cap_Spacing')
FORMULAS = dict((p[0], p[3]) for p in PARAMETERS if p[3])

# Built-in identity parameters (the family already owns Manufacturer, Model, Description,
# Type Comments and URL; custom parameters with those names would collide).
IDENTITY = {
    'ALL_MODEL_MANUFACTURER': 'CRL',
    'ALL_MODEL_MODEL': 'SGC180BBRZ',
    'ALL_MODEL_DESCRIPTION': 'Square 180 Deg Glass-to-Glass Clamp',
    'ALL_MODEL_TYPE_COMMENTS': 'SGC180BBRZ - Brushed Bronze',
    'ALL_MODEL_URL': ('https://www.crlaurence.com/All-Products/Shower-Hardware/Glass-Shower-Clamps-and-Brackets/'
                      'Glass-to-Glass-Clamps/Square-Profile-Clamps---Glass-To-Glass/'
                      'CRL-Brushed-Bronze-Square-180-Degree-Glass-to-Glass-Clamp/p/SGC180BBRZ'),
}
ACCURACY_NOTE = ('Generic stand-in for CRL SGC180BBRZ. CRL-verified: 2 x 5 in, 3/8-1/2 in glass, 1/16 in joint gap, '
                 'screw centres 1-19/32 in from each glass edge, 2 rear screws, plain front. ASSUMED: plate 1/8 in, '
                 'screw head 1/2 in dia x 1/16 in proud. Screw head diameter and position are fixed (Joint_Gap, '
                 'Hole_Edge_Distance, Cap_Diameter, Cap_Spacing are formula-locked and informational); heads follow '
                 'Plate Outer Back and Cap_Height. Gaskets not modelled. See output/glass_clamp_180/INFERENCES.md.')

# Material: finish-database name for the 651 Belmont primary-bath bronze (Kohler BV rows,
# Duplex Down / Penthouse / Simplex primary baths). Values from the task sheet.
MATERIAL = {
    'name': 'Vibrant Brushed Bronze',
    'color': (110, 86, 62),
    'glossiness': 0.65,          # task sheet roughness ~0.35
    'is_metal': True,            # task sheet metallic 1.0
    'refl0': 0.55, 'refl90': 0.90,
    'material_class': 'Metal',
}

SUBCATEGORIES = ('Clamp Plate', 'Clamp Cap')
PARTS = [  # key, subcategory, shown in coarse
    ('plate_front', 'Clamp Plate', True),
    ('plate_back', 'Clamp Plate', True),
    ('cap_left', 'Clamp Cap', False),
    ('cap_right', 'Clamp Cap', False),
]
CAP_SIDE = 'back'   # CRL rear view carries the screws; front (+Y, room side) is plain

# Reference planes. Six names come from the task sheet; the four clamp-edge planes are
# added so every plate sketch edge can be locked. 'Joint CL' is the template's
# 'Center (Left/Right)' renamed; the glass centre plane stays 'Center (Front/Back)'.
SPEC_PLANES = ['Joint CL', 'Glass Mid', 'Glass Face Front', 'Glass Face Back',
               'Plate Outer Front', 'Plate Outer Back']
EXTRA_PLANES = ['Clamp Left', 'Clamp Right', 'Clamp Top', 'Clamp Bottom']
# Screw-head planes: centre lines EQ about Joint CL (Cap_Spacing); flats EQ about each centre line and about
# Glass Mid (Cap_Diameter). None of them moves when Glass_Thickness, Clamp_Width or Plate_Thickness flex.
SCREW_PLANES = ['Screw L CL', 'Screw R CL', 'Screw L Left', 'Screw L Right', 'Screw R Left', 'Screw R Right',
                'Screw Top', 'Screw Bottom']
CAP_SIDES = 24               # head prism: faces normal to +-X and +-Z exist because CAP_SIDES % 4 == 0
# Labelled dimensions expected in the saved family: label -> count
LABELLED_DIMENSIONS = {'Glass_Thickness': 1, 'Plate_Thickness': 2, 'Clamp_Width': 1, 'Clamp_Height': 1,
                       'Cap_Spacing': 1, 'Cap_Diameter': 3}
EQ_DIMENSIONS = 7            # glass, clamp sides, clamp top/bottom, screw centres, 2 x screw flats X, screw flats Z
DIMENSION_KEYS = ['glass', 'glass_eq', 'height', 'height_eq', 'plate_back', 'plate_front', 'screw_l_dia',
                  'screw_l_eq', 'screw_r_dia', 'screw_r_eq', 'screw_spacing', 'screw_spacing_eq', 'screw_z_dia',
                  'screw_z_eq', 'width', 'width_eq']
MIN_LOCKED_ALIGNMENTS = 8    # 4 side faces per plate
MIN_CAP_LOCKS = 8            # 4 flats (+-X, +-Z) per screw head

FLEX = [('Glass_Thickness', [0.375, 0.5]),
        ('Clamp_Width', [4.0, 6.0]),
        ('Plate_Thickness', [0.1875, 0.125])]

DIM_TOL = 1e-3
MAX_RFA_BYTES = 500 * 1024
MIN_FAMILY_IMAGES = 4


def cap_polygon(cx, y, v):
    """Screw-head prism profile in family inches: regular CAP_SIDES-gon, apothem = Cap_Diameter / 2, rotated so
    that faces are normal to +-X and +-Z (edge midpoints at 0, 90, 180, 270 degrees)."""
    a = v['Cap_Diameter'] / 2.0
    r = a / math.cos(math.pi / CAP_SIDES)
    pts = []
    for k in range(CAP_SIDES):
        t = (k + 0.5) * 2.0 * math.pi / CAP_SIDES
        pts.append((cx + r * math.cos(t), y, r * math.sin(t)))
    return pts


def resolve(values=None):
    """Full value set (inches) with formulas evaluated; overrides in `values`."""
    v = dict(LENGTH_DEFAULTS)
    if values:
        v.update(values)
    v['Cap_Spacing'] = 2.0 * v['Hole_Edge_Distance'] + v['Joint_Gap']
    v['Cap_Offset'] = v['Cap_Spacing'] / 2.0     # derived here only; not a Revit parameter
    return v


def y_bands(v):
    g, p, c = v['Glass_Thickness'], v['Plate_Thickness'], v['Cap_Height']
    return {
        'plate_front': (g / 2.0, g / 2.0 + p),
        'plate_back': (-g / 2.0 - p, -g / 2.0),
        'cap': (-g / 2.0 - p - c, -g / 2.0 - p),
    }


def part_rays(v):
    """Rays in family coordinates. expect = intervals along `axis` for that part only."""
    yb = y_bands(v)
    w, h, d, s = v['Clamp_Width'], v['Clamp_Height'], v['Cap_Diameter'], v['Cap_Offset']
    reach = 8.0
    rays = []
    for part in ('plate_front', 'plate_back'):
        ymid = sum(yb[part]) / 2.0
        rays.append({'key': part + '_thickness', 'part': part, 'axis': 1,
                     'p0': (0.3, -reach, 0.3), 'p1': (0.3, reach, 0.3), 'expect': [yb[part]]})
        rays.append({'key': part + '_width', 'part': part, 'axis': 0,
                     'p0': (-reach, ymid, 0.3), 'p1': (reach, ymid, 0.3), 'expect': [(-w / 2.0, w / 2.0)]})
        rays.append({'key': part + '_height', 'part': part, 'axis': 2,
                     'p0': (0.3, ymid, -reach), 'p1': (0.3, ymid, reach), 'expect': [(-h / 2.0, h / 2.0)]})
    ycap = sum(yb['cap']) / 2.0
    for part, sign in (('cap_left', -1.0), ('cap_right', 1.0)):
        cx = sign * s
        rays.append({'key': part + '_x', 'part': part, 'axis': 0,
                     'p0': (-reach, ycap, 0.0), 'p1': (reach, ycap, 0.0),
                     'expect': [(cx - d / 2.0, cx + d / 2.0)]})
        rays.append({'key': part + '_z', 'part': part, 'axis': 2,
                     'p0': (cx, ycap, -reach), 'p1': (cx, ycap, reach), 'expect': [(-d / 2.0, d / 2.0)]})
        rays.append({'key': part + '_y', 'part': part, 'axis': 1,
                     'p0': (cx, -reach, 0.0), 'p1': (cx, reach, 0.0), 'expect': [yb['cap']]})
    return rays


def project_rays(v):
    """Rays through the whole placed instance (all solids together), family coordinates."""
    yb = y_bands(v)
    s, d = v['Cap_Offset'], v['Cap_Diameter']
    reach = 8.0
    ycap = sum(yb['cap']) / 2.0
    return [
        {'key': 'through_plates', 'axis': 1, 'p0': (0.3, -reach, 0.3), 'p1': (0.3, reach, 0.3),
         'expect': [yb['plate_back'], yb['plate_front']]},
        {'key': 'through_screw_heads', 'axis': 0, 'p0': (-reach, ycap, 0.0), 'p1': (reach, ycap, 0.0),
         'expect': [(-s - d / 2.0, -s + d / 2.0), (s - d / 2.0, s + d / 2.0)]},
        {'key': 'through_right_screw', 'axis': 1, 'p0': (s, -reach, 0.0), 'p1': (s, reach, 0.0),
         'expect': [yb['cap'], yb['plate_back'], yb['plate_front']]},
    ]


def intervals(ray, segments):
    """Segments [((x,y,z),(x,y,z)), ...] -> sorted, merged (lo, hi) along the ray axis."""
    a = ray['axis']
    spans = sorted((min(p[a], q[a]), max(p[a], q[a])) for p, q in segments)
    merged = []
    for lo, hi in spans:
        if merged and lo - merged[-1][1] <= 1e-6:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    return merged


def compare(ray, segments, tol=DIM_TOL, merge=True):
    """True when measured intervals match ray['expect'] one-to-one within tol."""
    a = ray['axis']
    if merge:
        got = intervals(ray, segments)
    else:
        got = sorted((min(p[a], q[a]), max(p[a], q[a])) for p, q in segments)
    want = sorted(tuple(x) for x in ray['expect'])
    if merge:
        # touching expected bands (screw head on plate) merge the same way as the measurement
        fake = [((lo if a == 0 else 0, lo if a == 1 else 0, lo if a == 2 else 0),
                 (hi if a == 0 else 0, hi if a == 1 else 0, hi if a == 2 else 0)) for lo, hi in want]
        want = intervals(ray, fake)
    ok = len(got) == len(want) and all(abs(g[0] - w[0]) <= tol and abs(g[1] - w[1]) <= tol
                                       for g, w in zip(got, want))
    return ok, got, want


def overall_box(v):
    """Expected instance bounding box (inches, family coordinates)."""
    yb = y_bands(v)
    ymin = yb['cap'][0] if CAP_SIDE == 'back' else yb['plate_back'][0]
    return {'min': (-v['Clamp_Width'] / 2.0, ymin, -v['Clamp_Height'] / 2.0),
            'max': (v['Clamp_Width'] / 2.0, yb['plate_front'][1], v['Clamp_Height'] / 2.0)}


def catalog_text():
    """Type catalog contents (ASCII, CRLF). Only Glass_Thickness varies, as the task sheet asks."""
    lines = [',Glass_Thickness##length##inches']
    for name, g in TYPES:
        lines.append('%s,%s' % (name, repr(g)))
    return '\r\n'.join(lines) + '\r\n'


def check_spec():
    """Static self-consistency; returns a list of problems (empty = clean)."""
    problems = []
    v = resolve()
    for name, default in LENGTH_DEFAULTS.items():
        if name in FORMULAS and abs(v[name] - default) > 1e-9:
            problems.append('%s default %r disagrees with formula value %r' % (name, default, v[name]))
    for width in [5.0] + [x for n, xs in FLEX if n == 'Clamp_Width' for x in xs]:
        for dia in [v['Cap_Diameter']] + [x for n, xs in FLEX if n == 'Cap_Diameter' for x in xs]:
            if v['Cap_Offset'] + dia / 2.0 >= width / 2.0:
                problems.append('screw head leaves the plate at width %r, diameter %r' % (width, dia))
            if v['Cap_Offset'] - dia / 2.0 <= v['Joint_Gap'] / 2.0:
                problems.append('screw head crosses the joint at diameter %r' % dia)
    if v['Cap_Height'] < 1.0 / 32.0:
        problems.append('Cap_Height below Revit short-curve comfort (1/32 in)')
    if CAP_SIDES % 4:
        problems.append('CAP_SIDES must be a multiple of 4 so the head has +-X and +-Z flats')
    edge = v['Cap_Diameter'] * math.tan(math.pi / CAP_SIDES)
    if edge < 0.035:
        problems.append('screw-head prism edge %.4f in is under 0.035 in (Revit short-curve margin)' % edge)
    if abs(v['Cap_Spacing'] - (2.0 * v['Hole_Edge_Distance'] + v['Joint_Gap'])) > 1e-9:
        problems.append('Cap_Spacing constant disagrees with 2 x Hole_Edge_Distance + Joint_Gap')
    return problems
