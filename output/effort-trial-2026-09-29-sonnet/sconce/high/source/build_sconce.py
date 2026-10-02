# -*- coding: utf-8 -*-
"""Build the Visual Comfort Studio Nodes Angled Wall Sconce KW1041MBK as a native Revit 2025 face-based lighting family.
Run only through _harness/revit_run.py. Writes build_result.json (stage log) and the RFA into the run folder."""
import sys
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/high/source')
from common import *

report = {'stages': []}
docs = []


def stage(name):
    report['stages'].append(name)
    write_json('build_result.json', report)


def set_color(asset, key, color):
    prop = asset.FindByName(key)
    if prop is None:
        raise RuntimeError('Appearance property missing: ' + key)
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.SetValueAsColor(DB.Color(*color))


def set_scalar(asset, key, value, optional=False):
    prop = asset.FindByName(key)
    if prop is None:
        if optional:
            report.setdefault('material_props_missing', []).append(key)
            return
        raise RuntimeError('Appearance property missing: ' + key)
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.Value = value


def make_material(doc, app, name, color, gloss, refl, transparency, mclass):
    assets = list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source = next(a for a in assets if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value == 'GenericSchema')
    appearance = DB.AppearanceAssetElement.Create(doc, name, source)
    mat = doc.GetElement(DB.Material.Create(doc, name))
    mat.AppearanceAssetId = appearance.Id
    mat.Color = DB.Color(*color)
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    asset = scope.Start(appearance.Id)
    set_color(asset, 'generic_diffuse', color)
    set_scalar(asset, 'generic_glossiness', gloss)
    set_scalar(asset, 'generic_reflectivity_at_0deg', refl)
    set_scalar(asset, 'generic_reflectivity_at_90deg', 0.75)
    set_scalar(asset, 'generic_transparency', transparency, optional=True)
    scope.Commit(True)
    scope.Dispose()
    mat.MaterialClass = mclass
    if transparency:
        mat.Transparency = int(round(transparency * 100))
    return mat


def bind(doc, solid, name, param, subcat):
    element = DB.FreeFormElement.Create(doc, solid)
    element.Subcategory = subcat
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), param)
    report.setdefault('parts', {})[name] = element.Id.IntegerValue
    return element


try:
    app = __revit__.Application
    report['revit_version'] = app.VersionNumber
    assert app.VersionNumber == '2025'
    report['derived'] = {'theta_deg': math.degrees(THETA), 'D0_in': D0, 'A_C_in': A_C}
    doc = app.NewFamilyDocument(TEMPLATE)
    docs.append(doc)
    stage('family created')

    tx = DB.Transaction(doc, 'Category')
    tx.Start()
    doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_LightingFixtures)
    tx.Commit()
    stage('category set')

    tx = DB.Transaction(doc, 'Light source + type')
    tx.Start()
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE).Set(1)
    fm = doc.FamilyManager
    fm.NewType(TYPE_NAME)
    tx.Commit()
    stage('light source enabled, type created')

    tx = DB.Transaction(doc, 'Parameters, materials, solids')
    tx.Start()
    metal = make_material(doc, app, 'KW1041MBK - Midnight Black Metal', (24, 24, 26), 0.45, 0.10, 0.0, 'Metal')
    glass = make_material(doc, app, 'KW1041MBK - Milk Glass', (244, 241, 232), 0.85, 0.06, 0.0, 'Glass')
    mp = fm.AddParameter('Metal Finish', DB.GroupTypeId.Materials, DB.SpecTypeId.Reference.Material, False)
    gp = fm.AddParameter('Glass Finish', DB.GroupTypeId.Materials, DB.SpecTypeId.Reference.Material, False)
    sp = fm.AddParameter('Show Disc', DB.GroupTypeId.Graphics, DB.SpecTypeId.Boolean.YesNo, True)
    fm.Set(mp, metal.Id)
    fm.Set(gp, glass.Id)
    fm.Set(sp, 1)
    stage('parameters and materials')

    cat = doc.OwnerFamily.FamilyCategory
    subs = {}
    for n in ['Backplate', 'Body', 'Socket', 'Disc', 'Shade']:
        subs[n] = doc.Settings.Categories.NewSubcategory(cat, n)

    # backplate: 5.25 in disc, 0.125 in deep, on the wall face (Z 0..0.125)
    z0 = DB.XYZ.BasisZ
    back = extrude([circle_loop(xyz(0, 0, 0), DB.XYZ.BasisX, DB.XYZ.BasisY, BACK_R)], z0, BACK_T)
    bind(doc, back, 'Backplate', mp, subs['Backplate'])

    # body: 4.25 in drum along the wall normal, cut by the plane through the face centre tilted THETA from vertical
    drum = extrude([circle_loop(xyz(0, 0, BACK_T), DB.XYZ.BasisX, DB.XYZ.BasisY, BODY_R)], z0, D0 + 3.0 - BACK_T)
    cutter = extrude([rect_loop(FACE_CENTER, DB.XYZ.BasisX, UP, 6.0, 8.0)], AXIS, 6.0)
    body = DB.BooleanOperationsUtils.ExecuteBooleanOperation(drum, cutter, DB.BooleanOperationsType.Difference)
    bind(doc, body, 'Body', mp, subs['Body'])

    # socket: collar through the disc hole, then a lamp-holder stem inside the shade; revolved about the shade axis
    socket = revolve_profile([('L', (0, 0), (COLLAR_R, 0)), ('L', (COLLAR_R, 0), (COLLAR_R, S0)), ('L', (COLLAR_R, S0), (STEM_R, S0)),
                              ('L', (STEM_R, S0), (STEM_R, S0 + STEM_LEN)), ('L', (STEM_R, S0 + STEM_LEN), (0, S0 + STEM_LEN)),
                              ('L', (0, S0 + STEM_LEN), (0, 0))])
    bind(doc, socket, 'Socket', mp, subs['Socket'])

    # disc: 8 in diameter steel disc parallel to the slanted face, with a hole for the socket collar
    disc = extrude([circle_loop(FACE_CENTER, DB.XYZ.BasisX, UP, DISC_R), circle_loop(FACE_CENTER, DB.XYZ.BasisX, UP, COLLAR_R + 0.01)], AXIS, DISC_T)
    disc_el = bind(doc, disc, 'Disc', mp, subs['Disc'])
    fm.AssociateElementParameterToFamilyParameter(disc_el.get_Parameter(DB.BuiltInParameter.IS_VISIBLE_PARAM), sp)

    # shade: hollow milk glass sphere R 1.75 truncated 0.25 in at the back (3.25 in along the axis)
    ro = SHADE_R
    ri = SHADE_R - SHADE_WALL
    psi_o = math.acos(-(A_C - S0) / ro)
    psi_i = math.acos(-(A_C - S0) / ri)

    def pol(r, psi):
        return (r * math.sin(psi), A_C + r * math.cos(psi))
    shade = revolve_profile([('A', pol(ro, psi_o), (0, A_C + ro), pol(ro, psi_o / 2.0)),
                             ('L', (0, A_C + ro), (0, A_C + ri)),
                             ('A', (0, A_C + ri), pol(ri, psi_i), pol(ri, psi_i / 2.0)),
                             ('L', pol(ri, psi_i), pol(ro, psi_o))])
    bind(doc, shade, 'Shade', gp, subs['Shade'])
    stage('solids')

    # identity data
    for bip, value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, 'Visual Comfort Studio'), (DB.BuiltInParameter.ALL_MODEL_MODEL, 'KW1041MBK'),
                       (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION, 'Nodes Angled Wall Sconce, Midnight Black / Milk, 1 x G9 3W LED')]:
        try:
            p = fm.get_Parameter(bip)
            fm.Set(p, value)
        except Exception as ex:
            report.setdefault('identity_errors', []).append(str(bip) + ': ' + str(ex))
    tx.Commit()
    stage('identity data')

    # light source
    tx = DB.Transaction(doc, 'Configure light source')
    tx.Start()
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    lf.SetLightShapeStyle(DB.Lighting.LightShapeStyle.Point)
    lf.SetLightDistributionStyle(DB.Lighting.LightDistributionStyle.Spherical)
    tx.Commit()
    tx = DB.Transaction(doc, 'Move light source')
    tx.Start()
    ids = [e.Id for e in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource)]
    report['light_source_ids'] = [i.IntegerValue for i in ids]
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    cur = lf.GetLightSourceTransform().Origin
    target = xyz(0, -A_C * SIN, D0 + A_C * COS)
    report['light_before_in'] = [cur.X * 12, cur.Y * 12, cur.Z * 12]
    DB.ElementTransformUtils.MoveElement(doc, ids[0], target.Subtract(cur))
    tx.Commit()
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    now = lf.GetLightSourceTransform().Origin
    report['light_after_in'] = [now.X * 12, now.Y * 12, now.Z * 12]
    report['light_target_in'] = [target.X * 12, target.Y * 12, target.Z * 12]
    report['light_types'] = lf.GetNumberOfLightTypes()
    stage('light source moved')

    tx = DB.Transaction(doc, 'Light type values')
    tx.Start()
    try:
        lt = lf.GetLightType(0)
        lt.SetLightShape(DB.Lighting.PointLightShape())
        lt.SetLightDistribution(DB.Lighting.SphericalLightDistribution())
        lt.SetInitialIntensity(DB.Lighting.InitialWattageIntensity(90.0, 3.0))
        lt.SetInitialColor(DB.Lighting.CustomInitialColor(2700.0))
        lt.SetLossFactor(DB.Lighting.BasicLossFactor(1.0))
        report['light_type_set'] = True
    except Exception:
        report['light_type_error'] = traceback.format_exc()
    tx.Commit()
    stage('light type values')

    opts = DB.SaveAsOptions()
    opts.OverwriteExistingFile = True
    doc.SaveAs(guard(RFA), opts)
    stage('saved')
    report['ok'] = True
except Exception:
    report['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
    write_json('build_result.json', report)
