# -*- coding: utf-8 -*-
"""Exploration 4 (pyRevit): shape and settings of the auto-created light source; API types for lighting; settable photometrics."""
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
    dump_json(rep, RUN + 'work/explore4.json')


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


def src_of(doc):
    return DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource).FirstElement()


def bbox(e):
    bb = e.get_BoundingBox(None)
    return None if bb is None else [round(v, 5) for v in (bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z)]


def pdump(e):
    out = []
    for p in e.Parameters:
        d = {'name': p.Definition.Name, 'storage': str(p.StorageType), 'ro': p.IsReadOnly}
        try:
            d['bip'] = str(p.Definition.BuiltInParameter)
        except Exception:
            pass
        try:
            if p.StorageType == DB.StorageType.Double:
                d['value'] = p.AsDouble()
            elif p.StorageType == DB.StorageType.Integer:
                d['value'] = p.AsInteger()
            elif p.StorageType == DB.StorageType.String:
                d['value'] = p.AsString()
            d['vs'] = p.AsValueString()
        except Exception as ex:
            d['err'] = str(ex)
        out.append(d)
    return out


try:
    app = __revit__.Application
    asm = clr.GetClrType(DB.Element).Assembly
    names = []
    for t in asm.GetTypes():
        try:
            if t.IsPublic and ('Light' in t.Name or (t.Namespace and 'Lighting' in t.Namespace)):
                names.append([t.Namespace, t.Name])
        except Exception:
            pass
    rep['light_types'] = names
    save()

    a = app.NewFamilyDocument(TDIR + 'Generic Model face based.rft')
    docs.append(a)
    tx_run(a, 'cat', lambda: setattr(a.OwnerFamily, 'FamilyCategory', DB.Category.GetCategory(a, DB.BuiltInCategory.OST_LightingFixtures)))
    p = a.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE)
    tx_run(a, 'ls', lambda: p.Set(1))
    fm = a.FamilyManager
    s = src_of(a)
    rep['src_bbox_default'] = bbox(s)
    rep['src_params_default'] = pdump(s)
    rep['src_class'] = s.GetType().FullName
    rep['src_methods'] = [n for n in dir(s) if not n.startswith('_')][:200]
    try:
        geo = s.get_Geometry(DB.Options())
        gl = []
        if geo is not None:
            for g in geo:
                gl.append(g.GetType().Name)
        rep['src_geometry'] = gl
    except Exception:
        rep['src_geometry_err'] = traceback.format_exc()[-300:]
    save()

    # type + settable FM params
    tx_run(a, 'type', lambda: setattr(fm, 'CurrentType', fm.NewType('T')))
    rep['fm_params'] = []
    for q in fm.Parameters:
        rep['fm_params'].append([q.Definition.Name, str(q.StorageType), q.IsInstance, q.IsReadOnly])
    def find(nm):
        for q in fm.Parameters:
            if q.Definition.Name == nm:
                return q
        return None
    tests = {}
    rep['set_tests'] = tests
    for nm, val in (('Emit from Line Length', 0.0), ('Emit from Line Length', 0.01), ('Light Source Symbol Size', 0.05),
                    ('Apparent Power', 3.0), ('Wattage Comments', '3 W LED'), ('Lamp', 'JCD G9 3W LED 120V'),
                    ('Initial Intensity', 100.0), ('Initial Intensity', 100), ('Light Loss Factor', 1.0), ('Initial Color', 3000)):
        fp = find(nm)
        key = nm + ' = ' + str(val)
        if fp is None:
            tests[key] = 'missing'
            continue
        try:
            tx_run(a, 'set ' + nm, lambda: fm.Set(fp, val))
            tests[key] = 'ok'
        except Exception:
            tests[key] = 'ERR ' + traceback.format_exc().strip().split('\n')[-1][:200]
    s = src_of(a)
    rep['src_bbox_after_sets'] = bbox(s)
    rep['src_params_after'] = pdump(s)
    # direct element params on the source
    d2 = {}
    rep['src_direct'] = d2
    for bn in ('FBX_LIGHT_INITIAL_INTENSITY', 'FBX_LIGHT_WATTAGE', 'FBX_LIGHT_LIMUNOUS_FLUX', 'FBX_LIGHT_INITIAL_COLOR_TEMPERATURE',
               'FBX_LIGHT_EMIT_LINE_LENGTH', 'FBX_LIGHT_SOURCE_LENGTH', 'FBX_LIGHT_EMIT_SHAPE_VISIBLE', 'FBX_LIGHT_PHOTOMETRICS',
               'FBX_LIGHT_INITIAL_INTENSITY_INPUT_METHOD', 'FBX_LIGHT_LOSS_FACTOR_METHOD', 'FBX_LIGHT_ILLUMINANCE'):
        try:
            q = s.get_Parameter(getattr(DB.BuiltInParameter, bn))
            d2[bn] = None if q is None else {'storage': str(q.StorageType), 'ro': q.IsReadOnly}
        except Exception:
            d2[bn] = 'ERR'
    # family-level params (owner family) now
    rep['fam_params_now'] = pdump(a.OwnerFamily)
    # move the source and record
    try:
        tx_run(a, 'mv', lambda: DB.ElementTransformUtils.MoveElement(a, s.Id, DB.XYZ(0.1, 0.2, 0.3)))
        rep['src_bbox_after_move'] = bbox(src_of(a))
    except Exception:
        rep['move_err'] = traceback.format_exc()[-300:]
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
