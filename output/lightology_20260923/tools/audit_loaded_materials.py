# -*- coding: utf-8 -*-
import os,json,clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path=os.path.join(ROOT,'f05_1441643','RBW_Dimple_Black_Anodized_Amber_3000K_R2025.rfa')
app=__revit__.Application;doc=app.OpenDocumentFile(path);project=app.NewProjectDocument(DB.UnitSystem.Imperial)
result=[]
def matrow(doc,mat):
    asset=doc.GetElement(mat.AppearanceAssetId).GetRenderingAsset()
    vals={}
    for key in ['generic_diffuse','generic_transparency','generic_glossiness','generic_is_metal','generic_self_illum_luminance','generic_self_illum_color_temperature']:
        p=asset.FindByName(key)
        try:val=p.Value
        except Exception:val=list(p.GetValueAsDoubles())
        vals[key]=val
    return {'name':mat.Name,'asset_id':str(mat.AppearanceAssetId.Value),'asset_name':asset.Name,'values':vals}
try:
    for mat in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        if 'Dimple' in mat.Name:result.append({'scope':'family','material':matrow(doc,mat)})
    fam=doc.LoadFamily(project);sym=project.GetElement(list(fam.GetFamilySymbolIds())[0])
    for mat in DB.FilteredElementCollector(project).OfClass(DB.Material):
        if 'Dimple' in mat.Name:result.append({'scope':'project','material':matrow(project,mat)})
    with open(os.path.join(ROOT,'appearance_load_diagnostic.json'),'w') as f:json.dump(result,f,indent=2,default=str)
finally:project.Close(False);doc.Close(False)