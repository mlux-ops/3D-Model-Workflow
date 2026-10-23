# -*- coding: utf-8 -*-
"""Native Revit 2025 OEM inspection; no Save, SaveAs or source transactions.

Run only through the task-local launch_readonly_r02.py ownership handshake.
All model writes occur in fresh unsaved disposable projects, never in RFAs.
An emitter flag, type name, or successful placement cannot release a variant.
IronPython 2.7 compatible. No import from the earlier project/runner.
"""
from __future__ import print_function
import hashlib
import json
import os
import sys
import time
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System import Diagnostics, Environment
from System.Collections.Generic import List

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN_ID = Environment.GetEnvironmentVariable('BELMONT_READONLY_RUN_ID')
TOKEN = Environment.GetEnvironmentVariable('BELMONT_READONLY_TOKEN')
APP = __revit__.Application


def require(okay, message):
    if not okay:
        raise RuntimeError(message)


def text(value):
    return None if value is None else unicode(value)


def guarded(*parts):
    path = os.path.abspath(os.path.join(BASE, *parts))
    require(path.lower().startswith(BASE.lower() + os.sep), 'Write outside task directory')
    return path


def sha(path):
    result = hashlib.sha256()
    with open(path, 'rb') as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            result.update(block)
    return result.hexdigest()


def write_once(path, data):
    require(not os.path.exists(path), 'Refuse receipt overwrite: ' + path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
    with os.fdopen(fd, 'w') as handle:
        json.dump(data, handle, indent=2, ensure_ascii=True)


def now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def progress(stage, detail=None):
    entry = {'utc': now(), 'stage': stage, 'detail': detail}
    with open(PROGRESS, 'a') as handle:
        handle.write(json.dumps(entry, ensure_ascii=True) + '\n')
    print('BELMONT_NATIVE_READONLY ' + stage)
    sys.stdout.flush()


def eid(value):
    return None if value is None else int(value.Value)


def name(element):
    if element is None:
        return None
    return text(DB.Element.Name.GetValue(element))


def warnings(doc):
    return [text(x.GetDescriptionText()) for x in doc.GetWarnings()]


def material(doc, mid):
    result = {'id': eid(mid)}
    if mid is None or eid(mid) < 0:
        result['name'] = None
        return result
    value = doc.GetElement(mid)
    if value is None:
        result['unresolved'] = True
        return result
    result.update({'name': name(value), 'class': text(value.GetType().Name)})
    if isinstance(value, DB.Material):
        result['graphics_rgb'] = [int(value.Color.Red), int(value.Color.Green), int(value.Color.Blue)]
        result['graphics_transparency'] = int(value.Transparency)
        result['appearance_asset_id'] = eid(value.AppearanceAssetId)
        result['appearance_asset_name'] = name(doc.GetElement(value.AppearanceAssetId))
    return result


def type_inventory(doc):
    manager = doc.FamilyManager
    result = []
    for typ in manager.Types:
        row = {'name': text(typ.Name), 'parameters': []}
        for param in manager.Parameters:
            entry = {'name': text(param.Definition.Name), 'storage': text(param.StorageType),
                     'is_instance': bool(param.IsInstance), 'formula': text(param.Formula)}
            try:
                entry['display'] = text(typ.AsValueString(param))
                if param.StorageType == DB.StorageType.String:
                    entry['value'] = text(typ.AsString(param))
                elif param.StorageType == DB.StorageType.Integer:
                    value = typ.AsInteger(param)
                    entry['value'] = None if value is None else int(value)
                elif param.StorageType == DB.StorageType.Double:
                    value = typ.AsDouble(param)
                    entry['internal_value'] = None if value is None else float(value)
                    entry['spec'] = text(param.Definition.GetDataType().TypeId)
                elif param.StorageType == DB.StorageType.ElementId:
                    value = typ.AsElementId(param)
                    entry['value_id'] = eid(value)
                    if param.Definition.GetDataType() == DB.SpecTypeId.Reference.Material:
                        entry['material'] = material(doc, value)
            except Exception:
                entry['read_error'] = traceback.format_exc()
            row['parameters'].append(entry)
        result.append(row)
    return result


def native_lighting(doc):
    result = {'inspection_complete': False, 'flag_is_not_emitter_proof': True}
    try:
        flag = doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE)
        result['owner_light_source_flag'] = flag.AsInteger() if flag else None
        family = DB.Lighting.LightFamily.GetLightFamily(doc)
        result['light_family_exists'] = family is not None
        result['light_types'] = []
        if family is not None:
            result['light_type_count'] = int(family.GetNumberOfLightTypes())
            for i in range(result['light_type_count']):
                typ = family.GetLightType(i)
                dist = typ.GetLightDistribution()
                shape = typ.GetLightShape()
                item = {'index': i, 'distribution_class': text(dist.GetType().FullName),
                        'shape_class': text(shape.GetType().FullName),
                        'initial_intensity_class': text(typ.GetInitialIntensity().GetType().FullName),
                        'initial_color_class': text(typ.GetInitialColor().GetType().FullName)}
                if isinstance(dist, DB.Lighting.PhotometricWebLightDistribution):
                    reference = text(dist.PhotometricWebFile)
                    item['photometric_reference'] = reference
                    item['absolute_reference_exists'] = bool(reference and os.path.isabs(reference)
                                                             and os.path.isfile(reference))
                    item['selected_variant_ies_match'] = 'NOT_VERIFIED'
                result['light_types'].append(item)
        result['inspection_complete'] = True
    except Exception:
        result['error'] = traceback.format_exc()
    return result


class Geometry(object):
    def __init__(self, doc):
        self.doc = doc
        self.solids = []
        self.mesh_count = 0
        self.errors = []
        self.null_edges_skipped = 0

    def walk(self, values, depth=0):
        if values is None:
            self.errors.append('Null geometry')
            return
        if depth > 15:
            self.errors.append('Nested geometry depth limit exceeded')
            return
        for value in values:
            try:
                if isinstance(value, DB.GeometryInstance):
                    self.walk(value.GetInstanceGeometry(), depth + 1)
                elif isinstance(value, DB.Mesh):
                    self.mesh_count += 1
                elif isinstance(value, DB.Solid) and value.Volume > 1e-12:
                    self.solid(value, depth)
            except Exception:
                self.errors.append(traceback.format_exc())

    def solid(self, value, depth):
        minimum = [float('inf')] * 3
        maximum = [float('-inf')] * 3
        materials = {}
        points = [0]

        def sample(point):
            for axis, v in enumerate((point.X, point.Y, point.Z)):
                minimum[axis] = min(minimum[axis], float(v))
                maximum[axis] = max(maximum[axis], float(v))
            points[0] += 1

        for face in value.Faces:
            mid = eid(face.MaterialElementId)
            materials[str(mid)] = materials.get(str(mid), 0) + 1
            for point in face.Triangulate().Vertices:
                sample(point)
        for edge in value.Edges:
            curve = edge.AsCurve()
            if curve is None:
                self.null_edges_skipped += 1
                continue
            count = 2 if isinstance(curve, DB.Line) else 33
            for i in range(count):
                sample(curve.Evaluate(float(i) / float(count - 1), True))
        require(points[0] > 0, 'Positive-volume solid yielded no points')
        self.solids.append({'index': len(self.solids), 'nested_depth': depth,
                            'minimum_world_xyz_mm': [x * 304.8 for x in minimum],
                            'maximum_world_xyz_mm': [x * 304.8 for x in maximum],
                            'xyz_mm': [(b - a) * 304.8 for a, b in zip(minimum, maximum)],
                            'volume_mm3': float(value.Volume) * 304.8 ** 3,
                            'sample_points': points[0],
                            'face_materials': [{'face_count': count,
                                                'material': material(self.doc, DB.ElementId(int(mid)))}
                                               for mid, count in sorted(materials.items())]})

    def report(self):
        result = {'positive_volume_solids': self.solids, 'standalone_mesh_count': self.mesh_count,
                  'errors': self.errors, 'null_edges_skipped': self.null_edges_skipped,
                  'bounds_scope': 'Placed positive-volume solids only; excludes host, curves and reference planes.',
                  'body_canopy_cord_separation': 'PENDING_SOURCE_COMPONENT_REVIEW'}
        if self.solids:
            lo = [min(s['minimum_world_xyz_mm'][i] for s in self.solids) for i in range(3)]
            hi = [max(s['maximum_world_xyz_mm'][i] for s in self.solids) for i in range(3)]
            result['minimum_world_xyz_mm'] = lo
            result['maximum_world_xyz_mm'] = hi
            result['whole_assembly_xyz_mm'] = [b - a for a, b in zip(lo, hi)]
        result['native_solid_geometry_pass'] = bool(self.solids and not self.errors)
        result['loose_mesh_visual_review'] = 'PENDING' if self.mesh_count else 'NOT_PRESENT'
        return result


def placement(family_doc, selection):
    project = None
    tx = None
    report = {'success': False, 'source_family_modified': False,
              'disposable_project_saved': False, 'host_kind': 'ACTUAL_CEILING'}
    try:
        project = APP.NewProjectDocument(DB.UnitSystem.Imperial)
        require(project is not None, 'No disposable project')
        family = family_doc.LoadFamily(project)
        require(family is not None, 'Family document LoadFamily returned no Family')
        symbols = [project.GetElement(i) for i in family.GetFamilySymbolIds()]
        names = {name(symbol): symbol for symbol in symbols}
        wanted = selection['requested_sku']
        preferred = {'41411-BG': '41411-BK', '402401BG-LED': '4024014BG-LED',
                     '494502M-GD': '494502M-GD', 'A691-474-37-27K': 'A691-240'}
        tested = wanted if wanted in names else preferred.get(wanted)
        require(tested in names, 'No known representative or exact type to test')
        symbol = names[tested]
        report['tested_type'] = tested
        report['requested_type_exact_name'] = tested == wanted
        report['representative_is_not_selected_variant_approval'] = tested != wanted
        report['family_placement_type'] = text(family.FamilyPlacementType)
        tx = DB.Transaction(project, 'Disposable ceiling-host and placement inspection')
        tx.Start()
        level = DB.Level.Create(project, 0.0)
        ceiling_types = list(DB.FilteredElementCollector(project).OfClass(DB.CeilingType))
        require(bool(ceiling_types), 'No real CeilingType in blank project; do not substitute floor')
        perimeter = DB.CurveLoop()
        points = [DB.XYZ(-8, -8, 0), DB.XYZ(8, -8, 0), DB.XYZ(8, 8, 0), DB.XYZ(-8, 8, 0)]
        for i in range(4):
            perimeter.Append(DB.Line.CreateBound(points[i], points[(i + 1) % 4]))
        ceiling = DB.Ceiling.Create(project, List[DB.CurveLoop]([perimeter]), ceiling_types[0].Id, level.Id)
        offset = ceiling.get_Parameter(DB.BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM)
        require(offset is not None and not offset.IsReadOnly, 'Ceiling height unavailable')
        offset.Set(10.0)
        symbol.Activate()
        project.Regenerate()
        refs = list(DB.HostObjectUtils.GetBottomFaces(ceiling))
        require(bool(refs), 'Ceiling underside has no referenceable face')
        face = ceiling.GetGeometryObjectFromReference(refs[0])
        hit = face.Project(DB.XYZ(0, 0, 10))
        require(hit is not None, 'Cannot project placement point onto ceiling underside')
        point = hit.XYZPoint
        if family.FamilyPlacementType == DB.FamilyPlacementType.WorkPlaneBased:
            instance = project.Create.NewFamilyInstance(refs[0], point, DB.XYZ.BasisX, symbol)
            report['method'] = 'CEILING_UNDERSIDE_FACE_REFERENCE'
        elif family.FamilyPlacementType == DB.FamilyPlacementType.OneLevelBasedHosted:
            instance = project.Create.NewFamilyInstance(point, symbol, ceiling, level,
                                                       DB.Structure.StructuralType.NonStructural)
            report['method'] = 'ACTUAL_CEILING_ELEMENT_AND_LEVEL'
        else:
            raise RuntimeError('Unexpected pendant hosting type: ' + report['family_placement_type'])
        project.Regenerate()
        require(instance.Host is not None and instance.Host.Id == ceiling.Id,
                'Instance is not attached to disposable actual ceiling')
        report['actual_ceiling_host_verified'] = True
        report['actual_host_class'] = text(instance.Host.GetType().FullName)
        report['ceiling_underside_z_mm'] = float(point.Z) * 304.8
        report['instance_id'] = eid(instance.Id)
        report['instance_origin_world_mm'] = [float(x) * 304.8 for x in
                                              (instance.GetTransform().Origin.X,
                                               instance.GetTransform().Origin.Y,
                                               instance.GetTransform().Origin.Z)]
        options = DB.Options()
        options.DetailLevel = DB.ViewDetailLevel.Fine
        options.IncludeNonVisibleObjects = False
        geometry = Geometry(project)
        geometry.walk(instance.get_Geometry(options))
        report['geometry'] = geometry.report()
        tx.Commit()
        tx = None
        report['warnings'] = warnings(project)
        report['success'] = bool(report['geometry']['native_solid_geometry_pass'] and not report['warnings'])
        report['dimension_source_fidelity'] = 'PENDING_COMPONENT_SEPARATION_AND_DRAWING_COMPARISON'
        report['front_oblique_visual_evidence'] = 'NOT_EXPORTED_IN_FIRST_READONLY_PROBE'
    except Exception:
        report['error'] = traceback.format_exc()
    finally:
        if tx is not None:
            try:
                tx.RollBack()
            except Exception:
                report['rollback_error'] = traceback.format_exc()
        if project is not None:
            try:
                project.Close(False)
                report['disposable_project_closed_without_save'] = True
            except Exception:
                report['close_error'] = traceback.format_exc()
                report['success'] = False
    return report


require(RUN_ID and RUN_ID.replace('_', '').isalnum() and TOKEN, 'Missing isolated ownership handshake')
REQUEST = guarded('runner', 'requests', RUN_ID + '.json')
OUTPUT = guarded('qa', 'native_readonly_' + RUN_ID + '.json')
PROGRESS = guarded('qa', 'native_readonly_' + RUN_ID + '_progress.jsonl')
require(not os.path.exists(OUTPUT) and not os.path.exists(PROGRESS), 'Native run already has evidence')
with open(REQUEST, 'r') as handle:
    request = json.load(handle)
require(TOKEN == request['token'], 'Ownership token mismatch')
pid = int(Diagnostics.Process.GetCurrentProcess().Id)
require(pid not in request['preexisting_revit_pids'], 'Refuse to use any preexisting Revit process')
require(str(APP.VersionNumber) == '2025', 'Revit 2025 required')
require(getattr(__revit__, 'ActiveUIDocument', None) is None, 'Active user document prohibited')
require(not list(APP.Documents), 'Fresh isolated process must have zero documents')
report = {'status': 'STARTED', 'started_utc': now(), 'pid': pid,
          'version': text(APP.VersionNumber), 'build': text(APP.VersionBuild),
          'run_id': RUN_ID, 'families': [], 'all_originals_unchanged': False,
          'release_status': 'REVIEW_NOT_RELEASED', 'documents_before': []}
before = {}
try:
    progress('ISOLATED_DOCUMENT_FREE_PROCESS_VERIFIED', {'pid': pid})
    for selection in request['families']:
        path = selection['file']
        require(os.path.abspath(path).lower().startswith(BASE.lower() + os.sep), 'Source outside task')
        before[path] = sha(path)
        require(before[path] == selection['original_rfa_sha256'], 'Source hash mismatch')
    for selection in request['families']:
        path = selection['file']
        doc = None
        entry = {'file': path, 'requested_sku': selection['requested_sku'],
                 'source_sha256': before[path], 'revit_save_performed': False}
        progress('OPENING_ORIGINAL', {'sku': selection['requested_sku']})
        try:
            doc = APP.OpenDocumentFile(path)
            require(doc.IsFamilyDocument, 'Not a family document')
            entry['category'] = text(doc.OwnerFamily.FamilyCategory.Name)
            entry['family_placement_type'] = text(doc.OwnerFamily.FamilyPlacementType)
            entry['native_types'] = type_inventory(doc)
            entry['native_materials'] = [material(doc, x.Id) for x in
                                          DB.FilteredElementCollector(doc).OfClass(DB.Material)]
            entry['native_lighting'] = native_lighting(doc)
            entry['family_warnings'] = warnings(doc)
            entry['native_open_pass'] = True
            progress('FAMILY_INSPECTED', {'sku': selection['requested_sku'],
                                         'type_count': len(entry['native_types'])})
            entry['placement'] = placement(doc, selection)
            entry['native_basic_technical_pass'] = bool(
                entry['category'] == 'Lighting Fixtures' and not entry['family_warnings']
                and entry['placement']['success'])
            entry['source_fidelity'] = 'PENDING_EXACT_VARIANT_AND_GEOMETRY_VISUAL_REVIEW'
        except Exception:
            entry['error'] = traceback.format_exc()
            entry['native_basic_technical_pass'] = False
        finally:
            if doc is not None:
                doc.Close(False)
                entry['original_closed_without_save'] = True
            entry['after_sha256'] = sha(path)
            entry['source_bytes_unchanged'] = entry['after_sha256'] == before[path]
            report['families'].append(entry)
            write_once(guarded('qa', 'native_readonly_' + RUN_ID + '_'
                               + str(len(report['families'])) + '.json'), entry)
            progress('FAMILY_CLOSED', {'sku': selection['requested_sku'],
                                        'basic_technical_pass': entry['native_basic_technical_pass']})
            require(entry['source_bytes_unchanged'], 'Original bytes changed')
    report['status'] = 'BASIC_TECHNICAL_PASS_FIDELITY_HOLD' if all(
        x['native_basic_technical_pass'] for x in report['families']) else 'NATIVE_QA_HOLD'
except Exception:
    report['status'] = 'ERROR'
    report['error'] = traceback.format_exc()
finally:
    report['all_originals_unchanged'] = (len(before) == len(request['families']) and
                                       all(sha(path) == value for path, value in before.items()))
    report['documents_after'] = [text(x.Title) for x in APP.Documents]
    report['completed_utc'] = now()
    report['complete_count'] = len(report['families'])
    write_once(OUTPUT, report)
    progress('FINAL_RECEIPT_WRITTEN', {'status': report['status']})
