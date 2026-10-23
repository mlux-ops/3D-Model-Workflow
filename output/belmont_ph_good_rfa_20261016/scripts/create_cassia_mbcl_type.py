# -*- coding: utf-8 -*-
"""Create an isolated Alora Cassia LP549448MBCL Revit 2025 R02 candidate.

Run with IronPython 2.7 in a separate Revit 2025 pyRevit process:

    pyrevit run "E:\\Claude\\3D-Model-Workflow\\output\\belmont_ph_good_rfa_20261016\\scripts\\create_cassia_mbcl_type.py" --revit=2025

Source OEM type LP549448MBOP (Matte Black / Opal) is duplicated to the
manufacturer-listed LP549448MBCL (Matte Black / Clear). Its type-level
GLASS_COLOR material reference changes to a newly created material and
independently cloned Glass (Clear) appearance asset. METAL_FINISH remains
CASSIA_MB_FINISH. Original types and source RFA are left intact.

No fixture geometry, nested families, photometry or user RVT is edited.
Requires independent geometry/placement/visual acceptance after the build.
"""
from __future__ import print_function

import hashlib
import json
import os
import sys
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB


BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SOURCE = os.path.join(BASE, 'families',
                      'Alora_Cassia_LP549448MBCL_R2025.rfa')
TARGET = os.path.join(BASE, 'candidates',
                      'Alora_Cassia_LP549448MBCL_R2025_R02.rfa')
RECEIPT = os.path.join(BASE, 'qa', 'cassia_mbcl_r02_build.json')

# Independent 2026-10-16 OEM QA receipt, for the existing family copy.
EXPECTED_SOURCE_SHA256 = '27ce97b87c28cabaf249ebc4410ce9bf1b387e16a2232e2fc29e153530c09ac3'
SOURCE_TYPE = 'LP549448MBOP'
NEW_TYPE = 'LP549448MBCL'
OTHER_TYPE = 'LP549448AGOP'
GLASS_PARAM = 'GLASS_COLOR'
METAL_PARAM = 'METAL_FINISH'
OPAL_NAME = 'CASSIA_OPAL_GLASS'
BLACK_NAME = 'CASSIA_MB_FINISH'
CLEAR_REFERENCE_NAME = 'BULB_GLASS'
NEW_MATERIAL_NAME = 'CASSIA_CLEAR_GLASS_MBCL'
NEW_APPEARANCE_NAME = 'Cassia Clear Glass LP549448MBCL'
SHADED_TRANSPARENCY = 95


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def element_name(element):
    # Explicit Element.Name descriptor also works on pyRevit IPY2712PR.
    try:
        return str(DB.Element.Name.GetValue(element))
    except Exception:
        return str(element.Name)


def type_by_name(manager, name):
    for family_type in manager.Types:
        if str(family_type.Name) == name:
            return family_type
    return None


def parameter_by_name(manager, name):
    for parameter in manager.Parameters:
        if str(parameter.Definition.Name) == name:
            return parameter
    raise RuntimeError('Required type parameter absent: ' + name)


def material_by_name(doc, name):
    for material in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        if element_name(material) == name:
            return material
    return None


def material_at_type(doc, family_type, parameter):
    material_id = family_type.AsElementId(parameter)
    material = doc.GetElement(material_id)
    check(isinstance(material, DB.Material),
          'Type material is not bound: ' + str(parameter.Definition.Name))
    return material


def parameter_value(family_type, parameter):
    """Read a type parameter with its native .NET value for lossless copying."""
    storage = str(parameter.StorageType)
    if storage == 'ElementId':
        return family_type.AsElementId(parameter)
    if storage == 'Double':
        return family_type.AsDouble(parameter)
    if storage == 'Integer':
        return family_type.AsInteger(parameter)
    if storage == 'String':
        return family_type.AsString(parameter)
    return None


def equal_value(left, right, storage):
    if left is None or right is None:
        return left is None and right is None
    if storage == 'ElementId':
        return bool(left.Equals(right))
    if storage == 'Double':
        return abs(float(left) - float(right)) <= 1e-9
    return left == right


def preserve_original_type_parameters(manager, original, new_type):
    """Repair any missing NewType defaults before changing the two finishes.

    Autodesk documents cases where Revit loses type metadata on duplication.
    This explicitly compares all editable type parameters, including rod
    lengths, electrical fields, IFC metadata, model number and wattage notes.
    """
    restored = []
    manager.CurrentType = new_type
    for parameter in manager.Parameters:
        if parameter.IsInstance:
            continue
        name = str(parameter.Definition.Name)
        if name in (GLASS_PARAM, METAL_PARAM):
            continue
        storage = str(parameter.StorageType)
        if storage not in ('ElementId', 'Double', 'Integer', 'String'):
            continue
        original_value = parameter_value(original, parameter)
        current_value = parameter_value(new_type, parameter)
        if equal_value(original_value, current_value, storage):
            continue
        formula = parameter.Formula
        check(not parameter.IsReadOnly and not formula,
              'Cannot copy read-only/formula type parameter: ' + name)
        check(original_value is not None,
              'Cannot restore a null source value for: ' + name)
        manager.Set(parameter, original_value)
        check(equal_value(parameter_value(new_type, parameter),
                          original_value, storage),
              'Copied type parameter did not match source: ' + name)
        restored.append(name)
    return restored


def inspect_finish(doc, type_name, glass_param, metal_param):
    family_type = type_by_name(doc.FamilyManager, type_name)
    check(family_type is not None, 'Family type missing: ' + type_name)
    glass = material_at_type(doc, family_type, glass_param)
    metal = material_at_type(doc, family_type, metal_param)
    asset = doc.GetElement(glass.AppearanceAssetId)
    check(isinstance(asset, DB.AppearanceAssetElement),
          'Glass does not reference an appearance asset: ' + type_name)
    return {
        'type': type_name,
        'glass_material': element_name(glass),
        'glass_transparency': int(glass.Transparency),
        'glass_appearance': element_name(asset),
        'metal_material': element_name(metal),
        'metal_transparency': int(metal.Transparency)
    }


def validate_family(doc):
    check(doc.IsFamilyDocument, 'Saved output must be a FamilyDocument')
    category = element_name(doc.OwnerFamily.FamilyCategory)
    check(category == 'Lighting Fixtures', 'Unexpected family category: ' + category)
    check(str(doc.OwnerFamily.FamilyPlacementType) == 'OneLevelBasedHosted',
          'Unexpected family placement type (source was OneLevelBasedHosted)')
    manager = doc.FamilyManager
    glass_param = parameter_by_name(manager, GLASS_PARAM)
    metal_param = parameter_by_name(manager, METAL_PARAM)
    check(not glass_param.IsInstance and not metal_param.IsInstance,
          'Both finish controls must be type-level parameters')
    check(str(glass_param.StorageType) == 'ElementId' and
          str(metal_param.StorageType) == 'ElementId',
          'Finish controls must be Material ElementId parameters')
    source_finish = inspect_finish(doc, SOURCE_TYPE, glass_param, metal_param)
    other_finish = inspect_finish(doc, OTHER_TYPE, glass_param, metal_param)
    new_finish = inspect_finish(doc, NEW_TYPE, glass_param, metal_param)
    check(source_finish['glass_material'] == OPAL_NAME and
          source_finish['metal_material'] == BLACK_NAME,
          'Original Matte Black / Opal type changed unexpectedly')
    check(other_finish['glass_material'] == OPAL_NAME and
          other_finish['metal_material'] == 'CASSIA_AG-FINISH',
          'Original Aged Gold / Opal type changed unexpectedly')
    check(new_finish['glass_material'] == NEW_MATERIAL_NAME and
          new_finish['metal_material'] == BLACK_NAME,
          'New material or preserved black finish is not bound')
    check(new_finish['glass_transparency'] == SHADED_TRANSPARENCY and
          new_finish['glass_appearance'] == NEW_APPEARANCE_NAME,
          'Clear glass transparency/appearance did not survive reopen')
    check(new_finish['metal_transparency'] == 0,
          'Matte black became transparent')
    check(len(list(manager.Types)) == 3, 'Expected exactly three OEM types')
    warning_count = len(list(doc.GetWarnings()))
    check(warning_count == 0, 'Saved RFA contains %d warning(s)' % warning_count)
    return {
        'category': category,
        'placement_type': str(doc.OwnerFamily.FamilyPlacementType),
        'type_names': sorted(str(item.Name) for item in manager.Types),
        'source_mbop': source_finish,
        'source_agop': other_finish,
        'candidate_mbcl': new_finish,
        'warning_count': warning_count
    }


def save_receipt_once(data):
    check(not os.path.lexists(RECEIPT), 'Build receipt exists: ' + RECEIPT)
    temporary = RECEIPT + '.tmp'
    check(not os.path.lexists(temporary), 'Receipt temporary file exists: ' + temporary)
    with open(temporary, 'w') as stream:
        json.dump(data, stream, indent=2, sort_keys=True, ensure_ascii=True)
    check(not os.path.lexists(RECEIPT), 'Build receipt appeared during run')
    os.rename(temporary, RECEIPT)


def main():
    check('__revit__' in globals(), 'Run in isolated pyRevit/Revit 2025')
    app = __revit__.Application
    check(str(app.VersionNumber) == '2025', 'Requires native Revit 2025')
    check(getattr(__revit__, 'ActiveUIDocument', None) is None,
          'Use a separate pyrevit run process with no active user model')
    check(os.path.isfile(SOURCE), 'Family source missing: ' + SOURCE)
    check(not os.path.lexists(TARGET), 'Candidate already exists: ' + TARGET)
    check(not os.path.lexists(RECEIPT), 'Candidate receipt already exists: ' + RECEIPT)
    check(os.path.normcase(os.path.abspath(SOURCE)) !=
          os.path.normcase(os.path.abspath(TARGET)),
          'Source and target must differ')
    source_hash_before = sha256(SOURCE)
    check(source_hash_before == EXPECTED_SOURCE_SHA256,
          'Source RFA differs from independently audited OEM family copy')

    output_dir = os.path.dirname(TARGET)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    source_doc = None
    transaction = None
    restored = []
    try:
        source_doc = app.OpenDocumentFile(SOURCE)
        check(source_doc.IsFamilyDocument, 'Source is not a Revit family document')
        original_state = validate_source_before_edit(source_doc)

        transaction = DB.Transaction(source_doc,
                                     'Add Cassia LP549448MBCL clear glass type')
        transaction.Start()
        fm = source_doc.FamilyManager
        source_type = type_by_name(fm, SOURCE_TYPE)
        glass_parameter = parameter_by_name(fm, GLASS_PARAM)
        metal_parameter = parameter_by_name(fm, METAL_PARAM)
        fm.CurrentType = source_type
        original_metal = source_type.AsElementId(metal_parameter)

        bulb_clear = material_by_name(source_doc, CLEAR_REFERENCE_NAME)
        check(bulb_clear is not None, 'Known clear-glass OEM material missing')
        check(int(bulb_clear.Transparency) >= 90,
              'OEM bulb clear-glass material is not highly transparent')
        source_asset = source_doc.GetElement(bulb_clear.AppearanceAssetId)
        check(isinstance(source_asset, DB.AppearanceAssetElement),
              'OEM BULB_GLASS lacks a usable appearance asset')
        check('clear' in element_name(source_asset).lower(),
              'OEM BULB_GLASS appearance is not identified as clear')
        check(material_by_name(source_doc, NEW_MATERIAL_NAME) is None,
              'New clear material name already exists')

        # Independent appearance asset: avoids changing OEM BULB_GLASS render.
        duplicate_asset = source_asset.Duplicate(NEW_APPEARANCE_NAME)
        new_mat_id = DB.Material.Create(source_doc, NEW_MATERIAL_NAME)
        new_mat = source_doc.GetElement(new_mat_id)
        new_mat.Color = DB.Color(245, 245, 243)
        new_mat.Transparency = SHADED_TRANSPARENCY
        new_mat.AppearanceAssetId = duplicate_asset.Id

        # NewType adopts CurrentType; repair unusual missed OEM defaults.
        new_type = fm.NewType(NEW_TYPE)
        check(new_type is not None and str(fm.CurrentType.Name) == NEW_TYPE,
              'FamilyManager did not activate the new type')
        restored = preserve_original_type_parameters(fm, source_type, new_type)
        fm.Set(glass_parameter, new_mat.Id)
        fm.Set(metal_parameter, original_metal)
        check(bool(new_type.AsElementId(glass_parameter).Equals(new_mat.Id)),
              'GLASS_COLOR not bound to new clear material')
        check(bool(new_type.AsElementId(metal_parameter).Equals(original_metal)),
              'METAL_FINISH not preserved from original Matte Black type')
        source_doc.Regenerate()
        check(len(list(source_doc.GetWarnings())) == 0,
              'New family edits introduced warnings')

        status = transaction.Commit()
        transaction = None
        check(status == DB.TransactionStatus.Committed,
              'Revit failed to commit Cassia family changes')
        save_options = DB.SaveAsOptions()
        save_options.OverwriteExistingFile = False
        save_options.MaximumBackups = 1
        check(not os.path.lexists(TARGET), 'Candidate appeared before SaveAs')
        source_doc.SaveAs(TARGET, save_options)
        source_doc.Close(False)
        source_doc = None
    finally:
        if transaction is not None:
            try:
                transaction.RollBack()
            except Exception:
                pass
        if source_doc is not None:
            try:
                source_doc.Close(False)
            except Exception:
                pass

    check(os.path.isfile(TARGET), 'SaveAs did not create candidate RFA')
    check(sha256(SOURCE) == source_hash_before,
          'OEM family source bytes changed unexpectedly')
    saved_doc = app.OpenDocumentFile(TARGET)
    try:
        saved_state = validate_family(saved_doc)
    finally:
        saved_doc.Close(False)

    check(original_state['source_mbop'] == saved_state['source_mbop'],
          'Original MBOP material state altered')
    check(original_state['source_agop'] == saved_state['source_agop'],
          'Original AGOP material state altered')
    receipt = {
        'schema_version': 1,
        'status': 'SAVED_REOPENED_MATERIAL_PASS_PENDING_VISUAL_AND_PLACEMENT_QA',
        'revit_version': '2025',
        'source_rfa': SOURCE,
        'source_sha256': source_hash_before,
        'output_rfa': TARGET,
        'output_sha256': sha256(TARGET),
        'preserved_parameter_values_repaired': restored,
        'glass_shaded_transparency_percent': SHADED_TRANSPARENCY,
        'glass_appearance_source': CLEAR_REFERENCE_NAME,
        'manufacturer_sku': NEW_TYPE,
        'validation': saved_state,
        'source_url': 'https://aloralights.com/products/cassia-linear-suspension/',
        'unverified': ['Hosted placement in a disposable project',
                       'Geometry envelope and nested material face response',
                       'Clear-glass optical appearance in Revit Realistic/render',
                       'IES and light output calibration']
    }
    save_receipt_once(receipt)
    print('CASSIA_MBCL_R02: ' + receipt['status'])
    print('CANDIDATE_RFA: ' + TARGET)
    print('NATIVE_RECEIPT: ' + RECEIPT)


def validate_source_before_edit(doc):
    check(doc.IsFamilyDocument, 'Source not a family document')
    check(element_name(doc.OwnerFamily.FamilyCategory) == 'Lighting Fixtures',
          'Expected Lighting Fixtures OEM family')
    check(str(doc.OwnerFamily.FamilyPlacementType) == 'OneLevelBasedHosted',
          'Source hosting differs from independent OEM QA')
    manager = doc.FamilyManager
    check(type_by_name(manager, SOURCE_TYPE) is not None,
          'Source Matte Black / Opal type missing')
    check(type_by_name(manager, OTHER_TYPE) is not None,
          'Source Aged Gold / Opal type missing')
    check(type_by_name(manager, NEW_TYPE) is None,
          'Clear-glass target type already exists in source')
    check(len(list(manager.Types)) == 2,
          'Expected precisely two source OEM types')
    glass = parameter_by_name(manager, GLASS_PARAM)
    metal = parameter_by_name(manager, METAL_PARAM)
    check(not glass.IsInstance and not metal.IsInstance,
          'Finish parameters unexpectedly instance-based')
    check(str(glass.StorageType) == 'ElementId' and
          str(metal.StorageType) == 'ElementId',
          'Finish parameters are not material IDs')
    source_mbop = inspect_finish(doc, SOURCE_TYPE, glass, metal)
    source_agop = inspect_finish(doc, OTHER_TYPE, glass, metal)
    check(source_mbop['glass_material'] == OPAL_NAME and
          source_mbop['metal_material'] == BLACK_NAME,
          'Source Matte Black / Opal does not match OEM QA')
    check(source_agop['glass_material'] == OPAL_NAME and
          source_agop['metal_material'] == 'CASSIA_AG-FINISH',
          'Source Aged Gold / Opal does not match OEM QA')
    check(len(list(doc.GetWarnings())) == 0,
          'Source family has warnings; re-audit before conversion')
    return {'source_mbop': source_mbop, 'source_agop': source_agop}


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('CASSIA_MBCL_R02_FAILED: ' + traceback.format_exc())
        raise
