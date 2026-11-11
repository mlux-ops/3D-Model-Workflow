# -*- coding: utf-8 -*-
"""Revit 2025 / IronPython 2.7: native-light retrofit of Hinkley 53860BK R03.

Run only by prime in an ISOLATED document-free pyRevit 2025 process:
  pyrevit run <this absolute script> --revit=2025

ROOT CAUSE
  R03 used "Generic Model face based.rft" and changed FamilyCategory to
  Lighting Fixtures. A category alone does not create the native LightFamily:
  LightFamily.GetLightFamily() raises ArgumentException. The proven Revit 2025
  fix is OwnerFamily.get_Parameter(FBX_ASSET_TYPE).Set(1), with the change
  committed, after the category is already Lighting Fixtures.

This creates a real LightFamily, a real Light Source element, a PhotometricWeb
LightType and type-level native IES settings. It PRESERVES the original
face-based/WorkPlaneBased family template and wall-face hosting, the 10 original
FreeFormElement solids, existing material/appearance assets, IDs, finishes,
and the published 25 x 5.5 x 3 inch physical envelope. The 24-inch native
emitter proxy is excluded from the physical-geometry measurement.

The alternative "Lighting Fixture wall based.rft" is installed but would
change face hosting and require orientation/mirrored geometry and material
transfer. It is deliberately NOT used because direct native LightFamily
activation is verified by 2026-09 sconce and 2026-10 grazer Revit runs.

SOURCES:
  https://www.revitapidocs.com/2025/c572d26c-9344-9256-64b0-88b19b6d768d.htm
  https://forums.autodesk.com/t5/revit-api-forum/fbx-light-photometric-file-absolute-ies-path-issue/td-p/6869026
  https://hinkleymedia.s3.amazonaws.com/Products/files/ies/53860.ies

Never saves the source R03. Only issues NEW R05 from a validated staged,
closed and reopened family; no overwrite of prior candidates or receipts.
"""
from __future__ import print_function
import os
import sys
import json
import uuid
import time
import math
import hashlib
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SOURCE = os.path.join(BASE, 'candidates',
                      'Hinkley_Eos_53860BK_R2025_R03_UNAPPROVED.rfa')
IES = os.path.join(BASE, 'sources', 'photometry',
                   'HIN53860BK_53860_official.ies')
TARGET = os.path.join(BASE, 'candidates',
                      'Hinkley_Eos_53860BK_R2025_R05_NATIVE_LIGHT_IES_UNAPPROVED.rfa')
RECEIPT = os.path.join(BASE, 'qa',
                       'hin_r05_native_light_build_receipt.json')
SOURCE_SHA = 'f98a11733c8896549a8a16e956001379df3eb16f76f59acbc2e7197c9713ea70'
IES_SHA = 'b8f4e409bd01f235c2a6a17024825aca667dc187dd95ceb84a5adec90c50e8b9'
IES_URL = 'https://hinkleymedia.s3.amazonaws.com/Products/files/ies/53860.ies'
EXPECTED_TYPE = '53860BK - Black / Etched Glass R03'
EXPECTED_FAMILY_CATEGORY = 'Lighting Fixtures'
EXPECTED_ENVELOPE_IN = (25.0, 5.5, 3.0)
TESTED_IES_FLUX_LM = 1109.0
TESTED_IES_WATT = 18.45
CATALOG_FLUX_LM = 1000.0
CATALOG_WATT = 19.0
CCT_K = 3000.0
CRI = 93
LED_ENGINE = '5386XD'
LED_VOLTAGE = 120
DOC_NOTES = (
    'R05 native Revit lighting emitter enabled via Family Light Source flag. '
    'Exact Hinkley Labs 53860BK LM-63 IES dated 2024-08-15. '
    'LM-63 measured 1109 lm at 18.45 W; manufacturer catalog nominal '
    '1000 lm / 19 W, 3000 K, CRI 93, LED 5386XD, 120 V. '
    'R03 photo-derived geometry and original finish assets preserved. '
    'Photometric orientation, visible output and portability need native '
    'project/render approval. No native electrical connector is claimed.'
)

def require(ok, why):
    if not ok:
        raise RuntimeError(why)

def sha256(path):
    hasher = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            part = stream.read(1024*1024)
            if not part:
                break
            hasher.update(part)
    return hasher.hexdigest()

def id_number(value):
    try: return int(value.Value)
    except Exception: return int(value.IntegerValue)

def name_of(item):
    if item is None: return None
    try: return unicode(DB.Element.Name.GetValue(item))
    except Exception:
        try: return unicode(item.Name)
        except Exception: return None

def list_warnings(doc):
    return sorted(unicode(w.GetDescriptionText()) for w in doc.GetWarnings())

def bbox_tuple(item):
    bb = item.get_BoundingBox(None)
    if bb is None:
        raise RuntimeError('Native physical form without bbox '+str(id_number(item.Id)))
    return tuple(round(float(x), 8) for x in
                 (bb.Min.X,bb.Min.Y,bb.Min.Z,bb.Max.X,bb.Max.Y,bb.Max.Z))

def protected_fingerprint(doc):
    """Everything visually/materially present before enabling native emitter."""
    forms = list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    require(len(forms)==10, 'R03 no longer contains exactly ten known FreeFormElements')
    form_data = []
    for item in forms:
        comments = item.LookupParameter('Comments')
        form_data.append({
            'id': id_number(item.Id), 'bbox_ft': bbox_tuple(item),
            'materials': sorted(id_number(v) for v in item.GetMaterialIds(False)),
            'material_parameter': (
                id_number(item.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM).AsElementId())
                if item.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM) is not None
                else None),
            'comments': comments.AsString() if comments else None
        })
    materials = []
    for m in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        materials.append({
            'id': id_number(m.Id), 'name': name_of(m),
            'rgb': (int(m.Color.Red),int(m.Color.Green),int(m.Color.Blue)),
            'transparency': int(m.Transparency),
            'material_class': unicode(m.MaterialClass),
            'appearance_asset_id': id_number(m.AppearanceAssetId)
        })
    pnames = []
    fm = doc.FamilyManager
    for p in fm.Parameters:
        n = unicode(p.Definition.Name)
        if n.endswith(' Material'):
            require(str(p.StorageType)=='ElementId','Source finish is not native material parameter: '+n)
            pnames.append((n,id_number(fm.CurrentType.AsElementId(p))))
    require(len(pnames)>=2,'Expected source Black Steel / Etched Diffuser materials missing')
    require(DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance).GetElementCount()==0,
            'Unexpected imported geometry')
    return {'physical_freeform':sorted(form_data,key=lambda r:r['id']),
            'materials':sorted(materials,key=lambda r:r['id']),
            'finish_type_values':sorted(pnames),
            'placement_type':str(doc.OwnerFamily.FamilyPlacementType)}

def physical_envelope(doc):
    """Whole, positive-volume R03 forms only; excludes Light Source proxy."""
    options=DB.Options()
    options.DetailLevel=DB.ViewDetailLevel.Fine
    pmin=[float('inf')]*3
    pmax=[float('-inf')]*3
    count=[0]
    def point(v):
        xyz=(float(v.X),float(v.Y),float(v.Z))
        for k in range(3):
            pmin[k]=min(pmin[k],xyz[k])
            pmax[k]=max(pmax[k],xyz[k])
        count[0]+=1
    for element in DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement):
        geom=element.get_Geometry(options)
        for obj in geom:
            if isinstance(obj,DB.Solid) and obj.Volume>1e-12:
                for face in obj.Faces:
                    mesh=face.Triangulate(1.0)
                    for v in mesh.Vertices:point(v)
                for edge in obj.Edges:
                    curve=edge.AsCurve()
                    if curve is None: continue
                    n=2 if isinstance(curve,DB.Line) else 33
                    for i in range(n):
                        point(curve.Evaluate(float(i)/float(n-1),True))
    require(count[0]>0,'No native geometry vertices collected')
    return {'xyz_in':[(pmax[k]-pmin[k])*12.0 for k in range(3)],
            'min_ft':pmin,'max_ft':pmax,'physical_points':count[0]}

def family_light_info(doc):
    flag=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE)
    require(flag is not None and flag.AsInteger()==1,
            'No native Light Source family flag')
    lf=DB.Lighting.LightFamily.GetLightFamily(doc)
    require(lf is not None,'Not a native LightFamily document')
    require(int(lf.GetNumberOfLightTypes())==1,'Expected 1 native photometric light type')
    lt=lf.GetLightType(0)
    require(lt is not None,'GetLightType(0) failed')
    return lf,lt

def light_receipt(doc):
    lf,lt=family_light_info(doc)
    distribution=lt.GetLightDistribution()
    require(isinstance(distribution,DB.Lighting.PhotometricWebLightDistribution),
            'No real PhotometricWebLightDistribution')
    intensity=lt.GetInitialIntensity()
    color=lt.GetInitialColor()
    require(isinstance(intensity,DB.Lighting.InitialFluxIntensity),
            'No native InitialFluxIntensity')
    require(isinstance(color,DB.Lighting.CustomInitialColor),
            'No native CustomInitialColor')
    file=unicode(distribution.PhotometricWebFile or '')
    fparam=doc.FamilyManager.get_Parameter(
        DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
    require(fparam is not None and str(fparam.StorageType)=='String',
            'No native type Photometric Web File string parameter')
    type_value=doc.FamilyManager.CurrentType.AsString(fparam)
    sources=list(DB.FilteredElementCollector(doc).OfCategory(
        DB.BuiltInCategory.OST_LightingFixtureSource))
    require(len(sources)>=1,'No actual Light Source element')
    transform=lf.GetLightSourceTransform()
    return {
      'category':str(doc.OwnerFamily.FamilyCategory.Name),
      'family_placement_type':str(doc.OwnerFamily.FamilyPlacementType),
      'light_source_flag':1,
      'native_light_source_element_ids':[id_number(s.Id) for s in sources],
      'light_shape_style':str(lf.GetLightShapeStyle()),
      'light_distribution_style':str(lf.GetLightDistributionStyle()),
      'distribution_class':str(distribution.GetType().Name),
      'ies_light_type_path':file,
      'ies_type_parameter_path':unicode(type_value or ''),
      'native_initial_flux_lm':float(intensity.Flux),
      'native_initial_kelvin':float(color.Temperature),
      'native_source_transform_origin_ft':[
         float(transform.Origin.X),float(transform.Origin.Y),float(transform.Origin.Z)],
      'native_source_transform_basis_z':[
         float(transform.BasisZ.X),float(transform.BasisZ.Y),float(transform.BasisZ.Z)],
      'warnings':list_warnings(doc)
    }

def assert_emitter(value):
    require(value['category']==EXPECTED_FAMILY_CATEGORY,'Not Lighting Fixtures')
    require(value['family_placement_type']=='WorkPlaneBased','Face hosting changed')
    expected_name=os.path.basename(IES).lower()
    for key in ('ies_light_type_path','ies_type_parameter_path'):
        actual=os.path.basename(value[key].replace('\\','/')).lower()
        require(actual==expected_name,
                'Saved real photometric source mismatch '+key+': '+unicode(value[key]))
    require('PhotometricWeb' in value['light_distribution_style'],
            'Native distribution style reverted')
    require('Point' in value['light_shape_style'],'Native emitter shape not Point')
    require(abs(value['native_initial_flux_lm']-TESTED_IES_FLUX_LM)<0.05,
            'Native source lumens do not equal 2024 test lumens')
    require(abs(value['native_initial_kelvin']-CCT_K)<0.05,
            'Native source CCT mismatch')

def text_parameter(fm,name,value,existing_ok=False):
    p=fm.get_Parameter(name)
    if p is None:
        p=fm.AddParameter(name,DB.GroupTypeId.IdentityData,
                          DB.SpecTypeId.String.Text,False)
    else:
        require(existing_ok,'Unexpected reused metadata field '+name)
        require(not p.IsReadOnly and str(p.StorageType)=='String',
                'Native metadata cannot be updated '+name)
    fm.Set(p,unicode(value))
    return p

def preflight():
    require(sys.version_info[0]==2,'Isolated IronPython 2.7 required')
    try:app=__revit__.Application
    except NameError:raise RuntimeError('pyRevit 2025 context missing')
    require(str(app.VersionNumber)=='2025','Revit 2025 required')
    require(getattr(__revit__,'ActiveUIDocument',None) is None,
            'Refusing to run in active user project')
    require(os.path.isfile(SOURCE) and sha256(SOURCE)==SOURCE_SHA,
            'Protected R03 SHA256 mismatch')
    require(os.path.isfile(IES) and sha256(IES)==IES_SHA,
            'Exact official Hinkley 53860BK IES SHA256 mismatch')
    require(not os.path.lexists(TARGET) and not os.path.lexists(RECEIPT),
            'R05 candidate or receipt already exists')
    with open(IES,'rb') as f:header=f.read(600).decode('ascii')
    for fragment in ('IESNA:LM-63-2002','[MANUFAC] Hinkley',
                     '[LUMINAIRE] 53860BK','[TESTLAB] Hinkley Labs'):
        require(fragment in header,'Official IES header mismatch: '+fragment)
    return app

def transaction(doc,name):
    tx=DB.Transaction(doc,name)
    require(tx.Start()==DB.TransactionStatus.Started,
            'Could not start transaction: '+name)
    return tx

def main():
    app=preflight()
    stage=os.path.join(BASE,'candidates',
        '_stage_hin_53860bk_r05_'+uuid.uuid4().hex+'.rfa')
    report={'model':'53860BK','status':'STARTED',
            'source_rfa':SOURCE,'source_sha256':SOURCE_SHA,
            'exact_official_ies_file':IES,'ies_sha256':IES_SHA,
            'official_ies_url':IES_URL,
            'new_r05_candidate':TARGET,
            'native_template_provenance':(
                'R03 Generic Model face based template; Revit Lighting Fixtures '
                'category, converted to REAL native LightFamily with '
                'OwnerFamily.FBX_ASSET_TYPE=1, preserves face hosting.'),
            'catalog_lumens':CATALOG_FLUX_LM,
            'catalog_watts':CATALOG_WATT,
            'ies_test_lumens':TESTED_IES_FLUX_LM,
            'ies_test_watts':TESTED_IES_WATT,
            'cct_kelvin':CCT_K,'cri':CRI,'led_engine':LED_ENGINE,
            'native_ies_portability':'COMPANION_FILE_REQUIRED',
            'electrical_connector':'UNVERIFIED_NOT_CREATED',
            'render_orientation_and_visual_qa':'PENDING',
            'geometry_from_R03_photo_reconstruction':'PRESERVED_NOT_OEM_CAD',
            'stage':stage}
    doc=None
    reopened=None
    tx=None
    try:
        doc=app.OpenDocumentFile(SOURCE)
        require(doc.IsFamilyDocument,'Source is not RFA')
        require(str(doc.OwnerFamily.FamilyCategory.Name)==EXPECTED_FAMILY_CATEGORY,
                'R03 category no longer Lighting Fixtures')
        require(str(doc.OwnerFamily.FamilyPlacementType)=='WorkPlaneBased',
                'Source face-host placement changed')
        fm=doc.FamilyManager
        types=list(fm.Types)
        require(len(types)==1 and unicode(types[0].Name)==EXPECTED_TYPE,
                'Original R03 family type was modified')
        require(fm.CurrentType is not None and
                unicode(fm.CurrentType.Name)==EXPECTED_TYPE,'Wrong R03 active type')
        flag=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE)
        require(flag is not None and not flag.IsReadOnly and flag.AsInteger()==0,
                'Source light flag not known OFF; refuse ambiguous retrofit')
        report['source_physical']=protected_fingerprint(doc)
        report['source_envelope']=physical_envelope(doc)
        report['source_warnings']=list_warnings(doc)
        require(not report['source_warnings'],'R03 source warning set not empty')
        require(max(abs(report['source_envelope']['xyz_in'][i]-
                        EXPECTED_ENVELOPE_IN[i]) for i in range(3)) < 1.0/25.4,
                'R03 source physical envelope differs >1mm from 25x5.5x3')
        # Revit native confirmed precedent: sconce 2026-09-29 and grazer 10-04.
        tx=transaction(doc,'R05 enable TRUE native family light source')
        require(flag.Set(1),'Revit failed to enable owner Light Source parameter')
        require(tx.Commit()==DB.TransactionStatus.Committed,'Light flag commit failed')
        tx=None
        lf,lt=family_light_info(doc)
        require(protected_fingerprint(doc)==report['source_physical'],
                'Enabling native emitter changed original ten solids or material assets')
        # Shape/distribution changes must be isolated from LightType numeric
        # edits (Revit regenerates/replaces native light-type parameters).
        tx=transaction(doc,'R05 native light point and photometric web style')
        lf.SetLightShapeStyle(DB.Lighting.LightShapeStyle.Point)
        lf.SetLightDistributionStyle(DB.Lighting.LightDistributionStyle.PhotometricWeb)
        require(tx.Commit()==DB.TransactionStatus.Committed,
                'Native photometric style commit failed')
        tx=None
        lf,lt=family_light_info(doc)
        require(isinstance(lt.GetLightDistribution(),
                          DB.Lighting.PhotometricWebLightDistribution),
                'PhotometricWeb setting did not create real native distribution')
        tx=transaction(doc,'R05 bind certified IES and native light color and flux')
        distribution=lt.GetLightDistribution()
        distribution.PhotometricWebFile=IES
        lt.SetLightDistribution(distribution)
        lt.SetInitialIntensity(DB.Lighting.InitialFluxIntensity(TESTED_IES_FLUX_LM))
        lt.SetInitialColor(DB.Lighting.CustomInitialColor(CCT_K))
        lt.SetLossFactor(DB.Lighting.BasicLossFactor(1.0))
        web=fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
        require(web is not None and str(web.StorageType)=='String' and not web.IsReadOnly,
                'Native family photometric parameter unavailable/unwritable')
        fm.Set(web,IES)
        doc.Regenerate()
        require(tx.Commit()==DB.TransactionStatus.Committed,
                'Photometric source/type commit failed')
        tx=None
        # Source is a point emitter, parked physically within central assembly
        # 1.6in from wall face, exactly x=y=0. Aim MUST be visually confirmed.
        lf,lt=family_light_info(doc)
        source_ids=[e.Id for e in DB.FilteredElementCollector(doc).OfCategory(
                     DB.BuiltInCategory.OST_LightingFixtureSource)]
        require(len(source_ids)==1,
                'Expected exactly one native light source to move')
        source_transform=lf.GetLightSourceTransform()
        target_origin=DB.XYZ(0.0,0.0,1.6/12.0)
        tx=transaction(doc,'R05 center native emitter within fixture projection')
        DB.ElementTransformUtils.MoveElement(
            doc,source_ids[0],target_origin.Subtract(source_transform.Origin))
        require(tx.Commit()==DB.TransactionStatus.Committed,
                'Moving native light source failed')
        tx=None
        # Only write true, source-attributed metadata. 19W is catalog ELECTRIC
        # rating, not an invented electrical connector or apparent-load value.
        tx=transaction(doc,'R05 source-backed type data and revision metadata')
        for key,value in [
           ('R05 Native Light Source','YES - Revit LightFamily, Photometric Web'),
           ('R05 Official IES URL',IES_URL),
           ('R05 Official IES SHA256',IES_SHA),
           ('R05 Hinkley LED Engine',LED_ENGINE),
           ('R05 Nominal LED Power','19 W (Hinkley catalog)'),
           ('R05 Test LED Power','18.45 W (Hinkley Labs 2024-08-15 IES)'),
           ('R05 Nominal Delivered Lumens','1000 lm (Hinkley catalog)'),
           ('R05 IES Test Lumens','1109 lm (Hinkley Labs IES)'),
           ('R05 LED CCT','3000 K'),
           ('R05 LED CRI','93'),
           ('R05 LED Voltage','120 V'),
           ('R05 Native Connector Status','No verified electrical connector'),
           ('R05 IES Orientation Status','PENDING project/photometric visual QA'),
           ('R05 Geometry Source','R03 dimension-checked photo reconstruction'),
           ('R05 Reconstruction Notes',DOC_NOTES)
        ]:text_parameter(fm,key,value)
        text_parameter(fm,'Photometry Status',
                       'Exact verified Hinkley 53860BK official IES bound; '+DOC_NOTES,
                       existing_ok=True)
        require(tx.Commit()==DB.TransactionStatus.Committed,
                'R05 metadata commit failed')
        tx=None
        report['working_native_light']=light_receipt(doc)
        assert_emitter(report['working_native_light'])
        require(protected_fingerprint(doc)==report['source_physical'],
                'Real light source conversion mutated R03 visible solids/materials')
        report['working_envelope']=physical_envelope(doc)
        require(max(abs(report['working_envelope']['xyz_in'][i]-
                        EXPECTED_ENVELOPE_IN[i]) for i in range(3))<1.0/25.4,
                'Native light changed positive-volume physical bounds')
        require(not list_warnings(doc),'New warnings in native source family')
        require(not os.path.lexists(stage),'Stage RFA collision')
        save=DB.SaveAsOptions()
        save.OverwriteExistingFile=False
        save.MaximumBackups=1
        doc.SaveAs(stage,save)
        doc.Close(False)
        doc=None
        require(os.path.isfile(stage),'SaveAs failed to create staged new R05')
        reopened=app.OpenDocumentFile(stage)
        report['saved_native_light']=light_receipt(reopened)
        assert_emitter(report['saved_native_light'])
        require(report['saved_native_light']['warnings']==report['source_warnings'],
                'Reopened R05 emits native family warnings')
        require(protected_fingerprint(reopened)==report['source_physical'],
                'R05 SaveAs lost or changed source material/geometry')
        report['saved_envelope']=physical_envelope(reopened)
        require(max(abs(report['saved_envelope']['xyz_in'][i]-
                        EXPECTED_ENVELOPE_IN[i]) for i in range(3))<1.0/25.4,
                'Saved/reopened physical dimensions differ from 25x5.5x3')
        params=reopened.FamilyManager
        for name in ('R05 Nominal LED Power','R05 IES Test Lumens',
                     'Photometry Status','R05 Official IES SHA256'):
            p=params.get_Parameter(name)
            require(p is not None and params.CurrentType.AsString(p),
                    'New type evidence missing after reopen: '+name)
        reopened.Close(False)
        reopened=None
        require(sha256(SOURCE)==SOURCE_SHA,'R03 source hash changed')
        require(sha256(IES)==IES_SHA,'Official photometry file changed')
        require(not os.path.lexists(TARGET),'R05 target appeared during QA')
        validated_sha=sha256(stage)
        os.rename(stage,TARGET)
        stage=None
        require(sha256(TARGET)==validated_sha,'R05 promotion changed candidate bytes')
        report['status']='R05_REAL_LIGHTFAMILY_NATIVE_IES_REOPEN_PASS_VISUAL_HOLD'
        report['candidate_sha256']=validated_sha
        report['source_geometry_and_materials_unchanged']=True
    except Exception:
        report['status']='ERROR_NO_RELEASE'
        report['error']=traceback.format_exc()
    finally:
        if tx is not None:
            try:tx.RollBack()
            except Exception:pass
        for document in (reopened,doc):
            if document is not None:
                try:document.Close(False)
                except Exception:pass
        report['source_preserved']=os.path.isfile(SOURCE) and sha256(SOURCE)==SOURCE_SHA
        report['official_ies_preserved']=os.path.isfile(IES) and sha256(IES)==IES_SHA
        report['receipt_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
        # Create-new only, never overwrite any earlier run.
        if not os.path.lexists(RECEIPT):
            descriptor=os.open(RECEIPT,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o666)
            with os.fdopen(descriptor,'w') as handle:
                json.dump(report,handle,indent=2,sort_keys=True)
        print('HIN_R05_BUILD '+report['status'])
        print('R05_RECEIPT '+RECEIPT)
        if stage is not None and os.path.isfile(stage):
            print('R05_UNRELEASED_STAGE '+stage)
    require(report['status'].startswith('R05_REAL_LIGHTFAMILY'),
            'R05 native build hold: '+report.get('error','unknown reason'))

main()
