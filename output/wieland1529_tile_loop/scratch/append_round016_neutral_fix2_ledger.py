"""One-time second same-round Reviewer source correction and controlled interrupted-script audit."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];S=R/"state";L=S/"LEDGER.md"
H="## Round016 second independent precise blind-role wording FIX2 and controlled partial-write recovery — 2026-11-06"
assert H not in L.read_text(encoding="utf-8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sub=S/"ROUND016_SUBMISSION.json"
rec=S/"ROUND016_REVIEWER_NEUTRAL_LANGUAGE_FIX2.json"
assert sha(sub)=="dcc6e38897a0f92f65c372c2bc9526b54ddb139e9bdfff1788522e3007599d6a"
assert sha(rec)=="ee9ae680c4abb05c5e0e2b0407a155aa7cdd02de8bbdc3357fbd9a3a7494e38a"
r=json.loads(rec.read_text(encoding="utf-8"))
d=json.loads(sub.read_text(encoding="utf-8"))
assert r["source_before"]["sha256"]=="e08ea2e57fa161a55756a00b3953c1249329f8e4fad1082daf8edf725968997a"
assert len(r["changed_candidates"])==3 and len(r["other_three_candidate_fingerprints_byte_identical"])==3
assert r["changed_candidates"][0]["interrupted_write_reconciled"] is True
assert r["source_after"]["sha256"]==sha(sub)
assert d["critic_dispatch"]=="NOT_DISPATCHED" and d["R016_weighted_scoring"] is None
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists()
txt="\n"+H+"\n\n"
txt+="- Actual independent non-Pro Reviewer worker-15 SAME-R016 FIX2 isolated three residual role leaks, without any change to manufacturer-specific corrected AXOR/hansgrohe trim conflict: TX Powder B 'alternative to Haze' compared options, TX Powder2 A singled out its opposing Indigo scheme as the source benchmark and visual comparison, PH Powder C called itself 'Same manufacturer' and explicitly contrasted its composition against the full original Earth Lines quote. Rewrote precisely these candidate-specific sentences as standalone anonymous physical designs; retained honest historic per-copy material source rates and preserved dry wall versus wood floor, selected Brizo WALL faucet and selected Tecturis DECK.\n"
txt+="- Controlled one-time script failure and solution: first correction attempt fixed TX Powder B's role wording in its candidate text but stopped before touching source manifest when a second exact phrase differed (TX Powder2 A had a repeated 'not ... quote' suffix). No critic saw the unmanifested intermediate. Inspected actual bytes and resumed using PRE-FIX2 source submission fingerprints as the audit baseline, idempotently recognized the already-correct TX Powder B replacement, then surgically corrected TX Powder2 A and PH Powder C. Script also fixed a scratch-only Windows Path subscript typo before any original source mutation. Completed all three immutable old/new candidate SHA+byte receipts and signed the source atomically after cross-check; original other three source packets, common maker research and all private maps SHA-identical. No partial source price, owner approval, weighted score or procurement release was created.\n"
txt+="- R016 signed source SHA old "+r["source_before"]["sha256"]+" to new "+sha(sub)+"; exact before/after including interrupted controlled edit receipt SHA "+sha(rec)+". scratch/verify_round016_blind_powder_source_readonly.py PASSED six candidate files, 28 local/external links, exact three owner-selected faucet programs and separate AXOR/hansgrohe source conflict, original dry-room material $2,159.30 two-copy subset with first 15% waste included once. No current 1529 native verification or current Chicago installed bid. R014 worker9 DESIGN original failure and R015 four-seat hold persist; R016 critics/weights NULL.\n"
txt+="- Resubmitted exact SAME-R016 corrected source to standing worker-15. Actual follow-up Reviewer FIX/CONTINUE not yet received at this ledger checkpoint. Full 13-room objective OPEN; never dispatch substitute critics or issue POs without authorization.\n"
with L.open("a",encoding="utf-8",newline="") as f:f.write(txt)
print("PASS R016 surgical neutral-language FIX2 signed ledger, scratch interruption documented with resolution, original source and release fields unchanged")
