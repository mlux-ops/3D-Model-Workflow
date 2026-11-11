"""One-time new 156-point 13-room genuine GC shop/inspector witness plan SHA ledger."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];S=R/"state";L=S/"LEDGER.md"
H="## R021 156 source-specific manufacturer wet lab / plumbing / field witness photo and GC procurement gates across all 13 rooms — 2026-11-06"
assert H not in L.read_text(encoding="utf-8")
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
M=R/"deliverables/integrated-r21-install-witness-sequence/MANIFEST.json"
assert h(M)=="c277d5f8eec635150d069b73feefad040e885ebc7a2e7d5d369bcba56bb6c202"
m=json.loads(M.read_text(encoding="utf-8"))
assert len(m["outputs"])==3 and m["rooms"]==13 and m["evidence_hold_rows"]==156
assert m["unique_wet_rooms"]==8 and m["actual_Duravit_tub_only_rooms"]==3
assert m["original_hist_material_4unit_usd"]=="23572.44"
assert m["original_15pct_waste_in_old_gross_once"]
assert not any(m[k] for k in ("actual_1529_field_verified","actual_inspections_completed","owner_approval","GC_release","procurement_release"))
for n,s in m["outputs"].items():
 assert h(M.parent/n)==s["sha256"]
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists()
text="\n"+H+"\n\n"
text+="- Authored a **new independently testable construction-field witness and specific physical shop request**, not generic duplicate verification: signed additive R21 manifest SHA "+h(M)+" holds 156 individual stop-before-cover inspection evidence cells = **13 rooms × 12 sequenced phases**, each with responsible plumber/tile setter/waterproof inspector/architect/GC/owner, permitted application, expected field photo/test report, 1529 measured W1–W3, exact maker individual WALL/NICHE and raw LEVEL/PAN lab, drain rough shop, manufacturer-approved waterproofing, locally verified case/lot/quote and distinct final purchaser approval. Original historic source/owner approvals untouched; ZERO field test or sample falsely claimed complete.\n"
text+="- Eight actual wet bath programs are precisely segregated: PH/TX Primary selected 48in Brizo BNX LINEAR + BR73480 rough/no extra niche and shared WC floor LEVEL; PH4 selected BNX 4in SQUARE POINT WALK-IN; PH/TX Bath3 two owner TUB-vs-WALK-IN unresolved with separate selected Delta DT062412 Chrome and Brizo BT062415-BNX SQUARE POINT drains that are NEVER tub wastes; PH2/TX2/TX4 selected Duravit TUB/Hansgrohe PH2 Matte White/TX2 Chrome/TX4 Matte White, NO tiled shower PAN. Three dry powder vanity walls with wood floor need NO wet bath LEVEL or shower PAN; two WC rooms inherit Primary LEVEL once and no independent tile purchase. No 1527 model dimensions certified as 1529.\n"
text+="- New R21 field booklet cites original Delta 113919 Rev B and Brizo 113920 Rev C for traditional clamped liner/preslope/weep shop and explicitly prohibits inferred bonded waterproof compatibility, selected LINEAR rough substitution or fabricated Chicago code flood-test duration. No actual manufacturer or third-party raw individually measured wet floor lab exists; recorded maker Target and Zia Tier B summary remain unresolved. All current Chicago lot/case/complete installed bids and signed owner room cap/GC/PO are NULL/FALSE. Original four-unit material-only $23,572.44 and 15% waste once preserved.\n"
text+="- Independent non-Pro successor worker-15 accepted prior R019 same-round exact FIX2 and checked R020 dependent parent relink. Combined R020 procurement and R021 construction witness five-section Reviewer report sent to the same worker; exact audit verdict pending at this ledger checkpoint. R014 6/8 authentic original critiques due worker9 FAILED, R015 source cleared but original DESIGN seat blocks 4-seat critic dispatch, weighted scores NULL, global 13-room program OPEN.\n"
with L.open("a",encoding="utf-8",newline="") as f:f.write(text)
print("PASS 156 individualized R21 construction photo/witness and wet technical holds SHA ledger appended; no false release")
