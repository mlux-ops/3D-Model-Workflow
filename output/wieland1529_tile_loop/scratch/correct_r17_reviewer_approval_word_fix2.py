"""Same-R015 narrow Reviewer R17 wording FIX; exact signed SHA chain."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]; S=R/"state"; D=R/"deliverables/integrated-r17"
B=D/"R17_13_ROOM_DESIGN_AND_RELEASE_FIELD_BOOK.md"; M=D/"MANIFEST.json"
REC=S/"ROUND015_R17_REVIEWER_BOOK_AUTHORIZATION_WORD_FIX2.json"
assert not REC.exists()
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
before_m=fp(M)
assert before_m["sha256"]=="8f1e3070686a39b2423fe9287a6708303a114c0667e14d402e29c99840ab04ec"
src=S/"ROUND015_SUBMISSION.json"
assert fp(src)["sha256"]=="cf150c8156ab556c0b7dee386f62d8cdda33a4e14ea54019731fc345957dbca8"
assert not (S/"ROUND015_CRITIC_DISPATCH.json").exists()
data=json.loads(M.read_text(encoding="utf-8"))
old=data["outputs"]
assert all(fp(D/k)==v for k,v in old.items())
other={k:fp(D/k) for k in old if k!=B.name}
previous=fp(B)
t=B.read_text(encoding="utf-8")
oldtext="Corresponding approved WET WALL-only conditional designs"
newtext="Conditional flat-tile wet WALL design studies; manufacturer Wet Areas listing is NOT an owner or GC approval"
assert t.count(oldtext)==1
B.write_text(t.replace(oldtext,newtext),encoding="utf-8")
data["outputs"][B.name]=fp(B)
M.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert all(fp(D/k)==v for k,v in other.items())
assert all(fp(D/k)==v for k,v in data["outputs"].items())
assert not data["owner_approval"] and not data["procurement_release"]
assert data["R014_weighted_scoring"] is None
assert fp(src)["sha256"]=="cf150c8156ab556c0b7dee386f62d8cdda33a4e14ea54019731fc345957dbca8"
REC.write_text(json.dumps({"round":15,"as_of":"2026-11-06","reviewer":"worker-14",
 "scope":"Reviewer precise R17 text fix only: maker wet authorization is not owner approval",
 "old_r17_owner_book":previous,"new_r17_owner_book":fp(B),
 "old_r17_manifest":before_m,"new_r17_manifest":fp(M),
 "six_other_r17_outputs_unchanged":other,
 "R015_frozen_source_sha256_unchanged":fp(src)["sha256"],
 "R014_weighted_scoring":None,"R015_critic_dispatch":False,
 "owner_approval":False,"procurement_release":False},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("PASS R17 precise owner-approval maker wording FIX2; 6 other outputs stable, R015 source stable, no release")
print("R17_MANIFEST_SHA",fp(M)["sha256"])
print("FIX2_RECEIPT_SHA",fp(REC)["sha256"])
