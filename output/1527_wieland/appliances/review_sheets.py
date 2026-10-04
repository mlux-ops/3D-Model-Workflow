"""Assemble existing native preview evidence for visual inspection."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
models=json.loads((ROOT/'downloaded_models.json').read_text())
group='manufacturer'
if '--custom' in __import__('sys').argv:
    models=json.loads((ROOT/'custom_models.json').read_text())
    group='custom'
for start in range(0,len(models),6):
    canvas=Image.new('RGB',(1440,1080),'white')
    draw=ImageDraw.Draw(canvas)
    for j,model in enumerate(models[start:start+6]):
        paths=list((ROOT/model['slug']/'views').glob('placed_oblique*.png' if group=='manufacturer' else 'oblique*.png'))
        x=(j%3)*480;y=(j//3)*540
        draw.text((x+12,y+10),model['model'],fill='black')
        if paths:
            image=Image.open(paths[0]).convert('RGB')
            image.thumbnail((450,490))
            canvas.paste(image,(x+(480-image.width)//2,y+35+(490-image.height)//2))
        else:
            draw.text((x+12,y+60),'Preview absent',fill='black')
    path=ROOT/('review_%s_%d.png'%(group,start//6+1))
    canvas.save(path)
    print(path.name)
