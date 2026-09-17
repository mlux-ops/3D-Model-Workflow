using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Visual;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Events;

namespace Linear24Builder {
public class App : IExternalApplication {
 public Result OnStartup(UIControlledApplication a) { a.Idling += Run; return Result.Succeeded; }
 public Result OnShutdown(UIControlledApplication a) { return Result.Succeeded; }
 void Run(object sender, IdlingEventArgs e) {
  var ui=(UIApplication)sender;
  ui.Idling -= Run;
  string trigger=Path.Combine(Builder.Root,"tmp","linear24.run");
  if(!File.Exists(trigger)) return;
  File.Delete(trigger);
  try { new Builder().Build(ui); } catch(Exception ex) {File.WriteAllText(Path.Combine(Builder.Out,"error.txt"),ex.ToString());}
 }
}
public class Builder {
 public const string Root=@"C:\Users\mlux\Documents\GitHub\3D-Model-Workflow";
 public static readonly string Out=Path.Combine(Root,"output","linear24");
 string rfa=Path.Combine(Out,"Linear24_Black_Patterned_Diffuser_R2025.rfa");
 List<string> log=new List<string>();
 Document d; FamilyParameter metal,diffuser;
 XYZ P(double x,double y,double z) {return new XYZ(x/12,y/12,z/12);}
 void Log(string s) {log.Add(s);File.WriteAllLines(Path.Combine(Out,"validation.txt"),log);}
 FreeFormElement Box(string name,double x0,double y0,double z0,double x1,double y1,double z1,FamilyParameter p,Category c) {
  var pts=new[]{P(x0,y0,z0),P(x1,y0,z0),P(x1,y1,z0),P(x0,y1,z0)};
  var loop=new CurveLoop();for(int i=0;i<4;i++)loop.Append(Line.CreateBound(pts[i],pts[(i+1)%4]));
  var solid=GeometryCreationUtilities.CreateExtrusionGeometry(new List<CurveLoop>{loop},XYZ.BasisZ,(z1-z0)/12);
  var f=FreeFormElement.Create(d,solid); f.Subcategory=c;
  d.FamilyManager.AssociateElementParameterToFamilyParameter(f.get_Parameter(BuiltInParameter.MATERIAL_ID_PARAM),p);
  Log("Part: "+name);return f;
 }
 void Scalar(Asset a,string key,double value) {var p=a.FindByName(key);if(p.NumberOfConnectedProperties>0)p.RemoveConnectedAsset();((AssetPropertyDouble)p).Value=value;}
 void ColorValue(Asset a,string key,Color color) {var p=a.FindByName(key);if(p.NumberOfConnectedProperties>0)p.RemoveConnectedAsset();((AssetPropertyDoubleArray4d)p).SetValueAsColor(color);}
 Material Mat(Autodesk.Revit.ApplicationServices.Application app,string name,Color color,bool light) {
  var source=app.GetAssets(AssetType.Appearance).First(a=>(a.FindByName("BaseSchema") as AssetPropertyString)?.Value=="GenericSchema");
  var ae=AppearanceAssetElement.Create(d,name,source);var m=(Material)d.GetElement(Material.Create(d,name));m.AppearanceAssetId=ae.Id;m.Color=color;
  using(var scope=new AppearanceAssetEditScope(d)) {
   var a=scope.Start(ae.Id);ColorValue(a,"generic_diffuse",color);
   Scalar(a,"generic_glossiness",light?.30:.32);Scalar(a,"generic_transparency",light?.25:0);
   Scalar(a,"generic_reflectivity_at_0deg",light?.04:.10);Scalar(a,"generic_reflectivity_at_90deg",light?.4:.45);
   Scalar(a,"generic_self_illum_luminance",light?250:0);
   if(light) {ColorValue(a,Generic.GenericSelfIllumFilterMap,new Color(255,250,242));Scalar(a,Generic.GenericSelfIllumColorTemperature,3000);}
   if(light) {
    Bitmap(a,"generic_diffuse","Linear24_Diffuser_Color.png");
    Bitmap(a,"generic_transparency","Linear24_Diffuser_Transmission.png");
    Scalar(a,"generic_diffuse_image_fade",1);Scalar(a,"generic_transparency_image_fade",1);
   }
   scope.Commit(true);
  }
  m.MaterialClass=light?"Plastic":"Metal";return m;
 }

 void Bitmap(Asset a,string key,string file) {
  var p=a.FindByName(key);if(p.NumberOfConnectedProperties>0)p.RemoveConnectedAsset();p.AddConnectedAsset("UnifiedBitmap");var b=p.GetSingleConnectedAsset();
  ((AssetPropertyString)b.FindByName("unifiedbitmap_Bitmap")).Value=Path.Combine(Out,"textures",file);
  foreach(string k in new[]{"texture_RealWorldScaleX","texture_RealWorldScaleY"}) {var q=(AssetPropertyDistance)b.FindByName(k);q.Value=UnitUtils.ConvertFromInternalUnits(.32/12,q.GetUnitTypeId());}
  foreach(string k in new[]{"texture_URepeat","texture_VRepeat"}) ((AssetPropertyBoolean)b.FindByName(k)).Value=true;
 }
 CurveLoop RoundLoop(double x0,double z0,double x1,double z1,double r,double y) {
  var pts=new[]{P(x0+r,y,z0),P(x1-r,y,z0),P(x1,y,z0+r),P(x1,y,z1-r),P(x1-r,y,z1),P(x0+r,y,z1),P(x0,y,z1-r),P(x0,y,z0+r)};
  double k=1-Math.Sqrt(.5);var mids=new[]{P(x1-r*k,y,z0+r*k),P(x1-r*k,y,z1-r*k),P(x0+r*k,y,z1-r*k),P(x0+r*k,y,z0+r*k)};
  var l=new CurveLoop();for(int i=0;i<8;i++){if(i%2==0)l.Append(Line.CreateBound(pts[i],pts[(i+1)%8]));else l.Append(Arc.Create(pts[i],pts[(i+1)%8],mids[i/2]));}return l;
 }
 FreeFormElement Rounded(string name,double x0,double z0,double x1,double z1,double r,double y,double thick,double border,FamilyParameter p,Category cat) {
  var loops=new List<CurveLoop>{RoundLoop(x0,z0,x1,z1,r,y)};
  if(border>0)loops.Add(RoundLoop(x0+border,z0+border,x1-border,z1-border,r-border,y));
  var solid=GeometryCreationUtilities.CreateExtrusionGeometry(loops,XYZ.BasisY,thick/12);
  var e=FreeFormElement.Create(d,solid);e.Subcategory=cat;d.FamilyManager.AssociateElementParameterToFamilyParameter(e.get_Parameter(BuiltInParameter.MATERIAL_ID_PARAM),p);Log("Part: "+name);return e;
 }
 View3D View(string name,XYZ eye,bool realistic=false) {
  var vt=new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(v=>v.ViewFamily==ViewFamily.ThreeDimensional);
  var v=View3D.CreateIsometric(d,vt.Id);v.Name=name;
  var f=P(0,0,1.25).Subtract(eye).Normalize();var up=XYZ.BasisY;if(Math.Abs(f.DotProduct(up))>.99)up=XYZ.BasisZ;
  var right=f.CrossProduct(up).Normalize();v.SetOrientation(new ViewOrientation3D(eye,right.CrossProduct(f).Normalize(),f));
  v.DetailLevel=ViewDetailLevel.Fine;v.DisplayStyle=realistic?DisplayStyle.Realistic:DisplayStyle.Shading;v.Scale=1;
  foreach(Category c in d.Settings.Categories) if(c.Id!=d.OwnerFamily.FamilyCategory.Id && v.CanCategoryBeHidden(c.Id))v.SetCategoryHidden(c.Id,true);
  var b=new BoundingBoxXYZ{Min=P(-12.25,-2.7,.001),Max=P(12.25,2.7,3.3)};v.SetSectionBox(b);v.IsSectionBoxActive=true;return v;
 }
 IEnumerable<Solid> Solids(GeometryElement g) {foreach(var obj in g) {if(obj is Solid s && s.Volume>1e-12)yield return s; if(obj is GeometryInstance gi)foreach(var q in Solids(gi.GetInstanceGeometry()))yield return q;}}
 public void Build(UIApplication ui) {
  Directory.CreateDirectory(Out);var app=ui.Application;Log("Revit "+app.VersionNumber);if(app.VersionNumber!="2025")throw new Exception("Requires Revit 2025");
  d=app.NewFamilyDocument(@"C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft");
  List<View3D> views;
  using(var t=new Transaction(d,"Build Linear24 fixture")) {t.Start();
   d.OwnerFamily.FamilyCategory=Category.GetCategory(d,BuiltInCategory.OST_LightingFixtures);d.OwnerFamily.get_Parameter(BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0);
   var fm=d.FamilyManager;fm.NewType("24 inch - Satin Black - Patterned Warm Diffuser");
   metal=fm.AddParameter("Metal Finish",GroupTypeId.Materials,SpecTypeId.Reference.Material,false);diffuser=fm.AddParameter("Diffuser Finish",GroupTypeId.Materials,SpecTypeId.Reference.Material,false);
   fm.Set(metal,Mat(app,"Linear24 - Satin Black",new Color(32,33,31),false).Id);fm.Set(diffuser,Mat(app,"Linear24 - Patterned Light Guide",new Color(247,235,200),true).Id);
   var dims=new Dictionary<string,double>{{"Overall Width",24},{"Body Height",.9},{"Projection",3.1},{"Backplate Width",4.3},{"Overall Height",5},{"Backplate Depth",.5}};
   foreach(var pair in dims) {var p=fm.AddParameter(pair.Key,GroupTypeId.Geometry,SpecTypeId.Length,false);fm.SetFormula(p,pair.Value.ToString(System.Globalization.CultureInfo.InvariantCulture)+"\"");}
   var notes=fm.AddParameter("Accuracy Notes",GroupTypeId.IdentityData,SpecTypeId.String.Text,false);fm.Set(notes,"Supplied dimensions authoritative. Bar height, rounded frame profile, plate thickness and microdot scale inferred. Fixed-size visualization, editable materials, no MEP or photometric source.");
   var model=fm.get_Parameter(BuiltInParameter.ALL_MODEL_MODEL);if(model!=null)fm.Set(model,"24 inch rounded linear wall light - reference reconstruction");
   var housing=d.Settings.Categories.NewSubcategory(d.OwnerFamily.FamilyCategory,"Housing");var mount=d.Settings.Categories.NewSubcategory(d.OwnerFamily.FamilyCategory,"Mount");var lens=d.Settings.Categories.NewSubcategory(d.OwnerFamily.FamilyCategory,"Diffusers");
   // Local X horizontal, Y vertical, +Z away from wall. Inch dimensions.
   Box("Rectangular backplate",-2.15,-2.5,0,2.15,2.5,.5,metal,mount);
   Rounded("Continuous rounded perimeter frame",-12,.48,12,3.1,.30,-.45,.90,.13,metal,housing);
   Rounded("Recessed patterned light-guide panel",-11.875,.605,11.875,2.975,.175,-.29,.08,0,diffuser,lens);
   d.Regenerate();views=new List<View3D>{View("Front",P(0,0,35)),View("Oblique",P(16,-18,32)),View("Side",P(35,0,1.25)),View("Diffuser Face",P(0,-35,1.25)),View("Material Review",P(16,-18,32),true)};t.Commit();
  }
  d.SaveAs(rfa,new SaveAsOptions{OverwriteExistingFile=true,MaximumBackups=1,PreviewViewId=views[1].Id});Log("Saved RFA");
  var opt=new ImageExportOptions{ExportRange=ExportRange.SetOfViews,FilePath=Path.Combine(Out,"Linear24"),HLRandWFViewsFileType=ImageFileType.PNG,ShadowViewsFileType=ImageFileType.PNG,ImageResolution=ImageResolution.DPI_150,ZoomType=ZoomFitType.FitToPage,PixelSize=1600};opt.SetViewsAndSheets(views.Select(v=>v.Id).ToList());d.ExportImage(opt);Log("Exported five native review views");
  d.Close(false);d=app.OpenDocumentFile(rfa);Log("Reopened: "+d.IsFamilyDocument+"; Category: "+d.OwnerFamily.FamilyCategory.Name+"; Placement: "+d.OwnerFamily.FamilyPlacementType);
  var forms=new FilteredElementCollector(d).OfClass(typeof(FreeFormElement)).Cast<FreeFormElement>().ToList();var boxes=forms.Select(f=>f.get_BoundingBox(null)).ToList();
  double w=(boxes.Max(b=>b.Max.X)-boxes.Min(b=>b.Min.X))*12,h=(boxes.Max(b=>b.Max.Y)-boxes.Min(b=>b.Min.Y))*12,z=(boxes.Max(b=>b.Max.Z)-boxes.Min(b=>b.Min.Z))*12;
  Log("Bounds inches: "+w+" x "+h+" x "+z);if(Math.Abs(w-24)>1e-5||Math.Abs(h-5)>1e-5||Math.Abs(z-3.1)>1e-5)throw new Exception("Bounds failed");
  Log("Family warnings: "+d.GetWarnings().Count);
  var dm=new FilteredElementCollector(d).OfClass(typeof(Material)).Cast<Material>().First(m=>m.Name=="Linear24 - Patterned Light Guide");
  var asset=((AppearanceAssetElement)d.GetElement(dm.AppearanceAssetId)).GetRenderingAsset();
  foreach(string key in new[]{"generic_diffuse","generic_transparency"}) {var path=((AssetPropertyString)asset.FindByName(key).GetSingleConnectedAsset().FindByName("unifiedbitmap_Bitmap")).Value;Log(key+" texture: "+path);if(!File.Exists(path))throw new Exception("Missing texture");}

  var project=app.NewProjectDocument(UnitSystem.Imperial);var family=d.LoadFamily(project);var symbol=(FamilySymbol)project.GetElement(family.GetFamilySymbolIds().First());
  using(var t=new Transaction(project,"Test wall face placement and materials")) {t.Start();
   var level=new FilteredElementCollector(project).OfClass(typeof(Level)).Cast<Level>().FirstOrDefault()??Level.Create(project,0);
   var wt=new FilteredElementCollector(project).OfClass(typeof(WallType)).Cast<WallType>().First(q=>q.Kind==WallKind.Basic);
   var wall=Wall.Create(project,Line.CreateBound(new XYZ(-5,0,0),new XYZ(5,0,0)),wt.Id,level.Id,9,0,false,false);symbol.Activate();project.Regenerate();
   var reference=HostObjectUtils.GetSideFaces(wall,ShellLayerType.Exterior)[0];var face=(PlanarFace)wall.GetGeometryObjectFromReference(reference);var point=face.Project(new XYZ(0,0,5)).XYZPoint;
   var inst=project.Create.NewFamilyInstance(reference,point,XYZ.BasisX,symbol);project.Regenerate();
   bool hosted=inst.Host!=null&&inst.Host.Id==wall.Id;double dot=inst.GetTransform().BasisZ.DotProduct(face.FaceNormal);Log("Native wall hosted: "+hosted+"; mounting normal dot: "+dot);if(!hosted||Math.Abs(dot-1)>1e-6)throw new Exception("Placement failed");
   foreach(string name in new[]{"Metal Finish","Diffuser Finish"}) {var p=symbol.LookupParameter(name);var old=p.AsElementId();var alt=Material.Create(project,"QA "+name);p.Set(alt);project.Regenerate();bool pass=Solids(inst.get_Geometry(new Options())).Any(s=>s.Faces.Cast<Face>().Any(f=>f.MaterialElementId==alt))||inst.GetMaterialIds(false).Contains(alt);Log(name+" substitution: "+pass);if(!pass)throw new Exception("Material test failed");p.Set(old);project.Regenerate();}
   ElementTransformUtils.RotateElement(project,inst.Id,Line.CreateUnbound(point,face.FaceNormal),Math.PI/2);project.Regenerate();
   bool vertical=Math.Abs(inst.GetTransform().BasisX.DotProduct(XYZ.BasisZ))>.9999;Log("Vertical rotation on wall face: "+vertical);if(!vertical)throw new Exception("Vertical placement failed");
   t.Commit();
  }
  Log("Project warnings: "+project.GetWarnings().Count);project.Close(false);d.Close(false);Log("COMPLETE");
 }
}
}
