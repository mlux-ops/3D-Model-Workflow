"""Summarize native gates and prepare labeled preview sheets for human/agent inspection."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json
ROOT=Path(__file__).resolve().parents[1]
target=ROOT/'_review';target.mkdir(exist_ok=True)
records=[];images=[]
for folder in sorted(ROOT.iterdir()):
    path=folder/'validation.json'
    if not path.exists():continue
    try:data=json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        records.append({'key':folder.name,'json_error':str(exc)});continue
    record={'key':folder.name,'pass':data.get('native_gates_pass',False),'expected':data.get('expected_dimensions_in'),
            'actual':data.get('actual_dimensions_in'),'reopened_mm':data.get('actual_dimensions_after_reopen_mm'),
            'gates':data.get('gates'),'error':data.get('error')}
    records.append(record)
    files=[Path(f) for f in data.get('evidence_files',[]) if 'Native Oblique' in str(f)]
    if not files:files=sorted((folder/'evidence').glob('*Native Oblique.png')) if (folder/'evidence').exists() else []
    for file in files[-1:]:
        if not file.is_absolute():file=folder/'evidence'/file
        if file.exists():images.append((folder.name,file,record['pass']))
(target/'native_summary.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
for start in range(0,len(images),6):
    canvas=Image.new('RGB',(1560,1560),'white');draw=ImageDraw.Draw(canvas)
    for offset,(key,path,passed) in enumerate(images[start:start+6]):
        x=(offset%2)*780;y=(offset//2)*520
        im=Image.open(path).convert('RGB');im=ImageOps.contain(im,(760,470))
        canvas.paste(im,(x+(780-im.width)//2,y+35+(470-im.height)//2))
        draw.text((x+15,y+12),key+' | native '+('PASS' if passed else 'HOLD'),fill='black')
    canvas.save(target/('contact_%02d.png'%(start//6+1)))
print(json.dumps({'models':len(records),'passed':sum(bool(r.get('pass')) for r in records),'preview_sheets':(len(images)+5)//6,
                  'failed':[r for r in records if not r.get('pass')]}))
