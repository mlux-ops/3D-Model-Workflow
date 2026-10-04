# -*- coding: utf-8 -*-
"""Product-specific native geometry; invoke exclusively through revit_run.py."""
import os,sys,json,math,traceback
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,'_tools'))
from wieland_native import WielandFixture,DB,xyz
from native_fixture_support import loop,rounded_rect,cylinder_solid
from System.Collections.Generic import List

def extrude(b,name,origin,u,v,normal,profile,length,mat):
    solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop(origin,u,v,profile)]),normal,length/12.)
    return b.add(name,solid,mat)

def circle_loop(x,y,z,r):
    c=DB.CurveLoop()
    c.Append(DB.Arc.Create(xyz(x+r,y,z),xyz(x-r,y,z),xyz(x,y+r,z)))
    c.Append(DB.Arc.Create(xyz(x-r,y,z),xyz(x+r,y,z),xyz(x,y-r,z)))
    return c

def ring_plate(b,name,w,h,z,t,opening_w,opening_h,mat,corner=.1):
    loops=List[DB.CurveLoop]([loop(xyz(0,0,z),DB.XYZ.BasisX,DB.XYZ.BasisY,rounded_rect(-w/2.,-h/2.,w/2.,h/2.,corner)),
                            loop(xyz(0,0,z),DB.XYZ.BasisX,DB.XYZ.BasisY,rounded_rect(-opening_w/2,-opening_h/2,opening_w/2,opening_h/2,corner))])
    return b.add(name,DB.GeometryCreationUtilities.CreateExtrusionGeometry(loops,DB.XYZ.BasisZ,t/12.),mat)

def pendant(b,m,canopy_d,canopy_h,body_h,cord='Black',drop=48):
    canopy=b.cylinder('Ceiling canopy',xyz(),DB.XYZ.BasisZ,canopy_d/2,0,canopy_h,m[cord],min(.06,canopy_h/3))
    b.cylinder('Suspension cable',xyz(),DB.XYZ.BasisZ,.045,canopy_h,drop-body_h,m[cord])
    b.check_component('Canopy',[canopy],[canopy_d,canopy_d,canopy_h],b.report['source_url'])
    return drop-body_h

def reed(b,m):
    b.cylinder('Polished round wall plate',xyz(),DB.XYZ.BasisZ,2.125,0,.35,m['Nickel'],.06)
    b.cylinder('Central mounting sleeve',xyz(0,0,1.20),DB.XYZ.BasisY,.42,-.68,.68,m['Nickel'],.06)
    b.box('Rear sleeve support',-.32,-.5,.30,.32,.5,1.5,m['Nickel'],.08)
    b.cylinder('Continuous slender stem',xyz(0,0,1.68),DB.XYZ.BasisY,.095,-13.375,13.375,m['Nickel'])
    for center in [-6.95,6.95]:
        profile=[(0,-4.05),(.11,-4.05),('arc',(.17,-3.8),(.275,-3.45)),(.275,3.45),('arc',(.17,3.8),(.11,4.05)),(0,4.05)]
        b.revolve('Tapered spindle housing',xyz(0,center,1.68),DB.XYZ.BasisY,profile,m['Nickel'])
        lens=[(0,center-3.75),('arc',(-.19,center-3.45),(-.20,center-3.05)),(-.20,center+3.05),('arc',(-.19,center+3.45),(0,center+3.75)),('arc',(.19,center+3.45),(.20,center+3.05)),(.20,center-3.05),('arc',(.19,center-3.45),(0,center-3.75))]
        extrude(b,'Outward opal spindle lens',xyz(0,0,1.96),DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ,lens,.04,m['Opal'])

def panasonic(b,m):
    b.expected_category='Mechanical Equipment'
    b.doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(b.doc,DB.BuiltInCategory.OST_MechanicalEquipment)
    body=[]
    for args in [(-5.125,-5.125,-7.5,5.125,5.125,-7.40),(-5.125,-5.125,-7.5,-5.025,5.125,0),(5.025,-5.125,-7.5,5.125,5.125,0),(-5.125,-5.125,-7.5,5.125,-5.025,0),(-5.125,5.025,-7.5,5.125,5.125,0)]:
        body.append(b.box('Galvanized fan housing',*(args+(m['Steel'],))))
    b.check_component('Main housing',body,[10.25,10.25,7.5],b.report['source_url']+' page 4')
    grille=[]
    grille.append(ring_plate(b,'Rounded white perimeter bezel',13,13,0,.875,10.4,10.4,m['White'],.45))
    holes=List[DB.CurveLoop]([loop(xyz(0,0,.58),DB.XYZ.BasisX,DB.XYZ.BasisY,[(-5.23,-5.23),(5.23,-5.23),(5.23,5.23),(-5.23,5.23)])])
    for row in range(43):
        for col in range(43):
            holes.Add(circle_loop((col-21)*.235+(row%2)*.04,(row-21)*.235,.58,.060))
    grille.append(b.add('Perforated removable grille - 1849 actual holes',DB.GeometryCreationUtilities.CreateExtrusionGeometry(holes,DB.XYZ.BasisZ,.08/12.),m['White']))
    b.check_component('Grille',grille,[13,13,.875],b.report['source_url']+' page 4')
    b.cylinder('Dark internal centrifugal impeller',xyz(0,0,-4),DB.XYZ.BasisZ,3.6,0,2.3,m['Black'],.12)
    b.box('Electronics enclosure',-4.6,-4.6,-2.2,-1.4,-1.8,-.2,m['Black'],.12)
    profile=[(1.85,0),(2.9375,0),(2.9375,1.0),(2.18,2.35),(1.9375,2.65),(1.9375,3.875),(1.81,3.875),(1.81,2.65),(2.02,2.25),(2.80,.9),(2.80,.12),(1.85,.12)]
    b.revolve('Stepped 4/6-inch duct adapter',xyz(5.125,-1.75,-3.375),DB.XYZ.BasisX,profile,m['Steel'])
    b.box('Electrical junction box',3.62,1.6,-6.2,5.12,5.1,-1.7,m['Steel'],.10)

def vera(b,m):
    w=37.87
    b.box('Square mounting plate',-2.375,-2.375,0,2.375,2.375,.5,m['Black'])
    b.box('Central support',-1.1,-.45,.5,1.1,.45,2.4,m['Black'])
    front=[(3.10,-.80),(3.17,-.80),('arc',(3.25,0),(3.17,.80)),(3.10,.80)]
    rear=[(2.40,-.80),(2.33,-.80),('arc',(2.25,0),(2.33,.80)),(2.40,.80)]
    cap=[(2.33,-.80),(3.17,-.80),('arc',(3.25,0),(3.17,.80)),(2.33,.80),('arc',(2.25,0),(2.33,-.80))]
    for p in [front,rear]:extrude(b,'Curved longitudinal housing',xyz(-w/2+.09,0,0),DB.XYZ.BasisZ,DB.XYZ.BasisY,DB.XYZ.BasisX,p,w-.18,m['Black'])
    for x in [-w/2,w/2-.08]:extrude(b,'End cap',xyz(x,0,0),DB.XYZ.BasisZ,DB.XYZ.BasisY,DB.XYZ.BasisX,cap,.08,m['Black'])
    for y in [-.785,.72]:b.box('Recessed upper/lower diffuser',-w/2+.10,y,2.38,w/2-.1,y+.065,3.12,m['Opal'])

def tetra(b,m):
    b.box('Wall backplate',-2.375,-2.5625,0,2.375,2.5625,.5,m['Black'])
    for box in [(-2.5,-6,1.25,-2.35,6,5.75),(2.35,-6,1.25,2.5,6,5.75),(-2.5,-6,5.60,2.5,6,5.75),(-2.5,-6,1.25,2.5,6,1.4)]:b.box('Open rectangular extrusion',*(box+(m['Black'],)))
    for y in [-5.7,5.52]:
        b.box('Recessed end glass',-2.23,y,1.52,2.23,y+.12,5.4,m['Clear'],.1)
        b.box('Recessed end optic',-1.55,y+.02,2.2,1.55,y+.10,4.8,m['Opal'],.1)
    b.box('Housing support',-.8,-1,.5,.8,1,1.3,m['Black'])

def silvio(b,m):
    b.tube('Black perimeter trim',xyz(),DB.XYZ.BasisZ,2.5,2.34,0,.75,m['Black'])
    b.cylinder('Recessed opal optic',xyz(),DB.XYZ.BasisZ,2.36,.15,.68,m['Opal'],.06)
    b.cylinder('Rear mounting pan',xyz(),DB.XYZ.BasisZ,2.35,0,.10,m['Black'])

def sky_reflector(b,m,z):
    return b.revolve('Shallow matte-black reflector',xyz(0,0,z),DB.XYZ.BasisZ,[(.27,0),(8.96,0),('arc',(9,.035),(8.96,.10)),(.27,.33)],m['Black'])

def sky_flush(b,m):
    b.cylinder('Rear 6.5-inch mount',xyz(),DB.XYZ.BasisZ,3.25,0,1.1,m['Aluminum'],.08)
    sky_reflector(b,m,1.3)
    b.cylinder('Central polished lamp rim',xyz(),DB.XYZ.BasisZ,2.63,2.9,3.85,m['Aluminum'],.08)
    b.cylinder('Opal light disk',xyz(),DB.XYZ.BasisZ,2.44,3.78,4,m['Opal'],.06)
    b.cylinder('Central support',xyz(),DB.XYZ.BasisZ,.22,1.0,3.2,m['Aluminum'])

def sky_pendant(b,m):
    start=pendant(b,m,5.3,1.25,17.5,'Aluminum')
    first=len(b.forms)
    b.cylinder('Polished central stem',xyz(),DB.XYZ.BasisZ,.14,start,47.5,m['Aluminum'])
    sky_reflector(b,m,start+9.2)
    b.cylinder('Polished lamp rim',xyz(),DB.XYZ.BasisZ,2.63,47.1,47.9,m['Aluminum'],.08)
    b.cylinder('Opal light disk',xyz(),DB.XYZ.BasisZ,2.44,47.82,48,m['Opal'],.06)
    b.check_component('Fixture body',b.forms[first:],[18,18,17.5],b.report['source_url'])

def stephord(b,m):
    b.cylinder('Black circular mount',xyz(),DB.XYZ.BasisZ,2.375,0,.63,m['Black'],.08)
    b.revolve('Curved clear annular glass',xyz(),DB.XYZ.BasisZ,[(1.05,.63),(2.12,.63),('arc',(2.31,.86),(2.28,1.22)),('arc',(1.91,1.63),(1.39,1.45)),('arc',(1.13,1.23),(1.05,1.02))],m['Clear'])
    b.cylinder('Black center disk',xyz(),DB.XYZ.BasisZ,1.08,.62,1.17,m['Black'],.07)
    b.tube('Recessed opal light ring',xyz(),DB.XYZ.BasisZ,2.05,1.24,.64,.77,m['Opal'])

def cedar(b,m):
    b.cylinder('Round 5-inch backplate',xyz(),DB.XYZ.BasisZ,2.5,0,.625,m['Black'],.08)
    b.cylinder('Lower black supporting dish',xyz(0,-2.875,3),DB.XYZ.BasisY,2,0,.15,m['Black'],.05)
    b.tube('Open clear cylindrical shade',xyz(0,-2.725,3),DB.XYZ.BasisY,2,1.92,0,5.60,m['Clear'])
    b.cylinder('Rear vertical support',xyz(0,-2.60,1.30),DB.XYZ.BasisY,.24,0,4.8,m['Black'])
    b.box('Wall support arm',-.5,-1.75,.55,.5,-1.2,3,m['Black'],.08)
    b.revolve('Domed opal internal diffuser',xyz(0,-2.56,3),DB.XYZ.BasisY,[(0,0),(1.13,0),('arc',(.88,.87),(0,1.13))],m['Opal'])

def silas(b,m):
    b.cylinder('Round midnight-black backplate',xyz(),DB.XYZ.BasisZ,2.25,0,.5,m['Black'],.05)
    b.cylinder('Central collar',xyz(0,0,1.46),DB.XYZ.BasisY,.54,-.82,.82,m['Black'])
    b.tube('Clear linear optic sleeve',xyz(0,0,1.46),DB.XYZ.BasisY,.45,.37,-12,12,m['Clear'])
    b.cylinder('Inner white light rod',xyz(0,0,1.46),DB.XYZ.BasisY,.31,-11.96,11.96,m['Opal'])
    b.box('Rear collar support',-.34,-.6,.45,.34,.6,1.6,m['Black'])

def rona(b,m):
    b.box('Square chrome backplate',-2.25,-2.25,0,2.25,2.25,.625,m['Chrome'],.10)
    b.box('Backplate stepped face',-2.06,-2.06,.625,2.06,2.06,.72,m['Chrome'],.09)
    b.cylinder('Chrome center clamp',xyz(0,0,2.06),DB.XYZ.BasisY,.69,-1.1,1.1,m['Chrome'],.06)
    b.cylinder('Opal acrylic cylinder',xyz(0,0,2.06),DB.XYZ.BasisY,.625,-12,12,m['Opal'],.06)
    b.box('Clamp support',-.65,-.9,.70,.65,.9,2.06,m['Chrome'],.08)

def pandora(b,m):
    b.box('Tall mounting body',-2.31,-10.5,0,2.31,-5.30,1.55,m['Black'],.22)
    b.box('Raised front of mount',-2.08,-10.32,1.50,2.08,-5.5,1.67,m['Black'],.18)
    b.box('Offset vertical light blade',-1.92,-7.82,3.39,-1.44,10.5,3.87,m['Black'],.07)
    b.box('Rear-facing opal blade strip',-1.86,-7.70,3.27,-1.50,10.40,3.39,m['Opal'],.06)
    b.box('Blade support arm',-1.98,-8.05,1.55,-1.38,-7.60,3.6,m['Black'],.06)

def vista(b,m):
    b.box('Full-height mounting plate',-2.125,-4.3125,0,2.125,4.3125,.25,m['Black'])
    for box in [(-2.125,-2.63,.25,-1.98,2.63,3.5),(1.98,-2.63,.25,2.125,2.63,3.5),(-2.125,-2.63,3.35,2.125,2.63,3.5)]:b.box('Open-ended raised wall body',*(box+(m['Black'],)))
    for y in [-2.35,2.23]:b.box('Recessed upper or lower diffuser',-1.81,y,.6,1.81,y+.12,3.10,m['Opal'],.07)

def exhaust(b,m):
    start=pendant(b,m,4.4,.3,5.71,'Graphite');first=len(b.forms)
    b.cylinder('Graphite cylindrical shell',xyz(),DB.XYZ.BasisZ,1.18,start,start+3.84,m['Graphite'],.08)
    b.tube('Smoked-bronze exposed knurled insert',xyz(),DB.XYZ.BasisZ,1.03,.83,start+3.75,48,m['Bronze'])
    for index in range(40):
        angle=2*math.pi*index/40
        x=.998*math.cos(angle);y=.998*math.sin(angle)
        b.cylinder('Insert fine vertical machining ridge',xyz(x,y,0),DB.XYZ.BasisZ,.036,start+3.93,47.85,m['Bronze'])
    b.cylinder('Recessed white optic',xyz(),DB.XYZ.BasisZ,.81,47.46,47.58,m['Opal'])
    b.cylinder('Small side machine screw',xyz(0,-1.13,start+1.16),DB.XYZ.BasisY,.12,-.05,.02,m['Black'])
    b.check_component('Pendant body',b.forms[first:],[2.36,2.36,5.71],b.report['source_url'])

def pylon(b,m):
    start=pendant(b,m,4.6,.8,18.6,'Brass');first=len(b.forms)
    b.cylinder('Fluted brass cylindrical body',xyz(),DB.XYZ.BasisZ,.6,start,47.55,m['Brass'])
    for i in range(16):
        angle=2*math.pi*i/16
        b.cylinder('Fine longitudinal brass rib',xyz(.565*math.cos(angle),.565*math.sin(angle),0),DB.XYZ.BasisZ,.035,start+.08,47.4,m['Brass'])
    b.tube('Clear lower optical collar',xyz(),DB.XYZ.BasisZ,.6,.50,47.5,48,m['Clear'])
    b.cylinder('Recessed opal optic',xyz(),DB.XYZ.BasisZ,.46,47.55,47.89,m['Opal'])
    b.cylinder('Black cord entry',xyz(),DB.XYZ.BasisZ,.085,start-.18,start,m['Black'])
    b.check_component('Brass and glass body',b.forms[first:-1],[1.2,1.2,18.6],b.report['source_url'])

def a_tube(b,m):
    start=pendant(b,m,4.92,.75,23.62,'White');first=len(b.forms)
    b.cylinder('Slim black aluminum tube',xyz(),DB.XYZ.BasisZ,.39,start,47.46,m['Black'],.06)
    b.tube('Clear optical tip',xyz(),DB.XYZ.BasisZ,.39,.30,47.40,48,m['Clear'])
    b.cylinder('Recessed luminous core',xyz(),DB.XYZ.BasisZ,.28,47.3,47.7,m['Opal'])
    b.check_component('Pendant body',b.forms[first:],[.78,.78,23.62],b.report['source_url'])

def castle(b,m):
    start=pendant(b,m,4.6,1,5.2);first=len(b.forms)
    profile=[(0,0),(1.05,0),('arc',(1.78,.34),(2.05,1.20)),(2.05,3.03),(1.88,3.03),(1.88,1.28),('arc',(1.55,.5),(.98,.20)),(0,.20)]
    b.revolve('Soft matte-black upper dome',xyz(0,0,start),DB.XYZ.BasisZ,profile,m['Black'])
    b.revolve('Lower opal bowl',xyz(0,0,start),DB.XYZ.BasisZ,[(0,2.7),(1.95,2.7),(1.95,3.12),('arc',(1.49,4.53),(0,5.2))],m['Opal'])
    b.check_component('Pendant body',b.forms[first:],[4.1,4.1,5.2],b.report['source_url'])

def motif_slim(b,m):
    start=pendant(b,m,4.625,.5,26.75);first=len(b.forms)
    b.cylinder('Upper black terminal',xyz(),DB.XYZ.BasisZ,.375,start,start+2.1,m['Black'])
    b.tube('Long clear cylindrical lens',xyz(),DB.XYZ.BasisZ,.375,.30,start+2.0,46.9,m['Clear'])
    b.cylinder('Fine LED filament core',xyz(),DB.XYZ.BasisZ,.09,start+2.05,46.95,m['Opal'])
    b.cylinder('Lower black terminal',xyz(),DB.XYZ.BasisZ,.375,46.85,48,m['Black'])
    b.check_component('Pendant body',b.forms[first:],[.75,.75,26.75],b.report['source_url'])

def run_one(app,key):
    jobs=json.load(open(os.path.join(ROOT,'CATALOG_JOBS.json')))
    job=next(j for j in jobs if j['key']==key);b=None
    try:
        b=WielandFixture(app,job['out'],job['name'],job['manufacturer'],job['model'],job['model'],job['host'],job['dimensions'])
        b.report.update({'source_url':job['source_url'],'rfa_search':job['rfa_search'],'catalog_key':key})
        mats={}
        for label,definition in job['material_definitions'].items():mats[label]=b.material(label,**definition)
        globals()[job['builder']](b,mats)
        b.note(job['notes'])
        return b.finish()
    except Exception:
        if b is not None:
            b.fail()
            with open(os.path.join(job['out'],'validation.json'),'w') as stream:json.dump(b.report,stream,indent=2,default=str)
        raise

def main(app):
    result=[]
    selection_path=os.path.join(ROOT,'CATALOG_RUN_KEYS.json')
    selected=json.load(open(selection_path)) if os.path.isfile(selection_path) else None
    for job in json.load(open(os.path.join(ROOT,'CATALOG_JOBS.json'))):
        if selected is not None and job['key'] not in selected:continue
        try:
            report=run_one(app,job['key']);result.append({'key':job['key'],'passed':report['technical_pass'],'path':report['rfa_path']})
        except Exception:result.append({'key':job['key'],'passed':False,'error':traceback.format_exc()})
        with open(os.path.join(ROOT,'CATALOG_BATCH_RESULT.json'),'w') as stream:json.dump(result,stream,indent=2)

if __name__=='__main__':main(__revit__.Application)
