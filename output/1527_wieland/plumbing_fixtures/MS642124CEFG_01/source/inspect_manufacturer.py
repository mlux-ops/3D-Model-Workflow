# -*- coding: utf-8 -*-
"""Inspect and upgrade the unmodified public TOTO manufacturer family."""
import os
import json
import time
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

SECTION = r'E:\Claude\3D-Model-Workflow\output\1527_wieland\plumbing_fixtures'
OUT = os.path.join(SECTION, 'MS642124CEFG_01')
SOURCE = os.path.join(SECTION, '_research', 'MS642124CEFG_01', 'downloads', 'BM-00593_MS642124CEFG_MS642124CUFG.rfa')
TARGET = os.path.join(OUT, 'TOTO_Nexus_MS642124CEFG_R2025.rfa')
r = {'started_at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'source_path': SOURCE, 'rfa_path': TARGET,
     'source_url': 'https://www.totousa.com/filemanager_uploads/product_assets/REVITModels/BM-00593_MS642124CEFG_MS642124CUFG.rfa',
     'success': False, 'visual_review': 'pending', 'dimensions_gate': 'pending', 'flex_gate': 'pending'}
doc = None
tx = None

def checkpoint(stage):
    r['stage'] = stage
    with open(os.path.join(OUT, 'validation.json'), 'w') as f:
        json.dump(r, f, indent=2, default=str)

def geometry_points(geometry):
    points = []
    materials = set()
    volume = 0.0
    if geometry is None:
        return points, materials, volume
    for g in geometry:
        if isinstance(g, DB.GeometryInstance):
            p, m, v = geometry_points(g.GetInstanceGeometry())
            points.extend(p); materials.update(m); volume += v
        elif isinstance(g, DB.Solid) and g.Volume > 1e-10:
            volume += g.Volume
            for edge in g.Edges:
                points.extend(list(edge.Tessellate()))
            for face in g.Faces:
                materials.add(str(face.MaterialElementId.Value))
        elif isinstance(g, DB.Mesh):
            points.extend(list(g.Vertices))
            materials.add(str(g.MaterialElementId.Value))
    return points, materials, volume

def bbox(points):
    if not points:
        return None
    return [min(getattr(p, a) for p in points)*304.8 for a in ['X', 'Y', 'Z']] + [max(getattr(p, a) for p in points)*304.8 for a in ['X', 'Y', 'Z']]

def measure(document):
    options = DB.Options()
    options.DetailLevel = DB.ViewDetailLevel.Fine
    parts = []
    all_points = []
    for e in DB.FilteredElementCollector(document).WhereElementIsNotElementType():
        if not isinstance(e, (DB.GenericForm, DB.FamilyInstance, DB.ImportInstance, DB.DirectShape)):
            continue
        if isinstance(e, DB.GenericForm) and not e.IsSolid:
            continue
        try:
            points, materials, volume = geometry_points(e.get_Geometry(options))
            if not points:
                continue
            b = bbox(points)
            name = DB.Element.Name.GetValue(e)
            parts.append({'id': str(e.Id.Value), 'class': e.GetType().Name, 'name': name,
                          'category': e.Category.Name if e.Category else None,
                          'subcategory': e.Subcategory.Name if isinstance(e, DB.GenericForm) and e.Subcategory else None,
                          'bounds_mm': b, 'dimensions_mm': [b[i+3]-b[i] for i in range(3)],
                          'material_ids': sorted(materials), 'volume_ft3': volume})
            all_points.extend(points)
        except Exception:
            r.setdefault('measurement_errors', []).append({'id': str(e.Id.Value), 'error': traceback.format_exc()})
    return {'bounds_mm': bbox(all_points), 'parts': parts}

def parameter_value(ft, parameter):
    try:
        if parameter.StorageType == DB.StorageType.String:
            return ft.AsString(parameter)
        if parameter.StorageType == DB.StorageType.Double:
            return ft.AsDouble(parameter)
        if parameter.StorageType == DB.StorageType.Integer:
            return ft.AsInteger(parameter)
        if parameter.StorageType == DB.StorageType.ElementId:
            return str(ft.AsElementId(parameter).Value)
    except Exception:
        return None

try:
    checkpoint('script invoked')
    app = __revit__.Application
    r['revit_version'] = app.VersionNumber
    r['revit_build'] = app.VersionBuild
    assert app.VersionNumber == '2025'
    info = DB.BasicFileInfo.Extract(SOURCE)
    for key in ['Format', 'SavedInVersion', 'IsSavedInCurrentVersion', 'IsSavedInLaterVersion']:
        try:
            r.setdefault('source_file_info', {})[key] = str(getattr(info, key))
        except Exception:
            pass
    info.Dispose()
    doc = app.OpenDocumentFile(SOURCE)
    assert doc.IsFamilyDocument
    r['category'] = doc.OwnerFamily.FamilyCategory.Name
    r['placement'] = str(doc.OwnerFamily.FamilyPlacementType)
    fm = doc.FamilyManager
    r['parameters'] = [{'name': p.Definition.Name, 'storage': str(p.StorageType), 'instance': p.IsInstance,
                        'readonly': p.IsReadOnly, 'formula': p.Formula} for p in fm.Parameters]
    r['types'] = [{'name': ft.Name, 'values': {p.Definition.Name: parameter_value(ft, p) for p in fm.Parameters}} for ft in fm.Types]
    r['nested_families'] = [{'id': str(f.Id.Value), 'name': f.Name, 'editable': f.IsEditable, 'in_place': f.IsInPlace} for f in DB.FilteredElementCollector(doc).OfClass(DB.Family)]
    for nested in DB.FilteredElementCollector(doc).OfClass(DB.Family):
        if nested.IsEditable and nested.Name == 'BM-00561_SS124':
            seat = doc.EditFamily(nested)
            seat_dir = os.path.join(SECTION, 'SS124_01')
            if not os.path.isdir(seat_dir): os.makedirs(seat_dir)
            seat_path = os.path.join(seat_dir, 'TOTO_SS124_Manufacturer_Extracted_R2025.rfa')
            seat_save = DB.SaveAsOptions(); seat_save.OverwriteExistingFile = True; seat_save.MaximumBackups = 1
            seat.SaveAs(seat_path, seat_save)
            r['extracted_seat'] = {'path': seat_path, 'category': seat.OwnerFamily.FamilyCategory.Name, 'measured': measure(seat)}
            seat.Close(False)
    checkpoint('family opened and types inspected')
    tx = DB.Transaction(doc, 'Select exact Nexus 1.28 GPF type and add review views'); tx.Start()
    candidates = [ft for ft in fm.Types if 'MS642124CEFG' in ft.Name.upper()]
    if candidates:
        fm.CurrentType = candidates[0]
    model_parameter = fm.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MODEL)
    r['source_model_typo'] = parameter_value(fm.CurrentType, model_parameter)
    fm.SetFormula(model_parameter, None)
    fm.Set(model_parameter, 'MS642124CEFG#01')
    r['metadata_correction'] = 'Manufacturer source type is MS642124CEFG but Model formula says MS642234CEFG. Corrected the separate 2025 copy to the requested source type; original RFA preserved.'
    r['selected_type'] = fm.CurrentType.Name if fm.CurrentType else None
    doc.Regenerate()
    measured = measure(doc)
    r['measured'] = measured
    bounds = measured['bounds_mm']
    assert bounds is not None
    center = DB.XYZ(*[(bounds[i]+bounds[i+3])/609.6 for i in range(3)])
    span = max(bounds[i+3]-bounds[i] for i in range(3))/304.8
    vtype = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    views = []
    for name, direction in [('QA Front', (0, -1, 0)), ('QA Side', (1, 0, 0)), ('QA Oblique', (1, -1.5, 1))]:
        view = DB.View3D.CreateIsometric(doc, vtype.Id); view.Name = name
        eye = center.Add(DB.XYZ(*direction).Normalize().Multiply(span*3))
        forward = center.Subtract(eye).Normalize()
        right = forward.CrossProduct(DB.XYZ.BasisZ).Normalize()
        view.SetOrientation(DB.ViewOrientation3D(eye, right.CrossProduct(forward), forward))
        view.DetailLevel = DB.ViewDetailLevel.Fine
        view.DisplayStyle = DB.DisplayStyle.Shading
        for category in doc.Settings.Categories:
            if category.Id not in [doc.OwnerFamily.FamilyCategory.Id, DB.ElementId(DB.BuiltInCategory.OST_GenericModel)] and view.CanCategoryBeHidden(category.Id):
                view.SetCategoryHidden(category.Id, True)
        box = DB.BoundingBoxXYZ()
        box.Min = DB.XYZ(bounds[0]/304.8-.15, bounds[1]/304.8-.15, max(0, bounds[2]/304.8))
        box.Max = DB.XYZ(bounds[3]/304.8+.15, bounds[4]/304.8+.15, bounds[5]/304.8+.15)
        view.SetSectionBox(box); view.IsSectionBoxActive = True
        views.append(view)
    tx.Commit(); tx = None
    save = DB.SaveAsOptions(); save.MaximumBackups = 1; save.OverwriteExistingFile = True; save.PreviewViewId = views[-1].Id
    doc.SaveAs(TARGET, save)
    checkpoint('2025 copy saved')
    export = DB.ImageExportOptions(); export.ExportRange = DB.ExportRange.SetOfViews
    export.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]))
    export.FilePath = os.path.join(OUT, 'Nexus')
    export.HLRandWFViewsFileType = DB.ImageFileType.PNG; export.ShadowViewsFileType = DB.ImageFileType.PNG
    export.ImageResolution = DB.ImageResolution.DPI_150; export.ZoomType = DB.ZoomFitType.FitToPage; export.PixelSize = 1400
    doc.ExportImage(export)
    doc.Close(False); doc = app.OpenDocumentFile(TARGET)
    r['reopened'] = doc.IsFamilyDocument
    r['reopened_category'] = doc.OwnerFamily.FamilyCategory.Name
    r['measured_after_reopen'] = measure(doc)
    r['warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    r['material_flex'] = {}
    fm = doc.FamilyManager
    tx = DB.Transaction(doc, 'Verify editable manufacturer materials'); tx.Start()
    alternate = DB.Material.Create(doc, 'QA temporary material')
    for pname in ['Product Material', 'Flush Lever Finish']:
        param = next(p for p in fm.Parameters if p.Definition.Name == pname)
        original = fm.CurrentType.AsElementId(param)
        fm.Set(param, alternate); doc.Regenerate()
        actual = measure(doc)
        ids = set(m for part in actual['parts'] for m in part['material_ids'])
        r['material_flex'][pname] = str(alternate.Value) in ids
        fm.Set(param, original); doc.Regenerate()
    tx.RollBack(); tx = None
    r['flex_gate'] = all(r['material_flex'].values())
    r['dimension_controls'] = 'Manufacturer fixes Width/Depth/Height with formulas. Materials flexed and restored; no unsupported product resizing asserted.'
    r['preview_files'] = [n for n in os.listdir(OUT) if n.endswith('.png')]
    r['save_reopen_gate'] = r['reopened'] and r['reopened_category'] == 'Plumbing Fixtures'
    checkpoint('saved and reopened; dimensional and material review pending')
except Exception:
    r['error'] = traceback.format_exc()
    checkpoint('failed at ' + r.get('stage', 'start'))
finally:
    if tx is not None:
        try: tx.RollBack()
        except Exception: pass
    if doc is not None:
        try: doc.Close(False)
        except Exception: pass
