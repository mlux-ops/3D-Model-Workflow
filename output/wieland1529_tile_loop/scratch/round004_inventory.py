"""Read-only board inventory of all 13 rooms."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))
for x in d['rooms']:
    print('{} | {} | {} | score={} | last={} | dollar_per_unit={} | gaps={}'.format(
        x['id'],x['status'],x.get('champion_id'),x.get('champion_score'),x.get('last_round'),
        x.get('carried_quote_material_subtotal_usd_per_unit'),len(x.get('open_gaps') or [])))
    if x['id'].startswith('PH-'):
        print('  carried:',[(r['surface'],r['carried_description'][:64],r['qty_sf_per_unit'],
            r['quoted_rate_usd_per_sf'],r['extended_quote_cost_usd_per_unit']) for r in x.get('carried_tile_rows',[])])
