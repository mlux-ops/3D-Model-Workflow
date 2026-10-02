# -*- coding: utf-8 -*-
"""Probe (pyRevit): why does the fixture render flat black in project Shading views? Tries a few view/material variants on a disposable project."""
import sys
import os
import math
import traceback
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/source')
from guard import dump_json, safe_path
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RUN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/'
RFA = RUN + 'Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa'
OUTD = RUN + 'work/probe_hosted/'
rep = {}
docs = []


def orient(view, eye, tgt):
    fwd = tgt.Subtract(eye).Normalize()
    right = fwd.CrossProduct(DB.XYZ.BasisZ).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, right.CrossProduct(fwd).Normalize(), fwd))


try:
    app = __revit__.Application
    fdoc = app.OpenDocumentFile(RFA)
    docs.append(fdoc)
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
    tx.Commit()

    vtype = next(v for v in DB.FilteredElementCollector(project).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    left = normal.CrossProduct(DB.XYZ.BasisZ)
    tgt = DB.XYZ(ptA.X, ptA.Y + 3.5 / 12.0, ptA.Z)
    eye = tgt.Add(normal.Multiply(45.2 / 12.0)).Add(left.Multiply(38.0 / 12.0)).Add(DB.XYZ.BasisZ.Multiply(10.4 / 12.0))
    vids = []

    def mkview(name, style=DB.DisplayStyle.Shading, hide_walls=False):
        tx = DB.Transaction(project, 'v ' + name)
        tx.Start()
        v = DB.View3D.CreateIsometric(project, vtype.Id)
        v.Name = name
        orient(v, eye, tgt)
        v.DisplayStyle = style
        v.DetailLevel = DB.ViewDetailLevel.Fine
        if hide_walls:
            v.SetCategoryHidden(DB.Category.GetCategory(project, DB.BuiltInCategory.OST_Walls).Id, True)
        project.Regenerate()
        v.CropBoxActive = True
        v.CropBoxVisible = False
        cb = v.CropBox
        inv2 = cb.Transform.Inverse
        xs = []
        ys = []
        for cx in (ptA.X - 6.0 / 12.0, ptA.X + 6.0 / 12.0):
            for cy in (ptA.Y - 1.0 / 12.0, ptA.Y + 7.0 / 12.0):
                for cz in (ptA.Z - 5.0 / 12.0, ptA.Z + 5.0 / 12.0):
                    q = inv2.OfPoint(DB.XYZ(cx, cy, cz))
                    xs.append(q.X)
                    ys.append(q.Y)
        cb.Min = DB.XYZ(min(xs) - 0.1, min(ys) - 0.1, cb.Min.Z)
        cb.Max = DB.XYZ(max(xs) + 0.1, max(ys) + 0.1, cb.Max.Z)
        v.CropBox = cb
        tx.Commit()
        vids.append(v.Id)
        return v

    if not os.path.isdir(OUTD):
        os.makedirs(OUTD)
    safe_path(OUTD + 'x')

    def snap(name):
        v = mkview(name)
        eo = DB.ImageExportOptions()
        eo.ExportRange = DB.ExportRange.SetOfViews
        eo.SetViewsAndSheets(List[DB.ElementId]([v.Id]))
        eo.FilePath = OUTD + 's'
        eo.HLRandWFViewsFileType = DB.ImageFileType.PNG
        eo.ShadowViewsFileType = DB.ImageFileType.PNG
        eo.ImageResolution = DB.ImageResolution.DPI_72
        eo.ZoomType = DB.ZoomFitType.FitToPage
        eo.PixelSize = 500
        project.ExportImage(eo)

    kw = [m for m in DB.FilteredElementCollector(project).OfClass(DB.Material) if m.Name.startswith('KW1041')]
    rep['kw_props'] = dict((m.Name, {'shininess': m.Shininess, 'smoothness': m.Smoothness, 'transparency': m.Transparency, 'asset': str(m.AppearanceAssetId.Value),
                                     'use_render': m.UseRenderAppearanceForShading}) for m in kw)
    snap('S0 as is')
    tx = DB.Transaction(project, 'render shading')
    tx.Start()
    for m in kw:
        m.UseRenderAppearanceForShading = True
    tx.Commit()
    snap('S1 use render appearance')
    tx = DB.Transaction(project, 'detach asset')
    tx.Start()
    for m in kw:
        m.UseRenderAppearanceForShading = False
        m.AppearanceAssetId = DB.ElementId.InvalidElementId
    tx.Commit()
    snap('S2 asset detached')
    rep['exported'] = sorted(os.listdir(OUTD))
except Exception:
    rep['error'] = traceback.format_exc()
finally:
    rep['done'] = True
    dump_json(rep, RUN + 'work/hosted_probe.json')
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
