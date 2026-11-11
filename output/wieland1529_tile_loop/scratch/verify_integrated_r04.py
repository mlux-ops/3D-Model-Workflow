"""Check generated owner package against 13-room source and transparent quote exceptions."""
from pathlib import Path
import json,csv
R=Path(__file__).resolve().parents[1]
records=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
target=R/'deliverables/integrated-r04'
assert len(records)==13
with (target/'SURFACE_TAKEOFF_13_ROOMS.csv').open(encoding='utf-8-sig',newline='') as f:
    lines=list(csv.DictReader(f))
assert len(lines)==sum(len(r['carried_tile_rows']) for r in records)
exact={(x['room'],x['Smartsheet_row_id']):x for x in lines}
for room in records:
    rid=room['id']
    geom=json.loads((R/'rooms'/rid/'geometry.json').read_text(encoding='utf-8'))
    assert geom['model_identity_verified'] is False,(rid,'no 1529 confirmed')
    for source in room['carried_tile_rows']:
        row=exact[(rid,source['smartsheet_row_id'])]
        assert float(row['gross_SF_per_unit_including_original_15pct_waste'])==source['qty_sf_per_unit']
        actual=source['extended_quote_cost_usd_per_unit']
        if actual is None:
            assert row['carried_extended_USD_per_unit']==''
        else:
            assert abs(float(row['carried_extended_USD_per_unit'])-actual)<1e-8
            assert abs(source['qty_sf_per_unit']*source['quoted_rate_usd_per_sf']-actual)<.015,(rid,source['surface'])
    assert rid in (target/'13_ROOM_SELECTION_AND_TIERS.md').read_text(encoding='utf-8')
    assert rid in (target/'13_ROOM_PROVISIONAL_DIMENSIONED_ELEVATIONS.md').read_text(encoding='utf-8')
    assert rid in (target/'OWNER_DECISIONS_R04.md').read_text(encoding='utf-8')
    assert rid in (target/'13_ROOM_SAMPLE_KIT_AND_RENDER_BRIEFS.md').read_text(encoding='utf-8')
    assert rid in (target/'13_ROOM_PROCUREMENT_HOLDS.md').read_text(encoding='utf-8')
assert 'TX-WC' in [r['id'] for r in records]
assert 'PH-WC' in [r['id'] for r in records]
assert not next(r for r in records if r['id']=='PH-WC')['carried_tile_rows']
assert not next(r for r in records if r['id']=='TX-WC')['carried_tile_rows']
assert '70 percent' in (target/'OWNER_DECISIONS_R04.md').read_text(encoding='utf-8')
print('PASS 13 unique rooms; {} source cost rows exact; 5 markdown deliverables cross-checked; WC floor double-count prevented'.format(len(lines)))
