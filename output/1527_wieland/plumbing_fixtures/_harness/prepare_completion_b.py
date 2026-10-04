"""Exact-source fixture components with measured and inferred geometry distinguished."""
import math
import prepare_products as p
from prepare_products import cyl,box,sweep,source,anchor,product
from prepare_completion_a import reference

def prepare():
    doc=reference('https://media.brizo.com/SpecSheet/BSP-B-T600110-LHP%20Rev%20A.pdf','Brizo BSP-B-T600110-LHP Rev A')
    g=[cyl('Handle sleeve',[0,0,0],[0,0,1],1.25,0,3.375),
       box('Control lever neck',[-.45,-.45,3.325,.45,.45,3.975],.12),
       box('Volume lever paddle',[-2.25,-.35,3.805,1.25,.35,4.125],.15),
       box('Temperature lever',[-2.15,-.29,2.87,1.15,.29,3.12],.10)]
    product('HL60110-BNX','Roccesco TempAssure lever handle kit','wall',[3.5,2.5,4.125],'onyx',g,[doc],
            ['Lever width 3.5 in and total handle projection 4.125 in: exact manufacturer handle detail.'],
            ['Sleeve diameter, control ring separation and relative temperature-lever depth are drawing-derived.','This is the handle kit only; separate trim and rough families are not incorporated.'],
            [anchor('Handle projection',['Handle sleeve','Control lever neck','Volume lever paddle'],2,4.125)])

    doc=reference('https://media.brizo.com/SpecSheet/BSP-B-RP71648%20Rev%20D.pdf','Brizo BSP-B-RP71648 Rev D')
    r=1.375;s=r/math.sqrt(2)
    g=[cyl('Wall flange',[0,0,0],[0,0,1],1.25,0,.20),
       sweep('Smooth bent shower arm',[[0,0,.15],[0,0,14.25],['arc',[0,-r+s,14.25+s],[0,-r,15.625]],[0,-2.50,15.625]],.375),
       cyl('Outlet bore',[0,-2.50,15.625],[0,1,0],.26,0,.06,'Detail')]
    product('RP71648BNX','16-inch round wall shower arm and flange','wall',[2.5,3.75,16],'onyx',g,[doc],
            ['Projection 16 in, flange diameter 2.5 in, and centerline-to-outlet drop 2.5 in: manufacturer drawing.'],
            ['Pipe diameter 0.75 in, bend radius 1.375 in and flange thickness 0.20 in are drawing-derived.','Thread grooves are omitted; open outlet is represented by a recessed dark face.'],
            [anchor('Arm projection',['Wall flange','Smooth bent shower arm'],2,16)],True)

    doc=reference('https://media.brizo.com/SpecSheet/BSP-L-R70400%20Rev%20C.pdf','Brizo BSP-L-R70400 Rev C')
    plate=box('Back mounting strap',[-5.375,-.40,0,5.375,.40,.125],.16,'Gray')
    g=[{'kind':'cut','name':'Slotted mounting strap','base':plate,'cutters':[
            cyl('Left fixing slot',[-5.125,0,0],[0,0,1],.125,-.1,.3),
            cyl('Right fixing slot',[5.125,0,0],[0,0,1],.125,-.1,.3)],'material':'Gray'},
       cyl('Brass cross manifold',[0,0,.85],[1,0,0],.4375,-4,4,'Brass')]
    for x,label in [(-4,'Hot'),(4,'Cold')]:
        g += [cyl(label+' valve body',[x,0,0],[0,0,1],.8125,.15,2.0,'Brass'),
              cyl(label+' down inlet',[x,0,.65],[0,-1,0],.625,.3,1.625,'Brass',.40),
              cyl(label+' guard',[x,0,0],[0,0,1],.75,1.6,2.60,'Detail'),
              cyl(label+' valve stem',[x,0,0],[0,0,1],.22,2.3,3.5,'Brass')]
    g += [cyl('Center spout outlet',[0,0,0],[0,0,1],.60,.20,2.5,'Brass',.40),
          cyl('Center test extension',[0,0,0],[0,0,1],.30,2.3,3.0,'Detail')]
    product('R70400','Two-handle wall tub filler rough','wall',[10.75,2.4375,3.5],'brass',g,[doc],
            ['Valve axes are 8 in apart; mounting-hole centers are 10.25 in apart; nominal mounting-to-wall distance is 2.75 in.'],
            ['ASSUMPTION: mounting strap projects 0.25 in beyond each dimensioned fixing center.','Overall height and test-stem projection are inferred from the drawing. Internal valves and thread details are omitted.'],
            [anchor('Mounting strap overall',['Slotted mounting strap'],0,10.75)])

    bar=reference('https://assets.specbooks.cloud/brand/brizo/spec/7646847/document/spec-sb-sccscf.pdf','Brizo BSP-K-61075LF-LHP Rev C',
                  '_research/61075LF-BLLHP/downloads/spec-sb-sccscf_pages/page_01.png')
    z=8.1875;endx=3+math.sqrt(9-(8.375-z)**2)
    g=[cyl('Round base',[0,0,0],[0,0,1],1.1875,0,.1875),
       cyl('Valve body',[0,0,0],[0,0,1],.78,.15,4.7),
       cyl('Side cartridge hub',[0,0,3.5],[1,0,0],.79,.5,2.35),
       cyl('Exposed handle spindle',[0,0,3.5],[1,0,0],.20,2.25,2.50,'Brass'),
       sweep('Continuous arc spout',[[0,0,4.65],[0,0,z],['arc',[0,-3,z+3],[0,-endx,8.375]]],.4375),
       cyl('Dark aerator',[0,-endx,8.375],[0,0,1],.34,0,.04,'Detail')]
    product('61075LF-BLLHP','Odin bar faucet, less handle','floor',[3.6875,7.625,11.625],'black',g,[bar],
            ['Overall height 11.625 in, nominal spout reach 6 in, outlet center height 8.375 in, base diameter 2.375 in.'],
            ['Below-deck shank and supply tubing are omitted.','Body and tube diameters are drawing-derived; spout endpoint follows the printed outlet height with a continuous tangent arc.','The separate HLB175 handle is intentionally absent from this less-handle SKU.'],
            [anchor('Faucet height',['Round base','Continuous arc spout'],2,11.625),anchor('Base diameter',['Round base'],0,2.375)])

    for sku,kind in [('HLB175-BL','bar'),('HLK175-BL','kitchen')]:
        handle_doc=bar if kind=='bar' else reference('https://media.brizo.com/SpecSheet/BSP-K-63121LF-LHP%20Rev%20B.pdf','Brizo BSP-K-63121LF-LHP Rev B')
        g=[cyl('Handle socket',[0,0,0],[0,0,1],.4375,0,1.10),
           cyl('Lever shank',[0,0,.75],[0,1,0],.1875,.20,3.25),
           box('Flattened lever tip',[-.17,3.0,.58,.17,3.25,.92],.06)]
        product(sku,'Odin '+kind+' lever handle','wall',[.875,3.6875,1.10],'black',g,[handle_doc],
                ['Socket nominal diameter 0.875 in and axis-to-lever-tip distance 3.25 in: manufacturer handle detail.'],
                ['Socket depth and lever section are drawing-derived. Handle supplied in an upright neutral pose.','HLB175 and HLK175 have separate product identities and must be aligned to their respective valve stems.'],
                [anchor('Socket diameter',['Handle socket'],0,.875)])

    axor=reference('https://assets.hansgrohe.com/mam/celum/celum_assets/153__amu01065_eps.jpg?format=HBW7','AXOR ONE 48140991 dimension drawing',
                   '_research/48140991/downloads/AXOR_ONE_48140991_dimensions.jpg')
    angle=math.radians(70);rad=1.5/(1-math.cos(angle));start=8.625-rad*math.sin(angle)
    g=[]
    for x,label in [(-4,'Left'),(0,'Spout'),(4,'Right')]:
        g.append(cyl(label+' escutcheon',[x,0,0],[0,0,1],1.1875,0,.1875))
    for x,label in [(-4,'Left'),(4,'Right')]:
        cross=[[-.12,1.375],[.12,1.375],[.16,.62],['arc',[.28,.28],[.62,.16]],
               [1.375,.12],[1.375,-.12],[.62,-.16],['arc',[.28,-.28],[.16,-.62]],
               [.12,-1.375],[-.12,-1.375],[-.16,-.62],['arc',[-.28,-.28],[-.62,-.16]],
               [-1.375,-.12],[-1.375,.12],[-.62,.16],['arc',[-.28,.28],[-.16,.62]]]
        g += [cyl(label+' handle neck',[x,0,0],[0,0,1],.47,.15,1.15),
              cyl(label+' handle hub',[x,0,0],[0,0,1],.36,.85,1.42),
              {'kind':'profile','name':label+' sculpted cross handle','origin':[x,0,1.10],
               'u':[1,0,0],'v':[0,1,0],'normal':[0,0,1],'points':cross,'length':.30}]
    g.append(sweep('Continuous angled outlet',[[0,0,.2],[0,0,start],['arc',[0,-rad*(1-math.cos(angle/2)),start+rad*math.sin(angle/2)],[0,-1.5,8.625]]],.4375))
    g.append(cyl('Outlet insert',[0,-1.5,8.625],[0,math.cos(math.radians(20)),-math.sin(math.radians(20))],.34,0,.04,'Detail'))
    s=product('48140991','AXOR ONE wall widespread cross-handle faucet','wall',[10.75,1.375+1.5+.4375*math.sin(math.radians(20)),8.625+.4375*math.cos(math.radians(20))],'gold',g,[axor],
              ['8 in centers; escutcheons diameter 2.375 in; cross handle axis-to-tip 1.375 in; tube diameter 0.875 in; outlet center reach 8.625 in; nominal projection 9 in.'],
              ['Finish 991 verified as Polished Gold Optic on the exact manufacturer product page.','Cross junction fillets, handle neck and coating response are inferred.','Outlet bend is a circular reconstruction from the 1.5 in drop and 20 degree outlet axis; its calculated outer projection is 9.036 in, within 1 mm of nominal 9 in.'],
              [anchor('Escutcheon diameter',['Spout escutcheon'],0,2.375)])
    s['materials']['Finish']=dict(s['materials']['Finish'],gloss=.96,reflectivity=.80)

    # Fixed display pose preserves the catalog's 28.25-inch bar and 63-inch hose.
    half=28.25/2
    g=[cyl('Vertical slide bar',[0,0,2],[0,1,0],.4375,-half,half),
       cyl('Top wall bracket',[0,half-.9375,0],[0,0,1],.56,0,2.2),
       cyl('Bottom wall bracket',[0,-half+.9375,0],[0,0,1],.56,0,2.2),
       cyl('Slider',[0,0,2],[1,0,0],.65,-.6,2.8),
       cyl('Handset handle',[2.8,0,3.5],[0,1,0],.40,-2.0,5.3),
       box('Rounded square head',[2.8-2.165,4.8,3.25,2.8+2.165,9.13,4.0],.85),
       box('Spray insert',[2.8-1.95,5.02,3.98,2.8+1.95,8.92,4.08],.75,'Ceramic')]
    for i in range(6):
        for j in range(6):g.append(cyl('Spray nozzle %s %s'%(i,j),[1.2+i*.64,5.4+j*.64,4.07],[0,0,1],.06,0,.08,'Detail'))
    radius=1.4;low=(-half-2+math.pi*radius-63)/2
    g.append(sweep('63 inch hose',[[0,-half,2.4],[0,low,2.4],['arc',[radius,low-radius,2.4],[2*radius,low,2.4]],[2*radius,-2,2.4]],.2))
    s=product('04790000','Croma Select E wallbar handshower package','wall',[.6+2.8+2.165,half-low+radius+.2,4.15],'chrome',g,[source(252)],
              ['Bar 28.25 in and diameter 0.875 in; hose 63 in; handset 110 mm nominal spray-face size.'],
              ['ASSUMPTION: upright handset and fixed U hose display pose. The full posed envelope is not a manufacturer rigid overall dimension.','Handset angle, slider, connection and rounded-square edge details are simplified.','The current catalog calls this 1.75 GPM, while the schedule describes 1.8 GPM.'],
              [anchor('Slide bar length',['Vertical slide bar'],1,28.25)])
    s['native_path_checks']=[{'part':'63 inch hose','nominal_in':63}]

    aquia=reference('https://www.totousa.com/filemanager_uploads/product_assets/SpecSheet/SS-02062_MS446124CEMF(G)N.pdf','TOTO Aquia IV SS-02062',
                    '_research/CT446CEFGNT40_01/downloads/SS-02062_MS446124CEMF_G_N_pages/page_02.png',2)
    bom=reference('https://www.totousa.com/filemanager_uploads/product_assets/PartsManual/PD-01451_446EN.pdf','TOTO Aquia IV PD-01451 parts',
                  '_research/CT446CEFGNT40_01/downloads/PD-01451_446EN_pages/page_01.png')
    outer=[{'center':[0,0,0],'size':[13.2,5.8],'radius':.8},
           {'center':[0,0,4],'size':[13.9,5.95],'radius':.86},
           {'center':[0,0,13.65],'size':[15.4,6.30],'radius':1.0}]
    inner=[{'center':[0,0,.4],'size':[12.5,5.1],'radius':.7},
           {'center':[0,0,13.8],'size':[14.55,5.55],'radius':.8}]
    g=[{'kind':'shell','name':'Tank ceramic shell','sections':outer,'inner':inner},
       box('Tank lid seam',[-7.69,-3.15,13.63,7.69,3.15,13.72],.9,'Gray'),
       {'kind':'cut','name':'Removable tank lid','base':box('Lid',[-7.75,-3.1875,13.72,7.75,3.1875,14.125],1.0),
        'cutters':[cyl('Button opening',[0,0,0],[0,0,1],.80,13.60,14.30)]}]
    product('ST446EMNA#01','Aquia IV dual-flush toilet tank','floor',[15.5,6.375,14.125],'ceramic',g,[aquia,bom],
            ['Tank width 15.5 in and depth 6.375 in from the complete-set drawing.','Tank height 14.125 in is derived from 30.25 in total minus 16.125 in rim-height datum.'],
            ['ASSUMPTION: tank mounting base aligns with the complete-set rim-height datum. Independent tank-height dimension is not published in this reference.','The ceramic body and lid are represented; internal flushing hardware, screws and gaskets are omitted.','THU842 button remains a separately scheduled component; lid opening diameter is drawing-derived.'],
            [anchor('Tank width',['Removable tank lid'],0,15.5)])

    outer=[{'center':[0,1.0,0],'size':[11.625,20.0],'radius':4.7},
           {'center':[0,1.0,6],'size':[12.0,20.5],'radius':5},
           {'center':[0,0,14.9],'size':[14.5,27.5625],'radius':6.5},
           {'center':[0,0,16.125],'size':[14.5,27.5625],'radius':6.5}]
    inner=[{'center':[0,-2.8,7.8],'size':[4.5,6.0],'radius':2.0},
           {'center':[0,-3.4,14.2],'size':[9.75,15.0],'radius':4.7},
           {'center':[0,-3.4,16.5],'size':[10.6,16.5],'radius':5.1}]
    shell={'kind':'shell','sections':outer,'inner':inner}
    g=[{'kind':'cut','name':'Open bowl with rear tank deck','base':shell,
        'cutters':[cyl('Bowl outlet',[0,-2.8,0],[0,0,1],1.0625,-.2,8.1)]}]
    product('CT446CEFGNT40#01','Aquia IV WASHLET+ elongated bowl','floor',[14.5,27.5625,16.125],'ceramic',g,[aquia,bom],
            ['Floor-to-rim 16.125 in and full set depth 27.5625 in from manufacturer drawing; exact component number confirmed in parts manual.'],
            ['Bowl-only width 14.5 in, underside footprint, bowl interior and shell curvature are drawing-derived; no separate bowl fabrication sheet was found.','The tank, seat and push-button are separate scheduled components. This family has an open bowl and rear mounting deck.','Internal trapway, WASHLET connection pocket and fixture-specific anchor recesses are omitted.'],
            [anchor('Rim height',['Open bowl with rear tank deck'],2,16.125)])

if __name__=='__main__':
    prepare();p.publish()
