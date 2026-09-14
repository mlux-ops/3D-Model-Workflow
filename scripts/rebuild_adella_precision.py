from pathlib import Path
import numpy as np
from PIL import Image
import json, shutil, zipfile, hashlib, struct, zlib
root=Path(__file__).resolve().parents[1]
old=root/'output/adella'; out=root/'output/adella_highres_review'
tex=out/'textures'; tex.mkdir(parents=True,exist_ok=True)
src=root/'references/adella/crawl2.jpg'
im=Image.open(src).convert('RGB'); crop=im.crop((12,12,2548,1257))
a=np.asarray(crop,dtype=np.float64)/255
def blur(a,s):
    p=int(s*4)+1
    b=np.pad(a,((p,p),(p,p)),mode='reflect')
    fy=np.fft.fftfreq(b.shape[0])[:,None]; fx=np.fft.rfftfreq(b.shape[1])[None,:]
    b=np.fft.irfft2(np.fft.rfft2(b)*np.exp(-2*np.pi**2*s*s*(fx*fx+fy*fy)),s=b.shape)
    return b[p:-p,p:-p]
def resize(a):
    return np.asarray(Image.fromarray(a.astype('float32')).resize((4096,2048),Image.Resampling.BICUBIC),dtype=float)
lum=a@np.array([.2126,.7152,.0722])
smooth=blur(lum,3)
signal=smooth-blur(smooth,100)
scale=np.percentile(np.abs(signal),99)
height=resize(.5+.20*np.tanh(signal/max(scale,1e-6)))
# Fade relief to a common tile edge, with a narrow neutral grout joint.
y,x=np.mgrid[:2048,:4096]; edge=np.minimum.reduce([x*611.1875/4096,(4095-x)*611.1875/4096,y*306.3875/2048,(2047-y)*306.3875/2048])
t=np.clip((edge-.8)/2,0,1); mask=t*t*(3-2*t)
height=.15+(.5+(height-.5)*mask-.15)*mask
base=np.stack([resize(blur(a[:,:,i],2)) for i in range(3)],axis=2)
# Attenuate photographed directional shading without claiming calibrated albedo.
base=.85*np.median(a,axis=(0,1))+.15*base
base=base*mask[:,:,None]+.86*(1-mask[:,:,None])
Image.fromarray(np.uint8(np.clip(base,0,1)*255+.5)).save(tex/'Adella_BaseColor.png')
q=np.uint16(np.clip(height,0,1)*65535+.5)
Image.fromarray(q).save(tex/'Adella_Bump.png'); Image.fromarray(q).save(tex/'Adella_Height16.png')
dy,dx=np.gradient(height*.6,306.3875/2048,611.1875/4096)
n=np.stack([-dx,dy,np.ones_like(dx)],axis=2); n/=np.linalg.norm(n,axis=2)[:,:,None]
# Lossless RGB16 PNG; avoid re-quantizing the near-flat normals to 8 bits.
def png16(path,a):
    data=np.asarray(np.clip(a,0,1)*65535+.5,dtype='>u2'); h,w,_=data.shape
    def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    raw=b''.join(b'\0'+row.tobytes() for row in data)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,16,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
png16(tex/'Adella_Normal_OpenGL.png',n*.5+.5)
Image.fromarray(np.uint8((.42*mask+.78*(1-mask))*255+.5)).save(tex/'Adella_Roughness.png')
light=np.array([-.8,.2,.5]);light/=np.linalg.norm(light)
preview=np.clip(base*(.35+.75*np.maximum(0,n@light)[:,:,None]),0,1)
Image.fromarray(np.uint8(preview*255)).resize((1600,800)).save(out/'Relief_Preview.jpg')
for name in ['MSI_Adella_Viso_White_R2025.adsklib','MSI_Adella_Viso_White.vrmat','MSI_Adella_Viso_White.vrscene']:
    shutil.copy2(old/name,out/name)
# Existing native library uses these original absolute bitmap paths on this PC.
for p in tex.glob('*.png'):shutil.copy2(p,old/'textures'/p.name)
report={'source_url':'https://www.stonelocator.com/wp-content/uploads/2017/11/NADEVISWHI1224_a-scaled.jpg','source_pixels':list(im.size),'crop':[12,12,2548,1257],'output_pixels':[4096,2048],'source_is_scan':False,'method':'floating point luminance filtering; photo-derived relief estimate, attenuated shading in color','height_full_range_mm':.6,'height_unique_values':int(len(np.unique(q))),'native_render':'not verified; prior V-Ray license unavailable','revit_library':'existing genuine Revit 2025 library reused with new external maps','normal_png_bit_depth':16}
assert len(np.unique(q))>1000
assert (tex/'Adella_Normal_OpenGL.png').read_bytes()[24]==16
with zipfile.ZipFile(out/'MSI_Adella_Viso_White_R2025.adsklib') as z:assert z.testzip() is None
for p in tex.glob('*.png'):
    with Image.open(p) as img:img.verify()
(out/'VALIDATION.json').write_text(json.dumps(report,indent=2))
(out/'README.md').write_text('''# Adella Viso White — high-resolution photo review

Revit 2025 ADSKLIB, V-Ray VRMAT/VRSCENE, and required textures.

Extract all files to a permanent folder. In Revit, open the library in Manage > Materials and add the material to the project. Repath BOTH Appearance color and bump images to this package's textures folder. The library's existing absolute paths also resolve to refreshed maps in output/adella/textures on this computer. Revit may cache images: reload/repath textures and restart the render before comparing. Do not use the older nested extracted package.

V-Ray: import the VRMAT, repath its three bitmap files to this textures folder, and use mapping channel 1 at 24.0625 x 12.0625 inches per repeat. The purple RGB16 image is a tangent-space OpenGL NORMAL map (linear/raw), not grayscale height. Adella_Bump.png and Adella_Height16.png are 16-bit grayscale height, also linear/raw. Displacement is not enabled. Avoid applying both the Revit bump and an additional V-Ray bump to the same surface.

Source: StoneLocator's single-tile photograph, 2560 x 1269 pixels. Output maps are resampled to 4096 x 2048; this does not create native 4K detail. Relief is inferred from a lit photograph, not measured height. Color shading is attenuated, not scientifically calibrated. Relief full-range scaling is an estimated 0.6 mm, with shallower photographed facet variation.

This revision fixes intermediate 8-bit quantization by retaining floating-point values through smoothing, resizing and gradient calculation. Both height and normal textures are exported at 16 bits. Preview is an illustrative shaded map, not a native Revit/V-Ray render. Native appearance remains subject to your review; prior claims that all rendering artifacts were eliminated were unsupported.
''')
archive=out/'MSI_Adella_HighRes_Review.zip'
files=[p for p in out.rglob('*') if p.is_file() and p!=archive]
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(out))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps(report));print(str(archive))
