# -*- coding: utf-8 -*-
"""Why does the placed horizontal source sit 21-48 mm into its plane, and which form differs by 2.8 mm3?"""
import json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

RUN = 'E:/Claude/3D-Model-Workflow/output/gola_nonhosted'
out = {}


def save():
    with open(RUN + '/logs/probe_origin.json', 'w') as f:
        json.dump(out, f, indent=2, default=str)


def mmv(p): return [round(p.X * 304.8, 4), round(p.Y * 304.8, 4), round(p.Z * 304.8, 4)]


def vol(e):
    t = 0.0
    for g in e.get_Geometry(DB.Options()):
        if isinstance(g, DB.Solid): t += g.Volume
    return t * 304.8 ** 3


def bbox(e):
    b = e.get_BoundingBox(None)
    return mmv(b.Min) + mmv(b.Max) if b else None


try:
    app = __revit__.Application
    for label, path in [('src', RUN + '/source/Richelieu_Gola_L_Channel_Horizontal_2025.rfa'),
                        ('dst', RUN + '/Richelieu_Gola_L_Channel_Horizontal_NonHosted_2025.rfa')]:
        doc = app.OpenDocumentFile(path)
        planes = []
        for r in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane):
            p = r.GetPlane()
            dop = r.get_Parameter(DB.BuiltInParameter.DATUM_PLANE_DEFINES_ORIGIN)
            isref = r.get_Parameter(DB.BuiltInParameter.ELEM_REFERENCE_NAME)
            planes.append({'name': r.Name, 'origin': mmv(p.Origin), 'normal': mmv(p.Normal),
                           'defines_origin': dop.AsInteger() if dop else None,
                           'is_reference': isref.AsValueString() if isref else None, 'pinned': r.Pinned})
        forms = []
        for e in sorted(DB.FilteredElementCollector(doc).OfClass(DB.GenericForm), key=lambda x: x.Id.Value):
            forms.append({'id': e.Id.Value, 'solid': e.IsSolid, 'volume_mm3': round(vol(e), 4), 'bbox': bbox(e),
                          'subcat': e.Subcategory.Name if e.Subcategory else None})
        wp = doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED)
        out[label] = {'planes': planes, 'forms': forms, 'placement': str(doc.OwnerFamily.FamilyPlacementType),
                      'levels': [[l.Name, round(l.Elevation * 304.8, 4)] for l in DB.FilteredElementCollector(doc).OfClass(DB.Level)]}
        save()
        doc.Close(False)
except Exception:
    out['error'] = traceback.format_exc(); save(); raise
