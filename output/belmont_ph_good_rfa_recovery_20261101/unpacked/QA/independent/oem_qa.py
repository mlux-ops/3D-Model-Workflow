# -*- coding: utf-8 -*-
"""Independent, read-only native QA for FOUR Belmont PH Good OEM RFAs.

Run in an ISOLATED Revit 2025 process:
pyrevit run "E:\\Claude\\3D-Model-Workflow\\output\\belmont_ph_good_rfa_20261016\\qa\\oem_qa.py" --revit=2025

IronPython 2.7. Opens only the four saved family outputs. Each placement test
uses a fresh unsaved disposable project; all Revit documents Close(False).
No existing RFA, RVT, previous receipt, pyRevit setting or extension is edited.
"""
from __future__ import print_function
import os
import sys
import time
import json
import re
import hashlib
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
RUNNER = os.path.join(BASE, 'runner')
QA_DIR = os.path.join(BASE, 'qa')
MANIFEST = os.path.join(RUNNER, 'manifest.json')
OUTPUT = os.path.join(QA_DIR, 'oem_qa.json')
PROGRESS = os.path.join(QA_DIR, 'oem_qa_progress.jsonl')
APP = __revit__.Application
MM_PER_FOOT = 304.8
GEOM_POINT_LIMIT = 350000
GEOM_DEPTH_LIMIT = 15

# Required scheduled finish, not a claim that the generic OEM RFA implements it.
EXPECTED = {
    'alr1280090': {
        'model': 'LP549448', 'scheduled_variant': 'LP549448MBCL',
        'finish': 'Matte Black / Clear', 'host': 'ceiling',
        'terms': [('matte black', ['matte black', 'black', 'mb']),
                  ('clear', ['clear', 'transparent', 'cl'])]},
    'kzc1353667': {
        'model': 'PD3106', 'scheduled_variant': 'PD3106-BG',
        'finish': 'Brushed Gold', 'host': 'ceiling',
        'terms': [('brushed gold', ['brushed gold', 'bg'])]},
    'mfr1415595': {
        'model': 'FR-W2502-52L', 'scheduled_variant': 'FR-W2502-52L-SB/MB',
        'finish': 'Soft Brass / Matte Black', 'host': 'ceiling',
        'terms': [('soft brass', ['soft brass', 'sb']),
                  ('matte black', ['matte black', 'black', 'mb'])]},
    'mfr201959': {
        'model': 'WS-3127', 'scheduled_variant': 'WS-3127-CH',
        'finish': 'Chrome', 'host': 'wall',
        'terms': [('chrome', ['chrome', 'chromium', 'ch'])]}
}

def as_text(value):
    if value is None:
        return None
    try:
        return unicode(value)
    except Exception:
        try:
            return str(value).decode('utf-8', 'replace')
        except Exception:
            return repr(value)

def stamp():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

def progress(stage, family=None, detail=None):
    msg = {'utc': stamp(), 'stage': stage, 'family': family, 'detail': detail}
    with open(PROGRESS, 'a') as stream:
        stream.write(json.dumps(msg, ensure_ascii=True, default=as_text) + '\n')
    print('OEM_QA %s %s' % (family or 'batch', stage))
    sys.stdout.flush()

def save_receipt_once(data):
    if os.path.exists(OUTPUT):
        raise RuntimeError('OEM QA receipt exists: refusing overwrite ' + OUTPUT)
    temp = OUTPUT + '.tmp'
    with open(temp, 'w') as stream:
        json.dump(data, stream, ensure_ascii=True, indent=2, default=as_text)
    if os.path.exists(OUTPUT):
        raise RuntimeError('OEM QA receipt appeared during run; preserving existing file')
    os.rename(temp, OUTPUT)

def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            h.update(block)
    return h.hexdigest()

def file_fingerprint(path):
    return {'path': path, 'sha256': digest(path), 'bytes': os.path.getsize(path)}

def value_id(element_id):
    if element_id is None:
        return None
    try:
        return int(element_id.Value)
    except Exception:
        try:
            return int(element_id.IntegerValue)
        except Exception:
            return None

def safe_name(element):
    try:
        return as_text(element.Name)
    except Exception:
        return None

def safe_category(element):
    try:
        return as_text(element.Category.Name) if element.Category else None
    except Exception:
        return None

def material_description(doc, matid):
    n = value_id(matid)
    if n is None or n < 0:
        return {'id': n, 'name': None, 'bound': False}
    mat = doc.GetElement(matid)
    if mat is None:
        return {'id': n, 'name': None, 'bound': False}
    result = {'id': n, 'name': safe_name(mat), 'bound': True}
    try:
        result['appearance_asset_name'] = safe_name(doc.GetElement(mat.AppearanceAssetId))
    except Exception:
        pass
    try:
        color = mat.Color
        result['rgb'] = [int(color.Red), int(color.Green), int(color.Blue)]
        result['transparency'] = int(mat.Transparency)
    except Exception:
        pass
    return result

def parameter_type_value(family_type, param, doc):
    name = as_text(param.Definition.Name)
    storage = as_text(param.StorageType)
    entry = {'name': name, 'is_instance': bool(param.IsInstance),
             'storage_type': storage}
    try:
        entry['formula'] = as_text(param.Formula)
    except Exception:
        pass
    try:
        entry['display'] = as_text(family_type.AsValueString(param))
    except Exception:
        entry['display'] = None
    try:
        if storage == 'ElementId':
            mid = family_type.AsElementId(param)
            entry['id_value'] = value_id(mid)
            datatype = ''
            try:
                datatype = as_text(param.Definition.GetDataType().TypeId)
            except Exception:
                pass
            if 'material' in (datatype or '').lower() or 'material' in name.lower():
                entry['material'] = material_description(doc, mid)
        elif storage == 'String':
            entry['value'] = as_text(family_type.AsString(param))
        elif storage == 'Double':
            v = family_type.AsDouble(param)
            entry['value_internal'] = float(v) if v is not None else None
        elif storage == 'Integer':
            v = family_type.AsInteger(param)
            entry['value'] = int(v) if v is not None else None
    except Exception as exc:
        entry['read_error'] = as_text(exc)
    return entry

def inspect_family_types(doc):
    manager = doc.FamilyManager
    types = list(manager.Types)
    parameters = list(manager.Parameters)
    relevant = ('finish', 'material', 'colour', 'color', 'glass', 'metal',
                'light', 'photometric', 'ies', 'lumen', 'watt', 'kelvin',
                'temperature', 'voltage', 'cri', 'cct', 'beam', 'source',
                'intensity', 'model', 'manufacturer', 'description')
    param_names = [as_text(p.Definition.Name) for p in parameters]
    result = {'count': len(types), 'parameter_count': len(parameters),
              'parameter_names': param_names, 'types': []}
    for typ in types:
        row = {'name': as_text(typ.Name), 'materials': [],
               'finish_fields': [], 'photometry_fields': [], 'identity_fields': []}
        for p in parameters:
            pname = as_text(p.Definition.Name).lower()
            if not any(t in pname for t in relevant):
                continue
            info = parameter_type_value(typ, p, doc)
            if 'material' in pname or 'finish' in pname or 'color' in pname or 'colour' in pname:
                row['materials'].append(info)
            if 'finish' in pname or 'color' in pname or 'colour' in pname:
                row['finish_fields'].append(info)
            if any(x in pname for x in ('light', 'photometric', 'ies', 'lumen', 'watt',
                                        'kelvin', 'temperature', 'voltage', 'cri',
                                        'cct', 'beam', 'source', 'intensity')):
                row['photometry_fields'].append(info)
            if any(x in pname for x in ('model', 'manufacturer', 'description')):
                row['identity_fields'].append(info)
        result['types'].append(row)
    result['materials_defined'] = []
    for m in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        result['materials_defined'].append(material_description(doc, m.Id))
    return result

def has_alias(value, aliases):
    v = re.sub('[^a-z0-9]+', ' ', (value or '').lower()).strip()
    for alias in aliases:
        a = re.sub('[^a-z0-9]+', ' ', alias.lower()).strip()
        if a and re.search(r'\b' + re.escape(a) + r'\b', v):
            return True
    return False

def finish_diagnosis(type_info, specification):
    candidates = []
    for row in type_info['types']:
        evidence = [row['name']]
        for param in row['materials'] + row['identity_fields']:
            for field in ('display', 'value'):
                if param.get(field):
                    evidence.append(as_text(param[field]))
            if param.get('material') and param['material'].get('name'):
                evidence.append(param['material']['name'])
        joined = ' | '.join([x for x in evidence if x])
        found = {}
        for name, aliases in specification['terms']:
            found[name] = has_alias(joined, aliases)
        candidates.append({'type': row['name'], 'evidence': evidence,
                           'required_finish_matches': found,
                           'matched_count': sum(1 for hit in found.values() if hit)})
    candidates.sort(key=lambda r: -r['matched_count'])
    any_full = [r for r in candidates if r['matched_count'] == len(specification['terms'])]
    # The OEM definition may contain multiple variants; report, do not mutate
    # FamilyManager.CurrentType or silently select a finish.
    selected = candidates[0] if candidates else None
    if any_full:
        outcome = 'MATCH_AVAILABLE_TYPE_UNSELECTED'
    elif selected is not None and selected['matched_count']:
        outcome = 'PARTIAL_FINISH_MATCH'
    else:
        outcome = 'FINISH_UNVERIFIED'
    return {'scheduled_variant': specification['scheduled_variant'],
            'scheduled_finish': specification['finish'],
            'status': outcome, 'matching_types': [x['type'] for x in any_full],
            'best_candidate': selected, 'type_candidates': candidates,
            'explicit_binding_verification': False}

def collect_connectors(doc):
    report = {'family_connector_elements': [], 'electrical_connector_count': 0,
              'photometry_status': 'NOT_CALIBRATED_BY_THIS_AUDIT',
              'light_source_elements': []}
    try:
        for conn in DB.FilteredElementCollector(doc).OfClass(DB.ConnectorElement):
            detail = {'id': value_id(conn.Id), 'name': safe_name(conn),
                      'category': safe_category(conn)}
            try:
                detail['domain'] = as_text(conn.Domain)
            except Exception:
                pass
            report['family_connector_elements'].append(detail)
            if 'electrical' in (detail.get('domain') or '').lower():
                report['electrical_connector_count'] += 1
    except Exception as exc:
        report['connector_collection_error'] = as_text(exc)
    try:
        for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
            cname = safe_category(e) or ''
            cls = as_text(e.GetType().Name)
            if 'light source' in cname.lower() or 'lightsource' in (cls or '').lower():
                report['light_source_elements'].append({
                    'id': value_id(e.Id), 'name': safe_name(e), 'class': cls})
    except Exception as exc:
        report['light_collection_error'] = as_text(exc)
    report['light_source_detected'] = bool(report['light_source_elements'])
    return report

class GeometryAudit(object):
    def __init__(self):
        self.minimum = [float('inf')] * 3
        self.maximum = [float('-inf')] * 3
        self.point_count = 0
        self.solid_count = 0
        self.mesh_count = 0
        self.nested_instances = 0
        self.errors = []
        self.material_ids = {}
        self.aborted = False

    def point(self, point):
        if self.point_count >= GEOM_POINT_LIMIT:
            self.aborted = True
            raise ValueError('Exceeded geometry vertex budget; envelope incomplete')
        xyz = [float(point.X), float(point.Y), float(point.Z)]
        for i in range(3):
            if xyz[i] < self.minimum[i]:
                self.minimum[i] = xyz[i]
            if xyz[i] > self.maximum[i]:
                self.maximum[i] = xyz[i]
        self.point_count += 1

    def mesh(self, m):
        self.mesh_count += 1
        for v in m.Vertices:
            self.point(v)

    def solid(self, solid):
        try:
            if solid.Volume <= 1e-12:
                return
        except Exception:
            return
        self.solid_count += 1
        for face in solid.Faces:
            try:
                fid = value_id(face.MaterialElementId)
                if fid is not None and fid >= 0:
                    key = str(fid)
                    self.material_ids[key] = self.material_ids.get(key, 0) + 1
            except Exception:
                pass
            try:
                self.mesh(face.Triangulate())
            except Exception as exc:
                self.errors.append('Triangulate: ' + as_text(exc))
        for edge in solid.Edges:
            try:
                curve = edge.AsCurve()
                count = 2 if isinstance(curve, DB.Line) else 97
                for i in range(count):
                    self.point(curve.Evaluate(float(i) / float(count - 1), True))
            except Exception as exc:
                self.errors.append('Analytic edge: ' + as_text(exc))

    def walk(self, geometry, depth=0):
        if depth > GEOM_DEPTH_LIMIT:
            self.aborted = True
            self.errors.append('Nested family geometry exceeds recursion depth')
            return
        if geometry is None:
            self.errors.append('Geometry returned None')
            return
        for part in geometry:
            if self.aborted:
                return
            try:
                if isinstance(part, DB.GeometryInstance):
                    self.nested_instances += 1
                    # Revit GetInstanceGeometry() applies the instance transform.
                    self.walk(part.GetInstanceGeometry(), depth + 1)
                elif isinstance(part, DB.Solid):
                    self.solid(part)
                elif isinstance(part, DB.Mesh):
                    self.mesh(part)
            except Exception as exc:
                self.errors.append('Geometry traversal: ' + as_text(exc))

    def receipt(self, doc):
        available = (self.point_count > 0 and
                     self.solid_count + self.mesh_count > 0)
        result = {'available': available, 'complete': bool(available and
                  not self.errors and not self.aborted),
                  'solid_count': self.solid_count,
                  'mesh_count': self.mesh_count,
                  'nested_geometry_instances': self.nested_instances,
                  'point_count': self.point_count, 'errors': self.errors,
                  'aborted': self.aborted,
                  'measurement_method': 'visible native solids/meshes, triangulated faces and sampled analytic edges; nested GetInstanceGeometry()'}
        if available:
            result['minimum_xyz_mm'] = [round(x * MM_PER_FOOT, 5) for x in self.minimum]
            result['maximum_xyz_mm'] = [round(x * MM_PER_FOOT, 5) for x in self.maximum]
            result['xyz_mm'] = [round((b-a) * MM_PER_FOOT, 5)
                                for a,b in zip(self.minimum, self.maximum)]
            result['xyz_in'] = [round((b-a) * 12., 6)
                                for a,b in zip(self.minimum, self.maximum)]
        result['geometry_face_materials'] = [
            {'face_count': count, 'material': material_description(doc, DB.ElementId(int(key)))}
            for key, count in sorted(self.material_ids.items())]
        return result

def family_geometry(doc):
    opts = DB.Options()
    opts.DetailLevel = DB.ViewDetailLevel.Fine
    opts.IncludeNonVisibleObjects = False
    audit = GeometryAudit()
    per_class = {}
    excluded = []
    for element in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        if not isinstance(element, (DB.GenericForm, DB.ImportInstance, DB.FamilyInstance)):
            continue
        category = safe_category(element) or ''
        if 'light source' in category.lower() or 'reference plane' in category.lower():
            excluded.append({'id': value_id(element.Id), 'category': category,
                             'name': safe_name(element)})
            continue
        kind = as_text(element.GetType().Name)
        per_class[kind] = per_class.get(kind, 0) + 1
        try:
            audit.walk(element.get_Geometry(opts))
        except Exception as exc:
            audit.errors.append('%s id=%s: %s' % (kind, value_id(element.Id), as_text(exc)))
    result = audit.receipt(doc)
    result['element_class_counts'] = per_class
    result['excluded_reference_or_light_elements'] = excluded
    result['scope'] = 'family-document geometry only; corroboration required from placed instance'
    return result

def warnings(doc):
    values = []
    for warning in doc.GetWarnings():
        try:
            text = as_text(warning.GetDescriptionText())
        except Exception:
            text = as_text(warning)
        values.append(text)
    return values

def project_placement(family_doc, family_spec, types):
    outcome = {'attempted': True, 'success': False, 'host_verified': False,
               'warnings': [], 'attempts': [], 'geometry': {'available': False},
               'isolated_disposable_project': True}
    project = None
    tx = None
    try:
        project = APP.NewProjectDocument(DB.UnitSystem.Imperial)
        if project is None:
            raise RuntimeError('NewProjectDocument returned None')
        family = family_doc.LoadFamily(project)
        if family is None:
            raise RuntimeError('LoadFamily returned None')
        symbol_ids = list(family.GetFamilySymbolIds())
        if not symbol_ids:
            raise RuntimeError('No project FamilySymbol ids found')
        symbols = [project.GetElement(i) for i in symbol_ids]
        # Testing a representative type is not proof of a requested finish.
        preferred = []
        candidates = family_spec.get('matching_types', [])
        for symbol in symbols:
            preferred.append((0 if safe_name(symbol) in candidates else 1, safe_name(symbol), symbol))
        preferred.sort(key=lambda t: (t[0], t[1] or ''))
        symbol = preferred[0][2]
        outcome['tested_type'] = safe_name(symbol)
        outcome['family_placement_type'] = as_text(family.FamilyPlacementType)
        tx = DB.Transaction(project, 'Disposable PH Good OEM native QA (rolled back)')
        tx.Start()
        levels = list(DB.FilteredElementCollector(project).OfClass(DB.Level))
        level = levels[0] if levels else DB.Level.Create(project, 0.0)
        walltype = next((x for x in DB.FilteredElementCollector(project).OfClass(DB.WallType)
                         if x.Kind == DB.WallKind.Basic), None)
        wall = None
        floor = None
        if walltype is not None:
            wall = DB.Wall.Create(project, DB.Line.CreateBound(
                DB.XYZ(-8,0,0), DB.XYZ(8,0,0)), walltype.Id, level.Id,
                10., 0., False, False)
        try:
            perimeter = DB.CurveLoop()
            z = 10.
            xy = [(-8.,-8.),(8.,-8.),(8.,8.),(-8.,8.),(-8.,-8.)]
            for i in range(4):
                a, b = xy[i], xy[i+1]
                perimeter.Append(DB.Line.CreateBound(DB.XYZ(a[0],a[1],z),
                                                     DB.XYZ(b[0],b[1],z)))
            default_floor_type = DB.Floor.GetDefaultFloorType(project, False)
            if value_id(default_floor_type) is not None and value_id(default_floor_type) >= 0:
                floor = DB.Floor.Create(project, List[DB.CurveLoop]([perimeter]),
                                        default_floor_type, level.Id)
        except Exception as exc:
            outcome['floor_host_error'] = as_text(exc)
        symbol.Activate()
        project.Regenerate()

        refs = []
        if wall is not None:
            try:
                wr = list(DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior))[0]
                wf = wall.GetGeometryObjectFromReference(wr)
                hit = wf.Project(DB.XYZ(0,0,5.))
                refs.append(('wall_face', wr, hit.XYZPoint, wall))
            except Exception as exc:
                outcome['wall_face_error'] = as_text(exc)
        if floor is not None:
            try:
                fr = list(DB.HostObjectUtils.GetBottomFaces(floor))[0]
                ff = floor.GetGeometryObjectFromReference(fr)
                hit = ff.Project(DB.XYZ(0,0,10.))
                refs.append(('ceiling_face', fr, hit.XYZPoint, floor))
            except Exception as exc:
                outcome['ceiling_face_error'] = as_text(exc)
        # Try intended face first; optional fallback reveals actual constraints.
        face_order = sorted(refs, key=lambda r: 0 if
                            ('ceiling' if family_spec['host'] == 'ceiling' else 'wall') in r[0] else 1)
        possibilities = []
        for name, ref, xyz, host in face_order:
            possibilities.append((name, ref, xyz, host))
        possibilities.append(('level_point', None, DB.XYZ(0,0,8.), None))
        for name, ref, xyz, host in possibilities:
            sub = DB.SubTransaction(project)
            sub.Start()
            try:
                if ref is None:
                    inst = project.Create.NewFamilyInstance(
                        xyz, symbol, level, DB.Structure.StructuralType.NonStructural)
                else:
                    inst = project.Create.NewFamilyInstance(ref, xyz, DB.XYZ.BasisX, symbol)
                project.Regenerate()
                actual_host = inst.Host
                hosted = bool(actual_host is not None and
                              host is not None and actual_host.Id == host.Id)
                try:
                    hosted = hosted and inst.HostFace is not None
                except Exception:
                    pass
                location = None
                try:
                    p = inst.Location.Point
                    location = [float(p.X), float(p.Y), float(p.Z)]
                except Exception:
                    pass
                wa = warnings(project)
                placement = {'method': name, 'created': True,
                             'symbol_name': safe_name(inst.Symbol),
                             'hosted_on_expected_element': hosted,
                             'host_id': value_id(actual_host.Id) if actual_host else None,
                             'location_ft': location, 'warnings': wa}
                audit = GeometryAudit()
                options = DB.Options()
                options.IncludeNonVisibleObjects = False
                options.DetailLevel = DB.ViewDetailLevel.Fine
                audit.walk(inst.get_Geometry(options))
                placement['geometry'] = audit.receipt(project)
                outcome['attempts'].append(placement)
                # A level-based family has no physical host. A face/host-based
                # variant must match the intended actual wall/ceiling face.
                family_pt = (outcome['family_placement_type'] or '').lower()
                requires_host = ('host' in family_pt or 'workplane' in family_pt)
                intended = (name == (family_spec['host'] + '_face'))
                okay = not wa and placement['geometry']['complete']
                if requires_host:
                    okay = okay and hosted and intended
                if okay:
                    outcome['success'] = True
                    outcome['host_verified'] = hosted
                    outcome['host_test_method'] = name
                    outcome['warnings'] = wa
                    outcome['geometry'] = placement['geometry']
                    sub.RollBack()
                    break
                sub.RollBack()
            except Exception as exc:
                outcome['attempts'].append({'method': name, 'created': False,
                                            'error': as_text(exc)})
                try:
                    sub.RollBack()
                except Exception:
                    pass
        if not outcome['success']:
            outcome['reason'] = 'No verified host/placement with complete visible geometry'
        tx.RollBack()
        tx = None
    except Exception:
        outcome['error'] = traceback.format_exc()
    finally:
        if tx is not None:
            try:
                tx.RollBack()
            except Exception:
                pass
        if project is not None:
            try:
                project.Close(False)
            except Exception as exc:
                outcome['project_close_error'] = as_text(exc)
    return outcome

def compare_previous_receipt(receipt, measured):
    prior = receipt.get('dimensions', {})
    old = prior.get('xyz_mm')
    if not old:
        return {'evaluated': False, 'reason': 'Previous receipt missing XYZ'}
    if not measured.get('complete'):
        return {'evaluated': False, 'prior_xyz_mm': old,
                'reason': 'Independent placed native envelope missing or incomplete'}
    new = measured['xyz_mm']
    deltas = [round(float(new[i]) - float(old[i]), 5) for i in range(3)]
    return {'evaluated': True, 'prior_xyz_mm': old,
            'actual_placed_xyz_mm': new, 'delta_actual_minus_prior_mm': deltas,
            'max_abs_difference_mm': round(max(abs(x) for x in deltas), 5),
            'agreement_with_prior_within_1mm': max(abs(x) for x in deltas) <= 1.0,
            'note': 'Disagreement may expose template/light-source/control geometry in the earlier source-document measurement; investigate measured solid provenance.'}

def audit_one(job):
    jid = job['id']
    spec = EXPECTED[jid]
    path = job['target_rfa']
    previous_path = os.path.join(RUNNER, 'receipts', jid + '.json')
    old = json.load(open(previous_path, 'r'))
    record = {'id': jid, 'model': spec['model'],
              'scheduled_variant': spec['scheduled_variant'],
              'scheduled_finish': spec['finish'],
              'family_path': path,
              'previous_native_batch': {'status': old.get('status'),
                                        'technical_pass': old.get('technical_pass'),
                                        'warnings': old.get('warning_count'),
                                        'dimension_fit_evaluated': old.get('dimension_fit', {}).get('evaluated', False)}}
    family_doc = None
    before = file_fingerprint(path)
    input_before = file_fingerprint(job['source_rfa'])
    try:
        progress('OPEN_FAMILY', jid)
        family_doc = APP.OpenDocumentFile(path)
        if not family_doc.IsFamilyDocument:
            raise RuntimeError('Expected an RFA FamilyDocument')
        record['category'] = as_text(family_doc.OwnerFamily.FamilyCategory.Name)
        record['category_pass'] = record['category'] == 'Lighting Fixtures'
        record['placement_type'] = as_text(family_doc.OwnerFamily.FamilyPlacementType)
        record['family_warning_messages'] = warnings(family_doc)
        record['family_warning_count'] = len(record['family_warning_messages'])
        progress('TYPES_AND_FINISH', jid)
        types = inspect_family_types(family_doc)
        record['type_and_materials'] = types
        finish = finish_diagnosis(types, spec)
        record['finish_diagnosis'] = finish
        progress('CONNECTOR_AND_PHOTOMETRY', jid)
        record['connectors_and_light'] = collect_connectors(family_doc)
        progress('SOURCE_GEOMETRY', jid)
        record['family_geometry'] = family_geometry(family_doc)
        progress('DISPOSABLE_PLACEMENT', jid)
        placed = project_placement(family_doc, spec, finish)
        record['temporary_project_placement'] = placed
        record['dimension_comparison_previous'] = compare_previous_receipt(
            old, placed.get('geometry', {}))
        # Comparing to the exact manufacturer dimensional scope requires a
        # separately authoritative cut-sheet envelope (overall/fixture/body).
        record['manufacturer_dimensions_mm'] = None
        record['manufacturer_dimension_match'] = 'NOT_EVALUATED_SOURCE_SCOPE_REQUIRED'
        record['material_finish_release'] = 'REVIEW_REQUIRED'
        record['photometric_release'] = 'UNVERIFIED'
        record['qa_pass'] = (record['category_pass'] and
                            record['family_warning_count'] == 0 and
                            placed['success'] and
                            placed.get('geometry', {}).get('complete', False))
        record['status'] = 'TECHNICAL_PASS_FINISH_HOLD' if record['qa_pass'] else 'HOLD'
        if not record['qa_pass']:
            record['review_reasons'] = ['Complete placed geometry and category/warnings/hosting gate not established']
    except Exception:
        record['status'] = 'ERROR'
        record['error'] = traceback.format_exc()
    finally:
        if family_doc is not None:
            try:
                family_doc.Close(False)
            except Exception as exc:
                record['close_error'] = as_text(exc)
        record['family_file_before'] = before
        record['family_file_after'] = file_fingerprint(path)
        record['oem_input_before'] = input_before
        record['oem_input_after'] = file_fingerprint(job['source_rfa'])
        record['files_unchanged'] = (
            before['sha256'] == record['family_file_after']['sha256'] and
            input_before['sha256'] == record['oem_input_after']['sha256'])
        record['matches_prior_output_sha256'] = (
            before['sha256'] == old.get('rfa_sha256'))
        if not record['files_unchanged'] or not record['matches_prior_output_sha256']:
            record['status'] = 'FAIL_HASH_CHANGE'
            record['qa_pass'] = False
    progress('FAMILY_COMPLETE', jid, record['status'])
    return record

def main():
    if str(APP.VersionNumber) != '2025':
        raise RuntimeError('Requires Revit 2025; observed ' + as_text(APP.VersionNumber))
    if getattr(__revit__, 'ActiveUIDocument', None) is not None:
        raise RuntimeError('Refusing to audit in a user document session; use isolated pyrevit run')
    if os.path.exists(OUTPUT):
        raise RuntimeError('Existing QA result cannot be overwritten: ' + OUTPUT)
    if not os.path.exists(QA_DIR):
        os.makedirs(QA_DIR)
    manifest = json.load(open(MANIFEST, 'r'))
    jobs = [j for j in manifest.get('families', []) if j.get('mode') == 'oem']
    ids = [j.get('id') for j in jobs]
    if len(jobs) != 4 or set(ids) != set(EXPECTED.keys()):
        raise RuntimeError('Expected precisely four known OEM families: ' + as_text(ids))
    for job in jobs:
        if not os.path.isfile(job['source_rfa']) or not os.path.isfile(job['target_rfa']):
            raise RuntimeError('RFA file missing: ' + job['id'])
        if not os.path.isfile(os.path.join(RUNNER, 'receipts', job['id'] + '.json')):
            raise RuntimeError('Missing previous native receipt for ' + job['id'])
    started = time.time()
    progress('BATCH_START', None, {'families': ids})
    report = {'schema_version': 1, 'purpose': '651 Belmont PH GOOD OEM independent native QA',
              'revit_version': as_text(APP.VersionNumber),
              'started_utc': stamp(), 'family_count': len(jobs),
              'read_only_sources': True, 'disposable_project_saved': False,
              'results': []}
    for job in jobs:
        try:
            report['results'].append(audit_one(job))
        except Exception:
            report['results'].append({'id': job['id'], 'status': 'ERROR',
                                      'error': traceback.format_exc()})
    report['completed_utc'] = stamp()
    report['duration_seconds'] = round(time.time() - started, 3)
    report['technical_pass_count'] = sum(1 for r in report['results'] if r.get('qa_pass'))
    report['finished_count'] = len(report['results'])
    report['release_ready'] = False
    report['release_holds'] = ['Exact type/finish and OEM dimensions require confirmed manufacturer source/variant review',
                               'Native emitter/IES quality and visual review are separate from file/placement inspection']
    save_receipt_once(report)
    progress('BATCH_COMPLETE', None, {'count': report['finished_count'],
                                      'technical_pass_count': report['technical_pass_count'],
                                      'release_ready': False})
    print('OEM_QA receipt ' + OUTPUT)

main()
