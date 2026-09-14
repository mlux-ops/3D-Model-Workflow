# -*- coding: utf-8 -*-
"""Run with the installed pyRevit CLI in a separate Revit 2025 process.

Creates only new family/project documents and writes inside this workspace.
All profile coordinates below are inches. Source and inferred dimensions are
documented in WORKFLOW.md. No existing project or source family is modified.
"""
import os
import json
import math
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow'
OUT = os.path.join(ROOT, 'output')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
RFA = os.path.join(OUT, 'KOHLER_Purist_K-T14489-4_CP_Visualization_R2025.rfa')
if not os.path.isdir(OUT):
    os.makedirs(OUT)
report = {'rfa_path': RFA, 'stage': 'start'}
docs = []
transaction = None


def checkpoint(stage):
    report['stage'] = stage
    with open(os.path.join(OUT, 'purist-validation.json'), 'w') as f:
        json.dump(report, f, indent=2, default=str)


def xyz(x, y, z):
    return DB.XYZ(x / 12.0, y / 12.0, z / 12.0)


def revolved(doc, name, origin, axis, points, matparam, subcategory):
    # Align the lever's revolve seam to its depth extremum so Revit's
    # display-derived bounding box includes the full analytic projection.
    radial = DB.XYZ.BasisZ if abs(axis.DotProduct(DB.XYZ.BasisY)) > 0.99 else DB.XYZ.BasisX
    frame = DB.Frame(origin, radial, axis.CrossProduct(radial), axis)
    def p(pair):
        return origin.Add(radial.Multiply(pair[0] / 12.0)).Add(axis.Multiply(pair[1] / 12.0))
    loop = DB.CurveLoop()
    start = points[0]
    current = start
    for item in points[1:]:
        if len(item) == 3 and item[0] == 'arc':
            mid, end = item[1], item[2]
            loop.Append(DB.Arc.Create(p(current), p(end), p(mid)))
        else:
            end = item
            loop.Append(DB.Line.CreateBound(p(current), p(end)))
        current = end
    loop.Append(DB.Line.CreateBound(p(current), p(start)))
    solid = DB.GeometryCreationUtilities.CreateRevolvedGeometry(frame, List[DB.CurveLoop]([loop]), 0, 2 * math.pi)
    element = DB.FreeFormElement.Create(doc, solid)
    element.Subcategory = subcategory
    comment = element.get_Parameter(DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
    if comment is not None and not comment.IsReadOnly:
        comment.Set(name)
    report.setdefault('parts', []).append({'name': name, 'element_id': str(element.Id.Value)})
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(
        element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), matparam)
    return element


def rounded_cylinder_profile(radius, start, end, rounding):
    r, a, b, q = radius, start, end, rounding
    k = 1.0 - math.sqrt(0.5)
    return [(0, a), (r-q, a), ('arc', (r-q*k, a+q*k), (r, a+q)),
            (r, b-q), ('arc', (r-q*k, b-q*k), (r-q, b)), (0, b)]


def asset_label(asset):
    labels = [asset.Name]
    for key in ['UIName', 'description', 'keyword', 'metal_color']:
        prop = asset.FindByName(key)
        if prop is not None:
            try:
                labels.append(str(prop.Value))
            except Exception:
                pass
    return ' | '.join(labels)


def make_chrome(doc, app):
    assets = list(app.GetAssets(DB.Visual.AssetType.Appearance))
    candidates = [(asset_label(a), a) for a in assets if 'chrome' in asset_label(a).lower()]
    report['chrome_candidates'] = [v[0] for v in candidates]
    if not candidates:
        raise RuntimeError('No native chrome appearance asset found; refusing a gray-only substitute')
    candidates.sort(key=lambda v: ('chrome - mirror' not in v[0].lower(),
                                    'black' in v[0].lower(), 'brushed' in v[0].lower(),
                                    'satin' in v[0].lower(), v[0]))
    label, asset = candidates[0]
    appearance = DB.AppearanceAssetElement.Create(doc, 'KOHLER CP - Polished Chrome', asset)
    mid = DB.Material.Create(doc, 'KOHLER CP - Polished Chrome')
    material = doc.GetElement(mid)
    material.MaterialClass = 'Metal'
    material.Color = DB.Color(190, 195, 200)
    material.Shininess = 128
    material.Smoothness = 100
    material.Transparency = 0
    material.AppearanceAssetId = appearance.Id
    report['chrome_appearance_asset'] = label
    return material


def all_solids(geometry):
    for item in geometry:
        if isinstance(item, DB.Solid) and item.Volume > 1e-12:
            yield item
        elif isinstance(item, DB.GeometryInstance):
            for solid in all_solids(item.GetInstanceGeometry()):
                yield solid


def model_bounds(elements):
    boxes = [e.get_BoundingBox(None) for e in elements]
    boxes = [b for b in boxes if b is not None]
    return [min(b.Min.X for b in boxes), min(b.Min.Y for b in boxes), min(b.Min.Z for b in boxes),
            max(b.Max.X for b in boxes), max(b.Max.Y for b in boxes), max(b.Max.Z for b in boxes)]


def preview_view(doc, name, eye, up, target):
    viewtype = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
                    if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(doc, viewtype.Id)
    view.Name = name
    forward = target.Subtract(eye).Normalize()
    right = forward.CrossProduct(up).Normalize()
    trueup = right.CrossProduct(forward).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, trueup, forward))
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.DisplayStyle = DB.DisplayStyle.Shading
    view.Scale = 1
    for category in doc.Settings.Categories:
        if category.Id != doc.OwnerFamily.FamilyCategory.Id and view.CanCategoryBeHidden(category.Id):
            try:
                view.SetCategoryHidden(category.Id, True)
            except Exception:
                pass
    # The face-based template's sample host is a same-category extrusion.
    # Hide that element in review views; category visibility alone cannot do it.
    hidden = [e.Id for e in DB.FilteredElementCollector(doc).OfClass(DB.GenericForm)
              if not isinstance(e, DB.FreeFormElement) and e.CanBeHidden(view)]
    if hidden:
        view.HideElements(List[DB.ElementId](hidden))
    section = DB.BoundingBoxXYZ()
    section.Min = xyz(-4.5,-5.2,0.001)
    section.Max = xyz(4.5,5.2,5.25)
    view.SetSectionBox(section)
    view.IsSectionBoxActive = True
    section_category = DB.ElementId(DB.BuiltInCategory.OST_SectionBox)
    if view.CanCategoryBeHidden(section_category):
        view.SetCategoryHidden(section_category, True)
    return view


def export_views(doc, views):
    options = DB.ImageExportOptions()
    options.ExportRange = DB.ExportRange.SetOfViews
    options.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]))
    options.FilePath = os.path.join(OUT, 'Purist')
    options.HLRandWFViewsFileType = DB.ImageFileType.PNG
    options.ShadowViewsFileType = DB.ImageFileType.PNG
    options.ImageResolution = DB.ImageResolution.DPI_150
    options.ZoomType = DB.ZoomFitType.FitToPage
    options.PixelSize = 1800
    doc.ExportImage(options)


try:
    app = __revit__.Application
    report['revit_version'] = app.VersionNumber
    report['revit_build'] = app.VersionBuild
    assert app.VersionNumber == '2025'
    checkpoint('create family')
    doc = app.NewFamilyDocument(TEMPLATE)
    docs.append(doc)
    transaction = DB.Transaction(doc, 'Build visualization fixture')
    transaction.Start()
    doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_PlumbingFixtures)
    always_vertical = doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)
    if always_vertical is not None and not always_vertical.IsReadOnly:
        always_vertical.Set(0)
    fm = doc.FamilyManager
    fm.NewType('K-T14489-4-CP - Polished Chrome')
    chrome = make_chrome(doc, app)
    finish = fm.AddParameter('Finish', DB.GroupTypeId.Materials, DB.SpecTypeId.Reference.Material, False)
    fm.Set(finish, chrome.Id)
    for name, value in [('Plate Diameter',7.25), ('Projection',4.25), ('Handle Axis Spacing',3.125), ('Overall Height',9.125)]:
        parameter = fm.AddParameter(name, DB.GroupTypeId.Geometry, DB.SpecTypeId.Length, False)
        fm.SetFormula(parameter, str(value) + '"')
    for builtin, value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, 'KOHLER'),
                           (DB.BuiltInParameter.ALL_MODEL_MODEL, 'K-T14489-4-CP'),
                           (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION, 'Purist stacked valve trim; visualization model; nominal fixed size; no MEP connectors')]:
        param = fm.get_Parameter(builtin)
        if param is not None:
            fm.Set(param, value)
    note = fm.AddParameter('Model Accuracy Notes', DB.GroupTypeId.IdentityData, DB.SpecTypeId.String.Text, False)
    fm.Set(note, 'Nominal inch dimensions from KOHLER drawing. Undimensioned barrel/lever diameters, plate profile and edge rounding inferred. Rendering approximation, not fabrication geometry.')
    categories = {}
    for name in ['Escutcheon', 'Handle Bodies', 'Levers']:
        cat = doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory, name)
        cat.Material = chrome
        categories[name] = cat
    elements = []
    plate = [(0,0), (3.575,0), ('arc',(3.610355,0.014645),(3.625,0.05)),
             (3.625,0.45), ('arc',(3.610355,0.485355),(3.575,0.5)),
             (3.45,0.5), ('arc',(2.935,0.515),(2.425,0.625)), (0,0.625)]
    elements.append(revolved(doc, 'Escutcheon - nominal diameter 7.25 in', DB.XYZ.Zero, DB.XYZ.BasisZ, plate, finish, categories['Escutcheon']))
    for label, y, lo, hi in [('Upper',1.5625,-1.35,3.0), ('Lower',-1.5625,-3.0,1.35)]:
        origin = xyz(0,y,0)
        elements.append(revolved(doc, label+' cylindrical sleeve', origin, DB.XYZ.BasisZ,
                                 rounded_cylinder_profile(0.8,0.61,2.72,0.025), finish, categories['Handle Bodies']))
        elements.append(revolved(doc, label+' collar', origin, DB.XYZ.BasisZ,
                                 rounded_cylinder_profile(0.8,2.73,2.84,0.03), finish, categories['Handle Bodies']))
        neck = [(0,2.70), (0.70,2.70), (0.70,2.82),
                ('arc',(0.405,2.89),(0.27,3.15)), (0.27,3.58),
                ('arc',(0.295,3.68),(0.35,3.76)), (0.35,3.94), (0,3.94)]
        elements.append(revolved(doc, label+' stem', origin, DB.XYZ.BasisZ, neck, finish, categories['Handle Bodies']))
        elements.append(revolved(doc, label+' lever', xyz(0,y,3.9375), DB.XYZ.BasisY,
                                 rounded_cylinder_profile(0.3125,lo,hi,0.04), finish, categories['Levers']))
    doc.Regenerate()
    target = xyz(0,0,2)
    views = [preview_view(doc, 'Visualization - Three Quarter', xyz(14,8,22), DB.XYZ.BasisY, target),
             preview_view(doc, 'Visualization - Front', xyz(0,0,24), DB.XYZ.BasisY, target),
             preview_view(doc, 'Visualization - Side', xyz(24,0,2), DB.XYZ.BasisY, target)]
    transaction.Commit()
    transaction = None
    checkpoint('save family')
    options = DB.SaveAsOptions()
    options.OverwriteExistingFile = True
    options.MaximumBackups = 1
    options.PreviewViewId = views[0].Id
    doc.SaveAs(RFA, options)
    report['export_error'] = None
    try:
        export_views(doc, views)
    except Exception:
        report['export_error'] = traceback.format_exc()
    doc.Close(False)
    docs.remove(doc)
    checkpoint('reopen saved family')
    doc = app.OpenDocumentFile(RFA)
    docs.append(doc)
    report['reopened'] = doc.IsFamilyDocument
    report['category'] = doc.OwnerFamily.FamilyCategory.Name
    report['placement'] = str(doc.OwnerFamily.FamilyPlacementType)
    elements = list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    bounds = model_bounds(elements)
    report['family_bounds_inches'] = [v * 12 for v in bounds]
    report['geometry_width_inches'] = (bounds[3]-bounds[0])*12
    report['geometry_height_inches'] = (bounds[4]-bounds[1])*12
    report['geometry_projection_inches'] = (bounds[5]-bounds[2])*12
    report['solid_count'] = len(elements)
    report['solid_volume_cubic_inches'] = sum(s.Volume * 1728 for e in elements for s in all_solids(e.get_Geometry(DB.Options())))
    depth_ray = DB.Line.CreateBound(xyz(0,1.5625,-1), xyz(0,1.5625,10))
    ray_depths = []
    for element in elements:
        for solid in all_solids(element.get_Geometry(DB.Options())):
            intersection = solid.IntersectWithCurve(depth_ray, DB.SolidCurveIntersectionOptions())
            for index in range(intersection.SegmentCount):
                segment = intersection.GetCurveSegment(index)
                ray_depths.extend([segment.GetEndPoint(0).Z*12, segment.GetEndPoint(1).Z*12])
    report['analytic_projection_inches'] = max(ray_depths)
    report['warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    checkpoint('load into disposable native project')
    project = app.NewProjectDocument(DB.UnitSystem.Imperial)
    docs.append(project)
    family = doc.LoadFamily(project)
    symbol = project.GetElement(list(family.GetFamilySymbolIds())[0])
    transaction = DB.Transaction(project, 'Verify face placement and finish')
    transaction.Start()
    level = next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)), None)
    if level is None:
        level = DB.Level.Create(project, 0)
    walltype = next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind == DB.WallKind.Basic)
    line = DB.Line.CreateBound(DB.XYZ(-4,0,0), DB.XYZ(4,0,0))
    wall = DB.Wall.Create(project, line, walltype.Id, level.Id, 8, 0, False, False)
    symbol.Activate()
    project.Regenerate()
    refs = DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior)
    face = wall.GetGeometryObjectFromReference(refs[0])
    point = face.Project(DB.XYZ(0,0,4)).XYZPoint
    instance = project.Create.NewFamilyInstance(refs[0], point, DB.XYZ.BasisX, symbol)
    project.Regenerate()
    report['loaded_and_face_placed'] = instance.Host is not None and instance.Host.Id == wall.Id
    report['mounting_normal_dot_host_normal'] = instance.GetTransform().BasisZ.DotProduct(face.FaceNormal)
    placedbox = instance.get_BoundingBox(None)
    report['placed_dimensions_inches'] = [(placedbox.Max.X-placedbox.Min.X)*12,
                                          (placedbox.Max.Y-placedbox.Min.Y)*12,
                                          (placedbox.Max.Z-placedbox.Min.Z)*12]
    param = symbol.LookupParameter('Finish')
    original = param.AsElementId()
    alternate = DB.Material.Create(project, 'QA temporary alternate finish')
    param.Set(alternate)
    project.Regenerate()
    face_materials = [f.MaterialElementId for s in all_solids(instance.get_Geometry(DB.Options())) for f in s.Faces]
    report['material_parameter_test'] = bool(face_materials) and all(mid == alternate for mid in face_materials)
    param.Set(original)
    project.Regenerate()
    transaction.Commit()
    transaction = None
    report['project_warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]
    report['preview_files'] = [os.path.join(OUT, name) for name in os.listdir(OUT) if name.startswith('Purist') and name.endswith('.png')]
    checkpoint('complete')
except Exception:
    report['error'] = traceback.format_exc()
    checkpoint('failed at '+report['stage'])
finally:
    if transaction is not None:
        try:
            transaction.RollBack()
        except Exception:
            pass
    for document in reversed(docs):
        try:
            document.Close(False)
        except Exception:
            pass
