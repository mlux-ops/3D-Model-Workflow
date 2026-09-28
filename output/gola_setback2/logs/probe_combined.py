# -*- coding: utf-8 -*-
"""Structure of the combined Gola family: types, forms and what drives their visibility, planes, recess params."""
import json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
RUN = 'E:/Claude/3D-Model-Workflow/output/gola_setback2'
out = {}
def save():
    with open(RUN + '/logs/probe_combined.json', 'w') as f: json.dump(out, f, indent=2, default=str)
try:
    app = __revit__.Application
    doc = app.OpenDocumentFile(RUN + '/source/Richelieu_Gola_Channel_Profiles_2025.rfa')
    fm = doc.FamilyManager
    out['placement'] = str(doc.OwnerFamily.FamilyPlacementType)
    out['types'] = [t.Name for t in fm.Types]
    out['params'] = [[p.Definition.Name, p.IsInstance, p.Formula] for p in fm.Parameters if p.Id.Value > 0]
    forms = []
    for e in DB.FilteredElementCollector(doc).OfClass(DB.GenericForm):
        links = [[p.Definition.Name, fm.GetAssociatedFamilyParameter(p).Definition.Name] for p in e.Parameters if fm.GetAssociatedFamilyParameter(p) is not None]
        c = e.get_Parameter(DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
        forms.append({'id': str(e.Id.Value), 'solid': e.IsSolid, 'subcat': e.Subcategory.Name if e.Subcategory else None,
                      'comment': c.AsString() if c else None, 'links': links})
    out['forms'] = forms
    planes = []
    for r in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane):
        p = r.GetPlane(); dop = r.get_Parameter(DB.BuiltInParameter.DATUM_PLANE_DEFINES_ORIGIN)
        planes.append([r.Name, [round(v * 304.8, 3) for v in (p.Origin.X, p.Origin.Y, p.Origin.Z)], [round(v, 3) for v in (p.Normal.X, p.Normal.Y, p.Normal.Z)], dop.AsInteger() if dop else None])
    out['planes'] = planes
    lab = []
    for d in DB.FilteredElementCollector(doc).OfClass(DB.Dimension):
        try: fl = d.FamilyLabel
        except Exception: fl = None
        if fl is not None: lab.append([fl.Definition.Name, d.Value * 304.8])
    out['labelled_dims'] = lab
    save(); doc.Close(False)
except Exception:
    out['error'] = traceback.format_exc(); save(); raise
