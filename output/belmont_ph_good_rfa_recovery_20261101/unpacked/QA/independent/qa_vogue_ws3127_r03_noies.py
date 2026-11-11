# -*- coding: utf-8 -*-
"""Independent native Revit 2025 QA for R03 preliminary non-IES model.
Source-only. Opens existing families read-only; NEVER saves Revit documents.
"""
from __future__ import print_function
import os, json, hashlib, traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
R02 = os.path.join(BASE,'candidates','ModernForms_Vogue_WS-3127_CH_R2025_R02.rfa')
R03 = os.path.join(BASE,'candidates','ModernForms_Vogue_WS-3127_CH_R2025_R03.rfa')
OUT = os.path.join(BASE,'qa','vogue_ws3127_r03_noies_independent_qa.json')
R02_SHA = 'e5d49df849079974e7e1e3e3718a898e7f9671d0ca03633f4dead35fc1c0d9b8'
PFX = 'PH GOOD '

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        while True:
            chunk=f.read(1048576)
            if not chunk:return h.hexdigest()
            h.update(chunk)

def inspect(doc):
    assert doc.IsFamilyDocument
    assert doc.OwnerFamily.FamilyCategory.Name == 'Lighting Fixtures'
    fm=doc.FamilyManager
    types=list(fm.Types)
    assert len(types)==1 and types[0].Name=='WS-3127-CH'
    lf=DB.Lighting.LightFamily.GetLightFamily(doc)
    assert lf.GetNumberOfLightTypes()==1
    lt=lf.GetLightType(0)
    dist=lt.GetLightDistribution()
    inten=lt.GetInitialIntensity()
    color=lt.GetInitialColor()
    assert isinstance(inten,DB.Lighting.InitialFluxIntensity)
    assert isinstance(color,DB.Lighting.CustomInitialColor)
    p=fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
    photoweb=types[0].AsString(p) if p else None
    names={}
    for m in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        if m.Name in ('PHGOOD_VOGUE_CH_CHROME','PHGOOD_VOGUE_MOUTH_BLOWN_OPAL'):
            names[str(m.Name)]={'color':[int(m.Color.Red),int(m.Color.Green),int(m.Color.Blue)],
                                'transparency':int(m.Transparency),
                                'appearance_id':str(m.AppearanceAssetId)}
    metadata={}
    for x in fm.Parameters:
        n=x.Definition.Name
        if n.startswith(PFX):
            v=None
            if str(x.StorageType)=='String':v=types[0].AsString(x)
            elif str(x.StorageType)=='Double':
                unit=None
                if n=='PH GOOD OEM Input Power':unit=DB.UnitTypeId.Watts
                if n=='PH GOOD OEM Delivered Flux':unit=DB.UnitTypeId.Lumens
                if n=='PH GOOD OEM Default CCT':unit=DB.UnitTypeId.Kelvin
                v=DB.UnitUtils.ConvertFromInternalUnits(types[0].AsDouble(x),unit) if unit else types[0].AsDouble(x)
            metadata[str(n)]=v
    connectors=[str(x.Id) for x in DB.FilteredElementCollector(doc).OfClass(DB.ConnectorElement)]
    return {'light_distribution_style':str(lf.GetLightDistributionStyle()),
            'distribution_class':str(dist.GetType().Name),
            'distribution_ies':str(dist.PhotometricWebFile) if isinstance(dist,DB.Lighting.PhotometricWebLightDistribution) else None,
            'family_type_ies':photoweb,
            'source_flux_lumens':float(inten.Flux),
            'source_cct_kelvin':float(color.Temperature),
            'connector_count':len(connectors),'connector_ids':connectors,
            'materials':names,'type_metadata':metadata,
            'warnings':[str(x.GetDescriptionText()) for x in doc.GetWarnings()]}

def main():
    assert str(__revit__.Application.VersionNumber)=='2025'
    assert os.path.isfile(R02) and sha(R02)==R02_SHA
    assert os.path.isfile(R03), 'R03 does not exist; do not claim validation'
    assert not os.path.lexists(OUT), 'QA receipt already exists'
    results=[]
    for path in (R02,R03):
        doc=__revit__.Application.OpenDocumentFile(path)
        try:
            data=inspect(doc)
            data['path']=path
            data['sha256']=sha(path)
            results.append(data)
        finally:
            doc.Close(False)
    baseline,actual=results
    expected={
       'PH GOOD OEM Input Power':40.6,
       'PH GOOD OEM Delivered Flux':2993.0,
       'PH GOOD OEM Default CCT':3000.0}
    checks={
      'R02_still_historical_web':'PhotometricWeb' in baseline['light_distribution_style'],
      'R03_generic_no_ies':('Spherical' in actual['light_distribution_style']
                            and actual['distribution_class']=='SphericalLightDistribution'
                            and actual['distribution_ies'] is None
                            and not actual['family_type_ies']),
      'R03_initial_flux':abs(actual['source_flux_lumens']-2993)<0.001,
      'R03_CCT':abs(actual['source_cct_kelvin']-3000)<0.001,
      'OEM_numeric_types':all(abs(float(actual['type_metadata'].get(k,-9999))-v)<0.001
                              for k,v in expected.items()),
      'status_disclosure':('GENERIC SPHERICAL' in str(actual['type_metadata'].get(
                         'PH GOOD Photometric Status',''))),
      'no_connector':baseline['connector_count']==actual['connector_count']==0,
      'visual_materials_preserved':baseline['materials']==actual['materials'],
      'no_new_warnings':baseline['warnings']==actual['warnings']}
    passed=all(checks.values())
    report={'status':'PASS_PRELIMINARY_NON_OEM_DISTRIBUTION' if passed else 'FAIL',
            'quality_class':'VISUALIZATION_PRELIMINARY_NON_OEM_DISTRIBUTION',
            'manufacturer_ies_matched':False,'lighting_calc_release':False,
            'electrical_circuit_release':False,'checks':checks,
            'R02':baseline,'R03':actual}
    fd=os.open(OUT,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o666)
    with os.fdopen(fd,'w') as f:json.dump(report,f,indent=2,sort_keys=True,ensure_ascii=True)
    print('INDEPENDENT_VOGUE_R03_'+('PASS_PRELIMINARY' if passed else 'FAIL'))
    if not passed:raise RuntimeError('R03 independent QA failure; inspect '+OUT)

if __name__=='__main__':
    try:main()
    except Exception:
        print('VOGUE_R03_QA_ERROR '+traceback.format_exc())
        raise
