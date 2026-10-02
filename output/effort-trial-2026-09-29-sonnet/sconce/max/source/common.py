# -*- coding: utf-8 -*-
"""Shared constants and helpers for the KW1041MBK build and validation scripts (pyRevit IronPython 2.7).

Family frame: X across the host face, Y up the host face, Z projecting out of the host face.
All lengths in this file are inches; Revit API calls convert to feet at the boundary (V, to_in).
"""
import sys
import os
import json
import math
import traceback

RUN = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max"
if RUN + "/source" not in sys.path:
    sys.path.insert(0, RUN + "/source")
from guard import safe

import clr
clr.AddReference('RevitAPI')
import System
from Autodesk.Revit import DB
from System.Collections.Generic import List

try:
    LT = DB.Lighting
except Exception:
    LT = None

RFA = RUN + "/Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa"
VIEWS = RUN + "/views"
TEMPLATE = "C:/ProgramData/Autodesk/RVT 2025/Family Templates/English-Imperial/Generic Model face based.rft"
TYPE_NAME = "KW1041MBK - Midnight Black / Milk"

# ---- geometry (inches) -------------------------------------------------------------------------------
TH = math.radians(17.78)         # disc tilt from the wall plane, top edge out; solves 8 cos(TH) + DISC_T sin(TH) = 7.63 (published height)
S, C = math.sin(TH), math.cos(TH)
N = (0.0, -S, C)                 # socket / shade / disc axis, unit, pointing out and slightly downward
UPV = (0.0, C, S)                # in-plane "up" of the tilted disc
XV = (1.0, 0.0, 0.0)
YV = (0.0, 1.0, 0.0)
ZV = (0.0, 0.0, 1.0)

BP_R, BP_T = 2.625, 0.125        # backplate 5.25 dia x 0.125 (published)
BODY_R = 2.155                   # body 4.31 dia (measured on the side reference)
DISC_R, DISC_T = 4.00, 0.04      # disc 8.00 dia (published width); rim band in the hero photo reads ~0.03 in, 0.04 stays above Revit's short-curve tolerance
COLLAR_R = 0.79                  # socket collar 1.58 dia (inferred from the photos)
SH_R, SH_WALL = 1.75, 0.10       # shade 3.5 dia (published); glass wall inferred
NECK_BELOW = 1.50                # neck plane below the sphere centre, giving the published 3.25 in shade height
GLOBE_AX = 1.72                  # sphere centre along the axis from the cut-face centre (measured)
YG = -0.442                      # sphere centre height relative to the backplate centre (measured)
DEPTH = 5.50                     # published projection
ZG = DEPTH - SH_R
CF = (0.0, YG + GLOBE_AX * S, ZG - GLOBE_AX * C)   # centre of the oblique cut face and of the disc back face
NECK_A = GLOBE_AX - NECK_BELOW                      # neck plane along the axis from CF
LIGHT_A = 1.40                                      # light source along the axis from CF (G9 capsule centre estimate)
LIGHT_POS = (CF[0] + N[0] * LIGHT_A, CF[1] + N[1] * LIGHT_A, CF[2] + N[2] * LIGHT_A)
SPHERE_C = (CF[0] + N[0] * GLOBE_AX, CF[1] + N[1] * GLOBE_AX, CF[2] + N[2] * GLOBE_AX)

PART_NAMES = ['Backplate', 'Body', 'Socket', 'Disc', 'Shade']

FAILURES = []


def ename(e):
    """Element name. ElementType.Name raises AttributeError in the pyRevit netcore IronPython engine."""
    try:
        return DB.Element.Name.GetValue(e)
    except Exception:
        return None


def close_doc(doc, log, label):
    """Close a document without saving and record the outcome (a silent close failure can leave Revit running)."""
    item = {'label': label}
    try:
        item['title'] = doc.Title
        item['valid'] = doc.IsValidObject
        item['closed'] = bool(doc.Close(False))
    except Exception:
        item['error'] = traceback.format_exc()
    log.append(item)
    return item


def V(p):
    return DB.XYZ(p[0] / 12.0, p[1] / 12.0, p[2] / 12.0)


def to_in(p):
    return (p.X * 12.0, p.Y * 12.0, p.Z * 12.0)


def dot(p, v):
    return p[0] * v[0] + p[1] * v[1] + p[2] * v[2]


def rel(p, o):
    return (p[0] - o[0], p[1] - o[1], p[2] - o[2])


def extent(pts, v):
    vals = [dot(p, v) for p in pts]
    return [round(min(vals), 4), round(max(vals), 4)]


def rnd(p, k=4):
    return [round(c, k) for c in p]


class FailureCollector(DB.IFailuresPreprocessor):
    """Records every failure message. Warnings are left in the document so the zero-warnings gate stays honest;
    an error rolls the transaction back instead of raising a dialog in the headless session."""
    def PreprocessFailures(self, accessor):
        try:
            has_error = False
            for m in list(accessor.GetFailureMessages()):
                sev = m.GetSeverity()
                FAILURES.append({'severity': str(sev), 'text': m.GetDescriptionText()})
                if sev != DB.FailureSeverity.Warning:
                    has_error = True
            if has_error:
                return DB.FailureProcessingResult.ProceedWithRollBack
        except Exception:
            FAILURES.append({'collector_error': traceback.format_exc()})
        return DB.FailureProcessingResult.Continue


class Tx(object):
    def __init__(self, doc, name):
        self.t = DB.Transaction(doc, name)
        self.name = name

    def __enter__(self):
        self.t.Start()
        opts = self.t.GetFailureHandlingOptions()
        opts.SetFailuresPreprocessor(FailureCollector())
        self.t.SetFailureHandlingOptions(opts)
        return self.t

    def __exit__(self, et, ev, tb):
        if et is None:
            st = self.t.Commit()
            if st != DB.TransactionStatus.Committed:
                raise RuntimeError('transaction %s ended as %s' % (self.name, st))
        else:
            try:
                self.t.RollBack()
            except Exception:
                pass
        return False


def iter_solids(geo):
    for g in geo:
        if isinstance(g, DB.Solid):
            if g.Volume > 1e-12:
                yield g
        elif isinstance(g, DB.GeometryInstance):
            for s in iter_solids(g.GetInstanceGeometry()):
                yield s


def curve_points(c, n=360):
    if isinstance(c, DB.Line):
        return [to_in(c.GetEndPoint(0)), to_in(c.GetEndPoint(1))]
    return [to_in(c.Evaluate(i / float(n), True)) for i in range(n + 1)]


def solid_edge_points(s):
    pts = []
    for e in s.Edges:
        pts.extend(curve_points(e.AsCurve()))
    return pts


def mesh_points(s):
    pts = []
    for f in s.Faces:
        try:
            m = f.Triangulate(1.0)
        except Exception:
            m = f.Triangulate()
        if m is not None:
            for v in m.Vertices:
                pts.append(to_in(v))
    return pts


def pval(p):
    try:
        st = p.StorageType
        if st == DB.StorageType.String:
            return p.AsString()
        if st == DB.StorageType.Double:
            return {'value': p.AsDouble(), 'text': p.AsValueString()}
        if st == DB.StorageType.Integer:
            return {'value': p.AsInteger(), 'text': p.AsValueString()}
        return {'element_id': str(p.AsElementId().Value)}
    except Exception as ex:
        return 'error: ' + str(ex)


def export_view(doc, view, folder, name):
    """Export one view to folder/name.png (Revit appends its own suffix to the prefix; rename afterwards)."""
    safe(folder + '/x')
    tag = '_tmp_' + name
    for fn in os.listdir(folder):
        if fn.startswith(tag):
            os.remove(safe(folder + '/' + fn))
    opts = DB.ImageExportOptions()
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.SetViewsAndSheets(List[DB.ElementId]([view.Id]))
    opts.FilePath = os.path.normpath(safe(folder + '/' + tag))
    opts.HLRandWFViewsFileType = DB.ImageFileType.PNG
    opts.ShadowViewsFileType = DB.ImageFileType.PNG
    opts.ImageResolution = DB.ImageResolution.DPI_150
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = 1600
    doc.ExportImage(opts)
    made = [fn for fn in os.listdir(folder) if fn.startswith(tag) and fn.lower().endswith('.png')]
    final = folder + '/' + name + '.png'
    if os.path.exists(final):
        os.remove(safe(final))
    if made:
        os.rename(safe(folder + '/' + made[0]), safe(final))
    return made


def read_light(doc):
    """Read the light family definition of a family document; every field guarded so one miss keeps the rest."""
    d = {}
    if LT is None:
        d['error'] = 'Autodesk.Revit.DB.Lighting is not available'
        return d
    try:
        lf = LT.LightFamily.GetLightFamily(doc)
    except Exception:
        d['error'] = traceback.format_exc()
        return d

    def grab(key, fn):
        try:
            d[key] = fn()
        except Exception as ex:
            d[key + '_error'] = str(ex)

    grab('light_types', lambda: lf.GetNumberOfLightTypes())
    grab('shape_style', lambda: str(lf.GetLightShapeStyle()))
    grab('distribution_style', lambda: str(lf.GetLightDistributionStyle()))

    def tr():
        t = lf.GetLightSourceTransform()
        return {'origin_in': rnd(to_in(t.Origin)), 'basis_z': rnd((t.BasisZ.X, t.BasisZ.Y, t.BasisZ.Z)),
                'basis_x': rnd((t.BasisX.X, t.BasisX.Y, t.BasisX.Z))}
    grab('source_transform', tr)
    try:
        n = lf.GetNumberOfLightTypes()
    except Exception:
        n = 0
    types = []
    for i in range(n):
        item = {}
        try:
            item['name'] = lf.GetLightTypeName(i)
            lt = lf.GetLightType(i)
            ii = lt.GetInitialIntensity()
            item['intensity_class'] = ii.GetType().Name
            for k in ('Wattage', 'Efficacy', 'Flux', 'Luminosity', 'Illuminance'):
                try:
                    item['intensity_' + k] = getattr(ii, k)
                except Exception:
                    pass
            ic = lt.GetInitialColor()
            item['color_class'] = ic.GetType().Name
            for k in ('Temperature', 'TemperatureValue', 'Color'):
                try:
                    item['color_' + k] = str(getattr(ic, k))
                except Exception:
                    pass
            lo = lt.GetLossFactor()
            item['loss_class'] = lo.GetType().Name
            for k in ('LossFactor', 'LossFactorValue'):
                try:
                    item['loss_' + k] = getattr(lo, k)
                except Exception:
                    pass
            item['shape_class'] = lt.GetLightShape().GetType().Name
            item['distribution_class'] = lt.GetLightDistribution().GetType().Name
        except Exception:
            item['error'] = traceback.format_exc()
        types.append(item)
    d['types'] = types
    return d
