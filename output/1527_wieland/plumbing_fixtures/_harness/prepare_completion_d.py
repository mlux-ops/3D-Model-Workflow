"""Articulating fixtures in explicitly documented fixed visualization poses."""
import math
import prepare_products as p
from prepare_products import cyl,box,sweep,anchor,product
from prepare_completion_a import reference

def prepare():
    ref=reference('https://media.brizo.com/SpecSheet/BSP-K-62810LF%20Rev%20N.pdf','Brizo shared pot-filler drawing, exact 62820 handle detail, Rev N')
    g=[cyl('Wall escutcheon',[0,0,0],[0,0,1],1.4375,0,.25),
       cyl('Wall inlet body',[0,0,0],[0,0,1],.65,.20,4.55),
       cyl('First vertical swivel',[0,0,3.5],[0,1,0],.65,0,3.35),
       cyl('First arm',[0,2.8,0],[0,0,1],.40,3.50,11.25),
       cyl('Second vertical swivel',[0,0,11.25],[0,1,0],.65,2.25,6.50),
       cyl('Second arm',[0,5.85,0],[0,0,1],.40,11.25,19.25),
       cyl('End valve body',[0,5.85,0],[0,0,1],.65,18.75,20.375),
       cyl('Downward outlet',[0,0,19.25],[0,1,0],.50,4.65,5.9),
       cyl('Aerator',[0,0,19.25],[0,1,0],.39,4.65,4.70,'Detail'),
       cyl('Wall lever hub',[0,0,0],[0,0,1],.6875,4.35,4.85),
       box('Wall lever paddle',[-.16,-2.75,4.70,.16,.20,4.90],.08),
       box('End lever paddle',[-.16,3.10,20.175,.16,6.0,20.375],.08)]
    product('62820LF-BL','European wall pot filler, extended fixed pose','wall',[2.875,9.25,20.375],'black',g,[ref],
            ['Wall-to-front 20.375 in; outlet axis 19.25 in from wall; swivel axes at 3.5 and 11.25 in; flange diameter 2.875 in.','6.5 in in the source is the top hinge height above the wall inlet axis, not the complete vertical envelope.'],
            ['ASSUMPTION: lower handle extends 2.75 in below the inlet axis, creating a 9.25 in full posed envelope.','Arms are fully extended; swivel, paddle rotation and minor collars are fixed and drawing-derived.','No operational joint flex is claimed; materials are the editable parameters.'],
            [anchor('Full projection',['Wall escutcheon','End valve body'],2,20.375)])

    ref=reference('https://media.brizo.com/SpecSheet/BSP-K-63121LF-LHP%20Rev%20B.pdf','Brizo Odin 63121/63221 less-handle specification Rev B')
    R=2.375;arc_center_z=19.125;head_top=15.4
    hose_bottom=2*arc_center_z+math.pi*R-head_top-23
    g=[cyl('Round base',[0,0,0],[0,0,1],1.21875,0,.1875),
       cyl('Valve column',[0,0,0],[0,0,1],.85,.15,6.75),
       cyl('Side valve sleeve',[0,0,4.5],[1,0,0],.68,.55,2.5),
       cyl('Bare lever spindle',[0,0,4.5],[1,0,0],.18,2.4,2.65,'Brass'),
       sweep('Lower articulating arm',[[0,0,6.75],[0,-1.4,12.625]],.30,oval=[.5,.75]),
       sweep('Upper articulating arm',[[0,-1.4,12.625],[0,-4.75,13.7]],.30,oval=[.5,.75]),
       cyl('Lower hinge',[0,0,6.75],[1,0,0],.60,-.40,.40),
       cyl('Upper hinge',[0,-1.4,12.625],[1,0,0],.50,-.42,.42),
       cyl('Magnetic wand holder',[0,-4.75,13.7],[1,0,0],.50,-.44,.44),
       cyl('Spray wand',[0,-4.75,0],[0,0,1],.57,11.80,15.4),
       cyl('Spray face',[0,-4.75,0],[0,0,1],.48,11.80,11.85,'Detail'),
       sweep('23 inch exposed hose',[[0,0,hose_bottom],[0,0,arc_center_z],['arc',[0,-R,arc_center_z+R],[0,-2*R,arc_center_z]],[0,-2*R,head_top]],.25)]
    s=product('63221LF-BLLHP','Odin articulating kitchen faucet, less handle','floor',[3.86875,6.53875,21.75],'black',g,[ref],
              ['Base diameter 2.4375 in; outlet reach 4.75 in; lower swivel datum 6.75 in; vertical distance to upper swivel 5.875 in; exposed hose 23 in.'],
              ['ASSUMPTION: hose is posed with a 21.75-inch outer crown; the manufacturer states overall height varies with arm position and depicts 21.5 in in another pose.','Above-deck family only; supply tubing and mounting shank omitted. HLK175 handle remains a separate row.','Rigid arm sections, wand length, pivots and sleeve proportions are drawing-derived. Articulation is represented as a fixed display pose.'],
              [anchor('Base diameter',['Round base'],0,2.4375)])
    s['native_path_checks']=[{'part':'23 inch exposed hose','nominal_in':23}]

    ref=reference('https://media.brizo.com/SpecSheet/BSP-B-873111%20Rev%20A.pdf','Brizo Roccesco jointed shower head BSP-B-873111 Rev A')
    q=math.sqrt(.5);radius=2.375;length=7.75
    back_z=14.5-(length+radius)*q
    back_y=5.5
    forward=[0,-q,q]
    g=[cyl('Round wall flange',[0,0,0],[0,0,1],2.375,0,.40),
       cyl('Threaded wall connection',[0,0,0],[0,0,1],.32,-1.5,.65,'Brass'),
       cyl('Wall pivot standoff',[0,0,0],[0,0,1],.70,.35,2.1),
       cyl('Wall-side hinge',[0,0,2.1],[1,0,0],.875,.80,2.25),
       sweep('Flattened jointed arm',[[1.45,0,2.1],[1.45,2.7,8.3]],.4,oval=[.60,1.75]),
       cyl('Head-side hinge',[0,2.7,8.3],[1,0,0],.875,.80,2.25),
       cyl('Cylindrical shower head',[0,back_y,back_z],forward,radius,0,length),
       cyl('Recessed spray disk',[0,back_y,back_z],forward,2.20,length-.04,length,'Detail')]
    center=[0,back_y-length*q,back_z+length*q]
    for r,n in [(.40,8),(1.0,16),(1.7,24)]:
        for i in range(n):
            a=2*math.pi*i/n;x=r*math.cos(a);offset=r*math.sin(a)
            g.append(cyl('Spray nozzle %.1f %d'%(r,i),[x,center[1]+offset*q,center[2]+offset*q],forward,.08,-.08,0,'Gray'))
    product('873111-BNX-2.5','Roccesco jointed sconce shower head, 45-degree pose','wall',[4.75,back_y+radius*q+2.375,16],'onyx',g,[ref],
            ['Shower cylinder diameter 4.75 in and axial length 7.75 in; wall flange diameter 4.75 in; full shown thread-to-head projection 16 in.'],
            ['ASSUMPTION: neutral 45-degree cylinder angle and 1.5-inch concealed stub; final finished-wall projection therefore depends on mounting depth.','Jointed arm plate, nozzle distribution and small pivots are drawing-derived.','Printed standard-specification body text names 873110, while this sheet title and model field explicitly identify 873111; the 873111 drawing is used.'],
            [anchor('Head diameter',['Cylindrical shower head'],0,4.75)])

if __name__=='__main__':
    prepare();p.publish()
