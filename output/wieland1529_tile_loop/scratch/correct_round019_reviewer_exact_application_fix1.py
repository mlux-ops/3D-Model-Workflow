"""One-time SAME-R019 reviewer FIX: exact 13-room lab/wall/niche applicability.
Do not edit color numeric source CSV, original R014/R015 candidates or signed R17/R18.
"""
from pathlib import Path
import hashlib,csv,json

R=Path(__file__).resolve().parents[1]; S=R/"state"
D=R/"deliverables/integrated-r19-manufacturer-wet-evidence-grades"
M=D/"MANIFEST.json"
REC=S/"ROUND019_REVIEWER_SOURCE_APPLICATION_FIX1.json"
assert not REC.exists(), "Original corrective receipt is already signed"

def fp(p):
    b=p.read_bytes()
    return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}

old_manifest=fp(M)
assert old_manifest["sha256"]=="8de01474d0c681ee61ba8d69ea7d4ef50aa2b3d76cbb819b77867eb9f58187a8"
m=json.loads(M.read_text(encoding="utf-8"))
prior={name:fp(D/name) for name in m["outputs"]}
assert all(prior[name]==sig for name,sig in m["outputs"].items())
paths={
    "matrix":D/"R19_13_ROOM_ORIGINAL_LAB_SPECIMEN_AND_APPROVAL_REQUEST_MATRIX.csv",
    "book":D/"R19_7_COLOR_SGS_DCOF_EVIDENCE_QUALITY_AND_INSTALLER_HOLDS.md",
    "start":D/"START_HERE_R19.md",
    "color":D/"R19_7_MAKER_COLOR_SPECIFIC_NUMERIC_THIRD_PARTY_SUMMARY_NOT_ORIGINAL_LAB.csv"
}
with paths["matrix"].open("r",encoding="utf-8",newline="") as f:
    reader=csv.DictReader(f)
    fields=reader.fieldnames
    rows=list(reader)
assert len(rows)==13 and len(fields)==14

for row in rows:
    room=row["room"]
    if "POWDER" in room:
        row["required_new_source_document_for_wet_LEVEL"]="N/A: DRY vanity WALL and WOOD floor; no tiled bath LEVEL wet DCOF lab request"
        row["individual_wet_WALL_document"]="N/A: DRY decorative vanity WALL; no wet shower/tub-wall authorization required"
        row["individual_wet_NICHE_document"]="N/A: no wet shower/tub NICHE; no wet niche authorization required"
        assert row["existing_LEVEL_gate"]=="N/A_WOOD_FLOOR" and row["existing_PAN_gate"]=="N/A"
    elif room in ("PH-WC","TX-WC"):
        parent=room.split("-")[0]+"-PRIMARY"
        row["required_new_source_document_for_wet_LEVEL"]="INHERITED FROM "+parent+": exact manufacturer SKU/size/finish raw measured wet LEVEL DCOF once; no separate WC tile SKU, test, cost or order"
        row["individual_wet_WALL_document"]="N/A: inherited WC LEVEL floor only; no scheduled wet tub/shower WALL in WC"
        row["individual_wet_NICHE_document"]="N/A: no scheduled wet shower/tub NICHE in WC"
        assert row["existing_LEVEL_gate"]=="REQUIRED_IN_PARENT_PRIMARY_ONCE" and row["existing_PAN_gate"]=="N/A"
    elif room in ("PH-PRIMARY","TX-PRIMARY"):
        row["required_new_source_document_for_wet_LEVEL"]="Original exact manufacturer/laboratory wet LEVEL DCOF report for selected Primary bath tile SKU, size, finish, tested surface treatment, sample ID, date and ANSI A326.3 actual numeric measurement; same result must cover inherited "+room[:2]+"-WC LEVEL once"
        row["individual_wet_WALL_document"]="Exact individual Primary WET shower WALL/ceiling SKU/color/finish manufacturer Wet Areas application; flat maker listing cannot transfer to relief Reed/Ribbed"
        row["individual_wet_NICHE_document"]="N/A — NO ADDITIONAL PRIMARY NICHE by owner; original excluded/unpriced reference NO SCOPE / NO ORDER"
        assert row["existing_PAN_gate"]=="REQUIRED_SEPARATE_LINEAR_RAW_EXACT_NUMERIC"
    else:
        assert room in ("PH-BATH2","PH-BATH3","PH-BATH4","TX-BATH2","TX-BATH3","TX-BATH4"),room
        row["required_new_source_document_for_wet_LEVEL"]="Exact original manufacturer/laboratory wet LEVEL tile SKU/size/finish raw numeric ANSI A326.3 measured DCOF with sample ID, test date, treatment/sealer and approved wet bath-floor application; NOT inherited from a different material or room"
        row["individual_wet_WALL_document"]="Exact individual SKU/color/finish tub or shower WET WALL manufacturer Wet Areas authorization; source flat finish cannot authorize relief and Sapphire cannot authorize Opal"
        row["individual_wet_NICHE_document"]="Exact individual SKU/color/finish WET NICHE manufacturer Wet Areas authorization; Sandstone/Soho permission cannot be transferred to unlisted Clara Caviar"
    if room=="PH-BATH3":
        row["separate_PAN_source_requirement"]="ONLY IF owner signs WALK-IN: selected Delta DT062412 Chrome 4in SQUARE POINT shower drain, 4-plane small-format PAN exact manufacturer raw numeric wet DCOF and approved membrane/rough/flood section; TUB PAN N/A, Delta NOT tub waste"
    elif room=="TX-BATH3":
        row["separate_PAN_source_requirement"]="ONLY IF owner signs WALK-IN: selected Brizo BT062415-BNX Black Onyx 4in SQUARE POINT shower drain, 4-plane small-format PAN exact manufacturer raw numeric wet DCOF and approved membrane/rough/flood section; TUB PAN N/A, Brizo NOT tub waste"

assert all(row["current_original_RAW_lab_reference"]=="" and row["owner_approved"]=="FALSE" and row["GC_released"]=="FALSE" and row["PO_released"]=="FALSE" for row in rows)
with paths["matrix"].open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

book=paths["book"]
text=book.read_text(encoding="utf-8")
old="# R19 — manufacturer color-specific third-party numeric wet friction data, not a selected project lab"
new="# R19 — manufacturer-published ANSI A326.3 numeric color DCOF, test wet condition unspecified; not a selected project raw lab"
assert text.count(old)==1
text=text.replace(old,new)
old="It still **does NOT supply the underlying individual original laboratory specimen certificate or report ID**, date, exact format/SKU, surface sealer and installed condition."
new="The published A326.3 color table does **NOT state the actual wet test fluid or test condition** and does **NOT supply the underlying original laboratory specimen certificate/report ID**, test date, exact tested format/SKU/finish, sealer, wax or final installed surface condition."
assert text.count(old)==1
text=text.replace(old,new)
old="rather than assuming 0.54-0.63 is post-wax slip."
new="rather than assuming 0.54-0.63 represents an independently established wet, post-wax or project-installed condition."
assert text.count(old)==1
text=text.replace(old,new)
old="merely because a color has a wet DCOF table"
new="merely because a color has a published A326.3 numerical DCOF table with wet condition unspecified"
assert text.count(old)==1
text=text.replace(old,new)
old="| B — maker third-party numeric summary with named laboratory | Zia official color-specific Cantera A326.3 chart credited SGS TEC Services, seven 0.53-0.63 reported values | Promising source request lead but **NOT Tier A** without specimen ID, exact size/finish, sealer/report and project-compatible install |"
new="| B — maker third-party numeric summary with named laboratory | Zia official color-specific Cantera A326.3 chart credited SGS TEC Services, seven 0.53-0.63 reported values; wet liquid/test condition unspecified | Promising source request lead but **NOT Tier A** without specimen ID, exact size/finish, wet condition, sealer/report and project-compatible install |"
assert text.count(old)==1
text=text.replace(old,new)
book.write_text(text,encoding="utf-8")

start=paths["start"]
t=start.read_text(encoding="utf-8")
old="# R19 — manufacturer-origin numeric wet DCOF evidence hierarchy"
new="# R19 — manufacturer-published ANSI A326.3 numeric color DCOF; wet test condition unspecified"
assert old in t
t=t.replace(old,new)
old="Official Zia Cantera color-specific ANSI A326.3 third-party SGS summary has seven published decimals but lacks underlying lab report, exact tested 12x24 SKU/finish/sealer and installed conditions"
new="Official Zia Cantera ANSI A326.3 manufacturer color table credits SGS and publishes seven decimal values, but the actual wet fluid/test condition and underlying original specimen report, exact tested format/SKU/finish/sealer/wax and installed condition are unavailable"
assert old in t
t=t.replace(old,new)
start.write_text(t,encoding="utf-8")

assert fp(paths["color"])==prior[paths["color"].name], "Original seven-color maker table must remain byte-identical"
for name in m["outputs"]:
    m["outputs"][name]=fp(D/name)
m["values_source_tier"]="B maker color-specific ANSI A326.3 summary credited SGS, wet test fluid/condition unspecified; NOT original exact installed SKU raw lab certificate"
M.write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert all(fp(D/n)==sig for n,sig in m["outputs"].items())
assert not m["owner_approval"] and not m["GC_release"] and not m["procurement_release"]
assert m["R014_scoring"] is None and m["R015_scoring"] is None
assert fp(R/"deliverables/integrated-r17/MANIFEST.json")["sha256"]==m["R17_original_signed_manifest_sha256"]
assert fp(R/"deliverables/integrated-r18-owner-sample-visual-and-shop/MANIFEST.json")["sha256"]==m["R18_signed_manifest_sha256"]
assert fp(S/"ROUND014_SUBMISSION.json")["sha256"]==m["R014_source_sha256"]
assert fp(S/"ROUND015_SUBMISSION.json")["sha256"]==m["R015_source_sha256"]
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists()
receipt={
 "round":19,"as_of":"2026-11-06","independent_reviewer":"worker-15",
 "reviewer_actual_verdict":"FIX — R19 applicability and raw-source wet condition wording, SAME-R019",
 "fixes":["3 dry wood-floor powder LEVEL/WALL/NICHE wet tests N/A","2 inherited WC LEVEL parent-single-source and wet WALL/NICHE N/A","both Primary niches NO ADDITIONAL NICHE / NO ORDER","six distinct standalone baths LEVEL lab requests do not copy WC","manufacturer SGS color A326.3 wet test condition unspecified","selected Delta PH and Brizo TX Bath3 POINT drains explicit conditional WALK-IN and never tub waste"],
 "old_manifest":old_manifest,"corrected_manifest":fp(M),
 "output_changes":[{"file":name,"before":oldsig,"after":fp(D/name),"changed":oldsig!=fp(D/name)} for name,oldsig in prior.items()],
 "original_color_report_csv_byte_identical":True,
 "older_R014_R015_R017_R018_source_preserved":True,
 "R014_scoring":None,"R015_scoring":None,
 "owner_approval":False,"GC_release":False,"procurement_release":False,
 "global_13_room_done":False
}
REC.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("PASS SAME-R019 exact Reviewer FIX1: 13 appropriate wet LEVEL/WALL/NICHE requests, owner Bath3 point drains, maker A326.3 condition unspecified, original 7-color CSV SHA intact; R014/15 scoring and all releases false")
print("R19_MANIFEST_SHA",fp(M)["sha256"])
print("FIX_RECEIPT_SHA",fp(REC)["sha256"])
