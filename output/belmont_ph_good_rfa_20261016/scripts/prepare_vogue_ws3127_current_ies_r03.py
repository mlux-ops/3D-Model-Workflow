# -*- coding: utf-8 -*-
"""Conditional Revit 2025 Vogue WS-3127-CH R03 IES converter (SOURCE ONLY).

HOLD: At authoring, no manufacturer-certified CURRENT 40.6W/2993-lm IES was
retrieved. The required current-source approval JSON deliberately DOES NOT
exist. This script must fail before opening Revit documents until a newly
verified OEM IES and its independent provenance have been supplied.

No geometry, Chrome/opal materials, electrical connector, CCT or wattage
parameters are created or changed by this converter. Native RFA R03 is
published only after an isolated staged SaveAs/reopen and readback passes.
"""
from __future__ import print_function
import os, sys, json, hashlib, math, ntpath, uuid, traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SOURCE = os.path.join(BASE, 'candidates', 'ModernForms_Vogue_WS-3127_CH_R2025_R02.rfa')
TARGET = os.path.join(BASE, 'candidates', 'ModernForms_Vogue_WS-3127_CH_R2025_R03.rfa')
APPROVAL = os.path.join(BASE, 'sources', 'photometry',
                        'WS-3127_CURRENT_IES_VERIFICATION.json')
RECEIPT = os.path.join(BASE, 'qa', 'vogue_ws3127_r03_ies_bind_receipt.json')
SOURCE_SHA = 'e5d49df849079974e7e1e3e3718a898e7f9671d0ca03633f4dead35fc1c0d9b8'
LEGACY_IES_SHA = '6c0a0da084b9fde830f254d8afff7d7b92df1a8e13cca7334e2c4e7e92c4837d'
MODEL = 'WS-3127-CH'
CHROME = 'PHGOOD_VOGUE_CH_CHROME'
OPAL = 'PHGOOD_VOGUE_MOUTH_BLOWN_OPAL'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def hash_file(filename):
    h = hashlib.sha256()
    with open(filename, 'rb') as stream:
        while True:
            data = stream.read(1024 * 1024)
            if not data:
                return h.hexdigest()
            h.update(data)


def norm_name(filename):
    return ntpath.basename(str(filename).replace('/', '\\')).lower()


def validated_current_ies():
    """Require *new* OEM source with matching distribution and test provenance."""
    require(os.path.isfile(APPROVAL),
            'CURRENT_IES_HOLD: no independent manufacturer verification JSON; '
            'the 2017 WS-3127.IES is NOT approved for R03')
    with open(APPROVAL, 'rb') as stream:
        record = json.load(stream)
    for field in ('verified_oem_download_url', 'oem_confirmation_url',
                  'ies_path', 'ies_sha256', 'model', 'finish',
                  'default_cct_kelvin', 'input_watts',
                  'delivered_lumens', 'verification_status'):
        require(field in record, 'OEM verification missing ' + field)
    require(record['verification_status'] == 'MANUFACTURER_CURRENT_IES_VERIFIED',
            'Current manufacturer photometry not independently approved')
    require(record['model'] == MODEL and record['finish'] == 'Chrome' and
            int(record['default_cct_kelvin']) == 3000,
            'Photometric verification must be for WS-3127-CH default 3000K')
    require(abs(float(record['input_watts']) - 40.6) < 0.15 and
            abs(float(record['delivered_lumens']) - 2993.0) < 20.0,
            'Manufacturer verification does not match current 40.6W / 2993 lm')
    urls = [str(record['verified_oem_download_url']).lower(),
            str(record['oem_confirmation_url']).lower()]
    require(all(url.startswith(('https://modernforms.com/',
                                'https://www.modernforms.com/',
                                'https://waclighting.com/',
                                'https://www.waclighting.com/'))
                for url in urls),
            'OEM source URL must be verified and manufacturer-owned')
    require('WS-3120_IESF.zip'.lower() not in urls[0],
            'Current download cannot be the known vintage WS-3120 IES ZIP')
    ies = os.path.abspath(record['ies_path'])
    photo_dir = os.path.normcase(os.path.join(BASE, 'sources', 'photometry'))
    require(os.path.normcase(os.path.dirname(ies)) == photo_dir,
            'Current IES must remain within the established source package')
    require(os.path.isfile(ies), 'Verified OEM IES bytes not present')
    actual_sha = hash_file(ies)
    require(actual_sha == str(record['ies_sha256']).lower(),
            'New IES hash differs from documented manufacturer verification')
    require(actual_sha != LEGACY_IES_SHA,
            'Refusing the old 2017 2424.9-lm WS-3127 IES')
    with open(ies, 'rb') as stream:
        text = stream.read().decode('latin-1')
    lines = text.replace('\r', '').split('\n')
    headers = dict((line[1:line.index(']')].upper(), line[line.index(']') + 1:].strip())
                   for line in lines if line.startswith('[') and ']' in line)
    require('WS-3127' in (headers.get('LUMCAT', '') + ' ' +
                          headers.get('LUMINAIRE', '')).upper(),
            'IES model identifier does not explicitly specify WS-3127')
    require(headers.get('TESTDATE', '') != '2017-11-09',
            'Known old 2017 photometric test date rejected')
    tilt_indexes = [i for i,line in enumerate(lines)
                    if line.strip().upper() == 'TILT=NONE']
    require(len(tilt_indexes) == 1, 'Expected one TILT=NONE LM-63 section')
    vals = []
    for line in lines[tilt_indexes[0] + 1:]:
        vals += [float(value) for value in line.replace(',', ' ').split()]
    require(len(vals) > 13 and vals[3] > 1 and vals[4] >= 1,
            'IES angular/candela data incomplete')
    num_v, num_h = int(vals[3]), int(vals[4])
    require(len(vals) >= 13 + num_v + num_h + num_v * num_h,
            'Incomplete photometric candela matrix')
    require(all(math.isfinite(value) for value in vals),
            'IES contains nonfinite photometric numbers')
    # For this exact 27-inch product, positive lumens/lamp is a precondition.
    # No synthetic scaling/normalization of any candela values is performed.
    require(abs(float(vals[1]) - 2993.0) <= 20.0,
            'IES photometric lumen value does not corroborate 2993 delivered lm')
    require(abs(float(vals[12]) - 40.6) <= 0.15,
            'IES input watts does not corroborate current 40.6W')
    return ies, actual_sha, record, {
        'ies_lumens': vals[1], 'ies_test_watts': vals[12],
        'ies_vert_angles': num_v, 'ies_horiz_angles': num_h,
        'ies_test_date': headers.get('TESTDATE')}


def material_faces(doc):
    names = dict((mat.Name, mat)
                 for mat in DB.FilteredElementCollector(doc).OfClass(DB.Material))
    require(CHROME in names and OPAL in names,
            'R02 Chrome/opal materials missing from family')
    mats = {'metal': names[CHROME], 'diffuser': names[OPAL]}
    require(int(mats['metal'].Transparency) == 0 and
            int(mats['diffuser'].Transparency) == 14,
            'R02 finish transparency changed; hold photometry conversion')
    counts = {'metal': 0, 'diffuser': 0}
    ids = dict((int(v.Id.Value), k) for k,v in mats.items())
    options = DB.Options()
    options.DetailLevel = DB.ViewDetailLevel.Fine
    for element in DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement):
        geom = element.get_Geometry(options)
        if geom is None:
            continue
        for solid in geom:
            if not isinstance(solid, DB.Solid) or solid.Volume <= 1e-12:
                continue
            for face in solid.Faces:
                try:
                    key = ids.get(int(face.MaterialElementId.Value))
                    if key is not None:
                        counts[key] += 1
                except Exception:
                    pass
    require(counts == {'metal': 336, 'diffuser': 52},
            'R02 finish geometry/material assignment no longer matches receipt: ' +
            repr(counts))
    return dict((k, {
        'name': m.Name, 'id': int(m.Id.Value),
        'color': [int(m.Color.Red), int(m.Color.Green), int(m.Color.Blue)],
        'transparency': int(m.Transparency),
        'appearance_id': int(m.AppearanceAssetId.Value),
        'assigned_faces': counts[k]}) for k,m in mats.items())


def photo_state(doc):
    require(doc.IsFamilyDocument and doc.OwnerFamily.FamilyCategory.Name == 'Lighting Fixtures',
            'Input must be a native Lighting Fixtures family')
    fm = doc.FamilyManager
    types = list(fm.Types)
    require(len(types) == 1 and types[0].Name == MODEL,
            'Expected exactly one named WS-3127-CH R02 type')
    param = fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
    require(param is not None and not param.IsReadOnly and
            str(param.StorageType) == 'String',
            'Photometric Web File type parameter unavailable/unwritable')
    value = types[0].AsString(param)
    require(value is not None, 'Cannot read photometric filename from family type')
    light_family = DB.Lighting.LightFamily.GetLightFamily(doc)
    require(light_family is not None and light_family.GetNumberOfLightTypes() == 1,
            'Expected exactly one native Revit light-source type')
    light_type = light_family.GetLightType(0)
    dist = light_type.GetLightDistribution()
    require(isinstance(dist, DB.Lighting.PhotometricWebLightDistribution),
            'Existing source light is not PhotometricWeb; no style conversions allowed')
    connectors = list(DB.FilteredElementCollector(doc).OfClass(DB.ConnectorElement))
    return {'fm': fm, 'parameter': param, 'light_type': light_type,
            'distribution': dist, 'path_parameter': str(value),
            'path_distribution': str(dist.PhotometricWebFile),
            'connectors': [int(c.Id.Value) for c in connectors],
            'materials': material_faces(doc)}


def assert_only_photometry_changed(before, after, new_ies):
    require(before['materials'] == after['materials'],
            'Chrome/opal material or geometry face map changed')
    require(before['connectors'] == after['connectors'],
            'Connector count or IDs changed; no connector mutations authorized')
    require(norm_name(after['path_parameter']) == norm_name(new_ies) and
            norm_name(after['path_distribution']) == norm_name(new_ies),
            'Photometric file reference not persisted to exact new IES')


def main():
    # The official photometric proof gate is intentionally FIRST.
    # A stale 2017 file cannot be bound even if the Revit app is available.
    ies, ies_sha, evidence, photometry = validated_current_ies()
    require(sys.version_info[0] == 2,
            'Native build requires pyRevit IronPython 2.7')
    app = __revit__.Application
    require(str(app.VersionNumber) == '2025', 'Revit 2025 required')
    require(os.path.isfile(SOURCE) and hash_file(SOURCE) == SOURCE_SHA,
            'R02 Chrome/opal family changed from verified SHA256')
    require(not os.path.lexists(TARGET) and not os.path.lexists(RECEIPT),
            'R03 target or receipt already exists; no overwriting')
    candidate_dir = os.path.dirname(TARGET)
    require(os.path.isdir(candidate_dir), 'Belmont candidate folder unavailable')
    stage = os.path.join(candidate_dir,
                         '_stage_ws3127_current_ies_' + uuid.uuid4().hex + '.rfa')
    doc = None
    reopened = None
    tx = None
    promoted = False
    try:
        doc = app.OpenDocumentFile(SOURCE)
        before = photo_state(doc)
        baseline_warnings = sorted(w.GetDescriptionText() for w in doc.GetWarnings())
        tx = DB.Transaction(doc, 'Bind verified modern WS-3127 current OEM IES')
        require(tx.Start() == DB.TransactionStatus.Started,
                'Could not start RFA transaction')
        before['distribution'].PhotometricWebFile = ies
        before['light_type'].SetLightDistribution(before['distribution'])
        before['fm'].Set(before['parameter'], ies)
        doc.Regenerate()
        candidate_state = photo_state(doc)
        assert_only_photometry_changed(before, candidate_state, ies)
        require(sorted(w.GetDescriptionText() for w in doc.GetWarnings()) ==
                baseline_warnings, 'New warning introduced by photometric change')
        require(tx.Commit() == DB.TransactionStatus.Committed,
                'Revit transaction did not commit')
        tx = None
        opts = DB.SaveAsOptions()
        opts.OverwriteExistingFile = False
        opts.MaximumBackups = 1
        doc.SaveAs(stage, opts)
        doc.Close(False)
        doc = None
        require(os.path.isfile(stage), 'Staged RFA not saved')
        reopened = app.OpenDocumentFile(stage)
        final_state = photo_state(reopened)
        assert_only_photometry_changed(before, final_state, ies)
        require(sorted(w.GetDescriptionText() for w in reopened.GetWarnings()) ==
                baseline_warnings, 'Reopened R03 family gained warnings')
        reopened.Close(False)
        reopened = None
        require(hash_file(SOURCE) == SOURCE_SHA,
                'R02 source RFA bytes changed unexpectedly')
        require(not os.path.lexists(TARGET), 'R03 candidate appeared before release')
        stage_hash = hash_file(stage)
        os.rename(stage, TARGET)
        promoted = True
        require(hash_file(TARGET) == stage_hash, 'Candidate publish hash mismatch')
        receipt = {
            'status': 'R03_NATIVE_PHOTOMETRY_ONLY_SAVE_REOPEN_PASS_ELECTRICAL_HOLD',
            'source': SOURCE, 'source_sha256': SOURCE_SHA,
            'candidate': TARGET, 'candidate_sha256': stage_hash,
            'ies_source': ies, 'ies_sha256': ies_sha,
            'official_download_url': evidence['verified_oem_download_url'],
            'oem_confirmation_url': evidence['oem_confirmation_url'],
            'ies_measurements': photometry,
            'model': MODEL, 'finish': 'Chrome', 'cct_claim_kelvin': 3000,
            'source_material_faces': before['materials'],
            'saved_material_faces': final_state['materials'],
            'electrical_connector_count': len(final_state['connectors']),
            'electrical_scheduling_status':
                'HOLD_NO_CONNECTOR' if not final_state['connectors']
                else 'EXISTING_CONNECTOR_UNCHANGED_UNVERIFIED_LOAD',
            'prebind_ies_reference': before['path_parameter'],
            'reopened_ies_reference': final_state['path_parameter'],
            'photometry_portability': 'Keep manufacturer IES companion; internal cache not independently verified',
            'native_light_output_electrical_qa': 'PENDING independent read-only script',
        }
        descriptor = os.open(RECEIPT, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
        with os.fdopen(descriptor, 'w') as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True, ensure_ascii=True)
        print('R03_SAVE_REOPEN_VERIFIED_PHOTOMETRY_ONLY_ELECTRICAL_HOLD')
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
            os.unlink(stage)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('VOGUE_CURRENT_IES_R03_HOLD: ' + traceback.format_exc())
        raise
