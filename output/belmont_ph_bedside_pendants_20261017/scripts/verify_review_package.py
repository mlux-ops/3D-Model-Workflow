"""Independent archive readback, manifest and original RFA identity verification."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    path = ROOT / 'release/Belmont_PH_Bedside_Pendants_OEM_REVIEW_NOT_RELEASED_20261017_r01.zip'
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        inventory = json.loads(archive.read('qa/PACKAGE_INVENTORY.json'))
        expected_names = {row['archive_member'] for row in inventory} | {'qa/PACKAGE_INVENTORY.json'}
        names = archive.namelist()
        assert len(names) == len(set(names))
        assert set(names) == expected_names, 'Unexpected or missing ZIP members'
        for row in inventory:
            data = archive.read(row['archive_member'])
            assert len(data) == row['bytes']
            assert sha(data) == row['sha256'], row['archive_member']
            assert data == Path(row['file']).read_bytes(), row['file']
        manifest = json.loads(archive.read('MANIFEST.json'))
        assert manifest['status'] == 'REVIEW_NOT_RELEASED'
        assert manifest['native_qa_passes'] == 0
        assert manifest['custom_rfa_files'] == 0
        assert manifest['rfa_modification_count'] == 0
        assert len(manifest['families']) == 4
        assert sum(x.endswith('.rfa') for x in names) == 4
        checks = []
        for family in manifest['families']:
            member = Path(family['file']).relative_to(ROOT).as_posix()
            family_data = archive.read(member)
            archive_member = Path(family['archive_file']).relative_to(ROOT).as_posix()
            # Independently compare the original member in the source ZIP INSIDE
            # the review package, not a previous script's boolean.
            import io
            with zipfile.ZipFile(io.BytesIO(archive.read(archive_member))) as original:
                original_data = original.read(family['archive_member'])
            assert family_data == original_data
            assert sha(original_data) == family['original_rfa_sha256'] == family['packaged_rfa_sha256']
            checks.append({'file': family['file'], 'original_rfa_sha256': sha(original_data),
                           'archived_original_byte_identity': 'PASS'})
    report = {
        'archive': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path.read_bytes()),
        'archive_crc': 'PASS', 'inventory_hashes': 'PASS', 'explicit_allow_list': 'PASS',
        'oem_original_comparisons': checks, 'file_count': len(names),
        'verification_result': 'OFFLINE_SOURCE_PACKAGE_PASS',
        'native_revit_2025_qa': 'NOT_RUN_STARTUP_CRASH',
        'release_status': 'REVIEW_NOT_RELEASED', 'drive_upload': 'NOT_ATTEMPTED',
    }
    receipt = ROOT / 'qa/REVIEW_ARCHIVE_READBACK.json'
    receipt.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
