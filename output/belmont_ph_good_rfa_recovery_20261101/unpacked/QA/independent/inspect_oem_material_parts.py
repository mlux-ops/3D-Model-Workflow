# -*- coding: utf-8 -*-
r"""651 Belmont PH Good: READ-ONLY native RFA material/geometry part probe.

STANDALONE, IronPython 2.7 / Revit 2025. NO Revit launch inside this script.
Run only from an ISOLATED pyRevit 2025 command session (no open user project):

  D:\Games\pyRevit-Master\bin\pyrevit.exe run "E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\inspect_oem_material_parts.py" --revit=2025

Reads the TWO previously saved OEM-source family copies at BASE/families:
  Kuzco_Bolla_PD3106_BG_R2025.rfa
  ModernForms_Smooth_FR-W2502-52L_SBMB_R2025.rfa
The downloaded OEM originals at BASE/sources/oem are only fingerprinted.

On actual native execution, creates ONE NEW receipt:
  BASE/qa/inspect_oem_material_parts.json
Never overwrites a receipt or any original RFA. Never creates/saves project
documents, edits type selections, starts a transaction or calls Save/SaveAs.
Every opened family document is closed with Close(False).

Bounding boxes are computed from actual visible physical SOLID/MESH geometry
vertices plus sampled analytic edges in FAMILY LOCAL COORDINATES. Imported
and nested geometry uses GetSymbolGeometry + composed transformations to
avoid incorrect/double placement transforms. 3D bounds use triangulated and
sampled geometry; they are not Autodesk Element.get_BoundingBox() extents
and are not guaranteed mathematical extrema for curved freeform surfaces.
Curve-only graphics are kept separate from physical solid/mesh bounds.

Face material IDs, element material parameters, graphics-style layer material
IDs and import subcategory materials have distinct origins in the JSON.
NO material is labeled 'gold', 'glass', 'housing' or 'blade' solely by color,
subcategory or vertical position. Geometry/material provenance is the gate
for making those decisions in a future, separately authorized native edit.
"""

from __future__ import print_function
import os
import sys
import time
import json
import hashlib
import math
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
OUTPUT = os.path.join(BASE, 'qa', 'inspect_oem_material_parts.json')
APP = __revit__.Application
MM_PER_FOOT = 304.8
MAX_RECURSION = 18
MAX_GEOMETRY_POINTS_PER_FAMILY = 900000
MAX_ERRORS_PER_FAMILY = 35
COORD_DECIMALS = 2

# These hashes were cross-checked against the actual files on 2026-10-16.
# Report a hash mismatch; never silently treat a new file as prior QA-approved.
INPUTS = [
    {
        'id': 'kzc1353667',
        'model': 'PD3106-BG',
        'manufacturer': 'Kuzco',
        'target_finish': 'Brushed Gold metal, clear outer and opal inner glass',
        'saved_rfa': os.path.join(BASE, 'families',
                                  'Kuzco_Bolla_PD3106_BG_R2025.rfa'),
        'saved_sha256': 'eb5cf17c25531152acc8e51ccb0ad5bd80913ae547f878d9108d059090e6f2f3',
        'downloaded_oem_rfa': os.path.join(
            BASE, 'sources', 'oem', 'extracted',
            'KZC1353667_PD3106_Bolla_Revit', 'PD3106 - Bolla.rfa'),
        'downloaded_oem_sha256': '8d84d0a6842b26ca3b8686f86948172349d1d1aec04a75a2b68af4463ef5c98a',
    },
    {
        'id': 'mfr1415595',
        'model': 'FR-W2502-52L-SB/MB',
        'manufacturer': 'Modern Forms',
        'target_finish': 'Soft Brass housing, Matte Black three blades, opal lens',
        'saved_rfa': os.path.join(
            BASE, 'families', 'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025.rfa'),
        'saved_sha256': '45c76b46fba9daebcf5d0ebbedb7b5592d4eaa50cbbd4b5b59fe44321b7b8e18',
        'downloaded_oem_rfa': os.path.join(
            BASE, 'sources', 'oem', 'extracted',
            'MFR1415595_FR-W2502_Smooth_Revit', 'FR-W2502-52L.rfa'),
        'downloaded_oem_sha256': '5275e71a2d6cfd033b4cb6d6fa1351d0e78c953586bdbcafe2b905893286d617',
    },
]


def ascii_text(value):
    """Avoid IronPython/.NET localized-name implicit decode at JSON boundary."""
    if value is None:
        return None
    try:
        s = unicode(value)
    except Exception:
        try:
            s = str(value).decode('utf-8', 'replace')
        except Exception:
            s = u'[UNPRINTABLE]'
    out = []
    for char in s:
        n = ord(char)
        if n > 126 or (n < 32 and n not in (9, 10, 13)):
            out.append('[U+%04X]' % n)
        elif n in (9, 10, 13):
            out.append(' ')
        else:
            out.append(chr(n))
    return ''.join(out)


def element_id(value):
    if value is None:
        return None
    try:
        return int(value.Value)
    except Exception:
        try:
            return int(value.IntegerValue)
        except Exception:
            return None


def valid_id(value):
    n = element_id(value)
    return n is not None and n >= 0


def element_name(elem):
    if elem is None:
        return None
    try:
        return ascii_text(DB.Element.Name.GetValue(elem))
    except Exception:
        try:
            return ascii_text(elem.Name)
        except Exception:
            try:
                p = elem.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
                return ascii_text(p.AsString()) if p is not None else None
            except Exception:
                return None


def category_desc(category):
    if category is None:
        return None
    d = {'id': element_id(category.Id), 'name': ascii_text(category.Name)}
    try:
        d['parent_id'] = element_id(category.Parent.Id) if category.Parent else None
        d['parent'] = ascii_text(category.Parent.Name) if category.Parent else None
    except Exception:
        pass
    try:
        d['material_id'] = element_id(category.Material.Id) if category.Material else None
    except Exception:
        pass
    return d


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def fingerprint(path, expected):
    if not os.path.isfile(path):
        return {'path': path, 'exists': False, 'expected_sha256': expected,
                'matches_expected_sha256': False}
    current = sha256(path)
    return {'path': path, 'exists': True, 'size_bytes': int(os.path.getsize(path)),
            'sha256': current, 'expected_sha256': expected,
            'matches_expected_sha256': current.lower() == expected.lower()}


def rounded(v):
    return round(float(v), COORD_DECIMALS)


def stamp():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


class Extents(object):
    def __init__(self):
        self.low = [float('inf')] * 3
        self.high = [float('-inf')] * 3
        self.points = 0

    def push(self, value):
        coords = [float(value.X), float(value.Y), float(value.Z)]
        for i in range(3):
            if coords[i] < self.low[i]:
                self.low[i] = coords[i]
            if coords[i] > self.high[i]:
                self.high[i] = coords[i]
        self.points += 1

    def merge(self, other):
        if other.points == 0:
            return
        for i in range(3):
            if other.low[i] < self.low[i]:
                self.low[i] = other.low[i]
            if other.high[i] > self.high[i]:
                self.high[i] = other.high[i]
        self.points += other.points

    def json(self, global_low_z_ft=None):
        if not self.points:
            return None
        lo = [rounded(v * MM_PER_FOOT) for v in self.low]
        hi = [rounded(v * MM_PER_FOOT) for v in self.high]
        report = {
            'min_xyz_mm': lo,
            'max_xyz_mm': hi,
            'size_xyz_mm': [rounded((self.high[i] - self.low[i]) * MM_PER_FOOT)
                            for i in range(3)],
            'z_from_family_origin_mm': [lo[2], hi[2]],
        }
        if global_low_z_ft is not None:
            report['z_offset_above_family_lowest_mm'] = rounded(
                (self.low[2] - global_low_z_ft) * MM_PER_FOOT)
        return report


class Group(object):
    def __init__(self, key, descriptor):
        self.key = key
        self.descriptor = descriptor
        self.physical = Extents()
        self.curves = Extents()
        self.solid_count = 0
        self.mesh_count = 0
        self.face_count = 0
        self.mesh_triangle_count = 0
        self.curve_count = 0

    def json(self, lowest_z):
        d = dict(self.descriptor)
        d.update({
            'solid_count': self.solid_count,
            'mesh_count': self.mesh_count,
            'face_count': self.face_count,
            'mesh_triangle_count': self.mesh_triangle_count,
            'curve_count': self.curve_count,
            'physical_aabb_mm': self.physical.json(lowest_z),
            'curve_only_aabb_mm': self.curves.json(),
        })
        return d


class Probe(object):
    def __init__(self, doc, max_points):
        self.doc = doc
        self.max_points = max_points
        self.total_points = 0
        self.errors = []
        self.truncated = False
        self.groups = {}
        self.all_physical = Extents()
        self.all_curves = Extents()
        self.instanced = []
        self.group_key_length = 0

    def warn(self, error):
        self.truncated = True
        if len(self.errors) < MAX_ERRORS_PER_FAMILY:
            self.errors.append(ascii_text(error))

    def push(self, group, point, transform, physical):
        if self.total_points >= self.max_points:
            if not self.truncated:
                self.warn('Geometry point budget reached before complete AABB')
            return False
        try:
            p = transform.OfPoint(point)
            if physical:
                group.physical.push(p)
                self.all_physical.push(p)
            else:
                group.curves.push(p)
                self.all_curves.push(p)
            self.total_points += 1
            return True
        except Exception as ex:
            self.warn('Transform.OfPoint failed: ' + ascii_text(ex))
            return False

    def graphics(self, obj):
        styleid = None
        try:
            styleid = element_id(obj.GraphicsStyleId)
        except Exception:
            pass
        style = self.doc.GetElement(DB.ElementId(styleid)) if styleid is not None and styleid >= 0 else None
        category = None
        if style is not None:
            try:
                category = style.GraphicsStyleCategory
            except Exception:
                pass
        d = {'graphics_style_id': styleid,
             'subcategory': category_desc(category)}
        if category is not None:
            try:
                d['graphics_style_type'] = ascii_text(style.GraphicsStyleType)
            except Exception:
                pass
        return d

    def group(self, path, obj, material_id, material_source, primitive):
        gs = self.graphics(obj)
        subtype = gs.get('subcategory') or {}
        key = ('/'.join(path), primitive, str(material_id),
               material_source, str(gs.get('graphics_style_id')),
               str(subtype.get('id')))
        if key not in self.groups:
            self.groups[key] = Group(key, {
                'nested_path': list(path),
                'primitive': primitive,
                'material_id': material_id,
                'material_source': material_source,
                'graphics_style_id': gs.get('graphics_style_id'),
                'subcategory': gs.get('subcategory'),
            })
        return self.groups[key]

    def resolve_material(self, obj, face=None):
        if face is not None:
            try:
                if valid_id(face.MaterialElementId):
                    return element_id(face.MaterialElementId), 'face'
            except Exception:
                pass
        try:
            if valid_id(obj.MaterialElementId):
                return element_id(obj.MaterialElementId), 'mesh_or_object'
        except Exception:
            pass
        gs = self.graphics(obj)
        cat = gs.get('subcategory') or {}
        m = cat.get('material_id')
        if m is not None and m >= 0:
            return m, 'graphics_style_fallback'
        return None, 'unassigned'

    def add_curve(self, curve, transform, group, physical=False):
        group.curve_count += 1
        try:
            pts = list(curve.Tessellate())
            if len(pts) < 2:
                pts = [curve.GetEndPoint(0), curve.GetEndPoint(1)]
            # Nonlinear edges can attain extrema between tessellation vertices.
            if not isinstance(curve, DB.Line):
                for i in range(1, 33):
                    pts.append(curve.Evaluate(float(i) / 33.0, True))
            for p in pts:
                if not self.push(group, p, transform, physical):
                    return
        except Exception as ex:
            self.warn('Curve sample failure: ' + ascii_text(ex))

    def add_mesh(self, mesh, transform, group):
        group.mesh_count += 1
        try:
            group.mesh_triangle_count += int(mesh.NumTriangles)
        except Exception:
            pass
        try:
            for point in mesh.Vertices:
                if not self.push(group, point, transform, True):
                    return
        except Exception as ex:
            self.warn('Mesh vertex read failure: ' + ascii_text(ex))

    def add_solid(self, solid, transform, path):
        try:
            if solid.Volume <= 1e-12:
                return
        except Exception:
            return
        solid_material, solid_source = self.resolve_material(solid)
        shell_group = self.group(path, solid, solid_material,
                                 solid_source, 'Solid')
        shell_group.solid_count += 1
        try:
            for face in solid.Faces:
                matid, source = self.resolve_material(solid, face)
                group = self.group(path, solid, matid, source, 'SolidFace')
                group.face_count += 1
                try:
                    mesh = face.Triangulate()
                    self.add_mesh(mesh, transform, group)
                except Exception as ex:
                    self.warn('Solid face triangulation failed: ' + ascii_text(ex))
            for edge in solid.Edges:
                try:
                    # Analytic edge samples complement face tessellation.
                    curve = edge.AsCurve()
                    self.add_curve(curve, transform, shell_group, True)
                except Exception as ex:
                    self.warn('Solid analytic edge failed: ' + ascii_text(ex))
        except Exception as ex:
            self.warn('Solid traversal failure: ' + ascii_text(ex))

    def walk(self, geom, transform, path, depth):
        if geom is None:
            return
        if depth > MAX_RECURSION:
            self.warn('Nested symbol geometry exceeded recursion limit')
            return
        if self.total_points >= self.max_points:
            self.warn('Point budget exhausted')
            return
        try:
            for obj in geom:
                if self.total_points >= self.max_points:
                    self.warn('Point budget exhausted')
                    return
                if isinstance(obj, DB.GeometryInstance):
                    child = None
                    mode = None
                    try:
                        inner = obj.GetSymbolGeometry()
                        if inner is None:
                            raise RuntimeError('GetSymbolGeometry returned None')
                        child = transform.Multiply(obj.Transform)
                        mode = 'symbol_geometry_with_explicit_composed_transform'
                    except Exception:
                        try:
                            inner = obj.GetInstanceGeometry()
                            child = transform
                            mode = 'instance_geometry_already_transformed'
                        except Exception as ex:
                            self.warn('GeometryInstance expansion failed: ' + ascii_text(ex))
                            continue
                    symid = None
                    symbol_name = None
                    try:
                        symbol = obj.Symbol
                        symid = element_id(symbol.Id)
                        symbol_name = element_name(symbol)
                    except Exception:
                        pass
                    label = 'GI-%s-%s' % (str(symid), len(self.instanced))
                    self.instanced.append({
                        'path': path + [label], 'symbol_id': symid,
                        'symbol_name': symbol_name, 'geometry_mode': mode,
                        'graphics': self.graphics(obj),
                        'local_transform_translation_mm': [
                            rounded(obj.Transform.Origin.X * MM_PER_FOOT),
                            rounded(obj.Transform.Origin.Y * MM_PER_FOOT),
                            rounded(obj.Transform.Origin.Z * MM_PER_FOOT),
                        ],
                    })
                    self.walk(inner, child, path + [label], depth + 1)
                elif isinstance(obj, DB.Solid):
                    self.add_solid(obj, transform, path)
                elif isinstance(obj, DB.Mesh):
                    mid, source = self.resolve_material(obj)
                    group = self.group(path, obj, mid, source, 'Mesh')
                    self.add_mesh(obj, transform, group)
                elif isinstance(obj, DB.PolyLine):
                    group = self.group(path, obj, None, 'none', 'PolyLine')
                    group.curve_count += 1
                    try:
                        for p in obj.GetCoordinates():
                            if not self.push(group, p, transform, False):
                                return
                    except Exception as ex:
                        self.warn('PolyLine vertices failed: ' + ascii_text(ex))
                elif isinstance(obj, DB.Curve):
                    group = self.group(path, obj, None, 'none', 'Curve')
                    self.add_curve(obj, transform, group)
                elif isinstance(obj, DB.Point):
                    # Photometric source points are NOT physical geometry.
                    continue
        except Exception as ex:
            self.warn('GeometryElement enumeration failure: ' + ascii_text(ex))


def describe_material(doc, material_id):
    if material_id is None or material_id < 0:
        return {'id': material_id, 'name': None, 'resolved': False}
    material = None
    try:
        material = doc.GetElement(DB.ElementId(int(material_id)))
    except Exception:
        pass
    if material is None or not isinstance(material, DB.Material):
        return {'id': material_id, 'name': None, 'resolved': False}
    d = {'id': material_id, 'name': element_name(material), 'resolved': True}
    try:
        c = material.Color
        d['rgb'] = [int(c.Red), int(c.Green), int(c.Blue)]
        d['transparency'] = int(material.Transparency)
    except Exception:
        pass
    try:
        d['appearance_asset_id'] = element_id(material.AppearanceAssetId)
        d['appearance_asset_name'] = element_name(
            doc.GetElement(material.AppearanceAssetId))
    except Exception:
        pass
    return d


def material_parameters(doc, elem):
    result = []
    try:
        for p in elem.Parameters:
            if p.StorageType != DB.StorageType.ElementId:
                continue
            mid = p.AsElementId()
            if not valid_id(mid):
                continue
            candidate = doc.GetElement(mid)
            if not isinstance(candidate, DB.Material):
                continue
            item = {'name': ascii_text(p.Definition.Name),
                    'material_id': element_id(mid),
                    'value_source': 'element_parameter'}
            try:
                fam = doc.FamilyManager.GetAssociatedFamilyParameter(p)
                item['associated_family_parameter'] = (
                    ascii_text(fam.Definition.Name) if fam else None)
            except Exception:
                pass
            result.append(item)
    except Exception:
        pass
    return sorted(result, key=lambda x: x.get('name') or '')


def element_direct_materials(elem):
    ids = []
    try:
        for mid in elem.GetMaterialIds(False):
            if valid_id(mid):
                ids.append(element_id(mid))
    except Exception:
        pass
    return sorted(set(ids))


def import_layers(elem):
    out = []
    cat = None
    try:
        cat = elem.Category
    except Exception:
        pass
    if cat is not None:
        try:
            for subcat in cat.SubCategories:
                out.append(category_desc(subcat))
        except Exception:
            pass
    return sorted(out, key=lambda x: (x.get('name') or '', str(x.get('id'))))


def inspect_type(doc):
    result = {'configured_type': None, 'available_types': [],
              'material_parameters': []}
    try:
        fm = doc.FamilyManager
        cur = fm.CurrentType
        result['configured_type'] = ascii_text(cur.Name) if cur else None
        result['available_types'] = sorted(
            ascii_text(t.Name) for t in fm.Types)
        if cur is not None:
            for p in fm.Parameters:
                if p.StorageType != DB.StorageType.ElementId:
                    continue
                try:
                    mid = cur.AsElementId(p)
                    if not valid_id(mid):
                        continue
                    material = doc.GetElement(mid)
                    if not isinstance(material, DB.Material):
                        continue
                    result['material_parameters'].append({
                        'name': ascii_text(p.Definition.Name),
                        'material_id': element_id(mid),
                        'material_name': element_name(material),
                        'is_instance': bool(p.IsInstance),
                        'formula': ascii_text(p.Formula),
                    })
                except Exception:
                    continue
    except Exception as ex:
        result['error'] = ascii_text(ex)
    return result


def digest_element(doc, elem, family_budget):
    uid = None
    category = None
    type_id = None
    try:
        uid = ascii_text(elem.UniqueId)
    except Exception:
        pass
    try:
        category = category_desc(elem.Category)
    except Exception:
        pass
    try:
        type_id = element_id(elem.GetTypeId())
    except Exception:
        pass
    entry = {
        'id': element_id(elem.Id),
        'unique_id': uid,
        'class': ascii_text(elem.GetType().FullName),
        'name': element_name(elem),
        'category': category,
        'type_id': type_id,
        'element_material_ids': element_direct_materials(elem),
        'material_parameters': material_parameters(doc, elem),
    }
    if isinstance(elem, DB.ImportInstance):
        entry['import_subcategories'] = import_layers(elem)
        try:
            entry['is_linked_import'] = bool(elem.IsLinked)
        except Exception:
            pass
    opt = DB.Options()
    opt.IncludeNonVisibleObjects = False
    opt.DetailLevel = DB.ViewDetailLevel.Fine
    opt.ComputeReferences = False
    try:
        geo = elem.get_Geometry(opt)
    except Exception as ex:
        entry['geometry_error'] = ascii_text(ex)
        return entry, 0, True
    if geo is None:
        entry['geometry'] = None
        return entry, 0, False
    audit = Probe(doc, family_budget)
    audit.walk(geo, DB.Transform.Identity, [], 0)
    entry['_probe'] = audit
    return entry, audit.total_points, audit.truncated


def make_groups_summary(entry, family_min_ft):
    probe = entry.pop('_probe', None)
    if probe is None:
        return
    material_face_counts = {}
    imported_layer_materials = {}
    all_geometry = []
    for g in probe.groups.values():
        row = g.json(family_min_ft)
        all_geometry.append(row)
        if g.face_count:
            mkey = '%s:%s' % (str(row['material_id']), row['material_source'])
            material_face_counts[mkey] = material_face_counts.get(mkey, 0) + g.face_count
        if row['subcategory'] is not None:
            cat = row['subcategory']
            key = '%s:%s:%s' % (
                cat.get('id'), cat.get('name'), row.get('material_id'))
            if key not in imported_layer_materials:
                imported_layer_materials[key] = {
                    'subcategory': cat, 'material_id': row['material_id'],
                    'face_count': 0, 'mesh_triangle_count': 0, 'group_count': 0}
            target = imported_layer_materials[key]
            target['face_count'] += g.face_count
            target['mesh_triangle_count'] += g.mesh_triangle_count
            target['group_count'] += 1
    all_geometry.sort(key=lambda x: (
        '/'.join(x['nested_path']), str(x.get('material_id')),
        x.get('primitive') or ''))
    entry['geometry'] = {
        'physical_aabb_mm': probe.all_physical.json(family_min_ft),
        'curve_only_aabb_mm': probe.all_curves.json(),
        'sample_count': int(probe.total_points),
        'complete': not probe.truncated,
        'geometry_errors': probe.errors,
        'native_material_face_counts': material_face_counts,
        'import_graphics_layer_summary': sorted(
            imported_layer_materials.values(), key=lambda x: (
                (x.get('subcategory') or {}).get('name') or '',
                str(x.get('material_id')))),
        'nested_instances': probe.instanced,
        'part_groups': all_geometry,
    }


def inspect_one(spec):
    saved = fingerprint(spec['saved_rfa'], spec['saved_sha256'])
    oem = fingerprint(spec['downloaded_oem_rfa'],
                      spec['downloaded_oem_sha256'])
    outcome = {
        'id': spec['id'], 'expected_model': spec['model'],
        'expected_finish': spec['target_finish'],
        'saved_family_before': saved,
        'downloaded_oem_source_before': oem,
        'inspection_status': 'PENDING',
        'docs_modified_or_saved': False,
        'source_paths_intact': False,
        'finish_part_mapping_verified': False,
        'elements': [],
    }
    if not saved['exists']:
        outcome['inspection_status'] = 'FILE_MISSING'
        return outcome
    if not oem['exists']:
        outcome['source_missing_warning'] = True

    doc = None
    try:
        doc = APP.OpenDocumentFile(spec['saved_rfa'])
        if not doc.IsFamilyDocument:
            raise RuntimeError('Expected Revit FamilyDocument: ' + saved['path'])
        outcome['family_category'] = category_desc(doc.OwnerFamily.FamilyCategory)
        outcome['family_placement_type'] = ascii_text(
            doc.OwnerFamily.FamilyPlacementType)
        outcome['types'] = inspect_type(doc)
        outcomes = []
        consumed_points = 0
        all_truncated = False
        skipped_classes = {}
        for element in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
            # Every independent native geometry element is evaluated, including
            # source Imported CAD instances, sweeps, revolutions and nested RFAs.
            classname = ascii_text(element.GetType().FullName)
            if isinstance(element, DB.Material):
                continue
            budget = max(0, MAX_GEOMETRY_POINTS_PER_FAMILY - consumed_points)
            if budget == 0:
                all_truncated = True
                break
            item, points, partial = digest_element(doc, element, budget)
            consumed_points += points
            # Empty annotation/view objects do not represent a material part.
            probe = item.get('_probe')
            has_parts = probe is not None and bool(probe.groups)
            if not has_parts and not isinstance(element,
                                                 (DB.ImportInstance, DB.GenericForm,
                                                  DB.FamilyInstance, DB.DirectShape)):
                skipped_classes[classname] = skipped_classes.get(classname, 0) + 1
                continue
            if partial:
                all_truncated = True
            outcomes.append(item)

        aggregate_bounds = Extents()
        referenced_ids = set()
        for item in outcomes:
            probe = item.get('_probe')
            if probe is None:
                continue
            aggregate_bounds.merge(probe.all_physical)
            for group in probe.groups.values():
                if group.face_count or group.solid_count or group.mesh_count:
                    mid = group.descriptor['material_id']
                    if mid is not None and mid >= 0:
                        referenced_ids.add(mid)
            for mid in item['element_material_ids']:
                referenced_ids.add(mid)
            for p in item['material_parameters']:
                referenced_ids.add(p['material_id'])
            for cat in item.get('import_subcategories', []):
                if cat.get('material_id') is not None and cat['material_id'] >= 0:
                    referenced_ids.add(cat['material_id'])
            for group in probe.groups.values():
                cat = group.descriptor.get('subcategory') or {}
                if cat.get('material_id') is not None and cat['material_id'] >= 0:
                    referenced_ids.add(cat['material_id'])

        global_low_ft = aggregate_bounds.low[2] if aggregate_bounds.points else None
        for item in outcomes:
            make_groups_summary(item, global_low_ft)
        outcomes.sort(key=lambda x: (x['id'] is None, x['id'] or -1))
        outcome['elements'] = outcomes
        outcome['material_definitions'] = [
            describe_material(doc, mid) for mid in sorted(referenced_ids)]
        outcome['all_defined_materials'] = sorted([
            describe_material(doc, element_id(material.Id))
            for material in DB.FilteredElementCollector(doc).OfClass(DB.Material)
        ], key=lambda mat: ((mat.get('name') or ''), mat.get('id') or -1))
        if not aggregate_bounds.points:
            all_truncated = True
        outcome['summary'] = {
            'inspected_native_elements': len(outcomes),
            'excluded_non_geometry_element_classes': skipped_classes,
            'real_visible_physical_geometry_aabb_mm':
                aggregate_bounds.json(global_low_ft),
            'point_count': consumed_points,
            'aabb_sampling_incomplete': all_truncated,
            'families_or_imports_with_unknown_materials': any(
                material.get('resolved') is False
                for material in outcome['material_definitions']),
            'face_to_material_mapping_is_an_observation_not_finish_certification': True,
        }
        outcome['matches_known_qa_hashes'] = bool(
            saved.get('matches_expected_sha256') and
            oem.get('matches_expected_sha256'))
        outcome['inspection_status'] = (
            'SOURCE_VARIANT_CHANGED_REVIEW_REQUIRED'
            if not outcome['matches_known_qa_hashes'] else (
                'PARTIAL_GEOMETRY_REVIEW_REQUIRED'
                if all_truncated else 'NATIVE_GEOMETRY_READ_COMPLETE'))
        # A hidden imported layer, unassigned face or shared gray appearance
        # cannot be declared the intended physical material by this tool.
        outcome['finish_part_mapping_verified'] = False
    except Exception:
        outcome['inspection_status'] = 'ERROR'
        outcome['inspection_error'] = ascii_text(traceback.format_exc())
    finally:
        if doc is not None:
            try:
                doc.Close(False)
            except Exception as ex:
                outcome['close_without_save_error'] = ascii_text(ex)
                outcome['inspection_status'] = 'ERROR_CLOSE'
        outcome['saved_family_after'] = fingerprint(
            spec['saved_rfa'], spec['saved_sha256'])
        outcome['downloaded_oem_source_after'] = fingerprint(
            spec['downloaded_oem_rfa'], spec['downloaded_oem_sha256'])
        outcome['source_paths_intact'] = (
            outcome['saved_family_before'].get('exists', False) and
            outcome['downloaded_oem_source_before'].get('exists', False) and
            outcome['saved_family_before'].get('sha256') ==
            outcome['saved_family_after'].get('sha256') and
            outcome['downloaded_oem_source_before'].get('sha256') ==
            outcome['downloaded_oem_source_after'].get('sha256'))
        if not outcome['source_paths_intact']:
            outcome['inspection_status'] = 'SOURCE_HASH_CHANGED'
    return outcome


def write_new_receipt(data):
    """Render complete ASCII JSON before opening file; atomic no-overwrite."""
    if os.path.exists(OUTPUT):
        raise RuntimeError('Receipt exists; never overwrite: ' + OUTPUT)
    payload = json.dumps(data, ensure_ascii=True, sort_keys=True,
                         separators=(',', ':'))
    tmp = OUTPUT + '.tmp'
    if os.path.exists(tmp):
        raise RuntimeError('Temporary receipt exists; will not overwrite: ' + tmp)
    handle = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(handle, 'wb') as stream:
            if isinstance(payload, unicode):
                payload = payload.encode('ascii', 'strict')
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if os.path.exists(OUTPUT):
            raise RuntimeError('Receipt appeared before final write; preserving it')
        os.rename(tmp, OUTPUT)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


def main():
    if str(APP.VersionNumber) != '2025':
        raise RuntimeError('Only Revit 2025 supported: ' +
                           ascii_text(APP.VersionNumber))
    if getattr(__revit__, 'ActiveUIDocument', None) is not None:
        raise RuntimeError('Standalone probe requires isolated pyRevit run '
                           'with no active user project')
    if os.path.exists(OUTPUT):
        raise RuntimeError('Refusing to overwrite prior probe: ' + OUTPUT)
    if not os.path.isdir(os.path.dirname(OUTPUT)):
        raise RuntimeError('Expected QA directory absent: ' + os.path.dirname(OUTPUT))
    report = {
        'schema_version': 1,
        'purpose': '651 Belmont Penthouse GOOD Bolla/Smooth OEM native geometry and material probe',
        'started_utc': stamp(),
        'revit_version': ascii_text(APP.VersionNumber),
        'read_only_input_documents': True,
        'original_revit_documents_saved': False,
        'execution_context': 'isolated_Revit_2025_standalone_IronPython',
        'coordinate_space': 'Family document local coordinates',
        'aabb_provenance': ('Visible physical native solid-face triangulations, '
                            'analytical edge samples and import/nested mesh vertices; '
                            'explicitly composed GeometryInstance transforms; '
                            'not Element.get_BoundingBox'),
        'units': 'millimetres',
        'output_path': OUTPUT,
        'families': [],
    }
    for spec in INPUTS:
        print('Inspect %s: %s' % (spec['id'], spec['saved_rfa']))
        sys.stdout.flush()
        report['families'].append(inspect_one(spec))
    report['completed_utc'] = stamp()
    report['all_sources_unchanged'] = all(
        fam['source_paths_intact'] for fam in report['families'])
    report['all_native_geometries_read'] = all(
        fam['inspection_status'] == 'NATIVE_GEOMETRY_READ_COMPLETE'
        for fam in report['families'])
    report['finish_release_status'] = 'HOLD_AWAITING_INSPECTED_MATERIAL_PART_MAPPING'
    write_new_receipt(report)
    print('INSPECTION_RECEIPT %s' % OUTPUT)
    print('READ_ONLY_UNCHANGED=%s GEOMETRY_COMPLETE=%s' % (
        report['all_sources_unchanged'], report['all_native_geometries_read']))
    sys.stdout.flush()
    if not report['all_sources_unchanged'] or not report['all_native_geometries_read']:
        raise RuntimeError('Probe receipt contains a source or geometry hold; review ' + OUTPUT)


if __name__ == '__main__':
    main()
