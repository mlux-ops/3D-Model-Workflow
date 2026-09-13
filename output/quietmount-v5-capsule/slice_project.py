from pathlib import Path
import subprocess,json,shutil
r=Path(__file__).resolve().parent;(r/'sliced').mkdir(exist_ok=True)
p=subprocess.run(['C:/Program Files/Bambu Studio/bambu-studio.exe',str(r/'QuietMount_Capsule_H2D_Project.3mf'),
 '--slice','0','--outputdir',str(r/'sliced'),'--export-3mf','QuietMount_Capsule_H2D_READY.3mf'],capture_output=True,timeout=900)
(r/'slice.log').write_bytes(p.stdout+p.stderr)
result=json.loads((r/'sliced/result.json').read_text())
print('Slice return',p.returncode,result.get('error_string'))
for plate in result.get('sliced_plates',[]):print(json.dumps(plate))
assert p.returncode==0 and result['return_code']==0
shutil.copyfile(r/'sliced/QuietMount_Capsule_H2D_READY.3mf',r/'QuietMount_Capsule_H2D_READY.3mf')
