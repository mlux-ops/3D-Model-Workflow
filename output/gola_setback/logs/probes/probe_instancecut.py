# -*- coding: utf-8 -*-
"""Does InstanceVoidCutUtils.AddInstanceVoidCut cut the expected recess, on face and on work plane?"""
import json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
RUN = 'E:/Claude/3D-Model-Workflow/output/gola_setback'
FILES = [('Richelieu_Gola_L_Channel_Horizontal_Setback_2025.rfa', 'horizontal', 1992.3993983194362),
         ('Richelieu_Gola_Vertical_Double_Grip_Setback_2025.rfa', 'vertical', 2157.4565732001893)]
out = {}
def save():
    with open(RUN + '/logs/probe_instancecut.json', 'w') as f: json.dump(out, f, indent=2, default=str)
def mm(v): return v / 304.8
def vol(e):
    t = 0.0
    for g in e.get_Geometry(DB.Options()):
        if isinstance(g, DB.Solid): t += g.Volume
    return t * 304.8 ** 3
try:
    app = __revit__.Application
    for name, kind, area in FILES:
        proj = app.NewProjectDocument(DB.UnitSystem.Metric)
        fdoc = app.OpenDocumentFile(RUN + '/' + name); fam = fdoc.LoadFamily(proj); fdoc.Close(False)
        tx = DB.Transaction(proj, 'cut'); tx.Start()
        sym = proj.GetElement(list(fam.GetFamilySymbolIds())[0]); sym.Activate()
        level = DB.FilteredElementCollector(proj).OfClass(DB.Level).FirstElement()
        wt = next(t for t in DB.FilteredElementCollector(proj).OfClass(DB.WallType) if t.Kind == DB.WallKind.Basic)
        wall = DB.Wall.Create(proj, DB.Line.CreateBound(DB.XYZ(0, 0, 0), DB.XYZ(mm(6000), 0, 0)), wt.Id, level.Id, mm(3000), 0, False, False)
        proj.Regenerate()
        v0 = vol(wall)
        ref = DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior)[0]
        face = wall.GetGeometryObjectFromReference(ref)
        q0 = face.Project(DB.XYZ(mm(1000), 0, mm(900))).XYZPoint
        d = DB.XYZ.BasisX if kind == 'horizontal' else DB.XYZ.BasisZ
        inst = proj.Create.NewFamilyInstance(ref, DB.Line.CreateBound(q0, q0.Add(d.Multiply(mm(1500)))), sym)
        proj.Regenerate()
        row = {'can_be_cut': DB.InstanceVoidCutUtils.CanBeCutWithVoid(wall),
               'has_unattached_void': DB.InstanceVoidCutUtils.IsVoidInstanceCuttingElement(inst) if hasattr(DB.InstanceVoidCutUtils, 'IsVoidInstanceCuttingElement') else None,
               'expected_mm3': area * 1500}
        try:
            DB.InstanceVoidCutUtils.AddInstanceVoidCut(proj, wall, inst)
            proj.Regenerate()
            row['removed_mm3'] = v0 - vol(wall)
            # flex: length follows, cut follows
            c = inst.Location.Curve; p0 = c.GetEndPoint(0)
            inst.Location.Curve = DB.Line.CreateBound(p0, p0.Add(d.Multiply(mm(2400)))); proj.Regenerate()
            row['removed_after_regrip_2400_mm3'] = v0 - vol(wall); row['expected_2400_mm3'] = area * 2400
        except Exception as ex:
            row['error'] = str(ex)
        out[kind] = row; save()
        tx.RollBack(); proj.Close(False)
except Exception:
    out['error'] = traceback.format_exc(); save(); raise
