# -*- coding: utf-8 -*-
"""Exploration 4: does committing the category change create a light source element? Read the LightFamily."""
import os
import json
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
import System

OUT = os.path.normpath('E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/high')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
report = {}
docs = []


def guard(path):
    p = os.path.normpath(path)
    if not p.lower().startswith(OUT.lower() + os.sep):
        raise RuntimeError('write outside run folder refused: ' + p)
    return p


def interesting(doc):
    res = []
    for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        cn = None
        try:
            cn = e.Category.Name if e.Category else None
        except Exception:
            pass
        tn = e.GetType().Name
        if tn in ('FillPatternElement', 'GraphicsStyle', 'ViewPlan', 'ViewSection'):
            continue
        res.append([str(e.Id.IntegerValue), tn, cn])
    return res


def lightinfo(doc):
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    d = {}
    for name in ['GetLightShapeStyle', 'GetLightDistributionStyle', 'GetNumberOfLightTypes']:
        try:
            d[name] = str(getattr(lf, name)())
        except Exception as ex:
            d[name] = 'ERR ' + str(ex)
    try:
        t = lf.GetLightSourceTransform()
        d['transform_origin_in'] = [t.Origin.X * 12, t.Origin.Y * 12, t.Origin.Z * 12]
        d['basisZ'] = [t.BasisZ.X, t.BasisZ.Y, t.BasisZ.Z]
    except Exception as ex:
        d['transform'] = 'ERR ' + str(ex)
    try:
        n = lf.GetNumberOfLightTypes()
        d['types'] = []
        for i in range(n):
            lt = lf.GetLightType(i)
            ti = {'name': lf.GetLightTypeName(i)}
            ti['intensity'] = str(lt.GetInitialIntensity().GetType().Name)
            try:
                ti['intensity_value'] = lt.GetInitialIntensity().InitialIntensityValue
            except Exception as ex:
                ti['intensity_value'] = 'ERR ' + str(ex)
            ti['shape'] = lt.GetLightShape().GetType().Name
            ti['dist'] = lt.GetLightDistribution().GetType().Name
            ti['color'] = lt.GetInitialColor().GetType().Name
            ti['loss'] = lt.GetLossFactor().GetType().Name
            d['types'].append(ti)
    except Exception as ex:
        d['types_err'] = traceback.format_exc()
    return d


try:
    app = __revit__.Application
    doc = app.NewFamilyDocument(TEMPLATE)
    docs.append(doc)
    report['before'] = interesting(doc)
    try:
        report['light_before'] = lightinfo(doc)
    except Exception:
        report['light_before'] = traceback.format_exc()
    tx = DB.Transaction(doc, 'cat')
    tx.Start()
    doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_LightingFixtures)
    tx.Commit()
    report['after'] = interesting(doc)
    try:
        report['light_after'] = lightinfo(doc)
    except Exception:
        report['light_after'] = traceback.format_exc()
    opts = DB.SaveAsOptions(); opts.OverwriteExistingFile = True
    tmp = guard(os.path.join(OUT, '_work', 'probe.rfa'))
    doc.SaveAs(tmp, opts)
    doc.Close(False); docs.remove(doc)
    doc = app.OpenDocumentFile(tmp); docs.append(doc)
    report['reopened_after'] = interesting(doc)
    try:
        report['light_reopened'] = lightinfo(doc)
    except Exception:
        report['light_reopened'] = traceback.format_exc()
    cat = doc.OwnerFamily.FamilyCategory
    report['subcats'] = [c.Name for c in cat.SubCategories]
    report['lightsrc_after'] = [str(e.Id.IntegerValue) for e in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource)]
    fm = doc.FamilyManager
    report['fm_params'] = [[p.Definition.Name, str(p.StorageType), p.IsInstance, p.IsReadOnly] for p in fm.Parameters]
    report['stage'] = 'done'
except Exception:
    report['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
with open(guard(os.path.join(OUT, '_work', 'explore5.json')), 'w') as f:
    json.dump(report, f, indent=1, default=str)
