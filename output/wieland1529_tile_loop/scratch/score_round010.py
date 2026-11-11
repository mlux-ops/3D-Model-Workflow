from pathlib import Path
import json,re,hashlib,decimal
ROOT=Path(__file__).resolve().parents[1]
ROOMS=('PH-PRIMARY','PH-BATH2','PH-BATH4')
SEATS={'market':(.30,4),'design':(.25,5),'build':(.25,5),'cost':(.20,5)}
submission=json.loads((ROOT/'state/ROUND010_SUBMISSION.json').read_text(encoding='utf-8'))
collection=json.loads((ROOT/'state/ROUND010_CRITIC_COLLECTION.json').read_text(encoding='utf-8'))
assert submission['round']==10 and submission['phase']=='2-board' and submission['all_critic_scores'] is None
assert collection['round']==10 and not collection['weighted_scoring_complete'] and collection['all_critic_scores'] is None
assert set(submission['candidate_files'])==set(collection['report_files'])==set(ROOMS)
result={'as_of':'2026-11-06','round':10,'source_submission':'state/ROUND010_SUBMISSION.json','source_submission_sha256':hashlib.sha256((ROOT/'state/ROUND010_SUBMISSION.json').read_bytes()).hexdigest(),'source_critic_collection':'state/ROUND010_CRITIC_COLLECTION.json','source_collection_sha256':hashlib.sha256((ROOT/'state/ROUND010_CRITIC_COLLECTION.json').read_bytes()).hexdigest(),'verification':{'candidate_frozen_files':6,'actual_independent_critiques':12,'criterion_checks':0,'local_links':0,'all_valid':False},'room_results':{}}
def one_decimal_mean(vals):
 return float((decimal.Decimal(str(sum(vals)))/decimal.Decimal(len(vals))).quantize(decimal.Decimal('0.1'),rounding=decimal.ROUND_HALF_UP))
def parse_score(block,rid,seat,letter):
 lines=[line for line in block.splitlines() if re.search(r'(?i)(?:overall.*(?:seat\s+mean|seat\s+score)|overall_score|seat_score)',line) and '/ 5.0' in line.replace('/5.0','/ 5.0')]
 assert len(lines)==1,(rid,seat,letter,'seat score line count',lines)
 match=re.findall(r'(?<!\d)([1-5](?:\.\d+)?)\s*/\s*5\.0',lines[0])
 assert match,(rid,seat,letter,'seat score parse',lines[0])
 return float(match[-1])
for rid in ROOMS:
 roomdir=ROOT/'rooms'/rid/'board/round-010'
 original=submission['candidate_files'][rid]
 role_mapping=json.loads((roomdir/'_key.json').read_text(encoding='utf-8'))
 assert set(role_mapping)==set(original) and len(original)==2
 hist=next(letter for letter,role in role_mapping.items() if 'historic' in role)
 revised=next(letter for letter in role_mapping if letter!=hist)
 for letter,rec in original.items():
  actual=(roomdir/'candidates'/(letter+'.md')).read_bytes()
  assert len(actual)==rec['bytes'] and hashlib.sha256(actual).hexdigest()==rec['sha256'],(rid,letter,'candidate SHA mismatch')
 crit_hashes={};crit_scores={k:{} for k in original};crit_evidence={}
 for seat,(weight,n) in SEATS.items():
  f=roomdir/('critic-'+seat+'.md')
  assert f.is_file(),(rid,seat,'critic missing')
  raw=f.read_bytes();t=raw.decode('utf-8')
  receipt=collection['report_files'][rid][seat]
  assert len(raw)==receipt['bytes'] and hashlib.sha256(raw).hexdigest()==receipt['sha256'],(rid,seat,'critic original SHA mismatch')
  assert len(raw)>2000 and all(tag in t.lower() for tag in ('top_fix','gate_flags','confidence','dcof')),(rid,seat,'report incomplete')
  assert not re.search(r'(?i)_key\.json|state/ROOMS\.json|state/LEDGER\.md|room[s]?/[^ \n]*history\.md|room[s]?/[^ \n]*champion\.md|round.?00[1-9]',t),(rid,seat,'blind/historical leak')
  assert not re.search(r'(?i)\bsteam\b',t),(rid,seat,'owner-excluded topic')
  chunks=re.split(r'(?im)^##\s+Candidate\s+([A-Z])\b[^\n]*\n',t)
  assert len(chunks)==5,(rid,seat,'candidate section count',len(chunks))
  assert set(chunks[1::2])==set(original),(rid,seat,'letter set',chunks[1::2])
  crit_hashes[seat]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
  for letter,block in zip(chunks[1::2],chunks[2::2]):
   table=[]
   for line in block.splitlines():
    if not line.startswith('|'):continue
    cells=[x.strip() for x in line.strip('|').split('|')]
    if len(cells)!=3:continue
    sc=re.sub(r'\*','',cells[1]).strip()
    sc=re.sub(r'\s*/\s*5\s*$','',sc).strip()
    if re.fullmatch(r'[1-5](?:\.\d+)?',sc):table.append((float(sc),cells[2]))
   assert len(table)==n,(rid,seat,letter,'criterion count',len(table),table)
   assert all(len(ev)>35 and ('[' in ev or 'http' in ev or 'OT0' in ev or 'source' in ev.lower()) for _,ev in table),(rid,seat,letter,'evidence incomplete')
   scores=[v for v,_ in table]
   actual_score=one_decimal_mean(scores)
   reported=parse_score(block,rid,seat,letter)
   assert abs(reported-actual_score)<1e-6,(rid,seat,letter,'criterion arithmetic',reported,actual_score,scores)
   assert len(re.findall(r'(?i)\btop_fix\s*:',block))==1 and len(re.findall(r'(?i)\bgate_flags\s*:',block))==1,(rid,seat,letter,'gate/fix count')
   assert 'FAIL' in block and 'confidence' in block.lower(),(rid,seat,letter,'gate description')
   for link in re.findall(r'\]\(([^)]+)\)',block):
    if link.startswith(('https://','http://','#','mailto:')):continue
    assert (f.parent/link.split('#')[0]).exists(),(rid,seat,letter,'missing citation',link)
    result['verification']['local_links']+=1
   crit_scores[letter][seat]=reported
   crit_evidence.setdefault(letter,{})[seat]={'criterion_scores':scores,'mean':reported}
   result['verification']['criterion_checks']+=n
 rr={'room':rid,'round':10,'critics_complete':True,'critic_file_fingerprints':crit_hashes,'weights':{s:v[0] for s,v in SEATS.items()},'incumbent_letter':hist,'challenger_letter':revised,'candidates':{}}
 for letter in sorted(original):
  ss=crit_scores[letter]
  weighted=round(sum(ss[s]*SEATS[s][0] for s in SEATS)+1e-9,2)
  fails=['FAIL: actual SKU-and-finish-specific bath LEVEL-floor wet DCOF raw numeric test report remains unavailable; a manufacturer reported >0.50 bound or Target >=0.42 is not the approved measured test point']
  if rid=='PH-PRIMARY':
   fails+=['FAIL: actual 48-in Brizo selected LINEAR pan tile exact maker lab wet-DCOF remains unavailable',
   'HOLD: Prime RL21 hex product order variant and manufacturer-approved linear rough/grate/membrane/slope section, HNC-to-RL21 transition and verified 1529 site geometry unavailable']
   if letter==hist:fails+=['FAIL: Cortar Bone Reed relief in shower lacks individual maker Wet Areas approval']
  elif rid=='PH-BATH2':
   fails+=['PASS for wall only: individual ELM Tones Sapphire 2x20 Glossy and Sandstone Wet Areas approved; Duravit and Matte White actual tub, NO tiled shower pan',
   'HOLD: tub flange/vanity wall/niche opening and net return, exact level tile and threshold geometry, finish and supplier offer unresolved']
  elif rid=='PH-BATH4':
   fails+=['FAIL: selected Brizo BT062415-BNX 4-in SQUARE POINT walk-in shower pan exact maker SKU wet DCOF unavailable',
   'HOLD: old 35-versus-27 SF owner/source discrepancy, original Cortar Charcoal Soft-vs-AntiSlip supplier finish, actual four-plane 4-in point drain/pan footprint unmeasured']
   if letter==hist:fails+=['FAIL: full wet Cortar Bone Ribbed Relief and Clara Caviar shower niche both lack individual manufacturer Wet Areas listings']
  fails+=['HOLD: true native 1529 model/site verification, exact current Chicago landed material/installed bid and lot/lead, signed owner room cap and selection unavailable; cannot infer 125% cost gate failure']
  rr['candidates'][letter]={'role':role_mapping[letter],'seat_scores':ss,'criterion_scores':crit_evidence[letter],'weighted_score':weighted,'minimum_critic_score':min(ss.values()),'all_seat_minimum_3_pass':min(ss.values())>=3.0,'hard_gates_pass':False,'gate_reasons':fails,'source_candidate_sha256':original[letter]['sha256']}
 old=rr['candidates'][hist];new=rr['candidates'][revised]
 rr['margin']=round(new['weighted_score']-old['weighted_score'],2)
 rr.update(status='blocked',decision='both_candidates_blocked_exact_numeric_wet_floor_or_pan_gate',champion_id=None,champion_score=None,accepted_challenger=False,owner_approved=False,procurement_release=False,provisional_design_preference=revised if rr['margin']>0 else hist,report='board/round-010/ROUND_REPORT.md')
 result['room_results'][rid]=rr
result['verification']['all_valid']=True
dest=ROOT/'state/ROUND010_SCORING.json'
assert not dest.exists(),'Existing Round010 score would be overwritten; inspect first'
dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
for rid,rr in result['room_results'].items():
 a,b=rr['incumbent_letter'],rr['challenger_letter']
 print(rid,'historic',a,rr['candidates'][a]['weighted_score'],'revised',b,rr['candidates'][b]['weighted_score'],'delta',rr['margin'],'min revised',rr['candidates'][b]['minimum_critic_score'],'BLOCKED')
print('PASS',result['verification']['actual_independent_critiques'],'frozen SHA independent critics,',result['verification']['candidate_frozen_files'],'frozen candidate SHA,',result['verification']['criterion_checks'],'criterion rows,',result['verification']['local_links'],'resolved citations; no owner/procurement release')
