# -*- coding: utf-8 -*-
r"""Isolated Revit 2025 IronPython glass appearance experiment.

Prime run, one variant per invocation by setting SELECT below:
  D:\Games\pyRevit-Master\bin\pyrevit.exe run "E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\scripts\repair_bolla_quorum_optics_r04_r05.py" --revit=2025

Default BOLLA. For Quorum, copy to a NEW uniquely named script and set
SELECT='QUORUM' before prime runs. Each original input is opened as
FamilyDocument and saved solely under a distinct no-overwrite candidate.
An optical comparison remains mandatory; this script is not final approval.
"""
import os,sys,json,hashlib,traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SELECT='QUORUM'
SPECS={
 'BOLLA':{
  'src':'Kuzco_Bolla_PD3106_BG_R2025_IES_FINISH_R03_PARTIAL.rfa',
  'sha':'c2baa17404d66866d4eeeb7c72daf12f0b757b039baaf4e67736dbaacbc53ed6',
  'new':'Kuzco_Bolla_PD3106_BG_R2025_R04_CLEAR_APPEARANCE_UNAPPROVED.rfa',
  'receipt':'bolla_r04_clear_glass_receipt.json',
  'clear_id':1742,'frosted_id':8722,'clear_faces':(4435,6),
  'frosted_faces':(5101,16),'clear_name':'Glass','frosted_name':'Glass Frosted',
  'type':'Type 1','expected_glass_asset':'GlazingSchema',
  'clear_rgb':(248,251,250),'clear_transparency':98,
  'frosted_rgb':(235,236,233),'frosted_transparency':72,
 },
 'QUORUM':{
  'src':'Quorum_Veno_858-59_R2025_R04_UNAPPROVED.rfa',
  'sha':'c115f4919582fad4cff1405c4ccca06ed173aeaec1186fba47fecea0653a7e35',
  'new':'Quorum_Veno_858-59_R2025_R05_CLEAR_APPEARANCE_UNAPPROVED.rfa',
  'receipt':'quorum_r05_clear_glass_receipt.json',
  'clear_name':'Clear Glass','clear_rgb':(248,251,250),
  'clear_transparency':98,
  'type':'858-59 - Matte Black / Clear - R04 photo-derived unapproved',
 }
}

def check(test,why):
 if not test:raise RuntimeError(why)
def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  while True:
   s=f.read(1048576)
   if not s:break
   h.update(s)
 return h.hexdigest()
def elt_id(x):
 try:return int(x.Value)
 except:return int(x.IntegerValue)
def ename(e):
 try:return unicode(DB.Element.Name.GetValue(e))
 except:return unicode(e.Name)
def solid_fingerprint(doc):
 """Geometry/material audit independent of graphics appearance changes."""
 out=[]
 opt=DB.Options();opt.DetailLevel=DB.ViewDetailLevel.Fine
 opt.IncludeNonVisibleObjects=False
 for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
  if not isinstance(e,(DB.GenericForm,DB.FreeFormElement,DB.ImportInstance,DB.FamilyInstance)):
   continue
  try:g=e.get_Geometry(opt)
  except:continue
  if g is None:continue
  solids=[s for s in g if isinstance(s,DB.Solid) and s.Volume>1e-12]
  if not solids:continue
  out.append({'id':elt_id(e.Id),'class':unicode(e.GetType().Name),
              'solids':[(round(float(s.Volume),8),len(list(s.Faces)),
                         sorted([elt_id(f.MaterialElementId) for f in s.Faces]))
                        for s in solids]})
 return sorted(out,key=lambda x:x['id'])
def face_paint_state(doc,eid,count,matid):
 e=doc.GetElement(DB.ElementId(eid))
 check(isinstance(e,DB.Revolution),'Bolla original Revolution changed')
 opt=DB.Options();opt.DetailLevel=DB.ViewDetailLevel.Fine
 solids=[s for s in e.get_Geometry(opt) if isinstance(s,DB.Solid) and s.Volume>1e-12]
 check(len(solids)==1 and len(list(solids[0].Faces))==count,'Original glass geometry changed')
 paint=[]
 for face in solids[0].Faces:
  a=elt_id(face.MaterialElementId)
  p=bool(doc.IsPainted(e.Id,face))
  b=elt_id(doc.GetPaintedMaterial(e.Id,face))
  paint.append((a,p,b))
 check(all(x==(matid,True,matid) for x in paint),'Original glass paint changed')
 return paint
def snapshot(doc,spec):
 recorded={'type':unicode(doc.FamilyManager.CurrentType.Name),
           'warnings':[unicode(x.GetDescriptionText()) for x in doc.GetWarnings()],
           'solid_signature':solid_fingerprint(doc)}
 if 'clear_faces' in spec:
  recorded['clear_faces']=face_paint_state(doc,spec['clear_faces'][0],
                                           spec['clear_faces'][1],spec['clear_id'])
  recorded['frosted_faces']=face_paint_state(doc,spec['frosted_faces'][0],
                                              spec['frosted_faces'][1],spec['frosted_id'])
 return recorded
def generic_asset(app):
 for asset in app.GetAssets(DB.Visual.AssetType.Appearance):
  b=asset.FindByName('BaseSchema')
  if b is not None and b.Value=='GenericSchema':
   return asset
 raise RuntimeError('GenericSchema appearance template missing')
def new_asset(doc,app,label,color,transparency):
 template=generic_asset(app)
 elem=DB.AppearanceAssetElement.Create(doc,label,template)
 scope=DB.Visual.AppearanceAssetEditScope(doc)
 try:
  edit=scope.Start(elem.Id)
  for key,value in [('generic_diffuse',color),
                    ('generic_transparency',float(transparency)/100),
                    ('generic_reflectivity_at_0deg',.035),
                    ('generic_reflectivity_at_90deg',.12),
                    ('generic_glossiness',.88)]:
   p=edit.FindByName(key)
   check(p is not None,'Generic appearance key missing: '+key)
   if p.NumberOfConnectedProperties:p.RemoveConnectedAsset()
   if key=='generic_diffuse':p.SetValueAsColor(DB.Color(*color))
   else:p.Value=value
  # Generic transparent material: its transparency channel is explicit,
  # unlike source GlazingSchema using separate transmittance mapping.
  scope.Commit(True)
 finally:scope.Dispose()
 return elem
def update_material(doc,app,mat,rgb,transp,label):
 new=new_asset(doc,app,label,rgb,transp)
 mat.Color=DB.Color(*rgb)
 mat.Transparency=int(transp)
 mat.AppearanceAssetId=new.Id
 check(elt_id(mat.AppearanceAssetId)==elt_id(new.Id),'Appearance not assigned')
 return {'material_id':elt_id(mat.Id),'render_asset_id':elt_id(new.Id),
         'render_asset_schema':'GenericSchema',
         'appearance_transparency':float(transp)/100,
         'shading_transparency':transp,'rgb':list(rgb)}
def materials(doc,name):
 return [m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material)
         if ename(m)==name]
def main():
 check(sys.version_info[0]==2,'IronPython 2.7 required')
 app=__revit__.Application
 check(str(app.VersionNumber)=='2025','Revit 2025 required')
 check(getattr(__revit__,'ActiveUIDocument',None) is None,'Isolated document-free session required')
 spec=SPECS[SELECT]
 src=os.path.join(BASE,'candidates',spec['src'])
 dst=os.path.join(BASE,'candidates',spec['new'])
 rec=os.path.join(BASE,'qa',spec['receipt'])
 check(os.path.isfile(src) and digest(src)==spec['sha'],'Source RFA identity changed')
 check(not os.path.lexists(dst) and not os.path.lexists(rec),'Output exists; refusing overwrite')
 doc=None;saved=None;tx=None
 try:
  doc=app.OpenDocumentFile(src)
  check(doc.IsFamilyDocument,'Input not RFA')
  check(ename(doc.OwnerFamily.FamilyCategory)=='Lighting Fixtures','Category changed')
  check(len(list(doc.FamilyManager.Types))==1 and
        unicode(doc.FamilyManager.CurrentType.Name)==spec['type'],'Unexpected family type')
  before=snapshot(doc,spec)
  check(not before['warnings'],'Source Revit warnings present')
  matched=materials(doc,spec['clear_name'])
  check(len(matched)==1,'Ambiguous clear-glass material name')
  clear=matched[0]
  if 'clear_id' in spec:
   check(elt_id(clear.Id)==spec['clear_id'],'Bolla clear glass ID changed')
   frosted=materials(doc,spec['frosted_name'])
   check(len(frosted)==1 and elt_id(frosted[0].Id)==spec['frosted_id'],
         'Bolla frosted glass ID changed')
   ca=doc.GetElement(clear.AppearanceAssetId)
   fa=doc.GetElement(frosted[0].AppearanceAssetId)
   check(elt_id(ca.Id)==elt_id(fa.Id) and
         unicode(ca.GetRenderingAsset().Name)=='GlazingSchema',
         'Bolla OEM shared GlazingSchema evidence changed')
  tx=DB.Transaction(doc,'Isolated clear glass Realistic material candidate')
  check(tx.Start()==DB.TransactionStatus.Started,'Revit transaction start failed')
  changes=[update_material(doc,app,clear,spec['clear_rgb'],
             spec['clear_transparency'],SELECT+'_R_REALISTIC_CLEAR')]
  # Bolla inner globe must remain translucent opal rather than perfectly
  # see-through; give it an INDEPENDENT appearance asset, not the clear asset.
  if 'frosted_id' in spec:
   changes.append(update_material(doc,app,frosted[0],
              spec['frosted_rgb'],spec['frosted_transparency'],
              'BOLLA_R04_REALISTIC_FROSTED_OPAL'))
  doc.Regenerate()
  after=snapshot(doc,spec)
  check(before==after,'Geometry, original face paint, type, or warnings changed')
  check(tx.Commit()==DB.TransactionStatus.Committed,'RFA transaction failed')
  tx=None
  opts=DB.SaveAsOptions()
  opts.OverwriteExistingFile=False;opts.MaximumBackups=1
  doc.SaveAs(dst,opts)
  doc.Close(False);doc=None
  saved=app.OpenDocumentFile(dst)
  check(snapshot(saved,spec)==before,'Saved readback changed native part state')
  for change in changes:
   mat=saved.GetElement(DB.ElementId(change['material_id']))
   asset=saved.GetElement(mat.AppearanceAssetId)
   check(asset.GetRenderingAsset().Name=='GenericSchema',
         'Saved appearance schema did not persist')
   p=asset.GetRenderingAsset().FindByName('generic_transparency')
   check(p is not None and abs(p.Value-change['appearance_transparency'])<0.0001,
         'Saved transparency appearance did not persist')
  saved.Close(False);saved=None
  check(digest(src)==spec['sha'],'Original RFA modified unexpectedly')
  result={'status':'NATIVE_RFA_APPEARANCE_CANDIDATE_UNAPPROVED',
          'source_rfa':src,'source_sha256':spec['sha'],
          'candidate_rfa':dst,'candidate_sha256':digest(dst),
          'changes':changes,'geometry_and_original_paint_unchanged':True,
          'release_ready':False,'visual_qa':'REQUIRES_NEW_NATIVE_REALISTIC_CHECKER_IMAGES',
          'known_limitations':['Numerical transmission, reflectance and color are provisional',
             'Realistic View is not a physically calibrated ray tracing test',
             'Quorum glass shell photo-derived; geometry not OEM CAD',
             'Bolla IES path and source photometry not deliberately modified']}
  text=json.dumps(result,sort_keys=True,indent=2)
  fd=os.open(rec,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o644)
  with os.fdopen(fd,'wb') as f:f.write(text)
  print('OPTICS_CANDIDATE '+dst)
  print('OPTICS_RECEIPT '+rec)
 finally:
  if tx is not None:
   try:tx.RollBack()
   except:pass
  if saved is not None:saved.Close(False)
  if doc is not None:doc.Close(False)
if __name__=='__main__':
 try:main()
 except Exception:
  print(traceback.format_exc())
  raise
