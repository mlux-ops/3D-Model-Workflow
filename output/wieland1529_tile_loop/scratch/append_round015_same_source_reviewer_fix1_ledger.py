"""One-time independent FIX1 source correction hash trail, no frozen older mutations."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];S=R/"state"
LEDGER=S/"LEDGER.md"
HEADER="## Round015 same-round independent blind/source maker FIX1 and R17 surgical re-sign — 2026-11-06"
assert HEADER not in LEDGER.read_text(encoding="utf-8")
P=S/"ROUND015_PREDISPATCH_REVIEWER_FIX1_AND_R17_MAKER_FACTS.json"
X=json.loads(P.read_text(encoding="utf-8"))
def sha(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(S/"ROUND015_SUBMISSION.json")==X["corrected_submission"]["sha256"]
assert sha(R/"deliverables/integrated-r17/MANIFEST.json")==X["corrected_r17_manifest"]["sha256"]
assert not (S/"ROUND015_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
text=chr(10)+HEADER+chr(10)+chr(10)
text+="- Standing non-Pro Reviewer worker-14 actual SAME-R015 pre-dispatch FIX: candidate C paragraphs directly identified original Cortar Clay/Bone and original niche; common critic-readable shared maker source called these original source LEVEL, revealing private role. Daltile individual White Elect EL30 current 12x24 matte page says MEXICO, not USA; Grey Koncrete KC04 current 12x24 matte USA recommends **3/16-inch** joint, not 1/8-inch. R17 owner book also misstated both maker values and counted six instead of five actual CSV outputs. Strict Daltile Target wet >=0.42 still NOT raw measured SKU wet DCOF and stays FAIL."+chr(10)
text+="- Exact SAME-R015 role text/maker corrections performed before any specialist dispatch; R015 old SHA "+X["initial_submission"]["sha256"]+" -> corrected SHA "+X["corrected_submission"]["sha256"]+"; common neutral research SHA "+X["research_updated"]["sha256"]+". Four original candidate file old/new SHA/byte fingerprints auditable in state/"+P.name+" SHA "+sha(P)+". Private keys remained confidential; no R014 or older scoring touched."+chr(10)
text+="- Separate additive R17 owner field book alone corrected and re-signed, existing R17 manifest old SHA "+X["initial_r17_signed_manifest"]["sha256"]+" -> new SHA "+X["corrected_r17_manifest"]["sha256"]+"; other six signed R17 files unchanged and individually checked. 13 rooms, 27 historic source lines, 65 trade actions, 25 preliminary wall studies and $23,572.44 four-unit tile MATERIAL history with 15% embedded once remain PASS. All raw lab, exact Chicago lot/installed bid, actual 1529 and owner/GC releases remain NULL/FALSE."+chr(10)
text+="- Correction was surgically applied and read-only source plus R17 verifier PASSED, four neutral candidates/32 local links, no critic dispatch, no formal R015 scores. Resubmitting FIX1 to SAME worker-14 for independent pre-dispatch verdict. Original R014 DESIGN worker-9 failed browser revival and no valid 8/8 collection or weighting; its genuine seat must not be impersonated."+chr(10)
with LEDGER.open("a",encoding="utf-8",newline="") as f:f.write(text)
print("PASS exact R015 source and R17 maker/count FIX1 ledger appended, all released states false")
print("RECEIPT_SHA",sha(P))
