"""2D planning diagnostic from native read-only bounding-box receipts."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];src=json.loads((P/'scratch/viewer3d_revit_sources.json').read_text())
C=src['categories']
for cut in (8,17,28,41):
 W,H=1200,2200
 im=Image.new('RGB',(W,H),'#f6f5ef');d=ImageDraw.Draw(im)
 left,right,bottom,top=-558,-507,162,272
 def xy(x,y):return (int((x-left)/(right-left)*W),int((top-y)/(top-bottom)*H))
 for key,c in (('walls','#454a50'),('doors','#b97145'),('windows','#51a7d0'),('casework','#c9b18f'),('plumbing','#214ba4')):
  for o in C[key]['items']:
   b=o.get('bounds')
   if not b:continue
   lo,hi=b['min'],b['max']
   if cut==8 and not (-1 <= lo[2] <= 9 and hi[2]>=7):continue
   if cut==17 and not (8 <= lo[2]<=19 and hi[2]>=16):continue
   if cut==28 and not (20<=lo[2]<=30 and hi[2]>=27):continue
   if cut==41 and not (30<=lo[2]<=43 and hi[2]>=40):continue
   a,bp=xy(lo[0],hi[1]);c2,e=xy(hi[0],lo[1])
   d.rectangle((a,bp,c2,e),fill=c if key=='walls' else None,outline=c,width=3 if key!='walls' else 1)
   if key=='plumbing':
    px,py=xy((lo[0]+hi[0])/2,(lo[1]+hi[1])/2)
    d.text((px+2,py),str(o['id'])[-4:]+':'+str(o['name'])[:8],fill=c,stroke_width=1,stroke_fill='white')
 # global mesh grid in internal feet, 10ft intervals
 for x in range(-550,-505,10):
  a,b=xy(x,top);c,e=xy(x,bottom)
  d.line([(a,b),(c,e)],fill='#d8d4c8',width=1);d.text((a+4,b+4),str(x),fill='#555')
 for y in range(170,275,10):
  a,b=xy(left,y);c,e=xy(right,y)
  d.line([(a,b),(c,e)],fill='#d8d4c8',width=1);d.text((a+4,b+4),str(y),fill='#555')
 d.rectangle((0,0,W,34),fill='#ffffff')
 d.text((12,9),'NATIVE REVIT bounding boxes at z~'+str(cut)+' ft; coordinate/room identity NOT established',fill='#111')
 dest=P/('scratch/viewer3d_context_z'+str(cut)+'.png')
 im.save(dest)
 print(dest)
