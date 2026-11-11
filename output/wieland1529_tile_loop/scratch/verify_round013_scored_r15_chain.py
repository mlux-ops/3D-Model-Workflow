"""Read-only end-to-end QA of formally scored R013 and signed owner R12-R15."""
from pathlib import Path
from decimal import Decimal
import csv,hashlib,json

ROOT=Path(__file__).resolve().parents[1]
def fp(p):
    b=p.read_bytes()
    return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}

score=ROOT/'state/ROUND013_SCORING.json'
s=json.loads(score.read_bytes())
sub=ROOT/'state/ROUND013_SUBMISSION.json'
dispatch=ROOT/'state/ROUND013_CRITIC_DISPATCH.json'
coll=ROOT/'state/ROUND013_CRITIC_COLLECTION.json'
clear=ROOT/'state/ROUND013_COLLECTION_REVIEWER_CLEARANCE.json'
assert all(json.loads(p.read_bytes())['all_critic_scores'] is None for p in (sub,dispatch,coll))
assert fp(sub)['sha256']==s['source_submission_sha256']
assert fp(dispatch)['sha256']==s['source_dispatch_sha256']
assert fp(coll)['sha256']==s['source_collection_sha256']
assert fp(clear)['sha256']==s['reviewer_clearance_receipt_sha256']
assert not s['owner_approval'] and not s['procurement_release']
assert s['verification']=={'frozen_candidates':6,'original_critics':12,'criteria':114,'recalculated_seat_means':24,'local_links':333,'valid':True}
e=json.loads(sub.read_bytes())
c=json.loads(coll.read_bytes())
for rid,parts in e['candidate_files'].items():
    for letter,expected in parts.items():
        p=ROOT/f'rooms/{rid}/board/round-013/candidates/{letter}.md'
        assert fp(p)==expected,(rid,letter)
    for seat,expected in c['report_files'][rid].items():
        p=ROOT/f'rooms/{rid}/board/round-013/{seat}.md'
        actual=fp(p)
        assert actual['bytes']==expected['bytes'] and actual['sha256']==expected['sha256'],(rid,seat)
        assert actual['sha256']==s['room_results'][rid]['critic_file_fingerprints'][seat.replace('critic-','')]['sha256']

rooms=json.loads((ROOT/'state/ROOMS.json').read_bytes())['rooms']
assert len(rooms)==13 and len(set(r['id'] for r in rooms))==13
by={r['id']:r for r in rooms}
for rid,row in s['room_results'].items():
    r=by[rid]
    assert r['last_round']==13 and r['status']=='blocked'
    assert r['champion_id'] is None and r['champion_score'] is None and r['owner_status'] is None
    assert r['board_round_013']==row
    assert r['board_round_010']['status']=='blocked'
    assert 'Round013 formal distinct-turn scoring' in (ROOT/f'rooms/{rid}/history.md').read_text(encoding='utf-8')
    assert (ROOT/f'rooms/{rid}/board/round-013/ROUND_REPORT.md').is_file()
    assert 'Round013 BLOCKED' in (ROOT/f'rooms/{rid}/champion.md').read_text(encoding='utf-8')
assert sum(Decimal(str(r['carried_quote_material_subtotal_usd_per_unit']))*r['unit_count'] for r in rooms)==Decimal('23572.44')

manifest_counts={12:6,13:5,14:3,15:4}
for num,count in manifest_counts.items():
    directory=ROOT/f'deliverables/integrated-r{num}'
    m=json.loads((directory/'MANIFEST.json').read_bytes())
    assert len(m['outputs'])==count
    for name,meta in m['outputs'].items():
        assert fp(directory/name)==meta,(num,name)
    assert not m.get('owner_approval',m.get('owner_approved')) and not m['procurement_release']

r15=ROOT/'deliverables/integrated-r15'
m15=json.loads((r15/'MANIFEST.json').read_bytes())
assert m15['r013_scoring_sha256']==fp(score)['sha256']
assert m15['r013_submission_sha256']==fp(sub)['sha256']
assert m15['r013_collection_sha256']==fp(coll)['sha256']
assert m15['r14_corrected_manifest_sha256']==fp(ROOT/'deliverables/integrated-r14/MANIFEST.json')['sha256']
with (r15/'R15_13_ROOM_SCORED_OWNER_RELEASE_REGISTER.csv').open(encoding='utf-8-sig',newline='') as f:
    release=list(csv.DictReader(f))
with (r15/'R15_65_TRADE_ACTIONS_LATEST_SCORES.csv').open(encoding='utf-8-sig',newline='') as f:
    actions=list(csv.DictReader(f))
assert len(release)==13 and len(actions)==65
assert len([r for r in actions if r['group']=='floor_pan_and_drain'])==13
assert set(r['room'] for r in release)==set(by)
assert sum(Decimal(r['historical_source_usd_two_units']) for r in release)==Decimal('23572.44')
assert all(r['owner_approved']=='FALSE' and r['gc_procurement_release']=='FALSE' and r['verified_1529_model']=='FALSE' for r in release)
assert all(r['purchase_release']=='False' and r['owner_approval']=='False' and r['exact_gc_approval']=='False' for r in actions)
assert all('Brizo LINEAR primaries require BR73480' not in r['measurable_next_closure'] for r in actions)
for rid in by:
    q=next(r['measurable_next_closure'] for r in actions if r['room']==rid and r['group']=='floor_pan_and_drain')
    assert q and len(q)>100,(rid,q)
    if rid in ('PH-POWDER','TX-POWDER','TX-POWDER2'):
        assert 'NO tiled shower PAN' in q
    if rid in ('PH-BATH2','TX-BATH2','TX-BATH4'):
        assert 'NO tiled shower PAN' in q
    if rid in ('PH-WC','TX-WC'):
        assert 'no independent' in q.lower() or 'no separately' in q.lower()
assert m15['original_four_unit_material_only_usd']==23572.44
assert m15['original_gross_waste_included_pct']==15
print('PASS 6 immutable R013 candidates + 12 original critics + 114 criteria/24 means/333 links,')
print('PASS scored 13-room status, all 18 SHA-signed outputs across R12-R15, 13 R15 release rows and 65 source-specific trade actions,')
print('PASS original four-unit material-only $23572.44, 15% once, no certified 1529 model, no owner/GC release')
print('SCORED_SHA',fp(score)['sha256'],'CURRENT_R15_MANIFEST_SHA',fp(r15/'MANIFEST.json')['sha256'])
