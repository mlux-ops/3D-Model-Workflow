# -*- coding: utf-8 -*-
"""Probe the Revit 2025 API for any route to create, write or export an ADSKLIB.

Reviewer requires the .adsklib as a delivered file, without opening a Revit
project to make it. Before reporting that as impossible, enumerate the actual
loaded assemblies rather than relying on recollection.
"""
import json
import os
import traceback

import clr
clr.AddReference('RevitAPI')
import System
from Autodesk.Revit import DB

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'library_api_probe.json')

KEYWORDS = ('adsklib', 'materiallibrary', 'assetlibrary', 'librarypath',
            'exportlibrary', 'savelibrary', 'createlibrary', 'materialexport')
NAME_HINTS = ('library', 'adsk', 'assetset', 'appearanceasset', 'propertyset')

report = {'revit_api_assembly': None, 'types': {}, 'candidate_members': [],
          'library_paths': None, 'notes': []}


def scan():
    asm = System.Reflection.Assembly.GetAssembly(DB.Document)
    report['revit_api_assembly'] = asm.FullName

    hits = []
    for t in asm.GetExportedTypes():
        full = t.FullName or ''
        low = full.lower()
        if not any(h in low for h in NAME_HINTS):
            continue
        members = []
        try:
            for m in t.GetMembers():
                ml = (m.Name or '').lower()
                if any(k in ml for k in KEYWORDS) or ('library' in ml) or ('export' in ml and 'asset' in low):
                    members.append('%s.%s' % (t.Name, m.Name))
        except Exception:
            pass
        if members:
            report['types'][full] = sorted(set(members))
            hits.extend(members)

    # Anything anywhere in the API whose member name mentions a material library.
    for t in asm.GetExportedTypes():
        try:
            for m in t.GetMembers():
                ml = (m.Name or '').lower()
                if any(k in ml for k in KEYWORDS):
                    report['candidate_members'].append('%s.%s' % (t.FullName, m.Name))
        except Exception:
            pass
    report['candidate_members'] = sorted(set(report['candidate_members']))

    app = __revit__.Application
    try:
        paths = app.GetLibraryPaths()
        report['library_paths'] = dict((k, paths[k]) for k in paths.Keys)
    except Exception as exc:
        report['library_paths'] = 'unavailable: %s' % exc

    # Does the Application expose any material-library member at all?
    app_members = []
    for m in app.GetType().GetMembers():
        ml = (m.Name or '').lower()
        if 'librar' in ml or 'material' in ml or 'asset' in ml:
            app_members.append(m.Name)
    report['application_members'] = sorted(set(app_members))


try:
    scan()
    report['conclusion'] = (
        'ADSKLIB write/export route found' if report['candidate_members']
        else 'No ADSKLIB write or export member exposed by the Revit API')
except Exception:
    report['error'] = traceback.format_exc()

with open(OUT, 'w') as handle:
    handle.write(json.dumps(report, indent=2, default=str, sort_keys=True))
print(report.get('conclusion', report.get('error')))
