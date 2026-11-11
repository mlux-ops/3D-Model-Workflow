"""Historical source aggregate across 2 PH + 2 TX, non-orderable until approvals."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
target=R/'deliverables/integrated-r04/PROJECT_MATERIAL_ROLLUP_R04.md'
sums={'Penthouse':0.0,'Triplex':0.0}
doc=['# 1529 Wieland — historic tile material rollup and commercial holds','',
 'Reconciliation of ELM September 3, 2026 source rates carried into Smartsheet. **Not a current supplier quote, approved budget, final takeoff or installed estimate.** Two Penthouse and two Triplex copies. WC flooring already included in Primary floor, with zero extra WC tile cost.',
 '',
 '| Unit type | Room | Source quote USD/room/unit | Copies | Historic two-copy USD | Scope caveat |',
 '|---|---|---:|---:|---:|---|']
for r in rooms:
 typ=r['unit_type'];amount=r['carried_quote_material_subtotal_usd_per_unit'];copies=r['unit_count']
 assert typ in sums and copies==2
 extended=round(amount*copies,2);sums[typ]+=extended
 if not r['carried_tile_rows']:note='Shared Primary floor, no new quoted WC invoice line'
 elif 'PRIMARY' in r['id']:note='Historic blended floor, no primary niche; DCOF unresolved'
 elif r['id'] in ('PH-BATH3','PH-BATH4','TX-BATH2','TX-BATH3','TX-BATH4'):note='Niche/field gross overlap unverified; exact floor DCOF absent'
 elif 'POWDER' in r['id']:note='Only dry vanity-wall tile; wood floor'
 else:note='Current Chicago stock and measured layout unverified'
 doc.append('| {} | {} | USD {:,.2f} | {} | USD {:,.2f} | {} |'.format(typ,r['id'],amount,copies,extended,note))
doc+=['','## Gross historical quote extensions — NOT an approved material budget','',
 '| Unit grouping | Historic material-only per dwelling | Historic two-dwelling gross |',
 '|---|---:|---:|']
for typ in ('Penthouse','Triplex'):
 doc.append('| {} | USD {:,.2f} | USD {:,.2f} |'.format(typ,sums[typ]/2,sums[typ]))
doc.append('| **All four dwellings** | N/A | **USD {:,.2f}** |'.format(sum(sums.values())))
doc+=['',
 'Historical source totals already include the 15 percent estimated installation waste. The gross values may overcount recess field/niche allocation and undercount all setting, waterproofing, slope/drain, trim, carton overage, freight, labor, tax and attic-stock. The separate project tile-section budget has not been allocated per room. Discontinued/unlisted wet-wall finishes and floors without exact measured wet DCOF make components non-orderable. The approved revised four-dwelling installed/project total remains **null** until priced and owner-approved, not the gross historic total.',
 '',
 '## Buy-package reconciliation checklist','',
 '- Confirm actual 1529 address, rooms, elevations, drain and opening schedule before gross-to-net takeoff, especially TX Bath3 tub versus shower and PH Bath4 35 versus 27 SF.',
 '- Deduct measured niche field face and add real jamb/back/sill returns once, do not apply a second 15 percent waste to source gross quantity.',
 '- Keep PH/TX WC sourced tile inside Primary quoted floor; no separate WC floor purchase row.',
 '- Price manufacturer-authorized wet wall finish, exact tested floor and small-format shower-pan SKU, delivered Chicago lot and lead, fully itemized grout/edge/membrane/mortar/labor.',
 '- Obtain room-specific owner upgrade allowance and dated selected manufacturer and distributor quotes before using a 125-percent material gate.',
 '','Auditable input: state/ROOMS.json plus SURFACE_TAKEOFF_13_ROOMS.csv; script scratch/create_material_rollup_r04.py.']
target.write_text('\n'.join(doc)+'\n',encoding='utf-8')
assert len(rooms)==13
print('PASS historic PH USD {:,.2f}, TX USD {:,.2f}, total gross USD {:,.2f}'.format(sums['Penthouse'],sums['Triplex'],sum(sums.values())))
