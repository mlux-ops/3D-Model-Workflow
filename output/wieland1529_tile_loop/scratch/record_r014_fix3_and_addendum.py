"""One-time addendum manifest, Reviewer clearance receipt and auditable ledger."""
from pathlib import Path
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[1]
S = R / "state"
AD = R / "deliverables/r014-bath3-point-drain-installation-addendum"
R16 = R / "deliverables/integrated-r16"
MAN = AD / "MANIFEST.json"
CLEAR = S / "ROUND014_R16_REVIEWER_FIX3_INDEPENDENT_CLEARANCE.json"
LEDGER = S / "LEDGER.md"
HEADER = "## Round014 four-critic dispatch and independent R16 FIX3 clearance; Bath3 drain-manual addendum — 2026-11-06"
assert not MAN.exists() and not CLEAR.exists(), "One-time output exists"
assert HEADER not in LEDGER.read_text(encoding="utf-8"), "Ledger already appended"

def fingerprint(path):
    b = path.read_bytes()
    return {"sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

src = S / "ROUND014_SUBMISSION.json"
dispatch = S / "ROUND014_CRITIC_DISPATCH.json"
r16m = R16 / "MANIFEST.json"
fix3 = S / "ROUND014_R16_REVIEWER_BOOK_FIX3.json"
assert fingerprint(src)["sha256"] == "946b3eda0a097961e28e76823607fd7d52b82209156e5bb59cdeb9c36450c8ed"
assert fingerprint(dispatch)["sha256"] == "f1d27d7e220e8581b2d039c42107595745305c95925f808850e018f4edf50270"
assert fingerprint(r16m)["sha256"] == "03bf0e1e811642d72778df053fcaa5495920a653db02ec36bddaa7b76f1ed7c1"
d,s,m,f = load(dispatch),load(src),load(r16m),load(fix3)
assert m["rooms"] == 13 and m["original_material_two_PH_two_TX_usd"] == 23572.44
assert m["original_gross_waste_included_once"]
assert not m["owner_approval"] and not m["procurement_release"]
assert d["all_critic_scores"] is None and d["weighted_scoring"] is None
assert d["source_submission_sha256"] == fingerprint(src)["sha256"]
assert f["manifest_after"]["sha256"] == fingerprint(r16m)["sha256"]
for fn, sig in m["outputs"].items():
    assert fingerprint(R16 / fn) == sig, fn
for room, letters in s["candidate_files"].items():
    for letter, sig in letters.items():
        assert fingerprint(R / sig["file"]) == {"sha256": sig["sha256"], "bytes": sig["bytes"]}, (room, letter)

with (AD / "PROVISIONAL_BATH3_GEOMETRY_AND_BRANCH_GATES.csv").open(newline="", encoding="utf-8") as h:
    rows = list(csv.DictReader(h))
assert len(rows)==2 and [r["room"] for r in rows]==["PH-BATH3","TX-BATH3"]
for row in rows:
    wall = sum(float(row[k]) for k in ("source_w1_ft","source_w2_ft","source_w3_ft")) * float(row["source_tiled_height_ft"])
    assert abs(wall-float(row["source_wall_w1_w3_area_before_waste_sf"]))<0.0001
    assert abs(wall*1.15-float(row["theoretical_wall_gross_once_15pct_sf"]))<0.001
    assert abs(float(row["source_floor_area_sf"])*1.15-float(row["theoretical_floor_gross_once_15pct_sf"]))<0.0001
    assert row["owner_tub_vs_walkin"]=="UNSELECTED"
    assert row["owner_release"]==row["GC_release"]=="false"
    assert row["level_raw_exact_numerical_wet_dcof"]=="NULL_FAIL"
    assert row["conditional_walkin_point_pan_raw_exact_numerical_wet_dcof"]=="NULL_FAIL_if_WALKIN"
assert rows[0]["owner_basin"]=="UNSELECTED" and rows[1]["owner_basin"]=="NOT_ASSERTED_UNSELECTED"
files = ["START_HERE.md","BATH3_POINT_DRAIN_MANUAL_AND_BRANCH_RECONCILIATION.md","PROVISIONAL_BATH3_GEOMETRY_AND_BRANCH_GATES.csv"]
manifest = {
    "round":14, "as_of":"2026-11-06",
    "kind":"additive official PH/TX Bath3 point drain manuals and two-program owner/GC research",
    "delta_manual":"https://media.deltafaucet.com/MandI/113919%20Rev%20B.pdf",
    "brizo_manual":"https://media.brizo.com/MandI/113920%20Rev%20C.pdf",
    "r014_source_sha256_unchanged":fingerprint(src)["sha256"],
    "r014_dispatch_sha256_unchanged":fingerprint(dispatch)["sha256"],
    "r16_manifest_sha256_unchanged":fingerprint(r16m)["sha256"],
    "source_historic_four_unit_material_usd":23572.44,
    "original_15pct_waste_included_once":True,
    "bath3_program_owner_selected":False,
    "true_1529_geometry_verified":False,
    "raw_exact_wet_lab_DCOF_verified":False,
    "owner_approval":False,"GC_release":False,"procurement_release":False,
    "all_critic_scores":None,"weighted_scoring":None,
    "outputs":{fn:fingerprint(AD/fn) for fn in files}
}
clear = {
    "round":14,"as_of":"2026-11-06","reviewer":"worker-14",
    "actual_result":"CONTINUE — SAME-R014 R16 owner-book FIX3 accepted independently; 13-room program still OPEN",
    "scope":"R16 four corrected rows/manifest only, not R014 eight-critic collection, weighted scoring or global DONE",
    "r16_manifest_sha256":fingerprint(r16m)["sha256"],
    "r16_owner_book_sha256":fingerprint(R16/"R16_13_ROOM_DESIGN_CONSTRUCTION_PROCUREMENT_BOOK.md")["sha256"],
    "fix3_receipt_sha256":fingerprint(fix3)["sha256"],
    "rows_corrected":["PH-PRIMARY","PH-BATH4","TX-PRIMARY","TX-BATH3"],
    "other_R16_signed_outputs_unchanged":True,
    "r013_r15_signed_chain_preserved":True,
    "original_r014_source_dispatch_preserved":True,
    "R014_collection_clearance":False,"weighted_scoring":None,
    "owner_approval":False,"procurement_release":False,"global_13_room_done":False
}
MAN.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
CLEAR.write_text(json.dumps(clear,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
buildph = fingerprint(R/"rooms/PH-BATH3/board/round-014/critic-build.md")
buildtx = fingerprint(R/"rooms/TX-BATH3/board/round-014/critic-build.md")
entry = "\n"+HEADER+"\n\n"
entry += "- Standing independent non-Pro Reviewer worker-14 returned actual CONTINUE on R16 FIX3. Four owner-book rows and signed R16 manifest SHA "+fingerprint(r16m)["sha256"]+" cleared. Independent clearance receipt SHA "+fingerprint(CLEAR)["sha256"]+". This is not global DONE.\n"
entry += "- R014 independent source-cleared 4 neutral frozen candidates and private maps unchanged; source SHA "+fingerprint(src)["sha256"]+"; dispatch SHA "+fingerprint(dispatch)["sha256"]+". Reused four originals: worker-13 market .30, worker-9 design .25, worker-10 build .25, worker-12 cost .20. Source/dispatch score fields remain null.\n"
entry += "- Actual worker-10 BUILD two original blind files verified: PH-BATH3 SHA "+buildph["sha256"]+" and TX-BATH3 SHA "+buildtx["sha256"]+"; 20 individual criteria, 4 one-decimal means and 55 local evidence links passed read-only parsing. Other 6 reports still pending at this checkpoint. No formal weighting, champion or release.\n"
entry += "- New supplemental official manual study: Delta DT062412 instruction 113919 Rev B and Brizo BT062415-BNX instruction 113920 Rev C identify 4-in shower square POINT drain conventional sloped mortar/clamped-liner installation sequence, not a certified alternative membrane assembly. Distinct owner TUB/WALK-IN elections unresolved, PH basin unselected. Addendum manifest SHA "+fingerprint(MAN)["sha256"]+"; new addendum has not yet been independently cleared by Reviewer.\n"
entry += "- Provisional arithmetic: PH W1-W3 theoretical wall 74.865 SF before waste / 86.095 SF at original 15%; floor 35 SF / 40.25 SF; TX wall 79.825 / 91.799 and floor 37 / 42.55, all approximate and unverified 1529. Historic source wall PH 86.20/TX 91.80 and floor PH 40.20/TX 42.50, waste already included ONCE. Do not duplicate whole LEVEL and conditional PAN or shared WC.\n"
entry += "- Entire 13-room scope still OPEN. Original 27 historic rows (2 excluded/no-order niches), 25 preliminary wall studies, 65 trade actions, four-unit MATERIAL $23,572.44 and R013/R15/R16 signed files preserved. Current Chicago verified quote/stock/carton, exact maker raw numerical wet LEVEL/conditional PAN DCOF, 1529 native geometry, approved drain or tub sections, owner caps and owner/GC release all missing/false.\n"
with LEDGER.open("a",encoding="utf-8",newline="") as fhandle:
    fhandle.write(entry)
assert fingerprint(r16m)["sha256"]==f["manifest_after"]["sha256"]
assert not (S/"ROUND014_SCORING.json").exists()
print("PASS R014 R16 FIX3 independent CONTINUE recorded; addendum 3 files SHA-signed and CSV verified; original source/dispatch/R16 immutable, no scoring; LEDGER appended")
print("ADDENDUM_MANIFEST_SHA",fingerprint(MAN)["sha256"])
print("CLEARANCE_SHA",fingerprint(CLEAR)["sha256"])
