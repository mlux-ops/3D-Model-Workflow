using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Structure;
using Autodesk.Revit.UI;
using CodexNativeRevit;

public sealed class BuildWindowTrimCut : ICompiledOperation
{
    static XYZ P(JsonElement e){var a=e.EnumerateArray().Select(x=>x.GetDouble()).ToArray();return new XYZ(a[0],a[1],a[2]);}
    static CurveArrArray Profile(IEnumerable<XYZ> points)
    {
        var p=points.ToArray();var curves=new CurveArray();for(int i=0;i<p.Length;i++)curves.Append(Line.CreateBound(p[i],p[(i+1)%p.Length]));
        var result=new CurveArrArray();result.Append(curves);return result;
    }
    public object Execute(UIApplication app,Document doc,JsonElement args)
    {
        if(!doc.IsFamilyDocument||!doc.IsModifiable||new FilteredElementCollector(doc).OfClass(typeof(GenericForm)).Any())throw new InvalidOperationException("Requires empty native family transaction");
        doc.OwnerFamily.FamilyCategory=Category.GetCategory(doc,BuiltInCategory.OST_Casework);
        var allowCut=doc.OwnerFamily.get_Parameter(BuiltInParameter.FAMILY_ALLOW_CUT_WITH_VOIDS);
        if(allowCut==null||allowCut.IsReadOnly)throw new InvalidOperationException("Cut with voids parameter unavailable");allowCut.Set(1);
        var fm=doc.FamilyManager;fm.NewType("Fourth-floor primary bedroom window adaptation");
        var finish=fm.AddParameter("Trim Finish",GroupTypeId.Materials,new ForgeTypeId("autodesk.spec.aec:material-1.0.0"),true);
        var localMaterial=Material.Create(doc,"Belmont trim finish - project matched");fm.Set(finish,localMaterial);
        var top=fm.AddParameter("Opening Cut Top",GroupTypeId.Geometry,SpecTypeId.Length,false);fm.Set(top,9.5);
        var bottom=fm.AddParameter("Opening Cut Bottom",GroupTypeId.Geometry,SpecTypeId.Length,false);fm.Set(bottom,-1.0/12);
        var thickness=fm.AddParameter("Panel Molding Thickness",GroupTypeId.Geometry,SpecTypeId.Length,false);
        double depth=args.GetProperty("depth").GetDouble();fm.Set(thickness,depth);
        var voidPlane=SketchPlane.Create(doc,Plane.CreateByNormalAndOrigin(XYZ.BasisZ,XYZ.Zero));
        var cutter=doc.FamilyCreate.NewExtrusion(false,Profile(new[]{new XYZ(-1.5,-0.5,0),new XYZ(1.5,-0.5,0),new XYZ(1.5,0.5,0),new XYZ(-1.5,0.5,0)}),voidPlane,9.5);
        cutter.StartOffset=-1.0/12;
        fm.AssociateElementParameterToFamilyParameter(cutter.get_Parameter(BuiltInParameter.EXTRUSION_END_PARAM),top);
        fm.AssociateElementParameterToFamilyParameter(cutter.get_Parameter(BuiltInParameter.EXTRUSION_START_PARAM),bottom);
        var rails=new List<object>();
        foreach(var rail in args.GetProperty("rails").EnumerateArray())
        {
            var points=rail.GetProperty("profile").EnumerateArray().Select(P).ToArray();
            var plane=SketchPlane.Create(doc,Plane.CreateByNormalAndOrigin(XYZ.BasisY,new XYZ(0,-depth,0)));
            var solid=doc.FamilyCreate.NewExtrusion(true,Profile(points),plane,depth);
            var category=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,rail.GetProperty("name").GetString());solid.Subcategory=category;
            fm.AssociateElementParameterToFamilyParameter(solid.get_Parameter(BuiltInParameter.MATERIAL_ID_PARAM),finish);
            fm.AssociateElementParameterToFamilyParameter(solid.get_Parameter(BuiltInParameter.EXTRUSION_END_PARAM),thickness);
            doc.Regenerate();double volume=solid.get_Geometry(new Options()).OfType<Solid>().Sum(s=>s.Volume);
            var bounds=solid.get_BoundingBox(null);
            if(solid.Sketch==null||volume<=0)throw new InvalidOperationException("Editable border geometry missing");
            rails.Add(new {name=rail.GetProperty("name").GetString(),id=solid.Id.Value,unique_id=solid.UniqueId,volume,editable_sketch_id=solid.Sketch.Id.Value});
        }
        doc.Regenerate();
        return new {void_form_id=cutter.Id.Value,void_editable_sketch_id=cutter.Sketch.Id.Value,cut_with_voids_when_loaded=allowCut.AsInteger()==1,rails,native_form_count=new FilteredElementCollector(doc).OfClass(typeof(GenericForm)).GetElementCount(),saved=false};
    }
}

public sealed class ApplyWindowTrimCut : ICompiledOperation
{
    static XYZ P(JsonElement e){var a=e.EnumerateArray().Select(x=>x.GetDouble()).ToArray();return new XYZ(a[0],a[1],a[2]);}
    static List<Solid> Solids(Element e)
    {
        var rows=new List<Solid>();void Walk(GeometryElement g){foreach(var item in g){if(item is Solid s&&s.Volume>1e-10)rows.Add(s);else if(item is GeometryInstance i)Walk(i.GetInstanceGeometry());}}Walk(e.get_Geometry(new Options{DetailLevel=ViewDetailLevel.Fine}));return rows;
    }
    static double Volume(Element e)=>Solids(e).Sum(s=>s.Volume);
    public object Execute(UIApplication app,Document doc,JsonElement args)
    {
        if(doc.Title!="25-012 651 W. Belmont_Issue for Construction_"||!doc.IsModifiable)throw new InvalidOperationException("Wrong project or transaction");
        var sourceIds=new[]{"a90217dd-fa42-44eb-bd0a-2c07a91eab57-00c87ad1","02e59096-cb94-4b8b-9416-b62fba27e642-00d0d34e","676af7a0-33d9-46b9-a8bb-d9537861af37-00cab9d1"};
        var targets=sourceIds.Select(uid=>doc.GetElement(uid)??throw new InvalidOperationException("Missing trim source")).ToArray();
        foreach(var e in targets){Util.Editable(e);if(!InstanceVoidCutUtils.CanBeCutWithVoid(e))throw new InvalidOperationException("Source cannot receive native void cut");}
        var protectedWall=doc.GetElement("514788bb-91a0-470d-95a8-8895070891a2-00d32098");if(protectedWall==null)throw new InvalidOperationException("Protected wall missing");
        double wallVolume=Volume(protectedWall);var wallBounds=protectedWall.get_BoundingBox(null);
        var dimensions=new[]{13960635L,13960707L,13962280L}.Select(id=>doc.GetElement(new ElementId(id)) as Dimension??throw new InvalidOperationException("Expected dimension missing")).ToArray();
        var dimensionValues=dimensions.Select(d=>new{uid=d.UniqueId,value=d.Value}).ToArray();
        var casing=doc.GetElement("0e5e1fa8-6b46-4fb4-a64a-e03decd36cde-00d77e2a");var cb=casing.get_BoundingBox(null);
        var point=P(args.GetProperty("point"));if(Math.Abs(cb.Min.X-(point.X-1.5))>1e-6||Math.Abs(cb.Max.X-(point.X+1.5))>1e-6)throw new InvalidOperationException("Casing dimensions or position changed");
        var symbol=doc.GetElement(args.GetProperty("type").GetString()) as FamilySymbol??throw new InvalidOperationException("Explicit adaptation family type required");
        if(symbol.Family.Name!="SHB_Primary_Bedroom_Window_Trim_Adaptation_R2025")throw new InvalidOperationException("Unexpected family");
        if(new FilteredElementCollector(doc).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Any(fi=>fi.Symbol.Family.Id==symbol.Family.Id))throw new InvalidOperationException("Adaptation already placed; reconcile existing instance");
        if(!symbol.IsActive)symbol.Activate();doc.Regenerate();
        var level=(Level)doc.GetElement(new ElementId(4209327L));
        // This native level-based overload adds level elevation to the supplied Z.
        var instance=doc.Create.NewFamilyInstance(new XYZ(point.X,point.Y,point.Z-level.Elevation),symbol,level,StructuralType.NonStructural);
        var finish=instance.LookupParameter("Trim Finish");finish.Set(new ElementId(13056506L));
        instance.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set("Native editable void cuts and panel returns for fourth-floor Primary Bedroom 403 window group 14122480");
        doc.Regenerate();
        if(((LocationPoint)instance.Location).Point.DistanceTo(point)>1e-6)throw new InvalidOperationException("Native placement elevation does not match explicit target");
        if(!InstanceVoidCutUtils.IsVoidInstanceCuttingElement(instance))throw new InvalidOperationException("Loaded family has no eligible native void");
        var loop=new CurveLoop();var pts=new[]{new XYZ(cb.Min.X,point.Y-0.5,point.Z-1.0/12),new XYZ(cb.Max.X,point.Y-0.5,point.Z-1.0/12),new XYZ(cb.Max.X,point.Y+0.5,point.Z-1.0/12),new XYZ(cb.Min.X,point.Y+0.5,point.Z-1.0/12)};
        for(int i=0;i<4;i++)loop.Append(Line.CreateBound(pts[i],pts[(i+1)%4]));
        var cutter=GeometryCreationUtilities.CreateExtrusionGeometry(new[]{loop},XYZ.BasisZ,9.5+1.0/12);
        var expected=targets.Select(e=>new{uid=e.UniqueId,before=Volume(e),after=Solids(e).Sum(s=>BooleanOperationsUtils.ExecuteBooleanOperation(s,cutter,BooleanOperationsType.Difference).Volume)}).ToArray();
        foreach(var e in targets)InstanceVoidCutUtils.AddInstanceVoidCut(doc,e,instance);doc.Regenerate();
        var checks=targets.Select((e,index)=>new{unique_id=e.UniqueId,document_session_id=DocumentRegistry.Id(doc),id=e.Id.Value,before=expected[index].before,expected=expected[index].after,actual=Volume(e),linked=InstanceVoidCutUtils.GetCuttingVoidInstances(e).Contains(instance.Id)}).ToArray();
        if(checks.Any(c=>!c.linked||Math.Abs(c.actual-c.expected)>1e-6))throw new InvalidOperationException("Native cut volume does not match exact planned opening: "+JsonSerializer.Serialize(new{checks,placement=Util.Describe(instance)}));
        if(doc.GetElement(protectedWall.UniqueId)==null||Math.Abs(Volume(protectedWall)-wallVolume)>1e-7)throw new InvalidOperationException("Protected exterior wall changed");
        var afterBounds=protectedWall.get_BoundingBox(null);if(afterBounds.Min.DistanceTo(wallBounds.Min)>1e-7||afterBounds.Max.DistanceTo(wallBounds.Max)>1e-7)throw new InvalidOperationException("Protected wall bounds changed");
        foreach(var d in dimensionValues){var actual=doc.GetElement(d.uid) as Dimension;if(actual==null||actual.Value.HasValue!=d.value.HasValue||(actual.Value.HasValue&&Math.Abs(actual.Value.Value-d.value.Value)>1e-7))throw new InvalidOperationException("Existing dimension changed");}
        return new {instance=Util.Describe(instance),native_cut_checks=checks,preserved_dimension_ids=dimensions.Select(d=>d.Id.Value).ToArray(),protected_wall_id=protectedWall.Id.Value,wall_unchanged=true,deleted_elements=Array.Empty<long>(),saved=false};
    }
}

public sealed class PreviewWindowTrimCut : ICompiledOperation
{
    public object Execute(UIApplication app,Document doc,JsonElement args)
    {
        using(var tx=new Transaction(doc,"Preview bedroom window trim cuts"))
        {
            tx.Start();
            try{var result=new ApplyWindowTrimCut().Execute(app,doc,args);doc.Regenerate();tx.RollBack();return new{preview=true,data=result,transaction_status="rolled_back"};}
            catch{if(tx.GetStatus()==TransactionStatus.Started)tx.RollBack();throw;}
        }
    }
}
