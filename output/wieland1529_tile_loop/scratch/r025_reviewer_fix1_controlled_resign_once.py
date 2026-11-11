"""Apply independent R025 Reviewer21 PRECISE FIX without touching prior signed rounds."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
source=R/"state/ROUND025_PH_THREE_ROOM_PREPARED_NOT_SUBMITTED.json"
owners=R/"state/ROUND025_13_OWNER_SELECTION_CARDS_SHA.json"
s=json.loads(source.read_text(encoding="utf8"))
o=json.loads(owners.read_text(encoding="utf8"))
assert "FIX1" not in s and "FIX1" not in o
original_source_receipt=source.read_bytes()
original_owner_receipt=owners.read_bytes()
changes=[]
for rel,old in s["files"].items():
 p=R/rel;b=p.read_bytes()
 assert hashlib.sha256(b).hexdigest()==old["sha256"] and len(b)==old["bytes"],rel
 text=b.decode("utf8")
 new=text
 if "/prepared/candidates/" in rel:
  rid=rel.split("/")[1]
  assert rid in ("PH-PRIMARY","PH-BATH3","PH-BATH4"),rel
  if rid=="PH-PRIMARY":
   new=new.replace("Selected 48-inch LINEAR PAN. If PAN applies, same exact","Selected 48-inch LINEAR PAN. Same exact")
   new=new.replace("to the selected POINT/LINEAR drain","to the retained Black Onyx 48-inch LINEAR drain and factory solid BNX grate")
   new=new.replace("For the PH-BATH3 TUB branch there is NO pan and the conditional Delta POINT drain is not a tub waste. ","")
   new=new.replace("Resolve LEVEL net and separate PAN net/Primary WC net by native receipt and owner program. New-option illustrative gross = LEVEL net x1.15 + installer-cut PAN net x1.25 + inherited PH-WC net x1.15 only when Primary. If TUB branch, PAN N/A.",
    "Resolve actual Primary LEVEL, LINEAR PAN and inherited PH-WC net areas separately using native element receipts; prospective replacement gross = LEVEL net x1.15 + LINEAR PAN net x1.25 + PH-WC net x1.15 (count WC once). Primary remains a selected WALK-IN wet-room program with LINEAR PAN.")
   new=new.replace(" plus niche 6.50 SF/box."," (NO niche cartons are needed).")
   new=new.replace("No owner program selected for PH3, no owner grout/budget upgrade endorsement",
    "Primary LINEAR wet-room program is selected, but grout/budget upgrade endorsement remains owner-only")
  elif rid=="PH-BATH4":
   new=new.replace("Selected four-plane POINT PAN. If PAN applies, same exact","Selected four-plane POINT PAN. Same exact")
   new=new.replace("to the selected POINT/LINEAR drain","to the selected Brizo Black Onyx four-inch square POINT drain")
   new=new.replace("For the PH-BATH3 TUB branch there is NO pan and the conditional Delta POINT drain is not a tub waste. ","")
   new=new.replace("Resolve LEVEL net and separate PAN net/Primary WC net by native receipt and owner program. New-option illustrative gross = LEVEL net x1.15 + installer-cut PAN net x1.25 + inherited PH-WC net x1.15 only when Primary. If TUB branch, PAN N/A.",
    "Resolve PH-BATH4 LEVEL net and separate four-plane POINT PAN net using native element receipts; prospective replacement gross = LEVEL net x1.15 + POINT PAN net x1.25. PH-BATH4 remains owner-selected WALK-IN; there is no independent WC floor allocation.")
   new=new.replace("No owner program selected for PH3, no owner grout/budget upgrade endorsement",
    "PH-BATH4 WALK-IN is owner-selected, but niche color and grout/budget upgrade endorsement remain owner-only")
  elif rid=="PH-BATH3":
   new=new.replace("WALK-IN conditional four-plane POINT PAN; TUB branch has NO tiled PAN. If PAN applies, same exact",
    "Only if the owner selects WALK-IN: conditional Delta Chrome four-plane POINT PAN; same exact")
   new=new.replace("to the selected POINT/LINEAR drain","to the conditional Delta DT062412 Chrome square POINT drain")
   new=new.replace("Resolve LEVEL net and separate PAN net/Primary WC net by native receipt and owner program. New-option illustrative gross = LEVEL net x1.15 + installer-cut PAN net x1.25 + inherited PH-WC net x1.15 only when Primary. If TUB branch, PAN N/A.",
    "After owner decides PH-BATH3 TUB versus WALK-IN, use native element receipts for LEVEL net; only WALK-IN adds a separate POINT PAN net x1.25 to LEVEL net x1.15. Under TUB selection, PAN N/A and conditional Delta POINT is not a tub waste.")
  new=new.replace("board gate 125% **","provisional 125%-of-original comparison (NOT owner-allocated budget) **")
  new=new.replace("This is NOT a box-rounded, delivered,",
    "Actual room owner-allocated budget in ROOMS.json is NULL; this comparison is NOT an owner-approved cap or hard-gate PASS. This is NOT a box-rounded, delivered,")
  assert "to the selected POINT/LINEAR drain" not in new
  if rid!="PH-BATH3":
   assert "PH-BATH3 TUB branch" not in new and "No owner program selected for PH3" not in new
  if new!=text:
   p.write_text(new,encoding="utf8",newline="\n")
   bb=p.read_bytes()
   after={"sha256":hashlib.sha256(bb).hexdigest(),"bytes":len(bb)}
   changes.append({"path":rel,"before":old,"after":after})
   s["files"][rel]=after
s["FIX1"]={"independent_reviewer":"worker-21 PRECISE FIX","description":"Source room-specific POINT/LINEAR and TUB/WALK-IN language; provisional 125%-of-carried arithmetic, NULL owner allocation, exact PH3 half-up threshold","changes":changes}
source.write_text(json.dumps(s,indent=2)+"\n",encoding="utf8",newline="\n")
ownerchanges=[]
for rel,old in o["files"].items():
 p=R/rel;b=p.read_bytes()
 assert hashlib.sha256(b).hexdigest()==old["sha256"] and len(b)==old["bytes"],rel
 text=b.decode("utf8")
 new=text.replace("125% board cap","provisional 125%-of-original comparison (NOT owner-set budget)")
 if rel.endswith("/PH-BATH3.md"):
  assert "$1163.02/copy" in new
  new=new.replace("$1163.02/copy","$1163.03/copy")
  new=new.replace("Original source 15% waste included once",
   "Half-up rounding applies to $930.42 x 1.25 = $1163.025 to $1163.03. Original source 15% waste included once")
 if new!=text:
  p.write_text(new,encoding="utf8",newline="\n")
  bb=p.read_bytes()
  after={"sha256":hashlib.sha256(bb).hexdigest(),"bytes":len(bb)}
  ownerchanges.append({"path":rel,"before":old,"after":after})
  o["files"][rel]=after
parent="state/ROUND025_PH_THREE_ROOM_PREPARED_NOT_SUBMITTED.json"
assert parent in o["immutable_parents"]
old_parent=o["immutable_parents"][parent]
assert hashlib.sha256(original_source_receipt).hexdigest()==old_parent["sha256"] and len(original_source_receipt)==old_parent["bytes"]
updated_parent=source.read_bytes()
o["immutable_parents"][parent]={"sha256":hashlib.sha256(updated_parent).hexdigest(),"bytes":len(updated_parent)}
o["FIX1"]={"independent_reviewer":"worker-21 PRECISE FIX","rounding":"ROUND_HALF_UP", "old_source_receipt_sha256":hashlib.sha256(original_source_receipt).hexdigest(),
 "new_source_receipt_sha256":hashlib.sha256(updated_parent).hexdigest(),
 "old_owner_receipt_sha256":hashlib.sha256(original_owner_receipt).hexdigest(),"changes":ownerchanges}
owners.write_text(json.dumps(o,indent=2)+"\n",encoding="utf8",newline="\n")
print("R025 controlled FIX1 source",len(changes),"new source hashes, owner cards",len(ownerchanges),"updated, unchanged prior signed R018-R024")
