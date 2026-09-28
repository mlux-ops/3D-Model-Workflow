# -*- coding: utf-8 -*-
"""Build and verify the Richelieu Gola Wall Unit Profile (upper-cabinet door pull) as a two-click family.

Run with: pyrevit run "<abs path>/build_wall_unit.py" --revit=2025
Line based: first click = start, second click = end, drawn on the door's front face along its
bottom edge. The door front face lands on the clicked plane (instance Door Face Offset, default 0,
moves the profile out of / into the face). The profile hangs below the line when drawn left to
right as seen facing the door; instance Flip Profile mirrors it for the other direction.
"""
import os, sys, json, math, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RUN = 'E:/Claude/3D-Model-Workflow/output/gola_wall_unit'
sys.path.insert(0, RUN)
import wall_unit_profile as W

TEMPLATE = 'C:/ProgramData/Autodesk/RVT 2025/Family Templates/English-Imperial/Generic Model line based.rft'
RFA = RUN + '/Richelieu_Gola_Wall_Unit_Upper_Cabinet_2025.rfa'
TYPE_NAME = 'Wall Unit - Upper Cabinet Door Pull'
URL = 'https://www.richelieu.com/us/en/category/moldings-corbels-and-components/metal-and-pvc-moldings-profiles-and-rails/gola-cabinet-profiles/gola-wall-unit-profile/1182685'
SKU = '70026804170'
report = {'stage': 'start', 'rfa': RFA, 'section_area_mm2_design': W.section_area_mm2()}
open_docs = []


def out_path(p):
    q = os.path.normpath(p)
    if not q.lower().startswith(os.path.normpath(RUN).lower() + os.sep): raise ValueError('outside run dir: ' + q)
    return q


def check(stage):
    report['stage'] = stage
    with open(out_path(RUN + '/validation.json'), 'w') as f: json.dump(report, f, indent=2, default=str)


def close_doc(doc):
    open_docs[:] = [d for d in open_docs if d is not doc]
    doc.Close(False)


def mm(v): return v / 304.8
def to_mm(v): return v * 304.8


class RecordWarnings(DB.IFailuresPreprocessor):
    def PreprocessFailures(self, accessor):
        rollback = False
        for f in accessor.GetFailureMessages():
            report.setdefault('revit_failures', []).append([report['stage'], str(f.GetSeverity()), f.GetDescriptionText()])
            if f.GetSeverity() == DB.FailureSeverity.Warning: accessor.DeleteWarning(f)
            else: rollback = True
        return DB.FailureProcessingResult.ProceedWithRollBack if rollback else DB.FailureProcessingResult.Continue


def transaction(doc, name):
    tx = DB.Transaction(doc, name)
    o = tx.GetFailureHandlingOptions(); o.SetFailuresPreprocessor(RecordWarnings()); o.SetClearAfterRollback(True)
    tx.SetFailureHandlingOptions(o); tx.Start()
    return tx


def commit(tx, step):
    if tx.Commit() != DB.TransactionStatus.Committed:
        raise ValueError('Transaction "%s" did not commit; see revit_failures' % step)


def on_dialog(sender, args):
    report.setdefault('dialogs_cancelled', []).append(args.DialogId)
    args.OverrideResult(2)


def curve_array(loop, mirror):
    s = -1.0 if mirror else 1.0
    def P(q):
        y, z = W.to_local(q)
        return DB.XYZ(0, mm(s * y), mm(z))
    arr = DB.CurveArray()
    cur = loop[0]
    for item in loop[1:] + [loop[0]]:
        if isinstance(item[0], str):
            arr.Append(DB.Arc.Create(P(cur), P(item[2]), P(item[1]))); cur = item[2]
        else:
            if P(cur).DistanceTo(P(item)) < mm(0.8): raise ValueError('short edge %s-%s' % (cur, item))
            arr.Append(DB.Line.CreateBound(P(cur), P(item))); cur = item
    return arr


def solids(geom):
    for g in geom:
        if isinstance(g, DB.Solid) and g.Volume > 1e-12: yield g
        elif isinstance(g, DB.GeometryInstance):
            for s in solids(g.GetInstanceGeometry()): yield s


def pts(ss): return [p for s in ss for ed in s.Edges for p in ed.Tessellate()]


def build(app):
    doc = app.NewFamilyDocument(TEMPLATE); open_docs.append(doc)
    fm = doc.FamilyManager
    tx = transaction(doc, 'Gola wall unit profile')
    doc.SetUnits(DB.Units(DB.UnitSystem.Metric))
    # The line-based template already has one blank-named type: rename it rather than add a second.
    if fm.Types.Size:
        fm.CurrentType = list(fm.Types)[0]; fm.RenameCurrentType(TYPE_NAME)
    else:
        fm.NewType(TYPE_NAME)
    report['template_types'] = fm.Types.Size
    length = next(p for p in fm.Parameters if p.Definition.Name == 'Length')
    fm.Set(length, mm(1000))
    asset = next(a for a in app.GetAssets(DB.Visual.AssetType.Appearance) if a.Name == 'Metal-029')
    mat = doc.GetElement(DB.Material.Create(doc, 'Gola - Brushed Stainless Finish'))
    mat.MaterialClass = 'Metal'; mat.Color = DB.Color(180, 184, 186); mat.Shininess = 50; mat.Smoothness = 75
    mat.AppearanceAssetId = DB.AppearanceAssetElement.Create(doc, 'Gola - Brushed Stainless Finish', asset).Id
    pm = fm.AddParameter('Profile Material', DB.GroupTypeId.Materials, DB.SpecTypeId.Reference.Material, False)
    fm.Set(pm, mat.Id)
    flip = fm.AddParameter('Flip Profile', DB.GroupTypeId.Constraints, DB.SpecTypeId.Boolean.YesNo, True)
    fm.Set(flip, 0)
    normal = fm.AddParameter('Profile Unflipped', DB.GroupTypeId.Constraints, DB.SpecTypeId.Boolean.YesNo, True)
    fm.SetFormula(normal, 'not(Flip Profile)')
    off = fm.AddParameter('Door Face Offset', DB.GroupTypeId.Constraints, DB.SpecTypeId.Length, True)
    fm.Set(off, 0.0)
    fm.SetDescription(off, 'Moves the profile out of (+) or into (-) the door face you clicked. 0 = door front face on the clicked plane.')
    fm.SetDescription(flip, 'Tick if the profile sits above the line instead of hanging below it (line drawn right to left).')
    texts = {'Profile Type': 'WU', 'Application': 'Upper cabinets - bottom edge of the door',
             'Manufacturer Product Number': SKU, 'Finish': 'Stainless steel look (anodized aluminium)',
             'Base Material': 'Aluminium', 'Other Finishes': '7002680410 aluminium satin; 70026804900 black matte (powder coat)',
             'Door Machining': 'Groove 3 mm wide x 8 mm deep, centred in the edge of an 18 mm door (manufacturer sheet 1344404)',
             'Model Accuracy Notes': 'ART. 268 section 20 x 20 mm, curl 6.5 mm from manufacturer sheet 1344403. Wall ~1.1 mm, tongue ~7 mm / barb ~3 mm, scoop and teardrop curves measured from the drawing; approximations.'}
    for n, v in texts.items():
        p = fm.AddParameter(n, DB.GroupTypeId.IdentityData, DB.SpecTypeId.String.Text, False); fm.Set(p, v)
    for n, v in [('Profile Width', 20.0), ('Profile Height', 20.0), ('Stock Length', 4000.0)]:
        p = fm.AddParameter(n, DB.GroupTypeId.Geometry, DB.SpecTypeId.Length, False); fm.Set(p, mm(v))
    for b, v in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, 'Richelieu Hardware'), (DB.BuiltInParameter.ALL_MODEL_MODEL, SKU),
                 (DB.BuiltInParameter.ALL_MODEL_URL, URL),
                 (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION, 'Gola wall unit profile (ART. 268) for upper cabinet doors; two-click line based')]:
        p = fm.get_Parameter(b)
        if p: fm.Set(p, v)
    sub = doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory, 'Channel Profiles')
    sp = DB.SketchPlane.Create(doc, DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisX, DB.XYZ.Zero))
    forms = []
    for mirror, vis in [(False, normal), (True, flip)]:
        loops = DB.CurveArrArray(); loops.Append(curve_array(W.OUTER, mirror)); loops.Append(curve_array(W.HOLE, mirror))
        e = doc.FamilyCreate.NewExtrusion(True, loops, sp, mm(1000))
        e.Subcategory = sub
        e.get_Parameter(DB.BuiltInParameter.EXTRUSION_START_PARAM).Set(0.0)
        fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM), length)
        fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), pm)
        fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.IS_VISIBLE_PARAM), vis)
        forms.append(e)
    doc.Regenerate()
    report['family_form_volumes_mm3'] = [sum(s.Volume for s in solids(e.get_Geometry(DB.Options()))) * 304.8 ** 3 for e in forms]

    # Origin: Placement Plane at z = 50 mm - Door Face Offset defines the insertion depth.
    view = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.View)
                if not v.IsTemplate and v.ViewType == DB.ViewType.Elevation and abs(v.ViewDirection.Z) < 1e-9)
    old = [r for r in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane)
           if r.get_Parameter(DB.BuiltInParameter.DATUM_PLANE_DEFINES_ORIGIN).AsInteger() == 1 and abs(abs(r.GetPlane().Normal.Z) - 1) < 1e-9]
    d = DB.XYZ.BasisZ.CrossProduct(view.ViewDirection).Normalize()
    o = DB.XYZ(0, 0, mm(W.FACE_BASE_MM))
    plane = doc.FamilyCreate.NewReferencePlane(o.Add(d.Multiply(mm(300))), o.Subtract(d.Multiply(mm(300))), view.ViewDirection, view)
    plane.Name = 'Placement Plane'
    plane.get_Parameter(DB.BuiltInParameter.DATUM_PLANE_DEFINES_ORIGIN).Set(1)
    for r in old: r.get_Parameter(DB.BuiltInParameter.DATUM_PLANE_DEFINES_ORIGIN).Set(0)
    doc.Regenerate()
    po = fm.AddParameter('Placement Offset', DB.GroupTypeId.Constraints, DB.SpecTypeId.Length, True)
    fm.SetDescription(po, 'Internal: drives the Placement Plane. Do not edit - use Door Face Offset.')
    level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
    refs = DB.ReferenceArray(); refs.Append(level.GetPlaneReference()); refs.Append(plane.GetReference())
    side = d.Multiply(mm(-250))
    dim = doc.FamilyCreate.NewDimension(view, DB.Line.CreateBound(side, side.Add(DB.XYZ(0, 0, mm(W.FACE_BASE_MM)))), refs)
    fm.Set(po, dim.Value)
    dim.FamilyLabel = po
    doc.Regenerate()
    fm.SetFormula(po, '%g mm - Door Face Offset' % W.FACE_BASE_MM)
    doc.Regenerate()
    report['placement_plane_mm'] = to_mm(plane.GetPlane().Origin.Z)
    report['old_origin_planes_cleared'] = [r.Name for r in old]
    commit(tx, 'build family')
    so = DB.SaveAsOptions(); so.OverwriteExistingFile = True; so.MaximumBackups = 1
    check('save')
    doc.SaveAs(out_path(RFA), so)
    close_doc(doc)


def extents(ss):
    ps = pts(ss)
    return [to_mm(min(p.X for p in ps)), to_mm(min(p.Y for p in ps)), to_mm(min(p.Z for p in ps)),
            to_mm(max(p.X for p in ps)), to_mm(max(p.Y for p in ps)), to_mm(max(p.Z for p in ps))]


def rel(ss, origin, axes):
    """Extents of the solids in a frame (origin, list of unit axes), mm."""
    ps = pts(ss)
    out = []
    for a in axes:
        v = [(p - origin).DotProduct(a) for p in ps]
        out.append([to_mm(min(v)), to_mm(max(v))])
    return out


def verify(app):
    fdoc = app.OpenDocumentFile(out_path(RFA)); open_docs.append(fdoc)
    report['reopened'] = {'placement_type': str(fdoc.OwnerFamily.FamilyPlacementType), 'types': [t.Name for t in fdoc.FamilyManager.Types]}
    proj = app.NewProjectDocument(DB.UnitSystem.Metric); open_docs.append(proj)
    fam = fdoc.LoadFamily(proj); close_doc(fdoc)
    tx = transaction(proj, 'verify')
    sym = proj.GetElement(list(fam.GetFamilySymbolIds())[0]); sym.Activate()
    level = DB.FilteredElementCollector(proj).OfClass(DB.Level).FirstElement()
    NS = DB.Structure.StructuralType.NonStructural
    t = {}

    # A. two clicks on a level
    p0 = DB.XYZ(0, 0, 0); p1 = DB.XYZ(mm(1500), 0, 0)
    a = proj.Create.NewFamilyInstance(DB.Line.CreateBound(p0, p1), sym, level, NS); proj.Regenerate()
    c = a.Location.Curve
    ends = [DB.XYZ(q.X, q.Y, q.Z) for q in (c.GetEndPoint(0), c.GetEndPoint(1))]
    ss = list(solids(a.get_Geometry(DB.Options())))
    t['A_level'] = {'start_ok': ends[0].DistanceTo(p0) < 1e-9, 'end_ok': ends[1].DistanceTo(p1) < 1e-9,
                    'extents_mm': extents(ss), 'volume_mm3': sum(s.Volume for s in ss) * 304.8 ** 3, 'length_mm': 1500.0,
                    'host': a.Host.GetType().Name if a.Host else None}
    a.Location.Curve = DB.Line.CreateBound(p0, p0.Add(DB.XYZ.BasisX.Multiply(mm(2400)))); proj.Regenerate()
    ss = list(solids(a.get_Geometry(DB.Options())))
    t['A_regrip'] = {'extents_mm': extents(ss), 'volume_mm3': sum(s.Volume for s in ss) * 304.8 ** 3, 'length_mm': 2400.0}
    face_mats = set(proj.GetElement(f.MaterialElementId).Name for s in ss for f in s.Faces if proj.GetElement(f.MaterialElementId))
    t['materials'] = sorted(face_mats)

    # B/C/D. On a wall face ("door face"), drawn left->right and right->left as seen facing it
    wt = next(x for x in DB.FilteredElementCollector(proj).OfClass(DB.WallType) if x.Kind == DB.WallKind.Basic)
    wall = DB.Wall.Create(proj, DB.Line.CreateBound(DB.XYZ(0, mm(-3000), 0), DB.XYZ(mm(6000), mm(-3000), 0)), wt.Id, level.Id, mm(3000), 0, False, False)
    proj.Regenerate()
    ref = DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior)[0]
    face = wall.GetGeometryObjectFromReference(ref)
    n = face.FaceNormal
    right = n.Negate().CrossProduct(DB.XYZ.BasisZ).Normalize()   # viewer faces -n; right = forward x up
    q0 = face.Project(DB.XYZ(mm(1000), mm(-3000), mm(1400))).XYZPoint
    axes = [right, DB.XYZ.BasisZ, n]    # run, up, out of face
    rows = {}
    for label, s0, s1 in [('left_to_right', q0, q0.Add(right.Multiply(mm(1500)))),
                          ('right_to_left', q0.Add(right.Multiply(mm(1500))), q0)]:
        inst = proj.Create.NewFamilyInstance(ref, DB.Line.CreateBound(s0, s1), sym); proj.Regenerate()
        r = {'unflipped': rel(list(solids(inst.get_Geometry(DB.Options()))), q0, axes)}
        inst.LookupParameter('Flip Profile').Set(1); proj.Regenerate()
        r['flipped'] = rel(list(solids(inst.get_Geometry(DB.Options()))), q0, axes)
        inst.LookupParameter('Flip Profile').Set(0)
        if label == 'left_to_right':
            inst.LookupParameter('Door Face Offset').Set(mm(5)); proj.Regenerate()
            r['offset_5mm'] = rel(list(solids(inst.get_Geometry(DB.Options()))), q0, axes)
            inst.LookupParameter('Door Face Offset').Set(0); proj.Regenerate()
            keep = inst
        else:
            proj.Delete(inst.Id)
        rows[label] = r
    t['wall_face'] = rows
    t['wall_face_host'] = keep.Host.GetType().Name if keep.Host else None
    report['tests'] = t

    # preview: section cut at mid-run of the left->right instance, walls hidden
    vt = next(v for v in DB.FilteredElementCollector(proj).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    v = DB.View3D.CreateIsometric(proj, vt.Id); v.Name = 'Gola wall unit section'
    mid = q0.Add(right.Multiply(mm(750)))
    eye = mid.Add(right.Multiply(mm(-600))).Add(n.Multiply(mm(700))).Add(DB.XYZ(0, 0, mm(-300)))
    fw = mid.Subtract(eye).Normalize(); rt = fw.CrossProduct(DB.XYZ.BasisZ).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye, rt.CrossProduct(fw).Normalize(), fw))
    v.DetailLevel = DB.ViewDetailLevel.Fine; v.DisplayStyle = DB.DisplayStyle.ShadingWithEdges; v.Scale = 1
    v.SetCategoryHidden(DB.ElementId(DB.BuiltInCategory.OST_Walls), True)
    b = DB.BoundingBoxXYZ()
    lo = [mid.X, mid.Y, mid.Z]; b.Min = DB.XYZ(mid.X - mm(40), mid.Y - mm(40), mid.Z - mm(40)); b.Max = DB.XYZ(mid.X + mm(150), mid.Y + mm(40), mid.Z + mm(40))
    # box spans the run direction on the +right side only, so the cut face shows the section
    if abs(right.X) < 0.5: b.Min = DB.XYZ(mid.X - mm(40), mid.Y - mm(150), mid.Z - mm(40)); b.Max = DB.XYZ(mid.X + mm(40), mid.Y + mm(40), mid.Z + mm(40))
    v.SetSectionBox(b); v.IsSectionBoxActive = True
    commit(tx, 'verify')
    o = DB.ImageExportOptions(); o.ExportRange = DB.ExportRange.SetOfViews
    o.SetViewsAndSheets(List[DB.ElementId]([v.Id])); o.FilePath = out_path(RUN + '/preview/wall_unit_section')
    o.HLRandWFViewsFileType = DB.ImageFileType.PNG; o.ShadowViewsFileType = DB.ImageFileType.PNG
    o.ZoomType = DB.ZoomFitType.FitToPage; o.PixelSize = 1600
    proj.ExportImage(o)
    report['preview'] = o.FilePath
    close_doc(proj)


try:
    app = __revit__.Application
    __revit__.DialogBoxShowing += on_dialog
    if app.VersionNumber != '2025': raise ValueError('Revit 2025 required')
    if not os.path.isdir(RUN + '/preview'): os.makedirs(RUN + '/preview')
    check('build'); build(app)
    check('verify'); verify(app)
    check('complete')
except Exception:
    report['error'] = traceback.format_exc(); check('failed: ' + report['stage']); raise
finally:
    try: __revit__.DialogBoxShowing -= on_dialog
    except Exception as ex: report.setdefault('close_errors', []).append(str(ex))
    for dd in list(open_docs):
        try: dd.Close(False)
        except Exception as ex: report.setdefault('close_errors', []).append(str(ex))
