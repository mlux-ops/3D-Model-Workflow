from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
import json

out=Path(__file__).resolve().parents[1]/'output/adella'
tex=out/'textures';tex.mkdir(parents=True,exist_ok=True)
# Procedural reconstruction of softly indented elongated facets, not measured geometry.
w,h=2048,1024
y,x=np.mgrid[0:h,0:w].astype(float)
x/=w;y/=h
rng=np.random.default_rng(1224)
height=np.ones((h,w))*0.8
for row in range(-1,7):
    for col in range(-1,15):
        cx=(col+.5+(row%2)*.45+rng.uniform(-.13,.13))/13
        cy=(row+.5+rng.uniform(-.17,.17))/5
        rx=rng.uniform(.032,.046);ry=rng.uniform(.074,.11)
        dx=(x-cx)/rx;dy=(y-cy)/ry
        # Faceted bowl with softened transitions and irregular vertical proportions.
        d=np.maximum(np.abs(dx)*.86+np.abs(dy)*.30,np.abs(dy))
        bowl=np.clip(1-d,0,1)
        height-=rng.uniform(.20,.34)*np.sin(bowl*np.pi/2)**.8
height=np.asarray(Image.fromarray(np.uint8(np.clip(height,0,1)*255)).filter(ImageFilter.GaussianBlur(2.5)),dtype=float)/255
# 24 x 12 inch tile with a 1/16 inch joint included in repeat dimensions.
edge=np.minimum.reduce([x*(24.0625), (1-x)*24.0625,y*12.0625,(1-y)*12.0625])
mask=np.clip((edge-.03125)/.045,0,1)
height=.10+(height-.10)*mask
base=np.empty((h,w,3));base[:]=[239,240,239]
base=base*mask[:,:,None]+np.array([218,219,216])*(1-mask[:,:,None])
rough=.40*mask+.78*(1-mask)
Image.fromarray(np.uint8(np.clip(base,0,255))).save(tex/'Adella_BaseColor.png')
Image.fromarray(np.uint16(np.clip(height,0,1)*65535)).save(tex/'Adella_Height16.png')
Image.fromarray(np.uint8(np.clip(height,0,1)*255)).save(tex/'Adella_Bump.png')
Image.fromarray(np.uint8(rough*255)).save(tex/'Adella_Roughness.png')
dy,dx=np.gradient(height*1.5,306.3875/h,611.1875/w)
n=np.dstack([-dx,dy,np.ones_like(dx)]);n/=np.linalg.norm(n,axis=2)[:,:,None]
Image.fromarray(np.uint8((n*.5+.5)*255)).save(tex/'Adella_Normal_OpenGL.png')
light=np.array([-.6,.35,.72]);light/=np.linalg.norm(light)
shade=np.clip((n*light).sum(2),0,1)
preview=np.clip(base*(.45+.65*shade[:,:,None]),0,255).astype('uint8')
Image.fromarray(np.tile(preview,(2,2,1))).resize((1200,600)).save(out/'Relief_Preview.jpg')
(out/'map_spec.json').write_text(json.dumps({'repeat_inches':[24.0625,12.0625],'tile_nominal_inches':[24,12],'joint_inches':.0625,'layout':'horizontal stacked','relief':'approximate procedural indented facets; not a manufacturer scan','height_full_range_mm':1.5,'ior':1.5,'roughness':.4,'resolution':[w,h]},indent=2))
print('Maps created:',[p.name for p in tex.iterdir()])
