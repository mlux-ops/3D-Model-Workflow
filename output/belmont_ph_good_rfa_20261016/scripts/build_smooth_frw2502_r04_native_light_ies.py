# -*- coding: utf-8 -*-
"""Native Revit 2025 Smooth FR-W2502-52L R04 light-source activation and IES.

SOURCE ONLY. Prime executes in isolated IronPython 2.7 / pyRevit 2025.
Starts from exact source-hash-guarded OEM-derived R02. Creates a NEW R04
only after a real LightFamily.GetLightType(0), official IES assignment,
unchanged physical geometry/finishes and native SaveAs/reopen verification.

The earlier R03 photometry-only attempt FAILED because the R02 family had
zero active LightTypes. This explicitly tests the Hinkley-proven owner-family
Light Source flag before trying to bind manufacturer photometry.
No other source family, purchased RVT or Revit open document is edited.
"""
from __future__ import print_function
import hashlib
import json
import math
import os
import sys
import time
import traceback
import uuid

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SOURCE = os.path.join(BASE, 'candidates',
    'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R02_PARTIAL_UNAPPROVED.rfa')
IES = os.path.join(BASE, 'sources', 'photometry', 'FR-W2502-52L.IES')
VALIDATION = os.path.join(BASE, 'qa',
    'smooth_frw2502_ies_source_validation_20261016.json')
R02_QA = os.path.join(BASE, 'qa', 'smooth_sbmb_r02_native_qa.json')
TARGET = os.path.join(BASE, 'candidates',
    'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R04_NATIVE_LIGHT_IES_UNAPPROVED.rfa')
RECEIPT = os.path.join(BASE, 'qa', 'smooth_sbmb_r04_native_light_ies_receipt.json')

SOURCE_SHA = 'f1741c711a07a26101c550b580a2db6be99bc4d3689cb75104eaafb0834379db'
IES_SHA = '6044dda98294020d03decd14ad118be2717845536597d1ca9bb9cc296fdcda8e'
VALIDATION_SHA = 'b9d8836a641a1c4e6b912d5aabe36f7d738110a389e615f61e9f38c2c3b7c622'
R02_QA_SHA = '2ea2921f50d0bff745f5693c1e3a3eb6be1e79af3ed2d8462e2e03f2248b0d08'
IES_ARCHIVE_URL = 'https://modernforms.com/images/products/IES_FILES/FR-W2502-52_IES.zip'
OEM_SPEC = 'https://modernforms.com/images/products/SPECSHEET_PDF/FR-W2502_SPSHT.pdf'
IES_NAME = 'FR-W2502-52L.IES'
IES_FLUX = 707.09
IES_TEST_WATTS = 16.7549
OEM_LED_WATTS = 16.0
CCT = 3000.0
EXPECTED_RADIAL_SWEEP_MM = 1321.6925205853231
EXPECTED_FACE_COUNTS = {
    2997:140, 2998:140, 2999:140, 3000:97,
    3038:52, 3039:20, 3040:22, 3041:29, 3042:103}
EXPECTED_IMPORTS = (2977,2980,2982,2985,2986,2987,2988,
                    2989,2990,2991,2992,2993,2994)
EXPECTED_BLADES = (2997,2998,2999)
EXPECTED_LIGHT_LENS = 3000
BLACK_MAT = 'PH GOOD Smooth MB ABS Blades R02 Provisional'
BRASS_MAT = 'PH GOOD Smooth SB Housing R02 Provisional'
LIGHT_SOURCE_CATEGORY = DB.BuiltInCategory.OST_LightingFixtureSource


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            chunk = stream.read(1024*1024)
            if not chunk:
                return h.hexdigest()
            h.update(chunk)


def eid(value):
    try:
        return int(value.Value)
    except Exception:
        return int(value.IntegerValue)


def name(value):
    try:
        return unicode(DB.Element.Name.GetValue(value))
    except Exception:
        return unicode(value.Name)


def basename(value):
    return os.path.basename(unicode(value or '').replace('\\', '/')).lower()


def warning_text(doc):
    return sorted(unicode(w.GetDescriptionText()) for w in doc.GetWarnings())


def bbox(element):
    bb = element.get_BoundingBox(None)
    require(bb is not None, 'Protected model element missing BoundingBox')
    return [round(float(v),8) for v in (
        bb.Min.X,bb.Min.Y,bb.Min.Z,bb.Max.X,bb.Max.Y,bb.Max.Z)]


def protected(doc):
    """Hash-like semantic fingerprint; intentionally excludes light emitter."""
    geom = []
    for cls in (DB.FreeFormElement, DB.ImportInstance, DB.FamilyInstance):
        for item in DB.FilteredElementCollector(doc).OfClass(cls):
            # Light Source element is DB.Element, not physical OEM geometry.
            cat = name(item.Category) if item.Category else ''
            require(cat.lower() != 'light source',
                    'Unexpected source represented as protected physical geometry')
            geom.append([eid(item.Id), unicode(cls.Name), bbox(item),
                         sorted(eid(v) for v in item.GetMaterialIds(False))])
    materials = []
    for item in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        c = item.Color
        materials.append([eid(item.Id), name(item),
                          [int(c.Red),int(c.Green),int(c.Blue)],
                          int(item.Transparency),eid(item.AppearanceAssetId)])
    fm = doc.FamilyManager
    return {'elements':sorted(geom,key=lambda a:a[0]),
            'materials':sorted(materials,key=lambda a:a[0]),
            'placement':str(doc.OwnerFamily.FamilyPlacementType),
            'types':sorted(name(t) for t in fm.Types)}


def known_parts(doc, baseline_qa):
    freeforms = [e for e in DB.FilteredElementCollector(doc).OfClass(
        DB.FreeFormElement)]
    by_id = dict((eid(e.Id), e) for e in freeforms)
    require(all(x in by_id for x in EXPECTED_FACE_COUNTS),
            'Expected original nine FreeFormElements absent')
    actual_imports = sorted(eid(e.Id) for e in
        DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance))
    require(actual_imports == list(EXPECTED_IMPORTS),
            'OEM imported CAD instance IDs changed')
    mappings = baseline_qa['material']['finish_face_mapping']
    for item_id, count in EXPECTED_FACE_COUNTS.items():
        require(str(item_id) in mappings and
                sum(int(v) for v in mappings[str(item_id)].values()) == count,
                'R02 audited CAD/finish face count mismatch '+str(item_id))
    require(abs(float(baseline_qa['placed']['radial']['radial_sweep_mm'])-
                EXPECTED_RADIAL_SWEEP_MM)<.001 and
            baseline_qa['placed']['radial']['passed'] is True,
            'Original 52in blade sweep acceptance changed')
    mats = dict((name(m),eid(m.Id))
                for m in DB.FilteredElementCollector(doc).OfClass(DB.Material))
    require(mats.get(BLACK_MAT)==3370 and mats.get(BRASS_MAT)==3372,
            'R02 Matte Black blade / Soft Brass housing finish identity changed')
    lens = by_id[EXPECTED_LIGHT_LENS]
    box = lens.get_BoundingBox(None)
    require(box is not None, 'OEM light lens lacks native bounds')
    actual = [float(v)*304.8 for v in (
        box.Min.X,box.Min.Y,box.Min.Z,box.Max.X,box.Max.Y,box.Max.Z)]
    expected = [-56.75,-56.25,344.30,56.75,57.25,365.80]
    require(max(abs(actual[i]-expected[i]) for i in range(6)) < 2.0,
            'Light diffuser physical position changed; cannot infer emitter location')
    return {'lens_mm':actual,'lens_center_mm':[(actual[i]+actual[i+3])/2.
             for i in range(3)],
            'blade_ids':list(EXPECTED_BLADES),'imports':actual_imports,
            'radial_sweep_mm':EXPECTED_RADIAL_SWEEP_MM}


def source_elements(doc):
    return list(DB.FilteredElementCollector(doc).OfCategory(
        LIGHT_SOURCE_CATEGORY))


def preflight():
    require(sys.version_info[0] == 2, 'Isolated IronPython 2.7 required')
    app = __revit__.Application
    require(str(app.VersionNumber) == '2025', 'Revit 2025 required')
    require(getattr(__revit__, 'ActiveUIDocument', None) is None,
            'Do not run with user RVT active')
    for path, expected in (
        (SOURCE,SOURCE_SHA), (IES,IES_SHA),
        (VALIDATION,VALIDATION_SHA), (R02_QA,R02_QA_SHA)):
        require(os.path.isfile(path) and sha256(path)==expected,
                'Protected source/photometry hash mismatch: '+path)
    require(not os.path.lexists(TARGET) and not os.path.lexists(RECEIPT),
            'R04 candidate or receipt already exists; refuse overwrite')
    require(os.path.isdir(os.path.dirname(TARGET)),
            'Approved candidate directory unavailable')
    with open(VALIDATION,'rb') as stream:
        validation=json.load(stream)
    require(validation.get('status')==
            'EXACT_MANUFACTURER_LM63_VALIDATED_NATIVE_REVIT_BINDING_PENDING',
            'Exact IES validation status invalid')
    require(validation.get('official_archive_url')==IES_ARCHIVE_URL and
            validation.get('ies_sha256')==IES_SHA and
            validation.get('base_model')=='FR-W2502-52L',
            'Manufacturer model/photometry URL/hash mismatch')
    optical=validation['ies_validation']
    require(optical['valid'] is True and
            optical['header_tags']['LUMINAIRE']=='FR-W2502-52L' and
            optical['header_tags']['MANUFAC']=='WAC Lighting' and
            abs(float(optical['lamp_lumens'])-IES_FLUX)<.01 and
            abs(float(optical['test_input_watts'])-IES_TEST_WATTS)<.0001,
            'Official optical model/lumens/wattage not exact')
    with open(IES,'rb') as stream:
        header=stream.read(800).decode('ascii')
    for value in ('IESNA:LM-63-2002','[MANUFAC] WAC Lighting',
                  '[LUMINAIRE] FR-W2502-52L','TILT=NONE'):
        require(value in header,'Official IES LM63 header mismatch: '+value)
    with open(R02_QA,'rb') as stream:
        qa=json.load(stream)
    require(qa.get('status')=='NATIVE_MATERIAL_AND_SWEEP_PASS_VISUAL_HOLD'
            and qa['input_shas'].get(SOURCE)==SOURCE_SHA,
            'Protected R02 material/sweep QA not matching source')
    return app,qa,optical


def native_light(doc):
    flag=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE)
    require(flag is not None and str(flag.StorageType)=='Integer',
            'BLOCK_NATIVE_LIGHT_FLAG_UNSUPPORTED')
    require(flag.AsInteger()==1, 'Family owner light-source flag not enabled')
    lf=DB.Lighting.LightFamily.GetLightFamily(doc)
    require(lf is not None and int(lf.GetNumberOfLightTypes())==1,
            'BLOCK_NO_NATIVE_LIGHTTYPE_AFTER_ACTIVATION')
    lt=lf.GetLightType(0)
    require(lt is not None,'Native LightType(0) unavailable')
    require(len(source_elements(doc))==1,
            'BLOCK_EXPECTED_ONE_REAL_LIGHT_SOURCE_ELEMENT')
    return lf,lt


def bound_state(doc):
    lf,lt=native_light(doc)
    dist=lt.GetLightDistribution()
    require(isinstance(dist,DB.Lighting.PhotometricWebLightDistribution),
            'BLOCK_NO_REAL_PHOTOMETRIC_WEB_DISTRIBUTION')
    flux=lt.GetInitialIntensity()
    color=lt.GetInitialColor()
    require(isinstance(flux,DB.Lighting.InitialFluxIntensity),
            'Native light intensity class is not InitialFluxIntensity')
    require(isinstance(color,DB.Lighting.CustomInitialColor),
            'Native light color class is not CustomInitialColor')
    fm=doc.FamilyManager
    web=fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
    require(web is not None and str(web.StorageType)=='String',
            'No native writable type Photometric Web File parameter')
    transform=lf.GetLightSourceTransform()
    result={
        'category':name(doc.OwnerFamily.FamilyCategory),
        'placement':str(doc.OwnerFamily.FamilyPlacementType),
        'light_type_count':int(lf.GetNumberOfLightTypes()),
        'source_element_ids':[eid(x.Id) for x in source_elements(doc)],
        'shape_style':str(lf.GetLightShapeStyle()),
        'distribution_style':str(lf.GetLightDistributionStyle()),
        'ies_distribution':unicode(dist.PhotometricWebFile or ''),
        'ies_type':unicode(fm.CurrentType.AsString(web) or ''),
        'flux_lm':float(flux.Flux),
        'cct_kelvin':float(color.Temperature),
        'emitter_origin_ft':[float(transform.Origin.X),
                             float(transform.Origin.Y),
                             float(transform.Origin.Z)],
        'emitter_basis_z':[float(transform.BasisZ.X),
                           float(transform.BasisZ.Y),
                           float(transform.BasisZ.Z)],
        'warnings':warning_text(doc)}
    return result


def assert_bound(state):
    require(state['category']=='Lighting Fixtures'
            and state['placement']=='WorkPlaneBased',
            'Light category/hosting changed')
    require(state['light_type_count']==1 and
            len(state['source_element_ids'])==1,
            'No true one-source Revit LightFamily')
    require('Point' in state['shape_style'] and
            'PhotometricWeb' in state['distribution_style'],
            'Native optical shape or IES style not preserved')
    for key in ('ies_distribution','ies_type'):
        require(basename(state[key])==IES_NAME.lower(),
                'Official model IES not bound in '+key)
    require(abs(state['flux_lm']-IES_FLUX)<.01 and
            abs(state['cct_kelvin']-CCT)<.05,
            'Native flux or factory default CCT does not match OEM')
    require(state['emitter_basis_z'][2]>.90,
            'Native emitter orientation not safely aligned with fan light lens')
    require(not state['warnings'],
            'BLOCK_NATIVE_LIGHT_GEOMETRY_WARNING: '+str(state['warnings']))


def tx_start(doc,label):
    tx=DB.Transaction(doc,label)
    require(tx.Start()==DB.TransactionStatus.Started,
            'Cannot start '+label)
    return tx


def add_type_metadata(fm,label,value):
    require(fm.get_Parameter(label) is None,
            'R04 status parameter already exists '+label)
    p=fm.AddParameter(label,DB.GroupTypeId.IdentityData,
                      DB.SpecTypeId.String.Text,False)
    fm.Set(p,unicode(value))


def main():
    app,qa,optical=preflight()
    stage=os.path.join(os.path.dirname(TARGET),
                       '_stage_smooth_r04_light_'+uuid.uuid4().hex+'.rfa')
    doc=None
    opened=None
    tx=None
    promoted=False
    report={'status':'STARTED','model':'FR-W2502-52L-SB/MB',
            'source':SOURCE,'source_sha256':SOURCE_SHA,
            'manufacturer_archive_url':IES_ARCHIVE_URL,
            'official_ies':IES,'official_ies_sha256':IES_SHA,
            'r02_native_qa_sha256':R02_QA_SHA,
            'source_validation_sha256':VALIDATION_SHA,
            'target':TARGET,
            'photometric_test_lumens':IES_FLUX,
            'photometric_test_watts':IES_TEST_WATTS,
            'manufacturer_nominal_light_kit_watts':OEM_LED_WATTS,
            'default_cct_kelvin':CCT,
            'not_certified':['finish-specific light photometry',
              'CCT-specific angular photometry','fan motor electric load',
              'MEP connector/circuit scheduling','IES orientation in project']}
    try:
        doc=app.OpenDocumentFile(SOURCE)
        require(doc.IsFamilyDocument and
                name(doc.OwnerFamily.FamilyCategory)=='Lighting Fixtures' and
                str(doc.OwnerFamily.FamilyPlacementType)=='WorkPlaneBased',
                'BLOCK_SOURCE_NOT_LIGHTING_FIXTURE_OR_HOST_CHANGED')
        fm=doc.FamilyManager
        types=list(fm.Types)
        require(len(types)==1 and fm.CurrentType is not None,
                'BLOCK_UNEXPECTED_OEM_FAMILY_TYPES')
        report['source_type_name']=name(fm.CurrentType)
        flag=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE)
        require(flag is not None and not flag.IsReadOnly and
                str(flag.StorageType)=='Integer' and flag.AsInteger()==0,
                'BLOCK_LIGHT_FLAG_UNAVAILABLE_OR_ALREADY_ACTIVE')
        report['original_native_flag']=int(flag.AsInteger())
        lf=DB.Lighting.LightFamily.GetLightFamily(doc)
        require(lf is not None and lf.GetNumberOfLightTypes()==0,
                'BLOCK_ROOT_CAUSE_CHANGED_EXPECTED_ZERO_LIGHTTYPES')
        pre_sources=source_elements(doc)
        require(len(pre_sources)==1 and eid(pre_sources[0].Id)==3044,
                'BLOCK_OEM_DORMANT_LIGHT_SOURCE_ID_NOT_VERIFIED')
        p=fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
        require(p is not None and str(p.StorageType)=='String' and
                basename(fm.CurrentType.AsString(p))==IES_NAME.lower(),
                'BLOCK_EXPECTED_EXACT_OEM_IES_REFERENCE_NOT_PRESENT')
        initial_warn=warning_text(doc)
        require(not initial_warn,'Original R02 family has Revit warnings')
        baseline=protected(doc)
        physical=known_parts(doc,qa)
        report['source_physical_fingerprint']=baseline
        report['lens_source_dimensions']=physical
        report['source_warnings']=initial_warn

        # Same native Light Source flag activation as successful Hinkley R05.
        tx=tx_start(doc,'R04 activate real native Smooth light family')
        require(flag.Set(1),'OwnerFamily Light Source flag Set(1) failed')
        require(tx.Commit()==DB.TransactionStatus.Committed,
                'Native light flag transaction failed')
        tx=None
        lf,lt=native_light(doc)
        require(protected(doc)==baseline,
                'Activation changed existing OEM blade/housing/import geometry')

        # Set light shape/distribution in separate family-element transaction.
        tx=tx_start(doc,'R04 native light point and photometric web style')
        lf.SetLightShapeStyle(DB.Lighting.LightShapeStyle.Point)
        lf.SetLightDistributionStyle(DB.Lighting.LightDistributionStyle.PhotometricWeb)
        require(tx.Commit()==DB.TransactionStatus.Committed,
                'Native point/photometric-web style transaction failed')
        tx=None
        lf,lt=native_light(doc)
        require(isinstance(lt.GetLightDistribution(),
                           DB.Lighting.PhotometricWebLightDistribution),
                'BLOCK_STYLE_HAS_NO_NATIVE_PHOTOMETRIC_DISTRIBUTION')

        # API 2025 warns family light distribution is an element setting;
        # keep this transaction isolated from the type lumens/CCT edits.
        tx=tx_start(doc,'R04 exact official IES distribution')
        dist=lt.GetLightDistribution()
        dist.PhotometricWebFile=IES
        lt.SetLightDistribution(dist)
        require(tx.Commit()==DB.TransactionStatus.Committed,
                'Manufacturer IES distribution transaction failed')
        tx=None

        tx=tx_start(doc,'R04 tested flux and source default CCT')
        lf,lt=native_light(doc)
        lt.SetInitialIntensity(DB.Lighting.InitialFluxIntensity(IES_FLUX))
        lt.SetInitialColor(DB.Lighting.CustomInitialColor(CCT))
        lt.SetLossFactor(DB.Lighting.BasicLossFactor(1.0))
        native_web=fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
        require(native_web is not None and not native_web.IsReadOnly and
                str(native_web.StorageType)=='String',
                'BLOCK_REAL_TYPE_WEB_NOT_WRITABLE')
        fm.Set(native_web,IES)
        require(tx.Commit()==DB.TransactionStatus.Committed,
                'Revit native flux/CCT/type filename commit failed')
        tx=None

        # OEM 3D lens id3000 is Z344.30..365.80mm in source family.
        # Put the single real point source 5.08mm beyond its front surface,
        # normal +Z, preserving every physical fan element at existing pose.
        lf,lt=native_light(doc)
        trans=lf.GetLightSourceTransform()
        require(float(trans.BasisZ.Z)>.90,
                'BLOCK_UNVERIFIED_LIGHT_SOURCE_ORIENTATION')
        mm=physical['lens_mm']
        center_x=(mm[0]+mm[3])/2.0
        center_y=(mm[1]+mm[4])/2.0
        target=DB.XYZ(center_x/304.8,center_y/304.8,
                      (mm[5]+5.08)/304.8)
        origin=trans.Origin
        require(abs(float(origin.X)*304.8-center_x) < 100.0 and
                abs(float(origin.Y)*304.8-center_y) < 100.0 and
                abs(float(origin.Z)*304.8-mm[5]) < 100.0,
                'BLOCK_NATIVE_EMITTER_TOO_FAR_FROM_OEM_LIGHT_KIT')
        tx=tx_start(doc,'R04 locate native emitter outside OEM lens')
        light_source=source_elements(doc)[0]
        DB.ElementTransformUtils.MoveElement(
            doc,light_source.Id,target.Subtract(origin))
        require(tx.Commit()==DB.TransactionStatus.Committed,
                'Native emitter relocation failed')
        tx=None

        tx=tx_start(doc,'R04 exact OEM optics provenance type metadata')
        for title,value in (
            ('R04 OEM Luminaire','FR-W2502-52L'),
            ('R04 Official IES URL',IES_ARCHIVE_URL),
            ('R04 Official IES SHA256',IES_SHA),
            ('R04 IES Measured Light Output','707.09 lm at 16.7549 W - WAC 2024-11-25'),
            ('R04 Nominal LED Light Kit','16 W, 707 delivered lm - Modern Forms'),
            ('R04 Default Color Temperature','3000 K, 2700/4000/5000 K selectable'),
            ('R04 Optical Release','Exact model IES bound. CCT/finish angular match unverified.'),
            ('R04 Electrical Status','Fan motor/driver load and MEP connector not verified.'),
            ('R04 Finish Status','R02 Matte Black blades and Soft Brass housing preserved; CAD imports partial.'),
            ('R04 Visual Status','NATIVE SOURCE ACTIVATED; PROJECT LIGHT BEAM / REALISTIC QA PENDING')):
            add_type_metadata(fm,title,value)
        require(tx.Commit()==DB.TransactionStatus.Committed,
                'R04 provenance parameter transaction failed')
        tx=None
        state=bound_state(doc)
        assert_bound(state)
        report['working_light']=state
        require(protected(doc)==baseline,
                'R04 changed original 52in fan geometry or finish materials')
        require(known_parts(doc,qa)==physical,
                'R04 altered light kit lens or blade/low-level imported geometry')
        # Save only after all native state and source safety checks passed.
        require(not os.path.lexists(stage),'Staging file name collision')
        opt=DB.SaveAsOptions()
        opt.OverwriteExistingFile=False
        opt.MaximumBackups=1
        doc.SaveAs(stage,opt)
        doc.Close(False)
        doc=None
        require(os.path.isfile(stage),'Staged R04 RFA SaveAs missing')
        opened=app.OpenDocumentFile(stage)
        saved=bound_state(opened)
        assert_bound(saved)
        report['reopened_light']=saved
        require(protected(opened)==baseline,
                'R04 staged/reopened fan geometry or materials drifted')
        require(known_parts(opened,qa)==physical,
                'R04 staged/reopened fan dimensions/parts changed')
        require([name(t) for t in opened.FamilyManager.Types]==
                [report['source_type_name']],
                'R04 family type changed during source activation')
        opened.Close(False)
        opened=None
        require(sha256(SOURCE)==SOURCE_SHA and sha256(IES)==IES_SHA,
                'Original R02 or IES bytes changed during native work')
        require(not os.path.lexists(TARGET),
                'R04 target appeared during staged QA; refusing overwrite')
        verified_sha=sha256(stage)
        os.rename(stage,TARGET)
        stage=None
        require(sha256(TARGET)==verified_sha,'R04 file changed during promotion')
        report['candidate_sha256']=verified_sha
        report['status']='R04_REAL_LIGHTFAMILY_EXACT_IES_REOPEN_PASS_VISUAL_HOLD'
        report['original_geometry_material_and_52in_sweep_preserved']=True
        report['companion_ies_required_for_portability']=True
    except Exception:
        report['status']='BLOCKED_OR_ERROR_NO_RELEASE'
        report['error']=traceback.format_exc()
    finally:
        if tx is not None:
            try:tx.RollBack()
            except Exception:pass
        for item in (opened,doc):
            if item is not None:
                try:item.Close(False)
                except Exception:pass
        report['protected_r02_sha256_after']=sha256(SOURCE)
        report['official_ies_sha256_after']=sha256(IES)
        report['protected_sources_unchanged']=(report['protected_r02_sha256_after']==SOURCE_SHA and
                                               report['official_ies_sha256_after']==IES_SHA)
        report['time_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
        if not os.path.lexists(RECEIPT):
            fd=os.open(RECEIPT,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o666)
            with os.fdopen(fd,'w') as stream:
                json.dump(report,stream,indent=2,sort_keys=True,ensure_ascii=True)
                stream.write('\n')
        print('SMOOTH_R04_NATIVE_IES '+report['status'])
        print('R04_RECEIPT '+RECEIPT)
        if stage is not None and os.path.isfile(stage):
            print('R04_UNRELEASED_STAGE '+stage)
    require(report['status']=='R04_REAL_LIGHTFAMILY_EXACT_IES_REOPEN_PASS_VISUAL_HOLD',
            report.get('error','No validated native R04 candidate released'))


if __name__ == '__main__':
    main()
