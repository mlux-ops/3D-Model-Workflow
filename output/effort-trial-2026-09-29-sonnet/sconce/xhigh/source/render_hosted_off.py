# -*- coding: utf-8 -*-
"""pyRevit: places the saved family on a disposable wall, sets the instance's Show Disc = No, and exports
front / side / oblique views (walls + fixture only). Nothing is saved. Used for the white-variant photo comparison,
because a family-document view does not apply the visibility parameter (exports were pixel-identical to Show Disc = Yes)."""
import sys
import os
import itertools
import traceback
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/source')
from guard import dump_json, safe_path
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RUN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/'
RFA = RUN + 'Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa'
OUTD = RUN + 'work/export_hosted_off/'
rep = {}
docs = []
try:
    app = __revit__.Application
    fdoc = app.OpenDocumentFile(RFA)
    docs.append(fdoc)
    rep['family_warnings_on_open'] = [w.GetDescriptionText() for w in fdoc.GetWarnings()]
    project = app.NewProjectDocument(DB.UnitSystem.Imperial)
    docs.append(project)
    fam = fdoc.LoadFamily(project)
    symbol = project.GetElement(list(fam.GetFamilySymbolIds())[0])
    tx = DB.Transaction(project, 'place')
    tx.Start()
    level = next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)))
    wt = next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind == DB.WallKind.Basic)
    wall = DB.Wall.Create(project, DB.Line.CreateBound(DB.XYZ(-8, 0, 0), DB.XYZ(8, 0, 0)), wt.Id, level.Id, 10, 0, False, False)
    symbol.Activate()
    project.Regenerate()
    ref = DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior)[0]
    face = wall.GetGeometryObjectFromReference(ref)
    normal = face.FaceNormal
    ptA = face.Project(DB.XYZ(0, 0, 5)).XYZPoint
    inst = project.Create.NewFamilyInstance(ref, ptA, DB.XYZ.BasisZ.CrossProduct(normal), symbol)
    project.Regenerate()
    inst.LookupParameter('Show Disc').Set(0)
    project.Regenerate()
    rep['show_disc_instance'] = inst.LookupParameter('Show Disc').AsInteger()
    bb = inst.get_BoundingBox(None)
    rep['instance_bbox_in'] = [[round(bb.Min.X * 12, 4), round(bb.Min.Y * 12, 4), round(bb.Min.Z * 12, 4)],
                               [round(bb.Max.X * 12, 4), round(bb.Max.Y * 12, 4), round(bb.Max.Z * 12, 4)]]
    tx.Commit()

    tx = DB.Transaction(project, 'view')
    tx.Start()
    vtype = next(v for v in DB.FilteredElementCollector(project).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    keep = (DB.BuiltInCategory.OST_Walls, DB.BuiltInCategory.OST_LightingFixtures)
    keep_ids = [DB.Category.GetCategory(project, k).Id.Value for k in keep]
    left = normal.CrossProduct(DB.XYZ.BasisZ)
    tgt = DB.XYZ(ptA.X, ptA.Y + 3.5 / 12.0, ptA.Z)
    variants = [('off oblique', (45.2, 38.0, 10.4)),
                ('off side', (0.0, 60.0, 0.0)),
                ('off front', (60.0, 0.0, 0.0))]
    vids = []
    for vname, voff in variants:
        eye = tgt.Add(normal.Multiply(voff[0] / 12.0)).Add(left.Multiply(voff[1] / 12.0)).Add(DB.XYZ.BasisZ.Multiply(voff[2] / 12.0))
        fwd = tgt.Subtract(eye).Normalize()
        right = fwd.CrossProduct(DB.XYZ.BasisZ).Normalize()
        if abs(fwd.Z) > 0.99:
            right = DB.XYZ.BasisX
        view = DB.View3D.CreateIsometric(project, vtype.Id)
        view.Name = vname
        view.SetOrientation(DB.ViewOrientation3D(eye, right.CrossProduct(fwd).Normalize(), fwd))
        view.DetailLevel = DB.ViewDetailLevel.Fine
        view.DisplayStyle = DB.DisplayStyle.Shading
        for cat in project.Settings.Categories:
            if cat.Id.Value not in keep_ids and view.CanCategoryBeHidden(cat.Id):
                view.SetCategoryHidden(cat.Id, True)
        region = DB.BoundingBoxXYZ()
        region.Min = DB.XYZ(ptA.X - 14.0 / 12.0, ptA.Y - 4.0 / 12.0, ptA.Z - 12.0 / 12.0)
        region.Max = DB.XYZ(ptA.X + 14.0 / 12.0, ptA.Y + 8.0 / 12.0, ptA.Z + 12.0 / 12.0)
        view.SetSectionBox(region)
        view.IsSectionBoxActive = True
        project.Regenerate()
        view.CropBoxActive = True
        view.CropBoxVisible = False
        cb = view.CropBox
        inv2 = cb.Transform.Inverse
        xs = []
        ys = []
        for cx, cy, cz in itertools.product((ptA.X - 5.0 / 12.0, ptA.X + 5.0 / 12.0), (ptA.Y - 4.0 / 12.0, ptA.Y + 6.0 / 12.0), (ptA.Z - 4.5 / 12.0, ptA.Z + 4.5 / 12.0)):
            q = inv2.OfPoint(DB.XYZ(cx, cy, cz))
            xs.append(q.X)
            ys.append(q.Y)
        pad = 2.0 / 12.0
        cb.Min = DB.XYZ(min(xs) - pad, min(ys) - pad, cb.Min.Z)
        cb.Max = DB.XYZ(max(xs) + pad, max(ys) + pad, cb.Max.Z)
        view.CropBox = cb
        vids.append(view.Id)
    tx.Commit()
    if not os.path.isdir(OUTD):
        os.makedirs(OUTD)
    safe_path(OUTD + 'x')
    eo = DB.ImageExportOptions()
    eo.ExportRange = DB.ExportRange.SetOfViews
    eo.SetViewsAndSheets(List[DB.ElementId](vids))
    eo.FilePath = OUTD + 'hosted'
    eo.HLRandWFViewsFileType = DB.ImageFileType.PNG
    eo.ShadowViewsFileType = DB.ImageFileType.PNG
    eo.ImageResolution = DB.ImageResolution.DPI_150
    eo.ZoomType = DB.ZoomFitType.FitToPage
    eo.PixelSize = 1200
    project.ExportImage(eo)
    rep['exported'] = sorted(os.listdir(OUTD))
    rep['project_warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]
except Exception:
    rep['error'] = traceback.format_exc()
finally:
    rep['done'] = True
    dump_json(rep, RUN + 'work/render_hosted_off.json')
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
