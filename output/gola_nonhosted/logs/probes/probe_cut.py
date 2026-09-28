# -*- coding: utf-8 -*-
"""Does cutting the converted channel with the recess void reproduce the source volume?"""
import json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
RUN = 'E:/Claude/3D-Model-Workflow/output/gola_nonhosted'
out = {}
def save():
    with open(RUN + '/logs/probe_cut.json', 'w') as f: json.dump(out, f, indent=2, default=str)
def vol(e):
    return sum(g.Volume for g in e.get_Geometry(DB.Options()) if isinstance(g, DB.Solid)) * 304.8 ** 3
try:
    app = __revit__.Application
    doc = app.OpenDocumentFile(RUN + '/Richelieu_Gola_L_Channel_Horizontal_NonHosted_2025.rfa')
    forms = list(DB.FilteredElementCollector(doc).OfClass(DB.GenericForm))
    void = [f for f in forms if not f.IsSolid][0]
    chan = max([f for f in forms if f.IsSolid], key=vol)
    out['before'] = vol(chan)
    out['can_cut'] = DB.SolidSolidCutUtils.CanElementCutElement(void, chan)[0] if isinstance(DB.SolidSolidCutUtils.CanElementCutElement(void, chan), tuple) else str(DB.SolidSolidCutUtils.CanElementCutElement(void, chan))
    tx = DB.Transaction(doc, 'probe'); tx.Start()
    try:
        DB.SolidSolidCutUtils.AddCutBetweenSolids(doc, chan, void)
        doc.Regenerate()
        out['after_cut'] = vol(chan)
    except Exception as ex:
        out['cut_error'] = str(ex)
    tx.RollBack()
    save(); doc.Close(False)
except Exception:
    out['error'] = traceback.format_exc(); save(); raise
