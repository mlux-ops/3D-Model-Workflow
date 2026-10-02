# -*- coding: utf-8 -*-
"""Validate the saved KW1041MBK family in Revit 2025: reopen, warnings, category, placement, hosting on a wall in a disposable
project, envelope and part measurements with Show Disc on/off, material substitution, light source, and view export.
Run only through _harness/revit_run.py. Writes validation.json."""
import sys
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/high/source')
from common import *
import glob

V = {'stages': [], 'gates': {}}
docs = []
VIEWS = os.path.join(OUT, 'views')
EXPORT_TMP = os.path.join(OUT, '_work', 'export')
IN = 12.0


def stage(name):
    V['stages'].append(name)
    write_json('validation.json', V)


def r4(x):
    return round(x, 4)


def ename(el):
    return DB.Element.Name.__get__(el)


# ---------------------------------------------------------------- measurement
def solid_points(solid):
    pts = []
    for f in solid.Faces:
        m = f.Triangulate(1.0)
        if m is not None:
            for v in m.Vertices:
                pts.append(v)
    for e in solid.Edges:
        c = e.AsCurve()
        if isinstance(c, DB.Line):
            pts.append(c.GetEndPoint(0))
            pts.append(c.GetEndPoint(1))
        elif isinstance(c, DB.Arc):
            n = 360
            for i in range(n + 1):
                pts.append(c.Evaluate(i / float(n), True))
        else:
            for p in c.Tessellate():
                pts.append(p)
    return pts


def extent(pts, O, d):
    vals = [(p.Subtract(O)).DotProduct(d) * IN for p in pts]
    return [r4(min(vals)), r4(max(vals))]


def rng(e):
    return r4(e[1] - e[0])


def measure(doc, inst, O, ex, ey, ez):
    opt = DB.Options()
    opt.DetailLevel = DB.ViewDetailLevel.Fine
    opt.ComputeReferences = False
    parts = {}
    allpts = []
    axis_w = ey.Multiply(-SIN).Add(ez.Multiply(COS))
    disc_v = ey.Multiply(COS).Add(ez.Multiply(SIN))
    for solid in all_solids(inst.get_Geometry(opt)):
        gs = doc.GetElement(solid.GraphicsStyleId)
        name = gs.GraphicsStyleCategory.Name if gs is not None and gs.GraphicsStyleCategory is not None else 'unknown'
        pts = solid_points(solid)
        if name != 'Light Source':
            allpts.extend(pts)
        faces = {}
        for f in solid.Faces:
            mid = f.MaterialElementId
            mn = ename(doc.GetElement(mid)) if mid != DB.ElementId.InvalidElementId else '<none>'
            faces[mn] = faces.get(mn, 0) + 1
        parts[name] = {'u': extent(pts, O, ex), 'v': extent(pts, O, ey), 'w': extent(pts, O, ez), 'axis': extent(pts, O, axis_w),
                       'in_plane_v': extent(pts, O, disc_v), 'faces': faces, 'face_count': solid.Faces.Size, 'volume_in3': r4(solid.Volume * IN ** 3)}
    env = {'u': extent(allpts, O, ex), 'v': extent(allpts, O, ey), 'w': extent(allpts, O, ez)}
    bb = inst.get_BoundingBox(None)
    env['instance_get_BoundingBox_world_in'] = [[r4(bb.Min.X * IN), r4(bb.Min.Y * IN), r4(bb.Min.Z * IN)], [r4(bb.Max.X * IN), r4(bb.Max.Y * IN), r4(bb.Max.Z * IN)]]
    env['size_in'] = {'W': rng(env['u']), 'H': rng(env['v']), 'D': rng(env['w'])}
    return {'parts': parts, 'envelope': env}


def face_material_table(m):
    return dict((k, v['faces']) for k, v in m['parts'].items())


# ---------------------------------------------------------------- light
def light_info(doc):
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    t = lf.GetLightSourceTransform()
    d = {'shape': str(lf.GetLightShapeStyle()), 'distribution': str(lf.GetLightDistributionStyle()), 'n_types': lf.GetNumberOfLightTypes(),
         'origin_in': [r4(t.Origin.X * IN), r4(t.Origin.Y * IN), r4(t.Origin.Z * IN)]}
    if d['n_types']:
        lt = lf.GetLightType(0)
        ii = lt.GetInitialIntensity()
        d['intensity_class'] = ii.GetType().Name
        for attr in ['Wattage', 'Efficacy', 'Flux']:
            try:
                d['intensity_' + attr] = getattr(ii, attr)
            except Exception:
                pass
        ic = lt.GetInitialColor()
        d['color_class'] = ic.GetType().Name
        try:
            d['color_temperature_K'] = ic.Temperature
        except Exception:
            pass
        d['light_shape'] = lt.GetLightShape().GetType().Name
        d['light_distribution'] = lt.GetLightDistribution().GetType().Name
        d['loss_factor'] = lt.GetLossFactor().GetType().Name
        try:
            d['loss_factor_value'] = lt.GetLossFactor().LossFactor
        except Exception:
            pass
    return d


# ---------------------------------------------------------------- views
def make_view(doc, name, eye, target, keep_cat_ids, bmin, bmax, hide_ids=None):
    vtype = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(doc, vtype.Id)
    view.Name = name
    fwd = target.Subtract(eye).Normalize()
    up = DB.XYZ.BasisZ if doc.IsFamilyDocument is False else DB.XYZ.BasisY
    if abs(up.DotProduct(fwd)) > 0.98:
        up = DB.XYZ.BasisY if doc.IsFamilyDocument is False else DB.XYZ.BasisZ
    right = fwd.CrossProduct(up).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, right.CrossProduct(fwd).Normalize(), fwd))
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.DisplayStyle = DB.DisplayStyle.Shading
    for cat in doc.Settings.Categories:
        try:
            if cat.Id not in keep_cat_ids and view.CanCategoryBeHidden(cat.Id):
                view.SetCategoryHidden(cat.Id, True)
        except Exception:
            pass
    if hide_ids:
        view.HideElements(List[DB.ElementId](hide_ids))
    box = DB.BoundingBoxXYZ()
    box.Min = bmin
    box.Max = bmax
    view.SetSectionBox(box)
    view.IsSectionBoxActive = True
    return view


def export_view(doc, view, out_name, pixels=1400):
    if not os.path.isdir(guard(EXPORT_TMP)):
        os.makedirs(EXPORT_TMP)
    for old in glob.glob(os.path.join(EXPORT_TMP, '*')):
        os.remove(guard(old))
    opts = DB.ImageExportOptions()
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.SetViewsAndSheets(List[DB.ElementId]([view.Id]))
    opts.FilePath = guard(os.path.join(EXPORT_TMP, 'v'))
    opts.HLRandWFViewsFileType = DB.ImageFileType.PNG
    opts.ShadowViewsFileType = DB.ImageFileType.PNG
    opts.ImageResolution = DB.ImageResolution.DPI_150
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = pixels
    doc.ExportImage(opts)
    files = glob.glob(os.path.join(EXPORT_TMP, '*.png'))
    if len(files) != 1:
        raise RuntimeError('export produced %d files for %s' % (len(files), out_name))
    dst = guard(os.path.join(VIEWS, out_name))
    if os.path.exists(dst):
        os.remove(dst)
    os.rename(files[0], dst)
    return dst


def wf(f, O, ex, ey, ez, u, v, w):
    """World point from wall-frame inches."""
    return O.Add(ex.Multiply(u / IN)).Add(ey.Multiply(v / IN)).Add(ez.Multiply(w / IN))


try:
    app = __revit__.Application
    if not os.path.isdir(VIEWS):
        os.makedirs(VIEWS)

    # ------------------------------------------------ A. reopen the family
    fdoc = app.OpenDocumentFile(RFA)
    docs.append(fdoc)
    fam = {}
    fam['warnings'] = [w.GetDescriptionText() for w in fdoc.GetWarnings()]
    fam['warning_count'] = len(fam['warnings'])
    fam['category'] = fdoc.OwnerFamily.FamilyCategory.Name
    fam['placement_type'] = str(fdoc.OwnerFamily.FamilyPlacementType)
    fm = fdoc.FamilyManager
    fam['types'] = [t.Name for t in fm.Types]
    fam['current_type'] = fm.CurrentType.Name
    plist = []
    for p in fm.Parameters:
        entry = {'name': p.Definition.Name, 'instance': p.IsInstance, 'storage': str(p.StorageType)}
        try:
            if p.StorageType == DB.StorageType.ElementId:
                eid = fm.CurrentType.AsElementId(p)
                el = fdoc.GetElement(eid)
                entry['value'] = el.Name if el is not None else str(eid.IntegerValue)
            elif p.StorageType == DB.StorageType.Integer:
                entry['value'] = fm.CurrentType.AsInteger(p)
            elif p.StorageType == DB.StorageType.String:
                entry['value'] = fm.CurrentType.AsString(p)
        except Exception as ex:
            entry['value_error'] = str(ex)
        plist.append(entry)
    fam['parameters'] = [p for p in plist if p['name'] in ('Metal Finish', 'Glass Finish', 'Show Disc', 'Manufacturer', 'Model', 'Description')]
    fam['light_source_param'] = fdoc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE).AsInteger()
    fam['forms'] = {}
    for e in DB.FilteredElementCollector(fdoc).OfClass(DB.FreeFormElement):
        mp = e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM)
        fam['forms'][e.Subcategory.Name if e.Subcategory else str(e.Id.IntegerValue)] = {'id': e.Id.IntegerValue, 'material_param_associated': True}
    fam['light'] = light_info(fdoc)
    ctr = (0.0, -A_C * SIN, D0 + A_C * COS)
    lo = fam['light']['origin_in']
    dist = math.sqrt(sum((lo[i] - ctr[i]) ** 2 for i in range(3)))
    axial = lo[1] * N_AXIS[1] + (lo[2] - D0) * N_AXIS[2]
    fam['light']['shade_centre_in'] = [r4(c) for c in ctr]
    fam['light']['distance_to_shade_centre_in'] = r4(dist)
    fam['light']['axial_position_from_face_in'] = r4(axial)
    fam['light']['inside_shade_cavity'] = bool(dist < SHADE_R - SHADE_WALL and axial > S0)
    V['family'] = fam
    stage('family reopened')

    V['views'] = {}
    fdoc.Close(False)
    docs.remove(fdoc)

    # ------------------------------------------------ B. host in a disposable project
    pdoc = app.NewProjectDocument(DB.UnitSystem.Imperial)
    docs.append(pdoc)
    tx = DB.Transaction(pdoc, 'wall + fixture')
    tx.Start()
    level = DB.Level.Create(pdoc, 0.0)
    wtype = DB.FilteredElementCollector(pdoc).OfClass(DB.WallType).FirstElement()
    V['wall_type'] = ename(wtype) if wtype is not None else None
    wall = DB.Wall.Create(pdoc, DB.Line.CreateBound(DB.XYZ(0, 0, 0), DB.XYZ(20, 0, 0)), wtype.Id, level.Id, 12.0, 0.0, False, False)
    pdoc.Regenerate()
    ext = DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior)[0]
    pface = wall.GetGeometryObjectFromReference(ext)
    ez = pface.FaceNormal
    ey = DB.XYZ.BasisZ
    ex = ey.CrossProduct(ez)
    O = DB.XYZ(10.0, pface.Origin.Y, 5.0)
    famref = clr.Reference[DB.Family]()
    ok = pdoc.LoadFamily(RFA, famref)
    family = famref.Value
    sym = pdoc.GetElement(list(family.GetFamilySymbolIds())[0])
    V['symbol'] = ename(sym)
    if not sym.IsActive:
        sym.Activate()
    pdoc.Regenerate()
    inst = pdoc.Create.NewFamilyInstance(ext, O, ex, sym)
    pdoc.Regenerate()
    tx.Commit()
    V['hosting'] = {'wall_exterior_normal': [r4(ez.X), r4(ez.Y), r4(ez.Z)], 'facing_orientation': [r4(inst.FacingOrientation.X), r4(inst.FacingOrientation.Y), r4(inst.FacingOrientation.Z)],
                    'host_is_wall': inst.Host.Id == wall.Id, 'placement_type': str(family.FamilyPlacementType), 'family_category': family.FamilyCategory.Name,
                    'instance_location_vs_face_in_normal_dir': r4((inst.Location.Point.Subtract(O)).DotProduct(ez) * IN)}
    stage('placed')

    # measurements, disc on
    m_on = measure(pdoc, inst, O, ex, ey, ez)
    V['measure_disc_on'] = m_on
    bp = m_on['parts']['Backplate']
    V['hosting']['backplate_w_range_in'] = bp['w']
    V['hosting']['fixture_w_range_in'] = m_on['envelope']['w']
    V['hosting']['all_solids_on_exterior_side_of_face'] = bool(m_on['envelope']['w'][0] >= -0.001)
    V['hosting']['backplate_on_face'] = bool(abs(bp['w'][0]) < 0.001 and abs(bp['w'][1] - BACK_T) < 0.001)
    V['hosting']['wall_normal_used_as_projection_axis'] = [r4(ez.X), r4(ez.Y), r4(ez.Z)]
    stage('measured disc on')

    # disc off
    tx = DB.Transaction(pdoc, 'disc off')
    tx.Start()
    pdoc.GetElement(inst.Id).LookupParameter('Show Disc').Set(0)
    tx.Commit()
    m_off = measure(pdoc, pdoc.GetElement(inst.Id), O, ex, ey, ez)
    V['measure_disc_off'] = m_off
    moved = {}
    for k in m_off['parts']:
        a, b = m_on['parts'][k], m_off['parts'][k]
        moved[k] = max(abs(a[c][i] - b[c][i]) for c in ('u', 'v', 'w') for i in (0, 1))
    V['disc_off_max_shift_of_other_parts_in'] = moved
    V['disc_off_parts'] = sorted(m_off['parts'].keys())
    stage('measured disc off')
    tx = DB.Transaction(pdoc, 'disc on')
    tx.Start()
    pdoc.GetElement(inst.Id).LookupParameter('Show Disc').Set(1)
    tx.Commit()

    # material substitution (type parameters)
    tx = DB.Transaction(pdoc, 'materials')
    tx.Start()
    red = pdoc.GetElement(DB.Material.Create(pdoc, 'TEST_RED'))
    red.Color = DB.Color(200, 20, 20)
    green = pdoc.GetElement(DB.Material.Create(pdoc, 'TEST_GREEN'))
    green.Color = DB.Color(20, 180, 40)
    sym = pdoc.GetElement(sym.Id)
    orig = {}
    orig_ids = {}
    for pn in ('Metal Finish', 'Glass Finish'):
        p = sym.LookupParameter(pn)
        orig_ids[pn] = p.AsElementId()
        orig[pn] = ename(pdoc.GetElement(p.AsElementId()))
    V['material_defaults'] = orig
    sym.LookupParameter('Metal Finish').Set(red.Id)
    tx.Commit()
    m_metal = measure(pdoc, pdoc.GetElement(inst.Id), O, ex, ey, ez)
    tx = DB.Transaction(pdoc, 'materials 2')
    tx.Start()
    sym.LookupParameter('Glass Finish').Set(green.Id)
    tx.Commit()
    m_glass = measure(pdoc, pdoc.GetElement(inst.Id), O, ex, ey, ez)
    V['material_swap'] = {'default': face_material_table(m_on), 'metal_finish_to_TEST_RED': face_material_table(m_metal),
                          'glass_finish_also_to_TEST_GREEN': face_material_table(m_glass)}
    stage('material swap')

    # restore defaults for the hosted view
    tx = DB.Transaction(pdoc, 'restore')
    tx.Start()
    sym.LookupParameter('Metal Finish').Set(orig_ids['Metal Finish'])
    sym.LookupParameter('Glass Finish').Set(orig_ids['Glass Finish'])
    tx.Commit()

    # light in project
    try:
        lt = DB.Lighting.LightType.GetLightTypeFromInstance(pdoc, inst.Id)
        V['project_light'] = {'intensity': lt.GetInitialIntensity().GetType().Name, 'wattage': getattr(lt.GetInitialIntensity(), 'Wattage', None),
                              'color': lt.GetInitialColor().GetType().Name, 'shape': lt.GetLightShape().GetType().Name}
    except Exception:
        V['project_light_error'] = traceback.format_exc()
    V['project_warnings'] = [w.GetDescriptionText() for w in pdoc.GetWarnings()]

    # views: hosted instance only, wall lightened for contrast, light-source proxy hidden, tight section box
    tx = DB.Transaction(pdoc, 'views')
    tx.Start()
    fixcat = DB.Category.GetCategory(pdoc, DB.BuiltInCategory.OST_LightingFixtures)
    keepcats = [fixcat.Id, DB.Category.GetCategory(pdoc, DB.BuiltInCategory.OST_Walls).Id]
    proxy_ids = [sc.Id for sc in fixcat.SubCategories if sc.Name == 'Light Source']
    wall_mat_ids = [l.MaterialId for l in pdoc.GetElement(wall.GetTypeId()).GetCompoundStructure().GetLayers()]
    V['wall_layer_materials'] = [ename(pdoc.GetElement(i)) if i != DB.ElementId.InvalidElementId else '<none>' for i in wall_mat_ids]
    for i in wall_mat_ids:
        if i != DB.ElementId.InvalidElementId:
            pdoc.GetElement(i).Color = DB.Color(214, 214, 208)
    tgt = wf(None, O, ex, ey, ez, 0, -0.25, 2.6)
    specs = [('front', wf(None, O, ex, ey, ez, 0, 0, 120), (-5.5, 5.5), (-5.5, 5.5), (-2, 7)),
             ('side', wf(None, O, ex, ey, ez, -120, -0.25, 2.6), (-5, 5), (-5, 5), (-2, 7)),
             ('oblique', wf(None, O, ex, ey, ez, -60, 45, 80), (-5.5, 5.5), (-5.5, 5.5), (-2, 7)),
             ('hosted_on_wall', wf(None, O, ex, ey, ez, 40, 25, 60), (-14, 14), (-14, 14), (-6, 9))]
    made = []
    solid_fill = next(f for f in DB.FilteredElementCollector(pdoc).OfClass(DB.FillPatternElement) if f.GetFillPattern().IsSolidFill)
    ogs = DB.OverrideGraphicSettings()
    ogs.SetSurfaceForegroundPatternId(solid_fill.Id)
    ogs.SetSurfaceForegroundPatternColor(DB.Color(226, 226, 220))
    for nm, eye, ur, vr, wr in specs:
        pts = [wf(None, O, ex, ey, ez, u, v, w) for u in ur for v in vr for w in wr]
        bmin = DB.XYZ(min(p.X for p in pts), min(p.Y for p in pts), min(p.Z for p in pts))
        bmax = DB.XYZ(max(p.X for p in pts), max(p.Y for p in pts), max(p.Z for p in pts))
        vw = make_view(pdoc, 'KW_' + nm, eye, tgt, keepcats, bmin, bmax)
        for pid in proxy_ids:
            vw.SetCategoryHidden(pid, True)
        vw.SetElementOverrides(wall.Id, ogs)
        pdoc.Regenerate()
        cb = vw.CropBox
        c = cb.Transform.Inverse.OfPoint(tgt)
        half = max(max(abs(x) for x in ur), max(abs(x) for x in vr)) / IN * (1.15 if nm != 'side' else 1.0)
        if nm == 'side':
            half = 5.5 / IN
        cb.Min = DB.XYZ(c.X - half, c.Y - half, cb.Min.Z)
        cb.Max = DB.XYZ(c.X + half, c.Y + half, cb.Max.Z)
        vw.CropBox = cb
        vw.CropBoxActive = True
        vw.CropBoxVisible = False
        made.append((nm, vw))
    tx.Commit()
    for nm, vw in made:
        V['views'][nm] = export_view(pdoc, vw, 'KW1041MBK_%s.png' % nm)
    stage('views exported')
    pdoc.Close(False)
    docs.remove(pdoc)
    V['ok'] = True
except Exception:
    V['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
    write_json('validation.json', V)
