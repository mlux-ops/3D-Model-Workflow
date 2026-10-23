# -*- coding: utf-8 -*-
"""Native Revit helpers for the recovered Lightology fixture builds.
All geometry dimensions are inches; native internal lengths are feet.
Only task-owned family and disposable QA documents are modified.
"""
import os, math, json, datetime, traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'

def xyz(x=0,y=0,z=0):
    return DB.XYZ(float(x)/12,float(y)/12,float(z)/12)

def loop(origin,u,v,points):
    def at(p): return origin.Add(u.Multiply(p[0]/12.0)).Add(v.Multiply(p[1]/12.0))
    result=DB.CurveLoop(); current=points[0]
    for step in points[1:]:
        if len(step)==3 and step[0]=='arc':
            middle,end=step[1],step[2]
            result.Append(DB.Arc.Create(at(current),at(end),at(middle)))
        else:
            end=step
            if abs(end[0]-current[0])+abs(end[1]-current[1])>1e-8:
                result.Append(DB.Line.CreateBound(at(current),at(end)))
        current=end
    if abs(current[0]-points[0][0])+abs(current[1]-points[0][1])>1e-8:
        result.Append(DB.Line.CreateBound(at(current),at(points[0])))
    return result

def rounded_rect(x0,y0,x1,y1,r):
    k=1-math.sqrt(.5)
    return [(x0+r,y0),(x1-r,y0),('arc',(x1-r*k,y0+r*k),(x1,y0+r)),(x1,y1-r),
            ('arc',(x1-r*k,y1-r*k),(x1-r,y1)),(x0+r,y1),
            ('arc',(x0+r*k,y1-r*k),(x0,y1-r)),(x0,y0+r),('arc',(x0+r*k,y0+r*k),(x0+r,y0))]

def revolve_solid(origin,axis,profile):
    axis=axis.Normalize()
    radial=DB.XYZ.BasisX if abs(axis.X)<.9 else DB.XYZ.BasisY
    radial=radial.Subtract(axis.Multiply(radial.DotProduct(axis))).Normalize()
    frame=DB.Frame(origin,radial,axis.CrossProduct(radial),axis)
    return DB.GeometryCreationUtilities.CreateRevolvedGeometry(frame,List[DB.CurveLoop]([loop(origin,radial,axis,profile)]),0,math.pi*2)

def cylinder_solid(origin,axis,r,a,b,rounding=0):
    if rounding:
        q=rounding;k=1-math.sqrt(.5)
        p=[(0,a),(r-q,a),('arc',(r-q*k,a+q*k),(r,a+q)),(r,b-q),('arc',(r-q*k,b-q*k),(r-q,b)),(0,b)]
    else: p=[(0,a),(r,a),(r,b),(0,b)]
    return revolve_solid(origin,axis,p)

def sphere_solid(center,r):
    return revolve_solid(center,DB.XYZ.BasisZ,[(0,-r),('arc',(r,0),(0,r))])

def all_solids(geometry):
    if geometry is None: return
    for item in geometry:
        if isinstance(item,DB.Solid) and item.Volume>1e-12: yield item
        elif isinstance(item,DB.GeometryInstance):
            for solid in all_solids(item.GetInstanceGeometry()): yield solid

def element_bounds(elements):
    boxes=[e.get_BoundingBox(None) for e in elements]
    boxes=[b for b in boxes if b is not None]
    if not boxes: raise RuntimeError('No geometry bounds')
    return [min(b.Min.X for b in boxes)*12,min(b.Min.Y for b in boxes)*12,min(b.Min.Z for b in boxes)*12,
            max(b.Max.X for b in boxes)*12,max(b.Max.Y for b in boxes)*12,max(b.Max.Z for b in boxes)*12]

def measured_geometry_bounds(elements):
    """Measure native surfaces/analytic edges rather than display tessellation boxes."""
    points=[]
    options=DB.Options();options.DetailLevel=DB.ViewDetailLevel.Fine
    for element in elements:
        for solid in all_solids(element.get_Geometry(options)):
            for face in solid.Faces:
                points.extend(list(face.Triangulate(1.0).Vertices))
            for edge in solid.Edges:
                curve=edge.AsCurve()
                count=1 if isinstance(curve,DB.Line) else 128
                points.extend(curve.Evaluate(float(i)/count,True) for i in range(count+1))
    if not points:raise RuntimeError('No native geometry for measurement')
    return [min(p.X for p in points)*12,min(p.Y for p in points)*12,min(p.Z for p in points)*12,
            max(p.X for p in points)*12,max(p.Y for p in points)*12,max(p.Z for p in points)*12]
class NativeFixture(object):
    def __init__(self, app, out, basename, manufacturer, model, type_name, host, dimensions, cct=None):
        self.app=app; self.out=out; self.basename=basename; self.host=host; self.expected=dimensions; self.cct=cct
        if not os.path.isdir(out): os.makedirs(out)
        self.evidence=os.path.join(out,'evidence')
        if not os.path.isdir(self.evidence): os.makedirs(self.evidence)
        self.path=os.path.join(out,basename+'.rfa'); self.report_path=os.path.join(out,basename+'_validation.json')
        self.report={'rfa_path':self.path,'model':model,'manufacturer':manufacturer,'type':type_name,'revit_version':app.VersionNumber,
                     'revit_build':app.VersionBuild,'started_utc':datetime.datetime.utcnow().isoformat()+'Z','technical_pass':False,'expected_dimensions_in':dimensions,'cct_k':cct}
        self.docs=[]; self.tx=None; self.forms=[]; self.parameters={}; self.materials={}; self.parts=[]
        self.checkpoint('create_face_family')
        if app.VersionNumber!='2025': raise RuntimeError('This build requires Revit 2025')
        self.doc=app.NewFamilyDocument(TEMPLATE); self.docs.append(self.doc)
        self.template_form_ids=[e.Id for e in DB.FilteredElementCollector(self.doc).OfClass(DB.GenericForm)]
        self.tx=DB.Transaction(self.doc,'Build '+model); self.tx.Start()
        self.doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(self.doc,DB.BuiltInCategory.OST_LightingFixtures)
        self.doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
        self.fm=self.doc.FamilyManager; self.fm.NewType(type_name)
        for bip,value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,manufacturer),(DB.BuiltInParameter.ALL_MODEL_MODEL,model),
                          (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'Face-based visualization family; dimensioned product geometry with documented inferred details')]:
            p=self.fm.get_Parameter(bip)
            if p is not None: self.fm.Set(p,value)
        for label,val in zip(['Model Width','Model Height' if host=='wall' else 'Model Depth','Projection' if host=='wall' else 'Total Drop'],dimensions):
            self.length(label,val)
        if cct is not None:
            p=self.fm.AddParameter('Color Temperature K',DB.GroupTypeId.IdentityData,DB.SpecTypeId.Number,False);self.fm.Set(p,float(cct))
        self.report['template_form_ids']=[str(i.Value) for i in self.template_form_ids]

    def checkpoint(self,stage):
        self.report['stage']=stage
        with open(self.report_path,'w') as stream: json.dump(self.report,stream,indent=2,default=str)

    def length(self,name,value):
        p=self.fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False);self.fm.SetFormula(p,str(value)+' in');return p

    def note(self,text):
        p=self.fm.AddParameter('Model Accuracy Notes',DB.GroupTypeId.IdentityData,DB.SpecTypeId.String.Text,False);self.fm.Set(p,text);self.report['inferences']=text

    def material(self,label,rgb,gloss=.3,transparency=0,reflectivity=.08,emission=0,cct=None,material_class='Metal'):
        base=next(a for a in self.app.GetAssets(DB.Visual.AssetType.Appearance) if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value=='GenericSchema')
        appearance=DB.AppearanceAssetElement.Create(self.doc,self.basename+' '+label,base)
        mat=self.doc.GetElement(DB.Material.Create(self.doc,self.basename+' '+label));mat.AppearanceAssetId=appearance.Id
        mat.Color=DB.Color(*rgb);mat.Transparency=int(transparency*100);mat.MaterialClass=material_class
        scope=DB.Visual.AppearanceAssetEditScope(self.doc);asset=scope.Start(appearance.Id)
        def color(key,val):
            prop=asset.FindByName(key)
            if prop is None: raise RuntimeError('Required appearance property missing: '+key)
            if prop.NumberOfConnectedProperties:prop.RemoveConnectedAsset()
            prop.SetValueAsColor(DB.Color(*val))
        def scalar(key,val,required=True):
            prop=asset.FindByName(key)
            if prop is None:
                if required:raise RuntimeError('Required appearance property missing: '+key)
                return
            if prop.NumberOfConnectedProperties:prop.RemoveConnectedAsset()
            prop.Value=val
        color('generic_diffuse',rgb)
        scalar('generic_glossiness',gloss);scalar('generic_transparency',transparency)
        scalar('generic_reflectivity_at_0deg',reflectivity);scalar('generic_reflectivity_at_90deg',.65 if transparency else .30)
        scalar('generic_refraction_index',1.52 if material_class=='Glass' else 1.0)
        scalar('generic_self_illum_luminance',emission)
        if cct is not None:
            scalar(DB.Visual.Generic.GenericSelfIllumColorTemperature,float(cct))
            color(DB.Visual.Generic.GenericSelfIllumFilterMap,(255,247,232))
        scope.Commit(True);scope.Dispose()
        param=self.fm.AddParameter(label,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False);self.fm.Set(param,mat.Id)
        self.parameters[label]=param;self.materials[label]=mat
        self.report.setdefault('appearance_defaults',{})[label]={'rgb':rgb,'gloss':gloss,'transparency':transparency,'cct_k':cct,'luminance':emission}
        return param

    def add(self,name,solid,material):
        form=DB.FreeFormElement.Create(self.doc,solid)
        self.fm.AssociateElementParameterToFamilyParameter(form.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),material)
        self.forms.append(form);self.parts.append({'name':name,'id':str(form.Id.Value),'volume_ft3':solid.Volume})
        return form

    def revolve(self,name,origin,axis,profile,material):return self.add(name,revolve_solid(origin,axis,profile),material)
    def cylinder(self,name,origin,axis,r,a,b,material,rounding=0):return self.add(name,cylinder_solid(origin,axis,r,a,b,rounding),material)
    def box(self,name,x0,y0,z0,x1,y1,z1,material,rounding=0):
        points=rounded_rect(x0,y0,x1,y1,rounding) if rounding else [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
        solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop(xyz(0,0,z0),DB.XYZ.BasisX,DB.XYZ.BasisY,points)]),DB.XYZ.BasisZ,(z1-z0)/12.)
        return self.add(name,solid,material)
    def tube(self,name,center,axis,outer,inner,a,b,material):
        return self.revolve(name,center,axis,[(inner,a),(outer,a),(outer,b),(inner,b)],material)
    def globe(self,name,center,r,thickness,opening_axis,opening_r,material):
        outer=sphere_solid(center,r);inner=sphere_solid(center,r-thickness)
        solid=DB.BooleanOperationsUtils.ExecuteBooleanOperation(outer,inner,DB.BooleanOperationsType.Difference)
        cutter=cylinder_solid(center,opening_axis,opening_r,r-1,r+1)
        solid=DB.BooleanOperationsUtils.ExecuteBooleanOperation(solid,cutter,DB.BooleanOperationsType.Difference)
        return self.add(name,solid,material)

    def _view(self,doc,name,eye,target,up,objects,realistic=False,template_ids=None):
        vt=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
        view=DB.View3D.CreateIsometric(doc,vt.Id);view.Name=name;view.DetailLevel=DB.ViewDetailLevel.Fine;view.Scale=1
        forward=target.Subtract(eye).Normalize()
        if abs(forward.DotProduct(up))>.98:up=DB.XYZ.BasisY if abs(forward.Y)<.98 else DB.XYZ.BasisX
        right=forward.CrossProduct(up).Normalize();trueup=right.CrossProduct(forward).Normalize()
        view.SetOrientation(DB.ViewOrientation3D(eye,trueup,forward))
        view.DisplayStyle=DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
        white=DB.Color(255,255,255);view.SetBackground(DB.ViewDisplayBackground.CreateGradient(white,white,white))
        if template_ids:
            view.HideElementsTemporary(List[DB.ElementId](template_ids))
        for cat in doc.Settings.Categories:
            if cat.CategoryType==DB.CategoryType.Annotation and view.CanCategoryBeHidden(cat.Id):view.SetCategoryHidden(cat.Id,True)
        doc.Regenerate()
        b=element_bounds(objects);margin=max(.2,max(b[3]-b[0],b[4]-b[1],b[5]-b[2])*.06)
        section=DB.BoundingBoxXYZ();section.Min=xyz(b[0]-margin,b[1]-margin,b[2]-.01);section.Max=xyz(b[3]+margin,b[4]+margin,b[5]+margin)
        view.SetSectionBox(section);view.IsSectionBoxActive=True
        # Explicit crop from fixture geometry, not the template host's extents.
        doc.Regenerate();crop=view.CropBox;inverse=crop.Transform.Inverse
        points=[inverse.OfPoint(xyz(x,y,z)) for x in [b[0],b[3]] for y in [b[1],b[4]] for z in [b[2],b[5]]]
        lo=DB.XYZ(min(p.X for p in points)-margin/12,min(p.Y for p in points)-margin/12,crop.Min.Z)
        hi=DB.XYZ(max(p.X for p in points)+margin/12,max(p.Y for p in points)+margin/12,crop.Max.Z)
        crop.Min=lo;crop.Max=hi;view.CropBox=crop;view.CropBoxActive=True;view.CropBoxVisible=False
        return view

    def _export(self,doc,views,prefix):
        options=DB.ImageExportOptions();options.ExportRange=DB.ExportRange.SetOfViews
        options.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]));options.FilePath=os.path.join(self.evidence,prefix)
        options.HLRandWFViewsFileType=DB.ImageFileType.PNG;options.ShadowViewsFileType=DB.ImageFileType.PNG
        options.ImageResolution=DB.ImageResolution.DPI_150;options.ZoomType=DB.ZoomFitType.FitToPage;options.PixelSize=1800
        doc.ExportImage(options)

    def finish(self):
        self.doc.Regenerate();self.report['display_bounds_in']=element_bounds(self.forms);bounds=measured_geometry_bounds(self.forms);self.report['bounds_in']=bounds;self.report['bounds_method']='Fine native face meshes plus 128-sample analytic edges';self.report['parts']=self.parts
        dimensions=[bounds[i+3]-bounds[i] for i in range(3)];self.report['actual_dimensions_in']=dimensions
        center=xyz((bounds[0]+bounds[3])/2,(bounds[1]+bounds[4])/2,(bounds[2]+bounds[5])/2)
        span=max(dimensions)*2+12;up=DB.XYZ.BasisY if self.host=='wall' else DB.XYZ(0,0,-1)
        eyes=[('Front',center.Add(xyz(0,0,span)) if self.host=='wall' else center.Add(xyz(0,-span,0))),
              ('Side',center.Add(xyz(span,0,0))),('Oblique',center.Add(xyz(span*.65,-span*.45,span*.65)))]
        views=[self._view(self.doc,n,e,center,up,self.forms,False,self.template_form_ids) for n,e in eyes]
        views.append(self._view(self.doc,'Material',eyes[-1][1],center,up,self.forms,True,self.template_form_ids))
        self.tx.Commit();self.tx=None;self.checkpoint('save_export')
        so=DB.SaveAsOptions();so.OverwriteExistingFile=True;so.MaximumBackups=1;so.PreviewViewId=views[2].Id
        self.doc.SaveAs(self.path,so);self._export(self.doc,views,self.basename)
        self.report['family_warnings']=[w.GetDescriptionText() for w in self.doc.GetWarnings()]
        self.doc.Close(False);self.docs.remove(self.doc)
        self.checkpoint('reopen_native_qa');doc=self.app.OpenDocumentFile(self.path);self.docs.append(doc)
        self.report['reopened']=doc.IsFamilyDocument;self.report['category']=doc.OwnerFamily.FamilyCategory.Name;self.report['placement']=str(doc.OwnerFamily.FamilyPlacementType)
        self.report['reopened_warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
        project=self.app.NewProjectDocument(DB.UnitSystem.Imperial);self.docs.append(project)
        family=doc.LoadFamily(project);symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
        self.tx=DB.Transaction(project,'Native face placement and material verification');self.tx.Start()
        level=DB.Level.Create(project,10 if self.host=='ceiling' else 0)
        if self.host=='wall':
            wt=next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind==DB.WallKind.Basic)
            host=DB.Wall.Create(project,DB.Line.CreateBound(DB.XYZ(-8,0,0),DB.XYZ(8,0,0)),wt.Id,level.Id,10,0,False,False)
            project.Regenerate();reference=DB.HostObjectUtils.GetSideFaces(host,DB.ShellLayerType.Exterior)[0];face=host.GetGeometryObjectFromReference(reference);point=face.Project(DB.XYZ(0,0,5)).XYZPoint
        else:
            floor_type=DB.Floor.GetDefaultFloorType(project,False)
            perimeter=loop(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,[(-96,-96),(96,-96),(96,96),(-96,96)])
            host=DB.Floor.Create(project,List[DB.CurveLoop]([perimeter]),floor_type,level.Id)
            project.Regenerate();reference=DB.HostObjectUtils.GetBottomFaces(host)[0];face=host.GetGeometryObjectFromReference(reference);point=face.Project(DB.XYZ(0,0,10)).XYZPoint
        symbol.Activate();project.Regenerate();instance=project.Create.NewFamilyInstance(reference,point,DB.XYZ.BasisX,symbol);project.Regenerate()
        normal_dot=instance.GetTransform().BasisZ.DotProduct(face.FaceNormal)
        self.report['host']={'host_id':str(host.Id.Value),'instance_host_id':str(instance.Host.Id.Value) if instance.Host else None,'hostface_present':instance.HostFace is not None,'normal_dot':normal_dot,'host_kind':self.host}
        self.report['material_tests']={}
        for label in self.parameters:
            p=symbol.LookupParameter(label);original=p.AsElementId();alternate=DB.Material.Create(project,'QA '+label);p.Set(alternate);project.Regenerate()
            ids=[f.MaterialElementId for s in all_solids(instance.get_Geometry(DB.Options())) for f in s.Faces]
            self.report['material_tests'][label]={'writable':not p.IsReadOnly,'substitution_reaches_faces':alternate in ids,'face_count':len(ids)}
            p.Set(original);project.Regenerate()
        box=instance.get_BoundingBox(None);target=(box.Min+box.Max)*.5
        hostedeye=target.Add(DB.XYZ(4,-6,2 if self.host=='wall' else -3))
        hosted=self._view(project,'Hosted',hostedeye,target,DB.XYZ.BasisZ,[instance],False)
        native_views=[];transform=instance.GetTransform()
        for label,local_eye in eyes:
            isolated=self._view(project,'Native '+label,transform.OfPoint(local_eye),transform.OfPoint(center),transform.OfVector(up),[instance],False)
            isolated.HideElements(List[DB.ElementId]([host.Id]));native_views.append(isolated)
        isolated=self._view(project,'Native Material',transform.OfPoint(eyes[-1][1]),transform.OfPoint(center),transform.OfVector(up),[instance],True)
        isolated.HideElements(List[DB.ElementId]([host.Id]));native_views.append(isolated)
        self.tx.Commit();self.tx=None;self._export(project,[hosted],self.basename+'_Hosted');self._export(project,native_views,self.basename+'_Isolated')
        self.report['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
        self.report['evidence_files']=[n for n in os.listdir(self.evidence) if n.startswith(self.basename) and n.endswith('.png')]
        cct_ok=True
        if self.cct is not None:
            actual=symbol.LookupParameter('Color Temperature K').AsDouble();self.report['saved_cct_parameter_k']=actual;cct_ok=abs(actual-self.cct)<.01
        gates={'reopened':self.report['reopened'],'category':self.report['category']=='Lighting Fixtures',
               'actual_face_host':instance.Host is not None and instance.Host.Id==host.Id and instance.HostFace is not None,
               'orientation':abs(normal_dot-1)<1e-6,'dimensions':all(abs(a-b)<.025 for a,b in zip(dimensions,self.expected)),
               'materials':all(row['substitution_reaches_faces'] for row in self.report['material_tests'].values()),'cct':cct_ok,
               'warnings':not self.report['family_warnings'] and not self.report['reopened_warnings'] and not self.report['project_warnings'],
               'views':len(self.report['evidence_files'])>=5}
        self.report['gates']=gates;self.report['technical_pass']=all(gates.values());self.report['finished_utc']=datetime.datetime.utcnow().isoformat()+'Z'
        self.checkpoint('complete' if self.report['technical_pass'] else 'failed_gates')
        if not self.report['technical_pass']:raise RuntimeError('Failed native gates: '+str([k for k,v in gates.items() if not v]))
        self.close()
        return self.report

    def fail(self):
        self.report['error']=traceback.format_exc();self.report['technical_pass']=False;self.checkpoint('failed');self.close()

    def close(self):
        if self.tx is not None:
            try:self.tx.RollBack()
            except Exception:pass
            self.tx=None
        for doc in reversed(self.docs):
            try:doc.Close(False)
            except Exception:pass
        self.docs=[]