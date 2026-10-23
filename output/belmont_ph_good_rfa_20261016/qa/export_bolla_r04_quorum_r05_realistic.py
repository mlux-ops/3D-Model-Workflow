# -*- coding: utf-8 -*-
r"""Revit 2025 IronPython 2.7: isolated Realistic clear-glass comparison.

Prime-only invocation (NO Revit launch by this script):
 D:\Games\pyRevit-Master\bin\pyrevit.exe run "E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\export_bolla_quorum_realistic_r01.py" --revit=2025

Four explicit optically focused Native View3D PNGs:
 - bolla_r03_front.png, bolla_r03_oblique.png
 - quorum_r04_front.png, quorum_r04_oblique.png

Exact source RFA hashes and unique symbol/type are checked. Each camera
gets its OWN disposable UNSAVED project, with the correct family placement
and a black/white, 8x8 checkerboard created as native Revit DirectShape
solids. The checkerboard's front lies 0.22 in BEHIND the far outer glass
surface along the actual camera direction. Glass focus is derived only from
positive-volume placed instance faces with exact verified glass material
names, never inferred from a template bounding box.

CRITICAL: View3D.DisplayStyle must be EXACTLY DB.DisplayStyle.Realistic
after view creation, project regeneration, transaction commit AND export.
The script raises on unsupported Realistic rather than replacing it with
Shading. Source family files are NEVER modified or saved. Disposable Revit
projects are ALWAYS closed with Close(False).

Realistic visual style is NOT ray-traced photometric validation. Visible
contrast is an optical-view inspection aid, not proof of physical refraction,
transmittance, optical accuracy, or calibrated glass/metal appearance.
"""
from __future__ import print_function
import os
import sys
import json
import time
import math
import struct
import hashlib
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
DEST = os.path.join(ROOT, 'qa', 'previews_realistic_r04_r05')
RECEIPT = os.path.join(DEST, 'optical_qa_receipt.json')
PIXEL_WIDTH = 1400
CHECKER_GRID = 8
CHECKER_GAP_FT = 0.22 / 12.0
CHECKER_THICKNESS_FT = 0.045 / 12.0
CHECKER_MARGIN_FT = 0.15
RECURSION_LIMIT = 12
APP = __revit__.Application
REALISTIC = DB.DisplayStyle.Realistic

TARGETS = [
    {
        'id': 'bolla_r04',
        'label': 'Kuzco Bolla PD3106-BG',
        'path': os.path.join(
            ROOT, 'candidates',
            'Kuzco_Bolla_PD3106_BG_R2025_R04_CLEAR_APPEARANCE_UNAPPROVED.rfa'),
        'sha256': 'CANDIDATE_HASH_FROM_NATIVE_RECEIPT',
        'placement': 'level',
        'expected_family_placement': 'OneLevelBasedHosted',
        'exact_symbol': 'Type 1',
        'glass_material': 'Glass',
        'unapproved': True,
    },
    {
        'id': 'quorum_r05',
        'label': 'Quorum Veno 858-59',
        'path': os.path.join(
            ROOT, 'candidates',
            'Quorum_Veno_858-59_R2025_R05_CLEAR_APPEARANCE_UNAPPROVED.rfa'),
        'sha256': 'CANDIDATE_HASH_FROM_NATIVE_RECEIPT',
        'placement': 'ceiling_face',
        'expected_family_placement': 'WorkPlaneBased',
        'exact_symbol': '858-59 - Matte Black / Clear - R04 photo-derived unapproved',
        'glass_material': 'Clear Glass',
        'unapproved': True,
    },
]


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def eid(item):
    try:
        return int(item.Value)
    except Exception:
        try:
            return int(item.IntegerValue)
        except Exception:
            return None


def name_of(elem):
    if elem is None:
        return None
    try:
        return unicode(DB.Element.Name.GetValue(elem))
    except Exception:
        try:
            return unicode(elem.Name)
        except Exception:
            return None


def fingerprint(path):
    require(os.path.isfile(path), 'Required input missing: ' + path)
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            part = f.read(1024 * 1024)
            if not part:
                break
            h.update(part)
    return {'path': path, 'sha256': h.hexdigest(),
            'bytes': int(os.path.getsize(path))}


def xyz(values):
    return DB.XYZ(float(values[0]), float(values[1]), float(values[2]))


def triplet(v):
    return [round(float(v.X), 7), round(float(v.Y), 7),
            round(float(v.Z), 7)]


def extrema(points):
    require(bool(points), 'Cannot measure empty physical glass points')
    a = 'XYZ'
    return {
        'min': [min(float(getattr(p, n)) for p in points) for n in a],
        'max': [max(float(getattr(p, n)) for p in points) for n in a],
    }


def vertices_from_face(face):
    points = []
    mesh = face.Triangulate()
    require(mesh is not None and mesh.NumTriangles > 0,
            'Original glass face has no physical triangulation')
    points.extend(list(mesh.Vertices))
    for loop in face.EdgeLoops:
        for edge in loop:
            curve = edge.AsCurve()
            if curve is None:
                continue
            samples = 2 if isinstance(curve, DB.Line) else 25
            for i in range(samples):
                points.append(curve.Evaluate(
                    float(i) / float(samples - 1), True))
    return points


def physical_glass_points(project, instance, exact_material_name):
    """R05 native instance geometry traversal with exact glass name filter."""
    opt = DB.Options()
    opt.DetailLevel = DB.ViewDetailLevel.Fine
    opt.IncludeNonVisibleObjects = False
    points = []
    count = [0]
    total_solids = [0]
    material_ids = set()

    def walk(geometry, depth):
        require(depth <= RECURSION_LIMIT, 'Nested Revit geometry recursion exceeded')
        require(geometry is not None, 'Placed family returned no native geometry')
        for item in geometry:
            if isinstance(item, DB.GeometryInstance):
                walk(item.GetInstanceGeometry(), depth + 1)
            elif isinstance(item, DB.Solid):
                if item.Volume <= 1e-12:
                    continue
                total_solids[0] += 1
                for face in item.Faces:
                    material = project.GetElement(face.MaterialElementId)
                    if name_of(material) == exact_material_name:
                        points.extend(vertices_from_face(face))
                        count[0] += 1
                        material_ids.add(eid(face.MaterialElementId))
                        require(len(points) < 250000,
                                'Glass facet sampling exceeded deterministic budget')
    walk(instance.get_Geometry(opt), 0)
    require(total_solids[0] > 0, 'No native positive-volume fixture solids')
    require(count[0] > 0 and len(points) >= 12,
            'Could not identify actual clear glass by exact material ' +
            exact_material_name)
    bounds = extrema(points)
    span = [bounds['max'][i] - bounds['min'][i] for i in range(3)]
    require(max(span) > 0.2 and max(span) < 3.0,
            'Implausible native clear-glass region: ' + repr(span))
    return points, {
        'glass_face_count': count[0],
        'positive_volume_solids': total_solids[0],
        'glass_material': exact_material_name,
        'glass_material_ids': sorted(material_ids),
        'glass_point_count': len(points),
        'glass_aabb_world_ft': bounds,
        'glass_sizes_mm': [round(x * 304.8, 3) for x in span],
    }


def prepare_family(project, spec):
    family_doc = None
    try:
        family_doc = APP.OpenDocumentFile(spec['path'])
        require(family_doc.IsFamilyDocument,
                'Input RFA does not open as a Revit family')
        require(family_doc.OwnerFamily.FamilyCategory.Name == 'Lighting Fixtures',
                'Input RFA category unexpectedly differs')
        require(str(family_doc.OwnerFamily.FamilyPlacementType) ==
                spec['expected_family_placement'],
                'RFA placement type changed')
        family = family_doc.LoadFamily(project)
        require(isinstance(family, DB.Family), 'Native RFA failed to load')
        symbols = [project.GetElement(s) for s in family.GetFamilySymbolIds()]
        exact = []
        for sym in symbols:
            p = sym.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
            symname = unicode(p.AsString()) if p is not None and p.AsString() else name_of(sym)
            if symname == spec['exact_symbol']:
                exact.append(sym)
        require(len(symbols) == 1 and len(exact) == 1,
                'RFA has unexpected type choices: '+repr([name_of(s) for s in symbols]))
        return exact[0]
    finally:
        if family_doc is not None:
            family_doc.Close(False)


def disposable_fixture(project, spec, level, sym):
    if spec['placement'] == 'level':
        return (project.Create.NewFamilyInstance(
            DB.XYZ(0, 0, 8), sym, level,
            DB.Structure.StructuralType.NonStructural), None)
    if spec['placement'] == 'ceiling_face':
        ft = DB.Floor.GetDefaultFloorType(project, False)
        require(eid(ft) is not None and eid(ft) >= 0,
                'No floor type in unsaved project')
        path = [DB.XYZ(-7, -7, 10), DB.XYZ(7, -7, 10),
                DB.XYZ(7, 7, 10), DB.XYZ(-7, 7, 10)]
        loop = DB.CurveLoop()
        for i in range(4):
            loop.Append(DB.Line.CreateBound(path[i], path[(i + 1) % 4]))
        floor = DB.Floor.Create(
            project, List[DB.CurveLoop]([loop]), ft, level.Id)
        project.Regenerate()
        underside = list(DB.HostObjectUtils.GetBottomFaces(floor))
        require(len(underside) > 0, 'Disposable ceiling underside missing')
        reference = underside[0]
        face = floor.GetGeometryObjectFromReference(reference)
        pt = face.Project(DB.XYZ(0, 0, 10)).XYZPoint
        inst = project.Create.NewFamilyInstance(
            reference, pt, DB.XYZ.BasisX, sym)
        require(inst.Host is not None and inst.Host.Id == floor.Id
                and inst.HostFace is not None,
                'Original Quorum face-host contract failed')
        return inst, floor
    raise RuntimeError('Unknown family host')


def make_generic_material(project, suffix, color):
    label = 'PHGOOD_REALISTIC_QA_' + suffix
    mid = DB.Material.Create(project, label)
    mat = project.GetElement(mid)
    mat.Color = DB.Color(*color)
    mat.Transparency = 0
    chosen = None
    for generic in APP.GetAssets(DB.Visual.AssetType.Appearance):
        marker = generic.FindByName('BaseSchema')
        if marker is not None and marker.Value == 'GenericSchema':
            chosen = generic
            break
    require(chosen is not None, 'Revit GenericSchema render asset unavailable')
    asset = DB.AppearanceAssetElement.Create(project, label + '_RENDER', chosen)
    scope = DB.Visual.AppearanceAssetEditScope(project)
    try:
        edit = scope.Start(asset.Id)
        diffuse = edit.FindByName('generic_diffuse')
        require(diffuse is not None,
                'Generic appearance missing diffuse property')
        if diffuse.NumberOfConnectedProperties:
            diffuse.RemoveConnectedAsset()
        diffuse.SetValueAsColor(DB.Color(*color))
        transparency = edit.FindByName('generic_transparency')
        require(transparency is not None,
                'Generic appearance missing transparency property')
        transparency.Value = 0.0
        scope.Commit(True)
    finally:
        scope.Dispose()
    mat.AppearanceAssetId = asset.Id
    require(eid(mat.AppearanceAssetId) == eid(asset.Id),
            'Checker render appearance failed to bind')
    return mat


def checker_geometry(project, facepoints, eye_dir, right, up):
    """Optical target orientation is unique to each camera in each project."""
    glass = extrema(facepoints)
    center = xyz([(glass['min'][i] + glass['max'][i]) / 2.0
                  for i in range(3)])
    right_projections = [p.DotProduct(right) for p in facepoints]
    up_projections = [p.DotProduct(up) for p in facepoints]
    eye_projections = [p.DotProduct(eye_dir) for p in facepoints]
    width = max(right_projections) - min(right_projections) + 2 * CHECKER_MARGIN_FT
    height = max(up_projections) - min(up_projections) + 2 * CHECKER_MARGIN_FT
    require(width > 0.3 and height > 0.3,
            'Checkerboard is too small for optical contrast')
    require(width < 3.2 and height < 3.2,
            'Checkerboard too large for glass comparison')
    # Center the board on the glass screen projection, not on any canopy/stem.
    delta = min(eye_projections) - center.DotProduct(eye_dir)
    board = center.Add(eye_dir.Multiply(
        delta - CHECKER_GAP_FT - CHECKER_THICKNESS_FT))
    dark = make_generic_material(project, 'DARK', (14, 14, 17))
    light = make_generic_material(project, 'LIGHT', (245, 245, 238))
    materials = [dark, light]
    dsids = []
    corners_all = []
    samples_by_finish = {'DARK': [], 'LIGHT': []}
    for iy in range(CHECKER_GRID):
        for ix in range(CHECKER_GRID):
            x0 = (float(ix) / CHECKER_GRID - 0.5) * width
            x1 = (float(ix + 1) / CHECKER_GRID - 0.5) * width
            y0 = (float(iy) / CHECKER_GRID - 0.5) * height
            y1 = (float(iy + 1) / CHECKER_GRID - 0.5) * height
            abcd = [
                board.Add(right.Multiply(x0)).Add(up.Multiply(y0)),
                board.Add(right.Multiply(x1)).Add(up.Multiply(y0)),
                board.Add(right.Multiply(x1)).Add(up.Multiply(y1)),
                board.Add(right.Multiply(x0)).Add(up.Multiply(y1)),
            ]
            profile = DB.CurveLoop()
            for k in range(4):
                profile.Append(DB.Line.CreateBound(abcd[k], abcd[(k + 1) % 4]))
            which = (ix + iy) % 2
            mat = materials[which]
            solidopts = DB.SolidOptions(mat.Id, DB.ElementId.InvalidElementId)
            solid = DB.GeometryCreationUtilities.CreateExtrusionGeometry(
                List[DB.CurveLoop]([profile]),
                eye_dir,
                CHECKER_THICKNESS_FT,
                solidopts)
            # Confirm the material is present in the actual solid, before
            # DirectShape insertion (Revit Realistic requires render assets).
            require(any(eid(f.MaterialElementId) == eid(mat.Id)
                        for f in solid.Faces),
                    'Checker solid lost its material identity')
            ds = DB.DirectShape.CreateElement(
                project, DB.ElementId(DB.BuiltInCategory.OST_GenericModel))
            ds.ApplicationId = 'PHGood_Realistic_Optical_Test'
            ds.ApplicationDataId = 'tile_%d_%d' % (ix, iy)
            ds.SetShape(List[DB.GeometryObject]([solid]))
            dsids.append(eid(ds.Id))
            samples_by_finish['DARK' if which == 0 else 'LIGHT'].append(ds.Id)
            corners_all.extend(abcd)
            corners_all.extend(p.Add(eye_dir.Multiply(CHECKER_THICKNESS_FT))
                               for p in abcd)
    require(len(dsids) == CHECKER_GRID * CHECKER_GRID,
            'Checkerboard tile count incomplete')
    project.Regenerate()
    # Insertion/readback proves that actual independent model solids retain
    # their two distinct appearance-material IDs.
    for key, mats in [('DARK', dark), ('LIGHT', light)]:
        element = project.GetElement(samples_by_finish[key][0])
        opt = DB.Options()
        opt.DetailLevel = DB.ViewDetailLevel.Fine
        material_ids = set()
        for g in element.get_Geometry(opt):
            if isinstance(g, DB.Solid):
                for face in g.Faces:
                    material_ids.add(eid(face.MaterialElementId))
        require(eid(mats.Id) in material_ids,
                'DirectShape %s checker material did not survive readback' % key)
    front_proj = board.DotProduct(eye_dir) + CHECKER_THICKNESS_FT
    separation_ft = min(eye_projections) - front_proj
    require(abs(separation_ft - CHECKER_GAP_FT) < 0.00001,
            'Checkerboard front intersects glass or lies too far away')
    return {
        'board_center_ft': triplet(board),
        'board_width_in': round(width * 12, 3),
        'board_height_in': round(height * 12, 3),
        'checker_tile_count': len(dsids),
        'checker_material_ids': {'dark': eid(dark.Id), 'light': eid(light.Id)},
        'checker_material_rgb': {'dark': [14, 14, 17],
                                 'light': [245, 245, 238]},
        'nearest_clear_glass_to_checker_front_in': round(separation_ft * 12, 5),
        'checker_thickness_in': CHECKER_THICKNESS_FT * 12,
        'placed_geometry': 'native DirectShape SolidOptions per-face materials',
    }, corners_all


def all_bounds(points):
    return extrema(points)


def create_view(project, spec, view_label, center_points, checker_points,
                eye_dir, host):
    vft = [v for v in DB.FilteredElementCollector(project).OfClass(DB.ViewFamilyType)
           if v.ViewFamily == DB.ViewFamily.ThreeDimensional]
    require(bool(vft), 'No View3D type in disposable project')
    view = DB.View3D.CreateIsometric(project, vft[0].Id)
    view.Name = 'PHGOOD_REALISTIC_%s_%s' % (spec['id'], view_label)
    view.DetailLevel = DB.ViewDetailLevel.Fine
    # THIS MUST FAIL if Revit refuses Realistic; no Shaded fallback.
    view.DisplayStyle = REALISTIC
    require(view.DisplayStyle == REALISTIC,
            'Native Revit View3D does not support Realistic display')
    extent = extrema(center_points + checker_points)
    center = xyz([(extent['min'][i] + extent['max'][i]) * 0.5
                  for i in range(3)])
    dimension = max(extent['max'][i] - extent['min'][i]
                    for i in range(3))
    eye = center.Add(eye_dir.Multiply(dimension * 3.5 + 3.0))
    forward = center.Subtract(eye).Normalize()
    up = DB.XYZ.BasisZ
    if abs(forward.DotProduct(up)) > 0.98:
        up = DB.XYZ.BasisY
    right = forward.CrossProduct(up).Normalize()
    true_up = right.CrossProduct(forward).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, true_up, forward))
    padding = max(0.12, dimension * 0.18)
    section = DB.BoundingBoxXYZ()
    section.Min = xyz([extent['min'][i] - padding for i in range(3)])
    section.Max = xyz([extent['max'][i] + padding for i in range(3)])
    view.SetSectionBox(section)
    view.IsSectionBoxActive = True
    # Keep the checker DirectShape category visible. Hide only host and
    # annotation/reference geometry, not the family Generic Model subparts.
    if host is not None:
        # Revit 2025 View3D has no CanElementBeHidden member. Ask the
        # element through CanBeHidden(view), and fail only if the wall/floor
        # cannot be hidden without also concealing the hosted fixture.
        try:
            if host.CanBeHidden(view):
                view.HideElements(List[DB.ElementId]([host.Id]))
        except Exception as err:
            raise RuntimeError('Host visibility check failed: '+str(err))
    for cat in project.Settings.Categories:
        try:
            nm = (name_of(cat) or '').lower()
            if (cat.CategoryType == DB.CategoryType.Annotation or
                    nm in ('light source', 'lights', 'reference planes',
                           'section boxes', 'cameras')):
                if view.CanCategoryBeHidden(cat.Id):
                    view.SetCategoryHidden(cat.Id, True)
        except Exception:
            pass
    try:
        white = DB.Color(255, 255, 255)
        view.SetBackground(DB.ViewDisplayBackground.CreateGradient(
            white, white, white))
    except Exception:
        # Failure to set white sky does not affect checker contrasts.
        pass
    project.Regenerate()
    # Square optical comparison crop. Revit's R05 FitToPage can sometimes
    # create e.g. 1200x3600 outputs; do not assume PixelSize is longest side.
    crop = view.CropBox
    inv = crop.Transform.Inverse
    local = [inv.OfPoint(pt) for pt in center_points + checker_points]
    xlo = min(x.X for x in local)
    xhi = max(x.X for x in local)
    ylo = min(x.Y for x in local)
    yhi = max(x.Y for x in local)
    halfside = max(xhi - xlo, yhi - ylo) * 0.66
    require(halfside > 0.05, 'Native optical region degenerate')
    midx, midy = (xlo + xhi) * 0.5, (ylo + yhi) * 0.5
    crop.Min = DB.XYZ(midx - halfside, midy - halfside, crop.Min.Z)
    crop.Max = DB.XYZ(midx + halfside, midy + halfside, crop.Max.Z)
    view.CropBox = crop
    view.CropBoxActive = True
    view.CropBoxVisible = False
    project.Regenerate()
    require(view.DisplayStyle == REALISTIC,
            'Native Realistic was reset while framing View3D')
    require(not view.IsPerspective and view.CropBoxActive,
            'Optical View3D is not a cropped orthographic view')
    return view, {
        'view_id': eid(view.Id), 'view_name': view.Name,
        'native_display_style': str(view.DisplayStyle),
        'orthographic': not view.IsPerspective,
        'camera_eye_from_glass': triplet(eye_dir),
        'framing': 'square_crop_of_actual_clear_glass_and_checker_only',
        'section_bounds_ft': {'min': triplet(section.Min),
                              'max': triplet(section.Max)},
        'checker_not_hidden': True,
        'aspect_crop_view_ft': [
            round((crop.Max.X - crop.Min.X), 5),
            round((crop.Max.Y - crop.Min.Y), 5)],
    }


def png_dims(path):
    with open(path, 'rb') as f:
        header = f.read(24)
    require(len(header) == 24 and
            header[:8] == b'\x89PNG\r\n\x1a\n' and
            header[12:16] == b'IHDR',
            'Revit PNG export has invalid header')
    return list(struct.unpack('>II', header[16:24]))


def export_native_realistic(project, view, spec, label):
    require(view.DisplayStyle == REALISTIC,
            'Refusing export: view reverted to Shaded')
    require(view.ViewType == DB.ViewType.ThreeD,
            'Refusing export: not a native View3D')
    stem = '%s_%s' % (spec['id'], label)
    filename = stem + '.png'
    final = os.path.join(DEST, filename)
    prefix = os.path.join(DEST, 'revit_realistic_' + stem)
    require(not os.path.lexists(final),
            'Optical image already exists, no overwrite: ' + final)
    for existing in os.listdir(DEST):
        require(not (existing.startswith('revit_realistic_' + stem)
                     and existing.lower().endswith('.png')),
                'Prior Revit image for this view already exists')
    options = DB.ImageExportOptions()
    options.FilePath = prefix
    options.ExportRange = DB.ExportRange.SetOfViews
    options.SetViewsAndSheets(List[DB.ElementId]([view.Id]))
    options.ZoomType = DB.ZoomFitType.FitToPage
    options.FitDirection = DB.FitDirectionType.Horizontal
    options.PixelSize = PIXEL_WIDTH
    options.ImageResolution = DB.ImageResolution.DPI_150
    options.HLRandWFViewsFileType = DB.ImageFileType.PNG
    options.ShadowViewsFileType = DB.ImageFileType.PNG
    project.ExportImage(options)
    require(view.DisplayStyle == REALISTIC,
            'ExportImage silently reverted view away from Realistic')
    candidates = [os.path.join(DEST, n) for n in os.listdir(DEST)
                  if n.lower().endswith('.png') and
                  n.startswith('revit_realistic_' + stem)]
    require(len(candidates) == 1,
            'Expected one native PNG output, got: ' + repr(candidates))
    dimensions = png_dims(candidates[0])
    require(min(dimensions) >= 800 and
            max(dimensions) <= 5000 and
            max(dimensions) / float(min(dimensions)) <= 1.8,
            'Revit PNG framing invalid; refuse misleading optical QA: ' +
            repr(dimensions))
    os.rename(candidates[0], final)
    return {
        'path': final,
        'sha256': fingerprint(final)['sha256'],
        'pixels': dimensions,
        'bytes': os.path.getsize(final),
        'exporter': 'native Revit2025 Document.ExportImage',
        'display_style_verified': 'Realistic',
    }


def render_one(spec, label):
    source_before = fingerprint(spec['path'])
    require(source_before['sha256'] == spec['sha256'],
            'Source family digest changed before load')
    project = None
    tx = None
    record = {
        'target': spec['id'], 'view': label,
        'source_rfa': spec['path'],
        'source_sha256_expected': spec['sha256'],
        'started_utc': now(),
        'status': 'STARTED',
        'original_source_modified': False,
        'disposable_project_saved': False,
        'previews_are_photo_or_refraction_certification': False,
    }
    try:
        project = APP.NewProjectDocument(DB.UnitSystem.Imperial)
        require(project is not None and not project.IsFamilyDocument,
                'Cannot create standalone unsaved Revit test project')
        symbol = prepare_family(project, spec)
        tx = DB.Transaction(project, 'Disposable Realistic optical QA')
        require(tx.Start() == DB.TransactionStatus.Started,
                'Failed to start disposable project transaction')
        level = DB.Level.Create(project, 0.0)
        symbol.Activate()
        project.Regenerate()
        instance, host = disposable_fixture(project, spec, level, symbol)
        project.Regenerate()
        glasspoints, glass_receipt = physical_glass_points(
            project, instance, spec['glass_material'])
        direction = (DB.XYZ(0, -1, 0.04) if label == 'front'
                     else DB.XYZ(0.85, -1, 0.60)).Normalize()
        right = DB.XYZ.BasisZ.CrossProduct(direction).Normalize()
        up = direction.CrossProduct(right).Normalize()
        checker, board_points = checker_geometry(
            project, glasspoints, direction, right, up)
        view, view_receipt = create_view(
            project, spec, label, glasspoints, board_points, direction, host)
        record['glass'] = glass_receipt
        record['checker'] = checker
        record['camera_view'] = view_receipt
        require(len(list(project.GetWarnings())) == 0,
                'Temporary test project contains native Revit warnings')
        require(tx.Commit() == DB.TransactionStatus.Committed,
                'Temporary optical project transaction could not commit')
        tx = None
        require(view.DisplayStyle == REALISTIC,
                'Realistic unavailable after native project commit')
        record['png'] = export_native_realistic(project, view, spec, label)
        record['status'] = 'NATIVE_REALISTIC_PNG_SAVED'
    except Exception:
        record['status'] = 'FAILED_NO_OPTICAL_PASS'
        record['error'] = traceback.format_exc()
    finally:
        if tx is not None:
            try:
                tx.RollBack()
            except Exception:
                pass
        if project is not None:
            try:
                project.Close(False)
            except Exception as e:
                record['close_error'] = str(e)
                record['status'] = 'FAILED_CLOSE'
        source_after = fingerprint(spec['path'])
        record['source_after_sha256'] = source_after['sha256']
        record['original_source_modified'] = (
            source_before['sha256'] != source_after['sha256'])
        if record['original_source_modified']:
            record['status'] = 'FAIL_SOURCE_SHA_CHANGED'
        record['finished_utc'] = now()
    return record


def receipt_once(obj):
    require(not os.path.lexists(RECEIPT),
            'Prior Realistic receipt exists, no overwrite')
    tmp = RECEIPT + '.tmp'
    require(not os.path.lexists(tmp),
            'Temporary receipt exists; inspect before retrying')
    data = json.dumps(obj, ensure_ascii=True, sort_keys=True, indent=2)
    handle = os.open(tmp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    try:
        with os.fdopen(handle, 'wb') as f:
            if isinstance(data, unicode):
                data = data.encode('ascii', 'strict')
            f.write(data)
        require(not os.path.lexists(RECEIPT),
                'Other run created receipt during export')
        os.rename(tmp, RECEIPT)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


def main():
    # Independent release check: exact native converter receipts must exist
    # and verify candidate hashes. No autogenerated hash trust from filenames.
    expected_receipts = {
        'bolla_r04': os.path.join(ROOT, 'qa', 'bolla_r04_clear_glass_receipt.json'),
        'quorum_r05': os.path.join(ROOT, 'qa', 'quorum_r05_clear_glass_receipt.json'),
    }
    for spec in TARGETS:
        receipt_path = expected_receipts[spec['id']]
        require(os.path.isfile(receipt_path),
                'Native material conversion receipt missing: '+receipt_path)
        with open(receipt_path,'rb') as handle:
            prior=json.load(handle)
        require(prior.get('status')=='NATIVE_RFA_APPEARANCE_CANDIDATE_UNAPPROVED' and
                prior.get('geometry_and_original_paint_unchanged') is True,
                'Converter did not pass its native part and paint safeguards')
        require(os.path.normcase(prior['candidate_rfa']) ==
                os.path.normcase(spec['path']),
                'Converter receipt candidate path mismatched')
        spec['sha256']=prior['candidate_sha256']
    require(sys.version_info[0] == 2,
            'Standalone IronPython 2.7 process required')
    require(str(APP.VersionNumber) == '2025',
            'Revit 2025 required')
    require(getattr(__revit__, 'ActiveUIDocument', None) is None,
            'Use an isolated Revit process with no open user documents')
    require(str(REALISTIC) == 'Realistic',
            'Revit API lacks DB.DisplayStyle.Realistic')
    require(len(TARGETS) == 2 and set([s['id'] for s in TARGETS]) ==
            set(['bolla_r04', 'quorum_r05']),
            'Exact two-target optical scope changed')
    for s in TARGETS:
        require(fingerprint(s['path'])['sha256'] == s['sha256'],
                'Exact RFA version changed: ' + s['path'])
    require(not os.path.lexists(RECEIPT),
            'Realistic optical batch receipt already exists')
    if not os.path.isdir(DEST):
        os.makedirs(DEST)
    # No file overwrites, including partially exported files from prior runs.
    require(len(os.listdir(DEST)) == 0,
            'Optical output folder is nonempty: review existing artifacts '
            'instead of rerunning')
    report = {
        'schema_version': 1,
        'purpose': '651 Belmont PH Good Bolla R04 and Quorum R05 optical glass comparison',
        'started_utc': now(),
        'native_revit_version': str(APP.VersionNumber),
        'display_style_required': 'Realistic',
        'checkerboard_expected_squares': CHECKER_GRID * CHECKER_GRID,
        'test_placement': 'isolated unsaved project per family and camera',
        'rfa_count': 2, 'expected_images': 4,
        'sources_saved': False, 'disposable_projects_saved': False,
        'optical_conclusion_requires_visual_review': True,
        'results': [],
    }
    for spec in TARGETS:
        for label in ('front', 'oblique'):
            print('REALISTIC_OPTICAL_START %s %s' % (spec['id'], label))
            sys.stdout.flush()
            result = render_one(spec, label)
            report['results'].append(result)
            print('REALISTIC_OPTICAL_%s %s %s' % (
                result['status'], spec['id'], label))
            sys.stdout.flush()
            if result['status'] != 'NATIVE_REALISTIC_PNG_SAVED':
                # Fail early. A missing or non-Realistic image cannot be
                # converted into a successful optical acceptance receipt.
                break
        if report['results'][-1]['status'] != 'NATIVE_REALISTIC_PNG_SAVED':
            break
    report['finished_utc'] = now()
    report['successful_native_realistic_images'] = len([
        x for x in report['results']
        if x['status'] == 'NATIVE_REALISTIC_PNG_SAVED'])
    report['all_sources_unchanged'] = all(
        not x['original_source_modified'] for x in report['results'])
    report['all_four_realistic_images_ready'] = (
        report['successful_native_realistic_images'] == 4
        and report['all_sources_unchanged'])
    report['release_ready'] = False
    report['readback_status'] = ('FOUR_IMAGES_READY_FOR_HUMAN_OPTICAL_QA'
                                 if report['all_four_realistic_images_ready']
                                 else 'FAILED_OR_INCOMPLETE')
    receipt_once(report)
    print('REALISTIC_OPTICAL_RECEIPT ' + RECEIPT)
    if not report['all_four_realistic_images_ready']:
        raise RuntimeError(
            'Realistic exporter did not validate four required images. '
            'Read exact failure from ' + RECEIPT)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('REALISTIC_OPTICAL_EXPORT_FAILED ' + traceback.format_exc())
        raise
