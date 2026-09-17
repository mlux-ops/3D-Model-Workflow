"""Prepare a rounded linear fixture from user references; reuse tested Revit scaffolding."""
from pathlib import Path
import shutil
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parents[1]
out=root/'output/linear24'
refs=root/'references/linear24'
(out/'textures').mkdir(parents=True,exist_ok=True)
refs.mkdir(parents=True,exist_ok=True)
sources={
 'product.jpg':r'C:\Users\mlux\Downloads\download (1).jpg',
 'dimensions.png':r'C:\Users\mlux\AppData\Local\Temp\codex-clipboard-2da0bc60-f572-4f1c-96d3-c192e2596fd3.png',
 'side.png':r'C:\Users\mlux\AppData\Local\Temp\codex-clipboard-07054346-0faa-4aaf-9a4a-1f400d0aa4d2.png',
 'vertical.png':r'C:\Users\mlux\AppData\Local\Temp\codex-clipboard-bc7d090b-f190-4e37-9e30-b0053c166606.png',
 'diffuser_detail.png':r'C:\Users\mlux\AppData\Local\Temp\codex-clipboard-4261bc60-1cb7-42d4-b07e-6f2ffd2f0c7c.png',
}
for name,path in sources.items():shutil.copy2(path,refs/name)
# Newly generated seamless microdot maps, an approximation of the visible regular pattern.
# Eight staggered rows per 0.32 inch tile; exact pitch and transmission are unmeasured.
for name,bg,dot in [('Linear24_Diffuser_Color.png',(255,247,221),(160,145,107)),('Linear24_Diffuser_Transmission.png',(90,90,90),(18,18,18))]:
 im=Image.new('RGB',(1024,1024),bg);draw=ImageDraw.Draw(im)
 for row in range(-1,9):
  for col in range(-1,9):
   x=col*128+(64 if row%2 else 0);y=row*128
   draw.ellipse((x-30,y-30,x+30,y+30),fill=dot)
 im.resize((512,512),Image.Resampling.LANCZOS).save(out/'textures'/name)
s=(root/'scripts/CinchBuilder.cs').read_text()
s=s.replace('CinchBuilder','Linear24Builder').replace('cinch','linear24').replace('Cinch','Linear24')
s=s.replace('Linear24_18_625_Brushed_Metal_R2025.rfa','Linear24_Black_Patterned_Diffuser_R2025.rfa')
s=s.replace('light?.28:.48','light?.30:.32').replace('Scalar(a,"generic_transparency",0);','Scalar(a,"generic_transparency",light?.25:0);')
s=s.replace('light?.04:.55','light?.04:.10').replace('light?.4:.85','light?.4:.45').replace('light?180:0','light?250:0').replace('3500','3000')
s=s.replace('scope.Commit(true);','''if(light) {
    Bitmap(a,"generic_diffuse","Linear24_Diffuser_Color.png");
    Bitmap(a,"generic_transparency","Linear24_Diffuser_Transmission.png");
    Scalar(a,"generic_diffuse_image_fade",1);Scalar(a,"generic_transparency_image_fade",1);
   }
   scope.Commit(true);''')
s=s.replace(' View3D View(',r'''
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
 View3D View(''')
s=s.replace('Min=P(-9.5,-1.6,.001),Max=P(9.5,1.6,2.6)','Min=P(-12.25,-2.7,.001),Max=P(12.25,2.7,3.3)')
s=s.replace('18 5-8 inch - Brushed Metal - Soft Glow','24 inch - Satin Black - Patterned Warm Diffuser')
s=s.replace('Linear24 - Satin Brushed Metal","new','Linear24 - Satin Black","new')
s=s.replace('Linear24 - Satin Brushed Metal','Linear24 - Satin Black').replace('new Color(178,175,165)','new Color(32,33,31)')
s=s.replace('Linear24 - Opal Diffuser Soft Glow','Linear24 - Patterned Light Guide').replace('new Color(250,248,243)','new Color(247,235,200)')
s=s.replace('{{"Overall Width",18.625},{"Body Height",2.375},{"Projection",2.5},{"Backplate Width",5.75},{"Overall Height",2.875},{"Backplate Depth",.875}}','{{"Overall Width",24},{"Body Height",.9},{"Projection",3.1},{"Backplate Width",4.3},{"Overall Height",5},{"Backplate Depth",.5}}')
s=s.replace('Front metal band, bar depth, standoff and seams inferred.','Bar height, rounded frame profile, plate thickness and microdot scale inferred.')
s=s.replace('Linear24 - 18 5/8 inch reference reconstruction','24 inch rounded linear wall light - reference reconstruction')
start=s.index('   Box("Backplate"')
end=s.index('   d.Regenerate();views=',start)
s=s[:start]+'''   Box("Rectangular backplate",-2.15,-2.5,0,2.15,2.5,.5,metal,mount);
   Rounded("Continuous rounded perimeter frame",-12,.48,12,3.1,.30,-.45,.90,.13,metal,housing);
   Rounded("Recessed patterned light-guide panel",-11.875,.605,11.875,2.975,.175,-.29,.08,0,diffuser,lens);
'''+s[end:]
s=s.replace('P(19,12,32)','P(16,-18,32)').replace('View("Top",P(0,35,1.25))','View("Diffuser Face",P(0,-35,1.25))')
s=s.replace('Math.Abs(w-18.625)','Math.Abs(w-24)').replace('Math.Abs(h-2.875)','Math.Abs(h-5)').replace('Math.Abs(z-2.5)','Math.Abs(z-3.1)')
s=s.replace('  Log("Family warnings: "+d.GetWarnings().Count);','''  Log("Family warnings: "+d.GetWarnings().Count);
  var dm=new FilteredElementCollector(d).OfClass(typeof(Material)).Cast<Material>().First(m=>m.Name=="Linear24 - Patterned Light Guide");
  var asset=((AppearanceAssetElement)d.GetElement(dm.AppearanceAssetId)).GetRenderingAsset();
  foreach(string key in new[]{"generic_diffuse","generic_transparency"}) {var path=((AssetPropertyString)asset.FindByName(key).GetSingleConnectedAsset().FindByName("unifiedbitmap_Bitmap")).Value;Log(key+" texture: "+path);if(!File.Exists(path))throw new Exception("Missing texture");}
''')
s=s.replace('project.Regenerate();}t.Commit();','''project.Regenerate();}
   ElementTransformUtils.RotateElement(project,inst.Id,Line.CreateUnbound(point,face.FaceNormal),Math.PI/2);project.Regenerate();
   bool vertical=Math.Abs(inst.GetTransform().BasisX.DotProduct(XYZ.BasisZ))>.9999;Log("Vertical rotation on wall face: "+vertical);if(!vertical)throw new Exception("Vertical placement failed");
   t.Commit();''')
(root/'scripts/Linear24Builder.cs').write_text(s)
compiler=(root/'scripts/compile_cinch.ps1').read_text().replace('CinchBuilder','Linear24Builder')
(root/'scripts/compile_linear24.ps1').write_text(compiler)
manifest=(root/'tmp/CinchTask.addin').read_text().replace('Cinch','Linear24').replace('A7313B90-3B61-4877-BBE7-F994D471D97A','7921EF80-3C01-49DE-9D47-A633E0E1D154')
(root/'tmp/Linear24Task.addin').write_text(manifest)
(root/'tmp/linear24.run').write_text('build')
print('Builder, textures, references and launch manifest prepared.')
