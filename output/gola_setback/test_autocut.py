# -*- coding: utf-8 -*-
"""Native test of the GolaAutoCut extension: the real updater and button logic, in a scratch project.

Run with: pyrevit run "<abs path>/test_autocut.py" --revit=2025
Expected recess areas (void cross-section on the wall side of the placement plane) come
from the void sketch profiles, measured by logs/probes/probe_autocut.py.
"""
import os, sys, json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

RUN = 'E:/Claude/3D-Model-Workflow/output/gola_setback'
sys.path.insert(0, RUN + '/pyrevit/GolaAutoCut.extension/lib')
import gola_autocut

FAMS = {'horizontal': ('Richelieu_Gola_L_Channel_Horizontal_Setback_2025.rfa', 1992.3993983194362),
        'vertical': ('Richelieu_Gola_Vertical_Double_Grip_Setback_2025.rfa', 2157.4565732001893)}
report = {'stage': 'start', 'tests': {}}


def check(stage):
    report['stage'] = stage
    with open(RUN + '/validation_autocut.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)


def mm(v): return v / 304.8


def vol(e):
    return sum(g.Volume for g in e.get_Geometry(DB.Options()) if isinstance(g, DB.Solid)) * 304.8 ** 3


def committed(doc, name, fn, flush=True):
    tx = DB.Transaction(doc, name); tx.Start()
    r = fn()
    if tx.Commit() != DB.TransactionStatus.Committed: raise ValueError('Transaction %s not committed' % name)
    report.setdefault('queued_after', []).append([name, [sorted(ids) for _, ids in gola_autocut._pending]])
    if flush: report.setdefault('flushed', []).append([name, gola_autocut.process_pending()])
    return r


def wall(doc, level, wt, y, base_offset_mm, height_mm):
    return DB.Wall.Create(doc, DB.Line.CreateBound(DB.XYZ(0, mm(y), 0), DB.XYZ(mm(6000), mm(y), 0)),
                          wt.Id, level.Id, mm(height_mm), mm(base_offset_mm), False, False)


def on_face(doc, w, sym, x0, z0, d, length):
    ref = DB.HostObjectUtils.GetSideFaces(w, DB.ShellLayerType.Exterior)[0]
    face = w.GetGeometryObjectFromReference(ref)
    q0 = face.Project(DB.XYZ(mm(x0), w.Location.Curve.GetEndPoint(0).Y, mm(z0))).XYZPoint
    return doc.Create.NewFamilyInstance(ref, DB.Line.CreateBound(q0, q0.Add(d.Multiply(mm(length)))), sym)


try:
    app = __revit__.Application
    try:
        from pyrevit import HOST_APP
        addin_id = HOST_APP.addin_id
    except Exception as ex:
        report['host_app_error'] = str(ex); addin_id = app.ActiveAddInId
    report['addin_id'] = str(addin_id.GetGUID()) if addin_id is not None else None
    log_start = os.path.getsize(gola_autocut.LOG) if os.path.isfile(gola_autocut.LOG) else 0
    check('register')
    # Headless Revit never idles, so the ExternalEvent cannot fire here; the queue it would
    # flush is flushed by calling process_pending() right after each user transaction.
    gola_autocut.register(addin_id, with_event=False)
    report['registered'] = DB.UpdaterRegistry.IsUpdaterRegistered(DB.UpdaterId(addin_id, gola_autocut.UPDATER_GUID))

    proj = app.NewProjectDocument(DB.UnitSystem.Metric)
    syms = {}
    for k, (name, area) in FAMS.items():
        fdoc = app.OpenDocumentFile(RUN + '/' + name); fam = fdoc.LoadFamily(proj); fdoc.Close(False)
        syms[k] = fam
    level = DB.FilteredElementCollector(proj).OfClass(DB.Level).FirstElement()
    wt = next(t for t in DB.FilteredElementCollector(proj).OfClass(DB.WallType) if t.Kind == DB.WallKind.Basic)

    def symbol(k):
        s = proj.GetElement(list(syms[k].GetFamilySymbolIds())[0])
        if not s.IsActive: s.Activate()
        return s

    # Walls far apart so each test touches only its own wall.
    wA, wB, wC, wD = committed(proj, 'walls', lambda: (wall(proj, level, wt, 0, 0, 3000), wall(proj, level, wt, -3000, 0, 3000),
                                                       wall(proj, level, wt, -6000, -1000, 1000), wall(proj, level, wt, -9000, 0, 3000)))
    committed(proj, 'activate', lambda: [symbol(k) for k in FAMS])
    base = dict((w.Id.Value, vol(w)) for w in (wA, wB, wC, wD))

    def removed(w): return base[w.Id.Value] - vol(w)

    check('T1 horizontal on face')
    iA = committed(proj, 'T1', lambda: on_face(proj, wA, symbol('horizontal'), 1000, 900, DB.XYZ.BasisX, 1500))
    report['tests']['T1_horizontal_face_1500'] = {'removed_mm3': removed(wA), 'expected_mm3': FAMS['horizontal'][1] * 1500,
                                                  'host': iA.Host.GetType().Name if iA.Host else None}

    check('T2 regrip')
    def regrip():
        c = iA.Location.Curve; p0 = c.GetEndPoint(0)
        iA.Location.Curve = DB.Line.CreateBound(p0, p0.Add(DB.XYZ.BasisX.Multiply(mm(2400))))
    committed(proj, 'T2', regrip)
    report['tests']['T2_regrip_2400'] = {'removed_mm3': removed(wA), 'expected_mm3': FAMS['horizontal'][1] * 2400}

    check('T3 vertical on face')
    iB = committed(proj, 'T3', lambda: on_face(proj, wB, symbol('vertical'), 1000, 300, DB.XYZ.BasisZ, 1500))
    report['tests']['T3_vertical_face_1500'] = {'removed_mm3': removed(wB), 'expected_mm3': FAMS['vertical'][1] * 1500,
                                                'host': iB.Host.GetType().Name if iB.Host else None}

    check('T4 unhosted work plane')
    # Wall C's top is at the level; a channel drawn on the level along its centreline sits inside it.
    iC = committed(proj, 'T4', lambda: proj.Create.NewFamilyInstance(
        DB.Line.CreateBound(DB.XYZ(mm(1000), mm(-6000), 0), DB.XYZ(mm(2500), mm(-6000), 0)), symbol('horizontal'), level,
        DB.Structure.StructuralType.NonStructural))
    report['tests']['T4_unhosted_level_1500'] = {'removed_mm3': removed(wC), 'expected_mm3': FAMS['horizontal'][1] * 1500,
                                                 'host': iC.Host.GetType().Name if iC.Host else None,
                                                 'cut_ids': [i.Value for i in DB.InstanceVoidCutUtils.GetElementsBeingCut(iC)]}

    check('T5 move away')
    committed(proj, 'T5', lambda: DB.ElementTransformUtils.MoveElement(proj, iC.Id, DB.XYZ(0, mm(2000), 0)))
    report['tests']['T5_moved_off_wall'] = {'removed_mm3': removed(wC), 'expected_mm3': 0.0,
                                            'cut_ids': [i.Value for i in DB.InstanceVoidCutUtils.GetElementsBeingCut(iC)]}

    check('T6 button without updater')
    gola_autocut.unregister(addin_id)
    iD = committed(proj, 'T6 place', lambda: on_face(proj, wD, symbol('horizontal'), 1000, 900, DB.XYZ.BasisX, 1500))
    before_button = removed(wD)
    rows = gola_autocut.apply(proj, gola_autocut.gola_instances(proj))   # the button's call; manages its own transactions
    changes = sum(len(r[1]) + len(r[2]) for r in rows)
    report['tests']['T6_button'] = {'removed_before_button_mm3': before_button, 'removed_mm3': removed(wD),
                                    'expected_mm3': FAMS['horizontal'][1] * 1500, 'changes': changes}

    others = [w for w in (wA, wB, wC, wD)]
    report['untouched_walls_check'] = dict((str(w.Id.Value), removed(w)) for w in others)
    proj.Close(False)
    with open(gola_autocut.LOG) as f:
        f.seek(log_start); report['log'] = f.read().splitlines()
    check('complete')
except Exception:
    report['error'] = traceback.format_exc()
    check('failed: ' + report['stage'])
    raise
finally:
    try: gola_autocut.unregister(addin_id)
    except Exception as ex: report.setdefault('cleanup_errors', []).append(str(ex))
