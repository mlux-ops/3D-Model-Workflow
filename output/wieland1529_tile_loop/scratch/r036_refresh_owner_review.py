"""Rebuild the 13 provisional owner review pages from an authenticated R036 decision.

Does not execute unless the prime has created state/ROUND036_THREE_WET_BATH_DECISIONS.json
from complete independent four-seat critiques. Retains all unaffected R035 choices.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / 'state' / 'ROUND036_THREE_WET_BATH_DECISIONS.json'
assert DECISION.is_file(), 'No authenticated final R036 board decision; no owner pages should change.'
decisions = json.loads(DECISION.read_text(encoding='utf-8'))
assert decisions.get('criterion_count') == 114 and decisions.get('seat_means_count') == 24
assert decisions.get('weighted_count') == 6
assert set(decisions['rooms']) == {'PH-BATH4', 'PH-BATH3', 'TX-BATH3'}

# Reuse established, physically printed 13-room page composition, but never write R035.
template = ROOT / 'scratch' / 'build_r035_owner_review.py'
source = template.read_text(encoding='utf-8')
marker = 'assert len(R)==13 and len(set(x[\'id\'] for x in R))==13'
assert source.count(marker) == 1
prefix, suffix = source.split(marker, 1)
env = {'__file__': str(template), '__name__': 'r036_source_data'}
exec(compile(prefix, str(template), 'exec'), env)
T = env['T']
U = env['U']
U.update({
    'pienza':'https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html',
    'derossi':'https://www.flooranddecor.com/porcelain-tile/de-rossi-ivory-matte-porcelain-tile-100996800.html',
    'emerald':'https://www.elmsurfaces.com/product/emerald-tones',
})
env['LOCAL_IMAGE_KEY'].update({U[k]:k for k in ('pienza','derossi','emerald')})
for key in ('pienza','derossi','emerald'):
    assert (ROOT/'deliverables'/'assets'/'tile_thumbs'/(key+'.jpg')).is_file(),key
P = T('F&D Pienza Terra Matte Porcelain 110850387', '24×48, actual 23.59×47.30, 9 mm rectified',
      '$2.99/SF IA public retail observed 2026-11-07', U['pienza'],
      'Exact Shower Walls YES; Bathroom Floor YES; Shower Floor YES; wet DCOF ≥0.42')
D = T('F&D De Rossi Ivory Matte Porcelain 100996800', '24×24, actual 23.50×23.50, 10.5 mm rectified',
      '$6.99/SF AZ public retail observed 2026-11-07', U['derossi'],
      'Exact Bathroom Floor YES; Shower Floor YES; wet DCOF ≥0.42; not certified overhead')
E = T('Elm Tones Emerald Glossy', '2×20, 8.5 mm glossy',
      '$6.95/SF 2026-09-04 1529 trade quote', U['emerald'], 'Maker Walls + Wet Areas YES; not shower floor')

products = {
 'PH-BATH4':{
  'A':[('Wet WALL',env['perimeter']),('Niche all faces',env['purity']),('Shared LEVEL + POINT PAN',env['luxe'])],
  'B':[('Wet WALL',P),('Niche all faces',env['sandstone']),('Shared LEVEL + POINT PAN',P)],
  'amounts':{'A':'$616.01','B':'$500.70'},
  'holds':'Owner-selected WALK-IN; Brizo BNX BT062415-BNX POINT. 35 SF owner floor vs 27 SF drawing conflict, one historic 40.2 SF LEVEL/PAN gross (15% waste once). BNX grate/rough, actual four-plane cuts, >=3-in exposed edges, niche sill waterproofing, Chicago matching lot and installed price, owner budget FILL IN and owner approval OPEN.'},
 'PH-BATH3':{
  'A':[('Wet WALL',P),('Niche all faces',env['sandstone']),('Bath LEVEL',D),('WALK-IN only conditional POINT PAN',D)],
  'B':[('Wet WALL',env['sapphire']),('Niche all faces',env['sandstone']),('Bath LEVEL',env['luxe']),('WALK-IN only conditional POINT PAN',env['luxe'])],
  'amounts':{'A':'$598.71','B':'$799.37'},
  'holds':'Owner TUB/WALK-IN UNSELECTED; basin UNSELECTED. Hansgrohe Chrome and Delta DT062412 Chrome POINT only if WALK-IN; separate optional PAN SF and price NULL, not zero and never added to 40.2 SF LEVEL. Tub uses its own waste. Measured layout, waterproof niche/sill, Chicago lot/landed and owner budget FILL IN OPEN.'},
 'TX-BATH3':{
  'A':[('Wet WALL',env['antique']),('Niche all faces',env['purity']),('Bath LEVEL',env['luxe']),('WALK-IN only conditional POINT PAN',env['luxe'])],
  'B':[('Wet WALL',E),('Niche all faces',env['purity']),('Bath LEVEL',P),('WALK-IN only conditional POINT PAN',P)],
  'amounts':{'A':'$685.92','B':'$792.27'},
  'holds':'Owner TUB/WALK-IN UNSELECTED. Brizo BNX BT062415-BNX POINT only if WALK-IN; independent optional PAN SF and price NULL, never bathtub waste. Original bath LEVEL 42.5 SF only with historical 15% waste once. Field cuts/waterproof niche sill, Chicago lot/landed, owner budget FILL IN and approval OPEN.'}
}
R = env['R']
for room in R:
    id = room['id']
    if id not in products: continue
    decision = decisions['rooms'][id]
    letter = decision['selected_letter']
    assert letter in ('A','B') and decision['selected_id']
    assert not decision.get('owner_approved', False)
    assert decision.get('four_seat_complete') is True
    spec = products[id]
    room['status'] = ('PROVISIONAL CHAMPION — R036 changed' if decision['changed'] else 'PROVISIONAL CHAMPION — R036 defended')
    room['score'] = (f"R036 {decision['selected_id']} {decision['selected_score']:.3f}; "
                     f"alternate {('B' if letter=='A' else 'A')} {decision['other_score']:.3f}")
    room['surfaces'] = spec[letter]
    room['cost'] = (f"R036 {letter} gross material rate {spec['amounts'][letter]}/copy, two physical copies; "
                    "not carton-rounded/landed; historic 15% material waste counted once. "
                    + ("PH-BATH4 WALK-IN is selected: one original combined 40.2 SF LEVEL/POINT PAN gross pool; NO separate extra PAN quantity or second PAN charge."
                       if id=='PH-BATH4' else
                       "TUB/WALK-IN remains UNSELECTED: additional conditional WALK-IN POINT PAN area and cost NULL (not zero), excluded from current LEVEL gross."))
    room['alts'] = f"Authentic same-round four-seat board: {decision['decision_summary']}. Unselected {('B' if letter=='A' else 'A')} material rate {spec['amounts']['B' if letter=='A' else 'A']}/copy. No owner signature."
    room['holds'] = spec['holds']
env['OUT'] = ROOT / 'deliverables' / 'r036-13-owner-review-PROVISIONAL'
env['OUT'].mkdir(parents=True, exist_ok=True)
suffix = (marker + suffix).replace('R035_13_ROOM_OWNER_REVIEW_PAGES', 'R036_13_ROOM_OWNER_REVIEW_PAGES').replace(
    'r035-13-owner-review-PROVISIONAL', 'r036-13-owner-review-PROVISIONAL')
# Maintain readable one-page Letter review while allowing new R036 fourth
# conditional surface rows and full technical/owner holds.
suffix = suffix.replace('font-size:10.5pt;line-height:1.32',
                        'font-size:10.2pt;line-height:1.28')
suffix = suffix.replace('padding:6px 7px;vertical-align:top',
                        'padding:5px 7px;vertical-align:top')
exec(compile(suffix, str(template), 'exec'), env)
assert (env['OUT']/'R036_13_ROOM_OWNER_REVIEW_PAGES.html').is_file()
# Image-truth correction from independent R036 reviewer: the Elm maker's
# sandstone-copper.png is a mixed installation photograph, NOT Sandstone-only.
# Preserve the original maker photograph and SKU URLs, but disclose that visual
# limitation in every individual/combined owner page and the 13-card review.
import re
review_pages = ([env['OUT']/(r['id']+'.html') for r in env['R']] +
                [env['OUT']/'R036_13_ROOM_OWNER_REVIEW_PAGES.html',
                 ROOT/'deliverables'/'TILE_SELECTIONS_REVIEW.html'])
for html_path in review_pages:
    src = html_path.read_text(encoding='utf-8')
    if 'sandstone.jpg' not in src:
        continue
    corrected = src.replace(
        'alt="Vendor product illustration Elm Tones Sandstone Glossy"',
        'alt="Maker mixed Sandstone/Copper installation; not standalone Sandstone appearance"'
    ).replace(
        '<span>Elm Tones Sandstone Glossy</span>',
        '<span>Sandstone/Copper mixed photo; NOT exact Sandstone</span>'
    ).replace(
        'alt="Vendor source illustration: Elm Tones Sandstone Glossy"',
        'alt="Maker mixed Sandstone/Copper installation; not standalone Sandstone appearance"'
    )
    corrected = re.sub(
        r'(<img class="tilephoto"[^>]*sandstone\.jpg[^>]*>.*?)'
        r'(<span class="photo-note">)[^<]*(</span>)',
        r'\1\2Sandstone/Copper MIXED maker installation, not exact Sandstone-only appearance.\3',
        corrected,
        flags=re.S,
    )
    assert corrected != src, (html_path, 'mixed image disclosure missing')
    html_path.write_text(corrected, encoding='utf-8')
print('PASS reviewer FIX: Sandstone mixed-maker-image disclosure in all affected HTML/alt text, PH4 combined PAN wording corrected.')
print('PASS R036 provisional 13-room owner HTML refreshed; PDFs still need printing and physical QA.')
