"""Build an explicit allow-list archive of source-verified, unchanged OEM RFAs.

This script cannot release construction-ready content or upload to Drive. It
records native QA holds rather than promoting offline metadata to native tests.
"""
import datetime
import hashlib
import json
from pathlib import Path
import zipfile

from extract_oem_unchanged import ROOT, load, out_path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(parts, value):
    out_path(*parts).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


def main():
    byte_report = load(ROOT / 'qa/OEM_BYTE_IDENTITY.json')
    stored = load(ROOT / 'qa/OEM_STORED_METADATA.json')
    by_path = {x['file']: x for x in stored}
    note = {
        '41411-BG': 'FINISH_HOLD: stored types BK, BN, CH, VB and WH; BG absent. Do not substitute VB for BG.',
        '402401BG-LED': 'FINISH_HOLD: literal saved type 4024014BG-LED contains an extra 4; actual metal/optic assignments unverified.',
        '494502M-GD': 'STORED_TYPE_MATCH: exact 494502M-GD with 494502_GD_FINISH; native geometry/finish QA pending.',
        'A691-474-37-27K': 'VARIANT_HOLD: 30 legacy types; no exact requested SKU, no Cream material or 0-10V type. '
                            '13 cm types show 13.5 cm diameter, Triac or 24V, White/Blue/Green/Amber/Pink; '
                            'stored canopy 4.8 cm diameter x 13.4 cm height differs from current US 0-10V canopy.',
    }
    native_log = ROOT / 'temp/606c5606-70b2-4142-8856-4d54aa2cb7e6/journal.0001.txt'
    journal = native_log.read_text(encoding='utf-8', errors='replace')
    assert 'ExceptionCode=0xe06d7363' in journal
    assert 'unrecoverable error' in journal.lower()
    assert not (ROOT / 'runner/receipts/probe_native.json').exists()
    runtime = {
        'status': 'HOLD_STARTUP_CRASH_BEFORE_PROBE', 'revit_build': '2025.4.5 20260410_1515(x64)',
        'observed_exception': '0xe06d7363', 'observed_journal_local_time': '2026-10-17 01:19:15.053',
        'timezone': 'America/Chicago', 'cause': 'UNKNOWN',
        'last_verified_stage': 'Native startup; loadAllDB completed; exception before pyRevit command.',
        'probe_receipt_exists': False, 'identical_launch_retried': False,
        'prior_launcher_receipt': str(ROOT / 'runner/receipts/probe_launcher_r01.json'),
        'prior_launcher_receipt_sha256': digest(ROOT / 'runner/receipts/probe_launcher_r01.json'),
        'journal': str(native_log), 'journal_sha256': digest(native_log),
        'visible_process_check': 'Get-Process at approximately 01:20 local: no Revit/pyrevit processes visible, including recorded CLI PID 49704.',
        'cim_inspection': 'Access denied; Get-Process fallback used.',
        'active_user_model': 'No user document opened, edited, saved or closed by this execution.',
        'native_open_types_materials_geometry_ceiling_light_visual': 'ALL_PENDING',
        'recovery': 'Clear isolated Revit startup failure before one serialized native QA/build run; do not route to active user model.',
    }
    write_json(('qa', 'NATIVE_RUNTIME_HOLD.json'), runtime)

    entries = []
    for family in byte_report['families']:
        metadata = by_path[family['file']]
        assert digest(Path(family['file'])) == family['original_rfa_sha256']
        entries.append(dict(family,
                            stored_product_version=metadata.get('saved_product_version'),
                            stored_category=metadata.get('saved_category'),
                            stored_host=metadata.get('saved_host'),
                            stored_type_names=[t['title']['value'] for t in metadata['saved_types']],
                            stored_metadata_scope='OFFLINE_NOT_NATIVE_QA',
                            selection_status=note[family['requested_sku']]))
    missing = dict(byte_report['missing_selection'])
    missing.update({
        'file': None, 'native_lighting_source': None,
        'source_drawing': str(ROOT / 'sources/premium/originals/SCHNEID_STUCCO_DataSheet.pdf'),
        'source_drawing_sha256': digest(ROOT / 'sources/premium/originals/SCHNEID_STUCCO_DataSheet.pdf'),
        'build_status': 'NOT_BUILT_ISOLATED_NATIVE_RUNTIME_BLOCKED',
        'next_step': 'Finish OEM library inspection; if no usable model exists, build only Stucco II in an isolated Revit 2025 process.',
    })
    manifest = {
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'task_root': str(ROOT), 'status': 'REVIEW_NOT_RELEASED',
        'requested_selections': 5, 'unchanged_oem_rfa_files': 4,
        'custom_rfa_files': 0, 'native_qa_passes': 0,
        'rfa_modification_count': 0, 'families': entries,
        'missing_selection': missing, 'native_runtime': runtime,
        'drive_status': 'NOT_UPLOADED_FULL_PACKAGE_QA_REQUIRED',
        'prime_coordination': 'Connector agents status denied: MCP tool requires approval but policy is never. Local handoff provided.',
    }
    write_json(('MANIFEST.json',), manifest)

    lines = [
        '# Belmont PH bedside pendants — REVIEW_NOT_RELEASED', '',
        'Four original manufacturer RFAs are included unchanged. This is a source review package, '
        'not a completed five-selection family delivery. Native Revit 2025 QA has not run. '
        'No fixture was recreated and no original RFA was saved by Revit.', '',
        'Package root: `' + str(ROOT) + '`.', '',
        'Read the source-selection report at `' + str(ROOT / 'SOURCE_SELECTION.md') + '` '
        'and machine-readable manifest at `' + str(ROOT / 'MANIFEST.json') + '`.', '',
        '| Requested selection | Original family copy | Status |',
        '| --- | --- | --- |',
    ]
    for family in entries:
        lines.append('| ' + family['requested_sku'] + ' | `' + family['file'] + '` | '
                     + family['selection_status'] + ' |')
    lines += [
        '| STUCCO-II-CLAY-UL | No RFA | OEM library inspection incomplete; custom build blocked by isolated Revit startup crash. |', '',
        'Use these as preserved OEM sources for review. The three Kuzco families have stored ceiling-host metadata; '
        'Marset has stored face-host metadata. None has been placed in a disposable Revit 2025 project in this task. '
        'All four report Revit 2019 in their saved metadata; opening/upgrading in 2025 remains untested.', '',
        'Jarvis BG is absent from saved types. Malabar gold needs inspection. Milca Gold has matching stored type/material '
        'metadata. Marset Cream 0–10V is not among the 30 saved legacy types. No alternate type is approved as a substitute.', '',
        'Native checks still required: open in Revit 2025, read actual types/material assignments, measure instantiated '
        'body/canopy/cord separately, place each on its real ceiling/face host in a disposable project, verify native '
        'light types and any external assets, inspect warnings, and compare front/oblique views against manufacturer sources. '
        'Do not test in the active Belmont model. Changes to OEM families would require separate explicit scope; these copies stay unchanged.', '',
        'The previous isolated probe crashed before its script, at 01:19:15 local. '
        'Evidence: `' + str(ROOT / 'qa/NATIVE_RUNTIME_HOLD.json') + '`. No duplicate launch was made. '
        'The crash cause is unknown.', '',
        'Schneid source: `' + str(ROOT / 'sources/premium/originals/SCHNEID_STUCCO_DataSheet.pdf') + '`. '
        'Manufacturer-linked 186,260,124-byte Dropbox library was not downloaded because its size exceeded the research '
        'script’s 60 MiB per-file cap. This does not prove an OEM model is unavailable. If discovery finds none, '
        'build only Stucco II from its drawing after the isolated native runtime works.', '',
        'Source archive CRC, download sizes/SHA-256, RFA byte identity and compound-file streams pass offline checks. '
        'Stored thumbnails were inspected; the tiny Kuzco thumbnails show host/reference geometry and are insufficient '
        'for product visual approval. The Marset thumbnail shows a suspended globe but cannot establish its colour/variant.', '',
        'Companion source archives include drawings, CAD and photometry. They are preserved research sources; no IES '
        'was bound or certified as the selected variant. Marset’s recovered 13 cm off-white photometry is not an exact '
        'Cream 0–10V match. Jarvis/Milca lamp photometry depends on the selected GU10 bulb.', '',
        'No Drive upload was attempted: the user requires complete package QA first. '
        'No active user Revit document was modified. No file outside the workspace was changed by this execution.', '',
        'Reproduce OEM extraction with:', '',
        '```powershell',
        "python.exe '" + str(ROOT / 'scripts/extract_oem_unchanged.py') + "'",
        "python.exe '" + str(ROOT / 'scripts/inspect_saved_oem_metadata.py') + "'", '```', '',
        'The extraction script refuses a conflicting existing family and independently rechecks each original archive member. '
        'The metadata script reads saved PartAtom XML and stored PNG streams; it does not open Revit.', '',
        'Archive contents use ZIP member names internally. Every local path in this handoff refers to the original task location. '
        'After moving the package, use its extracted root when running the scripts; they derive their root from their own location.', '',
    ]
    out_path('README.md').write_text('\n'.join(lines), encoding='utf-8')

    selection = [
        '# Source selection and provenance — REVIEW_NOT_RELEASED', '',
        'This report combines preserved manufacturer downloads with the completed source-worker handoff. '
        'Offline saved metadata is evidence about archive content, not evidence of live Revit behavior.', '',
        '| Selection | Official product | Dimensions and model caveat |',
        '| --- | --- | --- |',
        '| Jarvis 41411-BG | https://kuzcolighting.com/products/jarvis-41411-kuzco | Body D2.75 × H12.625 in; canopy D4.75 × H0.25 in. Clear glass and socket housing must remain distinct; GU10 lamp not included. |',
        '| Malabar 402401BG-LED | https://kuzcolighting.com/products/malabar-402401-led-kuzco | Body D3 × H9.5 in; canopy D4.75 × H0.375 in; 6W integrated, 3000K. Clear exterior/frosted interior acrylic; exact BG IES is in source archive, not bound here. |',
        '| Milca 494502M-GD | https://kuzcolighting.com/products/milca-494502m-kuzco | Body D2.375 × H10.875 in; canopy D4.75 × H0.375 in. Gold sliced shade and black braided cable; GU10 lamp not included. |',
        '| Dipping Light 13 Cream A691-474-37-27K | https://www.marset.com/usa/indoor-lighting/pendant-light-fixtures/dipping-light-pendant/ | Current USA sheet: 5.3 in globe; 0–10V canopy D4.3 × H1.8 in, 6W, 2700K. Legacy RFA canopy/type/colour differs; exact type not established. |',
        '| Stucco II Clay UL STUCCO-II-CLAY-UL | https://schneidstudio.com/shop/p/stucco-lamp-no2 | Ceramic body D100 × H265 mm; rose D105 × H125 mm, 2.5m cord. UL retailer E26 variant differs from manufacturer EU E27. No source geometry manufactured in this task. |', '',
        'Printed source dimensions above are acceptance targets, not measurements of the RFAs. '
        'Suspension/overall drop is separate from body height and must be verified natively.', '',
    ]
    for family in entries:
        selection += [
            '## ' + family['manufacturer'] + ' ' + family['selection'], '',
            'Requested SKU: `' + family['requested_sku'] + '`.', '',
            'Preserved archive: `' + family['archive_file'] + '`.',
            'Download URL: ' + family['source_url'],
            'Archive SHA-256: `' + family['archive_sha256'] + '`.', '',
            'Original standalone family: `' + family['file'] + '`.',
            'Original and packaged RFA SHA-256: `' + family['original_rfa_sha256'] + '`.',
            'Byte count: ' + str(family['bytes']) + '; exact archive-member name is recorded in the JSON manifest.', '',
            'Stored metadata: product version ' + str(family['stored_product_version']) + ', category '
            + str(family['stored_category']) + ', host ' + str(family['stored_host']) + '.',
            'Stored type names: ' + ', '.join('`' + x + '`' for x in family['stored_type_names']) + '.', '',
            family['selection_status'], '',
            'Decision: retain unchanged OEM bytes; native type/finish/scale/placement/light/visual gates remain pending.', '',
        ]
    selection += [
        '## Schneid discovery boundary and only potential new build', '',
        'No exact Stucco II OEM RFA was established in the researched/downloaded sources. '
        'The manufacturer-linked Dropbox library remains uninspected: '
        'https://www.dropbox.com/scl/fo/ilg9k5nqeb6od7xbihltv/AJhqNQ6n2bWNgEzoa700D-0?rlkey=ra335kifa8h4anjl5kk6j8yf5&dl=0 . '
        'The source worker’s handoff describes a 120MB cap; the actual preserved downloader enforces 60MiB per file. '
        'Its manifest records the 186260124-byte response as rejected. No large download was repeated.', '',
        'Source drawing: `' + missing['source_drawing'] + '`; SHA-256 `' + missing['source_drawing_sha256'] + '`.', '',
        'A custom Stucco II RFA was not built because native Revit startup is blocked. Do not substitute a proxy, '
        'a renamed unrelated family, an OBJ, or a builder script as a finished RFA. Finish source-library inspection '
        'before deciding a custom build is necessary. Keep E26 UL and E27 EU data distinct; source-drawing geometry, '
        'photo-derived ceramic contours, inferred bulb/canopy details, native emitter position and 2700K lamp behavior '
        'must be recorded separately in any later build.', '',
        'Source manifests: `' + str(ROOT / 'sources/kuzco/SOURCE_MANIFEST.json') + '` and `'
        + str(ROOT / 'sources/premium/OEM_SOURCE_MANIFEST.json') + '`.', '',
        'Independent offline receipts: `' + str(ROOT / 'qa/OEM_BYTE_IDENTITY.json') + '` and `'
        + str(ROOT / 'qa/OEM_STORED_METADATA.json') + '`.', '',
    ]
    out_path('SOURCE_SELECTION.md').write_text('\n'.join(selection), encoding='utf-8')

    # Select research extracts only when identical to their original ZIP members.
    extract_root = ROOT / 'sources/premium/extracted_exact_candidates'
    premium_specs = [
        ('MARSET_Dipping_Pendant_2D.zip', '2D_Dipping Light_13.dwg'),
        ('MARSET_Dipping_Pendant_3D_DWG.zip', 'lamp_marset_dipping_light_13.dwg'),
        ('MARSET_Dipping_Pendant_3D_OBJ.zip', 'lamp_marset_dipping_light_13.obj'),
        ('MARSET_Dipping_Pendant_Assembly.zip', 'Assembly_Instructions_Dipping_Light_13_0-10_UL.pdf'),
    ]
    sources_by_name = {Path(x['file']).name: x for x in byte_report['sources']}
    extract_paths = []
    extract_receipts = []
    for archive_name, member in premium_specs:
        source = sources_by_name[archive_name]
        with zipfile.ZipFile(source['file']) as archive:
            data = archive.read(member)
        path = extract_root / member
        assert path.read_bytes() == data, str(path)
        extract_paths.append(path)
        extract_receipts.append({'file': str(path), 'archive': source['file'],
                                 'archive_sha256': source['sha256'], 'member': member,
                                 'sha256': digest(path), 'byte_identity_pass': True})
    write_json(('qa', 'SELECTED_COMPANION_IDENTITY.json'), extract_receipts)

    allowed = [Path(x['file']) for x in byte_report['sources']]
    allowed += [Path(x['file']) for x in entries]
    allowed += extract_paths
    allowed += [ROOT / rel for rel in (
        'README.md', 'SOURCE_SELECTION.md', 'MANIFEST.json',
        'qa/OEM_BYTE_IDENTITY.json', 'qa/OEM_STORED_METADATA.json',
        'qa/NATIVE_RUNTIME_HOLD.json', 'qa/SELECTED_COMPANION_IDENTITY.json',
        'sources/kuzco/SOURCE_MANIFEST.json', 'sources/premium/OEM_SOURCE_MANIFEST.json',
        'scripts/extract_oem_unchanged.py', 'scripts/inspect_saved_oem_metadata.py',
        'scripts/make_review_package.py', 'scripts/verify_review_package.py',
        'runner/launch_native.py', 'runner/probe_native.py',
        'runner/receipts/probe_launcher_r01.json', 'runner/receipts/probe_stdout_r01.log',
    )]
    allowed += [Path(x) for row in stored for x in row['stored_preview_files']]
    allowed += [native_log]
    assert len(allowed) == len(set(allowed))
    inventory = []
    for path in allowed:
        assert ROOT in path.resolve().parents and path.is_file()
        inventory.append({'file': str(path), 'archive_member': path.relative_to(ROOT).as_posix(),
                          'bytes': path.stat().st_size, 'sha256': digest(path)})
    write_json(('qa', 'PACKAGE_INVENTORY.json'), inventory)
    allowed.append(ROOT / 'qa/PACKAGE_INVENTORY.json')
    target = out_path('release', 'Belmont_PH_Bedside_Pendants_OEM_REVIEW_NOT_RELEASED_20261017_r01.zip')
    if target.exists():
        raise RuntimeError('Refuse to overwrite existing archive: ' + str(target))
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in allowed:
            archive.write(path, path.relative_to(ROOT).as_posix())
    print(json.dumps({'archive': str(target), 'files': len(allowed),
                      'bytes': target.stat().st_size, 'sha256': digest(target),
                      'status': 'REVIEW_NOT_RELEASED'}, indent=2))


if __name__ == '__main__':
    main()
