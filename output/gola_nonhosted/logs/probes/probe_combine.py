# -*- coding: utf-8 -*-
"""Source GeomCombinations, and whether combining channel + void in the converted file matches the source volume."""
import json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
RUN = 'E:/Claude/3D-Model-Workflow/output/gola_nonhosted'
out = {}
def save():
    with open(RUN + '/logs/probe_combine.json', 'w') as f: json.dump(out, f, indent=2, default=str)
def vol(e):
    return sum(g.Volume for g in e.get_Geometry(DB.Options()) if isinstance(g, DB.Solid)) * 304.8 ** 3
try:
    app = __revit__.Application
    src = app.OpenDocumentFile(RUN + '/source/Richelieu_Gola_L_Channel_Horizontal_2025.rfa')
    out['src_combinations'] = [[m.Id.Value for m in c.AllMembers] for c in DB.FilteredElementCollector(src).OfClass(DB.GeomCombination)]
    sforms = list(DB.FilteredElementCollector(src).OfClass(DB.GenericForm))
    schan = max([f for f in sforms if f.IsSolid], key=vol)
    out['src_channel_volume'] = vol(schan)
    out['src_channel_faces'] = sum(g.Faces.Size for g in schan.get_Geometry(DB.Options()) if isinstance(g, DB.Solid))
    src.Close(False)
    doc = app.OpenDocumentFile(RUN + '/Richelieu_Gola_L_Channel_Horizontal_NonHosted_2025.rfa')
    forms = list(DB.FilteredElementCollector(doc).OfClass(DB.GenericForm))
    void = [f for f in forms if not f.IsSolid][0]
    chan = max([f for f in forms if f.IsSolid], key=vol)
    out['dst_channel_volume'] = vol(chan)
    out['dst_channel_faces'] = sum(g.Faces.Size for g in chan.get_Geometry(DB.Options()) if isinstance(g, DB.Solid))
    tx = DB.Transaction(doc, 'probe'); tx.Start()
    try:
        arr = DB.CombinableElementArray(); arr.Append(chan); arr.Append(void)
        gc = doc.CombineElements(arr); doc.Regenerate()
        out['combined_volume'] = sum(g.Volume for g in gc.get_Geometry(DB.Options()) if isinstance(g, DB.Solid)) * 304.8 ** 3
    except Exception as ex:
        out['combine_error'] = str(ex)
    tx.RollBack()
    save(); doc.Close(False)
except Exception:
    out['error'] = traceback.format_exc(); save(); raise
