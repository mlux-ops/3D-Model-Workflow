"""Additional Brizo geometry from exact manufacturer technical drawings."""
import math
import prepare_products as p
from prepare_products import cyl,box,sweep,anchor,product

def doc(key,filename,title,page=1,official=None):
    url=official or 'https://bravo.requested-info.com/brands/BRZ/documents/specSheets/'+filename+'.pdf'
    return {'url':url,'document':title,'page':page,'local_image':'_research/'+key+'/downloads/'+filename+'_pages/page_%02d.png'%page}

def prepare():
    sens=doc('T66T0110-BNXLHP','T66T0110-BLLHP_Spec','BSP-B-T66T0110-LHP Rev A')
    g=[cyl('Escutcheon',[0,0,0],[0,0,1],3.5,0,.5),
       cyl('Cartridge collar',[0,0,0],[0,0,1],1.125,.5,2.0),
       cyl('Cartridge sleeve',[0,0,0],[0,0,1],.85,2,2.65),
       cyl('Thermostatic stem',[0,0,0],[0,0,1],.25,2.65,3.125,'Brass')]
    product('T66T0110-BNXLHP','Roccesco Sensori thermostatic trim, less handle','wall',[7,7,3.125],'onyx',g,[sens],
            ['Escutcheon diameter 7 in; projection 3.125 in; collar diameter 2.25 in.'],
            ['Handle is separately supplied as HL66110. Cartridge sleeve steps are simplified.'],
            [anchor('Plate diameter',['Escutcheon'],0,7)],True)
    g=[cyl('Handle base',[0,0,0],[0,0,1],1.0,0,1.35),
       box('Handle neck',[-.50,-.50,1.25,.50,.50,2.50],.15),
       box('Horizontal paddle',[-1.2,-.38,2.23,3,.38,2.625],.18)]
    product('HL66110-BNX','Roccesco Sensori thermostat lever handle','wall',[4.2,2,2.625],'onyx',g,[sens],
            ['Height/projection 2.625 in and lever axis-to-end reach 3 in: selected HL66110 detail.'],
            ['Base diameter and left overhang are scaled from the handle detail.','Handle supplied alone with its installation axis at origin; do not place it as an additional escutcheon.'],
            [anchor('Handle projection',['Handle base','Handle neck','Horizontal paddle'],2,2.625)])

    widespread=doc('653110LF-BNXLHP','653110LF-BLLHP_Spec','BSP-L-653110LF-LHP Rev A')
    g=[cyl('Spout base',[0,0,0],[0,0,1],1,0,.16),
       sweep('Oval arch spout',[[0,0,.16],[0,0,6.3125],['arc',[0,-3,9.0625],[0,-6,6.3125]]],.25,oval=[1.125,.5])]
    for x in [-4,4]:
        g.append(cyl('Valve flange '+str(x),[x,0,0],[0,0,1],.9375,0,.16))
        g.append(cyl('Valve stem '+str(x),[x,0,0],[0,0,1],.18,.16,.60,'Brass'))
    product('653110LF-BNXLHP','Roccesco widespread arc faucet, less handles','floor',[9.875,7.25,9.3125],'onyx',g,[widespread],
            ['Height 9.3125 in; outlet height 6.3125 in; reach 6 in; bases 2 in and 1.875 in.'],
            ['ASSUMPTION: 8 in valve centers selected within the published 4-16 in range.','Above-deck scope only; handles supplied separately. Oval section and arc shoulders are drawing-derived.'],
            [anchor('Height',['Spout base','Oval arch spout'],2,9.3125),anchor('Spout base diameter',['Spout base'],0,2)])
    for sku,centers,base_d,lever,h in [('HL53110-BNX',8,1.875,2.5625,2.3125)]:
        g=[]
        for x in [-centers/2,centers/2]:
            sign=-1 if x<0 else 1
            g += [cyl('Handle flange '+str(x),[x,0,0],[0,0,1],base_d/2,0,.12),
                  box('Handle neck '+str(x),[x-.43,-.43,.12,x+.43,.43,h-.18],.15),
                  box('Handle paddle '+str(x),[min(x-.43,x+sign*lever),-.33,h-.40,max(x+.43,x+sign*lever),.33,h],.17)]
        product(sku,'Roccesco widespread lever handle pair','floor',[centers+2*lever,base_d,h],'onyx',g,[widespread],
                ['Handle height 2.3125 in; axis-to-tip reach 2.5625 in; base diameter follows the faucet flange 1.875 in.'],
                ['ASSUMPTION: paired at 8 in centers to align with this section faucet; controls point outward.','Fine lever waisting and edge radii are drawing-derived.'],
                [anchor('Handle height',['Handle flange -4.0','Handle neck -4.0','Handle paddle -4.0'],2,h)])

    tub=doc('T704110-BNXLHP','T704110-BLLHP_Spec','BSP-B-T704110-LHP Rev B')
    # Side profile in local Y/Z: wall at Z=0, outlet drops below axis.
    profile=[(0,.38),(9.85,.38),('arc',(11.43,-.12),(12.5625,-1.40)),
             (12.50,-1.78),(11.70,-1.78),('arc',(10.86,-.80),(9.70,-.38)),(0,-.38)]
    g=[cyl('Spout wall flange',[0,0,0],[0,0,1],1.40625,0,.28),
       {'name':'Rounded projecting tub spout','kind':'profile','origin':[-.875,0,0],'u':[0,0,1],'v':[0,1,0],'normal':[1,0,0],
        'points':profile,'length':1.75,'material':'Finish'},
       cyl('Left handle stem',[-4,0,0],[0,0,1],.14,0,.65,'Brass'),
       cyl('Right handle stem',[4,0,0],[0,0,1],.14,0,.65,'Brass')]
    product('T704110-BNXLHP','Roccesco wall-mounted tub filler trim, less handles','wall',[8.28,3.18625,12.5625],'onyx',g,[tub],
            ['Projection 12.5625 in; nominal outlet reach 11.875 in; flange diameter 2.8125 in; stem centers 8 in.'],
            ['Rounded spout side profile, underside arch and vertical outlet position are drawing-derived.','LHP handles and R70400 rough are separate inventory items.'],
            [anchor('Flange diameter',['Spout wall flange'],0,2.8125),anchor('Projection',['Spout wall flange','Rounded projecting tub spout'],2,12.5625)])
    g=[]
    for x in [-4,4]:
        sign=-1 if x<0 else 1
        g += [cyl('Wall base '+str(x),[x,0,0],[0,0,1],1.375,0,.28),
              box('Handle neck '+str(x),[x-.45,-.45,.28,x+.45,.45,2.7],.15),
              box('Lever '+str(x),[min(x-.45,x+sign*3.125),-.38,2.50,max(x+.45,x+sign*3.125),.38,2.875],.18)]
    product('HL704110-BNX','Roccesco wall tub filler lever handle pair','wall',[14.25,2.75,2.875],'onyx',g,[tub],
            ['Bases diameter 2.75 in; installed handle projection 2.875 in; lever axis-to-tip reach 3.125 in.'],
            ['ASSUMPTION: paired at the companion trim 8 in centers, levers pointing outwards. Fine lever taper is simplified.'],
            [anchor('Handle projection',['Wall base -4','Handle neck -4','Lever -4'],2,2.875)])

    flw=doc('T65722LF-GL','T65722LF-GL_Spec','BSP-L-T65722LF Rev D')
    g=[box('Square wall escutcheon',[-1.15625,-1.15625,0,1.15625,1.15625,.50],.035),
       box('Rear rectangular body',[-.70,-.50,.45,.70,.5,5.75],.035),
       box('Raised valve body',[-.70,-.50,4.75,.70,1.55,5.75],.035),
       box('Flat cantilever spout',[-.70,.02,5.40,.70,.42,10.6875],.035),
       box('Top rectangular lever',[-.68,1.98,4.68,.68,2.34375,7.1],.035),
       box('Lever stem',[-.45,1.3,4.88,.45,2.00,5.60],.035),
       box('Laminar outlet',[-.55,-.13,9.5,.55,.03,9.875],.04,'Detail')]
    product('T65722LF-GL','Frank Lloyd Wright single-handle wall faucet','wall',[2.3125,3.5,10.6875],'gold',g,[flw],
            ['Overall projection 10.6875 in; overall vertical envelope 3.5 in; escutcheon square 2.3125 in; nominal outlet reach 9.625 in.'],
            ['Native model follows the current exact-SKU Frank Lloyd Wright drawing.','Control fore/aft placement and rectangular sections are drawing-derived; no teak insert is added to the non-TK SKU.','R65700 rough-in is separate.'],
            [anchor('Overall projection',['Square wall escutcheon','Flat cantilever spout'],2,10.6875)],True)

    # Optional basin drains: cap diameter is dimensioned; cut tailpiece length is a recorded assumption.
    for sku,finish in [('RP72414BNX','onyx'),('RP72414GL','gold')]:
        g=[cyl('Open tailpiece',[0,0,0],[0,0,1],.625,-6,-1.0,inner=.54),
           cyl('Threaded body',[0,0,0],[0,0,1],.85,-1.20,-.10),
           cyl('Compression washer',[0,0,0],[0,0,1],1.10,-1.15,-.75,'Detail'),
           cyl('Basin flange',[0,0,0],[0,0,1],1.18,-.1,.10),
           cyl('Open cap shadow',[0,0,0],[0,0,1],.80,.10,.28,'Detail'),
           {'name':'Domed push cap','kind':'revolve','origin':[0,0,0],'axis':[0,0,1],
            'profile':[(0,.23),(1.375,.23),('arc',(.78,.46),(0,.50))],'material':'Finish'}]
        product(sku,'Push-button lavatory drain with overflow holes','floor',[2.75,2.75,6.5],finish,g,[widespread],
                ['Cap diameter 2.75 in from the exact RP72414 detail.'],
                ['ASSUMPTION: fixed 6 in tailpiece cut length, 1.25 in outside diameter and underside stack from the drawing.','Overflow ports and threaded internals are simplified; cap shown open.'],
                [anchor('Cap diameter',['Domed push cap'],0,2.75)])

    rain={'url':'https://media.brizo.com/SpecSheet/BSP-B-81392%20Rev%20B.pdf','document':'BSP-B-81392 Rev B','page':1,'visual_review_method':'Web PDF screenshot'}
    g=[cyl('Thin round rain plate',[0,0,0],[0,0,1],5.875,1.775,2.275),
       cyl('Pivot neck',[0,0,0],[0,0,1],.50,.5,1.825),cyl('Connection nut',[0,0,0],[0,0,1],.375,0,.6)]
    for radius,count in [(1,12),(1.8,20),(2.6,28),(3.4,36),(4.2,44),(5,52)]:
        for i in range(count):
            a=2*math.pi*i/count
            g.append(cyl('Spray nozzle %.1f %d'%(radius,i),[radius*math.cos(a),radius*math.sin(a),0],[0,0,1],.06,2.26,2.375,'Detail'))
    product('81392-BNX-2.5','12-inch linear round raincan, 2.5 GPM','ceiling',[11.75,11.75,2.375],'onyx',g,[rain],
            ['Actual plate diameter 11.75 in, plate thickness .5 in, total depth 2.375 in.'],
            ['Catalog market name is 12 in; model uses its dimensioned 11.75 in diameter.','Dense spray array follows the 2.5 GPM variant; individual nozzle positions are approximate.'],
            [anchor('Plate diameter',['Thin round rain plate'],0,11.75)],True)

    rough={'url':'https://media.brizo.com/SpecSheet/BSP-B-R35000-WS%20Rev%20C.pdf','document':'BSP-B-R35000-WS Rev C','page':1,'visual_review_method':'Web PDF screenshot'}
    diamond=[(-2.8125,0),(-2.55,-.9),(-.60,-2.30),(0,-2.46875),(.60,-2.30),(2.55,-.9),(2.8125,0),
             (2.55,.9),(.60,2.30),(0,2.46875),(-.60,2.30),(-2.55,.9)]
    g=[{'name':'Diamond plaster guard','kind':'profile','origin':[0,0,2.35],'u':[1,0,0],'v':[0,1,0],'normal':[0,0,1],
        'points':diamond,'length':.45,'material':'Detail'},
       cyl('Central rough body',[0,0,0],[0,0,1],1.3,.20,2.5,'Brass'),
       cyl('Hot inlet',[0,0,.9],[1,0,0],.72,-3.5,-1.0,'Brass',.4),
       cyl('Cold inlet',[0,0,.9],[1,0,0],.72,1.0,3.5,'Brass',.4),
       cyl('Upper outlet',[0,0,.9],[0,1,0],.72,.8,2.3,'Brass',.4),
       cyl('Test cap',[0,0,0],[0,0,1],1.0,2.65,3.15,'Detail'),
       cyl('Front test stem',[0,0,0],[0,0,1],.15,3.05,3.70,'Brass')]
    product('R35000-WS','Sensori thermostatic rough with stops','wall',[7,4.9375,3.5],'brass',g,[rough],
            ['Inlet-to-inlet width 7 in; plaster guard height 4.9375 in and width 5.625 in.'],
            ['ASSUMPTION: overall body depth 3.5 in includes the protruding test stem; source gives only stringer-to-finish-wall 3.25 in.','Internal flow paths, service stops and guard lettering are simplified.'],
            [anchor('Plaster guard width',['Diamond plaster guard'],0,5.625),anchor('Plaster guard height',['Diamond plaster guard'],1,4.9375)])
    rough={'url':'https://media.brizo.com/SpecSheet/BSP-B-R75000%20Rev%20F.pdf','document':'BSP-B-R75000 Rev F','page':1,'visual_review_method':'Web PDF screenshot'}
    g=[box('Rounded plaster guard',[-2.03125,-2.78125,2.50,2.03125,2.78125,2.70],1.5,'Detail')]
    for label,y,r in [('Lower',-1.4375,1.05),('Upper',1.4375,.88)]:
        end=4.0 if label=='Lower' else 2.8
        stem_end=4.8125 if label=='Lower' else 3.5
        g += [cyl(label+' brass valve',[0,y,0],[0,0,1],r,0,2.6,'Brass'),
              cyl(label+' test cover',[0,y,0],[0,0,1],r,2.6,end,'Detail'),
              box(label+' test cross horizontal',[-r*.8,y-.08,end-.03,r*.8,y+.08,end+.10],0,'Detail'),
              box(label+' test cross vertical',[-.08,y-r*.8,end-.03,.08,y+r*.8,end+.10],0,'Detail'),
              cyl(label+' test stem',[0,y,0],[0,0,1],.10,end,stem_end,'Brass')]
    for y in [-1.4375,1.4375]:
        g += [cyl('Left port '+str(y),[0,y,.85],[1,0,0],.42,-2.53125,-.80,'Brass',.27),
              cyl('Right port '+str(y),[0,y,.85],[1,0,0],.42,.80,2.53125,'Brass',.27)]
    g.append(cyl('Top outlet',[0,0,.85],[0,1,0],.42,1.80,3.375,'Brass',.27))
    product('R75000-WS','MultiChoice integrated diverter rough with stops','wall',[5.0625,6.15625,4.8125],'brass',g,[rough],
            ['With-stops inlet width 5.0625 in; plaster guard 4.0625 x 5.5625 in.','Overall front-stem projection 4.8125 in equals nominal stringer-to-wall 2.5625 in plus wall-to-stem 2.25 in.'],
            ['ASSUMPTION: upper outlet extension and upper test-stem projection are drawing-derived.','Test caps, guard and principal ports represented; internal seats and molded details simplified.'],
            [anchor('Guard height',['Rounded plaster guard'],1,5.5625)])

    # The exact current BT062415 spec depicts a slotted grate despite its Tile-In title.
    drain={'url':'https://media.brizo.com/SpecSheet/BSP-A-BT062415%20Rev%20C.pdf','document':'BSP-A-BT062415 Rev C','page':1,'visual_review_method':'Web PDF screenshot'}
    g=[cyl('PVC socket',[0,0,0],[0,0,1],1.34375,-4.0625,-2.6,'Gray',1.1875),
       cyl('Upper drain body',[0,0,0],[0,0,1],1.80,-2.7,-1.05,'Gray',1.15),
       cyl('Clamping flange',[0,0,0],[0,0,1],3.0625,-1.42,-1.22,'Gray',1.15),
       box('Grate left border',[-2.28125,-2.28125,-.18,-2.02,2.28125,0],.055),
       box('Grate right border',[2.02,-2.28125,-.18,2.28125,2.28125,0],.055),
       box('Grate front border',[-2.03,-2.28125,-.18,2.03,-2.02,0],.055),
       box('Grate back border',[-2.03,2.02,-.18,2.03,2.28125,0],.055)]
    for i in range(8):
        y=-1.90+i*.52
        g.append(box('Horizontal grate bar '+str(i),[-2.02,y,-.13,2.02,y+.24,0],.065))
        x=-.9 if i%2 else .9
        g.append(box('Staggered slot bridge '+str(i),[x-.10,y+.20,-.13,x+.10,min(y+.57,2.04),0],0))
    product('BT062415-BNX','4-inch square point shower drain','floor',[6.125,6.125,4.0625],'onyx',g,[drain],
            ['Flange diameter 6.125 in; grate width/depth 4.5625 in; overall height 4.0625 in; socket OD 2.6875 in.'],
            ['SOURCE CONFLICT: current manufacturer calls BT062415 Tile-In but Rev C depicts a slotted grate. This model follows the dimensioned Rev C drawing and must be reviewed against the purchased part.','Adjustable grate is set at the drawing minimum; detailed screw fittings omitted.'],
            [anchor('Flange diameter',['Clamping flange'],0,6.125)],True)

    rough={'url':'https://media.brizo.com/SpecSheet/BSP-B-BR73240%20Rev%20B.pdf','document':'BSP-B-BR73240 Rev B','page':1,'visual_review_method':'Web PDF screenshot'}
    # Waterproof membrane is a real separate dark material surrounding an open channel.
    g=[box('Membrane front',[-26.59375,-6.3125,-.10,26.59375,-2.21875,0],0,'Detail'),
       box('Membrane back',[-26.59375,2.21875,-.10,26.59375,6.3125,0],0,'Detail'),
       box('Membrane left',[-26.59375,-2.21875,-.10,-23.625,2.21875,0],0,'Detail'),
       box('Membrane right',[23.625,-2.21875,-.10,26.59375,2.21875,0],0,'Detail'),
       box('Channel floor',[-23.625,-2.21875,-.8125,23.625,2.21875,-.72],0),
       box('Front channel lip',[-23.625,-2.21875,-.75,23.625,-2.12,0],0),
       box('Back channel lip',[-23.625,2.12,-.75,23.625,2.21875,0],0),
       box('Left channel lip',[-23.625,-2.12,-.75,-23.52,2.12,0],0),
       box('Right channel lip',[23.52,-2.12,-.75,23.625,2.12,0],0),
       cyl('Drain outlet',[0,0,0],[0,0,1],1.40625,-2.8125,-.75,inner=1.0)]
    for x in [-21,21]:
        for y in [-1.45,1.45]:
            g += [cyl('Adjusting foot %.1f %.1f'%(x,y),[x,y,0],[0,0,1],.20,-5.1875,-.75),
                  box('Foot plate %.1f %.1f'%(x,y),[x-.8,y-.5,-5.4375,x+.8,y+.5,-5.1875],.07,'Detail')]
    product('BR73480','48-inch linear drain rough with membrane and feet','floor',[53.1875,12.625,5.4375],'chrome',g,[rough],
            ['Membrane footprint 53.1875 x 12.625 in; channel length 47.25 in and width 4.4375 in; feet set to published maximum 5.4375 in.'],
            ['Channel floor is simplified level geometry; hydraulic slope and hidden membrane seams are not modeled.','Visible drain trim is a separate inventory item.'],
            [anchor('Membrane length',['Membrane front'],0,53.1875),anchor('Channel length',['Channel floor'],0,47.25)],True)

if __name__=='__main__':
    prepare()
    p.publish()
