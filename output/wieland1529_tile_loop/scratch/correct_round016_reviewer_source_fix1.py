"""Same-R016 precise independent non-Pro Reviewer FIX1, BEFORE any critic dispatch.

Source-listed AXOR 48140991 and hansgrohe 32526141 are two different TRIMS,
not a compatible faucet + rough. Original plumbing.json is intentionally untouched.
Remove historical role cues and inapplicable deck-faucet wall escutcheon text.
"""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1];S=R/"state"
SUB=S/"ROUND016_SUBMISSION.json"
REC=S/"ROUND016_REVIEWER_FACET_AND_BLIND_NEUTRALITY_FIX1.json"
assert not REC.exists()
assert not (S/"ROUND016_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND016_SCORING.json").exists()
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
old=fp(SUB)
assert old["sha256"]=="1265b5fce959a862d1e7c067c44be434eba174a56ab57b595d1365309221aa2e"
sub=json.loads(SUB.read_text(encoding="utf-8"))
assert sub["critic_dispatch"]=="NOT_DISPATCHED"
assert sub["all_critic_scores"] is None and sub["R016_weighted_scoring"] is None
assert len(sub["candidate_source"])==3
changes=[]
def rewrite(path,replacements,why):
 before=fp(path)
 txt=path.read_text(encoding="utf-8")
 count=0
 for a,b in replacements:
  n=txt.count(a)
  assert n>=1,(path,a[:80],why)
  txt=txt.replace(a,b)
  count+=n
 path.write_text(txt,encoding="utf-8")
 changes.append({"file":str(path.relative_to(R)).replace(chr(92),"/"),"reason":why,"replacements":count,"before":before,"after":fp(path)})

official=(
 "[AXOR 48140991 official Polished Gold Optic One 220 cross-handle WALL faucet TRIM]"
 "(https://www.axor-design.com/us/articledetail-axor-one-wall-mounted-widespread-faucet-220-cross-handles-1-2-gpm-48140991)"
 " and [hansgrohe 32526141 official Brushed Bronze Metropol single-lever WALL faucet TRIM]"
 "(https://www.hansgrohe-usa.com/articledetail-metropol-wall-mounted-single-handle-faucet-trim-with-lever-handle-1-2-gpm-without-pop-up-drain-32526141)"
)
plumbing=(
 "Two mutually conflicting source-listed WALL faucet trim entries: "+official+
 ". **32526141 is NOT a rough-in. These two distinct brand/family/handle/finish trims cannot be assumed compatible or simultaneously selected.**"
 " Owner/architect/plumber must reconcile which actual trim, finish, and matching factory-verified rough is authorized; no accepted set or rough is inferred."
 " Preserve both original quoted spreadsheet/plumbing rows unchanged as source evidence, not as an approved assembly."
 " Check source [plumbing](../../../plumbing.json) and [provisional geometry](../../../geometry.json)."
)

for letter in ("B","C"):
 p=R/"rooms/TX-POWDER/board/round-016/candidates"/(letter+".md")
 pairs=[
  ("**Plumbing:** Hansgrohe wall faucet 48140991 and wall rough 32526141, exact observed finish not verified. Preserve fixture type, selected metal and physical rough. No custom faucet/basin/owner changes are authorized. Check source [plumbing](../../../plumbing.json) and [provisional geometry](../../../geometry.json).",
   "**Plumbing:** "+plumbing),
  ("Sample 1:1 FULL tile, relief depth/flat landing, owner-selected faucet finish, actual substrate and grout/edge",
   "Sample 1:1 FULL tile, wall finishing relief/flat plane, separate AXOR Polished Gold Optic and hansgrohe Brushed Bronze source-listed trim references as UNRESOLVED alternatives, actual substrate and grout/edge"),
  ("**Top coordination fix:** Verify true owner-selected faucet/rough face, mirror position",
   "**Top coordination fix:** Resolve the AXOR versus hansgrohe faucet TRIM conflict, confirm exact selected compatible factory ROUGH and real mirror/escutcheon coordinates"),
  ("no selected plumbing substitution.",
   "no trim/rough compatibility claimed; source conflict is a hard shop/owner HOLD, no replacement authorized."),
 ]
 if letter=="B":
  pairs.extend([
   ("vertically align tile modules with the selected Hansgrohe wall faucet 48140991 and verified wall-mounted rough 32526141.",
    "prepare a conditional balanced tile layout around a provisional wall faucet zone ONLY after owner/architect/plumber resolve the AXOR One versus hansgrohe Metropol competing trim records and manufacturer-matched rough."),
   ("maintain planar grout/edge landing for wall rough",
    "maintain a future confirmed planar grout/edge landing for whatever factory-approved wall-faucet rough is owner-selected")
  ])
 else:
  pairs.append((
   "center the Hansgrohe 48140991 and separate 32526141 rough on an actually verified flat planar landing.",
   "center 1.6x5 dry-wall modules around the future selected faucet escutcheon plane ONLY after the conflicting AXOR versus hansgrohe trim entries and actual manufacturer-matched rough are reconciled; do NOT treat either trim as rough."
  ))
 rewrite(p,pairs,"original product family and rough-type manufacturer conflict; proper room-only drywall faucet shop HOLD")

for letter in ("A","B"):
 p=R/"rooms/TX-POWDER2/board/round-016/candidates"/(letter+".md")
 pairs=[
  ("Preserve fixture type, selected metal and physical rough. No custom faucet/basin/owner changes are authorized.",
   "Preserve the selected DECK faucet and metal, but its countertop drilling/connection geometry remains held until the owner selects the basin; no wall faucet rough or wall escutcheon is included."),
  ("mirror/rough centering, escutcheon flat landing",
   "mirror centering, vanity countertop and owner-unselected basin / DECK faucet clearances (NO wall escutcheon)"),
  ("Sample 1:1 FULL tile, relief depth/flat landing, owner-selected faucet finish",
   "Sample 1:1 FULL dry tile, edge/mirror landing and DECK faucet color reference at the countertop, owner basin still UNSELECTED"),
  ("**Top coordination fix:** Verify true owner-selected faucet/rough face, mirror position, relief versus planar seal",
   "**Top coordination fix:** Verify selected DECK faucet 73072341 countertop clearances, mirror position, relief/mirror backing and owner-UNSELECTED sink drill-hole hold"),
 ]
 if letter=="A":
  pairs.extend([
   ("Replace all of the provisional 3.806-ft dry vanity feature wall with nominal 2x10 Earth Lines glossy relief",
    "Specify the provisional 3.806-ft dry vanity feature wall entirely in nominal 2x10 Earth Lines glossy relief"),
   ("ALREADY SELECTED Hansgrohe 73072341 faucet",
    "specified Hansgrohe 73072341 DECK faucet"),
   ("maintain planar grout/edge landing for wall rough",
    "maintain actual calibrated grout and mirror/edge landings; no wall-faucet penetration"),
   ("40.5 SF gross and $332.10/copy are original Indigo reference",
    "40.5 SF gross and $332.10/copy are the dated same-room Indigo source benchmark, not the Earth Lines material quote")
  ])
 else:
  pairs.extend([
   ("Continue 6x6 Indigo Edge glossy relief on the entire provisional 3.806-ft wide dry wall",
    "Specify 6x6 Indigo Edge glossy relief across the provisional 3.806-ft wide dry wall"),
   ("without the previously costly unpriced smooth tile insert",
    "without a second unpriced smooth-tile material or non-source inset"),
   ("Retain more playful Indigo square relief",
    "Emphasize playful Indigo square relief"),
   ("Original 40.5 SF/copy at $8.20/SF",
    "Dated source 40.5 SF/copy at $8.20/SF")
  ])
 rewrite(p,pairs,"remove implicit historical source-role cues and irrelevant wall-mounted faucet/escutcheon from DECK sink room")

research=R/sub["shared_maker_research"]
rewrite(research,[
 ("TX Powder Hansgrohe WALL faucet 48140991 with 32526141 rough; exact selected finish and alignment survey still hold.",
  "TX Powder has **UNRESOLVED manufacturer/fixture contradiction**, not a selected compatible kit: "+official+
  ". AXOR One 48140991 is Polished Gold Optic WALL cross-handle faucet trim; hansgrohe 32526141 is Brushed Bronze Metropol single-lever WALL faucet trim, **NOT a rough-in**. Original plumbing.json labels 32526141 as rough and is retained read-only as an unresolved source conflict. Obtain owner/architect/plumber choice, exact trim family and manufacturer-specified corresponding rough, actual dimensions before any wall elevation/shop/release."),
 ("Verify porcelain/vitreous-ceramic relief plane versus flat mounting support, tile transition, soft joints and mirror/backing in a 1:1 mockup.",
  "For the two wall-faucet powder rooms verify relief/flat sealing landing and actual selected compatible rough; for TX Powder2 only, verify DECK faucet countertop, basin and mirror backing without any wall escutcheon. No manufacturer rough replacement or owner finish election is made by this document.")
],"maker primary official source product/finish/rough conflict")

for room,letters in sub["candidate_source"].items():
 for letter,meta in letters.items():
  p=R/meta["path"]
  meta.update(fp(p))
  assert p.read_text(encoding="utf-8").startswith(f"# {room} — Candidate {letter} — complete tile design option")
  assert not re.search(r"(?i)Replace all|Continue 6x6|previously costly|Retain more playful",p.read_text(encoding="utf-8"))
sub["shared_maker_research_fingerprint"]=fp(research)
sub["revision"]="SAME-R016 independent worker-15 precise FIX1 before ANY critic: original source 48140991 AXOR Gold Optic and 32526141 hansgrohe Brushed Bronze are incompatible separate faucet TRIMS, not trim+rough. TX Powder2 role cues and deck inapplicable wall detail removed. Signed old/new audit receipt; all owner choices held."
SUB.write_text(json.dumps(sub,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert sub["critic_dispatch"]=="NOT_DISPATCHED" and sub["R016_weighted_scoring"] is None
assert not (S/"ROUND014_SCORING.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
assert fp(S/"ROUND014_SUBMISSION.json")["sha256"]==sub["R014_source_sha256"]
assert fp(S/"ROUND015_SUBMISSION.json")["sha256"]==sub["R015_source_sha256"]
assert fp(R/"deliverables/integrated-r21-install-witness-sequence/MANIFEST.json")["sha256"]==sub["last_signed_R21_manifest_sha256"]
REC.write_text(json.dumps({"round":16,"as_of":"2026-11-06","reviewer":"worker-15",
  "reviewer_verdict":"PRECISE FIX — AXOR versus hansgrohe trim family and wrong rough identity, and TX Powder2 blind role/deck word leak",
  "source_before":old,"source_after":fp(SUB),"file_changes":changes,
  "source_original_plumbing_rows_modified":False,"private_maps_modified":False,
  "critic_dispatch":"NOT_DISPATCHED","R014_scoring":None,"R015_scoring":None,
  "R016_scoring":None,"owner_approval":False,"GC_release":False,
  "procurement_release":False},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("PASS same-R016 exact AXOR/hansgrohe selected-rough conflict and blind role FIX, 4 candidate docs + common maker research SHA refrozen, 3 private maps intact, no critic dispatch/scoring/release")
print("R016_SHA",fp(SUB)["sha256"])
print("FIX1_RECEIPT_SHA",fp(REC)["sha256"])
