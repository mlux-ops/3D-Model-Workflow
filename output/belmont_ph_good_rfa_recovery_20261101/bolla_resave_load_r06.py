# -*- coding: utf-8 -*-
import os,json,traceback,hashlib
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
ROOT=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_recovery_20261101'
SRC=os.path.join(ROOT,'unpacked','REVIEW_RFAs','Kuzco_Bolla_PD3106_BG_R2025_R05_REPAINT_OPTICAL_DIAGNOSTIC_UNAPPROVED.rfa')
DEST=os.path.join(ROOT,'Kuzco_Bolla_PD3106_BG_R2025_R06_CLEAN_LOAD_TEST.rfa')
OUT=os.path.join(ROOT,'bolla_resave_load_r06.json')
result={'source':SRC,'candidate':DEST,'status':'STARTED'}
app=__revit__.Application
fam=None
proj=None
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        while True:
            b=f.read(1048576)
            if not b:break
            h.update(b)
    return h.hexdigest()
try:
    if os.path.exists(DEST) or os.path.exists(OUT):raise RuntimeError('Refusing overwrite')
    result['source_sha256']=sha(SRC)
    fam=app.OpenDocumentFile(SRC)
    opts=DB.SaveAsOptions();opts.OverwriteExistingFile=False
    fam.SaveAs(DEST,opts)
    fam.Close(False);fam=None
    result['candidate_sha256']=sha(DEST)
    proj=app.NewProjectDocument(DB.UnitSystem.Metric)
    result['file_load_result']=bool(proj.LoadFamily(DEST))
    result['family_count']=len([f for f in DB.FilteredElementCollector(proj).OfClass(DB.Family) if 'Bolla' in str(f.Name)])
    result['warnings']=[w.GetDescriptionText() for w in proj.GetWarnings()]
    result['source_unchanged']=sha(SRC)==result['source_sha256']
    result['status']='STANDARD_LOAD_PASS' if result['family_count']==1 else 'STANDARD_LOAD_FAIL'
except Exception as ex:
    result['status']='ERROR';result['error']=str(ex);result['traceback']=traceback.format_exc()[-2700:]
finally:
    if fam:fam.Close(False)
    if proj:proj.Close(False)
    with open(OUT,'w') as f:f.write(json.dumps(result,indent=2))
print('BOLLA_R06',result['status'])
