# -*- coding: utf-8 -*-
"""Read-only Revit 2025 visual QA: 6 PH Good family candidates, 12 PNG views.

Run ONLY in a separate, document-free Revit 2025 process:

pyrevit run "E:\\Claude\\3D-Model-Workflow\\output\\belmont_ph_good_rfa_20261016\\qa\\export_rfa_previews.py" --revit=2025

IronPython 2.7 / Autodesk Revit 2025 API.
Every RFA is opened without editing or saving. A disposable UNSAVED project
receives each family and hosts, transactionally creates its orthographic
project views, then closes with SaveModified=False. On ExportImage failure,
an unsaved temporary 3D view in the opened family is attempted and closed
without saving. Existing projects, extensions, RFAs and prior previews remain
unchanged. This script DOES NOT start Revit itself.
"""
from __future__ import print_function
import os
import sys
import json
import math
import time
import hashlib
import struct
import traceback
import re

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
QA = os.path.join(BASE, 'qa')
PREVIEWS = os.path.join(QA, 'previews')
RUN_RECEIPT = os.path.join(PREVIEWS, 'export_rfa_previews_receipt.json')
PROGRESS = os.path.join(PREVIEWS, 'export_progress.jsonl')
VERSION = 'R01'
PIXELS = 1200
MM_PER_FOOT = 304.8
MAX_NESTED_DEPTH = 14
APP = __revit__.Application

TARGETS = [
    {'id': 'cassia_r02', 'name': 'Alora Cassia LP549448MBCL R02',
     'path': os.path.join(BASE, 'candidates', 'Alora_Cassia_LP549448MBCL_R2025_R02.rfa'),
     'host': 'level', 'expected_type': 'LP549448MBCL',
     'type_materials': {'GLASS_COLOR': 'CASSIA_CLEAR_GLASS_MBCL',
                        'METAL_FINISH': 'CASSIA_MB_FINISH'},
     'focus': 'cassia_body'},
    {'id': 'hinkley_eos_r02', 'name': 'Hinkley Eos 53860BK R02 (unapproved)',
     'path': os.path.join(BASE, 'candidates', 'Hinkley_Eos_53860BK_R2025_R02_UNAPPROVED.rfa'),
     'host': 'wall_face', 'expected_type': '53860BK', 'focus': 'placed_solids'},
    {'id': 'vogue_ch_r02', 'name': 'Modern Forms Vogue WS-3127-CH R02',
     'path': os.path.join(BASE, 'candidates', 'ModernForms_Vogue_WS-3127_CH_R2025_R02.rfa'),
     'host': 'wall_face', 'expected_type': 'WS-3127', 'focus': 'placed_solids'},
    {'id': 'quorum_veno_r03', 'name': 'Quorum Veno 858-59 R03 (unapproved)',
     'path': os.path.join(BASE, 'candidates', 'Quorum_Veno_858-59_R2025_R03_UNAPPROVED.rfa'),
     'host': 'ceiling_face', 'expected_type': '858-59', 'focus': 'placed_solids'},
    {'id': 'bolla_oem', 'name': 'Kuzco Bolla PD3106-BG OEM',
     'path': os.path.join(BASE, 'families', 'Kuzco_Bolla_PD3106_BG_R2025.rfa'),
     'host': 'level', 'expected_type': 'Type 1', 'focus': 'placed_solids'},
    {'id': 'smooth_oem', 'name': 'Modern Forms Smooth FR-W2502-52L SB/MB OEM',
     'path': os.path.join(BASE, 'families', 'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025.rfa'),
     'host': 'ceiling_face', 'expected_type': None, 'focus': 'placed_solids'}
]

def name_of(element):
    if element is None:
        return None
    try:
        return unicode(DB.Element.Name.GetValue(element))
    except Exception:
        try:
            return unicode(element.Name)
        except Exception:
            return None

def text_of(value):
    if value is None:
        return None
    try:
        return unicode(value)
    except Exception:
        try:
            return str(value).decode('utf-8', 'replace')
        except Exception:
            return repr(value)

def element_number(eid):
    if eid is None:
        return None
    try:
        return int(eid.Value)
    except Exception:
        try:
            return int(eid.IntegerValue)
        except Exception:
            return None

def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

def write_once(path, data):
    if os.path.exists(path):
        raise RuntimeError('Existing evidence must not be overwritten: ' + path)
    temp = path + '.tmp'
    if os.path.exists(temp):
        raise RuntimeError('Incomplete previous evidence temp exists: ' + temp)
    raw = json.dumps(data, indent=2, ensure_ascii=True,
                     sort_keys=True, default=text_of).encode('ascii')
    with open(temp, 'wb') as stream:
        stream.write(raw)
    if os.path.exists(path):
        raise RuntimeError('Evidence appeared while writing: ' + path)
    os.rename(temp, path)

def log(stage, target=None, detail=None):
    event = {'utc': utc(), 'stage': stage,
             'id': target, 'detail': detail}
    with open(PROGRESS, 'a') as f:
        f.write(json.dumps(event, ensure_ascii=True, default=text_of) + '\n')
    print('RFA_PREVIEW %s %s' % (target or 'batch', stage))
    sys.stdout.flush()

def fingerprint(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return {'path': path, 'sha256': h.hexdigest(),
            'bytes': os.path.getsize(path)}

def warnings(doc):
    return [text_of(w.GetDescriptionText()) for w in doc.GetWarnings()]

def safe_symbol_name(symbol):
    try:
        p = symbol.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
        if p is not None:
            s = p.AsString()
            if s:
                return text_of(s)
    except Exception:
        pass
    return name_of(symbol)

def material_for_symbol(project, symbol, key):
    p = symbol.LookupParameter(key)
    if p is None:
        for candidate in symbol.Parameters:
            try:
                if text_of(candidate.Definition.Name) == key:
                    p = candidate
                    break
            except Exception:
                pass
    if p is None or str(p.StorageType) != 'ElementId':
        return None
    material = project.GetElement(p.AsElementId())
    return name_of(material)

def select_symbol(project, family, spec):
    ids = list(family.GetFamilySymbolIds())
    symbols = [project.GetElement(item) for item in ids]
    diagnostics = []
    for symbol in symbols:
        row = {'id': element_number(symbol.Id),
               'name': safe_symbol_name(symbol), 'materials': {}}
        for key in spec.get('type_materials', {}):
            row['materials'][key] = material_for_symbol(project, symbol, key)
        diagnostics.append(row)
    expected_materials = spec.get('type_materials')
    if expected_materials:
        matches = []
        for symbol, info in zip(symbols, diagnostics):
            if all(info['materials'].get(p) == mat
                   for p, mat in expected_materials.items()):
                matches.append(symbol)
        if len(matches) != 1:
            raise RuntimeError('No unique exact material-fingerprint FamilySymbol '
                               'for %s: %s' % (spec['id'], repr(diagnostics)))
        return matches[0], 'unique_exact_material_fingerprint', diagnostics
    desired = spec.get('expected_type')
    exact = [symbol for symbol in symbols
             if desired and safe_symbol_name(symbol) == desired]
    if len(exact) == 1:
        return exact[0], 'exact_symbol_name', diagnostics
    if len(symbols) == 1:
        return symbols[0], 'single_symbol_only_type_unverified', diagnostics
    raise RuntimeError('Multiple unresolved OEM family types; refusing guessed '
                       'type choice: ' + repr(diagnostics))

def prepare_host(project, spec, level, receipt):
    kind = spec['host']
    if kind == 'level':
        return None, None, DB.XYZ(0.0, 0.0, 8.0), None
    if kind == 'wall_face':
        types = [x for x in DB.FilteredElementCollector(project).OfClass(DB.WallType)
                 if x.Kind == DB.WallKind.Basic]
        if not types:
            raise RuntimeError('Disposable project has no basic wall type')
        wall = DB.Wall.Create(
            project, DB.Line.CreateBound(DB.XYZ(-12,0,0), DB.XYZ(12,0,0)),
            types[0].Id, level.Id, 12.0, 0.0, False, False)
        project.Regenerate()
        candidates = list(DB.HostObjectUtils.GetSideFaces(
            wall, DB.ShellLayerType.Exterior))
        if not candidates:
            raise RuntimeError('Wall exterior face absent')
        reference = candidates[0]
        face = wall.GetGeometryObjectFromReference(reference)
        point = face.Project(DB.XYZ(0.0, 0.0, 5.0)).XYZPoint
        normal = face.FaceNormal.Normalize()
        return wall, reference, point, normal
    if kind == 'ceiling_face':
        floor_type = DB.Floor.GetDefaultFloorType(project, False)
        if element_number(floor_type) is None or element_number(floor_type) < 0:
            raise RuntimeError('Disposable project has no default floor type')
        perimeter = DB.CurveLoop()
        xy = [(-12., -12.), (12., -12.),
              (12., 12.), (-12., 12.), (-12., -12.)]
        for a, b in zip(xy, xy[1:]):
            perimeter.Append(DB.Line.CreateBound(
                DB.XYZ(a[0], a[1], 10.0), DB.XYZ(b[0], b[1], 10.0)))
        host = DB.Floor.Create(project,
                               List[DB.CurveLoop]([perimeter]),
                               floor_type, level.Id)
        project.Regenerate()
        bottom = list(DB.HostObjectUtils.GetBottomFaces(host))
        if not bottom:
            raise RuntimeError('No ceiling-facing underside of disposable floor')
        reference = bottom[0]
        face = host.GetGeometryObjectFromReference(reference)
        point = face.Project(DB.XYZ(0.0,0.0,10.0)).XYZPoint
        normal = face.FaceNormal.Normalize()
        return host, reference, point, normal
    raise RuntimeError('Unknown placement: ' + text_of(kind))

def place_family(project, symbol, spec, level, host, face_reference, pt, normal):
    if spec['host'] == 'level':
        return project.Create.NewFamilyInstance(
            pt, symbol, level, DB.Structure.StructuralType.NonStructural)
    # Supported Revit 2025 face-based NewFamilyInstance overload.
    return project.Create.NewFamilyInstance(face_reference, pt,
                                             DB.XYZ.BasisX, symbol)

class Measure(object):
    """Collect WHOLE positive-volume placed solids with nested transforms."""
    def __init__(self, project):
        self.project = project
        self.solids = []
        self.loose_meshes = 0
        self.skipped_null_curves = 0
        self.geometry_instances = 0
        self.errors = []

    def measure_solid(self, solid):
        try:
            volume = float(solid.Volume)
        except Exception as e:
            self.errors.append('Unreadable volume: ' + text_of(e))
            return
        if volume <= 1e-12:
            return
        lo = [float('inf')] * 3
        hi = [float('-inf')] * 3
        n = [0]
        face_mats = {}
        def point(v):
            xyz = [float(v.X), float(v.Y), float(v.Z)]
            for k in range(3):
                lo[k] = min(lo[k], xyz[k])
                hi[k] = max(hi[k], xyz[k])
            n[0] += 1
        for face in solid.Faces:
            try:
                mat = name_of(self.project.GetElement(face.MaterialElementId))
                if mat:
                    face_mats[mat] = face_mats.get(mat, 0) + 1
            except Exception:
                pass
            try:
                mesh = face.Triangulate()
                if mesh is None:
                    self.errors.append('A physical solid face returned no triangulated mesh')
                else:
                    for v in mesh.Vertices:
                        point(v)
            except Exception as e:
                self.errors.append('Triangulation: ' + text_of(e))
        for edge in solid.Edges:
            try:
                curve = edge.AsCurve()
                if curve is None:
                    self.skipped_null_curves += 1
                    continue
                # Curved extrema may lie between triangle vertices.
                count = 2 if isinstance(curve, DB.Line) else 17
                for i in range(count):
                    point(curve.Evaluate(float(i)/float(count-1), True))
            except Exception as e:
                self.errors.append('Analytic edge: ' + text_of(e))
        if n[0]:
            self.solids.append({'min': lo, 'max': hi,
                                'volume_ft3': volume,
                                'dimensions_in': [(hi[i]-lo[i])*12.0 for i in range(3)],
                                'material_face_counts': face_mats,
                                'samples': n[0]})
        else:
            self.errors.append('Positive-volume solid yielded zero physical points')

    def walk(self, geom, depth=0):
        if depth > MAX_NESTED_DEPTH:
            self.errors.append('Nested geometry exceeded depth %d' % MAX_NESTED_DEPTH)
            return
        if geom is None:
            self.errors.append('Placed geometry returned None')
            return
        for item in geom:
            try:
                if isinstance(item, DB.GeometryInstance):
                    self.geometry_instances += 1
                    self.walk(item.GetInstanceGeometry(), depth+1)
                elif isinstance(item, DB.Solid):
                    self.measure_solid(item)
                elif isinstance(item, DB.Mesh):
                    self.loose_meshes += 1
            except Exception as e:
                self.errors.append('Native traversal: ' + text_of(e))

    def summary(self):
        return {'solids': len(self.solids),
                'loose_meshes': self.loose_meshes,
                'nested_instances': self.geometry_instances,
                'null_analytic_curves_skipped': self.skipped_null_curves,
                'errors': self.errors,
                'solid_geometry_complete': bool(self.solids) and not self.errors,
                'loose_mesh_visual_scope_pending': self.loose_meshes > 0}

def union_bounds(solids):
    if not solids:
        return None
    return {'min': [min(s['min'][k] for s in solids) for k in range(3)],
            'max': [max(s['max'][k] for s in solids) for k in range(3)]}

def xyz_of(v):
    return DB.XYZ(float(v[0]), float(v[1]), float(v[2]))

def classify_focus(measurement, instance, spec):
    solids = measurement.solids
    notes = []
    chosen = solids
    method = 'all_placed_positive_volume_solids'
    if spec.get('focus') == 'cassia_body':
        # Same whole-solid, material-anchored shade rule as independent native
        # Cassia R02 QA. Crops BODY only; suspension/rods are explicitly omitted.
        tr = instance.GetTransform().Inverse
        glass = 'CASSIA_CLEAR_GLASS_MBCL'
        anchors = [s for s in solids if s['material_face_counts'].get(glass, 0)]
        if anchors:
            # Local Z is authoritative for the intended fixture-body height.
            # World-space positive-volume bounds are inversely transformed via
            # eight corners (conservative under rotation).
            def local_z(s):
                v = [tr.OfPoint(DB.XYZ(x,y,z)).Z
                     for x in (s['min'][0], s['max'][0])
                     for y in (s['min'][1], s['max'][1])
                     for z in (s['min'][2], s['max'][2])]
                return min(v), max(v)
            lo = min(local_z(s)[0] for s in anchors)
            hi = max(local_z(s)[1] for s in anchors)
            if (hi-lo)*12.0 <= 6.75:
                allowed = set([glass, 'CASSIA_MB_FINISH',
                               'BULB_GLASS', 'BULB_PLASTIC'])
                selected = []
                for s in solids:
                    sl, sh = local_z(s)
                    height = (sh-sl)*12.0
                    mat = set(s['material_face_counts'].keys())
                    if (height <= 6.75 and
                        mat.intersection(allowed) and
                        sh >= lo-1.0/12. and sl <= hi+1.0/12.):
                        selected.append(s)
                if selected:
                    chosen = selected
                    method = 'cassia_clear_glass_anchored_whole_body_solids'
                    notes.append('Body-detail framing; long suspension, rods and distant physical solids excluded intentionally')
            else:
                notes.append('Clear glass anchor spans >6.75 in: no body-only crop inferred')
        else:
            notes.append('No known R02 clear-glass physical anchor; used all placed solids')
    bounds = union_bounds(chosen)
    if bounds is None:
        raise RuntimeError('No measured positive-volume native geometry for preview crop')
    ext = [(bounds['max'][k]-bounds['min'][k])*MM_PER_FOOT for k in range(3)]
    # Revit source family control/template 96-in extents must not define the crop.
    # This entire bound comes from the actual disposable project's *instance*.
    return {'bounds': bounds, 'solids_selected': len(chosen),
            'solids_total': len(solids), 'selection_method': method,
            'omitted_whole_solids': len(solids)-len(chosen),
            'xyz_mm': [round(v, 5) for v in ext],
            'warnings': notes, 'template_bbox_used': False,
            'geometry_origin': 'visible nested physical solids from placed FamilyInstance'}

def pad_bounds(bounds):
    lengths = [bounds['max'][i]-bounds['min'][i] for i in range(3)]
    largest = max(lengths)
    pad = max(0.10, 0.065 * largest)
    return {'min': [bounds['min'][i]-pad for i in range(3)],
            'max': [bounds['max'][i]+pad for i in range(3)],
            'padding_ft': pad}

def camera_directives(spec, bounds, normal):
    center = DB.XYZ(*[(bounds['min'][i]+bounds['max'][i])*0.5
                      for i in range(3)])
    span = max(bounds['max'][i]-bounds['min'][i] for i in range(3))
    span = max(1.0, span)
    if spec['host'] == 'wall_face':
        facing = normal if normal is not None else DB.XYZ(0,-1,0)
        facing = DB.XYZ(facing.X, facing.Y, 0).Normalize()
        right = DB.XYZ.BasisZ.CrossProduct(facing).Normalize()
        front = facing.Add(DB.XYZ.BasisZ.Multiply(0.025)).Normalize()
        oblique = facing.Add(right.Multiply(0.65)).Add(
            DB.XYZ.BasisZ.Multiply(0.35)).Normalize()
    else:
        # Pendants: front elevation along -Y; ceiling fans: front side
        # elevation, oblique from above exposes the full three-blade sweep.
        front = DB.XYZ(0,-1,0.04).Normalize()
        oblique = DB.XYZ(0.85,-1.0,0.60).Normalize()
    return center, span, [('front', front), ('oblique', oblique)]

def camera_view(project, spec, label, eye_dir, focus, host):
    three_d = [v for v in DB.FilteredElementCollector(project).OfClass(DB.ViewFamilyType)
               if v.ViewFamily == DB.ViewFamily.ThreeDimensional]
    if not three_d:
        raise RuntimeError('No 3D ViewFamilyType in disposable Revit project')
    view = DB.View3D.CreateIsometric(project, three_d[0].Id)
    view.Name = 'PHGood_' + spec['id'] + '_' + label
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.DisplayStyle = DB.DisplayStyle.Shading
    center, span, _ = camera_directives(spec, focus['bounds'],
                                        focus.get('host_normal'))
    eye = center.Add(eye_dir.Multiply(span * 3.5 + 3.0))
    forward = center.Subtract(eye).Normalize()
    up = DB.XYZ.BasisZ
    if abs(forward.DotProduct(up)) > 0.98:
        up = DB.XYZ.BasisY
    right = forward.CrossProduct(up).Normalize()
    true_up = right.CrossProduct(forward).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, true_up, forward))
    padded = pad_bounds(focus['bounds'])
    section = DB.BoundingBoxXYZ()
    section.Min = xyz_of(padded['min'])
    section.Max = xyz_of(padded['max'])
    view.SetSectionBox(section)
    view.IsSectionBoxActive = True
    # Hide only disposable architectural hosts and annotation/connector
    # graphics. Never hide imported CAD, Generic Models, or Lighting Fixtures:
    # official OEM geometry often uses those subcategories.
    hidden = []
    for cat in project.Settings.Categories:
        try:
            lower = (text_of(cat.Name) or '').lower()
            host_category = lower in ('walls','floors','roofs','ceilings')
            annotation = cat.CategoryType == DB.CategoryType.Annotation
            helper = lower in ('light source','lights','cameras',
                               'internal origin','section boxes',
                               'reference planes','connector elements')
            if host_category or annotation or helper:
                if view.CanCategoryBeHidden(cat.Id):
                    view.SetCategoryHidden(cat.Id, True)
                    hidden.append(text_of(cat.Name))
        except Exception:
            pass
    # Hide this specific disposable host too (without touching fixture).
    if host is not None:
        try:
            ids = List[DB.ElementId]([host.Id])
            if view.CanElementBeHidden(host.Id):
                view.HideElements(ids)
                hidden.append('host_element_id:' + str(element_number(host.Id)))
        except Exception:
            # Category hiding and section-box clipping remain authoritative.
            pass
    try:
        white = DB.Color(255,255,255)
        view.SetBackground(DB.ViewDisplayBackground.CreateGradient(
            white, white, white))
    except Exception:
        pass
    project.Regenerate()
    crop_error = None
    try:
        # Section box limits 3D geometry, crop box limits orthographic image
        # framing. Transform all world extents into view crop coordinates.
        crop = view.CropBox
        inverse = crop.Transform.Inverse
        corners = [inverse.OfPoint(DB.XYZ(x,y,z))
                   for x in (padded['min'][0],padded['max'][0])
                   for y in (padded['min'][1],padded['max'][1])
                   for z in (padded['min'][2],padded['max'][2])]
        crop.Min = DB.XYZ(min(p.X for p in corners),
                          min(p.Y for p in corners), crop.Min.Z)
        crop.Max = DB.XYZ(max(p.X for p in corners),
                          max(p.Y for p in corners), crop.Max.Z)
        view.CropBox = crop
        view.CropBoxActive = True
        view.CropBoxVisible = False
    except Exception:
        crop_error = traceback.format_exc()
    return view, {'name': view.Name, 'view_id': element_number(view.Id),
                  'orthographic': not bool(view.IsPerspective),
                  'model_xyz_mm': focus['xyz_mm'],
                  'section_bounds_ft': padded,
                  'hidden_categories_and_host': hidden,
                  'crop_box_error': crop_error,
                  'camera_direction_from_subject': [eye_dir.X,eye_dir.Y,eye_dir.Z]}

def dimensions_from_png(path):
    with open(path, 'rb') as f:
        header = f.read(24)
    if len(header) < 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError('Preview export is not valid PNG IHDR')
    width, height = struct.unpack('>II', header[16:24])
    return [width, height]

def export_one(doc, view, canonical_stem):
    final = os.path.join(PREVIEWS, canonical_stem + '.png')
    prefix = os.path.join(PREVIEWS, 'revit_' + canonical_stem)
    if os.path.exists(final):
        raise RuntimeError('Final preview already exists: ' + final)
    preexisting = [p for p in os.listdir(PREVIEWS)
                   if p.lower().endswith('.png') and
                   p.startswith('revit_' + canonical_stem)]
    if preexisting:
        raise RuntimeError('Existing Revit export artifact: ' + repr(preexisting))
    opts = DB.ImageExportOptions()
    opts.FilePath = prefix
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.SetViewsAndSheets(List[DB.ElementId]([view.Id]))
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = PIXELS
    opts.ImageResolution = DB.ImageResolution.DPI_150
    opts.HLRandWFViewsFileType = DB.ImageFileType.PNG
    opts.ShadowViewsFileType = DB.ImageFileType.PNG
    doc.ExportImage(opts)
    created = [os.path.join(PREVIEWS, p) for p in os.listdir(PREVIEWS)
               if p.lower().endswith('.png') and
               p.startswith('revit_' + canonical_stem)]
    if len(created) != 1:
        raise RuntimeError('Expected one PNG produced by Revit ExportImage, got %d: %s' %
                           (len(created), repr(created)))
    dim = dimensions_from_png(created[0])
    if max(dim) < 1150 or max(dim) > 1250:
        raise RuntimeError('PNG image is not approximately 1200px on longest side: ' +
                           repr(dim))
    os.rename(created[0], final)
    return {'path': final, 'size_bytes': os.path.getsize(final),
            'png_dimensions_px': dim, 'sha256': fingerprint(final)['sha256'],
            'exporter': 'Revit2025 Document.ExportImage', 'success': True}

def family_view_fallback(family_doc, spec, view_label, eye_dir, measured_focus,
                         base_dir=None):
    """Unsaved RFA temporary view, attempted only if project image export fails."""
    tx = None
    try:
        tx = DB.Transaction(family_doc, 'Unsaved PHGood fallback 3D preview')
        tx.Start()
        types = [t for t in DB.FilteredElementCollector(family_doc).OfClass(DB.ViewFamilyType)
                 if t.ViewFamily == DB.ViewFamily.ThreeDimensional]
        if not types:
            raise RuntimeError('RFA has no 3D view type')
        view = DB.View3D.CreateIsometric(family_doc, types[0].Id)
        view.Name = 'PHGood_Fallback_' + spec['id'] + '_' + view_label
        view.DetailLevel = DB.ViewDetailLevel.Fine
        view.DisplayStyle = DB.DisplayStyle.Shading
        # Reproject measured placed geometry through the placed FamilyInstance
        # transform, so RFA section bounds derive from *placed* physical
        # solids rather than the template's Reference Plane bounding boxes.
        world_bbox = measured_focus['bounds']
        inverse = measured_focus['instance_transform_inverse']
        pts = [inverse.OfPoint(DB.XYZ(x,y,z))
               for x in (world_bbox['min'][0],world_bbox['max'][0])
               for y in (world_bbox['min'][1],world_bbox['max'][1])
               for z in (world_bbox['min'][2],world_bbox['max'][2])]
        local = {'min':[min(getattr(p,a) for p in pts) for a in ('X','Y','Z')],
                 'max':[max(getattr(p,a) for p in pts) for a in ('X','Y','Z')]}
        ctr = DB.XYZ(*[(local['min'][i]+local['max'][i])*.5 for i in range(3)])
        span = max(local['max'][i]-local['min'][i] for i in range(3))
        eye = ctr.Add(eye_dir.Multiply(span*3.5+3.0))
        fwd = ctr.Subtract(eye).Normalize()
        up = DB.XYZ.BasisZ if abs(fwd.DotProduct(DB.XYZ.BasisZ)) < .98 else DB.XYZ.BasisY
        right = fwd.CrossProduct(up).Normalize()
        view.SetOrientation(DB.ViewOrientation3D(eye,
                            right.CrossProduct(fwd).Normalize(),fwd))
        box = pad_bounds(local)
        section = DB.BoundingBoxXYZ()
        section.Min = xyz_of(box['min'])
        section.Max = xyz_of(box['max'])
        view.SetSectionBox(section)
        view.IsSectionBoxActive = True
        for category in family_doc.Settings.Categories:
            try:
                if ((category.CategoryType == DB.CategoryType.Annotation or
                     (text_of(category.Name) or '').lower() in
                     ('reference planes','lights','light source','section boxes'))
                    and view.CanCategoryBeHidden(category.Id)):
                    view.SetCategoryHidden(category.Id, True)
            except Exception:
                pass
        family_doc.Regenerate()
        tx.Commit()
        tx = None
        response = export_one(family_doc,view,spec['id']+'_'+view_label+'_family_fallback')
        response['temporary_unsaved_family_view'] = True
        response['project_view_export_failed'] = True
        response['scope_warning'] = 'Source family view may show different type/visibility or reference geometry; separate manual visual review required'
        return response
    finally:
        if tx is not None:
            try:
                tx.RollBack()
            except Exception:
                pass

def render_target(spec):
    rec = {'id':spec['id'],'product':spec['name'],
           'source_rfa': spec['path'],
           'nominal_intended_host': spec['host'],
           'started_utc':utc(),'status':'STARTED',
           'views':[], 'family_saved':False,'disposable_project_saved':False}
    family_doc = None
    project = None
    transaction = None
    original = fingerprint(spec['path'])
    rec['source_fingerprint_before'] = original
    try:
        log('OPEN_RFA', spec['id'])
        family_doc = APP.OpenDocumentFile(spec['path'])
        if not family_doc.IsFamilyDocument:
            raise RuntimeError('RFA path opens a non-family document')
        rec['category'] = name_of(family_doc.OwnerFamily.FamilyCategory)
        rec['placement_type'] = str(family_doc.OwnerFamily.FamilyPlacementType)
        rec['family_warnings'] = warnings(family_doc)
        project = APP.NewProjectDocument(DB.UnitSystem.Imperial)
        if project is None or project.IsFamilyDocument:
            raise RuntimeError('Disposable unsaved Revit project unavailable')
        loaded = family_doc.LoadFamily(project)
        if not isinstance(loaded, DB.Family):
            raise RuntimeError('Document.LoadFamily(project) must return DB.Family')
        symbol, method, symbols = select_symbol(project,loaded,spec)
        rec['selected_symbol'] = safe_symbol_name(symbol)
        rec['symbol_id'] = element_number(symbol.Id)
        rec['symbol_selection_method'] = method
        rec['symbols_found'] = symbols
        transaction = DB.Transaction(project,'Disposable PHGood visual QA views')
        transaction.Start()
        level = DB.Level.Create(project, 0.0)
        host, face_ref, point, face_normal = prepare_host(
            project, spec, level, rec)
        symbol.Activate()
        project.Regenerate()
        instance = place_family(project, symbol, spec,level,
                                host,face_ref,point,face_normal)
        project.Regenerate()
        rec['instance_id'] = element_number(instance.Id)
        rec['actual_host_id'] = element_number(instance.Host.Id) if instance.Host else None
        rec['disposable_host_id'] = element_number(host.Id) if host else None
        rec['hosted_as_expected'] = (
            spec['host'] == 'level' or
            (host is not None and instance.Host is not None and
             instance.Host.Id == host.Id and instance.HostFace is not None))
        if not rec['hosted_as_expected']:
            raise RuntimeError('Instance did not retain required disposable host')
        geometry = Measure(project)
        opts = DB.Options()
        opts.DetailLevel = DB.ViewDetailLevel.Fine
        opts.IncludeNonVisibleObjects = False
        geometry.walk(instance.get_Geometry(opts))
        rec['geometry'] = geometry.summary()
        if not rec['geometry']['solid_geometry_complete']:
            raise RuntimeError('Cannot frame physical placed geometry: ' +
                               repr(rec['geometry']['errors']))
        focus = classify_focus(geometry,instance,spec)
        focus['host_normal'] = face_normal
        focus['instance_transform_inverse'] = instance.GetTransform().Inverse
        rec['physical_crop'] = dict((key, value) for key,value in focus.items()
                                    if key not in ('bounds','host_normal',
                                                   'instance_transform_inverse'))
        rec['physical_crop']['world_bounds_ft'] = focus['bounds']
        rec['physical_crop']['source_family_bbox_used'] = False
        center, span, cameras = camera_directives(
            spec, focus['bounds'], face_normal)
        pending=[]
        for label, camera_dir in cameras:
            view, meta = camera_view(project,spec,label,camera_dir,focus,host)
            pending.append((label,camera_dir,view,meta))
        rec['project_warning_count'] = len(warnings(project))
        rec['project_warnings'] = warnings(project)
        transaction.Commit()
        transaction = None
        for label, camera_dir, view, meta in pending:
            row={'label':label,'view_metadata':meta,'status':'PENDING',
                 'orthographic': meta['orthographic'],
                 'pixel_size_target':PIXELS}
            try:
                log('EXPORT_PROJECT_VIEW_'+label.upper(),spec['id'])
                row['image']=export_one(project, view,spec['id']+'_'+label)
                row['status']='PROJECT_PNG_OK'
            except Exception:
                row['project_export_error']=traceback.format_exc()
                log('PROJECT_IMAGE_ERROR_'+label.upper(),spec['id'],
                    row['project_export_error'][-1000:])
                try:
                    log('FAMILY_VIEW_FALLBACK_'+label.upper(),spec['id'])
                    row['family_fallback']=family_view_fallback(
                        family_doc,spec,label,camera_dir,focus)
                    row['status']='FAMILY_FALLBACK_PNG_REVIEW_REQUIRED'
                except Exception:
                    row['family_fallback_error']=traceback.format_exc()
                    row['status']='EXPORT_FAILED'
            rec['views'].append(row)
        rec['status'] = ('PROJECT_PREVIEWS_2_OF_2'
                          if sum(1 for x in rec['views']
                                 if x['status']=='PROJECT_PNG_OK') == 2 else
                         'PREVIEWS_INCOMPLETE_OR_FALLBACK')
    except Exception:
        rec['status']='ERROR'
        rec['error']=traceback.format_exc()
        log('FAMILY_ERROR',spec['id'],rec['error'][-1200:])
    finally:
        if transaction is not None:
            try:
                transaction.RollBack()
            except Exception:
                pass
        if project is not None:
            try:
                project.Close(False)
            except Exception as e:
                rec['project_close_error']=text_of(e)
        if family_doc is not None:
            try:
                family_doc.Close(False)
            except Exception as e:
                rec['family_close_error']=text_of(e)
        rec['source_fingerprint_after']=fingerprint(spec['path'])
        rec['source_bytes_identical']=(
            rec['source_fingerprint_before']['sha256']==
            rec['source_fingerprint_after']['sha256'])
        if not rec['source_bytes_identical']:
            rec['status']='SOURCE_HASH_CHANGED_HOLD'
        rec['completed_utc']=utc()
        write_once(os.path.join(PREVIEWS,spec['id']+'_receipt.json'),rec)
    return rec

def main():
    if str(APP.VersionNumber)!='2025':
        raise RuntimeError('Standalone exporter requires Revit 2025')
    if getattr(__revit__,'ActiveUIDocument',None) is not None:
        raise RuntimeError('Refusing active Revit document: run an isolated pyrevit process')
    if len(TARGETS)!=6 or len(set(item['id'] for item in TARGETS))!=6:
        raise RuntimeError('Expected exactly six distinct candidates')
    for spec in TARGETS:
        if not os.path.isfile(spec['path']):
            raise RuntimeError('Missing exact RFA: '+spec['path'])
    if not os.path.isdir(PREVIEWS):
        os.makedirs(PREVIEWS)
    if os.path.exists(RUN_RECEIPT) or os.path.exists(PROGRESS):
        raise RuntimeError('Previous exporter evidence exists; new revision required')
    for spec in TARGETS:
        if os.path.exists(os.path.join(PREVIEWS,spec['id']+'_receipt.json')):
            raise RuntimeError('Per-family receipt exists: '+spec['id'])
        for label in ('front','oblique'):
            if os.path.exists(os.path.join(PREVIEWS,spec['id']+'_'+label+'.png')):
                raise RuntimeError('PNG already exists for '+spec['id']+' '+label)
    report={'schema_version':1,'purpose':'651 Belmont PH Good six-RFA orthographic visual QA',
            'revit_version':str(APP.VersionNumber),'run_utc':utc(),
            'output_root':PREVIEWS,'requested_png_longest_side_px':PIXELS,
            'rfa_count':len(TARGETS),'disposable_projects_saved':False,
            'rfas_modified':False,'results':[]}
    log('BATCH_STARTED',None,{'families':[x['id'] for x in TARGETS]})
    for spec in TARGETS:
        try:
            report['results'].append(render_target(spec))
        except Exception:
            report['results'].append({'id':spec['id'],'status':'RUNNER_ERROR',
                                      'error':traceback.format_exc()})
    report['finished_utc']=utc()
    report['source_hashes_all_unchanged']=all(
        item.get('source_bytes_identical',False)
        for item in report['results'])
    report['project_png_views']=sum(
        1 for item in report['results'] for v in item.get('views',[])
        if v['status']=='PROJECT_PNG_OK')
    report['fallback_png_views']=sum(
        1 for item in report['results'] for v in item.get('views',[])
        if v['status']=='FAMILY_FALLBACK_PNG_REVIEW_REQUIRED')
    report['preview_complete']=(
        report['source_hashes_all_unchanged'] and
        report['project_png_views']==12)
    report['source_photometry_and_design_approval']='OUT_OF_SCOPE'
    write_once(RUN_RECEIPT,report)
    log('BATCH_COMPLETED',None,{'project_png_views':report['project_png_views'],
                                'fallback_png_views':report['fallback_png_views'],
                                'preview_complete':report['preview_complete']})
    print('RFA_PREVIEW receipt: '+RUN_RECEIPT)

main()
