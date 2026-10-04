"""Create labeled reference/native evidence comparisons; no generated geometry."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
jobs=json.loads((ROOT/'REUSE_JOBS.json').read_text())+json.loads((ROOT/'CATALOG_JOBS.json').read_text())
jobs=[j for j in jobs if j['key']!='DP-WS-S1-AA04-30-10_TRIAC_120V-IP65']
jobs.insert(0,dict(key='57670WTBK',out=str(ROOT/'L4-0__8334187740856196')))
jobs.append(dict(key='DP-WS-S1-AA04-30-10_TRIAC_120V-IP65',out=str(ROOT/'B2-2__5960925969973124')))
try:font=ImageFont.truetype('arial.ttf',19)
except OSError:font=ImageFont.load_default()
rows=[]
for job in jobs:
    out=Path(job['out']);vp=out/'validation.json'
    if not vp.exists():continue
    validation=json.loads(vp.read_text())
    if not validation.get('technical_pass'):continue
    files=list((out/'evidence').glob('*_Isolated - 3D View - Native Material.png'))
    if not files:continue
    native=max(files,key=lambda f:f.stat().st_mtime)
    ref=out/'source/reference_product.jpg'
    if not ref.exists():
        group=next((g for g in json.loads((ROOT/'GROUPS.json').read_text())['groups'] if g['key']==job.get('group_key',job['key'])),None)
        if group:ref=ROOT/group['canonical_item']/'source/reference_product.jpg'
    rows.append(dict(key=job['key'],out=str(out),native=str(native),reference=str(ref) if ref.exists() else None,
                     rfa_sha256=hashlib.sha256(Path(validation['rfa_path']).read_bytes()).hexdigest()))
review=ROOT/'_review';review.mkdir(exist_ok=True)
for page in range(0,len(rows),4):
    canvas=Image.new('RGB',(1600,1840),'white');draw=ImageDraw.Draw(canvas)
    for i,row in enumerate(rows[page:page+4]):
        y=i*460
        draw.text((20,y+6),row['key'],fill='black',font=font)
        for col,key in [(0,'reference'),(1,'native')]:
            path=row[key]
            if path:
                image=Image.open(path).convert('RGB');image.thumbnail((750,395))
                canvas.paste(image,(col*800+(800-image.width)//2,y+38+(395-image.height)//2))
            draw.text((col*800+20,y+435),'PRODUCT REFERENCE' if col==0 else 'SAVED RFA: NATIVE REVIT MATERIAL VIEW',fill='black',font=font)
        row['review_sheet']='review_%02d.jpg'%(page//4+1)
    canvas.save(review/('review_%02d.jpg'%(page//4+1)),quality=94)
(review/'manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print('Prepared '+str(len(rows))+' verified-native candidates on '+str((len(rows)+3)//4)+' review sheets')
