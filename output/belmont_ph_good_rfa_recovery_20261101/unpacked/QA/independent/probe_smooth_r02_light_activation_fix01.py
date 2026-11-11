# -*- coding: utf-8 -*-
"""Read-only native R02 Smooth emitter flag diagnosis. No transactions/SaveAs.

Use this BEFORE attempting to repair BLOCK_LIGHT_FLAG_UNAVAILABLE_OR_ALREADY_ACTIVE.
"""
from __future__ import print_function
import os, json, hashlib
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SOURCE=os.path.join(BASE,'candidates',
 'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R02_PARTIAL_UNAPPROVED.rfa')
REPORT=os.path.join(BASE,'qa','smooth_sbmb_r02_light_activation_probe_fix01.json')
SOURCE_SHA='f1741c711a07a26101c550b580a2db6be99bc4d3689cb75104eaafb0834379db'

def digest(filename):
    h=hashlib.sha256()
    with open(filename,'rb') as f:
        while True:
            b=f.read(1048576)
            if not b:break
            h.update(b)
    return h.hexdigest()

def value(parameter):
    if parameter is None:return {'present':False}
    result={'present':True,'read_only':bool(parameter.IsReadOnly),
            'storage':str(parameter.StorageType),
            'name':str(parameter.Definition.Name)}
    try:
        result['value']={'String':parameter.AsString,'Integer':parameter.AsInteger,
                         'Double':parameter.AsDouble,'ElementId':parameter.AsElementId
                        }[result['storage']]()
        if result['storage']=='ElementId':result['value']=str(result['value'])
    except Exception as exc:
        result['read_error']=type(exc).__name__
    return result

def main():
    app=__revit__.Application
    assert str(app.VersionNumber)=='2025'
    assert os.path.isfile(SOURCE) and digest(SOURCE)==SOURCE_SHA
    assert not os.path.lexists(REPORT)
    d=app.OpenDocumentFile(SOURCE)
    try:
        lf=DB.Lighting.LightFamily.GetLightFamily(d)
        flag=d.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE)
        source_ids=[str(e.Id) for e in DB.FilteredElementCollector(d).OfCategory(
              DB.BuiltInCategory.OST_LightingFixtureSource)]
        data={'status':'READ_ONLY_NATIVE_R02_FLAG_PROBE','source_sha':SOURCE_SHA,
              'family_category':str(d.OwnerFamily.FamilyCategory.Name),
              'placement':str(d.OwnerFamily.FamilyPlacementType),
              'owner_FBX_ASSET_TYPE':value(flag),
              'light_family_created':lf is not None,
              'native_light_types':int(lf.GetNumberOfLightTypes()) if lf else None,
              'light_source_elements':source_ids,
              'light_source_element_flags':[],'warnings':
              [str(w.GetDescriptionText()) for w in d.GetWarnings()]}
        for el in DB.FilteredElementCollector(d).OfCategory(
             DB.BuiltInCategory.OST_LightingFixtureSource):
            data['light_source_element_flags'].append({
               'id':str(el.Id),'element_class':str(el.GetType().FullName),
               'built_in_asset_type':value(el.get_Parameter(
                      DB.BuiltInParameter.FBX_ASSET_TYPE)),
               'parameters':[{'name':str(p.Definition.Name),
                              'storage':str(p.StorageType),'read_only':bool(p.IsReadOnly)}
                             for p in el.Parameters]})
    finally:d.Close(False)
    assert digest(SOURCE)==SOURCE_SHA
    fd=os.open(REPORT,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o666)
    with os.fdopen(fd,'w') as stream:json.dump(data,stream,indent=2,sort_keys=True)
    print('SMOOTH_R02_FLAG_PROBE',data['owner_FBX_ASSET_TYPE'],
          'light_types',data['native_light_types'])

main()
