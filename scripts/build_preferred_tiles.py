from pathlib import Path
import csv,json,shutil,hashlib
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
SRC=Path('C:/Users/mlux/Downloads/651-belmont-bathroom-tiles/651-belmont-bathroom-tiles')
OUT=ROOT/'output/belmont_preferred_bath2_bath3'
OUT.mkdir(parents=True,exist_ok=True)
rows=list(csv.DictReader((SRC/'TILES.csv').open()))
preferred=[r for r in rows if r['status'].strip().lower()=='preferred']
ids=list(dict.fromkeys(r['row_id'] for r in preferred))
assert ids==['B2-01','B2-02','B2-03','B3-01','B3-02','B3-03']
specs=[]
for id in ids:
 rr=[r for r in preferred if r['row_id']==id];r=rr[0]
 dest=OUT/id;tex=dest/'textures';tex.mkdir(parents=True,exist_ok=True)
 for srcrow in rr:
  sd=dest/'sources';sd.mkdir(exist_ok=True);shutil.copy2(SRC/srcrow['file'],sd/Path(srcrow['file']).name)
 source=SRC/(rr[1]['file'] if id=='B2-01' else r['file'])
 im=Image.open(source).convert('RGB')
 if id=='B2-01':
  boxes=[(30,30,1690,1660)];size=(6,6);gloss=.72;flutes=0
  note='Single tile photo; lower-edge white background excluded. Four rotations of same face, not four unique scans.'
 elif id=='B2-02':
  boxes=[(18,178,120,382),(127,178,229,382),(18,395,120,599),(127,395,229,599)];size=(5,10);gloss=.78;flutes=6
  note='Crops from installed panel: approximately 102 x 204 pixels per 5 x 10 tile; six scored strips inferred per tile. Baked reflections remain; estimated flute bump.'
 elif id=='B2-03':
  boxes=[(403,137,1517,1251)];size=(596/25.4,596/25.4);gloss=.18;flutes=0
  note='White margins removed from square product photo. Physical tile 596 x 596 mm; US store marketing size 23 x 23. Four rotations of one face.'
 elif id=='B3-02':
  boxes=[(165,616,333,1199),(350,616,516,1199),(538,616,703,1199),(724,616,880,1199)];size=(3,10);gloss=.55;flutes=10
  note='Perspective panel crops rectified to nominal 3 x 10. Approximately 156-168 x 583 pixels per face; ten flutes inferred. CSV height 2461 differs from actual supplied 1450. Exact gloss and relief depth unmeasured.'
 else:
  boxes=[(3,3,2397,1197)];size=(24,12);gloss=.16;flutes=0
  note='Matte 12 x 24 selection. Same source and map content for wall and floor assignments. Rotations limited to 0/180 degrees.'
 crops=[im.crop(b) for b in boxes]
 w,h=size;g=.0625;cw=int(round(900*(w+g)/max(w+g,h+g)));ch=int(round(900*(h+g)/max(w+g,h+g)))
 px=np.arange(cw,dtype=np.float32);py=np.arange(ch,dtype=np.float32)
 dx=np.minimum(px+.5,cw-px-.5)*(w+g)/cw;dy=np.minimum(py+.5,ch-py-.5)*(h+g)/ch
 edge=np.minimum(dx[None,:],dy[:,None]);alpha=np.clip((edge-g/2)/.025,0,1);alpha=alpha*alpha*(3-2*alpha)
 grout=np.array([178,176,165] if id!='B3-02' else [94,93,90],dtype=np.float32)
 color=np.zeros((ch*2,cw*2,3),np.uint8);height=np.zeros((ch*2,cw*2),np.float32)
 for n in range(4):
  c=crops[n%len(crops)]
  if len(crops)==1:c=c.rotate((n*90 if w==h else (n%2)*180),expand=True)
  # Mapping each photographed face into its exact tile area with half a grout joint on each repeat edge.
  tw=max(1,round(cw*w/(w+g)));th=max(1,round(ch*h/(h+g)))
  face=np.array(c.resize((tw,th),Image.Resampling.LANCZOS),dtype=np.float32)
  pad=np.pad(face,(((ch-th)//2,ch-th-(ch-th)//2),((cw-tw)//2,cw-tw-(cw-tw)//2),(0,0)),mode='edge')
  col=(pad*alpha[...,None]+grout*(1-alpha[...,None])).clip(0,255).astype(np.uint8)
  bump=alpha.copy()
  if flutes:
   u=np.clip(((px+.5)/cw*(w+g)-g/2)/w,0,1)
   curve=.5-.5*np.cos(2*np.pi*flutes*u)
   bump=alpha*(.72+.28*curve[None,:])
  yy=(n//2)*ch;xx=(n%2)*cw;color[yy:yy+ch,xx:xx+cw]=col;height[yy:yy+ch,xx:xx+cw]=bump
 Image.fromarray(color).save(tex/(id+'_Color.png'))
 Image.fromarray(np.round(height*65535).astype(np.uint16)).save(tex/(id+'_Bump.png'))
 preview=Image.fromarray(color);preview.thumbnail((700,700));preview.save(dest/'Preview.jpg',quality=93)
 spec={'id':id,'name':'651 Belmont - '+id+' - '+r['product'],'sku':r['sku'],'manufacturer':('MSI' if id=='B2-02' else 'Porcelanosa' if id=='B2-03' else 'ELM Surfaces'),'tile_inches':[w,h],'repeat_inches':[2*(w+g),2*(h+g)],'gloss':gloss,'color':[int(v) for v in color.mean(axis=(0,1))],'source':r['vendor_page'],'source_file':str(source),'native_crop_pixels':[[c.width,c.height] for c in crops],'crop_boxes':boxes,'pixels':[cw*2,ch*2],'notes':note,'layout':'Straight stack; 1/16 inch grout (assumed)','flutes':flutes}
 specs.append(spec)
 (dest/'NOTES.md').write_text(f"# {spec['name']}\n\nSKU: {r['sku']}\n\n{spec['layout']}. Tile {w:.5f} x {h:.5f} in; texture repeat {2*(w+g):.5f} x {2*(h+g):.5f} in.\n\n{note}\n\nGlossiness {gloss} and bump strength are visualization estimates. Photo color is not calibrated; this is not a measured PBR scan.\n\nProduct reference: {r['vendor_page']}\n",encoding='utf-8')
shutil.copy2(SRC/'TILES.csv',OUT/'SOURCE_TILES.csv')
(OUT/'manifest.json').write_text(json.dumps(specs,indent=2))
(OUT/'selection_audit.json').write_text(json.dumps({'filter':'status.strip().lower() == preferred','included_ids':ids,'excluded_ids':sorted(set(r['row_id'] for r in rows if r['status']!='preferred')),'material_assignments':6,'unique_products':5,'image_records':9,'source_csv_sha256':hashlib.sha256((SRC/'TILES.csv').read_bytes()).hexdigest()},indent=2))
sheet=Image.new('RGB',(1200,880),'#eeece7');draw=ImageDraw.Draw(sheet)
for n,s in enumerate(specs):
 im=Image.open(OUT/s['id']/'Preview.jpg');im.thumbnail((380,375));x=n%3*400;y=n//3*440
 sheet.paste(im,(x+(400-im.width)//2,y+45));draw.text((x+10,y+10),s['id']+' '+s['name'].split(' - ')[-1][:45],fill='black')
sheet.save(OUT/'Material_Overview.jpg',quality=94)
print(json.dumps({'materials':len(specs),'out':str(OUT)}))
