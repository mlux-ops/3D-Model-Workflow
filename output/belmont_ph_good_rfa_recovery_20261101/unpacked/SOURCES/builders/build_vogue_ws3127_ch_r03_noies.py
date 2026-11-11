# -*- coding: utf-8 -*-
"""WS-3127-CH R03 (NO-IES / OEM TYPE DATA), unexecuted / unapproved.

IronPython 2.7 in standalone pyRevit 2025. This script starts from the
SHA-guarded R02 Chrome/opal family and produces ONLY an isolated R03.

The manufacturer's CURRENT tested angular distribution was not available
on 2026-10-16. R03 replaces the old 2017 photometric-web distribution
with a visibly labeled generic spherical PRELIMINARY placeholder.
The placeholder is NOT manufacturer photometry and CANNOT be used
for lighting-level validation. No old IES is assigned or transformed.

Source https://modernforms.com/product/vogue/
Spec https://modernforms.com/dynamic-specsheet/?download=specs5&ppid=1546
API https://www.revitapidocs.com/2025/c572d26c-9344-9256-64b0-88b19b6d768d.htm
API https://www.revitapidocs.com/2025/0efb807e-bc7f-50dc-886f-ab8e9958901a.htm
API https://www.revitapidocs.com/2025/b5a83b94-c75b-f7d7-bd38-310c6e89bc3b.htm
"""
from __future__ import print_function
import os
import sys
import json
import math
import uuid
import hashlib
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SOURCE = os.path.join(BASE, 'candidates',
                      'ModernForms_Vogue_WS-3127_CH_R2025_R02.rfa')
TARGET = os.path.join(BASE, 'candidates',
                      'ModernForms_Vogue_WS-3127_CH_R2025_R03.rfa')
RECEIPT = os.path.join(BASE, 'qa',
                       'vogue_ws3127_r03_noies_builder_receipt.json')
OEM_PAGE = 'https://modernforms.com/product/vogue/'
OEM_SPEC = 'https://modernforms.com/dynamic-specsheet/?download=specs5&ppid=1546'
SOURCE_HASH = 'e5d49df849079974e7e1e3e3718a898e7f9671d0ca03633f4dead35fc1c0d9b8'
MODEL = 'WS-3127-CH'
OLD_WEB = 'WS-3127.IES'
OEM_WATTS = 40.6
OEM_DELIVERED_LUMENS = 2993.0
OEM_DEFAULT_CCT = 3000.0
CHROME = 'PHGOOD_VOGUE_CH_CHROME'
OPAL = 'PHGOOD_VOGUE_MOUTH_BLOWN_OPAL'
METADATA = {
    'PH GOOD OEM Input Power': (
        DB.GroupTypeId.Electrical, DB.SpecTypeId.ElectricalPower,
        DB.UnitTypeId.Watts, OEM_WATTS),
    'PH GOOD OEM Delivered Flux': (
        DB.GroupTypeId.Electrical, DB.SpecTypeId.LuminousFlux,
        DB.UnitTypeId.Lumens, OEM_DELIVERED_LUMENS),
    'PH GOOD OEM Default CCT': (
        DB.GroupTypeId.Electrical, DB.SpecTypeId.ColorTemperature,
        DB.UnitTypeId.Kelvin, OEM_DEFAULT_CCT),
}
TEXT_METADATA = {
    'PH GOOD Photometric Status':
        'NO CURRENT OEM IES - GENERIC SPHERICAL VISUALIZATION ONLY - PHOTOMETRIC CALCS HOLD',
    'PH GOOD Electrical Load Status':
        'NO MEP ELECTRICAL CONNECTOR - 40.6W OEM INPUT POWER ONLY - CIRCUIT VA UNKNOWN',
    'PH GOOD Manufacturer Evidence':
        OEM_PAGE + ' ; ' + OEM_SPEC,
    'PH GOOD CCT Options':
        '3000K default; field adjustable to 2700K/3500K (OEM)',
}


def require(ok, text):
    if not ok:
        raise RuntimeError(text)


def sha256(path):
    hasher = hashlib.sha256()
    with open(path, 'rb') as handle:
        while True:
            b = handle.read(1024 * 1024)
            if not b:
                return hasher.hexdigest()
            hasher.update(b)


def val_id(element_id):
    try:
        return int(element_id.Value)
    except Exception:
        return int(element_id.IntegerValue)


def name_of(item):
    return str(item.Name)


def physical_fingerprint(doc):
    """Preserve actual R02 appearance and bound physical model geometry.

    The old R02 visual-appearance receipt and the new native QA report
    disagree about the OPAL Material.Color/Transparency. Source R02 itself
    is the only baseline authority; no finish corrections are attempted.
    """
    mats = []
    names = set()
    for mat in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        names.add(name_of(mat))
        rgb = [int(mat.Color.Red), int(mat.Color.Green), int(mat.Color.Blue)]
        mats.append([val_id(mat.Id), name_of(mat), rgb,
                     int(mat.Transparency), val_id(mat.AppearanceAssetId)])
    require(CHROME in names and OPAL in names,
            'R02 Chrome/opal materials missing; cannot safely revise photometrics')
    geom = []
    for cls in (DB.FreeFormElement, DB.ImportInstance, DB.FamilyInstance):
        for item in DB.FilteredElementCollector(doc).OfClass(cls):
            bb = item.get_BoundingBox(None)
            bounds = None
            if bb is not None:
                bounds = [round(float(v), 8) for v in
                          (bb.Min.X, bb.Min.Y, bb.Min.Z,
                           bb.Max.X, bb.Max.Y, bb.Max.Z)]
            mids = sorted(val_id(x) for x in item.GetMaterialIds(False))
            geom.append([val_id(item.Id), str(cls.Name), bounds, mids])
    return {'materials': sorted(mats, key=lambda a: a[0]),
            'physical_elements': sorted(geom, key=lambda a: a[0])}


def family_state(doc):
    require(doc.IsFamilyDocument, 'Not a family document')
    require(doc.OwnerFamily.FamilyCategory.Name == 'Lighting Fixtures',
            'Unexpected category')
    fm = doc.FamilyManager
    family_types = list(fm.Types)
    require(len(family_types) == 1 and family_types[0].Name == MODEL,
            'Expected exactly one WS-3127-CH family type')
    require(fm.CurrentType is not None and fm.CurrentType.Name == MODEL,
            'Expected CurrentType WS-3127-CH')
    lf = DB.Lighting.LightFamily.GetLightFamily(doc)
    require(lf is not None and lf.GetNumberOfLightTypes() == 1,
            'Expected one native emitter light type')
    lt = lf.GetLightType(0)
    require(lt is not None and str(lf.GetLightTypeName(0)) == MODEL,
            'Native emitter type identity mismatch')
    intensity = lt.GetInitialIntensity()
    color = lt.GetInitialColor()
    require(isinstance(intensity, DB.Lighting.InitialFluxIntensity),
            'Native emitter not InitialFluxIntensity')
    require(isinstance(color, DB.Lighting.CustomInitialColor),
            'Native emitter not CustomInitialColor')
    web = lt.GetLightDistribution()
    web_name = str(web.PhotometricWebFile) if isinstance(
        web, DB.Lighting.PhotometricWebLightDistribution) else None
    web_param = fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
    stored = None
    if web_param is not None:
        require(str(web_param.StorageType) == 'String',
                'Unexpected photometric-web parameter storage')
        stored = family_types[0].AsString(web_param)
    connectors = list(DB.FilteredElementCollector(doc).OfClass(
        DB.ConnectorElement))
    return {
        'family_manager': fm, 'light_family': lf, 'light_type': lt,
        'initial_flux': float(intensity.Flux),
        'color_kelvin': float(color.Temperature),
        'distribution': str(lf.GetLightDistributionStyle()),
        'distribution_class': str(web.GetType().Name),
        'web_filename': web_name, 'web_parameter': stored,
        'connectors': sorted(val_id(x.Id) for x in connectors),
        'physical': physical_fingerprint(doc),
        'warnings': sorted(str(w.GetDescriptionText())
                           for w in doc.GetWarnings())}


def old_state_guard(s):
    require('PhotometricWeb' in s['distribution'],
            'R02 source is not the expected historical IES distribution')
    require(s['web_filename'] is not None and
            os.path.basename(s['web_filename'].replace('\\', '/')).upper() ==
            OLD_WEB.upper(), 'Expected unmodified 2017 WS-3127.IES')
    require(s['web_parameter'] is not None and
            os.path.basename(str(s['web_parameter']).replace('\\', '/')).upper() ==
            OLD_WEB.upper(), 'Historical photometric type value differs')
    require(abs(s['initial_flux'] - 2400.0) < .001 and
            abs(s['color_kelvin'] - OEM_DEFAULT_CCT) < .001,
            'Current native R02 emitter differs from fix01 QA evidence')
    require(len(s['connectors']) == 0,
            'Electrical connector status changed; re-audit before conversion')
    require(not s['warnings'], 'R02 source carries native Revit warnings')


def verify_noies(s, baseline):
    require('Spherical' in s['distribution'] and
            s['distribution_class'] == 'SphericalLightDistribution',
            'No-IES R03 requires native spherical generic distribution')
    require(s['web_filename'] is None,
            'R03 still exposes an IES photometric web')
    require(s['web_parameter'] is None or not str(s['web_parameter']).strip(),
            'R03 retains stale 2017 Photometric Web File type reference')
    require(abs(s['initial_flux'] - OEM_DELIVERED_LUMENS) < .001 and
            abs(s['color_kelvin'] - OEM_DEFAULT_CCT) < .001,
            'Native emitter lumens or Kelvin not retained')
    require(s['connectors'] == baseline['connectors'],
            'Connector count/IDs mutated unexpectedly')
    require(s['physical'] == baseline['physical'],
            'Existing geometry or Chrome/opal materials altered')
    require(s['warnings'] == baseline['warnings'],
            'Revit added family warnings')
    fm = s['family_manager']
    typ = fm.CurrentType
    for name, (group, spec, unit, expected) in METADATA.items():
        p = fm.get_Parameter(name)
        require(p is not None and not p.IsInstance and
                str(p.StorageType) == 'Double',
                'Source-backed native numeric type parameter missing: ' + name)
        val = DB.UnitUtils.ConvertFromInternalUnits(typ.AsDouble(p), unit)
        require(abs(val - expected) < .002,
                'Source-backed numeric type parameter mismatch: ' + name)
    for name, expected in TEXT_METADATA.items():
        p = fm.get_Parameter(name)
        require(p is not None and not p.IsInstance and
                str(p.StorageType) == 'String' and
                str(typ.AsString(p)) == expected,
                'Type metadata not persisted: ' + name)
    va = fm.get_Parameter(DB.BuiltInParameter.RBS_ELEC_APPARENT_LOAD)
    if va is not None:
        try:
            va_value = typ.AsDouble(va)
        except Exception:
            va_value = None
        require(va_value is None or abs(float(va_value)) < 1e-10,
                'Unexpected nonzero apparent load without connector')


def tx_begin(doc, label):
    tx = DB.Transaction(doc, label)
    require(tx.Start() == DB.TransactionStatus.Started,
            'Failed transaction start: ' + label)
    return tx


def main():
    require(sys.version_info[0] == 2, 'Requires IronPython 2.7 in Revit 2025')
    app = __revit__.Application
    require(str(app.VersionNumber) == '2025', 'Revit 2025 required')
    require(os.path.isfile(SOURCE) and sha256(SOURCE) == SOURCE_HASH,
            'R02 Chrome/opal source RFA SHA256 mismatch')
    require(not os.path.lexists(TARGET) and not os.path.lexists(RECEIPT),
            'Target R03 or receipt already exists; no overwrite authorized')
    require(os.path.isdir(os.path.dirname(TARGET)),
            'Isolated candidate directory missing')
    stage = os.path.join(os.path.dirname(TARGET),
                         '_stage_vogue_r03_noies_' + uuid.uuid4().hex + '.rfa')
    original_source_hash = sha256(SOURCE)
    doc = None
    reopened = None
    tx = None
    promoted = False
    try:
        doc = app.OpenDocumentFile(SOURCE)
        baseline = family_state(doc)
        old_state_guard(baseline)
        # Autodesk warns that distribution (family element) and intensity
        # (family type) changes must NOT share a Revit transaction.
        tx = tx_begin(doc, 'R03 retire vintage photometric web')
        lf = DB.Lighting.LightFamily.GetLightFamily(doc)
        lf.SetLightDistributionStyle(DB.Lighting.LightDistributionStyle.Spherical)
        doc.Regenerate()
        require(tx.Commit() == DB.TransactionStatus.Committed,
                'Light distribution change not committed')
        tx = None

        interim = family_state(doc)
        require('Spherical' in interim['distribution'] and
                interim['web_filename'] is None,
                'Stale PhotometricWeb style remains after conversion')
        require(interim['web_parameter'] is None or
                not str(interim['web_parameter']).strip(),
                'Stale IES string remains after style conversion; abort')
        require(interim['physical'] == baseline['physical'],
                'Distribution change altered physical appearance/geometry')
        tx = tx_begin(doc, 'R03 current OEM type specifications')
        lt = DB.Lighting.LightFamily.GetLightFamily(doc).GetLightType(0)
        intensity = lt.GetInitialIntensity()
        color = lt.GetInitialColor()
        require(isinstance(intensity, DB.Lighting.InitialFluxIntensity),
                'Emitter changed intensity class during style change')
        require(isinstance(color, DB.Lighting.CustomInitialColor),
                'Emitter changed CCT class during style change')
        intensity.Flux = OEM_DELIVERED_LUMENS
        lt.SetInitialIntensity(intensity)
        color.Temperature = OEM_DEFAULT_CCT
        lt.SetInitialColor(color)
        fm = doc.FamilyManager
        for name, (group, spec, unit, numeric) in METADATA.items():
            require(fm.get_Parameter(name) is None,
                    'Metadata parameter name already in use: ' + name)
            p = fm.AddParameter(name, group, spec, False)
            require(not p.IsInstance and not p.IsReadOnly,
                    'Native numeric metadata parameter is not writable')
            fm.Set(p, DB.UnitUtils.ConvertToInternalUnits(numeric, unit))
        for name, metadata in TEXT_METADATA.items():
            require(fm.get_Parameter(name) is None,
                    'Status parameter name already in use: ' + name)
            p = fm.AddParameter(name, DB.GroupTypeId.IdentityData,
                                DB.SpecTypeId.String.Text, False)
            fm.Set(p, metadata)
        doc.Regenerate()
        require(tx.Commit() == DB.TransactionStatus.Committed,
                'OEM type values failed to commit')
        tx = None
        before_save = family_state(doc)
        verify_noies(before_save, baseline)
        opts = DB.SaveAsOptions()
        opts.OverwriteExistingFile = False
        opts.MaximumBackups = 1
        doc.SaveAs(stage, opts)
        doc.Close(False)
        doc = None
        require(os.path.isfile(stage), 'Temporary R03 RFA not saved')
        reopened = app.OpenDocumentFile(stage)
        final = family_state(reopened)
        verify_noies(final, baseline)
        reopened.Close(False)
        reopened = None
        require(sha256(SOURCE) == original_source_hash == SOURCE_HASH,
                'Original R02 bytes changed')
        require(not os.path.lexists(TARGET), 'R03 appeared before promotion')
        validated_hash = sha256(stage)
        os.rename(stage, TARGET)
        promoted = True
        require(sha256(TARGET) == validated_hash, 'Published R03 hash mismatch')
        receipt = {
            'status': 'NATIVE_R03_NOIES_SAVE_REOPEN_PASS_PHOTOMETRY_HOLD',
            'model': MODEL, 'source_rfa': SOURCE,
            'source_sha256': SOURCE_HASH,
            'new_rfa': TARGET, 'new_sha256': validated_hash,
            'manufacturer': 'Modern Forms',
            'official_product_url': OEM_PAGE,
            'official_spec_url': OEM_SPEC,
            'manufacturer_input_watts': OEM_WATTS,
            'manufacturer_delivered_lumens': OEM_DELIVERED_LUMENS,
            'default_cct_kelvin': OEM_DEFAULT_CCT,
            'previous_ies': OLD_WEB,
            'new_ies': None,
            'new_light_distribution': 'Spherical (generic visualization only)',
            'manufacturer_angular_photometry_verified': False,
            'lighting_calculation_release': 'HOLD_NO_CURRENT_OEM_IES',
            'electrical_connectors': len(final['connectors']),
            'electrical_circuiting_release': 'HOLD_NO_CONNECTOR',
            'reopened_initial_flux_lm': final['initial_flux'],
            'reopened_color_kelvin': final['color_kelvin'],
            'material_and_physical_geometry_preserved': True,
            'quality_limits': ['No current IES', 'No electrical connector',
                               'Generic spherical angular distribution'],
        }
        fd = os.open(RECEIPT, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o666)
        with os.fdopen(fd, 'w') as out:
            json.dump(receipt, out, sort_keys=True, indent=2,
                      ensure_ascii=True)
            out.write('\n')
        print('R03_NOIES_NATIVE_SAVE_REOPEN_PASS_PHOTOMETRY_AND_ELECTRICAL_HOLD')
        print('CANDIDATE: ' + TARGET)
        print('RECEIPT: ' + RECEIPT)
    finally:
        if tx is not None:
            try:
                tx.RollBack()
            except Exception:
                pass
        for item in (reopened, doc):
            if item is not None:
                try:
                    item.Close(False)
                except Exception:
                    pass
        if not promoted and os.path.isfile(stage):
            try:
                os.unlink(stage)
            except Exception:
                pass


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('R03_NOIES_BUILD_FAILED: ' + traceback.format_exc())
        raise
