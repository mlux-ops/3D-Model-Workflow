import os, json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
ROOT = r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow'
r = {}
doc = None
try:
    app = __revit__.Application
    doc = app.NewFamilyDocument(r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model line based.rft')
    r['version'] = app.VersionNumber
    r['placement'] = str(doc.OwnerFamily.FamilyPlacementType)
    r['parameters'] = [{'name':p.Definition.Name,'instance':p.IsInstance,'formula':p.Formula,'id':str(p.Id)} for p in doc.FamilyManager.Parameters]
    r['planes'] = [{'name':p.Name,'origin':str(p.GetPlane().Origin),'normal':str(p.GetPlane().Normal),'reference':str(p.get_Parameter(DB.BuiltInParameter.ELEM_REFERENCE_NAME).AsInteger())} for p in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane)]
    r['assets'] = []
    for a in app.GetAssets(DB.Visual.AssetType.Appearance):
        label = a.Name
        for key in ['UIName','description','keyword']:
            p = a.FindByName(key)
            if p is not None:
                try: label += ' | '+str(p.Value)
                except: pass
        if 'stainless' in label.lower(): r['assets'].append(label)
    r['views'] = [{'name':v.Name,'type':str(v.ViewType)} for v in DB.FilteredElementCollector(doc).OfClass(DB.View)]
except:
    r['error'] = traceback.format_exc()
finally:
    if doc: doc.Close(False)
    with open(os.path.join(ROOT,'tmp','gola','probe.json'),'w') as f: json.dump(r,f,indent=2)
