# -*- coding: utf-8 -*-
"""Prime-only readback of R05 file already saved before builder CLR failure.
Does not edit or resave any RFA. IronPython 2.7 / Revit 2025 only.
"""
import os,sys,json,hashlib,traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
BASE=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SRC=os.path.join(BASE,'candidates','Kuzco_Bolla_PD3106_BG_R2025_R04_CLEAR_APPEARANCE_UNAPPROVED.rfa')
DST=os.path.join(BASE,'candidates','Kuzco_Bolla_PD3106_BG_R2025_R05_REPAINT_OPTICAL_DIAGNOSTIC_UNAPPROVED.rfa')
OUT=os.path.join(BASE,'qa','bolla_r05_repaint_optical_diagnostic_receipt.json')
R04_SHA='7e655de0c5316c2e3f3afc28bcac29cc9a26d1d30c7bd84dab1379d7d44182b9'
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while True:
   b=f.read(1048576)
   if not b:break
   h.update(b)
 return h.hexdigest()
def eid(v):
 try:return int(v.Value)
 except:return int(v.IntegerValue)
def fail(ok,msg):
 if not ok:raise RuntimeError(msg)
def snap(doc):
 opt=DB.Options();opt.DetailLevel=DB.ViewDetailLevel.Fine
 ans={}
 mats={x.Name:x for x in DB.FilteredElementCollector(doc).OfClass(DB.Material)}
 for key,el,n,trans in [('outer',4435,'BOLLA_R05_CLEAR_OUTER_DIAGNOSTIC',98),
                        ('inner',5101,'BOLLA_R05_OPAL_INNER_DIAGNOSTIC',96)]:
  m=mats[n]
  fail(m.Transparency==trans,'Transparency unexpected '+n)
  a=doc.GetElement(m.AppearanceAssetId)
  fail(a.GetRenderingAsset().Name=='GenericSchema','Render schema not generic '+n)
  property=a.GetRenderingAsset().FindByName('generic_transparency')
  fail(property is not None and abs(property.Value-trans/100.0)<.0001,
       'Render transparency not preserved '+n)
  element=doc.GetElement(DB.ElementId(el))
  solids=[s for s in element.get_Geometry(opt) if isinstance(s,DB.Solid) and s.Volume>1e-12]
  fail(len(solids)==1 and len(list(solids[0].Faces))==(6 if key=='outer' else 16),
       'Glass geometry or faces changed '+key)
  for face in solids[0].Faces:
   fail(doc.IsPainted(element.Id,face) and eid(doc.GetPaintedMaterial(element.Id,face))==eid(m.Id),
        'Fresh material did not reach painted face '+key)
  ans[key]={'material_id':eid(m.Id),'painted_faces':len(list(solids[0].Faces)),
            'transparency':trans,'render_asset_id':eid(a.Id),
            'volume':round(float(solids[0].Volume),8)}
 return ans
def shape_signature(doc):
 opt=DB.Options();opt.DetailLevel=DB.ViewDetailLevel.Fine
 data=[]
 for el in DB.FilteredElementCollector(doc).OfClass(DB.Revolution):
  solids=[s for s in el.get_Geometry(opt) if isinstance(s,DB.Solid) and s.Volume>1e-12]
  for s in solids:data.append((eid(el.Id),round(float(s.Volume),7),len(list(s.Faces))))
 return sorted(data)
def main():
 fail(sys.version_info[0]==2 and str(__revit__.Application.VersionNumber)=='2025',
      'Requires IronPython Revit2025')
 fail(getattr(__revit__,'ActiveUIDocument',None) is None,'Requires isolated no-document run')
 fail(os.path.isfile(DST) and os.path.isfile(SRC),'Files missing')
 fail(digest(SRC)==R04_SHA,'Source R04 checksum changed')
 fail(not os.path.lexists(OUT),'Readback receipt exists')
 doc=None;baseline=None
 try:
  baseline=__revit__.Application.OpenDocumentFile(SRC)
  before_geometry=shape_signature(baseline)
  doc=__revit__.Application.OpenDocumentFile(DST)
  glass=snap(doc)
  after_geometry=shape_signature(doc)
  fail(before_geometry==after_geometry,'Revolution geometry/volume/face counts changed from R04')
  fail(not list(doc.GetWarnings()),'Family warnings')
 finally:
  if doc is not None:doc.Close(False)
  if baseline is not None:baseline.Close(False)
 fail(digest(SRC)==R04_SHA,'R04 changed during readback')
 result={'status':'NATIVE_RFA_APPEARANCE_CANDIDATE_UNAPPROVED',
  'candidate_rfa':DST,'candidate_sha256':digest(DST),
  'source_rfa':SRC,'source_sha256':R04_SHA,
  'geometry_unchanged':True,'painted_faces_reassigned':{'outer':6,'inner':16},
  'glass_readback':glass,'solid_signature_count':len(after_geometry),'release_ready':False,
  'validation_scope':'R05 source-guarded recovered native material/face readback; no Revit render'}
 payload=json.dumps(result,indent=2,sort_keys=True)
 h=os.open(OUT,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o644)
 with os.fdopen(h,'wb') as f:f.write(payload.encode('ascii'))
 print('BOLLA_R05_RECOVERY_QA '+OUT)
main()
