# -*- coding: utf-8 -*-
"""Build and verify the Richelieu Gola Wall Unit Profile (upper-cabinet door pull) as a two-click family.

Run with: pyrevit run "<abs path>/build_wall_unit.py" --revit=2025
Line based: first click = start, second click = end, drawn on the UNDERSIDE of the upper cabinet along
its front edge (the cabinets are solid boxes; the door is not a separate panel). Rebuilt 2026-10-02:
the 2026-09-28 build expected the front face and came out rotated 90 degrees on the underside.
Family frame on the clicked face: x along the run, z out of the face (down), y = z cross x (towards
the cabinet front when drawn left to right facing the cabinet). The profile sits in the box: its
bottom on the clicked underside, its front face Wall Setback (default 3/4 in) behind the front edge,
web and tongue up into the box. Flip Profile mirrors it across the line (for runs drawn right to
left). One unattached recess void cuts the band 20 mm up from the underside (+1 mm below it), from
3 mm in front of the front edge to Cut Depth behind the profile front face. The GolaAutoCut
extension applies the cut to the touched cabinet.
Plane Faces Up (2026-10-02): mirrors profile and void in z for a work plane whose normal points up
(a level). GolaAutoCut uses it to swap a channel face-hosted on an in-place family (which Revit
cannot cut without a circular chain of references) for an identical unhosted copy on a level.
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
PROFILE_FRONT = W.FACE_BASE_MM + (20.0 - W.DOOR_FACE_YD)   # to_local z of the profile front face (51 mm)
FRONT_Y = -100.0      # family y of the unflipped profile front face; the flipped copy mirrors to +100
DATUM_Y = -1000.0     # fixed, pinned plane that the Placement Plane and the void are measured from
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


def curve_array(loop, mirror, up=False):
    """Section in the underside frame: to_local height above the line -> -z (up into the box);
    to_local out-of-face depth -> y, with the profile front face at y = FRONT_Y (mirror: -FRONT_Y).
    up mirrors z (height -> +z) for a work plane facing up (Plane Faces Up)."""
    s = -1.0 if mirror else 1.0
    sz = 1.0 if up else -1.0
    def P(q):
        h, o = W.to_local(q)
        return DB.XYZ(0, mm(s * (o - PROFILE_FRONT + FRONT_Y)), mm(sz * h))
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
    upp = fm.AddParameter('Plane Faces Up', DB.GroupTypeId.Constraints, DB.SpecTypeId.Boolean.YesNo, True)
    fm.Set(upp, 0)
    fm.SetDescription(upp, 'Tick when placed on a level or a plane facing up (the profile then rises above the plane). Set automatically by the GolaAutoCut add-in.')
    vis_params = {}
    for (m, u), (n, f) in zip([(False, False), (True, False), (False, True), (True, True)],
                              [('Show Profile', 'and(not(Flip Profile), not(Plane Faces Up))'),
                               ('Show Profile Flipped', 'and(Flip Profile, not(Plane Faces Up))'),
                               ('Show Profile Up', 'and(not(Flip Profile), Plane Faces Up)'),
                               ('Show Profile Up Flipped', 'and(Flip Profile, Plane Faces Up)')]):
        vp = fm.AddParameter(n, DB.GroupTypeId.Constraints, DB.SpecTypeId.Boolean.YesNo, True)
        fm.SetFormula(vp, f); fm.SetDescription(vp, 'Internal. Do not edit.')
        vis_params[(m, u)] = vp
    ws = fm.AddParameter('Wall Setback', DB.GroupTypeId.Constraints, DB.SpecTypeId.Length, True)
    fm.Set(ws, mm(SETBACK_MM))
    fm.SetDescription(ws, 'Distance the profile front face sits behind the face or plane picked at placement (default 3/4 in).')
    fm.SetDescription(flip, 'Tick if the profile lands in front of the cabinet instead of inside it (line drawn right to left).')
    texts = {'Profile Type': 'WU', 'Application': 'Upper cabinets - bottom edge of the door (Place on Face: the cabinet underside, click along its front edge)',
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
    for (mirror, up), vis in sorted(vis_params.items()):
        loops = DB.CurveArrArray(); loops.Append(curve_array(W.OUTER, mirror, up)); loops.Append(curve_array(W.HOLE, mirror, up))
        e = doc.FamilyCreate.NewExtrusion(True, loops, sp, mm(1000))
        e.Subcategory = sub
        e.get_Parameter(DB.BuiltInParameter.EXTRUSION_START_PARAM).Set(0.0)
        fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM), length)
        fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), pm)
        fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.IS_VISIBLE_PARAM), vis)
        forms.append(e)
    doc.Regenerate()
    report['family_form_volumes_mm3'] = [sum(s.Volume for s in solids(e.get_Geometry(DB.Options()))) * 304.8 ** 3 for e in forms]

    # Recess void: sketched on a fixed y plane (the pinned Setback Datum) as the band 20 mm up from the
    # underside (+1 mm below it), its end edges locked to the line's Left/Right planes so it follows
    # both clicks, extruded along y by formula. API-created voids stay unattached (they do not cut the
    # profile), which lets them cut the cabinet in the project.
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALLOW_CUT_WITH_VOIDS).Set(1)
    cutd = fm.AddParameter('Cut Depth', DB.GroupTypeId.Constraints, DB.SpecTypeId.Length, True)
    fm.Set(cutd, mm(20))
    fm.SetDescription(cutd, 'How far the recess is cut behind the profile front face. 20 mm clears the profile; use the cabinet depth to cut the full band.')
    fa = FRONT_Y - DATUM_Y        # 900: unflipped profile front face, measured from the datum
    fb = -FRONT_Y - DATUM_Y       # 1100: flipped profile front face
    # Unflipped: void y from the profile front - Cut Depth to 3 mm in front of the clicked edge
    # (front + Wall Setback + 3); flipped: the mirror image.
    # The void for the other plane direction parks 2..3 mm in front of the clicked edge (air).
    act_s = 'if(Flip Profile, %g mm - Wall Setback, %g mm - Cut Depth)' % (fb - 3, fa)
    act_e = 'if(Flip Profile, %g mm + Cut Depth, %g mm + Wall Setback)' % (fb, fa + 3)
    park_s = 'if(Flip Profile, %g mm - Wall Setback, %g mm + Wall Setback)' % (fb - 3, fa + 2)
    park_e = 'if(Flip Profile, %g mm - Wall Setback, %g mm + Wall Setback)' % (fb - 2, fa + 3)
    void_params = []
    for n, up in [('Recess', False), ('Recess Up', True)]:
        pair = []
        for end, (a_, k_) in [('Start', (act_s, park_s)), ('End', (act_e, park_e))]:
            p_ = fm.AddParameter('%s %s' % (n, end), DB.GroupTypeId.Constraints, DB.SpecTypeId.Length, True)
            fm.SetFormula(p_, 'if(Plane Faces Up, %s, %s)' % ((a_, k_) if up else (k_, a_)))
            fm.SetDescription(p_, 'Internal: recess void extent. Do not edit - use Cut Depth and Wall Setback.')
            pair.append(p_)
        void_params.append((up, pair[0], pair[1]))
    plan = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewPlan) if v.ViewType == DB.ViewType.FloorPlan and not v.IsTemplate)
    elev = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.View)
                if not v.IsTemplate and v.ViewType == DB.ViewType.Elevation and abs(v.ViewDirection.Y) > 0.99)
    planes = dict((r.Name, r) for r in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane))
    datum = doc.FamilyCreate.NewReferencePlane(DB.XYZ(mm(-300), mm(DATUM_Y), 0), DB.XYZ(mm(1300), mm(DATUM_Y), 0), DB.XYZ.BasisZ, plan)
    datum.Name = 'Setback Datum'
    datum.Pinned = True
    spy = DB.SketchPlane.Create(doc, DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisY, DB.XYZ(0, mm(DATUM_Y), 0)))
    for up, rs, re_ in void_params:
        z0, z1 = (-1.0, W.PROFILE_H) if up else (-W.PROFILE_H, 1.0)
        c = [DB.XYZ(0, mm(DATUM_Y), mm(z1)), DB.XYZ(mm(1000), mm(DATUM_Y), mm(z1)),
             DB.XYZ(mm(1000), mm(DATUM_Y), mm(z0)), DB.XYZ(0, mm(DATUM_Y), mm(z0))]
        arr = DB.CurveArray()
        for i in range(4): arr.Append(DB.Line.CreateBound(c[i], c[(i + 1) % 4]))
        loops = DB.CurveArrArray(); loops.Append(arr)
        v = doc.FamilyCreate.NewExtrusion(False, loops, spy, mm(fa + 3 + SETBACK_MM))
        fm.AssociateElementParameterToFamilyParameter(v.get_Parameter(DB.BuiltInParameter.EXTRUSION_START_PARAM), rs)
        fm.AssociateElementParameterToFamilyParameter(v.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM), re_)
        doc.Regenerate()
        for cv in [cv for loop in v.Sketch.Profile for cv in loop]:
            if abs(cv.Direction.Z) > 0.9:
                x = cv.Evaluate(0.5, True).X
                doc.FamilyCreate.NewAlignment(elev, (planes['Left'] if abs(x) < mm(0.1) else planes['Right']).GetReference(), cv.Reference)
        doc.Regenerate()
    after = [sum(s.Volume for s in solids(e.get_Geometry(DB.Options()))) * 304.8 ** 3 for e in forms]
    report['family_form_volumes_after_voids_mm3'] = after
    if any(abs(a - b) > 0.01 for a, b in zip(after, report['family_form_volumes_mm3'])):
        raise ValueError('Recess void cut the profile solid (not unattached)')

    # Origin: a y-normal Placement Plane on the clicked front edge, Wall Setback in front of the profile
    # front face (unflipped y = -100 + Wall Setback; flipped y = 100 - Wall Setback), driven from the datum.
    old = [r for r in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane)
           if r.get_Parameter(DB.BuiltInParameter.DATUM_PLANE_DEFINES_ORIGIN).AsInteger() == 1 and abs(abs(r.GetPlane().Normal.Y) - 1) < 1e-9]
    y0 = mm(FRONT_Y + SETBACK_MM)
    plane = doc.FamilyCreate.NewReferencePlane(DB.XYZ(mm(-300), y0, 0), DB.XYZ(mm(1300), y0, 0), DB.XYZ.BasisZ, plan)
    plane.Name = 'Placement Plane'
    for r in old: r.get_Parameter(DB.BuiltInParameter.DATUM_PLANE_DEFINES_ORIGIN).Set(0)
    plane.get_Parameter(DB.BuiltInParameter.DATUM_PLANE_DEFINES_ORIGIN).Set(1)
    doc.Regenerate()
    po = fm.AddParameter('Placement Offset', DB.GroupTypeId.Constraints, DB.SpecTypeId.Length, True)
    fm.SetDescription(po, 'Internal: drives the Placement Plane. Do not edit - use Wall Setback.')
    refs = DB.ReferenceArray(); refs.Append(datum.GetReference()); refs.Append(plane.GetReference())
    dim = doc.FamilyCreate.NewDimension(plan, DB.Line.CreateBound(DB.XYZ(mm(-250), mm(DATUM_Y), 0), DB.XYZ(mm(-250), y0, 0)), refs)
    fm.Set(po, dim.Value)
    dim.FamilyLabel = po
    doc.Regenerate()
    fm.SetFormula(po, 'if(Flip Profile, %g mm - Wall Setback, %g mm + Wall Setback)' % (fb, fa))
    doc.Regenerate()
    report['placement_plane_y_mm'] = to_mm(plane.GetPlane().Origin.Y)
    report['datum_y_mm'] = to_mm(datum.GetPlane().Origin.Y)
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


def underside(doc, box):
    """Instance-qualified reference to a box's bottom face (as a UI Place on Face click gives: symbol
    geometry with ComputeReferences, see logs/probes/probe_face_refs.py), the face's z and the box's
    front face y (normal -Y)."""
    o = DB.Options(); o.ComputeReferences = True
    ref = z = y = None
    for g in box.get_Geometry(o):
        if isinstance(g, DB.GeometryInstance):
            tr = g.Transform
            for s in g.GetSymbolGeometry():
                if isinstance(s, DB.Solid):
                    for f in s.Faces:
                        if not isinstance(f, DB.PlanarFace): continue
                        nrm = tr.OfVector(f.FaceNormal)
                        if nrm.Z < -0.99 and f.Reference is not None: ref, z = f.Reference, tr.OfPoint(f.Origin).Z
                        if nrm.Y < -0.99: y = tr.OfPoint(f.Origin).Y
    if ref is None or y is None: raise ValueError('box underside/front face not found')
    return ref, y, z


def on_underside(doc, sym, box, x0, x1):
    ref, y, z = underside(doc, box)
    return doc.Create.NewFamilyInstance(ref, DB.Line.CreateBound(DB.XYZ(mm(x0), y, z), DB.XYZ(mm(x1), y, z)), sym)


def load_box(app, proj, key, allow):
    ref_ = clr.Reference[DB.Family]()
    if not proj.LoadFamily(out_path(box_family(app, 'Test_Cabinet_Box_' + key, allow)), ref_): raise ValueError('box did not load')
    bs = proj.GetElement(list(ref_.Value.GetFamilySymbolIds())[0]); bs.Activate()
    return bs


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

    # A. two clicks on a level (face normal +Z, so y = +Y: the profile lands at -Y, below the level)
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
    a.Location.Curve = DB.Line.CreateBound(p0, p1)
    a.LookupParameter('Plane Faces Up').Set(1); proj.Regenerate()
    ss = list(solids(a.get_Geometry(DB.Options())))
    t['A_level_up'] = {'extents_mm': extents(ss), 'volume_mm3': sum(s.Volume for s in ss) * 304.8 ** 3}
    a.LookupParameter('Flip Profile').Set(1); proj.Regenerate()
    t['A_level_up_flipped'] = {'extents_mm': extents(list(solids(a.get_Geometry(DB.Options()))))}
    a.LookupParameter('Flip Profile').Set(0); a.LookupParameter('Plane Faces Up').Set(0); proj.Regenerate()

    # B. Place on Face on a cabinet underside along its front edge, drawn left->right and right->left
    # as seen facing the cabinet (front face normal -Y, so right = +X). Frame: run (+X), back into
    # the box (+Y from the front face), up (+Z from the underside).
    bs = load_box(app, proj, 'cuttable', True)
    pbox = proj.Create.NewFamilyInstance(DB.XYZ(0, mm(2000), 0), bs, level, NS); proj.Regenerate()
    _, fy, bz = underside(proj, pbox)
    q0 = DB.XYZ(mm(250), fy, bz)
    axes = [DB.XYZ.BasisX, DB.XYZ.BasisY, DB.XYZ.BasisZ]
    rows = {}
    for label, x0, x1 in [('left_to_right', 250, 1750), ('right_to_left', 1750, 250)]:
        inst = on_underside(proj, sym, pbox, x0, x1); proj.Regenerate()
        c = inst.Location.Curve
        r = {'unflipped': rel(list(solids(inst.get_Geometry(DB.Options()))), q0, axes),
             'line_mm': [to_mm(v) for q in (c.GetEndPoint(0), c.GetEndPoint(1)) for v in (q.X, q.Y, q.Z)],
             'host_is_box': inst.Host is not None and inst.Host.Id == pbox.Id}
        inst.LookupParameter('Flip Profile').Set(1); proj.Regenerate()
        r['flipped'] = rel(list(solids(inst.get_Geometry(DB.Options()))), q0, axes)
        inst.LookupParameter('Flip Profile').Set(0)
        if label == 'left_to_right':
            for key, sb in [('setback_0', 0.0), ('setback_1in', 25.4)]:
                inst.LookupParameter('Wall Setback').Set(mm(sb)); proj.Regenerate()
                r[key] = rel(list(solids(inst.get_Geometry(DB.Options()))), q0, axes)
            inst.LookupParameter('Flip Profile').Set(1); inst.LookupParameter('Wall Setback').Set(mm(25.4)); proj.Regenerate()
            r['flipped_setback_1in'] = rel(list(solids(inst.get_Geometry(DB.Options()))), q0, axes)
            inst.LookupParameter('Flip Profile').Set(0); inst.LookupParameter('Wall Setback').Set(mm(SETBACK_MM)); proj.Regenerate()
        proj.Delete(inst.Id)
        rows[label] = r
    t['underside'] = rows
    t['underside_frame'] = {'front_face_y_mm': to_mm(fy), 'underside_z_mm': to_mm(bz)}
    report['tests'] = t

    # C. Cutting solid cabinets (Casework boxes), the channel hosted on each box's underside, through
    # the GolaAutoCut module. apply() runs its own transactions, so the placement transaction is committed first.
    commit(tx, 'verify placement')
    cut = {}
    tx = transaction(proj, 'cut test setup')
    boxes = {'cuttable': proj.Create.NewFamilyInstance(DB.XYZ(0, mm(5000), 0), bs, level, NS)}
    boxes['blocked'] = proj.Create.NewFamilyInstance(DB.XYZ(0, mm(8000), 0), load_box(app, proj, 'blocked', False), level, NS)
    proj.Regenerate()
    base = dict((k, vol_mm3(b)) for k, b in boxes.items())
    _, cfy, cbz = underside(proj, boxes['cuttable'])   # read before cutting: a cut instance has no symbol geometry
    g1 = on_underside(proj, sym, boxes['cuttable'], 250, 1750)
    g2 = on_underside(proj, sym, boxes['blocked'], 250, 1750)
    commit(tx, 'cut test setup')
    prof = vol_mm3(g1)
    def run(label, **params):
        if params:
            t2 = transaction(proj, 'params ' + label)
            for n, v in params.items(): g1.LookupParameter(n.replace('_', ' ')).Set(v)
            commit(t2, 'params ' + label)
        row = gola_autocut.apply(proj, [g1])[0]
        cut[label] = {'removed_mm3': base['cuttable'] - vol_mm3(boxes['cuttable']), 'profile_mm3': vol_mm3(g1),
                      'added': row[1], 'removed_ids': row[2], 'blocked': row[3], 'refused': row[4],
                      'still_hosted_on_box': g1.Host is not None and g1.Host.Id == boxes['cuttable'].Id}
    run('box_depth_20')
    run('box_depth_300', Cut_Depth=mm(300))
    run('box_depth_300_flipped', Flip_Profile=1)
    run('box_depth_20_reset', Flip_Profile=0, Cut_Depth=mm(20))
    row = gola_autocut.apply(proj, [g2])[0]
    cut['blocked_box'] = {'removed_mm3': base['blocked'] - vol_mm3(boxes['blocked']), 'added': row[1], 'blocked': row[3], 'refused': row[4]}
    cut['profile_mm3_uncut'] = prof
    cut['length_mm'] = 1500.0
    report['tests']['cuts'] = cut

    # D. A channel on an in-place element must leave its face to cut it (Revit circular chain). In-place
    # families cannot be made through the API, so detach_all=True forces the same swap on a plain box.
    for flip in (0, 1):
        tx = transaction(proj, 'detach setup')
        dbox = proj.Create.NewFamilyInstance(DB.XYZ(0, mm(11000 + 3000 * flip), 0), bs, level, NS)
        proj.Regenerate()
        dv0 = vol_mm3(dbox)
        x0, x1 = (250, 1750) if not flip else (1750, 250)
        g3 = on_underside(proj, sym, dbox, x0, x1)
        g3.LookupParameter('Flip Profile').Set(flip)
        g3.LookupParameter('Cut Depth').Set(mm(30))
        g3.get_Parameter(DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set('detach test')
        proj.Regenerate()
        commit(tx, 'detach setup')
        old_id, old_box = g3.Id.Value, gola_autocut._box(g3)
        row = gola_autocut.apply(proj, [g3], detach_all=True)[0]
        new = proj.GetElement(DB.ElementId(row[0]))
        report['tests']['detach_%s' % ('right_to_left_flipped' if flip else 'left_to_right')] = {
            'old_id': old_id, 'new_id': row[0], 'old_deleted': proj.GetElement(DB.ElementId(old_id)) is None,
            'new_host': new.Host.GetType().Name if new.Host else None,
            'box_shift_mm': max(abs(a_ - b_) for a_, b_ in zip(old_box, gola_autocut._box(new))),
            'flip_up': [new.LookupParameter('Flip Profile').AsInteger(), new.LookupParameter('Plane Faces Up').AsInteger()],
            'cut_depth_mm': to_mm(new.LookupParameter('Cut Depth').AsDouble()),
            'comments': new.get_Parameter(DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString(),
            'removed_mm3': dv0 - vol_mm3(dbox), 'added': row[1], 'refused': row[4], 'note': row[5]}
    tx = transaction(proj, 'preview view')

    # preview: straight side-on section at mid-run of the cut channel g1 (looking +X; front of the cabinet on the left)
    vt = next(v for v in DB.FilteredElementCollector(proj).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    v = DB.View3D.CreateIsometric(proj, vt.Id); v.Name = 'Gola wall unit section'
    mid = DB.XYZ(mm(1000), cfy, cbz)
    v.SetOrientation(DB.ViewOrientation3D(mid.Add(DB.XYZ(mm(-600), 0, 0)), DB.XYZ.BasisZ, DB.XYZ.BasisX))
    v.DetailLevel = DB.ViewDetailLevel.Fine; v.DisplayStyle = DB.DisplayStyle.ShadingWithEdges; v.Scale = 1
    b = DB.BoundingBoxXYZ()
    b.Min = DB.XYZ(mid.X, mid.Y - mm(30), mid.Z - mm(20)); b.Max = DB.XYZ(mid.X + mm(150), mid.Y + mm(90), mid.Z + mm(50))
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
