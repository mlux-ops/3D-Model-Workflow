# -*- coding: utf-8 -*-
"""Read-only independent Revit 2025 QA for Cassia LP549448MBCL R02.

Run in an isolated, document-free Revit instance using:
  pyrevit run "E:\\Claude\\3D-Model-Workflow\\output\\belmont_ph_good_rfa_20261016\\qa\\cassia_mbcl_r02_native_qa.py" --revit=2025

Source/candidate RFAs are opened read-only in practice (never transacted or
saved). Only an unsaved disposable project receives the family and instance.
The sole persistent output is a NEW, immutable JSON QA receipt.

The manufacturer measures the 48 x 13.375 x 6 in L/W/H fixture BODY, not
the suspended installation, rods or large OEM reference/control solids.
Measurement uses actual placed native solid surfaces and a MATERIAL-ANCHORED,
WHOLE-SOLID body selection; it never crops a 6-in Z band and then calls
the clipped result an exact 6-in match. Ambiguous dimensions stay on HOLD.
"""
from __future__ import print_function

import hashlib
import json
import os
import time
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
CANDIDATE = os.path.join(BASE, 'candidates',
    'Alora_Cassia_LP549448MBCL_R2025_R02.rfa')
BASELINE = os.path.join(BASE, 'families',
    'Alora_Cassia_LP549448MBCL_R2025.rfa')
OEM = os.path.join(BASE, 'sources', 'oem', 'extracted',
    'ALR1280090_LP549448_Cassia_Revit', 'LP549448-Cassia.rfa')
BUILD_RECEIPT = os.path.join(BASE, 'qa', 'cassia_mbcl_r02_build.json')
OUTPUT = os.path.join(BASE, 'qa', 'cassia_mbcl_r02_native_qa_fix01.json')

EXPECTED_SHA = {
    CANDIDATE: 'c380fb71be8d69008911cef833b0838e53bc96b84650ece9d63d817ab56f3c02',
    BASELINE: '27ce97b87c28cabaf249ebc4410ce9bf1b387e16a2232e2fc29e153530c09ac3',
    OEM: '1bd05892bc0598d43b30afca32f648ad26fbd6df2e3776bd8c169b1ad743db9e'
}
SKU = 'LP549448MBCL'
GLASS = 'CASSIA_CLEAR_GLASS_MBCL'
GLASS_ASSET = 'Cassia Clear Glass LP549448MBCL'
BLACK = 'CASSIA_MB_FINISH'
ALLOWED_BODY_MATERIALS = set([
    GLASS, BLACK, 'BULB_GLASS', 'BULB_PLASTIC'
])
EXPECTED_BODY_IN = [48.0, 13.375, 6.0]   # L, W, H, manufacturer fixture BODY
BODY_TOLERANCE_IN = 0.125               # explicit QA tolerance, not an OEM tolerance
MAX_SHORT_BODY_SOLID_HEIGHT_IN = 6.75
BODY_NEAR_SHADE_IN = 1.0
MAX_NEST_DEPTH = 12


def as_text(value):
    if value is None:
        return None
    try:
        return unicode(value)
    except Exception:
        return str(value).decode('utf-8', 'replace')


def element_name(element):
    if element is None:
        return None
    try:
        return as_text(DB.Element.Name.GetValue(element))
    except Exception:
        try:
            return as_text(element.Name)
        except Exception:
            return None


def element_id_number(value):
    if value is None:
        return None
    try:
        return int(value.Value)
    except Exception:
        try:
            return int(value.IntegerValue)
        except Exception:
            return None


def fingerprint(path):
    if not os.path.isfile(path):
        return {'path': path, 'exists': False}
    hasher = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            part = stream.read(1024 * 1024)
            if not part:
                break
            hasher.update(part)
    return {'path': path, 'exists': True, 'bytes': os.path.getsize(path),
            'sha256': hasher.hexdigest()}


def check(condition, description):
    if not condition:
        raise RuntimeError(description)


def warnings(doc):
    return [as_text(w.GetDescriptionText()) for w in doc.GetWarnings()]


def manager_parameter(manager, name):
    for parameter in manager.Parameters:
        if as_text(parameter.Definition.Name) == name:
            return parameter
    raise RuntimeError('Missing family material parameter ' + name)


def family_type(manager, name):
    for item in manager.Types:
        if as_text(item.Name) == name:
            return item
    raise RuntimeError('Missing family type ' + name)


def material_record(doc, family_type_obj, parameter):
    check(not parameter.IsInstance and str(parameter.StorageType) == 'ElementId',
          'Material finish parameter must be a type ElementId')
    material_id = family_type_obj.AsElementId(parameter)
    material = doc.GetElement(material_id)
    check(isinstance(material, DB.Material),
          'Material parameter is not bound to a native Material')
    asset = doc.GetElement(material.AppearanceAssetId)
    color = material.Color
    return {
        'name': element_name(material),
        'id': element_id_number(material.Id),
        'appearance': element_name(asset),
        'appearance_asset_bound': isinstance(asset, DB.AppearanceAssetElement),
        'transparency_percent': int(material.Transparency),
        'rgb': [int(color.Red), int(color.Green), int(color.Blue)]
    }


def family_materials(doc):
    manager = doc.FamilyManager
    glass_param = manager_parameter(manager, 'GLASS_COLOR')
    metal_param = manager_parameter(manager, 'METAL_FINISH')
    result = {}
    for typename in (SKU, 'LP549448MBOP', 'LP549448AGOP'):
        typ = family_type(manager, typename)
        result[typename] = {
            'GLASS_COLOR': material_record(doc, typ, glass_param),
            'METAL_FINISH': material_record(doc, typ, metal_param)
        }
    actual_names = sorted(as_text(t.Name) for t in manager.Types)
    expected_names = sorted([SKU, 'LP549448MBOP', 'LP549448AGOP'])
    tests = {
        'all_exact_type_names': actual_names == expected_names,
        'clear_glass_type_binding':
            result[SKU]['GLASS_COLOR']['name'] == GLASS,
        'clear_glass_95_shaded_transparency':
            result[SKU]['GLASS_COLOR']['transparency_percent'] == 95,
        'clear_glass_realistic_appearance':
            result[SKU]['GLASS_COLOR']['appearance'] == GLASS_ASSET and
            result[SKU]['GLASS_COLOR']['appearance_asset_bound'],
        'matte_black_preserved':
            result[SKU]['METAL_FINISH']['name'] == BLACK and
            result[SKU]['METAL_FINISH']['transparency_percent'] == 0,
        'mbop_original_materials':
            result['LP549448MBOP']['GLASS_COLOR']['name'] == 'CASSIA_OPAL_GLASS' and
            result['LP549448MBOP']['METAL_FINISH']['name'] == BLACK,
        'agop_original_materials':
            result['LP549448AGOP']['GLASS_COLOR']['name'] == 'CASSIA_OPAL_GLASS' and
            result['LP549448AGOP']['METAL_FINISH']['name'] == 'CASSIA_AG-FINISH'
    }
    return {'types': result, 'type_names': actual_names, 'checks': tests}


def symbol_name(symbol):
    p = symbol.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
    if p is not None:
        value = p.AsString()
        if value:
            return as_text(value)
    return element_name(symbol)


def box_of(solids):
    if not solids:
        return None
    lo = [min(x['min_local_ft'][i] for x in solids) for i in range(3)]
    hi = [max(x['max_local_ft'][i] for x in solids) for i in range(3)]
    return {
        'min_local_in': [round(v * 12., 5) for v in lo],
        'max_local_in': [round(v * 12., 5) for v in hi],
        'xyz_in': [round((hi[i] - lo[i]) * 12., 5) for i in range(3)]
    }


class NativeGeometry(object):
    """Inspect every positive-volume solid with nested Revit transforms applied."""

    def __init__(self, project, instance):
        self.project = project
        self.to_local = instance.GetTransform().Inverse
        self.solids = []
        self.loose_meshes = 0
        self.nested_instances = 0
        self.errors = []
        self.null_edges = 0

    def material_name(self, mid):
        material = self.project.GetElement(mid)
        return element_name(material) or '(unbound)'

    def add_solid(self, solid):
        try:
            if float(solid.Volume) <= 1e-12:
                return
        except Exception as exc:
            self.errors.append('Solid volume: ' + as_text(exc))
            return
        lo = [float('inf')] * 3
        hi = [float('-inf')] * 3
        samples = [0]

        def point(value):
            local = self.to_local.OfPoint(value)
            for axis, v in enumerate((local.X, local.Y, local.Z)):
                lo[axis] = min(lo[axis], float(v))
                hi[axis] = max(hi[axis], float(v))
            samples[0] += 1

        face_mats = {}
        for face in solid.Faces:
            name = self.material_name(face.MaterialElementId)
            face_mats[name] = face_mats.get(name, 0) + 1
            try:
                for point_value in face.Triangulate().Vertices:
                    point(point_value)
            except Exception as exc:
                self.errors.append('Face triangulation: ' + as_text(exc))
        for edge in solid.Edges:
            try:
                curve = edge.AsCurve()
                if curve is None:
                    self.null_edges += 1
                    continue
                steps = 2 if isinstance(curve, DB.Line) else 17
                for i in range(steps):
                    point(curve.Evaluate(float(i) / float(steps - 1), True))
            except Exception as exc:
                self.errors.append('Analytic edge: ' + as_text(exc))
        if samples[0]:
            self.solids.append({
                'min_local_ft': lo,
                'max_local_ft': hi,
                'xyz_in': [round((hi[i]-lo[i])*12., 5) for i in range(3)],
                'face_material_counts': face_mats,
                'point_count': samples[0]
            })

    def walk(self, collection, depth=0):
        if depth > MAX_NEST_DEPTH:
            self.errors.append('Nested geometry exceeded depth limit')
            return
        if collection is None:
            self.errors.append('Instance geometry returned None')
            return
        for item in collection:
            if isinstance(item, DB.GeometryInstance):
                self.nested_instances += 1
                self.walk(item.GetInstanceGeometry(), depth + 1)
            elif isinstance(item, DB.Solid):
                self.add_solid(item)
            elif isinstance(item, DB.Mesh):
                self.loose_meshes += 1

    def report(self):
        counts = {}
        for solid in self.solids:
            for material, faces in solid['face_material_counts'].items():
                counts[material] = counts.get(material, 0) + faces
        return {
            'full_solid_envelope': box_of(self.solids),
            'positive_volume_solid_count': len(self.solids),
            'nested_geometry_instance_count': self.nested_instances,
            'loose_mesh_count': self.loose_meshes,
            'null_analytic_edges_skipped': self.null_edges,
            'material_face_counts': counts,
            'errors': self.errors,
            'measurement_method': 'Placed native solids; all triangulated faces and sampled analytic edges, nested GetInstanceGeometry, inverse instance transform',
            'complete': len(self.solids) > 0 and not self.errors and not self.loose_meshes
        }

    def body(self):
        """Anchor whole physical solids on clear shades, exclude rods and controls.

        The printed 6-in BODY height is evaluated on the measured union of
        complete selected solids. It is not used as a cropping height.
        """
        glass = [s for s in self.solids
                 if s['face_material_counts'].get(GLASS, 0)]
        result = {'nominal_body_in_LWH': EXPECTED_BODY_IN,
                  'tolerance_in_each_dimension': BODY_TOLERANCE_IN,
                  'glass_anchor_solid_count': len(glass),
                  'selection_rule': 'Whole positive-volume solids with known fixture materials, <=6.75 in tall, intersecting clear shade vertical neighborhood (+/-1 in); excludes long drops/reference controls',
                  'evaluated': False, 'passed': None}
        if not glass:
            result['status'] = 'HOLD_NO_CLEAR_SHADE_FACES_IN_PLACED_GEOMETRY'
            return result
        anchor = box_of(glass)
        result['glass_anchor_envelope'] = anchor
        if anchor['xyz_in'][2] > MAX_SHORT_BODY_SOLID_HEIGHT_IN:
            result['status'] = 'HOLD_GLASS_ANCHOR_INCLUDES_SUSPENSION_OR_CONTROLS'
            return result
        min_glass_z = min(s['min_local_ft'][2] for s in glass)
        max_glass_z = max(s['max_local_ft'][2] for s in glass)
        selected = []
        omitted = []
        for index, s in enumerate(self.solids):
            mats = set(s['face_material_counts'])
            eligible = bool(mats.intersection(ALLOWED_BODY_MATERIALS))
            short = s['xyz_in'][2] <= MAX_SHORT_BODY_SOLID_HEIGHT_IN
            near = (s['max_local_ft'][2] >= min_glass_z - BODY_NEAR_SHADE_IN/12. and
                    s['min_local_ft'][2] <= max_glass_z + BODY_NEAR_SHADE_IN/12.)
            if eligible and short and near:
                selected.append(s)
            else:
                omitted.append({'solid_index': index,
                                'xyz_in': s['xyz_in'],
                                'materials': s['face_material_counts'],
                                'why': ('unknown_material' if not eligible else
                                        'tall_suspension_or_control' if not short else
                                        'outside_shade_body_region')})
        measured = box_of(selected)
        result.update({'selected_solids': len(selected),
                       'omitted_solids': omitted,
                       'body_envelope_local_xyz': measured})
        if measured is None:
            result['status'] = 'HOLD_NO_BODY_SOLIDS_SELECTED'
            return result
        # Installed fixture local XY may use either axis for the linear run.
        xy = measured['xyz_in'][:2]
        actual = [max(xy), min(xy), measured['xyz_in'][2]]
        deviation = [round(actual[i] - EXPECTED_BODY_IN[i], 5) for i in range(3)]
        result.update({'evaluated': True, 'measured_body_in_LWH': actual,
                       'delta_in_LWH': deviation,
                       'max_abs_error_in': max(abs(v) for v in deviation),
                       'axis_convention': 'max(local X,local Y)=L; min=W; local Z=H',
                       'glass_face_count': sum(x['face_material_counts'].get(GLASS,0)
                                               for x in selected),
                       'black_face_count': sum(x['face_material_counts'].get(BLACK,0)
                                               for x in selected)})
        scope_ok = (self.report()['complete'] and
                    len(selected) >= len(glass) and
                    result['glass_face_count'] > 0 and
                    result['black_face_count'] > 0)
        result['scope_supported'] = scope_ok
        result['passed'] = bool(scope_ok and
                              all(abs(v) <= BODY_TOLERANCE_IN for v in deviation))
        result['status'] = ('MATCH_WITHIN_0_125_IN'
                            if result['passed'] else
                            'HOLD_BODY_ENVELOPE_OR_SCOPE_MISMATCH')
        return result


def verify_placed_level(project, instance, target_level):
    candidate_ids = {}
    try:
        candidate_ids['Element.LevelId'] = element_id_number(instance.LevelId)
    except Exception:
        pass
    for name in ('FAMILY_LEVEL_PARAM', 'INSTANCE_REFERENCE_LEVEL_PARAM',
                 'INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM'):
        try:
            parameter = instance.get_Parameter(getattr(DB.BuiltInParameter, name))
            if parameter is not None and str(parameter.StorageType) == 'ElementId':
                candidate_ids[name] = element_id_number(parameter.AsElementId())
        except Exception:
            pass
    level_id = element_id_number(target_level.Id)
    return {'level_id': level_id, 'observed_level_ids': candidate_ids,
            'level_reference_matches': level_id in candidate_ids.values(),
            'physical_host_id': (element_id_number(instance.Host.Id)
                                 if instance.Host is not None else None),
            'note': 'OneLevelBasedHosted legitimately places by Level and may have no physical Host'}


def check_placement(app):
    project = None
    transaction = None
    try:
        project = app.NewProjectDocument(DB.UnitSystem.Imperial)
        check(project is not None and not project.IsFamilyDocument,
              'Disposable project could not be constructed')
        # Load the exact saved candidate; no source/family transaction or save.
        loaded = project.LoadFamily(CANDIDATE)
        check(loaded is not None, 'Project.LoadFamily returned no family')
        # Revit 2025 string overload LoadFamily(path) returns bool, not Family.
        # Resolve the newly loaded symbols by exact type/name instead.
        matches = list(DB.FilteredElementCollector(project).OfClass(DB.FamilySymbol))
        matches = [s for s in matches if symbol_name(s) == SKU]
        check(len(matches) == 1, 'Cannot uniquely locate loaded MBCL FamilySymbol')
        symbol = matches[0]
        transaction = DB.Transaction(project, 'Disposable Cassia R02 level QA')
        transaction.Start()
        level = DB.Level.Create(project, 0.0)
        symbol.Activate()
        project.Regenerate()
        # As established by the OEM QA, OneLevelBasedHosted rejects a face
        # reference and must use the level-overload placement API.
        instance = project.Create.NewFamilyInstance(
            DB.XYZ(0.0, 0.0, 8.0), symbol, level,
            DB.Structure.StructuralType.NonStructural)
        project.Regenerate()
        level_check = verify_placed_level(project, instance, level)
        options = DB.Options()
        options.IncludeNonVisibleObjects = False
        options.DetailLevel = DB.ViewDetailLevel.Fine
        geometry = NativeGeometry(project, instance)
        geometry.walk(instance.get_Geometry(options))
        result = {
            'attempted': True, 'project_saved': False,
            'disposable_project': True,
            'placement_api': 'NewFamilyInstance(XYZ, FamilySymbol, Level, StructuralType)',
            'family_placement_type': 'OneLevelBasedHosted',
            'placed_symbol_name': symbol_name(instance.Symbol),
            'expected_level_id': element_id_number(level.Id),
            'level': level_check,
            'level_based_placement_verified':
                level_check['level_reference_matches'] and
                bool(instance.Symbol.Id.Equals(symbol.Id)),
            'warnings': warnings(project),
            'geometry': geometry.report(),
            'manufacturer_body': geometry.body()
        }
        return result
    finally:
        if transaction is not None:
            try:
                transaction.RollBack()
            except Exception:
                pass
        if project is not None:
            project.Close(False)


def save_receipt_once(value):
    check(not os.path.lexists(OUTPUT), 'QA receipt already exists: ' + OUTPUT)
    temp = OUTPUT + '.tmp'
    check(not os.path.lexists(temp), 'Incomplete QA receipt temp exists: ' + temp)
    encoded = json.dumps(value, ensure_ascii=True, indent=2,
                         sort_keys=True, default=as_text)
    with open(temp, 'wb') as f:
        f.write(encoded.encode('ascii'))
    check(not os.path.lexists(OUTPUT), 'QA receipt appeared before final rename')
    os.rename(temp, OUTPUT)


def main():
    check(not os.path.lexists(OUTPUT), 'Receipt exists: ' + OUTPUT)
    app = __revit__.Application
    check(str(app.VersionNumber) == '2025', 'Revit 2025 required')
    check(getattr(__revit__, 'ActiveUIDocument', None) is None,
          'Run in separate, document-free pyRevit process')
    protected = [CANDIDATE, BASELINE, OEM, BUILD_RECEIPT]
    before = dict((path, fingerprint(path)) for path in protected)
    report = {
        'schema_version': 1,
        'purpose': 'Independent native read-only QA of Cassia LP549448MBCL R02',
        'revit_version': str(app.VersionNumber),
        'run_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'candidate': CANDIDATE,
        'output': OUTPUT,
        'source_spec_url': 'https://s3-us-west-2.amazonaws.com/catsy.870/LP549448_Spec_Sheet.pdf',
        'status': 'ERROR',
        'source_files_before': before,
        'checks': {},
        'visual_render_status': 'NOT_TESTED_BY_THIS_SCRIPT',
        'photometric_status': 'NOT_TESTED_BY_THIS_SCRIPT'
    }
    family_doc = None
    try:
        for path in protected:
            check(before[path]['exists'], 'Missing required protected file: ' + path)
        for path, expected in EXPECTED_SHA.items():
            report['checks']['sha256_expected_' + os.path.basename(path)] = (
                before[path]['sha256'] == expected)
        check(all(report['checks'].values()), 'Candidate, baseline or OEM checksum differs')
        with open(BUILD_RECEIPT, 'r') as f:
            build = json.load(f)
        report['checks']['build_receipt_matches_candidate'] = (
            build.get('output_sha256') == before[CANDIDATE]['sha256'] and
            build.get('source_sha256') == before[BASELINE]['sha256'] and
            build.get('status') ==
                'SAVED_REOPENED_MATERIAL_PASS_PENDING_VISUAL_AND_PLACEMENT_QA')
        check(report['checks']['build_receipt_matches_candidate'],
              'Successful candidate build receipt does not match SHA/type')
        family_doc = app.OpenDocumentFile(CANDIDATE)
        check(family_doc.IsFamilyDocument, 'Candidate must open as Revit family')
        report['family_category'] = element_name(family_doc.OwnerFamily.FamilyCategory)
        report['family_placement_type'] = str(family_doc.OwnerFamily.FamilyPlacementType)
        report['family_warnings'] = warnings(family_doc)
        report['type_materials'] = family_materials(family_doc)
        report['checks'].update(report['type_materials']['checks'])
        report['checks']['lighting_fixture_category'] = (
            report['family_category'] == 'Lighting Fixtures')
        report['checks']['one_level_based_hosted_type'] = (
            report['family_placement_type'] == 'OneLevelBasedHosted')
        report['checks']['no_family_warnings'] = not report['family_warnings']
        family_doc.Close(False)
        family_doc = None
        report['placement'] = check_placement(app)
        placement = report['placement']
        body = placement['manufacturer_body']
        geom = placement['geometry']
        report['checks']['level_based_placement'] = placement['level_based_placement_verified']
        report['checks']['no_project_warnings'] = not placement['warnings']
        report['checks']['complete_placed_solid_geometry'] = geom['complete']
        report['checks']['clear_material_used_on_placed_faces'] = (
            geom['material_face_counts'].get(GLASS, 0) > 0 and
            geom['material_face_counts'].get('CASSIA_OPAL_GLASS', 0) == 0)
        report['checks']['black_material_used_on_placed_faces'] = (
            geom['material_face_counts'].get(BLACK, 0) > 0)
        report['checks']['manufacturer_48x13_375x6_body'] = bool(body['passed'])
        report['status'] = ('TECHNICAL_PASS_VISUAL_REVIEW_PENDING'
                            if all(report['checks'].values()) else
                            'HOLD_NATIVE_QA_CHECKS')
    except Exception:
        report['error'] = traceback.format_exc()
        report['status'] = 'ERROR'
    finally:
        if family_doc is not None:
            try:
                family_doc.Close(False)
            except Exception as exc:
                report['family_close_error'] = as_text(exc)
        after = dict((path, fingerprint(path)) for path in protected)
        report['source_files_after'] = after
        report['files_unchanged'] = all(before.get(path) == after.get(path)
                                        for path in protected)
        report['checks']['original_and_candidate_files_unchanged'] = report['files_unchanged']
        if not report['files_unchanged']:
            report['status'] = 'FAIL_PROTECTED_FILE_HASH_CHANGE'
        if report['status'] == 'TECHNICAL_PASS_VISUAL_REVIEW_PENDING' and not all(report['checks'].values()):
            report['status'] = 'HOLD_NATIVE_QA_CHECKS'
        save_receipt_once(report)
    print('CASSIA_R02_NATIVE_QA: ' + report['status'])
    print('RECEIPT: ' + OUTPUT)
    if report['status'] != 'TECHNICAL_PASS_VISUAL_REVIEW_PENDING':
        raise RuntimeError('Cassia R02 native QA not passed; inspect separate JSON receipt')


main()
