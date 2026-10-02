# -*- coding: utf-8 -*-
"""Exploration: size of the Light Source proxy geometry per light shape, and which light-source parameters could shrink it."""
import os
import json
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

OUT = os.path.normpath('E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/high')
RFA = OUT + '/Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa'
report = {}
docs = []


def guard(path):
    p = os.path.normpath(path)
    if not p.lower().startswith(OUT.lower() + os.sep):
        raise RuntimeError('write outside run folder refused: ' + p)
    return p


def ext_of(doc, el):
    opt = DB.Options()
    opt.DetailLevel = DB.ViewDetailLevel.Fine
    res = []
    g = el.get_Geometry(opt)
    if g is None:
        return None
    for item in g:
        res.append(item.GetType().Name)
        if isinstance(item, DB.GeometryInstance):
            for it2 in item.GetInstanceGeometry():
                res.append('  ' + it2.GetType().Name)
        if isinstance(item, DB.Solid):
            bb = item.GetBoundingBox()
            res.append('  bbox %s %s' % (bb.Min, bb.Max))
    bb = el.get_BoundingBox(None)
    if bb:
        res.append('elbbox in ' + str([round(v * 12, 3) for v in (bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z)]))
    return res


try:
    app = __revit__.Application
    doc = app.OpenDocumentFile(RFA)
    docs.append(doc)
    el = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource))[0]
    params = []
    for p in el.Parameters:
        try:
            v = p.AsValueString() or p.AsString()
        except Exception:
            v = None
        params.append([p.Definition.Name, str(p.StorageType), v, p.IsReadOnly])
    report['source_params'] = params
    report['geometry_point'] = ext_of(doc, el)
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    for shape in ['Circle', 'Rectangle', 'Line']:
        tx = DB.Transaction(doc, 'shape ' + shape)
        tx.Start()
        try:
            lf = DB.Lighting.LightFamily.GetLightFamily(doc)
            lf.SetLightShapeStyle(getattr(DB.Lighting.LightShapeStyle, shape))
            tx.Commit()
        except Exception:
            report['set_' + shape] = traceback.format_exc()
            tx.RollBack()
        el = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource))[0]
        report['geometry_' + shape] = ext_of(doc, el)
        report['params_' + shape] = [[p.Definition.Name, (p.AsValueString() or p.AsString())] for p in el.Parameters if not p.IsReadOnly][:20]
    report['stage'] = 'done'
except Exception:
    report['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
with open(guard(os.path.join(OUT, '_work', 'explore_proxy.json')), 'w') as f:
    json.dump(report, f, indent=1, default=str)
