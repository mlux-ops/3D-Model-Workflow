# -*- coding: utf-8 -*-
"""Exploration 8 (pyRevit): what makes the exported family views show a huge grey slab? Lists elements visible in each saved view."""
import sys
import traceback
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/source')
from guard import dump_json
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

RUN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/'
rep = {}
docs = []
try:
    app = __revit__.Application
    doc = app.OpenDocumentFile(RUN + 'Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa')
    docs.append(doc)
    views = [v for v in DB.FilteredElementCollector(doc).OfClass(DB.View3D) if not v.IsTemplate]
    for v in views:
        e = {'section_active': v.IsSectionBoxActive}
        try:
            sb = v.GetSectionBox()
            e['section_box_in'] = [round(c * 12, 3) for c in (sb.Min.X, sb.Min.Y, sb.Min.Z, sb.Max.X, sb.Max.Y, sb.Max.Z)]
        except Exception as ex:
            e['section_err'] = str(ex)[:100]
        items = []
        for el in DB.FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType():
            cat = el.Category.Name if el.Category is not None else None
            bb = el.get_BoundingBox(None)
            items.append([str(el.Id.Value), el.GetType().Name, cat, [round(c * 12, 2) for c in (bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z)] if bb else None])
        e['visible'] = items
        rep[v.Name] = e
    cats = {}
    for el in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        c = el.Category.Name if el.Category is not None else 'None'
        cats[c] = cats.get(c, 0) + 1
    rep['all_categories'] = cats
except Exception:
    rep['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
    rep['done'] = True
    dump_json(rep, RUN + 'work/explore8.json')
