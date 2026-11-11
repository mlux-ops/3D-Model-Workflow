"""R038 owner review built from current authenticated R036/R037 source data and R038 decisions."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
decision_path=ROOT/'state/ROUND038_TWO_WET_BATH_DECISIONS.json'
assert decision_path.is_file(),'No authenticated R038 board decision'
decision38=json.loads(decision_path.read_text(encoding='utf8'))
assert (decision38['criterion_count'],decision38['seat_means_count'],decision38['weighted_count'])==(76,16,4)
assert set(decision38['rooms'])=={'PH-BATH2','TX-BATH3'} and decision38['owner_approvals']==0
source=(ROOT/'scratch/r037_refresh_owner_review.py').read_text(encoding='utf8')
marker='assert len(R)==13 and len(set(r[\'id\'] for r in R))==13'
assert source.count(marker)==1
prefix,suffix=source.split(marker,1)
ctx={'__file__':str(ROOT/'scratch/r037_refresh_owner_review.py'),'__name__':'r038_reuse_previous_round_data'}
exec(compile(prefix,str(ROOT/'scratch/r037_refresh_owner_review.py'),'exec'),ctx)
env=ctx['env'];R=env['R']
for room in R:
    rid=room['id']
    if rid not in decision38['rooms']:continue
    d=decision38['rooms'][rid]
    assert not d['changed'] and d['four_seat_complete'] and d['selected_letter']=='A'
    room['status']='PROVISIONAL CHAMPION — R038 defended'
    room['score']='R038 '+d['selected_id']+' '+format(d['selected_score'],'.3f')+'; alternate B '+format(d['other_score'],'.3f')
    pan_basis = (
      'PH-BATH2 owner-selected Duravit TUB: tiled shower PAN not part of this room program; NO separate PAN material quantity or charge.'
      if rid=='PH-BATH2' else
      'TX-BATH3 TUB/WALK-IN remains UNSELECTED: original 42.5 SF bathroom LEVEL gross only; additional optional WALK-IN POINT PAN SF and cost NULL (not zero), not included or charged until individually measured and selected.'
    )
    room['cost']=('R038 authenticated original gross material area-rate $'+format(d['material_gross_rate_per_copy_usd'],'.2f')
      +'/physical copy (two copies), historic 15% waste already included once. NOT carton-rounded or Chicago landed; owner budget FILL IN. '
      +pan_basis)
    room['alts']='R038 four independently scored original seats: '+d['decision_summary']+'. No owner approval.'
    room['holds']=d['technical_holds']
# Preserve earlier owner presentation corrections and composer; only change round-specific destination labels.
tail=marker+suffix
tail=tail.replace('R037_13_ROOM_OWNER_REVIEW_PAGES','R038_13_ROOM_OWNER_REVIEW_PAGES')
tail=tail.replace('r037-13-owner-review-PROVISIONAL','r038-13-owner-review-PROVISIONAL')
tail=tail.replace('r037-13-owner-review-PROVISIONAL','r038-13-owner-review-PROVISIONAL')
# The previous composer defines env, original R035 marker, and correct 13-card nesting.
exec(compile(tail,str(ROOT/'scratch/r037_refresh_owner_review.py'),'exec'),ctx)
OUT=ROOT/'deliverables/r038-13-owner-review-PROVISIONAL'
assert len(list(OUT.glob('*.html')))==14
index=(ROOT/'deliverables/TILE_SELECTIONS_REVIEW.html').read_text(encoding='utf8')
assert index.count('<article class="room">')==13
assert index.count('<div class="item">')==31
assert index.count('Single-room owner packet')==13
assert index.count('Sandstone/Copper MIXED maker installation')>=1
assert all((OUT/(r['id']+'.html')).exists() for r in R)
print('PASS R038 13 PROVISIONAL owner HTML pages, combined print source, 31 surface rows inside 13 cards, 13 links, mixed-photo disclosure; PDFs not yet printed.')
