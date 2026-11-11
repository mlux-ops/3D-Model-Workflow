# -*- coding: utf-8 -*-
"""Hinkley Eos 53860BK R03 - dimension-correct source-guarded Revit 2025 builder.

Builder contract: APP (Revit Application), DB, TARGET_RFA, JOB,
progress(stage, detail), result. Call through run_hin_53860bk_r03.py, which
provides these globals in one isolated pyrevit run process.

AUTHORITY:
 - https://www.hinkley.com/53860bk.html
 - https://www.hinkley.com/product_spec_print/download/pdf/product_id/52426/Advanced/1
 - https://www.hinkley.com/media/catalog/product/2/f/2f013ee2ee5d2d0fc4fbd9688adb2dd6-53860BK_dim1.jpg
 - https://d1lnz90t7xw0i5.cloudfront.net/Products/files/53860.pdf

R02 ERROR (verified native): 25.0 W x 4.75 H x 3.0 D in (0.75 H short).
Manufacturer: 25.0 W x 5.5 H x 3.0 D; backplate 4.75-in dia.
The OFFICIAL manufacturer dimensioned PHOTO's 5.5-in dimension endpoints
track the *VISIBLE ROUND CENTER COVER*, not the offset glass or U-returns.
R03 therefore preserves the 4.75-dia inner wall mounting plate and adds
the 5.5-dia VISIBLE sculpted center face/cap, not a dummy solid. A builder
cannot prove manufacturer's hidden cover/plate construction from photos:
geometry is photo-reconstructed; do not mark an OEM-CAD match.

OTHER PHOTO CORRECTION: R02's hollow transparent glass exposes black bars
and open tube ends in its native oblique PNG; manufacturer's photo shows
closed diffuse etched white tube faces. R03 uses solid photo-appearance
diffusing envelopes, not assertions about physical glass wall thickness.

All inputs and source JPG are SHA256 guarded, and only a new R03 candidate
is saved. NO active RVT, baseline RFA, R02 candidate or global extension
is loaded for write, saved or overwritten. Native Revit is never run here.
"""
from __future__ import print_function
import os
import sys
import math
import hashlib
from System.Collections.Generic import List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from belmont_fixture_core import NativeBuild, xyz

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
MODEL = '53860BK'
RETAILER = 'HIN990485'
PREVIOUS = os.path.join(BASE, 'candidates',
                        'Hinkley_Eos_53860BK_R2025_R02_UNAPPROVED.rfa')
OFFICIAL_IMAGE = os.path.join(BASE, 'scripts',
                              'hinkley_53860bk_r03_official_dim1.jpg')
OUTPUT = os.path.join(BASE, 'candidates',
                      'Hinkley_Eos_53860BK_R2025_R03_UNAPPROVED.rfa')
EXPECTED_SHA = {
    PREVIOUS: '362925c6338b45894b0fff18dc8385c008dd0c83ae76408b1cca485905250618',
    OFFICIAL_IMAGE: '31b6a99bb2666549379e380db35b835f77a4991b0262753227994a7626737977'
}
MANUFACTURER = 'https://www.hinkley.com/53860bk.html'
SPEC = 'https://www.hinkley.com/product_spec_print/download/pdf/product_id/52426/Advanced/1'
PHOTO = 'https://www.hinkley.com/media/catalog/product/2/f/2f013ee2ee5d2d0fc4fbd9688adb2dd6-53860BK_dim1.jpg'
INSTALL = 'https://d1lnz90t7xw0i5.cloudfront.net/Products/files/53860.pdf'

PUBLISHED_IN = (25.0, 5.5, 3.0)
BACKPLATE_D = 4.75
VISIBLE_FACE_D = 5.5
GLASS_LENGTH = 17.5        # Distributor, not explicitly cut-sheet dimensioned
GLASS_DIAMETER = 1.25      # Distributor, not explicitly cut-sheet dimensioned
RAIL_Y = 1.02             # Derived from official front photograph
RAIL_AXIS_Z = 2.375       # 1.25-dia glass reaches physical 3-in extension
RAIL_END_X = 11.34
RETURN_RADIUS = 1.02
STEEL_ROD_R = 0.14
GLASS_R = GLASS_DIAMETER / 2.0
SHADER_METAL_RGB = (24, 24, 25)   # approximate official Black
SHADER_GLASS_RGB = (242, 243, 240) # approximate etched, diffuse white

NOTES = (
  'Hinkley 53860BK Eos, Black painted steel and Etched Glass. Official '
  'dimensions 25W x 5.5H x 3 projection; 4.75 dia mounting backplate. '
  'Official 53860BK dimensioned product photo aligns full 5.5 H to larger '
  'visible round center face. R03 separately models a 4.75 inner wall plate '
  'and a 5.5 visible round center cover. Inner/outer assembly layering and '
  'cover convexity are visually inferred, not manufacturer CAD. Two offset '
  'etched diffusor envelopes are closed/opaque in visual preview to match '
  'official photographed appearance (not physical glass wall thickness). '
  'Both black return-arm U-bends, narrow black tube rails, standoff, and '
  'Invisimount support retained. 17.5 L x 1.25 diameter glass numbers from '
  'distributor, not dimensions on manufacturer sheet. Integrated 19W LED, '
  '3000K, 1000 lm, CRI 93, 120V. No fabricated electrical connector or '
  'unverified IES. Manufacturer detailed text says horizontal only while '
  'marketing/photo elsewhere indicate both; default horizontal, orientation HOLD.'
)

def sha256(path):
    hasher = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            part = stream.read(1024*1024)
            if not part:
                break
            hasher.update(part)
    return hasher.hexdigest()

def preflight():
    if str(APP.VersionNumber) != '2025':
        raise RuntimeError('Revit 2025 is required')
    if getattr(__revit__, 'ActiveUIDocument', None) is not None:
        raise RuntimeError('Requires isolated document-free Revit process')
    if os.path.normcase(os.path.abspath(TARGET_RFA)) != os.path.normcase(OUTPUT):
        raise RuntimeError('Refusing a non-R03 target path: ' + TARGET_RFA)
    if os.path.lexists(OUTPUT):
        raise RuntimeError('R03 output exists: never overwrite ' + OUTPUT)
    for path, expected in EXPECTED_SHA.items():
        if not os.path.isfile(path):
            raise RuntimeError('Evidence/source missing: ' + path)
        actual = sha256(path)
        if actual.lower() != expected.lower():
            raise RuntimeError('Source sha256 mismatch for ' + path + ': ' + actual)
    # Strong shape guard: 5.5 visible steel disk is source-framed;
    # 4.75 mounting plate remains distinct, and tubes do not cause the height.
    if VISIBLE_FACE_D != PUBLISHED_IN[1] or BACKPLATE_D >= VISIBLE_FACE_D:
        raise RuntimeError('Visible cover/backplate dimension authority mismatch')
    if abs(RAIL_AXIS_Z+GLASS_R-PUBLISHED_IN[2]) > 1e-7:
        raise RuntimeError('Physical glass wall projection exceeds 3-inch source')

def circle_yz(x, y, z, radius):
    center = xyz(DB,x,y,z)
    loop = DB.CurveLoop()
    loop.Append(DB.Arc.Create(center,radius/12.0,0,math.pi,
                              DB.XYZ.BasisY, DB.XYZ.BasisZ))
    loop.Append(DB.Arc.Create(center,radius/12.0,math.pi,2*math.pi,
                              DB.XYZ.BasisY, DB.XYZ.BasisZ))
    return loop

def x_cylinder(x0, x1, y, z, radius):
    return DB.GeometryCreationUtilities.CreateExtrusionGeometry(
        List[DB.CurveLoop]([circle_yz(x0,y,z,radius)]),
        DB.XYZ.BasisX,float(x1-x0)/12.0)

def return_arm(side):
    # Steel U-end actually connects both adjacent black tube rails.
    x = float(side) * RAIL_END_X
    a = xyz(DB,x,RAIL_Y,RAIL_AXIS_Z)
    b = xyz(DB,x,-RAIL_Y,RAIL_AXIS_Z)
    apex = xyz(DB,x+side*RETURN_RADIUS,0.0,RAIL_AXIS_Z)
    path = DB.CurveLoop()
    path.Append(DB.Arc.Create(a,b,apex))
    return DB.GeometryCreationUtilities.CreateSweptGeometry(
        path,0,0,List[DB.CurveLoop]([
            circle_yz(x,RAIL_Y,RAIL_AXIS_Z,STEEL_ROD_R)]))

def material_appearance(fixture, parameter, name, rgb, transparency,
                        class_name, generic_gloss):
    """Bind a native Generic Appearance asset, then set basic shaded material.

    Numeric roughness and RGB are visually inferred; STEEL / ETCHED GLASS
    material identities are official source-backed categories.
    This code runs only in the disposable new R03 family transaction.
    """
    db = fixture.DB
    matid = fixture.fm.CurrentType.AsElementId(parameter)
    mat = fixture.doc.GetElement(matid)
    if mat is None:
        raise RuntimeError('Material parameter '+name+' is not bound')
    mat.Name = name
    mat.Color = db.Color(*rgb)
    mat.Transparency = int(round(transparency*100.0))
    mat.MaterialClass = class_name
    base = None
    for asset in fixture.app.GetAssets(db.Visual.AssetType.Appearance):
        try:
            prop = asset.FindByName('BaseSchema')
            if prop is not None and str(prop.Value) == 'GenericSchema':
                base = asset
                break
        except Exception:
            pass
    if base is None:
        raise RuntimeError('GenericSchema Revit appearance asset unavailable')
    appearance = db.AppearanceAssetElement.Create(
        fixture.doc,'HIN 53860BK R03 '+name,base)
    mat.AppearanceAssetId = appearance.Id
    scope = db.Visual.AppearanceAssetEditScope(fixture.doc)
    try:
        edit = scope.Start(appearance.Id)
        def rgb_prop(key):
            prop = edit.FindByName(key)
            if prop is None:
                raise RuntimeError('Missing Generic asset color '+key)
            if prop.NumberOfConnectedProperties:
                prop.RemoveConnectedAsset()
            prop.SetValueAsColor(db.Color(*rgb))
        def scalar(key,value):
            prop = edit.FindByName(key)
            if prop is None:
                raise RuntimeError('Missing Generic asset scalar '+key)
            if prop.NumberOfConnectedProperties:
                prop.RemoveConnectedAsset()
            prop.Value = float(value)
        rgb_prop('generic_diffuse')
        scalar('generic_glossiness', generic_gloss)
        scalar('generic_transparency',transparency)
        scalar('generic_reflectivity_at_0deg',.05 if class_name=='Glass' else .12)
        scalar('generic_reflectivity_at_90deg',.38 if class_name=='Glass' else .25)
        scalar('generic_refraction_index',1.52 if class_name=='Glass' else 1.0)
        scope.Commit(True)
    finally:
        scope.Dispose()
    return mat

def build():
    preflight()
    progress('hinkley_r03_source_guards_pass',{
        'model': MODEL, 'r02_sha256': EXPECTED_SHA[PREVIOUS],
        'official_dimensioned_photo_sha256': EXPECTED_SHA[OFFICIAL_IMAGE]})
    fixture = None
    try:
        fixture = NativeBuild(APP,DB,OUTPUT,MODEL,'Hinkley',
                              'Black / Etched Glass R03','wall',
                              MANUFACTURER,NOTES)
        fixture.text('Hinkley Item',MODEL)
        fixture.text('Lightology SKU',RETAILER)
        fixture.text('Native Appearance Scope','Black steel; opaque etched white visual diffusers')
        fixture.text('Photometry Status','Manufacturer integrated LED 19W 3000K 1000lm CRI93; IES not verified')
        fixture.text('Mounting Orientation Review','Horizontal default; official sources conflict')
        fixture.text('CAD/Fidelity Status','Photo-derived R03; source geometry/face overlay review pending')
        fixture.text('R02 SHA256',EXPECTED_SHA[PREVIOUS])
        fixture.text('Official Photo SHA256',EXPECTED_SHA[OFFICIAL_IMAGE])
        fixture.text('Official Spec PDF URL',SPEC)
        for name,size in (
                ('Overall Width',25.0),
                ('Overall Height',5.5),
                ('Overall Projection',3.0),
                ('Mounting Backplate Diameter',4.75),
                ('Visible Center Cover Diameter',5.5),
                ('Diffuser Length Reference',GLASS_LENGTH),
                ('Diffuser Diameter Reference',GLASS_DIAMETER)):
            fixture.size(name,size)
        black = fixture.material('Black Steel',(24,24,25),0)
        etched = fixture.material('Etched Diffuser',(242,243,240),0)
        material_appearance(fixture,black,'Hinkley Black Painted Steel 53860BK',
                            SHADER_METAL_RGB,0.0,'Metal',.25)
        material_appearance(fixture,etched,'Hinkley Etched Opal Glass 53860BK',
                            SHADER_GLASS_RGB,0.035,'Glass',.12)

        # Physical WALL MOUNT behind cover: exact manufacturer backplate 4.75
        # diameter. Face-based template host plane is Z=0 (wall face).
        fixture.cylinder('Inner 4.75in manufacturer wall mounting backplate',
                         0,0,0.0,BACKPLATE_D/2.0,.18,black)
        # Actual VISIBLE black face disk, not dummy geometry. Official dimensioned
        # photograph shows the vertical 5.5-in arrow from its top to bottom.
        # It is distinct from the concealed 4.75-in electrical attachment.
        fixture.cylinder('Visible 5.5in round black metal front cover',
                         0,0,.18,VISIBLE_FACE_D/2.0,.20,black)
        # Center standoff and saddle dimensions continue R02 photo inference.
        fixture.cylinder('Central concealed steel mounting standoff',
                         0,0,.38,.67,1.65,black)
        fixture.box('Twin bar central steel saddle',
                    (-1.02,-1.12,2.00,1.02,1.12,2.18),black)
        for label,y in (('Upper',RAIL_Y),('Lower',-RAIL_Y)):
            fixture.part(label+' continuous matte steel LED support',
                         x_cylinder(-RAIL_END_X,RAIL_END_X,y,
                                    RAIL_AXIS_Z,STEEL_ROD_R),black)
        fixture.part('Left solid steel rounded U return',return_arm(-1),black)
        fixture.part('Right solid steel rounded U return',return_arm(+1),black)
        # Source image and Hinkley narrative show CLOSED etched tubes. R02
        # open sleeves displayed hollow holes and black rods in preview.
        # Solid surrogate denotes exterior visual diffuser envelope, not
        # inferred literal solid physical glass in manufactured product.
        for label,x0,x1,y in (
                ('Upper closed etched white tube',-10.5,7.0,RAIL_Y),
                ('Lower closed etched white tube',-7.0,10.5,-RAIL_Y)):
            fixture.part(label,
                         x_cylinder(x0,x1,y,RAIL_AXIS_Z,GLASS_R),etched)
        output=fixture.finish()
        dims = output['geometry_dimensions_in']
        err = [abs(float(dims[i])-PUBLISHED_IN[i]) for i in range(3)]
        # This check runs AFTER NativeBuild saves its new R03 candidate.
        # The runner must treat any failure as HOLD, not a pass.
        # Primary whole-part native QA should remeasure after reopening.
        if max(err)>0.0393701:  # 1 mm
            raise RuntimeError('Saved R03 geometry failed 1mm envelope: '
                               +repr(dims)+' vs '+repr(PUBLISHED_IN))
        output.update({
          'source_urls':[MANUFACTURER,SPEC,PHOTO,INSTALL],
          'source_photo_sha256':EXPECTED_SHA[OFFICIAL_IMAGE],
          'r02_sha256':EXPECTED_SHA[PREVIOUS],
          'measured_r03_xyz_in':dims,
          'published_xyz_in':list(PUBLISHED_IN),
          'dimension_delta_abs_in':err,
          'visible_cover_diameter_in':VISIBLE_FACE_D,
          'inner_wall_plate_diameter_in':BACKPLATE_D,
          'glass_surrogate':'Closed exterior etched diffuser envelope (not literal solid glass)',
          'source_part_dimensions':{
             'manufacturer':{'W':25.0,'H':5.5,'projection':3.0,'backplate_d':4.75},
             'photo_derived':{'visible_cover_d':5.5,'rail_y':RAIL_Y,
                              'return_radius':RETURN_RADIUS},
             'distributor':{'glass_length':GLASS_LENGTH,
                            'glass_diameter':GLASS_DIAMETER}
          },
          'visual_source_review':'PENDING_NATIVE_FRONT_OBLIQUE_COMPARISON',
          'geometry_release':'HOLD_PENDING_INDEPENDENT_VISUAL_AND_DIMENSION_QA',
          'photometry':'NO_VALIDATED_IES_OR_ELECTRICAL_CONNECTOR',
          'candidate_version':'R03_UNAPPROVED'})
        result.update(output)
        progress('hinkley_r03_candidate_saved_unapproved',output)
    finally:
        if fixture is not None:
            fixture.close()
    for path,expected in EXPECTED_SHA.items():
        if sha256(path).lower()!=expected:
            raise RuntimeError('Protected source changed after R03 build: '+path)

build()
