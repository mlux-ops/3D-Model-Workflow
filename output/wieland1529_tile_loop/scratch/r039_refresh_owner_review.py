"""R039 13-room PROVISIONAL owner HTML; only after authentic 76/16/4 decision."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
decision=json.loads((ROOT/'state/ROUND039_TWO_DRY_POWDER_DECISIONS.json').read_text(encoding='utf-8'))
assert (decision['criterion_count'],decision['seat_means_count'],decision['weighted_count'])==(76,16,4)
assert decision['owner_approvals']==0 and set(decision['rooms'])=={'TX-POWDER','TX-POWDER2'}
assert decision['rooms']['TX-POWDER']['selected_id'] is None
assert decision['rooms']['TX-POWDER2']['selected_id']=='v4-TX-POWDER2'

# Rebuild ONLY the R038 content data prefix; never execute its R038 page writer.
r038=ROOT/'scratch/r038_refresh_owner_review.py'
source=r038.read_text(encoding='utf-8')
marker='# Preserve earlier owner presentation corrections and composer; only change round-specific destination labels.'
assert source.count(marker)==1
prefix=source.split(marker,1)[0]
ctx={'__file__':str(r038),'__name__':'r039_reuse_r038_content_only'}
exec(compile(prefix,str(r038),'exec'),ctx)
env=ctx['env'];R=env['R']
assert len(R)==13
for room in R:
 rid=room['id']
 if rid=='TX-POWDER':
  d=decision['rooms'][rid]
  assert d['four_seat_complete'] and d['selected_letter'] is None
  room['status']='BLOCKED — NO QUALIFIED R039 VANITY WALL TILE'
  room['score']='R039 A Haze 3.410 COST 2.8 FAIL; B Pienza 2.950 DESIGN 2.8 FAIL'
  room['surfaces']=[]  # No selected tile. Do not show disqualified Haze as the selected surface.
  room['cost']=('NO qualified tile selected or authorized for the single DRY vanity WALL. '
                'Original gross WALL allowance 31.8 SF/copy (two copies) carried for comparison, '
                'historic 15% waste included once. Rejected candidate area-rate screens: '
                'Haze $379.37/copy; Pienza $95.08/copy (non-Chicago public retail). '
                'Neither amount is a selected purchase, extra floor or PAN charge; '
                'existing WOOD floor retained; owner budget FILL IN.')
  room['alts']=('Four authentic strict-blind original R039 seats: A fails COST 2.8/5; '
                'B fails DESIGN 2.8/5. No selected tile; new materially distinct '
                'allowed-vendor DRY WALL alternative required immediately. Zero owner approvals.')
  room['holds']=d['technical_holds']
  room['plumbing']='Hansgrohe wall-mounted faucet/rough; actual visible finish UNCONFIRMED; DRY vanity WALL and retained WOOD flooring; no tiled LEVEL/PAN/NICHE/CEILING'
 if rid=='TX-POWDER2':
  d=decision['rooms'][rid]
  assert d['four_seat_complete'] and d['selected_letter']=='A' and not d['changed']
  room['status']='PROVISIONAL CHAMPION — R039 defended'
  room['score']='R039 v4-TX-POWDER2 Indigo Edge 3.660; B Sandstone 3.740 (+0.080 below +0.250)'
  room['surfaces']=[('DRY vanity WALL',env['indigo'])]
  room['cost']=('R039 authenticated original gross DRY vanity WALL area-rate $332.10/physical copy, '
                'two copies; source 15% waste included ONCE; wood floor retained; no '
                'LEVEL/PAN/NICHE/CEILING tile or separate floor charge. Not carton-rounded '
                'or Chicago landed; budget FILL IN.')
  room['alts']=('A Indigo Edge four-seat 3.660/5 qualified; materially distinct B Elm Tones '
                'Sandstone 2x20 four-seat 3.740/5 qualified, but +0.080 < incumbent '
                'protection +0.250, so A is retained. Sandstone photo if shown is maker '
                'Sandstone/Copper MIXED installation, NOT Sandstone-only. No owner approval.')
  room['holds']=d['technical_holds']
  room['plumbing']='Hansgrohe Tecturis E 73072341 Brushed Black Chrome deck-mounted faucet; basin UNSELECTED; DRY vanity WALL, existing WOOD floor; no tiled LEVEL/PAN/NICHE/CEILING'

# Established R037 composer recreates already verified R036/R037/R038 page content.
# Execute ONLY its writer suffix, with R039 destination names.
r037=ROOT/'scratch/r037_refresh_owner_review.py'
r037_source=r037.read_text(encoding='utf-8')
writer_marker="assert len(R)==13 and len(set(r['id'] for r in R))==13"
assert r037_source.count(writer_marker)==1
tail=writer_marker+r037_source.split(writer_marker,1)[1]
tail=tail.replace('R037_13_ROOM_OWNER_REVIEW_PAGES','R039_13_ROOM_OWNER_REVIEW_PAGES')
tail=tail.replace('r037-13-owner-review-PROVISIONAL','r039-13-owner-review-PROVISIONAL')
tail=tail.replace('font-size:10.2pt;line-height:1.28','font-size:10pt;line-height:1.25')
tail=tail.replace('padding:5px 7px;vertical-align:top','padding:4px 7px;vertical-align:top')
exec(compile(tail,str(r037),'exec'),ctx)
OUT=ROOT/'deliverables/r039-13-owner-review-PROVISIONAL'
assert len(list(OUT.glob('*.html')))==14
assert all((OUT/(r['id']+'.html')).exists() for r in R)
idx=(ROOT/'deliverables/TILE_SELECTIONS_REVIEW.html').read_text(encoding='utf-8')
assert idx.count('<article class="room">')==13
assert idx.count('<div class="item">')==30  # TX-POWDER deliberately has no selected surface.
assert idx.count('Single-room owner packet')==13
assert 'BLOCKED — NO QUALIFIED R039 VANITY WALL TILE' in idx
assert idx.count('Sandstone/Copper MIXED maker installation')>=1
blocked=(OUT/'TX-POWDER.html').read_text(encoding='utf-8')
assert 'NO qualified tile selected' in blocked
assert 'Haze $379.37' in blocked and 'Pienza $95.08' in blocked
assert 'TUB/WALK-IN remains UNSELECTED' in (OUT/'TX-BATH3.html').read_text(encoding='utf-8')
print('PASS R039: 13 PROVISIONAL HTML owner pages and combined, 30 selected surfaces; TX-POWDER BLOCKED/no tile selected; TX-POWDER2 Indigo defended; original R038 corrections preserved. PDFs still require printing.')
