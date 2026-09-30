# -*- coding: utf-8 -*-
"""Void vs profile X extents inside the wall-unit family, and reference plane positions."""
import json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
RUN = 'E:/Claude/3D-Model-Workflow/output/gola_wall_unit'
out = {}
def save():
    with open(RUN + '/logs/probe_void_x.json', 'w') as f: json.dump(out, f, indent=2, default=str)
try:
    app = __revit__.Application
    doc = app.OpenDocumentFile(RUN + '/Richelieu_Gola_Wall_Unit_Upper_Cabinet_2025.rfa')
    fm = doc.FamilyManager
    out['length_mm'] = fm.CurrentType.AsDouble(next(p for p in fm.Parameters if p.Definition.Name == 'Length')) * 304.8
    out['forms'] = []
    for e in DB.FilteredElementCollector(doc).OfClass(DB.GenericForm):
        b = e.get_BoundingBox(None)
        sk = []
        if isinstance(e, DB.Extrusion):
            for ca in e.Sketch.Profile:
                for c in ca: sk.append([round(c.GetEndPoint(0).X * 304.8, 3), round(c.GetEndPoint(1).X * 304.8, 3)])
        out['forms'].append({'id': e.Id.Value, 'solid': e.IsSolid, 'bbox_x': [round(b.Min.X * 304.8, 3), round(b.Max.X * 304.8, 3)],
                             'sketch_x': sk})
    out['planes'] = [[r.Name, round(r.GetPlane().Origin.X * 304.8, 3), [round(v, 3) for v in (r.GetPlane().Normal.X, r.GetPlane().Normal.Y, r.GetPlane().Normal.Z)],
                      r.get_Parameter(DB.BuiltInParameter.DATUM_PLANE_DEFINES_ORIGIN).AsInteger()] for r in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane)]
    save(); doc.Close(False)
except Exception:
    out['error'] = traceback.format_exc(); save(); raise
