from pathlib import Path
import json,subprocess,shutil,zipfile
r=Path(__file__).resolve().parent;old=r.parent/'quietmount-mixed-screws'
for folder in ['presets','internal','sliced']:(r/folder).mkdir(exist_ok=True)
for f in (old/'presets').glob('*.json'):shutil.copyfile(f,r/'presets'/f.name)
shutil.copyfile(old/'internal/machine_H2D_04.json',r/'internal/machine_H2D_04.json')
params={'sparse_infill_density':'100%','sparse_infill_pattern':'zig-zag','enable_support':'0','brim_type':'outer_only','brim_width':'3','brim_object_gap':'0.15'}
objects=[{'path':str(r/f'{label}_19.05mm_upper_mushroom_REPAIRED.stl'),'count':1,'filaments':[1],'pos_x':[130+i*35],'pos_y':[140],'pos_z':[0],'print_params':params} for i,label in enumerate('BC')]
(r/'layout.json').write_text(json.dumps({'plates':[{'plate_name':'B and C replacement upper keepers','need_arrange':False,'objects':objects}]},indent=2))
exe='C:/Program Files/Bambu Studio/bambu-studio.exe'
p=subprocess.run([exe,'--load-assemble-list',str(r/'layout.json'),'--load-settings',str(r/'internal/machine_H2D_04.json')+';'+str(r/'presets/QuietMount_Process.json'),'--load-filaments',str(r/'presets/QuietMount_PolyTerra_PLA.json'),'--curr-bed-type','Textured PEI Plate','--outputdir',str(r),'--export-3mf','QuietMount_BC_Replacement_Project.3mf'],capture_output=True,timeout=180)
(r/'export.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0
p=subprocess.run([exe,str(r/'QuietMount_BC_Replacement_Project.3mf'),'--slice','0','--outputdir',str(r/'sliced'),'--export-3mf','QuietMount_BC_Replacement_READY.3mf'],capture_output=True,timeout=900)
(r/'slice.log').write_bytes(p.stdout+p.stderr);d=json.loads((r/'sliced/result.json').read_text());assert p.returncode==0 and d['return_code']==0
shutil.copyfile(r/'sliced/QuietMount_BC_Replacement_READY.3mf',r/'QuietMount_BC_Replacement_READY.3mf')
plate=d['sliced_plates'][0];summary={'minutes':round(plate['total_predication']/60),'grams':round(sum(f['total_used_g'] for f in plate['filaments']),1),'warnings':plate['warning_message']}
(r/'slice_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
with zipfile.ZipFile(r/'QuietMount_Upper_Repair_2026-09-14.zip','w',zipfile.ZIP_DEFLATED) as z:
 for pattern in ['*.stl','*.3mf','*.md','validation.json','slice_summary.json','build.py','presets/*.json']:
  for f in r.glob(pattern):z.write(f,str(f.relative_to(r)))
