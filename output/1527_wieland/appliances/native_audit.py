# -*- coding: utf-8 -*-
"""Audit and upgrade manufacturer families through the shared serialized runner."""
import os
import json
import glob
import traceback
import datetime
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = os.path.dirname(os.path.abspath(__file__))
REPORT_NAME = os.environ.get('APPLIANCE_AUDIT_REPORT', 'native_audit.json')
REPORT = {'started_utc': str(datetime.datetime.utcnow()), 'items': []}

def dump():
    def clean(value):
        if isinstance(value, str):
            try:
                return value.decode('utf-8')
            except UnicodeDecodeError:
                return value.decode('cp1252', 'replace')
        if isinstance(value, dict):
            return dict((clean(k), clean(v)) for k, v in value.items())
        if isinstance(value, (list, tuple)):
            return [clean(v) for v in value]
        if isinstance(value, float) and (value == float('inf') or value == float('-inf')):
            return None
        return value
    payload = json.dumps(clean(REPORT), indent=2, default=unicode)
    with open(os.path.join(ROOT, REPORT_NAME), 'w') as f:
        f.write(payload)

def ename(element):
    return DB.Element.Name.__get__(element)

def points(geometry):
    for obj in geometry:
        if isinstance(obj, DB.Solid) and obj.Volume > 1e-10:
            for face in obj.Faces:
                mesh = face.Triangulate(1.0)
                if mesh:
                    for p in mesh.Vertices:
                        yield p
                else:
                    for edge_loop in face.EdgeLoops:
                        for edge in edge_loop:
                            for p in edge.Tessellate():
                                yield p
        elif isinstance(obj, DB.Mesh):
            for p in obj.Vertices:
                yield p
        elif isinstance(obj, DB.GeometryInstance):
            for p in points(obj.GetInstanceGeometry()):
                yield p

def measure(doc):
    opt = DB.Options()
    opt.DetailLevel = DB.ViewDetailLevel.Fine
    opt.IncludeNonVisibleObjects = False
    lo = [float('inf')] * 3
    hi = [float('-inf')] * 3
    parts = []
    for element in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        geometry = element.get_Geometry(opt)
        pp = list(points(geometry)) if geometry else []
        if not pp:
            continue
        xyz = [[p.X * 304.8, p.Y * 304.8, p.Z * 304.8] for p in pp]
        pmin = [min(p[i] for p in xyz) for i in range(3)]
        pmax = [max(p[i] for p in xyz) for i in range(3)]
        lo = [min(lo[i], pmin[i]) for i in range(3)]
        hi = [max(hi[i], pmax[i]) for i in range(3)]
        parts.append({'id': str(element.Id), 'class': element.GetType().Name,
                      'name': ename(element), 'min_mm': pmin, 'max_mm': pmax})
    return {'min_mm': lo, 'max_mm': hi, 'xyz_size_mm': [hi[i] - lo[i] for i in range(3)], 'parts': parts}

def preview(doc, folder, bounds):
    tx = DB.Transaction(doc, 'Appliance review view')
    tx.Start()
    vt = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
              if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(doc, vt.Id)
    view.Name = 'Wieland appliance review'
    lo, hi = bounds['min_mm'], bounds['max_mm']
    target = DB.XYZ(*[(lo[i] + hi[i]) / 609.6 for i in range(3)])
    fwd = DB.XYZ(-1, 1.5, -0.9).Normalize()
    up = fwd.CrossProduct(DB.XYZ.BasisZ).Normalize().CrossProduct(fwd).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(target.Subtract(fwd.Multiply(15)), up, fwd))
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.DisplayStyle = DB.DisplayStyle.Shading
    for category in doc.Settings.Categories:
        try:
            if category.Id != doc.OwnerFamily.FamilyCategory.Id and view.CanCategoryBeHidden(category.Id):
                view.SetCategoryHidden(category.Id, True)
        except Exception:
            pass
    box = DB.BoundingBoxXYZ()
    box.Min = DB.XYZ(*[(v - 20) / 304.8 for v in lo])
    box.Max = DB.XYZ(*[(v + 20) / 304.8 for v in hi])
    view.SetSectionBox(box)
    view.IsSectionBoxActive = True
    tx.Commit()
    output = os.path.join(folder, 'views')
    if not os.path.isdir(output):
        os.makedirs(output)
    opts = DB.ImageExportOptions()
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.SetViewsAndSheets(List[DB.ElementId]([view.Id]))
    opts.FilePath = os.path.join(output, 'native')
    opts.HLRandWFViewsFileType = DB.ImageFileType.PNG
    opts.ShadowViewsFileType = DB.ImageFileType.PNG
    opts.ImageResolution = DB.ImageResolution.DPI_150
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = 1200
    doc.ExportImage(opts)
    return glob.glob(os.path.join(output, '*.png'))

app = __revit__.Application
REPORT['revit_version'] = app.VersionNumber
dump()
slugs = os.environ.get('APPLIANCE_AUDIT_SLUGS', 'miele_h7280bp,miele_h7270bm,miele_g5051scvi,miele_kwt6722is').split(',')
for slug in slugs:
    sources = []
    for parent, dirs, files in os.walk(os.path.join(ROOT, slug, 'source', 'original')):
        for filename in files:
            if filename.lower().endswith('.rfa') and '2d' not in filename.lower():
                sources.append(os.path.join(parent, filename))
    sources.sort(key=lambda p: (len(p.split(os.sep)), len(os.path.basename(p))))
    if os.environ.get('APPLIANCE_PREFER_LEGACY') == '1':
        sources.sort(key=lambda p: ('-3d.rfa' not in p.lower(), len(p)))
    if not sources:
        continue
    result = {'slug': slug, 'source': sources[0], 'stage': 'starting', 'ok': False}
    REPORT['items'].append(result)
    doc = None
    try:
        result['source_revit_format'] = DB.BasicFileInfo.Extract(sources[0]).Format
        dump()
        doc = app.OpenDocumentFile(sources[0])
        result['stage'] = 'opened'
        result['category'] = doc.OwnerFamily.FamilyCategory.Name
        result['category_id'] = str(doc.OwnerFamily.FamilyCategory.Id)
        result['placement_type'] = str(doc.OwnerFamily.FamilyPlacementType)
        fm = doc.FamilyManager
        result['types'] = [t.Name for t in fm.Types]
        result['parameters'] = []
        for p in fm.Parameters:
            value = None
            if fm.CurrentType:
                if p.StorageType == DB.StorageType.String:
                    value = fm.CurrentType.AsString(p)
                elif p.StorageType == DB.StorageType.Double:
                    value = fm.CurrentType.AsDouble(p)
                elif p.StorageType == DB.StorageType.Integer:
                    value = fm.CurrentType.AsInteger(p)
                elif p.StorageType == DB.StorageType.ElementId:
                    eid = fm.CurrentType.AsElementId(p)
                    el = doc.GetElement(eid) if eid else None
                    value = ename(el) if el else str(eid)
            result['parameters'].append({'name': p.Definition.Name, 'value': value,
                                         'storage': str(p.StorageType), 'formula': p.Formula})
        result['material_inventory'] = []
        for material in DB.FilteredElementCollector(doc).OfClass(DB.Material):
            result['material_inventory'].append({'name': ename(material),
                'id': str(material.Id), 'appearance_id': str(material.AppearanceAssetId),
                'rgb': [material.Color.Red, material.Color.Green, material.Color.Blue],
                'transparency': material.Transparency})
        result['parameter_flex'] = []
        candidates = [p for p in fm.Parameters if p.StorageType == DB.StorageType.Integer
                      and not p.IsReadOnly and not p.Formula and p.Definition.Name.startswith('#')]
        for p in candidates[:4]:
            tx = DB.Transaction(doc, 'Validate manufacturer display parameter')
            try:
                tx.Start()
                before = fm.CurrentType.AsInteger(p)
                fm.Set(p, 0 if before else 1)
                doc.Regenerate()
                changed = fm.CurrentType.AsInteger(p)
                tx.RollBack()
                result['parameter_flex'].append({'name': p.Definition.Name, 'original': before,
                    'tested': changed, 'restored': fm.CurrentType.AsInteger(p), 'pass': changed != before})
            except Exception:
                if tx.HasStarted():
                    tx.RollBack()
                result['parameter_flex'].append({'name': p.Definition.Name, 'pass': False, 'error': traceback.format_exc()})
        result['bounds'] = measure(doc)
        result['warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
        result['stage'] = 'measured'
        dump()
        out = os.path.join(ROOT, slug, slug + '_R2025.rfa')
        options = DB.SaveAsOptions()
        options.OverwriteExistingFile = True
        doc.SaveAs(out, options)
        doc.Close(False)
        doc = app.OpenDocumentFile(out)
        result['saved_rfa'] = out
        result['reopened'] = True
        result['saved_revit_format'] = DB.BasicFileInfo.Extract(out).Format
        result['reopened_bounds'] = measure(doc)
        result['previews'] = preview(doc, os.path.join(ROOT, slug), result['reopened_bounds'])
        result['ok'] = True
        result['stage'] = 'saved_reopened_previewed'
    except Exception:
        result['error'] = traceback.format_exc()
    finally:
        if doc:
            try:
                doc.Close(False)
            except Exception:
                pass
        dump()
REPORT['finished_utc'] = str(datetime.datetime.utcnow())
dump()
