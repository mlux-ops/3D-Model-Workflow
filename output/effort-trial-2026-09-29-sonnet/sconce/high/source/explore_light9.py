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
    for tname in ['Lighting Fixture.rft']:
        d = app.NewFamilyDocument(BASE + tname)
        docs.append(d)
        r = {}
        r['cat'] = d.OwnerFamily.FamilyCategory.Name
        r['placement'] = str(d.OwnerFamily.FamilyPlacementType)
        ps = []
        for p in d.OwnerFamily.Parameters:
            try:
                v = p.AsValueString() or p.AsString()
            except Exception:
                v = None
            ps.append([p.Definition.Name, str(p.StorageType), v, p.IsReadOnly])
        r['owner_params'] = ps
        r['light'] = lightinfo(d)
        r['elems'] = [[str(e.Id.IntegerValue), e.GetType().Name, (e.Category.Name if e.Category else None)] for e in DB.FilteredElementCollector(d).WhereElementIsNotElementType() if e.Category is not None and e.Category.Name in ('Light Source', 'Reference Planes', 'Constraints', 'Levels', 'Walls')]
        tx = DB.Transaction(d, 'wp')
        tx.Start()
        try:
            p = d.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED)
            r['wp_param'] = None if p is None else [str(p.StorageType), p.AsInteger(), p.IsReadOnly]
            if p is not None:
                r['wp_set'] = p.Set(1)
        except Exception:
            r['wp_err'] = traceback.format_exc()
        tx.Commit()
        r['placement_after'] = str(d.OwnerFamily.FamilyPlacementType)
        try:
            r['light_after'] = lightinfo(d)
        except Exception:
            r['light_after'] = traceback.format_exc()
        r['elems_after'] = [[str(e.Id.IntegerValue), e.GetType().Name, (e.Category.Name if e.Category else None)] for e in DB.FilteredElementCollector(d).WhereElementIsNotElementType() if e.Category is not None and e.Category.Name in ('Light Source', 'Reference Planes', 'Constraints', 'Levels', 'Walls')]
        report[tname] = r
    report['stage'] = 'done'
except Exception:
    report['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
with open(guard(os.path.join(OUT, '_work', 'explore9.json')), 'w') as f:
    json.dump(report, f, indent=1, default=str)
