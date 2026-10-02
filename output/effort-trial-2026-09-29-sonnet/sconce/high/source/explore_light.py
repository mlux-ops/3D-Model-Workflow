# -*- coding: utf-8 -*-
"""Exploration: what does a Lighting Fixtures face-based family document expose for its light source?"""
import os
import json
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

OUT = os.path.normpath('E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/high')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
report = {}
docs = []


def guard(path):
    p = os.path.normpath(path)
    if not p.lower().startswith(OUT.lower() + os.sep):
        raise RuntimeError('write outside run folder refused: ' + p)
    return p


def checkpoint(stage):
    report['stage'] = stage
    with open(guard(os.path.join(OUT, '_work', 'explore.json')), 'w') as f:
        json.dump(report, f, indent=2, default=str)


def describe(doc, e):
    d = {'id': str(e.Id.IntegerValue), 'class': e.GetType().Name}
    try:
        d['cat'] = e.Category.Name if e.Category else None
    except Exception as ex:
        d['cat'] = 'err ' + str(ex)
    params = []
    try:
        for p in e.Parameters:
            try:
                val = p.AsValueString() or p.AsString() or (str(p.AsDouble()) if p.StorageType == DB.StorageType.Double else str(p.AsInteger()) if p.StorageType == DB.StorageType.Integer else str(p.AsElementId().IntegerValue))
            except Exception:
                val = '?'
            params.append([p.Definition.Name, str(p.StorageType), val, p.IsReadOnly])
    except Exception as ex:
        params = ['err ' + str(ex)]
    d['params'] = params
    return d


try:
    app = __revit__.Application
    report['version'] = app.VersionNumber
    doc = app.NewFamilyDocument(TEMPLATE)
    docs.append(doc)
    tx = DB.Transaction(doc, 'explore')
    tx.Start()
    doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_LightingFixtures)
    doc.Regenerate()
    checkpoint('category set')
    els = []
    for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        try:
            cname = e.Category.Name if e.Category else None
        except Exception:
            cname = None
        els.append([str(e.Id.IntegerValue), e.GetType().Name, cname])
    report['elements'] = els
    checkpoint('elements listed')
    try:
        ls = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource).WhereElementIsNotElementType())
        report['light_sources'] = [describe(doc, e) for e in ls]
    except Exception as ex:
        report['light_sources_err'] = traceback.format_exc()
    fm = doc.FamilyManager
    report['fm_params'] = [[p.Definition.Name, str(p.StorageType), p.IsInstance] for p in fm.Parameters]
    report['placement'] = str(doc.OwnerFamily.FamilyPlacementType)
    # reference planes
    report['ref_planes'] = [[e.Name, str(e.BubbleEnd), str(e.FreeEnd), str(e.Normal)] for e in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane)]
    tx.RollBack()
    checkpoint('done')
except Exception:
    report['error'] = traceback.format_exc()
    checkpoint('failed')
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
