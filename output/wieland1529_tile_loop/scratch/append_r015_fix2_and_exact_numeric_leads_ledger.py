"""One-time append exact R015/R17 second-review corrective audit and non-lab numeric leads."""
from pathlib import Path
import hashlib,json,csv
R=Path(__file__).resolve().parents[1];S=R/"state";LEDGER=S/"LEDGER.md"
H="## Round015 independent FIX1 complete, final R17 owner-approval language and two exact public DCOF research leads — 2026-11-06"
assert H not in LEDGER.read_text(encoding="utf-8")
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
src=S/"ROUND015_SUBMISSION.json"
fix1=S/"ROUND015_PREDISPATCH_REVIEWER_FIX1_AND_R17_MAKER_FACTS.json"
fix2=S/"ROUND015_R17_REVIEWER_BOOK_AUTHORIZATION_WORD_FIX2.json"
r17=R/"deliverables/integrated-r17/MANIFEST.json"
leads=R/"deliverables/integrated-r17-numeric-product-leads/MANIFEST.json"
assert fp(src)["sha256"]=="cf150c8156ab556c0b7dee386f62d8cdda33a4e14ea54019731fc345957dbca8"
assert fp(r17)["sha256"]=="78c0849c14a83dba65023d7ede812181d7360d2c7cd00eaa2f8cc0e33927aac1"
assert fp(leads)["sha256"]=="988166847464298c8341061e9bebdc7e4fedd83dc09fcaff5c5e6d80eecd146a"
assert fp(fix1)["sha256"]=="f5d4b43f9c956022f843aaf6027045bd7b4aef7058f39316145199fbc7706557"
assert fp(fix2)["sha256"]=="9dcc484041b24c816bf5b6ae25b13ec8b717730a690cad8d104927feaa1db631"
s=json.loads(src.read_text(encoding="utf-8"))
d=json.loads(leads.read_text(encoding="utf-8"))
assert s["critic_dispatch"]=="NOT_DISPATCHED" and s["weighted_scoring"] is None
assert not d["owner_approval"] and not d["procurement_release"]
assert d["original_raw_wet_LEVEL_lab_available"] is False
assert not (S/"ROUND015_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND014_SCORING.json").exists()
assert not (S/"ROUND014_CRITIC_COLLECTION.json").exists()
t=chr(10)+H+chr(10)+chr(10)
t+="- Actual Reviewer-14 first pre-dispatch verdict was FIX. Its exact blind-role, Daltile maker-country, grout and R17 count defects corrected BEFORE any R015 critic dispatch. Source SHA "+fp(src)["sha256"]+", first surgical fix receipt "+fp(fix1)["sha256"]+". R15 source remains 4 neutral current candidate hash/bytes, 2 prime/Reviewer-only private maps, 32 local verified links. Still UNSCORED/UNDISPATCHED until real preflight CONTINUE."+chr(10)
t+="- Reviewer identified R17 field-book ambiguity: individual flat tile maker Wet Areas authorization described as approved WET WALL conditional design, improperly could signal owner acceptance. Exact one-phrase correction states manufacturer application is NOT owner or GC approval, R17 owner book and manifest re-signed only; six other R17 outputs unchanged. Old R17 manifest 8f1e3070686a39b2423fe9287a6708303a114c0667e14d402e29c99840ab04ec -> new "+fp(r17)["sha256"]+". Exact word-fix2 receipt "+fp(fix2)["sha256"]+". Source R015 remains SHA "+fp(src)["sha256"]+". R17 13/27/65/25/13 verification PASS, all owner/GC/purchase fields false, historical $23,572.44 material and original once-only 15% intact."+chr(10)
t+="- Independently published exact SKU possible LEVEL-only floor study: TileBar New Rock Perla White matte SKU TLMGAGPR12X24 and Fumo Light Gray chiseled matte SKU TLMGAGFM12X24CH publicly report DCOF 0.66 each; merchant source pages show price $9.50/$9.95 per SF and 9.68 SF/box. These values are *not primary raw manufacturer/laboratory ANSI wet test records*; strict project raw exact lab gate still NULL/FAIL, current real Chicago lot/installed GC bid and 1529 dimensions unknown. Other fields in independently signed research manifest "+fp(leads)["sha256"]+"; no owner purchase/approval or alteration of R015 frozen candidates or predecessor R17. Distinguish maker target, public numerical marketing data, lab report, dated historic quote and real current GC bid."+chr(10)
t+="- SAME-R015 five-section Reviewer correction resubmission was queued for worker-14; actual post-correction verdict pending as of this ledger checkpoint. Original R014 DESIGN worker-9 FAILED after two browser unclaimed revivals, 6/8 authentic files only, so no complete collection, no formal weighted score, no invented specialist. Entire 13-room improvement objective OPEN."+chr(10)
with LEDGER.open("a",encoding="utf-8",newline="") as f:f.write(t)
print("PASS SAME-R015 exact source/owner authorization FIX1/FIX2 SHA ledger and external exact numeric-but-not-raw-LAB research appended; R014/R015 no scores/release")
