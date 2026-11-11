"""ONE-TIME R30 SAME-ROUND LOCAL QA FIX: add actually verified R12-R29 predecessor chain.

This corrects the initial R30 manifest's incomplete R12/R26 lineage.
It never touches any R12-R29 file, R014-017 board source, or the 19 R30 outputs.
Not an independent Reviewer verdict; cannot be rerun.
"""
from pathlib import Path
import hashlib
import json

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/"deliverables"/"integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement"
M=OUT/"MANIFEST.json"
OLD="221f2e860daf753019a185f6f64fe6414578b12075d0da32abb82ad65a3695fb"
RECEIPT=BASE/"state"/"ROUND030_MANIFEST_LOCAL_QA_PREDECESSOR_CHAIN_FIX1.json"
assert not RECEIPT.exists(),"FIX already completed, do not rerun"
old_bytes=M.read_bytes()
assert hashlib.sha256(old_bytes).hexdigest()==OLD,"not the original R30 manifest"
doc=json.loads(old_bytes)
assert len(doc["files"])==19
for f in doc["files"]:
    b=(OUT/f["relative_path"]).read_bytes()
    assert len(b)==f["bytes"] and hashlib.sha256(b).hexdigest()==f["sha256"]

dirs=sorted(d for d in (BASE/"deliverables").glob("integrated-r*") if (d/"MANIFEST.json").is_file())
verified={}
for d in dirs:
    name=d.name.split("-")[1]
    if not name.startswith("r"):
        continue
    try:
        nr=int(name[1:])
    except ValueError:
        continue
    if nr<12 or nr>29 or d.name=="integrated-r17-numeric-product-leads":
        continue
    key=f"R{nr:03d}_integrated_MANIFEST"
    assert key not in verified
    verified[key]=hashlib.sha256((d/"MANIFEST.json").read_bytes()).hexdigest()
assert len(verified)==18 and all(f"R{k:03d}_integrated_MANIFEST" in verified for k in range(12,30))
prior=doc["immutable_predecessor_SHA256"]
for nr in range(23,30):
    short=f"R{nr:03d}"
    if short in prior:
        assert prior[short]==verified[f"R{nr:03d}_integrated_MANIFEST"],short
assert verified["R023_integrated_MANIFEST"]==prior["R023_local_fix1_not_independent_review"]
prior.update(verified)
doc["local_same_round_fix1"]={
    "reason":"R30 initial MANIFEST omitted actual R12 and R26 and R13-R22 integrated manifest ancestors; add-only verified lineage correction",
    "old_manifest_SHA256":OLD,
    "old_manifest_bytes":len(old_bytes),
    "signed_R30_output_count_unchanged":19,
    "independent_review_verdict":"NONE_UNREVIEWED",
    "all_owner_GC_purchase_release":False
}
new=(json.dumps(doc,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
M.write_bytes(new)
new_hash=hashlib.sha256(new).hexdigest()
receipt={
    "phase":"R30_LOCAL_SAME_ROUND_MANIFEST_QA_FIX1_UNREVIEWED",
    "round":30,
    "old_sha256":OLD,"old_bytes":len(old_bytes),
    "new_sha256":new_hash,"new_bytes":len(new),
    "verified_R12_R29_integrated_predecessor_SHA256":verified,
    "original_19_R30_file_SHA256_and_bytes_unchanged":True,
    "original_R29_and_R30_preliminary_unchanged":True,
    "independent_Reviewer_CONTINUE":False,
    "global_DONE":False,"material_release":False,"purchase_authorized":False
}
RECEIPT.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
print("R30_PREDECESSOR_CHAIN_FIX1",new_hash,"BYTES",len(new))
print("ALL_R12_R29_INTEGRATED",len(verified),"R30 signed files unchanged",len(doc["files"]))
print("AUDIT_RECEIPT",RECEIPT.name,hashlib.sha256(RECEIPT.read_bytes()).hexdigest())
