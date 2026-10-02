# -*- coding: utf-8 -*-
"""Exploration: what is the large slab (template Extrusion) in the face-based template, and does it belong to the built family?"""
import os
import json
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

OUT = os.path.normpath('E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/high')
report = {}
docs = []


def guard(path):
    p = os.path.normpath(path)
    if not p.lower().startswith(OUT.lower() + os.sep):
        raise RuntimeError('write outside run folder refused: ' + p)
    return p


def describe(doc, e):
    d = {'id': e.Id.IntegerValue, 'type': e.GetType().Name}
    try:
        d['category'] = e.Category.Name if e.Category else None
    except Exception as ex:
        d['category_err'] = str(ex)
    try:
        d['subcategory'] = e.Subcategory.Name if e.Subcategory else None
    except Exception:
        pass
    try:
        bb = e.get_BoundingBox(None)
        d['bbox_in'] = [[round(v * 12, 3) for v in (bb.Min.X, bb.Min.Y, bb.Min.Z)], [round(v * 12, 3) for v in (bb.Max.X, bb.Max.Y, bb.Max.Z)]]
    except Exception as ex:
        d['bbox_err'] = str(ex)
    try:
        d['is_solid'] = e.IsSolid
        p = e.get_Parameter(DB.BuiltInParameter.IS_VISIBLE_PARAM)
        d['visible_param'] = p.AsInteger() if p else None
    except Exception:
        pass
    return d


try:
    from System.Collections.Generic import List
    app = __revit__.Application
    tpl = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
    doc = app.NewFamilyDocument(tpl)
    docs.append(doc)
    report['template'] = [describe(doc, e) for e in DB.FilteredElementCollector(doc).OfClass(DB.Extrusion)]
    rfa = OUT + '/Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa'
    fdoc = app.OpenDocumentFile(rfa)
    docs.append(fdoc)
    report['rfa_extrusions'] = [describe(fdoc, e) for e in DB.FilteredElementCollector(fdoc).OfClass(DB.Extrusion)]
    report['rfa_freeforms'] = [describe(fdoc, e) for e in DB.FilteredElementCollector(fdoc).OfClass(DB.FreeFormElement)]
    opt = DB.Options()
    opt.DetailLevel = DB.ViewDetailLevel.Fine
    sol = []
    for e in DB.FilteredElementCollector(fdoc).WhereElementIsNotElementType():
        try:
            if isinstance(e, (DB.Extrusion, DB.FreeFormElement)):
                g = e.get_Geometry(opt)
                n = 0
                for item in g:
                    if isinstance(item, DB.Solid) and item.Volume > 0:
                        n += 1
                sol.append([e.Id.IntegerValue, e.GetType().Name, n])
        except Exception as ex:
            sol.append([e.Id.IntegerValue, str(ex)])
    report['solid_elements'] = sol
    report['stage'] = 'done'
except Exception:
    report['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
with open(guard(os.path.join(OUT, '_work', 'explore_slab.json')), 'w') as f:
    json.dump(report, f, indent=1, default=str)
