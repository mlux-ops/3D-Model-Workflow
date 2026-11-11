"""R017 pre-review local hygiene: exact same-round source surgery, no critic ever dispatched."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
S=R/'state/ROUND017_SUBMISSION.json'
before=S.read_bytes()
old_hash=hashlib.sha256(before).hexdigest()
assert old_hash=='8ffdee0cd00978e7ad0e702f4cccc6f0f59382a4ff13d9377b851b2222e173a1'
sub=json.loads(before)
bad='**Non-transferable program:** PH/TX BATH3 owner TUB-vs-WALK-IN UNSELECTED. TUB requires newly owner-selected tub and dedicated tub waste/overflow with no tiled shower PAN; selected Delta/Brizo square shower drain MUST NOT be called tub waste. WALK-IN only retains owner-selected SQUARE POINT and independently approved 4-plane PAN. PH-BATH4 remains actual WALK-IN 4-in SQUARE POINT; PH-PRIMARY remains selected Brizo BNX 48-in LINEAR + BR73480 with separate Duravit tub, NO added niche, PH WC LEVEL included once. Room-specific rule applies, no unrelated fixture substitution.'
replacements={
 'PH-BATH3':'**Non-transferable room program:** PH-BATH3 owner TUB versus WALK-IN UNSELECTED; PH basin UNSELECTED. TUB requires owner-selected real bathtub and dedicated tub waste/overflow, alcove/flange section, no tiled PAN; selected Delta DT062412 CHROME 4-in SQUARE POINT is a shower drain, NOT bathtub waste. WALK-IN conditionally keeps that Delta point shower drain and requires its own fully approved four-plane small-format POINT PAN. Hansgrohe Chrome Croma/Ecostat selected shower fixtures remain. Do not infer an owner decision or replace the selected shower drain.',
 'TX-BATH3':'**Non-transferable room program:** TX-BATH3 owner TUB versus WALK-IN UNSELECTED; do not import PH Bath3 basin-unselected condition. TUB requires owner-selected bathtub with separate dedicated tub waste/overflow and revised alcove/flange, tiled shower PAN N/A. WALK-IN keeps selected Brizo BT062415-BNX Black Onyx 4-in SQUARE POINT shower drain and separate approved 4-plane small-format POINT PAN. Brizo Roccesco Black Onyx shower components remain selected; no 48-in linear substitution.',
 'PH-BATH4':'**Non-transferable room program:** PH-BATH4 is an ACTUAL WALK-IN shower (NOT owner-conditional tub) and selected Brizo BT062415-BNX Brilliance Black Onyx 4-in SQUARE POINT shower drain (NOT 48-in linear). A separate four-plane small-format POINT PAN and distinct LEVEL must be independently wet-tested; actual drain/corner/threshold, glass and factory liner remain unverified. Original 35 vs 27 SF and Soft/AntiSlip discrepancies remain, source vendor 214.4 SF wall issue is audit only.',
 'PH-PRIMARY':'**Non-transferable room program:** PH-PRIMARY uses the actual owner-selected Brizo BT0734816-BNX Brilliance Black Onyx 48-in LINEAR shower drain with separate BR73480 rough, plus the separate selected Duravit bathtub, no added Primary shower NICHE. PH-WC LEVEL floor is already in the Primary historical material area ONCE. The reversible selected solid-BNX-grate versus tile-in option is an installation configuration study and is not a drain replacement. LINEAR PAN needs a separate exact raw numeric wet test and factory approved membrane/slope/grate/rough section.'
}
def signature(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
changed={}
for room,variants in sub['blind_source_candidates'].items():
 for letter,rec in variants.items():
  p=R/rec['path'];original=p.read_bytes()
  assert signature(p)=={'sha256':rec['sha256'],'bytes':rec['bytes']}
  txt=original.decode('utf-8')
  assert txt.count(bad)==1,(room,letter,'source phrase drift')
  txt=txt.replace(bad,replacements[room])
  assert bad not in txt
  assert txt.splitlines()[2]=='This option is submitted for independent blind technical review ONLY; no historical/challenger status, prior results, owner approval, original source price substitution or authorization to order may be inferred.'
  p.write_text(txt,encoding='utf-8')
  after=signature(p)
  changed[f'{room}/{letter}']={'path':rec['path'],'before':{'sha256':rec['sha256'],'bytes':rec['bytes']},'after':after}
  rec.update(after)
assert len(changed)==8
for room,m in sub['confidential_prime_only_mappings'].items():
 assert signature(R/m['path'])=={'sha256':m['sha256'],'bytes':m['bytes']}
sub['source_revision']='same-R017 source-only internal pre-review fix: room-specific actual fixture/program lines replacing cross-room generic paragraph; all neutral alternatives, map identities, maker research, original accounting and gates remain'
S.write_text(json.dumps(sub,indent=2)+'\n',encoding='utf-8')
receipt={'round':17,'reason':'PRE-REVIEW original-room program hygiene, NOT independent Reviewer FIX and no critic dispatched','old_submission_sha256':old_hash,'new_submission_sha256':signature(S)['sha256'],'changed':changed,'unchanged_private_keys':True,'unchanged_shared_maker_research':True,'original_critic_dispatch':'NOT_DISPATCHED','scores':None,'owner_approval':False,'GC_release':False,'procurement_release':False}
path=R/'state/ROUND017_INTERNAL_ROOM_SCOPE_BLIND_HYGIENE.json'
assert not path.exists()
path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('PASS R017 room-specific source correction 8 packet identities preserved via new frozen SHA and exact before/after receipt; no critic dispatch')
print('R017_NEW_SHA',signature(S)['sha256'])
print('R017_HYGIENE_RECEIPT_SHA',signature(path)['sha256'])
