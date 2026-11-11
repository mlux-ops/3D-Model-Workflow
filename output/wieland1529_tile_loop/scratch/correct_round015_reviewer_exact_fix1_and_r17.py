"""SAME-R015 independent reviewer FIX1 correction before critic dispatch.

Neutralizes leaked candidate roles; corrects maker country and grout in both
R015 source and separately SHA-signed R17 field book. Keeps all other signed
R12-R16 and frozen R014 source/critic files intact.
"""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1]
S=R/"state"
source=S/"ROUND015_SUBMISSION.json"
research=R/"research/products/R15_TX_TUB_PAIR_EL30_KC04_INDIVIDUAL_MAKER_WET_APPLICATION_20261106.md"
r17=R/"deliverables/integrated-r17"
book=r17/"R17_13_ROOM_DESIGN_AND_RELEASE_FIELD_BOOK.md"
manifest=r17/"MANIFEST.json"
receipt=S/"ROUND015_PREDISPATCH_REVIEWER_FIX1_AND_R17_MAKER_FACTS.json"
assert not receipt.exists()
assert not (S/"ROUND015_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
assert not (S/"ROUND014_SCORING.json").exists()

def fp(path):
 b=path.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
def replace_exact(path,old,new,why,log):
 t=path.read_text(encoding="utf-8")
 hits=t.count(old)
 assert hits>0,(path.name,why,old)
 before=fp(path)
 path.write_text(t.replace(old,new),encoding="utf-8")
 log.append({"file":str(path.relative_to(R)).replace(chr(92),"/"),"reason":why,"occurrences":hits,"before":before,"after":fp(path)})

original_src=fp(source)
original_r17=fp(manifest)
assert original_src["sha256"]=="ff0339025e5302b101958ff08da8f2b538bc11c4b77d204b6fc7db031c75e835"
assert original_r17["sha256"]=="a34a381bcc9072836130e17141851c80b8215e15d464fd7b8406bdb0b8711f41"
old_sub=json.loads(source.read_text(encoding="utf-8"))
old_m=json.loads(manifest.read_text(encoding="utf-8"))
assert old_sub["critic_dispatch"]=="NOT_DISPATCHED" and old_sub["all_critic_scores"] is None
assert old_sub["weighted_scoring"] is None
assert not old_m["procurement_release"]
changes=[]

p=R/"rooms/TX-BATH2/board/round-015/candidates/C.md"
replace_exact(p,"Exact original Cortar Clay Soft LEVEL","Exact Cortar Clay Soft 12x24 LEVEL","remove historical role cue in Clay floor lab",changes)
p=R/"rooms/TX-BATH4/board/round-015/candidates/C.md"
replace_exact(p,"Original Cortar Bone Soft 12×24","Cortar Bone Soft 12×24","remove historical role cue in Bone floor lab",changes)
replace_exact(p,"visually darker original niche variant","visually darker Caviar niche variant","remove role cue in niche/appearance",changes)
replace_exact(p,"TUB PAN N/A..","TUB PAN N/A.","fix repeated punctuation",changes)
p=R/"rooms/TX-BATH2/board/round-015/candidates/A.md"
replace_exact(p,"White Elect EL30 12×24 Matte USA","White Elect EL30 12×24 Matte Mexico","maker exact EL30 official origin Mexico",changes)
p=R/"rooms/TX-BATH4/board/round-015/candidates/B.md"
replace_exact(p,"KC04 Target wet ≥0.42 / 1/8in joint","KC04 Target wet ≥0.42 / 3/16in joint","maker exact KC04 grout 3/16in",changes)

replace_exact(research,"]("
 + "https://www.elmsurfaces.com/product/cortar-clay) source bath LEVEL",
 "](https://www.elmsurfaces.com/product/cortar-clay) bath LEVEL material; provenance independently reviewed",
 "remove research role leakage for Clay",changes)
replace_exact(research,"]("
 + "https://www.elmsurfaces.com/product/cortar-bone) source bath LEVEL",
 "](https://www.elmsurfaces.com/product/cortar-bone) bath LEVEL material; provenance independently reviewed",
 "remove research role leakage for Bone",changes)
replace_exact(research,"[Exact White Elect](https://www.daltile.com/products/stone-look/prime/white-elect), USA 3/8in nominal","[Exact White Elect](https://www.daltile.com/products/stone-look/prime/white-elect), Mexico 3/8in nominal","maker White Elect EL30 precise origin; other KC04 remains USA",changes)
replace_exact(research,"Current maker joint 1/8in","Current maker joint 3/16in","maker Grey Koncrete KC04 exact grout page",changes)
replace_exact(research,"tube flange","tub flange","spelling: correct actual tub waterproofing",changes)

replace_exact(book,"white EL30 U.S. 12×24","white EL30 Mexico 12×24","R17 owner book exact White Elect country",changes)
replace_exact(book,"Maker 1/8-in grout recommendation","Maker 3/16-in grout recommendation","R17 owner book exact Grey Koncrete joint",changes)
replace_exact(book,"Six detailed CSV schedules below","Five detailed CSV schedules below","R17 correct five CSV count",changes)

# Re-sign frozen R015 neutral candidates and common maker source after exact
# independent source corrections. Private maps do not change and no critic gets
# their mapping. Submission is source-only and intentionally keeps scoring NULL.
updated=json.loads(source.read_text(encoding="utf-8"))
for rid,letters in updated["candidate_files"].items():
 for letter,entry in letters.items():
  b=fp(R/entry["file"])
  entry["sha256"],entry["bytes"]=b["sha256"],b["bytes"]
updated["shared_neutral_maker_research_sha256"]=fp(research)["sha256"]
updated["revision"]="SAME-R015 independent worker-14 exact FIX1 BEFORE critic dispatch: remove role cues; precise EL30 maker origin and KC04 grout; previous candidates/source immutable audit in separate fix receipt"
source.write_text(json.dumps(updated,indent=2,ensure_ascii=False)+chr(10),encoding="utf-8")

# Only R17 owner book changes, six other signed R17 outputs remain SHA-identical.
updated_m=json.loads(manifest.read_text(encoding="utf-8"))
other_before={name:fp(r17/name) for name in updated_m["outputs"] if name!="R17_13_ROOM_DESIGN_AND_RELEASE_FIELD_BOOK.md"}
updated_m["outputs"]["R17_13_ROOM_DESIGN_AND_RELEASE_FIELD_BOOK.md"]=fp(book)
manifest.write_text(json.dumps(updated_m,indent=2,ensure_ascii=False)+chr(10),encoding="utf-8")
assert all(fp(r17/name)==sig for name,sig in other_before.items())
assert all(fp(r17/name)==sig for name,sig in updated_m["outputs"].items())
assert fp(R/"deliverables/integrated-r16/MANIFEST.json")["sha256"]==updated_m["source_R16_manifest_sha256"]

for rid,letters in updated["candidate_files"].items():
 for letter,entry in letters.items():
  p=R/entry["file"]
  t=p.read_text(encoding="utf-8")
  assert not re.search(r"(?i)(original Cortar|historical candidate|revised candidate|incumbent|challenger|original niche variant)",t),(rid,letter)
  assert fp(p)=={"sha256":entry["sha256"],"bytes":entry["bytes"]}
assert not re.search(r"(?i)(source bath LEVEL|challenger|incumbent|revised candidate)",research.read_text(encoding="utf-8"))
assert "Current maker joint 3/16in" in research.read_text(encoding="utf-8")
assert "Mexico 3/8in nominal" in research.read_text(encoding="utf-8")
assert updated["critic_dispatch"]=="NOT_DISPATCHED" and updated["weighted_scoring"] is None
assert updated_m["R014_weighted_scoring"] is None and not updated_m["procurement_release"]

receipt.write_text(json.dumps({
 "round":15,"as_of":"2026-11-06","reviewer":"worker-14",
 "verdict":"FIX — R015 private role leak, maker origin and grout error before dispatch",
 "initial_submission":original_src,"corrected_submission":fp(source),
 "initial_r17_signed_manifest":original_r17,"corrected_r17_manifest":fp(manifest),
 "research_updated":fp(research),"file_changes":changes,
 "six_other_signed_r17_files_unchanged":other_before,
 "R014_R016_original_chain_preserved":True,
 "R015_critic_dispatch":False,"all_critic_scores":None,"weighted_scoring":None,
 "owner_approval":False,"procurement_release":False
},indent=2,ensure_ascii=False)+chr(10),encoding="utf-8")
print("PASS exact independent R015 FIX1 same-round role text, EL30 origin and KC04 grout fixed before critic dispatch; R17 book only re-signed, six other outputs SHA stable")
print("R015_SHA",fp(source)["sha256"])
print("R17_MANIFEST_SHA",fp(manifest)["sha256"])
print("FIX_RECEIPT_SHA",fp(receipt)["sha256"])
