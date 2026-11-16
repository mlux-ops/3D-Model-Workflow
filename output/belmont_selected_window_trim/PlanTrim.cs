using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using CodexNativeRevit;

public sealed class PlanTrim : ICompiledOperation
{
    static double[] V(XYZ p)=>new[]{p.X,p.Y,p.Z};
    static (XYZ Min,XYZ Max) Extents(Solid s)
    {
        var points=s.Edges.Cast<Edge>().SelectMany(e=>e.Tessellate()).ToArray();
        if(points.Length==0)throw new InvalidOperationException("Extent requested for empty solid, volume="+s.Volume+", faces="+s.Faces.Size);
        return (new XYZ(points.Min(p=>p.X),points.Min(p=>p.Y),points.Min(p=>p.Z)),new XYZ(points.Max(p=>p.X),points.Max(p=>p.Y),points.Max(p=>p.Z)));
    }
    static List<Solid> Solids(Element e)
    {
        var result=new List<Solid>();
        void Walk(GeometryElement g){foreach(var item in g){if(item is Solid s&&s.Volume>1e-10)result.Add(s);else if(item is GeometryInstance i)Walk(i.GetInstanceGeometry());}}
        Walk(e.get_Geometry(new Options{DetailLevel=ViewDetailLevel.Fine}));return result;
    }
    static Solid Box(double x0,double x1,double y0,double y1,double z0,double z1)
    {
        var pts=new[]{new XYZ(x0,y0,z0),new XYZ(x1,y0,z0),new XYZ(x1,y1,z0),new XYZ(x0,y1,z0)};
        var loop=new CurveLoop();for(int i=0;i<4;i++)loop.Append(Line.CreateBound(pts[i],pts[(i+1)%4]));
        return GeometryCreationUtilities.CreateExtrusionGeometry(new[]{loop},XYZ.BasisZ,z1-z0);
    }
    static object RefData(Document doc,Reference r)
    {
        var e=doc.GetElement(r.ElementId);var g=e?.GetGeometryObjectFromReference(r);
        return new {element_id=r.ElementId.Value,stable=r.ConvertToStableRepresentation(doc),kind=g?.GetType().Name,
            normal=g is PlanarFace p?V(p.FaceNormal):null,origin=g is PlanarFace q?V(q.Origin):null,
            edge=g is Edge edge?new[]{V(edge.AsCurve().GetEndPoint(0)),V(edge.AsCurve().GetEndPoint(1))}:null};
    }
    public object Execute(UIApplication app,Document doc,JsonElement args)
    {
        if(doc.Title!="25-012 651 W. Belmont_Issue for Construction_")throw new InvalidOperationException("Wrong model");
        var casing=doc.GetElement("0e5e1fa8-6b46-4fb4-a64a-e03decd36cde-00d77e2a");
        var bb=casing.get_BoundingBox(null);double left=bb.Min.X,right=bb.Max.X;
        if(Math.Abs(right-left-3)>1e-6)throw new InvalidOperationException("Casing changed; replan");
        var origin=new XYZ(34.39206524299543,-55.69033126642166,37.666666666666664);
        var cutter=Box(left,right,-57,-54,37,48);
        var targets=new[]{"a90217dd-fa42-44eb-bd0a-2c07a91eab57-00c87ad1","02e59096-cb94-4b8b-9416-b62fba27e642-00d0d34e","676af7a0-33d9-46b9-a8bb-d9537861af37-00cab9d1"};
        var parts=new List<object>();var targetRows=new List<object>();var allDeleted=new HashSet<long>();
        for(int t=0;t<targets.Length;t++)
        {
            var e=doc.GetElement(targets[t])??throw new InvalidOperationException("Missing source");Util.Editable(e);
            var sourceSolids=Solids(e);
            for(int sourceIndex=0;sourceIndex<sourceSolids.Count;sourceIndex++)
            {
                var source=sourceSolids[sourceIndex];var clipped=BooleanOperationsUtils.ExecuteBooleanOperation(source,cutter,BooleanOperationsType.Difference);
                var pieces=SolidUtils.SplitVolumes(clipped).Where(s=>s.Volume>1e-9).OrderBy(s=>Extents(s).Min.X).ToArray();
                for(int pieceIndex=0;pieceIndex<pieces.Length;pieceIndex++)
                {
                    var piece=pieces[pieceIndex];
                    if(t==0&&sourceIndex==0)
                    {
                        var sb=Extents(source);double rail=1.0/24;
                        var closure=pieceIndex==0?Box(left-rail,left,sb.Min.Y,sb.Max.Y,sb.Min.Z,sb.Max.Z):Box(right,right+rail,sb.Min.Y,sb.Max.Y,sb.Min.Z,sb.Max.Z);
                        piece=BooleanOperationsUtils.ExecuteBooleanOperation(piece,closure,BooleanOperationsType.Union);
                    }
                    // Wall molding is vertically extruded; its XY sketch preserves existing miters.
                    var axis=t==0?XYZ.BasisY:XYZ.BasisZ;
                    var startFace=piece.Faces.Cast<Face>().OfType<PlanarFace>().Where(f=>f.FaceNormal.DotProduct(axis)<-0.999999).OrderByDescending(f=>f.Area).FirstOrDefault();
                    if(startFace==null)throw new InvalidOperationException("No extrusion start face: target="+e.Id.Value+", source="+sourceIndex+", piece="+pieceIndex+", volume="+piece.Volume+", normals="+string.Join(";",piece.Faces.Cast<Face>().OfType<PlanarFace>().Select(f=>string.Join(",",V(f.FaceNormal)))));
                    var pb=Extents(piece);double length=t==0?pb.Max.Y-pb.Min.Y:pb.Max.Z-pb.Min.Z;
                    var loops=startFace.GetEdgesAsCurveLoops().Select(loop=>loop.Select(c=>V(c.GetEndPoint(0)-origin)).ToArray()).ToArray();
                    var reconstructed=GeometryCreationUtilities.CreateExtrusionGeometry(startFace.GetEdgesAsCurveLoops(),axis,length);
                    if(Math.Abs(reconstructed.Volume-piece.Volume)>1e-7)throw new InvalidOperationException("Source is not a matching native extrusion: target="+e.Id.Value+", solid="+sourceIndex+", piece="+pieceIndex+", length="+length+", measured="+piece.Volume+", reconstructed="+reconstructed.Volume);
                    string role=t==0?(sourceIndex==0?"Panel frame":"Lower panel infill"):t==1?"Crown":"Baseboard";
                    string side=pieceIndex==0?"Left":"Right";
                    var material=source.Faces.Cast<Face>().Select(f=>f.MaterialElementId).FirstOrDefault(id=>id!=ElementId.InvalidElementId);
                    parts.Add(new {name=role+" "+side,role,side,source_id=e.Id.Value,source_index=sourceIndex,plane=new{origin=V(startFace.Origin-origin),normal=V(axis)},profile=loops,length,expected_volume=piece.Volume,material_id=material?.Value,parameter=t==0?(sourceIndex==0?"Panel Frame Thickness":"Panel Infill Thickness"):role+" Height"});
                }
            }
            long[] deleted;
            using(var tx=new Transaction(doc,"Preview exact trim replacement dependencies")){tx.Start();deleted=doc.Delete(e.Id).Select(id=>id.Value).ToArray();tx.RollBack();}
            foreach(var id in deleted)allDeleted.Add(id);
            targetRows.Add(new{id=e.Id.Value,unique_id=e.UniqueId,expected_deleted_ids=deleted,
                dependencies=deleted.Select(id=>doc.GetElement(new ElementId(id))).Where(item=>item!=null).Select(item=>new{id=item.Id.Value,kind=item.GetType().Name,view_specific=item.ViewSpecific,view_id=item.OwnerViewId.Value,category=item.Category?.Name}).ToArray()});
        }
        var dimensions=allDeleted.Select(id=>doc.GetElement(new ElementId(id))).OfType<Dimension>().Where(d=>d.ViewSpecific && doc.GetElement(d.OwnerViewId) is View).Select(d=>new{
            id=d.Id.Value,unique_id=d.UniqueId,view_id=d.OwnerViewId.Value,type_id=d.GetTypeId().Value,
            curve=d.Curve is Line line?(line.IsBound?new[]{V(line.GetEndPoint(0)),V(line.GetEndPoint(1))}:new[]{V(line.Origin-line.Direction*100),V(line.Origin+line.Direction*100)}):null,
            value=d.Value,segments=d.Segments.Size,references=d.References.Cast<Reference>().Select(r=>RefData(doc,r)).ToArray(),
            above=d.Above,below=d.Below,prefix=d.Prefix,suffix=d.Suffix,value_override=d.ValueOverride
        }).ToArray();
        var dependentWall=doc.GetElement(new ElementId(13836440));var wb=dependentWall?.get_BoundingBox(null);
        var diagnostics=new {dependent_wall=dependentWall==null?null:new{id=dependentWall.Id.Value,unique_id=dependentWall.UniqueId,name=dependentWall.Name,bounds=wb==null?null:new{min=V(wb.Min),max=V(wb.Max)},parameters=dependentWall.Parameters.Cast<Parameter>().Where(p=>p.Definition.Name=="Comments"||p.Definition.Name=="Family"||p.Definition.Name=="Base Constraint").Select(p=>new{name=p.Definition.Name,value=p.AsValueString()??p.AsString()}).ToArray()},
            cut_support=targets.Select(uid=>doc.GetElement(uid)).Select(e=>new{id=e.Id.Value,void_cut=InstanceVoidCutUtils.CanBeCutWithVoid(e),solid_cut=SolidSolidCutUtils.IsAllowedForSolidCut(e)}).ToArray()};
        return new{origin=V(origin),opening=new{left,right},parts,targets=targetRows,dimensions,diagnostics,changed_elements=Array.Empty<long>()};
    }
}

public sealed class BuildTrim : ICompiledOperation
{
    static XYZ P(JsonElement e){var a=e.EnumerateArray().Select(v=>v.GetDouble()).ToArray();return new XYZ(a[0],a[1],a[2]);}
    public object Execute(UIApplication app,Document doc,JsonElement args)
    {
        if(!doc.IsFamilyDocument||!doc.IsModifiable)throw new InvalidOperationException("Requires new editable family transaction");
        if(new FilteredElementCollector(doc).OfClass(typeof(GenericForm)).Any())throw new InvalidOperationException("Family must contain no forms");
        doc.OwnerFamily.FamilyCategory=Category.GetCategory(doc,BuiltInCategory.OST_Casework);
        var fm=doc.FamilyManager;fm.NewType("Matched Belmont trim");
        var materialParameter=fm.AddParameter("Trim Finish",GroupTypeId.Materials,new ForgeTypeId("autodesk.spec.aec:material-1.0.0"),true);
        var localMaterial=Material.Create(doc,"Belmont trim finish - project matched");fm.Set(materialParameter,localMaterial);
        var parameters=new Dictionary<string,FamilyParameter>();var rows=new List<object>();
        foreach(var part in args.GetProperty("parts").EnumerateArray())
        {
            string name=part.GetProperty("name").GetString();var normal=P(part.GetProperty("plane").GetProperty("normal"));
            var plane=SketchPlane.Create(doc,Plane.CreateByNormalAndOrigin(normal,P(part.GetProperty("plane").GetProperty("origin"))));
            var profile=new CurveArrArray();
            foreach(var loop in part.GetProperty("profile").EnumerateArray())
            {
                var points=loop.EnumerateArray().Select(P).ToArray();var ca=new CurveArray();
                for(int i=0;i<points.Length;i++)ca.Append(Line.CreateBound(points[i],points[(i+1)%points.Length]));profile.Append(ca);
            }
            double length=part.GetProperty("length").GetDouble();
            var extrusion=doc.FamilyCreate.NewExtrusion(true,profile,plane,length);
            var subcategories=doc.OwnerFamily.FamilyCategory.SubCategories;Category subcategory;
            if(subcategories.Contains(name))subcategory=subcategories.get_Item(name);else subcategory=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,name);
            extrusion.Subcategory=subcategory;
            fm.AssociateElementParameterToFamilyParameter(extrusion.get_Parameter(BuiltInParameter.MATERIAL_ID_PARAM),materialParameter);
            string pn=part.GetProperty("parameter").GetString();
            if(!parameters.TryGetValue(pn,out var parameter)){parameter=fm.AddParameter(pn,GroupTypeId.Geometry,SpecTypeId.Length,false);fm.Set(parameter,length);parameters[pn]=parameter;}
            fm.AssociateElementParameterToFamilyParameter(extrusion.get_Parameter(BuiltInParameter.EXTRUSION_END_PARAM),parameter);
            doc.Regenerate();double volume=extrusion.get_Geometry(new Options()).OfType<Solid>().Sum(s=>s.Volume);
            double expected=part.GetProperty("expected_volume").GetDouble();
            if(Math.Abs(volume-expected)>1e-7)throw new InvalidOperationException("Native volume mismatch: "+name);
            if(extrusion.Sketch==null||extrusion.Sketch.Profile.Size==0)throw new InvalidOperationException("Native editable sketch missing");
            rows.Add(new{name,id=extrusion.Id.Value,unique_id=extrusion.UniqueId,volume,expected_volume=expected,editable_sketch_id=extrusion.Sketch.Id.Value,parameter=pn});
        }
        return new{forms=rows,all_native_editable_extrusions=true,material_parameter="Trim Finish",saved=false};
    }
}
