# -*- coding: utf-8 -*-
"""Exploration 1 (pyRevit / IronPython 2.7): template contents, light-source element after the category change."""
import sys
import json
import traceback
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/source')
from guard import safe_open
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RUN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/'
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
rep = {}
docs = []


def save():
    f = safe_open(RUN + 'work/explore1.json', 'w')
    json.dump(rep, f, indent=2, default=str)
    f.close()


def pinfo(p):
    d = {'name': p.Definition.Name, 'storage': str(p.StorageType), 'ro': p.IsReadOnly}
    try:
        if p.StorageType == DB.StorageType.Double:
            d['value'] = p.AsDouble()
        elif p.StorageType == DB.StorageType.Integer:
            d['value'] = p.AsInteger()
        elif p.StorageType == DB.StorageType.String:
            d['value'] = p.AsString()
        elif p.StorageType == DB.StorageType.ElementId:
            d['value'] = str(p.AsElementId().Value)
        d['vs'] = p.AsValueString()
    except Exception as e:
        d['err'] = str(e)
    try:
        d['bip'] = str(p.Definition.BuiltInParameter)
    except Exception:
        pass
    return d


tx = None
try:
    app = __revit__.Application
    rep['version'] = app.VersionNumber
    rep['build'] = app.VersionBuild
    doc = app.NewFamilyDocument(TEMPLATE)
    docs.append(doc)
    fam = doc.OwnerFamily
    rep['template_category'] = fam.FamilyCategory.Name
    rep['placement_type'] = str(fam.FamilyPlacementType)
    rep['ref_planes'] = []
    for rp in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane):
        rep['ref_planes'].append({'name': rp.Name, 'bubble': [rp.BubbleEnd.X, rp.BubbleEnd.Y, rp.BubbleEnd.Z],
                                  'free': [rp.FreeEnd.X, rp.FreeEnd.Y, rp.FreeEnd.Z],
                                  'normal': [rp.Normal.X, rp.Normal.Y, rp.Normal.Z],
                                  'isref': str(rp.get_Parameter(DB.BuiltInParameter.ELEM_REFERENCE_NAME).AsValueString()) if rp.get_Parameter(DB.BuiltInParameter.ELEM_REFERENCE_NAME) else None})
    rep['views'] = [[v.Name, str(v.ViewType)] for v in DB.FilteredElementCollector(doc).OfClass(DB.View) if not v.IsTemplate]
    rep['before_params'] = [p.Definition.Name for p in doc.FamilyManager.Parameters]
    allels = []
    for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        if e.Category is not None and e.GetType().Name not in ('GraphicsStyle',):
            allels.append([e.GetType().Name, e.Category.Name, str(e.Id.Value)])
    rep['template_elements'] = allels
    rep['lightish_bips'] = [n for n in dir(DB.BuiltInParameter) if 'LIGHT' in n or 'LUMIN' in n or 'FBX' in n]
    rep['lightish_bics'] = [n for n in dir(DB.BuiltInCategory) if 'OST_Light' in n]
    save()

    tx = DB.Transaction(doc, 'explore')
    tx.Start()
    fam.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_LightingFixtures)
    tx.Commit()
    tx = None
    rep['category_now'] = fam.FamilyCategory.Name
    rep['params_after_category'] = [[p.Definition.Name, str(p.StorageType)] for p in doc.FamilyManager.Parameters]
    # every element, incl. light source
    allels2 = []
    for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        if e.Category is not None and e.GetType().Name not in ('GraphicsStyle',):
            allels2.append([e.GetType().Name, e.Category.Name, str(e.Id.Value)])
    rep['elements_after_category'] = allels2
    src = []
    for bic in ('OST_LightingFixtureSource',):
        try:
            cat = DB.Category.GetCategory(doc, getattr(DB.BuiltInCategory, bic))
            rep['source_cat'] = [cat.Name, cat.Id.Value] if cat else None
            for e in DB.FilteredElementCollector(doc).OfCategory(getattr(DB.BuiltInCategory, bic)):
                entry = {'class': e.GetType().Name, 'id': str(e.Id.Value), 'params': [pinfo(p) for p in e.Parameters]}
                bb = e.get_BoundingBox(None)
                if bb:
                    entry['bbox'] = [bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z]
                loc = e.Location
                entry['loc'] = str(type(loc).__name__)
                if isinstance(loc, DB.LocationPoint):
                    entry['pt'] = [loc.Point.X, loc.Point.Y, loc.Point.Z]
                src.append(entry)
        except Exception:
            rep['src_err_' + bic] = traceback.format_exc()
    rep['light_sources'] = src
    # family-level params on the category dialog (owner family)
    rep['family_params'] = [pinfo(p) for p in fam.Parameters]
    # subcategories of Lighting Fixtures
    rep['subcats'] = [c.Name for c in fam.FamilyCategory.SubCategories]
    save()

    # visibility parameter on a freeform solid
    tx = DB.Transaction(doc, 'explore2')
    tx.Start()
    loop = DB.CurveLoop()
    pts = [DB.XYZ(0, 0, 0), DB.XYZ(.1, 0, 0), DB.XYZ(.1, .1, 0), DB.XYZ(0, .1, 0)]
    for i in range(4):
        loop.Append(DB.Line.CreateBound(pts[i], pts[(i + 1) % 4]))
    solid = DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]), DB.XYZ.BasisZ, .1)
    ff = DB.FreeFormElement.Create(doc, solid)
    rep['ff_params'] = [pinfo(p) for p in ff.Parameters]
    rep['ff_visible_prop'] = str(ff.Visible) if hasattr(ff, 'Visible') else 'no Visible prop'
    p = ff.get_Parameter(DB.BuiltInParameter.IS_VISIBLE_PARAM)
    rep['ff_IS_VISIBLE_PARAM'] = None if p is None else pinfo(p)
    tx.RollBack()
    tx = None
    save()
except Exception:
    rep['error'] = traceback.format_exc()
    save()
finally:
    if tx:
        try:
            tx.RollBack()
        except Exception:
            pass
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
    rep['done'] = True
    save()
