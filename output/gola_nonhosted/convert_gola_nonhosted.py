# -*- coding: utf-8 -*-
"""Convert the line-based Richelieu Gola RFAs into non-hosted Generic Model RFAs.

Run with: pyrevit run "<abs path>/convert_gola_nonhosted.py" --revit=2025
Reads copies of the source RFAs in source/, never the Drive originals.

Method: a new family from Generic Model.rft (one-level based, not work-plane
based) receives the source's family parameters, formulas, type values,
subcategories and materials. Every solid is copied with ElementTransformUtils
and re-associated to the same-named family parameters. The line-based
built-in Length becomes an ordinary instance Length parameter, labelled on a
"Channel End" reference plane so a placed instance has a drag handle.

Orientation (line-based local Z was the face normal):
  horizontal - run along X, profile height up (Z), depth toward the front (-Y)
  vertical   - run up (Z), profile width along X, depth toward the front (-Y)
Mounting plane is Y = 0 in both.
"""
import os, json, math, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RUN = 'E:/Claude/3D-Model-Workflow/output/gola_nonhosted'
TEMPLATE = 'C:/ProgramData/Autodesk/RVT 2025/Family Templates/English-Imperial/Generic Model.rft'
JOBS = [
    ('Richelieu_Gola_L_Channel_Horizontal_2025.rfa', 'Richelieu_Gola_L_Channel_Horizontal_NonHosted_2025.rfa', 'horizontal'),
    ('Richelieu_Gola_Vertical_Double_Grip_2025.rfa', 'Richelieu_Gola_Vertical_Double_Grip_NonHosted_2025.rfa', 'vertical')]
FLEX_MM = [600.0, 1000.0, 2400.0]
report = {'stage': 'start', 'run_dir': RUN, 'template': TEMPLATE, 'jobs': []}
open_docs = []


def out_path(*parts):
    p = os.path.normpath(os.path.join(RUN, *parts))
    if not p.lower().startswith(os.path.normpath(RUN).lower() + os.sep):
        raise ValueError('Refusing to write outside run dir: ' + p)
    return p


def close_doc(doc):
    """Drop by identity first: list.remove compares documents with Equals, which throws on a closed one."""
    open_docs[:] = [d for d in open_docs if d is not doc]
    doc.Close(False)


def check(stage):
    report['stage'] = stage
    with open(out_path('validation.json'), 'w') as f:
        json.dump(report, f, indent=2, default=str)


def mm(v): return v / 304.8
def to_mm(v): return v * 304.8
def ename(e): return DB.Element.Name.GetValue(e)


def orientation(kind, z0=0.0):
    """Rotation for the run direction, after shifting the source's origin-defining
    placement plane (local z = z0) onto the mounting plane."""
    if kind == 'horizontal':
        t = DB.Transform.CreateRotation(DB.XYZ.BasisX, math.pi / 2)
    else:
        t = DB.Transform.Identity
        t.BasisX = DB.XYZ(0, 0, 1)
        t.BasisY = DB.XYZ(-1, 0, 0)
        t.BasisZ = DB.XYZ(0, -1, 0)
    return t.Multiply(DB.Transform.CreateTranslation(DB.XYZ(0, 0, -z0)))


def placement_offset(src):
    """Local z of the reference plane that defines the line-based family's origin normal to the work plane."""
    zs = set()
    for r in DB.FilteredElementCollector(src).OfClass(DB.ReferencePlane):
        dop = r.get_Parameter(DB.BuiltInParameter.DATUM_PLANE_DEFINES_ORIGIN)
        p = r.GetPlane()
        if dop is not None and dop.AsInteger() == 1 and abs(abs(p.Normal.Z) - 1) < 1e-9:
            zs.add(round(p.Origin.Z, 9))
    if len(zs) > 1: raise ValueError('More than one origin-defining plane normal to Z: %s' % zs)
    return zs.pop() if zs else 0.0


class UseDestinationTypes(DB.IDuplicateTypeNamesHandler):
    def OnDuplicateTypeNamesFound(self, args):
        return DB.DuplicateTypeAction.UseDestinationTypes


def copy_opts():
    o = DB.CopyPasteOptions()
    o.SetDuplicateTypeNamesHandler(UseDestinationTypes())
    return o


def forms(doc):
    return sorted(DB.FilteredElementCollector(doc).OfClass(DB.GenericForm).ToElements(), key=lambda e: e.Id.Value)


def solids(geom):
    for g in geom:
        if isinstance(g, DB.Solid) and g.Volume > 1e-12:
            yield g
        elif isinstance(g, DB.GeometryInstance):
            for s in solids(g.GetInstanceGeometry()):
                yield s


def form_volume_mm3(doc):
    total = 0.0
    for e in forms(doc):
        for s in solids(e.get_Geometry(DB.Options())):
            total += s.Volume
    return total * 304.8 ** 3


def associations(doc, e):
    fm = doc.FamilyManager
    out = []
    for prm in e.Parameters:
        fp = fm.GetAssociatedFamilyParameter(prm)
        if fp is not None:
            out.append((prm, fp.Definition.Name))
    return out


def element_param(e, src_prm):
    d = src_prm.Definition
    bip = getattr(d, 'BuiltInParameter', DB.BuiltInParameter.INVALID)
    if bip != DB.BuiltInParameter.INVALID:
        return e.get_Parameter(bip)
    return e.LookupParameter(d.Name)


def is_builtin(p): return p.Id.Value < 0


def find_param(fm, name):
    for p in fm.Parameters:
        if p.Definition.Name == name:
            return p
    return None


def type_value(fam_type, p):
    st = p.StorageType
    if st == DB.StorageType.Double: return fam_type.AsDouble(p)
    if st == DB.StorageType.Integer: return fam_type.AsInteger(p)
    if st == DB.StorageType.String: return fam_type.AsString(p)
    if st == DB.StorageType.ElementId: return fam_type.AsElementId(p)
    return None


def extents_mm(ss):
    pts = []
    for s in ss:
        for ed in s.Edges:
            pts.extend(ed.Tessellate())
    if not pts:
        raise ValueError('No visible solid geometry on placed instance')
    return [to_mm(min(p.X for p in pts)), to_mm(min(p.Y for p in pts)), to_mm(min(p.Z for p in pts)),
            to_mm(max(p.X for p in pts)), to_mm(max(p.Y for p in pts)), to_mm(max(p.Z for p in pts))]


def view_named(doc, cls, name):
    return next(v for v in DB.FilteredElementCollector(doc).OfClass(cls) if not v.IsTemplate and v.Name == name)


def add_length_handle(dst, kind, length_param):
    """Reference plane at the run end, dimensioned from the origin and labelled Length."""
    if kind == 'horizontal':
        view = view_named(dst, DB.ViewPlan, 'Ref. Level')
        origin_ref = next(r for r in DB.FilteredElementCollector(dst).OfClass(DB.ReferencePlane) if r.Name == 'Center (Left/Right)').GetReference()
        plane = dst.FamilyCreate.NewReferencePlane(DB.XYZ(mm(1000), mm(-300), 0), DB.XYZ(mm(1000), mm(300), 0), DB.XYZ.BasisZ, view)
        line = DB.Line.CreateBound(DB.XYZ(0, mm(-200), 0), DB.XYZ(mm(1000), mm(-200), 0))
    else:
        view = view_named(dst, DB.ViewSection, 'Front')
        origin_ref = DB.FilteredElementCollector(dst).OfClass(DB.Level).FirstElement().GetPlaneReference()
        plane = dst.FamilyCreate.NewReferencePlane(DB.XYZ(mm(-300), 0, mm(1000)), DB.XYZ(mm(300), 0, mm(1000)), DB.XYZ.BasisY, view)
        line = DB.Line.CreateBound(DB.XYZ(mm(-200), 0, 0), DB.XYZ(mm(-200), 0, mm(1000)))
    plane.Name = 'Channel End'
    dst.Regenerate()
    refs = DB.ReferenceArray()
    refs.Append(origin_ref)
    refs.Append(plane.GetReference())
    dim = dst.FamilyCreate.NewDimension(view, line, refs)
    dim.FamilyLabel = length_param
    return plane, dim


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


def plane_geometry(e, T):
    """(origin, normal) of a reference plane or level after transform T."""
    if isinstance(e, DB.Level):
        return T.OfPoint(DB.XYZ(0, 0, e.Elevation)), T.OfVector(DB.XYZ.BasisZ)
    p = e.GetPlane()
    return T.OfPoint(p.Origin), T.OfVector(p.Normal)


def datum_planes(doc):
    return list(DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane)) + list(DB.FilteredElementCollector(doc).OfClass(DB.Level))


def coincident(dst, origin, normal):
    for e in datum_planes(dst):
        o, n = plane_geometry(e, DB.Transform.Identity)
        if abs(abs(n.DotProduct(normal)) - 1) < 1e-9 and abs(origin.Subtract(o).DotProduct(normal)) < mm(0.01):
            return e
    return None


def plane_ref(e):
    return e.GetPlaneReference() if isinstance(e, DB.Level) else e.GetReference()


def perpendicular_view(dst, normal):
    for v in DB.FilteredElementCollector(dst).OfClass(DB.View):
        if v.IsTemplate or v.ViewType not in (DB.ViewType.FloorPlan, DB.ViewType.Elevation): continue
        if abs(v.ViewDirection.DotProduct(normal)) < 1e-9: return v
    raise ValueError('No family view perpendicular to %s' % normal)


def recreate_datums(src, dst, T, dparams, job):
    """Map every source reference plane to a coincident destination datum, creating missing ones,
    then rebuild the labelled dimensions between them."""
    mapping = {}
    made = []
    for e in DB.FilteredElementCollector(src).OfClass(DB.ReferencePlane):
        o, n = plane_geometry(e, T)
        hit = coincident(dst, o, n)
        if hit is None:
            v = perpendicular_view(dst, n)
            d = n.CrossProduct(v.ViewDirection).Normalize()
            hit = dst.FamilyCreate.NewReferencePlane(o.Add(d.Multiply(mm(300))), o.Subtract(d.Multiply(mm(300))), v.ViewDirection, v)
            if e.Name != 'Reference Plane': hit.Name = e.Name  # the API reports unnamed planes as 'Reference Plane'
            made.append(e.Name)
        mapping[e.Id.Value] = hit
    for e in DB.FilteredElementCollector(src).OfClass(DB.Level):
        mapping[e.Id.Value] = coincident(dst, *plane_geometry(e, T))
    dst.Regenerate()
    # Labelled dimensions are recorded, not rebuilt: in the Gola sources they only annotate the recess
    # planes (no form is constrained to them), one is 0.5 mm - below Revit's short-curve tolerance -
    # and labelling the other against its formula makes Revit roll the transaction back.
    dims = []
    for d in DB.FilteredElementCollector(src).OfClass(DB.Dimension):
        try: fl = d.FamilyLabel
        except Exception: fl = None
        if fl is None: continue
        ends = [mapping.get(r.ElementId.Value) for r in d.References]
        if len(ends) != 2 or None in ends:
            raise ValueError('Labelled dimension %d (%s) references non-datum geometry' % (d.Id.Value, fl.Definition.Name))
        (oa, n), (ob, _) = plane_geometry(ends[0], DB.Transform.Identity), plane_geometry(ends[1], DB.Transform.Identity)
        dims.append([fl.Definition.Name, to_mm(d.Value), abs(to_mm(ob.Subtract(oa).DotProduct(n)))])
    job['datums'] = {'created_planes': made, 'labels_not_rebuilt': dims}


def convert(app, src_name, dst_name, kind, job):
    src = app.OpenDocumentFile(out_path('source', src_name)); open_docs.append(src)
    job['source_placement_type'] = str(src.OwnerFamily.FamilyPlacementType)
    sfm = src.FamilyManager
    if DB.FilteredElementCollector(src).OfClass(DB.FamilyInstance).GetElementCount():
        raise ValueError('Source has nested families; this converter does not copy them')
    src_forms = forms(src)
    src_params = list(sfm.Parameters)
    src_length = find_param(sfm, 'Length')
    if src_length is None:
        raise ValueError('Source has no Length parameter')
    job['source_length_builtin'] = is_builtin(src_length)
    custom = [p for p in src_params if not is_builtin(p) and p.Definition.Name != 'Length']
    for p in custom:
        if p.IsShared: raise ValueError('Shared parameter not supported: ' + p.Definition.Name)
        if p.IsReporting: raise ValueError('Reporting parameter not supported: ' + p.Definition.Name)
    job['source'] = {'forms': len(src_forms), 'custom_params': len(custom), 'types': sfm.Types.Size,
                     'form_volume_mm3': form_volume_mm3(src),
                     'reference_planes': DB.FilteredElementCollector(src).OfClass(DB.ReferencePlane).GetElementCount(),
                     'dimensions': DB.FilteredElementCollector(src).OfClass(DB.Dimension).GetElementCount()}
    src_assoc = [(e, associations(src, e)) for e in src_forms]
    # Forms locked to the line's Right end plane without a parameter on their end follow Length.
    right = next(r for r in DB.FilteredElementCollector(src).OfClass(DB.ReferencePlane) if r.Name == 'Right')
    locked_right = set()
    for d in DB.FilteredElementCollector(src).OfClass(DB.Dimension):
        refs = [r.ElementId.Value for r in d.References]
        if d.IsLocked and right.Id.Value in refs: locked_right.update(refs)
    added = []
    for e, links in src_assoc:
        if e.Id.Value not in locked_right or not isinstance(e, DB.Extrusion): continue
        end = e.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM)
        if any(p.Definition.Name == end.Definition.Name for p, _ in links): continue
        if abs(end.AsDouble() - sfm.CurrentType.AsDouble(src_length)) > mm(0.01):
            raise ValueError('Form %d is locked to Right but its end is not at Length' % e.Id.Value)
        links.append((end, 'Length')); added.append(e.Id.Value)
    job['end_linked_to_length_from_right_lock'] = added
    # Links to the built-in line Length cannot travel between documents, and pasted links to
    # same-named formula parameters make Revit write into them. Detach every link in this unsaved
    # copy; they are re-created explicitly from src_assoc after the paste.
    stx = transaction(src, 'Detach parameter links')
    detached = 0
    for e, links in src_assoc:
        for prm, name in links:
            if sfm.GetAssociatedFamilyParameter(prm) is not None:
                sfm.AssociateElementParameterToFamilyParameter(prm, None); detached += 1
    commit(stx, 'detach source links')
    job['detached_links'] = detached

    dst = app.NewFamilyDocument(TEMPLATE); open_docs.append(dst)
    fm = dst.FamilyManager
    tx = transaction(dst, 'Gola non-hosted conversion')
    dst.SetUnits(src.GetUnits())
    wp = dst.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED)
    if wp is not None and not wp.IsReadOnly: wp.Set(0)
    for bip in (DB.BuiltInParameter.FAMILY_ALLOW_CUT_WITH_VOIDS, DB.BuiltInParameter.FAMILY_SHARED):
        sp, dp = src.OwnerFamily.get_Parameter(bip), dst.OwnerFamily.get_Parameter(bip)
        if sp is not None and dp is not None and not dp.IsReadOnly: dp.Set(sp.AsInteger())
        job.setdefault('family_flags', {})[str(bip)] = dp.AsInteger() if dp is not None else None
    type_names = [t.Name for t in sfm.Types]
    existing = [t.Name for t in fm.Types]
    for n in type_names:
        if n not in existing: fm.NewType(n)
    job['template_types_found'] = existing

    dparams = {}
    for p in custom:
        d = p.Definition
        dparams[d.Name] = fm.AddParameter(d.Name, d.GetGroupTypeId(), d.GetDataType(), p.IsInstance)
    dparams['Length'] = fm.AddParameter('Length', DB.GroupTypeId.Geometry, DB.SpecTypeId.Length, True)

    mats = [m.Id for m in DB.FilteredElementCollector(src).OfClass(DB.Material)]
    DB.ElementTransformUtils.CopyElements(src, List[DB.ElementId](mats), dst, DB.Transform.Identity, copy_opts())
    dmats = dict((m.Name, m) for m in DB.FilteredElementCollector(dst).OfClass(DB.Material))
    dcat = dst.OwnerFamily.FamilyCategory
    dsub = dict((c.Name, c) for c in dcat.SubCategories)
    for c in src.OwnerFamily.FamilyCategory.SubCategories:
        if c.Name not in dsub:
            dsub[c.Name] = dst.Settings.Categories.NewSubcategory(dcat, c.Name)
        if c.Material is not None and c.Material.Name in dmats:
            dsub[c.Name].Material = dmats[c.Material.Name]
    dst.Regenerate()

    commit(tx, 'parameters and materials')

    check('convert %s: type values' % kind)
    tx = transaction(dst, 'Type values')
    skipped = []
    for st in sfm.Types:
        fm.CurrentType = next(t for t in fm.Types if t.Name == st.Name)
        for sp in src_params:
            if sp.Formula or not st.HasValue(sp): continue
            name = sp.Definition.Name
            v = type_value(st, sp)
            if v is None: continue
            if sp.StorageType == DB.StorageType.ElementId and v != DB.ElementId.InvalidElementId:
                sm = src.GetElement(v)
                if not isinstance(sm, DB.Material): raise ValueError('Non-material ElementId value on ' + name)
                v = dmats[sm.Name].Id
            if name == 'Length':
                fm.Set(dparams['Length'], v); continue
            if is_builtin(sp):
                dp = fm.get_Parameter(sp.Definition.BuiltInParameter)
                try:
                    if dp is None: raise ValueError('absent in template')
                    fm.Set(dp, v)
                except Exception as ex:
                    skipped.append([st.Name, name, str(ex)])
                continue
            fm.Set(dparams[name], v)
    job['builtin_values_skipped'] = skipped
    commit(tx, 'type values')

    check('convert %s: formulas' % kind)
    tx = transaction(dst, 'Formulas')
    formulas = dict((p.Definition.Name, p.Formula) for p in custom if p.Formula)
    pending = dict(formulas)
    for _ in range(len(pending) + 1):
        errors = {}
        for n, f in list(pending.items()):
            try:
                fm.SetFormula(dparams[n], f); del pending[n]
            except Exception as ex:
                errors[n] = str(ex)
        if not pending: break
    if pending: raise ValueError('Formulas could not be set: ' + json.dumps(errors))
    commit(tx, 'formulas')

    check('convert %s: forms' % kind)
    tx = transaction(dst, 'Forms and links')
    z0 = placement_offset(src)
    job['placement_plane_offset_mm'] = to_mm(z0)
    T = orientation(kind, z0)
    new_forms = []
    assoc_rows = []
    for e, links in src_assoc:
        ids = DB.ElementTransformUtils.CopyElements(src, List[DB.ElementId]([e.Id]), dst, T, copy_opts())
        g = [dst.GetElement(i) for i in ids if isinstance(dst.GetElement(i), DB.GenericForm)]
        if len(g) != 1: raise ValueError('Copy of form %d returned %d forms' % (e.Id.Value, len(g)))
        n = g[0]
        if e.Subcategory is not None: n.Subcategory = dsub[e.Subcategory.Name]
        for prm, fpname in links:
            dp = element_param(n, prm)
            if dp is None: raise ValueError('Form %d has no parameter %s' % (e.Id.Value, prm.Definition.Name))
            fm.AssociateElementParameterToFamilyParameter(dp, dparams[fpname])
        new_forms.append(n)
        assoc_rows.append([e.Id.Value, len(links), len(associations(dst, n))])
    job['association_rows'] = assoc_rows
    # Cut relationships between forms do not survive the paste; rebuild them. (JoinGeometryUtils is
    # project-only, so joins cannot be read here; the volume parity gates would expose a lost join.)
    dmap = dict((e.Id.Value, n) for (e, _), n in zip(src_assoc, new_forms))
    cuts = []
    for e, _ in src_assoc:
        for cid in DB.SolidSolidCutUtils.GetCuttingSolids(e):
            DB.SolidSolidCutUtils.AddCutBetweenSolids(dst, dmap[e.Id.Value], dmap[cid.Value])
            cuts.append([e.Id.Value, cid.Value])
    job['cuts_rebuilt'] = cuts
    commit(tx, 'forms and links')

    check('convert %s: datums' % kind)
    tx = transaction(dst, 'Datums')
    fm.CurrentType = next(t for t in fm.Types if t.Name == type_names[0])
    plane, dim = add_length_handle(dst, kind, dparams['Length'])
    dst.Regenerate()
    job['length_handle'] = {'plane': plane.Id.Value, 'dimension': dim.Id.Value,
                            'dimension_mm': to_mm(dim.Value), 'type_length_mm': to_mm(fm.CurrentType.AsDouble(dparams['Length']))}
    recreate_datums(src, dst, T, dparams, job)
    dst.Regenerate()
    v3 = next(v for v in DB.FilteredElementCollector(dst).OfClass(DB.View3D) if not v.IsTemplate)
    v3.DetailLevel = DB.ViewDetailLevel.Fine; v3.DisplayStyle = DB.DisplayStyle.ShadingWithEdges
    commit(tx, 'datums')

    job['converted'] = {'forms': len(new_forms), 'form_volume_mm3': form_volume_mm3(dst)}
    so = DB.SaveAsOptions(); so.OverwriteExistingFile = True; so.MaximumBackups = 1
    rfa = out_path(dst_name)
    check('convert %s: save' % kind)
    dst.SaveAs(rfa, so)
    check('convert %s: close' % kind)
    close_doc(dst)
    close_doc(src)
    job['rfa'] = rfa
    return rfa


def verify_family(app, rfa, kind, job):
    doc = app.OpenDocumentFile(rfa); open_docs.append(doc)
    fm = doc.FamilyManager
    wp = doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED)
    job['reopened'] = {'placement_type': str(doc.OwnerFamily.FamilyPlacementType),
                       'work_plane_based': wp.AsInteger() if wp else None,
                       'forms': len(forms(doc)), 'form_volume_mm3': form_volume_mm3(doc),
                       'custom_params': len([p for p in fm.Parameters if not is_builtin(p)]),
                       'types': [t.Name for t in fm.Types],
                       'formulas': len([p for p in fm.Parameters if p.Formula])}
    return doc


def place_and_flex(app, fdoc, kind, job, src_path):
    proj = app.NewProjectDocument(DB.UnitSystem.Metric); open_docs.append(proj)
    fam = fdoc.LoadFamily(proj)
    tx = transaction(proj, 'Place non-hosted Gola')
    sym = proj.GetElement(list(fam.GetFamilySymbolIds())[0])
    if not sym.IsActive: sym.Activate()
    level = DB.FilteredElementCollector(proj).OfClass(DB.Level).FirstElement()
    inst = proj.Create.NewFamilyInstance(DB.XYZ.Zero, sym, level, DB.Structure.StructuralType.NonStructural)
    proj.Regenerate()
    host = inst.Host
    job['placement'] = {'family_placement_type': str(fam.FamilyPlacementType),
                        'host_class': host.GetType().Name if host is not None else None,
                        'host_face_is_none': inst.HostFace is None}
    axis = 0 if kind == 'horizontal' else 2
    rows = []
    lp = inst.LookupParameter('Length')
    for L in FLEX_MM:
        lp.Set(mm(L)); proj.Regenerate()
        ss = list(solids(inst.get_Geometry(DB.Options())))
        ext = extents_mm(ss)
        rows.append({'length_mm': L, 'extents_mm': ext, 'run_span_mm': ext[axis + 3] - ext[axis],
                     'span_xyz_mm': [ext[3] - ext[0], ext[4] - ext[1], ext[5] - ext[2]]})
    job['flex'] = rows
    lp.Set(mm(1000)); proj.Regenerate()
    ss = list(solids(inst.get_Geometry(DB.Options())))
    # Parity: the original line-based family on a 1000 mm line, re-oriented, must match exactly.
    fref = clr.Reference[DB.Family]()
    loaded = proj.LoadFamily(src_path, fref); sfam = fref.Value
    if not loaded: raise ValueError('Source family did not load: ' + src_path)
    ssym = proj.GetElement(list(sfam.GetFamilySymbolIds())[0])
    if not ssym.IsActive: ssym.Activate()
    sinst = proj.Create.NewFamilyInstance(DB.Line.CreateBound(DB.XYZ.Zero, DB.XYZ(mm(1000), 0, 0)), ssym, level,
                                          DB.Structure.StructuralType.NonStructural)
    proj.Regenerate()
    T = orientation(kind)  # the placed instance already carries the placement-plane offset
    s_ss = list(solids(sinst.get_Geometry(DB.Options())))
    s_pts = [T.OfPoint(p) for s in s_ss for ed in s.Edges for p in ed.Tessellate()]
    s_ext = [to_mm(min(p.X for p in s_pts)), to_mm(min(p.Y for p in s_pts)), to_mm(min(p.Z for p in s_pts)),
             to_mm(max(p.X for p in s_pts)), to_mm(max(p.Y for p in s_pts)), to_mm(max(p.Z for p in s_pts))]
    job['parity'] = {'source_volume_mm3': sum(s.Volume for s in s_ss) * 304.8 ** 3,
                     'converted_volume_mm3': sum(s.Volume for s in ss) * 304.8 ** 3,
                     'source_extents_reoriented_mm': s_ext, 'converted_extents_mm': extents_mm(ss),
                     'source_solids': len(s_ss), 'converted_solids': len(ss)}
    proj.Delete(sinst.Id)
    face_mats = set()
    for s in ss:
        for fc in s.Faces:
            m = proj.GetElement(fc.MaterialElementId)
            face_mats.add(m.Name if m is not None else '<none>')
    pm = sym.LookupParameter('Profile Material')
    job['face_materials'] = sorted(face_mats)
    job['profile_material'] = proj.GetElement(pm.AsElementId()).Name if pm and pm.AsElementId() != DB.ElementId.InvalidElementId else None

    vt = next(v for v in DB.FilteredElementCollector(proj).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    views = []
    for label, box in [('overall', None),
                       ('end_closeup', [-40, -90, -40, 160, 90, 100] if kind == 'horizontal' else [-100, -90, -40, 40, 90, 160])]:
        v = DB.View3D.CreateIsometric(proj, vt.Id); v.Name = 'Gola ' + kind + ' ' + label
        eye = DB.XYZ(mm(1500), mm(-1500), mm(1200)); tgt = DB.XYZ(mm(500) if kind == 'horizontal' else 0, 0, 0 if kind == 'horizontal' else mm(500))
        fw = tgt.Subtract(eye).Normalize(); rt = fw.CrossProduct(DB.XYZ.BasisZ).Normalize()
        v.SetOrientation(DB.ViewOrientation3D(eye, rt.CrossProduct(fw).Normalize(), fw))
        v.DetailLevel = DB.ViewDetailLevel.Fine; v.DisplayStyle = DB.DisplayStyle.ShadingWithEdges; v.Scale = 1
        if box:
            b = DB.BoundingBoxXYZ(); b.Min = DB.XYZ(*[mm(x) for x in box[:3]]); b.Max = DB.XYZ(*[mm(x) for x in box[3:]])
            v.SetSectionBox(b); v.IsSectionBoxActive = True
        views.append((label, v))
    commit(tx, 'project placement')
    job['previews'] = []
    for label, v in views:
        o = DB.ImageExportOptions(); o.ExportRange = DB.ExportRange.SetOfViews
        o.SetViewsAndSheets(List[DB.ElementId]([v.Id]))
        o.FilePath = out_path('preview', kind + '_' + label)
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
    if not os.path.isdir(out_path('preview')): os.makedirs(out_path('preview'))
    for src_name, dst_name, kind in JOBS:
        job = {'source': src_name, 'output': dst_name, 'orientation': kind}
        report['jobs'].append(job)
        check('convert ' + kind)
        rfa = convert(app, src_name, dst_name, kind, job)
        check('verify family ' + kind)
        fdoc = verify_family(app, rfa, kind, job)
        check('place and flex ' + kind)
        place_and_flex(app, fdoc, kind, job, out_path('source', src_name))
        close_doc(fdoc)
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
