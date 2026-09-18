import json
import os
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB


ROOT = r'C:\Users\mlux\Documents\GitHub\3D-Model-Workflow'
OUT = os.path.join(ROOT, 'output', 'daltile_remedy_hydro')
TEX = os.path.join(OUT, 'textures')
REPORT = os.path.join(OUT, 'revit_validation.json')
TEMP_RVT = os.path.join(OUT, '_validation_Daltile_Remedy_Hydro_R2025.rvt')
MATERIAL_NAME = 'Daltile Remedy Hydro - 2x10 Fluted Glossy'
COLOR = os.path.join(TEX, 'Daltile_Remedy_Hydro_Fluted_BaseColor.png')
BUMP = os.path.join(TEX, 'Daltile_Remedy_Hydro_Fluted_Bump16.png')
SCALE_X_IN = 201.25
SCALE_Y_IN = 20.625


def write_report(report):
    with open(REPORT, 'w') as f:
        json.dump(report, f, indent=2)


def scalar_inches(asset, key):
    p = asset.FindByName(key)
    if p is None:
        return None
    return DB.UnitUtils.ConvertToInternalUnits(p.Value, p.GetUnitTypeId()) * 12.0


report = {'success': False, 'material': MATERIAL_NAME, 'temp_project': TEMP_RVT}
doc = None
tx = None
try:
    app = __revit__.Application
    report['revit_version'] = app.VersionNumber
    if app.VersionNumber != '2025':
        raise RuntimeError('expected Revit 2025, got %s' % app.VersionNumber)
    for p in (COLOR, BUMP):
        if not os.path.isfile(p):
            raise RuntimeError('missing texture: %s' % p)

    doc = app.NewProjectDocument(DB.UnitSystem.Imperial)
    tx = DB.Transaction(doc, 'Daltile Remedy Hydro validation material')
    tx.Start()
    source = next(a for a in app.GetAssets(DB.Visual.AssetType.Appearance)
                  if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value == 'GenericSchema')
    ae = DB.AppearanceAssetElement.Create(doc, MATERIAL_NAME, source)
    mat = doc.GetElement(DB.Material.Create(doc, MATERIAL_NAME))
    mat.AppearanceAssetId = ae.Id
    mat.Color = DB.Color(80, 101, 97)
    mat.MaterialClass = 'Ceramic'
    mat.Shininess = 85
    mat.Smoothness = 90
    p = mat.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER)
    if p and not p.IsReadOnly:
        p.Set('Daltile')
    p = mat.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MODEL)
    if p and not p.IsReadOnly:
        p.Set('RD22RCT210FLUGL')
    p = mat.get_Parameter(DB.BuiltInParameter.ALL_MODEL_URL)
    if p and not p.IsReadOnly:
        p.Set('https://www.daltile.com/products/wall/remedy/hydro')

    scope = DB.Visual.AppearanceAssetEditScope(doc)
    asset = scope.Start(ae.Id)

    def set_bitmap(key, filename):
        prop = asset.FindByName(key)
        if prop.NumberOfConnectedProperties:
            prop.RemoveConnectedAsset()
        prop.AddConnectedAsset('UnifiedBitmap')
        bmp = prop.GetSingleConnectedAsset()
        bmp.FindByName('unifiedbitmap_Bitmap').Value = filename
        for scale_key, inches in [('texture_RealWorldScaleX', SCALE_X_IN), ('texture_RealWorldScaleY', SCALE_Y_IN)]:
            sp = bmp.FindByName(scale_key)
            sp.Value = DB.UnitUtils.ConvertFromInternalUnits(inches / 12.0, sp.GetUnitTypeId())
        bmp.FindByName('texture_URepeat').Value = True
        bmp.FindByName('texture_VRepeat').Value = True

    set_bitmap('generic_diffuse', COLOR)
    set_bitmap('generic_bump_map', BUMP)
    bump_amount = asset.FindByName('generic_bump_amount')
    if bump_amount:
        bump_amount.Value = 0.06
    gloss = asset.FindByName('generic_glossiness')
    if gloss:
        gloss.Value = 0.82
    scope.Commit(True)
    scope.Dispose()
    tx.Commit()
    tx = None
    if os.path.exists(TEMP_RVT):
        os.remove(TEMP_RVT)
    save_opts = DB.SaveAsOptions()
    save_opts.OverwriteExistingFile = True
    doc.SaveAs(TEMP_RVT, save_opts)
    doc.Close(False)
    doc = None

    doc = app.OpenDocumentFile(TEMP_RVT)
    mats = [x for x in DB.FilteredElementCollector(doc).OfClass(DB.Material) if x.Name == MATERIAL_NAME]
    if len(mats) != 1:
        raise RuntimeError('material count after reopen: %d' % len(mats))
    mat = mats[0]
    asset = doc.GetElement(mat.AppearanceAssetId).GetRenderingAsset()
    maps = {}
    scales = {}
    for key in ('generic_diffuse', 'generic_bump_map'):
        prop = asset.FindByName(key)
        if prop is None or prop.NumberOfConnectedProperties != 1:
            raise RuntimeError('%s has no single bitmap connection after reopen' % key)
        bmp = prop.GetSingleConnectedAsset()
        maps[key] = bmp.FindByName('unifiedbitmap_Bitmap').Value
        scales[key] = [scalar_inches(bmp, 'texture_RealWorldScaleX'), scalar_inches(bmp, 'texture_RealWorldScaleY')]

    warnings = len(list(doc.GetWarnings()))
    report.update({
        'warnings': warnings,
        'maps': maps,
        'scales_in': scales,
        'map_files_exist': {k: os.path.isfile(v) for k, v in maps.items()},
        'material_name_reopen': mat.Name,
    })
    scale_pass = all(abs(v[0] - SCALE_X_IN) < 1e-4 and abs(v[1] - SCALE_Y_IN) < 1e-4 for v in scales.values())
    path_pass = os.path.normcase(maps['generic_diffuse']) == os.path.normcase(COLOR) and os.path.normcase(maps['generic_bump_map']) == os.path.normcase(BUMP)
    report['success'] = bool(warnings == 0 and scale_pass and path_pass and all(report['map_files_exist'].values()))
    doc.Close(False)
    doc = None
except Exception:
    report['error'] = traceback.format_exc()
    try:
        if tx is not None:
            tx.RollBack()
    except Exception:
        pass
    try:
        if doc is not None:
            doc.Close(False)
    except Exception:
        pass
finally:
    write_report(report)
