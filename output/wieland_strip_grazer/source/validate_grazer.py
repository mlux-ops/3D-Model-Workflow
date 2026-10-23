# -*- coding: utf-8 -*-
"""Validate the saved grazer family in Revit 2025: reopen, category, light source settings, placement on the top face of a ledge in a disposable
project, envelope, aim in world space, material substitution, view export. Run only through _harness/revit_run.py. Writes validation.json."""
import sys
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/wieland_strip_grazer/source')
from common import *
import glob

V = {'stages': [], 'gates': {}}
docs = []
VIEWS = os.path.join(OUT, 'views')
EXPORT_TMP = os.path.join(OUT, '_work', 'export')


def stage(name):
    V['stages'].append(name)
    write_json('validation.json', V)


def r4(x):
    return round(x, 4)


def ename(el):
    return DB.Element.Name.__get__(el)


def solid_points(solid):
    pts = []
    for f in solid.Faces:
        m = f.Triangulate(1.0)
        if m is not None:
            for v in m.Vertices:
                pts.append(v)
    return pts


def gate(name, ok, detail=None):
    V['gates'][name] = {'pass': bool(ok), 'detail': detail}


def light_info(doc):
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    t = lf.GetLightSourceTransform()
    d = {'shape': str(lf.GetLightShapeStyle()), 'distribution': str(lf.GetLightDistributionStyle()), 'n_types': lf.GetNumberOfLightTypes(),
         'origin_in': [r4(t.Origin.X * IN), r4(t.Origin.Y * IN), r4(t.Origin.Z * IN)],
         'basisX': [r4(t.BasisX.X), r4(t.BasisX.Y), r4(t.BasisX.Z)], 'basisZ': [r4(t.BasisZ.X), r4(t.BasisZ.Y), r4(t.BasisZ.Z)]}
    lt = lf.GetLightType(0)
    ii = lt.GetInitialIntensity()
    d['intensity_class'] = ii.GetType().Name
    for attr in ['Flux', 'Wattage', 'Efficacy']:
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
    d['loss_factor_class'] = lt.GetLossFactor().GetType().Name
    try:
        d['loss_factor_value'] = lt.GetLossFactor().LossFactor
    except Exception:
        pass
    return d


def cone_probe(doc):
    """Bounding box (inches, family frame) of the main spot-cone solid of the light source: the geometry item with the most points."""
    eid = [e.Id for e in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource)][0]
    opt = DB.Options()
    opt.DetailLevel = DB.ViewDetailLevel.Fine
    opt.IncludeNonVisibleObjects = True
    opt.ComputeReferences = False
    best = [0, None]

    def walk(g):
        for item in g:
            if isinstance(item, DB.GeometryInstance):
                walk(item.GetInstanceGeometry())
            elif isinstance(item, DB.Solid):
                pts = []
                for f in item.Faces:
                    m = f.Triangulate(1.0)
                    if m is not None:
                        pts.extend(list(m.Vertices))
                if len(pts) > best[0]:
                    best[0] = len(pts)
                    best[1] = pts
    walk(doc.GetElement(eid).get_Geometry(opt))
    pts = best[1]
    ext = lambda f: [r4(min(f(p) for p in pts) * IN), r4(max(f(p) for p in pts) * IN)]
    return {'n_points': best[0], 'x': ext(lambda p: p.X), 'y': ext(lambda p: p.Y), 'z': ext(lambda p: p.Z)}


def make_view(doc, name, eye, target, bmin, bmax):
    vtype = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(doc, vtype.Id)
    view.Name = name
    fwd = target.Subtract(eye).Normalize()
    up = DB.XYZ.BasisZ
    if abs(up.DotProduct(fwd)) > 0.98:
        up = DB.XYZ.BasisY
    right = fwd.CrossProduct(up).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, right.CrossProduct(fwd).Normalize(), fwd))
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.DisplayStyle = DB.DisplayStyle.Shading
    keep = [DB.ElementId(DB.BuiltInCategory.OST_LightingFixtures), DB.ElementId(DB.BuiltInCategory.OST_Floors)]
    for cat in doc.Settings.Categories:
        try:
            if cat.Id not in keep and view.CanCategoryBeHidden(cat.Id):
                view.SetCategoryHidden(cat.Id, True)
        except Exception:
            pass
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


try:
    app = __revit__.Application
    if not os.path.isdir(VIEWS):
        os.makedirs(VIEWS)

    # ---- A. reopen the saved family
    fdoc = app.OpenDocumentFile(RFA)
    docs.append(fdoc)
    fam = {'warnings': [w.GetDescriptionText() for w in fdoc.GetWarnings()]}
    fam['category'] = fdoc.OwnerFamily.FamilyCategory.Name
    fam['placement_type'] = str(fdoc.OwnerFamily.FamilyPlacementType)
    fm = fdoc.FamilyManager
    fam['types'] = [t.Name for t in fm.Types]
    fam['light_source_param'] = fdoc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE).AsInteger()
    ct = fm.CurrentType
    pv = {}
    for p in fm.Parameters:
        n = p.Definition.Name
        if n in ('Emit from Line Length', 'Spot Beam Angle', 'Spot Field Angle', 'Tilt Angle'):
            pv[n] = ct.AsDouble(p)
        elif n == MATERIAL_PARAM:
            pv[n] = {'instance': p.IsInstance, 'value': ename(fdoc.GetElement(ct.AsElementId(p)))}
    fam['type_parameters'] = pv
    fam['light'] = light_info(fdoc)
    SRC_T = DB.Lighting.LightFamily.GetLightFamily(fdoc).GetLightSourceTransform()
    CONE = cone_probe(fdoc)
    fam['cone_bbox_in'] = CONE
    V['family'] = fam
    stage('family reopened')
    fdoc.Close(False)
    docs.remove(fdoc)

    L = fam['light']
    gate('category_lighting_fixtures', fam['category'] == 'Lighting Fixtures', fam['category'])
    gate('placement_work_plane_based', fam['placement_type'] == 'WorkPlaneBased', fam['placement_type'])
    gate('light_source_flag_on', fam['light_source_param'] == 1)
    gate('type_name', fam['types'] == [TYPE_NAME], fam['types'])
    gate('family_warnings_zero', len(fam['warnings']) == 0, fam['warnings'])
    gate('shape_line', L['shape'] == 'Line' and L['light_shape'] == 'LineLightShape', [L['shape'], L['light_shape']])
    gate('distribution_spot', L['distribution'] == 'Spot' and L['light_distribution'] == 'SpotLightDistribution', [L['distribution'], L['light_distribution']])
    gate('line_length_4ft10', abs(pv['Emit from Line Length'] * IN - LINE_LENGTH) < 0.001, pv['Emit from Line Length'] * IN)
    gate('beam_10deg', abs(math.degrees(pv['Spot Beam Angle']) - BEAM_DEG) < 0.01, math.degrees(pv['Spot Beam Angle']))
    gate('field_30deg', abs(math.degrees(pv['Spot Field Angle']) - FIELD_DEG) < 0.01, math.degrees(pv['Spot Field Angle']))
    gate('tilt_90', abs(math.degrees(pv['Tilt Angle']) - TILT_DEG) < 0.01, math.degrees(pv['Tilt Angle']))
    gate('flux_2500', abs(L.get('intensity_Flux', -1) - FLUX_LM) < 0.5, [L['intensity_class'], L.get('intensity_Flux')])
    gate('cct_2800', abs(L.get('color_temperature_K', -1) - CCT_K) < 0.5, [L['color_class'], L.get('color_temperature_K')])
    gate('loss_factor_1', abs(L.get('loss_factor_value', -1) - LOSS) < 1e-6, L.get('loss_factor_value'))
    gate('source_origin_centered_1_75_above_host', abs(L['origin_in'][0]) < 0.001 and abs(L['origin_in'][1]) < 0.001 and abs(L['origin_in'][2] - SOURCE_Z) < 0.001, L['origin_in'])
    gate('source_rotated_180_about_x', L['basisZ'][2] < -0.999 and L['basisX'][0] > 0.999, [L['basisX'], L['basisZ']])
    # the spot cone itself: starts at the source, runs up 10 ft, centred in X and Y (a cone along the fixture would be centred on Y but skewed in X)
    oz = L['origin_in'][2]
    gate('cone_points_up_not_along_fixture', abs(CONE['z'][0] - oz) < 0.1 and CONE['z'][1] - oz > 100.0 and abs(CONE['x'][0] + CONE['x'][1]) < 0.5 and abs(CONE['y'][0] + CONE['y'][1]) < 0.5, CONE)
    gate('body_finish_type_param', pv[MATERIAL_PARAM]['instance'] is False, pv[MATERIAL_PARAM])

    # ---- B. host on the top face of a ledge (floor) in a disposable project
    pdoc = app.NewProjectDocument(DB.UnitSystem.Imperial)
    docs.append(pdoc)
    tx = DB.Transaction(pdoc, 'ledge + fixture')
    tx.Start()
    level = DB.Level.Create(pdoc, 0.0)
    ftype = DB.FilteredElementCollector(pdoc).OfClass(DB.FloorType).FirstElement()
    loop = DB.CurveLoop()
    pts = [DB.XYZ(-10, -2, 0), DB.XYZ(10, -2, 0), DB.XYZ(10, 2, 0), DB.XYZ(-10, 2, 0)]
    for i in range(4):
        loop.Append(DB.Line.CreateBound(pts[i], pts[(i + 1) % 4]))
    ledge = DB.Floor.Create(pdoc, List[DB.CurveLoop]([loop]), ftype.Id, level.Id)
    pdoc.Regenerate()
    top = DB.HostObjectUtils.GetTopFaces(ledge)[0]
    tface = ledge.GetGeometryObjectFromReference(top)
    famref = clr.Reference[DB.Family]()
    pdoc.LoadFamily(RFA, famref)
    family = famref.Value
    sym = pdoc.GetElement(list(family.GetFamilySymbolIds())[0])
    if not sym.IsActive:
        sym.Activate()
    pdoc.Regenerate()
    O = DB.XYZ(0.0, 0.0, tface.Origin.Z)
    inst = pdoc.Create.NewFamilyInstance(top, O, DB.XYZ.BasisX, sym)
    pdoc.Regenerate()
    tx.Commit()
    top_z_in = tface.Origin.Z * IN
    xf = inst.GetTransform()
    V['hosting'] = {'host_is_floor': inst.Host.Id == ledge.Id, 'top_face_normal': [r4(tface.FaceNormal.X), r4(tface.FaceNormal.Y), r4(tface.FaceNormal.Z)],
                    'top_z_in': r4(top_z_in), 'instance_transform_basisX': [r4(xf.BasisX.X), r4(xf.BasisX.Y), r4(xf.BasisX.Z)],
                    'instance_transform_basisZ': [r4(xf.BasisZ.X), r4(xf.BasisZ.Y), r4(xf.BasisZ.Z)], 'instance_origin_in': [r4(xf.Origin.X * IN), r4(xf.Origin.Y * IN), r4(xf.Origin.Z * IN)]}
    stage('placed')
    gate('hosted_on_ledge_top_face', V['hosting']['host_is_floor'] and tface.FaceNormal.Z > 0.999, V['hosting'])
    gate('instance_axes_align', xf.BasisX.X > 0.999 and xf.BasisZ.Z > 0.999, V['hosting'])

    # world-space aim: compose the instance transform with the family source transform (read from the reopened family in A)
    lt = SRC_T
    wo = xf.OfPoint(lt.Origin)
    cz = (CONE['z'][0] + CONE['z'][1]) / 2.0 - lt.Origin.Z * IN
    cx = (CONE['x'][0] + CONE['x'][1]) / 2.0 - lt.Origin.X * IN
    cy = (CONE['y'][0] + CONE['y'][1]) / 2.0 - lt.Origin.Y * IN
    emit = xf.OfVector(DB.XYZ(cx, cy, cz).Normalize())     # cone axis from the cone solid, not from the source frame's -Z
    V['light_world'] = {'origin_in': [r4(wo.X * IN), r4(wo.Y * IN), r4(wo.Z * IN)], 'emission_direction': [r4(emit.X), r4(emit.Y), r4(emit.Z)],
                        'height_above_host_in': r4(wo.Z * IN - top_z_in)}
    gate('light_emits_up_in_world', emit.Z > 0.999, V['light_world']['emission_direction'])
    gate('light_height_1_75_above_host', abs(V['light_world']['height_above_host_in'] - SOURCE_Z) < 0.001, V['light_world']['height_above_host_in'])

    # envelope of the body (light-source proxy excluded)
    opt = DB.Options()
    opt.DetailLevel = DB.ViewDetailLevel.Fine
    allpts = []
    faces = {}
    proxies = []
    for solid in all_solids(pdoc.GetElement(inst.Id).get_Geometry(opt)):
        gs = pdoc.GetElement(solid.GraphicsStyleId)
        cname = gs.GraphicsStyleCategory.Name if gs is not None and gs.GraphicsStyleCategory is not None else 'unknown'
        if cname == 'Light Source':
            proxies.append(cname)
            continue
        allpts.extend(solid_points(solid))
        for f in solid.Faces:
            mid = f.MaterialElementId
            mn = ename(pdoc.GetElement(mid)) if mid != DB.ElementId.InvalidElementId else '<none>'
            faces[mn] = faces.get(mn, 0) + 1

    def ext(d):
        vals = [p.Subtract(O).DotProduct(d) * IN for p in allpts]
        return [r4(min(vals)), r4(max(vals))]
    ex_, ey_, ez_ = ext(DB.XYZ.BasisX), ext(DB.XYZ.BasisY), ext(DB.XYZ.BasisZ)
    V['envelope_in'] = {'x': ex_, 'y': ey_, 'z': ez_, 'size': {'L': r4(ex_[1] - ex_[0]), 'W': r4(ey_[1] - ey_[0]), 'H': r4(ez_[1] - ez_[0])},
                        'light_source_proxy_solids_excluded': len(proxies), 'faces_by_material': faces}
    gate('body_4ft10_x_2_x_1_5', abs(V['envelope_in']['size']['L'] - BODY_L) < 0.01 and abs(V['envelope_in']['size']['W'] - BODY_W) < 0.01 and abs(V['envelope_in']['size']['H'] - BODY_H) < 0.01, V['envelope_in']['size'])
    gate('body_sits_on_host_face', abs(ez_[0]) < 0.01 and abs(ex_[0] + BODY_L / 2.0) < 0.01, [ex_, ez_])
    gate('source_clear_of_body', V['light_world']['height_above_host_in'] > ez_[1], [V['light_world']['height_above_host_in'], ez_[1]])
    stage('measured')

    # material substitution: point the type's Body Finish at a project material and read the face materials back
    tx = DB.Transaction(pdoc, 'material substitution')
    tx.Start()
    mat = pdoc.GetElement(DB.Material.Create(pdoc, 'TEST RED'))
    mat.Color = DB.Color(200, 20, 20)
    psym = pdoc.GetElement(sym.Id)
    orig_mat = psym.LookupParameter(MATERIAL_PARAM).AsElementId()
    psym.LookupParameter(MATERIAL_PARAM).Set(mat.Id)
    pdoc.Regenerate()
    tx.Commit()
    sub_faces = {}
    for solid in all_solids(pdoc.GetElement(inst.Id).get_Geometry(opt)):
        gs = pdoc.GetElement(solid.GraphicsStyleId)
        if gs is not None and gs.GraphicsStyleCategory is not None and gs.GraphicsStyleCategory.Name == 'Light Source':
            continue
        for f in solid.Faces:
            mid = f.MaterialElementId
            mn = ename(pdoc.GetElement(mid)) if mid != DB.ElementId.InvalidElementId else '<none>'
            sub_faces[mn] = sub_faces.get(mn, 0) + 1
    V['material_substitution_faces'] = sub_faces
    gate('material_substitution', set(sub_faces.keys()) == set(['TEST RED']) and sub_faces['TEST RED'] == 6, sub_faces)
    stage('material substitution')

    # views: oblique and end elevation of the placed fixture
    c = DB.XYZ(0.0, 0.0, tface.Origin.Z + 0.1)
    bmin = DB.XYZ(-3.0, -1.5, tface.Origin.Z - 0.3)
    bmax = DB.XYZ(3.0, 1.5, tface.Origin.Z + 0.6)
    tx = DB.Transaction(pdoc, 'views')
    tx.Start()
    pdoc.GetElement(sym.Id).LookupParameter(MATERIAL_PARAM).Set(orig_mat)
    v1 = make_view(pdoc, 'oblique', DB.XYZ(-8.0, -9.0, tface.Origin.Z + 5.0), c, DB.XYZ(-2.6, -1.5, tface.Origin.Z - 0.3), DB.XYZ(2.6, 1.5, tface.Origin.Z + 0.6))
    v2 = make_view(pdoc, 'front', DB.XYZ(0.0, -12.0, tface.Origin.Z + 0.1), c, DB.XYZ(-2.6, -1.5, tface.Origin.Z - 0.3), DB.XYZ(2.6, 1.5, tface.Origin.Z + 0.6))
    pdoc.Regenerate()
    tx.Commit()
    V['views'] = {'oblique': export_view(pdoc, v1, 'oblique.png'), 'front': export_view(pdoc, v2, 'front.png')}
    stage('views exported')

    V['technical_pass'] = all(g['pass'] for g in V['gates'].values())
    V['visual_verdict'] = 'PENDING REVIEWER'
    V['not_verified'] = ['Ray trace / render of the graze effect on the fluted stone (headless Revit cannot render artificial light); spec says to confirm in a Ray Trace view']
    stage('done')
except Exception:
    V['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
    write_json('validation.json', V)
