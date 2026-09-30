# -*- coding: utf-8 -*-
"""Build and verify the Richelieu Gola Wall Unit Profile (upper-cabinet door pull) as a two-click family.

Run with: pyrevit run "<abs path>/build_wall_unit.py" --revit=2025
Line based: first click = start, second click = end, drawn on the cabinet's front face along its
bottom edge (the cabinets are solid boxes; the door is not a separate panel). The front face lands on
the clicked plane set back by instance Wall Setback (default 3/4 in = 19.05 mm, measured to the profile's
front face, as in the base-cabinet Gola families) and the profile sits in the bottom 20 mm of
the box, above the line, when drawn left to right facing the cabinet; Flip Profile mirrors it.
Two unattached recess voids (one each side of the line; the unused one parks in the air in front
of the face) cut the box band from 3 mm in front of the face to Cut Depth behind the profile front
(default 20 mm), so the recess stays open to the face whatever the setback. The GolaAutoCut
extension applies the cut to the touched cabinet or wall.
"""
import os, sys, json, math, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RUN = 'E:/Claude/3D-Model-Workflow/output/gola_wall_unit'
sys.path.insert(0, RUN)
import wall_unit_profile as W
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/gola_setback/pyrevit/GolaAutoCut.extension/lib')
import gola_autocut
CASEWORK_TEMPLATE = 'C:/ProgramData/Autodesk/RVT 2025/Family Templates/English-Imperial/Casework.rft'

TEMPLATE = 'C:/ProgramData/Autodesk/RVT 2025/Family Templates/English-Imperial/Generic Model line based.rft'
RFA = RUN + '/Richelieu_Gola_Wall_Unit_Upper_Cabinet_2025.rfa'
TYPE_NAME = 'Wall Unit - Upper Cabinet Door Pull'
URL = 'https://www.richelieu.com/us/en/category/moldings-corbels-and-components/metal-and-pvc-moldings-profiles-and-rails/gola-cabinet-profiles/gola-wall-unit-profile/1182685'
SKU = '70026804170'
SETBACK_MM = 19.05
PROFILE_FRONT = W.FACE_BASE_MM + (20.0 - W.DOOR_FACE_YD)   # family z of the leg's outer face (51 mm)
report = {'stage': 'start', 'rfa': RFA, 'section_area_mm2_design': W.section_area_mm2(), 'setback_default_mm': SETBACK_MM}
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
    ws = fm.AddParameter('Wall Setback', DB.GroupTypeId.Constraints, DB.SpecTypeId.Length, True)
    fm.Set(ws, mm(SETBACK_MM))
    fm.SetDescription(ws, 'Distance the profile front face sits behind the face or plane picked at placement (default 3/4 in).')
    fm.SetDescription(flip, 'Tick if the profile lands below the line, outside the cabinet (line drawn right to left).')
    texts = {'Profile Type': 'WU', 'Application': 'Upper cabinets - bottom edge of the door (click the cabinet front bottom edge)',
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

    # Recess voids: sketched flat (normal Z) with their end edges locked to the line's Left/Right
    # planes so they follow both clicks; extruded through the depth by formula. API-created voids
    # stay unattached (they do not cut the profile), which lets them cut the cabinet in the project.
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALLOW_CUT_WITH_VOIDS).Set(1)
    cutd = fm.AddParameter('Cut Depth', DB.GroupTypeId.Constraints, DB.SpecTypeId.Length, True)
    fm.Set(cutd, mm(20))
    fm.SetDescription(cutd, 'How far the recess is cut behind the profile front face. 20 mm clears the profile; use the cabinet depth to cut the full band.')
    pf = PROFILE_FRONT
    # Clicked face is at family z = pf + Wall Setback. The void runs from pf - Cut Depth to 3 mm in front
    # of the clicked face; the unused void parks at 2..3 mm in front of the face (air).
    rfront = fm.AddParameter('Recess Front', DB.GroupTypeId.Constraints, DB.SpecTypeId.Length, True)
    fm.SetFormula(rfront, '%g mm + Wall Setback' % (pf + 3))
    fm.SetDescription(rfront, 'Internal: recess void front, 3 mm in front of the clicked face. Do not edit.')
    front = pf + 3.0
    starts = []
    for n, f in [('Recess Start Above', 'if(Flip Profile, %g mm + Wall Setback, %g mm - Cut Depth)' % (pf + 2, pf)),
                 ('Recess Start Below', 'if(Flip Profile, %g mm - Cut Depth, %g mm + Wall Setback)' % (pf, pf + 2))]:
        p = fm.AddParameter(n, DB.GroupTypeId.Constraints, DB.SpecTypeId.Length, True); fm.SetFormula(p, f)
        fm.SetDescription(p, 'Internal: recess void depth. Do not edit - use Cut Depth.')
        starts.append(p)
    plan = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewPlan) if v.ViewType == DB.ViewType.FloorPlan and not v.IsTemplate)
    planes = dict((r.Name, r) for r in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane))
    spz = DB.SketchPlane.Create(doc, DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisZ, DB.XYZ.Zero))
    voids = []
    for (y0, y1), sp_ in zip([(-1.0, W.PROFILE_H), (-W.PROFILE_H, 1.0)], starts):
        c = [DB.XYZ(0, mm(y0), 0), DB.XYZ(mm(1000), mm(y0), 0), DB.XYZ(mm(1000), mm(y1), 0), DB.XYZ(0, mm(y1), 0)]
        arr = DB.CurveArray()
        for i in range(4): arr.Append(DB.Line.CreateBound(c[i], c[(i + 1) % 4]))
        loops = DB.CurveArrArray(); loops.Append(arr)
        v = doc.FamilyCreate.NewExtrusion(False, loops, spz, mm(front))
        fm.AssociateElementParameterToFamilyParameter(v.get_Parameter(DB.BuiltInParameter.EXTRUSION_START_PARAM), sp_)
        fm.AssociateElementParameterToFamilyParameter(v.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM), rfront)
        doc.Regenerate()
        for cv in [cv for loop in v.Sketch.Profile for cv in loop]:
            if abs(cv.Direction.Y) > 0.9:
                x = cv.Evaluate(0.5, True).X
                doc.FamilyCreate.NewAlignment(plan, (planes['Left'] if abs(x) < mm(0.1) else planes['Right']).GetReference(), cv.Reference)
        voids.append(v)
    doc.Regenerate()
    after = [sum(s.Volume for s in solids(e.get_Geometry(DB.Options()))) * 304.8 ** 3 for e in forms]
    report['family_form_volumes_after_voids_mm3'] = after
    if any(abs(a - b) > 0.01 for a, b in zip(after, report['family_form_volumes_mm3'])):
        raise ValueError('Recess void cut the profile solid (not unattached)')

    # Origin: Placement Plane at z = profile front (51 mm) + Wall Setback defines the insertion depth.
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
    fm.SetDescription(po, 'Internal: drives the Placement Plane. Do not edit - use Wall Setback.')
    level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
    refs = DB.ReferenceArray(); refs.Append(level.GetPlaneReference()); refs.Append(plane.GetReference())
    side = d.Multiply(mm(-250))
    dim = doc.FamilyCreate.NewDimension(view, DB.Line.CreateBound(side, side.Add(DB.XYZ(0, 0, mm(W.FACE_BASE_MM)))), refs)
    fm.Set(po, dim.Value)
    dim.FamilyLabel = po
    doc.Regenerate()
    fm.SetFormula(po, '%g mm + Wall Setback' % PROFILE_FRONT)
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


def box_family(app, name, allow_cut):
    """Test cabinet: a solid Casework box 2000 x 400 x 700 mm whose top face is at its level (z -700..0),
    so a Gola drawn on the level along its y = 0 edge sits exactly as on a cabinet's bottom front edge."""
    doc = app.NewFamilyDocument(CASEWORK_TEMPLATE); open_docs.append(doc)
    tx = transaction(doc, 'box')
    c = [DB.XYZ(0, 0, 0), DB.XYZ(mm(2000), 0, 0), DB.XYZ(mm(2000), mm(400), 0), DB.XYZ(0, mm(400), 0)]
    arr = DB.CurveArray()
    for i in range(4): arr.Append(DB.Line.CreateBound(c[i], c[(i + 1) % 4]))
    loops = DB.CurveArrArray(); loops.Append(arr)
    e = doc.FamilyCreate.NewExtrusion(True, loops, DB.SketchPlane.Create(doc, DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisZ, DB.XYZ.Zero)), mm(700))
    e.get_Parameter(DB.BuiltInParameter.EXTRUSION_START_PARAM).Set(mm(-700)); e.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM).Set(0.0)
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALLOW_CUT_WITH_VOIDS).Set(1 if allow_cut else 0)
    commit(tx, 'box family')
    path = RUN + '/test_families/' + name + '.rfa'
    if not os.path.isdir(RUN + '/test_families'): os.makedirs(RUN + '/test_families')
    so = DB.SaveAsOptions(); so.OverwriteExistingFile = True; so.MaximumBackups = 1
    doc.SaveAs(out_path(path), so); close_doc(doc)
    return path


def vol_mm3(e): return sum(s.Volume for s in solids(e.get_Geometry(DB.Options()))) * 304.8 ** 3


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
    q0 = face.Project(DB.XYZ(mm(3000), mm(-3000), mm(1400))).XYZPoint   # mid-wall: a 1500 mm run either way stays on the wall
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
            inst.LookupParameter('Wall Setback').Set(0.0); proj.Regenerate()
            r['setback_0'] = rel(list(solids(inst.get_Geometry(DB.Options()))), q0, axes)
            inst.LookupParameter('Wall Setback').Set(mm(25.4)); proj.Regenerate()
            r['setback_1in'] = rel(list(solids(inst.get_Geometry(DB.Options()))), q0, axes)
            inst.LookupParameter('Wall Setback').Set(mm(SETBACK_MM)); proj.Regenerate()
            keep = inst
        else:
            proj.Delete(inst.Id)
        rows[label] = r
    t['wall_face'] = rows
    t['wall_face_run_direction'] = [right.X, right.Y, right.Z]
    t['wall_face_host'] = keep.Host.GetType().Name if keep.Host else None
    report['tests'] = t

    # E. Cutting solid cabinets (Casework boxes) and the wall, through the GolaAutoCut module.
    # apply() runs its own transactions, so the placement transaction is committed first.
    commit(tx, 'verify placement')
    cut = {}
    tx = transaction(proj, 'cut test setup')
    boxes = {}
    for key, allow, y in [('cuttable', True, 5000), ('blocked', False, 8000)]:
        ref_ = clr.Reference[DB.Family]()
        if not proj.LoadFamily(out_path(box_family(app, 'Test_Cabinet_Box_' + key, allow)), ref_): raise ValueError('box did not load')
        bs = proj.GetElement(list(ref_.Value.GetFamilySymbolIds())[0]); bs.Activate()
        boxes[key] = proj.Create.NewFamilyInstance(DB.XYZ(0, mm(y), 0), bs, level, NS)
    proj.Regenerate()
    base = dict((k, vol_mm3(b)) for k, b in boxes.items())
    g1 = proj.Create.NewFamilyInstance(DB.Line.CreateBound(DB.XYZ(mm(250), mm(5000), 0), DB.XYZ(mm(1750), mm(5000), 0)), sym, level, NS)
    g2 = proj.Create.NewFamilyInstance(DB.Line.CreateBound(DB.XYZ(mm(250), mm(8000), 0), DB.XYZ(mm(1750), mm(8000), 0)), sym, level, NS)
    commit(tx, 'cut test setup')
    prof = vol_mm3(g1)
    def run(label, **params):
        if params:
            t2 = transaction(proj, 'params ' + label)
            for n, v in params.items(): g1.LookupParameter(n.replace('_', ' ')).Set(v)
            commit(t2, 'params ' + label)
        row = gola_autocut.apply(proj, [g1])[0]
        cut[label] = {'removed_mm3': base['cuttable'] - vol_mm3(boxes['cuttable']), 'profile_mm3': vol_mm3(g1),
                      'added': row[1], 'removed_ids': row[2], 'blocked': row[3], 'refused': row[4]}
    run('box_depth_20')
    run('box_depth_300', Cut_Depth=mm(300))
    run('box_depth_300_flipped', Flip_Profile=1)
    t2 = transaction(proj, 'reset'); g1.LookupParameter('Flip Profile').Set(0); g1.LookupParameter('Cut Depth').Set(mm(20)); commit(t2, 'reset')
    row = gola_autocut.apply(proj, [g2])[0]
    cut['blocked_box'] = {'removed_mm3': base['blocked'] - vol_mm3(boxes['blocked']), 'added': row[1], 'blocked': row[3], 'refused': row[4]}
    wv = vol_mm3(wall)
    row = gola_autocut.apply(proj, [keep])[0]
    cut['wall_face'] = {'removed_mm3': wv - vol_mm3(wall), 'added': row[1], 'refused': row[4], 'profile_mm3': vol_mm3(keep)}
    cut['profile_mm3_uncut'] = prof
    cut['length_mm'] = 1500.0
    report['tests']['cuts'] = cut
    tx = transaction(proj, 'preview view')

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
