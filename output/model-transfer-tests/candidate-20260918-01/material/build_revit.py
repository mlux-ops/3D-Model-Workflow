# -*- coding: utf-8 -*-
"""M01 Revit stage: build, save, reopen and natively apply both Adella materials.

Run inside Revit 2025 through the pyRevit CLI. Adapted from
scripts/build_adella_revit.py, whose ROOT and OUT constants pointed at a
different checkout and wrote the RVT into output/adella, a shipped deliverable.

What this script does NOT do, deliberately:
  * it does not use Transfer Project Standards or any swatch-copy workaround.
    The 2026-09-17 standing user instruction rejects that method outright.
  * it does not claim an ADSKLIB. Creating or updating a material library is a
    native Material Browser operation with no Revit API route, so the library
    gates are recorded as BLOCKED for a human step, not quietly skipped.

As on P01, the script re-raises after writing its JSON: a clean pyRevit exit
code is not evidence.
"""
import json
import os
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

RUN_ID = 'candidate-20260918-01'

REPO_ROOT_CANDIDATES = [
    r'C:\Users\mlux\Documents\GitHub\3D-Model-Workflow',
    r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow',
]

VARIANTS = [
    {'key': 'baseline',
     'label': 'A - reproduction, 1/16 in grout',
     'name': 'MSI Adella Viso White - 12x24 Satin - Stacked',
     'scale_in': (24.0625, 12.0625),
     'description': ('Adella Viso White 12x24 satin ceramic wall tile; approximate indented '
                     'relief; 1/16 inch light grout'),
     'rvt': 'Adella_Trial_Baseline_R2025.rvt'},
    {'key': 'variant',
     'label': 'B - controlled variation, 1/8 in grout',
     'name': 'MSI Adella Viso White - 12x24 Satin - Stacked - 1-8 Grout',
     'scale_in': (24.125, 12.125),
     'description': ('Adella Viso White 12x24 satin ceramic wall tile; approximate indented '
                     'relief; 1/8 inch light grout'),
     'rvt': 'Adella_Trial_OneEighthGrout_R2025.rvt'},
]

DIM_TOL_IN = 0.0005


def repo_root():
    for candidate in REPO_ROOT_CANDIDATES:
        if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, 'AGENTS.md')):
            return candidate
    raise RuntimeError('No repository root found among: ' + ' | '.join(REPO_ROOT_CANDIDATES))


ROOT = repo_root()
RUN_DIR = os.path.join(ROOT, 'output', 'model-transfer-tests', RUN_ID, 'material')
_RUN_DIR_NORM = os.path.normpath(RUN_DIR)

REPORT = {
    'run_id': RUN_ID,
    'script': 'build_revit.py',
    'repo_root': ROOT,
    'run_dir': RUN_DIR,
    'specification': 'docs/model-transfer-tests/MATERIAL.md',
    'transfer_project_standards_used': False,
    'transfer_note': ('Rejected by the 2026-09-17 standing user instruction. Materials are '
                      'delivered as ADSKLIB plus companion textures.'),
    'variants': {},
    'stage': 'started',
}


def out_path(*parts):
    target = os.path.normpath(os.path.join(RUN_DIR, *parts))
    if target != _RUN_DIR_NORM and not target.startswith(_RUN_DIR_NORM + os.sep):
        raise RuntimeError('Write path escapes the run directory: ' + target)
    parent = os.path.dirname(target)
    if not os.path.isdir(parent):
        os.makedirs(parent)
    return target


def checkpoint(stage):
    REPORT['stage'] = stage
    payload = json.dumps(REPORT, indent=2, default=str, sort_keys=True)
    with open(out_path('validation-revit.json'), 'w') as handle:
        handle.write(payload)


def element_name(element):
    """Element.Name will not bind through a statically typed Element reference on
    the pyRevit .NET Core engine; P01 hit this as MissingMemberException."""
    try:
        return DB.Element.Name.GetValue(element)
    except Exception:
        param = element.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
        return param.AsString() if param else None


def generic_schema(app):
    for asset in app.GetAssets(DB.Visual.AssetType.Appearance):
        schema = asset.FindByName('BaseSchema')
        if schema is not None and schema.Value == 'GenericSchema':
            return asset
    raise RuntimeError('GenericSchema appearance asset not found')


def connect_bitmap(editable, key, path, scale_in):
    prop = editable.FindByName(key)
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.AddConnectedAsset('UnifiedBitmap')
    bitmap = prop.GetSingleConnectedAsset()
    bitmap.FindByName('unifiedbitmap_Bitmap').Value = path
    for name, size in [('texture_RealWorldScaleX', scale_in[0]),
                       ('texture_RealWorldScaleY', scale_in[1])]:
        sub = bitmap.FindByName(name)
        sub.Value = DB.UnitUtils.ConvertFromInternalUnits(size / 12.0, sub.GetUnitTypeId())
    for name in ['texture_URepeat', 'texture_VRepeat']:
        bitmap.FindByName(name).Value = True


def read_bitmap(asset, key):
    prop = asset.FindByName(key)
    if not prop or not prop.NumberOfConnectedProperties:
        return None
    bitmap = prop.GetSingleConnectedAsset()
    out = {'path': bitmap.FindByName('unifiedbitmap_Bitmap').Value}
    for name, label in [('texture_RealWorldScaleX', 'scale_x_in'),
                        ('texture_RealWorldScaleY', 'scale_y_in')]:
        sub = bitmap.FindByName(name)
        out[label] = DB.UnitUtils.ConvertToInternalUnits(sub.Value, sub.GetUnitTypeId()) * 12.0
    return out


def paint_test_face(doc, material_id):
    """Apply the material to a real face and read it back."""
    level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
    wall_type = DB.FilteredElementCollector(doc).OfClass(DB.WallType).FirstElement()
    line = DB.Line.CreateBound(DB.XYZ(0, 0, 0), DB.XYZ(10, 0, 0))
    wall = DB.Wall.Create(doc, line, wall_type.Id, level.Id, 10.0, 0.0, False, False)
    doc.Regenerate()

    options = DB.Options()
    options.ComputeReferences = True
    largest, area = None, 0.0
    for solid in wall.get_Geometry(options):
        if not isinstance(solid, DB.Solid):
            continue
        for face in solid.Faces:
            if face.Area > area and face.Reference is not None:
                largest, area = face, face.Area
    if largest is None:
        raise RuntimeError('No referenceable wall face found to paint')

    doc.Paint(wall.Id, largest, material_id)
    doc.Regenerate()
    painted = doc.GetPaintedMaterial(wall.Id, largest)
    return {
        'wall_id': str(wall.Id.Value),
        'face_area_sqft': area,
        'is_painted': bool(doc.IsPainted(wall.Id, largest)),
        'painted_material_id': str(painted.Value),
        'matches_material': painted == material_id,
    }


def build(app, cfg):
    record = {'label': cfg['label'], 'material_name': cfg['name']}
    textures = os.path.join(RUN_DIR, cfg['key'], 'textures')
    colour_map = os.path.join(textures, 'Adella_BaseColor.png')
    bump_map = os.path.join(textures, 'Adella_Bump.png')
    for path in (colour_map, bump_map):
        if not os.path.isfile(path):
            raise RuntimeError('Map missing, run build_maps.py first: ' + path)
    record['intended_maps'] = {'colour': colour_map, 'bump': bump_map}

    doc = app.NewProjectDocument(DB.UnitSystem.Imperial)
    tx = DB.Transaction(doc, 'Adella material')
    tx.Start()

    asset_element = DB.AppearanceAssetElement.Create(doc, cfg['name'], generic_schema(app))
    material = doc.GetElement(DB.Material.Create(doc, cfg['name']))
    material.AppearanceAssetId = asset_element.Id
    material.Color = DB.Color(239, 240, 239)
    material.MaterialClass = 'Ceramic'
    material.Shininess = 35
    material.Smoothness = 50
    for key, value in [
            (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION, cfg['description']),
            (DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, 'MSI'),
            (DB.BuiltInParameter.ALL_MODEL_MODEL, 'NADEVISWHI1224-N'),
            (DB.BuiltInParameter.ALL_MODEL_URL,
             'https://www.msisurfaces.com/3d-large-format-wall-tile/adella-viso-white-12x24-satin/')]:
        param = material.get_Parameter(key)
        if param and not param.IsReadOnly:
            param.Set(value)

    scope = DB.Visual.AppearanceAssetEditScope(doc)
    editable = scope.Start(asset_element.Id)
    for key, value in [('generic_glossiness', .60), ('generic_reflectivity_at_0deg', .04),
                       ('generic_reflectivity_at_90deg', 1.0), ('generic_transparency', 0.0),
                       ('generic_refraction_index', 1.5), ('generic_diffuse_image_fade', 1.0)]:
        prop = editable.FindByName(key)
        if prop.NumberOfConnectedProperties:
            prop.RemoveConnectedAsset()
        prop.Value = value
    connect_bitmap(editable, 'generic_diffuse', colour_map, cfg['scale_in'])
    connect_bitmap(editable, 'generic_bump_map', bump_map, cfg['scale_in'])
    bump_amount = editable.FindByName('generic_bump_amount')
    if bump_amount:
        bump_amount.Value = .15
    scope.Commit(True)
    scope.Dispose()

    record['paint_test'] = paint_test_face(doc, material.Id)
    tx.Commit()

    path = out_path(cfg['rvt'])
    doc.SaveAs(path, DB.SaveAsOptions())
    doc.Close(False)

    # Reopen from disk; everything below is read from the saved file.
    doc = app.OpenDocumentFile(path)
    saved = next(m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material)
                 if element_name(m) == cfg['name'])
    asset = doc.GetElement(saved.AppearanceAssetId).GetRenderingAsset()
    record['reopened'] = True
    record['revit_version'] = app.VersionNumber
    record['rvt_path'] = path
    record['rvt_bytes'] = os.path.getsize(path)
    record['material_class'] = saved.MaterialClass
    record['project_warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    record['connected'] = {'colour': read_bitmap(asset, 'generic_diffuse'),
                           'bump': read_bitmap(asset, 'generic_bump_map')}
    doc.Close(False)

    connected = record['connected']
    scales_ok = True
    for slot in ('colour', 'bump'):
        entry = connected.get(slot)
        if not entry:
            scales_ok = False
            continue
        if (abs(entry['scale_x_in'] - cfg['scale_in'][0]) > DIM_TOL_IN
                or abs(entry['scale_y_in'] - cfg['scale_in'][1]) > DIM_TOL_IN):
            scales_ok = False

    # A silent fallback to the original production directory is the specific
    # failure MATERIAL.md asks about, so test for that directory by name.
    def is_this_variant(entry, intended):
        if not entry:
            return False
        actual = os.path.normcase(os.path.normpath(entry['path']))
        return actual == os.path.normcase(os.path.normpath(intended))

    record['gates'] = {
        'rvt_saved_and_reopened': bool(record.get('reopened')),
        'material_class_ceramic': record['material_class'] == 'Ceramic',
        'colour_map_is_this_variant': is_this_variant(connected['colour'], colour_map),
        'bump_map_is_this_variant': is_this_variant(connected['bump'], bump_map),
        'no_fallback_to_production_dir': all(
            entry is not None
            and os.path.join('output', 'adella') not in os.path.normpath(entry['path'])
            for entry in (connected['colour'], connected['bump'])),
        'physical_scales_match_repeat': scales_ok,
        'applied_to_native_face': bool(record['paint_test']['matches_material']),
        'zero_project_warnings': not record['project_warnings'],
    }
    record['revit_pass'] = all(record['gates'].values())
    return record


def main():
    app = __revit__.Application
    for cfg in VARIANTS:
        REPORT['variants'][cfg['key']] = build(app, cfg)
        checkpoint('built-' + cfg['key'])

    REPORT['adsklib'] = {
        'status': 'BLOCKED',
        'created_or_reused': 'neither - not attempted',
        'reason': ('Creating or updating an ADSKLIB is a native Material Browser operation '
                   'with no Revit API route. Transfer Project Standards, the only other API '
                   'path into a second project, is rejected by the 2026-09-17 standing user '
                   'instruction. Requires a human step in Revit.'),
        'second_project_import': 'BLOCKED - depends on the library above',
    }
    failed = dict((k, sorted(n for n, ok in v['gates'].items() if not ok))
                  for k, v in REPORT['variants'].items())
    REPORT['failed_gates'] = failed
    REPORT['revit_pass'] = all(v['revit_pass'] for v in REPORT['variants'].values())
    checkpoint('complete')

    if any(failed.values()):
        raise RuntimeError('Gate failures: ' + json.dumps(failed))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        REPORT['error'] = traceback.format_exc()
        try:
            checkpoint('failed')
        finally:
            raise
