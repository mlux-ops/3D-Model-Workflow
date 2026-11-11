"""Read-only verify frozen R015 neutral pre-dispatch and additive R17 signed 13-room package."""
from pathlib import Path
from decimal import Decimal
import csv,json,hashlib,re
R=Path(__file__).resolve().parents[1];S=R/"state"
def sha(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
def j(p):
 return json.loads(p.read_text(encoding="utf-8"))
src=j(S/"ROUND015_SUBMISSION.json")
assert src["round"]==15 and src["critic_dispatch"]=="NOT_DISPATCHED"
assert src["all_critic_scores"] is None and src["weighted_scoring"] is None
assert src["rooms"]==["TX-BATH2","TX-BATH4"]
assert not (S/"ROUND015_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
research=R/src["shared_neutral_maker_research"]
assert sha(research)["sha256"]==src["shared_neutral_maker_research_sha256"]
forbidden=re.compile(r"(?i)(revised|challenger|historic|incumbent|prior\s+score|weighted\s+score|candidate\s+role)")
# Source-era quotations are common source provenance; but never leak candidate role.
assert not re.search(r"(?i)(challenger|incumbent|revised\s+candidate|source\s+candidate)",research.read_text(encoding="utf-8"))
candidate_links=0
for room,letters in src["candidate_files"].items():
 assert len(letters)==2
 key=j(R/src["private_keys_prime_and_reviewer_only"][room])
 assert key["confidential_prime_and_reviewer_only"]
 assert set(key["neutral_candidate_roles"])==set(letters)
 for letter,x in letters.items():
  p=R/x["file"]
  assert sha(p)=={"sha256":x["sha256"],"bytes":x["bytes"]},(room,letter)
  t=p.read_text(encoding="utf-8")
  lines=t.splitlines()
  assert lines[0]=="# "+room+" — Candidate "+letter+" — complete tile design option"
  assert lines[1]==""
  assert lines[2]=="This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified."
  assert len(lines)>55
  assert not re.search(r"(?i)(_key\.json|history\.md|champion\.md|ROUND012_SCORING|state/ROOMS\.json|state/LEDGER\.md)",t)
  assert "TUB" in t and "PAN" in t and "DCOF" in t
  assert "NO tiled shower PAN" in t or "PAN: **N/A" in t
  assert "999.92" in t if room=="TX-BATH2" else "1320.82" in t
  for link in re.findall(r"\]\(([^)]+)\)",t):
   if link.startswith(("https:","http:","#")):continue
   assert (p.parent/link.split("#")[0]).exists(),(room,letter,link)
   candidate_links+=1
R17=R/"deliverables/integrated-r17";man=j(R17/"MANIFEST.json")
assert man["room_count"]==13 and man["source_material_rows"]==27
assert man["source_trade_actions"]==65 and man["source_wall_elevations"]==25
assert man["original_historic_material_usd_four_unit"]=="23572.44"
assert man["source_waste_15pct_included_once"]
assert not man["owner_approval"] and not man["procurement_release"]
assert man["R014_weighted_scoring"] is None
for fn,sig in man["outputs"].items():
 assert sha(R17/fn)==sig,fn
def rows(fn):
 with (R17/fn).open(encoding="utf-8",newline="") as h:
  return list(csv.DictReader(h))
owner=rows("R17_13_OWNER_GC_RELEASE_GATES.csv")
materials=rows("R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv")
actions=rows("R17_65_TRADE_CLOSURE_EVIDENCE_REQUESTS.csv")
walls=rows("R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv")
lab=rows("R17_13_ROOM_WET_LAB_AND_PROGRAM_MATRIX.csv")
assert (len(owner),len(materials),len(actions),len(walls),len(lab))==(13,27,65,25,13)
assert sum(Decimal(x["source_material_usd_per_copy"])*2 for x in owner)==Decimal("23572.44")
assert sum(Decimal(x["historic_usd_two_copies"] or "0") for x in materials)==Decimal("23572.44")
assert len([x for x in materials if x["historic_niche_excluded_no_scope"]=="TRUE"])==2
assert all(x["owner_approved"]=="FALSE" and x["GC_release"]=="FALSE" and x["procurement_release"]=="FALSE" for x in owner)
assert all(x["owner_signed"]=="FALSE" and x["GC_signed"]=="FALSE" and x["purchase_release"]=="FALSE" for x in materials)
assert all(x["owner_signed"]=="FALSE" and x["GC_acceptance"]=="FALSE" and x["purchase_release"]=="FALSE" for x in actions)
assert all(x["owner_approved"]=="FALSE" and x["architect_gc_approved"]=="FALSE" for x in walls)
assert all(x["owner_approval"]=="FALSE" and x["GC_release"]=="FALSE" for x in lab)
assert all(x["required_PAN_lab_gate"]=="N/A_TUB" for x in lab if x["room"] in ("PH-BATH2","TX-BATH2","TX-BATH4"))
assert all(x["required_PAN_lab_gate"]=="N/A" for x in lab if "POWDER" in x["room"])
assert all(x["required_PAN_lab_gate"]=="CONDITIONAL_IF_OWNER_WALKIN_RAW_EXACT_NUMERIC" for x in lab if x["room"] in ("PH-BATH3","TX-BATH3"))
assert all(x["required_PAN_lab_gate"]=="REQUIRED_SEPARATE_LINEAR_RAW_EXACT_NUMERIC" for x in lab if x["room"] in ("PH-PRIMARY","TX-PRIMARY"))
assert all(x["actual_raw_numeric_LEVEL_wet_DCOF"]=="" and x["actual_raw_numeric_PAN_wet_DCOF"]=="" for x in lab)
assert sha(R/"deliverables/integrated-r16/MANIFEST.json")["sha256"]==man["source_R16_manifest_sha256"]
assert sha(R/"deliverables/integrated-r15/MANIFEST.json")["sha256"]==man["source_R15_manifest_sha256"]
assert sha(S/"ROUND014_SUBMISSION.json")["sha256"]==man["source_R014_submission_sha256"]
assert sha(S/"ROUND014_CRITIC_DISPATCH.json")["sha256"]==man["source_R014_dispatch_sha256"]
assert not (S/"ROUND014_SCORING.json").exists()
print("PASS R015 4 current neutral SHA frozen candidates 2 confidential keys, "+str(candidate_links)+" valid local links; source submission unscored no dispatch")
print("PASS R17 7 SHA outputs 13 owner gates, 27 historical source lines, 65 trade actions, 25 W elevations, 13 exact wet/PAN applicability rows; no false raw numeric lab, owner or GC release")
print("R015_SHA",sha(S/"ROUND015_SUBMISSION.json")["sha256"],"R17_MANIFEST_SHA",sha(R17/"MANIFEST.json")["sha256"])
