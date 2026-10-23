# -*- coding: utf-8 -*-
"""Build the Wieland hidden linear wall grazer (uplight) as a native Revit 2025 face-based Lighting Fixtures family with a Line / Spot light source.
Run only through _harness/revit_run.py. Writes build_result.json (stage log) and the RFA into the run folder."""
import sys
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/wieland_strip_grazer/source')
from common import *

report = {'stages': []}
docs = []


def stage(name):
    report['stages'].append(name)
    write_json('build_result.json', report)


def set_scalar(asset, key, value):
    prop = asset.FindByName(key)
    if prop is None:
        raise RuntimeError('Appearance property missing: ' + key)
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.Value = value


def make_material(doc, app, name, color, gloss, refl):
    assets = list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source = next(a for a in assets if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value == 'GenericSchema')
    appearance = DB.AppearanceAssetElement.Create(doc, name, source)
    mat = doc.GetElement(DB.Material.Create(doc, name))
    mat.AppearanceAssetId = appearance.Id
    mat.Color = DB.Color(*color)
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    asset = scope.Start(appearance.Id)
    prop = asset.FindByName('generic_diffuse')
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.SetValueAsColor(DB.Color(*color))
    set_scalar(asset, 'generic_glossiness', gloss)
    set_scalar(asset, 'generic_reflectivity_at_0deg', refl)
    set_scalar(asset, 'generic_reflectivity_at_90deg', 0.2)
    scope.Commit(True)
    scope.Dispose()
    mat.MaterialClass = 'Plastic'
    return mat


def find_param(fm, name):
    for p in fm.Parameters:
        if p.Definition.Name == name:
            return p
    return None


try:
    app = __revit__.Application
    report['revit_version'] = app.VersionNumber
    assert app.VersionNumber == '2025'
    doc = app.NewFamilyDocument(TEMPLATE)
    docs.append(doc)
    stage('family created')

    tx = DB.Transaction(doc, 'Category')
    tx.Start()
    doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_LightingFixtures)
    tx.Commit()
    stage('category set')

    # a Lighting Fixtures document only gets a light source once the owner-family "Light Source" parameter is on (ERRORS in the sconce trial, row 2)
    tx = DB.Transaction(doc, 'Light source + type')
    tx.Start()
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE).Set(1)
    fm = doc.FamilyManager
    fm.NewType(TYPE_NAME)
    tx.Commit()
    stage('light source enabled, type created')

    tx = DB.Transaction(doc, 'Parameters, material, body')
    tx.Start()
    black = make_material(doc, app, 'Grazer - Matte Black', (22, 22, 24), 0.12, 0.04)
    mp = fm.AddParameter(MATERIAL_PARAM, DB.GroupTypeId.Materials, DB.SpecTypeId.Reference.Material, False)
    fm.Set(mp, black.Id)
    sub = doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory, 'Body')
    body = DB.FreeFormElement.Create(doc, box_solid(-BODY_L / 2.0, BODY_L / 2.0, -BODY_W / 2.0, BODY_W / 2.0, 0.0, BODY_H))
    body.Subcategory = sub
    fm.AssociateElementParameterToFamilyParameter(body.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), mp)
    report['body_id'] = body.Id.IntegerValue
    for bip, value in [(DB.BuiltInParameter.ALL_MODEL_DESCRIPTION, 'Hidden linear LED wall grazer, 4\'-10" line source, 10 deg spot, 2800 K, 2500 lm')]:
        try:
            fm.Set(fm.get_Parameter(bip), value)
        except Exception as ex:
            report.setdefault('identity_errors', []).append(str(bip) + ': ' + str(ex))
    tx.Commit()
    stage('material and body')

    # light shape and distribution first: they create the line-length / spot-angle type parameters
    tx = DB.Transaction(doc, 'Light shape and distribution')
    tx.Start()
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    lf.SetLightShapeStyle(DB.Lighting.LightShapeStyle.Line)
    lf.SetLightDistributionStyle(DB.Lighting.LightDistributionStyle.Spot)
    tx.Commit()
    stage('shape Line, distribution Spot')

    # position and aim: move to 1 3/4 in above the host face, centred on the body, then rotate 180 deg about the family X axis so it emits +Z
    tx = DB.Transaction(doc, 'Move and aim light source')
    tx.Start()
    ids = [e.Id for e in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource)]
    report['light_source_ids'] = [i.IntegerValue for i in ids]
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    t0 = lf.GetLightSourceTransform()
    report['light_before'] = {'origin_in': [t0.Origin.X * IN, t0.Origin.Y * IN, t0.Origin.Z * IN], 'basisX': [t0.BasisX.X, t0.BasisX.Y, t0.BasisX.Z], 'basisZ': [t0.BasisZ.X, t0.BasisZ.Y, t0.BasisZ.Z]}
    target = xyz(0.0, 0.0, SOURCE_Z)
    DB.ElementTransformUtils.MoveElement(doc, ids[0], target.Subtract(t0.Origin))
    tx.Commit()
    tx = DB.Transaction(doc, 'Aim light source')
    tx.Start()
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    o = lf.GetLightSourceTransform().Origin
    DB.ElementTransformUtils.RotateElement(doc, ids[0], DB.Line.CreateBound(o, o.Add(DB.XYZ.BasisX)), math.pi)
    tx.Commit()
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    t1 = lf.GetLightSourceTransform()
    report['light_after'] = {'origin_in': [t1.Origin.X * IN, t1.Origin.Y * IN, t1.Origin.Z * IN], 'basisX': [t1.BasisX.X, t1.BasisX.Y, t1.BasisX.Z], 'basisZ': [t1.BasisZ.X, t1.BasisZ.Y, t1.BasisZ.Z]}
    stage('light source moved and rotated')

    tx = DB.Transaction(doc, 'Light type values')
    tx.Start()
    try:
        lt = lf.GetLightType(0)
        lt.SetInitialIntensity(DB.Lighting.InitialFluxIntensity(FLUX_LM))
        lt.SetInitialColor(DB.Lighting.CustomInitialColor(CCT_K))
        lt.SetLossFactor(DB.Lighting.BasicLossFactor(LOSS))
        report['light_type_set'] = True
    except Exception:
        report['light_type_error'] = traceback.format_exc()
    tx.Commit()
    stage('light type values')

    # type parameters created by Line / Spot: length in feet, angles in radians
    fm = doc.FamilyManager
    report['all_parameters'] = [(p.Definition.Name, str(p.StorageType), p.IsInstance) for p in fm.Parameters]
    tx = DB.Transaction(doc, 'Light type parameters')
    tx.Start()
    wanted = [('Emit from Line Length', LINE_LENGTH / IN), ('Spot Beam Angle', math.radians(BEAM_DEG)),
              ('Spot Field Angle', math.radians(FIELD_DEG)), ('Tilt Angle', math.radians(TILT_DEG))]
    report['light_params_set'] = {}
    for name, value in wanted:
        p = find_param(fm, name)
        if p is None:
            report['light_params_set'][name] = 'MISSING'
            continue
        try:
            fm.Set(p, value)
            report['light_params_set'][name] = value
        except Exception as ex:
            report['light_params_set'][name] = 'ERROR: ' + str(ex)
    tx.Commit()
    stage('light type parameters')

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
