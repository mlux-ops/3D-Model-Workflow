from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageFilter, ImageOps

root=Path(__file__).resolve().parents[1]
out=root/'output/adella'; tex=out/'textures'; tex.mkdir(parents=True,exist_ok=True)
w,h=4096,2048
source=Image.open(root/'references/adella/crawl1.jpg').convert('RGB')
# StoneLocator's exact-product image contains a large 24x12 panel in its
# upper-left quadrant. Crop that panel between the visible grout lines.
native=source.crop((5,5,1700,830))
# Suppress JPEG/pixel noise at the photographed resolution before enlargement.
native_smooth=native.filter(ImageFilter.GaussianBlur(0.8))
crop=native_smooth.resize((w,h),Image.Resampling.LANCZOS)
base=np.asarray(crop,dtype=float)
lum=np.asarray(ImageOps.grayscale(crop),dtype=float)/255.0
illum=np.asarray(ImageOps.grayscale(crop).filter(ImageFilter.GaussianBlur(90)),dtype=float)/255.0
detail=np.clip(lum-(illum-0.5),0,1)
height=np.clip((detail-0.38)/0.34,0.05,0.95)
rough=np.full((h,w),.42)
Image.fromarray(np.uint8(np.clip(base,0,255))).save(tex/'Adella_BaseColor.png')
Image.fromarray(np.uint16(height*65535)).save(tex/'Adella_Height16.png')
Image.fromarray(np.uint8(height*255)).save(tex/'Adella_Bump.png')
Image.fromarray(np.uint8(rough*255)).save(tex/'Adella_Roughness.png')
dy,dx=np.gradient(height*1.5,306.3875/h,611.1875/w)
n=np.dstack([-dx,dy,np.ones_like(dx)]); n/=np.linalg.norm(n,axis=2)[:,:,None]
Image.fromarray(np.uint8(np.clip(n*.5+.5,0,1)*255)).save(tex/'Adella_Normal_OpenGL.png')
light=np.array([-.6,.35,.72]); light/=np.linalg.norm(light)
shade=np.clip((n*light).sum(2),0,1)
preview=np.clip(base*(.45+.65*shade[:,:,None]),0,255).astype('uint8')
Image.fromarray(np.tile(preview,(2,2,1))).resize((1200,600)).save(out/'Relief_Preview.jpg')
(out/'map_spec.json').write_text(json.dumps({'repeat_inches':[24.0625,12.0625],'tile_nominal_inches':[24,12],'joint_inches':.0625,'layout':'horizontal stacked','relief':'derived from photographed exact-product tile crop','source_image':'references/adella/crawl1.jpg','source_resolution':[2560,2560],'crop_pixels':[5,5,1700,830],'height_method':'studio illumination removed from luminance; normalized photographic relief','height_full_range_mm':1.5,'ior':1.5,'roughness':.42,'resolution':[w,h]},indent=2))
print('Photographic maps created')
