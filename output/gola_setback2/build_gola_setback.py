# -*- coding: utf-8 -*-
"""Line-based Richelieu Gola families with a 3/4 in wall setback.

Run with: pyrevit run "<abs path>/build_gola_setback.py" --revit=2025
Reads source/ single-type RFAs extracted from the combined family by extract_types.py.

Placement stays line based: first click = start, second click = end.
Setback: instance parameter "Wall Setback" (default 19.05 mm = 3/4 in). The channel
profile's front face (the face nearest the room) lands that far behind the plane or face
that is clicked. It works by driving the origin-defining Placement Plane to
"Front Face Depth + Wall Setback" from the family's work plane (local z = 0); the family's
local +Z is the clicked plane's normal, so the profile sits in -Z (into the wall).
"""
import os, json, math, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RUN = 'E:/Claude/3D-Model-Workflow/output/gola_setback2'
JOBS = [
    ('Richelieu_Gola_C_Channel_Horizontal_2025.rfa', 'Richelieu_Gola_C_Channel_Horizontal_Setback_2025.rfa', 'horizontal'),
    ('Richelieu_Gola_Vertical_Single_Grip_2025.rfa', 'Richelieu_Gola_Vertical_Single_Grip_Setback_2025.rfa', 'vertical')]
SETBACK_MM = 19.05
report = {'stage': 'start', 'run_dir': RUN, 'setback_default_mm': SETBACK_MM, 'jobs': []}
open_docs = []


def out_path(*parts):
    p = os.path.normpath(os.path.join(RUN, *parts))
    if not p.lower().startswith(os.path.normpath(RUN).lower() + os.sep):
        raise ValueError('Refusing to write outside run dir: ' + p)
    return p


def check(stage):
    report['stage'] = stage
    with open(out_path('validation.json'), 'w') as f:
        json.dump(report, f, indent=2, default=str)


def close_doc(doc):
    """Drop by identity first: list.remove compares documents with Equals, which throws on a closed one."""
    open_docs[:] = [d for d in open_docs if d is not doc]
    doc.Close(False)


def mm(v): return v / 304.8
def to_mm(v): return v * 304.8


class RecordWarnings(DB.IFailuresPreprocessor):
    """Delete warnings (recorded), roll back on errors - never leave a modal prompt."""
    def PreprocessFailures(self, accessor):
        rollback = False
        for f in accessor.GetFailureMessages():
            report.setdefault('revit_failures', []).append([report['stage'], str(f.GetSeverity()), f.GetDescriptionText()])
            if f.GetSeverity() == DB.FailureSeverity.Warning:
                accessor.DeleteWarning(f)
            else:
                rollback = True
        return DB.FailureProcessingResult.ProceedWithRollBack if rollback else DB.FailureProcessingResult.Continue


def transaction(doc, name):
    tx = DB.Transaction(doc, name)
    o = tx.GetFailureHandlingOptions(); o.SetFailuresPreprocessor(RecordWarnings()); o.SetClearAfterRollback(True)
    tx.SetFailureHandlingOptions(o)
    tx.Start()
    return tx


def commit(tx, step):
    status = tx.Commit()
    if status != DB.TransactionStatus.Committed:
        raise ValueError('Transaction "%s" ended %s; see revit_failures' % (step, status))


def on_dialog(sender, args):
    # A headless run has nobody to answer a dialog; cancel it so the call fails loudly instead of hanging.
    report.setdefault('dialogs_cancelled', []).append(args.DialogId)
    args.OverrideResult(2)


def solids(geom):
    for g in geom:
        if isinstance(g, DB.Solid) and g.Volume > 1e-12:
            yield g
        elif isinstance(g, DB.GeometryInstance):
            for s in solids(g.GetInstanceGeometry()):
                yield s


def points(ss):
    return [p for s in ss for ed in s.Edges for p in ed.Tessellate()]


def channel_forms(doc):
    fs = [f for f in DB.FilteredElementCollector(doc).OfClass(DB.GenericForm)
          if f.IsSolid and f.Subcategory is not None and f.Subcategory.Name == 'Channel Profiles']
    if not fs: raise ValueError('No Channel Profiles forms found')
    return fs


def origin_plane(doc):
    """The reference plane that defines the origin normal to the work plane (local Z)."""
    hits = []
    for r in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane):
        dop = r.get_Parameter(DB.BuiltInParameter.DATUM_PLANE_DEFINES_ORIGIN)
        if dop is not None and dop.AsInteger() == 1 and abs(abs(r.GetPlane().Normal.Z) - 1) < 1e-9:
            hits.append(r)
    if len(hits) > 1: raise ValueError('More than one Z origin plane: %s' % [h.Name for h in hits])
    return hits[0] if hits else None


def elevation_view(doc):
    for v in DB.FilteredElementCollector(doc).OfClass(DB.View):
        if not v.IsTemplate and v.ViewType == DB.ViewType.Elevation and abs(v.ViewDirection.Z) < 1e-9:
            return v
    raise ValueError('No elevation view in family')


def build(app, src_name, dst_name, kind, job):
    doc = app.OpenDocumentFile(out_path('source', src_name)); open_docs.append(doc)
    job['source_placement_type'] = str(doc.OwnerFamily.FamilyPlacementType)
    if doc.OwnerFamily.FamilyPlacementType != DB.FamilyPlacementType.CurveBased:
        raise ValueError('Source is not line based')
    fm = doc.FamilyManager
    for n in ('Wall Setback', 'Front Face Depth', 'Placement Offset'):
        if any(p.Definition.Name == n for p in fm.Parameters): raise ValueError('Parameter already exists: ' + n)
    pts = points([s for f in channel_forms(doc) for s in solids(f.get_Geometry(DB.Options()))])
    front = max(p.Z for p in pts); back = min(p.Z for p in pts)
    job['channel_local_z_mm'] = [to_mm(back), to_mm(front)]
    if abs(back) > mm(0.01): raise ValueError('Channel back is not at local z = 0: %.4f mm' % to_mm(back))
    op = origin_plane(doc)
    job['origin_plane_before'] = None if op is None else {'name': op.Name, 'z_mm': to_mm(op.GetPlane().Origin.Z),
                                                          'normal_z': op.GetPlane().Normal.Z}

    tx = transaction(doc, 'Wall setback')
    ws = fm.AddParameter('Wall Setback', DB.GroupTypeId.Constraints, DB.SpecTypeId.Length, True)
    fd = fm.AddParameter('Front Face Depth', DB.GroupTypeId.Constraints, DB.SpecTypeId.Length, False)
    po = fm.AddParameter('Placement Offset', DB.GroupTypeId.Constraints, DB.SpecTypeId.Length, True)
    for t in fm.Types:
        fm.CurrentType = t
        fm.Set(ws, mm(SETBACK_MM)); fm.Set(fd, front)
    fm.SetDescription(ws, 'Distance the channel front face sits behind the plane or face picked at placement (default 3/4 in).')
    fm.SetDescription(po, 'Placement Plane depth behind the picked plane; drives the insertion point. Do not edit - change Wall Setback.')
    view = elevation_view(doc)
    if op is None or op.Name != 'Placement Plane':
        # Template's own origin plane is constrained to the level; give the origin role to a new plane.
        old = op
        d = DB.XYZ.BasisZ.CrossProduct(view.ViewDirection).Normalize()
        z = front + mm(SETBACK_MM)
        o = DB.XYZ(0, 0, z)
        op = doc.FamilyCreate.NewReferencePlane(o.Add(d.Multiply(mm(300))), o.Subtract(d.Multiply(mm(300))), view.ViewDirection, view)
        op.Name = 'Placement Plane'
        op.get_Parameter(DB.BuiltInParameter.DATUM_PLANE_DEFINES_ORIGIN).Set(1)
        if old is not None:
            old.get_Parameter(DB.BuiltInParameter.DATUM_PLANE_DEFINES_ORIGIN).Set(0)
        job['origin_plane_created'] = True
    doc.Regenerate()
    level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
    oz = op.GetPlane().Origin.Z
    refs = DB.ReferenceArray(); refs.Append(level.GetPlaneReference()); refs.Append(op.GetReference())
    side = DB.XYZ.BasisZ.CrossProduct(view.ViewDirection).Normalize().Multiply(mm(-250))
    if op.Pinned:
        op.Pinned = False; job['origin_plane_unpinned'] = True
    dim = doc.FamilyCreate.NewDimension(view, DB.Line.CreateBound(side, side.Add(DB.XYZ(0, 0, oz))), refs)
    # Label while the parameter equals the drawn value, then let the formula flex the plane.
    for t in fm.Types:
        fm.CurrentType = t; fm.Set(po, dim.Value)
    dim.FamilyLabel = po
    doc.Regenerate()
    fm.SetFormula(po, 'Front Face Depth + Wall Setback')
    doc.Regenerate()
    job['origin_plane_after'] = {'name': op.Name, 'z_mm': to_mm(op.GetPlane().Origin.Z), 'dimension_mm': to_mm(dim.Value)}
    commit(tx, 'wall setback')

    rfa = out_path(dst_name)
    so = DB.SaveAsOptions(); so.OverwriteExistingFile = True; so.MaximumBackups = 1
    check('build %s: save' % kind)
    doc.SaveAs(rfa, so)
    close_doc(doc)
    job['rfa'] = rfa
    return rfa


def channel_solids(proj, inst):
    out = []
    for s in solids(inst.get_Geometry(DB.Options())):
        gs = proj.GetElement(s.GraphicsStyleId)
        if gs is None: raise ValueError('Solid without graphics style; cannot tell channel from accessories')
        if gs.GraphicsStyleCategory.Name == 'Channel Profiles': out.append(s)
    if not out: raise ValueError('No Channel Profiles solids on placed instance')
    return out


def run_extent(pts, p0, d):
    ts = [(p - p0).DotProduct(d) for p in pts]
    return min(ts), max(ts)


def verify(app, rfa, src_path, kind, job):
    fdoc = app.OpenDocumentFile(rfa); open_docs.append(fdoc)
    wp = fdoc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED)
    job['reopened'] = {'placement_type': str(fdoc.OwnerFamily.FamilyPlacementType),
                       'work_plane_based': wp.AsInteger() if wp else None,
                       'origin_plane_z_mm': to_mm(origin_plane(fdoc).GetPlane().Origin.Z)}
    proj = app.NewProjectDocument(DB.UnitSystem.Metric); open_docs.append(proj)
    fam = fdoc.LoadFamily(proj)
    close_doc(fdoc)
    tx = transaction(proj, 'Verify setback')
    fref = clr.Reference[DB.Family]()
    if not proj.LoadFamily(src_path, fref): raise ValueError('Source did not load')
    sym = proj.GetElement(list(fam.GetFamilySymbolIds())[0]); sym.Activate()
    ssym = proj.GetElement(list(fref.Value.GetFamilySymbolIds())[0]); ssym.Activate()
    level = DB.FilteredElementCollector(proj).OfClass(DB.Level).FirstElement()
    lz = level.Elevation
    NS = DB.Structure.StructuralType.NonStructural

    # A. Two clicks on a level (the work-plane case), deliberately off-axis.
    p0 = DB.XYZ(mm(300), mm(200), lz); p1 = DB.XYZ(mm(300 + 1200), mm(200 + 900), lz)
    inst = proj.Create.NewFamilyInstance(DB.Line.CreateBound(p0, p1), sym, level, NS)
    proj.Regenerate()
    c = inst.Location.Curve
    ends = [DB.XYZ(q.X, q.Y, q.Z) for q in (c.GetEndPoint(0), c.GetEndPoint(1))]  # copy now: the curve is live
    d = p1.Subtract(p0).Normalize()
    rows = []
    for setback in (SETBACK_MM, 0.0, 25.4):
        inst.LookupParameter('Wall Setback').Set(mm(setback)); proj.Regenerate()
        pts = points(channel_solids(proj, inst))
        a, b = run_extent(pts, p0, d)
        rows.append({'setback_mm': setback, 'front_below_plane_mm': to_mm(lz - max(p.Z for p in pts)),
                     'back_below_plane_mm': to_mm(lz - min(p.Z for p in pts)), 'run_mm': [to_mm(a), to_mm(b)]})
    inst.LookupParameter('Wall Setback').Set(mm(SETBACK_MM))
    # second click moved: endpoint grip edit
    p2 = p0.Add(d.Multiply(mm(2400)))
    inst.Location.Curve = DB.Line.CreateBound(p0, p2); proj.Regenerate()
    a, b = run_extent(points(channel_solids(proj, inst)), p0, d)
    job_ends = ends
    job['level_two_click'] = {'location_curve_mm': [[to_mm(v) for v in (q.X, q.Y, q.Z)] for q in ends],
                              'clicks_mm': [[to_mm(v) for v in (q.X, q.Y, q.Z)] for q in (p0, p1)],
                              'start_matches_click': job_ends[0].DistanceTo(p0) < 1e-9,
                              'end_matches_click': job_ends[1].DistanceTo(p1) < 1e-9,
                              'clicked_length_mm': to_mm(p0.DistanceTo(p1)), 'setback_rows': rows,
                              'regrip_length_mm': 2400.0, 'regrip_run_mm': [to_mm(a), to_mm(b)],
                              'host': inst.Host.GetType().Name if inst.Host is not None else None}

    # B. Two clicks on a wall face (Place on Face).
    wt = next(t for t in DB.FilteredElementCollector(proj).OfClass(DB.WallType) if t.Kind == DB.WallKind.Basic)
    wall = DB.Wall.Create(proj, DB.Line.CreateBound(DB.XYZ(0, mm(-3000), lz), DB.XYZ(mm(6000), mm(-3000), lz)), wt.Id, level.Id, mm(3000), 0, False, False)
    proj.Regenerate()
    vol_before = sum(s.Volume for s in solids(wall.get_Geometry(DB.Options())))
    fref_w = DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior)[0]
    face = wall.GetGeometryObjectFromReference(fref_w)
    n = face.FaceNormal
    q0 = face.Project(DB.XYZ(mm(1000), mm(-3000), lz + mm(900))).XYZPoint
    run_dir = DB.XYZ.BasisX if kind == 'horizontal' else DB.XYZ.BasisZ
    q1 = q0.Add(run_dir.Multiply(mm(1500)))
    winst = proj.Create.NewFamilyInstance(fref_w, DB.Line.CreateBound(q0, q1), sym)
    proj.Regenerate()
    pts = points(channel_solids(proj, winst))
    depth = [(p - q0).DotProduct(n) for p in pts]
    a, b = run_extent(pts, q0, run_dir)
    vol_after = sum(s.Volume for s in solids(wall.get_Geometry(DB.Options())))
    job['wall_face'] = {'face_normal': [n.X, n.Y, n.Z], 'host': winst.Host.GetType().Name if winst.Host is not None else None,
                        'front_inside_face_mm': -to_mm(max(depth)), 'back_inside_face_mm': -to_mm(min(depth)),
                        'run_mm': [to_mm(a), to_mm(b)], 'clicked_length_mm': 1500.0,
                        'wall_volume_removed_mm3': (vol_before - vol_after) * 304.8 ** 3}

    # C. Regression: same solids as the source, only moved in local Z by the setback change.
    old_front = (job['origin_plane_before']['z_mm'] if job['origin_plane_before'] else 0.0) - job['channel_local_z_mm'][1]
    r0 = DB.XYZ(0, mm(3000), lz); r1 = DB.XYZ(mm(1000), mm(3000), lz)
    ninst = proj.Create.NewFamilyInstance(DB.Line.CreateBound(r0, r1), sym, level, NS)
    sinst = proj.Create.NewFamilyInstance(DB.Line.CreateBound(r0, r1), ssym, level, NS)
    proj.Regenerate()
    def ext(ss):
        ps = points(ss)
        return [to_mm(min(p.X for p in ps)), to_mm(min(p.Y for p in ps)), to_mm(min(p.Z for p in ps)),
                to_mm(max(p.X for p in ps)), to_mm(max(p.Y for p in ps)), to_mm(max(p.Z for p in ps))]
    nss = list(solids(ninst.get_Geometry(DB.Options()))); sss = list(solids(sinst.get_Geometry(DB.Options())))
    job['parity'] = {'source_setback_mm': old_front, 'expected_z_shift_mm': old_front - SETBACK_MM,
                                       'new_volume_mm3': sum(s.Volume for s in nss) * 304.8 ** 3,
                                       'source_volume_mm3': sum(s.Volume for s in sss) * 304.8 ** 3,
                                       'new_extents_mm': ext(nss), 'source_extents_mm': ext(sss)}
    proj.Delete(ninst.Id); proj.Delete(sinst.Id)

    # Review views: cut through the middle of the wall-face run.
    vt = next(v for v in DB.FilteredElementCollector(proj).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    mid = q0.Add(run_dir.Multiply(mm(750)))
    views = []
    v = DB.View3D.CreateIsometric(proj, vt.Id); v.Name = 'Gola ' + kind + ' in wall cut'
    eye = mid.Add(DB.XYZ(mm(-900), mm(-1400), mm(700))); fw = mid.Subtract(eye).Normalize()
    rt = fw.CrossProduct(DB.XYZ.BasisZ).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye, rt.CrossProduct(fw).Normalize(), fw))
    v.DetailLevel = DB.ViewDetailLevel.Fine; v.DisplayStyle = DB.DisplayStyle.ShadingWithEdges; v.Scale = 1
    b = DB.BoundingBoxXYZ()
    if kind == 'horizontal':
        b.Min = DB.XYZ(mid.X, mid.Y - mm(250), mid.Z - mm(120)); b.Max = DB.XYZ(mid.X + mm(200), mid.Y + mm(250), mid.Z + mm(180))
    else:
        b.Min = DB.XYZ(mid.X - mm(150), mid.Y - mm(250), mid.Z); b.Max = DB.XYZ(mid.X + mm(150), mid.Y + mm(250), mid.Z + mm(200))
    v.SetSectionBox(b); v.IsSectionBoxActive = True
    views.append(v)
    commit(tx, 'verify setback')
    job['previews'] = []
    for v in views:
        o = DB.ImageExportOptions(); o.ExportRange = DB.ExportRange.SetOfViews
        o.SetViewsAndSheets(List[DB.ElementId]([v.Id]))
        o.FilePath = out_path('preview', kind + '_in_wall_cut')
        o.HLRandWFViewsFileType = DB.ImageFileType.PNG; o.ShadowViewsFileType = DB.ImageFileType.PNG
        o.ZoomType = DB.ZoomFitType.FitToPage; o.PixelSize = 1600
        proj.ExportImage(o)
        job['previews'].append(o.FilePath)
    close_doc(proj)


try:
    app = __revit__.Application
    __revit__.DialogBoxShowing += on_dialog
    report['revit_version'] = app.VersionNumber
    if app.VersionNumber != '2025': raise ValueError('Revit 2025 required')
    for src_name, dst_name, kind in JOBS:
        job = {'source': src_name, 'output': dst_name, 'orientation': kind}
        report['jobs'].append(job)
        check('build ' + kind)
        rfa = build(app, src_name, dst_name, kind, job)
        check('verify ' + kind)
        verify(app, rfa, out_path('source', src_name), kind, job)
    check('complete')
except Exception:
    report['error'] = traceback.format_exc()
    check('failed: ' + report['stage'])
    raise
finally:
    try: __revit__.DialogBoxShowing -= on_dialog
    except Exception as ex: report.setdefault('close_errors', []).append(str(ex))
    for d in list(open_docs):
        try: d.Close(False)
        except Exception as ex: report.setdefault('close_errors', []).append(str(ex))
