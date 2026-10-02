# -*- coding: utf-8 -*-
"""Exploration 2 (pyRevit): light-source element in the lighting templates; can it be copied into a face-based family?"""
import sys
import json
import traceback
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/source')
from guard import safe_open, dump_json
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RUN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/'
TDIR = 'C:\\ProgramData\\Autodesk\\RVT 2025\\Family Templates\\English-Imperial\\'
GEN = TDIR + 'Generic Model face based.rft'
rep = {}
docs = []


def save():
    dump_json(rep, RUN + 'work/explore2.json')


def pinfo(p):
    d = {'name': p.Definition.Name, 'storage': str(p.StorageType), 'ro': p.IsReadOnly}
    try:
        if p.StorageType == DB.StorageType.Double:
            d['value'] = p.AsDouble()
        elif p.StorageType == DB.StorageType.Integer:
            d['value'] = p.AsInteger()
        elif p.StorageType == DB.StorageType.String:
            d['value'] = p.AsString()
        elif p.StorageType == DB.StorageType.ElementId:
            d['value'] = str(p.AsElementId().Value)
        d['vs'] = p.AsValueString()
    except Exception as e:
        d['err'] = str(e)
    try:
        d['bip'] = str(p.Definition.BuiltInParameter)
    except Exception:
        pass
    return d


def describe_sources(doc):
    out = []
    for e in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource):
        ent = {'class': e.GetType().Name, 'id': str(e.Id.Value), 'name': e.Name}
        try:
            bb = e.get_BoundingBox(None)
            if bb:
                ent['bbox'] = [bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z]
        except Exception as ex:
            ent['bbox_err'] = str(ex)
        loc = e.Location
        ent['loc'] = type(loc).__name__ if loc is not None else None
        try:
            if isinstance(loc, DB.LocationPoint):
                ent['pt'] = [loc.Point.X, loc.Point.Y, loc.Point.Z]
        except Exception:
            pass
        ent['params'] = [pinfo(p) for p in e.Parameters]
        try:
            ent['host'] = str(e.Host.Id.Value) if e.Host else None
        except Exception:
            pass
        out.append(ent)
    return out


try:
    app = __revit__.Application
    for nm in ('Lighting Fixture wall based', 'Spot Lighting Fixture wall based', 'Lighting Fixture', 'Lighting Fixture ceiling based'):
        try:
            d = app.NewFamilyDocument(TDIR + nm + '.rft')
            docs.append(d)
            rep[nm] = {'category': d.OwnerFamily.FamilyCategory.Name, 'placement': str(d.OwnerFamily.FamilyPlacementType),
                       'sources': describe_sources(d)}
            rep[nm]['family_params'] = [pinfo(p) for p in d.OwnerFamily.Parameters]
            rep[nm]['fm_params'] = [[p.Definition.Name, str(p.StorageType)] for p in d.FamilyManager.Parameters]
        except Exception:
            rep[nm] = {'error': traceback.format_exc()}
        save()

    # copy the light source into a face-based generic family after category change
    dst = app.NewFamilyDocument(GEN)
    docs.append(dst)
    t = DB.Transaction(dst, 'cat')
    t.Start()
    dst.OwnerFamily.FamilyCategory = DB.Category.GetCategory(dst, DB.BuiltInCategory.OST_LightingFixtures)
    t.Commit()
    rep['dst_sources_before'] = describe_sources(dst)
    for nm in ('Lighting Fixture wall based', 'Spot Lighting Fixture wall based', 'Lighting Fixture'):
        srcdoc = None
        for d in docs:
            try:
                if d.Title and nm == d.Title.replace('.rfa', '') or (d.OwnerFamily and d.OwnerFamily.Name == nm):
                    srcdoc = d
            except Exception:
                pass
        # match by order instead
    order = ['Lighting Fixture wall based', 'Spot Lighting Fixture wall based', 'Lighting Fixture', 'Lighting Fixture ceiling based']
    for i, nm in enumerate(order):
        rep['copy_' + nm] = {}
        try:
            srcdoc = docs[i]
            ids = List[DB.ElementId]()
            for e in DB.FilteredElementCollector(srcdoc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource):
                ids.Add(e.Id)
            rep['copy_' + nm]['n_ids'] = ids.Count
            if ids.Count == 0:
                continue
            t = DB.Transaction(dst, 'copy ' + nm)
            t.Start()
            try:
                new_ids = DB.ElementTransformUtils.CopyElements(srcdoc, ids, dst, DB.Transform.Identity, DB.CopyPasteOptions())
                rep['copy_' + nm]['new_ids'] = [str(x.Value) for x in new_ids]
                t.Commit()
            except Exception:
                rep['copy_' + nm]['copy_error'] = traceback.format_exc()
                t.RollBack()
            rep['copy_' + nm]['dst_sources_after'] = describe_sources(dst)
        except Exception:
            rep['copy_' + nm]['error'] = traceback.format_exc()
        save()
        if rep['copy_' + nm].get('new_ids'):
            break
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
