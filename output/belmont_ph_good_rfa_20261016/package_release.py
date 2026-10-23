"""Build an immutable, provenance-aware Belmont PH Good RFA review ZIP.

Run with Python 3 on Windows. Always emits a new filename, preserves all inputs.
"""
import hashlib
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent
FAMILY_DIR = ROOT / 'families'
RECEIPTS = ROOT / 'runner' / 'receipts'
OUT = ROOT / 'release'
SPECS = [
    ('ALR1280090', 'Alora_Cassia_LP549448MBCL_R2025.rfa', 'ALR1280090', 'oem'),
    ('HIN990485', 'Hinkley_Eos_53860BK_R2025.rfa', 'hin990485', 'custom'),
    ('KZC1353667', 'Kuzco_Bolla_PD3106_BG_R2025.rfa', 'kzc1353667', 'oem'),
    ('MFR1415595', 'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025.rfa', 'mfr1415595', 'oem'),
    ('MFR201959', 'ModernForms_Vogue_WS-3127_CH_R2025.rfa', 'mfr201959', 'oem'),
    ('QUO1249827', 'Quorum_Veno_858-59_R2025.rfa', 'quo1249827', 'custom'),
    ('VCS833918', None, None, 'reuse'),
]
NODES = pathlib.Path(r'E:\Claude\3D-Model-Workflow\output\lightology_20260923\release\Lightology_14_Face_Based_RFAs_R2025_Rev1\RFAs\Visual_Comfort_Nodes_KW1041BBS_Burnished_Brass_R2025.rfa')


def h(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    index = []
    files = []
    for sku, filename, rid, kind in SPECS:
        source = NODES if kind == 'reuse' else FAMILY_DIR / filename
        if not source.is_file():
            raise FileNotFoundError(source)
        receipt = None if rid is None else RECEIPTS / (rid.lower() + '.json')
        if receipt is not None:
            if not receipt.is_file():
                raise FileNotFoundError(receipt)
            native = json.loads(receipt.read_text(encoding='utf-8-sig'))
            if native.get('status') != 'PASS':
                raise RuntimeError('Native receipt not PASS: ' + str(receipt))
        else:
            native = None
        index.append({
            'smartsheet_sku': sku,
            'file_name': source.name,
            'kind': kind,
            'sha256': h(source),
            'bytes': source.stat().st_size,
            'native_batch_status': native.get('status') if native else 'prior accepted',
            'native_receipt': str(receipt) if receipt else None,
            'remaining_acceptance': ('Verify source finish/type, electrical and project placement' if kind == 'oem'
                                     else 'HOLD: visual-fidelity approval, IES and connector' if kind == 'custom'
                                     else 'Existing visualization-approved family; project validation pending'),
        })
        files.append((source, 'RFAs/' + source.name))
        if receipt:
            files.append((receipt, 'QA/native/' + receipt.name))
    qa = RECEIPTS / 'custom_qa.json'
    files.append((qa, 'QA/native/custom_qa.json'))
    files.append((RECEIPTS / 'batch_final.json', 'QA/native/batch_final.json'))
    files.append((ROOT / 'sources' / 'oem' / 'manifest.json', 'SOURCES/oem_manifest.json'))
    workflow = pathlib.Path(r'E:\Claude\3D-Model-Workflow\docs\REVIT_RFA_AGENT_WORKFLOW_20261016.md')
    files.append((workflow, 'WORKFLOW.md'))
    readme = ('651 Belmont Penthouse GOOD - Revit 2025 lighting family review package\n\n'
              'Seven Smartsheet selections: six 2026-10-16 native created/saved families and one reused Nodes family.\n'
              'Native save/reopen/category/warnings passed 6/6; two custom families passed independent host/geometry checks.\n'
              'REVIEW RELEASE: Product-source visual acceptance and IES/electrical validation remain open.\n'
              'Do not interpret technical PASS as construction-document or photometric approval.\n'
              'Quorum Veno has representative suspension and a reconstructed glass shade requiring correction.\n'
              'Details and exact source records in INDEX.json, QA/native and SOURCES.\n')
    path = OUT / 'Belmont_PH_GOOD_Lighting_RFA_REVIEW_20261016_r01.zip'
    if path.exists():
        raise FileExistsError(path)
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for source, member in files:
            if not source.is_file():
                raise FileNotFoundError(source)
            z.write(source, member)
        z.writestr('README.txt', readme)
        z.writestr('INDEX.json', json.dumps(index, indent=2))
    assert zipfile.ZipFile(path).testzip() is None
    receipt = OUT / 'REVIEW_RELEASE_MANIFEST.json'
    receipt.write_text(json.dumps({'archive': str(path), 'archive_sha256': h(path), 'rfas': index,
                                   'status': 'REVIEW_ONLY'}, indent=2), encoding='utf-8')
    print(json.dumps({'archive': str(path), 'bytes': path.stat().st_size, 'sha256': h(path),
                      'members': len(files) + 2, 'status': 'REVIEW_ONLY'}, indent=2))


if __name__ == '__main__':
    main()
