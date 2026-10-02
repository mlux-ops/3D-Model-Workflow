# -*- coding: utf-8 -*-
"""Exploration 3 (pyRevit): can a face-based Lighting Fixtures family get a light source (FBX_ASSET_TYPE), and how is it set up?"""
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
    dump_json(rep, RUN + 'work/explore3.json')


def sources(doc):
    out = []
    for e in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource):
        bb = e.get_BoundingBox(None)
        out.append({'id': str(e.Id.Value), 'class': e.GetType().Name,
                    'bbox': [bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z] if bb else None})
    return out


def fmparams(doc):
    res = []
    for p in doc.FamilyManager.Parameters:
        d = {'name': p.Definition.Name, 'inst': p.IsInstance, 'storage': str(p.StorageType)}
        try:
            d['bip'] = str(p.Definition.BuiltInParameter)
        except Exception:
            pass
        try:
            d['dtype'] = str(p.Definition.GetDataType().TypeId)
        except Exception:
            pass
        res.append(d)
    return res


def tx_run(doc, name, fn):
    t = DB.Transaction(doc, name)
    t.Start()
    try:
        r = fn()
        t.Commit()
        return r
    except Exception:
        t.RollBack()
        raise


try:
    app = __revit__.Application

    # --- A: generic face-based -> Lighting Fixtures, set FBX_ASSET_TYPE = 1
    A = {}
    rep['A'] = A
    try:
        a = app.NewFamilyDocument(TDIR + 'Generic Model face based.rft')
        docs.append(a)
        tx_run(a, 'cat', lambda: setattr(a.OwnerFamily, 'FamilyCategory', DB.Category.GetCategory(a, DB.BuiltInCategory.OST_LightingFixtures)))
        A['placement'] = str(a.OwnerFamily.FamilyPlacementType)
        A['fm_before'] = [x['name'] for x in fmparams(a)]
        p = a.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE)
        A['asset_param'] = None if p is None else {'ro': p.IsReadOnly, 'value': p.AsInteger(), 'vs': p.AsValueString()}
        if p is not None:
            def setit():
                return p.Set(1)
            A['set_result'] = str(tx_run(a, 'setls', setit))
            A['asset_after'] = p.AsInteger()
        A['sources_after'] = sources(a)
        A['fm_after'] = fmparams(a)
        A['placement_after'] = str(a.OwnerFamily.FamilyPlacementType)
        A['factory_light_methods'] = [n for n in dir(a.FamilyCreate) if 'ight' in n]
        A['doc_light_methods'] = [n for n in dir(a) if 'ight' in n]
    except Exception:
        A['error'] = traceback.format_exc()
    save()

    # --- C: Lighting Fixture.rft -> Work Plane-Based
    C = {}
    rep['C'] = C
    try:
        c = app.NewFamilyDocument(TDIR + 'Lighting Fixture.rft')
        docs.append(c)
        C['placement_before'] = str(c.OwnerFamily.FamilyPlacementType)
        wp = c.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED)
        av = c.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)

        def setwp():
            r1 = wp.Set(1)
            r2 = av.Set(0)
            return [r1, r2]
        C['set'] = str(tx_run(c, 'wp', setwp))
        C['placement_after'] = str(c.OwnerFamily.FamilyPlacementType)
        C['sources'] = sources(c)
        C['fm'] = fmparams(c)
        C['ref_planes'] = [[rp.Name, [rp.Normal.X, rp.Normal.Y, rp.Normal.Z], [rp.BubbleEnd.X, rp.BubbleEnd.Y, rp.BubbleEnd.Z]]
                           for rp in DB.FilteredElementCollector(c).OfClass(DB.ReferencePlane)]
        # move the source
        src = DB.FilteredElementCollector(c).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource).FirstElement()
        C['src_can_move_test'] = {}
        try:
            def mv():
                DB.ElementTransformUtils.MoveElement(c, src.Id, DB.XYZ(0.0, 0.0, 1.0))
            tx_run(c, 'mv', mv)
            C['src_can_move_test']['after'] = sources(c)
        except Exception:
            C['src_can_move_test']['error'] = traceback.format_exc()
        # read/set the special light params through FamilyManager
        fm = c.FamilyManager
        C['light_params'] = {}
        for nm in ('Initial Intensity', 'Initial Color', 'Light Loss Factor', 'Color Filter', 'Dimming Lamp Color Temperature Shift'):
            fp = None
            for q in fm.Parameters:
                if q.Definition.Name == nm:
                    fp = q
            e = {'found': fp is not None}
            if fp is not None:
                try:
                    e['vs'] = fm.CurrentType.AsValueString(fp) if fm.CurrentType else 'no current type'
                except Exception:
                    e['vs_err'] = traceback.format_exc()[-300:]
                try:
                    e['double'] = fm.CurrentType.AsDouble(fp)
                except Exception:
                    e['double_err'] = traceback.format_exc()[-200:]
                try:
                    e['int'] = fm.CurrentType.AsInteger(fp)
                except Exception:
                    e['int_err'] = traceback.format_exc()[-200:]
                e['inst'] = fp.IsInstance
            C['light_params'][nm] = e
        # builtin lookups on the family manager
        for bn in ('FBX_LIGHT_INITIAL_INTENSITY', 'FBX_LIGHT_WATTAGE', 'FBX_LIGHT_LIMUNOUS_FLUX', 'FBX_LIGHT_INITIAL_COLOR_TEMPERATURE', 'FBX_LIGHT_LIMUNOUS_INTENSITY'):
            try:
                fp = fm.get_Parameter(getattr(DB.BuiltInParameter, bn))
                C['light_params'][bn] = None if fp is None else fp.Definition.Name
            except Exception:
                C['light_params'][bn] = 'err ' + traceback.format_exc()[-160:]
    except Exception:
        C['error'] = traceback.format_exc()
    save()
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
