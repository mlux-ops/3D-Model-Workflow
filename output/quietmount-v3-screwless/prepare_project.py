from pathlib import Path
source=(Path(__file__).resolve().parent.parent/'quietmount-bambu-h2d/prepare_project.py').read_text()
exec(source[:source.index('inventory=[]')])
SRC=ROOT
process['name']=process['print_settings_id']='QuietMount Screwless - PolyTerra 0.08 Quality @H2D'
filament['name']='QuietMount Screwless - PolyTerra PLA Quality @H2D'
filament['filament_settings_id']=[filament['name']]
filament['filament_colour']=['#494F49']
for name,d in [('QuietMount_Process.json',process),('QuietMount_PolyTerra_PLA.json',filament)]:
    (ROOT/'presets'/name).write_text(json.dumps(d,indent=2))
inventory=[]
def obj(src,label,x,y,params):
    dst=ROOT/'parts'/(label+'.stl');shutil.copyfile(SRC/src,dst)
    inventory.append({'name':label,'source':src,'x':x,'y':y,'settings':params})
    return {'path':str(dst),'count':1,'filaments':[1],'pos_x':[x],'pos_y':[y],'pos_z':[0],'print_params':params}
small=[];frames=[]
positions=[(45,40),(135,40),(225,40),(90,140),(180,140)]
wallparams={'enable_support':'0','ironing_type':'topmost','ironing_speed':'20','ironing_flow':'10%',
            'ironing_spacing':'0.1','ironing_inset':'0.2','sparse_infill_density':'45%'}
for i,(x,y) in enumerate(positions):
    small.append(obj('01_adhesive_wallplate.stl','Wallplate_'+str(i+1),x,y,wallparams))
for i,(label,t) in enumerate([('A','12.7'),('B','19.05'),('C','19.05'),('D','20'),('E','22.225')]):
    params={'enable_support':'1','support_on_build_plate_only':'0','sparse_infill_density':'100%',
            'sparse_infill_pattern':'rectilinear','brim_type':'outer_only','brim_width':'3'}
    small.append(obj('top_'+t+'mm.stl',label+'_Top_'+t+'mm',50+i*50,246,params))
    small.append(obj('02_locking_key.stl',label+'_Locking_key',50+i*50,287,
                     {'enable_support':'0','sparse_infill_density':'100%','sparse_infill_pattern':'rectilinear'}))
    x,y=positions[i]
    frames.append(obj('frame_'+t+'mm.stl',label+'_Frame_'+t+'mm',x,y,params))
assembly={'plates':[{'plate_name':'01 - Smooth adhesive plates, top hooks and keys','need_arrange':False,'objects':small},
                    {'plate_name':'02 - Five frames with integrated lower hooks','need_arrange':False,'objects':frames}]}
(ROOT/'plate_layout.json').write_text(json.dumps(assembly,indent=2))
(ROOT/'inventory.json').write_text(json.dumps(inventory,indent=2))
args=[EXE,'--load-assemble-list',str(ROOT/'plate_layout.json'),'--load-settings',
      str(ROOT/'presets/machine_H2D_04.json')+';'+str(ROOT/'presets/QuietMount_Process.json'),
      '--load-filaments',str(ROOT/'presets/QuietMount_PolyTerra_PLA.json'),'--curr-bed-type','Textured PEI Plate',
      '--outputdir',str(ROOT),'--export-3mf','QuietMount_Screwless_project.3mf']
p=subprocess.run(args,capture_output=True,timeout=180)
assert p.returncode==0,p.returncode
print('Native Bambu project exported: 20 parts, two plates.')
