# -*- coding: utf-8 -*-
import os,json,traceback,hashlib
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
ROOT=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_recovery_20261101'
SRC=os.path.join(ROOT,'unpacked','REVIEW_RFAs','Kuzco_Bolla_PD3106_BG_R2025_R05_REPAINT_OPTICAL_DIAGNOSTIC_UNAPPROVED.rfa')
OUT=os.path.join(ROOT,'bolla_project_placement_fix03_20261101.json')
res={'source':SRC,'status':'STARTED'}
app=__revit__.Application
project=None;family_doc=None;transaction=None
try:
    project=app.NewProjectDocument(DB.UnitSystem.Metric)
    family_doc=app.OpenDocumentFile(SRC)
    loaded=family_doc.LoadFamily(project)
    if loaded is None:raise RuntimeError('FamilyDocument.LoadFamily returned None')
    symbols=[project.GetElement(x) for x in loaded.GetFamilySymbolIds()]
    if len(symbols)!=1:raise RuntimeError('Expected one type, got '+str(len(symbols)))
    sym=symbols[0]
    levels=list(DB.FilteredElementCollector(project).OfClass(DB.Level))
    if not levels:raise RuntimeError('No level in disposable project')
    lev=levels[0]
    transaction=DB.Transaction(project,'Disposable Bolla placement test');transaction.Start()
    if not sym.IsActive:sym.Activate()
    project.Regenerate()
    inst=project.Create.NewFamilyInstance(DB.XYZ(0,0,8),sym,lev,DB.Structure.StructuralType.NonStructural)
    project.Regenerate()
    res['instance_id']=int(inst.Id.IntegerValue)
    res['type']=str(DB.Element.Name.GetValue(sym))
    res['family']=str(loaded.Name)
    transaction.Commit();transaction=None
    bbox=inst.get_BoundingBox(None)
    res['bounding_box']=[float(bbox.Min.X),float(bbox.Min.Y),float(bbox.Min.Z),float(bbox.Max.X),float(bbox.Max.Y),float(bbox.Max.Z)] if bbox else None
    res['placed_instance_category']=str(inst.Category.Name)
    res['warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
    res['status']='PLACED_PASS' if res['instance_id'] and not res['warnings'] else 'PLACED_WITH_WARNINGS'
except Exception as e:
    res['status']='PLACEMENT_FAILED';res['error']=str(e);res['traceback']=traceback.format_exc()[-4000:]
finally:
    if transaction:
        try:transaction.RollBack()
        except:pass
    if family_doc:family_doc.Close(False)
    if project:project.Close(False)
    with open(OUT,'w') as f:f.write(json.dumps(res,indent=2))
print('BOLLA_PLACEMENT',res['status'],res.get('error',''))
