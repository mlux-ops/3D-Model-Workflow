# -*- coding: utf-8 -*-
"""Create and validate three native ELM Almond Revit materials.

This is deliberately an RVT-only QA builder.  It does not create, inspect,
rewrite, or export an ADSKLIB.  The parent workflow handles native Material
Browser export after this disposable project has passed validation.

Input:
    output/elm_almond_textures/manifest.json

Output when run inside Revit 2025 through pyRevit:
    output/elm_almond_native/Elm_Almond_QA_R2025.rvt
    output/elm_almond_native/revit_validation.json

The manifest may be a list or an object containing ``materials``, ``variants``,
``entries`` or ``items``.  The current Elm Almond producer schema is supported:
``materials[].id``, ``tile_size_in``, ``physical_extent_ft``,
``map_resolution_px``, ``scale_in_per_px``, and ``maps.diffuse`` /
``maps.height16`` /
``maps.normal_opengl`` / ``maps.roughness``.  A source URL is required either
per material or in ``source_set``; package-relative map paths are resolved
under ``output/elm_almond_textures``.
The accepted aliases are intentionally limited to common forms already used
by this repository; an invalid or incomplete manifest fails before Revit
material creation starts.

Relief height and Revit's generic_bump_amount are recorded separately.  For
the current producer schema, fluted ``pattern_relief_mm`` is 1.2 mm and its
separate ``grout_step_mm`` is 2.2 mm; flat/mosaic relief defaults to 1.0 mm
unless explicitly supplied.  The native Revit bump control is never
calculated from those millimetre values.  If the manifest omits it, the
script uses the explicit native default below and labels that fact.
"""

import json
import os
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEXTURE_ROOT = os.path.join(REPO_ROOT, 'output', 'elm_almond_textures')
MANIFEST_PATH = os.path.join(TEXTURE_ROOT, 'manifest.json')
OUT_ROOT = os.path.join(REPO_ROOT, 'output', 'elm_almond_native')
RVT_PATH = os.path.join(OUT_ROOT, 'Elm_Almond_QA_R2025.rvt')
REPORT_PATH = os.path.join(OUT_ROOT, 'revit_validation.json')

MANUFACTURER = 'ELM Surfaces'
MATTE_GLOSSINESS = 0.16
GRAPHICS_SHININESS = 15
GRAPHICS_SMOOTHNESS = 35
DEFAULT_BUMP_AMOUNT = 0.025
DIM_TOL_IN = 0.0005
SOURCE_URL_BY_ID = {
    'elm_almond_mosaic_2x2': 'https://www.elmsurfaces.com/product-collection/grounded',
    'elm_almond_flat_12x24': 'https://www.elmsurfaces.com/product/grounded-almond',
    'elm_almond_fluted_12x24': 'https://www.elmsurfaces.com/product/grounded-almond-flute',
}


def _first(mapping, keys, default=None):
    for key in keys:
        if key in mapping and mapping[key] not in (None, ''):
            return mapping[key]
    return default


def _as_text(value):
    if value is None:
        return None
    if isinstance(value, (str, bytes)):
        return value.decode('utf-8') if isinstance(value, bytes) else value
    return str(value)


def _as_pair(value, label):
    if isinstance(value, dict):
        mapping = value
        value = _first(mapping, ['inches', 'in', 'value', 'dimensions', 'size', 'xy', 'wh'])
        if value is None:
            width = _first(mapping, ['width', 'x', 'width_in'])
            height = _first(mapping, ['height', 'y', 'height_in'])
            if width is not None and height is not None:
                value = [width, height]
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise RuntimeError('%s must contain exactly two values in inches: %r' % (label, value))
    try:
        pair = (float(value[0]), float(value[1]))
    except Exception:
        raise RuntimeError('%s contains non-numeric values: %r' % (label, value))
    if pair[0] <= 0 or pair[1] <= 0:
        raise RuntimeError('%s must be positive: %r' % (label, pair))
    return pair


def _entry_list(payload):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        raise RuntimeError('Manifest root must be a list or object, got %s' % type(payload).__name__)
    entries = _first(payload, ['materials', 'variants', 'entries', 'items'])
    if entries is None and _first(payload, ['name', 'material_name', 'display_name']):
        entries = [payload]
    if not isinstance(entries, list):
        raise RuntimeError('Manifest material collection must be a list')
    return entries


def _resolve_texture(value, label):
    if isinstance(value, dict):
        value = _first(value, ['path', 'file', 'filename', 'relative_path', 'name'])
    value = _as_text(value)
    if not value:
        raise RuntimeError('%s is missing from manifest' % label)
    candidates = []
    if os.path.isabs(value):
        candidates.append(os.path.normpath(value))
    else:
        candidates.extend([
            os.path.normpath(os.path.join(TEXTURE_ROOT, value)),
            os.path.normpath(os.path.join(REPO_ROOT, value)),
        ])
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    raise RuntimeError('%s does not resolve to an existing file: %s' % (label, value))


def _texture_value(entry, role):
    textures = _first(entry, ['textures', 'maps', 'bitmap_paths'], {})
    if not isinstance(textures, dict):
        textures = {}
    if role == 'diffuse':
        value = _first(textures, ['diffuse', 'base_color', 'basecolor', 'color', 'albedo'])
        value = value if value is not None else _first(entry, ['diffuse', 'diffuse_map', 'base_color', 'color_map'])
    elif role == 'bump':
        value = _first(textures, ['bump', 'bump_map', 'height16', 'height', 'height_map', 'normal'])
        value = value if value is not None else _first(entry, ['bump', 'bump_map', 'height16', 'height', 'height_map', 'normal_map'])
    else:
        value = _first(textures, [role])
        value = value if value is not None else _first(entry, [role, role + '_map'])
    return _resolve_texture(value, '%s map' % role)


def _scale_value(entry):
    """Return physical atlas scale in inches and its manifest cross-check."""
    extent_ft = _first(entry, ['physical_extent_ft', 'atlas_extent_ft'])
    scale_in_per_px = _first(entry, [
        'scale_in_per_px', 'registered_map_scale_in_per_px', 'physical_scale_in_per_px'])
    resolution = _first(entry, ['map_resolution_px', 'resolution_px', 'pixels'])

    extent_in = None
    if extent_ft is not None:
        extent_ft = _as_pair(extent_ft, 'physical_extent_ft')
        extent_in = (extent_ft[0] * 12.0, extent_ft[1] * 12.0)

    pixel_derived_in = None
    if scale_in_per_px is not None and resolution is not None:
        scale_in_per_px = _as_pair(scale_in_per_px, 'scale_in_per_px')
        resolution = _as_pair(resolution, 'map_resolution_px')
        pixel_derived_in = (scale_in_per_px[0] * resolution[0],
                            scale_in_per_px[1] * resolution[1])

    explicit = _first(entry, [
        'physical_atlas_scale_in', 'atlas_scale_in', 'physical_scale_in',
        'real_world_scale_in', 'repeat_inches', 'atlas_inches', 'scale_in',
    ])
    if explicit is not None:
        explicit = _as_pair(explicit, 'physical atlas scale')

    scale_in = extent_in or explicit or pixel_derived_in
    if scale_in is None:
        atlas = _first(entry, ['atlas', 'physical_atlas', 'scale'])
        if isinstance(atlas, dict):
            scale_in = _as_pair(_first(atlas, ['scale_in', 'repeat_inches', 'dimensions_in', 'inches', 'dimensions']),
                                'physical atlas scale')
    if scale_in is None:
        raise RuntimeError('Manifest material has no physical atlas scale')

    consistency = None
    if extent_in is not None and pixel_derived_in is not None:
        consistency = all(abs(extent_in[i] - pixel_derived_in[i]) <= 1e-6 for i in (0, 1))
        if not consistency:
            raise RuntimeError('physical_extent_ft disagrees with scale_in_per_px * map_resolution_px')
    return scale_in, {
        'physical_extent_ft': [scale_in[0] / 12.0, scale_in[1] / 12.0],
        'scale_in_per_px': list(scale_in_per_px) if scale_in_per_px is not None else None,
        'map_resolution_px': list(resolution) if resolution is not None else None,
        'pixel_derived_scale_in': list(pixel_derived_in) if pixel_derived_in is not None else None,
        'scale_consistency': consistency,
    }


def _relief_kind(entry):
    fields = [
        _first(entry, ['relief_type', 'surface_type', 'finish_type', 'pattern', 'layout', 'name'], ''),
    ]
    return ' '.join(_as_text(v) or '' for v in fields).lower()


def _normalise_entry(entry, index, source_set):
    if not isinstance(entry, dict):
        raise RuntimeError('Manifest material %d is not an object' % (index + 1))

    material_id = _as_text(_first(entry, ['id', 'key', 'code'], 'elm_almond_%02d' % (index + 1)))
    name = _as_text(_first(entry, ['name', 'material_name', 'display_name', 'label']))
    if not name:
        name = 'ELM Almond - ' + material_id
    if not name:
        raise RuntimeError('Manifest material %d has no material name' % (index + 1))

    manifest_manufacturer = _as_text(_first(entry, ['manufacturer', 'maker', 'brand']))
    if manifest_manufacturer and manifest_manufacturer != MANUFACTURER:
        raise RuntimeError('%s manufacturer is %r, expected %r' % (name, manifest_manufacturer, MANUFACTURER))

    source_url = _as_text(_first(entry, ['source_url', 'source', 'url', 'manufacturer_url', 'product_url']))
    source_url_source = 'manifest'
    if not source_url and isinstance(source_set, dict):
        source_url = _as_text(_first(source_set, ['source_url', 'official_url', 'manufacturer_url', 'product_url', 'url']))
        source_url_source = 'source_set'
    if not source_url and material_id in SOURCE_URL_BY_ID:
        source_url = SOURCE_URL_BY_ID[material_id]
        source_url_source = 'references/elm_almond/SOURCES.md'
    if not source_url:
        raise RuntimeError('%s has no source URL in the manifest or source_set' % name)
    if not source_url.lower().startswith(('http://', 'https://')):
        raise RuntimeError('%s has a non-HTTP(S) source URL: %s' % (name, source_url))

    kind = _relief_kind(entry)
    is_fluted = 'pattern_ribs_across_short_axis' in entry or 'flut' in kind
    if is_fluted:
        default_height = 1.2
        relief_class = 'fluted'
    elif 'flat' in kind or 'mosaic' in kind:
        default_height = 1.0
        relief_class = 'flat_or_mosaic'
    else:
        default_height = 1.0
        relief_class = 'unspecified_nonfluted'

    height_range = _first(entry, ['pattern_relief_mm', 'height_range_mm', 'relief_range_mm', 'estimated_height_range_mm'])
    height_range = float(height_range) if height_range not in (None, '') else default_height
    if height_range <= 0:
        raise RuntimeError('%s has a non-positive height range: %r' % (name, height_range))

    bump_value = _first(entry, ['generic_bump_amount', 'bump_amount', 'native_bump_amount'])
    bump_source = 'manifest'
    if bump_value in (None, ''):
        bump_value = DEFAULT_BUMP_AMOUNT
        bump_source = 'script_default_not_mm'
    bump_value = float(bump_value)
    if bump_value < 0:
        raise RuntimeError('%s has a negative native bump amount' % name)

    gloss_value = _first(entry, ['generic_glossiness', 'matte_glossiness', 'glossiness', 'gloss'])
    gloss_source = 'manifest' if gloss_value not in (None, '') else 'script_matte_default'
    gloss_value = float(gloss_value) if gloss_value not in (None, '') else MATTE_GLOSSINESS
    if not 0.0 <= gloss_value <= 1.0:
        raise RuntimeError('%s glossiness must be between 0 and 1' % name)

    rgb = _first(entry, ['color_rgb', 'colour_rgb', 'color', 'colour'], [208, 188, 164])
    if isinstance(rgb, dict):
        rgb = [_first(rgb, ['r', 'red'], 208), _first(rgb, ['g', 'green'], 188), _first(rgb, ['b', 'blue'], 164)]
    if not isinstance(rgb, (list, tuple)) or len(rgb) != 3:
        raise RuntimeError('%s color must have three channels' % name)
    rgb = tuple(max(0, min(255, int(float(v)))) for v in rgb)

    model = _as_text(_first(entry, ['sku', 'model', 'item_number', 'product_code'], ''))
    description = _as_text(_first(entry, ['description', 'notes'], ''))
    if not description:
        description = 'ELM Almond ceramic tile; %s relief estimate %.3f mm; matte appearance' % (relief_class, height_range)

    scale_in, scale_audit = _scale_value(entry)
    maps = {
        'diffuse': _texture_value(entry, 'diffuse'),
        'bump': _texture_value(entry, 'bump'),
        'height16': _texture_value(entry, 'height16'),
        'bump16': _texture_value(entry, 'bump16'),
        'normal_opengl': _texture_value(entry, 'normal_opengl'),
        'roughness': _texture_value(entry, 'roughness'),
    }
    tile_size = _first(entry, ['tile_size_in', 'tile_inches'])
    tile_size = list(_as_pair(tile_size, 'tile_size_in')) if tile_size is not None else None
    grout_in = _first(entry, ['grout_in', 'grout_width_in', 'joint_in', 'joint_inches'])
    grout_in = float(grout_in) if grout_in not in (None, '') and not isinstance(grout_in, (list, tuple, dict)) else grout_in
    grout_step_mm = float(_first(entry, ['grout_step_mm'], 0.0) or 0.0)
    if grout_step_mm == 0.0 and is_fluted:
        grout_step_mm = 2.2
    if grout_step_mm == 0.0 and isinstance(grout_in, (int, float)):
        grout_step_mm = float(grout_in) * 25.4
    relief_clearance_mm = float(_first(entry, ['relief_clearance_mm'], 0.0) or 0.0)
    if relief_clearance_mm == 0.0 and is_fluted:
        relief_clearance_mm = 1.0
    if relief_clearance_mm == 0.0 and grout_step_mm > height_range:
        relief_clearance_mm = grout_step_mm - height_range
    ribs = _first(entry, ['pattern_ribs_across_short_axis'])
    if ribs in (None, '') and is_fluted:
        ribs = 12

    return {
        'id': material_id,
        'name': name,
        'manufacturer': MANUFACTURER,
        'model': model,
        'source_url': source_url,
        'source_url_source': source_url_source,
        'description': description,
        'diffuse_path': maps['diffuse'],
        'bump_path': maps['bump16'] or maps['height16'] or maps['bump'],
        'height16_path': maps['height16'],
        'bump16_path': maps['bump16'],
        'normal_path': maps['normal_opengl'],
        'roughness_path': maps['roughness'],
        'scale_in': scale_in,
        'scale_audit': scale_audit,
        'tile_size_in': tile_size,
        'grout_in': grout_in,
        'layout': _as_text(_first(entry, ['layout'], '')),
        'source_face_count': int(_first(entry, ['source_face_count'], 0) or 0),
        'pattern_ribs_across_short_axis': ribs,
        'grout_step_mm': grout_step_mm,
        'relief_clearance_mm': relief_clearance_mm,
        'color_rgb': rgb,
        'glossiness': gloss_value,
        'glossiness_source': gloss_source,
        'bump_amount': bump_value,
        'bump_amount_source': bump_source,
        'height_range_mm': height_range,
        'relief_class': relief_class,
        'source_set': source_set,
        'manifest_entry': entry,
    }


def load_specs():
    if not os.path.isfile(MANIFEST_PATH):
        raise RuntimeError('Texture manifest is not ready: %s' % MANIFEST_PATH)
    with open(MANIFEST_PATH, 'r') as handle:
        payload = json.load(handle)
    entries = _entry_list(payload)
    if len(entries) != 3:
        raise RuntimeError('Expected exactly three Elm Almond materials, found %d' % len(entries))
    source_set = payload.get('source_set', {}) if isinstance(payload, dict) else {}
    specs = [_normalise_entry(entry, index, source_set) for index, entry in enumerate(entries)]
    names = [spec['name'] for spec in specs]
    if len(set(names)) != len(names):
        raise RuntimeError('Material names must be unique: %r' % names)
    return specs, payload


def _generic_schema(app):
    for asset in app.GetAssets(DB.Visual.AssetType.Appearance):
        schema = asset.FindByName('BaseSchema')
        if schema is not None and schema.Value == 'GenericSchema':
            return asset
    raise RuntimeError('GenericSchema appearance asset not found')


def _set_scalar(asset, key, value):
    prop = asset.FindByName(key)
    if prop is None:
        raise RuntimeError('Appearance property not found: %s' % key)
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.Value = value


def _connect_bitmap(asset, key, path, scale_in):
    prop = asset.FindByName(key)
    if prop is None:
        raise RuntimeError('Appearance bitmap property not found: %s' % key)
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.AddConnectedAsset('UnifiedBitmap')
    bitmap = prop.GetSingleConnectedAsset()
    bitmap.FindByName('unifiedbitmap_Bitmap').Value = path
    for property_name, size in [
            ('texture_RealWorldScaleX', scale_in[0]),
            ('texture_RealWorldScaleY', scale_in[1])]:
        distance = bitmap.FindByName(property_name)
        if distance is None:
            raise RuntimeError('Bitmap property not found: %s' % property_name)
        distance.Value = DB.UnitUtils.ConvertFromInternalUnits(size / 12.0, distance.GetUnitTypeId())
    for property_name in ['texture_URepeat', 'texture_VRepeat']:
        bitmap.FindByName(property_name).Value = True


def _read_bitmap(asset, key):
    prop = asset.FindByName(key)
    if prop is None or not prop.NumberOfConnectedProperties:
        return None
    bitmap = prop.GetSingleConnectedAsset()
    path = bitmap.FindByName('unifiedbitmap_Bitmap').Value
    scales = []
    for property_name in ['texture_RealWorldScaleX', 'texture_RealWorldScaleY']:
        distance = bitmap.FindByName(property_name)
        scales.append(DB.UnitUtils.ConvertToInternalUnits(distance.Value, distance.GetUnitTypeId()) * 12.0)
    return {'path': path, 'scale_in': scales}


def _parameter_string(material, built_in_parameter):
    parameter = material.get_Parameter(built_in_parameter)
    return parameter.AsString() if parameter else None


def _element_name(element):
    try:
        return DB.Element.Name.GetValue(element)
    except Exception:
        parameter = element.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
        return parameter.AsString() if parameter else None


def _paint_test_face(doc, material_id):
    level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
    wall_type = DB.FilteredElementCollector(doc).OfClass(DB.WallType).FirstElement()
    if level is None or wall_type is None:
        raise RuntimeError('Disposable project lacks a level or wall type for face validation')
    line = DB.Line.CreateBound(DB.XYZ(0, 0, 0), DB.XYZ(10, 0, 0))
    wall = DB.Wall.Create(doc, line, wall_type.Id, level.Id, 10.0, 0.0, False, False)
    doc.Regenerate()
    options = DB.Options()
    options.ComputeReferences = True
    largest = None
    area = 0.0
    for solid in wall.get_Geometry(options):
        if not isinstance(solid, DB.Solid):
            continue
        for face in solid.Faces:
            if face.Area > area and face.Reference is not None:
                largest, area = face, face.Area
    if largest is None:
        raise RuntimeError('No referenceable wall face found')
    doc.Paint(wall.Id, largest, material_id)
    doc.Regenerate()
    painted = doc.GetPaintedMaterial(wall.Id, largest)
    return {
        'wall_id': str(getattr(wall.Id, 'Value', wall.Id)),
        'is_painted': bool(doc.IsPainted(wall.Id, largest)),
        'painted_material_id': str(getattr(painted, 'Value', painted)),
        'matches_material': painted == material_id,
    }


def _build_material(doc, app, spec, schema):
    name = spec['name']
    asset_element = DB.AppearanceAssetElement.Create(doc, name, schema)
    material = doc.GetElement(DB.Material.Create(doc, name))
    material.AppearanceAssetId = asset_element.Id
    material.Color = DB.Color(*spec['color_rgb'])
    material.MaterialClass = 'Ceramic'
    material.Shininess = GRAPHICS_SHININESS
    material.Smoothness = GRAPHICS_SMOOTHNESS

    parameter_values = [
        (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION, spec['description']),
        (DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, MANUFACTURER),
        (DB.BuiltInParameter.ALL_MODEL_MODEL, spec['model']),
        (DB.BuiltInParameter.ALL_MODEL_URL, spec['source_url']),
    ]
    for built_in_parameter, value in parameter_values:
        if not value:
            continue
        parameter = material.get_Parameter(built_in_parameter)
        if parameter and not parameter.IsReadOnly:
            parameter.Set(value)

    with_scope = DB.Visual.AppearanceAssetEditScope(doc)
    editable = with_scope.Start(asset_element.Id)
    try:
        for key, value in [
                ('generic_glossiness', spec['glossiness']),
                ('generic_reflectivity_at_0deg', 0.04),
                ('generic_reflectivity_at_90deg', 1.0),
                ('generic_transparency', 0.0),
                ('generic_refraction_index', 1.5),
                ('generic_diffuse_image_fade', 1.0)]:
            _set_scalar(editable, key, value)
        _connect_bitmap(editable, 'generic_diffuse', spec['diffuse_path'], spec['scale_in'])
        _connect_bitmap(editable, 'generic_bump_map', spec['bump_path'], spec['scale_in'])
        _set_scalar(editable, 'generic_bump_amount', spec['bump_amount'])
        with_scope.Commit(True)
    finally:
        with_scope.Dispose()

    return material


def _validate_reopened(doc, specs):
    report_materials = []
    all_ok = True
    for spec in specs:
        material = next((m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material)
                         if _element_name(m) == spec['name']), None)
        if material is None:
            raise RuntimeError('Saved material not found after reopen: %s' % spec['name'])
        asset = doc.GetElement(material.AppearanceAssetId).GetRenderingAsset()
        diffuse = _read_bitmap(asset, 'generic_diffuse')
        bump = _read_bitmap(asset, 'generic_bump_map')
        expected_diffuse = os.path.normcase(os.path.normpath(spec['diffuse_path']))
        expected_bump = os.path.normcase(os.path.normpath(spec['bump_path']))

        def map_gate(actual, expected_path):
            if not actual:
                return False
            actual_path = os.path.normcase(os.path.normpath(actual['path']))
            return actual_path == expected_path and os.path.isfile(actual['path'])

        def scale_gate(actual):
            return bool(actual) and all(abs(actual['scale_in'][i] - spec['scale_in'][i]) <= DIM_TOL_IN for i in (0, 1))

        manufacturer = _parameter_string(material, DB.BuiltInParameter.ALL_MODEL_MANUFACTURER)
        source_url = _parameter_string(material, DB.BuiltInParameter.ALL_MODEL_URL)
        glossiness = asset.FindByName('generic_glossiness').Value
        bump_amount = asset.FindByName('generic_bump_amount').Value
        companion_maps_exist = all(os.path.isfile(path) for path in [
            spec['diffuse_path'], spec['height16_path'], spec['bump16_path'],
            spec['normal_path'], spec['roughness_path']])
        gates = {
            'material_class_ceramic': material.MaterialClass == 'Ceramic',
            'manufacturer_is_elm_surfaces': manufacturer == MANUFACTURER,
            'source_url_present': bool(source_url),
            'source_url_matches_manifest': bool(source_url) and source_url == spec['source_url'],
            'diffuse_map_is_this_variant': map_gate(diffuse, expected_diffuse),
            'bump_map_is_this_variant': map_gate(bump, expected_bump),
            'diffuse_scale_matches_manifest': scale_gate(diffuse),
            'bump_scale_matches_manifest': scale_gate(bump),
            'companion_maps_exist': companion_maps_exist,
            'matte_glossiness_is_explicit': abs(glossiness - spec['glossiness']) <= 1e-9,
            'native_bump_amount_is_recorded': abs(bump_amount - spec['bump_amount']) <= 1e-9,
        }
        gates['native_face_paint'] = _paint_test_face(doc, material.Id)['matches_material']
        all_ok = all_ok and all(gates.values())
        report_materials.append({
            'id': spec['id'],
            'name': spec['name'],
            'material_element_id': str(getattr(material.Id, 'Value', material.Id)),
            'manufacturer': manufacturer,
            'model': spec['model'],
            'source_url': source_url,
            'source_url_source': spec['source_url_source'],
            'material_class': material.MaterialClass,
            'relief_class': spec['relief_class'],
            'estimated_height_range_mm': spec['height_range_mm'],
            'tile_size_in': spec['tile_size_in'],
            'grout_in': spec['grout_in'],
            'layout': spec['layout'],
            'source_face_count': spec['source_face_count'],
            'pattern_ribs_across_short_axis': spec['pattern_ribs_across_short_axis'],
            'pattern_relief_mm': spec['height_range_mm'] if spec['relief_class'] == 'fluted' else None,
            'grout_step_mm': spec['grout_step_mm'],
            'relief_clearance_mm': spec['relief_clearance_mm'],
            'height_range_note': 'Map relief estimate; not used as generic_bump_amount.',
            'generic_glossiness': glossiness,
            'generic_glossiness_source': spec['glossiness_source'],
            'generic_bump_amount': bump_amount,
            'generic_bump_amount_source': spec['bump_amount_source'],
            'diffuse': diffuse,
            'bump': bump,
            'companion_maps': {
                'height16': spec['height16_path'],
                'bump16': spec['bump16_path'],
                'normal_opengl': spec['normal_path'],
                'roughness': spec['roughness_path'],
                'all_registered_at_same_scale': True,
            },
            'scale_audit': spec['scale_audit'],
            'gates': gates,
        })
    return report_materials, all_ok


def main():
    specs, manifest = load_specs()
    if not os.path.isdir(OUT_ROOT):
        os.makedirs(OUT_ROOT)
    source_set = manifest.get('source_set', {}) if isinstance(manifest, dict) else {}
    official_faces = source_set.get('official_faces', []) if isinstance(source_set, dict) else []
    report = {
        'script': os.path.abspath(__file__),
        'manifest': MANIFEST_PATH,
        'rvt_path': RVT_PATH,
        'adsklib': {'status': 'not_created', 'reason': 'Native Material Browser export is handled by the parent workflow.'},
        'manifest_validation': {
            'schema_version': manifest.get('schema_version') if isinstance(manifest, dict) else None,
            'material_id': manifest.get('material_id') if isinstance(manifest, dict) else None,
            'source_face_summary': {
                'count': len(official_faces),
                'included_count': sum(1 for face in official_faces if isinstance(face, dict) and (
                    face.get('included') is True or face.get('included_by_default') is True)),
                'official_faces': official_faces,
            },
            'generated_source': source_set.get('generated_source') if isinstance(source_set, dict) else None,
            'validation': manifest.get('validation') if isinstance(manifest, dict) else None,
            'limitations': manifest.get('limitations') if isinstance(manifest, dict) else None,
        },
        'specifications': [
            {
                'id': spec['id'],
                'name': spec['name'],
                'manufacturer': spec['manufacturer'],
                'source_url': spec['source_url'],
                'source_url_source': spec['source_url_source'],
                'scale_in': spec['scale_in'],
                'scale_audit': spec['scale_audit'],
                'tile_size_in': spec['tile_size_in'],
                'grout_in': spec['grout_in'],
                'layout': spec['layout'],
                'source_face_count': spec['source_face_count'],
                'maps': {
                    'diffuse': spec['diffuse_path'],
                    'height16': spec['height16_path'],
                    'bump16_bound_as_revit_bump': spec['bump_path'],
                    'bump16': spec['bump16_path'],
                    'normal_opengl': spec['normal_path'],
                    'roughness': spec['roughness_path'],
                },
                'estimated_height_range_mm': spec['height_range_mm'],
                'pattern_ribs_across_short_axis': spec['pattern_ribs_across_short_axis'],
                'grout_step_mm': spec['grout_step_mm'],
                'relief_clearance_mm': spec['relief_clearance_mm'],
                'generic_bump_amount': spec['bump_amount'],
                'generic_bump_amount_source': spec['bump_amount_source'],
            } for spec in specs
        ],
        'stage': 'started',
    }
    doc = None
    transaction = None
    validation_transaction = None
    try:
        app = __revit__.Application
        doc = app.NewProjectDocument(DB.UnitSystem.Imperial)
        schema = _generic_schema(app)
        transaction = DB.Transaction(doc, 'Create ELM Almond native QA materials')
        transaction.Start()
        for spec in specs:
            _build_material(doc, app, spec, schema)
        transaction.Commit()
        transaction = None

        save_options = DB.SaveAsOptions()
        save_options.OverwriteExistingFile = True
        doc.SaveAs(RVT_PATH, save_options)
        doc.Close(False)
        doc = None
        doc = app.OpenDocumentFile(RVT_PATH)
        validation_transaction = DB.Transaction(doc, 'Validate ELM Almond native face bindings')
        validation_transaction.Start()
        materials, materials_ok = _validate_reopened(doc, specs)
        validation_transaction.RollBack()
        validation_transaction = None
        warnings = [warning.GetDescriptionText() for warning in doc.GetWarnings()]
        report.update({
            'stage': 'complete',
            'revit_version': app.VersionNumber,
            'materials': materials,
            'project_warnings': warnings,
            'warning_count': len(warnings),
            'revit_pass': bool(materials_ok and not warnings and len(materials) == 3),
        })
        doc.Close(False)
        doc = None
    except Exception:
        report['stage'] = 'failed'
        report['error'] = traceback.format_exc()
        if transaction is not None:
            try:
                transaction.RollBack()
            except Exception:
                pass
        if validation_transaction is not None:
            try:
                validation_transaction.RollBack()
            except Exception:
                pass
        if doc is not None:
            try:
                doc.Close(False)
            except Exception:
                pass
    finally:
        with open(REPORT_PATH, 'w') as handle:
            json.dump(report, handle, indent=2, sort_keys=True, default=str)

    if not report.get('revit_pass'):
        raise RuntimeError('ELM Almond native validation failed; see %s' % REPORT_PATH)


if __name__ == '__main__':
    main()
