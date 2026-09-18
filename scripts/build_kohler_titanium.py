import os, json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = r'C:\Users\mlux\Documents\GitHub\3D-Model-Workflow'
OUT = os.path.join(ROOT, 'output', 'kohler_vibrant_titanium')
QA = os.path.join(OUT, '_qa')
TEX = os.path.join(OUT, 'Textures', 'KOHLER_Vibrant_Titanium_TT_Color.png')
if not os.path.isdir(QA): os.makedirs(QA)
NAME = 'KOHLER - Vibrant Titanium (TT) - Polished'
report = {'material': NAME, 'textures_required': True, 'vray': 'not requested',
          'source': 'Four user photographs; Kohler Titanium finish sell sheet',
          'optical_values': 'Visual approximation; not measured manufacturer BRDF'}
doc = None
try:
    app = __revit__.Application
    doc = app.NewProjectDocument(DB.UnitSystem.Imperial)
    tx = DB.Transaction(doc, 'Create Kohler titanium finish'); tx.Start()
    source = next(a for a in app.GetAssets(DB.Visual.AssetType.Appearance)
                  if a.FindByName('BaseSchema') and a.FindByName('BaseSchema').Value == 'GenericSchema')
    ae = DB.AppearanceAssetElement.Create(doc, NAME, source)
    mat = doc.GetElement(DB.Material.Create(doc, NAME))
    mat.AppearanceAssetId = ae.Id
    mat.MaterialClass = 'Metal'; mat.Color = DB.Color(108, 104, 101)
    mat.Shininess = 120; mat.Smoothness = 100; mat.Transparency = 0
    for key, value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, 'KOHLER'),
                       (DB.BuiltInParameter.ALL_MODEL_MODEL, 'Vibrant Titanium (TT)'),
                       (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION, 'Independent visual approximation of polished dark titanium PVD. Seamless texture-free metallic appearance; optical values inferred from product images.'),
                       (DB.BuiltInParameter.ALL_MODEL_URL, 'https://resources.kohler.com/webassets/kpna/brochures/Titanium_SellSheet_FIN_.pdf')]:
        mat.get_Parameter(key).Set(value)
    scope = DB.Visual.AppearanceAssetEditScope(doc); a = scope.Start(ae.Id)
    report['available_properties'] = [a[i].Name for i in range(a.Size)]
    values = {'generic_glossiness': .94, 'generic_reflectivity_at_0deg': .65,
              'generic_reflectivity_at_90deg': .98, 'generic_transparency': 0.,
              'generic_is_metal': True, 'generic_bump_amount': 0.,
              'generic_self_illum_luminance': 0.}
    for i in range(a.Size):
        p = a[i]
        if p.NumberOfConnectedProperties: p.RemoveConnectedAsset()
    for key, value in values.items():
        p = a.FindByName(key)
        if p is None: raise RuntimeError('Required appearance property absent: ' + key)
        p.Value = value
    diffuse = a.FindByName('generic_diffuse')
    diffuse.SetValueAsColor(DB.Color(108, 104, 101))
    diffuse.AddConnectedAsset('UnifiedBitmap')
    bitmap = diffuse.GetSingleConnectedAsset()
    bitmap.FindByName('unifiedbitmap_Bitmap').Value = TEX
    fade = a.FindByName('generic_diffuse_image_fade')
    if fade is not None: fade.Value = 1.0
    scope.Commit(True); scope.Dispose()
    def box(x, y, z, w, d, h):
        pts = [DB.XYZ(x,y,z), DB.XYZ(x+w,y,z), DB.XYZ(x+w,y+d,z), DB.XYZ(x,y+d,z)]
        loop = DB.CurveLoop()
        for i in range(4): loop.Append(DB.Line.CreateBound(pts[i],pts[(i+1)%4]))
        return DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]), DB.XYZ.BasisZ, h, DB.SolidOptions(mat.Id, DB.ElementId.InvalidElementId))
    def cylinder(x, y, r, h):
        import math
        loop = DB.CurveLoop()
        for start in [0, math.pi]:
            loop.Append(DB.Arc.Create(DB.XYZ(x,y,0), r, start, start+math.pi, DB.XYZ.BasisX, DB.XYZ.BasisY))
        return DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]), DB.XYZ.BasisZ, h, DB.SolidOptions(mat.Id,DB.ElementId.InvalidElementId))
    for solid in [box(-6,0,0,12,.1,8), cylinder(-2,-2,.4,3), cylinder(0,-2,.4,1.5), box(1,-2,0,2,1,.12)]:
        e=DB.DirectShape.CreateElement(doc, DB.ElementId(DB.BuiltInCategory.OST_GenericModel))
        e.SetShape(List[DB.GeometryObject]([solid]))
    vt = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(doc, vt.Id); view.Name = 'Titanium - 12ft surface and fixture samples'
    view.DisplayStyle = DB.DisplayStyle.Realistic
    view.SetOrientation(DB.ViewOrientation3D(DB.XYZ(12,-20,11), DB.XYZ(-.14,.23,.963).Normalize(), DB.XYZ(-.5,.82,-.27).Normalize()))
    tx.Commit()
    path = os.path.join(QA, 'Titanium_Library_Source_R2025.rvt')
    opt = DB.SaveAsOptions(); opt.OverwriteExistingFile = True
    doc.SaveAs(path,opt)
    exp=DB.ImageExportOptions(); exp.FilePath=os.path.join(QA,'native_surface'); exp.ExportRange=DB.ExportRange.SetOfViews
    exp.SetViewsAndSheets(List[DB.ElementId]([view.Id])); exp.HLRandWFViewsFileType=DB.ImageFileType.PNG
    exp.ShadowViewsFileType=DB.ImageFileType.PNG; exp.ZoomType=DB.ZoomFitType.FitToPage; exp.PixelSize=1800
    doc.ExportImage(exp)
    doc.Close(False); doc=None
    doc=app.OpenDocumentFile(path)
    m=next(m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material) if m.Name==NAME)
    asset=doc.GetElement(m.AppearanceAssetId).GetRenderingAsset()
    dmap = asset.FindByName('generic_diffuse').GetSingleConnectedAsset()
    report.update(success=True,version=app.VersionNumber,warnings=len(list(doc.GetWarnings())),
                  settings={k:asset.FindByName(k).Value for k in values},
                  diffuse_rgb=[108,104,101],
                  diffuse_texture=dmap.FindByName('unifiedbitmap_Bitmap').Value,
                  diffuse_texture_exists=os.path.isfile(dmap.FindByName('unifiedbitmap_Bitmap').Value),
                  connected_assets=sum(asset[i].NumberOfConnectedProperties for i in range(asset.Size)),
                  tested_surface_ft=[12,8],library_import='pending',native_appearance_review='pending')
    doc.Close(False); doc=None
except Exception:
    report['error']=traceback.format_exc(); report['success']=False
    if doc:
        if doc.IsModifiable: tx.RollBack()
        doc.Close(False)
finally:
    with open(os.path.join(QA,'validation.json'),'w') as f: json.dump(report,f,indent=2)
if not report.get('success'): raise RuntimeError(report.get('error'))
