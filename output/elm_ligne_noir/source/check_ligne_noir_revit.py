# -*- coding: utf-8 -*-
"""ELM Vivid Ligne Noir 3x10 - native Revit 2025 check of the delivered maps.

Run through the pyRevit CLI:
    pyrevit run <this file> --revit=2025

Builds a disposable project, creates one Generic material with the delivered
colour and bump maps at the 36 x 40 in Sample Size, saves, reopens from disk and
re-reads every value from the saved file. Exports a frontal and a grazing-light
view of an 8 x 8 ft wall for a human to review.

Per output/elm_ligne_noir/HANDOFF_REVIT_CHECK.md:
  * every write goes through out_path(), which raises outside revit_check/;
  * the JSON report is written before the script re-raises - a clean pyRevit
    exit code is not evidence;
  * visual_verdict stays PENDING REVIEWER. The script never self-certifies.

Exported images are Realistic-display-style view exports, not raytraced
renders; Revit's renderer has no API entry point. They show the bound bitmaps,
their scale and, with the sun low, the bump response.
"""
import json
import math
import os
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

REPO_ROOT_CANDIDATES = [
    r'C:\Users\found\OneDrive\Documents\ChatGPT\3DModelWorkflow',
    r'C:\Users\mlux\Documents\GitHub\3D-Model-Workflow',
    r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow',
]

MATERIAL_NAME = 'ELM Vivid Ligne Noir - 3x10 Fluted Matte'
SCALE_IN = (36.0, 40.0)          # Sample Size, the full extent of the image
BUMP_AMOUNT = 0.4
GLOSSINESS = 0.15                # matte per the product page
DIM_TOL_IN = 0.0005
WALL_FT = 8.0                    # 8 x 8 ft review wall
GRAZE_ALTITUDE_DEG = 10.0
GRAZE_AZIMUTH_DEG = 115.0        # nearly parallel to the wall face, across the flutes


def repo_root():
    for candidate in REPO_ROOT_CANDIDATES:
        if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, 'AGENTS.md')):
            return candidate
    raise RuntimeError('No repository root found among: ' + ' | '.join(REPO_ROOT_CANDIDATES))


ROOT = repo_root()
PRODUCT_DIR = os.path.join(ROOT, 'output', 'elm_ligne_noir')
RUN_DIR = os.path.join(PRODUCT_DIR, 'revit_check')
_RUN_DIR_NORM = os.path.normpath(RUN_DIR)

COLOR_MAP = os.path.join(PRODUCT_DIR, 'textures', 'ELM_Ligne_Noir_3x10_Color.png')
BUMP_MAP = os.path.join(PRODUCT_DIR, 'textures', 'ELM_Ligne_Noir_3x10_Bump16.png')

REPORT = {
    'script': 'check_ligne_noir_revit.py',
    'product': 'ELM Surfaces Vivid Ligne Noir 3x10',
    'repo_root': ROOT,
    'run_dir': RUN_DIR,
    'specification': 'output/elm_ligne_noir/HANDOFF_REVIT_CHECK.md',
    'intended_maps': {'colour': COLOR_MAP, 'bump': BUMP_MAP},
    'sample_size_in': {'width': SCALE_IN[0], 'height': SCALE_IN[1]},
    'bump_amount': BUMP_AMOUNT,
    'transfer_project_standards_used': False,
    'render_note': ('Exports are Realistic display-style view exports. Revit has no API '
                    'entry point for a raytraced render, so no rendered image is claimed.'),
    'visual_verdict': 'PENDING REVIEWER',
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
    handle = open(out_path('validation.json'), 'w')
    try:
        handle.write(payload)
    finally:
        handle.close()


def element_name(element):
    """Element.Name does not bind through a statically typed Element reference on
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
    out['path_resolves'] = os.path.isfile(out['path'])
    return out


def read_scalar(asset, key):
    prop = asset.FindByName(key)
    return None if prop is None else prop.Value


def build_wall(doc):
    """8 x 8 ft wall centred on the origin line, face toward -Y."""
    level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
    wall_type = DB.FilteredElementCollector(doc).OfClass(DB.WallType).FirstElement()
    line = DB.Line.CreateBound(DB.XYZ(-WALL_FT / 2.0, 0, 0), DB.XYZ(WALL_FT / 2.0, 0, 0))
    wall = DB.Wall.Create(doc, line, wall_type.Id, level.Id, WALL_FT, 0.0, False, False)
    doc.Regenerate()
    return wall


def paint_face(doc, wall, material_id):
    options = DB.Options()
    options.ComputeReferences = True
    best, area, normal = None, 0.0, None
    for solid in wall.get_Geometry(options):
        if not isinstance(solid, DB.Solid):
            continue
        for face in solid.Faces:
            if face.Reference is None:
                continue
            direction = face.ComputeNormal(DB.UV(0.5, 0.5))
            # the face looking at the camera, i.e. pointing -Y
            if direction.Y < -0.9 and face.Area > area:
                best, area, normal = face, face.Area, direction
    if best is None:
        raise RuntimeError('No referenceable -Y wall face found to paint')

    doc.Paint(wall.Id, best, material_id)
    doc.Regenerate()
    painted = doc.GetPaintedMaterial(wall.Id, best)
    return {
        'wall_id': str(wall.Id.Value),
        'face_area_sqft': area,
        'face_normal': [normal.X, normal.Y, normal.Z],
        'is_painted': bool(doc.IsPainted(wall.Id, best)),
        'painted_material_id': str(painted.Value),
        'matches_material': painted == material_id,
    }


def set_param_by_name(element, names, value):
    """Set the first parameter matching one of `names`. Returns what it did."""
    for param in element.Parameters:
        label = param.Definition.Name
        if label in names and not param.IsReadOnly:
            param.Set(value)
            return {'parameter': label, 'set_to': value}
    return {'parameter': None, 'searched': list(names)}


def make_view(doc, name, half_width, graze, style):
    """3D view looking square at the painted face.

    A section box trims everything but the slab of wall being reviewed, so
    ZoomFitType.FitToPage frames the face instead of the whole model.
    `half_width` picks the framing: the full 8 ft wall, or a close-up.
    """
    view_family_type = next(
        v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
        if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(doc, view_family_type.Id)
    try:
        DB.Element.Name.SetValue(view, name)
    except Exception:
        view.get_Parameter(DB.BuiltInParameter.VIEW_NAME).Set(name)

    centre_z = WALL_FT / 2.0
    box = DB.BoundingBoxXYZ()
    box.Min = DB.XYZ(-half_width, -1.0, centre_z - half_width)
    box.Max = DB.XYZ(half_width, 1.0, centre_z + half_width)
    view.SetSectionBox(box)
    view.IsSectionBoxActive = True

    eye = DB.XYZ(0, -half_width * 3.0, centre_z)
    view.SetOrientation(DB.ViewOrientation3D(eye, DB.XYZ(0, 0, 1), DB.XYZ(0, 1, 0)))
    view.DisplayStyle = getattr(DB.DisplayStyle, style)
    view.DetailLevel = DB.ViewDetailLevel.Fine

    record = {'name': name, 'display_style': style, 'grazing': graze,
              'framed_width_ft': half_width * 2.0}
    # The sun-path compass is drawn at model scale and is pulled into the view
    # extents, so FitToPage zooms out to include it and the wall ends up tiny.
    # Keep it off; the sun DIRECTION below is a setting, not this graphic.
    record['sun_path'] = set_param_by_name(view, ('Sun Path',), 0)
    if graze:
        settings = view.SunAndShadowSettings
        # Revit 2025 exposes no SetFrameAzimuth; Altitude/Azimuth are radians.
        try:
            settings.SunAndShadowType = DB.SunAndShadowType.Lighting
            settings.Altitude = math.radians(GRAZE_ALTITUDE_DEG)
            settings.Azimuth = math.radians(GRAZE_AZIMUTH_DEG)
        except Exception as exc:
            record['sun_error'] = str(exc)
        record['sun_read_back'] = {
            'type': str(settings.SunAndShadowType),
            'altitude_deg': math.degrees(settings.Altitude),
            'azimuth_deg': math.degrees(settings.Azimuth),
        }
    return view, record


def export_views(doc, views):
    """Export one view at a time so a style Revit refuses cannot lose the rest.
    Revit names the files itself; report what actually landed on disk."""
    folder = out_path('exports')
    if not os.path.isdir(folder):
        os.makedirs(folder)
    results = []
    for view in views:
        before = set(os.listdir(folder))
        options = DB.ImageExportOptions()
        options.ZoomType = DB.ZoomFitType.FitToPage
        options.PixelSize = 1800
        options.FitDirection = DB.FitDirectionType.Horizontal
        options.HLRandWFViewsFileType = DB.ImageFileType.PNG
        options.ShadowViewsFileType = DB.ImageFileType.PNG
        options.ImageResolution = DB.ImageResolution.DPI_150
        options.ExportRange = DB.ExportRange.SetOfViews
        ids = List[DB.ElementId]()
        ids.Add(view.Id)
        options.SetViewsAndSheets(ids)
        options.FilePath = os.path.join(folder, 'ligne_noir')
        entry = {'view_id': str(view.Id.Value)}
        try:
            doc.ExportImage(options)
            entry['files'] = [{'file': name, 'bytes': os.path.getsize(os.path.join(folder, name))}
                              for name in sorted(set(os.listdir(folder)) - before)]
        except Exception as exc:
            entry['error'] = str(exc)
            entry['files'] = []
        results.append(entry)
    return results


def main():
    app = __revit__.Application
    REPORT['revit_version'] = app.VersionNumber

    for path in (COLOR_MAP, BUMP_MAP):
        if not os.path.isfile(path):
            raise RuntimeError('Map missing: ' + path)

    doc = app.NewProjectDocument(DB.UnitSystem.Imperial)
    tx = DB.Transaction(doc, 'Ligne Noir material check')
    tx.Start()

    asset_element = DB.AppearanceAssetElement.Create(doc, MATERIAL_NAME, generic_schema(app))
    material = doc.GetElement(DB.Material.Create(doc, MATERIAL_NAME))
    material.AppearanceAssetId = asset_element.Id
    material.Color = DB.Color(48, 41, 42)
    material.MaterialClass = 'Ceramic'
    material.Shininess = 10
    material.Smoothness = 20
    for key, value in [
            (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,
             'ELM Surfaces Vivid Ligne Noir 3x10 fluted matte ceramic wall tile, 1/16 in joint'),
            (DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, 'ELM Surfaces'),
            (DB.BuiltInParameter.ALL_MODEL_URL, 'https://www.elmsurfaces.com/product/ligne-noir')]:
        param = material.get_Parameter(key)
        if param and not param.IsReadOnly:
            param.Set(value)

    scope = DB.Visual.AppearanceAssetEditScope(doc)
    editable = scope.Start(asset_element.Id)
    for key, value in [('generic_glossiness', GLOSSINESS), ('generic_reflectivity_at_0deg', .04),
                       ('generic_reflectivity_at_90deg', 1.0), ('generic_transparency', 0.0),
                       ('generic_refraction_index', 1.5), ('generic_diffuse_image_fade', 1.0)]:
        prop = editable.FindByName(key)
        if prop.NumberOfConnectedProperties:
            prop.RemoveConnectedAsset()
        prop.Value = value
    connect_bitmap(editable, 'generic_diffuse', COLOR_MAP, SCALE_IN)
    connect_bitmap(editable, 'generic_bump_map', BUMP_MAP, SCALE_IN)
    bump_amount = editable.FindByName('generic_bump_amount')
    if bump_amount:
        bump_amount.Value = BUMP_AMOUNT
    scope.Commit(True)
    scope.Dispose()

    wall = build_wall(doc)
    REPORT['paint_test'] = paint_face(doc, wall, material.Id)

    views, view_records = [], []
    for name, half_width, graze, style in [
            ('Ligne Noir Wall Frontal', 4.0, False, 'Realistic'),
            ('Ligne Noir Wall Grazing', 4.0, True, 'Realistic'),
            ('Ligne Noir Closeup Grazing', 1.0, True, 'Realistic'),
            ('Ligne Noir Seam Closeup', 0.5, True, 'Realistic')]:
        view, record = make_view(doc, name, half_width, graze, style)
        views.append(view)
        view_records.append(record)
    REPORT['views'] = view_records
    tx.Commit()

    REPORT['exports'] = export_views(doc, views)
    checkpoint('exported')

    rvt = out_path('Ligne_Noir_Map_Check_R2025.rvt')
    # Overwrite is safe: out_path() has already proved the target is inside
    # revit_check/, which holds nothing but this disposable project.
    save_options = DB.SaveAsOptions()
    save_options.OverwriteExistingFile = True
    doc.SaveAs(rvt, save_options)
    doc.Close(False)

    # Everything below is re-read from the saved file.
    doc = app.OpenDocumentFile(rvt)
    saved = next(m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material)
                 if element_name(m) == MATERIAL_NAME)
    asset = doc.GetElement(saved.AppearanceAssetId).GetRenderingAsset()
    REPORT['reopened'] = True
    REPORT['rvt_path'] = rvt
    REPORT['rvt_bytes'] = os.path.getsize(rvt)
    REPORT['material_class'] = saved.MaterialClass
    REPORT['project_warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    REPORT['connected'] = {'colour': read_bitmap(asset, 'generic_diffuse'),
                           'bump': read_bitmap(asset, 'generic_bump_map')}
    REPORT['read_back'] = {'bump_amount': read_scalar(asset, 'generic_bump_amount'),
                           'glossiness': read_scalar(asset, 'generic_glossiness')}
    doc.Close(False)

    connected = REPORT['connected']

    def bound_to(entry, intended):
        if not entry:
            return False
        return (os.path.normcase(os.path.normpath(entry['path']))
                == os.path.normcase(os.path.normpath(intended)))

    def scale_ok(entry):
        return bool(entry
                    and abs(entry['scale_x_in'] - SCALE_IN[0]) <= DIM_TOL_IN
                    and abs(entry['scale_y_in'] - SCALE_IN[1]) <= DIM_TOL_IN)

    read_bump = REPORT['read_back']['bump_amount']
    REPORT['gates'] = {
        'material_saved_and_reopened': bool(REPORT.get('reopened')),
        'colour_bitmap_connected': bound_to(connected['colour'], COLOR_MAP),
        'bump_bitmap_connected': bound_to(connected['bump'], BUMP_MAP),
        'colour_path_resolves': bool(connected['colour'] and connected['colour']['path_resolves']),
        'bump_path_resolves': bool(connected['bump'] and connected['bump']['path_resolves']),
        'colour_scale_is_sample_size': scale_ok(connected['colour']),
        'bump_scale_is_sample_size': scale_ok(connected['bump']),
        'bump_amount_retained': read_bump is not None and abs(read_bump - BUMP_AMOUNT) <= 1e-6,
        'applied_to_native_face': bool(REPORT['paint_test']['matches_material']),
        'frontal_and_grazing_exported': sum(
            1 for e in REPORT['exports'] if e.get('files')) >= 3,
        'zero_project_warnings': not REPORT['project_warnings'],
    }
    REPORT['technical_pass'] = all(REPORT['gates'].values())
    REPORT['failed_gates'] = sorted(n for n, ok in REPORT['gates'].items() if not ok)
    checkpoint('complete')

    if REPORT['failed_gates']:
        raise RuntimeError('Gate failures: ' + json.dumps(REPORT['failed_gates']))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        REPORT['error'] = traceback.format_exc()
        try:
            checkpoint('failed')
        finally:
            raise
