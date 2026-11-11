"""Same-R35 pre-release source typo correction with exact old/new SHA+bytes.
Only R35 current package is touched, no predecessor/history/owner source change.
"""
from pathlib import Path
import hashlib,json
base=Path(__file__).resolve().parents[1]
out=base/"deliverables/integrated-r35-primary-wc-dual-floor-pan-grate-threshold-13room-GC"
m=out/"MANIFEST.json"
oldmanifest=hashlib.sha256(m.read_bytes()).hexdigest()
assert oldmanifest=="d00e9e6cf76778b0a3072d1c361c7e080e7c1fc3e7141f4e14d41e80ccc80a0f"
file=out/"R35_CONTRACT_A_V_B_PAN_QUOTE_MATERIAL_ALLOCATION_AND_GC_PAYMENT_BOOK.md"
old=file.read_bytes()
assert old.count(b"7.79914")==1
new=old.replace(b"7.79914",b"7.80000")
assert len(old)==len(new)
file.write_bytes(new)
data=json.loads(m.read_text(encoding="utf-8"))
entry=next(x for x in data["files"] if x["relative_path"]==file.name)
assert entry["bytes"]==len(old) and entry["sha256"]==hashlib.sha256(old).hexdigest()
entry["bytes"]=len(new);entry["sha256"]=hashlib.sha256(new).hexdigest()
m.write_bytes((json.dumps(data,indent=2,ensure_ascii=False)+"\n").encode("utf-8"))
print("R35_SAME_ROUND_RATE_FIX",file.name)
print("OLD_R35_MANIFEST_SHA",oldmanifest)
print("OLD_FILE_SHA",hashlib.sha256(old).hexdigest(),"NEW_FILE_SHA",hashlib.sha256(new).hexdigest(),"BYTES",len(new))
print("NEW_R35_MANIFEST_SHA",hashlib.sha256(m.read_bytes()).hexdigest())
