# -*- coding: utf-8 -*-
"""Build the Visual Comfort Studio Nodes Angled Wall Sconce KW1041MBK (Midnight Black / Milk) as a native
Revit 2025 face-based Lighting Fixtures family. Run with pyRevit (IronPython 2.7) through the harness runner:
  python _harness/revit_run.py <this file> 300
Writes the RFA, work/build_report.json and work/export/*.png. All dimensions are inches unless noted."""
import sys
import os
import math
import shutil
import traceback
RUN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/'
sys.path.insert(0, RUN + 'source')
from guard import safe_path, dump_json
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

TEMPLATE = 'C:\\ProgramData\\Autodesk\\RVT 2025\\Family Templates\\English-Imperial\\Generic Model face based.rft'
RFA = RUN + 'Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa'
TYPE_NAME = 'KW1041MBK - Midnight Black / Milk'

# ---- design values (inches) -------------------------------------------------------------------------
PLATE_D = 5.25          # published
PLATE_T = 0.125         # published
BODY_D = 4.24           # measured from the install sheet vector drawing
DISC_D = 8.0            # published overall width
DISC_T = 0.094          # measured from the install sheet vector drawing (0.094-0.10)
SOCKET_D = 1.06         # measured from the install sheet vector drawing (nipple)
SHADE_R = 1.75          # published 3.5 max dia
SHADE_AXIAL = 3.25      # published
H_ENV = 7.63            # published overall height
D_ENV = 5.50            # published overall projection
ZC = 1.975              # depth of the body cut-face centre: mean of measured top 2.65 and bottom 1.30 edge depths
LAMP_FLUX_LM = 250.0    # chosen: typical 3 W G9 LED (no lumen figure is published)
LAMP_CCT_K = 2700.0     # chosen: warm-white, typical for this lamp class (not published)
SOURCE_SYMBOL_FT = 0.05
GLASS_T = 0.10          # inferred shade wall thickness (not published)
SOCKET_LEN = 0.56       # measured nipple length on the install sheet drawing
BASE_R = math.sqrt(SHADE_R ** 2 - (SHADE_AXIAL - SHADE_R) ** 2)


def solve_theta():
    lo, hi = math.radians(5.0), math.radians(40.0)
    f = lambda a: DISC_D * math.cos(a) + DISC_T * math.sin(a) - H_ENV
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


THETA = solve_theta()
CT, ST = math.cos(THETA), math.sin(THETA)
N = (0.0, -ST, CT)      # outward normal of the angled cut face (out and downward)
U = (1.0, 0.0, 0.0)
V = (0.0, CT, ST)       # in-plane "up" of the cut face
C = (0.0, 0.0, ZC)      # cut-face centre
S_BASE = (D_ENV - SHADE_R - ZC) / CT - (SHADE_AXIAL - SHADE_R)   # shade base offset from the cut face along N
LAMP_CENTRE_OFF = S_BASE + (SHADE_AXIAL - SHADE_R)               # sphere centre offset along N

report = {'design': {'theta_deg': math.degrees(THETA), 'zc_in': ZC, 'shade_base_offset_along_axis_in': S_BASE,
                     'sphere_centre_offset_along_axis_in': LAMP_CENTRE_OFF, 'shade_base_dia_in': 2 * BASE_R,
                     'disc_t_in': DISC_T, 'body_d_in': BODY_D, 'socket_d_in': SOCKET_D, 'plate_d_in': PLATE_D,
                     'plate_t_in': PLATE_T, 'disc_d_in': DISC_D}}
docs = []


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def X(t):
    return DB.XYZ(t[0] / 12.0, t[1] / 12.0, t[2] / 12.0)


def D(t):
    return DB.XYZ(t[0], t[1], t[2])


def circle(center, u, v, r):
    loop = DB.CurveLoop()
    loop.Append(DB.Arc.Create(X(center), r / 12.0, 0.0, math.pi, D(u), D(v)))
    loop.Append(DB.Arc.Create(X(center), r / 12.0, math.pi, 2.0 * math.pi, D(u), D(v)))
    return loop


def rect(center, u, v, hu, hv):
    pts = [add(add(center, mul(u, -hu)), mul(v, -hv)), add(add(center, mul(u, hu)), mul(v, -hv)),
           add(add(center, mul(u, hu)), mul(v, hv)), add(add(center, mul(u, -hu)), mul(v, hv))]
    loop = DB.CurveLoop()
    for i in range(4):
        loop.Append(DB.Line.CreateBound(X(pts[i]), X(pts[(i + 1) % 4])))
    return loop


def extrude(loops, direction, dist_in):
    return DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop](loops), D(direction), dist_in / 12.0)


def make_material(doc, app, name, color, gloss, refl, mclass):
    assets = list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source = next(a for a in assets if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value == 'GenericSchema')
    appearance = DB.AppearanceAssetElement.Create(doc, name, source)
    mat = doc.GetElement(DB.Material.Create(doc, name))
    mat.AppearanceAssetId = appearance.Id
    mat.Color = DB.Color(*color)
    mat.MaterialClass = mclass
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    asset = scope.Start(appearance.Id)

    def setc(key, col):
        p = asset.FindByName(key)
        if p is None:
            raise RuntimeError('missing appearance property ' + key)
        if p.NumberOfConnectedProperties:
            p.RemoveConnectedAsset()
        p.SetValueAsColor(DB.Color(*col))

    def sets(key, val):
        p = asset.FindByName(key)
        if p is None:
            raise RuntimeError('missing appearance property ' + key)
        if p.NumberOfConnectedProperties:
            p.RemoveConnectedAsset()
        p.Value = val

    setc('generic_diffuse', color)
    sets('generic_glossiness', gloss)
    sets('generic_reflectivity_at_0deg', refl)
    sets('generic_reflectivity_at_90deg', 0.6)
    sets('generic_self_illum_luminance', 0.0)
    scope.Commit(True)
    scope.Dispose()
    return mat


def part(doc, name, solid, subcat, mat_param, parts):
    ff = DB.FreeFormElement.Create(doc, solid)
    ff.Subcategory = subcat
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(ff.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), mat_param)
    parts[name] = ff
    return ff


def preview(doc, name, eye_in, target_in):
    vtype = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(doc, vtype.Id)
    view.Name = name
    eye = X(eye_in)
    target = X(target_in)
    forward = target.Subtract(eye).Normalize()
    up = DB.XYZ.BasisY
    if abs(up.DotProduct(forward)) > 0.98:
        up = DB.XYZ.BasisZ
    right = forward.CrossProduct(up).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, right.CrossProduct(forward).Normalize(), forward))
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.DisplayStyle = DB.DisplayStyle.Shading
    for cat in doc.Settings.Categories:
        if cat.Id != doc.OwnerFamily.FamilyCategory.Id and view.CanCategoryBeHidden(cat.Id):
            view.SetCategoryHidden(cat.Id, True)
    slab_ids = [e.Id for e in DB.FilteredElementCollector(doc, view.Id).OfClass(DB.Extrusion)]
    if slab_ids:
        view.HideElements(List[DB.ElementId](slab_ids))
    region = DB.BoundingBoxXYZ()
    region.Min = X((-6.0, -6.0, -0.2))
    region.Max = X((6.0, 6.0, 7.5))
    view.SetSectionBox(region)
    view.IsSectionBoxActive = True
    doc.Regenerate()
    view.CropBoxActive = True
    view.CropBoxVisible = False
    cb = view.CropBox
    inv = cb.Transform.Inverse
    xs = []
    ys = []
    for cx in (-4.0, 4.0):
        for cy in (-3.9, 3.9):
            for cz in (0.0, 5.5):
                q = inv.OfPoint(X((cx, cy, cz)))
                xs.append(q.X)
                ys.append(q.Y)
    pad = 0.6 / 12.0
    cb.Min = DB.XYZ(min(xs) - pad, min(ys) - pad, cb.Min.Z)
    cb.Max = DB.XYZ(max(xs) + pad, max(ys) + pad, cb.Max.Z)
    view.CropBox = cb
    return view


def export(doc, views, prefix):
    opts = DB.ImageExportOptions()
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]))
    safe_path(prefix)
    if not os.path.isdir(os.path.dirname(prefix)):
        os.makedirs(os.path.dirname(prefix))
    opts.FilePath = prefix
    opts.HLRandWFViewsFileType = DB.ImageFileType.PNG
    opts.ShadowViewsFileType = DB.ImageFileType.PNG
    opts.ImageResolution = DB.ImageResolution.DPI_150
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = 1200
    doc.ExportImage(opts)


def solids_of(elem):
    out = []
    for g in elem.get_Geometry(DB.Options()):
        if isinstance(g, DB.Solid) and g.Volume > 1e-12:
            out.append(g)
    return out


tx = None
try:
    app = __revit__.Application
    report['revit_version'] = app.VersionNumber
    report['stage'] = 'create'
    dump_json(report, RUN + 'work/build_report.json')
    doc = app.NewFamilyDocument(TEMPLATE)
    docs.append(doc)
    tx = DB.Transaction(doc, 'Build KW1041MBK')
    tx.Start()
    doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_LightingFixtures)
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE).Set(1)
    fm = doc.FamilyManager
    fm.NewType(TYPE_NAME)

    black = make_material(doc, app, 'KW1041 Midnight Black', (34, 32, 32), 0.42, 0.10, 'Metal')
    milk = make_material(doc, app, 'KW1041 Milk Glass', (244, 240, 234), 0.62, 0.06, 'Glass')
    p_metal = fm.AddParameter('Metal Finish', DB.GroupTypeId.Materials, DB.SpecTypeId.Reference.Material, False)
    p_glass = fm.AddParameter('Glass Finish', DB.GroupTypeId.Materials, DB.SpecTypeId.Reference.Material, False)
    p_disc = fm.AddParameter('Show Disc', DB.GroupTypeId.Graphics, DB.SpecTypeId.Boolean.YesNo, True)
    p_notes = fm.AddParameter('Model Notes', DB.GroupTypeId.IdentityData, DB.SpecTypeId.String.Text, False)
    fm.Set(p_metal, black.Id)
    fm.Set(p_glass, milk.Id)
    fm.Set(p_disc, 1)
    fm.Set(p_notes, 'Visualization family built from published envelope (8.00 W x 7.63 H x 5.50 D in), install-sheet drawing and product photos. '
                    'Backplate 5.25 dia x 0.125 and shade 3.5 dia x 3.25 are published; body, disc thickness, socket and tilt are measured or derived (see README). '
                    'Lamp photometrics (250 lm, 2700 K) are assumed, not published.')
    for bip, val in ((DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, 'Visual Comfort Studio'),
                     (DB.BuiltInParameter.ALL_MODEL_MODEL, 'KW1041MBK'),
                     (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION, 'Nodes Angled Wall Sconce, Midnight Black with Milk glass shade. 1 x JCD/G9 3 W 120 V LED.')):
        p = fm.get_Parameter(bip)
        if p is not None:
            fm.Set(p, val)
    fam_text = {}
    for q in fm.Parameters:
        nm = q.Definition.Name
        if nm == 'Lamp':
            fm.Set(q, 'JCD/G9/3W/120V LED')
        elif nm == 'Wattage Comments':
            fm.Set(q, '3 W')
        elif nm == 'Apparent Power':
            fm.Set(q, DB.UnitUtils.ConvertToInternalUnits(3.0, DB.UnitTypeId.VoltAmperes))
        elif nm == 'Light Source Symbol Size':
            fm.Set(q, SOURCE_SYMBOL_FT)
    report['stage'] = 'params'

    cats = {}
    for nm in ('Backplate', 'Body', 'Socket', 'Disc', 'Shade'):
        cats[nm] = doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory, nm)

    parts = {}
    # backplate: on the host face (z = 0), projecting +Z
    plate = extrude([circle((0, 0, 0), (1, 0, 0), (0, 1, 0), PLATE_D / 2.0)], (0, 0, 1), PLATE_T)
    part(doc, 'Backplate', plate, cats['Backplate'], p_metal, parts)
    # body: cylinder cut by the angled plane through C with normal N
    z_top = ZC + (BODY_D / 2.0) * math.tan(THETA) + 0.5
    cyl = extrude([circle((0, 0, PLATE_T), (1, 0, 0), (0, 1, 0), BODY_D / 2.0)], (0, 0, 1), z_top - PLATE_T)
    cutter = extrude([rect(C, U, V, 6.0, 6.0)], N, 6.0)
    body = DB.BooleanOperationsUtils.ExecuteBooleanOperation(cyl, cutter, DB.BooleanOperationsType.Difference)
    part(doc, 'Body', body, cats['Body'], p_metal, parts)
    # socket nipple from the cut face into the shade opening (SOCKET_LEN = measured nipple length)
    sock = extrude([circle(C, U, V, SOCKET_D / 2.0)], N, SOCKET_LEN)
    part(doc, 'Socket', sock, cats['Socket'], p_metal, parts)
    # disc: annulus on the cut face, hole for the socket
    disc = extrude([circle(C, U, V, DISC_D / 2.0), circle(C, U, V, SOCKET_D / 2.0)], N, DISC_T)
    ff_disc = part(doc, 'Disc', disc, cats['Disc'], p_metal, parts)
    fm.AssociateElementParameterToFamilyParameter(ff_disc.get_Parameter(DB.BuiltInParameter.IS_VISIBLE_PARAM), p_disc)
    # shade: sphere R truncated flat at SHADE_AXIAL, revolved about the cut-face normal
    base = add(C, mul(N, S_BASE))
    pt0 = base
    pt1 = add(base, mul(U, BASE_R))
    pt2 = add(base, mul(N, SHADE_AXIAL))
    ctr = add(base, mul(N, SHADE_AXIAL - SHADE_R))
    phi0 = math.atan2(-(SHADE_AXIAL - SHADE_R), BASE_R)
    phim = 0.5 * (phi0 + math.pi / 2.0)
    ptm = add(ctr, add(mul(U, SHADE_R * math.cos(phim)), mul(N, SHADE_R * math.sin(phim))))
    ri = SHADE_R - GLASS_T
    ib = math.sqrt(ri ** 2 - (SHADE_AXIAL - SHADE_R) ** 2)
    pi_apex = add(base, mul(N, SHADE_AXIAL - GLASS_T))
    pi_base = add(base, mul(U, ib))
    iphi0 = math.atan2(-(SHADE_AXIAL - SHADE_R), ib)
    iphim = 0.5 * (iphi0 + math.pi / 2.0)
    pim = add(ctr, add(mul(U, ri * math.cos(iphim)), mul(N, ri * math.sin(iphim))))
    prof = DB.CurveLoop()
    prof.Append(DB.Line.CreateBound(X(pt1), X(pi_base)))
    prof.Append(DB.Arc.Create(X(pi_base), X(pi_apex), X(pim)))
    prof.Append(DB.Line.CreateBound(X(pi_apex), X(pt2)))
    prof.Append(DB.Arc.Create(X(pt2), X(pt1), X(ptm)))
    report['design']['shade_inner_base_dia_in'] = 2 * ib
    bx = DB.XYZ(U[0], U[1], U[2])
    bz = DB.XYZ(N[0], N[1], N[2])
    frame = DB.Frame(X(base), bx, bz.CrossProduct(bx), bz)
    shade = DB.GeometryCreationUtilities.CreateRevolvedGeometry(frame, List[DB.CurveLoop]([prof]), 0.0, 2.0 * math.pi)
    part(doc, 'Shade', shade, cats['Shade'], p_glass, parts)
    report['stage'] = 'geometry'

    # light source: point emitter at the sphere centre
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    lf.SetLightShapeStyle(DB.Lighting.LightShapeStyle.Point)
    lf.SetLightDistributionStyle(DB.Lighting.LightDistributionStyle.Spherical)
    lt = lf.GetLightType(0)
    lt.SetLightShape(DB.Lighting.PointLightShape())
    lt.SetLightDistribution(DB.Lighting.SphericalLightDistribution())
    lt.SetInitialIntensity(DB.Lighting.InitialFluxIntensity(LAMP_FLUX_LM))
    lt.SetInitialColor(DB.Lighting.CustomInitialColor(LAMP_CCT_K))
    lt.SetLossFactor(DB.Lighting.BasicLossFactor(1.0))
    doc.Regenerate()
    src = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource).FirstElement()
    origin0 = lf.GetLightSourceTransform().Origin
    target = add(C, mul(N, LAMP_CENTRE_OFF))
    move = DB.XYZ(target[0] / 12.0 - origin0.X, target[1] / 12.0 - origin0.Y, target[2] / 12.0 - origin0.Z)
    DB.ElementTransformUtils.MoveElement(doc, src.Id, move)
    report['light_target_in'] = list(target)
    report['stage'] = 'light'

    doc.Regenerate()
    tgt = (0.0, -0.6, 3.5)
    views = [preview(doc, 'Front', add(tgt, (0, 0, 60.0)), tgt),
             preview(doc, 'Side', add(tgt, (-60.0, 0, 0)), tgt),
             preview(doc, 'Oblique', add(tgt, (-38.0, 10.4, 45.2)), tgt)]
    tx.Commit()
    tx = None
    report['stage'] = 'committed'

    # in-family readback
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    lt = lf.GetLightType(0)
    o = lf.GetLightSourceTransform().Origin
    src = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource).FirstElement()
    bb = src.get_BoundingBox(None)
    report['light'] = {'shape_style': str(lf.GetLightShapeStyle()), 'distribution_style': str(lf.GetLightDistributionStyle()),
                       'intensity_type': type(lt.GetInitialIntensity()).__name__, 'intensity_value': lt.GetInitialIntensity().InitialIntensityValue,
                       'colour_type': type(lt.GetInitialColor()).__name__, 'colour_K': lt.GetInitialColor().TemperatureValue,
                       'loss_factor': lt.GetLossFactor().LossFactorValue,
                       'source_transform_origin_in': [o.X * 12, o.Y * 12, o.Z * 12],
                       'source_bbox_in': [bb.Min.X * 12, bb.Min.Y * 12, bb.Min.Z * 12, bb.Max.X * 12, bb.Max.Y * 12, bb.Max.Z * 12] if bb else None}
    pr = {}
    for nm, ff in parts.items():
        ss = solids_of(ff)
        b = ff.get_BoundingBox(None)
        pr[nm] = {'id': str(ff.Id.Value), 'solids': len(ss), 'faces': sum(s.Faces.Size for s in ss), 'volume_in3': sum(s.Volume for s in ss) * 1728.0,
                  'bbox_in': [c * 12 for c in (b.Min.X, b.Min.Y, b.Min.Z, b.Max.X, b.Max.Y, b.Max.Z)] if b else None}
    report['parts'] = pr
    report['family_params'] = [[q.Definition.Name, str(q.StorageType), q.IsInstance] for q in fm.Parameters]
    report['placement_type'] = str(doc.OwnerFamily.FamilyPlacementType)
    report['category'] = doc.OwnerFamily.FamilyCategory.Name
    report['family_warnings_prebuild'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    report['apparent_power_display'] = None
    for q in fm.Parameters:
        if q.Definition.Name == 'Apparent Power':
            report['apparent_power_display'] = fm.CurrentType.AsValueString(q)
    report['stage'] = 'saving'
    dump_json(report, RUN + 'work/build_report.json')

    so = DB.SaveAsOptions()
    so.OverwriteExistingFile = True
    so.PreviewViewId = views[2].Id
    doc.SaveAs(safe_path(RFA), so)
    export(doc, views, RUN + 'work/export/nodes')
    report['stage'] = 'saved'
    report['exports'] = sorted(os.listdir(RUN + 'work/export'))
except Exception:
    report['error'] = traceback.format_exc()
finally:
    if tx is not None:
        try:
            tx.RollBack()
        except Exception:
            pass
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
    report['done'] = True
    dump_json(report, RUN + 'work/build_report.json')
