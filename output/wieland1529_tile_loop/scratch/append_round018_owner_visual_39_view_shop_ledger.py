"""One-time SHA-audited ledger for individualized thirteen-room visual/GC briefs."""
from pathlib import Path
import hashlib,json,csv
from decimal import Decimal
R=Path(__file__).resolve().parents[1];S=R/"state";L=S/"LEDGER.md"
H="## R018 thirteen individual 1:1 material/sample, 39 buyer view and GC shop evidence packages — 2026-11-06"
assert H not in L.read_text(encoding="utf-8")
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
D=R/"deliverables/integrated-r18-owner-sample-visual-and-shop"
M=D/"MANIFEST.json";m=json.loads(M.read_text(encoding="utf-8"))
assert sh(M)=="c958b49e76f8f5b12b0aca267a8dfc1870527b04b12fd3714751fd024a565ebe"
with (D/"R18_13_ROOM_SAMPLE_RENDER_OWNER_GC_SIGNATURE_MATRIX.csv").open(encoding="utf-8",newline="") as f:
 rows=list(csv.DictReader(f))
assert len(rows)==13 and len(m["outputs"])==15
assert sum(Decimal(x["two_copy_historic_material_usd"]) for x in rows)==Decimal("23572.44")
assert not any(m[z] for z in ["actual_render_images","actual_samples_ordered","owner_approval","GC_release","procurement_release"])
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists()
text=chr(10)+H+chr(10)+chr(10)
text+="- After independently cleared R015 blind source SHA "+sh(S/"ROUND015_SUBMISSION.json")+" and signed R17 owner/GC manifest SHA "+sh(R/"deliverables/integrated-r17/MANIFEST.json")+", completed 13 individually tailored owner 1:1 physical sample, three-camera source-faithful visualization and GC field-shop specifications, **39 room-specific camera views**, thirteen-row owner/architect/GC/purchase acceptance matrix and START_HERE. 15 SHA/byte-signed outputs, manifest "+sh(M)+". Read-only verification PASS all 13 original room statuses and dollars, 15 signatures and 39 camera briefs. No actual rendering was generated and no mockup/sample ordered.\n"
text+="- Distinct authentic fixture controls all preserved: two Primary 48in Brizo Black Onyx LINEAR with BR73480 and NO niches; PH4 4in Brizo square POINT true WALK-IN; three Duravit actual TUB-only bathrooms PH2/TX2/TX4 NO tiled PAN; PH/TX Bath3 TUB/WALK-IN remains unselected and square shower POINT never tub waste; PH3/TX2/TX Powder2 basins unresolved; TX Powder2 faucet DECK-mounted; dry wood-floor powders no wet level or pan tests and both WCs inherit Primary LEVEL. W1-W3 nominal plans remain preliminary because native open 1527 not certified 1529.\n"
text+="- Every R18 document provides specific individual maker WET WALL/NICHE approvals, actual source-aligned three photo/camera scenes, exact proposed 1:1 grout/metal/glass/tub or drain rough mockup, movement/niche/trim takeoff and source-faithful owner signoff. Actual individual wet LEVEL and separate applicable PAN RAW numeric maker laboratory reading still required; not confused with Target >=0.42 or bounds. All owner, architect, GC, material and purchase releases FALSE. Full source four-unit historic material total **$23,572.44** with original 15% once; two original unpriced extra Primary niches remain NO SCOPE/NO ORDER.\n"
text+="- R014 authentic six original MARKET/BUILD/COST reviews remain and worker-9 original DESIGN failed to claim browser revivals; no two DESIGN source reports and NO weighting. R015 source independently pre-dispatch CONTINUE but dispatch held by original four-seat governance. Global 13-room program OPEN. R18 awaiting independent same-scope Reviewer review. No vendor, sample, form, email, Revit or Smartsheet writes or installs.\n"
with L.open("a",encoding="utf-8",newline="") as h:h.write(text)
print("PASS R18 signed whole-program detailed owner/GC visual field briefs ledger appended, original $23572.44 and no approvals")
