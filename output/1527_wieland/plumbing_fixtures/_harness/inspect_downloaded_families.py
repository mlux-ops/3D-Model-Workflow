# -*- coding: utf-8 -*-
"""Native save/reopen and placed-geometry review for manufacturer family sources."""
import os,sys,json,datetime,traceback,math,glob,shutil
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(HERE)
sys.path.insert(0,HERE)
from native_plumbing_support import all_solids,measured_geometry_bounds,loop

CASES=[
 {'key':'MS642124CEFG_01','model':'MS642124CEFG#01','choose_type':'MS642124CEFG',
  'source':'MS642124CEFG_01/TOTO_Nexus_MS642124CEFG_R2025.rfa','dimensions_mm':[444.5,725.4875,685.8],
  'source_url':'https://www.totousa.com/filemanager_uploads/product_assets/REVITModels/BM-00593_MS642124CEFG_MS642124CUFG.rfa','original_format':'2019',
  'spec_url':'https://www.totousa.com/filemanager_uploads/product_assets/SpecSheet/SS-01451_MS642124CEFG.pdf'},
 {'key':'SS124_01','model':'SS124#01','choose_type':'SS124',
  'source':'SS124_01/TOTO_SS124_Manufacturer_Extracted_R2025.rfa','dimensions_mm':[355.6,473.075,46.0375],
  'source_url':'https://www.totousa.com/filemanager_uploads/product_assets/REVITModels/BM-00593_MS642124CEFG_MS642124CUFG.rfa','original_format':'2019; extracted nested BM-00561_SS124',
  'spec_url':'https://www.totousa.com/filemanager_uploads/product_assets/SpecSheet/SS-02062_MS446124CEMF(G)N.pdf'},
 {'key':'700337000000090','model':'700337000000090','choose_type':'700337',
  'source':'_research/700337000000090/downloads/produravit_downloads_20261002_172721_files/Duravit_BIM_3347300.rfa','dimensions_mm':[1700,900,None],
  'source_url':'https://pro.duravit.us/pro/zip/sf_getfiles.us-en.zip?nodeId=3169365&ftd=ASSET_TYPE_REVIT',
  'spec_url':'https://pro.duravit.us/pro/content/homepage/series/series/overview/products~402880943a1b6e1b013a1bd20b39003d.us-en.html?product=3169365'}
]

def name(e):
    try:return DB.Element.Name.GetValue(e)
    except Exception:return str(e.GetType().Name)

def store(path,data):
    serialized=ascii_json(data)
    with open(path,'w') as f:f.write(serialized)

def quoted(value):
    if isinstance(value,str):
        try:value=value.decode('utf-8')
        except Exception:value=u''.join(unichr(ord(c)) for c in value)
    elif not isinstance(value,unicode):value=unicode(value)
    pieces=[]
    for character in value:
        code=ord(character)
        if character==u'"':pieces.append('\\"')
        elif character==u'\\':pieces.append('\\\\')
        elif 32<=code<127:pieces.append(chr(code))
        elif code<=65535:pieces.append('\\u%04x'%code)
        else:
            code-=65536;pieces.append('\\u%04x\\u%04x'%(0xD800+(code>>10),0xDC00+(code&1023)))
    return '"'+''.join(pieces)+'"'

def ascii_json(value):
    if value is None:return 'null'
    if value is True:return 'true'
    if value is False:return 'false'
    if isinstance(value,(int,long,float)):return str(value)
    if isinstance(value,dict):return '{'+','.join(quoted(k)+':'+ascii_json(v) for k,v in value.items())+'}'
    if isinstance(value,(list,tuple)):return '['+','.join(ascii_json(x) for x in value)+']'
    return quoted(value)

def execute(case,app):
    folder=os.path.join(ROOT,case['key']);evidence=os.path.join(folder,'evidence')
    if not os.path.isdir(evidence):os.makedirs(evidence)
    vp=os.path.join(folder,'validation.json')
    if os.path.isfile(vp):
        history=os.path.join(folder,'_history')
        if not os.path.isdir(history):os.makedirs(history)
        shutil.copy2(vp,os.path.join(history,'validation_before_manufacturer_review_'+datetime.datetime.utcnow().strftime('%H%M%S')+'.json'))
    result={'model':case['model'],'source_url':case['source_url'],'spec_url':case['spec_url'],'source_kind':'MANUFACTURER_RFA',
            'source_reference':case['source'],'started_utc':datetime.datetime.utcnow().isoformat()+'Z','revit_version':app.VersionNumber,
            'revit_build':app.VersionBuild,'native_gates_pass':False,'stage':'open_source','status':'DOWNLOADED'}
    docs=[];tx=None
    try:
        path=os.path.join(ROOT,case['source'])
        info=DB.BasicFileInfo.Extract(path)
        result['input_format']=info.Format;result['manufacturer_original_format']=case.get('original_format',info.Format)
        doc=app.OpenDocumentFile(path);docs.append(doc)
        result['source_category']=doc.OwnerFamily.FamilyCategory.Name
        fm=doc.FamilyManager;types=list(fm.Types)
        result['types']=[]
        for t in types:
            row={'name':t.Name,'identity':{}}
            for p in fm.Parameters:
                if p.StorageType==DB.StorageType.String:
                    value=t.AsString(p)
                    if value:row['identity'][p.Definition.Name]=value
            result['types'].append(row)
        tx=DB.Transaction(doc,'Select and upgrade manufacturer fixture');tx.Start()
        if types:
            selected=next((t for t in types if t.Name==case['choose_type']),None)
            if selected is None:selected=next((t for t in types if case['choose_type'] in t.Name),types[0])
            fm.CurrentType=selected
        else:fm.NewType(case['model'])
        result['selected_type']=fm.CurrentType.Name
        if doc.OwnerFamily.FamilyCategory.Id!=DB.ElementId(DB.BuiltInCategory.OST_PlumbingFixtures):
            doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_PlumbingFixtures)
            result['category_correction']='Delivery copy changed to Plumbing Fixtures; manufacturer source preserved.'
        doc.Regenerate();tx.Commit();tx=None
        rfa=os.path.join(folder,'Manufacturer_'+case['key']+'_R2025.rfa')
        so=DB.SaveAsOptions();so.OverwriteExistingFile=True;so.MaximumBackups=1
        doc.SaveAs(rfa,so);result['rfa_path']=rfa
        result['family_warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
        doc.Close(False);docs.remove(doc)
        doc=app.OpenDocumentFile(rfa);docs.append(doc)
        result['reopened']=doc.IsFamilyDocument;result['category']=doc.OwnerFamily.FamilyCategory.Name
        result['placement']=str(doc.OwnerFamily.FamilyPlacementType)
        result['reopened_warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
        result['saved_format']=DB.BasicFileInfo.Extract(rfa).Format
        project=app.NewProjectDocument(DB.UnitSystem.Imperial);docs.append(project)
        family=doc.LoadFamily(project)
        symbols=[project.GetElement(i) for i in family.GetFamilySymbolIds()]
        symbol=next((s for s in symbols if name(s)==result['selected_type']),symbols[0])
        tx=DB.Transaction(project,'Place and inspect manufacturer family');tx.Start()
        level=DB.Level.Create(project,0)
        perimeter=loop(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,[(-120,-120),(120,-120),(120,120),(-120,120)])
        host=DB.Floor.Create(project,List[DB.CurveLoop]([perimeter]),DB.Floor.GetDefaultFloorType(project,False),level.Id)
        project.Regenerate();ref=DB.HostObjectUtils.GetTopFaces(host)[0];face=host.GetGeometryObjectFromReference(ref)
        point=face.Project(DB.XYZ.Zero).XYZPoint;symbol.Activate();project.Regenerate()
        if result['placement']=='WorkPlaneBased':
            instance=project.Create.NewFamilyInstance(ref,point,DB.XYZ.BasisX,symbol)
        else:
            instance=project.Create.NewFamilyInstance(point,symbol,level,DB.Structure.StructuralType.NonStructural)
        project.Regenerate()
        bounds=measured_geometry_bounds([instance]);dims=[(bounds[i+3]-bounds[i])*25.4 for i in range(3)]
        result['actual_dimensions_after_reopen_mm']=dims;result['bounds_in']=bounds
        result['bounds_method']='Saved family loaded and placed in clean project, excluding template host; fine native faces and analytic edges.'
        expected=case['dimensions_mm']
        result['expected_dimensions_mm']=expected
        result['dimensional_comparison']=[{'axis':axis,'actual_mm':a,'nominal_mm':b,'deviation_mm':a-b if b is not None else None,
                                         'pass':abs(a-b)<=1 if b is not None else None} for axis,a,b in zip(['X','Y','Z'],dims,expected)]
        result['host']={'host_kind':'floor','hostface_present':instance.HostFace is not None,
                        'instance_host_id':str(instance.Host.Id.Value) if instance.Host else None}
        result['material_tests']={}
        for param in symbol.Parameters:
            if param.StorageType!=DB.StorageType.ElementId or param.IsReadOnly:continue
            original=param.AsElementId();mat=project.GetElement(original)
            if not isinstance(mat,DB.Material):continue
            alternate=DB.Material.Create(project,'QA '+param.Definition.Name)
            param.Set(alternate);project.Regenerate()
            ids=[f.MaterialElementId for s in all_solids(instance.get_Geometry(DB.Options())) for f in s.Faces]
            result['material_tests'][param.Definition.Name]={'substitution_reaches_faces':alternate in ids,'writable':True}
            param.Set(original);project.Regenerate()
        vt=next(v for v in DB.FilteredElementCollector(project).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
        center=DB.XYZ((bounds[0]+bounds[3])/24.,(bounds[1]+bounds[4])/24.,(bounds[2]+bounds[5])/24.)
        span=max(dims)/304.8*2+5
        views=[]
        for label,vector in [('Front',DB.XYZ(0,-span,0)),('Side',DB.XYZ(span,0,0)),('Oblique',DB.XYZ(span*.8,-span,span*.7))]:
            view=DB.View3D.CreateIsometric(project,vt.Id);view.Name='Manufacturer '+label;view.DetailLevel=DB.ViewDetailLevel.Fine
            eye=center+vector;forward=(center-eye).Normalize();up=DB.XYZ.BasisZ;right=forward.CrossProduct(up).Normalize()
            view.SetOrientation(DB.ViewOrientation3D(eye,right.CrossProduct(forward).Normalize(),forward));view.DisplayStyle=DB.DisplayStyle.Shading
            view.HideElements(List[DB.ElementId]([host.Id]))
            for cat in project.Settings.Categories:
                if (cat.CategoryType==DB.CategoryType.Annotation or cat.Name in ['Connectors','Reference Planes']) and view.CanCategoryBeHidden(cat.Id):view.SetCategoryHidden(cat.Id,True)
            white=DB.Color(255,255,255);view.SetBackground(DB.ViewDisplayBackground.CreateGradient(white,white,white))
            project.Regenerate();box=view.CropBox;inv=box.Transform.Inverse
            pts=[inv.OfPoint(DB.XYZ(x/12.,y/12.,z/12.)) for x in [bounds[0],bounds[3]] for y in [bounds[1],bounds[4]] for z in [bounds[2],bounds[5]]]
            margin=max(dims)/304.8*.07
            box.Min=DB.XYZ(min(v.X for v in pts)-margin,min(v.Y for v in pts)-margin,box.Min.Z)
            box.Max=DB.XYZ(max(v.X for v in pts)+margin,max(v.Y for v in pts)+margin,box.Max.Z)
            view.CropBox=box;view.CropBoxActive=True;view.CropBoxVisible=False;views.append(view)
        tx.Commit();tx=None
        options=DB.ImageExportOptions();options.ExportRange=DB.ExportRange.SetOfViews;options.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]))
        options.FilePath=os.path.join(evidence,'Manufacturer_'+case['key']);options.HLRandWFViewsFileType=DB.ImageFileType.PNG;options.ShadowViewsFileType=DB.ImageFileType.PNG
        options.PixelSize=1400;options.ZoomType=DB.ZoomFitType.FitToPage;project.ExportImage(options)
        result['evidence_files']=[x for x in os.listdir(evidence) if x.startswith('Manufacturer_') and x.endswith('.png')]
        result['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
        result['gates']={'reopened':result['reopened'],'category':result['category']=='Plumbing Fixtures',
                         'views':len(result['evidence_files'])>=3,'actual_face_host':instance.HostFace is not None,
                         'dimensions':all(x['pass'] is True for x in result['dimensional_comparison']),
                         'materials':bool(result['material_tests']) and all(x['substitution_reaches_faces'] for x in result['material_tests'].values()),
                         'warnings':not result['family_warnings'] and not result['reopened_warnings'] and not result['project_warnings']}
        result['native_gates_pass']=all(result['gates'].values());result['technical_pass']=result['native_gates_pass']
        result['visual_review']='PENDING_NATIVE_IMAGE_REVIEW';result['stage']='manufacturer_review_complete'
        result['all_overall_dimensions_authoritative']=all(d is not None for d in expected)
    except Exception:
        result['error']=traceback.format_exc();result['stage']='manufacturer_review_failed'
    finally:
        if tx is not None:
            try:tx.RollBack()
            except Exception:pass
        for d in reversed(docs):
            try:d.Close(False)
            except Exception:pass
        result['finished_utc']=datetime.datetime.utcnow().isoformat()+'Z';store(vp,result)
    return result

app=__revit__.Application
results=[]
for case in CASES:
    result=execute(case,app)
    results.append({'key':case['key'],'stage':result['stage'],'gates':result.get('gates'),'error':result.get('error')})
store(os.path.join(HERE,'manufacturer_review_batch.json'),results)
