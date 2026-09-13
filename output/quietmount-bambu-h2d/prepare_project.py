from pathlib import Path
import json,shutil,subprocess,zipfile
ROOT=Path(__file__).resolve().parent
SRC=ROOT.parent/'sample-holder-v2-minimal'
PROFILES=Path('C:/Program Files/Bambu Studio/resources/profiles/BBL')
EXE='C:/Program Files/Bambu Studio/bambu-studio.exe'
(ROOT/'presets').mkdir(exist_ok=True);(ROOT/'parts').mkdir(exist_ok=True)
def resolve(kind,name):
    d=json.loads((PROFILES/kind/(name+'.json')).read_text(encoding='utf-8'))
    result=resolve(kind,d['inherits']) if d.get('inherits') else {}
    for inc in d.get('include',[]):result.update(resolve(kind,inc))
    result.update(d);result.pop('include',None);return result
machine=resolve('machine','Bambu Lab H2D 0.4 nozzle');machine['inherits']=''
machine['extruder_nozzle_stats']=['Standard#1','Standard#1']
process=resolve('process','0.08mm Extra Fine @BBL H2D')
filament=resolve('filament','PolyTerra PLA @BBL H2D')
def setvals(d,updates):
    for k,v in updates.items():
        d[k]=[str(v)]*len(d[k]) if isinstance(d.get(k),list) else str(v)
process.update({'from':'User','name':'QuietMount - PolyTerra 0.08 Quality @H2D',
                'inherits':'0.08mm Extra Fine @BBL H2D','print_settings_id':'QuietMount - PolyTerra 0.08 Quality @H2D'})
process.pop('setting_id',None)
setvals(process,{'layer_height':.08,'initial_layer_print_height':.2,'wall_loops':6,
 'top_shell_layers':13,'bottom_shell_layers':10,'top_shell_thickness':1,'bottom_shell_thickness':.8,
 'sparse_infill_density':'45%','sparse_infill_pattern':'gyroid','outer_wall_speed':25,'inner_wall_speed':50,
 'top_surface_speed':25,'sparse_infill_speed':70,'internal_solid_infill_speed':50,'gap_infill_speed':30,
 'bridge_speed':25,'initial_layer_speed':20,'initial_layer_infill_speed':30,
 'default_acceleration':2500,'outer_wall_acceleration':800,'inner_wall_acceleration':1500,
 'top_surface_acceleration':800,'initial_layer_acceleration':400,'travel_acceleration':5000,
 'travel_speed':300,'resolution':.012,'elefant_foot_compensation':.15,'seam_position':'aligned',
 'top_surface_pattern':'monotonic','bottom_surface_pattern':'monotonic',
 'enable_support':0,'support_type':'normal(auto)','support_style':'snug','support_threshold_angle':30,
 'support_top_z_distance':.16,'support_bottom_z_distance':.16,'support_object_xy_distance':.35,
 'support_interface_top_layers':3,'support_interface_spacing':.2,'support_speed':45,
 'support_interface_speed':30,'support_on_build_plate_only':1,'bridge_no_support':1,
 'support_remove_small_overhang':0,'brim_type':'no_brim','brim_width':3,'brim_object_gap':.15,
 'enable_prime_tower':0,'print_sequence':'by layer','ironing_type':'no ironing'})
filament.update({'from':'User','name':'QuietMount - PolyTerra PLA Quality @H2D',
 'inherits':'PolyTerra PLA @BBL H2D','filament_settings_id':['QuietMount - PolyTerra PLA Quality @H2D']})
filament.pop('setting_id',None)
setvals(filament,{'nozzle_temperature':215,'nozzle_temperature_initial_layer':220,
 'textured_plate_temp':55,'textured_plate_temp_initial_layer':55,'filament_max_volumetric_speed':8,
 'additional_cooling_fan_speed':0,'fan_min_speed':100,'fan_max_speed':100,'close_fan_the_first_x_layers':1,
 'slow_down_layer_time':10,'slow_down_min_speed':15,'overhang_fan_speed':100})
for name,d in [('machine_H2D_04.json',machine),('QuietMount_Process.json',process),('QuietMount_PolyTerra_PLA.json',filament)]:
    (ROOT/'presets'/name).write_text(json.dumps(d,indent=2))

inventory=[]
def obj(src,label,x,y,params):
    dst=ROOT/'parts'/(label+'.stl');shutil.copyfile(SRC/src,dst)
    inventory.append({'name':label,'source':src,'x':x,'y':y,'settings':params})
    return {'path':str(dst),'count':1,'filaments':[1],'pos_x':[x],'pos_y':[y],'pos_z':[0],'print_params':params}
hooks=[]
for i,(label,t) in enumerate([('A','12.70'),('B','19.05'),('C','19.05'),('D','19.05'),('E','22.23')]):
    x=60+i*45
    params={'sparse_infill_density':'100%','sparse_infill_pattern':'rectilinear','enable_support':'0'}
    hooks.append(obj('lower_'+t+'mm.stl',label+'_'+t+'mm_lower_1',x,105,params))
    hooks.append(obj('lower_'+t+'mm.stl',label+'_'+t+'mm_lower_2',x,145,params))
    hooks.append(obj('upper_'+t+'mm.stl',label+'_'+t+'mm_upper',x,185,params))
structures=[]
for i,(x,y) in enumerate([(45,45),(135,45),(225,45),(90,155),(180,155)]):
    structures.append(obj('01_concealed_frame.stl','Frame_'+str(i+1),x,y,{'enable_support':'1'}))
for i,x in enumerate([60,110,160,210,260]):
    structures.append(obj('02_top_carriage.stl','Carriage_'+str(i+1),x,265,
                          {'enable_support':'1','support_on_build_plate_only':'0','brim_type':'outer_only','brim_width':'3','brim_object_gap':'0.15'}))
assembly={'plates':[{'plate_name':'01 - Small hooks - 5 sample sets','need_arrange':False,'objects':hooks},
                    {'plate_name':'02 - Concealed frames and carriages','need_arrange':False,'objects':structures}]}
(ROOT/'plate_layout.json').write_text(json.dumps(assembly,indent=2));(ROOT/'inventory.json').write_text(json.dumps(inventory,indent=2))
args=[EXE,'--load-assemble-list',str(ROOT/'plate_layout.json'),'--load-settings',str(ROOT/'presets/machine_H2D_04.json')+';'+str(ROOT/'presets/QuietMount_Process.json'),
      '--load-filaments',str(ROOT/'presets/QuietMount_PolyTerra_PLA.json'),'--curr-bed-type','Textured PEI Plate',
      '--outputdir',str(ROOT),'--export-3mf','QuietMount_H2D_PolyTerra_project.3mf']
print('Running Bambu Studio native project export',flush=True)
p=subprocess.run(args,capture_output=True,timeout=180)
(ROOT/'native_export.log').write_bytes(p.stdout+p.stderr)
print('Return:',p.returncode,'Project exists:',(ROOT/'QuietMount_H2D_PolyTerra_project.3mf').exists(),flush=True)
