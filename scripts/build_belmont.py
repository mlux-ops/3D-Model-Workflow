from pathlib import Path
import numpy as np
from PIL import Image
import json, struct, zlib, xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'references/belmont_tiles'
OUT=ROOT/'output/belmont_tiles'; OUT.mkdir(exist_ok=True)
specs=[]
def source(pattern):
    p=next(REF.glob(pattern)); return np.asarray(Image.open(p).convert('RGB'),dtype=np.float32)/255,p
def sample(a,u,v):
    h,w=a.shape[:2];x=np.clip(u*(w-1),0,w-1);y=np.clip(v*(h-1),0,h-1)
    ix=x.astype(int);iy=y.astype(int);fx=(x-ix)[...,None];fy=(y-iy)[...,None]
    return (a[iy,ix]*(1-fx)+a[iy,np.minimum(ix+1,w-1)]*fx)*(1-fy)+(a[np.minimum(iy+1,h-1),ix]*(1-fx)+a[np.minimum(iy+1,h-1),np.minimum(ix+1,w-1)]*fx)*fy
def smooth(d,b=.025):
    t=np.clip(d/b,0,1);return t*t*(3-2*t)
def png16(path,a):
    h,w=a.shape[:2]
    def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    data=np.asarray(np.clip(a,0,1)*65535+.5,dtype='>u2')
    raw=b''.join(b'\0'+row.tobytes() for row in data)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,16,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
def finish(id,name,col,mask,rough,W,H,src,detail,tile,layout):
    p=OUT/id;t=p/'textures';t.mkdir(parents=True,exist_ok=True)
    h,w=mask.shape;height=.2+.6*mask
    Image.fromarray(np.uint8(np.clip(col,0,1)*255+.5)).save(t/'Color.png')
    Image.fromarray(np.uint16(height*65535+.5)).save(t/'Bump.png')
    # Periodic central differences in float; no quantized photographic height.
    dx=(np.roll(height,-1,1)-np.roll(height,1,1))*.25/(2*W*25.4/w)
    dy=(np.roll(height,-1,0)-np.roll(height,1,0))*.25/(2*H*25.4/h)
    normal=np.stack([-dx,dy,np.ones_like(dx)],2);normal/=np.linalg.norm(normal,axis=2)[...,None]
    png16(t/'Normal.png',normal*.5+.5)
    Image.fromarray(np.uint8(np.clip(rough,0,1)*255+.5)).save(t/'Roughness.png')
    im=Image.fromarray(np.uint8(np.clip(col,0,1)*255+.5));im.thumbnail((1000,1000));im.save(p/'Preview.jpg',quality=95)
    s=dict(id=id,name='Belmont - '+name,repeat_inches=[W,H],tile_inches=tile,pixels=[w,h],source=src.name,native_detail=detail,layout=layout,roughness=float(np.median(rough)),height_difference_mm=.15)
    specs.append(s);(p/'SPEC.json').write_text(json.dumps(s,indent=2))
    # Reuse established V-Ray graph with entirely unique identities.
    code=(ROOT/'scripts/build_scandinavian_vray.py').read_text().split("vrmat=(out/")[0]
    code=code.replace("'output/scandinavian'",repr('output/belmont_tiles/'+id)).replace('Scandinavian_Color.png','Color.png').replace('Scandinavian_Normal.png','Normal.png').replace('Scandinavian_Roughness.png','Roughness.png').replace('Pattern_Preview.jpg','Preview.jpg').replace('Scandinavian Decor Grey Hex 6x7',s['name']).replace('Scandinavian_Decor_Grey',id).replace('Adella',id)
    exec(compile(code,str(ROOT/'scripts/build_scandinavian_vray.py'),'exec'),{'__file__':str(ROOT/'scripts/build_scandinavian_vray.py')})
    (p/'README.md').write_text(f"# {name}\n\nTile/chip: {tile} inches. Layout: {layout}. Texture repeat: {W:.6f} x {H:.6f} inches. Set V-Ray UV channel 1 to these physical dimensions; do not scale a multi-tile repeat to one chip.\n\nColor uses {src.name}. Native source detail: {detail}. Export: {w} x {h}; resampling adds no photographic detail. Keep textures beside the VRMAT; Revit references this workspace's texture paths and needs repathing if moved.\n\nBump and RGB normal are 16-bit, calculated in floating point from smooth joints/edges, with estimated 0.15 mm relief. Printed veins remain flat. Displacement disabled. Normal is tangent-space OpenGL, linear/raw; roughness and bump linear/raw; color sRGB. Surface finish values are visual estimates, not measured PBR scans. Fine glaze/stone relief cannot be recovered reliably from one lit photo and is not fabricated from its luminance.\n\nUse the shared Belmont_New_Tiles_R2025.adsklib and select {s['name']}. Native V-Ray rendering requires a working Chaos license; no final native render is claimed.\n")
    print(id,detail,flush=True)
def rect(id,name,pattern,boxes,tw,th,nx,ny,rough=.6,offset=False):
    a,src=source(pattern);faces=[a[y0:y1,x0:x1] for x0,y0,x1,y1 in boxes]
    gap=.0625;px=tw+gap;py=th+gap;W=nx*px;H=ny*py
    w=4096 if W>=H else round(4096*W/H);h=4096 if H>=W else round(4096*H/W)
    col=np.full((h,w,3),.82,dtype=np.float32);mask=np.zeros((h,w),np.float32)
    for row in range(ny):
      for c in range(-1,nx+1):
        left=(c+(.5 if offset and row%2 else 0))*px
        xa=max(0,int(left/W*w));xb=min(w,int((left+px)/W*w)+1);ya=int(row*py/H*h);yb=min(h,int((row+1)*py/H*h)+1)
        if xa>=xb:continue
        yy,xx=np.mgrid[ya:yb,xa:xb];x=(xx+.5)*W/w-left-gap/2;y=(yy+.5)*H/h-row*py-gap/2
        m=smooth(np.minimum.reduce([x,tw-x,y,th-y]));face=faces[(row*nx+(c%nx))%len(faces)]
        cc=sample(face,x/tw,y/th);col[ya:yb,xa:xb]=col[ya:yb,xa:xb]*(1-m[...,None])+cc*m[...,None]
        mask[ya:yb,xa:xb]=np.maximum(mask[ya:yb,xa:xb],m)
    finish(id,name,col,mask,rough*mask+.85*(1-mask),W,H,src,','.join(str((f.shape[1],f.shape[0])) for f in faces),[tw,th],'half-offset rows' if offset else 'stacked grid')

# Crop real tile faces, excluding source grout/background; retain photographed variation.
rect('Domino_White_1x6','MSI Domino White Matte 1x6 Stack','Bath2_Accent*',[(180+65*i,125,229+65*i,488) for i in range(8)],1,6,12,2)
rect('Soreno_Ivory_2x2','MSI Soreno Ivory 2x2 Mosaic','Bath3_Accent*',[(x*200+7,y*200+7,x*200+190,y*200+190) for y in range(5) for x in range(5)],2,2,5,5)
rect('RAW_Greige_24x48','ELM RAW Greige 24x48 Matte','Bath3_Floor*',[(0,0,1594,797)],48,24,1,1)
rect('Clara_Bermuda_4x4','ELM Clara Bermuda 4x4 Glazed','Bath3_Wall*',[(x*245+25,y*245+25,x*245+245,y*245+245) for y in range(4) for x in range(4)],4,4,4,4,.28)
rect('Soreno_Ivory_24x48','MSI Soreno Ivory 24x48 Matte','PrimaryBath_Floor*',[(5,5,495,245),(505,5,995,245),(255,255,745,495),(5,505,495,745),(505,505,995,745)],48,24,2,2,.6,True)
rect('ElmStone_Jute_24x48','ELM ElmStone Jute Vein-Cut 24x48 Matte','PrimaryBath_Wall*',[(0,0,1890,945)],48,24,1,1)

def hexes(id,name,pattern,honey=False):
    a,src=source(pattern)
    # Flat-top lattice; transpose axes for point-up Honey Comb.
    R=3.5 if not honey else 2/np.sqrt(3);hh=6 if not honey else 2
    pitch=hh+.0625;rr=pitch*R/hh;W=3*rr;H=3*pitch
    if honey:W*=2
    w=round(4096*W/max(W,H));h=round(4096*H/max(W,H))
    col=np.full((h,w,3),.82,np.float32);mask=np.zeros((h,w),np.float32);rough=np.full((h,w),.85,np.float32)
    for q in range(-1,6 if honey else 4):
      for r in range(-4,6):
        cx=1.5*rr*q;cy=pitch*(r+q/2)
        xa=max(0,int((cx-R)/W*w)-2);xb=min(w,int((cx+R)/W*w)+3);ya=max(0,int((cy-hh/2)/H*h)-2);yb=min(h,int((cy+hh/2)/H*h)+3)
        if xa>=xb or ya>=yb:continue
        yy,xx=np.mgrid[ya:yb,xa:xb];x=(xx+.5)*W/w-cx;y=(yy+.5)*H/h-cy
        m=smooth(np.minimum(hh/2-abs(y),(R-abs(x)-abs(y)*R/hh)/np.sqrt(1+(R/hh)**2)))
        if honey:
            # Select real complete chips from the photographed sheet; transpose back later.
            idx=(q%4*3+(r+q//2)%3)%24;row=idx//4;cl=1+idx%4
            sx=63+158.2*cl+(79.1 if row%2 else 0);sy=94+136.5*row
            if sx>920:sx-=158.2
            cc=sample(a,(sx+y/(hh/2)*68)/999,(sy+x/R*78)/999)
            rv=[.62,.36,.52][idx%3]
        else:cc=sample(a,(x/R+1)/2,(y/(hh/2)+1)/2);rv=.6
        col[ya:yb,xa:xb]=col[ya:yb,xa:xb]*(1-m[...,None])+cc*m[...,None]
        mask[ya:yb,xa:xb]=np.maximum(mask[ya:yb,xa:xb],m);rough[ya:yb,xa:xb]=rough[ya:yb,xa:xb]*(1-m)+rv*m
    if honey:col=col.transpose(1,0,2);mask=mask.T;rough=rough.T;W,H=H,W
    finish(id,name,col,mask,rough,W,H,src,'approx. 136 x 156 pixels per chip' if honey else '1000 x 868 pixels per hex',[2,2.309401] if honey else [7,6],'point-up hex, varied real stone faces' if honey else 'plain flat-top hex')
hexes('Scandinavian_Grey_Plain','Ribesalbes Scandinavian Grey Plain 6x7','Bath2_Floor_ALT*')
hexes('Honey_Comb_2in_Hex','MSI Honey Comb 2in Hex Multi-Finish','PrimaryBath_Accent*',True)
(OUT/'manifest.json').write_text(json.dumps(specs,indent=2))


