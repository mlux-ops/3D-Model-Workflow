# -*- coding: utf-8 -*-
"""Task-owned disposable Revit environment probe, no user model changes."""
import os
import json
import traceback
import datetime
import clr
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(OUT, 'native_environment_probe.json')
report = {'started_utc': datetime.datetime.utcnow().isoformat(), 'stage': 'started', 'success': False}
doc = None

def checkpoint(stage):
    report['stage'] = stage
    with open(REPORT, 'w') as stream:
        json.dump(report, stream, indent=2, default=str)

checkpoint('import_api')
try:
    clr.AddReference('RevitAPI')
    from Autodesk.Revit import DB
    app = __revit__.Application
    report['revit_version'] = app.VersionNumber
    report['revit_build'] = app.VersionBuild
    report['short_curve_tolerance_ft'] = app.ShortCurveTolerance
    template = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
    report['template'] = template
    report['template_exists'] = os.path.isfile(template)
    checkpoint('open_face_template')
    doc = app.NewFamilyDocument(template)
    report['is_family_document'] = doc.IsFamilyDocument
    report['family_placement_type'] = str(doc.OwnerFamily.FamilyPlacementType)
    report['template_warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    report['appearance_asset_count'] = len(list(app.GetAssets(DB.Visual.AssetType.Appearance)))
    report['success'] = app.VersionNumber == '2025' and doc.IsFamilyDocument and report['appearance_asset_count'] > 0
    checkpoint('complete')
except Exception:
    report['error'] = traceback.format_exc()
    checkpoint('failed')
    raise
finally:
    if doc is not None:
        doc.Close(False)
