# -*- coding: utf-8 -*-
"""Bind EXACT official FR-W2502-52L.IES to existing Smooth SB/MB R02.

Run ONLY in isolated Revit 2025 IronPython 2.7 (prime agent):

  pyrevit run "E:\\Claude\\3D-Model-Workflow\\output\\belmont_ph_good_rfa_20261016\\scripts\\bind_smooth_frw2502_r03_exact_ies.py" --revit=2025

Fail closed BEFORE edit unless the R02 family contains a REAL native
DB.Lighting.LightFamily, exactly one native LightType, a
PhotometricWebLightDistribution and a writable native photometric type
parameter. A filename string alone does not authorize an IES update.

Strict source SHA checks, immutable geometry/finishes, staged save/reopen,
separate R03 candidate and separate native receipt. No active user RVT.
Only prime may execute native Revit. No CCT/finish-specific photometry claimed.
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
SOURCE = os.path.join(BASE, 'candidates',
    'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R02_PARTIAL_UNAPPROVED.rfa')
IES = os.path.join(BASE, 'sources', 'photometry', 'FR-W2502-52L.IES')
VALIDATION = os.path.join(BASE, 'qa',
    'smooth_frw2502_ies_source_validation_20261016.json')
R02_NATIVE_QA = os.path.join(BASE, 'qa', 'smooth_sbmb_r02_native_qa.json')
TARGET = os.path.join(BASE, 'candidates',
    'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R03_IES_UNAPPROVED.rfa')
RECEIPT = os.path.join(BASE, 'qa', 'smooth_sbmb_r03_ies_native_bind_receipt.json')

SOURCE_SHA = 'f1741c711a07a26101c550b580a2db6be99bc4d3689cb75104eaafb0834379db'
IES_SHA = '6044dda98294020d03decd14ad118be2717845536597d1ca9bb9cc296fdcda8e'
VALIDATION_SHA = 'b9d8836a641a1c4e6b912d5aabe36f7d738110a389e615f61e9f38c2c3b7c622'
R02_QA_SHA = '2ea2921f50d0bff745f5693c1e3a3eb6be1e79af3ed2d8462e2e03f2248b0d08'
EXPECTED_IES_NAME = 'FR-W2502-52L.IES'
OFFICIAL_URL = 'https://modernforms.com/images/products/IES_FILES/FR-W2502-52_IES.zip'
EXPECTED_BLACK_MAT = 'PH GOOD Smooth MB ABS Blades R02 Provisional'
EXPECTED_BRASS_MAT = 'PH GOOD Smooth SB Housing R02 Provisional'
EXPECTED_MAT_IDS = {'blade': 3370, 'housing': 3372}
GEOMETRY_CLASSES = (DB.FreeFormElement, DB.ImportInstance, DB.FamilyInstance)


def require(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def elem_id(value):
    try:
        return int(value.Value)
    except Exception:
        return int(value.IntegerValue)


def elem_name(value):
    try:
        return unicode(DB.Element.Name.GetValue(value))
    except Exception:
        return unicode(value.Name)


def basename(value):
    return os.path.basename(str(value or '').replace('\\', '/'))


def exact_name(value):
    return basename(value).lower() == EXPECTED_IES_NAME.lower()


def inspect_sources():
    expected = [(SOURCE, SOURCE_SHA), (IES, IES_SHA),
                (VALIDATION, VALIDATION_SHA), (R02_NATIVE_QA, R02_QA_SHA)]
    for path, expected_hash in expected:
        require(os.path.isfile(path), 'Missing immutable input: ' + path)
        require(digest(path) == expected_hash,
                'Protected input hash changed; refusing native edit: ' + path)
    with open(VALIDATION, 'rb') as stream:
        manifest = json.load(stream)
    require(manifest.get('status') ==
            'EXACT_MANUFACTURER_LM63_VALIDATED_NATIVE_REVIT_BINDING_PENDING',
            'Official LM-63 source manifest is not validated')
    require(manifest.get('official_archive_url') == OFFICIAL_URL and
            manifest.get('ies_sha256') == IES_SHA and
            manifest.get('base_model') == 'FR-W2502-52L',
            'Official photometric manifest source or model mismatch')
    lm = manifest['ies_validation']
    require(lm.get('valid') is True and lm['header_tags'].get('MANUFAC') ==
            'WAC Lighting' and lm['header_tags'].get('LUMINAIRE') == 'FR-W2502-52L',
            'Official LM-63 source does not identify the exact Smooth model')
    require(abs(float(lm['lamp_lumens']) - 707.0) <= .2 and
            abs(float(lm['test_input_watts']) - 16.0) <= 1.0 and
            lm['candela_samples'] == 181 * 17,
            'Official lumens, test watts or candela grid mismatch')
    with open(IES, 'rb') as stream:
        header = stream.read(600).decode('ascii')
    require('IESNA:LM-63-2002' in header and
            '[LUMINAIRE] FR-W2502-52L' in header and
            '[MANUFAC] WAC Lighting' in header and 'TILT=NONE' in header,
            'Exact IES header changed')
    with open(R02_NATIVE_QA, 'rb') as stream:
        qa = json.load(stream)
    require(qa.get('status') == 'NATIVE_MATERIAL_AND_SWEEP_PASS_VISUAL_HOLD',
            'R02 manufacturer finish and radial native QA has not passed')
    require(qa['input_shas'].get(SOURCE) == SOURCE_SHA and
            qa['placed']['radial']['passed'] is True and
            qa['material']['matte_black_id'] == EXPECTED_MAT_IDS['blade'] and
            qa['material']['soft_brass_id'] == EXPECTED_MAT_IDS['housing'],
            'R02 QA does not match actual source candidate and material binding')
    return lm


def stable_geometry_and_material_state(doc):
    """Structural source fingerprint ignoring Revit's light-source geometry.

    Optical changes may update the light graphic; imported CAD, the actual
    fan blades/housing, non-light family instances, material definitions and
    their bounding boxes must remain byte-for-byte equal in these records.
    """
    result = {}
    for cls in GEOMETRY_CLASSES:
        items = []
        for element in DB.FilteredElementCollector(doc).OfClass(cls):
            category = elem_name(element.Category) if element.Category else ''
            if category.lower() == 'light source':
                continue
            bbox = element.get_BoundingBox(None)
            extent = None
            if bbox is not None:
                extent = [round(float(a), 8) for a in
                          (bbox.Min.X, bbox.Min.Y, bbox.Min.Z,
                           bbox.Max.X, bbox.Max.Y, bbox.Max.Z)]
            mids = sorted(elem_id(mid) for mid in element.GetMaterialIds(False))
            items.append([elem_id(element.Id), category, extent, mids])
        result[str(cls.Name)] = sorted(items, key=lambda row: row[0])
    materials = []
    for material in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        color = material.Color
        materials.append([elem_id(material.Id), elem_name(material),
                          [int(color.Red), int(color.Green), int(color.Blue)],
                          int(material.Transparency), elem_id(material.AppearanceAssetId)])
    result['materials'] = sorted(materials, key=lambda row: row[0])
    result['family_category'] = elem_name(doc.OwnerFamily.FamilyCategory)
    result['placement_type'] = str(doc.OwnerFamily.FamilyPlacementType)
    result['family_types'] = sorted(str(t.Name) for t in doc.FamilyManager.Types)
    return result


def light_cache_state(fm):
    try:
        p = fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE_CACHE)
        if p is None:
            return {'available': False}
        if str(p.StorageType) != 'String':
            return {'available': True, 'storage': str(p.StorageType)}
        value = fm.CurrentType.AsString(p) or ''
        # Deliberately do not emit potentially binary cached payload.
        return {'available': True, 'storage': 'String',
                'populated': bool(value), 'length': len(value)}
    except Exception as exc:
        return {'error': type(exc).__name__}


def read_native_light(doc, require_writable):
    require(doc.IsFamilyDocument, 'Source candidate must be FamilyDocument')
    require(elem_name(doc.OwnerFamily.FamilyCategory) == 'Lighting Fixtures',
            'Wrong family category; no emitter conversion authorized')
    require(str(doc.OwnerFamily.FamilyPlacementType) == 'WorkPlaneBased',
            'Smooth family placement changed')
    types = list(doc.FamilyManager.Types)
    require(len(types) == 1, 'Expected one OEM Smooth type, got %d' % len(types))
    fm = doc.FamilyManager
    require(fm.CurrentType is not None, 'Smooth type not active')
    param = fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
    require(param is not None and not param.IsInstance and
            str(param.StorageType) == 'String',
            'BLOCKED_UNSUPPORTED_FAMILY_PARAM: no native type photometric web string')
    if require_writable:
        require(not param.IsReadOnly and not param.Formula,
                'BLOCKED_READ_ONLY_PHOTOMETRIC_TYPE: cannot write native param')
    prior = fm.CurrentType.AsString(param) or ''
    require(exact_name(prior),
            'Expected OEM Photometric Web File filename FR-W2502-52L.IES')

    # Core safety gate: the presence of element 3044 and a web filename is NOT
    # enough. A real native LightFamily / LightType must accept photometry.
    try:
        light_family = DB.Lighting.LightFamily.GetLightFamily(doc)
    except Exception as exc:
        raise RuntimeError('BLOCKED_NO_REAL_LIGHT_FAMILY: ' + str(exc))
    require(light_family is not None,
            'BLOCKED_NO_REAL_LIGHT_FAMILY: source template lacks emitter API')
    count = int(light_family.GetNumberOfLightTypes())
    require(count == 1,
            'BLOCKED_NATIVE_LIGHT_TYPE_COUNT: expected 1; got %d' % count)
    light_type = light_family.GetLightType(0)
    require(light_type is not None, 'BLOCKED_NO_NATIVE_LIGHT_TYPE')
    distribution = light_type.GetLightDistribution()
    require(isinstance(distribution, DB.Lighting.PhotometricWebLightDistribution),
            'BLOCKED_LIGHT_DISTRIBUTION_NOT_WEB: refusing to change emission geometry')
    previous_distribution = str(distribution.PhotometricWebFile or '')
    require(not previous_distribution or exact_name(previous_distribution),
            'Existing native LightType distribution is for a different fixture')

    return {'fm': fm, 'type_param': param, 'native_type': light_type,
            'distribution': distribution, 'type_name': str(fm.CurrentType.Name),
            'type_path': str(prior), 'distribution_path': previous_distribution,
            'cache': light_cache_state(fm), 'light_type_count': count}


def assert_bound(state):
    require(exact_name(state['type_path']),
            'Revit type photometric param filename not exact OEM model')
    require(exact_name(state['distribution_path']),
            'Revit LightType distribution not bound to exact OEM file')
    # Save/reopen must preserve the bound path, including the folder that
    # contains the companion LM63 file until cache portability is audited.
    require(os.path.normcase(os.path.abspath(state['distribution_path'])) ==
            os.path.normcase(os.path.abspath(IES)),
            'Native Revit LightType distribution lost companion IES absolute path')


def receipt_once(report):
    require(not os.path.lexists(RECEIPT),
            'Refusing overwrite of R03 native binder receipt')
    fd = os.open(RECEIPT, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, 'w') as f:
        json.dump(report, f, indent=2, sort_keys=True, ensure_ascii=True)
        f.write('\n')


def main():
    require(sys.version_info[0] == 2, 'Use IronPython 2.7')
    app = __revit__.Application
    require(str(app.VersionNumber) == '2025', 'Revit 2025 required')
    require(getattr(__revit__, 'ActiveUIDocument', None) is None,
            'Use isolated pyRevit process without open user RVT')
    require(not os.path.lexists(TARGET) and not os.path.lexists(RECEIPT),
            'R03 candidate or receipt exists; no overwrites allowed')
    lm = inspect_sources()
    src_hash_before = digest(SOURCE)
    ies_hash_before = digest(IES)
    stage = os.path.join(BASE, 'candidates',
                         '_stage_smooth_ies_' + uuid.uuid4().hex + '.rfa')
    require(not os.path.lexists(stage), 'Stage path collision')

    doc = None
    reopened = None
    tx = None
    promoted = False
    report = {'status': 'STARTED', 'model': 'FR-W2502-52L',
              'finish': 'SB/MB', 'source': SOURCE, 'source_sha256': SOURCE_SHA,
              'ies': IES, 'ies_sha256': IES_SHA,
              'manufacturer_archive_url': OFFICIAL_URL,
              'validation_manifest_sha256': VALIDATION_SHA,
              'r02_native_qa_sha256': R02_QA_SHA,
              'ies_test_lumens': lm['lamp_lumens'],
              'ies_test_input_watts': lm['test_input_watts'],
              'output': TARGET, 'revit_version': '2025'}
    try:
        doc = app.OpenDocumentFile(SOURCE)
        before = read_native_light(doc, require_writable=True)
        expected_physical = stable_geometry_and_material_state(doc)
        require(expected_physical['placement_type'] == 'WorkPlaneBased',
                'Family placement changed')
        require(any(row[1] == EXPECTED_BLACK_MAT
                    for row in expected_physical['materials']),
                'R02 Black blade material missing')
        require(any(row[1] == EXPECTED_BRASS_MAT
                    for row in expected_physical['materials']),
                'R02 Brass housing material missing')
        original_warnings = sorted(str(w.GetDescriptionText())
                                   for w in doc.GetWarnings())
        require(not original_warnings, 'R02 source has native warnings')
        report['source_type_web'] = before['type_path']
        report['source_light_type_web'] = before['distribution_path']
        report['source_light_family_type_count'] = before['light_type_count']
        report['source_cache_state'] = before['cache']

        # All API capability checks above are complete before transaction.
        tx = DB.Transaction(doc, 'Bind exact official FR-W2502-52L LM63')
        require(tx.Start() == DB.TransactionStatus.Started,
                'Could not begin Revit family edit')
        before['distribution'].PhotometricWebFile = IES
        before['native_type'].SetLightDistribution(before['distribution'])
        before['fm'].Set(before['type_param'], IES)
        doc.Regenerate()
        candidate_state = read_native_light(doc, require_writable=True)
        assert_bound(candidate_state)
        require(stable_geometry_and_material_state(doc) == expected_physical,
                'Existing fan geometry or blade/housing materials changed')
        require(sorted(str(w.GetDescriptionText()) for w in doc.GetWarnings()) ==
                original_warnings, 'IES assignment introduced a Revit warning')
        require(tx.Commit() == DB.TransactionStatus.Committed,
                'IES Revit transaction failed')
        tx = None

        opts = DB.SaveAsOptions()
        opts.OverwriteExistingFile = False
        opts.MaximumBackups = 1
        require(not os.path.lexists(stage), 'Stage path appeared unexpectedly')
        doc.SaveAs(stage, opts)
        doc.Close(False)
        doc = None
        require(os.path.isfile(stage), 'Revit staged RFA missing after SaveAs')
        reopened = app.OpenDocumentFile(stage)
        saved = read_native_light(reopened, require_writable=False)
        assert_bound(saved)
        require(stable_geometry_and_material_state(reopened) == expected_physical,
                'Saved R03 native geometry/material fingerprint does not match R02')
        require(sorted(str(w.GetDescriptionText()) for w in reopened.GetWarnings()) ==
                original_warnings, 'Saved R03 family produced warnings')
        reopened.Close(False)
        reopened = None
        require(digest(SOURCE) == src_hash_before and digest(IES) == ies_hash_before,
                'Source RFA or official IES altered during native build')
        require(not os.path.lexists(TARGET), 'Final R03 path appeared unexpectedly')
        stage_hash = digest(stage)
        os.rename(stage, TARGET)
        promoted = True
        require(digest(TARGET) == stage_hash,
                'Promoted R03 candidate differs from validated staged file')
        report.update({
            'status': 'NATIVE_LIGHT_FAMILY_PHOTOMETRIC_WEB_BOUND_REOPEN_PASS',
            'candidate_sha256': stage_hash,
            'saved_type_web': saved['type_path'],
            'saved_light_type_web': saved['distribution_path'],
            'saved_cache_state': saved['cache'],
            'geometry_and_r02_blade_housing_materials_unchanged': True,
            'source_r02_unchanged': True,
            'independent_placed_sweep_qa': 'PENDING',
            'realistic_render_qa': 'PENDING',
            'physical_cct_and_finish_specific_distribution': 'NOT_ESTABLISHED',
            'companion_ies_required_for_portability': True,
        })
    except Exception:
        report['status'] = 'BLOCKED_OR_ERROR_NO_RELEASE'
        report['error'] = traceback.format_exc()
    finally:
        if tx is not None:
            try:
                tx.RollBack()
            except Exception:
                pass
        for opened in (reopened, doc):
            if opened is not None:
                try:
                    opened.Close(False)
                except Exception:
                    pass
        if not promoted and os.path.isfile(stage):
            try:
                os.unlink(stage)
            except Exception:
                pass
        report['protected_source_sha256_after'] = digest(SOURCE)
        report['official_ies_sha256_after'] = digest(IES)
        report['source_unchanged'] = report['protected_source_sha256_after'] == SOURCE_SHA
        report['official_ies_unchanged'] = report['official_ies_sha256_after'] == IES_SHA
        if not report['source_unchanged'] or not report['official_ies_unchanged']:
            report['status'] = 'FAIL_PROTECTED_INPUT_CHANGED'
        receipt_once(report)
        print('SMOOTH_R03_IES: ' + report['status'])
        print('RECEIPT: ' + RECEIPT)
        if promoted:
            print('R03_CANDIDATE: ' + TARGET)
    require(report['status'] == 'NATIVE_LIGHT_FAMILY_PHOTOMETRIC_WEB_BOUND_REOPEN_PASS',
            report.get('error', 'Smooth exact IES R03 did not pass native checks'))


main()
