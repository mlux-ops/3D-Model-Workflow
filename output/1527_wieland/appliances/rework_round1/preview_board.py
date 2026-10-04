"""Arrange actual native views for direct review."""
import json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
for c in json.loads((HERE/'configs.json').read_text()):
    folder=ROOT/c['slug']
    v=json.loads((folder/'source'/'rework_r1'/'validation.json').read_text())
    if not v.get('native_gates_pass'):
        print(c['slug']+': native gates not passed')
        continue
    board=Image.new('RGB',(1800,920),'white')
    draw=ImageDraw.Draw(board)
    for index,path in enumerate(v['previews']):
        im=ImageOps.contain(Image.open(path).convert('RGB'),(584,835))
        board.paste(im,(index*600+(600-im.width)//2,55+(835-im.height)//2))
        draw.text((index*600+12,12),c['model']+' / '+Path(path).stem.split(' - ')[0],fill='black')
    draw.text((12,896),'Complete native bounds W x D x H: '+' x '.join('%.3f'%x for x in v['placed_bounds']['xyz_size_mm'])+' mm',fill='black')
    path=HERE/(c['slug']+'_review.png')
    board.save(path)
    print(path.name)
