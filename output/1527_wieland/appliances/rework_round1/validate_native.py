# -*- coding: utf-8 -*-
"""Validate new appliance RFAs in a separate serialized Revit invocation."""
import os
import sys
import json
import datetime
import traceback
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(HERE)
sys.path.insert(0,ROOT)
from family_common import *

def family_material_tests(doc,v):
    fm=doc.FamilyManager
    forms=list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    parameters=[p for p in fm.Parameters if p.Definition.GetDataType()==DB.SpecTypeId.Reference.Material and not p.IsReadOnly and not p.Formula]
    v['parameter_flex']=[]
    v['material_inventory']=[]
    for p in parameters:
        old=fm.CurrentType.AsElementId(p)
        tx=DB.Transaction(doc,'Verify finish '+p.Definition.Name)
        try:
            tx.Start()
            test=doc.GetElement(DB.Material.Create(doc,'R1 test '+p.Definition.Name))
            fm.Set(p,test.Id)
            doc.Regenerate()
            ids=[]
            passes=[]
            for e in forms:
                ep=e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM)
                assoc=fm.GetAssociatedFamilyParameter(ep)
                if assoc and assoc.Id==p.Id:
                    ids.append(int(e.Id.Value))
                    passes.append(ep.AsElementId()==test.Id and test.Id in list(e.GetMaterialIds(False)))
            tx.RollBack()
            v['parameter_flex'].append({'name':p.Definition.Name,'geometry_bindings':len(ids),'bound_element_ids':ids,
                 'substitution_pass':bool(passes) and all(passes),'restored':fm.CurrentType.AsElementId(p)==old})
        finally:
            if tx.GetStatus()==DB.TransactionStatus.Started:tx.RollBack()
        m=doc.GetElement(old)
        appearance=doc.GetElement(m.AppearanceAssetId)
        asset=appearance.GetRenderingAsset() if appearance else None
        diffuse=asset.FindByName('generic_diffuse') if asset else None
        linked=diffuse.GetSingleConnectedAsset() if diffuse and diffuse.NumberOfConnectedProperties else None
        bp=linked.FindByName('unifiedbitmap_Bitmap') if linked else None
        bitmap=bp.Value if bp else None
        v['material_inventory'].append({'name':ename(m),'appearance_id':int(m.AppearanceAssetId.Value),
              'bitmap':bitmap,'bitmap_exists':bool(bitmap and os.path.isfile(bitmap))})

def placed_material_tests(project,inst,v):
    v['placed_material_flex']=[]
    for rec in v['parameter_flex']:
        name=rec['name']
        symbol=project.GetElement(inst.GetTypeId())
        p=symbol.LookupParameter(name)
        old=p.AsElementId()
        tx=DB.Transaction(project,'Placed finish test '+name)
        try:
            tx.Start()
            test=project.GetElement(DB.Material.Create(project,'Placed R1 '+name))
            p.Set(test.Id)
            project.Regenerate()
            has_test=test.Id in list(inst.GetMaterialIds(False))
            tx.RollBack()
            restored=project.GetElement(inst.GetTypeId()).LookupParameter(name).AsElementId()==old
            v['placed_material_flex'].append({'name':name,'substitution_pass':has_test,'restored':restored})
        finally:
            if tx.GetStatus()==DB.TransactionStatus.Started:tx.RollBack()

def validate(c,app):
    slug=c['slug']
    folder=os.path.join(ROOT,slug)
    rfa=os.path.join(folder,c['rfa_name'])
    checkpoint=os.path.join(folder,'source','rework_r1','validation.json')
    v={'slug':slug,'model':c['model'],'status':'BUILT_WITH_LIMITATIONS',
       'build_method':'native_custom_new_family','revision':'Custom_R1',
       'started_utc':str(datetime.datetime.utcnow()),'ok':False,'stage':'starting',
       'target_xyz_mm':c['target_xyz_mm'],'dimension_basis':c['dimension_basis'],
       'dimension_gate_scope':'overall','axis_convention':c['axis_convention'],
       'limitations':c['declared_limitations'],'replacement_reason':c['replacement_reason']}
    doc=None
    project=None
    try:
        assert app.VersionNumber=='2025'
        v['revit_version']=app.VersionNumber
        doc=app.OpenDocumentFile(rfa)
        v.update(reopened=True,saved_rfa=rfa,saved_revit_format=DB.BasicFileInfo.Extract(rfa).Format,
                 category=doc.OwnerFamily.FamilyCategory.Name,placement_type=str(doc.OwnerFamily.FamilyPlacementType))
        expected_category=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_SpecialityEquipment)
        v['category_gate']=doc.OwnerFamily.FamilyCategory.Id==expected_category.Id
        v['native_freeform_count']=DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement).GetElementCount()
        v['import_instance_count']=DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance).GetElementCount()
        v['nested_instance_count']=DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance).GetElementCount()
        v['family_bounds']=measure(list(DB.FilteredElementCollector(doc).WhereElementIsNotElementType()))
        v['family_dimension_delta_mm']=[v['family_bounds']['xyz_size_mm'][i]-c['target_xyz_mm'][i] for i in range(3)]
        fm=doc.FamilyManager
        v['identity']={}
        for name in ['Manufacturer','Model','Description']:
            p=fm.get_Parameter(name)
            v['identity'][name]=fm.CurrentType.AsString(p) if p else None
        v['identity_gate']=v['identity']['Model']==c['model'] and v['identity']['Manufacturer']==c['brand']
        v['fixed_dimension_parameters']=[]
        for name,value in zip(['Overall Width','Overall Depth','Overall Height'],c['target_xyz_mm']):
            p=fm.get_Parameter(name)
            actual=fm.CurrentType.AsDouble(p)*304.8
            v['fixed_dimension_parameters'].append({'name':name,'formula':p.Formula,'value_mm':actual,'matches_reference':abs(actual-value)<0.001})
        family_material_tests(doc,v)
        v['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
        v['stage']='reopened_measured_materials_flexed'
        write_json(checkpoint,v)
        doc.Close(False)
        doc=None
        project,inst,placement=place_family(app,rfa)
        v['placement']=placement
        v['placed_bounds']=measure([inst])
        actual=v['placed_bounds']['xyz_size_mm']
        v['dimension_delta_mm']=[actual[i]-c['target_xyz_mm'][i] for i in range(3)]
        v['dimension_gate']=all(abs(x)<=1 for x in v['dimension_delta_mm']+v['family_dimension_delta_mm'])
        v['measurement_scope']='All physical geometry in the complete reopened family and floor-face placed instance. No part or projection filter; no auxiliary bounding object.'
        placed_material_tests(project,inst,v)
        t=inst.GetTransform()
        v['placement_transform']={'origin_mm':[t.Origin.X*304.8,t.Origin.Y*304.8,t.Origin.Z*304.8],
                                  'basis_x':[t.BasisX.X,t.BasisX.Y,t.BasisX.Z],
                                  'basis_y':[t.BasisY.X,t.BasisY.Y,t.BasisY.Z],
                                  'basis_z':[t.BasisZ.X,t.BasisZ.Y,t.BasisZ.Z]}
        views=os.path.join(folder,'views','rework_r1')
        v['previews']=export_view(project,views,'oblique',v['placed_bounds'],(-1,1.6,-0.8),inst.Category.Id)
        v['previews']+=export_view(project,views,'front',v['placed_bounds'],(0,1,-0.01),inst.Category.Id)
        v['previews']+=export_view(project,views,'side',v['placed_bounds'],(1,0,-0.01),inst.Category.Id)
        v['placed_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
        v['material_gate']=bool(v['parameter_flex']) and all(x['substitution_pass'] and x['restored'] for x in v['parameter_flex']+v['placed_material_flex'])
        v['bitmap_gate']=bool(v['material_inventory']) and all(m['bitmap_exists'] for m in v['material_inventory'])
        gates=[v['dimension_gate'],v['category_gate'],v['identity_gate'],v['material_gate'],v['bitmap_gate'],
               placement['placed'],len(v['previews'])>=3,not v['warnings'],not v['placed_warnings'],
               v['import_instance_count']==0,v['nested_instance_count']==0]
        v['native_gates_pass']=all(gates)
        v['ok']=v['native_gates_pass']
        v['all_acceptance_gates_pass']=False
        v['visual_review_pending']=True
        v['stage']='saved_reopened_measured_flexed_placed_previewed'
    except Exception:
        v['error']=traceback.format_exc()
    finally:
        for d in [doc,project]:
            if d:
                try:d.Close(False)
                except Exception:pass
        v['finished_utc']=str(datetime.datetime.utcnow())
        write_json(checkpoint,v)
    return v

if __name__=='__main__':
    chosen=os.environ.get('APPLIANCE_R1_SLUGS','').split(',')
    all_results=[]
    for c in json.load(open(os.path.join(HERE,'configs.json'))):
        if chosen!=[''] and c['slug'] not in chosen:continue
        all_results.append(validate(c,__revit__.Application))
        write_json(os.path.join(HERE,'native_validation_results.json'),all_results)
