from pathlib import Path
import json,shutil,subprocess,zipfile
r=Path(__file__).resolve().parent;src=r.parent/'quietmount-v5-capsule'
for f in ['presets','internal','sliced']:(r/f).mkdir(exist_ok=True)
for n in ['QuietMount_Process.json','QuietMount_PolyTerra_PLA.json']:shutil.copyfile(src/'presets'/n,r/'presets'/n)
shutil.copyfile(src/'internal/machine_H2D_04.json',r/'internal/machine_H2D_04.json')
items=json.loads((r/'inventory.json').read_text());bodies=[];covers=[]
def obj(path,x,y,body):
 p={'sparse_infill_density':'100%','sparse_infill_pattern':'zig-zag','enable_support':'0','brim_type':'outer_only' if body else 'no_brim'}
 if body:p.update({'brim_width':'3','brim_object_gap':'0.15'})
 return {'path':str(path),'count':1,'filaments':[1],'pos_x':[x],'pos_y':[y],'pos_z':[0],'print_params':p}
for j,item in enumerate(items):
 bodies.append(obj(r/item['file'],45+(j%5)*48,65+(j//5)*48,True))
 covers.append(obj(r/(item['kind']+'_cover_snug_revised.stl'),45+(j%5)*48,65+(j//5)*48,False))
layout={'plates':[{'plate_name':'20 bodies - 9 tapered and 11 mushroom','need_arrange':False,'objects':bodies},{'plate_name':'20 revised snug covers - use with these bodies','need_arrange':False,'objects':covers}]}
(r/'plate_layout.json').write_text(json.dumps(layout,indent=2))
exe='C:/Program Files/Bambu Studio/bambu-studio.exe'
p=subprocess.run([exe,'--load-assemble-list',str(r/'plate_layout.json'),'--load-settings',str(r/'internal/machine_H2D_04.json')+';'+str(r/'presets/QuietMount_Process.json'),'--load-filaments',str(r/'presets/QuietMount_PolyTerra_PLA.json'),'--curr-bed-type','Textured PEI Plate','--outputdir',str(r),'--export-3mf','QuietMount_Mixed_Screws_Project.3mf'],capture_output=True,timeout=180)
(r/'export.log').write_bytes(p.stdout+p.stderr)
if p.returncode:raise RuntimeError('Export failed: '+str(p.returncode))
p=subprocess.run([exe,str(r/'QuietMount_Mixed_Screws_Project.3mf'),'--slice','0','--outputdir',str(r/'sliced'),'--export-3mf','QuietMount_Mixed_Screws_READY.3mf'],capture_output=True,timeout=900)
(r/'slice.log').write_bytes(p.stdout+p.stderr)
d=json.loads((r/'sliced/result.json').read_text())
if p.returncode or d['return_code']:raise RuntimeError(str(d))
shutil.copyfile(r/'sliced/QuietMount_Mixed_Screws_READY.3mf',r/'QuietMount_Mixed_Screws_READY.3mf')
summary=[{'plate':i+1,'minutes':round(p['total_predication']/60),'grams':round(sum(f['total_used_g'] for f in p['filaments']),1),'warnings':p.get('warning_message')} for i,p in enumerate(d['sliced_plates'])]
(r/'slice_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
with zipfile.ZipFile(r/'QuietMount_Mixed_Screws_STLs.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in r.glob('*.stl'):z.write(f,f.name)
 z.write(r/'inventory.json','inventory.json')
