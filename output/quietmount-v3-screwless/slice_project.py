from pathlib import Path
import subprocess,json
r=Path(__file__).resolve().parent;(r/'sliced').mkdir(exist_ok=True)
p=subprocess.run(['C:/Program Files/Bambu Studio/bambu-studio.exe',str(r/'QuietMount_Screwless_project.3mf'),
  '--slice','0','--outputdir',str(r/'sliced'),'--export-3mf','QuietMount_Screwless_H2D_READY.3mf'],capture_output=True,timeout=900)
print('Slice return',p.returncode)
result=json.loads((r/'sliced/result.json').read_text())
print(json.dumps({k:v for k,v in result.items() if k!='sliced_plates'},indent=2))
for plate in result.get('sliced_plates',[]):
    print({k:plate.get(k) for k in ['id','warning_message','total_predication','filaments']})
assert p.returncode==0 and result['return_code']==0
