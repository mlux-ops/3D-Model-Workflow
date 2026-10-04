"""Dimensioned Hansgrohe constructions with source-derived and inferred scope separated."""
import math
import prepare_products as p
from prepare_products import cyl,box,sweep,source,anchor,product

def prepare():
    for sku,finish,square,page in [('04388700','white',False,189),('04925000','chrome',True,190)]:
        if square:
            g=[box('Rounded square shower shell',[-3.6875,-3.6875,2.4,3.6875,3.6875,3.18],2.1),
               box('Spray face',[-3.57,-3.57,3.16,3.57,3.57,3.29],2.0,'Gray')]
        else:
            g=[cyl('Round shower shell',[0,0,0],[0,0,1],3.6875,2.4,3.18),
               cyl('Spray face',[0,0,0],[0,0,1],3.57,3.16,3.29,'Gray')]
        g += [cyl('Connection nut',[0,0,0],[0,0,1],.5,0,.6),
              {'name':'Sloped neck','kind':'revolve','origin':[0,0,0],'axis':[0,0,1],
               'profile':[(0,.5),(.5,.5),(.8,1.2),(1.05,2.0),(3.6875,2.4),(0,2.4)],'material':'Finish'}]
        for ring,count in [(1.0,18),(1.75,30),(2.5,42),(3.15,57)]:
            for j in range(count):
                a=j*2*math.pi/count
                g.append(cyl('Spray nozzle %.2f %02d'%(ring,j),[ring*math.cos(a),ring*math.sin(a),0],[0,0,1],.054,3.28,3.375,'Detail'))
        product(sku,'Croma Select '+('E' if square else 'S')+' 180 overhead shower','ceiling',[7.375,7.375,3.375],finish,g,[source(page)],
                ['Width and depth 7.375 in; total head height 3.375 in; 147 spray nozzles.'],
                ['Ball joint shown in the neutral vertical position. Nozzle distribution and shoulder profile follow the drawing approximately.']+
                (['Scheduled matte-white finish retained; the current catalog omits this legacy all-white SKU.'] if not square else []),
                [anchor('Head overall width',['Round shower shell' if not square else 'Rounded square shower shell'],0,7.375)],True)

    radius=1.75;tip=9.25-.375/math.sqrt(2);drop=2.5-.375/math.sqrt(2)
    start=tip-drop-radius*(math.sqrt(2)-1)
    elbow=[0,-radius*(1-math.cos(math.pi/4)),start+radius*math.sin(math.pi/4)]
    mid=[0,-radius*(1-math.cos(math.pi/8)),start+radius*math.sin(math.pi/8)]
    g=[cyl('Wall flange',[0,0,0],[0,0,1],1.25,0,.1875),
       sweep('Bent standard shower arm',[[0,0,.15],[0,0,start],['arc',mid,elbow],[0,-drop,tip]],.375)]
    product('04186703','Standard 9-inch showerarm with flange','wall',[2.5,3.75,9.25],'white',g,[source(204)],
            ['Flange diameter 2.5 in; total projection 9.25 in; connection drop 2.5 in below axis.'],
            ['Pipe radius and bend radius are drawing-derived. Threads omitted. Matte-white scheduled legacy variant retained.'],
            [anchor('Flange diameter',['Wall flange'],0,2.5)],True)

    # iBox: visible construction envelope, with internal valve simplified.
    g=[cyl('Protective green cylindrical shell',[0,0,0],[0,0,1],2.375,0,4.25,'Green',2.12),
       cyl('Rear brass valve body',[0,0,0],[0,0,1],1.55,.1,1.4,'Brass'),
       cyl('Service cartridge',[0,0,0],[0,0,1],.75,1.4,3.25,'Brass')]
    for axis in [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0]]:
        g.append(cyl('Port '+str(axis),[0,0,.875],axis,.59,1.45,2.9375,'Brass',.375))
    for x in [-1.98,1.98]:
        for y in [-1.98,1.98]:g.append(cyl('Mount lug %.2f %.2f'%(x,y),[x,y,0],[0,0,1],.35,0,.45,'Green',.13))
    product('01850181','iBox Universal Plus rough with service stops','wall',[5.875,5.875,4.25],'green',g,[source(374),
            {'url':'https://www.bimobject.com/en-us/hansgrohe/product/01850181','note':'Manufacturer listing confirms rough-in envelope.'}],
            ['Port-to-port envelope 5.875 in in both directions; body depth 4.25 in; shell diameter 4.75 in.'],
            ['Protective shell and brass valve are a coordination visualization. Internal cartridges, support ribs, mounting holes and threads are simplified.'],
            [anchor('Shell diameter',['Protective green cylindrical shell'],0,4.75)],True)

    # Smooth hose in a defined U pose, with exactly 63 in centerline before connectors.
    bend=3.0;leg=(63-math.pi*bend)/2
    g=[sweep('63 inch hose',[[0,0,1],[0,-leg,1],['arc',[3,-leg-3,1],[6,-leg,1]],[6,0,1]],.25),
       cyl('First swivel connector',[0,0,1],[0,1,0],.44,-1.5,.35),
       cyl('Second swivel connector',[6,0,1],[0,1,0],.44,-1.5,.35)]
    s=product('28276703','Techniflex 63-inch handshower hose','wall',[6.88,leg+3.60,.88],'white',g,[source(277)],
              ['Manufacturer nominal flexible hose length 63 in. U-pose centerline consists of two equal legs and a 3 in radius semicircle.'],
              ['Fixed hanging pose is an installation assumption; its bounding box is not a manufacturer product envelope.','Connector dimensions and hose outside diameter are drawing-derived. Matte-white legacy finish retained.'])
    s['native_path_checks']=[{'part':'63 inch hose','nominal_in':63}]

    # Outlet: underside connection is separate from the round wall flange.
    r=(.60*.60+.975*.975)/(2*.60);cx=1.25-r;angle=math.acos((.65-cx)/r)
    middle=(cx+r*math.cos(angle/2),.9+r*math.sin(angle/2))
    g=[cyl('Round flange',[0,0,0],[0,0,1],1.25,0,.7),
       {'name':'Rounded outlet shell','kind':'revolve','origin':[0,0,0],'axis':[0,0,1],
        'profile':[(0,.6),(1.25,.6),(1.25,.9),('arc',middle,(.65,1.875)),(0,1.875)],'material':'Finish'},
       cyl('Downward hose outlet',[0,0,1.20],[0,-1,0],.375,.6,1.62)]
    product('27458003','FixFit round wall outlet with check valve','wall',[2.5,2.87,1.875],'chrome',g,[source(272)],
            ['Body diameter 2.5 in; projection 1.875 in.'],
            ['Underside threaded connection extends below the dimensioned body; its 0.37 in exposed extension is drawing-derived.','Rounded shell and concealed check valve are simplified.'],
            [anchor('Flange diameter',['Round flange'],0,2.5)],False)

    # Talis S diverter tub spout, with vertically oriented end diverter.
    g=[cyl('Wall flange',[0,0,0],[0,0,1],1.375,0,.22),
       cyl('Spout tube',[0,0,0],[0,0,1],.6875,.15,6.45),
       cyl('End diverter cylinder',[0,0,5.6875],[0,1,0],.8125,-.8125,1.18),
       cyl('Diverter lift cap',[0,0,5.6875],[0,1,0],.8125,1.18,1.50),
       cyl('Outlet insert',[0,0,5.6875],[0,-1,0],.55,.8125,1.00,'Detail')]
    product('72411701','Talis S tub spout with diverter','wall',[2.75,2.875,6.5],'white',g,[source(282)],
            ['Overall spout projection 6.5 in; flange diameter 2.75 in; front diverter diameter 1.625 in.'],
            ['Tip reach is nominally 5.625 in; the terminal cylinder is placed at 5.6875 in to match the separately printed projection.','Top lift height is inferred from the drawing; markings and hidden fittings omitted.'],
            [anchor('Flange diameter',['Wall flange'],0,2.75)],False)

    # Vessel faucet body retains square outlines and right-side paddle.
    g=[box('Square base',[-.875,-.875,0,.875,.875,.16],.055),
       box('Tall rectangular body',[-.625,-.625,.12,.625,.625,10.25],.08),
       box('Long flat spout',[-.625,-8.125,9.55,.625,0,10.25],.09),
       box('Spout aerator',[-.45,-7.95,9.55,.45,-7.55,9.62],.08,'Detail'),
       cyl('Side control hub',[0,0,8.875],[1,0,0],.40,.55,1.25),
       box('Control paddle',[1.05,-.35,8.70,1.75,.35,10.05],.08)]
    product('73072341','Tecturis E 240 single-hole vessel faucet','floor',[2.625,9,10.25],'black_chrome',g,[source(62)],
            ['Overall height 10.25 in; base width 1.75 in; nominal outlet height 9.625 in; outlet reach 7.75 in.'],
            ['Body/spout section dimensions and side paddle thickness are drawing-derived.','Above-counter geometry only. Control shown closed; open-handle envelope is not modeled.'],
            [anchor('Overall height',['Tall rectangular body','Square base'],2,10.25),anchor('Base width',['Square base'],0,1.75)])

    # Two widespread sets; side profiles follow their distinct curved silhouettes.
    for sku,finish,name,h,reach,handle_len,handle_h,page in [
        ('72530001','chrome','Rebris S',5.125,5.25,2.5,2.25,69),
        ('75033701','white','Vivenis',4.625,5.875,3.125,2.5,86)]:
        width=1.5 if name=='Vivenis' else 1.20
        if name=='Vivenis':
            dx=reach+.4;radius=(dx*dx+1)/2;angle=math.atan2(dx,radius-1)
            midpoint=(-reach+.2+radius*math.sin(angle/2),h-radius+radius*math.cos(angle/2))
            profile=[(-.60,.14),(.60,.14),(.60,h-1),('arc',midpoint,(-reach+.2,h)),(-reach-.375,h-.38),
                     (-reach-.35,h-.72),('arc',(-2.3,h-.52),(-.60,h-1.0))]
        else:
            profile=[]
        g=[cyl('Spout base',[0,0,0],[0,0,1],1,0,.16),
           {'name':'Sculpted spout','kind':'profile','origin':[-width/2,0,0],'u':[0,1,0],'v':[0,0,1],'normal':[1,0,0],
            'points':profile,'length':width,'material':'Finish'}]
        if name=='Rebris S':
            endpoint=5.46
            for _ in range(12):
                dx=endpoint-1;radius=(dx*dx+.375*.375)/(.75);theta=math.atan2(dx,radius-.375)
                endpoint=5.5-.25*math.sin(theta)
            mid=[0,-1-radius*math.sin(theta/2),4.875-radius+radius*math.cos(theta/2)]
            g=[cyl('Spout base',[0,0,0],[0,0,1],1,0,.16),
               cyl('Rounded upright',[0,0,0],[0,0,1],.60,.16,3.875),
               sweep('Sculpted spout',[[0,0,.16],[0,0,3.875],['arc',[0,-1+math.sqrt(.5),3.875+math.sqrt(.5)],[0,-1,4.875]],
                                      ['arc',mid,[0,-endpoint,4.5]]],.25,oval=[1.2,.5])]
        for side,x in [('Left',-4),('Right',4)]:
            g.append(cyl(side+' valve base',[x,0,0],[0,0,1],.9375,0,.16))
            g.append(cyl(side+' valve body',[x,0,0],[0,0,1],.53,.16,handle_h-.18))
            sign=-1 if x<0 else 1
            bounds=[min(x,x+sign*handle_len),-.24,handle_h-.18,max(x,x+sign*handle_len),.24,handle_h]
            g.append(box(side+' flat lever',bounds,.16))
        outer=8+2*handle_len
        depth=reach+(1.375 if name=='Vivenis' else 1.25)
        product(sku,name+' widespread lavatory faucet, 8-inch centers','floor',[outer,depth,h],finish,g,[source(page)],
                ['8 in valve centers; height %.3f in; reach %.3f in; spout base diameter 2 in.'%(h,reach),
                 'Handle length %.3f in and height %.3f in from the manufacturer diagram.'%(handle_len,handle_h)],
                ['Fixed 8 in installation spacing; levers shown pointing outwards.','Above-counter set only; drain, supply hoses, cast underside and detailed aerator are omitted.','Waterfall/spout shoulders are traced approximately from the catalog side drawing.'],
                [anchor('Height',['Spout base','Sculpted spout'],2,h),anchor('Base diameter',['Spout base'],0,2)])

    g=[box('Spout wall plate',[-1.3125,-1.3125,0,1.3125,1.3125,.375],.10),
       box('Handle wall plate',[6.6875,-1.3125,0,9.3125,1.3125,.375],.10),
       box('Long wall spout',[-.75,-.40,.3,.75,.40,9.5],.08),
       box('Outlet insert',[-.60,-.44,8.65,.60,-.38,9.0],0,'Detail'),
       box('Valve body',[7.45,-.55,.35,8.55,.55,1.75],.1),
       box('Flat wall lever',[7.70,-.25,1.55,11.25,.25,1.78],.12)]
    product('32526141','Metropol single-handle wall-mounted faucet trim','wall',[12.5625,2.625,9.5],'bronze',g,[source(128)],
            ['Two square plates 2.625 in; plate thickness .375 in; total projection 9.5 in; nominal reach 8.875 in.'],
            ['ASSUMPTION: 8 in spout-to-control centers because the catalog does not specify spacing.','Inventory calls this SKU a rough-in; the exact SKU is faucet trim. Required rough 13622181 is not included.','Rectangular section thicknesses and control geometry are drawing-derived.'],
            [anchor('Plate width',['Spout wall plate'],0,2.625),anchor('Projection',['Spout wall plate','Long wall spout'],2,9.5)])

    for sku,finish,mode,page in [('50100341','black_chrome','Push-open',387),('50001141','bronze','Non-closing',386)]:
        g=[cyl('Tailpiece',[0,0,0],[0,0,1],.625,-5,-1.0,inner=.54),
           cyl('Body sleeve',[0,0,0],[0,0,1],.86,-1.15,-.15),
           cyl('Compression nut',[0,0,0],[0,0,1],1.12,-1.2,-.95),
           cyl('Basin flange',[0,0,0],[0,0,1],1.16,-.12,.08),
           cyl('Open drain shadow',[0,0,0],[0,0,1],.95,.07,.19,'Detail'),
           {'name':'Domed cap','kind':'revolve','origin':[0,0,0],'axis':[0,0,1],
            'profile':[(0,.17),(1.25,.17),('arc',(.70,.30),(0,.32))],'material':'Finish'}]
        product(sku,mode+' lavatory drain','floor',[2.5,2.5,5.32],finish,g,[source(page)],
                ['Cap diameter 2.5 in; tailpiece outside diameter 1.25 in.'],
                ['ASSUMPTION: tailpiece cut length and assembled underside stack are modeled for visualization; the source is an exploded diagram.','Open cap gap is fixed. It is not a functioning drain or plumbing clearance model.'],
                [anchor('Cap diameter',['Domed cap'],0,2.5),anchor('Tailpiece diameter',['Tailpiece'],0,1.25)])

    # Left-hand shelf holder, with explicit asymmetry retained.
    outline=[(-9.8125,0),(9.8125,0),(9.8125,1.05),('arc',(5.8,1.90),(3.0,2.05)),
             (-3.0,2.05),('arc',(-7.0,1.85),(-9.8125,1.05))]
    # Coordinates are front elevation; shelf depth and body drop are drawing-derived.
    g=[{'name':'Bowed shelf body','kind':'profile','origin':[0,0,0],'u':[1,0,0],'v':[0,-1,0],'normal':[0,0,1],
        'points':outline,'length':3.50,'material':'Finish'},
       box('Graphite safety-glass shelf',[-9.875,-.02,0,9.875,.18,3.75],.07,'Graphite'),
       cyl('Left hose outlet',[-8.30,-1.0,2.7],[0,-1,0],.32,0,1.2),
       box('Left holder outer cheek',[-9.6,-.55,3.1,-9.1,.25,3.85],.14),
       box('Left holder inner cheek',[-8.50,-.55,3.1,-8.00,.25,3.85],.14)]
    product('26843701','Rainfinity shelf and left-hand shower holder','wall',[19.75,2.45,3.85],'white',g,[source(266)],
            ['Body span 19.625 in; glass span 19.75 in interpreted from the two separately annotated widths; fixing centers 15.75 in.'],
            ['ASSUMPTION: shelf depth 3.75 in and holder projection 3.85 in from proportions; no explicit side dimension was recovered.','Left holder slot is represented by separate cheeks; the body, glass and outlet remain separate materials.','White legacy SKU is retained although omitted from the current main catalog.'],
            [anchor('Body span',['Bowed shelf body'],0,19.625),anchor('Glass span',['Graphite safety-glass shelf'],0,19.75)])

if __name__=='__main__':
    prepare()
    p.publish()
