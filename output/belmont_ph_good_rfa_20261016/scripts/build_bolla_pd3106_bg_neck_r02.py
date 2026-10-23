# -*- coding: utf-8 -*-
r"""651 Belmont PH Good: bounded Bolla PD3106-BG partial metal finish candidate.

STANDALONE pyRevit / IronPython 2.7 script for an ISOLATED Revit 2025 process.

To run later (prime only):
  D:\Games\pyRevit-Master\bin\pyrevit.exe run "E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\scripts\build_bolla_pd3106_bg_neck_r02.py" --revit=2025

NEVER overwrites the input, any OEM original, or an existing candidate. The
script has not been executed in native Revit as part of its preparation.

Verified sources:
 - OEM-derived family: source SHA256 EB5CF17C25531152ACC8E51CCB0AD5BD80913AE547F878D9108D059090E6F2F3
 - Downloaded OEM original: 8D84D0A6842B26CA3B8686F86948172349D1D1AEC04A75A2B68AF4463EF5C98A
 - Existing read-only Revit parts probe: 2EE88654C081A629FA324681703497A72ADFF29A2481A676F51B98D03B2213B3
 - Manufacturer Bolla: https://kuzcolighting.com/products/bolla-pd3106-kuzco
 - Manufacturer spec hosted by authorized distributor:
   https://kuzcolighting.lightingnewyork.com/on/demandware.static/-/Sites-master-catalog-lny/default/dw1bbe4fb8/brand/kuz/assets/specsheet/pd3106+spec+sheet.pdf

The probe establishes these stable Revit 2025 element IDs / face assignments:
  4435: Revolution. Clear outer globe, 6 faces, material 1742 "Glass".
  5101: Revolution. Opal inner globe, 16 faces, material 8722 "Glass Frosted".
  4715: Revolution. Small, unassigned metal-neck candidate, 8 faces,
        bounds 14.8x17.09x25.78 mm at Z3464.22..3490.00 mm.
  7721: Revolution. Unassigned 14-face suspension/canopy assembly, 510mm
        tall with 117x120 mm maximum section. DO NOT RECOLOR this element.
        It likely combines steel hardware and black suspension wire,
        requiring separate face-level evidence for a future full BG variant.

Only element 4715 receives a new, approximate Brushed Gold material. The
opaque/transparent glass finishes and 7721 stay untouched. Material RGB and
reflectance are provisional visual approximations, not OEM calibrated values.

STATUS: PARTIAL METAL NECK ONLY; UNSUITABLE FOR FINAL FINISH ACCEPTANCE.
"""
from __future__ import print_function

import os
import json
import time
import hashlib
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SOURCE = os.path.join(BASE, 'families', 'Kuzco_Bolla_PD3106_BG_R2025.rfa')
OEM_SOURCE = os.path.join(
    BASE, 'sources', 'oem', 'extracted', 'KZC1353667_PD3106_Bolla_Revit',
    'PD3106 - Bolla.rfa')
PROBE = os.path.join(BASE, 'qa', 'inspect_oem_material_parts.json')
TARGET = os.path.join(
    BASE, 'candidates', 'Kuzco_Bolla_PD3106_BG_R2025_R02_PARTIAL_NECK_UNAPPROVED.rfa')
RECEIPT = os.path.join(BASE, 'qa', 'bolla_pd3106_bg_r02_neck_build.json')

SOURCE_SHA256 = 'eb5cf17c25531152acc8e51ccb0ad5bd80913ae547f878d9108d059090e6f2f3'
OEM_SHA256 = '8d84d0a6842b26ca3b8686f86948172349d1d1aec04a75a2b68af4463ef5c98a'
PROBE_SHA256 = '2ee88654c081a629fa324681703497a72adff29a2481a676f51b98d03b2213b3'
EXPECTED_NAME = 'Type 1'
SOURCE_IDS = {'outer_glass': 4435, 'metal_neck': 4715,
              'inner_opal': 5101, 'mixed_suspension': 7721}
GLASS_MATS = {'outer_glass': 1742, 'inner_opal': 8722}
EXPECTED_FACES = {'outer_glass': 6, 'metal_neck': 8,
                  'inner_opal': 16, 'mixed_suspension': 14}
EXPECTED_Z_MM = {
    'outer_glass': (3337.68, 3476.78),
    'metal_neck': (3464.22, 3490.00),
    'inner_opal': (3396.50, 3475.31),
    'mixed_suspension': (3490.00, 4000.00),
}
EXPECTED_XY_SIZE_MM = {
    'outer_glass': (139.72, 140.65),
    'metal_neck': (14.80, 17.09),
    'inner_opal': (63.39, 63.52),
    'mixed_suspension': (116.99, 120.00),
}
GEOMETRY_TOL_MM = .75
NEW_MATERIAL = 'PHGOOD_KUZCO_BOLLA_BRUSHED_GOLD_NECK_R02_ESTIMATED'
NEW_ASSET = 'PHGOOD Bolla Brushed Gold Approximate Metal R02'
# Numerically estimated warm brass tone only; NOT a measured Kuzco BG sample.
BG_RGB = (199, 164, 108)
MFR_URL = 'https://kuzcolighting.com/products/bolla-pd3106-kuzco'
SPEC_URL = ('https://kuzcolighting.lightingnewyork.com/on/demandware.static/'
            '-/Sites-master-catalog-lny/default/dw1bbe4fb8/brand/kuz/'
            'assets/specsheet/pd3106+spec+sheet.pdf')


def guard(test, message):
    if not test:
        raise RuntimeError(message)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            part = stream.read(1024 * 1024)
            if not part:
                break
            digest.update(part)
    return digest.hexdigest()


def id_value(element_id):
    if element_id is None:
        return None
    try:
        return int(element_id.Value)
    except Exception:
        try:
            return int(element_id.IntegerValue)
        except Exception:
            return None


def elt_name(element):
    if element is None:
        return None
    try:
        return unicode(DB.Element.Name.GetValue(element))
    except Exception:
        try:
            return unicode(element.Name)
        except Exception:
            return None


def element(doc, value):
    return doc.GetElement(DB.ElementId(int(value)))


def xyz_bounds_of_solid(solid):
    low = [float('inf')] * 3
    high = [float('-inf')] * 3
    for face in solid.Faces:
        for vertex in face.Triangulate().Vertices:
            coords = (float(vertex.X), float(vertex.Y), float(vertex.Z))
            for i in range(3):
                low[i] = min(low[i], coords[i])
                high[i] = max(high[i], coords[i])
    for edge in solid.Edges:
        # Revit occasionally returns None for an analytic edge; tessellated
        # faces are still the source of bounds when that happens.
        curve = edge.AsCurve()
        if curve is None:
            continue
        count = 25 if not isinstance(curve, DB.Line) else 2
        for i in range(count):
            point = curve.Evaluate(float(i) / float(count - 1), True)
            coords = (float(point.X), float(point.Y), float(point.Z))
            for j in range(3):
                low[j] = min(low[j], coords[j])
                high[j] = max(high[j], coords[j])
    return low, high


def inspect_revolution(doc, name):
    original_id = SOURCE_IDS[name]
    target = element(doc, original_id)
    guard(isinstance(target, DB.Revolution),
          'Expected native Revolution at element %d (%s)' % (original_id, name))
    opts = DB.Options()
    opts.IncludeNonVisibleObjects = False
    opts.DetailLevel = DB.ViewDetailLevel.Fine
    solids = []
    for item in target.get_Geometry(opts):
        if isinstance(item, DB.Solid) and item.Volume > 1e-12:
            solids.append(item)
    guard(len(solids) == 1, 'Expected one solid at element %d' % original_id)
    solid = solids[0]
    faces = list(solid.Faces)
    guard(len(faces) == EXPECTED_FACES[name],
          'Face-count mismatch for %s: %d' % (name, len(faces)))
    material_ids = [id_value(face.MaterialElementId) for face in faces]
    low, high = xyz_bounds_of_solid(solid)
    low_mm = [round(x * 304.8, 3) for x in low]
    high_mm = [round(x * 304.8, 3) for x in high]
    span_xy = [high_mm[i] - low_mm[i] for i in (0, 1)]
    expect_z = EXPECTED_Z_MM[name]
    expect_xy = EXPECTED_XY_SIZE_MM[name]
    for measured, expected, label in [
        (low_mm[2], expect_z[0], 'Z min'),
        (high_mm[2], expect_z[1], 'Z max'),
        (span_xy[0], expect_xy[0], 'X width'),
        (span_xy[1], expect_xy[1], 'Y width'),
    ]:
        guard(abs(measured - expected) <= GEOMETRY_TOL_MM,
              '%s geometry changed: %s %.3f mm expected %.3f mm'
              % (name, label, measured, expected))
    if name in GLASS_MATS:
        guard(set(material_ids) == set([GLASS_MATS[name]]),
              'Glass face material IDs changed for %s: %s'
              % (name, repr(material_ids)))
    return {'id': original_id, 'class': 'Revolution', 'face_count': len(faces),
            'face_material_ids': sorted(set(material_ids),
                                        key=lambda k: (k is None, str(k))),
            'low_xyz_mm': low_mm, 'high_xyz_mm': high_mm,
            'size_xyz_mm': [round(high_mm[i] - low_mm[i], 3) for i in range(3)]}


def material_state(doc, mid):
    mat = element(doc, mid)
    guard(isinstance(mat, DB.Material), 'Material %s unexpectedly missing' % mid)
    color = mat.Color
    return {'id': mid, 'name': elt_name(mat),
            'rgb': [int(color.Red), int(color.Green), int(color.Blue)],
            'transparency': int(mat.Transparency),
            'appearance_asset_id': id_value(mat.AppearanceAssetId)}


def materials_for_existing_glass(doc):
    return dict((role, material_state(doc, mid)) for role, mid in GLASS_MATS.items())


def validate_source(doc, new_id=None):
    guard(doc.IsFamilyDocument, 'Opened document is not a Revit family')
    guard(elt_name(doc.OwnerFamily.FamilyCategory) == 'Lighting Fixtures',
          'Source is no longer a Lighting Fixtures family')
    guard(str(doc.OwnerFamily.FamilyPlacementType) == 'OneLevelBasedHosted',
          'Original Revit family hosting changed')
    names = sorted(unicode(t.Name) for t in doc.FamilyManager.Types)
    guard(names == [EXPECTED_NAME], 'Original family type(s) changed: ' + repr(names))
    guard(unicode(doc.FamilyManager.CurrentType.Name) == EXPECTED_NAME,
          'Configured source type unexpectedly changed')
    parts = dict((role, inspect_revolution(doc, role)) for role in SOURCE_IDS)
    guard(parts['outer_glass']['face_material_ids'] == [1742],
          'Outer glass not preserved')
    guard(parts['inner_opal']['face_material_ids'] == [8722],
          'Inner opal glass not preserved')
    guard(parts['mixed_suspension']['face_material_ids'] in ([None], [-1]),
          'Suspension/canopy no longer unassigned')
    if new_id is None:
        guard(parts['metal_neck']['face_material_ids'] in ([None], [-1]),
              'Neck no longer unassigned; source differs from probe')
    else:
        guard(parts['metal_neck']['face_material_ids'] == [new_id],
              'Only-neck Brushed Gold material did not bind every native face')
    guard(len(list(doc.GetWarnings())) == 0,
          'Source or candidate contains Revit document warnings')
    return {'parts': parts, 'glass_materials': materials_for_existing_glass(doc),
            'category': 'Lighting Fixtures', 'configured_type': EXPECTED_NAME}


def assert_probe_matches():
    data = json.load(open(PROBE, 'rb'))
    guard(data.get('schema_version') == 1,
          'Parts probe schema changed')
    guard(data.get('all_native_geometries_read') is True,
          'Parts probe geometry incomplete')
    family = [f for f in data.get('families', [])
              if f.get('id') == 'kzc1353667']
    guard(len(family) == 1, 'Bolla parts probe record missing/ambiguous')
    f = family[0]
    guard(f.get('source_paths_intact') is True
          and f.get('inspection_status') == 'NATIVE_GEOMETRY_READ_COMPLETE',
          'Parts probe source or geometry status changed')
    guard(f['saved_family_before']['sha256'].lower() == SOURCE_SHA256
          and f['downloaded_oem_source_before']['sha256'].lower() == OEM_SHA256,
          'Parts probe fingerprints differ from approved inputs')
    elements = dict((row['id'], row) for row in f['elements'])
    for role, eid in SOURCE_IDS.items():
        guard(eid in elements, 'Probe missing element %d' % eid)
        row = elements[eid]
        guard(row['class'] == 'Autodesk.Revit.DB.Revolution',
              'Probe element %d is not a Revolution' % eid)
        counts = row['geometry']['native_material_face_counts']
        expected_mat = str(GLASS_MATS[role]) + ':face' if role in GLASS_MATS else 'None:unassigned'
        guard(int(counts.get(expected_mat, -1)) == EXPECTED_FACES[role],
              'Probe faces mismatch for element %d' % eid)


def get_generic_asset(app):
    for asset in app.GetAssets(DB.Visual.AssetType.Appearance):
        marker = asset.FindByName('BaseSchema')
        if marker is not None and marker.Value == 'GenericSchema':
            return asset
    raise RuntimeError('No GenericSchema render asset template installed')


def build_gold(doc, app):
    for material in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        guard(elt_name(material) != NEW_MATERIAL,
              'Brushed Gold candidate material already exists')
    id_created = DB.Material.Create(doc, NEW_MATERIAL)
    material = doc.GetElement(id_created)
    material.Color = DB.Color(*BG_RGB)
    material.Transparency = 0
    asset = DB.AppearanceAssetElement.Create(doc, NEW_ASSET, get_generic_asset(app))
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    try:
        editable = scope.Start(asset.Id)
        values = [
            ('generic_diffuse', 'rgb', BG_RGB),
            ('generic_glossiness', 'double', .63),
            ('generic_reflectivity_at_0deg', 'double', .62),
            ('generic_reflectivity_at_90deg', 'double', .83),
            ('generic_transparency', 'double', 0.0),
        ]
        for key, value_type, val in values:
            p = editable.FindByName(key)
            guard(p is not None, 'Generic gold appearance property missing: ' + key)
            if p.NumberOfConnectedProperties:
                p.RemoveConnectedAsset()
            if value_type == 'rgb':
                p.SetValueAsColor(DB.Color(*val))
            else:
                p.Value = val
        scope.Commit(True)
    finally:
        scope.Dispose()
    material.AppearanceAssetId = asset.Id
    return material


def find_neck_material_parameter(neck):
    param = neck.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM)
    if param is None:
        candidates = [p for p in neck.Parameters
                      if unicode(p.Definition.Name).lower() == 'material']
        guard(len(candidates) == 1,
              'No unambiguous native Revolution Material parameter on neck')
        param = candidates[0]
    guard(param is not None and not param.IsReadOnly,
          'Neck Revolution Material parameter unavailable or read-only')
    guard(str(param.StorageType) == 'ElementId',
          'Neck Revolution material parameter is not ElementId')
    return param


def save_receipt_once(data):
    guard(not os.path.lexists(RECEIPT),
          'Native candidate receipt already exists; refusing overwrite')
    temporary = RECEIPT + '.tmp'
    guard(not os.path.lexists(temporary),
          'Temporary candidate receipt already exists')
    payload = json.dumps(data, sort_keys=True, indent=2, ensure_ascii=True)
    handle = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    try:
        with os.fdopen(handle, 'wb') as stream:
            if isinstance(payload, unicode):
                payload = payload.encode('ascii')
            stream.write(payload)
        guard(not os.path.lexists(RECEIPT),
              'Candidate receipt appeared during run; refusing overwrite')
        os.rename(temporary, RECEIPT)
    finally:
        if os.path.exists(temporary):
            try:
                os.remove(temporary)
            except Exception:
                pass


def main():
    guard('__revit__' in globals(), 'Run standalone in isolated pyRevit 2025')
    app = __revit__.Application
    guard(str(app.VersionNumber) == '2025', 'Native Revit 2025 required')
    guard(getattr(__revit__, 'ActiveUIDocument', None) is None,
          'Refusing to run in a session with an active user document')
    for path in (SOURCE, OEM_SOURCE, PROBE):
        guard(os.path.isfile(path), 'Required source missing: ' + path)
    for path in (TARGET, RECEIPT):
        guard(not os.path.lexists(path),
              'Output already exists; refusing overwrite: ' + path)
    guard(os.path.normcase(SOURCE) != os.path.normcase(TARGET),
          'Never update source in place')
    guard(sha256(SOURCE) == SOURCE_SHA256, 'Saved OEM-derived RFA hash changed')
    guard(sha256(OEM_SOURCE) == OEM_SHA256, 'Downloaded OEM RFA hash changed')
    guard(sha256(PROBE) == PROBE_SHA256, 'Independent native parts probe hash changed')
    assert_probe_matches()

    doc = None
    saved = None
    tx = None
    before = None
    try:
        doc = app.OpenDocumentFile(SOURCE)
        before = validate_source(doc)
        tx = DB.Transaction(doc, 'Bolla PD3106-BG partial Brushed Gold neck only')
        guard(tx.Start() == DB.TransactionStatus.Started,
              'Could not start isolated family transaction')
        new_mat = build_gold(doc, app)
        neck = element(doc, SOURCE_IDS['metal_neck'])
        param = find_neck_material_parameter(neck)
        guard(param.Set(new_mat.Id), 'Revit refused neck material assignment')
        doc.Regenerate()
        in_memory = validate_source(doc, id_value(new_mat.Id))
        guard(before['glass_materials'] == in_memory['glass_materials'],
              'Glass material definitions changed in candidate')
        for name in ('outer_glass', 'inner_opal', 'mixed_suspension'):
            guard(before['parts'][name] == in_memory['parts'][name],
                  'Protected geometry/material changed: ' + name)
        guard(before['parts']['metal_neck']['size_xyz_mm'] ==
              in_memory['parts']['metal_neck']['size_xyz_mm'],
              'Neck geometry changed unexpectedly')
        guard(tx.Commit() == DB.TransactionStatus.Committed,
              'Native candidate transaction commit failed')
        tx = None

        save_dir = os.path.dirname(TARGET)
        guard(os.path.isdir(save_dir),
              'Expected candidates directory missing: ' + save_dir)
        guard(not os.path.lexists(TARGET), 'Output appeared before SaveAs')
        opts = DB.SaveAsOptions()
        opts.OverwriteExistingFile = False
        opts.MaximumBackups = 1
        doc.SaveAs(TARGET, opts)
        doc.Close(False)
        doc = None
        guard(os.path.isfile(TARGET), 'Revit did not write candidate')
        guard(sha256(SOURCE) == SOURCE_SHA256, 'Saved source RFA was modified')
        guard(sha256(OEM_SOURCE) == OEM_SHA256, 'Original OEM RFA was modified')
        guard(sha256(PROBE) == PROBE_SHA256, 'Independent QA receipt was modified')

        saved = app.OpenDocumentFile(TARGET)
        candidates = [m for m in DB.FilteredElementCollector(saved).OfClass(DB.Material)
                      if elt_name(m) == NEW_MATERIAL]
        guard(len(candidates) == 1, 'Saved gold material absent or duplicated')
        candidate = candidates[0]
        candidate_material_id = id_value(candidate.Id)
        actual = validate_source(saved, candidate_material_id)
        guard(before['glass_materials'] == actual['glass_materials'],
              'Readback glass definitions differ from source')
        for name in ('outer_glass', 'inner_opal', 'mixed_suspension'):
            guard(before['parts'][name] == actual['parts'][name],
                  'Readback changed protected component: ' + name)
        guard(before['parts']['metal_neck']['size_xyz_mm'] ==
              actual['parts']['metal_neck']['size_xyz_mm'],
              'Readback changed neck geometry')
        saved.Close(False)
        saved = None

        receipt = {
            'schema_version': 1,
            'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'status': 'R02_PARTIAL_METAL_NECK_ONLY_UNAPPROVED',
            'release_ready': False,
            'revit_version': '2025',
            'source_rfa': SOURCE,
            'source_sha256': SOURCE_SHA256,
            'downloaded_oem_rfa_sha256': OEM_SHA256,
            'native_probe_sha256': PROBE_SHA256,
            'candidate_rfa': TARGET,
            'candidate_sha256': sha256(TARGET),
            'metal_neck_element_id': SOURCE_IDS['metal_neck'],
            'new_material_id': candidate_material_id,
            'new_material_name': NEW_MATERIAL,
            'estimated_material_rgb': list(BG_RGB),
            'protected_element_ids': {
                'outer_glass': SOURCE_IDS['outer_glass'],
                'inner_opal': SOURCE_IDS['inner_opal'],
                'mixed_suspension': SOURCE_IDS['mixed_suspension']},
            'before': before, 'after': actual,
            'sources': [MFR_URL, SPEC_URL],
            'holds': [
                'Element 7721 merges metal canopy/suspension with black wire; not recolored',
                'Brushed Gold material numbers are approximations, not OEM material values',
                'Visual and independent host/photometry validation not performed',
            ],
        }
        save_receipt_once(receipt)
        print('BOLLA_NECK_R02_STATUS ' + receipt['status'])
        print('BOLLA_NECK_R02_RFA ' + TARGET)
        print('BOLLA_NECK_R02_RECEIPT ' + RECEIPT)
    finally:
        if tx is not None:
            try:
                tx.RollBack()
            except Exception:
                pass
        if saved is not None:
            try:
                saved.Close(False)
            except Exception:
                pass
        if doc is not None:
            try:
                doc.Close(False)
            except Exception:
                pass


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('BOLLA_NECK_R02_FAIL: ' + traceback.format_exc())
        raise
