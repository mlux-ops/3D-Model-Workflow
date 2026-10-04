# -*- coding: utf-8 -*-
"""Construct and validate native visualization appliances. Use the shared lock runner."""
import os
import sys
import json
import traceback
import datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from family_common import *

TEMPLATE=r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model.rft'

class Builder(object):
    def __init__(self,doc,app,config):
        self.doc,self.app,self.c=doc,app,config
        self.parts=[]
        self.params={}
        definitions=json.load(open(os.path.join(ROOT,'finish_definitions.json')))
        if config['kind'] in ('washer','dryer'):
            cabinet=config['finish']
            mapping={'Cabinet Finish':cabinet,'Trim Finish':'Bronze Rim' if config['brand']=='LG' else 'Stainless Steel',
                     'Glass Finish':'Black Glass','Controls Finish':'Black Plastic','Interior Finish':'Gray Interior'}
        elif config['kind']=='cooktop':
            mapping={'Glass Finish':'Black Glass','Metal Finish':'Stainless Steel','Grate Finish':'Black Plastic'}
        elif config['kind']=='hood':
            mapping={'Metal Finish':'Stainless Steel','Dark Finish':'Black Plastic','Light Lens Finish':'White'}
        else:
            mapping={'Cabinet Finish':'Black Plastic','Panel Finish':'Panel Ready','Glass Finish':'Clear Glass',
                     'Shelf Finish':'Stainless Steel','Interior Finish':'Black Plastic'}
        for pname,finish in mapping.items():
            rgb,gloss,transparency=definitions[finish]
            bitmap=os.path.join(ROOT,config['slug'],'source',finish.replace(' ','_')+'_diffuse.png')
            mat=material(doc,app,config['model']+' '+pname,rgb,gloss,transparency,bitmap)
            self.params[pname]=mat_parameter(doc,pname,mat)

    def add(self,solid,name,pname):
        return bind(self.doc,solid,name,self.params[pname],self.parts)

    def box(self,name,pname,x0,y0,z0,x1,y1,z1):
        return self.add(box(x0,y0,z0,x1,y1,z1),name,pname)

    def cylinder(self,name,pname,center,r,length,direction=(0,0,1),inner=0):
        return self.add(cylinder(center,r,length,direction,inner),name,pname)

    def laundry(self):
        c=self.c; w,h,d=c['width'],c['height'],c['depth']; washer=c['kind']=='washer'
        self.add(rounded_front(-w/2,12,w/2,h,9,43,d-43),'Body','Cabinet Finish')
        # Feet and body remain within the published overall closed-appliance envelope.
        for ix,x in enumerate((-w/2+35,w/2-35)):
            for iy,y in enumerate((80,d-45)):
                self.cylinder('Foot%d%d'%(ix,iy),'Controls Finish',(x,y,0),14,12)
        self.add(rounded_front(-w/2+2,h-22,w/2-2,h,5,38,d-38),'Top Lid','Cabinet Finish')
        self.box('Control Fascia','Cabinet Finish',-w/2+4,30,h-155,w/2-4,46,h-23)
        self.cylinder('Selector Bezel','Controls Finish',(0,19,h-80),39,14,(0,1,0))
        self.cylinder('Selector Dial','Trim Finish',(0,9,h-80),33,16,(0,1,0))
        self.box('Selector Index','Controls Finish',-1.5,7,h-58,1.5,9,h-49)
        self.add(rounded_front(w*.15,h-124,w*.46,h-34,4,24,8),'Display Panel','Glass Finish')
        for i in range(4):
            self.box('Display Control%d'%i,'Trim Finish',w*.17+i*w*.066,22,h-112,w*.195+i*w*.066,24,h-108)
        # Product markings are abbreviated to geometric keys; undimensioned text is not fabricated.
        for i in range(6):
            for side in (-1,1):
                x=side*(w*.09+i*0.5)
                self.box('Cycle Tick%d_%d'%(i,side),'Controls Finish',x-10,28,h-40-i*13,x+10,30,h-37-i*13)
        if washer:
            self.add(rounded_front(-w*.46,h-127,-w*.15,h-35,5,26,7),'Detergent Drawer','Cabinet Finish')
            self.box('Drawer Recess','Controls Finish',-w*.4,24,h-120,-w*.19,26,h-114)
            if c['brand']=='LG':
                self.add(rounded_front(-w*.4,45,-w*.15,155,5,38,7),'Drain Service Door','Cabinet Finish')
                self.box('Service Latch','Controls Finish',-w*.292,36,150,-w*.26,38,154)
        cz=h*(.54 if c['brand']=='GE' else .568); r=w*.442
        self.cylinder('Door Outer Trim','Trim Finish',(0,20,cz),r,14,(0,1,0),r-3.5)
        self.cylinder('Door Black Surround','Glass Finish',(0,8,cz),r-3.5,28,(0,1,0),r*.745)
        self.cylinder('Door Glass','Glass Finish',(0,0,cz),r*.745,15,(0,1,0))
        self.cylinder('Inner Door Lip','Controls Finish',(0,5,cz),r*.767,15,(0,1,0),r*.745)
        if c['brand']=='GE' and washer:
            self.cylinder('UltraFresh Metallic Door Ring','Trim Finish',(0,3,cz),r*.935,5,(0,1,0),r*.875)
            for i in range(70):
                angle=math.pi*(.03+.94*i/69)
                ux,uz=math.cos(angle),math.sin(angle)
                vx,vz=-uz,ux
                profile=[(ux*rr+vx*tt,1,cz+uz*rr+vz*tt) for rr,tt in [(r*.884,-1.1),(r*.928,-1.1),(r*.928,1.1),(r*.884,1.1)]]
                self.add(prism(profile,DB.XYZ.BasisY,2),'UltraFresh Vent %02d'%i,'Controls Finish')
        # The small hinge/pocket differences prevent an unsupported mirrored front assembly.
        hinge=-1 if washer else 1
        self.box('Door Hinge','Controls Finish',hinge*r-8,27,cz-52,hinge*r+8,43,cz+52)
        self.box('Door Pocket','Controls Finish',-hinge*r-5,12,cz-36,-hinge*r+5,24,cz+36)
        # Shallow drum detail behind the tinted front cover, never claimed as an engineering model.
        self.cylinder('Drum Back','Interior Finish',(0,16,cz),r*.7,20,(0,1,0))

    def cooktop(self):
        w,h,d=self.c['width'],self.c['height'],self.c['depth']
        self.box('Body','Metal Finish',-w/2+14,14,-46,w/2-14,d-14,0)
        self.box('Glass Plate','Glass Finish',-w/2,0,0,w/2,d,7)
        # Positions are proportioned from the manufacturer's top photograph, not mirrored.
        burners=[(-325,313,57,True),(-35,389,35,False),(264,389,44,False),(-94,178,51,False),(320,178,44,False)]
        for i,(x,y,r,wok) in enumerate(burners):
            self.cylinder('Burner Base%d'%i,'Metal Finish',(x,y,7),r+8,6)
            self.cylinder('Burner Crown%d'%i,'Grate Finish',(x,y,13),r,12)
            if wok:
                self.cylinder('Wok Ring','Grate Finish',(x,y,25),r+24,7,inner=r+14)
                self.cylinder('Wok Center','Metal Finish',(x,y,25),22,4)
            # Cast supports use eight radial spokes around each burner.
            for j in range(8):
                a=j*math.pi/4
                radial_start=r+5; radial_end=100 if not wok else 112
                u=(math.cos(a),math.sin(a)); v=(-u[1],u[0])
                p=[(x+u[0]*rr+v[0]*vv,y+u[1]*rr+v[1]*vv,28) for rr,vv in [(radial_start,-3),(radial_end,-3),(radial_end,3),(radial_start,3)]]
                self.add(prism(p,DB.XYZ.BasisZ,14),'Grate%d_%d'%(i,j),'Grate Finish')
        # Rectangular bridging rails are asymmetric around the left wok burner.
        for i,y in enumerate((111,246,328,456)):
            self.box('Right Grate Rail%d'%i,'Grate Finish',-180,y,28,420,y+6,39)
        for i,x in enumerate((-235,115,183,245,307)):
            self.cylinder('Knob Base%d'%i,'Metal Finish',(x,47,7),21,5)
            self.cylinder('Knob%d'%i,'Metal Finish',(x,47,12),17.5,20)
            self.box('Knob Index%d'%i,'Grate Finish',x-1.5,48,31,x+1.5,61,33)

    def hood(self):
        w,h,d=self.c['width'],self.c['height'],self.c['depth']
        self.box('Body Back','Metal Finish',-w/2,d-3,0,w/2,d,h)
        self.box('Body Front','Metal Finish',-w/2,0,0,w/2,3,h)
        self.box('Body Left','Metal Finish',-w/2,3,0,-w/2+3,d-3,h)
        self.box('Body Right','Metal Finish',w/2-3,3,0,w/2,d-3,h)
        top=box(-w/2,0,h-3,w/2,d,h)
        collar=cylinder((0,d/2,h-4),88.9,5)
        top=DB.BooleanOperationsUtils.ExecuteBooleanOperation(top,collar,DB.BooleanOperationsType.Difference)
        self.add(top,'Body Top','Metal Finish')
        self.cylinder('Duct Collar','Metal Finish',(0,d/2,h),88.9,25.4,inner=86.9)
        self.box('Bottom Front Flange','Metal Finish',-w/2,0,0,w/2,26,4)
        self.box('Bottom Rear Flange','Metal Finish',-w/2,d-15,0,w/2,d,4)
        for side in (-1,1):
            x0=-w/2+18 if side<0 else 7
            x1=-7 if side<0 else w/2-18
            self.box('Filter Recess%d'%side,'Dark Finish',x0,34,16,x1,d-20,18)
            self.box('Filter Front Rail%d'%side,'Metal Finish',x0,34,4,x1,40,14)
            self.box('Filter Rear Rail%d'%side,'Metal Finish',x0,d-27,4,x1,d-20,14)
            for j in range(14):
                x=x0+9+j*(x1-x0-18)/13
                self.box('Baffle%d_%d'%(side,j),'Metal Finish',x,40,5,x+4,d-27,15)
        self.cylinder('LED Trim','Metal Finish',(-w*.33,15,0),10,4)
        self.cylinder('LED Lens','Light Lens Finish',(-w*.33,15,0),7,2)
        for i in range(4):
            self.cylinder('Control%d'%i,'Dark Finish',(w*.18+i*16,15,0),4,2)

    def wine(self):
        w,h,d=self.c['width'],self.c['height'],self.c['depth']
        # Model the factory envelope only; the unselected customer overlay/pull is absent.
        self.box('Body Back','Cabinet Finish',-w/2,d-30,0,w/2,d,h)
        self.box('Body Left','Cabinet Finish',-w/2,30,0,-w/2+32,d-30,h)
        self.box('Body Right','Cabinet Finish',w/2-32,30,0,w/2,d-30,h)
        self.box('Body Top','Cabinet Finish',-w/2,30,h-35,w/2,d,h)
        self.box('Bottom Plinth','Cabinet Finish',-w/2,30,0,w/2,d,120)
        for i in range(45):
            x=-w*.43+i*w*.86/44
            self.box('Plinth Vent%d'%i,'Shelf Finish',x,25,30,x+3,30,98)
        for side in (-1,1):
            x0=-w/2+4 if side<0 else w/2-36
            self.box('Door Side%d'%side,'Panel Finish',x0,0,120,x0+32,30,h-3)
        self.box('Door Bottom','Panel Finish',-w/2+4,0,120,w/2-4,30,160)
        self.box('Door Top','Panel Finish',-w/2+4,0,h-43,w/2-4,30,h-3)
        self.box('Door Glass','Glass Finish',-w/2+36,9,160,w/2-36,14,h-43)
        self.box('Zone Divider','Cabinet Finish',-w/2+32,33,h*.57,w/2-32,d-30,h*.57+38)
        for zone in range(2):
            low,high=(145,h*.57-25) if zone==0 else (h*.57+65,h-68)
            for i in range(8):
                z=low+(high-low)*i/7
                for rod in range(15):
                    x=-w/2+46+rod*(w-92)/14
                    self.box('Shelf%d_%d Wire%d'%(zone,i,rod),'Interior Finish',x,47,z,x+3,d-40,z+3)
                self.box('Shelf%d_%d Rear Wire'%(zone,i),'Interior Finish',-w/2+43,d-44,z,w/2-43,d-40,z+4)
                self.box('Shelf Edge%d_%d'%(zone,i),'Shelf Finish',-w/2+43,42,z-2,w/2-43,49,z+10)
        self.box('Zone Display','Glass Finish',-65,28,h*.57+7,65,33,h*.57+31)

def build_one(slug,app):
    folder=os.path.join(ROOT,slug)
    config=json.load(open(os.path.join(folder,'source','geometry_config.json')))
    report={'slug':slug,'model':config['model'],'started_utc':str(datetime.datetime.utcnow()),'ok':False,'stage':'starting'}
    path=os.path.join(folder,'validation.json')
    doc=None; project=None; tx=None
    try:
        report['revit_version']=app.VersionNumber
        assert app.VersionNumber=='2025'
        rfa=os.path.join(folder,slug+'_R2025.rfa')
        if not os.path.isfile(rfa) or os.environ.get('APPLIANCE_FORCE_REBUILD')=='1':
            doc=app.NewFamilyDocument(TEMPLATE)
            tx=DB.Transaction(doc,'Build '+config['model'])
            tx.Start()
            doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_SpecialityEquipment)
            doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED).Set(1)
            p=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)
            if p and not p.IsReadOnly:
                p.Set(0)
            fm=doc.FamilyManager
            fm.NewType(config['model'])
            for name,value in [('Manufacturer',config['brand']),('Model',config['model']),('Description','1527 Wieland appliance visualization'),('URL',config['spec_url'])]:
                fp=fm.get_Parameter(name)
                if fp:
                    fm.Set(fp,value)
            for pname,value in [('Overall Width',config['width']),('Body Height',config['height']),('Overall Depth',config['depth'])]:
                fp=fm.AddParameter(pname,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False)
                fm.Set(fp,value/MM)
                fm.SetFormula(fp,str(value)+' mm')
            b=Builder(doc,app,config)
            getattr(b,'laundry' if config['kind'] in ('washer','dryer') else config['kind'])()
            doc.Regenerate()
            tx.Commit()
            report['parts']=b.parts
            report['stage']='geometry_built'
            write_json(path,report)
            options=DB.SaveAsOptions(); options.OverwriteExistingFile=True
            doc.SaveAs(rfa,options)
            doc.Close(False); doc=None
        else:
            report['reused_existing_build']=True
        doc=app.OpenDocumentFile(rfa)
        report.update(saved_rfa=rfa,reopened=True,saved_revit_format=DB.BasicFileInfo.Extract(rfa).Format,
                      category=doc.OwnerFamily.FamilyCategory.Name,placement_type=str(doc.OwnerFamily.FamilyPlacementType))
        fm=doc.FamilyManager
        elements=list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
        report['family_bounds']=measure(elements)
        report['dimension_basis']=config['dimension_basis']
        report['target_xyz_mm']=[config['width'],config['depth'],config['height']]
        measured=report['family_bounds']['xyz_size_mm']
        if config.get('dimension_scope')=='body':
            body=[e for e in elements if ename(e.Subcategory).startswith('Body') or ename(e.Subcategory)=='Glass Plate']
            report['body_bounds']=measure(body)
            measured=report['body_bounds']['xyz_size_mm']
        report['dimension_delta_mm']=[measured[i]-report['target_xyz_mm'][i] for i in range(3)]
        report['dimension_gate']=all(abs(x)<=1.0 for x in report['dimension_delta_mm'])
        report['dimension_gate_scope']=config.get('dimension_scope','overall')
        report['parameter_flex']=[]
        material_params=[p for p in fm.Parameters if p.Definition.GetDataType()==DB.SpecTypeId.Reference.Material and not p.IsReadOnly]
        for p in material_params:
            tx=DB.Transaction(doc,'Test '+p.Definition.Name); tx.Start()
            before=fm.CurrentType.AsElementId(p)
            test_mat=doc.GetElement(DB.Material.Create(doc,'QA '+p.Definition.Name))
            test_mat.Color=DB.Color(180,90,90)
            fm.Set(p,test_mat.Id); doc.Regenerate()
            bound=[]
            for e in elements:
                ep=e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM)
                associated=fm.GetAssociatedFamilyParameter(ep)
                if associated and associated.Id==p.Id:
                    bound.append(ep.AsElementId()==test_mat.Id)
            tested=bool(bound) and all(bound)
            tx.RollBack()
            report['parameter_flex'].append({'name':p.Definition.Name,'geometry_bindings':len(bound),'substitution_pass':tested,
                'restored':fm.CurrentType.AsElementId(p)==before})
        report['material_inventory']=[]
        for m in DB.FilteredElementCollector(doc).OfClass(DB.Material):
            if m.AppearanceAssetId==DB.ElementId.InvalidElementId:
                continue
            a=doc.GetElement(m.AppearanceAssetId).GetRenderingAsset()
            prop=a.FindByName('generic_diffuse')
            connected=prop.GetSingleConnectedAsset() if prop and prop.NumberOfConnectedProperties else None
            bitmap=connected.FindByName('unifiedbitmap_Bitmap').Value if connected else None
            report['material_inventory'].append({'name':ename(m),'appearance_id':int(m.AppearanceAssetId.Value),'bitmap':bitmap,'bitmap_exists':os.path.isfile(bitmap) if bitmap else False})
        report['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
        doc.Close(False); doc=None
        project,instance,placement=place_family(app,rfa)
        report['placement']=placement
        report['placed_bounds']=measure([instance])
        fwd=(-1,1.5,0.8) if config['kind']=='hood' else (-1,1.5,-0.8)
        report['previews']=export_view(project,os.path.join(folder,'views'),'oblique',report['placed_bounds'],fwd,instance.Category.Id)
        report['previews']+=export_view(project,os.path.join(folder,'views'),'front',report['placed_bounds'],(0,1,-0.025),instance.Category.Id)
        report['placed_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
        report['ok']=bool(report['dimension_gate'] and all(p['substitution_pass'] and p['restored'] for p in report['parameter_flex']) and placement['placed'])
        report['stage']='saved_reopened_measured_flexed_placed_previewed'
        report['limitations']=config['limitations']
        report['assumptions']=config['assumptions']
    except Exception:
        report['error']=traceback.format_exc()
        if tx:
            try:
                if tx.GetStatus()==DB.TransactionStatus.Started:
                    tx.RollBack()
            except Exception:
                pass
    finally:
        for opened in [doc,project]:
            if opened:
                try:
                    opened.Close(False)
                except Exception:
                    pass
        report['finished_utc']=str(datetime.datetime.utcnow())
        write_json(path,report)
    return report

if __name__=='__main__':
    models=json.load(open(os.path.join(ROOT,'custom_models.json')))
    selected=os.environ.get('APPLIANCE_CUSTOM_SLUGS','').split(',')
    results=[]
    for model in models:
        if selected!=[''] and model['slug'] not in selected:
            continue
        result=build_one(model['slug'],__revit__.Application)
        results.append(result)
        write_json(os.path.join(ROOT,'custom_build_results.json'),results)
