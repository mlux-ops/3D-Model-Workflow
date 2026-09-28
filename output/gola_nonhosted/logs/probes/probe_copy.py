# -*- coding: utf-8 -*-
"""Diagnose why cross-document CopyElements fails for the horizontal Gola forms."""
import os, json, math, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RUN = 'E:/Claude/3D-Model-Workflow/output/gola_nonhosted'
TEMPLATE = 'C:/ProgramData/Autodesk/RVT 2025/Family Templates/English-Imperial/Generic Model.rft'
SRC = RUN + '/source/Richelieu_Gola_L_Channel_Horizontal_2025.rfa'
out = {'forms': [], 'dims': {}}


def save():
    with open(RUN + '/logs/probe_copy.json', 'w') as f:
        json.dump(out, f, indent=2, default=str)


class UseDest(DB.IDuplicateTypeNamesHandler):
    def OnDuplicateTypeNamesFound(self, args):
        return DB.DuplicateTypeAction.UseDestinationTypes


def opts():
    o = DB.CopyPasteOptions(); o.SetDuplicateTypeNamesHandler(UseDest()); return o


def attempt(src, ids, t, label):
    dst = app.NewFamilyDocument(TEMPLATE)
    tx = DB.Transaction(dst, 'probe'); tx.Start()
    try:
        r = DB.ElementTransformUtils.CopyElements(src, List[DB.ElementId](ids), dst, t, opts())
        res = 'ok %d' % r.Count
    except Exception as ex:
        res = 'FAIL ' + str(ex)
    tx.RollBack(); dst.Close(False)
    return res


try:
    app = __revit__.Application
    src = app.OpenDocumentFile(SRC)
    rot = DB.Transform.CreateRotation(DB.XYZ.BasisX, math.pi / 2)
    fs = list(DB.FilteredElementCollector(src).OfClass(DB.GenericForm).ToElements())
    dims = list(DB.FilteredElementCollector(src).OfClass(DB.Dimension).ToElements())
    labelled = 0; view_kinds = {}
    for d in dims:
        try:
            if d.FamilyLabel is not None: labelled += 1
        except Exception: pass
        v = src.GetElement(d.OwnerViewId)
        k = v.GetType().Name if v is not None else 'none'
        view_kinds[k] = view_kinds.get(k, 0) + 1
    out['dims'] = {'count': len(dims), 'labelled': labelled, 'owner_view_kinds': view_kinds}
    out['ref_planes'] = [r.Name for r in DB.FilteredElementCollector(src).OfClass(DB.ReferencePlane)]
    save()
    for e in fs:
        row = {'id': e.Id.Value, 'class': e.GetType().Name,
               'comment': (e.get_Parameter(DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString() if e.get_Parameter(DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS) else None),
               'sketch_dims': None}
        try:
            sk = e.Sketch
            row['sketch_plane_normal'] = str(sk.SketchPlane.GetPlane().Normal)
        except Exception as ex:
            row['sketch_err'] = str(ex)
        row['identity'] = attempt(src, [e.Id], DB.Transform.Identity, 'identity')
        row['rotated'] = attempt(src, [e.Id], rot, 'rotated')
        out['forms'].append(row); save()
    out['all_identity'] = attempt(src, [e.Id for e in fs], DB.Transform.Identity, 'all')
    save()
    src.Close(False)
except Exception:
    out['error'] = traceback.format_exc(); save(); raise
