# -*- coding: utf-8 -*-
"""pyRevit: places the saved family on a disposable wall (Show Disc = Yes) and exports photo-matched views of it:
walls hidden, fixture only, parallel projection, orientation and framing taken from the camera fit of the black product photo
(work/camera_fit_black2 numbers, entered in CAMS below). Roll is applied through the view's up vector. Nothing is saved."""
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
OUTD = RUN + 'work/export_hosted_match/'
PX = 780
# name: (az, el, roll, px_per_in, tx, ty) from source/fit_camera_black2.py; tx, ty = image position of the family origin, in photo pixels
CAMS = {
    'match C roll-free': (49.538, 6.474, -14.518, 98.758, 236.746, 414.155),
    'match D level': (55.555, -12.372, 0.0, 98.258, 224.986, 414.534),
}
rep = {}
docs = []


def cross(a, b):
    return DB.XYZ(a.Y * b.Z - a.Z * b.Y, a.Z * b.X - a.X * b.Z, a.X * b.Y - a.Y * b.X)


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
    trf = inst.GetTransform()
    org = trf.Origin
    rep['instance_transform'] = {'origin_in': [round(org.X * 12, 4), round(org.Y * 12, 4), round(org.Z * 12, 4)],
                                 'X': [trf.BasisX.X, trf.BasisX.Y, trf.BasisX.Z], 'Y': [trf.BasisY.X, trf.BasisY.Y, trf.BasisY.Z],
                                 'Z': [trf.BasisZ.X, trf.BasisZ.Y, trf.BasisZ.Z]}
    rep['show_disc_instance'] = inst.LookupParameter('Show Disc').AsInteger()
    tx.Commit()

    tx = DB.Transaction(project, 'view')
    tx.Start()
    vtype = next(v for v in DB.FilteredElementCollector(project).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    keep_ids = [DB.Category.GetCategory(project, DB.BuiltInCategory.OST_LightingFixtures).Id.Value]
    up_w = trf.BasisY
    vids = []
    rep['views'] = {}
    for vname, (az, el, roll, s, ptx, pty) in CAMS.items():
        a, e, rl = math.radians(az), math.radians(el), math.radians(roll)
        dx, dy, dz = -math.sin(a) * math.cos(e), math.sin(e), math.cos(a) * math.cos(e)
        d_w = trf.BasisX.Multiply(dx).Add(trf.BasisY.Multiply(dy)).Add(trf.BasisZ.Multiply(dz)).Normalize()
        fwd = d_w.Negate()
        right = cross(fwd, up_w).Normalize()
        upv = cross(right, fwd).Normalize()
        r2 = right.Multiply(math.cos(rl)).Add(upv.Multiply(math.sin(rl)))
        u2 = right.Multiply(-math.sin(rl)).Add(upv.Multiply(math.cos(rl)))
        eye = org.Add(d_w.Multiply(60.0 / 12.0))
        view = DB.View3D.CreateIsometric(project, vtype.Id)
        view.Name = vname
        view.SetOrientation(DB.ViewOrientation3D(eye, u2, fwd))
        view.DetailLevel = DB.ViewDetailLevel.Fine
        view.DisplayStyle = DB.DisplayStyle.Shading
        for cat in project.Settings.Categories:
            if cat.Id.Value not in keep_ids and view.CanCategoryBeHidden(cat.Id):
                view.SetCategoryHidden(cat.Id, True)
        region = DB.BoundingBoxXYZ()
        region.Min = DB.XYZ(org.X - 14.0 / 12.0, org.Y - 4.0 / 12.0, org.Z - 12.0 / 12.0)
        region.Max = DB.XYZ(org.X + 14.0 / 12.0, org.Y + 8.0 / 12.0, org.Z + 12.0 / 12.0)
        view.SetSectionBox(region)
        view.IsSectionBoxActive = True
        project.Regenerate()
        view.CropBoxActive = True
        view.CropBoxVisible = False
        cb = view.CropBox
        q0 = cb.Transform.Inverse.OfPoint(org)
        # photo pixel window [0, PX] x [0, PX]: image x = s*(P.r2) + ptx ; image y = -s*(P.u2) + pty
        cb.Min = DB.XYZ(q0.X + (0.0 - ptx) / s / 12.0, q0.Y + (-(PX - pty) / s) / 12.0, cb.Min.Z)
        cb.Max = DB.XYZ(q0.X + (PX - ptx) / s / 12.0, q0.Y + (pty / s) / 12.0, cb.Max.Z)
        view.CropBox = cb
        vids.append(view.Id)
        rep['views'][vname] = {'eye_in': [round(eye.X * 12, 3), round(eye.Y * 12, 3), round(eye.Z * 12, 3)],
                               'fwd': [round(fwd.X, 4), round(fwd.Y, 4), round(fwd.Z, 4)],
                               'up': [round(u2.X, 4), round(u2.Y, 4), round(u2.Z, 4)],
                               'crop_in': [round(cb.Min.X * 12, 3), round(cb.Min.Y * 12, 3), round(cb.Max.X * 12, 3), round(cb.Max.Y * 12, 3)]}
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
    eo.PixelSize = PX
    project.ExportImage(eo)
    rep['exported'] = sorted(os.listdir(OUTD))
    rep['project_warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]
except Exception:
    rep['error'] = traceback.format_exc()
finally:
    rep['done'] = True
    dump_json(rep, RUN + 'work/render_hosted_match.json')
    for dd in reversed(docs):
        try:
            dd.Close(False)
        except Exception:
            pass
