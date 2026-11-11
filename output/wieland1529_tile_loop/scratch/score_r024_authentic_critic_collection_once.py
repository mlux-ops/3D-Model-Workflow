"""Record-only scoring from four authentic R024 blind specialist files; never promote unknown gates."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[1]
ROOMS={x["id"]:x for x in json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf8"))["rooms"]}
ORIG=ROOT/"state/ROUND024_FROZEN_THREE_DURAVIT_TUB_BLIND_SOURCE.json"
DISPATCH=ROOT/"state/ROUND024_FRESH_FOUR_CRITIC_DISPATCH.json"
CLEAR=ROOT/"state/ROUND024_FRESH_INDEPENDENT_REVIEWER_CLEARANCE.json"
RESULT=ROOT/"state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json"
assert not RESULT.exists()
source=json.loads(ORIG.read_text(encoding="utf8"))
dispatch=json.loads(DISPATCH.read_text(encoding="utf8"))
assert dispatch["reviewer_worker"]=="worker-16" and "CONTINUE" in dispatch["reviewer_verdict"]
assert set(dispatch["specialists"])=={"critic-market","critic-design","critic-build","critic-cost"}
assert all(ROOMS[r]["status"]=="blocked" and ROOMS[r]["champion_id"] is None for r in source["focus_rooms"])
for path,meta in {**source["neutral_candidates"],**source["immutable_parent_receipts"]}.items():
 data=(ROOT/path).read_bytes()
 assert len(data)==meta["bytes"] and hashlib.sha256(data).hexdigest()==meta["sha256"],path

weights={"critic-market":Decimal(".30"),"critic-design":Decimal(".25"),"critic-build":Decimal(".25"),"critic-cost":Decimal(".20")}
expected={
 "PH-BATH2":{"critic-market":(Decimal("4.0"),Decimal("3.8")),"critic-design":(Decimal("3.6"),Decimal("3.8")),"critic-build":(Decimal("3.8"),Decimal("3.2")),"critic-cost":(Decimal("3.4"),Decimal("2.0"))},
 "TX-BATH2":{"critic-market":(Decimal("3.5"),Decimal("3.8")),"critic-design":(Decimal("3.8"),Decimal("3.4")),"critic-build":(Decimal("3.8"),Decimal("3.2")),"critic-cost":(Decimal("3.2"),Decimal("2.0"))},
 "TX-BATH4":{"critic-market":(Decimal("4.0"),Decimal("3.3")),"critic-design":(Decimal("3.8"),Decimal("3.4")),"critic-build":(Decimal("3.4"),Decimal("3.0")),"critic-cost":(Decimal("2.2"),Decimal("2.0"))}
}
def round1(x):
 return x.quantize(Decimal("0.1"),rounding=ROUND_HALF_UP)
collection={}
results={}
for rid in source["focus_rooms"]:
 scores={}
 for seat,(a,b) in expected[rid].items():
  path=ROOT/"rooms"/rid/"board/round-024"/(seat+".md")
  content=path.read_text(encoding="utf8")
  original=path.read_bytes()
  collection[str(path.relative_to(ROOT)).replace("\\","/")]={"sha256":hashlib.sha256(original).hexdigest(),"bytes":len(original),"worker":dispatch["specialists"][seat]["worker"]}
  # Each candidate has its own heading, criterion table, one arithmetic mean, top_fix and gates.
  sections=re.split(r"(?m)^## (?:Neutral |Option |Candidate )?(?:option )?([AB])\s*(?:[—-]|\n)",content)
  if len(sections)!=5:
   # Fallback for headings of the form '## Neutral A —' and '## Neutral option A —'.
   chunks=list(re.finditer(r"(?m)^##\s+Neutral\s+(?:option\s+)?([AB])\s*[—-]",content))
   assert len(chunks)==2,(rid,seat,"candidate header count",len(chunks))
   part={chunks[i].group(1):content[chunks[i].start():chunks[i+1].start() if i+1<2 else len(content)] for i in range(2)}
  else:
   part={sections[1]:sections[2],sections[3]:sections[4]}
  assert set(part)=={"A","B"},(rid,seat,list(part))
  for letter,wanted in zip(("A","B"),(a,b)):
   txt=part[letter]
   # Criterion rows: score in second Markdown column, either **4** or **4/5**.
   vals=[int(m.group(1)) for line in txt.splitlines() if (m:=re.match(r"^\|[^|]+\|\s*\*\*([1-5])(?:/5)?\*\*",line))]
   assert len(vals)==(4 if seat=="critic-market" else 5),(rid,seat,letter,vals)
   actual=round1(Decimal(sum(vals))/Decimal(len(vals)))
   assert actual==wanted,(rid,seat,letter,actual,wanted)
   assert re.search(r"(?i)top_fix",txt) and re.search(r"(?i)gate_flags",txt) and re.search(r"(?i)confidence",txt)
   assert re.search(r"(?i)(unknown|unverified|missing|null)",txt)
  scores[seat]={"A":float(a),"B":float(b),"worker":dispatch["specialists"][seat]["worker"]}
 roomout={"seat_scores":scores,"candidates":{}}
 for letter in ("A","B"):
  weighted=sum(weights[s]*Decimal(str(scores[s][letter])) for s in weights)
  minseat=min(Decimal(str(scores[s][letter])) for s in weights)
  eligibility="SEAT_MIN_PASS" if minseat>=Decimal("3.0") else "SEAT_MIN_FAIL"
  # Whole delivered budget and native geometry are UNKNOWN from all four independent seats.
  roomout["candidates"][letter]={
   "weighted_arithmetic":float(weighted),
   "seat_minimum":float(minseat),
   "individual_seat_threshold":eligibility,
   "documented_wet_wall_and_niche":"PASS",
   "documented_exact_level_wet_dcof":"PASS_PUBLISHED_GE_0.42",
   "tiled_pan":"N/A_SELECTED_DURAVIT_TUB",
   "budget_125_percent_full_delivered":"UNKNOWN",
   "native_revit_geometry_focal_cuts":"UNKNOWN",
   "current_us_distribution":"PASS_ACTIVE_PRODUCT_PAGE",
   "chicago_exact_lot_and_eta":"UNKNOWN",
   "all_applicable_hard_gates_pass":False,
   "champion_elected":False,
   "reason":"Full delivered-material budget and source-native tile geometry remain unknown; minimum-seat rule also fails where indicated."
  }
 results[rid]=roomout

out={
 "round":24,"phase":"FOUR_CRITICS_COLLECTED_WEIGHTED_CALCULATED_NO_ACCEPTED_CHAMPION",
 "source_receipt_sha256":hashlib.sha256(ORIG.read_bytes()).hexdigest(),
 "clearance_sha256":hashlib.sha256(CLEAR.read_bytes()).hexdigest(),
 "dispatch_sha256":hashlib.sha256(DISPATCH.read_bytes()).hexdigest(),
 "critic_authentic_sources_sha256_bytes":collection,
 "weights":{k:float(v) for k,v in weights.items()},
 "rooms":results,"owner_missing_seat_exception_used":False,"champion_changes":False,
 "original_13room_objective":"OPEN",
 "underlying_accepted_prior_champions_unchanged":True,
 "independent_scoring_reviewer":"PENDING",
 "owner_approval":False,"procurement_release":False
}
RESULT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf8",newline="\n")
for room,info in results.items():
 print(room,*[(letter,info["candidates"][letter]["weighted_arithmetic"],info["candidates"][letter]["individual_seat_threshold"]) for letter in ("A","B")], "HARD_GATES_NOT_ALL_PASS")
print("R024 AUTHENTIC CRITICS",len(collection),"/12; all source SHA/byte verified, no champion changed")
