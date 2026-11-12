using System.Reflection;
using System.IO;
using System.Text.Json;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Structure;
using Autodesk.Revit.UI;

namespace CodexNativeRevit;

public interface ICompiledOperation
{
    object Execute(UIApplication app, Document document, JsonElement arguments);
}

public static class Operations
{
    public static readonly string[] Names = ["documents.list","context.query","elements.query","elements.inspect","parameters.query","categories.query","warnings.query","links.query","coordinates.convert","api.lookup","document.create","document.save_as","document.close","family.place","element.move","element.rotate","element.copy","element.mirror","element.type","element.flip","element.pin","element.curve","element.delete_preview","element.delete","parameter.set","type.duplicate","wall.create","floor.create","view.create","view.inspect","view.duplicate","view.settings","sheet.create","sheet.inspect","viewport.place","viewport.move","viewport.settings","schedule.create","schedule.place","schedule.move","schedule.settings","annotation.text","annotation.lines","annotation.dimension","annotation.tag","annotation.filled_region","layout.propose","layout.apply","capture.export","compiled.query","compiled.modify","batch.atomic"];
    static readonly HashSet<string> Queries = ["documents.list","context.query","elements.query","elements.inspect","parameters.query","categories.query","warnings.query","links.query","coordinates.convert","api.lookup","element.delete_preview","sheet.inspect","layout.propose","compiled.query","view.inspect"];
    public static bool Mutates(string op)=>!Queries.Contains(op) && op is not "family.inspect" and not "family.geometry.inspect";
    public static bool Lifecycle(string op)=>op is "document.create" or "document.save_as" or "document.close" or "capture.export";
    static Document Required(Document? d)=>d??throw new ArgumentException("Explicit document session ID required.");
    static Element E(Document d,JsonElement a,string key)=>Util.Element(d,a.GetProperty(key));
    static XYZ P(JsonElement a,string key)=>Util.Point(a.GetProperty(key));
    static ElementId Id(JsonElement a,string key)=>new(a.GetProperty(key).GetInt64());
    static IEnumerable<Element> Filter(Document d,JsonElement a)
    {
        var f=new FilteredElementCollector(d);
        if(a.TryGetProperty("category",out var c))f.OfCategory(Enum.Parse<BuiltInCategory>(c.GetString()!));
        if(a.TryGetProperty("class",out var cls))f.OfClass(typeof(Element).Assembly.GetType("Autodesk.Revit.DB."+cls.GetString(),true)!);
        if(Util.Bool(a,"types"))f.WhereElementIsElementType();else f.WhereElementIsNotElementType();
        var name=Util.Get(a,"name_contains");return f.Where(e=>string.IsNullOrEmpty(name)||e.Name.Contains(name,StringComparison.OrdinalIgnoreCase));
    }
    static object Param(Parameter p)=>new{ id=p.Id.Value,name=p.Definition.Name,guid=p.IsShared?p.GUID.ToString():null,storage_type=p.StorageType.ToString(),data_type=p.Definition.GetDataType().TypeId,unit=p.StorageType==StorageType.Double&&UnitUtils.IsMeasurableSpec(p.Definition.GetDataType())?p.GetUnitTypeId().TypeId:null,is_read_only=p.IsReadOnly,has_value=p.HasValue,value=Value(p),formatted=p.AsValueString()};
    static object? Value(Parameter p)=>p.StorageType switch{StorageType.Double=>p.AsDouble(),StorageType.Integer=>p.AsInteger(),StorageType.String=>p.AsString(),StorageType.ElementId=>p.AsElementId().Value,_=>null};
    static Parameter Parameter(Element e,JsonElement a)
    {
        if(a.TryGetProperty("parameter_id",out var id)) return e.Parameters.Cast<Parameter>().FirstOrDefault(p=>p.Id.Value==id.GetInt64())??throw new ArgumentException("Parameter ID missing on element.");
        if(a.TryGetProperty("parameter_guid",out var guid))return e.get_Parameter(Guid.Parse(guid.GetString()!))??throw new ArgumentException("Shared parameter missing.");
        if(a.TryGetProperty("built_in",out var built))return e.get_Parameter(Enum.Parse<BuiltInParameter>(built.GetString()!))??throw new ArgumentException("Built-in parameter missing.");
        var ps=e.GetParameters(Util.Get(a,"name"));if(ps.Count!=1)throw new ArgumentException("Parameter name must resolve uniquely; use parameter_id/GUID/built_in.");return ps[0];
    }
    static object SetParameter(Document d,JsonElement a)
    {
        var e=E(d,a,"element");Util.Editable(e);var p=Parameter(e,a);if(p.IsReadOnly)throw new ArgumentException("Parameter is read-only.");
        if(e is ElementType&&!Util.Bool(a,"allow_type_change"))throw new ArgumentException("Type edits require allow_type_change=true or duplicate type first.");
        var before=Value(p);var v=a.GetProperty("value");bool ok=p.StorageType switch{StorageType.Double=>p.Set(a.TryGetProperty("unit",out var unit)?UnitUtils.ConvertToInternalUnits(v.GetDouble(),new ForgeTypeId(unit.GetString())):v.GetDouble()),StorageType.Integer=>p.Set(v.GetInt32()),StorageType.String=>p.Set(v.GetString()),StorageType.ElementId=>p.Set(new ElementId(v.GetInt64())),_=>false};
        if(!ok)throw new InvalidOperationException("Parameter setter returned false.");d.Regenerate();return new{element=Util.Describe(e),parameter_id=p.Id.Value,before,after=Value(p)};
    }
    public static object Execute(UIApplication app,Document? target,string op,JsonElement a)
    {
        if(op=="documents.list")return app.Application.Documents.Cast<Document>().Select(DocumentRegistry.Describe).ToArray();
        if(op=="api.lookup")
        {
            var name=Util.Get(a,"type");var t=typeof(Element).Assembly.GetType(name)??typeof(UIApplication).Assembly.GetType(name)??throw new ArgumentException("Type not found in installed Revit API.");
            var member=Util.Get(a,"member");return new{revit_version=app.Application.VersionNumber,build=app.Application.VersionBuild,type=t.FullName,members=t.GetMembers(BindingFlags.Public|BindingFlags.Instance|BindingFlags.Static).Where(m=>member==""||m.Name==member).Select(m=>m.ToString()).ToArray()};
        }
        var d=Required(target);
        switch(op)
        {
            case "context.query":return new{document=DocumentRegistry.Describe(d),active=d.Equals(app.ActiveUIDocument?.Document),active_view=d.Equals(app.ActiveUIDocument?.Document)?Util.Describe(app.ActiveUIDocument!.ActiveView):null,selection=d.Equals(app.ActiveUIDocument?.Document)?app.ActiveUIDocument!.Selection.GetElementIds().Select(x=>Util.Describe(d.GetElement(x))).ToArray():[]};
            case "categories.query":return d.Settings.Categories.Cast<Category>().Select(c=>new{id=c.Id.Value,name=c.Name,type=c.CategoryType.ToString(),allows_bound_parameters=c.AllowsBoundParameters}).ToArray();
            case "elements.query":
                var offset=Math.Max(0,(int)Util.Num(a,"offset"));var limit=Math.Clamp((int)Util.Num(a,"limit",100),1,500);var rows=Filter(d,a).Skip(offset).Take(limit+1).ToArray();return new{items=rows.Take(limit).Select(Util.Describe).ToArray(),offset,next_offset=rows.Length>limit?(int?)(offset+limit):null,units="internal feet"};
            case "elements.inspect":
                var elem=E(d,a,"element");return new{element=Util.Describe(elem),dependent_ids=elem.GetDependentElements(null).Select(x=>x.Value),phase_created_id=elem.CreatedPhaseId.Value,phase_demolished_id=elem.DemolishedPhaseId.Value,design_option=elem.DesignOption?.Name,workset_id=elem.WorksetId.IntegerValue,editable=!elem.Pinned&&elem.GroupId==ElementId.InvalidElementId&&!d.IsReadOnly,transform=elem is Instance inst?TransformInfo(inst.GetTransform()):null,geometry=a.TryGetProperty("geometry",out var geo)&&geo.GetBoolean()?GeometryInfo(elem):null};
            case "parameters.query":
                var pe=E(d,a,"element");var type=d.GetElement(pe.GetTypeId());return new{instance=pe.Parameters.Cast<Parameter>().Select(Param).ToArray(),type=type?.Parameters.Cast<Parameter>().Select(Param).ToArray(),type_id=type?.Id.Value,owner_is_type=pe is ElementType};
            case "warnings.query":return d.GetWarnings().Select(w=>new{description=w.GetDescriptionText(),failure_id=w.GetFailureDefinitionId().Guid,element_ids=w.GetFailingElements().Select(x=>x.Value)}).ToArray();
            case "links.query":return new FilteredElementCollector(d).OfClass(typeof(RevitLinkInstance)).Cast<RevitLinkInstance>().Select(l=>new{instance=Util.Describe(l),transform=TransformInfo(l.GetTotalTransform()),linked_document=l.GetLinkDocument()==null?null:DocumentRegistry.Describe(l.GetLinkDocument())}).ToArray();
            case "coordinates.convert":
                var point=P(a,"point");var system=Util.Get(a,"system");var transform=system=="shared"?d.ActiveProjectLocation.GetTotalTransform():system=="link"?((RevitLinkInstance)E(d,a,"link")).GetTotalTransform():Transform.Identity;
                if(system!="shared"&&system!="link"&&system!="project")throw new ArgumentException("system must be project/shared/link; sheet coordinates are separate 2D feet.");
                return new{point=Util.Xyz((Util.Bool(a,"inverse")?transform.Inverse:transform).OfPoint(point)),transform=TransformInfo(transform),unit="internal feet",direction=Util.Bool(a,"inverse")?"project_to_source":"source_to_project"};
            case "parameter.set":return SetParameter(d,a);
            case "type.duplicate":var duplicate=((ElementType)E(d,a,"type")).Duplicate(Util.Get(a,"name"));return Util.Describe(duplicate);
            case "family.place":return Place(d,a);
            case "element.move":case "element.rotate":case "element.copy":case "element.mirror":
                var moving=E(d,a,"element");Util.Editable(moving);var before=Util.Describe(moving);ICollection<ElementId> changed=[moving.Id];
                if(op=="element.move")ElementTransformUtils.MoveElement(d,moving.Id,P(a,"vector"));
                if(op=="element.rotate")ElementTransformUtils.RotateElement(d,moving.Id,Line.CreateBound(P(a,"axis_start"),P(a,"axis_end")),Util.Num(a,"radians"));
                if(op=="element.copy")changed=ElementTransformUtils.CopyElement(d,moving.Id,P(a,"vector"));
                if(op=="element.mirror") {bool copy=Util.Bool(a,"copy",true);var old=new HashSet<long>(new FilteredElementCollector(d).WhereElementIsNotElementType().Select(x=>x.Id.Value));ElementTransformUtils.MirrorElements(d,[moving.Id],Plane.CreateByNormalAndOrigin(P(a,"normal"),P(a,"origin")),copy);changed=copy?new FilteredElementCollector(d).WhereElementIsNotElementType().Where(x=>!old.Contains(x.Id.Value)).Select(x=>x.Id).ToArray():[moving.Id];}
                d.Regenerate();return new{before,after=changed.Select(x=>Util.Describe(d.GetElement(x))).ToArray()};
            case "element.type":var et=E(d,a,"element");Util.Editable(et);var newType=E(d,a,"type");var prev=et.GetTypeId().Value;var replacement=et.ChangeTypeId(newType.Id);d.Regenerate();return new{before_type_id=prev,element=Util.Describe(replacement==ElementId.InvalidElementId?et:d.GetElement(replacement))};
            case "element.flip":var fi=(FamilyInstance)E(d,a,"element");Util.Editable(fi);bool success=Util.Get(a,"kind")=="hand"?fi.flipHand():fi.flipFacing();if(!success)throw new ArgumentException("Family does not support requested flip.");d.Regenerate();return new{element=Util.Describe(fi),fi.HandFlipped,fi.FacingFlipped};
            case "element.pin":var pin=E(d,a,"element");if(pin.GroupId!=ElementId.InvalidElementId)throw new ArgumentException("Grouped element cannot be changed implicitly.");pin.Pinned=Util.Bool(a,"pinned");return Util.Describe(pin);
            case "element.curve":var ce=E(d,a,"element");Util.Editable(ce);if(ce.Location is not LocationCurve lc)throw new ArgumentException("Element has no editable location curve.");lc.Curve=Line.CreateBound(P(a,"start"),P(a,"end"));d.Regenerate();return Util.Describe(ce);
            case "element.delete_preview":
                var dp=E(d,a,"element");using(var preview=new Transaction(d,"Codex deletion dependency preview")){preview.Start();var ids=d.Delete(dp.Id).Select(x=>x.Value).ToArray();preview.RollBack();return new{deleted_ids_if_applied=ids,transaction_status="rolled_back"};}
            case "element.delete":var del=E(d,a,"element");Util.Editable(del);var deleted=d.Delete(del.Id).Select(x=>x.Value).ToArray();var allowed=a.GetProperty("expected_deleted_ids").EnumerateArray().Select(x=>x.GetInt64()).ToHashSet();if(!allowed.SetEquals(deleted))throw new ArgumentException("Deletion dependency set changed; obtain fresh delete_preview and approve exact set.");return new{deleted_ids=deleted};
            case "wall.create":return Util.Describe(Wall.Create(d,Line.CreateBound(P(a,"start"),P(a,"end")),E(d,a,"type").Id,E(d,a,"level").Id,Util.Num(a,"height"),Util.Num(a,"offset"),Util.Bool(a,"flip"),Util.Bool(a,"structural")));
            case "floor.create":return Util.Describe(Floor.Create(d,[Loop(a.GetProperty("profile"))],E(d,a,"type").Id,E(d,a,"level").Id));
            case "view.create":
                var vt=(ViewFamilyType)E(d,a,"type");View view=Util.Get(a,"kind")=="3d"?View3D.CreateIsometric(d,vt.Id):Util.Get(a,"kind")=="drafting"?ViewDrafting.Create(d,vt.Id):ViewPlan.Create(d,vt.Id,E(d,a,"level").Id);view.Name=Util.Get(a,"name");if(a.TryGetProperty("scale",out var sc))view.Scale=sc.GetInt32();return Util.Describe(view);
            case "view.duplicate":var vd=(View)E(d,a,"view");var duplicated=d.GetElement(vd.Duplicate(Enum.Parse<ViewDuplicateOption>(Util.Get(a,"option","Duplicate"))));duplicated.Name=Util.Get(a,"name");return Util.Describe(duplicated);
            case "view.inspect":var vr=(View)E(d,a,"view");return new{view=Util.Describe(vr),scale=vr.Scale,detail_level=vr.DetailLevel.ToString(),template_id=vr.ViewTemplateId.Value,crop_active=vr.CropBoxActive,section_box_active=(vr as View3D)?.IsSectionBoxActive,hidden_categories=d.Settings.Categories.Cast<Category>().Where(c=>vr.CanCategoryBeHidden(c.Id)).Select(c=>new{name=c.Name,id=c.Id.Value,hidden=vr.GetCategoryHidden(c.Id)}).ToArray()};
            case "view.settings":
                var vs=(View)E(d,a,"view");if(a.TryGetProperty("scale",out var scale))vs.Scale=scale.GetInt32();if(a.TryGetProperty("template",out _))vs.ViewTemplateId=E(d,a,"template").Id;
                if(a.TryGetProperty("detail_level",out var detail))vs.DetailLevel=Enum.Parse<ViewDetailLevel>(detail.GetString()!);
                if(a.TryGetProperty("category_visibility",out var visibility))foreach(var prop in visibility.EnumerateObject())vs.SetCategoryHidden(new ElementId((long)Enum.Parse<BuiltInCategory>(prop.Name)),!prop.Value.GetBoolean());
                if(a.TryGetProperty("crop",out var crop)){vs.CropBox=new BoundingBoxXYZ{Min=P(crop,"min"),Max=P(crop,"max"),Transform=vs.CropBox.Transform};vs.CropBoxActive=true;}
                if(a.TryGetProperty("section_box",out var sb)){var v3=(View3D)vs;v3.SetSectionBox(new BoundingBoxXYZ{Min=P(sb,"min"),Max=P(sb,"max")});v3.IsSectionBoxActive=true;}return Util.Describe(vs);
            case "sheet.create":var sheet=ViewSheet.Create(d,a.TryGetProperty("titleblock_type",out _)?E(d,a,"titleblock_type").Id:ElementId.InvalidElementId);sheet.SheetNumber=Util.Get(a,"number");sheet.Name=Util.Get(a,"name");return Util.Describe(sheet);
            case "sheet.inspect":return Sheet(d,(ViewSheet)E(d,a,"sheet"));
            case "viewport.place":var sh=(ViewSheet)E(d,a,"sheet");var vi=(View)E(d,a,"view");if(!Viewport.CanAddViewToSheet(d,sh.Id,vi.Id))throw new ArgumentException("View cannot be placed on this sheet.");var vp=Viewport.Create(d,sh.Id,vi.Id,P(a,"center"));d.Regenerate();return ViewportInfo(vp);
            case "viewport.move":var vm=(Viewport)E(d,a,"viewport");Util.Editable(vm);vm.SetBoxCenter(P(a,"center"));d.Regenerate();return ViewportInfo(vm);
            case "viewport.settings":var vset=(Viewport)E(d,a,"viewport");Util.Editable(vset);if(a.TryGetProperty("rotation",out var rot))vset.Rotation=Enum.Parse<ViewportRotation>(rot.GetString()!);if(a.TryGetProperty("type",out _))vset.ChangeTypeId(E(d,a,"type").Id);if(a.TryGetProperty("label_offset",out _))vset.LabelOffset=P(a,"label_offset");if(a.TryGetProperty("label_line_length",out var len))vset.LabelLineLength=len.GetDouble();d.Regenerate();return ViewportInfo(vset);
            case "schedule.create":var sch=ViewSchedule.CreateSchedule(d,new ElementId((long)Enum.Parse<BuiltInCategory>(Util.Get(a,"category"))));sch.Name=Util.Get(a,"name");if(a.TryGetProperty("fields",out var fs))foreach(var field in fs.EnumerateArray()){var f=sch.Definition.GetSchedulableFields().Single(x=>x.GetName(d)==field.GetString());sch.Definition.AddField(f);}return Util.Describe(sch);
            case "schedule.place":var spi=ScheduleSheetInstance.Create(d,E(d,a,"sheet").Id,E(d,a,"schedule").Id,P(a,"point"));d.Regenerate();return ScheduleInfo(spi);
            case "schedule.move":var sm=(ScheduleSheetInstance)E(d,a,"instance");Util.Editable(sm);sm.Point=P(a,"point");d.Regenerate();return ScheduleInfo(sm);
            case "schedule.settings":return ScheduleSettings(d,a);
            case "annotation.text":return Util.Describe(TextNote.Create(d,E(d,a,"view").Id,P(a,"point"),Util.Get(a,"text"),E(d,a,"type").Id));
            case "annotation.lines":var av=(View)E(d,a,"view");return a.GetProperty("segments").EnumerateArray().Select(s=>Util.Describe(d.Create.NewDetailCurve(av,Line.CreateBound(P(s,"start"),P(s,"end"))))).ToArray();
            case "annotation.dimension":var da=a.GetProperty("references").EnumerateArray().Select(x=>Reference.ParseFromStableRepresentation(d,x.GetString())).ToArray();var ra=new ReferenceArray();foreach(var reference in da)ra.Append(reference);return Util.Describe(d.Create.NewDimension((View)E(d,a,"view"),Line.CreateBound(P(a,"start"),P(a,"end")),ra));
            case "annotation.tag":var tag=IndependentTag.Create(d,E(d,a,"type").Id,E(d,a,"view").Id,Reference.ParseFromStableRepresentation(d,Util.Get(a,"reference")),Util.Bool(a,"leader"),Enum.Parse<TagOrientation>(Util.Get(a,"orientation","Horizontal")),P(a,"point"));return Util.Describe(tag);
            case "annotation.filled_region":return Util.Describe(FilledRegion.Create(d,E(d,a,"type").Id,E(d,a,"view").Id,[Loop(a.GetProperty("profile"))]));
            case "layout.propose":return Propose(d,a);
            case "layout.apply":return ApplyLayout(d,a);
            case "document.save_as":
                var path=Path.GetFullPath(Util.Get(a,"path"));if(File.Exists(path))throw new ArgumentException("SaveAs path exists; implicit overwrite forbidden.");if(d.IsWorkshared)throw new ArgumentException("Workshared save/synchronize not implemented.");d.SaveAs(path,new SaveAsOptions{OverwriteExistingFile=false,MaximumBackups=1});return new{document=DocumentRegistry.Describe(d),external_effect="file written; not undoable by project transaction"};
            case "document.close":if(!Util.Bool(a,"discard_changes"))throw new ArgumentException("Close requires explicit discard_changes=true; save is a separate operation.");if(d.Equals(app.ActiveUIDocument?.Document))throw new ArgumentException("Active UI document must be closed through Revit interface.");return new{closed=d.Close(false)};
            case "capture.export":
                var rawPrefix=Util.Get(a,"path_prefix");if(!Path.IsPathFullyQualified(rawPrefix))throw new ArgumentException("Capture requires an absolute path prefix.");
                var file=Path.GetFullPath(rawPrefix);if(Path.GetFileName(file).Contains('.'))throw new ArgumentException("Capture prefix filename must contain no dots or extension: Revit truncates dotted prefixes and can overwrite another export. Use underscores instead.");
                if(Directory.GetFiles(Path.GetDirectoryName(file)!,Path.GetFileName(file)+"*").Length>0)throw new ArgumentException("Capture prefix already exists.");var options=new ImageExportOptions{FilePath=file,ExportRange=ExportRange.SetOfViews,HLRandWFViewsFileType=ImageFileType.PNG,ShadowViewsFileType=ImageFileType.PNG,ZoomType=ZoomFitType.FitToPage,PixelSize=(int)Util.Num(a,"pixels",1600)};options.SetViewsAndSheets([E(d,a,"view").Id]);d.ExportImage(options);
                var exported=Directory.GetFiles(Path.GetDirectoryName(file)!,Path.GetFileName(file)+"*");if(exported.Length==0 || exported.Any(p=>new FileInfo(p).Length==0))throw new UnknownCompletionException("Native export returned without expected nonempty files; reconcile output directory before retry.");return new{files=exported,native_export=true};
            case "compiled.query":case "compiled.modify":return Compiled(app,d,op,a);
            case "batch.atomic":return Atomic(app,d,a);
            default:throw new NotSupportedException("Operation not implemented: "+op);
        }
    }
    public static CurveLoop Loop(JsonElement a)
    {
        var pts=a.EnumerateArray().Select(Util.Point).ToArray();if(pts.Length<3)throw new ArgumentException("Profile needs at least three vertices.");var loop=new CurveLoop();for(int i=0;i<pts.Length;i++)loop.Append(Line.CreateBound(pts[i],pts[(i+1)%pts.Length]));return loop;
    }
    static object Place(Document d,JsonElement a)
    {
        var symbol=(FamilySymbol)E(d,a,"type");if(!symbol.IsActive){symbol.Activate();d.Regenerate();}
        var placement=symbol.Family.FamilyPlacementType;var items=a.TryGetProperty("instances",out var batch)?batch.EnumerateArray().ToArray():[a];var result=new List<object>();
        foreach(var item in items)
        {
            FamilyInstance instance;
            if(placement==FamilyPlacementType.OneLevelBased || placement==FamilyPlacementType.TwoLevelsBased)
            {
                if(placement==FamilyPlacementType.TwoLevelsBased)throw new NotSupportedException("Two-level placement requires category-specific top-level handling.");
                instance=d.Create.NewFamilyInstance(P(item,"point"),symbol,(Level)E(d,item,"level"),StructuralType.NonStructural);
            }
            else if(placement==FamilyPlacementType.OneLevelBasedHosted)instance=d.Create.NewFamilyInstance(P(item,"point"),symbol,E(d,item,"host"),(Level)E(d,item,"level"),StructuralType.NonStructural);
            else if(placement==FamilyPlacementType.WorkPlaneBased)
            {
                var reference=Reference.ParseFromStableRepresentation(d,Util.Get(item,"face_reference"));instance=d.Create.NewFamilyInstance(reference,P(item,"point"),P(item,"reference_direction"),symbol);
            }
            else if(placement==FamilyPlacementType.CurveBased)instance=d.Create.NewFamilyInstance(Line.CreateBound(P(item,"start"),P(item,"end")),symbol,(Level)E(d,item,"level"),StructuralType.NonStructural);
            else throw new NotSupportedException("Placement type requires another native creation overload: "+placement);
            if(item.TryGetProperty("rotation_radians",out var angle) && angle.GetDouble()!=0){var p=((LocationPoint)instance.Location).Point;ElementTransformUtils.RotateElement(d,instance.Id,Line.CreateBound(p,p+XYZ.BasisZ),angle.GetDouble());}
            d.Regenerate();result.Add(Util.Describe(instance));
        }
        return new{placement_type=placement.ToString(),instances=result};
    }
    static object TransformInfo(Transform t)=>new{origin=Util.Xyz(t.Origin),basis_x=Util.Xyz(t.BasisX),basis_y=Util.Xyz(t.BasisY),basis_z=Util.Xyz(t.BasisZ)};
    static object GeometryInfo(Element e)
    {
        var options=new Options{ComputeReferences=true,DetailLevel=ViewDetailLevel.Fine};var rows=new List<object>();
        void Walk(GeometryElement geometry){foreach(var obj in geometry){if(obj is Solid s){rows.Add(new{kind="solid",volume=s.Volume,faces=s.Faces.Size,edges=s.Edges.Size});foreach(Face f in s.Faces)if(f.Reference!=null)rows.Add(new{kind="face",area=f.Area,reference=f.Reference.ConvertToStableRepresentation(e.Document),normal=f is PlanarFace pf?Util.Xyz(pf.FaceNormal):null});}else if(obj is GeometryInstance i)Walk(i.GetInstanceGeometry());}}
        var g=e.get_Geometry(options);if(g!=null)Walk(g);return rows;
    }
    static object OutlineInfo(Outline o)=>new{min=Util.Xyz(o.MinimumPoint),max=Util.Xyz(o.MaximumPoint)};
    public static object ViewportInfo(Viewport v)=>new{element=Util.Describe(v),sheet_id=v.SheetId.Value,view_id=v.ViewId.Value,center=Util.Xyz(v.GetBoxCenter()),box=OutlineInfo(v.GetBoxOutline()),label_box=OutlineInfo(v.GetLabelOutline()),label_offset=Util.Xyz(v.LabelOffset),label_line_length=v.LabelLineLength,rotation=v.Rotation.ToString()};
    static object ScheduleInfo(ScheduleSheetInstance s){var b=s.get_BoundingBox(s.Document.GetElement(s.OwnerViewId) as View);return new{element=Util.Describe(s),schedule_id=s.ScheduleId.Value,sheet_id=s.OwnerViewId.Value,point=Util.Xyz(s.Point),bounds=b==null?null:new{min=Util.Xyz(b.Min),max=Util.Xyz(b.Max)}};}
    static object Sheet(Document d,ViewSheet sheet)=>new{sheet=Util.Describe(sheet),outline=new{min=new[]{sheet.Outline.Min.U,sheet.Outline.Min.V},max=new[]{sheet.Outline.Max.U,sheet.Outline.Max.V}},viewports=sheet.GetAllViewports().Select(x=>ViewportInfo((Viewport)d.GetElement(x))).ToArray(),schedules=new FilteredElementCollector(d,sheet.Id).OfClass(typeof(ScheduleSheetInstance)).Cast<ScheduleSheetInstance>().Select(ScheduleInfo).ToArray(),titleblocks=new FilteredElementCollector(d,sheet.Id).OfCategory(BuiltInCategory.OST_TitleBlocks).Select(Util.Describe).ToArray(),unit="sheet feet; caller must supply printable/content regions"};
    static object ScheduleSettings(Document d,JsonElement a)
    {
        var s=(ViewSchedule)E(d,a,"schedule");var def=s.Definition;
        if(a.TryGetProperty("filters",out var filters))foreach(var f in filters.EnumerateArray()){var field=def.GetFieldOrder().Single(id=>def.GetField(id).GetName()==Util.Get(f,"field"));var kind=Enum.Parse<ScheduleFilterType>(Util.Get(f,"kind"));var value=f.GetProperty("value");def.AddFilter(value.ValueKind==JsonValueKind.String?new ScheduleFilter(field,kind,value.GetString()):new ScheduleFilter(field,kind,value.GetDouble()));}
        if(a.TryGetProperty("sort",out var sort))foreach(var f in sort.EnumerateArray()){var field=def.GetFieldOrder().Single(id=>def.GetField(id).GetName()==Util.Get(f,"field"));def.AddSortGroupField(new ScheduleSortGroupField(field,Enum.Parse<ScheduleSortOrder>(Util.Get(f,"order","Ascending"))));}
        if(a.TryGetProperty("itemized",out var itemized))def.IsItemized=itemized.GetBoolean();return new{schedule=Util.Describe(s),fields=def.GetFieldOrder().Select(id=>new{id=id.IntegerValue,name=def.GetField(id).GetName()}).ToArray()};
    }
    static object Propose(Document d,JsonElement a)
    {
        // Detached rectangle translation based on current native extents, including labels. No model edits.
        var region=a.GetProperty("content_region").EnumerateArray().Select(x=>x.GetDouble()).ToArray();if(region.Length!=4)throw new ArgumentException("content_region=[xmin,ymin,xmax,ymax].");
        var moves=a.GetProperty("moves").EnumerateArray().ToArray();var rects=new List<(string name,double x0,double y0,double x1,double y1)>();var proposal=new List<object>();
        foreach(var move in moves){var e=E(d,move,"element");var p=P(move,"point");XYZ old;BoundingBoxXYZ? b;
            if(e is Viewport v){old=v.GetBoxCenter();var box=v.GetBoxOutline();var label=v.GetLabelOutline();b=new BoundingBoxXYZ{Min=new XYZ(Math.Min(box.MinimumPoint.X,label.MinimumPoint.X),Math.Min(box.MinimumPoint.Y,label.MinimumPoint.Y),0),Max=new XYZ(Math.Max(box.MaximumPoint.X,label.MaximumPoint.X),Math.Max(box.MaximumPoint.Y,label.MaximumPoint.Y),0)};}
            else if(e is ScheduleSheetInstance schedule){old=schedule.Point;b=e.get_BoundingBox((View)d.GetElement(e.OwnerViewId));}else throw new ArgumentException("Layout supports viewports and placed schedules.");
            if(b==null)throw new ArgumentException("Missing native bounds.");var delta=p-old;var min=b.Min+delta;var max=b.Max+delta;rects.Add((e.UniqueId,min.X,min.Y,max.X,max.Y));proposal.Add(new{element=Util.Describe(e),point=Util.Xyz(p),predicted_bounds=new{min=Util.Xyz(min),max=Util.Xyz(max)}});
        }
        if(a.TryGetProperty("reserved_regions",out var reserved))foreach(var item in reserved.EnumerateArray()){var r=item.EnumerateArray().Select(x=>x.GetDouble()).ToArray();rects.Add(("reserved",r[0],r[1],r[2],r[3]));}
        var issues=new List<string>();for(int i=0;i<rects.Count;i++){var r=rects[i];if(r.name!="reserved"&&(r.x0<region[0]||r.y0<region[1]||r.x1>region[2]||r.y1>region[3]))issues.Add("Outside content region: "+r.name);for(int k=i+1;k<rects.Count;k++){var s=rects[k];if(r.x0<s.x1&&r.x1>s.x0&&r.y0<s.y1&&r.y1>s.y0)issues.Add("Overlap: "+r.name+" / "+s.name);}}
        return new{proposal,issues,valid=issues.Count==0,units="sheet feet",limitation="Checks supplied moves and reserved rectangles. Include all existing sheet content in the proposal; text/detail annotations are not inferred."};
    }
    static object ApplyLayout(Document d,JsonElement a)
    {
        var check=Util.Json(Propose(d,a));if(!check.GetProperty("valid").GetBoolean())throw new ArgumentException("Proposed layout has overlaps or boundary violations.");var result=new List<object>();foreach(var move in a.GetProperty("moves").EnumerateArray()){var e=E(d,move,"element");Util.Editable(e);if(e is Viewport v){v.SetBoxCenter(P(move,"point"));d.Regenerate();result.Add(ViewportInfo(v));}else if(e is ScheduleSheetInstance s){s.Point=P(move,"point");d.Regenerate();result.Add(ScheduleInfo(s));}}
        var post=Propose(d,a);if(!Util.Json(post).GetProperty("valid").GetBoolean())throw new ArgumentException("Regenerated layout invalid; rolled back.");return new{elements=result,verification=post};
    }
    static object Compiled(UIApplication app,Document d,string op,JsonElement a)
    {
        var pluginRoot=Environment.GetEnvironmentVariable("CODEX_REVIT_PLUGIN_DIR");if(string.IsNullOrEmpty(pluginRoot))throw new NotSupportedException("Trusted compiled execution disabled. Configure CODEX_REVIT_PLUGIN_DIR explicitly.");
        if(Util.Get(a,"purpose")=="" || !a.TryGetProperty("expected_changes",out _))throw new ArgumentException("purpose and expected_changes required.");
        var path=Path.GetFullPath(Util.Get(a,"assembly"));var root=Path.GetFullPath(pluginRoot)+Path.DirectorySeparatorChar;if(!path.StartsWith(root,StringComparison.OrdinalIgnoreCase))throw new ArgumentException("Assembly outside configured plugin directory.");
        var type=Assembly.LoadFrom(path).GetType(Util.Get(a,"type"),true)!;if(!typeof(ICompiledOperation).IsAssignableFrom(type))throw new ArgumentException("Plugin must implement ICompiledOperation.");
        using var guard=op=="compiled.query"?new TransactionGroup(d,"Codex trusted query rollback guard"):null;guard?.Start();
        try{return ((ICompiledOperation)Activator.CreateInstance(type)!).Execute(app,d,a.GetProperty("arguments"));}finally{guard?.RollBack();}
    }
    static object Atomic(UIApplication app,Document d,JsonElement a)
    {
        var result=new List<object>();foreach(var step in a.GetProperty("steps").EnumerateArray()){foreach(var property in step.EnumerateObject())if(property.Name is not "operation" and not "arguments")throw new ArgumentException("Atomic native steps support operation/arguments only; dependency order and common preconditions must be resolved by the controller.");var op=Util.Get(step,"operation");if(!Names.Contains(op)||!Mutates(op)||Lifecycle(op)||op.StartsWith("family.")||op.StartsWith("compiled.")||op=="batch.atomic")throw new ArgumentException("Atomic batch supports predefined mutations in one document; lifecycle and plugins excluded.");result.Add(Execute(app,d,op,step.GetProperty("arguments")));}return new{steps=result};
    }
}
