# -*- coding: utf-8 -*-
"""Exploration: which source rotation / Tilt Angle makes the Line + Spot cone point +Z?
The saved RFA (source rotated 180 deg about X, tilt 0) showed its cone along -X in the live Front elevation.
Opens the saved RFA, applies candidate rotations and tilts inside rolled-back transactions, and reports the offset of the source geometry
centroid from the source origin (the cone extends away from its apex). Run only through _harness/revit_run.py. Writes explore_aim.json."""
import sys
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/wieland_strip_grazer/source')
from common import *

R = {'variants': []}
docs = []


def geom_probe(doc, eid):
    el = doc.GetElement(eid)
    opt = DB.Options()
    opt.DetailLevel = DB.ViewDetailLevel.Fine
    opt.IncludeNonVisibleObjects = True
    opt.ComputeReferences = False
    pts = []
    kinds = {}

    items = []

    def walk(g):
        for item in g:
            before = len(pts)
            kinds[item.GetType().Name] = kinds.get(item.GetType().Name, 0) + 1
            if isinstance(item, DB.GeometryInstance):
                walk(item.GetInstanceGeometry())
            elif isinstance(item, DB.Solid):
                for f in item.Faces:
                    m = f.Triangulate(1.0)
                    if m is not None:
                        pts.extend(list(m.Vertices))
            elif isinstance(item, DB.Curve):
                pts.extend([item.GetEndPoint(0), item.GetEndPoint(1)])
                try:
                    pts.extend(list(item.Tessellate()))
                except Exception:
                    pass
            elif isinstance(item, DB.Mesh):
                pts.extend(list(item.Vertices))
            if not isinstance(item, DB.GeometryInstance) and len(pts) > before:
                sub = pts[before:]
                items.append({'type': item.GetType().Name, 'n': len(sub), 'style': item.GraphicsStyleId.IntegerValue,
                              'x': [round(min(p.X for p in sub) * IN, 2), round(max(p.X for p in sub) * IN, 2)],
                              'y': [round(min(p.Y for p in sub) * IN, 2), round(max(p.Y for p in sub) * IN, 2)],
                              'z': [round(min(p.Z for p in sub) * IN, 2), round(max(p.Z for p in sub) * IN, 2)]})
    g = el.get_Geometry(opt)
    if g is not None:
        walk(g)
    kinds['items'] = items
    return pts, kinds


def describe(doc, eid, label):
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    t = lf.GetLightSourceTransform()
    pts, kinds = geom_probe(doc, eid)
    d = {'label': label, 'kinds': kinds, 'n_pts': len(pts),
         'basisX': [round(t.BasisX.X, 3), round(t.BasisX.Y, 3), round(t.BasisX.Z, 3)],
         'basisY': [round(t.BasisY.X, 3), round(t.BasisY.Y, 3), round(t.BasisY.Z, 3)],
         'basisZ': [round(t.BasisZ.X, 3), round(t.BasisZ.Y, 3), round(t.BasisZ.Z, 3)],
         'origin_in': [round(t.Origin.X * IN, 3), round(t.Origin.Y * IN, 3), round(t.Origin.Z * IN, 3)]}
    if pts:
        xs = [p.X * IN for p in pts]
        ys = [p.Y * IN for p in pts]
        zs = [p.Z * IN for p in pts]
        d['bbox_in'] = {'x': [round(min(xs), 2), round(max(xs), 2)], 'y': [round(min(ys), 2), round(max(ys), 2)], 'z': [round(min(zs), 2), round(max(zs), 2)]}
        n = float(len(pts))
        d['centroid_offset_from_origin_in'] = [round(sum(xs) / n - t.Origin.X * IN, 2), round(sum(ys) / n - t.Origin.Y * IN, 2), round(sum(zs) / n - t.Origin.Z * IN, 2)]
    return d


def find_param(fm, name):
    for p in fm.Parameters:
        if p.Definition.Name == name:
            return p


try:
    app = __revit__.Application
    doc = app.OpenDocumentFile(RFA)
    docs.append(doc)
    eid = [e.Id for e in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource)][0]
    R['baseline_saved'] = describe(doc, eid, 'saved: rot X 180, tilt 0')
    fm = doc.FamilyManager
    tilt = find_param(fm, 'Tilt Angle')
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    o = lf.GetLightSourceTransform().Origin
    axes = {'X': DB.XYZ.BasisX, 'Y': DB.XYZ.BasisY, 'Z': DB.XYZ.BasisZ}
    # (extra rotation applied on top of the saved state, axis, degrees, tilt degrees)
    cases = [('none', None, 0, 90), ('none', None, 0, 0)]
    for name, ax, deg, tl in cases:
        tx = DB.Transaction(doc, 'probe')
        tx.Start()
        try:
            if ax:
                DB.ElementTransformUtils.RotateElement(doc, eid, DB.Line.CreateBound(o, o.Add(axes[ax])), math.radians(deg))
            if tl:
                fm.Set(tilt, math.radians(tl))
            doc.Regenerate()
            R['variants'].append(describe(doc, eid, 'extra rot %s %s deg, tilt %s deg' % (name, deg, tl)))
        except Exception:
            R['variants'].append({'label': 'extra rot %s %s tilt %s' % (name, deg, tl), 'error': traceback.format_exc()})
        tx.RollBack()
    R['ok'] = True
except Exception:
    R['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
    write_json('explore_aim3.json', R)
