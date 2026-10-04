# -*- coding: utf-8 -*-
"""Upgrade and validate manufacturer RFAs; preserve source geometry and report fit holds."""
import os
import sys
import json
import traceback
import datetime
import struct
import zlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from family_common import *

def png(path,rgb):
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    pixel=''.join(chr(v) for v in rgb)
    raw=('\x00'+pixel*8)*8
    data='\x89PNG\r\n\x1a\n'+chunk('IHDR',struct.pack('>IIBBBBB',8,8,8,2,0,0,0))+chunk('IDAT',zlib.compress(raw))+chunk('IEND','')
    with open(path,'wb') as handle:
        handle.write(data)

def repair_appearances(doc,app,folder):
    repaired=[]
    for mat in list(DB.FilteredElementCollector(doc).OfClass(DB.Material)):
        if mat.AppearanceAssetId!=DB.ElementId.InvalidElementId:
            continue
        rgb=[int(mat.Color.Red),int(mat.Color.Green),int(mat.Color.Blue)]
        path=os.path.join(folder,'source','imported_material_%d.png'%mat.Id.Value)
        png(path,rgb)
        made=material(doc,app,'Wieland appearance '+str(mat.Id.Value),rgb,0.35,mat.Transparency/100.0,path)
        mat.AppearanceAssetId=made.AppearanceAssetId
        doc.Delete(made.Id)
        repaired.append({'material':ename(mat),'bitmap':path})
    return repaired

def validate(config,app):
    folder=os.path.join(ROOT,config['slug'])
    output=os.path.join(folder,config['slug']+'_R2025.rfa')
    validation=os.path.join(folder,'validation.json')
    r=dict(config,started_utc=str(datetime.datetime.utcnow()),stage='starting',ok=False,status='DOWNLOADED')
    write_json(validation,r)
    doc=None; project=None; tx=None
    try:
        originals=[]
        for parent,dirs,files in os.walk(os.path.join(folder,'source','original')):
            originals.extend(os.path.join(parent,n) for n in files if n.lower().endswith('.rfa') and '2d' not in n.lower())
        originals.sort(key=lambda p:('-3d.rfa' not in p.lower(),len(p)))
        if not originals:
            raise RuntimeError('No manufacturer RFA extracted')
        r['manufacturer_original']=originals[0]
        source=output if os.path.isfile(output) else originals[0]
        doc=app.OpenDocumentFile(source)
        r['source_revit_format']=DB.BasicFileInfo.Extract(source).Format
        r['original_category']=doc.OwnerFamily.FamilyCategory.Name
        tx=DB.Transaction(doc,'Prepare appliance category and appearances');tx.Start()
        doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_SpecialityEquipment)
        flag=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED)
        if flag and not flag.IsReadOnly:
            flag.Set(1)
        flag=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)
        if flag and not flag.IsReadOnly:
            flag.Set(0)
        fm=doc.FamilyManager
        if not fm.CurrentType:
            choices=list(fm.Types)
            if choices:
                fm.CurrentType=next((t for t in choices if t.Name.strip()),choices[0])
            else:
                fm.NewType(config['model'])
        r['appearance_repairs']=repair_appearances(doc,app,folder)
        doc.Regenerate();tx.Commit()
        options=DB.SaveAsOptions();options.OverwriteExistingFile=True
        if os.path.normcase(doc.PathName)==os.path.normcase(output):
            doc.Save()
        else:
            doc.SaveAs(output,options)
        doc.Close(False);doc=None
        doc=app.OpenDocumentFile(output)
        r.update(reopened=True,saved_rfa=output,saved_revit_format=DB.BasicFileInfo.Extract(output).Format,
                 category=doc.OwnerFamily.FamilyCategory.Name,placement_type=str(doc.OwnerFamily.FamilyPlacementType),stage='reopened')
        write_json(validation,r)
        fm=doc.FamilyManager
        elements=list(DB.FilteredElementCollector(doc).WhereElementIsNotElementType())
        r['family_bounds']=measure(elements)
        r['parameter_flex']=[]
        r['material_parameters']=[]
        for p in fm.Parameters:
            if p.IsReadOnly or p.Formula or p.Definition.GetDataType()!=DB.SpecTypeId.Reference.Material:
                continue
            rec={'name':p.Definition.Name,'pass':False}
            tx=DB.Transaction(doc,'Flex manufacturer material '+p.Definition.Name)
            try:
                tx.Start()
                old=fm.CurrentType.AsElementId(p)
                test=doc.GetElement(DB.Material.Create(doc,'QA appliance '+str(p.Id.Value)))
                fm.Set(p,test.Id);doc.Regenerate()
                count=0
                for e in elements:
                    try:
                        if test.Id in list(e.GetMaterialIds(False)):
                            count+=1
                    except Exception:
                        pass
                rec.update(changed_parameter=fm.CurrentType.AsElementId(p)==test.Id,material_element_references=count)
                tx.RollBack()
                rec['restored']=fm.CurrentType.AsElementId(p)==old
                rec['pass']=bool(rec['changed_parameter'] and rec['restored'] and count)
            except Exception:
                if tx.GetStatus()==DB.TransactionStatus.Started:
                    tx.RollBack()
                rec['error']=traceback.format_exc()
            r['parameter_flex'].append(rec)
            r['material_parameters'].append(p.Definition.Name)
        r['material_inventory']=[{'name':ename(m),'appearance_id':str(m.AppearanceAssetId),
                                  'rgb':[int(m.Color.Red),int(m.Color.Green),int(m.Color.Blue)]}
                                 for m in DB.FilteredElementCollector(doc).OfClass(DB.Material)]
        r['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
        doc.Close(False);doc=None
        project,instance,placement=place_family(app,output)
        r['placement']=placement
        r['placed_bounds']=measure([instance])
        measured=r['placed_bounds']['xyz_size_mm']
        r['dimension_delta_mm']=[measured[i]-config['target_xyz_mm'][i] for i in range(3)]
        r['dimension_gate']=all(abs(d)<=1.0 for d in r['dimension_delta_mm'])
        r['dimension_gate_scope']='full native geometry versus published appliance envelope'
        r['previews']=export_view(project,os.path.join(folder,'views'),'placed_oblique',r['placed_bounds'],(-1,1.5,-0.65),instance.Category.Id)
        r['placed_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
        r['ok']=True
        r['all_acceptance_gates_pass']=bool(r['dimension_gate'] and r['parameter_flex'] and all(p['pass'] for p in r['parameter_flex']))
        r['limitations']=[]
        if not r['dimension_gate']:
            r['limitations'].append('Full native geometry differs by more than 1 mm from at least one published envelope dimension. Do not treat as dimensional acceptance; compare handles, flanges, panels, feet and original source geometry.')
        if not r['parameter_flex'] or not all(p['pass'] for p in r['parameter_flex']):
            r['limitations'].append('Some manufacturer materials are fixed/nested/imported or lack a confirmed top-level geometry binding; editable-material acceptance is limited.')
        r['stage']='saved_reopened_measured_flexed_placed_previewed'
    except Exception:
        r['error']=traceback.format_exc()
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
        r['finished_utc']=str(datetime.datetime.utcnow())
        write_json(validation,r)
    return r

app=__revit__.Application
results=[]
chosen=os.environ.get('APPLIANCE_DOWNLOADED_SLUGS','').split(',')
for config in json.load(open(os.path.join(ROOT,'downloaded_models.json'))):
    if chosen!=[''] and config['slug'] not in chosen:
        continue
    results.append(validate(config,app))
    write_json(os.path.join(ROOT,'downloaded_validation_results.json'),results)
