# -*- coding: utf-8 -*-
"""Nine explicit custom appliance replacements; invoke only via revit_run.py."""
import os
import sys
import json
import datetime
import traceback
import math

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(HERE)
sys.path.insert(0,ROOT)
from family_common import *

TEMPLATE=r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model.rft'

class Appliance(object):
    def __init__(self,doc,app,c):
        self.doc,self.app,self.c=doc,app,c
        self.w,self.d,self.h=c['target_xyz_mm']
        self.parts=[]
        self.params={}
        if c['kind'] in ('miele_oven','double_oven'):
            names=['Metal Finish','Black Finish','Glass Finish','Interior Finish','Display Finish']
        elif c['kind']=='dishwasher':
            names=['Metal Finish','Black Finish','Panel Finish','Display Finish']
        elif c['kind'].startswith('wine'):
            names=['Metal Finish','Black Finish','Clear Glass Finish','Panel Finish','Wood Finish','Display Finish']
        elif c['kind']=='fridge':
            names=['Metal Finish','Black Finish','Panel Finish']
        else:
            names=['Metal Finish','Black Finish','Grate Finish','Display Finish']
        for name in names:
            rgb,gloss,trans=c['palette'][name]
            bitmap=os.path.join(ROOT,c['slug'],'source','rework_r1',name.replace(' ','_')+'.png')
            mat=material(doc,app,c['model']+' '+name,rgb,gloss,trans,bitmap)
            self.params[name]=mat_parameter(doc,name,mat)

    def add(self,name,pname,solid):
        return bind(self.doc,solid,name,self.params[pname],self.parts)

    def box(self,name,pname,x0,y0,z0,x1,y1,z1):
        if min(x1-x0,y1-y0,z1-z0)<0.8:
            raise ValueError('Sub-tolerance component '+name)
        return self.add(name,pname,box(x0,y0,z0,x1,y1,z1))

    def cyl(self,name,pname,c,r,length,axis=(0,0,1),inner=0):
        return self.add(name,pname,cylinder(c,r,length,axis,inner))

    def front(self,name,pname,x0,z0,x1,z1,y,depth,r=2):
        return self.add(name,pname,rounded_front(x0,z0,x1,z1,r,y,depth))

    def frame(self,name,pname,x0,z0,x1,z1,y,depth,border):
        for suffix,a,b,c,d in [('Left',x0,z0,x0+border,z1),('Right',x1-border,z0,x1,z1),
                              ('Bottom',x0+border,z0,x1-border,z0+border),('Top',x0+border,z1-border,x1-border,z1)]:
            self.box(name+' '+suffix,pname,a,y,b,c,y+depth,d)

    def handle(self,name,z,width,skin,finish='Metal Finish',round_handle=False):
        if round_handle:
            radius=11.5
            self.cyl(name+' Grip',finish,(-width/2,13,z),radius,width,(1,0,0))
            for side,x in [('L',-width/2+20),('R',width/2-20)]:
                self.cyl(name+' Support '+side,finish,(x,13,z),9,skin-12,(0,1,0))
                self.cyl(name+' Cap '+side,finish,(x-12,13,z),13,24,(1,0,0))
        else:
            self.front(name+' Grip',finish,-width/2,z-9,width/2,z+9,0,14,4)
            for side,x in [('L',-width/2+15),('R',width/2-15)]:
                self.box(name+' Support '+side,finish,x-7,12,z-8,x+7,skin+2,z+8)

    def oven_module(self,label,z0,height,skin,miele=True):
        w,d=self.w,self.d
        black='Black Finish'
        facade=black if miele else 'Metal Finish'
        fascia_h=108 if miele else 115
        door_top=z0+height-fascia_h-5
        self.box(label+' Case Back','Metal Finish',-w/2+17,d-18,z0+7,w/2-17,d,z0+height-7)
        for side,x0,x1 in [('L',-w/2+17,-w/2+32),('R',w/2-32,w/2-17)]:
            self.box(label+' Case '+side,'Metal Finish',x0,skin+25,z0+7,x1,d-18,z0+height-7)
        self.box(label+' Case Top','Metal Finish',-w/2+32,skin+25,z0+height-22,w/2-32,d-18,z0+height-7)
        self.box(label+' Case Base','Metal Finish',-w/2+32,skin+25,z0+7,w/2-32,d-18,z0+22)
        self.box(label+' Cavity Back','Interior Finish',-w*.38,d-22,z0+48,w*.38,d-19,door_top-50)
        for i in range(3 if height<550 else 5):
            rack_z=z0+height*.15+i*(height*.47/(2 if height<550 else 4))
            for side,x in [('L',-w*.39),('R',w*.39)]:
                self.box(label+' Rack Guide '+str(i)+side,'Metal Finish',x-2,skin+42,rack_z,x+2,d-38,rack_z+3)
        self.frame(label+' Door',facade,-w/2,z0,w/2,door_top,skin,22,55)
        self.front(label+' Window','Glass Finish',-w/2+55,z0+55,w/2-55,door_top-55,skin+2,5,4)
        self.front(label+' Control Fascia',facade,-w/2,z0+height-fascia_h,w/2,z0+height,skin,25,2)
        # A real recessed separation, not a line added outside the envelope.
        self.box(label+' Vent Slot',black,-w*.41,skin+1,door_top+1,w*.41,skin+12,door_top+4)
        self.front(label+' Display','Display Finish',-62,z0+height-76,62,z0+height-35,skin-1.5,2,2)
        if miele:
            for i,x in enumerate([-235,-180,-122,122,180,235]):
                self.box(label+' Touch Key '+str(i),'Metal Finish',x-3,skin-1.5,z0+height-56,x+3,skin,z0+height-50)
            self.handle(label+' Handle',door_top-30,w*.77,skin,black,False)
        else:
            for i,x in enumerate([-w*.30,w*.30]):
                self.cyl(label+' Knob Base '+str(i),'Black Finish',(x,skin-14,z0+height-56),27,17,(0,1,0))
                self.cyl(label+' Knob '+str(i),'Metal Finish',(x,skin-34,z0+height-56),23,24,(0,1,0))
                self.box(label+' Knob Index '+str(i),'Black Finish',x-1.5,skin-35,z0+height-48,x+1.5,skin-33,z0+height-34)
            self.handle(label+' Handle',door_top-29,w*.81,skin,'Metal Finish',True)

    def miele_oven(self):
        self.oven_module('Oven',0,self.h,self.c['handle_projection_mm'],True)

    def double_oven(self):
        # Upper speed oven is shorter than the lower full-size oven.
        lower=self.h-499
        self.oven_module('Lower Oven',0,lower,self.c['handle_projection_mm'],False)
        self.oven_module('Upper Speed Oven',lower+3,self.h-lower-3,self.c['handle_projection_mm'],False)

    def dishwasher(self):
        w,d,h=self.w,self.d,self.h
        self.box('Cabinet Back','Metal Finish',-w/2,d-16,20,w/2,d,h)
        for side,x0,x1 in [('L',-w/2,-w/2+15),('R',w/2-15,w/2)]:
            self.box('Cabinet Side '+side,'Metal Finish',x0,38,20,x1,d-16,h)
        self.box('Cabinet Top','Metal Finish',-w/2+15,36,h-15,w/2-15,d-16,h)
        self.box('Machine Base','Black Finish',-w/2+15,80,12,w/2-15,d-24,130)
        self.box('Recessed Toe Panel','Black Finish',-w/2+20,68,20,w/2-20,76,113)
        self.front('Factory Door Skin','Panel Finish',-w/2+3,116,w/2-3,h-28,0,33,3)
        self.box('Top Control Strip','Metal Finish',-w/2+3,0,h-26,w/2-3,35,h-1)
        self.box('Control Display','Display Finish',45,4,h-2,88,24,h)
        for i,x in enumerate([-215,-175,-130,-85,125,160,195]):
            self.cyl('Top Control Key '+str(i),'Black Finish',(x,15,h-2),4,2)
        for i,x in enumerate([-w/2+35,w/2-35]):
            for j,y in enumerate([104,d-46]):
                self.cyl('Adjustable Foot %d %d'%(i,j),'Black Finish',(x,y,0),13,21)

    def wine(self,tall):
        w,d,h=self.w,self.d,self.h
        toe=48 if tall else 83
        wall=24
        self.box('Case Back','Metal Finish',-w/2,d-22,0,w/2,d,h)
        for side,x0,x1 in [('L',-w/2,-w/2+wall),('R',w/2-wall,w/2)]:
            self.box('Case '+side,'Black Finish',x0,35,0,x1,d-22,h)
        self.box('Case Roof','Black Finish',-w/2+wall,35,h-24,w/2-wall,d-22,h)
        self.box('Toe Housing','Black Finish',-w/2+wall,45,0,w/2-wall,d-22,toe)
        self.frame('Door Frame','Panel Finish',-w/2+3,toe,w/2-3,h-3,0,31,35)
        self.box('Insulated Door Glazing','Clear Glass Finish',-w/2+38,8,toe+35,w/2-38,14,h-38)
        self.box('Interior Rear Liner','Metal Finish',-w/2+wall,d-28,toe,w/2-wall,d-23,h-24)
        for i in range(29):
            x=-w*.42+i*w*.84/28
            self.box('Lower Air Slot %02d'%i,'Metal Finish',x,41,10,x+3,45,toe-12)
        self.box('Touch Display','Display Finish',-70,32,h-64,70,35,h-42)
        # Eight beech shelves/two zones for 6722; five/one zone for 7172.
        levels=[toe+150,toe+335,toe+520,toe+705,h-760,h-575,h-390,h-205] if tall else [toe+66,toe+196,toe+326,toe+456,toe+576]
        for i,z in enumerate(levels):
            for j in range(9):
                x=-w/2+48+j*(w-112)/8
                self.box('Beech Shelf %02d Slat %02d'%(i,j),'Wood Finish',x,50,z,x+16,d-44,z+10)
            self.box('Beech Shelf %02d Front'%i,'Wood Finish',-w/2+44,42,z-3,w/2-44,55,z+13)
            self.box('Shelf %02d NoteBoard'%i,'Black Finish',-70,40,z-2,70,42,z+12)
        if tall:
            middle=h*.52
            self.box('Two Zone Separator','Black Finish',-w/2+wall,35,middle,w/2-wall,d-24,middle+36)
            self.box('Zone Temperature Display','Display Finish',-60,31,middle+9,60,35,middle+28)
        for side in ['Top','Bottom']:
            z=h-35 if side=='Top' else toe+4
            self.box('Right Hinge '+side,'Metal Finish',w/2-39,31,z,w/2-9,52,z+20)

    def fridge(self):
        w,d,h=self.w,self.d,self.h
        toe=84
        split1=toe+502
        split2=split1+269
        self.box('Rear Cabinet','Black Finish',-w/2,d-24,185,w/2,d,h)
        for side,x0,x1 in [('L',-w/2,-w/2+28),('R',w/2-28,w/2)]:
            self.box('Cabinet Side '+side,'Black Finish',x0,34,12,x1,d,h)
        self.box('Cabinet Roof','Black Finish',-w/2+28,34,h-25,w/2-28,d-24,h)
        self.box('Base Chassis','Black Finish',-w/2+28,34,16,w/2-28,d-32,toe)
        self.box('Toe Vent Back','Black Finish',-w/2+28,29,20,w/2-28,34,toe-8)
        for i in range(58):
            x=-w/2+37+i*(w-78)/57
            self.box('Toe Vent Slat %02d'%i,'Metal Finish',x,27,23,x+3,30,toe-12)
        self.front('Bottom Freezer Factory Front','Panel Finish',-w/2,toe,w/2,split1,0,36,3)
        self.front('Convertible Drawer Factory Front','Panel Finish',-w/2,split1+3,w/2,split2,0,36,3)
        self.front('French Door Left Factory Front','Panel Finish',-w/2,split2+3,-1.5,h-3,0,36,3)
        self.front('French Door Right Factory Front','Panel Finish',1.5,split2+3,w/2,h-3,0,36,3)
        self.box('French Door Central Gasket','Black Finish',-1.5,4,split2+3,1.5,18,h-6)
        for i,x in enumerate([-w/2+37,w/2-37]):
            for j,y in enumerate([75,d-57]):
                self.cyl('Retracted Foot %d %d'%(i,j),'Black Finish',(x,y,0),17,18)
        # Small factory attachment plates are set within the appliance, no custom pulls.
        for label,z in [('Upper',h-42),('Mid',split2+12)]:
            for side,x in [('L',-w/2+20),('R',w/2-56)]:
                self.box(label+' Hinge Cover '+side,'Metal Finish',x,33,z,x+36,65,z+23)

    def star(self,name,x,y,z,r,height):
        pts=[]
        for i in range(10):
            a=math.pi/2+i*math.pi/5
            radius=r if i%2==0 else r*.49
            pts.append((x+radius*math.cos(a),y+radius*math.sin(a),z))
        self.add(name,'Grate Finish',prism(pts,DB.XYZ.BasisZ,height))

    def rangetop(self):
        w,d,h=self.w,self.d,self.h
        # Complete envelope includes knobs and upper grate tips, with no backguard.
        self.box('Case Back','Metal Finish',-w/2,d-12,0,w/2,d,h-48)
        for side,x0,x1 in [('L',-w/2,-w/2+12),('R',w/2-12,w/2)]:
            self.box('Case '+side,'Metal Finish',x0,43,0,x1,d-12,h-48)
        self.box('Case Base','Metal Finish',-w/2+12,43,0,w/2-12,d-12,12)
        self.box('Porcelain Deck','Black Finish',-w/2+12,107,h-62,w/2-12,d-10,h-51)
        self.front('Stainless Control Fascia','Metal Finish',-w/2,10,w/2,h-69,41,14,6)
        self.cyl('Rounded Front Bolster','Metal Finish',(-w/2,57,h-48),13,w,(1,0,0))
        col=w/4
        centers=[-w/2+col*.5,-w/2+col*1.5,w/2-col*.5]
        for i,x in enumerate(centers):
            for j,y in enumerate([d*.37,d*.77]):
                n='Burner %d %d'%(i,j)
                self.cyl(n+' Seat','Metal Finish',(x,y,h-51),44,5)
                self.star(n+' Star Crown',x,y,h-46,49,9)
                self.star(n+' Star Cap',x,y,h-37,44,5)
                # Grate cage around each zone, with four inward pot supports.
                rx=col*.425; ry=d*.175
                self.box(n+' Grate L','Grate Finish',x-rx,y-ry,h-20,x-rx+8,y+ry,h)
                self.box(n+' Grate R','Grate Finish',x+rx-8,y-ry,h-20,x+rx,y+ry,h)
                self.box(n+' Grate Front','Grate Finish',x-rx+8,y-ry,h-20,x+rx-8,y-ry+8,h)
                self.box(n+' Grate Rear','Grate Finish',x-rx+8,y+ry-8,h-20,x+rx-8,y+ry,h)
                for k,a in enumerate([math.pi*.25,math.pi*.75,math.pi*1.25,math.pi*1.75]):
                    u,v=(math.cos(a),math.sin(a)),(-math.sin(a),math.cos(a))
                    pts=[(x+u[0]*rr+v[0]*ss,y+u[1]*rr+v[1]*ss,h-18) for rr,ss in [(53,-5),(135,-5),(135,5),(53,5)]]
                    self.add(n+' Pot Support '+str(k),'Grate Finish',prism(pts,DB.XYZ.BasisZ,18))
        cx=col*.5
        self.box('Griddle Tray','Metal Finish',cx-col*.43,115,h-48,cx+col*.43,d-26,h-20)
        self.box('Griddle Cooking Surface','Grate Finish',cx-col*.40,140,h-20,cx+col*.40,d-42,h-14)
        self.box('Griddle Drain','Black Finish',cx-col*.38,122,h-19,cx+col*.38,135,h-17)
        knob_x=[-w*.43,-w*.33,-w*.21,-w*.11,w*.12,w*.33,w*.43]
        for i,x in enumerate(knob_x):
            self.cyl('Knob %d Bezel'%i,'Black Finish',(x,33,74),25,11,(0,1,0))
            self.cyl('Knob %d Grip'%i,'Metal Finish',(x,2,74),21,34,(0,1,0))
            self.front('Knob %d Blade'%i,'Metal Finish',x-5,58,x+5,90,0,7,2)
            self.box('Knob %d Index'%i,'Black Finish',x-1.5,0,86,x+1.5,2,93)
        self.box('Center Indicator','Display Finish',-10,39,120,10,41,124)

def build_one(slug,app):
    folder=os.path.join(ROOT,slug)
    c=json.load(open(os.path.join(folder,'source','rework_r1','config.json')))
    out=os.path.join(folder,c['rfa_name'])
    checkpoint=os.path.join(folder,'source','rework_r1','build_result.json')
    result={'slug':slug,'model':c['model'],'started_utc':str(datetime.datetime.utcnow()),'ok':False,'stage':'starting','rfa':out}
    doc=None;tx=None
    try:
        assert app.VersionNumber=='2025'
        if os.path.exists(out):
            raise RuntimeError('Replacement already exists; use a new revision or validate the existing file. '+out)
        doc=app.NewFamilyDocument(TEMPLATE)
        tx=DB.Transaction(doc,'Custom appliance '+c['model']);tx.Start()
        doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_SpecialityEquipment)
        doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED).Set(1)
        doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
        fm=doc.FamilyManager
        fm.NewType(c['model']+' - Custom R1')
        for key,value in [('Manufacturer',c['brand']),('Model',c['model']),('Description','Custom dimension-correct visualization replacement; see round-1 notes'),('URL',c['source_urls'][0])]:
            p=fm.get_Parameter(key)
            if p:fm.Set(p,value)
        for name,value in zip(['Overall Width','Overall Depth','Overall Height'],c['target_xyz_mm']):
            p=fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False)
            fm.Set(p,value/304.8)
            fm.SetFormula(p,str(value)+' mm')
        b=Appliance(doc,app,c)
        kind=c['kind']
        if kind.startswith('wine'):
            b.wine(kind=='wine_tall')
        else:
            getattr(b,kind)()
        doc.Regenerate();tx.Commit()
        result['parts']=b.parts
        result['build_bounds']=measure(list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement)))
        result['stage']='geometry_built';write_json(checkpoint,result)
        opts=DB.SaveAsOptions();opts.OverwriteExistingFile=False
        doc.SaveAs(out,opts)
        doc.Close(False);doc=None
        result.update(ok=True,stage='saved_custom_family',revit_version=app.VersionNumber,
                      finished_utc=str(datetime.datetime.utcnow()))
    except Exception:
        result['error']=traceback.format_exc()
        if tx and tx.GetStatus()==DB.TransactionStatus.Started:tx.RollBack()
    finally:
        if doc:
            try:doc.Close(False)
            except Exception:pass
        write_json(checkpoint,result)
    return result

if __name__=='__main__':
    chosen=os.environ.get('APPLIANCE_R1_SLUGS','').split(',')
    results=[]
    for c in json.load(open(os.path.join(HERE,'configs.json'))):
        if chosen!=[''] and c['slug'] not in chosen:continue
        result=build_one(c['slug'],__revit__.Application)
        results.append(result)
        write_json(os.path.join(HERE,'build_results.json'),results)
