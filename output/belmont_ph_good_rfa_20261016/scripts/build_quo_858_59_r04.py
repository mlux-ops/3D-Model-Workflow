# -*- coding: utf-8 -*-
"""Quorum Veno 858-59 R04 silhouette correction; PHOTO-DERIVED, UNAPPROVED.

Requires APP, DB, TARGET_RFA, progress, result in Revit 2025 IronPython 2.7.
Prime alone may run Revit. This script creates a NEW file and cannot overwrite.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from System.Collections.Generic import List
from belmont_fixture_core import NativeBuild, xyz

MODEL = '858-59'
SOURCE = 'https://www.quorumhome.com/products/858-59'
CUTSHEET = 'https://images.junipercdn.com/3206/application-assets/juniper-web/product%20cut%20sheets/858-59.pdf'
PHOTO = 'https://www.quorumhome.com/cdn/shop/files/858-59_2_700x700.jpg?v=1755215395'
CANOPY_H = 0.75
STEM_H = 24.0
BODY_H = 19.0
SHADE_H = 11.25
GLASS_START = CANOPY_H + STEM_H + BODY_H - SHADE_H
GLASS_WALL = 0.125  # explicitly inferred, not in OEM dimensions
# Photo glass outline: y pixels from ~210 (small neck) to ~610 (open base),
# maximum half-width ~189 px. 11 in nominal diameter sets peak radius 5.5in.
# z here is DOWN from the photo neck: ceiling face host flips local Z in project.
# Outer radii are rounded from both visible left and right silhouette edges.
# Segment endpoints preserve original measured photographic feature heights.
PROFILE_DOWN = [
    (0.00, 0.95),
    (0.42, 1.84),
    (0.84, 2.98),
    (1.40, 3.94),
    (2.11, 4.72),
    (2.81, 5.12),
    (3.51, 5.38),
    (4.36, 5.50),
    (5.20, 5.43),
    (6.32, 5.25),
    (7.44, 4.95),
    (8.56, 4.57),
    (9.68, 4.13),
    (10.52, 3.65),
    (11.25, 3.18)
]
NOTES = (
    'R04 UNAPPROVED photograph-derived geometry. Official OEM D11 x H19 body, '
    'glass H11.25; canopy D4.75 x H0.75; Matte Black steel / clear glass. '
    'Manufacturer image establishes narrow top, broad rounded shoulder and '
    'moderately open lower rim. Glass radii above were normalized from photo '
    'and are not manufacturer dimensioned. Wall thickness 0.125in and center '
    'socket/retainer hardware are inferred. Example 24in suspension equals '
    'two supplied 12in rods. Other supplied 8/16in stems and 12in chain not '
    'shown. No certified OEM RFA/CAD or exact IES/MEP connector verified.'
)


def revolved_shade(DB):
    """Closed thin-walled radial section with open ends, exact 11in max OD."""
    assert len(PROFILE_DOWN) >= 8
    assert PROFILE_DOWN[0][0] == 0.0
    assert abs(PROFILE_DOWN[-1][0] - SHADE_H) < 1e-9
    assert abs(2.0 * max(r for z, r in PROFILE_DOWN) - 11.0) < 1e-9
    for i in range(1, len(PROFILE_DOWN)):
        assert PROFILE_DOWN[i][0] > PROFILE_DOWN[i - 1][0]
    # Closed XZ cross section: its first and last radial connectors create
    # a physical lip; the shade remains open at both ends, not solid glass.
    outer = [(r, GLASS_START + z) for z, r in PROFILE_DOWN]
    inner = [(r - GLASS_WALL, GLASS_START + z)
             for z, r in reversed(PROFILE_DOWN)]
    if min(p[0] for p in inner) <= 0:
        raise ValueError('Glass thickness crosses centerline')
    points = outer + inner
    loop = DB.CurveLoop()
    for i in range(len(points)):
        p, q = points[i], points[(i + 1) % len(points)]
        a, b = xyz(DB, p[0], 0, p[1]), xyz(DB, q[0], 0, q[1])
        if a.DistanceTo(b) <= APP.ShortCurveTolerance:
            raise ValueError('Profile edge too short for Revit')
        loop.Append(DB.Line.CreateBound(a, b))
    frame = DB.Frame(DB.XYZ.Zero, DB.XYZ.BasisX, DB.XYZ.BasisY,
                     DB.XYZ.BasisZ)
    return DB.GeometryCreationUtilities.CreateRevolvedGeometry(
        frame, List[DB.CurveLoop]([loop]), 0.0, 2.0 * math.pi)


progress('preflight', {'model': MODEL, 'revision': 'R04_PHOTO_DERIVED_UNAPPROVED'})
f = None
try:
    f = NativeBuild(APP, DB, TARGET_RFA, MODEL, 'Quorum',
                    'Matte Black / Clear - R04 photo-derived unapproved',
                    'ceiling', SOURCE, NOTES)
    f.text('Lightology SKU', 'QUO1249827')
    f.text('Manufacturer Cut Sheet', CUTSHEET)
    f.text('Manufacturer Silhouette Photo', PHOTO)
    f.text('Geometry Accuracy', 'Photographic silhouette; NOT OEM section CAD')
    f.text('Lamp', 'One E26 medium-base, maximum 100W; lamp not supplied')
    f.text('Supplied Suspension', '2x8in, 2x12in, 2x16in stems; 12in chain')
    f.size('OEM Diameter', 11.0)
    f.size('OEM Body Height', BODY_H)
    f.size('OEM Shade Height', SHADE_H)
    f.size('OEM Canopy Diameter', 4.75)
    f.size('OEM Canopy Height', CANOPY_H)
    f.size('Selected Stem Drop', STEM_H)
    black = f.material('Matte Black', (23, 23, 23))
    glass = f.material('Clear Glass', (233, 237, 237), 95)
    f.cylinder('Canopy - OEM D4.75 x H.75', 0, 0, 0, 2.375, CANOPY_H, black)
    f.cylinder('Two selected 12in stems - representative', 0, 0,
               CANOPY_H, .20, STEM_H, black)
    body_top = CANOPY_H + STEM_H
    f.cylinder('Upper hardware coupling - inferred', 0, 0,
               body_top, .75, .5, black)
    f.cylinder('Central support - inferred', 0, 0,
               body_top + .5, .32, GLASS_START - body_top - .25, black)
    f.cylinder('E26 socket representation - inferred', 0, 0,
               GLASS_START + .25, .58, 1., black)
    f.part('Quorum photo-derived clear glass bell shell', revolved_shade(DB), glass)
    info = f.finish()
    info.update({
        'revision': 'R04_PHOTO_DERIVED_UNAPPROVED',
        'cut_sheet_url': CUTSHEET, 'photo_url': PHOTO,
        'profile_down_from_top_in': PROFILE_DOWN,
        'glass_wall_thickness_assumed_in': GLASS_WALL,
        'installed_drop_in': CANOPY_H + STEM_H + BODY_H,
        'shade_height_in': SHADE_H,
        'native_qa': 'PENDING', 'visual_approval': 'PENDING',
        'electrical_connector': 'NOT PROVIDED', 'exact_ies': 'NOT VERIFIED',
    })
    result.update(info)
    progress('saved', info)
finally:
    if f is not None:
        f.close()
