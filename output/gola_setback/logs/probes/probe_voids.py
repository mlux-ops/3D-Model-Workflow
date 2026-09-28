# -*- coding: utf-8 -*-
"""Dump void forms (profile, extents, links, locks) in the two setback families."""
import json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

RUN = 'E:/Claude/3D-Model-Workflow/output/gola_setback'
FILES = ['Richelieu_Gola_L_Channel_Horizontal_Setback_2025.rfa', 'Richelieu_Gola_Vertical_Double_Grip_Setback_2025.rfa']
out = {}


def save():
    with open(RUN + '/logs/probe_voids.json', 'w') as f:
        json.dump(out, f, indent=2, default=str)


def mmv(p): return [round(p.X * 304.8, 4), round(p.Y * 304.8, 4), round(p.Z * 304.8, 4)]


try:
    app = __revit__.Application
    for name in FILES:
        doc = app.OpenDocumentFile(RUN + '/' + name)
        fm = doc.FamilyManager
        rows = []
        for e in DB.FilteredElementCollector(doc).OfClass(DB.GenericForm):
            vol = sum(g.Volume for g in e.get_Geometry(DB.Options()) if isinstance(g, DB.Solid)) * 304.8 ** 3
            row = {'id': str(e.Id.Value), 'class': e.GetType().Name, 'solid': e.IsSolid, 'volume_mm3': round(vol, 4),
                   'subcat': e.Subcategory.Name if e.Subcategory else None}
            if not e.IsSolid:
                b = e.get_BoundingBox(None)
                row['bbox'] = mmv(b.Min) + mmv(b.Max)
                row['links'] = [[p.Definition.Name, fm.GetAssociatedFamilyParameter(p).Definition.Name]
                                for p in e.Parameters if fm.GetAssociatedFamilyParameter(p) is not None]
                if isinstance(e, DB.Extrusion):
                    row['start_end_mm'] = [e.StartOffset * 304.8, e.EndOffset * 304.8]
                    row['sketch_normal'] = mmv(e.Sketch.SketchPlane.GetPlane().Normal)
                    loops = []
                    for ca in e.Sketch.Profile:
                        loops.append([mmv(c.GetEndPoint(0)) for c in ca])
                    row['profile_loops'] = loops
                locks = []
                for d in DB.FilteredElementCollector(doc).OfClass(DB.Dimension):
                    refs = [r.ElementId.Value for r in d.References]
                    if e.Id.Value in refs and d.IsLocked:
                        locks.append([doc.GetElement(DB.ElementId(x)).GetType().Name + ' ' + (doc.GetElement(DB.ElementId(x)).Name if hasattr(doc.GetElement(DB.ElementId(x)), 'Name') else '') for x in refs if x != e.Id.Value])
                row['locked_to'] = locks
            rows.append(row)
        chan = [r for r in rows if r['subcat'] == 'Channel Profiles']
        out[name] = {'forms': rows, 'channel_volume_mm3': [r['volume_mm3'] for r in chan],
                     'cut_with_voids': doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALLOW_CUT_WITH_VOIDS).AsInteger()}
        save()
        doc.Close(False)
except Exception:
    out['error'] = traceback.format_exc(); save(); raise
