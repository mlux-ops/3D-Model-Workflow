# -*- coding: utf-8 -*-
"""Probe: how does a family document get a light source through the Revit 2025 API?
Runs through the serialized runner. Writes _work/probe_light2.json after every experiment."""
import sys
import json
import traceback

RUN = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max"
if RUN + "/source" not in sys.path:
    sys.path.insert(0, RUN + "/source")
from common import *

OUT = RUN + "/_work/probe_light2.json"
TDIR = "C:/ProgramData/Autodesk/RVT 2025/Family Templates/English-Imperial/"
app = __revit__.Application
R = {'revit': app.VersionName + ' ' + app.VersionBuild, 'experiments': {}}
DOCS = []


def save():
    with open(safe(OUT), 'w') as f:
        json.dump(R, f, indent=1, default=str)


def exp(name, fn, *a):
    try:
        R['experiments'][name] = fn(*a)
    except Exception:
        R['experiments'][name] = {'error': traceback.format_exc()}
    save()


def ename(e):
    try:
        return DB.Element.Name.GetValue(e)
    except Exception:
        return None


def fam_params(doc):
    out = {}
    for p in doc.OwnerFamily.Parameters:
        try:
            out[p.Definition.Name] = pval(p)
        except Exception as ex:
            out[p.Definition.Name] = 'error ' + str(ex)
    return out


def light_elements(doc):
    found = []
    try:
        col = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource).WhereElementIsNotElementType()
        for e in col:
            item = {'id': str(e.Id.Value), 'class': e.GetType().Name, 'category': e.Category.Name if e.Category else None}
            try:
                loc = e.Location
                item['location'] = loc.GetType().Name if loc is not None else None
                if loc is not None and hasattr(loc, 'Point'):
                    item['point_in'] = rnd(to_in(loc.Point))
            except Exception as ex:
                item['location_error'] = str(ex)
            try:
                bb = e.get_BoundingBox(None)
                if bb is not None:
                    item['bbox_in'] = [rnd(to_in(bb.Min)), rnd(to_in(bb.Max))]
            except Exception as ex:
                item['bbox_error'] = str(ex)
            try:
                item['parameters'] = [p.Definition.Name for p in e.Parameters]
            except Exception as ex:
                item['parameters_error'] = str(ex)
            found.append(item)
    except Exception:
        found.append({'error': traceback.format_exc()})
    return found


def scan_light_named(doc):
    hits = []
    for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        try:
            cn = e.Category.Name if e.Category else ''
            tn = e.GetType().Name
            if 'light' in cn.lower() or 'light' in tn.lower() or 'source' in cn.lower():
                hits.append({'id': str(e.Id.Value), 'class': tn, 'cat': cn})
        except Exception:
            pass
    return hits


def ref_planes(doc):
    out = []
    for e in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane):
        try:
            out.append({'name': e.Name, 'bubble_in': rnd(to_in(e.BubbleEnd)), 'free_in': rnd(to_in(e.FreeEnd)),
                        'normal': rnd((e.Normal.X, e.Normal.Y, e.Normal.Z))})
        except Exception as ex:
            out.append({'error': str(ex)})
    return out


def state(doc, with_planes=False):
    fam = doc.OwnerFamily
    s = {'title': doc.Title, 'category': fam.FamilyCategory.Name, 'placement_type': str(fam.FamilyPlacementType),
         'light_elements': light_elements(doc), 'light_named_scan': scan_light_named(doc), 'light_read': read_light(doc)}
    if with_planes:
        s['ref_planes'] = ref_planes(doc)
    return s


def new_doc(template):
    d = app.NewFamilyDocument(TDIR + template)
    DOCS.append(d)
    return d


def exp_templates():
    out = {}
    for t in ['Lighting Fixture.rft', 'Lighting Fixture wall based.rft', 'Lighting Fixture ceiling based.rft',
              'Generic Model face based.rft']:
        try:
            d = new_doc(t)
            item = state(d, with_planes=True)
            item['family_params'] = fam_params(d)
            out[t] = item
        except Exception:
            out[t] = {'error': traceback.format_exc()}
    return out


def exp_lf_workplane():
    d = new_doc('Lighting Fixture.rft')
    out = {'before': {'placement': str(d.OwnerFamily.FamilyPlacementType), 'params': fam_params(d)}}
    p = d.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED)
    out['work_plane_param_found'] = p is not None
    if p is not None:
        out['work_plane_param_readonly'] = p.IsReadOnly
        with Tx(d, 'work plane based'):
            p.Set(1)
            d.Regenerate()
        out['after_set'] = {'placement': str(d.OwnerFamily.FamilyPlacementType), 'value': pval(d.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED))}
    out['after_state'] = state(d, with_planes=True)
    return out


def exp_lf_move():
    d = new_doc('Lighting Fixture.rft')
    out = {'before': read_light(d), 'elements_before': light_elements(d)}
    els = DB.FilteredElementCollector(d).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource).WhereElementIsNotElementType().ToElements()
    if len(els) == 0:
        out['note'] = 'no light source element in Lighting Fixture.rft'
        return out
    el = els[0]
    vec = DB.XYZ(0.10, 0.20, 0.30)
    try:
        with Tx(d, 'move light'):
            DB.ElementTransformUtils.MoveElement(d, el.Id, vec)
            d.Regenerate()
        out['move_element'] = 'ok'
    except Exception:
        out['move_element'] = traceback.format_exc()
    out['after_move_element'] = read_light(d)
    out['elements_after_move'] = light_elements(d)
    try:
        with Tx(d, 'move light via location'):
            el.Location.Move(DB.XYZ(0.0, 0.0, 0.05))
            d.Regenerate()
        out['location_move'] = 'ok'
    except Exception:
        out['location_move'] = traceback.format_exc()
    out['after_location_move'] = read_light(d)
    return out


def exp_gfb_category_copy():
    out = {}
    src = new_doc('Lighting Fixture.rft')
    dst = new_doc('Generic Model face based.rft')
    cat = dst.Settings.Categories.get_Item(DB.BuiltInCategory.OST_LightingFixtures)
    with Tx(dst, 'category'):
        dst.OwnerFamily.FamilyCategory = cat
        dst.Regenerate()
    out['after_category'] = state(dst)
    ids = DB.FilteredElementCollector(src).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource).WhereElementIsNotElementType().ToElementIds()
    out['source_light_ids'] = [str(i.Value) for i in ids]
    if len(ids) > 0:
        try:
            with Tx(dst, 'copy light'):
                copied = DB.ElementTransformUtils.CopyElements(src, ids, dst, DB.Transform.Identity, DB.CopyPasteOptions())
                dst.Regenerate()
            out['copied_ids'] = [str(i.Value) for i in copied]
        except Exception:
            out['copy_error'] = traceback.format_exc()
        out['after_copy'] = state(dst)
    tmp = RUN + "/_work/probe_gfb.rfa"
    try:
        so = DB.SaveAsOptions()
        so.OverwriteExistingFile = True
        dst.SaveAs(os.path.normpath(safe(tmp)), so)
        out['saved'] = True
    except Exception:
        out['save_error'] = traceback.format_exc()
    return out


def exp_reopen_probe():
    tmp = RUN + "/_work/probe_gfb.rfa"
    if not os.path.exists(tmp):
        return {'note': 'no saved probe file'}
    d = app.OpenDocumentFile(os.path.normpath(tmp))
    DOCS.append(d)
    return state(d)


try:
    exp('templates', exp_templates)
    exp('lf_workplane', exp_lf_workplane)
    exp('lf_move', exp_lf_move)
    exp('gfb_category_copy', exp_gfb_category_copy)
finally:
    for d in list(DOCS):
        if d.Title.lower().startswith('probe_gfb'):
            try:
                d.Close(False)
            except Exception:
                pass
    DOCS[:] = [d for d in DOCS if d.IsValidObject and not d.Title.lower().startswith('probe_gfb')]
    try:
        exp('reopen_probe', exp_reopen_probe)
    finally:
        for d in DOCS:
            try:
                if d.IsValidObject:
                    d.Close(False)
            except Exception:
                pass
        R['closed_all'] = True
        save()
