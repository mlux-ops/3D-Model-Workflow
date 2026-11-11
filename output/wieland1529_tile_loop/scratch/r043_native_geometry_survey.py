"""Source-only native export survey; NEVER Revit calls or edits.

Visualize existing legally read-only Revit element BOUNDING BOXES as a plan
underlay so the architectural floor-plan evidence can be reconciled to world
coordinates. Do not infer that these rectangles equal hosted wall solids.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
SOURCE=json.loads((ROOT/'scratch/viewer3d_revit_sources.json').read_text(encoding='utf-8'))
OUTPUT=ROOT/'scratch'
XR=(-562.,-503.)
YR=(174.,262.)
SCALE=20
W=int((XR[1]-XR[0])*SCALE)
H=int((YR[1]-YR[0])*SCALE)
COLORS={'walls':(63,67,78,215),'doors':(206,128,61,150),
 'windows':(54,149,202,160),'plumbing':(63,196,173,215),
 'casework':(172,123,191,130),'floors':(100,100,100,35),'ceilings':(110,110,110,25)}
LEVELS={'LOWER':-5,'FIRST':6.6666667,'SECOND':17.3333333,
        'THIRD':28,'FOURTH':38.6666667}
try:FONT=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',14)
except OSError:FONT=ImageFont.load_default()

def P(x,y):
 return (int((x-XR[0])*SCALE),int((YR[1]-y)*SCALE))

def image_for(name,z):
 im=Image.new('RGB',(W,H),(245,247,248))
 dr=ImageDraw.Draw(im,'RGBA')
 for x in range(int(XR[0]),int(XR[1])+1,5):
  xx=P(x,YR[0])[0]
  dr.line([(xx,0),(xx,H)],fill=(205,213,218,180),width=1)
  dr.text((xx+3,3),str(x),fill=(44,69,88,255),font=FONT)
 for y in range(int(YR[0]),int(YR[1])+1,5):
  yy=P(XR[0],y)[1]
  dr.line([(0,yy),(W,yy)],fill=(205,213,218,180),width=1)
  dr.text((3,yy+3),str(y),fill=(44,69,88,255),font=FONT)
 counts={}
 for cat in ['walls','doors','windows','casework','plumbing']:
  count=0
  for obj in SOURCE['categories'][cat]['items']:
   box=obj.get('bounds')
   if not box:continue
   lo,hi=box.get('min'),box.get('max')
   if not lo or not hi:continue
   if hi[2]<z+.30 or lo[2]>z+10:continue
   if hi[0]<XR[0] or lo[0]>XR[1] or hi[1]<YR[0] or lo[1]>YR[1]:continue
   (x0,y1),(x1,y0)=P(lo[0],lo[1]),P(hi[0],hi[1])
   if abs(x1-x0)>1000 or abs(y1-y0)>1600:continue
   c=COLORS[cat]
   dr.rectangle([x0,y0,x1,y1],fill=(c[0],c[1],c[2],max(40,int(c[3]*.22))),
                outline=c,width=2 if cat=='walls' else 3)
   if cat=='plumbing':
    center=P((lo[0]+hi[0])/2,(lo[1]+hi[1])/2)
    dr.ellipse([center[0]-4,center[1]-4,center[0]+4,center[1]+4],
               fill=(23,137,102,255))
    dr.text((center[0]+4,center[1]-7),str(obj['id'])[-5:],fill=(15,78,65,255),font=FONT)
   count+=1
  counts[cat]=count
 dr.rectangle([W-500,8,W-10,96],fill=(255,255,255,235),outline=(81,94,104,255),width=2)
 dr.text((W-483,17),f'{name} floor | Revit z={z:.3f}ft',fill=(26,39,52,255),font=FONT)
 dr.text((W-483,42),'WALL grey   DOOR orange   WINDOW blue',fill=(40,56,69,255),font=FONT)
 dr.text((W-483,67),'CASEWORK purple   PLUMBING green',fill=(40,56,69,255),font=FONT)
 path=OUTPUT/f'r043_revit_{name.lower()}_bbox_plan.png';im.save(path)
 print(name,counts,path.name)

for name,z in LEVELS.items():image_for(name,z)
