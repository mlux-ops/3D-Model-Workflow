import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates
exec(open('iso.py').read().split('def acf_len')[0])
ppi=16; sig=0.5*ppi
def acf_in(img):
    img=gaussian_filter(img,sig)
    img=img-gaussian_filter(img,4*ppi)
    img=img[int(8*ppi):-int(8*ppi)] if img.shape[0]>20*ppi else img
    img=img[:, int(1*ppi):-int(1*ppi)]
    img=img-img.mean()
    f=np.fft.fft2(img,s=(img.shape[0]*2,img.shape[1]*2)); ac=np.fft.ifft2(np.abs(f)**2).real; ac/=ac[0,0]
    lx=np.argmax(ac[0,:]<0.5)/ppi; lz=np.argmax(ac[:,0]<0.5)/ppi
    return lx,lz
sw=np.asarray(Image.open('../../inputs/crosscut_swatch.webp').convert('L')).astype(float)
swr=np.asarray(Image.fromarray(sw).resize((int(2000/41.67*ppi),int(875/41.67*ppi)),Image.LANCZOS),float)
print('swatch lx,lz (in)',acf_in(swr))
cols=[(-49.78,-25.82),(-25.82,-1.76),(-1.76,22.2)]
for F in [80000,100000,120000,140000,160000,180000,200000]:
    zmax=F/(0-yh)-F/(yj-yh)-1
    res=[]
    for x0,x1 in cols:
        r,_=rect(F,ppi,1.5,zmax,x0+1,x1-1)
        res.append(acf_in(r))
    res=np.array(res)
    print(F,round(zmax,1),res.round(2).tolist(),'mean ratio lz/lx',round(float((res[:,1]/res[:,0]).mean()),3))
