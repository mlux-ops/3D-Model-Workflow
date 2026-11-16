using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using CodexNativeRevit;

public sealed class BedroomTrimInspect : ICompiledOperation
{
    static double[] Point(XYZ p) => new[] { p.X, p.Y, p.Z };
    static object Bounds(Element e)
    {
        var b=e.get_BoundingBox(null);
        return b==null ? null : new { min=Point(b.Min), max=Point(b.Max) };
    }
    static object CurveData(Curve c) => new { kind=c.GetType().Name, start=Point(c.GetEndPoint(0)), end=Point(c.GetEndPoint(1)), length=c.Length };
    static object[] SolidData(Element e)
    {
        var rows=new List<object>();
        void Walk(GeometryElement geometry)
        {
            foreach(var item in geometry)
            {
                if(item is GeometryInstance instance)Walk(instance.GetInstanceGeometry());
                else if(item is Solid solid && solid.Volume>0)
                    rows.Add(new { volume=solid.Volume, faces=solid.Faces.Cast<Face>().Select(face=>new {
                        kind=face.GetType().Name, area=face.Area,
                        origin=face is PlanarFace plane?Point(plane.Origin):null,
                        normal=face is PlanarFace planar?Point(planar.FaceNormal):null,
                        loops=face.GetEdgesAsCurveLoops().Select(loop=>loop.Select(CurveData).ToArray()).ToArray()
                    }).ToArray() });
            }
        }
        var geometry=e.get_Geometry(new Options{DetailLevel=ViewDetailLevel.Fine});
        if(geometry!=null)Walk(geometry);
        return rows.ToArray();
    }
    static object SketchData(Sketch s)
    {
        if(s==null)return null;
        return new { id=s.Id.Value, unique_id=s.UniqueId, normal=Point(s.SketchPlane.GetPlane().Normal), origin=Point(s.SketchPlane.GetPlane().Origin),
            loops=s.Profile.Cast<CurveArray>().Select(a=>a.Cast<Curve>().Select(CurveData).ToArray()).ToArray(),
            elements=s.GetAllElements().Select(id=>new { id=id.Value, type=s.Document.GetElement(id)?.GetType().Name, unique_id=s.Document.GetElement(id)?.UniqueId }).ToArray() };
    }
    public object Execute(UIApplication app, Document doc, JsonElement arguments)
    {
        if(doc.Title!="25-012 651 W. Belmont_Issue for Construction_")throw new InvalidOperationException("Wrong target model");
        var ids=arguments.GetProperty("elements").EnumerateArray().Select(x=>x.GetString()).ToArray();
        var rows=new List<object>();
        foreach(var uid in ids)
        {
            var e=doc.GetElement(uid)??throw new InvalidOperationException("Missing target "+uid);
            var fi=e as FamilyInstance;
            var sweep=e as WallSweep;
            var info=sweep?.GetWallSweepInfo();
            rows.Add(new { id=e.Id.Value, unique_id=e.UniqueId, kind=e.GetType().Name, bounds=Bounds(e),
                in_place=fi?.Symbol.Family.IsInPlace, family=fi?.Symbol.Family.Name,
                solids=SolidData(e),
                host_ids=sweep?.GetHostIds().Select(x=>x.Value).ToArray(),
                sweep_info=info==null?null:new { profile_id=info.ProfileId.Value, material_id=info.MaterialId.Value, distance=info.Distance, side=info.WallSide.ToString(), cut_by_inserts=info.IsCutByInserts, cuts_wall=info.CutsWall, offset=info.WallOffset, orientation=info.WallSweepOrientation.ToString() },
                dependents=e.GetDependentElements(null).Select(id=>{var item=doc.GetElement(id);return new {id=id.Value, unique_id=item.UniqueId,kind=item.GetType().Name,name=item.Name};}).ToArray() });
        }
        // Inspect accessible native sweep sketches. No transaction or model mutation.
        var sketches=new List<object>();
        foreach(Sweep sweep in new FilteredElementCollector(doc).OfClass(typeof(Sweep)))
        {
            var b=sweep.get_BoundingBox(null);
            if(b==null||b.Max.X<34||b.Min.X>60||b.Max.Y< -56||b.Min.Y> -55||b.Max.Z<38||b.Min.Z>47)continue;
            sketches.Add(new {id=sweep.Id.Value,unique_id=sweep.UniqueId,bounds=Bounds(sweep),profile=SketchData(sweep.ProfileSketch),path=SketchData(sweep.PathSketch)});
        }
        var rooms=new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
            .OfType<Autodesk.Revit.DB.Architecture.Room>().Where(r=>r.LevelId.Value==4209327)
            .Select(r=>new{id=r.Id.Value,unique_id=r.UniqueId,r.Name,r.Number,bounds=Bounds(r),area=r.Area}).ToArray();
        return new { targets=rows, native_sweep_sketches=sketches, rooms, saved=false, changed_elements=Array.Empty<long>() };
    }
}
