"""Retain product-reference images and make labeled source contact sheets."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import json
import re
ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT/'SOURCE_COLLECTION.json').read_text()) + json.loads((ROOT/'OEM_COLLECTION.json').read_text())
selected = {}
for record in records:
    if 'error' not in record and 'lightology.com' in record.get('final_url',''):
        key = record['group']
        if key not in selected or Path(record['html_path']).name > Path(selected[key]['html_path']).name:
            selected[key] = record

def process(record):
    candidates=[]
    text=Path(record['html_path']).read_text(encoding='utf-8',errors='replace')
    candidates.extend(re.findall(r'<meta property="og:image" content="([^"]+)"',text,re.I))
    for image in record['images']:
        for name in ['data-src','src']:
            url=urljoin(record['final_url'],image.get(name) or '')
            if '/img/prod/' in url and any(s in url for s in ['/650/','/original/','/large/','/full/','/big/']) and url not in candidates:
                candidates.append(url)
    result={'key':record['group'],'title':record['title'],'page':record['final_url'],'candidates':candidates[:3]}
    text=Path(record['html_path']).read_text(encoding='utf-8',errors='replace')
    result['spec_link_markup']=re.findall(r'<[^>]*pdf_specsheet[^>]*>',text,re.I)[:5]
    for url in candidates[:2]:
        try:
            with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as response:
                data=response.read(15*1024*1024)
            image=Image.open(BytesIO(data)).convert('RGB')
            if max(image.size)<200:continue
            path=Path(record['html_path']).parent/'reference_product.jpg'
            image.save(path,quality=94)
            result.update({'image_path':str(path),'image_url':url,'pixels':list(image.size)})
            break
        except Exception as exc:
            result['image_error']=str(exc)
    return result

results=[]
with ThreadPoolExecutor(max_workers=4) as pool:
    for future in as_completed([pool.submit(process,r) for r in selected.values()]):
        result=future.result();results.append(result)
        print(result['key']+' | '+('image saved' if result.get('image_path') else result.get('image_error','No large image link')),flush=True)
(ROOT/'VISUAL_SOURCES.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
valid=sorted([r for r in results if r.get('image_path')],key=lambda r:r['key'])
try:font=ImageFont.truetype('arial.ttf',16)
except OSError:font=ImageFont.load_default()
for page in range(0,len(valid),12):
    canvas=Image.new('RGB',(1440,1280),'white');draw=ImageDraw.Draw(canvas)
    for idx,row in enumerate(valid[page:page+12]):
        x=(idx%4)*360;y=(idx//4)*420
        image=Image.open(row['image_path']);image.thumbnail((330,330))
        canvas.paste(image,(x+(360-image.width)//2,y+(340-image.height)//2))
        draw.text((x+10,y+345),row['key'][:40],fill='black',font=font)
        title=row['title'].split(' by ')[0]
        draw.text((x+10,y+370),title[:43],fill='black',font=font)
        draw.text((x+10,y+393),'PRODUCT REFERENCE',fill='black',font=font)
    canvas.save(ROOT/('reference_contact_%02d.jpg'%(page//12+1)),quality=93)
print('Reference images:',len(valid))
