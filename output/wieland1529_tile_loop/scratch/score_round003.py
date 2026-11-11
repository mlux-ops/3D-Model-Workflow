"""Round003 independent four-seat audit and score; no synthetic critics."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1]
rooms=("TX-PRIMARY","TX-POWDER","TX-POWDER2")
weights={"market":.30,"design":.25,"build":.25,"cost":.20}
receipt=json.loads((R/"state/ROUND003_SUBMISSION.json").read_text(encoding="utf-8"))
register=json.loads((R/"state/ROOMS.json").read_text(encoding="utf-8"))
byid={x["id"]:x for x in register["rooms"]}
out={}
for rid in rooms:
 folder=R/"rooms"/rid/"board/round-003"
 private=json.loads((folder/"_key.json").read_text(encoding="utf-8"))
 letters=[x for x in private if x in ("A","B","C")]
 assert len(letters)==2
 assert len(list((folder/"candidates").glob("*.md")))==2
 for let in letters:
  p=folder/"candidates"/(let+".md")
  a=receipt["candidates"][rid][let]
  assert len(p.read_bytes())==a["bytes"] and hashlib.sha256(p.read_bytes()).hexdigest()==a["sha256"],(rid,let,"CHANGED PACKET")
 assert byid[rid]["round_003_submission"]["status"]=="blind_review_pending"
 scores={}
 for seat in weights:
  p=folder/("critic-"+seat+".md")
  assert p.exists(),("MISSING",rid,seat)
  t=p.read_text(encoding="utf-8")
  assert "top_fix" in t and "gate_flags" in t and "confidence" in t.lower(),(rid,seat)
  # Critics must not have made a private identity allegation.
  assert not re.search(r"(?i)private _key|v4 incumbent is|challenger is candidate",t),(rid,seat)
  sep=re.split(r"(?m)^## Candidate ([ABC])\b[^\n]*\n",t)
  assert len(sep)==5,(rid,seat,"candidate sections",len(sep))
  headline_scores=dict(re.findall(r"(?im)^## Candidate ([ABC])[^\n]*?overall seat score\D{0,12}([1-5]\.[0-9])",t))
  candidates={}
  for letter,portion in zip(sep[1::2],sep[2::2]):
   assert letter in letters and letter not in candidates
   if seat=="cost":
    m=re.search(r"(?i)\bseat_score:\s*([1-5]\.[0-9])",portion)
   elif seat=="design":
    m=re.search(r"(?i)\boverall_score:\s*([1-5]\.[0-9])",portion)
   else:
    m=re.search(r"(?i)(?:overall seat score|overall.*?seat score)\D{0,15}([1-5]\.[0-9])",portion)
   assert m or letter in headline_scores,(rid,seat,letter,"seat score not found")
   score=float(m.group(1) if m else headline_scores[letter])
   table=[ln for ln in portion.splitlines() if ln.startswith("|") and not ln.startswith("|---")]
   assert len(table)>=(5 if seat=="market" else 6),(rid,seat,letter,"no criteria",len(table))
   criteria=[]
   for ln in table[1:]:
    cols=[x.strip() for x in ln.split("|")[1:-1]]
    if len(cols)<3:continue
    mm=re.search(r"\b([1-5](?:\.[0-9])?)(?:\s*/\s*5)?\b",cols[1].replace("*",""))
    if mm:criteria.append(float(mm.group(1)))
   assert len(criteria)>=4,(rid,seat,letter,criteria)
   mean=sum(criteria)/len(criteria)
   assert abs(mean-score)<=.051,(rid,seat,letter,criteria,score,mean)
   section_low=portion.lower()
   assert "top_fix" in section_low and "gate_flags" in section_low and "confidence" in section_low
   candidates[letter]={"score":score,"criteria":criteria,"mean":round(mean,3)}
  assert set(candidates)==set(letters)
  scores[seat]=candidates
 evaluations={}
 for let in letters:
  votes={s:scores[s][let]["score"] for s in weights}
  total=round(sum(votes[s]*weights[s] for s in weights),3)
  reasons=[]
  if rid=="TX-PRIMARY":
   reasons=["FAIL: no exact measured SKU wet DCOF for floor and pan"]
   if let=="A":reasons.append("FAIL/HOLD: Clay Ribbed lacks Wet Areas listing if used inside shower")
   else:reasons.append("HOLD: PF07 12x24 plus 2x2 linear-drain pan slope/position unverified")
  elif rid=="TX-POWDER":
   reasons=["Dry wall only; wood floor => tile wet-floor DCOF N/A","HOLD: 1529 geometry, 70:30 color split and faucet mounting not verified"]
  else:
   reasons=["Dry wall only; wood floor => tile wet-floor DCOF N/A","HOLD: owner basin unselected, fixture/backing dimensions unknown"]
   if let=="A":reasons.append("HOLD: smooth panel material, area, price and washability unverified")
  evaluations[let]={"role":private[let],"seat_scores":votes,"weighted_score":total,"minimum_critic_score":min(votes.values()),
                    "hard_gates_pass":False if rid=="TX-PRIMARY" else True,
                    "gate_assessment":"floor and wet-wall hard gates NOT APPLICABLE; no proven owner veto, impossible geometry, discontinuation or >125% budget overrun, but source geometry, actual Chicago stock and install quote require later verification" if rid!="TX-PRIMARY" else "wet-floor DCOF definitively fails strict board evidence",
                    "gate_reasons":reasons}
 incumbent=next(x for x in letters if "incumbent" in private[x])
 challenger=next(x for x in letters if x!=incumbent)
 margin=round(evaluations[challenger]["weighted_score"]-evaluations[incumbent]["weighted_score"],3)
 if rid=="TX-PRIMARY":
  decision="blocked_no_qualified_floor_or_pan"
  candidate_status="blocked";champion_id=None;champion_score=None
 else:
  # Current local stock/date and measured geometry are project release HOLDS, not
  # automatic board hard-fails: rules gate discontinued/no US distribution or proven
  # impossible geometry. Dry-wall/wood floor DCOF is not applicable.
  if margin>=.25 and evaluations[challenger]["minimum_critic_score"]>=3 and evaluations[challenger]["hard_gates_pass"] is True:
   decision="accept_challenger";candidate_status="active";champion_id="round-003-"+challenger;champion_score=evaluations[challenger]["weighted_score"]
  else:
   decision="retain_v4_until_full_gate_clearance";candidate_status="active";champion_id="v4-"+rid;champion_score=evaluations[incumbent]["weighted_score"]
 out[rid]={"room":rid,"round":3,"critics_complete":True,"weights":weights,"candidates":evaluations,
           "incumbent_letter":incumbent,"challenger_letter":challenger,"margin":margin,
           "decision":decision,"status":candidate_status,"champion_id":champion_id,
           "champion_score":champion_score,"accepted_challenger":decision=="accept_challenger",
           "report":"board/round-003/ROUND_REPORT.md"}
 print(rid,"v4",incumbent,evaluations[incumbent]["weighted_score"],
       "challenger",challenger,evaluations[challenger]["weighted_score"],"delta",margin,
       "minimum",evaluations[challenger]["minimum_critic_score"],decision)
(R/"state/ROUND003_SCORING.json").write_text(json.dumps({"as_of":"2026-11-06","room_results":out},indent=2)+"\n",encoding="utf-8")
print("PASS: 12 complete independent critique files, 6 exact hashes, seat criteria re-averaged")
