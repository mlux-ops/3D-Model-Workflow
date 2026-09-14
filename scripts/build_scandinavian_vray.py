from pathlib import Path
import xml.etree.ElementTree as E
import base64
out=Path(__file__).resolve().parents[1]/'output/scandinavian'
root=E.Element('vrmat')
def asset(url,plugin,kind):
    a=E.SubElement(root,'Asset',renderer='vray',url=url,type=kind,layout='')
    ps=E.SubElement(E.SubElement(E.SubElement(a,'plugin'),'vrayplugin',name=plugin,type=kind,version='0'),'parameters')
    return a,ps
def param(ps,name,typ,val):
    v=E.SubElement(E.SubElement(ps,'parameter',handler='default',label=name,name=name,listType='none',type=typ),'value')
    if typ=='color':
        for k,n in zip('rgb',val):E.SubElement(v,k).text=str(n)
    else:v.text=str(val)
_,p=asset('/SettingsUnitsInfo','SettingsUnitsInfo','settings');param(p,'meters_scale','float',.01)
_,p=asset('/Adella/UVW','UVWGenChannel','UVW');param(p,'uvw_channel','integer',1)
for label,file,space in [('Color','Scandinavian_Color.png',2),('Normal','Scandinavian_Normal.png',0),('Roughness','Scandinavian_Roughness.png',0)]:
    _,p=asset('/Adella/'+label+'Buffer','BitmapBuffer','bitmap')
    param(p,'file','string','textures/'+file);param(p,'transfer_function','integer',space);param(p,'gamma','float',1)
    _,p=asset('/Adella/'+label,'TexBitmap','texture')
    param(p,'bitmap','plugin','/Adella/'+label+'Buffer');param(p,'uvwgen','plugin','/Adella/UVW');param(p,'tile','integer',1)
a,p=asset('/Adella/BRDF','BRDFVRayMtl','BRDF')
for name,typ,value in [('diffuse','acolor texture','/Adella/Color'),('reflect','color',(1,1,1)),('fresnel','bool',1),('fresnel_ior','float texture',1.5),('refract_ior','float texture',1.5),('metalness','float texture',0),('option_use_roughness','bool',1),('reflect_glossiness','float texture','/Adella/Roughness'),('bump_map','acolor texture','/Adella/Normal'),('bump_type','integer',1),('bump_amount','float texture',1)]:param(p,name,typ,value)
a,p=asset('/Scandinavian Decor Grey Hex 6x7','MtlSingleBRDF','material')
param(p,'brdf','plugin','/Adella/BRDF')
E.SubElement(a,'preview').text=base64.b64encode((out/'Pattern_Preview.jpg').read_bytes()).decode()
E.indent(root)
E.ElementTree(root).write(out/'Scandinavian_Decor_Grey.vrmat',encoding='utf-8',xml_declaration=True)
# Additional native material-only VRSCENE for hosts supporting material imports.
parts=['SettingsUnitsInfo Adella_units { meters_scale=0.01; }','UVWGenChannel Adella_uvw { uvw_channel=1; }']
for label,file,space in [('Color','Scandinavian_Color.png',2),('Normal','Scandinavian_Normal.png',0),('Roughness','Scandinavian_Roughness.png',0)]:
    parts.append(f'BitmapBuffer Adella_{label}_buffer {{ file="textures/{file}"; transfer_function={space}; gamma=1; }}')
    parts.append(f'TexBitmap Adella_{label} {{ bitmap=Adella_{label}_buffer; uvwgen=Adella_uvw; tile=1; }}')
parts.append('BRDFVRayMtl Adella_brdf { diffuse=Adella_Color; reflect=Color(1,1,1); fresnel=1; fresnel_ior=1.5; refract_ior=1.5; metalness=0; option_use_roughness=1; reflect_glossiness=Adella_Roughness; bump_map=Adella_Normal; bump_type=1; bump_amount=1; }')
parts.append('MtlSingleBRDF Scandinavian_Decor_Grey { brdf=Adella_brdf; }')
(out/'Scandinavian_Decor_Grey.vrscene').write_text('\n'.join(parts)+'\n')
vrmat=(out/'Scandinavian_Decor_Grey.vrmat').as_posix()
scene='''SettingsOutput output { img_width=800; img_height=400; }
SettingsImageSampler sampler { type=1; min_shade_rate=2; }
SettingsEnvironment env { bg_color=Color(0.5,0.5,0.5); gi_color=Color(1,1,1); }
SettingsGI gi { on=1; primary_engine=0; secondary_engine=0; }
RenderView camera { transform=Transform(Matrix(Vector(1,0,0),Vector(0,1,0),Vector(0,0,1)),Vector(0,0,150)); fov=0.85; }
LightRectangle softbox { transform=Transform(Matrix(Vector(1,0,0),Vector(0,1,0),Vector(0,0,1)),Vector(-50,70,100)); u_size=40; v_size=40; color=Color(1,1,1); intensity=10; invisible=1; }
GeomStaticMesh panel { vertices=ListVector(Vector(-61.11875,-30.63875,0),Vector(61.11875,-30.63875,0),Vector(61.11875,30.63875,0),Vector(-61.11875,30.63875,0)); faces=ListInt(0,1,2,0,2,3); map_channels=List(List(1,ListVector(Vector(0,0,0),Vector(2,0,0),Vector(2,2,0),Vector(0,2,0)),ListInt(0,1,2,0,2,3))); }
MtlVRmat tile { filename="VRMAT"; mtlname="/Scandinavian Decor Grey Hex 6x7"; }
Node wall { geometry=panel; material=tile; transform=Transform(Matrix(Vector(1,0,0),Vector(0,1,0),Vector(0,0,1)),Vector(0,0,0)); }
'''.replace('VRMAT',vrmat)
(out/'validation_scene.vrscene').write_text(scene)
print('VRMAT and native V-Ray validation scene created')
