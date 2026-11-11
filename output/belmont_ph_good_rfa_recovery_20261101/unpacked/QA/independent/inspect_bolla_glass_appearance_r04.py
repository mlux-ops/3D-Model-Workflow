# -*- coding: utf-8 -*-
r"""Read-only Revit 2025 IronPython Bolla R04 optical material and IES audit.

Run only in the prime's isolated Revit 2025 process:
 D:\Games\pyRevit-Master\bin\pyrevit.exe run "E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\inspect_bolla_glass_appearance_r04.py" --revit=2025

NO material writes, transactions, Save/SaveAs, Paint, user document mutation.
Outputs one new JSON; guards the R03 source SHA and companion IES SHA.
Revit Shaded mode may not depict physically transparent/refraction-correct
glass; the OEM's Glass(1) physical appearance must be examined before edits.
"""
from __future__ import print_function
import os, json, hashlib, traceback, time
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

ROOT=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
RFA=os.path.join(ROOT,'candidates','Kuzco_Bolla_PD3106_BG_R2025_IES_FINISH_R03_PARTIAL.rfa')
IES=os.path.join(ROOT,'sources','photometry','PD3106-BG - Bolla.IES')
OUT=os.path.join(ROOT,'qa','bolla_glass_appearance_r04_probe.json')
RFA_SHA='c2baa17404d66866d4eeeb7c72daf12f0b757b039baaf4e67736dbaacbc53ed6'
IES_SHA='9e9f70e2eecc3b1c4130bea2f3fcb3c5a1798fb61363185348b635cd71737ce4'
GLASS={1742:('Glass',4435,6),8722:('Glass Frosted',5101,16)}

def check(cond,why):
    if not cond: raise RuntimeError(why)
def digest(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        while True:
            b=f.read(1048576)
            if not b: break
            h.update(b)
    return h.hexdigest()
def ide(x):
    try:return int(x.Value)
    except:return int(x.IntegerValue)
def val(x):
    try:return unicode(x)
    except:return '[not serializable]'
def asset_walk(asset,depth=0):
    if asset is None or depth>3:return None
    rows=[]
    try: count=asset.Size
    except:count=0
    for i in range(count):
        p=asset[i]
        row={'name':val(p.Name),'property_type':val(p.GetType().FullName)}
        try:row['value']=val(p.Value)
        except:pass
        try:row['color_rgb']=[int(p.GetValueAsColor().Red),int(p.GetValueAsColor().Green),int(p.GetValueAsColor().Blue)]
        except:pass
        try:row['connected_asset_count']=int(p.NumberOfConnectedProperties)
        except:pass
        try:
            if p.NumberOfConnectedProperties>0:
                row['connected']=[]
                for n in range(p.NumberOfConnectedProperties):
                    row['connected'].append(asset_walk(p.GetConnectedProperty(n),depth+1))
        except Exception as ex:row['connected_read_error']=val(ex)
        rows.append(row)
    return {'name':val(asset.Name),'properties':rows}
def face_materials(doc,eid):
    el=doc.GetElement(DB.ElementId(eid))
    options=DB.Options();options.DetailLevel=DB.ViewDetailLevel.Fine
    options.ComputeReferences=True
    solids=[s for s in el.get_Geometry(options) if isinstance(s,DB.Solid) and s.Volume>1e-12]
    check(len(solids)==1,'Glass solid count differs '+str(eid))
    result=[]
    for f in solids[0].Faces:
        result.append({'original_face_material':ide(f.MaterialElementId),
                       'is_painted':bool(doc.IsPainted(el.Id,f)),
                       'painted_material_id':ide(doc.GetPaintedMaterial(el.Id,f))})
    return result
def main():
    app=__revit__.Application
    check(str(app.VersionNumber)=='2025','Must run Revit 2025')
    check(getattr(__revit__,'ActiveUIDocument',None) is None,'Isolated session required')
    for path,expected in ((RFA,RFA_SHA),(IES,IES_SHA)):
        check(os.path.isfile(path) and digest(path)==expected,'Input missing or changed '+path)
    check(not os.path.lexists(OUT),'No-overwrite receipt exists')
    doc=None
    try:
        doc=app.OpenDocumentFile(RFA)
        report={'schema_version':1,'status':'READ_ONLY_ASSET_AUDIT',
                'rfa_path':RFA,'rfa_sha256':RFA_SHA,
                'ies_path':IES,'ies_sha256':IES_SHA,
                'generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                'glass_materials':[],'source_saved':False}
        for mid,(name,eid,n) in GLASS.items():
            mat=doc.GetElement(DB.ElementId(mid))
            check(isinstance(mat,DB.Material),'Missing original OEM material ID '+str(mid))
            color=mat.Color
            row={'material_id':mid,'name':val(mat.Name),
                 'shading_color_rgb':[int(color.Red),int(color.Green),int(color.Blue)],
                 'shading_transparency':int(mat.Transparency),
                 'appearance_asset_id':ide(mat.AppearanceAssetId),
                 'face_element_id':eid,
                 'faces':face_materials(doc,eid)}
            check(len(row['faces'])==n,'OEM glass face count changed')
            check(all(x['is_painted'] and x['painted_material_id']==mid and
                      x['original_face_material']==mid for x in row['faces']),
                  'Original painted glass altered')
            try:
                appe=doc.GetElement(mat.AppearanceAssetId)
                row['appearance_asset_element_name']=val(appe.Name)
                row['appearance_asset_properties']=asset_walk(appe.GetRenderingAsset())
            except Exception as ex:row['appearance_read_error']=val(ex)
            report['glass_materials'].append(row)
    finally:
        if doc is not None:doc.Close(False)
    check(digest(RFA)==RFA_SHA and digest(IES)==IES_SHA,'Input changed during inspection')
    data=json.dumps(report,ensure_ascii=True,sort_keys=True,separators=(',',':'))
    handle=os.open(OUT,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644)
    with os.fdopen(handle,'wb') as f:f.write(data)
    print('BOLLA_R04_OPTICAL_AUDIT '+OUT)
if __name__=='__main__':
    try:main()
    except Exception:
        print('BOLLA_R04_OPTICAL_AUDIT_ERROR '+traceback.format_exc())
        raise
