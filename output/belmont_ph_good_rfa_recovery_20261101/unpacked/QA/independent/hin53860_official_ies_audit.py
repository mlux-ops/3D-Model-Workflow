"""Offline verification of exact Hinkley 53860BK LM-63 source."""
import hashlib
import json
from pathlib import Path

ROOT = Path(r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016')
IES = ROOT / 'sources' / 'photometry' / 'HIN53860BK_53860_official.ies'
REPORT = ROOT / 'sources' / 'photometry' / 'HIN53860BK_IES_VERIFICATION.json'
SOURCE_URL = 'https://hinkleymedia.s3.amazonaws.com/Products/files/ies/53860.ies'
EXPECTED_SHA = 'b8f4e409bd01f235c2a6a17024825aca667dc187dd95ceb84a5adec90c50e8b9'

def run():
    if REPORT.exists():
        raise RuntimeError('Report exists; refuse overwrite')
    raw = IES.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    assert sha == EXPECTED_SHA, sha
    lines = raw.decode('ascii').splitlines()
    assert lines[0].strip() == 'IESNA:LM-63-2002'
    meta = {}
    marker = None
    for idx, line in enumerate(lines):
        if line.startswith('[') and ']' in line:
            key, _, value = line[1:].partition(']')
            meta[key] = value.strip()
        if line.startswith('TILT='):
            assert line.strip() == 'TILT=NONE'
            marker = idx
            break
    assert marker is not None
    assert meta['LUMINAIRE'] == '53860BK'
    assert meta['MANUFAC'] == 'Hinkley'
    vals = ' '.join(lines[marker+1:]).split()
    first = list(map(float, vals[:10]))
    lamps, lumens_per_lamp, multiplier, nvertical, nhorizontal, phototype, units = first[:7]
    wattage = float(vals[12])
    assert int(lamps) == 1 and int(nvertical) == 37 and int(nhorizontal) == 21
    assert int(phototype) == 1 and int(units) == 2
    expected_count = 13 + 37 + 21 + 37 * 21
    assert len(vals) == expected_count, (len(vals), expected_count)
    vertical = list(map(float, vals[13:50]))
    horizontal = list(map(float, vals[50:71]))
    candela = list(map(float, vals[71:]))
    assert vertical[0] == 0 and vertical[-1] == 180
    assert horizontal[0] == 0 and horizontal[-1] == 360
    assert len(candela) == 777 and min(candela) >= 0
    report = {
        'exact_sku': '53860BK', 'source_url': SOURCE_URL,
        'local_file': str(IES), 'sha256': sha, 'size_bytes': len(raw),
        'format': 'IESNA LM-63-2002', 'metadata': meta,
        'lamp_count': int(lamps), 'lumens_per_lamp_lm63': lumens_per_lamp,
        'candela_multiplier': multiplier, 'test_wattage_w': wattage,
        'photometric_type': int(phototype), 'unit_type': int(units),
        'vertical_angles': len(vertical), 'horizontal_angles': len(horizontal),
        'candela_values': len(candela), 'maximum_candela': max(candela),
        'official_catalog_lumens': 1000, 'official_catalog_wattage_w': 19,
        'note': 'IES laboratory measured 1109 lm and 18.45 W; preserve these separately from published rounded 1000 lm / 19 W, do not scale an exact IES to make catalog values match.',
        'validated': True
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    run()
