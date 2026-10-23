# -*- coding: utf-8 -*-
"""Bind the verified OEM PD3106-BG IES to a NEW Bolla Revit 2025 family.

IronPython 2.7, isolated pyRevit 2025 command, source-only until authorized.
This edits only the family light distribution and its built-in type parameter.
It does not change materials, element geometry, family type names or source RFA.

The new candidate is published ONLY after an isolated staged RFA has been saved,
closed, reopened and inspected for both photometric API and parameter readback.
The OEM IES is kept alongside the package; internal IES caching/portability is
NOT assumed. See BOLLA_BG_IES_R02_README.md.

API: https://www.revitapidocs.com/2025/c572d26c-9344-9256-64b0-88b19b6d768d.htm
API: https://www.revitapidocs.com/2025/e9f78e79-9a67-e911-3fb9-bd9a316043dc.htm
Autodesk issue:
https://forums.autodesk.com/t5/revit-api-forum/fbx-light-photometric-file-absolute-ies-path-issue/td-p/6869026
"""
from __future__ import print_function

import hashlib
import json
import os
import sys
import traceback
import uuid

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SOURCE = os.path.join(BASE, 'families', 'Kuzco_Bolla_PD3106_BG_R2025.rfa')
IES = os.path.join(BASE, 'sources', 'photometry', 'PD3106-BG - Bolla.IES')
IES_MANIFEST = os.path.join(BASE, 'sources', 'photometry', 'photometry_manifest.json')
TARGET = os.path.join(BASE, 'candidates',
                      'Kuzco_Bolla_PD3106_BG_R2025_IES_R02.rfa')
RECEIPT = os.path.join(BASE, 'qa', 'bolla_bg_ies_r02_native_receipt.json')

# 2026-10-16 independent source probe and official IES extraction.
SOURCE_SHA256 = 'eb5cf17c25531152acc8e51ccb0ad5bd80913ae547f878d9108d059090e6f2f3'
IES_SHA256 = '9e9f70e2eecc3b1c4130bea2f3fcb3c5a1798fb61363185348b635cd71737ce4'
EXPECTED_RFA_BYTES = 524288
EXPECTED_IES_BYTES = 39098
EXPECTED_TYPE = 'Type 1'
IES_NAME = 'PD3106-BG - Bolla.IES'
IES_URL = 'https://s3.us-west-2.amazonaws.com/catsy.870/IES-PD3106-Bolla.zip'


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            piece = stream.read(1024 * 1024)
            if not piece:
                break
            h.update(piece)
    return h.hexdigest()


def parameter_name(parameter):
    return str(parameter.Definition.Name)


def name_only(value):
    if value is None:
        return ''
    return os.path.basename(str(value).replace('/', '\\')).lower()


def has_exact_bg_name(value):
    return name_only(value) == IES_NAME.lower()


def id_number(element_id):
    try:
        return int(element_id.Value)
    except Exception:
        return int(element_id.IntegerValue)


def element_name(element):
    try:
        return unicode(DB.Element.Name.GetValue(element))
    except Exception:
        return unicode(element.Name)


def geometry_material_fingerprint(doc):
    """Immutable-element evidence; does not include the changed emitter web.

    The photometric web can legitimately change the light-source graphic.
    Everything else, including imported OEM objects and material definitions,
    must retain the same element ids, bounding boxes and material links.
    """
    classes = [DB.FreeFormElement, DB.ImportInstance, DB.FamilyInstance]
    entries = {}
    for cls in classes:
        found = []
        for item in DB.FilteredElementCollector(doc).OfClass(cls):
            category = item.Category
            category_name = str(category.Name) if category else ''
            if category_name.lower() == 'light source':
                continue
            bounds = item.get_BoundingBox(None)
            bbox = None
            if bounds is not None:
                bbox = [round(float(v), 8) for v in
                        (bounds.Min.X, bounds.Min.Y, bounds.Min.Z,
                         bounds.Max.X, bounds.Max.Y, bounds.Max.Z)]
            mids = sorted(id_number(mid) for mid in item.GetMaterialIds(False))
            found.append((id_number(item.Id), category_name, bbox, mids))
        entries[str(cls.Name)] = sorted(found, key=lambda row: row[0])
    materials = []
    for mat in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        color = mat.Color
        materials.append((id_number(mat.Id), element_name(mat),
                          (int(color.Red), int(color.Green), int(color.Blue)),
                          int(mat.Transparency), id_number(mat.AppearanceAssetId)))
    return {'geometry': entries,
            'materials': sorted(materials, key=lambda row: row[0])}


def photometric_cache_info(fm):
    """Optional cache fingerprint; presence alone cannot prove portability."""
    try:
        param = fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE_CACHE)
        if param is None:
            return {'present': False}
        if str(param.StorageType) != 'String':
            return {'present': True, 'storage': str(param.StorageType)}
        value = fm.CurrentType.AsString(param)
        if value is None or len(value) == 0:
            return {'present': True, 'storage': 'String', 'populated': False}
        # Cache may be binary-esque .NET text; do not print or copy its bytes.
        return {'present': True, 'storage': 'String',
                'populated': True, 'length': len(value)}
    except Exception as exc:
        return {'inspect_error': type(exc).__name__}


def read_photo(doc, need_writable):
    require(doc.IsFamilyDocument, 'Input is not a Revit family')
    require(str(doc.OwnerFamily.FamilyCategory.Name) == 'Lighting Fixtures',
            'Input is not in Lighting Fixtures category')
    fm = doc.FamilyManager
    types = list(fm.Types)
    require(len(types) == 1 and str(types[0].Name) == EXPECTED_TYPE,
            'Expected exactly one Bolla family Type 1; no type changes permitted')
    require(fm.CurrentType is not None and
            str(fm.CurrentType.Name) == EXPECTED_TYPE,
            'Active Bolla family type unexpectedly changed')
    param = fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
    require(param is not None, 'FBX_LIGHT_PHOTOMETRIC_FILE parameter unavailable')
    require(str(param.StorageType) == 'String' and not param.IsInstance,
            'Photometric Web File is not an editable family type string')
    require((not need_writable) or not param.IsReadOnly,
            'Photometric Web File parameter read-only')
    if need_writable:
        require(not param.Formula, 'Photometric Web File controlled by formula')
    type_path = fm.CurrentType.AsString(param)
    require(type_path is not None and str(type_path).strip(),
            'Family type Photometric Web File cannot be read')
    light_family = DB.Lighting.LightFamily.GetLightFamily(doc)
    require(light_family is not None, 'No Revit LightFamily API light source')
    count = int(light_family.GetNumberOfLightTypes())
    require(count == 1, 'Expected exactly one native light-source type; found '+str(count))
    light_type = light_family.GetLightType(0)
    require(light_type is not None, 'Cannot retrieve LightType(0)')
    distribution = light_type.GetLightDistribution()
    require(isinstance(distribution, DB.Lighting.PhotometricWebLightDistribution),
            'Existing light is not PhotometricWeb; refusing distribution-style change')
    distribution_path = distribution.PhotometricWebFile
    require(distribution_path is not None and str(distribution_path).strip(),
            'PhotometricWebLightDistribution filename unreadable')
    return {
        'fm': fm, 'type_param': param, 'light_type': light_type,
        'distribution': distribution, 'type_path': str(type_path),
        'distribution_path': str(distribution_path),
        'cache': photometric_cache_info(fm),
    }


def verify_binding(inspection):
    require(has_exact_bg_name(inspection['type_path']),
            'Saved Photometric Web File type parameter does not point to PD3106-BG')
    require(has_exact_bg_name(inspection['distribution_path']),
            'Saved LightType distribution does not point to PD3106-BG')


def guard_manufacturer_ies():
    require(os.path.isfile(IES), 'Official PD3106-BG IES missing')
    require(os.stat(IES).st_size == EXPECTED_IES_BYTES, 'Unexpected IES size')
    require(sha256(IES) == IES_SHA256, 'IES SHA-256 no longer official validated file')
    with open(IES, 'rb') as stream:
        ies_start = stream.read(4000)
    require(b'IESNA:LM-63-2002' in ies_start and b'TILT=NONE' in ies_start,
            'IES photometric header absent')
    require(os.path.isfile(IES_MANIFEST), 'Photometry manifest missing')
    with open(IES_MANIFEST, 'rb') as stream:
        entries = json.load(stream)['fixtures']
    matches = [item for item in entries if item.get('sku') == 'KZC1353667']
    require(len(matches) == 1, 'Photometry manifest Bolla entry ambiguous')
    row = matches[0]
    require(row.get('model') == 'PD3106-BG' and
            row.get('source_zip_url') == IES_URL and
            row.get('ies_sha256') == IES_SHA256 and
            row.get('status') == 'VALID_IES_MODEL_MATCH' and
            row.get('lm63', {}).get('valid') is True,
            'Photometry manifest source/variant/LM-63 validation mismatch')


def save_receipt_once(receipt):
    parent = os.path.dirname(RECEIPT)
    if not os.path.isdir(parent):
        os.makedirs(parent)
    descriptor = os.open(RECEIPT, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
    with os.fdopen(descriptor, 'w') as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True, ensure_ascii=True)
        stream.write('\n')


def main():
    require(sys.version_info[0] == 2, 'This source requires IronPython 2.7')
    try:
        app = __revit__.Application
    except NameError:
        raise RuntimeError('Run in an isolated pyRevit 2025 process')
    require(str(app.VersionNumber) == '2025', 'Revit 2025 required')
    require(os.path.isfile(SOURCE), 'Expected existing Bolla source RFA missing')
    require(os.stat(SOURCE).st_size == EXPECTED_RFA_BYTES,
            'Existing source Bolla RFA byte length changed')
    require(sha256(SOURCE) == SOURCE_SHA256,
            'Bolla source SHA-256 mismatch; investigate before modifying')
    guard_manufacturer_ies()
    require(not os.path.lexists(TARGET), 'R02 candidate already exists')
    require(not os.path.lexists(RECEIPT), 'R02 receipt already exists')
    require(os.path.normcase(os.path.abspath(SOURCE)) !=
            os.path.normcase(os.path.abspath(TARGET)), 'Source and target identical')
    candidate_folder = os.path.dirname(TARGET)
    if not os.path.isdir(candidate_folder):
        os.makedirs(candidate_folder)
    stage = os.path.join(candidate_folder,
                         '_stage_bolla_bg_ies_' + uuid.uuid4().hex + '.rfa')
    require(not os.path.lexists(stage), 'Unexpected temporary path collision')
    original_hash = sha256(SOURCE)

    opened = None
    reopened = None
    transaction = None
    promoted = False
    try:
        opened = app.OpenDocumentFile(SOURCE)
        before = read_photo(opened, need_writable=True)
        # OEM generic family currently points to the CH IES. Fail closed if
        # native source no longer displays that expected prior assignment.
        previous_references = (before['type_path'], before['distribution_path'])
        require(not any(has_exact_bg_name(p) for p in previous_references),
                'Family already references PD3106-BG; do not issue redundant candidate')
        require(any('CH' in name_only(p).upper() and '.ies' in name_only(p)
                    for p in previous_references),
                'Prior OEM CH IES reference not confirmed; source review required')
        untouched = geometry_material_fingerprint(opened)
        old_warnings = sorted(str(w.GetDescriptionText()) for w in opened.GetWarnings())
        old_cache = before['cache']

        transaction = DB.Transaction(opened,
                                     'Bind verified Kuzco PD3106-BG OEM photometric web')
        require(transaction.Start() == DB.TransactionStatus.Started,
                'Could not start RFA transaction')
        # Autodesk API 2025: update the actual LightType distribution.
        # Do not call SetLightDistributionStyle: source already PhotometricWeb.
        distribution = before['distribution']
        distribution.PhotometricWebFile = IES
        before['light_type'].SetLightDistribution(distribution)
        # The family type parameter can otherwise retain the old path.
        before['fm'].Set(before['type_param'], IES)
        opened.Regenerate()
        verify_binding(read_photo(opened, need_writable=True))
        require(geometry_material_fingerprint(opened) == untouched,
                'Material or non-emitter geometry changed unexpectedly')
        new_warnings = sorted(str(w.GetDescriptionText()) for w in opened.GetWarnings())
        require(new_warnings == old_warnings, 'New Revit warning after IES binding')
        require(transaction.Commit() == DB.TransactionStatus.Committed,
                'Photometric IES transaction failed')
        transaction = None

        options = DB.SaveAsOptions()
        options.OverwriteExistingFile = False
        options.MaximumBackups = 1
        opened.SaveAs(stage, options)
        opened.Close(False)
        opened = None
        require(os.path.isfile(stage), 'Revit staged SaveAs did not create RFA')

        # Both readback interfaces MUST survive a clean close and reopen.
        reopened = app.OpenDocumentFile(stage)
        saved = read_photo(reopened, need_writable=False)
        verify_binding(saved)
        require(geometry_material_fingerprint(reopened) == untouched,
                'Saved family material/geometry fingerprint differs from source')
        stage_warnings = sorted(str(w.GetDescriptionText())
                                for w in reopened.GetWarnings())
        require(stage_warnings == old_warnings, 'Saved RFA warning set changed')
        new_cache = saved['cache']
        # A present cache cannot be presumed to hold the new IES. If Revit
        # exposes two nonempty equal lengths, no byte-level equivalence is
        # provable; companion IES remains mandatory for portability.
        reopened.Close(False)
        reopened = None

        require(sha256(SOURCE) == original_hash, 'Original Bolla source bytes changed')
        require(not os.path.lexists(TARGET), 'Candidate appeared during validation')
        validated_stage_hash = sha256(stage)
        os.rename(stage, TARGET)   # no overwrite on Windows
        promoted = True
        require(sha256(TARGET) == validated_stage_hash,
                'Promoted output does not match validated staged RFA')
        receipt = {
            'status': 'REOPEN_VERIFIED_IES_BINDING_PENDING_RENDER_AND_PORTABILITY_QA',
            'revit_version': '2025',
            'model': 'PD3106-BG',
            'source_rfa': SOURCE,
            'source_rfa_sha256': original_hash,
            'candidate_rfa': TARGET,
            'candidate_rfa_sha256': validated_stage_hash,
            'original_type_parameter': before['type_path'],
            'original_light_distribution': before['distribution_path'],
            'reopened_type_parameter': saved['type_path'],
            'reopened_light_distribution': saved['distribution_path'],
            'source_ies': IES,
            'source_ies_sha256': IES_SHA256,
            'official_ies_archive': IES_URL,
            'geometry_and_materials_unchanged': True,
            'source_preserved': True,
            'cache_before': old_cache,
            'cache_reopened': new_cache,
            'embedded_cache_verified': False,
            'companion_ies_required_for_portability': True,
            'native_qa': 'Saved-and-reopened binding only; hosting/lighting render pending',
        }
        save_receipt_once(receipt)
        print('BOLLA_BG_IES_R02 SAVED_REOPEN_VERIFIED')
        print('CANDIDATE_RFA: ' + TARGET)
        print('COMPANION_IES: ' + IES)
        print('RECEIPT: ' + RECEIPT)
    finally:
        if transaction is not None:
            try:
                transaction.RollBack()
            except Exception:
                pass
        for doc in (reopened, opened):
            if doc is not None:
                try:
                    doc.Close(False)
                except Exception:
                    pass
        # Only own unique stage is removed after unsuccessful validation;
        # source, OEM IES and existing candidate files are never deleted.
        if not promoted and os.path.isfile(stage):
            try:
                os.unlink(stage)
            except Exception:
                pass


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('BOLLA_BG_IES_R02_FAILED: ' + traceback.format_exc())
        raise
