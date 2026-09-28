# -*- coding: utf-8 -*-
"""Experiment: does an unattached copy of the recess void auto-cut the wall on Place on Face?

Works on scratch copies only (logs/probes/variant_*.rfa). Never touches the deliverables.
"""
import os, json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RUN = 'E:/Claude/3D-Model-Workflow/output/gola_setback'
PROBE = RUN + '/logs/probes'
FILES = [('Richelieu_Gola_L_Channel_Horizontal_Setback_2025.rfa', 'horizontal'),
         ('Richelieu_Gola_Vertical_Double_Grip_Setback_2025.rfa', 'vertical')]
out = {}


def save():
    with open(RUN + '/logs/probe_autocut.json', 'w') as f:
        json.dump(out, f, indent=2, default=str)


def mm(v): return v / 304.8


def solids(geom):
    for g in geom:
        if isinstance(g, DB.Solid) and g.Volume > 1e-12: yield g
        elif isinstance(g, DB.GeometryInstance):
            for s in solids(g.GetInstanceGeometry()): yield s


def vol_mm3(e): return sum(s.Volume for s in solids(e.get_Geometry(DB.Options()))) * 304.8 ** 3


def void_inside_area_mm2(doc, void, plane_z):
    """Cross-section area of the void on the wall side of the placement plane (local z < plane_z)."""
    # Void geometry has negative volume; rebuild a positive solid from its sketch profile.
    loops = List[DB.CurveLoop]()
    for ca in void.Sketch.Profile:
        cl = DB.CurveLoop()
        for c in ca: cl.Append(c)
        loops.Add(cl)
    n = void.Sketch.SketchPlane.GetPlane().Normal
    run = mm(1000)
    vs = DB.GeometryCreationUtilities.CreateExtrusionGeometry(loops, n, run)
    b = vs.GetBoundingBox(); t = b.Transform
    lo = t.OfPoint(b.Min); hi = t.OfPoint(b.Max)
    x0, x1 = min(lo.X, hi.X) - 1, max(lo.X, hi.X) + 1
    y0, y1 = min(lo.Y, hi.Y) - 1, max(lo.Y, hi.Y) + 1
    z0 = min(lo.Z, hi.Z) - 1
    pts = [DB.XYZ(x0, y0, z0), DB.XYZ(x1, y0, z0), DB.XYZ(x1, y1, z0), DB.XYZ(x0, y1, z0)]
    loop = DB.CurveLoop()
    for i in range(4): loop.Append(DB.Line.CreateBound(pts[i], pts[(i + 1) % 4]))
    box = DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]), DB.XYZ.BasisZ, plane_z - z0)
    inter = DB.BooleanOperationsUtils.ExecuteBooleanOperation(vs, box, DB.BooleanOperationsType.Intersect)
    return inter.Volume / run * 304.8 ** 2


def make_variant(app, name, kind, row):
    doc = app.OpenDocumentFile(RUN + '/' + name)
    fm = doc.FamilyManager
    voids = [f for f in DB.FilteredElementCollector(doc).OfClass(DB.GenericForm) if not f.IsSolid]
    chan = [f for f in DB.FilteredElementCollector(doc).OfClass(DB.GenericForm) if f.IsSolid and f.Subcategory and f.Subcategory.Name == 'Channel Profiles']
    row['channel_volume_before'] = sum(vol_mm3(c) for c in chan)
    plane = next(r for r in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane) if r.Name == 'Placement Plane')
    row['expected_cut_area_mm2'] = sum(void_inside_area_mm2(doc, v, plane.GetPlane().Origin.Z) for v in voids)
    length = next(p for p in fm.Parameters if p.Definition.Name == 'Length')
    tx = DB.Transaction(doc, 'unattach void'); tx.Start()
    new = []
    for v in voids:
        nid = list(DB.ElementTransformUtils.CopyElement(doc, v.Id, DB.XYZ.Zero))
        nv = [doc.GetElement(i) for i in nid if isinstance(doc.GetElement(i), DB.GenericForm)][0]
        doc.Delete(v.Id)
        fm.AssociateElementParameterToFamilyParameter(nv.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM), length)
        new.append(nv)
    doc.Regenerate()
    row['channel_volume_after_in_doc_copy'] = sum(vol_mm3(c) for c in chan)
    row['new_void_end_mm'] = [nv.EndOffset * 304.8 for nv in new]
    tx.Commit()
    path = PROBE + '/variant_' + name
    so = DB.SaveAsOptions(); so.OverwriteExistingFile = True; so.MaximumBackups = 1
    doc.SaveAs(path, so); doc.Close(False)
    return path


def wall_cut(app, rfa, kind):
    proj = app.NewProjectDocument(DB.UnitSystem.Metric)
    fdoc = app.OpenDocumentFile(rfa); fam = fdoc.LoadFamily(proj); fdoc.Close(False)
    tx = DB.Transaction(proj, 'cut test'); tx.Start()
    sym = proj.GetElement(list(fam.GetFamilySymbolIds())[0]); sym.Activate()
    level = DB.FilteredElementCollector(proj).OfClass(DB.Level).FirstElement()
    wt = next(t for t in DB.FilteredElementCollector(proj).OfClass(DB.WallType) if t.Kind == DB.WallKind.Basic)
    wall = DB.Wall.Create(proj, DB.Line.CreateBound(DB.XYZ(0, 0, 0), DB.XYZ(mm(6000), 0, 0)), wt.Id, level.Id, mm(3000), 0, False, False)
    proj.Regenerate()
    before = vol_mm3(wall)
    ref = DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior)[0]
    face = wall.GetGeometryObjectFromReference(ref)
    q0 = face.Project(DB.XYZ(mm(1000), 0, mm(900))).XYZPoint
    d = DB.XYZ.BasisX if kind == 'horizontal' else DB.XYZ.BasisZ
    inst = proj.Create.NewFamilyInstance(ref, DB.Line.CreateBound(q0, q0.Add(d.Multiply(mm(1500)))), sym)
    proj.Regenerate()
    after = vol_mm3(wall)
    res = {'wall_removed_mm3': before - after, 'wall_width_mm': wall.Width * 304.8,
           'instance_cuts_wall': DB.InstanceVoidCutUtils.InstanceVoidCutExists(wall, inst),
           'host': inst.Host.GetType().Name if inst.Host else None}
    tx.RollBack(); proj.Close(False)
    return res


try:
    app = __revit__.Application
    for name, kind in FILES:
        row = {}; out[kind] = row
        row['original_on_face'] = wall_cut(app, RUN + '/' + name, kind); save()
        v = make_variant(app, name, kind, row); save()
        row['variant_on_face'] = wall_cut(app, v, kind); save()
except Exception:
    out['error'] = traceback.format_exc(); save(); raise
