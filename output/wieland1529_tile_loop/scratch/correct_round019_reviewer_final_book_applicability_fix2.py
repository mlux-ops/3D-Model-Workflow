"""One-time SAME R019 narrow Reviewer FIX2: no false wet DCOF in N/A rooms."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
S=R/"state"
D=R/"deliverables/integrated-r19-manufacturer-wet-evidence-grades"
M=D/"MANIFEST.json";B=D/"R19_7_COLOR_SGS_DCOF_EVIDENCE_QUALITY_AND_INSTALLER_HOLDS.md"
REC=S/"ROUND019_REVIEWER_SOURCE_APPLICATION_FIX2.json"
assert not REC.exists()
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
before_m=fp(M)
assert before_m["sha256"]=="145523cf3a6953a8349e49d32d1eade41df3e723737237a7119ff4f508d8cde1"
m=json.loads(M.read_text(encoding="utf-8"))
other={name:fp(D/name) for name in m["outputs"] if name!=B.name}
before_b=fp(B)
text=B.read_text(encoding="utf-8")
old="Strict 1529 wet LEVEL and PAN release remains **FAIL/NULL** for every room until these are reconciled."
new="Strict 1529 original raw wet LEVEL DCOF lab remains **FAIL/NULL for applicable tiled bathrooms**; independently applicable LINEAR or SQUARE POINT shower PAN raw wet lab remains **FAIL/NULL**. DRY powder wood floors require no tiled bath LEVEL or shower PAN tests (**N/A**); both WC rooms inherit their respective Primary LEVEL test once; actual Duravit TUB-only rooms have no tiled shower PAN (**N/A**)."
assert text.count(old)==1
B.write_text(text.replace(old,new),encoding="utf-8")
m["outputs"][B.name]=fp(B)
M.write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert all(fp(D/n)==s for n,s in m["outputs"].items())
assert all(fp(D/n)==s for n,s in other.items())
assert fp(R/"deliverables/integrated-r17/MANIFEST.json")["sha256"]==m["R17_original_signed_manifest_sha256"]
assert fp(R/"deliverables/integrated-r18-owner-sample-visual-and-shop/MANIFEST.json")["sha256"]==m["R18_signed_manifest_sha256"]
assert fp(S/"ROUND014_SUBMISSION.json")["sha256"]==m["R014_source_sha256"]
assert fp(S/"ROUND015_SUBMISSION.json")["sha256"]==m["R015_source_sha256"]
assert not m["procurement_release"] and not m["owner_approval"] and not m["GC_release"]
assert m["R014_scoring"] is None and m["R015_scoring"] is None
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists()
REC.write_text(json.dumps({
 "round":19,"as_of":"2026-11-06","reviewer":"worker-15",
 "scope":"Only R19 owner-facing line 7 overbroad wet LEVEL/PAN every-room claim; narrow to applicable baths, WC parent once, powder and TUB PAN N/A",
 "old_book":before_b,"new_book":fp(B),
 "old_manifest":before_m,"new_manifest":fp(M),
 "three_other_signed_R19_outputs_SHA_byte_unchanged":other,
 "original_seven_color_SGS_CSV_unchanged":True,
 "R014_R015_R017_R018_unchanged":True,
 "R014_scoring":None,"R015_scoring":None,
 "owner_approval":False,"GC_release":False,"procurement_release":False,
 "global_13_room_done":False
},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("PASS SAME-R019 only book wet lab applicability overclaim corrected; three other R19 signed outputs unchanged, original source/owner release false")
print("R19_MANIFEST_SHA",fp(M)["sha256"])
print("FIX2_RECEIPT_SHA",fp(REC)["sha256"])
