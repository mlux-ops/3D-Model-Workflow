r"""Package the verified clamp family for delivery (CPython 3, standard library only).

    "C:\Program Files\pyRevit-Master\bin\cengines\CPY3123\python.exe" package_clamp.py

Refuses to package unless verify_clamp.py passes and REVIEW.md records
"Visual verdict: ACCEPTED". Allow-listed contents only (no logs, no *.000N.rfa backups);
re-opens the ZIP, runs testzip(), writes package_manifest.json. Upload is a separate,
verified step (README.md).
"""
import datetime
import hashlib
import json
import os
import sys
import zipfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import clamp_spec as S  # noqa: E402
import verify_clamp  # noqa: E402

RUN_DIR = os.path.normpath(os.path.join(HERE, '..'))
REPO = os.path.normpath(os.path.join(RUN_DIR, '..', '..'))
REF = os.path.join(REPO, 'references', 'crl_sgc180')
ZIP_NAME = 'SHB_Glass_Clamp_180_Square_R2025_Package.zip'
ROOT_FILES = [S.RFA_NAME, S.CATALOG_NAME, 'README.md', 'INFERENCES.md', 'REVIEW.md', 'validation.json']
_RUN_NORM = os.path.normpath(RUN_DIR)


def out_path(name):
    target = os.path.normpath(os.path.join(RUN_DIR, name))
    if not target.startswith(_RUN_NORM + os.sep):
        raise RuntimeError('write escapes run dir: ' + target)
    return target


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def allow_list():
    items = [(os.path.join(RUN_DIR, n), n) for n in ROOT_FILES]
    folder = os.path.join(RUN_DIR, 'evidence')
    for n in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if n.lower().endswith('.png'):
            items.append((os.path.join(folder, n), 'evidence/' + n))
    for n in sorted(os.listdir(REF)):
        items.append((os.path.join(REF, n), 'references/' + n))
    return items


def main():
    if verify_clamp.main() != 0:
        print('NOT PACKAGED - technical verification failed.')
        return 1
    review = os.path.join(RUN_DIR, 'REVIEW.md')
    if not os.path.isfile(review) or 'Visual verdict: ACCEPTED' not in open(review).read():
        print('NOT PACKAGED - REVIEW.md must record "Visual verdict: ACCEPTED" after the human review.')
        return 1
    items = allow_list()
    missing = [src for src, _ in items if not os.path.isfile(src)]
    if missing:
        print('NOT PACKAGED - missing: %r' % missing)
        return 1
    target = out_path(ZIP_NAME)
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as zf:
        for src, arc in items:
            zf.write(src, arc)
    with zipfile.ZipFile(target) as zf:
        bad = zf.testzip()
        names = zf.namelist()
    if bad is not None:
        print('PACKAGE CORRUPT - first bad entry: %s' % bad)
        return 1
    manifest = {'package': ZIP_NAME, 'created_utc': datetime.datetime.utcnow().isoformat() + 'Z',
                'entries': len(names), 'bytes': os.path.getsize(target), 'sha256': sha256(target),
                'testzip': 'no corrupt entries',
                'files': [{'path': arc, 'bytes': os.path.getsize(src), 'sha256': sha256(src)} for src, arc in items],
                'drive_destination': '3D Model Workflow (1Xsd3Y96SOi00cWNaxqYeqlp4tNe3Z8CD) / 3D Models',
                'drive_upload': 'PENDING - copy to the Drive for Desktop mount, then verify fileSize through the API'}
    with open(out_path('package_manifest.json'), 'w') as fh:
        json.dump(manifest, fh, indent=2)
    print('PACKAGED %s: %d entries, %d bytes, SHA-256 %s' % (target, len(names), manifest['bytes'], manifest['sha256']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
