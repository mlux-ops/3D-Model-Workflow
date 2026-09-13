from pathlib import Path
__file__=str(Path(__file__).resolve())
source=(Path(__file__).resolve().parent.parent/'quietmount-bambu-h2d/prepare_project.py').read_text()
exec(source[:source.index('inventory=[]')])
process['name']=process['print_settings_id']='QuietMount Capsule - PolyTerra 0.08 @H2D'
process['version']='2.7.0.8'
setvals(process,{'sparse_infill_density':'100%','sparse_infill_pattern':'zig-zag','enable_support':0,
 'brim_type':'no_brim','resolution':.006,'initial_layer_speed':18,'initial_layer_infill_speed':25})
filament['name']='QuietMount Capsule - PolyTerra PLA @H2D'
filament['filament_settings_id']=[filament['name']];filament['version']='2.7.0.8'
setvals(filament,{'close_fan_the_first_x_layers':2,'filament_flow_ratio':.98})
for name,d in [('QuietMount_Process.json',process),('QuietMount_PolyTerra_PLA.json',filament)]:
 (ROOT/'presets'/name).write_text(json.dumps(d,indent=2))
(ROOT/'internal').mkdir(exist_ok=True)
shutil.move(str(ROOT/'presets/machine_H2D_04.json'),str(ROOT/'internal/machine_H2D_04.json'))
inventory=[]
def obj(src,label,x,y,body=False):
 dst=ROOT/'parts'/(label+'.stl');shutil.copyfile(ROOT/src,dst)
 params={'sparse_infill_density':'100%','sparse_infill_pattern':'zig-zag','enable_support':'0'}
 if body:params.update({'brim_type':'outer_only','brim_width':'3','brim_object_gap':'0.15'})
 inventory.append({'name':label,'source':src,'x':x,'y':y,'settings':params})
 return {'path':str(dst),'count':1,'filaments':[1],'pos_x':[x],'pos_y':[y],'pos_z':[0],'print_params':params}
fit=[]
for i,(src,label) in enumerate([('cover_fit_gauge.stl','FIT_gauge'),('upper_cover_easy.stl','FIT_easy'),('upper_cover.stl','FIT_standard'),('upper_cover_snug.stl','FIT_snug')]):
 fit.append(obj(src,label,70+i*45,90,i==0))
sets=[]
for i,(label,t) in enumerate(zip('ABCDE',[12.7,19.05,19.05,20,22.225])):
 x=55+i*45
 sets.append(obj(f'lower_{t:g}mm.stl',f'{label}_Lower_{t:g}mm',x,65,True))
 sets.append(obj(f'upper_{t:g}mm.stl',f'{label}_Upper_{t:g}mm',x,115,True))
 sets.append(obj('lower_cover.stl',f'{label}_Lower_cover',x,170))
 sets.append(obj('upper_cover.stl',f'{label}_Upper_cover',x,205))
assembly={'plates':[{'plate_name':'01 - Optional cover fit check: gauge, easy, standard, snug','need_arrange':False,'objects':fit},
 {'plate_name':'02 - Five capsule sets: lower, upper, two covers','need_arrange':False,'objects':sets}]}
(ROOT/'plate_layout.json').write_text(json.dumps(assembly,indent=2));(ROOT/'inventory.json').write_text(json.dumps(inventory,indent=2))
args=[EXE,'--load-assemble-list',str(ROOT/'plate_layout.json'),'--load-settings',str(ROOT/'internal/machine_H2D_04.json')+';'+str(ROOT/'presets/QuietMount_Process.json'),
 '--load-filaments',str(ROOT/'presets/QuietMount_PolyTerra_PLA.json'),'--curr-bed-type','Textured PEI Plate','--outputdir',str(ROOT),'--export-3mf','QuietMount_Capsule_H2D_Project.3mf']
p=subprocess.run(args,capture_output=True,timeout=180);(ROOT/'export.log').write_bytes(p.stdout+p.stderr)
assert p.returncode==0,p.returncode
print('Exported native two-plate H2D project: four optional fit pieces and twenty finished-set parts.')
