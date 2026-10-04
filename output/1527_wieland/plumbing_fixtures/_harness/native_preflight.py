# -*- coding: utf-8 -*-
"""Read native Revit capability through the shared serialized runner."""
import json
import os
import time
import traceback

OUT = r'E:\Claude\3D-Model-Workflow\output\1527_wieland\plumbing_fixtures\_harness\native_preflight.json'
record = {'started_at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'stage': 'script invoked'}

def save():
    with open(OUT, 'w') as handle:
        json.dump(record, handle, indent=2)

save()
try:
    import clr
    clr.AddReference('RevitAPI')
    from Autodesk.Revit import DB
    app = __revit__.Application
    record['revit_version'] = app.VersionNumber
    record['revit_build'] = app.VersionBuild
    record['family_templates'] = {}
    for name in ['Generic Model.rft', 'Generic Model face based.rft', 'Plumbing Fixture.rft']:
        path = os.path.join(r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial', name)
        record['family_templates'][path] = os.path.isfile(path)
    record['stage'] = 'native API available'
    record['success'] = app.VersionNumber == '2025'
except Exception:
    record['error'] = traceback.format_exc()
    record['success'] = False
save()
