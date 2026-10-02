# -*- coding: utf-8 -*-
"""Exploration 2: reflect on the Revit API for light-source related types/methods."""
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


try:
    asm = DB.Document().GetType().Assembly if False else clr.GetClrType(DB.Document).Assembly
    types = []
    for t in asm.GetTypes():
        n = t.FullName
        if 'light' in n.lower() and t.IsPublic:
            types.append(n)
    report['light_types'] = sorted(types)
    fac = clr.GetClrType(DB.FamilyItemFactory) if hasattr(DB, 'FamilyItemFactory') else None
    from Autodesk.Revit import Creation
    ft = clr.GetClrType(Creation.FamilyItemFactory)
    report['factory_light_methods'] = sorted(set(m.Name for m in ft.GetMethods() if 'light' in m.Name.lower()))
    report['bip_light'] = [n for n in System.Enum.GetNames(clr.GetClrType(DB.BuiltInParameter)) if 'LIGHT' in n.upper()][:200]
    report['bic_light'] = [n for n in System.Enum.GetNames(clr.GetClrType(DB.BuiltInCategory)) if 'LIGHT' in n.upper()]
    report['stage'] = 'done'
except Exception:
    report['error'] = traceback.format_exc()
with open(guard(os.path.join(OUT, '_work', 'explore2.json')), 'w') as f:
    json.dump(report, f, indent=1, default=str)
