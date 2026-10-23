import numpy as np
exec(open('_work/calib.py').read().split("r=8\n")[0])
from scipy.optimize import brentq
def Rfun(alpha,r,sel,band):
    Ztop=alpha*(1/(8-yvp)-1/uj); Zbot=alpha*(1/(348-yvp)-1/uj)
    out,x,y,XX,ZZ=rect(fl,alpha,r,Xj[0]-24,Xj[-1],Zbot,Ztop)
    ok=np.isfinite(out)&(y>8)&(y<346)&(x>2)&(x<1997)
    dj=np.min(np.abs(XX[...,None]-Xj[None,None,:]),axis=2); ok&=dj>1.0; ok&=np.abs(ZZ)>1.0
    ok&=~((x>1780)&(y<240))
    o=np.where(np.isfinite(out),out,np.nanmean(out))
    okb=ndi.binary_erosion(ok,iterations=int(1.2*r))
    m=okb&sel(XX,ZZ)
    s1,s2=band[0]*r,band[1]*r
    d=ndi.gaussian_filter(o,s1)-ndi.gaussian_filter(o,s2); gy,gx=np.gradient(d)
    return (gy[m]**2).mean()/(gx[m]**2).mean()
def swR(r,band):
    sw_r=np.asarray(Image.fromarray(sw).resize((int(round(2000/41.6667*r)),int(round(875/41.6667*r))),Image.LANCZOS)).astype(float)
    m=np.zeros_like(sw_r,bool); b=int(3*band[1]*r); m[b:-b,b:-b]=True
    d=ndi.gaussian_filter(sw_r,band[0]*r)-ndi.gaussian_filter(sw_r,band[1]*r); gy,gx=np.gradient(d)
    return (gy[m]**2).mean()/(gx[m]**2).mean()
res={}
for band in [(0.35,0.9),(0.5,1.5),(0.8,2.4)]:
    r=8
    t=swR(r,band)
    sels={'top':lambda X,Z:Z>0,'bottom':lambda X,Z:Z<0,
          'col1':lambda X,Z:(X>Xj[0])&(X<Xj[1]),'col2':lambda X,Z:(X>Xj[1])&(X<Xj[2]),
          'col3':lambda X,Z:(X>Xj[2])&(X<Xj[3]),'col4':lambda X,Z:(X>Xj[3])&(X<Xj[4])}
    line='band %s swatchR %.3f :'%(band,t)
    for k,sel in sels.items():
        try:
            a=brentq(lambda al: Rfun(al,r,sel,band)-t,6e4,3.5e5,xtol=500)
        except Exception as e: a=np.nan
        res[(band,k)]=a; line+=' %s=%.0f'%(k,a)
    print(line,flush=True)
v=np.array([x for x in res.values() if np.isfinite(x)])
print('all: mean %.0f median %.0f std %.0f min %.0f max %.0f'%(v.mean(),np.median(v),v.std(),v.min(),v.max()))
