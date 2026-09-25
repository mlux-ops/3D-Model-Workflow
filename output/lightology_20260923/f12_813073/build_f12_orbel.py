# -*- coding: utf-8 -*-
"""Build and validate F12 Visual Comfort Modern Orbel wall sconce in Revit 2025.

Selected option: TLG1279684 / 700WSOBLNB, Natural Brass, frosted glass.
Owns only output/lightology_20260923/f12_813073.
"""
import os
import json
import math
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = r'E:\Claude\3D-Model-Workflow'
OUT = os.path.join(ROOT, 'output', 'lightology_20260923', 'f12_813073')
NATIVE = os.path.join(OUT, 'native')
REVIEW = os.path.join(OUT, 'review')
RFA = os.path.join(NATIVE, 'Visual_Comfort_Orbel_700WSOBLNB_Natural_Brass_R2025.rfa')
REPORT = os.path.join(NATIVE, 'validation.json')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
for p in (OUT, NATIVE, REVIEW):
    if not os.path.isdir(p): os.makedirs(p)
report = {'fixture':'F12','product':'Orbel Wall Sconce','sku':'700WSOBLNB','spec':'TLG1279684','finish':'Natural Brass','rfa_path':RFA}
docs=[]
tx=None

def checkpoint(stage):
    report['stage']=stage
    with open(REPORT,'w') as f: json.dump(report,f,indent=2,default=str)

def xyz(x,y,z): return DB.XYZ(x/12.0,y/12.0,z/12.0)

def curve_loop(origin,u,v,pts):
    def p(q): return origin.Add(u.Multiply(q[0]/12.0)).Add(v.Multiply(q[1]/12.0))
    loop=DB.CurveLoop(); cur=pts[0]
    for item in pts[1:]:
        if len(item)==3 and item[0]=='arc':
            mid,end=item[1],item[2]; loop.Append(DB.Arc.Create(p(cur),p(end),p(mid))); cur=end
        else:
            loop.Append(DB.Line.CreateBound(p(cur),p(item))); cur=item
    if cur != pts[0]: loop.Append(DB.Line.CreateBound(p(cur),p(pts[0])))
    return loop

def rounded_rect(x0,y0,x1,y1,r):
    k=1-math.sqrt(.5)
    return [(x0+r,y0),(x1-r,y0),('arc',(x1-r*k,y0+r*k),(x1,y0+r)),(x1,y1-r),('arc',(x1-r*k,y1-r*k),(x1-r,y1)),(x0+r,y1),('arc',(x0+r*k,y1-r*k),(x0,y1-r)),(x0,y0+r),('arc',(x0+r*k,y0+r*k),(x0+r,y0))]

def freeform(doc,name,solid,param,subcat):
    e=DB.FreeFormElement.Create(doc,solid); e.Subcategory=subcat
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),param)
    report.setdefault('parts',[]).append({'name':name,'id':str(e.Id.Value)})
    return e

def extrude(doc,name,origin,u,v,normal,pts,length,param,subcat):
    loop=curve_loop(origin,u,v,pts)
    solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]),normal,length/12.0)
    return freeform(doc,name,solid,param,subcat)

def sphere_solid(center,r):
    # Revolve a semicircular radial profile about local Y through 360 degrees.
    s=math.sqrt(.5)*r
    pts=[(0,-r),('arc',(s,-s),(r,0)),('arc',(s,s),(0,r))]
    loop=curve_loop(center,DB.XYZ.BasisX,DB.XYZ.BasisY,pts)
    frame=DB.Frame(center,DB.XYZ.BasisX,DB.XYZ.BasisY.CrossProduct(DB.XYZ.BasisX),DB.XYZ.BasisY)
    return DB.GeometryCreationUtilities.CreateRevolvedGeometry(frame,List[DB.CurveLoop]([loop]),0,2*math.pi)

def circle_loop(center,r):
    a=center.Add(DB.XYZ(-r/12.0,0,0)); b=center.Add(DB.XYZ(r/12.0,0,0)); m1=center.Add(DB.XYZ(0,r/12.0,0)); m2=center.Add(DB.XYZ(0,-r/12.0,0))
    loop=DB.CurveLoop(); loop.Append(DB.Arc.Create(a,b,m1)); loop.Append(DB.Arc.Create(b,a,m2)); return loop

def globe_shell(doc,param,subcat):
    center=xyz(0,-2.95,4.20); outer=sphere_solid(center,2.50); inner=sphere_solid(center,2.36)
    shell=DB.BooleanOperationsUtils.ExecuteBooleanOperation(outer,inner,DB.BooleanOperationsType.Difference)
    # True rear opening through the glass shell, centered on the concealed socket axis.
    ocenter=xyz(0,-2.95,1.25); opening=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([circle_loop(ocenter,.72)]),DB.XYZ.BasisZ,1.15/12.0)
    shell=DB.BooleanOperationsUtils.ExecuteBooleanOperation(shell,opening,DB.BooleanOperationsType.Difference)
    return freeform(doc,'Frosted glass globe shell with rear opening',shell,param,subcat)

def cylinder(doc,name,center_xy,z0,z1,r,param,subcat):
    c=xyz(center_xy[0],center_xy[1],z0); solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([circle_loop(c,r)]),DB.XYZ.BasisZ,(z1-z0)/12.0)
    return freeform(doc,name,solid,param,subcat)

def set_color(asset,key,rgb):
    p=asset.FindByName(key)
    if p is not None:
        if p.NumberOfConnectedProperties: p.RemoveConnectedAsset()
        p.SetValueAsColor(DB.Color(*rgb))

def set_scalar(asset,key,val):
    p=asset.FindByName(key)
    if p is not None:
        if p.NumberOfConnectedProperties: p.RemoveConnectedAsset()
        p.Value=val

def make_material(doc,app,name,rgb,transparency,metallic=False):
    assets=list(app.GetAssets(DB.Visual.AssetType.Appearance)); src=next(a for a in assets if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value=='GenericSchema')
    ae=DB.AppearanceAssetElement.Create(doc,name+' Appearance',src); mat=doc.GetElement(DB.Material.Create(doc,name)); mat.AppearanceAssetId=ae.Id; mat.Color=DB.Color(*rgb); mat.Transparency=transparency
    scope=DB.Visual.AppearanceAssetEditScope(doc); a=scope.Start(ae.Id)
    set_color(a,'generic_diffuse',rgb); set_scalar(a,'generic_glossiness',.42 if metallic else .22); set_scalar(a,'generic_transparency',transparency/100.0)
    set_scalar(a,'generic_reflectivity_at_0deg',.45 if metallic else .05); set_scalar(a,'generic_reflectivity_at_90deg',.75 if metallic else .35); set_scalar(a,'generic_self_illum_luminance',0.0)
    if not metallic: set_scalar(a,'generic_refraction_index',1.47)
    scope.Commit(True); scope.Dispose(); mat.MaterialClass='Metal' if metallic else 'Glass'; return mat

def bounds(elements):
    bs=[e.get_BoundingBox(None) for e in elements if e.get_BoundingBox(None) is not None]
    return [min(b.Min.X for b in bs)*12,min(b.Min.Y for b in bs)*12,min(b.Min.Z for b in bs)*12,max(b.Max.X for b in bs)*12,max(b.Max.Y for b in bs)*12,max(b.Max.Z for b in bs)*12]

def solids(geom):
    for g in geom:
        if isinstance(g,DB.Solid) and g.Volume>1e-12: yield g
        elif isinstance(g,DB.GeometryInstance):
            for s in solids(g.GetInstanceGeometry()): yield s

def view(doc,name,eye,target,realistic=False):
    vt=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    v=DB.View3D.CreateIsometric(doc,vt.Id); v.Name=name; f=target.Subtract(eye).Normalize(); up=DB.XYZ.BasisY
    if abs(f.DotProduct(up))>.98: up=DB.XYZ.BasisZ
    right=f.CrossProduct(up).Normalize(); v.SetOrientation(DB.ViewOrientation3D(eye,right.CrossProduct(f).Normalize(),f)); v.DetailLevel=DB.ViewDetailLevel.Fine; v.Scale=1; v.DisplayStyle=DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
    box=DB.BoundingBoxXYZ(); box.Min=xyz(-7,-8,-1); box.Max=xyz(7,8,8); v.SetSectionBox(box); v.IsSectionBoxActive=True; return v

def export_views(doc,views):
    for v in views:
        o=DB.ImageExportOptions(); o.ExportRange=DB.ExportRange.SetOfViews; o.SetViewsAndSheets(List[DB.ElementId]([v.Id])); o.FilePath=os.path.join(REVIEW,v.Name.replace(' ','_'))
        o.HLRandWFViewsFileType=DB.ImageFileType.PNG; o.ShadowViewsFileType=DB.ImageFileType.PNG; o.ImageResolution=DB.ImageResolution.DPI_150; o.ZoomType=DB.ZoomFitType.FitToPage; o.PixelSize=1600; doc.ExportImage(o)

try:
    app=__revit__.Application; report['revit_version']=app.VersionNumber; assert app.VersionNumber=='2025'; checkpoint('creating family')
    doc=app.NewFamilyDocument(TEMPLATE); docs.append(doc); tx=DB.Transaction(doc,'Build F12 Orbel Natural Brass'); tx.Start(); doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_LightingFixtures); doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
    fm=doc.FamilyManager; fm.NewType('Natural Brass / Frosted / Bulb Not Included')
    brass=make_material(doc,app,'Orbel - Natural Brass',(181,139,71),0,True); glass=make_material(doc,app,'Orbel - Frosted Glass',(247,244,235),58,False)
    pbr=fm.AddParameter('Metal Finish',DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False); fm.Set(pbr,brass.Id); pgl=fm.AddParameter('Glass Finish',DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False); fm.Set(pgl,glass.Id)
    for name,val in [('Overall Width',5.0),('Overall Height',12.9),('Projection',6.7),('Backplate Depth',0.7)]:
        p=fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False); fm.SetFormula(p,str(val)+'"')
    for bip,val in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'Visual Comfort Modern'),(DB.BuiltInParameter.ALL_MODEL_MODEL,'Orbel Wall Sconce 700WSOBLNB'),(DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'F12 visualization family; Natural Brass, frosted globe, bulb not included; face-based Revit 2025')]:
        p=fm.get_Parameter(bip)
        if p is not None: fm.Set(p,val)
    note=fm.AddParameter('Model Accuracy Notes',DB.GroupTypeId.IdentityData,DB.SpecTypeId.String.Text,False); fm.Set(note,'Printed overall 5 W x 12.9 H x 6.7 D and backplate 5 W x 12.9 H x 0.7 D are authoritative. Globe diameter/center, blade thickness/projection, 0.14 in glass shell, 1.44 in rear opening and concealed socket dimensions are inferred from manufacturer imagery. Real glass shell opening modeled. No photometric source or MEP connector.')
    cats={n:doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,n) for n in ['Backplate','Blade','Glass','Socket']}
    # Backplate is the exact printed envelope in X/Y; 0.7 in projection from the native host plane.
    extrude(doc,'Rounded rectangular backplate',xyz(0,0,0),DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ,rounded_rect(-2.5,-6.45,2.5,6.45,.10),.70,pbr,cats['Backplate'])
    # Thin full-height perpendicular sculptural blade, inferred from product photography.
    extrude(doc,'Perpendicular central blade',xyz(-.07,0,.70),DB.XYZ.BasisY,DB.XYZ.BasisZ,DB.XYZ.BasisX,[(-6.45,0),(6.45,0),(6.45,3.25),(-6.45,3.25)],.14,pbr,cats['Blade'])
    cylinder(doc,'Concealed brass socket boss',(0,-2.95),.70,2.05,.55,pbr,cats['Socket'])
    globe_shell(doc,pgl,cats['Glass']); doc.Regenerate()
    target=xyz(0,-.5,3.1); views=[view(doc,'Front',xyz(0,-.5,28),target),view(doc,'Side',xyz(25,-.5,3.1),target),view(doc,'Oblique',xyz(12,-8,21),target),view(doc,'Material',xyz(9,-5,18),target,True)]
    tx.Commit(); tx=None; o=DB.SaveAsOptions(); o.OverwriteExistingFile=True; o.MaximumBackups=1; o.PreviewViewId=views[2].Id; doc.SaveAs(RFA,o); export_views(doc,views); doc.Close(False); docs.remove(doc)
    checkpoint('reopen and inspect'); doc=app.OpenDocumentFile(RFA); docs.append(doc); report['reopened']=doc.IsFamilyDocument; report['category']=doc.OwnerFamily.FamilyCategory.Name; report['placement']=str(doc.OwnerFamily.FamilyPlacementType)
    forms=list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement)); b=bounds(forms); report['bounds_inches']=b; report['dimensions_inches']=[b[3]-b[0],b[4]-b[1],b[5]-b[2]]; report['family_warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    report['shell_opening_modeled']=any(e.Subcategory and e.Subcategory.Name=='Glass' for e in forms)
    checkpoint('native host and material QA'); project=app.NewProjectDocument(DB.UnitSystem.Imperial); docs.append(project); family=doc.LoadFamily(project); symbol=project.GetElement(list(family.GetFamilySymbolIds())[0]); tx=DB.Transaction(project,'F12 native wall face QA'); tx.Start(); level=next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)),None)
    if level is None: level=DB.Level.Create(project,0)
    wt=next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind==DB.WallKind.Basic); wall=DB.Wall.Create(project,DB.Line.CreateBound(DB.XYZ(-5,0,0),DB.XYZ(5,0,0)),wt.Id,level.Id,10,0,False,False); symbol.Activate(); project.Regenerate(); href=DB.HostObjectUtils.GetSideFaces(wall,DB.ShellLayerType.Exterior)[0]; face=wall.GetGeometryObjectFromReference(href); pt=face.Project(DB.XYZ(0,0,5)).XYZPoint; inst=project.Create.NewFamilyInstance(href,pt,DB.XYZ.BasisX,symbol); project.Regenerate(); report['hosted']=inst.Host is not None and inst.Host.Id==wall.Id; report['host_id']=str(inst.Host.Id.Value) if inst.Host else None; report['mounting_normal_dot_host_normal']=inst.GetTransform().BasisZ.DotProduct(face.FaceNormal)
    report['material_tests']={}
    for name in ['Metal Finish','Glass Finish']:
        p=symbol.LookupParameter(name); original=p.AsElementId(); alt=DB.Material.Create(project,'QA '+name); p.Set(alt); project.Regenerate(); mids=[]
        for s in solids(inst.get_Geometry(DB.Options())):
            for f in s.Faces: mids.append(f.MaterialElementId)
        report['material_tests'][name]=alt in mids or alt in list(inst.GetMaterialIds(False)); p.Set(original); project.Regenerate()
    hosted_view=view(project,'Hosted Wall',xyz(12,-18,8),xyz(0,0,5),False)
    tx.Commit(); tx=None
    export_views(project,[hosted_view])
    report['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
    report['review_files']=[f for f in os.listdir(REVIEW) if f.lower().endswith('.png')]
    dims=report['dimensions_inches']; report['technical_pass']=bool(report['reopened'] and report['category']=='Lighting Fixtures' and report['hosted'] and abs(abs(report['mounting_normal_dot_host_normal'])-1.0)<.01 and all(report['material_tests'].values()) and not report['family_warnings'] and not report['project_warnings'] and all(abs(a-b)<.03 for a,b in zip(dims,[5.0,12.9,6.7])))
    if not report['technical_pass']: raise RuntimeError('Required F12 QA gate failed: '+json.dumps(report,default=str))
    checkpoint('complete')
except Exception:
    report['error']=traceback.format_exc(); checkpoint('failed at '+report.get('stage','start'))
finally:
    if tx is not None:
        try: tx.RollBack()
        except Exception: pass
    for d in reversed(docs):
        try: d.Close(False)
        except Exception: pass


