# -*- coding: utf-8 -*-
r"""Read-only Revit 2025 IronPython face-level audit for Kuzco Bolla PD3106-BG.

Executed ONLY by the prime in an isolated Revit 2025 pyRevit session:
  D:\Games\pyRevit-Master\bin\pyrevit.exe run "E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\inspect_bolla_bg_r03_face_signatures.py" --revit=2025

READ-ONLY native investigation, with no transactions, Save or SaveAs.
It opens the verified IES R02 candidate, enumerates the four original
Revolution elements and records EACH SOLID FACE with an individual material
ID, painted-material ID (if any), stable reference when the API supplies it,
surface class, area, radial-distance profile, minimum/maximum Z, and sampled
boundary/mesh envelope. The source is closed with Close(False). It writes
ONE NEW JSON receipt, never overwriting an earlier file.

This is NOT a finish conversion. It deliberately DOES NOT assign
Brushed Gold, black, clear or frosted labels to the unassigned faces.
An R03 conversion must be blocked until a reviewer verifies that all
canopy/black suspension faces can be individually identified from this map
and subsequently painted without touching the protected glass.

The earlier native check failed because source mesh triangulation produced
14.8 x 17.09 mm for neck ID 4715, whereas analytic circular edges returned
17.07 x 17.09 mm (native check 17.086 x 17.086 mm). This probe records
both channels explicitly and avoids cross-comparing them.
"""
from __future__ import print_function
import os
import sys
import json
import hashlib
import time
import math
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SOURCE = os.path.join(BASE, 'candidates',
                      'Kuzco_Bolla_PD3106_BG_R2025_IES_R02.rfa')
IES = os.path.join(BASE, 'sources', 'photometry', 'PD3106-BG - Bolla.IES')
PRIOR = os.path.join(BASE, 'qa', 'inspect_oem_material_parts.json')
OUTPUT = os.path.join(BASE, 'qa', 'bolla_bg_r03_face_signatures.json')

SOURCE_SHA256 = '1d107108de7cf0a40562e764e5e73c8a4ae935861b1a3fc86f0e60a481b86c5d'
IES_SHA256 = '9e9f70e2eecc3b1c4130bea2f3fcb3c5a1798fb61363185348b635cd71737ce4'
PRIOR_SHA256 = '2ee88654c081a629fa324681703497a72adff29a2481a676f51b98d03b2213b3'
ELEMENTS = [('outer_clear_glass', 4435, 6, 1742),
            ('neck_unassigned', 4715, 8, None),
            ('inner_opal_glass', 5101, 16, 8722),
            ('canopy_and_black_wire_mixed', 7721, 14, None)]

MM_PER_FT = 304.8
MM2_PER_FT2 = MM_PER_FT * MM_PER_FT
ARC_STEPS = 48
MAX_FACE_POINTS = 16000


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            data = stream.read(1024 * 1024)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def id_number(item):
    if item is None:
        return None
    try:
        return int(item.Value)
    except Exception:
        try:
            return int(item.IntegerValue)
        except Exception:
            return None


def name(element):
    if element is None:
        return None
    try:
        return unicode(DB.Element.Name.GetValue(element))
    except Exception:
        try:
            return unicode(element.Name)
        except Exception:
            return None


def mm(value):
    return round(float(value) * MM_PER_FT, 4)


def mmp(point):
    return [mm(point.X), mm(point.Y), mm(point.Z)]


def point_stats(points):
    if not points:
        return None
    low = [min(getattr(point, c) for point in points) for c in 'XYZ']
    high = [max(getattr(point, c) for point in points) for c in 'XYZ']
    radii = [math.sqrt(float(p.X*p.X + p.Y*p.Y)) for p in points]
    return {
        'min_xyz_mm': [mm(v) for v in low],
        'max_xyz_mm': [mm(v) for v in high],
        'size_xyz_mm': [mm(high[i]-low[i]) for i in range(3)],
        'radius_min_mm': mm(min(radii)),
        'radius_max_mm': mm(max(radii)),
        'z_min_mm': mm(low[2]),
        'z_max_mm': mm(high[2]),
        'sample_count': len(points),
    }


def unique_points(points):
    """Bound payload size; for dense glass faceting retain extents samples."""
    if len(points) <= MAX_FACE_POINTS:
        return points, False
    step = int(math.ceil(float(len(points))/MAX_FACE_POINTS))
    selected = points[::step]
    # Always preserve axis extrema when creating representative sample.
    for axis in 'XYZ':
        selected.append(min(points, key=lambda p:getattr(p, axis)))
        selected.append(max(points, key=lambda p:getattr(p, axis)))
    return selected, True


def mesh_vertices(face):
    mesh = face.Triangulate()
    points = list(mesh.Vertices)
    return points, int(mesh.NumTriangles)


def boundary_vertices(face):
    """Samples ACTUAL trimmed face edges, including analytic circular arcs."""
    result = []
    loop_sizes = []
    for loop in face.EdgeLoops:
        count = 0
        for edge in loop:
            curve = edge.AsCurve()
            if curve is None:
                continue
            pts = list(curve.Tessellate())
            if isinstance(curve, DB.Line):
                for t in [0.0, 1.0]:
                    pts.append(curve.Evaluate(t, True))
            else:
                for i in range(ARC_STEPS + 1):
                    pts.append(curve.Evaluate(float(i)/float(ARC_STEPS), True))
            result.extend(pts)
            count += 1
        loop_sizes.append(count)
    return result, loop_sizes


def sample_surface(face):
    d = {'surface_class': unicode(face.GetType().FullName)}
    if isinstance(face, DB.CylindricalFace):
        d['cylinder_radius_mm'] = mm(face.Radius)
        try:
            d['cylinder_axis'] = mmp(face.Axis)
        except Exception:
            pass
        try:
            d['cylinder_origin_mm'] = mmp(face.Origin)
        except Exception:
            pass
    if isinstance(face, DB.ConicalFace):
        try:
            d['cone_half_angle_radians'] = round(float(face.HalfAngle), 6)
        except Exception:
            pass
    if isinstance(face, DB.PlanarFace):
        try:
            d['plane_normal'] = [
                round(float(v), 6) for v in
                (face.FaceNormal.X, face.FaceNormal.Y, face.FaceNormal.Z)]
        except Exception:
            pass
    return d


def paint_info(doc, element, face):
    info = {'original_face_material_id': id_number(face.MaterialElementId)}
    try:
        info['is_painted'] = bool(doc.IsPainted(element.Id, face))
        painted = doc.GetPaintedMaterial(element.Id, face)
        info['painted_material_id'] = id_number(painted)
    except Exception as ex:
        info['paint_query_error'] = unicode(ex)
    return info


def inspect(doc, role, element_id, expected_count, material_id):
    elem = doc.GetElement(DB.ElementId(element_id))
    require(isinstance(elem, DB.Revolution),
            '%s element %d missing native Revolution' % (role, element_id))
    opts = DB.Options()
    opts.DetailLevel = DB.ViewDetailLevel.Fine
    opts.IncludeNonVisibleObjects = False
    opts.ComputeReferences = True
    solids = [g for g in elem.get_Geometry(opts)
              if isinstance(g, DB.Solid) and g.Volume > 1e-12]
    require(len(solids) == 1,
            '%s expected exactly one original solid, found %d' %
            (role, len(solids)))
    solid = solids[0]
    faces = list(solid.Faces)
    require(len(faces) == expected_count,
            '%s face count changed: expected %d, got %d' %
            (role, expected_count, len(faces)))
    rows = []
    all_mesh_points = []
    all_edge_points = []
    for index, face in enumerate(faces):
        mesh_points, ntri = mesh_vertices(face)
        edge_points, edge_loop_sizes = boundary_vertices(face)
        all_mesh_points.extend(mesh_points)
        all_edge_points.extend(edge_points)
        mesh_representative, mesh_capped = unique_points(mesh_points)
        edge_representative, edge_capped = unique_points(edge_points)
        binding = paint_info(doc, elem, face)
        require(binding.get('original_face_material_id') in
                ((material_id, None) if material_id is None else (material_id,)),
                'Protected element %d face %d material unexpectedly changed' %
                (element_id, index))
        row = {
            'face_index': index,
            'mesh_triangle_count': ntri,
            'area_mm2': round(float(face.Area) * MM2_PER_FT2, 4),
            'analytic_boundary_loop_edge_counts': edge_loop_sizes,
            'mesh_sample_bounds': point_stats(mesh_representative),
            'analytic_edge_bounds': point_stats(edge_representative),
            'mesh_sample_truncated': mesh_capped,
            'analytic_edge_sample_truncated': edge_capped,
        }
        row.update(binding)
        row.update(sample_surface(face))
        try:
            if face.Reference is not None:
                row['stable_reference'] = unicode(
                    face.Reference.ConvertToStableRepresentation(doc))
        except Exception as ex:
            row['reference_error'] = unicode(ex)
        rows.append(row)
    return {
        'role': role, 'native_element_id': element_id, 'element_unique_id': unicode(elem.UniqueId),
        'class': unicode(elem.GetType().FullName), 'element_name': name(elem),
        'solid_count': 1, 'solid_volume_mm3': round(float(solid.Volume) * MM_PER_FT**3, 4),
        'face_count': len(rows),
        'element_mesh_bounds': point_stats(all_mesh_points),
        'element_analytic_edge_bounds': point_stats(all_edge_points),
        'faces': rows,
    }


def store_receipt_once(data):
    require(not os.path.lexists(OUTPUT),
            'Existing face-signature receipt is preserved: ' + OUTPUT)
    temp = OUTPUT + '.tmp'
    require(not os.path.lexists(temp),
            'Prior temporary receipt exists: ' + temp)
    content = json.dumps(data, ensure_ascii=True,
                         separators=(',', ':'), sort_keys=True)
    descriptor = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            if isinstance(content, unicode):
                content = content.encode('ascii')
            stream.write(content)
        require(not os.path.lexists(OUTPUT),
                'Another receipt appeared; refusing overwrite')
        os.rename(temp, OUTPUT)
    finally:
        if os.path.exists(temp):
            try:
                os.remove(temp)
            except Exception:
                pass


def main():
    require(sys.version_info[0] == 2, 'Run in IronPython 2.7 only')
    app = __revit__.Application
    require(str(app.VersionNumber) == '2025', 'Revit 2025 required')
    require(getattr(__revit__, 'ActiveUIDocument', None) is None,
            'Run in isolated pyRevit session with no active user RVT')
    for source_path, expected_hash in [
        (SOURCE, SOURCE_SHA256), (IES, IES_SHA256), (PRIOR, PRIOR_SHA256)
    ]:
        require(os.path.isfile(source_path), 'Required source missing: ' + source_path)
        require(digest(source_path) == expected_hash,
                'Source hash mismatch, stop: ' + source_path)
    require(not os.path.lexists(OUTPUT),
            'Output receipt exists, do not overwrite: ' + OUTPUT)
    doc = None
    try:
        doc = app.OpenDocumentFile(SOURCE)
        require(doc.IsFamilyDocument, 'IES candidate is not a family document')
        require(str(doc.OwnerFamily.FamilyCategory.Name) == 'Lighting Fixtures',
                'IES candidate category changed')
        require(str(doc.OwnerFamily.FamilyPlacementType) == 'OneLevelBasedHosted',
                'OEM placement changed')
        fm = doc.FamilyManager
        require(len(list(fm.Types)) == 1 and unicode(fm.CurrentType.Name) == 'Type 1',
                'Original native type mapping changed')
        receipt = {
            'schema_version': 1,
            'completed_utc': None,
            'revit_version': unicode(app.VersionNumber),
            'purpose': 'Bolla BG face identity audit: separate gold canopy and black cord',
            'source_rfa': SOURCE,
            'source_sha256': SOURCE_SHA256,
            'official_bg_ies_path': IES,
            'official_bg_ies_sha256': IES_SHA256,
            'independent_prior_probe_sha256': PRIOR_SHA256,
            'documents_saved': False,
            'native_family_type': 'Type 1',
            'face_paint_applied': False,
            'recommended_conversion_status': 'HOLD_PENDING_EXPLICIT_CANOPY_WIRE_FACE_MAP',
            'family_parts': [],
        }
        for role, element_id, expected_faces, mid in ELEMENTS:
            receipt['family_parts'].append(
                inspect(doc, role, element_id, expected_faces, mid))
        receipt['completed_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    finally:
        if doc is not None:
            doc.Close(False)
    for source_path, expected_hash in [
        (SOURCE, SOURCE_SHA256), (IES, IES_SHA256), (PRIOR, PRIOR_SHA256)
    ]:
        require(digest(source_path) == expected_hash,
                'Source changed during read-only probe: ' + source_path)
    store_receipt_once(receipt)
    print('BOLLA_R03_FACE_MAP ' + OUTPUT)
    print('FACES ' + str(sum(p['face_count'] for p in receipt['family_parts'])))
    print('CONVERSION_STATUS ' + receipt['recommended_conversion_status'])


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('BOLLA_R03_FACE_MAP_ERROR ' + traceback.format_exc())
        raise
