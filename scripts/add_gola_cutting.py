# -*- coding: utf-8 -*-
"""Add an unattached parametric recess void to the delivered Gola RFA.
Run under Revit 2025 via pyrevit. Preserves the original delivery.
"""
import os, json, math, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT=r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow'
SOURCE=os.path.join(ROOT,'output','gola','Richelieu_Gola_Channel_Profiles_2025.rfa')
OUT=os.path.join(ROOT,'output','gola_cutting')
if not os.path.isdir(OUT):os.makedirs(OUT)
RFA=os.path.join(OUT,os.path.basename(SOURCE))
RVT=os.path.join(OUT,'Gola_Recess_Cutting_Examples_2025.rvt')
report={'types':[],'rfa_path':RFA,'sample_project_path':RVT}
docs=[];tx=None
def checkpoint(stage):
    report['stage']=stage
    with open(os.path.join(OUT,'cutting_validation.json'),'w') as f:json.dump(report,f,indent=2)
def mm(n):return n/304.8
def xyz(x,y,z):return DB.XYZ(mm(x),mm(y),mm(z))
def solids(g):
    for a in g:
        if isinstance(a,DB.Solid) and a.Volume>1e-12:yield a
        elif isinstance(a,DB.GeometryInstance):
            for s in solids(a.GetInstanceGeometry()):yield s
def geom(e,view=None):
    o=DB.Options()
    if view:o.View=view
    return list(solids(e.get_Geometry(o)))
def volume(e,view=None):return sum(s.Volume for s in geom(e,view))*304.8**3
def profile_length(e,view):
    inv=e.GetTransform().Inverse
    p=[inv.OfPoint(p).X*304.8 for s in geom(e,view) for edge in s.Edges for p in edge.Tessellate()]
    return max(p)-min(p)
def set_length(e,n):
    c=e.Location.Curve;p=c.GetEndPoint(0);d=c.GetEndPoint(1).Subtract(p).Normalize()
    e.Location.Curve=DB.Line.CreateBound(p,p.Add(d.Multiply(mm(n))))
def rectxy(x0,y0,x1,y1):
    points=[xyz(x0,y0,0),xyz(x1,y0,0),xyz(x1,y1,0),xyz(x0,y1,0)]
    c=DB.CurveArray()
    for i in range(4):c.Append(DB.Line.CreateBound(points[i],points[(i+1)%4]))
    a=DB.CurveArrArray();a.Append(c);return a
def associate(doc,e,bip,p):doc.FamilyManager.AssociateElementParameterToFamilyParameter(e.get_Parameter(bip),p)
def view3d(doc,name,eye,target,box=None):
    vtype=next(t for t in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if t.ViewFamily==DB.ViewFamily.ThreeDimensional)
    v=DB.View3D.CreateIsometric(doc,vtype.Id);v.Name=name
    f=target.Subtract(eye).Normalize();r=f.CrossProduct(DB.XYZ.BasisZ).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye,r.CrossProduct(f).Normalize(),f))
    v.DetailLevel=DB.ViewDetailLevel.Fine;v.DisplayStyle=DB.DisplayStyle.ShadingWithEdges
    if box:
        b=DB.BoundingBoxXYZ();b.Min=xyz(*box[:3]);b.Max=xyz(*box[3:]);v.SetSectionBox(b);v.IsSectionBoxActive=True
    return v
def export(doc,v):
    o=DB.ImageExportOptions();o.FilePath=os.path.join(OUT,'Recess')
    o.ExportRange=DB.ExportRange.SetOfViews;o.SetViewsAndSheets(List[DB.ElementId]([v.Id]))
    o.ZoomType=DB.ZoomFitType.FitToPage;o.PixelSize=1800
    o.HLRandWFViewsFileType=DB.ImageFileType.PNG;o.ShadowViewsFileType=DB.ImageFileType.PNG
    doc.ExportImage(o)

try:
    app=__revit__.Application;assert app.VersionNumber=='2025';report['revit_version']=app.VersionNumber
    checkpoint('add void')
    doc=app.OpenDocumentFile(SOURCE);docs.append(doc);fm=doc.FamilyManager
    tx=DB.Transaction(doc,'Parametric host recess');tx.Start()
    original={e.Id:volume(e) for e in DB.FilteredElementCollector(doc).OfClass(DB.Extrusion) if e.IsSolid}
    params={p.Definition.Name:p for p in fm.Parameters}
    def add(name,spec=DB.SpecTypeId.Length,formula=None):
        p=fm.AddParameter(name,DB.GroupTypeId.Geometry,spec,True);params[name]=p
        if formula is not None:fm.SetFormula(p,formula)
        return p
    add('Recess Clearance');add('Extra Cut Depth');add('Front Cut Extension')
    add('Effective Recess Clearance',formula='if(Recess Clearance < 0.1 mm, 0.1 mm, Recess Clearance)')
    add('Recess Opening Width',formula='if(Type HC, 72.7 mm, if(Type HL, 56 mm, if(Type VS, 48.25 mm, 66.5 mm))) + 2 * Effective Recess Clearance')
    add('Recess Cut Back',formula='-Effective Recess Clearance - if(Extra Cut Depth < 0 mm, 0 mm, Extra Cut Depth)')
    add('Recess Cut Front',formula='if(Type HC, 26 mm, if(Type HL, 27 mm, 36.6 mm)) + Effective Recess Clearance + if(Front Cut Extension < 0 mm, 0 mm, Front Cut Extension)')
    for typ in fm.Types:
        fm.CurrentType=typ
        for n,value in [('Recess Clearance',.5),('Extra Cut Depth',0),('Front Cut Extension',50)]:fm.Set(params[n],mm(value))
    fm.CurrentType=next(t for t in fm.Types if t.Name=='Horizontal - C - Double Grip')
    doc.Regenerate()
    cutparam=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALLOW_CUT_WITH_VOIDS)
    cutparam.Set(1)
    plan=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewPlan) if v.ViewType==DB.ViewType.FloorPlan)
    refs={p.Name:p for p in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane)}
    lower=doc.FamilyCreate.NewReferencePlane(xyz(-100,-.5,0),xyz(1200,-.5,0),DB.XYZ.BasisZ,plan);lower.Name='Recess lower edge'
    upper=doc.FamilyCreate.NewReferencePlane(xyz(-100,73.2,0),xyz(1200,73.2,0),DB.XYZ.BasisZ,plan);upper.Name='Recess upper edge'
    doc.Regenerate()  # Materialize new plane references before dimensioning.
    def dim(a,b,p,x,y0,y1):
        arr=DB.ReferenceArray();arr.Append(a.GetReference());arr.Append(b.GetReference())
        # Dimension references set the measured gap; its support line need not
        # be as short as the sub-millimetre clearance itself.
        d=doc.FamilyCreate.NewLinearDimension(plan,DB.Line.CreateBound(xyz(x,y0-10,0),xyz(x,y1+10,0)),arr)
        d.FamilyLabel=p
    dim(lower,refs['Center (Front/Back)'],params['Effective Recess Clearance'],-200,-.5,0)
    dim(lower,upper,params['Recess Opening Width'],-150,-.5,73.2)
    doc.Regenerate()
    sp=DB.SketchPlane.Create(doc,DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisZ,DB.XYZ.Zero))
    void=doc.FamilyCreate.NewExtrusion(False,rectxy(0,-.5,1000,73.2),sp,mm(76.5))
    associate(doc,void,DB.BuiltInParameter.EXTRUSION_START_PARAM,params['Recess Cut Back'])
    associate(doc,void,DB.BuiltInParameter.EXTRUSION_END_PARAM,params['Recess Cut Front'])
    # Cuts Geometry controls internal family cuts, not external project cuts.
    # Keep this void unattached. Use native Cut/Uncut Geometry in the project.
    doc.Regenerate()
    # Locked sketch edges follow native Left/Right endpoint planes and width planes.
    edges=[]
    for loop in void.Sketch.Profile:
        for c in loop:edges.append(c)
    for c in edges:
        p=c.Evaluate(.5,True)
        if abs(c.Direction.X)>.9:plane=lower if p.Y<0 else upper
        else:plane=refs['Left'] if abs(p.X)<mm(.1) else refs['Right']
        doc.FamilyCreate.NewAlignment(plan,plane.GetReference(),c.Reference)
    doc.Regenerate()
    for id,v in original.items():assert abs(volume(doc.GetElement(id))-v)<.01,'Void cut channel solid'
    report['original_solids_preserved']=True
    tx.Commit();tx=None
    so=DB.SaveAsOptions();so.OverwriteExistingFile=True;so.MaximumBackups=1
    doc.SaveAs(RFA,so);doc.Close(False);docs.remove(doc)
    doc=app.OpenDocumentFile(RFA);docs.append(doc)
    report['reopened']=doc.IsFamilyDocument
    report['cut_with_voids']=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALLOW_CUT_WITH_VOIDS).AsInteger()==1
    report['family_warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    checkpoint('make casework test host')
    hostdoc=app.NewFamilyDocument(r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model.rft');docs.append(hostdoc)
    tx=DB.Transaction(hostdoc,'Casework validation panel');tx.Start()
    hostdoc.OwnerFamily.FamilyCategory=hostdoc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Casework)
    av=hostdoc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)
    if av and not av.IsReadOnly:av.Set(0)
    hfm=hostdoc.FamilyManager;hfm.NewType('HC test panel')
    hp=hfm.AddParameter('Panel Front',DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False)
    sp=DB.SketchPlane.Create(hostdoc,DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisZ,DB.XYZ.Zero))
    block=hostdoc.FamilyCreate.NewExtrusion(True,rectxy(-400,-80,2800,140),sp,mm(25))
    block.get_Parameter(DB.BuiltInParameter.EXTRUSION_START_PARAM).Set(mm(-100))
    associate(hostdoc,block,DB.BuiltInParameter.EXTRUSION_END_PARAM,hp)
    mid=DB.Material.Create(hostdoc,'Test cabinet panel - warm wood');mat=hostdoc.GetElement(mid);mat.Color=DB.Color(166,124,83)
    block.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM).Set(mid)
    for i,(key,depth) in enumerate([('HC',26),('HL',27),('VS',36.6),('VD',36.6)]):
        if i:hfm.NewType(key+' test panel')
        hfm.Set(hp,mm(depth-1))
    tx.Commit();tx=None
    hostdoc.SaveAs(os.path.join(OUT,'Gola_QA_Casework_Panel.rfa'),so)
    # Build a native vertical panel rather than rotating a previously cut copy;
    # copied cut instances can expose empty unique-geometry placeholders.
    vhostdoc=app.NewFamilyDocument(r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model.rft');docs.append(vhostdoc)
    tx=DB.Transaction(vhostdoc,'Vertical casework validation panel');tx.Start()
    vhostdoc.OwnerFamily.FamilyCategory=vhostdoc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Casework)
    vfm=vhostdoc.FamilyManager;vfm.NewType('HC vertical panel')
    vp=vfm.AddParameter('Panel Front',DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False)
    points=[xyz(0,-80,-400),xyz(0,140,-400),xyz(0,140,2800),xyz(0,-80,2800)]
    ca=DB.CurveArray()
    for j in range(4):ca.Append(DB.Line.CreateBound(points[j],points[(j+1)%4]))
    aa=DB.CurveArrArray();aa.Append(ca)
    sp=DB.SketchPlane.Create(vhostdoc,DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisX,DB.XYZ.Zero))
    vb=vhostdoc.FamilyCreate.NewExtrusion(True,aa,sp,mm(25))
    vb.get_Parameter(DB.BuiltInParameter.EXTRUSION_START_PARAM).Set(mm(-100))
    associate(vhostdoc,vb,DB.BuiltInParameter.EXTRUSION_END_PARAM,vp)
    vmid=DB.Material.Create(vhostdoc,'Test cabinet panel - warm wood');vhostdoc.GetElement(vmid).Color=DB.Color(166,124,83)
    vb.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM).Set(vmid)
    for i,(key,depth) in enumerate([('HC',26),('HL',27),('VS',36.6),('VD',66.5)]):
        if i:vfm.NewType(key+' vertical panel')
        vfm.Set(vp,mm(25 if key=='HC' else (26 if key=='HL' else 35.6)))
    tx.Commit();tx=None
    vhostdoc.SaveAs(os.path.join(OUT,'Gola_QA_Vertical_Casework_Panel.rfa'),so)
    pr=app.NewProjectDocument(DB.UnitSystem.Metric);docs.append(pr)
    fam=doc.LoadFamily(pr);hfamily=hostdoc.LoadFamily(pr);vhfamily=vhostdoc.LoadFamily(pr)
    symbols={pr.GetElement(i).get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString():pr.GetElement(i) for i in fam.GetFamilySymbolIds()}
    hs={pr.GetElement(i).get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString():pr.GetElement(i) for i in hfamily.GetFamilySymbolIds()}
    vhs={pr.GetElement(i).get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString():pr.GetElement(i) for i in vhfamily.GetFamilySymbolIds()}
    level=next(iter(DB.FilteredElementCollector(pr).OfClass(DB.Level)))
    tx=DB.Transaction(pr,'Verify real casework cuts');tx.Start()
    view=view3d(pr,'Recessed Gola - All Profiles',xyz(3000,-2200,3000),xyz(700,450,0),[-450,-150,-110,2850,1650,200])
    pairs=[]
    for i,(name,key,across,depth) in enumerate([
        ('Horizontal - C - Double Grip','HC',72.7,26),('Horizontal - L - Single Grip','HL',56,27),
        ('Vertical - Single Grip','VS',48.25,36.6),('Vertical - Double Grip','VD',66.5,36.6)]):
        checkpoint('test '+key)
        sym=symbols[name];sym.Activate();h=hs[key+' test panel'];h.Activate();pr.Regenerate()
        origin=xyz(0,i*450,0)
        host=pr.Create.NewFamilyInstance(origin,h,level,DB.Structure.StructuralType.NonStructural)
        inst=pr.Create.NewFamilyInstance(DB.Line.CreateBound(origin,origin.Add(xyz(1000,0,0))),sym,level,DB.Structure.StructuralType.NonStructural)
        for p in inst.Parameters:
            if p.Definition.Name.startswith('Show '):p.Set(0)
        pr.Regenerate();base=volume(host,view);channelbase=volume(inst,view)
        assert DB.InstanceVoidCutUtils.CanBeCutWithVoid(host)
        DB.InstanceVoidCutUtils.AddInstanceVoidCut(pr,host,inst);pr.Regenerate()
        assert DB.InstanceVoidCutUtils.InstanceVoidCutExists(host,inst)
        r={'key':key,'casework_cut':True,'flex':[]}
        report['types'].append(r)
        for n in [600,2400,1000]:
            set_length(inst,n);pr.Regenerate()
            removed=base-volume(host,view);expected=n*(across+1)*(depth-.5)
            r['flex'].append({'length_mm':n,'removed_mm3':removed,'expected_mm3':expected,'profile_length_mm':profile_length(inst,view)})
            assert abs(removed-expected)<1,(key,n,removed,expected)
            assert abs(profile_length(inst,view)-n)<.1
        assert abs(volume(inst,view)-channelbase)<.01,'Void damaged channel'
        DB.InstanceVoidCutUtils.RemoveInstanceVoidCut(pr,host,inst);pr.Regenerate()
        assert abs(volume(host,view)-base)<1
        DB.InstanceVoidCutUtils.AddInstanceVoidCut(pr,host,inst);pr.Regenerate()
        r['uncut_restores_host']=True
        inst.LookupParameter('Recess Clearance').Set(mm(2));inst.LookupParameter('Extra Cut Depth').Set(mm(5));pr.Regenerate()
        expected=1000*(across+4)*(depth+6)
        assert abs(base-volume(host,view)-expected)<1,(key,'clearance/depth',base-volume(host,view),expected)
        r['clearance_and_depth_test']=True
        inst.LookupParameter('Recess Clearance').Set(mm(.5));inst.LookupParameter('Extra Cut Depth').Set(0)
        for endpoint in [0,1]:
            c=inst.Location.Curve;p0=c.GetEndPoint(0);p1=c.GetEndPoint(1)
            if endpoint==0:p0=p0.Subtract(xyz(100,0,0))
            else:p1=p1.Add(xyz(150,0,0))
            inst.Location.Curve=DB.Line.CreateBound(p0,p1);pr.Regenerate()
            expected=inst.Location.Curve.Length*304.8*(across+1)*(depth-.5)
            assert abs(base-volume(host,view)-expected)<1
        r['both_endpoint_tests']=True
        inst.Location.Curve=DB.Line.CreateBound(origin,origin.Add(xyz(1000,0,0)));pr.Regenerate()
        pairs.append((host,inst))
    tx.Commit();tx=None
    checkpoint('vertical cutting tests')
    tx=DB.Transaction(pr,'Vertical face recessed test');tx.Start()
    vertical_pairs=[]
    for i,((host,inst),r) in enumerate(zip(pairs,report['types'])):
        vs=vhs[r['key']+' vertical panel'];vs.Activate();pr.Regenerate()
        origin=xyz(0,2500+i*450,0)
        vh=pr.Create.NewFamilyInstance(origin,vs,level,DB.Structure.StructuralType.NonStructural);pr.Regenerate()
        opt=DB.Options();opt.ComputeReferences=True
        def face_refs(ge,tr):
            for g in ge:
                if isinstance(g,DB.Solid):
                    for f in g.Faces:
                        if isinstance(f,DB.PlanarFace):yield f,tr
                elif isinstance(g,DB.GeometryInstance):
                    for pair in face_refs(g.GetSymbolGeometry(),tr.Multiply(g.Transform)):yield pair
        faces=[f for f,tr in face_refs(vh.get_Geometry(opt),DB.Transform.Identity) if tr.OfVector(f.FaceNormal).X>.9]
        assert faces,'Native vertical panel has no front face'
        face=max(faces,key=lambda f:f.Area)
        front=vs.LookupParameter('Panel Front').AsDouble()*304.8
        p0=origin.Add(xyz(front,0,0));p1=origin.Add(xyz(front,0,1000))
        vi=pr.Create.NewFamilyInstance(face.Reference,DB.Line.CreateBound(p0,p1),inst.Symbol);pr.Regenerate()
        offset=vi.get_Parameter(DB.BuiltInParameter.INSTANCE_FREE_HOST_OFFSET_PARAM)
        assert offset is not None and not offset.IsReadOnly,'Host offset unavailable'
        offset.Set(mm(-front));pr.Regenerate()
        for p in vi.Parameters:
            if p.Definition.Name.startswith('Show '):p.Set(0)
        base=volume(vh);DB.InstanceVoidCutUtils.AddInstanceVoidCut(pr,vh,vi);pr.Regenerate()
        set_length(vi,1200);pr.Regenerate()
        assert base-volume(vh)>10000,'No vertical recess removed'
        assert abs(profile_length(vi,None)-1200)<.1
        r['vertical_cut_test']=True
        vertical_pairs.append((vh,vi))
    vv=view3d(pr,'Vertical Recessed Gola',xyz(3000,1500,2800),xyz(0,3200,1000),[-150,2300,-500,250,4200,2850])
    for host,inst in vertical_pairs:view.HideElements(List[DB.ElementId]([host.Id,inst.Id]))
    for host,inst in pairs:vv.HideElements(List[DB.ElementId]([host.Id,inst.Id]))
    tx.Commit();tx=None
    report['project_warnings']=[w.GetDescriptionText() for w in pr.GetWarnings()]
    so.PreviewViewId=view.Id;pr.SaveAs(RVT,so)
    checkpoint('export verification views')
    export(pr,view);export(pr,vv)
    report['success']=True;checkpoint('complete')
except:
    report['error']=traceback.format_exc();checkpoint('failed '+report.get('stage','unknown'))
finally:
    if tx:
        try:tx.RollBack()
        except:pass
    for d in reversed(docs):
        try:d.Close(False)
        except:pass
