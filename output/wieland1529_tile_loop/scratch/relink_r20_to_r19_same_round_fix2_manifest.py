"""Re-sign only newer R20 manifest parent pointer after exact reviewer R19 FIX2."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];S=R/"state"
D=R/"deliverables/integrated-r20-tx-tub-public-retail-and-carton-holds"
M=D/"MANIFEST.json";R19=R/"deliverables/integrated-r19-manufacturer-wet-evidence-grades/MANIFEST.json"
REC=S/"ROUND019_R20_R19_PARENT_SHA_RELINK_FIX2.json"
assert not REC.exists()
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
original=fp(M)
assert original["sha256"]=="6afb6f05c745e2b7cb84305dafb2c3729255e8535de73c19ec5f4d7de59605ae"
newparent=fp(R19)
assert newparent["sha256"]=="cbbc76a1a0fb6cb03e2109c3d929e853b126053bfa6a1f4cdafea2a3e7b8cace"
m=json.loads(M.read_text(encoding="utf-8"))
assert m["R19_signed_manifest_sha"]=="145523cf3a6953a8349e49d32d1eade41df3e723737237a7119ff4f508d8cde1"
original_outputs={name:fp(D/name) for name in m["outputs"]}
assert all(original_outputs[n]==s for n,s in m["outputs"].items())
m["R19_signed_manifest_sha"]=newparent["sha256"]
M.write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert all(fp(D/n)==s for n,s in original_outputs.items())
assert not m["procurement_release"] and not m["GC_release"] and not m["owner_approval"]
assert fp(R/"deliverables/integrated-r17/MANIFEST.json")["sha256"]==m["R17_signed_manifest_sha"]
assert fp(R/"deliverables/integrated-r18-owner-sample-visual-and-shop/MANIFEST.json")["sha256"]==m["R18_signed_manifest_sha"]
assert fp(S/"ROUND015_SUBMISSION.json")["sha256"]==m["R015_original_frozen_submission_sha"]
REC.write_text(json.dumps({"as_of":"2026-11-06","round":19,"reason":"Parent R19 reviewer FIX2 re-signed original; R20 additive manifest only parent SHA updated; all four actual R20 signed outputs byte-identical",
 "old_R20_manifest":original,"new_R20_manifest":fp(M),"new_R19_parent":newparent,
 "unchanged_R20_outputs":original_outputs,"R014_scoring":None,"R015_scoring":None,
 "owner_approval":False,"GC_release":False,"procurement_release":False},indent=2)+"\n",encoding="utf-8")
print("PASS R20 dependent manifest relink to R19 precise FIX2 SHA, original 4 R20 outputs unchanged and all owner/GC release false")
print("R20_MANIFEST_SHA",fp(M)["sha256"])
print("RELINK_RECEIPT_SHA",fp(REC)["sha256"])
