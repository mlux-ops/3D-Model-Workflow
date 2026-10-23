# -*- coding: utf-8 -*-
"""Source-corrected Hinkley Eos 53860BK candidate, Revit 2025.

Runner contract: APP, DB, JOB, TARGET_RFA, SOURCE_RFA, progress, result.
Creates one fresh face-based Lighting Fixtures RFA at TARGET_RFA.
Never edits the baseline build script or any existing RFA / RVT.

THIS IS A RESEARCH CANDIDATE, NOT A NATIVE-VALIDATED OR OEM CAD MATCH.
Read the geometry limitations and published-versus-modeled envelope below.
"""
import os
import sys
import math
from System.Collections.Generic import List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from belmont_fixture_core import NativeBuild, xyz

MODEL = '53860BK'
RETAILER = 'HIN990485'
PRODUCT = 'https://www.hinkley.com/53860bk.html'
DIMENSIONS = 'https://www.hinkley.com/product_spec_print/download/advancedpdf/product_id/52426/'
INSTALL = 'https://d1lnz90t7xw0i5.cloudfront.net/Products/files/53860.pdf'
GLASS_REFERENCE = 'https://southernlightsinc.com/bath-eos-87-53860bk/'
SOURCE_LIST = [PRODUCT, DIMENSIONS, INSTALL, GLASS_REFERENCE]

# Manufacturer-confirmed: 25 W x 5.5 H x 3 extension; circular backplate
# 4.75 inch diameter; black steel; etched glass; two integrated LEDs.
# Third-party stock record lists each of the TWO glass elements as
# 1.25 inch diameter x 17.5 inch long. Crossbars + removable end arms +
# grooved/sliding glass are confirmed by Hinkley's own 53860 manual.
#
# Inferred only from photography, not dimensioned CAD:
# Rail center separation 2.04 in, each left/right U return radius 1.02 in,
# exposed metal tube diameter .28 in, glass radial thickness .08 in,
# individual glass X offsets, wall standoff profile/depth and rail Z.
# The official 5.5 in overall H cannot be reconciled from these photo-derived
# proportions: the current generated silhouette is approximately 4.75 in H
# because its circular backplate is tallest. This is a MATERIAL DIMENSION
# HOLD for geometry sign-off, never silently expand the silhouette to 5.5.

GLASS_LENGTH = 17.5
GLASS_DIAMETER = 1.25
GLASS_RADIUS = GLASS_DIAMETER / 2.0
GLASS_WALL = .08
RAIL_Y = 1.02
RAIL_END_X = 11.34
RETURN_RADIUS = 1.02
METAL_TUBE_RADIUS = .14
RAIL_AXIS_Z = 2.375

NOTES = (
    'Hinkley Eos 53860BK Black / Etched Glass, 25 W x 5.5 H x 3 D in, '
    '4.75 inch diameter round backplate, 19 W integrated LED, 3000 K, '
    '1000 lm, CRI 93, 120 V. Hinkley instruction 53860 specifies sliding '
    'glass inserts in grooved crossbars and removable bent end-arm caps. '
    'This candidate has two 17.5 L x 1.25 diameter etched tubular covers '
    '(dimensions independently repeated by distributor), offset on black '
    'crossbars and U-shaped returns. Rail spacing, glass wall, radius, '
    'fastener size and all minor sections are reconstructed from photos. '
    'Photo-proportioned nominal geometry height is 4.75 inches from the '
    'backplate, 0.75 inches short of published 5.5 inches: geometry hold. '
    'Manufacturer detailed spec says horizontal mounting only, but manufacturer '
    'product photos explicitly show the same 53860BK mounted vertically, and '
    'catalog marketing says both; orientation requires confirmation. '
    'Horizontal placement is the default geometry orientation. '
    'Not manufacturer-authored BIM. No validated IES or electrical connector.'
)


def circle_yz(cx, cy, cz, radius):
    """Circular section in Y-Z plane, normal parallel to fixture X axis."""
    origin = xyz(DB, cx, cy, cz)
    a = DB.Arc.Create(origin, radius / 12.0, 0.0, math.pi,
                      DB.XYZ.BasisY, DB.XYZ.BasisZ)
    b = DB.Arc.Create(origin, radius / 12.0, math.pi, 2.0 * math.pi,
                      DB.XYZ.BasisY, DB.XYZ.BasisZ)
    loop = DB.CurveLoop()
    loop.Append(a)
    loop.Append(b)
    return loop


def x_cylinder(x0, x1, y, z, radius):
    return DB.GeometryCreationUtilities.CreateExtrusionGeometry(
        List[DB.CurveLoop]([circle_yz(x0, y, z, radius)]),
        DB.XYZ.BasisX,
        float(x1 - x0) / 12.0,
    )


def open_etched_glass(x0, x1, y):
    """Hollow glass cylindrical sleeve; original glass wall not dimensioned."""
    outer = x_cylinder(x0, x1, y, RAIL_AXIS_Z, GLASS_RADIUS)
    # Longer cutter opens both ends and avoids coincident cut-face ambiguity.
    inner = x_cylinder(x0 - .10, x1 + .10, y, RAIL_AXIS_Z,
                       GLASS_RADIUS - GLASS_WALL)
    return DB.BooleanOperationsUtils.ExecuteBooleanOperation(
        outer, inner, DB.BooleanOperationsType.Difference
    )


def curved_end_arm(side):
    """Semicircular black steel return, following the product's end-loop."""
    x = float(side) * RAIL_END_X
    at_top = xyz(DB, x, RAIL_Y, RAIL_AXIS_Z)
    at_bottom = xyz(DB, x, -RAIL_Y, RAIL_AXIS_Z)
    at_bulge = xyz(DB, x + side * RETURN_RADIUS, 0, RAIL_AXIS_Z)
    path = DB.CurveLoop()
    path.Append(DB.Arc.Create(at_top, at_bottom, at_bulge))
    section = circle_yz(x, RAIL_Y, RAIL_AXIS_Z, METAL_TUBE_RADIUS)
    return DB.GeometryCreationUtilities.CreateSweptGeometry(
        path, 0, 0, List[DB.CurveLoop]([section])
    )


progress('research_correction_preflight', {'model': MODEL, 'sources': SOURCE_LIST})
fixture = None
try:
    fixture = NativeBuild(
        APP, DB, TARGET_RFA, MODEL, 'Hinkley',
        'Black / Etched Glass', 'wall', PRODUCT, NOTES
    )
    fixture.text('Lightology SKU', RETAILER)
    # Shared helper historically defaults Retailer SKU to manufacturer model.
    # Correct the existing family field without modifying the shared helper.
    for parameter in fixture.fm.Parameters:
        if parameter.Definition.Name == 'Retailer SKU':
            fixture.fm.Set(parameter, RETAILER)
            break
    fixture.text('Light Source', 'Integrated LED 5386XD; 19 W; 120 V; 3000 K')
    fixture.text('Delivered Lumens', '1000 (manufacturer specification)')
    fixture.text('CRI', '93 (manufacturer specification)')
    fixture.text('IES Status', 'Manufacturer lists IES resource; exact file not retrieved')
    fixture.text('Mounting Verification', 'Conflicting official text / vertical photo; horizontal default')
    fixture.text('Proportions Status', 'Published 5.5 H versus modeled 4.75 H; HOLD')
    fixture.size('Published Overall Width', 25.0)
    fixture.size('Published Overall Height', 5.5)
    fixture.size('Published Projection', 3.0)
    fixture.size('Round Backplate Diameter', 4.75)
    fixture.size('Etched Glass Sleeve Diameter (distributor)', GLASS_DIAMETER)
    fixture.size('Etched Glass Sleeve Length (distributor)', GLASS_LENGTH)

    black = fixture.material('Matte Black Steel', (25, 25, 25))
    glass = fixture.material('Etched Opal Glass', (240, 242, 239), 18)

    # Wall host face local z=0. Diameter is manufacturer-dimensioned.
    fixture.cylinder('Round Invisimount backplate 4.75 dia',
                     0, 0, 0, 2.375, .35, black)
    # Rear steel connection is largely occluded by the two tubes in product
    # photographs; these dimensions remain reconstructed.
    fixture.cylinder('Central concealed attachment and standoff',
                     0, 0, .35, .67, 1.68, black)
    fixture.box('Rear two-rail saddle', (-1.02, -1.12, 2.00,
                                         1.02, 1.12, 2.18), black)
    for side, y in [('upper', RAIL_Y), ('lower', -RAIL_Y)]:
        fixture.part('Continuous black %s crossbar' % side,
                     x_cylinder(-RAIL_END_X, RAIL_END_X, y,
                                RAIL_AXIS_Z, METAL_TUBE_RADIUS),
                     black)

    # Independent removable U-shaped end pieces: the manufacturer manual's
    # end arm cap assemblies (1), crossbars (A) and screw retention (2).
    fixture.part('Left curved steel return arm', curved_end_arm(-1), black)
    fixture.part('Right curved steel return arm', curved_end_arm(+1), black)

    # Manufacturer photography shows mirror-image X offset between the two
    # etched white tubes. This is 17.5 in each, from stock glass dimensions.
    for name, x0, x1, y in [
        ('Upper offset etched glass sleeve', -10.5, 7.0, RAIL_Y),
        ('Lower offset etched glass sleeve', -7.0, 10.5, -RAIL_Y),
    ]:
        fixture.part(name, open_etched_glass(x0, x1, y), glass)

    output = fixture.finish()
    output['retailer_sku'] = RETAILER
    output['source_urls'] = SOURCE_LIST
    output['published_envelope_in'] = [25.0, 5.5, 3.0]
    output['glass_nominal_each_in'] = [17.5, 1.25]
    output['glass_quantity'] = 2
    output['manufacturer_ies_status'] = 'LISTED_ON_PRODUCT_PAGE_NOT_DOWNLOADED'
    output['manufacturer_3d_cad_status'] = 'EXACT_MODEL_DOWNLOAD_NOT_VERIFIED'
    output['orientation_status'] = 'CONFLICTING_MANUFACTURER_EVIDENCE_REQUIRES_CONFIRMATION'
    output['geometry_release_status'] = 'HOLD_PENDING_NATIVE_QA_AND_MANUFACTURER_DIMENSION_DETAIL'
    output['modeled_height_conflict_in'] = 0.75
    output['material_and_geometry_assumptions'] = NOTES
    result.update(output)
    progress('r02_candidate_saved_pending_native', output)
finally:
    if fixture is not None:
        fixture.close()
