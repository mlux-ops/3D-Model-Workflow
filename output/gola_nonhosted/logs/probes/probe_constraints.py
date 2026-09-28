# -*- coding: utf-8 -*-
"""Find what the uncopyable Gola forms are constrained to, and test copy with companions."""
import json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RUN = 'E:/Claude/3D-Model-Workflow/output/gola_nonhosted'
TEMPLATE = 'C:/ProgramData/Autodesk/RVT 2025/Family Templates/English-Imperial/Generic Model.rft'
SRC = RUN + '/source/Richelieu_Gola_L_Channel_Horizontal_2025.rfa'
FAILING = [13077715, 13077889, 13077900, 13077974, 13077988, 13077999]
out = {}


def save():
    with open(RUN + '/logs/probe_constraints.json', 'w') as f:
        json.dump(out, f, indent=2, default=str)


class UseDest(DB.IDuplicateTypeNamesHandler):
    def OnDuplicateTypeNamesFound(self, args):
        return DB.DuplicateTypeAction.UseDestinationTypes


def attempt(src, ids):
    dst = app.NewFamilyDocument(TEMPLATE)
    tx = DB.Transaction(dst, 'probe'); tx.Start()
    o = DB.CopyPasteOptions(); o.SetDuplicateTypeNamesHandler(UseDest())
    try:
        r = DB.ElementTransformUtils.CopyElements(src, List[DB.ElementId](ids), dst, DB.Transform.Identity, o)
        res = 'ok %d' % r.Count
    except Exception as ex:
        res = 'FAIL ' + str(ex)
    tx.RollBack(); dst.Close(False)
    return res


def label(doc, eid):
    e = doc.GetElement(eid)
    if e is None: return str(eid.Value)
    n = ''
    try: n = DB.Element.Name.GetValue(e)
    except Exception: pass
    return '%d %s %s' % (eid.Value, e.GetType().Name, n)


try:
    app = __revit__.Application
    src = app.OpenDocumentFile(SRC)
    fm = src.FamilyManager
    ids13077 = [13077715, 13077889, 13077900, 13077974, 13077988, 13077999, 13077791]
    # labelled dimensions
    out['labelled_dims'] = []
    dims = list(DB.FilteredElementCollector(src).OfClass(DB.Dimension).ToElements())
    for d in dims:
        try: fl = d.FamilyLabel
        except Exception: fl = None
        if fl is not None:
            out['labelled_dims'].append({'id': d.Id.Value, 'label': fl.Definition.Name,
                                         'refs': [label(src, r.ElementId) for r in d.References]})
    # constraint dims touching each form
    forms = dict((e.Id.Value, e) for e in DB.FilteredElementCollector(src).OfClass(DB.GenericForm))
    out['forms'] = {}
    for fid, e in sorted(forms.items()):
        sketch_ids = set()
        try:
            sketch_ids.add(e.Sketch.Id.Value)
            for ca in e.Sketch.Profile:
                for c in ca:
                    if c.Reference is not None: sketch_ids.add(c.Reference.ElementId.Value)
        except Exception: pass
        touching = []
        for d in dims:
            refs = [r.ElementId.Value for r in d.References]
            if fid in refs or sketch_ids.intersection(refs):
                others = [label(src, r.ElementId) for r in d.References if r.ElementId.Value != fid and r.ElementId.Value not in sketch_ids]
                touching.append({'dim': d.Id.Value, 'locked': d.IsLocked, 'view': d.OwnerViewId.Value, 'others': others})
        row = {'is_solid': e.IsSolid, 'subcat': e.Subcategory.Name if e.Subcategory else None,
               'start_mm': e.get_Parameter(DB.BuiltInParameter.EXTRUSION_START_PARAM).AsDouble() * 304.8 if isinstance(e, DB.Extrusion) else None,
               'end_mm': e.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM).AsDouble() * 304.8 if isinstance(e, DB.Extrusion) else None,
               'assoc': [(p.Definition.Name, fm.GetAssociatedFamilyParameter(p).Definition.Name) for p in e.Parameters if fm.GetAssociatedFamilyParameter(p) is not None],
               'constraints_outside_sketch': [t for t in touching if t['others']],
               'constraint_count': len(touching),
               'failing': fid in FAILING or fid == 13077715}
        out['forms'][str(fid)] = row
        save()
    planes = [r.Id for r in DB.FilteredElementCollector(src).OfClass(DB.ReferencePlane)]
    out['copy_form_plus_planes'] = attempt(src, [DB.ElementId(13077889)] + planes)
    out['copy_form_plus_planes_and_dims'] = attempt(src, [DB.ElementId(13077889)] + planes + [d.Id for d in dims])
    save()
    src.Close(False)
except Exception:
    out['error'] = traceback.format_exc(); save(); raise
