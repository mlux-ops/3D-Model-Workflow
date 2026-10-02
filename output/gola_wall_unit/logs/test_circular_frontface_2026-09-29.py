# -*- coding: utf-8 -*-
"""Reproduce the Belmont "circular chain of references" (Gola placed on the cabinet face it cuts) and test the fix.

Run with: pyrevit run "<abs path>/test_circular.py" --revit=2025
Uses the real GolaAutoCut module from output/gola_setback/pyrevit (the copy that gets installed).
"""
import os, sys, json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

RUN = 'E:/Claude/3D-Model-Workflow/output/gola_wall_unit'
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/gola_setback/pyrevit/GolaAutoCut.extension/lib')
import gola_autocut

GOLA = RUN + '/Richelieu_Gola_Wall_Unit_Upper_Cabinet_2025.rfa'
BOX = RUN + '/test_families/Test_Cabinet_Box_cuttable.rfa'   # Casework box x 0..2000, y 0..400, z -700..0
report = {'stage': 'start', 'tests': {}}


def check(stage):
    report['stage'] = stage
    with open(RUN + '/validation_circular.json', 'w') as f: json.dump(report, f, indent=2, default=str)


def mm(v): return v / 304.8


class Rec(DB.IFailuresPreprocessor):
    def __init__(self): self.msgs = []
    def PreprocessFailures(self, a):
        rb = False
        for f in a.GetFailureMessages():
            self.msgs.append('%s: %s' % (f.GetSeverity(), f.GetDescriptionText()))
            if f.GetSeverity() == DB.FailureSeverity.Warning: a.DeleteWarning(f)
            else: rb = True
        return DB.FailureProcessingResult.ProceedWithRollBack if rb else DB.FailureProcessingResult.Continue


def tx(doc, name):
    t = DB.Transaction(doc, name); r = Rec()
    o = t.GetFailureHandlingOptions(); o.SetFailuresPreprocessor(r); o.SetClearAfterRollback(True)
    t.SetFailureHandlingOptions(o); t.Start()
    return t, r


def front_face_ref(doc, inst):
    """Reference to the box's y = 0 face (normal -Y) that hosts on the instance itself, as a UI click does:
    with ComputeReferences, symbol-geometry face references come back instance-qualified (probe_face_refs)."""
    o = DB.Options(); o.ComputeReferences = True
    for g in inst.get_Geometry(o):
        if isinstance(g, DB.GeometryInstance):
            t = g.Transform
            for s in g.GetSymbolGeometry():
                if isinstance(s, DB.Solid):
                    for f in s.Faces:
                        if isinstance(f, DB.PlanarFace) and t.OfVector(f.FaceNormal).Y < -0.99 and f.Reference is not None:
                            return f.Reference, t.OfPoint(f.Origin).Y
    raise ValueError('front face reference not found')


def place_on_face(doc, sym, box, z_mm, x0=250, x1=1750):
    ref, y = front_face_ref(doc, box)
    q0 = DB.XYZ(mm(x0), y, mm(z_mm)); q1 = DB.XYZ(mm(x1), y, mm(z_mm))
    return doc.Create.NewFamilyInstance(ref, DB.Line.CreateBound(q0, q1), sym)


def bbox(e):
    b = e.get_BoundingBox(None)
    return [round(v * 304.8, 3) for v in (b.Min.X, b.Min.Y, b.Min.Z, b.Max.X, b.Max.Y, b.Max.Z)]


try:
    app = __revit__.Application
    try:
        from pyrevit import HOST_APP
        addin = HOST_APP.addin_id
    except Exception:
        addin = app.ActiveAddInId
    proj = app.NewProjectDocument(DB.UnitSystem.Metric)
    t, r = tx(proj, 'setup')
    fams = {}
    for k, p in (('gola', GOLA), ('box', BOX)):
        ref = clr.Reference[DB.Family]()
        if not proj.LoadFamily(p, ref): raise ValueError('load failed ' + p)
        fams[k] = proj.GetElement(list(ref.Value.GetFamilySymbolIds())[0]); fams[k].Activate()
    level = DB.FilteredElementCollector(proj).OfClass(DB.Level).FirstElement()
    NS = DB.Structure.StructuralType.NonStructural
    boxA = proj.Create.NewFamilyInstance(DB.XYZ(0, 0, 0), fams['box'], level, NS)
    boxB = proj.Create.NewFamilyInstance(DB.XYZ(mm(2000), mm(1000), 0), fams['box'], level, NS)   # neighbour; moved flush against A's side later
    boxC = proj.Create.NewFamilyInstance(DB.XYZ(0, mm(5000), 0), fams['box'], level, NS)
    t.Commit()
    vA0, vC0 = gola_autocut.volume_mm3(boxA), gola_autocut.volume_mm3(boxC)

    check('T1 old behaviour')
    t, r = tx(proj, 'place on face'); g1 = place_on_face(proj, fams['gola'], boxA, -700); t.Commit()
    t, r = tx(proj, 'old plain cut')
    DB.InstanceVoidCutUtils.AddInstanceVoidCut(proj, boxA, g1)
    status = t.Commit()
    report['tests']['T1_old_plain_cut'] = {'status': str(status), 'failures': r.msgs, 'host': g1.Host.GetType().Name if g1.Host else None,
                                           'placed_on': gola_autocut.placed_on(proj, g1, boxA),
                                           'removed_mm3': vA0 - gola_autocut.volume_mm3(boxA)}

    check('T2a face-hosted: apply keeps the host')
    rows2a = gola_autocut.apply(proj, [g1])
    report['tests']['T2a_face_hosted'] = {'rows': rows2a, 'still_hosted_on_box': g1.IsValidObject and g1.Host is not None and g1.Host.Id == boxA.Id,
                                          'placed_on': gola_autocut.placed_on(proj, g1, boxA)}

    new = g1

    check('T3 neighbour flush against the run end')
    t, r = tx(proj, 'move neighbour'); DB.ElementTransformUtils.MoveElement(proj, boxB.Id, DB.XYZ(0, mm(-1000), 0)); t.Commit()
    vB0 = gola_autocut.volume_mm3(boxB)
    t, r = tx(proj, 'run to cabinet end'); c = new.Location.Curve; p0 = c.GetEndPoint(0)
    new.Location.Curve = DB.Line.CreateBound(p0, DB.XYZ(mm(2000), p0.Y, p0.Z)); t.Commit()
    vA1 = gola_autocut.volume_mm3(boxA)
    rows3 = gola_autocut.apply(proj, [new])
    report['box_bboxes_mm'] = {'boxA': bbox(boxA), 'boxB': bbox(boxB), 'gola': bbox(new),
                               'gola_line': [round(v * 304.8, 3) for q in (new.Location.Curve.GetEndPoint(0), new.Location.Curve.GetEndPoint(1)) for v in (q.X, q.Y, q.Z)]}
    report['tests']['T3_neighbour'] = {'rows': rows3, 'neighbour_removed_mm3': vB0 - gola_autocut.volume_mm3(boxB),
                                       'neighbour_cut': boxB.Id.Value in gola_autocut.cut_ids(new),
                                       'boxA_removed_mm3': vA0 - gola_autocut.volume_mm3(boxA),
                                       'boxA_expected_mm3': 20 * (19.05 + 20) * (1981.262 - 250), 'neighbour_expected_mm3': 20 * (19.05 + 20) * (2000 - 1981.262)}
    check('T3b run across both cabinets')
    t, r = tx(proj, 'run across'); c = new.Location.Curve; p0 = c.GetEndPoint(0)
    new.Location.Curve = DB.Line.CreateBound(p0, DB.XYZ(mm(3000), p0.Y, p0.Z)); t.Commit()
    rows3b = gola_autocut.apply(proj, [new])
    report['tests']['T3b_across'] = {'rows': rows3b, 'neighbour_removed_mm3': vB0 - gola_autocut.volume_mm3(boxB),
                                     'neighbour_expected_mm3': 20 * (19.05 + 20) * (3000 - 1981.262),
                                     'boxA_removed_mm3': vA0 - gola_autocut.volume_mm3(boxA),
                                     'boxA_expected_mm3': 20 * (19.05 + 20) * (1981.262 - 250)}

    check('T4 automatic path')
    gola_autocut.register(addin, with_event=False)
    t, r = tx(proj, 'place on face C'); g4 = place_on_face(proj, fams['gola'], boxC, -350); t.Commit()
    queued = [sorted(ids) for _, ids in gola_autocut._pending]
    rows4 = gola_autocut.process_pending()
    gola_autocut.unregister(addin)
    report['tests']['T4_updater'] = {'queued': queued, 'rows': rows4, 'removed_mm3': vC0 - gola_autocut.volume_mm3(boxC),
                                     'expected_mm3': 21 * (19.05 + 20) * 1500}
    check('T5 box touching the channel box but not reached by the void')
    # The test box family's solid sits 18.74 mm towards -X of its insertion point (Casework template),
    # so inserting at 1750 + 0.3 + 18.738 puts its solid face 0.3 mm past the channel end (x = 1750):
    # inside the 0.5 mm candidate pad, outside the void.
    t, r = tx(proj, 'touching box'); boxE = proj.Create.NewFamilyInstance(DB.XYZ(mm(1750 + 0.3 + 18.738), mm(5000), 0), fams['box'], level, NS); t.Commit()
    vE0 = gola_autocut.volume_mm3(boxE)
    cand = [e.Id.Value for e in gola_autocut.touching(proj, g4)[0]]
    rows5 = gola_autocut.apply(proj, [g4])
    report['tests']['T5_touch_only'] = {'is_candidate': boxE.Id.Value in cand, 'rows': rows5,
                                        'removed_mm3': vE0 - gola_autocut.volume_mm3(boxE),
                                        'cut': boxE.Id.Value in gola_autocut.cut_ids(g4),
                                        'boxC_still_cut': boxC.Id.Value in gola_autocut.cut_ids(g4)}
    with open(gola_autocut.LOG) as f: report['log_tail'] = f.read().splitlines()[-12:]
    proj.Close(False)
    check('complete')
except Exception:
    report['error'] = traceback.format_exc(); check('failed: ' + report['stage']); raise
