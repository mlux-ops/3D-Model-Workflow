"""Build physical tile atlases from imagegen-derived, reference-matched glaze fields.
Procedural construction handles dimensions/grout/relief; sources remain unchanged.
"""
from pathlib import Path
import json, shutil, hashlib, sys
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'output/belmont_preferred_bath2_bath3'
OUT=ROOT/'output/belmont_preferred_bath2_bath3_r2'
GEN=ROOT/'references/belmont_preferred_derived_fields'
FILES={'B2-01':'exec-4bc5209c-3220-4188-8ff6-f315d9d504e0.png',
       'B2-02':'exec-a5bf8bce-857b-48dc-8186-1e306d699d7c.png',
       'B2-03':'exec-cef029ad-e237-4c9a-a1f2-c36048cde779.png',
       'B3-01':'exec-9d094076-2e47-4776-893b-9262a399c7dc.png',
       'B3-02':'exec-7867aa09-5c3d-4e4d-94ff-9fd34e798847.png'}
GRID={'B2-01':(32,32,256,256),'B2-02':(40,20,192,382),
      'B2-03':(8,8,1024,1024),'B3-01':(8,16,1024,514),
      'B3-02':(64,20,128,421),'B3-03':(8,16,1024,514)}
OUT.mkdir(exist_ok=True)
specs=json.loads(((OUT if len(sys.argv)>1 else OLD)/'manifest.json').read_text())
overview=Image.new('RGB',(1500,1100),'#eeece7');draw=ImageDraw.Draw(overview)
for index,s in enumerate(specs):
    id=s['id']; product='B3-01' if id=='B3-03' else id
    if len(sys.argv)>1 and id not in sys.argv[1:]:
        room=Image.open(OUT/id/'Room_15ft.jpg');room.thumbnail((480,480));ox=(index%3)*500;oy=(index//3)*550
        overview.paste(room,(ox+(500-room.width)//2,oy+55));draw.text((ox+12,oy+12),id+' '+s['name'].split(' - ')[-1][:45],fill='black');draw.text((ox+12,oy+30),'15 x 15 ft / diffuse only',fill='black')
        continue
    dest=OUT/id; tex=dest/'textures'; tex.mkdir(parents=True,exist_ok=True)
    shutil.copytree(OLD/id/'sources',dest/'sources',dirs_exist_ok=True)
    shutil.copy2(GEN/FILES[product],dest/'sources'/'derived_glaze_field.png')
    field=Image.open(dest/'sources'/'derived_glaze_field.png').convert('RGB')
    source=Image.open(OLD/id/'sources'/Path(s['source_file']).name).convert('RGB')
    ref=np.asarray(source.crop(tuple(s['crop_boxes'][0])),dtype=np.float32)
    # Match reference midtone, excluding grout/specular extremes. Relief is separate.
    target=np.median(ref.reshape(-1,3),axis=0)
    if id=='B3-02': target=np.array([42,39,40],dtype=np.float32)
    if id=='B2-02': target=np.array([79,101,91],dtype=np.float32)
    nx,ny,cw,ch=GRID[id]; w,h=s['tile_inches'];g=.0625
    color=np.empty((ch*ny,cw*nx,3),dtype=np.uint8)
    height=np.empty((ch*ny,cw*nx),dtype=np.uint16)
    rough=np.empty((ch*ny,cw*nx),dtype=np.uint8)
    px=np.arange(cw,dtype=np.float32);py=np.arange(ch,dtype=np.float32)
    dx=np.minimum(px+.5,cw-px-.5)*(w+g)/cw
    dy=np.minimum(py+.5,ch-py-.5)*(h+g)/ch
    edge=np.minimum(dx[None,:],dy[:,None])
    alpha=np.clip((edge-g/2)/.025,0,1);alpha=alpha*alpha*(3-2*alpha)
    # Exact periodic grout samples at every tile perimeter, not just atlas edges.
    alpha[[0,-1],:]=0;alpha[:,[0,-1]]=0
    grout=np.array([178,176,165] if id!='B3-02' else [74,73,71],dtype=np.float32)
    bump=alpha.copy();flutes=s['flutes'];score=None
    if flutes:
        u=np.clip(((px+.5)/cw*(w+g)-g/2)/w,0,1)
        curve=.5-.5*np.cos(2*np.pi*flutes*u)
        bump=alpha*(.72+.28*curve[None,:])
        if id=='B2-02':
            # Caraibi has pale scored divisions within each nominal 5-inch tile.
            distance=np.abs(u*flutes-np.round(u*flutes))*w/flutes
            score=np.clip((.035-distance)/.020,0,1)[None,:]*alpha
            bump=alpha*(1-.28*score)
    seed=6512025+index*101;rng=np.random.default_rng(seed);layout=[];used=set()
    for y in range(ny):
        for x in range(nx):
            # Independent spatial samples, scale and valid rotations; no fixed face cycle.
            while True:
                long=int(rng.integers(500,1100));sw=round(long*w/max(w,h));sh=round(long*h/max(w,h))
                sx=int(rng.integers(0,field.width-sw));sy=int(rng.integers(0,field.height-sh))
                angle=int(rng.integers(0,4))*90 if w==h else int(rng.integers(0,2))*180
                key=(sx,sy,sw,sh,angle)
                if key not in used:used.add(key);break
            face=field.crop((sx,sy,sx+sw,sy+sh)).rotate(angle,expand=True).resize((cw,ch),Image.Resampling.LANCZOS)
            a=np.asarray(face,dtype=np.float32);mean=a.mean(axis=(0,1))
            strength=.65 if id=='B2-03' else .82
            a=(a-mean)*strength+target+rng.uniform(-1.8,1.8)
            if score is not None:a=a*(1-score[...,None])+grout*score[...,None]
            col=np.clip(a*alpha[...,None]+grout*(1-alpha[...,None]),0,255).astype(np.uint8)
            yy=y*ch;xx=x*cw;color[yy:yy+ch,xx:xx+cw]=col
            height[yy:yy+ch,xx:xx+cw]=np.round(bump*65535).astype(np.uint16)
            r=np.clip((1-s['gloss'])+(a.mean(axis=2)-a.mean())*.0007,.04,.95)
            rough[yy:yy+ch,xx:xx+cw]=np.round((r*alpha+.85*(1-alpha))*255).astype(np.uint8)
            layout.append({'x':x,'y':y,'crop':[sx,sy,sw,sh],'rotation':angle})
    for label,a in [('Color',color),('Bump',height),('Roughness',rough)]:
        Image.fromarray(a).save(tex/f'{id}_{label}.png')
    s.update({'revision':2,'atlas_tiles':[nx,ny],'pixels':[cw*nx,ch*ny],
        'repeat_inches':[nx*(w+g),ny*(h+g)],'seed':seed,
        'variation_method':'Independent crops of imagegen-derived reference-matched glaze field; constrained rotations; no fixed face cycle',
        'derived_source_pixels':list(field.size),'authentic_unique_faces':len(s['crop_boxes']),
        'notes':s['notes']+' R2 replaces the 2x2 atlas with derived face variation. Generated variation is not additional manufacturer scans. See REVIEW.md.',
        'color':[int(v) for v in target]})
    (dest/'layout.json').write_text(json.dumps(layout))
    preview=Image.fromarray(color);preview.thumbnail((1000,1000));preview.save(dest/'Preview.jpg',quality=94)
    # 3x3 repeated atlas with wrap corners, then crop a 15-foot room-scale panel.
    tile=Image.fromarray(color);tile.thumbnail((600,600))
    repeated=Image.new('RGB',(tile.width*3,tile.height*3))
    for yy in range(3):
        for xx in range(3): repeated.paste(tile,(xx*tile.width,yy*tile.height))
    repeated.save(dest/'Wrap_3x3.jpg',quality=94)
    rw=round(180/s['repeat_inches'][0]*color.shape[1]);rh=round(180/s['repeat_inches'][1]*color.shape[0])
    room=Image.fromarray(color[:rh,:rw]);room.thumbnail((1200,1200));room.save(dest/'Room_15ft.jpg',quality=95)
    crop=Image.fromarray(color[:min(ch*2,color.shape[0]),:min(cw*3,color.shape[1])]);crop.thumbnail((1500,1200));crop.save(dest/'Closeup.jpg',quality=95)
    thumb=room.copy();thumb.thumbnail((480,480));ox=(index%3)*500;oy=(index//3)*550
    overview.paste(thumb,(ox+(500-thumb.width)//2,oy+55));draw.text((ox+12,oy+12),id+' '+s['name'].split(' - ')[-1][:45],fill='black')
    draw.text((ox+12,oy+30),'15 x 15 ft / diffuse only',fill='black')
    (dest/'NOTES.md').write_text(f"# {s['name']} — R2\n\nTile {w:.5f} x {h:.5f} in; grout 1/16 in; straight stack.\nAtlas {nx} x {ny} tiles ({s['repeat_inches'][0]:.5f} x {s['repeat_inches'][1]:.5f} in).\n\n{s['variation_method']}. Seed {seed}. Derived field {field.size}; exported {color.shape[1]} x {color.shape[0]}. Native source crop sizes: {s['native_crop_pixels']}. Upscaling does not recover photographed detail.\n\nColor/bump/roughness maps share layout and scale. Bump is 16-bit physical-pattern relief, not photographed lighting. Roughness companion is supplied for renderer setup; Revit Generic uses the recorded scalar gloss. Optical properties remain estimates.\n",encoding='utf-8')
    print(id,'built',color.shape,flush=True)
(OUT/'manifest.json').write_text(json.dumps(specs,indent=2))
for f in ['SOURCE_TILES.csv','selection_audit.json']:shutil.copy2(OLD/f,OUT/f)
overview.save(OUT/'Material_Overview.jpg',quality=95)
