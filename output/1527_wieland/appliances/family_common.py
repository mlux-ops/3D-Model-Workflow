# -*- coding: utf-8 -*-
"""Native Revit 2025 appliance geometry, material and validation helpers."""
import os
import math
import json
import glob
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = os.path.dirname(os.path.abspath(__file__))
MM = 304.8

def ename(e):
    return e.Name if isinstance(e,DB.Category) else DB.Element.Name.__get__(e)

def clean(value):
    if isinstance(value, str):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('cp1252', 'replace')
    if isinstance(value, dict):
        return dict((clean(k), clean(v)) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, float) and (math.isinf(value) or math.isnan(value)):
        return None
    return value

def write_json(path, data):
    # IronPython's JSON encoder can attempt a code-page decode even after a
    # System.String was converted. Escape code points before the encoder sees it.
    def quote(value):
        value=value if isinstance(value,basestring) else str(value)
        out=[]
        for ch in value:
            code=ord(ch)
            if 32<=code<127 and ch not in ('"','\\'):
                out.append(ch)
            elif code<=65535:
                out.append('\\u%04x'%code)
            else:
                code-=65536
                out.append('\\u%04x\\u%04x'%(55296+(code>>10),56320+(code&1023)))
        return '"'+''.join(out)+'"'
    def encode(value,depth=0):
        if value is None:
            return 'null'
        if isinstance(value,bool):
            return 'true' if value else 'false'
        if isinstance(value,(int,long)):
            return str(value)
        if isinstance(value,float):
            return 'null' if math.isinf(value) or math.isnan(value) else repr(value)
        pad='  '*(depth+1)
        close='  '*depth
        if isinstance(value,dict):
            return '{\n'+',\n'.join(pad+quote(k)+': '+encode(v,depth+1) for k,v in value.items())+'\n'+close+'}'
        if isinstance(value,(list,tuple)):
            return '[\n'+',\n'.join(pad+encode(v,depth+1) for v in value)+'\n'+close+']'
        return quote(value)
    payload=encode(data)
    with open(path, 'w') as handle:
        handle.write(payload)

def xyz(x, y, z):
    return DB.XYZ(x/MM, y/MM, z/MM)

def loop(points):
    result = DB.CurveLoop()
    for a, b in zip(points, points[1:] + points[:1]):
        result.Append(DB.Line.CreateBound(xyz(*a), xyz(*b)))
    return result

def prism(points, direction, distance):
    return DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop(points)]), direction, distance/MM)

def box(x0,y0,z0,x1,y1,z1):
    return prism([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)],DB.XYZ.BasisZ,z1-z0)

def circle_loop(center, radius, direction):
    c=xyz(*center)
    axis=DB.XYZ(*direction).Normalize()
    u=DB.XYZ.BasisX if abs(axis.X)<0.9 else DB.XYZ.BasisY
    v=axis.CrossProduct(u).Normalize()
    result=DB.CurveLoop()
    for i in range(4):
        result.Append(DB.Arc.Create(c, radius/MM, i*math.pi/2, (i+1)*math.pi/2, u, v))
    return result

def cylinder(center,radius,length,direction=(0,0,1),inner=0):
    curves=[circle_loop(center,radius,direction)]
    if inner:
        curves.append(circle_loop(center,inner,direction))
    return DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop](curves),DB.XYZ(*direction),length/MM)

def rounded_front(x0,z0,x1,z1,radius,y,depth):
    r=radius
    # X/Z rounded rectangle, extruded toward the back (+Y).
    pts=[(x0+r,z0),(x1-r,z0),(x1,z0+r),(x1,z1-r),(x1-r,z1),(x0+r,z1),(x0,z1-r),(x0,z0+r)]
    mids=[(x1-r+r/math.sqrt(2),z0+r-r/math.sqrt(2)),
          (x1-r+r/math.sqrt(2),z1-r+r/math.sqrt(2)),
          (x0+r-r/math.sqrt(2),z1-r+r/math.sqrt(2)),
          (x0+r-r/math.sqrt(2),z0+r-r/math.sqrt(2))]
    cr=DB.CurveLoop()
    for i in range(8):
        a,b=pts[i],pts[(i+1)%8]
        if i%2:
            m=mids[i//2]
            cr.Append(DB.Arc.Create(xyz(a[0],y,a[1]),xyz(b[0],y,b[1]),xyz(m[0],y,m[1])))
        else:
            cr.Append(DB.Line.CreateBound(xyz(a[0],y,a[1]),xyz(b[0],y,b[1])))
    return DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([cr]),DB.XYZ.BasisY,depth/MM)

def material(doc,app,name,rgb,gloss=0.3,transparency=0.0,bitmap=None):
    assets=app.GetAssets(DB.Visual.AssetType.Appearance)
    source=next(a for a in assets if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value=='GenericSchema')
    appearance=DB.AppearanceAssetElement.Create(doc,name,source)
    mat=doc.GetElement(DB.Material.Create(doc,name))
    mat.AppearanceAssetId=appearance.Id
    mat.Color=DB.Color(*rgb)
    mat.Transparency=int(transparency*100)
    scope=DB.Visual.AppearanceAssetEditScope(doc)
    asset=scope.Start(appearance.Id)
    diffuse=asset.FindByName('generic_diffuse')
    if diffuse.NumberOfConnectedProperties:
        diffuse.RemoveConnectedAsset()
    diffuse.SetValueAsColor(DB.Color(*rgb))
    if bitmap:
        diffuse.AddConnectedAsset('UnifiedBitmap')
        connected=diffuse.GetSingleConnectedAsset()
        connected.FindByName('unifiedbitmap_Bitmap').Value=bitmap
    for key,value in [('generic_glossiness',gloss),('generic_reflectivity_at_0deg',0.1),('generic_reflectivity_at_90deg',0.65),('generic_transparency',transparency)]:
        prop=asset.FindByName(key)
        if prop is not None:
            if prop.NumberOfConnectedProperties:
                prop.RemoveConnectedAsset()
            prop.Value=value
    scope.Commit(True)
    scope.Dispose()
    return mat

def mat_parameter(doc,name,mat):
    fm=doc.FamilyManager
    p=fm.AddParameter(name,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False)
    fm.Set(p,mat.Id)
    return p

def bind(doc,solid,name,param,parts):
    element=DB.FreeFormElement.Create(doc,solid)
    subcat=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,name)
    element.Subcategory=subcat
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),param)
    parts.append({'name':name,'id':int(element.Id.Value),'parameter':param.Definition.Name})
    return element

def points(geometry):
    if geometry is None:
        return
    for g in geometry:
        if isinstance(g,DB.GeometryInstance):
            for p in points(g.GetInstanceGeometry()):
                yield p
        elif isinstance(g,DB.Solid) and g.Volume>1e-10:
            for face in g.Faces:
                mesh=face.Triangulate(1.0)
                if mesh:
                    for p in mesh.Vertices:
                        yield p
                else:
                    for edge_loop in face.EdgeLoops:
                        for edge in edge_loop:
                            for p in edge.Tessellate():
                                yield p
        elif isinstance(g,DB.Mesh):
            for p in g.Vertices:
                yield p

def measure(elements):
    opt=DB.Options()
    opt.DetailLevel=DB.ViewDetailLevel.Fine
    opt.IncludeNonVisibleObjects=False
    lo=[float('inf')]*3
    hi=[float('-inf')]*3
    parts=[]
    for e in elements:
        pp=list(points(e.get_Geometry(opt)))
        if not pp:
            continue
        rows=[[p.X*MM,p.Y*MM,p.Z*MM] for p in pp]
        mn=[min(p[i] for p in rows) for i in range(3)]
        mx=[max(p[i] for p in rows) for i in range(3)]
        lo=[min(lo[i],mn[i]) for i in range(3)]
        hi=[max(hi[i],mx[i]) for i in range(3)]
        parts.append({'id':int(e.Id.Value),'class':e.GetType().Name,'min_mm':mn,'max_mm':mx,
                      'name':ename(e.Subcategory) if isinstance(e,DB.GenericForm) and e.Subcategory else ename(e)})
    return {'min_mm':lo,'max_mm':hi,'xyz_size_mm':[hi[i]-lo[i] for i in range(3)],'parts':parts}

def export_view(doc,folder,name,bounds,forward=(-1,1.5,-0.7),category_id=None):
    tx=DB.Transaction(doc,'Appliance preview '+name)
    tx.Start()
    vt=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    view=DB.View3D.CreateIsometric(doc,vt.Id)
    view.Name=name
    lo,hi=bounds['min_mm'],bounds['max_mm']
    target=xyz(*[(lo[i]+hi[i])/2 for i in range(3)])
    fwd=DB.XYZ(*forward).Normalize()
    up=fwd.CrossProduct(DB.XYZ.BasisZ).Normalize().CrossProduct(fwd).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(target.Subtract(fwd.Multiply(15)),up,fwd))
    view.DetailLevel=DB.ViewDetailLevel.Fine
    view.DisplayStyle=DB.DisplayStyle.Shading
    for c in doc.Settings.Categories:
        try:
            hide=(c.CategoryType==DB.CategoryType.Annotation or c.Name in ('Floors','Levels','Grids') or 'connector' in c.Name.lower())
            if hide and c.Id!=category_id and view.CanCategoryBeHidden(c.Id):
                view.SetCategoryHidden(c.Id,True)
        except Exception:
            pass
    section=DB.BoundingBoxXYZ()
    section.Min=xyz(*[v-10 for v in lo])
    section.Max=xyz(*[v+10 for v in hi])
    view.SetSectionBox(section)
    view.IsSectionBoxActive=True
    tx.Commit()
    if not os.path.isdir(folder):
        os.makedirs(folder)
    opts=DB.ImageExportOptions()
    opts.ExportRange=DB.ExportRange.SetOfViews
    opts.SetViewsAndSheets(List[DB.ElementId]([view.Id]))
    opts.FilePath=os.path.join(folder,name)
    opts.HLRandWFViewsFileType=DB.ImageFileType.PNG
    opts.ShadowViewsFileType=DB.ImageFileType.PNG
    opts.ZoomType=DB.ZoomFitType.FitToPage
    opts.PixelSize=1400
    doc.ExportImage(opts)
    return glob.glob(os.path.join(folder,name+'*.png'))

def place_family(app,path):
    project=app.NewProjectDocument(DB.UnitSystem.Imperial)
    tx=DB.Transaction(project,'Place appliance for validation')
    tx.Start()
    level=DB.Level.Create(project,0)
    ref=clr.Reference[DB.Family]()
    loaded=project.LoadFamily(path,ref)
    family=ref.Value
    symbols=[project.GetElement(e) for e in family.GetFamilySymbolIds()]
    symbol=next((s for s in symbols if ename(s).strip()),symbols[0])
    symbol.Activate()
    project.Regenerate()
    host=None
    if family.FamilyPlacementType==DB.FamilyPlacementType.WorkPlaneBased:
        floor_type=DB.FilteredElementCollector(project).OfClass(DB.FloorType).FirstElement()
        footprint=loop([(-2000,-2000,0),(2000,-2000,0),(2000,3000,0),(-2000,3000,0)])
        host=DB.Floor.Create(project,List[DB.CurveLoop]([footprint]),floor_type.Id,level.Id)
        project.Regenerate()
        surface=DB.HostObjectUtils.GetTopFaces(host)[0]
        instance=project.Create.NewFamilyInstance(surface,DB.XYZ.Zero,DB.XYZ.BasisX,symbol)
    else:
        instance=project.Create.NewFamilyInstance(DB.XYZ.Zero,symbol,level,DB.Structure.StructuralType.NonStructural)
    project.Regenerate()
    tx.Commit()
    return project,instance,{'loaded':loaded,'placed':True,'type':ename(symbol),'placement_type':str(family.FamilyPlacementType),
                             'host_category':host.Category.Name if host else 'Level','family_category':family.FamilyCategory.Name}
