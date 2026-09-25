# -*- coding: utf-8 -*-
"""Build/validate F10 Covet KW 4115AB-ALB as an independent Revit 2025 face-based family."""
import os, sys, json
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = r'E:\Claude\3D-Model-Workflow'
OUT = os.path.join(ROOT, 'output', 'lightology_20260923', 'f10_1242580')
SRC = os.path.join(OUT, 'source')
TOOLS = os.path.join(ROOT, 'output', 'lightology_20260923', 'tools')
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
from native_fixture_support import NativeFixture, xyz, all_solids

MODEL = 'KW 4115AB-ALB'
BASENAME = 'VisualComfort_Covet_KW4115AB-ALB_AntiqueBurnishedBrass_Alabaster_R2025'
SOURCE_RFA = os.path.join(SRC, 'visualcomfort_kw4115_reference.rfa')
TEXTURE = os.path.join(SRC, 'covet_alabaster_diffuse.jpg')
REPORT_EXTRA = os.path.join(OUT, 'source_rfa_inspection.json')

def rect_loop(z, half):
    loop = DB.CurveLoop()
    pts = [xyz(-half,-half,z), xyz(half,-half,z), xyz(half,half,z), xyz(-half,half,z)]
    for a,b in zip(pts, pts[1:]+pts[:1]):
        loop.Append(DB.Line.CreateBound(a,b))
    return loop

def loft_square(z0, half0, z1, half1):
    loops = List[DB.CurveLoop]()
    loops.Add(rect_loop(z0, half0))
    loops.Add(rect_loop(z1, half1))
    return DB.GeometryCreationUtilities.CreateLoftGeometry(
        loops, DB.SolidOptions(DB.ElementId.InvalidElementId, DB.ElementId.InvalidElementId))

def inspect_source(app):
    rec = {'path':SOURCE_RFA, 'exists':os.path.isfile(SOURCE_RFA)}
    if not rec['exists']:
        with open(REPORT_EXTRA,'w') as s:
            json.dump(rec,s,indent=2)
        return rec
    doc = app.OpenDocumentFile(SOURCE_RFA)
    try:
        rec['title'] = doc.Title
        rec['is_family'] = doc.IsFamilyDocument
        rec['category'] = doc.OwnerFamily.FamilyCategory.Name if doc.IsFamilyDocument else None
        rec['placement'] = str(doc.OwnerFamily.FamilyPlacementType) if doc.IsFamilyDocument else None
        rec['warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
        opt = DB.Options()
        opt.DetailLevel = DB.ViewDetailLevel.Fine
        opt.IncludeNonVisibleObjects = True
        rows = []
        for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
            try:
                g = e.get_Geometry(opt)
            except Exception:
                continue
            for s in all_solids(g):
                b = s.GetBoundingBox()
                rows.append({
                    'element_id':str(e.Id.Value),
                    'category':e.Category.Name if e.Category else None,
                    'bbox_local_ft':[b.Min.X,b.Min.Y,b.Min.Z,b.Max.X,b.Max.Y,b.Max.Z],
                    'volume_ft3':s.Volume})
        rec['solid_count'] = len(rows)
        rec['solid_samples'] = rows[:120]
        if rows:
            rec['aggregate_local_bbox_ft'] = [
                min(r['bbox_local_ft'][0] for r in rows),
                min(r['bbox_local_ft'][1] for r in rows),
                min(r['bbox_local_ft'][2] for r in rows),
                max(r['bbox_local_ft'][3] for r in rows),
                max(r['bbox_local_ft'][4] for r in rows),
                max(r['bbox_local_ft'][5] for r in rows)]
    finally:
        doc.Close(False)
    with open(REPORT_EXTRA,'w') as s:
        json.dump(rec,s,indent=2)
    return rec

def bind_bitmap(doc, material, path):
    appearance = doc.GetElement(material.AppearanceAssetId)
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    asset = scope.Start(appearance.Id)
    prop = asset.FindByName('generic_diffuse')
    if prop is None:
        scope.Cancel()
        raise RuntimeError('generic_diffuse property missing for alabaster material')
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.AddConnectedAsset('UnifiedBitmap')
    bitmap = prop.GetSingleConnectedAsset()
    bitmap.FindByName('unifiedbitmap_Bitmap').Value = path
    fade = asset.FindByName('generic_diffuse_image_fade')
    if fade is not None:
        fade.Value = 1.0
    for key, val in [('texture_RealWorldScaleX',18.25/12.0),
                     ('texture_RealWorldScaleY',18.25/12.0)]:
        p = bitmap.FindByName(key)
        if p is not None:
            try:
                p.Value = val
            except Exception:
                pass
    glow=asset.FindByName('generic_self_illum_filter_map')
    if glow.NumberOfConnectedProperties:glow.RemoveConnectedAsset()
    glow.AddConnectedAsset('UnifiedBitmap')
    luminous=glow.GetSingleConnectedAsset()
    luminous.FindByName('unifiedbitmap_Bitmap').Value=path
    for key in ['texture_RealWorldScaleX','texture_RealWorldScaleY']:
        prop=luminous.FindByName(key)
        if prop is not None:prop.Value=18.25/12.0
    scope.Commit(True)
    scope.Dispose()

def inspect_saved_alabaster_texture(app, rfa_path):
    doc = app.OpenDocumentFile(rfa_path)
    try:
        target = None
        for mat in DB.FilteredElementCollector(doc).OfClass(DB.Material):
            try:
                name = DB.Element.Name.GetValue(mat)
            except Exception:
                name = ''
            if name.endswith(' Natural Alabaster'):
                target = mat
                break
        if target is None:
            return {'material_found':False,'texture_path':None,'texture_exists':False}
        appearance = doc.GetElement(target.AppearanceAssetId)
        asset = appearance.GetRenderingAsset()
        diffuse = asset.FindByName('generic_diffuse')
        texture_path = None
        if diffuse is not None and diffuse.NumberOfConnectedProperties:
            bitmap = diffuse.GetSingleConnectedAsset()
            if bitmap is not None:
                prop = bitmap.FindByName('unifiedbitmap_Bitmap')
                if prop is not None:
                    texture_path = str(prop.Value)
        return {'material_found':True,'material_name':DB.Element.Name.GetValue(target),
                'texture_path':texture_path,'texture_exists':bool(texture_path and os.path.isfile(texture_path))}
    finally:
        doc.Close(False)

app = __revit__.Application
if not os.path.isfile(TEXTURE):
    raise RuntimeError('Required alabaster companion texture missing: '+TEXTURE)
source = inspect_source(app)

f = None
try:
    f = NativeFixture(
        app, OUT, BASENAME, 'Visual Comfort Signature / Kelly Wearstler',
        MODEL, 'Antique-Burnished Brass - Alabaster - 2700K',
        'ceiling', [18.25,18.25,2.75], 2700)

    brass = f.material(
        'Antique-Burnished Brass', (173,125,58),
        gloss=.58, transparency=0, reflectivity=.48, material_class='Metal')
    alabaster = f.material(
        'Natural Alabaster', (238,231,216),
        gloss=.20, transparency=0.0, reflectivity=.04,
        emission=35, cct=2700, material_class='Stone')
    bind_bitmap(f.doc, f.materials['Natural Alabaster'], TEXTURE)

    f.box('Brass ceiling canopy', -8.625,-8.625,0.0, 8.625,8.625,0.50, brass, rounding=.08)

    # Exact option imagery and manufacturer-reference bounds show the ceiling-side stone edge
    # is the widest portion, with a narrower exposed underside.
    stone = loft_square(0.50, 9.125, 2.75, 8.75)
    f.add('Tapered alabaster body', stone, alabaster)

    # Two large opposite-side brass retainers. Manufacturer reference RFA contains two
    # solids approximately 1.60 in x 3.02 in x 11.01 in; the exact option photo shows
    # these as the two prominent side retainers. They span the overall drop and seat into/overlap both canopy and stone body.
    retainer_w = 1.60
    retainer_len = 11.00
    f.box('East brass retainer', 7.525,-retainer_len/2,0.00, 9.125,retainer_len/2,2.75, brass, rounding=.04)
    f.box('West brass retainer', -9.125,-retainer_len/2,0.00, -7.525,retainer_len/2,2.75, brass, rounding=.04)

    f.note('Printed selection: KW 4115AB-ALB, Antique-Burnished Brass / Alabaster, 18.25 in overall width, 2.75 in selected-option height, 17.25 in canopy, 2700K. Stone taper direction is photo/drawing-derived; two brass retainer dimensions are informed by native manufacturer-reference solid bounds and exact option photography. Companion alabaster bitmap is cropped from the exact Lightology option photograph; natural-stone variation is expected.')
    f.report['lightology_url'] = 'https://www.lightology.com/index.php?module=prod_detail&prod_id=1242580&option_id=1242586'
    f.report['lightology_spec'] = 'VCG1242586'
    f.report['selected_option'] = {
        'model':MODEL,'finish':'Antique-Burnished Brass','color':'Alabaster',
        'width_in':18.25,'height_in':2.75,'canopy_in':17.25,
        'cct_k':2700,'watts':50,'lumens':4000}
    f.report['companion_texture'] = {
        'path':TEXTURE,'exists':os.path.isfile(TEXTURE),
        'source':'crop of exact Lightology option image 1242586.jpg'}
    f.report['manufacturer_reference_rfa'] = source

    report = f.finish()
    if not report.get('technical_pass'):
        raise RuntimeError('Native support returned technical_pass false')
    report['saved_alabaster_texture_readback'] = inspect_saved_alabaster_texture(app, report['rfa_path'])
    if not report['saved_alabaster_texture_readback'].get('texture_exists'):
        report['technical_pass'] = False
        with open(os.path.join(OUT, BASENAME+'_validation.json'),'w') as stream:
            json.dump(report,stream,indent=2,default=str)
        raise RuntimeError('Saved alabaster diffuse texture did not resolve on RFA reopen')
    with open(os.path.join(OUT, BASENAME+'_validation.json'),'w') as stream:
        json.dump(report,stream,indent=2,default=str)
except Exception:
    if f is not None:
        f.fail()
    raise

