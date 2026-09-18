from pathlib import Path
import shutil, json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]
out=root/'output/beige_fluted_12x24'
tex=out/'textures';tex.mkdir(parents=True,exist_ok=True)
src=Path('C:/Users/found/OneDrive/Desktop/IMG_0786.jpeg')
shutil.copy2(src,tex/'Beige_Fluted_Color.jpeg')
im=Image.open(src).convert('RGB'); w,h=im.size
# A low-amplitude photographic relief estimate; never quantize intermediate values.
lum=np.asarray(im,dtype=np.float64)@np.array([.2126,.7152,.0722])/255
profile=np.median(lum[int(h*.1):int(h*.9)],axis=0)
freq=np.fft.rfftfreq(w)
def smooth(s):return np.fft.irfft(np.fft.rfft(profile)*np.exp(-2*np.pi**2*s*s*freq*freq),n=w)
signal=smooth(3)-smooth(70)
height=.5+.3*np.tanh(signal/max(np.percentile(abs(signal),98),1e-8))
bump=np.broadcast_to(height,(h,w))
Image.fromarray(np.uint16(np.clip(bump,0,1)*65535+.5)).save(tex/'Beige_Fluted_Bump16.png')
report={'source_pixels':[w,h],'export_pixels':[w,h],'tile_inches':[12,24], 'color':'Original supplied JPEG, byte-for-byte copy; photographed lighting preserved.', 'relief':'Approximate low-amplitude column profile derived from photograph, not measured surface depth.', 'average_rgb':np.mean(np.asarray(im),axis=(0,1)).round().astype(int).tolist(),'height_unique_values':int(len(np.unique(np.uint16(bump*65535+.5))))}
(out/'texture_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
