"""Prepare explicit per-product construction inputs; native execution is separate."""
from pathlib import Path
import json
import math
import re
from PIL import Image

SECTION=Path(__file__).resolve().parents[1]
GROUPS={g['sku']:g for g in json.loads((SECTION/'_research/groups.json').read_text(encoding='utf-8'))}
CATALOG='https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf'
PALETTE={
 'white':{'rgb':[242,243,240],'gloss':.17,'reflectivity':.06,'class':'Plastic'},
 'chrome':{'rgb':[195,198,201],'gloss':.96,'reflectivity':.88,'class':'Metal'},
 'onyx':{'rgb':[58,60,62],'gloss':.92,'reflectivity':.72,'class':'Metal'},
 'black':{'rgb':[20,21,22],'gloss':.17,'reflectivity':.10,'class':'Metal'},
 'gold':{'rgb':[195,159,90],'gloss':.63,'reflectivity':.62,'class':'Metal'},
 'bronze':{'rgb':[158,128,89],'gloss':.56,'reflectivity':.48,'class':'Metal'},
 'black_chrome':{'rgb':[77,73,69],'gloss':.60,'reflectivity':.58,'class':'Metal'},
 'ceramic':{'rgb':[245,245,241],'gloss':.86,'reflectivity':.22,'class':'Ceramic'},
 'detail':{'rgb':[24,25,26],'gloss':.17,'reflectivity':.04,'class':'Plastic'},
 'graphite':{'rgb':[64,67,69],'gloss':.36,'reflectivity':.16,'class':'Glass'},
 'brass':{'rgb':[160,124,64],'gloss':.40,'reflectivity':.38,'class':'Metal'},
 'green':{'rgb':[31,113,66],'gloss':.18,'reflectivity':.05,'class':'Plastic'},
 'gray':{'rgb':[131,132,130],'gloss':.32,'reflectivity':.12,'class':'Plastic'}
}
MODELS=[]

def cyl(name,origin,axis,radius,a,b,material='Finish',inner=None):
    p={'name':name,'kind':'cylinder','origin':origin,'axis':axis,'radius':radius,'a':a,'b':b,'material':material}
    if inner:p['inner_radius']=inner
    return p
def box(name,bounds,radius=0,material='Finish'):
    return {'name':name,'kind':'box','bounds':bounds,'radius':radius,'material':material}
def sweep(name,path,radius,material='Finish',oval=None):
    p={'name':name,'kind':'sweep','path':path,'radius':radius,'material':material}
    if oval:p['oval']=oval
    return p
def source(page):
    return {'url':CATALOG,'document':'Hansgrohe 2026 US Price Book','page':page,'local_image':'_research/catalog_pages/page_%03d.png'%page}
def anchor(label,parts,axis,value):
    return {'label':label,'parts':parts,'axis':axis,'nominal_in':value}
def product(sku,name,host,dimensions,finish,geometry,sources,authority,limitations,anchors=(),all_authoritative=False,search=None):
    group=GROUPS[sku];key=group['key'];row=group['rows'][0]
    materials={'Finish':PALETTE[finish],'Detail':PALETTE['detail'],'Graphite':PALETTE['graphite'],'Ceramic':PALETTE['ceramic'],
               'Brass':PALETTE['brass'],'Green':PALETTE['green'],'Gray':PALETTE['gray']}
    common=['Independent visualization reconstruction with fixed product dimensions and editable native materials.',
            'Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.',
            'No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.']
    type_name=re.sub(r'[\\:{}\[\]|;<>?`~]',' - ',sku+' - '+str(row.get('finish') or finish))
    spec={'key':key,'model':sku,'manufacturer':row.get('manufacturer') or 'See source','type_name':type_name,
          'basename':re.sub(r'[^A-Za-z0-9_.-]+','_',str(row.get('manufacturer') or 'Fixture')+'_'+sku+'_R2025'),
          'name':name,'host':host,'configured_dimensions_in':dimensions,'materials':materials,'geometry':geometry,'sources':sources,
          'dimension_authority':authority,'limitations':list(limitations)+common,'anchors':list(anchors),
          'all_overall_dimensions_authoritative':all_authoritative,
          'rfa_search':search or {'result':'No acceptable no-account RFA recovered','evidence':'_research/'+key+'/sources.json'}}
    MODELS.append(spec)
    return spec

def prepare_hansgrohe_pilot():
    # Rainfinity baton: catalog width and height; taper follows the side drawing.
    depth=25/25.4
    g=[cyl('Threaded hose connection',[0,0,0],[0,0,1],.25,0,.375),
       box('Rounded handle',[-.75,-depth/2+.03,.375,.75,depth/2,4.0],.16),
       {'kind':'loft','name':'Tapered spray head','sections':[
           {'center':[0,.015,3.625],'size':[1.5,depth-.03],'radius':.16},
           {'center':[0,-depth/2+.33,9],'size':[1.5,.60],'radius':.12}]},
       box('Graphite spray insert',[-.66,-depth/2,5,.66,-depth/2+.08,8.95],.04,'Graphite')]
    for row in range(19):
        for col in range(6):
            x=-.51+col*.204;y=5.12+row*.203
            g.append(cyl('Spray opening %02d %02d'%(row,col),[x,-depth/2-.012,y],[0,1,0],.033,0,.05,'Detail'))
    product('26866701','Rainfinity Baton Handshower 100','floor',[1.5,depth,9],'white',g,[source(229),
            {'url':'https://www.bimobject.com/en-us/hansgrohe/product/26866001','note':'Manufacturer listing includes finish 26866701.'}],
            ['Width 1.5 in and overall length 9 in: catalog drawing.','25 mm body depth is a dimensional reference from the manufacturer BIM listing; its conflicting width is not used.'],
            ['Matte white is retained from the exact inventory SKU and manufacturer BIM finish list; the 2026 main catalog omits that finish.','Nozzle count and undimensioned body taper are approximate.'],
            [anchor('Overall length',['Rounded handle','Tapered spray head','Threaded hose connection'],2,9),anchor('Body width',['Rounded handle'],0,1.5)])
    for sku,finish in [('15758001','chrome'),('15758701','white')]:
        g=[cyl('Escutcheon',[0,0,0],[0,0,1],2.9375,0,.1875),
           cyl('Upper collar',[0,1.4375,0],[0,0,1],.82,.1875,.625),
           cyl('Upper control',[0,1.4375,0],[0,0,1],.5625,.625,2.5),
           box('Upper selector tab',[-.15,1.8,2.4,.15,2.4,2.65],.10),
           cyl('Lower collar',[0,-1.4375,0],[0,0,1],1.15,.1875,.625),
           cyl('Temperature ring',[0,-1.4375,0],[0,0,1],.95,.625,.80,'Graphite'),
           cyl('Thermostatic knob',[0,-1.4375,0],[0,0,1],.875,.80,3),
           box('Lower lever',[-.20,-3.9375,2.94,.20,-1.6375,3.125],.17)]
        product(sku,'Ecostat S Thermostatic Trim with 2 Functions','wall',[5.875,6.875,3.125],finish,g,[source(302)],
                ['Escutcheon diameter 5.875 in; centers 2.875 in; lower control diameter 1.75 in; lower lever reach 2.5 in.',
                 'Projection configured at the published 3.125 in maximum; overall height derives from the down-pointing lower lever and plate.'],
                ['Installation-depth range is fixed at its outer limit for this visualization.','Temperature markings and small internal collars are simplified.']+
                (['Matte white identity comes from scheduled 15758701 and its manufacturer instruction listing; current family drawing is the same 15758 body.'] if finish=='white' else []),
                [anchor('Escutcheon diameter',['Escutcheon'],0,5.875)],False)

def prepare_brizo_pilot():
    doc={'url':'https://bravo.requested-info.com/brands/BRZ/documents/specSheets/650110LF-BL_Spec.pdf','document':'Brizo BSP-L-650110LF Rev B','page':1,
         'local_image':'_research/650110LF-BNX/downloads/650110LF-BL_Spec_pages/page_01.png'}
    g=[cyl('Base escutcheon',[0,0,0],[0,0,1],1,0,.1875),
       sweep('Continuous oval arc spout',[[0,0,.1875],[0,0,5.75],['arc',[0,-3.09375,8.875],[0,-6.1875,5.75]]],.25,oval=[1.125,.5]),
       cyl('Side valve hub',[0,0,3.125],[1,0,0],.5625,.35,1.75),
       cyl('Lever',[1.75,0,0],[0,0,1],.25,2.4,6.15),
       box('Recessed aerator',[-.46,-6.35,5.75,.46,-6.05,5.79],.06,'Detail')]
    product('650110LF-BNX','Roccesco single-handle arc lavatory faucet','floor',[3,7.4375,9.125],'onyx',g,[doc],
            ['Overall height 9.125 in, outlet height 5.75 in, reach 6.1875 in and base diameter 2 in: manufacturer drawing.',
             'Overall width derives from the 2.5625 in body-to-handle dimension plus the larger base; tube section thickness is drawing-derived.'],
            ['Above-deck visualization only; below-deck mounting shank and supply hoses are omitted.','Oval tube section and lever height are derived from the drawing, not separately dimensioned.'],
            [anchor('Base diameter',['Base escutcheon'],0,2),anchor('Overall height',['Base escutcheon','Continuous oval arc spout'],2,9.125)],False,
            {'result':'AVAILABLE_LOGIN_REQUIRED','url':'https://market.bimsmith.com/product/Brizo/revit-bim-ROCCESCO-SingleHandle-Lavatory-Faucet-with-Arc-Spout--650110LFPC-62969',
             'note':'Revit download led to Sign in to continue. Chrome listing would also need finish adaptation; no login used.'})
    doc={'url':'https://assets.specbooks.cloud/brand/brizo/spec/22628776/document/spec-sb-eli3kf.pdf','document':'Brizo BSP-B-813110 Rev A','page':1,
         'local_image':'_research/813110-BNX-2.5/downloads/spec-sb-eli3kf_pages/page_01.png'}
    g=[cyl('Open halo ring',[0,0,0],[0,0,1],6.125,2.875,3.40,inner=5.25),
       {'name':'Radial waterway spoke','kind':'profile','origin':[0,-.875,0],'u':[1,0,0],'v':[0,0,1],'normal':[0,1,0],
        'points':[(0,1.5),(1.3,1.5),(5.55,2.875),(5.55,3.4),(0,3.4)],'length':1.75,'material':'Finish'},
       cyl('Connection boss',[0,0,0],[0,0,1],.62,.45,1.8),cyl('Male connection',[0,0,0],[0,0,1],.25,0,.6)]
    for i in range(72):
        a=2*math.pi*i/72
        g.append(cyl('Perimeter spray nozzle %02d'%i,[5.68*math.cos(a),5.68*math.sin(a),0],[0,0,1],.065,3.4,3.5,'Detail'))
    product('813110-BNX-2.5','Roccesco open Halo raincan showerhead','ceiling',[12.25,12.25,3.5],'onyx',g,[doc],
            ['Diameter 12.25 in and total head depth 3.5 in: manufacturer drawing.','Radial spoke width 1.75 in: manufacturer drawing.'],
            ['Open annulus and radial spoke are retained; internal waterway and fine edge radii are simplified.','Arm is supplied as its separate 899110-12-BNX family.'],
            [anchor('Halo diameter',['Open halo ring'],0,12.25)],True)
    g=[cyl('Canopy',[0,0,0],[0,0,1],2.5,0,1),cyl('Suspension arm',[0,0,0],[0,0,1],.4375,1,13.5),
       cyl('Threaded end',[0,0,0],[0,0,1],.25,13.5,14)]
    product('899110-12-BNX','Roccesco 12-inch ceiling arm with flange','ceiling',[5,5,14],'onyx',g,[doc],
            ['Canopy diameter 5 in and visible projection 14 in: manufacturer drawing; marketed arm length is 12 in.'],
            ['Concealed connection above the finished ceiling plane is omitted.','Arm diameter and canopy thickness are drawing-derived.'],
            [anchor('Canopy diameter',['Canopy'],0,5),anchor('Projection',['Canopy','Suspension arm','Threaded end'],2,14)],True)
    doc={'url':'https://bravo.requested-info.com/brands/BRZ/documents/specSheets/T755110-BLLHP_Spec.pdf','document':'Brizo BSP-B-T755110-LHP Rev A','page':1,
         'local_image':'_research/T755110-BNXLHP/downloads/T755110-BLLHP_Spec_pages/page_01.png'}
    for sku in ['T755110-BNXLHP','T756110-BNXLHP']:
        g=[cyl('Escutcheon',[0,0,0],[0,0,1],3.75,0,.625),
           cyl('Upper collar',[0,1.4375,0],[0,0,1],.75,.625,1.70),
           cyl('Upper stem',[0,1.4375,0],[0,0,1],.20,1.70,2.625),
           cyl('Lower collar',[0,-1.4375,0],[0,0,1],1.25,.625,1.95),
           cyl('Cartridge outer sleeve',[0,-1.4375,0],[0,0,1],.9,1.95,2.65),
           cyl('Cartridge middle sleeve',[0,-1.4375,0],[0,0,1],.67,2.65,3.30),
           cyl('Cartridge end sleeve',[0,-1.4375,0],[0,0,1],.42,3.30,4.05),
           cyl('Lower stem',[0,-1.4375,0],[0,0,1],.18,4.05,4.50,'Brass')]
        product(sku,'Roccesco integrated thermostatic diverter trim, less handles','wall',[7.5,7.5,4.5],'onyx',g,[doc],
                ['Escutcheon diameter 7.5 in; maximum stem projection 4.5 in; upper projection 2.625 in.',
                 'Collar diameters 1.5 and 2.5 in; vertical centers scaled from the manufacturer drawing at 2.875 in.'],
                ['LHP scope is modeled without the separately scheduled HL75110 handles.','Cartridge steps and stem details are simplified.','Cartridge center spacing is drawing-derived and is not a rough-in fabrication dimension.'],
                [anchor('Escutcheon diameter',['Escutcheon'],0,7.5)],True)

def publish():
    rows=[]
    for spec in MODELS:
        folder=SECTION/spec['key'];src=folder/'source';src.mkdir(parents=True,exist_ok=True)
        (src/'model_spec.json').write_text(json.dumps(spec,indent=2),encoding='utf-8')
        wrapper='# -*- coding: utf-8 -*-\nimport os,sys\nsys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..","_harness")))\nfrom family_factory import build\nbuild('+repr(spec['key'])+',__revit__.Application)\n'
        (src/'build.py').write_text(wrapper,encoding='utf-8')
        textures=folder/'textures';textures.mkdir(exist_ok=True)
        used={p.get('material','Finish') for p in spec['geometry']}
        for label in used:
            Image.new('RGB',(32,32),tuple(spec['materials'][label]['rgb'])).save(textures/(label.replace(' ','_')+'.png'))
        rows.append({'key':spec['key'],'model':spec['model'],'parts':len(spec['geometry']),'source':str(src/'model_spec.json')})
    (SECTION/'_harness/prepared_models.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print(json.dumps(rows))

if __name__=='__main__':
    prepare_hansgrohe_pilot()
    prepare_brizo_pilot()
    publish()
