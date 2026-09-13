from pathlib import Path
import zipfile,json
r=Path(__file__).resolve().parent
paths=[r/n for n in ['QuietMount_Capsule_H2D_READY.3mf','QuietMount_Capsule_H2D_Project.3mf','START_HERE.md',
 'capsule-installed.png','capsule-mechanism.png','plate-layout.png','geometry_checks.json','stl_checks.json','slice_summary.json']]
paths+=list(r.glob('*.stl'))+[r/'presets/QuietMount_Process.json',r/'presets/QuietMount_PolyTerra_PLA.json']
out=r/'QuietMount_Capsule_Five_Sets.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in paths:z.write(p,'QuietMount_Capsule/'+str(p.relative_to(r)).replace('\\','/'))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert sum(n.endswith('.stl') for n in z.namelist())==15
print('Packaged',len(paths),'files;',round(out.stat().st_size/1024/1024,2),'MB. ZIP integrity passed.')
