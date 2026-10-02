# -*- coding: utf-8 -*-
"""Exploration 5 (pyRevit): reflection dump of Autodesk.Revit.DB.Lighting (LightFamily/LightType/shapes/distributions/intensity/colour)."""
import sys
import traceback
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/source')
from guard import dump_json
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
import System
from System.Reflection import BindingFlags

RUN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/'
rep = {}


def save():
    dump_json(rep, RUN + 'work/explore5.json')


def sig(m):
    try:
        ps = ', '.join('%s %s' % (p.ParameterType.Name, p.Name) for p in m.GetParameters())
    except Exception:
        ps = '?'
    return '%s(%s)' % (m.Name, ps)


try:
    asm = clr.GetClrType(DB.Element).Assembly
    want = ['LightFamily', 'LightType', 'LightShape', 'PointLightShape', 'LineLightShape', 'CircleLightShape', 'RectangleLightShape',
            'LightShapeStyle', 'LightDistribution', 'SphericalLightDistribution', 'HemisphericalLightDistribution', 'SpotLightDistribution',
            'PhotometricWebLightDistribution', 'LightDistributionStyle', 'InitialIntensity', 'InitialWattageIntensity', 'InitialFluxIntensity',
            'InitialLuminousIntensity', 'InitialIlluminanceIntensity', 'InitialColor', 'PresetInitialColor', 'CustomInitialColor', 'ColorPreset',
            'LossFactor', 'BasicLossFactor', 'AdvancedLossFactor', 'LightDimmingColor', 'LightingSource']
    flags = BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly
    out = {}
    for t in asm.GetTypes():
        if t.IsPublic and t.Name in want and t.Namespace and 'Revit.DB' in t.Namespace:
            e = {'ns': t.Namespace, 'isenum': t.IsEnum, 'base': t.BaseType.Name if t.BaseType else None}
            if t.IsEnum:
                e['values'] = [str(n) for n in System.Enum.GetNames(t)]
            else:
                e['ctors'] = [sig(c) for c in t.GetConstructors()]
                e['methods'] = sorted(set(sig(m) for m in t.GetMethods(flags) if not m.Name.startswith(('get_', 'set_'))))
                e['props'] = sorted(set('%s %s%s' % (p.PropertyType.Name, p.Name, ' [set]' if p.CanWrite else '') for p in t.GetProperties(flags)))
            out[t.FullName] = e
    rep['types'] = out
except Exception:
    rep['error'] = traceback.format_exc()
rep['done'] = True
save()
