"""Verify saved source manifests and extract original OEM RFA bytes without Revit.

Run with CPython 3. No third-party modules or downloads. Never replaces a file
whose bytes differ from its original archive member.
"""
import datetime
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MAGIC = bytes.fromhex('d0cf11e0a1b11ae1')


def out_path(*parts):
    path = ROOT.joinpath(*parts).resolve()
    if ROOT not in path.parents:
        raise ValueError('Write outside task root: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def extract():
    kuzco_manifest = ROOT / 'sources/kuzco/SOURCE_MANIFEST.json'
    premium_manifest = ROOT / 'sources/premium/OEM_SOURCE_MANIFEST.json'
    source_rows = []
    for record in load(kuzco_manifest):
        source_rows.append(dict(record, file=str(kuzco_manifest.parent / record['filename'])))
    source_rows.extend(load(premium_manifest))
    by_file = {}
    verified_sources = []
    holds = []
    for record in source_rows:
        if record.get('status') == 'failed':
            holds.append({k: record.get(k) for k in ('id', 'url', 'file', 'status', 'error')})
            continue
        path = Path(record['file']).resolve()
        if ROOT not in path.parents:
            raise ValueError('Source outside task: ' + str(path))
        data = path.read_bytes()
        assert sha(data) == record['sha256'].lower(), str(path)
        assert len(data) == record['bytes'], str(path)
        row = {'file': str(path), 'url': record['url'], 'bytes': len(data),
               'sha256': sha(data), 'recorded_source_manifest_hash_match': True}
        if path.suffix.lower() == '.zip':
            with zipfile.ZipFile(path) as archive:
                assert archive.testzip() is None, str(path)
                row['archive_crc_pass'] = True
                row['archive_members'] = [
                    {'name': x.filename, 'bytes': x.file_size,
                     'compression': x.compress_type, 'crc32': format(x.CRC, '08x')}
                    for x in archive.infolist() if not x.is_dir()]
        else:
            assert data.startswith(b'%PDF'), str(path)
            row['pdf_signature_pass'] = True
        by_file[path.name] = row
        verified_sources.append(row)

    selections = [
        ('Kuzco', 'Jarvis', '41411-BG', '41411',
         'REVIT-41411-Jarvis.zip', 'REVIT-41411-Jarvis/41411 - Jarvis.rfa',
         'Exact OEM 41411 family; Brushed Gold type/material not natively verified.'),
        ('Kuzco', 'Malabar', '402401BG-LED', '402401-LED',
         'REVIT-402401-LED-Malabar.zip', 'REVIT-402401LED-Malabar/402401LED-Malabar.rfa',
         'Exact OEM 402401LED family; Brushed Gold type/material not natively verified.'),
        ('Kuzco', 'Milca', '494502M-GD', '494502M',
         'REVIT-494502M-Milca.zip', '494502M-Milca.rfa',
         'Exact OEM 494502M family; Gold type/material not natively verified.'),
        ('Marset', 'Dipping Light', 'A691-474-37-27K', 'Dipping Light 13 Cream 0-10V',
         'MARSET_Dipping_Light_S_BIM_Link_Check.zip',
         'MARSET_Interior-Lighting-Fixture-Suspended_Dipping-Light.rfa',
         'OEM suspended Dipping Light family candidate; 13/Cream/0-10V variant not verified. '
         'The server URL says table lamp; archive member says suspended. No exact SKU claim.'),
    ]
    families = []
    for maker, name, sku, model, archive_name, member, caveat in selections:
        archive_row = by_file[archive_name]
        with zipfile.ZipFile(archive_row['file']) as archive:
            data = archive.read(member)
            assert data.startswith(MAGIC), member
            target = out_path('families', Path(member).name)
            if target.exists():
                assert target.read_bytes() == data, 'Conflicting existing output: ' + str(target)
            else:
                with target.open('xb') as handle:
                    handle.write(data)
            reread = target.read_bytes()
            assert reread == archive.read(member), str(target)
            families.append({
                'manufacturer': maker, 'selection': name, 'requested_sku': sku,
                'manufacturer_model': model, 'source_url': archive_row['url'],
                'archive_file': archive_row['file'],
                'archive_sha256': archive_row['sha256'], 'archive_member': member,
                'original_rfa_sha256': sha(data), 'packaged_rfa_sha256': sha(reread),
                'file': str(target), 'bytes': len(data), 'byte_for_byte_unchanged': True,
                'cfb_signature_pass': True, 'saved_by_revit_in_this_task': False,
                'variant_caveat': caveat,
                'native_revit_2025_open': 'NOT_RUN_STARTUP_CRASH',
                'native_types': None, 'native_material_assignments': None,
                'native_body_bounds': None, 'native_ceiling_placement': None,
                'native_lighting_source': None, 'visual_evidence': None,
                'release_status': 'SOURCE_BYTES_VERIFIED_NATIVE_QA_HOLD',
            })
    report = {
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'task_root': str(ROOT), 'release_status': 'REVIEW_NOT_RELEASED',
        'verification_scope': 'Archive CRC, recorded download SHA/size, RFA byte identity and CFB signature only.',
        'sources': verified_sources, 'families': families,
        'source_acquisition_holds': holds,
        'missing_selection': {'manufacturer': 'Schneid Studio', 'model': 'Stucco II',
                              'requested_sku': 'STUCCO-II-CLAY-UL',
                              'status': 'NO_OEM_RFA_ESTABLISHED_CUSTOM_NATIVE_BUILD_BLOCKED',
                              'unsearched_source': 'Manufacturer-linked Dropbox archive; 186260124 bytes; source worker size cap rejected download.',
                              'scope_limit': 'No claim that manufacturer library contains no usable model.'},
        'native_runtime': 'Prior isolated Revit 2025.4.5 startup crashed before probe script; no identical rerun.',
        'drive_upload': 'NOT_ATTEMPTED_FULL_PACKAGE_QA_PENDING',
    }
    out_path('qa', 'OEM_BYTE_IDENTITY.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'sources_verified': len(verified_sources), 'oem_rfas_extracted': len(families),
                      'unchanged': all(x['byte_for_byte_unchanged'] for x in families),
                      'source_holds': len(holds), 'native_qa': 'HOLD'}, indent=2))


if __name__ == '__main__':
    extract()
