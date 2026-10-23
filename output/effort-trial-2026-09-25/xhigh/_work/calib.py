import numpy as np
from PIL import Image
from scipy import ndimage as ndi
fl=np.asarray(Image.open('../inputs/crosscut_floor_angled.jpg').convert('L')).astype(float)
sw=np.asarray(Image.open('../inputs/crosscut_swatch.webp').convert('L')).astype(float)
fits=np.load('_work/joint_fits.npy'); vp=np.load('_work/vp.npy')
xvp,yvp=vp; slopes=fits[:,0]
pitch=24.0625
K=pitch/np.mean(np.diff(slopes)); print('K',K, 'joint X:',(K*slopes).round(3))
yj=260.5; uj=yj-yvp
def rect(img,alpha,r,X0,X1,Z0,Z1):
    X=np.arange(X0,X1,1/r); Z=np.arange(Z0,Z1,1/r)
    ZZ,XX=np.meshgrid(Z[::-1],X,indexing='ij')  # far at top
    u=1/(ZZ/alpha+1/uj); y=yvp+u; x=xvp+XX*u/K
    out=ndi.map_coordinates(img,[y,x],order=3,mode='constant',cval=np.nan)
    return out,x,y,XX,ZZ
def aniso(img,r,mask=None):
    s1,s2=0.35*r,0.9*r   # band ~ 1.5-4 in wavelengths
    f=lambda a,s: ndi.gaussian_filter(a,s)
    d=f(img,s1)-f(img,s2)
    gy,gx=np.gradient(d)
    if mask is None: mask=np.ones_like(d,bool)
    return (gy[mask]**2).mean()/(gx[mask]**2).mean()
r=8
sw_r=np.asarray(Image.fromarray(sw).resize((int(round(2000/41.6667*r)),int(round(875/41.6667*r))),Image.LANCZOS)).astype(float)
m=np.zeros_like(sw_r,bool); b=12; m[b:-b,b:-b]=True
print('swatch R(gy2/gx2)=%.3f'%aniso(sw_r,r,m))
# also swatch halves for spread
h=sw_r.shape[1]//2
print(' swatch left %.3f right %.3f'%(aniso(sw_r[:, :h],r,m[:, :h]),aniso(sw_r[:, h:],r,m[:, h:])))
Xj=K*slopes
for alpha in [5e4,7e4,8e4,9e4,1e5,1.1e5,1.2e5,1.4e5,1.7e5,2.0e5]:
    Ztop=alpha*(1/(8-yvp)-1/uj); Zbot=alpha*(1/(348-yvp)-1/uj)
    out,x,y,XX,ZZ=rect(fl,alpha,r,Xj[0]-24,Xj[-1],Zbot,Ztop)
    ok=np.isfinite(out)&(y>8)&(y<346)&(x>2)&(x<1997)
    # away from joints
    dj=np.min(np.abs(XX[...,None]-Xj[None,None,:]),axis=2)
    ok&=dj>1.0
    ok&=np.abs(ZZ)>1.0
    ok&=~((x>1780)&(y<240))  # shadows
    o=np.where(np.isfinite(out),out,np.nanmean(out))
    okb=ndi.binary_erosion(ok,iterations=int(1.2*r))
    Rt=aniso(o,r,okb&(ZZ>0)); Rb=aniso(o,r,okb&(ZZ<0))
    print('alpha %.0f Ztop %.1f Zbot %.1f  R_top %.3f R_bot %.3f  n=%d'%(alpha,Ztop,Zbot,Rt,Rb,okb.sum()))
