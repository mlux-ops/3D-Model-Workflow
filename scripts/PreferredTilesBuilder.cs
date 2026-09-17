using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Text.Json;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Visual;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Events;
namespace PreferredTilesBuilder {
public class App:IExternalApplication {
 public Result OnStartup(UIControlledApplication a){a.Idling+=Run;return Result.Succeeded;}
 public Result OnShutdown(UIControlledApplication a){return Result.Succeeded;}
 void Run(object sender,IdlingEventArgs e){var ui=(UIApplication)sender;ui.Idling-=Run;string flag=Path.Combine(Builder.Root,"tmp","preferred.run");if(!File.Exists(flag))return;File.Delete(flag);try{new Builder().Build(ui);}catch(Exception ex){File.WriteAllText(Path.Combine(Builder.Out,"error.txt"),ex.ToString());}}
}
public class Builder {
 public const string Root=@"C:\Users\mlux\Documents\GitHub\3D-Model-Workflow";
 public static readonly string Out=Path.Combine(Root,"output","belmont_preferred_bath2_bath3");
 static string S(JsonElement s,string k)=>s.GetProperty(k).GetString();
 static double N(JsonElement s,string k,int index)=>s.GetProperty(k)[index].GetDouble();
 void Scalar(Asset a,string k,double v){var p=a.FindByName(k);if(p.NumberOfConnectedProperties>0)p.RemoveConnectedAsset();((AssetPropertyDouble)p).Value=v;}
 void Bitmap(Asset a,string key,JsonElement s,string suffix){var p=a.FindByName(key);if(p.NumberOfConnectedProperties>0)p.RemoveConnectedAsset();p.AddConnectedAsset("UnifiedBitmap");var b=p.GetSingleConnectedAsset();string id=S(s,"id");((AssetPropertyString)b.FindByName("unifiedbitmap_Bitmap")).Value=Path.Combine(Out,id,"textures",id+suffix);int i=0;foreach(string k in new[]{"texture_RealWorldScaleX","texture_RealWorldScaleY"}){var q=(AssetPropertyDistance)b.FindByName(k);q.Value=UnitUtils.ConvertFromInternalUnits(N(s,"repeat_inches",i++)/12,q.GetUnitTypeId());}foreach(string k in new[]{"texture_URepeat","texture_VRepeat"})((AssetPropertyBoolean)b.FindByName(k)).Value=true;}
 void Param(Material m,BuiltInParameter p,string v){var q=m.get_Parameter(p);if(q!=null&&!q.IsReadOnly)q.Set(v);}
 public void Build(UIApplication ui){
  var app=ui.Application;var specs=JsonDocument.Parse(File.ReadAllText(Path.Combine(Out,"manifest.json"))).RootElement.EnumerateArray().ToArray();
  var d=app.NewProjectDocument(UnitSystem.Imperial);var source=app.GetAssets(AssetType.Appearance).First(a=>(a.FindByName("BaseSchema") as AssetPropertyString)?.Value=="GenericSchema");
  using(var tx=new Transaction(d,"Create six preferred tile materials")){tx.Start();int index=0;
   foreach(var s in specs){string name=S(s,"name");var ae=AppearanceAssetElement.Create(d,name,source);var m=(Material)d.GetElement(Material.Create(d,name));m.AppearanceAssetId=ae.Id;m.Color=new Color((byte)N(s,"color",0),(byte)N(s,"color",1),(byte)N(s,"color",2));m.MaterialClass="Ceramic";m.Shininess=30;m.Smoothness=50;
    Param(m,BuiltInParameter.ALL_MODEL_MANUFACTURER,S(s,"manufacturer"));Param(m,BuiltInParameter.ALL_MODEL_MODEL,S(s,"sku"));Param(m,BuiltInParameter.ALL_MODEL_URL,S(s,"source"));Param(m,BuiltInParameter.ALL_MODEL_DESCRIPTION,"Preferred; "+S(s,"layout")+"; "+S(s,"notes"));
    using(var scope=new AppearanceAssetEditScope(d)){var a=scope.Start(ae.Id);Scalar(a,"generic_glossiness",s.GetProperty("gloss").GetDouble());Scalar(a,"generic_transparency",0);Scalar(a,"generic_reflectivity_at_0deg",.04);Scalar(a,"generic_reflectivity_at_90deg",1);Scalar(a,"generic_refraction_index",1.5);Scalar(a,"generic_diffuse_image_fade",1);Bitmap(a,"generic_diffuse",s,"_Color.png");Bitmap(a,"generic_bump_map",s,"_Bump.png");Scalar(a,"generic_bump_amount",.025);scope.Commit(true);}
    var pattern=new FillPattern(S(s,"id")+" tile grid",FillPatternTarget.Model,FillPatternHostOrientation.ToHost);var gx=new FillGrid(0,(N(s,"tile_inches",1)+.0625)/12);var gy=new FillGrid(Math.PI/2,(N(s,"tile_inches",0)+.0625)/12);pattern.SetFillGrids(new List<FillGrid>{gx,gy});m.SurfaceForegroundPatternId=FillPatternElement.Create(d,pattern).Id;m.SurfaceForegroundPatternColor=new Color(110,110,105);
    double x=index%3*5,y=-(index/3)*5;var pts=new[]{new XYZ(x,y,0),new XYZ(x+4,y,0),new XYZ(x+4,y+4,0),new XYZ(x,y+4,0)};var loop=new CurveLoop();for(int j=0;j<4;j++)loop.Append(Line.CreateBound(pts[j],pts[(j+1)%4]));var solid=GeometryCreationUtilities.CreateExtrusionGeometry(new List<CurveLoop>{loop},XYZ.BasisZ,.05,new SolidOptions(m.Id,ElementId.InvalidElementId));var ds=DirectShape.CreateElement(d,new ElementId(BuiltInCategory.OST_GenericModel));ds.Name=name;ds.SetShape(new List<GeometryObject>{solid});index++;
   }
   var vt=new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(v=>v.ViewFamily==ViewFamily.ThreeDimensional);var view=View3D.CreateIsometric(d,vt.Id);view.Name="Preferred tile swatches - Bath 2 top, Bath 3 bottom";view.SetOrientation(new ViewOrientation3D(new XYZ(7,-.5,30),XYZ.BasisY,-XYZ.BasisZ));view.DisplayStyle=DisplayStyle.Realistic;view.DetailLevel=ViewDetailLevel.Fine;
   tx.Commit();
  }
  string path=Path.Combine(Out,"651_Belmont_Preferred_Tiles_R2025.rvt");d.SaveAs(path,new SaveAsOptions{OverwriteExistingFile=true});d.Close(false);
  d=app.OpenDocumentFile(path);var mats=new FilteredElementCollector(d).OfClass(typeof(Material)).Cast<Material>().Where(m=>m.Name.StartsWith("651 Belmont - ")).ToArray();var report=new List<object>();
  foreach(var m in mats){var s=specs.Single(v=>S(v,"name")==m.Name);var a=((AppearanceAssetElement)d.GetElement(m.AppearanceAssetId)).GetRenderingAsset();var maps=new List<object>();foreach(string key in new[]{"generic_diffuse","generic_bump_map"}){var b=a.FindByName(key).GetSingleConnectedAsset();string file=((AssetPropertyString)b.FindByName("unifiedbitmap_Bitmap")).Value;if(!File.Exists(file))throw new Exception("Missing texture "+file);var scales=new List<double>();int i=0;foreach(string k in new[]{"texture_RealWorldScaleX","texture_RealWorldScaleY"}){var p=(AssetPropertyDistance)b.FindByName(k);double inches=UnitUtils.ConvertToInternalUnits(p.Value,p.GetUnitTypeId())*12;if(Math.Abs(inches-N(s,"repeat_inches",i++))>1e-6)throw new Exception("Scale mismatch");scales.Add(inches);}maps.Add(new {key,file,repeat_inches=scales});}if(m.SurfaceForegroundPatternId==ElementId.InvalidElementId)throw new Exception("Missing model pattern");report.Add(new{name=m.Name,maps,model_pattern=true});}
  int warnings=d.GetWarnings().Count;bool ok=mats.Length==6&&warnings==0;File.WriteAllText(Path.Combine(Out,"revit_validation.json"),JsonSerializer.Serialize(new{success=ok,version=app.VersionNumber,count=mats.Length,warnings,materials=report},new JsonSerializerOptions{WriteIndented=true}));d.Close(false);if(!ok)throw new Exception("Native validation failed");
 }
}
}
