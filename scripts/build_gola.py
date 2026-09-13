# -*- coding: utf-8 -*-
"""Build and verify a native parametric Revit 2025 Gola family.

Run with installed pyrevit run. Creates new documents only. Dimensions in mm.
Cross-section envelopes are manufacturer dimensions. Small undimensioned
wall thicknesses, radii and accessory details are drawing-derived approximations.
"""
import os, json, math, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow'
OUT = os.path.join(ROOT, 'output', 'gola')
RFA = os.path.join(OUT, 'Richelieu_Gola_Channel_Profiles_2025.rfa')
RVT = os.path.join(OUT, 'Gola_2025_Placement_Examples.rvt')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model line based.rft'
URL = 'https://www.richelieu.com/us/en/category/moldings-corbels-and-components/metal-and-pvc-moldings-profiles-and-rails/gola-cabinet-profiles/1182698'
TYPES = [
 ('Horizontal - C - Double Grip', 'HC', 26.0,72.7,4100.0,'70010040410170'),
 ('Horizontal - L - Single Grip', 'HL', 27.0,56.0,4100.0,'70010050410170'),
 ('Vertical - Single Grip', 'VS', 48.25,36.6,4400.0,'70010200440170'),
 ('Vertical - Double Grip', 'VD', 66.5,36.6,4400.0,'70010190440170')]
report = {'stage':'start', 'rfa_path':RFA, 'sample_project_path':RVT,
          'types':[], 'previews':[], 'inferred':'Small wall thicknesses, radii, serrations and accessory internals are simplified from illustrations.'}
docs=[]
tx=None

def check(stage):
    report['stage']=stage
    with open(os.path.join(OUT,'validation.json'),'w') as f:
        json.dump(report,f,indent=2,default=str)

def mm(v): return v/304.8
def xyz(x,y,z): return DB.XYZ(mm(x),mm(y),mm(z))
def rect(a,b,c,d): return [(a,b),(c,b),(c,d),(a,d)]

def profile_c():
    # Coordinates are depth, height. Native tangent arcs preserve grip radii.
    p=[(22,72.7),(24.8,72.7),('a',(25.6485,72.3485),(26,71.5)),
       (26,68.9),('a',(25.6485,68.0515),(24.8,67.7)),(11.9,67.7),
       ('a',(8.0816,66.1184),(6.5,62.3)),(6.5,10.4),
       ('a',(8.0816,6.5816),(11.9,5)),(24.8,5),
       ('a',(25.6485,4.6485),(26,3.8)),(26,1.2),
       ('a',(25.6485,0.3515),(24.8,0)),(22,0),(22,1.2),(24.8,1.2),
       (24.8,3.8),(11.9,3.8),('a',(7.2331,5.7331),(5.3,10.4)),
       (5.3,28.2),(0,28.2),(0,33.4),(1.2,33.4),(1.2,29.4),
       (5.3,29.4),(5.3,43.3),(1.2,43.3),(1.2,39.3),(0,39.3),
       (0,44.5),(5.3,44.5),(5.3,62.3),('a',(7.2331,66.9669),(11.9,68.9)),
       (24.8,68.9),(24.8,71.5),(22,71.5)]
    return [swap_path(p)]

def swap_path(p):
    return [('a',(v[1][1],v[1][0]),(v[2][1],v[2][0])) if v[0]=='a' else (v[1],v[0]) for v in p]

def profile_l():
    p=[(0,56),(6.3,56),('a',(7.1485,55.6485),(7.5,54.8)),
       (7.5,10.5),('a',(9.0816,6.6816),(12.9,5.1)),(25.8,5.1),
       ('a',(26.6485,4.7485),(27,3.9)),(27,1.2),('a',(26.6485,0.3515),(25.8,0)),
       (23,0),(23,1.2),(25.8,1.2),(25.8,3.9),(12.9,3.9),
       ('a',(8.2331,5.8331),(6.3,10.5)),(6.3,10.7),(0.9,10.7),
       (0.9,15.9),(2.1,15.9),(2.1,11.9),(6.3,11.9),(6.3,25.6),
       (2.1,25.6),(2.1,21.6),(0.9,21.6),(0.9,26.8),(6.3,26.8),
       (6.3,54.8),(1.2,54.8),(1.2,53.5),(0,53.5)]
    # Merge the 0.2mm bend-to-rib segment below Revit's short-curve limit.
    p.remove((6.3,10.7))
    return [swap_path(p)]

def vertical(single):
    # Three separate solid components preserve the hollow mounting box.
    if single:
        front=[(0,24.6),(34.2,24.6),('a',(38.872,26.40),(41.1,30.7)),
               (42.0,35.4),(47.05,35.4),(47.05,25.8),(45.75,25.8),
               (45.75,24.6),(48.25,24.6),(48.25,36.6),(40.9,36.6),
               (39.9,30.9),('a',(38.081,27.239),(34.2,25.8)),(7.2,25.8),
               ('a',(2.957,27.557),(1.2,31.8)),(1.2,36.6),(0,36.6)]
        off=0
    else:
        front=[(0,24.6),(2.5,24.6),(2.5,25.8),(1.2,25.8),(1.2,35.4),
               (7.1,35.4),(8.1,30.7),('a',(10.328,26.40),(15,24.6)),
               (51.5,24.6),('a',(56.172,26.40),(58.4,30.7)),(59.4,35.4),
               (65.3,35.4),(65.3,25.8),(64,25.8),(64,24.6),(66.5,24.6),
               (66.5,36.6),(58.3,36.6),(57.2,30.9),
               ('a',(55.381,27.239),(51.5,25.8)),(15,25.8),
               ('a',(11.119,27.239),(9.3,30.9)),(8.2,36.6),(0,36.6)]
        off=18.25
    # Smooth screw receptacles retain the visible mounting topology; micro-teeth omitted.
    rail=[(off,0),(off+1.2,0),(off+1.2,1.6),(off+28.8,1.6),
          (off+28.8,0),(off+30,0),(off+30,2.8),(off+21.4,2.8),
          ('a',(off+20.3,4.6),(off+21.4,6.4)),(off+30,6.4),
          (off+30,24.6),(off+28.8,24.6),(off+28.8,7.6),(off+21.4,7.6),
          ('a',(off+19.1,5.7),(off+19.1,4.6)),('a',(off+19.2,3.6),(off+19.5,2.8)),
          (off+10.5,2.8),('a',(off+10.8,3.6),(off+10.9,4.6)),
          ('a',(off+10.9,5.7),(off+8.6,7.6)),(off+1.2,7.6),
          (off+1.2,24.6),(off,24.6),(off,6.4),(off+8.6,6.4),
          ('a',(off+9.7,4.6),(off+8.6,2.8)),(off,2.8)]
    return [front,rail]

def asset_label(a):
    s=a.Name
    for key in ['UIName','description','keyword']:
        p=a.FindByName(key)
        if p is not None:
            try:s+=' | '+str(p.Value)
            except:pass
    return s

def material(doc,name,color,asset=None,cls='Metal'):
    m=doc.GetElement(DB.Material.Create(doc,name))
    m.MaterialClass=cls; m.Color=DB.Color(*color); m.Shininess=50; m.Smoothness=75
    if asset is not None:
        m.AppearanceAssetId=DB.AppearanceAssetElement.Create(doc,name,asset).Id
    return m

params={}
formula_params={}
def add(doc,name,spec,instance=False,group=None,formula=None):
    fm=doc.FamilyManager
    p=fm.AddParameter(name, group or DB.GroupTypeId.Geometry,spec,instance)
    params[name]=p
    if formula is not None:fm.SetFormula(p,formula)
    return p

def assoc(doc,e,builtin,p):
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(e.get_Parameter(builtin),p)

def curve_array(path):
    c=DB.CurveArray()
    first=path[0]; current=first
    def p(v): return xyz(0,v[0],v[1])
    for item in path[1:]+[first]:
        if item[0]=='a':
            middle,end=item[1],item[2]
            c.Append(DB.Arc.Create(p(current),p(end),p(middle)))
        else:
            end=item
            if p(current).DistanceTo(p(end))<1e-9:continue
            if p(current).DistanceTo(p(end))<mm(0.80):
                raise ValueError('Short profile edge '+str((current,end)))
            c.Append(DB.Line.CreateBound(p(current),p(end)))
        current=end
    return c

def extrusion(doc,name,path,start,end,vis,mat,cat):
    a=DB.CurveArrArray(); a.Append(curve_array(path))
    sp=DB.SketchPlane.Create(doc,DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisX,DB.XYZ.Zero))
    e=doc.FamilyCreate.NewExtrusion(True,a,sp,mm(1000))
    e.Subcategory=cat
    comment=e.get_Parameter(DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
    if comment is not None and not comment.IsReadOnly:comment.Set(name)
    for built,value,label in [(DB.BuiltInParameter.EXTRUSION_START_PARAM,start,'Start'),(DB.BuiltInParameter.EXTRUSION_END_PARAM,end,'End')]:
        if isinstance(value,str):
            if value in params:p=params[value]
            elif value in formula_params:p=formula_params[value]
            else:
                pname='Control '+str(e.Id.Value)+' '+label
                p=add(doc,pname,DB.SpecTypeId.Length,True,DB.GroupTypeId.Constraints,value)
                formula_params[value]=p
            assoc(doc,e,built,p)
        else:e.get_Parameter(built).Set(mm(value))
    assoc(doc,e,DB.BuiltInParameter.MATERIAL_ID_PARAM,params[mat])
    assoc(doc,e,DB.BuiltInParameter.IS_VISIBLE_PARAM,params[vis])
    return e

def bool_formula(doc,name,formula):
    add(doc,name,DB.SpecTypeId.Boolean.YesNo,True,DB.GroupTypeId.Constraints,formula)
    return name

def solids(geom):
    for g in geom:
        if isinstance(g,DB.Solid) and g.Volume>1e-12:yield g
        elif isinstance(g,DB.GeometryInstance):
            for s in solids(g.GetInstanceGeometry()):yield s

def visible_solids(instance,view=None):
    o=DB.Options(); o.IncludeNonVisibleObjects=False
    if view:o.View=view
    return list(solids(instance.get_Geometry(o)))

def set_length(inst,length):
    # Native curve-based Length is read-only in a project. This is the
    # location curve edited by endpoint grips and temporary dimensions.
    c=inst.Location.Curve
    start=c.GetEndPoint(0);direction=c.GetEndPoint(1).Subtract(start).Normalize()
    inst.Location.Curve=DB.Line.CreateBound(start,start.Add(direction.Multiply(mm(length))))

def extents(ss,transform=None):
    pts=[]
    for s in ss:
        for e in s.Edges:
            for p in e.Tessellate():pts.append(transform.OfPoint(p) if transform else p)
    if not pts:raise ValueError('No solid geometry')
    return [min(p.X for p in pts)*304.8,min(p.Y for p in pts)*304.8,min(p.Z for p in pts)*304.8,
            max(p.X for p in pts)*304.8,max(p.Y for p in pts)*304.8,max(p.Z for p in pts)*304.8]

def preview(doc,name,eye,up,target,box=None):
    vt=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    v=DB.View3D.CreateIsometric(doc,vt.Id);v.Name=name
    fw=target.Subtract(eye).Normalize();rt=fw.CrossProduct(up).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye,rt.CrossProduct(fw).Normalize(),fw))
    v.DetailLevel=DB.ViewDetailLevel.Fine;v.DisplayStyle=DB.DisplayStyle.ShadingWithEdges;v.Scale=1
    for cat in doc.Settings.Categories:
        if cat.Id!=DB.ElementId(DB.BuiltInCategory.OST_GenericModel) and v.CanCategoryBeHidden(cat.Id):
            try:v.SetCategoryHidden(cat.Id,True)
            except:pass
    if box:
        b=DB.BoundingBoxXYZ();b.Min=xyz(*box[:3]);b.Max=xyz(*box[3:]);v.SetSectionBox(b);v.IsSectionBoxActive=True
    return v

def export(doc,view,prefix):
    o=DB.ImageExportOptions();o.ExportRange=DB.ExportRange.SetOfViews
    o.SetViewsAndSheets(List[DB.ElementId]([view.Id]));o.FilePath=os.path.join(OUT,prefix)
    o.HLRandWFViewsFileType=DB.ImageFileType.PNG;o.ShadowViewsFileType=DB.ImageFileType.PNG
    o.ZoomType=DB.ZoomFitType.FitToPage;o.PixelSize=1800
    doc.ExportImage(o)

try:
    app=__revit__.Application
    report['revit_version']=app.VersionNumber;assert app.VersionNumber=='2025'
    report['revit_build']=app.VersionBuild
    check('build family')
    doc=app.NewFamilyDocument(TEMPLATE);docs.append(doc)
    fm=doc.FamilyManager
    tx=DB.Transaction(doc,'Gola parametric profiles');tx.Start()
    fm.NewType(TYPES[0][0])
    for b,val in [(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL,0)]:
        p=doc.OwnerFamily.get_Parameter(b)
        if p and not p.IsReadOnly:p.Set(val)
    params['Length']=next(p for p in fm.Parameters if p.Definition.Name=='Length')
    fm.Set(params['Length'],mm(1000))
    unit=DB.Units(DB.UnitSystem.Metric);doc.SetUnits(unit)
    stainless=next(a for a in app.GetAssets(DB.Visual.AssetType.Appearance) if a.Name=='Metal-029')
    report['appearance_asset']=asset_label(stainless)
    def texture_paths(asset,depth=0):
        result=[]
        if depth>8:return result
        for i in range(asset.Size):
            prop=asset[i]
            if prop.Name=='unifiedbitmap_Bitmap':result.append(str(prop.Value))
            if prop.NumberOfConnectedProperties==1:
                child=prop.GetSingleConnectedAsset()
                if child is not None:result.extend(texture_paths(child,depth+1))
        return result
    report['texture_paths']=texture_paths(stainless)
    m=material(doc,'Gola - Brushed Stainless Finish',(180,184,186),stainless)
    plastic=material(doc,'Gola - Black Plastic Mounting Clips',(36,36,38),cls='Plastic')
    zinc=material(doc,'Gola - Galvanized Bracket',(154,157,158))
    mats={'Profile Material':m,'Cap Material':m,'Mounting Clip Material':plastic,'Bracket Material':zinc}
    for n in mats:add(doc,n,DB.SpecTypeId.Reference.Material,False,DB.GroupTypeId.Materials)
    for n in ['Profile Width','Profile Height','Stock Length']:add(doc,n,DB.SpecTypeId.Length)
    for n in ['Profile Type','Application','Grip Configuration','Manufacturer Product Number','Finish','Base Material',
              'Closed End Cap Product','Open End Cap Product','Internal Joint Product','External Joint Product','Accessory Notes','Model Accuracy Notes']:
        add(doc,n,DB.SpecTypeId.String.Text,False,DB.GroupTypeId.IdentityData)
    opts=['Show Mounting Clips','Show Assembly Bracket','Show Left End Cap','Show Right End Cap',
          'Left End Cap Open','Right End Cap Open','Show Internal 90 Joint','Show External 90 Joint','Bracket As Linear Join']
    for n in opts:add(doc,n,DB.SpecTypeId.Boolean.YesNo,True,DB.GroupTypeId.Visibility)
    add(doc,'Accessory Offset',DB.SpecTypeId.Length,True)
    add(doc,'Effective Accessory Offset',DB.SpecTypeId.Length,True,DB.GroupTypeId.Constraints,
        'if(Accessory Offset < 25 mm, 25 mm, if(Accessory Offset > Length / 2 - 20 mm, Length / 2 - 20 mm, Accessory Offset))')
    for _,key,_,_,_,_ in TYPES:add(doc,'Type '+key,DB.SpecTypeId.Boolean.YesNo,False,DB.GroupTypeId.Constraints)
    cats={}
    for name in ['Channel Profiles','End Caps','Mounting Clips','Assembly Brackets','Corner Joints']:
        cats[name]=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,name)
    geom={};paths={'HC':profile_c(),'HL':profile_l(),'VS':vertical(True),'VD':vertical(False)}
    for name,key,w,h,stock,sku in TYPES:
        check('geometry '+key)
        geom[key]=[]
        for i,path in enumerate(paths[key]):
            geom[key].append(extrusion(doc,key+' channel '+str(i),path,0,'Length','Type '+key,'Profile Material',cats['Channel Profiles']))
        if key not in ['HC','HL']:continue
        # Caps are non-LED series; open-ended caps follow the channel outline.
        for side,idx in [('Left',0),('Right',1)]:
            openvis=bool_formula(doc,key+' '+side+' open','and(Type '+key+', and(Show '+side+' End Cap, '+side+' End Cap Open))')
            closedvis=bool_formula(doc,key+' '+side+' closed','and(Type '+key+', and(Show '+side+' End Cap, not('+side+' End Cap Open)))')
            start,end=(-2,0) if idx==0 else ('Length','Length + 2 mm')
            extrusion(doc,key+' '+side+' closed cap face',rect(0,0,h,w),start,end,closedvis,'Cap Material',cats['End Caps'])
            start,end=(-11,0) if idx==0 else ('Length','Length + 11 mm')
            # Catalog sleeve envelope: C 76 x 29 x 11; L 58 x 29 x 11.
            # Internal sleeve contours remain schematic.
            capheight=76.0 if key=='HC' else 58.0
            def cappt(p):return (p[0]*capheight/h-(capheight-h)/2,p[1]*29.0/w)
            cappath=[('a',cappt(p[1]),cappt(p[2])) if p[0]=='a' else cappt(p) for p in paths[key][0]]
            extrusion(doc,key+' '+side+' open cap',cappath,start,end,openvis,'Cap Material',cats['End Caps'])
            # Closed cap insertion tongue: 8mm internal bearing, schematic.
            start,end=(0,8) if idx==0 else ('Length - 8 mm','Length')
            extrusion(doc,key+' '+side+' closed cap tongue',rect(7,5.3,h-7,7),start,end,closedvis,'Cap Material',cats['End Caps'])
        # BP7001010 plate 40 x 17mm, 3mm thick; 5.3mm dowels at 32mm centers.
        cv=bool_formula(doc,key+' clips','and(Type '+key+', Show Mounting Clips)')
        cy=36.35 if key=='HC' else 18.75
        for sign in [0,1]:
            pos='Effective Accessory Offset' if sign==0 else 'Length - Effective Accessory Offset'
            extrusion(doc,key+' clip plate '+str(sign),rect(cy-20,-12,cy+20,5),pos,pos+' + 3 mm',cv,'Mounting Clip Material',cats['Mounting Clips'])
            for sy in [-16,16]:
                # Circular dowels as two half arcs.
                center=(cy+sy,0.5);r=2.65
                circ=[(center[0]+r,center[1]),('a',(center[0],center[1]+r),(center[0]-r,center[1])),('a',(center[0],center[1]-r),(center[0]+r,center[1]))]
                # Last arc closes; curve builder handles separately below.
                extrusion(doc,key+' clip dowel',circ,pos+' + 3 mm',pos+' + 12.2 mm',cv,'Mounting Clip Material',cats['Mounting Clips'])
            extrusion(doc,key+' clip prong',rect(cy-8,0,cy-2.5,4.3),pos+' - 17 mm',pos,cv,'Mounting Clip Material',cats['Mounting Clips'])
            extrusion(doc,key+' clip prong',rect(cy+2.5,0,cy+8,4.3),pos+' - 17 mm',pos,cv,'Mounting Clip Material',cats['Mounting Clips'])
        bv=bool_formula(doc,key+' bracket bent','and(Type '+key+', and(Show Assembly Bracket, not(Bracket As Linear Join)))')
        bl=bool_formula(doc,key+' bracket linear','and(Type '+key+', and(Show Assembly Bracket, Bracket As Linear Join))')
        extrusion(doc,key+' bracket 90 arm',rect(cy-5.5,1.5,cy+5.5,3.9), 'Length - 68 mm','Length',bv,'Bracket Material',cats['Assembly Brackets'])
        extrusion(doc,key+' bracket 90 return',rect(cy-5.5,-34.1,cy+5.5,3.9),'Length - 2.4 mm','Length',bv,'Bracket Material',cats['Assembly Brackets'])
        extrusion(doc,key+' bracket straight join',rect(cy-5.5,1.5,cy+5.5,3.9),'Length - 34 mm','Length + 34 mm',bl,'Bracket Material',cats['Assembly Brackets'])
        # 29mm internal at start; 27mm external at finish. Junction solids
        # are dimensioned schematic fittings, not long perpendicular runs.
        iv=bool_formula(doc,key+' internal joint','and(Type '+key+', Show Internal 90 Joint)')
        ev=bool_formula(doc,key+' external joint','and(Type '+key+', Show External 90 Joint)')
        for vis,base,size,inward in [(iv,None,29,True),(ev,'Length',27,False)]:
            def xp(offset):return offset if base is None else (base+' + '+str(offset)+' mm')
            a=-size if inward else 0;b=0 if inward else size
            back=5.3 if inward else w-1.2
            extrusion(doc,key+' corner web along run',rect(5,back,h-5,back+1.2),xp(a),xp(b),vis,'Profile Material',cats['Corner Joints'])
            edge=a if inward else b-1.2
            extrusion(doc,key+' corner return web',rect(5,back,h-5,back+size-1.2) if inward else rect(5,back-size+1.2,h-5,back),xp(edge),xp(edge+1.2),vis,'Profile Material',cats['Corner Joints'])
            for y in ([3.8,h-5] if key=='HC' else [3.9]):
                extrusion(doc,key+' corner flange',rect(y,back if inward else back-size+1.2,y+1.2,back+size if inward else back+1.2),xp(a),xp(b),vis,'Profile Material',cats['Corner Joints'])
    for i,(name,key,w,h,stock,sku) in enumerate(TYPES):
        if i:fm.NewType(name)
        for _,k,_,_,_,_ in TYPES:fm.Set(params['Type '+k],1 if k==key else 0)
        for n,v in [('Profile Width',w),('Profile Height',h),('Stock Length',stock),('Length',1000),('Accessory Offset',50)]:fm.Set(params[n],mm(v))
        for n,v in mats.items():fm.Set(params[n],v.Id)
        for n in opts:fm.Set(params[n],1 if n=='Show Mounting Clips' and key[0]=='H' else 0)
        info={'Profile Type':key,'Application':'Horizontal' if key[0]=='H' else 'Vertical',
              'Grip Configuration':'Double' if key in ['HC','VD'] else 'Single','Manufacturer Product Number':sku,
              'Finish':'Brushed stainless steel appearance','Base Material':'Anodized aluminum',
              'Closed End Cap Product':'7001046170' if key=='HC' else ('7001044170' if key=='HL' else 'Not specified for vertical profiles'),
              'Open End Cap Product':'7001045170' if key=='HC' else ('7001013170' if key=='HL' else 'Not specified for vertical profiles'),
              'Internal Joint Product':'7001016I170' if key=='HC' else ('7001017I170' if key=='HL' else 'Not applicable'),
              'External Joint Product':'7001016E170' if key=='HC' else ('7001015E170' if key=='HL' else 'Not applicable'),
              'Accessory Notes':'Horizontal: BP7001010 clips; 70010999 bracket. Internal joint at START, external at END. Disable end cap where corner used. Vertical: direct screw fixing; horizontal fittings suppressed.',
              'Model Accuracy Notes':'Source overall sections: C 26x72.7; L 27x56; vertical single 48.25x36.6; double 66.5x36.6mm. Undimensioned small radii/thickness, teeth and accessory internals simplified. Stock vertical drawing 4400mm; website packaging sometimes states 4500mm.'}
        for n,v in info.items():fm.Set(params[n],v)
        for b,v in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'Richelieu Hardware'),(DB.BuiltInParameter.ALL_MODEL_MODEL,sku),(DB.BuiltInParameter.ALL_MODEL_URL,URL),(DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,name+'; line based length with endpoint grips')]:
            p=fm.get_Parameter(b)
            if p:fm.Set(p,v)
        doc.Regenerate()
    fm.CurrentType=next(t for t in fm.Types if t.Name==TYPES[0][0])
    pv=preview(doc,'Gola Profile Review',xyz(1500,1000,1000),DB.XYZ.BasisY,xyz(500,36,12))
    tx.Commit();tx=None
    check('save and reopen family')
    so=DB.SaveAsOptions();so.OverwriteExistingFile=True;so.MaximumBackups=1;so.PreviewViewId=pv.Id
    doc.SaveAs(RFA,so);doc.Close(False);docs.remove(doc)
    doc=app.OpenDocumentFile(RFA);docs.append(doc)
    report['reopened']=doc.IsFamilyDocument
    report['placement']=str(doc.OwnerFamily.FamilyPlacementType)
    report['family_warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    report['length_is_instance']=next(p for p in doc.FamilyManager.Parameters if p.Definition.Name=='Length').IsInstance
    report['endpoint_references']=[p.Name for p in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane) if p.Name in ['Left','Right']]
    check('placement and flex tests')
    pr=app.NewProjectDocument(DB.UnitSystem.Metric);docs.append(pr)
    fam=doc.LoadFamily(pr)
    symbols={pr.GetElement(i).get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString():pr.GetElement(i) for i in fam.GetFamilySymbolIds()}
    tx=DB.Transaction(pr,'Gola placement verification');tx.Start()
    level=next(iter(DB.FilteredElementCollector(pr).OfClass(DB.Level)),None)
    if not level:level=DB.Level.Create(pr,0)
    sk=DB.SketchPlane.Create(pr,DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisZ,DB.XYZ.Zero))
    checkview=preview(pr,'Gola All Four Profiles',xyz(2500,-1700,2500),DB.XYZ.BasisZ,xyz(600,450,0))
    instances=[]
    for i,(name,key,w,h,stock,sku) in enumerate(TYPES):
        sym=symbols[name];sym.Activate();pr.Regenerate()
        line=DB.Line.CreateBound(xyz(0,i*220,0),xyz(1000,i*220,0))
        inst=pr.Create.NewFamilyInstance(line,sym,level,DB.Structure.StructuralType.NonStructural)
        instances.append(inst);pr.Regenerate()
        for n in opts:inst.LookupParameter(n).Set(0)
        r={'name':name,'key':key,'flex':[],'accessories':[], 'native_length_readonly':inst.LookupParameter('Length').IsReadOnly}
        for length in [600,2400,1000]:
            set_length(inst,length);pr.Regenerate()
            ss=visible_solids(inst,checkview);b=extents(ss,inst.GetTransform().Inverse)
            actual=b[3]-b[0]
            r['flex'].append({'requested':length,'measured':actual,'section':b})
            assert abs(actual-length)<0.1,(name,'length',actual)
            assert abs(inst.LookupParameter('Length').AsDouble()*304.8-length)<0.1
        # Both endpoint changes use the same native location curve as grips.
        for endidx in [0,1]:
            c=inst.Location.Curve;p0=c.GetEndPoint(0);p1=c.GetEndPoint(1)
            if endidx==0:p0=p0.Subtract(xyz(100,0,0))
            else:p1=p1.Add(xyz(150,0,0))
            inst.Location.Curve=DB.Line.CreateBound(p0,p1);pr.Regenerate()
            actual=extents(visible_solids(inst,checkview),inst.GetTransform().Inverse)
            assert abs((actual[3]-actual[0])-inst.Location.Curve.Length*304.8)<0.1
        r['both_endpoint_edits']=True
        set_length(inst,1000);pr.Regenerate()
        for n in ['Show Mounting Clips','Show Assembly Bracket','Show Left End Cap','Show Right End Cap','Show Internal 90 Joint','Show External 90 Joint']:
            basevol=sum(s.Volume for s in visible_solids(inst,checkview))
            inst.LookupParameter(n).Set(1);pr.Regenerate()
            newvol=sum(s.Volume for s in visible_solids(inst,checkview))
            delta=(newvol-basevol)*304.8**3
            r['accessories'].append({'name':n,'added_volume_mm3':delta})
            assert (delta>0.1) if key[0]=='H' else abs(delta)<0.1,(key,n,delta)
            inst.LookupParameter(n).Set(0);pr.Regenerate()
        if key[0]=='H':
            inst.LookupParameter('Show Right End Cap').Set(1)
            for length in [600,2400]:
                set_length(inst,length);pr.Regenerate()
                b=extents(visible_solids(inst,checkview),inst.GetTransform().Inverse)
                assert abs(b[3]-length-2)<0.1,(key,'cap follow',b)
            r['end_cap_follows_length']=True
            inst.LookupParameter('Right End Cap Open').Set(1);pr.Regenerate()
            b=extents(visible_solids(inst,checkview),inst.GetTransform().Inverse)
            assert abs(b[3]-2411)<0.1
            inv=inst.GetTransform().Inverse
            capsolids=[s for s in visible_solids(inst,checkview) if inv.OfPoint(s.ComputeCentroid()).X>mm(2400)]
            cb=extents(capsolids,inv)
            r['open_cap_envelope_mm']=[cb[3]-cb[0],cb[4]-cb[1],cb[5]-cb[2]]
            for actual,expected in zip(r['open_cap_envelope_mm'],[11,76 if key=='HC' else 58,29]):assert abs(actual-expected)<0.1
            r['open_cap_test']=True
            inst.LookupParameter('Right End Cap Open').Set(0);inst.LookupParameter('Show Right End Cap').Set(0)
        original=sym.LookupParameter('Profile Material').AsElementId()
        alt=DB.Material.Create(pr,'QA alternate '+key)
        sym.LookupParameter('Profile Material').Set(alt);pr.Regenerate()
        assert all(f.MaterialElementId==alt for s in visible_solids(inst,checkview) for f in s.Faces)
        sym.LookupParameter('Profile Material').Set(original);r['material_test']=True
        set_length(inst,1000);pr.Regenerate()
        report['types'].append(r)
    tx.Commit();tx=None
    check('vertical work plane placement')
    tx=DB.Transaction(pr,'Vertical face line placement');tx.Start()
    walltype=next(w for w in DB.FilteredElementCollector(pr).OfClass(DB.WallType) if w.Kind==DB.WallKind.Basic)
    wall=DB.Wall.Create(pr,DB.Line.CreateBound(xyz(0,1800,0),xyz(1800,1800,0)),walltype.Id,level.Id,mm(2600),0,False,False)
    pr.Regenerate();ref=DB.HostObjectUtils.GetSideFaces(wall,DB.ShellLayerType.Exterior)[0]
    face=wall.GetGeometryObjectFromReference(ref)
    verts=[]
    for i,key in enumerate(['VS','VD']):
        sym=symbols[TYPES[2+i][0]]
        p0=face.Project(xyz(400+i*650,1800,150)).XYZPoint;p1=p0.Add(xyz(0,0,2100))
        vi=pr.Create.NewFamilyInstance(ref,DB.Line.CreateBound(p0,p1),sym);verts.append(vi);pr.Regenerate()
        assert isinstance(vi.Location,DB.LocationCurve)
        vi.Location.Curve=DB.Line.CreateBound(p0,p1.Add(xyz(0,0,100)));pr.Regenerate()
        bb=extents(visible_solids(vi,checkview),vi.GetTransform().Inverse)
        assert abs(bb[3]-bb[0]-2200)<0.1
    report['vertical_face_placement']=True
    normal=verts[0].GetTransform().BasisZ
    target=verts[0].Location.Curve.Evaluate(0.5,True).Add(xyz(325,0,0))
    report['vertical_surface_normal']=[face.FaceNormal.X,face.FaceNormal.Y,face.FaceNormal.Z]
    report['vertical_family_normal']=[normal.X,normal.Y,normal.Z]
    eye=target.Add(normal.Multiply(mm(4000))).Add(xyz(1800,0,500))
    vview=preview(pr,'Vertical Installation',eye,DB.XYZ.BasisZ,target,[-100,1000,-100,1900,2200,2600])
    report['vertical_camera_faces_profile']=eye.Subtract(target).DotProduct(normal)>0
    vv=DB.ElementId(DB.BuiltInCategory.OST_Walls)
    if vview.CanCategoryBeHidden(vv):vview.SetCategoryHidden(vv,False)
    # Separate views isolate each type for cross-section and proportion review.
    views=[]
    for i,inst in enumerate(instances):
        y=i*220
        v=preview(pr,TYPES[i][1]+' Profile',xyz(-400,y+220,400),DB.XYZ.BasisY,xyz(500,y+30,15),[-150,y-10,-10,1100,y+100,100])
        hidden=[j.Id for j in instances+verts if j.Id!=inst.Id]
        v.HideElements(List[DB.ElementId](hidden))
        views.append(v)
    allview=checkview
    allview.HideElements(List[DB.ElementId]([v.Id for v in verts]))
    for i in [0,1]:
        instances[i].LookupParameter('Show Mounting Clips').Set(1)
        instances[i].LookupParameter('Show Left End Cap').Set(1)
        instances[i].LookupParameter('Show Right End Cap').Set(1)
    tx.Commit();tx=None
    report['project_warnings']=[w.GetDescriptionText() for w in pr.GetWarnings()]
    so=DB.SaveAsOptions();so.OverwriteExistingFile=True;so.MaximumBackups=1;so.PreviewViewId=allview.Id
    pr.SaveAs(RVT,so)
    check('export previews')
    for v in views+[allview,vview]:export(pr,v,'Gola')
    report['previews']=[os.path.join(OUT,n) for n in os.listdir(OUT) if n.endswith('.png')]
    report['success']=True
    check('complete')
except:
    report['error']=traceback.format_exc();check('failed '+report['stage'])
finally:
    if tx:
        try:tx.RollBack()
        except:pass
    for d in reversed(docs):
        try:d.Close(False)
        except:pass
