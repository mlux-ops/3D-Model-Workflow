# -*- coding: utf-8 -*-
"""Exploration 7: copy the Light Source element from a Lighting Fixture template into the face-based Generic Model family."""
import os
import json
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

OUT = os.path.normpath('E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/high')
BASE = 'C:\\ProgramData\\Autodesk\\RVT 2025\\Family Templates\\English-Imperial\\'
TEMPLATE = BASE + 'Generic Model face based.rft'
TPL_LIGHT = BASE + 'Lighting Fixture wall based.rft'
report = {}
docs = []


def guard(path):
    p = os.path.normpath(path)
    if not p.lower().startswith(OUT.lower() + os.sep):
        raise RuntimeError('write outside run folder refused: ' + p)
    return p


def lightinfo(doc):
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    t = lf.GetLightSourceTransform()
    return {'shape': str(lf.GetLightShapeStyle()), 'dist': str(lf.GetLightDistributionStyle()), 'ntypes': lf.GetNumberOfLightTypes(),
            'origin_in': [round(t.Origin.X * 12, 4), round(t.Origin.Y * 12, 4), round(t.Origin.Z * 12, 4)],
            'basisZ': [round(t.BasisZ.X, 4), round(t.BasisZ.Y, 4), round(t.BasisZ.Z, 4)]}


try:
    app = __revit__.Application
    dst = app.NewFamilyDocument(TEMPLATE)
    docs.append(dst)
    tx = DB.Transaction(dst, 'cat')
    tx.Start()
    dst.OwnerFamily.FamilyCategory = DB.Category.GetCategory(dst, DB.BuiltInCategory.OST_LightingFixtures)
    tx.Commit()
    ps = []
    for p in dst.OwnerFamily.Parameters:
        try:
            v = p.AsValueString() or p.AsString()
        except Exception:
            v = None
        bip = None
        try:
            bip = str(p.Definition.BuiltInParameter)
        except Exception:
            pass
        ps.append([p.Definition.Name, str(p.StorageType), v, p.IsReadOnly, bip])
    report['owner_params_after_cat'] = ps
    tx = DB.Transaction(dst, 'ls')
    tx.Start()
    try:
        for p in dst.OwnerFamily.Parameters:
            if p.Definition.Name == 'Light Source':
                report['ls_before'] = p.AsInteger()
                report['ls_set'] = p.Set(1)
    except Exception:
        report['ls_err'] = traceback.format_exc()
    tx.Commit()
    report['dst_light_sources'] = [[str(e.Id.IntegerValue), e.GetType().Name] for e in DB.FilteredElementCollector(dst).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource)]
    try:
        report['dst_light'] = lightinfo(dst)
    except Exception:
        report['dst_light_err'] = traceback.format_exc()
    report['placement'] = str(dst.OwnerFamily.FamilyPlacementType)
    report['stage'] = 'done'
except Exception:
    report['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
with open(guard(os.path.join(OUT, '_work', 'explore10.json')), 'w') as f:
    json.dump(report, f, indent=1, default=str)
