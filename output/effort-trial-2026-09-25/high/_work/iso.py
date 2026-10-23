import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates
a=np.asarray(Image.open('../../inputs/crosscut_floor_angled.jpg').convert('L')).astype(float)
yh=-935.4; xv=1142.5; H=24/0.4145  # u/H = px per inch across
yj=261.0
def rect(F,ppi,Zmin,Zmax,Xmin,Xmax):
    # Z: inches forward measured from horizontal joint (positive = away from camera, i.e. up in image)
    Z=np.arange(Zmax,Zmin,-1/ppi); X=np.arange(Xmin,Xmax,1/ppi)
    uj=yj-yh
    u=F/(Z+F/uj)          # Z = F/u - F/uj
    y=u+yh
    XX,YY=np.meshgrid(X,y)
    UU=YY-yh
    xx=xv+XX*UU/H
    return map_coordinates(a,[YY,xx],order=1,mode='nearest'),y
def acf_len(img):
    img=img-gaussian_filter(img,6)
    f=np.fft.fft2(img); ac=np.fft.ifft2(np.abs(f)**2).real; ac/=ac[0,0]
    def l(v):
        i=np.argmax(v<0.5); return i
    return l(ac[0,:]),l(ac[:,0]), ac[0,1:8].round(2), ac[1:8,0].round(2)
# X positions of joints: at joint row, X=(x-xv)*H/u
uj=yj-yh
for x in [338.5-0.8606*261,725.5-0.4468*261,1114-0.03017*261,1501+0.3836*261]:
    print('joint X',round((x-xv)*H/uj,2))
for F in [80000,120000,160000,200000]:
    r,y=rect(F,4,0,40,-24,24)
    zmax_in=F/(0-yh)-F/uj
    print(F,'depth visible above joint',round(zmax_in,1),'in; fwd ppi top',round((0-yh)**2/F,1),'joint',round(uj**2/F,1),acf_len(r[: int(min(40,zmax_in-2)*4)]))
