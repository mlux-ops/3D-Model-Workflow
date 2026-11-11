"""Reviewer39 PRECISE FIX. Correct exactly four missed R027 neutral citations.
Keep FIX2 signed historical; do not rewrite three private keys or predecessors.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
FIX2="state/ROUND027_PREDISPATCH_FIX2_ROOM_ONLY_RESEARCH_REFREEZE.json"
FIX3="state/ROUND027_PREDISPATCH_FIX3_FOUR_ROOM_LINKS_REFROZEN.json"
OLD="research/products/R027_TUB_THREE_ROOM_SOURCED_ALTERNATIVES.md"
def fp(path):
 data=(ROOT/path).read_bytes()
 return {"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)}
def main():
 if (ROOT/FIX3).exists():raise FileExistsError("FIX3 already signed")
 x=json.loads((ROOT/FIX2).read_text(encoding="utf-8"))
 changed={}
 for room in ("PH-BATH2","TX-BATH2"):
  safe="research/products/R027_"+room.replace("-","_")+"_BLIND_PRODUCT_EVIDENCE.md"
  if fp(safe)!=x["three_critic_safe_room_specific_research"][safe]:
   raise RuntimeError("Room-safe research SHA changed "+safe)
  for letter in ("A","B"):
   rel=f"rooms/{room}/board/round-027/candidates/{letter}.md"
   before=fp(rel)
   if before!=x["corrected_neutral_candidates_before_after"][rel]["new"]:
    raise RuntimeError("FIX2 signed candidate mutated "+rel)
   content=(ROOT/rel).read_text(encoding="utf-8")
   if content.count(OLD)!=1:raise RuntimeError("One old shared source reference expected "+rel)
   new=content.replace(OLD,safe)
   with (ROOT/rel).open("w",encoding="utf-8",newline="\n") as f:f.write(new)
   changed[rel]={"before":before,"after":fp(rel),"target_safe_research":safe}
 for room in ("TX-BATH4",):
  safe="research/products/R027_"+room.replace("-","_")+"_BLIND_PRODUCT_EVIDENCE.md"
  for letter in ("A","B"):
   rel=f"rooms/{room}/board/round-027/candidates/{letter}.md"
   if fp(rel)!=x["corrected_neutral_candidates_before_after"][rel]["new"] or safe not in (ROOT/rel).read_text(encoding="utf-8"):
    raise RuntimeError("TX4 already corrected source changed unexpectedly")
 for rel,sig in x["prime_only_private_keys_unchanged"].items():
  if fp(rel)!=sig:raise RuntimeError("Prime key mutation "+rel)
 for rel,sig in x["five_original_signed_parents_unchanged"].items():
  if fp(rel)!=sig:raise RuntimeError("Predecessor mutation "+rel)
 # All six actual final source links to the exclusively same-room research.
 full={}
 for room in ("PH-BATH2","TX-BATH2","TX-BATH4"):
  safe="research/products/R027_"+room.replace("-","_")+"_BLIND_PRODUCT_EVIDENCE.md"
  for letter in ("A","B"):
   rel=f"rooms/{room}/board/round-027/candidates/{letter}.md"
   data=(ROOT/rel).read_text(encoding="utf-8")
   if safe not in data or OLD in data or "R024" in data or "_key.json" in data:
    raise RuntimeError("R027 candidate still contaminated "+rel)
   full[rel]=fp(rel)
 report={
  "round":27,"phase":"CONTROLLED_FIX3_ALL_SIX_R027_BLIND_LINKS_SOURCE_REFROZEN_FRESH_REVIEWER_PENDING",
  "original_frozen_and_FIX2_predecessor_preserved":{"file":FIX2,**fp(FIX2)},
  "reviewer39":"PRECISE FIX four missed own-room evidence links after FIX2",
  "four_targeted_before_after_sha_bytes":changed,
  "full_final_six_neutral_candidates":full,
  "same_room_only_product_research_files":x["three_critic_safe_room_specific_research"],
  "prime_only_keys_unchanged":x["prime_only_private_keys_unchanged"],
  "signed_ancestor_receipts_unchanged":x["five_original_signed_parents_unchanged"],
  "new_pre_dispatch_independent_reviewer":None,
  "critic_dispatch":None,"weighted_scores":None,"champions_changed":False,
  "owner_approval":False,"procurement_release":False,"global_DONE":False}
 with (ROOT/FIX3).open("x",encoding="utf-8",newline="\n") as f:
  f.write(json.dumps(report,indent=2)+"\n")
 print("FIX3 four bad room links corrected; six same-room-only candidates SHA PASS; keys 3 and parents 5 unchanged")
 print("RECEIPT",fp(FIX3))
if __name__=="__main__":main()
