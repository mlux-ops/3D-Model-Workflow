"""Independent read-only pre-dispatch R016 neutral candidate and quoted-source check."""
from pathlib import Path
import hashlib,json,re
from decimal import Decimal

R=Path(__file__).resolve().parents[1];S=R/"state"
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
sub=S/"ROUND016_SUBMISSION.json"
d=json.loads(sub.read_text(encoding="utf-8"))
assert d["round"]==16 and d["critic_dispatch"]=="NOT_DISPATCHED"
assert d["all_critic_scores"] is None and d["R016_weighted_scoring"] is None
assert d["predispatch_reviewer_verdict"] is None
assert not (S/"ROUND016_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND016_SCORING.json").exists()
assert not (S/"ROUND014_SCORING.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
assert d["focus_rooms"]==["PH-POWDER","TX-POWDER","TX-POWDER2"]
assert d["R014_source_sha256"]==fp(S/"ROUND014_SUBMISSION.json")["sha256"]
assert d["R015_source_sha256"]==fp(S/"ROUND015_SUBMISSION.json")["sha256"]
assert d["last_signed_R21_manifest_sha256"]==fp(R/"deliverables/integrated-r21-install-witness-sequence/MANIFEST.json")["sha256"]
research=R/d["shared_maker_research"]
assert fp(research)==d["shared_maker_research_fingerprint"]
roomdata={x["id"]:x for x in json.loads((S/"ROOMS.json").read_text(encoding="utf-8"))["rooms"]}
total=Decimal("0")
all_links=0
for room,letters in d["candidate_source"].items():
 assert len(letters)==2
 assert roomdata[room]["status"]=="active"
 k=json.loads((R/d["confidential_mappings"][room]).read_text(encoding="utf-8"))
 assert k["confidential_prime_and_independent_reviewer_only"] is True
 assert set(letters)==set(k["neutral_candidate_roles"])
 quote=d["room_source_per_copy_gross_and_usd"][room]
 original=roomdata[room]["carried_tile_rows"]
 assert len(original)==1
 assert Decimal(str(original[0]["qty_sf_per_unit"]))==Decimal(quote["gross_sf_with_original_15pct_once"])
 assert Decimal(str(original[0]["extended_quote_cost_usd_per_unit"]))==Decimal(quote["material_usd"])
 total+=Decimal(quote["material_usd"])*2
 for letter,meta in letters.items():
  p=R/meta["path"]
  assert fp(p)=={"sha256":meta["sha256"],"bytes":meta["bytes"]}
  txt=p.read_text(encoding="utf-8")
  lines=txt.splitlines()
  assert lines[0]==f"# {room} — Candidate {letter} — complete tile design option"
  assert lines[1]==""
  assert lines[2]=="This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified."
  assert len(lines)>=30
  assert "wood" in txt.lower() and "no" in txt.lower() and "no owner approval" in txt.lower()
  assert not re.search(r"(?i)_key\.json|state/ROOMS\.json|state/LEDGER\.md|champion\.md|history\.md|round-003|critic-market|critic-cost|weighted champion|incumbent|challenger",txt)
  assert "full" in txt.lower()
  links=re.findall(r"\]\(([^)]+)\)",txt)
  assert len(links)>=4,(room,letter,links)
  for link in links:
   if link.startswith(("https://","http://")):
    continue
   assert (p.parent/link).exists(),(room,letter,link)
  all_links+=len(links)
  if room=="PH-POWDER":
   assert "T65722LF-GL" in txt and "R65700" in txt
  if room=="TX-POWDER":
   assert "48140991" in txt and "32526141" in txt
   assert "AXOR" in txt and "Metropol" in txt and "NOT a rough-in" in txt
   assert "cannot be assumed compatible" in txt and "owner/architect/plumber" in txt.lower()
   assert "Hansgrohe wall faucet 48140991 and wall rough 32526141" not in txt
  if room=="TX-POWDER2":
   assert "73072341" in txt and "DECK" in txt and "UNSELECTED" in txt
   assert "no wall faucet rough" in txt.lower() or "NO wall escutcheon" in txt
   assert not re.search(r"(?i)replace all|continue 6x6|previously costly unpriced|retain more playful",txt)
assert total==Decimal("2159.30")
assert d["owner_approved"] is False and d["correct_1529_native_model_verified"] is False
print("PASS R016 six SHA/byte frozen neutral source candidates across three active dry powders; original historic room-specific quoted material subset 2159.30/2 copies and 15% gross once; links",all_links)
print("R016_SHA",fp(sub)["sha256"])
