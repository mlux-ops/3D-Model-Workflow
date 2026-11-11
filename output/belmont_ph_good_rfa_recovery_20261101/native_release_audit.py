# -*- coding: utf-8 -*-
"""Revit 2025 read-only audit of recovered Belmont Penthouse Good RFA files."""
import clr, os, json, hashlib, traceback, time
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

ROOT=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_recovery_20261101'
FOLDER=os.path.join(ROOT,'unpacked','REVIEW_RFAs')
REPORT=os.path.join(ROOT,'native_release_audit.json')
app=__revit__.Application
rows=[]

def hashfile(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        while True:
            x=f.read(1048576)
            if not x:break
            h.update(x)
    return h.hexdigest()

for name in sorted(os.listdir(FOLDER)):
    if not name.lower().endswith('.rfa'):continue
    path=os.path.join(FOLDER,name)
    row={'name':name,'path':path,'sha256_before':hashfile(path),'status':'ERROR'}
    doc=None
    try:
        doc=app.OpenDocumentFile(path)
        fam=doc.OwnerFamily
        row['family_document']=bool(doc.IsFamilyDocument)
        row['category']=fam.FamilyCategory.Name if fam.FamilyCategory else None
        row['placement']=str(fam.FamilyPlacementType)
        row['types']=[str(t.Name) for t in doc.FamilyManager.Types]
        row['warning_count']=len(doc.GetWarnings())
        row['connectors']=len(list(DB.FilteredElementCollector(doc).OfClass(DB.ConnectorElement)))
        try:
            lf=DB.Lighting.LightFamily.GetLightFamily(doc)
            row['native_light_types']=int(lf.GetNumberOfLightTypes()) if lf else 0
            if lf and row['native_light_types']:
                lt=lf.GetLightType(0)
                dist=lt.GetLightDistribution()
                row['light_distribution_class']=str(dist.GetType().Name)
                try:row['photometric_file']=str(dist.PhotometricWebFile)
                except:pass
        except Exception as ex:row['light_error']=str(ex)
        row['status']='OPEN_REVIEWED'
    except Exception as ex:
        row['error']=str(ex)
        row['traceback']=traceback.format_exc()[-1200:]
    finally:
        if doc is not None:
            try:doc.Close(False)
            except Exception as ex:row['close_error']=str(ex)
    row['sha256_after']=hashfile(path)
    row['untouched']=row['sha256_before']==row['sha256_after']
    rows.append(row)

with open(REPORT,'w') as f:
    f.write(json.dumps({'date_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'results':rows},indent=2))
print('RFA_AUDIT_COUNT',len(rows),'OPENED',sum(1 for x in rows if x['status']=='OPEN_REVIEWED'))
for row in rows:
    print(row['name'],row['status'],'light_types',row.get('native_light_types'),'connectors',row.get('connectors'))
print('RFA_AUDIT_REPORT',REPORT)
