# -*- coding: utf-8 -*-
"""Probe: what does a face-based family look like after its category becomes Lighting Fixtures?
Lists elements, family parameters and light-source parameters. Writes _work/probe_light.json.
"""
import sys
import json
import traceback
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

OUT = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/_work/probe_light.json"
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
report = {'stage': 'start'}


def dump():
    with open(safe(OUT), 'w') as f:
        json.dump(report, f, indent=1, default=str)


def pinfo(p):
    d = {'name': p.Definition.Name, 'storage': str(p.StorageType), 'ro': p.IsReadOnly}
    try:
        d['bip'] = str(p.Definition.BuiltInParameter)
    except Exception:
        pass
    try:
        if p.StorageType == DB.StorageType.String:
            d['value'] = p.AsString()
        elif p.StorageType == DB.StorageType.Double:
            d['value'] = p.AsDouble()
            d['vstr'] = p.AsValueString()
        elif p.StorageType == DB.StorageType.Integer:
            d['value'] = p.AsInteger()
            d['vstr'] = p.AsValueString()
        else:
            d['value'] = str(p.AsElementId().Value)
    except Exception as e:
        d['err'] = str(e)
    return d


doc = None
try:
    app = __revit__.Application
    report['revit'] = app.VersionNumber + ' ' + app.VersionBuild
    doc = app.NewFamilyDocument(TEMPLATE)
    report['title'] = doc.Title
    t = DB.Transaction(doc, 'category')
    t.Start()
    doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_LightingFixtures)
    t.Commit()
    doc.Regenerate()
    report['category'] = doc.OwnerFamily.FamilyCategory.Name
    report['placement'] = str(doc.OwnerFamily.FamilyPlacementType)
    report['stage'] = 'category set'
    dump()

    els = []
    for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        cat = e.Category.Name if e.Category else None
        els.append({'id': str(e.Id.Value), 'cls': e.GetType().Name, 'cat': cat, 'name': e.Name})
    report['elements'] = els
    dump()

    fm = doc.FamilyManager
    report['fam_params'] = []
    for p in fm.Parameters:
        try:
            report['fam_params'].append({'name': p.Definition.Name, 'inst': p.IsInstance,
                                         'group': str(p.Definition.ParameterGroup), 'ro': p.IsReadOnly})
        except Exception as e:
            report['fam_params'].append({'err': str(e)})
    report['types'] = [tt.Name for tt in fm.Types]
    dump()

    report['light'] = []
    for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        cat = e.Category.Name if e.Category else ''
        if 'Light' in cat or 'Light' in e.GetType().Name:
            item = {'id': str(e.Id.Value), 'cls': e.GetType().Name, 'cat': cat, 'params': []}
            try:
                bb = e.get_BoundingBox(None)
                item['bbox_in'] = [round(v * 12, 4) for v in (bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z)] if bb else None
            except Exception as ex:
                item['bbox_err'] = str(ex)
            try:
                loc = e.Location
                item['loc'] = str(type(loc).__name__)
                if hasattr(loc, 'Point'):
                    item['pt_in'] = [round(v * 12, 4) for v in (loc.Point.X, loc.Point.Y, loc.Point.Z)]
            except Exception as ex:
                item['loc_err'] = str(ex)
            for p in e.Parameters:
                item['params'].append(pinfo(p))
            # type parameters
            try:
                et = doc.GetElement(e.GetTypeId())
                if et is not None:
                    item['type_params'] = [pinfo(p) for p in et.Parameters]
            except Exception as ex:
                item['type_err'] = str(ex)
            report['light'].append(item)
    report['stage'] = 'probed light'
    dump()

    # try to find the light source through the subcategory
    try:
        cat = doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_LightingFixtures)
        report['subcats'] = [c.Name for c in cat.SubCategories]
    except Exception as ex:
        report['subcats_err'] = str(ex)
    try:
        cid = DB.ElementId(DB.BuiltInCategory.OST_LightingFixtureSource)
        report['fixture_source_elements'] = [str(e.Id.Value) for e in DB.FilteredElementCollector(doc).OfCategoryId(cid)]
    except Exception as ex:
        report['fixture_source_err'] = str(ex)
    report['stage'] = 'done'
except Exception:
    report['error'] = traceback.format_exc()
finally:
    try:
        if doc is not None:
            doc.Close(False)
    except Exception:
        report['close_error'] = traceback.format_exc()
    dump()
