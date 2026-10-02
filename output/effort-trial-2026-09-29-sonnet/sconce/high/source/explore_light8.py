# -*- coding: utf-8 -*-
"""Exploration 8: find any API surface that could create a family light source."""
import os
import json
import traceback
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
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
    asm = clr.GetClrType(DB.Document).Assembly
    hits = []
    for t in asm.GetTypes():
        if not t.IsPublic:
            continue
        for m in t.GetMethods():
            if m.DeclaringType != t:
                continue
            if 'light' in m.Name.lower() and 'skylight' not in m.Name.lower():
                hits.append(t.Name + '.' + m.Name)
    report['methods'] = sorted(set(hits))
    from Autodesk.Revit import UI
    report['postable'] = [n for n in System.Enum.GetNames(clr.GetClrType(UI.PostableCommand)) if 'light' in n.lower() or 'source' in n.lower()]
    report['uiapp_type'] = str(type(__revit__))
    try:
        report['active_uidoc'] = str(__revit__.ActiveUIDocument)
    except Exception as ex:
        report['active_uidoc'] = 'ERR ' + str(ex)
    # Family-level parameters on the face-based template's family
    app = __revit__.Application
    doc = app.NewFamilyDocument(r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft')
    try:
        ps = []
        for p in doc.OwnerFamily.Parameters:
            try:
                v = p.AsValueString() or p.AsString()
            except Exception:
                v = None
            ps.append([p.Definition.Name, str(p.StorageType), v, p.IsReadOnly])
        report['owner_params'] = ps
    finally:
        doc.Close(False)
    report['stage'] = 'done'
except Exception:
    report['error'] = traceback.format_exc()
with open(guard(os.path.join(OUT, '_work', 'explore8.json')), 'w') as f:
    json.dump(report, f, indent=1, default=str)
