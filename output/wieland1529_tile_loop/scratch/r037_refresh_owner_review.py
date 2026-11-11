"""Recompose all 13 PROVISIONAL owner pages only after authenticated R037 board integration.

Preserves already accepted R036 tile decisions and their two independent reviewer FIXes.
No R036 page writes. Requires source-parsed 76/16/4 and a complete formal R037 decision.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT/'state'/'ROUND037_TWO_DURAVIT_TUB_DECISIONS.json'
assert DECISION.is_file(), 'R037 board decision absent: no R037 owner packets permitted'
decision = json.loads(DECISION.read_text(encoding='utf-8'))
assert (decision['criterion_count'], decision['seat_means_count'], decision['weighted_count']) == (76,16,4)
assert set(decision['rooms']) == {'TX-BATH2','TX-BATH4'}
assert decision['owner_approvals'] == 0

# Execute ONLY the R036 content construction prefix, not its page writer.
# That prefix reconstructs existing R035 unaffected rooms then applies actual
# R036 PH3/PH4/TX3 decisions. Separate R037 replacements below follow.
r036 = ROOT/'scratch'/'r036_refresh_owner_review.py'
r036_source = r036.read_text(encoding='utf-8')
cut = "env['OUT'] = ROOT / 'deliverables' / 'r036-13-owner-review-PROVISIONAL'"
assert r036_source.count(cut) == 1
prefix = r036_source.split(cut,1)[0]
ctx = {'__file__':str(r036),'__name__':'r037_reuse_r036_data'}
exec(compile(prefix,str(r036),'exec'),ctx)
env = ctx['env']
R = env['R']
T = env['T']
U = env['U']
P = ctx['P']
D = ctx['D']

schemes = {
 'TX-BATH2':{
   'A':[('Wet tub WALL',P),('Niche vertical faces',env['sandstone']),('Bath LEVEL',D)],
   'B':[('Wet tub WALL',env['sapphire']),('Niche vertical faces',env['purity']),('Bath LEVEL',env['luxe'])],
   'amount':{'A':'$642.91','B':'$845.46'},
   'note':'Duravit 59-in owner-selected TUB, Hansgrohe Chrome, basin UNSELECTED; NO tiled shower PAN, no POINT shower drain, no tiled wet ceiling. Drawing W1 ~62.484 in versus assumed 59.496-in opening and nominal 59-in tub remains a field geometry conflict. Verify flange, waterproofed horizontal niche sill, edge cuts and grout; Chicago exact lot/ETA/landed amount and owner budget FILL IN are open.'
 },
 'TX-BATH4':{
   'A':[('Wet tub WALL',env['luxe48']),('Niche vertical faces',env['sandstone']),('Bath LEVEL',env['luxe'])],
   'B':[('Wet tub WALL',env['antique']),('Niche vertical faces',env['purity']),('Bath LEVEL',P)],
   'amount':{'A':'$572.89','B':'$679.73'},
   'note':'Duravit 59-in owner-selected TUB, Hansgrohe Matte White; NO tiled shower PAN, shower point drain or tiled wet ceiling. Actual finished tub alcove, flange/waste, niche horizontal sill waterproofing, edge cuts, grout and installed assembly remain unverified. Chicago exact matching lot, tax/freight/landed pricing and owner budget FILL IN are open.'
 }
}

for room in R:
    rid = room['id']
    if rid not in schemes:
        continue
    d = decision['rooms'][rid]
    selected = d['selected_letter']
    assert selected in ('A','B') and d['selected_id']
    assert d['four_seat_complete'] and not d['owner_approved']
    alt = 'B' if selected == 'A' else 'A'
    spec = schemes[rid]
    room['status'] = ('PROVISIONAL CHAMPION — R037 changed' if d['changed']
                      else 'PROVISIONAL CHAMPION — R037 defended')
    room['score'] = (f"R037 {d['selected_id']} {d['selected_score']:.3f}; "
                     f"alternate {alt} {d['other_score']:.3f}")
    room['surfaces'] = spec[selected]
    room['cost'] = (f"R037 {selected} gross material area-rate {spec['amount'][selected]}/copy; "
                    "two physical copies, source 15% waste already counted ONCE; "
                    "NOT carton rounded or installed/Chicago landed. "
                    "Owner-selected bathtub: bathroom LEVEL only, NO tiled PAN cost.")
    room['alts'] = (f"Authentic strict-blind four-seat R037: {d['decision_summary']}. "
                     f"Neutral {alt} source gross area-rate {spec['amount'][alt]}/copy. "
                     "No owner signature or order.")
    room['holds'] = spec['note']
assert len(R)==13 and len(set(r['id'] for r in R))==13

# Reuse ONLY established R035 layout/composition code (post data marker),
# emitting R037 page names and one-page typography as proven for R036.
template=ROOT/'scratch'/'build_r035_owner_review.py'
source=template.read_text(encoding='utf-8')
marker="assert len(R)==13 and len(set(x['id'] for x in R))==13"
assert source.count(marker)==1
suffix=marker+source.split(marker,1)[1]
suffix=suffix.replace('R035_13_ROOM_OWNER_REVIEW_PAGES','R037_13_ROOM_OWNER_REVIEW_PAGES')
suffix=suffix.replace('r035-13-owner-review-PROVISIONAL','r037-13-owner-review-PROVISIONAL')
suffix=suffix.replace('font-size:10.5pt;line-height:1.32','font-size:10.2pt;line-height:1.28')
suffix=suffix.replace('padding:6px 7px;vertical-align:top','padding:5px 7px;vertical-align:top')
env['OUT']=ROOT/'deliverables'/'r037-13-owner-review-PROVISIONAL'
env['OUT'].mkdir(parents=True,exist_ok=True)
exec(compile(suffix,str(template),'exec'),env)

# Preserve independent Reviewer81's original maker-image provenance FIX in
# each standalone/combined owner page and the complete 13-card review.
pages = ([env['OUT']/(r['id']+'.html') for r in R]
         +[env['OUT']/'R037_13_ROOM_OWNER_REVIEW_PAGES.html',
           ROOT/'deliverables'/'TILE_SELECTIONS_REVIEW.html'])
for path in pages:
    raw=path.read_text(encoding='utf-8')
    if 'sandstone.jpg' not in raw: continue
    amended=raw.replace(
        'alt="Vendor product illustration Elm Tones Sandstone Glossy"',
        'alt="Maker mixed Sandstone/Copper installation; not standalone Sandstone appearance"'
    ).replace(
        '<span>Elm Tones Sandstone Glossy</span>',
        '<span>Sandstone/Copper mixed photo; NOT exact Sandstone</span>'
    ).replace(
        'alt="Vendor source illustration: Elm Tones Sandstone Glossy"',
        'alt="Maker mixed Sandstone/Copper installation; not standalone Sandstone appearance"'
    )
    amended=re.sub(
        r'(<img class="tilephoto"[^>]*sandstone\.jpg[^>]*>.*?)'
        r'(<span class="photo-note">)[^<]*(</span>)',
        r'\1\2Sandstone/Copper MIXED maker installation, not exact Sandstone-only appearance.\3',
        amended,flags=re.S,
    )
    assert amended!=raw,(path,'Sandstone mixed photo disclosure not applied')
    path.write_text(amended,encoding='utf-8')
print('PASS: authentic R036 selections preserved, R037 choices integrated to 13 new PROVISIONAL owner HTML pages; maker mixed-photo disclosure retained. PDFs require fresh printing and physical QA.')
