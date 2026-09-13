from pathlib import Path
import json,shutil,subprocess,zipfile,xml.etree.ElementTree as ET
r=Path(__file__).resolve().parent
src=r.parent/'quietmount-v5-capsule'
for folder in ['presets','internal','parts','sliced']:(r/folder).mkdir(exist_ok=True)
for n in ['QuietMount_Process.json','QuietMount_PolyTerra_PLA.json']:shutil.copyfile(src/'presets'/n,r/'presets'/n)
for n in ['lower_cover_snug.stl','upper_cover_snug.stl']:shutil.copyfile(src/n,r/n)
shutil.copyfile(src/'internal/machine_H2D_04.json',r/'internal/machine_H2D_04.json')
inventory=[];objects=[]
thicknesses=[12.7,19.05,19.05,20,22.225,20.5,18.5,18,14,17]
for i,t in enumerate(thicknesses):
 label=chr(65+i);x=45+(i%5)*48;y0=100+(i//5)*65
 for kind,dy,file,body in [('Lower_cover_SNUG',0,'lower_cover_snug.stl',False),('Upper_cover_SNUG',28,'upper_cover_snug.stl',False)]:
  name=f'{label}_{t:g}mm_{kind}';dst=r/'parts'/(name+'.stl');shutil.copyfile(r/file,dst)
  params={'sparse_infill_density':'100%','sparse_infill_pattern':'zig-zag','enable_support':'0','brim_type':'outer_only' if body else 'no_brim'}
  if body:params.update({'brim_width':'3','brim_object_gap':'0.15'})
  objects.append({'path':str(dst),'count':1,'filaments':[1],'pos_x':[x],'pos_y':[y0+dy],'pos_z':[0],'print_params':params})
  inventory.append({'set':label,'thickness_mm':t,'part':kind,'source':file,'x':x,'y':y0+dy})
assembly={'plates':[{'plate_name':'COVERS ONLY - 10 lower and 10 upper - snug','need_arrange':False,'objects':objects}]}
(r/'plate_layout.json').write_text(json.dumps(assembly,indent=2));(r/'inventory.json').write_text(json.dumps(inventory,indent=2))
exe='C:/Program Files/Bambu Studio/bambu-studio.exe'
args=[exe,'--load-assemble-list',str(r/'plate_layout.json'),'--load-settings',str(r/'internal/machine_H2D_04.json')+';'+str(r/'presets/QuietMount_Process.json'),'--load-filaments',str(r/'presets/QuietMount_PolyTerra_PLA.json'),'--curr-bed-type','Textured PEI Plate','--outputdir',str(r),'--export-3mf','QuietMount_Covers_Only_Project.3mf']
p=subprocess.run(args,capture_output=True,timeout=180);(r/'export.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0,p.returncode
p=subprocess.run([exe,str(r/'QuietMount_Covers_Only_Project.3mf'),'--slice','0','--outputdir',str(r/'sliced'),'--export-3mf','QuietMount_Covers_Only_READY.3mf'],capture_output=True,timeout=900)
(r/'slice.log').write_bytes(p.stdout+p.stderr)
d=json.loads((r/'sliced/result.json').read_text());assert p.returncode==0 and d['return_code']==0,d
shutil.copyfile(r/'sliced/QuietMount_Covers_Only_READY.3mf',r/'QuietMount_Covers_Only_READY.3mf')
z=zipfile.ZipFile(r/'QuietMount_Covers_Only_READY.3mf');m=ET.fromstring(z.read('Metadata/model_settings.config'))
obs=[{v.get('key'):v.get('value') for v in o.findall('metadata') if v.get('key')} for o in m.findall('object')]
assert len(obs)==20 and all(o['sparse_infill_density']=='100%' and o['sparse_infill_pattern']=='zig-zag' and o['enable_support']=='0' and 'cover_SNUG' in o['name'] for o in obs)
plate=d['sliced_plates'][0];assert len(d['sliced_plates'])==1 and len(plate['objects'])==20
assert not plate['warning_message'],plate['warning_message']
(r/'plate-layout.png').write_bytes(z.read('Metadata/plate_1.png'))
summary={'sets':10,'parts':20,'scope':'covers only; screw-mounted bodies awaiting measurements','plates':1,'minutes':round(plate['total_predication']/60),'grams':round(sum(f['total_used_g'] for f in plate['filaments']),1),'warnings':plate['warning_message'],'covers':'snug','future_body_thicknesses_mm':thicknesses}
(r/'slice_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
