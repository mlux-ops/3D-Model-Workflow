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
    src = app.NewFamilyDocument(TPL_LIGHT)
    docs.append(src)
    ids = [e.Id for e in DB.FilteredElementCollector(src).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource)]
    report['src_ids'] = [str(i.IntegerValue) for i in ids]
    dst = app.NewFamilyDocument(TEMPLATE)
    docs.append(dst)
    tx = DB.Transaction(dst, 'cat+light')
    tx.Start()
    dst.OwnerFamily.FamilyCategory = DB.Category.GetCategory(dst, DB.BuiltInCategory.OST_LightingFixtures)
    tx.Commit()
    tx = DB.Transaction(dst, 'copy light')
    tx.Start()
    try:
        opts = DB.CopyPasteOptions()
        copied = DB.ElementTransformUtils.CopyElements(src, List[DB.ElementId](ids), dst, DB.Transform.Identity, opts)
        report['copied'] = [str(i.IntegerValue) for i in copied]
        tx.Commit()
    except Exception:
        report['copy_err'] = traceback.format_exc()
        tx.RollBack()
    dst.Regenerate()
    report['dst_light_sources'] = [[str(e.Id.IntegerValue), e.GetType().Name] for e in DB.FilteredElementCollector(dst).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource)]
    try:
        report['dst_light'] = lightinfo(dst)
    except Exception:
        report['dst_light_err'] = traceback.format_exc()
    # inspect source element parameters
    e = src.GetElement(ids[0])
    ps = []
    for p in e.Parameters:
        try:
            v = p.AsValueString()
        except Exception:
            v = None
        ps.append([p.Definition.Name, str(p.StorageType), v, p.IsReadOnly])
    report['src_params'] = ps
    try:
        bb = e.get_BoundingBox(None)
        report['src_bbox_in'] = [[bb.Min.X * 12, bb.Min.Y * 12, bb.Min.Z * 12], [bb.Max.X * 12, bb.Max.Y * 12, bb.Max.Z * 12]]
    except Exception as ex:
        report['src_bbox_err'] = str(ex)
    report['src_loc'] = str(e.Location)
    try:
        report['src_loc_pt'] = [e.Location.Point.X * 12, e.Location.Point.Y * 12, e.Location.Point.Z * 12]
    except Exception as ex:
        report['src_loc_pt_err'] = str(ex)
    report['stage'] = 'done'
except Exception:
    report['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
with open(guard(os.path.join(OUT, '_work', 'explore7.json')), 'w') as f:
    json.dump(report, f, indent=1, default=str)
