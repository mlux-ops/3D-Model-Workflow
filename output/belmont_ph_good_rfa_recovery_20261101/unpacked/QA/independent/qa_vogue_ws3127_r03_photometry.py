# -*- coding: utf-8 -*-
"""READ-ONLY native 2025 Vogue R02/R03 photometric and electrical probe.
No family SaveAs, no transaction, no Revit project creation.
"""
from __future__ import print_function
import os, json, hashlib, traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
R02 = os.path.join(BASE, 'candidates', 'ModernForms_Vogue_WS-3127_CH_R2025_R02.rfa')
R03 = os.path.join(BASE, 'candidates', 'ModernForms_Vogue_WS-3127_CH_R2025_R03.rfa')
OUT = os.path.join(BASE, 'qa', 'vogue_ws3127_r03_photometry_qa.json')
R02_SHA = 'e5d49df849079974e7e1e3e3718a898e7f9671d0ca03633f4dead35fc1c0d9b8'

def digest(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        while True:
            data = f.read(1024 * 1024)
            if not data: return h.hexdigest()
            h.update(data)

def read(doc):
    if not doc.IsFamilyDocument or doc.OwnerFamily.FamilyCategory.Name != 'Lighting Fixtures':
        raise RuntimeError('Expected Lighting Fixtures family')
    fm = doc.FamilyManager
    types = list(fm.Types)
    if len(types) != 1 or str(types[0].Name) != 'WS-3127-CH':
        raise RuntimeError('Expected one WS-3127-CH type')
    t = types[0]
    bips = [
        DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE,
        DB.BuiltInParameter.FBX_LIGHT_LIMUNOUS_FLUX,
        DB.BuiltInParameter.FBX_LIGHT_INITIAL_COLOR_TEMPERATURE,
        DB.BuiltInParameter.RBS_ELEC_APPARENT_LOAD,
    ]
    params = {}
    for bip in bips:
        p = fm.get_Parameter(bip)
        k = str(bip)
        if p is None:
            params[k] = {'present':False}
            continue
        st = str(p.StorageType)
        try:
            value = {'String':t.AsString,'Double':t.AsDouble,
                     'Integer':t.AsInteger,'ElementId':t.AsElementId}[st](p)
            if st == 'ElementId': value = str(value)
        except Exception as exc:
            value = None
        params[k] = {'present':True,'storage':st,'value':value}
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    light = []
    if lf is not None:
        for i in range(lf.GetNumberOfLightTypes()):
            lt = lf.GetLightType(i)
            dist = lt.GetLightDistribution()
            desc = {'type_name':str(lf.GetLightTypeName(i)),
                    'distribution_class':str(dist.GetType().FullName)}
            if isinstance(dist, DB.Lighting.PhotometricWebLightDistribution):
                desc['ies_file'] = str(dist.PhotometricWebFile)
                desc['tilt_radians'] = float(dist.TiltAngle)
            try:
                intensity = lt.GetInitialIntensity()
                desc['initial_intensity_class'] = str(intensity.GetType().FullName)
                for key in ('Flux','Wattage','Efficacy','LuminousIntensity'):
                    if hasattr(intensity,key):
                        desc[key] = float(getattr(intensity,key))
            except Exception as exc:
                desc['intensity_probe_error'] = type(exc).__name__
            try:
                color = lt.GetInitialColor()
                desc['initial_color_class'] = str(color.GetType().FullName)
                if hasattr(color,'Temperature'):
                    desc['temperature_kelvin'] = float(color.Temperature)
            except Exception as exc:
                desc['color_probe_error'] = type(exc).__name__
            light.append(desc)
    connectors = []
    for element in DB.FilteredElementCollector(doc).OfClass(DB.ConnectorElement):
        connectors.append({'id':str(element.Id),
                           'type':str(element.GetType().Name)})
    materials = {}
    for mat in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        if mat.Name in ('PHGOOD_VOGUE_CH_CHROME',
                        'PHGOOD_VOGUE_MOUTH_BLOWN_OPAL'):
            materials[str(mat.Name)] = {
                'transparency':int(mat.Transparency),
                'color':[mat.Color.Red,mat.Color.Green,mat.Color.Blue],
                'appearance_id':str(mat.AppearanceAssetId)}
    return {'type_parameters':params,'light_source':light,
            'connector_count':len(connectors),'connectors':connectors,
            'materials':materials,
            'warnings':[w.GetDescriptionText() for w in doc.GetWarnings()]}

def main():
    if str(__revit__.Application.VersionNumber) != '2025':
        raise RuntimeError('Revit 2025 required')
    if not os.path.isfile(R02) or digest(R02) != R02_SHA:
        raise RuntimeError('R02 source SHA changed or missing')
    if os.path.lexists(OUT):
        raise RuntimeError('Prior QA receipt exists; no overwrite allowed')
    entries=[]
    for path in (R02,R03):
        if not os.path.isfile(path):
            entries.append({'path':path,'status':'NOT_BUILT'})
            continue
        doc = __revit__.Application.OpenDocumentFile(path)
        try:
            data = read(doc)
            data.update({'path':path,'sha256':digest(path),'status':'READ_ONLY_INSPECTED'})
            entries.append(data)
        finally:
            doc.Close(False)
    report={'scope':'READ_ONLY Native Revit 2025 R02/R03 emitter and electrical audit',
            'expected_current_watts':40.6,'expected_delivered_lumens':2993,
            'expected_default_cct_kelvin':3000,'actual':entries,
            'release_status':'HOLD until verified current IES, connector and wattage semantics'}
    fd=os.open(OUT,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o666)
    with os.fdopen(fd,'w') as f:
        json.dump(report,f,indent=2,sort_keys=True)
    print('VOGUE_NATIVE_QA_WRITTEN: '+OUT)

if __name__=='__main__':
    try: main()
    except Exception:
        print('VOGUE_NATIVE_QA_FAILED: '+traceback.format_exc())
        raise
