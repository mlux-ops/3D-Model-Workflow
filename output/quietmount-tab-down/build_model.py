from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'quietmount-mixed-screws/build_model.py').read_text()
# Circular bores are now vertical; the old side-print teardrop is unnecessary.
src=src.replace('ts=[12.7', '''def capsule(name,width,z0,z1):
 rad=6.;c=width/2-rad
 o=box(name,(-c,-12,z0),(c,0,z1))
 for x in [-c,c]:boolean(o,cyl('round end',(x,-6,(z0+z1)/2),rad,z1-z0,n=192),'UNION')
 return o

def upper_tab(name,h,z0,z1):
 # Continuous rounded rectangular footprint: tangent sides and circular corners.
 o=capsule(name,14,z0,z1)
 q=capsule('extended rounded crown',14,z0,z1);q.location.y+=h
 bpy.context.view_layer.update();boolean(o,q,'UNION')
 boolean(o,box('tangent sides',(-7,-6,z0),(7,h-6,z1)),'UNION')
 return o

def bore(o,r,z0,z1):
 boolean(o,cyl('vertical round bore',(0,-6,(z0+z1)/2),r,z1-z0,n=160),'DIFFERENCE')

def rounded_tab(name,h,z0,z1):
 # One circular crown, tangent circular fillets joining the straight shoulders.
 R=5.;f=1.;yc=h-R;root=math.sqrt((R+f)**2-(f-yc)**2)
 tx=root*R/(R+f);ty=yc+(f-yc)*R/(R+f)
 end=math.atan2(ty-f,tx-root)
 right=[(root+f*math.cos(-math.pi/2+(end+math.pi/2)*i/24),f+f*math.sin(-math.pi/2+(end+math.pi/2)*i/24)) for i in range(25)]
 a=math.atan2(ty-yc,tx)
 crown=[(R*math.cos(a+(math.pi-2*a)*i/96),yc+R*math.sin(a+(math.pi-2*a)*i/96)) for i in range(1,97)]
 pts=[(-root,-3),(root,-3)]+right+crown+[(-x,y) for x,y in reversed(right[:-1])]
 return prism_z(name,pts,z0,z1)

ts=[12.7''')
src=src.replace("prism_z('lip',[(-a,-2),(a,-2),(a,0),(a-liph,liph),(-a+liph,liph),(-a,0)],F,L)","(upper_tab('rounded upper tab',liph,F,L) if kind=='upper' else rounded_tab('circular tab',liph,F,L))")
src=src.replace('bodyrot=Matrix(((0,0,1),(0,-1,0),(1,0,0)))','bodyrot=Matrix(((1,0,0),(0,-1,0),(0,0,-1)))')
exec(compile(src,__file__,'exec'))
