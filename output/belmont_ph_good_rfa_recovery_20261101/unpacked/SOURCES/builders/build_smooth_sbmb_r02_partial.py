# -*- coding: utf-8 -*-
"""Guarded PARTIAL finish conversion of OEM Modern Forms Smooth 52 fan.

IronPython 2.7, isolated Revit 2025. ONLY prime executes via pyrevit run.
This script colors three separately identified FreeFormElement blades black,
five distinct housing/canopy/downrod FreeFormElements brass, and leaves
ALL imported CAD and the unresolved lower light/lens untouched.

Candidate is UNAPPROVED until independent R02 native material/radial QA and
Realistic-view comparison. Swatch colors originate from manufacturer's
published SB/MB graphic; not calibrated manufacturer PBR values.
"""
from __future__ import print_function
import os
import json
import time
import hashlib
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SOURCE = os.path.join(BASE, 'families', 'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025.rfa')
OEM = os.path.join(BASE, 'sources', 'oem', 'extracted',
                   'MFR1415595_FR-W2502_Smooth_Revit', 'FR-W2502-52L.rfa')
PROBE = os.path.join(BASE, 'qa', 'inspect_oem_material_parts.json')
SWATCH = os.path.join(BASE, 'sources', 'oem',
                      'MFR1415595_Smooth_SBMB_official_swatch.jpg')
TARGET = os.path.join(BASE, 'candidates',
    'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R02_PARTIAL_UNAPPROVED.rfa')
RECEIPT = os.path.join(BASE, 'qa', 'smooth_sbmb_r02_build.json')

SOURCE_SHA = '45c76b46fba9daebcf5d0ebbedb7b5592d4eaa50cbbd4b5b59fe44321b7b8e18'
OEM_SHA = '5275e71a2d6cfd033b4cb6d6fa1351d0e78c953586bdbcafe2b905893286d617'
PROBE_SHA = '2ee88654c081a629fa324681703497a72adff29a2481a676f51b98d03b2213b3'
SWATCH_SHA = 'de2bb5517d6b23f9c23e467dad50000886823df6c43784336af97a91afc516c7'

BLADES = (2997, 2998, 2999)
HOUSING = (3038, 3039, 3040, 3041, 3042)
PRESERVE_LENS = 3000
IMPORTS = (2977, 2980, 2982, 2985, 2986, 2987, 2988, 2989,
           2990, 2991, 2992, 2993, 2994)

BLACK_NAME = 'PH GOOD Smooth MB ABS Blades R02 Provisional'
BRASS_NAME = 'PH GOOD Smooth SB Housing R02 Provisional'
BLACK_ASSET = 'PH GOOD Smooth MB Blades R02 Render'
BRASS_ASSET = 'PH GOOD Smooth SB Housing R02 Render'
# Manufacturer's own SB/MB finish swatch pixels: black (150,170), brass
# (40,20). RGB is display-referred photographic reference, not measured albedo.
BLACK_RGB = (14, 14, 14)
BRASS_RGB = (175, 156, 113)
FACE_COUNTS = {2997:140, 2998:140, 2999:140, 3038:52, 3039:20,
               3040:22, 3041:29, 3042:103, 3000:97}
# Measured local bounding XYZ sizes (mm) of exact OEM-derived RFA elements.
EXTENTS_MM = {
  2997:(403.15, 590.32, 50.87),
  2998:(404.76, 589.34, 50.87),
  2999:(644.60, 129.40, 50.87),
  3000:(113.50,113.50,21.50),
  3038:(120.00,119.88,92.00),
  3039:(82.00,81.88,42.10),
  3040:(26.59,26.60,152.40),
  3041:(179.00,179.00,65.50),
  3042:(78.00,78.00,4.30),
}


def guard(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            chunk = stream.read(1024*1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def eid(value):
    try:
        return int(value.Value)
    except Exception:
        return int(value.IntegerValue)


def elt_name(element):
    try:
        return unicode(DB.Element.Name.GetValue(element))
    except Exception:
        return unicode(element.Name)


def fingerprint(path):
    return {'path':path, 'bytes':os.path.getsize(path), 'sha256':sha(path)}


def audit_probe():
    with open(PROBE, 'rb') as stream:
        probe = json.load(stream)
    guard(probe.get('all_native_geometries_read') is True,
          'Native geometry probe was incomplete')
    record = [r for r in probe.get('families', [])
              if r.get('id') == 'mfr1415595']
    guard(len(record) == 1, 'Exactly one Smooth probe entry required')
    record = record[0]
    guard(record.get('source_paths_intact') is True and
          record.get('inspection_status') == 'NATIVE_GEOMETRY_READ_COMPLETE',
          'Source probe does not certify complete original read')
    guard(record['saved_family_before']['sha256'] == SOURCE_SHA and
          record['downloaded_oem_source_before']['sha256'] == OEM_SHA,
          'Probe does not refer to exact guarded OEM family')
    rows = dict((r['id'],r) for r in record['elements'])
    for element_id in BLADES+HOUSING+(PRESERVE_LENS,):
        guard(element_id in rows, 'Missing element %d in probe' % element_id)
        row = rows[element_id]
        guard(row['class'] == 'Autodesk.Revit.DB.FreeFormElement',
              'Expected FreeFormElement id=%d' % element_id)
        guard(row['geometry']['complete'] and
              int(row['geometry']['native_material_face_counts'].get(
                  'None:unassigned', 0)) == FACE_COUNTS[element_id],
              'Unassigned face count or geometry mismatch id=%d' % element_id)
        dims = row['geometry']['physical_aabb_mm']['size_xyz_mm']
        guard(all(abs(float(dims[i])-EXTENTS_MM[element_id][i]) < .3
                  for i in range(3)),
              'Unexpected source element envelope id=%d' % element_id)
    found_imports = [r['id'] for r in record['elements']
                     if r['class'] == 'Autodesk.Revit.DB.ImportInstance']
    guard(sorted(found_imports) == list(IMPORTS),
          'Import ID roster changed')
    for import_id in IMPORTS:
        row = rows[import_id]
        guard(row['geometry']['complete'] and
              list(row['geometry']['native_material_face_counts'].keys()) ==
              ['None:unassigned'],
              'CAD import no longer unassigned: %d' % import_id)
        names = [s['name'] for s in row.get('import_subcategories', [])]
        guard('0' in names and '20' in names,
              'CAD import layer roster changed id=%d' % import_id)
    return {'blade_ids':list(BLADES), 'housing_ids':list(HOUSING),
            'lens_untouched':PRESERVE_LENS, 'imports_untouched':list(IMPORTS)}


def faces_for_element(element):
    """Count visible physical faces by native MaterialElementId."""
    options = DB.Options()
    options.DetailLevel = DB.ViewDetailLevel.Fine
    options.IncludeNonVisibleObjects = False
    results = {}
    def walk(geometry):
        for item in geometry:
            if isinstance(item, DB.GeometryInstance):
                walk(item.GetInstanceGeometry())
            elif isinstance(item, DB.Solid) and item.Volume > 1e-12:
                for face in item.Faces:
                    n = eid(face.MaterialElementId)
                    results[str(n)] = results.get(str(n), 0) + 1
    walk(element.get_Geometry(options))
    return results


def editable_mat_parameter(element):
    param = element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM)
    if param is None:
        hits = [p for p in element.Parameters
                if unicode(p.Definition.Name).strip().lower() == 'material']
        guard(len(hits) == 1,
              'No unique Material parameter on element id=%d' % eid(element.Id))
        param = hits[0]
    guard(not param.IsReadOnly and str(param.StorageType) == 'ElementId',
          'Material parameter read-only/incorrect storage id=%d' % eid(element.Id))
    return param


def find_generic_asset(app):
    for asset in app.GetAssets(DB.Visual.AssetType.Appearance):
        marker = asset.FindByName('BaseSchema')
        if marker is not None and marker.Value == 'GenericSchema':
            return asset
    raise RuntimeError('GenericSchema appearance preset is unavailable')


def material_with_appearance(doc, app, name, appearance_name, rgb,
                             glossiness, reflectivity_zero, is_metal):
    for material in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        guard(elt_name(material) != name,
              'Source material name collision: '+name)
    asset = DB.AppearanceAssetElement.Create(
        doc, appearance_name, find_generic_asset(app))
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    try:
        editable = scope.Start(asset.Id)
        pairs = [
            ('generic_diffuse','color',rgb),
            ('generic_glossiness','number',glossiness),
            ('generic_reflectivity_at_0deg','number',reflectivity_zero),
            ('generic_reflectivity_at_90deg','number',.78 if is_metal else .42),
            ('generic_transparency','number',0.),
            ('generic_is_metal','bool',is_metal)
        ]
        for key, kind, value in pairs:
            prop = editable.FindByName(key)
            guard(prop is not None, 'Missing required appearance property '+key)
            if prop.NumberOfConnectedProperties:
                prop.RemoveConnectedAsset()
            if kind == 'color':
                prop.SetValueAsColor(DB.Color(*value))
            else:
                prop.Value = value
        scope.Commit(True)
    finally:
        scope.Dispose()
    mat = doc.GetElement(DB.Material.Create(doc, name))
    mat.Color = DB.Color(*rgb)
    mat.Transparency = 0
    mat.AppearanceAssetId = asset.Id
    return mat


def inspect_parts(doc, mode, matids=None):
    present = {}
    for element_id in BLADES+HOUSING+(PRESERVE_LENS,):
        element = doc.GetElement(DB.ElementId(element_id))
        guard(isinstance(element, DB.FreeFormElement),
              'Saved OEM element id is no longer FreeFormElement: %d' % element_id)
        counts = faces_for_element(element)
        expected = (FACE_COUNTS[element_id])
        if element_id == PRESERVE_LENS or mode == 'before':
            guard(sum(counts.values()) == expected and
                  len(counts) == 1 and (list(counts.keys())[0] == '-1'),
                  'Before/edit lens face materials changed id=%d: %s' % (element_id, counts))
        else:
            target_id = matids['blade'] if element_id in BLADES else matids['housing']
            guard(counts == {str(target_id):expected},
                  'R02 target material not on ALL geometry faces id=%d: %s' % (element_id, counts))
        present[str(element_id)] = {'faces':counts, 'face_count':expected}
    return present


def no_existing_output():
    guard(not os.path.lexists(TARGET), 'Candidate R02 output already exists')
    guard(not os.path.lexists(RECEIPT), 'R02 receipt already exists')
    guard(not os.path.lexists(RECEIPT+'.tmp'), 'R02 temp receipt already exists')


def save_receipt(data):
    no = RECEIPT+'.tmp'
    guard(not os.path.lexists(RECEIPT) and not os.path.lexists(no),
          'Build receipt or temp exists; refusing overwrite')
    payload = json.dumps(data, ensure_ascii=True, sort_keys=True, indent=2)
    with open(no,'wb') as stream:
        stream.write(payload.encode('ascii'))
    guard(not os.path.lexists(RECEIPT), 'Build receipt appeared before rename')
    os.rename(no,RECEIPT)


def main():
    app = __revit__.Application
    guard(str(app.VersionNumber) == '2025', 'Revit 2025 required')
    guard(getattr(__revit__, 'ActiveUIDocument', None) is None,
          'Use isolated, document-free pyrevit run')
    no_existing_output()
    for path,digest in ((SOURCE,SOURCE_SHA),(OEM,OEM_SHA),
                        (PROBE,PROBE_SHA),(SWATCH,SWATCH_SHA)):
        guard(os.path.isfile(path) and sha(path).lower() == digest.lower(),
              'Required source missing or SHA256 changed: '+path)
    probe_roles = audit_probe()
    source_before = fingerprint(SOURCE)
    oem_before = fingerprint(OEM)
    probe_before = fingerprint(PROBE)
    swatch_before = fingerprint(SWATCH)
    document = None
    tx = None
    status = 'STARTED'
    details = {}
    try:
        document = app.OpenDocumentFile(SOURCE)
        guard(document.IsFamilyDocument and
              elt_name(document.OwnerFamily.FamilyCategory)=='Lighting Fixtures',
              'Not an OEM Lighting Fixtures family')
        guard(str(document.OwnerFamily.FamilyPlacementType)=='WorkPlaneBased',
              'Unexpected source family hosting')
        guard(len(list(document.GetWarnings()))==0, 'Source family warnings')
        imports = sorted(eid(e.Id) for e in
            DB.FilteredElementCollector(document).OfClass(DB.ImportInstance))
        guard(imports == list(IMPORTS), 'Unexpected CAD import element list')
        details['before'] = inspect_parts(document, 'before')
        tx = DB.Transaction(document, 'R02 partial Smooth SB MB identified parts')
        tx.Start()
        matte = material_with_appearance(document,app,BLACK_NAME,BLACK_ASSET,
            BLACK_RGB,.11,.035,False)
        brass = material_with_appearance(document,app,BRASS_NAME,BRASS_ASSET,
            BRASS_RGB,.58,.48,True)
        matids = {'blade':eid(matte.Id),'housing':eid(brass.Id)}
        details['material_ids'] = matids
        for part_id in BLADES+HOUSING:
            element = document.GetElement(DB.ElementId(part_id))
            parameter = editable_mat_parameter(element)
            assigned = matte if part_id in BLADES else brass
            guard(bool(parameter.Set(assigned.Id)),
                  'Revit rejected material binding id=%d' % part_id)
        document.Regenerate()
        details['after'] = inspect_parts(document, 'after', matids)
        guard(len(list(document.GetWarnings()))==0,
              'Material assignment introduced warnings')
        guard(sorted(eid(e.Id) for e in DB.FilteredElementCollector(
            document).OfClass(DB.ImportInstance)) == list(IMPORTS),
              'Unexpected CAD import count after material assignment')
        guard(tx.Commit()==DB.TransactionStatus.Committed,
              'Revit transaction did not commit')
        tx = None
        options = DB.SaveAsOptions()
        options.OverwriteExistingFile = False
        options.MaximumBackups = 1
        no_existing_output()
        document.SaveAs(TARGET,options)
        document.Close(False)
        document = None

        document = app.OpenDocumentFile(TARGET)
        details['reopened'] = inspect_parts(document,'after',matids)
        guard(len(list(document.GetWarnings()))==0,'Saved candidate warnings')
        document.Close(False)
        document = None
        status = 'PARTIAL_FINISH_SAVED_NATIVE_FACE_BINDINGS_VERIFIED_VISUAL_HOLD'
    finally:
        if tx is not None:
            try:tx.RollBack()
            except Exception:pass
        if document is not None:
            try:document.Close(False)
            except Exception:pass
    protected_unchanged = (fingerprint(SOURCE)==source_before and
                           fingerprint(OEM)==oem_before and
                           fingerprint(PROBE)==probe_before and
                           fingerprint(SWATCH)==swatch_before)
    guard(protected_unchanged,'Original sources changed unexpectedly')
    report = {
        'status':status, 'target':TARGET, 'source':SOURCE,
        'source_sha256':SOURCE_SHA, 'oem_sha256':OEM_SHA,
        'target_sha256':sha(TARGET), 'candidate_bytes':os.path.getsize(TARGET),
        'probe_sha256':PROBE_SHA,'swatch_sha256':SWATCH_SHA,
        'roles':probe_roles,'revit_version':'2025','details':details,
        'no_original_sources_changed':protected_unchanged,
        'release_status':'HOLD_NONBLADES_CAD_IMPORTS_AND_LIGHT_LENS_UNRESOLVED',
        'colors':{'matte_black_rgb_from_official_swatch':BLACK_RGB,
                  'soft_brass_rgb_from_official_swatch':BRASS_RGB,
                  'appearance_numeric_roughness':'PROVISIONAL_NOT_MANUFACTURER_CALIBRATED'},
        'native_independent_qa':'PENDING',
        'official_revit_url':'https://modernforms.com/images/products/REVIT/FR-W2502_REVIT.zip',
        'official_finish_url':'https://modernforms.com/images/finishes/soft_brassmatte_black.jpg',
        'radial_sweep_status':'NOT_REMEASURED_IN_BUILD_NATIVE_QA_REQUIRED',
        'finished_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    }
    save_receipt(report)
    print('SMOOTH_R02 '+status)
    print('CANDIDATE '+TARGET)
    print('RECEIPT '+RECEIPT)


main()
