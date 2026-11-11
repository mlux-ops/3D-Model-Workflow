"""One-time actual Reviewer-identified maker/rough incompatibility and blind-role source fix audit."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];S=R/"state";L=S/"LEDGER.md"
H="## Round016 same-round independent source FIX1 AXOR versus hansgrohe trim/rough identity and dry Powder2 blind-role corrections — 2026-11-06"
assert H not in L.read_text(encoding="utf-8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rec=S/"ROUND016_REVIEWER_FACET_AND_BLIND_NEUTRALITY_FIX1.json"
sub=S/"ROUND016_SUBMISSION.json"
r=json.loads(rec.read_text(encoding="utf-8"))
s=json.loads(sub.read_text(encoding="utf-8"))
assert sha(rec)=="324f39bf5eb48ad72b53a6ed2cd3992520a5317299b53f5bba32876c9eb221ac"
assert sha(sub)=="e08ea2e57fa161a55756a00b3953c1249329f8e4fad1082daf8edf725968997a"
assert r["source_before"]["sha256"]=="1265b5fce959a862d1e7c067c44be434eba174a56ab57b595d1365309221aa2e"
assert r["source_after"]["sha256"]==sha(sub)
assert len(r["file_changes"])==5
assert s["critic_dispatch"]=="NOT_DISPATCHED" and s["R016_weighted_scoring"] is None
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists() and not (S/"ROUND016_SCORING.json").exists()
txt="\n"+H+"\n\n"
txt+="- Actual standing original non-Pro successor Reviewer worker-15 returned **PRECISE FIX** on first independent R016 source pre-dispatch audit. Critical fixture correction: TX-POWDER Smartsheet/plumbing.json source lists AXOR One 48140991 (official AXOR WALL faucet 220 cross handles Polished Gold Optic trim), and hansgrohe Metropol 32526141 (official hansgrohe WALL single-lever Brushed Bronze trim) mistakenly presented together as Hansgrohe faucet plus rough. 32526141 is itself a trim, NOT a rough or verified AXOR-compatible body. Original plumbing.json/source rows preserved unchanged, new candidate B/C and common maker research now cite two separate official manufacturer pages, identify mutually exclusive unselected trim/finish assemblies and hold exact required matched rough, wall plane, owner/architect/plumber election and physical sample. NO replacement trim, fixture or rough selected, ordered or approved.\n"
txt+="- Exact second reviewer FIX: TX-POWDER2 candidate A/B statements 'Replace all', 'Continue', 'previously costly' and 'Retain' leaked historical origin; all role/temporal hints replaced with neutral option-specific composition. Removed inapplicable wall-mount escutcheon/rough/lavatory assumption for TX Powder2: selected Hansgrohe Tecturis E 73072341 Brushed Black Chrome remains DECK mounted, owner basin UNSELECTED, countertop drill positions unknown. Candidate option Earth Lines 2x10 vs Indigo 6x6 unchanged, old two-copy source material basis unchanged and original PH Brizo remains fixed.\n"
txt+="- Surgically re-signed only four affected TX Powder / TX Powder2 neutral candidate files, shared R016 maker research, and R016 source pointer. OLD R016 source SHA "+r["source_before"]["sha256"]+" => corrected "+sha(sub)+"; exact old/new per-file SHA/bytes receipt "+sha(rec)+". Two PH-POWDER candidate packets and all three confidential private mappings untouched. Read-only scratch/verify_round016_blind_powder_source_readonly.py PASS 6/6 source fingerprints, 28 links (new official AXOR/hansgrohe pages), exact required neutral headings, source three-room two-copy $2159.30 material subset and first original 15% gross ONCE; no venue quote, owner cap, 1529 model geometry or order. R014/15 and signed R17–R21 SHA pointers unchanged.\n"
txt+="- Five-section exact SAME-R016 reviewer FIX resubmitted to original worker-15; actual independent follow-up verdict pending at this ledger checkpoint. R014 original DESIGN worker-9 FAILED, 6/8 authenticated, R015 original 4-seat critic dispatch HOLD, R016 likewise source-only/NOT_DISPATCHED, all scoring NULL. Full 13-room owner/GC release FALSE, next action independent pre-dispatch clearance and original DESIGN governance/actual 1529 identity resolution.\n"
with L.open("a",encoding="utf-8",newline="") as f:f.write(txt)
print("PASS exact R016 manufacturer/rough and blind neutrality source FIX1 SHA logged; original records and scores unchanged")
