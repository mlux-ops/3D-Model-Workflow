# -*- coding: utf-8 -*-
"""Exploration 7 (pyRevit): how the light source position is exposed (bbox, GetLightSourceTransform) under Point/Circle/Line shapes, before and after a move."""
import sys
import traceback
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/source')
from guard import dump_json
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

RUN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/'
TDIR = 'C:\\ProgramData\\Autodesk\\RVT 2025\\Family Templates\\English-Imperial\\'
rep = {}
docs = []


def save():
    dump_json(rep, RUN + 'work/explore7.json')


def snap(doc, lf, tag):
    src = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource).FirstElement()
    e = {'src_found': src is not None}
    if src is not None:
        bb = src.get_BoundingBox(None)
        e['bbox_in'] = [round(c * 12, 4) for c in (bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z)] if bb else None
        e['id'] = str(src.Id.Value)
    try:
        t = lf.GetLightSourceTransform()
        e['lst_origin_in'] = [round(t.Origin.X * 12, 4), round(t.Origin.Y * 12, 4), round(t.Origin.Z * 12, 4)]
        e['lst_basis'] = [[t.BasisX.X, t.BasisX.Y, t.BasisX.Z], [t.BasisY.X, t.BasisY.Y, t.BasisY.Z], [t.BasisZ.X, t.BasisZ.Y, t.BasisZ.Z]]
    except Exception:
        e['lst_err'] = traceback.format_exc().strip().split('\n')[-1][:200]
    rep[tag] = e
    save()


try:
    app = __revit__.Application
    doc = app.NewFamilyDocument(TDIR + 'Generic Model face based.rft')
    docs.append(doc)
    tx = DB.Transaction(doc, 'a')
    tx.Start()
    doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_LightingFixtures)
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE).Set(1)
    fm = doc.FamilyManager
    fm.NewType('T1')
    tx.Commit()
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    snap(doc, lf, 'default_line')

    tx = DB.Transaction(doc, 'point')
    tx.Start()
    lf.SetLightShapeStyle(DB.Lighting.LightShapeStyle.Point)
    lt = lf.GetLightType(0)
    lt.SetLightShape(DB.Lighting.PointLightShape())
    tx.Commit()
    snap(doc, lf, 'point_after_commit')
    tx = DB.Transaction(doc, 'regen')
    tx.Start()
    doc.Regenerate()
    tx.Commit()
    snap(doc, lf, 'point_after_regen')

    tx = DB.Transaction(doc, 'sizes')
    tx.Start()
    for q in fm.Parameters:
        if q.Definition.Name == 'Light Source Symbol Size':
            fm.Set(q, 0.05)
    tx.Commit()
    snap(doc, lf, 'point_symbol_size_0.05')

    tx = DB.Transaction(doc, 'move')
    tx.Start()
    src = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource).FirstElement()
    DB.ElementTransformUtils.MoveElement(doc, src.Id, DB.XYZ(0.0, -0.05, 0.3))
    tx.Commit()
    snap(doc, lf, 'point_after_move')

    tx = DB.Transaction(doc, 'circle')
    tx.Start()
    lf.SetLightShapeStyle(DB.Lighting.LightShapeStyle.Circle)
    lt = lf.GetLightType(0)
    lt.SetLightShape(DB.Lighting.CircleLightShape(0.01))
    tx.Commit()
    snap(doc, lf, 'circle_0.01_after_move')

    tx = DB.Transaction(doc, 'line')
    tx.Start()
    lf.SetLightShapeStyle(DB.Lighting.LightShapeStyle.Line)
    lt = lf.GetLightType(0)
    lt.SetLightShape(DB.Lighting.LineLightShape(0.01))
    tx.Commit()
    snap(doc, lf, 'line_0.01_after_move')
except Exception:
    rep['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
    rep['done'] = True
    save()
