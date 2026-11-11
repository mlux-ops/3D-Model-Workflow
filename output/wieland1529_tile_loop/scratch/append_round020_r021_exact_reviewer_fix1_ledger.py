"""One-time exact independent Reviewer R20/R21 FIX1 audit ledger."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];S=R/"state";L=S/"LEDGER.md"
H="## SAME-R020/R021 independent Reviewer carton physical contradiction and per-room witness applicability FIX1 — 2026-11-06"
assert H not in L.read_text(encoding="utf-8")
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rec=S/"ROUND020_R021_REVIEWER_EXACT_CASE_SCOPE_FIX1.json"
r20=R/"deliverables/integrated-r20-tx-tub-public-retail-and-carton-holds/MANIFEST.json"
r21=R/"deliverables/integrated-r21-install-witness-sequence/MANIFEST.json"
assert h(rec)=="f3ba0190d14be60e8cd4079de8eeba69f1616129f4c440c684d780a0e3f7aa2a"
assert h(r20)=="9559680c13f602d22fdf32ff5c3eac42e3ead515f6fcff0d2d34aa231dd676ae"
assert h(r21)=="a212a902fcf61433cbcf165c05b07681abffcb3f70ae9f8deeb8e0756989ad66"
x=json.loads(rec.read_text(encoding="utf-8"))
assert x["retailer_original_conflicting_piece_count"]=="8" and x["retailer_original_conflicting_case_sf"]=="17.49"
assert x["calculated_impossible_sf_per_nominal_12x24_piece"]=="2.18625"
assert x["retailer_case_metrics_available_to_order"] is False and x["supplier_confirmed_EL30_carton_yield"] is None
assert x["specific_scope_cells_changed"]==104
assert x["R21_manifest_after"]["sha256"]==h(r21)
assert x["R20_manifest_after"]["sha256"]==h(r20)
assert not x["owner_approval"] and not x["GC_release"] and not x["procurement_release"]
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists()
t="\n"+H+"\n\n"
t+="- Original sole standing non-Pro Reviewer worker-15 returned precise SAME-R020/R021 FIX: Sutherlands EL301224J1PV retailer 8 pieces and 17.49SF/carton for nominal 12x24 is internally physically contradictory, because nominal 8×2SF=16SF maximum and 17.49/8=2.18625SF per piece > nominal. Preserved both public original source claims separately for audit but explicitly labeled manufacturer carton count/coverage **UNCONFIRMED/NO ORDER BASIS**, not invented nine pieces; no procurement from historic or merchant carton. R20 public source CSV and explanatory book amended, R20 manifest SHA old c298f924... -> new "+h(r20)+".\n"
t+="- R21 156-row, 13-room × 12-step inspector/GC source-specific witness matrix identified generic narrative leakage despite correct applicability flags: all dry powders and inherited WCs need no shower wet WALL/NICHE or PAN lab, six standalone bath LEVEL tests must not import WC parent, and generic selected Brizo rough text was inappropriate for Duravit tub-only, dry vanity or DECK Tecturis TX Powder2. Corrected **104 specific_evidence_scope cell values ONLY** with actual source owner plumbing (PH/TX Primary 48in BNX LINEAR/BR73480/no niche + parent WC; PH4 4in BNX POINT WALK-IN; Bath3 owner branch unresolved selected square shower POINT not tub waste; actual PH2/TX2/TX4 Duravit TUB no tiled PAN; PH3/TX2/TX Powder2 unselected basins; dry powder wood floors). All remaining 156-row IDs, witness owners, existing application N/A, shop proof and release FALSE fields unchanged. R21 SHA old c277d5f8... -> new "+h(r21)+"; parent R20 pointer updated to current.\n"
t+="- Exact old/new SHA receipt "+h(rec)+" is independent reproduction audit; R20 four signed outputs and R21 three signed outputs rechecked with read-only verifiers, R21 stronger per-room assertions PASS, all original R014/15/R17/18/19 SHA preserved. No original actual native 1529 (open 1527), raw exact LEVEL/POINT/LINEAR wet laboratory specimen, actual Chicago installed bid/lot or verified case, signed owner/GC budget or purchasing; historical four-unit tile MATERIAL $23,572.44 with 15% original gross once unchanged. No original DESIGN worker9, R014 6/8/no scores, R015 independently source-cleared but critic dispatch blocked. Five-section SAME-R020/R021 Reviewer resubmission queued to worker-15; exact independent follow-up verdict pending. Entire objective OPEN.\n"
with L.open("a",encoding="utf-8",newline="") as f:f.write(t)
print("PASS R020 case physical contradiction/R021 104 room-specific witness scope FIX1 signed ledger, old/new SHA and all releases FALSE")
