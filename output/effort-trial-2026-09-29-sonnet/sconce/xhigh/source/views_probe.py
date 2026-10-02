# -*- coding: utf-8 -*-
"""Probe (pyRevit): export candidate oblique views of the saved RFA to pick the angle that matches the black product photo."""
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
OUTD = RUN + 'work/probe/'
rep = {}
docs = []


def xf(t):
    return DB.XYZ(t[0] / 12.0, t[1] / 12.0, t[2] / 12.0)


try:
    app = __revit__.Application
    doc = app.OpenDocumentFile(RUN + 'Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa')
    docs.append(doc)
    if not os.path.isdir(OUTD):
        os.makedirs(OUTD)
    safe_path(OUTD + 'x')
    tx = DB.Transaction(doc, 'probe views')
    tx.Start()
    vtype = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    tgt = (0.0, -0.6, 3.0)
    views = []
    for az in (25, 40, 55):
        for el in (10, 25):
            a = math.radians(az)
            e = math.radians(el)
            d = (-math.sin(a) * math.cos(e), math.sin(e), math.cos(a) * math.cos(e))
            eye = (tgt[0] + 60 * d[0], tgt[1] + 60 * d[1], tgt[2] + 60 * d[2])
            view = DB.View3D.CreateIsometric(doc, vtype.Id)
            view.Name = 'az%d_el%d' % (az, el)
            eyep = xf(eye)
            fwd = xf(tgt).Subtract(eyep).Normalize()
            right = fwd.CrossProduct(DB.XYZ.BasisY).Normalize()
            view.SetOrientation(DB.ViewOrientation3D(eyep, right.CrossProduct(fwd).Normalize(), fwd))
            view.DetailLevel = DB.ViewDetailLevel.Fine
            view.DisplayStyle = DB.DisplayStyle.Shading
            for cat in doc.Settings.Categories:
                if cat.Id != doc.OwnerFamily.FamilyCategory.Id and view.CanCategoryBeHidden(cat.Id):
                    view.SetCategoryHidden(cat.Id, True)
            region = DB.BoundingBoxXYZ()
            region.Min = xf((-6.0, -6.0, -0.2))
            region.Max = xf((6.0, 6.0, 7.5))
            view.SetSectionBox(region)
            view.IsSectionBoxActive = True
            doc.Regenerate()
            view.CropBoxActive = True
            view.CropBoxVisible = False
            cb = view.CropBox
            inv = cb.Transform.Inverse
            xs = []
            ys = []
            for cx in (-4.0, 4.0):
                for cy in (-3.9, 3.9):
                    for cz in (0.0, 5.5):
                        q = inv.OfPoint(xf((cx, cy, cz)))
                        xs.append(q.X)
                        ys.append(q.Y)
            pad = 0.6 / 12.0
            cb.Min = DB.XYZ(min(xs) - pad, min(ys) - pad, cb.Min.Z)
            cb.Max = DB.XYZ(max(xs) + pad, max(ys) + pad, cb.Max.Z)
            view.CropBox = cb
            views.append(view)
    tx.Commit()
    opts = DB.ImageExportOptions()
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]))
    opts.FilePath = OUTD + 'p'
    opts.HLRandWFViewsFileType = DB.ImageFileType.PNG
    opts.ShadowViewsFileType = DB.ImageFileType.PNG
    opts.ImageResolution = DB.ImageResolution.DPI_150
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = 700
    doc.ExportImage(opts)
    rep['exported'] = sorted(os.listdir(OUTD))
except Exception:
    rep['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
    rep['done'] = True
    dump_json(rep, RUN + 'work/views_probe.json')
