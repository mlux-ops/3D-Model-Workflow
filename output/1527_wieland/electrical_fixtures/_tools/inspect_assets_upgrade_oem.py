# -*- coding: utf-8 -*-
"""Inspect appearance properties and save separate 2025 OEM reference copies."""
import os,json,traceback,datetime,clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app=__revit__.Application
doc=app.OpenDocumentFile(os.path.join(ROOT,'L4-0__8334187740856196','Maxim_Trim_57670WTBK_Black_R2025.rfa'))
assets=[]
for param in doc.FamilyManager.Parameters:
    if param.Definition.GetDataType()!=DB.SpecTypeId.Reference.Material:continue
    mat=doc.GetElement(doc.FamilyManager.CurrentType.AsElementId(param))
    if mat is None or not isinstance(mat,DB.Material):continue
    asset=doc.GetElement(mat.AppearanceAssetId).GetRenderingAsset()
    properties=[]
    for i in range(asset.Size):
        p=asset[i]
        row={'name':p.Name,'type':p.GetType().Name,'connected':p.NumberOfConnectedProperties}
        try:row['value']=str(p.Value)
        except Exception:
            try:row['value']=list(p.GetValueAsDoubles())
            except Exception:pass
        properties.append(row)
    assets.append({'material':mat.Name,'properties':properties})
doc.Close(False)
with open(os.path.join(ROOT,'APPEARANCE_DIAGNOSTIC.json'),'w') as stream:json.dump(assets,stream,indent=2)
upgrades=[]
files=json.load(open(os.path.join(ROOT,'OEM_EXTRACTED_FILES.json')))
files.append({'path':os.path.join(ROOT,'B2-2__5960925969973124/source/RBW_Dimple_manufacturer_download.rfa'),'extension':'.rfa'})
for item in files:
    if item['extension']!='.rfa':continue
    path=item['path'];doc=None;row={'source':path}
    try:
        info=DB.BasicFileInfo.Extract(path);row['source_format']=str(info.Format);info.Dispose()
        doc=app.OpenDocumentFile(path)
        target=os.path.join(os.path.dirname(path),os.path.splitext(os.path.basename(path))[0]+'_Reference_R2025.rfa')
        opts=DB.SaveAsOptions();opts.OverwriteExistingFile=True;opts.MaximumBackups=1
        doc.SaveAs(target,opts);doc.Close(False);doc=None
        info=DB.BasicFileInfo.Extract(target);row['saved_format']=str(info.Format);info.Dispose()
        row.update({'saved_path':target,'status':'UPGRADED_REFERENCE_ONLY','acceptance':'Exact model/dimension/material/host gates remain separate from this version upgrade.'})
    except Exception:row['error']=traceback.format_exc()
    finally:
        if doc is not None:doc.Close(False)
    upgrades.append(row)
with open(os.path.join(ROOT,'OEM_UPGRADE_RECEIPT.json'),'w') as stream:json.dump(upgrades,stream,indent=2)
