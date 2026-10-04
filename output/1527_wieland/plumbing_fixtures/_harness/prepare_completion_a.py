"""Source-specific finishing inputs for shower assemblies, tub and kitchen fittings."""
import math
import prepare_products as p
from prepare_products import cyl,box,sweep,source,anchor,product

def reference(url,title,image=None,page=1):
    d={'url':url,'document':title,'page':page}
    if image:d['local_image']=image
    else:d['visual_review_method']='Manufacturer web PDF screenshot'
    return d

def prepare():
    air=reference('https://media.brizo.com/SpecSheet/BSP-A-69080%20Rev%20D.pdf','Brizo BSP-A-69080 Rev D')
    g=[cyl('Escutcheon',[0,0,0],[0,0,1],.875,0,.125),cyl('Inset seam',[0,0,0],[0,0,1],.68,.12,.16,'Detail'),
       cyl('Push button',[0,0,0],[0,0,1],.65,.15,.3125)]
    product('69080-BL','Disposal air-switch above-counter button','floor',[1.75,1.75,.3125],'black',g,[air],
            ['Trim diameter 1.75 in and visible height 0.3125 in from manufacturer diagram.'],
            ['Above-counter visualization; remote dual-outlet power module, air tube and threaded shank are not modeled.','Button seam and moving button diameter are drawing-derived.'],
            [anchor('Visible height',['Escutcheon','Push button'],2,.3125)],True)

    bev=reference('https://media.brizo.com/SpecSheet/BSP-K-61320LF-C%20Rev%20B.pdf','Brizo BSP-K-61320LF-C Rev B')
    reach=5.0625;r=reach/2;z=9.5-.375-r
    g=[cyl('Base',[0,0,0],[0,0,1],1,0,.20),cyl('Valve body',[0,0,0],[0,0,1],.75,.16,4.65),
       sweep('Continuous gooseneck',[[0,0,4.5],[0,0,z],['arc',[0,-r,z+r],[0,-reach,z]],[0,-reach,6.0625]],.375),
       cyl('Side control hub',[0,0,2.6],[1,0,0],.45,.60,1.9),
       cyl('Vertical lever',[2.25,0,0],[0,0,1],.25,2.4,4.6),
       cyl('Aerator insert',[0,-reach,0],[0,0,1],.30,6.0625,6.10,'Detail')]
    product('61320LF-C-BL','Solna cold-only beverage faucet','floor',[3.5,reach+1.375,9.5],'black',g,[bev],
            ['Overall height 9.5 in, base diameter 2 in, outlet height 6.0625 in and reach 5.0625 in.'],
            ['Above-counter scope only. Side lever envelope, body diameter and spout tube section are drawing-derived.'],
            [anchor('Height',['Base','Continuous gooseneck'],2,9.5),anchor('Base diameter',['Base'],0,2)])

    hl=reference('https://bravo.requested-info.com/brands/BRZ/documents/specSheets/T755110-BLLHP_Spec.pdf','Brizo BSP-B-T755110-LHP Rev A',
                 '_research/T755110-BNXLHP/downloads/T755110-BLLHP_Spec_pages/page_01.png')
    g=[]
    for label,y,radius,h in [('Lower',-1.4375,1.25,4.125),('Upper',1.4375,.6875,2.4375)]:
        g += [cyl(label+' handle sleeve',[0,y,0],[0,0,1],radius,0,h-.75),
              box(label+' lever neck',[-.45,y-.45,h-.80,.45,y+.45,h-.15],.12),
              box(label+' lever paddle',[-2.25,y-.35,h-.32,1.25,y+.35,h],.15)]
    g.append(box('Lower secondary temperature lever',[-2.15,-1.73,2.87,1.15,-1.15,3.12],.10))
    product('HL75110-BNX','Roccesco integrated diverter lever handle kit','wall',[3.5,4.8125,4.125],'onyx',g,[hl],
            ['Lower handle projection 4.125 in; upper handle projection 2.4375 in; lever length 3.5 in; upper sleeve diameter 1.375 in.'],
            ['ASSUMPTION: control center spacing 2.875 in follows the companion trim drawing.','Kit origins are representative and require alignment with the installed trim; concealed mating surfaces are not fabrication geometry.','Secondary temperature lever depth and sleeve diameters are drawing-derived.'],
            [anchor('Lower handle projection',['Lower handle sleeve','Lower lever neck','Lower lever paddle'],2,4.125)])

    lev=reference('https://media.brizo.com/SpecSheet/BSP-B-88798%20Rev%20D.pdf','Brizo BSP-B-88798 Rev D',
                  '_research/88798-BNX/downloads/BSP-B-88798_Rev_D_pages/page_01.png')
    half=26.6875/2
    bar=[(0,half-2),(0,half-.5),(2.9,half),(3.75,half-.5),(3.75,-half+.5),(2.9,-half),(0,-half+.5),(0,-half+2),
         (.30,-half+2),(.30,-half+.75),(2.8,-half+.35),(3.40,-half+.75),(3.40,half-.75),(2.8,half-.35),(.30,half-.75),(.30,half-2)]
    g=[{'kind':'profile','name':'Curved rectangular slide bar','origin':[-.875,0,0],'u':[0,0,1],'v':[0,1,0],'normal':[1,0,0],'points':bar,'length':1.75},
       cyl('Slider clamp',[0,-1.5,3.65],[1,0,0],.65,-2.125,3),
       cyl('Handshower round head',[3,7.4,3.8],[0,0,1],1.96875,0,.65),
       cyl('Spray face',[3,7.4,3.8],[0,0,1],1.83,.65,.72,'Gray'),
       cyl('Handshower handle',[3,0,4.05],[0,1,0],.52,-2.00625,5.95),
       cyl('Bottom hose outlet',[0,-half+1,2.0],[0,-1,0],.375,0,1.2)]
    for i in range(24):
        a=2*math.pi*i/24
        g.append(cyl('Head nozzle '+str(i),[3+1.35*math.cos(a),7.4+1.35*math.sin(a),4.5],[0,0,1],.08,0,.07,'Detail'))
    # A 60-inch hose in a fixed U pose; endpoint heights are installation assumptions.
    left=-half-.2;right=-2.00625;radius=1.5
    low=(left+right+math.pi*radius-60)/2
    g.append(sweep('60 inch hose',[[0,left,3.4],[0,low,3.4],['arc',[1.5,low-radius,3.4],[3,low,3.4]],[3,right,3.4]],.20))
    s=product('88798-BNX','Levoir wallbar handshower and hose','wall',[7.09375,half-low+radius+.20,4.57],'onyx',g,[lev],
              ['Bar height 26.6875 in; bar width 1.75 in; projection 3.75 in; head diameter 3.9375 in; handshower length 11.375 in.'],
              ['ASSUMPTION: handshower upright pose and 60 in hanging hose shape are fixed. The complete posed envelope is not a factory rigid-body dimension.','Bar end bends, slider fittings and nozzle layout are simplified; hose is smooth rather than corrugated.'],
              [anchor('Bar height',['Curved rectangular slide bar'],1,26.6875),anchor('Head diameter',['Handshower round head'],0,3.9375)])
    s['native_path_checks']=[{'part':'60 inch hose','nominal_in':60}]

    # Terrassa: curved oval shell, with actual open rim, drain and overflow openings.
    tub=reference('https://assets.fbgpg.com/shared/docs/product-specifications/spc-ter-n-sw_ofsp.pdf','Victoria + Albert Terrassa Rev 09/23',
                  '_research/TER-N-SW-OF/downloads/spc-ter-n-sw_ofsp_pages/page_01.png')
    outer=[{'center':[0,0,0],'size':[43.75,19.5],'radius':8},
           {'center':[0,0,3],'size':[50,22.2],'radius':10},
           {'center':[0,0,12],'size':[61.8,28.4],'radius':13.4},
           {'center':[0,0,20.75],'size':[67,31.25],'radius':15.4}]
    inner=[{'center':[0,0,.50],'size':[43.0,18.7],'radius':8.2},
           {'center':[0,0,3.2],'size':[48.5,21.3],'radius':9.8},
           {'center':[0,0,12],'size':[59.9,26.9],'radius':12.9},
           {'center':[0,0,21.0],'size':[65.3,29.65],'radius':14.5}]
    shell={'kind':'shell','sections':outer,'inner':inner}
    g=[{'kind':'cut','name':'Open sculpted tub shell','base':shell,'cutters':[
        cyl('Drain cutter',[0,0,0],[0,0,1],1,-1,1),cyl('Overflow cutter',[0,0,18.375],[0,1,0],.4,12,17)]}]
    product('TER-N-SW-OF','Terrassa freestanding tub with overflow','floor',[67,31.25,20.75],'ceramic',g,[tub],
            ['Overall 67 x 31.25 x 20.75 in; base 43.75 x 19.5 in; drain diameter 2 in.'],
            ['Undimensioned shell sections and curvature reconstructed from the orthographic drawing.','No K-51 waste assembly is included; the actual drain and overflow openings remain open.','Original manufacturer download was a 3DS mesh, not RFA, and is preserved as source evidence.'],
            [anchor('Overall length',['Open sculpted tub shell'],0,67)],True)

    kd=reference('https://assets.fbgpg.com/shared/docs/product-specifications/spc-k-70sp.pdf','Victoria + Albert K-70 Rev 05/24',
                 '_research/K-70-PVC/downloads/spc-k-70sp_pages/page_01.png')
    flange={'kind':'loft','sections':[{'center':[0,0,-.08],'size':[7,6.25],'shape':'ellipse'},
                                    {'center':[0,0,0],'size':[7,6.25],'shape':'ellipse'}]}
    cutters=[cyl('Central opening',[0,0,0],[0,0,1],2.5,-.2,.2)]
    for i in range(18):
        a=2*math.pi*i/18
        cutters.append(cyl('Flange perforation',[3.0*math.cos(a),2.7*math.sin(a),0],[0,0,1],.125 if i%2 else .20,-.2,.2))
    g=[{'kind':'cut','name':'Perforated elliptical flange','base':flange,'cutters':cutters,'material':'Detail'},
       {'kind':'revolve','name':'Recessed drain cup','origin':[0,0,0],'axis':[0,0,1],
        'profile':[(2.5,0),(2.375,-1.5),(1.25,-1.7),(1.25,-1.5),(2.22,-1.30),(2.35,0)],'material':'Detail'},
       cyl('PVC outlet sleeve',[0,0,0],[0,0,1],1.1875,-3.375,-1.50,'Finish',.82),
       cyl('Compression collar',[0,0,0],[0,0,1],1.60,-2.70,-1.70,'Finish',1.0),
       cyl('Central brass connection',[0,0,0],[0,0,1],.90,-1.70,-.15,'Brass',.8125)]
    product('K-70-PVC','Freestanding tub island drain box, PVC','floor',[7,6.25,3.375],'white',g,[kd],
            ['Elliptical flange 7 x 6.25 in; total body height 3.375 in; outlet OD 2.375 in.'],
            ['Thread ribs, locking tabs and red shipping insert omitted. Perforation distribution is drawing-derived.','The sub-floor drain is modeled below the face placement plane; no extension pipe is assumed.'],
            [anchor('Flange width',['Perforated elliptical flange'],0,7)],True)

if __name__=='__main__':
    prepare();p.publish()
