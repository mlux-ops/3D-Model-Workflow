import numpy as np
from PIL import Image
from scipy import ndimage as ndi
a=np.asarray(Image.open('../inputs/crosscut_floor_angled.jpg').convert('L')).astype(float)
H,W=a.shape
hp=a-ndi.gaussian_filter(a,4)
# rough lines: (x at y=0, x at y=349)
rough=[(337,40),(725,570),(1114,1104),(1500,1635),(1887,2159)]
fits=[]
for x0,x1 in rough:
    ys=[];xs=[]
    for y in range(2,H-2):
        xp=x0+(x1-x0)*y/(H-1)
        lo=int(round(xp-8)); hi=int(round(xp+8))
        if lo<1 or hi>W-2: continue
        # sum 3 rows for robustness
        prof=hp[y-1:y+2,lo:hi+1].mean(0)
        i=np.argmin(prof)
        if prof[i]>-4: continue
        # subpixel parabola
        if 0<i<len(prof)-1:
            d=prof[i-1]-2*prof[i]+prof[i+1]
            off=0.5*(prof[i-1]-prof[i+1])/d if d!=0 else 0
        else: off=0
        ys.append(y); xs.append(lo+i+off)
    ys=np.array(ys);xs=np.array(xs)
    for it in range(3):
        p=np.polyfit(ys,xs,1); r=xs-np.polyval(p,ys); s=np.std(r)
        k=np.abs(r)<max(2.5*s,0.6); ys,xs=ys[k],xs[k]
    p=np.polyfit(ys,xs,1); r=xs-np.polyval(p,ys)
    # also test curvature (lens distortion)
    p2=np.polyfit(ys,xs,2)
    fits.append(p)
    print('vjoint x=%.3f + %.5f*y  n=%d rms=%.3f  quad=%.2e  x@0=%.1f x@348=%.1f'%(p[1],p[0],len(ys),np.std(r),p2[0],np.polyval(p,0),np.polyval(p,348)))
# horizontal joint
xs=[];ys=[]
for x in range(2,W-2,2):
    prof=hp[240:285,x-1:x+2].mean(1)
    i=np.argmin(prof)
    if prof[i]>-3: continue
    if 0<i<len(prof)-1:
        d=prof[i-1]-2*prof[i]+prof[i+1]; off=0.5*(prof[i-1]-prof[i+1])/d if d!=0 else 0
    else: off=0
    xs.append(x); ys.append(240+i+off)
xs=np.array(xs);ys=np.array(ys)
for it in range(4):
    p=np.polyfit(xs,ys,1); r=ys-np.polyval(p,xs); s=np.std(r)
    k=np.abs(r)<max(2.5*s,0.6); xs,ys=xs[k],ys[k]
p=np.polyfit(xs,ys,1); r=ys-np.polyval(p,xs)
print('hjoint y=%.3f + %.6f*x n=%d rms=%.3f'%(p[1],p[0],len(xs),np.std(r)))
# vanishing point: least squares intersection of vjoints
A=[];b=[]
for s,c in fits:  # x = c + s*y  ->  x - s*y = c
    A.append([1,-s]); b.append(c)
A=np.array(A);b=np.array(b)
vp,res,_,_=np.linalg.lstsq(A,b,rcond=None)
print('VP x=%.2f y=%.2f'%(vp[0],vp[1]))
for s,c in fits: print('  line resid at VP: %.2f px'%(c+s*vp[1]-vp[0]))
# spacing at rows
for y in [0,100,200,261,348]:
    xx=[c+s*y for s,c in fits]; print(y, np.round(np.diff(xx),2), 'u=',round(y-vp[1],1), 'spacing/u=',np.round(np.diff(xx)/(y-vp[1]),5))
np.save('_work/joint_fits.npy',np.array(fits)); np.save('_work/hjoint.npy',p); np.save('_work/vp.npy',vp)
