from pathlib import Path
import numpy as np
from PIL import Image
import json, shutil, struct, zlib
root=Path(__file__).resolve().parents[1]; out=root/'output/scandinavian'; tex=out/'textures'
tex.mkdir(parents=True,exist_ok=True)
src=Path('C:/Users/found/OneDrive/Desktop/the-stones-more-group-scandinavian-decor-grey-1.jpg')
photo=Image.open(src).convert('RGB'); sw,sh=photo.size
# Flat-top 7-inch wide, 6-inch high tiles; three orientations meet at each star.
H=6.0625; R=H*7/12; W=3*R; HH=3*H
w,h=2389,4096
base=np.full((h,w,3),.88,dtype=np.float32); height=np.full((h,w),.2,dtype=np.float32)
for q in range(-1,4):
    for r in range(-4,5):
        cx=1.5*R*q; cy=H*(r+q/2)
        xa=max(0,int((cx-3.5)/W*w)-2); xb=min(w,int((cx+3.5)/W*w)+3)
        ya=max(0,int((cy-3)/HH*h)-2); yb=min(h,int((cy+3)/HH*h)+3)
        if xa>=xb or ya>=yb:continue
        y,x=np.mgrid[ya:yb,xa:xb]; X=(x+.5)*W/w-cx; Y=(y+.5)*HH/h-cy
        # Analytic smooth bevel and grout, independent of printed white artwork.
        d=np.minimum(3-np.abs(Y),(3.5-np.abs(X)-np.abs(Y)*7/12)/np.sqrt(1+(7/12)**2))
        t=np.clip(d/.025,0,1); mask=t*t*(3-2*t)
        # Match the shared-vertex three-tile fan/star arrangement in room photo.
        angle=-2*np.pi*((q+2*r)%3)/3
        c,s=np.cos(angle),np.sin(angle)
        # Rotate in regular-hex coordinates, then restore the 7:6 aspect ratio.
        xn=X/3.5; yn=Y/(3/np.sqrt(.75))
        u=c*xn+s*yn; v=-s*xn+c*yn
        # Bilinear sampling of the actual supplied photo, preserving its print.
        px=np.clip((u+1)*.5*(sw-1),0,sw-1); py=np.clip((v/np.sqrt(.75)+1)*.5*(sh-1),0,sh-1)
        ix=px.astype(int); iy=py.astype(int); fx=(px-ix)[:,:,None]; fy=(py-iy)[:,:,None]
        if 'a' not in globals():a=np.asarray(photo,dtype=np.float32)/255
        ix1=np.minimum(ix+1,sw-1);iy1=np.minimum(iy+1,sh-1)
        col=(a[iy,ix]*(1-fx)+a[iy,ix1]*fx)*(1-fy)+(a[iy1,ix]*(1-fx)+a[iy1,ix1]*fx)*fy
        region=base[ya:yb,xa:xb]; region[:]=region*(1-mask[:,:,None])+col*mask[:,:,None]
        height[ya:yb,xa:xb]=np.maximum(height[ya:yb,xa:xb],.2+.6*mask)
Image.fromarray(np.uint8(np.clip(base,0,1)*255+.5)).save(tex/'Scandinavian_Color.png')
Image.fromarray(np.uint16(height*65535+.5)).save(tex/'Scandinavian_Bump.png')
dy,dx=np.gradient(height*.25,HH*25.4/h,W*25.4/w)
n=np.stack([-dx,dy,np.ones_like(dx)],2);n/=np.linalg.norm(n,axis=2)[:,:,None]
data=np.asarray((n*.5+.5)*65535+.5,dtype='>u2')
def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
raw=b''.join(b'\0'+row.tobytes() for row in data)
(tex/'Scandinavian_Normal.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,16,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
Image.fromarray(np.uint8(np.where(height>.7,.6,.85)*255)).save(tex/'Scandinavian_Roughness.png')
preview=Image.fromarray(np.uint8(base*255)).resize((530,910))
panel=Image.new('RGB',(1060,910));panel.paste(preview,(0,0));panel.paste(preview,(530,0));panel.save(out/'Pattern_Preview.jpg',quality=95)
(out/'map_spec.json').write_text(json.dumps({'tile_inches':[7,6],'joint_inches':.0625,'repeat_inches':[W,HH],'pixels':[w,h],'source_pixels':[sw,sh],'orientations_degrees':[0,120,240],'layout':'three hexagon fans meet at shared vertices, matching supplied installation','bump':'joints and smooth bevel only; printed design remains flat','depth_range_mm':.25},indent=2))
# Native Revit build adapts the established API workflow with a unique new asset.
s=(root/'scripts/build_adella_revit.py').read_text()
s=s.replace("'adella'","'scandinavian'").replace('MSI Adella Viso White - 12x24 Satin - Stacked','Scandinavian Decor Grey - Hex 6x7 - Star Layout')
s=s.replace('Adella Viso White 12x24 satin ceramic wall tile; approximate indented relief; 1/16 inch light grout','Scandinavian Decor Grey hexagon 6x7 inch; three-tile star arrangement; printed lines flat')
s=s.replace("'MSI'","'The Stones and More Group'").replace('NADEVISWHI1224-N','Scandinavian Decor Grey').replace('https://www.msisurfaces.com/3d-large-format-wall-tile/adella-viso-white-12x24-satin/','')
s=s.replace('239,240,239','165,165,165').replace("('generic_glossiness',.60)","('generic_glossiness',.40)")
s=s.replace("24.0625)",str(W)+')').replace('12.0625)',str(HH)+')')
s=s.replace('Adella_BaseColor.png','Scandinavian_Color.png').replace('Adella_Bump.png','Scandinavian_Bump.png').replace('Adella_Material_R2025.rvt','Scandinavian_Material_R2025.rvt').replace('bump.Value=.15','bump.Value=.05')
(root/'scripts/build_scandinavian_revit.py').write_text(s)
# Reuse the checked V-Ray graph structure with new textures and material identity.
s=(root/'scripts/build_adella_vrmat.py').read_text().replace("'output/adella'","'output/scandinavian'")
s=s.replace('MSI Adella Viso White 12x24 Satin','Scandinavian Decor Grey Hex 6x7').replace('MSI_Adella_Viso_White','Scandinavian_Decor_Grey').replace('Adella_BaseColor.png','Scandinavian_Color.png').replace('Adella_Normal_OpenGL.png','Scandinavian_Normal.png').replace('Adella_Roughness.png','Scandinavian_Roughness.png').replace('Relief_Preview.jpg','Pattern_Preview.jpg')
(root/'scripts/build_scandinavian_vray.py').write_text(s)
print('Generated photographic pattern',W,HH,photo.size)
