# -*- coding: utf-8 -*-
"""Exploration 3: members of the Lighting namespace types."""
import os
import json
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
import System

OUT = os.path.normpath('E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/high')
report = {}


def guard(path):
    p = os.path.normpath(path)
    if not p.lower().startswith(OUT.lower() + os.sep):
        raise RuntimeError('write outside run folder refused: ' + p)
    return p


def members(t):
    out = []
    flags = System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.DeclaredOnly
    for m in t.GetMembers(flags):
        if m.MemberType.ToString() in ('Method', 'Property', 'Constructor'):
            if isinstance(m, System.Reflection.MethodInfo) and (m.Name.startswith('get_') or m.Name.startswith('set_')):
                continue
            if m.MemberType.ToString() == 'Method':
                sig = m.Name + '(' + ', '.join(['%s %s' % (p.ParameterType.Name, p.Name) for p in m.GetParameters()]) + ') -> ' + m.ReturnType.Name + (' [static]' if m.IsStatic else '')
            else:
                sig = m.MemberType.ToString() + ' ' + m.Name
            out.append(sig)
    return out


try:
    asm = clr.GetClrType(DB.Document).Assembly
    for n in ['Autodesk.Revit.DB.Lighting.LightFamily', 'Autodesk.Revit.DB.Lighting.LightGroupManager', 'Autodesk.Revit.DB.Lighting.LightGroup',
              'Autodesk.Revit.DB.Lighting.LightType', 'Autodesk.Revit.DB.Lighting.LightShape', 'Autodesk.Revit.DB.Lighting.PointLightShape',
              'Autodesk.Revit.DB.Lighting.CircleLightShape', 'Autodesk.Revit.DB.Lighting.LightDistribution', 'Autodesk.Revit.DB.Lighting.SphericalLightDistribution',
              'Autodesk.Revit.DB.Lighting.HemisphericalLightDistribution', 'Autodesk.Revit.DB.Lighting.SpotLightDistribution',
              'Autodesk.Revit.DB.Lighting.InitialWattageIntensity', 'Autodesk.Revit.DB.Lighting.InitialFluxIntensity', 'Autodesk.Revit.DB.Lighting.InitialLuminousIntensity',
              'Autodesk.Revit.DB.Lighting.InitialIntensity', 'Autodesk.Revit.DB.Lighting.InitialColor', 'Autodesk.Revit.DB.Lighting.PresetInitialColor',
              'Autodesk.Revit.DB.Lighting.CustomInitialColor', 'Autodesk.Revit.DB.Lighting.ColorPreset', 'Autodesk.Revit.DB.Lighting.BasicLossFactor',
              'Autodesk.Revit.DB.Lighting.LossFactor', 'Autodesk.Revit.DB.Lighting.LightShapeStyle', 'Autodesk.Revit.DB.Lighting.LightDistributionStyle',
              'Autodesk.Revit.DB.LightingSource', 'Autodesk.Revit.DB.Lighting.LightDimmingColor']:
        t = asm.GetType(n)
        if t is None:
            report[n] = 'missing'
            continue
        d = {'members': members(t)}
        if t.IsEnum:
            d['enum'] = list(System.Enum.GetNames(t))
        report[n] = d
    report['stage'] = 'done'
except Exception:
    report['error'] = traceback.format_exc()
with open(guard(os.path.join(OUT, '_work', 'explore3.json')), 'w') as f:
    json.dump(report, f, indent=1, default=str)
