import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
exec(open('iso.py').read().split('def acf_len')[0])
ppi=8
def aniso(img, lo=1/10, hi=1/1.5):
    img=img-img.mean()
    wy=np.hanning(img.shape[0])[:,None]; wx=np.hanning(img.shape[1])[None,:]
    P=np.abs(np.fft.fft2(img*wy*wx))**2
    fy=np.fft.fftfreq(img.shape[0],1/ppi)[:,None]; fx=np.fft.fftfreq(img.shape[1],1/ppi)[None,:]
    r=np.sqrt(fx**2+fy**2); m=(r>lo)&(r<hi)
    return float((P*fx**2)[m].sum()/(P*fy**2)[m].sum())
sw=np.asarray(Image.open('../../inputs/crosscut_swatch.webp').convert('L')).astype(float)
for vppi in [41.67,36.46]:
    swr=np.asarray(Image.fromarray(sw).resize((int(2000/41.67*ppi),int(875/vppi*ppi)),Image.LANCZOS),float)
    print('swatch vppi',vppi,'Ex/Ey',round(aniso(swr),3), [round(aniso(swr[:, i*96:(i+1)*96+96]),2) for i in range(3)])
cols=[(-49.78,-25.82),(-25.82,-1.76),(-1.76,22.2)]
for F in [100000,120000,140000,160000,180000,200000]:
    zmax=F/(0-yh)-F/(yj-yh)-2
    v=[aniso(rect(F,ppi,1.5,zmax,x0+1,x1-1)[0]) for x0,x1 in cols]
    print(F,round(zmax,1),np.round(v,3), round(float(np.mean(v)),3))
