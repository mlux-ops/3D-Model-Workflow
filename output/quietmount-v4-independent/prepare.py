from pathlib import Path
__file__=str(Path(__file__).resolve())
source=(Path(__file__).resolve().parent.parent/'quietmount-bambu-h2d/prepare_project.py').read_text()
exec(source[:source.index('inventory=[]')])
process['name']=process['print_settings_id']='QuietMount Independent - PolyTerra 0.08 @H2D'
setvals(process,{'sparse_infill_density':'45%','sparse_infill_pattern':'rectilinear','enable_support':0,'brim_type':'no_brim'})
filament['version']='2.7.0.8'
for name,d in [('QuietMount_Process.json',process),('QuietMount_PolyTerra_PLA.json',filament)]:
 (ROOT/'presets'/name).write_text(json.dumps(d,indent=2))
objects=[]
for i,t in enumerate([12.7,19.05,19.05,20,22.225]):
 for j,kind in enumerate(['lower','lower','upper']):
  objects.append({'path':str(ROOT/f'{kind}_{t:g}mm.stl'),'count':1,'filaments':[1], 'pos_x':[55+i*43],'pos_y':[85+j*40],'pos_z':[0],'print_params':{'sparse_infill_density':'100%','sparse_infill_pattern':'rectilinear'}})
(ROOT/'plate_layout.json').write_text(json.dumps({'plates':[{'plate_name':'Five sample sets - two lower and one upper each','need_arrange':False,'objects':objects}]},indent=2))
args=[EXE,'--load-assemble-list',str(ROOT/'plate_layout.json'),'--load-settings',str(ROOT/'presets/machine_H2D_04.json')+';'+str(ROOT/'presets/QuietMount_Process.json'),'--load-filaments',str(ROOT/'presets/QuietMount_PolyTerra_PLA.json'),'--curr-bed-type','Textured PEI Plate','--outputdir',str(ROOT),'--export-3mf','QuietMount_Independent_H2D.3mf']
p=subprocess.run(args,capture_output=True,timeout=180)
(ROOT/'export.log').write_bytes(p.stdout+p.stderr)
assert p.returncode==0,p.returncode
print('Native Bambu project exported with fifteen clips on one plate.')
