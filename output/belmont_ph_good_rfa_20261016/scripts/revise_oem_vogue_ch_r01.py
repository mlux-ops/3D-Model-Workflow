# -*- coding: utf-8 -*-
"""Source-guarded Revit 2025 finish candidate for Vogue WS-3127-CH.

This script requires the existing Belmont native batch runner globals:
    APP, DB, JOB, TARGET_RFA, SOURCE_RFA, progress(stage, detail), result

It reads an OEM-source or existing QA copy of WS-3127, changes MATERIAL
APPEARANCES only in the opened family document, and saves a NEW RFA.
It neither overwrites nor saves the input RFA or any .rvt project.

Basis: 651 Belmont QA oem_qa_r02.json, 2026-10-16.
    Vogue family metal: 336 faces assigned material "青铜色，建筑"
    Vogue diffuser:      52 faces assigned material "Diffuser-01"
Both are deterministic in the accepted OEM input SHA256 records below.

The manufacturer's model and finish code are exact; RGB, gloss, reflection,
and glass translucency are PHOTO/FINISH INTERPRETATIONS and must be visually
reviewed with a real manufacturer sample. No new IES or electrical connector
is created. Existing luminaire geometry and source photometry are retained.

Other fixtures on this task remain HELD: Kuzco PD3106-BG has no demonstrated
brushed-gold metal face binding; Modern Forms Smooth FR-W2502-52L-SB/MB has
unnamed type/import-heavy geometry with no housing-vs-blade binding.
"""

import os
import hashlib
import traceback

SOURCE_MODELS = {
    # Native OEM source copied into the project from manufacturer download.
    'bf4bd0f22c65eec080fc8e022c8fb817f526903408d17bbe52f752d3f4fab155',
    # Revit-2025 saved project copy from independent native QA R02.
    '1dcb1673b31ff277f9482bc5ded7a244922598f782196d2d2804c773768db4df',
}
MANUFACTURER = 'Modern Forms'
MODEL = 'WS-3127-CH'
OEM_FACE_METAL = u'\u9752\u94dc\u8272\uff0c\u5efa\u7b51'
OEM_FACE_GLASS = 'Diffuser-01'
CHROME_RGB = (207, 211, 216)
OPAL_RGB = (245, 244, 239)
SOURCE_WEB = 'https://modernforms.com/product/vogue/'
SOURCE_SPEC = 'https://modernforms.com/dynamic-specsheet/?download=specs5&ppid=1546'
REVIEW_NOTE = (
    'Original source material named architectural bronze / patina drives '
    '336 metal faces. Converted appearance to HIGH-REFLECTIVITY CHROME '
    'candidate for scheduled WS-3127-CH. Original Diffuser-01 drives '
    '52 faces; converted appearance to approximated etched opal glass. '
    'Numerical RGB/gloss/transparency are visual estimates, not OEM shaders. '
    'All original geometry, placements, photometric source, and electrical '
    'content remain as supplied by the OEM. A native readback, glass/metal '
    'visual review, and dimension review are needed before release.'
)

def digest(filename):
    h = hashlib.sha256()
    with open(filename, 'rb') as fp:
        while True:
            chunk = fp.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def members(elems):
    for e in elems:
        if isinstance(e, DB.Solid) and e.Volume > 1e-12:
            yield e
        elif isinstance(e, DB.GeometryInstance):
            for s in members(e.GetInstanceGeometry()):
                yield s

def count_faces(doc, target_mats):
    names_by_id = dict((int(mat.Id.Value), key) for key, mat in target_mats.items())
    counts = dict((key, 0) for key in target_mats)
    options = DB.Options()
    options.DetailLevel = DB.ViewDetailLevel.Fine
    for element in DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement):
        for solid in members(element.get_Geometry(options)):
            for face in solid.Faces:
                mid = face.MaterialElementId
                if mid is not None:
                    key = names_by_id.get(int(mid.Value))
                    if key is not None:
                        counts[key] += 1
    return counts

def get_generic():
    for a in APP.GetAssets(DB.Visual.AssetType.Appearance):
        marker = a.FindByName('BaseSchema')
        if marker is not None and marker.Value == 'GenericSchema':
            return a
    raise RuntimeError('Revit GenericSchema appearance template missing')

def configure_asset(doc, name, rgb, gloss, reflect0, reflect90, transparent):
    base = get_generic()
    entry = DB.AppearanceAssetElement.Create(doc, name, base)
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    try:
        asset = scope.Start(entry.Id)
        props = [
            ('generic_diffuse', 'color', rgb),
            ('generic_glossiness', 'scalar', float(gloss)),
            ('generic_reflectivity_at_0deg', 'scalar', float(reflect0)),
            ('generic_reflectivity_at_90deg', 'scalar', float(reflect90)),
            ('generic_transparency', 'scalar', float(transparent)),
        ]
        for key, typ, val in props:
            prop = asset.FindByName(key)
            if prop is None:
                raise RuntimeError('Missing expected Revit Generic appearance property: ' + key)
            if prop.NumberOfConnectedProperties:
                prop.RemoveConnectedAsset()
            if typ == 'color':
                prop.SetValueAsColor(DB.Color(*val))
            else:
                prop.Value = val
        scope.Commit(True)
    finally:
        scope.Dispose()
    return entry

def replace_existing_material(doc, mat, new_name, rgb, trans, gloss, refl0, refl90):
    # Editing the existing material is essential. Its ElementId is already
    # referenced by native geometry faces; a newly created unassigned material
    # would change nothing visible.
    fresh = configure_asset(doc, new_name + ' APPEARANCE', rgb, gloss, refl0, refl90, trans / 100.0)
    mat.Color = DB.Color(*rgb)
    mat.Transparency = int(trans)
    mat.AppearanceAssetId = fresh.Id
    mat.Name = new_name
    return {'name': mat.Name, 'rgb': list(rgb), 'transparency_percent': int(trans),
            'appearance_name': fresh.Name, 'material_id': int(mat.Id.Value)}

def put_family_metadata(doc):
    fm = doc.FamilyManager
    types = list(fm.Types)
    if len(types) != 1:
        raise RuntimeError('Expected one OEM family type; found ' + str(len(types)))
    fm.CurrentType = types[0]
    fm.RenameCurrentType(MODEL)
    for bip, value in [
        (DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, MANUFACTURER),
        (DB.BuiltInParameter.ALL_MODEL_MODEL, MODEL),
        (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,
         'Vogue 27in LED vanity/sconce; Chrome / mouth-blown etched opal glass; candidate visual finish'),
    ]:
        p = fm.get_Parameter(bip)
        if p is not None and not p.IsReadOnly:
            fm.Set(p, value)
    note = None
    for p in fm.Parameters:
        if p.Definition.Name == 'PH GOOD Finish Review Notes':
            note = p
            break
    if note is None:
        note = fm.AddParameter('PH GOOD Finish Review Notes',
                               DB.GroupTypeId.IdentityData,
                               DB.SpecTypeId.String.Text, False)
    fm.Set(note, REVIEW_NOTE + ' Sources: ' + SOURCE_WEB + ' ; ' + SOURCE_SPEC)

source = SOURCE_RFA
target = TARGET_RFA
if source is None or target is None:
    raise RuntimeError('Both SOURCE_RFA and TARGET_RFA are required')
source = os.path.abspath(source)
target = os.path.abspath(target)
if not os.path.isfile(source):
    raise RuntimeError('OEM/source family absent: ' + source)
if os.path.normcase(source) == os.path.normcase(target):
    raise RuntimeError('Refusing to overwrite OEM/source family')
if os.path.exists(target):
    raise RuntimeError('Target candidate already exists; choose a new revision')
low_target = os.path.normcase(target)
if 'belmont_ph_good_rfa_20261016' not in low_target:
    raise RuntimeError('Target outside authorized Belmont candidate package')
if ('\\sources\\oem\\' in low_target) or ('/sources/oem/' in low_target):
    raise RuntimeError('Cannot write candidate into extracted OEM source directory')
if str(APP.VersionNumber) != '2025':
    raise RuntimeError('Native Revit 2025 required')
before_digest = digest(source)
if before_digest not in SOURCE_MODELS:
    raise RuntimeError('Input RFA hash differs from independent native QA R02. Reaudit before editing: ' + before_digest)

progress('vogue_ch_preflight', {'source': source, 'source_sha256': before_digest, 'target': target})
doc = None
reopened = None
tx = None
try:
    doc = APP.OpenDocumentFile(source)
    if not doc.IsFamilyDocument:
        raise RuntimeError('Input is not a Revit family')
    if doc.OwnerFamily.FamilyCategory.Name != 'Lighting Fixtures':
        raise RuntimeError('Input family category unexpectedly changed')
    before_mats = dict((m.Name, m)
                       for m in DB.FilteredElementCollector(doc).OfClass(DB.Material))
    for required in (OEM_FACE_METAL, OEM_FACE_GLASS):
        if required not in before_mats:
            raise RuntimeError('OEM material mapping changed, expected: '+required)
    target_mats = {'metal': before_mats[OEM_FACE_METAL], 'diffuser': before_mats[OEM_FACE_GLASS]}
    original_face_counts = count_faces(doc, target_mats)
    if original_face_counts != {'metal': 336, 'diffuser': 52}:
        raise RuntimeError('Material-face assignment differs from independent QA: '+str(original_face_counts))

    tx = DB.Transaction(doc, 'PH GOOD Vogue exact CH finish candidate')
    tx.Start()
    outcome_metal = replace_existing_material(
        doc, target_mats['metal'], 'PHGOOD_VOGUE_CH_CHROME', CHROME_RGB,
        trans=0, gloss=.92, refl0=.80, refl90=.95
    )
    outcome_opal = replace_existing_material(
        doc, target_mats['diffuser'], 'PHGOOD_VOGUE_MOUTH_BLOWN_OPAL',
        OPAL_RGB, trans=14, gloss=.37, refl0=.12, refl90=.24
    )
    put_family_metadata(doc)
    doc.Regenerate()
    changed_faces = count_faces(doc, target_mats)
    if changed_faces != original_face_counts:
        raise RuntimeError('Material-face assignment changed during recolor')
    in_memory_warnings = [w.GetDescriptionText() for w in doc.GetWarnings()]
    if in_memory_warnings:
        raise RuntimeError('Candidate contains Revit warnings: ' + repr(in_memory_warnings))
    tx.Commit()
    tx = None

    if not os.path.isdir(os.path.dirname(target)):
        os.makedirs(os.path.dirname(target))
    opt = DB.SaveAsOptions()
    opt.OverwriteExistingFile = False
    opt.MaximumBackups = 1
    doc.SaveAs(target, opt)
    doc.Close(False)
    doc = None

    # This readback is part of any FUTURE native run, not executed by this
    # source-only deliverable. It checks saved material values/geometry ids.
    reopened = APP.OpenDocumentFile(target)
    saved_mats = dict((m.Name, m)
                      for m in DB.FilteredElementCollector(reopened).OfClass(DB.Material))
    for name in ('PHGOOD_VOGUE_CH_CHROME', 'PHGOOD_VOGUE_MOUTH_BLOWN_OPAL'):
        if name not in saved_mats:
            raise RuntimeError('Candidate material not saved: ' + name)
    saved_counts = count_faces(reopened, {
        'metal': saved_mats['PHGOOD_VOGUE_CH_CHROME'],
        'diffuser': saved_mats['PHGOOD_VOGUE_MOUTH_BLOWN_OPAL'],
    })
    if saved_counts != original_face_counts:
        raise RuntimeError('Saved candidate geometry material faces changed: '+str(saved_counts))
    if reopened.FamilyManager.CurrentType.Name != MODEL:
        raise RuntimeError('Saved OEM finish family type differs from selected model')
    saved_warnings = [w.GetDescriptionText() for w in reopened.GetWarnings()]
    if saved_warnings:
        raise RuntimeError('Saved candidate family has Revit warnings: '+repr(saved_warnings))
    reopened.Close(False)
    reopened = None
    source_after = digest(source)
    if source_after != before_digest:
        raise RuntimeError('OEM source hash changed unexpectedly')
    result.update({
        'model': MODEL,
        'source_rfa': source,
        'source_sha256_before_after': source_after,
        'candidate_rfa': target,
        'candidate_sha256': digest(target),
        'category': 'Lighting Fixtures',
        'source_binding_face_counts': original_face_counts,
        'saved_candidate_face_counts': saved_counts,
        'hardware': outcome_metal,
        'glass': outcome_opal,
        'manufacturer_finish_code': 'CH / Chrome',
        'manufacturer_glass': 'mouth-blown etched opal',
        'manufacturer_source_urls': [SOURCE_WEB, SOURCE_SPEC],
        'finish_rendition': 'VISUAL_APPROXIMATION_SOURCE_FINISH_EXACT',
        'native_qa_stage': 'SAVED_AND_REOPENED_PENDING_FULL_GEOMETRY_VISUAL_CHECKS',
        'geometry_modified': False,
        'ies_or_connector_modified': False,
    })
    progress('vogue_ch_saved_native_finish_candidate', {'candidate': target})
finally:
    if tx is not None:
        try:
            tx.RollBack()
        except Exception:
            pass
    for document in (reopened, doc):
        if document is not None:
            try:
                document.Close(False)
            except Exception:
                pass
