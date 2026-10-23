"""Independent R02 readback: exact allow-list, bytes, OEM RFA and CAD identity."""
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / 'release/Belmont_PH_Bedside_5_Selections_SOURCE_REVIEW_NOT_RELEASED_20261017_r03.zip'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    with zipfile.ZipFile(ZIP) as archive:
        assert archive.testzip() is None
        rows = json.loads(archive.read('qa/PACKAGE_INVENTORY_R02.json'))
        names = archive.namelist()
        assert len(names) == len(set(names))
        assert set(names) == {row['member'] for row in rows} | {'qa/PACKAGE_INVENTORY_R02.json'}
        for row in rows:
            data = archive.read(row['member'])
            assert len(data) == row['bytes'] and sha(data) == row['sha256'], row['member']
            assert Path(row['file']).read_bytes() == data, row['file']
        manifest = json.loads(archive.read('MANIFEST.json'))
        assert manifest['revision'] == 'R03' and manifest['status'] == 'REVIEW_NOT_RELEASED'
        assert manifest['manufacturer_source_download_count_verified'] == 19
        assert manifest['manufacturer_source_archive_count_verified'] == 11
        assert manifest['native_qa_passes'] == 0 and manifest['custom_rfa_files'] == 0
        assert len(manifest['families']) == 4
        assert sum(name.lower().endswith('.rfa') for name in names) == 4
        rfa_checks = []
        for row in manifest['families']:
            path = Path(row['file'])
            data = archive.read(path.relative_to(ROOT).as_posix())
            source_zip = Path(row['archive_file']).relative_to(ROOT).as_posix()
            with zipfile.ZipFile(io.BytesIO(archive.read(source_zip))) as source:
                assert source.read(row['archive_member']) == data
            assert sha(data) == row['original_rfa_sha256'] == row['packaged_rfa_sha256']
            rfa_checks.append({'file': str(path), 'sha256': sha(data), 'unchanged': True})
        cad = json.loads(archive.read('qa/SCHNEID_OEM_CAD_REVIEW_R02.json'))
        source_archive = Path(cad['archive'])
        assert sha(source_archive.read_bytes()) == cad['archive_sha256']
        cad_checks = []
        with zipfile.ZipFile(source_archive) as factory:
            assert factory.testzip() is None
            assert not [name for name in factory.namelist() if name.lower().endswith('.rfa')]
            for row in cad['oem_cad_sources']:
                path = Path(row['file'])
                data = archive.read(path.relative_to(ROOT).as_posix())
                assert factory.read(row['archive_member']) == data
                assert sha(data) == row['sha256']
                cad_checks.append({'file': str(path), 'sha256': sha(data), 'unchanged': True})
    report = {'archive': str(ZIP), 'bytes': ZIP.stat().st_size, 'sha256': sha(ZIP.read_bytes()),
              'files': len(names), 'crc': 'PASS', 'allow_list_and_inventory': 'PASS',
              'oem_rfa_byte_identity': rfa_checks, 'schneid_oem_cad_byte_identity': cad_checks,
              'official_schneid_archive_rfa_count': 0,
              'status': 'OFFLINE_SOURCE_REVIEW_PACKAGE_PASS', 'native_revit_qa': 'NOT_RUN',
              'full_five_rfa_release': False, 'drive_upload': 'NOT_ATTEMPTED'}
    (ROOT / 'qa/SOURCE_REVIEW_ARCHIVE_READBACK_R02.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'archive': str(ZIP), 'bytes': report['bytes'], 'sha256': report['sha256'],
                      'files': len(names), 'rfa_identity_passes': len(rfa_checks),
                      'cad_identity_passes': len(cad_checks), 'status': report['status'],
                      'native_revit_qa': report['native_revit_qa']}, indent=2))


if __name__ == '__main__':
    main()
