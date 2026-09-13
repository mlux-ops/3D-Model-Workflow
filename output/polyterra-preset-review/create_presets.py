from pathlib import Path
import json,zipfile,subprocess
r=Path(__file__).resolve().parent
src=Path('C:/Users/found/Downloads/Process Presets/Process presets/SHB IM 0.08 PlateFace Monotonic Anti-Lift Inland PLA Basic @BBL H2D.json')
p=json.loads(src.read_text()); original=dict(p)
profiles=Path('C:/Program Files/Bambu Studio/resources/profiles/BBL')
def resolve(kind,name):
    d=json.loads((profiles/kind/(name+'.json')).read_text())
    merged=resolve(kind,d['inherits']) if d.get('inherits') else {}
    for inc in d.get('include',[]):merged.update(resolve(kind,inc))
    merged.update(d);merged.pop('include',None);return merged
def setval(d,k,v):
    old=d.get(k)
    d[k]=[str(v) if x!='nil' else 'nil' for x in old] if isinstance(old,list) else str(v)
p.update(type='process',name='SHB 0.08 PlateFace Quality PolyTerra PLA @BBL H2D',
         print_settings_id='SHB 0.08 PlateFace Quality PolyTerra PLA @BBL H2D')
changes={'layer_height':.08,'initial_layer_print_height':.2,'initial_layer_flow_ratio':1,
 'outer_wall_speed':35,'inner_wall_speed':60,'internal_solid_infill_speed':60,
 'top_surface_speed':25,'outer_wall_acceleration':800,'inner_wall_acceleration':1500,
 'travel_speed':300,'travel_acceleration':5000,'top_surface_pattern':'monotonicline'}
for k,v in changes.items():setval(p,k,v)
# The bridge setting is an H2D variant vector inherited from the system parent.
p['bridge_speed']=['25','25','25','25','nil']
f=resolve('filament','PolyTerra PLA @BBL H2D')
f.update(name='SHB PolyTerra PLA Quality @BBL H2D',inherits='PolyTerra PLA @BBL H2D',**{'from':'User'})
f['version']='2.7.0.8'
f['filament_settings_id']=[f['name']];f.pop('setting_id',None)
for k,v in {'nozzle_temperature':215,'nozzle_temperature_initial_layer':220,
 'textured_plate_temp':55,'textured_plate_temp_initial_layer':55,
 'filament_flow_ratio':.98,'filament_max_volumetric_speed':8,
 'additional_cooling_fan_speed':0,'close_fan_the_first_x_layers':2,
 'fan_min_speed':100,'fan_max_speed':100,'slow_down_layer_time':10,
 'slow_down_min_speed':15,'overhang_fan_speed':100}.items():setval(f,k,v)
pn='SHB_PolyTerra_H2D_Process.json';fn='SHB_PolyTerra_H2D_Filament.json'
for name,d in [(pn,p),(fn,f)]: (r/name).write_text(json.dumps(d,indent=4))
(r/'changes.json').write_text(json.dumps({k:{'before':original.get(k,'inherited'),'after':p[k]} for k in list(changes)+['bridge_speed']},indent=2))
# Validate import through the installed native slicer using a separate tiny project.
validation=r/'validation';validation.mkdir(exist_ok=True)
flat=resolve('process',p['inherits']);flat.update(p)
(validation/'process_flat.json').write_text(json.dumps(flat))
machine=resolve('machine','Bambu Lab H2D 0.4 nozzle');machine['inherits']=''
machine['extruder_nozzle_stats']=['Standard#1','Standard#1']
(validation/'machine_flat.json').write_text(json.dumps(machine))
args=['C:/Program Files/Bambu Studio/bambu-studio.exe',str(r.parent/'quietmount-v3-screwless/02_locking_key.stl'),
 '--load-settings',str(validation/'machine_flat.json')+';'+str(validation/'process_flat.json'),
 '--load-filaments',str(r/fn),'--curr-bed-type','Textured PEI Plate','--outputdir',str(validation),'--export-3mf','preset_import_check.3mf']
run=subprocess.run(args,capture_output=True,timeout=120)
assert run.returncode==0,run.returncode
with zipfile.ZipFile(validation/'preset_import_check.3mf') as z:
    c=json.loads(z.read('Metadata/project_settings.config'))
    assert float(c['layer_height'])==.08 and float(c['initial_layer_flow_ratio'])==1
    assert c['nozzle_temperature'][0]=='215' and c['textured_plate_temp'][0]=='55'
    assert c['outer_wall_speed'][0]=='35' and c['filament_max_volumetric_speed'][0]=='8'
print('Both presets accepted by native Bambu Studio; effective settings confirmed. No physical calibration performed.')
