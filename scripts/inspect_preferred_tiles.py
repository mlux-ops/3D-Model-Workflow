import csv
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path('C:/Users/mlux/Downloads/651-belmont-bathroom-tiles/651-belmont-bathroom-tiles')
rows=[r for r in csv.DictReader((root/'TILES.csv').open()) if r['status'].strip().lower()=='preferred']
sheet=Image.new('RGB',(1200,400*((len(rows)+2)//3)), '#dddddd')
d=ImageDraw.Draw(sheet)
for i,r in enumerate(rows):
 im=Image.open(root/r['file']);im.thumbnail((380,350));x=(i%3)*400;y=(i//3)*400
 sheet.paste(im,(x+(400-im.width)//2,y+30));d.text((x+10,y+7),Path(r['file']).name,fill='black')
sheet.save('tmp/preferred_sources.jpg')
print(len(rows),'preferred image records')
