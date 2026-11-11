# -*- coding: utf-8 -*-
"""Clear reeded glass: build the Revit 2025 materials in a DISPOSABLE project,
save, reopen, read every setting back, and export Realistic test views.

Run inside Revit 2025 through the pyRevit CLI (IronPython 2.7):
  pyrevit run <this file> --revit=2025 --purge

Appearance type chosen from source/revit_probe.json: PrismTransparentSchema
(Revit UI: "Transparent"). It is the only candidate that has, together, an index
of refraction, a relief slot (surface_normal) that accepts a BumpMap asset whose
bumpmap_Type switches height / normal, and an image-capable colour slot
(surface_albedo) for the repo's bound-colour-bitmap rule.

What this script does NOT do:
  * no Transfer Project Standards, no swatch copy;
  * no ADSKLIB. A material library is a Material Browser operation with no Revit
    API route; that gate is recorded as PENDING, not skipped;
  * no ray-traced render (no API route). Realistic viewport exports only.

It writes its JSON first and re-raises: an exit code is not evidence.
"""
import json
import math
import os
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

# ---------------------------------------------------------------- job constants
PITCH_IN = 0.5
REEDS_ACROSS = 8
SAMPLE_IN = PITCH_IN * REEDS_ACROSS          # 4.0 in square
REED_DEPTH_MM = 1.5
GLASS_THICKNESS_MM = 6.0
IOR = 1.52
TRANSMISSION_COLOR = (0.98, 0.98, 0.98)      # colour reached after TRANSMISSION_DISTANCE_MM
TRANSMISSION_DISTANCE_MM = 6.0
SURFACE_ROUGHNESS = 0.0
GRAPHICS_TRANSPARENCY = 80                   # Graphics tab, percent
GRAPHICS_COLOR = (225, 236, 238)             # Graphics tab shading colour
BASE_NAME = 'Clear Reeded Glass - 0.5in Vertical Reed'
TEX_PREFIX = 'Clear_Reeded_Glass_0p5in'

RUN_DIR_CANDIDATES = [
    'E:/Claude/3D-Model-Workflow/.claude/worktrees/revit-clear-reeded-glass-4376d3/output/clear_reeded_glass',
    'E:/Claude/3D-Model-Workflow/output/clear_reeded_glass',
]
RUN_DIR = None
for _candidate in RUN_DIR_CANDIDATES:
    if os.path.isfile(os.path.join(_candidate, 'source', 'build_maps.py')):
        RUN_DIR = os.path.normpath(_candidate)
        break
if RUN_DIR is None:
    raise RuntimeError('Run directory not found among: ' + ' | '.join(RUN_DIR_CANDIDATES))

TEX = {
    'color': os.path.join(RUN_DIR, 'textures', TEX_PREFIX + '_Color.png'),
    'bump': os.path.join(RUN_DIR, 'textures', TEX_PREFIX + '_Bump_16bit.png'),
    'normal': os.path.join(RUN_DIR, 'textures', TEX_PREFIX + '_Normal_16bit.png'),
}

# relief: None | 'height' | 'normal';  albedo_bitmap: bound colour bitmap or not
VARIANTS = [
    {'key': 'height', 'name': BASE_NAME + ' (PBR Height Map)', 'relief': 'height', 'albedo_bitmap': True,
     'deliverable': True},
    {'key': 'normal', 'name': BASE_NAME + ' (PBR Normal Map)', 'relief': 'normal', 'albedo_bitmap': True,
     'deliverable': True},
    {'key': 'flat_bitmap', 'name': 'QA Clear Glass - colour bitmap only', 'relief': None,
     'albedo_bitmap': True, 'deliverable': False},
    {'key': 'flat_bare', 'name': 'QA Clear Glass - bare', 'relief': None, 'albedo_bitmap': False,
     'deliverable': False},
    # Comparison only: do the legacy appearance types show relief in the Realistic viewport?
    {'key': 'generic_height', 'name': 'QA Generic Glass - height', 'relief': 'height',
     'albedo_bitmap': True, 'deliverable': False, 'schema': 'generic'},
    {'key': 'generic_normal', 'name': 'QA Generic Glass - normal', 'relief': 'normal',
     'albedo_bitmap': True, 'deliverable': False, 'schema': 'generic'},
    {'key': 'solidglass_height', 'name': 'QA Solid Glass - height, preset clear colour', 'relief': 'height',
     'albedo_bitmap': False, 'deliverable': False, 'schema': 'solidglass'},
    # Default deliverable candidate: Solid Glass shows the reeds in the Realistic viewport.
    {'key': 'solidglass_bitmap', 'name': BASE_NAME, 'relief': 'height',
     'albedo_bitmap': True, 'deliverable': True, 'schema': 'solidglass'},
]
PANE_W_FT, PANE_H_FT, GROUP_SPACING_FT = 2.0, 1.5, 12.0

REPORT = {
    'script': 'build_revit.py',
    'run_dir': RUN_DIR,
    'appearance_schema': 'PrismTransparentSchema',
    'transfer_project_standards_used': False,
    'variants': {},
    'exports': {},
    'notes': [],
    'stage': 'started',
}


def out_path(*parts):
    target = os.path.normpath(os.path.join(RUN_DIR, *parts))
    if not target.startswith(RUN_DIR + os.sep):
        raise RuntimeError('Write path escapes the run directory: ' + target)
    parent = os.path.dirname(target)
    if not os.path.isdir(parent):
        os.makedirs(parent)
    return target


def checkpoint(stage):
    REPORT['stage'] = stage
    with open(out_path('source', 'revit_validation.json'), 'w') as handle:
        handle.write(json.dumps(REPORT, indent=2, default=str, sort_keys=True))


def element_name(element):
    try:
        return DB.Element.Name.GetValue(element)
    except Exception:
        param = element.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
        return param.AsString() if param else None


def library_asset(app, schema_name):
    for asset in app.GetAssets(DB.Visual.AssetType.Appearance):
        schema = asset.FindByName('BaseSchema')
        if schema is not None and schema.Value == schema_name:
            return asset
    raise RuntimeError(schema_name + ' appearance asset not found')


def set_doubles(prop, values):
    data = List[float]()
    for v in values:
        data.Add(float(v))
    prop.SetValueAsDoubles(data)


def set_distance_mm(prop, mm):
    prop.Value = DB.UnitUtils.ConvertFromInternalUnits(mm / 304.8, prop.GetUnitTypeId())


def get_distance_mm(prop):
    return DB.UnitUtils.ConvertToInternalUnits(prop.Value, prop.GetUnitTypeId()) * 304.8


def set_texture_size(texture):
    for name in ('texture_RealWorldScaleX', 'texture_RealWorldScaleY'):
        sub = texture.FindByName(name)
        sub.Value = DB.UnitUtils.ConvertFromInternalUnits(SAMPLE_IN / 12.0, sub.GetUnitTypeId())
    for name in ('texture_URepeat', 'texture_VRepeat'):
        texture.FindByName(name).Value = True
    for name in ('texture_RealWorldOffsetX', 'texture_RealWorldOffsetY'):
        sub = texture.FindByName(name)
        sub.Value = 0.0
    texture.FindByName('texture_WAngle').Value = 0.0


def clear_connection(prop):
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()


def build_legacy_appearance(doc, app, cfg):
    """QA comparison assets. Every assignment is recorded, because several enum values
    here are untested guesses and must not be mistaken for verified settings."""
    log = {}
    generic = cfg['schema'] == 'generic'
    element = DB.AppearanceAssetElement.Create(
        doc, cfg['name'], library_asset(app, 'GenericSchema' if generic else 'SolidGlassSchema'))
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    editable = scope.Start(element.Id)

    def assign(name, value):
        try:
            prop = editable.FindByName(name)
            clear_connection(prop)
            prop.Value = value
            log[name] = prop.Value
        except Exception as exc:
            log[name] = 'ERR ' + str(exc).splitlines()[0][:140]

    def connect(name, schema, bitmap_key, path, extra=None):
        try:
            prop = editable.FindByName(name)
            clear_connection(prop)
            prop.AddConnectedAsset(schema)
            texture = prop.GetSingleConnectedAsset()
            texture.FindByName(bitmap_key).Value = path
            set_texture_size(texture)
            if extra:
                extra(texture)
            log[name] = schema + ' <- ' + os.path.basename(path)
        except Exception as exc:
            log[name] = 'ERR ' + str(exc).splitlines()[0][:140]

    def as_normal(texture):
        texture.FindByName('bumpmap_Type').Value = 1
        texture.FindByName('bumpmap_NormalScale').Value = 1.0

    if generic:
        assign('generic_transparency', 0.92)
        assign('generic_refraction_index', IOR)
        assign('generic_glossiness', 1.0)
        assign('generic_reflectivity_at_0deg', 0.04)
        assign('generic_reflectivity_at_90deg', 1.0)
        connect('generic_diffuse', 'UnifiedBitmap', 'unifiedbitmap_Bitmap', TEX['color'])
        if cfg['relief'] == 'height':
            connect('generic_bump_map', 'UnifiedBitmap', 'unifiedbitmap_Bitmap', TEX['bump'])
        else:
            connect('generic_bump_map', 'BumpMap', 'bumpmap_Bitmap', TEX['normal'], as_normal)
        assign('generic_bump_amount', 1.0)
    else:
        if cfg['albedo_bitmap']:
            # 6 is an untested guess for the "Custom" colour preset; the readback records
            # what Revit actually kept.
            assign('solidglass_transmittance', 6)
            try:
                # neutral fallback colour under the bitmap, instead of the preset green
                set_doubles(editable.FindByName('solidglass_transmittance_custom_color'),
                            list(TRANSMISSION_COLOR) + [1.0])
            except Exception as exc:
                log['custom_color_base'] = 'ERR ' + str(exc).splitlines()[0][:140]
            connect('solidglass_transmittance_custom_color', 'UnifiedBitmap', 'unifiedbitmap_Bitmap',
                    TEX['color'])
        else:
            assign('solidglass_transmittance', 0)
        assign('solidglass_refr_ior', IOR)
        assign('solidglass_reflectance', 0.05)
        # solidglass_glossiness is left at the library default (0.0, the value on Autodesk's
        # own polished clear glass). The Revit UI labels this slider Roughness, so raising
        # it risks a frosted render; an earlier QA run that set 1.0 was an untested guess.
        assign('solidglass_glossiness', 0.0)
        assign('solidglass_bump_enable', 3)
        connect('solidglass_bump_map', 'UnifiedBitmap', 'unifiedbitmap_Bitmap', TEX['bump'])
        assign('solidglass_bump_amount', 1.0)
    scope.Commit(True)
    scope.Dispose()
    REPORT.setdefault('legacy_comparison_assignments', {})[cfg['key']] = log
    return element


def build_appearance(doc, app, cfg):
    if cfg.get('schema'):
        return build_legacy_appearance(doc, app, cfg)
    element = DB.AppearanceAssetElement.Create(doc, cfg['name'], library_asset(app, 'PrismTransparentSchema'))
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    editable = scope.Start(element.Id)

    set_doubles(editable.FindByName('transparent_color'), list(TRANSMISSION_COLOR) + [1.0])
    set_distance_mm(editable.FindByName('transparent_distance'), TRANSMISSION_DISTANCE_MM)
    editable.FindByName('transparent_ior').Value = IOR

    rough = editable.FindByName('surface_roughness')
    clear_connection(rough)
    rough.Value = SURFACE_ROUGHNESS
    editable.FindByName('surface_anisotropy').Value = 0.0
    editable.FindByName('surface_rotation').Value = 0.0
    clear_connection(editable.FindByName('surface_cutout'))

    albedo = editable.FindByName('surface_albedo')
    clear_connection(albedo)
    set_doubles(albedo, [1.0, 1.0, 1.0, 1.0])
    if cfg['albedo_bitmap']:
        albedo.AddConnectedAsset('UnifiedBitmap')
        bitmap = albedo.GetSingleConnectedAsset()
        bitmap.FindByName('unifiedbitmap_Bitmap').Value = TEX['color']
        set_texture_size(bitmap)

    normal = editable.FindByName('surface_normal')
    clear_connection(normal)
    if cfg['relief']:
        normal.AddConnectedAsset('BumpMap')
        bump = normal.GetSingleConnectedAsset()
        if cfg['relief'] == 'height':
            bump.FindByName('bumpmap_Bitmap').Value = TEX['bump']
            bump.FindByName('bumpmap_Type').Value = 0
            set_distance_mm(bump.FindByName('bumpmap_Depth'), REED_DEPTH_MM)
        else:
            bump.FindByName('bumpmap_Bitmap').Value = TEX['normal']
            bump.FindByName('bumpmap_Type').Value = 1
            bump.FindByName('bumpmap_NormalScale').Value = 1.0
        set_texture_size(bump)

    scope.Commit(True)
    scope.Dispose()
    return element


def build_material(doc, app, cfg):
    appearance = build_appearance(doc, app, cfg)
    material = doc.GetElement(DB.Material.Create(doc, cfg['name']))
    material.AppearanceAssetId = appearance.Id
    material.MaterialClass = 'Glass'
    material.Color = DB.Color(*GRAPHICS_COLOR)
    material.Transparency = GRAPHICS_TRANSPARENCY
    material.Shininess = 128
    material.Smoothness = 100
    material.UseRenderAppearanceForShading = False
    for key, value in [
            (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,
             'Clear reeded glass, vertical convex reeds, 1/2 in pitch, about 1.5 mm relief, '
             'nominal 1/4 in pane. Procedural maps; dimensions are design defaults, not '
             'manufacturer data.'),
            (DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS,
             'Texture Sample Size 4 in x 4 in (8 reeds). Relief: ' + str(cfg['relief']))]:
        param = material.get_Parameter(key)
        if param and not param.IsReadOnly:
            param.Set(value)
    return material


def flat_color_material(doc, app, name, rgb, texture_probe=False):
    element = DB.AppearanceAssetElement.Create(doc, name, library_asset(app, 'GenericSchema'))
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    editable = scope.Start(element.Id)
    diffuse = editable.FindByName('generic_diffuse')
    clear_connection(diffuse)
    set_doubles(diffuse, [rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0, 1.0])
    if texture_probe:
        # Diagnostic only: an opaque backdrop carrying the striped bump PNG as its colour
        # image. If these stripes are absent from an export, the export draws no textures
        # at all and says nothing about the glass relief.
        diffuse.AddConnectedAsset('UnifiedBitmap')
        bitmap = diffuse.GetSingleConnectedAsset()
        bitmap.FindByName('unifiedbitmap_Bitmap').Value = TEX['bump']
        set_texture_size(bitmap)
    scope.Commit(True)
    scope.Dispose()
    material = doc.GetElement(DB.Material.Create(doc, name))
    material.AppearanceAssetId = element.Id
    material.Color = DB.Color(*rgb)
    return material


def wall_type_for(doc, base_type, name, material_id, width_ft):
    new_type = base_type.Duplicate(name)
    structure = DB.CompoundStructure.CreateSingleLayerCompoundStructure(
        DB.MaterialFunctionAssignment.Structure, width_ft, material_id)
    new_type.SetCompoundStructure(structure)
    return new_type


def make_wall(doc, wall_type, level, x0, x1, y, height, base_offset=0.0):
    line = DB.Line.CreateBound(DB.XYZ(x0, y, 0), DB.XYZ(x1, y, 0))
    return DB.Wall.Create(doc, line, wall_type.Id, level.Id, height, base_offset, False, False)


def read_texture(texture, bitmap_key):
    out = {'schema': texture.FindByName('BaseSchema').Value,
           'path': texture.FindByName(bitmap_key).Value}
    for name, label in [('texture_RealWorldScaleX', 'size_x_in'), ('texture_RealWorldScaleY', 'size_y_in')]:
        sub = texture.FindByName(name)
        out[label] = DB.UnitUtils.ConvertToInternalUnits(sub.Value, sub.GetUnitTypeId()) * 12.0
    out['u_repeat'] = texture.FindByName('texture_URepeat').Value
    out['v_repeat'] = texture.FindByName('texture_VRepeat').Value
    out['rotation_deg'] = texture.FindByName('texture_WAngle').Value
    return out


def read_back(doc, cfg):
    material = None
    for candidate in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        if element_name(candidate) == cfg['name']:
            material = candidate
            break
    if material is None:
        raise RuntimeError('Material missing after reopen: ' + cfg['name'])
    asset = doc.GetElement(material.AppearanceAssetId).GetRenderingAsset()
    record = {
        'material_name': cfg['name'],
        'deliverable': cfg['deliverable'],
        'material_class': material.MaterialClass,
        'graphics_transparency_percent': material.Transparency,
        'graphics_color_rgb': [material.Color.Red, material.Color.Green, material.Color.Blue],
        'use_render_appearance_for_shading': material.UseRenderAppearanceForShading,
        'schema': asset.FindByName('BaseSchema').Value,
        'transparent_ior': asset.FindByName('transparent_ior').Value,
        'transparent_color': [round(v, 5) for v in asset.FindByName('transparent_color').GetValueAsDoubles()],
        'transparent_distance_mm': round(get_distance_mm(asset.FindByName('transparent_distance')), 4),
        'surface_roughness': asset.FindByName('surface_roughness').Value,
        'surface_albedo': [round(v, 5) for v in asset.FindByName('surface_albedo').GetValueAsDoubles()],
        'color_bitmap': None,
        'relief': None,
    }
    albedo = asset.FindByName('surface_albedo')
    if albedo.NumberOfConnectedProperties:
        record['color_bitmap'] = read_texture(albedo.GetSingleConnectedAsset(), 'unifiedbitmap_Bitmap')
    normal = asset.FindByName('surface_normal')
    if normal.NumberOfConnectedProperties:
        bump = normal.GetSingleConnectedAsset()
        relief = read_texture(bump, 'bumpmap_Bitmap')
        relief['bumpmap_Type'] = bump.FindByName('bumpmap_Type').Value
        relief['bumpmap_Depth_mm'] = round(get_distance_mm(bump.FindByName('bumpmap_Depth')), 4)
        relief['bumpmap_NormalScale'] = bump.FindByName('bumpmap_NormalScale').Value
        record['relief'] = relief

    def same(path_a, path_b):
        return os.path.normcase(os.path.normpath(path_a)) == os.path.normcase(os.path.normpath(path_b))

    def size_ok(entry):
        return (abs(entry['size_x_in'] - SAMPLE_IN) < 0.0005 and abs(entry['size_y_in'] - SAMPLE_IN) < 0.0005)

    gates = {
        'schema_is_transparent': record['schema'] == 'PrismTransparentSchema',
        'class_glass': record['material_class'] == 'Glass',
        'ior': abs(record['transparent_ior'] - IOR) < 1e-6,
        'roughness_zero': abs(record['surface_roughness'] - SURFACE_ROUGHNESS) < 1e-6,
        'graphics_transparency': record['graphics_transparency_percent'] == GRAPHICS_TRANSPARENCY,
        'transmission_distance': abs(record['transparent_distance_mm'] - TRANSMISSION_DISTANCE_MM) < 0.001,
    }
    if cfg['albedo_bitmap']:
        entry = record['color_bitmap']
        gates['color_bitmap_bound'] = bool(entry) and same(entry['path'], TEX['color'])
        gates['color_bitmap_file_exists'] = bool(entry) and os.path.isfile(entry['path'])
        gates['color_bitmap_sample_size'] = bool(entry) and size_ok(entry)
    else:
        gates['no_color_bitmap'] = record['color_bitmap'] is None
    if cfg['relief']:
        entry = record['relief']
        want = TEX['bump'] if cfg['relief'] == 'height' else TEX['normal']
        gates['relief_bound'] = bool(entry) and same(entry['path'], want)
        gates['relief_file_exists'] = bool(entry) and os.path.isfile(entry['path'])
        gates['relief_sample_size'] = bool(entry) and size_ok(entry)
        gates['relief_type'] = bool(entry) and entry['bumpmap_Type'] == (0 if cfg['relief'] == 'height' else 1)
        if cfg['relief'] == 'height':
            gates['relief_depth_mm'] = bool(entry) and abs(entry['bumpmap_Depth_mm'] - REED_DEPTH_MM) < 0.001
    else:
        gates['no_relief'] = record['relief'] is None
    record['gates'] = gates
    record['pass'] = all(gates.values())
    return record


def read_back_legacy(doc, cfg):
    material = None
    for candidate in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        if element_name(candidate) == cfg['name']:
            material = candidate
            break
    if material is None:
        raise RuntimeError('Material missing after reopen: ' + cfg['name'])
    asset = doc.GetElement(material.AppearanceAssetId).GetRenderingAsset()
    record = {'material_name': cfg['name'], 'deliverable': cfg['deliverable'],
              'schema': asset.FindByName('BaseSchema').Value,
              'material_class': material.MaterialClass,
              'graphics_transparency_percent': material.Transparency,
              'values': {}, 'textures': {}}
    for i in range(asset.Size):
        prop = asset.Get(i)
        name = prop.Name
        if not (name.startswith('solidglass_') or name.startswith('generic_')):
            continue
        try:
            if isinstance(prop, (DB.Visual.AssetPropertyDouble, DB.Visual.AssetPropertyInteger,
                                 DB.Visual.AssetPropertyBoolean)):
                record['values'][name] = prop.Value
            elif isinstance(prop, DB.Visual.AssetPropertyDoubleArray4d):
                record['values'][name] = [round(v, 5) for v in prop.GetValueAsDoubles()]
            elif isinstance(prop, DB.Visual.AssetPropertyDistance):
                record['values'][name + '_mm'] = round(get_distance_mm(prop), 4)
        except Exception as exc:
            record['values'][name] = 'ERR ' + str(exc).splitlines()[0][:100]
        if prop.NumberOfConnectedProperties:
            texture = prop.GetSingleConnectedAsset()
            key = 'bumpmap_Bitmap' if texture.FindByName('bumpmap_Bitmap') is not None else 'unifiedbitmap_Bitmap'
            entry = read_texture(texture, key)
            entry['file_exists'] = os.path.isfile(entry['path'])
            record['textures'][name] = entry
    return record


def set_light(doc, views, azimuth_deg, altitude_deg, label):
    """Try to steer the view lighting; record exactly what happened."""
    log = []
    for view in views:
        entry = {'view': view.Name}
        try:
            settings = view.SunAndShadowSettings
            entry['settings_id'] = str(settings.Id.Value)
            settings.SunAndShadowType = DB.SunAndShadowType.Lighting
            settings.RelativeToView = True
            settings.Azimuth = math.radians(azimuth_deg)
            settings.Altitude = math.radians(altitude_deg)
            entry['azimuth_deg'] = round(math.degrees(settings.Azimuth), 3)
            entry['altitude_deg'] = round(math.degrees(settings.Altitude), 3)
            entry['relative_to_view'] = settings.RelativeToView
        except Exception as exc:
            entry['error'] = str(exc).splitlines()[0][:200]
        log.append(entry)
    REPORT['notes'].append({'light_' + label: log})


def export_views(doc, views, prefix):
    ids = List[DB.ElementId]()
    for view in views:
        ids.Add(view.Id)
    options = DB.ImageExportOptions()
    options.ExportRange = DB.ExportRange.SetOfViews
    options.SetViewsAndSheets(ids)
    options.FilePath = out_path('qa', prefix)
    options.HLRandWFViewsFileType = DB.ImageFileType.PNG
    options.ShadowViewsFileType = DB.ImageFileType.PNG
    options.ImageResolution = DB.ImageResolution.DPI_150
    options.ZoomType = DB.ZoomFitType.FitToPage
    options.FitDirection = DB.FitDirectionType.Horizontal
    options.PixelSize = 1600
    doc.ExportImage(options)


def main():
    app = __revit__.Application
    REPORT['revit_version'] = app.VersionNumber
    REPORT['revit_build'] = app.VersionBuild
    for key, path in TEX.items():
        if not os.path.isfile(path):
            raise RuntimeError('Map missing, run build_maps.py first: ' + path)
    REPORT['textures'] = TEX

    doc = app.NewProjectDocument(DB.UnitSystem.Imperial)
    tx = DB.Transaction(doc, 'Clear reeded glass QA')
    tx.Start()

    level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
    base_type = None
    for wall_type in DB.FilteredElementCollector(doc).OfClass(DB.WallType):
        if wall_type.Kind == DB.WallKind.Basic:
            base_type = wall_type
            break
    if base_type is None:
        raise RuntimeError('No basic wall type in the default project')

    navy = flat_color_material(doc, app, 'QA Backdrop Navy', (20, 40, 110))
    orange = flat_color_material(doc, app, 'QA Backdrop Orange', (235, 120, 20))
    white = flat_color_material(doc, app, 'QA Backdrop White Striped Probe', (240, 240, 240), True)
    navy_type = wall_type_for(doc, base_type, 'QA Backdrop Navy', navy.Id, 0.05)
    orange_type = wall_type_for(doc, base_type, 'QA Backdrop Orange', orange.Id, 0.05)
    white_type = wall_type_for(doc, base_type, 'QA Backdrop White', white.Id, 0.05)

    groups = {}
    for index, cfg in enumerate(VARIANTS):
        material = build_material(doc, app, cfg)
        pane_type = wall_type_for(doc, base_type, 'QA Pane ' + cfg['key'], material.Id,
                                  GLASS_THICKNESS_MM / 304.8)
        x = index * GROUP_SPACING_FT
        ids = []
        ids.append(make_wall(doc, pane_type, level, x, x + PANE_W_FT, 0.0, PANE_H_FT, 0.15).Id)
        # backdrop 6 in behind the pane, wider and taller than it; colour edge at pane centre
        ids.append(make_wall(doc, navy_type, level, x - 0.4, x + 0.7, 0.5, 1.8).Id)
        ids.append(make_wall(doc, white_type, level, x + 0.7, x + 1.0, 0.5, 1.8).Id)
        ids.append(make_wall(doc, orange_type, level, x + 1.0, x + PANE_W_FT + 0.4, 0.5, 1.8).Id)
        groups[cfg['key']] = ids
    doc.Regenerate()

    view_type = None
    for candidate in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType):
        if candidate.ViewFamily == DB.ViewFamily.ThreeDimensional:
            view_type = candidate
            break
    all_ids = [i for ids in groups.values() for i in ids]

    def make_view(name, key, forward):
        view = DB.View3D.CreateIsometric(doc, view_type.Id)
        view.Name = name
        length = math.sqrt(sum(c * c for c in forward))
        f = DB.XYZ(forward[0] / length, forward[1] / length, forward[2] / length)
        right = f.CrossProduct(DB.XYZ.BasisZ).Normalize()
        up = right.CrossProduct(f).Normalize()
        centre = DB.XYZ(VARIANTS_INDEX[key] * GROUP_SPACING_FT + PANE_W_FT / 2.0, 0.0, 0.9)
        view.SetOrientation(DB.ViewOrientation3D(centre - f.Multiply(20.0), up, f))
        view.DisplayStyle = DB.DisplayStyle.Realistic
        view.DetailLevel = DB.ViewDetailLevel.Fine
        hide = List[DB.ElementId]()
        keep = set(i.Value for i in groups[key])
        for element_id in all_ids:
            if element_id.Value not in keep and doc.GetElement(element_id).CanBeHidden(view):
                hide.Add(element_id)
        if hide.Count:
            view.HideElements(hide)
        # Level datums show in 3D views in Revit 2025 and drag FitToPage out to their
        # extents (first run exported 1600 x 160 strips). Hide them and box the group.
        for category in (DB.BuiltInCategory.OST_Levels, DB.BuiltInCategory.OST_Grids):
            try:
                view.SetCategoryHidden(DB.ElementId(category), True)
            except Exception as exc:
                REPORT['notes'].append('category hide failed: ' + str(exc).splitlines()[0][:120])
        x0 = VARIANTS_INDEX[key] * GROUP_SPACING_FT
        box = DB.BoundingBoxXYZ()
        box.Min = DB.XYZ(x0 - 0.6, -0.5, -0.1)
        box.Max = DB.XYZ(x0 + PANE_W_FT + 0.6, 1.0, 2.0)
        view.SetSectionBox(box)
        view.IsSectionBoxActive = True
        try:
            view.SetCategoryHidden(DB.ElementId(DB.BuiltInCategory.OST_SectionBox), True)
        except Exception as exc:
            REPORT['notes'].append('section box hide failed: ' + str(exc).splitlines()[0][:120])
        return view

    front_views, oblique_views = [], []
    for cfg in VARIANTS:
        front_views.append(make_view('front ' + cfg['key'], cfg['key'], (0.0, 1.0, 0.0)))
    for cfg in VARIANTS:
        if cfg['relief']:
            oblique_views.append(make_view('oblique ' + cfg['key'], cfg['key'], (0.75, 1.0, -0.15)))
    textures_view = make_view('front height TEXTURES style', 'height', (0.0, 1.0, 0.0))
    textures_view.DisplayStyle = DB.DisplayStyle.Textures
    views = front_views + oblique_views + [textures_view]
    set_light(doc, views, 90.0, 20.0, 'A')
    tx.Commit()
    checkpoint('built')

    rvt = out_path('qa', 'Clear_Reeded_Glass_QA_DISPOSABLE_R2025.rvt')
    save = DB.SaveAsOptions()
    save.OverwriteExistingFile = True
    doc.SaveAs(rvt, save)
    checkpoint('saved')

    try:
        export_views(doc, views, 'lightA')
        REPORT['exports']['lightA'] = 'exported'
    except Exception:
        REPORT['exports']['lightA'] = 'FAILED ' + traceback.format_exc().splitlines()[-1]
    checkpoint('exported-A')

    tx2 = DB.Transaction(doc, 'light B')
    tx2.Start()
    set_light(doc, views, 270.0, 20.0, 'B')
    tx2.Commit()
    try:
        export_views(doc, [v for v, c in zip(front_views, VARIANTS) if c['relief']], 'lightB')
        REPORT['exports']['lightB'] = 'exported'
    except Exception:
        REPORT['exports']['lightB'] = 'FAILED ' + traceback.format_exc().splitlines()[-1]
    checkpoint('exported-B')

    doc.Save()
    doc.Close(False)

    # Reopen from disk; everything below is read from the saved file.
    doc = app.OpenDocumentFile(rvt)
    REPORT['reopened'] = True
    REPORT['rvt_path'] = rvt
    REPORT['rvt_bytes'] = os.path.getsize(rvt)
    REPORT['project_warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    REPORT['legacy_readback'] = {}
    for cfg in VARIANTS:
        if not cfg.get('schema'):
            REPORT['variants'][cfg['key']] = read_back(doc, cfg)
        else:
            REPORT['legacy_readback'][cfg['key']] = read_back_legacy(doc, cfg)
    doc.Close(False)

    REPORT['qa_images'] = sorted(n for n in os.listdir(os.path.join(RUN_DIR, 'qa'))
                                 if n.lower().endswith('.png'))
    REPORT['adsklib'] = {
        'status': 'PENDING',
        'reason': ('A material library is created in the Revit Material Browser; there is no '
                   'Revit API route. Not attempted by this script.'),
    }
    REPORT['ray_traced_render'] = 'NOT RUN - no API route; Realistic viewport exports only'
    failed = dict((k, sorted(n for n, ok in v['gates'].items() if not ok))
                  for k, v in REPORT['variants'].items())
    REPORT['failed_gates'] = failed
    REPORT['zero_project_warnings'] = not REPORT['project_warnings']
    REPORT['revit_pass'] = all(v['pass'] for v in REPORT['variants'].values())
    checkpoint('complete')
    if any(failed.values()):
        raise RuntimeError('Gate failures: ' + json.dumps(failed))


VARIANTS_INDEX = dict((cfg['key'], i) for i, cfg in enumerate(VARIANTS))

if __name__ == '__main__':
    try:
        main()
    except Exception:
        REPORT['error'] = traceback.format_exc()
        try:
            checkpoint('failed')
        finally:
            raise
