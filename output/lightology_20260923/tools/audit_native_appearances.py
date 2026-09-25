# -*- coding: utf-8 -*-
import os,json,clr,traceback
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows=[]
def props(asset):
    result={}
    for i in range(asset.Size):
        p=asset[i]
        try:v=p.Value
        except Exception:
            try:v=list(p.GetValueAsDoubles())
            except Exception:v=str(p.Type)
        result[p.Name]={'value':v,'connections':p.NumberOfConnectedProperties}
    return result
for relative in [os.path.join('f05_1441643','RBW_Dimple_Black_Anodized_Amber_3000K_R2025.rfa'),os.path.join('f08_1104949','Alora_Cassia_LP549448AGOP_R2025.rfa')]:
    doc=__revit__.Application.OpenDocumentFile(os.path.join(ROOT,relative))
    try:
        row={'rfa':relative,'materials':[]}
        for mat in DB.FilteredElementCollector(doc).OfClass(DB.Material):
            if not ('Dimple' in mat.Name or 'Cassia' in mat.Name):continue
            app=doc.GetElement(mat.AppearanceAssetId)
            row['materials'].append({'name':mat.Name,'color':[int(mat.Color.Red),int(mat.Color.Green),int(mat.Color.Blue)],'transparency':mat.Transparency,'properties':props(app.GetRenderingAsset()) if app else None})
        rows.append(row)
    finally:doc.Close(False)
with open(os.path.join(ROOT,'material_diagnostic.json'),'w') as f:json.dump(rows,f,indent=2,default=str)