"""Same-R016 independent reviewer FIX2: three exact residual role cues only.
No change to technical fixture resolution, shared maker research, private mapping,
historic quote values or original R014/R015 signed rounds.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]; S=R/"state"
SUB=S/"ROUND016_SUBMISSION.json"
OUT=S/"ROUND016_REVIEWER_NEUTRAL_LANGUAGE_FIX2.json"
assert not OUT.exists()
assert not (S/"ROUND016_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND016_SCORING.json").exists()
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
prior=fp(SUB)
assert prior["sha256"]=="e08ea2e57fa161a55756a00b3953c1249329f8e4fad1082daf8edf725968997a"
d=json.loads(SUB.read_text(encoding="utf-8"))
shared=R/d["shared_maker_research"]
shared_sig=fp(shared)
key_before={room:fp(R/key) for room,key in d["confidential_mappings"].items()}
# Compare to the PRE-FIX2 signed submission, not live bytes: the initial
# attempt wrote TX-POWDER B before a later exact phrase mismatch stopped it.
files_before={ (room,letter):{"sha256":meta["sha256"],"bytes":meta["bytes"]} for room,cs in d["candidate_source"].items() for letter,meta in cs.items()}
fixes=[
 ("TX-POWDER","B",[
  ("This material's finish is a substantive alternative to matte 1.6x5 Haze, not a source-rate switch.",
   "This glossy 2x10 relief wall design requires an individually calibrated joint/edge, a real flat wall-escutcheon landing and a physical glare/cleanability mockup; no current local tile price or finished installer scope is inferred.")
 ]),
 ("TX-POWDER2","A",[
  ("40.5 SF gross and $332.10/copy are the dated same-room Indigo source benchmark, not the Earth Lines material quote, NOT the new Earth Lines quote or orderable quantity.",
   "40.5 SF gross and $332.10/copy remain the dated same-room material-only budget comparator; they are not a current supplier quotation for this specified Earth Lines material, a full-case yield or an installed price."),
  ("A linear, sculptural but reduced individual-joint composition compared to 6x6 Indigo relief; test warm Earth Lines against Brushed Black Chrome Tecturis and wood floor in physical light, not via unverified product photo.",
   "The glossy 2x10 linear-joint rhythm gives a sculptural dry vanity focal field; test Earth Lines against Brushed Black Chrome DECK-mounted Tecturis and wood flooring in real light, not an unverified room or product photo.")
 ]),
 ("PH-POWDER","C",[
  ("Same manufacturer 2x10 relief limited to balanced vertical feature fields flanking an explicitly DRY painted, perfectly flat central faucet/escutcheon landing aligned with the actual Brizo rough; central painted area geometry and edge trim require the verified 1529 wall projection and selected mirror width. No flat tile SKU is invented. This is a physically different joint/cut/finish composition; do not assume the full original 44.9-SF relief source quote also applies after displaced center area.",
   "Specify ELM Vera Forma Earth Lines 2x10 relief in balanced flanking vertical feature fields around a DRY painted planar center reserved for the owner-selected Brizo T65722LF-GL Luxe Gold WALL faucet and R65700 rough. The painted-center width, backer plane, edge trims, mirror and relief net area remain unmeasured; deduct the painted opening from actual future tile NET once and obtain a separate documented paint/edge installation price before any order. No flat tile SKU, owner-approved paint finish or additional wall is invented.")
 ])
]
change=[]
for room,letter,pairs in fixes:
 p=R/d["candidate_source"][room][letter]["path"]
 t=p.read_text(encoding="utf-8")
 old=files_before[(room,letter)]
 already_partially_written=fp(p)!=old
 for a,b in pairs:
  if t.count(a)==1:
   t=t.replace(a,b)
  else:
   # Accept only the SAME previously applied exact replacement, not drift.
   assert t.count(a)==0 and t.count(b)==1,(room,letter,a[:70])
 if p.read_text(encoding="utf-8")!=t:
  p.write_text(t,encoding="utf-8")
 d["candidate_source"][room][letter].update(fp(p))
 change.append({"room":room,"letter":letter,"path":str(p.relative_to(R)).replace(chr(92),"/"),"before":old,"after":fp(p),"exact_replacements":len(pairs),"interrupted_write_reconciled":already_partially_written})
assert len(change)==3
for room,cs in d["candidate_source"].items():
 for letter,meta in cs.items():
  p=R/meta["path"]
  assert fp(p)=={"sha256":meta["sha256"],"bytes":meta["bytes"]}
  if (room,letter) not in {(x[0],x[1]) for x in fixes}:
   assert fp(p)==files_before[(room,letter)]
assert fp(shared)==shared_sig
assert all(fp(R/key)==key_before[room] for room,key in d["confidential_mappings"].items())
assert d["critic_dispatch"]=="NOT_DISPATCHED" and d["R016_weighted_scoring"] is None
d["revision"]="SAME-R016 independent worker-15 FIX1 maker/rough and deck + FIX2 exact 3 neutral role/temporal phrase removals; six frozen packets resig without changing other three options, shared maker study or private keys; no score or critic dispatch"
SUB.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert fp(S/"ROUND014_SUBMISSION.json")["sha256"]==d["R014_source_sha256"]
assert fp(S/"ROUND015_SUBMISSION.json")["sha256"]==d["R015_source_sha256"]
assert fp(R/"deliverables/integrated-r21-install-witness-sequence/MANIFEST.json")["sha256"]==d["last_signed_R21_manifest_sha256"]
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists()
OUT.write_text(json.dumps({"round":16,"as_of":"2026-11-06","reviewer":"worker-15",
 "reviewer_actual_verdict":"PRECISE FIX2 — three residual neutral source-role comparison phrases",
 "source_before":prior,"source_after":fp(SUB),"changed_candidates":change,
 "other_three_candidate_fingerprints_byte_identical":{room+"/"+letter:s for (room,letter),s in files_before.items() if (room,letter) not in {(x[0],x[1]) for x in fixes}},
 "shared_maker_research_unchanged":shared_sig,"all_three_private_mappings_unchanged":key_before,
 "original_plumbing_Smartsheet_Revit_modified":False,
 "critic_dispatch":"NOT_DISPATCHED","R014_scoring":None,"R015_scoring":None,
 "R016_scoring":None,"owner_approval":False,"GC_release":False,"procurement_release":False},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("PASS SAME-R016 reviewer FIX2 exact three candidate role-neutral phrasings, all other three frozen options, shared research, private keys and past source SHA unchanged; no critic/scoring/release")
print("R016_SHA",fp(SUB)["sha256"])
print("FIX2_SHA",fp(OUT)["sha256"])
