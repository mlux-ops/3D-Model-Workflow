import os
import json
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

root = r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow'
report = {}
try:
    app = __revit__.Application
    report['version'] = app.VersionNumber
    report['build'] = app.VersionBuild
    doc = app.NewFamilyDocument(r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft')
    report['family_placement'] = str(doc.OwnerFamily.FamilyPlacementType)
    report['category'] = doc.OwnerFamily.FamilyCategory.Name
    report['views'] = [v.Name for v in DB.FilteredElementCollector(doc).OfClass(DB.View)]
    report['materials'] = [m.Name for m in DB.FilteredElementCollector(doc).OfClass(DB.Material)]
    report['assets'] = [{'name':a.Name, 'schema':a.FindByName('BaseSchema').Value if a.FindByName('BaseSchema') else ''} for a in app.GetAssets(DB.Visual.AssetType.Appearance) if any(s in a.Name.lower() for s in ['chrome', 'metal', 'steel'])][:60]
    report['planes'] = [{'name':p.Name, 'origin':str(p.GetPlane().Origin),'normal':str(p.GetPlane().Normal)} for p in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane)]
    doc.Close(False)
    report['success'] = True
except Exception:
    report['error'] = traceback.format_exc()
with open(os.path.join(root, 'tmp', 'revit-probe.json'), 'w') as f:
    json.dump(report, f, indent=2)
