import os,json,traceback,clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
ROOT=r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow'
OUT=os.path.join(ROOT,'output','adella')
report={}
doc=None
try:
    app=__revit__.Application
    doc=app.NewProjectDocument(DB.UnitSystem.Imperial)
    tx=DB.Transaction(doc,'Adella material');tx.Start()
    source=next(a for a in app.GetAssets(DB.Visual.AssetType.Appearance) if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value=='GenericSchema')
    name='MSI Adella Viso White - 12x24 Satin - Stacked'
    ae=DB.AppearanceAssetElement.Create(doc,name,source)
    mat=doc.GetElement(DB.Material.Create(doc,name));mat.AppearanceAssetId=ae.Id
    mat.Color=DB.Color(239,240,239);mat.MaterialClass='Ceramic';mat.Shininess=35;mat.Smoothness=50
    for key,value in [(DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'Adella Viso White 12x24 satin ceramic wall tile; approximate indented relief; 1/16 inch light grout'),(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'MSI'),(DB.BuiltInParameter.ALL_MODEL_MODEL,'NADEVISWHI1224-N'),(DB.BuiltInParameter.ALL_MODEL_URL,'https://www.msisurfaces.com/3d-large-format-wall-tile/adella-viso-white-12x24-satin/')]:
        p=mat.get_Parameter(key)
        if p and not p.IsReadOnly:p.Set(value)
    scope=DB.Visual.AppearanceAssetEditScope(doc);a=scope.Start(ae.Id)
    report['properties']=[a[i].Name for i in range(a.Size)]
    for key,value in [('generic_glossiness',.60),('generic_reflectivity_at_0deg',.04),('generic_reflectivity_at_90deg',1.0),('generic_transparency',0.0),('generic_refraction_index',1.5),('generic_diffuse_image_fade',1.0)]:
        p=a.FindByName(key)
        if p.NumberOfConnectedProperties:p.RemoveConnectedAsset()
        p.Value=value
    def bitmap(key,filename):
        p=a.FindByName(key)
        if p.NumberOfConnectedProperties:p.RemoveConnectedAsset()
        p.AddConnectedAsset('UnifiedBitmap');b=p.GetSingleConnectedAsset()
        b.FindByName('unifiedbitmap_Bitmap').Value=os.path.join(OUT,'textures',filename)
        for key,size in [('texture_RealWorldScaleX',24.0625),('texture_RealWorldScaleY',12.0625)]:
            p=b.FindByName(key);p.Value=DB.UnitUtils.ConvertFromInternalUnits(size/12,p.GetUnitTypeId())
        for key in ['texture_URepeat','texture_VRepeat']:b.FindByName(key).Value=True
    bitmap('generic_diffuse','Adella_BaseColor.png');bitmap('generic_bump_map','Adella_Bump.png')
    bump=a.FindByName('generic_bump_amount')
    if bump:bump.Value=.15
    scope.Commit(True);scope.Dispose();tx.Commit()
    path=os.path.join(OUT,'Adella_Material_R2025.rvt')
    doc.SaveAs(path,DB.SaveAsOptions());doc.Close(False);doc=None
    doc=app.OpenDocumentFile(path)
    m=next(m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material) if m.Name==name)
    a=doc.GetElement(m.AppearanceAssetId).GetRenderingAsset()
    report.update(version=app.VersionNumber,name=m.Name,path=path,warnings=len(list(doc.GetWarnings())),success=True)
    report['maps']={k:a.FindByName(k).GetSingleConnectedAsset().FindByName('unifiedbitmap_Bitmap').Value for k in ['generic_diffuse','generic_bump_map']}
    doc.Close(False);doc=None
except Exception:
    report['error']=traceback.format_exc()
    if doc:
        try:
            if doc.IsModifiable:tx.RollBack()
            doc.Close(False)
        except:pass
with open(os.path.join(OUT,'revit_validation.json'),'w') as f:json.dump(report,f,indent=2)
