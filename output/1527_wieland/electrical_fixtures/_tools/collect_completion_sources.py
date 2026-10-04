"""Archive explicitly discovered product sources and inventory an official 3D ZIP."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import contextlib, io, json, sys, zipfile
from download_resource import download
sys.stdout.reconfigure(errors='replace')
ROOT = Path(__file__).resolve().parents[1]
GROUPS = {g['key']: g for g in json.loads((ROOT / 'GROUPS.json').read_text())['groups']}
SOURCES = [
    ('QC4_J6', 'https://pdmassets.azureedge.net/library/JL/documents/specsheets/QC4.pdf', 'QC4_manufacturer_spec.pdf', 'https://www.acuitybrands.com/products/detail/1755459/juno/quick-connect-new-construction-housing/qc-series-ic-rated-4-5-and-6-housing-for-use-with-led-retrofit-trims'),
    ('SKL924074', 'https://www.sklo.com/wp-content/uploads/2026/06/SkLO_Hold_12_Sconce_LT267_260609.pdf', 'SkLO_Hold12_current_spec.pdf', 'https://www.sklo.com/light/hold-sconce/'),
    ('SKL924074', 'https://www.sklo.com/wp-content/uploads/2017/12/SkLO_LT267_Hold12Sconce_US_3D.zip', 'SkLO_Hold12_manufacturer_3D.zip', 'https://www.sklo.com/light/hold-sconce/'),
    ('VIS1256139', 'https://www.lightology.com/img/prod/pdf/FARO SP P UL-combined-11-9-23.pdf', 'Vistosi_Faro_US_assembly.pdf', 'https://www.lightology.com/index.php?module=prod_detail&prod_id=1256139'),
    ('VIS1486649', 'https://www.lightology.com/img/prod/pdf/JUBE AP S UL-6-16-23.pdf', 'Vistosi_Jube_US_assembly.pdf', 'https://www.lightology.com/index.php?module=prod_detail&prod_id=1486649'),
    ('KZC1009522', 'https://s3-us-west-2.amazonaws.com/catsy.870/MP75121_Spec_Sheet.pdf', 'Kuzco_Motif_MP75121_spec.pdf', 'https://kuzcolighting.com/products/motif-mp75121-kuzco'),
    ('BOM1273301', 'https://www.lightology.com/img/prod/pdf/bomma-Dew Drops_wall & ceiling_EN-12-18-23.pdf', 'Bomma_Dew_Drops_assembly.pdf', 'https://www.lightology.com/index.php?module=prod_detail&prod_id=1273301'),
    ('AMB-MB-56-EB-870-CC', 'https://www.lightology.com/img/prod/pdf/modfan-AMB-InstallationManual-V2023-07-online-20231005.pdf', 'Ambit_manufacturer_installation.pdf', 'https://www.lightology.com/index.php?module=prod_detail&prod_id=1247814'),
    ('MKL1417874', 'https://www.lightology.com/img/prod/pdf/3114-L-English-052225.pdf', 'Minka_Verto_installation.pdf', 'https://www.lightology.com/index.php?module=prod_detail&prod_id=1417874'),
    ('700BCTRS3C-LED930', 'https://www.lightology.com/img/prod/pdf/vcmod-ig_920bctris-instr-20231211.pdf', 'Tris_manufacturer_installation.pdf', 'https://www.visualcomfort.com/us/p/tris-3-light-bath-700bctrs3'),
    ('TLG604508', 'https://www.lightology.com/img/prod/pdf/vcmod-ig_920bcmilan24-instr-20231228.pdf', 'Milan_manufacturer_installation.pdf', 'https://www.visualcomfort.com/us/p/milan-24-bath-700bcmln24'),
    ('MFR918914', 'https://modernforms.com/images/products/REVIT/FR-W2006-52_REVIT.zip', 'Zephyr52_manufacturer_Revit.zip', 'https://modernforms.com/product/zephyr-52/'),
    ('MFR918914', 'https://modernforms.com/images/products/SPECSHEET_PDF/FR-W2006-52_SPSHT.pdf', 'Zephyr52_manufacturer_spec.pdf', 'https://modernforms.com/product/zephyr-52/'),
    ('700BCTRS3C-LED930', 'https://www.visualcomfort.com/media/docs/spec_sheet/t/r/ss_tris_3-light_bath.pdf', 'Tris_manufacturer_spec.pdf', 'https://www.visualcomfort.com/us/p/tris-3-light-bath-700bctrs3'),
    ('TLG604508', 'https://www.visualcomfort.com/media/docs/spec_sheet/m/i/ss_milan_24_bath.pdf', 'Milan_manufacturer_spec.pdf', 'https://www.visualcomfort.com/us/p/milan-24-bath-700bcmln24'),
]

def acquire(entry):
    key, url, filename, provenance = entry
    target = ROOT / GROUPS[key]['canonical_item'] / 'source' / filename
    receipt = target.with_suffix(target.suffix + '.acquisition.json')
    if receipt.exists():
        return json.loads(receipt.read_text())
    if target.exists():
        return {'path': str(target), 'status': 'EXISTING_RESOURCE_PRESERVED'}
    return download(key, url, filename, provenance)

def main():
    # Download helper prints receipts; sequential calls keep acquisition logs readable.
    results = [acquire(entry) for entry in SOURCES]
    for result in results:
        path = Path(result.get('path', ''))
        if path.is_file() and path.suffix.lower() == '.zip':
            with zipfile.ZipFile(path) as archive:
                result['zip_crc_error'] = archive.testzip()
                result['zip_members'] = archive.namelist()
                out = path.with_suffix('')
                out.mkdir(exist_ok=True)
                for member in archive.infolist():
                    dest = (out / member.filename).resolve()
                    if not dest.is_relative_to(out.resolve()):
                        raise ValueError('ZIP path escapes source folder')
                    if not dest.exists():
                        archive.extract(member, out)
    (ROOT / 'COMPLETION_SOURCE_RECEIPTS.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print('Completed source receipts:', len(results), 'errors:', sum('error' in r for r in results))
    for result in results:
        if result.get('error'): print('ERROR', result['url'], result['error'])
        if result.get('zip_members'): print('ZIP CONTENTS', result['zip_members'])

if __name__ == '__main__':
    main()
