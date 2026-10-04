"""Remaining section fixtures; source dimensions and uncertain scope remain explicit."""
import copy,math
import prepare_products as p
from prepare_products import cyl,box,sweep,anchor,product
from prepare_completion_a import reference

def prepare():
    ref=reference('https://techcomm.kohler.com/techcomm/pdf/K-77685_spec_US-CA_Kohler_en.pdf','Kohler K-77685 specification, 2026-10-01',
                  '_research/K-77685-NA/downloads/K-77685_spec_US-CA_Kohler_en_pages/page_03.png',3)
    g=[cyl('Filter cartridge',[0,0,0],[0,0,1],1.475,0,8.35),
       cyl('Twist collar',[0,0,0],[0,0,1],1.50,8.30,8.95),
       box('Rounded manifold cover',[-1.53125,-1.5,8.8,1.53125,1.5,12.125],.30),
       box('Back mounting bracket',[-1.35,1.4,9.1,1.35,1.875,12.1],.12,'Gray')]
    product('K-77685-NA','Aquifer single-cartridge filter body','floor',[3.0625,3.375,12.125],'white',g,[ref],
            ['Body height 12.125 in, front width 3.0625 in, and total bracket depth 3.375 in.'],
            ['The two 24-inch connection tubes are installation-dependent and omitted from this rigid-body family.','Cartridge/manifold split and small corner radii are drawing-derived.'],
            [anchor('Body height',['Filter cartridge','Rounded manifold cover'],2,12.125)],True)

    ref=reference('https://media.deltafaucet.com/SpecSheet/DSP-A-DT062412%20Rev%20B.pdf','Delta DSP-A-DT062412 Rev B')
    source=next(s for s in p.MODELS if s['key']=='BT062415-BNX')
    g=copy.deepcopy(source['geometry'])
    product('DT062412','4-inch square point shower drain','floor',[6.125,6.125,4.0625],'chrome',g,[ref],
            ['Grate 4.5625 in square; flange 6.125 in diameter; minimum assembly height 4.0625 in; socket OD 2.6875 in.'],
            ['The manufacturer drawing shows a slotted grate although the product title says Tile-in. This model follows the inspected Rev B geometry.','Minimum adjustment setting represented; thread and screw details simplified.'],
            [anchor('Flange diameter',['Clamping flange'],0,6.125)],True)

    ref=reference('https://media.brizo.com/SpecSheet/BSP-L-R65700%20Rev%20B.pdf','Brizo BSP-L-R65700 Rev B')
    plate=box('Mounting plate',[-1.78125,-1,.0,1.78125,1,.125],.16,'Brass')
    holes=[cyl('Plate fixing',[x,y,0],[0,0,1],.125,-.1,.3) for x in [-1.53125,1.53125] for y in [-.75,.75]]
    g=[{'kind':'cut','name':'Perforated mounting plate','base':plate,'cutters':holes,'material':'Brass'},
       cyl('Brass manifold',[0,0,.80],[1,0,0],.60,-1.25,1.25,'Brass'),
       cyl('Upper branch',[0,.40,0],[0,0,1],.44,.20,2.4,'Brass'),
       cyl('Lower branch',[0,-.40,0],[0,0,1],.44,.20,2.4,'Brass'),
       box('Rectangular plaster guard',[-.625,-.625,2.25,.625,.625,4],.12,'Detail')]
    product('R65700','Single-handle wall lavatory rough','wall',[3.5625,2,4],'brass',g,[ref],
            ['Overall mounting plate 3.5625 x 2 in; full rough projection 4 in; fixing centers 3.0625 x 1.5 in.'],
            ['Hidden valve passages, stop screws and plaster-guard lettering are not modeled.'],
            [anchor('Mounting plate width',['Perforated mounting plate'],0,3.5625)],True)

    sink_sources=[reference('https://cdn.blanco.com/assets/hlr-system/svg/841/205841.svg','BLANCO INTEOS 30 top drawing'),
                  reference('https://cdn.blanco.com/assets/hlr-system/svg/824/205824.svg','BLANCO INTEOS 30 side drawing'),
                  reference('https://www.blanco.com/us/sinks/inteos/blancointeos30-u_276.724/443306','Exact 443306 product page')]
    cavity={'kind':'loft','sections':[{'center':[0,0,-9],'size':[25.2,13.9],'radius':.59},
                                     {'center':[0,0,-1.25],'size':[26.75,15.75],'radius':.59},
                                     {'center':[0,0,.4],'size':[28.25,17.3],'radius':1.0}]}
    outer={'kind':'loft','sections':[{'center':[0,0,-9.5],'size':[26.3,15.0],'radius':.75},
                                    {'center':[0,0,-.25],'size':[29,18.5],'radius':1.0}]}
    g=[{'kind':'cut','name':'Tapered SILGRANIT basin','base':outer,'cutters':[cavity,cyl('Drain opening',[8.75,0,0],[0,0,1],1.75,-10,-8.7)]},
       {'kind':'cut','name':'Flat undermount rim','base':box('Rim',[-15,-9.75,-.30,15,9.75,0],1),'cutters':[cavity]}]
    s=product('443306','INTEOS 30-U scheduled black visual variant','floor',[30,19.5,9.5],'black',g,sink_sources,
              ['External 30 x 19.5 x 9.5 in; nominal bowl opening 26.75 x 15.75 in; bowl depth 9 in; drain 3.5 in.'],
              ['IDENTITY HOLD: exact manufacturer SKU 443306 is White, while the schedule requests Black. Black is retained only as the requested visual variant; no replacement SKU is asserted.','Internal floor taper, bowl wall thickness and ledge transitions are drawing-derived; no fabrication template is implied.','The 28.25 x 18 inch supplied cutout is a separate countertop opening, not the sink envelope.'],
              [anchor('External width',['Flat undermount rim'],0,30)],True)
    s['materials']['Finish']=dict(s['materials']['Finish'],gloss=.12,reflectivity=.04)

    flange=reference('https://www.blanco.com/us/sinks/sink-accessories/strainers-and-drain-covers/','BLANCO strainer and flange identities')
    g=[cyl('Disposal opening collar',[0,0,0],[0,0,1],1.75,-.90,-.05,inner=1.58),
       cyl('Flat sink flange',[0,0,0],[0,0,1],2.15,-.08,.10,inner=1.58),
       cyl('Inner dark seal',[0,0,0],[0,0,1],1.60,-.85,-.35,'Detail',1.48)]
    product('240328','Disposal flange scheduled black visual variant','floor',[4.3,4.3,1],'black',g,[flange],
            ['Manufacturer identifies compatibility with nominal 3.5-inch disposal openings.'],
            ['IDENTITY HOLD: 240328 is a White SKU, while the schedule requests Black. Black geometry is a visual variant only.','ASSUMPTION: outer rim 4.3 in, collar length 0.9 in and rim thickness 0.18 in are photo-derived; no exact dimensional cut sheet was recovered.'],
            [anchor('Opening collar nominal OD',['Disposal opening collar'],0,3.5)])

    ref=reference('https://www.insinkerator.com/en-us/shop/insinkerator/products/garbage-disposals/insinkerator-pwr-75hp','InSinkErator Power .75 HP manufacturer product specifications')
    profile=[(0,0),(2.8,0),(3.20,.30),(3.20,2.1),(3.75,2.70),(4.125,3.70),(4.125,7.70),
             (3.7,8.30),(3.7,9.40),(3.0,10.15),(2.8,10.6),(0,10.6)]
    g=[{'kind':'revolve','name':'Motor and grind housing','origin':[0,0,0],'axis':[0,0,1],'profile':profile,'material':'Gray'},
       cyl('Upper mounting neck',[0,0,0],[0,0,1],2.3,10.4,11.25,'Detail'),
       cyl('Mounting ring',[0,0,0],[0,0,1],2.75,11.15,11.60,'Gray'),
       cyl('Sink flange',[0,0,0],[0,0,1],2.10,11.5,12.25,'Gray',1.7),
       cyl('Discharge socket',[0,0,5.3],[0,1,0],.9,3.2,4.0,'Detail',.75)]
    product('80019-ISE','Power Series .75 HP disposer motor body','floor',[8.25,8.25,12.25],'gray',g,[ref],
            ['Current manufacturer body specification is 12.25 in high and 8.25 in wide.'],
            ['IDENTITY HOLD: the current manufacturer page redirects the Power .75 product to package SKU 81222K; schedule 80019-ISE is retained as the requested legacy package identity.','ASSUMPTION: the motor body is shared; cord, adapter and discharge elbow are excluded.','Housing profile and band proportions are photo-derived.'],
            [anchor('Overall body height',['Motor and grind housing','Sink flange'],2,12.25)])

    ref=reference('https://pro.duravit.us/pro/content/homepage/series/series/overview/products~402880943a1b6e1b013a1bd20b39003d.us-en.html?nser=1110&product=3169419&ncat=bathtubs','Duravit 700332000000090 official product dimensions')
    outer={'kind':'loft','sections':[{'center':[0,0,0],'size':[53,23.7],'radius':2.3},
                                    {'center':[0,0,18.625],'size':[57.5,28.0],'radius':1.1}]}
    cavity={'kind':'loft','sections':[{'center':[0,0,1],'size':[43,18],'radius':3.5},
                                     {'center':[0,0,19.25],'size':[55.25,25.5],'radius':2.3}]}
    cutters=[cavity,cyl('Drain opening',[-22,0,0],[0,0,1],1.0625,-1,2),cyl('Overflow opening',[-30,0,15.6],[1,0,0],.75,0,5)]
    g=[{'kind':'cut','name':'Open acrylic tub body','base':outer,'cutters':cutters},
       {'kind':'cut','name':'Rectangular rim','base':box('Rim',[-29.5,-14.75,18.50,29.5,14.75,18.875],1.1),'cutters':[cavity]}]
    product('700332000000090','Starck 59-inch built-in bath body','floor',[59,29.5,18.875],'ceramic',g,[ref],
            ['Official body dimensions 59 x 29.5 x 18.875 in.'],
            ['The scheduled SKU includes a support frame; its concealed, installation-dependent frame is omitted from this visible tub-body family.','Interior slopes, floor profile, drain location and overflow diameter are drawing-derived.','Manufacturer lists STEP/DWG/DXF for this exact model but no public RFA on the inspected page.'],
            [anchor('Rim length',['Rectangular rim'],0,59)],True)

    ref=reference('https://media.brizo.com/SpecSheet/BSP-B-BT0732416%20Rev%20B.pdf','Brizo reversible linear drain dimensions, BSP-B-BT0732416 Rev B')
    L=45.625;W=2.6875
    g=[box('Front narrow frame',[-L/2,-W/2,-1.0625,L/2,-W/2+.10,0]),
       box('Back narrow frame',[-L/2,W/2-.10,-1.0625,L/2,W/2,0]),
       box('Left end frame',[-L/2,-W/2+.08,-1.0625,-L/2+.10,W/2-.08,0]),
       box('Right end frame',[L/2-.10,-W/2+.08,-1.0625,L/2,W/2-.08,0]),
       box('Solid reversible cover',[-L/2+.22,-W/2+.23,-.17,L/2-.22,W/2-.23,-.035],.07)]
    for x in [-18,0,18]:g.append(box('Support tab '+str(x),[x-.3,-.65,-1.0625,x+.3,.65,-.16]))
    product('BT0734816-BNX','48-inch nominal reversible linear drain trim','floor',[L,W,1.0625],'onyx',g,[ref],
            ['Actual trim 45.625 x 2.6875 in; minimum height 1.0625 in; maximum adjustable height 1.375 in.'],
            ['Solid metal side is shown; the reversible tile insert option is not populated with a tile.','Minimum-height fixed pose; frame spacers and small drain removal tool omitted.','The separate rough BR73480 and optional wall edge are not part of this trim family.'],
            [anchor('Trim length',['Front narrow frame'],0,L)],True)

    ref=reference('https://westbrass.com/product/12-4-bath-waste-overflow-assembly-with-tip-toe-drain-plug-and-illusionary-faceplate-sch-40-pvc-pipe/','Westbrass TD954 manufacturer product')
    g=[cyl('12 inch overflow tube',[0,0,0],[0,0,1],.95,0,12,inner=.80),
       cyl('Overflow elbow receiver',[0,0,12],[0,1,0],1.0,-.95,1.50,inner=.80),
       cyl('4 inch waste tube',[0,0,.75],[0,1,0],.95,0,4,inner=.80),
       cyl('Bottom tee',[0,0,0],[0,0,1],1.10,-1.5,1.9,inner=.80),
       cyl('Drain shoe',[0,4,.75],[0,0,1],1.20,0,1.75,inner=.90)]
    product('TD954-20LT','TD954 PVC waste and overflow, less visible trim','floor',[2.4,6.3,14.5],'white',g,[ref],
            ['Official TD954 description specifies 12-inch and 4-inch pipe lengths and nominal 1.5-inch Sch.40 PVC.'],
            ['IDENTITY HOLD: base TD954 is manufacturer-verified; the -20LT exact suffix was not independently verified.','ASSUMPTION: less-trim interpretation follows the schedule; visible stopper/overflow cover are omitted.','Pipe assembled positions, sockets and elbow envelopes are approximate; supplied pipes are field-cut to the selected tub.'],
            [anchor('Overflow pipe length',['12 inch overflow tube'],2,12)])

    ref=reference('https://westbrass.com/product/tip-toe-tub-trim-set-with-floating-faceplate/','Westbrass TD9028 manufacturer thread and finish description')
    for sku in ['TD9028-PCW','TD9028-LS-PCW']:
        g=[cyl('Drain threaded shoe',[-3,0,0],[0,0,1],.9375,-1.3,.0,inner=.75),
           cyl('Drain flange',[-3,0,0],[0,0,1],1.30,-.1,.10,inner=.75),
           cyl('Tip-toe stem',[-3,0,0],[0,0,1],.40,.0,.38,'Detail'),
           {'kind':'revolve','name':'Mushroom drain cap','origin':[-3,0,0],'axis':[0,0,1],
            'profile':[(0,.22),(1.45,.22),['arc',[.8,.45],[0,.50]]]},
           cyl('Floating overflow faceplate',[3,0,0],[0,0,1],1.60,0,.40),
           cyl('Overflow mounting ring',[3,0,0],[0,0,1],1.25,-.4,0,'Gray',1.0)]
        product(sku,'White tip-toe drain and floating overflow trim','floor',[9.05,3.20,1.8],'white',g,[ref],
                ['Manufacturer specifies 1.5-inch NPSM coarse drain thread with 1.875-inch nominal external diameter.'],
                ['The two trim components are displayed side-by-side, not in a tub installation pose.','ASSUMPTION: stopper cap 2.9 in and overflow plate 3.2 in are inferred from the product photo; no exact trim dimensional drawing was recovered.','The legacy -LS-PCW row uses the corrected TD9028-PCW geometry based on the other matching project rows; vendor confirmation remains required.'],
                [anchor('Thread exterior diameter',['Drain threaded shoe'],0,1.875)])

    # Separate push button: image-derived geometry is intentionally not a cut-sheet pass.
    ref=reference('https://www.totousa.com/filemanager_uploads/product_assets/PartsManual/PD-01451_446EN.pdf','TOTO PD-01451 Aquia IV exact component illustration',
                  '_research/CT446CEFGNT40_01/downloads/PD-01451_446EN_pages/page_01.png')
    g=[cyl('Circular button bezel',[0,0,0],[0,0,1],.93,-.18,.11,inner=.80),
       cyl('Button mounting sleeve',[0,0,0],[0,0,1],.78,-1.2,-.12,inner=.69),
       {'kind':'cut','name':'Split dual flush buttons','base':cyl('Face',[0,0,0],[0,0,1],.79,.07,.18),
        'cutters':[box('Button split',[-.035,-1,.02,.035,1,.3])]},
       cyl('Small flush rod',[-.32,0,0],[0,0,1],.09,-5.5,-.8,'Gray'),
       cyl('Full flush rod',[.32,0,0],[0,0,1],.09,-5.5,-.8,'Gray')]
    product('THU842#01-A','Aquia IV push-button and adjustable rods, indicative geometry','floor',[1.86,1.86,5.68],'white',g,[ref],
            ['Exact part identity is verified in the manufacturer component illustration; no independent numeric component dimensions are published there.'],
            ['DIMENSION HOLD: all button and rod dimensions are inferred from the illustrated relationship to the known tank; they are not manufacturer-verified dimensions.','Rod length 5.5 in is an illustrative uncut setting. This family is suitable only for approximate visualization until the supplied component is measured.'],[])

    ref=reference('https://media.brizo.com/SpecSheet/BSP-B-T84613%20Rev%20D.pdf','Brizo HydraChoice T84613 Rev D')
    g=[cyl('Round trim',[0,0,0],[0,0,1],1.75,0,.40625),
       cyl('Inset spray holder',[0,0,0],[0,0,1],.82,.37,.46,'Detail'),
       cyl('Full spray face',[0,0,0],[0,0,1],.73,.43,.52),
       cyl('Concealed rough housing',[0,0,0],[0,0,1],1.35,-3.2,-.02,'Brass'),
       cyl('Rough inlet',[0,0,-2.0],[0,-1,0],.40,.5,1.65,'Brass',.27)]
    for r,n in [(.25,6),(.48,12),(.64,16)]:
        for i in range(n):g.append(cyl('Spray nozzle %.2f %d'%(r,i),[r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n),.51],[0,0,1],.05,0,.06,'Detail'))
    sku=next(s for s in p.GROUPS if s.startswith('T84613-BNX,'))
    product(sku,'HydraChoice round full-spray assembly, historical descoped row','wall',[3.5,3.5,3.77],'onyx',g,[ref],
            ['Trim diameter 3.5 in and face projection 0.40625 in: manufacturer trim drawing.'],
            ['Historical body-spray row remains descoped; modeling does not restore procurement scope.','SH84103 spray face and R84100 concealed housing are simplified inferred geometry; only trim dimensions are independently verified.','Spray is shown in a neutral fixed pose; dynamic pop-out motion is not modeled.'],
            [anchor('Trim diameter',['Round trim'],0,3.5)])

if __name__=='__main__':
    prepare();p.publish()
