"""Create the current five-selection SOURCE REVIEW; never a five-RFA release."""
import datetime
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_NAME = 'Belmont_PH_Bedside_5_Selections_SOURCE_REVIEW_NOT_RELEASED_20261017_r03.zip'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(relative, data):
    path = (ROOT / relative).resolve()
    if ROOT not in path.parents:
        raise ValueError('Write outside task root')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding='utf-8')


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8-sig'))


def main():
    target = ROOT / 'release' / ARCHIVE_NAME
    if target.exists():
        raise RuntimeError('No archive overwrite: ' + str(target))
    old = load('MANIFEST.json')
    historical = ROOT / 'qa/HISTORICAL_MANIFEST_R01.json'
    if not historical.exists():
        historical.write_bytes((ROOT / 'MANIFEST.json').read_bytes())
    if old.get('revision') == 'R02':
        write('qa/HISTORICAL_MANIFEST_R02.json', json.dumps(old, indent=2))
    cad = load('qa/SCHNEID_OEM_CAD_REVIEW_R02.json')
    safety = load('qa/NATIVE_READONLY_STATIC_CHECK_R02.json')
    process = load('runner/receipts/process_ownership_r02.json')
    preflight = load('runner/receipts/readonly_preflight_r02_preflight.json')
    byte_report = load('qa/OEM_BYTE_IDENTITY.json')
    for family in old['families']:
        assert sha(Path(family['file'])) == family['original_rfa_sha256']
    assert safety['status'] == 'OFFLINE_SAFETY_AND_COMPILE_PASS_NOT_NATIVE_EXECUTION'
    assert cad['archive_crc'] == 'PASS' and cad['rfa_members'] == 0
    assert not (ROOT / 'qa/native_readonly_r02.json').exists(), 'Reconcile new native result before packaging'
    runtime = {
        'date': '2026-10-17', 'status': 'NATIVE_EXECUTION_BLOCKED_NO_RECOVERY_RECEIPT',
        'previous_crash': old['native_runtime'],
        'existing_revit_process': process,
        'offline_preflight': preflight,
        'native_launches_this_followup': 0, 'active_user_model_changes': 0,
        'native_script_prepared': str(ROOT / 'qa/native_readonly_oem_r02.py'),
        'script_static_safety_status': safety['status'],
        'supported_import_method': 'Revit 2025 Document.Import(path, ImportOptions3DM, View); optional native importer required.',
        'alternative_method_tested': False,
        'unresolved': 'No successful isolated document-free Revit 2025 probe or changed startup recovery evidence available.',
    }
    write('qa/NATIVE_RECOVERY_STATUS_R02.json', json.dumps(runtime, indent=2))
    manifest = dict(old)
    manifest.update({
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'revision': 'R03', 'status': 'REVIEW_NOT_RELEASED',
        'package_kind': 'FIVE_SELECTION_SOURCE_REVIEW_FOUR_OEM_RFAS_PLUS_OFFICIAL_STUCCO_CAD',
        'native_qa_passes': 0, 'native_launches_this_followup': 0,
        'custom_rfa_files': 0, 'unchanged_oem_rfa_files': 4,
        'manufacturer_source_download_count_verified': len(byte_report['sources']) + 1,
        'manufacturer_source_archive_count_verified': sum(
            Path(row['file']).suffix.lower() == '.zip' for row in byte_report['sources']) + 1,
        'native_recovery': runtime,
        'native_readonly_static_check': str(ROOT / 'qa/NATIVE_READONLY_STATIC_CHECK_R02.json'),
        'variant_audit': str(ROOT / 'qa/OEM_VARIANT_RESOLUTION.md'),
        'drive_status': 'NOT_UPLOADED_FULL_NATIVE_AND_VARIANT_QA_REQUIRED',
        'supersedes_for_current_status': str(ROOT / 'release/Belmont_PH_Bedside_5_Selections_SOURCE_REVIEW_NOT_RELEASED_20261017_r02.zip'),
    })
    for family in manifest['families']:
        if family['requested_sku'] == '402401BG-LED' and 'PHOTOMETRY_HOLD' not in family['selection_status']:
            family['selection_status'] += ' PHOTOMETRY_HOLD: saved file names Mina 401214WH-LED, not Malabar.'
    manifest['missing_selection'] = {
        'manufacturer': 'Schneid Studio', 'model': 'Stucco No.2 / Stucco II',
        'requested_sku': 'STUCCO-II-CLAY-UL', 'file': None,
        'status': 'OFFICIAL_CAD_RECOVERED_NO_RFA_IN_19_MEMBER_FACTORY_ARCHIVE_NATIVE_BUILD_BLOCKED',
        'source_archive': cad['archive'], 'source_archive_sha256': cad['archive_sha256'],
        'official_no2_cad': cad['oem_cad_sources'],
        'corrected_source_dimensions_mm': cad['corrected_manufacturer_dimensions_mm'],
        'offline_review': str(ROOT / 'qa/SCHNEID_OEM_CAD_REVIEW_R02.json'),
        'body_and_rose_native_measurement': 'NOT_RUN', 'native_lighting_source': 'NOT_BUILT',
        'ul_variant': cad['ul_variant'],
        'next_action': 'After isolated runtime recovery, use exact factory 3DM/STEP geometry for the ONLY new native family wrapper, then reopen/measure/ceiling/emitter/material/visual QA.',
    }
    write('MANIFEST.json', json.dumps(manifest, indent=2, ensure_ascii=False))

    lines = [
        '# Belmont PH bedside pendants — R03 SOURCE REVIEW, NOT RELEASED', '',
        'This review covers all five selections using four untouched OEM RFAs plus official Schneid No.2 CAD. '
        'It is not a completed five-RFA package. No family passed native Revit 2025 QA in this task and no Stucco RFA was created.', '',
        'Root: `' + str(ROOT) + '`.', '',
        '| Selection | Included original family / CAD | Current hold |',
        '| --- | --- | --- |',
    ]
    for family in manifest['families']:
        lines.append('| ' + family['requested_sku'] + ' | `' + family['file'] + '` | ' + family['selection_status'] + ' |')
    lines += [
        '| STUCCO-II-CLAY-UL | `' + str(ROOT / 'sources/premium/schneid_official_no2')
        + '` | Five original CAD formats; no RFA in factory archive; native import/build/QA pending. |', '',
        'Schneid dimensions are corrected from the preserved manufacturer PDF: ceramic body D105 × H265 mm, '
        'ceiling rose D140 × H140 mm. Earlier 100 mm body/105 × 125 mm rose notes mixed No.1 and No.2. '
        'The OEM STL whole assembly is approximately 139.934 × 139.867 × 1309.000 source units, including the '
        'factory default suspension and bulb; this is not a body measurement. STEP explicitly declares millimetres. '
        'STL units are inferred from that same-package STEP and physical component sizes.', '',
        'The official 19-member Schneid ZIP has no RFA. All five No.2 CAD extracts were re-compared byte-for-byte '
        'with that archive and their recorded SHA-256. The full 186,260,124-byte archive remains intact locally at `'
        + cad['archive'] + '`. This review ZIP includes the five exact No.2 files and provenance receipt, '
        'not the unrelated No.1/No.3 CAD or the complete multi-product archive.', '',
        'Factory STL front/oblique previews were visually inspected: they show the No.2 paired sculpted pieces, '
        'suspension and exposed bulb. Neutral schematic shading does not establish the Clay finish, E26 UL socket, '
        'photometry, or a native solid. The STL has many disconnected topological pieces; they are not semantic CAD parts. '
        'Prefer the original Rhino/STEP for native import instead of manufacturing new geometry from those triangles.', '',
        'Native recovery is unresolved. The previous probe crashed before its script. An existing Revit process '
        '(PID 11796, started 01:54 local, parent explorer.exe) is not owned by this worker; its document state is unknown. '
        'It was not attached to or stopped. No new resource-heavy launch was attempted. Native QA preparation and '
        'process evidence are described in `' + str(ROOT / 'runner/RECOVERY_COORDINATION_R02.md') + '`.', '',
        'The prepared read-only validator requires a newly owned, document-free Revit 2025 process. It never saves '
        'OEM RFAs, hashes originals before/after, creates real ceiling hosts in disposable unsaved projects, and '
        'records types, materials, physical solid bounds and true LightFamily sources. It has passed compilation '
        'and offline safety checks only. Real native API calls and visual/source fidelity gates remain untested.', '',
        'Native type/geometry/material/host/light checks, exact variant verification and product visual approval '
        'must pass before release. Jarvis BG and Marset Cream 0–10V are absent from saved OEM types. Malabar has '
        'a probable name typo, unverified plating and a saved IES filename for a different fixture. '
        'No type was renamed, substituted, repainted or rebuilt to hide these holds.', '',
        'No user Revit model or external settings were changed. No Drive upload was attempted because full QA '
        'has not passed. R01/R02 archives are retained as superseded source-review history; R03 corrects '
        'the metadata count to distinguish 19 source downloads from 11 ZIP archives.', '',
        'Selection/provenance: `' + str(ROOT / 'SOURCE_SELECTION.md') + '`.',
        'Machine manifest: `' + str(ROOT / 'MANIFEST.json') + '`.',
        'Independent source review: `' + str(ROOT / 'qa/SCHNEID_OEM_CAD_REVIEW_R02.json') + '`.',
        'Independent type audit: `' + str(ROOT / 'qa/OEM_VARIANT_RESOLUTION.md') + '`.', '',
        'Offline reproduction:', '', '```powershell',
        "python.exe '" + str(ROOT / 'scripts/extract_oem_unchanged.py') + "'",
        "python.exe '" + str(ROOT / 'scripts/inspect_saved_oem_metadata.py') + "'",
        "python.exe '" + str(ROOT / 'scripts/check_native_readonly_safety_r02.py') + "'",
        "python.exe '" + str(ROOT / 'scripts/verify_source_review_r02.py') + "'", '```', '',
        'The factory STL preview script additionally uses locally available trimesh/numpy/Pillow/pypdf. '
        'Native Revit scripts are preparation artifacts, not completed RFAs. Source paths refer to this task root; '
        'internal ZIP members retain their normal archive-relative names.', '',
    ]
    write('README.md', '\n'.join(lines))
    selection = [
        '# Current source selection and provenance — R03, REVIEW_NOT_RELEASED', '',
        'All four OEM RFA copies retain original archive member names and bytes. '
        'Manufacturer source/type presence is separate from exact finish, voltage/dimming, native scale and host QA.', '',
    ]
    for family in manifest['families']:
        selection += [
            '## ' + family['requested_sku'], '',
            'Original family: `' + family['file'] + '`.',
            'Original/package SHA-256: `' + family['original_rfa_sha256'] + '`.',
            'Archive: `' + family['archive_file'] + '`.',
            'Archive SHA-256: `' + family['archive_sha256'] + '`.',
            'Factory download URL: ' + family['source_url'], '',
            'Stored types: ' + ', '.join('`' + x + '`' for x in family['stored_type_names']) + '.', '',
            family['selection_status'], '',
            'Decision: include unchanged source only; no exact selected-variant approval or native technical pass.', '',
        ]
    selection += [
        '## STUCCO-II-CLAY-UL', '',
        'Official source: https://schneidstudio.com/stucco-collection ; '
        'https://schneidstudio.com/s/STUCCO_DataSheet.pdf .', '',
        'Recovered full source archive: `' + cad['archive'] + '`; SHA-256 `' + cad['archive_sha256'] + '`.',
        '19 entries, all source CRCs pass, zero RFA members. The earlier bounded download failure is resolved '
        'by the source worker’s one-time full acquisition; original failed-download manifest is retained as history.', '',
        'Confirmed No.2 manufacturer dimensions: body D105 × H265 mm; ceiling rose D140 × H140 mm. '
        'The sheet’s E27/220–240V specification is not proof of the selected US E26 UL variant. '
        'CAD includes bulb and suspension; exact UL internal hardware, clay rendering and lamp data remain unverified.', '',
    ]
    for source in cad['oem_cad_sources']:
        selection += ['Original CAD: `' + source['file'] + '`; SHA-256 `' + source['sha256'] + '`.', '']
    selection += [
        'Decision: preserve source geometry; build only a new Stucco native family wrapper after runtime recovery. '
        'Use supported Rhino/STEP import and verify actual source units, geometry, materials, emitter and ceiling placement. '
        'No synthetic replacement geometry or empty RFA is delivered.', '',
        'Native status: `' + str(ROOT / 'qa/NATIVE_RECOVERY_STATUS_R02.json') + '`.',
        'Detailed type/finish/photometry audit: `' + str(ROOT / 'qa/OEM_VARIANT_RESOLUTION.md') + '`.',
        'Source CAD measurements/previews: `' + str(ROOT / 'qa/SCHNEID_OEM_CAD_REVIEW_R02.json') + '`.', '',
    ]
    write('SOURCE_SELECTION.md', '\n'.join(selection))
    allowed = [Path(row['file']) for row in byte_report['sources']]
    allowed += [Path(row['file']) for row in manifest['families']]
    allowed += [Path(row['file']) for row in load('qa/SELECTED_COMPANION_IDENTITY.json')]
    allowed += [Path(row['file']) for row in cad['oem_cad_sources']]
    allowed += [Path(path) for row in load('qa/OEM_STORED_METADATA.json') for path in row['stored_preview_files']]
    allowed += [Path(path) for path in cad['previews']]
    extra = (
        'README.md', 'MANIFEST.json', 'SOURCE_SELECTION.md',
        'qa/OEM_BYTE_IDENTITY.json', 'qa/OEM_STORED_METADATA.json', 'qa/SELECTED_COMPANION_IDENTITY.json',
        'qa/OEM_VARIANT_RESOLUTION.md', 'qa/SCHNEID_OEM_CAD_REVIEW_R02.json',
        'qa/SCHNEID_DATASHEET_TEXT_R02.txt', 'qa/NATIVE_READONLY_STATIC_CHECK_R02.json',
        'qa/NATIVE_RECOVERY_STATUS_R02.json', 'qa/NATIVE_RUNTIME_HOLD.json',
        'qa/native_readonly_oem_r02.py',
        'runner/launch_readonly_r02.py', 'runner/inspect_process_ownership_r02.py',
        'runner/RECOVERY_COORDINATION_R02.md',
        'runner/receipts/readonly_preflight_r02_preflight.json', 'runner/receipts/process_ownership_r02.json',
        'runner/receipts/probe_launcher_r01.json',
        'sources/kuzco/SOURCE_MANIFEST.json', 'sources/premium/OEM_SOURCE_MANIFEST.json',
        'sources/premium/schneid_dropbox_probe/SCHNEID_OEM_ARCHIVE_RECEIPT.json',
        'sources/premium/schneid_dropbox_probe/SCHNEID_STUCCO_OEM_DISCOVERY.md',
        'sources/premium/schneid_dropbox_probe/acquire_oem_no2.py',
        'scripts/extract_oem_unchanged.py', 'scripts/inspect_saved_oem_metadata.py',
        'scripts/review_schneid_oem_cad_r02.py', 'scripts/check_native_readonly_safety_r02.py',
        'scripts/package_source_review_r02.py', 'scripts/verify_source_review_r02.py',
    )
    allowed += [ROOT / relative for relative in extra]
    assert len(allowed) == len(set(allowed))
    inventory = []
    for path in allowed:
        assert ROOT in path.resolve().parents and path.is_file(), str(path)
        inventory.append({'file': str(path), 'member': path.relative_to(ROOT).as_posix(),
                          'bytes': path.stat().st_size, 'sha256': sha(path)})
    write('qa/PACKAGE_INVENTORY_R02.json', json.dumps(inventory, indent=2))
    allowed.append(ROOT / 'qa/PACKAGE_INVENTORY_R02.json')
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in allowed:
            archive.write(path, path.relative_to(ROOT).as_posix())
    print(json.dumps({'archive': str(target), 'bytes': target.stat().st_size,
                      'sha256': sha(target), 'files': len(allowed),
                      'status': 'SOURCE_REVIEW_NOT_RELEASED'}, indent=2))


if __name__ == '__main__':
    main()
