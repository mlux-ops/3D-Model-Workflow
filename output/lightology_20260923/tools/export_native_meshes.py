# -*- coding: utf-8 -*-
"""Read-only extraction of actual saved RFA geometry and appearance evidence."""
import os,json,gzip,re,hashlib,datetime,traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOSTS={'f01':'ceiling','f02':'wall','f03':'wall','f04':'ceiling','f05':'wall','f06':'ceiling','f07':'wall','f08':'ceiling','f09':'wall','f10':'ceiling','f11':'ceiling','f12':'wall'}

def solids(geometry):
    if geometry is None:return
    for item in geometry:
        if isinstance(item,DB.Solid) and item.Volume>1e-12:yield item
        elif isinstance(item,DB.GeometryInstance):
            for s in solids(item.GetInstanceGeometry()):yield s

def appearance(doc,mat):
    data={'name':mat.Name,'class':mat.MaterialClass,'rgb':[int(mat.Color.Red)/255.,int(mat.Color.Green)/255.,int(mat.Color.Blue)/255.],'graphics_transparency':mat.Transparency/100.}
    ae=doc.GetElement(mat.AppearanceAssetId)
    if ae is None:return data
    a=ae.GetRenderingAsset()
    for name in ['generic_diffuse','generic_glossiness','generic_transparency','generic_reflectivity_at_0deg','generic_reflectivity_at_90deg','generic_is_metal','generic_refraction_index','generic_self_illum_luminance','generic_self_illum_color_temperature','generic_self_illum_filter_map']:
        p=a.FindByName(name)
        if p is None:continue
        try:value=p.Value
        except Exception:
            try:value=[float(x) for x in p.GetValueAsDoubles()]
            except Exception:continue
        data[name]=value
        if name in ['generic_diffuse','generic_self_illum_filter_map'] and p.NumberOfConnectedProperties:
            b=p.GetSingleConnectedAsset();bp=b.FindByName('unifiedbitmap_Bitmap')
            if bp is not None:
                data['bitmap' if name=='generic_diffuse' else 'emission_bitmap']=bp.Value
                data['bitmap_exists' if name=='generic_diffuse' else 'emission_bitmap_exists']=os.path.isfile(bp.Value)
            for key in ['texture_RealWorldScaleX','texture_RealWorldScaleY']:
                prop=b.FindByName(key)
                if prop is not None:data[key]=float(prop.Value)
    return data

index=[]
for folder in sorted(os.listdir(ROOT)):
    if folder[:3] not in HOSTS or not os.path.isdir(os.path.join(ROOT,folder)):continue
    filenames=list(os.listdir(os.path.join(ROOT,folder)))
    native_dir=os.path.join(ROOT,folder,'native')
    if os.path.isdir(native_dir):filenames.extend(os.path.join('native',n) for n in os.listdir(native_dir))
    for filename in sorted(filenames):
        if not filename.lower().endswith('.rfa') or re.search(r'\.\d{4}\.rfa$',filename,re.I):continue
        path=os.path.join(ROOT,folder,filename);doc=None
        row={'rfa':path,'folder':folder,'host':HOSTS[folder[:3]],'name':os.path.splitext(os.path.basename(filename))[0]}
        try:
            doc=__revit__.Application.OpenDocumentFile(path)
            row['sha256']=hashlib.sha256(open(path,'rb').read()).hexdigest()
            data={'source':row.copy(),'units':'metres','materials':{},'parts':[]}
            opt=DB.Options();opt.DetailLevel=DB.ViewDetailLevel.Fine
            for element in DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement):
                p=element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM)
                fallback=p.AsElementId() if p is not None else DB.ElementId.InvalidElementId
                for si,solid in enumerate(solids(element.get_Geometry(opt))):
                    vertices=[];normals=[];triangles=[];mat_ids=[]
                    for face in solid.Faces:
                        material_id=face.MaterialElementId
                        if material_id==DB.ElementId.InvalidElementId:material_id=fallback
                        key=str(material_id.Value);material=doc.GetElement(material_id)
                        if material is not None and key not in data['materials']:data['materials'][key]=appearance(doc,material)
                        mesh=face.Triangulate(1.0);lookup={};base=len(vertices)
                        for vi in range(mesh.Vertices.Count):
                            v=mesh.Vertices[vi];lookup[(round(v.X,9),round(v.Y,9),round(v.Z,9))]=base+vi
                            vertices.append([v.X*.3048,v.Y*.3048,v.Z*.3048])
                            projection=face.Project(v)
                            uv=projection.UVPoint if projection is not None else (face.GetBoundingBox().Min+face.GetBoundingBox().Max)*.5
                            n=face.ComputeNormal(uv);normals.append([n.X,n.Y,n.Z])
                        for ti in range(mesh.NumTriangles):
                            tr=mesh.get_Triangle(ti);ids=[]
                            for j in range(3):
                                v=tr.get_Vertex(j);ids.append(lookup[(round(v.X,9),round(v.Y,9),round(v.Z,9))])
                            triangles.append(ids);mat_ids.append(key)
                    data['parts'].append({'element':int(element.Id.Value),'solid':si,'vertices':vertices,'normals':normals,'triangles':triangles,'material_ids':mat_ids})
            if not data['parts']:raise RuntimeError('Saved family contained no exportable FreeFormElement geometry')
            outdir=os.path.join(ROOT,folder,'evidence')
            if not os.path.isdir(outdir):os.makedirs(outdir)
            target=os.path.join(outdir,row['name']+'_NativeMesh.json.gz')
            with gzip.open(target,'wb') as g:g.write(json.dumps(data,separators=(',',':'),default=str).encode('utf8'))
            row['mesh']=target;row['parts']=len(data['parts']);row['triangles']=sum(len(p['triangles']) for p in data['parts']);row['success']=True
        except Exception:
            row['success']=False;row['error']=traceback.format_exc()
            with open(os.path.join(os.path.dirname(os.path.dirname(ROOT)),'PROJECT_MEMORY.md'),'a') as log:log.write('\n- Native mesh export error '+folder+': '+row['error'].replace('\n',' ')+'; unresolved pending diagnostic.\n')
        finally:
            if doc is not None:doc.Close(False)
        index.append(row)
        with open(os.path.join(ROOT,'native_mesh_index.json'),'w') as stream:json.dump(index,stream,indent=2)